#!/usr/bin/env python3
"""
Dragon Warrior Monster Editor
Interactive editor for monster statistics and properties
"""

import json
from pathlib import Path
from typing import Dict, List, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich import print as rprint

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / 'extraction'))
from data_structures import MonsterStats, MonsterType, GameData

console = Console()

class MonsterEditor:
    """Interactive monster stats editor"""

    def __init__(self, data_file: str):
        self.data_file = Path(data_file)
        self.monsters: Dict[int, MonsterStats] = {}
        self.load_data()

    def load_data(self):
        """Load monster data from JSON"""
        if self.data_file.exists():
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                for monster_id_str, monster_data in data.items():
                    monster_id = int(monster_id_str)
                    monster = MonsterStats(**monster_data)
                    self.monsters[monster_id] = monster

                console.print(f"[green]✅ Loaded {len(self.monsters)} monsters from {self.data_file}[/green]")
            except Exception as e:
                console.print(f"[red]❌ Error loading data: {e}[/red]")
                self.monsters = {}
        else:
            console.print(f"[yellow]⚠️  Data file not found: {self.data_file}[/yellow]")

    def save_data(self):
        """Save monster data to JSON"""
        try:
            data = {str(k): v.to_dict() for k, v in self.monsters.items()}
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            console.print(f"[green]✅ Saved to {self.data_file}[/green]")
        except Exception as e:
            console.print(f"[red]❌ Error saving: {e}[/red]")

    def display_monsters(self, limit: int = 20):
        """Display monster list"""
        table = Table(title="Dragon Warrior Monsters")
        table.add_column("ID", style="cyan", width=3)
        table.add_column("Name", style="bold blue", width=15)
        table.add_column("HP", style="red", width=4)
        table.add_column("STR", style="yellow", width=4)
        table.add_column("AGI", style="green", width=4)
        table.add_column("DMG", style="magenta", width=4)
        table.add_column("EXP", style="cyan", width=5)
        table.add_column("Gold", style="yellow", width=5)
        table.add_column("Type", style="white", width=8)

        count = 0
        for monster_id, monster in sorted(self.monsters.items()):
            if count >= limit:
                break

            table.add_row(
                str(monster.id),
                monster.name,
                str(monster.hp),
                str(monster.strength),
                str(monster.agility),
                str(monster.max_damage),
                str(monster.experience),
                str(monster.gold),
                monster.monster_type.name
            )
            count += 1

        console.print(table)

        if len(self.monsters) > limit:
            console.print(f"[dim]... and {len(self.monsters) - limit} more monsters[/dim]")

    def edit_monster(self, monster_id: int):
        """Edit a specific monster"""
        if monster_id not in self.monsters:
            console.print(f"[red]❌ Monster {monster_id} not found[/red]")
            return

        monster = self.monsters[monster_id]

        console.print(Panel.fit(
            f"Editing Monster: {monster.name} (ID: {monster.id})",
            border_style="blue"
        ))

        # Display current stats
        self._display_monster_details(monster)

        # Edit menu
        while True:
            rprint("\n[bold cyan]Edit Options:[/bold cyan]")
            rprint("1. Name")
            rprint("2. HP")
            rprint("3. Strength")
            rprint("4. Agility")
            rprint("5. Max Damage")
            rprint("6. Dodge Rate")
            rprint("7. Sleep Resistance")
            rprint("8. Hurt Resistance")
            rprint("9. Experience")
            rprint("10. Gold")
            rprint("11. Monster Type")
            rprint("12. Sprite ID")
            rprint("0. Done")

            choice = Prompt.ask("Select option", choices=["0","1","2","3","4","5","6","7","8","9","10","11","12"])

            if choice == "0":
                break
            elif choice == "1":
                new_name = Prompt.ask("Enter new name", default=monster.name)
                monster.name = new_name
            elif choice == "2":
                new_hp = IntPrompt.ask("Enter new HP", default=monster.hp)
                monster.hp = max(1, new_hp)
            elif choice == "3":
                new_str = IntPrompt.ask("Enter new Strength", default=monster.strength)
                monster.strength = max(1, new_str)
            elif choice == "4":
                new_agi = IntPrompt.ask("Enter new Agility", default=monster.agility)
                monster.agility = max(1, new_agi)
            elif choice == "5":
                new_dmg = IntPrompt.ask("Enter new Max Damage", default=monster.max_damage)
                monster.max_damage = max(1, new_dmg)
            elif choice == "6":
                new_dodge = IntPrompt.ask("Enter new Dodge Rate (0-255)", default=monster.dodge_rate)
                monster.dodge_rate = max(0, min(255, new_dodge))
            elif choice == "7":
                new_sleep = IntPrompt.ask("Enter new Sleep Resistance (0-255)", default=monster.sleep_resistance)
                monster.sleep_resistance = max(0, min(255, new_sleep))
            elif choice == "8":
                new_hurt = IntPrompt.ask("Enter new Hurt Resistance (0-255)", default=monster.hurt_resistance)
                monster.hurt_resistance = max(0, min(255, new_hurt))
            elif choice == "9":
                new_exp = IntPrompt.ask("Enter new Experience", default=monster.experience)
                monster.experience = max(0, new_exp)
            elif choice == "10":
                new_gold = IntPrompt.ask("Enter new Gold", default=monster.gold)
                monster.gold = max(0, new_gold)
            elif choice == "11":
                self._edit_monster_type(monster)
            elif choice == "12":
                new_sprite = IntPrompt.ask("Enter new Sprite ID", default=monster.sprite_id)
                monster.sprite_id = new_sprite

            # Show updated stats
            self._display_monster_details(monster)

        self.monsters[monster_id] = monster
        console.print(f"[green]✅ Monster {monster.name} updated[/green]")

    def _display_monster_details(self, monster: MonsterStats):
        """Display detailed monster information"""
        details = f"""[bold]{monster.name}[/bold] (ID: {monster.id})
[red]HP:[/red] {monster.hp}  [yellow]STR:[/yellow] {monster.strength}  [green]AGI:[/green] {monster.agility}  [magenta]DMG:[/magenta] {monster.max_damage}
[cyan]Dodge:[/cyan] {monster.dodge_rate}  [blue]Sleep Res:[/blue] {monster.sleep_resistance}  [purple]Hurt Res:[/purple] {monster.hurt_resistance}
[yellow]EXP:[/yellow] {monster.experience}  [yellow]Gold:[/yellow] {monster.gold}  [white]Type:[/white] {monster.monster_type.name}  [dim]Sprite:[/dim] {monster.sprite_id}"""

        console.print(Panel(details, border_style="green"))

    def _edit_monster_type(self, monster: MonsterStats):
        """Edit monster type"""
        rprint("\n[bold]Monster Types:[/bold]")
        for i, mtype in enumerate(MonsterType):
            rprint(f"{i}. {mtype.name}")

        type_choice = IntPrompt.ask("Select type", choices=[str(i) for i in range(len(MonsterType))])
        monster.monster_type = list(MonsterType)[type_choice]

    def add_monster(self):
        """Add a new monster"""
        # Get next available ID
        max_id = max(self.monsters.keys()) if self.monsters else -1
        new_id = max_id + 1

        console.print(f"[cyan]Creating new monster with ID {new_id}[/cyan]")

        name = Prompt.ask("Enter monster name", default=f"NewMonster_{new_id}")
        hp = IntPrompt.ask("Enter HP", default=20)
        strength = IntPrompt.ask("Enter Strength", default=10)
        agility = IntPrompt.ask("Enter Agility", default=10)
        max_damage = IntPrompt.ask("Enter Max Damage", default=8)
        experience = IntPrompt.ask("Enter Experience reward", default=10)
        gold = IntPrompt.ask("Enter Gold reward", default=5)

        new_monster = MonsterStats(
            id=new_id,
            name=name,
            hp=hp,
            strength=strength,
            agility=agility,
            max_damage=max_damage,
            dodge_rate=0,
            sleep_resistance=0,
            hurt_resistance=0,
            experience=experience,
            gold=gold,
            monster_type=MonsterType.BEAST,
            sprite_id=new_id + 16
        )

        self.monsters[new_id] = new_monster
        console.print(f"[green]✅ Added monster {name} with ID {new_id}[/green]")

    def delete_monster(self, monster_id: int):
        """Delete a monster"""
        if monster_id not in self.monsters:
            console.print(f"[red]❌ Monster {monster_id} not found[/red]")
            return

        monster = self.monsters[monster_id]
        if Confirm.ask(f"Delete monster {monster.name} (ID: {monster_id})?"):
            del self.monsters[monster_id]
            console.print(f"[green]✅ Deleted monster {monster.name}[/green]")

    def bulk_edit(self):
        """Bulk edit operations"""
        rprint("\n[bold cyan]Bulk Edit Options:[/bold cyan]")
        rprint("1. Scale all HP by percentage")
        rprint("2. Scale all EXP by percentage")
        rprint("3. Scale all Gold by percentage")
        rprint("4. Set all resistances to value")
        rprint("0. Back")

        choice = Prompt.ask("Select option", choices=["0","1","2","3","4"])

        if choice == "1":
            scale = IntPrompt.ask("HP scale percentage", default=100)
            for monster in self.monsters.values():
                monster.hp = max(1, int(monster.hp * scale / 100))
            console.print(f"[green]✅ Scaled all monster HP by {scale}%[/green]")
        elif choice == "2":
            scale = IntPrompt.ask("EXP scale percentage", default=100)
            for monster in self.monsters.values():
                monster.experience = max(0, int(monster.experience * scale / 100))
            console.print(f"[green]✅ Scaled all monster EXP by {scale}%[/green]")
        elif choice == "3":
            scale = IntPrompt.ask("Gold scale percentage", default=100)
            for monster in self.monsters.values():
                monster.gold = max(0, int(monster.gold * scale / 100))
            console.print(f"[green]✅ Scaled all monster Gold by {scale}%[/green]")
        elif choice == "4":
            resistance = IntPrompt.ask("Resistance value (0-255)", default=0)
            resistance = max(0, min(255, resistance))
            for monster in self.monsters.values():
                monster.sleep_resistance = resistance
                monster.hurt_resistance = resistance
            console.print(f"[green]✅ Set all resistances to {resistance}[/green]")

    def run(self):
        """Run the monster editor"""
        console.print(Panel.fit(
            "🐉 Dragon Warrior Monster Editor",
            border_style="red"
        ))

        while True:
            rprint("\n[bold blue]Main Menu:[/bold blue]")
            rprint("1. List monsters")
            rprint("2. Edit monster")
            rprint("3. Add monster")
            rprint("4. Delete monster")
            rprint("5. Bulk edit")
            rprint("6. Save data")
            rprint("7. Reload data")
            rprint("0. Exit")

            choice = Prompt.ask("Select option", choices=["0","1","2","3","4","5","6","7"])

            if choice == "0":
                if Confirm.ask("Save before exit?"):
                    self.save_data()
                break
            elif choice == "1":
                limit = IntPrompt.ask("How many to show?", default=20)
                self.display_monsters(limit)
            elif choice == "2":
                monster_id = IntPrompt.ask("Enter monster ID")
                self.edit_monster(monster_id)
            elif choice == "3":
                self.add_monster()
            elif choice == "4":
                monster_id = IntPrompt.ask("Enter monster ID to delete")
                self.delete_monster(monster_id)
            elif choice == "5":
                self.bulk_edit()
            elif choice == "6":
                self.save_data()
            elif choice == "7":
                self.load_data()

@click.command()
@click.argument('data_file', type=click.Path())
def edit_monsters(data_file: str):
    """Dragon Warrior Monster Editor"""
    editor = MonsterEditor(data_file)
    editor.run()

if __name__ == "__main__":
    edit_monsters()
