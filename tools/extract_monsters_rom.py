#!/usr/bin/env python3
"""
Dragon Warrior Monster Sprite Extractor (ROM-based)

Extracts monster sprites directly from ROM using correct NES sprite format.
Uses Pattern Table 2 for monster tiles and proper OAM positioning.

Format (from ROM_HACKING_GUIDE.md):
  - Pointer table at 0x59f4 (39 monsters × 2 bytes)
  - Each sprite: triplets of (tile, attr_y, x_pal) terminated by 0x00
  - attr_y = VHYYYYYY (V=vflip, H=hflip, Y=Y offset 0-63)
  - x_pal = XXXXXXPP (X=X position 0-63, P=palette 0-3)

Usage:
	python tools/extract_monsters_rom.py ROM_FILE [--output DIR] [--monster ID]

Author: Dragon Warrior ROM Hacking Toolkit
Version: 3.0 - Direct ROM extraction with correct format
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass

try:
	from PIL import Image
	import numpy as np
except ImportError:
	print("ERROR: PIL and numpy required. Install with: pip install pillow numpy")
	sys.exit(1)


# ============================================================================
# CONSTANTS
# ============================================================================

# NES Palette (NTSC)
NES_PALETTE = [
	(124, 124, 124), (0, 0, 252), (0, 0, 188), (68, 40, 188),
	(148, 0, 132), (168, 0, 32), (168, 16, 0), (136, 20, 0),
	(80, 48, 0), (0, 120, 0), (0, 104, 0), (0, 88, 0),
	(0, 64, 88), (0, 0, 0), (0, 0, 0), (0, 0, 0),
	(188, 188, 188), (0, 120, 248), (0, 88, 248), (104, 68, 252),
	(216, 0, 204), (228, 0, 88), (248, 56, 0), (228, 92, 16),
	(172, 124, 0), (0, 184, 0), (0, 168, 0), (0, 168, 68),
	(0, 136, 136), (0, 0, 0), (0, 0, 0), (0, 0, 0),
	(248, 248, 248), (60, 188, 252), (104, 136, 252), (152, 120, 248),
	(248, 120, 248), (248, 88, 152), (248, 120, 88), (252, 160, 68),
	(248, 184, 0), (184, 248, 24), (88, 216, 84), (88, 248, 152),
	(0, 232, 216), (120, 120, 120), (0, 0, 0), (0, 0, 0),
	(252, 252, 252), (164, 228, 252), (184, 184, 248), (216, 184, 248),
	(248, 184, 248), (248, 164, 192), (240, 208, 176), (252, 224, 168),
	(248, 216, 120), (216, 248, 120), (184, 248, 184), (184, 248, 216),
	(0, 252, 252), (248, 216, 248), (0, 0, 0), (0, 0, 0),
]

# Monster names
MONSTER_NAMES = [
	"Slime", "Red Slime", "Drakee", "Ghost", "Magician",
	"Magidrakee", "Scorpion", "Druin", "Poltergeist", "Droll",
	"Drakeema", "Skeleton", "Warlock", "Metal Scorpion", "Wolf",
	"Wraith", "Metal Slime", "Specter", "Wolflord", "Druinlord",
	"Drollmagi", "Wyvern", "Rouge Scorpion", "Wraith Knight", "Golem",
	"Goldman", "Knight", "Magiwyvern", "Demon Knight", "Werewolf",
	"Green Dragon", "Starwyvern", "Wizard", "Axe Knight", "Blue Dragon",
	"Stoneman", "Armored Knight", "Red Dragon", "Dragonlord"
]

# Default palettes (these should ideally be read from ROM palette tables)
DEFAULT_PALETTES = [
	[0x0f, 0x1c, 0x15, 0x30],  # Cyan/Magenta/White (Slime)
	[0x0f, 0x16, 0x0d, 0x30],  # Red/Black/White (Red Slime)
	[0x0f, 0x01, 0x15, 0x30],  # Blue/Magenta/White (Drakee)
	[0x0f, 0x13, 0x15, 0x30],  # Purple/Magenta/White (Ghost)
]


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class SpriteEntry:
	"""Single sprite tile entry."""
	tile: int  # Tile index in Pattern Table 2
	y: int  # Y offset (0-63)
	x: int  # X position (0-63)
	palette: int  # Palette ID (0-3)
	h_flip: bool  # Horizontal flip
	v_flip: bool  # Vertical flip


@dataclass
class MonsterSprite:
	"""Complete monster sprite."""
	id: int
	name: str
	entries: List[SpriteEntry]
	default_palette: int = 0


# ============================================================================
# CHR DECODER
# ============================================================================

def decode_chr_tile(chr_data: bytes) -> np.ndarray:
	"""Decode 16-byte CHR tile to 8x8 pixel array."""
	if len(chr_data) != 16:
		raise ValueError(f"CHR tile must be 16 bytes, got {len(chr_data)}")

	pixels = np.zeros((8, 8), dtype=np.uint8)
	plane0 = chr_data[0:8]
	plane1 = chr_data[8:16]

	for y in range(8):
		for x in range(8):
			bit0 = (plane0[y] >> (7 - x)) & 1
			bit1 = (plane1[y] >> (7 - x)) & 1
			pixels[y, x] = bit0 | (bit1 << 1)

	return pixels


def decode_pattern_table(chr_data: bytes, table_id: int) -> List[np.ndarray]:
	"""Decode one pattern table (256 tiles)."""
	offset = table_id * 0x1000  # 4KB per table
	table_data = chr_data[offset:offset + 0x1000]

	tiles = []
	for i in range(256):
		tile_offset = i * 16
		tile_data = table_data[tile_offset:tile_offset + 16]
		pixels = decode_chr_tile(tile_data)
		tiles.append(pixels)

	return tiles


# ============================================================================
# ROM EXTRACTOR
# ============================================================================

class ROMExtractor:
	"""Extract monster sprites from ROM."""

	SPRITE_PTR_TABLE = 0x59f4  # Pointer table offset
	CHR_OFFSET = 0x10010  # CHR-ROM offset
	CHR_SIZE = 0x4000  # 16KB

	def __init__(self, rom_data: bytes):
		self.rom = rom_data

		# Extract and decode Pattern Table 2 (monster tiles)
		chr_data = rom_data[self.CHR_OFFSET:self.CHR_OFFSET + self.CHR_SIZE]
		self.tiles = decode_pattern_table(chr_data, table_id=2)

	def extract_monster(self, monster_id: int) -> Optional[MonsterSprite]:
		"""Extract single monster sprite."""
		if monster_id >= len(MONSTER_NAMES):
			return None

		# Read pointer
		ptr_offset = self.SPRITE_PTR_TABLE + (monster_id * 2)
		ptr = (self.rom[ptr_offset + 1] << 8) | self.rom[ptr_offset]

		# Convert to ROM offset (pointer is offset within bank + 0x4000)
		rom_offset = ptr + 0x4000

		if rom_offset >= len(self.rom):
			print(f"  Warning: Invalid offset for {MONSTER_NAMES[monster_id]}")
			return None

		# Read sprite entries
		entries = []
		offset = rom_offset

		for _ in range(32):  # Max 32 tiles per sprite
			if offset + 2 >= len(self.rom):
				break

			tile = self.rom[offset]
			if tile == 0x00:  # Terminator
				break

			attr_y = self.rom[offset + 1]
			x_pal = self.rom[offset + 2]

			# Decode attr_y (VHYYYYYY)
			v_flip = (attr_y & 0x80) != 0
			h_flip = (attr_y & 0x40) != 0
			y = attr_y & 0x3f

			# Decode x_pal (XXXXXXPP)
			x = (x_pal >> 2) & 0x3f
			palette = x_pal & 0x03

			entry = SpriteEntry(
				tile=tile,
				y=y,
				x=x,
				palette=palette,
				h_flip=h_flip,
				v_flip=v_flip
			)

			entries.append(entry)
			offset += 3

		if not entries:
			return None

		return MonsterSprite(
			id=monster_id,
			name=MONSTER_NAMES[monster_id],
			entries=entries
		)

	def extract_all(self) -> List[MonsterSprite]:
		"""Extract all 39 monsters."""
		monsters = []
		for i in range(len(MONSTER_NAMES)):
			monster = self.extract_monster(i)
			if monster:
				monsters.append(monster)
		return monsters


# ============================================================================
# SPRITE RENDERER
# ============================================================================

def render_tile(tile_pixels: np.ndarray, palette: List[int],
				h_flip: bool = False, v_flip: bool = False) -> np.ndarray:
	"""Render 8x8 tile with palette and flips."""
	pixels = tile_pixels.copy()

	if h_flip:
		pixels = np.fliplr(pixels)
	if v_flip:
		pixels = np.flipud(pixels)

	img = np.zeros((8, 8, 4), dtype=np.uint8)

	for y in range(8):
		for x in range(8):
			pal_idx = pixels[y, x]
			if pal_idx == 0:
				img[y, x] = [0, 0, 0, 0]  # Transparent
			else:
				rgb = NES_PALETTE[palette[pal_idx]]
				img[y, x] = [rgb[0], rgb[1], rgb[2], 255]

	return img


def render_monster(monster: MonsterSprite, tiles: List[np.ndarray],
				   palette: List[int], scale: int = 2) -> Image.Image:
	"""Render complete monster sprite."""
	if not monster.entries:
		return Image.new('RGBA', (16, 16), (0, 0, 0, 0))

	# Find bounds
	min_x = min(e.x for e in monster.entries)
	max_x = max(e.x for e in monster.entries) + 8
	min_y = min(e.y for e in monster.entries)
	max_y = max(e.y for e in monster.entries) + 8

	width = max_x - min_x
	height = max_y - min_y

	# Create canvas
	canvas = np.zeros((height, width, 4), dtype=np.uint8)

	# Render each tile
	for entry in monster.entries:
		if entry.tile >= len(tiles):
			continue

		tile_img = render_tile(
			tiles[entry.tile],
			palette,
			entry.h_flip,
			entry.v_flip
		)

		# Position on canvas
		x_pos = entry.x - min_x
		y_pos = entry.y - min_y

		# Composite
		for ty in range(8):
			for tx in range(8):
				cy = y_pos + ty
				cx = x_pos + tx

				if 0 <= cy < height and 0 <= cx < width:
					pixel = tile_img[ty, tx]
					if pixel[3] > 0:  # Not transparent
						canvas[cy, cx] = pixel

	# Convert to PIL Image
	img = Image.fromarray(canvas, 'RGBA')

	# Scale
	if scale > 1:
		img = img.resize((width * scale, height * scale), Image.NEAREST)

	return img


# ============================================================================
# MAIN
# ============================================================================

def main():
	parser = argparse.ArgumentParser(description="Extract Dragon Warrior monster sprites from ROM")
	parser.add_argument('rom', help="Dragon Warrior ROM file")
	parser.add_argument('--output', default='extracted_monsters_rom', help="Output directory")
	parser.add_argument('--monster', type=int, metavar='ID', help="Extract specific monster (0-38)")
	parser.add_argument('--scale', type=int, default=4, help="Image scale factor")
	parser.add_argument('--list', action='store_true', help="List all monsters")

	args = parser.parse_args()

	# Load ROM
	print(f"Loading ROM: {args.rom}")
	try:
		with open(args.rom, 'rb') as f:
			rom_data = f.read()
	except Exception as e:
		print(f"ERROR: {e}")
		return 1

	# Create extractor
	extractor = ROMExtractor(rom_data)

	print(f"  ROM size: {len(rom_data):,} bytes")
	print(f"  Pattern Table 2: {len(extractor.tiles)} tiles")

	# List mode
	if args.list:
		monsters = extractor.extract_all()
		print(f"\nMonsters ({len(monsters)} total):")
		print("=" * 70)
		for m in monsters:
			tiles_str = ', '.join(str(e.tile) for e in m.entries[:5])
			if len(m.entries) > 5:
				tiles_str += '...'
			print(f"  {m.id:2d}. {m.name:<20} - {len(m.entries):2d} tiles [{tiles_str}]")
		return 0

	# Create output dir
	output_dir = Path(args.output)
	output_dir.mkdir(parents=True, exist_ok=True)

	# Extract
	if args.monster is not None:
		# Single monster
		monster = extractor.extract_monster(args.monster)
		if not monster:
			print(f"ERROR: Failed to extract monster {args.monster}")
			return 1

		print(f"\nExtracting {monster.name}...")
		print(f"  Tiles: {len(monster.entries)}")
		print(f"  Tile IDs: {[e.tile for e in monster.entries]}")

		# Use default palette for monster's palette index
		pal_idx = monster.entries[0].palette if monster.entries else 0
		palette = DEFAULT_PALETTES[pal_idx % len(DEFAULT_PALETTES)]

		img = render_monster(monster, extractor.tiles, palette, args.scale)

		output_file = output_dir / f"{monster.id:02d}_{monster.name.lower().replace(' ', '_')}.png"
		img.save(output_file)

		print(f"  ✓ Saved: {output_file}")
		print(f"  Size: {img.width}×{img.height} pixels")

	else:
		# All monsters
		monsters = extractor.extract_all()
		print(f"\nExtracting {len(monsters)} monsters...")

		for monster in monsters:
			pal_idx = monster.entries[0].palette if monster.entries else 0
			palette = DEFAULT_PALETTES[pal_idx % len(DEFAULT_PALETTES)]

			img = render_monster(monster, extractor.tiles, palette, args.scale)

			output_file = output_dir / f"{monster.id:02d}_{monster.name.lower().replace(' ', '_')}.png"
			img.save(output_file)

			print(f"  [{monster.id:2d}] {monster.name:<20} - {len(monster.entries):2d} tiles - {img.width:3d}×{img.height:3d}px")

		print(f"\n✓ Extracted {len(monsters)} monsters to: {output_dir}")

	return 0


if __name__ == "__main__":
	sys.exit(main())
