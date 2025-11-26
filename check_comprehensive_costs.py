#!/usr/bin/env python3
"""Check comprehensive price table at 0x07E20"""
import struct

data = open('roms/Dragon Warrior (U) (PRG1) [!].nes', 'rb').read()

offset = 0x07E20
print(f"Comprehensive item cost table at ROM 0x{offset:05X}:")
print("="*80)

item_names = [
    "Torch", "Club", "Copper Sword", "Hand Axe", "Broad Sword", "Flame Sword",
    "Erdrick's Sword", "Clothes", "Leather Armor", "Chain Mail", "Half Plate",
    "Full Plate", "Magic Armor", "Erdrick's Armor", "Small Shield", "Large Shield",
    "Silver Shield", "Erdrick's Shield", "Herb", "Key", "Magic Key",
    "Erdrick's Token", "Gwaelin's Love", "Cursed Belt", "Silver Harp",
    "Death Necklace", "Stones of Sunlight", "Staff of Rain", "Rainbow Drop"
]

# Expected prices
expected = {
    "Torch": 8, "Club": 60, "Copper Sword": 180, "Hand Axe": 560,
    "Broad Sword": 1200, "Flame Sword": 9800, "Erdrick's Sword": 0,
    "Clothes": 20, "Leather Armor": 70, "Chain Mail": 300, "Half Plate": 1000,
    "Full Plate": 3000, "Magic Armor": 7700, "Erdrick's Armor": 0,
    "Small Shield": 90, "Large Shield": 800, "Silver Shield": 14800,
    "Erdrick's Shield": 0, "Herb": 24, "Key": 25, "Magic Key": 53
}

for i in range(35):
    price = struct.unpack('<H', data[offset + i*2:offset + i*2 + 2])[0]
    if i < len(item_names):
        name = item_names[i]
        exp = expected.get(name, "?")
        match = " ✓" if price == exp else f" (expected {exp})"
        print(f"  Slot {i:2d}: {price:5d} gold - {name:20s}{match}")
    else:
        print(f"  Slot {i:2d}: {price:5d} gold")
