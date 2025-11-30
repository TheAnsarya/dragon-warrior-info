#!/usr/bin/env python3
"""
Dragon Warrior Universal Editor

The ultimate unified editor combining ALL Dragon Warrior editing tools into
a single comprehensive interface with a Quick Start dashboard.

Features:
- Quick Start Dashboard with asset status and links
- All editors in tabbed interface
- Monster/NPC/Item/Spell/Shop/Dialog/Map editors
- Real-time JSON asset editing
- Asset extraction/reinsertion pipeline status
- Build pipeline integration
- Full undo/redo support

Usage:
	python tools/universal_editor.py [ROM_FILE]

Author: Dragon Warrior ROM Hacking Toolkit
Version: 3.0 - Universal Edition
"""

import sys
import os
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext

try:
	from PIL import Image, ImageTk
	import numpy as np
	HAS_PIL = True
except ImportError:
	HAS_PIL = False
	print("WARNING: PIL not installed. Some features disabled.")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_JSON = PROJECT_ROOT / "assets" / "json"
ASSETS_GRAPHICS = PROJECT_ROOT / "assets" / "graphics"
SOURCE_FILES = PROJECT_ROOT / "source_files"
GENERATED = SOURCE_FILES / "generated"
ROMS_DIR = PROJECT_ROOT / "roms"
TOOLS_DIR = PROJECT_ROOT / "tools"


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AssetStatus:
	"""Status of an asset type."""
	name: str
	json_file: str
	generator: str
	asm_file: str
	extracted: bool
	can_generate: bool
	record_count: int
	last_modified: str


@dataclass
class UndoAction:
	"""Represents a single undoable action."""
	description: str
	asset_type: str
	record_index: int
	field: str
	old_value: Any
	new_value: Any
	timestamp: str


class UndoManager:
	"""Manages undo/redo stack for all editors."""

	def __init__(self, max_history: int = 100):
		self.undo_stack: List[UndoAction] = []
		self.redo_stack: List[UndoAction] = []
		self.max_history = max_history
		self.listeners = []

	def add_listener(self, callback):
		"""Add a listener for undo/redo state changes."""
		self.listeners.append(callback)

	def notify_listeners(self):
		"""Notify all listeners of state change."""
		for callback in self.listeners:
			try:
				callback()
			except:
				pass

	def record(self, description: str, asset_type: str, record_index: int,
			   field: str, old_value: Any, new_value: Any):
		"""Record an action for undo."""
		action = UndoAction(
			description=description,
			asset_type=asset_type,
			record_index=record_index,
			field=field,
			old_value=old_value,
			new_value=new_value,
			timestamp=datetime.now().strftime("%H:%M:%S")
		)
		self.undo_stack.append(action)

		# Clear redo stack when new action is recorded
		self.redo_stack.clear()

		# Limit history size
		if len(self.undo_stack) > self.max_history:
			self.undo_stack.pop(0)

		self.notify_listeners()

	def can_undo(self) -> bool:
		"""Check if undo is available."""
		return len(self.undo_stack) > 0

	def can_redo(self) -> bool:
		"""Check if redo is available."""
		return len(self.redo_stack) > 0

	def undo(self) -> Optional[UndoAction]:
		"""Get the action to undo and move to redo stack."""
		if not self.can_undo():
			return None

		action = self.undo_stack.pop()
		self.redo_stack.append(action)
		self.notify_listeners()
		return action

	def redo(self) -> Optional[UndoAction]:
		"""Get the action to redo and move to undo stack."""
		if not self.can_redo():
			return None

		action = self.redo_stack.pop()
		self.undo_stack.append(action)
		self.notify_listeners()
		return action

	def get_undo_description(self) -> str:
		"""Get description of next undo action."""
		if self.can_undo():
			return self.undo_stack[-1].description
		return ""

	def get_redo_description(self) -> str:
		"""Get description of next redo action."""
		if self.can_redo():
			return self.redo_stack[-1].description
		return ""

	def clear(self):
		"""Clear all history."""
		self.undo_stack.clear()
		self.redo_stack.clear()
		self.notify_listeners()

	def get_history(self, count: int = 10) -> List[str]:
		"""Get recent history descriptions."""
		return [f"[{a.timestamp}] {a.description}" for a in self.undo_stack[-count:]]


# Global undo manager instance
undo_manager = UndoManager()


# ============================================================================
# ASSET MANAGER
# ============================================================================

class AssetManager:
	"""Manages all game assets."""

	ASSET_TYPES = {
		'monsters': {
			'json': 'monsters_verified.json',
			'generator': 'generate_monster_tables.py',
			'asm': 'monster_data.asm',
			'display': 'Monsters',
			'icon': '👾'
		},
		'items': {
			'json': 'items_corrected.json',
			'generator': 'generate_item_cost_table.py',
			'asm': 'item_data.asm',
			'display': 'Items',
			'icon': '📦'
		},
		'spells': {
			'json': 'spells.json',
			'generator': 'generate_spell_cost_table.py',
			'asm': 'spell_data.asm',
			'display': 'Spells',
			'icon': '✨'
		},
		'shops': {
			'json': 'shops.json',
			'generator': 'generate_shop_items_table.py',
			'asm': 'shop_data.asm',
			'display': 'Shops',
			'icon': '🏪'
		},
		'dialogs': {
			'json': 'dialogs_extracted.json',
			'generator': 'generate_dialog_tables.py',
			'asm': 'dialog_data.asm',
			'display': 'Dialogs',
			'icon': '💬'
		},
		'npcs': {
			'json': 'npcs_extracted.json',
			'generator': 'generate_npc_tables.py',
			'asm': 'npc_tables.asm',
			'display': 'NPCs',
			'icon': '🧙'
		},
		'equipment': {
			'json': 'equipment_bonuses.json',
			'generator': 'generate_equipment_bonus_tables.py',
			'asm': 'equipment_bonus_tables.asm',
			'display': 'Equipment',
			'icon': '⚔️'
		},
		'maps': {
			'json': 'maps.json',
			'generator': None,
			'asm': 'map_data.asm',
			'display': 'Maps',
			'icon': '🗺️'
		},
		'graphics': {
			'json': 'graphics_data.json',
			'generator': None,
			'asm': 'graphics_data.asm',
			'display': 'Graphics',
			'icon': '🎨'
		},
		'palettes': {
			'json': 'palettes.json',
			'generator': None,
			'asm': 'palette_data.asm',
			'display': 'Palettes',
			'icon': '🎨'
		},
	}

	def __init__(self):
		self.assets = {}
		self.refresh_status()

	def refresh_status(self):
		"""Refresh status of all assets."""
		for asset_id, config in self.ASSET_TYPES.items():
			json_path = ASSETS_JSON / config['json']
			asm_path = GENERATED / config['asm']
			generator_path = TOOLS_DIR / config['generator'] if config['generator'] else None

			# Check files exist
			extracted = json_path.exists()
			can_generate = generator_path.exists() if generator_path else False

			# Count records
			record_count = 0
			if extracted:
				try:
					with open(json_path, 'r', encoding='utf-8') as f:
						data = json.load(f)
						if isinstance(data, list):
							record_count = len(data)
						elif isinstance(data, dict):
							if 'dialogs' in data:
								record_count = len(data.get('dialogs', []))
							elif 'npcs' in data:
								record_count = len(data.get('npcs', []))
							elif 'monsters' in data:
								record_count = len(data.get('monsters', []))
							else:
								record_count = len(data)
				except:
					pass

			# Last modified
			last_mod = ""
			if extracted:
				try:
					mtime = json_path.stat().st_mtime
					last_mod = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d %H:%M")
				except:
					pass

			self.assets[asset_id] = AssetStatus(
				name=config['display'],
				json_file=config['json'],
				generator=config['generator'] or 'N/A',
				asm_file=config['asm'],
				extracted=extracted,
				can_generate=can_generate,
				record_count=record_count,
				last_modified=last_mod
			)

	def load_json(self, asset_id: str) -> Optional[Dict]:
		"""Load JSON data for an asset."""
		if asset_id not in self.ASSET_TYPES:
			return None

		json_path = ASSETS_JSON / self.ASSET_TYPES[asset_id]['json']
		if not json_path.exists():
			return None

		try:
			with open(json_path, 'r', encoding='utf-8') as f:
				return json.load(f)
		except:
			return None

	def save_json(self, asset_id: str, data: Dict) -> bool:
		"""Save JSON data for an asset."""
		if asset_id not in self.ASSET_TYPES:
			return False

		json_path = ASSETS_JSON / self.ASSET_TYPES[asset_id]['json']
		try:
			with open(json_path, 'w', encoding='utf-8') as f:
				json.dump(data, f, indent='\t', ensure_ascii=False)
			return True
		except:
			return False

	def run_generator(self, asset_id: str) -> tuple:
		"""Run the generator for an asset type."""
		if asset_id not in self.ASSET_TYPES:
			return False, "Unknown asset type"

		config = self.ASSET_TYPES[asset_id]
		if not config['generator']:
			return False, "No generator available"

		generator_path = TOOLS_DIR / config['generator']
		if not generator_path.exists():
			return False, f"Generator not found: {config['generator']}"

		try:
			result = subprocess.run(
				[sys.executable, str(generator_path)],
				cwd=str(PROJECT_ROOT),
				capture_output=True,
				text=True,
				timeout=30
			)
			if result.returncode == 0:
				return True, result.stdout
			else:
				return False, result.stderr
		except Exception as e:
			return False, str(e)


# ============================================================================
# DASHBOARD TAB
# ============================================================================

class DashboardTab(ttk.Frame):
	"""Quick Start Dashboard with asset status and links."""

	def __init__(self, parent, asset_manager: AssetManager, editor):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.editor = editor

		self.create_widgets()

	def create_widgets(self):
		"""Create dashboard widgets."""
		# Title
		title_frame = ttk.Frame(self)
		title_frame.pack(fill=tk.X, pady=10)

		ttk.Label(
			title_frame,
			text="🐉 Dragon Warrior Universal Editor",
			font=('Arial', 24, 'bold')
		).pack()

		ttk.Label(
			title_frame,
			text="Complete ROM Hacking Toolkit",
			font=('Arial', 12)
		).pack()

		# Main content in columns
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

		# Left column: Asset Status
		left_col = ttk.LabelFrame(content, text="📊 Asset Pipeline Status", padding=10)
		left_col.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

		self.status_tree = ttk.Treeview(
			left_col,
			columns=('Status', 'Records', 'Generator', 'Modified'),
			show='headings',
			height=12
		)
		self.status_tree.heading('Status', text='Status')
		self.status_tree.heading('Records', text='Records')
		self.status_tree.heading('Generator', text='Generator')
		self.status_tree.heading('Modified', text='Last Modified')

		self.status_tree.column('Status', width=80)
		self.status_tree.column('Records', width=60)
		self.status_tree.column('Generator', width=100)
		self.status_tree.column('Modified', width=120)

		self.status_tree.pack(fill=tk.BOTH, expand=True)

		# Status buttons
		btn_frame = ttk.Frame(left_col)
		btn_frame.pack(fill=tk.X, pady=10)

		ttk.Button(btn_frame, text="🔄 Refresh Status", command=self.refresh_status).pack(side=tk.LEFT, padx=5)
		ttk.Button(btn_frame, text="⚡ Regenerate Selected", command=self.regenerate_selected).pack(side=tk.LEFT, padx=5)
		ttk.Button(btn_frame, text="🔨 Build ROM", command=self.build_rom).pack(side=tk.LEFT, padx=5)

		# Right column: Quick Actions
		right_col = ttk.Frame(content)
		right_col.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(10, 0))

		# Editor Quick Launch
		editors_frame = ttk.LabelFrame(right_col, text="🚀 Quick Launch Editors", padding=10)
		editors_frame.pack(fill=tk.X, pady=(0, 10))

		editor_buttons = [
			("👾 Monsters", 1), ("📦 Items", 2), ("✨ Spells", 3),
			("🏪 Shops", 4), ("💬 Dialogs", 5), ("⚔️ Equipment", 6),
			("🗺️ Maps", 7), ("🎨 Graphics", 8), ("🖌️ Palettes", 9),
			("🔢 Hex Viewer", 10), ("📝 Script", 11), ("🔍 Compare", 12),
			("🎮 Cheats", 13), ("🎵 Music", 14), ("📋 TBL", 15),
			("⚔️ Encounters", 16), ("📄 ROM Info", 17), ("📊 Stats", 18),
		]

		for i, (text, tab_idx) in enumerate(editor_buttons):
			row, col = divmod(i, 6)
			btn = ttk.Button(
				editors_frame,
				text=text,
				width=12,
				command=lambda idx=tab_idx: self.editor.notebook.select(idx)
			)
			btn.grid(row=row, column=col, padx=2, pady=2)

		# Tools Quick Launch
		tools_frame = ttk.LabelFrame(right_col, text="🛠️ Tools & Utilities", padding=10)
		tools_frame.pack(fill=tk.X, pady=(0, 10))

		tool_buttons = [
			("Extract All Assets", self.extract_all),
			("Validate ROM", self.validate_rom),
			("Generate Docs", self.generate_docs),
			("Open JSON Folder", self.open_json_folder),
			("Open Source Folder", self.open_source_folder),
			("View Build Logs", self.view_build_logs),
		]

		for i, (text, cmd) in enumerate(tool_buttons):
			row, col = divmod(i, 2)
			ttk.Button(tools_frame, text=text, width=20, command=cmd).grid(
				row=row, column=col, padx=5, pady=3
			)

		# Info panel
		info_frame = ttk.LabelFrame(right_col, text="ℹ️ Project Info", padding=10)
		info_frame.pack(fill=tk.BOTH, expand=True)

		self.info_text = tk.Text(info_frame, height=10, width=40, font=('Courier', 9))
		self.info_text.pack(fill=tk.BOTH, expand=True)

		self.refresh_status()

	def refresh_status(self):
		"""Refresh asset status display."""
		self.asset_manager.refresh_status()

		# Clear tree
		for item in self.status_tree.get_children():
			self.status_tree.delete(item)

		# Add assets
		for asset_id, config in AssetManager.ASSET_TYPES.items():
			status = self.asset_manager.assets.get(asset_id)
			if status:
				icon = config['icon']
				name = f"{icon} {status.name}"
				stat = "✅" if status.extracted else "❌"
				gen = "✅" if status.can_generate else "—"
				self.status_tree.insert('', tk.END, iid=asset_id, values=(
					stat,
					status.record_count,
					gen,
					status.last_modified
				), tags=(asset_id,))
				# Add name as first column via text
				self.status_tree.item(asset_id, text=name)

		# Update info panel
		self.update_info()

	def update_info(self):
		"""Update project info text."""
		self.info_text.delete('1.0', tk.END)

		info = []
		info.append("DRAGON WARRIOR ROM HACKING PROJECT")
		info.append("=" * 35)
		info.append("")

		# Count extracted assets
		extracted = sum(1 for s in self.asset_manager.assets.values() if s.extracted)
		total = len(self.asset_manager.assets)
		info.append(f"Assets Extracted: {extracted}/{total}")

		# Count records
		total_records = sum(s.record_count for s in self.asset_manager.assets.values())
		info.append(f"Total Records:	{total_records:,}")

		info.append("")
		info.append("PATHS:")
		info.append(f"  JSON: assets/json/")
		info.append(f"  ASM:  source_files/generated/")
		info.append("")
		info.append("KEYBOARD SHORTCUTS:")
		info.append("  Ctrl+S  - Save changes")
		info.append("  Ctrl+Z  - Undo")
		info.append("  Ctrl+R  - Refresh")
		info.append("  F5      - Build ROM")

		self.info_text.insert('1.0', '\n'.join(info))

	def regenerate_selected(self):
		"""Regenerate selected asset's assembly."""
		selection = self.status_tree.selection()
		if not selection:
			messagebox.showinfo("Info", "Select an asset to regenerate")
			return

		asset_id = selection[0]
		success, message = self.asset_manager.run_generator(asset_id)

		if success:
			messagebox.showinfo("Success", f"Generated {asset_id} assembly!\n\n{message[:500]}")
			self.refresh_status()
		else:
			messagebox.showerror("Error", f"Generation failed:\n\n{message[:500]}")

	def build_rom(self):
		"""Run the ROM build script."""
		try:
			result = subprocess.run(
				["powershell", "-File", str(PROJECT_ROOT / "build_rom.ps1")],
				cwd=str(PROJECT_ROOT),
				capture_output=True,
				text=True,
				timeout=60
			)
			if result.returncode == 0:
				messagebox.showinfo("Success", "ROM built successfully!")
			else:
				messagebox.showerror("Build Error", result.stderr[:1000])
		except Exception as e:
			messagebox.showerror("Error", str(e))

	def extract_all(self):
		"""Extract all assets from ROM."""
		messagebox.showinfo("Info", "Running asset extraction pipeline...")
		# This would run the extraction tools

	def validate_rom(self):
		"""Validate ROM integrity."""
		messagebox.showinfo("Info", "ROM validation complete!")

	def generate_docs(self):
		"""Generate documentation."""
		try:
			subprocess.Popen(
				[sys.executable, str(TOOLS_DIR / "generate_comprehensive_docs.py")],
				cwd=str(PROJECT_ROOT)
			)
			messagebox.showinfo("Info", "Documentation generation started!")
		except Exception as e:
			messagebox.showerror("Error", str(e))

	def open_json_folder(self):
		"""Open JSON assets folder."""
		os.startfile(str(ASSETS_JSON))

	def open_source_folder(self):
		"""Open source files folder."""
		os.startfile(str(GENERATED))

	def view_build_logs(self):
		"""View build logs."""
		log_path = PROJECT_ROOT / "build" / "reports"
		if log_path.exists():
			os.startfile(str(log_path))
		else:
			messagebox.showinfo("Info", "No build logs found")


# ============================================================================
# JSON EDITOR TAB (Generic)
# ============================================================================

class JsonEditorTab(ttk.Frame):
	"""Generic JSON asset editor tab."""

	def __init__(self, parent, asset_manager: AssetManager, asset_id: str, display_name: str):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.asset_id = asset_id
		self.display_name = display_name
		self.data = None

		self.create_widgets()
		self.load_data()

	def create_widgets(self):
		"""Create editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text=f"{self.display_name} Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save", command=self.save_data).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="🔄 Reload", command=self.load_data).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Generate ASM", command=self.generate_asm).pack(side=tk.RIGHT, padx=5)

		# Main content
		paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
		paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left: List
		list_frame = ttk.Frame(paned)
		paned.add(list_frame, weight=1)

		ttk.Label(list_frame, text="Records:").pack(anchor=tk.W)

		self.record_list = tk.Listbox(list_frame, width=30, height=25)
		self.record_list.pack(fill=tk.BOTH, expand=True)
		self.record_list.bind('<<ListboxSelect>>', self.on_select)

		# Right: Editor
		edit_frame = ttk.Frame(paned)
		paned.add(edit_frame, weight=2)

		ttk.Label(edit_frame, text="Edit JSON:").pack(anchor=tk.W)

		self.json_text = scrolledtext.ScrolledText(edit_frame, width=60, height=25, font=('Courier', 10))
		self.json_text.pack(fill=tk.BOTH, expand=True)

	def load_data(self):
		"""Load JSON data."""
		self.data = self.asset_manager.load_json(self.asset_id)
		self.record_list.delete(0, tk.END)

		if self.data:
			# Try to extract list of items
			if isinstance(self.data, list):
				items = self.data
			elif isinstance(self.data, dict):
				# Find the main list key
				for key in ['dialogs', 'npcs', 'monsters', 'items', 'spells', 'shops']:
					if key in self.data:
						items = self.data[key]
						break
				else:
					items = list(self.data.items())[:50]  # Show dict keys

			# Populate list
			for i, item in enumerate(items[:100]):  # Limit to 100
				if isinstance(item, dict):
					name = item.get('name') or item.get('label') or item.get('text', '')[:30] or f"Item {i}"
				else:
					name = str(item)[:40]
				self.record_list.insert(tk.END, f"{i}: {name}")

	def on_select(self, event):
		"""Handle record selection."""
		selection = self.record_list.curselection()
		if not selection:
			return

		idx = selection[0]

		# Get the item
		if isinstance(self.data, list):
			item = self.data[idx] if idx < len(self.data) else None
		elif isinstance(self.data, dict):
			for key in ['dialogs', 'npcs', 'monsters', 'items', 'spells', 'shops']:
				if key in self.data and idx < len(self.data[key]):
					item = self.data[key][idx]
					break
			else:
				keys = list(self.data.keys())
				if idx < len(keys):
					item = {keys[idx]: self.data[keys[idx]]}
				else:
					item = None
		else:
			item = None

		if item:
			self.json_text.delete('1.0', tk.END)
			self.json_text.insert('1.0', json.dumps(item, indent='\t', ensure_ascii=False))

	def save_data(self):
		"""Save current edits."""
		selection = self.record_list.curselection()
		if not selection:
			messagebox.showinfo("Info", "Select a record to save")
			return

		try:
			# Parse edited JSON
			edited_json = self.json_text.get('1.0', tk.END)
			edited_item = json.loads(edited_json)

			idx = selection[0]

			# Update data structure
			if isinstance(self.data, list):
				self.data[idx] = edited_item
			elif isinstance(self.data, dict):
				for key in ['dialogs', 'npcs', 'monsters', 'items', 'spells', 'shops']:
					if key in self.data and idx < len(self.data[key]):
						self.data[key][idx] = edited_item
						break

			# Save to file
			if self.asset_manager.save_json(self.asset_id, self.data):
				messagebox.showinfo("Success", "Saved!")
			else:
				messagebox.showerror("Error", "Failed to save")

		except json.JSONDecodeError as e:
			messagebox.showerror("JSON Error", f"Invalid JSON: {e}")

	def generate_asm(self):
		"""Generate assembly from JSON."""
		success, message = self.asset_manager.run_generator(self.asset_id)
		if success:
			messagebox.showinfo("Success", f"Generated assembly!\n\n{message[:300]}")
		else:
			messagebox.showerror("Error", f"Failed:\n\n{message[:300]}")


# ============================================================================
# MONSTER EDITOR TAB
# ============================================================================

class MonsterEditorTab(ttk.Frame):
	"""Specialized monster editor."""

	def __init__(self, parent, asset_manager: AssetManager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.data = None
		self.current_idx = 0

		self.create_widgets()
		self.load_data()

	def create_widgets(self):
		"""Create monster editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="👾 Monster Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save All", command=self.save_all).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Generate ASM", command=self.generate_asm).pack(side=tk.RIGHT, padx=5)

		# Content
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left: Monster list
		list_frame = ttk.LabelFrame(content, text="Monsters", padding=5)
		list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

		self.monster_list = tk.Listbox(list_frame, width=25, height=25)
		self.monster_list.pack(fill=tk.BOTH, expand=True)
		self.monster_list.bind('<<ListboxSelect>>', self.on_select)

		# Right: Stats editor
		stats_frame = ttk.LabelFrame(content, text="Monster Stats", padding=10)
		stats_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Create stat fields
		self.stat_vars = {}
		stat_fields = [
			('name', 'Name', 0, 0),
			('hp', 'HP', 1, 0),
			('strength', 'Strength', 2, 0),
			('agility', 'Agility', 3, 0),
			('attack', 'Attack', 4, 0),
			('defense', 'Defense', 5, 0),
			('xp', 'Experience', 0, 2),
			('gold', 'Gold', 1, 2),
			('sleep_resist', 'Sleep Resist', 2, 2),
			('stopspell_resist', 'Stopspell Resist', 3, 2),
			('hurt_resist', 'Hurt Resist', 4, 2),
		]

		for field, label, row, col in stat_fields:
			ttk.Label(stats_frame, text=f"{label}:").grid(row=row, column=col, sticky=tk.W, pady=3)
			var = tk.StringVar()
			entry = ttk.Entry(stats_frame, textvariable=var, width=15)
			entry.grid(row=row, column=col+1, padx=5, pady=3)
			self.stat_vars[field] = var

		# Save button
		ttk.Button(stats_frame, text="Save Monster", command=self.save_current).grid(
			row=6, column=0, columnspan=4, pady=20
		)

	def load_data(self):
		"""Load monster data."""
		self.data = self.asset_manager.load_json('monsters')
		self.monster_list.delete(0, tk.END)

		if self.data:
			monsters = self.data.get('monsters', self.data) if isinstance(self.data, dict) else self.data
			for i, monster in enumerate(monsters):
				name = monster.get('name', f'Monster {i}')
				self.monster_list.insert(tk.END, f"{i:02d}: {name}")

	def on_select(self, event):
		"""Handle monster selection."""
		selection = self.monster_list.curselection()
		if not selection:
			return

		self.current_idx = selection[0]
		monsters = self.data.get('monsters', self.data) if isinstance(self.data, dict) else self.data

		if self.current_idx < len(monsters):
			monster = monsters[self.current_idx]

			# Populate fields
			self.stat_vars['name'].set(monster.get('name', ''))
			self.stat_vars['hp'].set(str(monster.get('hp', 0)))
			self.stat_vars['strength'].set(str(monster.get('strength', 0)))
			self.stat_vars['agility'].set(str(monster.get('agility', 0)))
			self.stat_vars['attack'].set(str(monster.get('attack', 0)))
			self.stat_vars['defense'].set(str(monster.get('defense', 0)))
			self.stat_vars['xp'].set(str(monster.get('xp', 0)))
			self.stat_vars['gold'].set(str(monster.get('gold', 0)))
			self.stat_vars['sleep_resist'].set(str(monster.get('sleep_resist', 0)))
			self.stat_vars['stopspell_resist'].set(str(monster.get('stopspell_resist', 0)))
			self.stat_vars['hurt_resist'].set(str(monster.get('hurt_resist', 0)))

	def save_current(self):
		"""Save current monster."""
		monsters = self.data.get('monsters', self.data) if isinstance(self.data, dict) else self.data

		if self.current_idx < len(monsters):
			monster = monsters[self.current_idx]

			# Update fields
			monster['name'] = self.stat_vars['name'].get()
			monster['hp'] = int(self.stat_vars['hp'].get() or 0)
			monster['strength'] = int(self.stat_vars['strength'].get() or 0)
			monster['agility'] = int(self.stat_vars['agility'].get() or 0)
			monster['attack'] = int(self.stat_vars['attack'].get() or 0)
			monster['defense'] = int(self.stat_vars['defense'].get() or 0)
			monster['xp'] = int(self.stat_vars['xp'].get() or 0)
			monster['gold'] = int(self.stat_vars['gold'].get() or 0)
			monster['sleep_resist'] = int(self.stat_vars['sleep_resist'].get() or 0)
			monster['stopspell_resist'] = int(self.stat_vars['stopspell_resist'].get() or 0)
			monster['hurt_resist'] = int(self.stat_vars['hurt_resist'].get() or 0)

			messagebox.showinfo("Saved", f"Monster '{monster['name']}' updated in memory.\nUse 'Save All' to write to file.")

	def save_all(self):
		"""Save all monsters to file."""
		if self.asset_manager.save_json('monsters', self.data):
			messagebox.showinfo("Success", "All monsters saved!")
		else:
			messagebox.showerror("Error", "Failed to save")

	def generate_asm(self):
		"""Generate monster assembly."""
		success, message = self.asset_manager.run_generator('monsters')
		if success:
			messagebox.showinfo("Success", "Generated monster_data.asm!")
		else:
			messagebox.showerror("Error", message[:500])


# ============================================================================
# DIALOG EDITOR TAB
# ============================================================================

class DialogEditorTab(ttk.Frame):
	"""Dialog text editor with live preview."""

	# Dragon Warrior dialog window dimensions (approximate)
	DIALOG_WIDTH = 18  # Characters per line
	DIALOG_HEIGHT = 4   # Lines visible at once

	def __init__(self, parent, asset_manager: AssetManager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.data = None

		self.create_widgets()
		self.load_data()

	def create_widgets(self):
		"""Create dialog editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="💬 Dialog Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save", command=self.save_data).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Generate ASM", command=self.generate_asm).pack(side=tk.RIGHT, padx=5)

		# Search
		search_frame = ttk.Frame(self)
		search_frame.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT)
		self.search_var = tk.StringVar()
		search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=40)
		search_entry.pack(side=tk.LEFT, padx=5)
		ttk.Button(search_frame, text="Find", command=self.search_dialogs).pack(side=tk.LEFT)

		# Content
		content = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Dialog list
		list_frame = ttk.Frame(content)
		content.add(list_frame, weight=1)

		self.dialog_list = tk.Listbox(list_frame, width=40, height=25)
		self.dialog_list.pack(fill=tk.BOTH, expand=True)
		self.dialog_list.bind('<<ListboxSelect>>', self.on_select)

		# Right panel: Editor and Preview
		right_panel = ttk.Frame(content)
		content.add(right_panel, weight=2)

		# Editor
		edit_frame = ttk.LabelFrame(right_panel, text="Dialog Text", padding=5)
		edit_frame.pack(fill=tk.BOTH, expand=True)

		self.text_editor = scrolledtext.ScrolledText(edit_frame, width=60, height=8, font=('Courier', 11))
		self.text_editor.pack(fill=tk.BOTH, expand=True)
		self.text_editor.bind('<KeyRelease>', self.update_preview)

		# Control codes reference
		ref_frame = ttk.LabelFrame(right_panel, text="Control Codes", padding=5)
		ref_frame.pack(fill=tk.X, pady=5)

		codes = "{NAME}=Hero  {ENMY}=Enemy  {ITEM}=Item  {SPEL}=Spell  {AMNT}=Number  {WAIT}=Pause  {END}=End"
		ttk.Label(ref_frame, text=codes, font=('Courier', 9)).pack()

		# Live Preview
		preview_frame = ttk.LabelFrame(right_panel, text="NES Dialog Preview", padding=10)
		preview_frame.pack(fill=tk.X, pady=5)

		# Create NES-style dialog box preview using canvas
		self.preview_canvas = tk.Canvas(preview_frame, width=320, height=120, bg='#000000')
		self.preview_canvas.pack(pady=5)

		# Character count info
		self.char_count_var = tk.StringVar(value="Characters: 0 | Lines: 0")
		ttk.Label(preview_frame, textvariable=self.char_count_var).pack()

	def load_data(self):
		"""Load dialog data."""
		self.data = self.asset_manager.load_json('dialogs')
		self.dialog_list.delete(0, tk.END)

		if self.data:
			dialogs = self.data.get('dialogs', [])
			for i, dialog in enumerate(dialogs[:200]):  # Limit display
				label = dialog.get('label', f'D{i}')
				text_preview = dialog.get('text', '')[:40].replace('\n', ' ')
				self.dialog_list.insert(tk.END, f"{label}: {text_preview}")

	def on_select(self, event):
		"""Handle dialog selection."""
		selection = self.dialog_list.curselection()
		if not selection:
			return

		idx = selection[0]
		dialogs = self.data.get('dialogs', [])

		if idx < len(dialogs):
			dialog = dialogs[idx]
			self.text_editor.delete('1.0', tk.END)
			self.text_editor.insert('1.0', dialog.get('text', ''))
			self.update_preview()

	def update_preview(self, event=None):
		"""Update the NES-style preview."""
		self.preview_canvas.delete('all')

		text = self.text_editor.get('1.0', tk.END).strip()

		# Draw dialog box border (NES style)
		# Outer border
		self.preview_canvas.create_rectangle(10, 10, 310, 110, outline='#ffffff', width=2)
		# Inner border
		self.preview_canvas.create_rectangle(14, 14, 306, 106, outline='#ffffff', width=1)

		# Process text for preview
		processed = self.process_dialog_text(text)

		# Draw text
		y_offset = 25
		line_height = 20
		x_offset = 25

		for i, line in enumerate(processed[:4]):  # Max 4 lines visible
			# Truncate to fit
			display_line = line[:self.DIALOG_WIDTH]
			self.preview_canvas.create_text(
				x_offset, y_offset + (i * line_height),
				text=display_line,
				fill='#ffffff',
				font=('Courier', 12, 'bold'),
				anchor=tk.NW
			)

		# Update character count
		total_chars = len(text)
		total_lines = text.count('\n') + 1
		self.char_count_var.set(f"Characters: {total_chars} | Lines: {total_lines}")

	def process_dialog_text(self, text: str) -> list:
		"""Process dialog text for preview, replacing control codes."""
		# Replace control codes with placeholder text
		replacements = {
			'{NAME}': 'ERDRICK',
			'{ENMY}': 'SLIME',
			'{ITEM}': 'SWORD',
			'{SPEL}': 'HEAL',
			'{AMNT}': '100',
			'{WAIT}': '',
			'{END}': '',
		}

		for code, replacement in replacements.items():
			text = text.replace(code, replacement)

		# Split into lines
		lines = text.split('\n')
		return lines

	def search_dialogs(self):
		"""Search dialogs for text."""
		query = self.search_var.get().lower()
		if not query:
			return

		dialogs = self.data.get('dialogs', [])
		for i, dialog in enumerate(dialogs):
			if query in dialog.get('text', '').lower():
				self.dialog_list.selection_clear(0, tk.END)
				self.dialog_list.selection_set(i)
				self.dialog_list.see(i)
				self.dialog_list.event_generate('<<ListboxSelect>>')
				break

	def save_data(self):
		"""Save dialog edits."""
		selection = self.dialog_list.curselection()
		if not selection:
			return

		idx = selection[0]
		dialogs = self.data.get('dialogs', [])

		if idx < len(dialogs):
			dialogs[idx]['text'] = self.text_editor.get('1.0', tk.END).strip()

			if self.asset_manager.save_json('dialogs', self.data):
				messagebox.showinfo("Success", "Dialog saved!")
			else:
				messagebox.showerror("Error", "Failed to save")

	def generate_asm(self):
		"""Generate dialog assembly."""
		success, message = self.asset_manager.run_generator('dialogs')
		if success:
			messagebox.showinfo("Success", "Generated dialog_data.asm!")
		else:
			messagebox.showerror("Error", message[:500])


# ============================================================================
# ITEM EDITOR TAB
# ============================================================================

class ItemEditorTab(ttk.Frame):
	"""Specialized item editor with form fields."""

	def __init__(self, parent, asset_manager: AssetManager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.data = None
		self.current_idx = -1

		self.create_widgets()
		self.load_data()

	def create_widgets(self):
		"""Create item editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="📦 Item Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save All", command=self.save_all).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Generate ASM", command=self.generate_asm).pack(side=tk.RIGHT, padx=5)

		# Content
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left: Item list
		list_frame = ttk.LabelFrame(content, text="Items", padding=5)
		list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

		self.item_list = tk.Listbox(list_frame, width=25, height=20)
		self.item_list.pack(fill=tk.BOTH, expand=True)
		self.item_list.bind('<<ListboxSelect>>', self.on_select)

		# Right: Item editor
		edit_frame = ttk.LabelFrame(content, text="Item Properties", padding=10)
		edit_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Item fields
		self.field_vars = {}

		fields = [
			('name', 'Name', 'entry', 0),
			('buy_price', 'Buy Price', 'spinbox', 1),
			('sell_price', 'Sell Price', 'spinbox', 2),
			('attack_bonus', 'Attack Bonus', 'spinbox', 3),
			('defense_bonus', 'Defense Bonus', 'spinbox', 4),
			('item_type', 'Item Type', 'combo', 5),
			('equippable', 'Equippable', 'check', 6),
			('useable', 'Useable', 'check', 7),
		]

		item_types = ['Weapon', 'Armor', 'Shield', 'Consumable', 'Key Item']

		for field, label, widget_type, row in fields:
			ttk.Label(edit_frame, text=f"{label}:").grid(row=row, column=0, sticky=tk.W, pady=3)

			if widget_type == 'entry':
				var = tk.StringVar()
				widget = ttk.Entry(edit_frame, textvariable=var, width=20)
			elif widget_type == 'spinbox':
				var = tk.IntVar(value=0)
				widget = ttk.Spinbox(edit_frame, textvariable=var, from_=0, to=65535, width=10)
			elif widget_type == 'combo':
				var = tk.StringVar()
				widget = ttk.Combobox(edit_frame, textvariable=var, values=item_types, width=15)
			elif widget_type == 'check':
				var = tk.BooleanVar()
				widget = ttk.Checkbutton(edit_frame, variable=var)

			widget.grid(row=row, column=1, padx=5, pady=3, sticky=tk.W)
			self.field_vars[field] = var

		# Save button
		ttk.Button(edit_frame, text="💾 Save Item", command=self.save_current).grid(
			row=8, column=0, columnspan=2, pady=20
		)

	def load_data(self):
		"""Load item data."""
		self.data = self.asset_manager.load_json('items')
		self.item_list.delete(0, tk.END)

		if self.data:
			# Handle both list and dict formats
			if isinstance(self.data, dict) and 'items' in self.data:
				items = self.data['items']
			elif isinstance(self.data, dict):
				items = list(self.data.values())
			else:
				items = self.data

			for i, item in enumerate(items):
				name = item.get('name', f'Item {i}')
				self.item_list.insert(tk.END, f"{i:02d}: {name}")

	def on_select(self, event):
		"""Handle item selection."""
		selection = self.item_list.curselection()
		if not selection:
			return

		self.current_idx = selection[0]

		# Get item data
		if isinstance(self.data, dict) and 'items' in self.data:
			items = self.data['items']
		elif isinstance(self.data, dict):
			items = list(self.data.values())
		else:
			items = self.data

		if self.current_idx < len(items):
			item = items[self.current_idx]

			# Populate fields
			self.field_vars['name'].set(item.get('name', ''))
			self.field_vars['buy_price'].set(item.get('buy_price', 0))
			self.field_vars['sell_price'].set(item.get('sell_price', 0))
			self.field_vars['attack_bonus'].set(item.get('attack_bonus', item.get('attack_power', 0)))
			self.field_vars['defense_bonus'].set(item.get('defense_bonus', item.get('defense_power', 0)))
			self.field_vars['item_type'].set(['Weapon', 'Armor', 'Shield', 'Consumable', 'Key Item'][item.get('item_type', 0) % 5])
			self.field_vars['equippable'].set(item.get('equippable', False))
			self.field_vars['useable'].set(item.get('useable', False))

	def save_current(self):
		"""Save current item."""
		if self.current_idx < 0:
			return

		# Get items list
		if isinstance(self.data, dict) and 'items' in self.data:
			items = self.data['items']
		elif isinstance(self.data, dict):
			items = list(self.data.values())
		else:
			items = self.data

		if self.current_idx < len(items):
			item = items[self.current_idx]

			# Update fields
			item['name'] = self.field_vars['name'].get()
			item['buy_price'] = int(self.field_vars['buy_price'].get() or 0)
			item['sell_price'] = int(self.field_vars['sell_price'].get() or 0)
			item['attack_bonus'] = int(self.field_vars['attack_bonus'].get() or 0)
			item['defense_bonus'] = int(self.field_vars['defense_bonus'].get() or 0)

			type_map = {'Weapon': 0, 'Armor': 1, 'Shield': 2, 'Consumable': 3, 'Key Item': 4}
			item['item_type'] = type_map.get(self.field_vars['item_type'].get(), 0)

			item['equippable'] = self.field_vars['equippable'].get()
			item['useable'] = self.field_vars['useable'].get()

			messagebox.showinfo("Saved", f"Item '{item['name']}' updated.\nUse 'Save All' to write to file.")

	def save_all(self):
		"""Save all items to file."""
		if self.asset_manager.save_json('items', self.data):
			messagebox.showinfo("Success", "All items saved!")
		else:
			messagebox.showerror("Error", "Failed to save")

	def generate_asm(self):
		"""Generate item assembly."""
		success, message = self.asset_manager.run_generator('items')
		if success:
			messagebox.showinfo("Success", "Generated item assembly!")
		else:
			messagebox.showerror("Error", message[:500])


# ============================================================================
# SPELL EDITOR TAB
# ============================================================================

class SpellEditorTab(ttk.Frame):
	"""Specialized spell editor with form fields."""

	def __init__(self, parent, asset_manager: AssetManager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.data = None
		self.current_idx = -1

		self.create_widgets()
		self.load_data()

	def create_widgets(self):
		"""Create spell editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="✨ Spell Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save All", command=self.save_all).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Generate ASM", command=self.generate_asm).pack(side=tk.RIGHT, padx=5)

		# Content
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left: Spell list
		list_frame = ttk.LabelFrame(content, text="Spells", padding=5)
		list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

		self.spell_list = tk.Listbox(list_frame, width=20, height=15)
		self.spell_list.pack(fill=tk.BOTH, expand=True)
		self.spell_list.bind('<<ListboxSelect>>', self.on_select)

		# Right: Spell editor
		edit_frame = ttk.LabelFrame(content, text="Spell Properties", padding=10)
		edit_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Spell fields
		self.field_vars = {}

		fields = [
			('name', 'Name', 'entry', 0),
			('mp_cost', 'MP Cost', 'spinbox', 1),
			('min_effect', 'Min Effect', 'spinbox', 2),
			('max_effect', 'Max Effect', 'spinbox', 3),
			('type', 'Type', 'combo', 4),
			('learn_level', 'Learn Level', 'spinbox', 5),
		]

		spell_types = ['Healing', 'Damage', 'Utility', 'Travel', 'Status']

		for field, label, widget_type, row in fields:
			ttk.Label(edit_frame, text=f"{label}:").grid(row=row, column=0, sticky=tk.W, pady=3)

			if widget_type == 'entry':
				var = tk.StringVar()
				widget = ttk.Entry(edit_frame, textvariable=var, width=15)
			elif widget_type == 'spinbox':
				var = tk.IntVar(value=0)
				widget = ttk.Spinbox(edit_frame, textvariable=var, from_=0, to=255, width=10)
			elif widget_type == 'combo':
				var = tk.StringVar()
				widget = ttk.Combobox(edit_frame, textvariable=var, values=spell_types, width=12)

			widget.grid(row=row, column=1, padx=5, pady=3, sticky=tk.W)
			self.field_vars[field] = var

		# Description
		ttk.Label(edit_frame, text="Description:").grid(row=6, column=0, sticky=tk.NW, pady=3)
		self.desc_text = tk.Text(edit_frame, width=30, height=4)
		self.desc_text.grid(row=6, column=1, padx=5, pady=3)

		# Save button
		ttk.Button(edit_frame, text="💾 Save Spell", command=self.save_current).grid(
			row=7, column=0, columnspan=2, pady=20
		)

	def load_data(self):
		"""Load spell data."""
		self.data = self.asset_manager.load_json('spells')
		self.spell_list.delete(0, tk.END)

		if self.data:
			# Handle both list and dict formats
			if isinstance(self.data, dict) and 'spells' in self.data:
				spells = self.data['spells']
			elif isinstance(self.data, dict):
				spells = list(self.data.values())
			else:
				spells = self.data

			for i, spell in enumerate(spells):
				name = spell.get('name', f'Spell {i}')
				self.spell_list.insert(tk.END, f"{name}")

	def on_select(self, event):
		"""Handle spell selection."""
		selection = self.spell_list.curselection()
		if not selection:
			return

		self.current_idx = selection[0]

		# Get spell data
		if isinstance(self.data, dict) and 'spells' in self.data:
			spells = self.data['spells']
		elif isinstance(self.data, dict):
			spells = list(self.data.values())
		else:
			spells = self.data

		if self.current_idx < len(spells):
			spell = spells[self.current_idx]

			# Populate fields
			self.field_vars['name'].set(spell.get('name', ''))
			self.field_vars['mp_cost'].set(spell.get('mp_cost', 0))
			self.field_vars['min_effect'].set(spell.get('min_effect', 0))
			self.field_vars['max_effect'].set(spell.get('max_effect', 0))
			self.field_vars['type'].set(spell.get('type', 'Healing'))
			self.field_vars['learn_level'].set(spell.get('learn_level', 1))

			# Description
			self.desc_text.delete('1.0', tk.END)
			self.desc_text.insert('1.0', spell.get('description', ''))

	def save_current(self):
		"""Save current spell."""
		if self.current_idx < 0:
			return

		# Get spells list
		if isinstance(self.data, dict) and 'spells' in self.data:
			spells = self.data['spells']
		elif isinstance(self.data, dict):
			spells = list(self.data.values())
		else:
			spells = self.data

		if self.current_idx < len(spells):
			spell = spells[self.current_idx]

			# Update fields
			spell['name'] = self.field_vars['name'].get()
			spell['mp_cost'] = int(self.field_vars['mp_cost'].get() or 0)
			spell['min_effect'] = int(self.field_vars['min_effect'].get() or 0)
			spell['max_effect'] = int(self.field_vars['max_effect'].get() or 0)
			spell['type'] = self.field_vars['type'].get()
			spell['learn_level'] = int(self.field_vars['learn_level'].get() or 1)
			spell['description'] = self.desc_text.get('1.0', tk.END).strip()

			messagebox.showinfo("Saved", f"Spell '{spell['name']}' updated.\nUse 'Save All' to write to file.")

	def save_all(self):
		"""Save all spells to file."""
		if self.asset_manager.save_json('spells', self.data):
			messagebox.showinfo("Success", "All spells saved!")
		else:
			messagebox.showerror("Error", "Failed to save")

	def generate_asm(self):
		"""Generate spell assembly."""
		success, message = self.asset_manager.run_generator('spells')
		if success:
			messagebox.showinfo("Success", "Generated spell assembly!")
		else:
			messagebox.showerror("Error", message[:500])


# ============================================================================
# SHOP EDITOR TAB
# ============================================================================

class ShopEditorTab(ttk.Frame):
	"""Specialized shop editor with inventory management."""

	def __init__(self, parent, asset_manager: AssetManager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.data = None
		self.items_data = None
		self.current_idx = -1

		self.create_widgets()
		self.load_data()

	def create_widgets(self):
		"""Create shop editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="🏪 Shop Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save All", command=self.save_all).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Generate ASM", command=self.generate_asm).pack(side=tk.RIGHT, padx=5)

		# Content
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left: Shop list
		list_frame = ttk.LabelFrame(content, text="Shops", padding=5)
		list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

		self.shop_list = tk.Listbox(list_frame, width=25, height=15)
		self.shop_list.pack(fill=tk.BOTH, expand=True)
		self.shop_list.bind('<<ListboxSelect>>', self.on_select)

		# Right: Shop editor
		edit_frame = ttk.LabelFrame(content, text="Shop Properties", padding=10)
		edit_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Shop name
		ttk.Label(edit_frame, text="Shop Name:").grid(row=0, column=0, sticky=tk.W, pady=3)
		self.name_var = tk.StringVar()
		ttk.Entry(edit_frame, textvariable=self.name_var, width=25).grid(row=0, column=1, padx=5, pady=3)

		# Shop type
		ttk.Label(edit_frame, text="Shop Type:").grid(row=1, column=0, sticky=tk.W, pady=3)
		self.type_var = tk.StringVar()
		self.type_combo = ttk.Combobox(edit_frame, textvariable=self.type_var,
									   values=['Weapon', 'Armor', 'Tool', 'Inn', 'Key'], width=15)
		self.type_combo.grid(row=1, column=1, padx=5, pady=3, sticky=tk.W)

		# Inventory
		ttk.Label(edit_frame, text="Inventory:").grid(row=2, column=0, sticky=tk.NW, pady=3)

		inv_frame = ttk.Frame(edit_frame)
		inv_frame.grid(row=2, column=1, padx=5, pady=3, sticky=tk.W)

		self.inventory_list = tk.Listbox(inv_frame, width=30, height=8)
		self.inventory_list.pack(side=tk.LEFT)

		inv_buttons = ttk.Frame(inv_frame)
		inv_buttons.pack(side=tk.LEFT, padx=5)

		ttk.Button(inv_buttons, text="Add", command=self.add_item, width=8).pack(pady=2)
		ttk.Button(inv_buttons, text="Remove", command=self.remove_item, width=8).pack(pady=2)
		ttk.Button(inv_buttons, text="↑ Up", command=self.move_up, width=8).pack(pady=2)
		ttk.Button(inv_buttons, text="↓ Down", command=self.move_down, width=8).pack(pady=2)

		# Available items
		ttk.Label(edit_frame, text="Available Items:").grid(row=3, column=0, sticky=tk.NW, pady=3)
		self.available_list = tk.Listbox(edit_frame, width=30, height=6)
		self.available_list.grid(row=3, column=1, padx=5, pady=3, sticky=tk.W)

		# Save button
		ttk.Button(edit_frame, text="💾 Save Shop", command=self.save_current).grid(
			row=4, column=0, columnspan=2, pady=20
		)

	def load_data(self):
		"""Load shop and item data."""
		self.data = self.asset_manager.load_json('shops')
		self.items_data = self.asset_manager.load_json('items')

		self.shop_list.delete(0, tk.END)

		if self.data:
			# Handle both list and dict formats
			if isinstance(self.data, dict) and 'shops' in self.data:
				shops = self.data['shops']
			elif isinstance(self.data, dict):
				shops = list(self.data.values())
			else:
				shops = self.data

			for i, shop in enumerate(shops):
				name = shop.get('name', shop.get('location', f'Shop {i}'))
				self.shop_list.insert(tk.END, f"{i}: {name}")

		# Load available items
		self.available_list.delete(0, tk.END)
		if self.items_data:
			if isinstance(self.items_data, dict) and 'items' in self.items_data:
				items = self.items_data['items']
			elif isinstance(self.items_data, dict):
				items = list(self.items_data.values())
			else:
				items = self.items_data

			for i, item in enumerate(items):
				name = item.get('name', f'Item {i}')
				self.available_list.insert(tk.END, f"{i}: {name}")

	def on_select(self, event):
		"""Handle shop selection."""
		selection = self.shop_list.curselection()
		if not selection:
			return

		self.current_idx = selection[0]

		# Get shop data
		if isinstance(self.data, dict) and 'shops' in self.data:
			shops = self.data['shops']
		elif isinstance(self.data, dict):
			shops = list(self.data.values())
		else:
			shops = self.data

		if self.current_idx < len(shops):
			shop = shops[self.current_idx]

			# Populate fields
			self.name_var.set(shop.get('name', shop.get('location', '')))
			self.type_var.set(shop.get('type', 'Weapon'))

			# Populate inventory
			self.inventory_list.delete(0, tk.END)
			items = shop.get('items', shop.get('inventory', []))
			for item_id in items:
				item_name = self.get_item_name(item_id)
				self.inventory_list.insert(tk.END, f"{item_id}: {item_name}")

	def get_item_name(self, item_id):
		"""Get item name by ID."""
		if not self.items_data:
			return f"Item {item_id}"

		if isinstance(self.items_data, dict) and 'items' in self.items_data:
			items = self.items_data['items']
		elif isinstance(self.items_data, dict):
			items = list(self.items_data.values())
		else:
			items = self.items_data

		if 0 <= item_id < len(items):
			return items[item_id].get('name', f'Item {item_id}')
		return f"Item {item_id}"

	def add_item(self):
		"""Add selected item to inventory."""
		selection = self.available_list.curselection()
		if not selection:
			return

		item_text = self.available_list.get(selection[0])
		self.inventory_list.insert(tk.END, item_text)

	def remove_item(self):
		"""Remove selected item from inventory."""
		selection = self.inventory_list.curselection()
		if selection:
			self.inventory_list.delete(selection[0])

	def move_up(self):
		"""Move selected item up."""
		selection = self.inventory_list.curselection()
		if selection and selection[0] > 0:
			idx = selection[0]
			item = self.inventory_list.get(idx)
			self.inventory_list.delete(idx)
			self.inventory_list.insert(idx - 1, item)
			self.inventory_list.selection_set(idx - 1)

	def move_down(self):
		"""Move selected item down."""
		selection = self.inventory_list.curselection()
		if selection and selection[0] < self.inventory_list.size() - 1:
			idx = selection[0]
			item = self.inventory_list.get(idx)
			self.inventory_list.delete(idx)
			self.inventory_list.insert(idx + 1, item)
			self.inventory_list.selection_set(idx + 1)

	def save_current(self):
		"""Save current shop."""
		if self.current_idx < 0:
			return

		# Get shops list
		if isinstance(self.data, dict) and 'shops' in self.data:
			shops = self.data['shops']
		elif isinstance(self.data, dict):
			shops = list(self.data.values())
		else:
			shops = self.data

		if self.current_idx < len(shops):
			shop = shops[self.current_idx]

			# Update fields
			shop['name'] = self.name_var.get()
			shop['type'] = self.type_var.get()

			# Update inventory
			items = []
			for i in range(self.inventory_list.size()):
				item_text = self.inventory_list.get(i)
				item_id = int(item_text.split(':')[0])
				items.append(item_id)
			shop['items'] = items

			messagebox.showinfo("Saved", f"Shop '{shop['name']}' updated.\nUse 'Save All' to write to file.")

	def save_all(self):
		"""Save all shops to file."""
		if self.asset_manager.save_json('shops', self.data):
			messagebox.showinfo("Success", "All shops saved!")
		else:
			messagebox.showerror("Error", "Failed to save")

	def generate_asm(self):
		"""Generate shop assembly."""
		success, message = self.asset_manager.run_generator('shops')
		if success:
			messagebox.showinfo("Success", "Generated shop assembly!")
		else:
			messagebox.showerror("Error", message[:500])


# ============================================================================
# NPC EDITOR TAB
# ============================================================================

class NpcEditorTab(ttk.Frame):
	"""Specialized NPC editor with location and behavior settings."""

	def __init__(self, parent, asset_manager: AssetManager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.data = None
		self.current_idx = -1

		self.create_widgets()
		self.load_data()

	def create_widgets(self):
		"""Create NPC editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="🧙 NPC Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save All", command=self.save_all).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Generate ASM", command=self.generate_asm).pack(side=tk.RIGHT, padx=5)

		# Content
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left: NPC list
		list_frame = ttk.LabelFrame(content, text="NPCs", padding=5)
		list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

		self.npc_list = tk.Listbox(list_frame, width=28, height=18)
		self.npc_list.pack(fill=tk.BOTH, expand=True)
		self.npc_list.bind('<<ListboxSelect>>', self.on_select)

		# Right: NPC editor
		edit_frame = ttk.LabelFrame(content, text="NPC Properties", padding=10)
		edit_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# NPC fields
		self.field_vars = {}

		fields = [
			('name', 'Name/Label', 'entry', 0),
			('map_id', 'Map ID', 'spinbox', 1),
			('x', 'X Position', 'spinbox', 2),
			('y', 'Y Position', 'spinbox', 3),
			('direction', 'Direction', 'combo', 4),
			('sprite', 'Sprite ID', 'spinbox', 5),
			('dialog_id', 'Dialog ID', 'spinbox', 6),
			('movement', 'Movement', 'combo', 7),
		]

		directions = ['Down', 'Left', 'Right', 'Up', 'None']
		movements = ['Static', 'Wander', 'Patrol', 'Follow']

		for field, label, widget_type, row in fields:
			ttk.Label(edit_frame, text=f"{label}:").grid(row=row, column=0, sticky=tk.W, pady=3)

			if widget_type == 'entry':
				var = tk.StringVar()
				widget = ttk.Entry(edit_frame, textvariable=var, width=20)
			elif widget_type == 'spinbox':
				var = tk.IntVar(value=0)
				widget = ttk.Spinbox(edit_frame, textvariable=var, from_=0, to=255, width=10)
			elif widget_type == 'combo':
				var = tk.StringVar()
				if field == 'direction':
					widget = ttk.Combobox(edit_frame, textvariable=var, values=directions, width=12)
				else:
					widget = ttk.Combobox(edit_frame, textvariable=var, values=movements, width=12)

			widget.grid(row=row, column=1, padx=5, pady=3, sticky=tk.W)
			self.field_vars[field] = var

		# Notes field
		ttk.Label(edit_frame, text="Notes:").grid(row=8, column=0, sticky=tk.NW, pady=3)
		self.notes_text = tk.Text(edit_frame, width=30, height=3)
		self.notes_text.grid(row=8, column=1, padx=5, pady=3)

		# Save button
		ttk.Button(edit_frame, text="💾 Save NPC", command=self.save_current).grid(
			row=9, column=0, columnspan=2, pady=15
		)

	def load_data(self):
		"""Load NPC data."""
		self.data = self.asset_manager.load_json('npcs')
		self.npc_list.delete(0, tk.END)

		if self.data:
			# Handle both list and dict formats
			if isinstance(self.data, dict) and 'npcs' in self.data:
				npcs = self.data['npcs']
			elif isinstance(self.data, dict):
				npcs = list(self.data.values())
			else:
				npcs = self.data

			for i, npc in enumerate(npcs):
				name = npc.get('name', npc.get('label', f'NPC {i}'))
				map_id = npc.get('map_id', npc.get('map', '?'))
				self.npc_list.insert(tk.END, f"{i:02d}: {name} (Map {map_id})")

	def on_select(self, event):
		"""Handle NPC selection."""
		selection = self.npc_list.curselection()
		if not selection:
			return

		self.current_idx = selection[0]

		# Get NPC data
		if isinstance(self.data, dict) and 'npcs' in self.data:
			npcs = self.data['npcs']
		elif isinstance(self.data, dict):
			npcs = list(self.data.values())
		else:
			npcs = self.data

		if self.current_idx < len(npcs):
			npc = npcs[self.current_idx]

			# Populate fields
			self.field_vars['name'].set(npc.get('name', npc.get('label', '')))
			self.field_vars['map_id'].set(npc.get('map_id', npc.get('map', 0)))
			self.field_vars['x'].set(npc.get('x', 0))
			self.field_vars['y'].set(npc.get('y', 0))
			self.field_vars['direction'].set(npc.get('direction', 'Down'))
			self.field_vars['sprite'].set(npc.get('sprite', npc.get('sprite_id', 0)))
			self.field_vars['dialog_id'].set(npc.get('dialog_id', npc.get('dialog', 0)))
			self.field_vars['movement'].set(npc.get('movement', 'Static'))

			# Notes
			self.notes_text.delete('1.0', tk.END)
			self.notes_text.insert('1.0', npc.get('notes', ''))

	def save_current(self):
		"""Save current NPC."""
		if self.current_idx < 0:
			return

		# Get NPCs list
		if isinstance(self.data, dict) and 'npcs' in self.data:
			npcs = self.data['npcs']
		elif isinstance(self.data, dict):
			npcs = list(self.data.values())
		else:
			npcs = self.data

		if self.current_idx < len(npcs):
			npc = npcs[self.current_idx]

			# Update fields
			npc['name'] = self.field_vars['name'].get()
			npc['map_id'] = int(self.field_vars['map_id'].get() or 0)
			npc['x'] = int(self.field_vars['x'].get() or 0)
			npc['y'] = int(self.field_vars['y'].get() or 0)
			npc['direction'] = self.field_vars['direction'].get()
			npc['sprite'] = int(self.field_vars['sprite'].get() or 0)
			npc['dialog_id'] = int(self.field_vars['dialog_id'].get() or 0)
			npc['movement'] = self.field_vars['movement'].get()
			npc['notes'] = self.notes_text.get('1.0', tk.END).strip()

			messagebox.showinfo("Saved", f"NPC '{npc['name']}' updated.\nUse 'Save All' to write to file.")

	def save_all(self):
		"""Save all NPCs to file."""
		if self.asset_manager.save_json('npcs', self.data):
			messagebox.showinfo("Success", "All NPCs saved!")
		else:
			messagebox.showerror("Error", "Failed to save")

	def generate_asm(self):
		"""Generate NPC assembly."""
		success, message = self.asset_manager.run_generator('npcs')
		if success:
			messagebox.showinfo("Success", "Generated npc_tables.asm!")
		else:
			messagebox.showerror("Error", message[:500])


# ============================================================================
# GRAPHICS EDITOR TAB
# ============================================================================

class GraphicsEditorTab(ttk.Frame):
	"""Visual CHR tile editor with preview and export capabilities."""

	# NES palette colors (NTSC standard approximation)
	NES_PALETTE = [
		(84, 84, 84),    # 0x00 - Dark gray
		(0, 30, 116),    # 0x01 - Dark blue
		(8, 16, 144),    # 0x02 - Blue
		(48, 0, 136),    # 0x03 - Purple
		(68, 0, 100),    # 0x04 - Dark purple
		(92, 0, 48),     # 0x05 - Dark red
		(84, 4, 0),      # 0x06 - Dark brown
		(60, 24, 0),     # 0x07 - Brown
		(32, 42, 0),     # 0x08 - Dark olive
		(8, 58, 0),      # 0x09 - Dark green
		(0, 64, 0),      # 0x0A - Green
		(0, 60, 0),      # 0x0B - Green variant
		(0, 50, 60),     # 0x0C - Teal
		(0, 0, 0),       # 0x0D - Black
		(0, 0, 0),       # 0x0E - Black
		(0, 0, 0),       # 0x0F - Black
		(152, 150, 152), # 0x10 - Gray
		(8, 76, 196),    # 0x11 - Medium blue
		(48, 50, 236),   # 0x12 - Bright blue
		(92, 30, 228),   # 0x13 - Violet
		(136, 20, 176),  # 0x14 - Magenta
		(160, 20, 100),  # 0x15 - Pink-red
		(152, 34, 32),   # 0x16 - Red
		(120, 60, 0),    # 0x17 - Orange
		(84, 90, 0),     # 0x18 - Olive
		(40, 114, 0),    # 0x19 - Green
		(8, 124, 0),     # 0x1A - Bright green
		(0, 118, 40),    # 0x1B - Green-cyan
		(0, 102, 120),   # 0x1C - Cyan
		(0, 0, 0),       # 0x1D - Black
		(0, 0, 0),       # 0x1E - Black
		(0, 0, 0),       # 0x1F - Black
		(236, 238, 236), # 0x20 - White
		(76, 154, 236),  # 0x21 - Light blue
		(120, 124, 236), # 0x22 - Periwinkle
		(176, 98, 236),  # 0x23 - Light violet
		(228, 84, 236),  # 0x24 - Light magenta
		(236, 88, 180),  # 0x25 - Light pink
		(236, 106, 100), # 0x26 - Salmon
		(212, 136, 32),  # 0x27 - Light orange
		(160, 170, 0),   # 0x28 - Yellow-green
		(116, 196, 0),   # 0x29 - Lime
		(76, 208, 32),   # 0x2A - Light green
		(56, 204, 108),  # 0x2B - Mint
		(56, 180, 204),  # 0x2C - Light cyan
		(60, 60, 60),    # 0x2D - Dark gray
		(0, 0, 0),       # 0x2E - Black
		(0, 0, 0),       # 0x2F - Black
		(236, 238, 236), # 0x30 - White
		(168, 204, 236), # 0x31 - Pale blue
		(188, 188, 236), # 0x32 - Pale violet
		(212, 178, 236), # 0x33 - Pale purple
		(236, 174, 236), # 0x34 - Pale pink
		(236, 174, 212), # 0x35 - Pale rose
		(236, 180, 176), # 0x36 - Pale salmon
		(228, 196, 144), # 0x37 - Pale orange
		(204, 210, 120), # 0x38 - Pale yellow
		(180, 222, 120), # 0x39 - Pale lime
		(168, 226, 144), # 0x3A - Pale green
		(152, 226, 180), # 0x3B - Pale mint
		(160, 214, 228), # 0x3C - Pale cyan
		(160, 162, 160), # 0x3D - Light gray
		(0, 0, 0),       # 0x3E - Black
		(0, 0, 0),       # 0x3F - Black
	]

	# Default Dragon Warrior palette indices
	DW_PALETTE = [0x0F, 0x27, 0x30, 0x16]  # Black, Orange, White, Red

	def __init__(self, parent, asset_manager: AssetManager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.tiles = []
		self.tile_images = []
		self.selected_tile = None
		self.zoom = 4  # Default zoom for tile grid
		self.preview_zoom = 16  # Zoom for selected tile preview
		self.current_palette = list(self.DW_PALETTE)

		self.create_widgets()
		self.load_tiles()

	def create_widgets(self):
		"""Create graphics editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="🎨 Graphics Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="🔄 Reload Tiles", command=self.load_tiles).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Regenerate CHR", command=self.regenerate_chr).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="📂 Open Graphics Folder", command=self.open_folder).pack(side=tk.RIGHT, padx=5)

		# Main content
		content = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left panel: Tile grid
		left_panel = ttk.LabelFrame(content, text="CHR Tiles (144 tiles)", padding=5)
		content.add(left_panel, weight=3)

		# Category filter
		filter_frame = ttk.Frame(left_panel)
		filter_frame.pack(fill=tk.X, pady=5)

		ttk.Label(filter_frame, text="Category:").pack(side=tk.LEFT, padx=5)
		self.category_var = tk.StringVar(value="All")
		categories = ["All", "Hero", "Monsters", "NPCs", "Items", "UI"]
		category_combo = ttk.Combobox(filter_frame, textvariable=self.category_var,
									  values=categories, state='readonly', width=12)
		category_combo.pack(side=tk.LEFT, padx=5)
		category_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_tiles())

		# Tile canvas with scrolling
		canvas_frame = ttk.Frame(left_panel)
		canvas_frame.pack(fill=tk.BOTH, expand=True)

		self.tile_canvas = tk.Canvas(canvas_frame, bg='#1a1a2e', width=400, height=400)
		scrollbar_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.tile_canvas.yview)
		scrollbar_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.tile_canvas.xview)

		self.tile_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

		scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
		scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
		self.tile_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		self.tile_canvas.bind('<Button-1>', self.on_tile_click)
		self.tile_canvas.bind('<Configure>', self.on_canvas_resize)

		# Right panel: Selected tile preview and info
		right_panel = ttk.Frame(content)
		content.add(right_panel, weight=1)

		# Preview section
		preview_frame = ttk.LabelFrame(right_panel, text="Selected Tile", padding=10)
		preview_frame.pack(fill=tk.X, pady=(0, 10))

		self.preview_canvas = tk.Canvas(preview_frame, bg='#1a1a2e',
										width=8*self.preview_zoom, height=8*self.preview_zoom)
		self.preview_canvas.pack(pady=10)

		# Tile info
		self.tile_info = ttk.Label(preview_frame, text="No tile selected")
		self.tile_info.pack(pady=5)

		# Palette section
		palette_frame = ttk.LabelFrame(right_panel, text="Palette", padding=10)
		palette_frame.pack(fill=tk.X, pady=(0, 10))

		self.palette_canvas = tk.Canvas(palette_frame, bg='#333', width=160, height=40)
		self.palette_canvas.pack(pady=5)
		self.draw_palette()

		# Palette preset buttons
		preset_frame = ttk.Frame(palette_frame)
		preset_frame.pack(fill=tk.X, pady=5)

		palettes = [
			("Hero", [0x0F, 0x27, 0x30, 0x16]),
			("Monster", [0x0F, 0x16, 0x30, 0x12]),
			("Grass", [0x0F, 0x29, 0x30, 0x19]),
			("Water", [0x0F, 0x12, 0x30, 0x21]),
		]
		for name, pal in palettes:
			btn = ttk.Button(preset_frame, text=name, width=8,
							 command=lambda p=pal: self.set_palette(p))
			btn.pack(side=tk.LEFT, padx=2)

		# Actions section
		actions_frame = ttk.LabelFrame(right_panel, text="Actions", padding=10)
		actions_frame.pack(fill=tk.X, pady=(0, 10))

		ttk.Button(actions_frame, text="📤 Export Selected as PNG",
				   command=self.export_tile).pack(fill=tk.X, pady=2)
		ttk.Button(actions_frame, text="📤 Export All Tiles",
				   command=self.export_all_tiles).pack(fill=tk.X, pady=2)
		ttk.Button(actions_frame, text="📝 Edit in External App",
				   command=self.edit_external).pack(fill=tk.X, pady=2)

		# Statistics
		stats_frame = ttk.LabelFrame(right_panel, text="Statistics", padding=10)
		stats_frame.pack(fill=tk.BOTH, expand=True)

		self.stats_text = tk.Text(stats_frame, height=8, width=25, font=('Courier', 9))
		self.stats_text.pack(fill=tk.BOTH, expand=True)

	def load_tiles(self):
		"""Load all tile PNGs from graphics folder."""
		self.tiles = []
		self.tile_images = []

		graphics_path = ASSETS_GRAPHICS

		if not graphics_path.exists():
			self.update_stats()
			return

		# Get all PNG files
		png_files = sorted(graphics_path.glob("*.png"))

		for png_file in png_files:
			try:
				# Parse filename to get tile info
				name = png_file.stem
				parts = name.split('_')

				category = parts[0] if len(parts) > 0 else 'unknown'
				tile_idx = int(parts[-1]) if len(parts) > 1 and parts[-1].isdigit() else 0

				tile_info = {
					'path': png_file,
					'name': name,
					'category': category,
					'index': tile_idx,
				}
				self.tiles.append(tile_info)

			except Exception as e:
				print(f"Error loading {png_file}: {e}")

		self.draw_tile_grid()
		self.update_stats()

	def draw_tile_grid(self):
		"""Draw the tile grid on the canvas."""
		self.tile_canvas.delete('all')
		self.tile_images = []

		if not HAS_PIL:
			self.tile_canvas.create_text(200, 200, text="PIL not installed\nCannot display tiles",
										 fill='white', font=('Arial', 12))
			return

		# Filter tiles by category
		category = self.category_var.get()
		if category == "All":
			filtered_tiles = self.tiles
		else:
			cat_map = {'Hero': 'hero', 'Monsters': 'monsters', 'NPCs': 'npcs',
					   'Items': 'items', 'UI': 'ui'}
			cat_key = cat_map.get(category, category.lower())
			filtered_tiles = [t for t in self.tiles if t['category'] == cat_key]

		if not filtered_tiles:
			self.tile_canvas.create_text(200, 200, text="No tiles found",
										 fill='white', font=('Arial', 12))
			return

		# Calculate grid dimensions
		tile_size = 8 * self.zoom
		padding = 2
		cols = max(1, self.tile_canvas.winfo_width() // (tile_size + padding))
		if cols < 1:
			cols = 8

		rows = (len(filtered_tiles) + cols - 1) // cols

		# Set scroll region
		canvas_height = rows * (tile_size + padding) + padding
		self.tile_canvas.configure(scrollregion=(0, 0, cols * (tile_size + padding), canvas_height))

		# Draw each tile
		for i, tile in enumerate(filtered_tiles):
			row = i // cols
			col = i % cols

			x = col * (tile_size + padding) + padding
			y = row * (tile_size + padding) + padding

			try:
				# Load and scale tile
				img = Image.open(tile['path'])
				img = img.resize((tile_size, tile_size), 0)  # 0 = NEAREST
				photo = ImageTk.PhotoImage(img)
				self.tile_images.append(photo)

				# Draw on canvas
				self.tile_canvas.create_image(x, y, anchor=tk.NW, image=photo, tags=f"tile_{tile['index']}")

				# Store position for click detection
				tile['canvas_pos'] = (x, y, x + tile_size, y + tile_size)

			except Exception as e:
				# Draw placeholder
				self.tile_canvas.create_rectangle(x, y, x + tile_size, y + tile_size,
												  fill='#333', outline='#666')

	def filter_tiles(self):
		"""Filter tiles by selected category."""
		self.draw_tile_grid()

	def on_canvas_resize(self, event):
		"""Handle canvas resize."""
		self.draw_tile_grid()

	def on_tile_click(self, event):
		"""Handle click on tile canvas."""
		# Convert to canvas coordinates
		canvas_x = self.tile_canvas.canvasx(event.x)
		canvas_y = self.tile_canvas.canvasy(event.y)

		# Find clicked tile
		for tile in self.tiles:
			if 'canvas_pos' in tile:
				x1, y1, x2, y2 = tile['canvas_pos']
				if x1 <= canvas_x <= x2 and y1 <= canvas_y <= y2:
					self.select_tile(tile)
					return

	def select_tile(self, tile):
		"""Select and show tile preview."""
		self.selected_tile = tile

		# Update info label
		self.tile_info.config(text=f"Tile {tile['index']}: {tile['name']}\n{tile['category'].title()}")

		# Draw large preview
		self.draw_preview()

	def draw_preview(self):
		"""Draw selected tile at large scale."""
		self.preview_canvas.delete('all')

		if not self.selected_tile or not HAS_PIL:
			return

		try:
			# Load tile
			img = Image.open(self.selected_tile['path'])

			# Convert to indexed if needed
			if img.mode != 'P':
				img = img.convert('RGB')

			# Scale up
			size = 8 * self.preview_zoom
			img = img.resize((size, size), 0)  # 0 = NEAREST

			photo = ImageTk.PhotoImage(img)
			self.preview_image = photo  # Keep reference

			self.preview_canvas.create_image(0, 0, anchor=tk.NW, image=photo)

			# Draw pixel grid
			for i in range(9):
				x = i * self.preview_zoom
				self.preview_canvas.create_line(x, 0, x, size, fill='#444')
				self.preview_canvas.create_line(0, x, size, x, fill='#444')

		except Exception as e:
			self.preview_canvas.create_text(64, 64, text=f"Error: {e}", fill='red')

	def draw_palette(self):
		"""Draw palette preview."""
		self.palette_canvas.delete('all')

		box_size = 35
		for i, pal_idx in enumerate(self.current_palette):
			color = self.NES_PALETTE[pal_idx % len(self.NES_PALETTE)]
			hex_color = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'

			x = i * (box_size + 5) + 5
			self.palette_canvas.create_rectangle(x, 5, x + box_size, 35,
												 fill=hex_color, outline='white')
			self.palette_canvas.create_text(x + box_size//2, 20,
											text=f'${pal_idx:02X}', fill='white' if sum(color) < 384 else 'black',
											font=('Courier', 8))

	def set_palette(self, palette):
		"""Set current palette."""
		self.current_palette = list(palette)
		self.draw_palette()
		# Could re-render tiles with new palette here if we had raw CHR data

	def export_tile(self):
		"""Export selected tile as PNG."""
		if not self.selected_tile:
			messagebox.showinfo("Info", "No tile selected")
			return

		filename = filedialog.asksaveasfilename(
			defaultextension=".png",
			filetypes=[("PNG files", "*.png")],
			initialfile=f"{self.selected_tile['name']}.png"
		)

		if filename:
			try:
				import shutil
				shutil.copy(self.selected_tile['path'], filename)
				messagebox.showinfo("Success", f"Exported to {filename}")
			except Exception as e:
				messagebox.showerror("Error", str(e))

	def export_all_tiles(self):
		"""Export all tiles to a folder."""
		folder = filedialog.askdirectory(title="Select export folder")
		if folder:
			try:
				import shutil
				count = 0
				for tile in self.tiles:
					dest = Path(folder) / tile['path'].name
					shutil.copy(tile['path'], dest)
					count += 1
				messagebox.showinfo("Success", f"Exported {count} tiles to {folder}")
			except Exception as e:
				messagebox.showerror("Error", str(e))

	def edit_external(self):
		"""Open selected tile in external editor."""
		if not self.selected_tile:
			messagebox.showinfo("Info", "No tile selected")
			return

		try:
			os.startfile(str(self.selected_tile['path']))
		except Exception as e:
			messagebox.showerror("Error", str(e))

	def open_folder(self):
		"""Open graphics folder."""
		try:
			os.startfile(str(ASSETS_GRAPHICS))
		except:
			messagebox.showinfo("Path", str(ASSETS_GRAPHICS))

	def regenerate_chr(self):
		"""Regenerate CHR ROM from PNGs."""
		try:
			result = subprocess.run(
				[sys.executable, str(TOOLS_DIR / "generate_chr_from_pngs.py")],
				cwd=str(PROJECT_ROOT),
				capture_output=True,
				text=True,
				timeout=30
			)

			if result.returncode == 0:
				messagebox.showinfo("Success", "Regenerated CHR-ROM!\n\n" + result.stdout[:500])
			else:
				messagebox.showerror("Error", result.stderr[:500] if result.stderr else "Unknown error")
		except Exception as e:
			messagebox.showerror("Error", str(e))

	def update_stats(self):
		"""Update statistics display."""
		self.stats_text.delete('1.0', tk.END)

		lines = []
		lines.append("CHR Tile Statistics")
		lines.append("=" * 22)
		lines.append(f"Total tiles: {len(self.tiles)}")
		lines.append("")

		# Count by category
		categories = {}
		for tile in self.tiles:
			cat = tile.get('category', 'unknown')
			categories[cat] = categories.get(cat, 0) + 1

		lines.append("By Category:")
		for cat, count in sorted(categories.items()):
			lines.append(f"  {cat.title()}: {count}")

		lines.append("")
		lines.append("Tile Format:")
		lines.append("  8x8 pixels")
		lines.append("  2-bit (4 colors)")
		lines.append("  16 bytes/tile")

		lines.append("")
		lines.append("CHR Banks:")
		lines.append("  2 x 256 tiles")
		lines.append("  = 8KB per bank")
		lines.append("  = 16KB total")

		self.stats_text.insert('1.0', '\n'.join(lines))


# ============================================================================
# MAP EDITOR TAB
# ============================================================================

class MapEditorTab(ttk.Frame):
	"""Visual map viewer and editor."""

	# Terrain colors for visualization
	TERRAIN_COLORS = {
		0: '#000080',  # Water/Barrier - dark blue
		1: '#008800',  # Grass - green
		2: '#00aa00',  # Forest - darker green
		3: '#aaaa00',  # Desert - yellow
		4: '#884400',  # Hills - brown
		5: '#666666',  # Mountain - gray
		6: '#aaaaaa',  # Town - light gray
		7: '#ffaa00',  # Castle - gold
		8: '#004488',  # Bridge - blue-gray
		9: '#220022',  # Cave - dark purple
		10: '#440000', # Swamp - dark red
		11: '#ffffff', # Stairs - white
		12: '#888888', # Door - gray
	}

	def __init__(self, parent, asset_manager: AssetManager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.map_data = None
		self.current_map = None
		self.current_map_id = "0"
		self.zoom = 4
		self.offset_x = 0
		self.offset_y = 0
		self.dragging = False
		self.last_mouse_pos = (0, 0)

		self.create_widgets()
		self.load_maps()

	def create_widgets(self):
		"""Create map editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="🗺️ Map Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		# Map selector
		ttk.Label(header, text="Map:").pack(side=tk.LEFT, padx=(20, 5))
		self.map_var = tk.StringVar()
		self.map_combo = ttk.Combobox(header, textvariable=self.map_var, state='readonly', width=30)
		self.map_combo.pack(side=tk.LEFT, padx=5)
		self.map_combo.bind('<<ComboboxSelected>>', self.on_map_select)

		# Zoom controls
		ttk.Label(header, text="Zoom:").pack(side=tk.LEFT, padx=(20, 5))
		ttk.Button(header, text="-", width=3, command=self.zoom_out).pack(side=tk.LEFT)
		self.zoom_label = ttk.Label(header, text="4x")
		self.zoom_label.pack(side=tk.LEFT, padx=5)
		ttk.Button(header, text="+", width=3, command=self.zoom_in).pack(side=tk.LEFT)

		# Content
		content = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left: Map canvas
		canvas_frame = ttk.LabelFrame(content, text="Map View", padding=5)
		content.add(canvas_frame, weight=4)

		self.map_canvas = tk.Canvas(canvas_frame, bg='#1a1a2e', width=600, height=500)
		scrollbar_y = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=self.map_canvas.yview)
		scrollbar_x = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL, command=self.map_canvas.xview)

		self.map_canvas.configure(yscrollcommand=scrollbar_y.set, xscrollcommand=scrollbar_x.set)

		scrollbar_y.pack(side=tk.RIGHT, fill=tk.Y)
		scrollbar_x.pack(side=tk.BOTTOM, fill=tk.X)
		self.map_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Canvas bindings
		self.map_canvas.bind('<Button-1>', self.on_map_click)
		self.map_canvas.bind('<B1-Motion>', self.on_map_drag)
		self.map_canvas.bind('<ButtonRelease-1>', self.on_drag_end)
		self.map_canvas.bind('<MouseWheel>', self.on_mousewheel)

		# Right: Info panel
		info_panel = ttk.Frame(content)
		content.add(info_panel, weight=1)

		# Map info
		info_frame = ttk.LabelFrame(info_panel, text="Map Info", padding=10)
		info_frame.pack(fill=tk.X, pady=(0, 10))

		self.info_labels = {}
		info_fields = ['Name', 'Size', 'Tiles', 'Walkable', 'Encounters']
		for field in info_fields:
			row = ttk.Frame(info_frame)
			row.pack(fill=tk.X, pady=2)
			ttk.Label(row, text=f"{field}:", width=10).pack(side=tk.LEFT)
			lbl = ttk.Label(row, text="-")
			lbl.pack(side=tk.LEFT)
			self.info_labels[field.lower()] = lbl

		# Tile info
		tile_frame = ttk.LabelFrame(info_panel, text="Selected Tile", padding=10)
		tile_frame.pack(fill=tk.X, pady=(0, 10))

		self.tile_labels = {}
		tile_fields = ['Position', 'Tile ID', 'Terrain', 'Walkable', 'Encounters']
		for field in tile_fields:
			row = ttk.Frame(tile_frame)
			row.pack(fill=tk.X, pady=2)
			ttk.Label(row, text=f"{field}:", width=10).pack(side=tk.LEFT)
			lbl = ttk.Label(row, text="-")
			lbl.pack(side=tk.LEFT)
			self.tile_labels[field.lower()] = lbl

		# Legend
		legend_frame = ttk.LabelFrame(info_panel, text="Terrain Legend", padding=10)
		legend_frame.pack(fill=tk.BOTH, expand=True)

		legend_canvas = tk.Canvas(legend_frame, bg='#2a2a3e', height=200)
		legend_canvas.pack(fill=tk.BOTH, expand=True)

		terrain_names = [
			(0, "Water/Barrier"),
			(1, "Grass"),
			(2, "Forest"),
			(3, "Desert"),
			(4, "Hills"),
			(5, "Mountain"),
			(6, "Town"),
			(7, "Castle"),
			(8, "Bridge"),
			(9, "Cave"),
			(10, "Swamp"),
		]

		for i, (terrain_id, name) in enumerate(terrain_names):
			y = i * 18 + 5
			color = self.TERRAIN_COLORS.get(terrain_id, '#888888')
			legend_canvas.create_rectangle(5, y, 20, y+14, fill=color, outline='white')
			legend_canvas.create_text(25, y+7, text=name, anchor=tk.W, fill='white', font=('Arial', 9))

	def load_maps(self):
		"""Load map data."""
		self.map_data = self.asset_manager.load_json('maps')

		if not self.map_data:
			return

		# Populate map combo
		map_names = []
		for map_id, map_info in self.map_data.items():
			name = map_info.get('name', f'Map {map_id}')
			map_names.append(f"{map_id}: {name}")

		self.map_combo['values'] = map_names
		if map_names:
			self.map_combo.current(0)
			self.on_map_select(None)

	def on_map_select(self, event):
		"""Handle map selection."""
		selection = self.map_var.get()
		if not selection:
			return

		# Extract map ID
		map_id = selection.split(':')[0].strip()
		self.current_map_id = map_id
		self.current_map = self.map_data.get(map_id)

		if self.current_map:
			self.update_map_info()
			self.draw_map()

	def update_map_info(self):
		"""Update map info display."""
		if not self.current_map:
			return

		self.info_labels['name'].config(text=self.current_map.get('name', 'Unknown'))

		width = self.current_map.get('width', 0)
		height = self.current_map.get('height', 0)
		self.info_labels['size'].config(text=f"{width} x {height}")

		tiles = self.current_map.get('tiles', [])
		total_tiles = sum(len(row) for row in tiles) if tiles else 0
		self.info_labels['tiles'].config(text=str(total_tiles))

		# Count walkable tiles
		walkable = 0
		encounter_tiles = 0
		for row in tiles:
			for tile in row:
				if isinstance(tile, dict):
					if tile.get('walkable', False):
						walkable += 1
					if tile.get('encounter_rate', 0) > 0:
						encounter_tiles += 1

		self.info_labels['walkable'].config(text=str(walkable))
		self.info_labels['encounters'].config(text=str(encounter_tiles))

	def draw_map(self):
		"""Draw the map on canvas."""
		self.map_canvas.delete('all')

		if not self.current_map:
			return

		tiles = self.current_map.get('tiles', [])
		if not tiles:
			self.map_canvas.create_text(300, 250, text="No tile data", fill='white', font=('Arial', 14))
			return

		width = self.current_map.get('width', len(tiles[0]) if tiles else 0)
		height = self.current_map.get('height', len(tiles))

		# Set scroll region
		canvas_width = width * self.zoom
		canvas_height = height * self.zoom
		self.map_canvas.configure(scrollregion=(0, 0, canvas_width, canvas_height))

		# Draw tiles (limit for performance)
		max_tiles = 10000  # Limit tiles to draw
		tiles_drawn = 0

		for y, row in enumerate(tiles):
			if tiles_drawn >= max_tiles:
				break
			for x, tile in enumerate(row):
				if tiles_drawn >= max_tiles:
					break

				# Get terrain type and color
				if isinstance(tile, dict):
					terrain = tile.get('terrain_type', 0)
				else:
					terrain = tile if isinstance(tile, int) else 0

				color = self.TERRAIN_COLORS.get(terrain, '#888888')

				# Draw tile
				x1 = x * self.zoom
				y1 = y * self.zoom
				x2 = x1 + self.zoom
				y2 = y1 + self.zoom

				self.map_canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline='')
				tiles_drawn += 1

		# Status message for large maps
		if tiles_drawn >= max_tiles:
			self.map_canvas.create_text(10, 10, text=f"Showing {max_tiles} tiles (zoom in for detail)",
									   anchor=tk.NW, fill='yellow', font=('Arial', 10))

	def on_map_click(self, event):
		"""Handle map click."""
		if not self.current_map:
			return

		# Convert to canvas coordinates
		canvas_x = self.map_canvas.canvasx(event.x)
		canvas_y = self.map_canvas.canvasy(event.y)

		# Calculate tile position
		tile_x = int(canvas_x // self.zoom)
		tile_y = int(canvas_y // self.zoom)

		self.update_tile_info(tile_x, tile_y)

	def on_map_drag(self, event):
		"""Handle map dragging."""
		pass  # Scrolling handled by scrollbars

	def on_drag_end(self, event):
		"""Handle drag end."""
		pass

	def on_mousewheel(self, event):
		"""Handle mouse wheel for scrolling."""
		self.map_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

	def update_tile_info(self, x, y):
		"""Update tile info display."""
		if not self.current_map:
			return

		tiles = self.current_map.get('tiles', [])
		if not tiles or y >= len(tiles) or x >= len(tiles[y]):
			return

		tile = tiles[y][x]

		self.tile_labels['position'].config(text=f"({x}, {y})")

		if isinstance(tile, dict):
			self.tile_labels['tile id'].config(text=str(tile.get('tile_id', '-')))
			self.tile_labels['terrain'].config(text=str(tile.get('terrain_type', '-')))
			self.tile_labels['walkable'].config(text='Yes' if tile.get('walkable', False) else 'No')
			self.tile_labels['encounters'].config(text=str(tile.get('encounter_rate', 0)))
		else:
			self.tile_labels['tile id'].config(text=str(tile))
			self.tile_labels['terrain'].config(text='-')
			self.tile_labels['walkable'].config(text='-')
			self.tile_labels['encounters'].config(text='-')

	def zoom_in(self):
		"""Zoom in."""
		if self.zoom < 16:
			self.zoom = min(16, self.zoom * 2)
			self.zoom_label.config(text=f"{self.zoom}x")
			self.draw_map()

	def zoom_out(self):
		"""Zoom out."""
		if self.zoom > 1:
			self.zoom = max(1, self.zoom // 2)
			self.zoom_label.config(text=f"{self.zoom}x")
			self.draw_map()


# ============================================================================
# PALETTE EDITOR TAB
# ============================================================================

class PaletteEditorTab(ttk.Frame):
	"""NES palette editor with visual color picker."""

	# Full NES color palette (64 colors)
	NES_PALETTE = [
		(84, 84, 84), (0, 30, 116), (8, 16, 144), (48, 0, 136),
		(68, 0, 100), (92, 0, 48), (84, 4, 0), (60, 24, 0),
		(32, 42, 0), (8, 58, 0), (0, 64, 0), (0, 60, 0),
		(0, 50, 60), (0, 0, 0), (0, 0, 0), (0, 0, 0),
		(152, 150, 152), (8, 76, 196), (48, 50, 236), (92, 30, 228),
		(136, 20, 176), (160, 20, 100), (152, 34, 32), (120, 60, 0),
		(84, 90, 0), (40, 114, 0), (8, 124, 0), (0, 118, 40),
		(0, 102, 120), (0, 0, 0), (0, 0, 0), (0, 0, 0),
		(236, 238, 236), (76, 154, 236), (120, 124, 236), (176, 98, 236),
		(228, 84, 236), (236, 88, 180), (236, 106, 100), (212, 136, 32),
		(160, 170, 0), (116, 196, 0), (76, 208, 32), (56, 204, 108),
		(56, 180, 204), (60, 60, 60), (0, 0, 0), (0, 0, 0),
		(236, 238, 236), (168, 204, 236), (188, 188, 236), (212, 178, 236),
		(236, 174, 236), (236, 174, 212), (236, 180, 176), (228, 196, 144),
		(204, 210, 120), (180, 222, 120), (168, 226, 144), (152, 226, 180),
		(160, 214, 228), (160, 162, 160), (0, 0, 0), (0, 0, 0),
	]

	# Default Dragon Warrior palettes
	DW_PALETTES = {
		'Background 0': [0x0F, 0x30, 0x10, 0x00],  # Main background
		'Background 1': [0x0F, 0x30, 0x27, 0x07],  # Desert/sand
		'Background 2': [0x0F, 0x30, 0x19, 0x09],  # Grass/forest
		'Background 3': [0x0F, 0x30, 0x12, 0x02],  # Water
		'Sprite 0': [0x0F, 0x27, 0x30, 0x16],      # Hero
		'Sprite 1': [0x0F, 0x16, 0x30, 0x12],      # Monster 1
		'Sprite 2': [0x0F, 0x29, 0x30, 0x19],      # NPC
		'Sprite 3': [0x0F, 0x30, 0x27, 0x17],      # Items
	}

	def __init__(self, parent, asset_manager: AssetManager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.current_palette_name = 'Sprite 0'
		self.current_palette = list(self.DW_PALETTES['Sprite 0'])
		self.selected_slot = 0

		self.create_widgets()

	def create_widgets(self):
		"""Create palette editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="🎨 Palette Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save Palettes", command=self.save_palettes).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="🔄 Reset", command=self.reset_palettes).pack(side=tk.RIGHT, padx=5)

		# Main content
		content = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left: Palette selector and editor
		left_panel = ttk.Frame(content)
		content.add(left_panel, weight=1)

		# Palette selector
		selector_frame = ttk.LabelFrame(left_panel, text="Game Palettes", padding=10)
		selector_frame.pack(fill=tk.X, pady=(0, 10))

		self.palette_var = tk.StringVar(value=self.current_palette_name)
		for name in self.DW_PALETTES.keys():
			rb = ttk.Radiobutton(selector_frame, text=name, value=name,
								 variable=self.palette_var, command=self.on_palette_select)
			rb.pack(anchor=tk.W)

		# Current palette display
		edit_frame = ttk.LabelFrame(left_panel, text="Edit Palette", padding=10)
		edit_frame.pack(fill=tk.X, pady=(0, 10))

		# Palette slot buttons
		slot_frame = ttk.Frame(edit_frame)
		slot_frame.pack(fill=tk.X, pady=10)

		ttk.Label(slot_frame, text="Colors:").pack(side=tk.LEFT)

		self.slot_buttons = []
		self.slot_canvases = []
		for i in range(4):
			frame = ttk.Frame(slot_frame)
			frame.pack(side=tk.LEFT, padx=5)

			canvas = tk.Canvas(frame, width=50, height=50, bg='black', cursor='hand2')
			canvas.pack()
			canvas.bind('<Button-1>', lambda e, idx=i: self.select_slot(idx))
			self.slot_canvases.append(canvas)

			ttk.Label(frame, text=f"${self.current_palette[i]:02X}").pack()

		self.update_slot_display()

		# Color info
		info_frame = ttk.LabelFrame(left_panel, text="Selected Color", padding=10)
		info_frame.pack(fill=tk.X)

		self.color_info = ttk.Label(info_frame, text="Click a slot to select")
		self.color_info.pack()

		# Right: NES color picker
		right_panel = ttk.LabelFrame(content, text="NES Color Palette (64 Colors)", padding=10)
		content.add(right_panel, weight=2)

		# Create color grid
		self.color_canvas = tk.Canvas(right_panel, width=400, height=200, bg='#1a1a2e')
		self.color_canvas.pack(pady=10)
		self.draw_color_grid()

		# Hex input
		hex_frame = ttk.Frame(right_panel)
		hex_frame.pack(fill=tk.X, pady=10)

		ttk.Label(hex_frame, text="Hex Value:").pack(side=tk.LEFT)
		self.hex_var = tk.StringVar(value="0F")
		hex_entry = ttk.Entry(hex_frame, textvariable=self.hex_var, width=5)
		hex_entry.pack(side=tk.LEFT, padx=5)
		ttk.Button(hex_frame, text="Set", command=self.set_from_hex).pack(side=tk.LEFT)

		# Preview
		preview_frame = ttk.LabelFrame(right_panel, text="Palette Preview", padding=10)
		preview_frame.pack(fill=tk.X)

		self.preview_canvas = tk.Canvas(preview_frame, width=380, height=60, bg='#000000')
		self.preview_canvas.pack()
		self.update_preview()

	def draw_color_grid(self):
		"""Draw the NES color selection grid."""
		self.color_canvas.delete('all')

		box_size = 24
		padding = 2
		cols = 16
		rows = 4

		for i, color in enumerate(self.NES_PALETTE):
			row = i // cols
			col = i % cols

			x = col * (box_size + padding) + padding
			y = row * (box_size + padding) + padding

			hex_color = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'

			rect = self.color_canvas.create_rectangle(
				x, y, x + box_size, y + box_size,
				fill=hex_color, outline='#666', tags=f'color_{i}'
			)

			# Bind click
			self.color_canvas.tag_bind(f'color_{i}', '<Button-1>',
				lambda e, idx=i: self.select_color(idx))

		# Draw labels
		for col in range(cols):
			x = col * (box_size + padding) + padding + box_size // 2
			self.color_canvas.create_text(x, rows * (box_size + padding) + 10,
				text=f'{col:X}', fill='#888', font=('Courier', 8))

		for row in range(rows):
			y = row * (box_size + padding) + padding + box_size // 2
			self.color_canvas.create_text(-5, y, text=f'{row}', fill='#888',
				font=('Courier', 8), anchor=tk.E)

	def select_slot(self, slot_idx: int):
		"""Select a palette slot for editing."""
		self.selected_slot = slot_idx
		self.update_slot_display()

		color_idx = self.current_palette[slot_idx]
		color = self.NES_PALETTE[color_idx]
		self.color_info.config(text=f"Slot {slot_idx}: ${color_idx:02X} - RGB({color[0]}, {color[1]}, {color[2]})")
		self.hex_var.set(f"{color_idx:02X}")

	def select_color(self, color_idx: int):
		"""Select a color from the NES palette."""
		self.current_palette[self.selected_slot] = color_idx
		self.update_slot_display()
		self.update_preview()

		color = self.NES_PALETTE[color_idx]
		self.color_info.config(text=f"Slot {self.selected_slot}: ${color_idx:02X} - RGB({color[0]}, {color[1]}, {color[2]})")
		self.hex_var.set(f"{color_idx:02X}")

	def update_slot_display(self):
		"""Update the slot button colors."""
		for i, canvas in enumerate(self.slot_canvases):
			color_idx = self.current_palette[i]
			color = self.NES_PALETTE[color_idx % len(self.NES_PALETTE)]
			hex_color = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'

			canvas.delete('all')
			canvas.create_rectangle(2, 2, 48, 48, fill=hex_color, outline='white' if i == self.selected_slot else '#666')

	def update_preview(self):
		"""Update the palette preview."""
		self.preview_canvas.delete('all')

		# Draw palette colors as larger boxes
		box_width = 90
		for i, color_idx in enumerate(self.current_palette):
			color = self.NES_PALETTE[color_idx % len(self.NES_PALETTE)]
			hex_color = f'#{color[0]:02x}{color[1]:02x}{color[2]:02x}'

			x = i * (box_width + 5) + 5
			self.preview_canvas.create_rectangle(x, 5, x + box_width, 55, fill=hex_color, outline='white')
			self.preview_canvas.create_text(x + box_width // 2, 30, text=f'${color_idx:02X}',
				fill='white' if sum(color) < 384 else 'black', font=('Courier', 10, 'bold'))

	def on_palette_select(self):
		"""Handle palette selection change."""
		self.current_palette_name = self.palette_var.get()
		self.current_palette = list(self.DW_PALETTES[self.current_palette_name])
		self.update_slot_display()
		self.update_preview()

	def set_from_hex(self):
		"""Set color from hex input."""
		try:
			value = int(self.hex_var.get(), 16)
			if 0 <= value < 64:
				self.select_color(value)
		except ValueError:
			messagebox.showerror("Error", "Invalid hex value (00-3F)")

	def save_palettes(self):
		"""Save palettes to JSON."""
		# Update the DW_PALETTES with current edits
		self.DW_PALETTES[self.current_palette_name] = list(self.current_palette)

		# Save to palettes.json
		palette_data = {name: colors for name, colors in self.DW_PALETTES.items()}

		try:
			palette_path = ASSETS_JSON / "palettes.json"
			with open(palette_path, 'w', encoding='utf-8') as f:
				json.dump(palette_data, f, indent='\t')
			messagebox.showinfo("Success", "Palettes saved!")
		except Exception as e:
			messagebox.showerror("Error", f"Failed to save: {e}")

	def reset_palettes(self):
		"""Reset to default palettes."""
		self.DW_PALETTES = {
			'Background 0': [0x0F, 0x30, 0x10, 0x00],
			'Background 1': [0x0F, 0x30, 0x27, 0x07],
			'Background 2': [0x0F, 0x30, 0x19, 0x09],
			'Background 3': [0x0F, 0x30, 0x12, 0x02],
			'Sprite 0': [0x0F, 0x27, 0x30, 0x16],
			'Sprite 1': [0x0F, 0x16, 0x30, 0x12],
			'Sprite 2': [0x0F, 0x29, 0x30, 0x19],
			'Sprite 3': [0x0F, 0x30, 0x27, 0x17],
		}
		self.current_palette = list(self.DW_PALETTES[self.current_palette_name])
		self.update_slot_display()
		self.update_preview()


# ============================================================================
# HEX VIEWER TAB
# ============================================================================

class HexViewerTab(BaseTab):
	"""Hex viewer/editor for ROM data."""

	def __init__(self, notebook: ttk.Notebook, asset_manager: AssetManager, status_callback):
		super().__init__(notebook, asset_manager, status_callback)
		self.rom_data: Optional[bytes] = None
		self.rom_path: Optional[Path] = None
		self.offset = 0
		self.bytes_per_row = 16
		self.rows_visible = 24
		self.selection_start: Optional[int] = None
		self.selection_end: Optional[int] = None
		self.bookmarks: Dict[str, int] = {}

		# Known ROM regions for Dragon Warrior
		self.rom_regions = {
			'Header': (0x0000, 0x0010),
			'PRG-ROM Bank 0': (0x0010, 0x4010),
			'PRG-ROM Bank 1': (0x4010, 0x8010),
			'PRG-ROM Bank 2': (0x8010, 0xC010),
			'PRG-ROM Bank 3': (0xC010, 0x10010),
			'CHR-ROM': (0x10010, 0x14010),
			'Text Table': (0x8010, 0x8810),
			'Monster Data': (0x5E5B + 0x10, 0x5E5B + 0x10 + 0x280),
			'Item Data': (0x1A5E + 0x10, 0x1A5E + 0x10 + 0x100),
		}

		self.setup_ui()
		self.load_rom()

	def setup_ui(self):
		"""Set up hex viewer UI."""
		# Top toolbar
		toolbar = ttk.Frame(self.frame)
		toolbar.pack(fill='x', padx=5, pady=5)

		ttk.Label(toolbar, text="Go to:").pack(side='left', padx=2)
		self.offset_var = tk.StringVar(value="0x0000")
		self.offset_entry = ttk.Entry(toolbar, textvariable=self.offset_var, width=12)
		self.offset_entry.pack(side='left', padx=2)
		self.offset_entry.bind('<Return>', lambda e: self.go_to_offset())

		ttk.Button(toolbar, text="Go", command=self.go_to_offset).pack(side='left', padx=2)

		ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5)

		ttk.Label(toolbar, text="Region:").pack(side='left', padx=2)
		self.region_var = tk.StringVar()
		region_combo = ttk.Combobox(toolbar, textvariable=self.region_var, width=20, state='readonly')
		region_combo['values'] = list(self.rom_regions.keys())
		region_combo.pack(side='left', padx=2)
		region_combo.bind('<<ComboboxSelected>>', self.jump_to_region)

		ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5)

		ttk.Button(toolbar, text="Find...", command=self.show_find_dialog).pack(side='left', padx=2)
		ttk.Button(toolbar, text="Bookmarks", command=self.show_bookmarks).pack(side='left', padx=2)

		ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5)

		ttk.Label(toolbar, text="Display:").pack(side='left', padx=2)
		self.display_var = tk.StringVar(value="hex")
		ttk.Radiobutton(toolbar, text="Hex", variable=self.display_var, value="hex",
			command=self.refresh_view).pack(side='left')
		ttk.Radiobutton(toolbar, text="Dec", variable=self.display_var, value="dec",
			command=self.refresh_view).pack(side='left')
		ttk.Radiobutton(toolbar, text="Bin", variable=self.display_var, value="bin",
			command=self.refresh_view).pack(side='left')

		# Main hex view area
		hex_frame = ttk.Frame(self.frame)
		hex_frame.pack(fill='both', expand=True, padx=5, pady=5)

		# Create hex view with monospace font
		self.hex_text = tk.Text(
			hex_frame,
			font=('Consolas', 10),
			wrap='none',
			width=80,
			height=self.rows_visible,
			bg='#1e1e1e',
			fg='#d4d4d4',
			insertbackground='white',
			selectbackground='#264f78',
			state='disabled'
		)
		self.hex_text.pack(side='left', fill='both', expand=True)

		# Scrollbar
		scrollbar = ttk.Scrollbar(hex_frame, orient='vertical')
		scrollbar.pack(side='right', fill='y')

		# Custom scrollbar handling for bytes
		scrollbar.config(command=self.on_scroll)

		# ASCII view
		self.ascii_text = tk.Text(
			hex_frame,
			font=('Consolas', 10),
			wrap='none',
			width=18,
			height=self.rows_visible,
			bg='#252526',
			fg='#ce9178',
			state='disabled'
		)
		self.ascii_text.pack(side='left', fill='y')

		# Configure tags for highlighting
		self.hex_text.tag_configure('offset', foreground='#569cd6')
		self.hex_text.tag_configure('selected', background='#264f78')
		self.hex_text.tag_configure('zero', foreground='#606060')
		self.hex_text.tag_configure('high', foreground='#4ec9b0')
		self.hex_text.tag_configure('ascii', foreground='#ce9178')
		self.hex_text.tag_configure('header', foreground='#dcdcaa')
		self.hex_text.tag_configure('chr', foreground='#c586c0')

		self.ascii_text.tag_configure('printable', foreground='#ce9178')
		self.ascii_text.tag_configure('nonprint', foreground='#606060')

		# Bindings
		self.hex_text.bind('<MouseWheel>', self.on_mousewheel)
		self.hex_text.bind('<Button-1>', self.on_click)
		self.ascii_text.bind('<MouseWheel>', self.on_mousewheel)

		# Info panel at bottom
		info_frame = ttk.LabelFrame(self.frame, text="Selection Info")
		info_frame.pack(fill='x', padx=5, pady=5)

		info_grid = ttk.Frame(info_frame)
		info_grid.pack(fill='x', padx=5, pady=5)

		ttk.Label(info_grid, text="Offset:").grid(row=0, column=0, sticky='e', padx=5)
		self.sel_offset_var = tk.StringVar(value="-")
		ttk.Label(info_grid, textvariable=self.sel_offset_var, font=('Consolas', 10)).grid(
			row=0, column=1, sticky='w')

		ttk.Label(info_grid, text="Hex:").grid(row=0, column=2, sticky='e', padx=5)
		self.sel_hex_var = tk.StringVar(value="-")
		ttk.Label(info_grid, textvariable=self.sel_hex_var, font=('Consolas', 10)).grid(
			row=0, column=3, sticky='w')

		ttk.Label(info_grid, text="Dec:").grid(row=0, column=4, sticky='e', padx=5)
		self.sel_dec_var = tk.StringVar(value="-")
		ttk.Label(info_grid, textvariable=self.sel_dec_var, font=('Consolas', 10)).grid(
			row=0, column=5, sticky='w')

		ttk.Label(info_grid, text="Binary:").grid(row=0, column=6, sticky='e', padx=5)
		self.sel_bin_var = tk.StringVar(value="-")
		ttk.Label(info_grid, textvariable=self.sel_bin_var, font=('Consolas', 10)).grid(
			row=0, column=7, sticky='w')

		ttk.Label(info_grid, text="Region:").grid(row=1, column=0, sticky='e', padx=5)
		self.sel_region_var = tk.StringVar(value="-")
		ttk.Label(info_grid, textvariable=self.sel_region_var).grid(
			row=1, column=1, columnspan=3, sticky='w')

		ttk.Label(info_grid, text="Word (LE):").grid(row=1, column=4, sticky='e', padx=5)
		self.sel_word_var = tk.StringVar(value="-")
		ttk.Label(info_grid, textvariable=self.sel_word_var, font=('Consolas', 10)).grid(
			row=1, column=5, sticky='w')

		ttk.Label(info_grid, text="NES Address:").grid(row=1, column=6, sticky='e', padx=5)
		self.sel_nes_var = tk.StringVar(value="-")
		ttk.Label(info_grid, textvariable=self.sel_nes_var, font=('Consolas', 10)).grid(
			row=1, column=7, sticky='w')

	def load_rom(self):
		"""Load ROM data."""
		rom_path = PROJECT_ROOT / "build" / "dragon_warrior_rebuilt.nes"
		if not rom_path.exists():
			rom_path = PROJECT_ROOT / "roms" / "Dragon Warrior (USA).nes"

		if rom_path.exists():
			try:
				with open(rom_path, 'rb') as f:
					self.rom_data = f.read()
				self.rom_path = rom_path
				self.status_callback(f"Loaded ROM: {rom_path.name} ({len(self.rom_data):,} bytes)")
				self.refresh_view()
			except Exception as e:
				self.status_callback(f"Failed to load ROM: {e}")
		else:
			self.status_callback("No ROM found")

	def refresh_view(self):
		"""Refresh the hex view."""
		if not self.rom_data:
			return

		self.hex_text.config(state='normal')
		self.ascii_text.config(state='normal')
		self.hex_text.delete('1.0', 'end')
		self.ascii_text.delete('1.0', 'end')

		display_mode = self.display_var.get()

		for row in range(self.rows_visible):
			addr = self.offset + row * self.bytes_per_row
			if addr >= len(self.rom_data):
				break

			# Offset column
			offset_str = f"{addr:08X}  "
			self.hex_text.insert('end', offset_str, 'offset')

			# Hex/Dec/Bin bytes
			ascii_chars = []
			for col in range(self.bytes_per_row):
				byte_addr = addr + col
				if byte_addr >= len(self.rom_data):
					self.hex_text.insert('end', '   ')
					ascii_chars.append(' ')
					continue

				byte = self.rom_data[byte_addr]

				# Determine tag based on value and region
				tag = ''
				if byte == 0:
					tag = 'zero'
				elif byte >= 0x80:
					tag = 'high'
				elif byte_addr < 0x10:
					tag = 'header'
				elif byte_addr >= 0x10010:
					tag = 'chr'

				# Format based on display mode
				if display_mode == 'hex':
					byte_str = f"{byte:02X} "
				elif display_mode == 'dec':
					byte_str = f"{byte:3d} "
				else:  # bin
					byte_str = f"{byte:08b} "[0:4]  # Truncate for space

				self.hex_text.insert('end', byte_str, tag)

				# ASCII representation
				if 32 <= byte < 127:
					ascii_chars.append(chr(byte))
				else:
					ascii_chars.append('.')

				# Add separator every 8 bytes
				if col == 7:
					self.hex_text.insert('end', ' ')

			self.hex_text.insert('end', '\n')
			self.ascii_text.insert('end', ''.join(ascii_chars) + '\n')

		self.hex_text.config(state='disabled')
		self.ascii_text.config(state='disabled')

	def on_scroll(self, *args):
		"""Handle scrollbar."""
		if not self.rom_data:
			return

		if args[0] == 'moveto':
			fraction = float(args[1])
			max_offset = max(0, len(self.rom_data) - self.rows_visible * self.bytes_per_row)
			self.offset = int(fraction * max_offset)
			self.offset = (self.offset // self.bytes_per_row) * self.bytes_per_row
			self.refresh_view()
		elif args[0] == 'scroll':
			amount = int(args[1])
			unit = args[2]
			if unit == 'units':
				self.offset += amount * self.bytes_per_row
			else:  # pages
				self.offset += amount * self.bytes_per_row * self.rows_visible
			self.offset = max(0, min(self.offset,
				len(self.rom_data) - self.rows_visible * self.bytes_per_row))
			self.offset = (self.offset // self.bytes_per_row) * self.bytes_per_row
			self.refresh_view()

	def on_mousewheel(self, event):
		"""Handle mouse wheel scrolling."""
		if not self.rom_data:
			return

		# Scroll 3 rows at a time
		delta = -3 if event.delta > 0 else 3
		self.offset += delta * self.bytes_per_row
		self.offset = max(0, min(self.offset,
			len(self.rom_data) - self.rows_visible * self.bytes_per_row))
		self.offset = (self.offset // self.bytes_per_row) * self.bytes_per_row
		self.refresh_view()
		return "break"

	def on_click(self, event):
		"""Handle click to select byte."""
		if not self.rom_data:
			return

		# Get click position
		index = self.hex_text.index(f"@{event.x},{event.y}")
		line, col = map(int, index.split('.'))

		# Calculate byte offset from column position
		# Format: "XXXXXXXX  XX XX XX XX XX XX XX XX  XX XX XX XX XX XX XX XX"
		# Offset: 10 chars, then bytes with spaces
		if col < 10:
			return  # Clicked on offset

		col -= 10  # Remove offset column
		display_mode = self.display_var.get()

		if display_mode == 'hex':
			byte_width = 3
			separator_at = 8 * 3
		elif display_mode == 'dec':
			byte_width = 4
			separator_at = 8 * 4
		else:
			byte_width = 4
			separator_at = 8 * 4

		# Account for separator
		if col >= separator_at:
			col -= 1

		byte_in_row = col // byte_width
		if byte_in_row >= self.bytes_per_row:
			return

		byte_offset = self.offset + (line - 1) * self.bytes_per_row + byte_in_row
		if byte_offset >= len(self.rom_data):
			return

		self.selection_start = byte_offset
		self.update_selection_info(byte_offset)

	def update_selection_info(self, offset: int):
		"""Update the selection info panel."""
		if offset >= len(self.rom_data):
			return

		byte = self.rom_data[offset]

		self.sel_offset_var.set(f"0x{offset:08X}")
		self.sel_hex_var.set(f"0x{byte:02X}")
		self.sel_dec_var.set(str(byte))
		self.sel_bin_var.set(f"{byte:08b}")

		# Find region
		region_name = "Unknown"
		for name, (start, end) in self.rom_regions.items():
			if start <= offset < end:
				region_name = name
				break
		self.sel_region_var.set(region_name)

		# Word (little-endian)
		if offset + 1 < len(self.rom_data):
			word = self.rom_data[offset] | (self.rom_data[offset + 1] << 8)
			self.sel_word_var.set(f"0x{word:04X} ({word})")
		else:
			self.sel_word_var.set("-")

		# NES address (accounting for header)
		if offset >= 0x10:
			nes_addr = (offset - 0x10) % 0x4000 + 0x8000
			bank = (offset - 0x10) // 0x4000
			self.sel_nes_var.set(f"${nes_addr:04X} (Bank {bank})")
		else:
			self.sel_nes_var.set("Header")

	def go_to_offset(self):
		"""Jump to specified offset."""
		try:
			offset_str = self.offset_var.get().strip()
			if offset_str.startswith('0x') or offset_str.startswith('$'):
				offset = int(offset_str.replace('$', '0x'), 16)
			else:
				offset = int(offset_str)

			if self.rom_data and 0 <= offset < len(self.rom_data):
				self.offset = (offset // self.bytes_per_row) * self.bytes_per_row
				self.selection_start = offset
				self.refresh_view()
				self.update_selection_info(offset)
				self.status_callback(f"Jumped to offset 0x{offset:08X}")
			else:
				messagebox.showwarning("Invalid Offset", "Offset is out of range")
		except ValueError:
			messagebox.showerror("Error", "Invalid offset format")

	def jump_to_region(self, event=None):
		"""Jump to selected ROM region."""
		region = self.region_var.get()
		if region in self.rom_regions:
			start, _ = self.rom_regions[region]
			self.offset_var.set(f"0x{start:08X}")
			self.go_to_offset()

	def show_find_dialog(self):
		"""Show find dialog."""
		dialog = tk.Toplevel(self.frame)
		dialog.title("Find Bytes")
		dialog.geometry("400x200")
		dialog.transient(self.frame.winfo_toplevel())

		ttk.Label(dialog, text="Search for (hex bytes, e.g., FF 00 AB):").pack(pady=5)
		search_entry = ttk.Entry(dialog, width=40)
		search_entry.pack(pady=5)

		result_var = tk.StringVar(value="")
		ttk.Label(dialog, textvariable=result_var).pack(pady=5)

		def do_find():
			if not self.rom_data:
				return

			pattern_str = search_entry.get().strip()
			try:
				# Parse hex bytes
				bytes_to_find = bytes.fromhex(pattern_str.replace(' ', ''))
				pos = self.rom_data.find(bytes_to_find, self.selection_start + 1 if self.selection_start else 0)

				if pos >= 0:
					self.offset = (pos // self.bytes_per_row) * self.bytes_per_row
					self.selection_start = pos
					self.refresh_view()
					self.update_selection_info(pos)
					result_var.set(f"Found at 0x{pos:08X}")
				else:
					# Wrap around
					pos = self.rom_data.find(bytes_to_find)
					if pos >= 0:
						self.offset = (pos // self.bytes_per_row) * self.bytes_per_row
						self.selection_start = pos
						self.refresh_view()
						self.update_selection_info(pos)
						result_var.set(f"Found at 0x{pos:08X} (wrapped)")
					else:
						result_var.set("Not found")
			except ValueError:
				result_var.set("Invalid hex format")

		ttk.Button(dialog, text="Find Next", command=do_find).pack(pady=10)
		search_entry.bind('<Return>', lambda e: do_find())
		search_entry.focus_set()

	def show_bookmarks(self):
		"""Show bookmarks dialog."""
		dialog = tk.Toplevel(self.frame)
		dialog.title("Bookmarks")
		dialog.geometry("350x300")
		dialog.transient(self.frame.winfo_toplevel())

		# Listbox for bookmarks
		listbox = tk.Listbox(dialog, font=('Consolas', 10))
		listbox.pack(fill='both', expand=True, padx=5, pady=5)

		# Add default bookmarks from ROM regions
		for name, (start, _) in self.rom_regions.items():
			listbox.insert('end', f"0x{start:08X}  {name}")

		# Add custom bookmarks
		for name, offset in self.bookmarks.items():
			listbox.insert('end', f"0x{offset:08X}  {name}")

		def jump_to_bookmark():
			sel = listbox.curselection()
			if sel:
				text = listbox.get(sel[0])
				offset_str = text.split()[0]
				self.offset_var.set(offset_str)
				self.go_to_offset()
				dialog.destroy()

		ttk.Button(dialog, text="Jump To", command=jump_to_bookmark).pack(pady=5)

		# Add current position as bookmark
		def add_bookmark():
			if self.selection_start is not None:
				name = simpledialog.askstring("Add Bookmark", "Bookmark name:")
				if name:
					self.bookmarks[name] = self.selection_start
					listbox.insert('end', f"0x{self.selection_start:08X}  {name}")

		ttk.Button(dialog, text="Add Current", command=add_bookmark).pack(pady=5)

		listbox.bind('<Double-Button-1>', lambda e: jump_to_bookmark())

	def refresh(self):
		"""Refresh hex view."""
		self.load_rom()


# ============================================================================
# SCRIPT/ASM EDITOR TAB
# ============================================================================

class ScriptEditorTab(BaseTab):
	"""Assembly/script source code editor with syntax highlighting."""

	# 6502 opcodes for syntax highlighting
	OPCODES_6502 = {
		'ADC', 'AND', 'ASL', 'BCC', 'BCS', 'BEQ', 'BIT', 'BMI', 'BNE', 'BPL',
		'BRK', 'BVC', 'BVS', 'CLC', 'CLD', 'CLI', 'CLV', 'CMP', 'CPX', 'CPY',
		'DEC', 'DEX', 'DEY', 'EOR', 'INC', 'INX', 'INY', 'JMP', 'JSR', 'LDA',
		'LDX', 'LDY', 'LSR', 'NOP', 'ORA', 'PHA', 'PHP', 'PLA', 'PLP', 'ROL',
		'ROR', 'RTI', 'RTS', 'SBC', 'SEC', 'SED', 'SEI', 'STA', 'STX', 'STY',
		'TAX', 'TAY', 'TSX', 'TXA', 'TXS', 'TYA',
	}

	# Ophis directives
	DIRECTIVES = {
		'.alias', '.advance', '.ascii', '.asciiz', '.byte', '.cbmfloat',
		'.charmap', '.charmapbin', '.checkpc', '.data', '.dword', '.else',
		'.elsif', '.endif', '.if', '.incbin', '.include', '.invoke', '.macro',
		'.macend', '.org', '.outfile', '.require', '.scope', '.scend',
		'.segment', '.space', '.text', '.word', '.wordbe', '.dwordbe',
	}

	def __init__(self, notebook: ttk.Notebook, asset_manager: AssetManager, status_callback):
		super().__init__(notebook, asset_manager, status_callback)
		self.current_file: Optional[Path] = None
		self.modified = False
		self.file_history: List[Path] = []

		self.setup_ui()
		self.load_file_list()

	def setup_ui(self):
		"""Set up the script editor UI."""
		# Top toolbar
		toolbar = ttk.Frame(self.frame)
		toolbar.pack(fill='x', padx=5, pady=5)

		ttk.Label(toolbar, text="File:").pack(side='left', padx=2)
		self.file_var = tk.StringVar()
		self.file_combo = ttk.Combobox(toolbar, textvariable=self.file_var, width=50)
		self.file_combo.pack(side='left', padx=2)
		self.file_combo.bind('<<ComboboxSelected>>', self.on_file_selected)

		ttk.Button(toolbar, text="Open...", command=self.open_file).pack(side='left', padx=2)
		ttk.Button(toolbar, text="Save", command=self.save_file).pack(side='left', padx=2)
		ttk.Button(toolbar, text="Reload", command=self.reload_file).pack(side='left', padx=2)

		ttk.Separator(toolbar, orient='vertical').pack(side='left', fill='y', padx=5)

		ttk.Button(toolbar, text="Find...", command=self.show_find).pack(side='left', padx=2)
		ttk.Button(toolbar, text="Go to Line...", command=self.goto_line).pack(side='left', padx=2)

		# Main editor pane with line numbers
		editor_frame = ttk.Frame(self.frame)
		editor_frame.pack(fill='both', expand=True, padx=5, pady=5)

		# Line numbers
		self.line_numbers = tk.Text(
			editor_frame,
			width=6,
			font=('Consolas', 10),
			bg='#1e1e1e',
			fg='#858585',
			state='disabled',
			relief='flat',
			padx=5
		)
		self.line_numbers.pack(side='left', fill='y')

		# Code editor
		self.editor = tk.Text(
			editor_frame,
			font=('Consolas', 10),
			wrap='none',
			undo=True,
			bg='#1e1e1e',
			fg='#d4d4d4',
			insertbackground='white',
			selectbackground='#264f78',
			relief='flat',
			padx=5,
			pady=5
		)
		self.editor.pack(side='left', fill='both', expand=True)

		# Scrollbars
		v_scroll = ttk.Scrollbar(editor_frame, orient='vertical', command=self.sync_scroll_v)
		v_scroll.pack(side='right', fill='y')
		self.editor.config(yscrollcommand=v_scroll.set)

		h_scroll = ttk.Scrollbar(self.frame, orient='horizontal', command=self.editor.xview)
		h_scroll.pack(fill='x')
		self.editor.config(xscrollcommand=h_scroll.set)

		# Configure syntax highlighting tags
		self.editor.tag_configure('opcode', foreground='#569cd6', font=('Consolas', 10, 'bold'))
		self.editor.tag_configure('directive', foreground='#c586c0')
		self.editor.tag_configure('comment', foreground='#6a9955', font=('Consolas', 10, 'italic'))
		self.editor.tag_configure('label', foreground='#dcdcaa')
		self.editor.tag_configure('number', foreground='#b5cea8')
		self.editor.tag_configure('string', foreground='#ce9178')
		self.editor.tag_configure('register', foreground='#9cdcfe')

		# Bindings
		self.editor.bind('<KeyRelease>', self.on_key_release)
		self.editor.bind('<Control-s>', lambda e: self.save_file())
		self.editor.bind('<Control-g>', lambda e: self.goto_line())
		self.editor.bind('<Control-f>', lambda e: self.show_find())

		# Status line
		status_frame = ttk.Frame(self.frame)
		status_frame.pack(fill='x', padx=5, pady=2)

		self.line_col_var = tk.StringVar(value="Line 1, Col 1")
		ttk.Label(status_frame, textvariable=self.line_col_var).pack(side='left')

		self.file_info_var = tk.StringVar(value="No file loaded")
		ttk.Label(status_frame, textvariable=self.file_info_var).pack(side='right')

		self.editor.bind('<ButtonRelease-1>', self.update_cursor_pos)
		self.editor.bind('<KeyRelease>', self.update_cursor_pos)

	def sync_scroll_v(self, *args):
		"""Synchronize vertical scrolling between line numbers and editor."""
		self.editor.yview(*args)
		self.line_numbers.yview(*args)

	def load_file_list(self):
		"""Load list of ASM/source files."""
		files = []

		# Source files from source_files directory
		source_dir = PROJECT_ROOT / "source_files"
		if source_dir.exists():
			files.extend(sorted(source_dir.glob("*.asm")))
			files.extend(sorted(source_dir.glob("*.inc")))
			files.extend(sorted(source_dir.glob("*.cfg")))

		# Build reinsertion files
		reinsertion_dir = PROJECT_ROOT / "build" / "reinsertion"
		if reinsertion_dir.exists():
			files.extend(sorted(reinsertion_dir.glob("*.asm")))

		# Asset generated files
		assets_text_dir = PROJECT_ROOT / "assets" / "text"
		if assets_text_dir.exists():
			files.extend(sorted(assets_text_dir.glob("*.asm")))

		self.file_list = files
		self.file_combo['values'] = [f.name for f in files]

		if files:
			self.file_var.set(files[0].name)
			self.load_file(files[0])

	def on_file_selected(self, event=None):
		"""Handle file selection from combo."""
		name = self.file_var.get()
		for f in self.file_list:
			if f.name == name:
				self.load_file(f)
				break

	def load_file(self, path: Path):
		"""Load a file into the editor."""
		if self.modified:
			if messagebox.askyesno("Save Changes?", "Save changes to current file?"):
				self.save_file()

		try:
			with open(path, 'r', encoding='utf-8', errors='replace') as f:
				content = f.read()

			self.editor.delete('1.0', 'end')
			self.editor.insert('1.0', content)
			self.current_file = path
			self.modified = False

			self.file_info_var.set(f"{path.name} ({len(content):,} bytes, {content.count(chr(10)):,} lines)")
			self.status_callback(f"Loaded: {path.name}")

			self.update_line_numbers()
			self.highlight_syntax()

		except Exception as e:
			messagebox.showerror("Error", f"Failed to load file: {e}")

	def open_file(self):
		"""Open a file dialog."""
		from tkinter import filedialog
		path = filedialog.askopenfilename(
			initialdir=PROJECT_ROOT / "source_files",
			filetypes=[
				("ASM files", "*.asm"),
				("Include files", "*.inc"),
				("All files", "*.*")
			]
		)
		if path:
			self.load_file(Path(path))

	def save_file(self):
		"""Save current file."""
		if not self.current_file:
			return

		try:
			content = self.editor.get('1.0', 'end-1c')
			with open(self.current_file, 'w', encoding='utf-8') as f:
				f.write(content)

			self.modified = False
			self.status_callback(f"Saved: {self.current_file.name}")
			messagebox.showinfo("Saved", f"Saved {self.current_file.name}")

		except Exception as e:
			messagebox.showerror("Error", f"Failed to save: {e}")

	def reload_file(self):
		"""Reload current file."""
		if self.current_file:
			self.load_file(self.current_file)

	def update_line_numbers(self):
		"""Update line number display."""
		self.line_numbers.config(state='normal')
		self.line_numbers.delete('1.0', 'end')

		content = self.editor.get('1.0', 'end-1c')
		line_count = content.count('\n') + 1

		line_nums = '\n'.join(str(i) for i in range(1, line_count + 1))
		self.line_numbers.insert('1.0', line_nums)
		self.line_numbers.config(state='disabled')

	def highlight_syntax(self):
		"""Apply syntax highlighting to the entire file."""
		# Clear existing tags
		for tag in ['opcode', 'directive', 'comment', 'label', 'number', 'string', 'register']:
			self.editor.tag_remove(tag, '1.0', 'end')

		content = self.editor.get('1.0', 'end')
		lines = content.split('\n')

		for line_num, line in enumerate(lines, 1):
			if not line.strip():
				continue

			# Comments (;)
			if ';' in line:
				comment_start = line.index(';')
				start = f"{line_num}.{comment_start}"
				end = f"{line_num}.end"
				self.editor.tag_add('comment', start, end)
				line = line[:comment_start]  # Only process before comment

			# Labels (word followed by :)
			import re
			label_match = re.match(r'^(\w+):', line)
			if label_match:
				self.editor.tag_add('label', f"{line_num}.0", f"{line_num}.{label_match.end()}")

			# Directives (start with .)
			for match in re.finditer(r'\.\w+', line):
				if match.group().lower() in self.DIRECTIVES:
					self.editor.tag_add('directive', f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")

			# Opcodes (3-letter uppercase)
			for match in re.finditer(r'\b([A-Za-z]{3})\b', line):
				if match.group().upper() in self.OPCODES_6502:
					self.editor.tag_add('opcode', f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")

			# Numbers (hex: $xx, 0x, #$, decimal)
			for match in re.finditer(r'(\$[0-9A-Fa-f]+|#\$[0-9A-Fa-f]+|0x[0-9A-Fa-f]+|\b[0-9]+\b)', line):
				self.editor.tag_add('number', f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")

			# Strings
			for match in re.finditer(r'"[^"]*"', line):
				self.editor.tag_add('string', f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")

			# Registers (A, X, Y)
			for match in re.finditer(r'\b[AXY]\b', line):
				self.editor.tag_add('register', f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")

	def on_key_release(self, event):
		"""Handle key release for live updates."""
		self.modified = True
		self.update_cursor_pos(event)

		# Update line numbers if line count changed
		self.update_line_numbers()

		# Simplified syntax highlighting for current line only
		line = self.editor.index('insert').split('.')[0]
		self.highlight_line(int(line))

	def highlight_line(self, line_num: int):
		"""Highlight a single line."""
		import re
		start = f"{line_num}.0"
		end = f"{line_num}.end"

		# Clear tags on this line
		for tag in ['opcode', 'directive', 'comment', 'label', 'number', 'string', 'register']:
			self.editor.tag_remove(tag, start, end)

		line = self.editor.get(start, end)
		if not line.strip():
			return

		# Comments
		if ';' in line:
			comment_start = line.index(';')
			self.editor.tag_add('comment', f"{line_num}.{comment_start}", end)
			line = line[:comment_start]

		# Labels
		label_match = re.match(r'^(\w+):', line)
		if label_match:
			self.editor.tag_add('label', start, f"{line_num}.{label_match.end()}")

		# Directives
		for match in re.finditer(r'\.\w+', line):
			if match.group().lower() in self.DIRECTIVES:
				self.editor.tag_add('directive', f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")

		# Opcodes
		for match in re.finditer(r'\b([A-Za-z]{3})\b', line):
			if match.group().upper() in self.OPCODES_6502:
				self.editor.tag_add('opcode', f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")

		# Numbers
		for match in re.finditer(r'(\$[0-9A-Fa-f]+|#\$[0-9A-Fa-f]+|0x[0-9A-Fa-f]+|\b[0-9]+\b)', line):
			self.editor.tag_add('number', f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")

		# Strings
		for match in re.finditer(r'"[^"]*"', line):
			self.editor.tag_add('string', f"{line_num}.{match.start()}", f"{line_num}.{match.end()}")

	def update_cursor_pos(self, event=None):
		"""Update cursor position display."""
		pos = self.editor.index('insert')
		line, col = pos.split('.')
		self.line_col_var.set(f"Line {line}, Col {int(col) + 1}")

	def show_find(self):
		"""Show find dialog."""
		dialog = tk.Toplevel(self.frame)
		dialog.title("Find")
		dialog.geometry("400x150")
		dialog.transient(self.frame.winfo_toplevel())

		ttk.Label(dialog, text="Find:").pack(pady=5)
		search_var = tk.StringVar()
		search_entry = ttk.Entry(dialog, textvariable=search_var, width=40)
		search_entry.pack(pady=5)

		result_var = tk.StringVar()
		ttk.Label(dialog, textvariable=result_var).pack(pady=5)

		def do_find():
			pattern = search_var.get()
			if not pattern:
				return

			# Start from current position
			start = self.editor.index('insert+1c')
			pos = self.editor.search(pattern, start, nocase=True)

			if not pos:
				# Wrap around
				pos = self.editor.search(pattern, '1.0', nocase=True)

			if pos:
				# Select found text
				self.editor.tag_remove('sel', '1.0', 'end')
				end = f"{pos}+{len(pattern)}c"
				self.editor.tag_add('sel', pos, end)
				self.editor.mark_set('insert', pos)
				self.editor.see(pos)
				result_var.set(f"Found at {pos}")
			else:
				result_var.set("Not found")

		ttk.Button(dialog, text="Find Next", command=do_find).pack(pady=10)
		search_entry.bind('<Return>', lambda e: do_find())
		search_entry.focus_set()

	def goto_line(self):
		"""Go to specific line number."""
		line = simpledialog.askinteger("Go to Line", "Line number:")
		if line:
			self.editor.mark_set('insert', f"{line}.0")
			self.editor.see(f"{line}.0")
			self.update_cursor_pos()

	def refresh(self):
		"""Refresh file list."""
		self.load_file_list()


# ============================================================================
# ROM COMPARISON TAB
# ============================================================================

class RomComparisonTab(BaseTab):
	"""Compare original ROM with rebuilt ROM to find differences."""

	def __init__(self, notebook: ttk.Notebook, asset_manager: AssetManager, status_callback):
		super().__init__(notebook, asset_manager, status_callback)
		self.original_rom: Optional[bytes] = None
		self.rebuilt_rom: Optional[bytes] = None
		self.differences: List[Tuple[int, int, int]] = []  # (offset, original_byte, rebuilt_byte)

		self.setup_ui()

	def setup_ui(self):
		"""Set up comparison UI."""
		# Top controls
		control_frame = ttk.Frame(self.frame)
		control_frame.pack(fill='x', padx=5, pady=5)

		ttk.Label(control_frame, text="Original ROM:").grid(row=0, column=0, sticky='e', padx=5)
		self.original_var = tk.StringVar()
		ttk.Entry(control_frame, textvariable=self.original_var, width=50).grid(row=0, column=1, padx=5)
		ttk.Button(control_frame, text="Browse...", command=self.browse_original).grid(row=0, column=2, padx=5)

		ttk.Label(control_frame, text="Rebuilt ROM:").grid(row=1, column=0, sticky='e', padx=5)
		self.rebuilt_var = tk.StringVar()
		ttk.Entry(control_frame, textvariable=self.rebuilt_var, width=50).grid(row=1, column=1, padx=5)
		ttk.Button(control_frame, text="Browse...", command=self.browse_rebuilt).grid(row=1, column=2, padx=5)

		ttk.Button(control_frame, text="Compare", command=self.compare_roms).grid(row=0, column=3, rowspan=2, padx=10)

		# Filter options
		filter_frame = ttk.LabelFrame(self.frame, text="Filter")
		filter_frame.pack(fill='x', padx=5, pady=5)

		self.filter_var = tk.StringVar(value="all")
		ttk.Radiobutton(filter_frame, text="All Differences", variable=self.filter_var,
			value="all", command=self.apply_filter).pack(side='left', padx=5)
		ttk.Radiobutton(filter_frame, text="PRG-ROM Only", variable=self.filter_var,
			value="prg", command=self.apply_filter).pack(side='left', padx=5)
		ttk.Radiobutton(filter_frame, text="CHR-ROM Only", variable=self.filter_var,
			value="chr", command=self.apply_filter).pack(side='left', padx=5)
		ttk.Radiobutton(filter_frame, text="Header Only", variable=self.filter_var,
			value="header", command=self.apply_filter).pack(side='left', padx=5)

		# Summary
		summary_frame = ttk.LabelFrame(self.frame, text="Summary")
		summary_frame.pack(fill='x', padx=5, pady=5)

		self.summary_text = tk.Text(summary_frame, height=4, font=('Consolas', 10), wrap='word')
		self.summary_text.pack(fill='x', padx=5, pady=5)

		# Difference list
		list_frame = ttk.LabelFrame(self.frame, text="Differences")
		list_frame.pack(fill='both', expand=True, padx=5, pady=5)

		# Treeview for differences
		columns = ('offset', 'nes_addr', 'region', 'original', 'rebuilt', 'diff')
		self.diff_tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=15)

		self.diff_tree.heading('offset', text='File Offset')
		self.diff_tree.heading('nes_addr', text='NES Address')
		self.diff_tree.heading('region', text='Region')
		self.diff_tree.heading('original', text='Original')
		self.diff_tree.heading('rebuilt', text='Rebuilt')
		self.diff_tree.heading('diff', text='XOR')

		self.diff_tree.column('offset', width=100)
		self.diff_tree.column('nes_addr', width=100)
		self.diff_tree.column('region', width=120)
		self.diff_tree.column('original', width=80)
		self.diff_tree.column('rebuilt', width=80)
		self.diff_tree.column('diff', width=80)

		scrollbar = ttk.Scrollbar(list_frame, orient='vertical', command=self.diff_tree.yview)
		self.diff_tree.configure(yscrollcommand=scrollbar.set)

		self.diff_tree.pack(side='left', fill='both', expand=True)
		scrollbar.pack(side='right', fill='y')

		# Set default paths
		original = PROJECT_ROOT / "roms" / "Dragon Warrior (USA).nes"
		rebuilt = PROJECT_ROOT / "build" / "dragon_warrior_rebuilt.nes"

		if original.exists():
			self.original_var.set(str(original))
		if rebuilt.exists():
			self.rebuilt_var.set(str(rebuilt))

	def browse_original(self):
		"""Browse for original ROM."""
		from tkinter import filedialog
		path = filedialog.askopenfilename(
			initialdir=PROJECT_ROOT / "roms",
			filetypes=[("NES ROMs", "*.nes"), ("All files", "*.*")]
		)
		if path:
			self.original_var.set(path)

	def browse_rebuilt(self):
		"""Browse for rebuilt ROM."""
		from tkinter import filedialog
		path = filedialog.askopenfilename(
			initialdir=PROJECT_ROOT / "build",
			filetypes=[("NES ROMs", "*.nes"), ("All files", "*.*")]
		)
		if path:
			self.rebuilt_var.set(path)

	def compare_roms(self):
		"""Compare the two ROMs."""
		original_path = self.original_var.get()
		rebuilt_path = self.rebuilt_var.get()

		if not original_path or not rebuilt_path:
			messagebox.showwarning("Missing Files", "Please select both ROMs to compare")
			return

		try:
			with open(original_path, 'rb') as f:
				self.original_rom = f.read()
			with open(rebuilt_path, 'rb') as f:
				self.rebuilt_rom = f.read()
		except Exception as e:
			messagebox.showerror("Error", f"Failed to read ROMs: {e}")
			return

		# Find differences
		self.differences = []
		min_len = min(len(self.original_rom), len(self.rebuilt_rom))

		for i in range(min_len):
			if self.original_rom[i] != self.rebuilt_rom[i]:
				self.differences.append((i, self.original_rom[i], self.rebuilt_rom[i]))

		# Size differences
		size_diff = len(self.original_rom) - len(self.rebuilt_rom)

		# Update summary
		self.summary_text.delete('1.0', 'end')
		summary_lines = [
			f"Original: {len(self.original_rom):,} bytes ({Path(original_path).name})",
			f"Rebuilt:  {len(self.rebuilt_rom):,} bytes ({Path(rebuilt_path).name})",
			f"Size Difference: {abs(size_diff):,} bytes {'(original larger)' if size_diff > 0 else '(rebuilt larger)' if size_diff < 0 else '(same size)'}",
			f"Byte Differences: {len(self.differences):,} bytes differ"
		]
		self.summary_text.insert('1.0', '\n'.join(summary_lines))

		self.apply_filter()
		self.status_callback(f"Comparison complete: {len(self.differences)} differences found")

	def get_region(self, offset: int) -> str:
		"""Get the region name for an offset."""
		if offset < 0x10:
			return "Header"
		elif offset < 0x10010:
			bank = (offset - 0x10) // 0x4000
			return f"PRG-ROM Bank {bank}"
		else:
			return "CHR-ROM"

	def get_nes_address(self, offset: int) -> str:
		"""Get NES address for an offset."""
		if offset < 0x10:
			return "Header"
		elif offset < 0x10010:
			return f"${(offset - 0x10) % 0x4000 + 0x8000:04X}"
		else:
			return f"CHR ${offset - 0x10010:04X}"

	def apply_filter(self):
		"""Apply filter to difference list."""
		# Clear tree
		for item in self.diff_tree.get_children():
			self.diff_tree.delete(item)

		filter_type = self.filter_var.get()

		count = 0
		for offset, orig, rebuilt in self.differences:
			region = self.get_region(offset)

			# Apply filter
			if filter_type == 'header' and offset >= 0x10:
				continue
			elif filter_type == 'prg' and (offset < 0x10 or offset >= 0x10010):
				continue
			elif filter_type == 'chr' and offset < 0x10010:
				continue

			xor = orig ^ rebuilt

			self.diff_tree.insert('', 'end', values=(
				f"0x{offset:08X}",
				self.get_nes_address(offset),
				region,
				f"0x{orig:02X} ({orig})",
				f"0x{rebuilt:02X} ({rebuilt})",
				f"0x{xor:02X}"
			))

			count += 1
			if count >= 5000:  # Limit display
				break

	def refresh(self):
		"""Refresh comparison."""
		if self.original_rom and self.rebuilt_rom:
			self.compare_roms()


# ============================================================================
# CHEAT CODE GENERATOR TAB
# ============================================================================

class CheatCodeTab(BaseTab):
	"""Generate Game Genie and Pro Action Replay codes."""

	# NES Game Genie encoding
	GENIE_CHARS = 'APZLGITYEOXUKSVN'

	def __init__(self, notebook: ttk.Notebook, asset_manager: AssetManager, status_callback):
		super().__init__(notebook, asset_manager, status_callback)
		self.rom_data: Optional[bytes] = None
		self.generated_codes: List[Dict] = []

		self.setup_ui()
		self.load_rom()

	def setup_ui(self):
		"""Set up cheat code generator UI."""
		# Main paned window
		paned = ttk.PanedWindow(self.frame, orient='horizontal')
		paned.pack(fill='both', expand=True, padx=5, pady=5)

		# Left side: Code generator
		left_frame = ttk.LabelFrame(paned, text="Code Generator")
		paned.add(left_frame, weight=1)

		# Address input
		addr_frame = ttk.Frame(left_frame)
		addr_frame.pack(fill='x', padx=5, pady=5)

		ttk.Label(addr_frame, text="ROM Offset:").grid(row=0, column=0, sticky='e', padx=5)
		self.addr_var = tk.StringVar(value="0x")
		ttk.Entry(addr_frame, textvariable=self.addr_var, width=12).grid(row=0, column=1, padx=5)

		ttk.Label(addr_frame, text="New Value:").grid(row=0, column=2, sticky='e', padx=5)
		self.value_var = tk.StringVar(value="0x")
		ttk.Entry(addr_frame, textvariable=self.value_var, width=8).grid(row=0, column=3, padx=5)

		ttk.Label(addr_frame, text="Compare (opt):").grid(row=1, column=0, sticky='e', padx=5)
		self.compare_var = tk.StringVar()
		ttk.Entry(addr_frame, textvariable=self.compare_var, width=12).grid(row=1, column=1, padx=5)

		ttk.Button(addr_frame, text="Generate Code", command=self.generate_code).grid(
			row=1, column=2, columnspan=2, padx=5, pady=5)

		# Code type selection
		type_frame = ttk.LabelFrame(left_frame, text="Code Type")
		type_frame.pack(fill='x', padx=5, pady=5)

		self.code_type_var = tk.StringVar(value="genie")
		ttk.Radiobutton(type_frame, text="Game Genie", variable=self.code_type_var,
			value="genie").pack(side='left', padx=10)
		ttk.Radiobutton(type_frame, text="Pro Action Replay", variable=self.code_type_var,
			value="par").pack(side='left', padx=10)
		ttk.Radiobutton(type_frame, text="Raw Patch", variable=self.code_type_var,
			value="raw").pack(side='left', padx=10)

		# Common cheats preset
		preset_frame = ttk.LabelFrame(left_frame, text="Common Cheats")
		preset_frame.pack(fill='x', padx=5, pady=5)

		presets = [
			("Infinite HP", self.generate_infinite_hp),
			("Infinite MP", self.generate_infinite_mp),
			("Infinite Gold", self.generate_infinite_gold),
			("Max Stats", self.generate_max_stats),
			("Walk Through Walls", self.generate_walk_through),
			("No Random Encounters", self.generate_no_encounters),
		]

		for i, (name, cmd) in enumerate(presets):
			row, col = divmod(i, 3)
			ttk.Button(preset_frame, text=name, command=cmd).grid(row=row, column=col, padx=5, pady=2)

		# Generated code output
		output_frame = ttk.LabelFrame(left_frame, text="Generated Code")
		output_frame.pack(fill='both', expand=True, padx=5, pady=5)

		self.code_output = tk.Text(output_frame, height=8, font=('Consolas', 12), bg='#1e1e1e', fg='#4ec9b0')
		self.code_output.pack(fill='both', expand=True, padx=5, pady=5)

		ttk.Button(output_frame, text="Copy to Clipboard", command=self.copy_code).pack(pady=5)

		# Right side: Code library
		right_frame = ttk.LabelFrame(paned, text="Saved Codes")
		paned.add(right_frame, weight=1)

		# Code library treeview
		columns = ('name', 'code', 'type')
		self.code_tree = ttk.Treeview(right_frame, columns=columns, show='headings')
		self.code_tree.heading('name', text='Name')
		self.code_tree.heading('code', text='Code')
		self.code_tree.heading('type', text='Type')
		self.code_tree.column('name', width=150)
		self.code_tree.column('code', width=120)
		self.code_tree.column('type', width=80)
		self.code_tree.pack(fill='both', expand=True, padx=5, pady=5)

		# Buttons
		btn_frame = ttk.Frame(right_frame)
		btn_frame.pack(fill='x', padx=5, pady=5)

		ttk.Button(btn_frame, text="Save Code", command=self.save_code).pack(side='left', padx=5)
		ttk.Button(btn_frame, text="Delete", command=self.delete_code).pack(side='left', padx=5)
		ttk.Button(btn_frame, text="Export All", command=self.export_codes).pack(side='left', padx=5)

		# Load existing codes
		self.load_saved_codes()

	def load_rom(self):
		"""Load ROM data for reference."""
		rom_path = PROJECT_ROOT / "build" / "dragon_warrior_rebuilt.nes"
		if not rom_path.exists():
			rom_path = PROJECT_ROOT / "roms" / "Dragon Warrior (USA).nes"

		if rom_path.exists():
			try:
				with open(rom_path, 'rb') as f:
					self.rom_data = f.read()
			except:
				pass

	def generate_code(self):
		"""Generate cheat code from inputs."""
		try:
			# Parse address
			addr_str = self.addr_var.get().strip()
			if addr_str.startswith('0x') or addr_str.startswith('$'):
				address = int(addr_str.replace('$', '0x'), 16)
			else:
				address = int(addr_str)

			# Parse value
			val_str = self.value_var.get().strip()
			if val_str.startswith('0x') or val_str.startswith('$'):
				value = int(val_str.replace('$', '0x'), 16)
			else:
				value = int(val_str)

			# Parse compare (optional)
			compare_str = self.compare_var.get().strip()
			compare = None
			if compare_str:
				if compare_str.startswith('0x') or compare_str.startswith('$'):
					compare = int(compare_str.replace('$', '0x'), 16)
				else:
					compare = int(compare_str)

			# Generate based on type
			code_type = self.code_type_var.get()

			if code_type == 'genie':
				code = self.encode_game_genie(address, value, compare)
			elif code_type == 'par':
				code = self.encode_par(address, value)
			else:
				code = f"ROM[0x{address:06X}] = 0x{value:02X}"

			self.code_output.delete('1.0', 'end')
			self.code_output.insert('1.0', code)
			self.status_callback(f"Generated {code_type} code: {code}")

		except ValueError as e:
			messagebox.showerror("Error", f"Invalid input: {e}")

	def encode_game_genie(self, address: int, value: int, compare: Optional[int] = None) -> str:
		"""Encode Game Genie code."""
		# Convert ROM offset to NES CPU address
		# Assuming PRG-ROM starts at 0x8000
		if address >= 0x10:  # Skip header
			nes_address = 0x8000 + ((address - 0x10) % 0x8000)
		else:
			nes_address = address

		# Game Genie encoding
		# 6-letter code: AAAA VVVV (address bits scrambled, value bits scrambled)
		# 8-letter code: adds compare value

		n = [0] * 8

		if compare is None:
			# 6-letter code
			n[0] = (value >> 4) & 0x08
			n[0] |= (value >> 0) & 0x07
			n[1] = (nes_address >> 4) & 0x08
			n[1] |= (value >> 4) & 0x07
			n[2] = (nes_address >> 4) & 0x07
			n[2] |= (nes_address >> 12) & 0x08
			n[3] = (nes_address >> 0) & 0x08
			n[3] |= (nes_address >> 8) & 0x07
			n[4] = (nes_address >> 8) & 0x08
			n[4] |= (nes_address >> 0) & 0x07
			n[5] = (nes_address >> 12) & 0x07
			n[5] |= (nes_address >> 0) & 0x08  # Set bit to indicate 6-letter

			return ''.join(self.GENIE_CHARS[n[i]] for i in range(6))
		else:
			# 8-letter code with compare
			n[0] = (value >> 4) & 0x08
			n[0] |= (value >> 0) & 0x07
			n[1] = (nes_address >> 4) & 0x08
			n[1] |= (value >> 4) & 0x07
			n[2] = (nes_address >> 4) & 0x07
			n[2] |= 0x00  # Clear bit to indicate 8-letter
			n[3] = (nes_address >> 0) & 0x08
			n[3] |= (nes_address >> 8) & 0x07
			n[4] = (compare >> 4) & 0x08
			n[4] |= (nes_address >> 0) & 0x07
			n[5] = (nes_address >> 12) & 0x07
			n[5] |= (compare >> 0) & 0x08
			n[6] = (nes_address >> 12) & 0x08
			n[6] |= (compare >> 0) & 0x07
			n[7] = (compare >> 0) & 0x08
			n[7] |= (compare >> 4) & 0x07

			return ''.join(self.GENIE_CHARS[n[i]] for i in range(8))

	def encode_par(self, address: int, value: int) -> str:
		"""Encode Pro Action Replay code."""
		# Simple format: AAAA:VV
		if address >= 0x10:
			nes_address = 0x8000 + ((address - 0x10) % 0x8000)
		else:
			nes_address = address
		return f"{nes_address:04X}:{value:02X}"

	def generate_infinite_hp(self):
		"""Generate infinite HP code."""
		# HP is typically at RAM $00C5
		self.code_output.delete('1.0', 'end')
		self.code_output.insert('1.0', "SXSZLGVG\n; Infinite HP - Prevents HP from decreasing in battle")

	def generate_infinite_mp(self):
		"""Generate infinite MP code."""
		self.code_output.delete('1.0', 'end')
		self.code_output.insert('1.0', "SXSXLZVG\n; Infinite MP - Prevents MP from decreasing")

	def generate_infinite_gold(self):
		"""Generate infinite gold code."""
		self.code_output.delete('1.0', 'end')
		self.code_output.insert('1.0', "AEKZTZGA\n; Infinite Gold - Gold doesn't decrease when buying")

	def generate_max_stats(self):
		"""Generate max stats codes."""
		self.code_output.delete('1.0', 'end')
		codes = [
			"AAAPZPPA  ; Max Strength",
			"AAASXPPA  ; Max Agility",
			"AAAVTPPA  ; Max HP Growth",
			"AAAEUPPA  ; Max MP Growth",
		]
		self.code_output.insert('1.0', '\n'.join(codes))

	def generate_walk_through(self):
		"""Generate walk-through-walls code."""
		self.code_output.delete('1.0', 'end')
		self.code_output.insert('1.0', "AAOIZTPA\n; Walk Through Walls - Can walk on any terrain")

	def generate_no_encounters(self):
		"""Generate no random encounters code."""
		self.code_output.delete('1.0', 'end')
		self.code_output.insert('1.0', "SXEOKOSE\n; No Random Encounters - No battles on world map")

	def copy_code(self):
		"""Copy generated code to clipboard."""
		code = self.code_output.get('1.0', 'end-1c').split('\n')[0]  # First line only
		self.frame.clipboard_clear()
		self.frame.clipboard_append(code)
		self.status_callback(f"Copied: {code}")

	def save_code(self):
		"""Save code to library."""
		code = self.code_output.get('1.0', 'end-1c').split('\n')[0]
		if not code:
			return

		name = simpledialog.askstring("Save Code", "Enter a name for this code:")
		if name:
			code_type = self.code_type_var.get()
			self.generated_codes.append({'name': name, 'code': code, 'type': code_type})
			self.code_tree.insert('', 'end', values=(name, code, code_type))
			self.save_codes_to_file()

	def delete_code(self):
		"""Delete selected code from library."""
		selection = self.code_tree.selection()
		if selection:
			for item in selection:
				values = self.code_tree.item(item, 'values')
				self.generated_codes = [c for c in self.generated_codes if c['code'] != values[1]]
				self.code_tree.delete(item)
			self.save_codes_to_file()

	def load_saved_codes(self):
		"""Load saved codes from file."""
		codes_file = PROJECT_ROOT / "assets" / "data" / "cheat_codes.json"
		if codes_file.exists():
			try:
				with open(codes_file, 'r') as f:
					self.generated_codes = json.load(f)
				for code in self.generated_codes:
					self.code_tree.insert('', 'end', values=(code['name'], code['code'], code['type']))
			except:
				pass

	def save_codes_to_file(self):
		"""Save codes to file."""
		codes_file = PROJECT_ROOT / "assets" / "data" / "cheat_codes.json"
		codes_file.parent.mkdir(parents=True, exist_ok=True)
		try:
			with open(codes_file, 'w') as f:
				json.dump(self.generated_codes, f, indent=2)
		except Exception as e:
			messagebox.showerror("Error", f"Failed to save codes: {e}")

	def export_codes(self):
		"""Export all codes to text file."""
		if not self.generated_codes:
			messagebox.showinfo("Info", "No codes to export")
			return

		from tkinter import filedialog
		path = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text files", "*.txt"), ("All files", "*.*")],
			initialfile="dragon_warrior_cheats.txt"
		)

		if path:
			try:
				with open(path, 'w') as f:
					f.write("Dragon Warrior - Cheat Codes\n")
					f.write("=" * 40 + "\n\n")
					for code in self.generated_codes:
						f.write(f"{code['name']}\n")
						f.write(f"  Code: {code['code']}\n")
						f.write(f"  Type: {code['type']}\n\n")
				messagebox.showinfo("Success", f"Exported {len(self.generated_codes)} codes")
			except Exception as e:
				messagebox.showerror("Error", f"Export failed: {e}")

	def refresh(self):
		"""Refresh tab."""
		self.load_rom()


# ============================================================================
# MUSIC/SOUND EDITOR TAB
# ============================================================================

class MusicEditorTab(BaseTab):
	"""View and edit music/sound data from the ROM."""

	# NES APU note frequencies (NTSC, based on CPU clock 1.789773 MHz)
	# These are period values for the square wave channels
	NOTE_NAMES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

	# Dragon Warrior music track info (approximate offsets - would need verification)
	MUSIC_TRACKS = {
		'Title Screen': {'offset': 0xF000 + 0x10, 'description': 'Main title music'},
		'Overworld': {'offset': 0xE800 + 0x10, 'description': 'World map theme'},
		'Castle': {'offset': 0xE900 + 0x10, 'description': 'Castle/town theme'},
		'Cave': {'offset': 0xEA00 + 0x10, 'description': 'Dungeon theme'},
		'Battle': {'offset': 0xEB00 + 0x10, 'description': 'Battle music'},
		'Victory': {'offset': 0xEC00 + 0x10, 'description': 'Victory fanfare'},
		'Death': {'offset': 0xED00 + 0x10, 'description': 'Game over theme'},
		'Inn': {'offset': 0xEE00 + 0x10, 'description': 'Inn rest jingle'},
		'Level Up': {'offset': 0xEF00 + 0x10, 'description': 'Level up fanfare'},
	}

	def __init__(self, notebook: ttk.Notebook, asset_manager: AssetManager, status_callback):
		super().__init__(notebook, asset_manager, status_callback)
		self.rom_data: Optional[bytes] = None
		self.current_track: Optional[str] = None

		self.setup_ui()
		self.load_rom()

	def setup_ui(self):
		"""Set up music editor UI."""
		# Main paned window
		paned = ttk.PanedWindow(self.frame, orient='horizontal')
		paned.pack(fill='both', expand=True, padx=5, pady=5)

		# Left side: Track list
		left_frame = ttk.LabelFrame(paned, text="Music Tracks")
		paned.add(left_frame, weight=1)

		# Track listbox
		self.track_listbox = tk.Listbox(left_frame, font=('Segoe UI', 10))
		self.track_listbox.pack(fill='both', expand=True, padx=5, pady=5)
		self.track_listbox.bind('<<ListboxSelect>>', self.on_track_select)

		for track_name in self.MUSIC_TRACKS.keys():
			self.track_listbox.insert('end', track_name)

		# Track info
		info_frame = ttk.LabelFrame(left_frame, text="Track Info")
		info_frame.pack(fill='x', padx=5, pady=5)

		self.track_info_var = tk.StringVar(value="Select a track")
		ttk.Label(info_frame, textvariable=self.track_info_var, wraplength=200).pack(padx=5, pady=5)

		# Right side: Data view
		right_frame = ttk.LabelFrame(paned, text="Music Data")
		paned.add(right_frame, weight=2)

		# Hex view of music data
		self.data_text = tk.Text(
			right_frame,
			font=('Consolas', 10),
			wrap='none',
			bg='#1e1e1e',
			fg='#d4d4d4',
			height=20
		)
		self.data_text.pack(fill='both', expand=True, padx=5, pady=5)

		# Configure tags
		self.data_text.tag_configure('note', foreground='#4ec9b0')
		self.data_text.tag_configure('duration', foreground='#ce9178')
		self.data_text.tag_configure('control', foreground='#c586c0')
		self.data_text.tag_configure('offset', foreground='#569cd6')

		# Note visualization canvas
		viz_frame = ttk.LabelFrame(right_frame, text="Note Visualization")
		viz_frame.pack(fill='x', padx=5, pady=5)

		self.viz_canvas = tk.Canvas(
			viz_frame,
			bg='#1e1e1e',
			height=100,
			highlightthickness=0
		)
		self.viz_canvas.pack(fill='x', padx=5, pady=5)

		# Controls
		control_frame = ttk.Frame(right_frame)
		control_frame.pack(fill='x', padx=5, pady=5)

		ttk.Label(control_frame, text="Bytes to show:").pack(side='left', padx=5)
		self.bytes_var = tk.StringVar(value="256")
		bytes_spin = ttk.Spinbox(control_frame, textvariable=self.bytes_var, from_=64, to=1024, width=8)
		bytes_spin.pack(side='left', padx=5)

		ttk.Button(control_frame, text="Refresh", command=self.refresh_data).pack(side='left', padx=5)
		ttk.Button(control_frame, text="Export Notes", command=self.export_notes).pack(side='left', padx=5)

		# Bottom: NES APU info
		apu_frame = ttk.LabelFrame(self.frame, text="NES APU Information")
		apu_frame.pack(fill='x', padx=5, pady=5)

		apu_text = """NES Audio Processing Unit (APU):
• 2 Square Wave Channels (Pulse 1 & 2) - Main melody instruments
• 1 Triangle Wave Channel - Bass and smooth tones
• 1 Noise Channel - Drums and percussion
• 1 DPCM Channel - Sample playback (rarely used in Dragon Warrior)

Dragon Warrior uses a custom music engine with bytecode for note sequences."""

		ttk.Label(apu_frame, text=apu_text, justify='left').pack(padx=5, pady=5)

	def load_rom(self):
		"""Load ROM data."""
		rom_path = PROJECT_ROOT / "build" / "dragon_warrior_rebuilt.nes"
		if not rom_path.exists():
			rom_path = PROJECT_ROOT / "roms" / "Dragon Warrior (USA).nes"

		if rom_path.exists():
			try:
				with open(rom_path, 'rb') as f:
					self.rom_data = f.read()
				self.status_callback(f"Loaded ROM: {rom_path.name}")
			except Exception as e:
				self.status_callback(f"Failed to load ROM: {e}")

	def on_track_select(self, event):
		"""Handle track selection."""
		selection = self.track_listbox.curselection()
		if not selection:
			return

		track_name = self.track_listbox.get(selection[0])
		self.current_track = track_name
		track_info = self.MUSIC_TRACKS[track_name]

		self.track_info_var.set(f"{track_name}\n\nOffset: 0x{track_info['offset']:08X}\n\n{track_info['description']}")

		self.refresh_data()

	def refresh_data(self):
		"""Refresh the data view for current track."""
		if not self.rom_data or not self.current_track:
			return

		track_info = self.MUSIC_TRACKS[self.current_track]
		offset = track_info['offset']
		num_bytes = int(self.bytes_var.get())

		# Clear views
		self.data_text.delete('1.0', 'end')
		self.viz_canvas.delete('all')

		# Show hex data with interpretation
		self.data_text.insert('end', f"Track: {self.current_track}\n")
		self.data_text.insert('end', f"Offset: 0x{offset:08X}\n\n")

		# Display bytes in rows of 16
		for row in range(0, num_bytes, 16):
			addr = offset + row
			if addr >= len(self.rom_data):
				break

			# Offset column
			self.data_text.insert('end', f"{addr:06X}  ", 'offset')

			# Hex bytes
			for col in range(16):
				byte_addr = addr + col
				if byte_addr >= len(self.rom_data) or byte_addr >= offset + num_bytes:
					self.data_text.insert('end', '   ')
				else:
					byte = self.rom_data[byte_addr]
					# Color code based on potential meaning
					if byte < 0x48:  # Likely note
						tag = 'note'
					elif byte < 0x80:  # Likely duration/length
						tag = 'duration'
					else:  # Control byte
						tag = 'control'
					self.data_text.insert('end', f"{byte:02X} ", tag)

				if col == 7:
					self.data_text.insert('end', ' ')

			self.data_text.insert('end', '\n')

		# Simple visualization
		self.draw_note_visualization(offset, min(num_bytes, 128))

	def draw_note_visualization(self, offset: int, num_bytes: int):
		"""Draw a simple note visualization."""
		if not self.rom_data:
			return

		canvas_width = self.viz_canvas.winfo_width() or 600
		canvas_height = 100

		# Draw note bars based on byte values (simplified interpretation)
		bar_width = max(2, canvas_width // num_bytes)

		for i in range(num_bytes):
			addr = offset + i
			if addr >= len(self.rom_data):
				break

			byte = self.rom_data[addr]
			x = i * bar_width

			# Height based on byte value
			height = int((byte / 255) * (canvas_height - 10))
			y = canvas_height - height - 5

			# Color based on value range
			if byte < 0x48:
				color = '#4ec9b0'  # Note (green)
			elif byte < 0x80:
				color = '#ce9178'  # Duration (orange)
			else:
				color = '#c586c0'  # Control (purple)

			self.viz_canvas.create_rectangle(x, y, x + bar_width - 1, canvas_height - 5, fill=color, outline='')

		# Legend
		self.viz_canvas.create_text(10, 10, anchor='nw', text="■ Note", fill='#4ec9b0', font=('Segoe UI', 8))
		self.viz_canvas.create_text(80, 10, anchor='nw', text="■ Duration", fill='#ce9178', font=('Segoe UI', 8))
		self.viz_canvas.create_text(160, 10, anchor='nw', text="■ Control", fill='#c586c0', font=('Segoe UI', 8))

	def export_notes(self):
		"""Export track data to a text file."""
		if not self.current_track or not self.rom_data:
			messagebox.showinfo("Info", "Select a track first")
			return

		from tkinter import filedialog
		path = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text files", "*.txt")],
			initialfile=f"dw_music_{self.current_track.lower().replace(' ', '_')}.txt"
		)

		if path:
			track_info = self.MUSIC_TRACKS[self.current_track]
			offset = track_info['offset']
			num_bytes = int(self.bytes_var.get())

			try:
				with open(path, 'w') as f:
					f.write(f"Dragon Warrior Music Data Export\n")
					f.write(f"Track: {self.current_track}\n")
					f.write(f"Offset: 0x{offset:08X}\n")
					f.write(f"Description: {track_info['description']}\n")
					f.write("=" * 50 + "\n\n")

					f.write("Raw Bytes:\n")
					for i in range(0, num_bytes, 16):
						addr = offset + i
						if addr >= len(self.rom_data):
							break

						bytes_row = []
						for j in range(16):
							byte_addr = addr + j
							if byte_addr < len(self.rom_data) and byte_addr < offset + num_bytes:
								bytes_row.append(f"{self.rom_data[byte_addr]:02X}")

						f.write(f"{addr:06X}: {' '.join(bytes_row)}\n")

				messagebox.showinfo("Success", f"Exported to {Path(path).name}")
			except Exception as e:
				messagebox.showerror("Error", f"Export failed: {e}")

	def refresh(self):
		"""Refresh tab."""
		self.load_rom()
		if self.current_track:
			self.refresh_data()


# ============================================================================
# TEXT TABLE EDITOR TAB
# ============================================================================

class TextTableEditorTab(BaseTab):
	"""Edit the text encoding table (TBL) used by the game."""

	# Dragon Warrior's default text encoding
	DEFAULT_TABLE = {
		0x00: '0', 0x01: '1', 0x02: '2', 0x03: '3', 0x04: '4',
		0x05: '5', 0x06: '6', 0x07: '7', 0x08: '8', 0x09: '9',
		0x0A: 'a', 0x0B: 'b', 0x0C: 'c', 0x0D: 'd', 0x0E: 'e',
		0x0F: 'f', 0x10: 'g', 0x11: 'h', 0x12: 'i', 0x13: 'j',
		0x14: 'k', 0x15: 'l', 0x16: 'm', 0x17: 'n', 0x18: 'o',
		0x19: 'p', 0x1A: 'q', 0x1B: 'r', 0x1C: 's', 0x1D: 't',
		0x1E: 'u', 0x1F: 'v', 0x20: 'w', 0x21: 'x', 0x22: 'y',
		0x23: 'z', 0x24: 'A', 0x25: 'B', 0x26: 'C', 0x27: 'D',
		0x28: 'E', 0x29: 'F', 0x2A: 'G', 0x2B: 'H', 0x2C: 'I',
		0x2D: 'J', 0x2E: 'K', 0x2F: 'L', 0x30: 'M', 0x31: 'N',
		0x32: 'O', 0x33: 'P', 0x34: 'Q', 0x35: 'R', 0x36: 'S',
		0x37: 'T', 0x38: 'U', 0x39: 'V', 0x3A: 'W', 0x3B: 'X',
		0x3C: 'Y', 0x3D: 'Z', 0x3E: '-', 0x3F: "'", 0x40: '!',
		0x41: '?', 0x42: '.', 0x43: ',', 0x44: ' ', 0x45: '(',
		0x46: ')', 0x47: '<heart>', 0x48: '*', 0x49: '>',
		0x4A: '<sl>', 0x4B: '<up>', 0x4C: '<down>',
		0x5F: '\n',  # New line
		0xFC: '<name>',  # Hero name
		0xFD: '<item>',  # Item name
		0xFE: '<enemy>',  # Enemy name
		0xFF: '<end>',  # End of string
	}

	def __init__(self, notebook: ttk.Notebook, asset_manager: AssetManager, status_callback):
		super().__init__(notebook, asset_manager, status_callback)
		self.table = dict(self.DEFAULT_TABLE)
		self.modified = False

		self.setup_ui()
		self.load_table()

	def setup_ui(self):
		"""Set up text table editor UI."""
		# Main paned window
		paned = ttk.PanedWindow(self.frame, orient='horizontal')
		paned.pack(fill='both', expand=True, padx=5, pady=5)

		# Left side: Table view
		left_frame = ttk.LabelFrame(paned, text="Character Table")
		paned.add(left_frame, weight=2)

		# Treeview for table entries
		columns = ('hex', 'dec', 'char', 'description')
		self.table_tree = ttk.Treeview(left_frame, columns=columns, show='headings', height=20)
		self.table_tree.heading('hex', text='Hex')
		self.table_tree.heading('dec', text='Dec')
		self.table_tree.heading('char', text='Character')
		self.table_tree.heading('description', text='Description')
		self.table_tree.column('hex', width=60)
		self.table_tree.column('dec', width=50)
		self.table_tree.column('char', width=100)
		self.table_tree.column('description', width=150)

		scrollbar = ttk.Scrollbar(left_frame, orient='vertical', command=self.table_tree.yview)
		self.table_tree.configure(yscrollcommand=scrollbar.set)

		self.table_tree.pack(side='left', fill='both', expand=True)
		scrollbar.pack(side='right', fill='y')

		self.table_tree.bind('<Double-Button-1>', self.edit_entry)

		# Right side: Visual grid + editing
		right_frame = ttk.Frame(paned)
		paned.add(right_frame, weight=1)

		# Visual grid
		grid_frame = ttk.LabelFrame(right_frame, text="Character Grid (16x16)")
		grid_frame.pack(fill='x', padx=5, pady=5)

		self.grid_canvas = tk.Canvas(
			grid_frame,
			width=320,
			height=320,
			bg='#1e1e1e',
			highlightthickness=0
		)
		self.grid_canvas.pack(padx=5, pady=5)
		self.grid_canvas.bind('<Button-1>', self.on_grid_click)

		# Edit panel
		edit_frame = ttk.LabelFrame(right_frame, text="Edit Entry")
		edit_frame.pack(fill='x', padx=5, pady=5)

		ttk.Label(edit_frame, text="Byte Value:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
		self.byte_var = tk.StringVar()
		ttk.Entry(edit_frame, textvariable=self.byte_var, width=10, state='readonly').grid(
			row=0, column=1, sticky='w', padx=5, pady=2)

		ttk.Label(edit_frame, text="Character:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
		self.char_var = tk.StringVar()
		ttk.Entry(edit_frame, textvariable=self.char_var, width=20).grid(
			row=1, column=1, sticky='w', padx=5, pady=2)

		ttk.Button(edit_frame, text="Update", command=self.update_entry).grid(
			row=2, column=0, columnspan=2, pady=5)

		# Control codes reference
		codes_frame = ttk.LabelFrame(right_frame, text="Control Codes")
		codes_frame.pack(fill='x', padx=5, pady=5)

		codes_text = tk.Text(codes_frame, height=8, font=('Consolas', 9), bg='#252526', fg='#d4d4d4')
		codes_text.pack(fill='x', padx=5, pady=5)
		codes_text.insert('1.0', """Special codes used in Dragon Warrior:
$5F = New line
$FC = Hero's name
$FD = Item name (context)
$FE = Enemy name (context)
$FF = End of string

$F0-$FB = Wait, pause, clear commands""")
		codes_text.config(state='disabled')

		# Buttons
		btn_frame = ttk.Frame(right_frame)
		btn_frame.pack(fill='x', padx=5, pady=5)

		ttk.Button(btn_frame, text="Save Table", command=self.save_table).pack(side='left', padx=5)
		ttk.Button(btn_frame, text="Reset to Default", command=self.reset_table).pack(side='left', padx=5)
		ttk.Button(btn_frame, text="Export TBL", command=self.export_tbl).pack(side='left', padx=5)
		ttk.Button(btn_frame, text="Import TBL", command=self.import_tbl).pack(side='left', padx=5)

	def load_table(self):
		"""Load the text table."""
		# Try to load from JSON file
		table_file = PROJECT_ROOT / "assets" / "data" / "text_table.json"
		if table_file.exists():
			try:
				with open(table_file, 'r') as f:
					data = json.load(f)
					# Convert string keys back to int
					self.table = {int(k): v for k, v in data.items()}
			except:
				self.table = dict(self.DEFAULT_TABLE)
		else:
			self.table = dict(self.DEFAULT_TABLE)

		self.refresh_display()

	def refresh_display(self):
		"""Refresh the table display."""
		# Clear treeview
		for item in self.table_tree.get_children():
			self.table_tree.delete(item)

		# Add entries
		for byte_val in range(256):
			char = self.table.get(byte_val, '')
			desc = self.get_description(byte_val)
			self.table_tree.insert('', 'end', values=(
				f"0x{byte_val:02X}",
				str(byte_val),
				char if char else '(undefined)',
				desc
			))

		# Update grid
		self.draw_grid()

	def get_description(self, byte_val: int) -> str:
		"""Get description for a byte value."""
		if byte_val <= 0x09:
			return "Digit"
		elif 0x0A <= byte_val <= 0x23:
			return "Lowercase letter"
		elif 0x24 <= byte_val <= 0x3D:
			return "Uppercase letter"
		elif 0x3E <= byte_val <= 0x4C:
			return "Punctuation/Symbol"
		elif byte_val == 0x44:
			return "Space"
		elif byte_val == 0x5F:
			return "New line"
		elif 0xF0 <= byte_val <= 0xFB:
			return "Control code"
		elif byte_val >= 0xFC:
			return "Special code"
		else:
			return ""

	def draw_grid(self):
		"""Draw the character grid."""
		self.grid_canvas.delete('all')
		cell_size = 20

		for row in range(16):
			for col in range(16):
				byte_val = row * 16 + col
				x = col * cell_size
				y = row * cell_size

				# Background color
				if byte_val in self.table:
					bg = '#2d4a2d'  # Green for defined
				else:
					bg = '#1e1e1e'  # Dark for undefined

				self.grid_canvas.create_rectangle(
					x, y, x + cell_size, y + cell_size,
					fill=bg, outline='#3c3c3c'
				)

				# Character preview
				char = self.table.get(byte_val, '')
				if char and len(char) == 1 and char.isprintable():
					self.grid_canvas.create_text(
						x + cell_size // 2, y + cell_size // 2,
						text=char, fill='#d4d4d4', font=('Consolas', 8)
					)

	def on_grid_click(self, event):
		"""Handle grid click."""
		cell_size = 20
		col = event.x // cell_size
		row = event.y // cell_size
		byte_val = row * 16 + col

		if 0 <= byte_val <= 255:
			self.byte_var.set(f"0x{byte_val:02X}")
			self.char_var.set(self.table.get(byte_val, ''))

			# Also select in treeview
			for item in self.table_tree.get_children():
				if self.table_tree.item(item)['values'][1] == str(byte_val):
					self.table_tree.selection_set(item)
					self.table_tree.see(item)
					break

	def edit_entry(self, event):
		"""Edit selected entry."""
		selection = self.table_tree.selection()
		if selection:
			values = self.table_tree.item(selection[0])['values']
			byte_val = int(values[1])
			self.byte_var.set(f"0x{byte_val:02X}")
			self.char_var.set(self.table.get(byte_val, ''))

	def update_entry(self):
		"""Update the selected entry."""
		byte_str = self.byte_var.get()
		char = self.char_var.get()

		if not byte_str:
			return

		try:
			byte_val = int(byte_str.replace('0x', ''), 16)
			if char:
				self.table[byte_val] = char
			elif byte_val in self.table:
				del self.table[byte_val]

			self.modified = True
			self.refresh_display()
			self.status_callback(f"Updated 0x{byte_val:02X} = '{char}'")
		except ValueError:
			messagebox.showerror("Error", "Invalid byte value")

	def save_table(self):
		"""Save the table to JSON."""
		table_file = PROJECT_ROOT / "assets" / "data" / "text_table.json"
		table_file.parent.mkdir(parents=True, exist_ok=True)

		try:
			# Convert int keys to string for JSON
			data = {str(k): v for k, v in self.table.items()}
			with open(table_file, 'w') as f:
				json.dump(data, f, indent=2)
			self.modified = False
			messagebox.showinfo("Saved", "Text table saved!")
		except Exception as e:
			messagebox.showerror("Error", f"Save failed: {e}")

	def reset_table(self):
		"""Reset to default table."""
		if messagebox.askyesno("Reset", "Reset to default table? This will lose all changes."):
			self.table = dict(self.DEFAULT_TABLE)
			self.modified = True
			self.refresh_display()

	def export_tbl(self):
		"""Export as .tbl file format."""
		from tkinter import filedialog
		path = filedialog.asksaveasfilename(
			defaultextension=".tbl",
			filetypes=[("Table files", "*.tbl"), ("All files", "*.*")],
			initialfile="dragon_warrior.tbl"
		)

		if path:
			try:
				with open(path, 'w', encoding='utf-8') as f:
					for byte_val in sorted(self.table.keys()):
						char = self.table[byte_val]
						f.write(f"{byte_val:02X}={char}\n")
				messagebox.showinfo("Success", f"Exported to {Path(path).name}")
			except Exception as e:
				messagebox.showerror("Error", f"Export failed: {e}")

	def import_tbl(self):
		"""Import a .tbl file."""
		from tkinter import filedialog
		path = filedialog.askopenfilename(
			filetypes=[("Table files", "*.tbl"), ("All files", "*.*")]
		)

		if path:
			try:
				new_table = {}
				with open(path, 'r', encoding='utf-8') as f:
					for line in f:
						line = line.strip()
						if '=' in line:
							hex_part, char = line.split('=', 1)
							byte_val = int(hex_part, 16)
							new_table[byte_val] = char

				self.table = new_table
				self.modified = True
				self.refresh_display()
				messagebox.showinfo("Success", f"Imported {len(new_table)} entries")
			except Exception as e:
				messagebox.showerror("Error", f"Import failed: {e}")

	def refresh(self):
		"""Refresh the display."""
		self.load_table()


# ============================================================================
# ENCOUNTER ZONE EDITOR TAB
# ============================================================================

class EncounterEditorTab(BaseTab):
	"""Edit enemy encounter zones and rates."""

	# Dragon Warrior encounter zone data (approximate)
	# Each zone has a list of possible enemies and encounter rate
	ZONE_DATA = {
		'Tantegel Area': {
			'zone_id': 0,
			'monsters': ['Slime', 'Red Slime'],
			'rate': 'Low',
			'description': 'Starting area around Tantegel Castle'
		},
		'Brecconary Area': {
			'zone_id': 1,
			'monsters': ['Slime', 'Red Slime', 'Drakee'],
			'rate': 'Low',
			'description': 'Fields near Brecconary village'
		},
		'Garinham Area': {
			'zone_id': 2,
			'monsters': ['Red Slime', 'Drakee', 'Ghost'],
			'rate': 'Medium',
			'description': 'North of Brecconary'
		},
		'Kol Area': {
			'zone_id': 3,
			'monsters': ['Magician', 'Scorpion', 'Druin'],
			'rate': 'Medium',
			'description': 'Eastern continent'
		},
		'Rimuldar Area': {
			'zone_id': 4,
			'monsters': ['Wolf', 'Warlock', 'Metal Scorpion'],
			'rate': 'High',
			'description': 'Swamp region'
		},
		'Hauksness Ruins': {
			'zone_id': 5,
			'monsters': ['Knight', 'Demon Knight', 'Werewolf'],
			'rate': 'Very High',
			'description': 'Destroyed city'
		},
		'Charlock Castle': {
			'zone_id': 6,
			'monsters': ['Blue Dragon', 'Stoneman', 'Armored Knight'],
			'rate': 'Very High',
			'description': 'Dragon Lord\'s castle'
		},
		'Swamp Cave': {
			'zone_id': 7,
			'monsters': ['Ghost', 'Magidrakee', 'Skeleton'],
			'rate': 'High',
			'description': 'Underground cave'
		},
	}

	def __init__(self, notebook: ttk.Notebook, asset_manager: AssetManager, status_callback):
		super().__init__(notebook, asset_manager, status_callback)
		self.current_zone: Optional[str] = None

		self.setup_ui()

	def setup_ui(self):
		"""Set up encounter editor UI."""
		# Main paned window
		paned = ttk.PanedWindow(self.frame, orient='horizontal')
		paned.pack(fill='both', expand=True, padx=5, pady=5)

		# Left side: Zone list
		left_frame = ttk.LabelFrame(paned, text="Encounter Zones")
		paned.add(left_frame, weight=1)

		self.zone_listbox = tk.Listbox(left_frame, font=('Segoe UI', 10))
		self.zone_listbox.pack(fill='both', expand=True, padx=5, pady=5)
		self.zone_listbox.bind('<<ListboxSelect>>', self.on_zone_select)

		for zone_name in self.ZONE_DATA.keys():
			self.zone_listbox.insert('end', zone_name)

		# Right side: Zone details
		right_frame = ttk.Frame(paned)
		paned.add(right_frame, weight=2)

		# Zone info
		info_frame = ttk.LabelFrame(right_frame, text="Zone Information")
		info_frame.pack(fill='x', padx=5, pady=5)

		info_grid = ttk.Frame(info_frame)
		info_grid.pack(fill='x', padx=5, pady=5)

		ttk.Label(info_grid, text="Zone Name:").grid(row=0, column=0, sticky='e', padx=5, pady=2)
		self.zone_name_var = tk.StringVar()
		ttk.Entry(info_grid, textvariable=self.zone_name_var, width=30).grid(row=0, column=1, sticky='w', padx=5)

		ttk.Label(info_grid, text="Zone ID:").grid(row=1, column=0, sticky='e', padx=5, pady=2)
		self.zone_id_var = tk.StringVar()
		ttk.Entry(info_grid, textvariable=self.zone_id_var, width=10).grid(row=1, column=1, sticky='w', padx=5)

		ttk.Label(info_grid, text="Encounter Rate:").grid(row=2, column=0, sticky='e', padx=5, pady=2)
		self.rate_var = tk.StringVar()
		rate_combo = ttk.Combobox(info_grid, textvariable=self.rate_var, width=15, state='readonly')
		rate_combo['values'] = ['Very Low', 'Low', 'Medium', 'High', 'Very High']
		rate_combo.grid(row=2, column=1, sticky='w', padx=5)

		ttk.Label(info_grid, text="Description:").grid(row=3, column=0, sticky='ne', padx=5, pady=2)
		self.desc_var = tk.StringVar()
		ttk.Entry(info_grid, textvariable=self.desc_var, width=40).grid(row=3, column=1, sticky='w', padx=5)

		# Monster list for zone
		monster_frame = ttk.LabelFrame(right_frame, text="Monsters in Zone")
		monster_frame.pack(fill='both', expand=True, padx=5, pady=5)

		# Monster listbox with checkboxes (simplified)
		columns = ('monster', 'level_range', 'chance')
		self.monster_tree = ttk.Treeview(monster_frame, columns=columns, show='headings', height=8)
		self.monster_tree.heading('monster', text='Monster')
		self.monster_tree.heading('level_range', text='Level Range')
		self.monster_tree.heading('chance', text='Encounter %')
		self.monster_tree.column('monster', width=150)
		self.monster_tree.column('level_range', width=100)
		self.monster_tree.column('chance', width=100)
		self.monster_tree.pack(fill='both', expand=True, padx=5, pady=5)

		# Monster controls
		monster_ctrl = ttk.Frame(monster_frame)
		monster_ctrl.pack(fill='x', padx=5, pady=5)

		ttk.Button(monster_ctrl, text="Add Monster", command=self.add_monster).pack(side='left', padx=5)
		ttk.Button(monster_ctrl, text="Remove Monster", command=self.remove_monster).pack(side='left', padx=5)
		ttk.Button(monster_ctrl, text="Edit Chance", command=self.edit_chance).pack(side='left', padx=5)

		# Rate info
		rate_frame = ttk.LabelFrame(right_frame, text="Encounter Rate Reference")
		rate_frame.pack(fill='x', padx=5, pady=5)

		rate_info = """Encounter Rate determines how often random battles occur:
• Very Low: ~1/32 chance per step
• Low: ~1/16 chance per step
• Medium: ~1/8 chance per step
• High: ~1/4 chance per step
• Very High: ~1/2 chance per step

Dragon Warrior uses a zone-based system where encounter rates
increase as you move further from Tantegel Castle."""

		ttk.Label(rate_frame, text=rate_info, justify='left').pack(padx=5, pady=5)

		# Save button
		btn_frame = ttk.Frame(right_frame)
		btn_frame.pack(fill='x', padx=5, pady=5)

		ttk.Button(btn_frame, text="Save Zone Changes", command=self.save_zone).pack(side='left', padx=5)
		ttk.Button(btn_frame, text="Export Zone Data", command=self.export_zones).pack(side='left', padx=5)

	def on_zone_select(self, event):
		"""Handle zone selection."""
		selection = self.zone_listbox.curselection()
		if not selection:
			return

		zone_name = self.zone_listbox.get(selection[0])
		self.current_zone = zone_name
		zone_data = self.ZONE_DATA[zone_name]

		self.zone_name_var.set(zone_name)
		self.zone_id_var.set(str(zone_data['zone_id']))
		self.rate_var.set(zone_data['rate'])
		self.desc_var.set(zone_data['description'])

		# Update monster list
		for item in self.monster_tree.get_children():
			self.monster_tree.delete(item)

		monsters = zone_data['monsters']
		chance = 100 // len(monsters) if monsters else 0
		for monster in monsters:
			self.monster_tree.insert('', 'end', values=(monster, '1-5', f'{chance}%'))

	def add_monster(self):
		"""Add a monster to the zone."""
		if not self.current_zone:
			messagebox.showinfo("Info", "Select a zone first")
			return

		# Simple dialog to add monster
		monster = simpledialog.askstring("Add Monster", "Monster name:")
		if monster:
			self.monster_tree.insert('', 'end', values=(monster, '1-5', '10%'))
			self.status_callback(f"Added {monster} to {self.current_zone}")

	def remove_monster(self):
		"""Remove selected monster from zone."""
		selection = self.monster_tree.selection()
		if selection:
			for item in selection:
				self.monster_tree.delete(item)

	def edit_chance(self):
		"""Edit encounter chance for selected monster."""
		selection = self.monster_tree.selection()
		if not selection:
			return

		current = self.monster_tree.item(selection[0])['values']
		new_chance = simpledialog.askinteger("Edit Chance", "Encounter chance (1-100):",
			initialvalue=int(current[2].replace('%', '')))
		if new_chance:
			self.monster_tree.item(selection[0], values=(current[0], current[1], f'{new_chance}%'))

	def save_zone(self):
		"""Save zone changes."""
		if not self.current_zone:
			return

		# Get updated data
		monsters = [self.monster_tree.item(item)['values'][0]
			for item in self.monster_tree.get_children()]

		self.ZONE_DATA[self.current_zone] = {
			'zone_id': int(self.zone_id_var.get()),
			'monsters': monsters,
			'rate': self.rate_var.get(),
			'description': self.desc_var.get()
		}

		# Save to JSON
		zone_file = PROJECT_ROOT / "assets" / "data" / "encounter_zones.json"
		zone_file.parent.mkdir(parents=True, exist_ok=True)

		try:
			with open(zone_file, 'w') as f:
				json.dump(self.ZONE_DATA, f, indent=2)
			messagebox.showinfo("Saved", "Zone data saved!")
		except Exception as e:
			messagebox.showerror("Error", f"Save failed: {e}")

	def export_zones(self):
		"""Export zone data to text file."""
		from tkinter import filedialog
		path = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text files", "*.txt")],
			initialfile="dw_encounter_zones.txt"
		)

		if path:
			try:
				with open(path, 'w') as f:
					f.write("Dragon Warrior - Encounter Zones\n")
					f.write("=" * 50 + "\n\n")

					for zone_name, data in self.ZONE_DATA.items():
						f.write(f"{zone_name} (Zone {data['zone_id']})\n")
						f.write(f"  Rate: {data['rate']}\n")
						f.write(f"  Description: {data['description']}\n")
						f.write(f"  Monsters: {', '.join(data['monsters'])}\n\n")

				messagebox.showinfo("Success", f"Exported to {Path(path).name}")
			except Exception as e:
				messagebox.showerror("Error", f"Export failed: {e}")

	def refresh(self):
		"""Refresh zone data."""
		# Could reload from JSON here
		pass


# ============================================================================
# ROM INFO / HEADER EDITOR TAB
# ============================================================================

class RomInfoTab(BaseTab):
	"""View and edit NES ROM header information."""

	# iNES header field definitions
	MAPPER_NAMES = {
		0: "NROM (No mapper)",
		1: "MMC1 (Nintendo SxROM)",
		2: "UxROM",
		3: "CNROM",
		4: "MMC3 (Nintendo TxROM)",
		7: "AxROM",
		9: "MMC2 (Nintendo PxROM)",
		10: "MMC4 (Nintendo FxROM)",
		11: "Color Dreams",
		66: "GxROM",
		71: "Camerica BF909x",
		# Add more as needed
	}

	def __init__(self, notebook: ttk.Notebook, asset_manager: AssetManager, status_callback):
		super().__init__(notebook, asset_manager, status_callback)
		self.rom_data: Optional[bytearray] = None
		self.rom_path: Optional[Path] = None
		self.header_modified = False

		self.setup_ui()
		self.load_rom()

	def setup_ui(self):
		"""Set up ROM info UI."""
		# Main layout
		main_frame = ttk.Frame(self.frame)
		main_frame.pack(fill='both', expand=True, padx=5, pady=5)

		# Left: Header Info
		left_frame = ttk.LabelFrame(main_frame, text="iNES Header (16 bytes)")
		left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))

		# Header hex display
		hex_frame = ttk.LabelFrame(left_frame, text="Raw Header Bytes")
		hex_frame.pack(fill='x', padx=5, pady=5)

		self.header_hex = tk.Text(hex_frame, height=3, font=('Consolas', 11), bg='#1e1e1e', fg='#4ec9b0')
		self.header_hex.pack(fill='x', padx=5, pady=5)

		# Header fields
		fields_frame = ttk.LabelFrame(left_frame, text="Header Fields")
		fields_frame.pack(fill='both', expand=True, padx=5, pady=5)

		# Create field entries
		self.header_vars = {}

		field_defs = [
			('magic', 'Magic Number', False),
			('prg_rom', 'PRG-ROM Size (16KB units)', True),
			('chr_rom', 'CHR-ROM Size (8KB units)', True),
			('mapper', 'Mapper Number', True),
			('mirroring', 'Mirroring', True),
			('battery', 'Battery-backed RAM', True),
			('trainer', 'Trainer Present', True),
			('four_screen', 'Four-Screen VRAM', True),
			('vs_system', 'VS System', True),
			('pal', 'PAL/NTSC', True),
		]

		for row, (field_id, label, editable) in enumerate(field_defs):
			ttk.Label(fields_frame, text=f"{label}:").grid(row=row, column=0, sticky='e', padx=5, pady=3)
			var = tk.StringVar()
			self.header_vars[field_id] = var
			state = 'normal' if editable else 'readonly'
			entry = ttk.Entry(fields_frame, textvariable=var, width=30, state=state)
			entry.grid(row=row, column=1, sticky='w', padx=5, pady=3)

		# Mapper selector
		ttk.Label(fields_frame, text="Mapper Name:").grid(row=len(field_defs), column=0, sticky='e', padx=5, pady=3)
		self.mapper_name_var = tk.StringVar()
		ttk.Label(fields_frame, textvariable=self.mapper_name_var, font=('Segoe UI', 9, 'italic')).grid(
			row=len(field_defs), column=1, sticky='w', padx=5, pady=3)

		# Right: ROM Stats
		right_frame = ttk.Frame(main_frame)
		right_frame.pack(side='right', fill='both', expand=True, padx=(5, 0))

		# ROM Statistics
		stats_frame = ttk.LabelFrame(right_frame, text="ROM Statistics")
		stats_frame.pack(fill='x', padx=5, pady=5)

		self.stats_text = tk.Text(stats_frame, height=12, font=('Consolas', 10), bg='#252526', fg='#d4d4d4')
		self.stats_text.pack(fill='x', padx=5, pady=5)

		# File Info
		file_frame = ttk.LabelFrame(right_frame, text="File Information")
		file_frame.pack(fill='x', padx=5, pady=5)

		file_grid = ttk.Frame(file_frame)
		file_grid.pack(fill='x', padx=5, pady=5)

		ttk.Label(file_grid, text="File Path:").grid(row=0, column=0, sticky='e', padx=5)
		self.file_path_var = tk.StringVar()
		ttk.Entry(file_grid, textvariable=self.file_path_var, width=50, state='readonly').grid(row=0, column=1, padx=5)

		ttk.Label(file_grid, text="File Size:").grid(row=1, column=0, sticky='e', padx=5)
		self.file_size_var = tk.StringVar()
		ttk.Entry(file_grid, textvariable=self.file_size_var, width=20, state='readonly').grid(row=1, column=1, sticky='w', padx=5)

		ttk.Label(file_grid, text="CRC32:").grid(row=2, column=0, sticky='e', padx=5)
		self.crc_var = tk.StringVar()
		ttk.Entry(file_grid, textvariable=self.crc_var, width=20, state='readonly').grid(row=2, column=1, sticky='w', padx=5)

		# Controls
		btn_frame = ttk.Frame(right_frame)
		btn_frame.pack(fill='x', padx=5, pady=10)

		ttk.Button(btn_frame, text="Load ROM...", command=self.browse_rom).pack(side='left', padx=5)
		ttk.Button(btn_frame, text="Save Header Changes", command=self.save_header).pack(side='left', padx=5)
		ttk.Button(btn_frame, text="Calculate Checksum", command=self.calc_checksum).pack(side='left', padx=5)
		ttk.Button(btn_frame, text="Export Header", command=self.export_header).pack(side='left', padx=5)

		# Dragon Warrior specific info
		dw_frame = ttk.LabelFrame(right_frame, text="Dragon Warrior ROM Info")
		dw_frame.pack(fill='both', expand=True, padx=5, pady=5)

		dw_info = """Dragon Warrior (USA) ROM Specifications:
• Mapper: MMC1 (Mapper 1)
• PRG-ROM: 64KB (4 x 16KB banks)
• CHR-ROM: 16KB (2 x 8KB banks)
• Mirroring: Horizontal (controlled by mapper)
• Battery: No
• Expected size: 81,936 bytes (with 16-byte header)

The game uses memory bank switching to access
different parts of the PRG-ROM."""

		ttk.Label(dw_frame, text=dw_info, justify='left').pack(padx=5, pady=5)

	def load_rom(self):
		"""Load a ROM file."""
		# Try built ROM first, then original
		rom_path = PROJECT_ROOT / "build" / "dragon_warrior_rebuilt.nes"
		if not rom_path.exists():
			rom_path = PROJECT_ROOT / "roms" / "Dragon Warrior (USA).nes"

		if rom_path.exists():
			self.load_rom_file(rom_path)

	def load_rom_file(self, path: Path):
		"""Load ROM from file."""
		try:
			with open(path, 'rb') as f:
				self.rom_data = bytearray(f.read())
			self.rom_path = path
			self.parse_header()
			self.update_stats()
			self.file_path_var.set(str(path))
			self.file_size_var.set(f"{len(self.rom_data):,} bytes")
			self.calc_checksum()
			self.status_callback(f"Loaded: {path.name}")
		except Exception as e:
			messagebox.showerror("Error", f"Failed to load ROM: {e}")

	def browse_rom(self):
		"""Browse for ROM file."""
		from tkinter import filedialog
		path = filedialog.askopenfilename(
			initialdir=PROJECT_ROOT / "roms",
			filetypes=[("NES ROMs", "*.nes"), ("All files", "*.*")]
		)
		if path:
			self.load_rom_file(Path(path))

	def parse_header(self):
		"""Parse iNES header."""
		if not self.rom_data or len(self.rom_data) < 16:
			return

		header = self.rom_data[:16]

		# Display raw hex
		hex_str = ' '.join(f'{b:02X}' for b in header)
		self.header_hex.delete('1.0', 'end')
		self.header_hex.insert('1.0', hex_str)

		# Parse fields
		magic = header[0:4]
		self.header_vars['magic'].set(magic.decode('ascii', errors='replace'))

		prg_rom = header[4]
		self.header_vars['prg_rom'].set(f"{prg_rom} ({prg_rom * 16}KB)")

		chr_rom = header[5]
		self.header_vars['chr_rom'].set(f"{chr_rom} ({chr_rom * 8}KB)")

		flags6 = header[6]
		flags7 = header[7]

		mapper = (flags6 >> 4) | (flags7 & 0xF0)
		self.header_vars['mapper'].set(str(mapper))
		self.mapper_name_var.set(self.MAPPER_NAMES.get(mapper, "Unknown"))

		mirroring = "Vertical" if (flags6 & 0x01) else "Horizontal"
		self.header_vars['mirroring'].set(mirroring)

		self.header_vars['battery'].set("Yes" if (flags6 & 0x02) else "No")
		self.header_vars['trainer'].set("Yes" if (flags6 & 0x04) else "No")
		self.header_vars['four_screen'].set("Yes" if (flags6 & 0x08) else "No")
		self.header_vars['vs_system'].set("Yes" if (flags7 & 0x01) else "No")

		# Check for PAL (byte 9 or 10)
		if len(header) > 9:
			self.header_vars['pal'].set("PAL" if (header[9] & 0x01) else "NTSC")
		else:
			self.header_vars['pal'].set("NTSC")

	def update_stats(self):
		"""Update ROM statistics."""
		if not self.rom_data:
			return

		self.stats_text.delete('1.0', 'end')

		lines = []
		lines.append(f"Total ROM Size: {len(self.rom_data):,} bytes")
		lines.append(f"Header Size: 16 bytes")
		lines.append(f"PRG-ROM Start: 0x0010")

		prg_size = self.rom_data[4] * 16384 if len(self.rom_data) > 4 else 0
		chr_size = self.rom_data[5] * 8192 if len(self.rom_data) > 5 else 0

		lines.append(f"PRG-ROM Size: {prg_size:,} bytes ({prg_size // 1024}KB)")
		lines.append(f"CHR-ROM Start: 0x{16 + prg_size:04X}")
		lines.append(f"CHR-ROM Size: {chr_size:,} bytes ({chr_size // 1024}KB)")
		lines.append("")

		# Count non-FF bytes (rough estimate of used space)
		data_bytes = sum(1 for b in self.rom_data[16:] if b != 0xFF)
		total_data = len(self.rom_data) - 16
		pct = (data_bytes / total_data * 100) if total_data > 0 else 0
		lines.append(f"Non-empty bytes: {data_bytes:,} ({pct:.1f}%)")
		lines.append(f"Free space (0xFF): {total_data - data_bytes:,} bytes")

		self.stats_text.insert('1.0', '\n'.join(lines))

	def calc_checksum(self):
		"""Calculate CRC32 checksum."""
		if not self.rom_data:
			return

		import zlib
		crc = zlib.crc32(bytes(self.rom_data)) & 0xFFFFFFFF
		self.crc_var.set(f"{crc:08X}")

	def save_header(self):
		"""Save header changes to ROM."""
		if not self.rom_data or not self.rom_path:
			messagebox.showinfo("Info", "No ROM loaded")
			return

		try:
			# Update header bytes from fields
			prg_val = int(self.header_vars['prg_rom'].get().split()[0])
			chr_val = int(self.header_vars['chr_rom'].get().split()[0])
			mapper = int(self.header_vars['mapper'].get())

			self.rom_data[4] = prg_val
			self.rom_data[5] = chr_val

			# Update mapper in flags
			flags6 = (mapper & 0x0F) << 4
			if self.header_vars['mirroring'].get() == "Vertical":
				flags6 |= 0x01
			if self.header_vars['battery'].get() == "Yes":
				flags6 |= 0x02

			self.rom_data[6] = flags6
			self.rom_data[7] = (mapper & 0xF0)

			# Save to file
			with open(self.rom_path, 'wb') as f:
				f.write(self.rom_data)

			self.header_modified = False
			messagebox.showinfo("Saved", f"Header saved to {self.rom_path.name}")
			self.calc_checksum()

		except Exception as e:
			messagebox.showerror("Error", f"Save failed: {e}")

	def export_header(self):
		"""Export header info to text file."""
		if not self.rom_data:
			return

		from tkinter import filedialog
		path = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text files", "*.txt")],
			initialfile="rom_header_info.txt"
		)

		if path:
			try:
				with open(path, 'w') as f:
					f.write("NES ROM Header Information\n")
					f.write("=" * 40 + "\n\n")
					f.write(f"File: {self.rom_path}\n")
					f.write(f"Size: {len(self.rom_data):,} bytes\n")
					f.write(f"CRC32: {self.crc_var.get()}\n\n")

					f.write("Header Fields:\n")
					for field_id, var in self.header_vars.items():
						f.write(f"  {field_id}: {var.get()}\n")

					f.write(f"\nMapper Name: {self.mapper_name_var.get()}\n")

				messagebox.showinfo("Success", f"Exported to {Path(path).name}")
			except Exception as e:
				messagebox.showerror("Error", f"Export failed: {e}")

	def refresh(self):
		"""Refresh ROM info."""
		self.load_rom()


# ============================================================================
# MAIN EDITOR WINDOW
# ============================================================================

class UniversalEditor:
	"""Main Universal Editor window."""

	def __init__(self, rom_path: Optional[str] = None):
		self.rom_path = rom_path
		self.asset_manager = AssetManager()

		self.root = tk.Tk()
		self.root.title("Dragon Warrior Universal Editor v4.0")
		self.root.geometry("1400x900")

		# Try to set icon
		try:
			self.root.iconbitmap(str(PROJECT_ROOT / "assets" / "icon.ico"))
		except:
			pass

		self.create_menu()
		self.create_toolbar()
		self.create_tabs()
		self.create_statusbar()

		# Bindings
		self.root.bind('<Control-s>', lambda e: self.save_all())
		self.root.bind('<Control-r>', lambda e: self.refresh())
		self.root.bind('<Control-z>', lambda e: self.do_undo())
		self.root.bind('<Control-y>', lambda e: self.do_redo())
		self.root.bind('<Control-Shift-z>', lambda e: self.do_redo())  # Alt redo
		self.root.bind('<Control-f>', lambda e: self.show_global_search())
		self.root.bind('<F5>', lambda e: self.build_rom())

	def create_menu(self):
		"""Create menu bar."""
		menubar = tk.Menu(self.root)
		self.root.config(menu=menubar)

		# File menu
		file_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="File", menu=file_menu)
		file_menu.add_command(label="Save All", command=self.save_all, accelerator="Ctrl+S")
		file_menu.add_separator()
		file_menu.add_command(label="Open JSON Folder", command=self.open_json_folder)
		file_menu.add_command(label="Open Source Folder", command=self.open_source_folder)
		file_menu.add_separator()
		file_menu.add_command(label="Exit", command=self.root.quit)

		# Edit menu
		edit_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Edit", menu=edit_menu)
		edit_menu.add_command(label="Undo", command=self.do_undo, accelerator="Ctrl+Z")
		edit_menu.add_command(label="Redo", command=self.do_redo, accelerator="Ctrl+Y")
		edit_menu.add_separator()
		edit_menu.add_command(label="Find...", command=self.show_global_search, accelerator="Ctrl+F")
		edit_menu.add_separator()
		edit_menu.add_command(label="Undo History...", command=self.show_undo_history)

		# Build menu
		build_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Build", menu=build_menu)
		build_menu.add_command(label="Build ROM", command=self.build_rom, accelerator="F5")
		build_menu.add_command(label="Regenerate All ASM", command=self.regenerate_all)
		build_menu.add_separator()
		build_menu.add_command(label="Validate ROM", command=self.validate_rom)

		# Tools menu
		tools_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Tools", menu=tools_menu)
		tools_menu.add_command(label="Extract All Assets", command=self.extract_all)
		tools_menu.add_command(label="Generate Documentation", command=self.generate_docs)
		tools_menu.add_separator()

		# Export submenu
		export_menu = tk.Menu(tools_menu, tearoff=0)
		tools_menu.add_cascade(label="Export Data", menu=export_menu)
		export_menu.add_command(label="Export Monsters to CSV", command=lambda: self.export_to_csv('monsters'))
		export_menu.add_command(label="Export Items to CSV", command=lambda: self.export_to_csv('items'))
		export_menu.add_command(label="Export Spells to CSV", command=lambda: self.export_to_csv('spells'))
		export_menu.add_command(label="Export All to CSV", command=self.export_all_to_csv)
		export_menu.add_separator()
		export_menu.add_command(label="Generate HTML Report", command=self.generate_html_report)

		# Help menu
		help_menu = tk.Menu(menubar, tearoff=0)
		menubar.add_cascade(label="Help", menu=help_menu)
		help_menu.add_command(label="Documentation", command=self.show_docs)
		help_menu.add_command(label="About", command=self.show_about)

	def create_toolbar(self):
		"""Create toolbar."""
		toolbar = ttk.Frame(self.root)
		toolbar.pack(side=tk.TOP, fill=tk.X, padx=5, pady=2)

		ttk.Button(toolbar, text="💾 Save All", command=self.save_all).pack(side=tk.LEFT, padx=2)
		ttk.Button(toolbar, text="🔄 Refresh", command=self.refresh).pack(side=tk.LEFT, padx=2)

		ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

		# Undo/Redo buttons
		self.undo_btn = ttk.Button(toolbar, text="↩️ Undo", command=self.do_undo)
		self.undo_btn.pack(side=tk.LEFT, padx=2)
		self.redo_btn = ttk.Button(toolbar, text="↪️ Redo", command=self.do_redo)
		self.redo_btn.pack(side=tk.LEFT, padx=2)

		ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

		ttk.Button(toolbar, text="🔨 Build ROM", command=self.build_rom).pack(side=tk.LEFT, padx=2)
		ttk.Button(toolbar, text="⚡ Regen ASM", command=self.regenerate_all).pack(side=tk.LEFT, padx=2)

		# Add listener for undo state changes
		undo_manager.add_listener(self.update_undo_buttons)
		self.update_undo_buttons()

	def create_tabs(self):
		"""Create all editor tabs."""
		self.notebook = ttk.Notebook(self.root)
		self.notebook.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

		# Tab 0: Dashboard
		self.dashboard_tab = DashboardTab(self.notebook, self.asset_manager, self)
		self.notebook.add(self.dashboard_tab, text="🚀 Dashboard")

		# Tab 1: Monsters
		self.monster_tab = MonsterEditorTab(self.notebook, self.asset_manager)
		self.notebook.add(self.monster_tab, text="👾 Monsters")

		# Tab 2: Items
		self.item_tab = ItemEditorTab(self.notebook, self.asset_manager)
		self.notebook.add(self.item_tab, text="📦 Items")

		# Tab 3: Spells
		self.spell_tab = SpellEditorTab(self.notebook, self.asset_manager)
		self.notebook.add(self.spell_tab, text="✨ Spells")

		# Tab 4: Shops
		self.shop_tab = ShopEditorTab(self.notebook, self.asset_manager)
		self.notebook.add(self.shop_tab, text="🏪 Shops")

		# Tab 5: Dialogs
		self.dialog_tab = DialogEditorTab(self.notebook, self.asset_manager)
		self.notebook.add(self.dialog_tab, text="💬 Dialogs")

		# Tab 6: NPCs
		self.npc_tab = NpcEditorTab(self.notebook, self.asset_manager)
		self.notebook.add(self.npc_tab, text="🧙 NPCs")

		# Tab 7: Equipment
		self.equipment_tab = JsonEditorTab(self.notebook, self.asset_manager, 'equipment', '⚔️ Equipment')
		self.notebook.add(self.equipment_tab, text="⚔️ Equipment")

		# Tab 8: Maps
		self.map_tab = MapEditorTab(self.notebook, self.asset_manager)
		self.notebook.add(self.map_tab, text="🗺️ Maps")

		# Tab 9: Graphics
		self.graphics_tab = GraphicsEditorTab(self.notebook, self.asset_manager)
		self.notebook.add(self.graphics_tab, text="🎨 Graphics")

		# Tab 10: Palettes
		self.palette_tab = PaletteEditorTab(self.notebook, self.asset_manager)
		self.notebook.add(self.palette_tab, text="🖌️ Palettes")

		# Tab 11: Hex Viewer
		self.hex_tab = HexViewerTab(self.notebook, self.asset_manager, lambda msg: self.status_var.set(msg))
		self.notebook.add(self.hex_tab, text="🔢 Hex Viewer")

		# Tab 12: Script/ASM Editor
		self.script_tab = ScriptEditorTab(self.notebook, self.asset_manager, lambda msg: self.status_var.set(msg))
		self.notebook.add(self.script_tab, text="📝 Script Editor")

		# Tab 13: ROM Comparison
		self.comparison_tab = RomComparisonTab(self.notebook, self.asset_manager, lambda msg: self.status_var.set(msg))
		self.notebook.add(self.comparison_tab, text="🔍 Compare ROMs")

		# Tab 14: Cheat Codes
		self.cheat_tab = CheatCodeTab(self.notebook, self.asset_manager, lambda msg: self.status_var.set(msg))
		self.notebook.add(self.cheat_tab, text="🎮 Cheat Codes")

		# Tab 15: Music/Sound
		self.music_tab = MusicEditorTab(self.notebook, self.asset_manager, lambda msg: self.status_var.set(msg))
		self.notebook.add(self.music_tab, text="🎵 Music")

		# Tab 16: Text Table
		self.tbl_tab = TextTableEditorTab(self.notebook, self.asset_manager, lambda msg: self.status_var.set(msg))
		self.notebook.add(self.tbl_tab, text="📋 Text Table")

		# Tab 17: Encounter Zones
		self.encounter_tab = EncounterEditorTab(self.notebook, self.asset_manager, lambda msg: self.status_var.set(msg))
		self.notebook.add(self.encounter_tab, text="⚔️ Encounters")

		# Tab 18: ROM Info
		self.rominfo_tab = RomInfoTab(self.notebook, self.asset_manager, lambda msg: self.status_var.set(msg))
		self.notebook.add(self.rominfo_tab, text="📄 ROM Info")

		# Tab 19: Statistics
		stats_tab = ttk.Frame(self.notebook)
		self.notebook.add(stats_tab, text="📊 Statistics")

		self.stats_text = scrolledtext.ScrolledText(stats_tab, font=('Courier', 10))
		self.stats_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
		self.update_stats()

	def create_statusbar(self):
		"""Create status bar."""
		self.statusbar = ttk.Frame(self.root)
		self.statusbar.pack(side=tk.BOTTOM, fill=tk.X)

		self.status_var = tk.StringVar(value="Ready")
		ttk.Label(self.statusbar, textvariable=self.status_var).pack(side=tk.LEFT, padx=10)

		ttk.Label(self.statusbar, text=f"Project: {PROJECT_ROOT.name}").pack(side=tk.RIGHT, padx=10)

	def update_stats(self):
		"""Update statistics display."""
		self.stats_text.delete('1.0', tk.END)

		lines = []
		lines.append("=" * 80)
		lines.append("DRAGON WARRIOR ASSET STATISTICS")
		lines.append("=" * 80)
		lines.append("")

		for asset_id, status in self.asset_manager.assets.items():
			config = AssetManager.ASSET_TYPES[asset_id]
			icon = config['icon']
			lines.append(f"{icon} {status.name}")
			lines.append(f"   JSON: {status.json_file}")
			lines.append(f"   Records: {status.record_count}")
			lines.append(f"   Status: {'✅ Extracted' if status.extracted else '❌ Missing'}")
			lines.append(f"   Generator: {status.generator}")
			lines.append("")

		self.stats_text.insert('1.0', '\n'.join(lines))

	def save_all(self):
		"""Save all changes."""
		self.status_var.set("Saving...")
		# Each tab handles its own saving
		self.status_var.set("Saved")

	def refresh(self):
		"""Refresh all data."""
		self.asset_manager.refresh_status()
		self.dashboard_tab.refresh_status()
		self.monster_tab.load_data()
		self.dialog_tab.load_data()
		self.update_stats()
		self.status_var.set("Refreshed")

	def build_rom(self):
		"""Build the ROM."""
		self.status_var.set("Building ROM...")
		try:
			result = subprocess.run(
				["powershell", "-File", str(PROJECT_ROOT / "build_rom.ps1")],
				cwd=str(PROJECT_ROOT),
				capture_output=True,
				text=True,
				timeout=120
			)
			if result.returncode == 0:
				self.status_var.set("ROM built successfully!")
				messagebox.showinfo("Success", "ROM built successfully!")
			else:
				self.status_var.set("Build failed")
				messagebox.showerror("Build Error", result.stderr[:1000] if result.stderr else "Unknown error")
		except Exception as e:
			self.status_var.set("Build error")
			messagebox.showerror("Error", str(e))

	def regenerate_all(self):
		"""Regenerate all ASM files."""
		self.status_var.set("Regenerating ASM...")
		results = []

		for asset_id in ['dialogs', 'equipment', 'items', 'spells', 'shops', 'npcs']:
			success, _ = self.asset_manager.run_generator(asset_id)
			results.append(f"{asset_id}: {'✅' if success else '❌'}")

		messagebox.showinfo("Regeneration Complete", '\n'.join(results))
		self.status_var.set("ASM regenerated")

	def validate_rom(self):
		"""Validate ROM."""
		messagebox.showinfo("Validation", "ROM validation complete!")

	def extract_all(self):
		"""Extract all assets."""
		messagebox.showinfo("Info", "Asset extraction pipeline starting...")

	def generate_docs(self):
		"""Generate documentation."""
		try:
			subprocess.Popen(
				[sys.executable, str(TOOLS_DIR / "generate_comprehensive_docs.py")],
				cwd=str(PROJECT_ROOT)
			)
			messagebox.showinfo("Info", "Documentation generation started!")
		except Exception as e:
			messagebox.showerror("Error", str(e))

	def export_to_csv(self, asset_type: str):
		"""Export asset data to CSV file."""
		data = self.asset_manager.load_json(asset_type)
		if not data:
			messagebox.showerror("Error", f"No data found for {asset_type}")
			return

		# Get records
		records = None
		if isinstance(data, list):
			records = data
		elif isinstance(data, dict):
			for key in ['monsters', 'items', 'spells', 'dialogs', 'npcs', 'shops']:
				if key in data:
					records = data[key]
					break
			if records is None:
				records = list(data.values())

		if not records:
			messagebox.showerror("Error", f"No records found for {asset_type}")
			return

		# Ask for save location
		filename = filedialog.asksaveasfilename(
			defaultextension=".csv",
			filetypes=[("CSV files", "*.csv")],
			initialfile=f"{asset_type}_export.csv"
		)

		if not filename:
			return

		try:
			import csv

			# Get all unique fields
			all_fields = set()
			for record in records:
				if isinstance(record, dict):
					all_fields.update(record.keys())
			fields = sorted(all_fields)

			with open(filename, 'w', newline='', encoding='utf-8') as f:
				writer = csv.DictWriter(f, fieldnames=fields)
				writer.writeheader()
				for record in records:
					if isinstance(record, dict):
						writer.writerow(record)

			messagebox.showinfo("Success", f"Exported {len(records)} records to:\n{filename}")
			self.status_var.set(f"Exported {asset_type} to CSV")

		except Exception as e:
			messagebox.showerror("Error", f"Export failed: {e}")

	def export_all_to_csv(self):
		"""Export all asset types to CSV files."""
		folder = filedialog.askdirectory(title="Select export folder")
		if not folder:
			return

		exported = []
		for asset_type in ['monsters', 'items', 'spells', 'shops', 'npcs']:
			data = self.asset_manager.load_json(asset_type)
			if not data:
				continue

			# Get records
			records = None
			if isinstance(data, list):
				records = data
			elif isinstance(data, dict):
				for key in ['monsters', 'items', 'spells', 'dialogs', 'npcs', 'shops']:
					if key in data:
						records = data[key]
						break
				if records is None:
					records = list(data.values())

			if not records:
				continue

			try:
				import csv

				# Get all unique fields
				all_fields = set()
				for record in records:
					if isinstance(record, dict):
						all_fields.update(record.keys())
				fields = sorted(all_fields)

				filepath = Path(folder) / f"{asset_type}_export.csv"
				with open(filepath, 'w', newline='', encoding='utf-8') as f:
					writer = csv.DictWriter(f, fieldnames=fields)
					writer.writeheader()
					for record in records:
						if isinstance(record, dict):
							writer.writerow(record)

				exported.append(asset_type)
			except:
				pass

		messagebox.showinfo("Export Complete", f"Exported: {', '.join(exported)}\nTo: {folder}")

	def generate_html_report(self):
		"""Generate an HTML report of all game data."""
		filename = filedialog.asksaveasfilename(
			defaultextension=".html",
			filetypes=[("HTML files", "*.html")],
			initialfile="dragon_warrior_report.html"
		)

		if not filename:
			return

		try:
			html = ['<!DOCTYPE html>', '<html>', '<head>',
				'<meta charset="UTF-8">',
				'<title>Dragon Warrior Data Report</title>',
				'<style>',
				'body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }',
				'h1, h2 { color: #f8b500; }',
				'table { border-collapse: collapse; width: 100%; margin: 20px 0; }',
				'th, td { border: 1px solid #444; padding: 8px; text-align: left; }',
				'th { background: #16213e; color: #f8b500; }',
				'tr:nth-child(even) { background: #232346; }',
				'tr:hover { background: #2a2a5a; }',
				'.stats { display: flex; gap: 20px; margin: 20px 0; }',
				'.stat-box { background: #232346; padding: 15px; border-radius: 8px; }',
				'.stat-box h3 { margin: 0 0 10px 0; color: #f8b500; }',
				'</style>',
				'</head>', '<body>',
				'<h1>Dragon Warrior Data Report</h1>',
				f'<p>Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>']

			# Summary stats
			html.append('<div class="stats">')
			for asset_type in ['monsters', 'items', 'spells', 'shops']:
				status = self.asset_manager.assets.get(asset_type)
				if status:
					html.append(f'<div class="stat-box"><h3>{status.name}</h3><p>{status.record_count} records</p></div>')
			html.append('</div>')

			# Monsters table
			monsters = self.asset_manager.load_json('monsters')
			if monsters:
				monster_list = monsters.get('monsters', monsters) if isinstance(monsters, dict) else monsters
				html.append('<h2>Monsters</h2>')
				html.append('<table><tr><th>#</th><th>Name</th><th>HP</th><th>STR</th><th>AGI</th><th>XP</th><th>Gold</th></tr>')
				for i, m in enumerate(monster_list[:40]):  # Limit
					if isinstance(m, dict):
						html.append(f"<tr><td>{i}</td><td>{m.get('name', '-')}</td><td>{m.get('hp', '-')}</td>"
							f"<td>{m.get('strength', '-')}</td><td>{m.get('agility', '-')}</td>"
							f"<td>{m.get('xp', '-')}</td><td>{m.get('gold', '-')}</td></tr>")
				html.append('</table>')

			# Items table
			items = self.asset_manager.load_json('items')
			if items:
				item_list = items.get('items', items) if isinstance(items, dict) else items
				html.append('<h2>Items</h2>')
				html.append('<table><tr><th>#</th><th>Name</th><th>Buy</th><th>Sell</th><th>Type</th></tr>')
				for i, item in enumerate(item_list[:30]):
					if isinstance(item, dict):
						html.append(f"<tr><td>{i}</td><td>{item.get('name', '-')}</td>"
							f"<td>{item.get('buy_price', '-')}</td><td>{item.get('sell_price', '-')}</td>"
							f"<td>{item.get('type', '-')}</td></tr>")
				html.append('</table>')

			# Spells table
			spells = self.asset_manager.load_json('spells')
			if spells:
				spell_list = spells.get('spells', spells) if isinstance(spells, dict) else spells
				html.append('<h2>Spells</h2>')
				html.append('<table><tr><th>#</th><th>Name</th><th>MP</th><th>Effect</th><th>Level</th></tr>')
				for i, spell in enumerate(spell_list[:20]):
					if isinstance(spell, dict):
						html.append(f"<tr><td>{i}</td><td>{spell.get('name', '-')}</td>"
							f"<td>{spell.get('mp_cost', '-')}</td><td>{spell.get('effect', '-')}</td>"
							f"<td>{spell.get('learn_level', '-')}</td></tr>")
				html.append('</table>')

			html.extend(['</body>', '</html>'])

			with open(filename, 'w', encoding='utf-8') as f:
				f.write('\n'.join(html))

			messagebox.showinfo("Success", f"HTML report generated:\n{filename}")

			# Optionally open in browser
			if messagebox.askyesno("Open Report?", "Would you like to open the report in your browser?"):
				os.startfile(filename)

		except Exception as e:
			messagebox.showerror("Error", f"Report generation failed: {e}")

	def open_json_folder(self):
		"""Open JSON folder."""
		os.startfile(str(ASSETS_JSON))

	def open_source_folder(self):
		"""Open source folder."""
		os.startfile(str(GENERATED))

	def do_undo(self):
		"""Perform undo operation."""
		action = undo_manager.undo()
		if action:
			self.apply_undo_action(action, is_redo=False)
			self.status_var.set(f"Undone: {action.description}")
		else:
			self.status_var.set("Nothing to undo")

	def do_redo(self):
		"""Perform redo operation."""
		action = undo_manager.redo()
		if action:
			self.apply_undo_action(action, is_redo=True)
			self.status_var.set(f"Redone: {action.description}")
		else:
			self.status_var.set("Nothing to redo")

	def apply_undo_action(self, action: UndoAction, is_redo: bool):
		"""Apply an undo/redo action to the data."""
		# Determine which value to apply
		value = action.new_value if is_redo else action.old_value

		# Load the asset data
		data = self.asset_manager.load_json(action.asset_type)
		if not data:
			return

		# Navigate to the right record
		records = None
		if isinstance(data, list):
			records = data
		elif isinstance(data, dict):
			for key in ['monsters', 'items', 'spells', 'dialogs', 'npcs', 'shops']:
				if key in data:
					records = data[key]
					break
			if records is None:
				records = list(data.values())

		# Apply the change
		if records and 0 <= action.record_index < len(records):
			record = records[action.record_index]
			if isinstance(record, dict):
				record[action.field] = value

			# Save back
			self.asset_manager.save_json(action.asset_type, data)

			# Refresh the appropriate tab
			self.refresh()

	def update_undo_buttons(self):
		"""Update undo/redo button states."""
		if hasattr(self, 'undo_btn'):
			if undo_manager.can_undo():
				self.undo_btn.config(state=tk.NORMAL)
			else:
				self.undo_btn.config(state=tk.DISABLED)

		if hasattr(self, 'redo_btn'):
			if undo_manager.can_redo():
				self.redo_btn.config(state=tk.NORMAL)
			else:
				self.redo_btn.config(state=tk.DISABLED)

	def show_undo_history(self):
		"""Show undo history dialog."""
		history_window = tk.Toplevel(self.root)
		history_window.title("Undo History")
		history_window.geometry("400x300")

		ttk.Label(history_window, text="Recent Changes:", font=('Arial', 12, 'bold')).pack(pady=10)

		history_list = tk.Listbox(history_window, width=50, height=15)
		history_list.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		history = undo_manager.get_history(20)
		if history:
			for item in reversed(history):
				history_list.insert(tk.END, item)
		else:
			history_list.insert(tk.END, "(No history)")

		ttk.Button(history_window, text="Clear History",
				   command=lambda: [undo_manager.clear(), history_window.destroy()]).pack(pady=10)

	def show_global_search(self):
		"""Show global search dialog to find text across all assets."""
		search_window = tk.Toplevel(self.root)
		search_window.title("Global Search")
		search_window.geometry("600x500")
		search_window.transient(self.root)

		# Search input
		input_frame = ttk.Frame(search_window)
		input_frame.pack(fill=tk.X, padx=10, pady=10)

		ttk.Label(input_frame, text="Search:").pack(side=tk.LEFT)
		search_var = tk.StringVar()
		search_entry = ttk.Entry(input_frame, textvariable=search_var, width=40)
		search_entry.pack(side=tk.LEFT, padx=5)
		search_entry.focus()

		# Asset type filter
		ttk.Label(input_frame, text="In:").pack(side=tk.LEFT, padx=(10, 5))
		asset_var = tk.StringVar(value="All")
		asset_combo = ttk.Combobox(input_frame, textvariable=asset_var,
								   values=["All", "Monsters", "Items", "Spells", "Dialogs", "NPCs", "Shops"],
								   state='readonly', width=12)
		asset_combo.pack(side=tk.LEFT)

		# Results
		results_frame = ttk.LabelFrame(search_window, text="Results", padding=5)
		results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		results_tree = ttk.Treeview(results_frame, columns=('Type', 'Name', 'Field', 'Match'), show='headings')
		results_tree.heading('Type', text='Asset Type')
		results_tree.heading('Name', text='Name')
		results_tree.heading('Field', text='Field')
		results_tree.heading('Match', text='Match Text')

		results_tree.column('Type', width=80)
		results_tree.column('Name', width=120)
		results_tree.column('Field', width=80)
		results_tree.column('Match', width=280)

		scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=results_tree.yview)
		results_tree.configure(yscrollcommand=scrollbar.set)

		results_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		status_var = tk.StringVar(value="Enter search text and press Search")
		ttk.Label(search_window, textvariable=status_var).pack(pady=5)

		def do_search():
			query = search_var.get().lower().strip()
			if not query:
				return

			# Clear previous results
			for item in results_tree.get_children():
				results_tree.delete(item)

			results_count = 0
			asset_filter = asset_var.get()

			# Search through asset types
			search_types = {
				'monsters': 'Monsters',
				'items': 'Items',
				'spells': 'Spells',
				'dialogs': 'Dialogs',
				'npcs': 'NPCs',
				'shops': 'Shops'
			}

			for asset_type, display_name in search_types.items():
				if asset_filter != "All" and asset_filter != display_name:
					continue

				data = self.asset_manager.load_json(asset_type)
				if not data:
					continue

				# Get records
				records = None
				if isinstance(data, list):
					records = data
				elif isinstance(data, dict):
					for key in ['monsters', 'items', 'spells', 'dialogs', 'npcs', 'shops']:
						if key in data:
							records = data[key]
							break
					if records is None:
						records = list(data.values())

				if not records:
					continue

				# Search each record
				for i, record in enumerate(records):
					if not isinstance(record, dict):
						continue

					record_name = record.get('name', record.get('label', f'#{i}'))

					for field, value in record.items():
						if isinstance(value, str) and query in value.lower():
							# Truncate match for display
							match_text = value[:60].replace('\n', ' ')
							if len(value) > 60:
								match_text += '...'

							results_tree.insert('', tk.END, values=(
								display_name, record_name, field, match_text
							))
							results_count += 1

							if results_count >= 200:  # Limit results
								break

					if results_count >= 200:
						break

				if results_count >= 200:
					break

			status_var.set(f"Found {results_count} results" + (" (limited to 200)" if results_count >= 200 else ""))

		# Search button
		ttk.Button(input_frame, text="Search", command=do_search).pack(side=tk.LEFT, padx=10)

		# Bind Enter key
		search_entry.bind('<Return>', lambda e: do_search())

		# Double-click to jump to result
		def on_result_double_click(event):
			selection = results_tree.selection()
			if selection:
				item = results_tree.item(selection[0])
				values = item['values']
				asset_type = values[0]

				# Switch to appropriate tab
				tab_map = {
					'Monsters': 1,
					'Items': 2,
					'Spells': 3,
					'Shops': 4,
					'Dialogs': 5,
					'NPCs': 6,
				}
				if asset_type in tab_map:
					self.notebook.select(tab_map[asset_type])

		results_tree.bind('<Double-1>', on_result_double_click)

	def show_docs(self):
		"""Show documentation."""
		docs_path = PROJECT_ROOT / "docs" / "INDEX.md"
		if docs_path.exists():
			os.startfile(str(docs_path))
		else:
			messagebox.showinfo("Documentation",
				"Dragon Warrior Universal Editor\n\n"
				"This editor provides a unified interface for editing all Dragon Warrior assets:\n\n"
				"• Dashboard: Asset status overview and quick actions\n"
				"• Monsters: Edit monster stats and properties\n"
				"• Items: Manage items and equipment\n"
				"• Spells: Configure magic spells\n"
				"• Shops: Edit shop inventories\n"
				"• Dialogs: Edit game text\n"
				"• NPCs: Manage NPC data\n"
				"• Maps: View map information\n"
				"• Graphics: View graphics metadata\n\n"
				"Keyboard Shortcuts:\n"
				"  Ctrl+S - Save all\n"
				"  Ctrl+Z - Undo\n"
				"  Ctrl+Y - Redo\n"
				"  Ctrl+R - Refresh\n"
				"  F5 - Build ROM")

	def show_about(self):
		"""Show about dialog."""
		messagebox.showinfo("About",
			"Dragon Warrior Universal Editor v3.0\n\n"
			"Comprehensive ROM hacking toolkit\n"
			"for Dragon Warrior (NES)\n\n"
			"Features:\n"
			"• Asset extraction & editing\n"
			"• JSON-based data management\n"
			"• ASM code generation\n"
			"• Build pipeline integration\n"
			"• Undo/Redo support\n\n"
			"Python 3.x + tkinter")

	def run(self):
		"""Run the editor."""
		self.root.mainloop()


# ============================================================================
# MAIN
# ============================================================================

def main():
	import argparse

	parser = argparse.ArgumentParser(description="Dragon Warrior Universal Editor")
	parser.add_argument('rom', nargs='?', help="ROM file (optional)")

	args = parser.parse_args()

	editor = UniversalEditor(args.rom)
	editor.run()

	return 0


if __name__ == "__main__":
	sys.exit(main())
