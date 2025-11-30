"""
Remove Unreferenced Lxxxx Labels

This script finds all labels matching the pattern L[0-9A-Fa-f]{4} (like LB5D2, LFF74)
that are never referenced in jumps, branches, or other instructions, and:
1. Removes the label from the line
2. Adds the address as a comment prefix (e.g., ;($B5D2))

Usage: python tools/remove_unreferenced_labels.py [--dry-run]
"""

import re
import sys
from pathlib import Path
from collections import defaultdict


def find_all_lxxxx_labels(content: str) -> list[tuple[str, int]]:
    """Find all Lxxxx labels and their line numbers."""
    labels = []
    lines = content.split('\n')
    label_pattern = re.compile(r'^(L[0-9A-Fa-f]{4}):\s*(.*)$')

    for i, line in enumerate(lines):
        match = label_pattern.match(line)
        if match:
            labels.append((match.group(1), i))

    return labels


def is_label_referenced(label: str, all_text: str, content: str) -> bool:
    """Check if a label is referenced anywhere (not just defined)."""
    label_lower = label.lower()

    # Count all occurrences
    total_count = len(re.findall(r'\b' + re.escape(label_lower) + r'\b', all_text.lower()))

    # If only 1 occurrence, it's just the definition
    if total_count <= 1:
        return False

    return True


def process_file(filepath: Path, all_text: str, dry_run: bool = False) -> tuple[int, list[str]]:
    """Process a single file, removing unreferenced Lxxxx labels."""
    content = filepath.read_text(encoding='utf-8')
    lines = content.split('\n')

    labels = find_all_lxxxx_labels(content)
    removed = []

    # Pattern to match label lines
    label_pattern = re.compile(r'^(L[0-9A-Fa-f]{4}):\s*(.*)$')

    for label, line_num in labels:
        if not is_label_referenced(label, all_text, content):
            # This label is not referenced - transform it
            line = lines[line_num]
            match = label_pattern.match(line)
            if match:
                label_name = match.group(1)
                rest_of_line = match.group(2)

                # Extract the hex address from the label (e.g., LB5D2 -> B5D2)
                addr = label_name[1:]  # Remove the 'L' prefix

                # Check if there's already a comment
                if ';' in rest_of_line:
                    # Insert address before existing comment
                    parts = rest_of_line.split(';', 1)
                    instruction = parts[0]
                    comment = parts[1]
                    new_line = f"        {instruction.strip():<24};(${addr}){comment}"
                else:
                    # Add address as new comment
                    new_line = f"        {rest_of_line.strip():<24};(${addr})"

                lines[line_num] = new_line
                removed.append(f"{filepath.name}:{line_num+1} {label}")

    if removed and not dry_run:
        filepath.write_text('\n'.join(lines), encoding='utf-8')

    return len(removed), removed


def main():
    dry_run = '--dry-run' in sys.argv

    source_dir = Path('source_files')
    source_files = ['Bank00.asm', 'Bank01.asm', 'Bank02.asm', 'Bank03.asm']

    # Load all source text for reference checking
    print("Loading all source files...")
    all_text = ''
    for fname in source_files + ['Dragon_Warrior_Defines.asm']:
        fpath = source_dir / fname
        if fpath.exists():
            all_text += fpath.read_text(encoding='utf-8')

    print(f"{'DRY RUN - ' if dry_run else ''}Processing files...")

    total_removed = 0
    all_removed = []

    for fname in source_files:
        fpath = source_dir / fname
        if fpath.exists():
            count, removed = process_file(fpath, all_text, dry_run)
            total_removed += count
            all_removed.extend(removed)
            print(f"  {fname}: {count} labels {'would be ' if dry_run else ''}removed")

    print(f"\n{'Would remove' if dry_run else 'Removed'} {total_removed} unreferenced Lxxxx labels")

    if total_removed > 0 and len(all_removed) <= 50:
        print("\nLabels removed:")
        for item in all_removed:
            print(f"  {item}")
    elif total_removed > 0:
        print(f"\nFirst 50 labels {'that would be ' if dry_run else ''}removed:")
        for item in all_removed[:50]:
            print(f"  {item}")
        print(f"  ... and {len(all_removed) - 50} more")


if __name__ == '__main__':
    main()
