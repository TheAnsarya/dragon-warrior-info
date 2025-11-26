"""
Asset Reinsertion Tool for Dragon Warrior ROM modifications.

This tool allows modifying extracted JSON data and reinserting changes
back into the ROM with validation.

Features:
- Modify monster stats and reinsert into ROM
- Modify spell data and reinsert into ROM
- Modify item/equipment stats and reinsert into ROM
- Validate all changes before insertion
- Create backup ROMs automatically
- Generate modification reports
"""

import json
import shutil
from pathlib import Path
from typing import Dict, List, Any, Tuple
from datetime import datetime

class DragonWarriorROMModifier:
    """Modify Dragon Warrior ROM using extracted JSON data."""

    def __init__(self, rom_path: str, output_path: str = None):
        """
        Initialize ROM modifier.

        Args:
            rom_path: Path to original ROM
            output_path: Path for modified ROM (default: rom_path with _modified suffix)
        """
        self.rom_path = Path(rom_path)

        # Read original ROM
        with open(rom_path, 'rb') as f:
            self.rom_data = bytearray(f.read())

        # Set output path
        if output_path:
            self.output_path = Path(output_path)
        else:
            self.output_path = self.rom_path.with_stem(
                self.rom_path.stem + "_modified"
            )

        # Data offsets (from extract_all_data.py)
        self.MONSTER_STATS_OFFSET = 0x5E5B  # 39 monsters, 16 bytes each
        self.SPELL_DATA_OFFSET = 0x7CFD     # 10 spells, MP costs
        self.WEAPON_DATA_OFFSET = 0x7CF5    # 7 weapons, attack power
        self.ARMOR_DATA_OFFSET = 0x7D05     # 7 armor, defense power
        self.SHIELD_DATA_OFFSET = 0x7D0D    # 3 shields, defense power

        # Modification log
        self.modifications = []

    def create_backup(self) -> Path:
        """Create timestamped backup of original ROM."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.rom_path.with_stem(
            f"{self.rom_path.stem}_backup_{timestamp}"
        )
        shutil.copy2(self.rom_path, backup_path)
        print(f"Created backup: {backup_path}")
        return backup_path

    def validate_monster_stats(self, monster: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate monster stat values are within acceptable ranges.

        Args:
            monster: Monster dict with stats

        Returns:
            (is_valid, error_message) tuple
        """
        # All stats must be 0-255 (single byte)
        stats_to_check = [
            ('attack_power', 0, 255),
            ('defense_power', 0, 255),
            ('hp', 0, 255),
            ('spell', 0, 255),  # 0 = no spell
            ('agility', 0, 255),
            ('magic_defense', 0, 255),
            ('experience', 0, 255),
            ('gold', 0, 255)
        ]

        for stat_name, min_val, max_val in stats_to_check:
            if stat_name not in monster:
                return False, f"Missing stat: {stat_name}"

            value = monster[stat_name]
            if not isinstance(value, int):
                return False, f"{stat_name} must be integer, got {type(value)}"

            if not (min_val <= value <= max_val):
                return False, f"{stat_name}={value} out of range [{min_val}-{max_val}]"

        return True, ""

    def modify_monster_stats(self, monsters_file: Path) -> int:
        """
        Modify monster stats from JSON file.

        Args:
            monsters_file: Path to monsters.json with modified stats

        Returns:
            Number of monsters modified
        """
        # Load modified monster data
        with open(monsters_file, 'r') as f:
            monsters = json.load(f)

        modifications_made = 0

        for monster in monsters:
            # Validate stats
            is_valid, error = self.validate_monster_stats(monster)
            if not is_valid:
                print(f"WARNING: Skipping {monster.get('name', 'Unknown')}: {error}")
                continue

            # Calculate ROM offset for this monster
            monster_id = monster['id']
            offset = self.MONSTER_STATS_OFFSET + (monster_id * 16)

            # Pack stats into 8 bytes (+ 8 unused bytes)
            stats_bytes = bytes([
                monster['attack_power'],
                monster['defense_power'],
                monster['hp'],
                monster['spell'],
                monster['agility'],
                monster['magic_defense'],
                monster['experience'],
                monster['gold']
            ])

            # Read original stats for comparison
            original_stats = self.rom_data[offset:offset + 8]

            if stats_bytes != original_stats:
                # Write modified stats
                self.rom_data[offset:offset + 8] = stats_bytes

                # Log modification
                self.modifications.append({
                    "type": "monster_stats",
                    "monster_id": monster_id,
                    "monster_name": monster['name'],
                    "offset": f"${offset:04X}",
                    "original": list(original_stats),
                    "modified": list(stats_bytes),
                    "changes": self._get_stat_changes(original_stats, stats_bytes, monster)
                })

                modifications_made += 1
                print(f"Modified {monster['name']} stats at ${offset:04X}")

        return modifications_made

    def _get_stat_changes(self, original: bytes, modified: bytes,
                         monster: Dict[str, Any]) -> List[str]:
        """Get human-readable list of stat changes."""
        stat_names = ['attack_power', 'defense_power', 'hp', 'spell',
                     'agility', 'magic_defense', 'experience', 'gold']
        changes = []

        for i, stat_name in enumerate(stat_names):
            if original[i] != modified[i]:
                changes.append(
                    f"{stat_name}: {original[i]} → {modified[i]}"
                )

        return changes

    def modify_spell_data(self, spells_file: Path) -> int:
        """
        Modify spell MP costs from JSON file.

        Args:
            spells_file: Path to spells.json with modified MP costs

        Returns:
            Number of spells modified
        """
        # Load modified spell data
        with open(spells_file, 'r') as f:
            spells = json.load(f)

        modifications_made = 0

        for spell in spells:
            spell_id = spell['id']
            mp_cost = spell['mp_cost']

            # Validate MP cost
            if not (0 <= mp_cost <= 255):
                print(f"WARNING: Skipping {spell['name']}: MP cost {mp_cost} out of range")
                continue

            # Calculate ROM offset
            offset = self.SPELL_DATA_OFFSET + spell_id

            # Read original MP cost
            original_mp = self.rom_data[offset]

            if mp_cost != original_mp:
                # Write modified MP cost
                self.rom_data[offset] = mp_cost

                # Log modification
                self.modifications.append({
                    "type": "spell_mp_cost",
                    "spell_id": spell_id,
                    "spell_name": spell['name'],
                    "offset": f"${offset:04X}",
                    "original_mp": original_mp,
                    "modified_mp": mp_cost
                })

                modifications_made += 1
                print(f"Modified {spell['name']} MP cost: {original_mp} → {mp_cost}")

        return modifications_made

    def modify_equipment_stats(self, equipment_file: Path) -> int:
        """
        Modify equipment (weapons, armor, shields) stats from JSON file.

        Args:
            equipment_file: Path to items_equipment.json with modified stats

        Returns:
            Number of items modified
        """
        # Load modified equipment data
        with open(equipment_file, 'r') as f:
            data = json.load(f)

        modifications_made = 0

        # Process weapons
        for weapon in data.get('weapons', []):
            if 'attack' in weapon:
                offset = self.WEAPON_DATA_OFFSET + weapon.get('id', 0)
                attack = weapon['attack']

                if 0 <= attack <= 255:
                    original = self.rom_data[offset]
                    if attack != original:
                        self.rom_data[offset] = attack
                        self.modifications.append({
                            "type": "weapon_attack",
                            "name": weapon['name'],
                            "offset": f"${offset:04X}",
                            "original": original,
                            "modified": attack
                        })
                        modifications_made += 1
                        print(f"Modified {weapon['name']} attack: {original} → {attack}")

        # Process armor
        for armor in data.get('armor', []):
            if 'defense' in armor:
                offset = self.ARMOR_DATA_OFFSET + armor.get('id', 0)
                defense = armor['defense']

                if 0 <= defense <= 255:
                    original = self.rom_data[offset]
                    if defense != original:
                        self.rom_data[offset] = defense
                        self.modifications.append({
                            "type": "armor_defense",
                            "name": armor['name'],
                            "offset": f"${offset:04X}",
                            "original": original,
                            "modified": defense
                        })
                        modifications_made += 1
                        print(f"Modified {armor['name']} defense: {original} → {defense}")

        # Process shields
        for shield in data.get('shields', []):
            if 'defense' in shield:
                offset = self.SHIELD_DATA_OFFSET + shield.get('id', 0)
                defense = shield['defense']

                if 0 <= defense <= 255:
                    original = self.rom_data[offset]
                    if defense != original:
                        self.rom_data[offset] = defense
                        self.modifications.append({
                            "type": "shield_defense",
                            "name": shield['name'],
                            "offset": f"${offset:04X}",
                            "original": original,
                            "modified": defense
                        })
                        modifications_made += 1
                        print(f"Modified {shield['name']} defense: {original} → {defense}")

        return modifications_made

    def save_modified_rom(self) -> Path:
        """Save modified ROM to output path."""
        with open(self.output_path, 'wb') as f:
            f.write(self.rom_data)
        print(f"\nSaved modified ROM: {self.output_path}")
        return self.output_path

    def generate_modification_report(self, output_dir: Path) -> Path:
        """
        Generate detailed report of all modifications made.

        Args:
            output_dir: Directory to save report

        Returns:
            Path to generated report
        """
        output_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = output_dir / f"modification_report_{timestamp}.json"

        report = {
            "timestamp": datetime.now().isoformat(),
            "original_rom": str(self.rom_path),
            "modified_rom": str(self.output_path),
            "total_modifications": len(self.modifications),
            "modifications_by_type": {},
            "modifications": self.modifications
        }

        # Count modifications by type
        for mod in self.modifications:
            mod_type = mod['type']
            report["modifications_by_type"][mod_type] = \
                report["modifications_by_type"].get(mod_type, 0) + 1

        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)

        print(f"\nGenerated modification report: {report_file}")

        # Print summary
        print("\n" + "="*60)
        print("MODIFICATION SUMMARY")
        print("="*60)
        print(f"Total modifications: {len(self.modifications)}")
        print("\nBy type:")
        for mod_type, count in report["modifications_by_type"].items():
            print(f"  {mod_type}: {count}")

        return report_file


def main():
    """Example usage of ROM modifier."""
    print("Dragon Warrior ROM Asset Reinsertion Tool")
    print("="*60)

    # Paths
    rom_path = "roms/Dragon Warrior (U) (PRG1) [!].nes"
    output_path = "output/dragon_warrior_modified.nes"

    # Initialize modifier
    modifier = DragonWarriorROMModifier(rom_path, output_path)

    # Create backup
    modifier.create_backup()

    print("\n" + "="*60)
    print("EXAMPLE: How to use this tool")
    print("="*60)
    print("""
1. Extract data using extract_all_data.py
   This creates: extracted_assets/data/monsters.json
                 extracted_assets/data/spells.json
                 extracted_assets/data/items_equipment.json

2. Modify the JSON files with desired changes
   Example: Edit monsters.json to change Slime HP from 3 to 10

3. Run this script to reinsert changes:

   from tools.reinsert_assets import DragonWarriorROMModifier

   modifier = DragonWarriorROMModifier(
       "roms/Dragon Warrior (U) (PRG1) [!].nes",
       "output/dragon_warrior_modified.nes"
   )

   # Create backup first
   modifier.create_backup()

   # Modify monster stats
   modifier.modify_monster_stats("extracted_assets/data/monsters.json")

   # Modify spell MP costs
   modifier.modify_spell_data("extracted_assets/data/spells.json")

   # Modify equipment stats
   modifier.modify_equipment_stats("extracted_assets/data/items_equipment.json")

   # Save modified ROM
   modifier.save_modified_rom()

   # Generate report
   modifier.generate_modification_report(Path("output/reports"))

4. Test modified ROM in emulator

5. Review modification report to verify changes
    """)

    print("="*60)
    print("Tool ready for use!")
    print("="*60)


if __name__ == "__main__":
    main()
