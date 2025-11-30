"""
Export Lxxxx Labels for Manual Review

Creates a CSV with all remaining Lxxxx labels and rich context to help
with manual naming decisions.
"""

import re
import csv
from pathlib import Path
from collections import defaultdict


def get_map_name(line_num: int, lines: list) -> str:
    """Look backwards for map section comment."""
    for i in range(line_num, max(0, line_num - 15), -1):
        line = lines[i].strip()
        if line.startswith(';') and ('Map #' in line or 'map' in line.lower()):
            # Extract map name
            clean = line.lstrip(';').strip()
            if '.' in clean:
                return clean.split('.')[0].strip()
            return clean[:50]
    return ''


def get_section_header(line_num: int, lines: list) -> str:
    """Look backwards for section header (;--- lines)."""
    for i in range(line_num, max(0, line_num - 30), -1):
        line = lines[i].strip()
        if line.startswith(';---') or line.startswith(';==='):
            # Next non-empty line might be the title
            for j in range(i + 1, min(len(lines), i + 5)):
                next_line = lines[j].strip()
                if next_line and not next_line.startswith(';---'):
                    if next_line.startswith(';'):
                        return next_line.lstrip(';').strip()[:60]
                    elif ':' in next_line:
                        return next_line.split(':')[0].strip()
    return ''


def get_parent_label(line_num: int, lines: list) -> str:
    """Find the parent named label (not Lxxxx)."""
    named_pattern = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*):')
    l_pattern = re.compile(r'^L[0-9A-Fa-f]{4}:')

    for i in range(line_num - 1, max(0, line_num - 100), -1):
        line = lines[i]
        if l_pattern.match(line):
            continue
        match = named_pattern.match(line)
        if match:
            return match.group(1)
    return ''


def get_reference_info(label: str, all_files: dict) -> tuple:
    """Get info about how this label is referenced."""
    refs = []
    ref_types = set()

    for fname, content in all_files.items():
        for i, line in enumerate(content.split('\n')):
            if label + ':' in line:  # Skip definition
                continue
            if re.search(r'\b' + re.escape(label) + r'\b', line):
                refs.append(f"{fname}:{i+1}")
                line_upper = line.upper()
                if 'BNE' in line_upper or 'BEQ' in line_upper:
                    ref_types.add('branch')
                elif 'BCS' in line_upper or 'BCC' in line_upper:
                    ref_types.add('carry_branch')
                elif 'BMI' in line_upper or 'BPL' in line_upper:
                    ref_types.add('sign_branch')
                elif 'JSR' in line_upper:
                    ref_types.add('call')
                elif 'JMP' in line_upper:
                    ref_types.add('jump')
                elif '.WORD' in line_upper:
                    ref_types.add('pointer')

    return refs, ref_types


def suggest_name(label: str, parent: str, section: str, map_name: str,
                 instruction: str, ref_types: set, comment: str) -> str:
    """Suggest a name based on context."""
    addr = label[1:]  # Remove 'L' prefix

    # Check for map data
    if map_name:
        # Clean map name
        map_short = re.sub(r'[^A-Za-z0-9]', '', map_name)[:15]
        if 'Overworld' in map_name:
            map_short = 'Overworld'
        elif 'Dragonlord' in map_name:
            map_short = 'DLCastle'
        elif 'Hauksness' in map_name:
            map_short = 'Hauksness'
        elif 'Tantagel' in map_name:
            map_short = 'Tantegel'
        elif 'Throne' in map_name:
            map_short = 'ThroneRoom'
        elif 'Brecconary' in map_name:
            map_short = 'Brecconary'
        elif 'Garinham' in map_name:
            map_short = 'Garinham'

        # Determine field type from instruction
        if '.word' in instruction.lower():
            return f"{map_short}MapPtr"
        elif 'column' in comment.lower():
            return f"{map_short}Columns"
        elif 'row' in comment.lower():
            return f"{map_short}Rows"
        elif 'boundary' in comment.lower() or 'swamp' in comment.lower() or 'water' in comment.lower():
            return f"{map_short}Boundary"
        else:
            return f"{map_short}Data_{addr}"

    # Check for loop target
    if 'branch' in ref_types:
        if parent:
            return f"{parent[:12]}Loop"

    # Check for subroutine
    if 'call' in ref_types:
        if parent:
            return f"{parent[:12]}Sub"

    # Check for jump target
    if 'jump' in ref_types:
        if parent:
            return f"{parent[:12]}Jmp"

    # Check for pointer entry
    if 'pointer' in ref_types:
        if parent:
            return f"{parent[:12]}Entry"

    # Default: use parent + instruction type
    if parent:
        instr = instruction.split()[0] if instruction else 'Code'
        return f"{parent[:10]}_{instr}_{addr}"

    return f"Code_{addr}"


def main():
    source_dir = Path('source_files')
    source_files = ['Bank00.asm', 'Bank01.asm', 'Bank02.asm', 'Bank03.asm']

    # Load all files
    all_files = {}
    file_lines = {}
    for fname in source_files:
        fpath = source_dir / fname
        if fpath.exists():
            content = fpath.read_text(encoding='utf-8')
            all_files[fname] = content
            file_lines[fname] = content.split('\n')

    # Find all Lxxxx labels
    l_pattern = re.compile(r'^(L[0-9A-Fa-f]{4}):(.*)$')

    results = []

    for fname, lines in file_lines.items():
        for i, line in enumerate(lines):
            match = l_pattern.match(line)
            if match:
                label = match.group(1)
                rest = match.group(2).strip()

                # Get context
                parent = get_parent_label(i, lines)
                section = get_section_header(i, lines)
                map_name = get_map_name(i, lines)

                # Parse instruction and comment
                instruction = rest.split(';')[0].strip() if rest else ''
                comment = rest.split(';')[1].strip() if ';' in rest else ''

                # Get reference info
                refs, ref_types = get_reference_info(label, all_files)

                # Suggest name
                suggested = suggest_name(label, parent, section, map_name,
                                        instruction, ref_types, comment)

                results.append({
                    'file': fname,
                    'line': i + 1,
                    'address': f"${label[1:]}",
                    'current_label': label,
                    'suggested_name': suggested,
                    'parent_label': parent,
                    'section': section,
                    'map_context': map_name,
                    'instruction': instruction,
                    'comment': comment,
                    'ref_count': len(refs),
                    'ref_types': ','.join(ref_types),
                    'references': '; '.join(refs[:5])
                })

    # Write CSV
    output_path = Path('lxxxx_labels_review.csv')
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'file', 'line', 'address', 'current_label', 'suggested_name',
            'parent_label', 'section', 'map_context', 'instruction', 'comment',
            'ref_count', 'ref_types', 'references'
        ])
        writer.writeheader()
        writer.writerows(results)

    print(f"Exported {len(results)} Lxxxx labels to {output_path}")
    print(f"\nBy file:")
    from collections import Counter
    file_counts = Counter(r['file'] for r in results)
    for fname, count in sorted(file_counts.items()):
        print(f"  {fname}: {count}")


if __name__ == '__main__':
    main()
