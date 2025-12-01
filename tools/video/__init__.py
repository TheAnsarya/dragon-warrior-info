"""
Video Production Toolchain for Dragon Warrior ROM Hacking Tutorials.

This package provides tools for automated video production:
- Script extraction and teleprompter generation
- Mesen automation and movie file creation
- Screenshot capture automation
- Scene planning and timeline generation
- Video description extraction
- FFmpeg-based video assembly

Modules:
--------
extract_narration
    Extract narration text from markdown scripts for teleprompter/TTS.

mesen_automation
    Generate Mesen Lua scripts for automated gameplay capture.

scene_planner
    Parse scripts into structured scene definitions.

generate_description
    Extract YouTube descriptions from script templates.

video_assembler
    FFmpeg wrapper for final video assembly.

Usage:
------
    # Extract narration from a script
    python -m tools.video.extract_narration docs/video_scripts/episode_01.md

    # Generate Mesen scripts for an episode
    python -m tools.video.mesen_automation generate-scripts --episode 1

    # Create scene plan from script
    python -m tools.video.scene_planner episode_01.md --format timeline

    # Extract video description
    python -m tools.video.generate_description episode_01.md

    # Assemble final video
    python -m tools.video.video_assembler project.json
"""

__version__ = "1.0.0"
__author__ = "Dragon Warrior Info Project"

# Module exports for convenience
__all__ = [
    "extract_narration",
    "mesen_automation",
    "scene_planner",
    "generate_description",
    "video_assembler",
]
