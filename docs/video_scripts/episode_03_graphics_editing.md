# Episode 3: Graphics Editing - PNG Workflow

## Video Metadata

| Field | Value |
|-------|-------|
| **Title** | "Dragon Warrior ROM Hacking: Edit Graphics with PNG Files" |
| **Duration** | 12-15 minutes |
| **Difficulty** | Intermediate |
| **Prerequisites** | Completed Episode 1, image editor (any!) |
| **Related Docs** | `docs/CHR_WORKFLOW.md`, `assets/graphics/` |

---

## Chapter Markers (YouTube Timestamps)

```text
0:00 - Introduction
0:45 - Understanding NES Graphics
2:00 - The Asset Pipeline Approach
3:30 - Extracting to PNG
4:30 - Editing with Any Image Editor
6:00 - NES Palette Limitations
7:30 - Let's Edit a Monster!
9:00 - Rebuilding the ROM
10:30 - Testing Your Changes
11:30 - Common Pitfalls
12:30 - Closing
```

---

## Full Script

### [0:00] Introduction (45 seconds)

**[VISUAL: Dragon Warrior sprites showcased, transition to PNG files in VS Code]**

**NARRATION:**
> "What's up everyone! Welcome back to the Dragon Warrior ROM Hacking series. So far we've been tweaking numbers - stats, experience, damage. But what if you want to change how things *look*?
>
> In this episode, we're getting visual! By the end, you'll know how to:
>
> - Extract graphics from the ROM as PNG files
> - Edit them with your favorite image editor - Photoshop, GIMP, Paint.NET, whatever you like!
> - Understand NES palette limitations (it's weird, but manageable)
> - Rebuild your ROM with custom graphics
>
> This is where ROM hacking gets REALLY creative. Let's make some art!"

---

### [0:45] Understanding NES Graphics (1 minute 15 seconds)

**[VISUAL: Animated diagram of NES tile system]**

**NARRATION:**
> "Before we start editing, let's understand how NES graphics actually work. Trust me, this will save you headaches later!
>
> The NES uses something called *tile-based* graphics. Everything you see on screen - characters, monsters, terrain, even text - is made up of tiny 8x8 pixel tiles, kind of like a mosaic.
>
> These tiles live in two areas:
>
> - **Sprite tiles** - for things that move: the hero, monsters, NPCs
> - **Background tiles** - for the world: maps, buildings, menus
>
> Dragon Warrior uses both. The Dragonlord, Slimes, and our hero are sprites. The overworld, dungeons, and those fancy menus are backgrounds."

**[VISUAL: In-game examples highlighted with tile grid overlay]**

---

### [2:00] The Asset Pipeline Approach (1 minute 30 seconds)

**[VISUAL: Diagram showing ROM → PNG → Edit → ROM pipeline]**

**NARRATION:**
> "Here's the beautiful thing about this project - we don't touch the ROM directly for graphics!
>
> Our asset pipeline works like this:
>
> 1. Extract CHR data from ROM → PNG files
> 2. Edit the PNG files with any image editor you like
> 3. Build pipeline converts PNG back to CHR
> 4. Final ROM includes your custom graphics
>
> This means you can use Photoshop, GIMP, Paint.NET, Aseprite - literally any tool that saves PNG files. No specialized CHR editor required!
>
> The project has already extracted everything to `assets/graphics/`. Let's check it out."

**[VISUAL: File explorer showing assets/graphics folder with PNG files]**

```text
assets/graphics/
├── chr_bank_00.png    # Main sprite tiles (hero, slimes)
├── chr_bank_01.png    # More sprites (monsters)
├── chr_bank_02.png    # Background tiles (overworld)
├── palettes/          # Color palette definitions
└── ...
```

> "Each PNG is a bank of tiles laid out in a grid. Edit the PNG, save it, rebuild - that's it!"

---

### [3:30] Extracting to PNG (1 minute)

**[VISUAL: Running extraction command]**

**NARRATION:**
> "If you need fresh extractions or want to see how it works, run:"

```powershell
python tools/extract_chr_data.py
```

> "This pulls the CHR data from the ROM and saves it as PNG files. But honestly, the project already has these extracted for you!"

**[VISUAL: Show extraction output and the resulting PNG files]**

---

### [4:30] Editing with Any Image Editor (1 minute 30 seconds)

**[VISUAL: Opening Paint.NET with a CHR PNG file]**

**NARRATION:**
> "Here's the magic - you can use literally ANY image editor! Let me show you with Paint.NET, which is free and easy.
>
> Open one of the PNG files from `assets/graphics/`. You'll see all the tiles laid out in a grid format.
>
> The important thing is to save as **indexed PNG** or at least preserve the exact colors. Don't add anti-aliasing or smoothing!
>
> For those who want a specialized tool, YY-CHR is great for viewing tiles and understanding the layout. But for actual editing, your favorite image editor works perfectly.
>
> I personally like Aseprite for pixel art, but GIMP, Photoshop, even MS Paint works in a pinch!"

**[VISUAL: Show the same file open in different editors side by side]**

> "The key is: what you see in the PNG is what goes in the ROM. Edit it, save it, rebuild!"

---

### [6:00] NES Palette Limitations (1 minute 30 seconds)

**[VISUAL: Colorful palette diagram with NES limitations highlighted]**

**NARRATION:**
> "Alright, here's the one tricky part - NES palette limitations. Pay attention, this WILL save you headaches!
>
> The NES can display 54 colors total, but with restrictions:
>
> - Each tile uses only 4 colors
> - One color is always transparent for sprites
> - The game defines which palette applies to which tiles
>
> When editing in your image editor, just stick to the exact colors already in the PNG. Don't add new colors, don't use anti-aliasing, don't blend!"

**[VISUAL: Show a tile with correct vs incorrect colors - crisp vs blurry]**

> "For Dragon Warrior specifically, the palette assignments are:
>
> - Sprites typically use palette 0 or 1
> - Overworld uses palette 2
> - Dungeons use palette 3
>
> Check `docs/CHR_WORKFLOW.md` for the exact RGB values."

---

### [7:30] Let's Edit a Monster! (1 minute 30 seconds)

**[VISUAL: Step-by-step monster sprite editing in Paint.NET]**

**NARRATION:**
> "Okay, enough theory - let's actually make something! I'm going to edit the Slime sprite to make it look angrier.
>
> Open `chr_bank_01.png` in your image editor. The monster sprites are all here."

**[VISUAL: Navigate to Slime tiles, zoom in]**

> "There's our happy little Slime! Let's give it angry eyebrows and some teeth.
>
> Zoom way in - we're working at the pixel level here. Each pixel matters!
>
> I'm using the pencil tool, making sure I only use colors that are already in the image."

**[VISUAL: Draw angry eyebrows and fangs on the Slime]**

> "And... look at that angry boy! Remember to save - and make sure it's still a PNG with the same color format. Don't let your editor add compression artifacts!"

**[VISUAL: Save the modified PNG with correct settings]**

---

### [9:00] Rebuilding the ROM (1 minute 30 seconds)

**[VISUAL: Build process with CHR conversion highlighted]**

**NARRATION:**
> "Time to see our angry Slime in action! Save the PNG and run our build script."

```powershell
.\build.ps1
```

> "Watch the build output - you'll see it processing the graphics files:
>
> 1. Converts PNG files back to binary CHR format
> 2. Includes the CHR data in the assembly
> 3. Produces the final ROM with your custom graphics
>
> Every PNG you've modified gets automatically processed!"

**[VISUAL: Build output with "Processing chr_bank_01.png" highlighted]**

> "For those who want more control, there's also a standalone tool:"

```powershell
python tools/chr_tool.py convert assets/graphics/chr_bank_01.png -o build/chr_bank_01.chr
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
>
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
>
> - Monster sprites
> - Terrain tiles
> - Menu graphics
> - Title screen
>
> In the next episode, we'll tackle dialog editing - changing what characters say. The King will say whatever YOU want!
>
> Show off your custom graphics in the comments! I want to see your angry Slimes, caped heroes, whatever you create. Like and subscribe for more tutorials!"

---

## Video Description Template

```text
🎮 Dragon Warrior ROM Hacking: Edit Graphics with PNG Files!

Learn how to create custom graphics for Dragon Warrior! This tutorial covers the PNG workflow - extract, edit with ANY image editor, rebuild. No specialized tools required!

📋 TIMESTAMPS:
0:00 - Introduction
0:45 - Understanding NES Graphics
2:00 - The Asset Pipeline Approach
3:30 - Extracting to PNG
4:30 - Editing with Any Image Editor
6:00 - NES Palette Limitations
7:30 - Let's Edit a Monster!
9:00 - Rebuilding the ROM
10:30 - Testing Your Changes
11:30 - Common Pitfalls
12:30 - Closing

🔧 IMAGE EDITORS (any of these work!):
• Paint.NET (free): https://getpaint.net
• GIMP (free): https://gimp.org
• Aseprite (pixel art): https://aseprite.org
• YY-CHR (reference): https://www.romhacking.net/utilities/119/

📁 FILES INVOLVED:
• assets/graphics/*.png - Extracted tile graphics
• tools/extract_chr_data.py - Extraction script
• tools/chr_tool.py - Conversion utility
• docs/CHR_WORKFLOW.md - Detailed guide

⌨️ COMMANDS:
python tools/extract_chr_data.py   # Extract fresh PNGs
.\build.ps1                        # Build with your changes

📺 SERIES:
• Ep 1: Getting Started: [LINK]
• Ep 2: Monster Stats: [LINK]
• Ep 4: Dialog Editing: [COMING SOON]

Tags: DragonWarrior, NES, ROMHacking, PixelArt, Tutorial
```

---

## Production Notes

### Visual Assets Needed

- [ ] NES graphics architecture diagram
- [ ] Palette limitation examples
- [ ] Before/after comparison shots (original vs angry Slime)
- [ ] Image editor interface screenshots

### Example Modifications

Prepare these ahead of time:

- Angry Slime (demonstrated)
- Hero with cape (bonus)
- Custom monster recolor

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-02 | 1.0 | Initial script creation |
| 2025-12-02 | 1.1 | Rewrite for PNG workflow, add personality |

