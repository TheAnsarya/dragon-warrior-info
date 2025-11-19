#!/usr/bin/env python3
"""
Dragon Warrior Item Editor
Interactive editor for weapons, armor, and items
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich import print as rprint

# Add extraction directory to path
sys.path.append(str(Path(__file__).parent.parent / 'extraction'))
from data_structures import ItemData, ItemType

console = Console()

class ItemEditor:
	"""Interactive item editor"""

	def __init__(self, data_file: str):
		self.data_file = Path(data_file)
		self.items: Dict[int, ItemData] = {}
		self.load_data()

	def load_data(self):
		"""Load item data from JSON"""
		if self.data_file.exists():
			try:
				with open(self.data_file, 'r', encoding='utf-8') as f:
					data = json.load(f)

				for item_id_str, item_data in data.items():
					item_id = int(item_id_str)
					item = ItemData(**item_data)
					self.items[item_id] = item

				console.print(f"[green]✅ Loaded {len(self.items)} items from {self.data_file}[/green]")
			except Exception as e:
				console.print(f"[red]❌ Error loading data: {e}[/red]")
				self.items = {}
		else:
			console.print(f"[yellow]⚠️	Data file not found: {self.data_file}[/yellow]")

	def save_data(self):
		"""Save item data to JSON"""
		try:
			data = {str(k): v.to_dict() for k, v in self.items.items()}
			with open(self.data_file, 'w', encoding='utf-8') as f:
				json.dump(data, f, indent=2, ensure_ascii=False)
			console.print(f"[green]✅ Saved to {self.data_file}[/green]")
		except Exception as e:
			console.print(f"[red]❌ Error saving: {e}[/red]")

	def display_items(self, item_type: Optional[ItemType] = None):
		"""Display item list"""
		table = Table(title="Dragon Warrior Items")
		table.add_column("ID", style="cyan", width=3)
		table.add_column("Name", style="bold blue", width=15)
		table.add_column("Type", style="yellow", width=8)
		table.add_column("ATK", style="red", width=4)
		table.add_column("DEF", style="green", width=4)
		table.add_column("Buy", style="yellow", width=6)
		table.add_column("Sell", style="cyan", width=6)
		table.add_column("Equip", style="white", width=5)
		table.add_column("Use", style="magenta", width=4)

		filtered_items = self.items
		if item_type:
			filtered_items = {k: v for k, v in self.items.items() if v.item_type == item_type}

		for item_id, item in sorted(filtered_items.items()):
			table.add_row(
				str(item.id),
				item.name,
				item.item_type.name,
				str(item.attack_bonus) if item.attack_bonus > 0 else "-",
				str(item.defense_bonus) if item.defense_bonus > 0 else "-",
				str(item.buy_price),
				str(item.sell_price),
				"✓" if item.equippable else "✗",
				"✓" if item.useable else "✗"
			)

		console.print(table)

	def edit_item(self, item_id: int):
		"""Edit a specific item"""
		if item_id not in self.items:
			console.print(f"[red]❌ Item {item_id} not found[/red]")
			return

		item = self.items[item_id]

		console.print(Panel.fit(
			f"Editing Item: {item.name} (ID: {item.id})",
			border_style="blue"
		))

		# Display current stats
		self._display_item_details(item)

		# Edit menu
		while True:
			rprint("\n[bold cyan]Edit Options:[/bold cyan]")
			rprint("1. Name")
			rprint("2. Item Type")
			rprint("3. Attack Bonus")
			rprint("4. Defense Bonus")
			rprint("5. Buy Price")
			rprint("6. Sell Price")
			rprint("7. Equippable")
			rprint("8. Useable")
			rprint("9. Description")
			rprint("10. Sprite ID")
			rprint("0. Done")

			choice = Prompt.ask("Select option", choices=["0","1","2","3","4","5","6","7","8","9","10"])

			if choice == "0":
				break
			elif choice == "1":
				new_name = Prompt.ask("Enter new name", default=item.name)
				item.name = new_name
			elif choice == "2":
				self._edit_item_type(item)
			elif choice == "3":
				new_attack = IntPrompt.ask("Enter attack bonus", default=item.attack_bonus)
				item.attack_bonus = max(0, new_attack)
			elif choice == "4":
				new_defense = IntPrompt.ask("Enter defense bonus", default=item.defense_bonus)
				item.defense_bonus = max(0, new_defense)
			elif choice == "5":
				new_buy = IntPrompt.ask("Enter buy price", default=item.buy_price)
				item.buy_price = max(0, new_buy)
				item.sell_price = new_buy // 2	# Auto-update sell price
			elif choice == "6":
				new_sell = IntPrompt.ask("Enter sell price", default=item.sell_price)
				item.sell_price = max(0, new_sell)
			elif choice == "7":
				item.equippable = Confirm.ask("Is equippable?", default=item.equippable)
			elif choice == "8":
				item.useable = Confirm.ask("Is useable?", default=item.useable)
			elif choice == "9":
				new_desc = Prompt.ask("Enter description", default=item.description)
				item.description = new_desc
			elif choice == "10":
				new_sprite = IntPrompt.ask("Enter sprite ID", default=item.sprite_id)
				item.sprite_id = new_sprite

			# Show updated stats
			self._display_item_details(item)

		self.items[item_id] = item
		console.print(f"[green]✅ Item {item.name} updated[/green]")

	def _display_item_details(self, item: ItemData):
		"""Display detailed item information"""
		details = f"""[bold]{item.name}[/bold] (ID: {item.id})
[yellow]Type:[/yellow] {item.item_type.name}
[red]Attack:[/red] {item.attack_bonus}	[green]Defense:[/green] {item.defense_bonus}
[yellow]Buy:[/yellow] {item.buy_price}g	[cyan]Sell:[/cyan] {item.sell_price}g
[white]Equippable:[/white] {'Yes' if item.equippable else 'No'}	[magenta]Useable:[/magenta] {'Yes' if item.useable else 'No'}
[dim]Sprite ID:[/dim] {item.sprite_id}
[blue]Description:[/blue] {item.description}"""

		console.print(Panel(details, border_style="green"))

	def _edit_item_type(self, item: ItemData):
		"""Edit item type"""
		rprint("\n[bold]Item Types:[/bold]")
		for i, itype in enumerate(ItemType):
			rprint(f"{i}. {itype.name}")

		type_choice = IntPrompt.ask("Select type", choices=[str(i) for i in range(len(ItemType))])
		item.item_type = list(ItemType)[type_choice]

	def add_item(self):
		"""Add a new item"""
		# Get next available ID
		max_id = max(self.items.keys()) if self.items else -1
		new_id = max_id + 1

		console.print(f"[cyan]Creating new item with ID {new_id}[/cyan]")

		name = Prompt.ask("Enter item name", default=f"NewItem_{new_id}")

		# Select item type
		rprint("\n[bold]Item Types:[/bold]")
		for i, itype in enumerate(ItemType):
			rprint(f"{i}. {itype.name}")
		type_choice = IntPrompt.ask("Select type", choices=[str(i) for i in range(len(ItemType))])
		item_type = list(ItemType)[type_choice]

		attack_bonus = IntPrompt.ask("Enter attack bonus", default=0)
		defense_bonus = IntPrompt.ask("Enter defense bonus", default=0)
		buy_price = IntPrompt.ask("Enter buy price", default=10)

		new_item = ItemData(
			id=new_id,
			name=name,
			item_type=item_type,
			attack_bonus=attack_bonus,
			defense_bonus=defense_bonus,
			buy_price=buy_price,
			sell_price=buy_price // 2,
			equippable=item_type in [ItemType.WEAPON, ItemType.ARMOR, ItemType.SHIELD],
			useable=item_type in [ItemType.TOOL, ItemType.KEY_ITEM],
			sprite_id=new_id + 70,
			description=f"A {name.lower()} for brave adventurers."
		)

		self.items[new_id] = new_item
		console.print(f"[green]✅ Added item {name} with ID {new_id}[/green]")

	def balance_items(self):
		"""Balance item prices and stats"""
		rprint("\n[bold cyan]Balance Options:[/bold cyan]")
		rprint("1. Auto-balance weapon attack values")
		rprint("2. Auto-balance armor defense values")
		rprint("3. Normalize prices (10x stat bonus)")
		rprint("4. Set sell prices to 50% of buy price")
		rprint("0. Back")

		choice = Prompt.ask("Select option", choices=["0","1","2","3","4"])

		if choice == "1":
			weapons = {k: v for k, v in self.items.items() if v.item_type == ItemType.WEAPON}
			for i, (item_id, weapon) in enumerate(sorted(weapons.items())):
				weapon.attack_bonus = 2 + (i * 3)	# Progressive weapon strength
			console.print(f"[green]✅ Balanced {len(weapons)} weapons[/green]")

		elif choice == "2":
			armors = {k: v for k, v in self.items.items() if v.item_type == ItemType.ARMOR}
			for i, (item_id, armor) in enumerate(sorted(armors.items())):
				armor.defense_bonus = 1 + (i * 2)	# Progressive armor defense
			console.print(f"[green]✅ Balanced {len(armors)} armor pieces[/green]")

		elif choice == "3":
			for item in self.items.values():
				total_bonus = item.attack_bonus + item.defense_bonus
				if total_bonus > 0:
					item.buy_price = max(10, total_bonus * 10)
					item.sell_price = item.buy_price // 2
			console.print(f"[green]✅ Normalized all item prices[/green]")

		elif choice == "4":
			for item in self.items.values():
				item.sell_price = item.buy_price // 2
			console.print(f"[green]✅ Updated all sell prices[/green]")

	def run(self):
		"""Run the item editor"""
		console.print(Panel.fit(
			"⚔️ Dragon Warrior Item Editor",
			border_style="yellow"
		))

		while True:
			rprint("\n[bold blue]Main Menu:[/bold blue]")
			rprint("1. List all items")
			rprint("2. List by type")
			rprint("3. Edit item")
			rprint("4. Add item")
			rprint("5. Balance items")
			rprint("6. Save data")
			rprint("7. Reload data")
			rprint("0. Exit")

			choice = Prompt.ask("Select option", choices=["0","1","2","3","4","5","6","7"])

			if choice == "0":
				if Confirm.ask("Save before exit?"):
					self.save_data()
				break
			elif choice == "1":
				self.display_items()
			elif choice == "2":
				rprint("\n[bold]Item Types:[/bold]")
				for i, itype in enumerate(ItemType):
					rprint(f"{i}. {itype.name}")
				type_choice = IntPrompt.ask("Select type", choices=[str(i) for i in range(len(ItemType))])
				item_type = list(ItemType)[type_choice]
				self.display_items(item_type)
			elif choice == "3":
				item_id = IntPrompt.ask("Enter item ID")
				self.edit_item(item_id)
			elif choice == "4":
				self.add_item()
			elif choice == "5":
				self.balance_items()
			elif choice == "6":
				self.save_data()
			elif choice == "7":
				self.load_data()

@click.command()
@click.argument('data_file', type=click.Path())
def edit_items(data_file: str):
	"""Dragon Warrior Item Editor"""
	editor = ItemEditor(data_file)
	editor.run()

if __name__ == "__main__":
	edit_items()
