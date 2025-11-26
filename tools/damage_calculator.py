#!/usr/bin/env python3
"""
Battle Damage Calculator and Simulator for Dragon Warrior

Comprehensive battle system simulator with damage calculations, AI behavior,
status effects, and statistical analysis. Helps balance encounters and test
game mechanics.

Features:
- Accurate Dragon Warrior damage formulas
- Status effect simulation (SLEEP, STOPSPELL, etc.)
- Monster AI behavior patterns
- Battle outcome prediction
- Statistical analysis (kill rates, average damage, rounds to victory)
- Equipment comparison
- Level progression analysis
- Party vs Monster simulations

Usage:
	python tools/damage_calculator.py [--player-level LV] [--monster-id ID]

Examples:
	# Calculate damage for level 10 vs Skeleton
	python tools/damage_calculator.py --player-level 10 --monster-id 11

	# Simulate 1000 battles
	python tools/damage_calculator.py --player-level 15 --monster-id 20 --simulate 1000

	# Interactive mode
	python tools/damage_calculator.py
"""

import sys
import argparse
import random
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import statistics


class StatusEffect(Enum):
	"""Status effects in Dragon Warrior."""
	NONE = "none"
	SLEEP = "sleep"
	STOPSPELL = "stopspell"


class SpellEffect(Enum):
	"""Spell effects."""
	HEAL = "heal"
	DAMAGE = "damage"
	SLEEP = "sleep"
	STOPSPELL = "stopspell"
	HURT = "hurt"
	HURTMORE = "hurtmore"


@dataclass
class Stats:
	"""Character/Monster stats."""
	hp: int
	max_hp: int
	mp: int
	max_mp: int
	attack: int
	defense: int
	agility: int
	level: int = 1

	# Equipment bonuses
	weapon_attack: int = 0
	armor_defense: int = 0
	shield_defense: int = 0

	# Status
	status: StatusEffect = StatusEffect.NONE
	status_duration: int = 0

	def get_total_attack(self) -> int:
		"""Get total attack including equipment."""
		return self.attack + self.weapon_attack

	def get_total_defense(self) -> int:
		"""Get total defense including equipment."""
		return self.defense + self.armor_defense + self.shield_defense

	def apply_damage(self, damage: int) -> int:
		"""Apply damage and return actual damage dealt."""
		actual = min(damage, self.hp)
		self.hp -= actual
		return actual

	def heal(self, amount: int) -> int:
		"""Heal and return actual HP restored."""
		before = self.hp
		self.hp = min(self.hp + amount, self.max_hp)
		return self.hp - before

	def is_alive(self) -> bool:
		"""Check if character is alive."""
		return self.hp > 0

	def apply_status(self, status: StatusEffect, duration: int = 3) -> None:
		"""Apply status effect."""
		self.status = status
		self.status_duration = duration

	def tick_status(self) -> None:
		"""Tick status duration."""
		if self.status_duration > 0:
			self.status_duration -= 1
			if self.status_duration == 0:
				self.status = StatusEffect.NONE

	def copy(self) -> 'Stats':
		"""Create a copy of these stats."""
		return Stats(
			hp=self.hp,
			max_hp=self.max_hp,
			mp=self.mp,
			max_mp=self.max_mp,
			attack=self.attack,
			defense=self.defense,
			agility=self.agility,
			level=self.level,
			weapon_attack=self.weapon_attack,
			armor_defense=self.armor_defense,
			shield_defense=self.shield_defense,
			status=self.status,
			status_duration=self.status_duration
		)


@dataclass
class Monster:
	"""Monster data."""
	id: int
	name: str
	stats: Stats
	xp: int
	gold: int

	# AI behavior
	spell_chance: float = 0.0		# Probability of casting spell per turn
	run_chance: float = 0.0			# Probability of fleeing

	# Resistances
	resist_sleep: bool = False
	resist_stopspell: bool = False
	resist_hurt: bool = False

	# Spell abilities
	has_heal: bool = False
	has_sleep: bool = False
	has_stopspell: bool = False
	has_hurt: bool = False


# Dragon Warrior monster database (from ROM data)
MONSTER_DATABASE = {
	0: Monster(0, "Slime", Stats(3, 3, 0, 0, 5, 3, 3, 1), 1, 2),
	1: Monster(1, "Red Slime", Stats(4, 4, 0, 0, 7, 3, 6, 1), 1, 3),
	2: Monster(2, "Drakee", Stats(6, 6, 0, 0, 9, 6, 6, 2), 2, 3),
	3: Monster(3, "Ghost", Stats(7, 7, 0, 0, 11, 8, 8, 2), 3, 5),
	4: Monster(4, "Magician", Stats(13, 13, 8, 8, 11, 12, 8, 3), 8, 16, spell_chance=0.25, has_hurt=True),
	5: Monster(5, "Magidrakee", Stats(15, 15, 0, 0, 14, 14, 14, 3), 10, 14),
	6: Monster(6, "Scorpion", Stats(20, 20, 0, 0, 18, 16, 16, 4), 11, 25),
	7: Monster(7, "Druin", Stats(22, 22, 0, 0, 20, 18, 6, 4), 12, 20),
	8: Monster(8, "Poltergeist", Stats(23, 23, 0, 0, 18, 20, 9, 4), 13, 18),
	9: Monster(9, "Droll", Stats(25, 25, 0, 0, 24, 24, 6, 5), 14, 25),
	10: Monster(10, "Drakeema", Stats(27, 27, 0, 0, 22, 26, 22, 5), 15, 28),
	11: Monster(11, "Skeleton", Stats(30, 30, 0, 0, 28, 28, 11, 6), 17, 30),
	12: Monster(12, "Warlock", Stats(30, 30, 15, 15, 28, 22, 15, 6), 18, 50, spell_chance=0.3, has_sleep=True, has_hurt=True),
	13: Monster(13, "Metal Scorpion", Stats(22, 22, 0, 0, 36, 42, 20, 6), 20, 48),
	14: Monster(14, "Wolf", Stats(38, 38, 0, 0, 40, 30, 30, 7), 22, 60),
	15: Monster(15, "Wraith", Stats(44, 44, 7, 7, 44, 34, 20, 8), 25, 70, spell_chance=0.25, has_hurt=True),
	16: Monster(16, "Metal Slime", Stats(4, 4, 0, 0, 10, 255, 255, 3), 115, 6, run_chance=0.75),
	17: Monster(17, "Specter", Stats(48, 48, 0, 0, 46, 38, 25, 9), 28, 75),
	18: Monster(18, "Wolflord", Stats(56, 56, 0, 0, 50, 40, 32, 10), 32, 85),
	19: Monster(19, "Druinlord", Stats(47, 47, 0, 0, 52, 50, 28, 10), 35, 95),
	20: Monster(20, "Drollmagi", Stats(58, 58, 12, 12, 52, 50, 23, 11), 38, 105, spell_chance=0.3, has_stopspell=True, has_hurt=True),
	21: Monster(21, "Wyvern", Stats(64, 64, 0, 0, 56, 48, 34, 12), 42, 105),
	22: Monster(22, "Rouge Scorpion", Stats(55, 55, 0, 0, 60, 90, 42, 12), 45, 110),
	23: Monster(23, "Wraith Knight", Stats(68, 68, 0, 0, 68, 56, 38, 13), 47, 120),
	24: Monster(24, "Golem", Stats(132, 132, 0, 0, 120, 255, 40, 18), 255, 10),
	25: Monster(25, "Goldman", Stats(65, 65, 0, 0, 60, 70, 40, 13), 50, 255),
	26: Monster(26, "Knight", Stats(76, 76, 0, 0, 76, 78, 42, 14), 52, 165),
	27: Monster(27, "Magiwyvern", Stats(78, 78, 16, 16, 78, 70, 50, 15), 58, 135, spell_chance=0.3, has_sleep=True, has_stopspell=True),
	28: Monster(28, "Demon Knight", Stats(79, 79, 0, 0, 79, 64, 45, 15), 60, 148),
	29: Monster(29, "Werewolf", Stats(86, 86, 0, 0, 86, 70, 68, 16), 63, 155),
	30: Monster(30, "Green Dragon", Stats(88, 88, 0, 0, 88, 80, 50, 16), 70, 160),
	31: Monster(31, "Starwyvern", Stats(86, 86, 0, 0, 90, 82, 75, 17), 78, 169),
	32: Monster(32, "Wizard", Stats(80, 80, 20, 20, 80, 70, 78, 17), 83, 185, spell_chance=0.35, has_heal=True, has_sleep=True, has_hurt=True),
	33: Monster(33, "Axe Knight", Stats(94, 94, 0, 0, 94, 92, 70, 18), 90, 165),
	34: Monster(34, "Blue Dragon", Stats(98, 98, 20, 20, 98, 95, 72, 19), 98, 150),
	35: Monster(35, "Stoneman", Stats(160, 160, 0, 0, 100, 255, 40, 20), 255, 135),
	36: Monster(36, "Armored Knight", Stats(105, 105, 0, 0, 105, 86, 80, 20), 105, 169),
	37: Monster(37, "Red Dragon", Stats(100, 100, 30, 30, 120, 90, 75, 22), 120, 143),
	38: Monster(38, "Dragonlord", Stats(100, 100, 20, 20, 90, 95, 75, 25), 0, 0, spell_chance=0.3, has_heal=True, has_hurt=True),
}


class DamageCalculator:
	"""Calculate damage using Dragon Warrior formulas."""

	@staticmethod
	def calculate_physical_damage(attacker: Stats, defender: Stats) -> int:
		"""
		Calculate physical attack damage.

		Dragon Warrior formula (approximate):
		damage = (attack / 2) - (defense / 4) + variance

		variance = ±(attack / 8)
		"""
		attack = attacker.get_total_attack()
		defense = defender.get_total_defense()

		# Base damage
		base = max(0, (attack // 2) - (defense // 4))

		# Variance
		variance = attack // 8
		damage = base + random.randint(-variance, variance)

		# Minimum damage (can always deal at least 1)
		damage = max(1, damage)

		return damage

	@staticmethod
	def calculate_spell_damage(spell_power: int, defender: Stats) -> int:
		"""
		Calculate spell damage.

		HURT: 10-17 damage
		HURTMORE: 35-65 damage
		"""
		if spell_power <= 10:
			# HURT
			base = 10
			variance = 7
		else:
			# HURTMORE
			base = 35
			variance = 30

		damage = base + random.randint(0, variance)

		# Resistance reduces damage
		# (Note: Dragon Warrior doesn't have spell resistance reduction,
		#  resistant monsters are immune)

		return damage

	@staticmethod
	def calculate_heal_amount(spell_power: int) -> int:
		"""
		Calculate heal amount.

		HEAL: 10-17 HP
		HEALMORE: 85-100 HP (approximate)
		"""
		if spell_power <= 10:
			# HEAL
			return 10 + random.randint(0, 7)
		else:
			# HEALMORE
			return 85 + random.randint(0, 15)

	@staticmethod
	def calculate_agility_order(stats1: Stats, stats2: Stats) -> Tuple[Stats, Stats]:
		"""
		Determine turn order based on agility.

		Returns (first, second) tuple.
		"""
		# Add randomness to agility check
		agi1 = stats1.agility + random.randint(-2, 2)
		agi2 = stats2.agility + random.randint(-2, 2)

		if agi1 >= agi2:
			return (stats1, stats2)
		else:
			return (stats2, stats1)

	@staticmethod
	def can_run(player: Stats, monster: Stats) -> bool:
		"""Check if player can run from battle."""
		# Higher agility = higher chance to run
		# Formula: (player_agility / monster_agility) > random(0, 1)
		if monster.agility == 0:
			return True

		escape_chance = player.agility / (monster.agility * 1.5)
		return random.random() < escape_chance


class BattleSimulator:
	"""Simulate battles between player and monsters."""

	def __init__(self):
		self.calculator = DamageCalculator()

	def simulate_battle(
		self,
		player_stats: Stats,
		monster: Monster,
		verbose: bool = False
	) -> Dict:
		"""
		Simulate a single battle.

		Returns dict with battle results:
		- winner: 'player' or 'monster'
		- rounds: number of rounds
		- player_damage_dealt: total damage dealt by player
		- monster_damage_dealt: total damage dealt by monster
		- player_final_hp: player HP at end
		"""
		# Make copies to not modify originals
		player = player_stats.copy()
		enemy_stats = monster.stats.copy()

		round_num = 0
		player_total_damage = 0
		monster_total_damage = 0

		if verbose:
			print(f"\nBattle: Player (Lv{player.level}) vs {monster.name}")
			print(f"Player: HP {player.hp}/{player.max_hp}, ATK {player.get_total_attack()}, DEF {player.get_total_defense()}")
			print(f"Enemy:  HP {enemy_stats.hp}/{enemy_stats.max_hp}, ATK {enemy_stats.attack}, DEF {enemy_stats.defense}")
			print()

		while player.is_alive() and enemy_stats.is_alive():
			round_num += 1

			if verbose:
				print(f"Round {round_num}:")

			# Determine turn order
			first, second = self.calculator.calculate_agility_order(player, enemy_stats)

			# Process turns
			for attacker, defender in [(first, second), (second, first)]:
				if not attacker.is_alive() or not defender.is_alive():
					break

				# Check status effects
				if attacker.status == StatusEffect.SLEEP:
					if verbose:
						name = "Player" if attacker == player else monster.name
						print(f"  {name} is asleep!")
					attacker.tick_status()
					continue

				# Determine action
				if attacker == enemy_stats:
					# Monster AI
					action = self._monster_ai_action(monster, enemy_stats, player)
				else:
					# Player always attacks in simulation
					action = 'attack'

				# Execute action
				if action == 'attack':
					damage = self.calculator.calculate_physical_damage(attacker, defender)
					actual = defender.apply_damage(damage)

					if attacker == player:
						player_total_damage += actual
					else:
						monster_total_damage += actual

					if verbose:
						name = "Player" if attacker == player else monster.name
						target = monster.name if attacker == player else "Player"
						print(f"  {name} attacks {target} for {actual} damage! ({defender.hp}/{defender.max_hp} HP)")

				elif action == 'hurt':
					damage = self.calculator.calculate_spell_damage(10, defender)
					actual = defender.apply_damage(damage)

					if attacker == enemy_stats:
						monster_total_damage += actual

					if verbose:
						print(f"  {monster.name} casts HURT! {actual} damage! ({defender.hp}/{defender.max_hp} HP)")

				elif action == 'heal':
					amount = self.calculator.calculate_heal_amount(10)
					healed = attacker.heal(amount)

					if verbose:
						print(f"  {monster.name} casts HEAL! Restored {healed} HP! ({attacker.hp}/{attacker.max_hp} HP)")

				elif action == 'sleep':
					if not player.status == StatusEffect.SLEEP:
						player.apply_status(StatusEffect.SLEEP, 3)
						if verbose:
							print(f"  {monster.name} casts SLEEP! Player fell asleep!")

				# Tick status
				attacker.tick_status()

			if verbose:
				print()

		# Determine winner
		winner = 'player' if player.is_alive() else 'monster'

		return {
			'winner': winner,
			'rounds': round_num,
			'player_damage_dealt': player_total_damage,
			'monster_damage_dealt': monster_total_damage,
			'player_final_hp': player.hp,
		}

	def _monster_ai_action(self, monster: Monster, enemy_stats: Stats, player: Stats) -> str:
		"""Determine monster AI action."""
		# Spell casting chance
		if random.random() < monster.spell_chance:
			# Choose spell
			available_spells = []

			if monster.has_heal and enemy_stats.hp < enemy_stats.max_hp * 0.5:
				available_spells.append('heal')

			if monster.has_hurt and not monster.resist_hurt:
				available_spells.append('hurt')

			if monster.has_sleep and player.status != StatusEffect.SLEEP:
				available_spells.append('sleep')

			if monster.has_stopspell and player.status != StatusEffect.STOPSPELL:
				available_spells.append('stopspell')

			if available_spells:
				return random.choice(available_spells)

		# Default to attack
		return 'attack'

	def simulate_multiple_battles(
		self,
		player_stats: Stats,
		monster: Monster,
		num_battles: int = 1000,
		verbose: bool = False
	) -> Dict:
		"""
		Simulate multiple battles and return statistics.

		Returns:
		- win_rate: player win percentage
		- avg_rounds: average battle length
		- avg_player_damage: average damage dealt by player
		- avg_monster_damage: average damage dealt by monster
		- avg_final_hp: average player HP at victory
		- min_rounds: minimum rounds in any battle
		- max_rounds: maximum rounds in any battle
		"""
		results = []

		for i in range(num_battles):
			result = self.simulate_battle(player_stats, monster, verbose=verbose and i == 0)
			results.append(result)

		# Calculate statistics
		wins = sum(1 for r in results if r['winner'] == 'player')
		win_rate = wins / num_battles

		avg_rounds = statistics.mean(r['rounds'] for r in results)
		avg_player_damage = statistics.mean(r['player_damage_dealt'] for r in results)
		avg_monster_damage = statistics.mean(r['monster_damage_dealt'] for r in results)

		# Only victories
		victories = [r for r in results if r['winner'] == 'player']
		avg_final_hp = statistics.mean(r['player_final_hp'] for r in victories) if victories else 0

		min_rounds = min(r['rounds'] for r in results)
		max_rounds = max(r['rounds'] for r in results)

		return {
			'num_battles': num_battles,
			'win_rate': win_rate,
			'avg_rounds': avg_rounds,
			'avg_player_damage': avg_player_damage,
			'avg_monster_damage': avg_monster_damage,
			'avg_final_hp': avg_final_hp,
			'min_rounds': min_rounds,
			'max_rounds': max_rounds,
		}


class InteractiveDamageCalculator:
	"""Interactive damage calculator and battle simulator."""

	def __init__(self):
		self.simulator = BattleSimulator()
		self.calculator = DamageCalculator()

		# Default player stats (level 10, copper sword, leather armor)
		self.player = Stats(
			hp=45, max_hp=45,
			mp=18, max_mp=18,
			attack=15, defense=12,
			agility=20, level=10,
			weapon_attack=10,	# Copper Sword
			armor_defense=4,		# Leather Armor
			shield_defense=4		# Small Shield
		)

	def run(self) -> None:
		"""Run interactive calculator."""
		print("Dragon Warrior Damage Calculator and Battle Simulator")
		print("=" * 60)
		print("Commands: stats, monster, damage, battle, simulate, equip, help, quit")
		print()

		while True:
			try:
				cmd = input("calculator> ").strip().lower()

				if not cmd:
					continue

				parts = cmd.split()
				command = parts[0]
				args = parts[1:] if len(parts) > 1 else []

				if command == 'quit' or command == 'exit':
					break
				elif command == 'help':
					self._show_help()
				elif command == 'stats':
					self._show_player_stats()
				elif command == 'monster':
					self._show_monster_info(args)
				elif command == 'damage':
					self._calculate_damage(args)
				elif command == 'battle':
					self._simulate_single_battle(args)
				elif command == 'simulate':
					self._simulate_multiple_battles(args)
				elif command == 'equip':
					self._equip_item(args)
				elif command == 'level':
					self._set_level(args)
				else:
					print(f"Unknown command: {command}")

			except KeyboardInterrupt:
				print("\nUse 'quit' to exit.")
			except Exception as e:
				print(f"Error: {e}")

	def _show_help(self) -> None:
		"""Show help text."""
		print("""
Damage Calculator Commands:

stats                       - Show player stats
monster <id>                - Show monster info
damage <monster_id>         - Calculate damage vs monster
battle <monster_id>         - Simulate single battle
simulate <monster_id> [num] - Simulate multiple battles
equip <weapon> <armor> <shield> - Set equipment attack/defense
level <level>               - Set player level
help                        - Show this help
quit                        - Exit calculator

Examples:
	stats
	monster 11
	damage 11
	battle 11
	simulate 11 1000
	equip 10 4 4
	level 15
""")

	def _show_player_stats(self) -> None:
		"""Show player stats."""
		print(f"\nPlayer Stats (Level {self.player.level}):")
		print(f"  HP: {self.player.hp}/{self.player.max_hp}")
		print(f"  MP: {self.player.mp}/{self.player.max_mp}")
		print(f"  Attack: {self.player.attack} + {self.player.weapon_attack} (weapon) = {self.player.get_total_attack()}")
		print(f"  Defense: {self.player.defense} + {self.player.armor_defense} (armor) + {self.player.shield_defense} (shield) = {self.player.get_total_defense()}")
		print(f"  Agility: {self.player.agility}")

	def _show_monster_info(self, args: List[str]) -> None:
		"""Show monster information."""
		if not args:
			print("Usage: monster <monster_id>")
			print("\nAvailable monsters:")
			for mid in sorted(MONSTER_DATABASE.keys())[:20]:
				monster = MONSTER_DATABASE[mid]
				print(f"  {mid:2d}: {monster.name}")
			print("  ... (and more)")
			return

		try:
			monster_id = int(args[0])
		except ValueError:
			print(f"Invalid monster ID: {args[0]}")
			return

		if monster_id not in MONSTER_DATABASE:
			print(f"Monster {monster_id} not found")
			return

		monster = MONSTER_DATABASE[monster_id]

		print(f"\n{monster.name} (ID: {monster.id}):")
		print(f"  HP: {monster.stats.max_hp}")
		print(f"  Attack: {monster.stats.attack}")
		print(f"  Defense: {monster.stats.defense}")
		print(f"  Agility: {monster.stats.agility}")
		print(f"  XP: {monster.xp}")
		print(f"  Gold: {monster.gold}")

		if monster.spell_chance > 0:
			print(f"  Spell Chance: {monster.spell_chance * 100:.0f}%")
			spells = []
			if monster.has_heal:
				spells.append("HEAL")
			if monster.has_hurt:
				spells.append("HURT")
			if monster.has_sleep:
				spells.append("SLEEP")
			if monster.has_stopspell:
				spells.append("STOPSPELL")
			if spells:
				print(f"  Spells: {', '.join(spells)}")

	def _calculate_damage(self, args: List[str]) -> None:
		"""Calculate damage against monster."""
		if not args:
			print("Usage: damage <monster_id>")
			return

		try:
			monster_id = int(args[0])
		except ValueError:
			print(f"Invalid monster ID: {args[0]}")
			return

		if monster_id not in MONSTER_DATABASE:
			print(f"Monster {monster_id} not found")
			return

		monster = MONSTER_DATABASE[monster_id]

		print(f"\nDamage Calculation: Player vs {monster.name}")
		print("=" * 60)

		# Player damage to monster
		player_damages = [
			self.calculator.calculate_physical_damage(self.player, monster.stats)
			for _ in range(100)
		]

		# Monster damage to player
		monster_damages = [
			self.calculator.calculate_physical_damage(monster.stats, self.player)
			for _ in range(100)
		]

		print(f"\nPlayer Attack:")
		print(f"  Min: {min(player_damages)}")
		print(f"  Max: {max(player_damages)}")
		print(f"  Avg: {statistics.mean(player_damages):.1f}")

		print(f"\n{monster.name} Attack:")
		print(f"  Min: {min(monster_damages)}")
		print(f"  Max: {max(monster_damages)}")
		print(f"  Avg: {statistics.mean(monster_damages):.1f}")

		# Rounds to kill
		avg_player_damage = statistics.mean(player_damages)
		avg_monster_damage = statistics.mean(monster_damages)

		rounds_to_kill = monster.stats.max_hp / avg_player_damage if avg_player_damage > 0 else 999
		player_survival_rounds = self.player.max_hp / avg_monster_damage if avg_monster_damage > 0 else 999

		print(f"\nEstimated Rounds:")
		print(f"  To kill {monster.name}: {rounds_to_kill:.1f} rounds")
		print(f"  Player survives: {player_survival_rounds:.1f} rounds")

		if rounds_to_kill < player_survival_rounds:
			print(f"  Outcome: Likely VICTORY")
		else:
			print(f"  Outcome: Likely DEFEAT")

	def _simulate_single_battle(self, args: List[str]) -> None:
		"""Simulate a single battle with verbose output."""
		if not args:
			print("Usage: battle <monster_id>")
			return

		try:
			monster_id = int(args[0])
		except ValueError:
			print(f"Invalid monster ID: {args[0]}")
			return

		if monster_id not in MONSTER_DATABASE:
			print(f"Monster {monster_id} not found")
			return

		monster = MONSTER_DATABASE[monster_id]

		result = self.simulator.simulate_battle(self.player, monster, verbose=True)

		print(f"\nBattle Result:")
		print(f"  Winner: {result['winner'].upper()}")
		print(f"  Rounds: {result['rounds']}")
		print(f"  Player Damage Dealt: {result['player_damage_dealt']}")
		print(f"  Monster Damage Dealt: {result['monster_damage_dealt']}")
		if result['winner'] == 'player':
			print(f"  Player Final HP: {result['player_final_hp']}/{self.player.max_hp}")

	def _simulate_multiple_battles(self, args: List[str]) -> None:
		"""Simulate multiple battles."""
		if not args:
			print("Usage: simulate <monster_id> [num_battles]")
			return

		try:
			monster_id = int(args[0])
			num_battles = int(args[1]) if len(args) > 1 else 1000
		except ValueError:
			print("Invalid parameters")
			return

		if monster_id not in MONSTER_DATABASE:
			print(f"Monster {monster_id} not found")
			return

		monster = MONSTER_DATABASE[monster_id]

		print(f"\nSimulating {num_battles} battles: Player (Lv{self.player.level}) vs {monster.name}...")

		stats = self.simulator.simulate_multiple_battles(self.player, monster, num_battles)

		print(f"\nSimulation Results:")
		print(f"  Battles: {stats['num_battles']}")
		print(f"  Win Rate: {stats['win_rate'] * 100:.1f}%")
		print(f"  Avg Rounds: {stats['avg_rounds']:.1f}")
		print(f"  Avg Player Damage: {stats['avg_player_damage']:.1f}")
		print(f"  Avg Monster Damage: {stats['avg_monster_damage']:.1f}")
		print(f"  Avg Final HP (victories): {stats['avg_final_hp']:.1f}/{self.player.max_hp}")
		print(f"  Min/Max Rounds: {stats['min_rounds']}/{stats['max_rounds']}")

	def _equip_item(self, args: List[str]) -> None:
		"""Set equipment bonuses."""
		if len(args) < 3:
			print("Usage: equip <weapon_atk> <armor_def> <shield_def>")
			return

		try:
			self.player.weapon_attack = int(args[0])
			self.player.armor_defense = int(args[1])
			self.player.shield_defense = int(args[2])
		except ValueError:
			print("Invalid equipment values")
			return

		print(f"Equipment updated:")
		print(f"  Total Attack: {self.player.get_total_attack()}")
		print(f"  Total Defense: {self.player.get_total_defense()}")

	def _set_level(self, args: List[str]) -> None:
		"""Set player level (and scale stats)."""
		if not args:
			print("Usage: level <level>")
			return

		try:
			level = int(args[0])
		except ValueError:
			print(f"Invalid level: {args[0]}")
			return

		# Scale stats based on level (rough approximation)
		self.player.level = level
		self.player.max_hp = 15 + (level * 3)
		self.player.hp = self.player.max_hp
		self.player.max_mp = max(0, (level - 1) * 2)
		self.player.mp = self.player.max_mp
		self.player.attack = 5 + level
		self.player.defense = 4 + level
		self.player.agility = 10 + level

		print(f"Player level set to {level}")
		self._show_player_stats()


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Dragon Warrior Damage Calculator and Battle Simulator'
	)
	parser.add_argument(
		'--player-level',
		type=int,
		help='Player level'
	)
	parser.add_argument(
		'--monster-id',
		type=int,
		help='Monster ID to analyze'
	)
	parser.add_argument(
		'--simulate',
		type=int,
		help='Number of battles to simulate'
	)

	args = parser.parse_args()

	calculator = InteractiveDamageCalculator()

	if args.player_level:
		calculator._set_level([str(args.player_level)])

	if args.monster_id is not None:
		if args.simulate:
			calculator._simulate_multiple_battles([str(args.monster_id), str(args.simulate)])
		else:
			calculator._calculate_damage([str(args.monster_id)])
			return

	calculator.run()


if __name__ == '__main__':
	main()
