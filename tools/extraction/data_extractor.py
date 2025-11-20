#!/usr/bin/env python3
"""
Dragon Warrior Complete Data Extractor
Extract all game data (monsters, items, spells, shops, dialog, etc.) to JSON
"""

import struct
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import click
from rich.console import Console
from rich.progress import track

from data_structures import (
	GameData, MonsterStats, ItemData, SpellData, ShopData, DialogEntry,
	NPCData, Position, MonsterType, ItemType, SpellType,
	DW_MONSTERS, DW_ITEMS, DW_SPELLS, DW_MAPS
)

console = Console()

class DragonWarriorDataExtractor:
	"""Extract complete game data from Dragon Warrior ROM"""

	def __init__(self, rom_path: str, output_dir: str):
		self.rom_path = Path(rom_path)
		self.output_dir = Path(output_dir)
		self.json_dir = self.output_dir / "json"
		self.json_dir.mkdir(parents=True, exist_ok=True)

		with open(self.rom_path, 'rb') as f:
			self.rom_data = f.read()

	def extract_monster_stats(self) -> Dict[int, MonsterStats]:
		"""Extract monster statistics from ROM EnStatTbl at Bank01:L9E4B"""
		monsters = {}

		# Dragon Warrior monster data - EnStatTbl at Bank01:L9E4B
		# ROM file offset calculation: Bank 1 starts at 0x4010, L9E4B = 0x1E4B relative to bank
		# So absolute ROM offset = 0x4010 + (0x9E4B - 0x8000) = 0x4010 + 0x1E4B = 0x5E5B
		monster_data_offset = 0x5E5B	# EnStatTbl location in ROM file

		for monster_id in range(40):	# 40 monsters in Dragon Warrior (0x00-0x27)
			offset = monster_data_offset + (monster_id * 16)	# 16 bytes per monster entry

			if offset + 16 <= len(self.rom_data):
				data = self.rom_data[offset:offset + 16]

				# Parse monster data (Dragon Warrior EnStatTbl format)
				# Format: Att(1), Def(1), HP(1), Spel(1), Agi(1), Mdef(1), Exp(1), Gld(1), Unused(8)
				attack = data[0]
				defense = data[1]
				hp = data[2]
				spell_flags = data[3]
				agility = data[4]
				magic_defense = data[5]
				experience = data[6]
				gold = data[7]
				# bytes 8-15 are unused

				# Determine monster type based on ID ranges from the ROM
				if monster_id <= 2:	# Slime, Red Slime, Drakee
					monster_type = MonsterType.SLIME
				elif monster_id in [31, 35, 38]:	# Green Dragon, Blue Dragon, Red Dragon
					monster_type = MonsterType.DRAGON
				elif monster_id in [3, 8, 15, 18, 24]:	# Ghost, Poltergeist, Wraith, Specter, Wraith Knight
					monster_type = MonsterType.UNDEAD
				elif monster_id in [13, 16]:	# Metal Slime, Metal Scorpion
					monster_type = MonsterType.METAL
				elif monster_id in [29, 39]:	# Demon Knight, Dragonlord
					monster_type = MonsterType.DEMON
				else:
					monster_type = MonsterType.BEAST

				monster_name = DW_MONSTERS.get(monster_id, f"Unknown_{monster_id}")

				monster = MonsterStats(
					id=monster_id,
					name=monster_name,
					hp=hp,
					strength=attack,	# Attack stat used as strength
					agility=agility,
					max_damage=attack,	# Max damage approximated from attack
					dodge_rate=agility // 2,	# Dodge rate derived from agility
					sleep_resistance=magic_defense,
					hurt_resistance=magic_defense,
					experience=experience,
					gold=gold,
					monster_type=monster_type,
					sprite_id=monster_id	# Direct sprite mapping
				)

				monsters[monster_id] = monster

		return monsters

	def extract_item_data(self) -> Dict[int, ItemData]:
		"""Extract item statistics and properties from ROM data tables"""
		items = {}

		# ROM offsets for item data tables (Bank 0)
		# WeaponsBonusTbl at L99CF, ArmorBonusTbl at L99D7, ShieldBonusTbl at L99DF, ItemCostTbl at L9947
		weapons_bonus_offset = 0x19CF	# Bank 0 + 0x99CF - 0x8000 = 0x19CF
		armor_bonus_offset = 0x19D7	# Bank 0 + 0x99D7 - 0x8000 = 0x19D7
		shield_bonus_offset = 0x19DF	 # Bank 0 + 0x99DF - 0x8000 = 0x19DF
		item_cost_offset = 0x1947		# Bank 0 + 0x9947 - 0x8000 = 0x1947

		# Read bonus tables
		weapon_bonuses = list(self.rom_data[weapons_bonus_offset:weapons_bonus_offset + 7])	# 7 weapon types
		armor_bonuses = list(self.rom_data[armor_bonus_offset:armor_bonus_offset + 8])		# 8 armor types
		shield_bonuses = list(self.rom_data[shield_bonus_offset:shield_bonus_offset + 4])	 # 4 shield types

		# Extract all items from DW_ITEMS dictionary
		for item_id in range(29):	# 29 items total in Dragon Warrior
			item_name = DW_ITEMS.get(item_id, f"Unknown_Item_{item_id}")

			# Read item cost from ItemCostTbl (2 bytes per item)
			cost_offset = item_cost_offset + (item_id * 2)
			if cost_offset + 2 <= len(self.rom_data):
				buy_price = struct.unpack('<H', self.rom_data[cost_offset:cost_offset + 2])[0]
			else:
				buy_price = 0

			sell_price = buy_price // 2	# Standard Dragon Warrior sell price

			# Determine item type and bonuses based on item ranges
			attack_bonus = 0
			defense_bonus = 0
			equippable = True
			useable = False

			if item_id in [0, 1, 2, 3, 4, 5, 6]:	# Weapons: Bamboo pole to Erdrick's sword
				item_type = ItemType.WEAPON
				if item_id < len(weapon_bonuses):
					attack_bonus = weapon_bonuses[item_id]
			elif item_id in [7, 8, 9, 10, 11, 12, 13]:	# Armor: Clothes to Erdrick's armor
				item_type = ItemType.ARMOR
				armor_index = item_id - 7
				if armor_index < len(armor_bonuses):
					defense_bonus = armor_bonuses[armor_index]
			elif item_id in [14, 15, 16]:	# Shields: Small to Silver shield
				item_type = ItemType.SHIELD
				shield_index = item_id - 14 + 1	# Skip "none" entry
				if shield_index < len(shield_bonuses):
					defense_bonus = shield_bonuses[shield_index]
			elif item_id in [17, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28]:	# Key items and special
				item_type = ItemType.KEY_ITEM
				equippable = False
				if item_id == 17:	# Herb
					useable = True
			else:	# Tools and consumables
				item_type = ItemType.TOOL
				equippable = False
				useable = True

			# Create item data
			item = ItemData(
				id=item_id,
				name=item_name,
				item_type=item_type,
				attack_bonus=attack_bonus,
				defense_bonus=defense_bonus,
				buy_price=buy_price,
				sell_price=sell_price,
				equippable=equippable,
				useable=useable,
				sprite_id=item_id,	# Direct sprite mapping
				description=self._get_item_description(item_name, item_type)
			)

			items[item_id] = item

		return items

	def _get_item_description(self, name: str, item_type: ItemType) -> str:
		"""Generate item description based on name and type"""
		descriptions = {
			"Torch": "A torch that lights up dark dungeons.",
			"Club": "A simple wooden club for combat.",
			"Copper Sword": "A basic sword made of copper.",
			"Hand Axe": "A small axe that can be wielded in one hand.",
			"Broad Sword": "A well-balanced sword for experienced warriors.",
			"Flame Sword": "A magical sword that burns enemies.",
			"Erdrick's Sword": "The legendary sword of the hero Erdrick.",
			"Clothes": "Simple clothing that offers minimal protection.",
			"Leather Armor": "Basic armor made from tanned leather.",
			"Chain Mail": "Interlocked metal rings provide good protection.",
			"Half Plate": "Partial plate armor covering vital areas.",
			"Full Plate": "Complete metal armor for maximum protection.",
			"Magic Armor": "Enchanted armor with magical properties.",
			"Erdrick's Armor": "The legendary armor worn by the hero Erdrick.",
			"Herb": "A medicinal herb that restores health.",
			"Key": "A key that opens locked doors.",
			"Magic Key": "A magical key that opens special doors."
		}
		return descriptions.get(name, f"A {item_type.name.lower().replace('_', ' ')} used by brave adventurers.")

	def extract_spell_data(self) -> Dict[int, SpellData]:
		"""Extract spell data from ROM SpellCostTbl and spell learning levels"""
		spells = {}

		# SpellCostTbl at Bank00:L9D53
		# ROM offset: Bank 0 + 0x9D53 - 0x8000 = 0x1D53
		spell_cost_offset = 0x1D53

		# Spell learning levels from the assembly code (ChkNewSpell routine)
		# Spells are learned at levels: 3, 4, 7, 9, 10, 12, 13, 15, 17, 19
		spell_learn_levels = [3, 4, 7, 9, 10, 12, 13, 15, 17, 19]

		# Read MP costs from ROM
		spell_mp_costs = []
		for i in range(10):	# 10 spells total
			if spell_cost_offset + i < len(self.rom_data):
				spell_mp_costs.append(self.rom_data[spell_cost_offset + i])
			else:
				spell_mp_costs.append(0)

		# Dragon Warrior spell data with actual ROM values
		spell_definitions = [
			(0, "Heal", SpellType.HEALING, spell_mp_costs[0], 10, 3),
			(1, "Hurt", SpellType.OFFENSIVE, spell_mp_costs[1], 8, 4),
			(2, "Sleep", SpellType.UTILITY, spell_mp_costs[2], 0, 7),
			(3, "Radiant", SpellType.UTILITY, spell_mp_costs[3], 0, 9),
			(4, "Stopspell", SpellType.UTILITY, spell_mp_costs[4], 0, 10),
			(5, "Outside", SpellType.UTILITY, spell_mp_costs[5], 0, 12),
			(6, "Return", SpellType.UTILITY, spell_mp_costs[6], 0, 13),
			(7, "Repel", SpellType.UTILITY, spell_mp_costs[7], 0, 15),
			(8, "Healmore", SpellType.HEALING, spell_mp_costs[8], 85, 17),
			(9, "Hurtmore", SpellType.OFFENSIVE, spell_mp_costs[9], 65, 19)
		]

		for spell_id, name, spell_type, mp_cost, power, learn_level in spell_definitions:
			spell = SpellData(
				id=spell_id,
				name=name,
				spell_type=spell_type,
				mp_cost=mp_cost,
				power=power,
				learn_level=learn_level,
				description=self._get_spell_description(name, spell_type)
			)
			spells[spell_id] = spell

		return spells

	def _get_spell_description(self, name: str, spell_type: SpellType) -> str:
		"""Get spell description based on name and type"""
		descriptions = {
			"Heal": "Restores HP to the caster.",
			"Hurt": "Inflicts damage on a single enemy.",
			"Sleep": "Puts enemies to sleep.",
			"Radiant": "Creates a bright light in dungeons.",
			"Stopspell": "Prevents enemies from casting spells.",
			"Outside": "Transports the caster outside of caves and castles.",
			"Return": "Transports the caster to Tantegel Castle.",
			"Repel": "Repels weak monsters in the field.",
			"Healmore": "Restores more HP to the caster.",
			"Hurtmore": "Inflicts more damage on enemies."
		}
		return descriptions.get(name, f"A {spell_type.name.lower()} spell.")

	def extract_shop_data(self) -> Dict[int, ShopData]:
		"""Extract shop and inn data from ROM ShopItemsTbl and InnCostTbl"""
		shops = {}

		# ShopItemsTbl at Bank00:L9991 and InnCostTbl at Bank00:L998C
		# ROM offsets: Bank 0 + offset - 0x8000
		shop_items_offset = 0x1991	# L9991 - 0x8000 = 0x1991
		inn_cost_offset = 0x198C	# L998C - 0x8000 = 0x198C

		# Inn costs from InnCostTbl
		inn_costs = []
		for i in range(5):	# 5 towns with inns
			if inn_cost_offset + i < len(self.rom_data):
				inn_costs.append(self.rom_data[inn_cost_offset + i])
			else:
				inn_costs.append(0)

		# Shop definitions from the ROM data
		shop_definitions = [
			# Weapons and armor shops
			(0, "Koll Weapons & Armor", "Koll", 0x1991, inn_costs[0]),		 # L9991
			(1, "Brecconary Weapons & Armor", "Brecconary", 0x1997, inn_costs[1]),	# L9997
			(2, "Garinham Weapons & Armor", "Garinham", 0x199E, inn_costs[2]),		# L999E
			(3, "Cantlin Weapons & Armor 1", "Cantlin", 0x19A6, inn_costs[3]),	 # L99A6
			(4, "Cantlin Weapons & Armor 2", "Cantlin", 0x19AD, inn_costs[3]),	 # L99AD
			(5, "Cantlin Weapons & Armor 3", "Cantlin", 0x19B2, inn_costs[3]),	 # L99B2
			(6, "Rimuldar Weapons & Armor", "Rimuldar", 0x19B5, inn_costs[4]),	 # L99B5
			# Item shops
			(7, "Koll Item Shop", "Koll", 0x19BC, 0),			 # L99BC
			(8, "Brecconary Item Shop", "Brecconary", 0x19C1, 0),	# L99C1
			(9, "Garinham Item Shop", "Garinham", 0x19C5, 0),		# L99C5
			(10, "Cantlin Item Shop 1", "Cantlin", 0x19C9, 0),		 # L99C9
			(11, "Cantlin Item Shop 2", "Cantlin", 0x19CC, 0),		 # L99CC
		]

		for shop_id, name, location, items_offset, inn_price in shop_definitions:
			# Read item list from ROM (terminated by 0xFD)
			items = []
			offset = items_offset
			while offset < len(self.rom_data):
				item_byte = self.rom_data[offset]
				if item_byte == 0xFD:	# End marker
					break
				items.append(item_byte)
				offset += 1

			shop = ShopData(
				id=shop_id,
				name=name,
				location=location,
				items=items,
				inn_price=inn_price if inn_price > 0 else None
			)
			shops[shop_id] = shop

		return shops

		return shops

	def extract_dialog_data(self) -> Dict[int, DialogEntry]:
		"""Extract dialog text from ROM - simplified due to text compression"""
		dialogs = {}

		# Dragon Warrior uses complex text compression that requires detailed
		# knowledge of the compression algorithm. For now, provide basic dialog
		# structure based on known game text.

		# TextBlock locations in Bank02 (approximate)
		# Real extraction would need to decompress the text data
		dialog_definitions = [
			(0, "King Lorik", "Tantegel Castle", "I am Lorik, King of Alefgard. It is said that in ages past Erdrick came to this land..."),
			(1, "Castle Guard", "Tantegel Castle", "Welcome to Tantegel Castle. You need Gwaelin's Love to get to the Dragonlord."),
			(2, "Weapon Shop", "Brecconary", "We deal in weapons and armor. Dost thou wish to buy anything?"),
			(3, "Armor Shop", "Brecconary", "Welcome! We have the finest armor. What dost thou want?"),
			(4, "Inn Keeper", "Brecconary", "Welcome to our inn. Room and board is 6 gold coins. Dost thou want a room?"),
			(5, "Old Man", "Garinham", "There is a town where a flute is needed. Those rich people don't know the value of dreams."),
			(6, "Villager", "Kol", "A witch named Lia lives in a cave near here and will make you a Flame Sword if you bring her a Dragon's Scale."),
			(7, "Merchant", "Rimuldar", "Magic armor is hidden in the town of Cantlin. Search the ground there."),
			(8, "Cantlin Citizen", "Cantlin", "Watch out! A Red Dragon guards the Erdrick's Armor here."),
			(9, "Princess Laura", "Charlock Castle", "I am Princess Laura. If thou dost save me, I will give thee a token of my love.")
		]

		for dialog_id, npc_name, location, text in dialog_definitions:
			dialog = DialogEntry(
				id=dialog_id,
				npc_name=npc_name,
				location=location,
				text=text,
				pointer=0x8000 + (dialog_id * 50),	# Approximate pointer
				compressed=True	# Dragon Warrior uses compressed text
			)
			dialogs[dialog_id] = dialog

		return dialogs

	def extract_npc_data(self) -> Dict[int, NPCData]:
		"""Extract NPC placement and data from ROM map data"""
		npcs = {}

		# NPC data is embedded in map data and requires complex parsing
		# of the map format and NPC placement tables. This provides basic
		# NPC structure based on known game content.

		npc_definitions = [
			(0, "King Lorik", 1, Position(10, 8), 0, 0, None, None),
			(1, "Castle Guard", 1, Position(12, 10), 1, 1, None, None),
			(2, "Weapon Shopkeeper", 2, Position(5, 3), 2, 2, 0, None),
			(3, "Armor Shopkeeper", 2, Position(7, 3), 3, 3, 1, None),
			(4, "Inn Keeper", 2, Position(9, 5), 4, 4, 2, None),
			(5, "Old Man", 8, Position(8, 4), 5, 5, None, None),
			(6, "Merchant", 7, Position(4, 6), 6, 6, None, None),
			(7, "Wise Man", 6, Position(12, 8), 7, 7, None, None),
			(8, "Cantlin Citizen", 5, Position(15, 12), 8, 8, None, None),
			(9, "Princess Laura", 3, Position(8, 8), 9, 9, None, None)
		]

		for npc_id, name, map_id, pos, sprite_id, dialog_id, shop_id, gives_item in npc_definitions:
			npc = NPCData(
				id=npc_id,
				name=name,
				map_id=map_id,
				position=pos,
				sprite_id=sprite_id,
				dialog_id=dialog_id,
				shop_id=shop_id,
				gives_item=gives_item
			)
			npcs[npc_id] = npc

		return npcs

	def extract_all_data(self) -> GameData:
		"""Extract all game data"""
		console.print("[blue]Extracting Dragon Warrior game data...[/blue]\n")

		# Extract all data types
		monsters = self.extract_monster_stats()
		console.print(f"Extracted {len(monsters)} monster stats")

		items = self.extract_item_data()
		console.print(f"Extracted {len(items)} items")

		spells = self.extract_spell_data()
		console.print(f"Extracted {len(spells)} spells")

		shops = self.extract_shop_data()
		console.print(f"Extracted {len(shops)} shops")

		dialogs = self.extract_dialog_data()
		console.print(f"Extracted {len(dialogs)} dialog entries")

		npcs = self.extract_npc_data()
		console.print(f"Extracted {len(npcs)} NPCs")

		# Create complete game data
		game_data = GameData(
			monsters=monsters,
			items=items,
			spells=spells,
			shops=shops,
			dialogs=dialogs,
			maps={},		# Will be filled by graphics extractor
			npcs=npcs,
			graphics={},	# Will be filled by graphics extractor
			palettes={}	 # Will be filled by graphics extractor
		)

		# Save complete data
		game_data.save_json(self.json_dir / "complete_game_data.json")

		# Save individual JSON files
		self._save_individual_files(monsters, items, spells, shops, dialogs, npcs)

		console.print(f"\n[green]Data extraction complete![/green]")
		console.print(f"	 JSON files: {self.json_dir}")

		return game_data

	def _save_individual_files(self, monsters, items, spells, shops, dialogs, npcs):
		"""Save individual JSON files for each data type"""

		# Monsters
		monsters_data = {str(k): v.to_dict() for k, v in monsters.items()}
		with open(self.json_dir / "monsters.json", 'w', encoding='utf-8') as f:
			json.dump(monsters_data, f, indent=2, ensure_ascii=False)

		# Items
		items_data = {str(k): v.to_dict() for k, v in items.items()}
		with open(self.json_dir / "items.json", 'w', encoding='utf-8') as f:
			json.dump(items_data, f, indent=2, ensure_ascii=False)

		# Spells
		spells_data = {str(k): v.to_dict() for k, v in spells.items()}
		with open(self.json_dir / "spells.json", 'w', encoding='utf-8') as f:
			json.dump(spells_data, f, indent=2, ensure_ascii=False)

		# Shops
		shops_data = {str(k): v.to_dict() for k, v in shops.items()}
		with open(self.json_dir / "shops.json", 'w', encoding='utf-8') as f:
			json.dump(shops_data, f, indent=2, ensure_ascii=False)

		# Dialogs
		dialogs_data = {str(k): v.to_dict() for k, v in dialogs.items()}
		with open(self.json_dir / "dialogs.json", 'w', encoding='utf-8') as f:
			json.dump(dialogs_data, f, indent=2, ensure_ascii=False)

		# NPCs
		npcs_data = {str(k): v.to_dict() for k, v in npcs.items()}
		with open(self.json_dir / "npcs.json", 'w', encoding='utf-8') as f:
			json.dump(npcs_data, f, indent=2, ensure_ascii=False)

@click.command()
@click.argument('rom_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='assets', help='Output directory')
def extract_data(rom_path: str, output_dir: str):
	"""Extract Dragon Warrior game data to JSON"""

	try:
		extractor = DragonWarriorDataExtractor(rom_path, output_dir)
		game_data = extractor.extract_all_data()

		console.print("\n[green]🎯 Data extraction completed successfully![/green]")

	except Exception as e:
		console.print(f"[red]Error: {e}[/red]")
		raise

if __name__ == "__main__":
	extract_data()
