#!/usr/bin/env python3
"""Test item extraction with corrected ROM offsets"""
import sys
import json
sys.path.insert(0, 'tools/extraction')

from data_extractor import DragonWarriorDataExtractor

# Create extractor (using PRG1 as per ROM_REQUIREMENTS.md)
extractor = DragonWarriorDataExtractor('roms/Dragon Warrior (U) (PRG1) [!].nes', 'assets')

# Extract items
items = extractor.extract_item_data()

# Print key items to verify correctness
print("=" * 80)
print("ITEM EXTRACTION VERIFICATION")
print("=" * 80)
print()

# Check critical items
test_items = [0, 1, 2, 5, 7, 14, 17, 18]
for item_id in test_items:
    if item_id in items:
        item = items[item_id]
        print(f"ID {item.id:2d}: {item.name:20s} Type:{str(item.item_type):15s} "
              f"Attack:{item.attack_power:3d} Defense:{item.defense_power:3d} "
              f"Price:{item.buy_price:5d} Effect:{item.effect or 'None'}")

print()
print("=" * 80)
print("EXPECTED VALUES:")
print("=" * 80)
print("ID  0: Torch                 Type:ItemType.TOOL   Attack:  0 Defense:  0 Effect:light")
print("ID  1: Club                  Type:ItemType.WEAPON Attack:  4 Defense:  0 Effect:None")
print("ID  2: Copper Sword          Type:ItemType.WEAPON Attack: 10 Defense:  0 Effect:None")
print("ID  5: Flame Sword           Type:ItemType.WEAPON Attack: 28 Defense:  0 Effect:None")
print("ID  7: Clothes               Type:ItemType.ARMOR  Attack:  0 Defense:  0 Effect:None")
print("ID 14: Small Shield          Type:ItemType.SHIELD Attack:  0 Defense:  4 Effect:None")
print("ID 17: Erdrick's Shield      Type:ItemType.SHIELD Attack:  0 Defense: 25 Effect:None")
print("ID 18: Herb                  Type:ItemType.TOOL   Attack:  0 Defense:  0 Effect:heal")

# Save to JSON file
output_data = {}
for item_id, item in items.items():
    output_data[item_id] = {
        'id': item.id,
        'name': item.name,
        'item_type': str(item.item_type),
        'attack_power': item.attack_power,
        'defense_power': item.defense_power,
        'buy_price': item.buy_price,
        'sell_price': item.sell_price,
        'equippable': item.equippable,
        'useable': item.useable,
        'sprite_id': item.sprite_id,
        'description': item.description,
        'effect': item.effect
    }

with open('assets/json/items_corrected.json', 'w') as f:
    json.dump(output_data, f, indent=2)

print()
print("✓ Saved corrected item data to: assets/json/items_corrected.json")
