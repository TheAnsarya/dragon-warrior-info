#!/usr/bin/env python3
"""
Dragon Warrior Asset Extractor
Extract graphics, text, music, and data from Dragon Warrior ROM
Based on FFMQ extraction patterns
"""

import os
import sys
import struct
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import json
import click
from rich.console import Console
from rich.progress import Progress, track
from rich.table import Table
import hashlib

console = Console()

class DragonWarriorROM:
	"""Dragon Warrior ROM data extractor and analyzer"""

	def __init__(self, rom_path: str):
		self.rom_path = Path(rom_path)
		if not self.rom_path.exists():
			raise FileNotFoundError(f"ROM file not found: {rom_path}")

		with open(self.rom_path, 'rb') as f:
			self.rom_data = f.read()

		self.rom_size = len(self.rom_data)
		console.print(f"[green]Loaded ROM: {self.rom_path.name} ({self.rom_size} bytes)[/green]")

		# Dragon Warrior ROM should be around 256KB
		if self.rom_size < 100_000 or self.rom_size > 1_000_000:
			console.print(f"[yellow]Warning: ROM size {self.rom_size} bytes seems unusual[/yellow]")

		self.output_dir = Path("assets")
		self.graphics_dir = self.output_dir / "graphics"
		self.text_dir = self.output_dir / "text"
		self.data_dir = self.output_dir / "data"
		self.music_dir = self.output_dir / "music"

	def verify_rom(self) -> Dict[str, str]:
		"""Verify ROM integrity and identify version"""
		console.print("[blue]Verifying ROM...[/blue]")

		# Calculate checksums
		md5_hash = hashlib.md5(self.rom_data).hexdigest()
		sha1_hash = hashlib.sha1(self.rom_data).hexdigest()

		# Known Dragon Warrior ROM checksums
		known_versions = {
			# Add known MD5 hashes for different Dragon Warrior versions
			"2c52c792": "Dragon Warrior (USA)",
			"6b19a2c6": "Dragon Warrior (USA) (Rev 1)",
			"1da17f0c": "Dragon Warrior (Japan)",
			# Add more as identified
		}

		version = known_versions.get(md5_hash[:8].lower(), "Unknown version")

		console.print(f"[green]ROM verification complete[/green]")
		console.print(f"MD5: {md5_hash}")
		console.print(f"SHA1: {sha1_hash}")
		console.print(f"Version: {version}")

		return {
			"md5": md5_hash,
			"sha1": sha1_hash,
			"version": version,
			"size": self.rom_size
		}

	def create_output_dirs(self):
		"""Create output directory structure"""
		for directory in [self.output_dir, self.graphics_dir, self.text_dir,
						self.data_dir, self.music_dir]:
			directory.mkdir(parents=True, exist_ok=True)

	def extract_graphics(self) -> Dict[str, any]:
		"""Extract graphics data from ROM"""
		console.print("[blue]Extracting graphics...[/blue]")

		graphics_info = {}

		# Dragon Warrior NES graphics are typically stored as CHR-ROM data
		# NES ROMs have header at 0x00-0x0F, PRG-ROM, then CHR-ROM

		# Read NES header
		if len(self.rom_data) >= 16:
			header = self.rom_data[:16]
			if header[:4] == b'NES\x1a':	# iNES header signature
				prg_size = header[4] * 16384	# PRG ROM size in 16KB units
				chr_size = header[5] * 8192	 # CHR ROM size in 8KB units

				console.print(f"NES ROM detected - PRG: {prg_size//1024}KB, CHR: {chr_size//1024}KB")

				# CHR-ROM starts after header + PRG-ROM
				chr_start = 16 + prg_size
				chr_end = chr_start + chr_size

				if chr_end <= len(self.rom_data):
					chr_data = self.rom_data[chr_start:chr_end]

					# Export CHR data as binary
					chr_file = self.graphics_dir / "chr_rom.bin"
					with open(chr_file, 'wb') as f:
						f.write(chr_data)

					console.print(f"Extracted CHR-ROM to {chr_file}")

					graphics_info = {
						"chr_rom": {
							"file": str(chr_file),
							"offset": chr_start,
							"size": chr_size,
							"tiles": chr_size // 16	# Each tile is 16 bytes
						}
					}
				else:
					console.print("[yellow]Warning: CHR-ROM extends beyond ROM file[/yellow]")

		return graphics_info

	def extract_text(self) -> Dict[str, any]:
		"""Extract text data from ROM"""
		console.print("[blue]Extracting text...[/blue]")

		text_info = {}

		# Dragon Warrior text extraction requires knowledge of text encoding
		# This is a starting framework - specific offsets need research

		# Common text areas to search (these are estimates)
		text_search_areas = [
			(0x8000, 0xA000, "dialog_text"),
			(0xA000, 0xC000, "item_names"),
			(0xC000, 0xE000, "monster_names"),
			(0xE000, 0xF800, "menu_text")
		]

		for start, end, section in text_search_areas:
			if end <= len(self.rom_data):
				section_data = self.rom_data[start:end]

				# Look for printable ASCII-ish sequences
				text_sequences = []
				current_text = b""

				for byte in section_data:
					if 0x20 <= byte <= 0x7E:	# Printable ASCII range
						current_text += bytes([byte])
					else:
						if len(current_text) >= 3:	# Minimum text length
							text_sequences.append(current_text.decode('ascii', errors='ignore'))
						current_text = b""

				if current_text and len(current_text) >= 3:
					text_sequences.append(current_text.decode('ascii', errors='ignore'))

				# Save text sequences
				if text_sequences:
					text_file = self.text_dir / f"{section}.txt"
					with open(text_file, 'w', encoding='utf-8') as f:
						for i, text in enumerate(text_sequences):
							f.write(f"String {i:04d}: {text}\n")

					text_info[section] = {
						"file": str(text_file),
						"offset": start,
						"size": end - start,
						"strings_found": len(text_sequences)
					}

					console.print(f"Extracted {len(text_sequences)} text strings from {section}")

		return text_info

	def extract_game_data(self) -> Dict[str, any]:
		"""Extract game data tables (stats, items, etc.)"""
		console.print("[blue]Extracting game data...[/blue]")

		data_info = {}

		# Dragon Warrior data structures (estimates - need research)
		data_areas = [
			(0x6000, 0x6100, "character_stats", 8),	# Character base stats
			(0x6100, 0x6200, "item_data", 16),		 # Item definitions
			(0x6200, 0x6400, "monster_stats", 32),	 # Monster stats
			(0x6400, 0x6500, "spell_data", 8),		 # Spell definitions
		]

		for start, end, section, record_size in data_areas:
			if end <= len(self.rom_data):
				section_data = self.rom_data[start:end]

				# Parse as structured data
				records = []
				for i in range(0, len(section_data), record_size):
					record_bytes = section_data[i:i+record_size]
					if len(record_bytes) == record_size:
						# Convert to hex representation for analysis
						hex_data = record_bytes.hex()
						records.append({
							"index": i // record_size,
							"offset": start + i,
							"hex": hex_data,
							"bytes": list(record_bytes)
						})

				if records:
					data_file = self.data_dir / f"{section}.json"
					with open(data_file, 'w', encoding='utf-8') as f:
						json.dump(records, f, indent=2)

					data_info[section] = {
						"file": str(data_file),
						"offset": start,
						"size": end - start,
						"records": len(records),
						"record_size": record_size
					}

					console.print(f"Extracted {len(records)} {section} records")

		return data_info

	def extract_music(self) -> Dict[str, any]:
		"""Extract music and sound data"""
		console.print("[blue]Extracting music data...[/blue]")

		music_info = {}

		# NES music is typically stored as code that writes to sound registers
		# This requires sophisticated analysis - placeholder implementation

		# Look for patterns that might be music data
		music_search_areas = [
			(0xF000, 0xF800, "music_data"),
			(0xF800, 0xFFFF, "sound_effects")
		]

		for start, end, section in music_search_areas:
			if end <= len(self.rom_data):
				section_data = self.rom_data[start:end]

				# Save raw music data for analysis
				music_file = self.music_dir / f"{section}.bin"
				with open(music_file, 'wb') as f:
					f.write(section_data)

				music_info[section] = {
					"file": str(music_file),
					"offset": start,
					"size": end - start
				}

				console.print(f"Extracted {section} ({len(section_data)} bytes)")

		return music_info

	def generate_extraction_report(self, rom_info: Dict, graphics_info: Dict,
								 text_info: Dict, data_info: Dict, music_info: Dict):
		"""Generate comprehensive extraction report"""

		report = {
			"rom_info": rom_info,
			"extraction_timestamp": str(Path().cwd()),
			"graphics": graphics_info,
			"text": text_info,
			"data": data_info,
			"music": music_info
		}

		# Save JSON report
		report_file = self.output_dir / "extraction_report.json"
		with open(report_file, 'w', encoding='utf-8') as f:
			json.dump(report, f, indent=2)

		# Generate markdown summary
		md_report = self.output_dir / "extraction_summary.md"
		with open(md_report, 'w', encoding='utf-8') as f:
			f.write("# Dragon Warrior Asset Extraction Report\n\n")
			f.write(f"**ROM:** {self.rom_path.name}\n")
			f.write(f"**Version:** {rom_info['version']}\n")
			f.write(f"**Size:** {rom_info['size']:,} bytes\n")
			f.write(f"**MD5:** {rom_info['md5']}\n\n")

			f.write("## Extraction Summary\n\n")

			if graphics_info:
				f.write("### Graphics\n")
				for section, info in graphics_info.items():
					f.write(f"- **{section}**: {info['size']:,} bytes, {info.get('tiles', 'N/A')} tiles\n")
				f.write("\n")

			if text_info:
				f.write("### Text\n")
				for section, info in text_info.items():
					f.write(f"- **{section}**: {info['strings_found']} strings found\n")
				f.write("\n")

			if data_info:
				f.write("### Game Data\n")
				for section, info in data_info.items():
					f.write(f"- **{section}**: {info['records']} records × {info['record_size']} bytes each\n")
				f.write("\n")

			if music_info:
				f.write("### Music\n")
				for section, info in music_info.items():
					f.write(f"- **{section}**: {info['size']:,} bytes\n")

		console.print(f"[green]Extraction report saved to {report_file}[/green]")
		console.print(f"[green]Summary saved to {md_report}[/green]")

@click.command()
@click.argument('rom_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='assets', help='Output directory for extracted assets')
@click.option('--graphics', is_flag=True, help='Extract graphics only')
@click.option('--text', is_flag=True, help='Extract text only')
@click.option('--data', is_flag=True, help='Extract game data only')
@click.option('--music', is_flag=True, help='Extract music only')
@click.option('--verify-only', is_flag=True, help='Verify ROM only, no extraction')
def extract_assets(rom_file: str, output: str, graphics: bool, text: bool,
					data: bool, music: bool, verify_only: bool):
	"""Extract assets from Dragon Warrior ROM file"""

	console.print("[bold blue]Dragon Warrior Asset Extractor[/bold blue]")
	console.print("Based on FFMQ extraction patterns\n")

	try:
		# Initialize ROM
		rom = DragonWarriorROM(rom_file)
		rom.output_dir = Path(output)
		rom.graphics_dir = rom.output_dir / "graphics"
		rom.text_dir = rom.output_dir / "text"
		rom.data_dir = rom.output_dir / "data"
		rom.music_dir = rom.output_dir / "music"

		# Verify ROM
		rom_info = rom.verify_rom()

		if verify_only:
			console.print("[green]ROM verification completed successfully![/green]")
			return

		# Create output directories
		rom.create_output_dirs()

		# Determine what to extract
		extract_all = not any([graphics, text, data, music])

		graphics_info = {}
		text_info = {}
		data_info = {}
		music_info = {}

		# Extract assets based on options
		with Progress() as progress:
			if extract_all or graphics:
				task = progress.add_task("Extracting graphics...", total=100)
				graphics_info = rom.extract_graphics()
				progress.advance(task, 100)

			if extract_all or text:
				task = progress.add_task("Extracting text...", total=100)
				text_info = rom.extract_text()
				progress.advance(task, 100)

			if extract_all or data:
				task = progress.add_task("Extracting game data...", total=100)
				data_info = rom.extract_game_data()
				progress.advance(task, 100)

			if extract_all or music:
				task = progress.add_task("Extracting music...", total=100)
				music_info = rom.extract_music()
				progress.advance(task, 100)

		# Generate report
		rom.generate_extraction_report(rom_info, graphics_info, text_info, data_info, music_info)

		console.print("\n[green]✅ Asset extraction completed successfully![/green]")
		console.print(f"[blue]Assets saved to: {rom.output_dir}[/blue]")

	except Exception as e:
		console.print(f"[red]Error during extraction: {e}[/red]")
		sys.exit(1)

if __name__ == "__main__":
	extract_assets()
