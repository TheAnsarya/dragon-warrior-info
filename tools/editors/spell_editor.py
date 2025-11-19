#!/usr/bin/env python3
"""
Dragon Warrior Spell Editor
Interactive editor for spell statistics and properties
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt
from rich.columns import Columns
from rich.text import Text
from rich import box

# Add extraction directory to path
import sys
sys.path.append(str(Path(__file__).parent.parent / 'tools' / 'extraction'))
from data_structures import SpellData

console = Console()

class SpellEditor:
	"""Interactive spell editor"""

	def __init__(self, json_file: str):
		self.json_file = Path(json_file)
		self.spells: Dict[str, Dict] = {}
		self.original_spells: Dict[str, Dict] = {}
		self.load_spells()

	def load_spells(self):
		"""Load spell data from JSON file"""
		try:
			if self.json_file.exists():
				with open(self.json_file, 'r', encoding='utf-8') as f:
					self.spells = json.load(f)
					self.original_spells = json.loads(json.dumps(self.spells))	# Deep copy
				console.print(f"[green]✅ Loaded {len(self.spells)} spells from {self.json_file}[/green]")
			else:
				console.print(f"[yellow]⚠️	File {self.json_file} not found. Creating new spell data.[/yellow]")
				self.spells = {}
				self.original_spells = {}
		except Exception as e:
			console.print(f"[red]❌ Error loading spells: {e}[/red]")
			self.spells = {}
			self.original_spells = {}

	def save_spells(self):
		"""Save spell data to JSON file"""
		try:
			self.json_file.parent.mkdir(parents=True, exist_ok=True)
			with open(self.json_file, 'w', encoding='utf-8') as f:
				json.dump(self.spells, f, indent=2, ensure_ascii=False)
			console.print(f"[green]✅ Saved spells to {self.json_file}[/green]")
			return True
		except Exception as e:
			console.print(f"[red]❌ Error saving spells: {e}[/red]")
			return False

	def display_all_spells(self):
		"""Display all spells in a table"""
		if not self.spells:
			console.print("[yellow]📝 No spells loaded[/yellow]")
			return

		table = Table(title="🪄 Dragon Warrior Spells", box=box.ROUNDED)
		table.add_column("ID", justify="center", width=4)
		table.add_column("Name", width=15)
		table.add_column("MP Cost", justify="right", width=8)
		table.add_column("Power", justify="right", width=7)
		table.add_column("Learn Lvl", justify="right", width=10)
		table.add_column("Type", width=12)
		table.add_column("Description", width=30)

		# Sort by spell ID
		for spell_id in sorted([int(k) for k in self.spells.keys()]):
			spell = self.spells[str(spell_id)]

			# Color code by type
			type_colors = {
				0: "blue",	 # Healing
				1: "red",		# Attack
				2: "green",	# Status
				3: "yellow",	 # Utility
			}
			color = type_colors.get(spell.get('spell_type', 3), "white")

			# Format type name
			type_names = {
				0: "Healing",
				1: "Attack",
				2: "Status",
				3: "Utility"
			}
			type_name = type_names.get(spell.get('spell_type', 3), "Unknown")

			table.add_row(
				f"[{color}]{spell_id}[/{color}]",
				f"[{color}]{spell['name']}[/{color}]",
				f"[cyan]{spell['mp_cost']}[/cyan]",
				f"[magenta]{spell['power']}[/magenta]",
				f"[green]{spell['learn_level']}[/green]",
				f"[{color}]{type_name}[/{color}]",
				spell.get('description', 'No description')[:28] + ("..." if len(spell.get('description', '')) > 28 else "")
			)

		console.print(table)

	def display_spell_details(self, spell_id: str):
		"""Display detailed information about a spell"""
		if spell_id not in self.spells:
			console.print(f"[red]❌ Spell ID {spell_id} not found[/red]")
			return

		spell = self.spells[spell_id]

		# Create detailed display panels
		info_panel = Panel(
			f"[bold cyan]Name:[/bold cyan] {spell['name']}\n"
			f"[bold yellow]MP Cost:[/bold yellow] {spell['mp_cost']}\n"
			f"[bold magenta]Power:[/bold magenta] {spell['power']}\n"
			f"[bold green]Learn Level:[/bold green] {spell['learn_level']}\n"
			f"[bold blue]Spell Type:[/bold blue] {spell.get('spell_type', 3)}",
			title=f"🪄 Spell {spell_id} Details",
			border_style="cyan"
		)

		desc_text = spell.get('description', 'No description available')
		desc_panel = Panel(
			desc_text,
			title="📜 Description",
			border_style="yellow"
		)

		console.print(Columns([info_panel, desc_panel]))

		# Show changes if any
		if spell_id in self.original_spells:
			original = self.original_spells[spell_id]
			changes = []

			for key in ['mp_cost', 'power', 'learn_level', 'spell_type']:
				if original.get(key) != spell.get(key):
					changes.append(f"[yellow]{key}:[/yellow] {original.get(key)} → [green]{spell.get(key)}[/green]")

			if changes:
				changes_panel = Panel(
					"\n".join(changes),
					title="📝 Changes Made",
					border_style="green"
				)
				console.print(changes_panel)

	def edit_spell(self, spell_id: str):
		"""Edit a spell's properties"""
		if spell_id not in self.spells:
			console.print(f"[red]❌ Spell ID {spell_id} not found[/red]")
			return

		spell = self.spells[spell_id]
		console.print(f"\n[bold cyan]✏️	Editing Spell: {spell['name']} (ID: {spell_id})[/bold cyan]")

		while True:
			# Display current spell
			self.display_spell_details(spell_id)

			console.print("\n[bold]What would you like to edit?[/bold]")
			console.print("1. 💙 MP Cost")
			console.print("2. ⚡ Power")
			console.print("3. 📈 Learn Level")
			console.print("4. 🔮 Spell Type")
			console.print("5. 📝 Name")
			console.print("6. 📜 Description")
			console.print("7. 💾 Save & Exit")
			console.print("8. 🚪 Exit without saving")

			choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8"])

			if choice == "1":
				new_cost = IntPrompt.ask(f"Enter new MP cost (current: {spell['mp_cost']})", default=spell['mp_cost'])
				if 0 <= new_cost <= 255:
					spell['mp_cost'] = new_cost
					console.print(f"[green]✅ MP cost updated to {new_cost}[/green]")
				else:
					console.print("[red]❌ MP cost must be between 0 and 255[/red]")

			elif choice == "2":
				new_power = IntPrompt.ask(f"Enter new power (current: {spell['power']})", default=spell['power'])
				if 0 <= new_power <= 255:
					spell['power'] = new_power
					console.print(f"[green]✅ Power updated to {new_power}[/green]")
				else:
					console.print("[red]❌ Power must be between 0 and 255[/red]")

			elif choice == "3":
				new_level = IntPrompt.ask(f"Enter new learn level (current: {spell['learn_level']})", default=spell['learn_level'])
				if 1 <= new_level <= 30:
					spell['learn_level'] = new_level
					console.print(f"[green]✅ Learn level updated to {new_level}[/green]")
				else:
					console.print("[red]❌ Learn level must be between 1 and 30[/red]")

			elif choice == "4":
				console.print("\nSpell Types:")
				console.print("0. 💚 Healing")
				console.print("1. ❤️	Attack")
				console.print("2. 💙 Status")
				console.print("3. 💛 Utility")

				new_type = IntPrompt.ask(f"Enter spell type (current: {spell.get('spell_type', 3)})", default=spell.get('spell_type', 3))
				if 0 <= new_type <= 3:
					spell['spell_type'] = new_type
					console.print(f"[green]✅ Spell type updated to {new_type}[/green]")
				else:
					console.print("[red]❌ Spell type must be between 0 and 3[/red]")

			elif choice == "5":
				new_name = Prompt.ask(f"Enter new name (current: {spell['name']})", default=spell['name'])
				if new_name.strip():
					spell['name'] = new_name.strip()
					console.print(f"[green]✅ Name updated to '{new_name.strip()}'[/green]")
				else:
					console.print("[red]❌ Name cannot be empty[/red]")

			elif choice == "6":
				current_desc = spell.get('description', '')
				console.print(f"[dim]Current: {current_desc}[/dim]")
				new_desc = Prompt.ask("Enter new description", default=current_desc)
				spell['description'] = new_desc
				console.print("[green]✅ Description updated[/green]")

			elif choice == "7":
				if self.save_spells():
					console.print("[green]✅ Spell saved successfully[/green]")
				break

			elif choice == "8":
				console.print("[yellow]⚠️	Exiting without saving[/yellow]")
				break

	def create_spell(self):
		"""Create a new spell"""
		console.print("\n[bold cyan]🆕 Creating New Spell[/bold cyan]")

		# Find next available ID
		existing_ids = [int(k) for k in self.spells.keys()] if self.spells else []
		next_id = max(existing_ids, default=-1) + 1

		spell_id = IntPrompt.ask(f"Enter spell ID", default=next_id)

		if str(spell_id) in self.spells:
			console.print(f"[red]❌ Spell ID {spell_id} already exists[/red]")
			return

		# Collect spell information
		name = Prompt.ask("Enter spell name")
		mp_cost = IntPrompt.ask("Enter MP cost", default=0)
		power = IntPrompt.ask("Enter power", default=0)
		learn_level = IntPrompt.ask("Enter learn level", default=1)

		console.print("\nSpell Types:")
		console.print("0. 💚 Healing")
		console.print("1. ❤️	Attack")
		console.print("2. 💙 Status")
		console.print("3. 💛 Utility")
		spell_type = IntPrompt.ask("Enter spell type", default=3)

		description = Prompt.ask("Enter description (optional)", default="")

		# Create spell data
		spell_data = {
			'name': name,
			'mp_cost': mp_cost,
			'power': power,
			'learn_level': learn_level,
			'spell_type': spell_type,
			'description': description
		}

		self.spells[str(spell_id)] = spell_data
		console.print(f"[green]✅ Created spell '{name}' with ID {spell_id}[/green]")

	def delete_spell(self, spell_id: str):
		"""Delete a spell"""
		if spell_id not in self.spells:
			console.print(f"[red]❌ Spell ID {spell_id} not found[/red]")
			return

		spell = self.spells[spell_id]
		confirm = Prompt.ask(f"Delete spell '{spell['name']}' (ID: {spell_id})? [y/N]", default="n")

		if confirm.lower() == 'y':
			del self.spells[spell_id]
			console.print(f"[green]✅ Deleted spell '{spell['name']}'[/green]")
		else:
			console.print("[yellow]⚠️	Delete cancelled[/yellow]")

	def search_spells(self):
		"""Search spells by name or properties"""
		search_term = Prompt.ask("Enter search term (name, type, etc.)").lower()

		found_spells = []
		for spell_id, spell in self.spells.items():
			if (search_term in spell['name'].lower() or
				search_term in spell.get('description', '').lower() or
				search_term in str(spell.get('spell_type', ''))):
				found_spells.append((spell_id, spell))

		if found_spells:
			console.print(f"\n[green]🔍 Found {len(found_spells)} spells matching '{search_term}':[/green]")

			table = Table(box=box.SIMPLE)
			table.add_column("ID", justify="center")
			table.add_column("Name")
			table.add_column("MP Cost", justify="right")
			table.add_column("Power", justify="right")
			table.add_column("Type")

			for spell_id, spell in found_spells:
				type_names = {0: "Healing", 1: "Attack", 2: "Status", 3: "Utility"}
				type_name = type_names.get(spell.get('spell_type', 3), "Unknown")

				table.add_row(
					spell_id,
					spell['name'],
					str(spell['mp_cost']),
					str(spell['power']),
					type_name
				)

			console.print(table)
		else:
			console.print(f"[yellow]🔍 No spells found matching '{search_term}'[/yellow]")

	def export_spell_list(self):
		"""Export spell list to text file"""
		output_file = self.json_file.parent / "spell_list.txt"

		try:
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write("Dragon Warrior Spell List\n")
				f.write("=" * 50 + "\n\n")

				for spell_id in sorted([int(k) for k in self.spells.keys()]):
					spell = self.spells[str(spell_id)]
					type_names = {0: "Healing", 1: "Attack", 2: "Status", 3: "Utility"}
					type_name = type_names.get(spell.get('spell_type', 3), "Unknown")

					f.write(f"ID {spell_id}: {spell['name']}\n")
					f.write(f"	MP Cost: {spell['mp_cost']}\n")
					f.write(f"	Power: {spell['power']}\n")
					f.write(f"	Learn Level: {spell['learn_level']}\n")
					f.write(f"	Type: {type_name}\n")
					f.write(f"	Description: {spell.get('description', 'None')}\n\n")

			console.print(f"[green]✅ Exported spell list to {output_file}[/green]")

		except Exception as e:
			console.print(f"[red]❌ Error exporting spell list: {e}[/red]")

	def run(self):
		"""Main editor loop"""
		console.print("[bold magenta]🪄 Dragon Warrior Spell Editor[/bold magenta]\n")

		while True:
			console.print("\n[bold]What would you like to do?[/bold]")
			console.print("1. 📋 List all spells")
			console.print("2. 👁️	View spell details")
			console.print("3. ✏️	Edit spell")
			console.print("4. 🆕 Create new spell")
			console.print("5. 🗑️	Delete spell")
			console.print("6. 🔍 Search spells")
			console.print("7. 💾 Save changes")
			console.print("8. 📄 Export spell list")
			console.print("9. 🚪 Exit")

			choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])

			if choice == "1":
				self.display_all_spells()

			elif choice == "2":
				spell_id = Prompt.ask("Enter spell ID to view")
				self.display_spell_details(spell_id)

			elif choice == "3":
				spell_id = Prompt.ask("Enter spell ID to edit")
				self.edit_spell(spell_id)

			elif choice == "4":
				self.create_spell()

			elif choice == "5":
				spell_id = Prompt.ask("Enter spell ID to delete")
				self.delete_spell(spell_id)

			elif choice == "6":
				self.search_spells()

			elif choice == "7":
				self.save_spells()

			elif choice == "8":
				self.export_spell_list()

			elif choice == "9":
				# Ask to save before exit
				if self.spells != self.original_spells:
					save_confirm = Prompt.ask("Save changes before exit? [Y/n]", default="y")
					if save_confirm.lower() != 'n':
						self.save_spells()

				console.print("[bold cyan]👋 Thanks for using Dragon Warrior Spell Editor![/bold cyan]")
				break

@click.command()
@click.argument('json_file', type=click.Path())
def spell_editor(json_file: str):
	"""Interactive Dragon Warrior spell editor"""

	editor = SpellEditor(json_file)
	editor.run()

if __name__ == "__main__":
	spell_editor()
