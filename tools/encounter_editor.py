#!/usr/bin/env python3
"""
Encounter Rate Editor for Dragon Warrior

Edit monster encounter tables, spawn rates, and zone configurations. Supports
per-area encounter customization, monster group definitions, and encounter
probability tuning.

Features:
- View encounter tables by map zone
- Edit monster pools for each area
- Adjust encounter rates (steps between battles)
- Configure monster groups (1-8 monsters per group)
- Probability distribution analysis
- Encounter simulation and testing
- Export encounter data to JSON/ROM

Usage:
	python tools/encounter_editor.py [ROM_FILE] [--zone ZONE_ID]

Examples:
	# View all encounter zones
	python tools/encounter_editor.py roms/dragon_warrior.nes

	# Edit specific zone
	python tools/encounter_editor.py roms/dragon_warrior.nes --zone 0x05

	# Interactive mode
	python tools/encounter_editor.py roms/dragon_warrior.nes
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
import random
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum


class ZoneType(Enum):
	"""Types of encounter zones."""
	OVERWORLD = "overworld"
	DUNGEON = "dungeon"
	CAVE = "cave"
	SPECIAL = "special"


@dataclass
class MonsterGroup:
	"""Group of monsters that can appear together."""
	monster_ids: List[int] = field(default_factory=list)
	min_count: int = 1
	max_count: int = 1

	def get_spawn_count(self) -> int:
		"""Get random spawn count for this group."""
		return random.randint(self.min_count, self.max_count)


@dataclass
class EncounterSlot:
	"""Single encounter slot with probability."""
	monster_id: int
	probability: int		# 0-255 (higher = more common)
	min_level: int = 1		# Minimum player level for encounter
	max_level: int = 99		# Maximum player level for encounter
	group: Optional[MonsterGroup] = None

	def should_appear(self, player_level: int) -> bool:
		"""Check if monster should appear at player level."""
		return self.min_level <= player_level <= self.max_level


@dataclass
class EncounterTable:
	"""Complete encounter table for a zone."""
	zone_id: int
	zone_name: str
	zone_type: ZoneType

	# Encounter configuration
	base_rate: int = 16			# Steps between encounters (avg)
	rate_variance: int = 8		# ±variance in steps

	# Monster slots
	slots: List[EncounterSlot] = field(default_factory=list)

	# Metadata
	min_level_recommendation: int = 1
	max_level_recommendation: int = 99

	def add_slot(self, slot: EncounterSlot) -> None:
		"""Add encounter slot."""
		self.slots.append(slot)

	def get_total_probability(self) -> int:
		"""Get sum of all probabilities."""
		return sum(slot.probability for slot in self.slots)

	def normalize_probabilities(self) -> None:
		"""Normalize probabilities to sum to 255."""
		total = self.get_total_probability()
		if total == 0:
			return

		# Scale to 255
		for slot in self.slots:
			slot.probability = int((slot.probability / total) * 255)

		# Adjust last slot to ensure total = 255
		if self.slots:
			diff = 255 - sum(s.probability for s in self.slots)
			self.slots[-1].probability += diff

	def select_encounter(self, player_level: int) -> Optional[EncounterSlot]:
		"""Select random encounter based on probabilities."""
		# Filter by level
		valid_slots = [s for s in self.slots if s.should_appear(player_level)]

		if not valid_slots:
			return None

		# Calculate cumulative probabilities
		total = sum(s.probability for s in valid_slots)
		if total == 0:
			return random.choice(valid_slots)

		# Random selection
		roll = random.randint(0, total - 1)
		cumulative = 0

		for slot in valid_slots:
			cumulative += slot.probability
			if roll < cumulative:
				return slot

		return valid_slots[-1]

	def get_encounter_probabilities(self, player_level: int) -> Dict[int, float]:
		"""Get encounter probability for each monster at player level."""
		valid_slots = [s for s in self.slots if s.should_appear(player_level)]
		total = sum(s.probability for s in valid_slots)

		if total == 0:
			return {}

		return {
			slot.monster_id: slot.probability / total
			for slot in valid_slots
		}

	def simulate_encounters(self, player_level: int, count: int = 1000) -> Dict[int, int]:
		"""Simulate encounters and return frequency counts."""
		results = {}

		for _ in range(count):
			slot = self.select_encounter(player_level)
			if slot:
				results[slot.monster_id] = results.get(slot.monster_id, 0) + 1

		return results

	def to_dict(self) -> Dict:
		"""Convert to dictionary for JSON."""
		return {
			'zone_id': self.zone_id,
			'zone_name': self.zone_name,
			'zone_type': self.zone_type.value,
			'base_rate': self.base_rate,
			'rate_variance': self.rate_variance,
			'min_level_recommendation': self.min_level_recommendation,
			'max_level_recommendation': self.max_level_recommendation,
			'slots': [
				{
					'monster_id': s.monster_id,
					'probability': s.probability,
					'min_level': s.min_level,
					'max_level': s.max_level,
				}
				for s in self.slots
			]
		}

	@staticmethod
	def from_dict(data: Dict) -> 'EncounterTable':
		"""Create from dictionary."""
		table = EncounterTable(
			zone_id=data['zone_id'],
			zone_name=data['zone_name'],
			zone_type=ZoneType(data.get('zone_type', 'overworld')),
			base_rate=data.get('base_rate', 16),
			rate_variance=data.get('rate_variance', 8),
			min_level_recommendation=data.get('min_level_recommendation', 1),
			max_level_recommendation=data.get('max_level_recommendation', 99),
		)

		for slot_data in data.get('slots', []):
			slot = EncounterSlot(
				monster_id=slot_data['monster_id'],
				probability=slot_data['probability'],
				min_level=slot_data.get('min_level', 1),
				max_level=slot_data.get('max_level', 99),
			)
			table.add_slot(slot)

		return table


# Dragon Warrior monster names for reference
MONSTER_NAMES = {
	0: 'Slime', 1: 'Red Slime', 2: 'Drakee', 3: 'Ghost', 4: 'Magician',
	5: 'Magidrakee', 6: 'Scorpion', 7: 'Druin', 8: 'Poltergeist',
	9: 'Droll', 10: 'Drakeema', 11: 'Skeleton', 12: 'Warlock',
	13: 'Metal Scorpion', 14: 'Wolf', 15: 'Wraith', 16: 'Metal Slime',
	17: 'Specter', 18: 'Wolflord', 19: 'Druinlord', 20: 'Drollmagi',
	21: 'Wyvern', 22: 'Rouge Scorpion', 23: 'Wraith Knight', 24: 'Golem',
	25: 'Goldman', 26: 'Knight', 27: 'Magiwyvern', 28: 'Demon Knight',
	29: 'Werewolf', 30: 'Green Dragon', 31: 'Starwyvern', 32: 'Wizard',
	33: 'Axe Knight', 34: 'Blue Dragon', 35: 'Stoneman',
	36: 'Armored Knight', 37: 'Red Dragon', 38: 'Dragonlord',
}


class EncounterExtractor:
	"""Extract encounter tables from Dragon Warrior ROM."""

	# Encounter table locations in ROM
	ENCOUNTER_TABLE_OFFSET = 0x0f300
	NUM_ZONES = 16

	def __init__(self, rom_path: Path):
		self.rom_path = rom_path
		self.rom_data = self._load_rom()

	def _load_rom(self) -> bytes:
		"""Load ROM file."""
		with open(self.rom_path, 'rb') as f:
			return f.read()

	def extract_zone_table(self, zone_id: int) -> Optional[EncounterTable]:
		"""
		Extract encounter table for zone.

		Format (approximate, based on Dragon Warrior structure):
		- Each zone has 8 encounter slots
		- Each slot: 1 byte monster_id + 1 byte probability
		"""
		if zone_id < 0 or zone_id >= self.NUM_ZONES:
			return None

		# Calculate offset for this zone
		offset = self.ENCOUNTER_TABLE_OFFSET + (zone_id * 16)  # 16 bytes per zone

		if offset + 16 > len(self.rom_data):
			return None

		# Zone type mapping (approximate)
		zone_types = [
			ZoneType.OVERWORLD, ZoneType.OVERWORLD, ZoneType.OVERWORLD,
			ZoneType.DUNGEON, ZoneType.DUNGEON, ZoneType.CAVE,
			ZoneType.CAVE, ZoneType.DUNGEON, ZoneType.OVERWORLD,
			ZoneType.DUNGEON, ZoneType.DUNGEON, ZoneType.DUNGEON,
			ZoneType.OVERWORLD, ZoneType.DUNGEON, ZoneType.DUNGEON,
			ZoneType.SPECIAL
		]

		zone_names = [
			"Starting Area (Tantegel)", "Tantegel Vicinity", "Mid Overworld",
			"Tantegel Cellar", "Cave North of Tantegel", "Mountain Cave",
			"Garinham Cave", "Erdrick's Cave", "Southern Continent",
			"Charlock Castle 1F", "Charlock Castle 2F", "Charlock Castle 3F",
			"Far Overworld", "Charlock Castle 4F", "Charlock Castle 5F",
			"Charlock Castle 6F (Throne)"
		]

		table = EncounterTable(
			zone_id=zone_id,
			zone_name=zone_names[zone_id] if zone_id < len(zone_names) else f"Zone {zone_id}",
			zone_type=zone_types[zone_id] if zone_id < len(zone_types) else ZoneType.OVERWORLD,
		)

		# Extract 8 slots (monster_id, probability pairs)
		for i in range(8):
			monster_id = self.rom_data[offset + i * 2]
			probability = self.rom_data[offset + i * 2 + 1]

			# Skip empty slots
			if monster_id == 0xff or probability == 0:
				continue

			slot = EncounterSlot(
				monster_id=monster_id,
				probability=probability,
			)
			table.add_slot(slot)

		return table

	def extract_all_zones(self) -> List[EncounterTable]:
		"""Extract all encounter zones."""
		tables = []

		for zone_id in range(self.NUM_ZONES):
			table = self.extract_zone_table(zone_id)
			if table:
				tables.append(table)

		return tables


class EncounterAnalyzer:
	"""Analyze encounter distributions."""

	@staticmethod
	def analyze_table(table: EncounterTable, player_levels: List[int] = [1, 5, 10, 15, 20, 30]) -> str:
		"""Analyze encounter table at different levels."""
		lines = []
		lines.append(f"\nEncounter Analysis: {table.zone_name}")
		lines.append("=" * 80)
		lines.append(f"Zone ID: {table.zone_id}")
		lines.append(f"Type: {table.zone_type.value}")
		lines.append(f"Encounter Rate: {table.base_rate} ± {table.rate_variance} steps")
		lines.append(f"Recommended Levels: {table.min_level_recommendation}-{table.max_level_recommendation}")
		lines.append()

		# Slot details
		lines.append("Monster Slots:")
		lines.append(f"{'ID':<4} {'Monster':<20} {'Prob':<6} {'%':<8} {'Level Range':<15}")
		lines.append("-" * 80)

		total_prob = table.get_total_probability()

		for slot in table.slots:
			monster_name = MONSTER_NAMES.get(slot.monster_id, f"Monster {slot.monster_id}")
			percentage = (slot.probability / total_prob * 100) if total_prob > 0 else 0
			level_range = f"{slot.min_level}-{slot.max_level}"

			lines.append(f"{slot.monster_id:<4} {monster_name:<20} {slot.probability:<6} {percentage:>6.2f}%  {level_range:<15}")

		lines.append()

		# Simulation at different levels
		lines.append("Encounter Probabilities by Level (1000 sample simulation):")
		lines.append()

		for level in player_levels:
			lines.append(f"Level {level}:")

			probabilities = table.get_encounter_probabilities(level)
			simulation = table.simulate_encounters(level, 1000)

			if not probabilities:
				lines.append("  No encounters at this level")
				continue

			for monster_id in sorted(probabilities.keys()):
				monster_name = MONSTER_NAMES.get(monster_id, f"Monster {monster_id}")
				expected = probabilities[monster_id] * 100
				actual = simulation.get(monster_id, 0) / 10.0

				lines.append(f"  {monster_name:<20} Expected: {expected:>5.1f}%  Actual: {actual:>5.1f}%")

			lines.append()

		return '\n'.join(lines)

	@staticmethod
	def compare_zones(tables: List[EncounterTable], player_level: int = 10) -> str:
		"""Compare encounter tables across zones."""
		lines = []
		lines.append(f"\nZone Comparison (Level {player_level})")
		lines.append("=" * 80)
		lines.append(f"{'Zone':<30} {'Type':<12} {'Rate':<8} {'# Monsters':<12}")
		lines.append("-" * 80)

		for table in tables:
			probabilities = table.get_encounter_probabilities(player_level)
			num_monsters = len(probabilities)

			lines.append(f"{table.zone_name:<30} {table.zone_type.value:<12} {table.base_rate:<8} {num_monsters:<12}")

		return '\n'.join(lines)


class InteractiveEncounterEditor:
	"""Interactive encounter table editor."""

	def __init__(self, rom_path: Optional[Path] = None):
		self.rom_path = rom_path
		self.extractor = EncounterExtractor(rom_path) if rom_path else None
		self.tables: Dict[int, EncounterTable] = {}
		self.current_zone_id: Optional[int] = None
		self.analyzer = EncounterAnalyzer()

	def run(self) -> None:
		"""Run interactive editor."""
		print("Dragon Warrior Encounter Editor")
		print("=" * 60)
		print("Commands: list, load, view, analyze, edit, add, remove, save, help, quit")
		print()

		while True:
			try:
				cmd = input(f"encounter-editor> ").strip().lower()

				if not cmd:
					continue

				parts = cmd.split()
				command = parts[0]
				args = parts[1:] if len(parts) > 1 else []

				if command == 'quit' or command == 'exit':
					break
				elif command == 'help':
					self._show_help()
				elif command == 'list':
					self._list_zones()
				elif command == 'load':
					self._load_zone(args)
				elif command == 'view':
					self._view_table()
				elif command == 'analyze':
					self._analyze_table()
				elif command == 'compare':
					self._compare_zones()
				elif command == 'edit':
					self._edit_slot(args)
				elif command == 'add':
					self._add_slot(args)
				elif command == 'remove':
					self._remove_slot(args)
				elif command == 'rate':
					self._edit_rate(args)
				elif command == 'save':
					self._save_table(args)
				elif command == 'simulate':
					self._simulate_encounters(args)
				else:
					print(f"Unknown command: {command}")

			except KeyboardInterrupt:
				print("\nUse 'quit' to exit.")
			except Exception as e:
				print(f"Error: {e}")

	def _show_help(self) -> None:
		"""Show help text."""
		print("""
Encounter Editor Commands:

list                    - List all encounter zones
load <zone_id>          - Load encounter table for zone
view                    - View current table details
analyze                 - Analyze current table probabilities
compare                 - Compare all zones
edit <slot> <field> <val> - Edit slot field
add <monster_id> <prob> - Add encounter slot
remove <slot>           - Remove encounter slot
rate <base> [variance]  - Set encounter rate
save [file]             - Save table to JSON
simulate <level> [count]- Simulate encounters at level
help                    - Show this help
quit                    - Exit editor

Examples:
	list
	load 0
	view
	analyze
	edit 0 probability 100
	add 16 50
	remove 7
	rate 20 10
	simulate 10 5000
	save encounters/tantegel.json
""")

	def _list_zones(self) -> None:
		"""List all zones."""
		if not self.extractor:
			print("No ROM loaded")
			return

		tables = self.extractor.extract_all_zones()

		print("\nEncounter Zones:")
		print(f"{'ID':<4} {'Name':<35} {'Type':<12} {'Rate':<8} {'# Slots':<8}")
		print("-" * 80)

		for table in tables:
			print(f"{table.zone_id:<4} {table.zone_name:<35} {table.zone_type.value:<12} {table.base_rate:<8} {len(table.slots):<8}")

	def _load_zone(self, args: List[str]) -> None:
		"""Load encounter zone."""
		if not args:
			print("Usage: load <zone_id>")
			return

		if not self.extractor:
			print("No ROM loaded")
			return

		try:
			zone_id = int(args[0])
		except ValueError:
			print(f"Invalid zone ID: {args[0]}")
			return

		table = self.extractor.extract_zone_table(zone_id)
		if not table:
			print(f"Zone {zone_id} not found")
			return

		self.tables[zone_id] = table
		self.current_zone_id = zone_id

		print(f"Loaded zone {zone_id}: {table.zone_name}")

	def _view_table(self) -> None:
		"""View current table."""
		if self.current_zone_id is None:
			print("No zone loaded")
			return

		table = self.tables.get(self.current_zone_id)
		if not table:
			print("Current zone not found")
			return

		print(f"\n{table.zone_name} (Zone {table.zone_id})")
		print("=" * 60)
		print(f"Type: {table.zone_type.value}")
		print(f"Encounter Rate: {table.base_rate} ± {table.rate_variance} steps")
		print()
		print(f"{'Slot':<6} {'ID':<4} {'Monster':<20} {'Probability':<12} {'%':<8}")
		print("-" * 60)

		total = table.get_total_probability()

		for i, slot in enumerate(table.slots):
			monster_name = MONSTER_NAMES.get(slot.monster_id, f"Monster {slot.monster_id}")
			percentage = (slot.probability / total * 100) if total > 0 else 0

			print(f"{i:<6} {slot.monster_id:<4} {monster_name:<20} {slot.probability:<12} {percentage:>6.2f}%")

	def _analyze_table(self) -> None:
		"""Analyze current table."""
		if self.current_zone_id is None:
			print("No zone loaded")
			return

		table = self.tables.get(self.current_zone_id)
		if not table:
			return

		analysis = self.analyzer.analyze_table(table)
		print(analysis)

	def _compare_zones(self) -> None:
		"""Compare all zones."""
		if not self.extractor:
			print("No ROM loaded")
			return

		tables = self.extractor.extract_all_zones()
		comparison = self.analyzer.compare_zones(tables)
		print(comparison)

	def _edit_slot(self, args: List[str]) -> None:
		"""Edit encounter slot."""
		if len(args) < 3:
			print("Usage: edit <slot_index> <field> <value>")
			return

		if self.current_zone_id is None:
			print("No zone loaded")
			return

		table = self.tables.get(self.current_zone_id)
		if not table:
			return

		try:
			slot_index = int(args[0])
			field = args[1]
			value = int(args[2])
		except ValueError:
			print("Invalid parameters")
			return

		if slot_index < 0 or slot_index >= len(table.slots):
			print(f"Invalid slot index: {slot_index}")
			return

		slot = table.slots[slot_index]

		if field == 'monster_id' or field == 'monster':
			slot.monster_id = value
			print(f"Set monster ID to {value}")
		elif field == 'probability' or field == 'prob':
			slot.probability = value
			print(f"Set probability to {value}")
		elif field == 'min_level':
			slot.min_level = value
			print(f"Set min level to {value}")
		elif field == 'max_level':
			slot.max_level = value
			print(f"Set max level to {value}")
		else:
			print(f"Unknown field: {field}")

	def _add_slot(self, args: List[str]) -> None:
		"""Add encounter slot."""
		if len(args) < 2:
			print("Usage: add <monster_id> <probability>")
			return

		if self.current_zone_id is None:
			print("No zone loaded")
			return

		table = self.tables.get(self.current_zone_id)
		if not table:
			return

		try:
			monster_id = int(args[0])
			probability = int(args[1])
		except ValueError:
			print("Invalid parameters")
			return

		slot = EncounterSlot(monster_id=monster_id, probability=probability)
		table.add_slot(slot)

		monster_name = MONSTER_NAMES.get(monster_id, f"Monster {monster_id}")
		print(f"Added {monster_name} with probability {probability}")

	def _remove_slot(self, args: List[str]) -> None:
		"""Remove encounter slot."""
		if not args:
			print("Usage: remove <slot_index>")
			return

		if self.current_zone_id is None:
			print("No zone loaded")
			return

		table = self.tables.get(self.current_zone_id)
		if not table:
			return

		try:
			slot_index = int(args[0])
		except ValueError:
			print(f"Invalid slot index: {args[0]}")
			return

		if slot_index < 0 or slot_index >= len(table.slots):
			print(f"Slot index out of range: {slot_index}")
			return

		removed = table.slots.pop(slot_index)
		monster_name = MONSTER_NAMES.get(removed.monster_id, f"Monster {removed.monster_id}")
		print(f"Removed slot {slot_index}: {monster_name}")

	def _edit_rate(self, args: List[str]) -> None:
		"""Edit encounter rate."""
		if not args:
			print("Usage: rate <base_rate> [variance]")
			return

		if self.current_zone_id is None:
			print("No zone loaded")
			return

		table = self.tables.get(self.current_zone_id)
		if not table:
			return

		try:
			base_rate = int(args[0])
			variance = int(args[1]) if len(args) > 1 else table.rate_variance
		except ValueError:
			print("Invalid parameters")
			return

		table.base_rate = base_rate
		table.rate_variance = variance

		print(f"Set encounter rate to {base_rate} ± {variance} steps")

	def _save_table(self, args: List[str]) -> None:
		"""Save table to JSON."""
		if self.current_zone_id is None:
			print("No zone loaded")
			return

		table = self.tables.get(self.current_zone_id)
		if not table:
			return

		if args:
			filename = args[0]
		else:
			filename = f"encounter_zone_{self.current_zone_id:02d}.json"

		filepath = Path(filename)
		filepath.parent.mkdir(parents=True, exist_ok=True)

		with open(filepath, 'w', encoding='utf-8') as f:
			json.dump(table.to_dict(), f, indent='\t')

		print(f"Saved to {filepath}")

	def _simulate_encounters(self, args: List[str]) -> None:
		"""Simulate encounters."""
		if not args:
			print("Usage: simulate <level> [count]")
			return

		if self.current_zone_id is None:
			print("No zone loaded")
			return

		table = self.tables.get(self.current_zone_id)
		if not table:
			return

		try:
			level = int(args[0])
			count = int(args[1]) if len(args) > 1 else 1000
		except ValueError:
			print("Invalid parameters")
			return

		print(f"\nSimulating {count} encounters at level {level}...")
		results = table.simulate_encounters(level, count)

		print(f"\n{'Monster':<20} {'Count':<8} {'Percentage':<10}")
		print("-" * 40)

		for monster_id in sorted(results.keys()):
			monster_name = MONSTER_NAMES.get(monster_id, f"Monster {monster_id}")
			encounter_count = results[monster_id]
			percentage = (encounter_count / count) * 100

			print(f"{monster_name:<20} {encounter_count:<8} {percentage:>6.2f}%")


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Dragon Warrior Encounter Rate Editor'
	)
	parser.add_argument(
		'rom',
		type=Path,
		nargs='?',
		help='Path to Dragon Warrior ROM'
	)
	parser.add_argument(
		'--zone',
		type=int,
		help='Load specific zone'
	)

	args = parser.parse_args()

	editor = InteractiveEncounterEditor(args.rom if args.rom else None)

	if args.zone is not None and args.rom:
		editor._load_zone([str(args.zone)])
		editor._view_table()

	editor.run()


if __name__ == '__main__':
	main()
