#!/usr/bin/env python3
"""
Dragon Warrior Map Editor
Interactive editor for world map, town maps, and dungeon maps
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich import print as rprint
from PIL import Image, ImageDraw
import math

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'extraction'))
from data_structures import MapData, MapTile, TerrainType, Position

console = Console()

class MapEditor:
	"""Interactive map editor"""

	def __init__(self, data_file: str, output_dir: str = "assets/maps"):
		self.data_file = Path(data_file)
		self.output_dir = Path(output_dir)
		self.output_dir.mkdir(parents=True, exist_ok=True)
		self.maps: Dict[int, MapData] = {}
		self.current_map: Optional[MapData] = None
		self.load_data()

	def load_data(self):
		"""Load map data from JSON"""
		if self.data_file.exists():
			try:
				with open(self.data_file, 'r', encoding='utf-8') as f:
					data = json.load(f)

				for map_id_str, map_data in data.items():
					map_id = int(map_id_str)

					# Reconstruct tiles
					tiles = []
					for row_data in map_data['tiles']:
						row = []
						for tile_data in row_data:
							tile = MapTile(**tile_data)
							row.append(tile)
						tiles.append(row)

					map_obj = MapData(
						id=map_data['id'],
						name=map_data['name'],
						width=map_data['width'],
						height=map_data['height'],
						tiles=tiles,
						encounters=map_data['encounters'],
						music_id=map_data['music_id'],
						palette_id=map_data['palette_id']
					)

					self.maps[map_id] = map_obj

				console.print(f"[green]✅ Loaded {len(self.maps)} maps from {self.data_file}[/green]")
			except Exception as e:
				console.print(f"[red]❌ Error loading data: {e}[/red]")
				self.maps = {}
		else:
			console.print(f"[yellow]⚠️	Data file not found: {self.data_file}[/yellow]")

	def save_data(self):
		"""Save map data to JSON"""
		try:
			data = {str(k): v.to_dict() for k, v in self.maps.items()}
			with open(self.data_file, 'w', encoding='utf-8') as f:
				json.dump(data, f, indent=2, ensure_ascii=False)
			console.print(f"[green]✅ Saved to {self.data_file}[/green]")
		except Exception as e:
			console.print(f"[red]❌ Error saving: {e}[/red]")

	def display_maps(self):
		"""Display map list"""
		table = Table(title="Dragon Warrior Maps")
		table.add_column("ID", style="cyan", width=3)
		table.add_column("Name", style="bold blue", width=20)
		table.add_column("Size", style="yellow", width=10)
		table.add_column("Music", style="green", width=6)
		table.add_column("Palette", style="magenta", width=7)
		table.add_column("Encounters", style="red", width=10)

		for map_id, map_data in sorted(self.maps.items()):
			table.add_row(
				str(map_data.id),
				map_data.name,
				f"{map_data.width}x{map_data.height}",
				str(map_data.music_id),
				str(map_data.palette_id),
				str(len(map_data.encounters))
			)

		console.print(table)

	def select_map(self, map_id: int):
		"""Select a map for editing"""
		if map_id not in self.maps:
			console.print(f"[red]❌ Map {map_id} not found[/red]")
			return False

		self.current_map = self.maps[map_id]
		console.print(f"[green]✅ Selected map: {self.current_map.name}[/green]")
		return True

	def display_map_overview(self):
		"""Display current map overview"""
		if not self.current_map:
			console.print("[red]❌ No map selected[/red]")
			return

		map_data = self.current_map

		info = f"""[bold]{map_data.name}[/bold] (ID: {map_data.id})
[yellow]Dimensions:[/yellow] {map_data.width} x {map_data.height}
[green]Music ID:[/green] {map_data.music_id}
[magenta]Palette ID:[/magenta] {map_data.palette_id}
[red]Encounters:[/red] {len(map_data.encounters)} groups"""

		console.print(Panel(info, border_style="blue"))

		# Terrain type counts
		terrain_counts = {}
		for row in map_data.tiles:
			for tile in row:
				terrain_type = tile.terrain_type
				terrain_counts[terrain_type] = terrain_counts.get(terrain_type, 0) + 1

		terrain_table = Table(title="Terrain Distribution")
		terrain_table.add_column("Terrain", style="cyan")
		terrain_table.add_column("Count", style="yellow")
		terrain_table.add_column("Percentage", style="green")

		total_tiles = map_data.width * map_data.height
		for terrain_type, count in sorted(terrain_counts.items()):
			percentage = (count / total_tiles) * 100
			terrain_table.add_row(
				terrain_type.name,
				str(count),
				f"{percentage:.1f}%"
			)

		console.print(terrain_table)

	def display_map_ascii(self, start_x: int = 0, start_y: int = 0, width: int = 40, height: int = 20):
		"""Display ASCII representation of map section"""
		if not self.current_map:
			console.print("[red]❌ No map selected[/red]")
			return

		map_data = self.current_map

		# Terrain symbols
		terrain_symbols = {
			TerrainType.GRASS: ".",
			TerrainType.WATER: "~",
			TerrainType.MOUNTAIN: "^",
			TerrainType.FOREST: "T",
			TerrainType.SWAMP: "&",
			TerrainType.DESERT: ":",
			TerrainType.TOWN: "#",
			TerrainType.CASTLE: "@",
			TerrainType.CAVE: "C",
			TerrainType.SHRINE: "S"
		}

		console.print(f"\n[bold]Map: {map_data.name} - Section ({start_x},{start_y}) to ({start_x+width-1},{start_y+height-1})[/bold]")

		# Column headers
		header = "	 "
		for x in range(width):
			actual_x = start_x + x
			if actual_x < map_data.width:
				header += f"{actual_x%10}"
			else:
				header += " "
		console.print(f"[dim]{header}[/dim]")

		# Map rows
		for y in range(height):
			actual_y = start_y + y
			if actual_y >= map_data.height:
				break

			row_str = f"{actual_y:2d} "
			for x in range(width):
				actual_x = start_x + x
				if actual_x >= map_data.width or actual_y >= len(map_data.tiles) or actual_x >= len(map_data.tiles[actual_y]):
					row_str += " "
				else:
					tile = map_data.tiles[actual_y][actual_x]
					symbol = terrain_symbols.get(tile.terrain_type, "?")
					row_str += symbol

			console.print(row_str)

	def edit_tile(self, x: int, y: int):
		"""Edit a specific tile"""
		if not self.current_map:
			console.print("[red]❌ No map selected[/red]")
			return

		map_data = self.current_map

		if x < 0 or x >= map_data.width or y < 0 or y >= map_data.height:
			console.print(f"[red]❌ Invalid coordinates ({x}, {y})[/red]")
			return

		tile = map_data.tiles[y][x]

		console.print(f"\n[bold]Editing tile at ({x}, {y})[/bold]")
		console.print(f"Current: {tile.terrain_type.name} - Walkable: {tile.walkable} - Encounter Rate: {tile.encounter_rate}")

		# Show terrain options
		rprint("\n[bold]Terrain Types:[/bold]")
		for i, terrain in enumerate(TerrainType):
			rprint(f"{i}. {terrain.name}")

		terrain_choice = IntPrompt.ask("Select terrain type", choices=[str(i) for i in range(len(TerrainType))])
		new_terrain = list(TerrainType)[terrain_choice]

		# Set walkable based on terrain
		walkable_default = new_terrain not in [TerrainType.WATER, TerrainType.MOUNTAIN]
		new_walkable = Confirm.ask(f"Is tile walkable?", default=walkable_default)

		# Set encounter rate
		if new_terrain in [TerrainType.GRASS, TerrainType.FOREST, TerrainType.SWAMP]:
			new_encounter_rate = IntPrompt.ask("Encounter rate (0-255)", default=tile.encounter_rate)
		else:
			new_encounter_rate = 0

		# Update tile
		tile.terrain_type = new_terrain
		tile.walkable = new_walkable
		tile.encounter_rate = max(0, min(255, new_encounter_rate))

		console.print(f"[green]✅ Updated tile ({x}, {y})[/green]")

	def fill_area(self, x1: int, y1: int, x2: int, y2: int, terrain_type: TerrainType):
		"""Fill rectangular area with terrain type"""
		if not self.current_map:
			console.print("[red]❌ No map selected[/red]")
			return

		map_data = self.current_map

		# Ensure coordinates are in bounds and ordered
		x1, x2 = min(x1, x2), max(x1, x2)
		y1, y2 = min(y1, y2), max(y1, y2)
		x1 = max(0, x1)
		y1 = max(0, y1)
		x2 = min(map_data.width - 1, x2)
		y2 = min(map_data.height - 1, y2)

		walkable = terrain_type not in [TerrainType.WATER, TerrainType.MOUNTAIN]
		encounter_rate = 15 if terrain_type in [TerrainType.GRASS, TerrainType.FOREST] else 0

		tiles_changed = 0
		for y in range(y1, y2 + 1):
			for x in range(x1, x2 + 1):
				if y < len(map_data.tiles) and x < len(map_data.tiles[y]):
					tile = map_data.tiles[y][x]
					tile.terrain_type = terrain_type
					tile.walkable = walkable
					tile.encounter_rate = encounter_rate
					tiles_changed += 1

		console.print(f"[green]✅ Filled {tiles_changed} tiles with {terrain_type.name}[/green]")

	def create_new_map(self):
		"""Create a new map"""
		# Get next available ID
		max_id = max(self.maps.keys()) if self.maps else -1
		new_id = max_id + 1

		console.print(f"[cyan]Creating new map with ID {new_id}[/cyan]")

		name = Prompt.ask("Enter map name", default=f"NewMap_{new_id}")
		width = IntPrompt.ask("Enter map width", default=32)
		height = IntPrompt.ask("Enter map height", default=32)
		music_id = IntPrompt.ask("Enter music ID", default=0)
		palette_id = IntPrompt.ask("Enter palette ID", default=0)

		# Create empty map with grass
		tiles = []
		for y in range(height):
			row = []
			for x in range(width):
				tile = MapTile(
					tile_id=y * width + x,
					terrain_type=TerrainType.GRASS,
					walkable=True,
					encounter_rate=15
				)
				row.append(tile)
			tiles.append(row)

		new_map = MapData(
			id=new_id,
			name=name,
			width=width,
			height=height,
			tiles=tiles,
			encounters=[],
			music_id=music_id,
			palette_id=palette_id
		)

		self.maps[new_id] = new_map
		console.print(f"[green]✅ Created map {name} with ID {new_id}[/green]")

	def export_map_image(self):
		"""Export current map as PNG image"""
		if not self.current_map:
			console.print("[red]❌ No map selected[/red]")
			return

		map_data = self.current_map
		tile_size = 4
		img_width = map_data.width * tile_size
		img_height = map_data.height * tile_size

		img = Image.new('RGB', (img_width, img_height), (0, 0, 0))
		draw = ImageDraw.Draw(img)

		# Terrain colors
		terrain_colors = {
			TerrainType.GRASS: (34, 139, 34),
			TerrainType.WATER: (0, 100, 200),
			TerrainType.MOUNTAIN: (139, 69, 19),
			TerrainType.FOREST: (0, 100, 0),
			TerrainType.SWAMP: (85, 107, 47),
			TerrainType.DESERT: (238, 203, 173),
			TerrainType.TOWN: (160, 160, 160),
			TerrainType.CASTLE: (128, 128, 128),
			TerrainType.CAVE: (64, 64, 64),
			TerrainType.SHRINE: (255, 215, 0)
		}

		for y in range(map_data.height):
			for x in range(map_data.width):
				if y < len(map_data.tiles) and x < len(map_data.tiles[y]):
					tile = map_data.tiles[y][x]
					color = terrain_colors.get(tile.terrain_type, (0, 0, 0))

					x1 = x * tile_size
					y1 = y * tile_size
					x2 = x1 + tile_size
					y2 = y1 + tile_size

					draw.rectangle([x1, y1, x2, y2], fill=color)

		# Save image
		filename = f"map_{map_data.id:02d}_{map_data.name.lower().replace(' ', '_')}.png"
		img_path = self.output_dir / filename
		img.save(img_path)
		console.print(f"[green]✅ Exported map image: {img_path}[/green]")

	def run(self):
		"""Run the map editor"""
		console.print(Panel.fit(
			"🗺️ Dragon Warrior Map Editor",
			border_style="blue"
		))

		while True:
			current_info = f" - Current: {self.current_map.name}" if self.current_map else ""
			rprint(f"\n[bold blue]Main Menu{current_info}:[/bold blue]")
			rprint("1. List maps")
			rprint("2. Select map")
			rprint("3. View map overview")
			rprint("4. View map (ASCII)")
			rprint("5. Edit tile")
			rprint("6. Fill area")
			rprint("7. Create new map")
			rprint("8. Export map image")
			rprint("9. Save data")
			rprint("10. Reload data")
			rprint("0. Exit")

			choice = Prompt.ask("Select option", choices=["0","1","2","3","4","5","6","7","8","9","10"])

			if choice == "0":
				if Confirm.ask("Save before exit?"):
					self.save_data()
				break
			elif choice == "1":
				self.display_maps()
			elif choice == "2":
				map_id = IntPrompt.ask("Enter map ID")
				self.select_map(map_id)
			elif choice == "3":
				self.display_map_overview()
			elif choice == "4":
				start_x = IntPrompt.ask("Start X", default=0)
				start_y = IntPrompt.ask("Start Y", default=0)
				width = IntPrompt.ask("View width", default=40)
				height = IntPrompt.ask("View height", default=20)
				self.display_map_ascii(start_x, start_y, width, height)
			elif choice == "5":
				x = IntPrompt.ask("Tile X coordinate")
				y = IntPrompt.ask("Tile Y coordinate")
				self.edit_tile(x, y)
			elif choice == "6":
				x1 = IntPrompt.ask("Start X")
				y1 = IntPrompt.ask("Start Y")
				x2 = IntPrompt.ask("End X")
				y2 = IntPrompt.ask("End Y")
				rprint("\n[bold]Terrain Types:[/bold]")
				for i, terrain in enumerate(TerrainType):
					rprint(f"{i}. {terrain.name}")
				terrain_choice = IntPrompt.ask("Select terrain", choices=[str(i) for i in range(len(TerrainType))])
				terrain_type = list(TerrainType)[terrain_choice]
				self.fill_area(x1, y1, x2, y2, terrain_type)
			elif choice == "7":
				self.create_new_map()
			elif choice == "8":
				self.export_map_image()
			elif choice == "9":
				self.save_data()
			elif choice == "10":
				self.load_data()

@click.command()
@click.argument('data_file', type=click.Path())
@click.option('--output-dir', '-o', default='assets/maps', help='Output directory for images')
def edit_maps(data_file: str, output_dir: str):
	"""Dragon Warrior Map Editor"""
	editor = MapEditor(data_file, output_dir)
	editor.run()

if __name__ == "__main__":
	edit_maps()
