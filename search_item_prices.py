#!/usr/bin/env python3
"""Search ROM for item cost data"""
import struct

data = open('roms/Dragon Warrior (U) (PRG1) [!].nes', 'rb').read()

# Known item costs (in gold):
# Herb (ID 18) = 24 gold
# Key (ID 19) = 8 gold (I think - need to verify)
# Actually from the output above:
# Item 25: 24 gold - this is Herb? No, Item 18 should be herb
# Item 26: 53 gold - Magic Key
# Item 27: 8 gold - Key?

# Let me search for known weapon prices instead
# Club = 60 gold = 0x3C00 in little-endian
# Copper Sword = 180 gold = 0xB400
# Hand Axe = 560 gold = 0x3002

print("Searching for Club price (60 = 0x3C)...")
target = bytes([0x3C, 0x00])  # 60 in little-endian
for i in range(len(data) - 1):
    if data[i:i+2] == target:
        print(f"  Found 0x3C00 at ROM offset: 0x{i:05X}")

print("\nSearching for Copper Sword price (180 = 0xB4)...")
target = bytes([0xB4, 0x00])  # 180 in little-endian
for i in range(len(data) - 1):
    if data[i:i+2] == target:
        print(f"  Found 0xB400 at ROM offset: 0x{i:05X}")

# Let me check known shop item prices: Herb=24
print("\nSearching for Herb price (24 = 0x18)...")
target = bytes([0x18, 0x00])  # 24 in little-endian
for i in range(len(data) - 1):
    if data[i:i+2] == target:
        # Check if it's followed by more prices
        if i + 10 < len(data):
            prices = [struct.unpack('<H', data[i+j*2:i+j*2+2])[0] for j in range(5)]
            print(f"  Found 0x1800 at ROM offset: 0x{i:05X} - next 5 values: {prices}")
