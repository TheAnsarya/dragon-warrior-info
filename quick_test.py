#!/usr/bin/env python3
"""
Quick Test Runner for Dragon Warrior ROM Toolkit

Simplified test execution with color output and progress indicators.
Automatically finds ROM and runs all tests with smart defaults.
"""

import sys
import os
import unittest
from pathlib import Path
import time
from typing import List, Tuple


# ANSI color codes
class Colors:
	"""Terminal colors for output."""
	HEADER = '\033[95m'
	OKBLUE = '\033[94m'
	OKCYAN = '\033[96m'
	OKGREEN = '\033[92m'
	WARNING = '\033[93m'
	FAIL = '\033[91m'
	ENDC = '\033[0m'
	BOLD = '\033[1m'
	UNDERLINE = '\033[4m'


def print_header(text: str):
	"""Print colored header."""
	print(f"\n{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}")
	print(f"{Colors.HEADER}{Colors.BOLD}{text.center(80)}{Colors.ENDC}")
	print(f"{Colors.HEADER}{Colors.BOLD}{'=' * 80}{Colors.ENDC}\n")


def print_section(text: str):
	"""Print section header."""
	print(f"\n{Colors.OKCYAN}{Colors.BOLD}{text}{Colors.ENDC}")
	print(f"{Colors.OKCYAN}{'-' * 80}{Colors.ENDC}")


def print_success(text: str):
	"""Print success message."""
	print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_error(text: str):
	"""Print error message."""
	print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_warning(text: str):
	"""Print warning message."""
	print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def find_rom() -> Path:
	"""Find Dragon Warrior ROM automatically."""
	possible_paths = [
		Path("roms") / "Dragon Warrior (U) (PRG1) [!].nes",
		Path("../roms") / "Dragon Warrior (U) (PRG1) [!].nes",
		Path("../../roms") / "Dragon Warrior (U) (PRG1) [!].nes",
	]
	
	for path in possible_paths:
		if path.exists():
			return path
	
	return None


def check_environment() -> Tuple[bool, List[str]]:
	"""Check if environment is ready for testing."""
	issues = []
	
	# Check Python version
	if sys.version_info < (3, 7):
		issues.append(f"Python 3.7+ required (current: {sys.version_info.major}.{sys.version_info.minor})")
	
	# Check required modules
	try:
		import numpy
	except ImportError:
		issues.append("NumPy not installed (pip install numpy)")
	
	try:
		import PIL
	except ImportError:
		issues.append("PIL not installed (pip install pillow)")
	
	# Check ROM
	rom_path = find_rom()
	if not rom_path:
		issues.append("Dragon Warrior ROM not found in roms/ directory")
	
	# Check test directory
	test_dir = Path("tests")
	if not test_dir.exists():
		issues.append("tests/ directory not found")
	
	return len(issues) == 0, issues


def run_quick_tests():
	"""Run quick smoke tests."""
	print_section("Quick Smoke Tests")
	
	tests_passed = 0
	tests_failed = 0
	
	# Test 1: ROM exists and is valid
	rom_path = find_rom()
	if rom_path and rom_path.exists():
		size = os.path.getsize(rom_path)
		if size > 0:
			print_success(f"ROM found: {rom_path.name} ({size:,} bytes)")
			tests_passed += 1
		else:
			print_error(f"ROM file is empty: {rom_path}")
			tests_failed += 1
	else:
		print_error("ROM not found")
		tests_failed += 1
	
	# Test 2: Tools directory
	if Path("tools").exists():
		tool_count = len(list(Path("tools").glob("*.py")))
		print_success(f"Tools directory found ({tool_count} Python files)")
		tests_passed += 1
	else:
		print_error("Tools directory not found")
		tests_failed += 1
	
	# Test 3: Import master editor
	try:
		sys.path.insert(0, "tools")
		from dragon_warrior_master_editor import ROMManager
		print_success("Master editor module loads successfully")
		tests_passed += 1
	except Exception as e:
		print_error(f"Failed to import master editor: {e}")
		tests_failed += 1
	
	# Test 4: Import test suite
	try:
		sys.path.insert(0, "tests")
		import test_rom_toolkit
		print_success("Test suite module loads successfully")
		tests_passed += 1
	except Exception as e:
		print_error(f"Failed to import test suite: {e}")
		tests_failed += 1
	
	print(f"\nQuick Tests: {Colors.OKGREEN}{tests_passed} passed{Colors.ENDC}, "
		  f"{Colors.FAIL}{tests_failed} failed{Colors.ENDC}")
	
	return tests_failed == 0


def run_full_tests(verbose: bool = False):
	"""Run full test suite."""
	print_section("Full Test Suite")
	
	# Add paths
	sys.path.insert(0, "tools")
	sys.path.insert(0, "tests")
	
	# Import test module
	try:
		import test_rom_toolkit
	except ImportError as e:
		print_error(f"Cannot import test suite: {e}")
		return False
	
	# Run tests
	loader = unittest.TestLoader()
	suite = loader.loadTestsFromModule(test_rom_toolkit)
	
	verbosity = 2 if verbose else 1
	runner = unittest.TextTestRunner(verbosity=verbosity)
	
	start_time = time.time()
	result = runner.run(suite)
	elapsed = time.time() - start_time
	
	# Print summary
	print_section("Test Summary")
	
	total = result.testsRun
	passed = total - len(result.failures) - len(result.errors)
	failed = len(result.failures)
	errors = len(result.errors)
	skipped = len(result.skipped)
	
	print(f"Total Tests:   {total}")
	print(f"{Colors.OKGREEN}✓ Passed:      {passed}{Colors.ENDC}")
	if failed > 0:
		print(f"{Colors.FAIL}✗ Failed:      {failed}{Colors.ENDC}")
	else:
		print(f"✓ Failed:      {failed}")
	if errors > 0:
		print(f"{Colors.FAIL}✗ Errors:      {errors}{Colors.ENDC}")
	else:
		print(f"✓ Errors:      {errors}")
	if skipped > 0:
		print(f"{Colors.WARNING}⚠ Skipped:     {skipped}{Colors.ENDC}")
	print(f"Time:          {elapsed:.3f}s")
	
	print()
	if result.wasSuccessful():
		print_success("ALL TESTS PASSED!")
		return True
	else:
		print_error("SOME TESTS FAILED")
		return False


def main():
	"""Main entry point."""
	import argparse
	
	parser = argparse.ArgumentParser(
		description="Quick test runner for Dragon Warrior ROM Toolkit",
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  python quick_test.py              # Run quick smoke tests
  python quick_test.py --full       # Run full test suite
  python quick_test.py --full -v    # Verbose output
  python quick_test.py --check      # Check environment only
		"""
	)
	
	parser.add_argument('--full', action='store_true',
					   help='Run full test suite')
	parser.add_argument('-v', '--verbose', action='store_true',
					   help='Verbose test output')
	parser.add_argument('--check', action='store_true',
					   help='Check environment only')
	
	args = parser.parse_args()
	
	print_header("DRAGON WARRIOR ROM TOOLKIT - QUICK TEST")
	
	# Environment check
	print_section("Environment Check")
	
	env_ok, issues = check_environment()
	
	if env_ok:
		print_success("Environment is ready!")
	else:
		print_warning(f"Found {len(issues)} issue(s):")
		for issue in issues:
			print(f"  • {issue}")
	
	if args.check:
		return 0 if env_ok else 1
	
	if not env_ok:
		print_warning("\nContinuing with tests despite environment issues...")
	
	# Run tests
	if args.full:
		success = run_full_tests(verbose=args.verbose)
	else:
		success = run_quick_tests()
	
	# Exit code
	return 0 if success else 1


if __name__ == '__main__':
	sys.exit(main())
