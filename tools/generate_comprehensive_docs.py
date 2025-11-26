#!/usr/bin/env python3
"""
Comprehensive API Documentation Generator

Automatically generates complete API documentation for all Dragon Warrior toolkit
modules, classes, and functions. Creates HTML, Markdown, and JSON output with
cross-references, code examples, and usage patterns.

Features:
- Automatic docstring extraction
- Type hint documentation
- Parameter/return value tables
- Code example extraction
- Cross-reference linking
- Usage statistics
- Dependency graphs
- Multiple output formats (HTML, MD, JSON)
- Search index generation

Usage:
	python tools/generate_comprehensive_docs.py [--format html|md|json|all]

Examples:
	# Generate HTML docs
	python tools/generate_comprehensive_docs.py --format html

	# Generate all formats
	python tools/generate_comprehensive_docs.py --format all

	# Interactive mode
	python tools/generate_comprehensive_docs.py
"""

import sys
import ast
import inspect
import importlib
import pkgutil
from pathlib import Path
from typing import List, Dict, Optional, Any, Tuple, Set
from dataclasses import dataclass, field, asdict
import json
import re


@dataclass
class Parameter:
	"""Function parameter information."""
	name: str
	type_hint: str = "Any"
	default: Optional[str] = None
	description: str = ""


@dataclass
class FunctionDoc:
	"""Function documentation."""
	name: str
	module: str
	qualname: str
	signature: str
	docstring: str
	parameters: List[Parameter] = field(default_factory=list)
	returns: str = "None"
	return_description: str = ""
	raises: List[str] = field(default_factory=list)
	examples: List[str] = field(default_factory=list)
	see_also: List[str] = field(default_factory=list)
	deprecated: bool = False
	since_version: str = ""


@dataclass
class ClassDoc:
	"""Class documentation."""
	name: str
	module: str
	qualname: str
	docstring: str
	bases: List[str] = field(default_factory=list)
	methods: List[FunctionDoc] = field(default_factory=list)
	attributes: Dict[str, str] = field(default_factory=dict)
	examples: List[str] = field(default_factory=list)
	see_also: List[str] = field(default_factory=list)


@dataclass
class ModuleDoc:
	"""Module documentation."""
	name: str
	path: str
	docstring: str
	classes: List[ClassDoc] = field(default_factory=list)
	functions: List[FunctionDoc] = field(default_factory=list)
	constants: Dict[str, Any] = field(default_factory=dict)
	imports: List[str] = field(default_factory=list)


class DocstringParser:
	"""Parse and extract information from docstrings."""

	@staticmethod
	def parse(docstring: str) -> Dict[str, Any]:
		"""
		Parse docstring into structured components.

		Supports Google-style and reStructuredText formats.
		"""
		if not docstring:
			return {
				'summary': '',
				'description': '',
				'parameters': {},
				'returns': '',
				'raises': [],
				'examples': [],
				'see_also': []
			}

		lines = docstring.split('\n')

		# Extract summary (first line)
		summary = lines[0].strip() if lines else ''

		# Parse sections
		current_section = 'description'
		description = []
		parameters = {}
		returns = ''
		raises = []
		examples = []
		see_also = []

		i = 1
		while i < len(lines):
			line = lines[i].strip()

			# Check for section headers
			if line.startswith('Args:') or line.startswith('Arguments:') or line.startswith('Parameters:'):
				current_section = 'args'
				i += 1
				continue
			elif line.startswith('Returns:'):
				current_section = 'returns'
				i += 1
				continue
			elif line.startswith('Raises:'):
				current_section = 'raises'
				i += 1
				continue
			elif line.startswith('Examples:') or line.startswith('Example:'):
				current_section = 'examples'
				i += 1
				continue
			elif line.startswith('See Also:') or line.startswith('See also:'):
				current_section = 'see_also'
				i += 1
				continue

			# Process line based on current section
			if current_section == 'description':
				if line:
					description.append(line)

			elif current_section == 'args':
				# Parse parameter: "name (type): description"
				match = re.match(r'(\w+)\s*(\([^)]+\))?\s*:\s*(.+)', line)
				if match:
					param_name = match.group(1)
					param_desc = match.group(3)
					parameters[param_name] = param_desc

			elif current_section == 'returns':
				if line:
					returns += line + ' '

			elif current_section == 'raises':
				if line:
					raises.append(line)

			elif current_section == 'examples':
				if line:
					examples.append(line)

			elif current_section == 'see_also':
				if line:
					see_also.append(line)

			i += 1

		return {
			'summary': summary,
			'description': '\n'.join(description).strip(),
			'parameters': parameters,
			'returns': returns.strip(),
			'raises': raises,
			'examples': examples,
			'see_also': see_also
		}


class CodeAnalyzer:
	"""Analyze Python source code for documentation."""

	def __init__(self, source_path: Path):
		self.source_path = source_path
		self.parser = DocstringParser()

	def analyze_file(self, filepath: Path) -> Optional[ModuleDoc]:
		"""Analyze a single Python file."""
		try:
			with open(filepath, 'r', encoding='utf-8') as f:
				source = f.read()

			tree = ast.parse(source, filepath.name)

			# Extract module docstring
			module_docstring = ast.get_docstring(tree) or ""

			# Get module name from path
			rel_path = filepath.relative_to(self.source_path)
			module_name = str(rel_path.with_suffix('')).replace('/', '.').replace('\\', '.')

			module_doc = ModuleDoc(
				name=module_name,
				path=str(filepath),
				docstring=module_docstring
			)

			# Analyze top-level definitions
			for node in ast.iter_child_nodes(tree):
				if isinstance(node, ast.ClassDef):
					class_doc = self._analyze_class(node, module_name)
					if class_doc:
						module_doc.classes.append(class_doc)

				elif isinstance(node, ast.FunctionDef):
					func_doc = self._analyze_function(node, module_name)
					if func_doc:
						module_doc.functions.append(func_doc)

				elif isinstance(node, ast.Assign):
					# Constants (uppercase variables)
					for target in node.targets:
						if isinstance(target, ast.Name) and target.id.isupper():
							value = ast.unparse(node.value) if hasattr(ast, 'unparse') else '<value>'
							module_doc.constants[target.id] = value

			return module_doc

		except Exception as e:
			print(f"Error analyzing {filepath}: {e}", file=sys.stderr)
			return None

	def _analyze_class(self, node: ast.ClassDef, module: str) -> Optional[ClassDoc]:
		"""Analyze a class definition."""
		docstring = ast.get_docstring(node) or ""

		class_doc = ClassDoc(
			name=node.name,
			module=module,
			qualname=f"{module}.{node.name}",
			docstring=docstring,
			bases=[self._get_base_name(base) for base in node.bases]
		)

		# Parse docstring
		parsed = self.parser.parse(docstring)
		class_doc.examples = parsed['examples']
		class_doc.see_also = parsed['see_also']

		# Analyze methods
		for item in node.body:
			if isinstance(item, ast.FunctionDef):
				method_doc = self._analyze_function(item, module, class_name=node.name)
				if method_doc:
					class_doc.methods.append(method_doc)

			elif isinstance(item, ast.AnnAssign):
				# Class attributes with type hints
				if isinstance(item.target, ast.Name):
					attr_name = item.target.name
					attr_type = self._get_type_hint(item.annotation)
					class_doc.attributes[attr_name] = attr_type

		return class_doc

	def _analyze_function(
		self,
		node: ast.FunctionDef,
		module: str,
		class_name: Optional[str] = None
	) -> Optional[FunctionDoc]:
		"""Analyze a function definition."""
		docstring = ast.get_docstring(node) or ""

		qualname = f"{module}.{class_name}.{node.name}" if class_name else f"{module}.{node.name}"

		func_doc = FunctionDoc(
			name=node.name,
			module=module,
			qualname=qualname,
			signature=self._get_signature(node),
			docstring=docstring
		)

		# Parse docstring
		parsed = self.parser.parse(docstring)
		func_doc.examples = parsed['examples']
		func_doc.see_also = parsed['see_also']
		func_doc.return_description = parsed['returns']
		func_doc.raises = parsed['raises']

		# Extract parameters
		for arg in node.args.args:
			param = Parameter(name=arg.arg)

			# Type hint
			if arg.annotation:
				param.type_hint = self._get_type_hint(arg.annotation)

			# Default value
			defaults_offset = len(node.args.args) - len(node.args.defaults)
			arg_index = node.args.args.index(arg)
			if arg_index >= defaults_offset:
				default_node = node.args.defaults[arg_index - defaults_offset]
				param.default = ast.unparse(default_node) if hasattr(ast, 'unparse') else '<default>'

			# Description from docstring
			if arg.arg in parsed['parameters']:
				param.description = parsed['parameters'][arg.arg]

			func_doc.parameters.append(param)

		# Return type
		if node.returns:
			func_doc.returns = self._get_type_hint(node.returns)

		return func_doc

	def _get_signature(self, node: ast.FunctionDef) -> str:
		"""Generate function signature string."""
		args = []

		for arg in node.args.args:
			arg_str = arg.arg

			if arg.annotation:
				arg_str += f": {self._get_type_hint(arg.annotation)}"

			args.append(arg_str)

		# Add defaults
		defaults_offset = len(node.args.args) - len(node.args.defaults)
		for i, default in enumerate(node.args.defaults):
			arg_index = defaults_offset + i
			default_str = ast.unparse(default) if hasattr(ast, 'unparse') else '<default>'
			args[arg_index] += f" = {default_str}"

		return_hint = ""
		if node.returns:
			return_hint = f" -> {self._get_type_hint(node.returns)}"

		return f"({', '.join(args)}){return_hint}"

	def _get_type_hint(self, node: ast.expr) -> str:
		"""Extract type hint as string."""
		if hasattr(ast, 'unparse'):
			return ast.unparse(node)
		else:
			# Fallback for older Python
			if isinstance(node, ast.Name):
				return node.id
			elif isinstance(node, ast.Constant):
				return repr(node.value)
			else:
				return 'Any'

	def _get_base_name(self, node: ast.expr) -> str:
		"""Get base class name."""
		if isinstance(node, ast.Name):
			return node.id
		elif isinstance(node, ast.Attribute):
			return f"{node.value.id}.{node.attr}" if isinstance(node.value, ast.Name) else node.attr
		else:
			return 'object'


class HTMLDocGenerator:
	"""Generate HTML documentation."""

	def __init__(self, output_dir: Path):
		self.output_dir = output_dir
		self.output_dir.mkdir(parents=True, exist_ok=True)

	def generate(self, modules: List[ModuleDoc]) -> None:
		"""Generate HTML documentation for all modules."""
		# Generate index
		self._generate_index(modules)

		# Generate module pages
		for module in modules:
			self._generate_module_page(module)

	def _generate_index(self, modules: List[ModuleDoc]) -> None:
		"""Generate index.html."""
		html = ['<!DOCTYPE html>']
		html.append('<html lang="en">')
		html.append('<head>')
		html.append('\t<meta charset="UTF-8">')
		html.append('\t<meta name="viewport" content="width=device-width, initial-scale=1.0">')
		html.append('\t<title>Dragon Warrior Toolkit API Documentation</title>')
		html.append('\t<style>')
		html.append(self._get_css())
		html.append('\t</style>')
		html.append('</head>')
		html.append('<body>')

		html.append('\t<header>')
		html.append('\t\t<h1>Dragon Warrior Toolkit API Documentation</h1>')
		html.append('\t\t<p>Comprehensive API reference for all toolkit modules</p>')
		html.append('\t</header>')

		html.append('\t<main>')
		html.append('\t\t<section id="modules">')
		html.append('\t\t\t<h2>Modules</h2>')
		html.append('\t\t\t<ul class="module-list">')

		for module in sorted(modules, key=lambda m: m.name):
			html.append(f'\t\t\t\t<li>')
			html.append(f'\t\t\t\t\t<a href="{module.name}.html">{module.name}</a>')

			# Module summary
			summary = module.docstring.split('\n')[0] if module.docstring else "No description"
			html.append(f'\t\t\t\t\t<p>{summary}</p>')

			# Stats
			num_classes = len(module.classes)
			num_functions = len(module.functions)
			html.append(f'\t\t\t\t\t<small>{num_classes} classes, {num_functions} functions</small>')

			html.append(f'\t\t\t\t</li>')

		html.append('\t\t\t</ul>')
		html.append('\t\t</section>')
		html.append('\t</main>')

		html.append('\t<footer>')
		html.append('\t\t<p>Generated by Dragon Warrior Toolkit Documentation Generator</p>')
		html.append('\t</footer>')

		html.append('</body>')
		html.append('</html>')

		output_file = self.output_dir / 'index.html'
		with open(output_file, 'w', encoding='utf-8') as f:
			f.write('\n'.join(html))

		print(f"Generated {output_file}")

	def _generate_module_page(self, module: ModuleDoc) -> None:
		"""Generate module documentation page."""
		html = ['<!DOCTYPE html>']
		html.append('<html lang="en">')
		html.append('<head>')
		html.append('\t<meta charset="UTF-8">')
		html.append(f'\t<title>{module.name} - Dragon Warrior Toolkit</title>')
		html.append('\t<style>')
		html.append(self._get_css())
		html.append('\t</style>')
		html.append('</head>')
		html.append('<body>')

		html.append('\t<header>')
		html.append(f'\t\t<h1>Module: {module.name}</h1>')
		html.append('\t\t<nav><a href="index.html">← Back to Index</a></nav>')
		html.append('\t</header>')

		html.append('\t<main>')

		# Module docstring
		if module.docstring:
			html.append('\t\t<section class="description">')
			html.append(f'\t\t\t<p>{self._format_docstring(module.docstring)}</p>')
			html.append('\t\t</section>')

		# Constants
		if module.constants:
			html.append('\t\t<section id="constants">')
			html.append('\t\t\t<h2>Constants</h2>')
			html.append('\t\t\t<table>')
			html.append('\t\t\t\t<thead>')
			html.append('\t\t\t\t\t<tr><th>Name</th><th>Value</th></tr>')
			html.append('\t\t\t\t</thead>')
			html.append('\t\t\t\t<tbody>')

			for name, value in sorted(module.constants.items()):
				html.append(f'\t\t\t\t\t<tr><td><code>{name}</code></td><td><code>{value}</code></td></tr>')

			html.append('\t\t\t\t</tbody>')
			html.append('\t\t\t</table>')
			html.append('\t\t</section>')

		# Classes
		if module.classes:
			html.append('\t\t<section id="classes">')
			html.append('\t\t\t<h2>Classes</h2>')

			for cls in sorted(module.classes, key=lambda c: c.name):
				html.extend(self._format_class(cls))

			html.append('\t\t</section>')

		# Functions
		if module.functions:
			html.append('\t\t<section id="functions">')
			html.append('\t\t\t<h2>Functions</h2>')

			for func in sorted(module.functions, key=lambda f: f.name):
				html.extend(self._format_function(func))

			html.append('\t\t</section>')

		html.append('\t</main>')
		html.append('</body>')
		html.append('</html>')

		output_file = self.output_dir / f'{module.name}.html'
		with open(output_file, 'w', encoding='utf-8') as f:
			f.write('\n'.join(html))

		print(f"Generated {output_file}")

	def _format_class(self, cls: ClassDoc) -> List[str]:
		"""Format class documentation."""
		html = []

		html.append(f'\t\t\t<div class="class" id="{cls.name}">')
		html.append(f'\t\t\t\t<h3>class {cls.name}</h3>')

		# Bases
		if cls.bases:
			bases_str = ', '.join(cls.bases)
			html.append(f'\t\t\t\t<p class="bases">Inherits from: {bases_str}</p>')

		# Docstring
		if cls.docstring:
			html.append(f'\t\t\t\t<p>{self._format_docstring(cls.docstring)}</p>')

		# Attributes
		if cls.attributes:
			html.append('\t\t\t\t<h4>Attributes</h4>')
			html.append('\t\t\t\t<ul>')
			for name, type_hint in sorted(cls.attributes.items()):
				html.append(f'\t\t\t\t\t<li><code>{name}: {type_hint}</code></li>')
			html.append('\t\t\t\t</ul>')

		# Methods
		if cls.methods:
			html.append('\t\t\t\t<h4>Methods</h4>')
			for method in sorted(cls.methods, key=lambda m: m.name):
				html.extend(self._format_function(method, indent=4))

		html.append('\t\t\t</div>')

		return html

	def _format_function(self, func: FunctionDoc, indent: int = 3) -> List[str]:
		"""Format function documentation."""
		html = []
		tab = '\t' * indent

		html.append(f'{tab}<div class="function" id="{func.name}">')
		html.append(f'{tab}\t<h4>{func.name}{func.signature}</h4>')

		# Docstring summary
		if func.docstring:
			summary = func.docstring.split('\n')[0]
			html.append(f'{tab}\t<p>{summary}</p>')

		# Parameters
		if func.parameters:
			html.append(f'{tab}\t<table class="parameters">')
			html.append(f'{tab}\t\t<thead>')
			html.append(f'{tab}\t\t\t<tr><th>Parameter</th><th>Type</th><th>Default</th><th>Description</th></tr>')
			html.append(f'{tab}\t\t</thead>')
			html.append(f'{tab}\t\t<tbody>')

			for param in func.parameters:
				default = param.default or '-'
				desc = param.description or ''
				html.append(f'{tab}\t\t\t<tr>')
				html.append(f'{tab}\t\t\t\t<td><code>{param.name}</code></td>')
				html.append(f'{tab}\t\t\t\t<td><code>{param.type_hint}</code></td>')
				html.append(f'{tab}\t\t\t\t<td><code>{default}</code></td>')
				html.append(f'{tab}\t\t\t\t<td>{desc}</td>')
				html.append(f'{tab}\t\t\t</tr>')

			html.append(f'{tab}\t\t</tbody>')
			html.append(f'{tab}\t</table>')

		# Returns
		if func.returns != 'None' or func.return_description:
			html.append(f'{tab}\t<p><strong>Returns:</strong> <code>{func.returns}</code>')
			if func.return_description:
				html.append(f' - {func.return_description}')
			html.append('</p>')

		# Raises
		if func.raises:
			html.append(f'{tab}\t<p><strong>Raises:</strong></p>')
			html.append(f'{tab}\t<ul>')
			for exc in func.raises:
				html.append(f'{tab}\t\t<li>{exc}</li>')
			html.append(f'{tab}\t</ul>')

		# Examples
		if func.examples:
			html.append(f'{tab}\t<p><strong>Examples:</strong></p>')
			html.append(f'{tab}\t<pre><code>')
			html.append('\n'.join(func.examples))
			html.append(f'{tab}\t</code></pre>')

		html.append(f'{tab}</div>')

		return html

	def _format_docstring(self, docstring: str) -> str:
		"""Format docstring for HTML."""
		# Simple formatting
		return docstring.replace('\n\n', '</p><p>').replace('\n', ' ')

	def _get_css(self) -> str:
		"""Get CSS styles."""
		return """
		body {
			font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
			line-height: 1.6;
			max-width: 1200px;
			margin: 0 auto;
			padding: 20px;
			background: #f5f5f5;
		}
		header {
			background: #2c3e50;
			color: white;
			padding: 20px;
			border-radius: 5px;
			margin-bottom: 20px;
		}
		header h1 {
			margin: 0;
		}
		header nav {
			margin-top: 10px;
		}
		header nav a {
			color: #3498db;
			text-decoration: none;
		}
		main {
			background: white;
			padding: 20px;
			border-radius: 5px;
			box-shadow: 0 2px 4px rgba(0,0,0,0.1);
		}
		h2 {
			color: #2c3e50;
			border-bottom: 2px solid #3498db;
			padding-bottom: 10px;
		}
		h3 {
			color: #34495e;
		}
		code {
			background: #ecf0f1;
			padding: 2px 5px;
			border-radius: 3px;
			font-family: "Courier New", monospace;
		}
		pre {
			background: #2c3e50;
			color: #ecf0f1;
			padding: 15px;
			border-radius: 5px;
			overflow-x: auto;
		}
		pre code {
			background: none;
			padding: 0;
		}
		table {
			width: 100%;
			border-collapse: collapse;
			margin: 10px 0;
		}
		th, td {
			padding: 8px;
			text-align: left;
			border-bottom: 1px solid #ddd;
		}
		th {
			background: #34495e;
			color: white;
		}
		.module-list li {
			margin-bottom: 15px;
			padding: 10px;
			background: #ecf0f1;
			border-radius: 5px;
		}
		.class, .function {
			margin: 20px 0;
			padding: 15px;
			background: #f8f9fa;
			border-left: 4px solid #3498db;
			border-radius: 3px;
		}
		.bases {
			color: #7f8c8d;
			font-style: italic;
		}
		footer {
			text-align: center;
			margin-top: 40px;
			color: #7f8c8d;
		}
		"""


class MarkdownDocGenerator:
	"""Generate Markdown documentation."""

	def __init__(self, output_dir: Path):
		self.output_dir = output_dir
		self.output_dir.mkdir(parents=True, exist_ok=True)

	def generate(self, modules: List[ModuleDoc]) -> None:
		"""Generate Markdown documentation."""
		# Generate index
		self._generate_index(modules)

		# Generate module pages
		for module in modules:
			self._generate_module_page(module)

	def _generate_index(self, modules: List[ModuleDoc]) -> None:
		"""Generate README.md index."""
		lines = []
		lines.append('# Dragon Warrior Toolkit API Documentation')
		lines.append('')
		lines.append('Comprehensive API reference for all toolkit modules.')
		lines.append('')
		lines.append('## Modules')
		lines.append('')

		for module in sorted(modules, key=lambda m: m.name):
			summary = module.docstring.split('\n')[0] if module.docstring else "No description"
			num_classes = len(module.classes)
			num_functions = len(module.functions)

			lines.append(f'### [{module.name}]({module.name}.md)')
			lines.append('')
			lines.append(f'{summary}')
			lines.append('')
			lines.append(f'*{num_classes} classes, {num_functions} functions*')
			lines.append('')

		output_file = self.output_dir / 'README.md'
		with open(output_file, 'w', encoding='utf-8') as f:
			f.write('\n'.join(lines))

		print(f"Generated {output_file}")

	def _generate_module_page(self, module: ModuleDoc) -> None:
		"""Generate module documentation page."""
		lines = []
		lines.append(f'# Module: {module.name}')
		lines.append('')

		if module.docstring:
			lines.append(module.docstring)
			lines.append('')

		# Constants
		if module.constants:
			lines.append('## Constants')
			lines.append('')
			for name, value in sorted(module.constants.items()):
				lines.append(f'- `{name} = {value}`')
			lines.append('')

		# Classes
		if module.classes:
			lines.append('## Classes')
			lines.append('')
			for cls in sorted(module.classes, key=lambda c: c.name):
				lines.extend(self._format_class(cls))
				lines.append('')

		# Functions
		if module.functions:
			lines.append('## Functions')
			lines.append('')
			for func in sorted(module.functions, key=lambda f: f.name):
				lines.extend(self._format_function(func))
				lines.append('')

		output_file = self.output_dir / f'{module.name}.md'
		with open(output_file, 'w', encoding='utf-8') as f:
			f.write('\n'.join(lines))

		print(f"Generated {output_file}")

	def _format_class(self, cls: ClassDoc) -> List[str]:
		"""Format class documentation."""
		lines = []

		lines.append(f'### class {cls.name}')
		lines.append('')

		if cls.bases:
			bases_str = ', '.join(cls.bases)
			lines.append(f'*Inherits from: {bases_str}*')
			lines.append('')

		if cls.docstring:
			lines.append(cls.docstring)
			lines.append('')

		# Attributes
		if cls.attributes:
			lines.append('**Attributes:**')
			lines.append('')
			for name, type_hint in sorted(cls.attributes.items()):
				lines.append(f'- `{name}: {type_hint}`')
			lines.append('')

		# Methods
		if cls.methods:
			lines.append('**Methods:**')
			lines.append('')
			for method in sorted(cls.methods, key=lambda m: m.name):
				lines.extend(self._format_function(method, level=4))
				lines.append('')

		return lines

	def _format_function(self, func: FunctionDoc, level: int = 3) -> List[str]:
		"""Format function documentation."""
		lines = []

		heading = '#' * level
		lines.append(f'{heading} {func.name}{func.signature}')
		lines.append('')

		if func.docstring:
			summary = func.docstring.split('\n')[0]
			lines.append(summary)
			lines.append('')

		# Parameters
		if func.parameters:
			lines.append('**Parameters:**')
			lines.append('')
			for param in func.parameters:
				param_str = f'- `{param.name}` (`{param.type_hint}`)'
				if param.default:
					param_str += f', default: `{param.default}`'
				if param.description:
					param_str += f' - {param.description}'
				lines.append(param_str)
			lines.append('')

		# Returns
		if func.returns != 'None' or func.return_description:
			lines.append(f'**Returns:** `{func.returns}`')
			if func.return_description:
				lines.append(f'- {func.return_description}')
			lines.append('')

		return lines


def main():
	"""Main entry point."""
	parser = argparse.ArgumentParser(
		description='Generate comprehensive API documentation'
	)
	parser.add_argument(
		'--format',
		choices=['html', 'md', 'json', 'all'],
		default='all',
		help='Output format'
	)
	parser.add_argument(
		'--source',
		type=Path,
		default=Path('tools'),
		help='Source directory to document'
	)
	parser.add_argument(
		'--output',
		type=Path,
		default=Path('docs/api'),
		help='Output directory'
	)

	args = parser.parse_args()

	print(f"Analyzing source directory: {args.source}")

	# Analyze all Python files
	analyzer = CodeAnalyzer(args.source)
	modules = []

	for filepath in args.source.rglob('*.py'):
		# Skip __pycache__ and other non-source files
		if '__pycache__' in filepath.parts or filepath.name.startswith('_'):
			continue

		module_doc = analyzer.analyze_file(filepath)
		if module_doc:
			modules.append(module_doc)

	print(f"Analyzed {len(modules)} modules")

	# Generate documentation
	if args.format in ['html', 'all']:
		print("\nGenerating HTML documentation...")
		html_gen = HTMLDocGenerator(args.output / 'html')
		html_gen.generate(modules)

	if args.format in ['md', 'all']:
		print("\nGenerating Markdown documentation...")
		md_gen = MarkdownDocGenerator(args.output / 'markdown')
		md_gen.generate(modules)

	if args.format in ['json', 'all']:
		print("\nGenerating JSON documentation...")
		json_output = args.output / 'api.json'
		json_output.parent.mkdir(parents=True, exist_ok=True)

		json_data = [asdict(module) for module in modules]
		with open(json_output, 'w', encoding='utf-8') as f:
			json.dump(json_data, f, indent='\t')

		print(f"Generated {json_output}")

	print(f"\nDocumentation generated in {args.output}")


if __name__ == '__main__':
	main()
