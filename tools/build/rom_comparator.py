#!/usr/bin/env python3
"""
Dragon Warrior Build System - ROM Comparator
Compare built ROM against reference with detailed reporting
Based on FFMQ comparison patterns
"""

import os
import sys
import struct
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track

console = Console()

class ROMComparator:
	"""Compare built ROM against reference ROM with detailed analysis"""
	
	def __init__(self, reference_rom: str, built_rom: str):
		self.reference_rom = Path(reference_rom)
		self.built_rom = Path(built_rom)
		
		if not self.reference_rom.exists():
			raise FileNotFoundError(f"Reference ROM not found: {reference_rom}")
		if not self.built_rom.exists():
			raise FileNotFoundError(f"Built ROM not found: {built_rom}")
		
		with open(self.reference_rom, 'rb') as f:
			self.ref_data = f.read()
		with open(self.built_rom, 'rb') as f:
			self.built_data = f.read()
		
		console.print(f"[green]Reference ROM: {self.reference_rom.name} ({len(self.ref_data)} bytes)[/green]")
		console.print(f"[green]Built ROM: {self.built_rom.name} ({len(self.built_data)} bytes)[/green]")
	
	def compare_roms(self) -> Dict[str, Any]:
		"""Perform comprehensive ROM comparison"""
		console.print("\n[blue]Performing detailed ROM comparison...[/blue]")
		
		comparison = {
			"reference_rom": str(self.reference_rom),
			"built_rom": str(self.built_rom),
			"reference_size": len(self.ref_data),
			"built_size": len(self.built_data),
			"size_match": len(self.ref_data) == len(self.built_data),
			"checksums": self._compare_checksums(),
			"byte_analysis": self._analyze_bytes(),
			"section_analysis": self._analyze_sections(),
			"differences": self._find_differences(),
			"match_percentage": 0.0,
			"match_report": {}
		}
		
		# Calculate overall match percentage
		if comparison["size_match"]:
			matching_bytes = comparison["byte_analysis"]["matching_bytes"]
			total_bytes = len(self.ref_data)
			comparison["match_percentage"] = (matching_bytes / total_bytes) * 100
		
		return comparison
	
	def _compare_checksums(self) -> Dict[str, str]:
		"""Compare ROM checksums"""
		return {
			"reference_md5": hashlib.md5(self.ref_data).hexdigest(),
			"built_md5": hashlib.md5(self.built_data).hexdigest(),
			"reference_sha1": hashlib.sha1(self.ref_data).hexdigest(),
			"built_sha1": hashlib.sha1(self.built_data).hexdigest(),
			"md5_match": hashlib.md5(self.ref_data).hexdigest() == hashlib.md5(self.built_data).hexdigest()
		}
	
	def _analyze_bytes(self) -> Dict[str, Any]:
		"""Analyze byte-by-byte differences"""
		if len(self.ref_data) != len(self.built_data):
			return {
				"error": "ROM sizes don't match",
				"matching_bytes": 0,
				"different_bytes": 0
			}
		
		matching = 0
		different = 0
		
		for i in range(len(self.ref_data)):
			if self.ref_data[i] == self.built_data[i]:
				matching += 1
			else:
				different += 1
		
		return {
			"total_bytes": len(self.ref_data),
			"matching_bytes": matching,
			"different_bytes": different,
			"match_percentage": (matching / len(self.ref_data)) * 100
		}
	
	def _analyze_sections(self) -> Dict[str, Any]:
		"""Analyze ROM sections (header, PRG, CHR)"""
		sections = {}
		
		# Header comparison (first 16 bytes)
		if len(self.ref_data) >= 16 and len(self.built_data) >= 16:
			ref_header = self.ref_data[:16]
			built_header = self.built_data[:16]
			
			sections["header"] = {
				"offset": 0,
				"size": 16,
				"matches": ref_header == built_header,
				"differences": self._find_section_differences(ref_header, built_header, 0)
			}
		
		# PRG-ROM comparison
		if len(self.ref_data) >= 16:
			header = self.ref_data[:16]
			if header[:4] == b'NES\x1a':  # Valid iNES header
				prg_size = header[4] * 16384
				
				if 16 + prg_size <= min(len(self.ref_data), len(self.built_data)):
					ref_prg = self.ref_data[16:16 + prg_size]
					built_prg = self.built_data[16:16 + prg_size]
					
					sections["prg_rom"] = {
						"offset": 16,
						"size": prg_size,
						"matches": ref_prg == built_prg,
						"differences": self._find_section_differences(ref_prg, built_prg, 16)
					}
				
				# CHR-ROM comparison (if present)
				chr_size = header[5] * 8192
				if chr_size > 0:
					chr_offset = 16 + prg_size
					if chr_offset + chr_size <= min(len(self.ref_data), len(self.built_data)):
						ref_chr = self.ref_data[chr_offset:chr_offset + chr_size]
						built_chr = self.built_data[chr_offset:chr_offset + chr_size]
						
						sections["chr_rom"] = {
							"offset": chr_offset,
							"size": chr_size,
							"matches": ref_chr == built_chr,
							"differences": self._find_section_differences(ref_chr, built_chr, chr_offset)
						}
		
		return sections
	
	def _find_section_differences(self, ref_data: bytes, built_data: bytes, base_offset: int) -> List[Dict[str, Any]]:
		"""Find differences in a specific section"""
		if len(ref_data) != len(built_data):
			return [{"error": "Section sizes don't match"}]
		
		differences = []
		current_diff = None
		
		for i in range(len(ref_data)):
			if ref_data[i] != built_data[i]:
				if current_diff is None:
					current_diff = {
						"start_offset": base_offset + i,
						"length": 1,
						"reference_bytes": [ref_data[i]],
						"built_bytes": [built_data[i]]
					}
				else:
					# Extend current difference
					current_diff["length"] += 1
					current_diff["reference_bytes"].append(ref_data[i])
					current_diff["built_bytes"].append(built_data[i])
			else:
				if current_diff is not None:
					# End current difference
					differences.append(current_diff)
					current_diff = None
		
		# Add final difference if exists
		if current_diff is not None:
			differences.append(current_diff)
		
		# Limit to first 50 differences to avoid huge reports
		return differences[:50]
	
	def _find_differences(self) -> List[Dict[str, Any]]:
		"""Find all byte-level differences"""
		if len(self.ref_data) != len(self.built_data):
			return [{"error": "ROM sizes don't match"}]
		
		return self._find_section_differences(self.ref_data, self.built_data, 0)
	
	def generate_report(self, comparison: Dict[str, Any], output_file: Optional[str] = None) -> str:
		"""Generate detailed comparison report"""
		report_lines = [
			"# Dragon Warrior ROM Comparison Report",
			f"**Generated:** {os.path.basename(__file__)}",
			f"**Reference ROM:** {comparison['reference_rom']}",
			f"**Built ROM:** {comparison['built_rom']}",
			"",
			"## Summary",
			f"- **Match Percentage:** {comparison['match_percentage']:.4f}%",
			f"- **Size Match:** {'✅ Yes' if comparison['size_match'] else '❌ No'}",
			f"- **MD5 Match:** {'✅ Yes' if comparison['checksums']['md5_match'] else '❌ No'}",
			""
		]
		
		# Size information
		report_lines.extend([
			"## Size Analysis",
			f"- **Reference Size:** {comparison['reference_size']:,} bytes",
			f"- **Built Size:** {comparison['built_size']:,} bytes",
			""
		])
		
		# Checksum information
		checksums = comparison["checksums"]
		report_lines.extend([
			"## Checksum Analysis",
			f"- **Reference MD5:** `{checksums['reference_md5']}`",
			f"- **Built MD5:** `{checksums['built_md5']}`",
			f"- **Reference SHA1:** `{checksums['reference_sha1']}`",
			f"- **Built SHA1:** `{checksums['built_sha1']}`",
			""
		])
		
		# Byte analysis
		if "byte_analysis" in comparison and "error" not in comparison["byte_analysis"]:
			ba = comparison["byte_analysis"]
			report_lines.extend([
				"## Byte-Level Analysis",
				f"- **Total Bytes:** {ba['total_bytes']:,}",
				f"- **Matching Bytes:** {ba['matching_bytes']:,}",
				f"- **Different Bytes:** {ba['different_bytes']:,}",
				f"- **Match Percentage:** {ba['match_percentage']:.4f}%",
				""
			])
		
		# Section analysis
		if "section_analysis" in comparison:
			report_lines.append("## Section Analysis")
			for section_name, section_data in comparison["section_analysis"].items():
				status = "✅ Match" if section_data["matches"] else "❌ Differ"
				diff_count = len(section_data.get("differences", []))
				report_lines.append(f"- **{section_name.upper()}:** {status} ({diff_count} difference blocks)")
			report_lines.append("")
		
		# Differences (first 10)
		if "differences" in comparison and comparison["differences"]:
			report_lines.extend([
				"## First 10 Differences",
				"| Offset | Length | Reference | Built |",
				"|--------|---------|-----------|-------|"
			])
			
			for diff in comparison["differences"][:10]:
				if "error" not in diff:
					offset = f"0x{diff['start_offset']:08X}"
					length = diff['length']
					ref_hex = ' '.join(f"{b:02X}" for b in diff['reference_bytes'][:8])
					built_hex = ' '.join(f"{b:02X}" for b in diff['built_bytes'][:8])
					if diff['length'] > 8:
						ref_hex += "..."
						built_hex += "..."
					
					report_lines.append(f"| {offset} | {length} | {ref_hex} | {built_hex} |")
			
			report_lines.append("")
		
		report_text = "\n".join(report_lines)
		
		if output_file:
			output_path = Path(output_file)
			output_path.parent.mkdir(parents=True, exist_ok=True)
			
			with open(output_path, 'w', encoding='utf-8') as f:
				f.write(report_text)
			
			console.print(f"[green]Report saved to: {output_path}[/green]")
		
		return report_text
	
	def display_summary(self, comparison: Dict[str, Any]):
		"""Display comparison summary in console"""
		
		# Overall status
		if comparison["match_percentage"] == 100.0:
			status = "[green]PERFECT MATCH[/green]"
		elif comparison["match_percentage"] >= 99.0:
			status = "[yellow]NEAR PERFECT[/yellow]"
		elif comparison["match_percentage"] >= 90.0:
			status = "[orange3]GOOD MATCH[/orange3]"
		else:
			status = "[red]SIGNIFICANT DIFFERENCES[/red]"
		
		console.print(Panel.fit(
			f"ROM Comparison: {status}\n"
			f"Match Percentage: [bold]{comparison['match_percentage']:.4f}%[/bold]",
			border_style="blue",
			title="Comparison Result"
		))
		
		# Summary table
		table = Table(title="ROM Comparison Summary")
		table.add_column("Metric", style="cyan", no_wrap=True)
		table.add_column("Reference", style="green")
		table.add_column("Built", style="blue")
		table.add_column("Match", style="bold")
		
		table.add_row(
			"Size",
			f"{comparison['reference_size']:,} bytes",
			f"{comparison['built_size']:,} bytes",
			"✅" if comparison['size_match'] else "❌"
		)
		
		checksums = comparison["checksums"]
		table.add_row(
			"MD5",
			checksums['reference_md5'][:16] + "...",
			checksums['built_md5'][:16] + "...",
			"✅" if checksums['md5_match'] else "❌"
		)
		
		if "byte_analysis" in comparison and "error" not in comparison["byte_analysis"]:
			ba = comparison["byte_analysis"]
			table.add_row(
				"Bytes",
				f"{ba['matching_bytes']:,}/{ba['total_bytes']:,}",
				f"{ba['different_bytes']:,} different",
				f"{ba['match_percentage']:.2f}%"
			)
		
		console.print(table)

@click.command()
@click.argument('reference_rom', type=click.Path(exists=True))
@click.argument('built_rom', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output report file')
@click.option('--json-output', help='JSON output file for build system')
def compare_roms(reference_rom: str, built_rom: str, output: Optional[str], json_output: Optional[str]):
	"""Compare built ROM against reference ROM"""
	
	console.print("[bold blue]Dragon Warrior ROM Comparator[/bold blue]\n")
	
	try:
		comparator = ROMComparator(reference_rom, built_rom)
		comparison = comparator.compare_roms()
		
		# Display summary
		comparator.display_summary(comparison)
		
		# Generate reports
		if output:
			comparator.generate_report(comparison, output)
		
		if json_output:
			with open(json_output, 'w', encoding='utf-8') as f:
				json.dump(comparison, f, indent=2)
			console.print(f"[green]JSON data saved to: {json_output}[/green]")
		
		# Exit with appropriate code
		if comparison["match_percentage"] == 100.0:
			console.print("\n[green]✅ Perfect match![/green]")
			sys.exit(0)
		else:
			console.print(f"\n[yellow]⚠️  {comparison['match_percentage']:.4f}% match[/yellow]")
			sys.exit(1 if comparison["match_percentage"] < 90.0 else 0)
		
	except Exception as e:
		console.print(f"[red]Error: {e}[/red]")
		sys.exit(1)

if __name__ == "__main__":
	compare_roms()