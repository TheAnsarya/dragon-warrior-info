#!/usr/bin/env python3
"""
Scene Planner - Parse video scripts into production scene definitions.

This tool reads episode scripts and generates a structured scene plan
that can be used by other tools (Mesen automation, video assembly, etc.).

Output formats:
- JSON scene definitions for programmatic use
- CSV for spreadsheet planning
- Timeline view for video editing reference

Usage:
    python scene_planner.py episode_01_getting_started.md
    python scene_planner.py --all --output scenes/
    python scene_planner.py episode_02.md --format csv
"""

import re
import json
import csv
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum


class SceneType(Enum):
    """Types of scenes in a video."""
    INTRO = "intro"
    GAMEPLAY = "gameplay"
    NARRATION = "narration"
    TRANSITION = "transition"
    OUTRO = "outro"
    DEMONSTRATION = "demonstration"
    TITLE_CARD = "title_card"
    PAUSE = "pause"


@dataclass
class Scene:
    """A single scene in the video."""
    id: str
    scene_type: SceneType
    title: str
    description: str
    estimated_duration: int  # seconds
    narration: Optional[str] = None
    visual_notes: Optional[str] = None
    gameplay_actions: list = field(default_factory=list)
    screenshot_ref: Optional[str] = None
    savestate_ref: Optional[str] = None
    start_time: Optional[int] = None  # calculated
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        d = asdict(self)
        d['scene_type'] = self.scene_type.value
        return d


@dataclass
class ScenePlan:
    """Complete scene plan for an episode."""
    episode_number: int
    episode_title: str
    total_duration: int  # seconds
    scenes: list = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
    
    def add_scene(self, scene: Scene):
        """Add a scene and update timestamps."""
        if self.scenes:
            scene.start_time = self.scenes[-1].start_time + self.scenes[-1].estimated_duration
        else:
            scene.start_time = 0
        self.scenes.append(scene)
        self.total_duration = scene.start_time + scene.estimated_duration
    
    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'episode_number': self.episode_number,
            'episode_title': self.episode_title,
            'total_duration': self.total_duration,
            'total_duration_formatted': format_time(self.total_duration),
            'scene_count': len(self.scenes),
            'scenes': [s.to_dict() for s in self.scenes],
            'metadata': self.metadata
        }


def format_time(seconds: int) -> str:
    """Format seconds as MM:SS."""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def parse_duration(duration_str: str) -> int:
    """Parse duration string to seconds."""
    # Handle "X-Y minutes" format
    minutes_match = re.search(r'(\d+)-?(\d+)?\s*minutes?', duration_str, re.IGNORECASE)
    if minutes_match:
        min_val = int(minutes_match.group(1))
        max_val = minutes_match.group(2)
        if max_val:
            return (min_val + int(max_val)) // 2 * 60
        return min_val * 60
    
    # Handle "X:XX" format
    time_match = re.search(r'(\d+):(\d{2})', duration_str)
    if time_match:
        return int(time_match.group(1)) * 60 + int(time_match.group(2))
    
    return 0


def parse_script(markdown_content: str) -> ScenePlan:
    """Parse a video script markdown file into a scene plan."""
    plan = ScenePlan(episode_number=0, episode_title="", total_duration=0)
    
    # Extract episode metadata
    ep_match = re.search(r'Episode\s+(\d+)', markdown_content, re.IGNORECASE)
    if ep_match:
        plan.episode_number = int(ep_match.group(1))
    
    title_match = re.search(r'\*\*Title\*\*\s*\|\s*"([^"]+)"', markdown_content)
    if title_match:
        plan.episode_title = title_match.group(1)
    
    # Parse sections into scenes
    # Look for ## Scene or numbered sections like ## 1. Title
    scene_pattern = r'^##\s+(?:Scene\s+)?(\d+)?\.?\s*([^\n]+)\n(.*?)(?=^##|\Z)'
    
    matches = re.finditer(scene_pattern, markdown_content, re.MULTILINE | re.DOTALL)
    
    scene_id = 0
    for match in matches:
        section_num = match.group(1)
        section_title = match.group(2).strip()
        section_content = match.group(3).strip()
        
        # Skip non-content sections
        if any(skip in section_title.lower() for skip in ['metadata', 'checklist', 'notes', 'resources', 'description']):
            continue
        
        scene_id += 1
        
        # Determine scene type
        scene_type = SceneType.GAMEPLAY
        title_lower = section_title.lower()
        if 'intro' in title_lower or 'hook' in title_lower:
            scene_type = SceneType.INTRO
        elif 'outro' in title_lower or 'closing' in title_lower or 'next episode' in title_lower:
            scene_type = SceneType.OUTRO
        elif 'transition' in title_lower:
            scene_type = SceneType.TRANSITION
        elif 'demo' in title_lower or 'showing' in title_lower:
            scene_type = SceneType.DEMONSTRATION
        
        # Extract narration (text in blockquotes)
        narration_parts = re.findall(r'>\s*(.+)', section_content)
        narration = ' '.join(narration_parts) if narration_parts else None
        
        # Extract visual notes (in asterisks or Visual: prefix)
        visual_notes = []
        visual_matches = re.findall(r'\*\*?Visual:?\*?\*?\s*(.+)', section_content)
        visual_notes.extend(visual_matches)
        
        # Also look for [Visual] or (Visual) patterns
        bracket_visuals = re.findall(r'[\[\(]Visual[:\]]?\s*([^\]\)]+)[\]\)]', section_content)
        visual_notes.extend(bracket_visuals)
        
        # Extract gameplay actions (lines starting with - or *)
        action_matches = re.findall(r'^[\-\*]\s+(.+)$', section_content, re.MULTILINE)
        
        # Estimate duration from content length and narration
        estimated_duration = 30  # base duration
        if narration:
            # Roughly 150 words per minute speaking rate
            word_count = len(narration.split())
            estimated_duration = max(30, (word_count / 150) * 60)
        
        scene = Scene(
            id=f"scene_{scene_id:02d}",
            scene_type=scene_type,
            title=section_title,
            description=section_content[:200].replace('\n', ' '),
            estimated_duration=int(estimated_duration),
            narration=narration,
            visual_notes='; '.join(visual_notes) if visual_notes else None,
            gameplay_actions=action_matches[:10],  # Limit to 10 actions
        )
        
        plan.add_scene(scene)
    
    return plan


def output_json(plan: ScenePlan, output_path: Path):
    """Output scene plan as JSON."""
    output_path.write_text(
        json.dumps(plan.to_dict(), indent=2),
        encoding='utf-8'
    )


def output_csv(plan: ScenePlan, output_path: Path):
    """Output scene plan as CSV."""
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Scene ID', 'Start Time', 'Duration', 'Type', 'Title',
            'Narration Preview', 'Visual Notes', 'Actions Count'
        ])
        
        for scene in plan.scenes:
            writer.writerow([
                scene.id,
                format_time(scene.start_time or 0),
                format_time(scene.estimated_duration),
                scene.scene_type.value,
                scene.title,
                (scene.narration[:100] + '...') if scene.narration and len(scene.narration) > 100 else scene.narration,
                scene.visual_notes,
                len(scene.gameplay_actions)
            ])


def output_timeline(plan: ScenePlan) -> str:
    """Generate a visual timeline representation."""
    lines = [
        f"EPISODE {plan.episode_number}: {plan.episode_title}",
        f"Total Duration: {format_time(plan.total_duration)}",
        "=" * 60,
        ""
    ]
    
    for scene in plan.scenes:
        time_str = format_time(scene.start_time or 0)
        duration_str = format_time(scene.estimated_duration)
        
        lines.append(f"[{time_str}] {scene.title}")
        lines.append(f"         Type: {scene.scene_type.value} | Duration: {duration_str}")
        if scene.narration:
            preview = scene.narration[:60] + '...' if len(scene.narration) > 60 else scene.narration
            lines.append(f"         Narration: \"{preview}\"")
        lines.append("")
    
    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Parse video scripts into production scene plans"
    )
    
    parser.add_argument(
        "script_file",
        nargs="?",
        type=Path,
        help="Path to a single script file"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Process all episode scripts"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("scene_plans"),
        help="Output directory"
    )
    parser.add_argument(
        "--format", "-f",
        choices=['json', 'csv', 'timeline', 'all'],
        default='json',
        help="Output format"
    )
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=Path("docs/video_scripts"),
        help="Directory containing script files"
    )
    
    args = parser.parse_args()
    
    def process_file(script_path: Path, output_dir: Path):
        print(f"Processing: {script_path.name}")
        content = script_path.read_text(encoding='utf-8')
        plan = parse_script(content)
        
        output_dir.mkdir(parents=True, exist_ok=True)
        stem = script_path.stem
        
        if args.format in ('json', 'all'):
            output_json(plan, output_dir / f"{stem}_scenes.json")
            print(f"  Created: {stem}_scenes.json")
        
        if args.format in ('csv', 'all'):
            output_csv(plan, output_dir / f"{stem}_scenes.csv")
            print(f"  Created: {stem}_scenes.csv")
        
        if args.format in ('timeline', 'all'):
            timeline = output_timeline(plan)
            (output_dir / f"{stem}_timeline.txt").write_text(timeline, encoding='utf-8')
            print(f"  Created: {stem}_timeline.txt")
        
        if args.format == 'timeline':
            # Also print to console for single file
            if not args.all:
                print("\n" + timeline)
    
    if args.all:
        scripts = sorted(args.scripts_dir.glob("episode_*.md"))
        for script in scripts:
            process_file(script, args.output)
    elif args.script_file:
        if not args.script_file.exists():
            print(f"Error: File not found: {args.script_file}")
            return 1
        process_file(args.script_file, args.output)
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
