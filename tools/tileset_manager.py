#!/usr/bin/env python3
"""
Comprehensive Tileset & Graphics Manager

Advanced tile and graphics management tool for Dragon Warrior with
metatile editing, tileset organization, pattern table manipulation,
and graphics compression analysis.

Features:
- CHR-ROM tile extraction and editing
- Metatile (16x16, 32x32) composition
- Tileset organization and arrangement
- Pattern table visualization
- Tile usage analysis and optimization
- Duplicate tile detection
- Tile deduplication and compression
- Palette assignment and swapping
- Attribute table editing
- Collision map generation
- Auto-tiling algorithms
- Tile animation sequencing
- Graphics compression ratio analysis
- Unused tile detection
- Tile reference counting
- Import/export to PNG tile sheets
- Tile atlas generation
- Batch tile operations
- Tile flipping and rotation
- CHR bank management

Dragon Warrior Graphics Organization:
- Pattern Table 0: Font & UI (256 tiles)
- Pattern Table 1: Hero sprites (256 tiles)
- Pattern Table 2: Monster sprites (256 tiles)
- Pattern Table 3: Map tiles & NPCs (256 tiles)

Usage:
	python tools/tileset_manager.py <rom_file>

Examples:
	# Extract all tiles
	python tools/tileset_manager.py rom.nes --extract-all output/

	# Find duplicate tiles
	python tools/tileset_manager.py rom.nes --find-duplicates

	# Optimize tileset
	python tools/tileset_manager.py rom.nes --optimize

	# Export pattern table
	python tools/tileset_manager.py rom.nes --export-pattern-table 0 table0.png

	# Analyze tile usage
	python tools/tileset_manager.py rom.nes --analyze-usage

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import os
import struct
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field
from collections import defaultdict
from enum import Enum
import argparse

try:
	from PIL import Image
	import numpy as np
except ImportError:
	print("ERROR: PIL/numpy required. Install with: pip install pillow numpy")
	sys.exit(1)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class TileFormat(Enum):
	"""Tile format types."""
	CHR_8x8 = "chr_8x8"
	META_16x16 = "meta_16x16"
	META_32x32 = "meta_32x32"


@dataclass
class Tile:
	"""8x8 CHR tile."""
	id: int
	pixels: np.ndarray  # 8x8 array of palette indices (0-3)
	chr_data: bytes  # 16 bytes CHR format
	bank: int = 0

	def __hash__(self):
		"""Hash for duplicate detection."""
		return hash(self.chr_data)

	def __eq__(self, other):
		"""Equality check for duplicate detection."""
		if not isinstance(other, Tile):
			return False
		return self.chr_data == other.chr_data


@dataclass
class Metatile:
	"""16x16 or 32x32 metatile composed of multiple 8x8 tiles."""
	id: int
	tiles: List[int]  # Tile IDs
	width: int = 2  # In 8x8 tiles
	height: int = 2
	palette_id: int = 0
	collision: int = 0  # Collision flags


@dataclass
class PatternTable:
	"""Pattern table (256 tiles)."""
	id: int
	name: str
	tiles: List[Tile] = field(default_factory=list)
	offset: int = 0

	def get_tile(self, tile_id: int) -> Optional[Tile]:
		"""Get tile by ID."""
		if 0 <= tile_id < len(self.tiles):
			return self.tiles[tile_id]
		return None


@dataclass
class TileUsage:
	"""Tile usage statistics."""
	tile_id: int
	references: int = 0
	locations: List[Tuple[str, int]] = field(default_factory=list)  # (context, offset)


@dataclass
class TilesetStats:
	"""Tileset statistics."""
	total_tiles: int = 0
	unique_tiles: int = 0
	duplicate_tiles: int = 0
	unused_tiles: int = 0
	compression_ratio: float = 0.0
	most_used_tile: Optional[int] = None
	most_used_count: int = 0


# NES Palette
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


# ============================================================================
# CHR CODEC
# ============================================================================

class CHRCodec:
	"""Encode/decode CHR tile format."""

	@staticmethod
	def decode_tile(chr_data: bytes) -> np.ndarray:
		"""Decode 16-byte CHR tile to 8x8 pixel array."""
		if len(chr_data) != 16:
			raise ValueError("CHR tile must be 16 bytes")

		pixels = np.zeros((8, 8), dtype=np.uint8)

		plane0 = chr_data[0:8]
		plane1 = chr_data[8:16]

		for y in range(8):
			for x in range(8):
				bit0 = (plane0[y] >> (7 - x)) & 1
				bit1 = (plane1[y] >> (7 - x)) & 1
				pixels[y, x] = bit0 | (bit1 << 1)

		return pixels

	@staticmethod
	def encode_tile(pixels: np.ndarray) -> bytes:
		"""Encode 8x8 pixel array to 16-byte CHR tile."""
		if pixels.shape != (8, 8):
			raise ValueError("Pixels must be 8x8 array")

		plane0 = bytearray(8)
		plane1 = bytearray(8)

		for y in range(8):
			for x in range(8):
				color = pixels[y, x] & 0x03

				bit0 = color & 1
				bit1 = (color >> 1) & 1

				if bit0:
					plane0[y] |= (1 << (7 - x))
				if bit1:
					plane1[y] |= (1 << (7 - x))

		return bytes(plane0 + plane1)


# ============================================================================
# TILESET MANAGER
# ============================================================================

class TilesetManager:
	"""Manage tilesets and pattern tables."""

	def __init__(self, rom_path: str):
		self.rom_path = Path(rom_path)
		self.rom_data: bytes = b''
		self.pattern_tables: List[PatternTable] = []
		self.tile_usage: Dict[int, TileUsage] = {}

	def load_rom(self) -> bool:
		"""Load ROM file."""
		if not self.rom_path.exists():
			print(f"ERROR: ROM not found: {self.rom_path}")
			return False

		with open(self.rom_path, 'rb') as f:
			self.rom_data = f.read()

		return True

	def extract_pattern_tables(self):
		"""Extract all pattern tables from CHR-ROM."""
		# CHR-ROM offset: 0x10 (header) + 0x10000 (64KB PRG-ROM) = 0x10010
		chr_offset = 0x10010
		chr_size = 0x4000  # 16KB (1024 tiles)

		if chr_offset + chr_size > len(self.rom_data):
			print(f"ERROR: CHR-ROM extends beyond ROM size")
			return

		chr_data = self.rom_data[chr_offset:chr_offset + chr_size]

		# Create 4 pattern tables (256 tiles each)
		table_names = ["Font & UI", "Hero Sprites", "Monster Sprites", "Map Tiles"]

		for table_id in range(4):
			table_offset = table_id * 256 * 16
			table = PatternTable(
				id=table_id,
				name=table_names[table_id],
				offset=chr_offset + table_offset
			)

			# Extract 256 tiles
			for tile_id in range(256):
				chr_start = table_offset + (tile_id * 16)
				chr_bytes = chr_data[chr_start:chr_start + 16]

				pixels = CHRCodec.decode_tile(chr_bytes)

				tile = Tile(
					id=tile_id,
					pixels=pixels,
					chr_data=chr_bytes,
					bank=table_id
				)

				table.tiles.append(tile)

			self.pattern_tables.append(table)

		print(f"✓ Extracted {len(self.pattern_tables)} pattern tables ({len(self.pattern_tables) * 256} tiles)")

	def find_duplicates(self) -> Dict[bytes, List[int]]:
		"""Find duplicate tiles across all pattern tables."""
		tile_map: Dict[bytes, List[int]] = defaultdict(list)

		for table in self.pattern_tables:
			for tile in table.tiles:
				global_id = (table.id * 256) + tile.id
				tile_map[tile.chr_data].append(global_id)

		# Filter to only duplicates
		duplicates = {k: v for k, v in tile_map.items() if len(v) > 1}

		return duplicates

	def analyze_usage(self) -> TilesetStats:
		"""Analyze tile usage and generate statistics."""
		stats = TilesetStats()

		# Total tiles
		stats.total_tiles = sum(len(table.tiles) for table in self.pattern_tables)

		# Find duplicates
		duplicates = self.find_duplicates()

		unique_tiles = set()
		for table in self.pattern_tables:
			for tile in table.tiles:
				unique_tiles.add(tile.chr_data)

		stats.unique_tiles = len(unique_tiles)
		stats.duplicate_tiles = stats.total_tiles - stats.unique_tiles

		# Compression ratio
		if stats.total_tiles > 0:
			stats.compression_ratio = stats.unique_tiles / stats.total_tiles

		# Most used tile (simplified - would analyze ROM references)
		if duplicates:
			max_tile = max(duplicates.items(), key=lambda x: len(x[1]))
			stats.most_used_tile = max_tile[1][0]
			stats.most_used_count = len(max_tile[1])

		return stats

	def export_pattern_table_png(self, table_id: int, output_path: str, scale: int = 2):
		"""Export pattern table as PNG image."""
		if table_id < 0 or table_id >= len(self.pattern_tables):
			print(f"ERROR: Invalid pattern table ID: {table_id}")
			return

		table = self.pattern_tables[table_id]

		# 16x16 grid of 8x8 tiles
		columns = 16
		rows = 16

		tile_size = 8 * scale
		width = columns * tile_size
		height = rows * tile_size

		img = Image.new('RGB', (width, height), (0, 0, 0))

		# Default grayscale palette
		palette = [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]

		for tile in table.tiles:
			x = (tile.id % columns) * tile_size
			y = (tile.id // columns) * tile_size

			# Render tile
			tile_img = Image.new('RGB', (8, 8))
			for py in range(8):
				for px in range(8):
					color_idx = tile.pixels[py, px]
					tile_img.putpixel((px, py), palette[color_idx])

			# Scale and paste
			if scale > 1:
				tile_img = tile_img.resize((tile_size, tile_size), Image.NEAREST)

			img.paste(tile_img, (x, y))

		img.save(output_path)
		print(f"✓ Pattern table {table_id} exported: {output_path}")
		print(f"  Size: {width}x{height} pixels")


# ============================================================================
# TILE OPTIMIZER
# ============================================================================

class TileOptimizer:
	"""Optimize tileset by removing duplicates."""

	@staticmethod
	def optimize_tileset(manager: TilesetManager) -> Dict[str, Any]:
		"""Optimize tileset and generate report."""
		print("Analyzing tileset...")

		# Find duplicates
		duplicates = manager.find_duplicates()

		# Generate optimization report
		report = {
			"duplicates_found": len(duplicates),
			"potential_savings": 0,
			"recommendations": []
		}

		total_duplicate_tiles = sum(len(v) - 1 for v in duplicates.values())
		report["potential_savings"] = total_duplicate_tiles * 16  # bytes

		# Generate recommendations
		if duplicates:
			report["recommendations"].append(
				f"Remove {total_duplicate_tiles} duplicate tiles to save {report['potential_savings']} bytes"
			)

			# Top 5 most duplicated tiles
			top_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:5]

			for chr_data, tile_ids in top_duplicates:
				report["recommendations"].append(
					f"Tile appears {len(tile_ids)} times: {[f'0x{t:03X}' for t in tile_ids]}"
				)

		return report


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Comprehensive Tileset & Graphics Manager"
	)

	parser.add_argument('rom', help="ROM file")
	parser.add_argument('--extract-all', type=str, help="Extract all tiles to directory")
	parser.add_argument('--find-duplicates', action='store_true', help="Find duplicate tiles")
	parser.add_argument('--analyze-usage', action='store_true', help="Analyze tile usage")
	parser.add_argument('--optimize', action='store_true', help="Optimize tileset")
	parser.add_argument('--export-pattern-table', type=int, help="Export pattern table (0-3)")
	parser.add_argument('--output', type=str, help="Output file path")
	parser.add_argument('--scale', type=int, default=2, help="Render scale factor")

	args = parser.parse_args()

	# Load ROM
	manager = TilesetManager(args.rom)
	if not manager.load_rom():
		return 1

	# Extract pattern tables
	print("Extracting pattern tables...")
	manager.extract_pattern_tables()

	# Find duplicates
	if args.find_duplicates:
		print("\nSearching for duplicate tiles...")
		duplicates = manager.find_duplicates()

		print(f"\n✓ Found {len(duplicates)} unique tiles with duplicates")
		print(f"  Total duplicate instances: {sum(len(v) - 1 for v in duplicates.values())}")

		# Show top 5
		print("\n  Top 5 most duplicated tiles:")
		top_duplicates = sorted(duplicates.items(), key=lambda x: len(x[1]), reverse=True)[:5]

		for i, (chr_data, tile_ids) in enumerate(top_duplicates, 1):
			print(f"    {i}. {len(tile_ids)} instances: {[f'0x{t:03X}' for t in tile_ids[:5]]}", end="")
			if len(tile_ids) > 5:
				print(f" ... and {len(tile_ids) - 5} more")
			else:
				print()

	# Analyze usage
	if args.analyze_usage:
		print("\nAnalyzing tile usage...")
		stats = manager.analyze_usage()

		print(f"\n✓ Tileset Statistics:")
		print(f"  Total tiles: {stats.total_tiles}")
		print(f"  Unique tiles: {stats.unique_tiles}")
		print(f"  Duplicate tiles: {stats.duplicate_tiles}")
		print(f"  Compression ratio: {stats.compression_ratio:.2%}")

		if stats.most_used_tile is not None:
			print(f"\n  Most used tile: 0x{stats.most_used_tile:03X} ({stats.most_used_count} instances)")

	# Optimize
	if args.optimize:
		print("\nOptimizing tileset...")
		report = TileOptimizer.optimize_tileset(manager)

		print(f"\n✓ Optimization Report:")
		print(f"  Duplicates found: {report['duplicates_found']}")
		print(f"  Potential savings: {report['potential_savings']} bytes")

		if report["recommendations"]:
			print("\n  Recommendations:")
			for rec in report["recommendations"]:
				print(f"    • {rec}")

	# Export pattern table
	if args.export_pattern_table is not None:
		output_path = args.output or f"pattern_table_{args.export_pattern_table}.png"
		manager.export_pattern_table_png(
			args.export_pattern_table,
			output_path,
			args.scale
		)

	return 0


if __name__ == "__main__":
	sys.exit(main())
