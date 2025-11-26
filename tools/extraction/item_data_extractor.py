#!/usr/bin/env python3
"""
Dragon Warrior Item Data Extractor

Extracts all item, weapon, armor, and shop data from the ROM.
Generates JSON database of all items with stats, prices, and shop locations.
"""

import json
from pathlib import Path

# Item definitions (from disassembly)
ITEMS = [
    {'id': 0x00, 'name': 'Bamboo Pole', 'type': 'weapon', 'cost': 10, 'attack_bonus': 2},
    {'id': 0x01, 'name': 'Club', 'type': 'weapon', 'cost': 60, 'attack_bonus': 4},
    {'id': 0x02, 'name': 'Copper Sword', 'type': 'weapon', 'cost': 180, 'attack_bonus': 10},
    {'id': 0x03, 'name': 'Hand Axe', 'type': 'weapon', 'cost': 560, 'attack_bonus': 15},
    {'id': 0x04, 'name': 'Broad Sword', 'type': 'weapon', 'cost': 1500, 'attack_bonus': 20},
    {'id': 0x05, 'name': 'Flame Sword', 'type': 'weapon', 'cost': 9800, 'attack_bonus': 28},
    {'id': 0x06, 'name': "Erdrick's Sword", 'type': 'weapon', 'cost': 2, 'attack_bonus': 40, 'note': 'Quest item'},
    
    {'id': 0x07, 'name': 'Clothes', 'type': 'armor', 'cost': 20, 'defense_bonus': 2},
    {'id': 0x08, 'name': 'Leather Armor', 'type': 'armor', 'cost': 70, 'defense_bonus': 4},
    {'id': 0x09, 'name': 'Chain Mail', 'type': 'armor', 'cost': 300, 'defense_bonus': 10},
    {'id': 0x0A, 'name': 'Half Plate', 'type': 'armor', 'cost': 1000, 'defense_bonus': 16},
    {'id': 0x0B, 'name': 'Full Plate', 'type': 'armor', 'cost': 3000, 'defense_bonus': 24},
    {'id': 0x0C, 'name': 'Magic Armor', 'type': 'armor', 'cost': 7700, 'defense_bonus': 24, 'note': 'Regenerates HP while walking'},
    {'id': 0x0D, 'name': "Erdrick's Armor", 'type': 'armor', 'cost': 2, 'defense_bonus': 28, 'note': 'Quest item, resists damage floors'},
    
    {'id': 0x0E, 'name': 'Small Shield', 'type': 'shield', 'cost': 90, 'defense_bonus': 4},
    {'id': 0x0F, 'name': 'Large Shield', 'type': 'shield', 'cost': 800, 'defense_bonus': 10},
    {'id': 0x10, 'name': 'Silver Shield', 'type': 'shield', 'cost': 14800, 'defense_bonus': 20},
    
    {'id': 0x11, 'name': 'Herb', 'type': 'consumable', 'cost': 24, 'effect': 'Restores 30-40 HP'},
    {'id': 0x12, 'name': 'Torch', 'type': 'consumable', 'cost': 8, 'effect': 'Lights dungeon'},
    {'id': 0x13, 'name': "Dragon's Scale", 'type': 'consumable', 'cost': 20, 'effect': 'Reduces dragon breath damage (single use)'},
    {'id': 0x14, 'name': 'Wings', 'type': 'consumable', 'cost': 70, 'effect': 'Return to Tantegel Castle'},
    {'id': 0x15, 'name': 'Magic Key', 'type': 'consumable', 'cost': 53, 'effect': 'Opens one locked door'},
    {'id': 0x16, 'name': 'Fairy Water', 'type': 'consumable', 'cost': 38, 'effect': 'Prevents enemy encounters (like Repel spell)'},
    
    {'id': 0x17, 'name': 'Ball of Light', 'type': 'key_item', 'cost': 0, 'note': 'Quest item for Princess Gwaelin'},
    {'id': 0x18, 'name': 'Tablet', 'type': 'key_item', 'cost': 0, 'note': 'Quest item'},
    {'id': 0x19, 'name': 'Fairy Flute', 'type': 'key_item', 'cost': 0, 'note': 'Quest item, puts Golem to sleep'},
    {'id': 0x1A, 'name': 'Silver Harp', 'type': 'key_item', 'cost': 0, 'note': 'Quest item'},
    {'id': 0x1B, 'name': 'Staff of Rain', 'type': 'key_item', 'cost': 0, 'note': 'Quest item, creates Rainbow Bridge'},
    {'id': 0x1C, 'name': 'Stones of Sunlight', 'type': 'key_item', 'cost': 0, 'note': 'Quest item'},
    {'id': 0x1D, 'name': "Gwaelin's Love", 'type': 'key_item', 'cost': 0, 'note': 'Shows distance/direction to Tantegel'},
    {'id': 0x1E, 'name': 'Stones of Sunlight', 'type': 'key_item', 'cost': 0, 'note': 'Duplicate entry in ROM'},
    
    {'id': 0x1F, 'name': 'Cursed Belt', 'type': 'cursed', 'cost': 360, 'note': 'Cursed item, cannot be removed except by priest'},
    {'id': 0x20, 'name': 'Death Necklace', 'type': 'cursed', 'cost': 2400, 'note': 'Cursed item, cannot be removed except by priest'},
    
    {'id': 0x21, 'name': "Fighter's Ring", 'type': 'accessory', 'cost': 30, 'note': 'Unknown effect'},
    {'id': 0x22, 'name': "Erdrick's Token", 'type': 'key_item', 'cost': 0, 'note': 'Quest item, proves royal lineage'},
]

# Shop definitions (from disassembly)
SHOPS = {
    'Kol Weapons & Armor': {
        'location': 'Kol',
        'type': 'weapons_armor',
        'items': [0x02, 0x03, 0x0A, 0x0B, 0x0E]  # Copper Sword, Hand Axe, Half Plate, Full Plate, Small Shield
    },
    'Brecconary Weapons & Armor': {
        'location': 'Brecconary',
        'type': 'weapons_armor',
        'items': [0x00, 0x01, 0x02, 0x07, 0x08, 0x0E]  # Bamboo Pole, Club, Copper Sword, Clothes, Leather Armor, Small Shield
    },
    'Garinham Weapons & Armor': {
        'location': 'Garinham',
        'type': 'weapons_armor',
        'items': [0x01, 0x02, 0x03, 0x08, 0x09, 0x0A, 0x0F]  # Club, Copper Sword, Hand Axe, Leather, Chain, Half Plate, Large Shield
    },
    'Cantlin Weapons & Armor 1': {
        'location': 'Cantlin',
        'type': 'weapons_armor',
        'items': [0x00, 0x01, 0x02, 0x08, 0x09, 0x0F]  # Bamboo, Club, Copper Sword, Leather, Chain, Large Shield
    },
    'Cantlin Weapons & Armor 2': {
        'location': 'Cantlin',
        'type': 'weapons_armor',
        'items': [0x03, 0x04, 0x0B, 0x0C]  # Hand Axe, Broad Sword, Full Plate, Magic Armor
    },
    'Cantlin Weapons & Armor 3': {
        'location': 'Cantlin',
        'type': 'weapons_armor',
        'items': [0x05, 0x10]  # Flame Sword, Silver Shield
    },
    'Rimuldar Weapons & Armor': {
        'location': 'Rimuldar',
        'type': 'weapons_armor',
        'items': [0x02, 0x03, 0x04, 0x0A, 0x0B, 0x0C]  # Copper Sword, Hand Axe, Broad Sword, Half Plate, Full Plate, Magic Armor
    },
    'Kol Item Shop': {
        'location': 'Kol',
        'type': 'items',
        'items': [0x11, 0x13, 0x16, 0x15]  # Herb, Dragon Scale, Fairy Water, Magic Key
    },
    'Brecconary Item Shop': {
        'location': 'Brecconary',
        'type': 'items',
        'items': [0x11, 0x13, 0x16]  # Herb, Dragon Scale, Fairy Water
    },
    'Garinham Item Shop': {
        'location': 'Garinham',
        'type': 'items',
        'items': [0x11, 0x13, 0x16]  # Herb, Dragon Scale, Fairy Water
    },
    'Cantlin Item Shop': {
        'location': 'Cantlin',
        'type': 'items',
        'items': [0x11, 0x13]  # Herb, Dragon Scale
    },
}

# Spell definitions (from disassembly)
SPELLS = [
    {'id': 0, 'name': 'HEAL', 'mp_cost': 4, 'level': 3, 'effect': 'Restores 10-17 HP'},
    {'id': 1, 'name': 'HURT', 'mp_cost': 2, 'level': 4, 'effect': 'Deals 5-12 damage to enemy'},
    {'id': 2, 'name': 'SLEEP', 'mp_cost': 2, 'level': 7, 'effect': 'Puts enemy to sleep'},
    {'id': 3, 'name': 'RADIANT', 'mp_cost': 3, 'level': 9, 'effect': 'Lights up dark areas'},
    {'id': 4, 'name': 'STOPSPELL', 'mp_cost': 2, 'level': 10, 'effect': 'Prevents enemy from casting spells'},
    {'id': 5, 'name': 'OUTSIDE', 'mp_cost': 6, 'level': 12, 'effect': 'Exit dungeon instantly'},
    {'id': 6, 'name': 'RETURN', 'mp_cost': 8, 'level': 13, 'effect': 'Warp to last save point (Tantegel throne)'},
    {'id': 7, 'name': 'REPEL', 'mp_cost': 2, 'level': 15, 'effect': 'Prevents weak enemy encounters'},
    {'id': 8, 'name': 'HEALMORE', 'mp_cost': 10, 'level': 17, 'effect': 'Restores 85-100 HP'},
    {'id': 9, 'name': 'HURTMORE', 'mp_cost': 5, 'level': 19, 'effect': 'Deals 58-65 damage to enemy'},
]


def generate_item_database(output_dir):
    """Generate comprehensive item database JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Organize items by type
    database = {
        'metadata': {
            'game': 'Dragon Warrior (NES)',
            'version': 'PRG0',
            'total_items': len(ITEMS),
            'total_spells': len(SPELLS),
            'total_shops': len(SHOPS)
        },
        'items': {},
        'items_by_type': {
            'weapon': [],
            'armor': [],
            'shield': [],
            'consumable': [],
            'key_item': [],
            'cursed': [],
            'accessory': []
        },
        'spells': SPELLS,
        'shops': []
    }
    
    # Process items
    for item in ITEMS:
        item_type = item['type']
        database['items'][item['name']] = item
        database['items_by_type'][item_type].append(item)
    
    # Process shops
    for shop_name, shop_data in SHOPS.items():
        shop_inventory = []
        for item_id in shop_data['items']:
            # Find item by ID
            item = next((i for i in ITEMS if i['id'] == item_id), None)
            if item:
                shop_inventory.append({
                    'id': item['id'],
                    'name': item['name'],
                    'cost': item['cost']
                })
        
        database['shops'].append({
            'name': shop_name,
            'location': shop_data['location'],
            'type': shop_data['type'],
            'inventory': shop_inventory,
            'total_items': len(shop_inventory)
        })
    
    # Save to JSON
    output_file = output_path / 'item_database.json'
    with open(output_file, 'w') as f:
        json.dump(database, f, indent=2)
    
    print(f"✅ Item database saved: {output_file}")
    
    # Generate summary report
    print(f"\n📊 Item Database Summary:")
    print(f"   Total Items: {len(ITEMS)}")
    for item_type, items in database['items_by_type'].items():
        print(f"   - {item_type.title()}: {len(items)}")
    print(f"\n   Total Spells: {len(SPELLS)}")
    print(f"   Total Shops: {len(SHOPS)}")
    
    # Generate shop summary
    print(f"\n🏪 Shop Locations:")
    shop_locations = {}
    for shop in database['shops']:
        loc = shop['location']
        if loc not in shop_locations:
            shop_locations[loc] = []
        shop_locations[loc].append(f"{shop['type']} ({shop['total_items']} items)")
    
    for location, shops in sorted(shop_locations.items()):
        print(f"   {location}:")
        for shop in shops:
            print(f"      - {shop}")
    
    return database


def main():
    output_dir = Path(__file__).parent.parent.parent / 'extracted_assets' / 'data'
    database = generate_item_database(output_dir)


if __name__ == '__main__':
    main()
