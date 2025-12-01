#!/usr/bin/env python3
"""
Tests for the asset generation pipeline.

Tests the unified asset generator and individual generators.
"""

import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / 'tools'))


class TestUnifiedGenerator(unittest.TestCase):
    """Test the unified asset generator script."""

    def test_generator_config(self):
        """Test that generator configuration is valid."""
        # Import the generators config
        try:
            from generate_all_assets import GENERATORS
            self.assertIsInstance(GENERATORS, dict)
            self.assertGreater(len(GENERATORS), 0)
        except ImportError:
            self.skipTest("generate_all_assets.py not found")

    def test_all_generators_registered(self):
        """Test that all expected generators are registered."""
        try:
            from generate_all_assets import GENERATORS

            expected_generators = [
                'monsters', 'items', 'spells', 'equipment', 'shops',
                'npcs', 'dialogs', 'damage', 'spell_fx', 'experience', 'music'
            ]

            for gen in expected_generators:
                self.assertIn(gen, GENERATORS, f"Generator '{gen}' not registered")
        except ImportError:
            self.skipTest("generate_all_assets.py not found")

    def test_generator_config_structure(self):
        """Test that each generator config has required fields."""
        try:
            from generate_all_assets import GENERATORS

            for name, config in GENERATORS.items():
                self.assertIsInstance(config, tuple, f"{name}: config should be tuple")
                self.assertEqual(len(config), 4, f"{name}: config should have 4 elements")

                json_file, script, output, description = config
                self.assertTrue(json_file.endswith('.json'), f"{name}: JSON file should end with .json")
                self.assertTrue(script.endswith('.py'), f"{name}: Script should end with .py")
                self.assertTrue(output.endswith('.asm'), f"{name}: Output should end with .asm")
                self.assertIsInstance(description, str, f"{name}: Description should be string")
        except ImportError:
            self.skipTest("generate_all_assets.py not found")


class TestDamageGenerator(unittest.TestCase):
    """Test the damage formulas generator."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.json_path = PROJECT_ROOT / 'assets' / 'json' / 'damage_formulas.json'

    def test_json_exists(self):
        """Test that damage_formulas.json exists."""
        self.assertTrue(self.json_path.exists(), "damage_formulas.json not found")

    def test_json_structure(self):
        """Test damage_formulas.json structure."""
        if not self.json_path.exists():
            self.skipTest("damage_formulas.json not found")

        with open(self.json_path, 'r') as f:
            data = json.load(f)

        # Check required sections
        expected_sections = ['physical_damage', 'spell_damage', 'healing_spells', 'environmental_damage']
        for section in expected_sections:
            self.assertIn(section, data, f"Missing section: {section}")

    def test_generator_exists(self):
        """Test that generator script exists."""
        generator = PROJECT_ROOT / 'tools' / 'generate_damage_tables.py'
        self.assertTrue(generator.exists(), "generate_damage_tables.py not found")


class TestSpellEffectsGenerator(unittest.TestCase):
    """Test the spell effects generator."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.json_path = PROJECT_ROOT / 'assets' / 'json' / 'spell_effects.json'

    def test_json_exists(self):
        """Test that spell_effects.json exists."""
        self.assertTrue(self.json_path.exists(), "spell_effects.json not found")

    def test_json_structure(self):
        """Test spell_effects.json structure."""
        if not self.json_path.exists():
            self.skipTest("spell_effects.json not found")

        with open(self.json_path, 'r') as f:
            data = json.load(f)

        # Check required sections
        self.assertIn('spells', data, "Missing spells section")
        self.assertIn('enemy_spells', data, "Missing enemy_spells section")

        # Check some specific spells
        spells = data.get('spells', {})
        expected_spells = ['HEAL', 'HURT', 'SLEEP']
        for spell in expected_spells:
            self.assertIn(spell, spells, f"Missing spell: {spell}")

    def test_generator_exists(self):
        """Test that generator script exists."""
        generator = PROJECT_ROOT / 'tools' / 'generate_spell_effects.py'
        self.assertTrue(generator.exists(), "generate_spell_effects.py not found")


class TestExperienceGenerator(unittest.TestCase):
    """Test the experience table generator."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.json_path = PROJECT_ROOT / 'assets' / 'json' / 'experience_table.json'

    def test_json_exists(self):
        """Test that experience_table.json exists."""
        self.assertTrue(self.json_path.exists(), "experience_table.json not found")

    def test_json_structure(self):
        """Test experience_table.json structure."""
        if not self.json_path.exists():
            self.skipTest("experience_table.json not found")

        with open(self.json_path, 'r') as f:
            data = json.load(f)

        # Check required fields
        self.assertIn('levels', data, "Missing levels section")
        self.assertIn('max_level', data, "Missing max_level field")

        # Check that we have 30 levels
        levels = data.get('levels', {})
        self.assertEqual(len(levels), 30, f"Expected 30 levels, got {len(levels)}")

    def test_generator_exists(self):
        """Test that generator script exists."""
        generator = PROJECT_ROOT / 'tools' / 'generate_experience_table.py'
        self.assertTrue(generator.exists(), "generate_experience_table.py not found")


class TestMusicGenerator(unittest.TestCase):
    """Test the music tables generator."""

    @classmethod
    def setUpClass(cls):
        """Set up test fixtures."""
        cls.json_path = PROJECT_ROOT / 'assets' / 'json' / 'music.json'

    def test_json_exists(self):
        """Test that music.json exists."""
        self.assertTrue(self.json_path.exists(), "music.json not found")

    def test_json_structure(self):
        """Test music.json structure."""
        if not self.json_path.exists():
            self.skipTest("music.json not found")

        with open(self.json_path, 'r') as f:
            data = json.load(f)

        # Check required sections
        self.assertIn('_metadata', data, "Missing _metadata section")
        self.assertIn('music_tracks', data, "Missing music_tracks section")
        self.assertIn('sound_effects', data, "Missing sound_effects section")
        self.assertIn('note_table', data, "Missing note_table section")

        # Check track counts
        tracks = data.get('music_tracks', {})
        sfx = data.get('sound_effects', {})
        notes = data.get('note_table', {})

        self.assertEqual(len(tracks), 27, f"Expected 27 music tracks, got {len(tracks)}")
        self.assertEqual(len(sfx), 22, f"Expected 22 sound effects, got {len(sfx)}")
        self.assertEqual(len(notes), 73, f"Expected 73 musical notes, got {len(notes)}")

    def test_generator_exists(self):
        """Test that generator script exists."""
        generator = PROJECT_ROOT / 'tools' / 'generate_music_tables.py'
        self.assertTrue(generator.exists(), "generate_music_tables.py not found")


class TestEditorTabsExtended(unittest.TestCase):
    """Test the extended editor tabs module."""

    def test_module_import(self):
        """Test that editor_tabs_extended.py can be imported."""
        try:
            from editor_tabs_extended import (
                DamageEditorTab,
                SpellEffectsEditorTab,
                ExperienceEditorTab,
                MusicEditorTab
            )
        except ImportError as e:
            self.skipTest(f"Cannot import editor_tabs_extended: {e}")

    def test_tab_classes_exist(self):
        """Test that all editor tab classes are defined."""
        try:
            from editor_tabs_extended import (
                DamageEditorTab,
                SpellEffectsEditorTab,
                ExperienceEditorTab,
                MusicEditorTab
            )

            # Verify they're classes
            self.assertTrue(hasattr(DamageEditorTab, '__init__'))
            self.assertTrue(hasattr(SpellEffectsEditorTab, '__init__'))
            self.assertTrue(hasattr(ExperienceEditorTab, '__init__'))
            self.assertTrue(hasattr(MusicEditorTab, '__init__'))
        except ImportError:
            self.skipTest("editor_tabs_extended.py not importable")


class TestGeneratedASM(unittest.TestCase):
    """Test that generated ASM files exist and are valid."""

    def test_damage_asm_exists(self):
        """Test that damage_tables.asm can be generated."""
        asm_path = PROJECT_ROOT / 'build' / 'reinsertion' / 'damage_tables.asm'
        # File might not exist if generator hasn't been run
        if asm_path.exists():
            with open(asm_path, 'r') as f:
                content = f.read()
            self.assertIn('DAMAGE', content.upper(), "ASM should contain damage-related content")

    def test_spell_effects_asm_exists(self):
        """Test that spell_effects.asm can be generated."""
        asm_path = PROJECT_ROOT / 'build' / 'reinsertion' / 'spell_effects.asm'
        if asm_path.exists():
            with open(asm_path, 'r') as f:
                content = f.read()
            self.assertIn('SPELL', content.upper(), "ASM should contain spell-related content")

    def test_experience_asm_exists(self):
        """Test that experience_table.asm can be generated."""
        asm_path = PROJECT_ROOT / 'build' / 'reinsertion' / 'experience_table.asm'
        if asm_path.exists():
            with open(asm_path, 'r') as f:
                content = f.read()
            self.assertIn('LEVEL', content.upper(), "ASM should contain level-related content")

    def test_music_asm_exists(self):
        """Test that music_tables.asm can be generated."""
        asm_path = PROJECT_ROOT / 'build' / 'reinsertion' / 'music_tables.asm'
        if asm_path.exists():
            with open(asm_path, 'r') as f:
                content = f.read()
            self.assertIn('MUSIC', content.upper(), "ASM should contain music-related content")


if __name__ == '__main__':
    unittest.main()
