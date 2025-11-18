#!/usr/bin/env python3
"""
Dragon Warrior ROM Analyzer
Comprehensive ROM analysis and hex dump utilities
Based on FFMQ analysis patterns
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
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich.syntax import Syntax
import numpy as np

console = Console()

class ROMAnalyzer:
	"""Dragon Warrior ROM analysis and inspection tools"""

	def __init__(self, rom_path: str):
		self.rom_path = Path(rom_path)
		if not self.rom_path.exists():
			raise FileNotFoundError(f"ROM file not found: {rom_path}")

		with open(self.rom_path, 'rb') as f:
			self.rom_data = f.read()

		self.rom_size = len(self.rom_data)
		self.header_info = self._parse_header()

		console.print(f"[green]Loaded ROM: {self.rom_path.name} ({self.rom_size:,} bytes)[/green]")

	def _parse_header(self) -> Dict[str, Any]:
		"""Parse NES ROM header"""
		if len(self.rom_data) < 16:
			return {"valid": False, "error": "ROM too small for header"}

		header = self.rom_data[:16]

		# Check for iNES header signature
		if header[:4] != b'NES\x1a':
			return {"valid": False, "error": "Invalid iNES header signature"}

		info = {
			"valid": True,
			"signature": header[:4].decode('ascii', errors='ignore'),
			"prg_size": header[4] * 16384,  # PRG ROM in 16KB units
			"chr_size": header[5] * 8192,   # CHR ROM in 8KB units
			"flags6": header[6],
			"flags7": header[7],
			"flags8": header[8],
			"flags9": header[9],
			"flags10": header[10],
			"padding": header[11:16]
		}

		# Parse flags
		info["mapper"] = ((info["flags7"] & 0xf0) >> 4) | (info["flags6"] >> 4)
		info["mirroring"] = "vertical" if (info["flags6"] & 0x01) else "horizontal"
		info["battery"] = bool(info["flags6"] & 0x02)
		info["trainer"] = bool(info["flags6"] & 0x04)
		info["four_screen"] = bool(info["flags6"] & 0x08)

		# Calculate offsets
		trainer_size = 512 if info["trainer"] else 0
		info["prg_offset"] = 16 + trainer_size
		info["chr_offset"] = info["prg_offset"] + info["prg_size"]

		return info

	def display_header_info(self):
		"""Display detailed header information"""
		if not self.header_info["valid"]:
			console.print(f"[red]Invalid ROM: {self.header_info['error']}[/red]")
			return

		table = Table(title="NES ROM Header Analysis")
		table.add_column("Field", style="cyan", no_wrap=True)
		table.add_column("Value", style="green")
		table.add_column("Description", style="dim")

		h = self.header_info

		table.add_row("Signature", h["signature"], "iNES format identifier")
		table.add_row("PRG ROM", f"{h['prg_size']:,} bytes", f"{h['prg_size']//1024}KB program code")
		table.add_row("CHR ROM", f"{h['chr_size']:,} bytes", f"{h['chr_size']//1024}KB character data")
		table.add_row("Mapper", str(h["mapper"]), "Memory mapper type")
		table.add_row("Mirroring", h["mirroring"], "Nametable mirroring")
		table.add_row("Battery", str(h["battery"]), "Battery-backed SRAM")
		table.add_row("Trainer", str(h["trainer"]), "512-byte trainer present")

		console.print(table)

	def hex_dump(self, start: int = 0, length: int = 256, width: int = 16) -> str:
		"""Generate hex dump of ROM data"""
		if start >= len(self.rom_data):
			return "Start offset beyond ROM size"

		end = min(start + length, len(self.rom_data))
		data = self.rom_data[start:end]

		lines = []
		for i in range(0, len(data), width):
			# Address
			addr = start + i
			addr_str = f"{addr:08x}"

			# Hex bytes
			chunk = data[i:i+width]
			hex_bytes = ' '.join(f"{b:02x}" for b in chunk)
			hex_bytes = hex_bytes.ljust(width * 3 - 1)  # Pad to consistent width

			# ASCII representation
			ascii_chars = ''.join(chr(b) if 32 <= b <= 126 else '.' for b in chunk)

			lines.append(f"{addr_str}  {hex_bytes}  |{ascii_chars}|")

		return '\n'.join(lines)

	def analyze_data_patterns(self, start: int = 0, length: int = None) -> Dict[str, Any]:
		"""Analyze data patterns in ROM section"""
		if length is None:
			length = len(self.rom_data) - start

		end = min(start + length, len(self.rom_data))
		data = self.rom_data[start:end]

		if len(data) == 0:
			return {"error": "No data to analyze"}

		analysis = {
			"offset": start,
			"size": len(data),
			"byte_frequency": {},
			"entropy": 0.0,
			"null_runs": [],
			"repeated_patterns": [],
			"text_likelihood": 0.0
		}

		# Byte frequency analysis
		byte_counts = np.bincount(data, minlength=256)
		analysis["byte_frequency"] = {i: int(count) for i, count in enumerate(byte_counts) if count > 0}

		# Calculate entropy (measure of randomness)
		probabilities = byte_counts[byte_counts > 0] / len(data)
		analysis["entropy"] = float(-np.sum(probabilities * np.log2(probabilities)))

		# Find null byte runs
		null_runs = []
		in_run = False
		run_start = 0
		for i, byte in enumerate(data):
			if byte == 0:
				if not in_run:
					in_run = True
					run_start = i
			else:
				if in_run:
					in_run = False
					if i - run_start > 3:  # Only report runs > 3 bytes
						null_runs.append((start + run_start, i - run_start))

		analysis["null_runs"] = null_runs

		# Analyze text likelihood
		printable_count = sum(1 for b in data if 32 <= b <= 126)
		analysis["text_likelihood"] = printable_count / len(data)

		# Find repeated patterns
		patterns = {}
		for pattern_len in [2, 4, 8]:
			for i in range(0, len(data) - pattern_len + 1, pattern_len):
				pattern = tuple(data[i:i+pattern_len])
				if pattern in patterns:
					patterns[pattern] += 1
				else:
					patterns[pattern] = 1

		# Report patterns that occur more than once
		repeated = [(pattern, count) for pattern, count in patterns.items() if count > 1]
		repeated.sort(key=lambda x: x[1], reverse=True)
		analysis["repeated_patterns"] = repeated[:10]  # Top 10

		return analysis

	def find_text_strings(self, min_length: int = 4) -> List[Tuple[int, str]]:
		"""Find potential text strings in ROM"""
		strings = []
		current_string = ""
		start_pos = 0

		for i, byte in enumerate(self.rom_data):
			if 32 <= byte <= 126:  # Printable ASCII range
				if not current_string:
					start_pos = i
				current_string += chr(byte)
			else:
				if len(current_string) >= min_length:
					strings.append((start_pos, current_string))
				current_string = ""

		# Check final string
		if len(current_string) >= min_length:
			strings.append((start_pos, current_string))

		return strings

	def analyze_chr_data(self) -> Dict[str, Any]:
		"""Analyze CHR-ROM data if present"""
		if not self.header_info["valid"] or self.header_info["chr_size"] == 0:
			return {"error": "No CHR-ROM data found"}

		chr_start = self.header_info["chr_offset"]
		chr_end = chr_start + self.header_info["chr_size"]

		if chr_end > len(self.rom_data):
			return {"error": "CHR-ROM extends beyond ROM file"}

		chr_data = self.rom_data[chr_start:chr_end]

		analysis = {
			"offset": chr_start,
			"size": len(chr_data),
			"tiles": len(chr_data) // 16,  # Each NES tile is 16 bytes
			"patterns": []
		}

		# Analyze tile patterns
		for tile_num in range(analysis["tiles"]):
			tile_offset = tile_num * 16
			tile_data = chr_data[tile_offset:tile_offset + 16]

			# Simple pattern analysis - check for blank tiles
			if all(b == 0 for b in tile_data):
				analysis["patterns"].append((tile_num, "blank"))
			elif all(b == 0xff for b in tile_data):
				analysis["patterns"].append((tile_num, "solid"))

		return analysis

	def generate_memory_map(self) -> Dict[str, Any]:
		"""Generate detailed memory map of ROM"""
		memory_map = {
			"header": {
				"offset": 0,
				"size": 16,
				"description": "iNES header"
			}
		}

		if self.header_info["valid"]:
			# PRG-ROM section
			prg_offset = self.header_info["prg_offset"]
			prg_size = self.header_info["prg_size"]

			memory_map["prg_rom"] = {
				"offset": prg_offset,
				"size": prg_size,
				"description": "Program ROM",
				"banks": []
			}

			# Divide into 16KB banks for NROM
			for bank in range(prg_size // 16384):
				bank_offset = prg_offset + (bank * 16384)
				memory_map["prg_rom"]["banks"].append({
					"bank": bank,
					"offset": bank_offset,
					"size": 16384,
					"cpu_address": 0x8000 + (bank * 16384) if bank < 2 else 0x8000 + ((bank-2) * 16384)
				})

			# CHR-ROM section (if present)
			if self.header_info["chr_size"] > 0:
				memory_map["chr_rom"] = {
					"offset": self.header_info["chr_offset"],
					"size": self.header_info["chr_size"],
					"description": "Character ROM"
				}

		return memory_map

	def save_analysis_report(self, output_path: str):
		"""Save comprehensive analysis report"""
		report = {
			"rom_file": str(self.rom_path),
			"rom_size": self.rom_size,
			"checksums": {
				"md5": hashlib.md5(self.rom_data).hexdigest(),
				"sha1": hashlib.sha1(self.rom_data).hexdigest()
			},
			"header_info": self.header_info,
			"memory_map": self.generate_memory_map(),
			"data_analysis": {},
			"text_strings": self.find_text_strings()[:50],  # First 50 strings
			"chr_analysis": self.analyze_chr_data()
		}

		# Analyze key sections
		sections = [
			("header", 0, 16),
			("prg_bank0", 0x10, 16384),
			("prg_bank1", 0x4010, 16384),
		]

		for section_name, start, size in sections:
			if start + size <= len(self.rom_data):
				report["data_analysis"][section_name] = self.analyze_data_patterns(start, size)

		# Save JSON report
		output_file = Path(output_path)
		with open(output_file, 'w', encoding='utf-8') as f:
			json.dump(report, f, indent=2)

		console.print(f"[green]Analysis report saved to: {output_file}[/green]")

@click.group()
def cli():
	"""Dragon Warrior ROM Analyzer - Comprehensive ROM analysis tools"""
	console.print(Panel.fit(
		"[bold blue]Dragon Warrior ROM Analyzer[/bold blue]\n"
		"Comprehensive ROM analysis and inspection tools",
		border_style="blue"
	))

@cli.command()
@click.argument('rom_file', type=click.Path(exists=True))
def info(rom_file: str):
	"""Display ROM header and basic information"""
	analyzer = ROMAnalyzer(rom_file)
	analyzer.display_header_info()

@cli.command()
@click.argument('rom_file', type=click.Path(exists=True))
@click.option('--start', '-s', default=0, help='Start offset (hex or decimal)')
@click.option('--length', '-l', default=256, help='Number of bytes to dump')
@click.option('--width', '-w', default=16, help='Bytes per line')
def hexdump(rom_file: str, start: str, length: int, width: int):
	"""Display hex dump of ROM data"""
	analyzer = ROMAnalyzer(rom_file)

	# Parse start offset (handle hex)
	if start.startswith('0x'):
		start_offset = int(start, 16)
	else:
		start_offset = int(start)

	dump = analyzer.hex_dump(start_offset, length, width)

	console.print(f"\n[bold]Hex dump of {rom_file}[/bold]")
	console.print(f"Offset: 0x{start_offset:08x}, Length: {length} bytes\n")

	syntax = Syntax(dump, "hexdump", theme="monokai", line_numbers=False)
	console.print(syntax)

@cli.command()
@click.argument('rom_file', type=click.Path(exists=True))
@click.option('--start', '-s', default=0, help='Start offset (hex or decimal)')
@click.option('--length', '-l', help='Number of bytes to analyze')
def analyze(rom_file: str, start: str, length: Optional[int]):
	"""Analyze data patterns in ROM section"""
	analyzer = ROMAnalyzer(rom_file)

	# Parse start offset
	if start.startswith('0x'):
		start_offset = int(start, 16)
	else:
		start_offset = int(start)

	analysis = analyzer.analyze_data_patterns(start_offset, length)

	if "error" in analysis:
		console.print(f"[red]Error: {analysis['error']}[/red]")
		return

	console.print(f"\n[bold]Data Pattern Analysis[/bold]")
	console.print(f"Offset: 0x{analysis['offset']:08x}")
	console.print(f"Size: {analysis['size']:,} bytes")
	console.print(f"Entropy: {analysis['entropy']:.2f} bits")
	console.print(f"Text likelihood: {analysis['text_likelihood']:.1%}")

	if analysis["null_runs"]:
		console.print("\n[yellow]Null byte runs found:[/yellow]")
		for offset, length in analysis["null_runs"][:5]:
			console.print(f"  0x{offset:08x}: {length} bytes")

	# Show most common bytes
	freq = analysis["byte_frequency"]
	most_common = sorted(freq.items(), key=lambda x: x[1], reverse=True)[:10]

	table = Table(title="Most Common Bytes")
	table.add_column("Byte", style="cyan")
	table.add_column("Hex", style="green")
	table.add_column("Count", style="yellow")
	table.add_column("Percentage", style="blue")

	for byte_val, count in most_common:
		percentage = (count / analysis["size"]) * 100
		char = chr(byte_val) if 32 <= byte_val <= 126 else '.'
		table.add_row(
			char,
			f"0x{byte_val:02x}",
			str(count),
			f"{percentage:.1f}%"
		)

	console.print(table)

@cli.command()
@click.argument('rom_file', type=click.Path(exists=True))
@click.option('--min-length', '-m', default=4, help='Minimum string length')
@click.option('--limit', '-l', default=50, help='Maximum strings to show')
def strings(rom_file: str, min_length: int, limit: int):
	"""Find text strings in ROM"""
	analyzer = ROMAnalyzer(rom_file)
	strings = analyzer.find_text_strings(min_length)

	table = Table(title=f"Text Strings (min length: {min_length})")
	table.add_column("Offset", style="cyan", no_wrap=True)
	table.add_column("Length", style="green", no_wrap=True)
	table.add_column("String", style="yellow")

	for offset, string in strings[:limit]:
		# Truncate very long strings for display
		display_string = string[:60] + "..." if len(string) > 60 else string
		table.add_row(
			f"0x{offset:08x}",
			str(len(string)),
			repr(display_string)
		)

	console.print(table)
	console.print(f"\nFound {len(strings)} strings total")

@cli.command()
@click.argument('rom_file', type=click.Path(exists=True))
@click.option('--output', '-o', default='rom_analysis.json', help='Output file path')
def report(rom_file: str, output: str):
	"""Generate comprehensive analysis report"""
	analyzer = ROMAnalyzer(rom_file)

	with console.status("Generating comprehensive analysis report..."):
		analyzer.save_analysis_report(output)

	console.print(f"[green]✅ Comprehensive analysis completed![/green]")
	console.print(f"[blue]Report saved to: {output}[/blue]")

if __name__ == "__main__":
	cli()
