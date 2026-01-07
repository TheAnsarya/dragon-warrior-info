#!/usr/bin/env python3
"""
Generate Dragon Warrior Item Cost Table for Bank00.asm

Reads item data from assets/json/items.json and generates ItemCostTbl assembly.
Items.json uses correct ROM ordering where ID matches ItemCostTbl index.
"""
import json
from pathlib import Path

# Paths
JSON_PATH = Path(__file__).parent.parent / "assets" / "json" / "items.json"
OUTPUT_PATH = Path(__file__).parent.parent / "source_files" / "generated" / "item_cost_table.asm"


def generate_item_cost_table():
	"""Generate ItemCostTbl assembly from items.json."""
	print(f"Reading: {JSON_PATH}")

	with open(JSON_PATH, "r") as f:
		items = json.load(f)

	lines = [
		";----------------------------------------------------------------------------------------------------",
		"; Item Cost Table - Generated from assets/json/items.json",
		"; To modify item prices, edit the JSON file and rebuild",
		";----------------------------------------------------------------------------------------------------",
		"",
		"ItemCostTbl:",
	]

	# Process items in order (0-32)
	for item_id in range(33):
		item_key = str(item_id)
		if item_key not in items:
			print(f"  WARNING: Item {item_id} not found in JSON, using 0")
			price = 0
			name = f"Unknown_{item_id}"
		else:
			item = items[item_key]
			price = item.get("buy_price", 0)
			name = item.get("name", f"Unknown_{item_id}")

		# Generate word entry
		lines.append(f"        .word ${price:04X}             ;{name:20s} - {price:5d}  gold.")

	# Write output
	print(f"Writing: {OUTPUT_PATH}")
	OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

	with open(OUTPUT_PATH, "w", newline="\n") as f:
		f.write("\n".join(lines))

	print(f"Generated {len(items)} item costs")


def main():
	"""Generate item cost table"""
	generate_item_cost_table()
	return 0


if __name__ == "__main__":
	import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
	sys.exit(main())
