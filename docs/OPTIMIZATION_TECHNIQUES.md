# Advanced Optimization Techniques

**Expert-Level ROM Optimization for Dragon Warrior**

*Version 1.0 - November 2024*

---

## Table of Contents

1. [Introduction](#introduction)
2. [Space Analysis](#space-analysis)
3. [CHR-ROM Optimization](#chr-rom-optimization)
4. [PRG-ROM Optimization](#prg-rom-optimization)
5. [Text Compression](#text-compression)
6. [Map Data Compression](#map-data-compression)
7. [Code Optimization](#code-optimization)
8. [Advanced Techniques](#advanced-techniques)

---

## Introduction

Dragon Warrior (NES) has limited space:
- **PRG-ROM**: 32KB (program code + data)
- **CHR-ROM**: 8KB (graphics tiles)

This guide covers techniques to maximize use of this space for ROM hacks.

### Current Space Usage

```
PRG-ROM (32KB):
├── Program Code: ~25KB
├── Monster Data: 624 bytes (0x5C10-0x5E80)
├── Spell Data: 40 bytes (0x1D410-0x1D438)
├── Item Data: 256 bytes (0x1CF70-0x1D070)
├── Map Data: ~4KB (variable)
├── Text Data: ~2KB (dialog, names)
└── Unused: ~500 bytes (scattered)

CHR-ROM (8KB):
├── Used Tiles: 252 tiles (3,024 bytes)
├── Unused Tiles: 260 tiles (4,968 bytes)
└── Efficiency: 37% utilized
```

---

## Space Analysis

### Finding Unused Space

```python
#!/usr/bin/env python3
"""Find unused ROM regions"""

def find_unused_regions(rom_data, min_size=16):
    """
    Find regions filled with 0x00 or 0xFF
    
    Args:
        rom_data: ROM bytes
        min_size: Minimum region size to report
        
    Returns:
        List of (offset, size, fill_byte) tuples
    """
    regions = []
    i = 0
    
    while i < len(rom_data):
        fill_byte = rom_data[i]
        
        # Skip if not likely unused (0x00 or 0xFF)
        if fill_byte not in (0x00, 0xFF):
            i += 1
            continue
        
        # Count consecutive bytes
        start = i
        while i < len(rom_data) and rom_data[i] == fill_byte:
            i += 1
        
        size = i - start
        
        # Report if large enough
        if size >= min_size:
            regions.append((start, size, fill_byte))
    
    return regions


# Example usage
with open('roms/dragon_warrior.nes', 'rb') as f:
    rom = bytearray(f.read())

# Find unused regions
unused = find_unused_regions(rom[16:], min_size=32)  # Skip header

print("Unused ROM Regions:")
for offset, size, fill in unused:
    print(f"  0x{offset:05X}: {size} bytes (fill: 0x{fill:02X})")

total = sum(size for _, size, _ in unused)
print(f"\nTotal unused: {total} bytes ({total/1024:.2f} KB)")
```

**Expected Output**:
```
Unused ROM Regions:
  0x1F800: 128 bytes (fill: 0xFF)
  0x1FC00: 256 bytes (fill: 0xFF)
  ...

Total unused: 487 bytes (0.48 KB)
```

### Entropy Analysis

Identify compressible data:

```python
import math
from collections import Counter

def calculate_entropy(data):
    """
    Calculate Shannon entropy (0-8 bits)
    
    Low entropy = repetitive (compressible)
    High entropy = random (not compressible)
    """
    if not data:
        return 0
    
    # Count byte frequencies
    counts = Counter(data)
    length = len(data)
    
    # Calculate entropy
    entropy = 0
    for count in counts.values():
        probability = count / length
        if probability > 0:
            entropy -= probability * math.log2(probability)
    
    return entropy


# Analyze different data types
monster_data = rom[0x5C10:0x5E80]
spell_data = rom[0x1D410:0x1D438]
map_data = rom[0x1B3B0:0x1C000]  # Approximate

print("Entropy Analysis:")
print(f"Monster data: {calculate_entropy(monster_data):.3f} bits")
print(f"Spell data: {calculate_entropy(spell_data):.3f} bits")
print(f"Map data: {calculate_entropy(map_data):.3f} bits")
print("\nLow entropy (<4.0) = good compression candidate")
```

---

## CHR-ROM Optimization

### Duplicate Tile Detection

```python
def find_duplicate_tiles(chr_rom):
    """
    Find duplicate 8×8 tiles
    
    Args:
        chr_rom: CHR-ROM data (8192 bytes)
        
    Returns:
        Dict mapping tile_id → list of duplicate tile_ids
    """
    tile_size = 16  # 8×8 tile = 16 bytes
    num_tiles = len(chr_rom) // tile_size
    
    tiles = {}
    duplicates = {}
    
    for i in range(num_tiles):
        offset = i * tile_size
        tile_data = chr_rom[offset:offset + tile_size]
        tile_key = bytes(tile_data)
        
        if tile_key in tiles:
            # Duplicate found
            original = tiles[tile_key]
            if original not in duplicates:
                duplicates[original] = []
            duplicates[original].append(i)
        else:
            tiles[tile_key] = i
    
    return duplicates


# Find duplicates
chr_rom = rom[0x10010:0x12010]
dupes = find_duplicate_tiles(chr_rom)

print("Duplicate Tiles:")
for original, copies in dupes.items():
    print(f"Tile {original}: {len(copies)} duplicates")
    print(f"  Wasted space: {len(copies) * 16} bytes")

total_wasted = sum(len(copies) * 16 for copies in dupes.values())
print(f"\nTotal wasted: {total_wasted} bytes")
```

### Sprite Sharing Optimization

**Current State**:
```
39 monsters using 19 sprite definitions = 51% sharing efficiency
184 tiles saved through palette swapping
```

**Optimization Potential**:

1. **Identify similar monsters**:
   ```python
   # Find monsters that could share sprites
   similar_monsters = [
       ("Wolflord", "Druin"),      # Similar quadruped
       ("Scorpion", "Metal Scorpion"),  # Same base
       ("Skeleton", "Starwyvern"),  # Humanoid frame
   ]
   ```

2. **Create palette variants**:
   ```python
   def create_palette_variant(base_monster, new_name, palette_index):
       """Create color variant without using CHR space"""
       new_monster = base_monster.copy()
       new_monster['name'] = new_name
       new_monster['palette_index'] = palette_index
       new_monster['sprite_family'] = base_monster['sprite_family']
       return new_monster
   
   # Example: Blue Slime from base Slime
   blue_slime = create_palette_variant(
       base_monster=monsters[0],  # Slime
       new_name="Blue Slime",
       palette_index=2  # Use blue palette
   )
   ```

**Potential Savings**: 10-15 additional monsters using 0 bytes CHR

---

## PRG-ROM Optimization

### Table Compression

Compress lookup tables using delta encoding:

```python
def delta_encode(values):
    """
    Delta encode values
    
    Instead of: [10, 20, 35, 55, 80, 110]
    Store: [10, +10, +15, +20, +25, +30]
    
    Benefits: Smaller values, better compression
    """
    if not values:
        return []
    
    deltas = [values[0]]  # First value unchanged
    for i in range(1, len(values)):
        delta = values[i] - values[i-1]
        deltas.append(delta)
    
    return deltas


# Example: XP table
xp_values = [1, 2, 3, 6, 11, 22, 47, 100, 150, 255]

original_size = len(xp_values) * 2  # 16-bit values
deltas = delta_encode(xp_values)
delta_size = 2 + len(deltas)  # First value 16-bit, rest 8-bit

print(f"Original: {original_size} bytes")
print(f"Delta encoded: {delta_size} bytes")
print(f"Savings: {original_size - delta_size} bytes")
```

### Pointer Table Optimization

**Before**:
```
Monster pointers: 39 × 2 bytes = 78 bytes
Each pointer: 16-bit absolute address
```

**After** (8-bit offset table):
```
Base address: 2 bytes (0x5C10)
Offsets: 39 × 1 byte = 39 bytes
Each offset: 8-bit relative to base

Savings: 78 - 41 = 37 bytes
```

Implementation:
```assembly
; Before
MonsterPtrs:
    .word Monster00Data  ; 0x5C10
    .word Monster01Data  ; 0x5C20
    .word Monster02Data  ; 0x5C30
    ; ... (78 bytes total)

; After
MonsterBase:
    .word $5C10          ; Base address (2 bytes)
MonsterOffsets:
    .byte $00            ; Monster 0: +0 from base
    .byte $10            ; Monster 1: +16 from base
    .byte $20            ; Monster 2: +32 from base
    ; ... (39 bytes total)
```

---

## Text Compression

### Word Substitution Analysis

Current substitutions (0x80-0x8F):
```
0x80: SWORD (5 bytes → 1 byte, 4 saved × count)
0x81: STAFF (5 bytes → 1 byte)
0x82: SHIELD (6 bytes → 1 byte)
...
```

**Optimization Strategy**:

1. **Analyze frequency**:
   ```powershell
   python tools/analyze_text_frequency.py
   ```

   Output:
   ```
   Top Compression Candidates:
   1. TANTEGEL (42 occurrences, 7 bytes) → saves 252 bytes
   2. PRINCESS (38 occurrences, 8 bytes) → saves 228 bytes
   3. ERDRICK (35 occurrences, 7 bytes) → saves 175 bytes
   4. DRAGONLORD (28 occurrences, 10 bytes) → saves 224 bytes
   ```

2. **Assign new codes** (0x90-0x9F):
   ```python
   NEW_SUBSTITUTIONS = {
       0x90: "TANTEGEL",
       0x91: "PRINCESS",
       0x92: "ERDRICK",
       0x93: "DRAGONLORD",
       0x94: "GWAELIN",
       0x95: "CHARLOCK",
       0x96: "RADIANT",
       0x97: "CURSED",
   }
   ```

3. **Implement decoder**:
   ```assembly
   TextDecoder:
       LDA TextData,X
       CMP #$80          ; Check if substitution
       BCC NormalChar
       CMP #$A0          ; Check if in range $80-$9F
       BCS NormalChar
       
       ; Load substitution pointer
       SEC
       SBC #$80
       ASL A             ; × 2 for 16-bit pointer
       TAX
       LDA SubstPtrs,X
       ; ... decode word ...
   ```

**Total Potential Savings**: ~1,270 bytes

### Huffman Encoding

For extreme compression:

```python
import heapq
from collections import Counter

class HuffmanNode:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None
    
    def __lt__(self, other):
        return self.freq < other.freq


def build_huffman_tree(text):
    """Build Huffman tree from text"""
    # Count frequencies
    freq = Counter(text)
    
    # Create heap
    heap = [HuffmanNode(char, f) for char, f in freq.items()]
    heapq.heapify(heap)
    
    # Build tree
    while len(heap) > 1:
        left = heapq.heappop(heap)
        right = heapq.heappop(heap)
        
        parent = HuffmanNode(None, left.freq + right.freq)
        parent.left = left
        parent.right = right
        
        heapq.heappush(heap, parent)
    
    return heap[0]


def generate_codes(node, prefix="", codes=None):
    """Generate Huffman codes"""
    if codes is None:
        codes = {}
    
    if node.char is not None:
        codes[node.char] = prefix
    else:
        generate_codes(node.left, prefix + "0", codes)
        generate_codes(node.right, prefix + "1", codes)
    
    return codes


# Example
text = "THE PRINCESS IS IN TANTEGEL CASTLE"
tree = build_huffman_tree(text)
codes = generate_codes(tree)

print("Huffman Codes:")
for char, code in sorted(codes.items()):
    print(f"  '{char}': {code}")

# Calculate compression
original_bits = len(text) * 8
compressed_bits = sum(len(codes[c]) for c in text)

print(f"\nOriginal: {original_bits} bits")
print(f"Compressed: {compressed_bits} bits")
print(f"Ratio: {compressed_bits / original_bits:.2%}")
```

**Typical Results**: 40-60% compression for English text

---

## Map Data Compression

### Run-Length Encoding (RLE)

```python
def rle_compress(data):
    """
    RLE compression (3-byte format)
    
    Format: [marker][count][value]
    Marker: 0xFE (not used in normal map data)
    Count: 1-255
    Value: Tile ID
    """
    compressed = []
    i = 0
    
    while i < len(data):
        # Count consecutive bytes
        count = 1
        while (i + count < len(data) and 
               data[i] == data[i + count] and 
               count < 255):
            count += 1
        
        if count >= 4:  # Worth compressing
            compressed.extend([0xFE, count, data[i]])
        else:
            # Raw bytes
            compressed.extend(data[i:i+count])
        
        i += count
    
    return bytes(compressed)


def rle_decompress(data):
    """Decompress RLE data"""
    decompressed = []
    i = 0
    
    while i < len(data):
        if data[i] == 0xFE:
            # RLE marker
            count = data[i + 1]
            value = data[i + 2]
            decompressed.extend([value] * count)
            i += 3
        else:
            # Raw byte
            decompressed.append(data[i])
            i += 1
    
    return bytes(decompressed)


# Example: Overworld map
map_data = rom[0x1B3B0:0x1C000]  # Approximate

compressed = rle_compress(map_data)
ratio = len(compressed) / len(map_data)

print(f"Original: {len(map_data)} bytes")
print(f"Compressed: {len(compressed)} bytes")
print(f"Ratio: {ratio:.2%}")
print(f"Savings: {len(map_data) - len(compressed)} bytes")
```

**Expected Results**:
- Overworld: ~35-40% compression (lots of water/grass)
- Dungeons: ~20-30% compression (more variety)
- Towns: ~15-25% compression (complex layouts)

### Dictionary Compression

For repeating patterns:

```python
def find_repeated_patterns(data, min_length=4, min_occurrences=3):
    """Find repeated byte sequences"""
    patterns = {}
    
    for length in range(min_length, 16):  # Max pattern length
        for i in range(len(data) - length):
            pattern = bytes(data[i:i+length])
            
            if pattern not in patterns:
                patterns[pattern] = []
            patterns[pattern].append(i)
    
    # Filter by occurrence count
    frequent = {
        pattern: offsets 
        for pattern, offsets in patterns.items() 
        if len(offsets) >= min_occurrences
    }
    
    return frequent


# Find patterns
patterns = find_repeated_patterns(map_data)

print("Frequent Patterns:")
for pattern, offsets in sorted(patterns.items(), 
                                key=lambda x: len(x[0]) * len(x[1]), 
                                reverse=True)[:10]:
    savings = len(pattern) * (len(offsets) - 1)
    print(f"  Pattern (len {len(pattern)}): {len(offsets)} occurrences")
    print(f"    Potential savings: {savings} bytes")
```

---

## Code Optimization

### Assembly Optimizations

**1. Replace Subroutine Calls with Inlining** (small subroutines):

```assembly
; Before (6 bytes)
JSR AddHP
RTS

AddHP:
    CLC
    ADC PlayerHP
    STA PlayerHP
    RTS

; After (4 bytes)
CLC
ADC PlayerHP
STA PlayerHP

; Savings: 2 bytes per call
```

**2. Use Zero Page** (faster, smaller):

```assembly
; Before (4 bytes)
LDA $0300
STA $0301

; After (3 bytes) - if moved to zero page
LDA $30
STA $31

; Savings: 1 byte per operation
```

**3. Optimize Loops**:

```assembly
; Before
    LDX #39
Loop:
    ; ... process monster X ...
    DEX
    BPL Loop

; After (combine operations)
    LDX #39
Loop:
    ; ... process monster X ...
    DEX
    BNE Loop  ; Assumes X never 0 (works if count < 128)

; Savings: 1 byte
```

**4. Table Lookup vs Calculation**:

When to use tables:
- Small result set (< 256 values)
- Frequently accessed
- Complex calculation

Example:
```assembly
; Multiplication by 16 - calculate vs table

; Calculate (5 bytes, slower)
ASL A
ASL A
ASL A
ASL A

; Table lookup (3 bytes, faster)
TAX
LDA Mult16Table,X

Mult16Table:
    .byte 0, 16, 32, 48, 64, 80, 96, 112, ...
```

---

## Advanced Techniques

### Bank Switching

For ROMs > 32KB PRG:

```assembly
; Define banks
BANK0 = $8000
BANK1 = $C000

; Switch to bank 1
LDA #$01
STA BankRegister

; Access bank 1 data
LDA BANK1+$0100
```

**Dragon Warrior doesn't use bank switching**, but could be expanded.

### CHR Switching

Switch graphics mid-game:

```assembly
; Switch to dungeon tiles
LDA #$01
STA $2006  ; PPU address high
LDA #$00
STA $2006  ; PPU address low

; Copy new CHR data
LDX #$00
Loop:
    LDA DungeonCHR,X
    STA $2007
    INX
    BNE Loop
```

### Dynamic Decompression

Decompress data at runtime:

```assembly
DecompressRLE:
    LDY #$00
Loop:
    LDA (SrcPtr),Y
    CMP #$FE         ; RLE marker?
    BEQ RLERun
    
    ; Raw byte
    STA (DstPtr),Y
    INY
    JMP Loop

RLERun:
    INY
    LDA (SrcPtr),Y   ; Count
    TAX
    INY
    LDA (SrcPtr),Y   ; Value
WriteRun:
    STA (DstPtr),Y
    INY
    DEX
    BNE WriteRun
    INY
    JMP Loop
```

---

## Optimization Checklist

### Before Starting

- [ ] Analyze current space usage
- [ ] Identify unused regions
- [ ] Calculate entropy for data types
- [ ] Find duplicate tiles
- [ ] Analyze text frequency

### CHR-ROM Optimization

- [ ] Remove duplicate tiles
- [ ] Maximize sprite sharing (palette swapping)
- [ ] Consolidate similar tiles
- [ ] Consider dynamic CHR switching

### PRG-ROM Optimization

- [ ] Compress map data (RLE, dictionary)
- [ ] Implement text substitution
- [ ] Optimize lookup tables (delta encoding)
- [ ] Consolidate code (inline small subroutines)
- [ ] Use zero page where possible

### Testing

- [ ] Verify ROM size unchanged (or smaller)
- [ ] Test all game areas
- [ ] Verify no graphical glitches
- [ ] Check for crashes
- [ ] Benchmark performance (should be same or better)

---

## Case Study: Adding 10 Monsters

**Goal**: Add 10 new monsters without increasing ROM size

**Strategy**:

1. **Sprite Sharing** (0 bytes CHR):
   - Create 10 palette variants of existing sprites
   - Use different color palettes (0x00-0x07)

2. **Text Compression** (+879 bytes PRG):
   - Implement new substitutions (0x90-0x9F)
   - Save ~1,270 bytes from dialog
   - Use ~391 bytes for new monster names/data

3. **Map Compression** (+500 bytes PRG):
   - Compress overworld map with RLE
   - Save ~650 bytes
   - Use ~150 bytes for 10 monsters (10 × 16 bytes = 160 bytes)

**Result**:
- 10 new monsters added
- Net savings: ~879 bytes PRG
- No CHR space used
- ROM size: Same or smaller

---

## Tools

Use these tools to aid optimization:

```powershell
# Analyze ROM space
python tools/analyze_rom_space.py

# Analyze text compression
python tools/analyze_text_frequency.py

# Find palette optimizations
python tools/palette_analyzer.py --suggest-optimizations

# Benchmark performance
python tools/benchmark.py
```

---

## Conclusion

With careful optimization, Dragon Warrior ROM hacks can:

- Add 10-20 new monsters (using sprite sharing)
- Add 5-10 new spells (using saved text space)
- Expand dialog by 30-50%
- Create new map areas (using compression)

**All within the original 40KB ROM size.**

---

*Last Updated: November 2024*
*Dragon Warrior ROM Hacking Toolkit v1.0*
