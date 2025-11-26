#!/usr/bin/env python3
"""
Asset Manager Demo - Shows how editors can use the unified asset system
"""
import sys
from pathlib import Path

# Add tools directory to path
sys.path.insert(0, str(Path(__file__).parent / 'tools'))

from asset_manager import AssetManager, AssetValidationError


def demo_load_assets():
    """Demo: Loading assets from JSON files"""
    print("="*80)
    print("DEMO 1: Loading Assets")
    print("="*80)
    
    manager = AssetManager()
    
    # Load items
    print("\nLoading items...")
    items = manager.load_asset('items')
    print(f"✓ Loaded {len(items)} items")
    print(f"  Sample: {items[1]}")  # Club
    
    # Load monsters
    print("\nLoading monsters...")
    monsters = manager.load_asset('monsters')
    print(f"✓ Loaded {len(monsters)} monsters")
    print(f"  Sample: {monsters[0]}")  # Slime
    
    print("\n✓ All assets loaded successfully")


def demo_modify_and_save():
    """Demo: Modifying assets and saving with backup"""
    print("\n" + "="*80)
    print("DEMO 2: Modifying and Saving Assets")
    print("="*80)
    
    manager = AssetManager()
    
    # Load items
    items = manager.load_asset('items')
    
    # Modify an item (make Club stronger!)
    club = items[1]
    original_attack = club.get('attack_power', 0)
    club['attack_power'] = original_attack + 5
    
    print(f"\nModified Club: attack_power {original_attack} → {club['attack_power']}")
    
    # Mark as dirty
    manager.mark_dirty('items')
    print(f"Unsaved changes: {manager.has_unsaved_changes('items')}")
    
    # Save with backup
    print("\nSaving items with backup...")
    saved_path = manager.save_asset('items', items, create_backup=True)
    print(f"✓ Saved to: {saved_path}")
    
    # Check backups
    backups = manager.list_backups('items')
    print(f"✓ Available backups: {len(backups)}")
    if backups:
        print(f"  Latest: {backups[0].name}")
    
    # Restore original value
    club['attack_power'] = original_attack
    manager.save_asset('items', items, create_backup=False)
    print(f"\n✓ Restored Club to original attack_power={original_attack}")


def demo_validation():
    """Demo: Asset validation catches errors"""
    print("\n" + "="*80)
    print("DEMO 3: Asset Validation")
    print("="*80)
    
    manager = AssetManager()
    items = manager.load_asset('items')
    
    # Create an invalid item
    invalid_item = {
        'id': 99,
        'name': 'Test Sword',
        'attack_power': 500,  # Too high! Max is 127
        'defense_power': 0,
        'buy_price': 100,
        'sell_price': 50
    }
    
    items[99] = invalid_item
    
    print("\nTrying to save item with invalid attack_power=500...")
    try:
        manager.save_asset('items', items, validate=True, create_backup=False)
        print("❌ Should have failed validation!")
    except AssetValidationError as e:
        print(f"✓ Validation caught error: {e}")
    
    # Fix the item
    invalid_item['attack_power'] = 50
    print(f"\nFixed item: attack_power=50")
    
    try:
        manager.save_asset('items', items, validate=True, create_backup=False)
        print("✓ Item saved successfully after fix")
    except AssetValidationError as e:
        print(f"❌ Unexpected error: {e}")
    
    # Remove test item
    del items[99]
    manager.save_asset('items', items, create_backup=False)


def demo_metadata():
    """Demo: Asset metadata and information"""
    print("\n" + "="*80)
    print("DEMO 4: Asset Metadata")
    print("="*80)
    
    manager = AssetManager()
    
    # Load assets
    items = manager.load_asset('items')
    monsters = manager.load_asset('monsters')
    
    # Get metadata
    print("\nAsset Metadata:")
    print("-"*80)
    
    for asset_type in ['items', 'monsters']:
        metadata = manager.get_metadata(asset_type)
        if metadata:
            print(f"\n{asset_type.upper()}:")
            print(f"  File: {metadata.file_path.name}")
            print(f"  Records: {metadata.record_count}")
            print(f"  Last Modified: {metadata.last_modified}")
            print(f"  Version: {metadata.version}")


def demo_editor_workflow():
    """Demo: Typical editor workflow"""
    print("\n" + "="*80)
    print("DEMO 5: Complete Editor Workflow")
    print("="*80)
    
    manager = AssetManager()
    
    print("\n1. Load assets...")
    items = manager.load_asset('items')
    print(f"   ✓ Loaded {len(items)} items")
    
    print("\n2. User edits item (Copper Sword)...")
    copper_sword = items[2]
    original_price = copper_sword.get('buy_price', 0)
    copper_sword['buy_price'] = 200  # Increase price
    manager.mark_dirty('items')
    print(f"   ✓ Changed price: {original_price} → {copper_sword['buy_price']}")
    
    print("\n3. Check for unsaved changes...")
    if manager.has_unsaved_changes('items'):
        print("   ⚠ Unsaved changes detected!")
    
    print("\n4. Save changes with validation and backup...")
    try:
        saved_path = manager.save_asset('items', items, create_backup=True, validate=True)
        print(f"   ✓ Saved successfully to: {saved_path.name}")
    except AssetValidationError as e:
        print(f"   ❌ Validation failed: {e}")
    
    print("\n5. Verify changes were saved...")
    manager.clear_cache('items')  # Force reload from disk
    items_reloaded = manager.load_asset('items', use_cache=False)
    copper_sword_reloaded = items_reloaded[2]
    print(f"   ✓ Reloaded price: {copper_sword_reloaded.get('buy_price')}")
    
    print("\n6. Restore original...")
    copper_sword_reloaded['buy_price'] = original_price
    manager.save_asset('items', items_reloaded, create_backup=False)
    print(f"   ✓ Restored original price: {original_price}")
    
    print("\n✓ Complete workflow demonstrated successfully!")


def main():
    """Run all demonstrations"""
    print("\n" + "#"*80)
    print("# ASSET MANAGER DEMONSTRATION")
    print("# Shows how editors can use the unified asset management system")
    print("#"*80 + "\n")
    
    try:
        demo_load_assets()
        demo_modify_and_save()
        demo_validation()
        demo_metadata()
        demo_editor_workflow()
        
        print("\n" + "="*80)
        print("ALL DEMONSTRATIONS COMPLETED SUCCESSFULLY")
        print("="*80)
        print("\nKey Features Demonstrated:")
        print("  ✓ Loading assets from JSON with caching")
        print("  ✓ Modifying asset data")
        print("  ✓ Automatic backup creation")
        print("  ✓ Data validation before save")
        print("  ✓ Change tracking (dirty flags)")
        print("  ✓ Metadata management")
        print("  ✓ Complete editor workflow")
        print("\nEditors can now use AssetManager instead of direct ROM editing!")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
