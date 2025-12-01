#!/usr/bin/env python3
"""
Dragon Warrior Build System - Enhanced Error Messages & Troubleshooting

This module provides:
- Detailed error messages with context
- Troubleshooting suggestions for common errors
- Error categorization and logging
- User-friendly explanations

Usage:
	from tools.build_errors import BuildErrorHandler, BuildError

	error_handler = BuildErrorHandler()
	try:
		# build code
	except Exception as e:
		error_handler.handle_error(e, context="asset extraction")

Author: Dragon Warrior ROM Hacking Toolkit
"""

import sys
import os
import traceback
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum, auto
import json
import re


class ErrorCategory(Enum):
	"""Categories of build system errors."""
	FILE_NOT_FOUND = auto()
	FILE_PERMISSION = auto()
	FILE_CORRUPT = auto()
	ROM_INVALID = auto()
	ROM_WRONG_VERSION = auto()
	ASSEMBLER_ERROR = auto()
	ASSEMBLER_SYNTAX = auto()
	ASSEMBLER_MISSING = auto()
	ASSET_INVALID = auto()
	ASSET_MISSING = auto()
	ASSET_CORRUPT = auto()
	JSON_PARSE = auto()
	JSON_SCHEMA = auto()
	PYTHON_IMPORT = auto()
	PYTHON_RUNTIME = auto()
	MEMORY_ERROR = auto()
	DISK_SPACE = auto()
	NETWORK_ERROR = auto()
	CONFIG_ERROR = auto()
	UNKNOWN = auto()


@dataclass
class BuildError:
	"""Structured build error with context and suggestions."""
	category: ErrorCategory
	message: str
	details: str = ""
	file_path: Optional[Path] = None
	line_number: Optional[int] = None
	column: Optional[int] = None
	suggestions: List[str] = field(default_factory=list)
	related_docs: List[str] = field(default_factory=list)
	original_exception: Optional[Exception] = None
	timestamp: datetime = field(default_factory=datetime.now)

	def to_dict(self) -> Dict[str, Any]:
		"""Convert to dictionary for logging."""
		return {
			"category": self.category.name,
			"message": self.message,
			"details": self.details,
			"file_path": str(self.file_path) if self.file_path else None,
			"line_number": self.line_number,
			"column": self.column,
			"suggestions": self.suggestions,
			"related_docs": self.related_docs,
			"timestamp": self.timestamp.isoformat(),
		}


# Common error patterns and their explanations
ERROR_PATTERNS: Dict[str, Tuple[ErrorCategory, str, List[str], List[str]]] = {
	# ROM-related errors
	r"ROM file not found": (
		ErrorCategory.FILE_NOT_FOUND,
		"The Dragon Warrior ROM file could not be found.",
		[
			"Ensure the ROM is in the 'roms/' directory",
			"Expected filename: Dragon Warrior (U) (PRG1) [!].nes",
			"Check file permissions and ensure the file exists",
			"PRG1 is the recommended version for modding",
		],
		["docs/QUICK_START.md", "docs/ROM_SETUP.md"],
	),
	r"Invalid ROM header|iNES header": (
		ErrorCategory.ROM_INVALID,
		"The ROM file has an invalid or missing iNES header.",
		[
			"Ensure you're using an unmodified Dragon Warrior ROM",
			"The ROM should be exactly 65,552 bytes (64KB + 16-byte header)",
			"Check if the file was corrupted during download",
			"Try re-obtaining the ROM from a reliable source",
		],
		["docs/ROM_FORMAT.md"],
	),
	r"PRG0.*not supported|wrong ROM version": (
		ErrorCategory.ROM_WRONG_VERSION,
		"You appear to be using PRG0 instead of PRG1.",
		[
			"This toolkit requires the PRG1 revision of Dragon Warrior",
			"Look for 'Dragon Warrior (U) (PRG1) [!].nes'",
			"PRG0 has known bugs that were fixed in PRG1",
			"Check ROM databases for the correct version",
		],
		["docs/ROM_VERSIONS.md"],
	),

	# Assembler errors
	r"ophis.*not found|assembler not found": (
		ErrorCategory.ASSEMBLER_MISSING,
		"The Ophis assembler was not found.",
		[
			"Ensure Ophis is installed in the 'Ophis/' directory",
			"Download Ophis from: https://michaelcmartin.github.io/Ophis/",
			"On Windows, look for 'Ophis/ophis.exe'",
			"On Linux/Mac, ensure 'ophis' is in your PATH",
		],
		["docs/BUILD_SETUP.md", "Ophis/README"],
	),
	r"Undefined label|Unknown label": (
		ErrorCategory.ASSEMBLER_ERROR,
		"An undefined label was referenced in the assembly code.",
		[
			"Check that all .include files exist and are in the correct location",
			"Ensure label definitions match exactly (case-sensitive)",
			"Verify the source_files/ directory is complete",
			"Check for typos in label names",
		],
		["docs/ASSEMBLY_REFERENCE.md"],
	),
	r"Syntax error|Parse error": (
		ErrorCategory.ASSEMBLER_SYNTAX,
		"There's a syntax error in the assembly code.",
		[
			"Check the line number mentioned in the error",
			"Verify proper Ophis syntax is used",
			"Common issues: missing colons, wrong opcodes, bad addressing modes",
			"Compare with original source files for correct syntax",
		],
		["docs/OPHIS_SYNTAX.md"],
	),
	r"Bank overflow|ROM space exceeded": (
		ErrorCategory.ASSEMBLER_ERROR,
		"The assembled code exceeds the available ROM space.",
		[
			"Your modifications have made the ROM too large",
			"Try removing unused code or data",
			"Consider using bank switching techniques",
			"Check if you accidentally duplicated data",
		],
		["docs/ROM_LAYOUT.md"],
	),

	# Asset errors
	r"asset.*not found|missing asset": (
		ErrorCategory.ASSET_MISSING,
		"A required asset file is missing.",
		[
			"Run 'Extract Assets' from the build menu first",
			"Check that the assets/json/ directory exists",
			"Verify all required JSON files are present",
			"Re-extract assets if files appear corrupted",
		],
		["docs/ASSET_PIPELINE.md"],
	),
	r"Invalid.*JSON|JSON decode error": (
		ErrorCategory.JSON_PARSE,
		"A JSON file contains invalid syntax.",
		[
			"Check for missing commas, brackets, or quotes",
			"Use a JSON validator to find the error location",
			"Restore from backup if available",
			"Common issues: trailing commas, unescaped quotes",
		],
		["docs/JSON_FORMAT.md"],
	),
	r"Schema validation|invalid.*schema": (
		ErrorCategory.JSON_SCHEMA,
		"The JSON data doesn't match the expected format.",
		[
			"Check that all required fields are present",
			"Verify data types match (string, number, array)",
			"Compare with example JSON files in docs/examples/",
			"Check the schema documentation for field requirements",
		],
		["docs/JSON_SCHEMAS.md"],
	),

	# Python errors
	r"ImportError|ModuleNotFoundError": (
		ErrorCategory.PYTHON_IMPORT,
		"A required Python module is missing.",
		[
			"Install requirements: pip install -r requirements.txt",
			"Check that you're using Python 3.8 or newer",
			"Verify your virtual environment is activated",
			"Some optional modules: PIL (Pillow), numpy",
		],
		["docs/REQUIREMENTS.md", "requirements.txt"],
	),
	r"PermissionError|Access denied": (
		ErrorCategory.FILE_PERMISSION,
		"The system denied access to a file or directory.",
		[
			"Close any programs that might have the file open",
			"Check file permissions (read/write access)",
			"On Windows, check if files are marked read-only",
			"Try running as administrator if necessary",
		],
		[],
	),
	r"MemoryError|out of memory": (
		ErrorCategory.MEMORY_ERROR,
		"The system ran out of memory.",
		[
			"Close other applications to free memory",
			"Try processing assets in smaller batches",
			"Check for memory leaks in custom scripts",
			"Consider increasing system swap/page file",
		],
		[],
	),
	r"No space left|disk full": (
		ErrorCategory.DISK_SPACE,
		"There is not enough disk space.",
		[
			"Free up disk space (build requires ~50MB)",
			"Clean build artifacts: run 'Clean Build'",
			"Check that temp directories aren't full",
			"Move project to a drive with more space",
		],
		[],
	),
}


class BuildErrorHandler:
	"""Enhanced error handler with categorization and suggestions."""

	def __init__(self, log_dir: Optional[Path] = None):
		"""Initialize the error handler.

		Args:
			log_dir: Directory for error logs. Defaults to 'logs/build_errors/'
		"""
		self.log_dir = log_dir or Path("logs/build_errors")
		self.log_dir.mkdir(parents=True, exist_ok=True)
		self.errors: List[BuildError] = []
		self.warnings: List[str] = []

	def categorize_error(self, error: Exception, context: str = "") -> BuildError:
		"""Categorize an error and generate helpful suggestions.

		Args:
			error: The exception that occurred.
			context: Additional context about what was happening.

		Returns:
			A BuildError with categorized information and suggestions.
		"""
		error_str = str(error).lower()
		error_type = type(error).__name__

		# Try to match against known patterns
		for pattern, (category, explanation, suggestions, docs) in ERROR_PATTERNS.items():
			if re.search(pattern, str(error), re.IGNORECASE):
				return BuildError(
					category=category,
					message=explanation,
					details=f"{error_type}: {error}\nContext: {context}",
					suggestions=suggestions,
					related_docs=docs,
					original_exception=error,
				)

		# Parse file/line info from traceback
		file_path = None
		line_number = None
		tb = traceback.extract_tb(error.__traceback__)
		if tb:
			last_frame = tb[-1]
			file_path = Path(last_frame.filename)
			line_number = last_frame.lineno

		# Fallback for unknown errors
		return BuildError(
			category=ErrorCategory.UNKNOWN,
			message=f"An unexpected error occurred: {error_type}",
			details=f"{error}\n\nContext: {context}\n\nFull traceback:\n{traceback.format_exc()}",
			file_path=file_path,
			line_number=line_number,
			suggestions=[
				"Check the full error details above",
				"Search the project issues on GitHub",
				"Ensure all prerequisites are installed",
				"Try running with --verbose for more info",
			],
			related_docs=["docs/TROUBLESHOOTING.md"],
			original_exception=error,
		)

	def handle_error(self, error: Exception, context: str = "", raise_error: bool = False) -> BuildError:
		"""Handle an error with logging and user-friendly output.

		Args:
			error: The exception that occurred.
			context: Additional context about what was happening.
			raise_error: Whether to re-raise after handling.

		Returns:
			The categorized BuildError.
		"""
		build_error = self.categorize_error(error, context)
		self.errors.append(build_error)

		# Log to file
		self._log_error(build_error)

		if raise_error:
			raise error

		return build_error

	def format_error(self, build_error: BuildError, use_rich: bool = True) -> str:
		"""Format an error for display.

		Args:
			build_error: The error to format.
			use_rich: Whether to use rich markup.

		Returns:
			Formatted error string.
		"""
		lines = []

		if use_rich:
			lines.append(f"\n[bold red]❌ {build_error.category.name.replace('_', ' ')}[/bold red]")
			lines.append(f"[red]{build_error.message}[/red]")

			if build_error.file_path:
				location = f"[dim]Location: {build_error.file_path}"
				if build_error.line_number:
					location += f":{build_error.line_number}"
				location += "[/dim]"
				lines.append(location)

			if build_error.details:
				lines.append(f"\n[dim]Details:[/dim]\n{build_error.details}")

			if build_error.suggestions:
				lines.append("\n[cyan]💡 Suggestions:[/cyan]")
				for i, suggestion in enumerate(build_error.suggestions, 1):
					lines.append(f"  {i}. {suggestion}")

			if build_error.related_docs:
				lines.append("\n[yellow]📚 Related Documentation:[/yellow]")
				for doc in build_error.related_docs:
					lines.append(f"  • {doc}")
		else:
			lines.append(f"\n❌ {build_error.category.name.replace('_', ' ')}")
			lines.append(f"   {build_error.message}")

			if build_error.file_path:
				location = f"   Location: {build_error.file_path}"
				if build_error.line_number:
					location += f":{build_error.line_number}"
				lines.append(location)

			if build_error.details:
				lines.append(f"\n   Details:\n   {build_error.details}")

			if build_error.suggestions:
				lines.append("\n   💡 Suggestions:")
				for i, suggestion in enumerate(build_error.suggestions, 1):
					lines.append(f"     {i}. {suggestion}")

			if build_error.related_docs:
				lines.append("\n   📚 Related Documentation:")
				for doc in build_error.related_docs:
					lines.append(f"     • {doc}")

		return "\n".join(lines)

	def print_error(self, build_error: BuildError) -> None:
		"""Print an error to the console.

		Args:
			build_error: The error to print.
		"""
		try:
			from rich.console import Console
			from rich.panel import Panel
			console = Console()
			formatted = self.format_error(build_error, use_rich=True)
			console.print(Panel(formatted, title="Build Error", border_style="red"))
		except ImportError:
			print(self.format_error(build_error, use_rich=False))

	def _log_error(self, build_error: BuildError) -> None:
		"""Log an error to file.

		Args:
			build_error: The error to log.
		"""
		timestamp = build_error.timestamp.strftime("%Y%m%d_%H%M%S")
		log_file = self.log_dir / f"error_{timestamp}.json"

		try:
			with open(log_file, 'w', encoding='utf-8') as f:
				json.dump(build_error.to_dict(), f, indent='\t')
		except Exception:
			pass  # Don't fail on logging errors

	def get_summary(self) -> str:
		"""Get a summary of all errors.

		Returns:
			Summary string with error counts by category.
		"""
		if not self.errors:
			return "No errors recorded."

		counts: Dict[ErrorCategory, int] = {}
		for error in self.errors:
			counts[error.category] = counts.get(error.category, 0) + 1

		lines = [f"Total errors: {len(self.errors)}"]
		for category, count in sorted(counts.items(), key=lambda x: x[1], reverse=True):
			lines.append(f"  {category.name}: {count}")

		return "\n".join(lines)

	def add_warning(self, message: str) -> None:
		"""Add a warning message.

		Args:
			message: The warning message.
		"""
		self.warnings.append(message)

	def print_warnings(self) -> None:
		"""Print all accumulated warnings."""
		if not self.warnings:
			return

		try:
			from rich.console import Console
			console = Console()
			console.print(f"\n[yellow]⚠️ {len(self.warnings)} Warning(s):[/yellow]")
			for warning in self.warnings:
				console.print(f"  • {warning}")
		except ImportError:
			print(f"\n⚠️ {len(self.warnings)} Warning(s):")
			for warning in self.warnings:
				print(f"  • {warning}")

	def clear(self) -> None:
		"""Clear all recorded errors and warnings."""
		self.errors.clear()
		self.warnings.clear()


# Convenience functions for quick error handling
def handle_build_error(error: Exception, context: str = "") -> BuildError:
	"""Quick error handling without instantiating handler.

	Args:
		error: The exception that occurred.
		context: Additional context.

	Returns:
		Categorized BuildError.
	"""
	handler = BuildErrorHandler()
	return handler.handle_error(error, context)


def print_build_error(error: Exception, context: str = "") -> None:
	"""Quick error printing.

	Args:
		error: The exception that occurred.
		context: Additional context.
	"""
	handler = BuildErrorHandler()
	build_error = handler.handle_error(error, context)
	handler.print_error(build_error)


# Assembler-specific error parser
class AssemblerErrorParser:
	"""Parse and explain Ophis assembler errors."""

	# Ophis-specific error patterns
	OPHIS_ERRORS = {
		r"Undefined label '([^']+)'": (
			"Undefined Label",
			"The label '{0}' is used but never defined.",
			[
				"Check spelling of the label (case-sensitive)",
				"Ensure the file defining the label is included",
				"Look for the label in source_files/*.asm",
			],
		),
		r"Illegal instruction '([^']+)'": (
			"Illegal Instruction",
			"The instruction '{0}' is not a valid 6502 opcode.",
			[
				"Check the opcode spelling",
				"Valid opcodes: LDA, STA, LDX, STX, LDY, STY, etc.",
				"See 6502 instruction reference",
			],
		),
		r"Range error: value ([^:]+)": (
			"Range Error",
			"The value {0} is out of range.",
			[
				"For zero-page addressing, value must be 0-255",
				"For branches, target must be within -128 to +127 bytes",
				"Check if you meant to use absolute addressing",
			],
		),
		r"Recursive include": (
			"Recursive Include",
			"A file is including itself, creating an infinite loop.",
			[
				"Check your .include directives",
				"Look for circular include chains",
				"Use include guards if necessary",
			],
		),
		r"File not found: '([^']+)'": (
			"Include File Not Found",
			"The file '{0}' could not be found.",
			[
				"Check the file path is correct",
				"Paths are relative to the assembler's working directory",
				"Ensure the file exists in source_files/",
			],
		),
	}

	@classmethod
	def parse_error(cls, stderr: str, source_dir: Path = None) -> List[BuildError]:
		"""Parse assembler stderr output for errors.

		Args:
			stderr: The stderr output from the assembler.
			source_dir: Path to source files for context.

		Returns:
			List of parsed BuildErrors.
		"""
		errors = []
		lines = stderr.strip().split('\n')

		for line in lines:
			if not line.strip():
				continue

			# Try to parse file:line format
			file_match = re.match(r'^(.+?):(\d+):\s*(.+)$', line)
			if file_match:
				file_path = Path(file_match.group(1))
				line_number = int(file_match.group(2))
				error_msg = file_match.group(3)
			else:
				file_path = None
				line_number = None
				error_msg = line

			# Match against known patterns
			matched = False
			for pattern, (title, explanation, suggestions) in cls.OPHIS_ERRORS.items():
				match = re.search(pattern, error_msg, re.IGNORECASE)
				if match:
					# Format with captured groups
					formatted_explanation = explanation.format(*match.groups())
					errors.append(BuildError(
						category=ErrorCategory.ASSEMBLER_ERROR,
						message=title,
						details=formatted_explanation,
						file_path=file_path,
						line_number=line_number,
						suggestions=suggestions,
						related_docs=["docs/OPHIS_SYNTAX.md", "docs/6502_REFERENCE.md"],
					))
					matched = True
					break

			if not matched and error_msg.strip():
				# Generic assembler error
				errors.append(BuildError(
					category=ErrorCategory.ASSEMBLER_ERROR,
					message="Assembler Error",
					details=error_msg,
					file_path=file_path,
					line_number=line_number,
					suggestions=[
						"Check the error message above",
						"Verify syntax at the indicated line",
						"Compare with original source files",
					],
					related_docs=["docs/OPHIS_SYNTAX.md"],
				))

		return errors


# Quick diagnostic checks
def run_diagnostics() -> Dict[str, Any]:
	"""Run quick diagnostic checks for common issues.

	Returns:
		Dictionary with diagnostic results.
	"""
	results = {
		"python_version": sys.version,
		"working_directory": os.getcwd(),
		"checks": {},
	}

	# Check Python version
	results["checks"]["python_3.8+"] = sys.version_info >= (3, 8)

	# Check required directories
	required_dirs = ["source_files", "roms", "Ophis", "tools", "assets"]
	for dir_name in required_dirs:
		results["checks"][f"dir_{dir_name}"] = Path(dir_name).exists()

	# Check required files
	required_files = [
		"tools/asset_pipeline.py",
		"Ophis/ophis.exe",
		"requirements.txt",
	]
	for file_name in required_files:
		results["checks"][f"file_{file_name}"] = Path(file_name).exists()

	# Check for ROM
	roms_dir = Path("roms")
	rom_found = False
	if roms_dir.exists():
		rom_files = list(roms_dir.glob("*.nes"))
		rom_found = len(rom_files) > 0
		results["rom_files"] = [str(f) for f in rom_files]
	results["checks"]["rom_present"] = rom_found

	# Check imports
	for module in ["PIL", "numpy", "click", "rich"]:
		try:
			__import__(module.lower().replace("PIL", "PIL"))
			results["checks"][f"import_{module}"] = True
		except ImportError:
			results["checks"][f"import_{module}"] = False

	# Summary
	failed = [k for k, v in results["checks"].items() if not v]
	results["all_passed"] = len(failed) == 0
	results["failed_checks"] = failed

	return results


def print_diagnostics() -> None:
	"""Print diagnostic results to console."""
	results = run_diagnostics()

	try:
		from rich.console import Console
		from rich.table import Table
		from rich import box

		console = Console()
		console.print("\n[bold cyan]🔍 Build System Diagnostics[/bold cyan]\n")

		table = Table(box=box.SIMPLE)
		table.add_column("Check", style="cyan")
		table.add_column("Status", justify="center")

		for check, passed in results["checks"].items():
			status = "[green]✅[/green]" if passed else "[red]❌[/red]"
			table.add_row(check.replace("_", " ").title(), status)

		console.print(table)

		if results["all_passed"]:
			console.print("\n[bold green]✅ All diagnostics passed![/bold green]")
		else:
			console.print(f"\n[bold red]❌ {len(results['failed_checks'])} check(s) failed:[/bold red]")
			for check in results["failed_checks"]:
				console.print(f"  • {check}")

	except ImportError:
		print("\n🔍 Build System Diagnostics\n")
		for check, passed in results["checks"].items():
			status = "✅" if passed else "❌"
			print(f"  {status} {check.replace('_', ' ').title()}")

		if results["all_passed"]:
			print("\n✅ All diagnostics passed!")
		else:
			print(f"\n❌ {len(results['failed_checks'])} check(s) failed:")
			for check in results["failed_checks"]:
				print(f"  • {check}")


if __name__ == "__main__":
	# Run diagnostics when called directly
	print_diagnostics()
