#!/usr/bin/env python3
"""
Dragon Warrior Graphics Index Generator
Creates visual index/catalog of all extracted graphics
"""

from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
from rich.console import Console
import json

console = Console()

def create_graphics_index(base_dir: str):
	"""Create visual index of extracted graphics"""
	base_path = Path(base_dir)

	console.print("[cyan]Creating graphics index...[/cyan]\n")

	# Load palette data
	palette_file = base_path / "palettes.json"
	if palette_file.exists():
		with open(palette_file) as f:
			palettes = json.load(f)

		console.print(f"[green]✓ Found {len(palettes)} palettes[/green]")

		# Create palette catalog
		create_palette_catalog(base_path, palettes)

	# Create tile index sheets
	console.print("[cyan]Creating tile index sheets...[/cyan]")

	for bank_num in range(2):
		bank_dir = base_path / f"chr_bank_{bank_num}"
		if bank_dir.exists():
			tile_count = len(list(bank_dir.glob("tile_*.png")))
			console.print(f"  Bank {bank_num}: {tile_count} tiles")

	# Check monsters
	monster_dir = base_path / "monsters"
	if monster_dir.exists():
		monster_count = len([d for d in monster_dir.iterdir() if d.is_dir()])
		console.print(f"[green]✓ Found {monster_count} monsters[/green]")

		# Create monster catalog
		create_monster_catalog(monster_dir)

	console.print("\n[bold green]✓ Graphics index complete![/bold green]")

def create_palette_catalog(base_path: Path, palettes: dict):
	"""Create visual catalog of all palettes"""
	swatch_width = 256
	swatch_height = 64
	padding = 20

	# Calculate catalog size
	num_palettes = len(palettes)
	catalog_width = swatch_width + padding * 2
	catalog_height = (swatch_height + padding) * num_palettes + padding

	# Create catalog image
	catalog = Image.new('RGB', (catalog_width, catalog_height), (32, 32, 32))
	draw = ImageDraw.Draw(catalog)

	y_pos = padding
	for name, palette_data in palettes.items():
		# Draw palette swatch
		for i, color_rgb in enumerate(palette_data['rgb_colors']):
			x1 = padding + i * 64
			y1 = y_pos
			x2 = x1 + 64
			y2 = y1 + swatch_height

			draw.rectangle([x1, y1, x2, y2], fill=tuple(color_rgb))

		# Draw palette name
		text_y = y_pos + swatch_height + 5
		draw.text((padding, text_y), name, fill=(255, 255, 255))

		# Draw NES indices
		indices_text = f"NES: {' '.join(f'{i:02X}' for i in palette_data['nes_indices'])}"
		draw.text((padding + 150, text_y), indices_text, fill=(200, 200, 200))

		y_pos += swatch_height + padding

	catalog_path = base_path / "palette_catalog.png"
	catalog.save(catalog_path)
	console.print(f"[green]  Saved: palette_catalog.png[/green]")

def create_monster_catalog(monster_dir: Path):
	"""Create visual catalog of monsters"""
	# Load monster database
	db_file = monster_dir / "monsters_database.json"
	if not db_file.exists():
		return

	with open(db_file) as f:
		monsters = json.load(f)

	# Create simple list catalog
	catalog_width = 800
	catalog_height = 40 * len(monsters) + 100

	catalog = Image.new('RGB', (catalog_width, catalog_height), (16, 16, 16))
	draw = ImageDraw.Draw(catalog)

	# Title
	draw.text((20, 20), "Dragon Warrior Monster Catalog", fill=(255, 255, 255))
	draw.text((20, 45), f"Total Monsters: {len(monsters)}", fill=(200, 200, 200))

	y_pos = 80
	for monster in monsters:
		# Monster name
		draw.text((20, y_pos), f"{monster['id']:02d}. {monster['name']}", fill=(255, 255, 255))

		# Palette colors
		x_pos = 300
		for color_rgb in monster['palette_rgb']:
			draw.rectangle([x_pos, y_pos, x_pos + 30, y_pos + 30], fill=tuple(color_rgb))
			x_pos += 35

		y_pos += 40

	catalog_path = monster_dir / "monster_catalog.png"
	catalog.save(catalog_path)
	console.print(f"[green]  Saved: monsters/monster_catalog.png[/green]")

def main():
	import sys
	if len(sys.argv) < 2:
		base_dir = "extracted_assets/graphics_comprehensive"
	else:
		base_dir = sys.argv[1]

	create_graphics_index(base_dir)

if __name__ == "__main__":
	main()
