#!/usr/bin/env python3
"""
Dragon Warrior Monster Editor - Asset-First Design
Modern CLI editor using Rich library and AssetManager
"""
import sys
from pathlib import Path
from typing import Optional

# Add tools to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from asset_manager import AssetManager, AssetValidationError
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich import box

console = Console()


class MonsterEditor:
    """Interactive monster editor using asset-first workflow"""

    def __init__(self):
        self.manager = AssetManager()
        self.monsters = None
        self.modified = False

    def run(self):
        """Main editor loop"""
        console.print(Panel.fit(
            "[bold cyan]Dragon Warrior Monster Editor[/bold cyan]\n"
            "[dim]Asset-First Design - Edit monsters.json directly[/dim]",
            border_style="cyan"
        ))

        # Load monsters
        try:
            self.monsters = self.manager.load_asset('monsters')
            console.print(f"\n✓ Loaded {len(self.monsters)} monsters", style="green")
        except FileNotFoundError:
            console.print("\n❌ monsters.json not found! Please extract monsters first.", style="red")
            return 1

        # Main menu loop
        while True:
            console.print()
            choice = self._show_menu()

            if choice == '1':
                self._list_monsters()
            elif choice == '2':
                self._view_monster()
            elif choice == '3':
                self._edit_monster()
            elif choice == '4':
                self._search_monsters()
            elif choice == '5':
                self._compare_monsters()
            elif choice == '6':
                self._show_statistics()
            elif choice == '7':
                self._balance_analysis()
            elif choice == '8':
                self._save_changes()
            elif choice == '9':
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

        menu.add_row("1.", "List all monsters")
        menu.add_row("2.", "View monster details")
        menu.add_row("3.", "Edit monster stats")
        menu.add_row("4.", "Search monsters")
        menu.add_row("5.", "Compare monsters")
        menu.add_row("6.", "📊 Statistics")
        menu.add_row("7.", "⚖️ Balance analysis")
        menu.add_row("8.", "💾 Save changes")
        menu.add_row("9.", "🚪 Quit")

        console.print(menu)

        # Show unsaved changes indicator
        if self.manager.has_unsaved_changes('monsters'):
            console.print("\n[yellow]⚠ Unsaved changes![/yellow]")

        return Prompt.ask("\n[cyan]Choice[/cyan]", default="1")

    def _list_monsters(self):
        """List all monsters in a formatted table"""
        table = Table(title="Dragon Warrior Monsters", box=box.ROUNDED)

        table.add_column("ID", justify="right", style="cyan")
        table.add_column("Name", style="bold")
        table.add_column("HP", justify="right", style="red")
        table.add_column("STR", justify="right", style="yellow")
        table.add_column("AGI", justify="right", style="green")
        table.add_column("EXP", justify="right", style="blue")
        table.add_column("Gold", justify="right", style="yellow")

        for monster_id in sorted(self.monsters.keys()):
            monster = self.monsters[monster_id]

            table.add_row(
                str(monster_id),
                monster.get('name', 'Unknown'),
                str(monster.get('hp', 0)),
                str(monster.get('strength', 0)),
                str(monster.get('agility', 0)),
                str(monster.get('experience', 0)),
                f"{monster.get('gold', 0)}g"
            )

        console.print("\n", table)

    def _view_monster(self):
        """View detailed information about a monster"""
        monster_id = IntPrompt.ask("\n[cyan]Monster ID[/cyan]")

        if monster_id not in self.monsters:
            console.print(f"[red]Monster {monster_id} not found![/red]")
            return

        monster = self.monsters[monster_id]

        # Create detail panel
        details = f"""[bold]{monster.get('name', 'Unknown')}[/bold]

[cyan]ID:[/cyan] {monster_id}

[red]Combat Stats:[/red]
  HP: {monster.get('hp', 0)}
  Strength: {monster.get('strength', 0)}
  Agility: {monster.get('agility', 0)}
  Defense: {monster.get('defense', 0)}
  Attack Pattern: {monster.get('attack_pattern', 0)}

[green]Resistances:[/green]
  HURT Resistance: {monster.get('hurt_resistance', 0)}
  SLEEP Resistance: {monster.get('sleep_resistance', 0)}
  STOPSPELL Resistance: {monster.get('stopspell_resistance', 0)}
  Magic Defense: {monster.get('magic_defense', 0)}

[yellow]Rewards:[/yellow]
  Experience: {monster.get('experience', 0)}
  Gold: {monster.get('gold', 0)}g

[magenta]Special:[/magenta]
  Dodges: {'Yes' if monster.get('dodges') else 'No'}
  Runs Away: {'Yes' if monster.get('runs_away') else 'No'}
  Casts Spells: {'Yes' if monster.get('spell', 0) > 0 else 'No'}
  Spell: {self._get_spell_name(monster.get('spell', 0))}"""

        console.print(Panel(details, title=f"Monster {monster_id}", border_style="cyan"))

    def _get_spell_name(self, spell_id: int) -> str:
        """Get spell name from ID"""
        spell_names = {
            0: "None",
            1: "HEAL",
            2: "HURT",
            3: "SLEEP",
            4: "RADIANT",
            5: "STOPSPELL",
            6: "OUTSIDE",
            7: "RETURN",
            8: "REPEL",
            9: "HEALMORE",
            10: "HURTMORE"
        }
        return spell_names.get(spell_id, f"Unknown ({spell_id})")

    def _edit_monster(self):
        """Edit a monster's properties"""
        monster_id = IntPrompt.ask("\n[cyan]Monster ID to edit[/cyan]")

        if monster_id not in self.monsters:
            console.print(f"[red]Monster {monster_id} not found![/red]")
            return

        monster = self.monsters[monster_id]
        console.print(f"\n[bold]Editing: {monster.get('name')}[/bold]")

        # Edit menu
        while True:
            console.print("\nWhat to edit?")
            console.print("  1. HP")
            console.print("  2. Strength")
            console.print("  3. Agility")
            console.print("  4. Defense")
            console.print("  5. Experience Reward")
            console.print("  6. Gold Reward")
            console.print("  7. Magic Defense")
            console.print("  8. Spell")
            console.print("  9. Done editing")

            choice = Prompt.ask("[cyan]Choice[/cyan]", default="9")

            if choice == '1':
                current = monster.get('hp', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]HP[/cyan] (current: {current}, range: 1-255)",
                    default=current
                )
                if 1 <= new_value <= 255:
                    monster['hp'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('monsters')
                    console.print(f"[green]✓ Updated to {new_value}[/green]")
                else:
                    console.print("[red]Invalid value! Must be 1-255[/red]")

            elif choice == '2':
                current = monster.get('strength', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]Strength[/cyan] (current: {current}, range: 0-255)",
                    default=current
                )
                if 0 <= new_value <= 255:
                    monster['strength'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('monsters')
                    console.print(f"[green]✓ Updated to {new_value}[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-255[/red]")

            elif choice == '3':
                current = monster.get('agility', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]Agility[/cyan] (current: {current}, range: 0-255)",
                    default=current
                )
                if 0 <= new_value <= 255:
                    monster['agility'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('monsters')
                    console.print(f"[green]✓ Updated to {new_value}[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-255[/red]")

            elif choice == '4':
                current = monster.get('defense', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]Defense[/cyan] (current: {current}, range: 0-255)",
                    default=current
                )
                if 0 <= new_value <= 255:
                    monster['defense'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('monsters')
                    console.print(f"[green]✓ Updated to {new_value}[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-255[/red]")

            elif choice == '5':
                current = monster.get('experience', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]Experience Reward[/cyan] (current: {current}, range: 0-65535)",
                    default=current
                )
                if 0 <= new_value <= 65535:
                    monster['experience'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('monsters')
                    console.print(f"[green]✓ Updated to {new_value}[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-65535[/red]")

            elif choice == '6':
                current = monster.get('gold', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]Gold Reward[/cyan] (current: {current}, range: 0-65535)",
                    default=current
                )
                if 0 <= new_value <= 65535:
                    monster['gold'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('monsters')
                    console.print(f"[green]✓ Updated to {new_value}[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-65535[/red]")

            elif choice == '7':
                current = monster.get('magic_defense', 0)
                new_value = IntPrompt.ask(
                    f"[cyan]Magic Defense[/cyan] (current: {current}, range: 0-255)",
                    default=current
                )
                if 0 <= new_value <= 255:
                    monster['magic_defense'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('monsters')
                    console.print(f"[green]✓ Updated to {new_value}[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-255[/red]")

            elif choice == '8':
                current = monster.get('spell', 0)
                console.print(f"\nCurrent: {self._get_spell_name(current)}")
                console.print("Spells: 0=None, 1=HEAL, 2=HURT, 3=SLEEP, 4=RADIANT, 5=STOPSPELL")
                new_value = IntPrompt.ask(
                    "[cyan]Spell ID[/cyan]",
                    default=current
                )
                if 0 <= new_value <= 10:
                    monster['spell'] = new_value
                    self.modified = True
                    self.manager.mark_dirty('monsters')
                    console.print(f"[green]✓ Updated to {self._get_spell_name(new_value)}[/green]")
                else:
                    console.print("[red]Invalid value! Must be 0-10[/red]")

            elif choice == '9':
                break

    def _search_monsters(self):
        """Search monsters by name or properties"""
        query = Prompt.ask("\n[cyan]Search for[/cyan]").lower()

        results = []
        for monster_id, monster in self.monsters.items():
            if query in monster.get('name', '').lower():
                results.append((monster_id, monster))

        if not results:
            console.print("[yellow]No monsters found[/yellow]")
            return

        console.print(f"\n[green]Found {len(results)} monster(s):[/green]")
        for monster_id, monster in results:
            console.print(f"  {monster_id:2d}. {monster.get('name')} (HP: {monster.get('hp')}, STR: {monster.get('strength')})")

    def _compare_monsters(self):
        """Compare two monsters side by side"""
        id1 = IntPrompt.ask("\n[cyan]First monster ID[/cyan]")
        id2 = IntPrompt.ask("[cyan]Second monster ID[/cyan]")

        if id1 not in self.monsters or id2 not in self.monsters:
            console.print("[red]One or both monsters not found![/red]")
            return

        monster1 = self.monsters[id1]
        monster2 = self.monsters[id2]

        table = Table(title="Monster Comparison", box=box.DOUBLE)
        table.add_column("Stat")
        table.add_column(monster1.get('name'), style="cyan")
        table.add_column(monster2.get('name'), style="magenta")
        table.add_column("Difference", style="yellow")

        # Compare stats
        stats = [
            ('HP', 'hp'),
            ('Strength', 'strength'),
            ('Agility', 'agility'),
            ('Defense', 'defense'),
            ('Experience', 'experience'),
            ('Gold', 'gold'),
            ('Magic Defense', 'magic_defense')
        ]

        for label, key in stats:
            val1 = monster1.get(key, 0)
            val2 = monster2.get(key, 0)
            diff = val2 - val1
            diff_str = f"+{diff}" if diff > 0 else str(diff)
            table.add_row(label, str(val1), str(val2), diff_str)

        console.print("\n", table)

    def _show_statistics(self):
        """Show monster statistics"""
        # Calculate stats
        total = len(self.monsters)

        avg_hp = sum(m.get('hp', 0) for m in self.monsters.values()) / total
        avg_str = sum(m.get('strength', 0) for m in self.monsters.values()) / total
        avg_exp = sum(m.get('experience', 0) for m in self.monsters.values()) / total
        avg_gold = sum(m.get('gold', 0) for m in self.monsters.values()) / total

        max_hp = max((m.get('hp', 0) for m in self.monsters.values()), default=0)
        max_str = max((m.get('strength', 0) for m in self.monsters.values()), default=0)
        max_exp = max((m.get('experience', 0) for m in self.monsters.values()), default=0)
        max_gold = max((m.get('gold', 0) for m in self.monsters.values()), default=0)

        spell_casters = sum(1 for m in self.monsters.values() if m.get('spell', 0) > 0)

        stats = f"""[bold]Monster Statistics[/bold]

[cyan]Total Monsters:[/cyan] {total}

[green]Average Stats:[/green]
  HP: {avg_hp:.1f}
  Strength: {avg_str:.1f}
  Experience: {avg_exp:.1f}
  Gold: {avg_gold:.1f}g

[yellow]Maximum Values:[/yellow]
  HP: {max_hp}
  Strength: {max_str}
  Experience: {max_exp}
  Gold: {max_gold}g

[magenta]Special:[/magenta]
  Spell Casters: {spell_casters} ({spell_casters/total*100:.1f}%)"""

        console.print(Panel(stats, title="📊 Statistics", border_style="cyan"))

    def _balance_analysis(self):
        """Analyze monster balance and progression"""
        console.print("\n[bold cyan]Balance Analysis[/bold cyan]\n")

        # Group monsters by strength tiers
        weak = []
        medium = []
        strong = []
        boss = []

        for monster_id, monster in self.monsters.items():
            hp = monster.get('hp', 0)
            strength = monster.get('strength', 0)
            power = hp + strength * 2  # Simple power metric

            if power < 50:
                weak.append((monster_id, monster, power))
            elif power < 150:
                medium.append((monster_id, monster, power))
            elif power < 300:
                strong.append((monster_id, monster, power))
            else:
                boss.append((monster_id, monster, power))

        table = Table(title="Monster Tiers by Power", box=box.ROUNDED)
        table.add_column("Tier", style="bold")
        table.add_column("Count", justify="right")
        table.add_column("Examples", style="dim")

        table.add_row(
            "Weak (< 50)",
            str(len(weak)),
            ", ".join(m[1]['name'] for m in weak[:3])
        )
        table.add_row(
            "Medium (50-149)",
            str(len(medium)),
            ", ".join(m[1]['name'] for m in medium[:3])
        )
        table.add_row(
            "Strong (150-299)",
            str(len(strong)),
            ", ".join(m[1]['name'] for m in strong[:3])
        )
        table.add_row(
            "Boss (300+)",
            str(len(boss)),
            ", ".join(m[1]['name'] for m in boss[:3])
        )

        console.print(table)

        # Reward efficiency
        console.print("\n[bold]Top 5 Reward Efficiency (EXP per HP):[/bold]")
        efficiency = []
        for monster_id, monster in self.monsters.items():
            hp = monster.get('hp', 0)
            exp = monster.get('experience', 0)
            if hp > 0:
                eff = exp / hp
                efficiency.append((monster_id, monster, eff))

        efficiency.sort(key=lambda x: x[2], reverse=True)
        for i, (monster_id, monster, eff) in enumerate(efficiency[:5], 1):
            console.print(f"  {i}. {monster['name']:20s} - {eff:.2f} EXP/HP")

    def _save_changes(self):
        """Save changes to monsters.json"""
        if not self.manager.has_unsaved_changes('monsters'):
            console.print("\n[dim]No changes to save[/dim]")
            return

        console.print("\n[yellow]Saving changes with automatic backup...[/yellow]")

        try:
            saved_path = self.manager.save_asset('monsters', self.monsters, create_backup=True, validate=True)
            console.print(f"[green]✓ Saved successfully to {saved_path.name}[/green]")

            # Show backups
            backups = self.manager.list_backups('monsters')
            if backups:
                console.print(f"[dim]Backup created: {backups[0].name}[/dim]")

            self.modified = False
        except AssetValidationError as e:
            console.print(f"[red]❌ Validation failed: {e}[/red]")
        except Exception as e:
            console.print(f"[red]❌ Save failed: {e}[/red]")

    def _quit(self) -> bool:
        """Quit the editor (with unsaved changes warning)"""
        if self.manager.has_unsaved_changes('monsters'):
            console.print("\n[yellow]⚠ You have unsaved changes![/yellow]")
            if not Confirm.ask("[cyan]Really quit without saving?[/cyan]"):
                return False

        console.print("\n[dim]Goodbye![/dim]\n")
        return True


def main():
    """Main entry point"""
    try:
        editor = MonsterEditor()
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
