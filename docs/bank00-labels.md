# Dragon Warrior - Bank 00 Label Documentation

## Overview
Bank 00 is the main fixed code bank containing core game systems.
CPU address range: $8000-$BFFF (16KB)
File offset: $0010-$400F

## Major Systems

### Dialog System

| Label | Address | Description |
|-------|---------|-------------|
| `DoDialogHiBlock` | Various | High-level dialog block processing |
| `GetDialogChar` | Various | Retrieves next character from dialog stream |
| `PrintChar` | Various | Renders character to screen buffer |
| `DialogWaitBtn` | Various | Waits for button press during dialog |
| `ClearDialogLine` | Various | Clears current dialog line |
| `AdvanceDialogPtr` | Various | Advances dialog data pointer |

### Window System

| Label | Address | Description |
|-------|---------|-------------|
| `DoWindow` | $C6F0 | Main window handler |
| `WindowErase` | Various | Erases window from screen |
| `WindowEraseParams` | Various | Window erase parameter table |
| `WindowYesNo` | Various | Yes/No selection window |
| `WindowLoadCmd` | Various | Command menu window |

### Menu System

| Label | Address | Description |
|-------|---------|-------------|
| `CommandMenuHandler` | Various | Main command menu |
| `StatusMenuHandler` | Various | Status screen |
| `ItemMenuHandler` | Various | Item selection |
| `SpellMenuHandler` | Various | Spell selection |
| `EquipMenuHandler` | Various | Equipment screen |

### Combat System

| Label | Address | Description |
|-------|---------|-------------|
| `CalcAttackDamage` | Various | Calculate physical attack damage |
| `CalcDefense` | Various | Calculate defense reduction |
| `CalcMagicDamage` | Various | Calculate spell damage |
| `ProcessEnemyTurn` | Various | Handle enemy actions |
| `CheckCritical` | Various | Critical hit check |
| `CheckMiss` | Various | Miss chance check |

### Math Utilities

| Label | Address | Description |
|-------|---------|-------------|
| `Multiply8x8` | Various | 8-bit multiplication |
| `Divide16` | Various | 16-bit division |
| `BinToBCD` | Various | Binary to BCD conversion |
| `BCDToBin` | Various | BCD to binary conversion |
| `RandomNumber` | Various | RNG routine |

### Gold/Experience

| Label | Address | Description |
|-------|---------|-------------|
| `AddGold` | Various | Add gold to player |
| `SubtractGold` | Various | Remove gold from player |
| `CheckGold` | Various | Check if player has enough gold |
| `AddExperience` | Various | Add XP to player |
| `CheckLevelUp` | Various | Check for level up |
| `DoLevelUp` | Various | Process level up stats |

## Data Tables

### Equipment Tables
- `WeaponsBonusTbl` - Weapon attack bonuses
- `ArmorBonusTbl` - Armor defense bonuses
- `ShieldBonusTbl` - Shield defense bonuses

### Price Tables
- `ItemCostTbl` - Item purchase prices
- `ShopItemsTbl` - Shop inventory lists

### Spell Data
- `SpellCostTbl` - MP costs for spells
- `SpellEffectTbl` - Spell effect data

## Label Prefixes

| Prefix | Meaning |
|--------|---------|
| `_Loop` | Loop body |
| `_Continue` | Loop continuation |
| `_Break` | Loop exit |
| `_Exit` | Function exit |
| `_Return` | Return to caller |
| `_Branchto` | Branch target |
| `_Call` | Subroutine call |
| `_Load` | Load operation |
| `_Store` | Store operation |
| `_Calc` | Calculation |
| `_Check` | Condition check |
| `_Init` | Initialization |
| `_Done` | Completion |
