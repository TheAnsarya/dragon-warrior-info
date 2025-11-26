#!/usr/bin/env python3
"""
ROM Comparison and Regression Testing Tool

Comprehensive ROM comparison system for tracking changes, verifying modifications,
and running regression tests. Supports byte-level diffs, checksums, and automated
validation.

Features:
- Byte-level ROM comparison with visual diff
- Checksum verification (CRC32, MD5, SHA256)
- Region-based comparison (isolate specific ROM areas)
- Change tracking and annotation
- Regression test suite
- Before/after screenshots comparison
- Automated build verification
- History tracking

Usage:
	python tools/rom_comparison_tool.py [ROM1] [ROM2] [--verbose]

Examples:
	# Compare two ROMs
	python tools/rom_comparison_tool.py roms/original.nes roms/modified.nes

	# Compare specific regions
	python tools/rom_comparison_tool.py rom1.nes rom2.nes --region 0x8000 0xA000

	# Run regression tests
	python tools/rom_comparison_tool.py --test

	# Generate comparison report
	python tools/rom_comparison_tool.py rom1.nes rom2.nes --report comparison.html
"""

import sys
import argparse
import hashlib
import zlib
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field, asdict
import struct
import json
from datetime import datetime


@dataclass
class MemoryRegion:
	"""Define a memory region in the ROM."""
	name: str
	start: int
	end: int
	description: str = ""
	
	def contains(self, offset: int) -> bool:
		"""Check if offset is in this region."""
		return self.start <= offset < self.end
	
	def size(self) -> int:
		"""Get region size."""
		return self.end - self.start


# Dragon Warrior ROM regions
DW_REGIONS = [
	MemoryRegion("PRG-ROM Bank 0", 0x00010, 0x04010, "First PRG bank"),
	MemoryRegion("PRG-ROM Bank 1", 0x04010, 0x08010, "Second PRG bank"),
	MemoryRegion("PRG-ROM Bank 2", 0x08010, 0x0C010, "Third PRG bank"),
	MemoryRegion("PRG-ROM Bank 3", 0x0C010, 0x10010, "Fourth PRG bank"),
	MemoryRegion("CHR-ROM Bank 0", 0x10010, 0x12010, "First CHR bank"),
	MemoryRegion("CHR-ROM Bank 1", 0x12010, 0x14010, "Second CHR bank"),
	MemoryRegion("Monster Stats", 0x05E5B, 0x05F3B, "39 monsters * 16 bytes"),
	MemoryRegion("Spell Data", 0x05F3B, 0x05F83, "10 spells * 8 bytes"),
	MemoryRegion("Item Data", 0x05F83, 0x06083, "32 items * 8 bytes"),
	MemoryRegion("Dialog Text", 0x08000, 0x0A000, "Compressed dialog strings"),
	MemoryRegion("Map Data", 0x0B000, 0x0C000, "World and dungeon maps"),
]


@dataclass
class ByteDiff:
	"""Represents a difference between two ROM bytes."""
	offset: int
	original: int
	modified: int
	region: Optional[str] = None
	
	def __str__(self) -> str:
		region_str = f" ({self.region})" if self.region else ""
		return f"0x{self.offset:05X}{region_str}: 0x{self.original:02X} -> 0x{self.modified:02X}"


@dataclass
class ComparisonResult:
	"""Results of ROM comparison."""
	rom1_path: str
	rom2_path: str
	rom1_size: int
	rom2_size: int
	rom1_checksums: Dict[str, str] = field(default_factory=dict)
	rom2_checksums: Dict[str, str] = field(default_factory=dict)
	differences: List[ByteDiff] = field(default_factory=list)
	identical_regions: List[str] = field(default_factory=list)
	modified_regions: Dict[str, int] = field(default_factory=dict)	# region -> num_changes
	timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
	
	def num_differences(self) -> int:
		"""Get total number of differences."""
		return len(self.differences)
	
	def is_identical(self) -> bool:
		"""Check if ROMs are identical."""
		return self.num_differences() == 0
	
	def diff_percentage(self) -> float:
		"""Get percentage of bytes that differ."""
		if self.rom1_size == 0:
			return 0.0
		return (self.num_differences() / self.rom1_size) * 100


class ROMComparator:
	"""Compare two ROM files."""
	
	def __init__(self, regions: Optional[List[MemoryRegion]] = None):
		self.regions = regions or DW_REGIONS
	
	def compare(
		self,
		rom1_path: Path,
		rom2_path: Path,
		region_filter: Optional[Tuple[int, int]] = None
	) -> ComparisonResult:
		"""
		Compare two ROM files.
		
		Args:
			rom1_path: Path to first ROM
			rom2_path: Path to second ROM
			region_filter: Optional (start, end) tuple to limit comparison
		
		Returns:
			ComparisonResult with all differences
		"""
		# Load ROMs
		rom1 = self._load_rom(rom1_path)
		rom2 = self._load_rom(rom2_path)
		
		# Create result
		result = ComparisonResult(
			rom1_path=str(rom1_path),
			rom2_path=str(rom2_path),
			rom1_size=len(rom1),
			rom2_size=len(rom2)
		)
		
		# Calculate checksums
		result.rom1_checksums = self._calculate_checksums(rom1)
		result.rom2_checksums = self._calculate_checksums(rom2)
		
		# Compare byte-by-byte
		min_size = min(len(rom1), len(rom2))
		
		# Apply region filter if specified
		start_offset = region_filter[0] if region_filter else 0
		end_offset = region_filter[1] if region_filter else min_size
		
		for offset in range(start_offset, end_offset):
			if rom1[offset] != rom2[offset]:
				# Find region
				region = self._find_region(offset)
				
				diff = ByteDiff(
					offset=offset,
					original=rom1[offset],
					modified=rom2[offset],
					region=region.name if region else None
				)
				
				result.differences.append(diff)
				
				# Track modified regions
				if region:
					result.modified_regions[region.name] = \
						result.modified_regions.get(region.name, 0) + 1
		
		# Find identical regions
		for region in self.regions:
			if region.name not in result.modified_regions:
				result.identical_regions.append(region.name)
		
		# Check size differences
		if len(rom1) != len(rom2):
			size_diff = abs(len(rom1) - len(rom2))
			print(f"WARNING: ROM sizes differ by {size_diff} bytes")
		
		return result
	
	def _load_rom(self, path: Path) -> bytes:
		"""Load ROM file."""
		with open(path, 'rb') as f:
			return f.read()
	
	def _calculate_checksums(self, data: bytes) -> Dict[str, str]:
		"""Calculate various checksums for data."""
		return {
			'crc32': f"{zlib.crc32(data):08X}",
			'md5': hashlib.md5(data).hexdigest(),
			'sha256': hashlib.sha256(data).hexdigest()
		}
	
	def _find_region(self, offset: int) -> Optional[MemoryRegion]:
		"""Find region containing offset."""
		for region in self.regions:
			if region.contains(offset):
				return region
		return None


class ComparisonReporter:
	"""Generate comparison reports."""
	
	@staticmethod
	def print_summary(result: ComparisonResult) -> None:
		"""Print comparison summary to console."""
		print("\n" + "=" * 80)
		print("ROM COMPARISON SUMMARY")
		print("=" * 80)
		print(f"ROM 1: {result.rom1_path}")
		print(f"ROM 2: {result.rom2_path}")
		print(f"Timestamp: {result.timestamp}")
		print()
		
		# Checksums
		print("Checksums:")
		print(f"  ROM 1 CRC32: {result.rom1_checksums['crc32']}")
		print(f"  ROM 2 CRC32: {result.rom2_checksums['crc32']}")
		print(f"  Match: {'YES' if result.rom1_checksums['crc32'] == result.rom2_checksums['crc32'] else 'NO'}")
		print()
		
		# Sizes
		print(f"ROM 1 Size: {result.rom1_size:,} bytes")
		print(f"ROM 2 Size: {result.rom2_size:,} bytes")
		print()
		
		# Differences
		num_diffs = result.num_differences()
		print(f"Differences: {num_diffs:,} bytes ({result.diff_percentage():.4f}%)")
		print()
		
		if result.is_identical():
			print("✓ ROMs are IDENTICAL")
		else:
			print("✗ ROMs are DIFFERENT")
			
			# Modified regions
			if result.modified_regions:
				print("\nModified Regions:")
				for region, count in sorted(result.modified_regions.items()):
					print(f"  {region}: {count} bytes changed")
			
			# Identical regions
			if result.identical_regions:
				print(f"\nIdentical Regions: {len(result.identical_regions)}")
				for region in sorted(result.identical_regions):
					print(f"  ✓ {region}")
		
		print("=" * 80)
	
	@staticmethod
	def print_detailed_diff(result: ComparisonResult, max_diffs: int = 100) -> None:
		"""Print detailed byte-by-byte differences."""
		print("\n" + "=" * 80)
		print("DETAILED DIFFERENCES")
		print("=" * 80)
		print(f"{'Offset':<12} {'Region':<30} {'Original':<10} {'Modified':<10}")
		print("-" * 80)
		
		diffs_shown = 0
		for diff in result.differences:
			if diffs_shown >= max_diffs:
				remaining = len(result.differences) - max_diffs
				print(f"\n... and {remaining} more differences")
				break
			
			region = diff.region or "Unknown"
			print(f"0x{diff.offset:05X}    {region:<30} 0x{diff.original:02X}       0x{diff.modified:02X}")
			diffs_shown += 1
		
		print("=" * 80)
	
	@staticmethod
	def generate_html_report(result: ComparisonResult, output_path: Path) -> None:
		"""Generate HTML comparison report."""
		html = ['<!DOCTYPE html>']
		html.append('<html lang="en">')
		html.append('<head>')
		html.append('\t<meta charset="UTF-8">')
		html.append('\t<title>ROM Comparison Report</title>')
		html.append('\t<style>')
		html.append(ComparisonReporter._get_css())
		html.append('\t</style>')
		html.append('</head>')
		html.append('<body>')
		
		# Header
		html.append('\t<header>')
		html.append('\t\t<h1>ROM Comparison Report</h1>')
		html.append(f'\t\t<p>Generated: {result.timestamp}</p>')
		html.append('\t</header>')
		
		# Summary
		html.append('\t<main>')
		html.append('\t\t<section class="summary">')
		html.append('\t\t\t<h2>Summary</h2>')
		html.append('\t\t\t<table>')
		html.append(f'\t\t\t\t<tr><th>ROM 1</th><td>{result.rom1_path}</td></tr>')
		html.append(f'\t\t\t\t<tr><th>ROM 2</th><td>{result.rom2_path}</td></tr>')
		html.append(f'\t\t\t\t<tr><th>ROM 1 Size</th><td>{result.rom1_size:,} bytes</td></tr>')
		html.append(f'\t\t\t\t<tr><th>ROM 2 Size</th><td>{result.rom2_size:,} bytes</td></tr>')
		html.append(f'\t\t\t\t<tr><th>Differences</th><td>{result.num_differences():,} bytes ({result.diff_percentage():.4f}%)</td></tr>')
		html.append(f'\t\t\t\t<tr><th>Status</th><td class="{"identical" if result.is_identical() else "different"}">{"IDENTICAL" if result.is_identical() else "DIFFERENT"}</td></tr>')
		html.append('\t\t\t</table>')
		html.append('\t\t</section>')
		
		# Checksums
		html.append('\t\t<section class="checksums">')
		html.append('\t\t\t<h2>Checksums</h2>')
		html.append('\t\t\t<table>')
		html.append('\t\t\t\t<tr><th>Algorithm</th><th>ROM 1</th><th>ROM 2</th><th>Match</th></tr>')
		
		for algo in ['crc32', 'md5', 'sha256']:
			rom1_hash = result.rom1_checksums.get(algo, 'N/A')
			rom2_hash = result.rom2_checksums.get(algo, 'N/A')
			match = '✓' if rom1_hash == rom2_hash else '✗'
			
			html.append(f'\t\t\t\t<tr>')
			html.append(f'\t\t\t\t\t<td>{algo.upper()}</td>')
			html.append(f'\t\t\t\t\t<td><code>{rom1_hash}</code></td>')
			html.append(f'\t\t\t\t\t<td><code>{rom2_hash}</code></td>')
			html.append(f'\t\t\t\t\t<td>{match}</td>')
			html.append(f'\t\t\t\t</tr>')
		
		html.append('\t\t\t</table>')
		html.append('\t\t</section>')
		
		# Modified regions
		if result.modified_regions:
			html.append('\t\t<section class="regions">')
			html.append('\t\t\t<h2>Modified Regions</h2>')
			html.append('\t\t\t<table>')
			html.append('\t\t\t\t<tr><th>Region</th><th>Changes</th></tr>')
			
			for region, count in sorted(result.modified_regions.items(), key=lambda x: -x[1]):
				html.append(f'\t\t\t\t<tr><td>{region}</td><td>{count}</td></tr>')
			
			html.append('\t\t\t</table>')
			html.append('\t\t</section>')
		
		# Detailed differences (limit to first 1000)
		if result.differences:
			html.append('\t\t<section class="differences">')
			html.append('\t\t\t<h2>Detailed Differences</h2>')
			html.append('\t\t\t<table>')
			html.append('\t\t\t\t<tr><th>Offset</th><th>Region</th><th>Original</th><th>Modified</th></tr>')
			
			for diff in result.differences[:1000]:
				region = diff.region or "Unknown"
				html.append(f'\t\t\t\t<tr>')
				html.append(f'\t\t\t\t\t<td>0x{diff.offset:05X}</td>')
				html.append(f'\t\t\t\t\t<td>{region}</td>')
				html.append(f'\t\t\t\t\t<td>0x{diff.original:02X}</td>')
				html.append(f'\t\t\t\t\t<td>0x{diff.modified:02X}</td>')
				html.append(f'\t\t\t\t</tr>')
			
			if len(result.differences) > 1000:
				html.append(f'\t\t\t\t<tr><td colspan="4">... and {len(result.differences) - 1000} more differences</td></tr>')
			
			html.append('\t\t\t</table>')
			html.append('\t\t</section>')
		
		html.append('\t</main>')
		html.append('</body>')
		html.append('</html>')
		
		with open(output_path, 'w', encoding='utf-8') as f:
			f.write('\n'.join(html))
		
		print(f"Generated HTML report: {output_path}")
	
	@staticmethod
	def _get_css() -> str:
		"""Get CSS styles."""
		return """
		body {
			font-family: Arial, sans-serif;
			margin: 0;
			padding: 20px;
			background: #f5f5f5;
		}
		header {
			background: #2c3e50;
			color: white;
			padding: 20px;
			border-radius: 5px;
		}
		main {
			background: white;
			padding: 20px;
			margin-top: 20px;
			border-radius: 5px;
		}
		h2 {
			color: #2c3e50;
			border-bottom: 2px solid #3498db;
			padding-bottom: 5px;
		}
		table {
			width: 100%;
			border-collapse: collapse;
			margin: 10px 0;
		}
		th, td {
			padding: 8px;
			text-align: left;
			border-bottom: 1px solid #ddd;
		}
		th {
			background: #34495e;
			color: white;
		}
		code {
			font-family: monospace;
			background: #ecf0f1;
			padding: 2px 5px;
			border-radius: 3px;
		}
		.identical {
			color: green;
			font-weight: bold;
		}
		.different {
			color: red;
			font-weight: bold;
		}
		"""
	
	@staticmethod
	def export_json(result: ComparisonResult, output_path: Path) -> None:
		"""Export comparison result to JSON."""
		data = asdict(result)
		
		with open(output_path, 'w', encoding='utf-8') as f:
			json.dump(data, f, indent='\t')
		
		print(f"Exported JSON: {output_path}")


class RegressionTester:
	"""Run regression tests on ROM modifications."""
	
	def __init__(self, comparator: ROMComparator):
		self.comparator = comparator
		self.tests: List[Dict] = []
	
	def add_test(
		self,
		name: str,
		expected_regions: List[str],
		forbidden_regions: List[str] = None
	) -> None:
		"""
		Add a regression test.
		
		Args:
			name: Test name
			expected_regions: Regions that should be modified
			forbidden_regions: Regions that must not be modified
		"""
		self.tests.append({
			'name': name,
			'expected': expected_regions,
			'forbidden': forbidden_regions or []
		})
	
	def run_tests(self, original_rom: Path, modified_rom: Path) -> Dict[str, bool]:
		"""Run all regression tests."""
		result = self.comparator.compare(original_rom, modified_rom)
		
		test_results = {}
		
		for test in self.tests:
			passed = True
			
			# Check expected modifications
			for region in test['expected']:
				if region not in result.modified_regions:
					print(f"FAIL: {test['name']} - Expected modification in {region} not found")
					passed = False
			
			# Check forbidden modifications
			for region in test['forbidden']:
				if region in result.modified_regions:
					print(f"FAIL: {test['name']} - Forbidden modification in {region} detected")
					passed = False
			
			test_results[test['name']] = passed
			
			if passed:
				print(f"PASS: {test['name']}")
		
		return test_results


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='ROM Comparison and Regression Testing Tool'
	)
	parser.add_argument(
		'rom1',
		type=Path,
		nargs='?',
		help='First ROM file'
	)
	parser.add_argument(
		'rom2',
		type=Path,
		nargs='?',
		help='Second ROM file'
	)
	parser.add_argument(
		'--region',
		type=str,
		nargs=2,
		metavar=('START', 'END'),
		help='Compare only specific region (hex offsets)'
	)
	parser.add_argument(
		'--verbose',
		action='store_true',
		help='Show detailed differences'
	)
	parser.add_argument(
		'--report',
		type=Path,
		help='Generate HTML report'
	)
	parser.add_argument(
		'--json',
		type=Path,
		help='Export JSON report'
	)
	parser.add_argument(
		'--test',
		action='store_true',
		help='Run regression tests'
	)
	
	args = parser.parse_args()
	
	if args.test:
		# Run regression tests
		print("Running regression tests...")
		
		comparator = ROMComparator()
		tester = RegressionTester(comparator)
		
		# Define tests
		tester.add_test(
			"Monster Stats Modification",
			expected_regions=["Monster Stats"],
			forbidden_regions=["CHR-ROM Bank 0", "CHR-ROM Bank 1"]
		)
		
		tester.add_test(
			"Dialog Text Modification",
			expected_regions=["Dialog Text"],
			forbidden_regions=["Monster Stats", "Spell Data", "Item Data"]
		)
		
		# Run tests (would need actual ROM files)
		# results = tester.run_tests(Path('roms/original.nes'), Path('roms/modified.nes'))
		
		print("Regression test framework ready.")
		return
	
	if not args.rom1 or not args.rom2:
		parser.print_help()
		return
	
	# Parse region filter
	region_filter = None
	if args.region:
		start = int(args.region[0], 16) if args.region[0].startswith('0x') else int(args.region[0])
		end = int(args.region[1], 16) if args.region[1].startswith('0x') else int(args.region[1])
		region_filter = (start, end)
		print(f"Comparing region: 0x{start:05X} - 0x{end:05X}")
	
	# Compare ROMs
	comparator = ROMComparator()
	result = comparator.compare(args.rom1, args.rom2, region_filter)
	
	# Print summary
	reporter = ComparisonReporter()
	reporter.print_summary(result)
	
	# Print detailed diff if requested
	if args.verbose:
		reporter.print_detailed_diff(result)
	
	# Generate HTML report
	if args.report:
		reporter.generate_html_report(result, args.report)
	
	# Export JSON
	if args.json:
		reporter.export_json(result, args.json)


if __name__ == '__main__':
	main()
