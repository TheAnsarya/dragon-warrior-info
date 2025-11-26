#!/usr/bin/env python3
"""Analyze item cost patterns"""
import struct

data = open('roms/Dragon Warrior (U) (PRG1) [!].nes', 'rb').read()

print("Known Dragon Warrior item prices:")
print("="*80)
known_prices = {
    "Torch": 8, "Club": 60, "Copper Sword": 180, "Hand Axe": 560,
    "Broad Sword": 1200, "Flame Sword": 9800,
    "Clothes": 20, "Leather Armor": 70, "Chain Mail": 300,
    "Half Plate": 1000, "Full Plate": 3000, "Magic Armor": 7700,
    "Small Shield": 90, "Large Shield": 800, "Silver Shield": 14800,
    "Erdrick's Shield": "Not sold",
    "Herb": 24, "Key": 25, "Magic Key": 53,
    "Wings/Fairy Water": 70
}

for name, price in known_prices.items():
    print(f"  {name:20s}: {price} gold")

print("\n" + "="*80)
print("Current extraction at 0x1947:")
print("="*80)
for i in range(29):
    offset = 0x1947 + i*2
    price = struct.unpack('<H', data[offset:offset+2])[0]
    item_names = ["Torch", "Club", "Copper Sword", "Hand Axe", "Broad Sword", "Flame Sword",
                  "Erdrick's Sword", "Clothes", "Leather Armor", "Chain Mail", "Half Plate",
                  "Full Plate", "Magic Armor", "Erdrick's Armor", "Small Shield", "Large Shield",
                  "Silver Shield", "Erdrick's Shield", "Herb", "Key", "Magic Key",
                  "Erdrick's Token", "Gwaelin's Love", "Cursed Belt", "Silver Harp",
                  "Death Necklace", "Stones of Sunlight", "Staff of Rain", "Rainbow Drop"]
    print(f"  ID {i:2d} {item_names[i]:20s}: {price:5d} gold")

# 514 = 0x0202, that's suspicious - maybe it's not cost data at all?
print(f"\n514 decimal = 0x{514:04X} hex = binary {bin(514)}")
print("This looks like it might be sprite/tile data or pointers, not prices!")
