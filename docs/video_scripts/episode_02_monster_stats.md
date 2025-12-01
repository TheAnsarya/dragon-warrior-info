# Episode 2: Modifying Monster Stats

## Video Metadata

| Field | Value |
|-------|-------|
| **Title** | "Dragon Warrior ROM Hacking: Modifying Monster Stats" |
| **Duration** | 8-10 minutes |
| **Difficulty** | Beginner |
| **Prerequisites** | Completed Episode 1, Working build environment |
| **Related Docs** | `docs/MODIFICATION_EXAMPLES.md`, `assets/json/monsters.json` |

---

## Chapter Markers (YouTube Timestamps)

```
0:00 - Introduction
0:30 - Understanding Monster Data
1:30 - Opening the JSON File
2:30 - Changing Slime Stats
4:00 - Regenerating Assets
5:00 - Building & Testing
6:30 - Using the Universal Editor
8:00 - Advanced: Batch Modifications
9:00 - Closing
```

---

## Full Script

### [0:00] Introduction (30 seconds)

**[VISUAL: Red Slime battle in emulator, transition to monsters.json]**

**NARRATION:**
> "Welcome back to the Dragon Warrior ROM Hacking series! In our last video, we set up the development environment. Now we're going to make our first real modification - changing monster stats.
>
> By the end of this video, you'll know how to make any monster easier, harder, or completely ridiculous."

---

### [0:30] Understanding Monster Data (1 minute)

**[VISUAL: monsters.json structure on screen, highlight key fields]**

**NARRATION:**
> "Dragon Warrior has 40 monsters, each with these main stats:
>
> - **Strength** - Affects physical attack damage
> - **Agility** - Determines turn order and dodge chance  
> - **HP** - How much damage they can take
> - **Sleep Resist** - Resistance to SLEEP spell
> - **Stopspell Resist** - Resistance to STOPSPELL
> - **Hurt Resist** - Resistance to HURT and HURTMORE
> - **Experience** - XP awarded when defeated
> - **Gold** - Gold dropped when defeated
>
> All of this is stored in `assets/json/monsters.json` in an easy-to-edit format."

**[VISUAL: Show actual JSON highlighting each stat]**

---

### [1:30] Opening the JSON File (1 minute)

**[VISUAL: VS Code opening monsters.json]**

**NARRATION:**
> "Let's open the monster data. In VS Code, navigate to `assets/json/monsters.json`.
>
> You'll see each monster defined with all their properties. Let's look at the Slime - the weakest monster in the game."

**[VISUAL: Scroll to Slime entry, zoom in on stats]**

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

> "Pretty weak, right? Let's make it a bit more interesting."

---

### [2:30] Changing Slime Stats (1 minute 30 seconds)

**[VISUAL: Editing JSON in VS Code]**

**NARRATION:**
> "Let's create a Super Slime! I'm going to bump up its stats:"

**[VISUAL: Type changes live]**

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

> "I've increased:
> - Strength from 5 to 20 - it'll hit harder
> - Agility from 3 to 15 - faster and harder to hit
> - HP from 2-3 to 10-15 - takes more hits to kill
> - Experience from 1 to 5 - better rewards
> - Gold from 2 to 10 - more money!
>
> Save the file with Ctrl+S."

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

```
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
```

📺 SERIES:
• Ep 1: Getting Started: [LINK]
• Ep 3: Graphics Editing: [COMING SOON]

#DragonWarrior #NES #ROMHacking #Modding #Tutorial
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

