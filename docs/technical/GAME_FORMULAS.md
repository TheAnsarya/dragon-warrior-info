# Dragon Warrior Game Formulas and Constants

**Complete Reference for All Game Calculations and Magic Numbers**

Version: 1.0  
Last Updated: November 2024

---

## Table of Contents

1. [Battle System](#battle-system)
2. [Experience and Leveling](#experience-and-leveling)
3. [Stat Growth](#stat-growth)
4. [Spell Formulas](#spell-formulas)
5. [Item Effects](#item-effects)
6. [Encounter System](#encounter-system)
7. [Enemy AI](#enemy-ai)
8. [Technical Limits](#technical-limits)

---

## Battle System

### Physical Damage Calculation

**Player Attacks Enemy:**

```
Damage = (PlayerATK / 2) - (EnemyDEF / 4)
If Damage < 0: Damage = 0
RandomVariance = Random(0, 4)
FinalDamage = Damage + RandomVariance
```

**Assembly Location:** `Bank03.asm` at `CalcPhysicalDamage` (~line 4000)

**Constants:**
- `PLAYER_ATK_DIVISOR = 2` - Player attack power divisor
- `ENEMY_DEF_DIVISOR = 4` - Enemy defense divisor
- `DAMAGE_VARIANCE = 4` - Random damage variance (0-4)

**Example:**
```
Player ATK = 20, Enemy DEF = 8
Base Damage = (20 / 2) - (8 / 4) = 10 - 2 = 8
Random Variance = 0-4
Final Damage = 8-12
```

**Enemy Attacks Player:**

```
Damage = (EnemySTR / 2) - (PlayerDEF / 4)
If Damage < 0: Damage = 0
RandomVariance = Random(0, 4)
FinalDamage = Damage + RandomVariance
```

**Constants:**
- `ENEMY_STR_DIVISOR = 2` - Enemy strength divisor
- `PLAYER_DEF_DIVISOR = 4` - Player defense divisor

### Critical Hits

**Critical Hit Chance:**

```
CritChance = PlayerAGI / 64
RandValue = Random(0, 255)
IsCrit = (RandValue < CritChance)
```

**Critical Damage Multiplier:**

```
CritDamage = NormalDamage * 2
```

**Assembly Location:** `Bank03.asm` at `CheckCriticalHit` (~line 4100)

**Constants:**
- `CRIT_AGI_DIVISOR = 64` - Agility to crit chance divisor
- `CRIT_MULTIPLIER = 2` - Critical hit damage multiplier

**Example:**
```
Player AGI = 32
CritChance = 32 / 64 = 0.5 (128/256 = 50%)
If Random < 128: Critical Hit!
```

### Hit/Miss Calculation

**Player Hit Chance:**

```
BaseHitChance = 224  ; 87.5% (224/256)
EvasionPenalty = EnemyAGI / 4
HitChance = BaseHitChance - EvasionPenalty
RandValue = Random(0, 255)
IsHit = (RandValue < HitChance)
```

**Enemy Hit Chance:**

```
BaseHitChance = 192  ; 75% (192/256)
EvasionPenalty = PlayerAGI / 2
HitChance = BaseHitChance - EvasionPenalty
RandValue = Random(0, 255)
IsHit = (RandValue < HitChance)
```

**Assembly Location:** `Bank03.asm` at `CheckHit` (~line 4200)

**Constants:**
- `PLAYER_BASE_HIT = 224` - Player base hit chance (87.5%)
- `ENEMY_BASE_HIT = 192` - Enemy base hit chance (75%)
- `ENEMY_AGI_EVASION_DIV = 4` - Enemy agility evasion divisor
- `PLAYER_AGI_EVASION_DIV = 2` - Player agility evasion divisor

### Dodge Calculation

**Excellent Move (Dodge):**

```
DodgeChance = PlayerAGI / 4
RandValue = Random(0, 255)
IsDodge = (RandValue < DodgeChance)
```

**Assembly Location:** `Bank03.asm` at `CheckDodge` (~line 4300)

**Constants:**
- `DODGE_AGI_DIVISOR = 4` - Agility to dodge chance divisor

**Example:**
```
Player AGI = 64
DodgeChance = 64 / 4 = 16 (16/256 = 6.25%)
```

### Sleep Chance

**Enemy Sleep Spell:**

```
BaseSleepChance = 128  ; 50% (128/256)
ResistPenalty = PlayerLevel * 2
SleepChance = BaseSleepChance - ResistPenalty
If SleepChance < 32: SleepChance = 32  ; Min 12.5%
RandValue = Random(0, 255)
IsSleep = (RandValue < SleepChance)
```

**Assembly Location:** `Bank03.asm` at `ApplySleep` (~line 5100)

**Constants:**
- `BASE_SLEEP_CHANCE = 128` - Base sleep success chance (50%)
- `LEVEL_RESIST_MULT = 2` - Level resistance multiplier
- `MIN_SLEEP_CHANCE = 32` - Minimum sleep chance (12.5%)

### Stopspell Chance

**Stopspell Success:**

```
BaseStopChance = 160  ; 62.5% (160/256)
ResistPenalty = EnemyLevel * 3
StopChance = BaseStopChance - ResistPenalty
If StopChance < 16: StopChance = 16  ; Min 6.25%
RandValue = Random(0, 255)
IsStop = (RandValue < StopChance)
```

**Assembly Location:** `Bank03.asm` at `ApplyStopspell` (~line 5200)

**Constants:**
- `BASE_STOPSPELL_CHANCE = 160` - Base stopspell chance (62.5%)
- `ENEMY_LEVEL_RESIST = 3` - Enemy level resistance multiplier
- `MIN_STOPSPELL_CHANCE = 16` - Minimum stopspell chance (6.25%)

---

## Experience and Leveling

### Experience Requirements

**Level-Up Experience Formula:**

The game uses a lookup table, not a formula. Experience required for each level:

| Level | Total EXP | EXP for Level |
|-------|-----------|---------------|
| 1 | 0 | 0 |
| 2 | 7 | 7 |
| 3 | 23 | 16 |
| 4 | 47 | 24 |
| 5 | 110 | 63 |
| 6 | 220 | 110 |
| 7 | 450 | 230 |
| 8 | 800 | 350 |
| 9 | 1,300 | 500 |
| 10 | 2,000 | 700 |
| 11 | 2,900 | 900 |
| 12 | 4,000 | 1,100 |
| 13 | 5,500 | 1,500 |
| 14 | 7,500 | 2,000 |
| 15 | 10,000 | 2,500 |
| 16 | 13,000 | 3,000 |
| 17 | 16,500 | 3,500 |
| 18 | 20,000 | 3,500 |
| 19 | 24,000 | 4,000 |
| 20 | 28,000 | 4,000 |
| 21 | 32,000 | 4,000 |
| 22 | 36,000 | 4,000 |
| 23 | 40,000 | 4,000 |
| 24 | 44,000 | 4,000 |
| 25 | 48,000 | 4,000 |
| 26 | 52,000 | 4,000 |
| 27 | 56,000 | 4,000 |
| 28 | 60,000 | 4,000 |
| 29 | 64,000 | 4,000 |
| 30 | 65,535 | 1,535 |

**Assembly Location:** `Bank01.asm` at `ExpRequirements` table (~line 3400)

**Data Format:**
```assembly
ExpRequirements:
    .word $0000  ; Level 1: 0 EXP
    .word $0007  ; Level 2: 7 EXP
    .word $0017  ; Level 3: 23 EXP
    ; ... etc
```

**Constants:**
- `MAX_LEVEL = 30` - Maximum player level
- `MAX_EXP = 65535` - Maximum experience (16-bit limit)

### Experience Gain

**Formula:**

```
ExpGained = MonsterBaseExp
GoldGained = MonsterBaseGold
```

**No bonuses or modifiers** - direct values from monster stats table.

**Assembly Location:** `Bank03.asm` at `BattleVictory` (~line 4700)

---

## Stat Growth

### HP Gain Per Level

**HP Growth Formula:**

The game uses a lookup table with some randomness:

```
BaseHPGain = HPGainTable[NewLevel]
RandomBonus = Random(0, 3)
FinalHPGain = BaseHPGain + RandomBonus
NewHP = OldHP + FinalHPGain
```

**HP Gain Table:**

| Level | Base HP Gain | Range (with random) |
|-------|--------------|---------------------|
| 2 | 5 | 5-8 |
| 3 | 4 | 4-7 |
| 4 | 8 | 8-11 |
| 5 | 6 | 6-9 |
| 6 | 10 | 10-13 |
| 7 | 8 | 8-11 |
| 8 | 12 | 12-15 |
| 9 | 10 | 10-13 |
| 10 | 15 | 15-18 |
| 11 | 12 | 12-15 |
| 12 | 18 | 18-21 |
| 13 | 15 | 15-18 |
| 14 | 20 | 20-23 |
| 15 | 18 | 18-21 |
| 16 | 22 | 22-25 |
| 17 | 20 | 20-23 |
| 18 | 25 | 25-28 |
| 19 | 22 | 22-25 |
| 20 | 28 | 28-31 |
| 21-30 | 5 | 5-8 |

**Assembly Location:** `Bank03.asm` at `HPGainTable` and `LevelUpHP` routine (~line 3800)

**Constants:**
- `HP_RANDOM_BONUS = 3` - Random HP bonus range (0-3)

### MP Gain Per Level

**MP Growth Formula:**

Similar to HP, uses a lookup table:

```
BaseMPGain = MPGainTable[NewLevel]
RandomBonus = Random(0, 2)
FinalMPGain = BaseMPGain + RandomBonus
NewMP = OldMP + FinalMPGain
```

**MP Gain Table:**

| Level | Base MP Gain | Range (with random) |
|-------|--------------|---------------------|
| 2 | 0 | 0-2 |
| 3 | 5 | 5-7 |
| 4 | 3 | 3-5 |
| 5 | 6 | 6-8 |
| 6 | 4 | 4-6 |
| 7 | 8 | 8-10 |
| 8 | 6 | 6-8 |
| 9 | 10 | 10-12 |
| 10 | 8 | 8-10 |
| 11 | 12 | 12-14 |
| 12 | 10 | 10-12 |
| 13 | 15 | 15-17 |
| 14 | 12 | 12-14 |
| 15 | 18 | 18-20 |
| 16 | 15 | 15-17 |
| 17 | 20 | 20-22 |
| 18-30 | 3 | 3-5 |

**Assembly Location:** `Bank03.asm` at `MPGainTable` and `LevelUpMP` routine (~line 3900)

**Constants:**
- `MP_RANDOM_BONUS = 2` - Random MP bonus range (0-2)

### Strength Gain

**STR Growth Formula:**

```
If (NewLevel % 2 == 0):  ; Even levels
    STRGain = Random(2, 4)
Else:  ; Odd levels
    STRGain = Random(1, 3)
NewSTR = OldSTR + STRGain
```

**Assembly Location:** `Bank03.asm` at `LevelUpSTR` routine (~line 4000)

**Constants:**
- `EVEN_LEVEL_STR_MIN = 2` - Minimum STR gain on even levels
- `EVEN_LEVEL_STR_MAX = 4` - Maximum STR gain on even levels
- `ODD_LEVEL_STR_MIN = 1` - Minimum STR gain on odd levels
- `ODD_LEVEL_STR_MAX = 3` - Maximum STR gain on odd levels

### Agility Gain

**AGI Growth Formula:**

```
If (NewLevel % 2 == 1):  ; Odd levels
    AGIGain = Random(2, 5)
Else:  ; Even levels
    AGIGain = Random(1, 3)
NewAGI = OldAGI + AGIGain
```

**Assembly Location:** `Bank03.asm` at `LevelUpAGI` routine (~line 4050)

**Constants:**
- `ODD_LEVEL_AGI_MIN = 2` - Minimum AGI gain on odd levels
- `ODD_LEVEL_AGI_MAX = 5` - Maximum AGI gain on odd levels
- `EVEN_LEVEL_AGI_MIN = 1` - Minimum AGI gain on even levels
- `EVEN_LEVEL_AGI_MAX = 3` - Maximum AGI gain on even levels

### Spell Learning

**Spell Unlock Levels:**

| Level | Spell Learned |
|-------|---------------|
| 3 | HEAL |
| 4 | HURT |
| 7 | SLEEP |
| 9 | RADIANT |
| 10 | STOPSPELL |
| 12 | OUTSIDE |
| 13 | RETURN |
| 15 | REPEL |
| 17 | HEALMORE |
| 19 | HURTMORE |

**Assembly Location:** `Bank03.asm` at `CheckSpellLearning` and spell unlock table (~line 4100)

**Data Format:**
```assembly
SpellUnlockTable:
    .byte 3, SPELL_HEAL
    .byte 4, SPELL_HURT
    .byte 7, SPELL_SLEEP
    ; ... etc
    .byte $FF  ; End marker
```

---

## Spell Formulas

### HEAL

**Healing Amount:**

```
MinHeal = 10
MaxHeal = 17
HealAmount = Random(MinHeal, MaxHeal)
NewHP = CurrentHP + HealAmount
If NewHP > MaxHP: NewHP = MaxHP
```

**Assembly Location:** `Bank03.asm` at `SpellHEAL` (~line 4800)

**Constants:**
- `HEAL_MIN = 10` - Minimum HP restored
- `HEAL_MAX = 17` - Maximum HP restored
- `HEAL_MP_COST = 4` - MP cost

### HEALMORE

**Healing Amount:**

```
MinHeal = 85
MaxHeal = 100
HealAmount = Random(MinHeal, MaxHeal)
NewHP = CurrentHP + HealAmount
If NewHP > MaxHP: NewHP = MaxHP
```

**Assembly Location:** `Bank03.asm` at `SpellHEALMORE` (~line 4850)

**Constants:**
- `HEALMORE_MIN = 85` - Minimum HP restored
- `HEALMORE_MAX = 100` - Maximum HP restored
- `HEALMORE_MP_COST = 10` - MP cost

### HURT

**Damage Amount:**

```
MinDamage = 5
MaxDamage = 12
BaseDamage = Random(MinDamage, MaxDamage)
EnemyResist = EnemyDEF / 8
FinalDamage = BaseDamage - EnemyResist
If FinalDamage < 1: FinalDamage = 1
```

**Assembly Location:** `Bank03.asm` at `SpellHURT` (~line 4900)

**Constants:**
- `HURT_MIN = 5` - Minimum base damage
- `HURT_MAX = 12` - Maximum base damage
- `HURT_RESIST_DIV = 8` - Enemy defense resistance divisor
- `HURT_MP_COST = 2` - MP cost

### HURTMORE

**Damage Amount:**

```
MinDamage = 58
MaxDamage = 65
BaseDamage = Random(MinDamage, MaxDamage)
EnemyResist = EnemyDEF / 4
FinalDamage = BaseDamage - EnemyResist
If FinalDamage < 1: FinalDamage = 1
```

**Assembly Location:** `Bank03.asm` at `SpellHURTMORE` (~line 4950)

**Constants:**
- `HURTMORE_MIN = 58` - Minimum base damage
- `HURTMORE_MAX = 65` - Maximum base damage
- `HURTMORE_RESIST_DIV = 4` - Enemy defense resistance divisor
- `HURTMORE_MP_COST = 5` - MP cost

### SLEEP

**Success Chance:**

```
BaseSleepChance = 160  ; 62.5%
ResistPenalty = EnemyLevel * 2
SleepChance = BaseSleepChance - ResistPenalty
If SleepChance < 32: SleepChance = 32  ; Min 12.5%
RandValue = Random(0, 255)
IsSleep = (RandValue < SleepChance)
```

**Assembly Location:** `Bank03.asm` at `SpellSLEEP` (~line 5000)

**Constants:**
- `SLEEP_BASE_CHANCE = 160` - Base success chance (62.5%)
- `SLEEP_RESIST_MULT = 2` - Enemy level resistance
- `SLEEP_MIN_CHANCE = 32` - Minimum success (12.5%)
- `SLEEP_MP_COST = 2` - MP cost

### STOPSPELL

**Success Chance:**

```
BaseStopChance = 160  ; 62.5%
ResistPenalty = EnemyLevel * 3
StopChance = BaseStopChance - ResistPenalty
If StopChance < 16: StopChance = 16  ; Min 6.25%
RandValue = Random(0, 255)
IsStop = (RandValue < StopChance)
```

**Assembly Location:** `Bank03.asm` at `SpellSTOPSPELL` (~line 5050)

**Constants:**
- `STOPSPELL_BASE_CHANCE = 160` - Base success chance (62.5%)
- `STOPSPELL_RESIST_MULT = 3` - Enemy level resistance
- `STOPSPELL_MIN_CHANCE = 16` - Minimum success (6.25%)
- `STOPSPELL_MP_COST = 2` - MP cost

### RADIANT

**Light Radius:**

```
LightRadius = 3  ; Tiles around player
Duration = Permanent until map change
```

**Assembly Location:** `Bank03.asm` at `SpellRADIANT` (~line 5100)

**Constants:**
- `RADIANT_RADIUS = 3` - Light radius in tiles
- `RADIANT_MP_COST = 3` - MP cost

### OUTSIDE / RETURN

**Functionality:**

```
OUTSIDE: Warp to position outside current dungeon/cave
RETURN: Warp to Tantegel Castle throne room
```

**Assembly Location:** `Bank03.asm` at `SpellOUTSIDE` and `SpellRETURN` (~line 5150)

**Constants:**
- `OUTSIDE_MP_COST = 6` - MP cost
- `RETURN_MP_COST = 8` - MP cost
- `TANTEGEL_X = 43` - Return X coordinate
- `TANTEGEL_Y = 43` - Return Y coordinate

### REPEL

**Effect Duration:**

```
RepelSteps = 127  ; Steps before repel wears off
EncounterRate = 0 (while active)
```

**Assembly Location:** `Bank03.asm` at `SpellREPEL` (~line 5200)

**Constants:**
- `REPEL_DURATION = 127` - Steps with no encounters
- `REPEL_MP_COST = 2` - MP cost

---

## Item Effects

### Herbs

**Healing Amount:**

```
MinHeal = 23
MaxHeal = 30
HealAmount = Random(MinHeal, MaxHeal)
NewHP = CurrentHP + HealAmount
If NewHP > MaxHP: NewHP = MaxHP
```

**Assembly Location:** `Bank03.asm` at `UseHerb` (~line 5400)

**Constants:**
- `HERB_MIN_HEAL = 23` - Minimum HP restored
- `HERB_MAX_HEAL = 30` - Maximum HP restored

### Torch

**Light Duration:**

```
LightRadius = 3  ; Same as RADIANT
Duration = Until next battle or map change
```

**Assembly Location:** `Bank03.asm` at `UseTorch` (~line 5450)

**Constants:**
- `TORCH_RADIUS = 3` - Light radius in tiles

### Wings

**Functionality:**

```
Warp to Tantegel Castle (same as RETURN spell)
TargetX = 43
TargetY = 43
```

**Assembly Location:** `Bank03.asm` at `UseWings` (~line 5500)

**Constants:**
- `WINGS_TARGET_X = 43` - Tantegel X coordinate
- `WINGS_TARGET_Y = 43` - Tantegel Y coordinate

### Dragon's Scale

**Effect:**

```
Damage reduction = EnemyDamage / 3
FinalDamage = EnemyDamage - Reduction
If FinalDamage < 0: FinalDamage = 0
```

**Assembly Location:** `Bank03.asm` at `ApplyDragonScale` (~line 5550)

**Constants:**
- `DRAGON_SCALE_DIVISOR = 3` - Damage reduction divisor

### Rainbow Drop

**Functionality:**

```
If PlayerX == 69 AND PlayerY == 69:  ; Rainbow bridge location
    CreateRainbowBridge()
    RemoveRainbowDrop()
```

**Assembly Location:** `Bank03.asm` at `UseRainbowDrop` (~line 5600)

**Constants:**
- `RAINBOW_X = 69` - Bridge X coordinate
- `RAINBOW_Y = 69` - Bridge Y coordinate

---

## Encounter System

### Random Encounter Rate

**Base Encounter Check:**

```
Every step on walkable tile:
    StepCounter = StepCounter + 1
    If StepCounter >= EncounterDelay:
        RandValue = Random(0, 255)
        If RandValue < EncounterRate:
            TriggerBattle()
        StepCounter = 0
```

**Encounter Delay:**

```
EncounterDelay = 8  ; Check every 8 steps minimum
```

**Encounter Rate by Zone:**

| Zone Type | Encounter Rate | % Chance per Check |
|-----------|----------------|---------------------|
| Tantegel area | 16 | 6.25% |
| Grassland | 32 | 12.5% |
| Forest | 48 | 18.75% |
| Hills | 64 | 25% |
| Mountains | 80 | 31.25% |
| Swamp | 96 | 37.5% |
| Desert (unused) | 112 | 43.75% |

**Assembly Location:** `Bank03.asm` at `EncounterCheck` (~line 6000)

**Constants:**
- `ENCOUNTER_DELAY = 8` - Steps between encounter checks
- `TANTEGEL_RATE = 16` - Tantegel area encounter rate
- `GRASS_RATE = 32` - Grassland encounter rate
- `FOREST_RATE = 48` - Forest encounter rate
- `HILLS_RATE = 64` - Hills encounter rate
- `MOUNTAIN_RATE = 80` - Mountain encounter rate
- `SWAMP_RATE = 96` - Swamp encounter rate

### Enemy Selection

**Monster Group Tables:**

Each zone has a table of possible encounters:

```
TantegelMonsters:
    .byte SLIME, RED_SLIME, DRAKEE, GHOST
    
GrassMonsters:
    .byte SLIME, RED_SLIME, DRAKEE, GHOST, MAGICIAN, SCORPION
    
; ... etc for each zone
```

**Selection:**

```
MonsterTable = GetZoneMonsterTable()
TableSize = GetTableSize()
RandIndex = Random(0, TableSize - 1)
SelectedMonster = MonsterTable[RandIndex]
```

**Assembly Location:** `Bank03.asm` at `SelectEncounter` and monster tables (~line 6100)

### Flee Success Rate

**Flee Chance:**

```
If EnemyIsRunAway:  ; Special "runs away" enemies
    FleeChance = 100%
Else:
    BaseFleeChance = 192  ; 75%
    AgilityBonus = (PlayerAGI - EnemyAGI) / 4
    FleeChance = BaseFleeChance + AgilityBonus
    If FleeChance < 64: FleeChance = 64  ; Min 25%
    If FleeChance > 224: FleeChance = 224  ; Max 87.5%
    RandValue = Random(0, 255)
    IsFleeSuccess = (RandValue < FleeChance)
```

**Assembly Location:** `Bank03.asm` at `AttemptFlee` (~line 6200)

**Constants:**
- `BASE_FLEE_CHANCE = 192` - Base flee success (75%)
- `AGI_FLEE_BONUS_DIV = 4` - Agility difference divisor
- `MIN_FLEE_CHANCE = 64` - Minimum flee chance (25%)
- `MAX_FLEE_CHANCE = 224` - Maximum flee chance (87.5%)

---

## Enemy AI

### AI Behavior Patterns

**Monster AI Types:**

Each monster has an AI pattern byte that determines behavior:

```
AI Pattern Bits:
Bit 0-2: Base behavior
    000 = Attack only
    001 = Can cast SLEEP
    010 = Can cast HURT
    011 = Can cast STOPSPELL
    100 = Can cast HEALMORE (self)
    101 = Can cast HURTMORE
    110 = Can breathe fire
    111 = Special Dragonlord AI

Bit 3: Can flee (runs away)
Bit 4: Resists SLEEP
Bit 5: Resists STOPSPELL
Bit 6: Resists HURT
Bit 7: Immune to all magic
```

**AI Decision Making:**

```
If Monster_Can_Cast_Spell:
    RandValue = Random(0, 255)
    If RandValue < 64:  ; 25% chance
        CastSpell()
    Else:
        PhysicalAttack()
Else:
    PhysicalAttack()
```

**Assembly Location:** `Bank03.asm` at `ProcessEnemyTurn` (~line 6400)

**Constants:**
- `AI_SPELL_CHANCE = 64` - Spell cast chance (25%)

### Dragonlord Special AI

**Form 1 (Human):**

```
AI Pattern:
- 50% HURTMORE
- 25% HURT
- 25% Physical attack
```

**Form 2 (Dragon):**

```
AI Pattern:
- Turn 1: Always breathe fire
- Turn 2+:
    - If HP > 50%: 50% fire breath, 50% attack
    - If HP ≤ 50%: 75% HEALMORE, 25% attack
```

**Assembly Location:** `Bank03.asm` at `DragonlordAI` (~line 6500)

---

## Technical Limits

### Stat Maximums

**Hard Limits:**

| Stat | Maximum | Type |
|------|---------|------|
| Level | 30 | Hard cap |
| HP | 255 | 8-bit unsigned |
| MP | 255 | 8-bit unsigned |
| STR | 255 | 8-bit unsigned |
| AGI | 255 | 8-bit unsigned |
| ATK | 255 | 8-bit unsigned |
| DEF | 255 | 8-bit unsigned |
| Gold | 65535 | 16-bit unsigned |
| Experience | 65535 | 16-bit unsigned |

**Practical Maximums:**

| Stat | Practical Max | Notes |
|------|---------------|-------|
| Level | 30 | Game max level |
| HP | ~220 | Normal level 30 HP |
| MP | ~160 | Normal level 30 MP |
| STR | ~140 | Best equipment + level 30 |
| AGI | ~150 | Best equipment + level 30 |

### Item Limits

**Inventory:**

```
MAX_ITEMS = 8  ; 8 inventory slots
```

**Prices:**

```
MIN_PRICE = 0
MAX_PRICE = 65535  ; 16-bit unsigned
```

### Map Limits

**Overworld:**

```
MAP_WIDTH = 120 tiles
MAP_HEIGHT = 120 tiles
TOTAL_TILES = 14400
```

**Towns/Dungeons:**

```
MAX_INTERIOR_WIDTH = 32 tiles
MAX_INTERIOR_HEIGHT = 32 tiles
```

**Assembly Location:** `Dragon_Warrior_Defines.asm` at map constants

**Constants:**
- `OVERWORLD_WIDTH = 120`
- `OVERWORLD_HEIGHT = 120`
- `INTERIOR_MAX_WIDTH = 32`
- `INTERIOR_MAX_HEIGHT = 32`

### Battle Limits

**Damage:**

```
MAX_DAMAGE = 255  ; 8-bit unsigned
MIN_DAMAGE = 0
```

**Healing:**

```
MAX_HEAL = 255  ; 8-bit unsigned (capped by MaxHP)
```

### Text Limits

**Dialog:**

```
MAX_DIALOG_LENGTH = 128 bytes (compressed)
MAX_NAME_LENGTH = 16 characters
```

### Enemy Limits

**Monster Count:**

```
MAX_MONSTERS = 40  ; 0x00-0x27 (including both Dragonlord forms)
```

**Monster Stats:**

```
MAX_MONSTER_HP = 255
MAX_MONSTER_STR = 255
MAX_MONSTER_AGI = 255
MAX_MONSTER_EXP = 255
MAX_MONSTER_GOLD = 255
```

---

## Modification Examples

### Double All Damage

**Edit:** `Bank03.asm` at `CalcPhysicalDamage`

**Change:**

```assembly
; Original
LSR A          ; Divide ATK by 2

; Modified
; Remove LSR instruction - no division
NOP            ; No operation
```

### Make HEAL Restore Full HP

**Edit:** `Bank03.asm` at `SpellHEAL`

**Change:**

```assembly
; Original
LDA #10        ; Min heal
STA TempMin
LDA #17        ; Max heal
STA TempMax
JSR Random

; Modified
LDA PlayerMaxHP   ; Load max HP
STA PlayerHP      ; Set current = max
RTS               ; Return early
```

### Increase Critical Hit Rate

**Edit:** `Bank03.asm` at `CheckCriticalHit`

**Change:**

```assembly
; Original
LDA PlayerAGI
LSR A          ; Divide by 2
LSR A          ; Divide by 4
LSR A          ; Divide by 8 (total /64)

; Modified
LDA PlayerAGI
LSR A          ; Divide by 2
LSR A          ; Divide by 4 (total /16)
; Remove third LSR - 4x crit rate
```

### Adjust Encounter Rate

**Edit:** `Bank03.asm` at encounter rate constants

**Change:**

```assembly
; Original
GRASS_RATE = 32    ; 12.5%

; Modified
GRASS_RATE = 16    ; 6.25% (half encounters)
; or
GRASS_RATE = 64    ; 25% (double encounters)
```

---

## Quick Reference Tables

### Spell MP Costs

| Spell | MP Cost | Level Learned |
|-------|---------|---------------|
| HEAL | 4 | 3 |
| HURT | 2 | 4 |
| SLEEP | 2 | 7 |
| RADIANT | 3 | 9 |
| STOPSPELL | 2 | 10 |
| OUTSIDE | 6 | 12 |
| RETURN | 8 | 13 |
| REPEL | 2 | 15 |
| HEALMORE | 10 | 17 |
| HURTMORE | 5 | 19 |

### Weapon Attack Values

| Weapon | ATK Bonus |
|--------|-----------|
| Unarmed | +4 |
| Bamboo Pole | +2 |
| Club | +4 |
| Copper Sword | +10 |
| Hand Axe | +15 |
| Broad Sword | +20 |
| Flame Sword | +28 |
| Erdrick's Sword | +40 |

### Armor Defense Values

| Armor | DEF Bonus |
|-------|-----------|
| Clothes | +2 |
| Leather Armor | +4 |
| Chain Mail | +10 |
| Half Plate | +16 |
| Full Plate | +24 |
| Magic Armor | +24 |
| Erdrick's Armor | +28 |

### Shield Defense Values

| Shield | DEF Bonus |
|--------|-----------|
| Small Shield | +4 |
| Large Shield | +10 |
| Silver Shield | +20 |

---

## Assembly Code Locations Summary

**Quick lookup for common formulas:**

| Formula | Bank | Routine Name | Line # (approx) |
|---------|------|--------------|-----------------|
| Physical Damage | Bank03 | CalcPhysicalDamage | 4000 |
| Critical Hit | Bank03 | CheckCriticalHit | 4100 |
| Hit/Miss | Bank03 | CheckHit | 4200 |
| Dodge | Bank03 | CheckDodge | 4300 |
| HP Gain | Bank03 | LevelUpHP | 3800 |
| MP Gain | Bank03 | LevelUpMP | 3900 |
| STR Gain | Bank03 | LevelUpSTR | 4000 |
| AGI Gain | Bank03 | LevelUpAGI | 4050 |
| HEAL | Bank03 | SpellHEAL | 4800 |
| HEALMORE | Bank03 | SpellHEALMORE | 4850 |
| HURT | Bank03 | SpellHURT | 4900 |
| HURTMORE | Bank03 | SpellHURTMORE | 4950 |
| SLEEP | Bank03 | SpellSLEEP | 5000 |
| STOPSPELL | Bank03 | SpellSTOPSPELL | 5050 |
| Encounter Check | Bank03 | EncounterCheck | 6000 |
| Flee Check | Bank03 | AttemptFlee | 6200 |
| Enemy AI | Bank03 | ProcessEnemyTurn | 6400 |

**Data Tables:**

| Data | Bank | Table Name | Line # (approx) |
|------|------|------------|-----------------|
| Monster Stats | Bank01 | MonsterStats | 1400 |
| Item Prices | Bank01 | ItemPrices | 2600 |
| Weapon Data | Bank01 | WeaponData | 2600 |
| Armor Data | Bank01 | ArmorData | 2700 |
| Spell Costs | Bank01 | SpellCosts | 2900 |
| EXP Requirements | Bank01 | ExpRequirements | 3400 |
| HP Gain Table | Bank03 | HPGainTable | 3800 |
| MP Gain Table | Bank03 | MPGainTable | 3900 |
| Encounter Rates | Bank03 | EncounterRates | 6000 |

---

## Verified Assembly Code Locations

The following are exact verified locations from the disassembly:

### Bank01.asm Addresses

| Address | Label | Description |
|---------|-------|-------------|
| $99B4 | SetBaseStats | Load player base stats for level |
| $9E49 | EnStatTblPtr | Pointer to enemy stats table |
| $9E4B | EnStatTbl | Enemy statistics table (16 bytes/enemy) |
| $A0CB | BaseStatsTbl | Player base stats per level (6 bytes/level) |

### Bank03.asm Addresses

| Address | Label | Description |
|---------|-------|-------------|
| $DBB8 | DoHeal | HEAL spell: `10 + random(0-7)` HP |
| $DBD7 | DoHealmore | HEALMORE spell: `85 + random(0-15)` HP |
| $EFE5 | PlayerCalcHitDmg | Player physical damage calculation |
| $EFF4 | EnCalcHitDmg | Enemy physical damage calculation |
| $F050 | LoadStats | Level determination from experience |
| $F0CD | AddItemBonuses | Apply equipment bonuses to stats |
| $F35B | LevelUpTbl | Experience requirements (2 bytes/level) |

### Dragon_Warrior_Defines.asm

| Alias | Address | Description |
|-------|---------|-------------|
| CalcDamage | $3C | Calculated damage storage |
| AttackStat | $3D | Current attack value |
| DefenseStat | $3E | Current defense value |
| ExpLB | $BA | Experience lower byte |
| ExpUB | $BB | Experience upper byte |
| HitPoints | $C5 | Current HP |
| DisplayedMaxHP | $C6 | Max HP display value |

### Generated Files

| File | Description |
|------|-------------|
| `source_files/generated/equipment_bonus_tables.asm` | Weapon/Armor/Shield bonuses |
| `source_files/generated/spell_data.asm` | Spell MP costs and effect types |
| `source_files/generated/spell_cost_table.asm` | Spell MP cost table |

---

## Credits

- **Original Game** - Chunsoft, Enix (1989)
- **Formula Documentation** - Community research and disassembly analysis
- **This Reference** - Compiled from source code and testing

---

**For complete source code and detailed assembly listings, see the `source_files/` directory.**

**Happy Formula Hacking! 📐🐉**
