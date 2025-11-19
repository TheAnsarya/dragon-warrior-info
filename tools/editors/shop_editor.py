#!/usr/bin/env python3
"""
Dragon Warrior Shop Editor
Interactive editor for shop inventories and inn prices
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich.columns import Columns
from rich.text import Text
from rich import box

# Add extraction directory to path
import sys
sys.path.append(str(Path(__file__).parent.parent / 'tools' / 'extraction'))
from data_structures import ShopData

console = Console()

class ShopEditor:
	"""Interactive shop editor"""

	def __init__(self, json_file: str, items_file: str = None):
		self.json_file = Path(json_file)
		self.items_file = Path(items_file) if items_file else None
		self.shops: Dict[str, Dict] = {}
		self.original_shops: Dict[str, Dict] = {}
		self.items: Dict[str, Dict] = {}
		self.load_shops()
		self.load_items()

	def load_shops(self):
		"""Load shop data from JSON file"""
		try:
			if self.json_file.exists():
				with open(self.json_file, 'r', encoding='utf-8') as f:
					self.shops = json.load(f)
					self.original_shops = json.loads(json.dumps(self.shops))	# Deep copy
				console.print(f"[green]✅ Loaded {len(self.shops)} shops from {self.json_file}[/green]")
			else:
				console.print(f"[yellow]⚠️	File {self.json_file} not found. Creating new shop data.[/yellow]")
				self.shops = {}
				self.original_shops = {}
		except Exception as e:
			console.print(f"[red]❌ Error loading shops: {e}[/red]")
			self.shops = {}
			self.original_shops = {}

	def load_items(self):
		"""Load item data for reference"""
		if not self.items_file:
			# Try to find items file in same directory
			items_path = self.json_file.parent / "items.json"
			if items_path.exists():
				self.items_file = items_path

		try:
			if self.items_file and self.items_file.exists():
				with open(self.items_file, 'r', encoding='utf-8') as f:
					self.items = json.load(f)
				console.print(f"[green]✅ Loaded {len(self.items)} items for reference[/green]")
			else:
				console.print(f"[yellow]⚠️	No items file found. Item names will not be displayed.[/yellow]")
				self.items = {}
		except Exception as e:
			console.print(f"[red]❌ Error loading items: {e}[/red]")
			self.items = {}

	def save_shops(self):
		"""Save shop data to JSON file"""
		try:
			self.json_file.parent.mkdir(parents=True, exist_ok=True)
			with open(self.json_file, 'w', encoding='utf-8') as f:
				json.dump(self.shops, f, indent=2, ensure_ascii=False)
			console.print(f"[green]✅ Saved shops to {self.json_file}[/green]")
			return True
		except Exception as e:
			console.print(f"[red]❌ Error saving shops: {e}[/red]")
			return False

	def get_item_name(self, item_id: int) -> str:
		"""Get item name from item ID"""
		if str(item_id) in self.items:
			return self.items[str(item_id)]['name']
		return f"Item {item_id}"

	def display_all_shops(self):
		"""Display all shops in a table"""
		if not self.shops:
			console.print("[yellow]🏪 No shops loaded[/yellow]")
			return

		table = Table(title="🏪 Dragon Warrior Shops", box=box.ROUNDED)
		table.add_column("ID", justify="center", width=4)
		table.add_column("Name", width=20)
		table.add_column("Type", width=12)
		table.add_column("Items", justify="center", width=8)
		table.add_column("Inn Price", justify="right", width=10)
		table.add_column("Location", width=15)

		# Sort by shop ID
		for shop_id in sorted([int(k) for k in self.shops.keys()]):
			shop = self.shops[str(shop_id)]

			# Determine shop type
			shop_type = "Shop"
			if shop.get('inn_price'):
				shop_type = "Inn + Shop" if shop.get('items') else "Inn"

			# Color code by type
			type_color = "cyan" if "Inn" in shop_type else "green"

			inn_price = f"${shop['inn_price']}" if shop.get('inn_price') else "-"
			item_count = len(shop.get('items', []))

			table.add_row(
				f"[{type_color}]{shop_id}[/{type_color}]",
				f"[{type_color}]{shop['name']}[/{type_color}]",
				f"[{type_color}]{shop_type}[/{type_color}]",
				f"[yellow]{item_count}[/yellow]",
				f"[green]{inn_price}[/green]",
				shop.get('location', 'Unknown')
			)

		console.print(table)

	def display_shop_details(self, shop_id: str):
		"""Display detailed information about a shop"""
		if shop_id not in self.shops:
			console.print(f"[red]❌ Shop ID {shop_id} not found[/red]")
			return

		shop = self.shops[shop_id]

		# Create shop info panel
		shop_type = "Shop"
		if shop.get('inn_price'):
			shop_type = "Inn + Shop" if shop.get('items') else "Inn"

		info_text = f"[bold cyan]Name:[/bold cyan] {shop['name']}\n"
		info_text += f"[bold yellow]Type:[/bold yellow] {shop_type}\n"
		info_text += f"[bold blue]Location:[/bold blue] {shop.get('location', 'Unknown')}\n"

		if shop.get('inn_price'):
			info_text += f"[bold green]Inn Price:[/bold green] ${shop['inn_price']}"

		info_panel = Panel(
			info_text,
			title=f"🏪 Shop {shop_id} Details",
			border_style="cyan"
		)

		# Create inventory panel
		items_list = shop.get('items', [])
		if items_list:
			inventory_text = ""
			for i, item_id in enumerate(items_list):
				item_name = self.get_item_name(item_id)
				inventory_text += f"[yellow]{i+1:2d}.[/yellow] [cyan]{item_name}[/cyan] [dim](ID: {item_id})[/dim]\n"

			inventory_panel = Panel(
				inventory_text.rstrip(),
				title=f"📦 Inventory ({len(items_list)} items)",
				border_style="green"
			)
		else:
			inventory_panel = Panel(
				"[dim]No items in inventory[/dim]",
				title="📦 Inventory",
				border_style="red"
			)

		console.print(Columns([info_panel, inventory_panel]))

		# Show changes if any
		if shop_id in self.original_shops:
			original = self.original_shops[shop_id]
			changes = []

			if original.get('inn_price') != shop.get('inn_price'):
				changes.append(f"[yellow]Inn Price:[/yellow] {original.get('inn_price', 'None')} → [green]{shop.get('inn_price', 'None')}[/green]")

			if original.get('items') != shop.get('items'):
				orig_count = len(original.get('items', []))
				new_count = len(shop.get('items', []))
				changes.append(f"[yellow]Items:[/yellow] {orig_count} items → [green]{new_count} items[/green]")

			if changes:
				changes_panel = Panel(
					"\n".join(changes),
					title="📝 Changes Made",
					border_style="green"
				)
				console.print(changes_panel)

	def edit_shop(self, shop_id: str):
		"""Edit a shop's properties"""
		if shop_id not in self.shops:
			console.print(f"[red]❌ Shop ID {shop_id} not found[/red]")
			return

		shop = self.shops[shop_id]
		console.print(f"\n[bold cyan]✏️	Editing Shop: {shop['name']} (ID: {shop_id})[/bold cyan]")

		while True:
			# Display current shop
			self.display_shop_details(shop_id)

			console.print("\n[bold]What would you like to edit?[/bold]")
			console.print("1. 🏪 Shop Name")
			console.print("2. 📍 Location")
			console.print("3. 🛏️	Inn Price")
			console.print("4. 📦 Inventory")
			console.print("5. 💾 Save & Exit")
			console.print("6. 🚪 Exit without saving")

			choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6"])

			if choice == "1":
				new_name = Prompt.ask(f"Enter new name (current: {shop['name']})", default=shop['name'])
				if new_name.strip():
					shop['name'] = new_name.strip()
					console.print(f"[green]✅ Name updated to '{new_name.strip()}'[/green]")
				else:
					console.print("[red]❌ Name cannot be empty[/red]")

			elif choice == "2":
				new_location = Prompt.ask(f"Enter new location (current: {shop.get('location', 'Unknown')})",
										default=shop.get('location', ''))
				shop['location'] = new_location.strip()
				console.print(f"[green]✅ Location updated to '{new_location.strip()}'[/green]")

			elif choice == "3":
				current_price = shop.get('inn_price', 0)
				if current_price == 0:
					console.print("[yellow]This shop currently has no inn. Set a price to add inn functionality.[/yellow]")

				new_price = IntPrompt.ask(f"Enter inn price (current: {current_price}, 0 to remove)", default=current_price)

				if new_price < 0:
					console.print("[red]❌ Inn price cannot be negative[/red]")
				elif new_price == 0:
					shop.pop('inn_price', None)
					console.print("[green]✅ Inn functionality removed[/green]")
				else:
					shop['inn_price'] = new_price
					console.print(f"[green]✅ Inn price updated to ${new_price}[/green]")

			elif choice == "4":
				self._edit_inventory(shop)

			elif choice == "5":
				if self.save_shops():
					console.print("[green]✅ Shop saved successfully[/green]")
				break

			elif choice == "6":
				console.print("[yellow]⚠️	Exiting without saving[/yellow]")
				break

	def _edit_inventory(self, shop: Dict):
		"""Edit shop inventory"""
		while True:
			items = shop.get('items', [])

			console.print(f"\n[bold cyan]📦 Inventory for {shop['name']}[/bold cyan]")

			if items:
				table = Table(box=box.SIMPLE)
				table.add_column("Slot", justify="center", width=6)
				table.add_column("Item ID", justify="center", width=8)
				table.add_column("Item Name", width=20)

				for i, item_id in enumerate(items):
					item_name = self.get_item_name(item_id)
					table.add_row(
						str(i + 1),
						str(item_id),
						item_name
					)

				console.print(table)
			else:
				console.print("[dim]Inventory is empty[/dim]")

			console.print("\n[bold]Inventory Options:[/bold]")
			console.print("1. ➕ Add item")
			console.print("2. ➖ Remove item")
			console.print("3. 🔄 Replace item")
			console.print("4. 🗑️	Clear inventory")
			console.print("5. 🔙 Back to shop menu")

			choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5"])

			if choice == "1":
				item_id = IntPrompt.ask("Enter item ID to add")
				if item_id >= 0:
					if 'items' not in shop:
						shop['items'] = []
					shop['items'].append(item_id)
					item_name = self.get_item_name(item_id)
					console.print(f"[green]✅ Added {item_name} (ID: {item_id})[/green]")
				else:
					console.print("[red]❌ Item ID must be non-negative[/red]")

			elif choice == "2":
				if not items:
					console.print("[yellow]⚠️	Inventory is empty[/yellow]")
					continue

				slot = IntPrompt.ask(f"Enter slot number to remove (1-{len(items)})")
				if 1 <= slot <= len(items):
					removed_item = items.pop(slot - 1)
					item_name = self.get_item_name(removed_item)
					console.print(f"[green]✅ Removed {item_name} from slot {slot}[/green]")
				else:
					console.print(f"[red]❌ Invalid slot number. Must be between 1 and {len(items)}[/red]")

			elif choice == "3":
				if not items:
					console.print("[yellow]⚠️	Inventory is empty[/yellow]")
					continue

				slot = IntPrompt.ask(f"Enter slot number to replace (1-{len(items)})")
				if 1 <= slot <= len(items):
					new_item_id = IntPrompt.ask("Enter new item ID")
					if new_item_id >= 0:
						old_item = items[slot - 1]
						items[slot - 1] = new_item_id
						old_name = self.get_item_name(old_item)
						new_name = self.get_item_name(new_item_id)
						console.print(f"[green]✅ Replaced {old_name} with {new_name} in slot {slot}[/green]")
					else:
						console.print("[red]❌ Item ID must be non-negative[/red]")
				else:
					console.print(f"[red]❌ Invalid slot number. Must be between 1 and {len(items)}[/red]")

			elif choice == "4":
				if items:
					confirm = Confirm.ask("Clear entire inventory?")
					if confirm:
						shop['items'] = []
						console.print("[green]✅ Inventory cleared[/green]")
				else:
					console.print("[yellow]⚠️	Inventory is already empty[/yellow]")

			elif choice == "5":
				break

	def create_shop(self):
		"""Create a new shop"""
		console.print("\n[bold cyan]🆕 Creating New Shop[/bold cyan]")

		# Find next available ID
		existing_ids = [int(k) for k in self.shops.keys()] if self.shops else []
		next_id = max(existing_ids, default=-1) + 1

		shop_id = IntPrompt.ask(f"Enter shop ID", default=next_id)

		if str(shop_id) in self.shops:
			console.print(f"[red]❌ Shop ID {shop_id} already exists[/red]")
			return

		# Collect shop information
		name = Prompt.ask("Enter shop name")
		location = Prompt.ask("Enter location", default="")

		# Ask about inn functionality
		has_inn = Confirm.ask("Does this shop have an inn?")
		inn_price = IntPrompt.ask("Enter inn price", default=8) if has_inn else 0

		# Create shop data
		shop_data = {
			'name': name,
			'location': location,
			'items': []
		}

		if inn_price > 0:
			shop_data['inn_price'] = inn_price

		self.shops[str(shop_id)] = shop_data
		console.print(f"[green]✅ Created shop '{name}' with ID {shop_id}[/green]")

		# Ask if they want to add items
		add_items = Confirm.ask("Add items to inventory now?")
		if add_items:
			self._edit_inventory(shop_data)

	def delete_shop(self, shop_id: str):
		"""Delete a shop"""
		if shop_id not in self.shops:
			console.print(f"[red]❌ Shop ID {shop_id} not found[/red]")
			return

		shop = self.shops[shop_id]
		confirm = Confirm.ask(f"Delete shop '{shop['name']}' (ID: {shop_id})?")

		if confirm:
			del self.shops[shop_id]
			console.print(f"[green]✅ Deleted shop '{shop['name']}'[/green]")
		else:
			console.print("[yellow]⚠️	Delete cancelled[/yellow]")

	def search_shops(self):
		"""Search shops by name or location"""
		search_term = Prompt.ask("Enter search term (name, location, etc.)").lower()

		found_shops = []
		for shop_id, shop in self.shops.items():
			if (search_term in shop['name'].lower() or
				search_term in shop.get('location', '').lower()):
				found_shops.append((shop_id, shop))

		if found_shops:
			console.print(f"\n[green]🔍 Found {len(found_shops)} shops matching '{search_term}':[/green]")

			table = Table(box=box.SIMPLE)
			table.add_column("ID", justify="center")
			table.add_column("Name")
			table.add_column("Location")
			table.add_column("Items", justify="center")
			table.add_column("Inn Price", justify="right")

			for shop_id, shop in found_shops:
				inn_price = f"${shop['inn_price']}" if shop.get('inn_price') else "-"
				item_count = len(shop.get('items', []))

				table.add_row(
					shop_id,
					shop['name'],
					shop.get('location', 'Unknown'),
					str(item_count),
					inn_price
				)

			console.print(table)
		else:
			console.print(f"[yellow]🔍 No shops found matching '{search_term}'[/yellow]")

	def export_shop_list(self):
		"""Export shop list to text file"""
		output_file = self.json_file.parent / "shop_list.txt"

		try:
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write("Dragon Warrior Shop List\n")
				f.write("=" * 50 + "\n\n")

				for shop_id in sorted([int(k) for k in self.shops.keys()]):
					shop = self.shops[str(shop_id)]

					f.write(f"ID {shop_id}: {shop['name']}\n")
					f.write(f"	Location: {shop.get('location', 'Unknown')}\n")

					if shop.get('inn_price'):
						f.write(f"	Inn Price: ${shop['inn_price']}\n")

					items = shop.get('items', [])
					if items:
						f.write(f"	Items ({len(items)}):\n")
						for i, item_id in enumerate(items):
							item_name = self.get_item_name(item_id)
							f.write(f"	{i+1}. {item_name} (ID: {item_id})\n")
					else:
						f.write("	Items: None\n")

					f.write("\n")

			console.print(f"[green]✅ Exported shop list to {output_file}[/green]")

		except Exception as e:
			console.print(f"[red]❌ Error exporting shop list: {e}[/red]")

	def run(self):
		"""Main editor loop"""
		console.print("[bold green]🏪 Dragon Warrior Shop Editor[/bold green]\n")

		while True:
			console.print("\n[bold]What would you like to do?[/bold]")
			console.print("1. 📋 List all shops")
			console.print("2. 👁️	View shop details")
			console.print("3. ✏️	Edit shop")
			console.print("4. 🆕 Create new shop")
			console.print("5. 🗑️	Delete shop")
			console.print("6. 🔍 Search shops")
			console.print("7. 💾 Save changes")
			console.print("8. 📄 Export shop list")
			console.print("9. 🚪 Exit")

			choice = Prompt.ask("Enter your choice", choices=["1", "2", "3", "4", "5", "6", "7", "8", "9"])

			if choice == "1":
				self.display_all_shops()

			elif choice == "2":
				shop_id = Prompt.ask("Enter shop ID to view")
				self.display_shop_details(shop_id)

			elif choice == "3":
				shop_id = Prompt.ask("Enter shop ID to edit")
				self.edit_shop(shop_id)

			elif choice == "4":
				self.create_shop()

			elif choice == "5":
				shop_id = Prompt.ask("Enter shop ID to delete")
				self.delete_shop(shop_id)

			elif choice == "6":
				self.search_shops()

			elif choice == "7":
				self.save_shops()

			elif choice == "8":
				self.export_shop_list()

			elif choice == "9":
				# Ask to save before exit
				if self.shops != self.original_shops:
					save_confirm = Confirm.ask("Save changes before exit?")
					if save_confirm:
						self.save_shops()

				console.print("[bold cyan]👋 Thanks for using Dragon Warrior Shop Editor![/bold cyan]")
				break

@click.command()
@click.argument('json_file', type=click.Path())
@click.option('--items-file', '-i', help='Items JSON file for reference')
def shop_editor(json_file: str, items_file: str):
	"""Interactive Dragon Warrior shop editor"""

	editor = ShopEditor(json_file, items_file)
	editor.run()

if __name__ == "__main__":
	shop_editor()
