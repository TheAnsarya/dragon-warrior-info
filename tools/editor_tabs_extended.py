#!/usr/bin/env python3
"""
Additional Editor Tabs for Dragon Warrior Universal Editor

This module adds three new editor tabs:
- DamageEditorTab: Edit damage calculation parameters
- SpellEffectsEditorTab: Edit spell behavior parameters  
- ExperienceEditorTab: Edit experience/level progression

These tabs should be added to the main universal_editor.py
"""

import json
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from pathlib import Path
from typing import Dict, Any, Optional


# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
ASSETS_JSON = PROJECT_ROOT / "assets" / "json"


# ============================================================================
# DAMAGE FORMULA EDITOR TAB
# ============================================================================

class DamageEditorTab(ttk.Frame):
	"""Edit damage calculation parameters from damage_formulas.json."""

	def __init__(self, parent, asset_manager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.data = None
		self.modified = False

		self.create_widgets()
		self.load_data()

	def create_widgets(self):
		"""Create damage editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="⚔️ Damage Formula Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save All", command=self.save_all).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Generate ASM", command=self.generate_asm).pack(side=tk.RIGHT, padx=5)

		# Notebook for categories
		self.notebook = ttk.Notebook(self)
		self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Tab 1: Physical Damage
		self.physical_frame = ttk.Frame(self.notebook)
		self.notebook.add(self.physical_frame, text="Physical Damage")
		self.create_physical_tab()

		# Tab 2: Spell Damage
		self.spell_frame = ttk.Frame(self.notebook)
		self.notebook.add(self.spell_frame, text="Spell Damage")
		self.create_spell_tab()

		# Tab 3: Healing
		self.healing_frame = ttk.Frame(self.notebook)
		self.notebook.add(self.healing_frame, text="Healing")
		self.create_healing_tab()

		# Tab 4: Environmental
		self.env_frame = ttk.Frame(self.notebook)
		self.notebook.add(self.env_frame, text="Environmental")
		self.create_env_tab()

	def create_physical_tab(self):
		"""Create physical damage editing interface."""
		frame = self.physical_frame

		# Player Attack section
		player_frame = ttk.LabelFrame(frame, text="Player Attack", padding=10)
		player_frame.pack(fill=tk.X, padx=10, pady=5)

		self.player_vars = {}

		fields = [
			('defense_divisor', 'Defense Divisor', 'Divides enemy defense (default: 2)'),
			('result_divisor', 'Result Divisor', 'Final damage divisor (default: 4)'),
			('weak_threshold', 'Weak Attack Threshold', 'STR-DEF threshold for weak attack (default: 2)'),
		]

		for i, (field, label, desc) in enumerate(fields):
			row = ttk.Frame(player_frame)
			row.pack(fill=tk.X, pady=2)

			ttk.Label(row, text=f"{label}:", width=20).pack(side=tk.LEFT)

			var = tk.IntVar(value=0)
			spin = ttk.Spinbox(row, textvariable=var, from_=1, to=16, width=5)
			spin.pack(side=tk.LEFT, padx=5)

			ttk.Label(row, text=desc, foreground='gray').pack(side=tk.LEFT, padx=10)

			self.player_vars[field] = var

		# Enemy Attack section
		enemy_frame = ttk.LabelFrame(frame, text="Enemy Attack", padding=10)
		enemy_frame.pack(fill=tk.X, padx=10, pady=5)

		self.enemy_vars = {}

		fields = [
			('weak_addend', 'Weak Attack Addend', 'Added before division (default: 2)'),
			('weak_divisor', 'Weak Attack Divisor', 'Divisor for weak attack (default: 3)'),
		]

		for i, (field, label, desc) in enumerate(fields):
			row = ttk.Frame(enemy_frame)
			row.pack(fill=tk.X, pady=2)

			ttk.Label(row, text=f"{label}:", width=20).pack(side=tk.LEFT)

			var = tk.IntVar(value=0)
			spin = ttk.Spinbox(row, textvariable=var, from_=1, to=16, width=5)
			spin.pack(side=tk.LEFT, padx=5)

			ttk.Label(row, text=desc, foreground='gray').pack(side=tk.LEFT, padx=10)

			self.enemy_vars[field] = var

		# Dodge section
		dodge_frame = ttk.LabelFrame(frame, text="Dodge Mechanics", padding=10)
		dodge_frame.pack(fill=tk.X, padx=10, pady=5)

		row = ttk.Frame(dodge_frame)
		row.pack(fill=tk.X, pady=2)

		ttk.Label(row, text="Dodge Threshold (x/64):", width=20).pack(side=tk.LEFT)

		self.dodge_var = tk.IntVar(value=14)
		spin = ttk.Spinbox(row, textvariable=self.dodge_var, from_=0, to=63, width=5)
		spin.pack(side=tk.LEFT, padx=5)

		self.dodge_percent = ttk.Label(row, text="= 21.9%", foreground='blue')
		self.dodge_percent.pack(side=tk.LEFT, padx=10)

		self.dodge_var.trace_add('write', self.update_dodge_percent)

	def update_dodge_percent(self, *args):
		"""Update dodge percentage display."""
		try:
			val = self.dodge_var.get()
			pct = (val / 64) * 100
			self.dodge_percent.config(text=f"= {pct:.1f}%")
		except:
			pass

	def create_spell_tab(self):
		"""Create spell damage editing interface."""
		frame = self.spell_frame

		# Player spells
		player_frame = ttk.LabelFrame(frame, text="Player Spell Damage", padding=10)
		player_frame.pack(fill=tk.X, padx=10, pady=5)

		self.player_spell_vars = {}

		spells = [
			('HURT', 'HURT (5-12)', 5, 7),
			('HURTMORE', 'HURTMORE (58-65)', 58, 7),
		]

		for spell_id, label, default_base, default_mask in spells:
			row = ttk.Frame(player_frame)
			row.pack(fill=tk.X, pady=3)

			ttk.Label(row, text=f"{label}:", width=20).pack(side=tk.LEFT)

			ttk.Label(row, text="Base:").pack(side=tk.LEFT, padx=5)
			base_var = tk.IntVar(value=default_base)
			ttk.Spinbox(row, textvariable=base_var, from_=0, to=255, width=5).pack(side=tk.LEFT)

			ttk.Label(row, text="Variance:").pack(side=tk.LEFT, padx=5)
			mask_var = tk.IntVar(value=default_mask)
			ttk.Spinbox(row, textvariable=mask_var, from_=0, to=63, width=5).pack(side=tk.LEFT)

			self.player_spell_vars[spell_id] = {'base': base_var, 'mask': mask_var}

		# Enemy spells
		enemy_frame = ttk.LabelFrame(frame, text="Enemy Spell Damage", padding=10)
		enemy_frame.pack(fill=tk.X, padx=10, pady=5)

		self.enemy_spell_vars = {}

		spells = [
			('HURT', 'HURT (7-10)', 7, 3),
			('HURTMORE', 'HURTMORE (30-45)', 30, 15),
		]

		for spell_id, label, default_base, default_mask in spells:
			row = ttk.Frame(enemy_frame)
			row.pack(fill=tk.X, pady=3)

			ttk.Label(row, text=f"{label}:", width=20).pack(side=tk.LEFT)

			ttk.Label(row, text="Base:").pack(side=tk.LEFT, padx=5)
			base_var = tk.IntVar(value=default_base)
			ttk.Spinbox(row, textvariable=base_var, from_=0, to=255, width=5).pack(side=tk.LEFT)

			ttk.Label(row, text="Variance:").pack(side=tk.LEFT, padx=5)
			mask_var = tk.IntVar(value=default_mask)
			ttk.Spinbox(row, textvariable=mask_var, from_=0, to=63, width=5).pack(side=tk.LEFT)

			self.enemy_spell_vars[spell_id] = {'base': base_var, 'mask': mask_var}

		# Armor reduction
		armor_frame = ttk.LabelFrame(frame, text="Armor Spell Reduction", padding=10)
		armor_frame.pack(fill=tk.X, padx=10, pady=5)

		row = ttk.Frame(armor_frame)
		row.pack(fill=tk.X, pady=3)

		ttk.Label(row, text="Magic/Erdrick's Armor:", width=20).pack(side=tk.LEFT)
		ttk.Label(row, text="Damage × 2/3 (reduces spell damage by 1/3)").pack(side=tk.LEFT)

	def create_healing_tab(self):
		"""Create healing spell editing interface."""
		frame = self.healing_frame

		heal_frame = ttk.LabelFrame(frame, text="Healing Spells", padding=10)
		heal_frame.pack(fill=tk.X, padx=10, pady=5)

		self.heal_vars = {}

		spells = [
			('HEAL', 'HEAL (10-17)', 10, 7),
			('HEALMORE', 'HEALMORE (85-100)', 85, 15),
		]

		for spell_id, label, default_base, default_mask in spells:
			row = ttk.Frame(heal_frame)
			row.pack(fill=tk.X, pady=3)

			ttk.Label(row, text=f"{label}:", width=20).pack(side=tk.LEFT)

			ttk.Label(row, text="Base:").pack(side=tk.LEFT, padx=5)
			base_var = tk.IntVar(value=default_base)
			ttk.Spinbox(row, textvariable=base_var, from_=0, to=255, width=5).pack(side=tk.LEFT)

			ttk.Label(row, text="Variance:").pack(side=tk.LEFT, padx=5)
			mask_var = tk.IntVar(value=default_mask)
			ttk.Spinbox(row, textvariable=mask_var, from_=0, to=63, width=5).pack(side=tk.LEFT)

			self.heal_vars[spell_id] = {'base': base_var, 'mask': mask_var}

		# Formula explanation
		formula_frame = ttk.LabelFrame(frame, text="Formula", padding=10)
		formula_frame.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(formula_frame, text="HP Restored = Base + Random(0 to Variance)").pack(anchor=tk.W)
		ttk.Label(formula_frame, text="Example: HEAL = 10 + Random(0-7) = 10-17 HP").pack(anchor=tk.W)

	def create_env_tab(self):
		"""Create environmental damage editing interface."""
		frame = self.env_frame

		env_frame = ttk.LabelFrame(frame, text="Environmental Damage", padding=10)
		env_frame.pack(fill=tk.X, padx=10, pady=5)

		self.env_vars = {}

		damages = [
			('SWAMP', 'Swamp (per step)', 2),
			('BARRIER', 'Barrier (per step)', 15),
		]

		for dmg_id, label, default_val in damages:
			row = ttk.Frame(env_frame)
			row.pack(fill=tk.X, pady=3)

			ttk.Label(row, text=f"{label}:", width=20).pack(side=tk.LEFT)

			var = tk.IntVar(value=default_val)
			ttk.Spinbox(row, textvariable=var, from_=1, to=255, width=5).pack(side=tk.LEFT, padx=5)

			ttk.Label(row, text="damage").pack(side=tk.LEFT)

			self.env_vars[dmg_id] = var

	def load_data(self):
		"""Load damage formula data from JSON."""
		json_path = ASSETS_JSON / 'damage_formulas.json'
		if json_path.exists():
			try:
				with open(json_path, 'r') as f:
					self.data = json.load(f)
					self.populate_fields()
			except Exception as e:
				print(f"Error loading damage formulas: {e}")

	def populate_fields(self):
		"""Populate UI fields from loaded data."""
		if not self.data:
			return

		# Physical damage
		phys = self.data.get('physical_damage', {})
		player = phys.get('player_attack', {})
		self.player_vars['defense_divisor'].set(player.get('defense_divisor', 2))
		self.player_vars['result_divisor'].set(player.get('result_divisor', 4))
		self.player_vars['weak_threshold'].set(player.get('weak_threshold', 2))

		enemy = phys.get('enemy_attack', {})
		enemy_weak = enemy.get('weak_attack', {})
		self.enemy_vars['weak_addend'].set(enemy_weak.get('addend', 2))
		self.enemy_vars['weak_divisor'].set(enemy_weak.get('divisor', 3))

		# Dodge
		dodge = self.data.get('dodge_mechanics', {}).get('enemy_dodge', {})
		self.dodge_var.set(dodge.get('threshold', 14))

		# Spell damage
		spell_dmg = self.data.get('spell_damage', {})
		for spell_id in ['HURT', 'HURTMORE']:
			if spell_id in spell_dmg.get('player_spells', {}):
				spell = spell_dmg['player_spells'][spell_id]
				if spell_id in self.player_spell_vars:
					self.player_spell_vars[spell_id]['base'].set(spell.get('base_damage', 0))
					self.player_spell_vars[spell_id]['mask'].set(spell.get('variance_mask', 0))

			if spell_id in spell_dmg.get('enemy_spells', {}):
				spell = spell_dmg['enemy_spells'][spell_id]
				if spell_id in self.enemy_spell_vars:
					self.enemy_spell_vars[spell_id]['base'].set(spell.get('base_damage', 0))
					self.enemy_spell_vars[spell_id]['mask'].set(spell.get('variance_mask', 0))

		# Healing
		healing = self.data.get('healing_spells', {})
		for spell_id in ['HEAL', 'HEALMORE']:
			if spell_id in healing:
				spell = healing[spell_id]
				if spell_id in self.heal_vars:
					self.heal_vars[spell_id]['base'].set(spell.get('base_value', 0))
					self.heal_vars[spell_id]['mask'].set(spell.get('variance_mask', 0))

		# Environmental
		env = self.data.get('environmental_damage', {})
		if 'SWAMP' in env:
			self.env_vars['SWAMP'].set(env['SWAMP'].get('damage', 2))
		if 'BARRIER' in env:
			self.env_vars['BARRIER'].set(env['BARRIER'].get('damage', 15))

	def save_all(self):
		"""Save all changes to JSON file."""
		if not self.data:
			self.data = {}

		# Update physical damage
		self.data.setdefault('physical_damage', {})
		self.data['physical_damage'].setdefault('player_attack', {})
		self.data['physical_damage']['player_attack']['defense_divisor'] = self.player_vars['defense_divisor'].get()
		self.data['physical_damage']['player_attack']['result_divisor'] = self.player_vars['result_divisor'].get()
		self.data['physical_damage']['player_attack']['weak_threshold'] = self.player_vars['weak_threshold'].get()

		self.data['physical_damage'].setdefault('enemy_attack', {})
		self.data['physical_damage']['enemy_attack'].setdefault('weak_attack', {})
		self.data['physical_damage']['enemy_attack']['weak_attack']['addend'] = self.enemy_vars['weak_addend'].get()
		self.data['physical_damage']['enemy_attack']['weak_attack']['divisor'] = self.enemy_vars['weak_divisor'].get()

		# Update dodge
		self.data.setdefault('dodge_mechanics', {})
		self.data['dodge_mechanics'].setdefault('enemy_dodge', {})
		threshold = self.dodge_var.get()
		self.data['dodge_mechanics']['enemy_dodge']['threshold'] = threshold
		self.data['dodge_mechanics']['enemy_dodge']['percentage'] = round((threshold / 64) * 100, 3)

		# Update spell damage
		self.data.setdefault('spell_damage', {})
		self.data['spell_damage'].setdefault('player_spells', {})
		self.data['spell_damage'].setdefault('enemy_spells', {})

		for spell_id, vars in self.player_spell_vars.items():
			self.data['spell_damage']['player_spells'].setdefault(spell_id, {})
			base = vars['base'].get()
			mask = vars['mask'].get()
			self.data['spell_damage']['player_spells'][spell_id]['base_damage'] = base
			self.data['spell_damage']['player_spells'][spell_id]['variance_mask'] = mask
			self.data['spell_damage']['player_spells'][spell_id]['min_damage'] = base
			self.data['spell_damage']['player_spells'][spell_id]['max_damage'] = base + mask

		for spell_id, vars in self.enemy_spell_vars.items():
			self.data['spell_damage']['enemy_spells'].setdefault(spell_id, {})
			base = vars['base'].get()
			mask = vars['mask'].get()
			self.data['spell_damage']['enemy_spells'][spell_id]['base_damage'] = base
			self.data['spell_damage']['enemy_spells'][spell_id]['variance_mask'] = mask
			self.data['spell_damage']['enemy_spells'][spell_id]['min_damage'] = base
			self.data['spell_damage']['enemy_spells'][spell_id]['max_damage'] = base + mask

		# Update healing
		self.data.setdefault('healing_spells', {})
		for spell_id, vars in self.heal_vars.items():
			self.data['healing_spells'].setdefault(spell_id, {})
			base = vars['base'].get()
			mask = vars['mask'].get()
			self.data['healing_spells'][spell_id]['base_value'] = base
			self.data['healing_spells'][spell_id]['variance_mask'] = mask
			self.data['healing_spells'][spell_id]['min_heal'] = base
			self.data['healing_spells'][spell_id]['max_heal'] = base + mask

		# Update environmental
		self.data.setdefault('environmental_damage', {})
		self.data['environmental_damage']['SWAMP'] = {
			'damage': self.env_vars['SWAMP'].get(),
			'description': 'Damage per step in swamp'
		}
		self.data['environmental_damage']['BARRIER'] = {
			'damage': self.env_vars['BARRIER'].get(),
			'description': 'Damage per step on barrier tiles'
		}

		# Save to file
		json_path = ASSETS_JSON / 'damage_formulas.json'
		try:
			with open(json_path, 'w') as f:
				json.dump(self.data, f, indent=2)
			messagebox.showinfo("Success", "Damage formulas saved!")
		except Exception as e:
			messagebox.showerror("Error", f"Failed to save: {e}")

	def generate_asm(self):
		"""Generate assembly code from current data."""
		import subprocess

		generator = PROJECT_ROOT / 'tools' / 'generate_damage_tables.py'
		if generator.exists():
			try:
				result = subprocess.run(['python', str(generator)], capture_output=True, text=True)
				if result.returncode == 0:
					messagebox.showinfo("Success", "Generated damage_tables.asm!")
				else:
					messagebox.showerror("Error", f"Generation failed:\n{result.stderr}")
			except Exception as e:
				messagebox.showerror("Error", f"Failed to run generator: {e}")
		else:
			messagebox.showwarning("Warning", "Generator not found: tools/generate_damage_tables.py")


# ============================================================================
# SPELL EFFECTS EDITOR TAB
# ============================================================================

class SpellEffectsEditorTab(ttk.Frame):
	"""Edit spell effect parameters from spell_effects.json."""

	def __init__(self, parent, asset_manager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.data = None
		self.current_spell = None

		self.create_widgets()
		self.load_data()

	def create_widgets(self):
		"""Create spell effects editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="✨ Spell Effects Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save All", command=self.save_all).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Generate ASM", command=self.generate_asm).pack(side=tk.RIGHT, padx=5)

		# Main content
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left: Spell list
		list_frame = ttk.LabelFrame(content, text="Spells", padding=5)
		list_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

		self.spell_list = tk.Listbox(list_frame, width=20, height=20, font=('Arial', 11))
		self.spell_list.pack(fill=tk.BOTH, expand=True)
		self.spell_list.bind('<<ListboxSelect>>', self.on_select)

		# Right: Spell details
		self.detail_frame = ttk.LabelFrame(content, text="Spell Properties", padding=10)
		self.detail_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

		# Spell fields
		self.spell_vars = {}

		rows = [
			('name', 'Name', 'entry'),
			('mp_cost', 'MP Cost', 'spin'),
			('target', 'Target', 'combo'),
			('effect_type', 'Effect Type', 'combo'),
			('success_rate', 'Success Rate %', 'spin'),
			('learn_level', 'Learn Level', 'spin'),
		]

		for i, (field, label, widget_type) in enumerate(rows):
			ttk.Label(self.detail_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=3)

			if widget_type == 'entry':
				var = tk.StringVar()
				widget = ttk.Entry(self.detail_frame, textvariable=var, width=20)
			elif widget_type == 'spin':
				var = tk.IntVar(value=0)
				widget = ttk.Spinbox(self.detail_frame, textvariable=var, from_=0, to=100, width=8)
			elif widget_type == 'combo':
				var = tk.StringVar()
				if field == 'target':
					values = ['self', 'enemy', 'field']
				else:
					values = ['damage', 'healing', 'status', 'utility', 'movement']
				widget = ttk.Combobox(self.detail_frame, textvariable=var, values=values, width=15)

			widget.grid(row=i, column=1, padx=5, pady=3, sticky=tk.W)
			self.spell_vars[field] = var

		# Effect details (context-sensitive)
		self.effect_frame = ttk.LabelFrame(self.detail_frame, text="Effect Details", padding=5)
		self.effect_frame.grid(row=len(rows), column=0, columnspan=2, sticky=tk.EW, pady=10)

		self.effect_text = tk.Text(self.effect_frame, height=8, width=40, font=('Courier', 10))
		self.effect_text.pack(fill=tk.X)

		# Description
		ttk.Label(self.detail_frame, text="Description:").grid(row=len(rows)+1, column=0, sticky=tk.NW, pady=3)
		self.desc_var = tk.StringVar()
		ttk.Entry(self.detail_frame, textvariable=self.desc_var, width=40).grid(
			row=len(rows)+1, column=1, padx=5, sticky=tk.W
		)

		# Save button
		ttk.Button(self.detail_frame, text="💾 Save Spell", command=self.save_current).grid(
			row=len(rows)+2, column=0, columnspan=2, pady=20
		)

	def load_data(self):
		"""Load spell effects data from JSON."""
		json_path = ASSETS_JSON / 'spell_effects.json'
		if json_path.exists():
			try:
				with open(json_path, 'r') as f:
					self.data = json.load(f)
					self.populate_spell_list()
			except Exception as e:
				print(f"Error loading spell effects: {e}")

	def populate_spell_list(self):
		"""Populate spell list from data."""
		self.spell_list.delete(0, tk.END)

		if self.data:
			# Player spells
			for spell_id in self.data.get('player_spells', {}):
				spell = self.data['player_spells'][spell_id]
				mp = spell.get('mp_cost', 0)
				self.spell_list.insert(tk.END, f"⭐ {spell_id} ({mp} MP)")

			# Enemy spells
			for spell_id in self.data.get('enemy_spells', {}):
				self.spell_list.insert(tk.END, f"👹 EN_{spell_id}")

	def on_select(self, event):
		"""Handle spell selection."""
		selection = self.spell_list.curselection()
		if not selection:
			return

		item = self.spell_list.get(selection[0])

		# Parse selection
		if item.startswith('⭐'):
			# Player spell
			spell_id = item.split()[1]
			spell = self.data.get('player_spells', {}).get(spell_id, {})
			self.current_spell = ('player', spell_id)
		elif item.startswith('👹'):
			# Enemy spell
			spell_id = item.split('_')[1]
			spell = self.data.get('enemy_spells', {}).get(spell_id, {})
			self.current_spell = ('enemy', spell_id)
		else:
			return

		# Populate fields
		self.spell_vars['name'].set(spell.get('name', spell_id))
		self.spell_vars['mp_cost'].set(spell.get('mp_cost', 0))
		self.spell_vars['target'].set(spell.get('target', 'enemy'))
		self.spell_vars['effect_type'].set(spell.get('effect', {}).get('type', 'damage'))
		self.spell_vars['success_rate'].set(spell.get('resistance', {}).get('base_success_rate', 100))
		self.spell_vars['learn_level'].set(spell.get('learn_level', 1))
		self.desc_var.set(spell.get('description', ''))

		# Show effect details
		self.effect_text.delete('1.0', tk.END)
		effect = spell.get('effect', {})
		self.effect_text.insert('1.0', json.dumps(effect, indent=2))

	def save_current(self):
		"""Save current spell."""
		if not self.current_spell:
			return

		category, spell_id = self.current_spell

		if category == 'player':
			spells = self.data.setdefault('player_spells', {})
		else:
			spells = self.data.setdefault('enemy_spells', {})

		spell = spells.setdefault(spell_id, {})
		spell['name'] = self.spell_vars['name'].get()
		spell['mp_cost'] = self.spell_vars['mp_cost'].get()
		spell['target'] = self.spell_vars['target'].get()
		spell['description'] = self.desc_var.get()

		# Parse effect JSON
		try:
			effect_json = self.effect_text.get('1.0', tk.END).strip()
			spell['effect'] = json.loads(effect_json)
		except:
			pass

		messagebox.showinfo("Saved", f"Spell '{spell_id}' updated.\nUse 'Save All' to write to file.")

	def save_all(self):
		"""Save all changes to JSON file."""
		json_path = ASSETS_JSON / 'spell_effects.json'
		try:
			with open(json_path, 'w') as f:
				json.dump(self.data, f, indent=2)
			messagebox.showinfo("Success", "Spell effects saved!")
		except Exception as e:
			messagebox.showerror("Error", f"Failed to save: {e}")

	def generate_asm(self):
		"""Generate assembly code from current data."""
		import subprocess

		generator = PROJECT_ROOT / 'tools' / 'generate_spell_effects.py'
		if generator.exists():
			try:
				result = subprocess.run(['python', str(generator)], capture_output=True, text=True)
				if result.returncode == 0:
					messagebox.showinfo("Success", "Generated spell_effects.asm!")
				else:
					messagebox.showerror("Error", f"Generation failed:\n{result.stderr}")
			except Exception as e:
				messagebox.showerror("Error", f"Failed to run generator: {e}")
		else:
			messagebox.showwarning("Warning", "Generator not found: tools/generate_spell_effects.py")


# ============================================================================
# EXPERIENCE TABLE EDITOR TAB
# ============================================================================

class ExperienceEditorTab(ttk.Frame):
	"""Edit experience and level progression from experience_table.json."""

	def __init__(self, parent, asset_manager):
		super().__init__(parent)
		self.asset_manager = asset_manager
		self.data = None
		self.current_level = -1

		self.create_widgets()
		self.load_data()

	def create_widgets(self):
		"""Create experience editor widgets."""
		# Header
		header = ttk.Frame(self)
		header.pack(fill=tk.X, padx=10, pady=5)

		ttk.Label(header, text="📈 Experience & Level Editor", font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(header, text="💾 Save All", command=self.save_all).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="⚡ Generate ASM", command=self.generate_asm).pack(side=tk.RIGHT, padx=5)
		ttk.Button(header, text="📊 Show Chart", command=self.show_chart).pack(side=tk.RIGHT, padx=5)

		# Main content
		content = ttk.Frame(self)
		content.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left: Level table
		table_frame = ttk.LabelFrame(content, text="Level Progression", padding=5)
		table_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

		# Treeview for levels
		columns = ('level', 'exp', 'str', 'agi', 'hp', 'mp')
		self.level_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

		self.level_tree.heading('level', text='Lvl')
		self.level_tree.heading('exp', text='Exp Required')
		self.level_tree.heading('str', text='STR')
		self.level_tree.heading('agi', text='AGI')
		self.level_tree.heading('hp', text='HP')
		self.level_tree.heading('mp', text='MP')

		self.level_tree.column('level', width=40)
		self.level_tree.column('exp', width=100)
		self.level_tree.column('str', width=50)
		self.level_tree.column('agi', width=50)
		self.level_tree.column('hp', width=50)
		self.level_tree.column('mp', width=50)

		scrollbar = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.level_tree.yview)
		self.level_tree.configure(yscrollcommand=scrollbar.set)

		self.level_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.level_tree.bind('<<TreeviewSelect>>', self.on_select)

		# Right: Level editor
		edit_frame = ttk.LabelFrame(content, text="Edit Level", padding=10)
		edit_frame.pack(side=tk.RIGHT, fill=tk.Y)

		self.level_vars = {}

		fields = [
			('level', 'Level', False),
			('exp', 'Experience Required', True),
			('str', 'Strength', True),
			('agi', 'Agility', True),
			('hp', 'Max HP', True),
			('mp', 'Max MP', True),
		]

		for i, (field, label, editable) in enumerate(fields):
			ttk.Label(edit_frame, text=f"{label}:").grid(row=i, column=0, sticky=tk.W, pady=3)

			var = tk.IntVar(value=0)
			state = 'normal' if editable else 'readonly'
			widget = ttk.Spinbox(edit_frame, textvariable=var, from_=0, to=65535, width=8, state=state)
			widget.grid(row=i, column=1, padx=5, pady=3, sticky=tk.W)

			self.level_vars[field] = var

		# Spells learned section
		spell_frame = ttk.LabelFrame(edit_frame, text="Spells at This Level", padding=5)
		spell_frame.grid(row=len(fields), column=0, columnspan=2, sticky=tk.EW, pady=10)

		self.spell_listbox = tk.Listbox(spell_frame, height=5, width=20)
		self.spell_listbox.pack(fill=tk.X)

		# Save button
		ttk.Button(edit_frame, text="💾 Update Level", command=self.save_current).grid(
			row=len(fields)+1, column=0, columnspan=2, pady=15
		)

		# Quick actions
		quick_frame = ttk.LabelFrame(edit_frame, text="Quick Actions", padding=5)
		quick_frame.grid(row=len(fields)+2, column=0, columnspan=2, sticky=tk.EW)

		ttk.Button(quick_frame, text="Scale +10%", command=lambda: self.scale_exp(1.1)).pack(fill=tk.X, pady=2)
		ttk.Button(quick_frame, text="Scale -10%", command=lambda: self.scale_exp(0.9)).pack(fill=tk.X, pady=2)
		ttk.Button(quick_frame, text="Reset to Original", command=self.reset_original).pack(fill=tk.X, pady=2)

	def load_data(self):
		"""Load experience table data from JSON."""
		json_path = ASSETS_JSON / 'experience_table.json'
		if json_path.exists():
			try:
				with open(json_path, 'r') as f:
					self.data = json.load(f)
					self.populate_table()
			except Exception as e:
				print(f"Error loading experience table: {e}")

	def populate_table(self):
		"""Populate level table from data."""
		# Clear existing
		for item in self.level_tree.get_children():
			self.level_tree.delete(item)

		if not self.data:
			return

		levels = self.data.get('levels', [])
		for level_data in levels:
			lvl = level_data.get('level', 1)
			exp = level_data.get('experience_required', 0)
			stats = level_data.get('stats', {})

			self.level_tree.insert('', tk.END, values=(
				lvl,
				exp,
				stats.get('strength', 0),
				stats.get('agility', 0),
				stats.get('max_hp', 0),
				stats.get('max_mp', 0)
			))

	def on_select(self, event):
		"""Handle level selection."""
		selection = self.level_tree.selection()
		if not selection:
			return

		item = self.level_tree.item(selection[0])
		values = item['values']

		self.current_level = values[0] - 1  # 0-indexed

		self.level_vars['level'].set(values[0])
		self.level_vars['exp'].set(values[1])
		self.level_vars['str'].set(values[2])
		self.level_vars['agi'].set(values[3])
		self.level_vars['hp'].set(values[4])
		self.level_vars['mp'].set(values[5])

		# Show spells
		self.spell_listbox.delete(0, tk.END)
		if self.data and self.current_level >= 0:
			levels = self.data.get('levels', [])
			if self.current_level < len(levels):
				spells = levels[self.current_level].get('spells', {}).get('known', [])
				for spell in spells:
					self.spell_listbox.insert(tk.END, spell)

	def save_current(self):
		"""Save current level."""
		if self.current_level < 0:
			return

		levels = self.data.setdefault('levels', [])

		# Ensure level exists
		while len(levels) <= self.current_level:
			levels.append({'level': len(levels) + 1})

		level_data = levels[self.current_level]
		level_data['experience_required'] = self.level_vars['exp'].get()
		level_data.setdefault('stats', {})
		level_data['stats']['strength'] = self.level_vars['str'].get()
		level_data['stats']['agility'] = self.level_vars['agi'].get()
		level_data['stats']['max_hp'] = self.level_vars['hp'].get()
		level_data['stats']['max_mp'] = self.level_vars['mp'].get()

		self.populate_table()
		messagebox.showinfo("Updated", f"Level {self.current_level + 1} updated.\nUse 'Save All' to write to file.")

	def save_all(self):
		"""Save all changes to JSON file."""
		json_path = ASSETS_JSON / 'experience_table.json'
		try:
			with open(json_path, 'w') as f:
				json.dump(self.data, f, indent=2)
			messagebox.showinfo("Success", "Experience table saved!")
		except Exception as e:
			messagebox.showerror("Error", f"Failed to save: {e}")

	def scale_exp(self, factor: float):
		"""Scale all experience values by factor."""
		if not self.data:
			return

		levels = self.data.get('levels', [])
		for level_data in levels:
			exp = level_data.get('experience_required', 0)
			level_data['experience_required'] = int(exp * factor)

		self.populate_table()
		messagebox.showinfo("Scaled", f"Experience scaled by {factor*100:.0f}%")

	def reset_original(self):
		"""Reset to original Dragon Warrior values."""
		# Original DW experience curve
		original_exp = [
			0, 7, 23, 47, 110, 220, 450, 800, 1300, 2000,
			2900, 4000, 5500, 7500, 10000, 13000, 17000, 21000, 25000, 29000,
			33000, 37000, 41000, 45000, 49000, 53000, 57000, 61000, 65000, 65535
		]

		if self.data:
			levels = self.data.get('levels', [])
			for i, exp in enumerate(original_exp):
				if i < len(levels):
					levels[i]['experience_required'] = exp

			self.populate_table()
			messagebox.showinfo("Reset", "Experience table reset to original Dragon Warrior values")

	def show_chart(self):
		"""Show experience curve chart (if matplotlib available)."""
		try:
			import matplotlib.pyplot as plt

			if not self.data:
				return

			levels = self.data.get('levels', [])
			x = [l.get('level', 0) for l in levels]
			y = [l.get('experience_required', 0) for l in levels]

			plt.figure(figsize=(10, 6))
			plt.plot(x, y, 'b-o', label='Experience Required')
			plt.xlabel('Level')
			plt.ylabel('Experience')
			plt.title('Dragon Warrior Experience Curve')
			plt.grid(True, alpha=0.3)
			plt.legend()
			plt.show()
		except ImportError:
			messagebox.showwarning("Warning", "matplotlib not installed.\nInstall with: pip install matplotlib")

	def generate_asm(self):
		"""Generate assembly code from current data."""
		import subprocess

		generator = PROJECT_ROOT / 'tools' / 'generate_experience_table.py'
		if generator.exists():
			try:
				result = subprocess.run(['python', str(generator)], capture_output=True, text=True)
				if result.returncode == 0:
					messagebox.showinfo("Success", "Generated experience_table.asm!")
				else:
					messagebox.showerror("Error", f"Generation failed:\n{result.stderr}")
			except Exception as e:
				messagebox.showerror("Error", f"Failed to run generator: {e}")
		else:
			messagebox.showwarning("Warning", "Generator not found: tools/generate_experience_table.py")


# ============================================================================
# REGISTRATION HELPER
# ============================================================================

def register_new_tabs(universal_editor):
	"""
	Register the new editor tabs in the Universal Editor.
	
	Call this after creating tabs in the main application:
	
		from editor_tabs_extended import register_new_tabs
		register_new_tabs(app)
	"""
	notebook = universal_editor.notebook
	asset_manager = universal_editor.asset_manager

	# Add Damage Editor Tab
	damage_tab = DamageEditorTab(notebook, asset_manager)
	notebook.add(damage_tab, text="⚔️ Damage")

	# Add Spell Effects Tab
	spell_effects_tab = SpellEffectsEditorTab(notebook, asset_manager)
	notebook.add(spell_effects_tab, text="✨ Spell FX")

	# Add Experience Tab
	experience_tab = ExperienceEditorTab(notebook, asset_manager)
	notebook.add(experience_tab, text="📈 Experience")

	return damage_tab, spell_effects_tab, experience_tab


if __name__ == '__main__':
	# Standalone test
	root = tk.Tk()
	root.title("Extended Editor Tabs Test")
	root.geometry("800x600")

	notebook = ttk.Notebook(root)
	notebook.pack(fill=tk.BOTH, expand=True)

	# Mock asset manager
	class MockAssetManager:
		pass

	am = MockAssetManager()

	# Add tabs
	damage_tab = DamageEditorTab(notebook, am)
	notebook.add(damage_tab, text="⚔️ Damage")

	spell_tab = SpellEffectsEditorTab(notebook, am)
	notebook.add(spell_tab, text="✨ Spell FX")

	exp_tab = ExperienceEditorTab(notebook, am)
	notebook.add(exp_tab, text="📈 Experience")

	root.mainloop()
