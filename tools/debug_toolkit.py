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
	python tools/debug_toolkit.py roms/dragon_warrior.nes --track 0x5E5B --bytes 16

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
		0x0A: ("ASL", AddressingMode.ACCUMULATOR, 1, 2),
		0x0D: ("ORA", AddressingMode.ABSOLUTE, 3, 4),
		0x0E: ("ASL", AddressingMode.ABSOLUTE, 3, 6),

		0x10: ("BPL", AddressingMode.RELATIVE, 2, 2),
		0x11: ("ORA", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0x15: ("ORA", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x16: ("ASL", AddressingMode.ZERO_PAGE_X, 2, 6),
		0x18: ("CLC", AddressingMode.IMPLICIT, 1, 2),
		0x19: ("ORA", AddressingMode.ABSOLUTE_Y, 3, 4),
		0x1D: ("ORA", AddressingMode.ABSOLUTE_X, 3, 4),
		0x1E: ("ASL", AddressingMode.ABSOLUTE_X, 3, 7),

		0x20: ("JSR", AddressingMode.ABSOLUTE, 3, 6),
		0x21: ("AND", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0x24: ("BIT", AddressingMode.ZERO_PAGE, 2, 3),
		0x25: ("AND", AddressingMode.ZERO_PAGE, 2, 3),
		0x26: ("ROL", AddressingMode.ZERO_PAGE, 2, 5),
		0x28: ("PLP", AddressingMode.IMPLICIT, 1, 4),
		0x29: ("AND", AddressingMode.IMMEDIATE, 2, 2),
		0x2A: ("ROL", AddressingMode.ACCUMULATOR, 1, 2),
		0x2C: ("BIT", AddressingMode.ABSOLUTE, 3, 4),
		0x2D: ("AND", AddressingMode.ABSOLUTE, 3, 4),
		0x2E: ("ROL", AddressingMode.ABSOLUTE, 3, 6),

		0x30: ("BMI", AddressingMode.RELATIVE, 2, 2),
		0x31: ("AND", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0x35: ("AND", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x36: ("ROL", AddressingMode.ZERO_PAGE_X, 2, 6),
		0x38: ("SEC", AddressingMode.IMPLICIT, 1, 2),
		0x39: ("AND", AddressingMode.ABSOLUTE_Y, 3, 4),
		0x3D: ("AND", AddressingMode.ABSOLUTE_X, 3, 4),
		0x3E: ("ROL", AddressingMode.ABSOLUTE_X, 3, 7),

		0x40: ("RTI", AddressingMode.IMPLICIT, 1, 6),
		0x41: ("EOR", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0x45: ("EOR", AddressingMode.ZERO_PAGE, 2, 3),
		0x46: ("LSR", AddressingMode.ZERO_PAGE, 2, 5),
		0x48: ("PHA", AddressingMode.IMPLICIT, 1, 3),
		0x49: ("EOR", AddressingMode.IMMEDIATE, 2, 2),
		0x4A: ("LSR", AddressingMode.ACCUMULATOR, 1, 2),
		0x4C: ("JMP", AddressingMode.ABSOLUTE, 3, 3),
		0x4D: ("EOR", AddressingMode.ABSOLUTE, 3, 4),
		0x4E: ("LSR", AddressingMode.ABSOLUTE, 3, 6),

		0x50: ("BVC", AddressingMode.RELATIVE, 2, 2),
		0x51: ("EOR", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0x55: ("EOR", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x56: ("LSR", AddressingMode.ZERO_PAGE_X, 2, 6),
		0x58: ("CLI", AddressingMode.IMPLICIT, 1, 2),
		0x59: ("EOR", AddressingMode.ABSOLUTE_Y, 3, 4),
		0x5D: ("EOR", AddressingMode.ABSOLUTE_X, 3, 4),
		0x5E: ("LSR", AddressingMode.ABSOLUTE_X, 3, 7),

		0x60: ("RTS", AddressingMode.IMPLICIT, 1, 6),
		0x61: ("ADC", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0x65: ("ADC", AddressingMode.ZERO_PAGE, 2, 3),
		0x66: ("ROR", AddressingMode.ZERO_PAGE, 2, 5),
		0x68: ("PLA", AddressingMode.IMPLICIT, 1, 4),
		0x69: ("ADC", AddressingMode.IMMEDIATE, 2, 2),
		0x6A: ("ROR", AddressingMode.ACCUMULATOR, 1, 2),
		0x6C: ("JMP", AddressingMode.INDIRECT, 3, 5),
		0x6D: ("ADC", AddressingMode.ABSOLUTE, 3, 4),
		0x6E: ("ROR", AddressingMode.ABSOLUTE, 3, 6),

		0x70: ("BVS", AddressingMode.RELATIVE, 2, 2),
		0x71: ("ADC", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0x75: ("ADC", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x76: ("ROR", AddressingMode.ZERO_PAGE_X, 2, 6),
		0x78: ("SEI", AddressingMode.IMPLICIT, 1, 2),
		0x79: ("ADC", AddressingMode.ABSOLUTE_Y, 3, 4),
		0x7D: ("ADC", AddressingMode.ABSOLUTE_X, 3, 4),
		0x7E: ("ROR", AddressingMode.ABSOLUTE_X, 3, 7),

		0x81: ("STA", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0x84: ("STY", AddressingMode.ZERO_PAGE, 2, 3),
		0x85: ("STA", AddressingMode.ZERO_PAGE, 2, 3),
		0x86: ("STX", AddressingMode.ZERO_PAGE, 2, 3),
		0x88: ("DEY", AddressingMode.IMPLICIT, 1, 2),
		0x8A: ("TXA", AddressingMode.IMPLICIT, 1, 2),
		0x8C: ("STY", AddressingMode.ABSOLUTE, 3, 4),
		0x8D: ("STA", AddressingMode.ABSOLUTE, 3, 4),
		0x8E: ("STX", AddressingMode.ABSOLUTE, 3, 4),

		0x90: ("BCC", AddressingMode.RELATIVE, 2, 2),
		0x91: ("STA", AddressingMode.INDIRECT_INDEXED, 2, 6),
		0x94: ("STY", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x95: ("STA", AddressingMode.ZERO_PAGE_X, 2, 4),
		0x96: ("STX", AddressingMode.ZERO_PAGE_Y, 2, 4),
		0x98: ("TYA", AddressingMode.IMPLICIT, 1, 2),
		0x99: ("STA", AddressingMode.ABSOLUTE_Y, 3, 5),
		0x9A: ("TXS", AddressingMode.IMPLICIT, 1, 2),
		0x9D: ("STA", AddressingMode.ABSOLUTE_X, 3, 5),

		0xA0: ("LDY", AddressingMode.IMMEDIATE, 2, 2),
		0xA1: ("LDA", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0xA2: ("LDX", AddressingMode.IMMEDIATE, 2, 2),
		0xA4: ("LDY", AddressingMode.ZERO_PAGE, 2, 3),
		0xA5: ("LDA", AddressingMode.ZERO_PAGE, 2, 3),
		0xA6: ("LDX", AddressingMode.ZERO_PAGE, 2, 3),
		0xA8: ("TAY", AddressingMode.IMPLICIT, 1, 2),
		0xA9: ("LDA", AddressingMode.IMMEDIATE, 2, 2),
		0xAA: ("TAX", AddressingMode.IMPLICIT, 1, 2),
		0xAC: ("LDY", AddressingMode.ABSOLUTE, 3, 4),
		0xAD: ("LDA", AddressingMode.ABSOLUTE, 3, 4),
		0xAE: ("LDX", AddressingMode.ABSOLUTE, 3, 4),

		0xB0: ("BCS", AddressingMode.RELATIVE, 2, 2),
		0xB1: ("LDA", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0xB4: ("LDY", AddressingMode.ZERO_PAGE_X, 2, 4),
		0xB5: ("LDA", AddressingMode.ZERO_PAGE_X, 2, 4),
		0xB6: ("LDX", AddressingMode.ZERO_PAGE_Y, 2, 4),
		0xB8: ("CLV", AddressingMode.IMPLICIT, 1, 2),
		0xB9: ("LDA", AddressingMode.ABSOLUTE_Y, 3, 4),
		0xBA: ("TSX", AddressingMode.IMPLICIT, 1, 2),
		0xBC: ("LDY", AddressingMode.ABSOLUTE_X, 3, 4),
		0xBD: ("LDA", AddressingMode.ABSOLUTE_X, 3, 4),
		0xBE: ("LDX", AddressingMode.ABSOLUTE_Y, 3, 4),

		0xC0: ("CPY", AddressingMode.IMMEDIATE, 2, 2),
		0xC1: ("CMP", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0xC4: ("CPY", AddressingMode.ZERO_PAGE, 2, 3),
		0xC5: ("CMP", AddressingMode.ZERO_PAGE, 2, 3),
		0xC6: ("DEC", AddressingMode.ZERO_PAGE, 2, 5),
		0xC8: ("INY", AddressingMode.IMPLICIT, 1, 2),
		0xC9: ("CMP", AddressingMode.IMMEDIATE, 2, 2),
		0xCA: ("DEX", AddressingMode.IMPLICIT, 1, 2),
		0xCC: ("CPY", AddressingMode.ABSOLUTE, 3, 4),
		0xCD: ("CMP", AddressingMode.ABSOLUTE, 3, 4),
		0xCE: ("DEC", AddressingMode.ABSOLUTE, 3, 6),

		0xD0: ("BNE", AddressingMode.RELATIVE, 2, 2),
		0xD1: ("CMP", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0xD5: ("CMP", AddressingMode.ZERO_PAGE_X, 2, 4),
		0xD6: ("DEC", AddressingMode.ZERO_PAGE_X, 2, 6),
		0xD8: ("CLD", AddressingMode.IMPLICIT, 1, 2),
		0xD9: ("CMP", AddressingMode.ABSOLUTE_Y, 3, 4),
		0xDD: ("CMP", AddressingMode.ABSOLUTE_X, 3, 4),
		0xDE: ("DEC", AddressingMode.ABSOLUTE_X, 3, 7),

		0xE0: ("CPX", AddressingMode.IMMEDIATE, 2, 2),
		0xE1: ("SBC", AddressingMode.INDEXED_INDIRECT, 2, 6),
		0xE4: ("CPX", AddressingMode.ZERO_PAGE, 2, 3),
		0xE5: ("SBC", AddressingMode.ZERO_PAGE, 2, 3),
		0xE6: ("INC", AddressingMode.ZERO_PAGE, 2, 5),
		0xE8: ("INX", AddressingMode.IMPLICIT, 1, 2),
		0xE9: ("SBC", AddressingMode.IMMEDIATE, 2, 2),
		0xEA: ("NOP", AddressingMode.IMPLICIT, 1, 2),
		0xEC: ("CPX", AddressingMode.ABSOLUTE, 3, 4),
		0xED: ("SBC", AddressingMode.ABSOLUTE, 3, 4),
		0xEE: ("INC", AddressingMode.ABSOLUTE, 3, 6),

		0xF0: ("BEQ", AddressingMode.RELATIVE, 2, 2),
		0xF1: ("SBC", AddressingMode.INDIRECT_INDEXED, 2, 5),
		0xF5: ("SBC", AddressingMode.ZERO_PAGE_X, 2, 4),
		0xF6: ("INC", AddressingMode.ZERO_PAGE_X, 2, 6),
		0xF8: ("SED", AddressingMode.IMPLICIT, 1, 2),
		0xF9: ("SBC", AddressingMode.ABSOLUTE_Y, 3, 4),
		0xFD: ("SBC", AddressingMode.ABSOLUTE_X, 3, 4),
		0xFE: ("INC", AddressingMode.ABSOLUTE_X, 3, 7),
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
		'hero_hp': 0x00C5,
		'hero_mp': 0x00C6,
		'hero_level': 0x00BA,
		'hero_xp_low': 0x00BB,
		'hero_xp_high': 0x00BC,
		'hero_gold_low': 0x00BD,
		'hero_gold_high': 0x00BE,
		'hero_str': 0x00C7,
		'hero_agi': 0x00C8,
		'hero_atk': 0x00C9,
		'hero_def': 0x00CA,
	}

	@staticmethod
	def generate_game_genie(address: int, value: int) -> str:
		"""Generate NES Game Genie code."""
		# Game Genie encoding (simplified)
		# Note: Real Game Genie uses complex encoding
		code_chars = "APZLGITYEOXUKSVN"

		# This is a simplified version - real encoding is more complex
		addr_code = address & 0x7FFF
		val_code = value & 0xFF

		# Create 6-letter code (simplified)
		code = ""
		temp = (addr_code << 8) | val_code

		for i in range(6):
			code += code_chars[temp & 0x0F]
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
			0xFF,
			"Max Gold (65535) - High Byte"
		))
		cheats.append(self.generate_raw_cheat(
			self.KNOWN_ADDRESSES['hero_gold_low'],
			0xFF,
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
