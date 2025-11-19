#!/usr/bin/env python3
"""
Dragon Warrior Asset Validation Framework
Comprehensive validation tools for extracted assets and data integrity
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional, Set
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import track
from rich import print as rprint

console = Console()

class AssetValidator:
	"""Comprehensive asset validation and integrity checking"""
	
	def __init__(self, assets_dir: str):
		self.assets_dir = Path(assets_dir)
		self.json_dir = self.assets_dir / "json"
		self.graphics_dir = self.assets_dir / "graphics"
		self.validation_errors = []
		self.validation_warnings = []
		
	def validate_all_assets(self) -> Dict[str, Any]:
		"""Run complete asset validation suite"""
		console.print("[bold blue]🔍 Dragon Warrior Asset Validation[/bold blue]\n")
		
		results = {
			"directory_structure": self._validate_directory_structure(),
			"json_files": self._validate_json_files(),
			"cross_references": self._validate_cross_references(),
			"data_integrity": self._validate_data_integrity(),
			"graphics_assets": self._validate_graphics_assets()
		}
		
		# Generate summary report
		self._generate_validation_report(results)
		return results
	
	def _validate_directory_structure(self) -> Dict[str, Any]:
		"""Validate expected directory structure exists"""
		console.print("[cyan]📁 Validating directory structure...[/cyan]")
		
		expected_dirs = [
			self.json_dir,
			self.graphics_dir,
			self.assets_dir / "palettes",
			self.assets_dir / "maps"
		]
		
		missing_dirs = []
		existing_dirs = []
		
		for expected_dir in expected_dirs:
			if expected_dir.exists() and expected_dir.is_dir():
				existing_dirs.append(expected_dir.name)
			else:
				missing_dirs.append(expected_dir.name)
		
		return {
			"existing_directories": existing_dirs,
			"missing_directories": missing_dirs,
			"valid": len(missing_dirs) == 0
		}
	
	def _validate_json_files(self) -> Dict[str, Any]:
		"""Validate JSON file structure and content"""
		console.print("[cyan]📄 Validating JSON files...[/cyan]")
		
		expected_files = [
			"monsters.json",
			"items.json", 
			"spells.json",
			"shops.json",
			"complete_game_data.json"
		]
		
		validation_results = {}
		
		for filename in track(expected_files, description="Checking JSON files..."):
			file_path = self.json_dir / filename
			result = self._validate_json_file(file_path)
			validation_results[filename] = result
		
		return validation_results
	
	def _validate_json_file(self, file_path: Path) -> Dict[str, Any]:
		"""Validate individual JSON file"""
		if not file_path.exists():
			return {"exists": False, "valid_json": False, "error": "File not found"}
		
		try:
			with open(file_path, 'r', encoding='utf-8') as f:
				data = json.load(f)
			
			# Basic structure validation
			if not isinstance(data, dict):
				return {
					"exists": True,
					"valid_json": True,
					"valid_structure": False,
					"error": "Root element must be a dictionary"
				}
			
			# File-specific validation
			if file_path.name == "monsters.json":
				validation = self._validate_monster_data(data)
			elif file_path.name == "items.json":
				validation = self._validate_item_data(data)
			elif file_path.name == "spells.json":
				validation = self._validate_spell_data(data)
			elif file_path.name == "shops.json":
				validation = self._validate_shop_data(data)
			else:
				validation = {"valid_structure": True, "record_count": len(data)}
			
			return {
				"exists": True,
				"valid_json": True,
				"file_size": file_path.stat().st_size,
				**validation
			}
			
		except json.JSONDecodeError as e:
			return {
				"exists": True,
				"valid_json": False,
				"error": f"JSON decode error: {e}"
			}
		except Exception as e:
			return {
				"exists": True,
				"valid_json": False,
				"error": f"Unexpected error: {e}"
			}
	
	def _validate_monster_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate monster data structure and values"""
		required_fields = ["hp", "strength", "agility", "max_damage"]
		errors = []
		warnings = []
		
		for monster_id, monster in data.items():
			if not isinstance(monster, dict):
				errors.append(f"Monster {monster_id}: Must be a dictionary")
				continue
			
			# Check required fields
			missing_fields = [field for field in required_fields if field not in monster]
			if missing_fields:
				errors.append(f"Monster {monster_id}: Missing fields {missing_fields}")
			
			# Validate HP range (Dragon Warrior monsters: 3-165 HP)
			if "hp" in monster:
				hp = monster["hp"]
				if not isinstance(hp, int) or hp < 1 or hp > 200:
					warnings.append(f"Monster {monster_id}: Unusual HP value {hp}")
		
		return {
			"valid_structure": len(errors) == 0,
			"record_count": len(data),
			"validation_errors": errors,
			"validation_warnings": warnings
		}
	
	def _validate_item_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate item data structure and values"""
		errors = []
		warnings = []
		
		for item_id, item in data.items():
			if not isinstance(item, dict):
				errors.append(f"Item {item_id}: Must be a dictionary")
				continue
			
			# Check price ranges (Dragon Warrior items: 6-9800 gold)
			if "buy_price" in item:
				price = item["buy_price"]
				if isinstance(price, int) and (price < 0 or price > 15000):
					warnings.append(f"Item {item_id}: Unusual buy price {price}")
		
		return {
			"valid_structure": len(errors) == 0,
			"record_count": len(data),
			"validation_errors": errors,
			"validation_warnings": warnings
		}
	
	def _validate_spell_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate spell data structure and values"""
		errors = []
		warnings = []
		
		for spell_id, spell in data.items():
			if not isinstance(spell, dict):
				errors.append(f"Spell {spell_id}: Must be a dictionary")
				continue
			
			# Check MP cost range (Dragon Warrior spells: 2-15 MP)
			if "mp_cost" in spell:
				mp = spell["mp_cost"]
				if isinstance(mp, int) and (mp < 1 or mp > 20):
					warnings.append(f"Spell {spell_id}: Unusual MP cost {mp}")
		
		return {
			"valid_structure": len(errors) == 0,
			"record_count": len(data),
			"validation_errors": errors,
			"validation_warnings": warnings
		}
	
	def _validate_shop_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
		"""Validate shop data structure and references"""
		errors = []
		warnings = []
		
		for shop_id, shop in data.items():
			if not isinstance(shop, dict):
				errors.append(f"Shop {shop_id}: Must be a dictionary")
				continue
			
			# Validate item list structure
			if "items" in shop:
				items = shop["items"]
				if not isinstance(items, list):
					errors.append(f"Shop {shop_id}: items must be a list")
				elif len(items) == 0:
					warnings.append(f"Shop {shop_id}: No items in inventory")
		
		return {
			"valid_structure": len(errors) == 0,
			"record_count": len(data),
			"validation_errors": errors,
			"validation_warnings": warnings
		}
	
	def _validate_cross_references(self) -> Dict[str, Any]:
		"""Validate cross-references between data files"""
		console.print("[cyan]🔗 Validating cross-references...[/cyan]")
		
		# Load all data files
		try:
			items_file = self.json_dir / "items.json"
			shops_file = self.json_dir / "shops.json"
			
			if not items_file.exists() or not shops_file.exists():
				return {"valid": False, "error": "Required files missing for cross-reference validation"}
			
			with open(items_file, 'r') as f:
				items_data = json.load(f)
			with open(shops_file, 'r') as f:
				shops_data = json.load(f)
			
			# Check shop inventory references
			errors = []
			warnings = []
			
			item_ids = set(items_data.keys())
			
			for shop_id, shop in shops_data.items():
				if "items" in shop and isinstance(shop["items"], list):
					for item_id in shop["items"]:
						if str(item_id) not in item_ids:
							errors.append(f"Shop {shop_id} references unknown item {item_id}")
			
			return {
				"valid": len(errors) == 0,
				"cross_reference_errors": errors,
				"cross_reference_warnings": warnings,
				"items_checked": len(item_ids),
				"shops_checked": len(shops_data)
			}
			
		except Exception as e:
			return {"valid": False, "error": f"Error during cross-reference validation: {e}"}
	
	def _validate_data_integrity(self) -> Dict[str, Any]:
		"""Validate data integrity and Dragon Warrior-specific rules"""
		console.print("[cyan]🎮 Validating game data integrity...[/cyan]")
		
		try:
			# Load complete game data
			complete_file = self.json_dir / "complete_game_data.json"
			if not complete_file.exists():
				return {"valid": False, "error": "Complete game data file not found"}
			
			with open(complete_file, 'r') as f:
				game_data = json.load(f)
			
			integrity_errors = []
			integrity_warnings = []
			
			# Validate game balance (example checks)
			if "monsters" in game_data:
				monsters = game_data["monsters"]
				
				# Check for monsters with 0 HP or negative stats
				for monster_id, monster in monsters.items():
					if isinstance(monster, dict):
						if monster.get("hp", 0) <= 0:
							integrity_errors.append(f"Monster {monster_id} has invalid HP")
						
						if monster.get("experience", 0) < 0:
							integrity_errors.append(f"Monster {monster_id} has negative experience")
			
			return {
				"valid": len(integrity_errors) == 0,
				"integrity_errors": integrity_errors,
				"integrity_warnings": integrity_warnings,
				"sections_validated": len(game_data)
			}
			
		except Exception as e:
			return {"valid": False, "error": f"Error during integrity validation: {e}"}
	
	def _validate_graphics_assets(self) -> Dict[str, Any]:
		"""Validate graphics assets and file integrity"""
		console.print("[cyan]🎨 Validating graphics assets...[/cyan]")
		
		if not self.graphics_dir.exists():
			return {"valid": False, "error": "Graphics directory not found"}
		
		png_files = list(self.graphics_dir.glob("*.png"))
		
		valid_files = 0
		invalid_files = []
		
		try:
			from PIL import Image
			
			for png_file in track(png_files, description="Checking PNG files..."):
				try:
					with Image.open(png_file) as img:
						# Basic validation - can load and has reasonable size
						width, height = img.size
						if width > 0 and height > 0 and width <= 2048 and height <= 2048:
							valid_files += 1
						else:
							invalid_files.append(f"{png_file.name}: Invalid dimensions {width}x{height}")
				except Exception as e:
					invalid_files.append(f"{png_file.name}: Cannot load - {e}")
			
			return {
				"valid": len(invalid_files) == 0,
				"total_files": len(png_files),
				"valid_files": valid_files,
				"invalid_files": invalid_files
			}
			
		except ImportError:
			return {"valid": None, "error": "PIL not available for graphics validation"}
		except Exception as e:
			return {"valid": False, "error": f"Error during graphics validation: {e}"}
	
	def _generate_validation_report(self, results: Dict[str, Any]):
		"""Generate comprehensive validation report"""
		console.print("\n")
		console.print(Panel.fit("🔍 Asset Validation Report", border_style="blue"))
		
		# Summary table
		table = Table(title="Validation Results Summary")
		table.add_column("Component", style="cyan")
		table.add_column("Status", style="bold")
		table.add_column("Details", style="dim")
		
		# Directory structure
		dir_result = results["directory_structure"]
		status = "✅ PASS" if dir_result["valid"] else "❌ FAIL"
		details = f"{len(dir_result['existing_directories'])} dirs found"
		if dir_result["missing_directories"]:
			details += f", {len(dir_result['missing_directories'])} missing"
		table.add_row("Directory Structure", status, details)
		
		# JSON files
		json_results = results["json_files"]
		valid_json_files = sum(1 for r in json_results.values() if r.get("valid_json", False))
		total_json_files = len(json_results)
		status = "✅ PASS" if valid_json_files == total_json_files else "❌ FAIL"
		table.add_row("JSON Files", status, f"{valid_json_files}/{total_json_files} valid")
		
		# Cross-references
		cross_result = results["cross_references"]
		if cross_result.get("valid") is not None:
			status = "✅ PASS" if cross_result["valid"] else "❌ FAIL"
			details = f"{cross_result.get('items_checked', 0)} items, {cross_result.get('shops_checked', 0)} shops"
		else:
			status = "⚠️ SKIP"
			details = "Validation skipped"
		table.add_row("Cross-References", status, details)
		
		# Data integrity
		integrity_result = results["data_integrity"]
		if integrity_result.get("valid") is not None:
			status = "✅ PASS" if integrity_result["valid"] else "❌ FAIL"
			details = f"{integrity_result.get('sections_validated', 0)} sections checked"
		else:
			status = "⚠️ SKIP"
			details = "Validation skipped"
		table.add_row("Data Integrity", status, details)
		
		# Graphics assets
		graphics_result = results["graphics_assets"]
		if graphics_result.get("valid") is not None:
			status = "✅ PASS" if graphics_result["valid"] else "❌ FAIL"
			details = f"{graphics_result.get('valid_files', 0)}/{graphics_result.get('total_files', 0)} PNG files"
		else:
			status = "⚠️ SKIP"
			details = "Validation skipped"
		table.add_row("Graphics Assets", status, details)
		
		console.print(table)
		
		# Detailed error reporting
		self._report_detailed_errors(results)
	
	def _report_detailed_errors(self, results: Dict[str, Any]):
		"""Report detailed validation errors and warnings"""
		all_errors = []
		all_warnings = []
		
		# Collect errors from all validation components
		for component, result in results.items():
			if isinstance(result, dict):
				if "error" in result:
					all_errors.append(f"{component}: {result['error']}")
				
				# Collect validation errors from JSON file checks
				if component == "json_files":
					for filename, file_result in result.items():
						if "validation_errors" in file_result:
							for error in file_result["validation_errors"]:
								all_errors.append(f"{filename}: {error}")
						if "validation_warnings" in file_result:
							for warning in file_result["validation_warnings"]:
								all_warnings.append(f"{filename}: {warning}")
		
		# Display errors
		if all_errors:
			console.print("\n[bold red]❌ Validation Errors:[/bold red]")
			for error in all_errors:
				console.print(f"  • {error}")
		
		# Display warnings  
		if all_warnings:
			console.print("\n[bold yellow]⚠️ Validation Warnings:[/bold yellow]")
			for warning in all_warnings:
				console.print(f"  • {warning}")
		
		if not all_errors and not all_warnings:
			console.print("\n[bold green]🎉 All validations passed with no issues![/bold green]")

@click.command()
@click.argument('assets_dir', type=click.Path(exists=True))
@click.option('--json-only', is_flag=True, help='Validate only JSON files')
@click.option('--cross-refs', is_flag=True, help='Validate only cross-references')
def validate_assets(assets_dir: str, json_only: bool, cross_refs: bool):
	"""Validate Dragon Warrior extracted assets"""
	try:
		validator = AssetValidator(assets_dir)
		
		if json_only:
			console.print("[cyan]📄 JSON-only validation mode[/cyan]")
			results = {"json_files": validator._validate_json_files()}
		elif cross_refs:
			console.print("[cyan]🔗 Cross-reference validation mode[/cyan]")
			results = {"cross_references": validator._validate_cross_references()}
		else:
			results = validator.validate_all_assets()
		
		# Exit with error code if validation failed
		has_errors = any(
			result.get("valid") is False 
			for result in results.values() 
			if isinstance(result, dict)
		)
		
		if has_errors:
			console.print("\n[red]❌ Validation failed[/red]")
			sys.exit(1)
		else:
			console.print("\n[green]✅ Validation passed[/green]")
			
	except Exception as e:
		console.print(f"[red]❌ Validation error: {e}[/red]")
		sys.exit(1)

if __name__ == "__main__":
	validate_assets()