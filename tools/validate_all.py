#!/usr/bin/env python3
"""
Comprehensive Validation Test Suite

Validates all extracted data and ROM modifications for correctness.

Features:
- Monster data validation
- Spell data validation
- Item data validation
- Graphics validation
- Binary integrity checks
- Cross-reference validation

Usage:
    python tools/validate_all.py
    python tools/validate_all.py --quick
    python tools/validate_all.py --verbose

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import json
import argparse
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import struct

# Default paths
DEFAULT_ASSETS = "extracted_assets"


class ValidationError(Exception):
    """Custom validation error"""
    pass


class DataValidator:
    """Comprehensive data validation"""
    
    def __init__(self, assets_dir: str = DEFAULT_ASSETS):
        """
        Initialize validator
        
        Args:
            assets_dir: Assets directory
        """
        self.assets_dir = Path(assets_dir)
        self.json_dir = self.assets_dir / "json"
        self.graphics_dir = self.assets_dir / "graphics"
        self.binary_dir = self.assets_dir / "binary"
        
        self.errors = []
        self.warnings = []
        
    def log_error(self, category: str, message: str):
        """Log validation error"""
        self.errors.append(f"[{category}] {message}")
        print(f"  ❌ {message}")
    
    def log_warning(self, category: str, message: str):
        """Log validation warning"""
        self.warnings.append(f"[{category}] {message}")
        print(f"  ⚠ {message}")
    
    def load_json(self, filename: str) -> Optional[List[Dict]]:
        """Load JSON file"""
        filepath = self.json_dir / filename
        
        if not filepath.exists():
            self.log_error("FILE", f"{filename} not found")
            return None
        
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.log_error("JSON", f"Failed to parse {filename}: {e}")
            return None
    
    def validate_monsters(self) -> bool:
        """Validate monster data"""
        print("\n--- Validating Monster Data ---")
        
        monsters = self.load_json('monsters.json')
        if monsters is None:
            return False
        
        valid = True
        
        # Check count
        expected_count = 39
        if len(monsters) < expected_count:
            self.log_error("MONSTERS", f"Expected {expected_count} monsters, found {len(monsters)}")
            valid = False
        elif len(monsters) > expected_count:
            self.log_warning("MONSTERS", f"More than {expected_count} monsters found ({len(monsters)})")
        
        # Validate each monster
        for i, monster in enumerate(monsters):
            # Check required fields
            required_fields = ['id', 'name', 'hp', 'attack', 'defense', 'agility',
                             'spell', 'm_defense', 'xp', 'gold']
            
            for field in required_fields:
                if field not in monster:
                    self.log_error("MONSTERS", f"Monster {i} missing field: {field}")
                    valid = False
            
            # Validate ID
            if monster.get('id') != i:
                self.log_error("MONSTERS", f"Monster {i} has incorrect ID: {monster.get('id')}")
                valid = False
            
            # Validate HP (must be 1-255)
            hp = monster.get('hp', 0)
            if not (1 <= hp <= 255):
                self.log_error("MONSTERS", f"{monster.get('name')}: Invalid HP {hp} (must be 1-255)")
                valid = False
            
            # Validate attack (0-255)
            attack = monster.get('attack', 0)
            if not (0 <= attack <= 255):
                self.log_error("MONSTERS", f"{monster.get('name')}: Invalid attack {attack} (must be 0-255)")
                valid = False
            
            # Validate defense (0-255)
            defense = monster.get('defense', 0)
            if not (0 <= defense <= 255):
                self.log_error("MONSTERS", f"{monster.get('name')}: Invalid defense {defense} (must be 0-255)")
                valid = False
            
            # Validate spell (0-9, 0 = none)
            spell = monster.get('spell', 0)
            if not (0 <= spell <= 9):
                self.log_error("MONSTERS", f"{monster.get('name')}: Invalid spell {spell} (must be 0-9)")
                valid = False
            
            # Validate XP (0-65535)
            xp = monster.get('xp', 0)
            if not (0 <= xp <= 65535):
                self.log_error("MONSTERS", f"{monster.get('name')}: Invalid XP {xp} (must be 0-65535)")
                valid = False
            
            # Validate gold (0-65535)
            gold = monster.get('gold', 0)
            if not (0 <= gold <= 65535):
                self.log_error("MONSTERS", f"{monster.get('name')}: Invalid gold {gold} (must be 0-65535)")
                valid = False
        
        if valid:
            print(f"  ✓ Validated {len(monsters)} monsters")
        
        return valid
    
    def validate_spells(self) -> bool:
        """Validate spell data"""
        print("\n--- Validating Spell Data ---")
        
        spells = self.load_json('spells.json')
        if spells is None:
            return False
        
        valid = True
        
        # Check count
        expected_count = 10
        if len(spells) != expected_count:
            self.log_warning("SPELLS", f"Expected {expected_count} spells, found {len(spells)}")
        
        # Validate each spell
        for i, spell in enumerate(spells):
            # Check required fields
            required_fields = ['id', 'name', 'mp_cost', 'power']
            
            for field in required_fields:
                if field not in spell:
                    self.log_error("SPELLS", f"Spell {i} missing field: {field}")
                    valid = False
            
            # Validate MP cost (0-255)
            mp_cost = spell.get('mp_cost', 0)
            if not (0 <= mp_cost <= 255):
                self.log_error("SPELLS", f"{spell.get('name')}: Invalid MP cost {mp_cost} (must be 0-255)")
                valid = False
            
            # Validate power (0-255)
            power = spell.get('power', 0)
            if not (0 <= power <= 255):
                self.log_error("SPELLS", f"{spell.get('name')}: Invalid power {power} (must be 0-255)")
                valid = False
        
        if valid:
            print(f"  ✓ Validated {len(spells)} spells")
        
        return valid
    
    def validate_items(self) -> bool:
        """Validate item data"""
        print("\n--- Validating Item Data ---")
        
        items = self.load_json('items.json')
        if items is None:
            return False
        
        valid = True
        
        # Check count
        expected_count = 32
        if len(items) != expected_count:
            self.log_warning("ITEMS", f"Expected {expected_count} items, found {len(items)}")
        
        # Validate each item
        for i, item in enumerate(items):
            # Check required fields
            required_fields = ['id', 'name', 'buy_price', 'sell_price',
                             'attack_bonus', 'defense_bonus']
            
            for field in required_fields:
                if field not in item:
                    self.log_error("ITEMS", f"Item {i} missing field: {field}")
                    valid = False
            
            # Validate prices (0-65535)
            buy_price = item.get('buy_price', 0)
            if not (0 <= buy_price <= 65535):
                self.log_error("ITEMS", f"{item.get('name')}: Invalid buy price {buy_price}")
                valid = False
            
            sell_price = item.get('sell_price', 0)
            if not (0 <= sell_price <= 65535):
                self.log_error("ITEMS", f"{item.get('name')}: Invalid sell price {sell_price}")
                valid = False
            
            # Validate bonuses (-128 to 127)
            attack_bonus = item.get('attack_bonus', 0)
            if not (-128 <= attack_bonus <= 127):
                self.log_error("ITEMS", f"{item.get('name')}: Invalid attack bonus {attack_bonus}")
                valid = False
            
            defense_bonus = item.get('defense_bonus', 0)
            if not (-128 <= defense_bonus <= 127):
                self.log_error("ITEMS", f"{item.get('name')}: Invalid defense bonus {defense_bonus}")
                valid = False
        
        if valid:
            print(f"  ✓ Validated {len(items)} items")
        
        return valid
    
    def validate_cross_references(self) -> bool:
        """Validate cross-references between data"""
        print("\n--- Validating Cross-References ---")
        
        monsters = self.load_json('monsters.json')
        spells = self.load_json('spells.json')
        
        if not monsters or not spells:
            return False
        
        valid = True
        
        # Check monster spell references
        spell_ids = {spell['id'] for spell in spells}
        
        for monster in monsters:
            spell_id = monster.get('spell', 0)
            
            # Spell 0 means no spell
            if spell_id > 0 and spell_id not in spell_ids:
                self.log_error(
                    "CROSS-REF",
                    f"{monster['name']}: References non-existent spell ID {spell_id}"
                )
                valid = False
        
        if valid:
            print("  ✓ All cross-references valid")
        
        return valid
    
    def validate_graphics(self) -> bool:
        """Validate graphics data"""
        print("\n--- Validating Graphics Data ---")
        
        # Check for chr_tiles.png
        chr_file = self.graphics_dir / "chr_tiles.png"
        
        if not chr_file.exists():
            self.log_warning("GRAPHICS", "chr_tiles.png not found")
            return True  # Not critical
        
        try:
            from PIL import Image
            
            img = Image.open(chr_file)
            width, height = img.size
            
            # CHR tiles should be 256x256 (32x32 tiles of 8x8 pixels)
            expected_size = (256, 256)
            if (width, height) != expected_size:
                self.log_warning(
                    "GRAPHICS",
                    f"chr_tiles.png size is {width}x{height}, expected {expected_size[0]}x{expected_size[1]}"
                )
            else:
                print(f"  ✓ Graphics validated ({width}x{height})")
            
            return True
        except ImportError:
            self.log_warning("GRAPHICS", "Pillow not installed, skipping graphics validation")
            return True
        except Exception as e:
            self.log_error("GRAPHICS", f"Failed to validate graphics: {e}")
            return False
    
    def validate_binary_integrity(self) -> bool:
        """Validate binary file integrity"""
        print("\n--- Validating Binary Integrity ---")
        
        if not self.binary_dir.exists():
            self.log_warning("BINARY", "Binary directory not found")
            return True  # Not critical
        
        valid = True
        
        # Check for .dwdata files
        binary_files = list(self.binary_dir.glob("*.dwdata"))
        
        if not binary_files:
            self.log_warning("BINARY", "No .dwdata files found")
            return True
        
        for binary_file in binary_files:
            try:
                with open(binary_file, 'rb') as f:
                    # Read header
                    magic = f.read(4)
                    
                    if magic != b'DWDT':
                        self.log_error("BINARY", f"{binary_file.name}: Invalid magic (expected DWDT)")
                        valid = False
                        continue
                    
                    # Read version
                    version = struct.unpack('<HH', f.read(4))
                    
                    if version != (1, 0):
                        self.log_warning("BINARY", f"{binary_file.name}: Version {version[0]}.{version[1]}")
                    
                    print(f"  ✓ {binary_file.name} validated")
                    
            except Exception as e:
                self.log_error("BINARY", f"{binary_file.name}: {e}")
                valid = False
        
        return valid
    
    def run_all_validations(self, quick: bool = False) -> bool:
        """
        Run all validations
        
        Args:
            quick: Skip slow validations
            
        Returns:
            True if all validations pass
        """
        print("=" * 70)
        print("Dragon Warrior Data Validation Suite")
        print("=" * 70)
        
        all_valid = True
        
        # Core data validation
        if not self.validate_monsters():
            all_valid = False
        
        if not self.validate_spells():
            all_valid = False
        
        if not self.validate_items():
            all_valid = False
        
        if not self.validate_cross_references():
            all_valid = False
        
        # Optional validations
        if not quick:
            if not self.validate_graphics():
                all_valid = False
            
            if not self.validate_binary_integrity():
                all_valid = False
        
        # Summary
        print("\n" + "=" * 70)
        print("Validation Summary")
        print("=" * 70)
        
        print(f"\nErrors: {len(self.errors)}")
        if self.errors:
            for error in self.errors:
                print(f"  {error}")
        
        print(f"\nWarnings: {len(self.warnings)}")
        if self.warnings:
            for warning in self.warnings[:10]:  # Show first 10
                print(f"  {warning}")
            
            if len(self.warnings) > 10:
                print(f"  ... and {len(self.warnings) - 10} more warnings")
        
        if all_valid and not self.errors:
            print("\n✅ All validations passed!")
        else:
            print(f"\n❌ Validation failed with {len(self.errors)} errors")
        
        print("=" * 70)
        
        return all_valid


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Validate all Dragon Warrior extracted data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full validation
  python tools/validate_all.py
  
  # Quick validation (skip slow checks)
  python tools/validate_all.py --quick
  
  # Verbose output
  python tools/validate_all.py --verbose
        """
    )
    
    parser.add_argument(
        '--assets',
        default=DEFAULT_ASSETS,
        help=f'Assets directory (default: {DEFAULT_ASSETS})'
    )
    
    parser.add_argument(
        '--quick',
        action='store_true',
        help='Skip slow validations'
    )
    
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Verbose output'
    )
    
    args = parser.parse_args()
    
    # Initialize validator
    validator = DataValidator(args.assets)
    
    # Run validations
    success = validator.run_all_validations(quick=args.quick)
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
