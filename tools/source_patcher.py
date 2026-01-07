#!/usr/bin/env python3
"""
Dragon Warrior Source File Patcher
Modifies original source files to use asset includes instead of hardcoded data
"""

import sys
import io

# Force UTF-8 output encoding for Unicode support (emoji, checkmarks, arrows)
# This fixes UnicodeEncodeError on Windows when printing to cp1252 console
if hasattr(sys.stdout, 'buffer'):
	sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
if hasattr(sys.stderr, 'buffer'):
	sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
import re
from pathlib import Path
from typing import List, Optional, Tuple
import click
from rich.console import Console

console = Console()

class SourcePatcher:
	"""Patches Dragon Warrior source files to use asset includes"""

	def __init__(self, source_dir: str = "source_files", backup_dir: str = "source_files_backup"):
		self.source_dir = Path(source_dir)
		self.backup_dir = Path(backup_dir)

	def patch_all_sources(self) -> bool:
		"""Patch all source files to use asset includes"""
		console.print("[blue]🔧 Patching source files to use asset includes...[/blue]\n")

		# Create backup directory
		self.backup_dir.mkdir(parents=True, exist_ok=True)

		success = True

		# Patch Bank01.asm for monster data
		bank01_success = self._patch_bank01_monster_data()
		if not bank01_success:
			success = False

		# TODO: Add patching for other data tables in other banks

		if success:
			console.print("[green]✅ All source files patched successfully![/green]")
		else:
			console.print("[red]❌ Some source file patches failed[/red]")

		return success

	def _patch_bank01_monster_data(self) -> bool:
		"""Patch Bank01.asm to include monster data instead of hardcoded table"""
		try:
			bank01_file = self.source_dir / "Bank01.asm"
			backup_file = self.backup_dir / "Bank01.asm"

			if not bank01_file.exists():
				console.print(f"[red]❌ Bank01.asm not found: {bank01_file}[/red]")
				return False

			# Create backup
			console.print(f"[dim]Creating backup: {backup_file}[/dim]")
			with open(bank01_file, 'r', encoding='utf-8') as f:
				original_content = f.read()
			with open(backup_file, 'w', encoding='utf-8') as f:
				f.write(original_content)

			# Find and replace the EnStatTbl section
			lines = original_content.split('\n')

			# Find the EnStatTbl section
			enstattbl_start = -1
			enstattbl_end = -1

			for i, line in enumerate(lines):
				if 'EnStatTblPtr:' in line:
					# Keep the pointer but look for the table
					continue
				elif 'EnStatTbl:' in line:
					enstattbl_start = i
				elif enstattbl_start != -1 and line.strip().startswith(';----------------------------------------------------------------------------------------------------'):
					# Found the separator line that marks end of monster table
					enstattbl_end = i
					break

			if enstattbl_start == -1:
				console.print("[yellow]⚠️  Could not find EnStatTbl in Bank01.asm[/yellow]")
				return False

			if enstattbl_end == -1:
				console.print("[yellow]⚠️  Could not find end of EnStatTbl table[/yellow]")
				return False

			console.print(f"[dim]Found EnStatTbl at lines {enstattbl_start+1}-{enstattbl_end}[/dim]")

			# Replace the table section with an include
			new_lines = (
				lines[:enstattbl_start] +
				[
					"EnStatTbl:",
					".ifdef USE_EDITED_ASSETS",
					"\t.include \"build/generated/monster_data.asm\"",
					".else",
					"\t.include \"build/default_assets/default_monster_data.asm\"",
					".endif",
					""
				] +
				lines[enstattbl_end:]
			)

			# Write modified file
			modified_content = '\n'.join(new_lines)
			with open(bank01_file, 'w', encoding='utf-8') as f:
				f.write(modified_content)

			console.print(f"[green]✅ Patched {bank01_file}[/green]")
			console.print(f"[dim]Replaced {enstattbl_end - enstattbl_start} lines with asset include[/dim]")

			return True

		except Exception as e:
			console.print(f"[red]❌ Error patching Bank01.asm: {e}[/red]")
			return False

	def restore_backups(self) -> bool:
		"""Restore original source files from backups"""
		console.print("[blue]🔄 Restoring source files from backups...[/blue]\n")

		if not self.backup_dir.exists():
			console.print(f"[red]❌ Backup directory not found: {self.backup_dir}[/red]")
			return False

		restored_count = 0

		for backup_file in self.backup_dir.glob("*.asm"):
			original_file = self.source_dir / backup_file.name

			try:
				with open(backup_file, 'r', encoding='utf-8') as f:
					content = f.read()
				with open(original_file, 'w', encoding='utf-8') as f:
					f.write(content)

				console.print(f"[green]✅ Restored {original_file}[/green]")
				restored_count += 1

			except Exception as e:
				console.print(f"[red]❌ Error restoring {original_file}: {e}[/red]")

		console.print(f"[cyan]Restored {restored_count} files from backup[/cyan]")
		return restored_count > 0

@click.command()
@click.option('--source-dir', default='source_files', help='Source files directory')
@click.option('--backup-dir', default='source_files_backup', help='Backup directory')
@click.option('--restore', is_flag=True, help='Restore from backups instead of patching')
def patch_sources(source_dir: str, backup_dir: str, restore: bool):
	"""Patch Dragon Warrior source files to use asset includes"""

	patcher = SourcePatcher(source_dir, backup_dir)

	if restore:
		success = patcher.restore_backups()
	else:
		success = patcher.patch_all_sources()

	if not success:
		console.print("[red]❌ Operation failed[/red]")
		exit(1)

if __name__ == "__main__":
	patch_sources()
