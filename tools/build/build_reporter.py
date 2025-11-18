#!/usr/bin/env python3
"""
Dragon Warrior Build Reporter
Generate comprehensive build reports with asset analysis and ROM comparison
"""

import os
import sys
import json
import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

console = Console()

class BuildReporter:
	"""Generate comprehensive build reports"""

	def __init__(self, build_dir: str):
		self.build_dir = Path(build_dir)
		self.reports_dir = self.build_dir / "reports"
		self.reports_dir.mkdir(parents=True, exist_ok=True)

	def collect_build_data(self) -> Dict[str, Any]:
		"""Collect all build-related data"""

		build_data = {
			"timestamp": datetime.datetime.now().isoformat(),
			"build_directory": str(self.build_dir),
			"files": self._scan_build_files(),
			"rom_comparison": self._load_rom_comparison(),
			"asset_analysis": self._analyze_assets(),
			"build_logs": self._collect_build_logs()
		}

		return build_data

	def _scan_build_files(self) -> Dict[str, Any]:
		"""Scan build directory for files"""
		files = {}

		for file_path in self.build_dir.rglob("*"):
			if file_path.is_file():
				rel_path = file_path.relative_to(self.build_dir)
				size = file_path.stat().st_size

				files[str(rel_path)] = {
					"path": str(file_path),
					"size": size,
					"extension": file_path.suffix.lower()
				}

		return files

	def _load_rom_comparison(self) -> Optional[Dict[str, Any]]:
		"""Load ROM comparison data if available"""
		comparison_file = self.reports_dir / "rom_comparison.json"

		if comparison_file.exists():
			try:
				with open(comparison_file, 'r', encoding='utf-8') as f:
					return json.load(f)
			except Exception as e:
				console.print(f"[yellow]Warning: Could not load ROM comparison: {e}[/yellow]")

		return None

	def _analyze_assets(self) -> Dict[str, Any]:
		"""Analyze extracted assets"""
		asset_analysis = {
			"extracted_files": 0,
			"total_size": 0,
			"file_types": {}
		}

		assets_dir = self.build_dir.parent / "assets"
		if assets_dir.exists():
			for file_path in assets_dir.rglob("*"):
				if file_path.is_file():
					asset_analysis["extracted_files"] += 1
					size = file_path.stat().st_size
					asset_analysis["total_size"] += size

					ext = file_path.suffix.lower()
					if ext not in asset_analysis["file_types"]:
						asset_analysis["file_types"][ext] = {"count": 0, "total_size": 0}

					asset_analysis["file_types"][ext]["count"] += 1
					asset_analysis["file_types"][ext]["total_size"] += size

		return asset_analysis

	def _collect_build_logs(self) -> List[str]:
		"""Collect build log entries"""
		log_file = self.build_dir / "build.log"

		if log_file.exists():
			try:
				with open(log_file, 'r', encoding='utf-8') as f:
					return f.readlines()
			except Exception:
				pass

		return []

	def generate_html_report(self, build_data: Dict[str, Any]) -> str:
		"""Generate HTML report"""

		html_content = f"""<!DOCTYPE html>
<html>
<head>
	<title>Dragon Warrior Build Report</title>
	<style>
		body {{ font-family: Arial, sans-serif; margin: 20px; }}
		.header {{ background: #2c3e50; color: white; padding: 20px; border-radius: 8px; }}
		.section {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 8px; }}
		.success {{ background: #d4edda; border-color: #c3e6cb; }}
		.warning {{ background: #fff3cd; border-color: #ffeaa7; }}
		.error {{ background: #f8d7da; border-color: #f5c6cb; }}
		table {{ width: 100%; border-collapse: collapse; }}
		th, td {{ padding: 10px; border: 1px solid #ddd; text-align: left; }}
		th {{ background: #f8f9fa; }}
		.percentage {{ font-weight: bold; font-size: 1.2em; }}
	</style>
</head>
<body>
	<div class="header">
		<h1>🐲 Dragon Warrior Build Report</h1>
		<p>Generated: {build_data['timestamp']}</p>
		<p>Build Directory: {build_data['build_directory']}</p>
	</div>
"""

		# ROM Comparison Section
		rom_comparison = build_data.get("rom_comparison")
		if rom_comparison:
			match_percent = rom_comparison.get("match_percentage", 0)

			if match_percent == 100:
				section_class = "success"
				status = "✅ PERFECT MATCH"
			elif match_percent >= 99:
				section_class = "warning"
				status = "⚠️ NEAR PERFECT"
			else:
				section_class = "error"
				status = "❌ SIGNIFICANT DIFFERENCES"

			html_content += f"""
	<div class="section {section_class}">
		<h2>🔍 ROM Comparison</h2>
		<div class="percentage">{status}: {match_percent:.4f}%</div>

		<table>
			<tr><th>Metric</th><th>Reference</th><th>Built</th><th>Match</th></tr>
			<tr>
				<td>Size</td>
				<td>{rom_comparison['reference_size']:,} bytes</td>
				<td>{rom_comparison['built_size']:,} bytes</td>
				<td>{'✅' if rom_comparison['size_match'] else '❌'}</td>
			</tr>
			<tr>
				<td>MD5</td>
				<td>{rom_comparison['checksums']['reference_md5'][:16]}...</td>
				<td>{rom_comparison['checksums']['built_md5'][:16]}...</td>
				<td>{'✅' if rom_comparison['checksums']['md5_match'] else '❌'}</td>
			</tr>
		</table>
	</div>
"""

		# Asset Analysis Section
		asset_analysis = build_data.get("asset_analysis", {})
		if asset_analysis.get("extracted_files", 0) > 0:
			html_content += f"""
	<div class="section">
		<h2>📦 Asset Analysis</h2>
		<p><strong>Extracted Files:</strong> {asset_analysis['extracted_files']}</p>
		<p><strong>Total Size:</strong> {asset_analysis['total_size']:,} bytes</p>

		<table>
			<tr><th>File Type</th><th>Count</th><th>Size</th></tr>
"""

			for ext, data in asset_analysis.get("file_types", {}).items():
				html_content += f"""
			<tr>
				<td>{ext or 'No extension'}</td>
				<td>{data['count']}</td>
				<td>{data['total_size']:,} bytes</td>
			</tr>
"""

			html_content += """
		</table>
	</div>
"""

		# Build Files Section
		build_files = build_data.get("files", {})
		if build_files:
			html_content += f"""
	<div class="section">
		<h2>📁 Build Files</h2>
		<p><strong>Total Files:</strong> {len(build_files)}</p>

		<table>
			<tr><th>File</th><th>Size</th><th>Type</th></tr>
"""

			for filename, file_data in sorted(build_files.items()):
				html_content += f"""
			<tr>
				<td>{filename}</td>
				<td>{file_data['size']:,} bytes</td>
				<td>{file_data['extension'] or 'No extension'}</td>
			</tr>
"""

			html_content += """
		</table>
	</div>
"""

		html_content += """
</body>
</html>
"""

		return html_content

	def generate_markdown_report(self, build_data: Dict[str, Any]) -> str:
		"""Generate Markdown report"""

		report_lines = [
			"# 🐲 Dragon Warrior Build Report",
			f"**Generated:** {build_data['timestamp']}",
			f"**Build Directory:** {build_data['build_directory']}",
			""
		]

		# ROM Comparison
		rom_comparison = build_data.get("rom_comparison")
		if rom_comparison:
			match_percent = rom_comparison.get("match_percentage", 0)

			if match_percent == 100:
				status = "✅ PERFECT MATCH"
			elif match_percent >= 99:
				status = "⚠️ NEAR PERFECT"
			else:
				status = "❌ SIGNIFICANT DIFFERENCES"

			report_lines.extend([
				"## 🔍 ROM Comparison",
				f"**Status:** {status}",
				f"**Match Percentage:** {match_percent:.4f}%",
				"",
				"| Metric | Reference | Built | Match |",
				"|--------|-----------|-------|-------|",
				f"| Size | {rom_comparison['reference_size']:,} bytes | {rom_comparison['built_size']:,} bytes | {'✅' if rom_comparison['size_match'] else '❌'} |",
				f"| MD5 | {rom_comparison['checksums']['reference_md5'][:16]}... | {rom_comparison['checksums']['built_md5'][:16]}... | {'✅' if rom_comparison['checksums']['md5_match'] else '❌'} |",
				""
			])

		# Asset Analysis
		asset_analysis = build_data.get("asset_analysis", {})
		if asset_analysis.get("extracted_files", 0) > 0:
			report_lines.extend([
				"## 📦 Asset Analysis",
				f"- **Extracted Files:** {asset_analysis['extracted_files']}",
				f"- **Total Size:** {asset_analysis['total_size']:,} bytes",
				"",
				"| File Type | Count | Size |",
				"|-----------|--------|------|"
			])

			for ext, data in asset_analysis.get("file_types", {}).items():
				ext_display = ext if ext else "No extension"
				report_lines.append(f"| {ext_display} | {data['count']} | {data['total_size']:,} bytes |")

			report_lines.append("")

		# Build Files
		build_files = build_data.get("files", {})
		if build_files:
			report_lines.extend([
				"## 📁 Build Files",
				f"**Total Files:** {len(build_files)}",
				"",
				"| File | Size | Type |",
				"|------|------|------|"
			])

			for filename, file_data in sorted(build_files.items()):
				ext_display = file_data['extension'] if file_data['extension'] else "No extension"
				report_lines.append(f"| {filename} | {file_data['size']:,} bytes | {ext_display} |")

		return "\n".join(report_lines)

	def save_report(self, build_data: Dict[str, Any], format_type: str = "both") -> List[str]:
		"""Save build report in specified format(s)"""

		saved_files = []

		if format_type in ("markdown", "both"):
			markdown_content = self.generate_markdown_report(build_data)
			markdown_file = self.reports_dir / "build_report.md"

			with open(markdown_file, 'w', encoding='utf-8') as f:
				f.write(markdown_content)

			saved_files.append(str(markdown_file))

		if format_type in ("html", "both"):
			html_content = self.generate_html_report(build_data)
			html_file = self.reports_dir / "build_report.html"

			with open(html_file, 'w', encoding='utf-8') as f:
				f.write(html_content)

			saved_files.append(str(html_file))

		# Always save JSON data
		json_file = self.reports_dir / "build_data.json"
		with open(json_file, 'w', encoding='utf-8') as f:
			json.dump(build_data, f, indent=2)

		saved_files.append(str(json_file))

		return saved_files

@click.command()
@click.argument('build_dir', type=click.Path(exists=True))
@click.option('--format', 'format_type', type=click.Choice(['markdown', 'html', 'both']), default='both')
def generate_report(build_dir: str, format_type: str):
	"""Generate comprehensive build report"""

	console.print("[bold blue]Dragon Warrior Build Reporter[/bold blue]\n")

	try:
		reporter = BuildReporter(build_dir)

		console.print("📊 Collecting build data...")
		build_data = reporter.collect_build_data()

		console.print("📝 Generating reports...")
		saved_files = reporter.save_report(build_data, format_type)

		console.print("\n[green]✅ Reports generated:[/green]")
		for file_path in saved_files:
			console.print(f"   📄 {file_path}")

		# Display summary
		rom_comparison = build_data.get("rom_comparison")
		if rom_comparison:
			match_percent = rom_comparison.get("match_percentage", 0)
			if match_percent == 100:
				console.print(f"\n[green]🎯 ROM Match: PERFECT ({match_percent:.4f}%)[/green]")
			elif match_percent >= 99:
				console.print(f"\n[yellow]⚠️  ROM Match: Near Perfect ({match_percent:.4f}%)[/yellow]")
			else:
				console.print(f"\n[red]❌ ROM Match: Significant Differences ({match_percent:.4f}%)[/red]")

	except Exception as e:
		console.print(f"[red]Error: {e}[/red]")
		sys.exit(1)

if __name__ == "__main__":
	generate_report()
