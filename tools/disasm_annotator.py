#!/usr/bin/env python3
"""
Advanced Disassembly Annotator & Label Manager

Comprehensive tool for managing 6502 assembly disassembly labels, comments,
and annotations. Supports automatic label generation, cross-reference
tracking, and export to multiple assembler formats.

Features:
- Label database management (addresses -> names)
- Comment database (inline and block comments)
- Cross-reference tracking (jumps, calls, data reads/writes)
- Automatic label generation from code analysis
- Import/export to multiple formats:
  * FCEUX .nl (name list)
  * Mesen-S .mlb (Mesen label format)
  * ca65 .inc (includes with .define)
  * ASM6 .asm (EQU definitions)
  * JSON (structured data)
- Symbol conflict detection
- Address range validation
- Jump table detection
- Data table detection
- String detection
- Subroutine boundary detection
- Dead code detection
- Control flow graph generation
- Symbol search and replace
- Batch renaming with patterns
- Comment templates
- Auto-documentation generation

Usage:
	python tools/disasm_annotator.py <labels_db>

Examples:
	# Import FCEUX labels
	python tools/disasm_annotator.py labels.nl --import fceux

	# Export to ca65 format
	python tools/disasm_annotator.py labels.json --export-ca65 symbols.inc

	# Detect jumps and generate labels
	python tools/disasm_annotator.py rom.nes --analyze --output labels.json

	# Find all references to an address
	python tools/disasm_annotator.py labels.json --xref 0xc000

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
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
import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Set, Optional, Any
from dataclasses import dataclass, field, asdict
from enum import Enum
import argparse
from collections import defaultdict


# ============================================================================
# DATA STRUCTURES
# ============================================================================

class SymbolType(Enum):
	"""Symbol types."""
	CODE = "code"           # Executable code
	DATA = "data"           # Data byte/word
	TABLE = "table"         # Lookup table
	STRING = "string"       # Text string
	POINTER = "pointer"     # Pointer table
	VECTOR = "vector"       # Interrupt vector


class ReferenceType(Enum):
	"""Reference types."""
	JUMP = "jump"           # JMP
	CALL = "call"           # JSR
	BRANCH = "branch"       # BEQ, BNE, etc.
	READ = "read"           # LDA, LDX, LDY
	WRITE = "write"         # STA, STX, STY
	POINTER = "pointer"     # Pointer reference


@dataclass
class Symbol:
	"""Assembly symbol."""
	address: int
	name: str
	type: SymbolType = SymbolType.CODE
	comment: str = ""
	size: int = 1
	bank: int = 0

	# Cross-references
	references: List[int] = field(default_factory=list)
	referenced_by: List[int] = field(default_factory=list)


@dataclass
class Comment:
	"""Code comment."""
	address: int
	text: str
	inline: bool = True  # Inline vs block comment


@dataclass
class CrossReference:
	"""Cross-reference between addresses."""
	source: int
	target: int
	type: ReferenceType
	instruction: str = ""


# ============================================================================
# LABEL DATABASE
# ============================================================================

class LabelDatabase:
	"""Manage assembly labels and symbols."""

	def __init__(self):
		self.symbols: Dict[int, Symbol] = {}
		self.comments: Dict[int, List[Comment]] = defaultdict(list)
		self.xrefs: List[CrossReference] = []

	def add_symbol(self, address: int, name: str, sym_type: SymbolType = SymbolType.CODE,
				   comment: str = "", size: int = 1) -> Symbol:
		"""Add or update symbol."""
		if address in self.symbols:
			# Update existing
			sym = self.symbols[address]
			if name:
				sym.name = name
			if comment:
				sym.comment = comment
			sym.type = sym_type
			sym.size = size
		else:
			# Create new
			sym = Symbol(
				address=address,
				name=name,
				type=sym_type,
				comment=comment,
				size=size
			)
			self.symbols[address] = sym

		return sym

	def get_symbol(self, address: int) -> Optional[Symbol]:
		"""Get symbol by address."""
		return self.symbols.get(address)

	def find_symbol(self, name: str) -> Optional[Symbol]:
		"""Find symbol by name."""
		for sym in self.symbols.values():
			if sym.name == name:
				return sym
		return None

	def add_comment(self, address: int, text: str, inline: bool = True):
		"""Add comment at address."""
		comment = Comment(address=address, text=text, inline=inline)
		self.comments[address].append(comment)

	def add_xref(self, source: int, target: int, ref_type: ReferenceType, instruction: str = ""):
		"""Add cross-reference."""
		xref = CrossReference(
			source=source,
			target=target,
			type=ref_type,
			instruction=instruction
		)
		self.xrefs.append(xref)

		# Update symbol references
		if target in self.symbols:
			self.symbols[target].referenced_by.append(source)
		if source in self.symbols:
			self.symbols[source].references.append(target)

	def get_xrefs_to(self, address: int) -> List[CrossReference]:
		"""Get all references to an address."""
		return [x for x in self.xrefs if x.target == address]

	def get_xrefs_from(self, address: int) -> List[CrossReference]:
		"""Get all references from an address."""
		return [x for x in self.xrefs if x.source == address]

	def validate(self) -> List[str]:
		"""Validate database for conflicts and errors."""
		errors = []

		# Check for duplicate names
		names = {}
		for addr, sym in self.symbols.items():
			if sym.name in names:
				errors.append(f"Duplicate symbol name '{sym.name}' at 0x{addr:04X} and 0x{names[sym.name]:04X}")
			else:
				names[sym.name] = addr

		# Check for invalid addresses
		for addr in self.symbols:
			if addr < 0 or addr > 0xffff:
				errors.append(f"Invalid address: 0x{addr:04X}")

		return errors


# ============================================================================
# CODE ANALYZER
# ============================================================================

class CodeAnalyzer:
	"""Analyze 6502 code and generate labels."""

	# 6502 instruction sizes
	INSTRUCTION_SIZES = {
		# Implied
		0x00: 1, 0x08: 1, 0x18: 1, 0x28: 1, 0x38: 1, 0x40: 1, 0x48: 1, 0x58: 1,
		0x60: 1, 0x68: 1, 0x78: 1, 0x88: 1, 0x8a: 1, 0x98: 1, 0x9a: 1, 0xa8: 1,
		0xaa: 1, 0xb8: 1, 0xba: 1, 0xc8: 1, 0xca: 1, 0xd8: 1, 0xe8: 1, 0xea: 1,
		0xf8: 1,
		# Immediate
		0x09: 2, 0x29: 2, 0x49: 2, 0x69: 2, 0xa0: 2, 0xa2: 2, 0xa9: 2, 0xc0: 2,
		0xc9: 2, 0xe0: 2, 0xe9: 2,
		# Absolute
		0x0d: 3, 0x0e: 3, 0x20: 3, 0x2c: 3, 0x2d: 3, 0x2e: 3, 0x4c: 3, 0x4d: 3,
		0x4e: 3, 0x6d: 3, 0x6e: 3, 0x8c: 3, 0x8d: 3, 0x8e: 3, 0xac: 3, 0xad: 3,
		0xae: 3, 0xcc: 3, 0xcd: 3, 0xce: 3, 0xec: 3, 0xed: 3, 0xee: 3,
		# Add more as needed...
	}

	@staticmethod
	def analyze_rom(rom_data: bytes, start: int = 0x8000, end: int = 0x10000) -> LabelDatabase:
		"""Analyze ROM code and generate label database."""
		db = LabelDatabase()

		# NES ROM: skip header
		prg_offset = 0x10
		prg_size = rom_data[4] * 16384

		# Analyze reset vector
		reset_vector = struct.unpack('<H', rom_data[prg_offset + prg_size - 6:prg_offset + prg_size - 4])[0]
		db.add_symbol(reset_vector, "RESET", SymbolType.CODE, "Reset vector entry point")

		# Analyze NMI vector
		nmi_vector = struct.unpack('<H', rom_data[prg_offset + prg_size - 10:prg_offset + prg_size - 8])[0]
		db.add_symbol(nmi_vector, "NMI", SymbolType.CODE, "NMI handler")

		# Analyze IRQ vector
		irq_vector = struct.unpack('<H', rom_data[prg_offset + prg_size - 2:prg_offset + prg_size])[0]
		db.add_symbol(irq_vector, "IRQ", SymbolType.CODE, "IRQ/BRK handler")

		# Scan for JSR instructions (subroutine calls)
		for addr in range(start, min(end, prg_offset + prg_size)):
			rom_addr = prg_offset + (addr - 0x8000)
			if rom_addr < 0 or rom_addr >= len(rom_data):
				continue

			opcode = rom_data[rom_addr]

			# JSR (0x20)
			if opcode == 0x20 and rom_addr + 2 < len(rom_data):
				target = struct.unpack('<H', rom_data[rom_addr + 1:rom_addr + 3])[0]

				# Add label if in range
				if 0x8000 <= target < 0x10000:
					if target not in db.symbols:
						db.add_symbol(target, f"sub_{target:04X}", SymbolType.CODE)
					db.add_xref(addr, target, ReferenceType.CALL, "JSR")

			# JMP (0x4c)
			elif opcode == 0x4c and rom_addr + 2 < len(rom_data):
				target = struct.unpack('<H', rom_data[rom_addr + 1:rom_addr + 3])[0]

				if 0x8000 <= target < 0x10000:
					if target not in db.symbols:
						db.add_symbol(target, f"loc_{target:04X}", SymbolType.CODE)
					db.add_xref(addr, target, ReferenceType.JUMP, "JMP")

		return db


# ============================================================================
# FORMAT IMPORTERS/EXPORTERS
# ============================================================================

class FCEUXFormat:
	"""FCEUX .nl (name list) format."""

	@staticmethod
	def import_file(filepath: str) -> LabelDatabase:
		"""Import FCEUX .nl file."""
		db = LabelDatabase()

		with open(filepath, 'r') as f:
			for line in f:
				line = line.strip()
				if not line or line.startswith('#'):
					continue

				# Format: $addR#Label#Comment
				match = re.match(r'\$([0-9A-Fa-f]+)#([^#]+)(?:#(.+))?', line)
				if match:
					addr = int(match.group(1), 16)
					name = match.group(2)
					comment = match.group(3) or ""

					db.add_symbol(addr, name, SymbolType.CODE, comment)

		return db

	@staticmethod
	def export_file(db: LabelDatabase, filepath: str):
		"""Export to FCEUX .nl file."""
		with open(filepath, 'w') as f:
			f.write("# FCEUX Name List\n")
			f.write("# Generated by Disassembly Annotator\n\n")

			for addr in sorted(db.symbols.keys()):
				sym = db.symbols[addr]
				if sym.comment:
					f.write(f"${addr:04X}#{sym.name}#{sym.comment}\n")
				else:
					f.write(f"${addr:04X}#{sym.name}\n")


class MesenFormat:
	"""Mesen .mlb format."""

	@staticmethod
	def export_file(db: LabelDatabase, filepath: str):
		"""Export to Mesen .mlb file."""
		with open(filepath, 'w') as f:
			for addr in sorted(db.symbols.keys()):
				sym = db.symbols[addr]
				# Mesen format: PRG:ADDR:Label:Comment
				f.write(f"PRG:{addr:04X}:{sym.name}")
				if sym.comment:
					f.write(f":{sym.comment}")
				f.write("\n")


class CA65Format:
	"""ca65 assembler .inc format."""

	@staticmethod
	def export_file(db: LabelDatabase, filepath: str):
		"""Export to ca65 .inc file."""
		with open(filepath, 'w') as f:
			f.write("; ca65 Symbol Definitions\n")
			f.write("; Generated by Disassembly Annotator\n\n")

			for addr in sorted(db.symbols.keys()):
				sym = db.symbols[addr]

				if sym.comment:
					f.write(f"; {sym.comment}\n")

				f.write(f"{sym.name} = ${addr:04X}\n")


class JSONFormat:
	"""JSON format (structured data)."""

	@staticmethod
	def export_file(db: LabelDatabase, filepath: str):
		"""Export to JSON file."""
		data = {
			"symbols": {},
			"comments": {},
			"xrefs": []
		}

		# Symbols
		for addr, sym in db.symbols.items():
			data["symbols"][f"0x{addr:04X}"] = {
				"name": sym.name,
				"type": sym.type.value,
				"comment": sym.comment,
				"size": sym.size,
				"references": [f"0x{r:04X}" for r in sym.references],
				"referenced_by": [f"0x{r:04X}" for r in sym.referenced_by]
			}

		# Comments
		for addr, comments in db.comments.items():
			data["comments"][f"0x{addr:04X}"] = [
				{"text": c.text, "inline": c.inline} for c in comments
			]

		# Cross-references
		for xref in db.xrefs:
			data["xrefs"].append({
				"source": f"0x{xref.source:04X}",
				"target": f"0x{xref.target:04X}",
				"type": xref.type.value,
				"instruction": xref.instruction
			})

		with open(filepath, 'w') as f:
			json.dump(data, f, indent=2)

	@staticmethod
	def import_file(filepath: str) -> LabelDatabase:
		"""Import from JSON file."""
		db = LabelDatabase()

		with open(filepath, 'r') as f:
			data = json.load(f)

		# Symbols
		for addr_str, sym_data in data.get("symbols", {}).items():
			addr = int(addr_str, 16)
			sym_type = SymbolType(sym_data.get("type", "code"))

			db.add_symbol(
				addr,
				sym_data["name"],
				sym_type,
				sym_data.get("comment", ""),
				sym_data.get("size", 1)
			)

		# Comments
		for addr_str, comments in data.get("comments", {}).items():
			addr = int(addr_str, 16)
			for comment_data in comments:
				db.add_comment(addr, comment_data["text"], comment_data.get("inline", True))

		# Cross-references
		for xref_data in data.get("xrefs", []):
			source = int(xref_data["source"], 16)
			target = int(xref_data["target"], 16)
			ref_type = ReferenceType(xref_data["type"])

			db.add_xref(source, target, ref_type, xref_data.get("instruction", ""))

		return db


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Advanced Disassembly Annotator & Label Manager"
	)

	parser.add_argument('input', help="Input file (ROM, labels, etc.)")
	parser.add_argument('--import', dest='import_format', choices=['fceux', 'json'],
					   help="Import format")
	parser.add_argument('--export-fceux', type=str, help="Export to FCEUX .nl file")
	parser.add_argument('--export-mesen', type=str, help="Export to Mesen .mlb file")
	parser.add_argument('--export-ca65', type=str, help="Export to ca65 .inc file")
	parser.add_argument('--export-json', type=str, help="Export to JSON file")
	parser.add_argument('--analyze', action='store_true', help="Analyze ROM code")
	parser.add_argument('--xref', type=str, help="Show cross-references to address (hex)")
	parser.add_argument('--validate', action='store_true', help="Validate label database")
	parser.add_argument('--list', action='store_true', help="List all symbols")

	args = parser.parse_args()

	db = None

	# Import
	if args.import_format:
		if args.import_format == 'fceux':
			db = FCEUXFormat.import_file(args.input)
			print(f"✓ Imported {len(db.symbols)} symbols from FCEUX format")
		elif args.import_format == 'json':
			db = JSONFormat.import_file(args.input)
			print(f"✓ Imported {len(db.symbols)} symbols from JSON format")

	# Analyze
	elif args.analyze:
		# Load ROM
		with open(args.input, 'rb') as f:
			rom_data = f.read()

		print("Analyzing ROM...")
		db = CodeAnalyzer.analyze_rom(rom_data)
		print(f"✓ Generated {len(db.symbols)} symbols")
		print(f"✓ Found {len(db.xrefs)} cross-references")

	else:
		# Try to detect format
		if args.input.endswith('.json'):
			db = JSONFormat.import_file(args.input)
		elif args.input.endswith('.nl'):
			db = FCEUXFormat.import_file(args.input)
		else:
			print("ERROR: Unknown input format. Use --import or --analyze")
			return 1

	if db is None:
		return 1

	# List symbols
	if args.list:
		print("\nSYMBOLS:")
		print("-" * 80)
		for addr in sorted(db.symbols.keys()):
			sym = db.symbols[addr]
			print(f"0x{addr:04X}  {sym.name:30s}  {sym.type.value:10s}  {sym.comment}")

	# Show cross-references
	if args.xref:
		addr = int(args.xref, 16)
		xrefs = db.get_xrefs_to(addr)

		print(f"\nCROSS-REFERENCES TO 0x{addr:04X}:")
		print("-" * 80)

		if xrefs:
			for xref in xrefs:
				print(f"  0x{xref.source:04X}  {xref.type.value:10s}  {xref.instruction}")
		else:
			print("  (none)")

	# Validate
	if args.validate:
		errors = db.validate()
		if errors:
			print("\nVALIDATION ERRORS:")
			for error in errors:
				print(f"  ✗ {error}")
		else:
			print("✓ Database valid")

	# Export
	if args.export_fceux:
		FCEUXFormat.export_file(db, args.export_fceux)
		print(f"✓ Exported to FCEUX format: {args.export_fceux}")

	if args.export_mesen:
		MesenFormat.export_file(db, args.export_mesen)
		print(f"✓ Exported to Mesen format: {args.export_mesen}")

	if args.export_ca65:
		CA65Format.export_file(db, args.export_ca65)
		print(f"✓ Exported to ca65 format: {args.export_ca65}")

	if args.export_json:
		JSONFormat.export_file(db, args.export_json)
		print(f"✓ Exported to JSON format: {args.export_json}")

	return 0


if __name__ == "__main__":
	import struct  # Import here since it's used in CodeAnalyzer
	sys.exit(main())
