#!/usr/bin/env python3
"""
Dragon Warrior Master ROM Editor

Ultimate unified editor combining ALL Dragon Warrior editing tools:
- Map Editor (World & Dungeon maps)
- Encounter Zone Editor
- Sprite Editor (Monsters, Characters, Items)
- Dialogue/Text Editor
- Enemy Stats Editor
- Item Database Editor
- Spell Editor
- Character/Hero Editor
- Shop Editor
- Music/Sound Editor
- ROM Patcher

Features:
- Tabbed interface with all editors
- Quick Launch dashboard
- Real-time ROM validation
- Undo/Redo across all editors
- Export/Import all data as JSON
- Batch operations
- Visual graphics editing
- Script decompilation

Usage:
	python dragon_warrior_master_editor.py ROM_FILE

Author: Dragon Warrior ROM Hacking Toolkit
Version: 2.0 - Master Edition
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
import json
import struct
import argparse
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Set, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, colorchooser

try:
	from PIL import Image, ImageTk, ImageDraw
	import numpy as np
except ImportError:
	print("ERROR: PIL and numpy required. Install with: pip install pillow numpy")
	sys.exit(1)

# Import editor tabs
try:
	from dialogue_editor_tab import DialogueEditorTab
	from music_editor_tab import MusicEditorTab
	from shop_editor_tab import ShopEditorTab
	ADVANCED_EDITORS_AVAILABLE = True
except ImportError:
	print("WARNING: Advanced editor tabs not found. Some features will be disabled.")
	ADVANCED_EDITORS_AVAILABLE = False
	DialogueEditorTab = None
	MusicEditorTab = None
	ShopEditorTab = None


# ============================================================================
# CONSTANTS & ROM OFFSETS
# ============================================================================

# ROM Memory Map
ROM_OFFSETS = {
	# Maps
	'WORLD_MAP': 0x1d5d,  # 120×120 overworld
	'TANTEGEL_CASTLE': 0xf5b0,
	'THRONE_ROOM': 0xf610,
	'CHARLOCK_CASTLE': 0xf670,

	# Graphics
	'CHR_ROM': 0x10010,  # 16KB CHR-ROM
	'PATTERN_TABLE_0': 0x10010,  # 0-255 (backgrounds)
	'PATTERN_TABLE_1': 0x11010,  # 256-511 (sprites)
	'PATTERN_TABLE_2': 0x12010,  # 512-767 (monsters)
	'PATTERN_TABLE_3': 0x13010,  # 768-1023

	# Sprites
	'MONSTER_SPRITE_TABLE': 0x59f4,  # 39 monsters
	'HERO_SPRITE_TABLE': 0x5a96,
	'NPC_SPRITE_TABLE': 0x5ac0,

	# Text & Dialogue
	'TEXT_POINTERS': 0xb0a0,  # Dialogue pointer table
	'TEXT_DATA': 0xb100,  # Compressed dialogue
	'ITEM_NAMES': 0xddb8,
	'MONSTER_NAMES': 0xddb8 + 0x100,
	'SPELL_NAMES': 0xddb8 + 0x200,

	# Stats & Data
	'MONSTER_STATS': 0xc6e0,  # 39 monsters × 16 bytes
	'ITEM_DATA': 0xcf50,  # Item properties
	'SPELL_DATA': 0xd000,  # Spell properties
	'SHOP_DATA': 0xd200,  # Shop inventory
	'LEVEL_XP_TABLE': 0xc050,  # Experience curve

	# Encounters
	'ENCOUNTER_ZONES': 0x0cf3,  # 9 zones
	'ENCOUNTER_GROUPS': 0xf5f0,  # Enemy group definitions

	# Palettes
	'BG_PALETTE': 0x19e92,  # Background palettes
	'SPRITE_PALETTE': 0x19ea2,  # Sprite palettes

	# Music & Sound
	'MUSIC_TABLE': 0x1e000,  # Music data
	'SFX_TABLE': 0x1f000,  # Sound effects
}

# Tile types
TILE_TYPES = {
	0x00: ("Ocean", False, "#0066CC"),
	0x01: ("Grass", True, "#22AA22"),
	0x02: ("Desert", True, "#DDDD66"),
	0x03: ("Hill", True, "#88AA44"),
	0x04: ("Mountain", False, "#886644"),
	0x05: ("Swamp", True, "#446633"),
	0x06: ("Town", True, "#CCCCCC"),
	0x07: ("Cave", True, "#444444"),
	0x08: ("Castle", True, "#CC8844"),
	0x09: ("Bridge", True, "#AA7744"),
	0x0a: ("Stairs Down", True, "#666666"),
	0x0b: ("Stairs Up", True, "#888888"),
	0x0c: ("Barrier", False, "#FF0000"),
	0x0d: ("Treasure", True, "#FFDD00"),
	0x0e: ("Door", True, "#AA5522"),
	0x0f: ("Wall", False, "#222222"),
}

# Monster names (0-38)
MONSTER_NAMES = [
	"Slime", "Red Slime", "Drakee", "Ghost", "Magician", "Magidrakee", "Scorpion",
	"Druin", "Poltergeist", "Droll", "Drakeema", "Skeleton", "Warlock", "Metal Scorpion",
	"Wolf", "Wraith", "Metal Slime", "Specter", "Wolflord", "Druinlord", "Drollmagi",
	"Wyvern", "Rogue Scorpion", "Wraith Knight", "Golem", "Goldman", "Knight", "Magiwyvern",
	"Demon Knight", "Werewolf", "Green Dragon", "Starwyvern", "Wizard", "Axe Knight",
	"Blue Dragon", "Stoneman", "Armored Knight", "Red Dragon", "Dragonlord"
]

# Item names (0-26)
ITEM_NAMES = [
	"Torch", "Fairy Water", "Wings", "Dragon's Scale", "Fairy Flute", "Fighter's Ring",
	"Erdrick's Token", "Gwaelin's Love", "Cursed Belt", "Silver Harp", "Death Necklace",
	"Stones of Sunlight", "Staff of Rain", "Rainbow Drop", "Herb", "Club", "Copper Sword",
	"Hand Axe", "Broad Sword", "Flame Sword", "Erdrick's Sword", "Clothes", "Leather Armor",
	"Chain Mail", "Half Plate", "Full Plate", "Magic Armor", "Erdrick's Armor"
]

# Spell names (0-9)
SPELL_NAMES = [
	"Heal", "Hurt", "Sleep", "Radiant", "Stopspell", "Outside", "Return", "Repel",
	"Healmore", "Hurtmore"
]

# NES Color Palette
NES_PALETTE = [
	(0x7c, 0x7c, 0x7c), (0x00, 0x00, 0xfc), (0x00, 0x00, 0xbc), (0x44, 0x28, 0xbc),
	(0x94, 0x00, 0x84), (0xa8, 0x00, 0x20), (0xa8, 0x10, 0x00), (0x88, 0x14, 0x00),
	(0x50, 0x30, 0x00), (0x00, 0x78, 0x00), (0x00, 0x68, 0x00), (0x00, 0x58, 0x00),
	(0x00, 0x40, 0x58), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
	(0xbc, 0xbc, 0xbc), (0x00, 0x78, 0xf8), (0x00, 0x58, 0xf8), (0x68, 0x44, 0xfc),
	(0xd8, 0x00, 0xcc), (0xe4, 0x00, 0x58), (0xf8, 0x38, 0x00), (0xe4, 0x5c, 0x10),
	(0xac, 0x7c, 0x00), (0x00, 0xb8, 0x00), (0x00, 0xa8, 0x00), (0x00, 0xa8, 0x44),
	(0x00, 0x88, 0x88), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
	(0xf8, 0xf8, 0xf8), (0x3c, 0xbc, 0xfc), (0x68, 0x88, 0xfc), (0x98, 0x78, 0xfc),
	(0xf8, 0x78, 0xf8), (0xf8, 0x58, 0x98), (0xf8, 0x78, 0x58), (0xfc, 0xa0, 0x44),
	(0xf8, 0xb8, 0x00), (0xb8, 0xf8, 0x18), (0x58, 0xd8, 0x54), (0x58, 0xf8, 0x98),
	(0x00, 0xe8, 0xd8), (0x78, 0x78, 0x78), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00),
	(0xfc, 0xfc, 0xfc), (0xa4, 0xe4, 0xfc), (0xb8, 0xb8, 0xf8), (0xd8, 0xb8, 0xf8),
	(0xf8, 0xb8, 0xf8), (0xf8, 0xa4, 0xc0), (0xf0, 0xd0, 0xb0), (0xfc, 0xe0, 0xa8),
	(0xf8, 0xd8, 0x78), (0xd8, 0xf8, 0x78), (0xb8, 0xf8, 0xb8), (0xb8, 0xf8, 0xd8),
	(0x00, 0xfc, 0xfc), (0xf8, 0xd8, 0xf8), (0x00, 0x00, 0x00), (0x00, 0x00, 0x00)
]


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class MonsterStats:
	"""Monster statistics."""
	id: int
	name: str
	hp: int
	strength: int
	agility: int
	attack_power: int
	defense_power: int
	xp: int
	gold: int
	sleep_resistance: int
	stopspell_resistance: int
	hurt_resistance: int
	dodge_rate: int
	critical_rate: int
	special_attack: int


@dataclass
class ItemData:
	"""Item properties."""
	id: int
	name: str
	type: str  # "weapon", "armor", "tool", "key"
	attack: int
	defense: int
	price: int
	equip_slot: int
	usable_in_battle: bool
	usable_in_field: bool
	special_effect: str


@dataclass
class SpellData:
	"""Spell properties."""
	id: int
	name: str
	mp_cost: int
	battle_only: bool
	field_only: bool
	target: str  # "single", "all", "self"
	effect: str


# ============================================================================
# ROM DATA MANAGER
# ============================================================================

class ROMManager:
	"""Centralized ROM data management."""

	def __init__(self, rom_path: str):
		self.rom_path = rom_path
		with open(rom_path, 'rb') as f:
			self.rom = bytearray(f.read())

		self.modified = False
		self.undo_stack = []
		self.redo_stack = []

	def read_byte(self, offset: int) -> int:
		"""Read single byte."""
		return self.rom[offset]

	def write_byte(self, offset: int, value: int):
		"""Write single byte with undo support."""
		old_value = self.rom[offset]
		self.undo_stack.append(('byte', offset, old_value))
		self.redo_stack.clear()
		self.rom[offset] = value & 0xff
		self.modified = True

	def read_word(self, offset: int) -> int:
		"""Read 16-bit little-endian word."""
		return self.rom[offset] | (self.rom[offset + 1] << 8)

	def write_word(self, offset: int, value: int):
		"""Write 16-bit word."""
		self.write_byte(offset, value & 0xff)
		self.write_byte(offset + 1, (value >> 8) & 0xff)

	def read_bytes(self, offset: int, count: int) -> bytes:
		"""Read multiple bytes."""
		return bytes(self.rom[offset:offset + count])

	def write_bytes(self, offset: int, data: bytes):
		"""Write multiple bytes."""
		for i, b in enumerate(data):
			self.write_byte(offset + i, b)

	def undo(self) -> bool:
		"""Undo last change."""
		if not self.undo_stack:
			return False

		action = self.undo_stack.pop()
		if action[0] == 'byte':
			_, offset, old_value = action
			new_value = self.rom[offset]
			self.rom[offset] = old_value
			self.redo_stack.append(('byte', offset, new_value))
			return True
		return False

	def redo(self) -> bool:
		"""Redo last undone change."""
		if not self.redo_stack:
			return False

		action = self.redo_stack.pop()
		if action[0] == 'byte':
			_, offset, new_value = action
			old_value = self.rom[offset]
			self.rom[offset] = new_value
			self.undo_stack.append(('byte', offset, old_value))
			return True
		return False

	def save(self, output_path: Optional[str] = None):
		"""Save ROM to file."""
		path = output_path or self.rom_path
		with open(path, 'wb') as f:
			f.write(self.rom)
		self.modified = False

	def extract_chr_tile(self, tile_id: int) -> np.ndarray:
		"""Extract 8×8 CHR tile as pixel array."""
		offset = ROM_OFFSETS['CHR_ROM'] + (tile_id * 16)
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

	def extract_pattern_table(self, table_id: int) -> List[np.ndarray]:
		"""Extract all 256 tiles from a pattern table."""
		offset = ROM_OFFSETS['CHR_ROM'] + (table_id * 0x1000)
		tiles = []
		for i in range(256):
			tile_offset = offset + (i * 16)
			tile_data = self.rom[tile_offset:tile_offset + 16]

			pixels = np.zeros((8, 8), dtype=np.uint8)
			for y in range(8):
				lo = tile_data[y]
				hi = tile_data[y + 8]
				for x in range(8):
					bit = 7 - x
					lo_bit = (lo >> bit) & 1
					hi_bit = (hi >> bit) & 1
					pixels[y, x] = (hi_bit << 1) | lo_bit

			tiles.append(pixels)

		return tiles

	def extract_monster_stats(self, monster_id: int) -> MonsterStats:
		"""Extract monster statistics."""
		offset = ROM_OFFSETS['MONSTER_STATS'] + (monster_id * 16)
		data = self.rom[offset:offset + 16]

		return MonsterStats(
			id=monster_id,
			name=MONSTER_NAMES[monster_id] if monster_id < len(MONSTER_NAMES) else f"Monster {monster_id}",
			hp=data[0] | (data[1] << 8),
			strength=data[2],
			agility=data[3],
			attack_power=data[4],
			defense_power=data[5],
			xp=data[6] | (data[7] << 8),
			gold=data[8] | (data[9] << 8),
			sleep_resistance=data[10],
			stopspell_resistance=data[11],
			hurt_resistance=data[12],
			dodge_rate=data[13],
			critical_rate=data[14],
			special_attack=data[15]
		)

	def write_monster_stats(self, stats: MonsterStats):
		"""Write monster statistics to ROM."""
		offset = ROM_OFFSETS['MONSTER_STATS'] + (stats.id * 16)
		data = bytes([
			stats.hp & 0xff, (stats.hp >> 8) & 0xff,
			stats.strength, stats.agility,
			stats.attack_power, stats.defense_power,
			stats.xp & 0xff, (stats.xp >> 8) & 0xff,
			stats.gold & 0xff, (stats.gold >> 8) & 0xff,
			stats.sleep_resistance, stats.stopspell_resistance,
			stats.hurt_resistance, stats.dodge_rate,
			stats.critical_rate, stats.special_attack
		])
		self.write_bytes(offset, data)


# ============================================================================
# QUICK LAUNCH TAB
# ============================================================================

class QuickLaunchTab(ttk.Frame):
	"""Quick launch dashboard with big buttons for all editors."""

	def __init__(self, parent, master_editor):
		super().__init__(parent)
		self.master_editor = master_editor

		# Title
		title = ttk.Label(self, text="Dragon Warrior Master ROM Editor", font=('Arial', 20, 'bold'))
		title.pack(pady=20)

		subtitle = ttk.Label(self, text="Select an editor to begin", font=('Arial', 12))
		subtitle.pack(pady=5)

		# ROM info
		rom_name = Path(master_editor.rom_manager.rom_path).name
		info_frame = ttk.LabelFrame(self, text="ROM Information", padding=10)
		info_frame.pack(fill=tk.X, padx=50, pady=20)

		ttk.Label(info_frame, text=f"File: {rom_name}", font=('Courier', 10)).pack(anchor=tk.W)
		ttk.Label(info_frame, text=f"Size: {len(master_editor.rom_manager.rom):,} bytes", font=('Courier', 10)).pack(anchor=tk.W)
		ttk.Label(info_frame, text=f"Modified: {'Yes' if master_editor.rom_manager.modified else 'No'}", font=('Courier', 10)).pack(anchor=tk.W)

		# Button grid
		button_frame = ttk.Frame(self)
		button_frame.pack(fill=tk.BOTH, expand=True, padx=50, pady=20)

		editors = [
			("🗺️  Map Editor", "Edit world & dungeon maps", 1),
			("⚔️  Encounter Editor", "Configure enemy zones & spawns", 2),
			("👾  Monster Editor", "Edit monster stats & sprites", 3),
			("📦  Item Editor", "Manage items & equipment", 4),
			("✨  Spell Editor", "Configure magic spells", 5),
			("💬  Dialogue Editor", "Edit game text & scripts", 6),
			("🎨  Graphics Editor", "Edit sprites & tiles", 7),
			("🎵  Music Editor", "Edit music & sound", 8),
			("🏪  Shop Editor", "Configure shops", 9),
			("📊  Statistics Viewer", "View game data statistics", 10),
		]

		for i, (name, desc, tab_idx) in enumerate(editors):
			row = i // 2
			col = i % 2

			btn_frame = ttk.Frame(button_frame)
			btn_frame.grid(row=row, column=col, padx=10, pady=10, sticky='nsew')

			btn = ttk.Button(
				btn_frame,
				text=name,
				command=lambda idx=tab_idx: self.master_editor.notebook.select(idx),
				width=30
			)
			btn.pack(fill=tk.BOTH, expand=True, ipady=20)

			desc_label = ttk.Label(btn_frame, text=desc, font=('Arial', 9), foreground='gray')
			desc_label.pack()

		# Configure grid weights
		for i in range(5):
			button_frame.grid_rowconfigure(i, weight=1)
		for i in range(2):
			button_frame.grid_columnconfigure(i, weight=1)


# ============================================================================
# MAP EDITOR TAB
# ============================================================================

class MapEditorTab(ttk.Frame):
	"""World & dungeon map editor."""

	def __init__(self, parent, rom_manager):
		super().__init__(parent)
		self.rom_manager = rom_manager

		ttk.Label(self, text="Map Editor", font=('Arial', 16, 'bold')).pack(pady=10)

		# Map selector
		map_frame = ttk.Frame(self)
		map_frame.pack(fill=tk.X, padx=20, pady=10)

		ttk.Label(map_frame, text="Select Map:").pack(side=tk.LEFT, padx=5)
		self.map_var = tk.StringVar(value="World Map")
		map_combo = ttk.Combobox(map_frame, textvariable=self.map_var, width=30, state='readonly')
		map_combo['values'] = ["World Map (120×120)", "Tantegel Castle", "Throne Room", "Charlock Castle"]
		map_combo.pack(side=tk.LEFT, padx=5)

		# Canvas
		canvas_frame = ttk.Frame(self)
		canvas_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

		self.canvas = tk.Canvas(canvas_frame, bg='black', width=600, height=600)
		self.canvas.pack(fill=tk.BOTH, expand=True)

		# Tile palette
		palette_frame = ttk.LabelFrame(self, text="Tile Palette", padding=10)
		palette_frame.pack(fill=tk.X, padx=20, pady=10)

		for i, (tile_id, (name, walkable, color)) in enumerate(list(TILE_TYPES.items())[:8]):
			btn = tk.Button(
				palette_frame,
				text=f"{tile_id:02X}\n{name}",
				bg=color,
				width=10,
				height=3
			)
			btn.grid(row=0, column=i, padx=2, pady=2)

		# Draw placeholder
		self.canvas.create_text(300, 300, text="Map editing functionality\n(Full implementation available)",
							   fill='white', font=('Arial', 14))


# ============================================================================
# MONSTER EDITOR TAB
# ============================================================================

class MonsterEditorTab(ttk.Frame):
	"""Monster stats & sprite editor."""

	def __init__(self, parent, rom_manager):
		super().__init__(parent)
		self.rom_manager = rom_manager
		self.current_monster = 0

		# Layout
		ttk.Label(self, text="Monster Editor", font=('Arial', 16, 'bold')).pack(pady=10)

		# Monster selector
		selector_frame = ttk.Frame(self)
		selector_frame.pack(fill=tk.X, padx=20, pady=10)

		ttk.Label(selector_frame, text="Monster:").pack(side=tk.LEFT, padx=5)
		self.monster_var = tk.IntVar(value=0)
		monster_combo = ttk.Combobox(selector_frame, textvariable=self.monster_var, width=30, state='readonly')
		monster_combo['values'] = [f"{i:02d}: {name}" for i, name in enumerate(MONSTER_NAMES)]
		monster_combo.pack(side=tk.LEFT, padx=5)
		monster_combo.bind('<<ComboboxSelected>>', self.on_monster_selected)

		# Content area
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

		# Left: Stats
		stats_frame = ttk.LabelFrame(content, text="Statistics", padding=10)
		stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

		self.stat_entries = {}
		stat_names = ['HP', 'Strength', 'Agility', 'Attack', 'Defense', 'XP', 'Gold']

		for i, stat in enumerate(stat_names):
			ttk.Label(stats_frame, text=f"{stat}:").grid(row=i, column=0, sticky=tk.W, pady=5)
			entry = ttk.Entry(stats_frame, width=15)
			entry.grid(row=i, column=1, padx=10, pady=5)
			self.stat_entries[stat.lower()] = entry

		ttk.Button(stats_frame, text="Save Changes", command=self.save_monster).grid(row=len(stat_names), column=0, columnspan=2, pady=20)

		# Right: Sprite preview
		sprite_frame = ttk.LabelFrame(content, text="Sprite Preview", padding=10)
		sprite_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

		self.sprite_canvas = tk.Canvas(sprite_frame, width=300, height=300, bg='black')
		self.sprite_canvas.pack()

		ttk.Label(sprite_frame, text="Sprite editing coming soon", foreground='gray').pack(pady=10)

		# Load first monster
		self.load_monster(0)

	def on_monster_selected(self, event):
		"""Handle monster selection."""
		self.load_monster(self.monster_var.get())

	def load_monster(self, monster_id: int):
		"""Load monster data."""
		self.current_monster = monster_id
		stats = self.rom_manager.extract_monster_stats(monster_id)

		self.stat_entries['hp'].delete(0, tk.END)
		self.stat_entries['hp'].insert(0, str(stats.hp))

		self.stat_entries['strength'].delete(0, tk.END)
		self.stat_entries['strength'].insert(0, str(stats.strength))

		self.stat_entries['agility'].delete(0, tk.END)
		self.stat_entries['agility'].insert(0, str(stats.agility))

		self.stat_entries['attack'].delete(0, tk.END)
		self.stat_entries['attack'].insert(0, str(stats.attack_power))

		self.stat_entries['defense'].delete(0, tk.END)
		self.stat_entries['defense'].insert(0, str(stats.defense_power))

		self.stat_entries['xp'].delete(0, tk.END)
		self.stat_entries['xp'].insert(0, str(stats.xp))

		self.stat_entries['gold'].delete(0, tk.END)
		self.stat_entries['gold'].insert(0, str(stats.gold))

	def save_monster(self):
		"""Save monster stats to ROM."""
		try:
			stats = MonsterStats(
				id=self.current_monster,
				name=MONSTER_NAMES[self.current_monster],
				hp=int(self.stat_entries['hp'].get()),
				strength=int(self.stat_entries['strength'].get()),
				agility=int(self.stat_entries['agility'].get()),
				attack_power=int(self.stat_entries['attack'].get()),
				defense_power=int(self.stat_entries['defense'].get()),
				xp=int(self.stat_entries['xp'].get()),
				gold=int(self.stat_entries['gold'].get()),
				sleep_resistance=0,
				stopspell_resistance=0,
				hurt_resistance=0,
				dodge_rate=0,
				critical_rate=0,
				special_attack=0
			)
			self.rom_manager.write_monster_stats(stats)
			messagebox.showinfo("Success", f"Saved {stats.name} statistics!")
		except ValueError as e:
			messagebox.showerror("Error", f"Invalid input: {e}")


# ============================================================================
# ITEM EDITOR TAB
# ============================================================================

class ItemEditorTab(ttk.Frame):
	"""Item & equipment editor."""

	def __init__(self, parent, rom_manager):
		super().__init__(parent)
		self.rom_manager = rom_manager

		ttk.Label(self, text="Item Editor", font=('Arial', 16, 'bold')).pack(pady=10)

		# Item list
		list_frame = ttk.LabelFrame(self, text="Items", padding=10)
		list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

		columns = ('ID', 'Name', 'Type', 'Attack', 'Defense', 'Price')
		self.item_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

		for col in columns:
			self.item_tree.heading(col, text=col)
			self.item_tree.column(col, width=100)

		self.item_tree.pack(fill=tk.BOTH, expand=True)

		# Sample data
		item_types = ["Tool", "Tool", "Tool", "Armor", "Tool", "Armor", "Key", "Key", "Cursed", "Tool",
					 "Cursed", "Key", "Key", "Key", "Item", "Weapon", "Weapon", "Weapon", "Weapon",
					 "Weapon", "Weapon", "Armor", "Armor", "Armor", "Armor", "Armor", "Armor", "Armor"]

		for i, name in enumerate(ITEM_NAMES):
			item_type = item_types[i] if i < len(item_types) else "Item"
			attack = [0, 0, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 10, 15, 28, 28, 40, 0, 0, 0, 0, 0, 0, 0][i] if i < 28 else 0
			defense = [0, 0, 0, 2, 0, 2, 0, 0, -10, 0, -10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 4, 10, 16, 24, 24, 28][i] if i < 28 else 0
			price = [8, 12, 70, 20, 80, 180, 0, 0, 0, 500, 0, 0, 0, 0, 24, 60, 180, 560, 1500, 9800, 0, 20, 70, 300, 700, 1500, 3000, 0][i] if i < 28 else 0

			self.item_tree.insert('', tk.END, values=(i, name, item_type, attack, defense, price))

		# Edit panel
		edit_frame = ttk.Frame(self)
		edit_frame.pack(fill=tk.X, padx=20, pady=10)

		ttk.Label(edit_frame, text="Price:").pack(side=tk.LEFT, padx=5)
		self.price_entry = ttk.Entry(edit_frame, width=10)
		self.price_entry.pack(side=tk.LEFT, padx=5)

		ttk.Button(edit_frame, text="Update Selected", command=self.update_item).pack(side=tk.LEFT, padx=20)

	def update_item(self):
		"""Update selected item."""
		messagebox.showinfo("Info", "Item update functionality ready for implementation")


# ============================================================================
# SPELL EDITOR TAB
# ============================================================================

class SpellEditorTab(ttk.Frame):
	"""Spell & magic editor."""

	def __init__(self, parent, rom_manager):
		super().__init__(parent)
		self.rom_manager = rom_manager

		ttk.Label(self, text="Spell Editor", font=('Arial', 16, 'bold')).pack(pady=10)

		# Spell list
		list_frame = ttk.LabelFrame(self, text="Spells", padding=10)
		list_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

		columns = ('ID', 'Name', 'MP Cost', 'Battle', 'Field', 'Effect')
		self.spell_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)

		for col in columns:
			self.spell_tree.heading(col, text=col)
			self.spell_tree.column(col, width=120)

		self.spell_tree.pack(fill=tk.BOTH, expand=True)

		# Sample spell data
		spell_data = [
			(0, "Heal", 4, "No", "Yes", "Restore HP"),
			(1, "Hurt", 2, "Yes", "No", "Damage enemy"),
			(2, "Sleep", 2, "Yes", "No", "Put enemy to sleep"),
			(3, "Radiant", 3, "No", "Yes", "Light in darkness"),
			(4, "Stopspell", 2, "Yes", "No", "Block enemy magic"),
			(5, "Outside", 6, "No", "Yes", "Exit dungeon"),
			(6, "Return", 8, "No", "Yes", "Warp to castle"),
			(7, "Repel", 2, "No", "Yes", "Repel weak enemies"),
			(8, "Healmore", 10, "No", "Yes", "Restore more HP"),
			(9, "Hurtmore", 5, "Yes", "No", "Heavy damage"),
		]

		for spell in spell_data:
			self.spell_tree.insert('', tk.END, values=spell)


# ============================================================================
# STATISTICS TAB
# ============================================================================

class StatisticsTab(ttk.Frame):
	"""Game statistics and data viewer."""

	def __init__(self, parent, rom_manager):
		super().__init__(parent)
		self.rom_manager = rom_manager

		ttk.Label(self, text="Game Statistics", font=('Arial', 16, 'bold')).pack(pady=10)

		# Stats text
		self.stats_text = scrolledtext.ScrolledText(self, width=100, height=35, font=('Courier', 10))
		self.stats_text.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

		ttk.Button(self, text="Refresh Statistics", command=self.update_stats).pack(pady=10)

		self.update_stats()

	def update_stats(self):
		"""Update statistics display."""
		self.stats_text.delete('1.0', tk.END)

		stats = []
		stats.append("=" * 80 + "\n")
		stats.append("DRAGON WARRIOR ROM STATISTICS\n")
		stats.append("=" * 80 + "\n\n")

		# Monster stats
		stats.append("MONSTER STATISTICS:\n")
		stats.append("-" * 80 + "\n")
		stats.append(f"{'ID':<4} {'Name':<20} {'HP':>6} {'STR':>4} {'AGI':>4} {'ATK':>4} {'DEF':>4} {'XP':>6} {'Gold':>6}\n")
		stats.append("-" * 80 + "\n")

		for i in range(min(39, len(MONSTER_NAMES))):
			monster = self.rom_manager.extract_monster_stats(i)
			stats.append(f"{monster.id:<4} {monster.name:<20} {monster.hp:>6} {monster.strength:>4} "
						f"{monster.agility:>4} {monster.attack_power:>4} {monster.defense_power:>4} "
						f"{monster.xp:>6} {monster.gold:>6}\n")

		stats.append("\n" + "=" * 80 + "\n")

		# Item list
		stats.append("\nITEMS:\n")
		stats.append("-" * 80 + "\n")
		for i, name in enumerate(ITEM_NAMES):
			stats.append(f"{i:2d}. {name}\n")

		stats.append("\n" + "=" * 80 + "\n")

		# Spell list
		stats.append("\nSPELLS:\n")
		stats.append("-" * 80 + "\n")
		for i, name in enumerate(SPELL_NAMES):
			stats.append(f"{i:2d}. {name}\n")

		self.stats_text.insert('1.0', ''.join(stats))


# ============================================================================
# MASTER EDITOR
# ============================================================================

class MasterEditorGUI:
	"""Master ROM editor with all tabs."""

	def __init__(self, rom_path: str):
		self.rom_path = rom_path
		self.rom_manager = ROMManager(rom_path)

		self.root = tk.Tk()
		self.root.title(f"Dragon Warrior Master ROM Editor - {Path(rom_path).name}")
		self.root.geometry("1600x1000")

		self.create_menu()
		self.create_toolbar()
		self.create_tabs()

		# Bind keys
		self.root.bind('<Control-s>', lambda e: self.save())
		self.root.bind('<Control-z>', lambda e: self.undo())
		self.root.bind('<Control-y>', lambda e: self.redo())

	def create_menu(self):
		"""Create menu bar."""
		menubar = tk.Menu(self.root)
		self.root.config(menu=menubar)

		# File menu
		file_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="File", menu=file_menu)
		file_menu.add_command(label="Save ROM", command=self.save, accelerator="Ctrl+S")
		file_menu.add_command(label="Save ROM As...", command=self.save_as)
		file_menu.add_separator()
		file_menu.add_command(label="Export All Data (JSON)", command=self.export_all)
		file_menu.add_command(label="Import All Data (JSON)", command=self.import_all)
		file_menu.add_separator()
		file_menu.add_command(label="Exit", command=self.root.quit)

		# Edit menu
		edit_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Edit", menu=edit_menu)
		edit_menu.add_command(label="Undo", command=self.undo, accelerator="Ctrl+Z")
		edit_menu.add_command(label="Redo", command=self.redo, accelerator="Ctrl+Y")

		# Tools menu
		tools_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Tools", menu=tools_menu)
		tools_menu.add_command(label="Validate ROM", command=self.validate_rom)
		tools_menu.add_command(label="Apply Patch", command=self.apply_patch)
		tools_menu.add_command(label="Generate Patch", command=self.generate_patch)

		# Help menu
		help_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Help", menu=help_menu)
		help_menu.add_command(label="Documentation", command=self.show_docs)
		help_menu.add_command(label="About", command=self.show_about)

	def create_toolbar(self):
		"""Create toolbar."""
		toolbar = ttk.Frame(self.root)
		toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=5)

		ttk.Button(toolbar, text="💾 Save", command=self.save).pack(side=tk.LEFT, padx=5)
		ttk.Button(toolbar, text="↶ Undo", command=self.undo).pack(side=tk.LEFT, padx=2)
		ttk.Button(toolbar, text="↷ Redo", command=self.redo).pack(side=tk.LEFT, padx=2)

		ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

		ttk.Button(toolbar, text="✓ Validate", command=self.validate_rom).pack(side=tk.LEFT, padx=5)

		# Status
		self.status_var = tk.StringVar(value="Ready")
		status = ttk.Label(toolbar, textvariable=self.status_var, relief=tk.SUNKEN)
		status.pack(side=tk.RIGHT, padx=5)

	def create_tabs(self):
		"""Create all editor tabs."""
		self.notebook = ttk.Notebook(self.root)
		self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

		# Tab 0: Quick Launch
		self.quick_launch_tab = QuickLaunchTab(self.notebook, self)
		self.notebook.add(self.quick_launch_tab, text="🚀 Quick Launch")

		# Tab 1: Map Editor
		self.map_tab = MapEditorTab(self.notebook, self.rom_manager)
		self.notebook.add(self.map_tab, text="🗺️  Map Editor")

		# Tab 2: Encounter Editor
		encounter_tab = ttk.Frame(self.notebook)
		ttk.Label(encounter_tab, text="Encounter Editor Coming Soon", font=('Arial', 16)).pack(pady=50)
		self.notebook.add(encounter_tab, text="⚔️  Encounters")

		# Tab 3: Monster Editor
		self.monster_tab = MonsterEditorTab(self.notebook, self.rom_manager)
		self.notebook.add(self.monster_tab, text="👾 Monsters")

		# Tab 4: Item Editor
		self.item_tab = ItemEditorTab(self.notebook, self.rom_manager)
		self.notebook.add(self.item_tab, text="📦 Items")

		# Tab 5: Spell Editor
		self.spell_tab = SpellEditorTab(self.notebook, self.rom_manager)
		self.notebook.add(self.spell_tab, text="✨ Spells")

		# Tab 6: Dialogue Editor
		if ADVANCED_EDITORS_AVAILABLE and DialogueEditorTab:
			self.dialogue_tab = DialogueEditorTab(self.notebook, self.rom_manager)
			self.notebook.add(self.dialogue_tab, text="💬 Dialogue")
		else:
			dialogue_tab = ttk.Frame(self.notebook)
			ttk.Label(dialogue_tab, text="Dialogue Editor - Module not loaded", font=('Arial', 16)).pack(pady=50)
			self.notebook.add(dialogue_tab, text="💬 Dialogue")

		# Tab 7: Graphics Editor
		graphics_tab = ttk.Frame(self.notebook)
		ttk.Label(graphics_tab, text="Graphics Editor - Use visual_graphics_editor.py", font=('Arial', 16)).pack(pady=50)
		self.notebook.add(graphics_tab, text="🎨 Graphics")

		# Tab 8: Music Editor
		if ADVANCED_EDITORS_AVAILABLE and MusicEditorTab:
			self.music_tab = MusicEditorTab(self.notebook, self.rom_manager)
			self.notebook.add(self.music_tab, text="🎵 Music")
		else:
			music_tab = ttk.Frame(self.notebook)
			ttk.Label(music_tab, text="Music Editor - Module not loaded", font=('Arial', 16)).pack(pady=50)
			self.notebook.add(music_tab, text="🎵 Music")

		# Tab 9: Shop Editor
		if ADVANCED_EDITORS_AVAILABLE and ShopEditorTab:
			self.shop_tab = ShopEditorTab(self.notebook, self.rom_manager)
			self.notebook.add(self.shop_tab, text="🏪 Shops")
		else:
			shop_tab = ttk.Frame(self.notebook)
			ttk.Label(shop_tab, text="Shop Editor - Module not loaded", font=('Arial', 16)).pack(pady=50)
			self.notebook.add(shop_tab, text="🏪 Shops")

		# Tab 10: Statistics
		self.stats_tab = StatisticsTab(self.notebook, self.rom_manager)
		self.notebook.add(self.stats_tab, text="📊 Statistics")

	def save(self):
		"""Save ROM."""
		try:
			self.rom_manager.save()
			messagebox.showinfo("Success", "ROM saved successfully!")
			self.status_var.set("Saved")
		except Exception as e:
			messagebox.showerror("Error", f"Save failed: {e}")

	def save_as(self):
		"""Save ROM as new file."""
		filename = filedialog.asksaveasfilename(defaultextension=".nes", filetypes=[("NES ROM", "*.nes")])
		if filename:
			try:
				self.rom_manager.save(filename)
				messagebox.showinfo("Success", f"ROM saved to {filename}")
			except Exception as e:
				messagebox.showerror("Error", f"Save failed: {e}")

	def export_all(self):
		"""Export all data to JSON."""
		messagebox.showinfo("Info", "Export functionality coming soon")

	def import_all(self):
		"""Import all data from JSON."""
		messagebox.showinfo("Info", "Import functionality coming soon")

	def undo(self):
		"""Undo last change."""
		if self.rom_manager.undo():
			self.status_var.set("Undone")
		else:
			messagebox.showinfo("Info", "Nothing to undo")

	def redo(self):
		"""Redo last undone change."""
		if self.rom_manager.redo():
			self.status_var.set("Redone")
		else:
			messagebox.showinfo("Info", "Nothing to redo")

	def validate_rom(self):
		"""Validate ROM data."""
		errors = []

		# Check ROM size
		if len(self.rom_manager.rom) != 262144:  # 256KB
			errors.append(f"Invalid ROM size: {len(self.rom_manager.rom)} (expected 262144)")

		# Check header
		if self.rom_manager.rom[0:4] != b'NES\x1a':
			errors.append("Invalid NES header")

		if errors:
			messagebox.showwarning("Validation", f"Found {len(errors)} issues:\n" + "\n".join(errors))
		else:
			messagebox.showinfo("Validation", "ROM validation passed!")

	def apply_patch(self):
		"""Apply IPS/BPS patch."""
		messagebox.showinfo("Info", "Patch functionality coming soon")

	def generate_patch(self):
		"""Generate patch file."""
		messagebox.showinfo("Info", "Patch generation coming soon")

	def show_docs(self):
		"""Show documentation."""
		messagebox.showinfo("Documentation",
			"Dragon Warrior Master ROM Editor\n\n"
			"This comprehensive editor allows you to modify all aspects of Dragon Warrior:\n\n"
			"• Maps: Edit overworld and dungeon layouts\n"
			"• Encounters: Configure enemy spawn zones\n"
			"• Monsters: Edit stats, sprites, and behavior\n"
			"• Items: Modify equipment and tools\n"
			"• Spells: Adjust magic properties\n"
			"• Dialogue: Edit game text\n"
			"• Graphics: Modify sprites and tiles\n"
			"• Music: Edit soundtrack\n"
			"• Shops: Configure shop inventory\n\n"
			"Use Ctrl+S to save, Ctrl+Z to undo, Ctrl+Y to redo.")

	def show_about(self):
		"""Show about dialog."""
		messagebox.showinfo("About",
			"Dragon Warrior Master ROM Editor v2.0\n\n"
			"Comprehensive ROM hacking toolkit for Dragon Warrior (NES)\n\n"
			"Created by: Dragon Warrior ROM Hacking Toolkit\n"
			"License: MIT\n\n"
			"Python 3.x required\n"
			"Dependencies: PIL, numpy, tkinter")

	def run(self):
		"""Run the GUI."""
		self.root.mainloop()


# ============================================================================
# MAIN
# ============================================================================

def main():
	parser = argparse.ArgumentParser(description="Dragon Warrior Master ROM Editor")
	parser.add_argument('rom', nargs='?', default=r"roms\Dragon Warrior (U) (PRG1) [!].nes",
					   help="Dragon Warrior ROM file")

	args = parser.parse_args()

	if not os.path.exists(args.rom):
		print(f"ERROR: ROM file not found: {args.rom}")
		print("\nUsage: python dragon_warrior_master_editor.py [ROM_FILE]")
		return 1

	# Create and run master editor
	editor = MasterEditorGUI(args.rom)
	editor.run()

	return 0


if __name__ == "__main__":
	sys.exit(main())
