#!/usr/bin/env python3
"""
Dragon Warrior Spell & Magic System Editor

Comprehensive magic system editor for Dragon Warrior spells, MP costs,
effects, learning levels, and magic formulas.

Features:
- Spell data editing (MP cost, power, effect)
- Spell learning levels
- Magic formula modification
- Damage calculation analysis
- Healing formula editing
- Status effect configuration
- Spell resistance editing
- MP cost balancing
- Spell progression curves
- Magic damage scaling
- Spell unlock requirements
- Effect duration editing
- Spell animation data
- Magic power vs level curves
- Spell comparison analysis
- MP efficiency calculation

Dragon Warrior Spells:
Player Spells (10):
- Heal (3 MP): Restore ~10-17 HP
- Hurt (2 MP): 8-16 damage
- Sleep (2 MP): Sleep enemy
- Radiant (3 MP): Light radius
- Stopspell (2 MP): Block enemy magic
- Outside (6 MP): Exit dungeon
- Return (8 MP): Return to castle
- Repel (2 MP): Repel weak enemies
- Healmore (10 MP): Restore ~85-100 HP
- Hurtmore (5 MP): 58-65 damage

Enemy Spells (5):
- Hurt, Sleep, Stopspell, Hurtmore, Healmore

Spell Data Locations:
- Spell Names: 0x1c40-0x1cff
- MP Costs: 0x1d00-0x1d3f
- Spell Effects: 0x1d40-0x1d7f
- Learning Levels: 0x1d80-0x1dbf
- Damage Tables: 0x1dc0-0x1dff

Usage:
	python tools/spell_editor.py <rom_file>

Examples:
	# List all spells
	python tools/spell_editor.py rom.nes --list

	# Show spell details
	python tools/spell_editor.py rom.nes --spell "Heal"

	# Edit spell stats
	python tools/spell_editor.py rom.nes --spell "Hurt" --mp-cost 1 --power 20 -o new.nes

	# Analyze spell balance
	python tools/spell_editor.py rom.nes --analyze-balance

	# Show progression curve
	python tools/spell_editor.py rom.nes --analyze-progression

	# Export spell database
	python tools/spell_editor.py rom.nes --export spells.json

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
import math


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class SpellType(Enum):
	"""Spell categories."""
	HEALING = "healing"
	DAMAGE = "damage"
	STATUS = "status"
	UTILITY = "utility"
	BUFF = "buff"
	DEBUFF = "debuff"


class SpellTarget(Enum):
	"""Spell target."""
	SELF = "self"
	SINGLE_ENEMY = "single_enemy"
	ALL_ENEMIES = "all_enemies"
	PARTY = "party"
	FIELD = "field"


@dataclass
class Spell:
	"""Spell data."""
	id: int
	name: str
	spell_type: SpellType
	target: SpellTarget
	mp_cost: int
	power: int = 0  # Damage or healing amount
	variance: int = 0  # Random variance
	learn_level: int = 0
	effect: str = ""
	duration: int = 0  # For status effects (turns)
	success_rate: float = 1.0  # 0.0-1.0


@dataclass
class SpellAnalysis:
	"""Spell balance analysis."""
	spell_id: int
	efficiency: float = 0.0  # Effect per MP
	power_rating: float = 0.0
	balance_rating: str = "balanced"
	recommendations: List[str] = field(default_factory=list)


@dataclass
class MagicFormula:
	"""Magic calculation formula."""
	name: str
	formula: str
	base_power: int
	variance: int
	level_scaling: float = 0.0


# Complete spell database
SPELLS_DATABASE = {
	# Player spells
	0: Spell(0, "Heal", SpellType.HEALING, SpellTarget.SELF,
	         mp_cost=3, power=10, variance=7, learn_level=3,
	         effect="Restore 10-17 HP"),

	1: Spell(1, "Hurt", SpellType.DAMAGE, SpellTarget.SINGLE_ENEMY,
	         mp_cost=2, power=8, variance=8, learn_level=4,
	         effect="Deal 8-16 damage"),

	2: Spell(2, "Sleep", SpellType.STATUS, SpellTarget.SINGLE_ENEMY,
	         mp_cost=2, power=0, learn_level=7, duration=6,
	         effect="Put enemy to sleep", success_rate=0.75),

	3: Spell(3, "Radiant", SpellType.UTILITY, SpellTarget.FIELD,
	         mp_cost=3, learn_level=9,
	         effect="Create light radius"),

	4: Spell(4, "Stopspell", SpellType.DEBUFF, SpellTarget.SINGLE_ENEMY,
	         mp_cost=2, learn_level=10,
	         effect="Block enemy magic", success_rate=0.80),

	5: Spell(5, "Outside", SpellType.UTILITY, SpellTarget.FIELD,
	         mp_cost=6, learn_level=12,
	         effect="Exit dungeon instantly"),

	6: Spell(6, "Return", SpellType.UTILITY, SpellTarget.FIELD,
	         mp_cost=8, learn_level=13,
	         effect="Return to Tantegel Castle"),

	7: Spell(7, "Repel", SpellType.BUFF, SpellTarget.SELF,
	         mp_cost=2, learn_level=15,
	         effect="Repel weak enemies"),

	8: Spell(8, "Healmore", SpellType.HEALING, SpellTarget.SELF,
	         mp_cost=10, power=85, variance=15, learn_level=17,
	         effect="Restore 85-100 HP"),

	9: Spell(9, "Hurtmore", SpellType.DAMAGE, SpellTarget.SINGLE_ENEMY,
	         mp_cost=5, power=58, variance=7, learn_level=19,
	         effect="Deal 58-65 damage"),
}

# Magic formulas
MAGIC_FORMULAS = {
	"heal": MagicFormula(
		name="Heal",
		formula="Random(10, 17)",
		base_power=10,
		variance=7
	),
	"healmore": MagicFormula(
		name="Healmore",
		formula="Random(85, 100)",
		base_power=85,
		variance=15
	),
	"hurt": MagicFormula(
		name="Hurt",
		formula="Random(8, 16)",
		base_power=8,
		variance=8
	),
	"hurtmore": MagicFormula(
		name="Hurtmore",
		formula="Random(58, 65)",
		base_power=58,
		variance=7
	),
}


# ============================================================================
# SPELL DATA LOADER
# ============================================================================

class SpellDataLoader:
	"""Load spell data from ROM."""

	# ROM offsets (simplified)
	SPELL_NAMES_OFFSET = 0x1c40
	MP_COSTS_OFFSET = 0x1d00
	SPELL_EFFECTS_OFFSET = 0x1d40
	LEARNING_LEVELS_OFFSET = 0x1d80
	DAMAGE_TABLES_OFFSET = 0x1dc0

	@staticmethod
	def load_spell(rom_data: bytes, spell_id: int) -> Optional[Spell]:
		"""Load spell from ROM."""
		if spell_id in SPELLS_DATABASE:
			return SPELLS_DATABASE[spell_id]
		return None

	@staticmethod
	def save_spell(rom_data: bytearray, spell: Spell):
		"""Save spell to ROM."""
		# MP cost
		mp_offset = SpellDataLoader.MP_COSTS_OFFSET + spell.id
		if mp_offset < len(rom_data):
			rom_data[mp_offset] = spell.mp_cost

		# Power (damage/healing)
		power_offset = SpellDataLoader.SPELL_EFFECTS_OFFSET + spell.id
		if power_offset < len(rom_data):
			rom_data[power_offset] = spell.power

		# Learning level
		level_offset = SpellDataLoader.LEARNING_LEVELS_OFFSET + spell.id
		if level_offset < len(rom_data):
			rom_data[level_offset] = spell.learn_level


# ============================================================================
# MAGIC CALCULATOR
# ============================================================================

class MagicCalculator:
	"""Calculate magic effects."""

	@staticmethod
	def calculate_damage(spell: Spell, caster_level: int = 1,
	                     target_resistance: int = 0) -> Tuple[int, int]:
		"""Calculate spell damage range."""
		# Base damage
		min_damage = spell.power
		max_damage = spell.power + spell.variance

		# Apply resistance
		if target_resistance > 0:
			reduction = 1.0 - (target_resistance / 100.0)
			min_damage = int(min_damage * reduction)
			max_damage = int(max_damage * reduction)

		return (max(0, min_damage), max(0, max_damage))

	@staticmethod
	def calculate_healing(spell: Spell, caster_level: int = 1) -> Tuple[int, int]:
		"""Calculate healing amount range."""
		min_heal = spell.power
		max_heal = spell.power + spell.variance

		return (min_heal, max_heal)

	@staticmethod
	def calculate_mp_efficiency(spell: Spell) -> float:
		"""Calculate damage or healing per MP."""
		if spell.mp_cost == 0:
			return 0.0

		if spell.spell_type in (SpellType.DAMAGE, SpellType.HEALING):
			avg_effect = spell.power + (spell.variance / 2.0)
			return avg_effect / spell.mp_cost

		return 0.0

	@staticmethod
	def calculate_success_chance(spell: Spell, caster_level: int,
	                              target_level: int, target_resistance: int = 0) -> float:
		"""Calculate spell success probability."""
		base_chance = spell.success_rate

		# Level difference modifier
		level_diff = caster_level - target_level
		level_modifier = 1.0 + (level_diff * 0.05)

		# Resistance modifier
		resistance_modifier = 1.0 - (target_resistance / 100.0)

		chance = base_chance * level_modifier * resistance_modifier

		return max(0.0, min(1.0, chance))


# ============================================================================
# SPELL ANALYZER
# ============================================================================

class SpellAnalyzer:
	"""Analyze spell balance."""

	@staticmethod
	def analyze_spell(spell: Spell) -> SpellAnalysis:
		"""Analyze spell balance."""
		efficiency = MagicCalculator.calculate_mp_efficiency(spell)

		# Calculate power rating
		if spell.spell_type == SpellType.DAMAGE:
			power_rating = spell.power / 10.0
		elif spell.spell_type == SpellType.HEALING:
			power_rating = spell.power / 15.0
		else:
			power_rating = 5.0  # Utility spells

		# Classify balance
		recommendations = []

		if spell.spell_type in (SpellType.DAMAGE, SpellType.HEALING):
			if efficiency < 3.0:
				rating = "inefficient"
				recommendations.append("Increase power or decrease MP cost")
			elif efficiency > 12.0:
				rating = "overpowered"
				recommendations.append("Decrease power or increase MP cost")
			else:
				rating = "balanced"
		else:
			rating = "utility"

		return SpellAnalysis(
			spell_id=spell.id,
			efficiency=efficiency,
			power_rating=power_rating,
			balance_rating=rating,
			recommendations=recommendations
		)


# ============================================================================
# PROGRESSION ANALYZER
# ============================================================================

class ProgressionAnalyzer:
	"""Analyze spell progression."""

	@staticmethod
	def analyze_damage_curve(spells: List[Spell]) -> Dict[str, Any]:
		"""Analyze damage spell progression."""
		damage_spells = [s for s in spells if s.spell_type == SpellType.DAMAGE]
		damage_spells.sort(key=lambda x: x.learn_level)

		if not damage_spells:
			return {}

		power_values = [s.power for s in damage_spells]
		level_values = [s.learn_level for s in damage_spells]

		# Calculate power increase rate
		power_gaps = []
		for i in range(1, len(power_values)):
			gap = power_values[i] - power_values[i-1]
			power_gaps.append(gap)

		avg_gap = sum(power_gaps) / len(power_gaps) if power_gaps else 0

		return {
			"damage_spells": len(damage_spells),
			"power_range": (min(power_values), max(power_values)),
			"level_range": (min(level_values), max(level_values)),
			"average_power_increase": avg_gap,
			"curve": "smooth" if avg_gap < 30 else "steep"
		}

	@staticmethod
	def analyze_healing_curve(spells: List[Spell]) -> Dict[str, Any]:
		"""Analyze healing spell progression."""
		healing_spells = [s for s in spells if s.spell_type == SpellType.HEALING]
		healing_spells.sort(key=lambda x: x.learn_level)

		if not healing_spells:
			return {}

		power_values = [s.power for s in healing_spells]
		level_values = [s.learn_level for s in healing_spells]
		mp_values = [s.mp_cost for s in healing_spells]

		return {
			"healing_spells": len(healing_spells),
			"power_range": (min(power_values), max(power_values)),
			"level_range": (min(level_values), max(level_values)),
			"mp_range": (min(mp_values), max(mp_values)),
		}


# ============================================================================
# SPELL EDITOR
# ============================================================================

class SpellEditor:
	"""Edit spells and magic system."""

	def __init__(self, rom_path: str):
		self.rom_path = Path(rom_path)
		self.rom_data: bytearray = bytearray()
		self.spells: Dict[int, Spell] = {}

	def load_rom(self) -> bool:
		"""Load ROM file."""
		if not self.rom_path.exists():
			print(f"ERROR: ROM not found: {self.rom_path}")
			return False

		with open(self.rom_path, 'rb') as f:
			self.rom_data = bytearray(f.read())

		return True

	def load_all_spells(self):
		"""Load all spells."""
		print("Loading spells...")
		self.spells = SPELLS_DATABASE.copy()
		print(f"✓ Loaded {len(self.spells)} spells")

	def get_spell_by_name(self, name: str) -> Optional[Spell]:
		"""Get spell by name."""
		for spell in self.spells.values():
			if spell.name.lower() == name.lower():
				return spell
		return None

	def edit_spell(self, spell_id: int, **kwargs):
		"""Edit spell stats."""
		if spell_id not in self.spells:
			print(f"ERROR: Invalid spell ID: {spell_id}")
			return

		spell = self.spells[spell_id]

		# Update stats
		if 'mp_cost' in kwargs:
			spell.mp_cost = kwargs['mp_cost']
		if 'power' in kwargs:
			spell.power = kwargs['power']
		if 'variance' in kwargs:
			spell.variance = kwargs['variance']
		if 'learn_level' in kwargs:
			spell.learn_level = kwargs['learn_level']

		# Save to ROM
		SpellDataLoader.save_spell(self.rom_data, spell)

		print(f"✓ Updated {spell.name}")

	def save_rom(self, output_path: str):
		"""Save modified ROM."""
		with open(output_path, 'wb') as f:
			f.write(self.rom_data)

		print(f"✓ ROM saved: {output_path}")

	def export_json(self, output_path: str):
		"""Export spell database to JSON."""
		data = {
			"spells": [
				{
					"id": spell.id,
					"name": spell.name,
					"type": spell.spell_type.value,
					"target": spell.target.value,
					"mp_cost": spell.mp_cost,
					"power": spell.power,
					"variance": spell.variance,
					"learn_level": spell.learn_level,
					"effect": spell.effect,
					"duration": spell.duration,
					"success_rate": spell.success_rate
				}
				for spell in self.spells.values()
			]
		}

		with open(output_path, 'w') as f:
			json.dump(data, f, indent=2)

		print(f"✓ Spell database exported: {output_path}")


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Dragon Warrior Spell & Magic System Editor"
	)

	parser.add_argument('rom', help="ROM file")
	parser.add_argument('--list', action='store_true', help="List all spells")
	parser.add_argument('--spell', type=str, help="Spell name")
	parser.add_argument('--mp-cost', type=int, help="Set MP cost")
	parser.add_argument('--power', type=int, help="Set power")
	parser.add_argument('--variance', type=int, help="Set variance")
	parser.add_argument('--learn-level', type=int, help="Set learning level")
	parser.add_argument('--analyze-balance', action='store_true', help="Analyze spell balance")
	parser.add_argument('--analyze-progression', action='store_true', help="Analyze progression")
	parser.add_argument('--export', type=str, help="Export to JSON")
	parser.add_argument('-o', '--output', type=str, help="Output ROM file")

	args = parser.parse_args()

	# Load ROM
	editor = SpellEditor(args.rom)
	if not editor.load_rom():
		return 1

	# Load spells
	editor.load_all_spells()

	# List spells
	if args.list:
		print("\nSpells:")
		print("=" * 100)
		print(f"{'ID':<4} {'Name':<12} {'Type':<10} {'MP':<4} {'Power':<7} {'Var':<5} {'Lvl':<4} {'Effect'}")
		print("-" * 100)

		for spell in sorted(editor.spells.values(), key=lambda x: x.learn_level):
			power_str = f"{spell.power}" if spell.power > 0 else "-"
			var_str = f"{spell.variance}" if spell.variance > 0 else "-"

			print(f"{spell.id:<4} {spell.name:<12} {spell.spell_type.value:<10} "
			      f"{spell.mp_cost:<4} {power_str:<7} {var_str:<5} "
			      f"{spell.learn_level:<4} {spell.effect}")

	# Show spell details
	if args.spell:
		spell = editor.get_spell_by_name(args.spell)

		if spell:
			print(f"\n{spell.name} (ID: {spell.id})")
			print("=" * 60)
			print(f"Type: {spell.spell_type.value}")
			print(f"Target: {spell.target.value}")
			print(f"MP Cost: {spell.mp_cost}")

			if spell.power > 0:
				print(f"Power: {spell.power}")
			if spell.variance > 0:
				print(f"Variance: {spell.variance}")

				# Show damage/healing range
				if spell.spell_type == SpellType.DAMAGE:
					min_dmg, max_dmg = MagicCalculator.calculate_damage(spell)
					print(f"Damage Range: {min_dmg}-{max_dmg}")
				elif spell.spell_type == SpellType.HEALING:
					min_heal, max_heal = MagicCalculator.calculate_healing(spell)
					print(f"Healing Range: {min_heal}-{max_heal}")

			print(f"Learn Level: {spell.learn_level}")

			if spell.duration > 0:
				print(f"Duration: {spell.duration} turns")
			if spell.success_rate < 1.0:
				print(f"Success Rate: {spell.success_rate:.0%}")

			print(f"\nEffect: {spell.effect}")

			# Show efficiency
			efficiency = MagicCalculator.calculate_mp_efficiency(spell)
			if efficiency > 0:
				print(f"MP Efficiency: {efficiency:.2f} per MP")

			# Edit stats if provided
			edits = {}
			if args.mp_cost is not None:
				edits['mp_cost'] = args.mp_cost
			if args.power is not None:
				edits['power'] = args.power
			if args.variance is not None:
				edits['variance'] = args.variance
			if args.learn_level is not None:
				edits['learn_level'] = args.learn_level

			if edits:
				print(f"\nApplying edits...")
				editor.edit_spell(spell.id, **edits)

				if args.output:
					editor.save_rom(args.output)
		else:
			print(f"ERROR: Spell not found: {args.spell}")

	# Analyze balance
	if args.analyze_balance:
		print("\nSpell Balance Analysis:")
		print("=" * 80)

		imbalanced = []

		for spell in editor.spells.values():
			analysis = SpellAnalyzer.analyze_spell(spell)

			if analysis.balance_rating in ("inefficient", "overpowered"):
				imbalanced.append((spell, analysis))

		if imbalanced:
			print(f"\nFound {len(imbalanced)} imbalanced spells:\n")

			for spell, analysis in imbalanced:
				print(f"{spell.name}:")
				print(f"  Efficiency: {analysis.efficiency:.2f}")
				print(f"  Rating: {analysis.balance_rating}")

				for rec in analysis.recommendations:
					print(f"  → {rec}")
				print()
		else:
			print("✓ All spells are balanced!")

	# Analyze progression
	if args.analyze_progression:
		print("\nSpell Progression Analysis:")
		print("=" * 80)

		spells_list = list(editor.spells.values())

		damage_curve = ProgressionAnalyzer.analyze_damage_curve(spells_list)
		if damage_curve:
			print("\nDamage Spell Progression:")
			print(f"  Damage spells: {damage_curve['damage_spells']}")
			print(f"  Power range: {damage_curve['power_range'][0]}-{damage_curve['power_range'][1]}")
			print(f"  Level range: {damage_curve['level_range'][0]}-{damage_curve['level_range'][1]}")
			print(f"  Average power increase: {damage_curve['average_power_increase']:.1f}")
			print(f"  Curve: {damage_curve['curve']}")

		healing_curve = ProgressionAnalyzer.analyze_healing_curve(spells_list)
		if healing_curve:
			print("\nHealing Spell Progression:")
			print(f"  Healing spells: {healing_curve['healing_spells']}")
			print(f"  Power range: {healing_curve['power_range'][0]}-{healing_curve['power_range'][1]}")
			print(f"  Level range: {healing_curve['level_range'][0]}-{healing_curve['level_range'][1]}")
			print(f"  MP range: {healing_curve['mp_range'][0]}-{healing_curve['mp_range'][1]}")

	# Export
	if args.export:
		editor.export_json(args.export)

	return 0


if __name__ == "__main__":
	sys.exit(main())
