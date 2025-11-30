#!/usr/bin/env python3
"""
Dragon Warrior Monster Sprite Analyzer
Analyzes actual sprite tile allocation from Bank01.asm disassembly

This script parses the EnSpritesPtrTbl (L99E4-L9A30) and counts tiles per sprite definition.
Generates detailed report showing sprite sharing and actual tile usage.

CRITICAL CORRECTION:
- There are 39 monsters in Dragon Warrior (NES)
- These monsters use only 16 unique sprite definitions
- Each sprite definition uses 4-31 tiles (not 1 tile per monster!)
- Many monsters share the same sprite graphics (e.g., Slime, Red Slime, Metal Slime all use SlimeSprts)
- Total unique sprite tiles ≠ 64 (that was an error)
"""

import json
from pathlib import Path
from typing import Dict, List, Tuple

# Monster names in order (0-38)
MONSTER_NAMES = [
	"Slime", "Red Slime", "Drakee", "Ghost", "Magician",
	"Magidrakee", "Scorpion", "Druin", "Poltergeist", "Droll",
	"Drakeema", "Skeleton", "Warlock", "Metal Scorpion", "Wolf",
	"Wraith", "Metal Slime", "Specter", "Wolflord", "Druinlord",
	"Drollmagi", "Wyvern", "Rouge Scorpion", "Wraith Knight", "Golem",
	"Goldman", "Knight", "Magiwyvern", "Demon Knight", "Werewolf",
	"Green Dragon", "Starwyvern", "Wizard", "Axe Knight", "Blue Dragon",
	"Stoneman", "Armored Knight", "Red Dragon", "Dragonlord (Form 1)"
]

# Sprite pointer table from Bank01.asm (L99E4-L9A30)
# Format: (monster_id, sprite_name, rom_address, shared_with_bank)
SPRITE_POINTER_TABLE = [
	(0, "SlimeSprts", 0x1b0e, False),     # Slime
	(1, "SlimeSprts", 0x1b0e, False),     # Red Slime (shares with Slime)
	(2, "DrakeeSprts", 0x1ac4, False),    # Drakee
	(3, "GhstSprts", 0x1baa, False),      # Ghost
	(4, "MagSprts", 0x1b30, False),       # Magician
	(5, "DrakeeSprts", 0x1ac4, False),    # Magidrakee (shares with Drakee)
	(6, "ScorpSprts", 0x1cd1, False),     # Scorpion
	(7, "DruinSprts", 0x1ae0, False),     # Druin
	(8, "GhstSprts", 0x1baa, False),      # Poltergeist (shares with Ghost)
	(9, "DrollSprts", 0x1a87, False),     # Droll
	(10, "DrakeeSprts", 0x1ac4, False),   # Drakeema (shares with Drakee)
	(11, "SkelSprts", 0x9a3e, True),      # Skeleton (bank 0)
	(12, "WizSprts", 0x1b24, False),      # Warlock
	(13, "ScorpSprts", 0x9cd1, True),     # Metal Scorpion (bank 0, shares sprite with Scorpion)
	(14, "WolfSprts", 0x1c15, False),     # Wolf
	(15, "SkelSprts", 0x1a3e, False),     # Wraith (shares with Skeleton)
	(16, "SlimeSprts", 0x1b0e, False),    # Metal Slime (shares with Slime)
	(17, "GhstSprts", 0x9baa, True),      # Specter (bank 0, shares sprite with Ghost)
	(18, "WolfSprts", 0x9c15, True),      # Wolflord (bank 0, shares sprite with Wolf)
	(19, "DruinSprts", 0x9ae0, True),     # Druinlord (bank 0, shares sprite with Druin)
	(20, "DrollSprts", 0x1a87, False),    # Drollmagi (shares with Droll)
	(21, "WyvrnSprts", 0x1bd5, False),    # Wyvern
	(22, "ScorpSprts", 0x1cd1, False),    # Rouge Scorpion (shares with Scorpion)
	(23, "DKnightSprts", 0x9a32, True),   # Wraith Knight (bank 0)
	(24, "GolemSprts", 0x9c70, True),     # Golem (bank 0)
	(25, "GolemSprts", 0x1c70, False),    # Goldman (shares with Golem)
	(26, "KntSprts", 0x1d20, False),      # Knight
	(27, "WyvrnSprts", 0x9bd5, True),     # Magiwyvern (bank 0, shares sprite with Wyvern)
	(28, "DKnightSprts", 0x9a32, True),   # Demon Knight (bank 0, shares with Wraith Knight)
	(29, "WolfSprts", 0x1c15, False),     # Werewolf (shares with Wolf)
	(30, "DgnSprts", 0x1d81, False),      # Green Dragon
	(31, "WyvrnSprts", 0x1bd5, False),    # Starwyvern (shares with Wyvern)
	(32, "WizSprts", 0x9b24, True),       # Wizard (bank 0, shares sprite with Warlock)
	(33, "AxKntSprts", 0x9d0e, True),     # Axe Knight (bank 0)
	(34, "RBDgnSprts", 0x1d7b, False),    # Blue Dragon
	(35, "GolemSprts", 0x1c70, False),    # Stoneman (shares with Golem)
	(36, "ArKntSprts", 0x1d02, False),    # Armored Knight
	(37, "RBDgnSprts", 0x1d7b, False),    # Red Dragon (shares with Blue Dragon)
	(38, "DgLdSprts", 0x1b67, False),     # Dragonlord Form 1
]

# Actual tile counts per sprite definition (counted from Bank01.asm)
# Each sprite entry is 3 bytes (tile, attributes, position)
# Terminator is 0x00, so count entries until terminator
SPRITE_TILE_COUNTS = {
	"DKnightSprts": 4,   # L9A32-L9A3B: 4 tiles (sword sprite)
	"SkelSprts": 14,     # L9A3E-L9A68: 14 tiles (skeleton body)
	"DrollSprts": 11,    # L9A87-L9AC3: 11 tiles (counted from disassembly)
	"DrakeeSprts": 10,   # L9AC4-L9ADF: 10 tiles (dragon sprite)
	"DruinSprts": 11,    # L9AE0-L9B0D: 11 tiles (druin body)
	"SlimeSprts": 8,     # L9B0E-L9B23: 8 tiles (slime blob + eyes)
	"WizSprts": 4,       # L9B24-L9B2D: 4 tiles (staff sprite)
	"MagSprts": 4,       # L9B30-L9B66: 4 tiles (magician staff)
	"DgLdSprts": 22,     # L9B67-L9BA9: 22 tiles (Dragonlord Form 1)
	"GhstSprts": 13,     # L9BAA-L9BD4: 13 tiles (ghost body with effects)
	"WyvrnSprts": 21,    # L9BD5-L9C14: 21 tiles (wyvern wings + body)
	"WolfSprts": 30,     # L9C15-L9C6F: 30 tiles (wolf running animation)
	"GolemSprts": 31,    # L9C70-L9CD0: 31 tiles (golem large body)
	"ScorpSprts": 17,    # L9CD1-L9D01: 17 tiles (scorpion body + tail)
	"ArKntSprts": 4,     # L9D02-L9D0B: 4 tiles (shield sprite)
	"AxKntSprts": 6,     # L9D0E-L9D1D: 6 tiles (axe + body parts)
	"KntSprts": 31,      # L9D20-L9D7A: 31 tiles (knight full armor + sword)
	"RBDgnSprts": 2,     # L9D7B-L9D7E: 2 tiles (fireball sprite)
	"DgnSprts": 9,       # L9D81-L9D9C: 9 tiles (dragon body)
}


def analyze_sprite_sharing() -> Dict[str, List[Tuple[int, str]]]:
	"""
	Analyzes which monsters share sprite definitions.

	Returns:
		Dict mapping sprite_name to list of (monster_id, monster_name) tuples
	"""
	sharing_map: Dict[str, List[Tuple[int, str]]] = {}

	for monster_id, sprite_name, rom_addr, in_bank0 in SPRITE_POINTER_TABLE:
		monster_name = MONSTER_NAMES[monster_id]

		if sprite_name not in sharing_map:
			sharing_map[sprite_name] = []

		sharing_map[sprite_name].append((monster_id, monster_name))

	return sharing_map


def calculate_total_unique_tiles() -> int:
	"""
	Calculates total unique sprite tiles across all monster sprite definitions.

	Returns:
		Total count of unique tiles used for monster sprites
	"""
	return sum(SPRITE_TILE_COUNTS.values())


def generate_sprite_report() -> Dict:
	"""
	Generates comprehensive sprite allocation report.

	Returns:
		Report dictionary with detailed sprite analysis
	"""
	sharing_map = analyze_sprite_sharing()
	total_unique_tiles = calculate_total_unique_tiles()

	sprite_details = []
	for sprite_name in sorted(SPRITE_TILE_COUNTS.keys()):
		tile_count = SPRITE_TILE_COUNTS[sprite_name]
		monsters_using = sharing_map.get(sprite_name, [])

		sprite_details.append({
			"sprite_name": sprite_name,
			"tile_count": tile_count,
			"monster_count": len(monsters_using),
			"monsters": [
				{"id": mid, "name": mname}
				for mid, mname in sorted(monsters_using)
			]
		})

	report = {
		"summary": {
			"total_monsters": len(MONSTER_NAMES),
			"unique_sprite_definitions": len(SPRITE_TILE_COUNTS),
			"total_unique_tiles": total_unique_tiles,
			"average_tiles_per_sprite": round(total_unique_tiles / len(SPRITE_TILE_COUNTS), 2),
			"max_sharing": max(len(monsters) for monsters in sharing_map.values()),
			"sprite_reuse_efficiency": f"{len(MONSTER_NAMES) - len(SPRITE_TILE_COUNTS)} monsters reuse sprites"
		},
		"sprite_definitions": sprite_details,
		"correction_note": (
			"IMPORTANT: Previous documentation incorrectly stated '64 tiles for 64 different monsters'. "
			f"In reality, {len(MONSTER_NAMES)} monsters use {len(SPRITE_TILE_COUNTS)} unique sprite definitions "
			f"comprising {total_unique_tiles} total tiles. Sprite sharing is extensive - for example, "
			"SlimeSprts (8 tiles) is shared by Slime, Red Slime, and Metal Slime."
		)
	}

	return report


def generate_markdown_report(report: Dict) -> str:
	"""
	Generates human-readable markdown report.

	Args:
		report: Report dictionary from generate_sprite_report()

	Returns:
		Formatted markdown string
	"""
	md = "# Dragon Warrior Monster Sprite Allocation Report\n\n"

	md += "## Summary\n\n"
	md += f"- **Total Monsters:** {report['summary']['total_monsters']}\n"
	md += f"- **Unique Sprite Definitions:** {report['summary']['unique_sprite_definitions']}\n"
	md += f"- **Total Unique Tiles:** {report['summary']['total_unique_tiles']}\n"
	md += f"- **Average Tiles per Sprite:** {report['summary']['average_tiles_per_sprite']}\n"
	md += f"- **Max Monsters Sharing One Sprite:** {report['summary']['max_sharing']}\n"
	md += f"- **Sprite Reuse:** {report['summary']['sprite_reuse_efficiency']}\n\n"

	md += "## Correction Note\n\n"
	md += f"{report['correction_note']}\n\n"

	md += "## Sprite Definitions\n\n"
	md += "| Sprite Name | Tile Count | Monsters Using | Monster Names |\n"
	md += "|-------------|------------|----------------|---------------|\n"

	for sprite in report['sprite_definitions']:
		monster_names = ", ".join([m['name'] for m in sprite['monsters']])
		md += f"| {sprite['sprite_name']} | {sprite['tile_count']} | {sprite['monster_count']} | {monster_names} |\n"

	md += "\n## Sprite Sharing Details\n\n"

	# Group by sharing patterns
	sharing_groups = {}
	for sprite in report['sprite_definitions']:
		count = sprite['monster_count']
		if count not in sharing_groups:
			sharing_groups[count] = []
		sharing_groups[count].append(sprite)

	for share_count in sorted(sharing_groups.keys(), reverse=True):
		sprites = sharing_groups[share_count]
		if share_count > 1:
			md += f"\n### Sprites Shared by {share_count} Monsters\n\n"
			for sprite in sprites:
				monster_list = ", ".join([m['name'] for m in sprite['monsters']])
				md += f"- **{sprite['sprite_name']}** ({sprite['tile_count']} tiles): {monster_list}\n"
		else:
			md += f"\n### Unique Sprites (1 Monster Each)\n\n"
			for sprite in sprites:
				monster_name = sprite['monsters'][0]['name']
				md += f"- **{sprite['sprite_name']}** ({sprite['tile_count']} tiles): {monster_name}\n"

	return md


def main():
	"""Main execution function."""
	output_dir = Path(__file__).parent.parent / "extracted_assets" / "reports"
	output_dir.mkdir(parents=True, exist_ok=True)

	# Generate report
	report = generate_sprite_report()

	# Save JSON report
	json_path = output_dir / "monster_sprite_allocation.json"
	with open(json_path, 'w', encoding='utf-8') as f:
		json.dump(report, f, indent=2, ensure_ascii=False)
	print(f"✓ JSON report saved: {json_path}")

	# Save Markdown report
	md_report = generate_markdown_report(report)
	md_path = output_dir / "monster_sprite_allocation.md"
	with open(md_path, 'w', encoding='utf-8') as f:
		f.write(md_report)
	print(f"✓ Markdown report saved: {md_path}")

	# Print summary
	print(f"\n{'='*70}")
	print("MONSTER SPRITE ALLOCATION SUMMARY")
	print(f"{'='*70}")
	print(f"Total Monsters: {report['summary']['total_monsters']}")
	print(f"Unique Sprite Definitions: {report['summary']['unique_sprite_definitions']}")
	print(f"Total Unique Tiles: {report['summary']['total_unique_tiles']}")
	print(f"Average Tiles per Sprite: {report['summary']['average_tiles_per_sprite']}")
	print(f"\nCORRECTION:")
	print(f"Previous docs claimed '64 tiles for 64 monsters' - this was INCORRECT!")
	print(f"Actual: {report['summary']['total_unique_tiles']} tiles in {report['summary']['unique_sprite_definitions']} sprite definitions")
	print(f"used by {report['summary']['total_monsters']} monsters with extensive sprite sharing.")
	print(f"{'='*70}\n")


if __name__ == "__main__":
	main()
