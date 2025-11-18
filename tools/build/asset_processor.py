#!/usr/bin/env python3
"""
Dragon Warrior Build System - Asset Processor
Extract assets from reference ROM and prepare for insertion during build
Based on FFMQ asset processing patterns
"""

import os
import sys
import struct
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json
import click
from rich.console import Console
from rich.progress import track
from rich.table import Table

console = Console()

class DragonWarriorAssetProcessor:
	"""Process assets for build system"""

	def __init__(self, reference_rom: str):
		self.reference_rom = Path(reference_rom)
		if not self.reference_rom.exists():
			raise FileNotFoundError(f"Reference ROM not found: {reference_rom}")

		with open(self.reference_rom, 'rb') as f:
			self.rom_data = f.read()

		self.assets_dir = Path("assets")
		self.extracted_dir = self.assets_dir / "extracted"
		self.processed_dir = self.assets_dir / "processed"

		console.print(f"[green]Loaded reference ROM: {self.reference_rom.name} ({len(self.rom_data)} bytes)[/green]")

	def extract_all_assets(self) -> Dict[str, Any]:
		"""Extract all assets from reference ROM"""
		console.print("[blue]Extracting assets from reference ROM...[/blue]")

		# Create directories
		for directory in [self.assets_dir, self.extracted_dir, self.processed_dir]:
			directory.mkdir(parents=True, exist_ok=True)

		assets = {
			"text_data": self._extract_text_data(),
			"character_data": self._extract_character_data(),
			"monster_data": self._extract_monster_data(),
			"item_data": self._extract_item_data(),
			"spell_data": self._extract_spell_data(),
			"map_data": self._extract_map_data(),
			"graphics_data": self._extract_graphics_data()
		}

		# Save asset manifest
		manifest_file = self.extracted_dir / "asset_manifest.json"
		with open(manifest_file, 'w', encoding='utf-8') as f:
			json.dump(assets, f, indent=2)

		console.print(f"[green]Asset extraction complete. Manifest: {manifest_file}[/green]")
		return assets

	def _extract_text_data(self) -> Dict[str, Any]:
		"""Extract text and dialog data"""
		# Dragon Warrior text areas (approximate - needs analysis)
		text_areas = [
			(0x8B40, 0x9000, "dialog_text"),
			(0x9000, 0x9200, "item_names"),
			(0x9200, 0x9400, "spell_names"),
			(0x9400, 0x9600, "monster_names"),
		]

		text_data = {}
		for start, end, section in text_areas:
			if end <= len(self.rom_data):
				data = self.rom_data[start:end]

				# Save raw data
				raw_file = self.extracted_dir / f"{section}_raw.bin"
				with open(raw_file, 'wb') as f:
					f.write(data)

				text_data[section] = {
					"offset": start,
					"size": end - start,
					"raw_file": str(raw_file),
					"checksum": hashlib.md5(data).hexdigest()
				}

		return text_data

	def _extract_character_data(self) -> Dict[str, Any]:
		"""Extract character stats and progression data"""
		# Character data locations (estimates)
		char_base_stats = 0x6180  # Base character stats
		char_level_data = 0x61A0  # Level progression

		data = {}

		# Base stats (estimated structure)
		if char_base_stats + 32 <= len(self.rom_data):
			base_data = self.rom_data[char_base_stats:char_base_stats + 32]
			data_file = self.extracted_dir / "character_base_stats.bin"
			with open(data_file, 'wb') as f:
				f.write(base_data)

			data["base_stats"] = {
				"offset": char_base_stats,
				"size": 32,
				"file": str(data_file),
				"checksum": hashlib.md5(base_data).hexdigest()
			}

		return data

	def _extract_monster_data(self) -> Dict[str, Any]:
		"""Extract monster stats and data"""
		# Monster data location (estimate - needs analysis)
		monster_start = 0x6200
		monster_count = 32  # Estimated monster count
		monster_record_size = 16  # Estimated record size

		total_size = monster_count * monster_record_size

		if monster_start + total_size <= len(self.rom_data):
			monster_data = self.rom_data[monster_start:monster_start + total_size]
			data_file = self.extracted_dir / "monster_data.bin"
			with open(data_file, 'wb') as f:
				f.write(monster_data)

			return {
				"offset": monster_start,
				"size": total_size,
				"count": monster_count,
				"record_size": monster_record_size,
				"file": str(data_file),
				"checksum": hashlib.md5(monster_data).hexdigest()
			}

		return {}

	def _extract_item_data(self) -> Dict[str, Any]:
		"""Extract item and equipment data"""
		# Item data location (estimate)
		item_start = 0x6400
		item_count = 64  # Estimated item count
		item_record_size = 8  # Estimated record size

		total_size = item_count * item_record_size

		if item_start + total_size <= len(self.rom_data):
			item_data = self.rom_data[item_start:item_start + total_size]
			data_file = self.extracted_dir / "item_data.bin"
			with open(data_file, 'wb') as f:
				f.write(item_data)

			return {
				"offset": item_start,
				"size": total_size,
				"count": item_count,
				"record_size": item_record_size,
				"file": str(data_file),
				"checksum": hashlib.md5(item_data).hexdigest()
			}

		return {}

	def _extract_spell_data(self) -> Dict[str, Any]:
		"""Extract spell and magic data"""
		# Spell data location (estimate)
		spell_start = 0x6600
		spell_count = 16  # Estimated spell count
		spell_record_size = 8  # Estimated record size

		total_size = spell_count * spell_record_size

		if spell_start + total_size <= len(self.rom_data):
			spell_data = self.rom_data[spell_start:spell_start + total_size]
			data_file = self.extracted_dir / "spell_data.bin"
			with open(data_file, 'wb') as f:
				f.write(spell_data)

			return {
				"offset": spell_start,
				"size": total_size,
				"count": spell_count,
				"record_size": spell_record_size,
				"file": str(data_file),
				"checksum": hashlib.md5(spell_data).hexdigest()
			}

		return {}

	def _extract_map_data(self) -> Dict[str, Any]:
		"""Extract map and world data"""
		# Map data location (estimate)
		map_start = 0xA000
		map_size = 0x1000  # 4KB estimated

		if map_start + map_size <= len(self.rom_data):
			map_data = self.rom_data[map_start:map_start + map_size]
			data_file = self.extracted_dir / "map_data.bin"
			with open(data_file, 'wb') as f:
				f.write(map_data)

			return {
				"offset": map_start,
				"size": map_size,
				"file": str(data_file),
				"checksum": hashlib.md5(map_data).hexdigest()
			}

		return {}

	def _extract_graphics_data(self) -> Dict[str, Any]:
		"""Extract graphics and CHR data"""
		# Check if ROM has CHR-ROM
		header = self.rom_data[:16]
		if len(header) >= 16 and header[:4] == b'NES\x1a':
			chr_size = header[5] * 8192  # CHR ROM size
			if chr_size > 0:
				prg_size = header[4] * 16384
				chr_start = 16 + prg_size

				if chr_start + chr_size <= len(self.rom_data):
					chr_data = self.rom_data[chr_start:chr_start + chr_size]
					data_file = self.extracted_dir / "chr_data.bin"
					with open(data_file, 'wb') as f:
						f.write(chr_data)

					return {
						"offset": chr_start,
						"size": chr_size,
						"file": str(data_file),
						"checksum": hashlib.md5(chr_data).hexdigest()
					}

		return {}

	def generate_insertion_code(self, assets: Dict[str, Any]) -> str:
		"""Generate assembly code for asset insertion"""
		asm_code = [
			"; Dragon Warrior - Auto-generated asset insertion",
			"; Generated by asset processor",
			"",
		]

		for asset_type, asset_data in assets.items():
			if not asset_data:
				continue

			asm_code.append(f"; {asset_type.upper()} DATA")

			if isinstance(asset_data, dict) and "offset" in asset_data:
				offset = asset_data["offset"]
				file_path = asset_data.get("file", "")

				if file_path:
					rel_path = Path(file_path).relative_to(Path.cwd())
					asm_code.append(f"	.org ${offset:04X}")
					asm_code.append(f"	.incbin \"{rel_path}\"")
					asm_code.append("")

		return "\n".join(asm_code)

@click.command()
@click.argument('reference_rom', type=click.Path(exists=True))
@click.option('--extract-only', is_flag=True, help='Extract assets only, no processing')
@click.option('--generate-asm', is_flag=True, help='Generate assembly insertion code')
def process_assets(reference_rom: str, extract_only: bool, generate_asm: bool):
	"""Process Dragon Warrior assets for build system"""

	console.print("[bold blue]Dragon Warrior Asset Processor[/bold blue]\n")

	try:
		processor = DragonWarriorAssetProcessor(reference_rom)
		assets = processor.extract_all_assets()

		if generate_asm:
			asm_code = processor.generate_insertion_code(assets)
			asm_file = processor.processed_dir / "asset_insertion.asm"

			with open(asm_file, 'w', encoding='utf-8') as f:
				f.write(asm_code)

			console.print(f"[green]Assembly insertion code generated: {asm_file}[/green]")

		console.print("\n[green]✅ Asset processing complete![/green]")

	except Exception as e:
		console.print(f"[red]Error: {e}[/red]")
		sys.exit(1)

if __name__ == "__main__":
	process_assets()
