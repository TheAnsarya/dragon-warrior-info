#!/usr/bin/env python3
"""
Dragon Warrior Complete Asset Pipeline
Unified tool for extraction, editing, and reinsersion of all game assets
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any
import json
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich import print as rprint

# Add extraction directory to path
sys.path.append(str(Path(__file__).parent / 'extraction'))
from data_structures import GameData

console = Console()

class AssetPipeline:
	"""Complete asset extraction, editing, and reinsertion pipeline"""

	def __init__(self, rom_path: str, output_dir: str = "assets"):
		self.rom_path = Path(rom_path)
		self.output_dir = Path(output_dir)
		self.output_dir.mkdir(parents=True, exist_ok=True)

		# Asset directories
		self.json_dir = self.output_dir / "json"
		self.graphics_dir = self.output_dir / "graphics"
		self.maps_dir = self.output_dir / "maps"
		self.palettes_dir = self.output_dir / "palettes"
		self.asm_dir = self.output_dir / "assembly"

		# Create all directories
		for dir_path in [self.json_dir, self.graphics_dir, self.maps_dir, self.palettes_dir, self.asm_dir]:
			dir_path.mkdir(parents=True, exist_ok=True)

	def extract_all_assets(self):
		"""Extract all assets from ROM"""
		console.print("[bold blue]🎯 Dragon Warrior Asset Extraction Pipeline[/bold blue]\n")

		with Progress(
			SpinnerColumn(),
			TextColumn("[progress.description]{task.description}"),
			console=console
		) as progress:

			# Extract graphics and palettes
			task = progress.add_task("Extracting graphics and palettes...", total=None)
			self._run_graphics_extractor()
			progress.update(task, completed=True)

			# Extract game data
			task = progress.add_task("Extracting game data...", total=None)
			self._run_data_extractor()
			progress.update(task, completed=True)

			# Merge data files
			task = progress.add_task("Merging data files...", total=None)
			self._merge_data_files()
			progress.update(task, completed=True)

		console.print("\n[green]✅ Asset extraction complete![/green]")
		self._display_extraction_summary()

	def _run_graphics_extractor(self):
		"""Run the graphics extractor"""
		extractor_path = Path(__file__).parent / "extraction" / "graphics_extractor.py"

		if extractor_path.exists():
			try:
				result = subprocess.run([
					sys.executable, str(extractor_path),
					str(self.rom_path),
					"--output-dir", str(self.output_dir)
				], capture_output=True, text=True, check=True)

			except subprocess.CalledProcessError as e:
				console.print(f"[red]Graphics extraction failed: {e.stderr}[/red]")
		else:
			console.print(f"[yellow]Graphics extractor not found: {extractor_path}[/yellow]")

	def _run_data_extractor(self):
		"""Run the data extractor"""
		extractor_path = Path(__file__).parent / "extraction" / "data_extractor.py"

		if extractor_path.exists():
			try:
				result = subprocess.run([
					sys.executable, str(extractor_path),
					str(self.rom_path),
					"--output-dir", str(self.output_dir)
				], capture_output=True, text=True, check=True)

			except subprocess.CalledProcessError as e:
				console.print(f"[red]Data extraction failed: {e.stderr}[/red]")
		else:
			console.print(f"[yellow]Data extractor not found: {extractor_path}[/yellow]")

	def _merge_data_files(self):
		"""Merge all extracted data into complete game data"""
		try:
			# Load individual data files
			graphics_file = self.json_dir / "graphics_data.json"
			complete_file = self.json_dir / "complete_game_data.json"

			graphics_data = {}
			complete_data = {}

			if graphics_file.exists():
				with open(graphics_file, 'r', encoding='utf-8') as f:
					graphics_data = json.load(f)

			if complete_file.exists():
				with open(complete_file, 'r', encoding='utf-8') as f:
					complete_data = json.load(f)

			# Merge data
			merged_data = {**complete_data, **graphics_data}

			# Save merged data
			merged_file = self.json_dir / "merged_game_data.json"
			with open(merged_file, 'w', encoding='utf-8') as f:
				json.dump(merged_data, f, indent=2, ensure_ascii=False)

		except Exception as e:
			console.print(f"[yellow]Warning: Could not merge data files: {e}[/yellow]")

	def _display_extraction_summary(self):
		"""Display summary of extracted assets"""
		table = Table(title="Extracted Assets Summary")
		table.add_column("Asset Type", style="cyan")
		table.add_column("Count", style="yellow")
		table.add_column("Location", style="green")

		# Count files in each directory
		graphics_count = len(list(self.graphics_dir.glob("*.png"))) if self.graphics_dir.exists() else 0
		palette_count = len(list(self.palettes_dir.glob("*.png"))) if self.palettes_dir.exists() else 0
		map_count = len(list(self.maps_dir.glob("*.png"))) if self.maps_dir.exists() else 0
		json_count = len(list(self.json_dir.glob("*.json"))) if self.json_dir.exists() else 0

		table.add_row("Graphics (PNG)", str(graphics_count), str(self.graphics_dir))
		table.add_row("Palettes (PNG)", str(palette_count), str(self.palettes_dir))
		table.add_row("Maps (PNG)", str(map_count), str(self.maps_dir))
		table.add_row("Data Files (JSON)", str(json_count), str(self.json_dir))

		console.print(table)

	def launch_editor(self, editor_type: str):
		"""Launch a specific editor"""
		editors = {
			"monster": "editors/monster_editor.py",
			"item": "editors/item_editor.py",
			"map": "editors/map_editor.py",
			"spell": "editors/spell_editor.py",
			"dialog": "editors/dialog_editor.py",
			"shop": "editors/shop_editor.py"
		}

		if editor_type not in editors:
			console.print(f"[red]Unknown editor: {editor_type}[/red]")
			return

		editor_path = Path(__file__).parent / editors[editor_type]

		if not editor_path.exists():
			console.print(f"[red]Editor not found: {editor_path}[/red]")
			return

		# Determine data file based on editor type
		data_files = {
			"monster": self.json_dir / "monsters.json",
			"item": self.json_dir / "items.json",
			"map": self.json_dir / "maps.json",
			"spell": self.json_dir / "spells.json",
			"dialog": self.json_dir / "dialogs.json",
			"shop": self.json_dir / "shops.json"
		}

		data_file = data_files[editor_type]

		if not data_file.exists():
			console.print(f"[red]Data file not found: {data_file}[/red]")
			console.print("[yellow]Run extraction first![/yellow]")
			return

		console.print(f"[cyan]Launching {editor_type} editor...[/cyan]")

		try:
			# Launch editor in new process
			subprocess.run([
				sys.executable, str(editor_path), str(data_file)
			], check=False)
		except Exception as e:
			console.print(f"[red]Error launching editor: {e}[/red]")

	def generate_assembly_code(self):
		"""Generate assembly insertion code from extracted data"""
		console.print("[blue]🔧 Generating assembly insertion code...[/blue]")

		# Load merged game data
		merged_file = self.json_dir / "merged_game_data.json"
		if not merged_file.exists():
			console.print("[red]Merged game data not found. Run extraction first.[/red]")
			return

		with open(merged_file, 'r', encoding='utf-8') as f:
			game_data = json.load(f)

		# Generate assembly files
		asm_files = []

		# Monster data assembly
		if 'monsters' in game_data:
			monster_asm = self._generate_monster_assembly(game_data['monsters'])
			monster_file = self.asm_dir / "monster_data.asm"
			with open(monster_file, 'w', encoding='utf-8') as f:
				f.write(monster_asm)
			asm_files.append(monster_file)

		# Item data assembly
		if 'items' in game_data:
			item_asm = self._generate_item_assembly(game_data['items'])
			item_file = self.asm_dir / "item_data.asm"
			with open(item_file, 'w', encoding='utf-8') as f:
				f.write(item_asm)
			asm_files.append(item_file)

		# Shop data assembly
		if 'shops' in game_data:
			shop_asm = self._generate_shop_assembly(game_data['shops'])
			shop_file = self.asm_dir / "shop_data.asm"
			with open(shop_file, 'w', encoding='utf-8') as f:
				f.write(shop_asm)
			asm_files.append(shop_file)

		console.print(f"[green]✅ Generated {len(asm_files)} assembly files:[/green]")
		for asm_file in asm_files:
			console.print(f"	 📄 {asm_file}")

	def _generate_monster_assembly(self, monsters: Dict[str, Any]) -> str:
		"""Generate monster data assembly"""
		asm_lines = [
			"; Dragon Warrior Monster Data",
			"; Generated by Asset Pipeline",
			"",
			".segment \"MonsterData\"",
			"",
			"MonsterStats:"
		]

		for monster_id, monster in sorted(monsters.items()):
			asm_lines.extend([
				f"Monster_{monster_id:02d}:",
				f"	.word {monster['hp']}		 ; HP",
				f"	.byte {monster['strength']}	 ; Strength",
				f"	.byte {monster['agility']}	; Agility",
				f"	.byte {monster['max_damage']} ; Max Damage",
				f"	.byte {monster['dodge_rate']} ; Dodge Rate",
				f"	.byte {monster['sleep_resistance']} ; Sleep Resistance",
				f"	.byte {monster['hurt_resistance']}	; Hurt Resistance",
				f"	.word {monster['experience']} ; Experience",
				f"	.word {monster['gold']}		 ; Gold",
				f"	.byte {monster['monster_type']} ; Monster Type",
				f"	.byte {monster['sprite_id']}	; Sprite ID",
				""
			])

		return "\n".join(asm_lines)

	def _generate_item_assembly(self, items: Dict[str, Any]) -> str:
		"""Generate item data assembly"""
		asm_lines = [
			"; Dragon Warrior Item Data",
			"; Generated by Asset Pipeline",
			"",
			".segment \"ItemData\"",
			"",
			"ItemStats:"
		]

		for item_id, item in sorted(items.items()):
			asm_lines.extend([
				f"Item_{item_id:02d}:",
				f"	.byte {item['attack_bonus']}	; Attack Bonus",
				f"	.byte {item['defense_bonus']} ; Defense Bonus",
				f"	.word {item['buy_price']}	 ; Buy Price",
				f"	.word {item['sell_price']}	; Sell Price",
				f"	.byte {int(item['equippable']) | (int(item['useable']) << 1)} ; Flags",
				f"	.byte {item['item_type']}	 ; Item Type",
				f"	.byte {item['sprite_id']}	 ; Sprite ID",
				""
			])

		return "\n".join(asm_lines)

	def _generate_shop_assembly(self, shops: Dict[str, Any]) -> str:
		"""Generate shop data assembly"""
		asm_lines = [
			"; Dragon Warrior Shop Data",
			"; Generated by Asset Pipeline",
			"",
			".segment \"ShopData\"",
			"",
			"ShopInventories:"
		]

		for shop_id, shop in sorted(shops.items()):
			asm_lines.extend([
				f"Shop_{shop_id:02d}:",
				f"	.byte {len(shop['items'])} ; Item count",
			])

			# Add item IDs
			if shop['items']:
				item_list = ", ".join(str(item_id) for item_id in shop['items'])
				asm_lines.append(f"	.byte {item_list}")

			# Inn price if applicable
			if shop.get('inn_price'):
				asm_lines.append(f"	.word {shop['inn_price']} ; Inn price")

			asm_lines.append("")

		return "\n".join(asm_lines)

	def run_pipeline(self):
		"""Run the complete asset pipeline"""
		console.print(Panel.fit(
			"🎮 Dragon Warrior Complete Asset Pipeline",
			border_style="blue"
		))

		while True:
			rprint("\n[bold blue]Asset Pipeline Menu:[/bold blue]")
			rprint("1. Extract all assets from ROM")
			rprint("2. Launch Monster Editor")
			rprint("3. Launch Item Editor")
			rprint("4. Launch Map Editor")
			rprint("5. Launch Spell Editor")
			rprint("6. Launch Dialog Editor")
			rprint("7. Launch Shop Editor")
			rprint("8. Generate Assembly Code")
			rprint("9. View Asset Summary")
			rprint("0. Exit")

			choice = click.prompt("Select option", type=click.Choice(["0","1","2","3","4","5","6","7","8","9"]))

			if choice == "0":
				break
			elif choice == "1":
				self.extract_all_assets()
			elif choice == "2":
				self.launch_editor("monster")
			elif choice == "3":
				self.launch_editor("item")
			elif choice == "4":
				self.launch_editor("map")
			elif choice == "5":
				self.launch_editor("spell")
			elif choice == "6":
				self.launch_editor("dialog")
			elif choice == "7":
				self.launch_editor("shop")
			elif choice == "8":
				self.generate_assembly_code()
			elif choice == "9":
				self._display_extraction_summary()

@click.command()
@click.argument('rom_path', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='assets', help='Output directory')
@click.option('--extract-only', is_flag=True, help='Extract assets only, no menu')
def asset_pipeline(rom_path: str, output_dir: str, extract_only: bool):
	"""Dragon Warrior Complete Asset Pipeline"""

	pipeline = AssetPipeline(rom_path, output_dir)

	if extract_only:
		pipeline.extract_all_assets()
	else:
		pipeline.run_pipeline()

if __name__ == "__main__":
	asset_pipeline()
