#!/usr/bin/env python3
"""
Generate Monster Data Tables from JSON

Reads monsters_verified.json and generates monster_data.asm for
integration into the Dragon Warrior build pipeline.

Usage:
	python tools/generate_monster_tables.py [--verbose]

Output:
	source_files/generated/monster_data.asm
"""

import json
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_JSON = PROJECT_ROOT / "assets" / "json"
GENERATED = PROJECT_ROOT / "source_files" / "generated"


def load_monsters(json_path: Path) -> List[Dict[str, Any]]:
	"""Load monster data from JSON file."""
	with open(json_path, 'r', encoding='utf-8') as f:
		data = json.load(f)

	# Handle both list and dict formats
	if isinstance(data, list):
		return data
	elif isinstance(data, dict):
		# Could be keyed by ID
		monsters = []
		for key in sorted(data.keys(), key=lambda k: int(k) if k.isdigit() else 0):
			monster = data[key]
			if isinstance(monster, dict):
				monsters.append(monster)
		return monsters
	return []


def generate_monster_asm(monsters: List[Dict], output_path: Path, verbose: bool = False) -> int:
	"""Generate monster data assembly file."""
	lines = []

	# Header
	lines.append(';' + '=' * 100)
	lines.append('; Dragon Warrior Monster Data Tables')
	lines.append('; Generated from assets/json/monsters_verified.json')
	lines.append('; This file is auto-generated - do not edit directly')
	lines.append(';' + '=' * 100)
	lines.append('')
	lines.append('; Monster count: ' + str(len(monsters)))
	lines.append('')

	# Monster stats table
	lines.append(';' + '-' * 100)
	lines.append('; Monster Statistics Table')
	lines.append('; Format: HP (2), STR, AGI, MaxDmg, Dodge, SleepRes, HurtRes, XP (2), Gold (2)')
	lines.append(';' + '-' * 100)
	lines.append('')
	lines.append('MonsterStatsTable:')

	total_bytes = 0
	for monster in monsters:
		monster_id = monster.get('id', 0)
		name = monster.get('name', f'Monster_{monster_id}')
		hp = monster.get('hp', 0)
		strength = monster.get('strength', 0)
		agility = monster.get('agility', 0)
		max_damage = monster.get('max_damage', 0)
		dodge = monster.get('dodge_rate', 0)
		sleep_res = monster.get('sleep_resistance', 0)
		hurt_res = monster.get('hurt_resistance', 0)
		xp = monster.get('experience', 0)
		gold = monster.get('gold', 0)

		lines.append(f'')
		lines.append(f'; Monster {monster_id:02d}: {name}')
		lines.append(f'Monster{monster_id:02d}_Stats:')

		# HP (2 bytes, little endian)
		lines.append(f'\t.byte ${hp & 0xFF:02X}, ${(hp >> 8) & 0xFF:02X}\t\t; HP: {hp}')

		# Stats (single bytes)
		lines.append(f'\t.byte ${strength & 0xFF:02X}\t\t\t; Strength: {strength}')
		lines.append(f'\t.byte ${agility & 0xFF:02X}\t\t\t; Agility: {agility}')
		lines.append(f'\t.byte ${max_damage & 0xFF:02X}\t\t\t; Max Damage: {max_damage}')
		lines.append(f'\t.byte ${dodge & 0xFF:02X}\t\t\t; Dodge Rate: {dodge}')
		lines.append(f'\t.byte ${sleep_res & 0xFF:02X}\t\t\t; Sleep Resistance: {sleep_res}')
		lines.append(f'\t.byte ${hurt_res & 0xFF:02X}\t\t\t; Hurt Resistance: {hurt_res}')

		# XP (2 bytes)
		lines.append(f'\t.byte ${xp & 0xFF:02X}, ${(xp >> 8) & 0xFF:02X}\t\t; Experience: {xp}')

		# Gold (2 bytes)
		lines.append(f'\t.byte ${gold & 0xFF:02X}, ${(gold >> 8) & 0xFF:02X}\t\t; Gold: {gold}')

		total_bytes += 11  # 2+1+1+1+1+1+1+2+2 = 11 bytes per monster

		if verbose:
			print(f"  {monster_id:02d}: {name} - HP:{hp} STR:{strength} AGI:{agility}")

	lines.append('')
	lines.append(';' + '-' * 100)
	lines.append('; Monster Names Table')
	lines.append(';' + '-' * 100)
	lines.append('')
	lines.append('MonsterNamesTable:')

	for monster in monsters:
		monster_id = monster.get('id', 0)
		name = monster.get('name', f'Monster_{monster_id}')

		# Convert name to byte encoding (simplified)
		lines.append(f'\t.word MonsterName{monster_id:02d}')

	lines.append('')

	# Individual name strings
	for monster in monsters:
		monster_id = monster.get('id', 0)
		name = monster.get('name', f'Monster_{monster_id}')

		lines.append(f'MonsterName{monster_id:02d}:')
		# Encode name using DW encoding
		encoded_bytes = encode_name(name)
		byte_str = ', '.join(f'${b:02X}' for b in encoded_bytes)
		lines.append(f'\t.byte {byte_str}, $FC\t; "{name}"')

	lines.append('')
	lines.append(';' + '=' * 100)
	lines.append(f'; End of Monster Data - {len(monsters)} monsters, ~{total_bytes} bytes stats')
	lines.append(';' + '=' * 100)

	# Write output
	output_path.parent.mkdir(parents=True, exist_ok=True)
	with open(output_path, 'w', encoding='utf-8') as f:
		f.write('\n'.join(lines))

	return len(monsters)


def encode_name(name: str) -> List[int]:
	"""Encode name string to Dragon Warrior byte format."""
	# DW character encoding
	CHAR_TO_BYTE = {
		' ': 0x5F,
		'0': 0x00, '1': 0x01, '2': 0x02, '3': 0x03, '4': 0x04,
		'5': 0x05, '6': 0x06, '7': 0x07, '8': 0x08, '9': 0x09,
		'a': 0x0A, 'b': 0x0B, 'c': 0x0C, 'd': 0x0D, 'e': 0x0E,
		'f': 0x0F, 'g': 0x10, 'h': 0x11, 'i': 0x12, 'j': 0x13,
		'k': 0x14, 'l': 0x15, 'm': 0x16, 'n': 0x17, 'o': 0x18,
		'p': 0x19, 'q': 0x1A, 'r': 0x1B, 's': 0x1C, 't': 0x1D,
		'u': 0x1E, 'v': 0x1F, 'w': 0x20, 'x': 0x21, 'y': 0x22,
		'z': 0x23,
		'A': 0x24, 'B': 0x25, 'C': 0x26, 'D': 0x27, 'E': 0x28,
		'F': 0x29, 'G': 0x2A, 'H': 0x2B, 'I': 0x2C, 'J': 0x2D,
		'K': 0x2E, 'L': 0x2F, 'M': 0x30, 'N': 0x31, 'O': 0x32,
		'P': 0x33, 'Q': 0x34, 'R': 0x35, 'S': 0x36, 'T': 0x37,
		'U': 0x38, 'V': 0x39, 'W': 0x3A, 'X': 0x3B, 'Y': 0x3C,
		'Z': 0x3D,
	}

	result = []
	for char in name:
		if char in CHAR_TO_BYTE:
			result.append(CHAR_TO_BYTE[char])
		else:
			result.append(0x5F)  # Space for unknown

	return result


def main():
	parser = argparse.ArgumentParser(description='Generate monster data tables from JSON')
	parser.add_argument('--verbose', '-v', action='store_true', help='Verbose output')
	parser.add_argument('--input', '-i', type=str, default=None, help='Input JSON file')
	parser.add_argument('--output', '-o', type=str, default=None, help='Output ASM file')

	args = parser.parse_args()

	# Paths
	input_path = Path(args.input) if args.input else ASSETS_JSON / 'monsters_verified.json'
	output_path = Path(args.output) if args.output else GENERATED / 'monster_data.asm'

	if not input_path.exists():
		print(f"ERROR: Input file not found: {input_path}")
		return 1

	print(f"Loading monsters from: {input_path}")
	monsters = load_monsters(input_path)

	if not monsters:
		print("ERROR: No monsters loaded")
		return 1

	print(f"Found {len(monsters)} monsters")

	count = generate_monster_asm(monsters, output_path, args.verbose)
	print(f"Generated monster data: {output_path}")
	print(f"  Monsters: {count}")

	return 0


if __name__ == '__main__':
	exit(main())
