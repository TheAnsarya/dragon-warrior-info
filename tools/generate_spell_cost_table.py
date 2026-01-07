#!/usr/bin/env python3
"""
Generate Dragon Warrior Spell Cost Table for Bank00.asm
This generates the SpellCostTbl in the exact format needed by Bank00.asm
"""
import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import json
from pathlib import Path
from typing import Dict

# Spell order in Bank00 SpellCostTbl
# Based on Bank00.asm at $9d53
SPELL_ORDER = [
	("HEAL", 4),
	("HURT", 2),
	("SLEEP", 2),
	("RADIANT", 3),
	("STOPSPELL", 2),
	("OUTSIDE", 6),
	("RETURN", 8),
	("REPEL", 2),
	("HEALMORE", 10),
	("HURTMORE", 5),
]

# Labels at specific offsets (some have named labels, most don't)
LABELED_OFFSETS = {
	0: "SpellCostTbl_Byte_9D53",
	3: "SpellCostTbl_Byte_9D56",
	6: "SpellCostTbl_Byte_9D59",
	9: "SpellCostTbl_Byte_9D5C",
}


def generate_spell_cost_table(spells_json_path: Path) -> str:
	"""Generate Bank00-style spell cost table ASM code"""

	# Load spells from JSON
	with open(spells_json_path, 'r') as f:
		spells = json.load(f)

	# Create name->spell lookup (case-insensitive)
	spells_by_name = {}
	for spell_id, spell in spells.items():
		spells_by_name[spell['name'].upper()] = spell

	asm_lines = [
		"; Spell Cost Table - Generated from assets/json/spells.json",
		"; To modify spell MP costs, edit the JSON file and rebuild",
		"",
		"SpellCostTbl:"
	]

	base_offset = 0x9d53  # Starting address

	for idx, (spell_name, default_mp) in enumerate(SPELL_ORDER):
		# Get spell from JSON or use default
		if spell_name in spells_by_name:
			spell = spells_by_name[spell_name]
			mp_cost = spell.get('mp_cost', default_mp)
		else:
			mp_cost = default_mp

		# Build the line
		comment = f";{spell_name:10s} {mp_cost}MP."

		if idx in LABELED_OFFSETS:
			label = LABELED_OFFSETS[idx]
			line = f"{label}:  .byte ${mp_cost:02X}               {comment}"
		else:
			addr_comment = f";(${base_offset + idx:04X})"
			line = f"        .byte ${mp_cost:02X}               {addr_comment}{spell_name:10s} {mp_cost}MP."

		asm_lines.append(line)

	return "\n".join(asm_lines)


def main():
	"""Generate spell cost table"""
	spells_json = Path("assets/json/spells.json")

	if not spells_json.exists():
		print("❌ No spells JSON file found!")
		return 1

	print(f"Generating spell cost table from {spells_json.name}...")

	output_dir = Path("source_files/generated")
	output_dir.mkdir(parents=True, exist_ok=True)

	output_file = output_dir / "spell_cost_table.asm"

	asm_code = generate_spell_cost_table(spells_json)

	with open(output_file, 'w') as f:
		f.write(asm_code)
		f.write("\n")

	print(f"✓ Generated {output_file}")
	return 0


if __name__ == "__main__":
	exit(main())
