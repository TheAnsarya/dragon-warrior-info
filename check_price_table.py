#!/usr/bin/env python3
"""Check potential item price table at 0x07E42"""
import struct

data = open('roms/Dragon Warrior (U) (PRG1) [!].nes', 'rb').read()

# Check 0x07E42 which had sequence [24, 8, 20, 70, 53]
offset = 0x07E42
print(f"Item prices at 0x{offset:05X}:")
print("="*60)
for i in range(29):
    addr = offset + i*2
    price = struct.unpack('<H', data[addr:addr+2])[0]
    print(f"  Offset 0x{addr:05X} Item {i:2d}: {price:5d} gold")

print("\n" + "="*60)
print("EXPECTED PRICES (from Dragon Warrior):")
print("="*60)
print("  Torch: Free (or 8 gold?)")
print("  Club: 60 gold")
print("  Copper Sword: 180 gold")
print("  Hand Axe: 560 gold")
print("  Broad Sword: 1200 gold")
print("  Flame Sword: 9800 gold")
print("  Erdrick's Sword: Not sold")
print("  Clothes: 20 gold")
print("  Leather Armor: 70 gold")
print("  Chain Mail: 300 gold")
print("  Half Plate: 1000 gold")
print("  Full Plate: 3000 gold")
print("  Magic Armor: 7700 gold")
print("  Small Shield: 90 gold")
print("  Large Shield: 800 gold")
print("  Silver Shield: 14800 gold")
print("  Herb: 24 gold")
print("  Magic Key: 53 gold")
print("  Wings (Fairy Water): 70 gold")
