#!/usr/bin/env python3
"""
Dragon Warrior Item Editor - Asset-First Design
Modern CLI editor using Rich library and AssetManager
"""
import sys
from pathlib import Path
from typing import Optional

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from asset_manager import AssetManager, AssetValidationError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich import box

console = Console()


class ItemEditor:
    """Interactive item editor using asset-first workflow"""
    
    ITEM_TYPES = {
        '0': 'WEAPON',
        '1': 'ARMOR',
        '2': 'SHIELD',
        '3': 'TOOL',
        '4': 'KEY_ITEM'
    }
    
    def __init__(self):
        self.manager = AssetManager()
        self.items = None
        self.modified = False
    
    def run(self):
        """Main editor loop"""
        console.print(Panel.fit(
            "[bold cyan]Dragon Warrior Item Editor[/bold cyan]\n"
            "[dim]Asset-First Design - Edit items.json directly[/dim]",
            border_style="cyan"
        ))
        
        # Load items
        try:
            self.items = self.manager.load_asset('items')
            console.print(f"\n✓ Loaded {len(self.items)} items from assets/json/items.json", style="green")
        except FileNotFoundError:
            console.print("\n❌ items.json not found! Please extract items first.", style="red")
            return 1
        
        # Main menu loop
        while True:
            console.print()
            choice = self._show_menu()
            
            if choice == '1':
                self._list_items()
            elif choice == '2':
                self._view_item()
            elif choice == '3':
                self._edit_item()
            elif choice == '4':
                self._search_items()
            elif choice == '5':
                self._compare_items()
            elif choice == '6':
                self._save_changes()
            elif choice == '7':
                self._show_statistics()
            elif choice == '8':
                if self._quit():
                    break
            else:
                console.print("[red]Invalid choice[/red]")
        
        return 0
    
    def _show_menu(self) -> str:
        """Display main menu and get user choice"""
        menu = Table.grid(padding=(0, 2))
        menu.add_column(style="cyan", justify="right")
        menu.add_column()
        
        menu.add_row("1.", "List all items")
        menu.add_row("2.", "View item details")
        menu.add_row("3.", "Edit item")
        menu.add_row("4.", "Search items")
        menu.add_row("5.", "Compare items")
        menu.add_row("6.", "💾 Save changes")
        menu.add_row("7.", "📊 Statistics")
        menu.add_row("8.", "🚪 Quit")
        
        console.print(menu)
        
        # Show unsaved changes indicator
        if self.manager.has_unsaved_changes('items'):
            console.print("\n[yellow]⚠ Unsaved changes![/yellow]")
        
        return Prompt.ask("\n[cyan]Choice[/cyan]", default="1")
    
    def _list_items(self):
        """List all items in a formatted table"""
        table = Table(title="Dragon Warrior Items", box=box.ROUNDED)
        
        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("Type", style="magenta")
        table.add_column("ATK", justify="right", style="red")
        table.add_column("DEF", justify="right", style="blue")
        table.add_column("Price", justify="right", style="yellow")
        table.add_column("Effect", style="green")
        
        for item_id in sorted(self.items.keys()):
            item = self.items[item_id]
            
            item_type = self.ITEM_TYPES.get(str(item.get('item_type')), 'UNKNOWN')
            attack = str(item.get('attack_power', 0)) if item.get('attack_power', 0) > 0 else "-"
            defense = str(item.get('defense_power', 0)) if item.get('defense_power', 0) > 0 else "-"
            price = f"{item.get('buy_price', 0):,}g"
            effect = item.get('effect') or "-"
            
            table.add_row(
                str(item_id),
                item.get('name', 'Unknown'),
                item_type,
                attack,
                defense,
                price,
                effect
            )
        
        console.print("\n", table)
    
    def _view_item(self):
        """View detailed information about an item"""
        item_id = IntPrompt.ask("\n[cyan]Item ID[/cyan]")
        
        if item_id not in self.items:
            console.print(f"[red]Item {item_id} not found![/red]")
            return
        
        item = self.items[item_id]
        
        # Create detail panel
        details = f"""[bold]{item.get('name', 'Unknown')}[/bold]
        
[cyan]ID:[/cyan] {item_id}
[cyan]Type:[/cyan] {self.ITEM_TYPES.get(str(item.get('item_type')), 'UNKNOWN')}
[cyan]Attack Power:[/cyan] {item.get('attack_power', 0)}
[cyan]Defense Power:[/cyan] {item.get('defense_power', 0)}

[yellow]Buy Price:[/yellow] {item.get('buy_price', 0):,} gold
[yellow]Sell Price:[/yellow] {item.get('sell_price', 0):,} gold

[green]Equippable:[/green] {'Yes' if item.get('equippable') else 'No'}
[green]Useable:[/green] {'Yes' if item.get('useable') else 'No'}
[green]Effect:[/green] {item.get('effect') or 'None'}

[dim]{item.get('description', 'No description')}[/dim]"""
        
        console.print(Panel(details, title=f"Item {item_id}", border_style="cyan"))
    
    def _edit_item(self):
        """Edit an item's properties"""
        item_id = IntPrompt.ask("\n[cyan]Item ID to edit[/cyan]")
        
        if item_id not in self.items:
            console.print(f"[red]Item {item_id} not found![/red]")
            return
        
        item = self.items[item_id]
        console.print(f"\n[bold]Editing: {item.get('name')}[/bold]")
        
        # Edit menu
        while True:
            console.print("\nWhat to edit?")
            console.print("  1. Attack Power")
            console.print("  2. Defense Power")
            console.print("  3. Buy Price")
            console.print("  4. Sell Price")
            console.print("  5. Description")
            console.print("  6. Effect")
            console.print("  7. Done editing")
            
            choice = Prompt.ask("[cyan]Choice[/cyan]", default="7")
            
            if choice == '1':
                current = item.get('attack_power', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]Attack Power[/cyan] (current: {current}, max: 127)",
                    default=current
                )
                if 0 <= new_value <= 127:
                    item['attack_power'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('items')
                    console.print(f"[green]✓ Updated to {new_value}[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-127[/red]")
            
            elif choice == '2':
                current = item.get('defense_power', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]Defense Power[/cyan] (current: {current}, max: 127)",
                    default=current
                )
                if 0 <= new_value <= 127:
                    item['defense_power'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('items')
                    console.print(f"[green]✓ Updated to {new_value}[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-127[/red]")
            
            elif choice == '3':
                current = item.get('buy_price', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]Buy Price[/cyan] (current: {current:,}g, max: 65535)",
                    default=current
                )
                if 0 <= new_value <= 65535:
                    item['buy_price'] = new_value
                    # Auto-update sell price (half of buy price)
                    item['sell_price'] = new_value // 2
                    self.modified = True
                    self.manager.mark_dirty('items')
                    console.print(f"[green]✓ Updated buy: {new_value:,}g, sell: {item['sell_price']:,}g[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-65535[/red]")
            
            elif choice == '4':
                current = item.get('sell_price', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]Sell Price[/cyan] (current: {current:,}g)",
                    default=current
                )
                if 0 <= new_value <= 65535:
                    item['sell_price'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('items')
                    console.print(f"[green]✓ Updated to {new_value:,}g[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-65535[/red]")
            
            elif choice == '5':
                current = item.get('description', '')
                new_value = Prompt.ask("[cyan]Description[/cyan]", default=current)
                item['description'] = new_value
                self.modified = True
                self.manager.mark_dirty('items')
                console.print("[green]✓ Updated[/green]")
            
            elif choice == '6':
                current = item.get('effect') or 'none'
                console.print("\nCommon effects: light, heal, unlock_door, unlock_magic_door, return_to_castle")
                new_value = Prompt.ask("[cyan]Effect[/cyan] (or 'none')", default=current)
                item['effect'] = None if new_value.lower() == 'none' else new_value
                self.modified = True
                self.manager.mark_dirty('items')
                console.print("[green]✓ Updated[/green]")
            
            elif choice == '7':
                break
    
    def _search_items(self):
        """Search items by name or properties"""
        query = Prompt.ask("\n[cyan]Search for[/cyan]").lower()
        
        results = []
        for item_id, item in self.items.items():
            if query in item.get('name', '').lower():
                results.append((item_id, item))
        
        if not results:
            console.print("[yellow]No items found[/yellow]")
            return
        
        console.print(f"\n[green]Found {len(results)} item(s):[/green]")
        for item_id, item in results:
            console.print(f"  {item_id:2d}. {item.get('name')}")
    
    def _compare_items(self):
        """Compare two items side by side"""
        id1 = IntPrompt.ask("\n[cyan]First item ID[/cyan]")
        id2 = IntPrompt.ask("[cyan]Second item ID[/cyan]")
        
        if id1 not in self.items or id2 not in self.items:
            console.print("[red]One or both items not found![/red]")
            return
        
        item1 = self.items[id1]
        item2 = self.items[id2]
        
        table = Table(title="Item Comparison", box=box.DOUBLE)
        table.add_column("Property")
        table.add_column(item1.get('name'), style="cyan")
        table.add_column(item2.get('name'), style="magenta")
        
        table.add_row("Attack Power", str(item1.get('attack_power', 0)), str(item2.get('attack_power', 0)))
        table.add_row("Defense Power", str(item1.get('defense_power', 0)), str(item2.get('defense_power', 0)))
        table.add_row("Buy Price", f"{item1.get('buy_price', 0):,}g", f"{item2.get('buy_price', 0):,}g")
        table.add_row("Sell Price", f"{item1.get('sell_price', 0):,}g", f"{item2.get('sell_price', 0):,}g")
        table.add_row("Equippable", str(item1.get('equippable')), str(item2.get('equippable')))
        table.add_row("Effect", item1.get('effect') or '-', item2.get('effect') or '-')
        
        console.print("\n", table)
    
    def _save_changes(self):
        """Save changes to items.json"""
        if not self.manager.has_unsaved_changes('items'):
            console.print("\n[dim]No changes to save[/dim]")
            return
        
        console.print("\n[yellow]Saving changes with automatic backup...[/yellow]")
        
        try:
            saved_path = self.manager.save_asset('items', self.items, create_backup=True, validate=True)
            console.print(f"[green]✓ Saved successfully to {saved_path.name}[/green]")
            
            # Show backups
            backups = self.manager.list_backups('items')
            if backups:
                console.print(f"[dim]Backup created: {backups[0].name}[/dim]")
            
            self.modified = False
        except AssetValidationError as e:
            console.print(f"[red]❌ Validation failed: {e}[/red]")
        except Exception as e:
            console.print(f"[red]❌ Save failed: {e}[/red]")
    
    def _show_statistics(self):
        """Show item statistics"""
        # Calculate stats
        total_items = len(self.items)
        weapons = sum(1 for item in self.items.values() if item.get('item_type') == '0')
        armor = sum(1 for item in self.items.values() if item.get('item_type') == '1')
        shields = sum(1 for item in self.items.values() if item.get('item_type') == '2')
        tools = sum(1 for item in self.items.values() if item.get('item_type') == '3')
        
        max_attack = max((item.get('attack_power', 0) for item in self.items.values()), default=0)
        max_defense = max((item.get('defense_power', 0) for item in self.items.values()), default=0)
        max_price = max((item.get('buy_price', 0) for item in self.items.values()), default=0)
        
        stats = f"""[bold]Item Statistics[/bold]

[cyan]Total Items:[/cyan] {total_items}
[cyan]Weapons:[/cyan] {weapons}
[cyan]Armor:[/cyan] {armor}
[cyan]Shields:[/cyan] {shields}
[cyan]Tools:[/cyan] {tools}

[green]Highest Attack:[/green] {max_attack}
[green]Highest Defense:[/green] {max_defense}
[yellow]Most Expensive:[/yellow] {max_price:,} gold"""
        
        console.print(Panel(stats, title="📊 Statistics", border_style="cyan"))
    
    def _quit(self) -> bool:
        """Quit the editor (with unsaved changes warning)"""
        if self.manager.has_unsaved_changes('items'):
            console.print("\n[yellow]⚠ You have unsaved changes![/yellow]")
            if not Confirm.ask("[cyan]Really quit without saving?[/cyan]"):
                return False
        
        console.print("\n[dim]Goodbye![/dim]\n")
        return True


def main():
    """Main entry point"""
    try:
        editor = ItemEditor()
        return editor.run()
    except KeyboardInterrupt:
        console.print("\n\n[dim]Interrupted by user[/dim]")
        return 0
    except Exception as e:
        console.print(f"\n[red]❌ Fatal error: {e}[/red]")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
