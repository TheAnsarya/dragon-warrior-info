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

```
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
> "Welcome to the Dragon Warrior ROM Hacking Tutorial Series! I'm going to show you how to go from zero to building your own modified Dragon Warrior ROM in just about 10 minutes.
>
> By the end of this video, you'll have:
> - Your own copy of the project on GitHub
> - All the tools you need installed
> - A freshly built ROM running in an emulator
>
> Let's get started!"

**[B-ROLL: Quick montage of Universal Editor, monsters.json editing, emulator gameplay]**

---

### [0:45] What You'll Need (45 seconds)

**[VISUAL: Desktop with browser open, split screen showing requirements list]**

**NARRATION:**
> "Before we begin, here's what you'll need:
>
> First, a Windows computer. This project uses PowerShell scripts optimized for Windows.
>
> Second, a GitHub account. If you don't have one, go to github.com and sign up - it's free.
>
> Third, we'll install two things: Python 3 and the Ophis assembler. I'll walk you through both.
>
> And finally, you'll need a Dragon Warrior ROM. For legal reasons, I can't provide this - you'll need to dump your own cartridge. The file should be named `dragon_warrior.nes` and placed in the `roms` folder."

**[VISUAL: Bullet point list appearing on screen as items are mentioned]**

---

### [1:30] Forking the Repository (1 minute 15 seconds)

**[VISUAL: Browser navigating to GitHub repository]**

**NARRATION:**
> "Let's start by forking the repository. Open your browser and go to:
>
> `github.com/nmikstas/dragon-warrior-disassembly`
>
> This is the original disassembly project by nmikstas that makes all of this possible."

**[VISUAL: Click on Fork button]**

> "Click the 'Fork' button in the top right corner. This creates your own copy of the project under your GitHub account.
>
> If you're prompted for options, just accept the defaults and click 'Create Fork'.
>
> Now you have your own version that you can modify however you like!"

**[VISUAL: Show forked repository under user's account]**

---

### [2:45] Cloning to Your Computer (1 minute 15 seconds)

**[VISUAL: GitHub repository page with Code button]**

**NARRATION:**
> "Now let's get the code onto your computer. Click the green 'Code' button and copy the HTTPS URL.
>
> Open PowerShell - you can search for it in the Start menu."

**[VISUAL: PowerShell window opening]**

> "Navigate to where you want to store the project. I like to use a 'repos' folder:"

**[VISUAL: Type command in PowerShell]**

```powershell
cd ~\source\repos
git clone https://github.com/YOUR-USERNAME/dragon-warrior-disassembly.git
cd dragon-warrior-disassembly
```

> "Replace 'YOUR-USERNAME' with your actual GitHub username. Git will download all the project files."

**[VISUAL: Git clone progress, folder structure in VS Code]**

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
> "Thanks for watching! If this helped you get started, give the video a like and subscribe for more ROM hacking tutorials.
>
> Drop a comment if you have questions or suggestions for future videos.
>
> Links to the project, documentation, and all the tools are in the description below.
>
> See you in the next one - happy hacking!"

**[VISUAL: Dragon Warrior ending fanfare, fade to end card]**

---

## Video Description Template

```
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
• Main Repository: https://github.com/nmikstas/dragon-warrior-disassembly
• Documentation: [YOUR FORK]/docs/
• Universal Editor: Run `python tools/universal_editor.py`

🔧 TOOLS:
• Python: https://python.org
• Ophis Assembler: https://github.com/michaelcmartin/Ophis/releases
• Mesen Emulator: https://mesen.ca
• FCEUX Emulator: https://fceux.com

⌨️ COMMANDS USED:
```powershell
# Clone the repository
cd ~\source\repos
git clone https://github.com/YOUR-USERNAME/dragon-warrior-disassembly.git
cd dragon-warrior-disassembly

# Check Python installation
python --version

# Build the ROM
.\build.ps1
```

📺 NEXT VIDEO: Modifying Monster Stats

👍 Like and subscribe for more NES ROM hacking tutorials!

#DragonWarrior #NES #ROMHacking #Retrogaming #Tutorial
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

