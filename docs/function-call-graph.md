# Dragon Warrior - Function Call Graph

This document shows the call relationships between major functions in the Dragon Warrior disassembly.

## Main Game Loop (Bank 03)

```
RESET ($FF8E)
├── InitializeHardware
├── ClearRAM
├── SetupMMC1
└── MainGameLoop
    ├── ProcessVBlank
    │   ├── WaitForNMI ($FF74)
    │   ├── UpdateSprites
    │   └── UpdatePPU
    ├── CheckForTriggers ($CBF7)
    │   ├── CheckDoorTrigger
    │   ├── CheckStairsTrigger
    │   ├── CheckChestTrigger
    │   └── CheckNPCTrigger
    ├── ProcessPlayerInput
    │   ├── HandleMovement
    │   ├── HandleMenuOpen
    │   └── HandleActionButton
    └── UpdateGameState
        ├── UpdateNPCs
        ├── UpdateAnimations
        └── CheckRandomEncounter
```

## Dialog System (Bank 00/01)

```
DoDialogHiBlock
├── GetDialogChar
│   ├── ReadDialogByte
│   └── ProcessControlCode
│       ├── HandleNewLine
│       ├── HandlePlayerName
│       ├── HandleEnemyName
│       ├── HandleNumber
│       └── HandleWait
├── PrintChar
│   ├── CalcPPUBufferAddr ($C596)
│   └── AddPPUBufferEntry ($C690)
└── DialogWaitBtn
    └── GetJoypadStatus
```

## Window System (Bank 00/01)

```
DoWindow ($C6F0)
├── WindowCreate
│   ├── CalcWindowPosition
│   ├── DrawWindowBorder
│   └── FillWindowBackground
├── WindowErase
│   ├── GetEraseParams
│   └── ClearWindowArea
├── WindowYesNo
│   ├── DrawYesNoOptions
│   ├── HandleCursorMovement
│   └── ReturnSelection
└── WindowShowHide ($ABC4)
    ├── ShowWindow
    └── HideWindow
```

## Combat System (Bank 00/03)

```
InitBattle
├── LoadEnemyStats ($9961)
├── LoadBattleGraphics
├── SetupBattleVariables
└── DoBattleLoop
    ├── ShowBattleMenu
    │   ├── ShowFightOption
    │   ├── ShowSpellOption
    │   ├── ShowItemOption
    │   └── ShowRunOption
    ├── ProcessPlayerAction
    │   ├── CalcAttackDamage
    │   │   ├── GetPlayerAttack
    │   │   ├── GetEnemyDefense
    │   │   ├── CalcBaseDamage
    │   │   └── ApplyRandomVariance
    │   ├── ProcessSpellCast
    │   │   ├── CheckMPCost
    │   │   ├── CalcSpellEffect
    │   │   └── ApplySpellDamage
    │   └── ProcessItemUse
    ├── ProcessEnemyAction
    │   ├── SelectEnemyAction
    │   ├── CalcEnemyDamage
    │   └── ApplyDamageToPlayer
    └── CheckBattleEnd
        ├── CheckPlayerDeath
        ├── CheckEnemyDeath
        │   ├── AwardExperience
        │   ├── AwardGold
        │   └── CheckItemDrop
        └── CheckLevelUp
```

## Sound System (Bank 01)

```
UpdateSound ($8XXX)
├── ProcessMusicQueue
│   ├── LoadMusicData
│   ├── UpdateMusicChannels
│   │   ├── UpdateSquare1
│   │   ├── UpdateSquare2
│   │   ├── UpdateTriangle
│   │   └── UpdateNoise
│   └── HandleMusicEnd
├── ProcessSFXQueue
│   ├── LoadSFXData
│   ├── PlaySFXChannel
│   └── HandleSFXPriority
└── ClearSoundRegisters ($8178)
```

## Map System (Bank 00/02/03)

```
ChangeMaps ($D9E2)
├── SaveCurrentMapState
├── LoadNewMapData
│   ├── GetMapDataPointer
│   ├── LoadMapTiles
│   └── LoadMapObjects
├── LoadMapGraphics
│   ├── Bank0ToCHR0 ($FCA3)
│   ├── Bank2ToCHR1 ($FCAD)
│   └── LoadMapPalettes
├── SpawnNPCs
│   ├── LoadNPCTable
│   └── InitializeNPCPositions
└── SetPlayerPosition
```

## Sprite System (Bank 00)

```
DoSprites ($B6DA)
├── UpdatePlayerSprite
│   ├── GetPlayerAnimation
│   ├── CalcPlayerScreenPos
│   └── WritePlayerOAM
├── UpdateNPCSprites
│   ├── GetNPCSpriteIndex ($C0F4)
│   ├── CalcNPCScreenPos
│   └── WriteNPCOAM
└── ClearSpriteRAM ($C6BB)
```

## Math Utilities (Bank 00)

```
WordMultiply ($C1C9)
├── Setup16BitMultiply
├── MultiplyLoop
└── StoreResult

ByteDivide ($C1F0)
├── Setup8BitDivide
├── DivideLoop
└── StoreQuotientRemainder

UpdateRandNumber ($C55B)
├── GetCurrentSeed
├── LFSRStep
└── StorNewSeed
```

## Palette System (Bank 00)

```
PalFadeIn ($C529)
├── SetInitialPalette
├── FadeStep
│   ├── IncrementColors
│   └── UpdatePPUPalette
└── CheckFadeComplete

PalFadeOut ($C212)
├── GetCurrentPalette
├── FadeStep
│   ├── DecrementColors
│   └── UpdatePPUPalette
└── CheckFadeComplete

LoadStartPals ($AA7E)
├── PrepBGPalLoad ($C63D)
├── PrepSPPalLoad ($C632)
└── TransferPalettes
```

## Bank Switching (Bank 03)

```
IRQ Handler
├── SaveRegisters
├── ReadBankPointer
├── CallBankFunction
│   ├── SetMMC1Bank
│   ├── JSR ToFunction
│   └── RestoreBank
└── RestoreRegisters

Bank0ToCHR0 ($FCA3)
├── SetMMC1CHRBank0
└── Return

Bank1ToCHR0 ($FC98)
├── SetMMC1CHRBank0
└── Return
```

## Key Memory Locations

| Address | Name | Description |
|---------|------|-------------|
| $00-$FF | Zero Page | Fast access variables |
| $0200-$02FF | OAM Buffer | Sprite data |
| $0300-$03FF | PPU Buffer | Pending PPU writes |
| $0400-$07FF | Game State | Player stats, inventory, flags |
| $6000-$7FFF | Save RAM | Battery-backed save data |

## Interrupt Vectors

| Vector | Address | Handler |
|--------|---------|---------|
| NMI | $FFFA | NMI ($BFD8) |
| RESET | $FFFC | RESET ($BFD8) |
| IRQ | $FFFE | IRQ ($BFD8) |
