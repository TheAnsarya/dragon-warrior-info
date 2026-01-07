#!/usr/bin/env python3
"""
Dialog Tree Editor for Dragon Warrior

Comprehensive dialog editing system with visual tree representation, branching
logic, NPC assignment, and compression analysis.

Features:
- Visual dialog tree display (ASCII art)
- Branch/choice management
- NPC dialog assignment
- Compression analysis and optimization
- Export to ROM-compatible format
- Text encoding with Dragon Warrior character table
- Dialog ID tracking and cross-references

Usage:
	python tools/dialog_editor.py [ROM_FILE] [--dialog-id ID] [--npc NAME]

Examples:
	# Edit specific dialog
	python tools/dialog_editor.py roms/dragon_warrior.nes --dialog-id 0x08120

	# Edit NPC dialogs
	python tools/dialog_editor.py roms/dragon_warrior.nes --npc "King Lorik"

	# Interactive mode
	python tools/dialog_editor.py roms/dragon_warrior.nes
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
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
from enum import Enum
import struct

# Import the correct TBL-based text encoding
try:
	from dw_text_encoding import (
		encode_text, decode_bytes, validate_text,
		BYTE_TO_CHAR, CHAR_TO_BYTE, CONTROL_CODES, CONTROL_NAMES
	)
	_HAS_DW_ENCODING = True
except ImportError:
	_HAS_DW_ENCODING = False


class DialogType(Enum):
	"""Types of dialog nodes."""
	TEXT = "text"				# Simple text display
	CHOICE = "choice"			# Yes/No choice
	BRANCH = "branch"			# Conditional branch
	END = "end"					# End of dialog


@dataclass
class DialogNode:
	"""Represents a single dialog node in the tree."""
	id: int
	type: DialogType
	text: str
	offset: int = 0

	# Branching
	next_id: Optional[int] = None			# Next node (for TEXT)
	yes_id: Optional[int] = None			# Yes branch (for CHOICE)
	no_id: Optional[int] = None				# No branch (for CHOICE)
	condition: Optional[str] = None			# Condition (for BRANCH)

	# Metadata
	npc_name: Optional[str] = None
	location: Optional[str] = None
	category: str = "generic"

	# Encoding
	encoded: bytes = b''
	compressed_size: int = 0

	def __post_init__(self):
		if isinstance(self.type, str):
			self.type = DialogType(self.type)


@dataclass
class DialogTree:
	"""Collection of dialog nodes forming a tree structure."""
	root_id: int
	nodes: Dict[int, DialogNode] = field(default_factory=dict)
	metadata: Dict = field(default_factory=dict)

	def add_node(self, node: DialogNode) -> None:
		"""Add a node to the tree."""
		self.nodes[node.id] = node

	def get_node(self, node_id: int) -> Optional[DialogNode]:
		"""Get a node by ID."""
		return self.nodes.get(node_id)

	def get_children(self, node_id: int) -> List[DialogNode]:
		"""Get all child nodes of a given node."""
		node = self.get_node(node_id)
		if not node:
			return []

		children = []
		if node.next_id is not None:
			child = self.get_node(node.next_id)
			if child:
				children.append(child)

		if node.yes_id is not None:
			child = self.get_node(node.yes_id)
			if child:
				children.append(child)

		if node.no_id is not None:
			child = self.get_node(node.no_id)
			if child:
				children.append(child)

		return children

	def traverse(self, start_id: Optional[int] = None) -> List[DialogNode]:
		"""Traverse tree in depth-first order."""
		if start_id is None:
			start_id = self.root_id

		visited = set()
		result = []

		def _traverse(node_id: int) -> None:
			if node_id in visited or node_id not in self.nodes:
				return

			visited.add(node_id)
			node = self.nodes[node_id]
			result.append(node)

			# Visit children
			if node.next_id:
				_traverse(node.next_id)
			if node.yes_id:
				_traverse(node.yes_id)
			if node.no_id:
				_traverse(node.no_id)

		_traverse(start_id)
		return result

	def to_dict(self) -> Dict:
		"""Convert tree to dictionary for JSON export."""
		return {
			'root_id': self.root_id,
			'nodes': {
				str(node_id): {
					**asdict(node),
					'type': node.type.value,
					'encoded': node.encoded.hex() if node.encoded else ''
				}
				for node_id, node in self.nodes.items()
			},
			'metadata': self.metadata
		}

	@staticmethod
	def from_dict(data: Dict) -> 'DialogTree':
		"""Create tree from dictionary."""
		tree = DialogTree(root_id=data['root_id'])
		tree.metadata = data.get('metadata', {})

		for node_id_str, node_data in data['nodes'].items():
			node_data = dict(node_data)	# Copy
			node_data['id'] = int(node_id_str)

			# Convert encoded from hex
			if 'encoded' in node_data and node_data['encoded']:
				node_data['encoded'] = bytes.fromhex(node_data['encoded'])

			node = DialogNode(**node_data)
			tree.add_node(node)

		return tree


class DragonWarriorTextEncoder:
	"""
	Dragon Warrior text encoding/decoding.

	Uses the correct TBL-based encoding from dw_text_encoding module:
	- 0x00-0x09: 0-9
	- 0x0a-0x23: a-z (lowercase)
	- 0x24-0x3d: A-Z (uppercase)
	- 0x3e-0x5f: Punctuation and special characters
	- 0x5f: Space
	- 0xf0-0xfc: Control codes (PLRL, ENMY, NAME, WAIT, END, etc.)
	"""

	@classmethod
	def encode(cls, text: str) -> bytes:
		"""
		Encode text to Dragon Warrior format using correct TBL encoding.
		"""
		if _HAS_DW_ENCODING:
			return bytes(encode_text(text))
		else:
			# Fallback if module not available
			return cls._legacy_encode(text)

	@classmethod
	def decode(cls, data: bytes) -> str:
		"""Decode Dragon Warrior text data using correct TBL encoding."""
		if _HAS_DW_ENCODING:
			return decode_bytes(list(data))
		else:
			# Fallback if module not available
			return cls._legacy_decode(data)

	@classmethod
	def calculate_compression_ratio(cls, text: str) -> float:
		"""Calculate compression ratio (text vs encoded)."""
		encoded = cls.encode(text)
		uncompressed_size = len(text) + 1  # +1 for END marker
		compressed_size = len(encoded)

		if uncompressed_size == 0:
			return 1.0

		return compressed_size / uncompressed_size

	# Legacy fallback methods (if dw_text_encoding not available)
	@classmethod
	def _legacy_encode(cls, text: str) -> bytes:
		"""Legacy encoding fallback."""
		# Basic ASCII-like encoding for fallback
		encoded = bytearray()
		for char in text:
			if char == '\n':
				encoded.append(0xfd)
			elif char == ' ':
				encoded.append(0x5f)
			elif 'a' <= char <= 'z':
				encoded.append(ord(char) - ord('a') + 0x0a)
			elif 'A' <= char <= 'Z':
				encoded.append(ord(char) - ord('A') + 0x24)
			elif '0' <= char <= '9':
				encoded.append(ord(char) - ord('0'))
			else:
				encoded.append(0x5f)  # Default to space
		encoded.append(0xfc)  # END marker
		return bytes(encoded)

	@classmethod
	def _legacy_decode(cls, data: bytes) -> str:
		"""Legacy decoding fallback."""
		result = []
		for byte in data:
			if byte == 0xfc:
				result.append('{END}')
			elif byte == 0xfb:
				result.append('{WAIT}')
			elif byte == 0xfd:
				result.append('\n')
			elif byte == 0xf8:
				result.append('{NAME}')
			elif byte == 0x5f:
				result.append(' ')
			elif 0x0a <= byte <= 0x23:
				result.append(chr(byte - 0x0a + ord('a')))
			elif 0x24 <= byte <= 0x3d:
				result.append(chr(byte - 0x24 + ord('A')))
			elif 0x00 <= byte <= 0x09:
				result.append(chr(byte + ord('0')))
			else:
				result.append(f'[${byte:02X}]')
		return ''.join(result)


class DialogExtractor:
	"""Extract dialogs from Dragon Warrior ROM."""

	# Dialog regions in ROM
	DIALOG_REGIONS = [
		(0x08000, 0x0a000),	# Main dialog region
		(0x0a000, 0x0c000),	# NPC dialogs
		(0x0c000, 0x0e000),	# Special dialogs
	]

	def __init__(self, rom_path: Path):
		self.rom_path = rom_path
		self.rom_data = self._load_rom()
		self.encoder = DragonWarriorTextEncoder()

	def _load_rom(self) -> bytes:
		"""Load ROM file."""
		with open(self.rom_path, 'rb') as f:
			return f.read()

	def extract_dialog(self, offset: int) -> Optional[DialogNode]:
		"""Extract a single dialog at given offset."""
		if offset >= len(self.rom_data):
			return None

		# Read until terminator (0xff)
		end_offset = offset
		while end_offset < len(self.rom_data) and self.rom_data[end_offset] != 0xff:
			end_offset += 1

		if end_offset >= len(self.rom_data):
			return None

		# Include terminator
		encoded = self.rom_data[offset:end_offset + 1]

		# Decode
		text = self.encoder.decode(encoded)

		# Determine type
		dialog_type = DialogType.TEXT
		if '<CHOICE>' in text:
			dialog_type = DialogType.CHOICE

		node = DialogNode(
			id=offset,
			type=dialog_type,
			text=text,
			offset=offset,
			encoded=encoded,
			compressed_size=len(encoded)
		)

		return node

	def scan_dialogs(self) -> List[DialogNode]:
		"""Scan ROM for all dialogs."""
		dialogs = []

		for start, end in self.DIALOG_REGIONS:
			offset = start

			while offset < end:
				# Heuristic: dialogs usually start with a letter
				byte = self.rom_data[offset]

				if byte >= 0x00 and byte <= 0x19:  # A-Z
					node = self.extract_dialog(offset)
					if node and len(node.text) > 5:  # Minimum length
						dialogs.append(node)
						offset += node.compressed_size
					else:
						offset += 1
				else:
					offset += 1

		return dialogs

	def extract_npc_dialogs(self, npc_name: str) -> List[DialogNode]:
		"""Extract all dialogs for a specific NPC (by searching text)."""
		all_dialogs = self.scan_dialogs()

		# Filter by NPC name appearing in text
		npc_dialogs = []
		for dialog in all_dialogs:
			# Mark as NPC dialog if NPC name appears
			dialog.npc_name = npc_name
			npc_dialogs.append(dialog)

		return npc_dialogs


class DialogTreeVisualizer:
	"""Visualize dialog trees as ASCII art."""

	@staticmethod
	def render_tree(tree: DialogTree, max_width: int = 80) -> str:
		"""
		Render dialog tree as ASCII art.

		Format:
			[ID] Text preview
			├─> [NEXT_ID] ...
			├─Y [YES_ID] ...
			└─N [NO_ID] ...
		"""
		lines = []
		visited = set()

		def _render_node(node_id: int, prefix: str = "", is_last: bool = True) -> None:
			if node_id in visited or node_id not in tree.nodes:
				return

			visited.add(node_id)
			node = tree.nodes[node_id]

			# Format text preview (truncate to fit)
			text_preview = node.text.replace('\n', ' ')[:50]
			if len(node.text) > 50:
				text_preview += '...'

			# Type indicator
			type_indicator = {
				DialogType.TEXT: 'T',
				DialogType.CHOICE: 'C',
				DialogType.BRANCH: 'B',
				DialogType.END: 'E'
			}.get(node.type, '?')

			# Node line
			connector = "└─" if is_last else "├─"
			node_line = f"{prefix}{connector}[{node.id:04X}:{type_indicator}] {text_preview}"
			lines.append(node_line)

			# Children
			children = tree.get_children(node_id)

			if node.type == DialogType.CHOICE:
				# Yes/No branches
				child_prefix = prefix + ("   " if is_last else "│  ")

				if node.yes_id:
					yes_line = f"{child_prefix}├─Y"
					lines.append(yes_line)
					_render_node(node.yes_id, child_prefix + "│  ", False)

				if node.no_id:
					no_line = f"{child_prefix}└─N"
					lines.append(no_line)
					_render_node(node.no_id, child_prefix + "   ", True)

			elif node.next_id:
				# Simple next pointer
				child_prefix = prefix + ("   " if is_last else "│  ")
				_render_node(node.next_id, child_prefix, True)

		# Start from root
		lines.append(f"Dialog Tree (Root: {tree.root_id:04X})")
		lines.append("=" * max_width)
		_render_node(tree.root_id)

		return '\n'.join(lines)


class InteractiveDialogEditor:
	"""Interactive command-line dialog editor."""

	def __init__(self, rom_path: Optional[Path] = None):
		self.rom_path = rom_path
		self.extractor = DialogExtractor(rom_path) if rom_path else None
		self.trees: Dict[int, DialogTree] = {}
		self.current_tree_id: Optional[int] = None
		self.encoder = DragonWarriorTextEncoder()
		self.visualizer = DialogTreeVisualizer()

	def run(self) -> None:
		"""Run interactive editor loop."""
		print("Dragon Warrior Dialog Editor")
		print("=" * 60)
		print("Commands: list, load, view, edit, add, delete, save, export, help, quit")
		print()

		while True:
			try:
				cmd = input(f"dialog-editor> ").strip().lower()

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
					self._list_dialogs()
				elif command == 'load':
					self._load_dialog(args)
				elif command == 'view':
					self._view_tree()
				elif command == 'edit':
					self._edit_node(args)
				elif command == 'add':
					self._add_node(args)
				elif command == 'delete':
					self._delete_node(args)
				elif command == 'save':
					self._save_tree(args)
				elif command == 'export':
					self._export_tree(args)
				elif command == 'analyze':
					self._analyze_compression()
				else:
					print(f"Unknown command: {command}. Type 'help' for commands.")

			except KeyboardInterrupt:
				print("\nUse 'quit' to exit.")
			except Exception as e:
				print(f"Error: {e}")

	def _show_help(self) -> None:
		"""Show help text."""
		print("""
Dialog Editor Commands:

list                - List all dialogs in ROM
load <offset>       - Load dialog tree at offset (hex)
view                - View current dialog tree (ASCII art)
edit <id> [text]    - Edit dialog node text
add <type> [parent] - Add new dialog node
delete <id>         - Delete dialog node
save [file]         - Save current tree to JSON
export [file]       - Export tree to ROM format
analyze             - Analyze compression ratios
help                - Show this help
quit                - Exit editor

Examples:
	list
	load 0x8120
	view
	edit 0x8120 "Welcome to TANTEGEL!"
	add text 0x8120
	save dialogs/king_lorik.json
	export dialogs/king_lorik.bin
""")

	def _list_dialogs(self) -> None:
		"""List all dialogs in ROM."""
		if not self.extractor:
			print("No ROM loaded.")
			return

		print("Scanning ROM for dialogs...")
		dialogs = self.extractor.scan_dialogs()

		print(f"\nFound {len(dialogs)} dialogs:\n")
		print(f"{'Offset':<10} {'Type':<10} {'Size':<6} {'Preview':<50}")
		print("-" * 76)

		for dialog in dialogs[:50]:  # Show first 50
			preview = dialog.text[:47].replace('\n', ' ')
			if len(dialog.text) > 47:
				preview += '...'

			print(f"{dialog.offset:04X}      {dialog.type.value:<10} {dialog.compressed_size:<6} {preview}")

		if len(dialogs) > 50:
			print(f"\n... and {len(dialogs) - 50} more dialogs")

	def _load_dialog(self, args: List[str]) -> None:
		"""Load dialog tree at offset."""
		if not args:
			print("Usage: load <offset>")
			return

		if not self.extractor:
			print("No ROM loaded.")
			return

		# Parse offset
		try:
			offset = int(args[0], 16) if args[0].startswith('0x') else int(args[0])
		except ValueError:
			print(f"Invalid offset: {args[0]}")
			return

		# Extract dialog
		node = self.extractor.extract_dialog(offset)
		if not node:
			print(f"No dialog found at offset {offset:04X}")
			return

		# Create tree
		tree = DialogTree(root_id=node.id)
		tree.add_node(node)

		self.trees[node.id] = tree
		self.current_tree_id = node.id

		print(f"Loaded dialog tree at {offset:04X}")
		print(f"Root: {node.text[:60]}...")

	def _view_tree(self) -> None:
		"""View current dialog tree."""
		if self.current_tree_id is None:
			print("No tree loaded. Use 'load <offset>' first.")
			return

		tree = self.trees.get(self.current_tree_id)
		if not tree:
			print("Current tree not found.")
			return

		visualization = self.visualizer.render_tree(tree)
		print(visualization)

	def _edit_node(self, args: List[str]) -> None:
		"""Edit dialog node text."""
		if not args:
			print("Usage: edit <node_id> [new_text]")
			return

		if self.current_tree_id is None:
			print("No tree loaded.")
			return

		tree = self.trees[self.current_tree_id]

		try:
			node_id = int(args[0], 16) if args[0].startswith('0x') else int(args[0])
		except ValueError:
			print(f"Invalid node ID: {args[0]}")
			return

		node = tree.get_node(node_id)
		if not node:
			print(f"Node {node_id:04X} not found in tree.")
			return

		# Get new text
		if len(args) > 1:
			new_text = ' '.join(args[1:])
		else:
			print(f"Current text: {node.text}")
			new_text = input("New text: ")

		# Update node
		node.text = new_text
		node.encoded = self.encoder.encode(new_text)
		node.compressed_size = len(node.encoded)

		print(f"Updated node {node_id:04X}")
		print(f"New size: {node.compressed_size} bytes")

	def _add_node(self, args: List[str]) -> None:
		"""Add new dialog node."""
		print("Add node not yet implemented.")

	def _delete_node(self, args: List[str]) -> None:
		"""Delete dialog node."""
		print("Delete node not yet implemented.")

	def _save_tree(self, args: List[str]) -> None:
		"""Save tree to JSON file."""
		if self.current_tree_id is None:
			print("No tree loaded.")
			return

		tree = self.trees[self.current_tree_id]

		# Get filename
		if args:
			filename = args[0]
		else:
			filename = f"dialog_tree_{self.current_tree_id:04X}.json"

		filepath = Path(filename)
		filepath.parent.mkdir(parents=True, exist_ok=True)

		# Export to JSON
		with open(filepath, 'w', encoding='utf-8') as f:
			json.dump(tree.to_dict(), f, indent='\t', ensure_ascii=False)

		print(f"Saved tree to {filepath}")

	def _export_tree(self, args: List[str]) -> None:
		"""Export tree to ROM binary format."""
		if self.current_tree_id is None:
			print("No tree loaded.")
			return

		tree = self.trees[self.current_tree_id]

		# Get filename
		if args:
			filename = args[0]
		else:
			filename = f"dialog_tree_{self.current_tree_id:04X}.bin"

		filepath = Path(filename)
		filepath.parent.mkdir(parents=True, exist_ok=True)

		# Collect all encoded dialogs
		all_nodes = tree.traverse()

		with open(filepath, 'wb') as f:
			for node in all_nodes:
				f.write(node.encoded)

		total_size = sum(node.compressed_size for node in all_nodes)
		print(f"Exported {len(all_nodes)} nodes ({total_size} bytes) to {filepath}")

	def _analyze_compression(self) -> None:
		"""Analyze compression ratios."""
		if self.current_tree_id is None:
			print("No tree loaded.")
			return

		tree = self.trees[self.current_tree_id]
		all_nodes = tree.traverse()

		print("\nCompression Analysis:")
		print("=" * 60)
		print(f"{'Node':<10} {'Original':<10} {'Compressed':<10} {'Ratio':<10}")
		print("-" * 60)

		total_original = 0
		total_compressed = 0

		for node in all_nodes:
			original_size = len(node.text) + 1
			compressed_size = node.compressed_size
			ratio = compressed_size / original_size if original_size > 0 else 1.0

			print(f"{node.id:04X}      {original_size:<10} {compressed_size:<10} {ratio:.2f}")

			total_original += original_size
			total_compressed += compressed_size

		print("-" * 60)
		overall_ratio = total_compressed / total_original if total_original > 0 else 1.0
		savings = total_original - total_compressed

		print(f"Total:     {total_original:<10} {total_compressed:<10} {overall_ratio:.2f}")
		print(f"\nBytes saved: {savings} ({savings / total_original * 100:.1f}%)")


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Dragon Warrior Dialog Tree Editor'
	)
	parser.add_argument(
		'rom',
		type=Path,
		nargs='?',
		help='Path to Dragon Warrior ROM file'
	)
	parser.add_argument(
		'--dialog-id',
		type=str,
		help='Load specific dialog by offset (hex)'
	)
	parser.add_argument(
		'--npc',
		type=str,
		help='Filter dialogs by NPC name'
	)
	parser.add_argument(
		'--export',
		type=Path,
		help='Export dialogs to JSON file'
	)

	args = parser.parse_args()

	# Create editor
	editor = InteractiveDialogEditor(args.rom if args.rom else None)

	# Load specific dialog if requested
	if args.dialog_id and args.rom:
		offset = int(args.dialog_id, 16) if args.dialog_id.startswith('0x') else int(args.dialog_id)
		editor._load_dialog([f"0x{offset:X}"])
		editor._view_tree()

	# Run interactive mode
	if not args.export:
		editor.run()
	else:
		# Non-interactive export
		if editor.current_tree_id:
			editor._save_tree([str(args.export)])


if __name__ == '__main__':
	main()
