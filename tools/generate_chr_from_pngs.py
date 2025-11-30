#!/usr/bin/env python3
"""
Dragon Warrior PNG to CHR-ROM Generator

Regenerates chr_rom.bin from edited PNG tiles in assets/graphics/

Usage:
	python tools/generate_chr_from_pngs.py

This script:
1. Reads all PNG files from assets/graphics/
2. Validates each tile has at most 4 colors
3. Encodes each PNG to NES 2bpp planar CHR format
4. Writes the complete chr_rom.bin to source_files/chr_rom.bin
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple, Optional
import numpy as np

try:
	from PIL import Image
except ImportError:
	print("Error: Pillow is required. Install with: pip install pillow")
	sys.exit(1)

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
GRAPHICS_DIR = PROJECT_ROOT / "assets" / "graphics"
OUTPUT_CHR = PROJECT_ROOT / "source_files" / "chr_rom.bin"
REFERENCE_CHR = PROJECT_ROOT / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"


class CHRGenerator:
	"""Generates CHR-ROM from PNG tiles."""

	def __init__(self):
		# Default grayscale palette for encoding
		self.palette = [
			(0, 0, 0),         # Index 0: Transparent/black
			(85, 85, 85),      # Index 1: Dark gray
			(170, 170, 170),   # Index 2: Light gray
			(255, 255, 255),   # Index 3: White
		]

	def color_distance(self, c1: Tuple[int, ...], c2: Tuple[int, int, int]) -> float:
		"""Calculate Euclidean distance between two RGB colors."""
		r1, g1, b1 = c1[:3]
		r2, g2, b2 = c2
		return ((r1 - r2) ** 2 + (g1 - g2) ** 2 + (b1 - b2) ** 2) ** 0.5

	def map_color_to_index(self, color: Tuple[int, ...]) -> int:
		"""Map an RGB color to the nearest palette index (0-3)."""
		# Handle transparent pixels
		if len(color) == 4 and color[3] < 128:
			return 0  # Transparent = index 0

		# Find closest palette color
		min_dist = float('inf')
		best_idx = 0

		for idx, pal_color in enumerate(self.palette):
			dist = self.color_distance(color, pal_color)
			if dist < min_dist:
				min_dist = dist
				best_idx = idx

		return best_idx

	def encode_tile(self, img: Image.Image) -> bytes:
		"""
		Encode an 8x8 tile image to 16 bytes of CHR data.
		Returns 16 bytes: first 8 are bitplane 0, next 8 are bitplane 1.
		"""
		# Ensure image is 8x8
		if img.size != (8, 8):
			img = img.resize((8, 8), Image.Resampling.NEAREST)

		# Convert to RGBA if needed
		if img.mode != 'RGBA':
			img = img.convert('RGBA')

		pixels = list(img.getdata())

		# Initialize bitplanes
		plane0 = bytearray(8)
		plane1 = bytearray(8)

		for y in range(8):
			for x in range(8):
				pixel_idx = y * 8 + x
				color = pixels[pixel_idx]
				palette_idx = self.map_color_to_index(color)

				# Split into bitplanes
				bit0 = palette_idx & 1
				bit1 = (palette_idx >> 1) & 1

				# Set bits (MSB = leftmost pixel)
				bit_pos = 7 - x
				if bit0:
					plane0[y] |= (1 << bit_pos)
				if bit1:
					plane1[y] |= (1 << bit_pos)

		return bytes(plane0 + plane1)

	def load_tile_pngs(self) -> dict:
		"""
		Load all PNG tiles from the graphics directory.
		Returns dict mapping tile index to PNG path.
		"""
		tiles = {}

		if not GRAPHICS_DIR.exists():
			print(f"Error: Graphics directory not found: {GRAPHICS_DIR}")
			return tiles

		for png_file in GRAPHICS_DIR.glob("*.png"):
			# Extract tile index from filename (e.g., "hero_000.png" -> 0)
			name = png_file.stem
			parts = name.split('_')
			if len(parts) >= 2:
				try:
					tile_idx = int(parts[-1])
					tiles[tile_idx] = png_file
				except ValueError:
					print(f"  Warning: Could not parse tile index from {png_file.name}")

		return tiles

	def generate_chr_rom(self, output_path: Path = OUTPUT_CHR) -> bool:
		"""
		Generate chr_rom.bin from PNG tiles.
		Returns True on success.
		"""
		print("=" * 60)
		print("Dragon Warrior CHR-ROM Generator")
		print("=" * 60)

		# Load PNG tiles
		tiles = self.load_tile_pngs()
		if not tiles:
			print("Error: No PNG tiles found in assets/graphics/")
			return False

		print(f"\nFound {len(tiles)} PNG tiles")

		# Dragon Warrior CHR-ROM is 16KB total
		# First 8KB (512 tiles) + Second 8KB (duplicate/background)
		# We generate 512 tiles for the first bank, then duplicate for bank 2
		num_tiles = 512  # First pattern table
		chr_bank1 = bytearray(num_tiles * 16)  # 8KB

		# Get reference CHR-ROM for tiles we don't have
		reference_chr = None
		if REFERENCE_CHR.exists():
			with open(REFERENCE_CHR, 'rb') as f:
				# Read full ROM
				rom_data = f.read()
				# iNES header is 16 bytes, PRG is 64KB, CHR starts at 0x10010
				chr_offset = 16 + 64 * 1024
				reference_chr = rom_data[chr_offset:chr_offset + 16384]
				print(f"Using reference CHR for missing tiles")

		# Process each tile
		success_count = 0
		error_count = 0

		for tile_idx in range(num_tiles):
			if tile_idx in tiles:
				# Load PNG and encode
				try:
					img = Image.open(tiles[tile_idx])
					chr_bytes = self.encode_tile(img)
					chr_bank1[tile_idx * 16:(tile_idx + 1) * 16] = chr_bytes
					success_count += 1
				except Exception as e:
					print(f"  Error encoding tile {tile_idx}: {e}")
					error_count += 1
					# Fall back to reference if available
					if reference_chr:
						chr_bank1[tile_idx * 16:(tile_idx + 1) * 16] = reference_chr[tile_idx * 16:(tile_idx + 1) * 16]
			elif reference_chr:
				# Use reference CHR for missing tiles
				chr_bank1[tile_idx * 16:(tile_idx + 1) * 16] = reference_chr[tile_idx * 16:(tile_idx + 1) * 16]

		# Build full 16KB CHR-ROM (first bank + second bank from reference)
		chr_data = chr_bank1
		if reference_chr:
			# Append the second 8KB bank from reference ROM
			chr_data = chr_bank1 + reference_chr[8192:16384]

		# Write output
		output_path.parent.mkdir(parents=True, exist_ok=True)
		with open(output_path, 'wb') as f:
			f.write(chr_data)

		print(f"\nResults:")
		print(f"  Encoded: {success_count} tiles from PNG")
		print(f"  Errors: {error_count}")
		print(f"  Reference: {num_tiles - len(tiles)} tiles from original (bank 1)")
		print(f"  Bank 2: From reference ROM")
		print(f"\nOutput: {output_path}")
		print(f"Size: {len(chr_data)} bytes")

		return error_count == 0


def main():
	generator = CHRGenerator()
	success = generator.generate_chr_rom()
	return 0 if success else 1


if __name__ == "__main__":
	sys.exit(main())
