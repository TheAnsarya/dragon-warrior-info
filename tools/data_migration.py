#!/usr/bin/env python3
"""
Data Migration Tool for Dragon Warrior

Migrate data between different ROM versions and formats.

Features:
- ROM version detection
- Data format conversion
- Backward compatibility
- Migration validation
- Rollback support

Usage:
	python tools/data_migration.py --from v1.0 --to v2.0
	python tools/data_migration.py --check-version
	python tools/data_migration.py --rollback

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
import shutil
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional

# Default paths
DEFAULT_ASSETS = "extracted_assets"
DEFAULT_BACKUP = "backups"


class DataMigration:
	"""Handle data migration between versions"""

	# Version configurations
	VERSIONS = {
		"1.0": {
			"description": "Initial release",
			"date": "2024-11",
			"changes": []
		},
		"1.1": {
			"description": "Added spell resistance fields",
			"date": "2024-11",
			"changes": [
				"Added resist_sleep to monsters",
				"Added resist_stopspell to monsters",
				"Added resist_hurt to monsters",
				"Added resist_dodge to monsters"
			]
		},
		"1.2": {
			"description": "Added sprite family tracking",
			"date": "2024-11",
			"changes": [
				"Added sprite_family to monsters",
				"Added palette_index to monsters"
			]
		},
		"2.0": {
			"description": "Binary intermediate format",
			"date": "2024-11",
			"changes": [
				"Introduced .dwdata binary format",
				"Added CRC32 validation",
				"Added metadata tracking"
			]
		}
	}

	def __init__(self, assets_dir: str, backup_dir: str):
		"""
		Initialize migration tool

		Args:
			assets_dir: Assets directory
			backup_dir: Backup directory
		"""
		self.assets_dir = Path(assets_dir)
		self.backup_dir = Path(backup_dir)
		self.json_dir = self.assets_dir / "json"

	def detect_version(self) -> Optional[str]:
		"""
		Detect current data version

		Returns:
			Version string or None
		"""
		version_file = self.assets_dir / "version.json"

		if version_file.exists():
			with open(version_file, 'r') as f:
				version_data = json.load(f)
				return version_data.get('version')

		# Try to detect from data structure
		monsters_file = self.json_dir / "monsters.json"
		if not monsters_file.exists():
			return None

		with open(monsters_file, 'r') as f:
			monsters = json.load(f)

		if not monsters:
			return None

		sample = monsters[0]

		# Check for v2.0 features
		if 'sprite_family' in sample and 'resist_sleep' in sample:
			return "2.0"

		# Check for v1.2 features
		if 'sprite_family' in sample:
			return "1.2"

		# Check for v1.1 features
		if 'resist_sleep' in sample:
			return "1.1"

		# Default to v1.0
		return "1.0"

	def save_version(self, version: str):
		"""
		Save version information

		Args:
			version: Version string
		"""
		version_file = self.assets_dir / "version.json"

		version_data = {
			'version': version,
			'description': self.VERSIONS[version]['description'],
			'migration_date': datetime.now().isoformat(),
			'previous_version': self.detect_version()
		}

		with open(version_file, 'w') as f:
			json.dump(version_data, f, indent=2)

		print(f"✓ Saved version: {version}")

	def create_backup(self) -> str:
		"""
		Create backup of current data

		Returns:
			Backup directory name
		"""
		timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
		current_version = self.detect_version() or "unknown"
		backup_name = f"backup_{current_version}_{timestamp}"

		backup_path = self.backup_dir / backup_name
		backup_path.mkdir(parents=True, exist_ok=True)

		# Copy all JSON files
		for json_file in self.json_dir.glob("*.json"):
			shutil.copy2(json_file, backup_path / json_file.name)

		# Copy version file if exists
		version_file = self.assets_dir / "version.json"
		if version_file.exists():
			shutil.copy2(version_file, backup_path / "version.json")

		print(f"✓ Created backup: {backup_path}")
		return backup_name

	def migrate_1_0_to_1_1(self) -> bool:
		"""
		Migrate from v1.0 to v1.1

		Adds resistance fields to monsters

		Returns:
			True if successful
		"""
		print("\n--- Migrating v1.0 → v1.1 ---")

		monsters_file = self.json_dir / "monsters.json"

		with open(monsters_file, 'r') as f:
			monsters = json.load(f)

		# Add default resistance values
		for monster in monsters:
			if 'resist_sleep' not in monster:
				monster['resist_sleep'] = 0
			if 'resist_stopspell' not in monster:
				monster['resist_stopspell'] = 0
			if 'resist_hurt' not in monster:
				monster['resist_hurt'] = 0
			if 'resist_dodge' not in monster:
				monster['resist_dodge'] = 0

		# Save updated data
		with open(monsters_file, 'w') as f:
			json.dump(monsters, f, indent=2)

		print(f"✓ Added resistance fields to {len(monsters)} monsters")
		return True

	def migrate_1_1_to_1_2(self) -> bool:
		"""
		Migrate from v1.1 to v1.2

		Adds sprite family tracking

		Returns:
			True if successful
		"""
		print("\n--- Migrating v1.1 → v1.2 ---")

		# Sprite family mapping (from analyze_monster_sprites.py)
		SPRITE_FAMILIES = {
			"Slime": "SlimeSprts",
			"Red Slime": "SlimeSprts",
			"Metal Slime": "SlimeSprts",
			"Drakee": "DrakeeSprts",
			"Magician": "DrakeeSprts",
			"Magiwyvern": "DrakeeSprts",
			"Ghost": "GhostSprts",
			"Specter": "GhostSprts",
			"Poltergeist": "GhostSprts",
			"Scorpion": "ScorpSprts",
			"Wolflord": "ScorpSprts",
			"Druin": "ScorpSprts",
			"Golem": "GolemSprts",
			"Goldman": "GolemSprts",
			"Knight": "GolemSprts",
			"Magidrakee": "MgDrkSprts",
			"Wyvern": "MgDrkSprts",
			"Dragon": "DragonSprts",
			"Red Dragon": "DragonSprts",
			"Starwyvern": "DragonSprts",
			"Drakeema": "DrakemaSprts",
			"Skeleton": "SkeletonSprts",
			"Warlock": "WarlockSprts",
			"Metal Scorpion": "MScorpSprts",
			"Dragonlord (1st form)": "DL1Sprts",
			"Dragonlord (2nd form)": "DL2Sprts",
			# Add more mappings...
		}

		monsters_file = self.json_dir / "monsters.json"

		with open(monsters_file, 'r') as f:
			monsters = json.load(f)

		# Add sprite family
		for monster in monsters:
			name = monster.get('name', '')
			if 'sprite_family' not in monster:
				monster['sprite_family'] = SPRITE_FAMILIES.get(name, 'Unknown')
			if 'palette_index' not in monster:
				monster['palette_index'] = 0  # Default palette

		# Save updated data
		with open(monsters_file, 'w') as f:
			json.dump(monsters, f, indent=2)

		print(f"✓ Added sprite family to {len(monsters)} monsters")
		return True

	def migrate_1_2_to_2_0(self) -> bool:
		"""
		Migrate from v1.2 to v2.0

		Converts to binary intermediate format

		Returns:
			True if successful
		"""
		print("\n--- Migrating v1.2 → v2.0 ---")

		try:
			# Import binary tools
			sys.path.insert(0, str(Path(__file__).parent))
			from assets_to_binary import BinaryPackager

			packager = BinaryPackager(str(self.assets_dir))

			# Package monsters
			if packager.package_monsters():
				print("✓ Converted monsters to binary format")

			# Package spells
			if packager.package_spells():
				print("✓ Converted spells to binary format")

			# Package items
			if packager.package_items():
				print("✓ Converted items to binary format")

			return True
		except Exception as e:
			print(f"❌ Migration failed: {e}")
			return False

	def migrate(self, from_version: str, to_version: str) -> bool:
		"""
		Perform migration between versions

		Args:
			from_version: Source version
			to_version: Target version

		Returns:
			True if successful
		"""
		if from_version not in self.VERSIONS:
			print(f"❌ Unknown source version: {from_version}")
			return False

		if to_version not in self.VERSIONS:
			print(f"❌ Unknown target version: {to_version}")
			return False

		if from_version == to_version:
			print(f"ℹ Already at version {to_version}")
			return True

		print("=" * 70)
		print(f"Data Migration: v{from_version} → v{to_version}")
		print("=" * 70)

		# Create backup
		backup = self.create_backup()

		# Determine migration path
		version_order = ["1.0", "1.1", "1.2", "2.0"]

		try:
			start_idx = version_order.index(from_version)
			end_idx = version_order.index(to_version)
		except ValueError:
			print("❌ Cannot determine migration path")
			return False

		if start_idx > end_idx:
			print("❌ Downgrade not supported (use --rollback)")
			return False

		# Perform sequential migrations
		current_version = from_version

		for i in range(start_idx, end_idx):
			next_version = version_order[i + 1]

			print(f"\nMigrating {current_version} → {next_version}...")

			# Call appropriate migration function
			if current_version == "1.0" and next_version == "1.1":
				if not self.migrate_1_0_to_1_1():
					raise Exception("Migration failed")
			elif current_version == "1.1" and next_version == "1.2":
				if not self.migrate_1_1_to_1_2():
					raise Exception("Migration failed")
			elif current_version == "1.2" and next_version == "2.0":
				if not self.migrate_1_2_to_2_0():
					raise Exception("Migration failed")

			current_version = next_version

		# Save new version
		self.save_version(to_version)

		print("\n" + "=" * 70)
		print(f"✓ Migration complete: v{from_version} → v{to_version}")
		print(f"  Backup saved: {backup}")
		print("=" * 70)

		return True

	def rollback(self, backup_name: Optional[str] = None) -> bool:
		"""
		Rollback to previous backup

		Args:
			backup_name: Specific backup to restore (or latest)

		Returns:
			True if successful
		"""
		if backup_name:
			backup_path = self.backup_dir / backup_name
		else:
			# Find latest backup
			backups = sorted(self.backup_dir.glob("backup_*"))
			if not backups:
				print("❌ No backups found")
				return False
			backup_path = backups[-1]

		if not backup_path.exists():
			print(f"❌ Backup not found: {backup_path}")
			return False

		print(f"Rolling back to: {backup_path.name}")

		# Restore JSON files
		for json_file in backup_path.glob("*.json"):
			dest = self.json_dir / json_file.name
			shutil.copy2(json_file, dest)
			print(f"  Restored: {json_file.name}")

		# Restore version file
		version_file = backup_path / "version.json"
		if version_file.exists():
			shutil.copy2(version_file, self.assets_dir / "version.json")

		print("✓ Rollback complete")
		return True

	def list_versions(self):
		"""List all available versions"""
		print("=" * 70)
		print("Available Versions")
		print("=" * 70)

		for version, info in self.VERSIONS.items():
			print(f"\nv{version} - {info['description']} ({info['date']})")
			if info['changes']:
				for change in info['changes']:
					print(f"  • {change}")

	def check_version(self):
		"""Check current version"""
		current = self.detect_version()

		print("=" * 70)
		print("Version Information")
		print("=" * 70)

		if current:
			info = self.VERSIONS.get(current, {})
			print(f"\nCurrent Version: v{current}")
			print(f"Description: {info.get('description', 'Unknown')}")
			print(f"Release Date: {info.get('date', 'Unknown')}")
		else:
			print("\n⚠ Cannot detect version")

		version_file = self.assets_dir / "version.json"
		if version_file.exists():
			with open(version_file, 'r') as f:
				data = json.load(f)
			print(f"\nVersion File:")
			print(f"  Version: {data.get('version')}")
			print(f"  Migration Date: {data.get('migration_date')}")
			print(f"  Previous: {data.get('previous_version')}")


def main():
	"""Main entry point"""
	parser = argparse.ArgumentParser(
		description='Migrate Dragon Warrior data between versions',
		formatter_class=argparse.RawDescriptionHelpFormatter,
		epilog="""
Examples:
  # Check current version
  python tools/data_migration.py --check-version

  # Migrate to latest
  python tools/data_migration.py --from 1.0 --to 2.0

  # Rollback to latest backup
  python tools/data_migration.py --rollback

  # List all versions
  python tools/data_migration.py --list-versions
		"""
	)

	parser.add_argument(
		'--assets',
		default=DEFAULT_ASSETS,
		help=f'Assets directory (default: {DEFAULT_ASSETS})'
	)

	parser.add_argument(
		'--backup',
		default=DEFAULT_BACKUP,
		help=f'Backup directory (default: {DEFAULT_BACKUP})'
	)

	parser.add_argument(
		'--from',
		dest='from_version',
		help='Source version'
	)

	parser.add_argument(
		'--to',
		dest='to_version',
		help='Target version'
	)

	parser.add_argument(
		'--check-version',
		action='store_true',
		help='Check current version'
	)

	parser.add_argument(
		'--list-versions',
		action='store_true',
		help='List all available versions'
	)

	parser.add_argument(
		'--rollback',
		nargs='?',
		const=True,
		help='Rollback to backup (optionally specify backup name)'
	)

	args = parser.parse_args()

	# Initialize migration tool
	migration = DataMigration(args.assets, args.backup)

	# Handle commands
	if args.check_version:
		migration.check_version()
		return 0

	if args.list_versions:
		migration.list_versions()
		return 0

	if args.rollback:
		backup_name = None if args.rollback is True else args.rollback
		success = migration.rollback(backup_name)
		return 0 if success else 1

	if args.from_version and args.to_version:
		success = migration.migrate(args.from_version, args.to_version)
		return 0 if success else 1

	# Default: show version
	migration.check_version()
	return 0


if __name__ == '__main__':
	sys.exit(main())
