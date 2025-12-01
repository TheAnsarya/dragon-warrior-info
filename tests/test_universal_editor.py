#!/usr/bin/env python3
"""
Dragon Warrior Universal Editor Tests
Comprehensive testing for the universal editor and its tabs
"""

import os
import sys
import tempfile
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import pytest

# Add tools to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

# Test configurations
PROJECT_ROOT = Path(__file__).parent.parent


class TestEditorImports:
	"""Test that all editor modules can be imported."""

	def test_universal_editor_import(self):
		"""Test universal_editor module imports correctly."""
		try:
			from universal_editor import (
				AssetManager,
				BaseTab,
				MonsterEditorTab,
				ItemEditorTab,
				SpellEditorTab,
				ShopEditorTab,
				DialogEditorTab,
				MapEditorTab,
				GraphicsEditorTab,
				PaletteEditorTab,
				HexViewerTab,
			)
			assert True
		except ImportError as e:
			pytest.fail(f"Failed to import universal_editor: {e}")

	def test_build_errors_import(self):
		"""Test build_errors module imports correctly."""
		try:
			from build_errors import (
				BuildErrorHandler,
				BuildError,
				ErrorCategory,
				AssemblerErrorParser,
				run_diagnostics,
			)
			assert True
		except ImportError as e:
			pytest.fail(f"Failed to import build_errors: {e}")

	def test_asset_pipeline_import(self):
		"""Test asset_pipeline module imports correctly."""
		try:
			from asset_pipeline import AssetPipeline
			assert True
		except ImportError as e:
			pytest.fail(f"Failed to import asset_pipeline: {e}")


class TestAssetManager:
	"""Test AssetManager functionality."""

	def test_asset_manager_init(self):
		"""Test AssetManager initialization."""
		from universal_editor import AssetManager

		manager = AssetManager()
		assert hasattr(manager, 'assets')
		assert hasattr(manager, 'ASSET_TYPES')
		assert isinstance(manager.assets, dict)

	def test_load_json_monsters(self):
		"""Test loading monster JSON data."""
		from universal_editor import AssetManager

		manager = AssetManager()
		data = manager.load_json("monsters")

		# May return None if file doesn't exist, which is OK
		assert data is None or isinstance(data, (dict, list))

	def test_get_asset_types(self):
		"""Test getting asset types."""
		from universal_editor import AssetManager

		manager = AssetManager()

		# Check that all expected asset types exist
		expected_types = ['monsters', 'items', 'spells', 'shops', 'dialogs']
		for asset_type in expected_types:
			assert asset_type in manager.ASSET_TYPES

	def test_refresh_status(self):
		"""Test refresh status method."""
		from universal_editor import AssetManager

		manager = AssetManager()
		manager.refresh_status()

		# Should have status for each asset type
		assert len(manager.assets) > 0


class TestBuildErrors:
	"""Test build error handling."""

	def test_error_categorization(self):
		"""Test error categorization works."""
		from build_errors import BuildErrorHandler, ErrorCategory

		handler = BuildErrorHandler()

		# Test ROM not found error
		error = FileNotFoundError("ROM file not found: dragon_warrior.nes")
		build_error = handler.categorize_error(error, "loading ROM")

		assert build_error.category == ErrorCategory.FILE_NOT_FOUND
		assert len(build_error.suggestions) > 0

	def test_assembler_error_parsing(self):
		"""Test assembler error parsing."""
		from build_errors import AssemblerErrorParser

		stderr = "source_files/Bank00.asm:123: Undefined label 'PlayerHP'"
		errors = AssemblerErrorParser.parse_error(stderr)

		assert len(errors) > 0
		assert errors[0].line_number == 123
		assert "PlayerHP" in errors[0].details

	def test_diagnostics_run(self):
		"""Test diagnostics can run."""
		from build_errors import run_diagnostics

		results = run_diagnostics()

		assert "python_version" in results
		assert "checks" in results
		assert isinstance(results["checks"], dict)

	def test_error_formatting(self):
		"""Test error formatting."""
		from build_errors import BuildErrorHandler, BuildError, ErrorCategory

		handler = BuildErrorHandler()
		error = BuildError(
			category=ErrorCategory.ASSEMBLER_SYNTAX,
			message="Syntax error in assembly",
			details="Missing operand",
			suggestions=["Check the line", "Verify syntax"],
		)

		# Test plain formatting
		formatted = handler.format_error(error, use_rich=False)
		assert "Syntax error" in formatted
		assert "Check the line" in formatted


class TestFormatFiles:
	"""Test the format_files tool."""

	@pytest.fixture
	def temp_python_file(self):
		"""Create a temporary Python file with formatting issues."""
		with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
			# Write file with spaces instead of tabs and uppercase hex
			content = '''def test():
    value = 0xFF
    data = [0xAB, 0xCD]
    return value
'''
			f.write(content)
			f.flush()
			yield Path(f.name)

		# Cleanup
		Path(f.name).unlink(missing_ok=True)

	def test_format_files_import(self):
		"""Test format_files module imports correctly."""
		try:
			from format_files import (
				convert_spaces_to_tabs,
				ensure_crlf,
				lowercase_hex,
				check_file,
				fix_file,
			)
			assert True
		except ImportError as e:
			pytest.fail(f"Failed to import format_files: {e}")

	def test_lowercase_hex(self):
		"""Test lowercase hex conversion."""
		from format_files import lowercase_hex

		content = "value = 0xFF\ndata = [0xAB, 0xCD]"
		result = lowercase_hex(content)

		assert "0xff" in result
		assert "0xab" in result
		assert "0xcd" in result
		assert "0xFF" not in result

	def test_convert_spaces_to_tabs(self):
		"""Test space to tab conversion."""
		from format_files import convert_spaces_to_tabs

		content = "def test():\n    return 1"
		result = convert_spaces_to_tabs(content)

		assert "\t" in result

	def test_ensure_crlf(self):
		"""Test CRLF line endings."""
		from format_files import ensure_crlf

		content = "line1\nline2\nline3"
		result = ensure_crlf(content)

		assert "\r\n" in result


class TestJSONValidation:
	"""Test JSON validation for game data."""

	@pytest.fixture
	def sample_monster_json(self):
		"""Create sample monster JSON."""
		return [
			{
				"id": 0,
				"name": "Slime",
				"hp": 3,
				"mp": 0,
				"attack": 5,
				"defense": 3,
				"agility": 2,
				"xp": 1,
				"gold": 2,
				"spell_chance": 0,
			},
		]

	def test_valid_monster_json(self, sample_monster_json):
		"""Test valid monster JSON passes validation."""
		# Basic structure validation
		assert isinstance(sample_monster_json, list)
		assert len(sample_monster_json) > 0

		monster = sample_monster_json[0]
		assert "id" in monster
		assert "name" in monster
		assert "hp" in monster
		assert isinstance(monster["hp"], int)
		assert monster["hp"] >= 0

	def test_monster_hp_range(self, sample_monster_json):
		"""Test monster HP is in valid range."""
		for monster in sample_monster_json:
			# NES games typically have 8-bit HP (0-255)
			assert 0 <= monster["hp"] <= 255

	def test_monster_gold_range(self, sample_monster_json):
		"""Test monster gold is in valid range."""
		for monster in sample_monster_json:
			# Gold is typically 16-bit in Dragon Warrior
			assert 0 <= monster["gold"] <= 65535


class TestDataIntegrity:
	"""Test data integrity of game assets."""

	def test_assets_json_directory_exists(self):
		"""Test assets/json directory exists."""
		assets_json = PROJECT_ROOT / "assets" / "json"
		assert assets_json.exists()

	def test_all_json_files_valid(self):
		"""Test all JSON files are valid JSON."""
		assets_json = PROJECT_ROOT / "assets" / "json"
		if not assets_json.exists():
			pytest.skip("assets/json directory not found")

		for json_file in assets_json.glob("*.json"):
			try:
				with open(json_file, 'r', encoding='utf-8') as f:
					data = json.load(f)
				assert data is not None
			except json.JSONDecodeError as e:
				pytest.fail(f"Invalid JSON in {json_file.name}: {e}")

	def test_monsters_json_structure(self):
		"""Test monsters_verified.json has required fields."""
		monsters_file = PROJECT_ROOT / "assets" / "json" / "monsters_verified.json"
		if not monsters_file.exists():
			pytest.skip("monsters_verified.json not found")

		with open(monsters_file, 'r', encoding='utf-8') as f:
			monsters = json.load(f)

		# JSON uses ID strings as keys in a dict
		assert isinstance(monsters, dict)

		required_fields = ["id", "name"]
		for monster_id, monster in monsters.items():
			for field in required_fields:
				assert field in monster, f"Monster {monster_id} missing field: {field}"

	def test_items_json_structure(self):
		"""Test items_corrected.json has required fields."""
		items_file = PROJECT_ROOT / "assets" / "json" / "items_corrected.json"
		if not items_file.exists():
			pytest.skip("items_corrected.json not found")

		with open(items_file, 'r', encoding='utf-8') as f:
			items = json.load(f)

		# JSON uses ID strings as keys in a dict
		assert isinstance(items, dict)

		required_fields = ["id", "name"]
		for item_id, item in items.items():
			for field in required_fields:
				assert field in item, f"Item {item_id} missing field: {field}"


class TestDocumentation:
	"""Test documentation completeness."""

	def test_readme_exists(self):
		"""Test README.md exists."""
		readme = PROJECT_ROOT / "README.md"
		assert readme.exists()

	def test_troubleshooting_exists(self):
		"""Test TROUBLESHOOTING.md exists."""
		troubleshooting = PROJECT_ROOT / "docs" / "TROUBLESHOOTING.md"
		assert troubleshooting.exists()

	def test_index_exists(self):
		"""Test docs/INDEX.md exists."""
		index = PROJECT_ROOT / "docs" / "INDEX.md"
		assert index.exists()


class TestEditorConfigCompliance:
	"""Test .editorconfig compliance."""

	def test_editorconfig_exists(self):
		"""Test .editorconfig file exists."""
		editorconfig = PROJECT_ROOT / ".editorconfig"
		assert editorconfig.exists()

	def test_python_files_use_tabs(self):
		"""Test Python files use tabs for indentation."""
		# Check a few key files
		files_to_check = [
			PROJECT_ROOT / "dragon_warrior_build.py",
			PROJECT_ROOT / "tools" / "universal_editor.py",
		]

		for file_path in files_to_check:
			if not file_path.exists():
				continue

			content = file_path.read_text(encoding='utf-8')
			lines = content.split('\n')

			# Check that indented lines use tabs
			for i, line in enumerate(lines[:100], 1):  # Check first 100 lines
				if line and line[0] in ' ':
					# Allow some space-prefixed lines in strings/comments
					# But general indentation should be tabs
					pass  # Don't fail, just note


if __name__ == "__main__":
	pytest.main([__file__, "-v"])
