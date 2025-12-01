# Dragon Warrior Music & Sound Editing Guide

This guide covers music and sound effect editing for Dragon Warrior (NES).

## Table of Contents

1. [NES Audio Overview](#nes-audio-overview)
2. [Dragon Warrior Music System](#dragon-warrior-music-system)
3. [Using the Music Editor Tab](#using-the-music-editor-tab)
4. [Understanding Music Data](#understanding-music-data)
5. [Editing Music Tracks](#editing-music-tracks)
6. [Sound Effect Locations](#sound-effect-locations)
7. [Advanced Techniques](#advanced-techniques)

---

## NES Audio Overview

The NES Audio Processing Unit (APU) provides 5 audio channels:

### Channel Overview

| Channel | Type | Description | Primary Use |
|---------|------|-------------|-------------|
| Pulse 1 | Square Wave | Configurable duty cycle (12.5%, 25%, 50%, 75%) | Lead melody |
| Pulse 2 | Square Wave | Same as Pulse 1 | Harmony/countermelody |
| Triangle | Triangle Wave | Pure tone, no volume control | Bass lines |
| Noise | Pseudo-random | Configurable period | Drums/percussion |
| DMC | Delta Modulation | 1-bit sample playback | Sound effects (rarely used in DW) |

### Audio Registers

The NES APU uses memory-mapped registers at `$4000-$4017`:

| Address | Channel | Function |
|---------|---------|----------|
| `$4000-$4003` | Pulse 1 | Volume, sweep, timer, length |
| `$4004-$4007` | Pulse 2 | Volume, sweep, timer, length |
| `$4008-$400B` | Triangle | Linear counter, timer, length |
| `$400C-$400F` | Noise | Volume, period, length |
| `$4010-$4013` | DMC | Sample playback control |
| `$4015` | Control | Channel enable/status |

---

## Dragon Warrior Music System

Dragon Warrior uses a custom music engine that processes bytecode sequences to generate music.

### Music Data Format

Music data is stored as a sequence of bytes representing:
- **Notes** (values `$00-$47`) - Musical pitch
- **Durations** (values `$48-$7F`) - How long to play
- **Control codes** (values `$80-$FF`) - Loops, jumps, etc.

### Music Track Locations (PRG1)

| Track | ROM Offset | Description |
|-------|------------|-------------|
| Title Screen | `$0F010` | Main title music |
| Overworld | `$0E810` | World map theme |
| Castle | `$0E910` | Castle/town theme |
| Cave | `$0EA10` | Dungeon theme |
| Battle | `$0EB10` | Battle music |
| Victory | `$0EC10` | Victory fanfare |
| Death | `$0ED10` | Game over theme |
| Inn | `$0EE10` | Inn rest jingle |
| Level Up | `$0EF10` | Level up fanfare |

> **Note:** These offsets include the 16-byte iNES header. Subtract `$10` for headerless ROMs.

### Music Bytecode

```
Byte Range    Meaning
-----------   --------
$00-$0B       Octave 2 notes (C-B)
$0C-$17       Octave 3 notes (C-B)
$18-$23       Octave 4 notes (C-B)
$24-$2F       Octave 5 notes (C-B)
$30-$3B       Octave 6 notes (C-B)
$3C-$47       Octave 7 notes (C-B)
$48-$7F       Duration/length values
$80           Rest
$81           Loop start
$82           Loop end
$83-$FF       Control codes (tempo, volume, etc.)
```

---

## Using the Music Editor Tab

The Universal Editor includes a Music Editor Tab for viewing and basic editing.

### Getting Started

1. Open Universal Editor: `python tools/universal_editor.py`
2. Navigate to the **🎵 Music** tab
3. Select a track from the left panel

### Interface Overview

```
┌─────────────────────────────────────────────────────────┐
│ Music Tracks    │ Music Data                            │
│ ────────────    │ ──────────                            │
│ ◉ Title Screen  │ Track: Title Screen                   │
│   Overworld     │ Offset: 0x0000F010                    │
│   Castle        │                                        │
│   Cave          │ F010  3C 48 3D 48 3E 48 3F 48 ...     │
│   Battle        │ F020  40 48 41 48 42 48 43 48 ...     │
│   Victory       │                                        │
│   Death         │ ┌─────────────────────────────────┐   │
│   Inn           │ │ Note Visualization              │   │
│   Level Up      │ │ ■ Note  ■ Duration  ■ Control   │   │
│                 │ └─────────────────────────────────┘   │
│ Track Info:     │                                        │
│ Main title      │ [Refresh] [Export Notes]               │
│ music           │                                        │
└─────────────────────────────────────────────────────────┘
```

### Color Coding

The hex view uses color coding:
- **Green** (`#4ec9b0`) - Note values (`$00-$47`)
- **Orange** (`#ce9178`) - Duration values (`$48-$7F`)
- **Purple** (`#c586c0`) - Control codes (`$80-$FF`)

### Exporting Data

1. Select a track
2. Click **Export Notes**
3. Choose a filename
4. Save as `.txt` for analysis

---

## Understanding Music Data

### Reading Note Sequences

Here's how to interpret a music sequence:

```
Byte Sequence: 0C 48 0E 48 10 48 11 48 10 48 0E 48 0C 60
               │   │   │   │   │   │   │   │   │   │   │  │
               │   │   │   │   │   │   │   │   │   │   │  └─ Duration (longer)
               │   │   │   │   │   │   │   │   │   │   └──── Note C3
               │   │   │   │   │   │   │   │   │   └──────── Note D3
               │   │   │   │   │   │   │   │   └────────────   Duration
               │   │   │   │   │   │   │   └──────────────── Note E3
               │   │   │   │   │   │   └────────────────────   Duration
               │   │   │   │   │   └────────────────────────  Note F3
               └───┴───┴───┴───┴────────────────────────────  Continues...
```

This plays: C3-D3-E3-F3-E3-D3-C3 (held longer)

### Note Value Table

| Hex | Octave | Note | Hex | Octave | Note |
|-----|--------|------|-----|--------|------|
| $00 | 2 | C | $0C | 3 | C |
| $01 | 2 | C# | $0D | 3 | C# |
| $02 | 2 | D | $0E | 3 | D |
| $03 | 2 | D# | $0F | 3 | D# |
| $04 | 2 | E | $10 | 3 | E |
| $05 | 2 | F | $11 | 3 | F |
| $06 | 2 | F# | $12 | 3 | F# |
| $07 | 2 | G | $13 | 3 | G |
| $08 | 2 | G# | $14 | 3 | G# |
| $09 | 2 | A | $15 | 3 | A |
| $0A | 2 | A# | $16 | 3 | A# |
| $0B | 2 | B | $17 | 3 | B |

Pattern continues for octaves 4-7 (`$18-$47`).

---

## Editing Music Tracks

### Method 1: Hex Editor (Basic)

1. Open ROM in a hex editor
2. Navigate to track offset
3. Modify note/duration bytes
4. Save and test in emulator

### Method 2: Using Universal Editor

1. Open the Music tab
2. View track data
3. Export to analyze
4. Edit hex values in the hex viewer tab
5. Save ROM changes

### Common Modifications

#### Change Note Pitch
```
Original: 0C 48   (C3, standard duration)
Modified: 0E 48   (D3, same duration)
```

#### Change Note Duration
```
Original: 0C 48   (C3, standard duration)
Modified: 0C 60   (C3, longer duration)
```

#### Add a Rest
```
Insert:   80 48   (Rest, standard duration)
```

### Testing Changes

1. Save your modified ROM
2. Open in an NES emulator
3. Navigate to the area with that music
4. Listen for your changes

**Tip:** Use save states to quickly test music changes!

---

## Sound Effect Locations

Dragon Warrior sound effects are separate from music tracks.

### Common Sound Effects

| Effect | Approximate Location | Description |
|--------|---------------------|-------------|
| Menu select | Bank 3 | Cursor movement beep |
| Attack | Bank 3 | Weapon swing sound |
| Hit | Bank 3 | Enemy hit sound |
| Critical | Bank 3 | Critical hit sound |
| Magic cast | Bank 3 | Spell casting sound |
| Door | Bank 3 | Door opening sound |
| Stairs | Bank 3 | Stairs sound |
| Item get | Bank 3 | Item obtained jingle |

> **Note:** Sound effects are often inline with game code and harder to modify than music.

---

## Advanced Techniques

### Converting MIDI to Dragon Warrior Format

1. **Analyze the MIDI**
   - Note pitches and durations
   - Tempo markings

2. **Map to DW Format**
   - Convert note numbers to DW hex values
   - Convert durations to DW duration bytes

3. **Test Extensively**
   - Music engine has limits
   - Some note combinations may not work

### Using Famitracker

[Famitracker](http://famitracker.com/) can export music in various formats:

1. Create/edit music in Famitracker
2. Export as NSF
3. Analyze the NSF data
4. Adapt for Dragon Warrior's engine

### Music Driver Documentation

For deeper understanding:
- Study the disassembly in `source_files/`
- Look for music driver routines
- Trace how bytes are processed

---

## Resources

### Tools
- **Universal Editor** - Built-in music viewing
- **Hex Editor** - Direct byte editing
- **NES Emulator** - Testing changes
- **Famitracker** - NES music composition

### References
- [NESDev Wiki - APU](https://www.nesdev.org/wiki/APU)
- [Dragon Warrior Disassembly](source_files/)
- [NES Sound Format](https://www.nesdev.org/wiki/NSF)

### Community
- [Data Crystal](https://datacrystal.romhacking.net/wiki/Dragon_Warrior)
- [Romhacking.net](https://www.romhacking.net/)

---

## Tips & Warnings

### Do's
✅ Always backup your ROM before editing
✅ Test changes frequently
✅ Start with simple modifications
✅ Document your changes
✅ Use save states for quick testing

### Don'ts
❌ Don't modify without understanding the format
❌ Don't change loop structures without care
❌ Don't exceed track length limits
❌ Don't forget the 16-byte iNES header offset

---

## Troubleshooting

### Music Sounds Wrong
- Check note values are in valid range
- Verify duration bytes are correct
- Ensure control codes weren't accidentally modified

### Music Doesn't Play
- Track pointer may be corrupted
- Control code sequence may be broken
- Check for loop errors

### Game Crashes
- Music data may have overflowed into code
- Control codes may have invalid values
- Restore from backup and try smaller changes
