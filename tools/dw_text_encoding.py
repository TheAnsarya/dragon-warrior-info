"""
Dragon Warrior Text Encoding Module

This module provides the correct character encoding for Dragon Warrior (NES)
based on the official TBL (table) file format.

The encoding maps byte values to characters as used in the ROM's text data.
Control codes are special byte values that trigger in-game text processing.

Usage:
	from dw_text_encoding import (
		encode_text, decode_bytes,
		CHAR_TO_BYTE, BYTE_TO_CHAR, CONTROL_CODES
	)

	# Encode text to bytes
	byte_data = encode_text("Hello {NAME}!")

	# Decode bytes to text
	text = decode_bytes([0x2b, 0x0e, 0x15, 0x15, 0x18])  # "Hello"
"""

import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from typing import Dict, List, Tuple, Optional

# ============================================================================
# Character Encoding Table (TBL Format)
# Based on: Dragon Warrior (NES).tbl
# ============================================================================

# Byte value -> Character mapping
BYTE_TO_CHAR: Dict[int, str] = {
	# Numbers (0x00-0x09)
	0x00: '0', 0x01: '1', 0x02: '2', 0x03: '3', 0x04: '4',
	0x05: '5', 0x06: '6', 0x07: '7', 0x08: '8', 0x09: '9',

	# Lowercase letters (0x0a-0x23)
	0x0a: 'a', 0x0b: 'b', 0x0c: 'c', 0x0d: 'd', 0x0e: 'e',
	0x0f: 'f', 0x10: 'g', 0x11: 'h', 0x12: 'i', 0x13: 'j',
	0x14: 'k', 0x15: 'l', 0x16: 'm', 0x17: 'n', 0x18: 'o',
	0x19: 'p', 0x1a: 'q', 0x1b: 'r', 0x1c: 's', 0x1d: 't',
	0x1e: 'u', 0x1f: 'v', 0x20: 'w', 0x21: 'x', 0x22: 'y',
	0x23: 'z',

	# Uppercase letters (0x24-0x3d)
	0x24: 'A', 0x25: 'B', 0x26: 'C', 0x27: 'D', 0x28: 'E',
	0x29: 'F', 0x2a: 'G', 0x2b: 'H', 0x2c: 'I', 0x2d: 'J',
	0x2e: 'K', 0x2f: 'L', 0x30: 'M', 0x31: 'N', 0x32: 'O',
	0x33: 'P', 0x34: 'Q', 0x35: 'R', 0x36: 'S', 0x37: 'T',
	0x38: 'U', 0x39: 'V', 0x3a: 'W', 0x3b: 'X', 0x3c: 'Y',
	0x3d: 'Z',

	# Punctuation and special characters (0x3e-0x5f)
	0x3e: '"',   # Opening double quote
	0x3f: '"',   # Closing double quote
	0x40: "'",   # Right single quote (apostrophe in dialog)
	0x41: '*',   # Asterisk
	0x44: ':',   # Colon
	0x45: '..',  # Double period (ellipsis-like)
	0x46: '.',   # Period (alternate)
	0x47: '.',   # Period (standard)
	0x48: ',',   # Comma
	0x49: '-',   # Hyphen/dash
	0x4b: '?',   # Question mark
	0x4c: '!',   # Exclamation mark
	0x4d: ';',   # Semicolon
	0x4e: ')',   # Right parenthesis
	0x4f: '(',   # Left parenthesis
	0x50: '`',   # Opening single quote (backtick style)
	0x51: '`',   # Opening single quote (alternate)
	0x52: ".'",  # Period + apostrophe combination
	0x53: "'",   # Apostrophe (standard)
	0x54: "'",   # Apostrophe (alternate)
	0x5f: ' ',   # Space

	# Special markers
	0x60: ' ',   # Indent/line start marker (rendered as space)
}

# Character -> Byte value mapping (reverse of above)
CHAR_TO_BYTE: Dict[str, int] = {v: k for k, v in BYTE_TO_CHAR.items()}
# Override some characters to use preferred byte values
CHAR_TO_BYTE[' '] = 0x5f    # Space
CHAR_TO_BYTE['.'] = 0x47    # Period (use standard)
CHAR_TO_BYTE["'"] = 0x53    # Apostrophe (use standard)
CHAR_TO_BYTE['"'] = 0x3e    # Double quote (use opening)

# ============================================================================
# Control Codes
# These are special byte values that trigger in-game text processing
# ============================================================================

CONTROL_CODES: Dict[int, str] = {
	# General text control
	0x57: 'INDT',   # Indent following text lines by 1 space
	0xfd: 'NEWL',   # Newline (line break)
	0xfb: 'WAIT',   # Wait for player button press
	0xfc: 'END',    # End of text block

	# Variable substitution
	0xf0: 'PLRL',   # Plural marker ("s " or " " based on quantity)
	0xf1: 'ENM2',   # Enemy name with "a" or "an" prefix
	0xf3: 'AMTP',   # Amount followed by "Point" or "Points"
	0xf4: 'ENMY',   # Enemy name
	0xf5: 'AMNT',   # Numeric amount value
	0xf6: 'SPEL',   # Spell name
	0xf7: 'ITEM',   # Item name
	0xf8: 'NAME',   # Player name
}

# Control code tags used in text strings
CONTROL_TAGS: Dict[str, int] = {
	'{INDT}': 0x57,
	'{NEWL}': 0xfd,
	'{\\n}': 0xfd,    # Alternate newline syntax
	'{WAIT}': 0xfb,
	'{END}': 0xfc,
	'{PLRL}': 0xf0,
	'{ENM2}': 0xf1,
	'{AMTP}': 0xf3,
	'{ENMY}': 0xf4,
	'{AMNT}': 0xf5,
	'{SPEL}': 0xf6,
	'{ITEM}': 0xf7,
	'{NAME}': 0xf8,
}

# Reverse mapping: byte -> tag
BYTE_TO_TAG: Dict[int, str] = {
	0x57: '{INDT}',
	0xfd: '\n',      # Render newlines naturally
	0xfb: '{WAIT}',
	0xfc: '{END}',
	0xf0: '{PLRL}',
	0xf1: '{ENM2}',
	0xf3: '{AMTP}',
	0xf4: '{ENMY}',
	0xf5: '{AMNT}',
	0xf6: '{SPEL}',
	0xf7: '{ITEM}',
	0xf8: '{NAME}',
}


# ============================================================================
# Encoding Functions
# ============================================================================

def encode_text(text: str) -> List[int]:
	"""
	Encode a text string to Dragon Warrior byte format.

	Args:
		text: Text string with optional control code tags like {NAME}, {WAIT}

	Returns:
		List of byte values

	Example:
		>>> encode_text("Hello {NAME}!")
		[0x2b, 0x0e, 0x15, 0x15, 0x18, 0x5f, 0xf8, 0x4c]
	"""
	result = []
	i = 0

	while i < len(text):
		# Check for control code tags
		if text[i] == '{':
			end = text.find('}', i)
			if end != -1:
				tag = text[i:end+1]
				if tag in CONTROL_TAGS:
					result.append(CONTROL_TAGS[tag])
					i = end + 1
					continue

		# Check for natural newline
		if text[i] == '\n':
			result.append(0xfd)
			i += 1
			continue

		# Check for special two-character sequences
		if i + 1 < len(text):
			two_char = text[i:i+2]
			if two_char == ".'":
				result.append(0x52)
				i += 2
				continue
			if two_char == '..':
				result.append(0x45)
				i += 2
				continue

		# Regular character
		char = text[i]
		if char in CHAR_TO_BYTE:
			result.append(CHAR_TO_BYTE[char])
		else:
			# Unknown character - use space as fallback
			result.append(0x5f)

		i += 1

	return result


def decode_bytes(data: List[int], use_tags: bool = True) -> str:
	"""
	Decode Dragon Warrior bytes to a text string.

	Args:
		data: List of byte values
		use_tags: If True, render control codes as {TAG} format

	Returns:
		Decoded text string

	Example:
		>>> decode_bytes([0x2b, 0x0e, 0x15, 0x15, 0x18])
		'Hello'
	"""
	result = []

	for byte_val in data:
		if byte_val in BYTE_TO_TAG:
			if use_tags:
				result.append(BYTE_TO_TAG[byte_val])
			elif byte_val == 0xfd:
				result.append('\n')
			# Skip other control codes if not using tags
		elif byte_val in BYTE_TO_CHAR:
			result.append(BYTE_TO_CHAR[byte_val])
		else:
			# Unknown byte - show as hex
			result.append(f'[${byte_val:02X}]')

	return ''.join(result)


def bytes_to_asm(data: List[int], label: Optional[str] = None) -> str:
	"""
	Convert bytes to assembly .byte directive format.

	Args:
		data: List of byte values
		label: Optional label for the first line

	Returns:
		Assembly code string
	"""
	lines = []
	bytes_per_line = 16

	for i in range(0, len(data), bytes_per_line):
		chunk = data[i:i + bytes_per_line]
		byte_str = ', '.join(f'${b:02X}' for b in chunk)

		if i == 0 and label:
			lines.append(f'{label}:  .byte {byte_str}')
		else:
			lines.append(f'        .byte {byte_str}')

	return '\n'.join(lines)


def load_tbl_file(tbl_path: str) -> Dict[int, str]:
	"""
	Load character encoding from a TBL file.

	TBL files use the format: XX=char
	where XX is a hex byte value and char is the character.

	Args:
		tbl_path: Path to TBL file

	Returns:
		Dictionary mapping byte values to characters
	"""
	encoding = BYTE_TO_CHAR.copy()

	with open(tbl_path, 'r', encoding='utf-8') as f:
		for line in f:
			line = line.strip()
			if '=' in line and not line.startswith('#'):
				parts = line.split('=', 1)
				try:
					byte_val = int(parts[0], 16)
					char = parts[1] if parts[1] else ' '
					encoding[byte_val] = char
				except (ValueError, IndexError):
					continue

	return encoding


# ============================================================================
# Utility Functions
# ============================================================================

def get_text_length(text: str) -> int:
	"""
	Calculate the encoded byte length of a text string.

	Args:
		text: Text string with optional control codes

	Returns:
		Number of bytes when encoded
	"""
	return len(encode_text(text))


def strip_control_codes(text: str) -> str:
	"""
	Remove control code tags from text.

	Args:
		text: Text with control code tags

	Returns:
		Text with tags removed
	"""
	import re
	# Remove {TAG} patterns
	text = re.sub(r'\{[A-Z0-9]+\}', '', text)
	# Clean up extra whitespace
	text = ' '.join(text.split())
	return text.strip()


def validate_text(text: str) -> Tuple[bool, List[str]]:
	"""
	Validate text for encoding compatibility.

	Args:
		text: Text to validate

	Returns:
		Tuple of (is_valid, list of error messages)
	"""
	errors = []
	import re

	# Check for unknown characters, skipping control code tags
	i = 0
	while i < len(text):
		char = text[i]
		if char == '{':
			# Skip entire control code tag
			end = text.find('}', i)
			if end != -1:
				i = end + 1
				continue
		if char == '\n':
			i += 1
			continue
		if char not in CHAR_TO_BYTE:
			errors.append(f"Unknown character '{char}' at position {i}")
		i += 1

	# Check for unclosed tags
	if text.count('{') != text.count('}'):
		errors.append("Mismatched { } brackets")

	# Check for invalid tags
	tag_pattern = r'\{([A-Z0-9]+)\}'
	for match in re.finditer(tag_pattern, text):
		tag = '{' + match.group(1) + '}'
		if tag not in CONTROL_TAGS:
			errors.append(f"Unknown control tag: {tag}")

	return len(errors) == 0, errors


# ============================================================================
# Module Test
# ============================================================================

if __name__ == '__main__':
	# Test encoding/decoding
	test_texts = [
		"Hello, world!",
		"{NAME} found the {ITEM}!",
		"`Good morning.'{WAIT}{END}",
		"Thou art dead.\n{END}",
	]

	print("Dragon Warrior Text Encoding Test")
	print("=" * 50)

	for text in test_texts:
		encoded = encode_text(text)
		decoded = decode_bytes(encoded)

		print(f"\nOriginal: {repr(text)}")
		print(f"Encoded:  {[f'${b:02X}' for b in encoded]}")
		print(f"Decoded:  {repr(decoded)}")

		is_valid, errors = validate_text(text)
		if not is_valid:
			print(f"Errors:   {errors}")
