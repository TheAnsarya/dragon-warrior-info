#!/usr/bin/env python3
"""
Generate Equipment Bonus Tables for Dragon Warrior

Reads equipment bonus data from JSON and generates the WeaponsBonusTbl,
ArmorBonusTbl, and ShieldBonusTbl assembly code for inclusion in Bank00.asm.
"""

import json
from pathlib import Path

# Paths
JSON_PATH = Path(__file__).parent.parent / "assets" / "json" / "equipment_bonuses.json"
OUTPUT_PATH = Path(__file__).parent.parent / "source_files" / "generated" / "equipment_bonus_tables.asm"


def generate_equipment_bonus_tables():
	"""Generate equipment bonus table assembly from JSON."""
	print(f"Reading: {JSON_PATH}")

	with open(JSON_PATH, "r") as f:
		data = json.load(f)

	lines = [
		";----------------------------------------------------------------------------------------------------",
		"; Equipment Bonus Tables - Generated from assets/json/equipment_bonuses.json",
		"; To modify equipment stats, edit the JSON file and rebuild",
		";----------------------------------------------------------------------------------------------------",
		"",
		";This table contains weapon bonuses added to the",
		";strength score to produce the attack power stat.",
		"",
		"WeaponsBonusTbl:",
	]

	# Generate weapons table
	weapons = data["weapons"]
	for idx in range(len(weapons)):
		item = weapons[str(idx)]
		bonus = item["bonus"]
		name = item["name"]
		lines.append(f"        .byte ${bonus:02X}               ;{name:16s} +{bonus}.")

	lines.extend([
		"",
		";This table contains armor bonuses added to the",
		";agility score to produce the defense power stat.",
		"",
		"ArmorBonusTbl:",
	])

	# Generate armor table
	armor = data["armor"]
	for idx in range(len(armor)):
		item = armor[str(idx)]
		bonus = item["bonus"]
		name = item["name"]
		lines.append(f"        .byte ${bonus:02X}               ;{name:16s} +{bonus}.")

	lines.extend([
		"",
		";This table contains shield bonuses added to the",
		";agility score to produce the defense power stat.",
		"",
		"ShieldBonusTbl:",
	])

	# Generate shields table
	shields = data["shields"]
	for idx in range(len(shields)):
		item = shields[str(idx)]
		bonus = item["bonus"]
		name = item["name"]
		lines.append(f"        .byte ${bonus:02X}               ;{name:16s} +{bonus}.")

	lines.append("")

	# Write output
	print(f"Writing: {OUTPUT_PATH}")
	OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

	with open(OUTPUT_PATH, "w", newline="\n") as f:
		f.write("\n".join(lines))

	print("Done!")


if __name__ == "__main__":
	generate_equipment_bonus_tables()
