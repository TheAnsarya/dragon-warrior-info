#!/usr/bin/env python3
"""
Extract NPC data from Dragon Warrior ROM

NPCs are stored in Mobile and Static tables per map.
Each entry is 3 bytes: sprite_type_flags, X_position, Y_position_and_flags
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

# ROM path
ROM_PATH = Path(__file__).parent.parent / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"
OUTPUT_PATH = Path(__file__).parent.parent / "assets" / "json" / "npcs_extracted.json"

# NES header size
NES_HEADER_SIZE = 16

# NPC sprite types (from disassembly)
# NNN bits in byte 1
# Note: Same sprite graphics are used for different characters in different contexts
SPRITE_TYPES = {
	0: "Male Villager",
	1: "Fighter",
	2: "Guard",
	3: "Shopkeeper",
	4: "King Lorik",
	5: "Wizard",           # Also used for Dragonlord (same sprite)
	6: "Female Villager",  # Also used for Princess Gwaelin (same sprite)
	7: "Trumpet Guard",    # Stationary guard with trumpet
}

# Direction types
DIRECTIONS = {
	0: "Up",
	1: "Right",
	2: "Down",
	3: "Left",
}

# Map names by ID
MAP_NAMES = {
	4: "Tantegel Castle",
	5: "Throne Room",
	6: "Tantegel Sublevel",
	7: "Charlock Bottom (Dragonlord Fight)",
	8: "Staff of Rain Cave",
	9: "Rainbow Drop Cave",
	10: "Cantlin",
	11: "Rimuldar",
	12: "Brecconary",
	13: "Garinham",
	14: "Kol",
	# Add more as needed
}

# NPC table offsets from Bank00.asm comments
# ROM offset = (Bank address - 0x8000) + NES_HEADER_SIZE
# Bank00 addresses from comments in disassembly
NPC_TABLES = [
	("TantagelMobileTable", "Tantegel Mobile", 0x9764 - 0x8000 + NES_HEADER_SIZE),
	("TantStatTbl", "Tantegel Static", 0x9783 - 0x8000 + NES_HEADER_SIZE),
	("ThRmMobTbl", "Throne Room Mobile", 0x97a2 - 0x8000 + NES_HEADER_SIZE),
	("ThRmStatTbl", "Throne Room Static", 0x97a6 - 0x8000 + NES_HEADER_SIZE),
	("TaSLMobTbl", "Tantegel SL Mobile", 0x97b3 - 0x8000 + NES_HEADER_SIZE),
	("TaSLStatTbl", "Tantegel SL Static", 0x97b4 - 0x8000 + NES_HEADER_SIZE),
	("TaDLMobTbl", "Tantegel DL Mobile", 0x97b8 - 0x8000 + NES_HEADER_SIZE),
	("TaDLStatTbl", "Tantegel DL Static", 0x97ce - 0x8000 + NES_HEADER_SIZE),
	("DLBFMobTbl", "DragonLord BF Mobile", 0x97ea - 0x8000 + NES_HEADER_SIZE),
	("DLBFStatTbl", "DragonLord BF Static", 0x97eb - 0x8000 + NES_HEADER_SIZE),
	("RainMobTbl", "Rain Cave Mobile", 0x97ef - 0x8000 + NES_HEADER_SIZE),
	("RainStatTbl", "Rain Cave Static", 0x97f0 - 0x8000 + NES_HEADER_SIZE),
	("RnbwMobTbl", "Rainbow Cave Mobile", 0x97f4 - 0x8000 + NES_HEADER_SIZE),
	("RnbwStatTbl", "Rainbow Cave Static", 0x97f5 - 0x8000 + NES_HEADER_SIZE),
	("CantMobTbl", "Cantlin Mobile", 0x97f9 - 0x8000 + NES_HEADER_SIZE),
	("CantStatTbl", "Cantlin Static", 0x9818 - 0x8000 + NES_HEADER_SIZE),
	("RimMobTbl", "Rimuldar Mobile", 0x9837 - 0x8000 + NES_HEADER_SIZE),
	("RimStatTbl", "Rimuldar Static", 0x9856 - 0x8000 + NES_HEADER_SIZE),
	("BrecMobTbl", "Brecconary Mobile", 0x9875 - 0x8000 + NES_HEADER_SIZE),
	("BrecStatTbl", "Brecconary Static", 0x9894 - 0x8000 + NES_HEADER_SIZE),
	("KolMobTbl", "Kol Mobile", 0x98b3 - 0x8000 + NES_HEADER_SIZE),
	("KolStatTbl", "Kol Static", 0x98cf - 0x8000 + NES_HEADER_SIZE),
	("GarMobTbl", "Garinham Mobile", 0x98e5 - 0x8000 + NES_HEADER_SIZE),
	("GarStatTbl", "Garinham Static", 0x98fb - 0x8000 + NES_HEADER_SIZE),
]


def decode_npc_entry(byte1, byte2, byte3):
	"""
	Decode a 3-byte NPC entry.

	Format from disassembly:
	NNNXXXXX _DDYYYYY CCCCCCCC

	Byte 1: NNN = NPC graphic (3 bits), XXXXX = X position (5 bits)
	Byte 2: _ = unused, DD = direction (2 bits), YYYYY = Y position (5 bits)
	Byte 3: Dialog control byte
	"""
	# Byte 1: NNNXXXXX
	sprite_type = (byte1 >> 5) & 0x07  # Top 3 bits
	x_pos = byte1 & 0x1f  # Bottom 5 bits

	# Byte 2: _DDYYYYY
	direction = (byte2 >> 5) & 0x03  # Bits 5-6 (2 bits)
	y_pos = byte2 & 0x1f  # Bottom 5 bits

	# Byte 3: Dialog control
	dialog_id = byte3

	return {
		"sprite_type": sprite_type,
		"sprite_name": SPRITE_TYPES.get(sprite_type, f"Unknown_{sprite_type}"),
		"x": x_pos,
		"y": y_pos,
		"direction": direction,
		"direction_name": DIRECTIONS.get(direction, f"Unknown_{direction}"),
		"dialog_id": dialog_id,
		"raw_bytes": [byte1, byte2, byte3]
	}


def extract_npc_table(rom_data, offset, table_name):
	"""Extract all NPCs from a table until 0xff terminator."""
	npcs = []
	pos = offset

	while pos + 2 < len(rom_data):
		byte1 = rom_data[pos]

		# 0xff marks end of table
		if byte1 == 0xff:
			break

		byte2 = rom_data[pos + 1]
		byte3 = rom_data[pos + 2]

		npc = decode_npc_entry(byte1, byte2, byte3)
		npc["offset"] = f"${pos - NES_HEADER_SIZE + 0x8000:04X}"
		npcs.append(npc)

		pos += 3

	return npcs


def extract_all_npcs():
	"""Extract all NPC data from ROM."""
	print(f"Reading ROM: {ROM_PATH}")

	with open(ROM_PATH, "rb") as f:
		rom_data = f.read()

	print(f"ROM size: {len(rom_data)} bytes")

	all_npcs = {}

	for label, table_name, offset in NPC_TABLES:
		print(f"\nExtracting {table_name} ({label}) at offset 0x{offset:04X}...")

		npcs = extract_npc_table(rom_data, offset, table_name)

		all_npcs[label] = {
			"name": table_name,
			"offset": f"${offset - NES_HEADER_SIZE + 0x8000:04X}",
			"count": len(npcs),
			"npcs": npcs
		}

		print(f"  Found {len(npcs)} NPCs")
		for npc in npcs:
			print(f"    {npc['sprite_name']:25s} at ({npc['x']:2d}, {npc['y']:2d})")

	return all_npcs


def main():
	npcs = extract_all_npcs()

	# Calculate totals
	total = sum(t["count"] for t in npcs.values())

	print(f"\n\nTotal NPCs extracted: {total}")
	print(f"Saving to: {OUTPUT_PATH}")

	with open(OUTPUT_PATH, "w") as f:
		json.dump(npcs, f, indent="\t")

	print("Done!")


if __name__ == "__main__":
	main()
