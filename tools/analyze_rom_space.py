#!/usr/bin/env python3
"""
Dragon Warrior ROM Space Analyzer

Analyzes ROM for unused regions, compressible patterns, and optimization opportunities.

Features:
- Identify unused byte sequences (0x00 or 0xff padding)
- Find sparse data regions
- Detect compressible patterns (RLE candidates)
- Calculate potential space savings
- Generate comprehensive space usage report

Usage:
	python tools/analyze_rom_space.py
	python tools/analyze_rom_space.py --rom custom_rom.nes
	python tools/analyze_rom_space.py --detailed
	python tools/analyze_rom_space.py --export-report

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
import struct
from pathlib import Path
from typing import List, Tuple, Dict, Set
from collections import Counter, defaultdict
import argparse
import json

# Default ROM path
DEFAULT_ROM = "roms/Dragon Warrior (U) (PRG1) [!].nes"

# Known data regions in Dragon Warrior ROM
ROM_REGIONS = {
	'header': (0x0000, 0x0010, 'iNES Header'),
	'prg_rom': (0x0010, 0xa010, 'PRG-ROM (40KB)'),
	'chr_rom': (0xa010, 0x14010, 'CHR-ROM (16KB)'),
	'monster_stats': (0x5e5b, 0x606a, 'Monster Statistics'),
	'spell_data': (0x5f3b, 0x5f82, 'Spell Data'),
	'item_data': (0x5f83, 0x6082, 'Item/Equipment Data'),
	'map_data': (0x9000, 0x9fff, 'Map Tile Data (estimated)'),
	'text_data': (0x6400, 0x8fff, 'Text/Dialog Data (estimated)'),
}


class ROMSpaceAnalyzer:
	"""Analyze ROM space usage and optimization opportunities"""

	def __init__(self, rom_path: str):
		"""
		Initialize analyzer with ROM file

		Args:
			rom_path: Path to Dragon Warrior ROM
		"""
		self.rom_path = rom_path
		self.rom_data = None
		self.rom_size = 0

	def load_rom(self) -> bool:
		"""Load and validate ROM file"""
		if not os.path.exists(self.rom_path):
			print(f"❌ ROM file not found: {self.rom_path}")
			return False

		with open(self.rom_path, 'rb') as f:
			self.rom_data = f.read()

		self.rom_size = len(self.rom_data)

		# Validate ROM
		if self.rom_size != 81936:
			print(f"⚠ Warning: ROM size is {self.rom_size} bytes (expected 81936)")

		if self.rom_data[0:4] != b'NES\x1A':
			print(f"❌ Invalid NES header")
			return False

		print(f"✓ Loaded ROM: {self.rom_path}")
		print(f"  Size: {self.rom_size:,} bytes")
		return True

	def find_unused_regions(self, min_size: int = 16) -> List[Tuple[int, int, int]]:
		"""
		Find unused byte sequences (0x00 or 0xff padding)

		Args:
			min_size: Minimum size in bytes to report

		Returns:
			List of (start_offset, size, byte_value) tuples
		"""
		unused_regions = []
		i = 0

		while i < self.rom_size:
			byte_val = self.rom_data[i]

			# Check if this is a padding byte
			if byte_val in [0x00, 0xff]:
				start = i

				# Count consecutive identical bytes
				while i < self.rom_size and self.rom_data[i] == byte_val:
					i += 1

				size = i - start

				# Only report if meets minimum size
				if size >= min_size:
					unused_regions.append((start, size, byte_val))
			else:
				i += 1

		return unused_regions

	def analyze_byte_distribution(self) -> Dict[int, int]:
		"""
		Analyze byte value distribution across ROM

		Returns:
			Dict mapping byte values to occurrence counts
		"""
		return Counter(self.rom_data)

	def find_repeated_sequences(self, min_length: int = 4, min_occurrences: int = 3) -> List[Tuple[bytes, int, List[int]]]:
		"""
		Find repeated byte sequences (potential compression candidates)

		Args:
			min_length: Minimum sequence length
			min_occurrences: Minimum number of occurrences

		Returns:
			List of (sequence, count, [offsets]) tuples
		"""
		sequences = defaultdict(list)

		# Scan for sequences
		for length in range(min_length, min(33, self.rom_size // 100)):  # Up to 32 bytes
			for i in range(self.rom_size - length + 1):
				seq = bytes(self.rom_data[i:i+length])

				# Skip sequences of all same byte (already found by unused_regions)
				if len(set(seq)) > 1:
					sequences[seq].append(i)

		# Filter by minimum occurrences
		repeated = []
		for seq, offsets in sequences.items():
			if len(offsets) >= min_occurrences:
				repeated.append((seq, len(offsets), offsets[:10]))  # Limit offset list

		# Sort by potential savings (length × occurrences)
		repeated.sort(key=lambda x: len(x[0]) * x[1], reverse=True)

		return repeated[:50]  # Top 50 patterns

	def estimate_rle_compression(self, data: bytes) -> Tuple[int, float, int]:
		"""
		Estimate RLE compression ratio

		Args:
			data: Data to analyze

		Returns:
			Tuple of (compressed_size, ratio, savings)
		"""
		compressed_size = 0
		i = 0

		while i < len(data):
			byte_val = data[i]
			count = 1

			# Count consecutive identical bytes
			while i + count < len(data) and data[i + count] == byte_val and count < 255:
				count += 1

			if count >= 3:
				# RLE: marker (1) + count (1) + value (1) = 3 bytes
				compressed_size += 3
				i += count
			else:
				# Store literal
				compressed_size += 1
				i += 1

		ratio = compressed_size / len(data) if len(data) > 0 else 1.0
		savings = len(data) - compressed_size

		return compressed_size, ratio, savings

	def analyze_compressibility(self) -> Dict[str, Dict]:
		"""
		Analyze compression potential for different ROM regions

		Returns:
			Dict mapping region names to compression stats
		"""
		results = {}

		for name, (start, end, desc) in ROM_REGIONS.items():
			if start >= self.rom_size or end > self.rom_size:
				continue

			region_data = self.rom_data[start:end]
			comp_size, ratio, savings = self.estimate_rle_compression(region_data)

			results[name] = {
				'description': desc,
				'offset': f"0x{start:04X}-0x{end:04X}",
				'original_size': len(region_data),
				'compressed_size': comp_size,
				'ratio': ratio,
				'savings': savings,
				'savings_percent': (savings / len(region_data) * 100) if len(region_data) > 0 else 0
			}

		return results

	def find_duplicate_tiles(self) -> List[Tuple[int, List[int]]]:
		"""
		Find duplicate CHR tiles in graphics data

		Returns:
			List of (tile_id, [duplicate_tile_ids])
		"""
		chr_start = 0x10010
		chr_size = 0x4000

		if chr_start + chr_size > self.rom_size:
			return []

		chr_data = self.rom_data[chr_start:chr_start + chr_size]

		tiles = {}
		duplicates = defaultdict(list)

		# Extract all tiles (16 bytes each)
		for i in range(len(chr_data) // 16):
			tile_bytes = bytes(chr_data[i*16:(i+1)*16])

			# Check if this tile already exists
			if tile_bytes in tiles:
				original_id = tiles[tile_bytes]
				duplicates[original_id].append(i)
			else:
				tiles[tile_bytes] = i

		# Convert to list format
		result = [(tile_id, dups) for tile_id, dups in duplicates.items()]
		result.sort(key=lambda x: len(x[1]), reverse=True)

		return result

	def calculate_entropy(self, data: bytes) -> float:
		"""
		Calculate Shannon entropy (randomness measure)

		Args:
			data: Data to analyze

		Returns:
			Entropy value (0 = all same, 8 = maximum randomness)
		"""
		if len(data) == 0:
			return 0.0

		# Count byte frequencies
		freq = Counter(data)

		# Calculate entropy
		import math
		entropy = 0.0
		for count in freq.values():
			probability = count / len(data)
			entropy -= probability * math.log2(probability)

		return entropy

	def generate_report(self, detailed: bool = False) -> Dict:
		"""
		Generate comprehensive space analysis report

		Args:
			detailed: Include detailed analysis

		Returns:
			Report dict
		"""
		print("\n" + "=" * 70)
		print("Dragon Warrior ROM Space Analysis Report")
		print("=" * 70)

		report = {
			'rom_path': self.rom_path,
			'rom_size': self.rom_size,
			'sections': {}
		}

		# 1. Unused Regions Analysis
		print("\n--- Unused Regions (Padding) ---")
		unused = self.find_unused_regions(min_size=16)

		total_unused = sum(size for _, size, _ in unused)
		unused_percent = (total_unused / self.rom_size) * 100

		print(f"Total Unused: {total_unused:,} bytes ({unused_percent:.2f}% of ROM)")
		print(f"Regions Found: {len(unused)}")

		if unused:
			print("\nLargest Unused Regions:")
			for addr, size, byte_val in sorted(unused, key=lambda x: x[1], reverse=True)[:10]:
				print(f"  0x{addr:05X}: {size:4} bytes (0x{byte_val:02X} padding)")

		report['sections']['unused'] = {
			'total_bytes': total_unused,
			'percent': unused_percent,
			'regions': len(unused),
			'top_regions': [
				{'offset': f"0x{addr:05X}", 'size': size, 'byte': f"0x{val:02X}"}
				for addr, size, val in sorted(unused, key=lambda x: x[1], reverse=True)[:10]
			]
		}

		# 2. Compression Analysis
		print("\n--- Compression Potential (RLE) ---")
		compression = self.analyze_compressibility()

		total_original = sum(r['original_size'] for r in compression.values())
		total_compressed = sum(r['compressed_size'] for r in compression.values())
		total_savings = total_original - total_compressed

		print(f"Total Potential Savings: {total_savings:,} bytes")
		print(f"Overall Compression: {(total_compressed/total_original)*100:.1f}%")

		print("\nPer-Region Analysis:")
		for name, stats in compression.items():
			if stats['savings'] > 0:
				print(f"  {stats['description']:30} {stats['savings']:5} bytes saved ({stats['savings_percent']:5.1f}%)")

		report['sections']['compression'] = {
			'total_savings': total_savings,
			'compression_ratio': total_compressed / total_original if total_original > 0 else 1.0,
			'regions': compression
		}

		# 3. Duplicate Tiles Analysis
		print("\n--- CHR Tile Duplicates ---")
		duplicates = self.find_duplicate_tiles()

		total_duplicate_tiles = sum(len(dups) for _, dups in duplicates)
		duplicate_bytes = total_duplicate_tiles * 16

		print(f"Duplicate Tiles: {total_duplicate_tiles}")
		print(f"Wasted Space: {duplicate_bytes:,} bytes")

		if duplicates:
			print("\nTop Duplicate Tiles:")
			for tile_id, dups in duplicates[:10]:
				print(f"  Tile 0x{tile_id:03X}: {len(dups)} duplicates")

		report['sections']['duplicates'] = {
			'total_tiles': total_duplicate_tiles,
			'wasted_bytes': duplicate_bytes,
			'unique_duplicated': len(duplicates),
			'top_duplicates': [
				{'tile_id': f"0x{tid:03X}", 'count': len(dups)}
				for tid, dups in duplicates[:10]
			]
		}

		# 4. Byte Distribution (if detailed)
		if detailed:
			print("\n--- Byte Value Distribution ---")
			distribution = self.analyze_byte_distribution()

			# Find most/least common bytes
			most_common = distribution.most_common(10)
			least_common = [(b, c) for b, c in distribution.items() if c > 0]
			least_common.sort(key=lambda x: x[1])
			least_common = least_common[:10]

			print("\nMost Common Bytes:")
			for byte_val, count in most_common:
				percent = (count / self.rom_size) * 100
				print(f"  0x{byte_val:02X}: {count:6} times ({percent:5.2f}%)")

			print("\nLeast Common Bytes:")
			for byte_val, count in least_common:
				print(f"  0x{byte_val:02X}: {count:6} times")

			report['sections']['distribution'] = {
				'most_common': [{'byte': f"0x{b:02X}", 'count': c} for b, c in most_common],
				'least_common': [{'byte': f"0x{b:02X}", 'count': c} for b, c in least_common]
			}

		# 5. Repeated Sequences (if detailed)
		if detailed:
			print("\n--- Repeated Sequences (Dictionary Compression Candidates) ---")
			repeated = self.find_repeated_sequences(min_length=4, min_occurrences=3)

			if repeated:
				print("\nTop Repeated Patterns:")
				for seq, count, offsets in repeated[:15]:
					savings = (len(seq) - 2) * count  # 2 bytes for reference
					print(f"  {len(seq):2} bytes × {count:3} times = {savings:5} bytes saved")
					print(f"    Pattern: {seq[:16].hex()}")

			total_seq_savings = sum((len(seq) - 2) * count for seq, count, _ in repeated)
			print(f"\nTotal Dictionary Compression Potential: {total_seq_savings:,} bytes")

			report['sections']['sequences'] = {
				'patterns_found': len(repeated),
				'potential_savings': total_seq_savings,
				'top_patterns': [
					{
						'length': len(seq),
						'count': count,
						'savings': (len(seq) - 2) * count,
						'pattern': seq[:16].hex()
					}
					for seq, count, _ in repeated[:15]
				]
			}

		# 6. Summary
		print("\n" + "=" * 70)
		print("Optimization Summary")
		print("=" * 70)

		total_potential = total_unused + total_savings + duplicate_bytes
		if detailed and 'sequences' in report['sections']:
			total_potential += report['sections']['sequences']['potential_savings']

		print(f"\nTotal Optimization Potential: {total_potential:,} bytes")
		print(f"Percentage of ROM: {(total_potential / self.rom_size) * 100:.2f}%")

		print("\nBreakdown:")
		print(f"  Unused Regions:     {total_unused:7,} bytes")
		print(f"  RLE Compression:    {total_savings:7,} bytes")
		print(f"  Duplicate Tiles:    {duplicate_bytes:7,} bytes")
		if detailed and 'sequences' in report['sections']:
			seq_savings = report['sections']['sequences']['potential_savings']
			print(f"  Dictionary Comp:    {seq_savings:7,} bytes")

		report['summary'] = {
			'total_potential': total_potential,
			'percent_of_rom': (total_potential / self.rom_size) * 100,
			'breakdown': {
				'unused': total_unused,
				'rle_compression': total_savings,
				'duplicate_tiles': duplicate_bytes
			}
		}

		if detailed and 'sequences' in report['sections']:
			report['summary']['breakdown']['dictionary'] = report['sections']['sequences']['potential_savings']

		print("\n" + "=" * 70)

		return report

	def export_report(self, output_path: str, report: Dict) -> bool:
		"""
		Export report to JSON file

		Args:
			output_path: Path for JSON output
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
		description='Analyze Dragon Warrior ROM space usage and optimization opportunities',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  python tools/analyze_rom_space.py
  python tools/analyze_rom_space.py --rom custom_rom.nes
  python tools/analyze_rom_space.py --detailed
  python tools/analyze_rom_space.py --export-report space_analysis.json
		"""
	)

	parser.add_argument(
		'--rom',
		default=DEFAULT_ROM,
		help=f'Path to Dragon Warrior ROM (default: {DEFAULT_ROM})'
	)

	parser.add_argument(
		'--detailed',
		action='store_true',
		help='Include detailed analysis (byte distribution, repeated sequences)'
	)

	parser.add_argument(
		'--export-report',
		metavar='PATH',
		help='Export report to JSON file'
	)

	parser.add_argument(
		'--min-unused',
		type=int,
		default=16,
		help='Minimum unused region size to report (default: 16 bytes)'
	)

	args = parser.parse_args()

	# Initialize analyzer
	analyzer = ROMSpaceAnalyzer(args.rom)

	if not analyzer.load_rom():
		return 1

	# Generate report
	report = analyzer.generate_report(detailed=args.detailed)

	# Export if requested
	if args.export_report:
		default_path = 'extracted_assets/reports/rom_space_analysis.json'
		output_path = args.export_report if args.export_report != 'True' else default_path
		analyzer.export_report(output_path, report)

	return 0


if __name__ == '__main__':
	sys.exit(main())
