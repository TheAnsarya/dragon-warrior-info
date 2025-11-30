"""
Dragon Warrior CHR Tile Extractor
Extracts all 512 CHR tiles (2 banks × 256 tiles) from ROM
"""

import sys
from pathlib import Path
from PIL import Image

class CHRExtractor:
	"""Extracts CHR tiles from NES ROM"""

	# NES palette (approximation of NTSC NES colors)
	NES_PALETTE = [
		(84, 84, 84),      # 0x00
		(0, 30, 116),      # 0x01
		(8, 16, 144),      # 0x02
		(48, 0, 136),      # 0x03
		(68, 0, 100),      # 0x04
		(92, 0, 48),       # 0x05
		(84, 4, 0),        # 0x06
		(60, 24, 0),       # 0x07
		(32, 42, 0),       # 0x08
		(8, 58, 0),        # 0x09
		(0, 64, 0),        # 0x0a
		(0, 60, 0),        # 0x0b
		(0, 50, 60),       # 0x0c
		(0, 0, 0),         # 0x0d
		(0, 0, 0),         # 0x0e
		(0, 0, 0),         # 0x0f
		(152, 150, 152),   # 0x10
		(8, 76, 196),      # 0x11
		(48, 50, 236),     # 0x12
		(92, 30, 228),     # 0x13
		(136, 20, 176),    # 0x14
		(160, 20, 100),    # 0x15
		(152, 34, 32),     # 0x16
		(120, 60, 0),      # 0x17
		(84, 90, 0),       # 0x18
		(40, 114, 0),      # 0x19
		(8, 124, 0),       # 0x1a
		(0, 118, 40),      # 0x1b
		(0, 102, 120),     # 0x1c
		(0, 0, 0),         # 0x1d
		(0, 0, 0),         # 0x1e
		(0, 0, 0),         # 0x1f
		(236, 238, 236),   # 0x20
		(76, 154, 236),    # 0x21
		(120, 124, 236),   # 0x22
		(176, 98, 236),    # 0x23
		(228, 84, 236),    # 0x24
		(236, 88, 180),    # 0x25
		(236, 106, 100),   # 0x26
		(212, 136, 32),    # 0x27
		(160, 170, 0),     # 0x28
		(116, 196, 0),     # 0x29
		(76, 208, 32),     # 0x2a
		(56, 204, 108),    # 0x2b
		(56, 180, 204),    # 0x2c
		(60, 60, 60),      # 0x2d
		(0, 0, 0),         # 0x2e
		(0, 0, 0),         # 0x2f
		(236, 238, 236),   # 0x30
		(168, 204, 236),   # 0x31
		(188, 188, 236),   # 0x32
		(212, 178, 236),   # 0x33
		(236, 174, 236),   # 0x34
		(236, 174, 212),   # 0x35
		(236, 180, 176),   # 0x36
		(228, 196, 144),   # 0x37
		(204, 210, 120),   # 0x38
		(180, 222, 120),   # 0x39
		(168, 226, 144),   # 0x3a
		(152, 226, 180),   # 0x3b
		(160, 214, 228),   # 0x3c
		(160, 162, 160),   # 0x3d
		(0, 0, 0),         # 0x3e
		(0, 0, 0),         # 0x3f
	]

	def __init__(self, rom_path: str):
		self.rom_path = Path(rom_path)
		if not self.rom_path.exists():
			raise FileNotFoundError(f"ROM not found: {rom_path}")

		with open(rom_path, 'rb') as f:
			self.rom_data = f.read()

		# Verify NES header
		if self.rom_data[:4] != b'NES\x1a':
			raise ValueError("Invalid NES ROM header")

		# CHR starts at offset 0x10 + PRG size
		# Dragon Warrior: 16-byte header + 64KB PRG (4 × 16KB) + 8KB CHR (2 × 4KB)
		self.prg_size = self.rom_data[4] * 16384  # PRG ROM size in bytes
		self.chr_size = self.rom_data[5] * 8192   # CHR ROM size in bytes
		self.chr_offset = 0x10 + self.prg_size

		print(f"ROM: {rom_path}")
		print(f"PRG size: {self.prg_size} bytes ({self.prg_size // 1024}KB)")
		print(f"CHR size: {self.chr_size} bytes ({self.chr_size // 1024}KB)")
		print(f"CHR offset: 0x{self.chr_offset:X}")

	def decode_tile(self, tile_data: bytes) -> list:
		"""
		Decode a single 8×8 NES tile from 16 bytes of CHR data
		Returns 64 pixel values (0-3)
		"""
		if len(tile_data) != 16:
			raise ValueError("Tile data must be exactly 16 bytes")

		pixels = []
		for y in range(8):
			bitplane0 = tile_data[y]
			bitplane1 = tile_data[y + 8]

			for x in range(8):
				# Extract bits from both bitplanes (MSB first)
				bit_pos = 7 - x
				bit0 = (bitplane0 >> bit_pos) & 1
				bit1 = (bitplane1 >> bit_pos) & 1
				pixel = bit0 | (bit1 << 1)
				pixels.append(pixel)

		return pixels

	def render_tile(self, pixels: list, palette: list = None) -> Image.Image:
		"""
		Render a tile as a PIL Image
		pixels: 64 values (0-3)
		palette: 4 RGB tuples, defaults to grayscale
		"""
		if palette is None:
			# Default grayscale palette
			palette = [(0, 0, 0), (85, 85, 85), (170, 170, 170), (255, 255, 255)]

		img = Image.new('RGB', (8, 8))
		for y in range(8):
			for x in range(8):
				pixel_idx = y * 8 + x
				color_idx = pixels[pixel_idx]
				img.putpixel((x, y), palette[color_idx])

		return img

	def extract_all_tiles(self, output_dir: str, scale: int = 4):
		"""
		Extract all CHR tiles to PNG files
		scale: upscale factor (1=8x8, 2=16x16, 4=32x32, etc.)
		"""
		output_path = Path(output_dir)
		output_path.mkdir(parents=True, exist_ok=True)

		total_tiles = self.chr_size // 16
		print(f"\nExtracting {total_tiles} tiles to {output_dir}")

		# Default palette (can be customized per tile if needed)
		default_palette = [
			(0, 0, 0),         # Transparent/background
			(85, 85, 85),      # Dark
			(170, 170, 170),   # Medium
			(255, 255, 255),   # Light
		]

		for tile_idx in range(total_tiles):
			offset = self.chr_offset + (tile_idx * 16)
			tile_data = self.rom_data[offset:offset + 16]

			# Decode and render
			pixels = self.decode_tile(tile_data)
			img = self.render_tile(pixels, default_palette)

			# Upscale using nearest neighbor
			if scale > 1:
				img = img.resize((8 * scale, 8 * scale), Image.NEAREST)

			# Save as PNG
			bank = tile_idx // 256
			tile_in_bank = tile_idx % 256
			filename = f"chr_bank{bank}_tile{tile_in_bank:03d}_{tile_idx:03d}.png"
			img.save(output_path / filename)

			if (tile_idx + 1) % 64 == 0:
				print(f"  Extracted {tile_idx + 1}/{total_tiles} tiles...")

		print(f"✓ Extracted {total_tiles} tiles successfully!")

		# Also create a combined sheet
		self.create_tile_sheet(output_path, scale)

	def create_tile_sheet(self, output_dir: Path, scale: int = 4):
		"""Create a combined sprite sheet of all tiles"""
		total_tiles = self.chr_size // 16
		tiles_per_row = 16
		rows = (total_tiles + tiles_per_row - 1) // tiles_per_row

		tile_size = 8 * scale
		sheet_width = tiles_per_row * tile_size
		sheet_height = rows * tile_size

		print(f"\nCreating tile sheet ({sheet_width}×{sheet_height})...")

		sheet = Image.new('RGB', (sheet_width, sheet_height), (0, 0, 0))

		default_palette = [
			(0, 0, 0),
			(85, 85, 85),
			(170, 170, 170),
			(255, 255, 255),
		]

		for tile_idx in range(total_tiles):
			offset = self.chr_offset + (tile_idx * 16)
			tile_data = self.rom_data[offset:offset + 16]

			pixels = self.decode_tile(tile_data)
			img = self.render_tile(pixels, default_palette)

			if scale > 1:
				img = img.resize((tile_size, tile_size), Image.NEAREST)

			# Calculate position in sheet
			x = (tile_idx % tiles_per_row) * tile_size
			y = (tile_idx // tiles_per_row) * tile_size
			sheet.paste(img, (x, y))

		sheet_path = output_dir / "chr_tiles_complete_sheet.png"
		sheet.save(sheet_path)
		print(f"✓ Tile sheet saved: {sheet_path}")

	def extract_with_palette(self, tile_idx: int, nes_palette_indices: list) -> Image.Image:
		"""Extract a single tile with specific NES palette colors"""
		offset = self.chr_offset + (tile_idx * 16)
		tile_data = self.rom_data[offset:offset + 16]

		pixels = self.decode_tile(tile_data)
		palette = [self.NES_PALETTE[idx] for idx in nes_palette_indices]

		return self.render_tile(pixels, palette)


def main():
	"""Main extraction entry point"""
	repo_root = Path(__file__).parent.parent
	rom_path = repo_root / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"
	output_dir = repo_root / "extracted_assets" / "chr_tiles"

	if not rom_path.exists():
		print(f"ERROR: ROM not found at {rom_path}")
		sys.exit(1)

	extractor = CHRExtractor(str(rom_path))
	extractor.extract_all_tiles(str(output_dir), scale=4)

	print("\n" + "=" * 70)
	print("CHR Tile Extraction Complete!")
	print("=" * 70)


if __name__ == "__main__":
	main()
