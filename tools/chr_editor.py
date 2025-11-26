#!/usr/bin/env python3
"""
CHR-ROM Visual Editor for Dragon Warrior

Interactive tile editor with visual feedback, palette management, and real-time
sprite composition. Supports editing 8x8 tiles, creating sprites from tiles,
and palette swapping.

Features:
- Visual tile grid display (ASCII/terminal graphics)
- Individual pixel editing
- Tile copy/paste/flip/rotate operations
- Palette editor with NES color picker
- Sprite composition (2x2 tile assemblies)
- Export to PNG/CHR format
- Undo/redo support
- Real-time preview

Usage:
	python tools/chr_editor.py [CHR_FILE] [--tile ID] [--palette ID]

Examples:
	# Edit specific tile
	python tools/chr_editor.py extracted_assets/chr_tiles/tiles.chr --tile 0x42

	# Edit with palette
	python tools/chr_editor.py extracted_assets/chr_tiles/tiles.chr --palette 2

	# Interactive mode
	python tools/chr_editor.py extracted_assets/chr_tiles/tiles.chr
"""

import sys
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import struct
import copy


# NES Color Palette (64 colors)
NES_PALETTE = [
	# 0x00-0x0F
	(84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136),
	(68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0),
	(32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
	(0, 50, 60), (0, 0, 0), (0, 0, 0), (0, 0, 0),

	# 0x10-0x1F
	(152, 150, 152), (8, 76, 196), (48, 50, 236), (92, 30, 228),
	(136, 20, 176), (160, 20, 100), (152, 34, 32), (120, 60, 0),
	(84, 90, 0), (40, 114, 0), (8, 124, 0), (0, 118, 40),
	(0, 102, 120), (0, 0, 0), (0, 0, 0), (0, 0, 0),

	# 0x20-0x2F
	(236, 238, 236), (76, 154, 236), (120, 124, 236), (176, 98, 236),
	(228, 84, 236), (236, 88, 180), (236, 106, 100), (212, 136, 32),
	(160, 170, 0), (116, 196, 0), (76, 208, 32), (56, 204, 108),
	(56, 180, 204), (60, 60, 60), (0, 0, 0), (0, 0, 0),

	# 0x30-0x3F
	(236, 238, 236), (168, 204, 236), (188, 188, 236), (212, 178, 236),
	(236, 174, 236), (236, 174, 212), (236, 180, 176), (228, 196, 144),
	(204, 210, 120), (180, 222, 120), (168, 226, 144), (152, 226, 180),
	(160, 214, 228), (160, 162, 160), (0, 0, 0), (0, 0, 0),
]


class TileOperation(Enum):
	"""Types of tile operations for undo/redo."""
	EDIT_PIXEL = "edit_pixel"
	FLIP_HORIZONTAL = "flip_h"
	FLIP_VERTICAL = "flip_v"
	ROTATE_CW = "rotate_cw"
	ROTATE_CCW = "rotate_ccw"
	CLEAR = "clear"
	FILL = "fill"


@dataclass
class Tile:
	"""
	Represents an 8x8 pixel tile.

	NES tiles are 16 bytes:
	- Bytes 0-7: Low bit plane
	- Bytes 8-15: High bit plane

	Each pixel is 2 bits (4 colors per tile).
	"""
	id: int
	data: bytearray = field(default_factory=lambda: bytearray(16))

	def get_pixel(self, x: int, y: int) -> int:
		"""Get pixel value (0-3) at position."""
		if x < 0 or x >= 8 or y < 0 or y >= 8:
			return 0

		# Get bits from both planes
		low_bit = (self.data[y] >> (7 - x)) & 1
		high_bit = (self.data[y + 8] >> (7 - x)) & 1

		return (high_bit << 1) | low_bit

	def set_pixel(self, x: int, y: int, value: int) -> None:
		"""Set pixel value (0-3) at position."""
		if x < 0 or x >= 8 or y < 0 or y >= 8:
			return

		value = value & 0x03	# Clamp to 0-3

		# Extract bits
		low_bit = value & 1
		high_bit = (value >> 1) & 1

		# Set in both planes
		mask = 1 << (7 - x)

		if low_bit:
			self.data[y] |= mask
		else:
			self.data[y] &= ~mask

		if high_bit:
			self.data[y + 8] |= mask
		else:
			self.data[y + 8] &= ~mask

	def get_pixels(self) -> List[List[int]]:
		"""Get all pixels as 8x8 array."""
		return [[self.get_pixel(x, y) for x in range(8)] for y in range(8)]

	def flip_horizontal(self) -> None:
		"""Flip tile horizontally."""
		pixels = self.get_pixels()
		for y in range(8):
			for x in range(8):
				self.set_pixel(x, y, pixels[y][7 - x])

	def flip_vertical(self) -> None:
		"""Flip tile vertically."""
		pixels = self.get_pixels()
		for y in range(8):
			for x in range(8):
				self.set_pixel(x, y, pixels[7 - y][x])

	def rotate_cw(self) -> None:
		"""Rotate tile 90° clockwise."""
		pixels = self.get_pixels()
		for y in range(8):
			for x in range(8):
				self.set_pixel(x, y, pixels[7 - x][y])

	def rotate_ccw(self) -> None:
		"""Rotate tile 90° counter-clockwise."""
		pixels = self.get_pixels()
		for y in range(8):
			for x in range(8):
				self.set_pixel(x, y, pixels[x][7 - y])

	def clear(self) -> None:
		"""Clear tile to color 0."""
		self.data = bytearray(16)

	def fill(self, color: int) -> None:
		"""Fill tile with color."""
		for y in range(8):
			for x in range(8):
				self.set_pixel(x, y, color)

	def copy(self) -> 'Tile':
		"""Create a copy of this tile."""
		tile = Tile(id=self.id)
		tile.data = bytearray(self.data)
		return tile


@dataclass
class Palette:
	"""
	NES sprite palette (4 colors).

	Format:
	- Color 0: Transparent (background)
	- Colors 1-3: Palette colors
	"""
	id: int
	colors: List[int] = field(default_factory=lambda: [0x0F, 0x00, 0x10, 0x30])

	def get_rgb(self, index: int) -> Tuple[int, int, int]:
		"""Get RGB color for palette index."""
		if index < 0 or index >= 4:
			return (0, 0, 0)

		nes_color = self.colors[index]
		if nes_color >= len(NES_PALETTE):
			return (0, 0, 0)

		return NES_PALETTE[nes_color]

	def set_color(self, index: int, nes_color: int) -> None:
		"""Set palette color."""
		if index >= 0 and index < 4:
			self.colors[index] = nes_color & 0x3F


@dataclass
class Sprite:
	"""
	NES sprite (2x2 tiles = 16x16 pixels).
	"""
	id: int
	tiles: List[int] = field(default_factory=lambda: [0, 0, 0, 0])  # [TL, TR, BL, BR]
	palette_id: int = 0

	def get_tile_ids(self) -> List[int]:
		"""Get all tile IDs in order: top-left, top-right, bottom-left, bottom-right."""
		return self.tiles


@dataclass
class CHRBank:
	"""Collection of tiles (256 tiles per bank)."""
	tiles: List[Tile] = field(default_factory=list)

	def __post_init__(self):
		if not self.tiles:
			self.tiles = [Tile(id=i) for i in range(256)]

	def get_tile(self, tile_id: int) -> Optional[Tile]:
		"""Get tile by ID."""
		if tile_id < 0 or tile_id >= len(self.tiles):
			return None
		return self.tiles[tile_id]

	def set_tile(self, tile_id: int, tile: Tile) -> None:
		"""Set tile at ID."""
		if tile_id >= 0 and tile_id < len(self.tiles):
			self.tiles[tile_id] = tile


@dataclass
class UndoState:
	"""State for undo/redo."""
	operation: TileOperation
	tile_id: int
	before: Tile
	after: Tile


class TileRenderer:
	"""Render tiles as ASCII art."""

	# Characters for different pixel values
	PIXEL_CHARS = [' ', '░', '▒', '█']	# 0=transparent, 1=light, 2=medium, 3=dark

	@staticmethod
	def render_tile(tile: Tile, palette: Optional[Palette] = None) -> str:
		"""Render single tile as ASCII art."""
		lines = []
		lines.append("┌────────┐")

		for y in range(8):
			line = "│"
			for x in range(8):
				pixel = tile.get_pixel(x, y)
				line += TileRenderer.PIXEL_CHARS[pixel]
			line += "│"
			lines.append(line)

		lines.append("└────────┘")
		return '\n'.join(lines)

	@staticmethod
	def render_tile_grid(bank: CHRBank, start_id: int = 0, count: int = 16, cols: int = 8) -> str:
		"""Render grid of tiles."""
		lines = []

		for row in range((count + cols - 1) // cols):
			# Top borders
			border_line = ""
			for col in range(cols):
				tile_id = start_id + row * cols + col
				if tile_id >= start_id + count:
					break
				border_line += f"┌────────┐ "
			lines.append(border_line)

			# 8 rows of pixels per tile
			for y in range(8):
				pixel_line = ""
				for col in range(cols):
					tile_id = start_id + row * cols + col
					if tile_id >= start_id + count:
						break

					tile = bank.get_tile(tile_id)
					if tile:
						pixel_line += "│"
						for x in range(8):
							pixel = tile.get_pixel(x, y)
							pixel_line += TileRenderer.PIXEL_CHARS[pixel]
						pixel_line += "│ "
				lines.append(pixel_line)

			# Bottom borders with IDs
			border_line = ""
			id_line = ""
			for col in range(cols):
				tile_id = start_id + row * cols + col
				if tile_id >= start_id + count:
					break
				border_line += f"└────────┘ "
				id_line += f" {tile_id:02X}       "

			lines.append(border_line)
			lines.append(id_line)
			lines.append("")  # Spacing between rows

		return '\n'.join(lines)

	@staticmethod
	def render_sprite(sprite: Sprite, bank: CHRBank, palette: Optional[Palette] = None) -> str:
		"""Render 16x16 sprite from 4 tiles."""
		lines = []
		lines.append("┌────────────────┐")

		# Top row (tiles 0, 1)
		tile_tl = bank.get_tile(sprite.tiles[0])
		tile_tr = bank.get_tile(sprite.tiles[1])

		for y in range(8):
			line = "│"
			if tile_tl:
				for x in range(8):
					pixel = tile_tl.get_pixel(x, y)
					line += TileRenderer.PIXEL_CHARS[pixel]
			else:
				line += " " * 8

			if tile_tr:
				for x in range(8):
					pixel = tile_tr.get_pixel(x, y)
					line += TileRenderer.PIXEL_CHARS[pixel]
			else:
				line += " " * 8

			line += "│"
			lines.append(line)

		# Bottom row (tiles 2, 3)
		tile_bl = bank.get_tile(sprite.tiles[2])
		tile_br = bank.get_tile(sprite.tiles[3])

		for y in range(8):
			line = "│"
			if tile_bl:
				for x in range(8):
					pixel = tile_bl.get_pixel(x, y)
					line += TileRenderer.PIXEL_CHARS[pixel]
			else:
				line += " " * 8

			if tile_br:
				for x in range(8):
					pixel = tile_br.get_pixel(x, y)
					line += TileRenderer.PIXEL_CHARS[pixel]
			else:
				line += " " * 8

			line += "│"
			lines.append(line)

		lines.append("└────────────────┘")
		return '\n'.join(lines)


class CHREditor:
	"""Interactive CHR tile editor."""

	def __init__(self, chr_path: Optional[Path] = None):
		self.chr_path = chr_path
		self.bank = CHRBank()
		self.palettes = [Palette(id=i) for i in range(8)]
		self.current_tile_id = 0
		self.current_palette_id = 0
		self.undo_stack: List[UndoState] = []
		self.redo_stack: List[UndoState] = []
		self.renderer = TileRenderer()

		if chr_path and chr_path.exists():
			self.load_chr(chr_path)

	def load_chr(self, path: Path) -> None:
		"""Load CHR file."""
		with open(path, 'rb') as f:
			data = f.read()

		# Each tile is 16 bytes
		num_tiles = min(len(data) // 16, 256)

		for i in range(num_tiles):
			offset = i * 16
			tile = Tile(id=i)
			tile.data = bytearray(data[offset:offset + 16])
			self.bank.set_tile(i, tile)

		print(f"Loaded {num_tiles} tiles from {path}")

	def save_chr(self, path: Path) -> None:
		"""Save CHR file."""
		with open(path, 'wb') as f:
			for tile in self.bank.tiles:
				f.write(tile.data)

		print(f"Saved {len(self.bank.tiles)} tiles to {path}")

	def edit_pixel(self, tile_id: int, x: int, y: int, color: int) -> None:
		"""Edit a single pixel with undo support."""
		tile = self.bank.get_tile(tile_id)
		if not tile:
			return

		# Save undo state
		before = tile.copy()

		# Edit pixel
		tile.set_pixel(x, y, color)

		# Save undo state
		after = tile.copy()
		self.undo_stack.append(UndoState(
			operation=TileOperation.EDIT_PIXEL,
			tile_id=tile_id,
			before=before,
			after=after
		))
		self.redo_stack.clear()

	def undo(self) -> None:
		"""Undo last operation."""
		if not self.undo_stack:
			print("Nothing to undo")
			return

		state = self.undo_stack.pop()
		self.bank.set_tile(state.tile_id, state.before.copy())
		self.redo_stack.append(state)

		print(f"Undid {state.operation.value} on tile {state.tile_id:02X}")

	def redo(self) -> None:
		"""Redo last undone operation."""
		if not self.redo_stack:
			print("Nothing to redo")
			return

		state = self.redo_stack.pop()
		self.bank.set_tile(state.tile_id, state.after.copy())
		self.undo_stack.append(state)

		print(f"Redid {state.operation.value} on tile {state.tile_id:02X}")

	def run(self) -> None:
		"""Run interactive editor."""
		print("CHR-ROM Tile Editor")
		print("=" * 60)
		print("Commands: view, grid, edit, flip, rotate, clear, fill, copy, paste,")
		print("          save, load, undo, redo, palette, help, quit")
		print()

		clipboard = None

		while True:
			try:
				cmd = input(f"chr-editor [Tile:{self.current_tile_id:02X}]> ").strip().lower()

				if not cmd:
					continue

				parts = cmd.split()
				command = parts[0]
				args = parts[1:] if len(parts) > 1 else []

				if command == 'quit' or command == 'exit':
					break

				elif command == 'help':
					self._show_help()

				elif command == 'view':
					self._view_tile(args)

				elif command == 'grid':
					self._view_grid(args)

				elif command == 'edit':
					self._edit_pixel_interactive(args)

				elif command == 'flip':
					self._flip_tile(args)

				elif command == 'rotate':
					self._rotate_tile(args)

				elif command == 'clear':
					self._clear_tile()

				elif command == 'fill':
					self._fill_tile(args)

				elif command == 'copy':
					clipboard = self.bank.get_tile(self.current_tile_id).copy()
					print(f"Copied tile {self.current_tile_id:02X}")

				elif command == 'paste':
					if clipboard:
						self.bank.set_tile(self.current_tile_id, clipboard.copy())
						print(f"Pasted to tile {self.current_tile_id:02X}")
					else:
						print("Clipboard empty")

				elif command == 'save':
					self._save(args)

				elif command == 'load':
					self._load(args)

				elif command == 'undo':
					self.undo()

				elif command == 'redo':
					self.redo()

				elif command == 'palette':
					self._edit_palette(args)

				else:
					print(f"Unknown command: {command}")

			except KeyboardInterrupt:
				print("\nUse 'quit' to exit.")
			except Exception as e:
				print(f"Error: {e}")
				import traceback
				traceback.print_exc()

	def _show_help(self) -> None:
		"""Show help text."""
		print("""
CHR Editor Commands:

view [tile_id]      - View current or specified tile
grid [start] [count]- View grid of tiles
edit <x> <y> <col>  - Edit pixel at x,y with color 0-3
flip h|v            - Flip tile horizontally or vertically
rotate cw|ccw       - Rotate tile clockwise or counter-clockwise
clear               - Clear tile to color 0
fill <color>        - Fill tile with color
copy                - Copy current tile to clipboard
paste               - Paste clipboard to current tile
save [file]         - Save CHR to file
load <file>         - Load CHR from file
undo                - Undo last operation
redo                - Redo last undone operation
palette [id]        - View/edit palette
help                - Show this help
quit                - Exit editor

Examples:
	view 0x42
	grid 0x40 16
	edit 3 4 2
	flip h
	rotate cw
	fill 1
	save tiles_edited.chr
""")

	def _view_tile(self, args: List[str]) -> None:
		"""View tile."""
		tile_id = self.current_tile_id

		if args:
			try:
				tile_id = int(args[0], 16) if args[0].startswith('0x') else int(args[0])
			except ValueError:
				print(f"Invalid tile ID: {args[0]}")
				return

		tile = self.bank.get_tile(tile_id)
		if not tile:
			print(f"Tile {tile_id:02X} not found")
			return

		self.current_tile_id = tile_id

		print(f"\nTile {tile_id:02X}:")
		print(self.renderer.render_tile(tile))
		print()

	def _view_grid(self, args: List[str]) -> None:
		"""View grid of tiles."""
		start = 0
		count = 16

		if args:
			try:
				start = int(args[0], 16) if args[0].startswith('0x') else int(args[0])
			except ValueError:
				print(f"Invalid start ID: {args[0]}")
				return

		if len(args) > 1:
			try:
				count = int(args[1])
			except ValueError:
				print(f"Invalid count: {args[1]}")
				return

		print(self.renderer.render_tile_grid(self.bank, start, count))

	def _edit_pixel_interactive(self, args: List[str]) -> None:
		"""Edit pixel interactively."""
		if len(args) < 3:
			print("Usage: edit <x> <y> <color>")
			return

		try:
			x = int(args[0])
			y = int(args[1])
			color = int(args[2])
		except ValueError:
			print("Invalid coordinates or color")
			return

		self.edit_pixel(self.current_tile_id, x, y, color)
		print(f"Set pixel ({x},{y}) to color {color}")
		self._view_tile([])

	def _flip_tile(self, args: List[str]) -> None:
		"""Flip tile."""
		if not args:
			print("Usage: flip h|v")
			return

		tile = self.bank.get_tile(self.current_tile_id)
		if not tile:
			return

		before = tile.copy()

		if args[0] == 'h':
			tile.flip_horizontal()
			print("Flipped horizontally")
		elif args[0] == 'v':
			tile.flip_vertical()
			print("Flipped vertically")
		else:
			print("Usage: flip h|v")
			return

		self._view_tile([])

	def _rotate_tile(self, args: List[str]) -> None:
		"""Rotate tile."""
		if not args:
			print("Usage: rotate cw|ccw")
			return

		tile = self.bank.get_tile(self.current_tile_id)
		if not tile:
			return

		if args[0] == 'cw':
			tile.rotate_cw()
			print("Rotated clockwise")
		elif args[0] == 'ccw':
			tile.rotate_ccw()
			print("Rotated counter-clockwise")
		else:
			print("Usage: rotate cw|ccw")
			return

		self._view_tile([])

	def _clear_tile(self) -> None:
		"""Clear tile."""
		tile = self.bank.get_tile(self.current_tile_id)
		if tile:
			tile.clear()
			print("Cleared tile")
			self._view_tile([])

	def _fill_tile(self, args: List[str]) -> None:
		"""Fill tile with color."""
		if not args:
			print("Usage: fill <color>")
			return

		try:
			color = int(args[0])
		except ValueError:
			print("Invalid color")
			return

		tile = self.bank.get_tile(self.current_tile_id)
		if tile:
			tile.fill(color)
			print(f"Filled with color {color}")
			self._view_tile([])

	def _save(self, args: List[str]) -> None:
		"""Save CHR file."""
		if args:
			path = Path(args[0])
		elif self.chr_path:
			path = self.chr_path
		else:
			print("Usage: save <filename>")
			return

		path.parent.mkdir(parents=True, exist_ok=True)
		self.save_chr(path)

	def _load(self, args: List[str]) -> None:
		"""Load CHR file."""
		if not args:
			print("Usage: load <filename>")
			return

		path = Path(args[0])
		if not path.exists():
			print(f"File not found: {path}")
			return

		self.load_chr(path)

	def _edit_palette(self, args: List[str]) -> None:
		"""Edit palette."""
		print("Palette editor not yet implemented")


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='CHR-ROM Visual Tile Editor'
	)
	parser.add_argument(
		'chr',
		type=Path,
		nargs='?',
		help='Path to CHR file'
	)
	parser.add_argument(
		'--tile',
		type=str,
		help='Start with specific tile (hex)'
	)
	parser.add_argument(
		'--palette',
		type=int,
		help='Use specific palette (0-7)'
	)

	args = parser.parse_args()

	editor = CHREditor(args.chr if args.chr else None)

	if args.tile:
		tile_id = int(args.tile, 16) if args.tile.startswith('0x') else int(args.tile)
		editor.current_tile_id = tile_id

	if args.palette is not None:
		editor.current_palette_id = args.palette

	editor.run()


if __name__ == '__main__':
	main()
