"""
Dragon Warrior Label Inventory Generator

Analyzes all assembly source files to create a comprehensive spreadsheet
of labels with their addresses, probable expanded names, reference counts,
and contextual descriptions.
"""

import re
import csv
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


# Abbreviation expansion patterns
EXPANSION_PATTERNS = {
    'Tbl': 'Table',
    'Ptr': 'Pointer',
    'Dat': 'Data',
    'Wdth': 'Width',
    'Flgs': 'Flags',
    'Pos': 'Position',
    'Mob': 'Mobile',
    'Stat': 'Static',
    'Num': 'Number',
    'Buf': 'Buffer',
    'Cnt': 'Count',
    'Idx': 'Index',
    'Tmp': 'Temporary',
    'Dest': 'Destination',
    'Src': 'Source',
    'Calc': 'Calculate',
    'Attrib': 'Attribute',
    'Vert': 'Vertical',
    'Horz': 'Horizontal',
    'Dgn': 'Dungeon',
    'Brec': 'Brecconary',
    'Cant': 'Cantlin',
    'Gar': 'Garinham',
    'Rim': 'Rimuldar',
    'Kol': 'Kol',
    'Tant': 'Tantegel',
    'Rnbw': 'Rainbow',
    'Blk': 'Block',
    'Chr': 'Character',
    'Gfx': 'Graphics',
    'Spr': 'Sprite',
    'Anim': 'Animation',
    'Eqip': 'Equip',
    'Wpn': 'Weapon',
    'Armr': 'Armor',
    'Itm': 'Item',
    'Trsr': 'Treasure',
    'Dlg': 'Dialog',
    'Msg': 'Message',
    'Wnd': 'Window',
    'Spel': 'Spell',
    'Rand': 'Random',
    'Nm': 'Name',
    'Addr': 'Address',
    'Ofst': 'Offset',
    'Val': 'Value',
    'Cur': 'Current',
    'Prev': 'Previous',
    'Updt': 'Update',
    'Clr': 'Clear',
    'Init': 'Initialize',
    'Chk': 'Check',
    'Cmp': 'Compare',
    'Incr': 'Increment',
    'Decr': 'Decrement',
    'Mult': 'Multiply',
    'Div': 'Divide',
    'Ppu': 'PPU',
    'Nmi': 'NMI',
    'Irq': 'IRQ',
    'Rst': 'Reset',
    'Prg': 'Program',
    'Oam': 'OAM',
    'Pal': 'Palette',
    'Cvrd': 'Covered',
    'Rmv': 'Remove',
    'Strs': 'Stairs',
    'Wrld': 'World',
    'Ovr': 'Overworld',
    'Drp': 'Drop',
}

# System/area categorization patterns
SYSTEM_CATEGORIES = {
    'PPU': ['ppu', 'nametable', 'attrib', 'palette', 'scroll'],
    'Graphics': ['gfx', 'sprite', 'tile', 'chr', 'oam'],
    'Audio': ['sound', 'music', 'sfx', 'apu'],
    'Input': ['controller', 'button', 'input', 'joypad'],
    'NPC': ['npc', 'mob', 'static'],
    'Map': ['map', 'block', 'world', 'overworld'],
    'Combat': ['battle', 'enemy', 'attack', 'defense', 'damage'],
    'Items': ['item', 'weapon', 'armor', 'equip', 'treasure'],
    'Spells': ['spell', 'magic', 'heal', 'radiant', 'stopspell'],
    'Dialog': ['dialog', 'text', 'message', 'window'],
    'Player': ['hero', 'player', 'level', 'exp', 'gold'],
    'Location': ['tantegel', 'brecconary', 'garinham', 'cantlin', 'rimuldar', 'kol', 'hauksness', 'cave', 'castle'],
    'Math': ['divide', 'multiply', 'random', 'calc'],
    'System': ['init', 'reset', 'nmi', 'irq', 'bank'],
}


class LabelInventory:
    def __init__(self, source_dir: Path):
        self.source_dir = source_dir
        self.labels: List[Dict] = []
        self.label_references: Dict[str, int] = defaultdict(int)
        self.all_source_text = ""

    def load_all_sources(self):
        """Load all source files for reference counting."""
        source_files = [
            'Bank00.asm',
            'Bank01.asm',
            'Bank02.asm',
            'Bank03.asm',
            'Dragon_Warrior_Defines.asm',
        ]

        for filename in source_files:
            filepath = self.source_dir / filename
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    self.all_source_text += f.read().lower()

    def count_references(self, label_name: str) -> int:
        """Count how many times a label is referenced across all sources."""
        # Convert to lowercase for case-insensitive search
        label_lower = label_name.lower()
        # Count occurrences (excluding the definition itself)
        count = self.all_source_text.count(label_lower)
        # Subtract 1 for the definition
        return max(0, count - 1)

    def expand_abbreviation(self, name: str) -> str:
        """
        Generate probable expanded name by replacing known abbreviations.

        Examples:
            ThRmMobTbl -> ThroneRoomMobileTable
            BlockDataPtrLB -> BlockDataPointerLowByte
            CalcPPUBufAddr -> CalculatePPUBufferAddress
        """
        expanded = name

        # Handle common suffixes first
        if expanded.endswith('LB'):
            expanded = expanded[:-2] + 'LowByte'
        elif expanded.endswith('UB') or expanded.endswith('HB'):
            expanded = expanded[:-2] + 'UpperByte'
        elif expanded.endswith('LUB'):
            expanded = expanded[:-3] + 'LowUpperByte'

        # Replace abbreviations
        for abbrev, full in EXPANSION_PATTERNS.items():
            # Use word boundary replacement to avoid partial matches
            expanded = re.sub(r'\b' + abbrev + r'(?=[A-Z]|$)', full, expanded)

        # Special cases
        if 'ThRm' in expanded:
            expanded = expanded.replace('ThRm', 'ThroneRoom')
        if 'DLBF' in expanded:
            expanded = expanded.replace('DLBF', 'DragonlordBeforeFloor')
        if 'TaSL' in expanded:
            expanded = expanded.replace('TaSL', 'TantegelSwampLevel')
        if 'TaDL' in expanded:
            expanded = expanded.replace('TaDL', 'TantegelDungeonLevel')
        if 'SL' in expanded and 'Swamp' not in expanded:
            expanded = expanded.replace('SL', 'SwampLevel')
        if 'DL' in expanded and 'Dungeon' not in expanded:
            expanded = expanded.replace('DL', 'DungeonLevel')
        if 'BF' in expanded and 'Before' not in expanded:
            expanded = expanded.replace('BF', 'BeforeFloor')

        return expanded

    def categorize_label(self, label_name: str, context: str) -> str:
        """Determine the system/area category for a label."""
        label_lower = label_name.lower()
        context_lower = context.lower()
        combined = label_lower + ' ' + context_lower

        for category, keywords in SYSTEM_CATEGORIES.items():
            for keyword in keywords:
                if keyword in combined:
                    return category

        return 'General'

    def extract_description(self, lines: List[str], line_num: int) -> str:
        """Extract contextual description from nearby comments."""
        description_parts = []

        # Look backward for comments (up to 5 lines)
        for i in range(max(0, line_num - 5), line_num):
            line = lines[i].strip()
            if ';' in line:
                comment = line.split(';', 1)[1].strip()
                if comment and not comment.startswith('-'):
                    description_parts.append(comment)

        # Check current line for inline comment
        current_line = lines[line_num].strip()
        if ';' in current_line:
            comment = current_line.split(';', 1)[1].strip()
            if comment:
                description_parts.append(comment)

        # Look forward for comments (up to 2 lines)
        for i in range(line_num + 1, min(len(lines), line_num + 3)):
            line = lines[i].strip()
            if ';' in line:
                comment = line.split(';', 1)[1].strip()
                if comment and not comment.startswith('-'):
                    description_parts.append(comment)
                    break

        return ' | '.join(description_parts[:3]) if description_parts else ''

    def parse_file(self, filename: str):
        """Parse a single assembly file for labels."""
        filepath = self.source_dir / filename
        if not filepath.exists():
            print(f"Warning: {filename} not found")
            return

        with open(filepath, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Pattern to match labels
        # Matches: "LabelName:" or "LabelName = $1234" or ".alias LabelName OtherName" or ".alias LabelName $1234"
        label_pattern = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*[:=]')
        address_pattern = re.compile(r'=\s*\$([0-9A-Fa-f]+)')
        alias_pattern = re.compile(r'^\.alias\s+([A-Za-z_][A-Za-z0-9_]*)\s+(.+)')
        alias_addr_pattern = re.compile(r'^\$([0-9A-Fa-f]+)')

        for line_num, line in enumerate(lines):
            stripped = line.strip()

            # Skip comments and empty lines
            if not stripped or stripped.startswith(';'):
                continue

            # Handle .alias directives
            alias_match = alias_pattern.match(stripped)
            if alias_match:
                alias_name = alias_match.group(1)
                target_text = alias_match.group(2).strip()

                # Check if target is an address or another label
                addr_match = alias_addr_pattern.match(target_text)
                if addr_match:
                    # .alias LabelName $1234
                    address = '$' + addr_match.group(1).upper()
                    description = self.extract_description(lines, line_num)
                    is_alias = False
                else:
                    # .alias LabelName OtherName
                    target_name = target_text.split()[0]  # Get first word (handles comments)
                    address = ''
                    description = f"Alias for {target_name}"
                    is_alias = True

                self.labels.append({
                    'file_name': filename,
                    'address': address,
                    'name': alias_name,
                    'label': alias_name,
                    'probable_expanded_name': self.expand_abbreviation(alias_name),
                    'reference_count': 0,  # Will be filled later
                    'system_area': 'Alias' if is_alias else self.categorize_label(alias_name, description),
                    'description': description,
                })
                continue

            # Handle regular labels
            label_match = label_pattern.match(stripped)
            if label_match:
                label_name = label_match.group(1)

                # Extract address if present
                address = ''
                addr_match = address_pattern.search(stripped)
                if addr_match:
                    address = '$' + addr_match.group(1).upper()

                # Get description from nearby comments
                description = self.extract_description(lines, line_num)

                # Determine system area
                system_area = self.categorize_label(label_name, description)

                self.labels.append({
                    'file_name': filename,
                    'address': address,
                    'name': label_name,
                    'label': label_name,
                    'probable_expanded_name': self.expand_abbreviation(label_name),
                    'reference_count': 0,  # Will be filled later
                    'system_area': system_area,
                    'description': description,
                })

    def generate_inventory(self):
        """Generate complete label inventory."""
        print("Loading all source files for reference counting...")
        self.load_all_sources()

        source_files = [
            'Dragon_Warrior_Defines.asm',  # Parse defines first
            'Bank00.asm',
            'Bank01.asm',
            'Bank02.asm',
            'Bank03.asm',
        ]

        print("Parsing source files...")
        for filename in source_files:
            print(f"  Processing {filename}...")
            self.parse_file(filename)

        print("Counting label references...")
        for label_data in self.labels:
            label_data['reference_count'] = self.count_references(label_data['name'])

        # Sort by file, then address, then name
        self.labels.sort(key=lambda x: (
            x['file_name'],
            x['address'] if x['address'] else 'ZZZZ',
            x['name']
        ))

    def save_csv(self, output_path: Path):
        """Save label inventory to CSV file."""
        print(f"Writing CSV to {output_path}...")

        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'file_name',
                'address',
                'name',
                'label',
                'probable_expanded_name',
                'reference_count',
                'system_area',
                'description',
            ])

            writer.writeheader()
            writer.writerows(self.labels)

        print(f"✓ Generated label inventory with {len(self.labels)} entries")


def main():
    """Main entry point."""
    # Paths
    repo_root = Path(__file__).parent.parent
    source_dir = repo_root / 'source_files'
    output_path = repo_root / 'labels_inventory.csv'

    # Generate inventory
    inventory = LabelInventory(source_dir)
    inventory.generate_inventory()
    inventory.save_csv(output_path)

    # Print statistics
    print("\nLabel Statistics:")
    print(f"  Total labels: {len(inventory.labels)}")

    by_file = defaultdict(int)
    by_system = defaultdict(int)

    for label in inventory.labels:
        by_file[label['file_name']] += 1
        by_system[label['system_area']] += 1

    print("\nBy File:")
    for filename, count in sorted(by_file.items()):
        print(f"  {filename}: {count}")

    print("\nBy System Area:")
    for area, count in sorted(by_system.items(), key=lambda x: -x[1]):
        print(f"  {area}: {count}")


if __name__ == '__main__':
    main()
