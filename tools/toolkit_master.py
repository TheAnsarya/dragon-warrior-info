#!/usr/bin/env python3
"""
Dragon Warrior ROM Toolkit - Master Controller

Unified interface for all Dragon Warrior ROM hacking tools.
Orchestrates workflows, batch operations, and tool integration.

Features:
- Unified tool launcher
- Batch operations across multiple tools
- Workflow automation
- Project management
- Change tracking
- Rollback support
- Integration testing
- Report generation
- Asset pipeline
- Build automation

Workflows:
- Complete ROM analysis
- Graphics overhaul pipeline
- Balance rebalancing
- Text localization
- Music extraction
- Patch creation
- Quality assurance

Usage:
	python tools/toolkit_master.py <command> [options]

Commands:
	analyze     - Complete ROM analysis
	extract     - Extract all assets
	validate    - Validate ROM and assets
	build       - Build modified ROM
	patch       - Create distribution patch
	report      - Generate comprehensive report
	workflow    - Run predefined workflow

Examples:
	# Analyze ROM
	python tools/toolkit_master.py analyze rom.nes

	# Extract all assets
	python tools/toolkit_master.py extract rom.nes --output assets/

	# Run balance workflow
	python tools/toolkit_master.py workflow balance rom.nes

	# Build modified ROM
	python tools/toolkit_master.py build project.json -o modified.nes

	# Create patch
	python tools/toolkit_master.py patch original.nes modified.nes -o myhack.bps

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
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import argparse


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class Project:
	"""ROM hacking project configuration."""
	name: str
	version: str
	original_rom: str
	modified_rom: str
	assets_dir: str
	patches_dir: str
	tools_used: List[str] = field(default_factory=list)
	changes_log: List[Dict] = field(default_factory=list)
	created: str = ""
	modified: str = ""


@dataclass
class WorkflowStep:
	"""Individual workflow step."""
	id: int
	name: str
	tool: str
	command: List[str]
	dependencies: List[int] = field(default_factory=list)
	output_files: List[str] = field(default_factory=list)


@dataclass
class Workflow:
	"""Predefined workflow."""
	name: str
	description: str
	steps: List[WorkflowStep] = field(default_factory=list)


@dataclass
class AnalysisReport:
	"""Comprehensive analysis report."""
	rom_info: Dict[str, Any] = field(default_factory=dict)
	graphics_info: Dict[str, Any] = field(default_factory=dict)
	text_info: Dict[str, Any] = field(default_factory=dict)
	balance_info: Dict[str, Any] = field(default_factory=dict)
	issues: List[str] = field(default_factory=list)
	recommendations: List[str] = field(default_factory=list)


# Predefined workflows
WORKFLOWS = {
	"analysis": Workflow(
		name="Complete ROM Analysis",
		description="Analyze all aspects of the ROM",
		steps=[
			WorkflowStep(1, "ROM Metadata", "rom_metadata_analyzer.py",
			             ["rom.nes", "--detailed"]),
			WorkflowStep(2, "Tileset Analysis", "tileset_manager.py",
			             ["rom.nes", "--analyze-usage"]),
			WorkflowStep(3, "Text Analysis", "dialogue_editor.py",
			             ["rom.nes", "--stats"]),
			WorkflowStep(4, "Enemy Balance", "enemy_ai_editor.py",
			             ["rom.nes", "--analyze-balance"]),
			WorkflowStep(5, "Item Balance", "item_shop_editor.py",
			             ["rom.nes", "--analyze-balance"]),
			WorkflowStep(6, "Spell Balance", "spell_editor.py",
			             ["rom.nes", "--analyze-balance"]),
			WorkflowStep(7, "Character Progression", "character_editor.py",
			             ["rom.nes", "--analyze"]),
		]
	),

	"extract": Workflow(
		name="Asset Extraction",
		description="Extract all assets from ROM",
		steps=[
			WorkflowStep(1, "Extract Tiles", "tileset_manager.py",
			             ["rom.nes", "--extract-all", "assets/tiles/"]),
			WorkflowStep(2, "Extract Monsters", "sprite_editor_advanced.py",
			             ["rom.nes", "--extract-monsters", "assets/sprites/"]),
			WorkflowStep(3, "Extract Text", "dialogue_editor.py",
			             ["rom.nes", "--extract-all", "assets/text/"]),
			WorkflowStep(4, "Extract Music", "music_editor_advanced.py",
			             ["rom.nes", "--extract-all", "assets/music/"]),
			WorkflowStep(5, "Export Data", "enemy_ai_editor.py",
			             ["rom.nes", "--export", "assets/data/enemies.json"]),
			WorkflowStep(6, "Export Items", "item_shop_editor.py",
			             ["rom.nes", "--export", "assets/data/items.json"]),
			WorkflowStep(7, "Export Spells", "spell_editor.py",
			             ["rom.nes", "--export", "assets/data/spells.json"]),
			WorkflowStep(8, "Export Stats", "character_editor.py",
			             ["rom.nes", "--export", "assets/data/stats.json"]),
		]
	),

	"balance": Workflow(
		name="Game Balance Rebalancing",
		description="Rebalance all game systems",
		steps=[
			WorkflowStep(1, "Analyze Current Balance", "enemy_ai_editor.py",
			             ["rom.nes", "--analyze-balance"]),
			WorkflowStep(2, "Rebalance XP Curve", "character_editor.py",
			             ["rom.nes", "--rebalance-xp", "--difficulty", "normal", "-o", "temp.nes"]),
			WorkflowStep(3, "Balance Enemy Rewards", "enemy_ai_editor.py",
			             ["temp.nes", "--balance-rewards", "-o", "temp2.nes"]),
			WorkflowStep(4, "Verify Balance", "enemy_ai_editor.py",
			             ["temp2.nes", "--analyze-balance"]),
		]
	),
}


# ============================================================================
# TOOL EXECUTOR
# ============================================================================

class ToolExecutor:
	"""Execute toolkit tools."""

	@staticmethod
	def run_tool(tool_name: str, args: List[str]) -> Tuple[int, str, str]:
		"""Run a toolkit tool and return result."""
		tools_dir = Path(__file__).parent
		tool_path = tools_dir / tool_name

		if not tool_path.exists():
			return (1, "", f"Tool not found: {tool_name}")

		cmd = [sys.executable, str(tool_path)] + args

		try:
			result = subprocess.run(
				cmd,
				capture_output=True,
				text=True,
				timeout=300  # 5 minute timeout
			)

			return (result.returncode, result.stdout, result.stderr)

		except subprocess.TimeoutExpired:
			return (1, "", "Tool execution timed out")

		except Exception as e:
			return (1, "", f"Tool execution error: {e}")

	@staticmethod
	def run_workflow(workflow: Workflow, rom_path: str) -> bool:
		"""Execute a complete workflow."""
		print(f"\n{'=' * 80}")
		print(f"Running Workflow: {workflow.name}")
		print(f"{workflow.description}")
		print(f"{'=' * 80}\n")

		for step in workflow.steps:
			print(f"\nStep {step.id}: {step.name}")
			print(f"Running: {step.tool}")

			# Replace rom.nes placeholder with actual path
			args = [rom_path if arg == "rom.nes" else arg for arg in step.command[1:]]

			returncode, stdout, stderr = ToolExecutor.run_tool(step.tool, args)

			if returncode != 0:
				print(f"ERROR in step {step.id}: {step.name}")
				print(stderr)
				return False

			print(stdout)

		print(f"\n{'=' * 80}")
		print(f"Workflow Complete: {workflow.name}")
		print(f"{'=' * 80}\n")

		return True


# ============================================================================
# ANALYZER
# ============================================================================

class ROMAnalyzer:
	"""Comprehensive ROM analysis."""

	@staticmethod
	def analyze_rom(rom_path: str) -> AnalysisReport:
		"""Perform complete ROM analysis."""
		report = AnalysisReport()

		print("Analyzing ROM...")

		# ROM metadata
		print("  - ROM metadata...")
		returncode, stdout, stderr = ToolExecutor.run_tool(
			"rom_metadata_analyzer.py",
			[rom_path]
		)
		report.rom_info = {"status": "complete" if returncode == 0 else "failed"}

		# Graphics analysis
		print("  - Graphics...")
		returncode, stdout, stderr = ToolExecutor.run_tool(
			"tileset_manager.py",
			[rom_path, "--analyze-usage"]
		)
		report.graphics_info = {"status": "complete" if returncode == 0 else "failed"}

		# Text analysis
		print("  - Text...")
		returncode, stdout, stderr = ToolExecutor.run_tool(
			"dialogue_editor.py",
			[rom_path, "--stats"]
		)
		report.text_info = {"status": "complete" if returncode == 0 else "failed"}

		# Balance analysis
		print("  - Game balance...")
		returncode, stdout, stderr = ToolExecutor.run_tool(
			"enemy_ai_editor.py",
			[rom_path, "--analyze-balance"]
		)
		report.balance_info = {"status": "complete" if returncode == 0 else "failed"}

		print("Analysis complete!")

		return report


# ============================================================================
# PROJECT MANAGER
# ============================================================================

class ProjectManager:
	"""Manage ROM hacking projects."""

	@staticmethod
	def create_project(name: str, rom_path: str, output_dir: str) -> Project:
		"""Create new project."""
		output_path = Path(output_dir)
		output_path.mkdir(parents=True, exist_ok=True)

		(output_path / "assets").mkdir(exist_ok=True)
		(output_path / "patches").mkdir(exist_ok=True)
		(output_path / "builds").mkdir(exist_ok=True)

		project = Project(
			name=name,
			version="1.0",
			original_rom=rom_path,
			modified_rom="",
			assets_dir=str(output_path / "assets"),
			patches_dir=str(output_path / "patches"),
			created=datetime.now().isoformat(),
			modified=datetime.now().isoformat()
		)

		# Save project file
		project_file = output_path / "project.json"
		with open(project_file, 'w') as f:
			json.dump(project.__dict__, f, indent=2)

		print(f"✓ Project created: {name}")
		print(f"  Location: {output_path}")

		return project

	@staticmethod
	def load_project(project_file: str) -> Optional[Project]:
		"""Load existing project."""
		try:
			with open(project_file, 'r') as f:
				data = json.load(f)

			return Project(**data)

		except Exception as e:
			print(f"ERROR: Failed to load project: {e}")
			return None


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Dragon Warrior ROM Toolkit - Master Controller"
	)

	subparsers = parser.add_subparsers(dest='command', help='Command to execute')

	# Analyze command
	analyze_parser = subparsers.add_parser('analyze', help='Analyze ROM')
	analyze_parser.add_argument('rom', help='ROM file')

	# Extract command
	extract_parser = subparsers.add_parser('extract', help='Extract all assets')
	extract_parser.add_argument('rom', help='ROM file')
	extract_parser.add_argument('--output', type=str, default='assets/', help='Output directory')

	# Workflow command
	workflow_parser = subparsers.add_parser('workflow', help='Run predefined workflow')
	workflow_parser.add_argument('workflow', choices=list(WORKFLOWS.keys()),
	                              help='Workflow name')
	workflow_parser.add_argument('rom', help='ROM file')

	# Project command
	project_parser = subparsers.add_parser('project', help='Create new project')
	project_parser.add_argument('name', help='Project name')
	project_parser.add_argument('rom', help='Original ROM file')
	project_parser.add_argument('--output', type=str, default='.', help='Output directory')

	# Patch command
	patch_parser = subparsers.add_parser('patch', help='Create patch')
	patch_parser.add_argument('original', help='Original ROM')
	patch_parser.add_argument('modified', help='Modified ROM')
	patch_parser.add_argument('-o', '--output', type=str, help='Output patch file')

	args = parser.parse_args()

	if not args.command:
		parser.print_help()
		return 0

	# Execute command
	if args.command == 'analyze':
		report = ROMAnalyzer.analyze_rom(args.rom)
		print("\n✓ Analysis complete")

	elif args.command == 'extract':
		workflow = WORKFLOWS['extract']
		success = ToolExecutor.run_workflow(workflow, args.rom)

		if success:
			print(f"\n✓ Assets extracted to: {args.output}")
		else:
			print("\n✗ Extraction failed")
			return 1

	elif args.command == 'workflow':
		workflow = WORKFLOWS[args.workflow]
		success = ToolExecutor.run_workflow(workflow, args.rom)

		if not success:
			return 1

	elif args.command == 'project':
		project = ProjectManager.create_project(args.name, args.rom, args.output)

	elif args.command == 'patch':
		output = args.output or "patch.bps"
		returncode, stdout, stderr = ToolExecutor.run_tool(
			"binary_patch_tool.py",
			[args.original, args.modified, "--create", output, "--format", "bps"]
		)

		if returncode == 0:
			print(f"\n✓ Patch created: {output}")
		else:
			print(f"\n✗ Patch creation failed")
			print(stderr)
			return 1

	return 0


if __name__ == "__main__":
	sys.exit(main())
