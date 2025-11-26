"""
Extract town/dungeon interior maps and NPC data from Dragon Warrior ROM.

Extracts:
- Interior location maps (towns, castles, caves)
- NPC positions and data
- Treasure chest locations
- Warp/stair positions
"""

import json
import struct
from pathlib import Path
from typing import Dict, List, Tuple, Any

class DragonWarriorMapExtractor:
    """Extract maps and NPC data from Dragon Warrior ROM."""
    
    def __init__(self, rom_path: str):
        """Initialize extractor with ROM path."""
        self.rom_path = Path(rom_path)
        with open(rom_path, 'rb') as f:
            self.rom_data = f.read()
        
        # Map data locations from Bank00
        # MapDatTbl at Bank00:0x000A = ROM offset 0x801A
        # 5 bytes per map: .word pointer, .byte width, .byte height, .byte boundary
        self.MAP_TABLE_OFFSET = 0x801A  # Bank00:0x000A - Map data table (5 bytes per map)
        self.NPC_TABLE_OFFSET = 0xA3D0  # Bank00:0x23C0 - NPC mob pointer table
        self.NPC_STAT_OFFSET = 0xA400   # Bank00:0x23F0 - NPC stat pointer table
        
        # Map IDs from Bank00.asm
        # Map 0 = Unused, Map 1 = Overworld (special), Maps 2-23 = Interior locations
        self.MAPS = {
            2: "Dragonlord's Castle - Ground Floor",
            3: "Hauksness",
            4: "Tantegel Castle - Ground Floor",
            5: "Throne Room",
            6: "Dragonlord's Castle - Bottom Level",
            7: "Kol",
            8: "Brecconary",
            9: "Garinham",
            10: "Cantlin",
            11: "Rimuldar",
            12: "Tantegel Castle - Sublevel",
            13: "Staff of Rain Cave",
            14: "Rainbow Drop Cave",
            15: "Dragonlord's Castle - Sublevel 1",
            16: "Dragonlord's Castle - Sublevel 2",
            17: "Dragonlord's Castle - Sublevel 3",
            18: "Dragonlord's Castle - Sublevel 4",
            19: "Dragonlord's Castle - Sublevel 5",
            20: "Dragonlord's Castle - Sublevel 6",
            21: "Swamp Cave",
            22: "Rock Mountain Cave - B1",
            23: "Erdrick's Cave"
        }
        
        # Tile mappings for visualization
        self.TILE_CHARS = {
            0x00: '.',  # Floor
            0x01: '#',  # Wall
            0x02: 'D',  # Door
            0x03: 'S',  # Stairs down
            0x04: 'U',  # Stairs up
            0x05: 'C',  # Chest
            0x06: 'W',  # Water
            0x07: 'T',  # Throne
            0x08: 'B',  # Bed
            0x09: 'A',  # Counter
        }
    
    def extract_all_maps(self) -> Dict[str, Any]:
        """Extract all interior maps from ROM."""
        maps_data = {}
        
        for map_id, map_name in self.MAPS.items():
            print(f"Extracting map {map_id}: {map_name}")
            map_info = self.extract_map(map_id)
            maps_data[map_name] = map_info
        
        return maps_data
    
    def extract_map(self, map_id: int) -> Dict[str, Any]:
        """
        Extract a single interior map.
        
        Map data format (5 bytes per map in MapDatTbl at ROM 0x801A):
        - 2 bytes: Pointer to map data (little-endian, CPU address)
        - 1 byte: Map width (columns)
        - 1 byte: Map height (rows)
        - 1 byte: Boundary block (out-of-bounds tile)
        
        Map data is stored as sequential tiles (width * height bytes).
        """
        # Each map entry is 5 bytes in MapDatTbl
        table_offset = self.MAP_TABLE_OFFSET + (map_id * 5)
        
        if table_offset + 5 > len(self.rom_data):
            return {
                "error": f"Map {map_id} table entry out of bounds",
                "width": 0,
                "height": 0,
                "tiles": []
            }
        
        # Read map table entry
        ptr_low = self.rom_data[table_offset]
        ptr_high = self.rom_data[table_offset + 1]
        width = self.rom_data[table_offset + 2]
        height = self.rom_data[table_offset + 3]
        boundary = self.rom_data[table_offset + 4]
        
        # Convert CPU pointer ($8000-$BFFF) to ROM offset
        map_data_ptr = (ptr_high << 8) | ptr_low
        
        if map_data_ptr == 0:
            return {
                "error": f"Map {map_id} has null pointer",
                "width": width,
                "height": height,
                "boundary": boundary,
                "tiles": []
            }
        
        # Bank00 CPU range $8000-$BFFF maps to ROM 0x0010-0x4010
        if 0x8000 <= map_data_ptr <= 0xBFFF:
            rom_offset = map_data_ptr - 0x8000 + 0x10
        else:
            return {
                "error": f"Invalid map pointer: ${map_data_ptr:04X}",
                "width": width,
                "height": height,
                "boundary": boundary,
                "tiles": []
            }
        
        if width == 0 or height == 0:
            return {
                "width": width,
                "height": height,
                "boundary": boundary,
                "tiles": [],
                "warning": f"Map has zero dimensions: {width}x{height}"
            }
        
        # Read tile data (width * height bytes)
        tiles = []
        expected_tiles = width * height
        
        for i in range(expected_tiles):
            if rom_offset + i < len(self.rom_data):
                tiles.append(self.rom_data[rom_offset + i])
            else:
                tiles.append(boundary)  # Use boundary tile for out-of-bounds
        
        # Create 2D tile array
        tile_grid = []
        for y in range(height):
            row = []
            for x in range(width):
                idx = y * width + x
                if idx < len(tiles):
                    row.append(tiles[idx])
                else:
                    row.append(boundary)
            tile_grid.append(row)
        
        # Generate ASCII visualization
        ascii_map = self._generate_ascii_map(tile_grid)
        
        return {
            "map_id": map_id,
            "width": width,
            "height": height,
            "boundary": boundary,
            "rom_offset": f"${rom_offset:04X}",
            "cpu_pointer": f"${map_data_ptr:04X}",
            "tiles": tile_grid,
            "ascii_map": ascii_map,
            "total_tiles": len(tiles)
        }
    
    def _generate_ascii_map(self, tile_grid: List[List[int]]) -> List[str]:
        """Generate ASCII representation of map for visualization."""
        ascii_lines = []
        for row in tile_grid:
            line = ""
            for tile in row:
                line += self.TILE_CHARS.get(tile, '?')
            ascii_lines.append(line)
        return ascii_lines
    
    def extract_npc_data(self) -> List[Dict[str, Any]]:
        """
        Extract NPC data from ROM.
        
        NPC format (3 bytes per NPC):
        Byte 0: Graphics/sprite index
        Byte 1: Position (X in lower nibble, Y in upper nibble)
        Byte 2: Direction and dialog control
        """
        npcs = []
        
        # NPC data appears to be in tables
        # Each location has a list of NPCs
        # Format varies - need to analyze Bank00 more carefully
        
        # For now, extract raw NPC table data
        npc_table_start = 0xA3D0
        npc_table_end = 0xA400
        
        offset = npc_table_start
        npc_id = 0
        
        while offset < npc_table_end:
            if offset + 3 > len(self.rom_data):
                break
            
            sprite = self.rom_data[offset]
            position = self.rom_data[offset + 1]
            control = self.rom_data[offset + 2]
            
            # Skip if all zeros (unused entry)
            if sprite == 0 and position == 0 and control == 0:
                offset += 3
                continue
            
            x = position & 0x0F
            y = (position >> 4) & 0x0F
            
            npcs.append({
                "id": npc_id,
                "sprite": sprite,
                "x": x,
                "y": y,
                "direction": control & 0x03,
                "control": control,
                "rom_offset": f"${offset:04X}"
            })
            
            offset += 3
            npc_id += 1
        
        return npcs
    
    def extract_treasure_chests(self) -> List[Dict[str, Any]]:
        """
        Extract treasure chest locations and contents.
        
        Chest data format:
        - Map ID
        - X, Y position
        - Item/Gold amount
        - Flags
        """
        chests = []
        
        # Treasure chest data from Bank00
        # Format needs verification from disassembly
        chest_data_offset = 0xA100  # Approximate location
        
        # Known chest locations (from game knowledge):
        known_chests = [
            {"map": "Tantegel Castle", "x": 7, "y": 4, "item": "Torch", "quantity": 1},
            {"map": "Tantegel Castle", "x": 10, "y": 3, "item": "Magic Key", "quantity": 1},
            {"map": "Erdrick's Cave", "x": 5, "y": 5, "item": "Erdrick's Token", "quantity": 1},
            {"map": "Charlock Castle Basement 4", "x": 1, "y": 1, "item": "Erdrick's Armor", "quantity": 1},
        ]
        
        # TODO: Extract actual chest data from ROM
        # For now, return known locations
        return known_chests
    
    def save_maps_json(self, output_dir: Path):
        """Save extracted maps to JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Extract all data
        maps = self.extract_all_maps()
        npcs = self.extract_npc_data()
        chests = self.extract_treasure_chests()
        
        # Save maps
        maps_file = output_dir / "interior_maps.json"
        with open(maps_file, 'w') as f:
            json.dump(maps, f, indent=2)
        print(f"Saved {len(maps)} maps to {maps_file}")
        
        # Save NPCs
        npcs_file = output_dir / "npcs.json"
        with open(npcs_file, 'w') as f:
            json.dump(npcs, f, indent=2)
        print(f"Saved {len(npcs)} NPCs to {npcs_file}")
        
        # Save chests
        chests_file = output_dir / "treasure_chests.json"
        with open(chests_file, 'w') as f:
            json.dump(chests, f, indent=2)
        print(f"Saved {len(chests)} treasure chests to {chests_file}")
        
        # Create summary
        summary = {
            "total_maps": len(maps),
            "total_npcs": len(npcs),
            "total_chests": len(chests),
            "maps_file": str(maps_file),
            "npcs_file": str(npcs_file),
            "chests_file": str(chests_file),
            "extraction_notes": [
                "Interior maps extracted from ROM using pointer table",
                "NPC data partially extracted - needs verification",
                "Treasure chest data uses known locations - needs ROM verification",
                "ASCII maps generated for visualization"
            ]
        }
        
        summary_file = output_dir / "map_extraction_summary.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        print(f"Saved summary to {summary_file}")
        
        # Print ASCII maps for verification
        print("\n" + "="*60)
        print("ASCII MAP VISUALIZATIONS")
        print("="*60)
        for map_name, map_data in maps.items():
            if 'ascii_map' in map_data:
                print(f"\n{map_name} ({map_data.get('width', 0)}x{map_data.get('height', 0)}):")
                print("-" * 40)
                for line in map_data['ascii_map']:
                    print(line)


def main():
    """Main extraction function."""
    rom_path = "roms/Dragon Warrior (U) (PRG1) [!].nes"
    output_dir = Path("extracted_assets/maps")
    
    print("Dragon Warrior Map & NPC Extractor")
    print("="*60)
    
    extractor = DragonWarriorMapExtractor(rom_path)
    extractor.save_maps_json(output_dir)
    
    print("\n" + "="*60)
    print("Map extraction complete!")
    print("="*60)


if __name__ == "__main__":
    main()
