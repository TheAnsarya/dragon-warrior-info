#!/usr/bin/env python3
"""
Generate video descriptions from script markdown files.

Extracts the Video Description Template section from episode scripts
and processes it for YouTube upload.

Usage:
    python generate_description.py episode_01_getting_started.md
    python generate_description.py --all --output descriptions/
"""

import re
import argparse
from pathlib import Path
from typing import Optional


def extract_description(markdown_content: str) -> Optional[str]:
    """
    Extract the Video Description Template from a script file.
    
    The template is expected to be in a fenced code block under
    the "## Video Description Template" heading.
    """
    # Pattern to find the description template section
    pattern = r'##\s*Video Description Template\s*\n+```(?:text)?\s*\n(.*?)```'
    
    match = re.search(pattern, markdown_content, re.DOTALL)
    
    if match:
        return match.group(1).strip()
    
    return None


def process_description(description: str, replacements: dict = None) -> str:
    """
    Process a description template with optional replacements.
    
    Replacements can include:
    - [LINK] placeholders for video links
    - Dynamic content insertion
    """
    if replacements:
        for key, value in replacements.items():
            description = description.replace(f"[{key}]", value)
    
    return description


def extract_metadata(markdown_content: str) -> dict:
    """Extract video metadata from the script header."""
    metadata = {}
    
    # Extract title
    title_match = re.search(r'\*\*Title\*\*\s*\|\s*"([^"]+)"', markdown_content)
    if title_match:
        metadata['title'] = title_match.group(1)
    
    # Extract duration
    duration_match = re.search(r'\*\*Duration\*\*\s*\|\s*([^\|]+)', markdown_content)
    if duration_match:
        metadata['duration'] = duration_match.group(1).strip()
    
    # Extract difficulty
    diff_match = re.search(r'\*\*Difficulty\*\*\s*\|\s*([^\|]+)', markdown_content)
    if diff_match:
        metadata['difficulty'] = diff_match.group(1).strip()
    
    return metadata


def generate_tags_from_description(description: str) -> list:
    """Extract hashtags and generate tag list."""
    # Find hashtags at the end (TAGS: line)
    tags_match = re.search(r'TAGS:\s*(.+)$', description, re.MULTILINE)
    if tags_match:
        tags_str = tags_match.group(1)
        # Split by comma or space
        tags = [t.strip() for t in re.split(r'[,\s]+', tags_str) if t.strip()]
        return tags
    
    # Find traditional hashtags
    hashtags = re.findall(r'#(\w+)', description)
    return hashtags


def process_all_scripts(scripts_dir: Path, output_dir: Path):
    """Process all episode scripts in a directory."""
    output_dir.mkdir(parents=True, exist_ok=True)
    
    scripts = sorted(scripts_dir.glob("episode_*.md"))
    
    for script in scripts:
        print(f"Processing: {script.name}")
        
        content = script.read_text(encoding='utf-8')
        description = extract_description(content)
        
        if description:
            output_file = output_dir / f"{script.stem}_description.txt"
            output_file.write_text(description, encoding='utf-8')
            print(f"  Created: {output_file.name}")
            
            # Also generate metadata JSON
            metadata = extract_metadata(content)
            metadata['tags'] = generate_tags_from_description(description)
            
            import json
            meta_file = output_dir / f"{script.stem}_metadata.json"
            meta_file.write_text(json.dumps(metadata, indent=2), encoding='utf-8')
            print(f"  Created: {meta_file.name}")
        else:
            print(f"  Warning: No description template found")


def main():
    parser = argparse.ArgumentParser(
        description="Generate YouTube descriptions from video scripts"
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
        help="Process all episode scripts in docs/video_scripts/"
    )
    parser.add_argument(
        "--output", "-o",
        type=Path,
        default=Path("video_descriptions"),
        help="Output directory for descriptions"
    )
    parser.add_argument(
        "--scripts-dir",
        type=Path,
        default=Path("docs/video_scripts"),
        help="Directory containing script files"
    )
    
    args = parser.parse_args()
    
    if args.all:
        process_all_scripts(args.scripts_dir, args.output)
    elif args.script_file:
        if not args.script_file.exists():
            print(f"Error: File not found: {args.script_file}")
            return 1
        
        content = args.script_file.read_text(encoding='utf-8')
        description = extract_description(content)
        
        if description:
            if args.output.is_dir():
                output_file = args.output / f"{args.script_file.stem}_description.txt"
            else:
                output_file = args.output
            
            output_file.parent.mkdir(parents=True, exist_ok=True)
            output_file.write_text(description, encoding='utf-8')
            print(f"Description saved to: {output_file}")
        else:
            print("Error: No description template found in script")
            return 1
    else:
        parser.print_help()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
