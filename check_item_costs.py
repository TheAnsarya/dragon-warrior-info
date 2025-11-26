#!/usr/bin/env python3
"""Check item cost data in ROM"""
import struct

data = open('roms/Dragon Warrior (U) (PRG1) [!].nes', 'rb').read()

print('Item costs at 0x1947:')
for i in range(29):
    offset = 0x1947 + i*2
    cost = struct.unpack('<H', data[offset:offset + 2])[0]
    print(f'  Item {i:2d}: {cost:5d} gold')
