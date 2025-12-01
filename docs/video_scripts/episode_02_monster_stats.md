# Episode 2: Modifying Monster Stats

## Video Metadata

| Field | Value |
|-------|-------|
| **Title** | "Dragon Warrior ROM Hacking: Make Slimes TERRIFYING!" |
| **Duration** | 8-10 minutes |
| **Difficulty** | Beginner |
| **Prerequisites** | Completed Episode 1, Working build environment |
| **Related Docs** | `docs/MODIFICATION_EXAMPLES.md`, `assets/json/monsters.json` |

---

## Chapter Markers (YouTube Timestamps)

```text
0:00 - Introduction
0:30 - Understanding Monster Data
1:30 - Opening the JSON File
2:30 - Creating Our Super Slime
4:00 - Regenerating Assets
5:00 - Building & Testing
6:30 - Using the Universal Editor
8:00 - Advanced: Batch Modifications
9:00 - Closing
```

---

## Full Script

### [0:00] Introduction (30 seconds)

**[VISUAL: Red Slime battle in emulator, hero getting demolished, transition to monsters.json]**

**NARRATION:**
> "Hey everyone! Welcome back to Dragon Warrior ROM Hacking! In our last video, we got everything set up and running. Now it's time to make our first REAL change to the game.
>
> We're going to turn the humble Slime - that cute little blue blob that's basically free XP - into an absolute NIGHTMARE. By the end of this video, you'll know how to make any monster as easy or as brutally difficult as you want.
>
> Let's break some game balance!"

---

### [0:30] Understanding Monster Data (1 minute)

**[VISUAL: monsters.json structure on screen, highlight key fields with callout boxes]**

**NARRATION:**
> "Dragon Warrior has 40 monsters total, from the lowly Slime to the mighty Dragonlord. Each one has these stats:
>
> - **Strength** - How hard they punch. Higher = ouchie.
> - **Agility** - Who goes first AND how often they dodge your attacks
> - **HP** - The health pool. You gotta drain this to win!
> - **Sleep Resist** - Can they shrug off your SLEEP spell?
> - **Stopspell Resist** - Can they ignore your STOPSPELL?
> - **Hurt Resist** - Protection against HURT and HURTMORE
> - **Experience** - What you get for killing them
> - **Gold** - What they drop (monsters carry coins, don't question it)
>
> All of this lives in `assets/json/monsters.json` - human-readable JSON, not cryptic hex codes!"

**[VISUAL: Side-by-side comparison of hex data vs JSON - dramatically easier to read]**

---

### [1:30] Opening the JSON File (1 minute)

**[VISUAL: VS Code opening monsters.json with smooth animation]**

**NARRATION:**
> "Let's crack open that monster data! In VS Code, hit Ctrl+P and type `monsters.json` to quick-open it.
>
> Scroll through and... look at all these monsters! Each one is a JSON object with all their stats laid out clearly. Let's find our victim - er, subject. The Slime!"

**[VISUAL: Scroll to Slime entry, zoom in with highlight effect]**

```json
{
  "name": "Slime",
  "id": 0,
  "strength": 5,
  "agility": 3,
  "hp_min": 2,
  "hp_max": 3,
  "experience": 1,
  "gold": 2
}
```

> "Look at these pathetic numbers! Strength 5, HP 2-3... this thing dies if you sneeze at it. Time to fix that!"

---

### [2:30] Creating Our Super Slime (1 minute 30 seconds)

**[VISUAL: Editing JSON in VS Code with typing sounds]**

**NARRATION:**
> "Alright, let's create our SUPER SLIME! I'm going to crank these stats way up:"

**[VISUAL: Type changes live with dramatic zoom]**

```json
{
  "name": "Slime",
  "id": 0,
  "strength": 20,
  "agility": 15,
  "hp_min": 10,
  "hp_max": 15,
  "experience": 5,
  "gold": 10
}
```

> "Check out these changes:
>
> - Strength from 5 to 20 - this blob now hits like a truck!
> - Agility from 3 to 15 - good luck hitting it, AND it goes first
> - HP from 2-3 to 10-15 - no more one-shotting these guys
> - Experience from 1 to 5 - at least you get rewarded for the pain
> - Gold from 2 to 10 - they're carrying more treasure now
>
> Save the file with Ctrl+S. Our Slime is ready to terrorize some heroes!"

---

### [4:00] Regenerating Assets (1 minute)

**[VISUAL: Terminal running generate command]**

**NARRATION:**
> "Now we need to convert our JSON changes into assembly code. The project does this automatically, but let's see it happen.
>
> Open PowerShell in the project folder and run:"

```powershell
python tools/generate_all_assets.py
```

> "This regenerates all the assembly include files from JSON. You'll see it process monsters, items, spells, and everything else.
>
> Look for the 'monsters' line - it should say 'succeeded'."

**[VISUAL: Terminal output showing successful generation]**

---

### [5:00] Building & Testing (1 minute 30 seconds)

**[VISUAL: Build process, then emulator]**

**NARRATION:**
> "Now let's build and test. Run:"

```powershell
.\build.ps1
```

> "The build script automatically regenerates assets and assembles the ROM.
>
> Once it completes, open the built ROM in your emulator."

**[VISUAL: Emulator loading, start new game]**

> "Start a new game and head outside to fight a Slime..."

**[VISUAL: Battle with modified Slime]**

> "Look at that! The Slime now hits harder and takes more damage. We turned the game's pushover into a real threat!
>
> The experience and gold rewards are higher too - check your stats after winning."

---

### [6:30] Using the Universal Editor (1 minute 30 seconds)

**[VISUAL: Universal Editor opening]**

**NARRATION:**
> "Editing JSON is fine, but the project includes a graphical editor that makes it even easier. Run:"

```powershell
python tools/universal_editor.py
```

> "This opens the Universal Editor with tabs for everything - monsters, items, spells, shops, and more."

**[VISUAL: Navigate to Monster tab]**

> "Click the Monster Stats tab. You'll see all 40 monsters listed. Select one and you can change any stat with spinboxes and dropdowns.
>
> The editor validates your changes and saves directly to the JSON file."

**[VISUAL: Editing a monster, saving]**

> "After editing, just run the build script again to see your changes."

---

### [8:00] Advanced: Batch Modifications (1 minute)

**[VISUAL: Python script example]**

**NARRATION:**
> "Want to make sweeping changes? You can write Python scripts to modify the JSON programmatically.
>
> For example, to double all monster HP:"

```python
import json
with open('assets/json/monsters.json', 'r') as f:
    data = json.load(f)

for monster in data['monsters']:
    monster['hp_min'] *= 2
    monster['hp_max'] *= 2

with open('assets/json/monsters.json', 'w') as f:
    json.dump(data, f, indent=2)
```

> "This is great for difficulty mods or total conversions where you want to scale everything at once."

---

### [9:00] Closing (30-45 seconds)

**[VISUAL: End card with links]**

**NARRATION:**
> "You've just made your first Dragon Warrior mod! You learned how to:
>
> - Edit monster stats in JSON
> - Regenerate assets and build
> - Use the Universal Editor
> - Make batch modifications with scripts
>
> In the next video, we'll explore graphics editing - changing how monsters and tiles look.
>
> If you enjoyed this, like and subscribe for more tutorials. See you next time!"

---

## Video Description Template

```text
🎮 Dragon Warrior ROM Hacking: Modifying Monster Stats

Learn how to change monster statistics in Dragon Warrior! From a simple JSON edit to using the Universal Editor, this tutorial covers everything you need to rebalance the game.

📋 TIMESTAMPS:
0:00 - Introduction
0:30 - Understanding Monster Data
1:30 - Opening the JSON File
2:30 - Changing Slime Stats
4:00 - Regenerating Assets
5:00 - Building & Testing
6:30 - Using the Universal Editor
8:00 - Advanced: Batch Modifications
9:00 - Closing

📁 FILES MODIFIED:
• assets/json/monsters.json - Monster stat definitions

⌨️ COMMANDS USED:
```powershell
# Regenerate assets
python tools/generate_all_assets.py

# Build ROM
.\build.ps1

# Open Universal Editor
python tools/universal_editor.py

📺 SERIES:
• Ep 1: Getting Started: [LINK]
• Ep 3: Graphics Editing: [COMING SOON]

TAGS: DragonWarrior, NES, ROMHacking, Modding, Tutorial
```

---

## Production Notes

### Key Footage Needed

- [ ] Before/after Slime battle comparison
- [ ] JSON editing close-up
- [ ] Universal Editor monster tab demo
- [ ] Build output success

### Monster Stat Ranges

For reference when demonstrating:

- Strength: 5-180
- Agility: 3-200
- HP: 2-230
- Resistances: 0-15

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-02 | 1.0 | Initial script creation |
