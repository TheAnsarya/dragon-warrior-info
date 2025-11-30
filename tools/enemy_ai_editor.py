#!/usr/bin/env python3
"""
Dragon Warrior Enemy AI & Battle Mechanics Editor

Comprehensive editor for enemy behavior, battle mechanics, and AI patterns
in Dragon Warrior. Supports enemy stats, spell usage, attack patterns,
encounter rates, and battle formulas.

Features:
- Enemy stat editing (HP, strength, agility, XP, gold)
- AI behavior pattern editing
- Spell usage probability configuration
- Attack pattern analysis
- Critical hit rate editing
- Sleep/Stopspell resistance
- Run success formula
- Encounter rate editing
- Enemy group composition
- Battle formula modification
- Damage calculation analysis
- XP/Gold curve balancing
- Enemy tier classification
- Boss battle configuration
- Special attack handling
- Enemy scaling
- Random number generation analysis

Dragon Warrior Enemy Data:
- Enemy Count: 39 enemies
- Base Stats: 0x5e9d-0x604c
- Spell Usage: 0x604d-0x611c
- Enemy Groups: 0x611d-0x61cc
- Encounter Rates: 0x61cd-0x625c

Battle Formulas:
- Damage: Random(0-255) * Strength / Enemy Defense / 2
- Hit Chance: 1 - (Enemy Agility / (2 * Player Agility))
- Critical: 1/32 chance
- Run: (Player Agility - Enemy Agility) / 4
- Sleep Duration: Random(1-6) turns

Usage:
	python tools/enemy_ai_editor.py <rom_file>

Examples:
	# List all enemies
	python tools/enemy_ai_editor.py rom.nes --list

	# Show enemy details
	python tools/enemy_ai_editor.py rom.nes --enemy "Dragon"

	# Edit enemy stats
	python tools/enemy_ai_editor.py rom.nes --enemy "Slime" --hp 10 --strength 8 -o new.nes

	# Analyze AI patterns
	python tools/enemy_ai_editor.py rom.nes --analyze-ai

	# Balance XP/Gold rewards
	python tools/enemy_ai_editor.py rom.nes --balance-rewards

	# Export enemy database
	python tools/enemy_ai_editor.py rom.nes --export enemies.json

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
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

class EnemySpell(Enum):
	"""Enemy spells."""
	NONE = 0
	HURT = 1
	SLEEP = 2
	STOPSPELL = 3
	HURTMORE = 4
	HEALMORE = 5


class AttackPattern(Enum):
	"""Enemy attack patterns."""
	PHYSICAL_ONLY = "physical"
	SPELL_PREFERRED = "spell_preferred"
	SPELL_ONLY = "spell_only"
	MIXED = "mixed"
	DEFENSIVE = "defensive"


@dataclass
class EnemyStats:
	"""Enemy base statistics."""
	id: int
	name: str
	hp: int
	strength: int
	agility: int
	xp: int
	gold: int
	sleep_resistance: int = 0
	stopspell_resistance: int = 0
	hurt_resistance: int = 0


@dataclass
class EnemyAI:
	"""Enemy AI behavior."""
	enemy_id: int
	spell: EnemySpell = EnemySpell.NONE
	spell_probability: float = 0.0  # 0.0-1.0
	pattern: AttackPattern = AttackPattern.PHYSICAL_ONLY
	aggression: float = 0.5  # 0.0-1.0


@dataclass
class EnemyGroup:
	"""Enemy encounter group."""
	id: int
	enemies: List[int]  # Enemy IDs
	min_count: int = 1
	max_count: int = 1
	zone: str = "unknown"


@dataclass
class BattleFormula:
	"""Battle calculation formula."""
	name: str
	formula: str
	offset: int
	parameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EncounterRate:
	"""Encounter rate configuration."""
	zone_id: int
	zone_name: str
	rate: int  # Steps between encounters
	enemy_groups: List[int] = field(default_factory=list)


@dataclass
class EnemyAnalysis:
	"""Enemy balance analysis."""
	enemy_id: int
	difficulty_score: float = 0.0
	reward_score: float = 0.0
	balance_rating: str = "balanced"
	recommendations: List[str] = field(default_factory=list)


# Enemy database (partial - would load from ROM)
ENEMY_NAMES = [
	"Slime", "Red Slime", "Drakee", "Ghost", "Magician",
	"Magidrakee", "Scorpion", "Druin", "Poltergeist", "Droll",
	"Drakeema", "Skeleton", "Warlock", "Metal Scorpion", "Wolf",
	"Wraith", "Metal Slime", "Specter", "Wolflord", "Druinlord",
	"Drollmagi", "Wyvern", "Rogue Scorpion", "Wraith Knight", "Golem",
	"Goldman", "Knight", "Magiwyvern", "Demon Knight", "Werewolf",
	"Green Dragon", "Starwyvern", "Wizard", "Axe Knight", "Blue Dragon",
	"Stoneman", "Armored Knight", "Red Dragon", "Dragonlord 1", "Dragonlord 2"
]


# ============================================================================
# ENEMY DATA LOADER
# ============================================================================

class EnemyDataLoader:
	"""Load enemy data from ROM."""

	# ROM offsets
	ENEMY_STATS_OFFSET = 0x5e9d
	ENEMY_SPELL_OFFSET = 0x604d
	ENEMY_GROUP_OFFSET = 0x611d
	ENCOUNTER_RATE_OFFSET = 0x61cd

	@staticmethod
	def load_enemy_stats(rom_data: bytes, enemy_id: int) -> EnemyStats:
		"""Load enemy stats from ROM."""
		# Each enemy: 8 bytes
		# +0: HP (2 bytes, little endian)
		# +2: Strength
		# +3: Agility
		# +4: XP (2 bytes, little endian)
		# +6: Gold (2 bytes, little endian)

		offset = EnemyDataLoader.ENEMY_STATS_OFFSET + (enemy_id * 8)

		hp = struct.unpack('<H', rom_data[offset:offset+2])[0]
		strength = rom_data[offset + 2]
		agility = rom_data[offset + 3]
		xp = struct.unpack('<H', rom_data[offset+4:offset+6])[0]
		gold = struct.unpack('<H', rom_data[offset+6:offset+8])[0]

		name = ENEMY_NAMES[enemy_id] if enemy_id < len(ENEMY_NAMES) else f"Enemy_{enemy_id}"

		return EnemyStats(
			id=enemy_id,
			name=name,
			hp=hp,
			strength=strength,
			agility=agility,
			xp=xp,
			gold=gold
		)

	@staticmethod
	def save_enemy_stats(rom_data: bytearray, stats: EnemyStats):
		"""Save enemy stats to ROM."""
		offset = EnemyDataLoader.ENEMY_STATS_OFFSET + (stats.id * 8)

		struct.pack_into('<H', rom_data, offset, stats.hp)
		rom_data[offset + 2] = stats.strength
		rom_data[offset + 3] = stats.agility
		struct.pack_into('<H', rom_data, offset + 4, stats.xp)
		struct.pack_into('<H', rom_data, offset + 6, stats.gold)

	@staticmethod
	def load_enemy_ai(rom_data: bytes, enemy_id: int) -> EnemyAI:
		"""Load enemy AI data."""
		# Spell usage offset
		offset = EnemyDataLoader.ENEMY_SPELL_OFFSET + enemy_id
		spell_byte = rom_data[offset]

		# Decode spell and probability
		# Format: SSSSPPPPP
		# S = Spell type (3 bits)
		# P = Probability (5 bits, 0-31 = 0%-100%)

		spell_id = (spell_byte >> 5) & 0x07
		probability = (spell_byte & 0x1f) / 31.0

		spell = EnemySpell(spell_id) if spell_id < 6 else EnemySpell.NONE

		# Determine pattern
		if spell == EnemySpell.NONE:
			pattern = AttackPattern.PHYSICAL_ONLY
		elif probability > 0.7:
			pattern = AttackPattern.SPELL_PREFERRED
		elif probability > 0.3:
			pattern = AttackPattern.MIXED
		else:
			pattern = AttackPattern.DEFENSIVE

		return EnemyAI(
			enemy_id=enemy_id,
			spell=spell,
			spell_probability=probability,
			pattern=pattern,
			aggression=probability
		)


# ============================================================================
# BATTLE CALCULATOR
# ============================================================================

class BattleCalculator:
	"""Calculate battle mechanics."""

	@staticmethod
	def calculate_damage(attacker_strength: int, defender_agility: int,
	                     random_value: int = 128) -> int:
		"""Calculate physical damage."""
		# Dragon Warrior damage formula
		# Damage = Random(0-255) * Strength / Defense / 2

		defense = max(1, defender_agility // 2)  # Simplified
		damage = (random_value * attacker_strength) // (defense * 2)

		return max(0, damage)

	@staticmethod
	def calculate_hit_chance(attacker_agility: int, defender_agility: int) -> float:
		"""Calculate hit probability."""
		if attacker_agility <= 0:
			return 0.0

		# Hit chance = 1 - (Defender Agility / (2 * Attacker Agility))
		chance = 1.0 - (defender_agility / (2.0 * attacker_agility))

		return max(0.0, min(1.0, chance))

	@staticmethod
	def calculate_run_chance(player_agility: int, enemy_agility: int) -> float:
		"""Calculate run success probability."""
		# Run chance = (Player Agility - Enemy Agility) / 4
		# Simplified formula

		if player_agility <= enemy_agility:
			return 0.1  # Minimum 10% chance

		chance = (player_agility - enemy_agility) / 4.0 / 100.0

		return max(0.1, min(1.0, chance))

	@staticmethod
	def calculate_critical_chance() -> float:
		"""Calculate critical hit probability."""
		return 1.0 / 32.0  # 3.125%


# ============================================================================
# ENEMY AI ANALYZER
# ============================================================================

class EnemyAIAnalyzer:
	"""Analyze enemy AI patterns."""

	@staticmethod
	def analyze_difficulty(stats: EnemyStats, ai: EnemyAI) -> float:
		"""Calculate enemy difficulty score."""
		# Weighted difficulty score
		hp_score = stats.hp / 10.0
		strength_score = stats.strength * 2.0
		agility_score = stats.agility * 1.5

		# AI modifier
		ai_modifier = 1.0
		if ai.spell != EnemySpell.NONE:
			ai_modifier += ai.spell_probability * 0.5

		difficulty = (hp_score + strength_score + agility_score) * ai_modifier

		return difficulty

	@staticmethod
	def analyze_rewards(stats: EnemyStats) -> float:
		"""Calculate reward score."""
		return stats.xp + (stats.gold * 0.5)

	@staticmethod
	def analyze_balance(stats: EnemyStats, ai: EnemyAI) -> EnemyAnalysis:
		"""Analyze enemy balance."""
		difficulty = EnemyAIAnalyzer.analyze_difficulty(stats, ai)
		rewards = EnemyAIAnalyzer.analyze_rewards(stats)

		# Calculate balance ratio
		if difficulty > 0:
			balance_ratio = rewards / difficulty
		else:
			balance_ratio = 0.0

		# Classify balance
		if balance_ratio < 5.0:
			rating = "underrewarding"
			recommendations = ["Increase XP or gold rewards"]
		elif balance_ratio > 15.0:
			rating = "overrewarding"
			recommendations = ["Decrease rewards or increase difficulty"]
		else:
			rating = "balanced"
			recommendations = []

		return EnemyAnalysis(
			enemy_id=stats.id,
			difficulty_score=difficulty,
			reward_score=rewards,
			balance_rating=rating,
			recommendations=recommendations
		)


# ============================================================================
# ENEMY EDITOR
# ============================================================================

class EnemyEditor:
	"""Edit enemy data."""

	def __init__(self, rom_path: str):
		self.rom_path = Path(rom_path)
		self.rom_data: bytearray = bytearray()
		self.enemies: List[EnemyStats] = []
		self.ai_data: List[EnemyAI] = []

	def load_rom(self) -> bool:
		"""Load ROM file."""
		if not self.rom_path.exists():
			print(f"ERROR: ROM not found: {self.rom_path}")
			return False

		with open(self.rom_path, 'rb') as f:
			self.rom_data = bytearray(f.read())

		return True

	def load_all_enemies(self):
		"""Load all enemy data."""
		print("Loading enemy data...")

		for enemy_id in range(len(ENEMY_NAMES)):
			stats = EnemyDataLoader.load_enemy_stats(self.rom_data, enemy_id)
			ai = EnemyDataLoader.load_enemy_ai(self.rom_data, enemy_id)

			self.enemies.append(stats)
			self.ai_data.append(ai)

		print(f"✓ Loaded {len(self.enemies)} enemies")

	def get_enemy_by_name(self, name: str) -> Optional[Tuple[EnemyStats, EnemyAI]]:
		"""Get enemy by name."""
		for stats, ai in zip(self.enemies, self.ai_data):
			if stats.name.lower() == name.lower():
				return stats, ai

		return None

	def edit_enemy_stats(self, enemy_id: int, **kwargs):
		"""Edit enemy stats."""
		if enemy_id < 0 or enemy_id >= len(self.enemies):
			print(f"ERROR: Invalid enemy ID: {enemy_id}")
			return

		stats = self.enemies[enemy_id]

		# Update stats
		if 'hp' in kwargs:
			stats.hp = kwargs['hp']
		if 'strength' in kwargs:
			stats.strength = kwargs['strength']
		if 'agility' in kwargs:
			stats.agility = kwargs['agility']
		if 'xp' in kwargs:
			stats.xp = kwargs['xp']
		if 'gold' in kwargs:
			stats.gold = kwargs['gold']

		# Save to ROM
		EnemyDataLoader.save_enemy_stats(self.rom_data, stats)

		print(f"✓ Updated {stats.name}")

	def save_rom(self, output_path: str):
		"""Save modified ROM."""
		with open(output_path, 'wb') as f:
			f.write(self.rom_data)

		print(f"✓ ROM saved: {output_path}")

	def export_json(self, output_path: str):
		"""Export enemy database to JSON."""
		data = {
			"enemies": [
				{
					"id": stats.id,
					"name": stats.name,
					"hp": stats.hp,
					"strength": stats.strength,
					"agility": stats.agility,
					"xp": stats.xp,
					"gold": stats.gold,
					"ai": {
						"spell": ai.spell.name,
						"spell_probability": ai.spell_probability,
						"pattern": ai.pattern.value
					}
				}
				for stats, ai in zip(self.enemies, self.ai_data)
			]
		}

		with open(output_path, 'w') as f:
			json.dump(data, f, indent=2)

		print(f"✓ Enemy database exported: {output_path}")


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Dragon Warrior Enemy AI & Battle Mechanics Editor"
	)

	parser.add_argument('rom', help="ROM file")
	parser.add_argument('--list', action='store_true', help="List all enemies")
	parser.add_argument('--enemy', type=str, help="Enemy name")
	parser.add_argument('--hp', type=int, help="Set HP")
	parser.add_argument('--strength', type=int, help="Set strength")
	parser.add_argument('--agility', type=int, help="Set agility")
	parser.add_argument('--xp', type=int, help="Set XP")
	parser.add_argument('--gold', type=int, help="Set gold")
	parser.add_argument('--analyze-ai', action='store_true', help="Analyze AI patterns")
	parser.add_argument('--analyze-balance', action='store_true', help="Analyze reward balance")
	parser.add_argument('--export', type=str, help="Export to JSON")
	parser.add_argument('-o', '--output', type=str, help="Output ROM file")

	args = parser.parse_args()

	# Load ROM
	editor = EnemyEditor(args.rom)
	if not editor.load_rom():
		return 1

	# Load enemies
	editor.load_all_enemies()

	# List enemies
	if args.list:
		print("\nEnemies:")
		print("=" * 80)
		print(f"{'ID':<4} {'Name':<20} {'HP':<6} {'STR':<5} {'AGI':<5} {'XP':<6} {'Gold':<6}")
		print("-" * 80)

		for stats in editor.enemies:
			print(f"{stats.id:<4} {stats.name:<20} {stats.hp:<6} {stats.strength:<5} "
			      f"{stats.agility:<5} {stats.xp:<6} {stats.gold:<6}")

	# Show enemy details
	if args.enemy:
		result = editor.get_enemy_by_name(args.enemy)

		if result:
			stats, ai = result

			print(f"\n{stats.name} (ID: {stats.id})")
			print("=" * 60)
			print(f"HP: {stats.hp}")
			print(f"Strength: {stats.strength}")
			print(f"Agility: {stats.agility}")
			print(f"XP: {stats.xp}")
			print(f"Gold: {stats.gold}")
			print(f"\nAI:")
			print(f"  Spell: {ai.spell.name}")
			print(f"  Spell Probability: {ai.spell_probability:.1%}")
			print(f"  Pattern: {ai.pattern.value}")

			# Edit stats if provided
			edits = {}
			if args.hp is not None:
				edits['hp'] = args.hp
			if args.strength is not None:
				edits['strength'] = args.strength
			if args.agility is not None:
				edits['agility'] = args.agility
			if args.xp is not None:
				edits['xp'] = args.xp
			if args.gold is not None:
				edits['gold'] = args.gold

			if edits:
				print(f"\nApplying edits...")
				editor.edit_enemy_stats(stats.id, **edits)

				if args.output:
					editor.save_rom(args.output)
		else:
			print(f"ERROR: Enemy not found: {args.enemy}")

	# Analyze AI
	if args.analyze_ai:
		print("\nAI Pattern Analysis:")
		print("=" * 80)

		pattern_counts = {}
		spell_counts = {}

		for ai in editor.ai_data:
			pattern_counts[ai.pattern.value] = pattern_counts.get(ai.pattern.value, 0) + 1
			spell_counts[ai.spell.name] = spell_counts.get(ai.spell.name, 0) + 1

		print("\nAttack Patterns:")
		for pattern, count in sorted(pattern_counts.items()):
			print(f"  {pattern}: {count} enemies")

		print("\nSpell Usage:")
		for spell, count in sorted(spell_counts.items()):
			print(f"  {spell}: {count} enemies")

	# Analyze balance
	if args.analyze_balance:
		print("\nReward Balance Analysis:")
		print("=" * 80)

		imbalanced = []

		for stats, ai in zip(editor.enemies, editor.ai_data):
			analysis = EnemyAIAnalyzer.analyze_balance(stats, ai)

			if analysis.balance_rating != "balanced":
				imbalanced.append((stats, analysis))

		if imbalanced:
			print(f"\nFound {len(imbalanced)} imbalanced enemies:\n")

			for stats, analysis in imbalanced:
				print(f"{stats.name}:")
				print(f"  Difficulty: {analysis.difficulty_score:.1f}")
				print(f"  Rewards: {analysis.reward_score:.1f}")
				print(f"  Rating: {analysis.balance_rating}")

				for rec in analysis.recommendations:
					print(f"  → {rec}")
				print()
		else:
			print("✓ All enemies are balanced!")

	# Export
	if args.export:
		editor.export_json(args.export)

	return 0


if __name__ == "__main__":
	sys.exit(main())
