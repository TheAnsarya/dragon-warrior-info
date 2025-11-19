#!/usr/bin/env python3
"""
Dragon Warrior Dialog Editor
Interactive editor for NPC dialog and text
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
from data_structures import DialogEntry

console = Console()

class DialogEditor:
    """Interactive dialog editor"""

    def __init__(self, data_file: str):
        self.data_file = Path(data_file)
        self.dialogs: Dict[int, DialogEntry] = {}
        self.load_data()

    def load_data(self):
        """Load dialog data from JSON"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for dialog_id_str, dialog_data in data.items():
                    dialog_id = int(dialog_id_str)
                    dialog = DialogEntry(**dialog_data)
                    self.dialogs[dialog_id] = dialog

                console.print(f"[green]✅ Loaded {len(self.dialogs)} dialogs from {self.data_file}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Error loading data: {e}[/red]")
                self.dialogs = {}
        else:
            console.print(f"[yellow]⚠️  Data file not found: {self.data_file}[/yellow]")

    def save_data(self):
        """Save dialog data to JSON"""
        try:
            data = {str(k): v.to_dict() for k, v in self.dialogs.items()}
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✅ Saved to {self.data_file}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error saving: {e}[/red]")

    def display_dialogs(self, location_filter: Optional[str] = None):
        """Display dialog list"""
        table = Table(title="Dragon Warrior Dialogs")
        table.add_column("ID", style="cyan", width=3)
        table.add_column("NPC", style="bold blue", width=15)
        table.add_column("Location", style="yellow", width=12)
        table.add_column("Text Preview", style="white", width=40)
        table.add_column("Compressed", style="green", width=5)

        filtered_dialogs = self.dialogs
        if location_filter:
            filtered_dialogs = {k: v for k, v in self.dialogs.items()
                              if location_filter.lower() in v.location.lower()}

        for dialog_id, dialog in sorted(filtered_dialogs.items()):
            preview = dialog.text[:37] + "..." if len(dialog.text) > 40 else dialog.text
            table.add_row(
                str(dialog.id),
                dialog.npc_name,
                dialog.location,
                preview,
                "✓" if dialog.compressed else "✗"
            )

        console.print(table)

    def edit_dialog(self, dialog_id: int):
        """Edit a specific dialog"""
        if dialog_id not in self.dialogs:
            console.print(f"[red]❌ Dialog {dialog_id} not found[/red]")
            return

        dialog = self.dialogs[dialog_id]

        console.print(Panel.fit(
            f"Editing Dialog: {dialog.npc_name} - {dialog.location}",
            border_style="blue"
        ))

        # Display current dialog
        self._display_dialog_details(dialog)

        # Edit menu
        while True:
            rprint("\n[bold cyan]Edit Options:[/bold cyan]")
            rprint("1. NPC Name")
            rprint("2. Location")
            rprint("3. Dialog Text")
            rprint("4. ROM Pointer")
            rprint("5. Compressed Flag")
            rprint("0. Done")

            choice = Prompt.ask("Select option", choices=["0","1","2","3","4","5"])

            if choice == "0":
                break
            elif choice == "1":
                new_name = Prompt.ask("Enter NPC name", default=dialog.npc_name)
                dialog.npc_name = new_name
            elif choice == "2":
                new_location = Prompt.ask("Enter location", default=dialog.location)
                dialog.location = new_location
            elif choice == "3":
                self._edit_dialog_text(dialog)
            elif choice == "4":
                new_pointer = IntPrompt.ask("Enter ROM pointer (hex)", default=dialog.pointer)
                dialog.pointer = new_pointer
            elif choice == "5":
                dialog.compressed = Confirm.ask("Is dialog compressed?", default=dialog.compressed)

            # Show updated dialog
            self._display_dialog_details(dialog)

        self.dialogs[dialog_id] = dialog
        console.print(f"[green]✅ Dialog {dialog_id} updated[/green]")

    def _display_dialog_details(self, dialog: DialogEntry):
        """Display detailed dialog information"""
        details = f"""[bold]{dialog.npc_name}[/bold] - [yellow]{dialog.location}[/yellow] (ID: {dialog.id})
[cyan]ROM Pointer:[/cyan] 0x{dialog.pointer:04X}  [green]Compressed:[/green] {'Yes' if dialog.compressed else 'No'}

[blue]Dialog Text:[/blue]
{dialog.text}"""

        console.print(Panel(details, border_style="green"))

    def _edit_dialog_text(self, dialog: DialogEntry):
        """Edit dialog text with multi-line support"""
        console.print("\n[bold]Current Text:[/bold]")
        console.print(dialog.text)
        console.print("\n[dim]Enter new text (type 'END' on a new line to finish):[/dim]")

        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)

        new_text = "\n".join(lines)
        if new_text.strip():
            dialog.text = new_text
            console.print("[green]✅ Dialog text updated[/green]")
        else:
            console.print("[yellow]⚠️  No changes made[/yellow]")

    def add_dialog(self):
        """Add a new dialog"""
        # Get next available ID
        max_id = max(self.dialogs.keys()) if self.dialogs else -1
        new_id = max_id + 1

        console.print(f"[cyan]Creating new dialog with ID {new_id}[/cyan]")

        npc_name = Prompt.ask("Enter NPC name", default=f"NPC_{new_id}")
        location = Prompt.ask("Enter location", default="Town")

        console.print("\n[dim]Enter dialog text (type 'END' on a new line to finish):[/dim]")
        lines = []
        while True:
            line = input()
            if line.strip() == "END":
                break
            lines.append(line)

        text = "\n".join(lines) if lines else f"Hello! I am {npc_name}."

        new_dialog = DialogEntry(
            id=new_id,
            npc_name=npc_name,
            location=location,
            text=text,
            pointer=0x7000 + (new_id * 50),  # Estimated pointer
            compressed=True
        )

        self.dialogs[new_id] = new_dialog
        console.print(f"[green]✅ Added dialog for {npc_name} with ID {new_id}[/green]")

    def search_dialogs(self):
        """Search dialogs by text content"""
        search_term = Prompt.ask("Enter search term").lower()

        matches = {}
        for dialog_id, dialog in self.dialogs.items():
            if (search_term in dialog.text.lower() or
                search_term in dialog.npc_name.lower() or
                search_term in dialog.location.lower()):
                matches[dialog_id] = dialog

        if matches:
            console.print(f"\n[green]Found {len(matches)} matches:[/green]")

            table = Table()
            table.add_column("ID", style="cyan")
            table.add_column("NPC", style="blue")
            table.add_column("Location", style="yellow")
            table.add_column("Text", style="white")

            for dialog_id, dialog in matches.items():
                preview = dialog.text[:50] + "..." if len(dialog.text) > 50 else dialog.text
                table.add_row(str(dialog_id), dialog.npc_name, dialog.location, preview)

            console.print(table)
        else:
            console.print("[yellow]No matches found[/yellow]")

    def export_text_file(self):
        """Export all dialogs to a text file"""
        try:
            output_file = self.data_file.parent / "dialogs_export.txt"

            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("Dragon Warrior Dialog Export\n")
                f.write("=" * 40 + "\n\n")

                for dialog_id, dialog in sorted(self.dialogs.items()):
                    f.write(f"ID: {dialog.id}\n")
                    f.write(f"NPC: {dialog.npc_name}\n")
                    f.write(f"Location: {dialog.location}\n")
                    f.write(f"Pointer: 0x{dialog.pointer:04X}\n")
                    f.write(f"Compressed: {'Yes' if dialog.compressed else 'No'}\n")
                    f.write(f"Text:\n{dialog.text}\n")
                    f.write("-" * 40 + "\n\n")

            console.print(f"[green]✅ Exported dialogs to {output_file}[/green]")

        except Exception as e:
            console.print(f"[red]❌ Export failed: {e}[/red]")

    def run(self):
        """Run the dialog editor"""
        console.print(Panel.fit(
            "💬 Dragon Warrior Dialog Editor",
            border_style="cyan"
        ))

        while True:
            rprint("\n[bold blue]Main Menu:[/bold blue]")
            rprint("1. List all dialogs")
            rprint("2. Filter by location")
            rprint("3. Edit dialog")
            rprint("4. Add dialog")
            rprint("5. Search dialogs")
            rprint("6. Export to text file")
            rprint("7. Save data")
            rprint("8. Reload data")
            rprint("0. Exit")

            choice = Prompt.ask("Select option", choices=["0","1","2","3","4","5","6","7","8"])

            if choice == "0":
                if Confirm.ask("Save before exit?"):
                    self.save_data()
                break
            elif choice == "1":
                self.display_dialogs()
            elif choice == "2":
                location = Prompt.ask("Enter location to filter by")
                self.display_dialogs(location)
            elif choice == "3":
                dialog_id = IntPrompt.ask("Enter dialog ID")
                self.edit_dialog(dialog_id)
            elif choice == "4":
                self.add_dialog()
            elif choice == "5":
                self.search_dialogs()
            elif choice == "6":
                self.export_text_file()
            elif choice == "7":
                self.save_data()
            elif choice == "8":
                self.load_data()

@click.command()
@click.argument('data_file', type=click.Path())
def edit_dialogs(data_file: str):
    """Dragon Warrior Dialog Editor"""
    editor = DialogEditor(data_file)
    editor.run()

if __name__ == "__main__":
    edit_dialogs()
