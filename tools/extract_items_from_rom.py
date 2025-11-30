#!/usr/bin/env python3
"""
Extract items from Dragon Warrior ROM

Extracts item data from ROM and creates properly-ordered items.json
matching the ROM's ItemCostTbl order.
"""

import json
from pathlib import Path

# ROM path
ROM_PATH = Path(__file__).parent.parent / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"
OUTPUT_PATH = Path(__file__).parent.parent / "assets" / "json" / "items.json"
BACKUP_PATH = Path(__file__).parent.parent / "assets" / "backups"

# NES header size
NES_HEADER_SIZE = 16

# ItemCostTbl offset (Bank00 $9947 → ROM offset 0x1947 + header)
ITEM_COST_OFFSET = 0x1947 + NES_HEADER_SIZE

# WeaponsBonusTbl offset ($99cf)
WEAPON_BONUS_OFFSET = 0x19cf + NES_HEADER_SIZE

# ArmorBonusTbl offset ($99d7)
ARMOR_BONUS_OFFSET = 0x19d7 + NES_HEADER_SIZE

# ShieldBonusTbl offset ($99df)
SHIELD_BONUS_OFFSET = 0x19df + NES_HEADER_SIZE

# Item definitions matching ROM order from ItemCostTbl
# Index 0-6: Weapons, 7-13: Armor, 14-16: Shields, 17+: Items
ITEMS = [
	# Weapons (indices 0-6)
	{"id": 0, "name": "Bamboo Pole", "item_type": "weapon"},
	{"id": 1, "name": "Club", "item_type": "weapon"},
	{"id": 2, "name": "Copper Sword", "item_type": "weapon"},
	{"id": 3, "name": "Hand Axe", "item_type": "weapon"},
	{"id": 4, "name": "Broad Sword", "item_type": "weapon"},
	{"id": 5, "name": "Flame Sword", "item_type": "weapon"},
	{"id": 6, "name": "Erdrick's Sword", "item_type": "weapon"},
	# Armor (indices 7-13)
	{"id": 7, "name": "Clothes", "item_type": "armor"},
	{"id": 8, "name": "Leather Armor", "item_type": "armor"},
	{"id": 9, "name": "Chain Mail", "item_type": "armor"},
	{"id": 10, "name": "Half Plate", "item_type": "armor"},
	{"id": 11, "name": "Full Plate", "item_type": "armor"},
	{"id": 12, "name": "Magic Armor", "item_type": "armor"},
	{"id": 13, "name": "Erdrick's Armor", "item_type": "armor"},
	# Shields (indices 14-16)
	{"id": 14, "name": "Small Shield", "item_type": "shield"},
	{"id": 15, "name": "Large Shield", "item_type": "shield"},
	{"id": 16, "name": "Silver Shield", "item_type": "shield"},
	# Consumables/Items (indices 17+)
	{"id": 17, "name": "Herb", "item_type": "consumable", "effect": "heal", "description": "A medicinal herb that restores 30-40 HP."},
	{"id": 18, "name": "Magic Key", "item_type": "consumable", "effect": "unlock", "description": "Opens one locked door."},
	{"id": 19, "name": "Torch", "item_type": "consumable", "effect": "light", "description": "Lights up dark dungeons."},
	{"id": 20, "name": "Fairy Water", "item_type": "consumable", "effect": "repel", "description": "Prevents weak enemy encounters."},
	{"id": 21, "name": "Wings", "item_type": "consumable", "effect": "return", "description": "Return to Tantegel Castle."},
	{"id": 22, "name": "Dragon's Scale", "item_type": "consumable", "effect": "dragon_resist", "description": "Reduces dragon breath damage."},
	{"id": 23, "name": "Fairy Flute", "item_type": "key_item", "effect": "golem_sleep", "description": "Puts the Golem to sleep."},
	{"id": 24, "name": "Fighter's Ring", "item_type": "accessory", "effect": "attack_boost", "description": "Boosts attack power slightly."},
	{"id": 25, "name": "Erdrick's Token", "item_type": "key_item", "effect": None, "description": "Proof of Erdrick's lineage."},
	{"id": 26, "name": "Gwaelin's Love", "item_type": "key_item", "effect": "distance", "description": "Shows distance to Tantegel."},
	{"id": 27, "name": "Cursed Belt", "item_type": "cursed", "effect": "curse", "description": "A cursed item that cannot be removed."},
	{"id": 28, "name": "Silver Harp", "item_type": "key_item", "effect": "monster_attract", "description": "Attracts monsters when played."},
	{"id": 29, "name": "Death Necklace", "item_type": "cursed", "effect": "curse", "description": "A cursed item that cannot be removed."},
	{"id": 30, "name": "Stones of Sunlight", "item_type": "key_item", "effect": None, "description": "Creates Rainbow Bridge with Staff of Rain."},
	{"id": 31, "name": "Staff of Rain", "item_type": "key_item", "effect": None, "description": "Creates Rainbow Bridge with Stones of Sunlight."},
	{"id": 32, "name": "Rainbow Drop", "item_type": "key_item", "effect": "bridge", "description": "Creates the Rainbow Bridge to Charlock."},
]

# Weapon bonus values (from WeaponsBonusTbl)
WEAPON_BONUSES = [0, 2, 4, 10, 15, 20, 28, 40]  # None through Erdrick's Sword

# Armor bonus values (from ArmorBonusTbl)
ARMOR_BONUSES = [0, 2, 4, 10, 16, 24, 24, 28]  # None through Erdrick's Armor

# Shield bonus values (from ShieldBonusTbl)
SHIELD_BONUSES = [0, 4, 10, 20]  # None through Silver Shield


def extract_items():
	"""Extract item data from ROM."""
	print(f"Reading ROM: {ROM_PATH}")

	with open(ROM_PATH, "rb") as f:
		rom_data = f.read()

	print(f"ROM size: {len(rom_data)} bytes")

	items = {}

	for item in ITEMS:
		item_id = item["id"]
		item_data = item.copy()

		# Read buy price (2 bytes, little-endian) from ItemCostTbl
		price_offset = ITEM_COST_OFFSET + (item_id * 2)
		if price_offset + 1 < len(rom_data):
			buy_price = rom_data[price_offset] | (rom_data[price_offset + 1] << 8)
		else:
			buy_price = 0

		item_data["buy_price"] = buy_price
		item_data["sell_price"] = buy_price // 2  # Sell price is always half

		# Set attack/defense bonuses based on type
		item_type = item["item_type"]

		if item_type == "weapon":
			# Weapon index is 0-6, bonus index is 1-7 (0 is "None")
			bonus_idx = item_id + 1 if item_id < len(WEAPON_BONUSES) - 1 else 0
			item_data["attack_power"] = WEAPON_BONUSES[bonus_idx] if bonus_idx < len(WEAPON_BONUSES) else 0
			item_data["defense_power"] = 0
			item_data["equippable"] = True
			item_data["useable"] = False
		elif item_type == "armor":
			# Armor index is 7-13 (Clothes to Erdrick's Armor), bonus index 1-7
			armor_idx = item_id - 6  # Clothes is id 7, bonus index 1
			item_data["attack_power"] = 0
			item_data["defense_power"] = ARMOR_BONUSES[armor_idx] if 0 < armor_idx < len(ARMOR_BONUSES) else 0
			item_data["equippable"] = True
			item_data["useable"] = False
		elif item_type == "shield":
			# Shield index is 14-16, bonus index 1-3
			shield_idx = item_id - 13  # Small Shield is id 14, bonus index 1
			item_data["attack_power"] = 0
			item_data["defense_power"] = SHIELD_BONUSES[shield_idx] if 0 < shield_idx < len(SHIELD_BONUSES) else 0
			item_data["equippable"] = True
			item_data["useable"] = False
		else:
			item_data["attack_power"] = 0
			item_data["defense_power"] = 0
			item_data["equippable"] = False
			item_data["useable"] = item_type in ["consumable", "key_item"]

		# Add description if not already present
		if "description" not in item_data:
			item_data["description"] = f"A {item_type} used by brave adventurers."

		if "effect" not in item_data:
			item_data["effect"] = None

		items[str(item_id)] = item_data

		print(f"  {item_id:2d}: {item['name']:20s} - {buy_price:5d} gold, ATK: {item_data['attack_power']:2d}, DEF: {item_data['defense_power']:2d}")

	return items


def main():
	items = extract_items()

	# Create backup directory
	BACKUP_PATH.mkdir(parents=True, exist_ok=True)

	# Backup existing file if it exists
	if OUTPUT_PATH.exists():
		import datetime
		timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
		backup_file = BACKUP_PATH / f"items_backup_{timestamp}.json"
		print(f"\nBacking up existing file to: {backup_file}")
		with open(OUTPUT_PATH, "r") as f:
			existing = f.read()
		with open(backup_file, "w") as f:
			f.write(existing)

	# Save to JSON
	print(f"\nSaving to: {OUTPUT_PATH}")
	with open(OUTPUT_PATH, "w") as f:
		json.dump(items, f, indent="\t")

	print("Done!")


if __name__ == "__main__":
	main()
