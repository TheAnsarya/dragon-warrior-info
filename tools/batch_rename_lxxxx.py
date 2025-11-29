"""
Batch Rename Lxxxx Labels by Section

Renames Lxxxx labels based on their parent section/table context.
"""

import re
from pathlib import Path
from collections import defaultdict


def analyze_sections(fname: str, lines: list) -> dict:
    """Find named sections and their Lxxxx children."""
    named_pattern = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*):')
    l_pattern = re.compile(r'^(L[0-9A-Fa-f]{4}):(.*)$')
    
    sections = {}
    current_named = None
    current_line = 0
    
    for i, line in enumerate(lines):
        named_match = named_pattern.match(line)
        l_match = l_pattern.match(line)
        
        if named_match and not l_pattern.match(line):
            current_named = named_match.group(1)
            current_line = i
            if current_named not in sections:
                sections[current_named] = {'line': i, 'lxxxx': []}
        elif l_match and current_named:
            label = l_match.group(1)
            rest = l_match.group(2).strip()
            sections[current_named]['lxxxx'].append({
                'label': label,
                'line': i,
                'rest': rest
            })
    
    return sections


def generate_rename(parent: str, index: int, rest: str, label: str) -> str:
    """Generate a new name based on parent section and context."""
    addr = label[1:]  # Get hex address without L prefix
    
    # Common section name mappings
    section_map = {
        'BankPointers': 'BankPtr',
        'MapDataTable': 'MapData',
        'WrldMapPtrTbl': 'WrldMapRow',
        'WorldMapPointerTable': 'WrldMapRow',
        'NPCMobilePointerTable': 'MobNPCPtr',
        'NPCStaticPointerTable': 'StatNPCPtr',
        'NPCMobPtrTbl': 'MobNPCPtr',
        'NPCStatPtrTbl': 'StatNPCPtr',
        'EnemyStatsTable': 'EnemyStat',
        'ItemCostTbl': 'ItemCost',
        'SpellMPCostTbl': 'SpellCost',
        'WeaponBonusTbl': 'WpnBonus',
        'ArmorBonusTbl': 'ArmorBonus',
        'ShieldBonusTbl': 'ShieldBonus',
        'BlackPalPtr': 'PalPtr',
        'SprPalTbl': 'SpritePal',
        'BGPalTbl': 'BGPal',
        'TextBlock': 'Text',
        'TextBlock1': 'Text1',
        'DialogTable': 'Dialog',
        'BrecCvrdDatPointer': 'BrecCvrd',
        'GarCvrdDatPtr': 'GarCvrd',
        'CantCvrdDatPtr': 'CantCvrd',
        'RimCvrdDatPtr': 'RimCvrd',
        'DLCstlGFDat': 'DLCastleGF',
        'HauksnessDat': 'Hauksness',
        'TantGFDat': 'TantegelGF',
        'ThrnRoomDat': 'ThroneRoom',
        'BrecDat': 'Brecconary',
        'GarinDat': 'Garinham',
        'KolDat': 'Kol',
        'RimDat': 'Rimuldar',
        'CantDat': 'Cantlin',
    }
    
    # Get parent prefix
    prefix = parent
    for full, short in section_map.items():
        if full in parent or parent == full:
            prefix = short
            break
    
    # Limit prefix length
    if len(prefix) > 12:
        prefix = prefix[:10]
    
    # Parse comment for hints
    comment = ''
    if ';' in rest:
        comment = rest.split(';', 1)[1].strip().lower()
    
    # Determine suffix based on instruction and comment
    rest_lower = rest.lower()
    
    if '.word' in rest_lower:
        if 'pointer' in comment or 'ptr' in comment:
            suffix = 'Ptr'
        elif 'row' in comment:
            suffix = 'Row'
        else:
            suffix = 'Word'
    elif '.byte' in rest_lower:
        if 'column' in comment:
            suffix = 'Cols'
        elif 'row' in comment:
            suffix = 'Rows'  
        elif 'width' in comment:
            suffix = 'Width'
        elif 'height' in comment:
            suffix = 'Height'
        elif 'x' in comment and ('pos' in comment or 'coord' in comment):
            suffix = 'X'
        elif 'y' in comment and ('pos' in comment or 'coord' in comment):
            suffix = 'Y'
        elif 'boundary' in comment or 'swamp' in comment or 'water' in comment or 'grass' in comment:
            suffix = 'Bound'
        elif 'tile' in comment:
            suffix = 'Tile'
        elif 'palette' in comment or 'pal' in comment:
            suffix = 'Pal'
        else:
            suffix = 'Byte'
    elif '.text' in rest_lower:
        suffix = 'Str'
    elif 'rts' in rest_lower:
        suffix = 'Exit'
    elif 'jsr' in rest_lower:
        suffix = 'Call'
    elif 'jmp' in rest_lower:
        suffix = 'Jmp'
    elif 'lda' in rest_lower or 'ldx' in rest_lower or 'ldy' in rest_lower:
        suffix = 'Load'
    elif 'sta' in rest_lower or 'stx' in rest_lower or 'sty' in rest_lower:
        suffix = 'Store'
    elif 'cmp' in rest_lower or 'cpx' in rest_lower or 'cpy' in rest_lower:
        suffix = 'Cmp'
    elif 'bne' in rest_lower or 'beq' in rest_lower:
        suffix = 'Branch'
    elif 'inc' in rest_lower or 'dec' in rest_lower:
        suffix = 'Count'
    else:
        suffix = 'L'
    
    # Use address for uniqueness instead of index
    return f"{prefix}_{suffix}_{addr}"


def process_file(fpath: Path, dry_run: bool = False) -> dict:
    """Process a single file, renaming Lxxxx labels by section."""
    content = fpath.read_text(encoding='utf-8')
    lines = content.split('\n')
    
    sections = analyze_sections(fpath.name, lines)
    
    # Build rename map
    renames = {}
    
    for parent, data in sections.items():
        for idx, ldata in enumerate(data['lxxxx']):
            old_name = ldata['label']
            new_name = generate_rename(parent, idx, ldata['rest'], old_name)
            
            # Ensure unique
            base = new_name
            counter = 1
            while new_name in renames.values():
                new_name = f"{base}_{counter}"
                counter += 1
            
            renames[old_name] = new_name
    
    if dry_run:
        return renames
    
    # Apply renames
    new_content = content
    for old, new in renames.items():
        # Replace definition
        new_content = re.sub(rf'^{old}:', f'{new}:', new_content, flags=re.MULTILINE)
        # Replace references
        new_content = re.sub(rf'\b{old}\b', new, new_content)
    
    fpath.write_text(new_content, encoding='utf-8')
    return renames


def main():
    import sys
    dry_run = '--dry-run' in sys.argv
    
    source_dir = Path('source_files')
    files = ['Bank00.asm', 'Bank01.asm', 'Bank02.asm']
    
    total = 0
    for fname in files:
        fpath = source_dir / fname
        if fpath.exists():
            renames = process_file(fpath, dry_run)
            print(f"{fname}: {len(renames)} labels {'would be ' if dry_run else ''}renamed")
            total += len(renames)
            
            if dry_run and len(renames) > 0:
                print("  Sample renames:")
                for old, new in list(renames.items())[:10]:
                    print(f"    {old} -> {new}")
    
    print(f"\nTotal: {total} labels {'would be ' if dry_run else ''}renamed")


if __name__ == '__main__':
    main()
