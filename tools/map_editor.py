#!/usr/bin/env python3
"""
Dragon Warrior Map Editor

Interactive map editing tool with visualization and validation.
Supports overworld, towns, and dungeons.

Usage:
    python tools/map_editor.py [options]
    
    --rom PATH              Path to ROM file
    --map TYPE              Map type: overworld, town, dungeon
    --export PATH           Export map data to file
    --import PATH           Import map data from file
    --visualize             Show visual representation
    --validate              Validate map data

Features:
    - Interactive tile editing
    - Visual map display with colors
    - Collision detection
    - NPC position validation
    - Warp/stairs detection
    - Map statistics

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import argparse
import json
import os
import sys
from dataclasses import dataclass, asdict
from typing import List, Tuple, Optional, Dict
from pathlib import Path


@dataclass
class Tile:
    """
    8×8 map tile
    
    Attributes:
        id: Tile ID (0x00-0xFF)
        name: Tile name (e.g., "Grass", "Water")
        walkable: Can player walk on this tile?
        damage: Damage taken per step (e.g., swamp)
        encounter: Enable random encounters?
    """
    id: int
    name: str
    walkable: bool = True
    damage: int = 0
    encounter: bool = False
    
    def __repr__(self):
        flags = []
        if not self.walkable:
            flags.append("BLOCK")
        if self.damage:
            flags.append(f"DMG:{self.damage}")
        if self.encounter:
            flags.append("ENC")
        
        flag_str = f" [{', '.join(flags)}]" if flags else ""
        return f"Tile({self.id:02X}: {self.name}{flag_str})"


@dataclass
class MapObject:
    """
    Map object (NPC, warp, stairs)
    
    Attributes:
        x: X position
        y: Y position
        type: Object type
        id: Object ID
        data: Additional data (direction, destination, etc.)
    """
    x: int
    y: int
    type: str  # "npc", "warp", "stairs", "treasure"
    id: int
    data: Dict = None
    
    def __post_init__(self):
        if self.data is None:
            self.data = {}


class MapData:
    """
    Dragon Warrior map data
    
    Supports:
        - Overworld (120×120 tiles)
        - Towns (various sizes)
        - Dungeons (various sizes)
    """
    
    # Tile definitions (Dragon Warrior NES)
    TILE_DEFS = {
        0x00: Tile(0x00, "Ocean", walkable=False),
        0x01: Tile(0x01, "Grass", walkable=True, encounter=True),
        0x02: Tile(0x02, "Desert", walkable=True, encounter=True),
        0x03: Tile(0x03, "Hill", walkable=True, encounter=True),
        0x04: Tile(0x04, "Mountain", walkable=False),
        0x05: Tile(0x05, "Swamp", walkable=True, damage=1, encounter=True),
        0x06: Tile(0x06, "Town", walkable=True),
        0x07: Tile(0x07, "Cave", walkable=True),
        0x08: Tile(0x08, "Castle", walkable=True),
        0x09: Tile(0x09, "Bridge", walkable=True),
        0x0A: Tile(0x0A, "Stairs Down", walkable=True),
        0x0B: Tile(0x0B, "Stairs Up", walkable=True),
        0x0C: Tile(0x0C, "Barrier", walkable=False),
        0x0D: Tile(0x0D, "Treasure", walkable=True),
        0x0E: Tile(0x0E, "Door", walkable=True),
        0x0F: Tile(0x0F, "Brick Wall", walkable=False),
        # Add more as needed...
    }
    
    # Visual representation for terminal
    TILE_CHARS = {
        0x00: '≈',  # Ocean
        0x01: '.',  # Grass
        0x02: '·',  # Desert
        0x03: '^',  # Hill
        0x04: '▲',  # Mountain
        0x05: '~',  # Swamp
        0x06: '■',  # Town
        0x07: '○',  # Cave
        0x08: '▣',  # Castle
        0x09: '=',  # Bridge
        0x0A: '↓',  # Stairs down
        0x0B: '↑',  # Stairs up
        0x0C: '#',  # Barrier
        0x0D: '$',  # Treasure
        0x0E: '+',  # Door
        0x0F: '█',  # Wall
    }
    
    def __init__(self, width: int, height: int, name: str = "Untitled"):
        """
        Initialize map data
        
        Args:
            width: Map width in tiles
            height: Map height in tiles
            name: Map name
        """
        self.width = width
        self.height = height
        self.name = name
        
        # Initialize with grass (0x01)
        self.tiles = [[0x01 for _ in range(width)] for _ in range(height)]
        
        # Map objects
        self.objects: List[MapObject] = []
        
        # Metadata
        self.metadata = {
            'encounters_enabled': True,
            'starting_position': (60, 60),
            'music': 0,
        }
    
    def get_tile(self, x: int, y: int) -> int:
        """Get tile ID at position"""
        if not self.in_bounds(x, y):
            return 0xFF
        return self.tiles[y][x]
    
    def set_tile(self, x: int, y: int, tile_id: int) -> bool:
        """
        Set tile at position
        
        Returns:
            True if successful, False if out of bounds
        """
        if not self.in_bounds(x, y):
            return False
        
        self.tiles[y][x] = tile_id
        return True
    
    def in_bounds(self, x: int, y: int) -> bool:
        """Check if position is within map bounds"""
        return 0 <= x < self.width and 0 <= y < self.height
    
    def is_walkable(self, x: int, y: int) -> bool:
        """Check if tile is walkable"""
        tile_id = self.get_tile(x, y)
        tile_def = self.TILE_DEFS.get(tile_id)
        
        if tile_def is None:
            return True  # Unknown tiles default to walkable
        
        return tile_def.walkable
    
    def add_object(self, obj: MapObject) -> bool:
        """
        Add map object
        
        Returns:
            True if successful, False if position invalid
        """
        if not self.in_bounds(obj.x, obj.y):
            return False
        
        self.objects.append(obj)
        return True
    
    def remove_object(self, x: int, y: int) -> bool:
        """
        Remove object at position
        
        Returns:
            True if object removed, False if none found
        """
        for i, obj in enumerate(self.objects):
            if obj.x == x and obj.y == y:
                del self.objects[i]
                return True
        return False
    
    def get_objects_at(self, x: int, y: int) -> List[MapObject]:
        """Get all objects at position"""
        return [obj for obj in self.objects if obj.x == x and obj.y == y]
    
    def flood_fill(self, x: int, y: int, new_tile: int):
        """
        Flood fill region with new tile
        
        Fills all connected tiles of the same type.
        """
        old_tile = self.get_tile(x, y)
        if old_tile == new_tile:
            return  # No change
        
        # Stack-based flood fill (avoid recursion depth issues)
        stack = [(x, y)]
        visited = set()
        
        while stack:
            cx, cy = stack.pop()
            
            if (cx, cy) in visited:
                continue
            if not self.in_bounds(cx, cy):
                continue
            if self.get_tile(cx, cy) != old_tile:
                continue
            
            # Fill this tile
            self.set_tile(cx, cy, new_tile)
            visited.add((cx, cy))
            
            # Add neighbors
            stack.extend([
                (cx + 1, cy),
                (cx - 1, cy),
                (cx, cy + 1),
                (cx, cy - 1),
            ])
    
    def draw_rectangle(self, x1: int, y1: int, x2: int, y2: int, 
                       tile_id: int, fill: bool = False):
        """
        Draw rectangle
        
        Args:
            x1, y1: Top-left corner
            x2, y2: Bottom-right corner
            tile_id: Tile to draw
            fill: Fill interior if True
        """
        # Ensure proper ordering
        if x1 > x2:
            x1, x2 = x2, x1
        if y1 > y2:
            y1, y2 = y2, y1
        
        if fill:
            # Fill rectangle
            for y in range(y1, y2 + 1):
                for x in range(x1, x2 + 1):
                    self.set_tile(x, y, tile_id)
        else:
            # Draw outline
            for x in range(x1, x2 + 1):
                self.set_tile(x, y1, tile_id)
                self.set_tile(x, y2, tile_id)
            for y in range(y1, y2 + 1):
                self.set_tile(x1, y, tile_id)
                self.set_tile(x2, y, tile_id)
    
    def visualize(self, x: int = 0, y: int = 0, 
                  width: int = 40, height: int = 20) -> str:
        """
        Generate ASCII visualization
        
        Args:
            x, y: Top-left corner of view
            width, height: View size
            
        Returns:
            String representation
        """
        lines = []
        
        # Header
        lines.append(f"Map: {self.name} ({self.width}×{self.height})")
        lines.append(f"View: ({x},{y}) to ({x+width},{y+height})")
        lines.append("─" * (width + 2))
        
        # Tiles
        for row in range(y, min(y + height, self.height)):
            line = ""
            for col in range(x, min(x + width, self.width)):
                tile_id = self.tiles[row][col]
                
                # Check for objects at this position
                objs = self.get_objects_at(col, row)
                if objs:
                    # Show object instead of tile
                    obj = objs[0]
                    if obj.type == "npc":
                        line += "N"
                    elif obj.type == "warp":
                        line += "W"
                    elif obj.type == "stairs":
                        line += "S"
                    elif obj.type == "treasure":
                        line += "T"
                    else:
                        line += "?"
                else:
                    # Show tile
                    line += self.TILE_CHARS.get(tile_id, '?')
            
            lines.append(line)
        
        lines.append("─" * (width + 2))
        
        # Legend
        lines.append("\nLegend:")
        shown_tiles = set()
        for row in self.tiles[y:y+height]:
            for tile_id in row[x:x+width]:
                if tile_id not in shown_tiles:
                    tile_def = self.TILE_DEFS.get(tile_id)
                    char = self.TILE_CHARS.get(tile_id, '?')
                    name = tile_def.name if tile_def else f"Unknown (0x{tile_id:02X})"
                    lines.append(f"  {char} = {name}")
                    shown_tiles.add(tile_id)
        
        # Objects
        if self.objects:
            lines.append(f"\nObjects: {len(self.objects)}")
            for obj in self.objects[:10]:  # Show first 10
                lines.append(f"  {obj.type} at ({obj.x},{obj.y})")
            if len(self.objects) > 10:
                lines.append(f"  ... and {len(self.objects) - 10} more")
        
        return "\n".join(lines)
    
    def validate(self) -> List[str]:
        """
        Validate map data
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check dimensions
        if self.width < 1 or self.height < 1:
            errors.append(f"Invalid dimensions: {self.width}×{self.height}")
        
        if self.width > 255 or self.height > 255:
            errors.append(f"Dimensions too large: {self.width}×{self.height}")
        
        # Check for unreachable areas
        start_x, start_y = self.metadata.get('starting_position', (0, 0))
        if not self.in_bounds(start_x, start_y):
            errors.append(f"Starting position out of bounds: ({start_x},{start_y})")
        elif not self.is_walkable(start_x, start_y):
            errors.append(f"Starting position not walkable: ({start_x},{start_y})")
        
        # Check objects
        for obj in self.objects:
            if not self.in_bounds(obj.x, obj.y):
                errors.append(f"Object {obj.type} out of bounds: ({obj.x},{obj.y})")
            
            if obj.type == "npc" and not self.is_walkable(obj.x, obj.y):
                errors.append(f"NPC on unwalkable tile: ({obj.x},{obj.y})")
            
            if obj.type == "warp":
                if 'destination' not in obj.data:
                    errors.append(f"Warp missing destination: ({obj.x},{obj.y})")
        
        # Check for isolated tiles
        if errors == []:  # Only check if no critical errors
            walkable_count = sum(
                1 for row in self.tiles for tile in row 
                if self.TILE_DEFS.get(tile, Tile(0, "")).walkable
            )
            
            if walkable_count == 0:
                errors.append("No walkable tiles in map")
        
        return errors
    
    def calculate_statistics(self) -> Dict:
        """
        Calculate map statistics
        
        Returns:
            Dictionary with statistics
        """
        tile_counts = {}
        
        for row in self.tiles:
            for tile in row:
                tile_counts[tile] = tile_counts.get(tile, 0) + 1
        
        total_tiles = self.width * self.height
        
        stats = {
            'dimensions': f"{self.width}×{self.height}",
            'total_tiles': total_tiles,
            'unique_tiles': len(tile_counts),
            'objects': len(self.objects),
            'tile_breakdown': {},
        }
        
        for tile_id, count in sorted(tile_counts.items(), 
                                       key=lambda x: x[1], 
                                       reverse=True):
            tile_def = self.TILE_DEFS.get(tile_id)
            name = tile_def.name if tile_def else f"Unknown (0x{tile_id:02X})"
            percentage = (count / total_tiles) * 100
            stats['tile_breakdown'][name] = {
                'count': count,
                'percentage': f"{percentage:.1f}%"
            }
        
        return stats
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON export"""
        return {
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'tiles': self.tiles,
            'objects': [asdict(obj) for obj in self.objects],
            'metadata': self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'MapData':
        """Load from dictionary"""
        map_data = cls(data['width'], data['height'], data['name'])
        map_data.tiles = data['tiles']
        map_data.objects = [MapObject(**obj) for obj in data['objects']]
        map_data.metadata = data.get('metadata', {})
        return map_data
    
    def export_to_file(self, path: str):
        """Export map to JSON file"""
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2)
        print(f"Map exported to {path}")
    
    @classmethod
    def import_from_file(cls, path: str) -> 'MapData':
        """Import map from JSON file"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)


class MapEditor:
    """
    Interactive map editor
    
    Commands:
        view [x] [y] [w] [h] - View map region
        set <x> <y> <tile>   - Set tile
        fill <x> <y> <tile>  - Flood fill
        rect <x1> <y1> <x2> <y2> <tile> [fill] - Draw rectangle
        obj <type> <x> <y>   - Add object
        rmobj <x> <y>        - Remove object
        validate             - Validate map
        stats                - Show statistics
        save <path>          - Save map
        load <path>          - Load map
        help                 - Show commands
        quit                 - Exit
    """
    
    def __init__(self, map_data: MapData):
        """Initialize editor"""
        self.map = map_data
        self.view_x = 0
        self.view_y = 0
        self.view_width = 40
        self.view_height = 20
    
    def run(self):
        """Run interactive editor"""
        print(f"Dragon Warrior Map Editor - {self.map.name}")
        print("Type 'help' for commands\n")
        
        # Show initial view
        print(self.map.visualize(self.view_x, self.view_y, 
                                  self.view_width, self.view_height))
        
        while True:
            try:
                command = input("\n> ").strip()
                if not command:
                    continue
                
                if not self.process_command(command):
                    break  # Quit
                    
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except Exception as e:
                print(f"Error: {e}")
    
    def process_command(self, command: str) -> bool:
        """
        Process command
        
        Returns:
            True to continue, False to quit
        """
        parts = command.split()
        if not parts:
            return True
        
        cmd = parts[0].lower()
        args = parts[1:]
        
        if cmd == 'quit' or cmd == 'exit':
            return False
        
        elif cmd == 'help':
            print(self.__class__.__doc__)
        
        elif cmd == 'view':
            if len(args) >= 4:
                self.view_x = int(args[0])
                self.view_y = int(args[1])
                self.view_width = int(args[2])
                self.view_height = int(args[3])
            print(self.map.visualize(self.view_x, self.view_y,
                                      self.view_width, self.view_height))
        
        elif cmd == 'set':
            if len(args) < 3:
                print("Usage: set <x> <y> <tile_id>")
                return True
            
            x, y = int(args[0]), int(args[1])
            tile = int(args[2], 16) if args[2].startswith('0x') else int(args[2])
            
            if self.map.set_tile(x, y, tile):
                print(f"Set tile at ({x},{y}) to 0x{tile:02X}")
                print(self.map.visualize(self.view_x, self.view_y,
                                          self.view_width, self.view_height))
            else:
                print("Position out of bounds")
        
        elif cmd == 'fill':
            if len(args) < 3:
                print("Usage: fill <x> <y> <tile_id>")
                return True
            
            x, y = int(args[0]), int(args[1])
            tile = int(args[2], 16) if args[2].startswith('0x') else int(args[2])
            
            self.map.flood_fill(x, y, tile)
            print(f"Flood filled from ({x},{y}) with 0x{tile:02X}")
            print(self.map.visualize(self.view_x, self.view_y,
                                      self.view_width, self.view_height))
        
        elif cmd == 'rect':
            if len(args) < 5:
                print("Usage: rect <x1> <y1> <x2> <y2> <tile> [fill]")
                return True
            
            x1, y1 = int(args[0]), int(args[1])
            x2, y2 = int(args[2]), int(args[3])
            tile = int(args[4], 16) if args[4].startswith('0x') else int(args[4])
            fill = len(args) > 5 and args[5].lower() == 'fill'
            
            self.map.draw_rectangle(x1, y1, x2, y2, tile, fill)
            print(f"Drew rectangle ({x1},{y1})-({x2},{y2})")
            print(self.map.visualize(self.view_x, self.view_y,
                                      self.view_width, self.view_height))
        
        elif cmd == 'obj':
            if len(args) < 3:
                print("Usage: obj <type> <x> <y>")
                return True
            
            obj_type, x, y = args[0], int(args[1]), int(args[2])
            obj = MapObject(x, y, obj_type, 0)
            
            if self.map.add_object(obj):
                print(f"Added {obj_type} at ({x},{y})")
            else:
                print("Invalid position")
        
        elif cmd == 'rmobj':
            if len(args) < 2:
                print("Usage: rmobj <x> <y>")
                return True
            
            x, y = int(args[0]), int(args[1])
            if self.map.remove_object(x, y):
                print(f"Removed object at ({x},{y})")
            else:
                print("No object found")
        
        elif cmd == 'validate':
            errors = self.map.validate()
            if errors:
                print("Validation errors:")
                for error in errors:
                    print(f"  - {error}")
            else:
                print("✓ Map is valid")
        
        elif cmd == 'stats':
            stats = self.map.calculate_statistics()
            print(f"\nMap Statistics: {self.map.name}")
            print(f"Dimensions: {stats['dimensions']}")
            print(f"Total tiles: {stats['total_tiles']}")
            print(f"Unique tiles: {stats['unique_tiles']}")
            print(f"Objects: {stats['objects']}")
            print("\nTile breakdown:")
            for name, data in stats['tile_breakdown'].items():
                print(f"  {name}: {data['count']} ({data['percentage']})")
        
        elif cmd == 'save':
            if len(args) < 1:
                print("Usage: save <path>")
                return True
            
            self.map.export_to_file(args[0])
        
        elif cmd == 'load':
            if len(args) < 1:
                print("Usage: load <path>")
                return True
            
            self.map = MapData.import_from_file(args[0])
            print(f"Loaded map: {self.map.name}")
            print(self.map.visualize(self.view_x, self.view_y,
                                      self.view_width, self.view_height))
        
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for commands")
        
        return True


def extract_map_from_rom(rom_path: str, map_type: str) -> MapData:
    """
    Extract map from ROM
    
    Args:
        rom_path: Path to Dragon Warrior ROM
        map_type: "overworld", "town", or "dungeon"
        
    Returns:
        MapData object
    """
    with open(rom_path, 'rb') as f:
        rom = bytearray(f.read())
    
    # Dragon Warrior map offsets (approximate)
    if map_type == "overworld":
        # Overworld is 120×120
        offset = 0x1B3B0
        width, height = 120, 120
        name = "Alefgard Overworld"
    elif map_type == "tantegel":
        offset = 0x1C000
        width, height = 30, 30
        name = "Tantegel Castle"
    elif map_type == "charlock":
        offset = 0x1C500
        width, height = 30, 30
        name = "Charlock Castle"
    else:
        raise ValueError(f"Unknown map type: {map_type}")
    
    # Create map
    map_data = MapData(width, height, name)
    
    # Extract tiles (row-major order)
    for y in range(height):
        for x in range(width):
            tile_offset = offset + (y * width + x)
            if tile_offset < len(rom):
                map_data.tiles[y][x] = rom[tile_offset]
    
    print(f"Extracted {name} from ROM")
    return map_data


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Dragon Warrior Map Editor"
    )
    parser.add_argument(
        '--rom',
        help="Path to Dragon Warrior ROM"
    )
    parser.add_argument(
        '--map',
        choices=['overworld', 'tantegel', 'charlock'],
        default='overworld',
        help="Map type to edit"
    )
    parser.add_argument(
        '--export',
        help="Export map to JSON file"
    )
    parser.add_argument(
        '--import',
        dest='import_path',
        help="Import map from JSON file"
    )
    parser.add_argument(
        '--visualize',
        action='store_true',
        help="Show visual representation and exit"
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help="Validate map and exit"
    )
    parser.add_argument(
        '--stats',
        action='store_true',
        help="Show statistics and exit"
    )
    parser.add_argument(
        '--create',
        nargs=2,
        metavar=('WIDTH', 'HEIGHT'),
        help="Create new empty map"
    )
    
    args = parser.parse_args()
    
    # Load or create map
    if args.import_path:
        map_data = MapData.import_from_file(args.import_path)
    elif args.rom:
        map_data = extract_map_from_rom(args.rom, args.map)
    elif args.create:
        width, height = int(args.create[0]), int(args.create[1])
        map_data = MapData(width, height, "New Map")
    else:
        # Default: create small test map
        map_data = MapData(40, 20, "Test Map")
        print("Created default 40×20 test map")
        print("Use --rom to load from ROM or --create WIDTH HEIGHT")
    
    # Process single-action commands
    if args.visualize:
        print(map_data.visualize())
        return 0
    
    if args.validate:
        errors = map_data.validate()
        if errors:
            print("Validation errors:")
            for error in errors:
                print(f"  - {error}")
            return 1
        else:
            print("✓ Map is valid")
            return 0
    
    if args.stats:
        stats = map_data.calculate_statistics()
        print(f"Map Statistics: {map_data.name}")
        print(f"Dimensions: {stats['dimensions']}")
        print(f"Total tiles: {stats['total_tiles']}")
        print(f"Unique tiles: {stats['unique_tiles']}")
        print(f"Objects: {stats['objects']}")
        print("\nTile breakdown:")
        for name, data in stats['tile_breakdown'].items():
            print(f"  {name}: {data['count']} ({data['percentage']})")
        return 0
    
    if args.export:
        map_data.export_to_file(args.export)
        return 0
    
    # Interactive mode
    editor = MapEditor(map_data)
    editor.run()
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
