"""
Generate Dragon Warrior dialog assembly from JSON.

This tool takes a dialogs JSON file and generates the corresponding
assembly code for Bank02.asm, properly encoding text using the TBL
character table and control codes.

This is the reverse of extract_dialogs_from_asm.py and enables the
full edit cycle: extract → edit JSON → regenerate ASM.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Any


# Character encoding: character -> byte value
# Reverse of the TBL encoding used in extraction
CHAR_TO_BYTE = {
	# Numbers
	'0': 0x00, '1': 0x01, '2': 0x02, '3': 0x03, '4': 0x04,
	'5': 0x05, '6': 0x06, '7': 0x07, '8': 0x08, '9': 0x09,
	# Lowercase letters
	'a': 0x0A, 'b': 0x0B, 'c': 0x0C, 'd': 0x0D, 'e': 0x0E,
	'f': 0x0F, 'g': 0x10, 'h': 0x11, 'i': 0x12, 'j': 0x13,
	'k': 0x14, 'l': 0x15, 'm': 0x16, 'n': 0x17, 'o': 0x18,
	'p': 0x19, 'q': 0x1A, 'r': 0x1B, 's': 0x1C, 't': 0x1D,
	'u': 0x1E, 'v': 0x1F, 'w': 0x20, 'x': 0x21, 'y': 0x22,
	'z': 0x23,
	# Uppercase letters
	'A': 0x24, 'B': 0x25, 'C': 0x26, 'D': 0x27, 'E': 0x28,
	'F': 0x29, 'G': 0x2A, 'H': 0x2B, 'I': 0x2C, 'J': 0x2D,
	'K': 0x2E, 'L': 0x2F, 'M': 0x30, 'N': 0x31, 'O': 0x32,
	'P': 0x33, 'Q': 0x34, 'R': 0x35, 'S': 0x36, 'T': 0x37,
	'U': 0x38, 'V': 0x39, 'W': 0x3A, 'X': 0x3B, 'Y': 0x3C,
	'Z': 0x3D,
	# Punctuation and special characters
	'"': 0x3E,  # Double quote
	':': 0x44,
	'.': 0x47,  # Period (use 0x46 or 0x47)
	',': 0x48,
	'-': 0x49,
	'?': 0x4B,
	'!': 0x4C,
	';': 0x4D,
	')': 0x4E,
	'(': 0x4F,
	'`': 0x50,  # Opening single quote
	"'": 0x53,  # Apostrophe
	' ': 0x5F,  # Space
}

# Control codes: tag -> byte value
CONTROL_TO_BYTE = {
	'{INDT}': 0x57,
	'{PLRL}': 0xF0,
	'{ENM2}': 0xF1,
	'{AMTP}': 0xF3,
	'{ENMY}': 0xF4,
	'{AMNT}': 0xF5,
	'{SPEL}': 0xF6,
	'{ITEM}': 0xF7,
	'{NAME}': 0xF8,
	'{WAIT}': 0xFB,
	'{END}': 0xFC,
	'\n': 0xFD,
}

# Control code names for comments
CONTROL_NAMES = {
	0x57: 'INDT',
	0xF0: 'PLRL',
	0xF1: 'ENM2',
	0xF3: 'AMTP',
	0xF4: 'ENMY',
	0xF5: 'AMNT',
	0xF6: 'SPEL',
	0xF7: 'ITEM',
	0xF8: 'NAME',
	0xFB: 'WAIT',
	0xFC: 'END',
	0xFD: '\\n',
}

# Byte to character for comment generation
BYTE_TO_CHAR = {v: k for k, v in CHAR_TO_BYTE.items()}
BYTE_TO_CHAR[0x5F] = '_'  # Show space as underscore in comments
BYTE_TO_CHAR[0x60] = '_'  # Indent marker
BYTE_TO_CHAR[0x40] = "'"  # Alternate apostrophe
BYTE_TO_CHAR[0x52] = ".'"  # Period + apostrophe combo
BYTE_TO_CHAR[0x45] = '..'  # Double period


def encode_text(text: str) -> List[int]:
	"""
	Encode text string to byte list.

	Args:
		text: Text with optional control code tags

	Returns:
		List of byte values
	"""
	result = []
	i = 0

	while i < len(text):
		# Check for control code tags
		if text[i] == '{':
			end = text.find('}', i)
			if end != -1:
				tag = text[i:end+1]
				if tag in CONTROL_TO_BYTE:
					result.append(CONTROL_TO_BYTE[tag])
					i = end + 1
					continue

		# Check for newline
		if text[i] == '\n':
			result.append(0xFD)
			i += 1
			continue

		# Check for special sequences
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
			# Unknown character - skip or use placeholder
			print(f"Warning: Unknown character '{char}' (0x{ord(char):02X})")
			result.append(0x5F)  # Replace with space

		i += 1

	return result


def byte_to_comment_char(byte_val: int) -> str:
	"""
	Convert byte value to comment character representation.

	Args:
		byte_val: Byte value

	Returns:
		Character representation for ASM comment
	"""
	if byte_val in CONTROL_NAMES:
		return CONTROL_NAMES[byte_val]
	if byte_val in BYTE_TO_CHAR:
		return BYTE_TO_CHAR[byte_val]
	return f'[${byte_val:02X}]'


def format_byte_line(
	bytes_data: List[int],
	label: Optional[str] = None,
	max_bytes: int = 16,
	include_comments: bool = True
) -> List[str]:
	"""
	Format bytes as .byte directive lines.

	Args:
		bytes_data: List of byte values
		label: Optional label for first line
		max_bytes: Maximum bytes per line
		include_comments: Include character comments

	Returns:
		List of formatted assembly lines
	"""
	lines = []

	for i in range(0, len(bytes_data), max_bytes):
		chunk = bytes_data[i:i + max_bytes]

		# Format bytes
		byte_str = ', '.join(f'${b:02X}' for b in chunk)

		# Generate comment
		if include_comments:
			comment_chars = [byte_to_comment_char(b) for b in chunk]
			# Pad comment chars to align
			comment = ''.join(f'{c:>5}' for c in comment_chars)
			comment_line = f';{comment}'
		else:
			comment_line = ''

		# Build line
		if i == 0 and label:
			line = f'{label}:  .byte {byte_str}'
		else:
			line = f'        .byte {byte_str}'

		# Add comment if not too long
		if include_comments and len(line) < 70:
			# Put comment on separate line above
			lines.append(comment_line)

		lines.append(line)

	return lines


def generate_dialog_asm(
	dialogs: List[Dict[str, Any]],
	include_comments: bool = True
) -> str:
	"""
	Generate assembly code for all dialogs.

	Args:
		dialogs: List of dialog entries from JSON
		include_comments: Include character mapping comments

	Returns:
		Generated assembly code string
	"""
	output_lines = [
		';' + '=' * 100,
		'; Dragon Warrior Dialog Data - Generated from JSON',
		'; This file is auto-generated by generate_dialog_tables.py',
		'; Do not edit directly - modify assets/json/dialogs_extracted.json instead',
		';' + '=' * 100,
		'',
	]

	# Group dialogs by block
	blocks: Dict[str, List[Dict]] = {}
	for dialog in dialogs:
		block = dialog.get('block', 'TextBlock1')
		if block not in blocks:
			blocks[block] = []
		blocks[block].append(dialog)

	# Generate each block
	for block_name, block_dialogs in sorted(blocks.items()):
		output_lines.append(f';{"-" * 100}')
		output_lines.append(f'{block_name}:')
		output_lines.append('')

		for dialog in block_dialogs:
			label = dialog.get('label', f'Dialog_{dialog.get("id", 0)}')

			# Get bytes - either from stored bytes_hex or encode from text
			if 'bytes_hex' in dialog and dialog['bytes_hex']:
				# Convert hex strings like "$F4" to integers
				byte_data = [int(b.replace('$', '0x'), 16) for b in dialog['bytes_hex']]
			elif 'bytes' in dialog and dialog['bytes']:
				# Legacy format - integer array
				byte_data = dialog['bytes']
			else:
				text = dialog.get('text', '')
				# Ensure END code if not present
				if not text.endswith('{END}'):
					text += '{END}'
				byte_data = encode_text(text)

			# Generate assembly lines
			asm_lines = format_byte_line(
				byte_data,
				label=label,
				include_comments=include_comments
			)

			output_lines.extend(asm_lines)
			output_lines.append('')
			output_lines.append(';' + '-' * 100)
			output_lines.append('')

	return '\n'.join(output_lines)


def load_dialogs_json(json_path: str) -> List[Dict[str, Any]]:
	"""
	Load dialogs from JSON file.

	Args:
		json_path: Path to JSON file

	Returns:
		List of dialog entries
	"""
	with open(json_path, 'r', encoding='utf-8') as f:
		data = json.load(f)

	# Handle both formats
	if 'dialogs' in data:
		return data['dialogs']
	elif isinstance(data, list):
		return data
	elif isinstance(data, dict):
		# Convert dict format to list
		return list(data.values())

	return []


def main():
	"""Main entry point."""
	import argparse

	parser = argparse.ArgumentParser(
		description='Generate Dragon Warrior dialog assembly from JSON'
	)
	parser.add_argument(
		'--input', '-i',
		default='assets/json/dialogs_extracted.json',
		help='Input JSON file (default: assets/json/dialogs_extracted.json)'
	)
	parser.add_argument(
		'--output', '-o',
		default='source_files/generated/dialog_data.asm',
		help='Output ASM file (default: source_files/generated/dialog_data.asm)'
	)
	parser.add_argument(
		'--no-comments',
		action='store_true',
		help='Exclude character mapping comments'
	)
	parser.add_argument(
		'--verbose', '-v',
		action='store_true',
		help='Print verbose output'
	)

	args = parser.parse_args()

	# Find project root
	script_dir = Path(__file__).parent
	project_root = script_dir.parent

	input_path = project_root / args.input
	output_path = project_root / args.output

	if not input_path.exists():
		print(f"Error: Input file not found: {input_path}")
		return 1

	# Load dialogs
	dialogs = load_dialogs_json(str(input_path))

	if args.verbose:
		print(f"Loaded {len(dialogs)} dialogs from: {input_path}")

	# Generate assembly
	asm_code = generate_dialog_asm(
		dialogs,
		include_comments=not args.no_comments
	)

	# Save output
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with open(output_path, 'w', encoding='utf-8') as f:
		f.write(asm_code)

	print(f"Generated dialog assembly: {output_path}")
	print(f"  Dialogs: {len(dialogs)}")

	# Verify round-trip by comparing byte counts
	if args.verbose:
		total_bytes = sum(len(d.get('bytes', [])) for d in dialogs)
		print(f"  Total bytes: {total_bytes}")

	return 0


if __name__ == '__main__':
	exit(main())
