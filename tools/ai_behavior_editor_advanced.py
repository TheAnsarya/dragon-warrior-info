#!/usr/bin/env python3
"""
AI and Behavior Editor for Dragon Warrior

Comprehensive AI system for monsters, NPCs, and bosses with behavior trees,
state machines, decision logic, and combat tactics.

Features:
- Monster AI behavior editing
- NPC movement patterns and schedules
- Boss battle tactics and phases
- Behavior tree editor
- State machine designer
- Decision tree logic
- Combat action priorities
- Spell usage patterns
- AI testing and simulation
- Behavior templates
- Difficulty balancing
- AI performance metrics

Usage:
	python tools/ai_behavior_editor_advanced.py [ROM_FILE]

Examples:
	# Interactive editor
	python tools/ai_behavior_editor_advanced.py roms/dragon_warrior.nes

	# Export AI data
	python tools/ai_behavior_editor_advanced.py roms/dragon_warrior.nes --export ai_data.json

	# Simulate battle
	python tools/ai_behavior_editor_advanced.py --simulate monster_id player_level

	# Test AI behavior
	python tools/ai_behavior_editor_advanced.py --test ai_data.json

Author: Dragon Warrior ROM Hacking Toolkit
Version: 2.0
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
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import argparse


# ============================================================================
# AI DATA STRUCTURES
# ============================================================================

class AIState(Enum):
	"""AI state machine states."""
	IDLE = "idle"
	PATROL = "patrol"
	CHASE = "chase"
	ATTACK = "attack"
	FLEE = "flee"
	DEFEND = "defend"
	CAST_SPELL = "cast_spell"
	USE_ITEM = "use_item"
	DEAD = "dead"


class ActionType(Enum):
	"""Combat action types."""
	PHYSICAL_ATTACK = "physical_attack"
	MAGIC_ATTACK = "magic_attack"
	HEAL = "heal"
	BUFF = "buff"
	DEBUFF = "debuff"
	DEFEND = "defend"
	FLEE = "flee"
	SPECIAL = "special"


class ConditionType(Enum):
	"""AI condition types."""
	HP_BELOW = "hp_below"
	HP_ABOVE = "hp_above"
	MP_BELOW = "mp_below"
	MP_ABOVE = "mp_above"
	ENEMY_HP_BELOW = "enemy_hp_below"
	ENEMY_HP_ABOVE = "enemy_hp_above"
	TURN_NUMBER = "turn_number"
	RANDOM_CHANCE = "random_chance"
	ALWAYS = "always"


@dataclass
class AICondition:
	"""AI decision condition."""
	type: ConditionType
	value: float
	negate: bool = False

	def evaluate(self, context: Dict[str, Any]) -> bool:
		"""Evaluate condition against context."""
		result = False

		if self.type == ConditionType.ALWAYS:
			result = True

		elif self.type == ConditionType.HP_BELOW:
			current_hp = context.get('current_hp', 0)
			max_hp = context.get('max_hp', 1)
			hp_percent = (current_hp / max_hp) * 100
			result = hp_percent < self.value

		elif self.type == ConditionType.HP_ABOVE:
			current_hp = context.get('current_hp', 0)
			max_hp = context.get('max_hp', 1)
			hp_percent = (current_hp / max_hp) * 100
			result = hp_percent > self.value

		elif self.type == ConditionType.MP_BELOW:
			current_mp = context.get('current_mp', 0)
			max_mp = context.get('max_mp', 1)
			mp_percent = (current_mp / max_mp) * 100
			result = mp_percent < self.value

		elif self.type == ConditionType.ENEMY_HP_BELOW:
			enemy_hp = context.get('enemy_current_hp', 0)
			enemy_max_hp = context.get('enemy_max_hp', 1)
			hp_percent = (enemy_hp / enemy_max_hp) * 100
			result = hp_percent < self.value

		elif self.type == ConditionType.TURN_NUMBER:
			turn = context.get('turn', 1)
			result = turn >= int(self.value)

		elif self.type == ConditionType.RANDOM_CHANCE:
			result = random.random() * 100 < self.value

		if self.negate:
			result = not result

		return result


@dataclass
class AIAction:
	"""AI action definition."""
	id: int
	type: ActionType
	name: str
	description: str
	priority: int = 10  # Higher = more important
	conditions: List[AICondition] = field(default_factory=list)
	target_self: bool = False
	spell_id: Optional[int] = None
	item_id: Optional[int] = None
	damage_multiplier: float = 1.0
	mp_cost: int = 0
	cooldown: int = 0

	def can_execute(self, context: Dict[str, Any]) -> bool:
		"""Check if action can be executed."""
		# Check all conditions
		for condition in self.conditions:
			if not condition.evaluate(context):
				return False

		# Check MP cost
		if self.mp_cost > 0:
			current_mp = context.get('current_mp', 0)
			if current_mp < self.mp_cost:
				return False

		# Check cooldown
		if self.cooldown > 0:
			last_used = context.get(f'action_{self.id}_last_used', -999)
			current_turn = context.get('turn', 0)
			if current_turn - last_used < self.cooldown:
				return False

		return True


@dataclass
class BehaviorRule:
	"""Behavior rule (condition -> action)."""
	id: int
	name: str
	conditions: List[AICondition]
	action_id: int
	priority: int = 10
	enabled: bool = True

	def matches(self, context: Dict[str, Any]) -> bool:
		"""Check if rule matches context."""
		if not self.enabled:
			return False

		for condition in self.conditions:
			if not condition.evaluate(context):
				return False

		return True


@dataclass
class AIBehavior:
	"""Complete AI behavior definition."""
	id: int
	name: str
	description: str
	monster_id: int
	actions: List[AIAction] = field(default_factory=list)
	rules: List[BehaviorRule] = field(default_factory=list)
	default_action_id: int = 0
	aggression: int = 50  # 0-100 (0=passive, 100=aggressive)
	intelligence: int = 50  # 0-100 (0=random, 100=optimal)
	courage: int = 50  # 0-100 (0=cowardly, 100=brave)

	def get_action(self, action_id: int) -> Optional[AIAction]:
		"""Get action by ID."""
		for action in self.actions:
			if action.id == action_id:
				return action
		return None

	def select_action(self, context: Dict[str, Any]) -> Optional[AIAction]:
		"""Select best action for current context."""
		# Apply intelligence modifier to randomness
		intelligence_factor = self.intelligence / 100.0

		# Find matching rules
		matching_rules = []
		for rule in self.rules:
			if rule.matches(context):
				matching_rules.append(rule)

		# Sort by priority
		matching_rules.sort(key=lambda r: r.priority, reverse=True)

		# Try to execute highest priority matching rule
		for rule in matching_rules:
			action = self.get_action(rule.action_id)
			if action and action.can_execute(context):
				# Intelligence affects whether we use optimal action
				if random.random() < intelligence_factor:
					return action

		# No matching rule - use default action
		default_action = self.get_action(self.default_action_id)
		if default_action and default_action.can_execute(context):
			return default_action

		# Find any executable action
		executable_actions = [a for a in self.actions if a.can_execute(context)]

		if executable_actions:
			# Sort by priority
			executable_actions.sort(key=lambda a: a.priority, reverse=True)

			# Pick action based on intelligence
			if random.random() < intelligence_factor:
				return executable_actions[0]  # Best action
			else:
				return random.choice(executable_actions)  # Random action

		return None


@dataclass
class NPCSchedule:
	"""NPC movement and behavior schedule."""
	npc_id: int
	name: str
	waypoints: List[Tuple[int, int]] = field(default_factory=list)  # (x, y) positions
	speed: int = 1  # Tiles per update
	loop: bool = True
	pause_duration: int = 60  # Frames to pause at each waypoint
	dialogue_id: Optional[int] = None
	active_hours: Tuple[int, int] = (0, 23)  # Hour range when NPC is active


@dataclass
class BossPhase:
	"""Boss battle phase."""
	id: int
	name: str
	hp_threshold: float  # Percentage of max HP to trigger phase
	behavior_id: int
	dialogue: Optional[str] = None
	special_effect: Optional[str] = None


@dataclass
class BossAI:
	"""Boss monster AI with phases."""
	monster_id: int
	name: str
	phases: List[BossPhase] = field(default_factory=list)
	current_phase: int = 0
	enrage_threshold: float = 25.0  # HP % to enrage

	def get_current_phase(self, hp_percent: float) -> BossPhase:
		"""Get current boss phase based on HP."""
		for phase in sorted(self.phases, key=lambda p: p.hp_threshold):
			if hp_percent <= phase.hp_threshold:
				return phase

		# Return first phase if no threshold met
		return self.phases[0] if self.phases else None


# ============================================================================
# AI BEHAVIOR LIBRARY
# ============================================================================

class AIBehaviorLibrary:
	"""Library of pre-defined AI behaviors."""

	@staticmethod
	def create_basic_melee() -> AIBehavior:
		"""Create basic melee attacker AI."""
		behavior = AIBehavior(
			id=1,
			name="Basic Melee",
			description="Simple physical attacker",
			monster_id=0,
			aggression=75,
			intelligence=30,
			courage=60
		)

		# Physical attack action
		attack = AIAction(
			id=1,
			type=ActionType.PHYSICAL_ATTACK,
			name="Attack",
			description="Basic physical attack",
			priority=10,
			conditions=[AICondition(ConditionType.ALWAYS, 0)]
		)
		behavior.actions.append(attack)
		behavior.default_action_id = 1

		return behavior

	@staticmethod
	def create_spellcaster() -> AIBehavior:
		"""Create spellcaster AI."""
		behavior = AIBehavior(
			id=2,
			name="Spellcaster",
			description="Prefers magic attacks",
			monster_id=0,
			aggression=60,
			intelligence=70,
			courage=40
		)

		# Offensive spell
		spell = AIAction(
			id=1,
			type=ActionType.MAGIC_ATTACK,
			name="Fire Spell",
			description="Cast offensive spell",
			priority=15,
			mp_cost=5,
			conditions=[
				AICondition(ConditionType.MP_ABOVE, 20)
			],
			spell_id=1
		)
		behavior.actions.append(spell)

		# Physical attack fallback
		attack = AIAction(
			id=2,
			type=ActionType.PHYSICAL_ATTACK,
			name="Attack",
			description="Physical attack when low MP",
			priority=5
		)
		behavior.actions.append(attack)

		behavior.default_action_id = 2

		return behavior

	@staticmethod
	def create_healer() -> AIBehavior:
		"""Create healer AI."""
		behavior = AIBehavior(
			id=3,
			name="Healer",
			description="Heals when HP is low",
			monster_id=0,
			aggression=40,
			intelligence=80,
			courage=30
		)

		# Heal spell (high priority when hurt)
		heal = AIAction(
			id=1,
			type=ActionType.HEAL,
			name="Heal",
			description="Restore HP",
			priority=20,
			mp_cost=4,
			target_self=True,
			conditions=[
				AICondition(ConditionType.HP_BELOW, 50),
				AICondition(ConditionType.MP_ABOVE, 15)
			],
			spell_id=2
		)
		behavior.actions.append(heal)

		# Attack
		attack = AIAction(
			id=2,
			type=ActionType.PHYSICAL_ATTACK,
			name="Attack",
			description="Physical attack",
			priority=5
		)
		behavior.actions.append(attack)

		behavior.default_action_id = 2

		return behavior

	@staticmethod
	def create_tactical() -> AIBehavior:
		"""Create tactical AI with multiple strategies."""
		behavior = AIBehavior(
			id=4,
			name="Tactical",
			description="Uses different tactics based on situation",
			monster_id=0,
			aggression=65,
			intelligence=85,
			courage=70
		)

		# Strong attack when enemy is weak
		strong_attack = AIAction(
			id=1,
			type=ActionType.PHYSICAL_ATTACK,
			name="Power Attack",
			description="Strong attack to finish weak enemy",
			priority=18,
			damage_multiplier=1.5,
			mp_cost=3,
			conditions=[
				AICondition(ConditionType.ENEMY_HP_BELOW, 30),
				AICondition(ConditionType.MP_ABOVE, 10)
			]
		)
		behavior.actions.append(strong_attack)

		# Defend when low HP
		defend = AIAction(
			id=2,
			type=ActionType.DEFEND,
			name="Defend",
			description="Defensive stance when hurt",
			priority=15,
			target_self=True,
			conditions=[
				AICondition(ConditionType.HP_BELOW, 40)
			]
		)
		behavior.actions.append(defend)

		# Normal attack
		attack = AIAction(
			id=3,
			type=ActionType.PHYSICAL_ATTACK,
			name="Attack",
			description="Normal attack",
			priority=10
		)
		behavior.actions.append(attack)

		behavior.default_action_id = 3

		return behavior


# ============================================================================
# AI SIMULATOR
# ============================================================================

class BattleSimulator:
	"""Simulate battle for AI testing."""

	def __init__(self):
		self.turn = 0
		self.log: List[str] = []

	def simulate_battle(self, monster: Dict, player: Dict,
					   ai_behavior: AIBehavior, max_turns: int = 50) -> Dict:
		"""Simulate a battle."""
		self.turn = 0
		self.log = []

		monster_hp = monster['hp']
		monster_mp = monster.get('mp', 0)
		player_hp = player['hp']

		self.log.append(f"Battle Start: {monster['name']} vs Hero")
		self.log.append(f"Monster HP: {monster_hp}, Player HP: {player_hp}")

		while self.turn < max_turns:
			self.turn += 1
			self.log.append(f"\n--- Turn {self.turn} ---")

			# Build AI context
			context = {
				'turn': self.turn,
				'current_hp': monster_hp,
				'max_hp': monster['hp'],
				'current_mp': monster_mp,
				'max_mp': monster.get('mp', 0),
				'enemy_current_hp': player_hp,
				'enemy_max_hp': player['hp']
			}

			# Monster turn
			action = ai_behavior.select_action(context)

			if action:
				self.log.append(f"Monster uses: {action.name}")

				if action.type == ActionType.PHYSICAL_ATTACK:
					damage = int(monster['attack'] * action.damage_multiplier)
					player_hp -= damage
					self.log.append(f"  Deals {damage} damage to player")

				elif action.type == ActionType.MAGIC_ATTACK:
					damage = int(monster['attack'] * 0.8 * action.damage_multiplier)
					player_hp -= damage
					monster_mp -= action.mp_cost
					self.log.append(f"  Spell deals {damage} damage to player")

				elif action.type == ActionType.HEAL:
					heal_amount = int(monster['hp'] * 0.3)
					monster_hp = min(monster_hp + heal_amount, monster['hp'])
					monster_mp -= action.mp_cost
					self.log.append(f"  Heals {heal_amount} HP")

				elif action.type == ActionType.DEFEND:
					self.log.append(f"  Takes defensive stance")

				# Update context for cooldown tracking
				context[f'action_{action.id}_last_used'] = self.turn

			# Check if player defeated
			if player_hp <= 0:
				self.log.append("\nPlayer defeated!")
				return {
					'winner': 'monster',
					'turns': self.turn,
					'log': self.log,
					'monster_hp_remaining': monster_hp
				}

			# Player turn (simplified)
			player_damage = player['attack']
			monster_hp -= player_damage
			self.log.append(f"Player attacks for {player_damage} damage")

			# Check if monster defeated
			if monster_hp <= 0:
				self.log.append("\nMonster defeated!")
				return {
					'winner': 'player',
					'turns': self.turn,
					'log': self.log,
					'player_hp_remaining': player_hp
				}

		self.log.append("\nBattle timeout - draw")
		return {
			'winner': 'draw',
			'turns': self.turn,
			'log': self.log
		}


# ============================================================================
# AI EDITOR
# ============================================================================

class AIBehaviorEditor:
	"""AI behavior editor."""

	def __init__(self):
		self.behaviors: Dict[int, AIBehavior] = {}
		self.npc_schedules: Dict[int, NPCSchedule] = {}
		self.boss_ais: Dict[int, BossAI] = {}
		self.library = AIBehaviorLibrary()

	def load_from_file(self, filepath: Path):
		"""Load AI data from JSON."""
		with open(filepath, 'r') as f:
			data = json.load(f)

		# Load behaviors
		for b_data in data.get('behaviors', []):
			behavior = AIBehavior(
				id=b_data['id'],
				name=b_data['name'],
				description=b_data['description'],
				monster_id=b_data['monster_id'],
				aggression=b_data.get('aggression', 50),
				intelligence=b_data.get('intelligence', 50),
				courage=b_data.get('courage', 50),
				default_action_id=b_data.get('default_action_id', 0)
			)

			# Load actions
			for a_data in b_data.get('actions', []):
				action = AIAction(
					id=a_data['id'],
					type=ActionType(a_data['type']),
					name=a_data['name'],
					description=a_data['description'],
					priority=a_data.get('priority', 10),
					mp_cost=a_data.get('mp_cost', 0),
					damage_multiplier=a_data.get('damage_multiplier', 1.0)
				)

				# Load conditions
				for c_data in a_data.get('conditions', []):
					condition = AICondition(
						type=ConditionType(c_data['type']),
						value=c_data['value'],
						negate=c_data.get('negate', False)
					)
					action.conditions.append(condition)

				behavior.actions.append(action)

			self.behaviors[behavior.id] = behavior

	def save_to_file(self, filepath: Path):
		"""Save AI data to JSON."""
		data = {
			'behaviors': [asdict(b) for b in self.behaviors.values()],
			'npc_schedules': [asdict(s) for s in self.npc_schedules.values()],
			'boss_ais': [asdict(b) for b in self.boss_ais.values()]
		}

		with open(filepath, 'w') as f:
			json.dump(data, f, indent=2)

	def add_behavior(self, behavior: AIBehavior):
		"""Add behavior to editor."""
		self.behaviors[behavior.id] = behavior

	def get_behavior_stats(self, behavior: AIBehavior) -> Dict:
		"""Get statistics about behavior."""
		return {
			'name': behavior.name,
			'num_actions': len(behavior.actions),
			'num_rules': len(behavior.rules),
			'aggression': behavior.aggression,
			'intelligence': behavior.intelligence,
			'courage': behavior.courage,
			'avg_action_priority': sum(a.priority for a in behavior.actions) / max(len(behavior.actions), 1)
		}


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="AI and Behavior Editor"
	)

	parser.add_argument('rom_file', nargs='?', help="ROM file to edit")
	parser.add_argument('--export', help="Export AI data to JSON")
	parser.add_argument('--import', dest='import_file', help="Import AI data from JSON")
	parser.add_argument('--simulate', nargs=2, metavar=('MONSTER_ID', 'PLAYER_LEVEL'),
					   help="Simulate battle")
	parser.add_argument('--template', choices=['melee', 'spellcaster', 'healer', 'tactical'],
					   help="Create AI from template")

	args = parser.parse_args()

	editor = AIBehaviorEditor()

	# Import from JSON
	if args.import_file:
		import_path = Path(args.import_file)
		if import_path.exists():
			editor.load_from_file(import_path)
			print(f"Loaded {len(editor.behaviors)} AI behaviors")

	# Create from template
	if args.template:
		if args.template == 'melee':
			behavior = editor.library.create_basic_melee()
		elif args.template == 'spellcaster':
			behavior = editor.library.create_spellcaster()
		elif args.template == 'healer':
			behavior = editor.library.create_healer()
		elif args.template == 'tactical':
			behavior = editor.library.create_tactical()

		editor.add_behavior(behavior)
		print(f"Created '{behavior.name}' behavior from template")

	# Export
	if args.export:
		export_path = Path(args.export)
		editor.save_to_file(export_path)
		print(f"Exported {len(editor.behaviors)} behaviors to {export_path}")

	# Simulate battle
	if args.simulate:
		monster_id = int(args.simulate[0])
		player_level = int(args.simulate[1])

		# Get behavior
		behavior = editor.behaviors.get(monster_id)

		if not behavior:
			# Use default melee
			behavior = editor.library.create_basic_melee()
			print("Using default melee AI")

		# Create test data
		monster = {
			'name': f'Monster {monster_id}',
			'hp': 50 + (monster_id * 10),
			'mp': 20,
			'attack': 10 + monster_id
		}

		player = {
			'hp': 30 + (player_level * 5),
			'attack': 8 + player_level
		}

		# Run simulation
		simulator = BattleSimulator()
		result = simulator.simulate_battle(monster, player, behavior)

		print("\nBattle Simulation Result:")
		print(f"Winner: {result['winner']}")
		print(f"Turns: {result['turns']}")

		print("\nBattle Log:")
		for line in result['log']:
			print(line)

	# Interactive mode
	if not any([args.export, args.simulate, args.template]):
		print("\n=== AI and Behavior Editor ===")
		print(f"Loaded {len(editor.behaviors)} behaviors")
		print("\nCommands:")
		print("  list      - List all behaviors")
		print("  view <id> - View behavior details")
		print("  stats <id> - Show behavior statistics")
		print("  quit      - Exit")

		while True:
			try:
				cmd = input("\n> ").strip().split()

				if not cmd:
					continue

				if cmd[0] == 'quit':
					break

				elif cmd[0] == 'list':
					for b_id, behavior in sorted(editor.behaviors.items()):
						print(f"  {b_id:3d}: {behavior.name} (Int:{behavior.intelligence}, Agg:{behavior.aggression})")

				elif cmd[0] == 'view' and len(cmd) > 1:
					b_id = int(cmd[1])
					behavior = editor.behaviors.get(b_id)

					if behavior:
						print(f"\nBehavior {b_id}: {behavior.name}")
						print(f"Description: {behavior.description}")
						print(f"Aggression: {behavior.aggression}")
						print(f"Intelligence: {behavior.intelligence}")
						print(f"Courage: {behavior.courage}")
						print(f"\nActions ({len(behavior.actions)}):")

						for action in behavior.actions:
							print(f"  [{action.id}] {action.name} (Priority: {action.priority})")
							print(f"      {action.description}")

				elif cmd[0] == 'stats' and len(cmd) > 1:
					b_id = int(cmd[1])
					behavior = editor.behaviors.get(b_id)

					if behavior:
						stats = editor.get_behavior_stats(behavior)
						print(f"\nBehavior Statistics:")
						for key, value in stats.items():
							print(f"  {key}: {value}")

			except (KeyboardInterrupt, EOFError):
				break
			except Exception as e:
				print(f"Error: {e}")

	return 0


if __name__ == "__main__":
	sys.exit(main())
