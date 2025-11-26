"""
Example: Create a "Hard Mode" ROM hack for Dragon Warrior

This example demonstrates how to use the extraction and reinsertion tools
to create a modified version of Dragon Warrior with increased difficulty.

Changes made in this example:
- All monsters get +50% HP, attack, and defense
- Boss monsters (Dragonlord, Dragon, etc.) get +100% HP
- All spells cost +50% MP
- Equipment prices increased by 2x
- Weapon attack reduced by 20% (make combat harder)
"""

import json
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from tools.reinsert_assets import DragonWarriorROMModifier

def create_hard_mode():
    """Create a Hard Mode Dragon Warrior ROM."""
    
    print("="*60)
    print("Dragon Warrior - Hard Mode ROM Hack Creator")
    print("="*60)
    
    # Paths
    original_rom = Path("roms/Dragon Warrior (U) (PRG1) [!].nes")
    output_rom = Path("output/Dragon Warrior - Hard Mode.nes")
    monsters_file = Path("extracted_assets/data/monsters.json")
    spells_file = Path("extracted_assets/data/spells.json")
    equipment_file = Path("extracted_assets/data/items_equipment.json")
    
    # Step 1: Load and modify monster data
    print("\n1. Loading monster data...")
    with open(monsters_file, 'r') as f:
        monsters = json.load(f)
    
    print(f"   Found {len(monsters)} monsters")
    
    # Identify boss monsters
    boss_monsters = [
        "Dragonlord", "Dragonlord (Dragon Form)", 
        "Red Dragon", "Blue Dragon", "Green Dragon",
        "Golem", "Stoneman", "Armored Knight",
        "Demon Knight", "Axe Knight"
    ]
    
    print("\n2. Modifying monster stats...")
    for monster in monsters:
        name = monster['name']
        
        # Determine multiplier
        if name in boss_monsters:
            hp_mult = 2.0    # Bosses get +100% HP
            stat_mult = 1.5  # +50% attack/defense
            print(f"   BOSS: {name} - HP x2.0, Stats x1.5")
        else:
            hp_mult = 1.5    # Regular monsters get +50%
            stat_mult = 1.5
        
        # Apply multipliers
        monster['hp'] = min(255, int(monster['hp'] * hp_mult))
        monster['attack_power'] = min(255, int(monster['attack_power'] * stat_mult))
        monster['defense_power'] = min(255, int(monster['defense_power'] * stat_mult))
        
        # Slightly increase EXP and gold to compensate
        monster['experience'] = min(255, int(monster['experience'] * 1.2))
        monster['gold'] = min(255, int(monster['gold'] * 1.2))
    
    # Save modified monsters
    modified_monsters_file = Path("output/hard_mode_monsters.json")
    modified_monsters_file.parent.mkdir(parents=True, exist_ok=True)
    with open(modified_monsters_file, 'w') as f:
        json.dump(monsters, f, indent=2)
    print(f"   Saved modified monsters to {modified_monsters_file}")
    
    # Step 2: Modify spell MP costs
    print("\n3. Loading and modifying spell data...")
    with open(spells_file, 'r') as f:
        spells = json.load(f)
    
    for spell in spells:
        original_mp = spell['mp_cost']
        spell['mp_cost'] = min(255, int(original_mp * 1.5))
        print(f"   {spell['name']}: MP {original_mp} → {spell['mp_cost']}")
    
    modified_spells_file = Path("output/hard_mode_spells.json")
    with open(modified_spells_file, 'w') as f:
        json.dump(spells, f, indent=2)
    print(f"   Saved modified spells to {modified_spells_file}")
    
    # Step 3: Modify equipment
    print("\n4. Loading and modifying equipment...")
    with open(equipment_file, 'r') as f:
        equipment = json.load(f)
    
    # Reduce weapon attack (make combat harder)
    for weapon in equipment.get('weapons', []):
        if 'attack' in weapon:
            original = weapon['attack']
            weapon['attack'] = max(1, int(original * 0.8))  # Reduce by 20%
            print(f"   {weapon['name']}: Attack {original} → {weapon['attack']}")
        
        if 'price' in weapon:
            weapon['price'] = int(weapon['price'] * 2)  # Double price
    
    # Increase armor prices
    for armor in equipment.get('armor', []):
        if 'price' in armor:
            armor['price'] = int(armor['price'] * 2)
    
    for shield in equipment.get('shields', []):
        if 'price' in shield:
            shield['price'] = int(shield['price'] * 2)
    
    modified_equipment_file = Path("output/hard_mode_equipment.json")
    with open(modified_equipment_file, 'w') as f:
        json.dump(equipment, f, indent=2)
    print(f"   Saved modified equipment to {modified_equipment_file}")
    
    # Step 4: Create modified ROM
    print("\n5. Creating modified ROM...")
    modifier = DragonWarriorROMModifier(str(original_rom), str(output_rom))
    
    # Create backup
    backup_path = modifier.create_backup()
    print(f"   Created backup: {backup_path}")
    
    # Apply modifications
    print("\n6. Reinserting modified data into ROM...")
    monsters_modified = modifier.modify_monster_stats(modified_monsters_file)
    print(f"   Modified {monsters_modified} monsters")
    
    spells_modified = modifier.modify_spell_data(modified_spells_file)
    print(f"   Modified {spells_modified} spells")
    
    equipment_modified = modifier.modify_equipment_stats(modified_equipment_file)
    print(f"   Modified {equipment_modified} equipment items")
    
    # Save modified ROM
    modifier.save_modified_rom()
    
    # Generate report
    report_path = modifier.generate_modification_report(Path("output/reports"))
    
    print("\n" + "="*60)
    print("HARD MODE ROM CREATION COMPLETE!")
    print("="*60)
    print(f"\nModified ROM: {output_rom}")
    print(f"Modification Report: {report_path}")
    print("\nChanges Summary:")
    print(f"  - {monsters_modified} monsters modified (+50% HP/stats, bosses +100% HP)")
    print(f"  - {spells_modified} spells modified (+50% MP cost)")
    print(f"  - {equipment_modified} equipment modified (weapons -20% attack, prices x2)")
    print("\nTest the ROM in your favorite NES emulator!")
    print("Recommended: FCEUX, Mesen, or Nestopia")
    print("="*60)


def create_easy_mode():
    """Create an Easy Mode Dragon Warrior ROM."""
    
    print("="*60)
    print("Dragon Warrior - Easy Mode ROM Hack Creator")
    print("="*60)
    
    # Similar to hard mode but with opposite changes
    print("\nEasy Mode features:")
    print("  - All monsters: -30% HP, attack, defense")
    print("  - All spells: -30% MP cost")
    print("  - Weapons: +50% attack power")
    print("  - Equipment prices: -50%")
    print("\nImplementation left as exercise for the user!")
    print("Follow the hard_mode example and reverse the multipliers.")


def create_chaos_mode():
    """Create a Chaos Mode with randomized stats."""
    
    import random
    
    print("="*60)
    print("Dragon Warrior - Chaos Mode ROM Hack Creator")
    print("="*60)
    
    print("\nChaos Mode features:")
    print("  - Randomized monster stats (50%-200% of original)")
    print("  - Randomized spell MP costs (1-20 MP)")
    print("  - Randomized weapon/armor stats")
    print("  - Randomized equipment prices")
    print("\nImplementation left as exercise for the user!")
    print("Use random.randint() to randomize values within valid ranges (0-255).")


if __name__ == "__main__":
    import sys
    
    print("\nDragon Warrior ROM Hack Examples")
    print("="*60)
    print("\nAvailable modes:")
    print("  1. Hard Mode - Increased difficulty")
    print("  2. Easy Mode - Reduced difficulty")
    print("  3. Chaos Mode - Randomized stats")
    print("\nUsage:")
    print("  python tools/example_rom_hack.py hard")
    print("  python tools/example_rom_hack.py easy")
    print("  python tools/example_rom_hack.py chaos")
    
    if len(sys.argv) < 2:
        print("\nNo mode specified. Run with 'hard', 'easy', or 'chaos' argument.")
        print("\nExample: python tools/example_rom_hack.py hard")
        sys.exit(0)
    
    mode = sys.argv[1].lower()
    
    if mode == "hard":
        create_hard_mode()
    elif mode == "easy":
        create_easy_mode()
    elif mode == "chaos":
        create_chaos_mode()
    else:
        print(f"\nUnknown mode: {mode}")
        print("Use 'hard', 'easy', or 'chaos'")
