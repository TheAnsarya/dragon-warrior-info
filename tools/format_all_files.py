#!/usr/bin/env python3
"""
Format All Files - Convert Spaces to Tabs

Systematically converts all indentation from spaces to tabs across the entire
codebase. Processes files in order: Python, JSON, Markdown, Assembly, then others.

Usage:
	python tools/format_all_files.py [--dry-run] [--verbose]

Options:
	--dry-run: Show what would be changed without modifying files
	--verbose: Print detailed information about each file processed
"""

import os
import sys
import argparse
import re
from pathlib import Path
from typing import List, Tuple, Dict
import json


class FileFormatter:
	"""Handles conversion of spaces to tabs for various file types."""

	def __init__(self, dry_run: bool = False, verbose: bool = False):
		self.dry_run = dry_run
		self.verbose = verbose
		self.stats = {
			'processed': 0,
			'modified': 0,
			'errors': 0,
			'by_type': {}
		}

	def convert_indentation(self, content: str, tab_width: int = 4) -> Tuple[str, int]:
		"""
		Convert leading spaces to tabs.

		Args:
			content: File content to convert
			tab_width: Number of spaces per tab (default 4)

		Returns:
			Tuple of (converted_content, num_lines_changed)
		"""
		lines = content.split('\n')
		converted_lines = []
		changes = 0

		for line in lines:
			# Count leading spaces
			stripped = line.lstrip(' ')
			if line and not stripped.startswith('\t'):
				spaces = len(line) - len(stripped)
				if spaces > 0:
					# Convert spaces to tabs
					tabs = spaces // tab_width
					remaining_spaces = spaces % tab_width
					new_line = ('\t' * tabs) + (' ' * remaining_spaces) + stripped
					if new_line != line:
						changes += 1
					converted_lines.append(new_line)
				else:
					converted_lines.append(line)
			else:
				converted_lines.append(line)

		return '\n'.join(converted_lines), changes

	def format_python(self, filepath: Path) -> bool:
		"""Format Python file with tab indentation."""
		try:
			with open(filepath, 'r', encoding='utf-8') as f:
				content = f.read()

			converted, changes = self.convert_indentation(content, tab_width=4)

			if changes > 0:
				if self.verbose:
					print(f"  {filepath}: {changes} lines changed")

				if not self.dry_run:
					with open(filepath, 'w', encoding='utf-8') as f:
						f.write(converted)

				self.stats['modified'] += 1
				return True

			return False

		except Exception as e:
			print(f"ERROR processing {filepath}: {e}", file=sys.stderr)
			self.stats['errors'] += 1
			return False

	def format_json(self, filepath: Path) -> bool:
		"""Format JSON file with tab indentation."""
		try:
			with open(filepath, 'r', encoding='utf-8') as f:
				data = json.load(f)

			# Re-serialize with tabs
			formatted = json.dumps(data, indent='\t', ensure_ascii=False)

			if not self.dry_run:
				with open(filepath, 'w', encoding='utf-8') as f:
					f.write(formatted)
					f.write('\n')  # Ensure newline at end

			if self.verbose:
				print(f"  {filepath}: formatted")

			self.stats['modified'] += 1
			return True

		except json.JSONDecodeError as e:
			print(f"ERROR: Invalid JSON in {filepath}: {e}", file=sys.stderr)
			self.stats['errors'] += 1
			return False
		except Exception as e:
			print(f"ERROR processing {filepath}: {e}", file=sys.stderr)
			self.stats['errors'] += 1
			return False

	def format_markdown(self, filepath: Path) -> bool:
		"""Format Markdown file - preserve code blocks, convert other indents."""
		try:
			with open(filepath, 'r', encoding='utf-8') as f:
				content = f.read()

			lines = content.split('\n')
			converted_lines = []
			in_code_block = False
			changes = 0

			for line in lines:
				# Track code blocks (preserve spaces in code)
				if line.strip().startswith('```'):
					in_code_block = not in_code_block
					converted_lines.append(line)
					continue

				if in_code_block:
					# Preserve code block content exactly
					converted_lines.append(line)
				else:
					# Convert list indentation and other leading spaces
					stripped = line.lstrip(' ')
					if line and not stripped.startswith('\t'):
						spaces = len(line) - len(stripped)
						if spaces > 0:
							# For markdown, use tab_width=2 for list nesting
							tabs = spaces // 2
							remaining = spaces % 2
							new_line = ('\t' * tabs) + (' ' * remaining) + stripped
							if new_line != line:
								changes += 1
							converted_lines.append(new_line)
						else:
							converted_lines.append(line)
					else:
						converted_lines.append(line)

			if changes > 0:
				if self.verbose:
					print(f"  {filepath}: {changes} lines changed")

				if not self.dry_run:
					with open(filepath, 'w', encoding='utf-8') as f:
						f.write('\n'.join(converted_lines))

				self.stats['modified'] += 1
				return True

			return False

		except Exception as e:
			print(f"ERROR processing {filepath}: {e}", file=sys.stderr)
			self.stats['errors'] += 1
			return False

	def format_assembly(self, filepath: Path) -> bool:
		"""Format assembly file with tab indentation."""
		try:
			with open(filepath, 'r', encoding='utf-8') as f:
				content = f.read()

			# Assembly typically uses 8-space tabs
			converted, changes = self.convert_indentation(content, tab_width=8)

			if changes > 0:
				if self.verbose:
					print(f"  {filepath}: {changes} lines changed")

				if not self.dry_run:
					with open(filepath, 'w', encoding='utf-8') as f:
						f.write(converted)

				self.stats['modified'] += 1
				return True

			return False

		except Exception as e:
			print(f"ERROR processing {filepath}: {e}", file=sys.stderr)
			self.stats['errors'] += 1
			return False

	def format_generic(self, filepath: Path, tab_width: int = 4) -> bool:
		"""Format generic text file with tab indentation."""
		try:
			with open(filepath, 'r', encoding='utf-8') as f:
				content = f.read()

			converted, changes = self.convert_indentation(content, tab_width=tab_width)

			if changes > 0:
				if self.verbose:
					print(f"  {filepath}: {changes} lines changed")

				if not self.dry_run:
					with open(filepath, 'w', encoding='utf-8') as f:
						f.write(converted)

				self.stats['modified'] += 1
				return True

			return False

		except Exception as e:
			print(f"ERROR processing {filepath}: {e}", file=sys.stderr)
			self.stats['errors'] += 1
			return False

	def process_file(self, filepath: Path) -> None:
		"""Process a single file based on its extension."""
		ext = filepath.suffix.lower()

		# Track by file type
		if ext not in self.stats['by_type']:
			self.stats['by_type'][ext] = {'processed': 0, 'modified': 0}

		self.stats['by_type'][ext]['processed'] += 1
		self.stats['processed'] += 1

		# Route to appropriate formatter
		if ext == '.py':
			modified = self.format_python(filepath)
		elif ext == '.json':
			modified = self.format_json(filepath)
		elif ext in ['.md', '.markdown']:
			modified = self.format_markdown(filepath)
		elif ext in ['.asm', '.s']:
			modified = self.format_assembly(filepath)
		elif ext in ['.txt', '.yml', '.yaml', '.xml', '.html', '.css', '.js']:
			modified = self.format_generic(filepath)
		else:
			# Skip unknown file types
			return

		if modified:
			self.stats['by_type'][ext]['modified'] += 1


def find_files(root_dir: Path, patterns: List[str]) -> List[Path]:
	"""Find all files matching the given patterns."""
	files = []

	# Directories to skip
	skip_dirs = {
		'.git', '__pycache__', 'node_modules', 'venv', '.venv',
		'build', 'dist', '.pytest_cache', '.mypy_cache',
		'Ophis', 'output', 'roms'  # Project-specific
	}

	for pattern in patterns:
		for filepath in root_dir.rglob(pattern):
			# Skip if in excluded directory
			if any(skip in filepath.parts for skip in skip_dirs):
				continue

			if filepath.is_file():
				files.append(filepath)

	return files


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Convert all indentation from spaces to tabs'
	)
	parser.add_argument(
		'--dry-run',
		action='store_true',
		help='Show what would be changed without modifying files'
	)
	parser.add_argument(
		'--verbose',
		action='store_true',
		help='Print detailed information about each file'
	)
	parser.add_argument(
		'--root',
		type=Path,
		default=Path.cwd(),
		help='Root directory to process (default: current directory)'
	)

	args = parser.parse_args()

	formatter = FileFormatter(dry_run=args.dry_run, verbose=args.verbose)
	root = args.root

	if args.dry_run:
		print("DRY RUN MODE - No files will be modified\n")

	# Process files in priority order
	file_groups = [
		('Python files', ['*.py']),
		('JSON files', ['*.json']),
		('Markdown files', ['*.md', '*.markdown']),
		('Assembly files', ['*.asm', '*.s']),
		('Other files', ['*.txt', '*.yml', '*.yaml', '*.xml', '*.html', '*.css', '*.js'])
	]

	for group_name, patterns in file_groups:
		print(f"\n{'=' * 60}")
		print(f"Processing {group_name}")
		print('=' * 60)

		files = find_files(root, patterns)
		print(f"Found {len(files)} files")

		if not args.verbose and files:
			print("Processing...", end='', flush=True)

		for filepath in sorted(files):
			formatter.process_file(filepath)
			if not args.verbose:
				print('.', end='', flush=True)

		if not args.verbose and files:
			print()  # Newline after progress dots

	# Print summary
	print(f"\n{'=' * 60}")
	print("SUMMARY")
	print('=' * 60)
	print(f"Total files processed: {formatter.stats['processed']}")
	print(f"Files modified: {formatter.stats['modified']}")
	print(f"Errors: {formatter.stats['errors']}")

	if formatter.stats['by_type']:
		print("\nBy file type:")
		for ext, counts in sorted(formatter.stats['by_type'].items()):
			print(f"  {ext}: {counts['modified']}/{counts['processed']} modified")

	if args.dry_run:
		print("\nDRY RUN COMPLETE - No files were actually modified")
		print("Run without --dry-run to apply changes")

	return 0 if formatter.stats['errors'] == 0 else 1


if __name__ == '__main__':
	sys.exit(main())
