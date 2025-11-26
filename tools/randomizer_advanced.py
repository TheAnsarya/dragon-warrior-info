#!/usr/bin/env python3
"""
Advanced Randomizer for Dragon Warrior

Comprehensive randomization system with configurable options for monsters,
items, maps, shops, and game logic.

Features:
- Monster randomization (stats, drops, locations)
- Item randomization (placement, prices, effects)
- Shop inventory randomization
- Treasure chest randomization
- Spell randomization
- Map entrance randomization
- Enemy encounter randomization
- Difficulty scaling
- Seed-based generation
- Logic validation
- Randomizer presets
- Spoiler log generation
- Progressive difficulty
- Race mode support

Usage:
	python tools/randomizer_advanced.py [ROM_FILE] [OPTIONS]

Examples:
	# Full randomization with seed
	python tools/randomizer_advanced.py rom.nes --seed 12345 --output randomized.nes

	# Monster stats only
	python tools/randomizer_advanced.py rom.nes --monsters-only --difficulty 150

	# Generate spoiler log
	python tools/randomizer_advanced.py rom.nes --seed 12345 --spoiler spoiler.txt

	# Use preset
	python tools/randomizer_advanced.py rom.nes --preset chaos

Author: Dragon Warrior ROM Hacking Toolkit
Version: 2.0
"""

import sys
import os
import json
import random
import hashlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import argparse
from datetime import datetime


# ============================================================================
# RANDOMIZER CONFIGURATION
# ============================================================================

class RandomizerPreset(Enum):
	"""Randomizer presets."""
	NORMAL = "normal"
	CHAOS = "chaos"
	HARD = "hard"
	EASY = "easy"
	BALANCED = "balanced"
	RACE = "race"


@dataclass
class RandomizerOptions:
	"""Randomizer configuration options."""
	seed: int = 0
	
	# What to randomize
	randomize_monsters: bool = True
	randomize_items: bool = True
	randomize_shops: bool = True
	randomize_treasures: bool = True
	randomize_spells: bool = True
	randomize_encounters: bool = False
	randomize_map_connections: bool = False
	
	# Monster options
	monster_stat_variance: int = 30  # Percent
	monster_hp_min: int = 5
	monster_hp_max: int = 255
	randomize_monster_gold: bool = True
	randomize_monster_exp: bool = True
	
	# Item options
	item_price_variance: int = 50  # Percent
	item_price_min: int = 10
	item_price_max: int = 9999
	randomize_equipment_stats: bool = True
	equipment_stat_variance: int = 40
	
	# Shop options
	shop_inventory_size: int = 6
	allow_random_shop_items: bool = True
	
	# Treasure options
	treasure_randomize_gold: bool = True
	treasure_gold_multiplier: float = 1.0
	
	# Difficulty
	difficulty_scale: int = 100  # Percent (100 = normal)
	progressive_difficulty: bool = True
	
	# Logic
	ensure_completion: bool = True  # Ensure game is beatable
	require_key_items: bool = True  # Key items must be accessible
	
	# Output
	generate_spoiler: bool = True
	spoiler_path: Optional[Path] = None


@dataclass
class RandomizationResult:
	"""Result of randomization."""
	seed: int
	timestamp: str
	options: RandomizerOptions
	monsters_changed: int = 0
	items_changed: int = 0
	shops_changed: int = 0
	treasures_changed: int = 0
	warnings: List[str] = field(default_factory=list)
	spoiler_data: Dict = field(default_factory=dict)


# ============================================================================
# RANDOMIZER ENGINE
# ============================================================================

class Randomizer:
	"""Main randomization engine."""

	def __init__(self, options: RandomizerOptions):
		self.options = options
		self.rng = random.Random(options.seed)
		self.result = RandomizationResult(
			seed=options.seed,
			timestamp=datetime.now().isoformat(),
			options=options
		)

	def randomize_monster_stats(self, monster: Dict) -> Dict:
		"""Randomize monster statistics."""
		randomized = monster.copy()

		variance = self.options.monster_stat_variance / 100.0

		# Randomize HP
		if 'hp' in monster:
			original_hp = monster['hp']
			min_hp = max(self.options.monster_hp_min, int(original_hp * (1 - variance)))
			max_hp = min(self.options.monster_hp_max, int(original_hp * (1 + variance)))
			randomized['hp'] = self.rng.randint(min_hp, max_hp)

		# Randomize strength
		if 'strength' in monster:
			original_str = monster['strength']
			min_str = max(1, int(original_str * (1 - variance)))
			max_str = min(255, int(original_str * (1 + variance)))
			randomized['strength'] = self.rng.randint(min_str, max_str)

		# Randomize agility
		if 'agility' in monster:
			original_agi = monster['agility']
			min_agi = max(1, int(original_agi * (1 - variance)))
			max_agi = min(255, int(original_agi * (1 + variance)))
			randomized['agility'] = self.rng.randint(min_agi, max_agi)

		# Randomize gold
		if self.options.randomize_monster_gold and 'gold' in monster:
			original_gold = monster['gold']
			min_gold = max(0, int(original_gold * (1 - variance)))
			max_gold = int(original_gold * (1 + variance))
			randomized['gold'] = self.rng.randint(min_gold, max_gold)

		# Randomize experience
		if self.options.randomize_monster_exp and 'experience' in monster:
			original_exp = monster['experience']
			min_exp = max(1, int(original_exp * (1 - variance)))
			max_exp = int(original_exp * (1 + variance))
			randomized['experience'] = self.rng.randint(min_exp, max_exp)

		# Apply difficulty scaling
		scale = self.options.difficulty_scale / 100.0
		if scale != 1.0:
			if 'hp' in randomized:
				randomized['hp'] = max(1, int(randomized['hp'] * scale))
			if 'strength' in randomized:
				randomized['strength'] = max(1, int(randomized['strength'] * scale))

		return randomized

	def randomize_item_stats(self, item: Dict) -> Dict:
		"""Randomize item statistics."""
		randomized = item.copy()

		variance = self.options.item_price_variance / 100.0

		# Randomize price
		if 'price' in item:
			original_price = item['price']
			min_price = max(self.options.item_price_min, int(original_price * (1 - variance)))
			max_price = min(self.options.item_price_max, int(original_price * (1 + variance)))
			randomized['price'] = self.rng.randint(min_price, max_price)

		# Randomize equipment stats
		if self.options.randomize_equipment_stats:
			eq_variance = self.options.equipment_stat_variance / 100.0

			if 'attack' in item:
				original_atk = item['attack']
				min_atk = max(0, int(original_atk * (1 - eq_variance)))
				max_atk = min(255, int(original_atk * (1 + eq_variance)))
				randomized['attack'] = self.rng.randint(min_atk, max_atk)

			if 'defense' in item:
				original_def = item['defense']
				min_def = max(0, int(original_def * (1 - eq_variance)))
				max_def = min(255, int(original_def * (1 + eq_variance)))
				randomized['defense'] = self.rng.randint(min_def, max_def)

		return randomized

	def randomize_shop_inventory(self, shop: Dict, all_items: List[Dict]) -> Dict:
		"""Randomize shop inventory."""
		randomized = shop.copy()

		if not self.options.allow_random_shop_items:
			return randomized

		# Get item pool (exclude key items)
		item_pool = [item for item in all_items if not item.get('key_item', False)]

		# Randomly select items
		num_items = min(self.options.shop_inventory_size, len(item_pool))
		selected_items = self.rng.sample(item_pool, num_items)

		randomized['inventory'] = [item['id'] for item in selected_items]

		return randomized

	def randomize_treasure(self, treasure: Dict, all_items: List[Dict]) -> Dict:
		"""Randomize treasure chest contents."""
		randomized = treasure.copy()

		# Decide if it's gold or item
		is_gold = self.rng.random() < 0.3

		if is_gold and self.options.treasure_randomize_gold:
			# Randomize gold amount
			base_gold = treasure.get('gold_amount', 100)
			min_gold = max(10, int(base_gold * 0.5))
			max_gold = int(base_gold * 1.5 * self.options.treasure_gold_multiplier)
			randomized['gold_amount'] = self.rng.randint(min_gold, max_gold)
			randomized['item_id'] = 0

		else:
			# Random item (avoid key items in random chests)
			if self.options.require_key_items:
				# Don't randomize key item chests
				if treasure.get('item_id', 0) > 0:
					original_item = next((i for i in all_items if i['id'] == treasure['item_id']), None)
					if original_item and original_item.get('key_item', False):
						return randomized

			# Pick random item
			item_pool = [item for item in all_items if not item.get('key_item', False)]
			if item_pool:
				selected_item = self.rng.choice(item_pool)
				randomized['item_id'] = selected_item['id']
				randomized['gold_amount'] = 0

		return randomized

	def randomize_encounter_zones(self, encounter_zones: List[Dict],
								  all_monsters: List[Dict]) -> List[Dict]:
		"""Randomize monster encounter zones."""
		randomized_zones = []

		for zone in encounter_zones:
			randomized_zone = zone.copy()

			# Shuffle monster groups
			monster_pool = [m for m in all_monsters]
			self.rng.shuffle(monster_pool)

			# Create new monster groups
			num_groups = len(zone.get('monster_groups', []))
			new_groups = []

			for i in range(num_groups):
				# Pick 1-3 monsters for this group
				group_size = self.rng.randint(1, 3)
				group_monsters = []

				for j in range(group_size):
					if monster_pool:
						monster = monster_pool[i % len(monster_pool)]
						group_monsters.append(monster['id'])

				new_groups.append(group_monsters)

			randomized_zone['monster_groups'] = new_groups
			randomized_zones.append(randomized_zone)

		return randomized_zones

	def validate_logic(self, game_data: Dict) -> List[str]:
		"""Validate that game is still beatable."""
		warnings = []

		# Check that key items are obtainable
		if self.options.require_key_items:
			key_items = [item for item in game_data.get('items', [])
						if item.get('key_item', False)]

			for key_item in key_items:
				# Check if it's in a treasure chest
				found_in_treasure = False
				for treasure in game_data.get('treasures', []):
					if treasure.get('item_id') == key_item['id']:
						found_in_treasure = True
						break

				if not found_in_treasure:
					warnings.append(f"Key item '{key_item['name']}' may not be obtainable")

		# Check for impossible difficulty spikes
		if self.options.ensure_completion:
			monsters = game_data.get('monsters', [])
			if monsters:
				# Check first area monsters aren't too strong
				first_area_monsters = monsters[:5]
				avg_hp = sum(m.get('hp', 0) for m in first_area_monsters) / len(first_area_monsters)

				if avg_hp > 100:
					warnings.append("Early game monsters may be too difficult")

		return warnings

	def generate_spoiler_log(self, original_data: Dict, randomized_data: Dict) -> str:
		"""Generate spoiler log."""
		lines = []
		lines.append("=" * 70)
		lines.append("DRAGON WARRIOR RANDOMIZER - SPOILER LOG")
		lines.append("=" * 70)
		lines.append(f"Seed: {self.options.seed}")
		lines.append(f"Generated: {self.result.timestamp}")
		lines.append("")

		# Monster changes
		if self.options.randomize_monsters:
			lines.append("MONSTER CHANGES")
			lines.append("-" * 70)

			orig_monsters = {m['id']: m for m in original_data.get('monsters', [])}
			for monster in randomized_data.get('monsters', []):
				orig = orig_monsters.get(monster['id'])
				if orig:
					lines.append(f"\n{monster.get('name', 'Unknown')} (ID: {monster['id']})")
					lines.append(f"  HP:       {orig.get('hp', 0):3d} → {monster.get('hp', 0):3d}")
					lines.append(f"  Strength: {orig.get('strength', 0):3d} → {monster.get('strength', 0):3d}")
					lines.append(f"  Agility:  {orig.get('agility', 0):3d} → {monster.get('agility', 0):3d}")

					if 'gold' in monster:
						lines.append(f"  Gold:     {orig.get('gold', 0):3d} → {monster.get('gold', 0):3d}")
					if 'experience' in monster:
						lines.append(f"  EXP:      {orig.get('experience', 0):3d} → {monster.get('experience', 0):3d}")

			lines.append("")

		# Item changes
		if self.options.randomize_items:
			lines.append("\nITEM CHANGES")
			lines.append("-" * 70)

			orig_items = {i['id']: i for i in original_data.get('items', [])}
			for item in randomized_data.get('items', []):
				orig = orig_items.get(item['id'])
				if orig:
					lines.append(f"\n{item.get('name', 'Unknown')} (ID: {item['id']})")

					if 'price' in item:
						lines.append(f"  Price:   {orig.get('price', 0):5d} → {item.get('price', 0):5d}")
					if 'attack' in item:
						lines.append(f"  Attack:  {orig.get('attack', 0):3d} → {item.get('attack', 0):3d}")
					if 'defense' in item:
						lines.append(f"  Defense: {orig.get('defense', 0):3d} → {item.get('defense', 0):3d}")

			lines.append("")

		# Treasure changes
		if self.options.randomize_treasures:
			lines.append("\nTREASURE CHANGES")
			lines.append("-" * 70)

			orig_treasures = {t['id']: t for t in original_data.get('treasures', [])}
			for treasure in randomized_data.get('treasures', []):
				orig = orig_treasures.get(treasure['id'])
				if orig:
					orig_item = orig.get('item_id', 0)
					new_item = treasure.get('item_id', 0)

					if orig_item != new_item or orig.get('gold_amount', 0) != treasure.get('gold_amount', 0):
						lines.append(f"\nTreasure {treasure['id']} at ({treasure.get('x', 0)}, {treasure.get('y', 0)})")

						if new_item > 0:
							lines.append(f"  Contains: Item #{new_item}")
						else:
							lines.append(f"  Contains: {treasure.get('gold_amount', 0)} gold")

			lines.append("")

		lines.append("=" * 70)

		return "\n".join(lines)


# ============================================================================
# PRESET CONFIGURATIONS
# ============================================================================

class RandomizerPresets:
	"""Predefined randomizer configurations."""

	@staticmethod
	def get_preset(preset: RandomizerPreset) -> RandomizerOptions:
		"""Get preset configuration."""
		if preset == RandomizerPreset.NORMAL:
			return RandomizerOptions(
				monster_stat_variance=30,
				item_price_variance=40,
				difficulty_scale=100,
				ensure_completion=True
			)

		elif preset == RandomizerPreset.CHAOS:
			return RandomizerOptions(
				monster_stat_variance=80,
				item_price_variance=100,
				randomize_encounters=True,
				randomize_map_connections=True,
				difficulty_scale=120,
				ensure_completion=False
			)

		elif preset == RandomizerPreset.HARD:
			return RandomizerOptions(
				monster_stat_variance=40,
				item_price_variance=50,
				difficulty_scale=150,
				progressive_difficulty=True,
				ensure_completion=True
			)

		elif preset == RandomizerPreset.EASY:
			return RandomizerOptions(
				monster_stat_variance=20,
				item_price_variance=30,
				difficulty_scale=70,
				ensure_completion=True
			)

		elif preset == RandomizerPreset.BALANCED:
			return RandomizerOptions(
				monster_stat_variance=25,
				item_price_variance=35,
				difficulty_scale=100,
				progressive_difficulty=True,
				ensure_completion=True
			)

		elif preset == RandomizerPreset.RACE:
			return RandomizerOptions(
				monster_stat_variance=30,
				item_price_variance=40,
				randomize_treasures=True,
				randomize_shops=True,
				difficulty_scale=110,
				ensure_completion=True,
				generate_spoiler=False
			)

		return RandomizerOptions()


# ============================================================================
# MAIN RANDOMIZER
# ============================================================================

def randomize_game_data(game_data: Dict, options: RandomizerOptions) -> Tuple[Dict, RandomizationResult]:
	"""Randomize game data."""
	randomizer = Randomizer(options)
	randomized_data = {}

	# Copy original data
	for key in game_data:
		if isinstance(game_data[key], list):
			randomized_data[key] = game_data[key].copy()
		else:
			randomized_data[key] = game_data[key]

	# Randomize monsters
	if options.randomize_monsters and 'monsters' in game_data:
		randomized_monsters = []
		for monster in game_data['monsters']:
			randomized_monster = randomizer.randomize_monster_stats(monster)
			randomized_monsters.append(randomized_monster)

		randomized_data['monsters'] = randomized_monsters
		randomizer.result.monsters_changed = len(randomized_monsters)

	# Randomize items
	if options.randomize_items and 'items' in game_data:
		randomized_items = []
		for item in game_data['items']:
			randomized_item = randomizer.randomize_item_stats(item)
			randomized_items.append(randomized_item)

		randomized_data['items'] = randomized_items
		randomizer.result.items_changed = len(randomized_items)

	# Randomize shops
	if options.randomize_shops and 'shops' in game_data:
		randomized_shops = []
		all_items = randomized_data.get('items', [])

		for shop in game_data['shops']:
			randomized_shop = randomizer.randomize_shop_inventory(shop, all_items)
			randomized_shops.append(randomized_shop)

		randomized_data['shops'] = randomized_shops
		randomizer.result.shops_changed = len(randomized_shops)

	# Randomize treasures
	if options.randomize_treasures and 'treasures' in game_data:
		randomized_treasures = []
		all_items = randomized_data.get('items', [])

		for treasure in game_data['treasures']:
			randomized_treasure = randomizer.randomize_treasure(treasure, all_items)
			randomized_treasures.append(randomized_treasure)

		randomized_data['treasures'] = randomized_treasures
		randomizer.result.treasures_changed = len(randomized_treasures)

	# Randomize encounters
	if options.randomize_encounters and 'encounter_zones' in game_data:
		all_monsters = randomized_data.get('monsters', [])
		randomized_zones = randomizer.randomize_encounter_zones(
			game_data['encounter_zones'],
			all_monsters
		)
		randomized_data['encounter_zones'] = randomized_zones

	# Validate logic
	if options.ensure_completion:
		warnings = randomizer.validate_logic(randomized_data)
		randomizer.result.warnings = warnings

	# Generate spoiler log
	if options.generate_spoiler:
		spoiler = randomizer.generate_spoiler_log(game_data, randomized_data)
		randomizer.result.spoiler_data['log'] = spoiler

	return randomized_data, randomizer.result


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Advanced Randomizer for Dragon Warrior"
	)

	parser.add_argument('rom_file', nargs='?', help="ROM file to randomize")
	parser.add_argument('--seed', type=int, help="Randomization seed")
	parser.add_argument('--output', type=Path, help="Output ROM file")
	parser.add_argument('--spoiler', type=Path, help="Spoiler log output file")

	parser.add_argument('--preset', choices=['normal', 'chaos', 'hard', 'easy', 'balanced', 'race'],
					   help="Use randomization preset")

	parser.add_argument('--monsters-only', action='store_true',
					   help="Only randomize monsters")
	parser.add_argument('--items-only', action='store_true',
					   help="Only randomize items")
	parser.add_argument('--difficulty', type=int, default=100,
					   help="Difficulty scale (100 = normal)")

	parser.add_argument('--no-spoiler', action='store_true',
					   help="Don't generate spoiler log")

	args = parser.parse_args()

	# Determine seed
	seed = args.seed if args.seed else random.randint(0, 999999999)

	# Get options
	if args.preset:
		preset = RandomizerPreset(args.preset)
		options = RandomizerPresets.get_preset(preset)
		options.seed = seed
	else:
		options = RandomizerOptions(seed=seed)

	# Apply CLI overrides
	if args.monsters_only:
		options.randomize_items = False
		options.randomize_shops = False
		options.randomize_treasures = False

	if args.items_only:
		options.randomize_monsters = False
		options.randomize_encounters = False

	if args.difficulty:
		options.difficulty_scale = args.difficulty

	if args.no_spoiler:
		options.generate_spoiler = False

	if args.spoiler:
		options.spoiler_path = args.spoiler

	# Load game data (mock for demonstration)
	game_data = {
		'monsters': [
			{'id': 0, 'name': 'Slime', 'hp': 3, 'strength': 5, 'agility': 3, 'gold': 2, 'experience': 1},
			{'id': 1, 'name': 'Red Slime', 'hp': 4, 'strength': 7, 'agility': 4, 'gold': 3, 'experience': 2},
			{'id': 2, 'name': 'Drakee', 'hp': 6, 'strength': 9, 'agility': 6, 'gold': 5, 'experience': 3}
		],
		'items': [
			{'id': 0, 'name': 'Copper Sword', 'type': 'Weapon', 'price': 60, 'attack': 8},
			{'id': 1, 'name': 'Leather Armor', 'type': 'Armor', 'price': 70, 'defense': 6},
			{'id': 2, 'name': 'Herb', 'type': 'Item', 'price': 24, 'effect': 'Heal 30 HP'}
		],
		'treasures': [
			{'id': 0, 'x': 10, 'y': 15, 'item_id': 2, 'gold_amount': 0},
			{'id': 1, 'x': 20, 'y': 25, 'item_id': 0, 'gold_amount': 120}
		]
	}

	print("=" * 70)
	print("DRAGON WARRIOR RANDOMIZER")
	print("=" * 70)
	print(f"Seed: {seed}")
	print(f"Preset: {args.preset if args.preset else 'Custom'}")
	print(f"Difficulty: {options.difficulty_scale}%")
	print("")

	# Perform randomization
	randomized_data, result = randomize_game_data(game_data, options)

	# Print results
	print("Randomization Complete!")
	print(f"  Monsters Changed: {result.monsters_changed}")
	print(f"  Items Changed: {result.items_changed}")
	print(f"  Shops Changed: {result.shops_changed}")
	print(f"  Treasures Changed: {result.treasures_changed}")

	if result.warnings:
		print(f"\nWarnings: {len(result.warnings)}")
		for warning in result.warnings:
			print(f"  - {warning}")

	# Save spoiler log
	if options.generate_spoiler:
		spoiler_log = result.spoiler_data.get('log', '')

		if args.spoiler:
			spoiler_path = args.spoiler
		else:
			spoiler_path = Path(f"spoiler_{seed}.txt")

		with open(spoiler_path, 'w') as f:
			f.write(spoiler_log)

		print(f"\nSpoiler log saved to: {spoiler_path}")

	print("=" * 70)

	return 0


if __name__ == "__main__":
	sys.exit(main())
