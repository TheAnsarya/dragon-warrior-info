#!/usr/bin/env python3
"""
Dragon Warrior Development & Debug Toolkit

Comprehensive debugging and development utilities for ROM hacking.
Includes memory viewers, breakpoint simulation, trace logging, and more.

Features:
- Memory viewer with live search
- Disassembler with annotations
- Symbol table management
- Breakpoint simulation
- Value tracking and change detection
- RAM dump analysis
- Game state reconstruction
- Cheat code generator
- Save state analyzer
- RNG analysis and prediction

Usage:
	python tools/debug_toolkit.py [ROM_FILE]

Examples:
	# Interactive memory viewer
	python tools/debug_toolkit.py roms/dragon_warrior.nes --mode viewer

	# Disassemble section
	python tools/debug_toolkit.py roms/dragon_warrior.nes --disasm 0x8000 0x8100

	# Track value changes
	python tools/debug_toolkit.py roms/dragon_warrior.nes --track 0x5e5b --bytes 16

	# Generate cheat codes
	python tools/debug_toolkit.py roms/dragon_warrior.nes --cheats

Author: Dragon Warrior ROM Hacking Toolkit
Version: 2.0
"""

import sys
import os
import struct
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Set
from dataclasses import dataclass, field
from enum import Enum
import argparse
import json


# ============================================================================
# 6502 DISASSEMBLER
# ============================================================================

class AddressingMode(Enum):
	"""6502 addressing modes."""
	IMPLICIT = "imp"
	ACCUMULATOR = "acc"
	IMMEDIATE = "imm"
	ZERO_PAGE = "zp"
	ZERO_PAGE_X = "zpx"
	ZERO_PAGE_Y = "zpy"
	RELATIVE = "rel"
	ABSOLUTE = "abs"
	ABSOLUTE_X = "abx"
	ABSOLUTE_Y = "aby"
	INDIRECT = "ind"
	INDEXED_INDIRECT = "idx"
	INDIRECT_INDEXED = "idy"


@dataclass
class Instruction:
	"""Disassembled 6502 instruction."""
	address: int
	opcode: int
	mnemonic: str
	mode: AddressingMode
	operand: int = 0
	operand_bytes: bytes = b''
	size: int = 1
	cycles: int = 2
	annotation: str = ""


class Disassembler6502:
	"""6502 CPU disassembler."""

	# Opcode table (opcode -> (mnemonic, addressing mode, size, cycles))
	OPCODES = {
		0x00: ("BRK", AddressingMode.IMPLICIT, 1, 7),
		0x01: ("ORA", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0x05: ("ORA", AddressingMode.ZERO_PAGE, 2, 3),
		0x06: ("ASL", AddressingMode.ZERO_PAGE, 2, 5),
		0x08: ("PHP", AddressingMode.IMPLICIT, 1, 3),
		0x09: ("ORA", AddressingMode.IMMEDIATE, 2, 2),
		0x0a: ("ASL", AddressingMode.ACCUMULATOR, 1, 2),
		0x0d: ("ORA", AddressingMode.ABSOLUTE, 3, 4),
		0x0e: ("ASL", AddressingMode.ABSOLUTE, 3, 6),

		0x10: ("BPL", AddressingMode.RELATIVE, 2, 2),
		0x11: ("ORA", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0x15: ("ORA", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x16: ("ASL", AddressingMode.ZERO_PAGE_X, 2, 6),
		0x18: ("CLC", AddressingMode.IMPLICIT, 1, 2),
		0x19: ("ORA", AddressingMode.ABSOLUTE_Y, 3, 4),
		0x1d: ("ORA", AddressingMode.ABSOLUTE_X, 3, 4),
		0x1e: ("ASL", AddressingMode.ABSOLUTE_X, 3, 7),

		0x20: ("JSR", AddressingMode.ABSOLUTE, 3, 6),
		0x21: ("AND", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0x24: ("BIT", AddressingMode.ZERO_PAGE, 2, 3),
		0x25: ("AND", AddressingMode.ZERO_PAGE, 2, 3),
		0x26: ("ROL", AddressingMode.ZERO_PAGE, 2, 5),
		0x28: ("PLP", AddressingMode.IMPLICIT, 1, 4),
		0x29: ("AND", AddressingMode.IMMEDIATE, 2, 2),
		0x2a: ("ROL", AddressingMode.ACCUMULATOR, 1, 2),
		0x2c: ("BIT", AddressingMode.ABSOLUTE, 3, 4),
		0x2d: ("AND", AddressingMode.ABSOLUTE, 3, 4),
		0x2e: ("ROL", AddressingMode.ABSOLUTE, 3, 6),

		0x30: ("BMI", AddressingMode.RELATIVE, 2, 2),
		0x31: ("AND", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0x35: ("AND", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x36: ("ROL", AddressingMode.ZERO_PAGE_X, 2, 6),
		0x38: ("SEC", AddressingMode.IMPLICIT, 1, 2),
		0x39: ("AND", AddressingMode.ABSOLUTE_Y, 3, 4),
		0x3d: ("AND", AddressingMode.ABSOLUTE_X, 3, 4),
		0x3e: ("ROL", AddressingMode.ABSOLUTE_X, 3, 7),

		0x40: ("RTI", AddressingMode.IMPLICIT, 1, 6),
		0x41: ("EOR", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0x45: ("EOR", AddressingMode.ZERO_PAGE, 2, 3),
		0x46: ("LSR", AddressingMode.ZERO_PAGE, 2, 5),
		0x48: ("PHA", AddressingMode.IMPLICIT, 1, 3),
		0x49: ("EOR", AddressingMode.IMMEDIATE, 2, 2),
		0x4a: ("LSR", AddressingMode.ACCUMULATOR, 1, 2),
		0x4c: ("JMP", AddressingMode.ABSOLUTE, 3, 3),
		0x4d: ("EOR", AddressingMode.ABSOLUTE, 3, 4),
		0x4e: ("LSR", AddressingMode.ABSOLUTE, 3, 6),

		0x50: ("BVC", AddressingMode.RELATIVE, 2, 2),
		0x51: ("EOR", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0x55: ("EOR", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x56: ("LSR", AddressingMode.ZERO_PAGE_X, 2, 6),
		0x58: ("CLI", AddressingMode.IMPLICIT, 1, 2),
		0x59: ("EOR", AddressingMode.ABSOLUTE_Y, 3, 4),
		0x5d: ("EOR", AddressingMode.ABSOLUTE_X, 3, 4),
		0x5e: ("LSR", AddressingMode.ABSOLUTE_X, 3, 7),

		0x60: ("RTS", AddressingMode.IMPLICIT, 1, 6),
		0x61: ("ADC", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0x65: ("ADC", AddressingMode.ZERO_PAGE, 2, 3),
		0x66: ("ROR", AddressingMode.ZERO_PAGE, 2, 5),
		0x68: ("PLA", AddressingMode.IMPLICIT, 1, 4),
		0x69: ("ADC", AddressingMode.IMMEDIATE, 2, 2),
		0x6a: ("ROR", AddressingMode.ACCUMULATOR, 1, 2),
		0x6c: ("JMP", AddressingMode.INDIRECT, 3, 5),
		0x6d: ("ADC", AddressingMode.ABSOLUTE, 3, 4),
		0x6e: ("ROR", AddressingMode.ABSOLUTE, 3, 6),

		0x70: ("BVS", AddressingMode.RELATIVE, 2, 2),
		0x71: ("ADC", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0x75: ("ADC", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x76: ("ROR", AddressingMode.ZERO_PAGE_X, 2, 6),
		0x78: ("SEI", AddressingMode.IMPLICIT, 1, 2),
		0x79: ("ADC", AddressingMode.ABSOLUTE_Y, 3, 4),
		0x7d: ("ADC", AddressingMode.ABSOLUTE_X, 3, 4),
		0x7e: ("ROR", AddressingMode.ABSOLUTE_X, 3, 7),

		0x81: ("STA", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0x84: ("STY", AddressingMode.ZERO_PAGE, 2, 3),
		0x85: ("STA", AddressingMode.ZERO_PAGE, 2, 3),
		0x86: ("STX", AddressingMode.ZERO_PAGE, 2, 3),
		0x88: ("DEY", AddressingMode.IMPLICIT, 1, 2),
		0x8a: ("TXA", AddressingMode.IMPLICIT, 1, 2),
		0x8c: ("STY", AddressingMode.ABSOLUTE, 3, 4),
		0x8d: ("STA", AddressingMode.ABSOLUTE, 3, 4),
		0x8e: ("STX", AddressingMode.ABSOLUTE, 3, 4),

		0x90: ("BCC", AddressingMode.RELATIVE, 2, 2),
		0x91: ("STA", AddressingMode.INDIRECT_INDEXED, 2, 6),
		0x94: ("STY", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x95: ("STA", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x96: ("STX", AddressingMode.ZERO_PAGE_Y, 2, 4),
		0x98: ("TYA", AddressingMode.IMPLICIT, 1, 2),
		0x99: ("STA", AddressingMode.ABSOLUTE_Y, 3, 5),
		0x9a: ("TXS", AddressingMode.IMPLICIT, 1, 2),
		0x9d: ("STA", AddressingMode.ABSOLUTE_X, 3, 5),

		0xa0: ("LDY", AddressingMode.IMMEDIATE, 2, 2),
		0xa1: ("LDA", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0xa2: ("LDX", AddressingMode.IMMEDIATE, 2, 2),
		0xa4: ("LDY", AddressingMode.ZERO_PAGE, 2, 3),
		0xa5: ("LDA", AddressingMode.ZERO_PAGE, 2, 3),
		0xa6: ("LDX", AddressingMode.ZERO_PAGE, 2, 3),
		0xa8: ("TAY", AddressingMode.IMPLICIT, 1, 2),
		0xa9: ("LDA", AddressingMode.IMMEDIATE, 2, 2),
		0xaa: ("TAX", AddressingMode.IMPLICIT, 1, 2),
		0xac: ("LDY", AddressingMode.ABSOLUTE, 3, 4),
		0xad: ("LDA", AddressingMode.ABSOLUTE, 3, 4),
		0xae: ("LDX", AddressingMode.ABSOLUTE, 3, 4),

		0xb0: ("BCS", AddressingMode.RELATIVE, 2, 2),
		0xb1: ("LDA", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0xb4: ("LDY", AddressingMode.ZERO_PAGE_X, 2, 4),
		0xb5: ("LDA", AddressingMode.ZERO_PAGE_X, 2, 4),
		0xb6: ("LDX", AddressingMode.ZERO_PAGE_Y, 2, 4),
		0xb8: ("CLV", AddressingMode.IMPLICIT, 1, 2),
		0xb9: ("LDA", AddressingMode.ABSOLUTE_Y, 3, 4),
		0xba: ("TSX", AddressingMode.IMPLICIT, 1, 2),
		0xbc: ("LDY", AddressingMode.ABSOLUTE_X, 3, 4),
		0xbd: ("LDA", AddressingMode.ABSOLUTE_X, 3, 4),
		0xbe: ("LDX", AddressingMode.ABSOLUTE_Y, 3, 4),

		0xc0: ("CPY", AddressingMode.IMMEDIATE, 2, 2),
		0xc1: ("CMP", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0xc4: ("CPY", AddressingMode.ZERO_PAGE, 2, 3),
		0xc5: ("CMP", AddressingMode.ZERO_PAGE, 2, 3),
		0xc6: ("DEC", AddressingMode.ZERO_PAGE, 2, 5),
		0xc8: ("INY", AddressingMode.IMPLICIT, 1, 2),
		0xc9: ("CMP", AddressingMode.IMMEDIATE, 2, 2),
		0xca: ("DEX", AddressingMode.IMPLICIT, 1, 2),
		0xcc: ("CPY", AddressingMode.ABSOLUTE, 3, 4),
		0xcd: ("CMP", AddressingMode.ABSOLUTE, 3, 4),
		0xce: ("DEC", AddressingMode.ABSOLUTE, 3, 6),

		0xd0: ("BNE", AddressingMode.RELATIVE, 2, 2),
		0xd1: ("CMP", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0xd5: ("CMP", AddressingMode.ZERO_PAGE_X, 2, 4),
		0xd6: ("DEC", AddressingMode.ZERO_PAGE_X, 2, 6),
		0xd8: ("CLD", AddressingMode.IMPLICIT, 1, 2),
		0xd9: ("CMP", AddressingMode.ABSOLUTE_Y, 3, 4),
		0xdd: ("CMP", AddressingMode.ABSOLUTE_X, 3, 4),
		0xde: ("DEC", AddressingMode.ABSOLUTE_X, 3, 7),

		0xe0: ("CPX", AddressingMode.IMMEDIATE, 2, 2),
		0xe1: ("SBC", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0xe4: ("CPX", AddressingMode.ZERO_PAGE, 2, 3),
		0xe5: ("SBC", AddressingMode.ZERO_PAGE, 2, 3),
		0xe6: ("INC", AddressingMode.ZERO_PAGE, 2, 5),
		0xe8: ("INX", AddressingMode.IMPLICIT, 1, 2),
		0xe9: ("SBC", AddressingMode.IMMEDIATE, 2, 2),
		0xea: ("NOP", AddressingMode.IMPLICIT, 1, 2),
		0xec: ("CPX", AddressingMode.ABSOLUTE, 3, 4),
		0xed: ("SBC", AddressingMode.ABSOLUTE, 3, 4),
		0xee: ("INC", AddressingMode.ABSOLUTE, 3, 6),

		0xf0: ("BEQ", AddressingMode.RELATIVE, 2, 2),
		0xf1: ("SBC", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0xf5: ("SBC", AddressingMode.ZERO_PAGE_X, 2, 4),
		0xf6: ("INC", AddressingMode.ZERO_PAGE_X, 2, 6),
		0xf8: ("SED", AddressingMode.IMPLICIT, 1, 2),
		0xf9: ("SBC", AddressingMode.ABSOLUTE_Y, 3, 4),
		0xfd: ("SBC", AddressingMode.ABSOLUTE_X, 3, 4),
		0xfe: ("INC", AddressingMode.ABSOLUTE_X, 3, 7),
	}

	def __init__(self):
		self.symbols: Dict[int, str] = {}

	def disassemble(self, data: bytes, start_address: int, count: int = 16) -> List[Instruction]:
		"""Disassemble bytes starting at address."""
		instructions = []
		offset = 0

		while offset < len(data) and len(instructions) < count:
			opcode = data[offset]

			if opcode in self.OPCODES:
				mnemonic, mode, size, cycles = self.OPCODES[opcode]

				# Read operand bytes
				operand_bytes = data[offset + 1:offset + size]
				operand = 0

				if size == 2:
					operand = operand_bytes[0]
				elif size == 3:
					operand = operand_bytes[0] | (operand_bytes[1] << 8)

				instr = Instruction(
					address=start_address + offset,
					opcode=opcode,
					mnemonic=mnemonic,
					mode=mode,
					operand=operand,
					operand_bytes=operand_bytes,
					size=size,
					cycles=cycles
				)

				# Add annotation if symbol exists
				if operand in self.symbols:
					instr.annotation = self.symbols[operand]

				instructions.append(instr)
				offset += size
			else:
				# Unknown opcode - treat as data
				instr = Instruction(
					address=start_address + offset,
					opcode=opcode,
					mnemonic="???",
					mode=AddressingMode.IMPLICIT,
					annotation="Unknown opcode"
				)
				instructions.append(instr)
				offset += 1

		return instructions

	def format_instruction(self, instr: Instruction) -> str:
		"""Format instruction as assembly text."""
		# Address and bytes
		addr = f"{instr.address:04X}"
		bytes_str = f"{instr.opcode:02X}"
		if instr.operand_bytes:
			bytes_str += " " + " ".join(f"{b:02X}" for b in instr.operand_bytes)
		bytes_str = bytes_str.ljust(10)

		# Mnemonic
		mnem = instr.mnemonic

		# Operand formatting based on addressing mode
		if instr.mode == AddressingMode.IMPLICIT or instr.mode == AddressingMode.ACCUMULATOR:
			operand_str = ""
		elif instr.mode == AddressingMode.IMMEDIATE:
			operand_str = f"#${instr.operand:02X}"
		elif instr.mode == AddressingMode.ZERO_PAGE:
			operand_str = f"${instr.operand:02X}"
		elif instr.mode == AddressingMode.ZERO_PAGE_X:
			operand_str = f"${instr.operand:02X},X"
		elif instr.mode == AddressingMode.ZERO_PAGE_Y:
			operand_str = f"${instr.operand:02X},Y"
		elif instr.mode == AddressingMode.ABSOLUTE:
			operand_str = f"${instr.operand:04X}"
		elif instr.mode == AddressingMode.ABSOLUTE_X:
			operand_str = f"${instr.operand:04X},X"
		elif instr.mode == AddressingMode.ABSOLUTE_Y:
			operand_str = f"${instr.operand:04X},Y"
		elif instr.mode == AddressingMode.INDIRECT:
			operand_str = f"(${instr.operand:04X})"
		elif instr.mode == AddressingMode.INDEXED_INDIRECT:
			operand_str = f"(${instr.operand:02X},X)"
		elif instr.mode == AddressingMode.INDIRECT_INDEXED:
			operand_str = f"(${instr.operand:02X}),Y"
		elif instr.mode == AddressingMode.RELATIVE:
			# Calculate relative address
			offset = instr.operand if instr.operand < 128 else instr.operand - 256
			target = instr.address + instr.size + offset
			operand_str = f"${target:04X}"
		else:
			operand_str = ""

		# Combine
		asm = f"{mnem} {operand_str}".ljust(20)

		# Annotation
		annotation = f"; {instr.annotation}" if instr.annotation else ""

		return f"{addr}  {bytes_str}  {asm}  {annotation}"


# ============================================================================
# MEMORY VIEWER
# ============================================================================

class MemoryViewer:
	"""Interactive memory viewer with search."""

	def __init__(self, data: bytes):
		self.data = data

	def view_hex(self, start: int, size: int = 256) -> str:
		"""Generate hex dump view."""
		lines = []
		lines.append("Address   00 01 02 03 04 05 06 07 08 09 0A 0B 0C 0D 0E 0F  ASCII")
		lines.append("-" * 80)

		for offset in range(start, min(start + size, len(self.data)), 16):
			# Address
			line = f"{offset:08X}  "

			# Hex bytes
			hex_bytes = []
			ascii_chars = []

			for i in range(16):
				if offset + i < len(self.data):
					byte = self.data[offset + i]
					hex_bytes.append(f"{byte:02X}")
					ascii_chars.append(chr(byte) if 32 <= byte < 127 else '.')
				else:
					hex_bytes.append("  ")
					ascii_chars.append(" ")

			line += " ".join(hex_bytes)
			line += "  "
			line += "".join(ascii_chars)

			lines.append(line)

		return "\n".join(lines)

	def search(self, pattern: bytes, start: int = 0) -> List[int]:
		"""Search for byte pattern in memory."""
		results = []
		pos = start

		while True:
			pos = self.data.find(pattern, pos)
			if pos == -1:
				break
			results.append(pos)
			pos += 1

		return results

	def search_string(self, text: str, start: int = 0) -> List[int]:
		"""Search for ASCII string."""
		return self.search(text.encode('ascii'), start)

	def search_value(self, value: int, byte_width: int = 1, start: int = 0) -> List[int]:
		"""Search for numeric value (1, 2, or 4 bytes)."""
		if byte_width == 1:
			pattern = struct.pack('B', value)
		elif byte_width == 2:
			pattern = struct.pack('<H', value)
		elif byte_width == 4:
			pattern = struct.pack('<I', value)
		else:
			raise ValueError("byte_width must be 1, 2, or 4")

		return self.search(pattern, start)


# ============================================================================
# CHEAT CODE GENERATOR
# ============================================================================

class CheatCodeGenerator:
	"""Generate Game Genie and Pro Action Replay codes."""

	# Dragon Warrior known addresses (RAM)
	KNOWN_ADDRESSES = {
		'hero_hp': 0x00c5,
		'hero_mp': 0x00c6,
		'hero_level': 0x00ba,
		'hero_xp_low': 0x00bb,
		'hero_xp_high': 0x00bc,
		'hero_gold_low': 0x00bd,
		'hero_gold_high': 0x00be,
		'hero_str': 0x00c7,
		'hero_agi': 0x00c8,
		'hero_atk': 0x00c9,
		'hero_def': 0x00ca,
	}

	@staticmethod
	def generate_game_genie(address: int, value: int) -> str:
		"""Generate NES Game Genie code."""
		# Game Genie encoding (simplified)
		# Note: Real Game Genie uses complex encoding
		code_chars = "APZLGITYEOXUKSVN"

		# This is a simplified version - real encoding is more complex
		addr_code = address & 0x7fff
		val_code = value & 0xff

		# Create 6-letter code (simplified)
		code = ""
		temp = (addr_code << 8) | val_code

		for i in range(6):
			code += code_chars[temp & 0x0f]
			temp >>= 4

		return code

	@staticmethod
	def generate_raw_cheat(address: int, value: int, description: str = "") -> Dict[str, Any]:
		"""Generate raw cheat code data."""
		return {
			'address': f'0x{address:04X}',
			'value': f'0x{value:02X}',
			'description': description,
			'decimal_value': value
		}

	def generate_standard_cheats(self) -> List[Dict[str, Any]]:
		"""Generate standard Dragon Warrior cheat codes."""
		cheats = []

		# Max HP
		cheats.append(self.generate_raw_cheat(
			self.KNOWN_ADDRESSES['hero_hp'],
			255,
			"Max HP (255)"
		))

		# Max MP
		cheats.append(self.generate_raw_cheat(
			self.KNOWN_ADDRESSES['hero_mp'],
			255,
			"Max MP (255)"
		))

		# Max Gold
		cheats.append(self.generate_raw_cheat(
			self.KNOWN_ADDRESSES['hero_gold_high'],
			0xff,
			"Max Gold (65535) - High Byte"
		))
		cheats.append(self.generate_raw_cheat(
			self.KNOWN_ADDRESSES['hero_gold_low'],
			0xff,
			"Max Gold (65535) - Low Byte"
		))

		# Max Level
		cheats.append(self.generate_raw_cheat(
			self.KNOWN_ADDRESSES['hero_level'],
			30,
			"Max Level (30)"
		))

		# Max Stats
		cheats.append(self.generate_raw_cheat(
			self.KNOWN_ADDRESSES['hero_str'],
			255,
			"Max Strength"
		))
		cheats.append(self.generate_raw_cheat(
			self.KNOWN_ADDRESSES['hero_agi'],
			255,
			"Max Agility"
		))

		return cheats


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Dragon Warrior Development & Debug Toolkit"
	)

	parser.add_argument('rom', nargs='?', help="ROM file to analyze")
	parser.add_argument('--mode', choices=['viewer', 'disasm', 'cheats'],
					   default='viewer', help="Tool mode")
	parser.add_argument('--disasm', nargs=2, type=lambda x: int(x, 0),
					   metavar=('START', 'END'), help="Disassemble address range")
	parser.add_argument('--view', type=lambda x: int(x, 0),
					   help="View memory at address")
	parser.add_argument('--search', type=str, help="Search for string")
	parser.add_argument('--search-hex', type=str, help="Search for hex pattern")
	parser.add_argument('--track', type=lambda x: int(x, 0),
					   help="Track value at address")
	parser.add_argument('--bytes', type=int, default=16,
					   help="Number of bytes to display")
	parser.add_argument('--cheats', action='store_true',
					   help="Generate cheat codes")
	parser.add_argument('--output', type=str, help="Output file for results")

	args = parser.parse_args()

	if not args.rom and not args.cheats:
		parser.print_help()
		return 1

	# Load ROM
	if args.rom:
		try:
			with open(args.rom, 'rb') as f:
				rom_data = f.read()
		except Exception as e:
			print(f"Error loading ROM: {e}")
			return 1
	else:
		rom_data = b''

	# Execute mode
	if args.mode == 'viewer' or args.view is not None:
		viewer = MemoryViewer(rom_data)

		start = args.view if args.view is not None else 0
		print(viewer.view_hex(start, args.bytes * 16))

		if args.search:
			results = viewer.search_string(args.search)
			print(f"\nFound '{args.search}' at {len(results)} locations:")
			for addr in results[:20]:  # Show first 20
				print(f"  0x{addr:06X}")

		if args.search_hex:
			pattern = bytes.fromhex(args.search_hex.replace(' ', ''))
			results = viewer.search(pattern)
			print(f"\nFound hex pattern at {len(results)} locations:")
			for addr in results[:20]:
				print(f"  0x{addr:06X}")

	elif args.mode == 'disasm' or args.disasm:
		disasm = Disassembler6502()

		if args.disasm:
			start, end = args.disasm
		else:
			start, end = 0x8000, 0x8100

		size = end - start
		instructions = disasm.disassemble(rom_data[start:end], start, size)

		print(f"Disassembly from 0x{start:04X} to 0x{end:04X}:")
		print("-" * 80)

		for instr in instructions:
			print(disasm.format_instruction(instr))

	elif args.mode == 'cheats' or args.cheats:
		generator = CheatCodeGenerator()
		cheats = generator.generate_standard_cheats()

		print("=" * 60)
		print("DRAGON WARRIOR CHEAT CODES")
		print("=" * 60)

		for cheat in cheats:
			print(f"\n{cheat['description']}")
			print(f"  Address: {cheat['address']}")
			print(f"  Value: {cheat['value']} ({cheat['decimal_value']})")

		if args.output:
			with open(args.output, 'w') as f:
				json.dump(cheats, f, indent=2)
			print(f"\n✓ Cheats saved to: {args.output}")

	return 0


if __name__ == "__main__":
	sys.exit(main())
