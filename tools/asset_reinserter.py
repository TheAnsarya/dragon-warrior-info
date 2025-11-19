#!/usr/bin/env python3
"""
Dragon Warrior Complete Asset Reinsertion System
Generate assembly code for reinserting edited assets back into ROM
"""

import json
import struct
from pathlib import Path
from typing import Dict, List, Any, Optional
import click
from rich.console import Console
from rich.progress import track
from PIL import Image

# Add extraction directory to path
import sys
sys.path.append(str(Path(__file__).parent / 'extraction'))
from data_structures import GameData

console = Console()

class AssetReinserter:
	"""Generate assembly code for reinserting edited assets"""

	def __init__(self, assets_dir: str, output_dir: str = "build/generated"):
		self.assets_dir = Path(assets_dir)
		self.output_dir = Path(output_dir)
		self.output_dir.mkdir(parents=True, exist_ok=True)

		self.json_dir = self.assets_dir / "json"
		self.graphics_dir = self.assets_dir / "graphics"
		self.palettes_dir = self.assets_dir / "palettes"
		self.maps_dir = self.assets_dir / "maps"

	def generate_all_assembly(self):
		"""Generate all assembly files for asset reinsertion"""
		console.print("[blue]🔧 Generating assembly code for asset reinsertion...[/blue]\n")

		generated_files = []

		# Generate monster data assembly
		monsters_file = self.json_dir / "monsters.json"
		if monsters_file.exists():
			asm_file = self._generate_monster_assembly(monsters_file)
			if asm_file:
				generated_files.append(asm_file)

		# Generate item data assembly
		items_file = self.json_dir / "items.json"
		if items_file.exists():
			asm_file = self._generate_item_assembly(items_file)
			if asm_file:
				generated_files.append(asm_file)

		# Generate shop data assembly
		shops_file = self.json_dir / "shops.json"
		if shops_file.exists():
			asm_file = self._generate_shop_assembly(shops_file)
			if asm_file:
				generated_files.append(asm_file)

		# Generate spell data assembly
		spells_file = self.json_dir / "spells.json"
		if spells_file.exists():
			asm_file = self._generate_spell_assembly(spells_file)
			if asm_file:
				generated_files.append(asm_file)

		# Generate dialog data assembly
		dialogs_file = self.json_dir / "dialogs.json"
		if dialogs_file.exists():
			asm_file = self._generate_dialog_assembly(dialogs_file)
			if asm_file:
				generated_files.append(asm_file)

		# Generate graphics data assembly
		graphics_file = self.json_dir / "graphics.json"
		if graphics_file.exists():
			asm_file = self._generate_graphics_assembly(graphics_file)
			if asm_file:
				generated_files.append(asm_file)

		# Generate palette data assembly
		palettes_file = self.json_dir / "palettes.json"
		if palettes_file.exists():
			asm_file = self._generate_palette_assembly(palettes_file)
			if asm_file:
				generated_files.append(asm_file)

		# Generate map data assembly
		maps_file = self.json_dir / "maps.json"
		if maps_file.exists():
			asm_file = self._generate_map_assembly(maps_file)
			if asm_file:
				generated_files.append(asm_file)

		# Generate master include file
		master_file = self._generate_master_include(generated_files)
		if master_file:
			generated_files.append(master_file)

		console.print(f"[green]✅ Generated {len(generated_files)} assembly files:[/green]")
		for file_path in generated_files:
			console.print(f"	 📄 {file_path}")

		return generated_files

	def _generate_monster_assembly(self, json_file: Path) -> Optional[Path]:
		"""Generate monster data assembly"""
		try:
			with open(json_file, 'r', encoding='utf-8') as f:
				monsters = json.load(f)

			asm_lines = [
				"; Dragon Warrior Monster Data",
				"; Generated from edited JSON data",
				"; This replaces the original monster stats with edited values",
				"",
				".include \"Dragon_Warrior_Defines.asm\"",
				"",
				".segment \"MonsterData\"",
				"",
				"; Monster Statistics Table",
				"; Format: HP(2), STR(1), AGI(1), DMG(1), DODGE(1), SLEEP_RES(1), HURT_RES(1), EXP(2), GOLD(2), TYPE(1), SPRITE(1)",
				"MonsterStatsTable:"
			]

			for monster_id in sorted([int(k) for k in monsters.keys()]):
				monster = monsters[str(monster_id)]
				asm_lines.extend([
					f"",
					f"; {monster['name']} (ID: {monster_id})",
					f"Monster_{monster_id:02d}_Stats:",
					f"	.word ${monster['hp']:04X}			 ; HP: {monster['hp']}",
					f"	.byte ${monster['strength']:02X}			 ; Strength: {monster['strength']}",
					f"	.byte ${monster['agility']:02X}				; Agility: {monster['agility']}",
					f"	.byte ${monster['max_damage']:02X}			 ; Max Damage: {monster['max_damage']}",
					f"	.byte ${monster['dodge_rate']:02X}			 ; Dodge Rate: {monster['dodge_rate']}",
					f"	.byte ${monster['sleep_resistance']:02X}	 ; Sleep Resistance: {monster['sleep_resistance']}",
					f"	.byte ${monster['hurt_resistance']:02X}		; Hurt Resistance: {monster['hurt_resistance']}",
					f"	.word ${monster['experience']:04X}			 ; Experience: {monster['experience']}",
					f"	.word ${monster['gold']:04X}				 ; Gold: {monster['gold']}",
					f"	.byte ${monster['monster_type']:02X}		 ; Monster Type: {monster['monster_type']}",
					f"	.byte ${monster['sprite_id']:02X}			; Sprite ID: {monster['sprite_id']}"
				])

			# Add pointer table
			asm_lines.extend([
				"",
				"; Monster Stats Pointer Table",
				"MonsterStatsPointers:"
			])

			for monster_id in sorted([int(k) for k in monsters.keys()]):
				asm_lines.append(f"	.word Monster_{monster_id:02d}_Stats")

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "monster_data.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			console.print(f"[red]❌ Error generating monster assembly: {e}[/red]")
			return None

	def _generate_item_assembly(self, json_file: Path) -> Optional[Path]:
		"""Generate item data assembly"""
		try:
			with open(json_file, 'r', encoding='utf-8') as f:
				items = json.load(f)

			asm_lines = [
				"; Dragon Warrior Item Data",
				"; Generated from edited JSON data",
				"",
				".include \"Dragon_Warrior_Defines.asm\"",
				"",
				".segment \"ItemData\"",
				"",
				"; Item Statistics Table",
				"; Format: ATK(1), DEF(1), BUY_PRICE(2), SELL_PRICE(2), FLAGS(1), TYPE(1), SPRITE(1)",
				"ItemStatsTable:"
			]

			for item_id in sorted([int(k) for k in items.keys()]):
				item = items[str(item_id)]
				flags = (int(item['equippable']) | (int(item['useable']) << 1))

				asm_lines.extend([
					f"",
					f"; {item['name']} (ID: {item_id})",
					f"Item_{item_id:02d}_Stats:",
					f"	.byte ${item['attack_bonus']:02X}			; Attack Bonus: {item['attack_bonus']}",
					f"	.byte ${item['defense_bonus']:02X}			 ; Defense Bonus: {item['defense_bonus']}",
					f"	.word ${item['buy_price']:04X}				 ; Buy Price: {item['buy_price']}",
					f"	.word ${item['sell_price']:04X}				; Sell Price: {item['sell_price']}",
					f"	.byte ${flags:02X}							 ; Flags: Equip={item['equippable']}, Use={item['useable']}",
					f"	.byte ${item['item_type']:02X}				 ; Item Type: {item['item_type']}",
					f"	.byte ${item['sprite_id']:02X}				 ; Sprite ID: {item['sprite_id']}"
				])

			# Add pointer table
			asm_lines.extend([
				"",
				"; Item Stats Pointer Table",
				"ItemStatsPointers:"
			])

			for item_id in sorted([int(k) for k in items.keys()]):
				asm_lines.append(f"	.word Item_{item_id:02d}_Stats")

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "item_data.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			console.print(f"[red]❌ Error generating item assembly: {e}[/red]")
			return None

	def _generate_graphics_assembly(self, json_file: Path) -> Optional[Path]:
		"""Generate graphics data assembly from edited graphics"""
		try:
			with open(json_file, 'r', encoding='utf-8') as f:
				graphics = json.load(f)

			asm_lines = [
				"; Dragon Warrior Graphics Data",
				"; Generated from edited graphics",
				"",
				".include \"Dragon_Warrior_Defines.asm\"",
				"",
				".segment \"CHR_ROM\"",
				"",
				"; Graphics Tiles Data",
				"; Each tile is 8x8 pixels, 2 bits per pixel, 16 bytes total",
				"GraphicsTiles:"
			]

			for gfx_id in sorted([int(k) for k in graphics.keys()]):
				gfx = graphics[str(gfx_id)]

				asm_lines.extend([
					f"",
					f"; {gfx['name']} (ID: {gfx_id})",
					f"Tile_{gfx_id:03d}:"
				])

				# Convert tile data to assembly bytes
				tile_data = gfx['tile_data']
				if len(tile_data) >= 16:
					# First 8 bytes (plane 1)
					plane1 = tile_data[:8]
					plane1_str = ", ".join(f"${b:02X}" for b in plane1)
					asm_lines.append(f"	.byte {plane1_str}	; Plane 1")

					# Second 8 bytes (plane 2)
					plane2 = tile_data[8:16]
					plane2_str = ", ".join(f"${b:02X}" for b in plane2)
					asm_lines.append(f"	.byte {plane2_str}	; Plane 2")
				else:
					# Empty tile
					asm_lines.append(f"	.byte $00, $00, $00, $00, $00, $00, $00, $00	; Plane 1 (empty)")
					asm_lines.append(f"	.byte $00, $00, $00, $00, $00, $00, $00, $00	; Plane 2 (empty)")

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "graphics_data.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			console.print(f"[red]❌ Error generating graphics assembly: {e}[/red]")
			return None

	def _generate_palette_assembly(self, json_file: Path) -> Optional[Path]:
		"""Generate palette data assembly"""
		try:
			with open(json_file, 'r', encoding='utf-8') as f:
				palettes = json.load(f)

			asm_lines = [
				"; Dragon Warrior Palette Data",
				"; Generated from edited palettes",
				"",
				".include \"Dragon_Warrior_Defines.asm\"",
				"",
				".segment \"PaletteData\"",
				"",
				"; Palette Data Table",
				"; Each palette has 4 colors (NES standard)",
				"PaletteTable:"
			]

			for pal_id in sorted([int(k) for k in palettes.keys()]):
				palette = palettes[str(pal_id)]

				asm_lines.extend([
					f"",
					f"; {palette['name']} Palette (ID: {pal_id})",
					f"Palette_{pal_id:02d}:"
				])

				# Convert RGB to NES palette indices (simplified conversion)
				nes_colors = []
				for color in palette['colors']:
					# This is a simplified conversion - real implementation would use proper NES palette mapping
					nes_index = self._rgb_to_nes_index(color['r'], color['g'], color['b'])
					nes_colors.append(nes_index)

				colors_str = ", ".join(f"${color:02X}" for color in nes_colors)
				asm_lines.append(f"	.byte {colors_str}")

			# Add palette pointer table
			asm_lines.extend([
				"",
				"; Palette Pointer Table",
				"PalettePointers:"
			])

			for pal_id in sorted([int(k) for k in palettes.keys()]):
				asm_lines.append(f"	.word Palette_{pal_id:02d}")

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "palette_data.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			console.print(f"[red]❌ Error generating palette assembly: {e}[/red]")
			return None

	def _rgb_to_nes_index(self, r: int, g: int, b: int) -> int:
		"""Convert RGB color to nearest NES palette index (simplified)"""
		# This is a simplified conversion - real implementation would use proper color distance calculation
		# NES palette has 64 colors (0x00-0x3F)

		# Simple grayscale-based mapping for demonstration
		gray = int(0.299 * r + 0.587 * g + 0.114 * b)

		if gray < 64:
			return 0x0F	# Black
		elif gray < 128:
			return 0x00	# Dark gray
		elif gray < 192:
			return 0x10	# Light gray
		else:
			return 0x30	# White

	def _generate_shop_assembly(self, json_file: Path) -> Optional[Path]:
		"""Generate shop data assembly"""
		try:
			with open(json_file, 'r', encoding='utf-8') as f:
				shops = json.load(f)

			asm_lines = [
				"; Dragon Warrior Shop Data",
				"; Generated from edited shop data",
				"",
				".include \"Dragon_Warrior_Defines.asm\"",
				"",
				".segment \"ShopData\"",
				"",
				"ShopInventories:"
			]

			for shop_id in sorted([int(k) for k in shops.keys()]):
				shop = shops[str(shop_id)]

				asm_lines.extend([
					f"",
					f"; {shop['name']} (ID: {shop_id})",
					f"Shop_{shop_id:02d}:",
					f"	.byte ${len(shop['items']):02X}				; Item count"
				])

				# Add item IDs
				if shop['items']:
					items_per_line = 8
					items = shop['items']
					for i in range(0, len(items), items_per_line):
						line_items = items[i:i+items_per_line]
						items_str = ", ".join(f"${item:02X}" for item in line_items)
						asm_lines.append(f"	.byte {items_str}")

				# Add inn price if applicable
				if shop.get('inn_price'):
					asm_lines.append(f"	.word ${shop['inn_price']:04X}			 ; Inn price")

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "shop_data.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			console.print(f"[red]❌ Error generating shop assembly: {e}[/red]")
			return None

	def _generate_spell_assembly(self, json_file: Path) -> Optional[Path]:
		"""Generate spell data assembly"""
		try:
			with open(json_file, 'r', encoding='utf-8') as f:
				spells = json.load(f)

			asm_lines = [
				"; Dragon Warrior Spell Data",
				"; Generated from edited spell data",
				"",
				".include \"Dragon_Warrior_Defines.asm\"",
				"",
				".segment \"SpellData\"",
				"",
				"SpellDataTable:"
			]

			for spell_id in sorted([int(k) for k in spells.keys()]):
				spell = spells[str(spell_id)]

				asm_lines.extend([
					f"",
					f"; {spell['name']} (ID: {spell_id})",
					f"Spell_{spell_id:02d}_Data:",
					f"	.byte ${spell['mp_cost']:02X}				; MP Cost: {spell['mp_cost']}",
					f"	.byte ${spell['power']:02X}					; Power: {spell['power']}",
					f"	.byte ${spell['learn_level']:02X}			; Learn Level: {spell['learn_level']}",
					f"	.byte ${spell['spell_type']:02X}			 ; Spell Type: {spell['spell_type']}"
				])

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "spell_data.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			console.print(f"[red]❌ Error generating spell assembly: {e}[/red]")
			return None

	def _generate_dialog_assembly(self, json_file: Path) -> Optional[Path]:
		"""Generate dialog data assembly"""
		try:
			with open(json_file, 'r', encoding='utf-8') as f:
				dialogs = json.load(f)

			asm_lines = [
				"; Dragon Warrior Dialog Data",
				"; Generated from edited dialog",
				"",
				".include \"Dragon_Warrior_Defines.asm\"",
				"",
				".segment \"DialogData\"",
				"",
				"DialogTable:"
			]

			for dialog_id in sorted([int(k) for k in dialogs.keys()]):
				dialog = dialogs[str(dialog_id)]

				asm_lines.extend([
					f"",
					f"; {dialog['npc_name']} - {dialog['location']} (ID: {dialog_id})",
					f"Dialog_{dialog_id:02d}:"
				])

				# Convert text to byte array (simplified - real implementation would handle compression)
				text = dialog['text']
				text_bytes = [ord(c) for c in text if ord(c) < 128]	# ASCII only for simplicity
				text_bytes.append(0)	# Null terminator

				# Write text bytes
				bytes_per_line = 16
				for i in range(0, len(text_bytes), bytes_per_line):
					line_bytes = text_bytes[i:i+bytes_per_line]
					bytes_str = ", ".join(f"${b:02X}" for b in line_bytes)
					asm_lines.append(f"	.byte {bytes_str}")

			# Add dialog pointer table
			asm_lines.extend([
				"",
				"; Dialog Pointer Table",
				"DialogPointers:"
			])

			for dialog_id in sorted([int(k) for k in dialogs.keys()]):
				asm_lines.append(f"	.word Dialog_{dialog_id:02d}")

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "dialog_data.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			console.print(f"[red]❌ Error generating dialog assembly: {e}[/red]")
			return None

	def _generate_map_assembly(self, json_file: Path) -> Optional[Path]:
		"""Generate map data assembly"""
		try:
			with open(json_file, 'r', encoding='utf-8') as f:
				maps = json.load(f)

			asm_lines = [
				"; Dragon Warrior Map Data",
				"; Generated from edited maps",
				"",
				".include \"Dragon_Warrior_Defines.asm\"",
				"",
				".segment \"MapData\"",
				"",
				"MapDataTable:"
			]

			for map_id in sorted([int(k) for k in maps.keys()]):
				map_data = maps[str(map_id)]

				asm_lines.extend([
					f"",
					f"; {map_data['name']} (ID: {map_id})",
					f"Map_{map_id:02d}_Header:",
					f"	.byte ${map_data['width']:02X}				 ; Width: {map_data['width']}",
					f"	.byte ${map_data['height']:02X}				; Height: {map_data['height']}",
					f"	.byte ${map_data['music_id']:02X}			; Music ID: {map_data['music_id']}",
					f"	.byte ${map_data['palette_id']:02X}			; Palette ID: {map_data['palette_id']}",
					f"",
					f"Map_{map_id:02d}_Tiles:"
				])

				# Convert tile data (simplified - real implementation would compress)
				tiles = map_data['tiles']
				for y, row in enumerate(tiles):
					if y >= 32:	# Limit output size for demonstration
						break
					row_data = []
					for x, tile in enumerate(row):
						if x >= 32:	# Limit output size
							break
						tile_id = tile.get('tile_id', 0)
						row_data.append(tile_id)

					if row_data:
						row_str = ", ".join(f"${tid:02X}" for tid in row_data)
						asm_lines.append(f"	.byte {row_str}")

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "map_data.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			console.print(f"[red]❌ Error generating map assembly: {e}[/red]")
			return None

	def _generate_master_include(self, generated_files: List[Path]) -> Optional[Path]:
		"""Generate master include file"""
		try:
			asm_lines = [
				"; Dragon Warrior Asset Reinsertion Master Include",
				"; Generated by Asset Reinsertion System",
				"; Include this file in your main assembly to use edited assets",
				"",
				".ifndef ASSET_REINSERTION_INCLUDED",
				".define ASSET_REINSERTION_INCLUDED",
				""
			]

			# Add includes for all generated files
			for file_path in generated_files:
				if file_path.name != "asset_reinsertion.asm":	# Don't include self
					asm_lines.append(f".include \"{file_path.name}\"")

			asm_lines.extend([
				"",
				".endif ; ASSET_REINSERTION_INCLUDED"
			])

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "asset_reinsertion.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			console.print(f"[red]❌ Error generating master include: {e}[/red]")
			return None

@click.command()
@click.argument('assets_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='build/generated', help='Output directory for assembly')
def reinsert_assets(assets_dir: str, output_dir: str):
	"""Generate assembly code for reinserting edited assets"""

	reinserter = AssetReinserter(assets_dir, output_dir)
	generated_files = reinserter.generate_all_assembly()

	console.print(f"\n[green]🎯 Asset reinsertion code generation complete![/green]")
	console.print(f"[cyan]Include 'asset_reinsertion.asm' in your main assembly file.[/cyan]")

if __name__ == "__main__":
	reinsert_assets()
