#!/usr/bin/env python3
"""
Generate spell effect assembly code from JSON definitions.

This tool takes spell_effects.json and generates assembly code that implements
spell behaviors in Dragon Warrior.

Usage:
	python generate_spell_effects.py [--output build/reinsertion/spell_effects.asm]
"""

import json
import os
import sys
from pathlib import Path


def load_spell_effects(json_path: str) -> dict:
	"""Load spell effect definitions from JSON file."""
	with open(json_path, 'r', encoding='utf-8') as f:
		return json.load(f)


def generate_spell_constants(data: dict) -> str:
	"""Generate assembly constants for spell definitions."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; SPELL CONSTANTS")
	lines.append("; Generated from assets/json/spell_effects.json")
	lines.append("; =============================================================================")
	lines.append("")

	# MP costs
	lines.append("; MP Costs")
	for spell_id, spell in data.get('player_spells', {}).items():
		mp = spell.get('mp_cost', 0)
		lines.append(f"MP_{spell_id.upper():<12} = ${mp:02X}  ; {spell.get('name', spell_id)}")
	lines.append("")

	# Spell IDs (for jump tables)
	lines.append("; Spell IDs")
	spell_ids = {
		'HEAL': 0, 'HURT': 1, 'SLEEP': 2, 'RADIANT': 3, 'STOPSPELL': 4,
		'OUTSIDE': 5, 'RETURN': 6, 'REPEL': 7, 'HEALMORE': 8, 'HURTMORE': 9
	}
	for spell_name, spell_num in spell_ids.items():
		lines.append(f"SPELL_{spell_name:<10} = ${spell_num:02X}")
	lines.append("")

	return '\n'.join(lines)


def generate_damage_effects(data: dict) -> str:
	"""Generate assembly code for damage spells."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; DAMAGE SPELL IMPLEMENTATIONS")
	lines.append("; =============================================================================")
	lines.append("")

	player_spells = data.get('player_spells', {})

	# HURT spell
	if 'HURT' in player_spells:
		hurt = player_spells['HURT']
		effect = hurt.get('effect', {})
		damage = effect.get('damage', {})
		base = damage.get('base', 5)
		mask = damage.get('variance_mask', 7)

		lines.append("; DoHurt - Player casts HURT")
		lines.append("; Deals 5-12 damage (base + 0-7 random)")
		lines.append("; Can be resisted based on enemy magic resistance")
		lines.append("DoHurt:")
		lines.append(f"	LDA #{base}          ; Base damage = {base}")
		lines.append(f"	STA TempVal")
		lines.append(f"	LDA #{mask}          ; Variance mask = {mask}")
		lines.append(f"	STA TempVal2")
		lines.append(f"	JSR CalcSpellDamage")
		lines.append(f"	; Continue to apply damage...")
		lines.append(f"	RTS")
		lines.append("")

	# HURTMORE spell
	if 'HURTMORE' in player_spells:
		hurtmore = player_spells['HURTMORE']
		effect = hurtmore.get('effect', {})
		damage = effect.get('damage', {})
		base = damage.get('base', 58)
		mask = damage.get('variance_mask', 7)

		lines.append("; DoHurtmore - Player casts HURTMORE")
		lines.append("; Deals 58-65 damage (base + 0-7 random)")
		lines.append("DoHurtmore:")
		lines.append(f"	LDA #{base}          ; Base damage = {base}")
		lines.append(f"	STA TempVal")
		lines.append(f"	LDA #{mask}          ; Variance mask = {mask}")
		lines.append(f"	STA TempVal2")
		lines.append(f"	JSR CalcSpellDamage")
		lines.append(f"	RTS")
		lines.append("")

	return '\n'.join(lines)


def generate_healing_effects(data: dict) -> str:
	"""Generate assembly code for healing spells."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; HEALING SPELL IMPLEMENTATIONS")
	lines.append("; =============================================================================")
	lines.append("")

	player_spells = data.get('player_spells', {})

	# HEAL spell
	if 'HEAL' in player_spells:
		heal = player_spells['HEAL']
		effect = heal.get('effect', {})
		hp = effect.get('hp_restored', {})
		base = hp.get('base', 10)
		mask = hp.get('variance_mask', 7)

		lines.append("; DoHeal - Player casts HEAL")
		lines.append(f"; Restores {base}-{base+mask} HP")
		lines.append("DoHeal:")
		lines.append(f"	LDA #{base}          ; Base healing = {base}")
		lines.append(f"	STA TempVal")
		lines.append(f"	LDA #{mask}          ; Variance mask = {mask}")
		lines.append(f"	STA TempVal2")
		lines.append(f"	JSR CalcHealing")
		lines.append(f"	JSR DisplayHealMessage")
		lines.append(f"	RTS")
		lines.append("")

	# HEALMORE spell
	if 'HEALMORE' in player_spells:
		healmore = player_spells['HEALMORE']
		effect = healmore.get('effect', {})
		hp = effect.get('hp_restored', {})
		base = hp.get('base', 85)
		mask = hp.get('variance_mask', 15)

		lines.append("; DoHealmore - Player casts HEALMORE")
		lines.append(f"; Restores {base}-{base+mask} HP")
		lines.append("DoHealmore:")
		lines.append(f"	LDA #{base}          ; Base healing = {base}")
		lines.append(f"	STA TempVal")
		lines.append(f"	LDA #{mask}          ; Variance mask = {mask}")
		lines.append(f"	STA TempVal2")
		lines.append(f"	JSR CalcHealing")
		lines.append(f"	JSR DisplayHealMessage")
		lines.append(f"	RTS")
		lines.append("")

	return '\n'.join(lines)


def generate_status_effects(data: dict) -> str:
	"""Generate assembly code for status effect spells."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; STATUS EFFECT SPELL IMPLEMENTATIONS")
	lines.append("; =============================================================================")
	lines.append("")

	player_spells = data.get('player_spells', {})

	# SLEEP spell
	if 'SLEEP' in player_spells:
		sleep = player_spells['SLEEP']
		effect = sleep.get('effect', {})
		resist = sleep.get('resistance', {})

		lines.append("; DoSleep - Player casts SLEEP")
		lines.append("; Puts enemy to sleep, can be resisted")
		lines.append("DoSleep:")
		lines.append(f"	; Check enemy magic resistance")
		lines.append(f"	LDA EnemyMagicResist")
		lines.append(f"	JSR CheckSpellResist")
		lines.append(f"	BCS .resisted")
		lines.append(f"	; Apply sleep status")
		lines.append(f"	LDA #$01")
		lines.append(f"	STA EnemySleepFlag")
		lines.append(f"	JSR DisplaySleepMessage")
		lines.append(f"	RTS")
		lines.append(".resisted:")
		lines.append(f"	JSR DisplayResistMessage")
		lines.append(f"	RTS")
		lines.append("")

	# STOPSPELL spell
	if 'STOPSPELL' in player_spells:
		lines.append("; DoStopspell - Player casts STOPSPELL")
		lines.append("; Prevents enemy from casting spells")
		lines.append("DoStopspell:")
		lines.append(f"	; Check enemy magic resistance")
		lines.append(f"	LDA EnemyMagicResist")
		lines.append(f"	JSR CheckSpellResist")
		lines.append(f"	BCS .resisted")
		lines.append(f"	; Apply stopspell status")
		lines.append(f"	LDA #$01")
		lines.append(f"	STA EnemyStopspellFlag")
		lines.append(f"	JSR DisplayStopspellMessage")
		lines.append(f"	RTS")
		lines.append(".resisted:")
		lines.append(f"	JSR DisplayResistMessage")
		lines.append(f"	RTS")
		lines.append("")

	return '\n'.join(lines)


def generate_utility_effects(data: dict) -> str:
	"""Generate assembly code for utility spells."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; UTILITY SPELL IMPLEMENTATIONS")
	lines.append("; =============================================================================")
	lines.append("")

	player_spells = data.get('player_spells', {})

	# RADIANT spell
	if 'RADIANT' in player_spells:
		radiant = player_spells['RADIANT']
		effect = radiant.get('effect', {})
		radius = effect.get('light_radius', 3)

		lines.append("; DoRadiant - Player casts RADIANT")
		lines.append(f"; Creates light radius of {radius} tiles in dungeons")
		lines.append("DoRadiant:")
		lines.append(f"	LDA #{radius}         ; Light radius")
		lines.append(f"	STA RadiantRadius")
		lines.append(f"	LDA #$01")
		lines.append(f"	STA RadiantActive")
		lines.append(f"	JSR DisplayRadiantMessage")
		lines.append(f"	RTS")
		lines.append("")

	# OUTSIDE spell
	if 'OUTSIDE' in player_spells:
		lines.append("; DoOutside - Player casts OUTSIDE")
		lines.append("; Exits current dungeon/cave")
		lines.append("DoOutside:")
		lines.append(f"	; Check if in dungeon")
		lines.append(f"	LDA CurrentMapType")
		lines.append(f"	CMP #MAP_DUNGEON")
		lines.append(f"	BNE .fail")
		lines.append(f"	; Teleport to entrance")
		lines.append(f"	JSR WarpToEntrance")
		lines.append(f"	RTS")
		lines.append(".fail:")
		lines.append(f"	JSR DisplayFailMessage")
		lines.append(f"	RTS")
		lines.append("")

	# RETURN spell
	if 'RETURN' in player_spells:
		lines.append("; DoReturn - Player casts RETURN")
		lines.append("; Warps to last save point")
		lines.append("DoReturn:")
		lines.append(f"	; Check if in combat or dialogue")
		lines.append(f"	JSR CheckCanReturn")
		lines.append(f"	BCS .fail")
		lines.append(f"	; Warp to save point")
		lines.append(f"	JSR WarpToSavePoint")
		lines.append(f"	RTS")
		lines.append(".fail:")
		lines.append(f"	JSR DisplayFailMessage")
		lines.append(f"	RTS")
		lines.append("")

	# REPEL spell
	if 'REPEL' in player_spells:
		repel = player_spells['REPEL']
		effect = repel.get('effect', {})
		steps = effect.get('duration_steps', 127)

		lines.append("; DoRepel - Player casts REPEL")
		lines.append(f"; Prevents encounters for {steps} steps")
		lines.append("DoRepel:")
		lines.append(f"	LDA #{steps}         ; Duration in steps")
		lines.append(f"	STA RepelCounter")
		lines.append(f"	JSR DisplayRepelMessage")
		lines.append(f"	RTS")
		lines.append("")

	return '\n'.join(lines)


def generate_enemy_spells(data: dict) -> str:
	"""Generate assembly code for enemy spell variants."""
	lines = []
	lines.append("; =============================================================================")
	lines.append("; ENEMY SPELL IMPLEMENTATIONS")
	lines.append("; =============================================================================")
	lines.append("")

	enemy_spells = data.get('enemy_spells', {})

	# Enemy HURT
	if 'HURT' in enemy_spells:
		hurt = enemy_spells['HURT']
		effect = hurt.get('effect', {})
		damage = effect.get('damage', {})
		base = damage.get('base', 7)
		mask = damage.get('variance_mask', 3)

		lines.append("; EnemyHurt - Enemy casts HURT")
		lines.append(f"; Deals {base}-{base+mask} damage")
		lines.append("EnemyHurt:")
		lines.append(f"	LDA #{base}          ; Base damage = {base}")
		lines.append(f"	STA TempVal")
		lines.append(f"	LDA #{mask}          ; Variance mask = {mask}")
		lines.append(f"	STA TempVal2")
		lines.append(f"	JSR CalcEnemySpellDamage")
		lines.append(f"	JSR ApplyArmorReduction")
		lines.append(f"	RTS")
		lines.append("")

	# Enemy HURTMORE
	if 'HURTMORE' in enemy_spells:
		hurtmore = enemy_spells['HURTMORE']
		effect = hurtmore.get('effect', {})
		damage = effect.get('damage', {})
		base = damage.get('base', 30)
		mask = damage.get('variance_mask', 15)

		lines.append("; EnemyHurtmore - Enemy casts HURTMORE")
		lines.append(f"; Deals {base}-{base+mask} damage")
		lines.append("EnemyHurtmore:")
		lines.append(f"	LDA #{base}          ; Base damage = {base}")
		lines.append(f"	STA TempVal")
		lines.append(f"	LDA #{mask}          ; Variance mask = {mask}")
		lines.append(f"	STA TempVal2")
		lines.append(f"	JSR CalcEnemySpellDamage")
		lines.append(f"	JSR ApplyArmorReduction")
		lines.append(f"	RTS")
		lines.append("")

	# Enemy HEAL
	if 'HEAL' in enemy_spells:
		heal = enemy_spells['HEAL']
		effect = heal.get('effect', {})
		hp = effect.get('hp_restored', {})
		base = hp.get('base', 20)
		mask = hp.get('variance_mask', 7)

		lines.append("; EnemyHeal - Enemy heals itself")
		lines.append(f"; Restores {base}-{base+mask} HP")
		lines.append("EnemyHeal:")
		lines.append(f"	LDA #{base}          ; Base healing = {base}")
		lines.append(f"	STA TempVal")
		lines.append(f"	LDA #{mask}          ; Variance mask = {mask}")
		lines.append(f"	STA TempVal2")
		lines.append(f"	JSR CalcHealing")
		lines.append(f"	; Add to enemy HP")
		lines.append(f"	LDA EnemyHP")
		lines.append(f"	CLC")
		lines.append(f"	ADC TempVal")
		lines.append(f"	STA EnemyHP")
		lines.append(f"	RTS")
		lines.append("")

	return '\n'.join(lines)


def generate_full_assembly(data: dict) -> str:
	"""Generate complete assembly file."""
	header = [
		"; =============================================================================",
		"; DRAGON WARRIOR - SPELL EFFECT IMPLEMENTATIONS",
		"; =============================================================================",
		"; Auto-generated from assets/json/spell_effects.json",
		"; Generator: tools/generate_spell_effects.py",
		"; ",
		"; To modify spell behaviors, edit the JSON file and run:",
		";   python tools/generate_spell_effects.py",
		"; =============================================================================",
		"",
	]

	sections = [
		'\n'.join(header),
		generate_spell_constants(data),
		generate_damage_effects(data),
		generate_healing_effects(data),
		generate_status_effects(data),
		generate_utility_effects(data),
		generate_enemy_spells(data),
	]

	return '\n'.join(sections)


def main():
	"""Main entry point."""
	script_dir = Path(__file__).parent
	project_root = script_dir.parent

	json_path = project_root / 'assets' / 'json' / 'spell_effects.json'
	output_path = project_root / 'build' / 'reinsertion' / 'spell_effects.asm'

	# Allow command line override
	if len(sys.argv) > 2 and sys.argv[1] == '--output':
		output_path = Path(sys.argv[2])

	# Load data
	if not json_path.exists():
		print(f"Error: JSON file not found: {json_path}")
		sys.exit(1)

	print(f"Loading spell effects from: {json_path}")
	data = load_spell_effects(str(json_path))

	# Generate assembly
	assembly = generate_full_assembly(data)

	# Ensure output directory exists
	output_path.parent.mkdir(parents=True, exist_ok=True)

	# Write output
	with open(output_path, 'w', encoding='utf-8') as f:
		f.write(assembly)

	print(f"Generated assembly file: {output_path}")
	print(f"  - Spell constants (MP costs, spell IDs)")
	print(f"  - Damage spell implementations")
	print(f"  - Healing spell implementations")
	print(f"  - Status effect implementations")
	print(f"  - Utility spell implementations")
	print(f"  - Enemy spell implementations")


if __name__ == '__main__':
	main()
