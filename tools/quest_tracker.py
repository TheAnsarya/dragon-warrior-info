#!/usr/bin/env python3
"""
Dragon Warrior Quest and Progression Tracker

Comprehensive quest tracking, progression analysis, and walkthrough generation system.
Features:
- Track all quests, items, and story progression
- Generate optimal walkthrough paths
- Analyze quest dependencies and unlock conditions
- Track item requirements and locations
- Calculate minimum level requirements
- Generate flowcharts and progression graphs
- Save/load game state for tracking
- Speedrun route optimization

Dragon Warrior Quest Structure:
- Main quest: Defeat Dragonlord
- Sub-quests: Rescue Gwaelin, Collect Erdrick's items, Rainbow Bridge
- Optional: Collect all items, max level, secret treasures

Author: Dragon Warrior Toolkit
Date: 2024-11-26
"""

import argparse
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Set, Tuple
from enum import IntEnum, auto
from collections import defaultdict


class QuestStatus(IntEnum):
	"""Quest completion status."""
	NOT_STARTED = 0
	IN_PROGRESS = 1
	COMPLETED = 2
	FAILED = 3


class ItemRarity(IntEnum):
	"""Item rarity levels."""
	COMMON = 0      # Can be bought
	UNCOMMON = 1    # Found in chests
	RARE = 2        # Quest reward
	LEGENDARY = 3   # Erdrick's equipment


@dataclass
class QuestItem:
	"""An item needed for or rewarded by a quest."""
	id: int
	name: str
	location: str
	rarity: ItemRarity
	required_for: List[str] = field(default_factory=list)  # Quest names
	unlocks: List[str] = field(default_factory=list)        # What it unlocks
	description: str = ""

	def to_dict(self) -> dict:
		return {
			'id': self.id,
			'name': self.name,
			'location': self.location,
			'rarity': ItemRarity(self.rarity).name,
			'required_for': self.required_for,
			'unlocks': self.unlocks,
			'description': self.description
		}


@dataclass
class Quest:
	"""A quest or objective in Dragon Warrior."""
	id: int
	name: str
	description: str
	prerequisites: List[int] = field(default_factory=list)  # Quest IDs
	required_items: List[str] = field(default_factory=list)
	required_level: int = 1
	rewards: List[str] = field(default_factory=list)
	unlocks: List[int] = field(default_factory=list)  # Quest IDs
	optional: bool = False
	location: str = ""

	def to_dict(self) -> dict:
		return {
			'id': self.id,
			'name': self.name,
			'description': self.description,
			'prerequisites': self.prerequisites,
			'required_items': self.required_items,
			'required_level': self.required_level,
			'rewards': self.rewards,
			'unlocks': self.unlocks,
			'optional': self.optional,
			'location': self.location
		}


@dataclass
class ProgressionMilestone:
	"""A milestone in game progression."""
	level: int
	name: str
	suggested_quests: List[int]
	recommended_equipment: List[str]
	accessible_areas: List[str]
	description: str = ""

	def to_dict(self) -> dict:
		return {
			'level': self.level,
			'name': self.name,
			'suggested_quests': self.suggested_quests,
			'recommended_equipment': self.recommended_equipment,
			'accessible_areas': self.accessible_areas,
			'description': self.description
		}


# Dragon Warrior quest items
DW_QUEST_ITEMS = [
	QuestItem(0, "Gwaelin's Love", "Rescue Gwaelin", ItemRarity.RARE,
	         required_for=["Navigate to Charlock"],
	         unlocks=["Distance to Tantegel"],
	         description="Shows distance to Tantegel Castle"),

	QuestItem(1, "Stones of Sunlight", "Hauksness", ItemRarity.RARE,
	         required_for=["Create Rainbow Bridge"],
	         description="One of two items needed for Rainbow Bridge"),

	QuestItem(2, "Staff of Rain", "Kol", ItemRarity.RARE,
	         required_for=["Create Rainbow Bridge"],
	         description="One of two items needed for Rainbow Bridge"),

	QuestItem(3, "Rainbow Drop", "Rimuldar", ItemRarity.RARE,
	         required_for=["Cross to Charlock"],
	         unlocks=["Rainbow Bridge"],
	         description="Creates Rainbow Bridge to Charlock"),

	QuestItem(4, "Erdrick's Token", "Mountain Cave", ItemRarity.LEGENDARY,
	         required_for=["Get Erdrick's Armor"],
	         description="Proof of Erdrick's lineage"),

	QuestItem(5, "Erdrick's Armor", "Swamp Cave", ItemRarity.LEGENDARY,
	         required_for=["Final Battle"],
	         unlocks=["Damage resistance", "No damage zones"],
	         description="Best armor, damage reduction"),

	QuestItem(6, "Erdrick's Sword", "Charlock Castle", ItemRarity.LEGENDARY,
	         required_for=["Final Battle"],
	         unlocks=["Maximum attack power"],
	         description="Most powerful weapon"),

	QuestItem(7, "Silver Harp", "Garin's Grave", ItemRarity.RARE,
	         required_for=["Defeat Golem"],
	         unlocks=["Access to Charlock"],
	         description="Puts Golem to sleep"),

	QuestItem(8, "Magic Key", "Garinham", ItemRarity.UNCOMMON,
	         unlocks=["Magic doors", "Many treasure chests"],
	         description="Opens magic doors"),

	QuestItem(9, "Fairy Flute", "Rimuldar", ItemRarity.RARE,
	         unlocks=["Safe navigation"],
	         description="Puts monsters to sleep in field"),

	QuestItem(10, "Fighter's Ring", "Garinham", ItemRarity.UNCOMMON,
	          description="Increases attack power"),
]

# Create lookup dictionary
ITEMS_BY_NAME = {item.name: item for item in DW_QUEST_ITEMS}


# Dragon Warrior quests
DW_QUESTS = [
	Quest(0, "Speak with the King",
	      "Talk to King Lorik in Tantegel Castle",
	      required_level=1,
	      location="Tantegel Castle",
	      rewards=["Start main quest", "120 gold"],
	      unlocks=[1]),

	Quest(1, "Explore Brecconary",
	      "Visit the starting town and gather information",
	      prerequisites=[0],
	      location="Brecconary",
	      unlocks=[2, 3],
	      rewards=["Town knowledge", "Shop access"]),

	Quest(2, "Rescue Princess Gwaelin",
	      "Find and rescue the princess from the Green Dragon",
	      prerequisites=[1],
	      required_level=7,
	      location="Swamp Cave",
	      rewards=["Gwaelin's Love"],
	      unlocks=[10]),

	Quest(3, "Obtain Magic Key",
	      "Buy the Magic Key in Garinham",
	      prerequisites=[1],
	      location="Garinham",
	      required_items=[],
	      rewards=["Magic Key"],
	      unlocks=[4, 5, 6]),

	Quest(4, "Find Erdrick's Token",
	      "Retrieve Erdrick's Token from Mountain Cave",
	      prerequisites=[3],
	      required_level=10,
	      required_items=["Magic Key"],
	      location="Mountain Cave",
	      rewards=["Erdrick's Token"],
	      unlocks=[7]),

	Quest(5, "Obtain Silver Harp",
	      "Get the Silver Harp from Garin's Grave",
	      prerequisites=[3],
	      required_level=12,
	      required_items=["Magic Key"],
	      location="Garin's Grave",
	      rewards=["Silver Harp"],
	      unlocks=[8]),

	Quest(6, "Find Fighter's Ring",
	      "Locate the Fighter's Ring in Garinham",
	      prerequisites=[3],
	      required_items=["Magic Key"],
	      location="Garinham",
	      rewards=["Fighter's Ring"],
	      optional=True),

	Quest(7, "Get Erdrick's Armor",
	      "Retrieve Erdrick's Armor from Swamp Cave",
	      prerequisites=[4],
	      required_level=13,
	      required_items=["Magic Key", "Erdrick's Token"],
	      location="Swamp Cave",
	      rewards=["Erdrick's Armor"],
	      unlocks=[11]),

	Quest(8, "Defeat the Golem",
	      "Use Silver Harp to put Golem to sleep and pass",
	      prerequisites=[5],
	      required_level=15,
	      required_items=["Silver Harp"],
	      location="Cantlin area",
	      rewards=["Access to Charlock region"],
	      unlocks=[9]),

	Quest(9, "Collect Rainbow Bridge Items",
	      "Gather Stones of Sunlight and Staff of Rain",
	      prerequisites=[8],
	      required_level=16,
	      location="Hauksness and Kol",
	      rewards=["Stones of Sunlight", "Staff of Rain"],
	      unlocks=[10]),

	Quest(10, "Create Rainbow Bridge",
	       "Bring both items to Rimuldar to create Rainbow Drop",
	       prerequisites=[9],
	       required_items=["Stones of Sunlight", "Staff of Rain"],
	       location="Rimuldar",
	       rewards=["Rainbow Drop"],
	       unlocks=[12]),

	Quest(11, "Explore Charlock Castle",
	       "Enter Charlock and navigate to Erdrick's Sword",
	       prerequisites=[10],
	       required_level=18,
	       required_items=["Rainbow Drop", "Erdrick's Armor"],
	       location="Charlock Castle",
	       rewards=["Erdrick's Sword"],
	       unlocks=[13]),

	Quest(12, "Final Preparation",
	       "Level up and prepare for final battle",
	       prerequisites=[11],
	       required_level=20,
	       location="Training areas",
	       rewards=["High level stats"],
	       unlocks=[13]),

	Quest(13, "Defeat the Dragonlord",
	       "Battle the Dragonlord in his throne room",
	       prerequisites=[11, 12],
	       required_level=20,
	       required_items=["Erdrick's Sword", "Erdrick's Armor", "Rainbow Drop"],
	       location="Charlock Castle - Throne Room",
	       rewards=["Victory", "Ending"],
	       unlocks=[]),
]


# Progression milestones
DW_MILESTONES = [
	ProgressionMilestone(
		level=1,
		name="Humble Beginnings",
		suggested_quests=[0, 1],
		recommended_equipment=["Bamboo Pole", "Clothes"],
		accessible_areas=["Tantegel Castle", "Brecconary", "Tantegel area"],
		description="Start the adventure, explore starting area"
	),

	ProgressionMilestone(
		level=3,
		name="First Steps",
		suggested_quests=[],
		recommended_equipment=["Copper Sword", "Leather Armor"],
		accessible_areas=["Garinham", "Kol", "Southern regions"],
		description="Venture further from castle, explore new towns"
	),

	ProgressionMilestone(
		level=7,
		name="The Rescue",
		suggested_quests=[2],
		recommended_equipment=["Copper Sword", "Chain Mail", "Small Shield"],
		accessible_areas=["Swamp Cave"],
		description="Rescue Princess Gwaelin"
	),

	ProgressionMilestone(
		level=10,
		name="Key Acquisitions",
		suggested_quests=[3, 4],
		recommended_equipment=["Hand Axe", "Chain Mail", "Large Shield"],
		accessible_areas=["Magic door areas", "Mountain Cave"],
		description="Get Magic Key and Erdrick's Token"
	),

	ProgressionMilestone(
		level=13,
		name="Erdrick's Legacy",
		suggested_quests=[5, 7],
		recommended_equipment=["Broad Sword", "Half Plate", "Large Shield"],
		accessible_areas=["Garin's Grave", "Swamp Cave"],
		description="Collect Erdrick's Armor and Silver Harp"
	),

	ProgressionMilestone(
		level=17,
		name="Road to Charlock",
		suggested_quests=[8, 9, 10],
		recommended_equipment=["Flame Sword", "Full Plate", "Silver Shield"],
		accessible_areas=["Charlock region", "All towns"],
		description="Create Rainbow Bridge, prepare for Charlock"
	),

	ProgressionMilestone(
		level=20,
		name="Final Challenge",
		suggested_quests=[11, 12, 13],
		recommended_equipment=["Erdrick's Sword", "Erdrick's Armor", "Silver Shield"],
		accessible_areas=["Charlock Castle interior"],
		description="Final equipment, max level preparation"
	),
]


class QuestTracker:
	"""Track quest completion and progression."""

	def __init__(self):
		self.quests = {q.id: q for q in DW_QUESTS}
		self.items = {item.name: item for item in DW_QUEST_ITEMS}
		self.milestones = DW_MILESTONES

		# Tracking state
		self.quest_status: Dict[int, QuestStatus] = {}
		self.items_collected: Set[str] = set()
		self.current_level: int = 1

		# Initialize all quests as not started
		for quest_id in self.quests:
			self.quest_status[quest_id] = QuestStatus.NOT_STARTED

	def complete_quest(self, quest_id: int) -> None:
		"""Mark a quest as completed."""
		if quest_id in self.quests:
			self.quest_status[quest_id] = QuestStatus.COMPLETED

			# Add rewards to collected items
			quest = self.quests[quest_id]
			for reward in quest.rewards:
				if reward in self.items:
					self.items_collected.add(reward)

	def can_start_quest(self, quest_id: int) -> Tuple[bool, List[str]]:
		"""Check if a quest can be started (prerequisites met)."""
		if quest_id not in self.quests:
			return False, ["Quest does not exist"]

		quest = self.quests[quest_id]
		issues = []

		# Check prerequisites
		for prereq_id in quest.prerequisites:
			if self.quest_status.get(prereq_id) != QuestStatus.COMPLETED:
				prereq_name = self.quests[prereq_id].name
				issues.append(f"Must complete: {prereq_name}")

		# Check required items
		for item_name in quest.required_items:
			if item_name not in self.items_collected:
				issues.append(f"Need item: {item_name}")

		# Check level
		if self.current_level < quest.required_level:
			issues.append(f"Need level {quest.required_level} (current: {self.current_level})")

		return len(issues) == 0, issues

	def get_available_quests(self) -> List[Quest]:
		"""Get list of quests that can currently be started."""
		available = []

		for quest_id, quest in self.quests.items():
			if self.quest_status[quest_id] == QuestStatus.NOT_STARTED:
				can_start, _ = self.can_start_quest(quest_id)
				if can_start:
					available.append(quest)

		return available

	def get_next_recommended_quest(self) -> Optional[Quest]:
		"""Get the next recommended quest based on current progress."""
		available = self.get_available_quests()

		if not available:
			return None

		# Prioritize main story quests (non-optional)
		main_quests = [q for q in available if not q.optional]
		if main_quests:
			# Return the one with lowest ID (story order)
			return min(main_quests, key=lambda q: q.id)

		# Return any available optional quest
		return available[0] if available else None

	def get_progression_percentage(self) -> float:
		"""Calculate overall progression percentage."""
		total_quests = len([q for q in self.quests.values() if not q.optional])
		completed_quests = len([
			q_id for q_id, status in self.quest_status.items()
			if status == QuestStatus.COMPLETED and not self.quests[q_id].optional
		])

		return (completed_quests / total_quests * 100) if total_quests > 0 else 0

	def get_current_milestone(self) -> Optional[ProgressionMilestone]:
		"""Get the current progression milestone."""
		for milestone in reversed(self.milestones):
			if self.current_level >= milestone.level:
				return milestone
		return None

	def generate_walkthrough(self, include_optional: bool = False) -> List[Quest]:
		"""Generate an optimal quest order walkthrough."""
		walkthrough = []

		# Sort quests by ID (story order)
		sorted_quests = sorted(self.quests.values(), key=lambda q: q.id)

		if include_optional:
			walkthrough = sorted_quests
		else:
			walkthrough = [q for q in sorted_quests if not q.optional]

		return walkthrough

	def analyze_dependencies(self) -> Dict[int, List[int]]:
		"""Analyze quest dependency graph."""
		dependencies = {}

		for quest_id, quest in self.quests.items():
			dependencies[quest_id] = quest.prerequisites.copy()

		return dependencies

	def find_critical_path(self) -> List[Quest]:
		"""Find the critical path (minimum quests to beat game)."""
		# Work backwards from final quest
		final_quest_id = 13  # Defeat Dragonlord
		critical_quests = set()

		def add_prerequisites(quest_id: int) -> None:
			if quest_id in critical_quests:
				return

			critical_quests.add(quest_id)
			quest = self.quests[quest_id]

			for prereq_id in quest.prerequisites:
				add_prerequisites(prereq_id)

		add_prerequisites(final_quest_id)

		# Return in order
		return [self.quests[qid] for qid in sorted(critical_quests)]

	def export_state(self) -> Dict:
		"""Export current tracking state."""
		return {
			'current_level': self.current_level,
			'quest_status': {
				self.quests[qid].name: status.name
				for qid, status in self.quest_status.items()
			},
			'items_collected': list(self.items_collected),
			'progression_percentage': self.get_progression_percentage(),
			'available_quests': [q.name for q in self.get_available_quests()],
			'next_recommended': self.get_next_recommended_quest().name if self.get_next_recommended_quest() else None
		}

	def import_state(self, state: Dict) -> None:
		"""Import tracking state."""
		self.current_level = state.get('current_level', 1)
		self.items_collected = set(state.get('items_collected', []))

		# Import quest status
		for quest_id, quest in self.quests.items():
			status_name = state.get('quest_status', {}).get(quest.name, 'NOT_STARTED')
			self.quest_status[quest_id] = QuestStatus[status_name]


class WalkthroughGenerator:
	"""Generate detailed walkthroughs and guides."""

	def __init__(self):
		self.tracker = QuestTracker()

	def generate_text_walkthrough(self, output_path: Path, include_optional: bool = True) -> None:
		"""Generate a text walkthrough guide."""
		lines = []

		lines.append("="*70)
		lines.append("DRAGON WARRIOR COMPLETE WALKTHROUGH")
		lines.append("="*70)
		lines.append("")

		# Introduction
		lines.append("This walkthrough covers all main story quests and optional content.")
		lines.append("")

		# Milestones
		lines.append("PROGRESSION MILESTONES")
		lines.append("-"*70)
		for milestone in self.tracker.milestones:
			lines.append(f"\nLevel {milestone.level}: {milestone.name}")
			lines.append(f"  {milestone.description}")
			lines.append(f"  Equipment: {', '.join(milestone.recommended_equipment)}")
			lines.append(f"  Areas: {', '.join(milestone.accessible_areas)}")

		lines.append("\n" + "="*70)

		# Quest walkthrough
		lines.append("QUEST WALKTHROUGH")
		lines.append("-"*70)

		walkthrough = self.tracker.generate_walkthrough(include_optional)

		for i, quest in enumerate(walkthrough, 1):
			lines.append(f"\n{i}. {quest.name}")
			lines.append(f"   Location: {quest.location}")
			lines.append(f"   Required Level: {quest.required_level}")

			if quest.required_items:
				lines.append(f"   Required Items: {', '.join(quest.required_items)}")

			lines.append(f"   Description: {quest.description}")

			if quest.rewards:
				lines.append(f"   Rewards: {', '.join(quest.rewards)}")

			if quest.optional:
				lines.append("   [OPTIONAL]")

		# Critical path
		lines.append("\n" + "="*70)
		lines.append("CRITICAL PATH (Minimum to beat game)")
		lines.append("-"*70)

		critical = self.tracker.find_critical_path()
		for i, quest in enumerate(critical, 1):
			lines.append(f"{i}. {quest.name} (Level {quest.required_level})")

		# Item locations
		lines.append("\n" + "="*70)
		lines.append("IMPORTANT ITEM LOCATIONS")
		lines.append("-"*70)

		for item in sorted(DW_QUEST_ITEMS, key=lambda x: x.rarity, reverse=True):
			lines.append(f"\n{item.name} [{ItemRarity(item.rarity).name}]")
			lines.append(f"  Location: {item.location}")
			lines.append(f"  Description: {item.description}")
			if item.required_for:
				lines.append(f"  Required for: {', '.join(item.required_for)}")

		# Write to file
		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text('\n'.join(lines))

		print(f"Generated walkthrough: {output_path}")

	def generate_json_guide(self, output_path: Path) -> None:
		"""Generate a JSON guide data file."""
		data = {
			'version': '1.0',
			'quests': [q.to_dict() for q in DW_QUESTS],
			'items': [item.to_dict() for item in DW_QUEST_ITEMS],
			'milestones': [m.to_dict() for m in DW_MILESTONES],
			'critical_path': [q.id for q in self.tracker.find_critical_path()],
			'dependencies': self.tracker.analyze_dependencies()
		}

		output_path.parent.mkdir(parents=True, exist_ok=True)
		with output_path.open('w') as f:
			json.dump(data, f, indent='\t')

		print(f"Generated JSON guide: {output_path}")

	def generate_speedrun_route(self, output_path: Path) -> None:
		"""Generate an optimized speedrun route."""
		lines = []

		lines.append("="*70)
		lines.append("DRAGON WARRIOR SPEEDRUN ROUTE")
		lines.append("="*70)
		lines.append("")

		lines.append("This route focuses on the minimum required quests and items.")
		lines.append("")

		critical = self.tracker.find_critical_path()

		lines.append("ROUTE OVERVIEW")
		lines.append("-"*70)

		for i, quest in enumerate(critical, 1):
			lines.append(f"\n{i}. {quest.name}")
			lines.append(f"   Level: {quest.required_level}")
			lines.append(f"   Location: {quest.location}")

			if quest.required_items:
				lines.append(f"   Items: {', '.join(quest.required_items)}")

		lines.append("\n" + "="*70)
		lines.append("ITEM COLLECTION ORDER")
		lines.append("-"*70)

		# Determine optimal item collection order
		required_items = set()
		for quest in critical:
			required_items.update(quest.required_items)
			required_items.update(quest.rewards)

		item_order = [item for item in DW_QUEST_ITEMS if item.name in required_items]

		for i, item in enumerate(item_order, 1):
			lines.append(f"{i}. {item.name} - {item.location}")

		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text('\n'.join(lines))

		print(f"Generated speedrun route: {output_path}")


class InteractiveQuestTracker:
	"""Interactive quest tracking interface."""

	def __init__(self):
		self.tracker = QuestTracker()
		self.generator = WalkthroughGenerator()

	def run(self) -> None:
		"""Run interactive tracker."""
		print("\n" + "="*70)
		print("Dragon Warrior Quest & Progression Tracker")
		print("="*70)

		while True:
			self._print_menu()
			choice = input("\nEnter choice: ").strip()

			if choice == '1':
				self._view_available_quests()
			elif choice == '2':
				self._view_all_quests()
			elif choice == '3':
				self._complete_quest()
			elif choice == '4':
				self._set_level()
			elif choice == '5':
				self._view_progress()
			elif choice == '6':
				self._view_items()
			elif choice == '7':
				self._generate_walkthrough()
			elif choice == '8':
				self._save_state()
			elif choice == '9':
				self._load_state()
			elif choice == 'q':
				break
			else:
				print("Invalid choice")

	def _print_menu(self) -> None:
		"""Print main menu."""
		print("\n" + "-"*70)
		print("Menu:")
		print("  1. View available quests")
		print("  2. View all quests")
		print("  3. Complete quest")
		print("  4. Set current level")
		print("  5. View progression")
		print("  6. View items")
		print("  7. Generate walkthrough")
		print("  8. Save state")
		print("  9. Load state")
		print("  q. Quit")

		print(f"\nCurrent Level: {self.tracker.current_level}")
		print(f"Progression: {self.tracker.get_progression_percentage():.1f}%")

	def _view_available_quests(self) -> None:
		"""View currently available quests."""
		print("\n" + "="*70)
		print("Available Quests")
		print("="*70)

		available = self.tracker.get_available_quests()

		if not available:
			print("\nNo quests currently available. Check prerequisites or level up.")
			return

		for quest in available:
			print(f"\n{quest.id}. {quest.name}")
			print(f"   Level {quest.required_level} - {quest.location}")
			print(f"   {quest.description}")

			if quest.optional:
				print("   [OPTIONAL]")

		next_quest = self.tracker.get_next_recommended_quest()
		if next_quest:
			print(f"\n>>> RECOMMENDED: {next_quest.name}")

	def _view_all_quests(self) -> None:
		"""View all quests with status."""
		print("\n" + "="*70)
		print("All Quests")
		print("="*70)

		for quest in sorted(self.tracker.quests.values(), key=lambda q: q.id):
			status = self.tracker.quest_status[quest.id].name
			print(f"\n{quest.id}. {quest.name} [{status}]")
			print(f"   Level {quest.required_level} - {quest.location}")

			if status == "NOT_STARTED":
				can_start, issues = self.tracker.can_start_quest(quest.id)
				if not can_start:
					print(f"   Prerequisites: {', '.join(issues)}")

	def _complete_quest(self) -> None:
		"""Mark a quest as completed."""
		quest_id = input("Enter quest ID to complete: ").strip()

		try:
			quest_id = int(quest_id)
			if quest_id in self.tracker.quests:
				self.tracker.complete_quest(quest_id)
				quest = self.tracker.quests[quest_id]
				print(f"\n✓ Completed: {quest.name}")

				if quest.rewards:
					print(f"  Rewards: {', '.join(quest.rewards)}")
			else:
				print("Invalid quest ID")
		except ValueError:
			print("Invalid input")

	def _set_level(self) -> None:
		"""Set current level."""
		level = input("Enter current level (1-30): ").strip()

		try:
			level = int(level)
			if 1 <= level <= 30:
				self.tracker.current_level = level
				print(f"Level set to {level}")

				milestone = self.tracker.get_current_milestone()
				if milestone:
					print(f"\nCurrent Milestone: {milestone.name}")
					print(f"  {milestone.description}")
			else:
				print("Level must be between 1 and 30")
		except ValueError:
			print("Invalid level")

	def _view_progress(self) -> None:
		"""View detailed progression."""
		print("\n" + "="*70)
		print("Progression Status")
		print("="*70)

		print(f"\nLevel: {self.tracker.current_level}")
		print(f"Overall Progress: {self.tracker.get_progression_percentage():.1f}%")

		milestone = self.tracker.get_current_milestone()
		if milestone:
			print(f"\nCurrent Milestone: {milestone.name}")
			print(f"  {milestone.description}")
			print(f"  Recommended Equipment: {', '.join(milestone.recommended_equipment)}")

		completed = len([s for s in self.tracker.quest_status.values() if s == QuestStatus.COMPLETED])
		total = len(self.tracker.quests)
		print(f"\nQuests Completed: {completed}/{total}")

		print(f"\nItems Collected: {len(self.tracker.items_collected)}")
		if self.tracker.items_collected:
			print(f"  {', '.join(sorted(self.tracker.items_collected))}")

	def _view_items(self) -> None:
		"""View all quest items."""
		print("\n" + "="*70)
		print("Quest Items")
		print("="*70)

		for item in sorted(DW_QUEST_ITEMS, key=lambda x: x.rarity, reverse=True):
			collected = "✓" if item.name in self.tracker.items_collected else " "
			print(f"\n[{collected}] {item.name} [{ItemRarity(item.rarity).name}]")
			print(f"    Location: {item.location}")
			print(f"    {item.description}")

	def _generate_walkthrough(self) -> None:
		"""Generate walkthrough files."""
		print("\nGenerating walkthrough files...")

		output_dir = Path("output/walkthrough")
		output_dir.mkdir(parents=True, exist_ok=True)

		self.generator.generate_text_walkthrough(output_dir / "complete_walkthrough.txt")
		self.generator.generate_json_guide(output_dir / "quest_data.json")
		self.generator.generate_speedrun_route(output_dir / "speedrun_route.txt")

		print(f"\n✓ Generated walkthrough files in {output_dir}")

	def _save_state(self) -> None:
		"""Save current state."""
		output_path = Path("output/quest_save.json")
		output_path.parent.mkdir(parents=True, exist_ok=True)

		state = self.tracker.export_state()

		with output_path.open('w') as f:
			json.dump(state, f, indent='\t')

		print(f"✓ Saved state to {output_path}")

	def _load_state(self) -> None:
		"""Load saved state."""
		input_path = Path("output/quest_save.json")

		if not input_path.exists():
			print("No saved state found")
			return

		with input_path.open('r') as f:
			state = json.load(f)

		self.tracker.import_state(state)
		print(f"✓ Loaded state from {input_path}")


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Dragon Warrior Quest and Progression Tracker'
	)

	parser.add_argument(
		'-i', '--interactive',
		action='store_true',
		help='Run interactive tracker'
	)

	parser.add_argument(
		'--walkthrough',
		type=Path,
		metavar='OUTPUT',
		help='Generate walkthrough to file'
	)

	parser.add_argument(
		'--speedrun',
		type=Path,
		metavar='OUTPUT',
		help='Generate speedrun route to file'
	)

	parser.add_argument(
		'--json',
		type=Path,
		metavar='OUTPUT',
		help='Export quest data to JSON'
	)

	args = parser.parse_args()

	if args.interactive or (not args.walkthrough and not args.speedrun and not args.json):
		tracker = InteractiveQuestTracker()
		tracker.run()

	else:
		generator = WalkthroughGenerator()

		if args.walkthrough:
			generator.generate_text_walkthrough(args.walkthrough)

		if args.speedrun:
			generator.generate_speedrun_route(args.speedrun)

		if args.json:
			generator.generate_json_guide(args.json)

	return 0


if __name__ == '__main__':
	exit(main())
