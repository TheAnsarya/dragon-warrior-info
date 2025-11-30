#!/usr/bin/env python3
"""
Extract shop data from Dragon Warrior ROM

Extracts the ShopItemsTbl from Bank00 and saves to JSON format.
This creates correct shop data matching the ROM structure.
"""

import json
from pathlib import Path

# ROM path
ROM_PATH = Path(__file__).parent.parent / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"
OUTPUT_PATH = Path(__file__).parent.parent / "assets" / "json" / "shops.json"

# NES header size
NES_HEADER_SIZE = 16

# ShopItemsTbl offsets (Bank00 address - 0x8000 + NES_HEADER_SIZE)
# Bank00 starts after header at offset 0x10
SHOP_ITEMS_OFFSET = 0x1991 + NES_HEADER_SIZE  # L9991 in Bank00

# Inn costs offset
INN_COST_OFFSET = 0x198c + NES_HEADER_SIZE  # L998C in Bank00

# Item names by index (from ItemCostTbl order in Bank00)
ITEM_NAMES = {
	0x00: "Bamboo Pole",
	0x01: "Club",
	0x02: "Copper Sword",
	0x03: "Hand Axe",
	0x04: "Broad Sword",
	0x05: "Flame Sword",
	0x06: "Erdrick's Sword",
	0x07: "Clothes",
	0x08: "Leather Armor",
	0x09: "Chain Mail",
	0x0a: "Half Plate",
	0x0b: "Full Plate",
	0x0c: "Magic Armor",
	0x0d: "Erdrick's Armor",
	0x0e: "Small Shield",
	0x0f: "Large Shield",
	0x10: "Silver Shield",
	0x11: "Herb",
	0x12: "Magic Key",
	0x13: "Torch",
	0x14: "Fairy Water",
	0x15: "Wings",
	0x16: "Dragon's Scale",
	0x17: "Fairy Flute",
	0x18: "Fighter's Ring",
	0x19: "Erdrick's Token",
	0x1a: "Gwaelin's Love",
	0x1b: "Cursed Belt",
	0x1c: "Silver Harp",
	0x1d: "Death Necklace",
	0x1e: "Stones of Sunlight",
	0x1f: "Staff of Rain",
	0x20: "Rainbow Drop",
}

# Shop definitions with known offsets
SHOP_DEFINITIONS = [
	# (id, name, location, offset_from_L9991)
	(0, "Koll Weapons & Armor", "Koll", 0x00),           # L9991: 6 items
	(1, "Brecconary Weapons & Armor", "Brecconary", 0x06),  # L9997: 7 items
	(2, "Garinham Weapons & Armor", "Garinham", 0x0d),   # L999E: 8 items
	(3, "Cantlin Weapons & Armor 1", "Cantlin", 0x15),   # L99A6: 7 items
	(4, "Cantlin Weapons & Armor 2", "Cantlin", 0x1c),   # L99AD: 5 items
	(5, "Cantlin Weapons & Armor 3", "Cantlin", 0x21),   # L99B2: 3 items
	(6, "Rimuldar Weapons & Armor", "Rimuldar", 0x24),   # L99B5: 7 items
	(7, "Koll Item Shop", "Koll", 0x2b),                 # L99BC: 5 items
	(8, "Brecconary Item Shop", "Brecconary", 0x30),     # L99C1: 4 items
	(9, "Garinham Item Shop", "Garinham", 0x34),         # L99C5: 4 items
	(10, "Cantlin Item Shop 1", "Cantlin", 0x38),        # L99C9: 3 items
	(11, "Cantlin Item Shop 2", "Cantlin", 0x3b),        # L99CC: 3 items
]

# Inn cost definitions (5 towns)
INN_TOWNS = ["Kol", "Brecconary", "Garinham", "Cantlin", "Rimuldar"]


def extract_shops():
	"""Extract shop data from ROM."""
	print(f"Reading ROM: {ROM_PATH}")

	with open(ROM_PATH, "rb") as f:
		rom_data = f.read()

	print(f"ROM size: {len(rom_data)} bytes")

	# Read inn costs
	inn_costs = {}
	for i, town in enumerate(INN_TOWNS):
		inn_costs[town] = rom_data[INN_COST_OFFSET + i]

	print("\nInn costs:")
	for town, cost in inn_costs.items():
		print(f"  {town}: {cost} gold")

	# Extract shop data
	shops = {}

	print("\nShop data:")
	for shop_id, name, location, offset in SHOP_DEFINITIONS:
		items = []
		pos = SHOP_ITEMS_OFFSET + offset

		# Read items until terminator (0xfd)
		while rom_data[pos] != 0xfd:
			item_idx = rom_data[pos]
			items.append(item_idx)
			pos += 1

			# Safety check
			if len(items) > 20:
				print(f"  WARNING: Too many items in shop {name}, stopping")
				break

		# Categorize items
		weapons = [i for i in items if 0x00 <= i <= 0x06]
		armor = [i for i in items if 0x07 <= i <= 0x10]  # Includes shields
		tools = [i for i in items if i >= 0x11]

		# Get inn price for this location
		inn_price = inn_costs.get(location)

		shop_data = {
			"id": shop_id,
			"name": name,
			"location": location,
			"item_indices": items,
			"items": [ITEM_NAMES.get(i, f"Unknown_{i:02X}") for i in items],
			"weapons": weapons,
			"armor": armor,
			"tools": tools,
			"inn_price": inn_price if "Item" not in name else None
		}

		shops[str(shop_id)] = shop_data

		print(f"  {name}:")
		print(f"    Items: {[f'${i:02X}' for i in items]}")
		print(f"    Names: {shop_data['items']}")

	return shops


def main():
	shops = extract_shops()

	# Save to JSON
	print(f"\nSaving to: {OUTPUT_PATH}")
	with open(OUTPUT_PATH, "w") as f:
		json.dump(shops, f, indent="\t")

	print("Done!")


if __name__ == "__main__":
	main()
