#!/usr/bin/env python3
"""
Dragon Warrior - Unified Asset Generator

Runs all JSON → ASM generators to create assembly include files from asset data.
This ensures all game data is regenerated from the JSON source files before building.

Usage:
	python generate_all_assets.py [--verbose] [--only TYPE]

Options:
	--verbose    Show detailed output
	--only TYPE  Only generate specific asset type (monsters, items, spells, etc.)
	--force      Regenerate even if ASM is newer than JSON

Asset Types:
	monsters     - Monster stat tables
	items        - Item data and costs
	spells       - Spell MP costs
	equipment    - Equipment bonuses
	shops        - Shop item lists
	npcs         - NPC positions and dialogs
	dialogs      - Dialog text tables
	damage       - Damage calculation parameters
	spell_fx     - Spell effect implementations
	experience   - Experience/level progression
"""

import sys
import subprocess
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
TOOLS_DIR = PROJECT_ROOT / 'tools'
ASSETS_JSON = PROJECT_ROOT / 'assets' / 'json'
GENERATED_DIR = PROJECT_ROOT / 'source_files' / 'generated'
BUILD_REINSERTION = PROJECT_ROOT / 'build' / 'reinsertion'


# Generator configuration
# Format: (json_file, generator_script, output_file, description)
GENERATORS: Dict[str, Tuple[str, str, str, str]] = {
	'monsters': (
		'monsters.json',
		'generate_monster_tables.py',
		'source_files/generated/MonsterTables.asm',
		'Monster stats (HP, attack, defense, XP, gold)'
	),
	'items': (
		'items.json',
		'generate_item_cost_table.py',
		'source_files/generated/ItemTable.asm',
		'Item costs and properties'
	),
	'spells': (
		'spells.json',
		'generate_spell_cost_table.py',
		'source_files/generated/SpellTable.asm',
		'Spell MP costs'
	),
	'equipment': (
		'equipment_bonuses.json',
		'generate_equipment_bonus_tables.py',
		'source_files/generated/EquipmentBonuses.asm',
		'Equipment attack/defense bonuses'
	),
	'shops': (
		'shops.json',
		'generate_shop_items_table.py',
		'source_files/generated/ShopTables.asm',
		'Shop inventories'
	),
	'npcs': (
		'npcs.json',
		'generate_npc_tables.py',
		'source_files/generated/NpcTables.asm',
		'NPC positions and behaviors'
	),
	'dialogs': (
		'dialogs.json',
		'generate_dialog_tables.py',
		'source_files/generated/DialogTables.asm',
		'Dialog text and pointers'
	),
	'damage': (
		'damage_formulas.json',
		'generate_damage_tables.py',
		'build/reinsertion/damage_tables.asm',
		'Damage calculation parameters'
	),
	'spell_fx': (
		'spell_effects.json',
		'generate_spell_effects.py',
		'build/reinsertion/spell_effects.asm',
		'Spell effect implementations'
	),
	'experience': (
		'experience_table.json',
		'generate_experience_table.py',
		'build/reinsertion/experience_table.asm',
		'Experience/level progression tables'
	),
	'music': (
		'music.json',
		'generate_music_tables.py',
		'build/reinsertion/music_tables.asm',
		'Music and sound effect tables'
	),
}


def check_needs_regeneration(json_path: Path, asm_path: Path, force: bool = False) -> bool:
	"""Check if ASM file needs to be regenerated from JSON."""
	if force:
		return True

	if not asm_path.exists():
		return True

	if not json_path.exists():
		return False

	# Regenerate if JSON is newer than ASM
	json_mtime = json_path.stat().st_mtime
	asm_mtime = asm_path.stat().st_mtime

	return json_mtime > asm_mtime


def run_generator(asset_type: str, config: Tuple[str, str, str, str],
				  verbose: bool = False, force: bool = False) -> Tuple[bool, str]:
	"""Run a single generator script."""
	json_file, script_name, output_path, description = config

	json_path = ASSETS_JSON / json_file
	generator_path = TOOLS_DIR / script_name
	asm_path = PROJECT_ROOT / output_path

	# Check if JSON exists
	if not json_path.exists():
		return False, f"JSON file not found: {json_file}"

	# Check if generator exists
	if not generator_path.exists():
		return False, f"Generator not found: {script_name}"

	# Check if regeneration needed
	if not check_needs_regeneration(json_path, asm_path, force):
		if verbose:
			return True, f"Skipped (up to date)"
		return True, "Up to date"

	# Ensure output directory exists
	asm_path.parent.mkdir(parents=True, exist_ok=True)

	# Run generator
	try:
		result = subprocess.run(
			['python', str(generator_path)],
			capture_output=True,
			text=True,
			cwd=str(PROJECT_ROOT)
		)

		if result.returncode == 0:
			return True, "Generated successfully"
		else:
			error = result.stderr[:200] if result.stderr else result.stdout[:200]
			return False, f"Generator failed: {error}"

	except Exception as e:
		return False, f"Error running generator: {e}"


def print_summary_table(results: Dict[str, Tuple[bool, str]]):
	"""Print a summary table of generator results."""
	print("\n" + "=" * 70)
	print("ASSET GENERATION SUMMARY")
	print("=" * 70)

	success_count = sum(1 for ok, _ in results.values() if ok)
	total_count = len(results)

	print(f"\n{'Asset Type':<15} {'Status':<12} {'Details':<40}")
	print("-" * 70)

	for asset_type, (success, message) in results.items():
		status = "✅ OK" if success else "❌ FAIL"
		desc = GENERATORS.get(asset_type, (None, None, None, ''))[3]
		print(f"{asset_type:<15} {status:<12} {message[:40]}")

	print("-" * 70)
	print(f"Total: {success_count}/{total_count} generators succeeded")
	print("=" * 70)


def main():
	"""Main entry point."""
	# Parse arguments
	verbose = '--verbose' in sys.argv or '-v' in sys.argv
	force = '--force' in sys.argv or '-f' in sys.argv

	# Check for --only filter
	only_type = None
	if '--only' in sys.argv:
		idx = sys.argv.index('--only')
		if idx + 1 < len(sys.argv):
			only_type = sys.argv[idx + 1]

	print("=" * 70)
	print("DRAGON WARRIOR - ASSET GENERATOR")
	print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
	print("=" * 70)

	# Validate only_type if specified
	if only_type and only_type not in GENERATORS:
		print(f"\nError: Unknown asset type '{only_type}'")
		print(f"Valid types: {', '.join(GENERATORS.keys())}")
		sys.exit(1)

	# Run generators
	results: Dict[str, Tuple[bool, str]] = {}

	generators_to_run = {only_type: GENERATORS[only_type]} if only_type else GENERATORS

	for asset_type, config in generators_to_run.items():
		json_file, script_name, output_path, description = config

		print(f"\n[{asset_type.upper()}] {description}")
		print(f"  JSON: {json_file}")
		print(f"  Generator: {script_name}")
		print(f"  Output: {output_path}")

		success, message = run_generator(asset_type, config, verbose, force)
		results[asset_type] = (success, message)

		status_icon = "✅" if success else "❌"
		print(f"  Status: {status_icon} {message}")

	# Print summary
	print_summary_table(results)

	# Return exit code based on results
	all_success = all(ok for ok, _ in results.values())
	sys.exit(0 if all_success else 1)


if __name__ == '__main__':
	main()
