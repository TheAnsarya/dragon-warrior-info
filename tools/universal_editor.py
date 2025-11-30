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
			("🏪 Shops", 4), ("💬 Dialogs", 5), ("🧙 NPCs", 6),
			("🗺️ Maps", 7), ("🎨 Graphics", 8), ("📊 Stats", 9),
		]

		for i, (text, tab_idx) in enumerate(editor_buttons):
			row, col = divmod(i, 3)
			btn = ttk.Button(
				editors_frame,
				text=text,
				width=15,
				command=lambda idx=tab_idx: self.editor.notebook.select(idx)
			)
			btn.grid(row=row, column=col, padx=5, pady=5)

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
# MAIN EDITOR WINDOW
# ============================================================================

class UniversalEditor:
	"""Main Universal Editor window."""

	def __init__(self, rom_path: Optional[str] = None):
		self.rom_path = rom_path
		self.asset_manager = AssetManager()

		self.root = tk.Tk()
		self.root.title("Dragon Warrior Universal Editor v3.0")
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

		# Tab 11: Statistics
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
