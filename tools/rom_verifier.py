#!/usr/bin/env python3
"""
Dragon Warrior ROM Verifier and Comparison Tool
Verifies built ROMs against reference ROMs and generates detailed matching reports
"""

import hashlib
import struct
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import json
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn
from rich import box

console = Console()

class ROMVerifier:
    """Comprehensive ROM verification and comparison system"""

    def __init__(self, reference_rom: str, built_rom: str, output_dir: str = "verification_reports"):
        self.reference_rom = Path(reference_rom)
        self.built_rom = Path(built_rom)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        # Known ROM segments for Dragon Warrior
        self.rom_segments = {
            "nes_header": (0x0000, 0x0010),
            "trainer": (0x0010, 0x0210),  # If present
            "prg_rom_bank0": (0x8010, 0xC000),
            "prg_rom_bank1": (0xC000, 0x10000),
            "chr_rom": (0x10000, 0x12000),
        }

        # Critical ROM areas that should match exactly
        self.critical_areas = {
            "nes_header": "NES header and ROM configuration",
            "reset_vector": (0xFFFC, 0xFFFE, "CPU reset vector"),
            "nmi_vector": (0xFFFA, 0xFFFC, "NMI interrupt vector"),
            "irq_vector": (0xFFFE, 0x10000, "IRQ interrupt vector"),
        }

    def verify_roms(self) -> Dict[str, Any]:
        """Complete ROM verification with detailed analysis"""
        console.print(Panel(
            "[bold cyan]ROM Verification and Comparison[/bold cyan]\n"
            f"Reference: [green]{self.reference_rom.name}[/green]\n"
            f"Built ROM: [yellow]{self.built_rom.name}[/yellow]",
            title="ROM Verifier",
            border_style="blue"
        ))

        if not self.reference_rom.exists():
            console.print(f"[red]Reference ROM not found: {self.reference_rom}[/red]")
            return {"error": "Reference ROM not found"}

        if not self.built_rom.exists():
            console.print(f"[red]Built ROM not found: {self.built_rom}[/red]")
            return {"error": "Built ROM not found"}

        # Load ROM data
        with open(self.reference_rom, 'rb') as f:
            ref_data = f.read()
        with open(self.built_rom, 'rb') as f:
            built_data = f.read()

        # Perform comprehensive verification
        verification_results = {
            "timestamp": datetime.now().isoformat(),
            "reference_rom": {
                "filename": self.reference_rom.name,
                "size": len(ref_data),
                "md5": hashlib.md5(ref_data).hexdigest(),
                "sha1": hashlib.sha1(ref_data).hexdigest(),
            },
            "built_rom": {
                "filename": self.built_rom.name,
                "size": len(built_data),
                "md5": hashlib.md5(built_data).hexdigest(),
                "sha1": hashlib.sha1(built_data).hexdigest(),
            },
            "comparison": self._compare_roms(ref_data, built_data),
            "segment_analysis": self._analyze_segments(ref_data, built_data),
            "critical_areas": self._check_critical_areas(ref_data, built_data),
            "differences": self._find_detailed_differences(ref_data, built_data),
            "match_percentage": self._calculate_match_percentage(ref_data, built_data)
        }

        # Generate reports
        self._generate_console_report(verification_results)
        self._generate_json_report(verification_results)
        self._generate_detailed_report(verification_results)

        return verification_results

    def _compare_roms(self, ref_data: bytes, built_data: bytes) -> Dict[str, Any]:
        """Basic ROM comparison"""
        return {
            "identical": ref_data == built_data,
            "size_match": len(ref_data) == len(built_data),
            "size_difference": len(built_data) - len(ref_data),
        }

    def _analyze_segments(self, ref_data: bytes, built_data: bytes) -> Dict[str, Dict[str, Any]]:
        """Analyze specific ROM segments"""
        segment_results = {}

        for segment_name, (start, end) in self.rom_segments.items():
            if start >= len(ref_data) or start >= len(built_data):
                continue

            ref_segment = ref_data[start:min(end, len(ref_data))]
            built_segment = built_data[start:min(end, len(built_data))]

            segment_results[segment_name] = {
                "start_offset": f"0x{start:04X}",
                "end_offset": f"0x{min(end, len(ref_data)):04X}",
                "size": len(ref_segment),
                "matches": ref_segment == built_segment,
                "differences": self._count_byte_differences(ref_segment, built_segment)
            }

            if ref_segment != built_segment:
                segment_results[segment_name]["first_difference"] = self._find_first_difference(ref_segment, built_segment, start)

        return segment_results

    def _check_critical_areas(self, ref_data: bytes, built_data: bytes) -> Dict[str, Dict[str, Any]]:
        """Check critical ROM areas that must match"""
        critical_results = {}

        for area_name, area_info in self.critical_areas.items():
            if area_name == "nes_header":
                start, end = 0, 16
                description = area_info
            else:
                start, end, description = area_info

            if start >= len(ref_data) or start >= len(built_data):
                continue

            ref_bytes = ref_data[start:end]
            built_bytes = built_data[start:end]

            critical_results[area_name] = {
                "description": description,
                "offset": f"0x{start:04X}-0x{end:04X}",
                "matches": ref_bytes == built_bytes,
                "reference_hex": ref_bytes.hex().upper(),
                "built_hex": built_bytes.hex().upper(),
            }

        return critical_results

    def _find_detailed_differences(self, ref_data: bytes, built_data: bytes) -> List[Dict[str, Any]]:
        """Find all differences between ROMs with context"""
        differences = []
        max_length = max(len(ref_data), len(built_data))
        current_diff = None

        for i in range(max_length):
            ref_byte = ref_data[i] if i < len(ref_data) else None
            built_byte = built_data[i] if i < len(built_data) else None

            if ref_byte != built_byte:
                if current_diff is None:
                    # Start new difference block
                    current_diff = {
                        "offset": f"0x{i:06X}",
                        "start_offset": i,
                        "reference_bytes": [],
                        "built_bytes": [],
                        "context_before": ref_data[max(0, i-8):i].hex().upper() if i > 0 else "",
                    }

                current_diff["reference_bytes"].append(f"{ref_byte:02X}" if ref_byte is not None else "??")
                current_diff["built_bytes"].append(f"{built_byte:02X}" if built_byte is not None else "??")
                current_diff["length"] = len(current_diff["reference_bytes"])

            else:
                if current_diff is not None:
                    # End current difference block
                    end_offset = current_diff["start_offset"] + current_diff["length"]
                    current_diff["context_after"] = ref_data[end_offset:end_offset+8].hex().upper()
                    current_diff["reference_hex"] = "".join(current_diff["reference_bytes"])
                    current_diff["built_hex"] = "".join(current_diff["built_bytes"])

                    differences.append(current_diff)
                    current_diff = None

        # Handle final difference if file ends with differences
        if current_diff is not None:
            end_offset = current_diff["start_offset"] + current_diff["length"]
            current_diff["context_after"] = ref_data[end_offset:end_offset+8].hex().upper() if end_offset < len(ref_data) else ""
            current_diff["reference_hex"] = "".join(current_diff["reference_bytes"])
            current_diff["built_hex"] = "".join(current_diff["built_bytes"])
            differences.append(current_diff)

        return differences[:100]  # Limit to first 100 differences for performance

    def _calculate_match_percentage(self, ref_data: bytes, built_data: bytes) -> float:
        """Calculate overall match percentage"""
        if len(ref_data) == 0 and len(built_data) == 0:
            return 100.0

        max_length = max(len(ref_data), len(built_data))
        matches = 0

        for i in range(max_length):
            ref_byte = ref_data[i] if i < len(ref_data) else None
            built_byte = built_data[i] if i < len(built_data) else None

            if ref_byte == built_byte:
                matches += 1

        return (matches / max_length) * 100.0

    def _count_byte_differences(self, data1: bytes, data2: bytes) -> int:
        """Count byte differences between two data blocks"""
        max_length = max(len(data1), len(data2))
        differences = 0

        for i in range(max_length):
            byte1 = data1[i] if i < len(data1) else None
            byte2 = data2[i] if i < len(data2) else None
            if byte1 != byte2:
                differences += 1

        return differences

    def _find_first_difference(self, data1: bytes, data2: bytes, base_offset: int = 0) -> Optional[Dict[str, str]]:
        """Find the first byte difference in two data blocks"""
        max_length = max(len(data1), len(data2))

        for i in range(max_length):
            byte1 = data1[i] if i < len(data1) else None
            byte2 = data2[i] if i < len(data2) else None

            if byte1 != byte2:
                return {
                    "offset": f"0x{base_offset + i:06X}",
                    "reference": f"{byte1:02X}" if byte1 is not None else "EOF",
                    "built": f"{byte2:02X}" if byte2 is not None else "EOF"
                }

        return None

    def _generate_console_report(self, results: Dict[str, Any]) -> None:
        """Generate console output report"""
        console.print("\n" + "="*80)
        console.print("[bold cyan]ROM Verification Results[/bold cyan]")
        console.print("="*80)

        # Overall status
        if results["comparison"]["identical"]:
            console.print("[bold green]ROMs ARE IDENTICAL[/bold green]")
            return

        match_pct = results["match_percentage"]
        if match_pct >= 99.0:
            status_color = "yellow"
            status_text = f"ROMs ARE {match_pct:.2f}% IDENTICAL"
        elif match_pct >= 95.0:
            status_color = "yellow"
            status_text = f"ROMs ARE {match_pct:.2f}% IDENTICAL"
        else:
            status_color = "red"
            status_text = f"ROMs ARE {match_pct:.2f}% IDENTICAL"

        console.print(f"[bold {status_color}]{status_text}[/bold {status_color}]")

        # Size comparison
        if results["comparison"]["size_match"]:
            console.print("[green]File sizes match[/green]")
        else:
            diff = results["comparison"]["size_difference"]
            console.print(f"[yellow]Size difference: {diff:+d} bytes[/yellow]")

        # Segment analysis table
        console.print("\n[bold]ROM Segment Analysis:[/bold]")
        table = Table(box=box.ROUNDED)
        table.add_column("Segment", style="cyan")
        table.add_column("Range", style="blue")
        table.add_column("Status", justify="center")
        table.add_column("Differences", justify="right", style="yellow")

        for segment_name, segment_info in results["segment_analysis"].items():
            status = "[green]Match[/green]" if segment_info["matches"] else "[red]Differ[/red]"
            diff_count = segment_info.get("differences", 0)

            table.add_row(
                segment_name.replace("_", " ").title(),
                f"{segment_info['start_offset']}-{segment_info['end_offset']}",
                status,
                str(diff_count) if diff_count > 0 else "-"
            )

        console.print(table)

        # Critical areas
        console.print("\n[bold]Critical Areas Check:[/bold]")
        for area_name, area_info in results["critical_areas"].items():
            status = "[green]PASS[/green]" if area_info["matches"] else "[red]FAIL[/red]"
            console.print(f"{status} {area_name}: {area_info['description']}")

        # Sample differences
        if results["differences"]:
            console.print(f"\n[bold]First 10 Differences:[/bold]")
            diff_table = Table(box=box.ROUNDED)
            diff_table.add_column("Offset", style="cyan")
            diff_table.add_column("Reference", style="green")
            diff_table.add_column("Built", style="red")
            diff_table.add_column("Length", justify="right")

            for diff in results["differences"][:10]:
                diff_table.add_row(
                    diff["offset"],
                    diff["reference_hex"][:16] + ("..." if len(diff["reference_hex"]) > 16 else ""),
                    diff["built_hex"][:16] + ("..." if len(diff["built_hex"]) > 16 else ""),
                    str(diff["length"])
                )

            console.print(diff_table)

            if len(results["differences"]) > 10:
                console.print(f"[dim]... and {len(results['differences']) - 10} more differences[/dim]")

    def _generate_json_report(self, results: Dict[str, Any]) -> Path:
        """Generate detailed JSON report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"verification_report_{timestamp}.json"

        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

        console.print(f"[dim]Detailed JSON report: {report_file}[/dim]")
        return report_file

    def _generate_detailed_report(self, results: Dict[str, Any]) -> Path:
        """Generate human-readable detailed report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"verification_detailed_{timestamp}.txt"

		with open(report_file, 'w', encoding='utf-8') as f:
			f.write("="*80 + "\n")
			f.write("Dragon Warrior ROM Verification Report\n")
			f.write("="*80 + "\n")
			f.write(f"Generated: {results['timestamp']}\n\n")
			
			f.write("REFERENCE ROM:\n")
			f.write(f"\tFile: {results['reference_rom']['filename']}\n")
			f.write(f"\tSize: {results['reference_rom']['size']:,} bytes\n")
			f.write(f"\tMD5:  {results['reference_rom']['md5']}\n")
			f.write(f"\tSHA1: {results['reference_rom']['sha1']}\n\n")
			
			f.write("BUILT ROM:\n")
			f.write(f"\tFile: {results['built_rom']['filename']}\n")
			f.write(f"\tSize: {results['built_rom']['size']:,} bytes\n")
			f.write(f"\tMD5:  {results['built_rom']['md5']}\n")
			f.write(f"\tSHA1: {results['built_rom']['sha1']}\n\n")
			
			f.write("COMPARISON RESULTS:\n")
			f.write(f"\tIdentical: {'YES' if results['comparison']['identical'] else 'NO'}\n")
			f.write(f"\tMatch Percentage: {results['match_percentage']:.2f}%\n")
			f.write(f"\tSize Difference: {results['comparison']['size_difference']:+d} bytes\n\n")
			
			f.write("SEGMENT ANALYSIS:\n")
			for segment_name, segment_info in results["segment_analysis"].items():
				f.write(f"\t{segment_name}:\n")
				f.write(f"\t\tRange: {segment_info['start_offset']}-{segment_info['end_offset']}\n")
				f.write(f"\t\tMatches: {'YES' if segment_info['matches'] else 'NO'}\n")
				f.write(f"\t\tDifferences: {segment_info.get('differences', 0)}\n")
				if 'first_difference' in segment_info:
					fd = segment_info['first_difference']
					f.write(f"\t\tFirst Diff: {fd['offset']} ({fd['reference']} -> {fd['built']})\n")
				f.write("\n")
			
			f.write("CRITICAL AREAS:\n")
			for area_name, area_info in results["critical_areas"].items():
				f.write(f"\t{area_name}: {'PASS' if area_info['matches'] else 'FAIL'}\n")
				f.write(f"\t\t{area_info['description']}\n")
				f.write(f"\t\tRange: {area_info['offset']}\n")
				if not area_info['matches']:
					f.write(f"\t\tReference: {area_info['reference_hex']}\n")
					f.write(f"\t\tBuilt:     {area_info['built_hex']}\n")
				f.write("\n")
			
			if results["differences"]:
				f.write("DETAILED DIFFERENCES:\n")
				for i, diff in enumerate(results["differences"], 1):
					f.write(f"\tDifference #{i}:\n")
					f.write(f"\t\tOffset: {diff['offset']} (length: {diff['length']})\n")
					f.write(f"\t\tContext: ...{diff['context_before']} [{diff['reference_hex']}] {diff['context_after']}...\n")
					f.write(f"\t\tReference: {diff['reference_hex']}\n")
					f.write(f"\t\tBuilt:     {diff['built_hex']}\n")
					f.write("\n")        console.print(f"[dim]Detailed text report: {report_file}[/dim]")
        return report_file


@click.command()
@click.argument('reference_rom', type=click.Path(exists=True))
@click.argument('built_rom', type=click.Path(exists=True))
@click.option('--output-dir', '-o', default='verification_reports', help='Output directory for reports')
@click.option('--json-only', is_flag=True, help='Generate only JSON report (no console output)')
def main(reference_rom: str, built_rom: str, output_dir: str, json_only: bool):
    """
    Dragon Warrior ROM Verifier

    Compare reference and built ROMs, generating detailed verification reports.

    REFERENCE_ROM: Path to the original/reference ROM file
    BUILT_ROM: Path to the built/modified ROM file
    """
    try:
        verifier = ROMVerifier(reference_rom, built_rom, output_dir)
        results = verifier.verify_roms()

        if json_only:
            # Suppress console output except for final JSON file path
            json_file = verifier._generate_json_report(results)
            print(str(json_file))

        # Debug: Check the actual comparison result
        comparison_identical = results.get("comparison", {}).get("identical", False)

        # Return 0 if ROMs are identical, 1 if different
        return 0 if comparison_identical else 1

    except Exception as e:
        console.print(f"[red]Error during verification: {e}[/red]")
        return 1


if __name__ == "__main__":
    exit(main())
