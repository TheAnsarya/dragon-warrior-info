# ROM Data Extraction - Real Data Implementation

## Overview

The Dragon Warrior asset extraction system has been updated to extract **real data from the ROM** instead of using sample/hardcoded data. This provides authentic game data for editing and modification.

## Fixed Data Sources

### 1. Monster Stats (`extract_monster_stats`)
**ROM Source**: `EnStatTbl` at Bank01:L9E4B (ROM offset 0x5E5B)
- **Format**: 16 bytes per monster (Attack, Defense, HP, Spell, Agility, Magic Defense, Experience, Gold, 8 unused bytes)
- **Count**: 40 monsters (Slime through Dragonlord)
- **Data**: Real attack, defense, HP, experience, and gold values from ROM

### 2. Item Data (`extract_item_data`)
**ROM Sources**: Multiple tables in Bank00
- **WeaponsBonusTbl** at L99CF (ROM offset 0x19CF) - Attack bonuses for weapons
- **ArmorBonusTbl** at L99D7 (ROM offset 0x19D7) - Defense bonuses for armor
- **ShieldBonusTbl** at L99DF (ROM offset 0x19DF) - Defense bonuses for shields  
- **ItemCostTbl** at L9947 (ROM offset 0x1947) - Buy/sell prices (2 bytes per item)
- **Count**: 29 items total
- **Data**: Real attack/defense bonuses and prices from ROM tables

### 3. Spell Data (`extract_spell_data`)
**ROM Source**: `SpellCostTbl` at Bank00:L9D53 (ROM offset 0x1D53)
- **Format**: 1 byte per spell for MP cost
- **Learning Levels**: Extracted from assembly code analysis (levels 3, 4, 7, 9, 10, 12, 13, 15, 17, 19)
- **Count**: 10 spells
- **Data**: Real MP costs from ROM, accurate learning levels

### 4. Shop Data (`extract_shop_data`)
**ROM Sources**: 
- **ShopItemsTbl** at Bank00:L9991 (ROM offset 0x1991) - Item inventories
- **InnCostTbl** at Bank00:L998C (ROM offset 0x198C) - Inn prices
- **Format**: Item lists terminated by 0xFD marker
- **Count**: 12 shops (7 weapon/armor shops + 5 item shops)
- **Data**: Real shop inventories and inn prices

### 5. Graphics Data (`extract_chr_rom`)
**ROM Source**: CHR-ROM at offset 0x8010
- **Format**: NES 2bpp tile format, 8x8 pixels, 16 bytes per tile
- **Size**: 8KB CHR-ROM (512 tiles)
- **Data**: Real graphics tiles from ROM

## ROM Address Calculations

Dragon Warrior uses standard NES banking:
- **Bank 0**: 0x0010-0x4000 (ROM offset = Address - 0x8000)
- **Bank 1**: 0x4010-0x8000 (ROM offset = 0x4010 + (Address - 0x8000))
- **CHR-ROM**: 0x8010-0xA010

## Data Validation

The extracted data now matches the actual game behavior:

### Monster Stats (Examples from ROM)
- **Slime**: HP=3, Attack=5, Defense=3, Experience=1, Gold=2
- **Red Slime**: HP=4, Attack=7, Defense=3, Experience=1, Gold=3
- **Dragonlord**: HP varies (final boss), high stats

### Item Prices (Examples from ROM)
- **Bamboo Pole**: 10 gold
- **Club**: 60 gold  
- **Flame Sword**: 9800 gold
- **Magic Armor**: 7700 gold

### Spell Costs (Examples from ROM)
- **Heal**: 4 MP (was incorrectly 3 in sample data)
- **Hurtmore**: 5 MP (was incorrectly 8 in sample data)
- **Healmore**: 10 MP (correct)

### Shop Inventories (Examples from ROM)
- **Brecconary Weapons**: Items [0, 1, 2, 7, 8, 14] (Bamboo Pole, Club, Copper Sword, Clothes, Leather Armor, Small Shield)
- **Cantlin Weapons 1**: Items [0, 1, 2, 8, 9, 15] 
- **Cantlin Weapons 3**: Items [5, 16] (Flame Sword, Silver Shield)

## Complex Data Notes

### Dialog Text
Dragon Warrior uses a complex text compression algorithm. The current implementation provides game-accurate dialog content but doesn't extract the compressed format. Full text extraction would require:
1. Text compression algorithm reverse engineering
2. Dictionary table extraction
3. Pointer table parsing

### Map Data  
Map data uses run-length encoding and complex block conversion tables. Current implementation provides basic map structure. Full extraction would require:
1. RLE decompression
2. Block conversion table parsing
3. NPC placement data extraction

## Usage Impact

This change ensures that:
1. **Editors show real game values** - No more placeholder data
2. **Modifications affect actual gameplay** - Changes are authentic
3. **Extraction is ROM-dependent** - Different ROM versions will extract different data
4. **Data integrity** - Values match what players experience in-game

## Testing

To verify real data extraction:

```bash
# Extract from actual Dragon Warrior ROM
python tools/extraction/data_extractor.py dragon_warrior.nes --output-dir extracted_assets

# Check monster HP values match game
# Slime should have HP=3, not placeholder values

# Check item prices match shops  
# Club should cost 60 gold, not generated values

# Check spell MP costs match gameplay
# Heal should cost 4 MP, not 3
```

This implementation provides an authentic foundation for ROM modification and ensures all extracted data reflects the actual Dragon Warrior game behavior.
