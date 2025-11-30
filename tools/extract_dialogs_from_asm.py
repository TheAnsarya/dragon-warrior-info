"""
Extract dialog text from Dragon Warrior Bank02.asm using proper TBL encoding.

This tool parses the Bank02.asm file and extracts all dialog text entries,
decoding them using the character table from the TBL file and handling
special control codes.

Control Codes:
- $57: INDT (indent following lines by 1 space)
- $F0: PLRL (plural "s " or " ") / PNTS (Point or Points)
- $F1: ENM2 (enemy name with "a" or "an" prefix)
- $F3: AMTP (numeric amount followed by Point/Points)
- $F4: ENMY (enemy name)
- $F5: AMNT (numeric amount)
- $F6: SPEL (spell name)
- $F7: ITEM (item name)
- $F8: NAME (player name)
- $FB: WAIT (wait for button press)
- $FC: END (end of text)
- $FD: \\n (newline)

Character Encoding (from TBL):
- $00-$09: 0-9
- $0A-$23: a-z
- $24-$3D: A-Z
- $3E-$5F: punctuation and special characters
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


def load_tbl_encoding(tbl_path: Optional[str] = None) -> Dict[int, str]:
	"""
	Load character encoding from TBL file.

	Args:
		tbl_path: Path to the TBL file. If None, uses default encoding.

	Returns:
		Dictionary mapping byte values to characters.
	"""
	# Default encoding based on Dragon Warrior TBL and Bank02.asm analysis
	encoding = {
		# Numbers
		0x00: '0', 0x01: '1', 0x02: '2', 0x03: '3', 0x04: '4',
		0x05: '5', 0x06: '6', 0x07: '7', 0x08: '8', 0x09: '9',
		# Lowercase letters
		0x0A: 'a', 0x0B: 'b', 0x0C: 'c', 0x0D: 'd', 0x0E: 'e',
		0x0F: 'f', 0x10: 'g', 0x11: 'h', 0x12: 'i', 0x13: 'j',
		0x14: 'k', 0x15: 'l', 0x16: 'm', 0x17: 'n', 0x18: 'o',
		0x19: 'p', 0x1A: 'q', 0x1B: 'r', 0x1C: 's', 0x1D: 't',
		0x1E: 'u', 0x1F: 'v', 0x20: 'w', 0x21: 'x', 0x22: 'y',
		0x23: 'z',
		# Uppercase letters
		0x24: 'A', 0x25: 'B', 0x26: 'C', 0x27: 'D', 0x28: 'E',
		0x29: 'F', 0x2A: 'G', 0x2B: 'H', 0x2C: 'I', 0x2D: 'J',
		0x2E: 'K', 0x2F: 'L', 0x30: 'M', 0x31: 'N', 0x32: 'O',
		0x33: 'P', 0x34: 'Q', 0x35: 'R', 0x36: 'S', 0x37: 'T',
		0x38: 'U', 0x39: 'V', 0x3A: 'W', 0x3B: 'X', 0x3C: 'Y',
		0x3D: 'Z',
		# Punctuation and special characters
		0x3E: '"', 0x3F: '"',  # Opening/closing quotes
		0x40: "'",  # Apostrophe (right single quote)
		0x41: '*',
		0x44: ':',
		0x45: '..', 0x46: '.', 0x47: '.',
		0x48: ',',
		0x49: '-',
		0x4B: '?',
		0x4C: '!',
		0x4D: ';',
		0x4E: ')',
		0x4F: '(',
		0x50: '`',  # Opening single quote (backtick)
		0x51: '`',
		0x52: ".'",  # Period + apostrophe
		0x53: "'",  # Apostrophe
		0x54: "'",
		0x5F: ' ',  # Space
		# Special start-of-line marker
		0x60: ' ',  # Indent/start marker (treated as space)
	}

	# Load from TBL file if provided
	if tbl_path and Path(tbl_path).exists():
		try:
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
		except Exception as e:
			print(f"Warning: Could not load TBL file: {e}")

	return encoding


# Control code definitions
CONTROL_CODES = {
	0x57: '{INDT}',      # Indent following text
	0xF0: '{PLRL}',      # Plural s or space / Points
	0xF1: '{ENM2}',      # Enemy with a/an
	0xF3: '{AMTP}',      # Amount + Point/Points
	0xF4: '{ENMY}',      # Enemy name
	0xF5: '{AMNT}',      # Numeric amount
	0xF6: '{SPEL}',      # Spell name
	0xF7: '{ITEM}',      # Item name
	0xF8: '{NAME}',      # Player name
	0xFB: '{WAIT}',      # Wait for button
	0xFC: '{END}',       # End of text
	0xFD: '\n',          # Newline
}


def parse_byte_line(line: str) -> Tuple[Optional[str], List[int]]:
	"""
	Parse a .byte directive line from assembly.

	Args:
		line: Assembly line containing .byte directive

	Returns:
		Tuple of (label, list of byte values)
	"""
	# Extract label if present
	label = None
	label_match = re.match(r'^(\w+):', line)
	if label_match:
		label = label_match.group(1)
		line = line[label_match.end():]

	# Find .byte directive
	byte_match = re.search(r'\.byte\s+(.*?)(?:;|$)', line, re.IGNORECASE)
	if not byte_match:
		return label, []

	byte_str = byte_match.group(1).strip()

	# Parse byte values
	bytes_list = []
	for part in byte_str.split(','):
		part = part.strip()
		if part.startswith('$'):
			try:
				bytes_list.append(int(part[1:], 16))
			except ValueError:
				continue
		elif part.startswith('0x'):
			try:
				bytes_list.append(int(part, 16))
			except ValueError:
				continue

	return label, bytes_list


def decode_bytes(byte_data: List[int], encoding: Dict[int, str]) -> str:
	"""
	Decode a list of bytes to text using the encoding table.

	Args:
		byte_data: List of byte values
		encoding: Character encoding dictionary

	Returns:
		Decoded text string
	"""
	result = []
	for byte_val in byte_data:
		if byte_val in CONTROL_CODES:
			result.append(CONTROL_CODES[byte_val])
		elif byte_val in encoding:
			result.append(encoding[byte_val])
		else:
			result.append(f'[${byte_val:02X}]')
	return ''.join(result)


def extract_dialogs_from_asm(
	asm_path: str,
	encoding: Dict[int, str]
) -> List[Dict[str, Any]]:
	"""
	Extract dialog entries from Bank02.asm.

	Args:
		asm_path: Path to Bank02.asm
		encoding: Character encoding dictionary

	Returns:
		List of dialog entry dictionaries
	"""
	dialogs = []
	current_block = None
	current_entry = None
	current_label = None
	entry_bytes = []
	comment_text = []

	with open(asm_path, 'r', encoding='utf-8') as f:
		lines = f.readlines()

	i = 0
	while i < len(lines):
		line = lines[i].rstrip()

		# Track text blocks
		block_match = re.match(r'^(TextBlock\d+):', line)
		if block_match:
			current_block = block_match.group(1)
			i += 1
			continue

		# Track text entries (TB1E0, TB2E3, etc.)
		entry_match = re.match(r'^(TB\d+E\d+):', line)
		if entry_match:
			# Save previous entry if exists
			if current_entry and entry_bytes:
				decoded = decode_bytes(entry_bytes, encoding)
				comment_full = ' '.join(comment_text) if comment_text else ''
				dialogs.append({
					'label': current_entry,
					'block': current_block,
					'bytes': entry_bytes.copy(),
					'bytes_hex': [f'${b:02X}' for b in entry_bytes],
					'text': decoded,
					'comment': comment_full,
				})

			current_entry = entry_match.group(1)
			entry_bytes = []
			comment_text = []
			i += 1
			continue

		# Parse comments for character reference
		if line.strip().startswith(';') and current_entry:
			# Extract character annotations from comments
			comment = line.strip()[1:].strip()
			if comment and not comment.startswith('-'):
				comment_text.append(comment)

		# Parse .byte directives
		if '.byte' in line.lower() and current_entry:
			label, bytes_data = parse_byte_line(line)
			if label and not current_entry:
				current_entry = label
			entry_bytes.extend(bytes_data)

			# Check if this line ends the entry (contains $FC)
			if 0xFC in bytes_data:
				decoded = decode_bytes(entry_bytes, encoding)
				comment_full = ' '.join(comment_text) if comment_text else ''
				dialogs.append({
					'label': current_entry,
					'block': current_block,
					'bytes': entry_bytes.copy(),
					'bytes_hex': [f'${b:02X}' for b in entry_bytes],
					'text': decoded,
					'comment': comment_full,
				})
				current_entry = None
				entry_bytes = []
				comment_text = []

		i += 1

	return dialogs


def format_for_json(dialogs: List[Dict[str, Any]]) -> Dict[str, Any]:
	"""
	Format dialog list for JSON output.

	Args:
		dialogs: List of dialog dictionaries

	Returns:
		Formatted dictionary for JSON output
	"""
	# Group by block
	blocks = {}
	for i, dialog in enumerate(dialogs):
		block = dialog.get('block', 'Unknown')
		if block not in blocks:
			blocks[block] = []
		blocks[block].append({
			'id': i,
			'label': dialog['label'],
			'text': dialog['text'],
			'text_cleaned': dialog['text'].replace('{END}', '').replace('{WAIT}', '').strip(),
			'bytes_hex': dialog['bytes_hex'],
		})

	return {
		'_comment': 'Dragon Warrior dialog text extracted from Bank02.asm',
		'_encoding': 'TBL-based encoding with control codes',
		'_control_codes': {
			'INDT': 'Indent following lines by 1 space',
			'PLRL': 'Plural s or space',
			'ENM2': 'Enemy name with a/an prefix',
			'AMTP': 'Amount followed by Point/Points',
			'ENMY': 'Enemy name',
			'AMNT': 'Numeric amount',
			'SPEL': 'Spell name',
			'ITEM': 'Item name',
			'NAME': 'Player name',
			'WAIT': 'Wait for button press',
			'END': 'End of text',
		},
		'dialog_count': len(dialogs),
		'block_count': len(blocks),
		'blocks': blocks,
		'dialogs': [
			{
				'id': i,
				'label': d['label'],
				'block': d.get('block', 'Unknown'),
				'text': d['text'],
				'text_cleaned': d['text'].replace('{END}', '').replace('{WAIT}', '').strip(),
				'bytes': d['bytes'],
			}
			for i, d in enumerate(dialogs)
		]
	}


def main():
	"""Main entry point."""
	import argparse

	parser = argparse.ArgumentParser(
		description='Extract dialog text from Dragon Warrior Bank02.asm'
	)
	parser.add_argument(
		'--asm', '-a',
		default='source_files/Bank02.asm',
		help='Path to Bank02.asm (default: source_files/Bank02.asm)'
	)
	parser.add_argument(
		'--tbl', '-t',
		default=None,
		help='Path to TBL encoding file (optional)'
	)
	parser.add_argument(
		'--output', '-o',
		default='assets/json/dialogs_extracted.json',
		help='Output JSON file path (default: assets/json/dialogs_extracted.json)'
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

	asm_path = project_root / args.asm
	output_path = project_root / args.output

	if not asm_path.exists():
		print(f"Error: ASM file not found: {asm_path}")
		return 1

	# Load encoding
	tbl_path = args.tbl
	if tbl_path:
		tbl_path = project_root / tbl_path if not Path(tbl_path).is_absolute() else tbl_path

	encoding = load_tbl_encoding(tbl_path)

	if args.verbose:
		print(f"Extracting dialogs from: {asm_path}")
		print(f"Character encoding entries: {len(encoding)}")

	# Extract dialogs
	dialogs = extract_dialogs_from_asm(str(asm_path), encoding)

	if args.verbose:
		print(f"Found {len(dialogs)} dialog entries")

	# Format and save
	output_data = format_for_json(dialogs)

	output_path.parent.mkdir(parents=True, exist_ok=True)
	with open(output_path, 'w', encoding='utf-8') as f:
		json.dump(output_data, f, indent='\t', ensure_ascii=False)

	print(f"Extracted {len(dialogs)} dialogs to: {output_path}")

	# Print sample
	if args.verbose and dialogs:
		print("\nSample dialogs:")
		for dialog in dialogs[:5]:
			text = dialog['text'].replace('{END}', '').replace('{WAIT}', '')
			print(f"  [{dialog['label']}]: {text[:60]}...")

	return 0


if __name__ == '__main__':
	exit(main())
