"""
Dragon Warrior ROM Validator & Analyzer
Comprehensive ROM validation, analysis, and data mining tool

Features:
- ROM format validation (header, size, checksums)
- Data integrity checks
- Known version detection
- Data structure analysis
- Memory map generation
- Unused space detection
- Text extraction and analysis

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import os
import struct
import hashlib
from typing import List, Tuple, Dict, Optional, Set
from dataclasses import dataclass
from collections import Counter
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


@dataclass
class ROMInfo:
	"""Comprehensive ROM information"""
	file_path: str
	file_size: int
	md5_hash: str
	sha1_hash: str

	# NES header info
	has_header: bool
	prg_rom_size: int
	chr_rom_size: int
	mapper_number: int
	has_battery: bool
	has_trainer: bool
	mirroring: str

	# Known version
	version_name: Optional[str]
	version_region: Optional[str]
	version_revision: Optional[str]


@dataclass
class DataRegion:
	"""Named data region in ROM"""
	name: str
	start_offset: int
	end_offset: int
	data_type: str  # 'code', 'graphics', 'text', 'data', 'music', 'unknown'
	description: str

	@property
	def size(self) -> int:
		return self.end_offset - start_offset + 1


@dataclass
class ValidationResult:
	"""ROM validation result"""
	is_valid: bool
	issues: List[str]
	warnings: List[str]
	info: List[str]
	rom_info: Optional[ROMInfo]


class ROMValidator:
	"""ROM validation engine"""

	# Known Dragon Warrior ROM versions
	KNOWN_VERSIONS = {
		'a8f2038caa4faa85297b8a38fd5e9825': {
			'name': 'Dragon Warrior (USA)',
			'region': 'NTSC-U',
			'revision': 'Rev A',
			'size': 262144,  # 256 KB
		},
		# Add more known versions here
	}

	@staticmethod
	def validate_rom(rom_data: bytes, file_path: str = "") -> ValidationResult:
		"""
		Comprehensive ROM validation

		Returns ValidationResult with all findings
		"""
		issues = []
		warnings = []
		info = []

		# Calculate hashes
		md5_hash = hashlib.md5(rom_data).hexdigest()
		sha1_hash = hashlib.sha1(rom_data).hexdigest()

		info.append(f"File size: {len(rom_data):,} bytes")
		info.append(f"MD5: {md5_hash}")
		info.append(f"SHA1: {sha1_hash}")

		# Check known version
		version_name = None
		version_region = None
		version_revision = None

		if md5_hash in ROMValidator.KNOWN_VERSIONS:
			version_info = ROMValidator.KNOWN_VERSIONS[md5_hash]
			version_name = version_info['name']
			version_region = version_info['region']
			version_revision = version_info['revision']
			info.append(f"✓ Recognized version: {version_name} ({version_region}, {version_revision})")
		else:
			warnings.append("⚠ Unknown ROM version (MD5 not in database)")

		# Parse NES header
		has_header = False
		prg_rom_size = 0
		chr_rom_size = 0
		mapper_number = 0
		has_battery = False
		has_trainer = False
		mirroring = "Unknown"

		if len(rom_data) >= 16:
			header = rom_data[:16]

			# Check for "NES" magic
			if header[:4] == b'NES\x1A':
				has_header = True
				info.append("✓ Valid iNES header found")

				# Parse header
				prg_rom_size = header[4] * 16384  # 16 KB units
				chr_rom_size = header[5] * 8192   # 8 KB units

				flags6 = header[6]
				flags7 = header[7]

				mapper_number = ((flags7 & 0xf0) | (flags6 >> 4))
				has_battery = bool(flags6 & 0x02)
				has_trainer = bool(flags6 & 0x04)
				mirroring = "Vertical" if (flags6 & 0x01) else "Horizontal"

				info.append(f"  PRG ROM: {prg_rom_size:,} bytes ({prg_rom_size // 1024} KB)")
				info.append(f"  CHR ROM: {chr_rom_size:,} bytes ({chr_rom_size // 1024} KB)")
				info.append(f"  Mapper: {mapper_number}")
				info.append(f"  Mirroring: {mirroring}")
				info.append(f"  Battery: {has_battery}")
				info.append(f"  Trainer: {has_trainer}")

				# Validate sizes
				expected_size = 16 + (512 if has_trainer else 0) + prg_rom_size + chr_rom_size
				if len(rom_data) != expected_size:
					warnings.append(f"⚠ ROM size mismatch: expected {expected_size:,}, got {len(rom_data):,}")

				# Check for Dragon Warrior specifics
				if mapper_number != 0:
					warnings.append(f"⚠ Unexpected mapper: {mapper_number} (Dragon Warrior typically uses mapper 0)")

				if prg_rom_size not in [32768, 65536]:  # 32 KB or 64 KB
					warnings.append(f"⚠ Unusual PRG ROM size: {prg_rom_size} bytes")

				if chr_rom_size != 32768:  # 32 KB
					warnings.append(f"⚠ Unusual CHR ROM size: {chr_rom_size} bytes")

			else:
				issues.append("✗ Invalid or missing iNES header")
				warnings.append("⚠ ROM may be headerless or corrupted")
		else:
			issues.append("✗ File too small to be valid NES ROM")

		# Check CHR-ROM data
		if has_header and len(rom_data) > 16 + prg_rom_size:
			chr_offset = 16 + prg_rom_size
			chr_data = rom_data[chr_offset:chr_offset + chr_rom_size]

			# Check if CHR is all zeros (should have graphics data)
			if chr_data == b'\x00' * len(chr_data):
				issues.append("✗ CHR-ROM is all zeros (no graphics data)")
			else:
				info.append("✓ CHR-ROM contains graphics data")

				# Check for valid tile patterns
				non_zero_bytes = sum(1 for b in chr_data if b != 0)
				utilization = (non_zero_bytes / len(chr_data) * 100) if chr_data else 0
				info.append(f"  CHR utilization: {utilization:.1f}% non-zero bytes")

		# Check for common corruption patterns
		if b'\xFF' * 256 in rom_data:
			warnings.append("⚠ Long sequence of 0xff bytes detected (possible corruption)")

		if b'\x00' * 256 in rom_data[16:]:  # Ignore header
			info.append("  Note: Contains large empty regions (may be unused space)")

		# Create ROM info object
		rom_info = ROMInfo(
			file_path=file_path,
			file_size=len(rom_data),
			md5_hash=md5_hash,
			sha1_hash=sha1_hash,
			has_header=has_header,
			prg_rom_size=prg_rom_size,
			chr_rom_size=chr_rom_size,
			mapper_number=mapper_number,
			has_battery=has_battery,
			has_trainer=has_trainer,
			mirroring=mirroring,
			version_name=version_name,
			version_region=version_region,
			version_revision=version_revision
		)

		# Determine overall validity
		is_valid = len(issues) == 0 and has_header

		return ValidationResult(
			is_valid=is_valid,
			issues=issues,
			warnings=warnings,
			info=info,
			rom_info=rom_info
		)


class ROMAnalyzer:
	"""Advanced ROM analysis"""

	# Dragon Warrior known data regions
	DW_MEMORY_MAP = [
		DataRegion("iNES Header", 0x0000, 0x000f, "header", "16-byte iNES header"),
		DataRegion("PRG-ROM Bank 0", 0x0010, 0x4010, "code", "Program code and data"),
		DataRegion("World Map Data", 0x1d5d, 0x1f5c, "data", "120×120 overworld map"),
		DataRegion("Monster Stats", 0xc6e0, 0xc8af, "data", "39 monster stat blocks"),
		DataRegion("Text Pointers", 0xb0a0, 0xb0ff, "data", "Dialogue pointer table"),
		DataRegion("Text Data", 0xb100, 0xcfff, "text", "Compressed dialogue text"),
		DataRegion("Item Data", 0xcf50, 0xcfff, "data", "Item definitions"),
		DataRegion("Spell Data", 0xd000, 0xd1ff, "data", "Spell definitions"),
		DataRegion("Shop Data", 0xd200, 0xd7ff, "data", "Shop inventories and prices"),
		DataRegion("CHR-ROM", 0x10010, 0x18010, "graphics", "32 KB graphics data"),
		DataRegion("Pattern Table 0", 0x10010, 0x11010, "graphics", "Background tiles"),
		DataRegion("Pattern Table 1", 0x11010, 0x12010, "graphics", "Sprite tiles"),
		DataRegion("Pattern Table 2", 0x12010, 0x13010, "graphics", "Monster graphics"),
		DataRegion("Pattern Table 3", 0x13010, 0x14010, "graphics", "Extended graphics"),
	]

	@staticmethod
	def analyze_rom(rom_data: bytes) -> Dict:
		"""
		Perform comprehensive ROM analysis

		Returns dictionary with analysis results
		"""
		results = {}

		# Byte distribution
		byte_counts = Counter(rom_data)
		results['byte_distribution'] = {
			'total_bytes': len(rom_data),
			'unique_bytes': len(byte_counts),
			'most_common': byte_counts.most_common(10),
			'zero_bytes': byte_counts[0x00],
			'ff_bytes': byte_counts[0xff],
		}

		# Entropy analysis (simple)
		entropy = -sum((count / len(rom_data)) * (count / len(rom_data)).bit_length()
					  for count in byte_counts.values() if count > 0)
		results['entropy'] = entropy

		# Find text-like regions (ASCII printable + common control codes)
		text_regions = ROMAnalyzer._find_text_regions(rom_data)
		results['text_regions'] = text_regions

		# Find unused space
		unused_regions = ROMAnalyzer._find_unused_space(rom_data)
		results['unused_space'] = unused_regions

		# Pattern analysis
		patterns = ROMAnalyzer._find_patterns(rom_data)
		results['patterns'] = patterns

		return results

	@staticmethod
	def _find_text_regions(rom_data: bytes, min_length: int = 16) -> List[Tuple[int, int, bytes]]:
		"""Find regions that look like text"""
		text_regions = []
		current_start = None
		current_bytes = bytearray()

		for i, byte in enumerate(rom_data):
			# Check if printable ASCII or common control
			if (32 <= byte < 127) or byte in [0x00, 0x0a, 0x0d]:
				if current_start is None:
					current_start = i
				current_bytes.append(byte)
			else:
				# End of text region
				if current_start is not None and len(current_bytes) >= min_length:
					text_regions.append((current_start, i - 1, bytes(current_bytes)))
				current_start = None
				current_bytes = bytearray()

		# Check final region
		if current_start is not None and len(current_bytes) >= min_length:
			text_regions.append((current_start, len(rom_data) - 1, bytes(current_bytes)))

		return text_regions

	@staticmethod
	def _find_unused_space(rom_data: bytes, min_length: int = 64) -> List[Tuple[int, int]]:
		"""Find regions of unused space (all 0x00 or 0xff)"""
		unused_regions = []

		for fill_byte in [0x00, 0xff]:
			current_start = None
			current_length = 0

			for i, byte in enumerate(rom_data):
				if byte == fill_byte:
					if current_start is None:
						current_start = i
					current_length += 1
				else:
					if current_start is not None and current_length >= min_length:
						unused_regions.append((current_start, i - 1))
					current_start = None
					current_length = 0

			# Check final region
			if current_start is not None and current_length >= min_length:
				unused_regions.append((current_start, len(rom_data) - 1))

		return unused_regions

	@staticmethod
	def _find_patterns(rom_data: bytes) -> Dict:
		"""Find repeating patterns"""
		patterns = {
			'repeating_bytes': {},
			'repeating_words': {},
		}

		# Find repeating single bytes (RLE candidates)
		i = 0
		while i < len(rom_data):
			byte = rom_data[i]
			count = 1
			while i + count < len(rom_data) and rom_data[i + count] == byte:
				count += 1

			if count >= 16:  # Significant repetition
				if byte not in patterns['repeating_bytes']:
					patterns['repeating_bytes'][byte] = []
				patterns['repeating_bytes'][byte].append((i, count))

			i += count

		# Find repeating 2-byte patterns
		i = 0
		while i < len(rom_data) - 1:
			word = struct.unpack('<H', rom_data[i:i+2])[0]
			count = 1
			while i + count * 2 < len(rom_data) and rom_data[i + count * 2:i + (count + 1) * 2] == rom_data[i:i+2]:
				count += 1

			if count >= 8:
				if word not in patterns['repeating_words']:
					patterns['repeating_words'][word] = []
				patterns['repeating_words'][word].append((i, count))

			i += 2

		return patterns


class ROMValidatorGUI:
	"""GUI for ROM validation and analysis"""

	def __init__(self, master=None):
		self.master = master or tk.Tk()
		self.master.title("Dragon Warrior ROM Validator & Analyzer")
		self.master.geometry("900x700")

		self.rom_path = tk.StringVar()
		self.rom_data: Optional[bytes] = None
		self.validation_result: Optional[ValidationResult] = None
		self.analysis_result: Optional[Dict] = None

		self.setup_ui()

	def setup_ui(self):
		"""Setup GUI layout"""
		# Top panel: File selection
		top_frame = ttk.Frame(self.master)
		top_frame.pack(fill='x', padx=5, pady=5)

		ttk.Label(top_frame, text="ROM File:").pack(side='left', padx=5)
		ttk.Entry(top_frame, textvariable=self.rom_path, width=60).pack(side='left', padx=5)
		ttk.Button(top_frame, text="Browse...", command=self.browse_rom).pack(side='left', padx=5)
		ttk.Button(top_frame, text="Validate & Analyze", command=self.validate_and_analyze).pack(side='left', padx=10)

		# Notebook
		self.notebook = ttk.Notebook(self.master)
		self.notebook.pack(fill='both', expand=True, padx=5, pady=5)

		# Validation tab
		validation_frame = ttk.Frame(self.notebook)
		self.notebook.add(validation_frame, text='Validation')
		self.setup_validation_tab(validation_frame)

		# Analysis tab
		analysis_frame = ttk.Frame(self.notebook)
		self.notebook.add(analysis_frame, text='Analysis')
		self.setup_analysis_tab(analysis_frame)

		# Memory Map tab
		memmap_frame = ttk.Frame(self.notebook)
		self.notebook.add(memmap_frame, text='Memory Map')
		self.setup_memmap_tab(memmap_frame)

	def setup_validation_tab(self, parent):
		"""Setup Validation tab"""
		self.validation_text = scrolledtext.ScrolledText(parent, width=100, height=35, font=('Courier', 9))
		self.validation_text.pack(fill='both', expand=True, padx=5, pady=5)

		# Configure tags
		self.validation_text.tag_config('header', font=('Courier', 10, 'bold'), foreground='blue')
		self.validation_text.tag_config('success', foreground='green')
		self.validation_text.tag_config('warning', foreground='orange')
		self.validation_text.tag_config('error', foreground='red')

	def setup_analysis_tab(self, parent):
		"""Setup Analysis tab"""
		self.analysis_text = scrolledtext.ScrolledText(parent, width=100, height=35, font=('Courier', 9))
		self.analysis_text.pack(fill='both', expand=True, padx=5, pady=5)

	def setup_memmap_tab(self, parent):
		"""Setup Memory Map tab"""
		# Treeview for memory map
		columns = ('Offset', 'Size', 'Type', 'Description')
		self.memmap_tree = ttk.Treeview(parent, columns=columns, show='headings', height=30)

		self.memmap_tree.heading('Offset', text='Offset Range')
		self.memmap_tree.heading('Size', text='Size')
		self.memmap_tree.heading('Type', text='Type')
		self.memmap_tree.heading('Description', text='Description')

		self.memmap_tree.column('Offset', width=200)
		self.memmap_tree.column('Size', width=100)
		self.memmap_tree.column('Type', width=100)
		self.memmap_tree.column('Description', width=400)

		scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.memmap_tree.yview)
		self.memmap_tree.configure(yscrollcommand=scrollbar.set)

		self.memmap_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
		scrollbar.pack(side='right', fill='y', pady=5)

		# Populate with known memory map
		for region in ROMAnalyzer.DW_MEMORY_MAP:
			self.memmap_tree.insert('', 'end', values=(
				f"0x{region.start_offset:06X} - 0x{region.end_offset:06X}",
				f"{region.size:,} bytes",
				region.data_type.capitalize(),
				region.description
			))

	def browse_rom(self):
		filename = filedialog.askopenfilename(
			title="Select ROM File",
			filetypes=[("NES ROM", "*.nes"), ("All Files", "*.*")]
		)
		if filename:
			self.rom_path.set(filename)

	def validate_and_analyze(self):
		"""Validate and analyze ROM"""
		try:
			if not self.rom_path.get():
				messagebox.showerror("Error", "Please select a ROM file")
				return

			# Load ROM
			with open(self.rom_path.get(), 'rb') as f:
				self.rom_data = f.read()

			# Validate
			self.validation_result = ROMValidator.validate_rom(self.rom_data, self.rom_path.get())

			# Analyze
			self.analysis_result = ROMAnalyzer.analyze_rom(self.rom_data)

			# Update displays
			self.display_validation_results()
			self.display_analysis_results()

			# Show summary
			if self.validation_result.is_valid:
				messagebox.showinfo("Success", "✓ ROM validation passed!\n\nSee tabs for detailed results.")
			else:
				messagebox.showwarning("Validation Issues",
					f"⚠ ROM validation found {len(self.validation_result.issues)} issue(s)\n\n" +
					"See Validation tab for details.")

		except Exception as e:
			messagebox.showerror("Error", f"Failed to validate ROM:\n{e}")

	def display_validation_results(self):
		"""Display validation results"""
		if not self.validation_result:
			return

		text = self.validation_text
		text.delete('1.0', 'end')

		# Header
		text.insert('end', "=" * 80 + "\n", 'header')
		text.insert('end', "ROM VALIDATION REPORT\n", 'header')
		text.insert('end', "=" * 80 + "\n\n", 'header')

		text.insert('end', f"File: {os.path.basename(self.rom_path.get())}\n\n")

		# Overall status
		if self.validation_result.is_valid:
			text.insert('end', "✓ VALIDATION PASSED\n\n", 'success')
		else:
			text.insert('end', "✗ VALIDATION FAILED\n\n", 'error')

		# Issues
		if self.validation_result.issues:
			text.insert('end', f"ISSUES ({len(self.validation_result.issues)}):\n", 'error')
			for issue in self.validation_result.issues:
				text.insert('end', f"  {issue}\n", 'error')
			text.insert('end', "\n")

		# Warnings
		if self.validation_result.warnings:
			text.insert('end', f"WARNINGS ({len(self.validation_result.warnings)}):\n", 'warning')
			for warning in self.validation_result.warnings:
				text.insert('end', f"  {warning}\n", 'warning')
			text.insert('end', "\n")

		# Info
		if self.validation_result.info:
			text.insert('end', f"INFORMATION:\n")
			for info in self.validation_result.info:
				text.insert('end', f"  {info}\n")
			text.insert('end', "\n")

		text.insert('end', "=" * 80 + "\n")

	def display_analysis_results(self):
		"""Display analysis results"""
		if not self.analysis_result:
			return

		text = self.analysis_text
		text.delete('1.0', 'end')

		text.insert('end', "=" * 80 + "\n")
		text.insert('end', "ROM ANALYSIS REPORT\n")
		text.insert('end', "=" * 80 + "\n\n")

		# Byte distribution
		dist = self.analysis_result['byte_distribution']
		text.insert('end', "BYTE DISTRIBUTION:\n")
		text.insert('end', f"  Total bytes: {dist['total_bytes']:,}\n")
		text.insert('end', f"  Unique byte values: {dist['unique_bytes']}\n")
		text.insert('end', f"  Zero bytes (0x00): {dist['zero_bytes']:,} ({dist['zero_bytes']/dist['total_bytes']*100:.1f}%)\n")
		text.insert('end', f"  FF bytes (0xff): {dist['ff_bytes']:,} ({dist['ff_bytes']/dist['total_bytes']*100:.1f}%)\n")
		text.insert('end', f"  Entropy: {self.analysis_result['entropy']:.2f}\n\n")

		text.insert('end', "  Most common bytes:\n")
		for byte, count in dist['most_common']:
			text.insert('end', f"    0x{byte:02X}: {count:,} times ({count/dist['total_bytes']*100:.1f}%)\n")
		text.insert('end', "\n")

		# Unused space
		unused = self.analysis_result['unused_space']
		if unused:
			text.insert('end', f"UNUSED SPACE ({len(unused)} regions):\n")
			total_unused = sum(end - start + 1 for start, end in unused)
			text.insert('end', f"  Total unused: {total_unused:,} bytes ({total_unused/dist['total_bytes']*100:.1f}%)\n")
			for start, end in unused[:10]:  # Show first 10
				size = end - start + 1
				text.insert('end', f"    0x{start:06X} - 0x{end:06X}: {size:,} bytes\n")
			if len(unused) > 10:
				text.insert('end', f"    ... and {len(unused) - 10} more regions\n")
			text.insert('end', "\n")

		# Text regions
		text_regions = self.analysis_result['text_regions']
		if text_regions:
			text.insert('end', f"TEXT-LIKE REGIONS ({len(text_regions)} found):\n")
			for start, end, data in text_regions[:10]:  # Show first 10
				preview = data[:50].decode('ascii', errors='replace').replace('\n', '\\n')
				text.insert('end', f"    0x{start:06X}: \"{preview}...\"\n")
			if len(text_regions) > 10:
				text.insert('end', f"    ... and {len(text_regions) - 10} more regions\n")
			text.insert('end', "\n")

		text.insert('end', "=" * 80 + "\n")

	def run(self):
		"""Run the GUI"""
		self.master.mainloop()


def main():
	"""Main entry point"""
	app = ROMValidatorGUI()
	app.run()


if __name__ == '__main__':
	main()
