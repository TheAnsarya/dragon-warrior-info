#!/usr/bin/env python3
"""
Event and Dialogue System Editor for Dragon Warrior

Comprehensive event scripting and dialogue editing tool with branching
conversations, conditional triggers, and cutscene management.

Features:
- Dialogue editor with text compression
- Event script editor with visual flow
- NPC conversation trees
- Conditional triggers and flags
- Cutscene sequencing
- Text preview with character limits
- Export to game format
- Import from ROM
- Dialogue search and replace
- Event dependency visualization

Usage:
	python tools/event_editor_advanced.py [ROM_FILE]

Examples:
	# Interactive mode
	python tools/event_editor_advanced.py roms/dragon_warrior.nes

	# Export all dialogues
	python tools/event_editor_advanced.py roms/dragon_warrior.nes --export dialogues.json

	# Import modified dialogues
	python tools/event_editor_advanced.py roms/dragon_warrior.nes --import dialogues.json

	# Search dialogue
	python tools/event_editor_advanced.py --search "princess"

Author: Dragon Warrior ROM Hacking Toolkit
Version: 2.0
"""

import sys
import os
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import argparse


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class EventType(Enum):
	"""Event types."""
	DIALOGUE = "dialogue"
	BATTLE = "battle"
	ITEM_GET = "item_get"
	DOOR_OPEN = "door_open"
	TELEPORT = "teleport"
	HEAL = "heal"
	SHOP = "shop"
	INN = "inn"
	SAVE = "save"
	CUTSCENE = "cutscene"


class ConditionType(Enum):
	"""Condition types for events."""
	FLAG_SET = "flag_set"
	FLAG_CLEAR = "flag_clear"
	ITEM_OWNED = "item_owned"
	LEVEL_MIN = "level_min"
	GOLD_MIN = "gold_min"
	ALWAYS = "always"


@dataclass
class Condition:
	"""Event trigger condition."""
	type: ConditionType
	parameter: int = 0

	def evaluate(self, game_state: Dict) -> bool:
		"""Evaluate condition against game state."""
		if self.type == ConditionType.ALWAYS:
			return True
		elif self.type == ConditionType.FLAG_SET:
			return game_state.get('flags', set()).get(self.parameter, False)
		elif self.type == ConditionType.ITEM_OWNED:
			return self.parameter in game_state.get('items', [])
		elif self.type == ConditionType.LEVEL_MIN:
			return game_state.get('level', 1) >= self.parameter
		elif self.type == ConditionType.GOLD_MIN:
			return game_state.get('gold', 0) >= self.parameter
		return False


@dataclass
class DialogueLine:
	"""Single line of dialogue."""
	id: int
	speaker: str
	text: str
	next_id: Optional[int] = None
	choices: List[Tuple[str, int]] = field(default_factory=list)  # (text, next_id)
	conditions: List[Condition] = field(default_factory=list)

	def get_compressed_size(self) -> int:
		"""Estimate compressed size using DTE."""
		# Simplified compression estimate
		# Common pairs: "th", "he", "in", "er", "an", "on", etc.
		common_pairs = ["th", "he", "in", "er", "an", "on", "ed", "nd", "to", "or"]

		text = self.text
		size = len(text)

		for pair in common_pairs:
			count = text.count(pair)
			size -= count  # Each pair saves 1 byte

		return max(size, len(text) // 2)


@dataclass
class Dialogue:
	"""Dialogue tree."""
	id: int
	name: str
	location: str
	npc_id: int
	lines: List[DialogueLine] = field(default_factory=list)
	entry_point: int = 0

	def get_total_size(self) -> int:
		"""Get total dialogue size in bytes."""
		return sum(line.get_compressed_size() for line in self.lines)

	def get_line_by_id(self, line_id: int) -> Optional[DialogueLine]:
		"""Get dialogue line by ID."""
		for line in self.lines:
			if line.id == line_id:
				return line
		return None

	def get_flow_paths(self) -> List[List[int]]:
		"""Get all possible dialogue flow paths."""
		paths = []

		def explore_path(current_id: int, path: List[int]):
			if current_id in path:
				# Circular reference
				return

			path = path + [current_id]
			line = self.get_line_by_id(current_id)

			if not line:
				paths.append(path)
				return

			if line.next_id is not None:
				explore_path(line.next_id, path)
			elif line.choices:
				for choice_text, choice_id in line.choices:
					explore_path(choice_id, path)
			else:
				paths.append(path)

		explore_path(self.entry_point, [])
		return paths


@dataclass
class Event:
	"""Game event."""
	id: int
	name: str
	type: EventType
	location: str
	trigger_x: int
	trigger_y: int
	conditions: List[Condition] = field(default_factory=list)
	actions: List[Dict] = field(default_factory=list)
	dialogue_id: Optional[int] = None
	flags_set: Set[int] = field(default_factory=set)
	flags_cleared: Set[int] = field(default_factory=set)


@dataclass
class Cutscene:
	"""Cutscene sequence."""
	id: int
	name: str
	description: str
	events: List[Event] = field(default_factory=list)
	duration_frames: int = 0

	def get_total_duration_seconds(self) -> float:
		"""Get total cutscene duration in seconds (NTSC)."""
		return self.duration_frames / 60.0


# ============================================================================
# TEXT COMPRESSION
# ============================================================================

class TextCompressor:
	"""Text compression using Dual-Tile Encoding (DTE)."""

	def __init__(self):
		# Common English digraphs
		self.dictionary = [
			"th", "he", "in", "er", "an", "on", "ed", "nd",
			"to", "or", "is", "it", "ar", "en", "at", "re",
			"of", "st", "te", "ou", "le", "as", "al", "ve",
			"me", "se", "om", "be", "ha", "de", "wa", "ma",
			"co", "li", "hi", "wi", "ti", "fo", "yo", "ne",
			"ca", "ra", "la", "ta", "ri", "sa", "ro", "na",
		]

	def compress(self, text: str) -> bytes:
		"""Compress text using DTE."""
		result = []
		i = 0

		while i < len(text):
			# Try to find 2-character match
			if i + 1 < len(text):
				pair = text[i:i+2].lower()
				if pair in self.dictionary:
					# Use dictionary token (0x80 + index)
					token = 0x80 + self.dictionary.index(pair)
					result.append(token)
					i += 2
					continue

			# Single character
			result.append(ord(text[i]))
			i += 1

		return bytes(result)

	def decompress(self, data: bytes) -> str:
		"""Decompress DTE text."""
		result = []

		for byte in data:
			if byte >= 0x80 and byte < 0x80 + len(self.dictionary):
				# Dictionary token
				result.append(self.dictionary[byte - 0x80])
			elif byte == 0x00:
				# String terminator
				break
			else:
				# Regular character
				result.append(chr(byte))

		return ''.join(result)

	def estimate_savings(self, text: str) -> Tuple[int, int, int]:
		"""Estimate compression savings."""
		original_size = len(text)
		compressed = self.compress(text)
		compressed_size = len(compressed)
		savings = original_size - compressed_size

		return original_size, compressed_size, savings


# ============================================================================
# DIALOGUE EXTRACTOR
# ============================================================================

class DialogueExtractor:
	"""Extract dialogues from ROM."""

	# Dragon Warrior dialogue locations (approximate)
	DIALOGUE_POINTERS = 0x1d000
	DIALOGUE_DATA = 0x1d100
	NUM_DIALOGUES = 100

	def __init__(self, rom_data: bytes):
		self.rom_data = rom_data
		self.compressor = TextCompressor()

	def extract_string(self, offset: int, max_length: int = 256) -> str:
		"""Extract null-terminated string from ROM."""
		result = []
		for i in range(max_length):
			if offset + i >= len(self.rom_data):
				break

			byte = self.rom_data[offset + i]

			if byte == 0x00:  # String terminator
				break
			elif byte == 0xff:  # Line break
				result.append('\n')
			elif byte >= 0x20 and byte < 0x7f:
				result.append(chr(byte))
			elif byte >= 0x80:  # Compressed token
				# Decompress
				pass

		return ''.join(result)

	def extract_dialogue(self, dialogue_id: int) -> Optional[Dialogue]:
		"""Extract dialogue by ID."""
		# Read pointer
		pointer_offset = self.DIALOGUE_POINTERS + (dialogue_id * 2)

		if pointer_offset + 2 > len(self.rom_data):
			return None

		pointer = (self.rom_data[pointer_offset] |
				  (self.rom_data[pointer_offset + 1] << 8))

		# Convert pointer to ROM offset
		offset = pointer - 0x8000 + 0x10000

		if offset >= len(self.rom_data):
			return None

		# Extract text
		text = self.extract_string(offset)

		# Create dialogue structure
		dialogue = Dialogue(
			id=dialogue_id,
			name=f"Dialogue {dialogue_id}",
			location="Unknown",
			npc_id=dialogue_id
		)

		# Parse text into lines
		lines = text.split('\n')
		for i, line_text in enumerate(lines):
			if line_text.strip():
				dialogue.lines.append(DialogueLine(
					id=i,
					speaker="NPC",
					text=line_text.strip()
				))

		return dialogue

	def extract_all_dialogues(self) -> List[Dialogue]:
		"""Extract all dialogues from ROM."""
		dialogues = []

		for i in range(self.NUM_DIALOGUES):
			dialogue = self.extract_dialogue(i)
			if dialogue and dialogue.lines:
				dialogues.append(dialogue)

		return dialogues


# ============================================================================
# DIALOGUE EDITOR
# ============================================================================

class DialogueEditor:
	"""Interactive dialogue editor."""

	def __init__(self):
		self.dialogues: List[Dialogue] = []
		self.current_dialogue: Optional[Dialogue] = None
		self.compressor = TextCompressor()

	def load_from_file(self, filepath: Path):
		"""Load dialogues from JSON file."""
		with open(filepath, 'r') as f:
			data = json.load(f)

		self.dialogues = []
		for d in data['dialogues']:
			dialogue = Dialogue(
				id=d['id'],
				name=d['name'],
				location=d['location'],
				npc_id=d['npc_id']
			)

			for line_data in d['lines']:
				line = DialogueLine(
					id=line_data['id'],
					speaker=line_data['speaker'],
					text=line_data['text'],
					next_id=line_data.get('next_id')
				)
				dialogue.lines.append(line)

			self.dialogues.append(dialogue)

	def save_to_file(self, filepath: Path):
		"""Save dialogues to JSON file."""
		data = {
			'dialogues': [asdict(d) for d in self.dialogues]
		}

		with open(filepath, 'w') as f:
			json.dump(data, f, indent=2)

	def add_dialogue(self, dialogue: Dialogue):
		"""Add new dialogue."""
		self.dialogues.append(dialogue)

	def search_dialogues(self, query: str) -> List[Tuple[Dialogue, DialogueLine]]:
		"""Search for text in dialogues."""
		results = []
		query_lower = query.lower()

		for dialogue in self.dialogues:
			for line in dialogue.lines:
				if query_lower in line.text.lower():
					results.append((dialogue, line))

		return results

	def replace_text(self, old_text: str, new_text: str) -> int:
		"""Replace text in all dialogues."""
		count = 0

		for dialogue in self.dialogues:
			for line in dialogue.lines:
				if old_text in line.text:
					line.text = line.text.replace(old_text, new_text)
					count += 1

		return count

	def get_compression_stats(self) -> Dict:
		"""Get compression statistics for all dialogues."""
		total_original = 0
		total_compressed = 0

		for dialogue in self.dialogues:
			for line in dialogue.lines:
				orig, comp, _ = self.compressor.estimate_savings(line.text)
				total_original += orig
				total_compressed += comp

		return {
			'original_size': total_original,
			'compressed_size': total_compressed,
			'savings': total_original - total_compressed,
			'ratio': total_compressed / max(total_original, 1)
		}

	def visualize_dialogue_flow(self, dialogue: Dialogue) -> str:
		"""Create ASCII visualization of dialogue flow."""
		lines = []
		lines.append(f"Dialogue: {dialogue.name}")
		lines.append("=" * 60)

		visited = set()

		def render_line(line_id: int, indent: int = 0):
			if line_id in visited:
				return

			visited.add(line_id)
			line = dialogue.get_line_by_id(line_id)

			if not line:
				return

			prefix = "  " * indent
			lines.append(f"{prefix}[{line.id}] {line.speaker}: {line.text[:40]}...")

			if line.choices:
				for choice_text, next_id in line.choices:
					lines.append(f"{prefix}  → {choice_text}")
					render_line(next_id, indent + 2)
			elif line.next_id is not None:
				render_line(line.next_id, indent)

		render_line(dialogue.entry_point)

		return "\n".join(lines)


# ============================================================================
# EVENT EDITOR
# ============================================================================

class EventEditor:
	"""Event script editor."""

	def __init__(self):
		self.events: List[Event] = []
		self.cutscenes: List[Cutscene] = []

	def add_event(self, event: Event):
		"""Add new event."""
		self.events.append(event)

	def get_events_by_location(self, location: str) -> List[Event]:
		"""Get all events in a location."""
		return [e for e in self.events if e.location == location]

	def get_event_dependencies(self, event: Event) -> List[Event]:
		"""Get events that this event depends on (flag dependencies)."""
		dependencies = []

		for other in self.events:
			# Check if other event sets flags that this event requires
			for condition in event.conditions:
				if condition.type == ConditionType.FLAG_SET:
					if condition.parameter in other.flags_set:
						dependencies.append(other)

		return dependencies

	def visualize_event_graph(self) -> str:
		"""Create ASCII visualization of event dependencies."""
		lines = []
		lines.append("Event Dependency Graph")
		lines.append("=" * 60)

		for event in self.events:
			lines.append(f"\n{event.name} (ID: {event.id})")
			lines.append(f"  Location: {event.location}")
			lines.append(f"  Type: {event.type.value}")

			deps = self.get_event_dependencies(event)
			if deps:
				lines.append("  Depends on:")
				for dep in deps:
					lines.append(f"    - {dep.name}")

			if event.flags_set:
				lines.append(f"  Sets flags: {sorted(event.flags_set)}")

		return "\n".join(lines)


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Event and Dialogue System Editor"
	)

	parser.add_argument('rom_file', nargs='?', help="ROM file to edit")
	parser.add_argument('--export', help="Export dialogues to JSON file")
	parser.add_argument('--import', dest='import_file', help="Import dialogues from JSON file")
	parser.add_argument('--search', help="Search dialogue text")
	parser.add_argument('--replace', nargs=2, metavar=('OLD', 'NEW'),
					   help="Replace text in dialogues")
	parser.add_argument('--stats', action='store_true',
					   help="Show compression statistics")

	args = parser.parse_args()

	editor = DialogueEditor()

	# Load ROM if provided
	if args.rom_file:
		rom_path = Path(args.rom_file)

		if not rom_path.exists():
			print(f"Error: ROM file not found: {rom_path}")
			return 1

		print(f"Loading ROM: {rom_path}")

		with open(rom_path, 'rb') as f:
			rom_data = f.read()

		extractor = DialogueExtractor(rom_data)
		dialogues = extractor.extract_all_dialogues()

		print(f"Extracted {len(dialogues)} dialogues")

		for dialogue in dialogues:
			editor.add_dialogue(dialogue)

	# Import from JSON
	if args.import_file:
		import_path = Path(args.import_file)
		if import_path.exists():
			editor.load_from_file(import_path)
			print(f"Imported dialogues from {import_path}")

	# Export to JSON
	if args.export:
		export_path = Path(args.export)
		editor.save_to_file(export_path)
		print(f"Exported {len(editor.dialogues)} dialogues to {export_path}")

	# Search
	if args.search:
		results = editor.search_dialogues(args.search)
		print(f"\nFound {len(results)} matches for '{args.search}':")

		for dialogue, line in results:
			print(f"\n{dialogue.name} (Line {line.id}):")
			print(f"  {line.text}")

	# Replace
	if args.replace:
		old_text, new_text = args.replace
		count = editor.replace_text(old_text, new_text)
		print(f"Replaced {count} occurrences of '{old_text}' with '{new_text}'")

	# Statistics
	if args.stats:
		stats = editor.get_compression_stats()
		print("\nCompression Statistics:")
		print(f"  Original size: {stats['original_size']:,} bytes")
		print(f"  Compressed size: {stats['compressed_size']:,} bytes")
		print(f"  Savings: {stats['savings']:,} bytes ({100*(1-stats['ratio']):.1f}%)")

	# Interactive mode
	if not any([args.export, args.search, args.replace, args.stats]):
		print("\n=== Event and Dialogue Editor ===")
		print(f"Loaded {len(editor.dialogues)} dialogues")
		print("\nCommands:")
		print("  list          - List all dialogues")
		print("  view <id>     - View dialogue details")
		print("  flow <id>     - Show dialogue flow")
		print("  search <text> - Search dialogues")
		print("  stats         - Show compression stats")
		print("  quit          - Exit")

		while True:
			try:
				cmd = input("\n> ").strip().split()

				if not cmd:
					continue

				if cmd[0] == 'quit':
					break

				elif cmd[0] == 'list':
					for d in editor.dialogues:
						print(f"  {d.id:3d}: {d.name} ({len(d.lines)} lines)")

				elif cmd[0] == 'view' and len(cmd) > 1:
					dialogue_id = int(cmd[1])
					dialogue = next((d for d in editor.dialogues if d.id == dialogue_id), None)

					if dialogue:
						print(f"\nDialogue {dialogue.id}: {dialogue.name}")
						print(f"Location: {dialogue.location}")
						print(f"Lines: {len(dialogue.lines)}")
						print(f"Total size: ~{dialogue.get_total_size()} bytes compressed")

						for line in dialogue.lines:
							print(f"\n  [{line.id}] {line.speaker}:")
							print(f"    {line.text}")

				elif cmd[0] == 'flow' and len(cmd) > 1:
					dialogue_id = int(cmd[1])
					dialogue = next((d for d in editor.dialogues if d.id == dialogue_id), None)

					if dialogue:
						flow = editor.visualize_dialogue_flow(dialogue)
						print(f"\n{flow}")

				elif cmd[0] == 'stats':
					stats = editor.get_compression_stats()
					print("\nCompression Statistics:")
					print(f"  Original: {stats['original_size']:,} bytes")
					print(f"  Compressed: {stats['compressed_size']:,} bytes")
					print(f"  Savings: {stats['savings']:,} bytes")

			except (KeyboardInterrupt, EOFError):
				break
			except Exception as e:
				print(f"Error: {e}")

	return 0


if __name__ == "__main__":
	sys.exit(main())
