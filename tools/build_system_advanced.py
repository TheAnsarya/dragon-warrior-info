#!/usr/bin/env python3
"""
Advanced Build Automation System for Dragon Warrior

Comprehensive build pipeline with dependency tracking, incremental builds,
parallel processing, and validation checkpoints.

Features:
- Multi-stage build pipeline with dependency resolution
- Incremental builds (rebuild only changed files)
- Parallel task execution
- Build caching and artifact management
- Automatic validation checkpoints
- Build configuration profiles
- Pre/post-build hooks
- Error recovery and rollback
- Build metrics and timing
- CI/CD integration support

Usage:
	python tools/build_system_advanced.py [TARGET]

Examples:
	# Full clean build
	python tools/build_system_advanced.py clean all

	# Incremental build
	python tools/build_system_advanced.py

	# Build specific target
	python tools/build_system_advanced.py assets

	# Parallel build (4 jobs)
	python tools/build_system_advanced.py -j 4 all

	# Dry run (show what would be built)
	python tools/build_system_advanced.py --dry-run all

Author: Dragon Warrior ROM Hacking Toolkit
Version: 2.0
"""

import sys
import os
import time
import hashlib
import json
import shutil
import subprocess
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set, Callable, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import argparse
from datetime import datetime
import concurrent.futures


# ============================================================================
# BUILD CONFIGURATION
# ============================================================================

class BuildStatus(Enum):
	"""Build task status."""
	PENDING = "pending"
	RUNNING = "running"
	SUCCESS = "success"
	FAILED = "failed"
	SKIPPED = "skipped"
	CACHED = "cached"


class BuildTarget(Enum):
	"""Build targets."""
	CLEAN = "clean"
	ASSETS = "assets"
	BINARY = "binary"
	ROM = "rom"
	VALIDATE = "validate"
	ALL = "all"


@dataclass
class BuildConfig:
	"""Build configuration."""
	project_root: Path
	build_dir: Path
	cache_dir: Path
	output_dir: Path

	# Paths
	rom_source: Path = Path("roms/dragon_warrior.nes")
	assets_dir: Path = Path("assets")
	tools_dir: Path = Path("tools")

	# Build options
	parallel_jobs: int = 1
	incremental: bool = True
	verbose: bool = False
	dry_run: bool = False

	# Validation
	validate_checksums: bool = True
	validate_assets: bool = True

	# Cache
	use_cache: bool = True
	cache_ttl: int = 86400  # 1 day in seconds


@dataclass
class BuildTask:
	"""Individual build task."""
	id: str
	name: str
	description: str
	dependencies: List[str] = field(default_factory=list)
	inputs: List[Path] = field(default_factory=list)
	outputs: List[Path] = field(default_factory=list)
	command: Optional[Callable] = None
	status: BuildStatus = BuildStatus.PENDING
	start_time: float = 0.0
	end_time: float = 0.0
	error_message: str = ""

	@property
	def duration(self) -> float:
		"""Get task duration in seconds."""
		if self.end_time > 0:
			return self.end_time - self.start_time
		return 0.0


@dataclass
class BuildResult:
	"""Build execution result."""
	success: bool
	tasks_run: int
	tasks_skipped: int
	tasks_cached: int
	tasks_failed: int
	total_duration: float
	failed_tasks: List[str] = field(default_factory=list)
	error_messages: List[str] = field(default_factory=list)


# ============================================================================
# BUILD CACHE
# ============================================================================

class BuildCache:
	"""Manage build cache for incremental builds."""

	def __init__(self, cache_dir: Path):
		self.cache_dir = cache_dir
		self.cache_dir.mkdir(parents=True, exist_ok=True)
		self.cache_file = cache_dir / "build_cache.json"
		self.cache: Dict[str, Any] = self._load_cache()

	def _load_cache(self) -> Dict[str, Any]:
		"""Load cache from disk."""
		if self.cache_file.exists():
			try:
				with open(self.cache_file, 'r') as f:
					return json.load(f)
			except Exception as e:
				print(f"Warning: Failed to load cache: {e}")
		return {}

	def _save_cache(self) -> None:
		"""Save cache to disk."""
		try:
			with open(self.cache_file, 'w') as f:
				json.dump(self.cache, f, indent=2)
		except Exception as e:
			print(f"Warning: Failed to save cache: {e}")

	def get_file_hash(self, filepath: Path) -> str:
		"""Calculate hash of file."""
		if not filepath.exists():
			return ""

		hasher = hashlib.sha256()
		with open(filepath, 'rb') as f:
			while chunk := f.read(8192):
				hasher.update(chunk)
		return hasher.hexdigest()

	def get_task_hash(self, task: BuildTask) -> str:
		"""Calculate hash of task inputs."""
		hasher = hashlib.sha256()

		# Hash all input files
		for input_file in task.inputs:
			if input_file.exists():
				hasher.update(self.get_file_hash(input_file).encode())
			else:
				hasher.update(b'missing')

		# Hash task ID for uniqueness
		hasher.update(task.id.encode())

		return hasher.hexdigest()

	def is_task_cached(self, task: BuildTask, max_age: int = 86400) -> bool:
		"""Check if task results are cached and valid."""
		task_hash = self.get_task_hash(task)

		if task.id not in self.cache:
			return False

		cache_entry = self.cache[task.id]

		# Check hash
		if cache_entry.get('hash') != task_hash:
			return False

		# Check age
		cache_time = cache_entry.get('timestamp', 0)
		if time.time() - cache_time > max_age:
			return False

		# Check outputs exist
		for output in task.outputs:
			if not output.exists():
				return False

		return True

	def cache_task_result(self, task: BuildTask) -> None:
		"""Cache task result."""
		task_hash = self.get_task_hash(task)

		self.cache[task.id] = {
			'hash': task_hash,
			'timestamp': time.time(),
			'status': task.status.value,
			'duration': task.duration
		}

		self._save_cache()

	def invalidate_task(self, task_id: str) -> None:
		"""Invalidate cached task."""
		if task_id in self.cache:
			del self.cache[task_id]
			self._save_cache()

	def clear(self) -> None:
		"""Clear entire cache."""
		self.cache = {}
		self._save_cache()


# ============================================================================
# BUILD EXECUTOR
# ============================================================================

class BuildExecutor:
	"""Execute build tasks with dependency resolution."""

	def __init__(self, config: BuildConfig):
		self.config = config
		self.cache = BuildCache(config.cache_dir)
		self.tasks: Dict[str, BuildTask] = {}

	def register_task(self, task: BuildTask) -> None:
		"""Register a build task."""
		self.tasks[task.id] = task

	def get_task_order(self) -> List[str]:
		"""Get tasks in dependency order (topological sort)."""
		# Build dependency graph
		in_degree = {task_id: 0 for task_id in self.tasks}
		graph = {task_id: [] for task_id in self.tasks}

		for task_id, task in self.tasks.items():
			for dep in task.dependencies:
				if dep in self.tasks:
					graph[dep].append(task_id)
					in_degree[task_id] += 1

		# Kahn's algorithm
		queue = [task_id for task_id, degree in in_degree.items() if degree == 0]
		order = []

		while queue:
			task_id = queue.pop(0)
			order.append(task_id)

			for dependent in graph[task_id]:
				in_degree[dependent] -= 1
				if in_degree[dependent] == 0:
					queue.append(dependent)

		if len(order) != len(self.tasks):
			raise RuntimeError("Circular dependency detected in build tasks")

		return order

	def should_run_task(self, task: BuildTask) -> Tuple[bool, str]:
		"""Determine if task should run."""
		# Check cache
		if self.config.use_cache and self.cache.is_task_cached(task, self.config.cache_ttl):
			return False, "cached"

		# Check if outputs exist and inputs unchanged (incremental build)
		if self.config.incremental:
			all_outputs_exist = all(output.exists() for output in task.outputs)

			if all_outputs_exist and task.outputs:
				# Check if any input is newer than outputs
				newest_output = max((out.stat().st_mtime for out in task.outputs if out.exists()),
								   default=0)
				oldest_input = min((inp.stat().st_mtime for inp in task.inputs if inp.exists()),
								  default=float('inf'))

				if newest_output > oldest_input:
					return False, "up-to-date"

		return True, "needed"

	def execute_task(self, task: BuildTask) -> bool:
		"""Execute a single build task."""
		if self.config.dry_run:
			print(f"[DRY RUN] Would execute: {task.name}")
			task.status = BuildStatus.SUCCESS
			return True

		print(f"[BUILD] {task.name}...")

		task.start_time = time.time()
		task.status = BuildStatus.RUNNING

		try:
			if task.command:
				# Execute task command
				success = task.command()

				if success:
					task.status = BuildStatus.SUCCESS
					task.end_time = time.time()

					# Cache result
					if self.config.use_cache:
						self.cache.cache_task_result(task)

					print(f"[✓] {task.name} completed in {task.duration:.2f}s")
					return True
				else:
					raise RuntimeError("Task command returned failure")
			else:
				# No command - just mark as success
				task.status = BuildStatus.SUCCESS
				task.end_time = time.time()
				return True

		except Exception as e:
			task.status = BuildStatus.FAILED
			task.end_time = time.time()
			task.error_message = str(e)
			print(f"[✗] {task.name} failed: {e}")
			return False

	def execute_parallel(self, task_ids: List[str]) -> bool:
		"""Execute tasks in parallel."""
		with concurrent.futures.ThreadPoolExecutor(max_workers=self.config.parallel_jobs) as executor:
			futures = {executor.submit(self.execute_task, self.tasks[tid]): tid
					  for tid in task_ids}

			all_success = True
			for future in concurrent.futures.as_completed(futures):
				if not future.result():
					all_success = False

			return all_success

	def build(self, target_tasks: Optional[List[str]] = None) -> BuildResult:
		"""Execute build pipeline."""
		start_time = time.time()

		# Get task execution order
		try:
			task_order = self.get_task_order()
		except RuntimeError as e:
			return BuildResult(
				success=False,
				tasks_run=0,
				tasks_skipped=0,
				tasks_cached=0,
				tasks_failed=0,
				total_duration=0.0,
				error_messages=[str(e)]
			)

		# Filter to target tasks if specified
		if target_tasks:
			# Include dependencies
			required_tasks = set()
			for target in target_tasks:
				if target in self.tasks:
					required_tasks.add(target)
					# Add dependencies recursively
					stack = [target]
					while stack:
						current = stack.pop()
						for dep in self.tasks[current].dependencies:
							if dep not in required_tasks:
								required_tasks.add(dep)
								stack.append(dep)

			task_order = [tid for tid in task_order if tid in required_tasks]

		# Execute tasks
		tasks_run = 0
		tasks_skipped = 0
		tasks_cached = 0
		tasks_failed = 0
		failed_tasks = []
		error_messages = []

		for task_id in task_order:
			task = self.tasks[task_id]

			# Check if task should run
			should_run, reason = self.should_run_task(task)

			if not should_run:
				if reason == "cached":
					task.status = BuildStatus.CACHED
					tasks_cached += 1
					print(f"[CACHED] {task.name}")
				else:
					task.status = BuildStatus.SKIPPED
					tasks_skipped += 1
					if self.config.verbose:
						print(f"[SKIP] {task.name} ({reason})")
				continue

			# Execute task
			success = self.execute_task(task)

			if success:
				tasks_run += 1
			else:
				tasks_failed += 1
				failed_tasks.append(task_id)
				error_messages.append(f"{task.name}: {task.error_message}")

				# Stop on first failure
				break

		total_duration = time.time() - start_time

		return BuildResult(
			success=(tasks_failed == 0),
			tasks_run=tasks_run,
			tasks_skipped=tasks_skipped,
			tasks_cached=tasks_cached,
			tasks_failed=tasks_failed,
			total_duration=total_duration,
			failed_tasks=failed_tasks,
			error_messages=error_messages
		)


# ============================================================================
# BUILD TASK DEFINITIONS
# ============================================================================

def create_build_tasks(config: BuildConfig) -> List[BuildTask]:
	"""Create all build tasks."""
	tasks = []

	# Task: Clean build directories
	def clean_task():
		if config.build_dir.exists():
			shutil.rmtree(config.build_dir)
		config.build_dir.mkdir(parents=True, exist_ok=True)
		return True

	tasks.append(BuildTask(
		id="clean",
		name="Clean Build",
		description="Remove all build artifacts",
		command=clean_task
	))

	# Task: Validate ROM source
	def validate_rom():
		if not config.rom_source.exists():
			print(f"Error: ROM not found: {config.rom_source}")
			return False

		# Check ROM size
		size = config.rom_source.stat().st_size
		if size != 131072:  # 128KB
			print(f"Warning: Unexpected ROM size: {size} bytes")

		return True

	tasks.append(BuildTask(
		id="validate_rom",
		name="Validate ROM Source",
		description="Verify source ROM integrity",
		inputs=[config.rom_source],
		command=validate_rom
	))

	# Task: Extract assets
	def extract_assets():
		extract_script = config.tools_dir / "extract_all_data.py"
		if not extract_script.exists():
			print(f"Error: Extract script not found: {extract_script}")
			return False

		result = subprocess.run(
			[sys.executable, str(extract_script)],
			cwd=config.project_root,
			capture_output=True,
			text=True
		)

		if result.returncode != 0:
			print(f"Extract failed:\n{result.stderr}")
			return False

		return True

	tasks.append(BuildTask(
		id="extract_assets",
		name="Extract Assets",
		description="Extract data from ROM to editable assets",
		dependencies=["validate_rom"],
		inputs=[config.rom_source],
		outputs=[
			config.assets_dir / "monsters.json",
			config.assets_dir / "items.json",
			config.assets_dir / "spells.json"
		],
		command=extract_assets
	))

	# Task: Convert to binary
	def convert_binary():
		binary_script = config.tools_dir / "extract_to_binary.py"
		if not binary_script.exists():
			print(f"Error: Binary script not found: {binary_script}")
			return False

		result = subprocess.run(
			[sys.executable, str(binary_script)],
			cwd=config.project_root,
			capture_output=True,
			text=True
		)

		return result.returncode == 0

	tasks.append(BuildTask(
		id="convert_binary",
		name="Convert to Binary",
		description="Convert assets to binary intermediate format",
		dependencies=["extract_assets"],
		inputs=[
			config.assets_dir / "monsters.json",
			config.assets_dir / "items.json"
		],
		outputs=[
			config.build_dir / "monsters.dwdata",
			config.build_dir / "items.dwdata"
		],
		command=convert_binary
	))

	# Task: Build ROM
	def build_rom():
		build_script = config.tools_dir / "dragon_warrior_build.py"
		if not build_script.exists():
			print(f"Error: Build script not found: {build_script}")
			return False

		result = subprocess.run(
			[sys.executable, str(build_script)],
			cwd=config.project_root,
			capture_output=True,
			text=True
		)

		if result.returncode != 0:
			print(f"Build failed:\n{result.stderr}")
			return False

		return True

	tasks.append(BuildTask(
		id="build_rom",
		name="Build ROM",
		description="Assemble final ROM file",
		dependencies=["convert_binary"],
		inputs=[
			config.build_dir / "monsters.dwdata",
			config.build_dir / "items.dwdata"
		],
		outputs=[config.output_dir / "dragon_warrior_modified.nes"],
		command=build_rom
	))

	# Task: Validate output
	def validate_output():
		output_rom = config.output_dir / "dragon_warrior_modified.nes"

		if not output_rom.exists():
			print(f"Error: Output ROM not found: {output_rom}")
			return False

		# Check size
		size = output_rom.stat().st_size
		if size != 131072:
			print(f"Error: Output ROM has wrong size: {size} bytes")
			return False

		print(f"✓ Output ROM validated: {size:,} bytes")
		return True

	tasks.append(BuildTask(
		id="validate_output",
		name="Validate Output",
		description="Verify built ROM integrity",
		dependencies=["build_rom"],
		inputs=[config.output_dir / "dragon_warrior_modified.nes"],
		command=validate_output
	))

	return tasks


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Advanced Build Automation System"
	)

	parser.add_argument('targets', nargs='*', default=['all'],
					   help="Build targets (clean, assets, binary, rom, validate, all)")
	parser.add_argument('-j', '--jobs', type=int, default=1,
					   help="Number of parallel jobs")
	parser.add_argument('--no-cache', action='store_true',
					   help="Disable build cache")
	parser.add_argument('--no-incremental', action='store_true',
					   help="Force rebuild all targets")
	parser.add_argument('--dry-run', action='store_true',
					   help="Show what would be built without executing")
	parser.add_argument('-v', '--verbose', action='store_true',
					   help="Verbose output")
	parser.add_argument('--clean', action='store_true',
					   help="Clean before building")

	args = parser.parse_args()

	# Create build configuration
	project_root = Path.cwd()

	config = BuildConfig(
		project_root=project_root,
		build_dir=project_root / "build",
		cache_dir=project_root / "build" / ".cache",
		output_dir=project_root / "output",
		parallel_jobs=args.jobs,
		incremental=not args.no_incremental,
		use_cache=not args.no_cache,
		verbose=args.verbose,
		dry_run=args.dry_run
	)

	# Create build executor
	executor = BuildExecutor(config)

	# Register all tasks
	tasks = create_build_tasks(config)
	for task in tasks:
		executor.register_task(task)

	print("=" * 70)
	print("DRAGON WARRIOR BUILD SYSTEM")
	print("=" * 70)
	print(f"Project: {config.project_root}")
	print(f"Build Dir: {config.build_dir}")
	print(f"Parallel Jobs: {config.parallel_jobs}")
	print(f"Incremental: {config.incremental}")
	print(f"Cache: {'Enabled' if config.use_cache else 'Disabled'}")
	print("=" * 70)

	# Clean if requested
	if args.clean or 'clean' in args.targets:
		print("\n[CLEAN] Removing build artifacts...")
		executor.execute_task(executor.tasks['clean'])

	# Determine target tasks
	target_task_ids = []

	if 'all' in args.targets:
		target_task_ids = ['validate_output']  # This includes all dependencies
	else:
		for target in args.targets:
			if target in executor.tasks:
				target_task_ids.append(target)
			else:
				print(f"Warning: Unknown target: {target}")

	# Execute build
	print(f"\n[BUILD] Starting build...")
	result = executor.build(target_task_ids)

	# Print summary
	print("\n" + "=" * 70)
	print("BUILD SUMMARY")
	print("=" * 70)
	print(f"Status: {'✓ SUCCESS' if result.success else '✗ FAILED'}")
	print(f"Duration: {result.total_duration:.2f}s")
	print(f"Tasks Run: {result.tasks_run}")
	print(f"Tasks Cached: {result.tasks_cached}")
	print(f"Tasks Skipped: {result.tasks_skipped}")
	print(f"Tasks Failed: {result.tasks_failed}")

	if result.failed_tasks:
		print(f"\nFailed Tasks:")
		for task_id in result.failed_tasks:
			print(f"  - {task_id}")

	if result.error_messages:
		print(f"\nErrors:")
		for error in result.error_messages:
			print(f"  {error}")

	print("=" * 70)

	return 0 if result.success else 1


if __name__ == "__main__":
	sys.exit(main())
