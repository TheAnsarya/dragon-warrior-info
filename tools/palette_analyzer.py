#!/usr/bin/env python3
"""
NES Palette Analyzer for Dragon Warrior

Analyze and optimize NES palette usage.

Features:
- Extract palettes from CHR data
- Identify unused palette slots
- Suggest palette optimizations
- Generate palette swatches
- Analyze color frequency

Usage:
	python tools/palette_analyzer.py
	python tools/palette_analyzer.py --export-swatches
	python tools/palette_analyzer.py --suggest-optimizations

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
from collections import Counter

try:
	from PIL import Image, ImageDraw
except ImportError:
	print("ERROR: PIL/Pillow is required")
	print("Install with: pip install pillow")
	sys.exit(1)

# Default paths
DEFAULT_ROM = "roms/dragon_warrior.nes"
DEFAULT_OUTPUT = "output/palettes"

# NES standard palette (64 colors)
NES_PALETTE = [
	(124, 124, 124), (0, 0, 252), (0, 0, 188), (68, 40, 188),
	(148, 0, 132), (168, 0, 32), (168, 16, 0), (136, 20, 0),
	(80, 48, 0), (0, 120, 0), (0, 104, 0), (0, 88, 0),
	(0, 64, 88), (0, 0, 0), (0, 0, 0), (0, 0, 0),
	(188, 188, 188), (0, 120, 248), (0, 88, 248), (104, 68, 252),
	(216, 0, 204), (228, 0, 88), (248, 56, 0), (228, 92, 16),
	(172, 124, 0), (0, 184, 0), (0, 168, 0), (0, 168, 68),
	(0, 136, 136), (0, 0, 0), (0, 0, 0), (0, 0, 0),
	(248, 248, 248), (60, 188, 252), (104, 136, 252), (152, 120, 248),
	(248, 120, 248), (248, 88, 152), (248, 120, 88), (252, 160, 68),
	(248, 184, 0), (184, 248, 24), (88, 216, 84), (88, 248, 152),
	(0, 232, 216), (120, 120, 120), (0, 0, 0), (0, 0, 0),
	(252, 252, 252), (164, 228, 252), (184, 184, 248), (216, 184, 248),
	(248, 184, 248), (248, 164, 192), (240, 208, 176), (252, 224, 168),
	(248, 216, 120), (216, 248, 120), (184, 248, 184), (184, 248, 216),
	(0, 252, 252), (248, 216, 248), (0, 0, 0), (0, 0, 0)
]


class PaletteAnalyzer:
	"""Analyze NES palettes"""

	# Dragon Warrior palette definitions (from ROM)
	DW_PALETTES = {
		"background": {
			0: [0x0F, 0x30, 0x27, 0x17],  # Default background
			1: [0x0F, 0x30, 0x11, 0x21],  # Caves/dungeons
			2: [0x0F, 0x30, 0x16, 0x26],  # Castle
			3: [0x0F, 0x30, 0x12, 0x22],  # Town
		},
		"sprite": {
			0: [0x0F, 0x30, 0x27, 0x17],  # Hero
			1: [0x0F, 0x16, 0x27, 0x30],  # Monsters (green)
			2: [0x0F, 0x12, 0x22, 0x30],  # Monsters (blue)
			3: [0x0F, 0x06, 0x16, 0x26],  # Monsters (red)
			4: [0x0F, 0x00, 0x10, 0x30],  # Monsters (gray)
			5: [0x0F, 0x28, 0x18, 0x38],  # Monsters (yellow)
			6: [0x0F, 0x02, 0x12, 0x22],  # Monsters (purple)
			7: [0x0F, 0x14, 0x24, 0x34],  # Monsters (pink)
		}
	}

	def __init__(self, rom_path: str, output_dir: str):
		"""
		Initialize palette analyzer

		Args:
			rom_path: ROM file path
			output_dir: Output directory
		"""
		self.rom_path = Path(rom_path)
		self.output_dir = Path(output_dir)
		self.rom_data = None

	def load_rom(self) -> bool:
		"""Load ROM file"""
		if not self.rom_path.exists():
			print(f"❌ ROM not found: {self.rom_path}")
			return False

		with open(self.rom_path, 'rb') as f:
			self.rom_data = bytearray(f.read())

		print(f"✓ Loaded ROM: {len(self.rom_data)} bytes")
		return True

	def extract_palettes(self) -> Dict[str, List[List[int]]]:
		"""
		Extract palette data from ROM

		Returns:
			Dictionary of palette types and values
		"""
		if not self.rom_data:
			return {}

		# For Dragon Warrior, palettes are at specific addresses
		# Background palettes: 0x1CDD0 - 0x1CDDF
		# Sprite palettes: 0x1CDE0 - 0x1CDFF

		palettes = {
			'background': [],
			'sprite': []
		}

		# Extract background palettes (4 palettes × 4 bytes)
		bg_offset = 0x1CDD0
		for i in range(4):
			palette = []
			for j in range(4):
				palette.append(self.rom_data[bg_offset + i * 4 + j])
			palettes['background'].append(palette)

		# Extract sprite palettes (8 palettes × 4 bytes)
		spr_offset = 0x1CDE0
		for i in range(8):
			palette = []
			for j in range(4):
				palette.append(self.rom_data[spr_offset + i * 4 + j])
			palettes['sprite'].append(palette)

		return palettes

	def get_color_name(self, nes_color: int) -> str:
		"""
		Get descriptive name for NES color

		Args:
			nes_color: NES palette index (0-63)

		Returns:
			Color name string
		"""
		color_names = {
			0x0F: "Black",
			0x00: "Dark Gray",
			0x10: "Light Gray",
			0x20: "Light Gray 2",
			0x30: "White",
			0x01: "Blue",
			0x11: "Light Blue",
			0x21: "Sky Blue",
			0x02: "Dark Purple",
			0x12: "Purple",
			0x22: "Light Purple",
			0x06: "Dark Red",
			0x16: "Red",
			0x26: "Light Red",
			0x07: "Brown",
			0x17: "Orange",
			0x27: "Yellow-Orange",
			0x08: "Dark Green",
			0x18: "Green",
			0x28: "Yellow",
			0x38: "Light Yellow",
			0x14: "Pink",
			0x24: "Light Pink",
			0x34: "Lightest Pink",
		}

		return color_names.get(nes_color, f"Color ${nes_color:02X}")

	def analyze_color_usage(self, palettes: Dict[str, List[List[int]]]) -> Dict:
		"""
		Analyze color usage across all palettes

		Args:
			palettes: Palette dictionary

		Returns:
			Analysis results
		"""
		all_colors = []

		for pal_type, pal_list in palettes.items():
			for palette in pal_list:
				all_colors.extend(palette)

		color_counts = Counter(all_colors)

		# Find most/least common
		most_common = color_counts.most_common(5)
		least_common = color_counts.most_common()[-5:]

		# Find unused colors (from NES palette)
		used_colors = set(all_colors)
		all_nes_colors = set(range(64))
		unused_colors = all_nes_colors - used_colors

		return {
			'total_colors_used': len(used_colors),
			'total_color_slots': len(all_colors),
			'most_common': most_common,
			'least_common': least_common,
			'unused_nes_colors': sorted(unused_colors),
			'color_frequency': dict(color_counts)
		}

	def find_duplicate_palettes(self, palettes: Dict[str, List[List[int]]]) -> List:
		"""
		Find duplicate palette definitions

		Args:
			palettes: Palette dictionary

		Returns:
			List of duplicate palette pairs
		"""
		duplicates = []

		for pal_type, pal_list in palettes.items():
			for i, pal1 in enumerate(pal_list):
				for j, pal2 in enumerate(pal_list[i+1:], start=i+1):
					if pal1 == pal2:
						duplicates.append({
							'type': pal_type,
							'palette1': i,
							'palette2': j,
							'colors': pal1
						})

		return duplicates

	def suggest_optimizations(self, palettes: Dict, analysis: Dict) -> List[str]:
		"""
		Suggest palette optimizations

		Args:
			palettes: Palette dictionary
			analysis: Analysis results

		Returns:
			List of suggestions
		"""
		suggestions = []

		# Check for unused colors
		if analysis['unused_nes_colors']:
			suggestions.append(
				f"• {len(analysis['unused_nes_colors'])} NES colors never used - "
				f"consider using for new graphics"
			)

		# Check for duplicate palettes
		duplicates = self.find_duplicate_palettes(palettes)
		if duplicates:
			suggestions.append(
				f"• {len(duplicates)} duplicate palette(s) found - "
				f"could merge to free slots"
			)

		# Check color frequency
		least_used = [c for c, count in analysis['most_common'][-3:] if count == 1]
		if least_used:
			suggestions.append(
				f"• {len(least_used)} color(s) used only once - "
				f"consider consolidating"
			)

		# Palette slot usage
		bg_used = len(palettes.get('background', []))
		spr_used = len(palettes.get('sprite', []))
		if bg_used < 4:
			suggestions.append(
				f"• {4 - bg_used} unused background palette slot(s) available"
			)
		if spr_used < 8:
			suggestions.append(
				f"• {8 - spr_used} unused sprite palette slot(s) available"
			)

		return suggestions

	def export_palette_swatch(self, palettes: Dict[str, List[List[int]]]):
		"""
		Export palette swatches as images

		Args:
			palettes: Palette dictionary
		"""
		self.output_dir.mkdir(parents=True, exist_ok=True)

		# Swatch dimensions
		swatch_size = 40
		padding = 5

		for pal_type, pal_list in palettes.items():
			# Calculate image size
			width = 4 * swatch_size + 5 * padding
			height = len(pal_list) * (swatch_size + padding) + padding

			# Create image
			img = Image.new('RGB', (width, height), (255, 255, 255))
			draw = ImageDraw.Draw(img)

			# Draw each palette
			for i, palette in enumerate(pal_list):
				y = i * (swatch_size + padding) + padding

				for j, color_idx in enumerate(palette):
					x = j * (swatch_size + padding) + padding

					# Get RGB color
					if color_idx < len(NES_PALETTE):
						rgb = NES_PALETTE[color_idx]
					else:
						rgb = (0, 0, 0)

					# Draw swatch
					draw.rectangle(
						[x, y, x + swatch_size, y + swatch_size],
						fill=rgb,
						outline=(0, 0, 0)
					)

			# Save
			output_file = self.output_dir / f"{pal_type}_palettes.png"
			img.save(output_file)
			print(f"✓ Exported {pal_type} palette swatch: {output_file}")

	def export_color_usage_chart(self, analysis: Dict):
		"""
		Export color usage chart

		Args:
			analysis: Analysis results
		"""
		# Create bar chart of color usage
		freq = analysis['color_frequency']

		# Sort by frequency
		sorted_colors = sorted(freq.items(), key=lambda x: x[1], reverse=True)

		# Chart dimensions
		bar_width = 10
		bar_max_height = 200
		padding = 20

		width = len(sorted_colors) * (bar_width + 2) + 2 * padding
		height = bar_max_height + 2 * padding + 30

		img = Image.new('RGB', (width, height), (255, 255, 255))
		draw = ImageDraw.Draw(img)

		max_count = max(freq.values())

		for i, (color, count) in enumerate(sorted_colors):
			x = i * (bar_width + 2) + padding
			bar_height = int((count / max_count) * bar_max_height)
			y = height - padding - 30 - bar_height

			# Get color
			if color < len(NES_PALETTE):
				rgb = NES_PALETTE[color]
			else:
				rgb = (128, 128, 128)

			# Draw bar
			draw.rectangle(
				[x, y, x + bar_width, height - padding - 30],
				fill=rgb,
				outline=(0, 0, 0)
			)

		output_file = self.output_dir / "color_usage.png"
		img.save(output_file)
		print(f"✓ Exported color usage chart: {output_file}")

	def generate_report(self, palettes: Dict, analysis: Dict, suggestions: List[str]):
		"""
		Generate analysis report

		Args:
			palettes: Palette dictionary
			analysis: Analysis results
			suggestions: Optimization suggestions
		"""
		print("\n" + "=" * 70)
		print("NES Palette Analysis Report")
		print("=" * 70)

		print("\n--- Palette Counts ---")
		for pal_type, pal_list in palettes.items():
			print(f"{pal_type.capitalize()}: {len(pal_list)} palette(s)")

		print("\n--- Color Usage ---")
		print(f"Total unique colors used: {analysis['total_colors_used']} / 64")
		print(f"Total color slots: {analysis['total_color_slots']}")

		print("\n--- Most Common Colors ---")
		for color, count in analysis['most_common']:
			name = self.get_color_name(color)
			print(f"  ${color:02X} ({name}): {count} times")

		print("\n--- Palette Definitions ---")
		for pal_type, pal_list in palettes.items():
			print(f"\n{pal_type.capitalize()} Palettes:")
			for i, palette in enumerate(pal_list):
				colors = ', '.join([f"${c:02X}" for c in palette])
				names = ' / '.join([self.get_color_name(c) for c in palette])
				print(f"  Palette {i}: [{colors}]")
				print(f"             [{names}]")

		if suggestions:
			print("\n--- Optimization Suggestions ---")
			for suggestion in suggestions:
				print(suggestion)

		print("\n" + "=" * 70)


def main():
	"""Main entry point"""
	parser = argparse.ArgumentParser(
		description='Analyze NES palette usage in Dragon Warrior',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  # Basic analysis
  python tools/palette_analyzer.py

  # Export palette swatches
  python tools/palette_analyzer.py --export-swatches

  # Show optimization suggestions
  python tools/palette_analyzer.py --suggest-optimizations
		"""
	)

	parser.add_argument(
		'--rom',
		default=DEFAULT_ROM,
		help=f'ROM file path (default: {DEFAULT_ROM})'
	)

	parser.add_argument(
		'--output',
		default=DEFAULT_OUTPUT,
		help=f'Output directory (default: {DEFAULT_OUTPUT})'
	)

	parser.add_argument(
		'--export-swatches',
		action='store_true',
		help='Export palette swatches as images'
	)

	parser.add_argument(
		'--export-chart',
		action='store_true',
		help='Export color usage chart'
	)

	parser.add_argument(
		'--suggest-optimizations',
		action='store_true',
		help='Show optimization suggestions'
	)

	args = parser.parse_args()

	# Initialize analyzer
	analyzer = PaletteAnalyzer(args.rom, args.output)

	# Load ROM
	if not analyzer.load_rom():
		return 1

	# Extract palettes
	palettes = analyzer.extract_palettes()

	# Analyze
	analysis = analyzer.analyze_color_usage(palettes)

	# Generate suggestions
	suggestions = []
	if args.suggest_optimizations:
		suggestions = analyzer.suggest_optimizations(palettes, analysis)

	# Generate report
	analyzer.generate_report(palettes, analysis, suggestions)

	# Export visuals
	if args.export_swatches:
		analyzer.export_palette_swatch(palettes)

	if args.export_chart:
		analyzer.export_color_usage_chart(analysis)

	return 0


if __name__ == '__main__':
	sys.exit(main())
