#!/usr/bin/env python3
"""
Generate Mesen movie files (.mmo) and Lua scripts for automated gameplay capture.

This tool creates:
1. Input sequence definitions for specific gameplay scenarios
2. Lua scripts that automate gameplay and capture screenshots/video
3. Batch processing scripts for multiple scenes

Usage:
    python mesen_automation.py generate-scripts --episode 1
    python mesen_automation.py create-scene --name slime_battle --inputs inputs.json
"""

import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum


class NESButton(Enum):
    """NES controller buttons."""
    A = "a"
    B = "b"
    SELECT = "select"
    START = "start"
    UP = "up"
    DOWN = "down"
    LEFT = "left"
    RIGHT = "right"


@dataclass
class InputFrame:
    """A single frame of controller input."""
    frame: int
    buttons: List[str]
    duration: int = 1  # How many frames to hold
    
    def to_lua_input(self) -> Dict[str, bool]:
        """Convert to Mesen Lua input format."""
        return {btn: True for btn in self.buttons}


@dataclass
class GameScene:
    """A scripted game scene for video capture."""
    name: str
    description: str
    start_savestate: Optional[str]
    inputs: List[InputFrame]
    screenshot_frames: List[int]
    end_action: str  # "savestate", "screenshot", "continue"
    duration_frames: int
    
    def to_lua_script(self) -> str:
        """Generate Mesen Lua script for this scene."""
        return generate_scene_lua(self)


# Dragon Warrior specific memory addresses for scene detection
DW_MEMORY_ADDRESSES = {
    "game_state": 0x0045,       # Current game state
    "player_x": 0x008E,         # Player X position
    "player_y": 0x008F,         # Player Y position  
    "current_map": 0x0045,      # Current map ID
    "battle_state": 0x00E0,     # Battle state
    "menu_state": 0x00D8,       # Menu state
    "player_hp": 0x00C5,        # Player current HP
    "player_max_hp": 0x00C6,    # Player max HP
    "player_level": 0x00C7,     # Player level
    "gold": 0x00BC,             # Gold (low byte)
    "in_battle": 0x00E0,        # Non-zero when in battle
}

# Scene templates for common video tutorial scenarios
SCENE_TEMPLATES = {
    "title_screen": {
        "description": "Dragon Warrior title screen display",
        "start_savestate": None,
        "inputs": [
            {"frame": 0, "buttons": [], "duration": 180},  # 3 seconds on title
        ],
        "screenshot_frames": [60, 120],
        "end_action": "screenshot",
        "duration_frames": 180
    },
    "new_game_start": {
        "description": "Starting a new game - name entry to throne room",
        "start_savestate": "title.mss",
        "inputs": [
            {"frame": 0, "buttons": ["start"], "duration": 1},
            {"frame": 60, "buttons": ["a"], "duration": 1},  # Select adventure log
            {"frame": 120, "buttons": ["a"], "duration": 1},  # Begin
            # Name entry handled separately
        ],
        "screenshot_frames": [60, 180, 300],
        "end_action": "savestate",
        "duration_frames": 300
    },
    "exit_throne_room": {
        "description": "Walk out of throne room to overworld",
        "start_savestate": "throne_room.mss",
        "inputs": [
            {"frame": 0, "buttons": ["down"], "duration": 30},
            {"frame": 30, "buttons": ["down"], "duration": 30},
            {"frame": 60, "buttons": ["down"], "duration": 30},
            {"frame": 90, "buttons": [], "duration": 30},
        ],
        "screenshot_frames": [30, 60, 90, 120],
        "end_action": "savestate",
        "duration_frames": 150
    },
    "slime_encounter": {
        "description": "Walk until slime encounter, show battle",
        "start_savestate": "overworld.mss",
        "inputs": [
            # Walk in grass until encounter (RNG-based)
            {"frame": 0, "buttons": ["right"], "duration": 60},
            {"frame": 60, "buttons": ["up"], "duration": 60},
            {"frame": 120, "buttons": ["right"], "duration": 60},
        ],
        "screenshot_frames": [30, 90],
        "end_action": "continue",
        "duration_frames": 180
    },
    "battle_attack": {
        "description": "Attack command in battle",
        "start_savestate": "slime_battle.mss",
        "inputs": [
            {"frame": 0, "buttons": [], "duration": 30},
            {"frame": 30, "buttons": ["a"], "duration": 1},  # Select FIGHT
            {"frame": 60, "buttons": [], "duration": 60},    # Watch attack
        ],
        "screenshot_frames": [0, 30, 60, 90, 120],
        "end_action": "screenshot",
        "duration_frames": 150
    },
    "open_menu": {
        "description": "Open status menu",
        "start_savestate": "overworld.mss", 
        "inputs": [
            {"frame": 0, "buttons": ["a"], "duration": 1},
            {"frame": 30, "buttons": [], "duration": 60},  # Menu displayed
        ],
        "screenshot_frames": [30, 60],
        "end_action": "screenshot",
        "duration_frames": 90
    },
    "shop_interaction": {
        "description": "Enter shop and browse items",
        "start_savestate": "brecconary_shop.mss",
        "inputs": [
            {"frame": 0, "buttons": ["a"], "duration": 1},   # Talk to shopkeeper
            {"frame": 60, "buttons": ["a"], "duration": 1},  # Yes, buy
            {"frame": 120, "buttons": ["down"], "duration": 1},  # Browse items
            {"frame": 180, "buttons": ["down"], "duration": 1},
        ],
        "screenshot_frames": [60, 120, 180, 240],
        "end_action": "screenshot",
        "duration_frames": 300
    },
    "level_up": {
        "description": "Level up display",
        "start_savestate": "near_level_up.mss",
        "inputs": [
            # Battle victory leading to level up
            {"frame": 0, "buttons": ["a"], "duration": 1},
            {"frame": 60, "buttons": [], "duration": 120},  # Victory + level up display
        ],
        "screenshot_frames": [60, 90, 120, 150],
        "end_action": "screenshot",
        "duration_frames": 180
    }
}


def generate_scene_lua(scene: GameScene) -> str:
    """Generate a Mesen Lua script for a game scene."""
    
    lua_script = f'''-- {scene.name}.lua
-- {scene.description}
-- Auto-generated by mesen_automation.py

local scene_name = "{scene.name}"
local frame_count = 0
local screenshots_taken = 0
local scene_complete = false

-- Screenshot frames
local screenshot_frames = {{{", ".join(str(f) for f in scene.screenshot_frames)}}}

-- Input sequence
local inputs = {{
'''
    
    for inp in scene.inputs:
        buttons = ", ".join(f'{b} = true' for b in inp.buttons) if inp.buttons else ""
        lua_script += f'    {{frame = {inp.frame}, duration = {inp.duration}, buttons = {{{buttons}}}}},\n'
    
    lua_script += f'''}}

-- Screenshot output folder
local output_folder = emu.getScriptDataFolder() .. "/{scene.name}/"

function onStartFrame()
    if scene_complete then return end
    
    -- Check if we should take a screenshot
    for _, sf in ipairs(screenshot_frames) do
        if frame_count == sf then
            local png_data = emu.takeScreenshot()
            local filename = output_folder .. scene_name .. "_" .. string.format("%04d", frame_count) .. ".png"
            local file = io.open(filename, "wb")
            if file then
                file:write(png_data)
                file:close()
                screenshots_taken = screenshots_taken + 1
                emu.log("Screenshot: " .. filename)
            end
        end
    end
    
    -- Apply inputs
    for _, input in ipairs(inputs) do
        if frame_count >= input.frame and frame_count < input.frame + input.duration then
            emu.setInput(0, input.buttons)
        end
    end
    
    frame_count = frame_count + 1
    
    -- Scene duration check
    if frame_count >= {scene.duration_frames} then
        scene_complete = true
        emu.log("Scene complete: " .. scene_name)
        emu.log("Screenshots taken: " .. screenshots_taken)
'''
    
    if scene.end_action == "savestate":
        lua_script += f'''
        -- Save end state
        emu.saveSavestateAsync(99)
        emu.log("Saved end state to slot 99")
'''
    
    lua_script += '''    end
end

-- Register callback
emu.addEventCallback(onStartFrame, emu.eventType.startFrame)

emu.log("Scene script loaded: " .. scene_name)
'''
    
    return lua_script


def generate_battle_detector_lua() -> str:
    """Generate Lua script that detects battle start/end for auto-capture."""
    return '''-- battle_detector.lua
-- Automatically captures screenshots when battles begin and end

local in_battle = false
local battle_count = 0
local output_folder = emu.getScriptDataFolder() .. "/battles/"

-- Dragon Warrior battle state memory address
local BATTLE_STATE_ADDR = 0x00E0

function checkBattleState()
    local battle_value = emu.read(BATTLE_STATE_ADDR, emu.memType.cpuDebug)
    
    if battle_value > 0 and not in_battle then
        -- Battle started
        in_battle = true
        battle_count = battle_count + 1
        emu.log("Battle started: #" .. battle_count)
        
        -- Take screenshot of battle start
        local png_data = emu.takeScreenshot()
        local filename = output_folder .. "battle_" .. battle_count .. "_start.png"
        local file = io.open(filename, "wb")
        if file then
            file:write(png_data)
            file:close()
        end
    elseif battle_value == 0 and in_battle then
        -- Battle ended
        in_battle = false
        emu.log("Battle ended: #" .. battle_count)
        
        -- Take screenshot of battle end/victory
        local png_data = emu.takeScreenshot()
        local filename = output_folder .. "battle_" .. battle_count .. "_end.png"
        local file = io.open(filename, "wb")
        if file then
            file:write(png_data)
            file:close()
        end
    end
end

emu.addEventCallback(checkBattleState, emu.eventType.endFrame)
emu.log("Battle detector loaded - watching for encounters")
'''


def generate_demo_playback_lua(inputs_file: str) -> str:
    """Generate Lua script for playing back a recorded input sequence."""
    return f'''-- demo_playback.lua
-- Play back recorded inputs for demo video capture

local inputs_json = [[
-- Input data will be loaded here
]]

local frame_count = 0
local input_index = 1
local inputs = {{}}  -- Will be populated from JSON

-- Parse simple input format
function parseInputs(json_str)
    -- Simple JSON array parser for our input format
    local result = {{}}
    for frame, buttons, duration in json_str:gmatch('"frame":%s*(%d+).-"buttons":%s*%[([^%]]*)%].-"duration":%s*(%d+)') do
        local btn_list = {{}}
        for btn in buttons:gmatch('"([^"]+)"') do
            btn_list[btn] = true
        end
        table.insert(result, {{
            frame = tonumber(frame),
            buttons = btn_list,
            duration = tonumber(duration)
        }})
    end
    return result
end

function onInputPolled()
    -- Find current input
    local current_input = nil
    for _, inp in ipairs(inputs) do
        if frame_count >= inp.frame and frame_count < inp.frame + inp.duration then
            current_input = inp
            break
        end
    end
    
    if current_input then
        emu.setInput(0, current_input.buttons)
    end
    
    frame_count = frame_count + 1
end

-- Load inputs from file if specified
local file = io.open("{inputs_file}", "r")
if file then
    inputs_json = file:read("*all")
    file:close()
    inputs = parseInputs(inputs_json)
    emu.log("Loaded " .. #inputs .. " input frames from file")
end

emu.addEventCallback(onInputPolled, emu.eventType.inputPolled)
emu.log("Demo playback script loaded")
'''


def generate_video_overlay_lua() -> str:
    """Generate Lua script for adding tutorial overlays during recording."""
    return '''-- video_overlay.lua
-- Add tutorial overlays and annotations during video recording

local overlay_text = ""
local overlay_duration = 0
local overlay_position = {x = 10, y = 220}

-- Colors
local OVERLAY_BG = 0xCC000000  -- Semi-transparent black
local OVERLAY_TEXT = 0xFFFFFF  -- White
local HIGHLIGHT_COLOR = 0xFFFF00  -- Yellow

function showOverlay(text, duration, x, y)
    overlay_text = text
    overlay_duration = duration or 180  -- 3 seconds default
    if x then overlay_position.x = x end
    if y then overlay_position.y = y end
end

function highlightMemory(addr, label)
    local value = emu.read(addr, emu.memType.cpuDebug)
    showOverlay(label .. ": " .. value, 60)
end

function drawOverlays()
    if overlay_duration > 0 then
        -- Draw background
        local text_width = #overlay_text * 8
        emu.drawRectangle(
            overlay_position.x - 2, 
            overlay_position.y - 2,
            text_width + 4,
            12,
            OVERLAY_BG,
            true
        )
        
        -- Draw text
        emu.drawString(
            overlay_position.x,
            overlay_position.y,
            overlay_text,
            OVERLAY_TEXT,
            0x00000000
        )
        
        overlay_duration = overlay_duration - 1
    end
end

emu.addEventCallback(drawOverlays, emu.eventType.endFrame)

-- Export functions for external control
_G.showOverlay = showOverlay
_G.highlightMemory = highlightMemory

emu.log("Video overlay script loaded")
'''


def create_episode_scenes(episode_num: int) -> List[GameScene]:
    """Create all scenes needed for a specific episode."""
    
    # Episode-specific scene lists
    episode_scenes = {
        1: [  # Getting Started
            "title_screen",
            "new_game_start",
        ],
        2: [  # Monster Stats
            "slime_encounter",
            "battle_attack",
            "level_up",
        ],
        3: [  # Graphics Editing
            "title_screen",
            "slime_encounter",
        ],
        4: [  # Dialog Editing
            "new_game_start",  # King's dialog
            "shop_interaction",
        ],
        5: [  # Game Balance
            "level_up",
            "shop_interaction",
            "slime_encounter",
        ],
        6: [  # Advanced Assembly
            "battle_attack",
            "level_up",
        ],
        7: [  # Troubleshooting
            # Minimal scenes - mostly code/terminal footage
            "title_screen",
        ]
    }
    
    scenes = []
    scene_names = episode_scenes.get(episode_num, [])
    
    for name in scene_names:
        if name in SCENE_TEMPLATES:
            template = SCENE_TEMPLATES[name]
            scene = GameScene(
                name=name,
                description=template["description"],
                start_savestate=template.get("start_savestate"),
                inputs=[InputFrame(**inp) for inp in template["inputs"]],
                screenshot_frames=template["screenshot_frames"],
                end_action=template["end_action"],
                duration_frames=template["duration_frames"]
            )
            scenes.append(scene)
    
    return scenes


def generate_episode_scripts(episode_num: int, output_dir: Path):
    """Generate all Lua scripts for an episode."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scenes = create_episode_scenes(episode_num)
    
    # Generate scene scripts
    for scene in scenes:
        script_path = output_dir / f"{scene.name}.lua"
        script_path.write_text(scene.to_lua_script(), encoding='utf-8')
        print(f"Generated: {script_path}")
    
    # Generate utility scripts
    (output_dir / "battle_detector.lua").write_text(
        generate_battle_detector_lua(), encoding='utf-8'
    )
    (output_dir / "video_overlay.lua").write_text(
        generate_video_overlay_lua(), encoding='utf-8'
    )
    
    # Generate master runner script
    master_script = generate_master_runner_lua(scenes)
    (output_dir / "run_all_scenes.lua").write_text(master_script, encoding='utf-8')
    
    # Generate scene index
    index = {
        "episode": episode_num,
        "scenes": [
            {
                "name": s.name,
                "description": s.description,
                "savestate": s.start_savestate,
                "duration_frames": s.duration_frames,
                "screenshots": len(s.screenshot_frames)
            }
            for s in scenes
        ]
    }
    (output_dir / "scene_index.json").write_text(
        json.dumps(index, indent=2), encoding='utf-8'
    )
    
    print(f"\nGenerated {len(scenes)} scene scripts for Episode {episode_num}")
    print(f"Output directory: {output_dir}")


def generate_master_runner_lua(scenes: List[GameScene]) -> str:
    """Generate a master script that runs all scenes in sequence."""
    scene_list = ", ".join(f'"{s.name}"' for s in scenes)
    
    return f'''-- run_all_scenes.lua
-- Master script to run all episode scenes in sequence

local scenes = {{{scene_list}}}
local current_scene_index = 1
local scene_running = false

function loadNextScene()
    if current_scene_index > #scenes then
        emu.log("All scenes complete!")
        return
    end
    
    local scene_name = scenes[current_scene_index]
    emu.log("Loading scene: " .. scene_name)
    
    -- Load the scene script
    local script_path = emu.getScriptDataFolder() .. "/" .. scene_name .. ".lua"
    dofile(script_path)
    
    scene_running = true
    current_scene_index = current_scene_index + 1
end

-- Start first scene
loadNextScene()

emu.log("Master runner loaded - " .. #scenes .. " scenes queued")
'''


def main():
    parser = argparse.ArgumentParser(
        description="Generate Mesen automation scripts for video tutorials"
    )
    
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    # Generate episode scripts
    gen_parser = subparsers.add_parser(
        "generate-scripts",
        help="Generate all Lua scripts for an episode"
    )
    gen_parser.add_argument(
        "--episode", "-e",
        type=int,
        required=True,
        choices=[1, 2, 3, 4, 5, 6, 7],
        help="Episode number"
    )
    gen_parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("video_assets/mesen_scripts"),
        help="Output directory"
    )
    
    # List available scenes
    list_parser = subparsers.add_parser(
        "list-scenes",
        help="List available scene templates"
    )
    
    # Create custom scene
    scene_parser = subparsers.add_parser(
        "create-scene",
        help="Create a custom scene script"
    )
    scene_parser.add_argument("--name", required=True, help="Scene name")
    scene_parser.add_argument("--inputs", type=Path, help="Input sequence JSON file")
    scene_parser.add_argument("--output", "-o", type=Path, help="Output Lua file")
    
    args = parser.parse_args()
    
    if args.command == "generate-scripts":
        output_dir = args.output / f"episode_{args.episode:02d}"
        generate_episode_scripts(args.episode, output_dir)
    
    elif args.command == "list-scenes":
        print("Available scene templates:")
        print("-" * 40)
        for name, template in SCENE_TEMPLATES.items():
            print(f"  {name}")
            print(f"    {template['description']}")
            print(f"    Duration: {template['duration_frames']} frames")
            print()
    
    elif args.command == "create-scene":
        # Custom scene creation
        if args.inputs and args.inputs.exists():
            inputs_data = json.loads(args.inputs.read_text())
            scene = GameScene(
                name=args.name,
                description=f"Custom scene: {args.name}",
                start_savestate=inputs_data.get("savestate"),
                inputs=[InputFrame(**i) for i in inputs_data.get("inputs", [])],
                screenshot_frames=inputs_data.get("screenshot_frames", []),
                end_action=inputs_data.get("end_action", "screenshot"),
                duration_frames=inputs_data.get("duration_frames", 300)
            )
        else:
            # Create empty scene template
            scene = GameScene(
                name=args.name,
                description=f"Custom scene: {args.name}",
                start_savestate=None,
                inputs=[],
                screenshot_frames=[60],
                end_action="screenshot",
                duration_frames=300
            )
        
        output_path = args.output or Path(f"{args.name}.lua")
        output_path.write_text(scene.to_lua_script(), encoding='utf-8')
        print(f"Created: {output_path}")


if __name__ == "__main__":
    main()
