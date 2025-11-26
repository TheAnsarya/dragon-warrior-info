#!/usr/bin/env python3
"""Check item costs from window/shop table"""
import struct

data = open('roms/Dragon Warrior (U) (PRG1) [!].nes', 'rb').read()

# WndCostTbl at CPU 0xBE10
# Assuming Bank 3: ROM offset = (0xBE10 - 0x8000) + Bank3_start
# Bank3 starts at: header (16) + Bank0 (16KB) + Bank1 (16KB) + Bank2 (16KB) = 16 + 0x4000*3 = 0xC010
# So 0xBE10 - 0x8000 = 0x3E10, + 0xC010 = 0xFC20

offset = 0xFC20
print(f"WndCostTbl at ROM 0x{offset:05X} (CPU 0xBE10):")
print("="*60)
for i in range(29):
    price = struct.unpack('<H', data[offset + i*2:offset + i*2 + 2])[0]
    print(f"  Item {i:2d}: {price:5d} gold")

print("\n\nAlso checking alternate calculation:")
# Maybe it's Bank 1? Bank1 starts at 0x4010
# 0xBE10 - 0x8000 = 0x3E10, + 0x4010 = 0x7E20
offset2 = 0x7E20
print(f"Alternate at ROM 0x{offset2:05X}:")
for i in range(10):
    price = struct.unpack('<H', data[offset2 + i*2:offset2 + i*2 + 2])[0]
    print(f"  Item {i:2d}: {price:5d} gold")
