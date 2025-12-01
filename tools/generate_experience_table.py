#!/usr/bin/env python3
"""
Generate experience and level progression tables from JSON definitions.

This tool takes experience_table.json and generates assembly code for
level requirements and stat progression in Dragon Warrior.

Usage:
	python generate_experience_table.py [--output build/reinsertion/experience_table.asm]
"""

import json
import os
import sys
from pathlib import Path


def load_experience_table(json_path: str) -> dict:
	"""Load experience table definitions from JSON file."""
	with open(json_path, 'r', encoding='utf-8') as f:
		return json.load(f)


def generate_experience_table(data: dict) -> str:
	"""Generate assembly code for experience requirements table."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; EXPERIENCE REQUIREMENTS TABLE")
	lines.append("; Address: $F35B (Bank03)")
	lines.append("; Format: 2 bytes per level (low byte, high byte)")
	lines.append("; =============================================================================")
	lines.append("")
	lines.append("LevelUpTbl:")

	levels = data.get('levels', [])
	for level_data in levels:
		level = level_data.get('level', 1)
		exp = level_data.get('experience_required', 0)
		low_byte = exp & 0xFF
		high_byte = (exp >> 8) & 0xFF
		lines.append(f"	.byte ${low_byte:02X}, ${high_byte:02X}    ; Level {level:2d}: {exp:5d} exp")

	lines.append("")
	return '\n'.join(lines)


def generate_stat_table(data: dict) -> str:
	"""Generate assembly code for base stats table."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; BASE STATS TABLE")
	lines.append("; Address: $A0CD (Bank01)")
	lines.append("; Format: 6 bytes per level (STR, AGI, MaxHP, MaxMP, SpellMask_L, SpellMask_H)")
	lines.append("; =============================================================================")
	lines.append("")
	lines.append("BaseStatsTbl:")

	levels = data.get('levels', [])
	for level_data in levels:
		level = level_data.get('level', 1)
		stats = level_data.get('stats', {})
		spells = level_data.get('spells', {})

		strength = stats.get('strength', 4)
		agility = stats.get('agility', 4)
		max_hp = stats.get('max_hp', 15)
		max_mp = stats.get('max_mp', 0)

		# Calculate spell mask
		spell_mask = spells.get('spell_mask', 0)
		mask_low = spell_mask & 0xFF
		mask_high = (spell_mask >> 8) & 0xFF

		lines.append(f"	; Level {level:2d}")
		lines.append(f"	.byte ${strength:02X}       ; STR = {strength}")
		lines.append(f"	.byte ${agility:02X}       ; AGI = {agility}")
		lines.append(f"	.byte ${max_hp:02X}       ; MaxHP = {max_hp}")
		lines.append(f"	.byte ${max_mp:02X}       ; MaxMP = {max_mp}")
		lines.append(f"	.byte ${mask_low:02X}       ; SpellMask_L")
		lines.append(f"	.byte ${mask_high:02X}       ; SpellMask_H")

	lines.append("")
	return '\n'.join(lines)


def generate_spell_learning_reference(data: dict) -> str:
	"""Generate a reference table showing spell learning."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; SPELL LEARNING REFERENCE")
	lines.append("; Shows which spells are learned at each level")
	lines.append("; =============================================================================")
	lines.append("")

	# Spell bit definitions
	spell_bits = {
		0: 'HEAL',
		1: 'HURT',
		2: 'SLEEP',
		3: 'RADIANT',
		4: 'STOPSPELL',
		5: 'OUTSIDE',
		6: 'RETURN',
		7: 'REPEL',
		8: 'HEALMORE',
		9: 'HURTMORE'
	}

	lines.append("; Spell Bit Definitions:")
	for bit, spell in spell_bits.items():
		lines.append(f";   Bit {bit}: {spell}")
	lines.append("")

	levels = data.get('levels', [])
	prev_spells = []

	lines.append("; Spell Progression:")
	for level_data in levels:
		level = level_data.get('level', 1)
		known = level_data.get('spells', {}).get('known', [])

		# Find newly learned spells
		new_spells = [s for s in known if s not in prev_spells]

		if new_spells:
			lines.append(f";   Level {level:2d}: Learn {', '.join(new_spells)}")

		prev_spells = known.copy()

	lines.append("")
	return '\n'.join(lines)


def generate_constants(data: dict) -> str:
	"""Generate level-related constants."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; LEVEL PROGRESSION CONSTANTS")
	lines.append("; =============================================================================")
	lines.append("")

	levels = data.get('levels', [])
	max_level = len(levels)
	max_exp = levels[-1].get('experience_required', 65535) if levels else 65535

	lines.append(f"MAX_LEVEL           = ${max_level:02X}    ; Maximum player level")
	lines.append(f"MAX_EXP_LOW         = ${max_exp & 0xFF:02X}    ; Max exp low byte")
	lines.append(f"MAX_EXP_HIGH        = ${(max_exp >> 8) & 0xFF:02X}    ; Max exp high byte")
	lines.append(f"BYTES_PER_STAT_ROW  = $06    ; 6 bytes per level in stat table")
	lines.append(f"BYTES_PER_EXP_ROW   = $02    ; 2 bytes per level in exp table")
	lines.append("")

	# Key milestones
	lines.append("; Level Milestones")
	milestones = [3, 7, 10, 13, 17, 19, 20, 30]
	for m in milestones:
		if m <= len(levels):
			level_data = levels[m - 1]
			exp = level_data.get('experience_required', 0)
			spells = level_data.get('spells', {}).get('known', [])
			spell_str = ', '.join(spells[:3]) if spells else 'None'
			lines.append(f"; Level {m:2d}: {exp:5d} exp - Spells: {spell_str}")
	lines.append("")

	return '\n'.join(lines)


def generate_full_assembly(data: dict) -> str:
	"""Generate complete assembly file."""
	header = [
		"; =============================================================================",
		"; DRAGON WARRIOR - EXPERIENCE AND LEVEL PROGRESSION TABLES",
		"; =============================================================================",
		"; Auto-generated from assets/json/experience_table.json",
		"; Generator: tools/generate_experience_table.py",
		"; ",
		"; To modify level progression, edit the JSON file and run:",
		";   python tools/generate_experience_table.py",
		"; =============================================================================",
		"",
	]

	sections = [
		'\n'.join(header),
		generate_constants(data),
		generate_spell_learning_reference(data),
		generate_experience_table(data),
		generate_stat_table(data),
	]

	return '\n'.join(sections)


def main():
	"""Main entry point."""
	script_dir = Path(__file__).parent
	project_root = script_dir.parent

	json_path = project_root / 'assets' / 'json' / 'experience_table.json'
	output_path = project_root / 'build' / 'reinsertion' / 'experience_table.asm'

	# Allow command line override
	if len(sys.argv) > 2 and sys.argv[1] == '--output':
		output_path = Path(sys.argv[2])

	# Load data
	if not json_path.exists():
		print(f"Error: JSON file not found: {json_path}")
		sys.exit(1)

	print(f"Loading experience table from: {json_path}")
	data = load_experience_table(str(json_path))

	# Generate assembly
	assembly = generate_full_assembly(data)

	# Ensure output directory exists
	output_path.parent.mkdir(parents=True, exist_ok=True)

	# Write output
	with open(output_path, 'w', encoding='utf-8') as f:
		f.write(assembly)

	print(f"Generated assembly file: {output_path}")
	print(f"  - Level progression constants")
	print(f"  - Spell learning reference")
	print(f"  - Experience requirements table (30 levels)")
	print(f"  - Base stats table (STR, AGI, HP, MP, spells)")


if __name__ == '__main__':
	main()
