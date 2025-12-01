# Episode 4: Creating Custom Dialog and Text

## Video Metadata

| Field | Value |
|-------|-------|
| **Title** | "Dragon Warrior ROM Hacking: Custom Dialog and Text" |
| **Duration** | 10-12 minutes |
| **Difficulty** | Beginner-Intermediate |
| **Prerequisites** | Completed Episode 1 |
| **Related Docs** | `docs/ASSET_PIPELINE.md`, `assets/json/dialogs.json` |

---

## Chapter Markers (YouTube Timestamps)

```
0:00 - Introduction
0:30 - How Dialog Works in Dragon Warrior
1:30 - The Dialog JSON Structure
3:00 - Control Codes (NAME, ITEM, etc.)
4:30 - Editing Dialog with Universal Editor
6:00 - Creating New Dialog Lines
7:30 - Testing Your Changes
8:30 - Advanced: Multi-Line and Branching
10:00 - Closing
```

---

## Full Script

### [0:00] Introduction (30 seconds)

**[VISUAL: King's throne room dialog in-game]**

**NARRATION:**
> "In Dragon Warrior, dialog brings the world to life - from the King's opening speech to the barkeep's rumors.
>
> In this episode, we'll learn how to edit and create custom dialog. You'll be able to:
> - Modify any NPC's text
> - Use special control codes
> - Create entirely new messages
>
> Let's give Alefgard a new voice!"

---

### [0:30] How Dialog Works in Dragon Warrior (1 minute)

**[VISUAL: Dialog flow diagram]**

**NARRATION:**
> "Dragon Warrior stores dialog as encoded text with special control codes. When you talk to an NPC, the game:
>
> 1. Looks up that NPC's dialog ID
> 2. Loads the encoded text from ROM
> 3. Processes control codes as it displays
> 4. Waits for player input at pause points
>
> The project has decoded all this into readable JSON, making it easy to edit."

**[VISUAL: Show dialogs.json briefly]**

---

### [1:30] The Dialog JSON Structure (1 minute 30 seconds)

**[VISUAL: VS Code with dialogs.json open]**

**NARRATION:**
> "Open `assets/json/dialogs.json`. Each entry has:
>
> - **id** - The dialog's identifier
> - **speaker** - Who says this (for documentation)
> - **text** - The actual message
> - **location** - Where this triggers"

```json
{
  "id": "DLG_KING_INTRO",
  "speaker": "King Lorik",
  "text": "Descendant of Erdrick!{WAIT}I am greatly pleased that thou hast come.",
  "location": "Throne Room"
}
```

> "Notice that `{WAIT}` in the middle? That's a control code. The game pauses until the player presses a button."

**[VISUAL: Highlight the {WAIT} code]**

---

### [3:00] Control Codes (1 minute 30 seconds)

**[VISUAL: Table of control codes on screen]**

**NARRATION:**
> "Dragon Warrior supports several control codes:
>
> - `{WAIT}` - Pause until button press
> - `{NAME}` - Insert hero's name
> - `{ITEM}` - Insert item name
> - `{NUM}` - Insert a number
> - `{CLEAR}` - Clear the text window
> - `{END}` - End the dialog
>
> For example:"

```json
"text": "{NAME}, thou hast gained {NUM} experience points!{END}"
```

> "This becomes: 'HERO, thou hast gained 50 experience points!' at runtime."

**[VISUAL: Show in-game example]**

> "The full list is in `docs/ASSET_PIPELINE.md` under the Dialog section."

---

### [4:30] Editing Dialog with Universal Editor (1 minute 30 seconds)

**[VISUAL: Opening Universal Editor, Dialog tab]**

**NARRATION:**
> "The easiest way to edit dialog is with the Universal Editor. Run:"

```powershell
python tools/universal_editor.py
```

> "Click the 'Dialog' tab. You'll see all dialog entries in a list. Select any entry to edit it."

**[VISUAL: Navigate the dialog tab]**

> "Let's change the King's introduction. Find 'DLG_KING_INTRO' and select it.
>
> In the text field, let's make it more dramatic:"

```
"Descendant of Erdrick, the legendary hero!{WAIT}At last, thou hast arrived! Our kingdom's darkest hour is upon us."
```

> "Click 'Save' to update the JSON file."

**[VISUAL: Edit and save]**

---

### [6:00] Creating New Dialog Lines (1 minute 30 seconds)

**[VISUAL: Adding new dialog entry]**

**NARRATION:**
> "Want to add entirely new dialog? In the Universal Editor, click 'Add New Entry'.
>
> Give it a unique ID:"

```json
{
  "id": "DLG_GUARD_CUSTOM",
  "speaker": "Castle Guard",
  "text": "Beware, {NAME}!{WAIT}I've heard rumors of a powerful new enemy lurking in the dungeons.",
  "location": "Tantegel Castle"
}
```

> "For this dialog to appear in-game, you'd need to connect it to an NPC. That requires editing the NPC data and potentially assembly code - we'll cover that in an advanced episode.
>
> But you can also replace existing dialog by using the same ID as an original entry."

---

### [7:30] Testing Your Changes (1 minute)

**[VISUAL: Build and test in emulator]**

**NARRATION:**
> "After editing, rebuild and test:"

```powershell
.\build.ps1
```

> "Load the ROM in your emulator and find the NPC you edited. In our case, head to the King!"

**[VISUAL: Walk to King, see new dialog]**

> "There it is - our dramatic new introduction! The control codes work seamlessly."

**[VISUAL: Show {WAIT} pause in action]**

---

### [8:30] Advanced: Multi-Line and Branching (1 minute 30 seconds)

**[VISUAL: Code examples of complex dialog]**

**NARRATION:**
> "For advanced usage, Dragon Warrior supports:
>
> **Multi-line formatting:**
> Use actual newlines in your JSON or the `{LINE}` code to control line breaks.
>
> **Conditional dialog:**
> Some dialog checks game state - whether you have an item, defeated a boss, etc. This is controlled in the assembly code, not JSON.
>
> **Character limits:**
> The text window holds about 40 characters per line and 3 lines at a time. Plan your text accordingly!"

```json
"text": "This is line one...{LINE}This is line two...{LINE}And line three!{WAIT}{CLEAR}This continues on a new screen."
```

> "Test frequently! Long dialog can overflow or display oddly."

---

### [10:00] Closing (30-45 seconds)

**[VISUAL: Montage of custom dialog examples]**

**NARRATION:**
> "You now know how to customize Dragon Warrior's dialog! This opens up:
> - Story modifications
> - Humor and personality changes  
> - Hint system improvements
> - Complete translation projects
>
> Next episode covers game balance - adjusting experience curves, shop prices, and spell effects.
>
> Share your best custom dialog in the comments! Like and subscribe for more."

---

## Video Description Template

```
🎮 Dragon Warrior ROM Hacking: Custom Dialog and Text

Learn how to edit NPC dialog in Dragon Warrior! This tutorial covers the dialog system, control codes like {NAME} and {WAIT}, and using the Universal Editor to customize every line of text.

📋 TIMESTAMPS:
0:00 - Introduction
0:30 - How Dialog Works in Dragon Warrior
1:30 - The Dialog JSON Structure
3:00 - Control Codes (NAME, ITEM, etc.)
4:30 - Editing Dialog with Universal Editor
6:00 - Creating New Dialog Lines
7:30 - Testing Your Changes
8:30 - Advanced: Multi-Line and Branching
10:00 - Closing

📁 FILES INVOLVED:
• assets/json/dialogs.json - All dialog text
• tools/universal_editor.py - Visual editor
• docs/ASSET_PIPELINE.md - Control code reference

⌨️ CONTROL CODES:
• {WAIT} - Pause for button press
• {NAME} - Insert hero's name
• {ITEM} - Insert item name
• {NUM} - Insert number
• {CLEAR} - Clear text window
• {END} - End dialog

📺 SERIES:
• Ep 1: Getting Started: [LINK]
• Ep 2: Monster Stats: [LINK]
• Ep 3: Graphics Editing: [LINK]
• Ep 5: Game Balance: [COMING SOON]

#DragonWarrior #NES #ROMHacking #Dialog #Tutorial
```

---

## Production Notes

### Scenes to Record
- [ ] King's dialog before and after edit
- [ ] Universal Editor dialog tab walkthrough
- [ ] Control codes in action ({NAME}, {WAIT})
- [ ] Text overflow example (what NOT to do)

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-02 | 1.0 | Initial script creation |

