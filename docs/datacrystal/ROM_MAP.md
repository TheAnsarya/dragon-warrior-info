# Dragon Warrior - ROM Map

**Game:** Dragon Warrior (USA)  
**Platform:** Nintendo Entertainment System (NES)  
**ROM Size:** 256 KB (262,144 bytes)  
**Mapper:** NROM (Mapper 0)  

## ROM Structure Overview

Dragon Warrior uses the standard NES ROM format with a 16-byte iNES header followed by PRG-ROM and CHR-ROM data.

### iNES Header (0x0000-0x000f)
```
Offset  Size  Description
0x0000  4     "NES" followed by MS-DOS EOF (0x4e 0x45 0x53 0x1a)
0x0004  1     PRG-ROM size in 16KB units (0x10 = 256KB)
0x0005  1     CHR-ROM size in 8KB units (0x00 = no CHR-ROM)
0x0006  1     Flags 6 (Mapper, mirroring, battery, trainer)
0x0007  1     Flags 7 (Mapper, VS/Playchoice, NES 2.0)
0x0008  1     Flags 8 (PRG-RAM size)
0x0009  1     Flags 9 (TV system)
0x000a  1     Flags 10 (TV system, PRG-RAM presence)
0x000b  5     Unused padding (should be zero)
```

## Memory Layout

### CPU Memory Map (6502 Address Space)
```
Address Range   Size    Description
0x0000-0x07ff   2KB     Internal RAM (mirrored 4 times)
0x0800-0x1fff   -       Mirrors of RAM
0x2000-0x2007   8B      PPU registers (mirrored)
0x2008-0x3fff   -       Mirrors of PPU registers  
0x4000-0x4017   24B     APU and I/O registers
0x4018-0x401f   8B      APU and I/O functionality (disabled)
0x4020-0x5fff   8KB     Expansion ROM (rarely used)
0x6000-0x7fff   8KB     SRAM (battery-backed save data)
0x8000-0xbfff   16KB    PRG-ROM Bank 0 (fixed)
0xc000-0xffff   16KB    PRG-ROM Bank 1 (fixed)
```

### PPU Memory Map (Video)
```
Address Range   Size    Description
0x0000-0x0fff   4KB     Pattern Table 0
0x1000-0x1fff   4KB     Pattern Table 1  
0x2000-0x23ff   1KB     Name Table 0
0x2400-0x27ff   1KB     Name Table 1
0x2800-0x2bff   1KB     Name Table 2 (mirror)
0x2c00-0x2fff   1KB     Name Table 3 (mirror)
0x3000-0x3eff   -       Mirrors of Name Tables
0x3f00-0x3f1f   32B     Palette RAM
0x3f20-0x3fff   -       Mirrors of Palette RAM
```

## ROM Data Sections

### PRG-ROM (0x0010-0x4000f in ROM file)

#### Bank 0 (0x8000-0xbfff)
```
CPU Address  ROM Offset  Size   Description
0x8000       0x0010     ?KB    Game initialization code
0x????       0x????     ?KB    Main game loop
0x????       0x????     ?KB    Battle system code
0x????       0x????     ?KB    Menu and interface code
0x????       0x????     ?KB    Map and movement code
0xbfff       0x????     -      End of Bank 0
```

#### Bank 1 (0xc000-0xffff)
```
CPU Address  ROM Offset  Size   Description
0xc000       0x????     ?KB    Game data tables
0x????       0x????     ?KB    Text and dialog data
0x????       0x????     ?KB    Music and sound data
0x????       0x????     ?KB    Graphics data (if any)
0xfffa       0x????     6B     Interrupt vectors (NMI, RESET, IRQ)
```

### CHR-ROM (Pattern Tables)
Dragon Warrior uses CHR-RAM instead of CHR-ROM, so graphics data is stored in PRG-ROM and copied to CHR-RAM during runtime.

## SRAM Layout (0x6000-0x7fff)

The SRAM (Save RAM) area contains the game's save data, typically battery-backed to persist between power cycles.

```
Offset  Size  Description
0x6000  ?B    Player character data
0x????  ?B    Inventory data
0x????  ?B    Progress flags and switches
0x????  ?B    Current location and position
0x????  ?B    Game statistics
0x????  ?B    Checksum or validation data
```

*Note: Exact SRAM structure requires detailed analysis*

## Data Tables and Structures

### Character Stats
*Location: TBD through analysis*
```
Offset  Size  Description
+0x00   1B    Level
+0x01   2B    Hit Points (current/max)
+0x03   2B    Magic Points (current/max)  
+0x05   1B    Strength
+0x06   1B    Agility
+0x07   1B    Attack Power
+0x08   1B    Defense Power
+0x09   2B    Experience Points
+0x0b   2B    Gold
```

### Monster Stats
*Location: TBD through analysis*
```
Offset  Size  Description
+0x00   1B    Monster ID
+0x01   2B    Hit Points
+0x03   1B    Attack Power
+0x04   1B    Defense Power
+0x05   1B    Agility
+0x06   1B    Experience Reward
+0x07   2B    Gold Reward
+0x09   1B    Special abilities flags
```

### Item Data
*Location: TBD through analysis*
```
Offset  Size  Description
+0x00   1B    Item ID
+0x01   1B    Item Type (weapon, armor, item, etc.)
+0x02   2B    Effect Value (attack bonus, healing, etc.)
+0x04   2B    Purchase Price
+0x06   2B    Sale Price
+0x08   1B    Usability flags
```

### Spell Data
*Location: TBD through analysis*
```
Offset  Size  Description  
+0x00   1B    Spell ID
+0x01   1B    MP Cost
+0x02   1B    Spell Type (healing, attack, utility)
+0x03   2B    Base Effect Value
+0x05   1B    Level Requirement
+0x06   1B    Target type (self, enemy, etc.)
```

## Text Encoding

Dragon Warrior uses a custom text encoding system:

### Character Set
*To be determined through analysis*
```
Value   Character
0x00    [End of string]
0x01    [Space]
0x02-?  [Letters A-Z]
?-?     [Numbers 0-9]
?-?     [Punctuation]
?-?     [Special control codes]
```

### Dialog System
*Structure to be analyzed*
- Text compression method (if any)
- Dialog box formatting codes
- Character name insertion
- Number formatting for stats/gold

## Graphics Format

### Tile Format
Dragon Warrior uses standard NES 2bpp (2 bits per pixel) tile format:
- Each tile is 8x8 pixels
- 2 bits per pixel = 4 colors per tile
- 16 bytes per tile (8 bytes plane 0, 8 bytes plane 1)

### Sprite Format
Character and monster sprites use the same 2bpp format but may be composed of multiple tiles.

### Palette Format
NES palette format:
- 4 background palettes (4 colors each)
- 4 sprite palettes (4 colors each)
- Color 0 of each palette is transparent for sprites
- Colors reference the NES system palette (64 colors total)

## Music and Sound

### Audio Engine
*To be analyzed*
- Sound register usage patterns
- Music data format and compression
- Sound effect storage and playback
- Tempo and timing systems

## Known Addresses

*To be populated through analysis*

### Important Functions
```
Address   Description
0x????    Main game loop
0x????    Battle system entry
0x????    Text display routine
0x????    Save game routine
0x????    Load game routine
0x????    Random number generator
```

### Data Tables
```
Address   Description
0x????    Monster stats table
0x????    Item data table
0x????    Spell data table
0x????    Experience table
0x????    Character name table
```

## Hacking Notes

### Common Modifications
- Stat modifications: Adjust character growth rates
- Item editing: Change prices, effects, availability
- Monster editing: HP, attack, defense, rewards
- Text changes: Dialog, item names, descriptions
- Graphics: Sprite and tile replacement

### Technical Considerations
- NROM mapper limitations (no bank switching)
- Limited ROM space for modifications
- SRAM save compatibility
- Emulator vs. hardware differences

## Research Status

**Completion: ~5%**

- ✅ Basic ROM structure identified
- ✅ Memory layout documented
- ⏳ Data table locations (in progress)
- ❌ Text encoding system (not started)
- ❌ Graphics compression (not started)
- ❌ Music format (not started)
- ❌ Save system details (not started)

## References

- [NES Development Wiki](https://wiki.nesdev.com/)
- [Dragon Warrior GameFAQs](https://gamefaqs.gamespot.com/nes/563408-dragon-warrior)
- [DataCrystal Dragon Warrior](https://datacrystal.tcrf.net/) (if available)

---
**Last Updated:** November 18, 2025  
**Analyzed ROM:** Dragon Warrior (USA)  
**Analysis Tools:** Custom Python extraction suite