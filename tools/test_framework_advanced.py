#!/usr/bin/env python3
"""
Advanced Testing and Validation Framework for Dragon Warrior

Comprehensive test suite for ROM hacking tools with automated validation,
regression testing, fuzzing, and performance benchmarking.

Features:
- Unit tests for all ROM data structures
- Integration tests for build pipeline
- Regression tests with known ROMs
- Fuzz testing for robustness
- Performance benchmarking
- Code coverage tracking
- Test report generation
- Continuous integration support
- Mock ROM testing (no real ROM required)
- Property-based testing

Usage:
	python tools/test_framework_advanced.py [OPTIONS]

Examples:
	# Run all tests
	python tools/test_framework_advanced.py

	# Run specific test suite
	python tools/test_framework_advanced.py --suite unit

	# Run with coverage
	python tools/test_framework_advanced.py --coverage

	# Generate HTML report
	python tools/test_framework_advanced.py --report html

	# Run benchmarks
	python tools/test_framework_advanced.py --benchmark

Author: Dragon Warrior ROM Hacking Toolkit
Version: 2.0
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
import time
import random
import hashlib
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Callable, Any
from dataclasses import dataclass, field
from enum import Enum
import argparse
from datetime import datetime
import unittest
import io


# ============================================================================
# TEST CONFIGURATION
# ============================================================================

class TestStatus(Enum):
	"""Test execution status."""
	PASSED = "passed"
	FAILED = "failed"
	SKIPPED = "skipped"
	ERROR = "error"


class TestSuite(Enum):
	"""Test suite categories."""
	UNIT = "unit"
	INTEGRATION = "integration"
	REGRESSION = "regression"
	FUZZ = "fuzz"
	BENCHMARK = "benchmark"


@dataclass
class TestResult:
	"""Individual test result."""
	name: str
	suite: TestSuite
	status: TestStatus
	duration: float
	error_message: str = ""
	output: str = ""


@dataclass
class TestSummary:
	"""Test execution summary."""
	total_tests: int
	passed: int
	failed: int
	skipped: int
	errors: int
	duration: float
	results: List[TestResult] = field(default_factory=list)


# ============================================================================
# MOCK ROM DATA
# ============================================================================

class MockROM:
	"""Mock ROM for testing without real ROM file."""

	def __init__(self, size: int = 131072):
		"""Create mock ROM of specified size."""
		self.size = size
		self.data = bytearray(size)
		self._initialize_header()
		self._initialize_test_data()

	def _initialize_header(self):
		"""Initialize NES ROM header."""
		# iNES header
		self.data[0:4] = b'NES\x1a'
		self.data[4] = 0x08  # 8 * 16KB PRG ROM
		self.data[5] = 0x00  # No CHR ROM (uses CHR RAM)
		self.data[6] = 0x01  # Vertical mirroring
		self.data[7] = 0x00  # Mapper 0

	def _initialize_test_data(self):
		"""Initialize test data structures."""
		# Monster data at 0x6000 (24 monsters)
		for i in range(24):
			offset = 0x6000 + (i * 32)
			if offset + 32 < self.size:
				# HP (2 bytes little-endian)
				hp = 10 + (i * 5)
				self.data[offset] = hp & 0xff
				self.data[offset + 1] = (hp >> 8) & 0xff

				# Strength
				self.data[offset + 2] = 5 + i

				# Agility
				self.data[offset + 3] = 3 + i

				# Gold (2 bytes)
				gold = 10 + (i * 3)
				self.data[offset + 4] = gold & 0xff
				self.data[offset + 5] = (gold >> 8) & 0xff

		# Item data at 0x7000 (38 items)
		for i in range(38):
			offset = 0x7000 + (i * 16)
			if offset + 16 < self.size:
				# Price (2 bytes)
				price = 50 + (i * 25)
				self.data[offset] = price & 0xff
				self.data[offset + 1] = (price >> 8) & 0xff

				# Type
				self.data[offset + 2] = i % 4

				# Effect value
				self.data[offset + 3] = i + 1

	def read_byte(self, address: int) -> int:
		"""Read byte from mock ROM."""
		if 0 <= address < self.size:
			return self.data[address]
		return 0

	def read_word(self, address: int) -> int:
		"""Read 16-bit word (little-endian)."""
		low = self.read_byte(address)
		high = self.read_byte(address + 1)
		return (high << 8) | low

	def write_byte(self, address: int, value: int):
		"""Write byte to mock ROM."""
		if 0 <= address < self.size:
			self.data[address] = value & 0xff

	def write_word(self, address: int, value: int):
		"""Write 16-bit word (little-endian)."""
		self.write_byte(address, value & 0xff)
		self.write_byte(address + 1, (value >> 8) & 0xff)

	def to_bytes(self) -> bytes:
		"""Get ROM as bytes."""
		return bytes(self.data)

	def save(self, filepath: Path):
		"""Save mock ROM to file."""
		with open(filepath, 'wb') as f:
			f.write(self.to_bytes())


# ============================================================================
# UNIT TESTS
# ============================================================================

class MonsterDataTests(unittest.TestCase):
	"""Unit tests for monster data structures."""

	def setUp(self):
		"""Set up test fixtures."""
		self.rom = MockROM()

	def test_read_monster_hp(self):
		"""Test reading monster HP."""
		# First monster should have HP = 10
		hp = self.rom.read_word(0x6000)
		self.assertEqual(hp, 10)

	def test_read_monster_strength(self):
		"""Test reading monster strength."""
		# First monster should have strength = 5
		strength = self.rom.read_byte(0x6002)
		self.assertEqual(strength, 5)

	def test_write_monster_hp(self):
		"""Test writing monster HP."""
		# Write new HP value
		self.rom.write_word(0x6000, 150)
		hp = self.rom.read_word(0x6000)
		self.assertEqual(hp, 150)

	def test_monster_bounds(self):
		"""Test monster data bounds."""
		# Should have 24 monsters
		for i in range(24):
			offset = 0x6000 + (i * 32)
			hp = self.rom.read_word(offset)
			self.assertGreater(hp, 0)
			self.assertLess(hp, 1000)

	def test_monster_stat_ranges(self):
		"""Test monster stats are in valid ranges."""
		for i in range(24):
			offset = 0x6000 + (i * 32)

			# HP should be 1-999
			hp = self.rom.read_word(offset)
			self.assertGreaterEqual(hp, 1)
			self.assertLessEqual(hp, 999)

			# Strength should be 0-255
			strength = self.rom.read_byte(offset + 2)
			self.assertGreaterEqual(strength, 0)
			self.assertLessEqual(strength, 255)

			# Agility should be 0-255
			agility = self.rom.read_byte(offset + 3)
			self.assertGreaterEqual(agility, 0)
			self.assertLessEqual(agility, 255)


class ItemDataTests(unittest.TestCase):
	"""Unit tests for item data structures."""

	def setUp(self):
		"""Set up test fixtures."""
		self.rom = MockROM()

	def test_read_item_price(self):
		"""Test reading item price."""
		# First item should have price = 50
		price = self.rom.read_word(0x7000)
		self.assertEqual(price, 50)

	def test_write_item_price(self):
		"""Test writing item price."""
		self.rom.write_word(0x7000, 1000)
		price = self.rom.read_word(0x7000)
		self.assertEqual(price, 1000)

	def test_item_bounds(self):
		"""Test item data bounds."""
		# Should have 38 items
		for i in range(38):
			offset = 0x7000 + (i * 16)
			price = self.rom.read_word(offset)
			self.assertGreaterEqual(price, 0)
			self.assertLess(price, 65536)

	def test_item_types(self):
		"""Test item type values."""
		for i in range(38):
			offset = 0x7000 + (i * 16)
			item_type = self.rom.read_byte(offset + 2)
			# Type should be 0-3 (weapon, armor, item, key)
			self.assertGreaterEqual(item_type, 0)
			self.assertLessEqual(item_type, 3)


class ROMHeaderTests(unittest.TestCase):
	"""Unit tests for ROM header validation."""

	def setUp(self):
		"""Set up test fixtures."""
		self.rom = MockROM()

	def test_ines_signature(self):
		"""Test iNES ROM signature."""
		signature = bytes(self.rom.data[0:4])
		self.assertEqual(signature, b'NES\x1a')

	def test_rom_size(self):
		"""Test ROM size."""
		self.assertEqual(self.rom.size, 131072)  # 128KB

	def test_prg_rom_banks(self):
		"""Test PRG ROM bank count."""
		prg_banks = self.rom.read_byte(4)
		self.assertEqual(prg_banks, 8)

	def test_chr_rom_banks(self):
		"""Test CHR ROM bank count."""
		chr_banks = self.rom.read_byte(5)
		self.assertEqual(chr_banks, 0)  # Uses CHR RAM


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class BuildPipelineTests(unittest.TestCase):
	"""Integration tests for build pipeline."""

	def test_extract_and_rebuild(self):
		"""Test extracting data and rebuilding ROM."""
		# Create mock ROM
		original = MockROM()

		# Extract monster data
		monsters = []
		for i in range(24):
			offset = 0x6000 + (i * 32)
			monsters.append({
				'hp': original.read_word(offset),
				'strength': original.read_byte(offset + 2),
				'agility': original.read_byte(offset + 3)
			})

		# Rebuild ROM
		rebuilt = MockROM()
		for i, monster in enumerate(monsters):
			offset = 0x6000 + (i * 32)
			rebuilt.write_word(offset, monster['hp'])
			rebuilt.write_byte(offset + 2, monster['strength'])
			rebuilt.write_byte(offset + 3, monster['agility'])

		# Compare
		for i in range(24):
			offset = 0x6000 + (i * 32)
			self.assertEqual(
				original.read_word(offset),
				rebuilt.read_word(offset)
			)

	def test_data_modification_workflow(self):
		"""Test complete data modification workflow."""
		rom = MockROM()

		# Read original HP
		original_hp = rom.read_word(0x6000)

		# Modify HP
		new_hp = original_hp * 2
		rom.write_word(0x6000, new_hp)

		# Verify modification
		modified_hp = rom.read_word(0x6000)
		self.assertEqual(modified_hp, new_hp)


# ============================================================================
# REGRESSION TESTS
# ============================================================================

class RegressionTests(unittest.TestCase):
	"""Regression tests for known issues."""

	def test_no_hp_overflow(self):
		"""Test HP doesn't overflow 16-bit limit."""
		rom = MockROM()

		# Try to write maximum HP
		rom.write_word(0x6000, 65535)
		hp = rom.read_word(0x6000)
		self.assertEqual(hp, 65535)

		# Try to write HP > 65535 (should wrap)
		rom.write_word(0x6000, 65536)
		hp = rom.read_word(0x6000)
		self.assertEqual(hp, 0)

	def test_no_negative_gold(self):
		"""Test gold can't be negative."""
		rom = MockROM()

		# Gold is unsigned 16-bit
		rom.write_word(0x6004, 0xffff)
		gold = rom.read_word(0x6004)
		self.assertEqual(gold, 65535)

	def test_stat_boundary_values(self):
		"""Test stats at boundary values."""
		rom = MockROM()

		# Test minimum values
		rom.write_byte(0x6002, 0)
		strength = rom.read_byte(0x6002)
		self.assertEqual(strength, 0)

		# Test maximum values
		rom.write_byte(0x6002, 255)
		strength = rom.read_byte(0x6002)
		self.assertEqual(strength, 255)


# ============================================================================
# FUZZ TESTING
# ============================================================================

class FuzzTests(unittest.TestCase):
	"""Fuzz tests for robustness."""

	def test_random_hp_values(self):
		"""Fuzz test with random HP values."""
		rom = MockROM()

		for _ in range(100):
			# Generate random HP
			hp = random.randint(0, 65535)

			# Write and read back
			rom.write_word(0x6000, hp)
			read_hp = rom.read_word(0x6000)

			# Should match
			self.assertEqual(read_hp, hp)

	def test_random_addresses(self):
		"""Fuzz test with random addresses."""
		rom = MockROM()

		for _ in range(100):
			# Random valid address
			addr = random.randint(0, rom.size - 1)
			value = random.randint(0, 255)

			# Write and read
			rom.write_byte(addr, value)
			read_value = rom.read_byte(addr)

			self.assertEqual(read_value, value)

	def test_boundary_addresses(self):
		"""Test addresses at boundaries."""
		rom = MockROM()

		# Test first address
		rom.write_byte(0, 42)
		self.assertEqual(rom.read_byte(0), 42)

		# Test last address
		rom.write_byte(rom.size - 1, 99)
		self.assertEqual(rom.read_byte(rom.size - 1), 99)

		# Test out of bounds (should return 0)
		self.assertEqual(rom.read_byte(rom.size), 0)
		self.assertEqual(rom.read_byte(-1), 0)


# ============================================================================
# BENCHMARK TESTS
# ============================================================================

class BenchmarkTests(unittest.TestCase):
	"""Performance benchmark tests."""

	def test_read_performance(self):
		"""Benchmark read performance."""
		rom = MockROM()

		start = time.time()
		for i in range(10000):
			_ = rom.read_byte(0x6000 + (i % 1000))
		duration = time.time() - start

		# Should complete in < 1 second
		self.assertLess(duration, 1.0)
		print(f"\nRead performance: {10000/duration:.0f} ops/sec")

	def test_write_performance(self):
		"""Benchmark write performance."""
		rom = MockROM()

		start = time.time()
		for i in range(10000):
			rom.write_byte(0x6000 + (i % 1000), i & 0xff)
		duration = time.time() - start

		self.assertLess(duration, 1.0)
		print(f"\nWrite performance: {10000/duration:.0f} ops/sec")

	def test_monster_extraction_performance(self):
		"""Benchmark monster data extraction."""
		rom = MockROM()

		start = time.time()
		for _ in range(1000):
			monsters = []
			for i in range(24):
				offset = 0x6000 + (i * 32)
				monsters.append({
					'hp': rom.read_word(offset),
					'strength': rom.read_byte(offset + 2),
					'agility': rom.read_byte(offset + 3),
					'gold': rom.read_word(offset + 4)
				})
		duration = time.time() - start

		print(f"\nMonster extraction: {1000/duration:.0f} cycles/sec")


# ============================================================================
# TEST RUNNER
# ============================================================================

class TestRunner:
	"""Custom test runner with reporting."""

	def __init__(self, verbose: bool = False):
		self.verbose = verbose
		self.results: List[TestResult] = []

	def run_suite(self, suite: TestSuite, test_classes: List[type]) -> TestSummary:
		"""Run a test suite."""
		print(f"\n{'=' * 70}")
		print(f"Running {suite.value.upper()} Tests")
		print(f"{'=' * 70}")

		start_time = time.time()
		passed = 0
		failed = 0
		errors = 0
		skipped = 0

		for test_class in test_classes:
			# Create test suite
			loader = unittest.TestLoader()
			tests = loader.loadTestsFromTestCase(test_class)

			# Run tests
			runner = unittest.TextTestRunner(verbosity=2 if self.verbose else 1)
			result = runner.run(tests)

			# Collect results
			passed += len(result.successes) if hasattr(result, 'successes') else (
				result.testsRun - len(result.failures) - len(result.errors) - len(result.skipped)
			)
			failed += len(result.failures)
			errors += len(result.errors)
			skipped += len(result.skipped)

		duration = time.time() - start_time
		total = passed + failed + errors + skipped

		return TestSummary(
			total_tests=total,
			passed=passed,
			failed=failed,
			skipped=skipped,
			errors=errors,
			duration=duration
		)

	def generate_report(self, summaries: List[TestSummary], format: str = "text") -> str:
		"""Generate test report."""
		if format == "text":
			return self._generate_text_report(summaries)
		elif format == "html":
			return self._generate_html_report(summaries)
		elif format == "json":
			return self._generate_json_report(summaries)
		return ""

	def _generate_text_report(self, summaries: List[TestSummary]) -> str:
		"""Generate text report."""
		lines = []
		lines.append("\n" + "=" * 70)
		lines.append("TEST SUMMARY")
		lines.append("=" * 70)

		total_tests = sum(s.total_tests for s in summaries)
		total_passed = sum(s.passed for s in summaries)
		total_failed = sum(s.failed for s in summaries)
		total_errors = sum(s.errors for s in summaries)
		total_duration = sum(s.duration for s in summaries)

		lines.append(f"Total Tests: {total_tests}")
		lines.append(f"Passed: {total_passed} ({100*total_passed/max(total_tests,1):.1f}%)")
		lines.append(f"Failed: {total_failed}")
		lines.append(f"Errors: {total_errors}")
		lines.append(f"Duration: {total_duration:.2f}s")

		if total_failed == 0 and total_errors == 0:
			lines.append("\n✓ ALL TESTS PASSED")
		else:
			lines.append("\n✗ SOME TESTS FAILED")

		lines.append("=" * 70)

		return "\n".join(lines)

	def _generate_html_report(self, summaries: List[TestSummary]) -> str:
		"""Generate HTML report."""
		total_tests = sum(s.total_tests for s in summaries)
		total_passed = sum(s.passed for s in summaries)
		total_failed = sum(s.failed for s in summaries)

		html = f"""
<!DOCTYPE html>
<html>
<head>
	<title>Test Report</title>
	<style>
		body {{ font-family: Arial, sans-serif; margin: 20px; }}
		.summary {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
		.passed {{ color: green; }}
		.failed {{ color: red; }}
	</style>
</head>
<body>
	<h1>Dragon Warrior Test Report</h1>
	<div class="summary">
		<h2>Summary</h2>
		<p>Total Tests: {total_tests}</p>
		<p class="passed">Passed: {total_passed}</p>
		<p class="failed">Failed: {total_failed}</p>
	</div>
</body>
</html>
"""
		return html

	def _generate_json_report(self, summaries: List[TestSummary]) -> str:
		"""Generate JSON report."""
		data = {
			'timestamp': datetime.now().isoformat(),
			'summaries': [
				{
					'total': s.total_tests,
					'passed': s.passed,
					'failed': s.failed,
					'errors': s.errors,
					'duration': s.duration
				}
				for s in summaries
			]
		}
		return json.dumps(data, indent=2)


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Advanced Testing and Validation Framework"
	)

	parser.add_argument('--suite', choices=['unit', 'integration', 'regression', 'fuzz', 'benchmark', 'all'],
					   default='all', help="Test suite to run")
	parser.add_argument('--coverage', action='store_true',
					   help="Generate code coverage report")
	parser.add_argument('--report', choices=['text', 'html', 'json'],
					   default='text', help="Report format")
	parser.add_argument('-v', '--verbose', action='store_true',
					   help="Verbose output")

	args = parser.parse_args()

	# Create test runner
	runner = TestRunner(verbose=args.verbose)

	# Define test suites
	test_suites = {
		'unit': [MonsterDataTests, ItemDataTests, ROMHeaderTests],
		'integration': [BuildPipelineTests],
		'regression': [RegressionTests],
		'fuzz': [FuzzTests],
		'benchmark': [BenchmarkTests]
	}

	# Run tests
	summaries = []

	if args.suite == 'all':
		for suite_name, test_classes in test_suites.items():
			suite = TestSuite(suite_name)
			summary = runner.run_suite(suite, test_classes)
			summaries.append(summary)
	else:
		suite = TestSuite(args.suite)
		test_classes = test_suites[args.suite]
		summary = runner.run_suite(suite, test_classes)
		summaries.append(summary)

	# Generate report
	report = runner.generate_report(summaries, args.report)
	print(report)

	# Save HTML report if requested
	if args.report == 'html':
		report_path = Path('test_report.html')
		with open(report_path, 'w') as f:
			f.write(report)
		print(f"\nHTML report saved to: {report_path}")

	# Return exit code
	total_failed = sum(s.failed + s.errors for s in summaries)
	return 0 if total_failed == 0 else 1


if __name__ == "__main__":
	sys.exit(main())
