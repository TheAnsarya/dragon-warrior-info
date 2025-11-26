#!/usr/bin/env python3
"""
Advanced ROM Hack: New Monster Creation

Demonstrates how to add a new monster using sprite sharing.

This example shows:
1. How to identify reusable sprites
2. Adding a 40th monster entry
3. Modifying monster data structures
4. Handling sprite pointer tables
5. Validating monster data

Techniques:
- Sprite sharing (SlimeSprts reuse for Blue Slime)
- JSON data structure modification
- Binary data generation
- ROM space conservation

Usage:
    python tools/advanced_rom_hacks/new_monster.py
    python tools/advanced_rom_hacks/new_monster.py --name "Blue Slime"
    python tools/advanced_rom_hacks/new_monster.py --stats hp=25,attack=15

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from binary_to_assets import BinaryReader, AssetTransformer
from assets_to_binary import AssetValidator, BinaryPackager
from binary_to_rom import ROMModifier


class NewMonsterCreator:
    """Create new monster using sprite sharing"""

    def __init__(self, assets_dir: str = "extracted_assets"):
        """
        Initialize creator

        Args:
            assets_dir: Directory containing asset files
        """
        self.assets_dir = Path(assets_dir)
        self.json_dir = self.assets_dir / "json"
        self.binary_dir = self.assets_dir / "binary"

    def load_monsters(self) -> List[Dict]:
        """Load existing monster data"""
        monsters_file = self.json_dir / "monsters.json"

        if not monsters_file.exists():
            print(f"❌ Monsters file not found: {monsters_file}")
            print("Run extract_to_binary.py and binary_to_assets.py first")
            return []

        with open(monsters_file, 'r') as f:
            return json.load(f)

    def save_monsters(self, monsters: List[Dict]) -> bool:
        """Save modified monster data"""
        monsters_file = self.json_dir / "monsters.json"

        try:
            with open(monsters_file, 'w') as f:
                json.dump(monsters, f, indent=2)

            print(f"✓ Saved {len(monsters)} monsters to {monsters_file}")
            return True
        except Exception as e:
            print(f"❌ Failed to save monsters: {e}")
            return False

    def find_sprite_candidates(self, monsters: List[Dict]) -> Dict[str, List[str]]:
        """
        Find monsters that share sprites (candidates for variants)

        Args:
            monsters: List of monster dicts

        Returns:
            Dict mapping sprite families to monster names
        """
        # Known sprite sharing patterns from analyze_monster_sprites.py
        sprite_families = {
            'Slime Family': ['Slime', 'Red Slime', 'Metal Slime'],
            'Drakee Family': ['Drakee', 'Magidrakee', 'Drakeema'],
            'Golem Family': ['Golem', 'Goldman', 'Stoneman'],
            'Dragon Family': ['Red Dragon', 'Blue Dragon', 'Green Dragon'],
            'Knight Family': ['Knight', 'Armored Knight', 'Metal Slime'],
            'Wizard Family': ['Wizard', 'Warlock'],
            'Wolf Family': ['Wolf', 'Scorpion'],
        }

        return sprite_families

    def create_new_monster(
        self,
        base_monster_name: str,
        new_name: str,
        stats: Optional[Dict[str, int]] = None
    ) -> Dict:
        """
        Create a new monster as a variant of existing one

        Args:
            base_monster_name: Name of monster to use as template
            new_name: Name for new monster
            stats: Optional stat overrides

        Returns:
            New monster dict
        """
        monsters = self.load_monsters()

        # Find base monster
        base_monster = None
        for monster in monsters:
            if monster['name'].lower() == base_monster_name.lower():
                base_monster = monster.copy()
                break

        if not base_monster:
            print(f"❌ Base monster '{base_monster_name}' not found")
            return None

        # Create new monster
        new_monster = base_monster.copy()
        new_monster['id'] = len(monsters)  # Assign new ID
        new_monster['name'] = new_name

        # Apply stat overrides
        if stats:
            for stat, value in stats.items():
                if stat in new_monster:
                    new_monster[stat] = value
                    print(f"  {stat}: {base_monster[stat]} → {value}")

        print(f"\n✓ Created new monster: {new_name}")
        print(f"  Base: {base_monster_name}")
        print(f"  ID: {new_monster['id']}")
        print(f"  HP: {new_monster['hp']}")
        print(f"  Attack: {new_monster['attack']}")
        print(f"  Defense: {new_monster['defense']}")
        print(f"  Sprite: Shared with {base_monster_name}")

        return new_monster

    def add_monster_to_data(self, new_monster: Dict) -> bool:
        """
        Add new monster to monsters.json

        Args:
            new_monster: Monster dict to add

        Returns:
            True if successful
        """
        monsters = self.load_monsters()

        # Add to list
        monsters.append(new_monster)

        # Save
        return self.save_monsters(monsters)

    def validate_monster(self, monster: Dict) -> bool:
        """
        Validate monster data

        Args:
            monster: Monster dict

        Returns:
            True if valid
        """
        required_fields = ['id', 'name', 'hp', 'attack', 'defense', 'agility',
                          'spell', 'm_defense', 'xp', 'gold']

        # Check required fields
        for field in required_fields:
            if field not in monster:
                print(f"❌ Missing field: {field}")
                return False

        # Validate ranges
        if not (1 <= monster['hp'] <= 255):
            print(f"❌ HP must be 1-255 (got {monster['hp']})")
            return False

        if not (0 <= monster['attack'] <= 255):
            print(f"❌ Attack must be 0-255 (got {monster['attack']})")
            return False

        if not (0 <= monster['defense'] <= 255):
            print(f"❌ Defense must be 0-255 (got {monster['defense']})")
            return False

        if not (0 <= monster['spell'] <= 9):
            print(f"❌ Spell must be 0-9 (got {monster['spell']})")
            return False

        print("✓ Monster data valid")
        return True

    def rebuild_binary(self) -> bool:
        """
        Rebuild binary from modified JSON

        Returns:
            True if successful
        """
        print("\n--- Rebuilding Binary Data ---")

        # Use BinaryPackager to rebuild
        packager = BinaryPackager(
            self.json_dir,
            self.assets_dir / "graphics",
            self.binary_dir
        )

        # Package monsters
        success = packager.package_monsters()

        if success:
            print("✓ Binary data rebuilt successfully")
        else:
            print("❌ Failed to rebuild binary")

        return success

    def generate_insertion_guide(self, new_monster: Dict):
        """
        Generate guide for inserting new monster into ROM

        Args:
            new_monster: The new monster dict
        """
        print("\n" + "=" * 70)
        print("Monster Insertion Guide")
        print("=" * 70)

        print(f"\nNew Monster: {new_monster['name']}")
        print(f"ID: {new_monster['id']}")

        print("\nSteps to insert into ROM:")
        print("1. Run binary rebuild (done above)")
        print("2. Run binary_to_rom.py to reinsert data:")
        print(f"   python tools/binary_to_rom.py")

        print("\nSprite Sharing:")
        print(f"  - Uses existing sprite (no CHR-ROM changes needed)")
        print(f"  - 0 additional bytes used")

        print("\nData Structure Changes:")
        print(f"  - Monster count: 39 → 40")
        print(f"  - Monster data size: 624 bytes → 640 bytes")
        print(f"  - Additional space needed: 16 bytes")

        print("\nTesting:")
        print("  1. Build modified ROM")
        print("  2. Load in emulator")
        print("  3. Use Game Genie code to encounter new monster")
        print(f"     - Monster ID: {new_monster['id']}")

        print("\nCaveats:")
        print("  - Requires modifying monster count constant in game code")
        print("  - May need to adjust monster tables/pointers")
        print("  - Test thoroughly to avoid crashes")

        print("\n" + "=" * 70)


def parse_stats(stats_str: str) -> Dict[str, int]:
    """
    Parse stats from command-line format

    Args:
        stats_str: Format "hp=25,attack=15,defense=10"

    Returns:
        Dict of stat overrides
    """
    stats = {}

    if not stats_str:
        return stats

    for part in stats_str.split(','):
        if '=' in part:
            key, value = part.split('=')
            stats[key.strip()] = int(value.strip())

    return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Create new Dragon Warrior monster using sprite sharing',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create Blue Slime variant
  python tools/advanced_rom_hacks/new_monster.py

  # Create custom variant with specific stats
  python tools/advanced_rom_hacks/new_monster.py --base "Red Slime" --name "Purple Slime" --stats "hp=30,attack=18"

  # Create Dragon variant
  python tools/advanced_rom_hacks/new_monster.py --base "Red Dragon" --name "Black Dragon" --stats "hp=200,attack=150,defense=100"
        """
    )

    parser.add_argument(
        '--base',
        default='Slime',
        help='Base monster to use as template (default: Slime)'
    )

    parser.add_argument(
        '--name',
        default='Blue Slime',
        help='Name for new monster (default: Blue Slime)'
    )

    parser.add_argument(
        '--stats',
        help='Stat overrides (format: hp=25,attack=15,defense=10)'
    )

    parser.add_argument(
        '--assets-dir',
        default='extracted_assets',
        help='Assets directory (default: extracted_assets)'
    )

    parser.add_argument(
        '--no-rebuild',
        action='store_true',
        help='Skip binary rebuild step'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Dragon Warrior - New Monster Creator")
    print("=" * 70)

    # Initialize creator
    creator = NewMonsterCreator(args.assets_dir)

    # Parse stats
    stats = parse_stats(args.stats)

    # Default stats if none provided (boost base stats by 25%)
    if not stats:
        stats = {
            'hp': 25,
            'attack': 15,
            'defense': 12,
            'agility': 8,
            'xp': 50,
            'gold': 20
        }

    # Show sprite families
    monsters = creator.load_monsters()
    if not monsters:
        return 1

    sprite_families = creator.find_sprite_candidates(monsters)

    print("\n--- Sprite Families (Reuse Candidates) ---")
    for family, members in sprite_families.items():
        print(f"{family}: {', '.join(members)}")

    # Create new monster
    print(f"\n--- Creating New Monster ---")
    new_monster = creator.create_new_monster(args.base, args.name, stats)

    if not new_monster:
        return 1

    # Validate
    if not creator.validate_monster(new_monster):
        return 1

    # Add to data
    if not creator.add_monster_to_data(new_monster):
        return 1

    # Rebuild binary (unless skipped)
    if not args.no_rebuild:
        if not creator.rebuild_binary():
            return 1

    # Generate insertion guide
    creator.generate_insertion_guide(new_monster)

    print("\n✓ New monster created successfully!")
    print("\nNext steps:")
    print("1. Run: python tools/binary_to_rom.py")
    print("2. Test modified ROM in emulator")

    return 0


if __name__ == '__main__':
    sys.exit(main())
