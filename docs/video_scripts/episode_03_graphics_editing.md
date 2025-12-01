# Episode 3: Graphics Editing with CHR Tools

## Video Metadata

| Field | Value |
|-------|-------|
| **Title** | "Dragon Warrior ROM Hacking: Graphics Editing with CHR Tools" |
| **Duration** | 12-15 minutes |
| **Difficulty** | Intermediate |
| **Prerequisites** | Completed Episode 1, CHR editing software |
| **Related Docs** | `docs/CHR_WORKFLOW.md`, `assets/graphics/` |

---

## Chapter Markers (YouTube Timestamps)

```
0:00 - Introduction
0:45 - Understanding NES Graphics
2:00 - The CHR-ROM Explained
3:30 - Extracting Graphics
4:30 - Using YY-CHR
6:00 - NES Palette Limitations
7:30 - Editing a Tile
9:00 - Reinserting Graphics
10:30 - Testing Changes
11:30 - Common Pitfalls
12:30 - Closing
```

---

## Full Script

### [0:00] Introduction (45 seconds)

**[VISUAL: Dragon Warrior sprites, transition to tile editor]**

**NARRATION:**
> "Welcome back to Dragon Warrior ROM Hacking! So far we've modified stats, but what if you want to change how things look?
>
> In this episode, we're diving into graphics editing. By the end, you'll know how to:
> - Extract graphics from the ROM
> - Edit tiles and sprites
> - Work within NES limitations
> - Reinsert your custom graphics
>
> This is where ROM hacking gets really creative!"

---

### [0:45] Understanding NES Graphics (1 minute 15 seconds)

**[VISUAL: Diagram of NES graphics system]**

**NARRATION:**
> "Before we edit anything, let's understand how NES graphics work.
>
> The NES uses tile-based graphics. Everything you see - characters, monsters, terrain - is made of 8x8 pixel tiles.
>
> These tiles are arranged in two tables:
> - **Background tiles** for maps, menus, and text
> - **Sprite tiles** for characters, NPCs, and animations
>
> Dragon Warrior uses both extensively. The hero, monsters, and NPCs are sprites. The overworld, towns, and dungeons use background tiles."

**[VISUAL: Show examples of each in-game]**

---

### [2:00] The CHR-ROM Explained (1 minute 30 seconds)

**[VISUAL: Hex view of ROM, CHR section highlighted]**

**NARRATION:**
> "All these tiles are stored in a section of the ROM called CHR-ROM, short for Character ROM.
>
> Dragon Warrior's CHR data starts at a specific offset in the ROM file. The project has already extracted these into PNG files in the `assets/graphics` folder.
>
> Let's look at what we have:"

**[VISUAL: File explorer showing assets/graphics folder]**

```
assets/graphics/
├── chr_bank_00.png    # Main sprite tiles
├── chr_bank_01.png    # More sprites
├── chr_bank_02.png    # Background tiles
└── ...
```

> "Each PNG represents a bank of tiles. The project converts these back into the binary CHR format during build."

---

### [3:30] Extracting Graphics (1 minute)

**[VISUAL: Running extraction command]**

**NARRATION:**
> "If you want fresh extractions or haven't extracted yet, run:"

```powershell
python tools/extract_chr_data.py
```

> "This pulls the CHR data from the ROM and saves it as PNG files.
>
> You can also extract to other formats, but PNG works great with most tile editors."

**[VISUAL: Show extraction output]**

---

### [4:30] Using YY-CHR (1 minute 30 seconds)

**[VISUAL: Opening YY-CHR, loading a PNG]**

**NARRATION:**
> "For editing, I recommend YY-CHR. It's a free tile editor designed specifically for retro console graphics.
>
> Download it, open it, and load one of the PNG files. You'll see all the tiles laid out in a grid."

**[VISUAL: YY-CHR interface tour]**

> "On the left, you have your palette selector. On the right, your drawing tools. The main area shows your tiles.
>
> Click on any tile to select it, then draw with the pencil tool. It's like a very simple paint program, but limited to 4 colors per tile."

**[VISUAL: Demonstrate selecting and drawing]**

---

### [6:00] NES Palette Limitations (1 minute 30 seconds)

**[VISUAL: Palette diagram, examples of color limitations]**

**NARRATION:**
> "Here's the tricky part - NES palette limitations.
>
> The NES can display 54 colors total, but with restrictions:
> - Each tile uses only 4 colors
> - One color is always transparent for sprites
> - The game defines which palette applies to which tiles
>
> In YY-CHR, stick to the indexed colors already in use. If you add new colors, they might not display correctly in-game."

**[VISUAL: Show a tile with correct vs incorrect colors]**

> "For Dragon Warrior specifically:
> - Sprites typically use palette 0 or 1
> - Overworld uses palette 2
> - Dungeons use palette 3
>
> Check `docs/CHR_WORKFLOW.md` for the exact palette definitions."

---

### [7:30] Editing a Tile (1 minute 30 seconds)

**[VISUAL: Step-by-step tile editing]**

**NARRATION:**
> "Let's edit something! I'm going to modify the hero's walking sprite.
>
> Find the hero tiles - they're in bank 00 around offset 0x20."

**[VISUAL: Navigate to hero tiles]**

> "I'll give our hero a cape by adding some pixels behind them."

**[VISUAL: Draw modifications]**

> "Remember:
> - Work within the 8x8 grid
> - Use only existing palette colors
> - The transparent color won't show in-game
> - Save your changes!"

**[VISUAL: Save the modified PNG]**

---

### [9:00] Reinserting Graphics (1 minute 30 seconds)

**[VISUAL: Build process with CHR conversion]**

**NARRATION:**
> "To get your changes into the ROM, save the PNG and run the build script."

```powershell
.\build.ps1
```

> "The build pipeline:
> 1. Converts PNG files back to binary CHR format
> 2. Includes the CHR data in the assembly
> 3. Produces the final ROM with your graphics
>
> If you've edited multiple files, they'll all be processed."

**[VISUAL: Build output highlighting CHR processing]**

> "For advanced users, you can also use the chr_tool.py directly:"

```powershell
python tools/chr_tool.py convert assets/graphics/chr_bank_00.png -o build/chr_bank_00.chr
```

---

### [10:30] Testing Changes (1 minute)

**[VISUAL: Emulator showing modified graphics]**

**NARRATION:**
> "Load the built ROM in your emulator, and... there's our caped hero!
>
> Move around, check different areas. Make sure your edits look correct everywhere the tile appears."

**[VISUAL: Walking around showing the modification]**

> "If something looks wrong, check:
> - Did you save the PNG?
> - Did the build complete successfully?
> - Did you edit the right tile?"

---

### [11:30] Common Pitfalls (1 minute)

**[VISUAL: Examples of common mistakes]**

**NARRATION:**
> "Watch out for these common issues:
>
> **Wrong palette:** Your tile looks garbled because it's using unexpected colors. Stick to the original palette.
>
> **Tile reuse:** Many tiles are used in multiple places. Edit carefully - changing one tile might affect several sprites.
>
> **Animation frames:** Characters have multiple animation frames. Don't forget to edit all of them or your sprite will flicker between old and new.
>
> **Overwriting important tiles:** Some tiles are used for UI elements. Don't accidentally edit menu borders!"

---

### [12:30] Closing (30-45 seconds)

**[VISUAL: End card with showcase of modifications]**

**NARRATION:**
> "You now know how to edit Dragon Warrior graphics! The same process works for:
> - Monster sprites
> - Terrain tiles
> - Menu graphics
> - Title screen
>
> In the next episode, we'll tackle dialog editing - changing what characters say.
>
> Show off your custom graphics in the comments! Like and subscribe for more tutorials."

---

## Video Description Template

```
🎮 Dragon Warrior ROM Hacking: Graphics Editing with CHR Tools

Learn how to edit graphics in Dragon Warrior! This tutorial covers extracting CHR data, using tile editors, understanding NES palette limitations, and reinserting your custom art.

📋 TIMESTAMPS:
0:00 - Introduction
0:45 - Understanding NES Graphics
2:00 - The CHR-ROM Explained
3:30 - Extracting Graphics
4:30 - Using YY-CHR
6:00 - NES Palette Limitations
7:30 - Editing a Tile
9:00 - Reinserting Graphics
10:30 - Testing Changes
11:30 - Common Pitfalls
12:30 - Closing

🔧 TOOLS:
• YY-CHR: https://www.romhacking.net/utilities/119/
• Tile Molester: https://www.romhacking.net/utilities/109/

📁 FILES INVOLVED:
• assets/graphics/*.png - Extracted tile graphics
• tools/extract_chr_data.py - Extraction script
• tools/chr_tool.py - Conversion utility
• docs/CHR_WORKFLOW.md - Detailed guide

⌨️ COMMANDS:
```powershell
# Extract CHR data
python tools/extract_chr_data.py

# Build with new graphics
.\build.ps1
```

📺 SERIES:
• Ep 1: Getting Started: [LINK]
• Ep 2: Monster Stats: [LINK]
• Ep 4: Dialog Editing: [COMING SOON]

#DragonWarrior #NES #ROMHacking #PixelArt #Tutorial
```

---

## Production Notes

### Visual Assets Needed
- [ ] NES graphics architecture diagram
- [ ] Palette limitation examples
- [ ] Before/after comparison shots
- [ ] YY-CHR interface annotations

### Example Modifications
Prepare these ahead of time:
- Hero with cape (demonstrated)
- Slime with hat (bonus)
- Custom tile example

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-02 | 1.0 | Initial script creation |

