#!/usr/bin/env python3
"""
Fix Unicode encoding issues in all Python files.

This script adds UTF-8 encoding wrapper to all Python files that:
1. Have 'import sys' but not the io.TextIOWrapper fix
2. Use print() statements

The fix ensures proper Unicode output on Windows consoles that use cp1252 encoding.

Usage:
	python fix_unicode_encoding.py [--dry-run] [--verbose]

Options:
	--dry-run   Show what would be changed without modifying files
	--verbose   Show detailed output for all files
"""

import os
import re
import sys
import argparse
from pathlib import Path

# The encoding fix to insert
UTF8_FIX = '''import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
'''


def needs_fix(content: str) -> bool:
	"""Check if file needs the UTF-8 encoding fix."""
	# Skip if already has the fix
	if 'io.TextIOWrapper' in content:
		return False
	# Skip if no print statements
	if 'print(' not in content:
		return False
	return True


def apply_fix(content: str) -> str:
	"""Apply the UTF-8 encoding fix to file content."""
	# Find import sys and add after it
	# Pattern: 'import sys' possibly followed by newline and other imports
	sys_import_pattern = r'(import sys\n)'

	if re.search(sys_import_pattern, content):
		# Add after 'import sys'
		return re.sub(sys_import_pattern, r'\1' + UTF8_FIX, content, count=1)

	# If no 'import sys', find first import block and add sys import with fix
	first_import_pattern = r'(^import |^from )'
	match = re.search(first_import_pattern, content, re.MULTILINE)
	if match:
		insert_pos = match.start()
		return content[:insert_pos] + 'import sys\n' + UTF8_FIX + content[insert_pos:]

	# If no imports at all (unlikely), add after docstring
	docstring_pattern = r'("""[\s\S]*?""")\n'
	match = re.search(docstring_pattern, content)
	if match:
		insert_pos = match.end()
		return content[:insert_pos] + '\nimport sys\n' + UTF8_FIX + content[insert_pos:]

	# Last resort: add at beginning
	return 'import sys\n' + UTF8_FIX + content


def fix_file(filepath: Path, dry_run: bool = False, verbose: bool = False) -> bool:
	"""Fix a single Python file. Returns True if file was modified."""
	try:
		content = filepath.read_text(encoding='utf-8')
	except UnicodeDecodeError:
		if verbose:
			print(f"  ⚠️ Skipping {filepath.name}: Cannot decode as UTF-8")
		return False

	if not needs_fix(content):
		if verbose:
			print(f"  ✓ {filepath.name}: Already fixed or no print statements")
		return False

	if dry_run:
		print(f"  Would fix: {filepath.name}")
		return True

	new_content = apply_fix(content)
	filepath.write_text(new_content, encoding='utf-8')
	print(f"  ✅ Fixed: {filepath.name}")
	return True


def main():
	parser = argparse.ArgumentParser(description='Fix Unicode encoding in Python files')
	parser.add_argument('--dry-run', action='store_true', help='Show what would be changed')
	parser.add_argument('--verbose', '-v', action='store_true', help='Show all files')
	args = parser.parse_args()

	# Find all Python files in tools/
	tools_dir = Path(__file__).parent
	py_files = sorted(tools_dir.glob('*.py'))

	print(f"Scanning {len(py_files)} Python files in tools/...")
	if args.dry_run:
		print("(DRY RUN - no files will be modified)")
	print()

	fixed_count = 0
	for filepath in py_files:
		# Skip this script itself
		if filepath.name == 'fix_unicode_encoding.py':
			continue

		if fix_file(filepath, args.dry_run, args.verbose):
			fixed_count += 1

	print()
	if args.dry_run:
		print(f"Would fix {fixed_count} files")
	else:
		print(f"Fixed {fixed_count} files")


if __name__ == '__main__':
	main()
