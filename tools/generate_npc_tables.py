#!/usr/bin/env python3
"""
Generate NPC table assembly from npcs.json

Generates NPC Mobile and Static tables for each map area.
Each NPC entry is 3 bytes: NNNXXXXX _DDYYYYY CCCCCCCC
"""

import json
from pathlib import Path

# Paths
INPUT_PATH = Path(__file__).parent.parent / "assets" / "json" / "npcs.json"
OUTPUT_PATH = Path(__file__).parent.parent / "source_files" / "generated" / "npc_tables.asm"

# Table order matching original ROM layout
TABLE_ORDER = [
    "TantagelMobileTable",
    "TantStatTbl",
    "ThRmMobTbl",
    "ThRmStatTbl",
    "TaSLMobTbl",
    "TaSLStatTbl",
    "TaDLMobTbl",
    "TaDLStatTbl",
    "DLBFMobTbl",
    "DLBFStatTbl",
    "RainMobTbl",
    "RainStatTbl",
    "RnbwMobTbl",
    "RnbwStatTbl",
    "CantMobTbl",
    "CantStatTbl",
    "RimMobTbl",
    "RimStatTbl",
    "BrecMobTbl",
    "BrecStatTbl",
    "KolMobTbl",
    "KolStatTbl",
    "GarMobTbl",
    "GarStatTbl",
]


def encode_npc_bytes(npc):
    """
    Encode an NPC entry to 3 bytes.
    
    Format:
    NNNXXXXX _DDYYYYY CCCCCCCC
    
    Byte 1: NNN = sprite type (3 bits), XXXXX = X position (5 bits)
    Byte 2: _ = unused (0), DD = direction (2 bits), YYYYY = Y position (5 bits)
    Byte 3: Dialog control byte
    """
    sprite_type = npc.get("sprite_type", 0) & 0x07
    x_pos = npc.get("x", 0) & 0x1F
    direction = npc.get("direction", 2) & 0x03  # Default to facing down
    y_pos = npc.get("y", 0) & 0x1F
    dialog_id = npc.get("dialog_id", 0) & 0xFF
    
    byte1 = (sprite_type << 5) | x_pos
    byte2 = (direction << 5) | y_pos
    byte3 = dialog_id
    
    return byte1, byte2, byte3


def get_sprite_name(sprite_type):
    """Get human-readable sprite name."""
    names = {
        0: "Male villager",
        1: "Fighter",
        2: "Guard",
        3: "Shopkeeper",
        4: "King Lorik",
        5: "Wizard",
        6: "Female villager",
        7: "Trumpet guard",
    }
    return names.get(sprite_type, f"Unknown_{sprite_type}")


def generate_npc_tables(data):
    """Generate assembly code for all NPC tables."""
    lines = []
    
    # Header
    lines.append(";----------------------------------------------------------------------------------------------------")
    lines.append("; NPC Tables - Generated from assets/json/npcs.json")
    lines.append("; To modify NPC data, edit the JSON file and rebuild")
    lines.append(";----------------------------------------------------------------------------------------------------")
    lines.append("")
    lines.append(";The tables below control the characteristics of the NPCs. There are 3 bytes per entry and are")
    lines.append(";formatted as follows:")
    lines.append("")
    lines.append(";NNNXXXXX _DDYYYYY CCCCCCCC")
    lines.append(";")
    lines.append(";NNN      - NPC graphic: 0=Male villager, 1=Fighter, 2=Guard, 3=Shopkeeper, 4=King Lorik,")
    lines.append(";             5=Wizard/Dragonlord, 6=Princess Gwaelin/Female villager")
    lines.append(";             7=Stationary guard/Guard with trumpet.")
    lines.append(";XXXXX    - NPC X position.")
    lines.append(";_        - Unused.")
    lines.append(";DD       - NPC direction: 0=Facing up, 1=Facing right, 2=Facing down, 3=Facing left.")
    lines.append(";YYYYY    - NPC Y position.")
    lines.append(";CCCCCCCC - Dialog control byte.")
    lines.append("")
    lines.append(";----------------------------------------------------------------------------------------------------")
    lines.append("")
    
    # Generate each table in order
    for table_name in TABLE_ORDER:
        if table_name not in data:
            print(f"Warning: Table {table_name} not found in JSON")
            continue
        
        table = data[table_name]
        npcs = table.get("npcs", [])
        
        lines.append(f"{table_name}:")
        
        if not npcs:
            # Empty table - just terminator
            lines.append("        .byte $FF               ;No NPCs.")
        else:
            for i, npc in enumerate(npcs):
                byte1, byte2, byte3 = encode_npc_bytes(npc)
                sprite_name = get_sprite_name(npc.get("sprite_type", 0))
                x = npc.get("x", 0)
                y = npc.get("y", 0)
                
                # Format: .byte $XX, $YY, $ZZ     ;Sprite at XX,YY.
                comment = f";{sprite_name} at {x:2},{y:2}."
                lines.append(f"        .byte ${byte1:02X}, ${byte2:02X}, ${byte3:02X}     {comment}")
            
            # Add terminator
            lines.append("        .byte $FF               ;End of table.")
        
        lines.append("")
    
    return "\n".join(lines)


def main():
    # Read input JSON
    if not INPUT_PATH.exists():
        print(f"Error: {INPUT_PATH} not found")
        print("Run extract_npcs_from_rom.py first, then rename npcs_extracted.json to npcs.json")
        return
    
    print(f"Reading: {INPUT_PATH}")
    with open(INPUT_PATH, "r") as f:
        data = json.load(f)
    
    # Generate assembly
    asm_content = generate_npc_tables(data)
    
    # Ensure output directory exists
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    # Write output
    print(f"Writing: {OUTPUT_PATH}")
    with open(OUTPUT_PATH, "w") as f:
        f.write(asm_content)
    
    # Count tables and NPCs
    total_npcs = sum(len(data.get(t, {}).get("npcs", [])) for t in TABLE_ORDER if t in data)
    print(f"Generated {len(TABLE_ORDER)} tables with {total_npcs} NPCs")
    print("Done!")


if __name__ == "__main__":
    main()
