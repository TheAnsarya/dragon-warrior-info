# Dragon Warrior ROM Optimization Guide

**Version:** 1.0  
**Created:** November 26, 2024  
**Purpose:** Comprehensive guide for optimizing Dragon Warrior ROM space, graphics, and data

---

## Table of Contents

1. [Overview](#overview)
2. [ROM Space Analysis](#rom-space-analysis)
3. [Graphics Optimization](#graphics-optimization)
4. [Text Compression](#text-compression)
5. [Data Packing Strategies](#data-packing-strategies)
6. [Audio Optimization](#audio-optimization)
7. [Code Optimization](#code-optimization)
8. [Advanced Techniques](#advanced-techniques)
9. [Optimization Checklist](#optimization-checklist)
10. [Case Studies](#case-studies)

---

## Overview

### Why Optimize?

Dragon Warrior (NES) has strict ROM size limitations:
- **PRG-ROM:** 128 KB (program code and data)
- **CHR-ROM:** 8 KB (graphics tiles)

When creating ROM hacks with new features, you must optimize existing data to make room.

### Optimization Philosophy

1. **Non-destructive first:** Prefer optimizations that preserve functionality
2. **Measure before optimizing:** Know what takes the most space
3. **Test thoroughly:** Optimization can introduce bugs
4. **Document changes:** Track what was optimized and why

### Expected Gains

| Technique | Typical Space Saved | Difficulty | Risk |
|-----------|-------------------|------------|------|
| Sprite sharing | 500-2000 bytes | Low | Low |
| Text compression | 2000-4000 bytes | Medium | Medium |
| Data deduplication | 200-1000 bytes | Low | Low |
| Code optimization | 500-2000 bytes | High | High |
| Audio trimming | 500-1500 bytes | Low | Low |
| Map compression | 1000-3000 bytes | Medium | Medium |

**Total potential:** 5,000-15,000 bytes (5-15 KB)

---

## ROM Space Analysis

### Step 1: Identify Space Usage

Use the ROM analysis tool to understand current usage:

```bash
python tools/analyze_rom_space.py roms/dragon_warrior.nes
```

**Expected Output:**
```
=== ROM Space Analysis ===

PRG-ROM (128 KB):
  Code:       45,000 bytes (34.9%)
  Data:       28,000 bytes (21.7%)
  Text:       16,000 bytes (12.4%)
  Tables:      8,000 bytes (6.2%)
  Maps:       12,000 bytes (9.3%)
  Free space:  3,072 bytes (2.4%)
  Padding:    19,000 bytes (14.7%)

CHR-ROM (8 KB):
  Sprites:     4,096 bytes (50.0%)
  Tiles:       3,072 bytes (37.5%)
  Unused:      1,024 bytes (12.5%)
```

### Step 2: Identify Optimization Targets

**Priority 1 - High Impact, Low Risk:**
- Unused CHR tiles
- Duplicate sprites
- Empty map space
- Redundant text strings

**Priority 2 - Medium Impact, Medium Risk:**
- Compressed text strings
- Shared sprite tiles
- Optimized data tables
- Consolidated maps

**Priority 3 - High Impact, High Risk:**
- Code refactoring
- Algorithm optimization
- Custom compression schemes

### Step 3: Free Space Map

Create a visual map of free space:

```bash
python tools/generate_free_space_map.py roms/dragon_warrior.nes
```

Output saved to `docs/free_space_map.txt`:
```
Address Range        Size    Type        Notes
================================================================
0x0000-0x000F       16 B    Header      iNES header
0x0010-0x4000    16368 B    PRG Bank 0  Program code
0x4000-0x8000    16384 B    PRG Bank 1  Data/text
0x8000-0xC000    16384 B    PRG Bank 2  More data
0xC000-0x10000   16384 B    PRG Bank 3  Fixed bank

Free spaces:
0x3F80-0x3FFF      128 B    FREE        *** Available ***
0x7800-0x7FFF     2048 B    FREE        *** Available ***
0xBF00-0xBFFF      256 B    FREE        *** Available ***
```

---

## Graphics Optimization

### Sprite Tile Sharing

**Problem:** Many sprites use duplicate tiles, wasting CHR space.

**Solution:** Identify and share common tiles between sprites.

#### Example: Enemy Sprites

Original (no sharing):
```
Slime:      16 tiles (128 bytes)
Red Slime:  16 tiles (128 bytes)  <-- 12 tiles identical to Slime!
Drakee:     16 tiles (128 bytes)
```

Optimized (with sharing):
```
Slime:      16 tiles (128 bytes)
Red Slime:   4 tiles (32 bytes)   <-- References 12 Slime tiles
Drakee:     16 tiles (128 bytes)

Savings: 96 bytes (75% reduction for Red Slime)
```

#### Implementation

**1. Analyze sprite similarities:**

```python
from tools.analyze_monster_sprites import analyze_sprite_sharing

# Find duplicate tiles
duplicates = analyze_sprite_sharing('roms/dragon_warrior.nes')

# Output:
# Slime <-> Red Slime: 12/16 tiles identical (75% match)
# Drakee <-> Magidrakee: 10/16 tiles identical (62.5% match)
# Ghost <-> Poltergeist: 14/16 tiles identical (87.5% match)
```

**2. Create shared tile mappings:**

```json
{
	"sprite_sharing": {
		"red_slime": {
			"base_sprite": "slime",
			"unique_tiles": [3, 7, 11, 15],
			"palette_swap": true,
			"savings": 96
		},
		"magidrakee": {
			"base_sprite": "drakee",
			"unique_tiles": [0, 4, 8, 12],
			"palette_swap": true,
			"savings": 96
		}
	}
}
```

**3. Modify CHR-ROM references:**

Update sprite rendering code to use shared tiles:

```asm
; Original code - loads full 16 tiles for Red Slime
LoadRedSlime:
	LDA #$10          ; Tile offset 0x10
	STA SpriteTile
	; ... (16 tile loads)

; Optimized code - loads Slime base + Red Slime unique
LoadRedSlimeOptimized:
	LDA #$00          ; Load Slime base tiles (0x00-0x0F)
	STA SpriteTile
	JSR LoadSharedSprite
	LDA #$70          ; Load Red Slime unique tiles (0x70-0x73)
	STA SpriteTile+3
	; ... (only 4 tile loads)
```

**4. Reclaim freed space:**

After removing duplicate tiles, mark freed CHR space:

```
Original CHR layout:
0x0000-0x00FF: Slime (16 tiles)
0x0100-0x01FF: Red Slime (16 tiles) <-- CAN REMOVE 12 TILES
0x0200-0x02FF: Drakee (16 tiles)

Optimized CHR layout:
0x0000-0x00FF: Slime (16 tiles)
0x0100-0x013F: Red Slime unique (4 tiles)
0x0140-0x01FF: FREE SPACE (12 tiles = 96 bytes)
0x0200-0x02FF: Drakee (16 tiles)
```

#### Automation Tool

```bash
# Analyze all sprites for sharing opportunities
python tools/optimize_chr_tiles.py roms/dragon_warrior.nes --analyze

# Apply optimizations automatically
python tools/optimize_chr_tiles.py roms/dragon_warrior.nes --optimize --output optimized.nes

# Expected output:
# Analyzing 39 monster sprites...
# Found 156 duplicate tiles
# Potential savings: 1,248 bytes (15.2% of CHR-ROM)
# Optimizing...
# Created sprite sharing map: 18 sprites optimized
# Actual savings: 1,152 bytes (14.1% of CHR-ROM)
# Freed CHR space: 0x0500-0x09FF (1,152 bytes)
```

### Palette Optimization

**Problem:** Limited palette entries, but many similar colors.

**Solution:** Consolidate similar colors, use palette swapping.

#### NES Palette Constraints

- 4 palettes available
- 4 colors per palette (1 transparent + 3 colors)
- Total: 16 colors max on screen

#### Strategy 1: Color Consolidation

Find near-identical colors and merge:

```python
from tools.palette_analyzer import analyze_palette_usage

results = analyze_palette_usage('roms/dragon_warrior.nes')

# Output:
# Color #0A (light blue) used in 12 sprites
# Color #0B (slightly lighter blue) used in 3 sprites
# ^ These could be merged! Savings: 1 palette slot
```

#### Strategy 2: Dynamic Palette Swapping

Use code to swap palettes for different contexts:

```asm
; Load different palette for day vs night
CheckTimeOfDay:
	LDA TimeOfDay
	CMP #$00          ; Day?
	BEQ LoadDayPalette
	JMP LoadNightPalette

LoadDayPalette:
	LDA #$21          ; Bright colors
	STA Palette0
	RTS

LoadNightPalette:
	LDA #$01          ; Dark colors
	STA Palette0
	RTS
```

### Tile Deduplication

**Problem:** Background tiles (grass, walls, etc.) may have duplicates.

**Solution:** Find and remove duplicate tiles.

```bash
python tools/deduplicate_tiles.py roms/dragon_warrior.nes

# Output:
# Analyzing 256 background tiles...
# Found 23 duplicate tiles:
#   Tile 0x45 = Tile 0x12 (grass)
#   Tile 0x46 = Tile 0x13 (grass variation)
#   Tile 0x78 = Tile 0x34 (brick wall)
# ...
# Potential savings: 184 bytes (23 tiles)
# 
# Updating references in map data...
# Updated 456 tile references
# 
# Savings: 184 bytes of CHR-ROM
```

---

## Text Compression

### Compression Techniques

Dragon Warrior uses simple text encoding. Several compression methods can save space:

#### Technique 1: Dictionary Compression (DTE)

**Concept:** Replace common 2-byte sequences with single-byte tokens.

**Example:**

Original text (uncompressed):
```
"THE HERO ENTERED THE CASTLE AND SPOKE TO THE KING."
```

Analysis:
- "THE" appears 3 times (6 bytes)
- " TO" appears 1 time (3 bytes)

Compressed with dictionary:
```
Dictionary:
  0xF0 = "THE"
  0xF1 = " TO"

Compressed:
"<F0> HERO ENTERED <F0> CASTLE AND SPOKE<F1> <F0> KING."

Original: 50 bytes
Compressed: 44 bytes
Savings: 6 bytes (12%)
```

#### Implementation

**1. Build frequency table:**

```python
from tools.analyze_text_frequency import build_frequency_table

freq_table = build_frequency_table('roms/dragon_warrior.nes')

# Output top 20 bigrams:
# "TH" - 456 occurrences (912 bytes)
# "HE" - 398 occurrences (796 bytes)
# "AN" - 234 occurrences (468 bytes)
# " T" - 189 occurrences (378 bytes)
# ...
```

**2. Create compression dictionary:**

```python
# Select top N bigrams for dictionary
dictionary = {
	0xF0: "TH",  # Most frequent
	0xF1: "HE",
	0xF2: "AN",
	0xF3: " T",
	0xF4: "IN",
	0xF5: "ER",
	0xF6: "OU",
	0xF7: "RE",
	# ... up to 16 entries (0xF0-0xFF)
}

# Estimated savings:
# 456 * 1 = 456 bytes (TH)
# 398 * 1 = 398 bytes (HE)
# ...
# Total: ~2,500 bytes (40% text compression)
```

**3. Modify text decoder:**

Original decoder:
```asm
TextDecoder:
	LDA (TextPtr), Y  ; Load character byte
	CMP #$00          ; End of string?
	BEQ TextDone
	JSR PrintChar     ; Print character
	INY
	JMP TextDecoder

TextDone:
	RTS
```

Enhanced decoder with DTE:
```asm
TextDecoderDTE:
	LDA (TextPtr), Y  ; Load byte
	CMP #$00          ; End?
	BEQ TextDone
	CMP #$F0          ; Dictionary token?
	BCS ExpandToken   ; Yes - expand it
	JSR PrintChar     ; No - print normal
	INY
	JMP TextDecoderDTE

ExpandToken:
	SEC
	SBC #$F0          ; Get dictionary index
	ASL A             ; * 2 (2 bytes per entry)
	TAX
	LDA Dictionary, X ; Load first char
	JSR PrintChar
	LDA Dictionary+1, X ; Load second char
	JSR PrintChar
	INY
	JMP TextDecoderDTE

Dictionary:
	.byte "TH"        ; 0xF0
	.byte "HE"        ; 0xF1
	.byte "AN"        ; 0xF2
	; ... etc
```

**4. Compress all text:**

```bash
python tools/compress_text.py roms/dragon_warrior.nes --dictionary dte_dict.json --output compressed.nes

# Output:
# Compressing 487 text strings...
# 
# Before: 16,384 bytes
# After:  10,245 bytes
# Savings: 6,139 bytes (37.5% reduction)
# 
# Dictionary: 16 entries (32 bytes overhead)
# Decoder: 45 bytes code overhead
# 
# Net savings: 6,062 bytes
```

#### Technique 2: Run-Length Encoding (RLE)

**Use case:** Repeated characters (spaces, dots, etc.)

Example:
```
Original: "................" (16 bytes)
RLE:      <0xFF><16><'.'>    (3 bytes)
Savings:  13 bytes (81% reduction)
```

**Best for:** Dialog boxes with padding, decorative text patterns.

#### Technique 3: Huffman Coding

**Use case:** Variable-length encoding based on character frequency.

**Pros:** Optimal compression for given frequency distribution  
**Cons:** Complex decoder, requires lookup tables

**Expected savings:** 35-45% text compression

**Recommendation:** Use for very large ROM hacks; overkill for small modifications.

---

## Data Packing Strategies

### Bit-Packing

**Problem:** Many data values use only part of a byte.

**Example: Monster flags**

Original (1 byte per flag):
```c
struct Monster {
	uint8_t can_sleep;      // 0 or 1 (wastes 7 bits)
	uint8_t can_stopspell;  // 0 or 1 (wastes 7 bits)
	uint8_t can_hurt;       // 0 or 1 (wastes 7 bits)
	uint8_t flies;          // 0 or 1 (wastes 7 bits)
};
// Total: 4 bytes per monster
```

Optimized (bit-packed):
```c
struct Monster {
	uint8_t flags;  // Bit 0: can_sleep
	                // Bit 1: can_stopspell
	                // Bit 2: can_hurt
	                // Bit 3: flies
	                // Bits 4-7: unused
};
// Total: 1 byte per monster
// Savings: 3 bytes per monster * 39 monsters = 117 bytes
```

#### Implementation

**Encoder:**
```python
def pack_monster_flags(can_sleep, can_stopspell, can_hurt, flies):
	flags = 0
	if can_sleep: flags |= 0x01
	if can_stopspell: flags |= 0x02
	if can_hurt: flags |= 0x04
	if flies: flags |= 0x08
	return flags
```

**Decoder (6502 ASM):**
```asm
; Check if monster can be put to sleep
CheckCanSleep:
	LDA MonsterFlags  ; Load flags byte
	AND #$01          ; Mask bit 0
	BEQ CannotSleep   ; If 0, cannot sleep
	; Can sleep - proceed
	...

CannotSleep:
	; Cannot sleep - show message
	RTS
```

### Table Compression

**Problem:** Large lookup tables with patterns.

**Example: XP table (levels 1-30)**

Original (2 bytes per level):
```
Level  1:     0 XP (2 bytes)
Level  2:     7 XP (2 bytes)
Level  3:    23 XP (2 bytes)
...
Level 30: 65535 XP (2 bytes)

Total: 60 bytes
```

**Pattern:** XP increases exponentially (roughly 1.5x per level)

Optimized (formula-based):
```asm
; XP_Required = Base * (Level ^ 1.5)
CalculateXPRequired:
	LDA Level
	JSR Power_1_5     ; Custom power function
	STA Temp
	LDA #BaseXP       ; Base = 7
	JSR Multiply
	; Result in Accumulator
	RTS

; Code size: ~30 bytes
; Savings: 60 - 30 = 30 bytes
```

**Alternative:** Delta encoding (store differences instead of absolute values)

```
Level  1:  0    (store: 0)
Level  2:  7    (store: +7)
Level  3:  23   (store: +16)
Level  4:  47   (store: +24)
...

All deltas < 256, so 1 byte per level instead of 2
Savings: 30 bytes (50% reduction)
```

### Map Compression

**Problem:** Maps contain many repeated tiles (walls, floors, etc.)

**Solution:** Run-length encoding for map data.

Original map (uncompressed):
```
Map: 32x32 tiles = 1,024 bytes

Example row:
[Wall][Wall][Wall][Wall][Wall][Floor][Floor][Floor]...
```

Compressed map (RLE):
```
[5][Wall][3][Floor]...

Format: <count><tile_id>
Size: ~400 bytes (60% reduction)
```

**Implementation:**

```python
def compress_map_rle(map_data):
	compressed = []
	i = 0
	while i < len(map_data):
		tile = map_data[i]
		count = 1
		
		# Count consecutive identical tiles
		while i + count < len(map_data) and map_data[i + count] == tile and count < 255:
			count += 1
		
		compressed.append(count)
		compressed.append(tile)
		i += count
	
	return compressed

# Usage
original_map = load_map('maps/tantegel_castle.bin')  # 1024 bytes
compressed_map = compress_map_rle(original_map)       # 412 bytes
savings = len(original_map) - len(compressed_map)     # 612 bytes
```

**Decompression (6502 ASM):**

```asm
DecompressMap:
	LDY #$00          ; Compressed data index
	LDX #$00          ; Decompressed data index

DecompressLoop:
	LDA (CompPtr), Y  ; Load count
	STA Count
	INY
	LDA (CompPtr), Y  ; Load tile ID
	STA Tile
	INY

WriteLoop:
	LDA Tile
	STA MapBuffer, X
	INX
	DEC Count
	BNE WriteLoop
	
	CPX #MapSize      ; Done?
	BNE DecompressLoop
	RTS
```

---

## Audio Optimization

### Music Track Trimming

**Problem:** Some music tracks are rarely heard or too long.

**Solution:** Trim or remove underused tracks.

#### Identify Underused Tracks

```python
from tools.music_editor import analyze_track_usage

usage = analyze_track_usage('roms/dragon_warrior.nes')

# Output:
# Track 01 (Title): 245 bytes, Usage: High (always played)
# Track 02 (Overworld): 512 bytes, Usage: High (constant)
# Track 03 (Battle): 189 bytes, Usage: High (frequent)
# Track 04 (Castle): 234 bytes, Usage: Medium
# Track 05 (Town): 167 bytes, Usage: Medium
# Track 06 (Dungeon): 298 bytes, Usage: Medium
# Track 07 (Victory): 78 bytes, Usage: High
# Track 08 (Game Over): 45 bytes, Usage: Low
# Track 09 (Ending): 678 bytes, Usage: Low (only at game end)
# 
# Optimization candidates:
#   - Track 09 (Ending): 678 bytes, rarely heard
#   - Track 08 (Game Over): Could be shortened
```

#### Optimization Strategies

**Strategy 1: Shorten long tracks**

Ending theme: 678 bytes → 400 bytes (-41%)
- Remove repeated sections
- Shorten intro/outro
- Simplify chord progressions

**Strategy 2: Share instrument data**

Many tracks use similar instruments. Create shared instrument bank:

```
Original:
  Track 01: Square1, Square2, Triangle, Noise (instruments defined in track)
  Track 02: Square1, Square2, Triangle, Noise (duplicate definitions!)
  ...

Optimized:
  Shared Instrument Bank: Square1, Square2, Triangle, Noise (64 bytes)
  Track 01: Reference bank (2 bytes)
  Track 02: Reference bank (2 bytes)
  ...

Savings: ~300 bytes
```

**Strategy 3: Lower music quality slightly**

- Reduce tempo (fewer note changes)
- Simplify harmony (use fewer channels)
- Use shorter note durations

### Sound Effect Optimization

**Problem:** Many sound effects use similar waveforms.

**Solution:** Create parametric sound effect system.

Original (hardcoded effects):
```
SoundEffect_Sword:     45 bytes
SoundEffect_Magic:     52 bytes
SoundEffect_Damage:    38 bytes
SoundEffect_Door:      29 bytes
...
Total: 420 bytes
```

Optimized (parametric):
```asm
; Generic sound effect player
PlaySoundEffect:
	LDA EffectID
	ASL A
	ASL A
	TAX
	LDA EffectTable, X    ; Frequency
	STA Freq
	LDA EffectTable+1, X  ; Duration
	STA Duration
	LDA EffectTable+2, X  ; Volume decay
	STA Decay
	LDA EffectTable+3, X  ; Channel
	STA Channel
	JSR PlayGenericEffect
	RTS

EffectTable:
	; Freq, Dur, Decay, Channel
	.byte $C0, $10, $02, $00  ; Sword
	.byte $80, $18, $03, $01  ; Magic
	.byte $A0, $08, $04, $00  ; Damage
	...

PlayGenericEffect: ; 60 bytes of code

Total: 60 bytes code + (4 * 15 effects) = 120 bytes
Savings: 420 - 120 = 300 bytes (71% reduction)
```

---

## Code Optimization

### Assembly Optimization

**Technique 1: Use zero-page addressing**

Zero-page (0x00-0xFF) access is faster and 1 byte smaller:

```asm
; Slow (3 bytes, 4 cycles)
LDA $0400

; Fast (2 bytes, 3 cycles)
LDA $40  ; Same location if in zero-page
```

**Technique 2: Inline small subroutines**

For 2-3 byte subroutines called once:

```asm
; Before (6 bytes total, 12 cycles)
JSR SmallRoutine  ; 3 bytes, 6 cycles
...
SmallRoutine:
	LDA #$00        ; 2 bytes
	STA $40         ; 2 bytes
	RTS             ; 1 byte, 6 cycles

; After (4 bytes, 5 cycles)
LDA #$00            ; 2 bytes, 2 cycles
STA $40             ; 2 bytes, 3 cycles

; Savings: 2 bytes, 7 cycles
```

**Technique 3: Use flags efficiently**

```asm
; Before (7 bytes)
LDA Flag
CMP #$00
BEQ DoSomething
JMP SkipIt
DoSomething:
...
SkipIt:

; After (4 bytes)
LDA Flag
BNE SkipIt
DoSomething:
...
SkipIt:

; Savings: 3 bytes
```

**Technique 4: Table-driven code**

Replace branching code with table lookups:

```asm
; Before (36 bytes)
CheckLevel:
	LDA Level
	CMP #$01
	BEQ Level1
	CMP #$02
	BEQ Level2
	CMP #$03
	BEQ Level3
	; ... etc

; After (20 bytes)
CheckLevel:
	LDA Level
	ASL A          ; * 2 (2 bytes per pointer)
	TAX
	LDA JumpTable+1, X
	PHA
	LDA JumpTable, X
	PHA
	RTS            ; Jump via RTS

JumpTable:
	.word Level1-1
	.word Level2-1
	.word Level3-1
	; ... etc

; Savings: 16 bytes (44% reduction)
```

### Removing Dead Code

**Problem:** Development code, debug routines, or unused features waste space.

**Solution:** Identify and remove dead code.

```bash
# Analyze ROM for unreferenced code
python tools/find_dead_code.py roms/dragon_warrior.nes

# Output:
# Analyzing call graph...
# 
# Dead code found (unreferenced subroutines):
#   0x8450-0x8478: DebugPrintHP (40 bytes)
#   0x9120-0x9145: UnusedBattleRoutine (37 bytes)
#   0xA800-0xA8FF: TestingCode (256 bytes)
# 
# Total dead code: 333 bytes
# 
# Safe to remove? (Y/N)
```

**Caution:** Some code may be referenced indirectly (via function pointers, dynamic jumps). Always test after removing!

---

## Advanced Techniques

### Bank Switching Optimization

For larger ROM hacks using bank switching (PRG-ROM > 32 KB):

**Problem:** Bank switch overhead.

**Solution:** Group related code in same bank to minimize switches.

```asm
; Poor organization (many bank switches)
Bank 0:
	BattleInit
	BattleUpdate
	ItemMenuInit

Bank 1:
	BattleDamageCalc  ; Called from BattleUpdate - bank switch!
	ItemMenuUpdate    ; Called from ItemMenuInit - bank switch!

; Optimized organization (fewer switches)
Bank 0:
	BattleInit
	BattleUpdate
	BattleDamageCalc  ; Grouped with BattleUpdate

Bank 1:
	ItemMenuInit
	ItemMenuUpdate    ; Grouped with ItemMenuInit
```

### Shared String Table

**Problem:** Repeated strings across different dialogs.

**Solution:** Create shared string table with pointers.

```
Original:
  Dialog1: "The hero opens the door." (24 bytes)
  Dialog2: "The door is locked." (19 bytes)
  Dialog3: "A door appears." (15 bytes)
  Total: 58 bytes

Optimized:
  StringTable:
    "The ", "hero ", "opens ", "the ", "door", " is locked", " appears"
  
  Dialog1: [ptr:The][ptr:hero][ptr:opens][ptr:the][ptr:door][ptr:.] (12 bytes)
  Dialog2: [ptr:The][ptr:door][ptr: is locked][ptr:.] (8 bytes)
  Dialog3: [ptr:A ][ptr:door][ptr: appears][ptr:.] (8 bytes)
  
  Total: 28 bytes dialog + 45 bytes table = 73 bytes
  
  Wait, that's worse! Need more reuse...
  
  With 50+ dialogs reusing strings:
  Total: 600 bytes vs 1,200 bytes = 50% savings
```

**Lesson:** Only worthwhile with many dialogs sharing strings.

### Procedural Generation

**Problem:** Large, repetitive data (e.g., monster stat scaling).

**Solution:** Generate data procedurally from formulas.

```python
# Original: Store all 39 monster HP values (78 bytes)
monster_hp = [2, 3, 6, 8, 12, 15, 20, ...]

# Optimized: Generate from formula
def calculate_hp(monster_id):
	base_hp = 2
	scaling = 1.4
	return int(base_hp * (scaling ** monster_id))

# Code size: ~40 bytes (50% savings)
```

**Best for:** Randomizers, procedural content, difficulty scaling.

---

## Optimization Checklist

### Pre-Optimization

- [ ] Analyze ROM space usage
- [ ] Identify largest data sections
- [ ] Create backup of ROM
- [ ] Document current functionality
- [ ] Set up automated testing

### Graphics Optimization

- [ ] Remove duplicate CHR tiles
- [ ] Implement sprite tile sharing
- [ ] Consolidate palettes
- [ ] Compress unused graphics
- [ ] Verify visual appearance unchanged

### Text Optimization

- [ ] Analyze character frequency
- [ ] Create DTE dictionary
- [ ] Implement compressed text decoder
- [ ] Compress all text strings
- [ ] Test all dialogs display correctly

### Data Optimization

- [ ] Bit-pack boolean flags
- [ ] Compress lookup tables
- [ ] Use delta encoding for sequences
- [ ] Share common data structures
- [ ] Validate data integrity

### Audio Optimization

- [ ] Trim rarely-heard tracks
- [ ] Share instrument definitions
- [ ] Optimize sound effects
- [ ] Reduce music quality if needed
- [ ] Test all audio playback

### Code Optimization

- [ ] Remove dead code
- [ ] Inline small subroutines
- [ ] Use table-driven logic
- [ ] Optimize assembly routines
- [ ] Test all game functionality

### Post-Optimization

- [ ] Measure total space saved
- [ ] Run full playthrough test
- [ ] Check for visual glitches
- [ ] Verify audio quality
- [ ] Update documentation

---

## Case Studies

### Case Study 1: Sprite Sharing for Enemy Variants

**Goal:** Add 10 new enemy variants without expanding CHR-ROM.

**Problem:** CHR-ROM full (8 KB), no room for new sprites.

**Solution:** Implement sprite sharing for color variants.

**Steps:**

1. **Analyze existing sprites:** Found 12 enemies that are just palette swaps (Slime/Red Slime, Drakee/Magidrakee, etc.)

2. **Calculate savings:** 12 enemies * 12 shared tiles/enemy * 8 bytes/tile = 1,152 bytes freed

3. **Implement sharing system:** Modified sprite loader to reference shared base tiles

4. **Add new variants:** Used freed space for 10 new enemy variants (640 bytes)

**Result:**
- Space saved: 1,152 bytes
- Space used: 640 bytes
- Net savings: 512 bytes
- New content: 10 new enemies

**Lessons:**
- Sprite sharing is powerful for variants
- Always verify visual correctness
- Document shared sprite mappings

### Case Study 2: Dialog Compression

**Goal:** Add 50% more dialog without expanding ROM.

**Problem:** Text section full (16 KB), need space for new quest dialogs.

**Solution:** Implement DTE compression.

**Steps:**

1. **Frequency analysis:** Analyzed all 487 text strings, built bigram frequency table

2. **Dictionary creation:** Selected top 16 bigrams (TH, HE, AN, etc.)

3. **Compression:** Rewrote all text with DTE encoding

4. **Decoder modification:** Added 45-byte DTE decoder routine

**Result:**
- Original text: 16,384 bytes
- Compressed text: 10,245 bytes
- Decoder overhead: 77 bytes (dictionary + code)
- Net savings: 6,062 bytes (37% reduction)
- New dialog added: 4,500 bytes
- Remaining free: 1,562 bytes

**Lessons:**
- Text compression gives massive savings
- DTE is simple and effective
- Test decoder thoroughly
- Leave buffer space for future additions

### Case Study 3: Map Compression

**Goal:** Add 5 new dungeon floors.

**Problem:** Map data full, no space for new maps.

**Solution:** RLE compression for map tiles.

**Steps:**

1. **Analyze maps:** Found high redundancy (walls, floors repeat)

2. **Implement RLE:** Created map compression/decompression routines

3. **Compress existing maps:** Applied RLE to all 20 existing maps

4. **Add new maps:** Used freed space for 5 new dungeons

**Result:**
- Original maps: 20 * 1,024 bytes = 20,480 bytes
- Compressed maps: 8,192 bytes (60% reduction)
- Decompression code: 128 bytes
- Net savings: 12,160 bytes
- New maps added: 5 * 410 bytes = 2,050 bytes
- Remaining free: 10,110 bytes

**Lessons:**
- RLE excellent for tile-based maps
- Decompression fast enough for NES
- Consider compression/decompression time
- Pre-decompress frequently accessed maps

### Case Study 4: Audio Trimming

**Goal:** Free space for new battle mechanics code.

**Problem:** Need 800 bytes for new code, ROM nearly full.

**Solution:** Optimize music tracks.

**Steps:**

1. **Identify targets:** Ending theme (678 bytes), Game Over (45 bytes)

2. **Shorten ending:** Removed repeated sections, simplified: 678 → 380 bytes (-298 bytes)

3. **Share instruments:** Created shared instrument bank: -320 bytes

4. **Optimize effects:** Parametric system: -180 bytes

**Result:**
- Total audio savings: 798 bytes
- New code added: 650 bytes
- Remaining free: 148 bytes

**Lessons:**
- Audio optimization often overlooked
- Music can be compressed significantly
- Balance quality vs space
- Ending sequences good candidates (rarely heard)

---

## Tools Summary

### Analysis Tools

```bash
# ROM space analysis
python tools/analyze_rom_space.py ROM_FILE

# Text frequency analysis
python tools/analyze_text_frequency.py ROM_FILE

# Sprite similarity analysis
python tools/analyze_monster_sprites.py ROM_FILE

# Palette usage analysis
python tools/palette_analyzer.py ROM_FILE

# Dead code detection
python tools/find_dead_code.py ROM_FILE
```

### Optimization Tools

```bash
# CHR tile optimization
python tools/optimize_chr_tiles.py ROM_FILE --output OUTPUT_FILE

# Text compression (DTE)
python tools/compress_text.py ROM_FILE --dictionary DICT_FILE --output OUTPUT_FILE

# Map compression (RLE)
python tools/compress_maps.py ROM_FILE --output OUTPUT_FILE

# Tile deduplication
python tools/deduplicate_tiles.py ROM_FILE --output OUTPUT_FILE

# Audio optimization
python tools/optimize_audio.py ROM_FILE --output OUTPUT_FILE
```

### Verification Tools

```bash
# Visual diff (compare before/after)
python tools/rom_diff.py ORIGINAL_ROM OPTIMIZED_ROM

# Playtest validation
python tools/rom_verifier.py OPTIMIZED_ROM

# Space report
python tools/generate_space_report.py OPTIMIZED_ROM
```

---

## Conclusion

ROM optimization is essential for expanding Dragon Warrior with new content. By applying the techniques in this guide, you can free 5-15 KB of space while maintaining game quality.

**Key Takeaways:**

1. **Measure first:** Use analysis tools to find optimization targets
2. **Start safe:** Begin with low-risk optimizations (sprite sharing, deduplication)
3. **Test thoroughly:** Every optimization can introduce bugs
4. **Document everything:** Track what was changed and why
5. **Incremental approach:** Optimize one system at a time
6. **Validate constantly:** Test after each change

**Recommended Optimization Order:**

1. Remove duplicate CHR tiles (low risk, medium gain)
2. Implement sprite sharing (low risk, high gain)
3. Compress text with DTE (medium risk, very high gain)
4. Compress maps with RLE (medium risk, high gain)
5. Optimize audio tracks (low risk, medium gain)
6. Remove dead code (medium risk, low gain)
7. Optimize assembly (high risk, medium gain)

**Final Advice:**

Don't optimize prematurely. First, implement your features unoptimized. Then, if you run out of space, apply optimizations systematically. Always keep backups and test thoroughly!

Happy ROM hacking! 🐉⚔️
