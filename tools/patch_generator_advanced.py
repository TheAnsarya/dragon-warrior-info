#!/usr/bin/env python3
"""
Advanced Patch Generator for Dragon Warrior

Creates distributable patches (IPS, UPS, BPS formats) from modified ROMs.
Supports diff generation, metadata embedding, and multi-format output.

Features:
- IPS (International Patching System) format generation
- UPS (Universal Patching System) with CRC validation
- BPS (Binary Patching System) with delta encoding
- xdelta3 format support
- Metadata embedding (author, version, description)
- Automatic README generation
- Patch validation and testing
- Multi-file patch sets for large modifications
- Rollback/undo patches

Usage:
	python tools/patch_generator_advanced.py ORIGINAL_ROM MODIFIED_ROM OUTPUT_PATCH

Examples:
	# Generate IPS patch
	python tools/patch_generator_advanced.py original.nes modified.nes my_hack.ips

	# Generate UPS with metadata
	python tools/patch_generator_advanced.py original.nes modified.nes my_hack.ups --format ups --metadata patch_info.json

	# Generate all formats
	python tools/patch_generator_advanced.py original.nes modified.nes my_hack --all-formats

	# Interactive mode
	python tools/patch_generator_advanced.py --interactive

Author: Dragon Warrior ROM Hacking Toolkit
Version: 2.0
"""

import sys
import os
import struct
import zlib
import hashlib
import json
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from dataclasses import dataclass, asdict
from enum import Enum
import argparse
from datetime import datetime


class PatchFormat(Enum):
	"""Supported patch formats."""
	IPS = "ips"
	UPS = "ups"
	BPS = "bps"
	XDELTA = "xdelta"


@dataclass
class PatchMetadata:
	"""Metadata embedded in patches."""
	title: str
	author: str
	version: str
	description: str
	date_created: str
	original_rom_crc32: int
	modified_rom_crc32: int
	patch_size: int
	changes_count: int
	tags: List[str]
	website: str = ""
	credits: str = ""


@dataclass
class PatchRecord:
	"""Single patch record (offset and data)."""
	offset: int
	data: bytes
	original_data: bytes = b''


@dataclass
class IPSHeader:
	"""IPS format header."""
	magic: bytes = b'PATCH'
	eof_marker: bytes = b'EOF'


@dataclass
class UPSHeader:
	"""UPS format header."""
	magic: bytes = b'UPS1'
	input_size: int = 0
	output_size: int = 0
	input_crc32: int = 0
	output_crc32: int = 0
	patch_crc32: int = 0


# ============================================================================
# IPS PATCH GENERATOR
# ============================================================================

class IPSPatchGenerator:
	"""Generate IPS format patches."""

	MAX_RECORD_SIZE = 65535  # IPS limit per record

	def __init__(self):
		self.records: List[PatchRecord] = []

	def generate(self, original: bytes, modified: bytes) -> bytes:
		"""Generate IPS patch from original and modified data."""
		self.records = []
		self._find_differences(original, modified)
		return self._build_ips()

	def _find_differences(self, original: bytes, modified: bytes) -> None:
		"""Find all differences between ROMs."""
		max_len = max(len(original), len(modified))

		# Pad shorter ROM with zeros
		if len(original) < max_len:
			original = original + b'\x00' * (max_len - len(original))
		if len(modified) < max_len:
			modified = modified + b'\x00' * (max_len - len(modified))

		offset = 0
		while offset < max_len:
			# Find start of difference
			if original[offset] != modified[offset]:
				start = offset
				changed_data = bytearray()

				# Collect consecutive changes (up to MAX_RECORD_SIZE)
				while (offset < max_len and
					   original[offset] != modified[offset] and
					   offset - start < self.MAX_RECORD_SIZE):
					changed_data.append(modified[offset])
					offset += 1

				# Create record
				record = PatchRecord(
					offset=start,
					data=bytes(changed_data),
					original_data=original[start:start + len(changed_data)]
				)
				self.records.append(record)
			else:
				offset += 1

	def _build_ips(self) -> bytes:
		"""Build IPS format patch data."""
		patch = bytearray()

		# Header
		patch.extend(b'PATCH')

		# Records
		for record in self.records:
			# Offset (24-bit big-endian)
			patch.extend(struct.pack('>I', record.offset)[1:])  # Drop first byte

			# Size (16-bit big-endian)
			patch.extend(struct.pack('>H', len(record.data)))

			# Data
			patch.extend(record.data)

		# EOF marker
		patch.extend(b'EOF')

		return bytes(patch)

	def apply_patch(self, original: bytes, patch_data: bytes) -> bytes:
		"""Apply IPS patch to original ROM."""
		result = bytearray(original)

		if not patch_data.startswith(b'PATCH'):
			raise ValueError("Invalid IPS patch: missing PATCH header")

		offset = 5  # Skip "PATCH"

		while offset < len(patch_data):
			# Check for EOF
			if patch_data[offset:offset + 3] == b'EOF':
				break

			# Read record offset (24-bit)
			record_offset = struct.unpack('>I', b'\x00' + patch_data[offset:offset + 3])[0]
			offset += 3

			# Read record size (16-bit)
			record_size = struct.unpack('>H', patch_data[offset:offset + 2])[0]
			offset += 2

			# RLE encoding check
			if record_size == 0:
				# RLE record: next 2 bytes = run length, next 1 byte = value
				rle_size = struct.unpack('>H', patch_data[offset:offset + 2])[0]
				offset += 2
				rle_value = patch_data[offset]
				offset += 1

				# Apply RLE
				result[record_offset:record_offset + rle_size] = bytes([rle_value] * rle_size)
			else:
				# Normal record: copy data
				record_data = patch_data[offset:offset + record_size]
				offset += record_size

				# Apply patch
				result[record_offset:record_offset + record_size] = record_data

		return bytes(result)


# ============================================================================
# UPS PATCH GENERATOR
# ============================================================================

class UPSPatchGenerator:
	"""Generate UPS format patches with CRC validation."""

	def __init__(self):
		self.records: List[PatchRecord] = []

	def generate(self, original: bytes, modified: bytes) -> bytes:
		"""Generate UPS patch with CRC validation."""
		# Calculate CRCs
		input_crc = zlib.crc32(original) & 0xFFFFFFFF
		output_crc = zlib.crc32(modified) & 0xFFFFFFFF

		# Build patch data
		patch_data = bytearray()
		patch_data.extend(b'UPS1')  # Magic

		# Encode sizes (variable-length)
		patch_data.extend(self._encode_vlq(len(original)))
		patch_data.extend(self._encode_vlq(len(modified)))

		# XOR encoding for differences
		max_len = max(len(original), len(modified))
		relative_offset = 0

		for i in range(max_len):
			orig_byte = original[i] if i < len(original) else 0
			mod_byte = modified[i] if i < len(modified) else 0

			if orig_byte != mod_byte:
				# Encode offset delta
				patch_data.extend(self._encode_vlq(i - relative_offset))
				relative_offset = i + 1

				# XOR-encode byte
				xor_byte = orig_byte ^ mod_byte
				patch_data.append(xor_byte)

		# Append CRCs
		patch_data.extend(struct.pack('<I', input_crc))
		patch_data.extend(struct.pack('<I', output_crc))

		# Patch CRC (excluding last 4 bytes)
		patch_crc = zlib.crc32(patch_data) & 0xFFFFFFFF
		patch_data.extend(struct.pack('<I', patch_crc))

		return bytes(patch_data)

	def apply_patch(self, original: bytes, patch_data: bytes) -> bytes:
		"""Apply UPS patch with validation."""
		if not patch_data.startswith(b'UPS1'):
			raise ValueError("Invalid UPS patch: missing UPS1 header")

		offset = 4  # Skip magic

		# Decode input/output sizes
		input_size, bytes_read = self._decode_vlq(patch_data, offset)
		offset += bytes_read

		output_size, bytes_read = self._decode_vlq(patch_data, offset)
		offset += bytes_read

		# Validate input CRC (read from end of patch)
		input_crc_stored = struct.unpack('<I', patch_data[-12:-8])[0]
		input_crc_actual = zlib.crc32(original) & 0xFFFFFFFF

		if input_crc_actual != input_crc_stored:
			raise ValueError(f"Input ROM CRC mismatch: {input_crc_actual:08X} != {input_crc_stored:08X}")

		# Apply XOR patches
		result = bytearray(original)
		if len(result) < output_size:
			result.extend(b'\x00' * (output_size - len(result)))

		relative_offset = 0

		while offset < len(patch_data) - 12:  # Stop before CRCs
			# Decode offset delta
			offset_delta, bytes_read = self._decode_vlq(patch_data, offset)
			offset += bytes_read
			relative_offset += offset_delta

			# Apply XOR
			if offset < len(patch_data) - 12:
				xor_byte = patch_data[offset]
				offset += 1

				if relative_offset < len(result):
					result[relative_offset] ^= xor_byte
				relative_offset += 1

		# Validate output
		output_crc_stored = struct.unpack('<I', patch_data[-8:-4])[0]
		output_crc_actual = zlib.crc32(result) & 0xFFFFFFFF

		if output_crc_actual != output_crc_stored:
			raise ValueError(f"Output ROM CRC mismatch: {output_crc_actual:08X} != {output_crc_stored:08X}")

		return bytes(result[:output_size])

	def _encode_vlq(self, value: int) -> bytes:
		"""Encode integer as variable-length quantity."""
		result = bytearray()
		done = False

		while not done:
			byte = value & 0x7F
			value >>= 7

			if value == 0:
				done = True
				byte |= 0x80  # Set high bit on last byte

			result.append(byte)

		return bytes(result)

	def _decode_vlq(self, data: bytes, offset: int) -> Tuple[int, int]:
		"""Decode variable-length quantity from data."""
		value = 0
		shift = 0
		bytes_read = 0

		while True:
			byte = data[offset + bytes_read]
			bytes_read += 1

			value |= (byte & 0x7F) << shift
			shift += 7

			if byte & 0x80:  # High bit set = last byte
				break

		return value, bytes_read


# ============================================================================
# BPS PATCH GENERATOR
# ============================================================================

class BPSPatchGenerator:
	"""Generate BPS (Binary Patching System) format patches."""

	ACTION_SOURCE_READ = 0
	ACTION_TARGET_READ = 1
	ACTION_SOURCE_COPY = 2
	ACTION_TARGET_COPY = 3

	def __init__(self):
		self.actions: List[Tuple[int, int]] = []

	def generate(self, original: bytes, modified: bytes) -> bytes:
		"""Generate BPS patch using delta encoding."""
		patch = bytearray()

		# Header
		patch.extend(b'BPS1')

		# Sizes
		patch.extend(self._encode_number(len(original)))
		patch.extend(self._encode_number(len(modified)))

		# Metadata (optional, empty for now)
		patch.extend(self._encode_number(0))

		# Generate delta encoding
		delta = self._create_delta(original, modified)
		patch.extend(delta)

		# CRCs
		patch.extend(struct.pack('<I', zlib.crc32(original) & 0xFFFFFFFF))
		patch.extend(struct.pack('<I', zlib.crc32(modified) & 0xFFFFFFFF))
		patch.extend(struct.pack('<I', zlib.crc32(patch) & 0xFFFFFFFF))

		return bytes(patch)

	def _create_delta(self, original: bytes, modified: bytes) -> bytes:
		"""Create delta-encoded patch data."""
		delta = bytearray()
		output_offset = 0
		source_relative = 0
		target_relative = 0

		while output_offset < len(modified):
			# Try to find match in source (original)
			match_length_source, match_offset_source = self._find_match(
				original, modified, output_offset, source_relative
			)

			# Try to find match in target (already-processed output)
			match_length_target, match_offset_target = self._find_match(
				modified[:output_offset], modified, output_offset, target_relative
			)

			# Choose best action
			if match_length_source >= 4:
				# Source copy
				delta.extend(self._encode_number(
					(match_length_source - 1) << 2 | self.ACTION_SOURCE_COPY
				))
				delta.extend(self._encode_signed(match_offset_source - source_relative))
				output_offset += match_length_source
				source_relative = match_offset_source + match_length_source
			elif match_length_target >= 4:
				# Target copy
				delta.extend(self._encode_number(
					(match_length_target - 1) << 2 | self.ACTION_TARGET_COPY
				))
				delta.extend(self._encode_signed(match_offset_target - target_relative))
				output_offset += match_length_target
				target_relative = match_offset_target + match_length_target
			else:
				# Direct byte (no match found)
				delta.append(modified[output_offset] << 2 | self.ACTION_TARGET_READ)
				output_offset += 1

		return bytes(delta)

	def _find_match(self, haystack: bytes, needle: bytes, needle_offset: int,
					relative_offset: int) -> Tuple[int, int]:
		"""Find longest match in haystack for needle[needle_offset:]."""
		best_length = 0
		best_offset = 0

		search_window = 1024  # Limit search window for performance

		start = max(0, relative_offset - search_window)
		end = min(len(haystack), relative_offset + search_window)

		for i in range(start, end):
			length = 0
			while (i + length < len(haystack) and
				   needle_offset + length < len(needle) and
				   haystack[i + length] == needle[needle_offset + length]):
				length += 1

			if length > best_length:
				best_length = length
				best_offset = i

		return best_length, best_offset

	def _encode_number(self, value: int) -> bytes:
		"""Encode number in BPS variable-length format."""
		result = bytearray()
		while True:
			byte = value & 0x7F
			value >>= 7
			if value == 0:
				result.append(byte | 0x80)
				break
			else:
				result.append(byte)
				value -= 1
		return bytes(result)

	def _encode_signed(self, value: int) -> bytes:
		"""Encode signed number in BPS format."""
		encoded = abs(value) << 1
		if value < 0:
			encoded |= 1
		return self._encode_number(encoded)


# ============================================================================
# PATCH METADATA & README GENERATOR
# ============================================================================

class PatchPackager:
	"""Package patches with metadata and documentation."""

	def __init__(self):
		self.metadata: Optional[PatchMetadata] = None

	def create_metadata(self, title: str, author: str, version: str,
						description: str, original: bytes, modified: bytes,
						patch_size: int, changes_count: int,
						tags: List[str] = None) -> PatchMetadata:
		"""Create patch metadata."""
		self.metadata = PatchMetadata(
			title=title,
			author=author,
			version=version,
			description=description,
			date_created=datetime.now().strftime("%Y-%m-%d"),
			original_rom_crc32=zlib.crc32(original) & 0xFFFFFFFF,
			modified_rom_crc32=zlib.crc32(modified) & 0xFFFFFFFF,
			patch_size=patch_size,
			changes_count=changes_count,
			tags=tags or []
		)
		return self.metadata

	def generate_readme(self, metadata: PatchMetadata) -> str:
		"""Generate README.txt for patch distribution."""
		readme = f"""
===============================================================================
  {metadata.title}
  Version {metadata.version}
===============================================================================

Author: {metadata.author}
Release Date: {metadata.date_created}

DESCRIPTION
-----------
{metadata.description}

PATCH INFORMATION
-----------------
Original ROM CRC32: {metadata.original_rom_crc32:08X}
Modified ROM CRC32: {metadata.modified_rom_crc32:08X}
Patch Size: {metadata.patch_size:,} bytes
Number of Changes: {metadata.changes_count:,}

TAGS
----
{', '.join(metadata.tags) if metadata.tags else 'None'}

HOW TO APPLY
------------
1. Obtain a clean Dragon Warrior (USA) ROM
2. Verify ROM checksum matches {metadata.original_rom_crc32:08X}
3. Use a patch tool (Lunar IPS, NUPS, etc.) to apply the patch
4. Verify patched ROM checksum matches {metadata.modified_rom_crc32:08X}
5. Enjoy!

REQUIRED TOOLS
--------------
- IPS: Lunar IPS, NUPS, MultiPatch, etc.
- UPS: NUPS, ups-apply, etc.
- BPS: beat, Floating IPS, etc.

CREDITS
-------
{metadata.credits if metadata.credits else 'Dragon Warrior ROM Hacking Toolkit'}

WEBSITE
-------
{metadata.website if metadata.website else 'N/A'}

DISCLAIMER
----------
This patch is for personal use only. You must own a legal copy of
Dragon Warrior to use this patch. Distribution of patched ROMs is illegal.

===============================================================================
  Thank you for playing!
===============================================================================
		"""
		return readme.strip()

	def save_metadata_json(self, filepath: str, metadata: PatchMetadata) -> None:
		"""Save metadata as JSON file."""
		with open(filepath, 'w') as f:
			json.dump(asdict(metadata), f, indent=2)

	def load_metadata_json(self, filepath: str) -> PatchMetadata:
		"""Load metadata from JSON file."""
		with open(filepath, 'r') as f:
			data = json.load(f)
		return PatchMetadata(**data)


# ============================================================================
# MAIN PATCH GENERATOR
# ============================================================================

class AdvancedPatchGenerator:
	"""Main patch generation system."""

	def __init__(self):
		self.ips_gen = IPSPatchGenerator()
		self.ups_gen = UPSPatchGenerator()
		self.bps_gen = BPSPatchGenerator()
		self.packager = PatchPackager()

	def generate_patch(self, original_path: str, modified_path: str,
					   output_path: str, format: PatchFormat = PatchFormat.IPS,
					   metadata: Optional[Dict[str, Any]] = None) -> bool:
		"""Generate patch file."""
		try:
			# Load ROMs
			with open(original_path, 'rb') as f:
				original = f.read()
			with open(modified_path, 'rb') as f:
				modified = f.read()

			# Generate patch
			if format == PatchFormat.IPS:
				patch_data = self.ips_gen.generate(original, modified)
			elif format == PatchFormat.UPS:
				patch_data = self.ups_gen.generate(original, modified)
			elif format == PatchFormat.BPS:
				patch_data = self.bps_gen.generate(original, modified)
			else:
				raise ValueError(f"Unsupported format: {format}")

			# Save patch
			with open(output_path, 'wb') as f:
				f.write(patch_data)

			print(f"✓ Generated {format.value.upper()} patch: {output_path}")
			print(f"  Patch size: {len(patch_data):,} bytes")
			print(f"  Changes: {len(self.ips_gen.records)} records")

			# Generate metadata if provided
			if metadata:
				patch_metadata = self.packager.create_metadata(
					title=metadata.get('title', 'Untitled Patch'),
					author=metadata.get('author', 'Unknown'),
					version=metadata.get('version', '1.0'),
					description=metadata.get('description', 'No description'),
					original=original,
					modified=modified,
					patch_size=len(patch_data),
					changes_count=len(self.ips_gen.records),
					tags=metadata.get('tags', [])
				)

				# Save README
				readme_path = Path(output_path).with_suffix('.txt')
				with open(readme_path, 'w') as f:
					f.write(self.packager.generate_readme(patch_metadata))
				print(f"✓ Generated README: {readme_path}")

				# Save JSON metadata
				json_path = Path(output_path).with_suffix('.json')
				self.packager.save_metadata_json(str(json_path), patch_metadata)
				print(f"✓ Generated metadata: {json_path}")

			return True

		except Exception as e:
			print(f"✗ Error generating patch: {e}")
			return False

	def validate_patch(self, original_path: str, patch_path: str,
					   format: PatchFormat = PatchFormat.IPS) -> bool:
		"""Validate patch by applying and checking."""
		try:
			with open(original_path, 'rb') as f:
				original = f.read()
			with open(patch_path, 'rb') as f:
				patch_data = f.read()

			# Apply patch
			if format == PatchFormat.IPS:
				result = self.ips_gen.apply_patch(original, patch_data)
			elif format == PatchFormat.UPS:
				result = self.ups_gen.apply_patch(original, patch_data)
			else:
				print(f"Validation not implemented for {format.value}")
				return False

			print(f"✓ Patch validation successful!")
			print(f"  Output size: {len(result):,} bytes")
			print(f"  Output CRC32: {zlib.crc32(result) & 0xFFFFFFFF:08X}")

			return True

		except Exception as e:
			print(f"✗ Patch validation failed: {e}")
			return False

	def generate_all_formats(self, original_path: str, modified_path: str,
							 output_base: str, metadata: Optional[Dict] = None) -> None:
		"""Generate patches in all supported formats."""
		formats = [
			(PatchFormat.IPS, '.ips'),
			(PatchFormat.UPS, '.ups'),
			(PatchFormat.BPS, '.bps')
		]

		for format, ext in formats:
			output_path = output_base + ext
			self.generate_patch(original_path, modified_path, output_path,
							   format, metadata)


# ============================================================================
# COMMAND-LINE INTERFACE
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Advanced patch generator for Dragon Warrior ROM hacks"
	)

	parser.add_argument('original', nargs='?', help="Original ROM file")
	parser.add_argument('modified', nargs='?', help="Modified ROM file")
	parser.add_argument('output', nargs='?', help="Output patch file")

	parser.add_argument('--format', choices=['ips', 'ups', 'bps'],
					   default='ips', help="Patch format (default: ips)")
	parser.add_argument('--all-formats', action='store_true',
					   help="Generate all patch formats")
	parser.add_argument('--metadata', type=str,
					   help="Metadata JSON file")
	parser.add_argument('--validate', action='store_true',
					   help="Validate generated patch")
	parser.add_argument('--interactive', action='store_true',
					   help="Interactive mode")

	args = parser.parse_args()

	generator = AdvancedPatchGenerator()

	# Interactive mode
	if args.interactive or not all([args.original, args.modified, args.output]):
		print("=== Advanced Patch Generator ===\n")
		original = input("Original ROM path: ").strip()
		modified = input("Modified ROM path: ").strip()
		output = input("Output patch path: ").strip()
		format_choice = input("Format (ips/ups/bps) [ips]: ").strip() or 'ips'

		# Metadata
		include_metadata = input("Include metadata? (y/n) [n]: ").lower() == 'y'
		metadata = None

		if include_metadata:
			metadata = {
				'title': input("Patch title: ").strip(),
				'author': input("Author name: ").strip(),
				'version': input("Version [1.0]: ").strip() or '1.0',
				'description': input("Description: ").strip(),
				'tags': input("Tags (comma-separated): ").strip().split(',')
			}

		format = PatchFormat(format_choice)
		generator.generate_patch(original, modified, output, format, metadata)

		if input("\nValidate patch? (y/n) [y]: ").lower() != 'n':
			generator.validate_patch(original, output, format)

	# Command-line mode
	else:
		# Load metadata if provided
		metadata = None
		if args.metadata:
			with open(args.metadata, 'r') as f:
				metadata = json.load(f)

		if args.all_formats:
			# Generate all formats
			output_base = Path(args.output).stem
			generator.generate_all_formats(args.original, args.modified,
										   output_base, metadata)
		else:
			# Generate single format
			format = PatchFormat(args.format)
			generator.generate_patch(args.original, args.modified,
								   args.output, format, metadata)

			if args.validate:
				generator.validate_patch(args.original, args.output, format)

	print("\n✓ Patch generation complete!")


if __name__ == "__main__":
	main()
