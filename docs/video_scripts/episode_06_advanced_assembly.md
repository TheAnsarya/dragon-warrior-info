# Episode 6: Advanced Assembly Code Modifications

## Video Metadata

| Field | Value |
|-------|-------|
| **Title** | "Dragon Warrior ROM Hacking: Advanced Assembly Modifications" |
| **Duration** | 15-18 minutes |
| **Difficulty** | Advanced |
| **Prerequisites** | Completed Episodes 1-5, Basic programming knowledge |
| **Related Docs** | `docs/technical/GAME_FORMULAS.md`, `source_files/` |

---

## Chapter Markers (YouTube Timestamps)

```
0:00 - Introduction
1:00 - Understanding 6502 Assembly Basics
3:00 - Navigating the Source Code
5:00 - Finding Code with Debuggers
7:00 - Example: Changing Damage Calculation
10:00 - Example: Adding a New Feature
13:00 - Building and Testing
14:30 - Debugging Tips
16:30 - Closing
```

---

## Full Script

### [0:00] Introduction (1 minute)

**[VISUAL: Assembly code on screen, transitioning to gameplay]**

**NARRATION:**
> "We've modified JSON data to change monsters, items, dialog, and balance. But some changes require going deeper - into the assembly code itself. This is where the real magic happens.
>
> This episode covers:
>
> - Basic 6502 assembly concepts
> - Navigating Dragon Warrior's source code
> - Using debuggers to find code locations
> - Making actual code modifications
>
> Don't let assembly intimidate you. Yes, it's more challenging than editing JSON, but the payoff is massive - you can literally change anything about how the game works.
>
> Don't worry if you don't understand everything immediately - even understanding the concepts opens doors!"

---

### [1:00] Understanding 6502 Assembly Basics (2 minutes)

**[VISUAL: Assembly code examples with annotations]**

**NARRATION:**
> "The NES uses a 6502 processor. Here are the key concepts:
>
> **Registers:**
>
> - **A** (Accumulator) - Main math register
> - **X** and **Y** - Index registers for loops and addresses
>
> **Common Instructions:**"

```asm
LDA #$10      ; Load A with value 16
STA $0400     ; Store A to memory address $0400
CMP #$05      ; Compare A to 5
BEQ label     ; Branch if equal to 'label'
JSR function  ; Call a subroutine
RTS           ; Return from subroutine
```

> "**Memory:**
>
> - `$` prefix means hexadecimal
> - `#` prefix means immediate value
> - No prefix means memory address
>
> Let's see how Dragon Warrior uses these."

---

### [3:00] Navigating the Source Code (2 minutes)

**[VISUAL: VS Code showing source_files/ structure]**

**NARRATION:**
> "The disassembly lives in `source_files/`. Key files:"

```text
source_files/
├── Bank00.asm        # Main game loop, core systems
├── Bank01.asm        # Music, some gameplay
├── Bank02.asm        # Battle system
├── Bank03.asm        # Maps, overworld
├── constants.asm     # Named values
├── macros.asm        # Reusable code snippets
└── generated/        # Auto-generated from JSON
```

> "Most game logic is in Banks 00-03. The `generated/` folder contains code created from JSON - don't edit those directly.
>
> Use VS Code's search (Ctrl+Shift+F) to find specific code. Labels are named descriptively:"

```asm
ProcessPlayerAttack:    ; Player attack logic
CalculateDamage:        ; Damage calculation
HandleVictory:          ; After winning a battle
```

---

### [5:00] Finding Code with Debuggers (2 minutes)

**[VISUAL: Mesen debugger interface]**

**NARRATION:**
> "Sometimes you need to find where specific behavior happens. Emulator debuggers help with this.
>
> I'll use Mesen's debugger. Open it with Debug → Debugger."

**[VISUAL: Setting a breakpoint]**

> "To find the damage calculation:
>
> 1. Start a battle
> 2. Set a write breakpoint on the HP variable
> 3. Attack - the debugger pauses when HP changes
> 4. Now you're at the damage code!
>
> The address shown corresponds to our disassembly. Search for that label to find it in the source."

**[VISUAL: Finding corresponding source code]**

> "Once you find code this way, add comments to remember it!"

---

### [7:00] Example: Changing Damage Calculation (3 minutes)

**[VISUAL: damage_formulas.json, then assembly code]**

**NARRATION:**
> "Let's modify how damage works. First, check `assets/json/damage_formulas.json` - some changes can be done there.
>
> But for deeper changes, we need assembly. Find the `CalculateDamage` routine in Bank02.asm:"

```asm
CalculateDamage:
    LDA PlayerAttack     ; Get player's attack
    SEC                  ; Set carry for subtraction
    SBC EnemyDefense     ; Subtract enemy defense
    BCS .positive        ; If result positive, skip
    LDA #$01             ; Minimum 1 damage
.positive:
    STA DamageDealt
    RTS
```

> "This is basic damage: Attack minus Defense, minimum 1.
>
> Let's make it deal double damage:"

**[VISUAL: Edit the code]**

```asm
CalculateDamage:
    LDA PlayerAttack
    ASL A                ; Shift left = multiply by 2!
    SEC
    SBC EnemyDefense
    BCS .positive
    LDA #$01
.positive:
    STA DamageDealt
    RTS
```

> "The `ASL A` instruction shifts bits left, effectively doubling the value. Now all physical attacks deal double damage!"

---

### [10:00] Example: Adding a New Feature (3 minutes)

**[VISUAL: Planning a simple feature]**

**NARRATION:**
> "Let's add something new: a critical hit system. 10% chance to deal triple damage.
>
> First, we need a random check:"

```asm
CalculateDamage:
    ; Check for critical hit (10% chance)
    JSR GetRandomByte    ; Get random 0-255
    CMP #$19             ; 25 = ~10% of 256
    BCS .normalDamage    ; If >= 25, normal damage
    
.criticalHit:
    LDA PlayerAttack
    ASL A                ; Double
    CLC
    ADC PlayerAttack     ; + original = triple
    JMP .applyDamage
    
.normalDamage:
    LDA PlayerAttack
    
.applyDamage:
    SEC
    SBC EnemyDefense
    BCS .positive
    LDA #$01
.positive:
    STA DamageDealt
    RTS
```

> "This code:
>
> 1. Calls the random number generator
> 2. If < 25 (about 10%), we critical hit
> 3. Critical does Attack×3 instead of Attack×1
> 4. Then applies defense and stores result
>
> You could also add a 'CRITICAL!' message display - but that's more complex."

---

### [13:00] Building and Testing (1 minute 30 seconds)

**[VISUAL: Build process, then testing]**

**NARRATION:**
> "After editing assembly, build with:"

```powershell
.\build.ps1
```

> "If you have syntax errors, the assembler will tell you which line failed. Common mistakes:
>
> - Missing labels
> - Wrong instruction names
> - Incorrect addressing modes
>
> Once built, test thoroughly! Enter battles and verify your changes work."

**[VISUAL: Battle showing modified damage]**

> "There it is - our double damage in action! Or if you implemented criticals, watch for those triple-damage hits."

---

### [14:30] Debugging Tips (2 minutes)

**[VISUAL: Common errors and fixes]**

**NARRATION:**
> "Assembly debugging is tricky. Here are tips:
>
> **Game crashes:** Usually a bad jump address or stack overflow. Use the debugger to trace execution.
>
> **Wrong values:** Check your math. Remember, NES math is 8-bit - values wrap at 256.
>
> **Nothing happens:** Make sure your code is actually reached. The game has multiple code paths.
>
> **Save state abuse:** Save before testing, reload quickly when bugs appear.
>
> **Comment everything:** Future you will thank present you."

```asm
; Calculate damage with critical hit chance
; Input: PlayerAttack, EnemyDefense
; Output: DamageDealt
; Modifies: A register
; Note: Added 2024-12-02 for combat enhancement
```

> "Good comments explain WHY, not just WHAT."

---

### [16:30] Closing (45 seconds)

**[VISUAL: Montage of possibilities]**

**NARRATION:**
> "You've seen how assembly modifications unlock unlimited possibilities:
>
> - Custom damage formulas
> - New game mechanics
> - Bug fixes for the original game
> - Completely new features
>
> This is where ROM hacking becomes true programming. You're not just tweaking numbers anymore - you're writing real code that runs on real hardware.
>
> This concludes the main tutorial series! The final episode covers troubleshooting common issues.
>
> If you've made it this far, you're a true ROM hacker. Show off your mods in the comments!
>
> Like and subscribe, and happy hacking!"

---

## Video Description Template

```text
🎮 Dragon Warrior ROM Hacking: Advanced Assembly Modifications

Go deep into Dragon Warrior's 6502 assembly code! Learn to navigate the disassembly, use debuggers to find code, and make modifications that aren't possible with JSON alone.

⚠️ ADVANCED TOPIC - Recommended after completing Episodes 1-5

📋 TIMESTAMPS:
0:00 - Introduction
1:00 - Understanding 6502 Assembly Basics
3:00 - Navigating the Source Code
5:00 - Finding Code with Debuggers
7:00 - Example: Changing Damage Calculation
10:00 - Example: Adding a New Feature
13:00 - Building and Testing
14:30 - Debugging Tips
16:30 - Closing

📚 6502 QUICK REFERENCE:
• LDA - Load Accumulator
• STA - Store Accumulator
• CMP - Compare
• BEQ/BNE - Branch if Equal/Not Equal
• JSR - Jump to Subroutine
• RTS - Return from Subroutine
• ASL - Arithmetic Shift Left (×2)

🔧 TOOLS:
• Mesen Debugger: https://mesen.ca
• FCEUX Debugger: https://fceux.com
• 6502 Reference: http://6502.org/tutorials/

📁 KEY FILES:
• source_files/Bank00-03.asm - Game logic
• source_files/constants.asm - Named values
• docs/technical/GAME_FORMULAS.md - Formula documentation

📺 SERIES:
• Ep 1: Getting Started: [LINK]
• Ep 2: Monster Stats: [LINK]
• Ep 3: Graphics Editing: [LINK]
• Ep 4: Dialog Editing: [LINK]
• Ep 5: Game Balance: [LINK]
• Ep 7: Troubleshooting: [COMING SOON]

TAGS: DragonWarrior, NES, ROMHacking, Assembly, 6502, Tutorial
```

---

## Production Notes

### Diagrams Needed

- [ ] 6502 register diagram
- [ ] Memory addressing modes visual
- [ ] Code flow diagram for damage calculation

### Key Code Sections to Show

- Actual CalculateDamage (or equivalent) from source
- Random number generation routine
- Bank structure overview

### Debugger Footage

- [ ] Setting breakpoints in Mesen
- [ ] Stepping through code
- [ ] Memory viewer showing variables

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-02 | 1.0 | Initial script creation |
