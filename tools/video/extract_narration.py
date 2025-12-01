#!/usr/bin/env python3
"""
Extract narration text from video script markdown files.

Converts markdown scripts to teleprompter-ready format or structured JSON
for AI text-to-speech processing.

Usage:
    python extract_narration.py episode_01_getting_started.md
    python extract_narration.py episode_01_getting_started.md --format json
    python extract_narration.py episode_01_getting_started.md --output teleprompter.txt
"""

import re
import json
import argparse
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Optional


@dataclass
class NarrationBlock:
    """A single narration block with metadata."""
    
    index: int
    timestamp: Optional[str]
    section_title: Optional[str]
    text: str
    visual_cue: Optional[str]
    duration_hint: Optional[str]
    
    def to_teleprompter(self) -> str:
        """Format for teleprompter display."""
        lines = []
        if self.timestamp:
            lines.append(f"[{self.timestamp}]")
        if self.section_title:
            lines.append(f"=== {self.section_title} ===")
        lines.append("")
        lines.append(self.text)
        lines.append("")
        return "\n".join(lines)
    
    def to_tts_text(self) -> str:
        """Format for text-to-speech processing."""
        # Clean up text for TTS
        text = self.text
        # Remove code formatting
        text = re.sub(r'`([^`]+)`', r'\1', text)
        # Expand common abbreviations
        text = text.replace("e.g.", "for example")
        text = text.replace("etc.", "et cetera")
        text = text.replace("i.e.", "that is")
        return text


def extract_narration_blocks(markdown_content: str) -> List[NarrationBlock]:
    """
    Extract all narration blocks from a video script markdown file.
    
    Narration is expected to be in blockquote format:
    > "Narration text here..."
    
    With optional visual cues:
    **[VISUAL: Description]**
    """
    blocks = []
    
    # Find all sections with timestamps
    section_pattern = r'###\s*\[([^\]]+)\]\s*([^\n]+)'
    sections = list(re.finditer(section_pattern, markdown_content))
    
    # Find all narration blocks (blockquotes with quotes)
    narration_pattern = r'>\s*"([^"]+(?:\n>[^"]*)*)"'
    
    current_section = None
    current_timestamp = None
    current_duration = None
    
    # Process the markdown line by line to track context
    lines = markdown_content.split('\n')
    in_narration = False
    current_narration = []
    last_visual = None
    block_index = 0
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for section header with timestamp
        section_match = re.match(r'###\s*\[([^\]]+)\]\s*(.+?)(?:\s*\(([^)]+)\))?$', line)
        if section_match:
            current_timestamp = section_match.group(1)
            current_section = section_match.group(2).strip()
            current_duration = section_match.group(3) if section_match.lastindex >= 3 else None
        
        # Check for visual cue
        visual_match = re.match(r'\*\*\[VISUAL:\s*([^\]]+)\]\*\*', line)
        if visual_match:
            last_visual = visual_match.group(1)
        
        # Check for narration start
        if line.strip().startswith('> "'):
            in_narration = True
            # Extract text after > "
            text = line.strip()[3:]  # Remove '> "'
            if text.endswith('"'):
                text = text[:-1]
                in_narration = False
                blocks.append(NarrationBlock(
                    index=block_index,
                    timestamp=current_timestamp,
                    section_title=current_section,
                    text=text,
                    visual_cue=last_visual,
                    duration_hint=current_duration
                ))
                block_index += 1
                last_visual = None
            else:
                current_narration = [text]
        elif in_narration:
            # Continuation of narration
            if line.strip().startswith('>'):
                text = line.strip()[1:].strip()
                if text.startswith('"'):
                    text = text[1:]
                if text.endswith('"'):
                    text = text[:-1]
                    current_narration.append(text)
                    blocks.append(NarrationBlock(
                        index=block_index,
                        timestamp=current_timestamp,
                        section_title=current_section,
                        text=' '.join(current_narration),
                        visual_cue=last_visual,
                        duration_hint=current_duration
                    ))
                    block_index += 1
                    in_narration = False
                    current_narration = []
                    last_visual = None
                else:
                    current_narration.append(text)
            else:
                # End of blockquote
                if current_narration:
                    blocks.append(NarrationBlock(
                        index=block_index,
                        timestamp=current_timestamp,
                        section_title=current_section,
                        text=' '.join(current_narration),
                        visual_cue=last_visual,
                        duration_hint=current_duration
                    ))
                    block_index += 1
                in_narration = False
                current_narration = []
                last_visual = None
        
        i += 1
    
    return blocks


def format_for_teleprompter(blocks: List[NarrationBlock]) -> str:
    """Format narration blocks for teleprompter display."""
    output = []
    output.append("=" * 60)
    output.append("TELEPROMPTER SCRIPT")
    output.append("=" * 60)
    output.append("")
    
    for block in blocks:
        output.append(block.to_teleprompter())
        output.append("-" * 40)
    
    return "\n".join(output)


def format_for_tts(blocks: List[NarrationBlock]) -> List[dict]:
    """Format narration blocks for TTS processing."""
    return [
        {
            "index": block.index,
            "timestamp": block.timestamp,
            "section": block.section_title,
            "text": block.to_tts_text(),
            "visual_cue": block.visual_cue
        }
        for block in blocks
    ]


def format_for_json(blocks: List[NarrationBlock]) -> str:
    """Format narration blocks as JSON."""
    return json.dumps([asdict(block) for block in blocks], indent=2)


def main():
    parser = argparse.ArgumentParser(
        description="Extract narration from video script markdown files"
    )
    parser.add_argument(
        "script_file",
        type=Path,
        help="Path to the markdown script file"
    )
    parser.add_argument(
        "--format",
        choices=["teleprompter", "json", "tts"],
        default="teleprompter",
        help="Output format (default: teleprompter)"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        help="Output file path (default: stdout)"
    )
    
    args = parser.parse_args()
    
    if not args.script_file.exists():
        print(f"Error: File not found: {args.script_file}")
        return 1
    
    content = args.script_file.read_text(encoding='utf-8')
    blocks = extract_narration_blocks(content)
    
    if not blocks:
        print("Warning: No narration blocks found in script")
        return 1
    
    print(f"Found {len(blocks)} narration blocks", file=__import__('sys').stderr)
    
    if args.format == "teleprompter":
        output = format_for_teleprompter(blocks)
    elif args.format == "json":
        output = format_for_json(blocks)
    elif args.format == "tts":
        output = json.dumps(format_for_tts(blocks), indent=2)
    
    if args.output:
        args.output.write_text(output, encoding='utf-8')
        print(f"Written to: {args.output}", file=__import__('sys').stderr)
    else:
        print(output)
    
    return 0


if __name__ == "__main__":
    exit(main())
