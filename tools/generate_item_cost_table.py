#!/usr/bin/env python3
"""
Generate Dragon Warrior Item Cost Table for Bank00.asm
This generates the ItemCostTbl in the exact format needed by Bank00.asm
"""
import json
from pathlib import Path
from typing import Dict

# Item order in Bank00 ItemCostTbl (different from item ID order!)
# Based on Bank00.asm L9947-L9987
BANK00_ITEM_ORDER = [
    # Weapons
    ("Bamboo Pole", 10),       # Missing from JSON, use default
    ("Club", None),             # ID 1
    ("Copper Sword", None),     # ID 2  
    ("Hand Axe", None),         # ID 3
    ("Broad Sword", None),      # ID 4
    ("Flame Sword", None),      # ID 5
    ("Erdrick's Sword", None),  # ID 6
    # Armor
    ("Clothes", None),          # ID 7
    ("Leather Armor", None),    # ID 8
    ("Chain Mail", None),       # ID 9
    ("Half Plate", None),       # ID 10
    ("Full Plate", None),       # ID 11
    ("Magic Armor", None),      # ID 12
    ("Erdrick's Armor", None),  # ID 13
    # Shields
    ("Small Shield", None),     # ID 14
    ("Large Shield", None),     # ID 15
    ("Silver Shield", None),    # ID 16
    # Items
    ("Herb", None),             # ID 18
    ("Magic Key", None),        # ID 20
    ("Torch", None),            # ID 0
    ("Fairy Water", 38),        # Missing from JSON, use default
    ("Wings", 70),              # Missing from JSON, use default
    ("Dragon's Scale", 20),     # Missing from JSON, use default (capitalization issue?)
    ("Fairy Flute", 0),         # Missing from JSON, use default
    ("Fighter's Ring", 30),     # Missing from JSON, use default  
    ("Erdrick's Token", None),  # ID 21
    ("Gwaelin's Love", None),   # ID 22
    ("Cursed Belt", None),      # ID 23
    ("Silver Harp", None),      # ID 24
    ("Death Necklace", None),   # ID 25
    ("Stones of Sunlight", None), # ID 26
    ("Staff of Rain", None),    # ID 27
    ("Rainbow Drop", None),     # ID 28
]


def generate_item_cost_table(items_json_path: Path) -> str:
    """Generate Bank00-style item cost table ASM code"""
    
    # Load items from JSON
    with open(items_json_path, 'r') as f:
        items = json.load(f)
    
    # Create name->item lookup
    items_by_name = {}
    for item_id, item in items.items():
        items_by_name[item['name']] = item
    
    asm_lines = [
        "ItemCostTbl:"
    ]
    
    label_offset = 0x9947  # Starting label
    
    for idx, (item_name, default_price) in enumerate(BANK00_ITEM_ORDER):
        label = f"L{label_offset + idx*2:04X}"
        
        # Get item from JSON or use default
        if item_name in items_by_name:
            item = items_by_name[item_name]
            price = item['buy_price']
            comment = f"{item_name:18s} - {price:5d}  gold."
        else:
            # Use default price for missing items
            price = default_price if default_price is not None else 0
            comment = f"{item_name:18s} - {price:5d}  gold. (default)"
        
        asm_lines.append(f"{label}:  .word ${price:04X}             ;{comment}")
    
    return "\n".join(asm_lines)


def main():
    """Generate item cost table"""
    items_json = Path("assets/json/items_corrected.json")
    
    if not items_json.exists():
        items_json = Path("assets/json/items.json")
    
    if not items_json.exists():
        print("❌ No items JSON file found!")
        return 1
    
    print(f"Generating item cost table from {items_json.name}...")
    table_asm = generate_item_cost_table(items_json)
    
    output_file = Path("source_files/generated/item_cost_table.asm")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w') as f:
        f.write(table_asm)
    
    print(f"✓ Generated {output_file}")
    print(f"  {len(BANK00_ITEM_ORDER)} items in cost table")
    
    # Display the table
    print("\nGenerated table:")
    print(table_asm)
    
    return 0


if __name__ == "__main__":
    import sys
    sys.exit(main())
