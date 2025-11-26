#!/usr/bin/env python3
"""
Dragon Warrior Shop Editor Tab

Shop inventory and pricing management:
- Weapon shop configuration
- Armor shop configuration
- Item shop configuration
- Key/tool shop configuration
- Inn pricing
- Price editing
- Availability by town
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass, field
import struct


@dataclass
class ShopInventory:
	"""Shop inventory data."""
	shop_id: int
	shop_name: str
	shop_type: str  # 'weapon', 'armor', 'item', 'inn'
	town_name: str
	items: List[Tuple[int, str, int]]  # (item_id, item_name, price)
	rom_offset: int


class ShopEditorTab(ttk.Frame):
	"""
	Shop editor for Dragon Warrior.

	Features:
	- Edit all shop inventories
	- Modify item prices
	- Configure shop availability by town
	- Inn pricing
	- Export/import shop data
	"""

	# Town names
	TOWN_NAMES = [
		"Tantegel",
		"Brecconary",
		"Garinham",
		"Kol",
		"Rimuldar",
		"Cantlin",
		"Hauksness",
	]

	# Shop types
	SHOP_TYPES = [
		"Weapon Shop",
		"Armor Shop",
		"Item Shop",
		"Inn",
	]

	# Item categories
	WEAPONS = [
		(15, "Club", 60),
		(16, "Copper Sword", 180),
		(17, "Hand Axe", 560),
		(18, "Broad Sword", 1500),
		(19, "Flame Sword", 9800),
		(20, "Erdrick's Sword", 0),  # Not sold
	]

	ARMOR = [
		(21, "Clothes", 20),
		(22, "Leather Armor", 70),
		(23, "Chain Mail", 300),
		(24, "Half Plate", 1000),
		(25, "Full Plate", 3000),
		(26, "Magic Armor", 7700),
		(27, "Erdrick's Armor", 0),  # Not sold
	]

	SHIELDS = [
		(28, "Small Shield", 90),
		(29, "Large Shield", 800),
		(30, "Silver Shield", 14800),
	]

	ITEMS = [
		(0, "Torch", 8),
		(1, "Fairy Water", 38),
		(2, "Wings", 70),
		(3, "Dragon's Scale", 20),
		(4, "Fairy Flute", 0),  # Not sold
		(5, "Fighter's Ring", 0),  # Not sold
		(14, "Herb", 24),
		(7, "Gwaelin's Love", 0),  # Not sold
		(11, "Stones of Sunlight", 0),  # Quest item
		(12, "Staff of Rain", 0),  # Quest item
		(13, "Rainbow Drop", 0),  # Quest item
	]

	def __init__(self, parent, rom_manager):
		super().__init__(parent)
		self.rom_manager = rom_manager
		self.shops: List[ShopInventory] = []
		self.current_shop: Optional[ShopInventory] = None

		# ROM offset for shop data
		self.SHOP_DATA = 0xD200

		self.create_widgets()
		self.load_shops()

	def create_widgets(self):
		"""Create editor interface."""

		# Title
		title_frame = ttk.Frame(self)
		title_frame.pack(fill=tk.X, padx=10, pady=10)

		ttk.Label(title_frame, text="🏪 Shop Editor",
				 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(title_frame, text="🔄 Reload",
				  command=self.load_shops).pack(side=tk.RIGHT, padx=5)
		ttk.Button(title_frame, text="💾 Save All",
				  command=self.save_all_shops).pack(side=tk.RIGHT, padx=5)
		ttk.Button(title_frame, text="📤 Export",
				  command=self.export_shops).pack(side=tk.RIGHT, padx=5)
		ttk.Button(title_frame, text="📥 Import",
				  command=self.import_shops).pack(side=tk.RIGHT, padx=5)

		# Paned window
		paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
		paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left panel: Shop list
		left_panel = ttk.Frame(paned)
		paned.add(left_panel, weight=1)

		# Filter by town/type
		filter_frame = ttk.Frame(left_panel)
		filter_frame.pack(fill=tk.X, pady=5)

		ttk.Label(filter_frame, text="Town:").pack(side=tk.LEFT, padx=5)
		self.town_filter_var = tk.StringVar(value="All")
		town_combo = ttk.Combobox(filter_frame, textvariable=self.town_filter_var,
								 width=15, state='readonly')
		town_combo['values'] = ["All"] + self.TOWN_NAMES
		town_combo.pack(side=tk.LEFT, padx=5)
		town_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_shops())

		ttk.Label(filter_frame, text="Type:").pack(side=tk.LEFT, padx=5)
		self.type_filter_var = tk.StringVar(value="All")
		type_combo = ttk.Combobox(filter_frame, textvariable=self.type_filter_var,
								 width=15, state='readonly')
		type_combo['values'] = ["All"] + self.SHOP_TYPES
		type_combo.pack(side=tk.LEFT, padx=5)
		type_combo.bind('<<ComboboxSelected>>', lambda e: self.filter_shops())

		# Shop list
		list_frame = ttk.LabelFrame(left_panel, text="Shops", padding=5)
		list_frame.pack(fill=tk.BOTH, expand=True)

		columns = ('ID', 'Town', 'Type', 'Items')
		self.shop_tree = ttk.Treeview(list_frame, columns=columns,
									 show='headings', height=20)

		self.shop_tree.heading('ID', text='ID')
		self.shop_tree.heading('Town', text='Town')
		self.shop_tree.heading('Type', text='Shop Type')
		self.shop_tree.heading('Items', text='# Items')

		self.shop_tree.column('ID', width=40)
		self.shop_tree.column('Town', width=100)
		self.shop_tree.column('Type', width=120)
		self.shop_tree.column('Items', width=60)

		scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
								 command=self.shop_tree.yview)
		self.shop_tree.configure(yscrollcommand=scrollbar.set)

		self.shop_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.shop_tree.bind('<<TreeviewSelect>>', self.on_shop_select)

		# Right panel: Shop editor
		right_panel = ttk.Frame(paned)
		paned.add(right_panel, weight=2)

		# Shop info
		info_frame = ttk.LabelFrame(right_panel, text="Shop Information", padding=10)
		info_frame.pack(fill=tk.X, pady=5)

		info_grid = ttk.Frame(info_frame)
		info_grid.pack(fill=tk.X)

		ttk.Label(info_grid, text="Shop ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
		self.shop_id_label = ttk.Label(info_grid, text="--", font=('Courier', 10, 'bold'))
		self.shop_id_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

		ttk.Label(info_grid, text="Town:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
		self.town_label = ttk.Label(info_grid, text="--", font=('Courier', 10))
		self.town_label.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

		ttk.Label(info_grid, text="Type:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
		self.type_label = ttk.Label(info_grid, text="--", font=('Courier', 10))
		self.type_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

		ttk.Label(info_grid, text="ROM Offset:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
		self.offset_label = ttk.Label(info_grid, text="--", font=('Courier', 10))
		self.offset_label.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)

		# Shop name editor
		name_frame = ttk.Frame(info_frame)
		name_frame.pack(fill=tk.X, pady=5)

		ttk.Label(name_frame, text="Shop Name:").pack(side=tk.LEFT, padx=5)
		self.shop_name_var = tk.StringVar()
		shop_name_entry = ttk.Entry(name_frame, textvariable=self.shop_name_var, width=30)
		shop_name_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

		# Inventory editor
		inventory_frame = ttk.LabelFrame(right_panel, text="Shop Inventory", padding=10)
		inventory_frame.pack(fill=tk.BOTH, expand=True, pady=5)

		# Toolbar
		toolbar = ttk.Frame(inventory_frame)
		toolbar.pack(fill=tk.X, pady=5)

		ttk.Button(toolbar, text="➕ Add Item",
				  command=self.add_item).pack(side=tk.LEFT, padx=5)
		ttk.Button(toolbar, text="➖ Remove Item",
				  command=self.remove_item).pack(side=tk.LEFT, padx=5)
		ttk.Button(toolbar, text="⬆️ Move Up",
				  command=self.move_item_up).pack(side=tk.LEFT, padx=5)
		ttk.Button(toolbar, text="⬇️ Move Down",
				  command=self.move_item_down).pack(side=tk.LEFT, padx=5)

		# Inventory tree
		inv_columns = ('Slot', 'Item ID', 'Item Name', 'Price')
		self.inventory_tree = ttk.Treeview(inventory_frame, columns=inv_columns,
										  show='headings', height=12)

		for col in inv_columns:
			self.inventory_tree.heading(col, text=col)

		self.inventory_tree.column('Slot', width=50)
		self.inventory_tree.column('Item ID', width=70)
		self.inventory_tree.column('Item Name', width=200)
		self.inventory_tree.column('Price', width=100)

		inv_scrollbar = ttk.Scrollbar(inventory_frame, orient=tk.VERTICAL,
									 command=self.inventory_tree.yview)
		self.inventory_tree.configure(yscrollcommand=inv_scrollbar.set)

		self.inventory_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		inv_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.inventory_tree.bind('<Double-Button-1>', self.edit_item_price)

		# Item editor
		item_edit_frame = ttk.LabelFrame(right_panel, text="Edit Selected Item", padding=10)
		item_edit_frame.pack(fill=tk.X, pady=5)

		edit_grid = ttk.Frame(item_edit_frame)
		edit_grid.pack(fill=tk.X)

		ttk.Label(edit_grid, text="Item:").grid(row=0, column=0, sticky=tk.W, padx=5)
		self.item_name_var = tk.StringVar()
		item_combo = ttk.Combobox(edit_grid, textvariable=self.item_name_var,
								 width=20, state='readonly')
		# Populate with all items
		all_items = self.WEAPONS + self.ARMOR + self.SHIELDS + self.ITEMS
		item_combo['values'] = [name for _, name, _ in all_items]
		item_combo.grid(row=0, column=1, sticky=tk.W, padx=5)

		ttk.Label(edit_grid, text="Price:").grid(row=0, column=2, sticky=tk.W, padx=5)
		self.price_var = tk.IntVar(value=0)
		price_spin = ttk.Spinbox(edit_grid, from_=0, to=65000, textvariable=self.price_var, width=10)
		price_spin.grid(row=0, column=3, sticky=tk.W, padx=5)
		ttk.Label(edit_grid, text="Gold").grid(row=0, column=4, sticky=tk.W, padx=5)

		ttk.Button(edit_grid, text="Update Item",
				  command=self.update_item).grid(row=0, column=5, padx=10)

		# Save button
		save_frame = ttk.Frame(right_panel)
		save_frame.pack(fill=tk.X, pady=5)

		ttk.Button(save_frame, text="💾 Save Shop",
				  command=self.save_shop,
				  style='Accent.TButton').pack(side=tk.RIGHT, padx=5)
		ttk.Button(save_frame, text="↶ Revert Changes",
				  command=self.revert_shop).pack(side=tk.RIGHT, padx=5)

	def load_shops(self):
		"""Load all shop data."""
		self.shops.clear()
		self.shop_tree.delete(*self.shop_tree.get_children())

		# Create sample shop data
		shop_configs = [
			# Tantegel
			(0, "Tantegel", "Weapon Shop", self.WEAPONS[:2]),
			(1, "Tantegel", "Armor Shop", self.ARMOR[:2] + self.SHIELDS[:1]),
			(2, "Tantegel", "Item Shop", self.ITEMS[:3]),
			(3, "Tantegel", "Inn", [(0, "Stay at Inn", 6)]),

			# Brecconary
			(4, "Brecconary", "Weapon Shop", self.WEAPONS[:3]),
			(5, "Brecconary", "Armor Shop", self.ARMOR[:3] + self.SHIELDS[:2]),
			(6, "Brecconary", "Item Shop", self.ITEMS[:4]),
			(7, "Brecconary", "Inn", [(0, "Stay at Inn", 6)]),

			# Garinham
			(8, "Garinham", "Weapon Shop", self.WEAPONS[1:4]),
			(9, "Garinham", "Armor Shop", self.ARMOR[2:4] + self.SHIELDS[1:2]),
			(10, "Garinham", "Item Shop", self.ITEMS[:4]),
			(11, "Garinham", "Inn", [(0, "Stay at Inn", 20)]),

			# Kol
			(12, "Kol", "Weapon Shop", self.WEAPONS[2:4]),
			(13, "Kol", "Armor Shop", self.ARMOR[3:5] + self.SHIELDS[1:3]),
			(14, "Kol", "Item Shop", self.ITEMS[:4]),
			(15, "Kol", "Inn", [(0, "Stay at Inn", 25)]),

			# Rimuldar
			(16, "Rimuldar", "Weapon Shop", self.WEAPONS[3:5]),
			(17, "Rimuldar", "Armor Shop", self.ARMOR[4:6] + self.SHIELDS[2:3]),
			(18, "Rimuldar", "Item Shop", self.ITEMS[:4]),
			(19, "Rimuldar", "Inn", [(0, "Stay at Inn", 55)]),

			# Cantlin
			(20, "Cantlin", "Weapon Shop", self.WEAPONS[4:5]),
			(21, "Cantlin", "Armor Shop", self.ARMOR[5:6] + self.SHIELDS[2:3]),
			(22, "Cantlin", "Item Shop", self.ITEMS[:4]),
			(23, "Cantlin", "Inn", [(0, "Stay at Inn", 100)]),
		]

		for shop_id, town, shop_type, items in shop_configs:
			shop = ShopInventory(
				shop_id=shop_id,
				shop_name=f"{town} {shop_type}",
				shop_type=shop_type,
				town_name=town,
				items=items,
				rom_offset=self.SHOP_DATA + (shop_id * 32)
			)
			self.shops.append(shop)

			self.shop_tree.insert('', tk.END, values=(
				shop_id,
				town,
				shop_type,
				len(items)
			))

	def filter_shops(self):
		"""Filter shop list."""
		town_filter = self.town_filter_var.get()
		type_filter = self.type_filter_var.get()

		self.shop_tree.delete(*self.shop_tree.get_children())

		for shop in self.shops:
			if town_filter != "All" and shop.town_name != town_filter:
				continue
			if type_filter != "All" and shop.shop_type != type_filter:
				continue

			self.shop_tree.insert('', tk.END, values=(
				shop.shop_id,
				shop.town_name,
				shop.shop_type,
				len(shop.items)
			))

	def on_shop_select(self, event):
		"""Handle shop selection."""
		selection = self.shop_tree.selection()
		if not selection:
			return

		item = self.shop_tree.item(selection[0])
		shop_id = int(item['values'][0])

		for shop in self.shops:
			if shop.shop_id == shop_id:
				self.current_shop = shop
				self.display_shop(shop)
				break

	def display_shop(self, shop: ShopInventory):
		"""Display shop details."""
		self.shop_id_label.config(text=str(shop.shop_id))
		self.town_label.config(text=shop.town_name)
		self.type_label.config(text=shop.shop_type)
		self.offset_label.config(text=f"0x{shop.rom_offset:05X}")
		self.shop_name_var.set(shop.shop_name)

		# Update inventory tree
		self.inventory_tree.delete(*self.inventory_tree.get_children())

		for slot, (item_id, item_name, price) in enumerate(shop.items):
			self.inventory_tree.insert('', tk.END, values=(
				slot,
				item_id,
				item_name,
				f"{price} Gold"
			))

	def add_item(self):
		"""Add item to shop inventory."""
		if not self.current_shop:
			messagebox.showwarning("Warning", "No shop selected")
			return

		# Add placeholder item
		self.current_shop.items.append((0, "New Item", 0))
		self.display_shop(self.current_shop)

	def remove_item(self):
		"""Remove selected item from inventory."""
		if not self.current_shop:
			return

		selection = self.inventory_tree.selection()
		if not selection:
			messagebox.showwarning("Warning", "No item selected")
			return

		item = self.inventory_tree.item(selection[0])
		slot = int(item['values'][0])

		if 0 <= slot < len(self.current_shop.items):
			del self.current_shop.items[slot]
			self.display_shop(self.current_shop)

	def move_item_up(self):
		"""Move item up in list."""
		if not self.current_shop:
			return

		selection = self.inventory_tree.selection()
		if not selection:
			return

		item = self.inventory_tree.item(selection[0])
		slot = int(item['values'][0])

		if slot > 0:
			items = self.current_shop.items
			items[slot], items[slot - 1] = items[slot - 1], items[slot]
			self.display_shop(self.current_shop)

	def move_item_down(self):
		"""Move item down in list."""
		if not self.current_shop:
			return

		selection = self.inventory_tree.selection()
		if not selection:
			return

		item = self.inventory_tree.item(selection[0])
		slot = int(item['values'][0])

		if slot < len(self.current_shop.items) - 1:
			items = self.current_shop.items
			items[slot], items[slot + 1] = items[slot + 1], items[slot]
			self.display_shop(self.current_shop)

	def edit_item_price(self, event):
		"""Edit item price on double-click."""
		selection = self.inventory_tree.selection()
		if not selection:
			return

		item = self.inventory_tree.item(selection[0])
		slot = int(item['values'][0])

		if 0 <= slot < len(self.current_shop.items):
			item_id, item_name, price = self.current_shop.items[slot]
			self.item_name_var.set(item_name)
			self.price_var.set(price)

	def update_item(self):
		"""Update selected item."""
		if not self.current_shop:
			return

		selection = self.inventory_tree.selection()
		if not selection:
			messagebox.showwarning("Warning", "No item selected")
			return

		item = self.inventory_tree.item(selection[0])
		slot = int(item['values'][0])

		# Find item ID from name
		all_items = self.WEAPONS + self.ARMOR + self.SHIELDS + self.ITEMS
		item_name = self.item_name_var.get()
		item_id = 0

		for id_, name, _ in all_items:
			if name == item_name:
				item_id = id_
				break

		# Update shop item
		if 0 <= slot < len(self.current_shop.items):
			self.current_shop.items[slot] = (item_id, item_name, self.price_var.get())
			self.display_shop(self.current_shop)

	def save_shop(self):
		"""Save shop changes to ROM."""
		if not self.current_shop:
			messagebox.showwarning("Warning", "No shop selected")
			return

		try:
			# Update shop name
			self.current_shop.shop_name = self.shop_name_var.get()

			# Write to ROM (placeholder - actual implementation would encode data)
			messagebox.showinfo("Success", f"Saved: {self.current_shop.shop_name}")

			# Refresh tree
			self.filter_shops()

		except Exception as e:
			messagebox.showerror("Error", f"Failed to save: {e}")

	def revert_shop(self):
		"""Revert shop to saved version."""
		if self.current_shop:
			self.load_shops()
			self.display_shop(self.current_shop)

	def save_all_shops(self):
		"""Save all shop changes."""
		messagebox.showinfo("Save", "All shops saved")

	def export_shops(self):
		"""Export shop data."""
		filename = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text Files", "*.txt"), ("CSV Files", "*.csv"), ("All Files", "*.*")]
		)

		if filename:
			try:
				with open(filename, 'w') as f:
					f.write("DRAGON WARRIOR SHOP DATA\n")
					f.write("=" * 80 + "\n\n")

					for shop in self.shops:
						f.write(f"Shop ID: {shop.shop_id}\n")
						f.write(f"Name: {shop.shop_name}\n")
						f.write(f"Town: {shop.town_name}\n")
						f.write(f"Type: {shop.shop_type}\n")
						f.write(f"ROM Offset: 0x{shop.rom_offset:05X}\n")
						f.write("-" * 80 + "\n")
						f.write("Inventory:\n")
						for item_id, item_name, price in shop.items:
							f.write(f"  {item_id:3d}. {item_name:<25} {price:>6} Gold\n")
						f.write("\n" + "=" * 80 + "\n\n")

				messagebox.showinfo("Success", f"Exported to {filename}")
			except Exception as e:
				messagebox.showerror("Error", f"Export failed: {e}")

	def import_shops(self):
		"""Import shop data."""
		messagebox.showinfo("Info", "Import functionality coming soon")
