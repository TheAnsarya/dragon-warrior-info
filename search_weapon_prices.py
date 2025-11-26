#!/usr/bin/env python3
"""Search for weapon price sequence"""
import struct

data = open('roms/Dragon Warrior (U) (PRG1) [!].nes', 'rb').read()

# Search for weapon sequence: [8, 60, 180, 560, 1200, 9800]
# In little-endian 16-bit: [0x08,0x00, 0x3C,0x00, 0xB4,0x00, 0x30,0x02, 0xB0,0x04, 0x48,0x26]
weapon_prices_bytes = bytes([
    0x08, 0x00,  # 8 (Torch)
    0x3C, 0x00,  # 60 (Club)
    0xB4, 0x00,  # 180 (Copper Sword)
    0x30, 0x02,  # 560 (Hand Axe)
    0xB0, 0x04,  # 1200 (Broad Sword)
    0x48, 0x26   # 9800 (Flame Sword)
])

print("Searching for weapon price sequence [8, 60, 180, 560, 1200, 9800]...")
for i in range(len(data) - len(weapon_prices_bytes)):
    if data[i:i+len(weapon_prices_bytes)] == weapon_prices_bytes:
        print(f"  FOUND at ROM offset: 0x{i:05X}")

        # Print surrounding data
        print(f"\n  Full item price table starting at 0x{i:05X}:")
        for j in range(29):
            offset = i + j*2
            price = struct.unpack('<H', data[offset:offset+2])[0]
            print(f"    Item {j:2d}: {price:5d} gold")

# Also try without Torch (starting with Club)
weapon_prices_no_torch = bytes([
    0x3C, 0x00,  # 60 (Club)
    0xB4, 0x00,  # 180 (Copper Sword)
    0x30, 0x02,  # 560 (Hand Axe)
    0xB0, 0x04,  # 1200 (Broad Sword)
    0x48, 0x26   # 9800 (Flame Sword)
])

print("\n\nSearching for weapon price sequence WITHOUT Torch [60, 180, 560, 1200, 9800]...")
for i in range(len(data) - len(weapon_prices_no_torch)):
    if data[i:i+len(weapon_prices_no_torch)] == weapon_prices_no_torch:
        print(f"  FOUND at ROM offset: 0x{i:05X}")

        # Check what's before this
        if i >= 2:
            price_before = struct.unpack('<H', data[i-2:i])[0]
            print(f"    Price before Club: {price_before} gold (should be Torch=8 if aligned)")
