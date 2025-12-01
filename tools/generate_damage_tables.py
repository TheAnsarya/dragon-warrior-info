#!/usr/bin/env python3
"""
Generate damage calculation assembly code from JSON definitions.

This tool takes damage_formulas.json and generates assembly code that can be
included in the Dragon Warrior ROM build process.

Usage:
	python generate_damage_tables.py [--output build/reinsertion/damage_tables.asm]
"""

import json
import os
import sys
from pathlib import Path


def load_damage_formulas(json_path: str) -> dict:
	"""Load damage formula definitions from JSON file."""
	with open(json_path, 'r', encoding='utf-8') as f:
		return json.load(f)


def generate_constants(data: dict) -> str:
	"""Generate assembly constants from damage formula data."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; DAMAGE CALCULATION CONSTANTS")
	lines.append("; Generated from assets/json/damage_formulas.json")
	lines.append("; DO NOT EDIT DIRECTLY - Edit the JSON file and regenerate")
	lines.append("; =============================================================================")
	lines.append("")

	# Physical damage constants
	phys = data.get('physical_damage', {})

	lines.append("; Physical Damage Constants")
	player = phys.get('player_attack', {})
	lines.append(f"PLAYER_DEF_DIVISOR      = ${player.get('defense_divisor', 2):02X}  ; Defense divisor for damage calc")
	lines.append(f"PLAYER_DMG_DIVISOR      = ${player.get('result_divisor', 4):02X}  ; Final damage divisor")
	lines.append(f"PLAYER_WEAK_THRESHOLD   = ${player.get('weak_threshold', 2):02X}  ; Threshold for weak attack")

	weak = player.get('weak_attack', {})
	lines.append(f"PLAYER_WEAK_MASK        = ${weak.get('random_mask', 1):02X}  ; Random mask for weak attack (0-{weak.get('random_mask', 1)})")

	enemy = phys.get('enemy_attack', {})
	enemy_weak = enemy.get('weak_attack', {})
	lines.append(f"ENEMY_WEAK_ADDEND       = ${enemy_weak.get('addend', 2):02X}  ; Addend for enemy weak attack")
	lines.append(f"ENEMY_WEAK_DIVISOR      = ${enemy_weak.get('divisor', 3):02X}  ; Divisor for enemy weak attack")
	lines.append("")

	# Dodge mechanics
	dodge = data.get('dodge_mechanics', {}).get('enemy_dodge', {})
	lines.append("; Dodge Constants")
	lines.append(f"ENEMY_DODGE_THRESHOLD   = ${dodge.get('threshold', 14):02X}  ; {dodge.get('threshold', 14)}/64 = {dodge.get('percentage', 21.875)}%")
	lines.append("")

	# Spell damage constants - player spells
	spell_dmg = data.get('spell_damage', {})
	player_spells = spell_dmg.get('player_spells', {})

	lines.append("; Player Spell Damage Constants")
	for spell_name, spell_data in player_spells.items():
		base = spell_data.get('base_damage', 0)
		mask = spell_data.get('variance_mask', 0)
		lines.append(f"PLR_{spell_name}_BASE      = ${base:02X}  ; {spell_data.get('min_damage', base)}-{spell_data.get('max_damage', base+mask)} damage")
		lines.append(f"PLR_{spell_name}_MASK      = ${mask:02X}  ; Variance mask")
	lines.append("")

	# Enemy spell damage constants
	enemy_spells = spell_dmg.get('enemy_spells', {})
	lines.append("; Enemy Spell Damage Constants")
	for spell_name, spell_data in enemy_spells.items():
		base = spell_data.get('base_damage', 0)
		mask = spell_data.get('variance_mask', 0)
		lines.append(f"EN_{spell_name}_BASE       = ${base:02X}  ; {spell_data.get('min_damage', base)}-{spell_data.get('max_damage', base+mask)} damage")
		lines.append(f"EN_{spell_name}_MASK       = ${mask:02X}  ; Variance mask")
	lines.append("")

	# Armor reduction
	armor = spell_dmg.get('armor_reduction', {})
	lines.append("; Armor Spell Reduction Constants")
	for armor_name, armor_data in armor.items():
		mult = armor_data.get('multiplier', 2)
		div = armor_data.get('divisor', 3)
		lines.append(f"; {armor_name}: {mult}/{div} damage")
	lines.append("ARMOR_SPELL_MULT        = $02  ; Multiply by 2")
	lines.append("ARMOR_SPELL_DIV         = $03  ; Divide by 3 (results in 2/3 damage)")
	lines.append("")

	# Healing constants
	healing = data.get('healing_spells', {})
	lines.append("; Healing Spell Constants")
	for spell_name, spell_data in healing.items():
		base = spell_data.get('base_value', 0)
		mask = spell_data.get('variance_mask', 0)
		lines.append(f"{spell_name}_BASE          = ${base:02X}  ; {spell_data.get('min_heal', base)}-{spell_data.get('max_heal', base+mask)} HP")
		lines.append(f"{spell_name}_MASK          = ${mask:02X}  ; Variance mask")
	lines.append("")

	# Environmental damage
	env = data.get('environmental_damage', {})
	lines.append("; Environmental Damage Constants")
	for env_name, env_data in env.items():
		dmg = env_data.get('damage', 0)
		lines.append(f"{env_name.upper()}_DAMAGE         = ${dmg:02X}  ; {env_data.get('description', '')}")
	lines.append("")

	return '\n'.join(lines)


def generate_macros(data: dict) -> str:
	"""Generate assembly macros for damage calculations."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; DAMAGE CALCULATION MACROS")
	lines.append("; =============================================================================")
	lines.append("")

	lines.append("; Macro: Calculate player spell damage with variance")
	lines.append("; Input: base damage in A, mask in Y")
	lines.append("; Output: final damage in A")
	lines.append(".macro CALC_SPELL_DAMAGE base, mask")
	lines.append("	JSR UpdateRandNum")
	lines.append("	LDA RandomNumberUB")
	lines.append("	AND #mask")
	lines.append("	CLC")
	lines.append("	ADC #base")
	lines.append(".endmacro")
	lines.append("")

	lines.append("; Macro: Check magic resistance")
	lines.append("; Input: resistance stat in A")
	lines.append("; Output: carry set if spell fails")
	lines.append(".macro CHECK_MAGIC_RESIST")
	lines.append("	LSR")
	lines.append("	LSR")
	lines.append("	LSR")
	lines.append("	LSR")
	lines.append("	JSR ChkSpellFail")
	lines.append(".endmacro")
	lines.append("")

	return '\n'.join(lines)


def generate_full_assembly(data: dict) -> str:
	"""Generate complete assembly file with constants and macros."""
	header = [
		"; =============================================================================",
		"; DRAGON WARRIOR - DAMAGE CALCULATION TABLES",
		"; =============================================================================",
		"; Auto-generated from assets/json/damage_formulas.json",
		"; Generator: tools/generate_damage_tables.py",
		"; ",
		"; To modify damage values, edit the JSON file and run:",
		";   python tools/generate_damage_tables.py",
		"; =============================================================================",
		"",
	]

	constants = generate_constants(data)
	macros = generate_macros(data)

	return '\n'.join(header) + '\n' + constants + '\n' + macros


def main():
	"""Main entry point."""
	# Determine paths
	script_dir = Path(__file__).parent
	project_root = script_dir.parent

	json_path = project_root / 'assets' / 'json' / 'damage_formulas.json'
	output_path = project_root / 'build' / 'reinsertion' / 'damage_tables.asm'

	# Allow command line override
	if len(sys.argv) > 2 and sys.argv[1] == '--output':
		output_path = Path(sys.argv[2])

	# Load data
	if not json_path.exists():
		print(f"Error: JSON file not found: {json_path}")
		sys.exit(1)

	print(f"Loading damage formulas from: {json_path}")
	data = load_damage_formulas(str(json_path))

	# Generate assembly
	assembly = generate_full_assembly(data)

	# Ensure output directory exists
	output_path.parent.mkdir(parents=True, exist_ok=True)

	# Write output
	with open(output_path, 'w', encoding='utf-8') as f:
		f.write(assembly)

	print(f"Generated assembly file: {output_path}")
	print(f"  - Physical damage constants")
	print(f"  - Spell damage constants")
	print(f"  - Healing constants")
	print(f"  - Environmental damage constants")
	print(f"  - Calculation macros")


if __name__ == '__main__':
	main()
