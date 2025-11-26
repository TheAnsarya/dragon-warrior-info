#!/usr/bin/env python3
"""
Dragon Warrior Enemy AI Behavior Editor

Advanced editor for Dragon Warrior's enemy AI patterns and battle behaviors.
Features:
- Edit AI decision trees for all 39 monsters
- Configure attack patterns, spell usage, and special abilities
- Balance difficulty curves across zones
- Simulate battle AI to test changes
- Generate AI behavior reports and statistics
- Create custom enemy behaviors and strategies

Dragon Warrior AI System:
- Each monster has an 8-bit attack pattern bitfield
- AI decides between: normal attack, spells, special abilities, flee
- Decision influenced by: HP%, MP, player level, battle turn count
- Some monsters have conditional behaviors (e.g., only use Hurt when HP > 50%)

Author: Dragon Warrior Toolkit
Date: 2024-11-26
"""

import argparse
import random
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from enum import IntEnum, Flag, auto
import json


class AIAction(IntEnum):
	"""Actions an enemy AI can take."""
	ATTACK = 0
	SLEEP_SPELL = 1
	STOPSPELL_SPELL = 2
	HURT_SPELL = 3
	HURTMORE_SPELL = 4
	FIRE_BREATH = 5
	STRONG_ATTACK = 6
	HEAL_SPELL = 7
	RUN_AWAY = 8
	DEFEND = 9
	SPECIAL_ABILITY = 10


class AICondition(Flag):
	"""Conditions that influence AI decisions."""
	ALWAYS = auto()
	HP_HIGH = auto()      # HP > 75%
	HP_MEDIUM = auto()    # HP 25-75%
	HP_LOW = auto()       # HP < 25%
	PLAYER_HP_HIGH = auto()
	PLAYER_HP_LOW = auto()
	PLAYER_ASLEEP = auto()
	PLAYER_STOPSPELLED = auto()
	TURN_FIRST = auto()   # First turn of battle
	TURN_LATE = auto()    # Turn 5+
	MP_AVAILABLE = auto()
	ALONE = auto()        # Only enemy in battle
	GROUP = auto()        # Multiple enemies


@dataclass
class AIBehaviorRule:
	"""A single AI behavior rule with conditions and action."""
	priority: int              # Higher priority rules checked first
	condition: AICondition
	action: AIAction
	action_probability: float  # 0.0-1.0 probability of taking action if condition met
	mp_cost: int = 0
	description: str = ""

	def check_condition(self, battle_state: 'BattleState', monster: 'MonsterAI') -> bool:
		"""Check if conditions are met for this rule."""
		if AICondition.ALWAYS in self.condition:
			return True

		conditions_met = True

		# HP conditions
		hp_percent = monster.current_hp / monster.max_hp if monster.max_hp > 0 else 0

		if AICondition.HP_HIGH in self.condition:
			conditions_met &= hp_percent > 0.75
		if AICondition.HP_MEDIUM in self.condition:
			conditions_met &= 0.25 <= hp_percent <= 0.75
		if AICondition.HP_LOW in self.condition:
			conditions_met &= hp_percent < 0.25

		# Player HP conditions
		player_hp_percent = battle_state.player_hp / battle_state.player_max_hp if battle_state.player_max_hp > 0 else 0

		if AICondition.PLAYER_HP_HIGH in self.condition:
			conditions_met &= player_hp_percent > 0.75
		if AICondition.PLAYER_HP_LOW in self.condition:
			conditions_met &= player_hp_percent < 0.25

		# Status conditions
		if AICondition.PLAYER_ASLEEP in self.condition:
			conditions_met &= battle_state.player_asleep
		if AICondition.PLAYER_STOPSPELLED in self.condition:
			conditions_met &= battle_state.player_stopspelled

		# Turn conditions
		if AICondition.TURN_FIRST in self.condition:
			conditions_met &= battle_state.turn_count == 1
		if AICondition.TURN_LATE in self.condition:
			conditions_met &= battle_state.turn_count >= 5

		# MP condition
		if AICondition.MP_AVAILABLE in self.condition:
			conditions_met &= monster.current_mp >= self.mp_cost

		# Group conditions
		if AICondition.ALONE in self.condition:
			conditions_met &= battle_state.enemy_count == 1
		if AICondition.GROUP in self.condition:
			conditions_met &= battle_state.enemy_count > 1

		return conditions_met

	def to_dict(self) -> dict:
		return {
			'priority': self.priority,
			'condition': str(self.condition),
			'action': AIAction(self.action).name,
			'probability': self.action_probability,
			'mp_cost': self.mp_cost,
			'description': self.description
		}


@dataclass
class BattleState:
	"""Current state of a battle for AI simulation."""
	turn_count: int = 1
	player_hp: int = 100
	player_max_hp: int = 100
	player_mp: int = 50
	player_max_mp: int = 50
	player_asleep: bool = False
	player_stopspelled: bool = False
	player_attack: int = 20
	player_defense: int = 20
	enemy_count: int = 1


@dataclass
class MonsterAI:
	"""AI configuration for a monster."""
	monster_id: int
	monster_name: str
	max_hp: int
	current_hp: int
	max_mp: int = 0
	current_mp: int = 0
	base_attack: int = 10
	agility: int = 10
	behavior_rules: List[AIBehaviorRule] = field(default_factory=list)

	def choose_action(self, battle_state: BattleState) -> Tuple[AIAction, str]:
		"""Choose an action based on AI rules and battle state."""
		# Sort rules by priority
		sorted_rules = sorted(self.behavior_rules, key=lambda r: r.priority, reverse=True)

		for rule in sorted_rules:
			if rule.check_condition(battle_state, self):
				# Check probability
				if random.random() <= rule.action_probability:
					# Check MP cost
					if rule.mp_cost <= self.current_mp or rule.mp_cost == 0:
						return rule.action, rule.description

		# Default: normal attack
		return AIAction.ATTACK, "Default attack"

	def simulate_action(self, action: AIAction, battle_state: BattleState) -> Dict:
		"""Simulate the result of an action."""
		result = {
			'action': AIAction(action).name,
			'success': True,
			'damage': 0,
			'effect': '',
			'mp_cost': 0
		}

		if action == AIAction.ATTACK:
			# Simple damage formula: (attack / 2) - (defense / 4) + variance
			base_damage = max(1, (self.base_attack // 2) - (battle_state.player_defense // 4))
			variance = random.randint(-base_damage // 4, base_damage // 4)
			damage = max(0, base_damage + variance)

			result['damage'] = damage
			result['effect'] = f"{self.monster_name} attacks for {damage} damage"

		elif action == AIAction.STRONG_ATTACK:
			base_damage = max(1, self.base_attack - (battle_state.player_defense // 4))
			variance = random.randint(-base_damage // 4, base_damage // 4)
			damage = max(0, base_damage + variance)

			result['damage'] = damage
			result['effect'] = f"{self.monster_name} unleashes a powerful attack for {damage} damage!"

		elif action == AIAction.SLEEP_SPELL:
			result['mp_cost'] = 2
			if self.current_mp >= 2:
				self.current_mp -= 2
				# Sleep success rate ~50%
				if random.random() < 0.5:
					result['effect'] = f"{self.monster_name} casts Sleep! The hero falls asleep!"
				else:
					result['effect'] = f"{self.monster_name} casts Sleep, but it fails!"
					result['success'] = False
			else:
				result['success'] = False
				result['effect'] = f"{self.monster_name} tried to cast Sleep, but has no MP!"

		elif action == AIAction.STOPSPELL_SPELL:
			result['mp_cost'] = 2
			if self.current_mp >= 2:
				self.current_mp -= 2
				if random.random() < 0.5:
					result['effect'] = f"{self.monster_name} casts Stopspell! The hero's magic is blocked!"
				else:
					result['effect'] = f"{self.monster_name} casts Stopspell, but it fails!"
					result['success'] = False
			else:
				result['success'] = False
				result['effect'] = f"{self.monster_name} tried to cast Stopspell, but has no MP!"

		elif action == AIAction.HURT_SPELL:
			result['mp_cost'] = 2
			if self.current_mp >= 2:
				self.current_mp -= 2
				damage = random.randint(5, 12)
				result['damage'] = damage
				result['effect'] = f"{self.monster_name} casts Hurt for {damage} damage!"
			else:
				result['success'] = False
				result['effect'] = f"{self.monster_name} tried to cast Hurt, but has no MP!"

		elif action == AIAction.HURTMORE_SPELL:
			result['mp_cost'] = 5
			if self.current_mp >= 5:
				self.current_mp -= 5
				damage = random.randint(58, 65)
				result['damage'] = damage
				result['effect'] = f"{self.monster_name} casts Hurtmore for {damage} damage!"
			else:
				result['success'] = False
				result['effect'] = f"{self.monster_name} tried to cast Hurtmore, but has no MP!"

		elif action == AIAction.FIRE_BREATH:
			damage = random.randint(16, 23)
			# Fire breath can be reduced by Dragon's Scale
			result['damage'] = damage
			result['effect'] = f"{self.monster_name} breathes fire for {damage} damage!"

		elif action == AIAction.HEAL_SPELL:
			result['mp_cost'] = 4
			if self.current_mp >= 4:
				self.current_mp -= 4
				heal_amount = random.randint(10, 17)
				self.current_hp = min(self.max_hp, self.current_hp + heal_amount)
				result['effect'] = f"{self.monster_name} casts Heal and recovers {heal_amount} HP!"
			else:
				result['success'] = False
				result['effect'] = f"{self.monster_name} tried to cast Heal, but has no MP!"

		elif action == AIAction.RUN_AWAY:
			result['effect'] = f"{self.monster_name} attempts to flee!"

		elif action == AIAction.DEFEND:
			result['effect'] = f"{self.monster_name} takes a defensive stance!"

		return result

	def to_dict(self) -> dict:
		return {
			'id': self.monster_id,
			'name': self.monster_name,
			'hp': self.max_hp,
			'mp': self.max_mp,
			'attack': self.base_attack,
			'agility': self.agility,
			'behavior_rules': [rule.to_dict() for rule in self.behavior_rules]
		}


# Pre-configured AI behaviors for all 39 Dragon Warrior monsters
def create_default_monster_ai() -> List[MonsterAI]:
	"""Create default AI configurations for all monsters."""
	monsters = []

	# Slime (0) - Basic attack only
	slime = MonsterAI(0, "Slime", 2, 2, 0, 0, 5, 3)
	slime.behavior_rules = [
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Always attack")
	]
	monsters.append(slime)

	# Red Slime (1) - Basic attack only
	red_slime = MonsterAI(1, "Red Slime", 3, 3, 0, 0, 7, 3)
	red_slime.behavior_rules = [
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Always attack")
	]
	monsters.append(red_slime)

	# Drakee (2) - Basic attack only
	drakee = MonsterAI(2, "Drakee", 6, 6, 0, 0, 9, 6)
	drakee.behavior_rules = [
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Always attack")
	]
	monsters.append(drakee)

	# Ghost (3) - Can use Hurt spell
	ghost = MonsterAI(3, "Ghost", 7, 7, 3, 3, 11, 8)
	ghost.behavior_rules = [
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.HURT_SPELL, 0.3, mp_cost=2, description="30% chance to cast Hurt"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(ghost)

	# Magician (4) - Can use Hurt and Sleep
	magician = MonsterAI(4, "Magician", 13, 13, 15, 15, 11, 12)
	magician.behavior_rules = [
		AIBehaviorRule(30, AICondition.PLAYER_HP_HIGH | AICondition.MP_AVAILABLE, AIAction.HURT_SPELL, 0.4, mp_cost=2, description="40% Hurt when player HP high"),
		AIBehaviorRule(25, AICondition.MP_AVAILABLE, AIAction.SLEEP_SPELL, 0.3, mp_cost=2, description="30% Sleep spell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(magician)

	# Magidrakee (5) - Uses Hurt frequently
	magidrakee = MonsterAI(5, "Magidrakee", 15, 15, 8, 8, 14, 14)
	magidrakee.behavior_rules = [
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.HURT_SPELL, 0.5, mp_cost=2, description="50% chance to cast Hurt"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(magidrakee)

	# Scorpion (6) - Basic attack
	scorpion = MonsterAI(6, "Scorpion", 20, 20, 0, 0, 18, 16)
	scorpion.behavior_rules = [
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Always attack")
	]
	monsters.append(scorpion)

	# Druin (7) - Basic attack
	druin = MonsterAI(7, "Druin", 22, 22, 0, 0, 20, 18)
	druin.behavior_rules = [
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Always attack")
	]
	monsters.append(druin)

	# Poltergeist (8) - Uses Hurt
	poltergeist = MonsterAI(8, "Poltergeist", 23, 23, 12, 12, 18, 20)
	poltergeist.behavior_rules = [
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.HURT_SPELL, 0.4, mp_cost=2, description="40% Hurt spell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(poltergeist)

	# Droll (9) - Uses Sleep
	droll = MonsterAI(9, "Droll", 25, 25, 6, 6, 24, 24)
	droll.behavior_rules = [
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.SLEEP_SPELL, 0.35, mp_cost=2, description="35% Sleep spell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(droll)

	# Drakeema (10) - Uses Stopspell
	drakeema = MonsterAI(10, "Drakeema", 20, 20, 8, 8, 22, 26)
	drakeema.behavior_rules = [
		AIBehaviorRule(25, AICondition.MP_AVAILABLE, AIAction.STOPSPELL_SPELL, 0.3, mp_cost=2, description="30% Stopspell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(drakeema)

	# Skeleton (11) - Basic attack
	skeleton = MonsterAI(11, "Skeleton", 30, 30, 0, 0, 28, 22)
	skeleton.behavior_rules = [
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Always attack")
	]
	monsters.append(skeleton)

	# Warlock (12) - Uses Hurt and Sleep
	warlock = MonsterAI(12, "Warlock", 30, 30, 15, 15, 28, 22)
	warlock.behavior_rules = [
		AIBehaviorRule(30, AICondition.PLAYER_HP_HIGH | AICondition.MP_AVAILABLE, AIAction.HURT_SPELL, 0.4, mp_cost=2, description="40% Hurt when player HP high"),
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.SLEEP_SPELL, 0.25, mp_cost=2, description="25% Sleep spell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(warlock)

	# Metal Scorpion (13) - Strong attack, fire breath
	metal_scorpion = MonsterAI(13, "Metal Scorpion", 22, 22, 0, 0, 36, 42)
	metal_scorpion.behavior_rules = [
		AIBehaviorRule(20, AICondition.PLAYER_HP_HIGH, AIAction.FIRE_BREATH, 0.3, description="30% fire breath when player HP high"),
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.2, description="20% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(metal_scorpion)

	# Wolf (14) - Fast, basic attack
	wolf = MonsterAI(14, "Wolf", 34, 34, 0, 0, 34, 40)
	wolf.behavior_rules = [
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Always attack")
	]
	monsters.append(wolf)

	# Wraith (15) - Uses Hurt
	wraith = MonsterAI(15, "Wraith", 36, 36, 10, 10, 34, 34)
	wraith.behavior_rules = [
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.HURT_SPELL, 0.45, mp_cost=2, description="45% Hurt spell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(wraith)

	# Metal Slime (16) - High defense, tries to flee
	metal_slime = MonsterAI(16, "Metal Slime", 4, 4, 0, 0, 10, 255)
	metal_slime.behavior_rules = [
		AIBehaviorRule(100, AICondition.ALWAYS, AIAction.RUN_AWAY, 0.9, description="90% chance to flee"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Rarely attacks")
	]
	monsters.append(metal_slime)

	# Specter (17) - Uses Stopspell
	specter = MonsterAI(17, "Specter", 36, 36, 8, 8, 40, 38)
	specter.behavior_rules = [
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.STOPSPELL_SPELL, 0.35, mp_cost=2, description="35% Stopspell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(specter)

	# Wolflord (18) - Strong attacks
	wolflord = MonsterAI(18, "Wolflord", 50, 50, 0, 0, 50, 50)
	wolflord.behavior_rules = [
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.25, description="25% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(wolflord)

	# Druinlord (19) - Basic attack
	druinlord = MonsterAI(19, "Druinlord", 47, 47, 0, 0, 52, 50)
	druinlord.behavior_rules = [
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Always attack")
	]
	monsters.append(druinlord)

	# Drollmagi (20) - Uses Sleep and Stopspell
	drollmagi = MonsterAI(20, "Drollmagi", 38, 38, 20, 20, 52, 50)
	drollmagi.behavior_rules = [
		AIBehaviorRule(25, AICondition.MP_AVAILABLE, AIAction.SLEEP_SPELL, 0.35, mp_cost=2, description="35% Sleep spell"),
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.STOPSPELL_SPELL, 0.3, mp_cost=2, description="30% Stopspell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(drollmagi)

	# Wyvern (21) - Fire breath
	wyvern = MonsterAI(21, "Wyvern", 56, 56, 0, 0, 56, 48)
	wyvern.behavior_rules = [
		AIBehaviorRule(20, AICondition.ALWAYS, AIAction.FIRE_BREATH, 0.4, description="40% fire breath"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(wyvern)

	# Rogue Scorpion (22) - Fire breath and strong attacks
	rogue_scorpion = MonsterAI(22, "Rogue Scorpion", 35, 35, 0, 0, 60, 90)
	rogue_scorpion.behavior_rules = [
		AIBehaviorRule(20, AICondition.ALWAYS, AIAction.FIRE_BREATH, 0.35, description="35% fire breath"),
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.2, description="20% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(rogue_scorpion)

	# Wraith Knight (23) - Hurt and strong attacks
	wraith_knight = MonsterAI(23, "Wraith Knight", 68, 68, 16, 16, 68, 58)
	wraith_knight.behavior_rules = [
		AIBehaviorRule(25, AICondition.MP_AVAILABLE, AIAction.HURT_SPELL, 0.35, mp_cost=2, description="35% Hurt spell"),
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.25, description="25% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(wraith_knight)

	# Golem (24) - Very strong, basic attack (sleeps with Silver Harp)
	golem = MonsterAI(24, "Golem", 153, 153, 0, 0, 120, 60)
	golem.behavior_rules = [
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.3, description="30% devastating attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(golem)

	# Goldman (25) - Strong attacks
	goldman = MonsterAI(25, "Goldman", 60, 60, 0, 0, 80, 70)
	goldman.behavior_rules = [
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.25, description="25% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(goldman)

	# Knight (26) - Strong attacks
	knight = MonsterAI(26, "Knight", 76, 76, 0, 0, 78, 68)
	knight.behavior_rules = [
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.25, description="25% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(knight)

	# Magiwyvern (27) - Fire breath and Stopspell
	magiwyvern = MonsterAI(27, "Magiwyvern", 78, 78, 12, 12, 78, 70)
	magiwyvern.behavior_rules = [
		AIBehaviorRule(25, AICondition.ALWAYS, AIAction.FIRE_BREATH, 0.4, description="40% fire breath"),
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.STOPSPELL_SPELL, 0.3, mp_cost=2, description="30% Stopspell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(magiwyvern)

	# Demon Knight (28) - Sleep and strong attacks
	demon_knight = MonsterAI(28, "Demon Knight", 80, 80, 10, 10, 82, 75)
	demon_knight.behavior_rules = [
		AIBehaviorRule(25, AICondition.MP_AVAILABLE, AIAction.SLEEP_SPELL, 0.35, mp_cost=2, description="35% Sleep spell"),
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.3, description="30% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(demon_knight)

	# Werewolf (29) - Fast, strong attacks
	werewolf = MonsterAI(29, "Werewolf", 86, 86, 0, 0, 86, 90)
	werewolf.behavior_rules = [
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.3, description="30% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(werewolf)

	# Green Dragon (30) - Fire breath frequently
	green_dragon = MonsterAI(30, "Green Dragon", 88, 88, 0, 0, 88, 58)
	green_dragon.behavior_rules = [
		AIBehaviorRule(20, AICondition.ALWAYS, AIAction.FIRE_BREATH, 0.5, description="50% fire breath"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(green_dragon)

	# Starwyvern (31) - Fire breath and Stopspell
	starwyvern = MonsterAI(31, "Starwyvern", 86, 86, 16, 16, 90, 80)
	starwyvern.behavior_rules = [
		AIBehaviorRule(25, AICondition.ALWAYS, AIAction.FIRE_BREATH, 0.45, description="45% fire breath"),
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.STOPSPELL_SPELL, 0.3, mp_cost=2, description="30% Stopspell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(starwyvern)

	# Wizard (32) - Hurtmore and other spells
	wizard = MonsterAI(32, "Wizard", 80, 80, 30, 30, 80, 70)
	wizard.behavior_rules = [
		AIBehaviorRule(30, AICondition.PLAYER_HP_HIGH | AICondition.MP_AVAILABLE, AIAction.HURTMORE_SPELL, 0.4, mp_cost=5, description="40% Hurtmore when player HP high"),
		AIBehaviorRule(20, AICondition.MP_AVAILABLE, AIAction.HURT_SPELL, 0.3, mp_cost=2, description="30% Hurt spell"),
		AIBehaviorRule(15, AICondition.MP_AVAILABLE, AIAction.SLEEP_SPELL, 0.25, mp_cost=2, description="25% Sleep spell"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(wizard)

	# Axe Knight (33) - Very strong attacks
	axe_knight = MonsterAI(33, "Axe Knight", 94, 94, 0, 0, 94, 78)
	axe_knight.behavior_rules = [
		AIBehaviorRule(20, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.35, description="35% devastating attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(axe_knight)

	# Blue Dragon (34) - Fire breath and strong attacks
	blue_dragon = MonsterAI(34, "Blue Dragon", 98, 98, 0, 0, 98, 84)
	blue_dragon.behavior_rules = [
		AIBehaviorRule(25, AICondition.ALWAYS, AIAction.FIRE_BREATH, 0.5, description="50% fire breath"),
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.3, description="30% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(blue_dragon)

	# Stoneman (35) - Very tough, strong attacks
	stoneman = MonsterAI(35, "Stoneman", 106, 106, 0, 0, 100, 53)
	stoneman.behavior_rules = [
		AIBehaviorRule(20, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.35, description="35% crushing attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(stoneman)

	# Armored Knight (36) - Strongest regular enemy
	armored_knight = MonsterAI(36, "Armored Knight", 105, 105, 0, 0, 105, 86)
	armored_knight.behavior_rules = [
		AIBehaviorRule(25, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.4, description="40% devastating attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(armored_knight)

	# Red Dragon (37) - Fire breath master
	red_dragon = MonsterAI(37, "Red Dragon", 120, 120, 0, 0, 120, 90)
	red_dragon.behavior_rules = [
		AIBehaviorRule(30, AICondition.ALWAYS, AIAction.FIRE_BREATH, 0.6, description="60% fire breath"),
		AIBehaviorRule(15, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.3, description="30% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(red_dragon)

	# Dragonlord Form 1 (38) - Boss with multiple spells
	dragonlord_1 = MonsterAI(38, "Dragonlord", 100, 100, 50, 50, 90, 75)
	dragonlord_1.behavior_rules = [
		AIBehaviorRule(40, AICondition.HP_LOW | AICondition.MP_AVAILABLE, AIAction.HEAL_SPELL, 0.8, mp_cost=4, description="80% Heal when HP low"),
		AIBehaviorRule(35, AICondition.PLAYER_HP_HIGH | AICondition.MP_AVAILABLE, AIAction.HURTMORE_SPELL, 0.5, mp_cost=5, description="50% Hurtmore when player HP high"),
		AIBehaviorRule(30, AICondition.MP_AVAILABLE, AIAction.STOPSPELL_SPELL, 0.3, mp_cost=2, description="30% Stopspell"),
		AIBehaviorRule(25, AICondition.MP_AVAILABLE, AIAction.SLEEP_SPELL, 0.3, mp_cost=2, description="30% Sleep spell"),
		AIBehaviorRule(20, AICondition.ALWAYS, AIAction.STRONG_ATTACK, 0.3, description="30% strong attack"),
		AIBehaviorRule(10, AICondition.ALWAYS, AIAction.ATTACK, 1.0, description="Default attack")
	]
	monsters.append(dragonlord_1)

	return monsters


class AISimulator:
	"""Simulate AI behavior in battles."""

	def __init__(self):
		self.monsters = create_default_monster_ai()

	def simulate_battle(self, monster_id: int, player_level: int = 10, num_turns: int = 10) -> List[Dict]:
		"""Simulate a battle with a monster."""
		if monster_id >= len(self.monsters):
			raise ValueError(f"Invalid monster ID: {monster_id}")

		monster = self.monsters[monster_id]

		# Create battle state
		battle_state = BattleState(
			player_hp=100,
			player_max_hp=100,
			player_mp=50,
			player_max_mp=50,
			player_attack=player_level * 2,
			player_defense=player_level * 2
		)

		# Reset monster HP/MP
		monster.current_hp = monster.max_hp
		monster.current_mp = monster.max_mp

		battle_log = []

		for turn in range(1, num_turns + 1):
			battle_state.turn_count = turn

			# Monster chooses action
			action, reason = monster.choose_action(battle_state)

			# Simulate action
			result = monster.simulate_action(action, battle_state)

			battle_log.append({
				'turn': turn,
				'monster_hp': f"{monster.current_hp}/{monster.max_hp}",
				'monster_mp': f"{monster.current_mp}/{monster.max_mp}",
				'action': AIAction(action).name,
				'reason': reason,
				'result': result['effect'],
				'damage': result['damage'],
				'success': result['success']
			})

			# Apply damage to player
			battle_state.player_hp -= result['damage']

			if battle_state.player_hp <= 0:
				battle_log.append({'event': 'Player defeated!'})
				break

		return battle_log


class InteractiveAIEditor:
	"""Interactive AI editor interface."""

	def __init__(self, rom_path: Path):
		self.rom_path = rom_path
		self.monsters = create_default_monster_ai()
		self.simulator = AISimulator()
		self.current_monster: Optional[MonsterAI] = None
		self.modified = False

	def run(self) -> None:
		"""Run interactive editor."""
		print("\n" + "="*70)
		print("Dragon Warrior Enemy AI Editor")
		print("="*70)

		while True:
			self._print_menu()
			choice = input("\nEnter choice: ").strip()

			if choice == '1':
				self._list_monsters()
			elif choice == '2':
				self._load_monster()
			elif choice == '3':
				self._display_ai()
			elif choice == '4':
				self._edit_rule()
			elif choice == '5':
				self._add_rule()
			elif choice == '6':
				self._remove_rule()
			elif choice == '7':
				self._simulate_battle()
			elif choice == '8':
				self._export_all()
			elif choice == 'q':
				break
			else:
				print("Invalid choice")

	def _print_menu(self) -> None:
		"""Print main menu."""
		print("\n" + "-"*70)
		print("Menu:")
		print("  1. List all monsters")
		print("  2. Load monster AI")
		print("  3. Display current AI rules")
		print("  4. Edit AI rule")
		print("  5. Add AI rule")
		print("  6. Remove AI rule")
		print("  7. Simulate battle")
		print("  8. Export all AI to JSON")
		print("  q. Quit")

		if self.current_monster:
			print(f"\nCurrent Monster: {self.current_monster.monster_name}")

	def _list_monsters(self) -> None:
		"""List all monsters."""
		print("\n" + "="*70)
		print("All Monsters")
		print("="*70)

		for monster in self.monsters:
			print(f"{monster.monster_id:2d}. {monster.monster_name:20s} (HP: {monster.max_hp:3d}, ATK: {monster.base_attack:3d}, Rules: {len(monster.behavior_rules)})")

	def _load_monster(self) -> None:
		"""Load a monster's AI."""
		monster_id = input("Enter monster ID (0-38): ").strip()

		try:
			monster_id = int(monster_id)
			if 0 <= monster_id < len(self.monsters):
				self.current_monster = self.monsters[monster_id]
				print(f"Loaded: {self.current_monster.monster_name}")
			else:
				print("Invalid monster ID")
		except ValueError:
			print("Invalid input")

	def _display_ai(self) -> None:
		"""Display current monster's AI rules."""
		if not self.current_monster:
			print("No monster loaded")
			return

		print(f"\n{'='*70}")
		print(f"AI Rules for {self.current_monster.monster_name}")
		print(f"{'='*70}")

		for i, rule in enumerate(self.current_monster.behavior_rules):
			print(f"\nRule {i}:")
			print(f"  Priority: {rule.priority}")
			print(f"  Condition: {rule.condition}")
			print(f"  Action: {AIAction(rule.action).name}")
			print(f"  Probability: {rule.action_probability * 100:.0f}%")
			print(f"  MP Cost: {rule.mp_cost}")
			print(f"  Description: {rule.description}")

	def _edit_rule(self) -> None:
		"""Edit an existing AI rule."""
		if not self.current_monster:
			print("No monster loaded")
			return

		self._display_ai()

		rule_idx = input("\nEnter rule number to edit: ").strip()

		try:
			rule_idx = int(rule_idx)
			if 0 <= rule_idx < len(self.current_monster.behavior_rules):
				rule = self.current_monster.behavior_rules[rule_idx]

				print("\nCurrent rule:")
				print(f"  Action: {AIAction(rule.action).name}")
				print(f"  Probability: {rule.action_probability * 100:.0f}%")

				new_prob = input("Enter new probability (0-100): ").strip()
				if new_prob:
					try:
						rule.action_probability = float(new_prob) / 100.0
						self.modified = True
						print("Rule updated")
					except ValueError:
						print("Invalid probability")
			else:
				print("Invalid rule number")
		except ValueError:
			print("Invalid input")

	def _add_rule(self) -> None:
		"""Add a new AI rule."""
		if not self.current_monster:
			print("No monster loaded")
			return

		print("\nAdd New AI Rule")
		print("Actions:", ", ".join(f"{i}={a.name}" for i, a in enumerate(AIAction)))

		# Simplified rule creation
		action_id = input("Enter action ID: ").strip()
		probability = input("Enter probability (0-100): ").strip()

		try:
			action = AIAction(int(action_id))
			prob = float(probability) / 100.0

			new_rule = AIBehaviorRule(
				priority=50,
				condition=AICondition.ALWAYS,
				action=action,
				action_probability=prob,
				description=f"Custom {action.name} rule"
			)

			self.current_monster.behavior_rules.append(new_rule)
			self.modified = True
			print("Rule added")
		except (ValueError, KeyError):
			print("Invalid input")

	def _remove_rule(self) -> None:
		"""Remove an AI rule."""
		if not self.current_monster:
			print("No monster loaded")
			return

		self._display_ai()

		rule_idx = input("\nEnter rule number to remove: ").strip()

		try:
			rule_idx = int(rule_idx)
			if 0 <= rule_idx < len(self.current_monster.behavior_rules):
				removed = self.current_monster.behavior_rules.pop(rule_idx)
				self.modified = True
				print(f"Removed rule: {removed.description}")
			else:
				print("Invalid rule number")
		except ValueError:
			print("Invalid input")

	def _simulate_battle(self) -> None:
		"""Simulate a battle with current monster."""
		if not self.current_monster:
			print("No monster loaded")
			return

		print(f"\nSimulating battle with {self.current_monster.monster_name}...")

		battle_log = self.simulator.simulate_battle(self.current_monster.monster_id, player_level=15, num_turns=10)

		print("\nBattle Log:")
		for entry in battle_log:
			if 'turn' in entry:
				print(f"\nTurn {entry['turn']}:")
				print(f"  Monster: {entry['monster_hp']} HP, {entry['monster_mp']} MP")
				print(f"  Action: {entry['action']} ({entry['reason']})")
				print(f"  Result: {entry['result']}")
			elif 'event' in entry:
				print(f"\n{entry['event']}")

	def _export_all(self) -> None:
		"""Export all monster AI to JSON."""
		output_path = Path("output/monster_ai.json")
		output_path.parent.mkdir(exist_ok=True, parents=True)

		data = {
			'version': '1.0',
			'monsters': [monster.to_dict() for monster in self.monsters]
		}

		with output_path.open('w') as f:
			json.dump(data, f, indent='\t')

		print(f"Exported AI data to {output_path}")
		self.modified = False


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Dragon Warrior Enemy AI Behavior Editor'
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
		'--simulate',
		type=int,
		metavar='MONSTER_ID',
		help='Simulate battle with monster ID'
	)

	parser.add_argument(
		'--export',
		type=Path,
		metavar='OUTPUT',
		help='Export all AI to JSON file'
	)

	args = parser.parse_args()

	if args.interactive or (args.rom_path and not args.simulate and not args.export):
		if not args.rom_path:
			parser.error("ROM path required for interactive mode")

		editor = InteractiveAIEditor(args.rom_path)
		editor.run()

	elif args.simulate is not None:
		simulator = AISimulator()
		battle_log = simulator.simulate_battle(args.simulate, player_level=15, num_turns=10)

		print(json.dumps(battle_log, indent=2))

	elif args.export:
		monsters = create_default_monster_ai()
		data = {
			'version': '1.0',
			'monsters': [monster.to_dict() for monster in monsters]
		}

		args.export.parent.mkdir(exist_ok=True, parents=True)
		with args.export.open('w') as f:
			json.dump(data, f, indent='\t')

		print(f"Exported AI data to {args.export}")

	else:
		parser.print_help()

	return 0


if __name__ == '__main__':
	exit(main())
