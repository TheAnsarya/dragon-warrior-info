#!/usr/bin/env python3
"""
Dragon Warrior Graphics and Palette Editor
Visual editor for game graphics, sprites, and palettes
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import click
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, Confirm
from rich import print as rprint
from PIL import Image, ImageDraw, ImageTk
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, filedialog

# Add extraction directory to path
sys.path.append(str(Path(__file__).parent.parent / 'extraction'))
from data_structures import GraphicsData, Palette, Color

console = Console()

class GraphicsEditor:
    """Visual graphics and palette editor using Tkinter"""

    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.graphics_dir = self.data_dir / "graphics"
        self.palettes_dir = self.data_dir / "palettes"
        self.json_dir = self.data_dir / "json"

        self.graphics: Dict[int, GraphicsData] = {}
        self.palettes: Dict[int, Palette] = {}
        self.current_graphic: Optional[GraphicsData] = None
        self.current_palette: Optional[Palette] = None

        # GUI components
        self.root = None
        self.canvas = None
        self.palette_frame = None
        self.tile_size = 64  # Display size for 8x8 tiles

        self.load_data()

    def load_data(self):
        """Load graphics and palette data"""
        # Load graphics
        graphics_file = self.json_dir / "graphics.json"
        if graphics_file.exists():
            with open(graphics_file, 'r', encoding='utf-8') as f:
                graphics_data = json.load(f)
                for gfx_id_str, gfx_data in graphics_data.items():
                    gfx_id = int(gfx_id_str)
                    graphic = GraphicsData(**gfx_data)
                    self.graphics[gfx_id] = graphic

        # Load palettes
        palettes_file = self.json_dir / "palettes.json"
        if palettes_file.exists():
            with open(palettes_file, 'r', encoding='utf-8') as f:
                palettes_data = json.load(f)
                for pal_id_str, pal_data in palettes_data.items():
                    pal_id = int(pal_id_str)
                    colors = [Color(**color_data) for color_data in pal_data['colors']]
                    palette = Palette(name=pal_data['name'], colors=colors)
                    self.palettes[pal_id] = palette

        console.print(f"[green]✅ Loaded {len(self.graphics)} graphics and {len(self.palettes)} palettes[/green]")

    def save_data(self):
        """Save graphics and palette data"""
        # Save graphics
        graphics_data = {str(k): v.to_dict() for k, v in self.graphics.items()}
        with open(self.json_dir / "graphics.json", 'w', encoding='utf-8') as f:
            json.dump(graphics_data, f, indent=2)

        # Save palettes
        palettes_data = {str(k): v.to_dict() for k, v in self.palettes.items()}
        with open(self.json_dir / "palettes.json", 'w', encoding='utf-8') as f:
            json.dump(palettes_data, f, indent=2)

        console.print("[green]✅ Saved graphics and palette data[/green]")

    def create_gui(self):
        """Create the main GUI window"""
        self.root = tk.Tk()
        self.root.title("Dragon Warrior Graphics & Palette Editor")
        self.root.geometry("1000x700")

        # Main layout
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left panel - Graphics list
        left_frame = ttk.LabelFrame(main_frame, text="Graphics", padding=10)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        # Graphics listbox
        self.graphics_listbox = tk.Listbox(left_frame, width=25)
        self.graphics_listbox.pack(fill=tk.BOTH, expand=True)
        self.graphics_listbox.bind('<<ListboxSelect>>', self.on_graphic_select)

        # Populate graphics list
        for gfx_id, graphic in sorted(self.graphics.items()):
            self.graphics_listbox.insert(tk.END, f"{gfx_id:03d}: {graphic.name}")

        # Center panel - Graphics canvas
        center_frame = ttk.LabelFrame(main_frame, text="Graphics Editor", padding=10)
        center_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))

        # Canvas for tile editing
        self.canvas = tk.Canvas(center_frame, width=512, height=512, bg='white')
        self.canvas.pack()
        self.canvas.bind('<Button-1>', self.on_canvas_click)
        self.canvas.bind('<B1-Motion>', self.on_canvas_drag)

        # Tool buttons
        tool_frame = ttk.Frame(center_frame)
        tool_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(tool_frame, text="Load PNG", command=self.load_png_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(tool_frame, text="Save PNG", command=self.save_png_file).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(tool_frame, text="Clear", command=self.clear_graphic).pack(side=tk.LEFT)

        # Right panel - Palettes
        right_frame = ttk.LabelFrame(main_frame, text="Palettes", padding=10)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Palette listbox
        self.palette_listbox = tk.Listbox(right_frame, width=20)
        self.palette_listbox.pack(fill=tk.X)
        self.palette_listbox.bind('<<ListboxSelect>>', self.on_palette_select)

        # Populate palette list
        for pal_id, palette in sorted(self.palettes.items()):
            self.palette_listbox.insert(tk.END, f"{pal_id}: {palette.name}")

        # Color buttons frame
        self.palette_frame = ttk.Frame(right_frame)
        self.palette_frame.pack(fill=tk.X, pady=(10, 0))

        # Palette tool buttons
        palette_tool_frame = ttk.Frame(right_frame)
        palette_tool_frame.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(palette_tool_frame, text="New Palette", command=self.create_palette).pack(fill=tk.X, pady=(0, 5))
        ttk.Button(palette_tool_frame, text="Export Palette", command=self.export_palette).pack(fill=tk.X)

        # Status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Menu bar
        self.create_menu()

        # Current drawing color
        self.current_color_index = 0

        return self.root

    def create_menu(self):
        """Create menu bar"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Save All", command=self.save_data)
        file_menu.add_command(label="Export All Graphics", command=self.export_all_graphics)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Create New Graphic", command=self.create_new_graphic)
        edit_menu.add_command(label="Duplicate Graphic", command=self.duplicate_graphic)
        edit_menu.add_command(label="Delete Graphic", command=self.delete_graphic)

    def on_graphic_select(self, event):
        """Handle graphics list selection"""
        selection = self.graphics_listbox.curselection()
        if selection:
            index = selection[0]
            gfx_id = list(sorted(self.graphics.keys()))[index]
            self.current_graphic = self.graphics[gfx_id]
            self.display_graphic()
            self.status_var.set(f"Selected: {self.current_graphic.name}")

    def on_palette_select(self, event):
        """Handle palette list selection"""
        selection = self.palette_listbox.curselection()
        if selection:
            index = selection[0]
            pal_id = list(sorted(self.palettes.keys()))[index]
            self.current_palette = self.palettes[pal_id]
            self.display_palette()
            self.display_graphic()  # Refresh graphic with new palette
            self.status_var.set(f"Selected palette: {self.current_palette.name}")

    def display_graphic(self):
        """Display current graphic on canvas"""
        if not self.current_graphic or not self.current_palette:
            return

        self.canvas.delete("all")

        # Draw 8x8 grid scaled up
        tile_data = self.current_graphic.tile_data

        if len(tile_data) >= 16:  # Valid NES tile data
            # Decode NES tile format
            pixels = self.decode_nes_tile(tile_data)

            # Draw pixels
            pixel_size = self.tile_size // 8
            for y in range(8):
                for x in range(8):
                    color_index = pixels[y][x]
                    if color_index < len(self.current_palette.colors):
                        color = self.current_palette.colors[color_index]
                        hex_color = f"#{color.r:02x}{color.g:02x}{color.b:02x}"

                        x1 = x * pixel_size
                        y1 = y * pixel_size
                        x2 = x1 + pixel_size
                        y2 = y1 + pixel_size

                        self.canvas.create_rectangle(x1, y1, x2, y2, fill=hex_color, outline="gray")

    def decode_nes_tile(self, tile_data: List[int]) -> List[List[int]]:
        """Decode NES 8x8 tile to 2D pixel array"""
        pixels = [[0] * 8 for _ in range(8)]

        if len(tile_data) >= 16:
            for y in range(8):
                plane1 = tile_data[y]
                plane2 = tile_data[y + 8]

                for x in range(8):
                    bit = 7 - x
                    pixel_value = ((plane1 >> bit) & 1) | (((plane2 >> bit) & 1) << 1)
                    pixels[y][x] = pixel_value

        return pixels

    def encode_nes_tile(self, pixels: List[List[int]]) -> List[int]:
        """Encode 2D pixel array to NES tile format"""
        tile_data = [0] * 16

        for y in range(8):
            plane1 = 0
            plane2 = 0

            for x in range(8):
                if y < len(pixels) and x < len(pixels[y]):
                    pixel_value = pixels[y][x]
                    bit = 7 - x

                    plane1 |= ((pixel_value & 1) << bit)
                    plane2 |= (((pixel_value >> 1) & 1) << bit)

            tile_data[y] = plane1
            tile_data[y + 8] = plane2

        return tile_data

    def display_palette(self):
        """Display current palette colors"""
        # Clear existing palette display
        for widget in self.palette_frame.winfo_children():
            widget.destroy()

        if not self.current_palette:
            return

        # Create color buttons
        for i, color in enumerate(self.current_palette.colors):
            hex_color = f"#{color.r:02x}{color.g:02x}{color.b:02x}"

            color_button = tk.Button(
                self.palette_frame,
                bg=hex_color,
                width=3,
                height=2,
                command=lambda idx=i: self.select_color(idx)
            )
            color_button.pack(side=tk.TOP, pady=2)
            color_button.bind('<Button-3>', lambda e, idx=i: self.edit_color(idx))  # Right click to edit

    def select_color(self, color_index: int):
        """Select a color for drawing"""
        self.current_color_index = color_index
        self.status_var.set(f"Selected color {color_index}")

    def edit_color(self, color_index: int):
        """Edit a palette color"""
        if not self.current_palette or color_index >= len(self.current_palette.colors):
            return

        current_color = self.current_palette.colors[color_index]
        initial_color = f"#{current_color.r:02x}{current_color.g:02x}{current_color.b:02x}"

        new_color = colorchooser.askcolor(initialcolor=initial_color, title=f"Edit Color {color_index}")
        if new_color[0]:  # User didn't cancel
            r, g, b = [int(c) for c in new_color[0]]
            self.current_palette.colors[color_index] = Color(r, g, b)
            self.display_palette()
            self.display_graphic()
            self.status_var.set(f"Updated color {color_index}")

    def on_canvas_click(self, event):
        """Handle canvas click for pixel editing"""
        self.paint_pixel(event.x, event.y)

    def on_canvas_drag(self, event):
        """Handle canvas drag for pixel editing"""
        self.paint_pixel(event.x, event.y)

    def paint_pixel(self, canvas_x: int, canvas_y: int):
        """Paint a pixel at canvas coordinates"""
        if not self.current_graphic or not self.current_palette:
            return

        # Convert canvas coordinates to tile coordinates
        pixel_size = self.tile_size // 8
        tile_x = canvas_x // pixel_size
        tile_y = canvas_y // pixel_size

        if 0 <= tile_x < 8 and 0 <= tile_y < 8:
            # Decode current tile
            pixels = self.decode_nes_tile(self.current_graphic.tile_data)

            # Set pixel color
            pixels[tile_y][tile_x] = self.current_color_index

            # Encode back to tile data
            self.current_graphic.tile_data = self.encode_nes_tile(pixels)

            # Refresh display
            self.display_graphic()

    def load_png_file(self):
        """Load PNG file as graphic"""
        if not self.current_graphic:
            messagebox.showwarning("Warning", "Select a graphic first")
            return

        file_path = filedialog.askopenfilename(
            title="Load PNG",
            filetypes=[("PNG files", "*.png")],
            initialdir=str(self.graphics_dir)
        )

        if file_path:
            try:
                img = Image.open(file_path)
                img = img.resize((8, 8), Image.NEAREST)
                img = img.convert('RGB')

                # Convert to palette indices (simplified)
                pixels = [[0] * 8 for _ in range(8)]
                for y in range(8):
                    for x in range(8):
                        r, g, b = img.getpixel((x, y))
                        # Find closest palette color
                        closest_index = 0
                        min_distance = float('inf')

                        if self.current_palette:
                            for i, pal_color in enumerate(self.current_palette.colors):
                                distance = ((r - pal_color.r) ** 2 +
                                          (g - pal_color.g) ** 2 +
                                          (b - pal_color.b) ** 2) ** 0.5
                                if distance < min_distance:
                                    min_distance = distance
                                    closest_index = i

                        pixels[y][x] = closest_index

                # Update tile data
                self.current_graphic.tile_data = self.encode_nes_tile(pixels)
                self.display_graphic()
                self.status_var.set(f"Loaded PNG: {Path(file_path).name}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to load PNG: {e}")

    def save_png_file(self):
        """Save current graphic as PNG"""
        if not self.current_graphic or not self.current_palette:
            messagebox.showwarning("Warning", "Select a graphic and palette first")
            return

        file_path = filedialog.asksaveasfilename(
            title="Save PNG",
            defaultextension=".png",
            filetypes=[("PNG files", "*.png")],
            initialdir=str(self.graphics_dir),
            initialname=f"{self.current_graphic.name}.png"
        )

        if file_path:
            try:
                # Create 8x8 image
                img = Image.new('RGB', (8, 8))
                pixels = self.decode_nes_tile(self.current_graphic.tile_data)

                pixel_data = []
                for y in range(8):
                    for x in range(8):
                        color_index = pixels[y][x]
                        if color_index < len(self.current_palette.colors):
                            color = self.current_palette.colors[color_index]
                            pixel_data.append((color.r, color.g, color.b))
                        else:
                            pixel_data.append((0, 0, 0))

                img.putdata(pixel_data)

                # Scale up for visibility
                img = img.resize((64, 64), Image.NEAREST)
                img.save(file_path)

                self.status_var.set(f"Saved PNG: {Path(file_path).name}")

            except Exception as e:
                messagebox.showerror("Error", f"Failed to save PNG: {e}")

    def create_new_graphic(self):
        """Create a new graphic"""
        # Get next available ID
        max_id = max(self.graphics.keys()) if self.graphics else -1
        new_id = max_id + 1

        # Create empty 8x8 tile
        empty_tile_data = [0] * 16

        new_graphic = GraphicsData(
            id=new_id,
            name=f"NewGraphic_{new_id:03d}",
            width=8,
            height=8,
            tile_data=empty_tile_data,
            palette_id=0
        )

        self.graphics[new_id] = new_graphic

        # Update graphics listbox
        self.graphics_listbox.insert(tk.END, f"{new_id:03d}: {new_graphic.name}")

        self.status_var.set(f"Created graphic {new_id}")

    def run(self):
        """Run the graphics editor GUI"""
        root = self.create_gui()

        # Select first items if available
        if self.graphics_listbox.size() > 0:
            self.graphics_listbox.select_set(0)
            self.on_graphic_select(None)

        if self.palette_listbox.size() > 0:
            self.palette_listbox.select_set(0)
            self.on_palette_select(None)

        root.mainloop()

@click.command()
@click.argument('data_dir', type=click.Path(exists=True))
def edit_graphics(data_dir: str):
    """Dragon Warrior Graphics & Palette Editor"""
    editor = GraphicsEditor(data_dir)
    editor.run()

if __name__ == "__main__":
    edit_graphics()
