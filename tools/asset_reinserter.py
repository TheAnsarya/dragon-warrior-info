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

	def generate_all_assembly(self, extract_defaults: bool = False):
		"""Generate all assembly files for asset reinsertion"""
		console.print("[blue]Generating assembly code for asset reinsertion...[/blue]\n")

		generated_files = []

		# Extract default assets if requested
		if extract_defaults:
			default_files = self.extract_default_assets()
			generated_files.extend(default_files)

		# Generate edited asset files
		edited_files = self._generate_edited_assets()
		generated_files.extend(edited_files)

		# Generate master include file
		has_edited_assets = len(edited_files) > 0
		master_file = self._generate_master_include(edited_files, use_edited_assets=has_edited_assets)
		if master_file:
			generated_files.append(master_file)

		print(f"Generated {len(generated_files)} assembly files:")
		for file_path in generated_files:
			print(f"   {file_path}")

		return generated_files

	def _generate_edited_assets(self) -> List[Path]:
		"""Generate assembly files for edited assets"""
		generated_files = []

		# Generate monster data assembly (prefer _verified version)
		monsters_file = self.json_dir / "monsters_verified.json"
		if not monsters_file.exists():
			monsters_file = self.json_dir / "monsters.json"
		if monsters_file.exists():
			asm_file = self._generate_monster_assembly(monsters_file)
			if asm_file:
				generated_files.append(asm_file)

		# Generate item data assembly (prefer _corrected version)
		items_file = self.json_dir / "items_corrected.json"
		if not items_file.exists():
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

		return generated_files

	def _generate_monster_assembly(self, json_file: Path) -> Optional[Path]:
		"""Generate monster data assembly that replaces EnemyStatsTable"""
		try:
			with open(json_file, 'r', encoding='utf-8') as f:
				monsters = json.load(f)

			asm_lines = [
				"; Dragon Warrior Monster Data Replacement",
				"; This file replaces the original EnemyStatsTable in Bank01.asm",
				"; Generated from edited JSON data",
				"",
				"; Monster Statistics Table",
				"; Format matches original Dragon Warrior: Att(1), Def(1), HP(1), Spel(1), Agi(1), Mdef(1), Exp(1), Gld(1), + 8 unused bytes",
				"EnemyStatsTable:"
			]

			# Generate monster entries in original Dragon Warrior format
			for monster_id in sorted([int(k) for k in monsters.keys()]):
				monster = monsters[str(monster_id)]

				# Convert JSON data to Dragon Warrior format
				att = min(255, monster.get('strength', 5))
				def_val = min(255, monster.get('defense', 3))
				hp = min(255, monster.get('hp', 3))
				spel = min(255, monster.get('spell_power', 0))
				agi = min(255, monster.get('agility', 15))
				mdef = min(255, monster.get('magic_defense', 1))
				exp = min(255, monster.get('experience', 1))
				gld = min(255, monster.get('gold', 2))

				# Calculate label address (0x9E4B is start of EnStatTbl)
				label_addr = 0x9E4B + (monster_id * 16)

				asm_lines.extend([
					f";",
					f";Enemy ${monster_id:02X}-{monster['name']}.",
					f";             Att  Def   HP  Spel Agi  Mdef Exp  Gld   |--------------Unused--------------|",
					f"L{label_addr:04X}:  .byte ${att:02X}, ${def_val:02X}, ${hp:02X}, ${spel:02X}, ${agi:02X}, ${mdef:02X}, ${exp:02X}, ${gld:02X}, $69, $40, $4A, $4D, $FA, $FA, $FA, $FA"
				])

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
					f"	.byte ${item.get('attack_power', item.get('attack_bonus', 0)):02X}			; Attack Power: {item.get('attack_power', item.get('attack_bonus', 0))}",
					f"	.byte ${item.get('defense_power', item.get('defense_bonus', 0)):02X}			 ; Defense Power: {item.get('defense_power', item.get('defense_bonus', 0))}",
					f"	.word ${item['buy_price']:04X}				 ; Buy Price: {item['buy_price']}",
					f"	.word ${item['sell_price']:04X}				; Sell Price: {item['sell_price']}",
					f"	.byte ${flags:02X}							 ; Flags: Equip={item['equippable']}, Use={item['useable']}",
					f"	.byte ${int(item['item_type']):02X}				 ; Item Type: {int(item['item_type'])}",
					f"	.byte ${int(item.get('sprite_id', 0)):02X}				 ; Sprite ID: {int(item.get('sprite_id', 0))}"
				])			# Add pointer table
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

				# Handle both old format ('items' with raw bytes) and new format ('item_indices')
				items = shop.get('item_indices', shop.get('items', []))

				asm_lines.extend([
					f"",
					f"; {shop['name']} (ID: {shop_id})",
					f"Shop_{shop_id:02d}:",
					f"	.byte ${len(items):02X}				; Item count"
				])

				# Add item IDs
				if items:
					items_per_line = 8
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
				"; Spell MP Cost Table",
				"SpellMPCosts:"
			]

			for spell_id in sorted([int(k) for k in spells.keys()]):
				spell = spells[str(spell_id)]
				asm_lines.append(f"	.byte ${spell['mp_cost']:02X}				; {spell['name']}: {spell['mp_cost']} MP")

			# Add additional spell metadata if available
			asm_lines.extend([
				"",
				"; Spell Effect Types",
				"SpellEffectTypes:"
			])

			for spell_id in sorted([int(k) for k in spells.keys()]):
				spell = spells[str(spell_id)]
				effect_type = spell.get('effect_type', 'unknown')
				# Map effect types to numeric IDs
				effect_map = {
					'heal': 0, 'damage': 1, 'status': 2,
					'teleport': 3, 'field': 4, 'unknown': 255
				}
				effect_id = effect_map.get(effect_type, 255)
				asm_lines.append(f"	.byte ${effect_id:02X}				; {spell['name']}: {effect_type}")

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "spell_data.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			print(f"Error generating spell assembly: {e}")
			import traceback
			traceback.print_exc()
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

	def extract_default_assets(self, source_dir: str = "source_files", default_dir: str = "build/default_assets"):
		"""Extract original data tables from source files into default asset includes"""
		console.print("[blue]📎 Extracting default assets from source files...[/blue]\n")

		default_path = Path(default_dir)
		default_path.mkdir(parents=True, exist_ok=True)
		source_path = Path(source_dir)

		generated_defaults = []

		# Extract monster data from Bank01.asm
		bank01_file = source_path / "Bank01.asm"
		if bank01_file.exists():
			default_monster_file = self._extract_monster_defaults(bank01_file, default_path)
			if default_monster_file:
				generated_defaults.append(default_monster_file)

		# Extract other data tables as needed
		# TODO: Add item data, shop data, spell data extraction

		console.print(f"[green]✅ Extracted {len(generated_defaults)} default asset files:[/green]")
		for file_path in generated_defaults:
			console.print(f"	 📄 {file_path}")

		return generated_defaults

	def _extract_monster_defaults(self, bank01_file: Path, default_dir: Path) -> Optional[Path]:
		"""Extract original EnStatTbl from Bank01.asm"""
		try:
			with open(bank01_file, 'r', encoding='utf-8') as f:
				content = f.read()

			# Find the EnStatTbl section
			lines = content.split('\n')
			enstattbl_start = -1
			enstattbl_end = -1

			for i, line in enumerate(lines):
				if 'EnStatTbl:' in line:
					enstattbl_start = i + 1  # Start AFTER the label
				elif enstattbl_start != -1 and line.strip().startswith(';----------------------------------------------------------------------------------------------------'):
					# Found the separator line that marks end of monster table
					enstattbl_end = i
					break

			if enstattbl_start == -1:
				console.print("[yellow]⚠️  Could not find EnStatTbl in Bank01.asm[/yellow]")
				return None

			if enstattbl_end == -1:
				console.print("[yellow]⚠️  Could not find end of monster table[/yellow]")
				return None

			# Extract the table content (excluding the label)
			table_lines = lines[enstattbl_start:enstattbl_end]

			# Create default monster data file
			asm_lines = [
				"; Dragon Warrior Default Monster Data",
				"; Extracted from original Bank01.asm",
				"; This is the original EnStatTbl data (without label)",
				""
			] + table_lines

			asm_content = "\n".join(asm_lines)

			default_file = default_dir / "default_monster_data.asm"
			with open(default_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return default_file

		except Exception as e:
			console.print(f"[red]❌ Error extracting monster defaults: {e}[/red]")
			return None

	def _generate_master_include(self, generated_files: List[Path], use_edited_assets: bool = True) -> Optional[Path]:
		"""Generate master include file with conditional asset loading"""
		try:
			asm_lines = [
				"; Dragon Warrior Asset System Master Include",
				"; Generated by Asset Reinsertion System",
				"; Conditionally includes edited or default assets",
				"",
				".ifndef DRAGON_WARRIOR_ASSETS_INCLUDED",
				".define DRAGON_WARRIOR_ASSETS_INCLUDED",
				""
			]

			if use_edited_assets:
				asm_lines.extend([
					"; Using edited/modified assets",
					".define USE_EDITED_ASSETS"
				])

				# Add includes for edited files
				for file_path in generated_files:
					if file_path.name != "dragon_warrior_assets.asm" and file_path.suffix == ".asm":
						asm_lines.append(f".include \"{file_path.name}\"")
			else:
				asm_lines.extend([
					"; Using default/original assets",
					".include \"default_assets/default_monster_data.asm\"",
					".include \"default_assets/default_item_data.asm\"",
					".include \"default_assets/default_shop_data.asm\"",
					".include \"default_assets/default_spell_data.asm\"",
					".include \"default_assets/default_graphics_data.asm\""
				])

			asm_lines.extend([
				"",
				".endif ; DRAGON_WARRIOR_ASSETS_INCLUDED"
			])

			asm_content = "\n".join(asm_lines)

			output_file = self.output_dir / "dragon_warrior_assets.asm"
			with open(output_file, 'w', encoding='utf-8') as f:
				f.write(asm_content)

			return output_file

		except Exception as e:
			console.print(f"[red]❌ Error generating master include: {e}[/red]")
			return None

@click.command()
@click.argument('assets_dir', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='build/generated', help='Output directory for assembly')
@click.option('--extract-defaults', is_flag=True, help='Extract default assets from source files')
def reinsert_assets(assets_dir: str, output_dir: str, extract_defaults: bool):
	"""Generate assembly code for reinserting edited assets"""

	reinserter = AssetReinserter(assets_dir, output_dir)
	generated_files = reinserter.generate_all_assembly(extract_defaults=extract_defaults)

	print(f"\nAsset reinsertion code generation complete!")
	print(f"Include 'dragon_warrior_assets.asm' in your main assembly file.")
	if extract_defaults:
		print(f"Default assets extracted to build/default_assets/")

if __name__ == "__main__":
	reinsert_assets()
