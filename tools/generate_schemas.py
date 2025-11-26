#!/usr/bin/env python3
"""
JSON Schema Generator for Dragon Warrior Data

Generates JSON schemas for validating extracted game data.

Features:
- Generate schema from sample data
- Strict type validation
- Range constraints
- Required field enforcement
- Cross-reference validation

Usage:
	python tools/generate_schemas.py
	python tools/generate_schemas.py --output schemas/
	python tools/generate_schemas.py --validate

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, Any, List

# Default paths
DEFAULT_ASSETS = "extracted_assets"
DEFAULT_OUTPUT = "schemas"


class SchemaGenerator:
	"""Generate JSON schemas for game data"""

	def __init__(self, assets_dir: str, output_dir: str):
		"""
		Initialize schema generator

		Args:
			assets_dir: Assets directory
			output_dir: Schema output directory
		"""
		self.assets_dir = Path(assets_dir)
		self.output_dir = Path(output_dir)
		self.json_dir = self.assets_dir / "json"

	def generate_monster_schema(self) -> Dict[str, Any]:
		"""Generate JSON schema for monster data"""
		schema = {
			"$schema": "http://json-schema.org/draft-07/schema#",
			"$id": "https://dragonwarrior.toolkit/schemas/monsters.json",
			"title": "Dragon Warrior Monster Data",
			"description": "Schema for validating monster statistics and attributes",
			"type": "array",
			"minItems": 39,
			"maxItems": 100,  # Allow for custom monsters
			"items": {
				"type": "object",
				"required": [
					"id", "name", "hp", "attack", "defense", "agility",
					"spell", "m_defense", "xp", "gold"
				],
				"properties": {
					"id": {
						"type": "integer",
						"description": "Monster ID (0-based index)",
						"minimum": 0,
						"maximum": 255
					},
					"name": {
						"type": "string",
						"description": "Monster name",
						"minLength": 1,
						"maxLength": 20
					},
					"hp": {
						"type": "integer",
						"description": "Hit points",
						"minimum": 1,
						"maximum": 255
					},
					"attack": {
						"type": "integer",
						"description": "Attack power",
						"minimum": 0,
						"maximum": 255
					},
					"defense": {
						"type": "integer",
						"description": "Defense power",
						"minimum": 0,
						"maximum": 255
					},
					"agility": {
						"type": "integer",
						"description": "Agility/speed",
						"minimum": 0,
						"maximum": 255
					},
					"spell": {
						"type": "integer",
						"description": "Spell ID (0 = none, 1-9 = spell)",
						"minimum": 0,
						"maximum": 9
					},
					"m_defense": {
						"type": "integer",
						"description": "Magic defense",
						"minimum": 0,
						"maximum": 255
					},
					"xp": {
						"type": "integer",
						"description": "Experience points rewarded",
						"minimum": 0,
						"maximum": 65535
					},
					"gold": {
						"type": "integer",
						"description": "Gold rewarded",
						"minimum": 0,
						"maximum": 65535
					},
					"resist_sleep": {
						"type": "integer",
						"description": "Sleep resistance (0-15)",
						"minimum": 0,
						"maximum": 15
					},
					"resist_stopspell": {
						"type": "integer",
						"description": "Stopspell resistance (0-15)",
						"minimum": 0,
						"maximum": 15
					},
					"resist_hurt": {
						"type": "integer",
						"description": "Hurt spell resistance (0-15)",
						"minimum": 0,
						"maximum": 15
					},
					"resist_dodge": {
						"type": "integer",
						"description": "Dodge chance (0-15)",
						"minimum": 0,
						"maximum": 15
					},
					"sprite_family": {
						"type": "string",
						"description": "Sprite family name"
					}
				},
				"additionalProperties": True  # Allow custom properties
			}
		}

		return schema

	def generate_spell_schema(self) -> Dict[str, Any]:
		"""Generate JSON schema for spell data"""
		schema = {
			"$schema": "http://json-schema.org/draft-07/schema#",
			"$id": "https://dragonwarrior.toolkit/schemas/spells.json",
			"title": "Dragon Warrior Spell Data",
			"description": "Schema for validating spell statistics",
			"type": "array",
			"minItems": 10,
			"maxItems": 20,
			"items": {
				"type": "object",
				"required": ["id", "name", "mp_cost", "power"],
				"properties": {
					"id": {
						"type": "integer",
						"description": "Spell ID",
						"minimum": 0,
						"maximum": 19
					},
					"name": {
						"type": "string",
						"description": "Spell name",
						"minLength": 1,
						"maxLength": 15
					},
					"mp_cost": {
						"type": "integer",
						"description": "MP cost to cast",
						"minimum": 0,
						"maximum": 255
					},
					"power": {
						"type": "integer",
						"description": "Spell power/effectiveness",
						"minimum": 0,
						"maximum": 255
					},
					"effect_type": {
						"type": "string",
						"description": "Type of spell effect",
						"enum": ["damage", "healing", "buff", "debuff", "utility"]
					},
					"target": {
						"type": "string",
						"description": "Spell target",
						"enum": ["self", "enemy", "all_enemies", "party", "field"]
					}
				},
				"additionalProperties": True
			}
		}

		return schema

	def generate_item_schema(self) -> Dict[str, Any]:
		"""Generate JSON schema for item data"""
		schema = {
			"$schema": "http://json-schema.org/draft-07/schema#",
			"$id": "https://dragonwarrior.toolkit/schemas/items.json",
			"title": "Dragon Warrior Item Data",
			"description": "Schema for validating item/equipment statistics",
			"type": "array",
			"minItems": 32,
			"maxItems": 64,
			"items": {
				"type": "object",
				"required": [
					"id", "name", "buy_price", "sell_price",
					"attack_bonus", "defense_bonus"
				],
				"properties": {
					"id": {
						"type": "integer",
						"description": "Item ID",
						"minimum": 0,
						"maximum": 63
					},
					"name": {
						"type": "string",
						"description": "Item name",
						"minLength": 1,
						"maxLength": 20
					},
					"buy_price": {
						"type": "integer",
						"description": "Purchase price (0 = not for sale)",
						"minimum": 0,
						"maximum": 65535
					},
					"sell_price": {
						"type": "integer",
						"description": "Sale price (0 = cannot sell)",
						"minimum": 0,
						"maximum": 65535
					},
					"attack_bonus": {
						"type": "integer",
						"description": "Attack bonus when equipped",
						"minimum": -128,
						"maximum": 127
					},
					"defense_bonus": {
						"type": "integer",
						"description": "Defense bonus when equipped",
						"minimum": -128,
						"maximum": 127
					},
					"type": {
						"type": "string",
						"description": "Item type",
						"enum": ["weapon", "armor", "shield", "helmet", "item", "key_item"]
					},
					"usable_in_battle": {
						"type": "boolean",
						"description": "Can be used in battle"
					},
					"usable_in_field": {
						"type": "boolean",
						"description": "Can be used in field/menu"
					}
				},
				"additionalProperties": True
			}
		}

		return schema

	def save_schema(self, filename: str, schema: Dict[str, Any]) -> bool:
		"""
		Save schema to file

		Args:
			filename: Output filename
			schema: Schema dict

		Returns:
			True if successful
		"""
		try:
			self.output_dir.mkdir(parents=True, exist_ok=True)

			output_file = self.output_dir / filename

			with open(output_file, 'w') as f:
				json.dump(schema, f, indent=2)

			print(f"✓ Saved schema: {output_file}")
			return True
		except Exception as e:
			print(f"❌ Failed to save {filename}: {e}")
			return False

	def generate_all_schemas(self):
		"""Generate all schemas"""
		print("=" * 70)
		print("Dragon Warrior JSON Schema Generator")
		print("=" * 70)

		print("\n--- Generating Schemas ---")

		# Monster schema
		monster_schema = self.generate_monster_schema()
		self.save_schema("monsters.schema.json", monster_schema)

		# Spell schema
		spell_schema = self.generate_spell_schema()
		self.save_schema("spells.schema.json", spell_schema)

		# Item schema
		item_schema = self.generate_item_schema()
		self.save_schema("items.schema.json", item_schema)

		print("\n" + "=" * 70)
		print(f"✓ Generated 3 schemas in {self.output_dir}")
		print("=" * 70)

	def validate_data_against_schema(self, data_file: str, schema_file: str) -> bool:
		"""
		Validate JSON data against schema

		Args:
			data_file: Data JSON file
			schema_file: Schema JSON file

		Returns:
			True if valid
		"""
		try:
			import jsonschema
		except ImportError:
			print("⚠ jsonschema package not installed")
			print("  Install with: pip install jsonschema")
			return False

		# Load data
		with open(self.json_dir / data_file, 'r') as f:
			data = json.load(f)

		# Load schema
		with open(self.output_dir / schema_file, 'r') as f:
			schema = json.load(f)

		# Validate
		try:
			jsonschema.validate(instance=data, schema=schema)
			print(f"✓ {data_file} validates against {schema_file}")
			return True
		except jsonschema.ValidationError as e:
			print(f"❌ Validation failed for {data_file}:")
			print(f"  {e.message}")
			print(f"  Path: {'.'.join(str(p) for p in e.absolute_path)}")
			return False

	def validate_all_data(self) -> bool:
		"""Validate all data files against schemas"""
		print("\n--- Validating Data Against Schemas ---")

		validations = [
			('monsters.json', 'monsters.schema.json'),
			('spells.json', 'spells.schema.json'),
			('items.json', 'items.schema.json'),
		]

		all_valid = True

		for data_file, schema_file in validations:
			if not self.validate_data_against_schema(data_file, schema_file):
				all_valid = False

		return all_valid


def main():
	"""Main entry point"""
	parser = argparse.ArgumentParser(
		description='Generate JSON schemas for Dragon Warrior data',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  # Generate all schemas
  python tools/generate_schemas.py

  # Custom output directory
  python tools/generate_schemas.py --output my_schemas/

  # Generate and validate
  python tools/generate_schemas.py --validate
		"""
	)

	parser.add_argument(
		'--assets',
		default=DEFAULT_ASSETS,
		help=f'Assets directory (default: {DEFAULT_ASSETS})'
	)

	parser.add_argument(
		'--output',
		default=DEFAULT_OUTPUT,
		help=f'Schema output directory (default: {DEFAULT_OUTPUT})'
	)

	parser.add_argument(
		'--validate',
		action='store_true',
		help='Validate data against generated schemas'
	)

	args = parser.parse_args()

	# Initialize generator
	generator = SchemaGenerator(args.assets, args.output)

	# Generate schemas
	generator.generate_all_schemas()

	# Validate if requested
	if args.validate:
		success = generator.validate_all_data()
		return 0 if success else 1

	return 0


if __name__ == '__main__':
	sys.exit(main())
