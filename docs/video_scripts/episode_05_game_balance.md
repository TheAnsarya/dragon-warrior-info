# Episode 5: Game Balance and Difficulty Adjustments

## Video Metadata

| Field | Value |
|-------|-------|
| **Title** | "Dragon Warrior ROM Hacking: Game Balance and Difficulty" |
| **Duration** | 10-12 minutes |
| **Difficulty** | Beginner-Intermediate |
| **Prerequisites** | Completed Episode 1, Episode 2 helpful |
| **Related Docs** | `docs/technical/GAME_FORMULAS.md`, `assets/json/` |

---

## Chapter Markers (YouTube Timestamps)

```
0:00 - Introduction
0:45 - Understanding Game Balance
1:45 - Experience Curves
3:15 - Shop Prices and Gold Drops
5:00 - Spell Effects and Costs
6:30 - Equipment Bonuses
7:45 - Creating a Difficulty Mod
9:30 - Testing Balance Changes
10:30 - Closing
```

---

## Full Script

### [0:00] Introduction (45 seconds)

**[VISUAL: Gameplay showing grinding, shop purchases, level up]**

**NARRATION:**
> "Dragon Warrior is infamous for its grinding. Hours spent fighting Slimes outside Tantegel just to afford a Copper Sword. We've all been there - and honestly, that's part of what makes the victory so sweet.
>
> But what if you could change that? What if you could tailor the experience to your exact preferences? In this episode, we'll adjust:
>
> - Experience curves for faster leveling
> - Gold drops and shop prices
> - Spell costs and effects
> - Equipment bonuses
>
> Whether you want an easier first playthrough for a friend, or a brutal challenge run that would make even the original developers cry, let's dive in!"

---

### [0:45] Understanding Game Balance (1 minute)

**[VISUAL: Balance diagram showing interconnected systems]**

**NARRATION:**
> "Game balance in Dragon Warrior involves interconnected systems:
>
> - **Experience** determines leveling speed
> - **Gold** determines equipment progression  
> - **Spells** provide strategic options
> - **Equipment** provides stat boosts
>
> Changing one affects the others. Double gold drops? Players get equipment earlier, making the game easier.
>
> Let's look at each system individually."

---

### [1:45] Experience Curves (1 minute 30 seconds)

**[VISUAL: experience_table.json in VS Code]**

**NARRATION:**
> "The experience table defines how much XP each level requires. Open `assets/json/experience_table.json`:"

```json
{
  "levels": [
    {"level": 1, "total_exp": 0},
    {"level": 2, "total_exp": 7},
    {"level": 3, "total_exp": 23},
    {"level": 4, "total_exp": 47},
    {"level": 5, "total_exp": 110}
  ]
}
```

> "Each level has a total XP requirement. Level 2 needs only 7, but by level 10 you need thousands.
>
> To make leveling faster, reduce these numbers. To make it harder, increase them."

**[VISUAL: Edit some values]**

> "Let's cut them in half for a 'Quick Play' mod:"

```python
# Quick script to halve all XP requirements
import json
with open('assets/json/experience_table.json', 'r') as f:
    data = json.load(f)
for level in data['levels']:
    level['total_exp'] //= 2
with open('assets/json/experience_table.json', 'w') as f:
    json.dump(data, f, indent=2)
```

---

### [3:15] Shop Prices and Gold Drops (1 minute 45 seconds)

**[VISUAL: shops.json and monsters.json side by side]**

**NARRATION:**
> "Gold economy involves two files:
>
> - `assets/json/monsters.json` - Gold dropped by each enemy
> - `assets/json/shops.json` - Item prices in shops
>
> Let's look at shops:"

```json
{
  "shop_id": "BRECCONARY",
  "items": [
    {"item": "Club", "price": 60},
    {"item": "Copper Sword", "price": 180},
    {"item": "Clothes", "price": 20}
  ]
}
```

> "The Copper Sword costs 180 gold. Slimes drop 2 gold. That's 90 Slime fights minimum!
>
> Let's rebalance:"

**[VISUAL: Edit values]**

```json
{"item": "Copper Sword", "price": 90}
```

> "Half the price, half the grind. Or increase monster gold drops instead:"

```json
{"name": "Slime", "gold": 5}
```

> "Now you only need 18 Slime fights. Pick whichever feels right for your mod."

---

### [5:00] Spell Effects and Costs (1 minute 30 seconds)

**[VISUAL: spells.json in VS Code]**

**NARRATION:**
> "Spells are defined in `assets/json/spells.json`:
>
> - **MP cost** - How expensive to cast
> - **Effect power** - Damage, healing amount, etc.
> - **Level learned** - When the hero learns it"

```json
{
  "name": "HEAL",
  "mp_cost": 4,
  "effect": "heal",
  "power": 10,
  "level_learned": 3
}
```

> "HEAL costs 4 MP and heals about 10 HP. Want a stronger early game? Reduce MP costs or increase power:"

**[VISUAL: Edit spell]**

```json
{
  "name": "HEAL",
  "mp_cost": 2,
  "effect": "heal", 
  "power": 15,
  "level_learned": 2
}
```

> "Now HEAL costs half as much, heals 50% more, and you learn it at level 2!"

**[VISUAL: spell_effects.json briefly]**

> "For advanced spell mechanics, check `assets/json/spell_effects.json`."

---

### [6:30] Equipment Bonuses (1 minute 15 seconds)

**[VISUAL: equipment_bonuses.json]**

**NARRATION:**
> "Equipment bonuses determine how much attack and defense each item provides. Open `assets/json/equipment_bonuses.json`:"

```json
{
  "weapons": [
    {"name": "Bamboo Pole", "attack": 2},
    {"name": "Club", "attack": 4},
    {"name": "Copper Sword", "attack": 10}
  ],
  "armor": [
    {"name": "Clothes", "defense": 2},
    {"name": "Leather Armor", "defense": 4}
  ]
}
```

> "Want the early game to be more survivable? Boost starting equipment:"

```json
{"name": "Clothes", "defense": 5}
```

> "Or make end-game equipment truly godlike for power fantasy mods."

---

### [7:45] Creating a Difficulty Mod (1 minute 45 seconds)

**[VISUAL: Universal Editor tabs showing multiple changes]**

**NARRATION:**
> "Let's combine everything into a complete 'Easy Mode' mod:
>
> 1. **Experience**: Halve all requirements
> 2. **Gold**: Double all monster gold drops
> 3. **Shops**: Reduce prices by 25%
> 4. **Spells**: Reduce all MP costs by 1
> 5. **Equipment**: +2 to all defensive equipment
>
> You can make these changes manually or write a script to automate it."

**[VISUAL: Show running a batch modification script]**

```powershell
python tools/apply_difficulty_preset.py --preset easy
```

> "The project could include preset scripts for common modifications. Community members often share their balance patches!"

---

### [9:30] Testing Balance Changes (1 minute)

**[VISUAL: Side-by-side gameplay comparison]**

**NARRATION:**
> "After making changes, rebuild and test thoroughly.
>
> Start a new game and play for a few levels. Check:
>
> - Is leveling too fast or too slow?
> - Can you afford early equipment reasonably?
> - Are battles challenging but fair?
>
> Balance is subjective - test until it feels right for your vision. What feels 'easy' to you might be perfect for someone else."

**[VISUAL: Level up happening quickly, buying equipment easily]**

> "Compare your mod to the original to see the difference clearly."

---

### [10:30] Closing (30-45 seconds)

**[VISUAL: Montage of different difficulty scenarios]**

**NARRATION:**
> "You now control Dragon Warrior's difficulty! Create:
>
> - 'Story Mode' for new players
> - 'Hard Mode' for veterans
> - 'Randomizer' with wild stat changes
> - 'Speedrun' optimized for fast completion
>
> The beauty of ROM hacking is making the game YOUR game. Share your creations with the community!
>
> Next episode goes advanced - we'll look at assembly code modifications for effects that can't be achieved with JSON alone.
>
> Share your difficulty mods in the comments! Like and subscribe for more."

---

## Video Description Template

```text
🎮 Dragon Warrior ROM Hacking: Game Balance and Difficulty

Learn how to adjust Dragon Warrior's difficulty! Modify experience curves, gold drops, shop prices, spell effects, and equipment bonuses to create your perfect game balance.

📋 TIMESTAMPS:
0:00 - Introduction
0:45 - Understanding Game Balance
1:45 - Experience Curves
3:15 - Shop Prices and Gold Drops
5:00 - Spell Effects and Costs
6:30 - Equipment Bonuses
7:45 - Creating a Difficulty Mod
9:30 - Testing Balance Changes
10:30 - Closing

📁 FILES INVOLVED:
• assets/json/experience_table.json - Level requirements
• assets/json/monsters.json - Gold drops, experience rewards
• assets/json/shops.json - Item prices
• assets/json/spells.json - Spell costs and power
• assets/json/equipment_bonuses.json - Weapon/armor stats
• docs/technical/GAME_FORMULAS.md - Damage calculations

💡 QUICK BALANCE TIPS:
• Double gold drops = half the grind
• Halve XP requirements = twice as fast leveling
• Reduce spell MP costs = more magic usage
• Boost early equipment = survivable early game

📺 SERIES:
• Ep 1: Getting Started: [LINK]
• Ep 2: Monster Stats: [LINK]
• Ep 3: Graphics Editing: [LINK]
• Ep 4: Dialog Editing: [LINK]
• Ep 6: Advanced Assembly: [COMING SOON]

TAGS: DragonWarrior, NES, ROMHacking, GameBalance, Tutorial
```

---

## Production Notes

### Gameplay Footage Needed

- [ ] Grinding comparison (original vs modded)
- [ ] Shop purchase with different prices
- [ ] Spell usage with modified costs
- [ ] Level up sequences

### Data for Reference

Prepare these stats for on-screen graphics:

- Original vs Modified XP table (levels 1-10)
- Original vs Modified shop prices
- Spell MP costs comparison

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-02 | 1.0 | Initial script creation |
