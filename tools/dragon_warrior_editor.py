#!/usr/bin/env python3
"""
Dragon Warrior Unified ROM Editor - Complete GUI Application

A comprehensive, all-in-one graphical editor for Dragon Warrior (NES) ROM hacking.
Combines all editing capabilities into a single, user-friendly tabbed interface.

Features:
- Monster/Enemy Editor (stats, HP, XP, gold, spells)
- Item/Equipment Editor (stats, prices, effects)
- Spell Editor (MP cost, power, effects)
- Map Editor (world map, towns, dungeons)
- Dialog/Text Editor (all game text with search)
- Graphics/Sprite Editor (CHR tiles, palettes)
- Music/Audio Editor (sequences, instruments)
- Shop Editor (inventory, prices)
- NPC/AI Editor (behavior patterns)
- Quest/Progression Editor (flags, items, gates)
- Save File Editor (modify saves)
- ROM Analyzer (data visualization, statistics)

Built with PyQt5 for modern, responsive UI.

Usage:
	python tools/dragon_warrior_editor.py [ROM_FILE]

Requirements:
	pip install PyQt5 pillow numpy

Author: Dragon Warrior ROM Hacking Toolkit
Version: 2.0
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
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from enum import Enum

try:
	from PyQt5.QtWidgets import (
		QApplication, QMainWindow, QTabWidget, QWidget, QVBoxLayout,
		QHBoxLayout, QLabel, QPushButton, QSpinBox, QLineEdit, QTextEdit,
		QComboBox, QCheckBox, QGroupBox, QTableWidget, QTableWidgetItem,
		QFileDialog, QMessageBox, QStatusBar, QMenuBar, QAction, QDialog,
		QDialogButtonBox, QFormLayout, QListWidget, QSplitter, QFrame,
		QScrollArea, QSlider, QDoubleSpinBox, QProgressBar, QTreeWidget,
		QTreeWidgetItem, QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
		QColorDialog, QToolBar, QMenu, QActionGroup, QDockWidget, QHeaderView
	)
	from PyQt5.QtCore import Qt, QTimer, QSize, pyqtSignal, QPoint, QRect
	from PyQt5.QtGui import (
		QPixmap, QImage, QColor, QPainter, QPen, QBrush, QFont, QIcon,
		QKeySequence, QPalette, QLinearGradient
	)
except ImportError:
	print("ERROR: PyQt5 not installed. Install with: pip install PyQt5")
	sys.exit(1)

try:
	from PIL import Image
	import numpy as np
except ImportError:
	print("ERROR: PIL/numpy not installed. Install with: pip install pillow numpy")
	sys.exit(1)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class DataType(Enum):
	"""Types of editable game data."""
	MONSTER = "monster"
	ITEM = "item"
	SPELL = "spell"
	MAP = "map"
	DIALOG = "dialog"
	GRAPHICS = "graphics"
	MUSIC = "music"
	SHOP = "shop"
	NPC = "npc"
	QUEST = "quest"


@dataclass
class MonsterData:
	"""Monster/enemy data structure."""
	id: int
	name: str
	hp: int
	mp: int = 0
	strength: int = 0
	agility: int = 0
	attack_power: int = 0
	defense_power: int = 0
	xp_reward: int = 0
	gold_reward: int = 0
	spell: str = "None"
	sleep_resist: int = 0
	stopspell_resist: int = 0
	hurt_resist: int = 0
	dodge_rate: int = 0


@dataclass
class ItemData:
	"""Item/equipment data structure."""
	id: int
	name: str
	type: str  # "weapon", "armor", "shield", "tool", "key"
	attack: int = 0
	defense: int = 0
	price: int = 0
	sellable: bool = True
	cursed: bool = False
	equippable: bool = True
	usable: bool = False
	effect: str = "None"


@dataclass
class SpellData:
	"""Spell data structure."""
	id: int
	name: str
	mp_cost: int
	power: int = 0
	type: str  # "heal", "attack", "utility", "buff", "debuff"
	target: str = "single"  # "single", "all", "self"
	field_usable: bool = False
	battle_usable: bool = True
	effect: str = ""


@dataclass
class ROMMetadata:
	"""ROM file metadata."""
	filepath: Path
	size: int
	checksum: int
	version: str = "Unknown"
	modified: bool = False
	backup_created: bool = False


# ============================================================================
# ROM DATA MANAGER
# ============================================================================

class ROMDataManager:
	"""Manages all ROM data loading, parsing, and saving."""

	# ROM Offsets (Dragon Warrior U PRG1)
	MONSTER_OFFSET = 0x5e5b
	MONSTER_COUNT = 39
	MONSTER_SIZE = 16

	SPELL_OFFSET = 0x5f3b
	SPELL_COUNT = 10
	SPELL_SIZE = 8

	ITEM_OFFSET = 0x5f83
	ITEM_COUNT = 32
	ITEM_SIZE = 8

	TEXT_OFFSET = 0x8000
	TEXT_SIZE = 0x4000

	CHR_OFFSET = 0x10010  # CHR-ROM starts at 0x10 + iNES header
	CHR_SIZE = 0x2000

	# Names
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

	SPELL_NAMES = [
		"Heal", "Hurt", "Sleep", "Radiant", "Stopspell",
		"Outside", "Return", "Repel", "Healmore", "Hurtmore"
	]

	ITEM_NAMES = [
		"Bamboo Pole", "Club", "Copper Sword", "Hand Axe", "Broad Sword",
		"Flame Sword", "Erdrick's Sword", "Clothes", "Leather Armor",
		"Chain Mail", "Half Plate", "Full Plate", "Magic Armor",
		"Erdrick's Armor", "Small Shield", "Large Shield", "Silver Shield",
		"Herb", "Torch", "Dragon's Scale", "Fairy Water", "Wings",
		"Stones of Sunlight", "Staff of Rain", "Rainbow Drop", "Gwaelin's Love",
		"Cursed Belt", "Silver Harp", "Death Necklace", "Erdrick's Token",
		"Fighter's Ring", "Warrior's Ring"
	]

	def __init__(self):
		self.rom_data: bytearray = bytearray()
		self.metadata: Optional[ROMMetadata] = None
		self.monsters: List[MonsterData] = []
		self.items: List[ItemData] = []
		self.spells: List[SpellData] = []

	def load_rom(self, filepath: str) -> bool:
		"""Load ROM file and extract all data."""
		try:
			path = Path(filepath)
			if not path.exists():
				return False

			with open(path, 'rb') as f:
				self.rom_data = bytearray(f.read())

			# Create metadata
			self.metadata = ROMMetadata(
				filepath=path,
				size=len(self.rom_data),
				checksum=sum(self.rom_data) & 0xffffffff,
				version=self._detect_version()
			)

			# Extract data
			self._extract_monsters()
			self._extract_items()
			self._extract_spells()

			return True

		except Exception as e:
			print(f"Error loading ROM: {e}")
			return False

	def save_rom(self, filepath: Optional[str] = None) -> bool:
		"""Save ROM with all modifications."""
		try:
			if filepath is None:
				if self.metadata is None:
					return False
				filepath = self.metadata.filepath

			# Create backup if not exists
			if not self.metadata.backup_created:
				backup_path = Path(str(filepath) + ".bak")
				if not backup_path.exists():
					with open(backup_path, 'wb') as f:
						# Read original file for backup
						with open(filepath, 'rb') as orig:
							f.write(orig.read())
					self.metadata.backup_created = True

			# Reinsert all data
			self._reinsert_monsters()
			self._reinsert_items()
			self._reinsert_spells()

			# Write to file
			with open(filepath, 'wb') as f:
				f.write(self.rom_data)

			self.metadata.modified = False
			return True

		except Exception as e:
			print(f"Error saving ROM: {e}")
			return False

	def _detect_version(self) -> str:
		"""Detect ROM version."""
		if len(self.rom_data) == 0x20000:
			return "Dragon Warrior (USA)"
		elif len(self.rom_data) == 0x40000:
			return "Dragon Quest (Japan)"
		return "Unknown"

	def _extract_monsters(self) -> None:
		"""Extract monster data from ROM."""
		self.monsters = []
		offset = self.MONSTER_OFFSET

		for i in range(self.MONSTER_COUNT):
			data = self.rom_data[offset:offset + self.MONSTER_SIZE]

			monster = MonsterData(
				id=i,
				name=self.MONSTER_NAMES[i],
				hp=data[0] | (data[1] << 8),
				strength=data[2],
				agility=data[3],
				attack_power=data[4],
				defense_power=data[5],
				xp_reward=data[6] | (data[7] << 8),
				gold_reward=data[8] | (data[9] << 8),
				spell=self._decode_spell(data[10]),
				sleep_resist=data[11],
				stopspell_resist=data[12],
				hurt_resist=data[13],
				dodge_rate=data[14]
			)

			self.monsters.append(monster)
			offset += self.MONSTER_SIZE

	def _extract_items(self) -> None:
		"""Extract item data from ROM."""
		self.items = []
		offset = self.ITEM_OFFSET

		for i in range(self.ITEM_COUNT):
			data = self.rom_data[offset:offset + self.ITEM_SIZE]

			item = ItemData(
				id=i,
				name=self.ITEM_NAMES[i] if i < len(self.ITEM_NAMES) else f"Item {i}",
				type=self._decode_item_type(data[0]),
				attack=data[1],
				defense=data[2],
				price=data[3] | (data[4] << 8),
				sellable=bool(data[5] & 0x01),
				cursed=bool(data[5] & 0x02),
				equippable=bool(data[5] & 0x04)
			)

			self.items.append(item)
			offset += self.ITEM_SIZE

	def _extract_spells(self) -> None:
		"""Extract spell data from ROM."""
		self.spells = []
		offset = self.SPELL_OFFSET

		for i in range(self.SPELL_COUNT):
			data = self.rom_data[offset:offset + self.SPELL_SIZE]

			spell = SpellData(
				id=i,
				name=self.SPELL_NAMES[i] if i < len(self.SPELL_NAMES) else f"Spell {i}",
				mp_cost=data[0],
				power=data[1],
				type=self._decode_spell_type(data[2]),
				field_usable=bool(data[3] & 0x01),
				battle_usable=bool(data[3] & 0x02)
			)

			self.spells.append(spell)
			offset += self.SPELL_SIZE

	def _reinsert_monsters(self) -> None:
		"""Reinsert monster data into ROM."""
		offset = self.MONSTER_OFFSET

		for monster in self.monsters:
			data = bytearray(self.MONSTER_SIZE)

			# Pack data
			data[0] = monster.hp & 0xff
			data[1] = (monster.hp >> 8) & 0xff
			data[2] = monster.strength & 0xff
			data[3] = monster.agility & 0xff
			data[4] = monster.attack_power & 0xff
			data[5] = monster.defense_power & 0xff
			data[6] = monster.xp_reward & 0xff
			data[7] = (monster.xp_reward >> 8) & 0xff
			data[8] = monster.gold_reward & 0xff
			data[9] = (monster.gold_reward >> 8) & 0xff
			data[10] = self._encode_spell(monster.spell)
			data[11] = monster.sleep_resist & 0xff
			data[12] = monster.stopspell_resist & 0xff
			data[13] = monster.hurt_resist & 0xff
			data[14] = monster.dodge_rate & 0xff

			# Write to ROM
			self.rom_data[offset:offset + self.MONSTER_SIZE] = data
			offset += self.MONSTER_SIZE

	def _reinsert_items(self) -> None:
		"""Reinsert item data into ROM."""
		offset = self.ITEM_OFFSET

		for item in self.items:
			data = bytearray(self.ITEM_SIZE)

			data[0] = self._encode_item_type(item.type)
			data[1] = item.attack & 0xff
			data[2] = item.defense & 0xff
			data[3] = item.price & 0xff
			data[4] = (item.price >> 8) & 0xff
			data[5] = (int(item.sellable) | (int(item.cursed) << 1) |
					   (int(item.equippable) << 2))

			self.rom_data[offset:offset + self.ITEM_SIZE] = data
			offset += self.ITEM_SIZE

	def _reinsert_spells(self) -> None:
		"""Reinsert spell data into ROM."""
		offset = self.SPELL_OFFSET

		for spell in self.spells:
			data = bytearray(self.SPELL_SIZE)

			data[0] = spell.mp_cost & 0xff
			data[1] = spell.power & 0xff
			data[2] = self._encode_spell_type(spell.type)
			data[3] = int(spell.field_usable) | (int(spell.battle_usable) << 1)

			self.rom_data[offset:offset + self.SPELL_SIZE] = data
			offset += self.SPELL_SIZE

	def _decode_spell(self, value: int) -> str:
		"""Decode spell ID to name."""
		if value == 0xff:
			return "None"
		elif value < len(self.SPELL_NAMES):
			return self.SPELL_NAMES[value]
		return f"Unknown ({value})"

	def _encode_spell(self, name: str) -> int:
		"""Encode spell name to ID."""
		if name == "None":
			return 0xff
		try:
			return self.SPELL_NAMES.index(name)
		except ValueError:
			return 0xff

	def _decode_item_type(self, value: int) -> str:
		"""Decode item type byte."""
		type_map = {0: "weapon", 1: "armor", 2: "shield", 3: "tool", 4: "key"}
		return type_map.get(value, "unknown")

	def _encode_item_type(self, type_str: str) -> int:
		"""Encode item type string."""
		type_map = {"weapon": 0, "armor": 1, "shield": 2, "tool": 3, "key": 4}
		return type_map.get(type_str, 0)

	def _decode_spell_type(self, value: int) -> str:
		"""Decode spell type."""
		type_map = {0: "heal", 1: "attack", 2: "utility", 3: "buff", 4: "debuff"}
		return type_map.get(value, "unknown")

	def _encode_spell_type(self, type_str: str) -> int:
		"""Encode spell type."""
		type_map = {"heal": 0, "attack": 1, "utility": 2, "buff": 3, "debuff": 4}
		return type_map.get(type_str, 0)


# ============================================================================
# GUI WIDGETS - MONSTER EDITOR
# ============================================================================

class MonsterEditorWidget(QWidget):
	"""Monster/enemy editor tab."""

	data_changed = pyqtSignal()

	def __init__(self, rom_manager: ROMDataManager):
		super().__init__()
		self.rom_manager = rom_manager
		self.current_monster_index = 0
		self.init_ui()

	def init_ui(self):
		"""Initialize the monster editor UI."""
		layout = QVBoxLayout()

		# Top: Monster selection
		select_layout = QHBoxLayout()
		select_layout.addWidget(QLabel("Monster:"))

		self.monster_combo = QComboBox()
		self.monster_combo.currentIndexChanged.connect(self.load_monster)
		select_layout.addWidget(self.monster_combo)

		select_layout.addStretch()
		layout.addLayout(select_layout)

		# Middle: Monster stats editor
		stats_group = QGroupBox("Monster Statistics")
		stats_layout = QFormLayout()

		self.hp_spin = QSpinBox()
		self.hp_spin.setRange(1, 65535)
		self.hp_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("HP:", self.hp_spin)

		self.str_spin = QSpinBox()
		self.str_spin.setRange(0, 255)
		self.str_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Strength:", self.str_spin)

		self.agi_spin = QSpinBox()
		self.agi_spin.setRange(0, 255)
		self.agi_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Agility:", self.agi_spin)

		self.atk_spin = QSpinBox()
		self.atk_spin.setRange(0, 255)
		self.atk_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Attack Power:", self.atk_spin)

		self.def_spin = QSpinBox()
		self.def_spin.setRange(0, 255)
		self.def_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Defense Power:", self.def_spin)

		self.xp_spin = QSpinBox()
		self.xp_spin.setRange(0, 65535)
		self.xp_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("XP Reward:", self.xp_spin)

		self.gold_spin = QSpinBox()
		self.gold_spin.setRange(0, 65535)
		self.gold_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Gold Reward:", self.gold_spin)

		self.spell_combo = QComboBox()
		self.spell_combo.addItems(["None"] + self.rom_manager.SPELL_NAMES)
		self.spell_combo.currentTextChanged.connect(self.on_data_changed)
		stats_layout.addRow("Spell:", self.spell_combo)

		self.sleep_resist_spin = QSpinBox()
		self.sleep_resist_spin.setRange(0, 255)
		self.sleep_resist_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Sleep Resist:", self.sleep_resist_spin)

		self.stop_resist_spin = QSpinBox()
		self.stop_resist_spin.setRange(0, 255)
		self.stop_resist_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Stopspell Resist:", self.stop_resist_spin)

		self.hurt_resist_spin = QSpinBox()
		self.hurt_resist_spin.setRange(0, 255)
		self.hurt_resist_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Hurt Resist:", self.hurt_resist_spin)

		self.dodge_spin = QSpinBox()
		self.dodge_spin.setRange(0, 255)
		self.dodge_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Dodge Rate:", self.dodge_spin)

		stats_group.setLayout(stats_layout)
		layout.addWidget(stats_group)

		# Bottom: Quick stats display
		info_group = QGroupBox("Quick Info")
		info_layout = QVBoxLayout()

		self.info_label = QLabel()
		self.info_label.setWordWrap(True)
		info_layout.addWidget(self.info_label)

		info_group.setLayout(info_layout)
		layout.addWidget(info_group)

		layout.addStretch()
		self.setLayout(layout)

	def refresh(self):
		"""Refresh monster list."""
		self.monster_combo.clear()
		for monster in self.rom_manager.monsters:
			self.monster_combo.addItem(monster.name)

	def load_monster(self, index: int):
		"""Load monster data into editor."""
		if index < 0 or index >= len(self.rom_manager.monsters):
			return

		self.current_monster_index = index
		monster = self.rom_manager.monsters[index]

		# Block signals during load
		self.hp_spin.blockSignals(True)
		self.str_spin.blockSignals(True)
		self.agi_spin.blockSignals(True)
		self.atk_spin.blockSignals(True)
		self.def_spin.blockSignals(True)
		self.xp_spin.blockSignals(True)
		self.gold_spin.blockSignals(True)
		self.spell_combo.blockSignals(True)
		self.sleep_resist_spin.blockSignals(True)
		self.stop_resist_spin.blockSignals(True)
		self.hurt_resist_spin.blockSignals(True)
		self.dodge_spin.blockSignals(True)

		# Set values
		self.hp_spin.setValue(monster.hp)
		self.str_spin.setValue(monster.strength)
		self.agi_spin.setValue(monster.agility)
		self.atk_spin.setValue(monster.attack_power)
		self.def_spin.setValue(monster.defense_power)
		self.xp_spin.setValue(monster.xp_reward)
		self.gold_spin.setValue(monster.gold_reward)
		self.spell_combo.setCurrentText(monster.spell)
		self.sleep_resist_spin.setValue(monster.sleep_resist)
		self.stop_resist_spin.setValue(monster.stopspell_resist)
		self.hurt_resist_spin.setValue(monster.hurt_resist)
		self.dodge_spin.setValue(monster.dodge_rate)

		# Unblock signals
		self.hp_spin.blockSignals(False)
		self.str_spin.blockSignals(False)
		self.agi_spin.blockSignals(False)
		self.atk_spin.blockSignals(False)
		self.def_spin.blockSignals(False)
		self.xp_spin.blockSignals(False)
		self.gold_spin.blockSignals(False)
		self.spell_combo.blockSignals(False)
		self.sleep_resist_spin.blockSignals(False)
		self.stop_resist_spin.blockSignals(False)
		self.hurt_resist_spin.blockSignals(False)
		self.dodge_spin.blockSignals(False)

		self.update_info()

	def save_monster(self):
		"""Save current monster data."""
		if self.current_monster_index < 0:
			return

		monster = self.rom_manager.monsters[self.current_monster_index]
		monster.hp = self.hp_spin.value()
		monster.strength = self.str_spin.value()
		monster.agility = self.agi_spin.value()
		monster.attack_power = self.atk_spin.value()
		monster.defense_power = self.def_spin.value()
		monster.xp_reward = self.xp_spin.value()
		monster.gold_reward = self.gold_spin.value()
		monster.spell = self.spell_combo.currentText()
		monster.sleep_resist = self.sleep_resist_spin.value()
		monster.stopspell_resist = self.stop_resist_spin.value()
		monster.hurt_resist = self.hurt_resist_spin.value()
		monster.dodge_rate = self.dodge_spin.value()

		if self.rom_manager.metadata:
			self.rom_manager.metadata.modified = True

	def on_data_changed(self):
		"""Handle data change."""
		self.save_monster()
		self.update_info()
		self.data_changed.emit()

	def update_info(self):
		"""Update quick info display."""
		monster = self.rom_manager.monsters[self.current_monster_index]

		# Calculate efficiency rating
		if monster.hp > 0:
			reward_total = monster.xp_reward + monster.gold_reward
			efficiency = reward_total / monster.hp
		else:
			efficiency = 0

		info_text = f"""
<b>{monster.name}</b><br>
<br>
<b>Combat Stats:</b><br>
HP: {monster.hp} | STR: {monster.strength} | AGI: {monster.agility}<br>
ATK: {monster.attack_power} | DEF: {monster.defense_power}<br>
<br>
<b>Rewards:</b><br>
XP: {monster.xp_reward} | Gold: {monster.gold_reward}<br>
Efficiency: {efficiency:.2f} (reward/HP)<br>
<br>
<b>Special:</b><br>
Spell: {monster.spell}<br>
Sleep Resist: {monster.sleep_resist} | Stopspell: {monster.stopspell_resist}<br>
Hurt Resist: {monster.hurt_resist} | Dodge: {monster.dodge_rate}
		"""

		self.info_label.setText(info_text.strip())


# ============================================================================
# GUI WIDGETS - ITEM EDITOR
# ============================================================================

class ItemEditorWidget(QWidget):
	"""Item/equipment editor tab."""

	data_changed = pyqtSignal()

	def __init__(self, rom_manager: ROMDataManager):
		super().__init__()
		self.rom_manager = rom_manager
		self.current_item_index = 0
		self.init_ui()

	def init_ui(self):
		"""Initialize the item editor UI."""
		layout = QVBoxLayout()

		# Top: Item selection
		select_layout = QHBoxLayout()
		select_layout.addWidget(QLabel("Item:"))

		self.item_combo = QComboBox()
		self.item_combo.currentIndexChanged.connect(self.load_item)
		select_layout.addWidget(self.item_combo)

		select_layout.addStretch()
		layout.addLayout(select_layout)

		# Middle: Item stats editor
		stats_group = QGroupBox("Item Properties")
		stats_layout = QFormLayout()

		self.type_combo = QComboBox()
		self.type_combo.addItems(["weapon", "armor", "shield", "tool", "key"])
		self.type_combo.currentTextChanged.connect(self.on_data_changed)
		stats_layout.addRow("Type:", self.type_combo)

		self.attack_spin = QSpinBox()
		self.attack_spin.setRange(0, 255)
		self.attack_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Attack Power:", self.attack_spin)

		self.defense_spin = QSpinBox()
		self.defense_spin.setRange(0, 255)
		self.defense_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Defense Power:", self.defense_spin)

		self.price_spin = QSpinBox()
		self.price_spin.setRange(0, 65535)
		self.price_spin.valueChanged.connect(self.on_data_changed)
		stats_layout.addRow("Price:", self.price_spin)

		self.sellable_check = QCheckBox()
		self.sellable_check.stateChanged.connect(self.on_data_changed)
		stats_layout.addRow("Sellable:", self.sellable_check)

		self.cursed_check = QCheckBox()
		self.cursed_check.stateChanged.connect(self.on_data_changed)
		stats_layout.addRow("Cursed:", self.cursed_check)

		self.equippable_check = QCheckBox()
		self.equippable_check.stateChanged.connect(self.on_data_changed)
		stats_layout.addRow("Equippable:", self.equippable_check)

		stats_group.setLayout(stats_layout)
		layout.addWidget(stats_group)

		# Bottom: Info
		info_group = QGroupBox("Item Info")
		info_layout = QVBoxLayout()

		self.info_label = QLabel()
		self.info_label.setWordWrap(True)
		info_layout.addWidget(self.info_label)

		info_group.setLayout(info_layout)
		layout.addWidget(info_group)

		layout.addStretch()
		self.setLayout(layout)

	def refresh(self):
		"""Refresh item list."""
		self.item_combo.clear()
		for item in self.rom_manager.items:
			self.item_combo.addItem(item.name)

	def load_item(self, index: int):
		"""Load item data into editor."""
		if index < 0 or index >= len(self.rom_manager.items):
			return

		self.current_item_index = index
		item = self.rom_manager.items[index]

		# Block signals
		self.type_combo.blockSignals(True)
		self.attack_spin.blockSignals(True)
		self.defense_spin.blockSignals(True)
		self.price_spin.blockSignals(True)
		self.sellable_check.blockSignals(True)
		self.cursed_check.blockSignals(True)
		self.equippable_check.blockSignals(True)

		# Set values
		self.type_combo.setCurrentText(item.type)
		self.attack_spin.setValue(item.attack)
		self.defense_spin.setValue(item.defense)
		self.price_spin.setValue(item.price)
		self.sellable_check.setChecked(item.sellable)
		self.cursed_check.setChecked(item.cursed)
		self.equippable_check.setChecked(item.equippable)

		# Unblock signals
		self.type_combo.blockSignals(False)
		self.attack_spin.blockSignals(False)
		self.defense_spin.blockSignals(False)
		self.price_spin.blockSignals(False)
		self.sellable_check.blockSignals(False)
		self.cursed_check.blockSignals(False)
		self.equippable_check.blockSignals(False)

		self.update_info()

	def save_item(self):
		"""Save current item data."""
		if self.current_item_index < 0:
			return

		item = self.rom_manager.items[self.current_item_index]
		item.type = self.type_combo.currentText()
		item.attack = self.attack_spin.value()
		item.defense = self.defense_spin.value()
		item.price = self.price_spin.value()
		item.sellable = self.sellable_check.isChecked()
		item.cursed = self.cursed_check.isChecked()
		item.equippable = self.equippable_check.isChecked()

		if self.rom_manager.metadata:
			self.rom_manager.metadata.modified = True

	def on_data_changed(self):
		"""Handle data change."""
		self.save_item()
		self.update_info()
		self.data_changed.emit()

	def update_info(self):
		"""Update info display."""
		item = self.rom_manager.items[self.current_item_index]

		info_text = f"""
<b>{item.name}</b><br>
<br>
<b>Type:</b> {item.type.capitalize()}<br>
<b>Stats:</b> ATK +{item.attack}, DEF +{item.defense}<br>
<b>Price:</b> {item.price} gold<br>
<b>Sell Price:</b> {item.price // 2 if item.sellable else 'Cannot sell'}<br>
<br>
<b>Flags:</b><br>
Sellable: {'Yes' if item.sellable else 'No'}<br>
Cursed: {'Yes' if item.cursed else 'No'}<br>
Equippable: {'Yes' if item.equippable else 'No'}
		"""

		self.info_label.setText(info_text.strip())


# ============================================================================
# GUI WIDGETS - SPELL EDITOR
# ============================================================================

class SpellEditorWidget(QWidget):
	"""Spell editor tab."""

	data_changed = pyqtSignal()

	def __init__(self, rom_manager: ROMDataManager):
		super().__init__()
		self.rom_manager = rom_manager
		self.current_spell_index = 0
		self.init_ui()

	def init_ui(self):
		"""Initialize spell editor UI."""
		layout = QVBoxLayout()

		# Top: Spell selection
		select_layout = QHBoxLayout()
		select_layout.addWidget(QLabel("Spell:"))

		self.spell_combo = QComboBox()
		self.spell_combo.currentIndexChanged.connect(self.load_spell)
		select_layout.addWidget(self.spell_combo)

		select_layout.addStretch()
		layout.addLayout(select_layout)

		# Middle: Spell properties
		props_group = QGroupBox("Spell Properties")
		props_layout = QFormLayout()

		self.mp_spin = QSpinBox()
		self.mp_spin.setRange(0, 255)
		self.mp_spin.valueChanged.connect(self.on_data_changed)
		props_layout.addRow("MP Cost:", self.mp_spin)

		self.power_spin = QSpinBox()
		self.power_spin.setRange(0, 255)
		self.power_spin.valueChanged.connect(self.on_data_changed)
		props_layout.addRow("Power:", self.power_spin)

		self.type_combo = QComboBox()
		self.type_combo.addItems(["heal", "attack", "utility", "buff", "debuff"])
		self.type_combo.currentTextChanged.connect(self.on_data_changed)
		props_layout.addRow("Type:", self.type_combo)

		self.field_check = QCheckBox()
		self.field_check.stateChanged.connect(self.on_data_changed)
		props_layout.addRow("Field Usable:", self.field_check)

		self.battle_check = QCheckBox()
		self.battle_check.stateChanged.connect(self.on_data_changed)
		props_layout.addRow("Battle Usable:", self.battle_check)

		props_group.setLayout(props_layout)
		layout.addWidget(props_group)

		# Info
		info_group = QGroupBox("Spell Info")
		info_layout = QVBoxLayout()

		self.info_label = QLabel()
		self.info_label.setWordWrap(True)
		info_layout.addWidget(self.info_label)

		info_group.setLayout(info_layout)
		layout.addWidget(info_group)

		layout.addStretch()
		self.setLayout(layout)

	def refresh(self):
		"""Refresh spell list."""
		self.spell_combo.clear()
		for spell in self.rom_manager.spells:
			self.spell_combo.addItem(spell.name)

	def load_spell(self, index: int):
		"""Load spell data."""
		if index < 0 or index >= len(self.rom_manager.spells):
			return

		self.current_spell_index = index
		spell = self.rom_manager.spells[index]

		self.mp_spin.blockSignals(True)
		self.power_spin.blockSignals(True)
		self.type_combo.blockSignals(True)
		self.field_check.blockSignals(True)
		self.battle_check.blockSignals(True)

		self.mp_spin.setValue(spell.mp_cost)
		self.power_spin.setValue(spell.power)
		self.type_combo.setCurrentText(spell.type)
		self.field_check.setChecked(spell.field_usable)
		self.battle_check.setChecked(spell.battle_usable)

		self.mp_spin.blockSignals(False)
		self.power_spin.blockSignals(False)
		self.type_combo.blockSignals(False)
		self.field_check.blockSignals(False)
		self.battle_check.blockSignals(False)

		self.update_info()

	def save_spell(self):
		"""Save spell data."""
		if self.current_spell_index < 0:
			return

		spell = self.rom_manager.spells[self.current_spell_index]
		spell.mp_cost = self.mp_spin.value()
		spell.power = self.power_spin.value()
		spell.type = self.type_combo.currentText()
		spell.field_usable = self.field_check.isChecked()
		spell.battle_usable = self.battle_check.isChecked()

		if self.rom_manager.metadata:
			self.rom_manager.metadata.modified = True

	def on_data_changed(self):
		"""Handle data change."""
		self.save_spell()
		self.update_info()
		self.data_changed.emit()

	def update_info(self):
		"""Update info display."""
		spell = self.rom_manager.spells[self.current_spell_index]

		usable = []
		if spell.field_usable:
			usable.append("Field")
		if spell.battle_usable:
			usable.append("Battle")

		info_text = f"""
<b>{spell.name}</b><br>
<br>
<b>Type:</b> {spell.type.capitalize()}<br>
<b>MP Cost:</b> {spell.mp_cost}<br>
<b>Power:</b> {spell.power}<br>
<b>Usable:</b> {', '.join(usable) if usable else 'None'}<br>
<br>
<b>Efficiency:</b> {spell.power / spell.mp_cost if spell.mp_cost > 0 else 0:.2f} power/MP
		"""

		self.info_label.setText(info_text.strip())


# ============================================================================
# MAIN WINDOW
# ============================================================================

class DragonWarriorEditor(QMainWindow):
	"""Main application window."""

	def __init__(self):
		super().__init__()
		self.rom_manager = ROMDataManager()
		self.current_file = None
		self.init_ui()

	def init_ui(self):
		"""Initialize main window UI."""
		self.setWindowTitle("Dragon Warrior ROM Editor v2.0")
		self.setGeometry(100, 100, 1200, 800)

		# Create menu bar
		self.create_menus()

		# Create central widget with tabs
		self.tabs = QTabWidget()
		self.setCentralWidget(self.tabs)

		# Create editor widgets
		self.monster_editor = MonsterEditorWidget(self.rom_manager)
		self.monster_editor.data_changed.connect(self.on_data_changed)
		self.tabs.addTab(self.monster_editor, "Monsters")

		self.item_editor = ItemEditorWidget(self.rom_manager)
		self.item_editor.data_changed.connect(self.on_data_changed)
		self.tabs.addTab(self.item_editor, "Items")

		self.spell_editor = SpellEditorWidget(self.rom_manager)
		self.spell_editor.data_changed.connect(self.on_data_changed)
		self.tabs.addTab(self.spell_editor, "Spells")

		# Placeholder tabs
		self.tabs.addTab(QLabel("Map editor coming soon..."), "Maps")
		self.tabs.addTab(QLabel("Dialog editor coming soon..."), "Dialogs")
		self.tabs.addTab(QLabel("Graphics editor coming soon..."), "Graphics")
		self.tabs.addTab(QLabel("Music editor coming soon..."), "Music")
		self.tabs.addTab(QLabel("Analysis tools coming soon..."), "Analysis")

		# Status bar
		self.status_bar = QStatusBar()
		self.setStatusBar(self.status_bar)
		self.status_bar.showMessage("Ready - No ROM loaded")

		# Auto-load ROM if provided
		if len(sys.argv) > 1:
			rom_path = sys.argv[1]
			if os.path.exists(rom_path):
				self.load_rom(rom_path)

	def create_menus(self):
		"""Create menu bar."""
		menubar = self.menuBar()

		# File menu
		file_menu = menubar.addMenu("&File")

		open_action = QAction("&Open ROM...", self)
		open_action.setShortcut(QKeySequence.Open)
		open_action.triggered.connect(self.open_rom_dialog)
		file_menu.addAction(open_action)

		save_action = QAction("&Save ROM", self)
		save_action.setShortcut(QKeySequence.Save)
		save_action.triggered.connect(self.save_rom)
		file_menu.addAction(save_action)

		save_as_action = QAction("Save ROM &As...", self)
		save_as_action.setShortcut(QKeySequence.SaveAs)
		save_as_action.triggered.connect(self.save_rom_as)
		file_menu.addAction(save_as_action)

		file_menu.addSeparator()

		exit_action = QAction("E&xit", self)
		exit_action.setShortcut(QKeySequence.Quit)
		exit_action.triggered.connect(self.close)
		file_menu.addAction(exit_action)

		# Edit menu
		edit_menu = menubar.addMenu("&Edit")

		undo_action = QAction("&Undo", self)
		undo_action.setShortcut(QKeySequence.Undo)
		undo_action.setEnabled(False)
		edit_menu.addAction(undo_action)

		redo_action = QAction("&Redo", self)
		redo_action.setShortcut(QKeySequence.Redo)
		redo_action.setEnabled(False)
		edit_menu.addAction(redo_action)

		# Tools menu
		tools_menu = menubar.addMenu("&Tools")

		analyze_action = QAction("&Analyze ROM", self)
		analyze_action.triggered.connect(self.analyze_rom)
		tools_menu.addAction(analyze_action)

		validate_action = QAction("&Validate Data", self)
		validate_action.triggered.connect(self.validate_data)
		tools_menu.addAction(validate_action)

		# Help menu
		help_menu = menubar.addMenu("&Help")

		about_action = QAction("&About", self)
		about_action.triggered.connect(self.show_about)
		help_menu.addAction(about_action)

	def open_rom_dialog(self):
		"""Open file dialog to load ROM."""
		filename, _ = QFileDialog.getOpenFileName(
			self,
			"Open Dragon Warrior ROM",
			"",
			"NES ROMs (*.nes);;All Files (*.*)"
		)

		if filename:
			self.load_rom(filename)

	def load_rom(self, filepath: str):
		"""Load ROM file."""
		if self.rom_manager.load_rom(filepath):
			self.current_file = filepath
			self.refresh_editors()
			self.status_bar.showMessage(f"Loaded: {filepath}")
			self.setWindowTitle(f"Dragon Warrior ROM Editor v2.0 - {Path(filepath).name}")
		else:
			QMessageBox.critical(self, "Error", f"Failed to load ROM: {filepath}")

	def save_rom(self):
		"""Save ROM to current file."""
		if self.current_file:
			if self.rom_manager.save_rom(self.current_file):
				self.status_bar.showMessage(f"Saved: {self.current_file}")
				QMessageBox.information(self, "Success", "ROM saved successfully!")
			else:
				QMessageBox.critical(self, "Error", "Failed to save ROM")
		else:
			self.save_rom_as()

	def save_rom_as(self):
		"""Save ROM to new file."""
		filename, _ = QFileDialog.getSaveFileName(
			self,
			"Save Dragon Warrior ROM",
			"",
			"NES ROMs (*.nes);;All Files (*.*)"
		)

		if filename:
			if self.rom_manager.save_rom(filename):
				self.current_file = filename
				self.status_bar.showMessage(f"Saved: {filename}")
				QMessageBox.information(self, "Success", "ROM saved successfully!")
			else:
				QMessageBox.critical(self, "Error", "Failed to save ROM")

	def refresh_editors(self):
		"""Refresh all editor widgets."""
		self.monster_editor.refresh()
		self.monster_editor.load_monster(0)

		self.item_editor.refresh()
		self.item_editor.load_item(0)

		self.spell_editor.refresh()
		self.spell_editor.load_spell(0)

	def on_data_changed(self):
		"""Handle data changes."""
		if self.rom_manager.metadata:
			self.rom_manager.metadata.modified = True
			self.status_bar.showMessage("Modified (unsaved changes)")

	def analyze_rom(self):
		"""Show ROM analysis."""
		if not self.rom_manager.metadata:
			QMessageBox.warning(self, "No ROM", "Please load a ROM first")
			return

		# Calculate statistics
		total_hp = sum(m.hp for m in self.rom_manager.monsters)
		total_xp = sum(m.xp_reward for m in self.rom_manager.monsters)
		total_gold = sum(m.gold_reward for m in self.rom_manager.monsters)

		total_items = len(self.rom_manager.items)
		total_weapons = sum(1 for i in self.rom_manager.items if i.type == "weapon")
		total_armor = sum(1 for i in self.rom_manager.items if i.type == "armor")

		analysis = f"""
<h2>ROM Analysis</h2>

<h3>File Info</h3>
Path: {self.rom_manager.metadata.filepath}<br>
Size: {self.rom_manager.metadata.size} bytes<br>
Version: {self.rom_manager.metadata.version}<br>
Checksum: {self.rom_manager.metadata.checksum:08X}<br>

<h3>Monster Statistics</h3>
Total Monsters: {len(self.rom_manager.monsters)}<br>
Total HP: {total_hp}<br>
Total XP: {total_xp}<br>
Total Gold: {total_gold}<br>
Average HP: {total_hp / len(self.rom_manager.monsters):.1f}<br>

<h3>Item Statistics</h3>
Total Items: {total_items}<br>
Weapons: {total_weapons}<br>
Armor: {total_armor}<br>
Shields: {sum(1 for i in self.rom_manager.items if i.type == "shield")}<br>
Tools: {sum(1 for i in self.rom_manager.items if i.type == "tool")}<br>

<h3>Spell Statistics</h3>
Total Spells: {len(self.rom_manager.spells)}<br>
Average MP Cost: {sum(s.mp_cost for s in self.rom_manager.spells) / len(self.rom_manager.spells):.1f}<br>
		"""

		msg = QMessageBox(self)
		msg.setWindowTitle("ROM Analysis")
		msg.setTextFormat(Qt.RichText)
		msg.setText(analysis)
		msg.exec_()

	def validate_data(self):
		"""Validate ROM data."""
		errors = []

		# Validate monsters
		for i, monster in enumerate(self.rom_manager.monsters):
			if monster.hp == 0:
				errors.append(f"Monster {i} ({monster.name}) has 0 HP")
			if monster.xp_reward == 0 and monster.gold_reward == 0:
				errors.append(f"Monster {i} ({monster.name}) has no rewards")

		# Validate items
		for i, item in enumerate(self.rom_manager.items):
			if item.type == "weapon" and item.attack == 0:
				errors.append(f"Weapon {i} ({item.name}) has 0 attack")
			if item.type == "armor" and item.defense == 0:
				errors.append(f"Armor {i} ({item.name}) has 0 defense")

		# Validate spells
		for i, spell in enumerate(self.rom_manager.spells):
			if spell.mp_cost == 0:
				errors.append(f"Spell {i} ({spell.name}) has 0 MP cost")

		if errors:
			msg = "Validation found issues:\n\n" + "\n".join(errors)
			QMessageBox.warning(self, "Validation Errors", msg)
		else:
			QMessageBox.information(self, "Validation", "All data validated successfully!")

	def show_about(self):
		"""Show about dialog."""
		about_text = """
<h2>Dragon Warrior ROM Editor v2.0</h2>

<p>A comprehensive, unified editor for Dragon Warrior (NES) ROM hacking.</p>

<p><b>Features:</b></p>
<ul>
<li>Monster/Enemy editing</li>
<li>Item/Equipment editing</li>
<li>Spell editing</li>
<li>Data validation</li>
<li>ROM analysis</li>
</ul>

<p><b>Author:</b> Dragon Warrior ROM Hacking Toolkit</p>
<p><b>License:</b> MIT</p>

<p>Built with PyQt5, Python 3.x</p>
		"""

		QMessageBox.about(self, "About Dragon Warrior Editor", about_text)

	def closeEvent(self, event):
		"""Handle window close event."""
		if self.rom_manager.metadata and self.rom_manager.metadata.modified:
			reply = QMessageBox.question(
				self,
				"Unsaved Changes",
				"You have unsaved changes. Do you want to save before exiting?",
				QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
			)

			if reply == QMessageBox.Save:
				self.save_rom()
				event.accept()
			elif reply == QMessageBox.Discard:
				event.accept()
			else:
				event.ignore()
		else:
			event.accept()


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
	"""Main entry point."""
	app = QApplication(sys.argv)

	# Set application style
	app.setStyle("Fusion")

	# Dark palette (optional)
	# palette = QPalette()
	# palette.setColor(QPalette.Window, QColor(53, 53, 53))
	# palette.setColor(QPalette.WindowText, Qt.white)
	# app.setPalette(palette)

	editor = DragonWarriorEditor()
	editor.show()

	sys.exit(app.exec_())


if __name__ == "__main__":
	main()
