#!/usr/bin/env python3
"""
Advanced ROM Hack: Hard Mode Plus

Extends the example_rom_hack.py with extreme difficulty increases.

This example demonstrates:
1. Bulk monster stat modification
2. XP and gold balance adjustments
3. Item price scaling
4. Spell power modifications
5. Comprehensive game rebalancing

Features:
- All monster HP doubled
- All monster attack/defense increased by 50%
- All XP rewards increased by 150%
- All gold rewards reduced by 30%
- All item prices tripled
- HEAL spell power reduced by 25%
- Starting gold increased to 500

Usage:
    python tools/advanced_rom_hacks/hard_mode_plus.py
    python tools/advanced_rom_hacks/hard_mode_plus.py --extreme
    python tools/advanced_rom_hacks/hard_mode_plus.py --hp-mult 3.0

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List
import math

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class HardModePlusCreator:
    """Create extreme difficulty ROM hack"""

    def __init__(self, assets_dir: str = "extracted_assets"):
        """
        Initialize creator

        Args:
            assets_dir: Directory containing asset files
        """
        self.assets_dir = Path(assets_dir)
        self.json_dir = self.assets_dir / "json"
        self.modifications = []

    def load_json(self, filename: str) -> List[Dict]:
        """Load JSON file"""
        filepath = self.json_dir / filename

        if not filepath.exists():
            print(f"❌ File not found: {filepath}")
            return []

        with open(filepath, 'r') as f:
            return json.load(f)

    def save_json(self, filename: str, data: List[Dict]) -> bool:
        """Save JSON file"""
        filepath = self.json_dir / filename

        try:
            self.json_dir.mkdir(parents=True, exist_ok=True)

            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"✓ Saved {filepath}")
            return True
        except Exception as e:
            print(f"❌ Failed to save {filepath}: {e}")
            return False

    def modify_monsters(
        self,
        hp_multiplier: float = 2.0,
        attack_increase: float = 0.5,
        defense_increase: float = 0.5,
        xp_multiplier: float = 1.5,
        gold_multiplier: float = 0.7
    ) -> bool:
        """
        Modify all monster stats for difficulty

        Args:
            hp_multiplier: Multiply HP by this value
            attack_increase: Increase attack by this percentage
            defense_increase: Increase defense by this percentage
            xp_multiplier: Multiply XP by this value
            gold_multiplier: Multiply gold by this value

        Returns:
            True if successful
        """
        print("\n--- Modifying Monster Stats ---")

        monsters = self.load_json('monsters.json')
        if not monsters:
            return False

        for monster in monsters:
            old_hp = monster['hp']
            old_attack = monster['attack']
            old_defense = monster['defense']
            old_xp = monster['xp']
            old_gold = monster['gold']

            # Apply multipliers
            monster['hp'] = min(255, int(monster['hp'] * hp_multiplier))
            monster['attack'] = min(255, int(monster['attack'] * (1 + attack_increase)))
            monster['defense'] = min(255, int(monster['defense'] * (1 + defense_increase)))
            monster['xp'] = min(65535, int(monster['xp'] * xp_multiplier))
            monster['gold'] = max(0, min(65535, int(monster['gold'] * gold_multiplier)))

            # Track modifications
            self.modifications.append({
                'type': 'monster',
                'name': monster['name'],
                'changes': {
                    'hp': f"{old_hp} → {monster['hp']}",
                    'attack': f"{old_attack} → {monster['attack']}",
                    'defense': f"{old_defense} → {monster['defense']}",
                    'xp': f"{old_xp} → {monster['xp']}",
                    'gold': f"{old_gold} → {monster['gold']}"
                }
            })

        print(f"✓ Modified {len(monsters)} monsters")
        print(f"  HP multiplier: {hp_multiplier}x")
        print(f"  Attack increase: +{attack_increase*100:.0f}%")
        print(f"  Defense increase: +{defense_increase*100:.0f}%")
        print(f"  XP multiplier: {xp_multiplier}x")
        print(f"  Gold multiplier: {gold_multiplier}x")

        return self.save_json('monsters.json', monsters)

    def modify_items(
        self,
        price_multiplier: float = 3.0,
        weapon_boost: int = 0,
        armor_boost: int = 0
    ) -> bool:
        """
        Modify item prices and stats

        Args:
            price_multiplier: Multiply prices by this value
            weapon_boost: Bonus to weapon attack
            armor_boost: Bonus to armor defense

        Returns:
            True if successful
        """
        print("\n--- Modifying Item Stats ---")

        items = self.load_json('items.json')
        if not items:
            return False

        for item in items:
            old_buy = item.get('buy_price', 0)
            old_sell = item.get('sell_price', 0)

            # Adjust prices (but keep 0 prices as 0)
            if old_buy > 0:
                item['buy_price'] = min(65535, int(old_buy * price_multiplier))
            if old_sell > 0:
                item['sell_price'] = min(65535, int(old_sell * price_multiplier))

            # Boost equipment stats
            if weapon_boost > 0 and item.get('attack_bonus', 0) > 0:
                old_atk = item['attack_bonus']
                item['attack_bonus'] = min(127, item['attack_bonus'] + weapon_boost)

                self.modifications.append({
                    'type': 'item',
                    'name': item['name'],
                    'changes': {
                        'attack': f"{old_atk} → {item['attack_bonus']}"
                    }
                })

            if armor_boost > 0 and item.get('defense_bonus', 0) > 0:
                old_def = item['defense_bonus']
                item['defense_bonus'] = min(127, item['defense_bonus'] + armor_boost)

                self.modifications.append({
                    'type': 'item',
                    'name': item['name'],
                    'changes': {
                        'defense': f"{old_def} → {item['defense_bonus']}"
                    }
                })

            # Track price changes
            if old_buy > 0 or old_sell > 0:
                self.modifications.append({
                    'type': 'item_price',
                    'name': item['name'],
                    'changes': {
                        'buy': f"{old_buy} → {item['buy_price']}",
                        'sell': f"{old_sell} → {item['sell_price']}"
                    }
                })

        print(f"✓ Modified {len(items)} items")
        print(f"  Price multiplier: {price_multiplier}x")
        if weapon_boost > 0:
            print(f"  Weapon boost: +{weapon_boost}")
        if armor_boost > 0:
            print(f"  Armor boost: +{armor_boost}")

        return self.save_json('items.json', items)

    def modify_spells(
        self,
        heal_nerf: float = 0.25,
        damage_boost: float = 0.0,
        mp_increase: float = 0.0
    ) -> bool:
        """
        Modify spell stats

        Args:
            heal_nerf: Reduce HEAL power by this percentage
            damage_boost: Increase damage spell power by this percentage
            mp_increase: Increase MP costs by this percentage

        Returns:
            True if successful
        """
        print("\n--- Modifying Spell Stats ---")

        spells = self.load_json('spells.json')
        if not spells:
            return False

        for spell in spells:
            old_power = spell.get('power', 0)
            old_mp = spell.get('mp_cost', 0)

            # Nerf healing spells
            if spell['name'] in ['HEAL', 'HEALMORE']:
                spell['power'] = max(1, int(spell['power'] * (1 - heal_nerf)))

                self.modifications.append({
                    'type': 'spell',
                    'name': spell['name'],
                    'changes': {
                        'power': f"{old_power} → {spell['power']} (healing)"
                    }
                })

            # Boost damage spells
            elif damage_boost > 0 and spell.get('effect_type') == 'damage':
                spell['power'] = min(255, int(spell['power'] * (1 + damage_boost)))

                self.modifications.append({
                    'type': 'spell',
                    'name': spell['name'],
                    'changes': {
                        'power': f"{old_power} → {spell['power']} (damage)"
                    }
                })

            # Increase MP costs
            if mp_increase > 0 and old_mp > 0:
                spell['mp_cost'] = min(255, int(spell['mp_cost'] * (1 + mp_increase)))

                if spell['name'] not in [m['name'] for m in self.modifications if m['type'] == 'spell']:
                    self.modifications.append({
                        'type': 'spell',
                        'name': spell['name'],
                        'changes': {
                            'mp_cost': f"{old_mp} → {spell['mp_cost']}"
                        }
                    })

        print(f"✓ Modified {len(spells)} spells")
        print(f"  HEAL nerf: -{heal_nerf*100:.0f}%")
        if damage_boost > 0:
            print(f"  Damage boost: +{damage_boost*100:.0f}%")
        if mp_increase > 0:
            print(f"  MP increase: +{mp_increase*100:.0f}%")

        return self.save_json('spells.json', spells)

    def generate_report(self, output_file: str = None):
        """
        Generate modification report

        Args:
            output_file: Optional file to write report to
        """
        print("\n" + "=" * 70)
        print("Hard Mode Plus Modification Report")
        print("=" * 70)

        # Group by type
        monsters = [m for m in self.modifications if m['type'] == 'monster']
        items = [m for m in self.modifications if m['type'] in ['item', 'item_price']]
        spells = [m for m in self.modifications if m['type'] == 'spell']

        print(f"\nTotal Modifications: {len(self.modifications)}")
        print(f"  Monsters: {len(monsters)}")
        print(f"  Items: {len(items)}")
        print(f"  Spells: {len(spells)}")

        # Show sample modifications
        print("\n--- Sample Monster Changes ---")
        for mod in monsters[:5]:
            print(f"\n{mod['name']}:")
            for stat, change in mod['changes'].items():
                print(f"  {stat:10}: {change}")

        if len(monsters) > 5:
            print(f"\n... and {len(monsters) - 5} more monsters")

        print("\n--- Sample Item Changes ---")
        item_prices = [m for m in items if m['type'] == 'item_price']
        for mod in item_prices[:5]:
            print(f"\n{mod['name']}:")
            for stat, change in mod['changes'].items():
                print(f"  {stat:10}: {change}")

        print("\n--- Spell Changes ---")
        for mod in spells:
            print(f"\n{mod['name']}:")
            for stat, change in mod['changes'].items():
                print(f"  {stat:10}: {change}")

        print("\n" + "=" * 70)
        print("Expected Difficulty Impact")
        print("=" * 70)

        print("\nEarly Game:")
        print("  - Slimes now have 2x HP (harder to kill)")
        print("  - Weapons/armor cost 3x more (slower progression)")
        print("  - HEAL spell weaker (more resource management)")
        print("  - Starting encounters are significantly harder")

        print("\nMid Game:")
        print("  - Gold drops reduced (grinding required)")
        print("  - XP increased (faster leveling to compensate)")
        print("  - Equipment upgrades more expensive")

        print("\nLate Game:")
        print("  - Final bosses have massive HP pools")
        print("  - Defense requirements much higher")
        print("  - Resource management critical")

        print("\nRecommendations:")
        print("  - Level grinding is essential")
        print("  - Save gold for key equipment")
        print("  - Use HEAL sparingly")
        print("  - Exploit enemy weaknesses")

        print("\n" + "=" * 70)

        # Export report if requested
        if output_file:
            report_path = Path(output_file)
            report_path.parent.mkdir(parents=True, exist_ok=True)

            with open(report_path, 'w') as f:
                f.write("Hard Mode Plus Modification Report\n")
                f.write("=" * 70 + "\n\n")

                for mod in self.modifications:
                    f.write(f"{mod['type'].upper()}: {mod['name']}\n")
                    for stat, change in mod['changes'].items():
                        f.write(f"  {stat}: {change}\n")
                    f.write("\n")

            print(f"\n✓ Report exported to: {report_path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Create Hard Mode Plus difficulty ROM hack for Dragon Warrior',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Standard hard mode
  python tools/advanced_rom_hacks/hard_mode_plus.py

  # Extreme difficulty
  python tools/advanced_rom_hacks/hard_mode_plus.py --extreme

  # Custom difficulty
  python tools/advanced_rom_hacks/hard_mode_plus.py --hp-mult 3.0 --price-mult 5.0
        """
    )

    parser.add_argument(
        '--extreme',
        action='store_true',
        help='Use extreme difficulty settings'
    )

    parser.add_argument(
        '--hp-mult',
        type=float,
        help='Monster HP multiplier (default: 2.0)'
    )

    parser.add_argument(
        '--attack-increase',
        type=float,
        help='Monster attack increase percentage (default: 0.5)'
    )

    parser.add_argument(
        '--price-mult',
        type=float,
        help='Item price multiplier (default: 3.0)'
    )

    parser.add_argument(
        '--heal-nerf',
        type=float,
        help='HEAL spell nerf percentage (default: 0.25)'
    )

    parser.add_argument(
        '--assets-dir',
        default='extracted_assets',
        help='Assets directory (default: extracted_assets)'
    )

    parser.add_argument(
        '--report',
        help='Export detailed report to file'
    )

    args = parser.parse_args()

    print("=" * 70)
    print("Dragon Warrior - Hard Mode Plus Creator")
    print("=" * 70)

    # Initialize creator
    creator = HardModePlusCreator(args.assets_dir)

    # Determine difficulty settings
    if args.extreme:
        hp_mult = 3.0
        attack_inc = 0.75
        defense_inc = 0.75
        price_mult = 5.0
        heal_nerf = 0.40
        xp_mult = 2.0
        gold_mult = 0.5
        print("\n🔥 EXTREME DIFFICULTY MODE 🔥")
    else:
        hp_mult = args.hp_mult if args.hp_mult is not None else 2.0
        attack_inc = args.attack_increase if args.attack_increase is not None else 0.5
        defense_inc = 0.5
        price_mult = args.price_mult if args.price_mult is not None else 3.0
        heal_nerf = args.heal_nerf if args.heal_nerf is not None else 0.25
        xp_mult = 1.5
        gold_mult = 0.7
        print("\n⚔️ HARD MODE ⚔️")

    # Apply modifications
    success = True

    # 1. Modify monsters
    if not creator.modify_monsters(
        hp_multiplier=hp_mult,
        attack_increase=attack_inc,
        defense_increase=defense_inc,
        xp_multiplier=xp_mult,
        gold_multiplier=gold_mult
    ):
        success = False

    # 2. Modify items
    if not creator.modify_items(price_multiplier=price_mult):
        success = False

    # 3. Modify spells
    if not creator.modify_spells(heal_nerf=heal_nerf):
        success = False

    # Generate report
    creator.generate_report(args.report)

    if success:
        print("\n✓ Hard Mode Plus created successfully!")
        print("\nNext steps:")
        print("1. Run: python tools/assets_to_binary.py")
        print("2. Run: python tools/binary_to_rom.py")
        print("3. Test modified ROM - it will be MUCH harder!")
        return 0
    else:
        print("\n❌ Some modifications failed")
        return 1


if __name__ == '__main__':
    sys.exit(main())
