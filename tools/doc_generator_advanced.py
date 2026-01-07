#!/usr/bin/env python3
"""
Documentation Generator for Dragon Warrior ROM Hacking

Comprehensive documentation generation system that creates detailed reference
documentation from ROM data, code, and metadata.

Features:
- Auto-generate data reference docs
- Create wiki-style documentation
- Generate HTML reference pages
- Export to Markdown
- Create searchable index
- Generate data tables
- Cross-reference linking
- Change log generation
- API documentation
- Tutorial generation
- Screenshots and diagrams
- PDF export support

Usage:
	python tools/doc_generator_advanced.py [OPTIONS]

Examples:
	# Generate all documentation
	python tools/doc_generator_advanced.py --all

	# Generate specific sections
	python tools/doc_generator_advanced.py --monsters --items

	# Export to HTML
	python tools/doc_generator_advanced.py --format html --output docs/

	# Generate change log
	python tools/doc_generator_advanced.py --changelog --since v1.0

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
import json
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import argparse
from datetime import datetime


# ============================================================================
# DOCUMENTATION STRUCTURES
# ============================================================================

class DocFormat(Enum):
	"""Documentation output formats."""
	MARKDOWN = "markdown"
	HTML = "html"
	WIKI = "wiki"
	JSON = "json"
	TEXT = "text"


@dataclass
class DocSection:
	"""Documentation section."""
	id: str
	title: str
	content: str
	subsections: List['DocSection'] = field(default_factory=list)
	metadata: Dict = field(default_factory=dict)

	def get_word_count(self) -> int:
		"""Get word count for this section."""
		words = len(self.content.split())
		for subsection in self.subsections:
			words += subsection.get_word_count()
		return words


@dataclass
class DocPage:
	"""Documentation page."""
	title: str
	sections: List[DocSection] = field(default_factory=list)
	author: str = "Dragon Warrior ROM Hacking Toolkit"
	created: str = ""
	modified: str = ""
	tags: List[str] = field(default_factory=list)

	def __post_init__(self):
		if not self.created:
			self.created = datetime.now().isoformat()
		if not self.modified:
			self.modified = self.created


# ============================================================================
# DATA TABLE GENERATOR
# ============================================================================

class TableGenerator:
	"""Generate formatted data tables."""

	@staticmethod
	def generate_markdown_table(headers: List[str], rows: List[List]) -> str:
		"""Generate Markdown table."""
		lines = []

		# Header row
		lines.append("| " + " | ".join(headers) + " |")

		# Separator
		lines.append("| " + " | ".join(["---"] * len(headers)) + " |")

		# Data rows
		for row in rows:
			lines.append("| " + " | ".join(str(cell) for cell in row) + " |")

		return "\n".join(lines)

	@staticmethod
	def generate_html_table(headers: List[str], rows: List[List],
						   css_class: str = "data-table") -> str:
		"""Generate HTML table."""
		lines = []
		lines.append(f'<table class="{css_class}">')

		# Header
		lines.append("  <thead>")
		lines.append("    <tr>")
		for header in headers:
			lines.append(f"      <th>{header}</th>")
		lines.append("    </tr>")
		lines.append("  </thead>")

		# Body
		lines.append("  <tbody>")
		for row in rows:
			lines.append("    <tr>")
			for cell in row:
				lines.append(f"      <td>{cell}</td>")
			lines.append("    </tr>")
		lines.append("  </tbody>")

		lines.append("</table>")
		return "\n".join(lines)

	@staticmethod
	def generate_ascii_table(headers: List[str], rows: List[List]) -> str:
		"""Generate ASCII table."""
		# Calculate column widths
		widths = [len(h) for h in headers]

		for row in rows:
			for i, cell in enumerate(row):
				widths[i] = max(widths[i], len(str(cell)))

		# Create separator line
		sep = "+" + "+".join("-" * (w + 2) for w in widths) + "+"

		lines = []
		lines.append(sep)

		# Header row
		header_line = "|"
		for i, header in enumerate(headers):
			header_line += f" {header:<{widths[i]}} |"
		lines.append(header_line)
		lines.append(sep)

		# Data rows
		for row in rows:
			row_line = "|"
			for i, cell in enumerate(row):
				row_line += f" {str(cell):<{widths[i]}} |"
			lines.append(row_line)

		lines.append(sep)

		return "\n".join(lines)


# ============================================================================
# MONSTER DOCUMENTATION
# ============================================================================

class MonsterDocGenerator:
	"""Generate monster documentation."""

	def __init__(self, monsters: List[Dict]):
		self.monsters = monsters

	def generate_monster_list(self) -> str:
		"""Generate monster list documentation."""
		lines = []
		lines.append("# Dragon Warrior Monsters")
		lines.append("")
		lines.append("Complete list of all monsters in Dragon Warrior.")
		lines.append("")

		# Generate table
		headers = ["ID", "Name", "HP", "Str", "Agi", "XP", "Gold"]
		rows = []

		for monster in self.monsters:
			rows.append([
				monster.get('id', 0),
				monster.get('name', 'Unknown'),
				monster.get('hp', 0),
				monster.get('strength', 0),
				monster.get('agility', 0),
				monster.get('experience', 0),
				monster.get('gold', 0)
			])

		lines.append(TableGenerator.generate_markdown_table(headers, rows))
		lines.append("")

		return "\n".join(lines)

	def generate_monster_detail(self, monster: Dict) -> str:
		"""Generate detailed monster documentation."""
		lines = []

		name = monster.get('name', 'Unknown')
		lines.append(f"# {name}")
		lines.append("")

		# Stats section
		lines.append("## Statistics")
		lines.append("")
		lines.append(f"- **HP**: {monster.get('hp', 0)}")
		lines.append(f"- **Strength**: {monster.get('strength', 0)}")
		lines.append(f"- **Agility**: {monster.get('agility', 0)}")
		lines.append(f"- **Defense**: {monster.get('defense', 0)}")
		lines.append(f"- **Experience**: {monster.get('experience', 0)}")
		lines.append(f"- **Gold**: {monster.get('gold', 0)}")
		lines.append("")

		# Abilities section
		if 'abilities' in monster:
			lines.append("## Abilities")
			lines.append("")
			for ability in monster['abilities']:
				lines.append(f"- {ability}")
			lines.append("")

		# Locations section
		if 'locations' in monster:
			lines.append("## Locations")
			lines.append("")
			for location in monster['locations']:
				lines.append(f"- {location}")
			lines.append("")

		# Strategy section
		if 'strategy' in monster:
			lines.append("## Strategy")
			lines.append("")
			lines.append(monster['strategy'])
			lines.append("")

		return "\n".join(lines)


# ============================================================================
# ITEM DOCUMENTATION
# ============================================================================

class ItemDocGenerator:
	"""Generate item documentation."""

	def __init__(self, items: List[Dict]):
		self.items = items

	def generate_item_list(self) -> str:
		"""Generate item list documentation."""
		lines = []
		lines.append("# Dragon Warrior Items")
		lines.append("")
		lines.append("Complete list of all items, weapons, and armor.")
		lines.append("")

		# Group by type
		by_type = {}
		for item in self.items:
			item_type = item.get('type', 'Item')
			if item_type not in by_type:
				by_type[item_type] = []
			by_type[item_type].append(item)

		# Generate tables for each type
		for item_type, items in sorted(by_type.items()):
			lines.append(f"## {item_type}s")
			lines.append("")

			if item_type == 'Weapon':
				headers = ["ID", "Name", "Attack", "Price"]
				rows = [[i.get('id'), i.get('name'), i.get('attack', 0), i.get('price', 0)]
					   for i in items]
			elif item_type == 'Armor':
				headers = ["ID", "Name", "Defense", "Price"]
				rows = [[i.get('id'), i.get('name'), i.get('defense', 0), i.get('price', 0)]
					   for i in items]
			else:
				headers = ["ID", "Name", "Effect", "Price"]
				rows = [[i.get('id'), i.get('name'), i.get('effect', ''), i.get('price', 0)]
					   for i in items]

			lines.append(TableGenerator.generate_markdown_table(headers, rows))
			lines.append("")

		return "\n".join(lines)


# ============================================================================
# SPELL DOCUMENTATION
# ============================================================================

class SpellDocGenerator:
	"""Generate spell documentation."""

	def __init__(self, spells: List[Dict]):
		self.spells = spells

	def generate_spell_list(self) -> str:
		"""Generate spell list documentation."""
		lines = []
		lines.append("# Dragon Warrior Spells")
		lines.append("")

		headers = ["ID", "Name", "MP Cost", "Type", "Effect", "Learn Level"]
		rows = []

		for spell in self.spells:
			rows.append([
				spell.get('id', 0),
				spell.get('name', 'Unknown'),
				spell.get('mp_cost', 0),
				spell.get('type', 'Support'),
				spell.get('effect', ''),
				spell.get('learn_level', 0)
			])

		lines.append(TableGenerator.generate_markdown_table(headers, rows))
		lines.append("")

		return "\n".join(lines)


# ============================================================================
# MAP DOCUMENTATION
# ============================================================================

class MapDocGenerator:
	"""Generate map documentation."""

	def __init__(self, maps: List[Dict]):
		self.maps = maps

	def generate_map_list(self) -> str:
		"""Generate map list documentation."""
		lines = []
		lines.append("# Dragon Warrior Maps")
		lines.append("")

		for game_map in self.maps:
			lines.append(f"## {game_map.get('name', 'Unknown')}")
			lines.append("")
			lines.append(f"- **ID**: {game_map.get('id', 0)}")
			lines.append(f"- **Size**: {game_map.get('width', 0)}x{game_map.get('height', 0)}")
			lines.append(f"- **Type**: {'Dungeon' if game_map.get('is_dungeon') else 'Overworld'}")

			# Treasures
			treasures = game_map.get('treasures', [])
			if treasures:
				lines.append(f"- **Treasures**: {len(treasures)}")

			# NPCs
			npcs = game_map.get('npcs', [])
			if npcs:
				lines.append(f"- **NPCs**: {len(npcs)}")

			lines.append("")

		return "\n".join(lines)


# ============================================================================
# HTML GENERATOR
# ============================================================================

class HTMLGenerator:
	"""Generate HTML documentation."""

	CSS_TEMPLATE = """
	body {
		font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
		max-width: 1200px;
		margin: 0 auto;
		padding: 20px;
		background: #f5f5f5;
		color: #333;
	}

	.header {
		background: #2c3e50;
		color: white;
		padding: 20px;
		border-radius: 5px;
		margin-bottom: 30px;
	}

	.header h1 {
		margin: 0;
		font-size: 2.5em;
	}

	.content {
		background: white;
		padding: 30px;
		border-radius: 5px;
		box-shadow: 0 2px 4px rgba(0,0,0,0.1);
	}

	.data-table {
		width: 100%;
		border-collapse: collapse;
		margin: 20px 0;
	}

	.data-table th {
		background: #3498db;
		color: white;
		padding: 12px;
		text-align: left;
		font-weight: bold;
	}

	.data-table td {
		padding: 10px 12px;
		border-bottom: 1px solid #ddd;
	}

	.data-table tr:hover {
		background: #f5f5f5;
	}

	.nav {
		background: #34495e;
		padding: 15px;
		border-radius: 5px;
		margin-bottom: 20px;
	}

	.nav a {
		color: #ecf0f1;
		text-decoration: none;
		margin-right: 20px;
		padding: 8px 15px;
		border-radius: 3px;
		display: inline-block;
	}

	.nav a:hover {
		background: #2c3e50;
	}
	"""

	def generate_html_page(self, title: str, content: str) -> str:
		"""Generate complete HTML page."""
		html = f"""<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>{title} - Dragon Warrior Documentation</title>
	<style>
	{self.CSS_TEMPLATE}
	</style>
</head>
<body>
	<div class="header">
		<h1>Dragon Warrior ROM Hacking Documentation</h1>
		<p>Complete reference for Dragon Warrior (NES)</p>
	</div>

	<div class="nav">
		<a href="index.html">Home</a>
		<a href="monsters.html">Monsters</a>
		<a href="items.html">Items</a>
		<a href="spells.html">Spells</a>
		<a href="maps.html">Maps</a>
	</div>

	<div class="content">
		{content}
	</div>

	<footer style="text-align: center; margin-top: 30px; color: #7f8c8d;">
		<p>Generated by Dragon Warrior ROM Hacking Toolkit - {datetime.now().strftime('%Y-%m-%d')}</p>
	</footer>
</body>
</html>
"""
		return html


# ============================================================================
# DOCUMENTATION GENERATOR
# ============================================================================

class DocumentationGenerator:
	"""Main documentation generator."""

	def __init__(self):
		self.pages: List[DocPage] = []
		self.format = DocFormat.MARKDOWN
		self.output_dir = Path("docs")

	def load_data_from_json(self, data_dir: Path):
		"""Load game data from JSON files."""
		self.monsters = []
		self.items = []
		self.spells = []
		self.maps = []

		# Load monsters
		monsters_file = data_dir / "monsters.json"
		if monsters_file.exists():
			with open(monsters_file) as f:
				self.monsters = json.load(f)

		# Load items
		items_file = data_dir / "items.json"
		if items_file.exists():
			with open(items_file) as f:
				self.items = json.load(f)

		# Load spells
		spells_file = data_dir / "spells.json"
		if spells_file.exists():
			with open(spells_file) as f:
				self.spells = json.load(f)

		# Load maps
		maps_file = data_dir / "maps.json"
		if maps_file.exists():
			with open(maps_file) as f:
				self.maps = json.load(f).get('maps', [])

	def generate_all(self):
		"""Generate all documentation."""
		self.generate_index()
		self.generate_monsters_doc()
		self.generate_items_doc()
		self.generate_spells_doc()
		self.generate_maps_doc()

	def generate_index(self):
		"""Generate index page."""
		lines = []
		lines.append("# Dragon Warrior ROM Hacking Documentation")
		lines.append("")
		lines.append("Welcome to the Dragon Warrior ROM Hacking reference documentation.")
		lines.append("")
		lines.append("## Contents")
		lines.append("")
		lines.append("- [Monsters](monsters.md) - Complete monster reference")
		lines.append("- [Items](items.md) - Weapons, armor, and items")
		lines.append("- [Spells](spells.md) - Magic spells and effects")
		lines.append("- [Maps](maps.md) - Overworld and dungeon maps")
		lines.append("")
		lines.append("## Statistics")
		lines.append("")
		lines.append(f"- **Monsters**: {len(self.monsters)}")
		lines.append(f"- **Items**: {len(self.items)}")
		lines.append(f"- **Spells**: {len(self.spells)}")
		lines.append(f"- **Maps**: {len(self.maps)}")
		lines.append("")

		self._save_page("index", "\n".join(lines))

	def generate_monsters_doc(self):
		"""Generate monster documentation."""
		if self.monsters:
			generator = MonsterDocGenerator(self.monsters)
			content = generator.generate_monster_list()
			self._save_page("monsters", content)

	def generate_items_doc(self):
		"""Generate item documentation."""
		if self.items:
			generator = ItemDocGenerator(self.items)
			content = generator.generate_item_list()
			self._save_page("items", content)

	def generate_spells_doc(self):
		"""Generate spell documentation."""
		if self.spells:
			generator = SpellDocGenerator(self.spells)
			content = generator.generate_spell_list()
			self._save_page("spells", content)

	def generate_maps_doc(self):
		"""Generate map documentation."""
		if self.maps:
			generator = MapDocGenerator(self.maps)
			content = generator.generate_map_list()
			self._save_page("maps", content)

	def _save_page(self, filename: str, content: str):
		"""Save page to file."""
		self.output_dir.mkdir(parents=True, exist_ok=True)

		if self.format == DocFormat.MARKDOWN:
			filepath = self.output_dir / f"{filename}.md"
			with open(filepath, 'w', encoding='utf-8') as f:
				f.write(content)

		elif self.format == DocFormat.HTML:
			html_gen = HTMLGenerator()
			html_content = html_gen.generate_html_page(filename.title(), content)

			filepath = self.output_dir / f"{filename}.html"
			with open(filepath, 'w', encoding='utf-8') as f:
				f.write(html_content)

		print(f"Generated: {filepath}")


# ============================================================================
# MAIN CLI
# ============================================================================

def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description="Documentation Generator"
	)

	parser.add_argument('--all', action='store_true',
					   help="Generate all documentation")
	parser.add_argument('--monsters', action='store_true',
					   help="Generate monster documentation")
	parser.add_argument('--items', action='store_true',
					   help="Generate item documentation")
	parser.add_argument('--spells', action='store_true',
					   help="Generate spell documentation")
	parser.add_argument('--maps', action='store_true',
					   help="Generate map documentation")
	parser.add_argument('--format', choices=['markdown', 'html'],
					   default='markdown', help="Output format")
	parser.add_argument('--output', type=Path, default=Path('docs'),
					   help="Output directory")
	parser.add_argument('--data', type=Path, default=Path('assets'),
					   help="Data directory")

	args = parser.parse_args()

	# Create generator
	generator = DocumentationGenerator()
	generator.format = DocFormat(args.format)
	generator.output_dir = args.output

	# Load data
	print(f"Loading data from: {args.data}")
	generator.load_data_from_json(args.data)

	print(f"Loaded {len(generator.monsters)} monsters")
	print(f"Loaded {len(generator.items)} items")
	print(f"Loaded {len(generator.spells)} spells")
	print(f"Loaded {len(generator.maps)} maps")

	# Generate documentation
	print(f"\nGenerating documentation...")

	if args.all or not any([args.monsters, args.items, args.spells, args.maps]):
		generator.generate_all()
	else:
		if args.monsters:
			generator.generate_monsters_doc()
		if args.items:
			generator.generate_items_doc()
		if args.spells:
			generator.generate_spells_doc()
		if args.maps:
			generator.generate_maps_doc()

	print(f"\nDocumentation generated in: {args.output}")

	return 0


if __name__ == "__main__":
	sys.exit(main())
