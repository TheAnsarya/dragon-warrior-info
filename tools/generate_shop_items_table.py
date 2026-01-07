#!/usr/bin/env python3
"""
Generate Shop Items Table for Dragon Warrior

Reads shop data from JSON and generates the ShopItemsTbl assembly code
for inclusion in Bank00.asm.
"""

import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import json
from pathlib import Path

# Paths
JSON_PATH = Path(__file__).parent.parent / "assets" / "json" / "shops.json"
OUTPUT_PATH = Path(__file__).parent.parent / "source_files" / "generated" / "shop_items_table.asm"

# Item names for comments (index -> name)
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
}


def generate_shop_items_table():
	"""Generate ShopItemsTbl assembly from JSON."""
	print(f"Reading: {JSON_PATH}")

	with open(JSON_PATH, "r") as f:
		shops = json.load(f)

	lines = [
		";----------------------------------------------------------------------------------------------------",
		"; Shop Items Table - Generated from assets/json/shops.json",
		"; To modify shop inventories, edit the JSON file and rebuild",
		";----------------------------------------------------------------------------------------------------",
		"",
		";The following table contains the items available in the shops. The first 7 rows are the items",
		";in the weapons and armor shops while the remaining rows are for the tool shops. The values in",
		";the table correspond to the item indexes in the ItemCostTbl above.",
		"",
		"ShopItemsTbl:",
		"",
	]

	# Process shops in order
	for shop_id in range(12):
		shop_key = str(shop_id)
		if shop_key not in shops:
			print(f"  WARNING: Shop {shop_id} not found in JSON")
			continue

		shop = shops[shop_key]
		name = shop["name"]
		items = shop["item_indices"]

		# Add shop comment
		lines.append(f";{name}.")

		# Generate item bytes
		item_bytes = ", ".join(f"${i:02X}" for i in items)
		item_names = ", ".join(ITEM_NAMES.get(i, f"?{i:02X}") for i in items)

		if items:
			lines.append(f"        .byte {item_bytes}, $fd  ;{item_names}")
		else:
			lines.append(f"        .byte $fd  ;Empty shop")

		lines.append("")

	# Write output
	print(f"Writing: {OUTPUT_PATH}")
	OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

	with open(OUTPUT_PATH, "w", newline="\n") as f:
		f.write("\n".join(lines))

	print("Done!")


if __name__ == "__main__":
	generate_shop_items_table()
