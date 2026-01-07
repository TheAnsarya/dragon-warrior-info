#!/usr/bin/env python3
"""
Dragon Warrior CHR Graphics Validator

Validates PNG graphics for NES CHR compatibility:
- Image dimensions must be multiples of 8
- Each 8x8 tile can have at most 4 colors
- Reports any tiles that violate these constraints

Usage:
	python chr_validator.py image.png
	python chr_validator.py --dir assets/graphics/
"""

import argparse
import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
from pathlib import Path
from typing import List, Tuple, Set

try:
	from PIL import Image
except ImportError:
	print("Error: Pillow is required. Install with: pip install pillow")
	sys.exit(1)


class CHRValidator:
	"""Validates images for NES CHR compatibility."""

	def __init__(self, verbose: bool = False):
		self.verbose = verbose
		self.max_colors_per_tile = 4

	def get_tile_colors(self, img: Image.Image, tx: int, ty: int) -> Set[Tuple]:
		"""Get unique colors in an 8x8 tile region."""
		left = tx * 8
		top = ty * 8

		tile = img.crop((left, top, left + 8, top + 8))

		if tile.mode == 'P':
			tile = tile.convert('RGBA')
		elif tile.mode == 'RGB':
			pass
		elif tile.mode == 'RGBA':
			pass
		else:
			tile = tile.convert('RGBA')

		pixels = list(tile.getdata())
		colors = set()

		for p in pixels:
			if len(p) == 4 and p[3] < 128:
				# Transparent - count as one color
				colors.add('transparent')
			else:
				colors.add(p[:3])

		return colors

	def validate_file(self, filepath: Path) -> Tuple[bool, List[str]]:
		"""
		Validate a single PNG file.

		Returns (is_valid, list of issue descriptions).
		"""
		issues = []

		try:
			img = Image.open(filepath)
		except Exception as e:
			return False, [f"Cannot open file: {e}"]

		# Check dimensions
		if img.width % 8 != 0:
			issues.append(f"Width {img.width} is not a multiple of 8")
		if img.height % 8 != 0:
			issues.append(f"Height {img.height} is not a multiple of 8")

		if issues:
			return False, issues

		# Check each tile
		tiles_x = img.width // 8
		tiles_y = img.height // 8
		bad_tiles = []

		for ty in range(tiles_y):
			for tx in range(tiles_x):
				colors = self.get_tile_colors(img, tx, ty)
				if len(colors) > self.max_colors_per_tile:
					tile_idx = ty * tiles_x + tx
					bad_tiles.append((tx, ty, tile_idx, len(colors)))

		if bad_tiles:
			for tx, ty, idx, num_colors in bad_tiles:
				issues.append(f"Tile {idx} at ({tx},{ty}): {num_colors} colors (max 4)")

		return len(issues) == 0, issues

	def validate_directory(self, dirpath: Path, pattern: str = "*.png") -> dict:
		"""
		Validate all PNG files in a directory.

		Returns dict of {filepath: (is_valid, issues)}.
		"""
		results = {}

		for filepath in sorted(dirpath.glob(pattern)):
			is_valid, issues = self.validate_file(filepath)
			results[filepath] = (is_valid, issues)

		return results


def main():
	parser = argparse.ArgumentParser(
		description="Validate PNG graphics for NES CHR compatibility"
	)

	parser.add_argument('input', nargs='?', help='PNG file or directory to validate')
	parser.add_argument('--dir', '-d', help='Directory to validate')
	parser.add_argument('--verbose', '-v', action='store_true', help='Show all files, not just errors')
	parser.add_argument('--pattern', '-p', default='*.png', help='File pattern for directory mode')

	args = parser.parse_args()

	validator = CHRValidator(verbose=args.verbose)

	# Determine what to validate
	target = None
	if args.dir:
		target = Path(args.dir)
		if not target.is_dir():
			print(f"Error: {args.dir} is not a directory")
			sys.exit(1)
	elif args.input:
		target = Path(args.input)
	else:
		parser.print_help()
		sys.exit(1)

	all_valid = True

	if target.is_dir():
		# Validate directory
		print(f"Validating {target}/**/{args.pattern}")
		print("-" * 60)

		results = validator.validate_directory(target, args.pattern)

		valid_count = 0
		invalid_count = 0

		for filepath, (is_valid, issues) in results.items():
			if is_valid:
				valid_count += 1
				if args.verbose:
					print(f"✓ {filepath.name}")
			else:
				invalid_count += 1
				all_valid = False
				print(f"✗ {filepath.name}")
				for issue in issues:
					print(f"    {issue}")

		print("-" * 60)
		print(f"Results: {valid_count} valid, {invalid_count} invalid")

	else:
		# Validate single file
		if not target.exists():
			print(f"Error: {target} not found")
			sys.exit(1)

		is_valid, issues = validator.validate_file(target)

		if is_valid:
			print(f"✓ {target.name} is valid")
		else:
			all_valid = False
			print(f"✗ {target.name} has issues:")
			for issue in issues:
				print(f"  - {issue}")

	sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
	main()
