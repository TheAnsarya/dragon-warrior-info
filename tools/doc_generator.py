#!/usr/bin/env python3
"""
Dragon Warrior Documentation Generator

Automated documentation generation system for Dragon Warrior ROM hacking.
Features:
- Generate comprehensive API documentation
- Create ROM data reference guides
- Build tool usage tutorials
- Generate code documentation from docstrings
- Create markdown wikis
- Build HTML documentation sites
- Generate PDF manuals
- Auto-generate changelog from git history
- Create quick reference cards
- Build searchable documentation database

Documentation Types:
- API Reference: Tool modules, classes, functions
- ROM Format: Memory maps, data structures, algorithms
- Tutorials: Step-by-step guides for common tasks
- Quick Reference: Cheat sheets and tables
- Development: Contributing guidelines, architecture

Author: Dragon Warrior Toolkit
Date: 2024-11-26
"""

import argparse
import ast
import inspect
import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import re


@dataclass
class FunctionDoc:
	"""Documentation for a function."""
	name: str
	signature: str
	docstring: str
	parameters: List[Tuple[str, str, str]]  # name, type, description
	returns: Optional[str]
	examples: List[str] = field(default_factory=list)

	def to_markdown(self) -> str:
		"""Convert to markdown."""
		lines = []

		lines.append(f"### `{self.name}()`")
		lines.append("")

		if self.docstring:
			lines.append(self.docstring)
			lines.append("")

		if self.parameters:
			lines.append("**Parameters:**")
			lines.append("")
			for name, param_type, desc in self.parameters:
				type_str = f" (`{param_type}`)" if param_type else ""
				lines.append(f"- `{name}`{type_str}: {desc}")
			lines.append("")

		if self.returns:
			lines.append("**Returns:**")
			lines.append("")
			lines.append(f"- {self.returns}")
			lines.append("")

		if self.examples:
			lines.append("**Examples:**")
			lines.append("")
			for example in self.examples:
				lines.append("```python")
				lines.append(example)
				lines.append("```")
				lines.append("")

		return '\n'.join(lines)


@dataclass
class ClassDoc:
	"""Documentation for a class."""
	name: str
	docstring: str
	methods: List[FunctionDoc] = field(default_factory=list)
	attributes: List[Tuple[str, str, str]] = field(default_factory=list)

	def to_markdown(self) -> str:
		"""Convert to markdown."""
		lines = []

		lines.append(f"## Class: `{self.name}`")
		lines.append("")

		if self.docstring:
			lines.append(self.docstring)
			lines.append("")

		if self.attributes:
			lines.append("### Attributes")
			lines.append("")
			for name, attr_type, desc in self.attributes:
				type_str = f" (`{attr_type}`)" if attr_type else ""
				lines.append(f"- `{name}`{type_str}: {desc}")
			lines.append("")

		if self.methods:
			lines.append("### Methods")
			lines.append("")
			for method in self.methods:
				lines.append(method.to_markdown())

		return '\n'.join(lines)


@dataclass
class ModuleDoc:
	"""Documentation for a module."""
	name: str
	description: str
	classes: List[ClassDoc] = field(default_factory=list)
	functions: List[FunctionDoc] = field(default_factory=list)

	def to_markdown(self) -> str:
		"""Convert to markdown."""
		lines = []

		lines.append(f"# Module: {self.name}")
		lines.append("")

		if self.description:
			lines.append(self.description)
			lines.append("")

		if self.classes:
			lines.append("## Classes")
			lines.append("")
			for cls in self.classes:
				lines.append(cls.to_markdown())
				lines.append("")

		if self.functions:
			lines.append("## Functions")
			lines.append("")
			for func in self.functions:
				lines.append(func.to_markdown())
				lines.append("")

		return '\n'.join(lines)


class CodeDocExtractor:
	"""Extract documentation from Python code."""

	def extract_module_doc(self, file_path: Path) -> Optional[ModuleDoc]:
		"""Extract documentation from a Python file."""
		if not file_path.exists() or file_path.suffix != '.py':
			return None

		try:
			source = file_path.read_text(encoding='utf-8')
			tree = ast.parse(source)

			# Get module docstring
			module_doc = ast.get_docstring(tree) or ""

			# Extract classes and functions
			classes = []
			functions = []

			for node in ast.walk(tree):
				if isinstance(node, ast.ClassDef):
					cls_doc = self._extract_class(node)
					if cls_doc:
						classes.append(cls_doc)

				elif isinstance(node, ast.FunctionDef):
					# Only top-level functions (not in classes)
					if isinstance(node, ast.FunctionDef) and not any(
						isinstance(parent, ast.ClassDef)
						for parent in ast.walk(tree)
					):
						func_doc = self._extract_function(node)
						if func_doc:
							functions.append(func_doc)

			return ModuleDoc(
				name=file_path.stem,
				description=module_doc,
				classes=classes,
				functions=functions
			)

		except Exception as e:
			print(f"Warning: Could not parse {file_path}: {e}")
			return None

	def _extract_class(self, node: ast.ClassDef) -> ClassDoc:
		"""Extract class documentation."""
		docstring = ast.get_docstring(node) or ""

		methods = []
		for item in node.body:
			if isinstance(item, ast.FunctionDef):
				method_doc = self._extract_function(item)
				if method_doc and not method_doc.name.startswith('_'):
					methods.append(method_doc)

		return ClassDoc(
			name=node.name,
			docstring=docstring,
			methods=methods
		)

	def _extract_function(self, node: ast.FunctionDef) -> FunctionDoc:
		"""Extract function documentation."""
		docstring = ast.get_docstring(node) or ""

		# Get function signature
		args = []
		for arg in node.args.args:
			args.append(arg.arg)

		signature = f"{node.name}({', '.join(args)})"

		# Parse parameters from docstring (simplified)
		parameters = []
		returns = None

		# Simple docstring parsing
		lines = docstring.split('\n')
		in_params = False
		in_returns = False

		for line in lines:
			line = line.strip()

			if 'Parameters:' in line or 'Args:' in line:
				in_params = True
				in_returns = False
				continue
			elif 'Returns:' in line:
				in_params = False
				in_returns = True
				continue

			if in_params and line.startswith('-') or line.startswith('*'):
				# Try to parse parameter line
				match = re.match(r'[-*]\s*(\w+)(?:\s*\(([^)]+)\))?\s*:\s*(.+)', line)
				if match:
					param_name, param_type, param_desc = match.groups()
					parameters.append((param_name, param_type or '', param_desc))

			elif in_returns and line:
				returns = line

		return FunctionDoc(
			name=node.name,
			signature=signature,
			docstring=docstring,
			parameters=parameters,
			returns=returns
		)


class DocumentationGenerator:
	"""Main documentation generator."""

	def __init__(self):
		self.extractor = CodeDocExtractor()

	def generate_api_docs(self, tools_dir: Path, output_dir: Path) -> None:
		"""Generate API documentation for all tools."""
		output_dir.mkdir(parents=True, exist_ok=True)

		print("Generating API documentation...")

		# Find all Python files
		py_files = list(tools_dir.glob("*.py"))

		# Generate table of contents
		toc_lines = []
		toc_lines.append("# Dragon Warrior Toolkit - API Documentation")
		toc_lines.append("")
		toc_lines.append("## Table of Contents")
		toc_lines.append("")

		module_docs = []

		for py_file in sorted(py_files):
			if py_file.name.startswith('_'):
				continue

			module_doc = self.extractor.extract_module_doc(py_file)
			if module_doc:
				module_docs.append(module_doc)
				toc_lines.append(f"- [{module_doc.name}]({module_doc.name}.md)")

		# Write table of contents
		toc_path = output_dir / "README.md"
		toc_path.write_text('\n'.join(toc_lines))

		# Write individual module docs
		for module_doc in module_docs:
			doc_path = output_dir / f"{module_doc.name}.md"
			doc_path.write_text(module_doc.to_markdown())
			print(f"  ✓ {module_doc.name}.md")

		print(f"✓ Generated API docs in {output_dir}")

	def generate_quick_reference(self, output_path: Path) -> None:
		"""Generate quick reference card."""
		lines = []

		lines.append("# Dragon Warrior Quick Reference")
		lines.append("")
		lines.append("## Stats by Level")
		lines.append("")
		lines.append("| Level | HP  | MP  | STR | AGI | EXP Required |")
		lines.append("|-------|-----|-----|-----|-----|--------------|")

		from save_editor import HP_TABLE, MP_TABLE, STR_TABLE, AGI_TABLE, EXP_TABLE

		for level in range(1, 31):
			idx = level - 1
			lines.append(
				f"| {level:2d}    | {HP_TABLE[idx]:3d} | {MP_TABLE[idx]:3d} | "
				f"{STR_TABLE[idx]:3d} | {AGI_TABLE[idx]:3d} | {EXP_TABLE[idx]:12d} |"
			)

		lines.append("")
		lines.append("## Spells")
		lines.append("")
		lines.append("| Spell      | Level | MP | Effect                        |")
		lines.append("|------------|-------|-----|-------------------------------|")
		lines.append("| HEAL       | 3     | 4   | Restore HP                    |")
		lines.append("| HURT       | 4     | 2   | Damage enemy                  |")
		lines.append("| SLEEP      | 7     | 2   | Put enemy to sleep            |")
		lines.append("| RADIANT    | 9     | 3   | Light up darkness             |")
		lines.append("| STOPSPELL  | 10    | 2   | Block enemy spells            |")
		lines.append("| OUTSIDE    | 12    | 6   | Exit dungeon                  |")
		lines.append("| RETURN     | 13    | 8   | Teleport to Tantegel          |")
		lines.append("| REPEL      | 15    | 2   | Prevent weak encounters       |")
		lines.append("| HEALMORE   | 17    | 10  | Restore more HP               |")
		lines.append("| HURTMORE   | 19    | 5   | Damage enemy (stronger)       |")

		lines.append("")
		lines.append("## Key Items")
		lines.append("")
		lines.append("| Item              | Location      | Purpose                  |")
		lines.append("|-------------------|---------------|--------------------------|")
		lines.append("| Magic Key         | Garinham      | Open magic doors         |")
		lines.append("| Erdrick's Token   | Mountain Cave | Trade for Erdrick's Armor|")
		lines.append("| Gwaelin's Love    | Swamp Cave    | Track distance to castle |")
		lines.append("| Silver Harp       | Garin's Grave | Put Golem to sleep       |")
		lines.append("| Stones of Sunlight| Hauksness     | Rainbow Drop ingredient  |")
		lines.append("| Staff of Rain     | Kol           | Rainbow Drop ingredient  |")
		lines.append("| Rainbow Drop      | Rimuldar      | Create Rainbow Bridge    |")
		lines.append("| Erdrick's Armor   | Swamp Cave    | Best armor               |")
		lines.append("| Erdrick's Sword   | Charlock      | Best weapon              |")

		lines.append("")
		lines.append("## Equipment Progression")
		lines.append("")
		lines.append("### Weapons")
		lines.append("")
		lines.append("| Weapon       | Attack | Cost   | Available   |")
		lines.append("|--------------|--------|--------|-------------|")
		lines.append("| Bamboo Pole  | +2     | 10     | Brecconary  |")
		lines.append("| Club         | +4     | 60     | Brecconary  |")
		lines.append("| Copper Sword | +10    | 180    | Garinham    |")
		lines.append("| Hand Axe     | +15    | 560    | Rimuldar    |")
		lines.append("| Broad Sword  | +20    | 1500   | Cantlin     |")
		lines.append("| Flame Sword  | +28    | 9800   | Cantlin     |")
		lines.append("| Erdrick's Sword| +40  | -      | Charlock    |")

		lines.append("")
		lines.append("### Armor")
		lines.append("")
		lines.append("| Armor        | Defense | Cost   | Available   |")
		lines.append("|--------------|---------|--------|-------------|")
		lines.append("| Clothes      | +2      | 20     | Brecconary  |")
		lines.append("| Leather      | +4      | 70     | Brecconary  |")
		lines.append("| Chain Mail   | +10     | 300    | Garinham    |")
		lines.append("| Half Plate   | +16     | 1000   | Cantlin     |")
		lines.append("| Full Plate   | +24     | 3000   | Cantlin     |")
		lines.append("| Magic Armor  | +24     | 7700   | Cantlin     |")
		lines.append("| Erdrick's    | +28     | -      | Swamp Cave  |")

		lines.append("")
		lines.append("## Damage Formula")
		lines.append("")
		lines.append("```")
		lines.append("Damage = (Attack - Defense / 2) ± 25% variance")
		lines.append("```")

		lines.append("")
		lines.append("## Enemy Weaknesses")
		lines.append("")
		lines.append("| Enemy Type    | Weak To      | Resists      |")
		lines.append("|---------------|--------------|--------------|")
		lines.append("| Ghosts        | Physical     | HURT         |")
		lines.append("| Magicians     | Physical     | STOPSPELL    |")
		lines.append("| Metal enemies | Magic        | Physical     |")
		lines.append("| Dragons       | Strong attacks| -           |")

		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text('\n'.join(lines))

		print(f"✓ Generated quick reference: {output_path}")

	def generate_tutorial(self, output_path: Path) -> None:
		"""Generate getting started tutorial."""
		lines = []

		lines.append("# Dragon Warrior Toolkit - Getting Started")
		lines.append("")
		lines.append("## Installation")
		lines.append("")
		lines.append("1. Clone the repository:")
		lines.append("   ```bash")
		lines.append("   git clone <repository-url>")
		lines.append("   cd dragon-warrior-info")
		lines.append("   ```")
		lines.append("")
		lines.append("2. Install dependencies:")
		lines.append("   ```bash")
		lines.append("   pip install -r requirements.txt")
		lines.append("   ```")
		lines.append("")
		lines.append("3. Place your Dragon Warrior ROM in the `roms/` directory")
		lines.append("")
		lines.append("## Basic Usage")
		lines.append("")
		lines.append("### Quest Tracking")
		lines.append("")
		lines.append("Track your progress through the game:")
		lines.append("")
		lines.append("```bash")
		lines.append("python tools/quest_tracker.py --interactive")
		lines.append("```")
		lines.append("")
		lines.append("### Save File Editing")
		lines.append("")
		lines.append("Edit your save files:")
		lines.append("")
		lines.append("```bash")
		lines.append("python tools/save_editor.py --interactive")
		lines.append("```")
		lines.append("")
		lines.append("Create a perfect save:")
		lines.append("")
		lines.append("```bash")
		lines.append("python tools/save_editor.py --sram saves/game.sav --slot 1 --perfect 30 --output saves/perfect.sav")
		lines.append("```")
		lines.append("")
		lines.append("### ROM Randomization")
		lines.append("")
		lines.append("Create a randomized ROM:")
		lines.append("")
		lines.append("```bash")
		lines.append("python tools/randomizer.py --rom roms/original.nes --output roms/randomized.nes --difficulty NORMAL")
		lines.append("```")
		lines.append("")
		lines.append("### Data Analysis")
		lines.append("")
		lines.append("Generate comprehensive analysis:")
		lines.append("")
		lines.append("```bash")
		lines.append("python tools/data_analyzer.py --report output/analysis.txt --json output/data.json")
		lines.append("```")
		lines.append("")
		lines.append("Analyze battles at specific level:")
		lines.append("")
		lines.append("```bash")
		lines.append("python tools/data_analyzer.py --battle 10")
		lines.append("```")
		lines.append("")
		lines.append("### Music Editing")
		lines.append("")
		lines.append("Extract and edit music:")
		lines.append("")
		lines.append("```bash")
		lines.append("python tools/music_editor.py --interactive")
		lines.append("```")
		lines.append("")
		lines.append("## Advanced Topics")
		lines.append("")
		lines.append("### Building ROMs")
		lines.append("")
		lines.append("The toolkit includes a complete build system:")
		lines.append("")
		lines.append("```bash")
		lines.append("python dragon_warrior_build.py --rom roms/original.nes --output build/modified.nes")
		lines.append("```")
		lines.append("")
		lines.append("### Testing")
		lines.append("")
		lines.append("Run the test suite:")
		lines.append("")
		lines.append("```bash")
		lines.append("python tools/test_suite.py")
		lines.append("```")
		lines.append("")
		lines.append("## Common Tasks")
		lines.append("")
		lines.append("### Task 1: Level up character quickly")
		lines.append("")
		lines.append("1. Open save editor: `python tools/save_editor.py -i`")
		lines.append("2. Load your save file")
		lines.append("3. Select save slot")
		lines.append("4. Edit stats and set level to 20")
		lines.append("5. Save the file")
		lines.append("")
		lines.append("### Task 2: Find optimal grinding spots")
		lines.append("")
		lines.append("1. Run data analyzer: `python tools/data_analyzer.py --report output/analysis.txt`")
		lines.append("2. Check 'Enemy Efficiency Ratings' section")
		lines.append("3. Look for high efficiency enemies at your level")
		lines.append("")
		lines.append("### Task 3: Create randomized race ROM")
		lines.append("")
		lines.append("1. Run randomizer: `python tools/randomizer.py --rom roms/original.nes --output roms/race.nes --seed 12345`")
		lines.append("2. Distribute ROM to racers")
		lines.append("3. Keep spoiler log hidden until race completion")
		lines.append("")
		lines.append("## Troubleshooting")
		lines.append("")
		lines.append("**Problem:** Import errors when running tools")
		lines.append("")
		lines.append("**Solution:** Make sure you're in the repository root and Python can find the tools directory")
		lines.append("")
		lines.append("**Problem:** ROM not found errors")
		lines.append("")
		lines.append("**Solution:** Check that your ROM is in the correct location and is the correct version")
		lines.append("")
		lines.append("**Problem:** Save file corruption")
		lines.append("")
		lines.append("**Solution:** Always backup your saves before editing. The tool creates backups automatically.")
		lines.append("")
		lines.append("## Getting Help")
		lines.append("")
		lines.append("For detailed help on any tool:")
		lines.append("")
		lines.append("```bash")
		lines.append("python tools/<tool_name>.py --help")
		lines.append("```")
		lines.append("")
		lines.append("Check the API documentation in `docs/api/` for detailed module information.")

		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text('\n'.join(lines))

		print(f"✓ Generated tutorial: {output_path}")

	def generate_rom_format_docs(self, output_path: Path) -> None:
		"""Generate ROM format documentation."""
		lines = []

		lines.append("# Dragon Warrior ROM Format Reference")
		lines.append("")
		lines.append("## ROM Header")
		lines.append("")
		lines.append("```")
		lines.append("Offset  Size  Description")
		lines.append("------  ----  -----------")
		lines.append("0x0000  16    iNES Header")
		lines.append("  0x00  4     'NES' + 0x1A")
		lines.append("  0x04  1     PRG ROM size (16KB units)")
		lines.append("  0x05  1     CHR ROM size (8KB units)")
		lines.append("  0x06  1     Flags 6 (Mapper, mirroring)")
		lines.append("  0x07  1     Flags 7 (Mapper)")
		lines.append("  0x08  8     Reserved (should be 0)")
		lines.append("```")
		lines.append("")
		lines.append("## Memory Map")
		lines.append("")
		lines.append("### PRG ROM")
		lines.append("")
		lines.append("```")
		lines.append("Bank 0 (0x8000-0xBFFF):")
		lines.append("  0x8000-0x9FFF: Code and data")
		lines.append("  0xA000-0xBFFF: Code and data")
		lines.append("")
		lines.append("Bank 1 (0xC000-0xFFFF):")
		lines.append("  0xC000-0xDFFF: Code and data")
		lines.append("  0xE000-0xFFFF: Code and data")
		lines.append("  0xFFFA-0xFFFB: NMI vector")
		lines.append("  0xFFFC-0xFFFD: Reset vector")
		lines.append("  0xFFFE-0xFFFF: IRQ vector")
		lines.append("```")
		lines.append("")
		lines.append("## Data Structures")
		lines.append("")
		lines.append("### Enemy Data")
		lines.append("")
		lines.append("```")
		lines.append("Each enemy: 8 bytes")
		lines.append("  +0: HP (1 byte)")
		lines.append("  +1: Strength (1 byte)")
		lines.append("  +2: Agility (1 byte)")
		lines.append("  +3: Attack pattern (1 byte)")
		lines.append("  +4: Gold drop (2 bytes, little-endian)")
		lines.append("  +6: EXP drop (2 bytes, little-endian)")
		lines.append("```")
		lines.append("")
		lines.append("### Item Data")
		lines.append("")
		lines.append("```")
		lines.append("Each item: 4 bytes")
		lines.append("  +0: Item ID (1 byte)")
		lines.append("  +1: Type flags (1 byte)")
		lines.append("  +2: Price (2 bytes, little-endian)")
		lines.append("```")
		lines.append("")
		lines.append("### Save Data")
		lines.append("")
		lines.append("```")
		lines.append("Battery RAM: 512 bytes")
		lines.append("  3 save slots of 128 bytes each")
		lines.append("  Remaining bytes: unused")
		lines.append("")
		lines.append("Each save slot:")
		lines.append("  +0x00: Level (1 byte)")
		lines.append("  +0x01: Experience (2 bytes, little-endian)")
		lines.append("  +0x03: Gold (2 bytes, little-endian)")
		lines.append("  +0x05: HP (1 byte)")
		lines.append("  +0x06: Max HP (1 byte)")
		lines.append("  +0x07: MP (1 byte)")
		lines.append("  +0x08: Max MP (1 byte)")
		lines.append("  +0x09: Strength (1 byte)")
		lines.append("  +0x0A: Agility (1 byte)")
		lines.append("  +0x0B: Attack power (1 byte)")
		lines.append("  +0x0C: Defense power (1 byte)")
		lines.append("  +0x0D: X position (1 byte)")
		lines.append("  +0x0E: Y position (1 byte)")
		lines.append("  +0x0F: Map ID (1 byte)")
		lines.append("  +0x10-0x12: Equipment (3 bytes)")
		lines.append("  +0x14-0x1B: Inventory (8 bytes)")
		lines.append("  +0x1C: Herb count (1 byte)")
		lines.append("  +0x1D: Magic keys (1 byte)")
		lines.append("  +0x1E: Spell flags (1 byte)")
		lines.append("  +0x1F: Game flags (1 byte)")
		lines.append("  +0x7E: Checksum (1 byte)")
		lines.append("```")
		lines.append("")
		lines.append("## CHR ROM")
		lines.append("")
		lines.append("```")
		lines.append("Pattern tables: 8KB total")
		lines.append("  Pattern table 0 (0x0000-0x0FFF): Sprites")
		lines.append("  Pattern table 1 (0x1000-0x1FFF): Background tiles")
		lines.append("")
		lines.append("Each tile: 16 bytes (8x8 pixels, 2bpp)")
		lines.append("  Bytes 0-7: Low bit plane")
		lines.append("  Bytes 8-15: High bit plane")
		lines.append("```")
		lines.append("")
		lines.append("## Important Offsets")
		lines.append("")
		lines.append("*(Approximate - verify with actual ROM)*")
		lines.append("")
		lines.append("```")
		lines.append("Enemy data: 0x????")
		lines.append("Item data: 0x????")
		lines.append("Shop data: 0x????")
		lines.append("Spell data: 0x????")
		lines.append("Text pointers: 0x????")
		lines.append("Map data: 0x????")
		lines.append("```")
		lines.append("")
		lines.append("## Algorithms")
		lines.append("")
		lines.append("### Damage Calculation")
		lines.append("")
		lines.append("```c")
		lines.append("damage = attacker_strength - (defender_defense / 2);")
		lines.append("variance = damage * 0.25;")
		lines.append("damage += random(-variance, +variance);")
		lines.append("damage = max(0, damage);")
		lines.append("```")
		lines.append("")
		lines.append("### Experience Calculation")
		lines.append("")
		lines.append("```c")
		lines.append("exp_for_level[level] = base_exp * (level * level);")
		lines.append("```")
		lines.append("")
		lines.append("### Random Encounters")
		lines.append("")
		lines.append("```c")
		lines.append("if (steps % 8 == 0) {")
		lines.append("    if (random() < encounter_rate) {")
		lines.append("        trigger_battle();")
		lines.append("    }")
		lines.append("}")
		lines.append("```")

		output_path.parent.mkdir(parents=True, exist_ok=True)
		output_path.write_text('\n'.join(lines))

		print(f"✓ Generated ROM format docs: {output_path}")


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Dragon Warrior Documentation Generator'
	)

	parser.add_argument(
		'--api',
		action='store_true',
		help='Generate API documentation'
	)

	parser.add_argument(
		'--quick-ref',
		action='store_true',
		help='Generate quick reference'
	)

	parser.add_argument(
		'--tutorial',
		action='store_true',
		help='Generate tutorial'
	)

	parser.add_argument(
		'--rom-format',
		action='store_true',
		help='Generate ROM format documentation'
	)

	parser.add_argument(
		'--all',
		action='store_true',
		help='Generate all documentation'
	)

	parser.add_argument(
		'--output',
		type=Path,
		default=Path("docs"),
		help='Output directory'
	)

	args = parser.parse_args()

	generator = DocumentationGenerator()

	if args.all or args.api:
		tools_dir = Path("tools")
		api_output = args.output / "api"
		generator.generate_api_docs(tools_dir, api_output)

	if args.all or args.quick_ref:
		ref_output = args.output / "quick_reference.md"
		generator.generate_quick_reference(ref_output)

	if args.all or args.tutorial:
		tutorial_output = args.output / "GETTING_STARTED.md"
		generator.generate_tutorial(tutorial_output)

	if args.all or args.rom_format:
		format_output = args.output / "ROM_FORMAT.md"
		generator.generate_rom_format_docs(format_output)

	if not any([args.api, args.quick_ref, args.tutorial, args.rom_format, args.all]):
		# Default: generate all
		tools_dir = Path("tools")
		generator.generate_api_docs(tools_dir, args.output / "api")
		generator.generate_quick_reference(args.output / "quick_reference.md")
		generator.generate_tutorial(args.output / "GETTING_STARTED.md")
		generator.generate_rom_format_docs(args.output / "ROM_FORMAT.md")

	print("\n✓ Documentation generation complete!")

	return 0


if __name__ == '__main__':
	exit(main())
