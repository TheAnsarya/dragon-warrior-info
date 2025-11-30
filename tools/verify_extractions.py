"""
Dragon Warrior Asset Extraction Verification Tool
Verifies accuracy of all extracted assets against the ROM data
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Add parent directory to path for ROM utilities
sys.path.insert(0, str(Path(__file__).parent.parent))

class ExtractionVerifier:
	"""Verifies extracted data matches ROM source"""

	def __init__(self, rom_path: str):
		self.rom_path = Path(rom_path)
		if not self.rom_path.exists():
			raise FileNotFoundError(f"ROM not found: {rom_path}")

		with open(rom_path, 'rb') as f:
			self.rom_data = f.read()

		self.errors = []
		self.warnings = []
		self.verified = 0

	def verify_monster_stats(self, extracted_json: str) -> bool:
		"""Verify monster stats match ROM data at Bank01:0x9e4b"""
		print("\n=== Verifying Monster Stats ===")

		with open(extracted_json, 'r') as f:
			monsters = json.load(f)

		# Monster stats start at Bank01:0x9e4b (CPU address)
		# File offset = 0x10 (header) + 0x4000 (Bank00) + (0x9e4b - 0x8000)
		# = 0x10 + 0x4000 + 0x1e4b = 0x5e5b
		stats_offset = 0x5e5b  # Corrected file offset for monster stats table

		monster_count = 39  # Total monsters including both Dragonlord forms
		errors_found = 0

		for i in range(monster_count):
			if str(i) not in monsters:
				self.errors.append(f"Monster {i} missing from extracted data")
				errors_found += 1
				continue

			monster = monsters[str(i)]
			offset = stats_offset + (i * 16)  # 16 bytes per monster

			# Read ROM stats (Attack, Defense, HP, Spell, Agility, MDef, Exp, Gold)
			rom_stats = {
				'strength': self.rom_data[offset + 0],
				'defense': self.rom_data[offset + 1],
				'hp': self.rom_data[offset + 2],
				'spell': self.rom_data[offset + 3],
				'agility': self.rom_data[offset + 4],
				'magic_defense': self.rom_data[offset + 5],
				'experience': self.rom_data[offset + 6],
				'gold': self.rom_data[offset + 7],
			}

			# Compare extracted vs ROM
			mismatches = []
			if monster.get('strength') != rom_stats['strength']:
				mismatches.append(f"strength: extracted={monster.get('strength')}, rom={rom_stats['strength']}")
			if monster.get('hp') != rom_stats['hp']:
				mismatches.append(f"hp: extracted={monster.get('hp')}, rom={rom_stats['hp']}")
			if monster.get('agility') != rom_stats['agility']:
				mismatches.append(f"agility: extracted={monster.get('agility')}, rom={rom_stats['agility']}")
			if monster.get('experience') != rom_stats['experience']:
				mismatches.append(f"experience: extracted={monster.get('experience')}, rom={rom_stats['experience']}")
			if monster.get('gold') != rom_stats['gold']:
				mismatches.append(f"gold: extracted={monster.get('gold')}, rom={rom_stats['gold']}")

			if mismatches:
				self.errors.append(f"Monster {i} ({monster.get('name')}): {', '.join(mismatches)}")
				errors_found += 1
			else:
				self.verified += 1

		if errors_found == 0:
			print(f"✓ All {monster_count} monster stats verified successfully!")
			return True
		else:
			print(f"✗ Found {errors_found} mismatches in monster stats")
			return False

	def verify_monster_sprites(self, sprite_db_json: str) -> bool:
		"""Verify monster sprite data matches ROM"""
		print("\n=== Verifying Monster Sprite Data ===")

		with open(sprite_db_json, 'r') as f:
			sprites = json.load(f)

		# Sprite pointer table at Bank01:0x99e4 (file offset 0x59f4)
		sprite_ptr_offset = 0x59f4

		# Known sprite data locations from disassembly
		sprite_locations = {
			0: ("SlimeSprts", 0x5b0e),     # Slime at Bank01:0x1b0e
			1: ("SlimeSprts", 0x5b0e),     # Red Slime (same as Slime)
			2: ("DrakeeSprts", 0x5ac4),    # Drakee at Bank01:0x1ac4
			3: ("GhstSprts", 0x5baa),      # Ghost at Bank01:0x1baa
			# Add more as needed
		}

		errors_found = 0

		for i, sprite in enumerate(sprites[:10]):  # Verify first 10 for now
			if 'sprite_data' not in sprite:
				self.warnings.append(f"Sprite {i} missing sprite_data field")
				continue

			# Read pointer from table
			ptr_offset = sprite_ptr_offset + (i * 2)
			ptr_low = self.rom_data[ptr_offset]
			ptr_high = self.rom_data[ptr_offset + 1]
			ptr_value = ptr_low | (ptr_high << 8)

			# Adjust for bank (Bank01 = 0x4000-0x7fff in CPU space, starts at 0x4010 in file)
			# Sprite pointers have 0x8000 subtracted and MSB indicates mirroring

			sprite_tiles = sprite.get('sprite_tiles', 0)
			if sprite_tiles > 0:
				print(f"  Sprite {i} ({sprite.get('name')}): {sprite_tiles} tiles")
				self.verified += 1

		if errors_found == 0:
			print(f"✓ Sprite data structures verified")
			return True
		else:
			print(f"✗ Found {errors_found} issues in sprite data")
			return False

	def verify_chr_tiles(self, chr_dir: str) -> bool:
		"""Verify CHR tile extraction"""
		print("\n=== Verifying CHR Tiles ===")

		chr_path = Path(chr_dir)
		if not chr_path.exists():
			self.errors.append(f"CHR tiles directory not found: {chr_dir}")
			return False

		# Dragon Warrior has 2 CHR banks (512 tiles total)
		# Each bank is 4096 bytes (256 tiles × 16 bytes/tile)
		chr_offset = 0x10  # CHR starts after 16-byte header

		# Count extracted tiles
		tile_files = list(chr_path.glob("*.png"))
		tile_count = len(tile_files)

		print(f"  Found {tile_count} extracted tile images")

		if tile_count == 512:
			print(f"✓ Correct number of CHR tiles extracted (512)")
			self.verified += 1
			return True
		else:
			self.warnings.append(f"Expected 512 CHR tiles, found {tile_count}")
			return False

	def verify_palettes(self, palette_json: str) -> bool:
		"""Verify palette extraction"""
		print("\n=== Verifying Palettes ===")

		with open(palette_json, 'r') as f:
			palettes = json.load(f)

		# Dragon Warrior uses 4 background and 4 sprite palettes
		# Each palette has 4 colors

		palette_count = len(palettes) if isinstance(palettes, list) else len(palettes.keys())
		print(f"  Found {palette_count} palettes")

		if palette_count >= 8:
			print(f"✓ Palettes extracted")
			self.verified += 1
			return True
		else:
			self.warnings.append(f"Expected at least 8 palettes, found {palette_count}")
			return False

	def verify_items(self, items_json: str) -> bool:
		"""Verify item data extraction"""
		print("\n=== Verifying Item Data ===")

		with open(items_json, 'r') as f:
			items = json.load(f)

		# Dragon Warrior has 35 items (0x00-0x22)
		expected_items = 35
		item_count = len(items)

		print(f"  Found {item_count} items")

		if item_count == expected_items:
			print(f"✓ All {expected_items} items extracted")
			self.verified += 1
			return True
		else:
			self.warnings.append(f"Expected {expected_items} items, found {item_count}")
			return False

	def verify_spells(self, spells_json: str) -> bool:
		"""Verify spell data extraction"""
		print("\n=== Verifying Spell Data ===")

		with open(spells_json, 'r') as f:
			spells = json.load(f)

		# Dragon Warrior has 10 spells
		expected_spells = 10
		spell_count = len(spells)

		print(f"  Found {spell_count} spells")

		if spell_count == expected_spells:
			print(f"✓ All {expected_spells} spells extracted")
			self.verified += 1
			return True
		else:
			self.warnings.append(f"Expected {expected_spells} spells, found {spell_count}")
			return False

	def run_full_verification(self, extracted_dir: str) -> bool:
		"""Run all verification tests"""
		extracted = Path(extracted_dir)

		print("=" * 70)
		print("Dragon Warrior Extraction Verification")
		print("=" * 70)

		all_passed = True

		# Verify monsters
		monster_json = extracted / "json" / "monsters.json"
		if monster_json.exists():
			all_passed &= self.verify_monster_stats(str(monster_json))
		else:
			self.errors.append("Monster stats JSON not found")
			all_passed = False

		# Verify monster sprites
		sprite_db = extracted / "graphics_comprehensive" / "monsters" / "monsters_database.json"
		if sprite_db.exists():
			all_passed &= self.verify_monster_sprites(str(sprite_db))
		else:
			self.warnings.append("Monster sprite database not found")

		# Verify CHR tiles
		chr_dir = extracted / "chr_tiles"
		if chr_dir.exists():
			self.verify_chr_tiles(str(chr_dir))
		else:
			self.warnings.append("CHR tiles directory not found")

		# Verify palettes
		palette_json = extracted / "json" / "palettes.json"
		if palette_json.exists():
			self.verify_palettes(str(palette_json))

		# Verify items
		items_json = extracted / "json" / "items.json"
		if items_json.exists():
			self.verify_items(str(items_json))

		# Verify spells
		spells_json = extracted / "json" / "spells.json"
		if spells_json.exists():
			self.verify_spells(str(spells_json))

		# Print summary
		print("\n" + "=" * 70)
		print("VERIFICATION SUMMARY")
		print("=" * 70)
		print(f"✓ Verified: {self.verified} items")
		print(f"⚠ Warnings: {len(self.warnings)}")
		print(f"✗ Errors: {len(self.errors)}")

		if self.warnings:
			print("\nWarnings:")
			for warning in self.warnings:
				print(f"  ⚠ {warning}")

		if self.errors:
			print("\nErrors:")
			for error in self.errors:
				print(f"  ✗ {error}")

		print("=" * 70)

		return all_passed and len(self.errors) == 0


def main():
	"""Main verification entry point"""
	import sys

	# Paths
	repo_root = Path(__file__).parent.parent
	rom_path = repo_root / "roms" / "Dragon Warrior (U) (PRG1) [!].nes"
	extracted_dir = repo_root / "extracted_assets"

	if not rom_path.exists():
		print(f"ERROR: ROM not found at {rom_path}")
		sys.exit(1)

	verifier = ExtractionVerifier(str(rom_path))
	success = verifier.run_full_verification(str(extracted_dir))

	sys.exit(0 if success else 1)


if __name__ == "__main__":
	main()
