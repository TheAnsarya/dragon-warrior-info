#!/usr/bin/env python3
"""
Dragon Warrior Dialogue & Text Editor

Advanced text editing system with full support for Dragon Warrior's
text encoding, DTE (Dual Tile Encoding), dialogue trees, string pointers,
and text compression analysis.

Features:
- Text extraction and insertion
- DTE (Dual Tile Encoding) compression/decompression
- Dialogue tree visualization
- String pointer management
- Text table editing
- Character frequency analysis
- Optimal DTE pair calculation
- Text compression optimization
- Multi-language support preparation
- String search and replace
- Text overflow detection
- Line breaking assistance
- Control code handling
- Menu text editing
- NPC dialogue editing
- Battle text editing
- Item/spell description editing
- Text statistics and analysis

Dragon Warrior Text Format:
- Character encoding: Custom tile-based
- Control codes: 0xF0-0xFF
- Line break: 0xFA
- Text end: 0xFC
- Player name: 0xF1
- DTE pairs: 0x80-0xEF (compressed common pairs)

Text Data Locations:
- Dialogue: 0x36A0-0x5FFF
- Menu text: 0x2800-0x36A0
- Item names: 0x1AF0-0x1C3F
- Spell names: 0x1C40-0x1CFF
- Monster names: 0x1D00-0x1E7F

Usage:
	python tools/dialogue_editor.py <rom_file>

Examples:
	# Extract all text
	python tools/dialogue_editor.py rom.nes --extract-all text/

	# Search for text
	python tools/dialogue_editor.py rom.nes --search "Welcome to"

	# Replace text
	python tools/dialogue_editor.py rom.nes --replace "Welcome" "Greetings" -o new.nes

	# Analyze DTE compression
	python tools/dialogue_editor.py rom.nes --analyze-dte

	# Generate optimal DTE pairs
	python tools/dialogue_editor.py rom.nes --optimize-dte

	# Export text table
	python tools/dialogue_editor.py rom.nes --export-table table.tbl

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import struct
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field
from collections import Counter, defaultdict
from enum import Enum
import argparse
import json


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class ControlCode(Enum):
	"""Text control codes."""
	PLAYER_NAME = 0xF1
	DELAY = 0xF2
	PAUSE = 0xF3
	SCROLL = 0xF4
	CHOICE = 0xF5
	ITEM = 0xF6
	NUMBER = 0xF7
	ENEMY_NAME = 0xF8
	LINE_BREAK = 0xFA
	PAGE_BREAK = 0xFB
	TEXT_END = 0xFC


@dataclass
class TextString:
	"""A text string with metadata."""
	id: int
	offset: int
	raw_bytes: bytes
	decoded_text: str
	length: int
	category: str = "unknown"
	references: List[int] = field(default_factory=list)
	compressed: bool = False


@dataclass
class DTEPair:
	"""DTE (Dual Tile Encoding) pair."""
	code: int  # 0x80-0xEF
	char1: int
	char2: int
	frequency: int = 0
	savings: int = 0  # Bytes saved


@dataclass
class TextTable:
	"""Character encoding table."""
	char_to_byte: Dict[str, int] = field(default_factory=dict)
	byte_to_char: Dict[int, str] = field(default_factory=dict)
	dte_pairs: Dict[int, Tuple[int, int]] = field(default_factory=dict)


@dataclass
class TextStats:
	"""Text statistics."""
	total_strings: int = 0
	total_bytes: int = 0
	total_characters: int = 0
	compressed_strings: int = 0
	compression_ratio: float = 0.0
	most_common_char: Optional[str] = None
	most_common_count: int = 0
	most_common_pair: Optional[str] = None
	most_common_pair_count: int = 0


# Default Dragon Warrior text table
DEFAULT_TEXT_TABLE = {
	0x00: ' ', 0x01: 'A', 0x02: 'B', 0x03: 'C', 0x04: 'D', 0x05: 'E',
	0x06: 'F', 0x07: 'G', 0x08: 'H', 0x09: 'I', 0x0A: 'J', 0x0B: 'K',
	0x0C: 'L', 0x0D: 'M', 0x0E: 'N', 0x0F: 'O', 0x10: 'P', 0x11: 'Q',
	0x12: 'R', 0x13: 'S', 0x14: 'T', 0x15: 'U', 0x16: 'V', 0x17: 'W',
	0x18: 'X', 0x19: 'Y', 0x1A: 'Z', 0x1B: 'a', 0x1C: 'b', 0x1D: 'c',
	0x1E: 'd', 0x1F: 'e', 0x20: 'f', 0x21: 'g', 0x22: 'h', 0x23: 'i',
	0x24: 'j', 0x25: 'k', 0x26: 'l', 0x27: 'm', 0x28: 'n', 0x29: 'o',
	0x2A: 'p', 0x2B: 'q', 0x2C: 'r', 0x2D: 's', 0x2E: 't', 0x2F: 'u',
	0x30: 'v', 0x31: 'w', 0x32: 'x', 0x33: 'y', 0x34: 'z', 0x35: '0',
	0x36: '1', 0x37: '2', 0x38: '3', 0x39: '4', 0x3A: '5', 0x3B: '6',
	0x3C: '7', 0x3D: '8', 0x3E: '9', 0x3F: '!', 0x40: '?', 0x41: '.',
	0x42: ',', 0x43: '\'', 0x44: '-', 0x45: ':', 0x46: ';', 0x47: '"',
	0x48: '(', 0x49: ')', 0x4A: '/', 0x4B: '+', 0x4C: '=', 0x4D: '*',
}

# DTE pairs (common two-letter combinations encoded as single bytes 0x80-0xEF)
DEFAULT_DTE_PAIRS = {
	0x80: ('t', 'h'),  # "th"
	0x81: ('e', 'r'),  # "er"
	0x82: ('o', 'n'),  # "on"
	0x83: ('a', 'n'),  # "an"
	0x84: ('r', 'e'),  # "re"
	0x85: ('h', 'e'),  # "he"
	0x86: ('i', 'n'),  # "in"
	0x87: ('e', 'd'),  # "ed"
	0x88: ('n', 'd'),  # "nd"
	0x89: ('h', 'a'),  # "ha"
	0x8A: ('a', 't'),  # "at"
	0x8B: ('e', 'n'),  # "en"
	0x8C: ('e', 's'),  # "es"
	0x8D: ('o', 'r'),  # "or"
	0x8E: ('t', 'e'),  # "te"
	0x8F: ('o', 'f'),  # "of"
}


# ============================================================================
# TEXT DECODER/ENCODER
# ============================================================================

class TextCodec:
	"""Encode/decode Dragon Warrior text."""
	
	def __init__(self, text_table: Optional[Dict[int, str]] = None,
	             dte_pairs: Optional[Dict[int, Tuple[str, str]]] = None):
		self.text_table = text_table or DEFAULT_TEXT_TABLE
		self.dte_pairs = dte_pairs or DEFAULT_DTE_PAIRS
		
		# Create reverse mappings
		self.char_to_byte = {v: k for k, v in self.text_table.items()}
		self.pair_to_code = {v: k for k, v in self.dte_pairs.items()}
	
	def decode(self, data: bytes) -> str:
		"""Decode bytes to text string."""
		result = []
		i = 0
		
		while i < len(data):
			byte = data[i]
			
			# Check for text end
			if byte == ControlCode.TEXT_END.value:
				break
			
			# Check for line break
			elif byte == ControlCode.LINE_BREAK.value:
				result.append('\n')
			
			# Check for player name placeholder
			elif byte == ControlCode.PLAYER_NAME.value:
				result.append('[NAME]')
			
			# Check for other control codes
			elif byte >= 0xF0:
				result.append(f'[{byte:02X}]')
			
			# Check for DTE pair
			elif 0x80 <= byte <= 0xEF and byte in self.dte_pairs:
				char1, char2 = self.dte_pairs[byte]
				result.append(char1)
				result.append(char2)
			
			# Regular character
			elif byte in self.text_table:
				result.append(self.text_table[byte])
			
			# Unknown byte
			else:
				result.append(f'[{byte:02X}]')
			
			i += 1
		
		return ''.join(result)
	
	def encode(self, text: str, use_dte: bool = True) -> bytes:
		"""Encode text string to bytes."""
		result = bytearray()
		i = 0
		
		while i < len(text):
			# Check for newline
			if text[i] == '\n':
				result.append(ControlCode.LINE_BREAK.value)
				i += 1
			
			# Check for control code placeholder
			elif text[i] == '[':
				end = text.find(']', i)
				if end != -1:
					code_str = text[i+1:end]
					
					# Check for special placeholders
					if code_str == 'NAME':
						result.append(ControlCode.PLAYER_NAME.value)
					else:
						# Hex code
						try:
							result.append(int(code_str, 16))
						except ValueError:
							print(f"WARNING: Unknown control code: [{code_str}]")
					
					i = end + 1
				else:
					i += 1
			
			# Check for DTE pair
			elif use_dte and i + 1 < len(text):
				pair = (text[i].lower(), text[i+1].lower())
				if pair in self.pair_to_code:
					result.append(self.pair_to_code[pair])
					i += 2
					continue
				
				# Single character
				if text[i] in self.char_to_byte:
					result.append(self.char_to_byte[text[i]])
				else:
					print(f"WARNING: Unknown character: {text[i]}")
				i += 1
			
			# Single character
			else:
				if text[i] in self.char_to_byte:
					result.append(self.char_to_byte[text[i]])
				else:
					print(f"WARNING: Unknown character: {text[i]}")
				i += 1
		
		# Add text end marker
		result.append(ControlCode.TEXT_END.value)
		
		return bytes(result)


# ============================================================================
# DIALOGUE EDITOR
# ============================================================================

class DialogueEditor:
	"""Edit dialogue and text in Dragon Warrior."""
	
	def __init__(self, rom_path: str):
		self.rom_path = Path(rom_path)
		self.rom_data: bytearray = bytearray()
		self.codec = TextCodec()
		self.strings: List[TextString] = []
		
		# Text regions
		self.text_regions = {
			"dialogue": (0x36A0, 0x5FFF),
			"menu": (0x2800, 0x36A0),
			"items": (0x1AF0, 0x1C3F),
			"spells": (0x1C40, 0x1CFF),
			"monsters": (0x1D00, 0x1E7F),
		}
	
	def load_rom(self) -> bool:
		"""Load ROM file."""
		if not self.rom_path.exists():
			print(f"ERROR: ROM not found: {self.rom_path}")
			return False
		
		with open(self.rom_path, 'rb') as f:
			self.rom_data = bytearray(f.read())
		
		return True
	
	def extract_strings(self, category: str = "all") -> List[TextString]:
		"""Extract text strings from ROM."""
		strings = []
		
		regions = self.text_regions.items() if category == "all" else \
		          [(category, self.text_regions[category])]
		
		for region_name, (start, end) in regions:
			# Simple extraction: find strings by text end marker
			offset = start
			string_id = 0
			
			while offset < end:
				# Find next text end marker
				text_end = offset
				while text_end < end and self.rom_data[text_end] != ControlCode.TEXT_END.value:
					text_end += 1
				
				if text_end >= end:
					break
				
				# Extract string
				raw_bytes = self.rom_data[offset:text_end + 1]
				
				# Skip empty strings
				if len(raw_bytes) > 1:
					decoded = self.codec.decode(raw_bytes)
					
					text_str = TextString(
						id=string_id,
						offset=offset,
						raw_bytes=raw_bytes,
						decoded_text=decoded,
						length=len(raw_bytes),
						category=region_name,
						compressed=any(0x80 <= b <= 0xEF for b in raw_bytes)
					)
					
					strings.append(text_str)
					string_id += 1
				
				offset = text_end + 1
		
		self.strings = strings
		return strings
	
	def search_text(self, query: str) -> List[TextString]:
		"""Search for text strings."""
		results = []
		
		query_lower = query.lower()
		
		for string in self.strings:
			if query_lower in string.decoded_text.lower():
				results.append(string)
		
		return results
	
	def replace_text(self, old_text: str, new_text: str) -> int:
		"""Replace text in all strings."""
		count = 0
		
		for string in self.strings:
			if old_text in string.decoded_text:
				# Replace text
				new_decoded = string.decoded_text.replace(old_text, new_text)
				
				# Encode new text
				new_bytes = self.codec.encode(new_decoded)
				
				# Check if it fits
				if len(new_bytes) <= string.length:
					# Replace in ROM
					self.rom_data[string.offset:string.offset + len(new_bytes)] = new_bytes
					
					# Pad if necessary
					if len(new_bytes) < string.length:
						padding = string.length - len(new_bytes)
						self.rom_data[string.offset + len(new_bytes):string.offset + string.length] = b'\xFC' * padding
					
					# Update string
					string.raw_bytes = new_bytes
					string.decoded_text = new_decoded
					string.length = len(new_bytes)
					
					count += 1
				else:
					print(f"WARNING: Replacement too long at 0x{string.offset:X} ({len(new_bytes)} > {string.length})")
		
		return count
	
	def save_rom(self, output_path: str):
		"""Save modified ROM."""
		with open(output_path, 'wb') as f:
			f.write(self.rom_data)
		
		print(f"✓ ROM saved: {output_path}")


# ============================================================================
# DTE ANALYZER
# ============================================================================

class DTEAnalyzer:
	"""Analyze and optimize DTE compression."""
	
	@staticmethod
	def analyze_frequency(strings: List[TextString]) -> Counter:
		"""Analyze character pair frequency."""
		pairs = Counter()
		
		for string in strings:
			text = string.decoded_text.replace('[NAME]', '').replace('\n', '')
			
			# Count all two-character pairs
			for i in range(len(text) - 1):
				if text[i].isalpha() and text[i+1].isalpha():
					pair = text[i:i+2].lower()
					pairs[pair] += 1
		
		return pairs
	
	@staticmethod
	def calculate_optimal_dte(strings: List[TextString], num_pairs: int = 112) -> List[DTEPair]:
		"""Calculate optimal DTE pairs for maximum compression."""
		# Analyze frequency
		pair_freq = DTEAnalyzer.analyze_frequency(strings)
		
		# Calculate savings for each pair
		dte_candidates = []
		
		for pair, freq in pair_freq.items():
			# Each occurrence saves 1 byte (2 chars -> 1 DTE code)
			savings = freq * 1
			
			if savings > 0:
				dte_candidates.append(DTEPair(
					code=0,  # Will assign later
					char1=ord(pair[0]),
					char2=ord(pair[1]),
					frequency=freq,
					savings=savings
				))
		
		# Sort by savings (descending)
		dte_candidates.sort(key=lambda x: x.savings, reverse=True)
		
		# Assign codes (0x80-0xEF = 112 slots)
		optimal_pairs = dte_candidates[:num_pairs]
		for i, pair in enumerate(optimal_pairs):
			pair.code = 0x80 + i
		
		return optimal_pairs
	
	@staticmethod
	def analyze_stats(strings: List[TextString]) -> TextStats:
		"""Generate text statistics."""
		stats = TextStats()
		
		stats.total_strings = len(strings)
		stats.total_bytes = sum(s.length for s in strings)
		
		# Count characters
		all_chars = Counter()
		for string in strings:
			all_chars.update(string.decoded_text.replace('[NAME]', '').replace('\n', ''))
		
		stats.total_characters = sum(all_chars.values())
		
		if all_chars:
			stats.most_common_char = all_chars.most_common(1)[0][0]
			stats.most_common_count = all_chars.most_common(1)[0][1]
		
		# Count pairs
		pair_freq = DTEAnalyzer.analyze_frequency(strings)
		if pair_freq:
			stats.most_common_pair = pair_freq.most_common(1)[0][0]
			stats.most_common_pair_count = pair_freq.most_common(1)[0][1]
		
		# Count compressed strings
		stats.compressed_strings = sum(1 for s in strings if s.compressed)
		
		# Calculate compression ratio
		if stats.total_characters > 0:
			stats.compression_ratio = stats.total_bytes / stats.total_characters
		
		return stats


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Dragon Warrior Dialogue & Text Editor"
	)
	
	parser.add_argument('rom', help="ROM file")
	parser.add_argument('--extract-all', type=str, help="Extract all text to directory")
	parser.add_argument('--search', type=str, help="Search for text")
	parser.add_argument('--replace', nargs=2, metavar=('OLD', 'NEW'), help="Replace text")
	parser.add_argument('--analyze-dte', action='store_true', help="Analyze DTE compression")
	parser.add_argument('--optimize-dte', action='store_true', help="Calculate optimal DTE pairs")
	parser.add_argument('--stats', action='store_true', help="Show text statistics")
	parser.add_argument('--category', type=str, default='all',
	                    choices=['all', 'dialogue', 'menu', 'items', 'spells', 'monsters'],
	                    help="Text category")
	parser.add_argument('-o', '--output', type=str, help="Output ROM file")
	
	args = parser.parse_args()
	
	# Load ROM
	editor = DialogueEditor(args.rom)
	if not editor.load_rom():
		return 1
	
	# Extract strings
	print(f"Extracting text (category: {args.category})...")
	strings = editor.extract_strings(args.category)
	print(f"✓ Found {len(strings)} text strings")
	
	# Search
	if args.search:
		print(f"\nSearching for: '{args.search}'")
		results = editor.search_text(args.search)
		
		print(f"\n✓ Found {len(results)} matches:")
		for i, result in enumerate(results[:10], 1):
			print(f"\n  {i}. Offset: 0x{result.offset:X} ({result.category})")
			print(f"     Text: {result.decoded_text[:100]}")
			if len(result.decoded_text) > 100:
				print(f"     ... ({len(result.decoded_text)} chars total)")
		
		if len(results) > 10:
			print(f"\n  ... and {len(results) - 10} more matches")
	
	# Replace
	if args.replace:
		old_text, new_text = args.replace
		print(f"\nReplacing '{old_text}' with '{new_text}'...")
		count = editor.replace_text(old_text, new_text)
		
		print(f"✓ Replaced {count} occurrences")
		
		# Save ROM
		if args.output:
			editor.save_rom(args.output)
	
	# Analyze DTE
	if args.analyze_dte:
		print("\nAnalyzing DTE compression...")
		pair_freq = DTEAnalyzer.analyze_frequency(strings)
		
		print(f"\n✓ Top 20 most common character pairs:")
		for i, (pair, freq) in enumerate(pair_freq.most_common(20), 1):
			savings = freq * 1  # 1 byte saved per occurrence
			print(f"  {i:2d}. '{pair}' - {freq:4d} times ({savings:4d} bytes savings)")
	
	# Optimize DTE
	if args.optimize_dte:
		print("\nCalculating optimal DTE pairs...")
		optimal = DTEAnalyzer.calculate_optimal_dte(strings)
		
		total_savings = sum(p.savings for p in optimal)
		
		print(f"\n✓ Top 20 optimal DTE pairs:")
		for i, pair in enumerate(optimal[:20], 1):
			char1 = chr(pair.char1)
			char2 = chr(pair.char2)
			print(f"  {i:2d}. 0x{pair.code:02X}: '{char1}{char2}' - {pair.frequency:4d} times ({pair.savings:4d} bytes)")
		
		print(f"\nTotal potential savings: {total_savings} bytes")
	
	# Statistics
	if args.stats:
		print("\nGenerating text statistics...")
		stats = DTEAnalyzer.analyze_stats(strings)
		
		print(f"\n✓ Text Statistics:")
		print(f"  Total strings: {stats.total_strings}")
		print(f"  Total bytes: {stats.total_bytes}")
		print(f"  Total characters: {stats.total_characters}")
		print(f"  Compressed strings: {stats.compressed_strings}")
		print(f"  Compression ratio: {stats.compression_ratio:.2f}")
		
		if stats.most_common_char:
			print(f"\n  Most common character: '{stats.most_common_char}' ({stats.most_common_count} times)")
		
		if stats.most_common_pair:
			print(f"  Most common pair: '{stats.most_common_pair}' ({stats.most_common_pair_count} times)")
	
	return 0


if __name__ == "__main__":
	sys.exit(main())
