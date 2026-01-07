#!/usr/bin/env python3
"""
Dragon Warrior Shop and Economy Editor

Comprehensive editor for Dragon Warrior's shops, item prices, and economy balance.
Features:
- Edit all 8 shops (weapons, armor, items, inns, key dealers)
- Adjust item prices and availability
- Balance economy (gold rewards, item costs, progression)
- Simulate player purchasing power at each level
- Generate economy reports and recommendations
- Inn price calculator based on player level
- Shop inventory management

Author: Dragon Warrior Toolkit
Date: 2024-11-26
"""

import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import argparse
import struct
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from enum import IntEnum
import json
import math


class ShopType(IntEnum):
	"""Types of shops in Dragon Warrior."""
	WEAPON = 0
	ARMOR = 1
	ITEM = 2
	INN = 3
	KEY = 4


class TownID(IntEnum):
	"""Town identifiers in Dragon Warrior."""
	TANTEGEL = 0
	BRECCONARY = 1
	GARINHAM = 2
	KOL = 3
	RIMULDAR = 4
	CANTLIN = 5
	MERCADO = 6
	HAUKSNESS = 7


@dataclass
class Item:
	"""An item that can be bought or sold."""
	id: int
	name: str
	buy_price: int
	sell_price: int
	item_type: str  # weapon, armor, shield, consumable, tool, key_item
	attack: int = 0
	defense: int = 0
	effect: str = ""
	equip_slot: str = ""  # weapon, armor, shield, none

	def get_sell_ratio(self) -> float:
		"""Get sell price as ratio of buy price."""
		if self.buy_price == 0:
			return 0.0
		return self.sell_price / self.buy_price

	def to_dict(self) -> dict:
		return {
			'id': self.id,
			'name': self.name,
			'buy_price': self.buy_price,
			'sell_price': self.sell_price,
			'type': self.item_type,
			'attack': self.attack,
			'defense': self.defense,
			'effect': self.effect,
			'equip_slot': self.equip_slot,
			'sell_ratio': self.get_sell_ratio()
		}


# Complete Dragon Warrior item database
DW_ITEMS = [
	# Consumables
	Item(0, "Herb", 24, 12, "consumable", effect="Restore ~30 HP"),
	Item(1, "Torch", 8, 4, "tool", effect="Light up caves"),
	Item(2, "Fairy Water", 38, 19, "consumable", effect="Repel weak monsters"),
	Item(3, "Wings", 70, 35, "tool", effect="Return to Tantegel"),
	Item(4, "Dragon's Scale", 20, 10, "tool", effect="Reduce breath damage"),

	# Weapons
	Item(5, "Bamboo Pole", 10, 5, "weapon", attack=2, equip_slot="weapon"),
	Item(6, "Club", 60, 30, "weapon", attack=4, equip_slot="weapon"),
	Item(7, "Copper Sword", 180, 90, "weapon", attack=10, equip_slot="weapon"),
	Item(8, "Hand Axe", 560, 280, "weapon", attack=15, equip_slot="weapon"),
	Item(9, "Broad Sword", 1500, 750, "weapon", attack=20, equip_slot="weapon"),
	Item(10, "Flame Sword", 9800, 4900, "weapon", attack=28, effect="Fire damage", equip_slot="weapon"),
	Item(11, "Erdrick's Sword", 0, 0, "weapon", attack=40, equip_slot="weapon"),

	# Armor
	Item(12, "Clothes", 20, 10, "armor", defense=2, equip_slot="armor"),
	Item(13, "Leather Armor", 70, 35, "armor", defense=4, equip_slot="armor"),
	Item(14, "Chain Mail", 300, 150, "armor", defense=10, equip_slot="armor"),
	Item(15, "Half Plate", 1000, 500, "armor", defense=16, equip_slot="armor"),
	Item(16, "Full Plate", 3000, 1500, "armor", defense=24, equip_slot="armor"),
	Item(17, "Magic Armor", 7700, 3850, "armor", defense=24, effect="No damage zones", equip_slot="armor"),
	Item(18, "Erdrick's Armor", 0, 0, "armor", defense=28, effect="Resist fire/damage", equip_slot="armor"),

	# Shields
	Item(19, "Small Shield", 90, 45, "shield", defense=4, equip_slot="shield"),
	Item(20, "Large Shield", 800, 400, "shield", defense=10, equip_slot="shield"),
	Item(21, "Silver Shield", 14800, 7400, "shield", defense=20, effect="Resist spells", equip_slot="shield"),

	# Key Items
	Item(22, "Magic Key", 83, 0, "key_item", effect="Open magic doors"),
	Item(23, "Stones of Sunlight", 0, 0, "key_item", effect="Create Rainbow Bridge"),
	Item(24, "Staff of Rain", 0, 0, "key_item", effect="Create Rainbow Bridge"),
	Item(25, "Gwaelin's Love", 0, 0, "key_item", effect="Check distance to Tantegel"),
	Item(26, "Cursed Belt", 0, 0, "key_item", effect="Cursed item"),
	Item(27, "Silver Harp", 0, 0, "key_item", effect="Put Golem to sleep"),
	Item(28, "Death Necklace", 0, 0, "key_item", effect="Cursed item"),
	Item(29, "Erdrick's Token", 0, 0, "key_item", effect="Proof of lineage"),
	Item(30, "Fighter's Ring", 0, 0, "key_item", effect="Increase attack"),
	Item(31, "Fairy Flute", 0, 0, "key_item", effect="Put monsters to sleep"),
]

# Create lookup dictionary
ITEMS_BY_ID = {item.id: item for item in DW_ITEMS}
ITEMS_BY_NAME = {item.name: item for item in DW_ITEMS}


@dataclass
class Shop:
	"""A shop in Dragon Warrior."""
	town: TownID
	shop_type: ShopType
	inventory: List[int] = field(default_factory=list)  # Item IDs
	inn_price: int = 0  # Only for inns

	def get_items(self) -> List[Item]:
		"""Get Item objects for all items in inventory."""
		return [ITEMS_BY_ID[item_id] for item_id in self.inventory if item_id in ITEMS_BY_ID]

	def total_inventory_value(self) -> int:
		"""Calculate total value of all items in shop."""
		return sum(item.buy_price for item in self.get_items())

	def to_dict(self) -> dict:
		return {
			'town': TownID(self.town).name,
			'type': ShopType(self.shop_type).name,
			'inventory': [ITEMS_BY_ID[item_id].name for item_id in self.inventory if item_id in ITEMS_BY_ID],
			'inventory_ids': self.inventory,
			'inn_price': self.inn_price,
			'total_value': self.total_inventory_value()
		}


# Dragon Warrior shop definitions
DW_SHOPS = [
	# Tantegel Castle - No shops in throne room

	# Brecconary (starting town)
	Shop(TownID.BRECCONARY, ShopType.WEAPON, [5, 6, 7]),  # Bamboo Pole, Club, Copper Sword
	Shop(TownID.BRECCONARY, ShopType.ARMOR, [12, 13, 19]),  # Clothes, Leather Armor, Small Shield
	Shop(TownID.BRECCONARY, ShopType.ITEM, [0, 1, 2, 3]),  # Herb, Torch, Fairy Water, Wings
	Shop(TownID.BRECCONARY, ShopType.INN, [], inn_price=6),

	# Garinham
	Shop(TownID.GARINHAM, ShopType.WEAPON, [7, 8]),  # Copper Sword, Hand Axe
	Shop(TownID.GARINHAM, ShopType.ARMOR, [13, 14, 19, 20]),  # Leather Armor, Chain Mail, shields
	Shop(TownID.GARINHAM, ShopType.ITEM, [0, 1, 2, 3, 4]),  # Herbs, tools, Dragon's Scale
	Shop(TownID.GARINHAM, ShopType.KEY, [22]),  # Magic Key
	Shop(TownID.GARINHAM, ShopType.INN, [], inn_price=20),

	# Kol
	Shop(TownID.KOL, ShopType.WEAPON, [8]),  # Hand Axe
	Shop(TownID.KOL, ShopType.ITEM, [0, 1]),  # Herb, Torch
	Shop(TownID.KOL, ShopType.INN, [], inn_price=25),

	# Rimuldar
	Shop(TownID.RIMULDAR, ShopType.WEAPON, [8, 9]),  # Hand Axe, Broad Sword
	Shop(TownID.RIMULDAR, ShopType.ARMOR, [14, 15, 20]),  # Chain Mail, Half Plate, Large Shield
	Shop(TownID.RIMULDAR, ShopType.ITEM, [0, 1, 2, 3, 4]),  # Full consumables
	Shop(TownID.RIMULDAR, ShopType.INN, [], inn_price=55),

	# Cantlin (advanced town)
	Shop(TownID.CANTLIN, ShopType.WEAPON, [10]),  # Flame Sword
	Shop(TownID.CANTLIN, ShopType.ARMOR, [16, 17, 21]),  # Full Plate, Magic Armor, Silver Shield
	Shop(TownID.CANTLIN, ShopType.ITEM, [0, 2, 3]),  # Herb, Fairy Water, Wings
	Shop(TownID.CANTLIN, ShopType.INN, [], inn_price=100),
]


@dataclass
class PlayerProgress:
	"""Player progression data for economy simulation."""
	level: int
	hp: int
	mp: int
	strength: int
	agility: int
	attack_power: int
	defense_power: int
	gold: int

	@classmethod
	def at_level(cls, level: int) -> 'PlayerProgress':
		"""Create player stats at a given level (approximations)."""
		# These are approximations of Dragon Warrior stat growth
		hp = 15 + (level - 1) * 5
		mp = 0 if level < 3 else (level - 2) * 3
		strength = 4 + level
		agility = 4 + level
		attack_power = 4 + level
		defense_power = 4 + level
		gold = 0  # Starting gold

		return cls(level, hp, mp, strength, agility, attack_power, defense_power, gold)


class EconomySimulator:
	"""Simulate Dragon Warrior economy and purchasing power."""

	def __init__(self):
		self.shops = DW_SHOPS
		self.items = DW_ITEMS

	def calculate_recommended_gold_for_level(self, level: int) -> int:
		"""Calculate recommended gold for a given level."""
		# Rough heuristic: gold needed for next equipment tier
		if level <= 2:
			return 200  # Enough for Copper Sword
		elif level <= 5:
			return 800  # Enough for Hand Axe and Chain Mail
		elif level <= 10:
			return 3000  # Enough for Broad Sword and Half Plate
		elif level <= 15:
			return 12000  # Enough for Flame Sword
		else:
			return 25000  # Late game equipment

	def get_available_shops_at_level(self, level: int) -> List[Shop]:
		"""Get shops typically available at a given level."""
		# Simplified: assume player explores towns in order
		if level <= 3:
			return [s for s in self.shops if s.town in [TownID.BRECCONARY]]
		elif level <= 7:
			return [s for s in self.shops if s.town in [TownID.BRECCONARY, TownID.GARINHAM, TownID.KOL]]
		elif level <= 12:
			return [s for s in self.shops if s.town in [TownID.BRECCONARY, TownID.GARINHAM, TownID.KOL, TownID.RIMULDAR]]
		else:
			return self.shops  # All shops

	def recommend_purchases_for_level(self, level: int, current_gold: int) -> List[Tuple[Item, str]]:
		"""Recommend what to buy at a given level with available gold."""
		recommendations = []
		player = PlayerProgress.at_level(level)
		available_shops = self.get_available_shops_at_level(level)

		# Get all available items
		available_items = set()
		for shop in available_shops:
			for item in shop.get_items():
				available_items.add(item)

		# Sort by effectiveness/price ratio for equipment
		equipment = [item for item in available_items if item.equip_slot]
		equipment.sort(key=lambda x: (x.attack + x.defense) / max(x.buy_price, 1), reverse=True)

		budget = current_gold

		# Recommend best weapon if affordable
		weapons = [item for item in equipment if item.equip_slot == "weapon"]
		if weapons and weapons[0].buy_price <= budget:
			recommendations.append((weapons[0], "Best weapon available"))
			budget -= weapons[0].buy_price

		# Recommend best armor if affordable
		armors = [item for item in equipment if item.equip_slot == "armor"]
		if armors and armors[0].buy_price <= budget:
			recommendations.append((armors[0], "Best armor available"))
			budget -= armors[0].buy_price

		# Recommend best shield if affordable
		shields = [item for item in equipment if item.equip_slot == "shield"]
		if shields and shields[0].buy_price <= budget:
			recommendations.append((shields[0], "Best shield available"))
			budget -= shields[0].buy_price

		# Recommend consumables
		herbs_count = budget // 24  # Herb price
		if herbs_count > 0:
			herb = ITEMS_BY_NAME["Herb"]
			recommendations.append((herb, f"Buy {min(herbs_count, 6)} for healing"))

		return recommendations

	def generate_progression_report(self) -> List[Dict]:
		"""Generate economy progression report for all levels."""
		report = []

		for level in range(1, 31):
			player = PlayerProgress.at_level(level)
			recommended_gold = self.calculate_recommended_gold_for_level(level)
			available_shops = self.get_available_shops_at_level(level)
			recommendations = self.recommend_purchases_for_level(level, recommended_gold)

			report.append({
				'level': level,
				'recommended_gold': recommended_gold,
				'available_towns': list(set(TownID(s.town).name for s in available_shops)),
				'shop_count': len(available_shops),
				'recommendations': [
					{
						'item': item.name,
						'price': item.buy_price,
						'reason': reason
					}
					for item, reason in recommendations
				]
			})

		return report

	def analyze_price_balance(self) -> Dict:
		"""Analyze economy balance and find potential issues."""
		issues = []
		stats = {}

		# Check sell ratios
		sell_ratios = [item.get_sell_ratio() for item in self.items if item.buy_price > 0]
		avg_sell_ratio = sum(sell_ratios) / len(sell_ratios) if sell_ratios else 0

		stats['average_sell_ratio'] = avg_sell_ratio
		stats['expected_sell_ratio'] = 0.5  # Dragon Warrior typically uses 50%

		# Find items with unusual sell ratios
		for item in self.items:
			if item.buy_price > 0:
				ratio = item.get_sell_ratio()
				if abs(ratio - 0.5) > 0.1:
					issues.append(f"{item.name}: Unusual sell ratio {ratio:.2f} (expected ~0.50)")

		# Check equipment progression (price should increase with power)
		weapons = sorted([item for item in self.items if item.equip_slot == "weapon" and item.buy_price > 0],
		                key=lambda x: x.attack)

		for i in range(len(weapons) - 1):
			current = weapons[i]
			next_item = weapons[i + 1]

			if next_item.buy_price <= current.buy_price:
				issues.append(f"Weapon progression: {next_item.name} ({next_item.buy_price}g) should cost more than {current.name} ({current.buy_price}g)")

			# Check if price increase matches power increase
			power_ratio = next_item.attack / current.attack if current.attack > 0 else 1
			price_ratio = next_item.buy_price / current.buy_price if current.buy_price > 0 else 1

			if price_ratio > power_ratio * 3:  # Price increases too fast
				issues.append(f"Price spike: {next_item.name} costs {price_ratio:.1f}x more but only {power_ratio:.1f}x stronger than {current.name}")

		# Check inn prices vs level progression
		inns = [shop for shop in self.shops if shop.shop_type == ShopType.INN]
		stats['inn_price_range'] = [min(s.inn_price for s in inns), max(s.inn_price for s in inns)]

		return {
			'stats': stats,
			'issues': issues
		}


class ShopEditor:
	"""Edit Dragon Warrior shops."""

	def __init__(self, rom_path: Path, verbose: bool = False):
		self.rom_path = rom_path
		self.verbose = verbose
		self.shops = DW_SHOPS.copy()
		self.items = DW_ITEMS.copy()
		self.modified = False

	def edit_item_price(self, item_name: str, new_buy_price: int) -> None:
		"""Edit an item's buy price."""
		if item_name not in ITEMS_BY_NAME:
			raise ValueError(f"Unknown item: {item_name}")

		item = ITEMS_BY_NAME[item_name]
		old_price = item.buy_price
		item.buy_price = new_buy_price
		item.sell_price = new_buy_price // 2  # Maintain 50% sell ratio

		self.modified = True

		if self.verbose:
			print(f"Changed {item_name} price: {old_price}g → {new_buy_price}g (sell: {item.sell_price}g)")

	def add_item_to_shop(self, town: TownID, shop_type: ShopType, item_id: int) -> None:
		"""Add an item to a shop's inventory."""
		# Find the shop
		shop = next((s for s in self.shops if s.town == town and s.shop_type == shop_type), None)

		if not shop:
			raise ValueError(f"No {shop_type.name} shop in {town.name}")

		if item_id not in ITEMS_BY_ID:
			raise ValueError(f"Unknown item ID: {item_id}")

		if item_id not in shop.inventory:
			shop.inventory.append(item_id)
			self.modified = True

			if self.verbose:
				print(f"Added {ITEMS_BY_ID[item_id].name} to {town.name} {shop_type.name} shop")

	def remove_item_from_shop(self, town: TownID, shop_type: ShopType, item_id: int) -> None:
		"""Remove an item from a shop's inventory."""
		shop = next((s for s in self.shops if s.town == town and s.shop_type == shop_type), None)

		if not shop:
			raise ValueError(f"No {shop_type.name} shop in {town.name}")

		if item_id in shop.inventory:
			shop.inventory.remove(item_id)
			self.modified = True

			if self.verbose:
				print(f"Removed {ITEMS_BY_ID[item_id].name} from {town.name} {shop_type.name} shop")

	def export_to_json(self, output_path: Path) -> None:
		"""Export shop data to JSON."""
		data = {
			'version': '1.0',
			'items': [item.to_dict() for item in self.items],
			'shops': [shop.to_dict() for shop in self.shops]
		}

		with output_path.open('w') as f:
			json.dump(data, f, indent='\t')

		print(f"Exported shop data to {output_path}")


class InteractiveShopEditor:
	"""Interactive shop and economy editor."""

	def __init__(self, rom_path: Path):
		self.rom_path = rom_path
		self.editor = ShopEditor(rom_path, verbose=True)
		self.simulator = EconomySimulator()

	def run(self) -> None:
		"""Run interactive editor."""
		print("\n" + "="*70)
		print("Dragon Warrior Shop & Economy Editor")
		print("="*70)

		while True:
			self._print_menu()
			choice = input("\nEnter choice: ").strip()

			if choice == '1':
				self._list_all_items()
			elif choice == '2':
				self._list_all_shops()
			elif choice == '3':
				self._edit_item_price()
			elif choice == '4':
				self._add_item_to_shop()
			elif choice == '5':
				self._remove_item_from_shop()
			elif choice == '6':
				self._show_progression_report()
			elif choice == '7':
				self._analyze_balance()
			elif choice == '8':
				self._simulate_level()
			elif choice == '9':
				self._export_data()
			elif choice == 'q':
				if self.editor.modified:
					confirm = input("You have unsaved changes. Exit anyway? (y/n): ")
					if confirm.lower() == 'y':
						break
				else:
					break
			else:
				print("Invalid choice")

	def _print_menu(self) -> None:
		"""Print main menu."""
		print("\n" + "-"*70)
		print("Menu:")
		print("  1. List all items")
		print("  2. List all shops")
		print("  3. Edit item price")
		print("  4. Add item to shop")
		print("  5. Remove item from shop")
		print("  6. Show progression report")
		print("  7. Analyze economy balance")
		print("  8. Simulate purchasing power at level")
		print("  9. Export data to JSON")
		print("  q. Quit")

		if self.editor.modified:
			print("\n⚠ You have unsaved changes")

	def _list_all_items(self) -> None:
		"""List all items."""
		print("\n" + "="*70)
		print("All Items")
		print("="*70)

		# Group by type
		by_type = {}
		for item in self.editor.items:
			if item.item_type not in by_type:
				by_type[item.item_type] = []
			by_type[item.item_type].append(item)

		for item_type, items in sorted(by_type.items()):
			print(f"\n{item_type.upper()}:")
			for item in sorted(items, key=lambda x: x.buy_price):
				stats = []
				if item.attack > 0:
					stats.append(f"ATK+{item.attack}")
				if item.defense > 0:
					stats.append(f"DEF+{item.defense}")
				if item.effect:
					stats.append(item.effect)

				stats_str = f" ({', '.join(stats)})" if stats else ""
				print(f"  {item.id:2d}. {item.name:20s} - Buy: {item.buy_price:5d}g, Sell: {item.sell_price:5d}g{stats_str}")

	def _list_all_shops(self) -> None:
		"""List all shops."""
		print("\n" + "="*70)
		print("All Shops")
		print("="*70)

		by_town = {}
		for shop in self.editor.shops:
			town_name = TownID(shop.town).name
			if town_name not in by_town:
				by_town[town_name] = []
			by_town[town_name].append(shop)

		for town_name, shops in sorted(by_town.items()):
			print(f"\n{town_name}:")
			for shop in shops:
				shop_type = ShopType(shop.shop_type).name
				if shop.shop_type == ShopType.INN:
					print(f"  {shop_type}: {shop.inn_price}g per stay")
				else:
					items_str = ", ".join(ITEMS_BY_ID[item_id].name for item_id in shop.inventory if item_id in ITEMS_BY_ID)
					print(f"  {shop_type}: {items_str}")

	def _edit_item_price(self) -> None:
		"""Edit an item's price."""
		item_name = input("Enter item name: ").strip()

		if item_name not in ITEMS_BY_NAME:
			print(f"Unknown item: {item_name}")
			return

		current_price = ITEMS_BY_NAME[item_name].buy_price
		print(f"Current price: {current_price}g")

		new_price_str = input("Enter new price: ").strip()

		try:
			new_price = int(new_price_str)
			if new_price < 0:
				print("Price must be non-negative")
				return

			self.editor.edit_item_price(item_name, new_price)
		except ValueError:
			print("Invalid price")

	def _add_item_to_shop(self) -> None:
		"""Add item to shop."""
		print("\nTowns:", ", ".join(f"{i}={t.name}" for i, t in enumerate(TownID)))
		town_id = input("Enter town ID: ").strip()

		try:
			town = TownID(int(town_id))
		except (ValueError, KeyError):
			print("Invalid town ID")
			return

		print("\nShop types:", ", ".join(f"{i}={t.name}" for i, t in enumerate(ShopType)))
		shop_type_id = input("Enter shop type ID: ").strip()

		try:
			shop_type = ShopType(int(shop_type_id))
		except (ValueError, KeyError):
			print("Invalid shop type")
			return

		item_id = input("Enter item ID (or name): ").strip()

		try:
			if item_id.isdigit():
				item_id = int(item_id)
			else:
				item_id = ITEMS_BY_NAME[item_id].id

			self.editor.add_item_to_shop(town, shop_type, item_id)
		except (ValueError, KeyError) as e:
			print(f"Error: {e}")

	def _remove_item_from_shop(self) -> None:
		"""Remove item from shop."""
		print("\nTowns:", ", ".join(f"{i}={t.name}" for i, t in enumerate(TownID)))
		town_id = input("Enter town ID: ").strip()

		try:
			town = TownID(int(town_id))
		except (ValueError, KeyError):
			print("Invalid town ID")
			return

		print("\nShop types:", ", ".join(f"{i}={t.name}" for i, t in enumerate(ShopType)))
		shop_type_id = input("Enter shop type ID: ").strip()

		try:
			shop_type = ShopType(int(shop_type_id))
		except (ValueError, KeyError):
			print("Invalid shop type")
			return

		# Show current inventory
		shop = next((s for s in self.editor.shops if s.town == town and s.shop_type == shop_type), None)
		if shop:
			print("\nCurrent inventory:")
			for item_id in shop.inventory:
				if item_id in ITEMS_BY_ID:
					print(f"  {item_id}: {ITEMS_BY_ID[item_id].name}")

		item_id = input("Enter item ID to remove: ").strip()

		try:
			item_id = int(item_id)
			self.editor.remove_item_from_shop(town, shop_type, item_id)
		except (ValueError, KeyError) as e:
			print(f"Error: {e}")

	def _show_progression_report(self) -> None:
		"""Show economy progression report."""
		print("\n" + "="*70)
		print("Economy Progression Report")
		print("="*70)

		report = self.simulator.generate_progression_report()

		# Show every 3 levels for brevity
		for entry in report[::3]:
			level = entry['level']
			gold = entry['recommended_gold']
			towns = ", ".join(entry['available_towns'])

			print(f"\nLevel {level}: Recommended Gold: {gold}g")
			print(f"  Available Towns: {towns}")
			print(f"  Recommended Purchases:")

			for rec in entry['recommendations'][:3]:  # Show top 3
				print(f"    - {rec['item']} ({rec['price']}g): {rec['reason']}")

	def _analyze_balance(self) -> None:
		"""Analyze economy balance."""
		print("\n" + "="*70)
		print("Economy Balance Analysis")
		print("="*70)

		analysis = self.simulator.analyze_price_balance()

		print(f"\nStatistics:")
		for key, value in analysis['stats'].items():
			print(f"  {key}: {value}")

		print(f"\nIssues Found: {len(analysis['issues'])}")
		for issue in analysis['issues'][:10]:  # Show first 10
			print(f"  ⚠ {issue}")

	def _simulate_level(self) -> None:
		"""Simulate purchasing power at a level."""
		level_str = input("Enter level (1-30): ").strip()

		try:
			level = int(level_str)
			if not 1 <= level <= 30:
				print("Level must be between 1 and 30")
				return

			recommended_gold = self.simulator.calculate_recommended_gold_for_level(level)
			recommendations = self.simulator.recommend_purchases_for_level(level, recommended_gold)

			print(f"\nLevel {level} Simulation:")
			print(f"  Recommended Gold: {recommended_gold}g")
			print(f"\n  Purchase Recommendations:")

			total_cost = 0
			for item, reason in recommendations:
				print(f"    - {item.name} ({item.buy_price}g): {reason}")
				total_cost += item.buy_price

			print(f"\n  Total Cost: {total_cost}g")
			print(f"  Remaining: {recommended_gold - total_cost}g")

		except ValueError:
			print("Invalid level")

	def _export_data(self) -> None:
		"""Export data to JSON."""
		output_path = Path("output/shop_data.json")
		output_path.parent.mkdir(exist_ok=True)

		self.editor.export_to_json(output_path)
		self.editor.modified = False


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Dragon Warrior Shop and Economy Editor',
		formatter_class=argparse.RawDescriptionHelpFormatter
	)

	parser.add_argument(
		'rom_path',
		type=Path,
		nargs='?',
		help='Path to Dragon Warrior ROM file'
	)

	parser.add_argument(
		'-i', '--interactive',
		action='store_true',
		help='Run interactive editor'
	)

	parser.add_argument(
		'--analyze',
		action='store_true',
		help='Analyze economy balance'
	)

	parser.add_argument(
		'--progression',
		action='store_true',
		help='Generate progression report'
	)

	parser.add_argument(
		'-o', '--output',
		type=Path,
		help='Output file path'
	)

	args = parser.parse_args()

	if args.interactive or (args.rom_path and not args.analyze and not args.progression):
		if not args.rom_path:
			parser.error("ROM path required for interactive mode")

		editor = InteractiveShopEditor(args.rom_path)
		editor.run()

	elif args.analyze:
		simulator = EconomySimulator()
		analysis = simulator.analyze_price_balance()

		print("Economy Balance Analysis")
		print("="*70)
		print(json.dumps(analysis, indent=2))

	elif args.progression:
		simulator = EconomySimulator()
		report = simulator.generate_progression_report()

		output_path = args.output or Path("output/progression_report.json")
		output_path.parent.mkdir(exist_ok=True, parents=True)

		with output_path.open('w') as f:
			json.dump(report, f, indent='\t')

		print(f"Generated progression report: {output_path}")

	else:
		parser.print_help()

	return 0


if __name__ == '__main__':
	exit(main())
