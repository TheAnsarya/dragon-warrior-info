#!/usr/bin/env python3
"""
Video Assembly Pipeline - Coordinate FFmpeg operations for final video.

This tool provides a high-level interface for assembling video content from:
- Gameplay recordings (from OBS/Mesen)
- AI-generated narration audio
- Background music
- Title cards and overlays

Usage:
    python video_assembler.py project.json
    python video_assembler.py --create-project episode_01
    python video_assembler.py --add-clip gameplay.mp4 --start 0 --end 120
"""

import json
import subprocess
import argparse
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Optional
from enum import Enum


class ClipType(Enum):
    """Types of video clips."""
    GAMEPLAY = "gameplay"
    TITLE_CARD = "title_card"
    TRANSITION = "transition"
    STATIC_IMAGE = "static_image"


class AudioTrackType(Enum):
    """Types of audio tracks."""
    NARRATION = "narration"
    MUSIC = "music"
    GAME_AUDIO = "game_audio"
    SOUND_EFFECT = "sfx"


@dataclass
class VideoClip:
    """A video clip in the timeline."""
    source_path: str
    clip_type: ClipType
    start_time: float  # Start position in the output
    duration: float  # Duration in seconds
    source_in: float = 0.0  # In point in source
    source_out: Optional[float] = None  # Out point in source
    fade_in: float = 0.0
    fade_out: float = 0.0
    scale: Optional[str] = None  # e.g., "1920:1080"

    def to_dict(self) -> dict:
        d = asdict(self)
        d['clip_type'] = self.clip_type.value
        return d


@dataclass
class AudioTrack:
    """An audio track in the timeline."""
    source_path: str
    track_type: AudioTrackType
    start_time: float
    duration: Optional[float] = None
    volume: float = 1.0
    fade_in: float = 0.0
    fade_out: float = 0.0
    loop: bool = False

    def to_dict(self) -> dict:
        d = asdict(self)
        d['track_type'] = self.track_type.value
        return d


@dataclass
class VideoProject:
    """A video assembly project."""
    name: str
    output_path: str
    resolution: str = "1920x1080"
    frame_rate: int = 30
    video_clips: list = field(default_factory=list)
    audio_tracks: list = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            'name': self.name,
            'output_path': self.output_path,
            'resolution': self.resolution,
            'frame_rate': self.frame_rate,
            'video_clips': [c.to_dict() for c in self.video_clips],
            'audio_tracks': [a.to_dict() for a in self.audio_tracks]
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'VideoProject':
        project = cls(
            name=data['name'],
            output_path=data['output_path'],
            resolution=data.get('resolution', '1920x1080'),
            frame_rate=data.get('frame_rate', 30)
        )

        for clip_data in data.get('video_clips', []):
            clip_data['clip_type'] = ClipType(clip_data['clip_type'])
            project.video_clips.append(VideoClip(**clip_data))

        for track_data in data.get('audio_tracks', []):
            track_data['track_type'] = AudioTrackType(track_data['track_type'])
            project.audio_tracks.append(AudioTrack(**track_data))

        return project

    def save(self, path: Path):
        """Save project to JSON file."""
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding='utf-8')

    @classmethod
    def load(cls, path: Path) -> 'VideoProject':
        """Load project from JSON file."""
        data = json.loads(path.read_text(encoding='utf-8'))
        return cls.from_dict(data)

    def total_duration(self) -> float:
        """Calculate total project duration."""
        max_video = max((c.start_time + c.duration for c in self.video_clips), default=0)
        max_audio = max((a.start_time + (a.duration or 0) for a in self.audio_tracks), default=0)
        return max(max_video, max_audio)


class FFmpegAssembler:
    """Assemble video using FFmpeg."""

    def __init__(self, project: VideoProject):
        self.project = project
        self.temp_dir = Path("temp_assembly")

    def generate_concat_file(self) -> Path:
        """Generate FFmpeg concat demuxer file for video clips."""
        self.temp_dir.mkdir(exist_ok=True)
        concat_file = self.temp_dir / "concat.txt"

        # Sort clips by start time
        sorted_clips = sorted(self.project.video_clips, key=lambda c: c.start_time)

        with open(concat_file, 'w') as f:
            for clip in sorted_clips:
                # Use FFmpeg's file directive format
                source = Path(clip.source_path).absolute()
                f.write(f"file '{source}'\n")
                if clip.source_in > 0 or clip.source_out:
                    f.write(f"inpoint {clip.source_in}\n")
                    if clip.source_out:
                        f.write(f"outpoint {clip.source_out}\n")

        return concat_file

    def build_filter_complex(self) -> str:
        """Build FFmpeg filter_complex for advanced assembly."""
        filters = []
        width, height = self.project.resolution.split('x')

        # Scale and pad each video input
        for i, clip in enumerate(self.project.video_clips):
            filters.append(
                f"[{i}:v]scale={width}:{height}:force_original_aspect_ratio=decrease,"
                f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2[v{i}]"
            )

        # Concatenate all video streams
        video_streams = ''.join(f'[v{i}]' for i in range(len(self.project.video_clips)))
        filters.append(f"{video_streams}concat=n={len(self.project.video_clips)}:v=1:a=0[outv]")

        return ';'.join(filters)

    def generate_simple_command(self) -> list:
        """Generate a simple FFmpeg command for basic assembly."""
        concat_file = self.generate_concat_file()

        cmd = [
            'ffmpeg',
            '-f', 'concat',
            '-safe', '0',
            '-i', str(concat_file),
        ]

        # Add audio tracks
        for track in self.project.audio_tracks:
            cmd.extend(['-i', track.source_path])

        # Output settings
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-r', str(self.project.frame_rate),
            '-y',  # Overwrite output
            self.project.output_path
        ])

        return cmd

    def generate_complex_command(self) -> list:
        """Generate FFmpeg command with filter_complex for advanced features."""
        cmd = ['ffmpeg']

        # Add video inputs
        for clip in self.project.video_clips:
            if clip.source_in > 0:
                cmd.extend(['-ss', str(clip.source_in)])
            if clip.source_out and clip.source_out > clip.source_in:
                cmd.extend(['-t', str(clip.source_out - clip.source_in)])
            cmd.extend(['-i', clip.source_path])

        # Add audio inputs
        for track in self.project.audio_tracks:
            cmd.extend(['-i', track.source_path])

        # Build and add filter complex
        filter_complex = self.build_filter_complex()
        cmd.extend(['-filter_complex', filter_complex])

        # Map outputs
        cmd.extend(['-map', '[outv]'])

        # Audio mixing (if we have audio tracks)
        if self.project.audio_tracks:
            audio_mix = self._build_audio_mix()
            cmd.extend(['-filter_complex', audio_mix])

        # Output settings
        cmd.extend([
            '-c:v', 'libx264',
            '-preset', 'medium',
            '-crf', '23',
            '-c:a', 'aac',
            '-b:a', '192k',
            '-y',
            self.project.output_path
        ])

        return cmd

    def _build_audio_mix(self) -> str:
        """Build audio mixing filter."""
        audio_inputs = []
        num_video = len(self.project.video_clips)

        for i, track in enumerate(self.project.audio_tracks):
            input_idx = num_video + i
            volume_filter = f"[{input_idx}:a]volume={track.volume}[a{i}]"
            audio_inputs.append(f'[a{i}]')

        if len(audio_inputs) > 1:
            return f"{''.join(audio_inputs)}amix=inputs={len(audio_inputs)}[outa]"
        elif audio_inputs:
            return f"{audio_inputs[0]}anull[outa]"
        return ""

    def run(self, dry_run: bool = False) -> bool:
        """Execute the assembly."""
        cmd = self.generate_simple_command()

        print("FFmpeg command:")
        print(' '.join(cmd))

        if dry_run:
            print("\n[DRY RUN - not executing]")
            return True

        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                print(f"Error: {result.stderr}")
                return False
            print(f"Video assembled: {self.project.output_path}")
            return True
        except FileNotFoundError:
            print("Error: FFmpeg not found. Please install FFmpeg.")
            return False


def create_project_template(name: str, output_dir: Path) -> VideoProject:
    """Create a new project template."""
    project = VideoProject(
        name=name,
        output_path=str(output_dir / f"{name}_final.mp4")
    )

    # Add placeholder clips
    project.video_clips.append(VideoClip(
        source_path="recordings/intro.mp4",
        clip_type=ClipType.TITLE_CARD,
        start_time=0,
        duration=5
    ))

    project.video_clips.append(VideoClip(
        source_path="recordings/gameplay_01.mp4",
        clip_type=ClipType.GAMEPLAY,
        start_time=5,
        duration=60,
        source_in=0,
        source_out=60
    ))

    # Add placeholder audio
    project.audio_tracks.append(AudioTrack(
        source_path="audio/narration.wav",
        track_type=AudioTrackType.NARRATION,
        start_time=0,
        volume=1.0
    ))

    project.audio_tracks.append(AudioTrack(
        source_path="audio/background_music.mp3",
        track_type=AudioTrackType.MUSIC,
        start_time=0,
        volume=0.3,
        loop=True
    ))

    return project


def main():
    parser = argparse.ArgumentParser(
        description="Video assembly pipeline using FFmpeg"
    )

    parser.add_argument(
        "project_file",
        nargs="?",
        type=Path,
        help="Path to project JSON file"
    )
    parser.add_argument(
        "--create-project",
        type=str,
        metavar="NAME",
        help="Create a new project template"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("video_output"),
        help="Output directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print FFmpeg command without executing"
    )

    args = parser.parse_args()

    if args.create_project:
        args.output.mkdir(parents=True, exist_ok=True)
        project = create_project_template(args.create_project, args.output)
        project_path = args.output / f"{args.create_project}_project.json"
        project.save(project_path)
        print(f"Project template created: {project_path}")
        print("\nEdit the JSON file to configure your video clips and audio tracks.")
        return 0

    if args.project_file:
        if not args.project_file.exists():
            print(f"Error: Project file not found: {args.project_file}")
            return 1

        project = VideoProject.load(args.project_file)
        assembler = FFmpegAssembler(project)

        success = assembler.run(dry_run=args.dry_run)
        return 0 if success else 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    exit(main())
