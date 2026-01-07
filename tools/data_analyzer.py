#!/usr/bin/env python3
"""
Dragon Warrior Data Analysis Tool

Advanced data mining and statistical analysis for Dragon Warrior ROMs.
Features:
- Enemy encounter rate analysis
- Damage formula validation and testing
- Experience curve analysis and balancing
- Gold economy simulation
- Drop rate calculations
- Stat distribution analysis
- Spell effectiveness metrics
- Item value analysis
- Progression pacing metrics
- Difficulty curve visualization

Analysis Categories:
- Battle System: Damage formulas, hit rates, critical hits
- Economy: Gold gains, shop prices, progression costs
- Progression: XP requirements, level pacing, stat growth
- Items: Equipment effectiveness, consumable value
- Enemies: Encounter rates, difficulty ratings, reward efficiency
- Spells: MP efficiency, damage output, utility value

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
import json
import math
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from enum import IntEnum
from collections import defaultdict, Counter


@dataclass
class BattleSimulation:
	"""Battle simulation results."""
	player_level: int
	enemy_name: str
	total_battles: int
	player_wins: int
	enemy_wins: int
	avg_turns: float
	avg_damage_dealt: float
	avg_damage_taken: float
	avg_hp_remaining: float

	def win_rate(self) -> float:
		"""Calculate win rate."""
		return (self.player_wins / self.total_battles * 100) if self.total_battles > 0 else 0

	def to_dict(self) -> dict:
		return {
			'player_level': self.player_level,
			'enemy': self.enemy_name,
			'battles': self.total_battles,
			'wins': self.player_wins,
			'losses': self.enemy_wins,
			'win_rate': f"{self.win_rate():.1f}%",
			'avg_turns': f"{self.avg_turns:.1f}",
			'avg_damage_dealt': f"{self.avg_damage_dealt:.1f}",
			'avg_damage_taken': f"{self.avg_damage_taken:.1f}",
			'avg_hp_remaining': f"{self.avg_hp_remaining:.1f}"
		}


@dataclass
class EconomyMetrics:
	"""Economy analysis metrics."""
	level: int
	gold_per_battle: float
	battles_for_equipment: Dict[str, int]
	total_equipment_cost: int
	recommended_gold: int

	def to_dict(self) -> dict:
		return {
			'level': self.level,
			'gold_per_battle': f"{self.gold_per_battle:.1f}",
			'battles_for_equipment': self.battles_for_equipment,
			'total_cost': self.total_equipment_cost,
			'recommended_gold': self.recommended_gold
		}


@dataclass
class ProgressionMetrics:
	"""Progression analysis metrics."""
	level: int
	exp_required: int
	exp_from_prev: int
	battles_needed: int
	estimated_time_minutes: int
	stat_growth: Dict[str, int]

	def to_dict(self) -> dict:
		return {
			'level': self.level,
			'exp_required': self.exp_required,
			'exp_from_previous': self.exp_from_prev,
			'battles_needed': self.battles_needed,
			'estimated_time': f"{self.estimated_time_minutes} min",
			'stat_growth': self.stat_growth
		}


# Dragon Warrior data
HP_TABLE = [15, 22, 24, 31, 35, 38, 40, 46, 50, 54, 62, 63, 70, 78, 86, 100, 115, 130, 138, 146, 155, 160, 165, 170, 174, 180, 189, 195, 220, 240]
MP_TABLE = [0, 0, 5, 16, 20, 24, 26, 29, 36, 40, 50, 58, 64, 70, 72, 95, 100, 115, 128, 135, 146, 155, 161, 161, 168, 175, 180, 190, 200, 255]
STR_TABLE = [4, 5, 7, 7, 12, 16, 18, 22, 30, 35, 40, 48, 52, 60, 68, 72, 72, 85, 87, 90, 92, 95, 97, 99, 103, 113, 117, 125, 130, 140]
AGI_TABLE = [4, 4, 6, 8, 10, 10, 17, 20, 22, 31, 35, 40, 48, 52, 55, 64, 70, 78, 84, 90, 95, 100, 103, 105, 110, 115, 120, 130, 135, 140]
EXP_TABLE = [0, 7, 23, 47, 110, 220, 450, 800, 1300, 2000, 2900, 4000, 5500, 7500, 10000, 13000, 16000, 19000, 22000, 26000, 30000, 34000, 38000, 42000, 46000, 50000, 54000, 58000, 62000, 65535]


@dataclass
class Enemy:
	"""Enemy data for analysis."""
	name: str
	hp: int
	attack: int
	defense: int
	agility: int
	gold: int
	exp: int
	encounter_weight: int = 1
	zone_level: int = 1  # What level zone they appear in

	def avg_gold_per_kill(self) -> float:
		"""Average gold per kill."""
		return float(self.gold)

	def avg_exp_per_kill(self) -> float:
		"""Average exp per kill."""
		return float(self.exp)

	def efficiency_score(self) -> float:
		"""Calculate enemy efficiency (exp + gold per difficulty)."""
		difficulty = (self.hp + self.attack + self.defense) / 3
		reward = self.exp + self.gold * 0.1  # Weight exp higher than gold
		return reward / max(difficulty, 1)


# Enemy database
ENEMIES = [
	Enemy("Slime", 3, 5, 0, 3, 2, 1, 10, 1),
	Enemy("Red Slime", 4, 7, 0, 3, 3, 2, 8, 1),
	Enemy("Drakee", 6, 9, 2, 6, 5, 3, 7, 2),
	Enemy("Ghost", 7, 11, 0, 8, 8, 4, 6, 2),
	Enemy("Magician", 13, 11, 4, 12, 16, 8, 5, 3),
	Enemy("Magidrakee", 15, 14, 2, 14, 20, 11, 5, 3),
	Enemy("Scorpion", 20, 18, 6, 16, 25, 16, 6, 4),
	Enemy("Druin", 22, 20, 4, 18, 30, 20, 5, 4),
	Enemy("Poltergeist", 23, 18, 0, 20, 32, 21, 4, 5),
	Enemy("Droll", 25, 22, 8, 18, 35, 25, 5, 5),
	Enemy("Skeleton", 30, 28, 10, 22, 50, 33, 6, 6),
	Enemy("Warlock", 30, 28, 12, 22, 50, 35, 5, 6),
	Enemy("Metal Scorpion", 22, 36, 20, 42, 6, 40, 2, 7),
	Enemy("Wolf", 40, 40, 14, 30, 60, 45, 7, 7),
	Enemy("Wraith", 36, 44, 16, 34, 70, 52, 5, 8),
	Enemy("Metal Slime", 4, 10, 30, 255, 6, 115, 1, 8),
	Enemy("Wolflord", 50, 56, 18, 40, 105, 70, 6, 9),
	Enemy("Druinlord", 47, 58, 16, 40, 110, 72, 6, 9),
	Enemy("Wyvern", 70, 64, 20, 48, 120, 85, 5, 10),
	Enemy("Golem", 153, 120, 60, 60, 10, 255, 1, 15),
	Enemy("Knight", 70, 78, 24, 64, 165, 105, 7, 11),
	Enemy("Demon Knight", 80, 84, 26, 70, 165, 120, 6, 12),
	Enemy("Werewolf", 86, 86, 28, 70, 155, 125, 6, 12),
	Enemy("Green Dragon", 75, 88, 22, 58, 160, 135, 5, 13),
	Enemy("Wizard", 80, 80, 30, 70, 185, 140, 5, 13),
	Enemy("Axe Knight", 90, 94, 32, 82, 165, 155, 6, 14),
	Enemy("Blue Dragon", 98, 98, 34, 84, 180, 150, 5, 14),
	Enemy("Red Dragon", 120, 120, 40, 90, 143, 174, 4, 15),
]


class BattleAnalyzer:
	"""Analyze battle system mechanics."""

	def __init__(self):
		self.rng = random.Random(42)  # Fixed seed for reproducibility

	def calculate_damage(self, attack: int, defense: int, variance: bool = True) -> int:
		"""Calculate damage using DW formula."""
		# Dragon Warrior damage formula: (Attack - Defense/2) with variance
		base_damage = attack - (defense // 2)

		if base_damage <= 0:
			return 0

		if variance:
			# Add random variance (±25%)
			variance_amount = int(base_damage * 0.25)
			damage = base_damage + self.rng.randint(-variance_amount, variance_amount)
		else:
			damage = base_damage

		return max(0, damage)

	def calculate_hit_chance(self, attacker_agi: int, defender_agi: int) -> float:
		"""Calculate hit chance based on agility."""
		# Simplified hit formula
		agi_diff = attacker_agi - defender_agi
		base_chance = 0.75  # 75% base hit rate

		# Adjust based on agility difference
		modifier = agi_diff * 0.01  # 1% per agility point

		hit_chance = base_chance + modifier
		return max(0.1, min(0.95, hit_chance))  # Clamp between 10% and 95%

	def simulate_battle(self, player_level: int, player_attack: int, player_defense: int,
	                     player_agi: int, player_hp: int, enemy: Enemy,
	                     num_simulations: int = 1000) -> BattleSimulation:
		"""Simulate battles between player and enemy."""
		player_wins = 0
		enemy_wins = 0
		total_turns = 0
		total_damage_dealt = 0
		total_damage_taken = 0
		total_hp_remaining = 0

		for _ in range(num_simulations):
			p_hp = player_hp
			e_hp = enemy.hp
			turns = 0
			damage_dealt = 0
			damage_taken = 0

			while p_hp > 0 and e_hp > 0:
				turns += 1

				# Player attacks
				if self.rng.random() < self.calculate_hit_chance(player_agi, enemy.agility):
					dmg = self.calculate_damage(player_attack, enemy.defense)
					e_hp -= dmg
					damage_dealt += dmg

				if e_hp <= 0:
					break

				# Enemy attacks
				if self.rng.random() < self.calculate_hit_chance(enemy.agility, player_agi):
					dmg = self.calculate_damage(enemy.attack, player_defense)
					p_hp -= dmg
					damage_taken += dmg

			# Record results
			total_turns += turns
			total_damage_dealt += damage_dealt
			total_damage_taken += damage_taken

			if p_hp > 0:
				player_wins += 1
				total_hp_remaining += p_hp
			else:
				enemy_wins += 1

		avg_hp_remaining = (total_hp_remaining / player_wins) if player_wins > 0 else 0

		return BattleSimulation(
			player_level=player_level,
			enemy_name=enemy.name,
			total_battles=num_simulations,
			player_wins=player_wins,
			enemy_wins=enemy_wins,
			avg_turns=total_turns / num_simulations,
			avg_damage_dealt=total_damage_dealt / num_simulations,
			avg_damage_taken=total_damage_taken / num_simulations,
			avg_hp_remaining=avg_hp_remaining
		)

	def analyze_damage_formula(self) -> Dict:
		"""Analyze damage formula characteristics."""
		results = {
			'formula': 'Damage = Attack - (Defense / 2) ± 25%',
			'samples': []
		}

		# Test various attack/defense combinations
		test_cases = [
			(10, 0, "Low Attack, No Defense"),
			(20, 10, "Moderate Attack, Low Defense"),
			(50, 20, "High Attack, Moderate Defense"),
			(100, 50, "Very High Attack, High Defense"),
			(30, 60, "Attack < Defense"),
		]

		for attack, defense, description in test_cases:
			damages = [self.calculate_damage(attack, defense) for _ in range(100)]

			results['samples'].append({
				'description': description,
				'attack': attack,
				'defense': defense,
				'min_damage': min(damages),
				'max_damage': max(damages),
				'avg_damage': sum(damages) / len(damages)
			})

		return results


class EconomyAnalyzer:
	"""Analyze game economy and gold progression."""

	def __init__(self):
		self.equipment_costs = {
			# Weapons
			"Bamboo Pole": 10,
			"Club": 60,
			"Copper Sword": 180,
			"Hand Axe": 560,
			"Broad Sword": 1500,
			"Flame Sword": 9800,

			# Armor
			"Clothes": 20,
			"Leather Armor": 70,
			"Chain Mail": 300,
			"Half Plate": 1000,
			"Full Plate": 3000,
			"Magic Armor": 7700,

			# Shields
			"Small Shield": 90,
			"Large Shield": 800,
			"Silver Shield": 14800,

			# Items
			"Herb": 24,
			"Torch": 8,
			"Magic Key": 83,
			"Fairy Water": 38,
			"Wings": 70,
		}

		self.equipment_progression = {
			3: ["Club", "Leather Armor"],
			5: ["Copper Sword", "Chain Mail", "Small Shield"],
			7: ["Hand Axe"],
			10: ["Broad Sword", "Half Plate", "Large Shield"],
			13: ["Full Plate"],
			17: ["Flame Sword", "Silver Shield"],
			20: ["Magic Armor"],
		}

	def calculate_gold_per_hour(self, level: int, zone_enemies: List[Enemy]) -> float:
		"""Calculate expected gold per hour at a level."""
		# Assume 10 battles per hour (conservative)
		battles_per_hour = 10

		# Calculate average gold per battle
		total_gold = sum(e.gold * e.encounter_weight for e in zone_enemies)
		total_weight = sum(e.encounter_weight for e in zone_enemies)
		avg_gold = total_gold / total_weight

		return avg_gold * battles_per_hour

	def analyze_equipment_costs(self, level: int) -> EconomyMetrics:
		"""Analyze equipment costs for a level."""
		# Get recommended equipment
		recommended = []
		for lvl, items in sorted(self.equipment_progression.items()):
			if lvl <= level:
				recommended = items

		# Calculate total cost
		total_cost = sum(self.equipment_costs.get(item, 0) for item in recommended)

		# Estimate gold per battle at this level
		zone_enemies = [e for e in ENEMIES if abs(e.zone_level - level) <= 2]
		if not zone_enemies:
			zone_enemies = ENEMIES[:5]  # Default to early enemies

		avg_gold = sum(e.gold for e in zone_enemies) / len(zone_enemies)

		# Calculate battles needed for each item
		battles_needed = {}
		for item in recommended:
			cost = self.equipment_costs.get(item, 0)
			battles = int(math.ceil(cost / avg_gold)) if avg_gold > 0 else 0
			battles_needed[item] = battles

		return EconomyMetrics(
			level=level,
			gold_per_battle=avg_gold,
			battles_for_equipment=battles_needed,
			total_equipment_cost=total_cost,
			recommended_gold=int(total_cost * 1.2)  # 20% buffer for items
		)


class ProgressionAnalyzer:
	"""Analyze character progression and leveling."""

	def analyze_exp_curve(self) -> List[ProgressionMetrics]:
		"""Analyze experience requirements and growth."""
		metrics = []

		for level in range(2, 31):
			idx = level - 1

			exp_required = EXP_TABLE[idx]
			exp_from_prev = exp_required - EXP_TABLE[idx - 1]

			# Calculate stat growth
			stat_growth = {
				'hp': HP_TABLE[idx] - HP_TABLE[idx - 1] if idx > 0 else HP_TABLE[idx],
				'mp': MP_TABLE[idx] - MP_TABLE[idx - 1] if idx > 0 else MP_TABLE[idx],
				'str': STR_TABLE[idx] - STR_TABLE[idx - 1] if idx > 0 else STR_TABLE[idx],
				'agi': AGI_TABLE[idx] - AGI_TABLE[idx - 1] if idx > 0 else AGI_TABLE[idx],
			}

			# Estimate battles needed (assume avg 25 exp per battle)
			avg_exp = 25
			battles_needed = int(math.ceil(exp_from_prev / avg_exp))

			# Estimate time (assume 1 minute per battle)
			estimated_time = battles_needed

			metrics.append(ProgressionMetrics(
				level=level,
				exp_required=exp_required,
				exp_from_prev=exp_from_prev,
				battles_needed=battles_needed,
				estimated_time_minutes=estimated_time,
				stat_growth=stat_growth
			))

		return metrics

	def identify_grinding_hotspots(self) -> List[Dict]:
		"""Identify levels that require significant grinding."""
		hotspots = []

		progression = self.analyze_exp_curve()

		for i, metrics in enumerate(progression):
			if i == 0:
				continue

			prev_metrics = progression[i - 1]

			# Check if exp requirement jumped significantly
			if metrics.exp_from_prev > prev_metrics.exp_from_prev * 1.5:
				hotspots.append({
					'level': metrics.level,
					'exp_increase': metrics.exp_from_prev - prev_metrics.exp_from_prev,
					'battles_needed': metrics.battles_needed,
					'reason': 'Large exp requirement jump'
				})

		return hotspots


class DataAnalyzer:
	"""Main data analysis coordinator."""

	def __init__(self):
		self.battle_analyzer = BattleAnalyzer()
		self.economy_analyzer = EconomyAnalyzer()
		self.progression_analyzer = ProgressionAnalyzer()

	def generate_comprehensive_report(self, output_path: Path) -> None:
		"""Generate comprehensive analysis report."""
		lines = []

		lines.append("="*70)
		lines.append("DRAGON WARRIOR COMPREHENSIVE DATA ANALYSIS")
		lines.append("="*70)
		lines.append("")

		# Battle System Analysis
		lines.append("="*70)
		lines.append("BATTLE SYSTEM ANALYSIS")
		lines.append("="*70)
		lines.append("")

		damage_analysis = self.battle_analyzer.analyze_damage_formula()
		lines.append(f"Damage Formula: {damage_analysis['formula']}")
		lines.append("")

		for sample in damage_analysis['samples']:
			lines.append(f"{sample['description']}:")
			lines.append(f"  Attack: {sample['attack']}, Defense: {sample['defense']}")
			lines.append(f"  Min: {sample['min_damage']}, Max: {sample['max_damage']}, Avg: {sample['avg_damage']:.1f}")
			lines.append("")

		# Simulate battles at key levels
		lines.append("Battle Simulations (1000 trials each):")
		lines.append("-"*70)

		test_levels = [5, 10, 15, 20]
		for level in test_levels:
			idx = level - 1
			player_attack = STR_TABLE[idx] + 10  # Assume weapon bonus
			player_defense = AGI_TABLE[idx] // 2 + 15  # Assume armor bonus
			player_agi = AGI_TABLE[idx]
			player_hp = HP_TABLE[idx]

			# Test against appropriate enemies
			suitable_enemies = [e for e in ENEMIES if abs(e.zone_level - level) <= 2][:3]

			lines.append(f"\nLevel {level} (HP: {player_hp}, ATK: {player_attack}, DEF: {player_defense}, AGI: {player_agi}):")

			for enemy in suitable_enemies:
				sim = self.battle_analyzer.simulate_battle(
					level, player_attack, player_defense, player_agi, player_hp, enemy, 1000
				)
				lines.append(f"  vs {enemy.name}: {sim.win_rate():.1f}% win rate, "
				           f"{sim.avg_turns:.1f} turns, {sim.avg_hp_remaining:.0f} HP remaining")

		lines.append("")

		# Economy Analysis
		lines.append("="*70)
		lines.append("ECONOMY ANALYSIS")
		lines.append("="*70)
		lines.append("")

		for level in [3, 5, 7, 10, 13, 17, 20]:
			metrics = self.economy_analyzer.analyze_equipment_costs(level)
			lines.append(f"\nLevel {level}:")
			lines.append(f"  Gold per battle: {metrics.gold_per_battle:.1f}G")
			lines.append(f"  Total equipment cost: {metrics.total_equipment_cost}G")
			lines.append(f"  Recommended gold: {metrics.recommended_gold}G")

			if metrics.battles_for_equipment:
				lines.append("  Battles needed for equipment:")
				for item, battles in metrics.battles_for_equipment.items():
					lines.append(f"    {item}: {battles} battles")

		lines.append("")

		# Progression Analysis
		lines.append("="*70)
		lines.append("PROGRESSION ANALYSIS")
		lines.append("="*70)
		lines.append("")

		progression = self.progression_analyzer.analyze_exp_curve()

		lines.append("Experience Requirements by Level:")
		lines.append("-"*70)
		lines.append(f"{'Level':<6} {'Total EXP':<10} {'From Prev':<10} {'Battles':<8} {'Time':<10} {'HP':<4} {'MP':<4} {'STR':<4} {'AGI':<4}")
		lines.append("-"*70)

		for metrics in progression[::2]:  # Every other level
			lines.append(
				f"{metrics.level:<6} {metrics.exp_required:<10} {metrics.exp_from_prev:<10} "
				f"{metrics.battles_needed:<8} {metrics.estimated_time_minutes:<10} "
				f"+{metrics.stat_growth['hp']:<3} +{metrics.stat_growth['mp']:<3} "
				f"+{metrics.stat_growth['str']:<3} +{metrics.stat_growth['agi']:<3}"
			)

		lines.append("")

		# Grinding hotspots
		hotspots = self.progression_analyzer.identify_grinding_hotspots()
		if hotspots:
			lines.append("\nGrinding Hotspots (levels requiring significant effort):")
			for hotspot in hotspots:
				lines.append(f"  Level {hotspot['level']}: {hotspot['reason']}")
				lines.append(f"    Battles needed: {hotspot['battles_needed']}")

		lines.append("")

		# Enemy efficiency ratings
		lines.append("="*70)
		lines.append("ENEMY EFFICIENCY RATINGS")
		lines.append("="*70)
		lines.append("")

		lines.append(f"{'Enemy':<20} {'HP':<5} {'Gold':<6} {'EXP':<6} {'Efficiency':<10}")
		lines.append("-"*70)

		sorted_enemies = sorted(ENEMIES, key=lambda e: e.efficiency_score(), reverse=True)

		for enemy in sorted_enemies[:15]:  # Top 15
			lines.append(
				f"{enemy.name:<20} {enemy.hp:<5} {enemy.gold:<6} {enemy.exp:<6} {enemy.efficiency_score():<10.2f}"
			)

		lines.append("")
		lines.append("="*70)
		lines.append("END OF ANALYSIS")
		lines.append("="*70)

		# Write report
		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text('\n'.join(lines))

		print(f"✓ Generated analysis report: {output_path}")

	def export_json_analysis(self, output_path: Path) -> None:
		"""Export analysis data as JSON."""
		data = {
			'damage_formula': self.battle_analyzer.analyze_damage_formula(),
			'economy_metrics': [
				self.economy_analyzer.analyze_equipment_costs(level).to_dict()
				for level in [3, 5, 7, 10, 13, 17, 20]
			],
			'progression_metrics': [
				m.to_dict() for m in self.progression_analyzer.analyze_exp_curve()
			],
			'enemy_efficiency': [
				{
					'name': e.name,
					'efficiency': e.efficiency_score(),
					'gold': e.gold,
					'exp': e.exp
				}
				for e in sorted(ENEMIES, key=lambda e: e.efficiency_score(), reverse=True)
			]
		}

		output_path.parent.mkdir(parents=True, exist_ok=True)
		with output_path.open('w') as f:
			json.dump(data, f, indent='\t')

		print(f"✓ Exported JSON analysis: {output_path}")


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Dragon Warrior Data Analysis Tool'
	)

	parser.add_argument(
		'--report',
		type=Path,
		metavar='OUTPUT',
		help='Generate comprehensive text report'
	)

	parser.add_argument(
		'--json',
		type=Path,
		metavar='OUTPUT',
		help='Export analysis data as JSON'
	)

	parser.add_argument(
		'--battle',
		type=int,
		metavar='LEVEL',
		help='Run battle simulations for specific level'
	)

	parser.add_argument(
		'--economy',
		type=int,
		metavar='LEVEL',
		help='Analyze economy for specific level'
	)

	args = parser.parse_args()

	analyzer = DataAnalyzer()

	if args.report:
		analyzer.generate_comprehensive_report(args.report)

	if args.json:
		analyzer.export_json_analysis(args.json)

	if args.battle:
		level = args.battle
		idx = level - 1

		print(f"\nBattle Analysis for Level {level}")
		print("="*70)

		player_attack = STR_TABLE[idx] + 10
		player_defense = AGI_TABLE[idx] // 2 + 15
		player_agi = AGI_TABLE[idx]
		player_hp = HP_TABLE[idx]

		suitable_enemies = [e for e in ENEMIES if abs(e.zone_level - level) <= 3]

		for enemy in suitable_enemies:
			sim = analyzer.battle_analyzer.simulate_battle(
				level, player_attack, player_defense, player_agi, player_hp, enemy, 1000
			)
			print(f"\nvs {enemy.name}:")
			print(f"  Win rate: {sim.win_rate():.1f}%")
			print(f"  Avg turns: {sim.avg_turns:.1f}")
			print(f"  Avg damage dealt: {sim.avg_damage_dealt:.1f}")
			print(f"  Avg damage taken: {sim.avg_damage_taken:.1f}")
			print(f"  Avg HP remaining: {sim.avg_hp_remaining:.1f}")

	if args.economy:
		level = args.economy
		metrics = analyzer.economy_analyzer.analyze_equipment_costs(level)

		print(f"\nEconomy Analysis for Level {level}")
		print("="*70)
		print(f"Gold per battle: {metrics.gold_per_battle:.1f}G")
		print(f"Total equipment cost: {metrics.total_equipment_cost}G")
		print(f"Recommended gold: {metrics.recommended_gold}G")
		print("\nBattles needed for equipment:")
		for item, battles in metrics.battles_for_equipment.items():
			cost = analyzer.economy_analyzer.equipment_costs[item]
			print(f"  {item} ({cost}G): {battles} battles")

	if not any([args.report, args.json, args.battle, args.economy]):
		# Default: generate both reports
		output_dir = Path("output/analysis")
		analyzer.generate_comprehensive_report(output_dir / "data_analysis.txt")
		analyzer.export_json_analysis(output_dir / "analysis_data.json")

	return 0


if __name__ == '__main__':
	exit(main())
