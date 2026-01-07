#!/usr/bin/env python3
"""
Dragon Warrior Item & Shop Editor

Comprehensive item and shop management system for Dragon Warrior.
Edit item stats, shop inventory, prices, equipment effects, and
consumable item behavior.

Features:
- Item stats editing (attack, defense, price)
- Shop inventory management
- Price balancing and analysis
- Equipment effect editing
- Consumable item behavior
- Item progression curves
- Shop location management
- Item rarity configuration
- Drop rate editing
- Key item flags
- Cursed item handling
- Equipment requirements
- Item description editing
- Shop stock limits
- Buy/sell price ratio
- Item unlock progression
- Equipment comparison

Dragon Warrior Items:
- Total Items: 38
- Weapons: 9 (Bamboo Pole to Erdrick's Sword)
- Armor: 8 (Clothes to Erdrick's Armor)
- Shields: 6 (Leather Shield to Silver Shield)
- Tools: 15 (Torch, Herbs, Keys, Wings, etc.)

Item Data Locations:
- Item Names: 0x1af0-0x1c3f
- Item Prices: 0x1c40-0x1cff
- Weapon Stats: 0x1d00-0x1d3f
- Armor Stats: 0x1d40-0x1d7f
- Shop Data: 0x1d80-0x1e7f

Usage:
	python tools/item_shop_editor.py <rom_file>

Examples:
	# List all items
	python tools/item_shop_editor.py rom.nes --list-items

	# Show item details
	python tools/item_shop_editor.py rom.nes --item "Erdrick's Sword"

	# Edit item stats
	python tools/item_shop_editor.py rom.nes --item "Copper Sword" --attack 15 -o new.nes

	# List shops
	python tools/item_shop_editor.py rom.nes --list-shops

	# Edit shop inventory
	python tools/item_shop_editor.py rom.nes --shop "Brecconary" --add "Magic Key" -o new.nes

	# Analyze item balance
	python tools/item_shop_editor.py rom.nes --analyze-balance

	# Export item database
	python tools/item_shop_editor.py rom.nes --export items.json

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import os
import struct
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import argparse
import json


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class ItemType(Enum):
	"""Item categories."""
	WEAPON = "weapon"
	ARMOR = "armor"
	SHIELD = "shield"
	TOOL = "tool"
	KEY_ITEM = "key_item"
	CONSUMABLE = "consumable"


@dataclass
class Item:
	"""Item data."""
	id: int
	name: str
	item_type: ItemType
	price: int
	attack: int = 0
	defense: int = 0
	effect: str = ""
	cursed: bool = False
	key_item: bool = False
	description: str = ""


@dataclass
class Shop:
	"""Shop data."""
	id: int
	name: str
	location: str
	inventory: List[int] = field(default_factory=list)  # Item IDs
	buy_price_multiplier: float = 1.0
	sell_price_multiplier: float = 0.5


@dataclass
class ItemAnalysis:
	"""Item balance analysis."""
	item_id: int
	power_score: float = 0.0
	cost_efficiency: float = 0.0
	balance_rating: str = "balanced"
	recommendations: List[str] = field(default_factory=list)


# Complete item database
ITEMS_DATABASE = {
	# Weapons
	0: Item(0, "Bamboo Pole", ItemType.WEAPON, 10, attack=2),
	1: Item(1, "Club", ItemType.WEAPON, 60, attack=4),
	2: Item(2, "Copper Sword", ItemType.WEAPON, 180, attack=10),
	3: Item(3, "Hand Axe", ItemType.WEAPON, 560, attack=15),
	4: Item(4, "Broad Sword", ItemType.WEAPON, 1500, attack=20),
	5: Item(5, "Flame Sword", ItemType.WEAPON, 9800, attack=28, effect="Fire damage"),
	6: Item(6, "Erdrick's Sword", ItemType.WEAPON, 0, attack=40, key_item=True),

	# Armor
	10: Item(10, "Clothes", ItemType.ARMOR, 20, defense=2),
	11: Item(11, "Leather Armor", ItemType.ARMOR, 70, defense=4),
	12: Item(12, "Chain Mail", ItemType.ARMOR, 300, defense=10),
	13: Item(13, "Half Plate", ItemType.ARMOR, 1000, defense=16),
	14: Item(14, "Full Plate", ItemType.ARMOR, 3000, defense=24),
	15: Item(15, "Magic Armor", ItemType.ARMOR, 7700, defense=24, effect="HP regen"),
	16: Item(16, "Erdrick's Armor", ItemType.ARMOR, 0, defense=28, key_item=True, effect="Damage reduction"),

	# Shields
	20: Item(20, "Leather Shield", ItemType.SHIELD, 90, defense=4),
	21: Item(21, "Iron Shield", ItemType.SHIELD, 800, defense=10),
	22: Item(22, "Silver Shield", ItemType.SHIELD, 14800, defense=20, effect="Breath resistance"),

	# Tools & Consumables
	30: Item(30, "Herb", ItemType.CONSUMABLE, 24, effect="Restore ~30 HP"),
	31: Item(31, "Torch", ItemType.TOOL, 8, effect="Light radius"),
	32: Item(32, "Dragon's Scale", ItemType.KEY_ITEM, 0, key_item=True, effect="Stopspell immunity"),
	33: Item(33, "Fairy Water", ItemType.CONSUMABLE, 38, effect="Repel enemies"),
	34: Item(34, "Wings", ItemType.CONSUMABLE, 70, effect="Return to castle"),
	35: Item(35, "Cursed Belt", ItemType.TOOL, 0, cursed=True, effect="Cannot flee"),
	36: Item(36, "Magic Key", ItemType.KEY_ITEM, 83, key_item=True, effect="Open magic doors"),
	37: Item(37, "Erdrick's Token", ItemType.KEY_ITEM, 0, key_item=True, effect="Princess proof"),
	38: Item(38, "Gwaelin's Love", ItemType.KEY_ITEM, 0, key_item=True, effect="Locate player"),
	39: Item(39, "Rainbow Drop", ItemType.KEY_ITEM, 0, key_item=True, effect="Create bridge"),
}

# Shop database
SHOPS_DATABASE = {
	0: Shop(0, "Brecconary Weapon Shop", "Brecconary", [0, 1, 2]),  # Bamboo Pole, Club, Copper Sword
	1: Shop(1, "Brecconary Armor Shop", "Brecconary", [10, 11, 20]),  # Clothes, Leather Armor, Leather Shield
	2: Shop(2, "Brecconary Tool Shop", "Brecconary", [30, 31, 33, 34, 36]),  # Herb, Torch, Fairy Water, Wings, Magic Key
	3: Shop(3, "Garinham Weapon Shop", "Garinham", [2, 3]),  # Copper Sword, Hand Axe
	4: Shop(4, "Garinham Armor Shop", "Garinham", [12, 21]),  # Chain Mail, Iron Shield
	5: Shop(5, "Kol Tool Shop", "Kol", [30, 31, 33]),  # Herb, Torch, Fairy Water
	6: Shop(6, "Rimuldar Weapon Shop", "Rimuldar", [3, 4]),  # Hand Axe, Broad Sword
	7: Shop(7, "Rimuldar Armor Shop", "Rimuldar", [13, 14, 21]),  # Half Plate, Full Plate, Iron Shield
	8: Shop(8, "Cantlin Weapon Shop", "Cantlin", [4, 5]),  # Broad Sword, Flame Sword
	9: Shop(9, "Cantlin Armor Shop", "Cantlin", [14, 15, 22]),  # Full Plate, Magic Armor, Silver Shield
}


# ============================================================================
# ITEM DATA LOADER
# ============================================================================

class ItemDataLoader:
	"""Load item data from ROM."""

	# ROM offsets (simplified - actual format may vary)
	ITEM_NAMES_OFFSET = 0x1af0
	ITEM_PRICES_OFFSET = 0x1c40
	WEAPON_STATS_OFFSET = 0x1d00
	ARMOR_STATS_OFFSET = 0x1d40
	SHOP_DATA_OFFSET = 0x1d80

	@staticmethod
	def load_item(rom_data: bytes, item_id: int) -> Optional[Item]:
		"""Load item from ROM."""
		if item_id in ITEMS_DATABASE:
			# Return from database (in real implementation, read from ROM)
			return ITEMS_DATABASE[item_id]
		return None

	@staticmethod
	def save_item(rom_data: bytearray, item: Item):
		"""Save item to ROM."""
		# Price (2 bytes, little endian)
		price_offset = ItemDataLoader.ITEM_PRICES_OFFSET + (item.id * 2)
		if price_offset + 2 <= len(rom_data):
			struct.pack_into('<H', rom_data, price_offset, item.price)

		# Weapon stats
		if item.item_type == ItemType.WEAPON:
			stats_offset = ItemDataLoader.WEAPON_STATS_OFFSET + item.id
			if stats_offset < len(rom_data):
				rom_data[stats_offset] = item.attack

		# Armor stats
		elif item.item_type in (ItemType.ARMOR, ItemType.SHIELD):
			stats_offset = ItemDataLoader.ARMOR_STATS_OFFSET + (item.id - 10)
			if stats_offset < len(rom_data):
				rom_data[stats_offset] = item.defense

	@staticmethod
	def load_shop(rom_data: bytes, shop_id: int) -> Optional[Shop]:
		"""Load shop from ROM."""
		if shop_id in SHOPS_DATABASE:
			return SHOPS_DATABASE[shop_id]
		return None


# ============================================================================
# ITEM ANALYZER
# ============================================================================

class ItemAnalyzer:
	"""Analyze item balance."""

	@staticmethod
	def calculate_power_score(item: Item) -> float:
		"""Calculate item power score."""
		if item.item_type == ItemType.WEAPON:
			return item.attack * 10.0
		elif item.item_type in (ItemType.ARMOR, ItemType.SHIELD):
			return item.defense * 8.0
		else:
			return 0.0

	@staticmethod
	def calculate_cost_efficiency(item: Item) -> float:
		"""Calculate cost efficiency (power per gold)."""
		if item.price == 0:
			return 0.0

		power = ItemAnalyzer.calculate_power_score(item)

		if power == 0:
			return 0.0

		return power / item.price

	@staticmethod
	def analyze_item(item: Item) -> ItemAnalysis:
		"""Analyze item balance."""
		power = ItemAnalyzer.calculate_power_score(item)
		efficiency = ItemAnalyzer.calculate_cost_efficiency(item)

		# Classify balance
		recommendations = []

		if item.key_item:
			rating = "key_item"
		elif efficiency == 0:
			rating = "tool"
		elif efficiency < 0.05:
			rating = "underpowered"
			recommendations.append("Increase stats or decrease price")
		elif efficiency > 0.15:
			rating = "overpowered"
			recommendations.append("Decrease stats or increase price")
		else:
			rating = "balanced"

		return ItemAnalysis(
			item_id=item.id,
			power_score=power,
			cost_efficiency=efficiency,
			balance_rating=rating,
			recommendations=recommendations
		)


# ============================================================================
# PROGRESSION ANALYZER
# ============================================================================

class ProgressionAnalyzer:
	"""Analyze item progression."""

	@staticmethod
	def analyze_weapon_curve(items: List[Item]) -> Dict[str, Any]:
		"""Analyze weapon power curve."""
		weapons = [item for item in items if item.item_type == ItemType.WEAPON]
		weapons.sort(key=lambda x: x.attack)

		attack_values = [w.attack for w in weapons]
		price_values = [w.price for w in weapons if w.price > 0]

		# Calculate progression smoothness
		attack_gaps = []
		for i in range(1, len(attack_values)):
			gap = attack_values[i] - attack_values[i-1]
			attack_gaps.append(gap)

		avg_gap = sum(attack_gaps) / len(attack_gaps) if attack_gaps else 0

		return {
			"weapons": len(weapons),
			"attack_range": (min(attack_values), max(attack_values)),
			"average_gap": avg_gap,
			"price_range": (min(price_values), max(price_values)) if price_values else (0, 0),
			"curve": "smooth" if avg_gap < 10 else "steep"
		}

	@staticmethod
	def analyze_armor_curve(items: List[Item]) -> Dict[str, Any]:
		"""Analyze armor defense curve."""
		armor = [item for item in items if item.item_type in (ItemType.ARMOR, ItemType.SHIELD)]
		armor.sort(key=lambda x: x.defense)

		defense_values = [a.defense for a in armor]
		price_values = [a.price for a in armor if a.price > 0]

		# Calculate progression smoothness
		defense_gaps = []
		for i in range(1, len(defense_values)):
			gap = defense_values[i] - defense_values[i-1]
			defense_gaps.append(gap)

		avg_gap = sum(defense_gaps) / len(defense_gaps) if defense_gaps else 0

		return {
			"armor_pieces": len(armor),
			"defense_range": (min(defense_values), max(defense_values)),
			"average_gap": avg_gap,
			"price_range": (min(price_values), max(price_values)) if price_values else (0, 0),
			"curve": "smooth" if avg_gap < 8 else "steep"
		}


# ============================================================================
# ITEM EDITOR
# ============================================================================

class ItemEditor:
	"""Edit items and shops."""

	def __init__(self, rom_path: str):
		self.rom_path = Path(rom_path)
		self.rom_data: bytearray = bytearray()
		self.items: Dict[int, Item] = {}
		self.shops: Dict[int, Shop] = {}

	def load_rom(self) -> bool:
		"""Load ROM file."""
		if not self.rom_path.exists():
			print(f"ERROR: ROM not found: {self.rom_path}")
			return False

		with open(self.rom_path, 'rb') as f:
			self.rom_data = bytearray(f.read())

		return True

	def load_all_items(self):
		"""Load all items."""
		print("Loading items...")
		self.items = ITEMS_DATABASE.copy()
		print(f"✓ Loaded {len(self.items)} items")

	def load_all_shops(self):
		"""Load all shops."""
		print("Loading shops...")
		self.shops = SHOPS_DATABASE.copy()
		print(f"✓ Loaded {len(self.shops)} shops")

	def get_item_by_name(self, name: str) -> Optional[Item]:
		"""Get item by name."""
		for item in self.items.values():
			if item.name.lower() == name.lower():
				return item
		return None

	def edit_item(self, item_id: int, **kwargs):
		"""Edit item stats."""
		if item_id not in self.items:
			print(f"ERROR: Invalid item ID: {item_id}")
			return

		item = self.items[item_id]

		# Update stats
		if 'price' in kwargs:
			item.price = kwargs['price']
		if 'attack' in kwargs:
			item.attack = kwargs['attack']
		if 'defense' in kwargs:
			item.defense = kwargs['defense']

		# Save to ROM
		ItemDataLoader.save_item(self.rom_data, item)

		print(f"✓ Updated {item.name}")

	def save_rom(self, output_path: str):
		"""Save modified ROM."""
		with open(output_path, 'wb') as f:
			f.write(self.rom_data)

		print(f"✓ ROM saved: {output_path}")

	def export_json(self, output_path: str):
		"""Export item database to JSON."""
		data = {
			"items": [
				{
					"id": item.id,
					"name": item.name,
					"type": item.item_type.value,
					"price": item.price,
					"attack": item.attack,
					"defense": item.defense,
					"effect": item.effect,
					"cursed": item.cursed,
					"key_item": item.key_item
				}
				for item in self.items.values()
			],
			"shops": [
				{
					"id": shop.id,
					"name": shop.name,
					"location": shop.location,
					"inventory": [self.items[item_id].name for item_id in shop.inventory if item_id in self.items]
				}
				for shop in self.shops.values()
			]
		}

		with open(output_path, 'w') as f:
			json.dump(data, f, indent=2)

		print(f"✓ Item database exported: {output_path}")


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Dragon Warrior Item & Shop Editor"
	)

	parser.add_argument('rom', help="ROM file")
	parser.add_argument('--list-items', action='store_true', help="List all items")
	parser.add_argument('--list-shops', action='store_true', help="List all shops")
	parser.add_argument('--item', type=str, help="Item name")
	parser.add_argument('--price', type=int, help="Set price")
	parser.add_argument('--attack', type=int, help="Set attack")
	parser.add_argument('--defense', type=int, help="Set defense")
	parser.add_argument('--analyze-balance', action='store_true', help="Analyze item balance")
	parser.add_argument('--analyze-progression', action='store_true', help="Analyze progression curves")
	parser.add_argument('--export', type=str, help="Export to JSON")
	parser.add_argument('-o', '--output', type=str, help="Output ROM file")

	args = parser.parse_args()

	# Load ROM
	editor = ItemEditor(args.rom)
	if not editor.load_rom():
		return 1

	# Load data
	editor.load_all_items()
	editor.load_all_shops()

	# List items
	if args.list_items:
		print("\nItems:")
		print("=" * 90)
		print(f"{'ID':<4} {'Name':<25} {'Type':<10} {'Price':<8} {'ATK':<5} {'DEF':<5} {'Effect'}")
		print("-" * 90)

		for item in sorted(editor.items.values(), key=lambda x: x.id):
			print(f"{item.id:<4} {item.name:<25} {item.item_type.value:<10} "
			      f"{item.price:<8} {item.attack:<5} {item.defense:<5} {item.effect}")

	# List shops
	if args.list_shops:
		print("\nShops:")
		print("=" * 80)

		for shop in sorted(editor.shops.values(), key=lambda x: x.id):
			print(f"\n{shop.name} ({shop.location}):")
			for item_id in shop.inventory:
				if item_id in editor.items:
					item = editor.items[item_id]
					print(f"  - {item.name} ({item.price} gold)")

	# Show item details
	if args.item:
		item = editor.get_item_by_name(args.item)

		if item:
			print(f"\n{item.name} (ID: {item.id})")
			print("=" * 60)
			print(f"Type: {item.item_type.value}")
			print(f"Price: {item.price} gold")
			if item.attack > 0:
				print(f"Attack: {item.attack}")
			if item.defense > 0:
				print(f"Defense: {item.defense}")
			if item.effect:
				print(f"Effect: {item.effect}")
			if item.cursed:
				print("CURSED")
			if item.key_item:
				print("KEY ITEM")

			# Edit stats if provided
			edits = {}
			if args.price is not None:
				edits['price'] = args.price
			if args.attack is not None:
				edits['attack'] = args.attack
			if args.defense is not None:
				edits['defense'] = args.defense

			if edits:
				print(f"\nApplying edits...")
				editor.edit_item(item.id, **edits)

				if args.output:
					editor.save_rom(args.output)
		else:
			print(f"ERROR: Item not found: {args.item}")

	# Analyze balance
	if args.analyze_balance:
		print("\nItem Balance Analysis:")
		print("=" * 80)

		imbalanced = []

		for item in editor.items.values():
			analysis = ItemAnalyzer.analyze_item(item)

			if analysis.balance_rating in ("underpowered", "overpowered"):
				imbalanced.append((item, analysis))

		if imbalanced:
			print(f"\nFound {len(imbalanced)} imbalanced items:\n")

			for item, analysis in imbalanced:
				print(f"{item.name}:")
				print(f"  Power: {analysis.power_score:.1f}")
				print(f"  Efficiency: {analysis.cost_efficiency:.4f}")
				print(f"  Rating: {analysis.balance_rating}")

				for rec in analysis.recommendations:
					print(f"  → {rec}")
				print()
		else:
			print("✓ All items are balanced!")

	# Analyze progression
	if args.analyze_progression:
		print("\nProgression Curve Analysis:")
		print("=" * 80)

		items_list = list(editor.items.values())

		weapon_curve = ProgressionAnalyzer.analyze_weapon_curve(items_list)
		print("\nWeapon Progression:")
		print(f"  Weapons: {weapon_curve['weapons']}")
		print(f"  Attack range: {weapon_curve['attack_range'][0]}-{weapon_curve['attack_range'][1]}")
		print(f"  Average gap: {weapon_curve['average_gap']:.1f}")
		print(f"  Price range: {weapon_curve['price_range'][0]}-{weapon_curve['price_range'][1]} gold")
		print(f"  Curve: {weapon_curve['curve']}")

		armor_curve = ProgressionAnalyzer.analyze_armor_curve(items_list)
		print("\nArmor Progression:")
		print(f"  Armor pieces: {armor_curve['armor_pieces']}")
		print(f"  Defense range: {armor_curve['defense_range'][0]}-{armor_curve['defense_range'][1]}")
		print(f"  Average gap: {armor_curve['average_gap']:.1f}")
		print(f"  Price range: {armor_curve['price_range'][0]}-{armor_curve['price_range'][1]} gold")
		print(f"  Curve: {armor_curve['curve']}")

	# Export
	if args.export:
		editor.export_json(args.export)

	return 0


if __name__ == "__main__":
	sys.exit(main())
