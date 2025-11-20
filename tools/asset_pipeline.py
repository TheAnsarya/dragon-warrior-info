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
		# Validate ROM file exists and is readable
		self.rom_path = Path(rom_path)
		if not self.rom_path.exists():
			raise FileNotFoundError(f"ROM file not found: {rom_path}")

		if not self.rom_path.is_file():
			raise ValueError(f"ROM path is not a file: {rom_path}")

		# Validate ROM file size (Dragon Warrior should be around 256KB)
		rom_size = self.rom_path.stat().st_size
		if rom_size < 100_000:
			console.print(f"[yellow]Warning: ROM file seems too small ({rom_size} bytes)[/yellow]")
		elif rom_size > 1_000_000:
			console.print(f"[yellow]Warning: ROM file seems too large ({rom_size} bytes)[/yellow]")

		try:
			# Test ROM file readability
			with open(self.rom_path, 'rb') as f:
				header = f.read(16)
				if len(header) >= 4 and header[:4] == b'NES\x1a':
					console.print(f"[green]Valid NES ROM detected: {self.rom_path.name}[/green]")
				else:
					console.print(f"[yellow]Warning: ROM doesn't appear to be iNES format[/yellow]")
		except PermissionError:
			raise PermissionError(f"Cannot read ROM file (permission denied): {rom_path}")
		except Exception as e:
			raise IOError(f"Error reading ROM file: {e}")

		# Setup output directory with error handling
		try:
			self.output_dir = Path(output_dir)
			self.output_dir.mkdir(parents=True, exist_ok=True)
		except PermissionError:
			raise PermissionError(f"Cannot create output directory (permission denied): {output_dir}")
		except Exception as e:
			raise IOError(f"Error creating output directory: {e}")

		# Asset directories
		self.json_dir = self.output_dir / "json"
		self.graphics_dir = self.output_dir / "graphics"
		self.maps_dir = self.output_dir / "maps"
		self.palettes_dir = self.output_dir / "palettes"
		self.asm_dir = self.output_dir / "assembly"

		# Create all directories with error handling
		for dir_path in [self.json_dir, self.graphics_dir, self.maps_dir, self.palettes_dir, self.asm_dir]:
			try:
				dir_path.mkdir(parents=True, exist_ok=True)
			except Exception as e:
				raise IOError(f"Error creating directory {dir_path}: {e}")

	def extract_all_assets(self):
		"""Extract all assets from ROM"""
		console.print("[bold blue]Dragon Warrior Asset Extraction Pipeline[/bold blue]\n")

		try:
			# Extract graphics and palettes
			console.print("[cyan]Extracting graphics and palettes...[/cyan]")
			try:
				self._run_graphics_extractor()
				console.print("[green]Graphics extraction completed[/green]")
			except Exception as e:
				console.print(f"[red]Graphics extraction failed: {e}[/red]")
				return False

			# Extract game data
			console.print("[cyan]Extracting game data...[/cyan]")
			try:
				self._run_data_extractor()
				console.print("[green]Data extraction completed[/green]")
			except Exception as e:
				console.print(f"[red]Data extraction failed: {e}[/red]")
				return False

			# Merge data files
			console.print("[cyan]Merging data files...[/cyan]")
			try:
				self._merge_data_files()
				console.print("[green]Data merging completed[/green]")
			except Exception as e:
				console.print(f"[red]Data merging failed: {e}[/red]")
				return False

			console.print("\n[green]Asset extraction complete![/green]")
			self._display_extraction_summary()

		except KeyboardInterrupt:
			console.print("\n[yellow]Extraction cancelled by user[/yellow]")
			return False
		except Exception as e:
			console.print(f"\n[red]Critical error during extraction: {e}[/red]")
			return False

		return True

	def _run_graphics_extractor(self):
		"""Run the graphics extractor"""
		extractor_path = Path(__file__).parent / "extraction" / "graphics_extractor.py"

		if not extractor_path.exists():
			raise FileNotFoundError(f"Graphics extractor not found: {extractor_path}")

		try:
			result = subprocess.run([
				sys.executable, str(extractor_path),
				str(self.rom_path),
				"--output-dir", str(self.output_dir)
			], capture_output=True, text=True, check=True, timeout=300)  # 5 minute timeout

			if result.stdout:
				console.print(f"[dim]Graphics extractor output: {result.stdout.strip()}[/dim]")

		except subprocess.TimeoutExpired:
			raise RuntimeError("Graphics extraction timed out (exceeded 5 minutes)")
		except subprocess.CalledProcessError as e:
			error_msg = f"Graphics extraction failed (exit code {e.returncode})"
			if e.stderr:
				error_msg += f": {e.stderr.strip()}"
			raise RuntimeError(error_msg)
		except Exception as e:
			raise RuntimeError(f"Unexpected error running graphics extractor: {e}")

	def _run_data_extractor(self):
		"""Run the data extractor"""
		extractor_path = Path(__file__).parent / "extraction" / "data_extractor.py"

		if not extractor_path.exists():
			raise FileNotFoundError(f"Data extractor not found: {extractor_path}")

		try:
			result = subprocess.run([
				sys.executable, str(extractor_path),
				str(self.rom_path),
				"--output-dir", str(self.output_dir)
			], capture_output=True, text=True, check=True, timeout=300)  # 5 minute timeout

			if result.stdout:
				console.print(f"[dim]Data extractor output: {result.stdout.strip()}[/dim]")

		except subprocess.TimeoutExpired:
			raise RuntimeError("Data extraction timed out (exceeded 5 minutes)")
		except subprocess.CalledProcessError as e:
			error_msg = f"Data extraction failed (exit code {e.returncode})"
			if e.stderr:
				error_msg += f": {e.stderr.strip()}"
			raise RuntimeError(error_msg)
		except Exception as e:
			raise RuntimeError(f"Unexpected error running data extractor: {e}")

	def _merge_data_files(self):
		"""Merge all extracted data into complete game data"""
		try:
			# Load individual data files with validation
			graphics_file = self.json_dir / "graphics_data.json"
			complete_file = self.json_dir / "complete_game_data.json"

			graphics_data = {}
			complete_data = {}

			# Load graphics data if available
			if graphics_file.exists():
				try:
					with open(graphics_file, 'r', encoding='utf-8') as f:
						graphics_data = json.load(f)
				except json.JSONDecodeError as e:
					raise ValueError(f"Invalid JSON in graphics data file: {e}")
				except Exception as e:
					raise IOError(f"Error reading graphics data file: {e}")

			# Load complete data if available
			if complete_file.exists():
				try:
					with open(complete_file, 'r', encoding='utf-8') as f:
						complete_data = json.load(f)
				except json.JSONDecodeError as e:
					raise ValueError(f"Invalid JSON in complete data file: {e}")
				except Exception as e:
					raise IOError(f"Error reading complete data file: {e}")

			# Validate data structure
			if not isinstance(graphics_data, dict):
				raise ValueError("Graphics data must be a dictionary")
			if not isinstance(complete_data, dict):
				raise ValueError("Complete data must be a dictionary")

			# Merge data (complete_data takes precedence)
			merged_data = {**graphics_data, **complete_data}

			# Save merged data with atomic write
			merged_file = self.json_dir / "merged_game_data.json"
			temp_file = merged_file.with_suffix('.tmp')

			try:
				with open(temp_file, 'w', encoding='utf-8') as f:
					json.dump(merged_data, f, indent=2, ensure_ascii=False)

				# Atomic rename to final location
				temp_file.replace(merged_file)
				console.print(f"[dim]Merged {len(merged_data)} data sections[/dim]")

			except Exception as e:
				# Clean up temp file if it exists
				if temp_file.exists():
					temp_file.unlink()
				raise IOError(f"Error writing merged data file: {e}")

		except Exception as e:
			raise RuntimeError(f"Error merging data files: {e}")

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
			"shop": "editors/shop_editor.py",
			"graphics": "editors/graphics_editor.py"
		}

		if editor_type not in editors:
			console.print(f"[red]Unknown editor: {editor_type}[/red]")
			console.print(f"[dim]Available editors: {', '.join(editors.keys())}[/dim]")
			return False

		editor_path = Path(__file__).parent / editors[editor_type]

		if not editor_path.exists():
			console.print(f"[red]Editor not found: {editor_path}[/red]")
			return False

		# Determine data file based on editor type
		data_files = {
			"monster": self.json_dir / "monsters.json",
			"item": self.json_dir / "items.json",
			"map": self.json_dir / "maps.json",
			"spell": self.json_dir / "spells.json",
			"dialog": self.json_dir / "dialogs.json",
			"shop": self.json_dir / "shops.json",
			"graphics": self.json_dir / "graphics.json"
		}

		data_file = data_files.get(editor_type)

		if data_file and not data_file.exists():
			console.print(f"[red]Data file not found: {data_file}[/red]")
			console.print("[yellow]💡 Run extraction first to generate data files![/yellow]")
			return False

		console.print(f"[cyan]Launching {editor_type} editor...[/cyan]")

		try:
			# Launch editor in new process
			args = [sys.executable, str(editor_path)]
			if data_file:
				args.append(str(data_file))

			result = subprocess.run(args, check=False)

			if result.returncode != 0:
				console.print(f"[yellow]Editor exited with code {result.returncode}[/yellow]")
			return result.returncode == 0

		except FileNotFoundError:
			console.print(f"[red]Python interpreter not found: {sys.executable}[/red]")
			return False
		except Exception as e:
			console.print(f"[red]Error launching editor: {e}[/red]")
			return False

	def generate_assembly_code(self):
		"""Generate assembly insertion code from extracted data"""
		console.print("[blue]Generating assembly insertion code...[/blue]")

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

		console.print(f"[green]Generated {len(asm_files)} assembly files:[/green]")
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
@click.option('--output-dir', '-o', default='extracted_assets', help='Output directory')
@click.option('--extract-only', is_flag=True, help='Extract assets only, no menu')
def asset_pipeline(rom_path: str, output_dir: str, extract_only: bool):
	"""Dragon Warrior Complete Asset Pipeline"""
	try:
		pipeline = AssetPipeline(rom_path, output_dir)

		if extract_only:
			success = pipeline.extract_all_assets()
			if not success:
				console.print("[red]Extraction failed[/red]")
				sys.exit(1)
		else:
			pipeline.run_pipeline()

	except KeyboardInterrupt:
		console.print("\n[yellow]Operation cancelled by user[/yellow]")
		sys.exit(130)
	except (FileNotFoundError, ValueError, PermissionError, IOError) as e:
		console.print(f"[red]{e}[/red]")
		sys.exit(1)
	except Exception as e:
		console.print(f"[red]Unexpected error: {e}[/red]")
		sys.exit(1)

if __name__ == "__main__":
	asset_pipeline()
