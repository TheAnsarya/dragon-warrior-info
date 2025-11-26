#!/usr/bin/env python3
"""
API Documentation Generator for Dragon Warrior Toolkit

Generates comprehensive API reference documentation from Python docstrings.

Features:
- Extract docstrings from all modules
- Generate Markdown API reference
- Create function/class index
- Include usage examples
- Type hint documentation
- Cross-reference generation

Usage:
    python tools/generate_api_docs.py
    python tools/generate_api_docs.py --output docs/API_REFERENCE.md
    python tools/generate_api_docs.py --module tools.extract_to_binary

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import inspect
import importlib
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import ast
import re

# Modules to document
TOOLKIT_MODULES = [
    'tools.organize_chr_tiles',
    'tools.extract_all_data',
    'tools.reinsert_assets',
    'tools.extract_to_binary',
    'tools.binary_to_assets',
    'tools.assets_to_binary',
    'tools.binary_to_rom',
    'tools.analyze_monster_sprites',
    'tools.analyze_rom_space',
    'tools.analyze_text_frequency',
]


class APIDocGenerator:
    """Generate API documentation from Python modules"""

    def __init__(self, output_path: str = "docs/API_REFERENCE.md"):
        """
        Initialize documentation generator

        Args:
            output_path: Output file path for documentation
        """
        self.output_path = Path(output_path)
        self.documentation = []

    def extract_function_signature(self, func) -> str:
        """
        Extract function signature with type hints

        Args:
            func: Function object

        Returns:
            Formatted signature string
        """
        try:
            sig = inspect.signature(func)
            return str(sig)
        except (ValueError, TypeError):
            return "()"

    def extract_docstring(self, obj) -> Optional[str]:
        """
        Extract and format docstring

        Args:
            obj: Python object with docstring

        Returns:
            Formatted docstring or None
        """
        docstring = inspect.getdoc(obj)
        if not docstring:
            return None

        # Clean up docstring formatting
        lines = docstring.split('\n')
        formatted = []

        for line in lines:
            # Convert Args/Returns/Raises sections to Markdown
            if line.strip().endswith(':'):
                section = line.strip()
                if section in ['Args:', 'Returns:', 'Raises:', 'Yields:', 'Examples:', 'Note:', 'Warning:']:
                    formatted.append(f"**{section}**\n")
                    continue

            formatted.append(line)

        return '\n'.join(formatted)

    def document_function(self, func, module_name: str) -> Dict[str, Any]:
        """
        Document a single function

        Args:
            func: Function object
            module_name: Module name for context

        Returns:
            Function documentation dict
        """
        name = func.__name__
        signature = self.extract_function_signature(func)
        docstring = self.extract_docstring(func)

        # Get source file and line number
        try:
            source_file = inspect.getsourcefile(func)
            source_lines = inspect.getsourcelines(func)
            line_number = source_lines[1] if source_lines else 0
        except (TypeError, OSError):
            source_file = "unknown"
            line_number = 0

        return {
            'type': 'function',
            'name': name,
            'full_name': f"{module_name}.{name}",
            'signature': signature,
            'docstring': docstring,
            'source_file': source_file,
            'line_number': line_number
        }

    def document_class(self, cls, module_name: str) -> Dict[str, Any]:
        """
        Document a class and its methods

        Args:
            cls: Class object
            module_name: Module name for context

        Returns:
            Class documentation dict
        """
        name = cls.__name__
        docstring = self.extract_docstring(cls)

        # Get methods
        methods = []
        for attr_name in dir(cls):
            if attr_name.startswith('_') and attr_name not in ['__init__']:
                continue  # Skip private methods except __init__

            attr = getattr(cls, attr_name)
            if callable(attr) and not inspect.isclass(attr):
                method_doc = self.document_function(attr, f"{module_name}.{name}")
                method_doc['type'] = 'method'
                methods.append(method_doc)

        return {
            'type': 'class',
            'name': name,
            'full_name': f"{module_name}.{name}",
            'docstring': docstring,
            'methods': methods
        }

    def document_module(self, module_name: str) -> Dict[str, Any]:
        """
        Document an entire module

        Args:
            module_name: Module name to document

        Returns:
            Module documentation dict
        """
        try:
            module = importlib.import_module(module_name)
        except ImportError as e:
            print(f"⚠ Warning: Could not import {module_name}: {e}")
            return None

        # Get module docstring
        module_docstring = self.extract_docstring(module)

        # Get module-level functions and classes
        functions = []
        classes = []

        for name in dir(module):
            if name.startswith('_'):
                continue

            obj = getattr(module, name)

            # Check if object is defined in this module (not imported)
            if hasattr(obj, '__module__') and obj.__module__ != module_name:
                continue

            if inspect.isfunction(obj):
                functions.append(self.document_function(obj, module_name))
            elif inspect.isclass(obj):
                classes.append(self.document_class(obj, module_name))

        return {
            'name': module_name,
            'docstring': module_docstring,
            'functions': functions,
            'classes': classes
        }

    def generate_markdown(self, modules: List[Dict[str, Any]]) -> str:
        """
        Generate Markdown documentation

        Args:
            modules: List of module documentation dicts

        Returns:
            Markdown documentation string
        """
        md = []

        # Header
        md.append("# Dragon Warrior Toolkit API Reference\n")
        md.append("Complete API documentation for the Dragon Warrior ROM Hacking Toolkit.\n")
        md.append("## Table of Contents\n")

        # TOC
        for module in modules:
            if not module:
                continue
            md.append(f"- [{module['name']}](#{module['name'].replace('.', '-')})")

        md.append("\n---\n")

        # Module documentation
        for module in modules:
            if not module:
                continue

            md.append(f"\n## {module['name']}\n")

            if module['docstring']:
                md.append(f"{module['docstring']}\n")

            # Classes
            if module['classes']:
                md.append("\n### Classes\n")

                for cls in module['classes']:
                    md.append(f"\n#### `{cls['name']}`\n")

                    if cls['docstring']:
                        md.append(f"{cls['docstring']}\n")

                    # Methods
                    if cls['methods']:
                        md.append("\n**Methods:**\n")

                        for method in cls['methods']:
                            md.append(f"\n##### `{method['name']}{method['signature']}`\n")

                            if method['docstring']:
                                md.append(f"{method['docstring']}\n")

            # Functions
            if module['functions']:
                md.append("\n### Functions\n")

                for func in module['functions']:
                    md.append(f"\n#### `{func['name']}{func['signature']}`\n")

                    if func['docstring']:
                        md.append(f"{func['docstring']}\n")

        md.append("\n---\n")
        md.append("\n*Generated by Dragon Warrior Toolkit API Documentation Generator*\n")

        return '\n'.join(md)

    def generate(self, module_names: Optional[List[str]] = None):
        """
        Generate complete API documentation

        Args:
            module_names: Optional list of module names to document
        """
        if module_names is None:
            module_names = TOOLKIT_MODULES

        print("=" * 70)
        print("Dragon Warrior Toolkit - API Documentation Generator")
        print("=" * 70)

        print(f"\n📚 Documenting {len(module_names)} modules...")

        # Document each module
        modules = []
        for module_name in module_names:
            print(f"  - {module_name}...", end=' ')
            module_doc = self.document_module(module_name)

            if module_doc:
                func_count = len(module_doc['functions'])
                class_count = len(module_doc['classes'])
                print(f"✓ ({class_count} classes, {func_count} functions)")
                modules.append(module_doc)
            else:
                print("⚠ Skipped")

        # Generate Markdown
        print(f"\n📝 Generating Markdown documentation...")
        markdown = self.generate_markdown(modules)

        # Write to file
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

        print(f"\n✓ Documentation written to: {self.output_path}")
        print(f"  Size: {len(markdown):,} characters")
        print(f"  Lines: {len(markdown.splitlines()):,}")

        # Statistics
        total_classes = sum(len(m['classes']) for m in modules)
        total_functions = sum(len(m['functions']) for m in modules)
        total_methods = sum(
            sum(len(c['methods']) for c in m['classes'])
            for m in modules
        )

        print("\n📊 Documentation Statistics:")
        print(f"  Modules: {len(modules)}")
        print(f"  Classes: {total_classes}")
        print(f"  Functions: {total_functions}")
        print(f"  Methods: {total_methods}")
        print(f"  Total API entries: {total_classes + total_functions + total_methods}")

        print("\n" + "=" * 70)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate API documentation for Dragon Warrior Toolkit',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate complete API documentation
  python tools/generate_api_docs.py

  # Generate for specific module
  python tools/generate_api_docs.py --module tools.extract_to_binary

  # Custom output location
  python tools/generate_api_docs.py --output custom_docs/API.md
        """
    )

    parser.add_argument(
        '--output',
        default='docs/API_REFERENCE.md',
        help='Output file path (default: docs/API_REFERENCE.md)'
    )

    parser.add_argument(
        '--module',
        action='append',
        help='Specific module to document (can be used multiple times)'
    )

    args = parser.parse_args()

    # Determine which modules to document
    modules = args.module if args.module else None

    # Generate documentation
    generator = APIDocGenerator(args.output)
    generator.generate(modules)

    return 0


if __name__ == '__main__':
    sys.exit(main())
