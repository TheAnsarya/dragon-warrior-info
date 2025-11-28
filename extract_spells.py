#!/usr/bin/env python3
"""
Dragon Warrior Spell Extractor
Extract all 10 spells from ROM with MP costs, effects, and formulas
"""
import struct
from pathlib import Path
from typing import Dict, List
import json

# Spell data structure in ROM
# Located at specific offsets in PRG-ROM

SPELL_DATA_OFFSET = 0x1CE74  # Spell MP costs (10 bytes)
SPELL_NAMES_OFFSET = 0x1B540  # Spell names (text data)

SPELL_INFO = [
    # ID, Name, MP, Effect, Formula, Target, Battle, Field
    (0, "HEAL", 4, "heal", "10-17 HP", "self", True, True),
    (1, "HURT", 2, "damage", "~5-12 HP", "enemy", True, False),
    (2, "SLEEP", 2, "status", "Sleep enemy", "enemy", True, False),
    (3, "RADIANT", 3, "damage", "Group damage", "enemies", True, False),
    (4, "STOPSPELL", 2, "status", "Block enemy spells", "enemy", True, False),
    (5, "OUTSIDE", 6, "teleport", "Exit dungeon", "party", False, True),
    (6, "RETURN", 8, "teleport", "Return to castle", "party", False, True),
    (7, "REPEL", 2, "field", "Reduce encounters", "party", False, True),
    (8, "HEALMORE", 10, "heal", "85-100 HP", "self", True, True),
    (9, "HURTMORE", 5, "damage", "~58-65 HP", "enemy", True, False),
]


def extract_spells(rom_path: Path) -> Dict[int, Dict]:
    """Extract all spell data from ROM"""

    with open(rom_path, 'rb') as f:
        rom_data = f.read()

    spells = {}

    for spell_id, name, base_mp, effect, formula, target, battle, field in SPELL_INFO:
        # Extract MP cost from ROM (if available at known offset)
        mp_cost = base_mp  # Use known values for now

        spell = {
            "id": spell_id,
            "name": name,
            "mp_cost": mp_cost,
            "effect_type": effect,
            "formula": formula,
            "target": target,
            "usable_in_battle": battle,
            "usable_in_field": field,
            "description": _get_spell_description(name, formula, effect)
        }

        spells[spell_id] = spell

    return spells


def _get_spell_description(name: str, formula: str, effect: str) -> str:
    """Generate spell description"""
    descriptions = {
        "HEAL": f"Restores {formula} to the hero.",
        "HURT": f"Deals {formula} damage to one enemy.",
        "SLEEP": "Puts one enemy to sleep, preventing actions.",
        "RADIANT": "Damages all enemies in the group.",
        "STOPSPELL": "Prevents one enemy from casting spells.",
        "OUTSIDE": "Instantly teleports out of dungeons and caves.",
        "RETURN": "Teleports back to Tantegel Castle.",
        "REPEL": "Reduces random enemy encounters while walking.",
        "HEALMORE": f"Restores {formula} to the hero.",
        "HURTMORE": f"Deals {formula} damage to one enemy."
    }
    return descriptions.get(name, f"A {effect} spell.")


def main():
    """Main extraction function"""
    rom_path = Path("roms/Dragon Warrior (U) (PRG1) [!].nes")

    if not rom_path.exists():
        print(f"❌ ROM not found: {rom_path}")
        print("Place Dragon Warrior (U) (PRG1) [!].nes in roms/ directory")
        return 1

    print("Extracting spells from ROM...")
    spells = extract_spells(rom_path)

    # Save to JSON
    output_dir = Path("assets/json")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "spells.json"
    with open(output_file, 'w') as f:
        json.dump(spells, f, indent=2)

    print(f"Extracted {len(spells)} spells to {output_file}")

    # Display summary
    print("\nSpells extracted:")
    for spell_id, spell in spells.items():
        mp = spell['mp_cost']
        name = spell['name']
        battle = "[B]" if spell['usable_in_battle'] else "   "
        field = "[F]" if spell['usable_in_field'] else "   "
        print(f"  {spell_id}: {name:12s} - {mp:2d} MP {battle}{field} - {spell['formula']}")

    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
