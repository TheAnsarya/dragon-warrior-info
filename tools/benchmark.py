#!/usr/bin/env python3
"""
Performance Benchmark Tool

Benchmark Dragon Warrior toolkit operations.

Features:
- Measure extraction/insertion speed
- Compare binary vs direct workflows
- Memory usage profiling
- Generate performance reports

Usage:
	python tools/benchmark.py
	python tools/benchmark.py --profile memory
	python tools/benchmark.py --iterations 100

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import time
import tempfile
import shutil
import psutil
import argparse
from pathlib import Path
from typing import Dict, List, Callable
from dataclasses import dataclass

# Default paths
DEFAULT_ROM = "roms/dragon_warrior.nes"
DEFAULT_ITERATIONS = 10


@dataclass
class BenchmarkResult:
	"""Store benchmark results"""
	name: str
	duration: float
	iterations: int
	memory_peak: float
	memory_avg: float

	@property
	def avg_duration(self) -> float:
		"""Average duration per iteration"""
		return self.duration / self.iterations if self.iterations > 0 else 0

	def __str__(self) -> str:
		return (
			f"{self.name}:\n"
			f"  Total: {self.duration:.3f}s\n"
			f"  Avg: {self.avg_duration:.3f}s\n"
			f"  Iterations: {self.iterations}\n"
			f"  Memory Peak: {self.memory_peak:.2f} MB\n"
			f"  Memory Avg: {self.memory_avg:.2f} MB"
		)


class ToolkitBenchmark:
	"""Benchmark toolkit operations"""

	def __init__(self, rom_path: str, iterations: int = 10):
		"""
		Initialize benchmark

		Args:
			rom_path: ROM file path
			iterations: Number of iterations
		"""
		self.rom_path = Path(rom_path)
		self.iterations = iterations
		self.results: List[BenchmarkResult] = []
		self.temp_dir = None

	def setup(self):
		"""Set up temporary workspace"""
		self.temp_dir = Path(tempfile.mkdtemp())
		print(f"Using temp workspace: {self.temp_dir}")

	def teardown(self):
		"""Clean up temporary workspace"""
		if self.temp_dir and self.temp_dir.exists():
			shutil.rmtree(self.temp_dir)

	def measure_time(self, func: Callable, name: str, iterations: int = None) -> BenchmarkResult:
		"""
		Measure execution time and memory

		Args:
			func: Function to benchmark
			name: Benchmark name
			iterations: Override default iterations

		Returns:
			Benchmark result
		"""
		if iterations is None:
			iterations = self.iterations

		print(f"\nBenchmarking: {name} ({iterations} iterations)")

		# Get process
		process = psutil.Process()

		# Memory tracking
		memory_samples = []

		# Warmup
		func()

		# Benchmark
		start_time = time.time()

		for i in range(iterations):
			# Sample memory before
			mem_before = process.memory_info().rss / 1024 / 1024  # MB

			# Run function
			func()

			# Sample memory after
			mem_after = process.memory_info().rss / 1024 / 1024  # MB
			memory_samples.append(mem_after)

			# Progress
			if (i + 1) % max(1, iterations // 10) == 0:
				print(f"  Progress: {i + 1}/{iterations}")

		end_time = time.time()
		duration = end_time - start_time

		# Calculate memory stats
		memory_peak = max(memory_samples)
		memory_avg = sum(memory_samples) / len(memory_samples)

		result = BenchmarkResult(
			name=name,
			duration=duration,
			iterations=iterations,
			memory_peak=memory_peak,
			memory_avg=memory_avg
		)

		self.results.append(result)
		print(f"  Completed in {duration:.3f}s (avg: {result.avg_duration:.3f}s)")

		return result

	def benchmark_rom_loading(self):
		"""Benchmark ROM loading"""
		def load_rom():
			with open(self.rom_path, 'rb') as f:
				data = f.read()
			return len(data)

		self.measure_time(load_rom, "ROM Loading")

	def benchmark_data_extraction(self):
		"""Benchmark full data extraction"""
		def extract_data():
			# Would call extract_all_data.py functions
			# Simplified for benchmark
			with open(self.rom_path, 'rb') as f:
				data = bytearray(f.read())

			# Simulate monster extraction (624 bytes)
			monsters_data = data[0x5c10:0x5c10+624]

			# Simulate spell extraction (40 bytes)
			spells_data = data[0x1d410:0x1d410+40]

			# Simulate item extraction (256 bytes)
			items_data = data[0x1cf70:0x1cf70+256]

			return len(monsters_data) + len(spells_data) + len(items_data)

		self.measure_time(extract_data, "Data Extraction")

	def benchmark_binary_creation(self):
		"""Benchmark .dwdata binary creation"""
		import struct
		import zlib

		def create_binary():
			# Simulate monster binary creation
			data = bytes([0xff] * 624)
			crc = zlib.crc32(data)

			header = struct.pack(
				'<4sBBHIIHHQ',
				b'DWDT',  # Magic
				1, 0,     # Version
				0,        # Reserved
				0x01,     # Data type
				crc,      # CRC32
				0x5c10,   # ROM offset
				624,      # Data size
				0,        # Reserved
				int(time.time())  # Timestamp
			)

			binary = header + data

			# Write to temp file
			output = self.temp_dir / "test.dwdata"
			with open(output, 'wb') as f:
				f.write(binary)

			return len(binary)

		self.measure_time(create_binary, "Binary Creation (.dwdata)")

	def benchmark_json_parsing(self):
		"""Benchmark JSON parsing"""
		import json

		def parse_json():
			# Create sample monster JSON
			monsters = []
			for i in range(39):
				monsters.append({
					"id": i,
					"name": f"Monster {i}",
					"hp": 10 + i,
					"attack": 5 + i,
					"defense": 3 + i,
					"agility": 4 + i,
					"spell": 0,
					"m_defense": 2,
					"xp": 8 + i * 2,
					"gold": 6 + i
				})

			# Write JSON
			json_file = self.temp_dir / "monsters.json"
			with open(json_file, 'w') as f:
				json.dump(monsters, f, indent=2)

			# Read JSON
			with open(json_file, 'r') as f:
				loaded = json.load(f)

			return len(loaded)

		self.measure_time(parse_json, "JSON Parsing")

	def benchmark_image_processing(self):
		"""Benchmark image processing"""
		try:
			from PIL import Image
		except ImportError:
			print("  Skipping (PIL not available)")
			return

		def process_image():
			# Create 256×256 test image
			img = Image.new('RGB', (256, 256), (0, 0, 0))

			# Draw some tiles
			from PIL import ImageDraw
			draw = ImageDraw.Draw(img)

			for y in range(0, 256, 8):
				for x in range(0, 256, 8):
					# Draw tile border
					draw.rectangle([x, y, x+7, y+7], outline=(255, 255, 255))

			# Save
			output = self.temp_dir / "chr_tiles.png"
			img.save(output)

			# Load
			loaded = Image.open(output)
			return loaded.size[0] * loaded.size[1]

		self.measure_time(process_image, "Image Processing (CHR tiles)")

	def benchmark_crc_calculation(self):
		"""Benchmark CRC32 calculation"""
		import zlib

		def calculate_crc():
			# Various data sizes
			data_sizes = [624, 40, 256, 8192]  # monsters, spells, items, graphics

			crcs = []
			for size in data_sizes:
				data = bytes([0xff] * size)
				crc = zlib.crc32(data)
				crcs.append(crc)

			return len(crcs)

		self.measure_time(calculate_crc, "CRC32 Calculation")

	def benchmark_validation(self):
		"""Benchmark data validation"""
		def validate_data():
			# Simulate monster validation
			monsters = []
			for i in range(39):
				monster = {
					"hp": 10 + i,
					"attack": 5 + i,
					"defense": 3 + i,
					"agility": 4 + i,
					"spell": 0,
					"m_defense": 2,
					"xp": 8 + i * 2,
					"gold": 6 + i
				}

				# Validate ranges
				valid = (
					1 <= monster["hp"] <= 255 and
					0 <= monster["attack"] <= 255 and
					0 <= monster["defense"] <= 255 and
					0 <= monster["agility"] <= 255 and
					0 <= monster["spell"] <= 9 and
					0 <= monster["xp"] <= 65535 and
					0 <= monster["gold"] <= 65535
				)

				if valid:
					monsters.append(monster)

			return len(monsters)

		self.measure_time(validate_data, "Data Validation")

	def generate_report(self):
		"""Generate performance report"""
		print("\n" + "=" * 70)
		print("Performance Benchmark Report")
		print("=" * 70)

		print(f"\nROM: {self.rom_path.name}")
		print(f"Iterations: {self.iterations}")

		print("\n--- Results ---\n")
		for result in self.results:
			print(result)
			print()

		print("--- Summary ---")
		total_time = sum(r.duration for r in self.results)
		print(f"Total benchmark time: {total_time:.3f}s")

		# Find fastest/slowest
		if self.results:
			fastest = min(self.results, key=lambda r: r.avg_duration)
			slowest = max(self.results, key=lambda r: r.avg_duration)

			print(f"\nFastest: {fastest.name} ({fastest.avg_duration:.3f}s)")
			print(f"Slowest: {slowest.name} ({slowest.avg_duration:.3f}s)")
			print(f"Ratio: {slowest.avg_duration / fastest.avg_duration:.2f}x")

		print("\n" + "=" * 70)

	def run_all_benchmarks(self):
		"""Run all benchmarks"""
		self.setup()

		try:
			print("=" * 70)
			print("Dragon Warrior Toolkit Performance Benchmark")
			print("=" * 70)

			self.benchmark_rom_loading()
			self.benchmark_data_extraction()
			self.benchmark_binary_creation()
			self.benchmark_json_parsing()
			self.benchmark_image_processing()
			self.benchmark_crc_calculation()
			self.benchmark_validation()

			self.generate_report()

		finally:
			self.teardown()


def main():
	"""Main entry point"""
	parser = argparse.ArgumentParser(
		description='Benchmark Dragon Warrior toolkit performance',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  # Run all benchmarks
  python tools/benchmark.py

  # Custom iteration count
  python tools/benchmark.py --iterations 100

  # Quick test (fewer iterations)
  python tools/benchmark.py --iterations 3
		"""
	)

	parser.add_argument(
		'--rom',
		default=DEFAULT_ROM,
		help=f'ROM file path (default: {DEFAULT_ROM})'
	)

	parser.add_argument(
		'--iterations',
		type=int,
		default=DEFAULT_ITERATIONS,
		help=f'Number of iterations (default: {DEFAULT_ITERATIONS})'
	)

	args = parser.parse_args()

	# Check ROM exists
	if not Path(args.rom).exists():
		print(f"ERROR: ROM not found: {args.rom}")
		return 1

	# Run benchmarks
	benchmark = ToolkitBenchmark(args.rom, args.iterations)
	benchmark.run_all_benchmarks()

	return 0


if __name__ == '__main__':
	sys.exit(main())
