#!/usr/bin/env python3
"""
Sprite Animation Generator

Generate animated GIFs of Dragon Warrior monster sprites.

Features:
- Create walking/idle animations
- Battle entrance animations
- Export as GIF or sprite sheets
- Configurable frame timing

Usage:
    python tools/sprite_animator.py --monster "Slime"
    python tools/sprite_animator.py --monster "Dragon" --frames 8
    python tools/sprite_animator.py --all --output animations/

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import argparse
from pathlib import Path
from typing import List, Tuple

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("ERROR: PIL/Pillow is required")
    print("Install with: pip install pillow")
    sys.exit(1)

# Default paths
DEFAULT_ASSETS = "extracted_assets"
DEFAULT_OUTPUT = "output/animations"

# NES palette
NES_PALETTE = [
    (124, 124, 124), (0, 0, 252), (0, 0, 188), (68, 40, 188),
    (148, 0, 132), (168, 0, 32), (168, 16, 0), (136, 20, 0),
    (80, 48, 0), (0, 120, 0), (0, 104, 0), (0, 88, 0),
    (0, 64, 88), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (188, 188, 188), (0, 120, 248), (0, 88, 248), (104, 68, 252),
    (216, 0, 204), (228, 0, 88), (248, 56, 0), (228, 92, 16),
    (172, 124, 0), (0, 184, 0), (0, 168, 0), (0, 168, 68),
    (0, 136, 136), (0, 0, 0), (0, 0, 0), (0, 0, 0),
    (248, 248, 248), (60, 188, 252), (104, 136, 252), (152, 120, 248),
    (248, 120, 248), (248, 88, 152), (248, 120, 88), (252, 160, 68),
    (248, 184, 0), (184, 248, 24), (88, 216, 84), (88, 248, 152),
    (0, 232, 216), (120, 120, 120), (0, 0, 0), (0, 0, 0),
    (252, 252, 252), (164, 228, 252), (184, 184, 248), (216, 184, 248),
    (248, 184, 248), (248, 164, 192), (240, 208, 176), (252, 224, 168),
    (248, 216, 120), (216, 248, 120), (184, 248, 184), (184, 248, 216),
    (0, 252, 252), (248, 216, 248), (0, 0, 0), (0, 0, 0)
]


class SpriteAnimator:
    """Generate sprite animations"""
    
    def __init__(self, assets_dir: str, output_dir: str):
        """
        Initialize animator
        
        Args:
            assets_dir: Assets directory
            output_dir: Output directory
        """
        self.assets_dir = Path(assets_dir)
        self.output_dir = Path(output_dir)
        self.graphics_dir = self.assets_dir / "graphics"
    
    def load_chr_tiles(self) -> Image.Image:
        """Load CHR tile sheet"""
        chr_file = self.graphics_dir / "chr_tiles.png"
        
        if not chr_file.exists():
            raise FileNotFoundError(f"CHR tiles not found: {chr_file}")
        
        return Image.open(chr_file)
    
    def get_monster_tiles(self, monster_name: str) -> List[Tuple[int, int]]:
        """
        Get tile coordinates for monster sprite
        
        Args:
            monster_name: Monster name
            
        Returns:
            List of (tile_x, tile_y) coordinates
        """
        # Simplified - would need sprite definition data
        # For demo, return generic 4×4 sprite (16 tiles)
        
        base_x = 0  # Would lookup from sprite data
        base_y = 0
        
        tiles = []
        for y in range(4):
            for x in range(4):
                tiles.append((base_x + x, base_y + y))
        
        return tiles
    
    def extract_sprite(self, chr_img: Image.Image, tiles: List[Tuple[int, int]], 
                       scale: int = 2) -> Image.Image:
        """
        Extract sprite from CHR tiles
        
        Args:
            chr_img: CHR tile sheet
            tiles: List of tile coordinates
            scale: Upscale factor
            
        Returns:
            Sprite image
        """
        # Calculate sprite dimensions
        max_x = max(t[0] for t in tiles)
        max_y = max(t[1] for t in tiles)
        
        width = (max_x + 1) * 8
        height = (max_y + 1) * 8
        
        # Create sprite image
        sprite = Image.new('RGB', (width, height), (0, 0, 0))
        
        # Copy tiles
        for tile_x, tile_y in tiles:
            # Extract 8×8 tile
            px = tile_x * 8
            py = tile_y * 8
            
            tile = chr_img.crop((px, py, px + 8, py + 8))
            
            # Paste into sprite
            sprite.paste(tile, (tile_x * 8, tile_y * 8))
        
        # Scale up
        if scale > 1:
            sprite = sprite.resize(
                (width * scale, height * scale),
                Image.NEAREST  # Pixelated scaling
            )
        
        return sprite
    
    def create_idle_animation(self, sprite: Image.Image, frames: int = 2) -> List[Image.Image]:
        """
        Create idle animation (subtle movement)
        
        Args:
            sprite: Base sprite image
            frames: Number of frames
            
        Returns:
            List of animation frames
        """
        animation = []
        
        for i in range(frames):
            # Create frame with slight vertical offset
            frame = Image.new('RGB', sprite.size, (0, 0, 0))
            
            offset_y = 1 if i % 2 == 0 else -1
            
            frame.paste(sprite, (0, offset_y))
            animation.append(frame)
        
        return animation
    
    def create_battle_entrance(self, sprite: Image.Image, frames: int = 8) -> List[Image.Image]:
        """
        Create battle entrance animation (fade in + shake)
        
        Args:
            sprite: Base sprite image
            frames: Number of frames
            
        Returns:
            List of animation frames
        """
        animation = []
        width, height = sprite.size
        
        for i in range(frames):
            frame = Image.new('RGB', sprite.size, (0, 0, 0))
            
            # Fade in effect (transparency simulation)
            if i < frames // 2:
                alpha = int((i / (frames // 2)) * 255)
            else:
                alpha = 255
            
            # Shake effect
            if i < frames - 2:
                shake_x = (i % 2) * 2 - 1
                shake_y = ((i + 1) % 2) * 2 - 1
            else:
                shake_x = shake_y = 0
            
            # Create faded sprite
            faded = sprite.copy()
            if alpha < 255:
                # Darken sprite for fade effect
                pixels = faded.load()
                for y in range(height):
                    for x in range(width):
                        r, g, b = pixels[x, y]
                        factor = alpha / 255.0
                        pixels[x, y] = (
                            int(r * factor),
                            int(g * factor),
                            int(b * factor)
                        )
            
            frame.paste(faded, (shake_x, shake_y))
            animation.append(frame)
        
        return animation
    
    def create_damage_animation(self, sprite: Image.Image, frames: int = 4) -> List[Image.Image]:
        """
        Create damage flash animation
        
        Args:
            sprite: Base sprite image
            frames: Number of frames
            
        Returns:
            List of animation frames
        """
        animation = []
        width, height = sprite.size
        
        for i in range(frames):
            if i % 2 == 0:
                # Flash white
                frame = Image.new('RGB', sprite.size, (255, 255, 255))
            else:
                # Normal sprite
                frame = sprite.copy()
            
            animation.append(frame)
        
        # Add final normal frame
        animation.append(sprite.copy())
        
        return animation
    
    def save_as_gif(self, frames: List[Image.Image], output_path: Path, 
                    duration: int = 100, loop: int = 0):
        """
        Save animation as GIF
        
        Args:
            frames: Animation frames
            output_path: Output file path
            duration: Frame duration in ms
            loop: Loop count (0 = infinite)
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=duration,
            loop=loop
        )
        
        print(f"✓ Saved GIF: {output_path}")
    
    def save_as_sprite_sheet(self, frames: List[Image.Image], output_path: Path):
        """
        Save animation as sprite sheet
        
        Args:
            frames: Animation frames
            output_path: Output file path
        """
        if not frames:
            return
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Calculate dimensions
        frame_width, frame_height = frames[0].size
        sheet_width = frame_width * len(frames)
        sheet_height = frame_height
        
        # Create sprite sheet
        sheet = Image.new('RGB', (sheet_width, sheet_height), (0, 0, 0))
        
        # Paste frames
        for i, frame in enumerate(frames):
            sheet.paste(frame, (i * frame_width, 0))
        
        sheet.save(output_path)
        print(f"✓ Saved sprite sheet: {output_path}")
    
    def generate_monster_animations(self, monster_name: str, 
                                     animation_types: List[str] = None):
        """
        Generate all animations for a monster
        
        Args:
            monster_name: Monster name
            animation_types: Types to generate (idle, entrance, damage)
        """
        if animation_types is None:
            animation_types = ['idle', 'entrance', 'damage']
        
        print(f"\n--- Generating animations for {monster_name} ---")
        
        # Load CHR tiles
        chr_img = self.load_chr_tiles()
        
        # Get monster tiles
        tiles = self.get_monster_tiles(monster_name)
        
        # Extract base sprite
        sprite = self.extract_sprite(chr_img, tiles, scale=4)
        
        # Generate animations
        if 'idle' in animation_types:
            idle_frames = self.create_idle_animation(sprite, frames=2)
            self.save_as_gif(
                idle_frames,
                self.output_dir / f"{monster_name}_idle.gif",
                duration=500
            )
            self.save_as_sprite_sheet(
                idle_frames,
                self.output_dir / f"{monster_name}_idle_sheet.png"
            )
        
        if 'entrance' in animation_types:
            entrance_frames = self.create_battle_entrance(sprite, frames=8)
            self.save_as_gif(
                entrance_frames,
                self.output_dir / f"{monster_name}_entrance.gif",
                duration=100,
                loop=1  # Play once
            )
            self.save_as_sprite_sheet(
                entrance_frames,
                self.output_dir / f"{monster_name}_entrance_sheet.png"
            )
        
        if 'damage' in animation_types:
            damage_frames = self.create_damage_animation(sprite, frames=4)
            self.save_as_gif(
                damage_frames,
                self.output_dir / f"{monster_name}_damage.gif",
                duration=80,
                loop=1
            )
            self.save_as_sprite_sheet(
                damage_frames,
                self.output_dir / f"{monster_name}_damage_sheet.png"
            )


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Generate sprite animations for Dragon Warrior monsters',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate all animations for Slime
  python tools/sprite_animator.py --monster "Slime"
  
  # Only idle animation
  python tools/sprite_animator.py --monster "Dragon" --type idle
  
  # All monsters (if implemented)
  python tools/sprite_animator.py --all
        """
    )
    
    parser.add_argument(
        '--assets',
        default=DEFAULT_ASSETS,
        help=f'Assets directory (default: {DEFAULT_ASSETS})'
    )
    
    parser.add_argument(
        '--output',
        default=DEFAULT_OUTPUT,
        help=f'Output directory (default: {DEFAULT_OUTPUT})'
    )
    
    parser.add_argument(
        '--monster',
        help='Monster name to animate'
    )
    
    parser.add_argument(
        '--type',
        choices=['idle', 'entrance', 'damage', 'all'],
        default='all',
        help='Animation type(s) to generate'
    )
    
    parser.add_argument(
        '--all',
        action='store_true',
        help='Generate for all monsters'
    )
    
    args = parser.parse_args()
    
    # Initialize animator
    animator = SpriteAnimator(args.assets, args.output)
    
    # Determine animation types
    if args.type == 'all':
        types = ['idle', 'entrance', 'damage']
    else:
        types = [args.type]
    
    # Generate animations
    if args.all:
        # Would iterate all monsters
        print("--all flag: Not yet implemented (need monster list)")
        return 1
    elif args.monster:
        animator.generate_monster_animations(args.monster, types)
    else:
        print("ERROR: Specify --monster or --all")
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
