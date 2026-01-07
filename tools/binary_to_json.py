#!/usr/bin/env python3
"""
Dragon Warrior Binary to JSON Converter

Converts .dwdata binary intermediate files to JSON format that can be
roundtripped back to binary with validate_roundtrip.py.

This ensures the JSON structure matches what the binary expects,
enabling proper validation of the asset pipeline.

Usage:
	python binary_to_json.py
	python binary_to_json.py --asset monsters
	python binary_to_json.py --output-dir assets/json/roundtrip

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
import json
import struct
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Monster names for reference
MONSTER_NAMES = [
	"Slime", "Red Slime", "Drakee", "Ghost", "Magician", "Magidrakee",
	"Scorpion", "Druin", "Poltergeist", "Droll", "Drakeema", "Skeleton",
	"Warlock", "Metal Scorpion", "Wolf", "Wraith", "Metal Slime", "Specter",
	"Wolflord", "Druinlord", "Drollmagi", "Wyvern", "Rogue Scorpion",
	"Wraith Knight", "Golem", "Goldman", "Knight", "Magiwyvern",
	"Demon Knight", "Werewolf", "Green Dragon", "Starwyvern", "Wizard",
	"Axe Knight", "Blue Dragon", "Stoneman", "Armored Knight", "Red Dragon",
	"Dragonlord (Form 1)", "Dragonlord (Form 2)"
]

# Spell names
SPELL_NAMES = [
	"HEAL", "HURT", "SLEEP", "RADIANT", "STOPSPELL",
	"OUTSIDE", "RETURN", "REPEL", "HEALMORE", "HURTMORE"
]

# Item names
ITEM_NAMES = [
	"Bamboo Pole", "Club", "Copper Sword", "Hand Axe", "Broad Sword",
	"Flame Sword", "Erdrick's Sword", "Clothes", "Leather Armor",
	"Chain Mail", "Half Plate", "Full Plate", "Magic Armor",
	"Erdrick's Armor", "Small Shield", "Large Shield", "Silver Shield",
	"Herb", "Magic Key", "Torch", "Fairy Water", "Wings", "Dragon's Scale",
	"Fighter's Ring", "Cursed Belt", "Cursed Necklace", "Gwaelin's Love",
	"Silver Harp", "Staff of Rain", "Stones of Sunlight", "Rainbow Drop",
	"Erdrick's Token"
]


class BinaryToJsonConverter:
	"""Converts .dwdata binary files to roundtrip-compatible JSON."""

	def __init__(self, project_root: Path):
		self.project_root = project_root
		self.dwdata_dir = project_root / 'extracted_assets' / 'binary'
		self.output_dir = project_root / 'assets' / 'json' / 'roundtrip'

	def load_dwdata(self, filename: str) -> Optional[bytes]:
		"""Load data section from .dwdata file (skip 32-byte header)."""
		path = self.dwdata_dir / filename
		if not path.exists():
			print(f"  ✗ File not found: {path}")
			return None

		with open(path, 'rb') as f:
			data = f.read()

		if len(data) < 32:
			print(f"  ✗ Invalid file (too small): {path}")
			return None

		# Get data size from header at offset 0x08
		data_size = struct.unpack_from('<I', data, 0x08)[0]
		return data[32:32 + data_size]

	def convert_monsters(self) -> Optional[Dict]:
		"""
		Convert monsters.dwdata to JSON.

		Monster format (16 bytes each):
		Bytes 0-7 (used):
			0: Strength (attack power)
			1: Defense
			2: HP
			3: Spell pattern
			4: Agility
			5: Resistance (magic defense)
			6: Experience
			7: Gold
		Bytes 8-15 (unused but preserved for exact roundtrip):
			8-15: Raw bytes (may contain garbage/other data)
		"""
		print("\n--- Converting monsters.dwdata ---")
		data = self.load_dwdata('monsters.dwdata')
		if data is None:
			return None

		monsters = []
		num_monsters = len(data) // 16

		for i in range(num_monsters):
			offset = i * 16
			record = data[offset:offset + 16]

			name = MONSTER_NAMES[i] if i < len(MONSTER_NAMES) else f"Monster_{i:02d}"

			# Extract used stats (bytes 0-7)
			monster = {
				"id": i,
				"name": name,
				"strength": record[0],
				"defense": record[1],
				"hp": record[2],
				"spell_pattern": record[3],
				"agility": record[4],
				"resistance": record[5],
				"experience": record[6],
				"gold": record[7],
				# Preserve unused bytes for exact roundtrip
				"_raw_bytes_8_15": [record[j] for j in range(8, 16)]
			}
			monsters.append(monster)

		result = {
			"_comment": "Dragon Warrior monster data - roundtrip compatible",
			"_source": "Extracted from monsters.dwdata",
			"_format": "16 bytes per monster: 8 used stats + 8 unused bytes",
			"monsters": monsters
		}

		print(f"  ✓ Converted {num_monsters} monsters")
		return result

	def convert_spells(self) -> Optional[Dict]:
		"""
		Convert spells.dwdata to JSON.

		NOTE: The spell offset in extract_to_binary.py may be incorrect.
		This converter preserves all raw bytes for exact roundtrip.

		Format: 8 bytes each, all preserved as raw bytes.
		"""
		print("\n--- Converting spells.dwdata ---")
		data = self.load_dwdata('spells.dwdata')
		if data is None:
			return None

		spells = []
		num_spells = len(data) // 8

		for i in range(num_spells):
			offset = i * 8
			record = data[offset:offset + 8]

			name = SPELL_NAMES[i] if i < len(SPELL_NAMES) else f"Spell_{i:02d}"

			# Preserve all 8 bytes as raw data for exact roundtrip
			spell = {
				"id": i,
				"name": name,
				"_raw_bytes": [record[j] for j in range(8)]
			}
			spells.append(spell)

		result = {
			"_comment": "Dragon Warrior spell data - roundtrip compatible",
			"_source": "Extracted from spells.dwdata",
			"_warning": "Spell offsets may need verification",
			"spells": spells
		}

		print(f"  ✓ Converted {num_spells} spells")
		return result

	def convert_items(self) -> Optional[Dict]:
		"""
		Convert items.dwdata to JSON.

		NOTE: The item offset in extract_to_binary.py may be incorrect.
		This converter preserves all raw bytes for exact roundtrip.

		Format: 8 bytes each, all preserved as raw bytes.
		"""
		print("\n--- Converting items.dwdata ---")
		data = self.load_dwdata('items.dwdata')
		if data is None:
			return None

		items = []
		num_items = len(data) // 8

		for i in range(num_items):
			offset = i * 8
			record = data[offset:offset + 8]

			name = ITEM_NAMES[i] if i < len(ITEM_NAMES) else f"Item_{i:02d}"

			# Preserve all 8 bytes as raw data for exact roundtrip
			item = {
				"id": i,
				"name": name,
				"_raw_bytes": [record[j] for j in range(8)]
			}
			items.append(item)

		result = {
			"_comment": "Dragon Warrior item data - roundtrip compatible",
			"_source": "Extracted from items.dwdata",
			"_warning": "Item offsets may need verification",
			"items": items
		}

		print(f"  ✓ Converted {num_items} items")
		return result

	def save_json(self, data: Dict, filename: str) -> bool:
		"""Save JSON data to file."""
		self.output_dir.mkdir(parents=True, exist_ok=True)
		path = self.output_dir / filename

		with open(path, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent='\t', ensure_ascii=False)

		print(f"  ✓ Wrote: {path}")
		return True

	def convert_all(self) -> bool:
		"""Convert all .dwdata files to JSON."""
		success = True

		# Monsters
		monsters = self.convert_monsters()
		if monsters:
			self.save_json(monsters, 'monsters_roundtrip.json')
		else:
			success = False

		# Spells
		spells = self.convert_spells()
		if spells:
			self.save_json(spells, 'spells_roundtrip.json')
		else:
			success = False

		# Items
		items = self.convert_items()
		if items:
			self.save_json(items, 'items_roundtrip.json')
		else:
			success = False

		return success


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Convert Dragon Warrior .dwdata files to roundtrip JSON'
	)
	parser.add_argument(
		'--asset', '-a',
		type=str,
		choices=['monsters', 'spells', 'items', 'all'],
		default='all',
		help='Asset type to convert'
	)
	parser.add_argument(
		'--output-dir', '-o',
		type=Path,
		help='Output directory for JSON files'
	)

	args = parser.parse_args()

	# Determine project root
	script_dir = Path(__file__).parent
	project_root = script_dir.parent

	print("=" * 60)
	print("Dragon Warrior Binary → JSON Converter")
	print("=" * 60)

	converter = BinaryToJsonConverter(project_root)

	if args.output_dir:
		converter.output_dir = args.output_dir

	if args.asset == 'all':
		success = converter.convert_all()
	elif args.asset == 'monsters':
		data = converter.convert_monsters()
		success = data is not None
		if success:
			converter.save_json(data, 'monsters_roundtrip.json')
	elif args.asset == 'spells':
		data = converter.convert_spells()
		success = data is not None
		if success:
			converter.save_json(data, 'spells_roundtrip.json')
	elif args.asset == 'items':
		data = converter.convert_items()
		success = data is not None
		if success:
			converter.save_json(data, 'items_roundtrip.json')

	print("\n" + "=" * 60)
	if success:
		print("✅ Conversion complete!")
		print("\nNext step: python tools/validate_roundtrip.py --roundtrip")
	else:
		print("❌ Some conversions failed")

	return 0 if success else 1


if __name__ == '__main__':
	sys.exit(main())
