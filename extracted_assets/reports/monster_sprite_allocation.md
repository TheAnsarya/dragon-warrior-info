# Dragon Warrior Monster Sprite Allocation Report

## Summary

- **Total Monsters:** 39
- **Unique Sprite Definitions:** 19
- **Total Unique Tiles:** 252
- **Average Tiles per Sprite:** 13.26
- **Max Monsters Sharing One Sprite:** 3
- **Sprite Reuse:** 20 monsters reuse sprites

## Correction Note

IMPORTANT: Previous documentation incorrectly stated '64 tiles for 64 different monsters'. In reality, 39 monsters use 19 unique sprite definitions comprising 252 total tiles. Sprite sharing is extensive - for example, SlimeSprts (8 tiles) is shared by Slime, Red Slime, and Metal Slime.

## Sprite Definitions

| Sprite Name | Tile Count | Monsters Using | Monster Names |
|-------------|------------|----------------|---------------|
| ArKntSprts | 4 | 1 | Armored Knight |
| AxKntSprts | 6 | 1 | Axe Knight |
| DKnightSprts | 4 | 2 | Wraith Knight, Demon Knight |
| DgLdSprts | 22 | 1 | Dragonlord (Form 1) |
| DgnSprts | 9 | 1 | Green Dragon |
| DrakeeSprts | 10 | 3 | Drakee, Magidrakee, Drakeema |
| DrollSprts | 11 | 2 | Droll, Drollmagi |
| DruinSprts | 11 | 2 | Druin, Druinlord |
| GhstSprts | 13 | 3 | Ghost, Poltergeist, Specter |
| GolemSprts | 31 | 3 | Golem, Goldman, Stoneman |
| KntSprts | 31 | 1 | Knight |
| MagSprts | 4 | 1 | Magician |
| RBDgnSprts | 2 | 2 | Blue Dragon, Red Dragon |
| ScorpSprts | 17 | 3 | Scorpion, Metal Scorpion, Rouge Scorpion |
| SkelSprts | 14 | 2 | Skeleton, Wraith |
| SlimeSprts | 8 | 3 | Slime, Red Slime, Metal Slime |
| WizSprts | 4 | 2 | Warlock, Wizard |
| WolfSprts | 30 | 3 | Wolf, Wolflord, Werewolf |
| WyvrnSprts | 21 | 3 | Wyvern, Magiwyvern, Starwyvern |

## Sprite Sharing Details


### Sprites Shared by 3 Monsters

- **DrakeeSprts** (10 tiles): Drakee, Magidrakee, Drakeema
- **GhstSprts** (13 tiles): Ghost, Poltergeist, Specter
- **GolemSprts** (31 tiles): Golem, Goldman, Stoneman
- **ScorpSprts** (17 tiles): Scorpion, Metal Scorpion, Rouge Scorpion
- **SlimeSprts** (8 tiles): Slime, Red Slime, Metal Slime
- **WolfSprts** (30 tiles): Wolf, Wolflord, Werewolf
- **WyvrnSprts** (21 tiles): Wyvern, Magiwyvern, Starwyvern

### Sprites Shared by 2 Monsters

- **DKnightSprts** (4 tiles): Wraith Knight, Demon Knight
- **DrollSprts** (11 tiles): Droll, Drollmagi
- **DruinSprts** (11 tiles): Druin, Druinlord
- **RBDgnSprts** (2 tiles): Blue Dragon, Red Dragon
- **SkelSprts** (14 tiles): Skeleton, Wraith
- **WizSprts** (4 tiles): Warlock, Wizard

### Unique Sprites (1 Monster Each)

- **ArKntSprts** (4 tiles): Armored Knight
- **AxKntSprts** (6 tiles): Axe Knight
- **DgLdSprts** (22 tiles): Dragonlord (Form 1)
- **DgnSprts** (9 tiles): Green Dragon
- **KntSprts** (31 tiles): Knight
- **MagSprts** (4 tiles): Magician
