#!/usr/bin/env python3
"""
ROM Comparison and Diff Tool

Compares two Dragon Warrior ROM files and generates detailed difference reports.

Features:
- Byte-by-byte ROM comparison
- Identify changed regions
- Detect modified data types
- Generate visual diff reports
- Export patch suggestions

Usage:
	python tools/rom_diff.py original.nes modified.nes
	python tools/rom_diff.py original.nes modified.nes --detailed
	python tools/rom_diff.py original.nes modified.nes --export diff_report.json

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import os
import argparse
from pathlib import Path
from typing import List, Tuple, Dict, Optional
import struct
import json

# Known data regions
ROM_REGIONS = {
	'header': (0x0000, 0x0010, 'iNES Header'),
	'monster_stats': (0x5e5b, 0x606a, 'Monster Statistics'),
	'spell_data': (0x5f3b, 0x5f82, 'Spell Data'),
	'item_data': (0x5f83, 0x6082, 'Item/Equipment Data'),
	'chr_rom': (0x10010, 0x14010, 'CHR-ROM Graphics'),
	'prg_rom': (0x0010, 0xa010, 'PRG-ROM Code/Data'),
}


class ROMDiff:
	"""Compare two ROM files"""

	def __init__(self, rom1_path: str, rom2_path: str):
		"""
		Initialize ROM differ

		Args:
			rom1_path: Path to first ROM (original)
			rom2_path: Path to second ROM (modified)
		"""
		self.rom1_path = rom1_path
		self.rom2_path = rom2_path
		self.rom1_data = None
		self.rom2_data = None
		self.differences = []

	def load_roms(self) -> bool:
		"""Load both ROM files"""
		# Load ROM 1
		if not os.path.exists(self.rom1_path):
			print(f"❌ ROM 1 not found: {self.rom1_path}")
			return False

		with open(self.rom1_path, 'rb') as f:
			self.rom1_data = bytearray(f.read())

		# Load ROM 2
		if not os.path.exists(self.rom2_path):
			print(f"❌ ROM 2 not found: {self.rom2_path}")
			return False

		with open(self.rom2_path, 'rb') as f:
			self.rom2_data = bytearray(f.read())

		# Validate sizes
		if len(self.rom1_data) != len(self.rom2_data):
			print(f"⚠ Warning: ROM sizes differ:")
			print(f"  ROM 1: {len(self.rom1_data):,} bytes")
			print(f"  ROM 2: {len(self.rom2_data):,} bytes")

			# Truncate to smaller size for comparison
			min_size = min(len(self.rom1_data), len(self.rom2_data))
			self.rom1_data = self.rom1_data[:min_size]
			self.rom2_data = self.rom2_data[:min_size]

		print(f"✓ Loaded ROMs:")
		print(f"  ROM 1: {len(self.rom1_data):,} bytes")
		print(f"  ROM 2: {len(self.rom2_data):,} bytes")

		return True

	def find_differences(self) -> List[Tuple[int, int, int]]:
		"""
		Find all byte differences

		Returns:
			List of (offset, old_byte, new_byte) tuples
		"""
		diffs = []

		for offset in range(len(self.rom1_data)):
			if self.rom1_data[offset] != self.rom2_data[offset]:
				diffs.append((
					offset,
					self.rom1_data[offset],
					self.rom2_data[offset]
				))

		return diffs

	def group_differences(
		self,
		diffs: List[Tuple[int, int, int]],
		max_gap: int = 16
	) -> List[Dict]:
		"""
		Group nearby differences into regions

		Args:
			diffs: List of differences
			max_gap: Maximum gap to consider part of same region

		Returns:
			List of region dicts
		"""
		if not diffs:
			return []

		regions = []
		current_region = {
			'start': diffs[0][0],
			'end': diffs[0][0],
			'changes': [diffs[0]]
		}

		for diff in diffs[1:]:
			offset = diff[0]

			# Check if this diff is close to current region
			if offset - current_region['end'] <= max_gap:
				# Extend current region
				current_region['end'] = offset
				current_region['changes'].append(diff)
			else:
				# Start new region
				regions.append(current_region)
				current_region = {
					'start': offset,
					'end': offset,
					'changes': [diff]
				}

		# Add final region
		regions.append(current_region)

		return regions

	def identify_region_type(self, offset: int) -> Optional[str]:
		"""
		Identify what type of data is at this offset

		Args:
			offset: ROM offset

		Returns:
			Region name or None
		"""
		for name, (start, end, desc) in ROM_REGIONS.items():
			if start <= offset < end:
				return f"{name} ({desc})"

		return "Unknown Region"

	def format_hex_diff(
		self,
		offset: int,
		old_bytes: List[int],
		new_bytes: List[int],
		context: int = 8
	) -> str:
		"""
		Format hex diff with context

		Args:
			offset: Start offset
			old_bytes: Old byte values
			new_bytes: New byte values
			context: Bytes of context before/after

		Returns:
			Formatted hex string
		"""
		lines = []

		# Header
		lines.append(f"Offset: 0x{offset:05X}")
		lines.append("")

		# Old bytes
		old_line = "Old: "
		for i in range(-context, len(old_bytes) + context):
			byte_offset = offset + i

			if 0 <= byte_offset < len(self.rom1_data):
				byte_val = self.rom1_data[byte_offset]

				if i < 0 or i >= len(old_bytes):
					# Context
					old_line += f"{byte_val:02X} "
				else:
					# Changed byte
					old_line += f"[{byte_val:02X}] "

		lines.append(old_line)

		# New bytes
		new_line = "New: "
		for i in range(-context, len(new_bytes) + context):
			byte_offset = offset + i

			if 0 <= byte_offset < len(self.rom2_data):
				byte_val = self.rom2_data[byte_offset]

				if i < 0 or i >= len(new_bytes):
					# Context
					new_line += f"{byte_val:02X} "
				else:
					# Changed byte
					new_line += f"[{byte_val:02X}] "

		lines.append(new_line)
		lines.append("")

		return '\n'.join(lines)

	def analyze_monster_changes(self, region: Dict) -> Optional[Dict]:
		"""
		Analyze changes in monster data region

		Args:
			region: Region dict

		Returns:
			Analysis dict or None
		"""
		monster_start = ROM_REGIONS['monster_stats'][0]
		monster_end = ROM_REGIONS['monster_stats'][1]

		if not (monster_start <= region['start'] < monster_end):
			return None

		# Monster stats are 16 bytes each
		monster_id = (region['start'] - monster_start) // 16
		stat_offset = (region['start'] - monster_start) % 16

		stat_names = [
			'HP', 'Attack', 'Defense', 'Agility', 'Spell',
			'M.Defense', 'XP (low)', 'XP (high)', 'Gold (low)', 'Gold (high)',
			'Resist Sleep', 'Resist Stopspell', 'Resist Hurt',
			'Resist Dodge', 'Unknown1', 'Unknown2'
		]

		stat_name = stat_names[stat_offset] if stat_offset < len(stat_names) else 'Unknown'

		return {
			'type': 'monster_stat',
			'monster_id': monster_id,
			'stat': stat_name,
			'stat_offset': stat_offset
		}

	def generate_report(self, detailed: bool = False) -> Dict:
		"""
		Generate comprehensive diff report

		Args:
			detailed: Include detailed analysis

		Returns:
			Report dict
		"""
		print("\n" + "=" * 70)
		print("ROM Comparison Report")
		print("=" * 70)

		print(f"\nROM 1: {self.rom1_path}")
		print(f"ROM 2: {self.rom2_path}")

		# Find differences
		print("\n--- Finding Differences ---")
		diffs = self.find_differences()

		total_bytes = len(self.rom1_data)
		changed_bytes = len(diffs)
		unchanged_bytes = total_bytes - changed_bytes
		change_percent = (changed_bytes / total_bytes * 100) if total_bytes > 0 else 0

		print(f"Total bytes: {total_bytes:,}")
		print(f"Changed: {changed_bytes:,} ({change_percent:.2f}%)")
		print(f"Unchanged: {unchanged_bytes:,}")

		if changed_bytes == 0:
			print("\n✓ ROMs are identical!")
			return {'identical': True}

		# Group differences into regions
		print("\n--- Grouping Changes ---")
		regions = self.group_differences(diffs)

		print(f"Changed regions: {len(regions)}")

		# Analyze regions
		print("\n--- Changed Regions ---")

		for i, region in enumerate(regions[:20], 1):  # Show top 20
			start = region['start']
			end = region['end']
			size = len(region['changes'])
			region_type = self.identify_region_type(start)

			print(f"\nRegion {i}:")
			print(f"  Offset: 0x{start:05X} - 0x{end:05X}")
			print(f"  Size: {size} bytes")
			print(f"  Type: {region_type}")

			# Monster-specific analysis
			monster_analysis = self.analyze_monster_changes(region)
			if monster_analysis:
				print(f"  Monster: #{monster_analysis['monster_id']}")
				print(f"  Stat: {monster_analysis['stat']}")

			if detailed and size <= 16:
				# Show hex diff for small regions
				old_bytes = [c[1] for c in region['changes']]
				new_bytes = [c[2] for c in region['changes']]

				print("\n" + self.format_hex_diff(start, old_bytes, new_bytes))

		if len(regions) > 20:
			print(f"\n... and {len(regions) - 20} more regions")

		# Summary by region type
		print("\n--- Summary by Region Type ---")

		type_summary = {}
		for region in regions:
			region_type = self.identify_region_type(region['start'])

			if region_type not in type_summary:
				type_summary[region_type] = {
					'regions': 0,
					'bytes': 0
				}

			type_summary[region_type]['regions'] += 1
			type_summary[region_type]['bytes'] += len(region['changes'])

		for region_type, stats in sorted(type_summary.items()):
			print(f"{region_type:30} {stats['regions']:3} regions, {stats['bytes']:5} bytes")

		print("\n" + "=" * 70)

		# Build report dict
		report = {
			'rom1': self.rom1_path,
			'rom2': self.rom2_path,
			'total_bytes': total_bytes,
			'changed_bytes': changed_bytes,
			'unchanged_bytes': unchanged_bytes,
			'change_percent': change_percent,
			'regions': len(regions),
			'region_summary': type_summary,
			'top_regions': [
				{
					'offset': f"0x{r['start']:05X}",
					'size': len(r['changes']),
					'type': self.identify_region_type(r['start'])
				}
				for r in regions[:20]
			]
		}

		return report

	def export_report(self, output_path: str, report: Dict) -> bool:
		"""
		Export report to JSON

		Args:
			output_path: Output file path
			report: Report dict

		Returns:
			True if successful
		"""
		try:
			os.makedirs(os.path.dirname(output_path), exist_ok=True)

			with open(output_path, 'w') as f:
				json.dump(report, f, indent=2)

			print(f"\n✓ Report exported to: {output_path}")
			return True
		except Exception as e:
			print(f"\n❌ Failed to export report: {e}")
			return False


def main():
	"""Main entry point"""
	parser = argparse.ArgumentParser(
		description='Compare two Dragon Warrior ROM files',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  # Basic comparison
  python tools/rom_diff.py original.nes modified.nes

  # Detailed comparison with hex output
  python tools/rom_diff.py original.nes modified.nes --detailed

  # Export report to JSON
  python tools/rom_diff.py original.nes modified.nes --export diff_report.json
		"""
	)

	parser.add_argument(
		'rom1',
		help='First ROM file (original)'
	)

	parser.add_argument(
		'rom2',
		help='Second ROM file (modified)'
	)

	parser.add_argument(
		'--detailed',
		action='store_true',
		help='Show detailed hex diffs'
	)

	parser.add_argument(
		'--export',
		metavar='PATH',
		help='Export report to JSON file'
	)

	args = parser.parse_args()

	# Initialize differ
	differ = ROMDiff(args.rom1, args.rom2)

	if not differ.load_roms():
		return 1

	# Generate report
	report = differ.generate_report(detailed=args.detailed)

	# Export if requested
	if args.export:
		default_path = 'extracted_assets/reports/rom_diff.json'
		output_path = args.export if args.export != 'True' else default_path
		differ.export_report(output_path, report)

	return 0


if __name__ == '__main__':
	sys.exit(main())
