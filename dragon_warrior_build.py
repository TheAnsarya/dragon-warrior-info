#!/usr/bin/env python3
"""
Dragon Warrior Complete Build System Integration
Master build script that integrates asset extraction-editing-reinsertion with ROM assembly
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import click
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.table import Table
from rich import box

console = Console()

class DragonWarriorBuild:
	"""Complete Dragon Warrior build system"""

	def __init__(self, source_dir: str = "source_files", assets_dir: str = "extracted_assets",
				 build_dir: str = "build", output_dir: str = "output"):
		self.source_dir = Path(source_dir)
		self.assets_dir = Path(assets_dir)
		self.build_dir = Path(build_dir)
		self.output_dir = Path(output_dir)
		self.tools_dir = Path("tools")

		# Create directories
		self.assets_dir.mkdir(exist_ok=True)
		self.build_dir.mkdir(exist_ok=True)
		self.output_dir.mkdir(exist_ok=True)

	def show_banner(self):
		"""Show build system banner"""
		banner = Panel(
			"[bold cyan]Dragon Warrior Complete Build System[/bold cyan]\n\n"
			"[green]• Extract game assets to JSON/PNG files[/green]\n"
			"[blue]• Edit assets using visual/interactive editors[/blue]\n"
			"[yellow]• Generate assembly code for reinsertion[/yellow]\n"
			"[magenta]• Build final ROM with modified assets[/magenta]",
			title="Build System",
			border_style="green"
		)
		console.print(banner)

	def check_prerequisites(self) -> bool:
		"""Check that all required tools exist"""
		console.print("\n[cyan]Checking prerequisites...[/cyan]")

		required_files = [
			self.tools_dir / "asset_pipeline.py",
			self.tools_dir / "asset_reinserter.py",
			self.tools_dir / "extraction" / "data_extractor.py",
			self.tools_dir / "extraction" / "graphics_extractor.py"
		]

		missing_files = []
		for file_path in required_files:
			if not file_path.exists():
				missing_files.append(file_path)

		if missing_files:
			console.print("[red]❌ Missing required files:[/red]")
			for file_path in missing_files:
				console.print(f"	 {file_path}")
			return False

		console.print("[green]✅ All prerequisites found[/green]")
		return True

	def extract_assets(self) -> bool:
		"""Extract assets from ROM using asset pipeline

		Uses Dragon Warrior (U) (PRG1) [!].nes as the primary reference ROM.
		PRG1 is the preferred version for modding and asset extraction.
		"""
		console.print("\n[cyan]Extracting assets from ROM...[/cyan]")

		# Primary reference ROM: Dragon Warrior (U) (PRG1) [!].nes
		rom_file = Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes"

		if not rom_file.exists():
			console.print(f"[red]❌ ROM file not found: {rom_file}[/red]")
			console.print("[dim]Expected: Dragon Warrior (U) (PRG1) [!].nes in roms/ directory[/dim]")
			return False

		try:
			result = subprocess.run([
				sys.executable,
				str(self.tools_dir / "asset_pipeline.py"),
				str(rom_file),
				"--extract-only",
				"--output-dir",
				str(self.assets_dir)
			], capture_output=True, text=True, check=True)

			console.print("[green]✅ Asset extraction complete[/green]")
			return True

		except subprocess.CalledProcessError as e:
			console.print(f"[red]❌ Asset extraction failed: {e}[/red]")
			if e.stdout:
				console.print(f"[dim]stdout: {e.stdout}[/dim]")
			if e.stderr:
				console.print(f"[dim]stderr: {e.stderr}[/dim]")
			return False

	def show_asset_summary(self):
		"""Show summary of extracted assets"""
		json_dir = self.assets_dir / "json"
		graphics_dir = self.assets_dir / "graphics"

		if not json_dir.exists():
			console.print("[yellow]⚠️	No extracted assets found[/yellow]")
			return

		table = Table(title="📋 Extracted Assets Summary", box=box.ROUNDED)
		table.add_column("Asset Type", style="cyan")
		table.add_column("JSON File", style="green")
		table.add_column("Count", justify="right", style="yellow")
		table.add_column("Graphics", style="blue")

		# Check each asset type
		asset_types = [
			("Monsters", "monsters.json", "monster_*.png"),
			("Items", "items.json", "item_*.png"),
			("Spells", "spells.json", "spell_*.png"),
			("Shops", "shops.json", None),
			("Dialogs", "dialogs.json", None),
			("Maps", "maps.json", "map_*.png"),
			("Graphics", "graphics.json", "tile_*.png"),
			("Palettes", "palettes.json", "palette_*.png")
		]

		for asset_name, json_file, graphics_pattern in asset_types:
			json_path = json_dir / json_file

			if json_path.exists():
				try:
					with open(json_path, 'r', encoding='utf-8') as f:
						data = json.load(f)
					count = len(data)
					json_status = "✅"
				except:
					count = "?"
					json_status = "❌"
			else:
				count = "0"
				json_status = "❌"

			# Check graphics
			graphics_status = "N/A"
			if graphics_pattern and graphics_dir.exists():
				graphics_files = list(graphics_dir.glob(graphics_pattern))
				if graphics_files:
					graphics_status = f"✅ ({len(graphics_files)})"
				else:
					graphics_status = "❌"

			table.add_row(asset_name, json_status, str(count), graphics_status)

		console.print(table)

	def launch_editor_menu(self):
		"""Show editor selection menu"""
		console.print("\n[bold cyan]Asset Editors[/bold cyan]")

		editors = [
			("1", "Monster Editor", "monster"),
			("2", "Item Editor", "item"),
			("3", "Map Editor", "map"),
			("4", "Spell Editor", "spell"),
			("5", "Dialog Editor", "dialog"),
			("6", "Shop Editor", "shop"),
			("7", "Graphics Editor", "graphics"),
			("8", "Back to main menu", None)
		]

		for num, name, _ in editors:
			console.print(f"	{num}. {name}")

		while True:
			choice = click.prompt("\nSelect editor", type=str).strip()

			for num, name, editor_type in editors:
				if choice == num:
					if editor_type:
						self.launch_editor(editor_type)
					return

			console.print(f"[red]Invalid choice: {choice}[/red]")

	def launch_editor(self, editor_type: str):
		"""Launch specific editor"""
		console.print(f"\n[cyan]Launching {editor_type} editor...[/cyan]")

		try:
			subprocess.run([
				sys.executable,
				str(self.tools_dir / "asset_pipeline.py"),
				"edit",
				editor_type
			], check=False)
		except Exception as e:
			console.print(f"[red]❌ Failed to launch editor: {e}[/red]")

	def generate_assembly(self) -> bool:
		"""Generate assembly code for asset reinsertion"""
		console.print("\n[cyan]Generating assembly code for asset reinsertion...[/cyan]")

		try:
			result = subprocess.run([
				sys.executable,
				str(self.tools_dir / "asset_reinserter.py"),
				str(self.assets_dir),
				"--extract-defaults"
			], capture_output=True, text=True, check=True)

			console.print("[green]✅ Assembly generation complete[/green]")
			return True

		except subprocess.CalledProcessError as e:
			console.print(f"[red]❌ Assembly generation failed: {e}[/red]")
			if e.stdout:
				console.print(f"[dim]stdout: {e.stdout}[/dim]")
			if e.stderr:
				console.print(f"[dim]stderr: {e.stderr}[/dim]")
			return False

	def patch_source_files(self) -> bool:
		"""Patch source files to use asset includes"""
		console.print("\n[cyan]Patching source files to use asset includes...[/cyan]")

		try:
			result = subprocess.run([
				sys.executable,
				str(self.tools_dir / "source_patcher.py")
			], capture_output=True, text=True, check=True)

			console.print("[green]✅ Source file patching complete[/green]")
			return True

		except subprocess.CalledProcessError as e:
			console.print(f"[red]❌ Source patching failed: {e}[/red]")
			if e.stdout:
				console.print(f"[dim]stdout: {e.stdout}[/dim]")
			if e.stderr:
				console.print(f"[dim]stderr: {e.stderr}[/dim]")
			return False

	def restore_source_files(self) -> bool:
		"""Restore original source files"""
		console.print("\n[cyan]Restoring original source files...[/cyan]")

		try:
			result = subprocess.run([
				sys.executable,
				str(self.tools_dir / "source_patcher.py"),
				"--restore"
			], capture_output=True, text=True, check=True)

			console.print("[green]✅ Source files restored[/green]")
			return True

		except subprocess.CalledProcessError as e:
			console.print(f"[red]❌ Source restoration failed: {e}[/red]")
			if e.stdout:
				console.print(f"[dim]stdout: {e.stdout}[/dim]")
			if e.stderr:
				console.print(f"[dim]stderr: {e.stderr}[/dim]")
			return False

	def generate_patches(self) -> bool:
		"""Generate IPS and BPS patches if built ROM differs from reference"""
		console.print("\n[cyan]Checking for ROM differences and generating patches...[/cyan]")

		# Look for reference ROM
		reference_rom = None
		for rom_file in ["dragon_warrior.nes", "Dragon Warrior.nes", "dragon_warrior_original.nes"]:
			if Path(rom_file).exists():
				reference_rom = Path(rom_file)
				break

		if not reference_rom:
			console.print("[yellow]⚠️ No reference ROM found - skipping patch generation[/yellow]")
			return True

		built_rom = self.output_dir / "dragon_warrior_modified.nes"
		if not built_rom.exists():
			console.print("[yellow]⚠️ No built ROM found - skipping patch generation[/yellow]")
			return True

		try:
			result = subprocess.run([
				sys.executable,
				str(self.tools_dir / "patch_generator.py"),
				str(reference_rom),
				str(built_rom)
			], capture_output=True, text=True, check=True)

			console.print("[green]✅ Patch generation complete[/green]")
			return True

		except subprocess.CalledProcessError as e:
			console.print(f"[red]❌ Patch generation failed: {e}[/red]")
			if e.stdout:
				console.print(f"[dim]stdout: {e.stdout}[/dim]")
			if e.stderr:
				console.print(f"[dim]stderr: {e.stderr}[/dim]")
			return False

	def validate_assets(self) -> bool:
		"""Validate extracted assets"""
		console.print("\n[cyan]Validating extracted assets...[/cyan]")

		try:
			result = subprocess.run([
				sys.executable,
				str(self.tools_dir / "asset_validator.py"),
				str(self.assets_dir)
			], capture_output=True, text=True, check=True)

			console.print("[green]✅ Asset validation complete[/green]")
			return True

		except subprocess.CalledProcessError as e:
			console.print(f"[red]❌ Asset validation failed: {e}[/red]")
			if e.stdout:
				console.print(f"[dim]stdout: {e.stdout}[/dim]")
			if e.stderr:
				console.print(f"[dim]stderr: {e.stderr}[/dim]")
			return False

	def build_rom(self) -> bool:
		"""Build final ROM with asset reinsertion"""
		console.print("\n[cyan]Building ROM with modified assets...[/cyan]")

		# Check for assembler
		assembler_path = Path("Ophis") / "ophis.exe"
		if not assembler_path.exists():
			console.print(f"[red]❌ Assembler not found: {assembler_path}[/red]")
			console.print("[yellow]Please ensure Ophis assembler is available[/yellow]")
			return False

		# Create main assembly file that includes asset reinsertion
		main_asm = self.build_dir / "dragon_warrior_modified.asm"

		asm_content = f"""
; Dragon Warrior Modified ROM
; Includes asset reinsertion from extracted/edited data

; Include original source files
.include "{str(self.source_dir / 'Dragon_Warrior_Defines.asm')}"
.include "{str(self.source_dir / 'Header.asm')}"

; Include modified asset data (if generated)
.ifdef INCLUDE_ASSET_REINSERTION
.include "generated/asset_reinsertion.asm"
.endif

; Include remaining original banks
.include "{str(self.source_dir / 'Bank00.asm')}"
.include "{str(self.source_dir / 'Bank01.asm')}"
.include "{str(self.source_dir / 'Bank02.asm')}"
.include "{str(self.source_dir / 'Bank03.asm')}"
"""

		try:
			with open(main_asm, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			# Build ROM
			output_rom = self.output_dir / "dragon_warrior_modified.nes"

			# Ophis uses simple syntax: ophis infile outfile
			build_cmd = [
				str(assembler_path),
				str(main_asm),
				str(output_rom)
			]

			result = subprocess.run(build_cmd, capture_output=True, text=True, cwd=self.build_dir)

			if result.returncode == 0:
				console.print(f"[green]✅ ROM built successfully: {output_rom}[/green]")

				# Automatically generate timestamped patches
				self._generate_automatic_patches(output_rom)

				return True
			else:
				console.print("[red]❌ ROM build failed[/red]")
				if result.stdout:
					console.print(f"[dim]stdout: {result.stdout}[/dim]")
				if result.stderr:
					console.print(f"[dim]stderr: {result.stderr}[/dim]")
				return False

		except Exception as e:
			console.print(f"[red]❌ ROM build error: {e}[/red]")
			return False

	def _generate_automatic_patches(self, built_rom: Path) -> None:
		"""Automatically generate timestamped patches after ROM build

		Generates IPS and BPS patches comparing the built ROM against the
		primary reference ROM: Dragon Warrior (U) (PRG1) [!].nes
		"""
		try:
			# Primary reference ROM: Dragon Warrior (U) (PRG1) [!].nes
			reference_rom = Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes"

			# Fallback ROM files for compatibility
			if not reference_rom.exists():
				for rom_file in ["dragon_warrior.nes", "Dragon Warrior.nes", "dragon_warrior_original.nes"]:
					if Path(rom_file).exists():
						reference_rom = Path(rom_file)
						break
				else:
					reference_rom = None

			if not reference_rom:
				console.print("[dim]📝 No reference ROM found - skipping automatic patch generation[/dim]")
				return

			# Generate timestamp
			timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

			# Create patches directory if it doesn't exist
			patches_dir = Path("patches")
			patches_dir.mkdir(exist_ok=True)

			console.print("[dim]Generating automatic timestamped patches...[/dim]")

			# Call patch generator with timestamped output
			result = subprocess.run([
				sys.executable,
				str(self.tools_dir / "patch_generator.py"),
				str(reference_rom),
				str(built_rom),
				"--patches-dir", str(patches_dir),
				"--timestamp", timestamp
			], capture_output=True, text=True)

			if result.returncode == 0:
				console.print("[dim]✅ Automatic patches generated[/dim]")
			else:
				console.print(f"[dim]⚠️  Patch generation skipped: {result.stderr.strip() if result.stderr else 'No differences found'}[/dim]")

		except Exception as e:
			console.print(f"[dim]⚠️  Error generating automatic patches: {e}[/dim]")

	def verify_rom(self) -> bool:
		"""Verify built ROM against reference ROM with detailed analysis"""
		console.print("\n[cyan]Verifying built ROM against reference...[/cyan]")

		# Primary reference ROM: Dragon Warrior (U) (PRG1) [!].nes
		reference_rom = Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes"

		# Check for built ROM
		built_rom = self.output_dir / "dragon_warrior_modified.nes"
		if not built_rom.exists():
			console.print("[yellow]⚠️ No built ROM found - run build first[/yellow]")
			return False

		# Fallback ROM files for compatibility
		if not reference_rom.exists():
			for rom_file in ["dragon_warrior.nes", "Dragon Warrior.nes", "dragon_warrior_original.nes"]:
				if Path(rom_file).exists():
					reference_rom = Path(rom_file)
					break
			else:
				console.print("[red]❌ No reference ROM found[/red]")
				console.print("[dim]Expected: Dragon Warrior (U) (PRG1) [!].nes in roms/ directory[/dim]")
				return False

		try:
			result = subprocess.run([
				sys.executable,
				str(self.tools_dir / "rom_verifier.py"),
				str(reference_rom),
				str(built_rom),
				"--output-dir", "verification_reports"
			], capture_output=True, text=True)

			if result.returncode == 0:
				console.print("[green]✅ ROM verification complete - ROMs are identical[/green]")
				return True
			else:
				console.print("[yellow]⚠️ ROM verification complete - differences found[/yellow]")
				console.print("[dim]Check verification_reports/ for detailed analysis[/dim]")
				return True  # Still successful verification, just not identical

		except subprocess.CalledProcessError as e:
			console.print(f"[red]❌ ROM verification failed: {e}[/red]")
			if e.stdout:
				console.print(f"[dim]stdout: {e.stdout}[/dim]")
			if e.stderr:
				console.print(f"[dim]stderr: {e.stderr}[/dim]")
			return False
		except Exception as e:
			console.print(f"[red]❌ ROM verification error: {e}[/red]")
			return False

	def clean_build(self):
		"""Clean build artifacts"""
		console.print("\n[cyan]Cleaning build artifacts...[/cyan]")

		import shutil

		# Remove build directory contents
		if self.build_dir.exists():
			shutil.rmtree(self.build_dir)
			self.build_dir.mkdir()

		console.print("[green]✅ Build cleaned[/green]")

	def show_status(self):
		"""Show current build status"""
		console.print("\n[bold cyan]📊 Build Status[/bold cyan]")

		status_table = Table(box=box.SIMPLE)
		status_table.add_column("Component", style="cyan")
		status_table.add_column("Status", style="green")
		status_table.add_column("Path")

		# Check asset extraction
		extracted = (self.assets_dir / "json").exists()
		status_table.add_row("Assets Extracted", "✅" if extracted else "❌", str(self.assets_dir))

		# Check generated assembly
		generated = (self.build_dir / "generated").exists()
		status_table.add_row("Assembly Generated", "✅" if generated else "❌", str(self.build_dir / "generated"))

		# Check ROM output
		rom_built = (self.output_dir / "dragon_warrior_modified.nes").exists()
		status_table.add_row("ROM Built", "✅" if rom_built else "❌", str(self.output_dir))

		console.print(status_table)

		# Show extracted asset summary if available
		if extracted:
			self.show_asset_summary()

	def run_interactive_menu(self):
		"""Run the interactive build menu"""

		while True:
			console.print("\n[bold green]Dragon Warrior Build System[/bold green]")
			console.print("1. Extract assets from ROM")
			console.print("2. Launch asset editors")
			console.print("3. Generate assembly code & extract defaults")
			console.print("4. Patch source files for asset includes")
			console.print("5. Restore original source files")
			console.print("6. Build modified ROM")
			console.print("7. Generate patches (IPS/BPS)")
			console.print("8. Verify ROM against reference")
			console.print("9. Show build status")
			console.print("10. Clean build")
			console.print("11. Full build pipeline")
			console.print("12. Exit")

			choice = click.prompt("\nSelect option", type=str).strip()

			# Extract just the number if user typed extra text
			import re
			number_match = re.match(r'^(\d+)', choice)
			if number_match:
				choice = number_match.group(1)

			if choice == "1":
				self.extract_assets()

			elif choice == "2":
				self.launch_editor_menu()

			elif choice == "3":
				self.generate_assembly()

			elif choice == "4":
				self.patch_source_files()

			elif choice == "5":
				self.restore_source_files()

			elif choice == "6":
				self.build_rom()

			elif choice == "7":
				self.generate_patches()

			elif choice == "8":
				self.verify_rom()

			elif choice == "9":
				self.show_status()

			elif choice == "10":
				self.clean_build()

			elif choice == "11":
				# Full pipeline
				console.print("\n[bold cyan]Running full build pipeline...[/bold cyan]")
				if (self.extract_assets() and
					self.generate_assembly() and
					self.patch_source_files() and
					self.build_rom()):

					# Generate patches
					self.generate_patches()

					# Verify ROM
					console.print("\n[cyan]Verifying built ROM...[/cyan]")
					self.verify_rom()  # Non-blocking verification

					console.print("\n[bold green]✅ Full build pipeline completed successfully![/bold green]")
				else:
					console.print("\n[bold red]❌ Build pipeline failed at some stage[/bold red]")

			elif choice == "12":
				console.print("\n[bold cyan]Thanks for using Dragon Warrior Build System![/bold cyan]")
				break

			else:
				console.print(f"[red]Invalid choice: {choice}[/red]")
				console.print(f"[red]Invalid choice: {choice}[/red]")

@click.command()
@click.option('--source-dir', '-s', default='source_files', help='Source assembly files directory')
@click.option('--assets-dir', '-a', default='extracted_assets', help='Extracted assets directory')
@click.option('--build-dir', '-b', default='build', help='Build directory')
@click.option('--output-dir', '-o', default='output', help='Output ROM directory')
@click.option('--interactive/--no-interactive', default=True, help='Run interactive menu')
def build_system(source_dir: str, assets_dir: str, build_dir: str, output_dir: str, interactive: bool):
	"""Dragon Warrior complete build system with asset editing"""

	builder = DragonWarriorBuild(source_dir, assets_dir, build_dir, output_dir)
	builder.show_banner()

	if not builder.check_prerequisites():
		console.print("\n[red]❌ Prerequisites check failed. Please ensure all tools are available.[/red]")
		sys.exit(1)

	if interactive:
		builder.run_interactive_menu()
	else:
		# Non-interactive mode - run full pipeline
		if (builder.extract_assets() and
			builder.generate_assembly() and
			builder.patch_source_files() and
			builder.build_rom() and
			builder.generate_patches()):
			console.print("\n[bold green]✅ Build completed successfully![/bold green]")
		else:
			console.print("\n[bold red]❌ Build failed[/bold red]")
			sys.exit(1)

if __name__ == "__main__":
	build_system()
