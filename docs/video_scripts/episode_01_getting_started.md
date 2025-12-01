# Episode 1: Getting Started with Dragon Warrior ROM Hacking

## Video Metadata

| Field | Value |
|-------|-------|
| **Title** | "Dragon Warrior ROM Hacking: Fork to First Build in 10 Minutes" |
| **Duration** | 10-12 minutes |
| **Difficulty** | Beginner |
| **Prerequisites** | Windows PC, GitHub account, Internet connection |
| **Related Docs** | `README.md`, `docs/BUILD_GUIDE.md` |

---

## Chapter Markers (YouTube Timestamps)

```text
0:00 - Introduction
0:45 - What You'll Need
1:30 - Forking the Repository
2:45 - Cloning to Your Computer
4:00 - Installing Python
5:15 - Installing Ophis Assembler
6:30 - Running Your First Build
8:00 - Testing in an Emulator
9:30 - What's Next
10:15 - Closing
```

---

## Full Script

### [0:00] Introduction (45 seconds)

**[VISUAL: Dragon Warrior title screen in emulator, fade to VS Code with project open]**

**NARRATION:**
> "Hey everyone, welcome to the Dragon Warrior ROM Hacking Tutorial Series! If you've ever wanted to create your own version of this classic NES RPG, you're in the right place.
>
> I'm about to show you how to go from absolutely nothing to building your own modified Dragon Warrior ROM in just about 10 minutes. Seriously, 10 minutes!
>
> By the end of this video, you'll have:
> - Your own copy of the project on GitHub
> - All the tools you need installed
> - A freshly built ROM running in an emulator
>
> Sound good? Let's dive in!"

**[B-ROLL: Quick montage showing the Universal Editor interface, editing monsters.json with cool stats visible, emulator gameplay showing a battle]**

---

### [0:45] What You'll Need (45 seconds)

**[VISUAL: Desktop with browser open, split screen showing requirements list]**

**NARRATION:**
> "Alright, before we get our hands dirty, here's what you'll need:
>
> First, a Windows computer. This project uses PowerShell scripts that are optimized for Windows. Mac and Linux folks - it's possible but you'll need to adapt a few things.
>
> Second, a GitHub account. If you don't have one yet, head to github.com and sign up - it's completely free and only takes a minute.
>
> Third, we'll be installing two things: Python 3 and the Ophis assembler. Don't worry if those sound intimidating - I'll walk you through both step by step.
>
> And finally - and this is important - you'll need a Dragon Warrior ROM. For legal reasons, I can't provide this. You'll need to dump your own cartridge or find it through... other means. The file should be named `dragon_warrior.nes` and placed in the `roms` folder."

**[VISUAL: Bullet point list appearing on screen as items are mentioned, with little checkmark animations]**

---

### [1:30] Forking the Repository (1 minute 15 seconds)

**[VISUAL: Browser navigating to GitHub repository]**

**NARRATION:**
> "Okay, here's where the magic starts! Let's fork the enhanced toolkit repository. Open your browser and navigate to:
>
> `github.com/YOUR-CHANNEL/dragon-warrior-info`
>
> Now, this isn't the original bare-bones disassembly - this is the enhanced toolkit with JSON-based editing, visual editors, and a complete build pipeline. All the good stuff we'll be using in this series!"

**[VISUAL: Click on Fork button with mouse cursor highlighted]**

> "See that 'Fork' button up in the top right corner? Give it a click. This creates your own personal copy of the entire project under your GitHub account.
>
> GitHub might ask you a few questions about the fork - just accept the defaults and hit 'Create Fork'.
>
> And just like that, you've got your own version! This is YOUR copy now - you can modify it however you want, break things, experiment, and push your changes back to GitHub. Pretty cool, right?"

**[VISUAL: Show forked repository under user's account with celebration animation]**

---

### [2:45] Cloning to Your Computer (1 minute 15 seconds)

**[VISUAL: GitHub repository page with Code button]**

**NARRATION:**
> "Now let's get all this goodness onto your computer. See that green 'Code' button? Click it and copy the HTTPS URL.
>
> Time to open PowerShell - you can search for it in the Start menu."

**[VISUAL: PowerShell window opening with dramatic sound effect]**

> "Navigate to where you want to store the project. I like to use a 'repos' folder in my user directory:"

**[VISUAL: Type command in PowerShell]**

```powershell
cd ~\source\repos
git clone https://github.com/YOUR-USERNAME/dragon-warrior-info.git
cd dragon-warrior-info
```

> "Replace 'YOUR-USERNAME' with your actual GitHub username. Watch as Git downloads all the project files - there's quite a bit here because we've got a full asset pipeline, graphical editors, documentation... the works!"

**[VISUAL: Git clone progress with file count, folder structure revealing in VS Code]**

---

### [4:00] Installing Python (1 minute 15 seconds)

**[VISUAL: Browser navigating to python.org]**

**NARRATION:**
> "Now let's install Python. Go to python.org and click 'Downloads'. Get the latest version for Windows.
>
> When you run the installer, there's one critical step:"

**[VISUAL: Python installer with checkbox highlighted]**

> "Make sure to check 'Add Python to PATH' at the bottom of the first screen. This is important!
>
> Then click 'Install Now' and wait for it to finish."

**[VISUAL: Installation progress, completion screen]**

> "Let's verify it worked. In PowerShell, type:"

```powershell
python --version
```

> "You should see the Python version number. If you get an error, try closing and reopening PowerShell."

**[VISUAL: PowerShell showing Python version]**

---

### [5:15] Installing Ophis Assembler (1 minute 15 seconds)

**[VISUAL: GitHub navigating to Ophis releases]**

**NARRATION:**
> "Next we need the Ophis assembler. This converts the assembly source code into the actual NES ROM file.
>
> Go to: `github.com/michaelcmartin/Ophis/releases`
>
> Download the latest Windows release - it's a zip file."

**[VISUAL: Downloading and extracting zip file]**

> "Extract it somewhere convenient. I recommend creating an 'Ophis' folder in the project directory.
>
> The key file is `Ophis.exe`. You can either:
> - Add the Ophis folder to your system PATH, or
> - Copy `Ophis.exe` into the project root folder
>
> The second option is easier for beginners."

**[VISUAL: File explorer showing Ophis.exe location]**

> "To add to PATH, search for 'Environment Variables' in Windows, click 'Path', 'Edit', and 'New', then paste the folder path."

---

### [6:30] Running Your First Build (1 minute 30 seconds)

**[VISUAL: VS Code with project open, PowerShell terminal visible]**

**NARRATION:**
> "Before we build, make sure your Dragon Warrior ROM is in the `roms` folder and named `dragon_warrior.nes`.
>
> Now, the moment of truth! In the project folder, open PowerShell and run:"

```powershell
.\build.ps1
```

**[VISUAL: Build script running, showing output]**

> "You'll see the build process go through several stages:
> - First, it regenerates asset files from JSON
> - Then it assembles the source code with Ophis
> - Finally, it creates the ROM in the `build` folder"

**[VISUAL: Terminal showing successful build messages]**

> "If everything worked, you'll see 'Build succeeded' and find `dragon_warrior_rebuilt.nes` in the build folder."

**[VISUAL: File explorer showing built ROM]**

> "If you see errors, don't panic! The most common issues are:
> - Missing ROM in the roms folder
> - Ophis not found - check your PATH or copy Ophis.exe to the project
> - Python not found - try restarting PowerShell"

---

### [8:00] Testing in an Emulator (1 minute 30 seconds)

**[VISUAL: Downloading/opening emulator]**

**NARRATION:**
> "Let's test our build! You'll need an NES emulator. I recommend Mesen for its accuracy and debugging features, but FCEUX or Nestopia also work great.
>
> Open your emulator and load the ROM from `build/dragon_warrior_rebuilt.nes`."

**[VISUAL: Emulator loading ROM, title screen appearing]**

> "You should see the familiar Dragon Warrior title screen. The game should play exactly like the original - because we haven't changed anything yet!
>
> But here's the exciting part: now you can modify the source files and rebuild to see your changes."

**[VISUAL: Quick gameplay footage - walking around, opening menu]**

> "Let me show you a quick preview. In the next video, we'll actually change something:"

**[VISUAL: Quick cut to monsters.json, changing a value, rebuilding, showing change in emulator]**

> "See how easy that is? That's the power of this disassembly project - you can edit JSON files instead of dealing with raw hex values."

---

### [9:30] What's Next (45 seconds)

**[VISUAL: Project structure overview in VS Code]**

**NARRATION:**
> "Congratulations! You've successfully set up your Dragon Warrior ROM hacking environment.
>
> Here's what you can explore next:
>
> - The `assets/json` folder contains all the game data in editable JSON format
> - Run `python tools/universal_editor.py` to open the graphical editor
> - Check out the `docs` folder for detailed guides on every aspect of the project
>
> In the next video, we'll modify monster stats and see the changes in-game."

**[VISUAL: Universal Editor opening, quick tour of tabs]**

---

### [10:15] Closing (30-45 seconds)

**[VISUAL: Subscribe/like graphics, links on screen]**

**NARRATION:**
> "Thanks for watching! If this helped you get started, smash that like button and subscribe for more ROM hacking tutorials.
>
> Got questions? Hit me up in the comments - I read every single one!
>
> Links to the project, documentation, and all the tools are waiting for you in the description below.
>
> See you in the next one - happy hacking!"

**[VISUAL: Dragon Warrior ending fanfare, fade to end card with subscribe animation]**

---

## Video Description Template

```text
🎮 Dragon Warrior ROM Hacking: Getting Started Tutorial

In this video, I show you how to set up everything you need to start modifying Dragon Warrior for the NES. Go from zero to a working build in just 10 minutes!

📋 TIMESTAMPS:
0:00 - Introduction
0:45 - What You'll Need
1:30 - Forking the Repository
2:45 - Cloning to Your Computer
4:00 - Installing Python
5:15 - Installing Ophis Assembler
6:30 - Running Your First Build
8:00 - Testing in an Emulator
9:30 - What's Next
10:15 - Closing

📁 PROJECT LINKS:
• Enhanced Toolkit: https://github.com/YOUR-CHANNEL/dragon-warrior-info
• Original Disassembly: https://github.com/nmikstas/dragon-warrior-disassembly
• Documentation: [YOUR FORK]/docs/
• Universal Editor: Run python tools/universal_editor.py

🔧 TOOLS:
• Python: https://python.org
• Ophis Assembler: https://github.com/michaelcmartin/Ophis/releases
• Mesen Emulator: https://mesen.ca
• FCEUX Emulator: https://fceux.com

⌨️ COMMANDS USED:
cd ~\source\repos
git clone https://github.com/YOUR-USERNAME/dragon-warrior-info.git
cd dragon-warrior-info
python --version
.\build.ps1

📺 NEXT VIDEO: Modifying Monster Stats

👍 Like and subscribe for more NES ROM hacking tutorials!

Tags: DragonWarrior, NES, ROMHacking, Retrogaming, Tutorial
```

---

## Production Notes

### B-Roll Needed

- [ ] Dragon Warrior title screen (5-10 seconds)
- [ ] Various gameplay clips (walking, menu, battle)
- [ ] Universal Editor interface tour
- [ ] Quick monster edit demonstration
- [ ] Build success terminal output

### Screen Recording Tips

1. **VS Code Settings**
   - Increase font size to 16+ for readability
   - Use a high-contrast theme (One Dark Pro recommended)
   - Hide unnecessary panels

2. **PowerShell Settings**
   - Increase font size
   - Clear screen before recording commands
   - Consider using Windows Terminal with a nice theme

3. **Emulator Settings**
   - Use integer scaling (2x or 3x)
   - Enable "Show FPS" off for cleaner footage
   - Configure clean video output filters

### Timing Notes

- Each section has buffer time built in
- Target 10 minutes, acceptable up to 12
- Can trim filler words and pauses in editing

---

## Revision History

| Date | Version | Changes |
|------|---------|---------|
| 2025-12-02 | 1.0 | Initial script creation |
| 2025-12-02 | 1.1 | Update to fork enhanced toolkit, add more personality |

