#!/usr/bin/env python3
"""
Asset Manager - Unified Asset Loading/Saving System
Provides centralized management of all Dragon Warrior game assets (items, monsters, spells, etc.)
"""
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
import shutil
from datetime import datetime


@dataclass
class AssetMetadata:
    """Metadata about an asset file"""
    asset_type: str  # 'items', 'monsters', 'spells', etc.
    file_path: Path
    last_modified: str
    version: str
    record_count: int
    checksum: Optional[str] = None


class AssetValidationError(Exception):
    """Raised when asset data fails validation"""
    pass


class AssetManager:
    """
    Centralized manager for all Dragon Warrior ROM assets
    
    Supports:
    - Loading assets from JSON files
    - Saving assets to JSON files with backup
    - Asset validation before save
    - Change tracking
    - Automatic backup creation
    - Asset metadata management
    """
    
    ASSET_TYPES = [
        'items', 'monsters', 'spells', 'shops', 'dialogue',
        'npcs', 'maps', 'zones', 'graphics', 'music'
    ]
    
    def __init__(self, assets_dir: str = "assets"):
        """
        Initialize Asset Manager
        
        Args:
            assets_dir: Root directory for all assets (default: "assets")
        """
        self.assets_dir = Path(assets_dir)
        self.json_dir = self.assets_dir / "json"
        self.backup_dir = self.assets_dir / "backups"
        
        # Ensure directories exist
        self.json_dir.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # Cache for loaded assets
        self._cache: Dict[str, Any] = {}
        
        # Change tracking
        self._dirty_assets: set = set()
        
        # Metadata storage
        self._metadata: Dict[str, AssetMetadata] = {}
    
    def load_asset(self, asset_type: str, use_cache: bool = True) -> Dict[int, Any]:
        """
        Load an asset file from JSON
        
        Args:
            asset_type: Type of asset ('items', 'monsters', etc.)
            use_cache: Whether to use cached version if available
        
        Returns:
            Dictionary mapping IDs to asset objects
        
        Raises:
            FileNotFoundError: If asset file doesn't exist
            json.JSONDecodeError: If JSON is invalid
        """
        if asset_type not in self.ASSET_TYPES:
            raise ValueError(f"Unknown asset type: {asset_type}. Must be one of {self.ASSET_TYPES}")
        
        # Check cache first
        if use_cache and asset_type in self._cache:
            return self._cache[asset_type]
        
        # Determine file path
        file_path = self.json_dir / f"{asset_type}.json"
        
        # Try verified version first
        verified_path = self.json_dir / f"{asset_type}_verified.json"
        if verified_path.exists():
            file_path = verified_path
        
        # Try corrected version
        corrected_path = self.json_dir / f"{asset_type}_corrected.json"
        if corrected_path.exists():
            file_path = corrected_path
        
        if not file_path.exists():
            raise FileNotFoundError(f"Asset file not found: {file_path}")
        
        # Load JSON
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert string keys to integers (JSON keys are always strings)
        assets = {int(k): v for k, v in data.items()}
        
        # Cache the data
        self._cache[asset_type] = assets
        
        # Update metadata
        self._metadata[asset_type] = AssetMetadata(
            asset_type=asset_type,
            file_path=file_path,
            last_modified=datetime.fromtimestamp(file_path.stat().st_mtime).isoformat(),
            version="1.0",
            record_count=len(assets)
        )
        
        return assets
    
    def save_asset(self, asset_type: str, assets: Dict[int, Any],
                   create_backup: bool = True, validate: bool = True) -> Path:
        """
        Save assets to JSON file with optional backup and validation
        
        Args:
            asset_type: Type of asset being saved
            assets: Dictionary mapping IDs to asset data
            create_backup: Whether to create backup before saving
            validate: Whether to validate data before saving
        
        Returns:
            Path to saved file
        
        Raises:
            AssetValidationError: If validation fails
        """
        if asset_type not in self.ASSET_TYPES:
            raise ValueError(f"Unknown asset type: {asset_type}")
        
        # Validate if requested
        if validate:
            self.validate_assets(asset_type, assets)
        
        # Determine output path
        output_path = self.json_dir / f"{asset_type}.json"
        
        # Create backup if requested and file exists
        if create_backup and output_path.exists():
            self._create_backup(asset_type, output_path)
        
        # Convert data to JSON-serializable format
        # Handle both dict and object formats
        json_data = {}
        for asset_id, asset_value in assets.items():
            if hasattr(asset_value, '__dict__'):
                # It's an object with attributes
                json_data[str(asset_id)] = asdict(asset_value) if hasattr(asset_value, '__dataclass_fields__') else asset_value.__dict__
            elif isinstance(asset_value, dict):
                # It's already a dictionary
                json_data[str(asset_id)] = asset_value
            else:
                # Try to convert to dict
                json_data[str(asset_id)] = dict(asset_value)
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, indent=2)
        
        # Update cache
        self._cache[asset_type] = assets
        
        # Mark as clean (just saved)
        self._dirty_assets.discard(asset_type)
        
        # Update metadata
        self._metadata[asset_type] = AssetMetadata(
            asset_type=asset_type,
            file_path=output_path,
            last_modified=datetime.now().isoformat(),
            version="1.0",
            record_count=len(assets)
        )
        
        return output_path
    
    def _create_backup(self, asset_type: str, source_path: Path) -> Path:
        """
        Create a timestamped backup of an asset file
        
        Args:
            asset_type: Type of asset
            source_path: Path to file being backed up
        
        Returns:
            Path to backup file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{asset_type}_backup_{timestamp}.json"
        backup_path = self.backup_dir / backup_filename
        
        shutil.copy2(source_path, backup_path)
        
        return backup_path
    
    def validate_assets(self, asset_type: str, assets: Dict[int, Any]):
        """
        Validate asset data before saving
        
        Args:
            asset_type: Type of asset
            assets: Asset data to validate
        
        Raises:
            AssetValidationError: If validation fails
        """
        if not assets:
            raise AssetValidationError(f"No {asset_type} data to save")
        
        # Type-specific validation
        if asset_type == 'items':
            self._validate_items(assets)
        elif asset_type == 'monsters':
            self._validate_monsters(assets)
        elif asset_type == 'spells':
            self._validate_spells(assets)
        # Add more validators as needed
    
    def _validate_items(self, items: Dict[int, Any]):
        """Validate item data"""
        required_fields = ['id', 'name', 'attack_power', 'defense_power', 'buy_price', 'sell_price']
        
        for item_id, item in items.items():
            # Get item as dict if it's an object
            item_dict = item if isinstance(item, dict) else (item.__dict__ if hasattr(item, '__dict__') else {})
            
            # Check required fields
            for field in required_fields:
                if field not in item_dict:
                    raise AssetValidationError(f"Item {item_id} missing required field: {field}")
            
            # Validate ranges
            if not (0 <= item_dict.get('attack_power', 0) <= 127):
                raise AssetValidationError(f"Item {item_id} has invalid attack_power: {item_dict.get('attack_power')}")
            
            if not (0 <= item_dict.get('defense_power', 0) <= 127):
                raise AssetValidationError(f"Item {item_id} has invalid defense_power: {item_dict.get('defense_power')}")
            
            if not (0 <= item_dict.get('buy_price', 0) <= 65535):
                raise AssetValidationError(f"Item {item_id} has invalid buy_price: {item_dict.get('buy_price')}")
    
    def _validate_monsters(self, monsters: Dict[int, Any]):
        """Validate monster data"""
        required_fields = ['id', 'name', 'hp', 'strength', 'agility', 'experience', 'gold']
        
        for monster_id, monster in monsters.items():
            monster_dict = monster if isinstance(monster, dict) else (monster.__dict__ if hasattr(monster, '__dict__') else {})
            
            # Check required fields
            for field in required_fields:
                if field not in monster_dict:
                    raise AssetValidationError(f"Monster {monster_id} missing required field: {field}")
            
            # Validate ranges
            if not (1 <= monster_dict.get('hp', 0) <= 255):
                raise AssetValidationError(f"Monster {monster_id} has invalid HP: {monster_dict.get('hp')}")
            
            if not (0 <= monster_dict.get('strength', 0) <= 255):
                raise AssetValidationError(f"Monster {monster_id} has invalid strength: {monster_dict.get('strength')}")
    
    def _validate_spells(self, spells: Dict[int, Any]):
        """Validate spell data"""
        required_fields = ['id', 'name', 'mp_cost']
        
        for spell_id, spell in spells.items():
            spell_dict = spell if isinstance(spell, dict) else (spell.__dict__ if hasattr(spell, '__dict__') else {})
            
            for field in required_fields:
                if field not in spell_dict:
                    raise AssetValidationError(f"Spell {spell_id} missing required field: {field}")
            
            if not (0 <= spell_dict.get('mp_cost', 0) <= 255):
                raise AssetValidationError(f"Spell {spell_id} has invalid MP cost: {spell_dict.get('mp_cost')}")
    
    def mark_dirty(self, asset_type: str):
        """Mark an asset type as modified (unsaved changes)"""
        self._dirty_assets.add(asset_type)
    
    def has_unsaved_changes(self, asset_type: Optional[str] = None) -> bool:
        """
        Check if there are unsaved changes
        
        Args:
            asset_type: Specific asset type to check, or None to check all
        
        Returns:
            True if there are unsaved changes
        """
        if asset_type:
            return asset_type in self._dirty_assets
        return len(self._dirty_assets) > 0
    
    def get_metadata(self, asset_type: str) -> Optional[AssetMetadata]:
        """Get metadata for an asset type"""
        return self._metadata.get(asset_type)
    
    def list_backups(self, asset_type: str) -> List[Path]:
        """List all backup files for a specific asset type"""
        pattern = f"{asset_type}_backup_*.json"
        backups = sorted(self.backup_dir.glob(pattern), reverse=True)  # Newest first
        return backups
    
    def restore_backup(self, asset_type: str, backup_path: Path) -> Path:
        """
        Restore an asset from a backup file
        
        Args:
            asset_type: Type of asset to restore
            backup_path: Path to backup file
        
        Returns:
            Path to restored file
        """
        if not backup_path.exists():
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        output_path = self.json_dir / f"{asset_type}.json"
        
        # Create backup of current file before restoring
        if output_path.exists():
            self._create_backup(asset_type, output_path)
        
        # Restore from backup
        shutil.copy2(backup_path, output_path)
        
        # Clear cache to force reload
        self._cache.pop(asset_type, None)
        
        return output_path
    
    def clear_cache(self, asset_type: Optional[str] = None):
        """
        Clear asset cache
        
        Args:
            asset_type: Specific asset to clear from cache, or None to clear all
        """
        if asset_type:
            self._cache.pop(asset_type, None)
        else:
            self._cache.clear()
    
    def save_all_dirty(self) -> Dict[str, Path]:
        """
        Save all assets with unsaved changes
        
        Returns:
            Dictionary mapping asset types to saved file paths
        """
        saved_files = {}
        
        for asset_type in list(self._dirty_assets):
            if asset_type in self._cache:
                path = self.save_asset(asset_type, self._cache[asset_type])
                saved_files[asset_type] = path
        
        return saved_files


# Convenience function for global access
_global_asset_manager = None

def get_asset_manager(assets_dir: str = "assets") -> AssetManager:
    """Get the global AssetManager instance (singleton pattern)"""
    global _global_asset_manager
    if _global_asset_manager is None:
        _global_asset_manager = AssetManager(assets_dir)
    return _global_asset_manager
