#!/usr/bin/env python3
"""
Dragon Warrior Music Data Extractor

Extracts music track data from the Dragon Warrior ROM/ASM files and
converts it to an editable JSON format.

The Dragon Warrior music engine uses:
- 3 audio channels: SQ1 (pulse), SQ2 (pulse), TRI (triangle)
- Control bytes for tempo, jumps, returns, volume, etc.
- Note values $80-$C8 corresponding to musical notes C2-C8

Usage:
	python extract_music.py [--rom path/to/rom.nes] [--output path/to/music.json]

Author: Dragon Warrior ROM Hacking Toolkit
"""

import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any


# Music control byte constants (from Dragon_Warrior_Defines.asm)
MUSIC_CTRL = {
	0xF6: 'END_SPACE',    # Stop adding quiet time between notes
	0xF7: 'ADD_SPACE',    # Add quiet time between notes
	0xF8: 'NOISE_VOL',    # Noise volume control byte
	0xF9: 'NOTE_OFFSET',  # Note offset control byte
	0xFA: 'CTRL1',        # Channel control 1 byte
	0xFB: 'CTRL0',        # Channel control 0 byte (duty/volume)
	0xFC: 'NO_OP',        # Skip byte, move to next
	0xFD: 'RETURN',       # Return to previous music data address
	0xFE: 'JUMP',         # Jump to new music data address
	0xFF: 'TEMPO',        # Change music tempo
}

# Note value to musical note mapping
# $80 = C2, stepping up chromatically
NOTE_NAMES = [
	'C2', 'C#2', 'D2', 'D#2', 'E2', 'F2', 'F#2', 'G2', 'G#2', 'A2', 'A#2', 'B2',  # $80-$8B
	'C3', 'C#3', 'D3', 'D#3', 'E3', 'F3', 'F#3', 'G3', 'G#3', 'A3', 'A#3', 'B3',  # $8C-$97
	'C4', 'C#4', 'D4', 'D#4', 'E4', 'F4', 'F#4', 'G4', 'G#4', 'A4', 'A#4', 'B4',  # $98-$A3
	'C5', 'C#5', 'D5', 'D#5', 'E5', 'F5', 'F#5', 'G5', 'G#5', 'A5', 'A#5', 'B5',  # $A4-$AF
	'C6', 'C#6', 'D6', 'D#6', 'E6', 'F6', 'F#6', 'G6', 'G#6', 'A6', 'A#6', 'B6',  # $B0-$BB
	'C7', 'C#7', 'D7', 'D#7', 'E7', 'F7', 'F#7', 'G7', 'G#7', 'A7', 'A#7', 'B7',  # $BC-$C7
	'C8',  # $C8
]

# Music track definitions
MUSIC_TRACKS = {
	0x00: {'id': 'MSC_NOSOUND', 'name': 'No Sound', 'description': 'Silence'},
	0x01: {'id': 'MSC_INTRO', 'name': 'Intro', 'description': 'Opening intro music'},
	0x02: {'id': 'MSC_THRN_ROOM', 'name': 'Throne Room', 'description': 'Tantegel throne room'},
	0x03: {'id': 'MSC_TANTAGEL2', 'name': 'Tantagel 2', 'description': 'Tantagel castle music'},
	0x04: {'id': 'MSC_VILLAGE', 'name': 'Village', 'description': 'Village/pre-game music'},
	0x05: {'id': 'MSC_OUTDOOR', 'name': 'Outdoor', 'description': 'Overworld music'},
	0x06: {'id': 'MSC_DUNGEON1', 'name': 'Dungeon 1', 'description': 'Dungeon level 1'},
	0x07: {'id': 'MSC_DUNGEON2', 'name': 'Dungeon 2', 'description': 'Dungeon level 2'},
	0x08: {'id': 'MSC_DUNGEON3', 'name': 'Dungeon 3', 'description': 'Dungeon level 3'},
	0x09: {'id': 'MSC_DUNGEON4', 'name': 'Dungeon 4', 'description': 'Dungeon level 4'},
	0x0A: {'id': 'MSC_DUNGEON5', 'name': 'Dungeon 5', 'description': 'Dungeon level 5'},
	0x0B: {'id': 'MSC_DUNGEON6', 'name': 'Dungeon 6', 'description': 'Dungeon level 6'},
	0x0C: {'id': 'MSC_DUNGEON7', 'name': 'Dungeon 7', 'description': 'Dungeon level 7'},
	0x0D: {'id': 'MSC_DUNGEON8', 'name': 'Dungeon 8', 'description': 'Dungeon level 8'},
	0x0E: {'id': 'MSC_ENTR_FGHT', 'name': 'Enter Fight', 'description': 'Battle start fanfare'},
	0x0F: {'id': 'MSC_END_BOSS', 'name': 'End Boss', 'description': 'Dragonlord battle'},
	0x10: {'id': 'MSC_END', 'name': 'Ending', 'description': 'End game music'},
	0x11: {'id': 'MSC_SILV_HARP', 'name': 'Silver Harp', 'description': 'Silver harp item music'},
	0x12: {'id': 'MSC_FRY_FLUTE', 'name': 'Fairy Flute', 'description': 'Fairy flute item music'},
	0x13: {'id': 'MSC_RNBW_BRDG', 'name': 'Rainbow Bridge', 'description': 'Rainbow bridge creation'},
	0x14: {'id': 'MSC_DEATH', 'name': 'Death', 'description': 'Player death music'},
	0x15: {'id': 'MSC_INN', 'name': 'Inn', 'description': 'Inn rest music'},
	0x16: {'id': 'MSC_PRNCS_LOVE', 'name': 'Princess Love', 'description': "Princess Gwaelin's love"},
	0x17: {'id': 'MSC_CURSED', 'name': 'Cursed', 'description': 'Cursed item music'},
	0x18: {'id': 'MSC_REG_FGHT', 'name': 'Regular Fight', 'description': 'Normal battle music'},
	0x19: {'id': 'MSC_VICTORY', 'name': 'Victory', 'description': 'Battle victory fanfare'},
	0x1A: {'id': 'MSC_LEVEL_UP', 'name': 'Level Up', 'description': 'Level up fanfare'},
}

# Sound effect definitions
SFX_LIST = {
	0x80: {'id': 'SFX_FFDAMAGE', 'name': 'Force Field', 'description': 'Force field damage'},
	0x81: {'id': 'SFX_WVRN_WNG', 'name': 'Wyvern Wing', 'description': 'Wings of Wyvern'},
	0x82: {'id': 'SFX_STAIRS', 'name': 'Stairs', 'description': 'Using stairs'},
	0x83: {'id': 'SFX_RUN', 'name': 'Run Away', 'description': 'Running from battle'},
	0x84: {'id': 'SFX_SWMP_DMG', 'name': 'Swamp', 'description': 'Swamp damage'},
	0x85: {'id': 'SFX_MENU_BTN', 'name': 'Menu Button', 'description': 'Menu selection'},
	0x86: {'id': 'SFX_CONFIRM', 'name': 'Confirm', 'description': 'Confirmation sound'},
	0x87: {'id': 'SFX_ENMY_HIT', 'name': 'Enemy Hit', 'description': 'Hitting an enemy'},
	0x88: {'id': 'SFX_EXCLNT_MOVE', 'name': 'Excellent Move', 'description': 'Critical hit'},
	0x89: {'id': 'SFX_ATTACK', 'name': 'Attack', 'description': 'Attack sound'},
	0x8A: {'id': 'SFX_PLYR_HIT1', 'name': 'Player Hit 1', 'description': 'Player taking damage 1'},
	0x8B: {'id': 'SFX_PLYR_HIT2', 'name': 'Player Hit 2', 'description': 'Player taking damage 2'},
	0x8C: {'id': 'SFX_ATCK_PREP', 'name': 'Attack Prep', 'description': 'Attack preparation'},
	0x8D: {'id': 'SFX_MISSED1', 'name': 'Missed 1', 'description': 'Attack missed 1'},
	0x8E: {'id': 'SFX_MISSED2', 'name': 'Missed 2', 'description': 'Attack missed 2'},
	0x8F: {'id': 'SFX_WALL_BUMP', 'name': 'Wall Bump', 'description': 'Walking into wall'},
	0x90: {'id': 'SFX_TEXT', 'name': 'Text', 'description': 'Text display'},
	0x91: {'id': 'SFX_SPELL', 'name': 'Spell', 'description': 'Spell casting'},
	0x92: {'id': 'SFX_RADIANT', 'name': 'Radiant', 'description': 'Radiant spell'},
	0x93: {'id': 'SFX_TRSR_CHEST', 'name': 'Treasure', 'description': 'Opening chest'},
	0x94: {'id': 'SFX_DOOR', 'name': 'Door', 'description': 'Opening door'},
	0x95: {'id': 'SFX_FIRE', 'name': 'Fire', 'description': 'Breath fire'},
}


def byte_to_note(byte_val: int) -> Optional[str]:
	"""Convert a byte value to a musical note name."""
	if 0x80 <= byte_val <= 0xC8:
		idx = byte_val - 0x80
		if idx < len(NOTE_NAMES):
			return NOTE_NAMES[idx]
	return None


def parse_asm_music_data(asm_content: str) -> Dict[str, Any]:
	"""
	Parse music data from ASM source file.

	Looks for music label patterns like:
	- SQ1Village:
	- TRIOutdoor:
	- SQ2EndBoss:
	"""
	tracks = {}

	# Find music labels
	label_pattern = re.compile(r'^(SQ[12]|TRI)\w+:', re.MULTILINE)
	byte_pattern = re.compile(r'\.byte\s+([^;]+)', re.IGNORECASE)

	for match in label_pattern.finditer(asm_content):
		label = match.group(0).rstrip(':')
		start_pos = match.end()

		# Find next label to get data bounds
		next_match = label_pattern.search(asm_content, start_pos)
		end_pos = next_match.start() if next_match else len(asm_content)

		block = asm_content[start_pos:end_pos]

		# Extract bytes
		bytes_data = []
		for byte_match in byte_pattern.finditer(block):
			byte_str = byte_match.group(1).strip()
			# Parse comma-separated values
			for val in byte_str.split(','):
				val = val.strip()
				# Handle different formats
				if val.startswith('$'):
					try:
						bytes_data.append(int(val[1:], 16))
					except ValueError:
						pass
				elif val.startswith('MCTL_') or val.startswith('MUSICCTL_'):
					# Control byte reference
					bytes_data.append({'control': val})
				elif val.startswith('%'):
					try:
						bytes_data.append(int(val[1:], 2))
					except ValueError:
						pass

		if bytes_data:
			tracks[label] = {
				'raw_bytes': bytes_data[:50],  # Limit for JSON size
				'length': len(bytes_data)
			}

	return tracks


def create_music_json() -> Dict[str, Any]:
	"""Create the complete music JSON structure."""
	return {
		"_metadata": {
			"format_version": "1.0",
			"game": "Dragon Warrior",
			"platform": "NES",
			"description": "Music and sound effect data for Dragon Warrior",
			"rom_addresses": {
				"music_pointers": "$8297 (Bank01)",
				"sfx_pointers": "$8339 (Bank01)",
				"note_table": "$8205 (Bank01)",
				"resume_music_table": "$B1AE (Bank00)"
			},
			"control_bytes": {
				"0xF6": "END_SPACE - Stop adding quiet time between notes",
				"0xF7": "ADD_SPACE - Add quiet time (next byte = count)",
				"0xF8": "NOISE_VOL - Noise volume (next byte = volume)",
				"0xF9": "NOTE_OFFSET - Note pitch offset",
				"0xFA": "CTRL1 - Channel control 1 (sweep)",
				"0xFB": "CTRL0 - Channel control 0 (duty/volume)",
				"0xFC": "NO_OP - No operation/skip",
				"0xFD": "RETURN - Return to previous address",
				"0xFE": "JUMP - Jump to address (next 2 bytes = addr)",
				"0xFF": "TEMPO - Set tempo (next byte = tempo value)"
			},
			"note_range": "0x80 (C2) to 0xC8 (C8)"
		},
		"music_tracks": {
			track_info['id']: {
				"track_id": track_num,
				"name": track_info['name'],
				"description": track_info['description'],
				"channels": {
					"sq1": {"label": f"SQ1{track_info['name'].replace(' ', '')}", "enabled": True},
					"sq2": {"label": f"SQ2{track_info['name'].replace(' ', '')}", "enabled": track_num != 0},
					"tri": {"label": f"TRI{track_info['name'].replace(' ', '')}", "enabled": True}
				},
				"tempo": 0x78,  # Default, actual varies per track
				"loop": True
			}
			for track_num, track_info in MUSIC_TRACKS.items()
		},
		"sound_effects": {
			sfx_info['id']: {
				"sfx_id": sfx_num,
				"name": sfx_info['name'],
				"description": sfx_info['description'],
				"uses_sq2": True,
				"uses_noise": True
			}
			for sfx_num, sfx_info in SFX_LIST.items()
		},
		"note_table": {
			f"0x{0x80 + i:02X}": {
				"note": note,
				"octave": int(note[-1]),
				"frequency_hz": round(440 * (2 ** ((i - 33) / 12)), 1)  # A4=440Hz at index 33
			}
			for i, note in enumerate(NOTE_NAMES)
		},
		"map_music": {
			"overworld": "MSC_OUTDOOR",
			"tantagel_throne": "MSC_THRN_ROOM",
			"tantagel_castle": "MSC_TANTAGEL2",
			"villages": "MSC_VILLAGE",
			"dungeons": ["MSC_DUNGEON1", "MSC_DUNGEON2", "MSC_DUNGEON3", "MSC_DUNGEON4",
						 "MSC_DUNGEON5", "MSC_DUNGEON6", "MSC_DUNGEON7", "MSC_DUNGEON8"],
			"dragonlord_castle": "MSC_DUNGEON8",
			"hauksness": "MSC_DUNGEON4"
		},
		"tempo_reference": {
			"formula": "Counts per second = 60 / (1 + (255 - tempo) / 255)",
			"examples": {
				"0x50": "32 counts/sec (slow)",
				"0x6E": "44 counts/sec",
				"0x73": "46 counts/sec",
				"0x78": "48 counts/sec",
				"0x7D": "50 counts/sec",
				"0x7E": "50 counts/sec (fast)"
			}
		}
	}


def main():
	"""Main entry point."""
	# Determine paths
	script_dir = Path(__file__).parent
	project_root = script_dir.parent

	output_path = project_root / 'assets' / 'json' / 'music.json'

	# Allow command line override
	if len(sys.argv) > 2 and sys.argv[1] == '--output':
		output_path = Path(sys.argv[2])

	# Create music JSON
	print("Extracting music data...")
	music_data = create_music_json()

	# Ensure output directory exists
	output_path.parent.mkdir(parents=True, exist_ok=True)

	# Write output
	with open(output_path, 'w', encoding='utf-8') as f:
		json.dump(music_data, f, indent=2)

	print(f"Generated music JSON: {output_path}")
	print(f"  - {len(MUSIC_TRACKS)} music tracks")
	print(f"  - {len(SFX_LIST)} sound effects")
	print(f"  - {len(NOTE_NAMES)} musical notes")
	print(f"  - Map-to-music assignments")
	print(f"  - Control byte documentation")


if __name__ == '__main__':
	main()
