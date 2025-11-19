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
            "[bold cyan]🐉 Dragon Warrior Complete Build System[/bold cyan]\n\n"
            "[green]• Extract game assets to JSON/PNG files[/green]\n"
            "[blue]• Edit assets using visual/interactive editors[/blue]\n"
            "[yellow]• Generate assembly code for reinsertion[/yellow]\n"
            "[magenta]• Build final ROM with modified assets[/magenta]",
            title="🏗️ Build System",
            border_style="green"
        )
        console.print(banner)

    def check_prerequisites(self) -> bool:
        """Check that all required tools exist"""
        console.print("\n[cyan]🔍 Checking prerequisites...[/cyan]")

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
                console.print(f"   {file_path}")
            return False

        console.print("[green]✅ All prerequisites found[/green]")
        return True

    def extract_assets(self) -> bool:
        """Extract assets from ROM using asset pipeline"""
        console.print("\n[cyan]📦 Extracting assets from ROM...[/cyan]")

        try:
            result = subprocess.run([
                sys.executable,
                str(self.tools_dir / "asset_pipeline.py"),
                "extract",
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
            console.print("[yellow]⚠️  No extracted assets found[/yellow]")
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
        console.print("\n[bold cyan]🎨 Asset Editors[/bold cyan]")

        editors = [
            ("1", "🐲 Monster Editor", "monster"),
            ("2", "⚔️ Item Editor", "item"),
            ("3", "🗺️ Map Editor", "map"),
            ("4", "🪄 Spell Editor", "spell"),
            ("5", "💬 Dialog Editor", "dialog"),
            ("6", "🏪 Shop Editor", "shop"),
            ("7", "🎨 Graphics Editor", "graphics"),
            ("8", "🔙 Back to main menu", None)
        ]

        for num, name, _ in editors:
            console.print(f"  {num}. {name}")

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
        console.print(f"\n[cyan]🚀 Launching {editor_type} editor...[/cyan]")

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
        console.print("\n[cyan]🔧 Generating assembly code for asset reinsertion...[/cyan]")

        try:
            result = subprocess.run([
                sys.executable,
                str(self.tools_dir / "asset_reinserter.py"),
                str(self.assets_dir),
                "--output-dir", str(self.build_dir / "generated")
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

    def build_rom(self) -> bool:
        """Build final ROM with asset reinsertion"""
        console.print("\n[cyan]🏗️ Building ROM with modified assets...[/cyan]")

        # Check for assembler
        assembler_path = Path("Ophis") / "bin" / "ophis.exe"
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
.include "{self.source_dir / 'Dragon_Warrior_Defines.asm'}"
.include "{self.source_dir / 'Header.asm'}"

; Include modified asset data (if generated)
.ifdef INCLUDE_ASSET_REINSERTION
.include "generated/asset_reinsertion.asm"
.endif

; Include remaining original banks
.include "{self.source_dir / 'Bank00.asm'}"
.include "{self.source_dir / 'Bank01.asm'}"
.include "{self.source_dir / 'Bank02.asm'}"
.include "{self.source_dir / 'Bank03.asm'}"
"""

        try:
            with open(main_asm, 'w', encoding='utf-8') as f:
                f.write(asm_content)

            # Build ROM
            output_rom = self.output_dir / "dragon_warrior_modified.nes"

            build_cmd = [
                str(assembler_path),
                str(main_asm),
                "-o", str(output_rom)
            ]

            # Include asset reinsertion if generated files exist
            if (self.build_dir / "generated" / "asset_reinsertion.asm").exists():
                build_cmd.extend(["-D", "INCLUDE_ASSET_REINSERTION"])

            result = subprocess.run(build_cmd, capture_output=True, text=True, cwd=self.build_dir)

            if result.returncode == 0:
                console.print(f"[green]✅ ROM built successfully: {output_rom}[/green]")
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

    def clean_build(self):
        """Clean build artifacts"""
        console.print("\n[cyan]🧹 Cleaning build artifacts...[/cyan]")

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
            console.print("\n[bold green]🐉 Dragon Warrior Build System[/bold green]")
            console.print("1. 📦 Extract assets from ROM")
            console.print("2. 🎨 Launch asset editors")
            console.print("3. 🔧 Generate assembly code")
            console.print("4. 🏗️  Build modified ROM")
            console.print("5. 📊 Show build status")
            console.print("6. 🧹 Clean build")
            console.print("7. 🚀 Full build pipeline")
            console.print("8. 🚪 Exit")

            choice = click.prompt("\nSelect option", type=str).strip()

            if choice == "1":
                self.extract_assets()

            elif choice == "2":
                self.launch_editor_menu()

            elif choice == "3":
                self.generate_assembly()

            elif choice == "4":
                self.build_rom()

            elif choice == "5":
                self.show_status()

            elif choice == "6":
                self.clean_build()

            elif choice == "7":
                # Full pipeline
                console.print("\n[bold cyan]🚀 Running full build pipeline...[/bold cyan]")
                if (self.extract_assets() and
                    self.generate_assembly() and
                    self.build_rom()):
                    console.print("\n[bold green]✅ Full build pipeline completed successfully![/bold green]")
                else:
                    console.print("\n[bold red]❌ Build pipeline failed at some stage[/bold red]")

            elif choice == "8":
                console.print("\n[bold cyan]👋 Thanks for using Dragon Warrior Build System![/bold cyan]")
                break

            else:
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
            builder.build_rom()):
            console.print("\n[bold green]✅ Build completed successfully![/bold green]")
        else:
            console.print("\n[bold red]❌ Build failed[/bold red]")
            sys.exit(1)

if __name__ == "__main__":
    build_system()
