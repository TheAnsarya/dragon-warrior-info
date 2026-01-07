#!/usr/bin/env python3
"""
Advanced ROM Comparison and Diff Tool

Comprehensive ROM comparison with visual diff output, statistics, and analysis.
Identifies changes by category (code, data, graphics, text) and generates reports.

Features:
- Byte-by-byte comparison with context
- Change categorization (code/data/graphics/text)
- Visual hex diff output
- HTML diff report generation
- Change statistics and heatmap
- Automatic section detection
- Side-by-side comparison viewer
- Export to multiple formats (text, HTML, JSON, CSV)
- Integration with patch generators

Usage:
	python tools/rom_comparison_advanced.py ROM1 ROM2

Examples:
	# Basic comparison
	python tools/rom_comparison_advanced.py original.nes modified.nes

	# With detailed report
	python tools/rom_comparison_advanced.py original.nes modified.nes --report report.html

	# JSON export
	python tools/rom_comparison_advanced.py original.nes modified.nes --export changes.json

	# Compare specific section
	python tools/rom_comparison_advanced.py original.nes modified.nes --section graphics

	# Interactive mode
	python tools/rom_comparison_advanced.py --interactive

Author: Dragon Warrior ROM Hacking Toolkit
Version: 2.0
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
import struct
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Set
from dataclasses import dataclass, asdict, field
from enum import Enum
import argparse
import json
import csv
from datetime import datetime


class ChangeType(Enum):
	"""Type of ROM change."""
	CODE = "code"
	DATA = "data"
	GRAPHICS = "graphics"
	TEXT = "text"
	AUDIO = "audio"
	UNKNOWN = "unknown"


class SectionType(Enum):
	"""ROM section types."""
	HEADER = "header"
	PRG_ROM = "prg_rom"
	CHR_ROM = "chr_rom"
	TRAINER = "trainer"


@dataclass
class ChangeRecord:
	"""Record of a single change between ROMs."""
	offset: int
	original_value: int
	modified_value: int
	section: SectionType
	change_type: ChangeType
	context_before: bytes = field(default_factory=bytes)
	context_after: bytes = field(default_factory=bytes)
	description: str = ""


@dataclass
class ComparisonStats:
	"""Statistics about ROM comparison."""
	total_bytes: int
	changed_bytes: int
	unchanged_bytes: int
	percent_changed: float
	changes_by_type: Dict[str, int] = field(default_factory=dict)
	changes_by_section: Dict[str, int] = field(default_factory=dict)
	largest_change_block: int = 0
	change_clusters: List[Tuple[int, int]] = field(default_factory=list)


@dataclass
class ROMSection:
	"""ROM section definition."""
	name: str
	offset: int
	size: int
	section_type: SectionType
	change_type: ChangeType


# ============================================================================
# ROM STRUCTURE DEFINITIONS
# ============================================================================

class DragonWarriorROMLayout:
	"""Dragon Warrior ROM memory layout."""

	# iNES Header
	HEADER_OFFSET = 0x0000
	HEADER_SIZE = 0x0010

	# PRG-ROM (128 KB total)
	PRG_ROM_OFFSET = 0x0010
	PRG_ROM_SIZE = 0x20000

	# CHR-ROM (8 KB)
	CHR_ROM_OFFSET = 0x20010
	CHR_ROM_SIZE = 0x2000

	# Known data sections within PRG-ROM
	SECTIONS = [
		ROMSection("iNES Header", 0x0000, 0x0010, SectionType.HEADER, ChangeType.DATA),

		# Code sections
		ROMSection("Reset Vector", 0x0010, 0x0100, SectionType.PRG_ROM, ChangeType.CODE),
		ROMSection("Main Code Bank 0", 0x0110, 0x4000, SectionType.PRG_ROM, ChangeType.CODE),
		ROMSection("Main Code Bank 1", 0x4010, 0x4000, SectionType.PRG_ROM, ChangeType.CODE),

		# Data sections
		ROMSection("Monster Data", 0x5e5b, 0x0270, SectionType.PRG_ROM, ChangeType.DATA),
		ROMSection("Spell Data", 0x5f3b, 0x0050, SectionType.PRG_ROM, ChangeType.DATA),
		ROMSection("Item Data", 0x5f83, 0x0100, SectionType.PRG_ROM, ChangeType.DATA),

		# Text sections
		ROMSection("Dialog Text", 0x8000, 0x4000, SectionType.PRG_ROM, ChangeType.TEXT),
		ROMSection("Menu Text", 0xc000, 0x1000, SectionType.PRG_ROM, ChangeType.TEXT),

		# Graphics
		ROMSection("CHR-ROM Graphics", 0x20010, 0x2000, SectionType.CHR_ROM, ChangeType.GRAPHICS),

		# Audio
		ROMSection("Music Data", 0x1c000, 0x2000, SectionType.PRG_ROM, ChangeType.AUDIO),
	]

	@classmethod
	def identify_section(cls, offset: int) -> ROMSection:
		"""Identify which section an offset belongs to."""
		for section in cls.SECTIONS:
			if section.offset <= offset < section.offset + section.size:
				return section

		# Default to code if unknown
		if offset < cls.PRG_ROM_SIZE:
			return ROMSection("Unknown PRG", offset, 1, SectionType.PRG_ROM, ChangeType.CODE)
		else:
			return ROMSection("Unknown CHR", offset, 1, SectionType.CHR_ROM, ChangeType.GRAPHICS)


# ============================================================================
# ROM COMPARATOR
# ============================================================================

class ROMComparator:
	"""Compare two ROMs and analyze differences."""

	def __init__(self, context_bytes: int = 8):
		self.context_bytes = context_bytes
		self.changes: List[ChangeRecord] = []
		self.stats: Optional[ComparisonStats] = None

	def compare(self, rom1: bytes, rom2: bytes) -> List[ChangeRecord]:
		"""Compare two ROMs and find all differences."""
		self.changes = []

		# Ensure same length (pad with zeros if needed)
		max_len = max(len(rom1), len(rom2))
		if len(rom1) < max_len:
			rom1 = rom1 + b'\x00' * (max_len - len(rom1))
		if len(rom2) < max_len:
			rom2 = rom2 + b'\x00' * (max_len - len(rom2))

		# Find all differences
		for offset in range(max_len):
			if rom1[offset] != rom2[offset]:
				section = DragonWarriorROMLayout.identify_section(offset)

				# Get context
				context_start = max(0, offset - self.context_bytes)
				context_end = min(max_len, offset + self.context_bytes + 1)

				change = ChangeRecord(
					offset=offset,
					original_value=rom1[offset],
					modified_value=rom2[offset],
					section=section.section_type,
					change_type=section.change_type,
					context_before=rom1[context_start:offset],
					context_after=rom1[offset + 1:context_end],
					description=f"Changed in {section.name}"
				)

				self.changes.append(change)

		# Calculate statistics
		self._calculate_stats(len(rom1))

		return self.changes

	def _calculate_stats(self, total_bytes: int) -> None:
		"""Calculate comparison statistics."""
		changed_bytes = len(self.changes)
		unchanged_bytes = total_bytes - changed_bytes
		percent_changed = (changed_bytes / total_bytes * 100) if total_bytes > 0 else 0

		# Count by type
		changes_by_type = {}
		for change in self.changes:
			type_name = change.change_type.value
			changes_by_type[type_name] = changes_by_type.get(type_name, 0) + 1

		# Count by section
		changes_by_section = {}
		for change in self.changes:
			section_name = change.section.value
			changes_by_section[section_name] = changes_by_section.get(section_name, 0) + 1

		# Find change clusters
		clusters = self._find_clusters()

		# Find largest block
		largest_block = max([end - start for start, end in clusters], default=0)

		self.stats = ComparisonStats(
			total_bytes=total_bytes,
			changed_bytes=changed_bytes,
			unchanged_bytes=unchanged_bytes,
			percent_changed=percent_changed,
			changes_by_type=changes_by_type,
			changes_by_section=changes_by_section,
			largest_change_block=largest_block,
			change_clusters=clusters
		)

	def _find_clusters(self, max_gap: int = 16) -> List[Tuple[int, int]]:
		"""Find clusters of changes (groups separated by small gaps)."""
		if not self.changes:
			return []

		clusters = []
		cluster_start = self.changes[0].offset
		cluster_end = self.changes[0].offset

		for i in range(1, len(self.changes)):
			offset = self.changes[i].offset

			if offset - cluster_end <= max_gap:
				# Extend current cluster
				cluster_end = offset
			else:
				# Start new cluster
				clusters.append((cluster_start, cluster_end))
				cluster_start = offset
				cluster_end = offset

		# Add final cluster
		clusters.append((cluster_start, cluster_end))

		return clusters

	def get_changes_in_range(self, start: int, end: int) -> List[ChangeRecord]:
		"""Get all changes within an address range."""
		return [c for c in self.changes if start <= c.offset < end]

	def get_changes_by_type(self, change_type: ChangeType) -> List[ChangeRecord]:
		"""Get all changes of a specific type."""
		return [c for c in self.changes if c.change_type == change_type]


# ============================================================================
# DIFF VISUALIZERS
# ============================================================================

class TextDiffVisualizer:
	"""Generate text-based diff output."""

	def __init__(self):
		pass

	def format_change(self, change: ChangeRecord, show_context: bool = True) -> str:
		"""Format a single change for text output."""
		lines = []

		# Header
		lines.append(f"Offset: 0x{change.offset:06X} ({change.offset})")
		lines.append(f"Type: {change.change_type.value}, Section: {change.section.value}")
		lines.append(f"Change: 0x{change.original_value:02X} -> 0x{change.modified_value:02X}")

		if change.description:
			lines.append(f"Description: {change.description}")

		# Context (hex dump style)
		if show_context:
			lines.append("\nContext:")
			context = change.context_before + bytes([change.original_value]) + change.context_after

			hex_str = ' '.join(f'{b:02X}' for b in context)
			ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)

			lines.append(f"  {hex_str}")
			lines.append(f"  {ascii_str}")

			# Highlight changed byte
			changed_pos = len(change.context_before)
			highlight = ' ' * (changed_pos * 3) + '^^'
			lines.append(f"  {highlight}")

		return '\n'.join(lines)

	def format_summary(self, stats: ComparisonStats) -> str:
		"""Format comparison summary."""
		lines = []

		lines.append("=" * 70)
		lines.append("ROM COMPARISON SUMMARY")
		lines.append("=" * 70)

		lines.append(f"\nTotal bytes compared: {stats.total_bytes:,}")
		lines.append(f"Changed bytes: {stats.changed_bytes:,}")
		lines.append(f"Unchanged bytes: {stats.unchanged_bytes:,}")
		lines.append(f"Percentage changed: {stats.percent_changed:.2f}%")

		lines.append("\nChanges by Type:")
		for change_type, count in sorted(stats.changes_by_type.items()):
			lines.append(f"  {change_type.capitalize()}: {count:,} changes")

		lines.append("\nChanges by Section:")
		for section, count in sorted(stats.changes_by_section.items()):
			lines.append(f"  {section}: {count:,} changes")

		lines.append(f"\nLargest change block: {stats.largest_change_block:,} bytes")
		lines.append(f"Number of change clusters: {len(stats.change_clusters)}")

		if stats.change_clusters:
			lines.append("\nChange Clusters (first 10):")
			for start, end in stats.change_clusters[:10]:
				size = end - start + 1
				lines.append(f"  0x{start:06X}-0x{end:06X} ({size} bytes)")

		lines.append("=" * 70)

		return '\n'.join(lines)


class HTMLDiffVisualizer:
	"""Generate HTML diff report."""

	def __init__(self):
		self.html_template = """
<!DOCTYPE html>
<html>
<head>
	<title>ROM Comparison Report</title>
	<style>
		body {{
			font-family: 'Consolas', 'Monaco', monospace;
			margin: 20px;
			background-color: #1e1e1e;
			color: #d4d4d4;
		}}
		h1, h2, h3 {{
			color: #569cd6;
		}}
		.summary {{
			background-color: #252526;
			padding: 15px;
			border-radius: 5px;
			margin-bottom: 20px;
		}}
		.stats {{
			display: grid;
			grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
			gap: 10px;
			margin: 10px 0;
		}}
		.stat-box {{
			background-color: #2d2d30;
			padding: 10px;
			border-radius: 3px;
			border-left: 3px solid #569cd6;
		}}
		.stat-label {{
			color: #9cdcfe;
			font-size: 0.9em;
		}}
		.stat-value {{
			font-size: 1.5em;
			font-weight: bold;
			color: #ce9178;
		}}
		.change {{
			background-color: #252526;
			padding: 10px;
			margin: 10px 0;
			border-radius: 3px;
			border-left: 3px solid #ce9178;
		}}
		.change-header {{
			font-weight: bold;
			color: #4ec9b0;
			margin-bottom: 5px;
		}}
		.hex-context {{
			background-color: #1e1e1e;
			padding: 8px;
			margin: 5px 0;
			font-family: 'Consolas', monospace;
			overflow-x: auto;
		}}
		.changed-byte {{
			background-color: #f44747;
			color: white;
			padding: 2px 4px;
			border-radius: 2px;
		}}
		.type-badge {{
			display: inline-block;
			padding: 2px 8px;
			border-radius: 3px;
			font-size: 0.85em;
			margin-right: 5px;
		}}
		.type-code {{ background-color: #569cd6; color: white; }}
		.type-data {{ background-color: #4ec9b0; color: white; }}
		.type-graphics {{ background-color: #c586c0; color: white; }}
		.type-text {{ background-color: #ce9178; color: white; }}
		.type-audio {{ background-color: #dcdcaa; color: black; }}
		.type-unknown {{ background-color: #6a6a6a; color: white; }}
		.heatmap {{
			display: flex;
			flex-wrap: wrap;
			gap: 2px;
			margin: 10px 0;
		}}
		.heatmap-cell {{
			width: 4px;
			height: 20px;
			background-color: #2d2d30;
		}}
		.heatmap-cell.changed {{
			background-color: #f44747;
		}}
	</style>
</head>
<body>
	<h1>ROM Comparison Report</h1>
	<p>Generated: {timestamp}</p>

	<div class="summary">
		<h2>Summary</h2>
		<div class="stats">
			{stats_boxes}
		</div>
	</div>

	<div class="summary">
		<h2>Change Heatmap</h2>
		<div class="heatmap">
			{heatmap}
		</div>
	</div>

	<div>
		<h2>Detailed Changes</h2>
		{changes}
	</div>
</body>
</html>
		"""

	def generate_report(self, changes: List[ChangeRecord], stats: ComparisonStats,
						max_changes: int = 1000) -> str:
		"""Generate HTML report."""
		# Stats boxes
		stats_boxes = f"""
		<div class="stat-box">
			<div class="stat-label">Total Bytes</div>
			<div class="stat-value">{stats.total_bytes:,}</div>
		</div>
		<div class="stat-box">
			<div class="stat-label">Changed</div>
			<div class="stat-value">{stats.changed_bytes:,}</div>
		</div>
		<div class="stat-box">
			<div class="stat-label">Percent Changed</div>
			<div class="stat-value">{stats.percent_changed:.2f}%</div>
		</div>
		<div class="stat-box">
			<div class="stat-label">Change Clusters</div>
			<div class="stat-value">{len(stats.change_clusters)}</div>
		</div>
		"""

		# Heatmap (sample every 256 bytes)
		heatmap_cells = []
		changed_offsets = {c.offset for c in changes}

		for i in range(0, stats.total_bytes, 256):
			has_change = any(i <= offset < i + 256 for offset in changed_offsets)
			cell_class = "heatmap-cell changed" if has_change else "heatmap-cell"
			heatmap_cells.append(f'<div class="{cell_class}" title="0x{i:06X}"></div>')

		heatmap = '\n'.join(heatmap_cells)

		# Change details
		change_html = []
		for i, change in enumerate(changes[:max_changes]):
			type_class = f"type-{change.change_type.value}"

			hex_context = self._format_hex_context(change)

			change_html.append(f"""
			<div class="change">
				<div class="change-header">
					Change #{i + 1}: Offset 0x{change.offset:06X}
					<span class="type-badge {type_class}">{change.change_type.value.upper()}</span>
				</div>
				<div>
					<strong>Original:</strong> 0x{change.original_value:02X}
					→
					<strong>Modified:</strong> 0x{change.modified_value:02X}
				</div>
				<div>{change.description}</div>
				<div class="hex-context">{hex_context}</div>
			</div>
			""")

		if len(changes) > max_changes:
			change_html.append(f"""
			<div class="change">
				<p>... and {len(changes) - max_changes} more changes not shown</p>
			</div>
			""")

		return self.html_template.format(
			timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
			stats_boxes=stats_boxes,
			heatmap=heatmap,
			changes='\n'.join(change_html)
		)

	def _format_hex_context(self, change: ChangeRecord) -> str:
		"""Format hex context with highlighting."""
		context = change.context_before + bytes([change.original_value]) + change.context_after
		changed_pos = len(change.context_before)

		hex_parts = []
		for i, byte in enumerate(context):
			if i == changed_pos:
				hex_parts.append(f'<span class="changed-byte">{byte:02X}</span>')
			else:
				hex_parts.append(f'{byte:02X}')

		hex_str = ' '.join(hex_parts)
		ascii_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in context)

		return f"{hex_str}<br>{ascii_str}"


# ============================================================================
# EXPORT FORMATS
# ============================================================================

class DiffExporter:
	"""Export diff data in various formats."""

	@staticmethod
	def export_json(changes: List[ChangeRecord], stats: ComparisonStats,
				   filepath: str) -> None:
		"""Export to JSON format."""
		data = {
			'timestamp': datetime.now().isoformat(),
			'statistics': asdict(stats),
			'changes': [
				{
					'offset': c.offset,
					'offset_hex': f'0x{c.offset:06X}',
					'original_value': c.original_value,
					'modified_value': c.modified_value,
					'section': c.section.value,
					'type': c.change_type.value,
					'description': c.description
				}
				for c in changes
			]
		}

		with open(filepath, 'w') as f:
			json.dump(data, f, indent=2)

	@staticmethod
	def export_csv(changes: List[ChangeRecord], filepath: str) -> None:
		"""Export to CSV format."""
		with open(filepath, 'w', newline='') as f:
			writer = csv.writer(f)
			writer.writerow(['Offset', 'Offset (Hex)', 'Original', 'Modified',
							'Section', 'Type', 'Description'])

			for c in changes:
				writer.writerow([
					c.offset,
					f'0x{c.offset:06X}',
					f'0x{c.original_value:02X}',
					f'0x{c.modified_value:02X}',
					c.section.value,
					c.change_type.value,
					c.description
				])

	@staticmethod
	def export_text(changes: List[ChangeRecord], stats: ComparisonStats,
				   filepath: str) -> None:
		"""Export to text format."""
		visualizer = TextDiffVisualizer()

		with open(filepath, 'w') as f:
			# Summary
			f.write(visualizer.format_summary(stats))
			f.write('\n\n')

			# Changes
			f.write("=" * 70 + '\n')
			f.write("DETAILED CHANGES\n")
			f.write("=" * 70 + '\n\n')

			for i, change in enumerate(changes):
				f.write(f"--- Change #{i + 1} ---\n")
				f.write(visualizer.format_change(change))
				f.write('\n\n')


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Advanced ROM comparison and diff tool"
	)

	parser.add_argument('rom1', nargs='?', help="First ROM file")
	parser.add_argument('rom2', nargs='?', help="Second ROM file")

	parser.add_argument('--report', type=str, help="Generate HTML report")
	parser.add_argument('--export', type=str, help="Export to JSON file")
	parser.add_argument('--csv', type=str, help="Export to CSV file")
	parser.add_argument('--text', type=str, help="Export to text file")
	parser.add_argument('--section', type=str, help="Filter by section type")
	parser.add_argument('--type', type=str, help="Filter by change type")
	parser.add_argument('--max-changes', type=int, default=1000,
					   help="Maximum changes to display")
	parser.add_argument('--interactive', action='store_true',
					   help="Interactive mode")

	args = parser.parse_args()

	# Interactive mode
	if args.interactive or not all([args.rom1, args.rom2]):
		print("=== ROM Comparison Tool ===\n")
		rom1_path = input("First ROM path: ").strip()
		rom2_path = input("Second ROM path: ").strip()
	else:
		rom1_path = args.rom1
		rom2_path = args.rom2

	# Load ROMs
	try:
		with open(rom1_path, 'rb') as f:
			rom1 = f.read()
		with open(rom2_path, 'rb') as f:
			rom2 = f.read()
	except Exception as e:
		print(f"Error loading ROMs: {e}")
		return 1

	# Compare
	print(f"\nComparing ROMs...")
	print(f"  ROM 1: {rom1_path} ({len(rom1):,} bytes)")
	print(f"  ROM 2: {rom2_path} ({len(rom2):,} bytes)")

	comparator = ROMComparator()
	changes = comparator.compare(rom1, rom2)

	# Filter if requested
	if args.type:
		try:
			change_type = ChangeType(args.type)
			changes = comparator.get_changes_by_type(change_type)
			print(f"\nFiltered to {args.type} changes: {len(changes)}")
		except ValueError:
			print(f"Invalid change type: {args.type}")

	# Display summary
	visualizer = TextDiffVisualizer()
	print('\n' + visualizer.format_summary(comparator.stats))

	# Display sample changes
	print(f"\nSample changes (showing first 10):\n")
	for i, change in enumerate(changes[:10]):
		print(f"--- Change #{i + 1} ---")
		print(visualizer.format_change(change, show_context=True))
		print()

	if len(changes) > 10:
		print(f"... and {len(changes) - 10} more changes")

	# Generate reports
	if args.report:
		html_gen = HTMLDiffVisualizer()
		html_report = html_gen.generate_report(changes, comparator.stats, args.max_changes)
		with open(args.report, 'w') as f:
			f.write(html_report)
		print(f"\n✓ HTML report saved to: {args.report}")

	if args.export:
		DiffExporter.export_json(changes, comparator.stats, args.export)
		print(f"✓ JSON export saved to: {args.export}")

	if args.csv:
		DiffExporter.export_csv(changes, args.csv)
		print(f"✓ CSV export saved to: {args.csv}")

	if args.text:
		DiffExporter.export_text(changes, comparator.stats, args.text)
		print(f"✓ Text export saved to: {args.text}")

	return 0


if __name__ == "__main__":
	sys.exit(main())
