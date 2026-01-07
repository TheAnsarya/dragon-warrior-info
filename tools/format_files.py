#!/usr/bin/env python3
"""
EditorConfig Formatter

Formats Python files according to .editorconfig rules:
- Convert spaces to tabs
- Ensure UTF-8 encoding
- Ensure CRLF line endings
- Add final newline

Usage:
	python tools/format_files.py [--check] [--fix] [files...]
"""

import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import argparse
import os
import re
from pathlib import Path


def convert_spaces_to_tabs(content: str, spaces_per_tab: int = 4) -> str:
	"""Convert leading spaces to tabs."""
	lines = content.split('\n')
	result = []

	for line in lines:
		# Count leading spaces
		stripped = line.lstrip(' ')
		leading_spaces = len(line) - len(stripped)

		# Convert to tabs
		tabs = leading_spaces // spaces_per_tab
		remaining_spaces = leading_spaces % spaces_per_tab

		new_line = '\t' * tabs + ' ' * remaining_spaces + stripped
		result.append(new_line)

	return '\n'.join(result)


def ensure_crlf(content: str) -> str:
	"""Ensure CRLF line endings."""
	# First normalize to LF, then convert to CRLF
	content = content.replace('\r\n', '\n').replace('\r', '\n')
	return content.replace('\n', '\r\n')


def lowercase_hex(content: str) -> str:
	"""Convert uppercase hex values to lowercase."""
	# Match hex values like $ab, 0xab, #AB
	def lower_hex(match):
		return match.group(0).lower()

	# $XX format
	content = re.sub(r'\$[0-9A-F]{1,4}', lower_hex, content)
	# 0xXX format
	content = re.sub(r'0x[0-9A-F]+', lower_hex, content)

	return content


def check_file(filepath: Path) -> dict:
	"""Check file for formatting issues."""
	issues = []

	try:
		with open(filepath, 'rb') as f:
			raw_content = f.read()

		# Check encoding
		try:
			content = raw_content.decode('utf-8')
		except UnicodeDecodeError:
			issues.append("Not UTF-8 encoded")
			return {'path': str(filepath), 'issues': issues, 'fixable': False}

		# Check for spaces (leading)
		lines = content.split('\n')
		for i, line in enumerate(lines, 1):
			if line.startswith('    '):  # 4 spaces
				issues.append(f"Line {i}: Leading spaces (should be tabs)")
				break  # Only report once

		# Check line endings
		if '\r\n' not in content and '\n' in content:
			issues.append("Uses LF line endings (should be CRLF)")

		# Check for missing final newline
		if content and not content.endswith('\n'):
			issues.append("Missing final newline")

		# Check for uppercase hex (in Python files)
		if filepath.suffix == '.py':
			if re.search(r'\$[0-9A-F]*[A-F][0-9A-F]*', content):
				issues.append("Contains uppercase hex values")
			if re.search(r'0x[0-9A-F]*[A-F][0-9A-F]*', content):
				issues.append("Contains uppercase 0x hex values")

		return {
			'path': str(filepath),
			'issues': issues,
			'fixable': True
		}

	except Exception as e:
		return {'path': str(filepath), 'issues': [f"Error: {e}"], 'fixable': False}


def fix_file(filepath: Path, dry_run: bool = False) -> bool:
	"""Fix formatting issues in a file."""
	try:
		with open(filepath, 'rb') as f:
			raw_content = f.read()

		try:
			content = raw_content.decode('utf-8')
		except UnicodeDecodeError:
			print(f"  Cannot fix non-UTF-8 file: {filepath}")
			return False

		original = content

		# Convert spaces to tabs
		content = convert_spaces_to_tabs(content)

		# Lowercase hex (only for Python files)
		if filepath.suffix == '.py':
			content = lowercase_hex(content)

		# Ensure CRLF
		content = ensure_crlf(content)

		# Ensure final newline
		if content and not content.endswith('\r\n'):
			content += '\r\n'

		if content != original:
			if not dry_run:
				with open(filepath, 'w', encoding='utf-8', newline='') as f:
					f.write(content)
			return True

		return False

	except Exception as e:
		print(f"  Error fixing {filepath}: {e}")
		return False


def main():
	parser = argparse.ArgumentParser(description='Format files according to .editorconfig')
	parser.add_argument('files', nargs='*', help='Files to format (default: all Python files in tools/)')
	parser.add_argument('--check', action='store_true', help='Only check, do not fix')
	parser.add_argument('--fix', action='store_true', help='Fix formatting issues')
	parser.add_argument('--dry-run', action='store_true', help='Show what would be fixed')

	args = parser.parse_args()

	# Find project root
	script_dir = Path(__file__).parent
	project_root = script_dir.parent

	# Get files to check
	if args.files:
		files = [Path(f) for f in args.files]
	else:
		# Default: all Python files in tools/
		tools_dir = project_root / 'tools'
		files = list(tools_dir.glob('*.py'))

	print(f"Checking {len(files)} files...\n")

	files_with_issues = []
	files_fixed = []

	for filepath in sorted(files):
		result = check_file(filepath)

		if result['issues']:
			files_with_issues.append(result)

			if args.check:
				print(f"[X] {filepath.name}")
				for issue in result['issues']:
					print(f"   - {issue}")

			elif args.fix or args.dry_run:
				if result['fixable']:
					fixed = fix_file(filepath, dry_run=args.dry_run)
					if fixed:
						files_fixed.append(filepath)
						if args.dry_run:
							print(f"[W] Would fix: {filepath.name}")
						else:
							print(f"[OK] Fixed: {filepath.name}")
				else:
					print(f"[!] Cannot fix: {filepath.name}")
		else:
			if args.check:
				print(f"[OK] {filepath.name}")

	# Summary
	print(f"\n{'='*50}")
	print(f"Files checked: {len(files)}")
	print(f"Files with issues: {len(files_with_issues)}")

	if args.fix and not args.dry_run:
		print(f"Files fixed: {len(files_fixed)}")
	elif args.dry_run:
		print(f"Files that would be fixed: {len(files_fixed)}")


if __name__ == '__main__':
	main()
