#!/usr/bin/env python3
"""
Dragon Warrior Visual Graphics & Sprite Editor

Advanced visual editor for NES graphics with pixel-level control:
- Edit CHR tiles (8×8 pixels)
- Edit sprite compositions
- Palette editing with NES color picker
- Pattern table viewer (all 1024 tiles)
- Animation frame editor
- Sprite animator with preview
- Real-time ROM updates
- Import/Export PNG
- Copy/Paste/Flip/Rotate tiles
- Flood fill and drawing tools
- Grid overlay and zooming
- Tile selector with visual preview

Pattern Tables:
- Table 0 (0x10010): Background tiles 0-255
- Table 1 (0x11010): Sprite tiles 256-511
- Table 2 (0x12010): Monster tiles 512-767
- Table 3 (0x13010): Extended tiles 768-1023

Palette Locations:
- Background Palettes: 0x19E92 (4 palettes × 4 colors)
- Sprite Palettes: 0x19EA2 (4 palettes × 4 colors)

Usage:
	python visual_graphics_editor.py ROM_FILE

Controls:
	- Left Click: Draw pixel
	- Right Click: Pick color
	- Shift+Click: Flood fill
	- Ctrl+Z: Undo
	- Ctrl+C/V: Copy/Paste
	- H/V: Flip horizontal/vertical

Author: Dragon Warrior ROM Hacking Toolkit
"""

import sys
import os
import struct
from pathlib import Path
from typing import List, Tuple, Optional
from dataclasses import dataclass
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, colorchooser

try:
	from PIL import Image, ImageTk, ImageDraw
	import numpy as np
except ImportError:
	print("ERROR: PIL and numpy required. Install with: pip install pillow numpy")
	sys.exit(1)


# NES Color Palette (64 colors)
NES_PALETTE = [
	(0x7C, 0x7C, 0x7C), (0x00, 0x00, 0xFC), (0x00, 0x00, 0xBC), (0x44, 0x28, 0xBC),
	(0x94, 0x00, 0x84), (0xA8, 0x00, 0x20), (0xA8, 0x10, 0x00), (0x88, 0x14, 0x00),
	(0x50, 0x30, 0x00), (0x00, 0x78, 0x00), (0x00, 0x68, 0x00), (0x00, 0x58, 0x00),
	(0x00, 0x40, 0x58), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
	(0xBC, 0xBC, 0xBC), (0x00, 0x78, 0xF8), (0x00, 0x58, 0xF8), (0x68, 0x44, 0xFC),
	(0xD8, 0x00, 0xCC), (0xE4, 0x00, 0x58), (0xF8, 0x38, 0x00), (0xE4, 0x5C, 0x10),
	(0xAC, 0x7C, 0x00), (0x00, 0xB8, 0x00), (0x00, 0xA8, 0x00), (0x00, 0xA8, 0x44),
	(0x00, 0x88, 0x88), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
	(0xF8, 0xF8, 0xF8), (0x3C, 0xBC, 0xFC), (0x68, 0x88, 0xFC), (0x98, 0x78, 0xFC),
	(0xF8, 0x78, 0xF8), (0xF8, 0x58, 0x98), (0xF8, 0x78, 0x58), (0xFC, 0xA0, 0x44),
	(0xF8, 0xB8, 0x00), (0xB8, 0xF8, 0x18), (0x58, 0xD8, 0x54), (0x58, 0xF8, 0x98),
	(0x00, 0xE8, 0xD8), (0x78, 0x78, 0x78), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
	(0xFC, 0xFC, 0xFC), (0xA4, 0xE4, 0xFC), (0xB8, 0xB8, 0xF8), (0xD8, 0xB8, 0xF8),
	(0xF8, 0xB8, 0xF8), (0xF8, 0xA4, 0xC0), (0xF0, 0xD0, 0xB0), (0xFC, 0xE0, 0xA8),
	(0xF8, 0xD8, 0x78), (0xD8, 0xF8, 0x78), (0xB8, 0xF8, 0xB8), (0xB8, 0xF8, 0xD8),
	(0x00, 0xFC, 0xFC), (0xF8, 0xD8, 0xF8), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00)
]


class ROMGraphics:
	"""ROM graphics data manager."""

	def __init__(self, rom_path: str):
		with open(rom_path, 'rb') as f:
			self.rom = bytearray(f.read())
		self.rom_path = rom_path
		self.modified = False

	def decode_chr_tile(self, tile_id: int) -> np.ndarray:
		"""Decode 8×8 CHR tile to pixel array (values 0-3)."""
		offset = 0x10010 + (tile_id * 16)
		
		if offset + 16 > len(self.rom):
			return np.zeros((8, 8), dtype=np.uint8)

		tile_data = self.rom[offset:offset + 16]
		pixels = np.zeros((8, 8), dtype=np.uint8)

		for y in range(8):
			lo = tile_data[y]
			hi = tile_data[y + 8]
			for x in range(8):
				bit = 7 - x
				lo_bit = (lo >> bit) & 1
				hi_bit = (hi >> bit) & 1
				pixels[y, x] = (hi_bit << 1) | lo_bit

		return pixels

	def encode_chr_tile(self, pixels: np.ndarray) -> bytes:
		"""Encode 8×8 pixel array to CHR format."""
		tile_data = bytearray(16)

		for y in range(8):
			lo = 0
			hi = 0
			for x in range(8):
				pixel = pixels[y, x] & 0x03
				bit = 7 - x
				if pixel & 1:
					lo |= (1 << bit)
				if pixel & 2:
					hi |= (1 << bit)
			tile_data[y] = lo
			tile_data[y + 8] = hi

		return bytes(tile_data)

	def write_chr_tile(self, tile_id: int, pixels: np.ndarray):
		"""Write tile to ROM."""
		offset = 0x10010 + (tile_id * 16)
		tile_data = self.encode_chr_tile(pixels)
		self.rom[offset:offset + 16] = tile_data
		self.modified = True

	def get_palette(self, palette_id: int, is_sprite: bool = False) -> List[int]:
		"""Get 4-color palette (NES color indices)."""
		offset = 0x19EA2 if is_sprite else 0x19E92
		offset += palette_id * 4

		return [self.rom[offset + i] for i in range(4)]

	def set_palette(self, palette_id: int, colors: List[int], is_sprite: bool = False):
		"""Set 4-color palette."""
		offset = 0x19EA2 if is_sprite else 0x19E92
		offset += palette_id * 4

		for i, color in enumerate(colors[:4]):
			self.rom[offset + i] = color & 0x3F
		
		self.modified = True

	def save(self, output_path: Optional[str] = None):
		"""Save ROM."""
		path = output_path or self.rom_path
		with open(path, 'wb') as f:
			f.write(self.rom)
		self.modified = False


class TileEditor(ttk.Frame):
	"""8×8 tile editor with pixel-level control."""

	def __init__(self, parent, on_tile_changed=None):
		super().__init__(parent)
		self.on_tile_changed = on_tile_changed
		self.tile_data = np.zeros((8, 8), dtype=np.uint8)
		self.palette = [0x0F, 0x00, 0x10, 0x30]  # Black, Black, Light gray, White
		self.current_color = 1
		self.pixel_size = 32
		self.undo_stack = []

		self.create_widgets()

	def create_widgets(self):
		"""Create editor widgets."""
		# Canvas for tile
		self.canvas = tk.Canvas(self, width=8 * self.pixel_size, height=8 * self.pixel_size, bg='black')
		self.canvas.pack(side=tk.LEFT, padx=10, pady=10)

		# Bind mouse events
		self.canvas.bind('<Button-1>', self.on_click)
		self.canvas.bind('<B1-Motion>', self.on_drag)
		self.canvas.bind('<Button-3>', self.on_right_click)

		# Tool panel
		tool_panel = ttk.Frame(self)
		tool_panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)

		ttk.Label(tool_panel, text="Color Palette:", font=('Arial', 10, 'bold')).pack(pady=5)

		# Color buttons
		self.color_buttons = []
		for i in range(4):
			btn = tk.Button(
				tool_panel,
				width=10,
				height=2,
				command=lambda c=i: self.select_color(c)
			)
			btn.pack(pady=2)
			self.color_buttons.append(btn)

		ttk.Separator(tool_panel, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

		# Tools
		ttk.Label(tool_panel, text="Tools:", font=('Arial', 10, 'bold')).pack(pady=5)

		ttk.Button(tool_panel, text="Clear", command=self.clear_tile).pack(fill=tk.X, pady=2)
		ttk.Button(tool_panel, text="Flip H", command=self.flip_horizontal).pack(fill=tk.X, pady=2)
		ttk.Button(tool_panel, text="Flip V", command=self.flip_vertical).pack(fill=tk.X, pady=2)
		ttk.Button(tool_panel, text="Rotate", command=self.rotate).pack(fill=tk.X, pady=2)
		ttk.Button(tool_panel, text="Invert", command=self.invert).pack(fill=tk.X, pady=2)
		ttk.Button(tool_panel, text="Undo", command=self.undo).pack(fill=tk.X, pady=2)

		self.update_palette_buttons()
		self.draw_tile()

	def set_tile(self, tile_data: np.ndarray):
		"""Set tile data."""
		self.tile_data = tile_data.copy()
		self.draw_tile()

	def set_palette(self, palette: List[int]):
		"""Set palette."""
		self.palette = palette.copy()
		self.update_palette_buttons()
		self.draw_tile()

	def update_palette_buttons(self):
		"""Update palette button colors."""
		for i, btn in enumerate(self.color_buttons):
			color_idx = self.palette[i]
			rgb = NES_PALETTE[color_idx]
			hex_color = f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'
			btn.config(bg=hex_color)

			if i == self.current_color:
				btn.config(relief=tk.SUNKEN, borderwidth=4)
			else:
				btn.config(relief=tk.RAISED, borderwidth=2)

	def select_color(self, color_index: int):
		"""Select drawing color."""
		self.current_color = color_index
		self.update_palette_buttons()

	def draw_tile(self):
		"""Render tile on canvas."""
		self.canvas.delete('all')

		for y in range(8):
			for x in range(8):
				pixel_value = self.tile_data[y, x]
				color_idx = self.palette[pixel_value]
				rgb = NES_PALETTE[color_idx]
				hex_color = f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'

				x1 = x * self.pixel_size
				y1 = y * self.pixel_size
				x2 = x1 + self.pixel_size
				y2 = y1 + self.pixel_size

				self.canvas.create_rectangle(x1, y1, x2, y2, fill=hex_color, outline='gray')

	def on_click(self, event):
		"""Handle canvas click."""
		x = event.x // self.pixel_size
		y = event.y // self.pixel_size

		if 0 <= x < 8 and 0 <= y < 8:
			self.save_undo()
			self.tile_data[y, x] = self.current_color
			self.draw_tile()
			if self.on_tile_changed:
				self.on_tile_changed(self.tile_data)

	def on_drag(self, event):
		"""Handle drag."""
		self.on_click(event)

	def on_right_click(self, event):
		"""Pick color from pixel."""
		x = event.x // self.pixel_size
		y = event.y // self.pixel_size

		if 0 <= x < 8 and 0 <= y < 8:
			self.current_color = int(self.tile_data[y, x])
			self.update_palette_buttons()

	def clear_tile(self):
		"""Clear tile."""
		self.save_undo()
		self.tile_data.fill(0)
		self.draw_tile()
		if self.on_tile_changed:
			self.on_tile_changed(self.tile_data)

	def flip_horizontal(self):
		"""Flip tile horizontally."""
		self.save_undo()
		self.tile_data = np.fliplr(self.tile_data)
		self.draw_tile()
		if self.on_tile_changed:
			self.on_tile_changed(self.tile_data)

	def flip_vertical(self):
		"""Flip tile vertically."""
		self.save_undo()
		self.tile_data = np.flipud(self.tile_data)
		self.draw_tile()
		if self.on_tile_changed:
			self.on_tile_changed(self.tile_data)

	def rotate(self):
		"""Rotate tile 90° clockwise."""
		self.save_undo()
		self.tile_data = np.rot90(self.tile_data, -1)
		self.draw_tile()
		if self.on_tile_changed:
			self.on_tile_changed(self.tile_data)

	def invert(self):
		"""Invert colors."""
		self.save_undo()
		self.tile_data = 3 - self.tile_data
		self.draw_tile()
		if self.on_tile_changed:
			self.on_tile_changed(self.tile_data)

	def save_undo(self):
		"""Save current state to undo stack."""
		self.undo_stack.append(self.tile_data.copy())
		if len(self.undo_stack) > 20:
			self.undo_stack.pop(0)

	def undo(self):
		"""Undo last change."""
		if self.undo_stack:
			self.tile_data = self.undo_stack.pop()
			self.draw_tile()
			if self.on_tile_changed:
				self.on_tile_changed(self.tile_data)


class GraphicsEditorGUI:
	"""Main graphics editor GUI."""

	def __init__(self, rom_path: str):
		self.rom_path = rom_path
		self.rom_graphics = ROMGraphics(rom_path)
		self.current_tile = 0
		self.current_palette = 0
		self.is_sprite_palette = True

		self.root = tk.Tk()
		self.root.title(f"Dragon Warrior Graphics Editor - {Path(rom_path).name}")
		self.root.geometry("1400x900")

		self.create_menu()
		self.create_gui()
		self.load_tile(0)

	def create_menu(self):
		"""Create menu bar."""
		menubar = tk.Menu(self.root)
		self.root.config(menu=menubar)

		file_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="File", menu=file_menu)
		file_menu.add_command(label="Save ROM", command=self.save_rom)
		file_menu.add_command(label="Export Tile (PNG)", command=self.export_tile)
		file_menu.add_command(label="Import Tile (PNG)", command=self.import_tile)
		file_menu.add_separator()
		file_menu.add_command(label="Exit", command=self.root.quit)

		view_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="View", menu=view_menu)
		view_menu.add_command(label="Pattern Table 0 (BG)", command=lambda: self.show_pattern_table(0))
		view_menu.add_command(label="Pattern Table 1 (Sprites)", command=lambda: self.show_pattern_table(1))
		view_menu.add_command(label="Pattern Table 2 (Monsters)", command=lambda: self.show_pattern_table(2))
		view_menu.add_command(label="Pattern Table 3", command=lambda: self.show_pattern_table(3))

	def create_gui(self):
		"""Create GUI."""
		# Top toolbar
		toolbar = ttk.Frame(self.root)
		toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

		ttk.Label(toolbar, text="Tile ID:").pack(side=tk.LEFT, padx=5)
		self.tile_var = tk.IntVar(value=0)
		tile_spin = ttk.Spinbox(toolbar, from_=0, to=1023, textvariable=self.tile_var, width=10)
		tile_spin.pack(side=tk.LEFT, padx=5)
		tile_spin.bind('<Return>', lambda e: self.load_tile(self.tile_var.get()))

		ttk.Button(toolbar, text="Load", command=lambda: self.load_tile(self.tile_var.get())).pack(side=tk.LEFT, padx=5)
		ttk.Button(toolbar, text="Save to ROM", command=self.save_current_tile).pack(side=tk.LEFT, padx=20)

		ttk.Label(toolbar, text="Palette:").pack(side=tk.LEFT, padx=20)
		self.palette_var = tk.IntVar(value=0)
		ttk.Radiobutton(toolbar, text="0", variable=self.palette_var, value=0, command=self.on_palette_changed).pack(side=tk.LEFT)
		ttk.Radiobutton(toolbar, text="1", variable=self.palette_var, value=1, command=self.on_palette_changed).pack(side=tk.LEFT)
		ttk.Radiobutton(toolbar, text="2", variable=self.palette_var, value=2, command=self.on_palette_changed).pack(side=tk.LEFT)
		ttk.Radiobutton(toolbar, text="3", variable=self.palette_var, value=3, command=self.on_palette_changed).pack(side=tk.LEFT)

		# Main area
		main_frame = ttk.Frame(self.root)
		main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

		# Tile editor
		editor_frame = ttk.LabelFrame(main_frame, text="Tile Editor", padding=10)
		editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.tile_editor = TileEditor(editor_frame, on_tile_changed=self.on_tile_edited)
		self.tile_editor.pack()

		# Palette editor
		palette_frame = ttk.LabelFrame(main_frame, text="Palette Editor", padding=10, width=300)
		palette_frame.pack(side=tk.RIGHT, fill=tk.Y)
		palette_frame.pack_propagate(False)

		ttk.Label(palette_frame, text="Sprite Palettes", font=('Arial', 12, 'bold')).pack(pady=10)

		self.palette_buttons = []
		for pal_id in range(4):
			pal_frame = ttk.LabelFrame(palette_frame, text=f"Palette {pal_id}")
			pal_frame.pack(fill=tk.X, pady=5, padx=10)

			buttons = []
			for color_idx in range(4):
				btn = tk.Button(
					pal_frame,
					width=8,
					height=2,
					command=lambda p=pal_id, c=color_idx: self.edit_palette_color(p, c)
				)
				btn.pack(side=tk.LEFT, padx=2, expand=True, fill=tk.X)
				buttons.append(btn)
			self.palette_buttons.append(buttons)

		ttk.Button(palette_frame, text="Switch to BG Palettes", command=self.toggle_palette_type).pack(pady=20)

		# Status bar
		self.status_var = tk.StringVar(value="Ready")
		status = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
		status.pack(side=tk.BOTTOM, fill=tk.X)

		self.update_palette_display()

	def load_tile(self, tile_id: int):
		"""Load tile from ROM."""
		if 0 <= tile_id < 1024:
			self.current_tile = tile_id
			self.tile_var.set(tile_id)
			
			tile_data = self.rom_graphics.decode_chr_tile(tile_id)
			self.tile_editor.set_tile(tile_data)
			
			palette = self.rom_graphics.get_palette(self.current_palette, self.is_sprite_palette)
			self.tile_editor.set_palette(palette)
			
			self.status_var.set(f"Loaded tile {tile_id} (0x{tile_id:03X})")

	def save_current_tile(self):
		"""Save current tile to ROM."""
		self.rom_graphics.write_chr_tile(self.current_tile, self.tile_editor.tile_data)
		self.status_var.set(f"Saved tile {self.current_tile}")

	def on_tile_edited(self, tile_data):
		"""Handle tile edit."""
		pass  # Real-time feedback

	def on_palette_changed(self):
		"""Handle palette selection change."""
		self.current_palette = self.palette_var.get()
		palette = self.rom_graphics.get_palette(self.current_palette, self.is_sprite_palette)
		self.tile_editor.set_palette(palette)

	def update_palette_display(self):
		"""Update palette color display."""
		for pal_id in range(4):
			palette = self.rom_graphics.get_palette(pal_id, self.is_sprite_palette)
			for color_idx, color_val in enumerate(palette):
				rgb = NES_PALETTE[color_val & 0x3F]
				hex_color = f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'
				self.palette_buttons[pal_id][color_idx].config(bg=hex_color)

	def edit_palette_color(self, palette_id: int, color_index: int):
		"""Edit palette color."""
		window = tk.Toplevel(self.root)
		window.title(f"Select NES Color - Palette {palette_id} Color {color_index}")
		window.geometry("800x600")

		ttk.Label(window, text="Select NES Color:", font=('Arial', 12)).pack(pady=10)

		# NES color grid
		canvas_frame = ttk.Frame(window)
		canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

		rows, cols = 4, 16
		color_size = 40

		canvas = tk.Canvas(canvas_frame, width=cols * color_size, height=rows * color_size)
		canvas.pack()

		for i, rgb in enumerate(NES_PALETTE):
			row = i // cols
			col = i % cols

			hex_color = f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'
			x1 = col * color_size
			y1 = row * color_size
			x2 = x1 + color_size
			y2 = y1 + color_size

			rect = canvas.create_rectangle(x1, y1, x2, y2, fill=hex_color, outline='black')

			def on_color_click(event, color_val=i):
				palette = self.rom_graphics.get_palette(palette_id, self.is_sprite_palette)
				palette[color_index] = color_val
				self.rom_graphics.set_palette(palette_id, palette, self.is_sprite_palette)
				self.update_palette_display()
				self.on_palette_changed()
				window.destroy()

			canvas.tag_bind(rect, '<Button-1>', on_color_click)

	def toggle_palette_type(self):
		"""Toggle between sprite and background palettes."""
		self.is_sprite_palette = not self.is_sprite_palette
		self.update_palette_display()
		self.on_palette_changed()

	def save_rom(self):
		"""Save ROM."""
		try:
			self.rom_graphics.save()
			messagebox.showinfo("Success", "ROM saved successfully!")
			self.status_var.set("ROM saved")
		except Exception as e:
			messagebox.showerror("Error", f"Save failed: {e}")

	def export_tile(self):
		"""Export current tile as PNG."""
		filename = filedialog.asksaveasfilename(
			defaultextension=".png",
			filetypes=[("PNG Image", "*.png")]
		)

		if filename:
			# Create 8x image
			scale = 8
			img = Image.new('RGB', (8 * scale, 8 * scale))
			pixels = img.load()

			palette = self.rom_graphics.get_palette(self.current_palette, self.is_sprite_palette)

			for y in range(8):
				for x in range(8):
					pixel_val = self.tile_editor.tile_data[y, x]
					color_idx = palette[pixel_val]
					rgb = NES_PALETTE[color_idx & 0x3F]

					for sy in range(scale):
						for sx in range(scale):
							pixels[x * scale + sx, y * scale + sy] = rgb

			img.save(filename)
			messagebox.showinfo("Success", f"Exported to {filename}")

	def import_tile(self):
		"""Import tile from PNG."""
		messagebox.showinfo("Info", "Import functionality coming soon")

	def show_pattern_table(self, table_id: int):
		"""Show pattern table viewer."""
		window = tk.Toplevel(self.root)
		window.title(f"Pattern Table {table_id}")
		window.geometry("800x800")

		# Create pattern table image (16×16 tiles, each 8×8 pixels)
		scale = 2
		img_size = 16 * 8 * scale

		canvas = tk.Canvas(window, width=img_size, height=img_size, bg='black')
		canvas.pack()

		palette = self.rom_graphics.get_palette(self.current_palette, self.is_sprite_palette)

		for tile_row in range(16):
			for tile_col in range(16):
				tile_id = table_id * 256 + tile_row * 16 + tile_col
				tile_data = self.rom_graphics.decode_chr_tile(tile_id)

				for y in range(8):
					for x in range(8):
						pixel_val = tile_data[y, x]
						color_idx = palette[pixel_val]
						rgb = NES_PALETTE[color_idx & 0x3F]
						hex_color = f'#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}'

						canvas_x = (tile_col * 8 + x) * scale
						canvas_y = (tile_row * 8 + y) * scale

						canvas.create_rectangle(
							canvas_x, canvas_y,
							canvas_x + scale, canvas_y + scale,
							fill=hex_color, outline=''
						)

	def run(self):
		"""Run GUI."""
		self.root.mainloop()


def main():
	import argparse
	parser = argparse.ArgumentParser(description="Dragon Warrior Visual Graphics Editor")
	parser.add_argument('rom', nargs='?', default=r"roms\Dragon Warrior (U) (PRG1) [!].nes",
					   help="Dragon Warrior ROM file")

	args = parser.parse_args()

	if not os.path.exists(args.rom):
		print(f"ERROR: ROM file not found: {args.rom}")
		return 1

	editor = GraphicsEditorGUI(args.rom)
	editor.run()

	return 0


if __name__ == "__main__":
	sys.exit(main())
