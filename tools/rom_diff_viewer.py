"""
Dragon Warrior ROM Diff Viewer
Compare two ROM versions and visualize differences

This tool provides comprehensive ROM comparison with multiple visualization modes:
- Hex diff view
- Visual difference map
- Change statistics
- Export diff reports

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import os
import struct
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from tkinter import font as tkfont


@dataclass
class DiffRegion:
    """Contiguous region of differences"""
    start_offset: int
    end_offset: int
    original_bytes: bytes
    modified_bytes: bytes
    
    @property
    def size(self) -> int:
        return self.end_offset - self.start_offset + 1
    
    @property
    def description(self) -> str:
        if self.size == 1:
            return f"1 byte changed at 0x{self.start_offset:06X}"
        return f"{self.size} bytes changed at 0x{self.start_offset:06X}-0x{self.end_offset:06X}"


@dataclass
class DiffStats:
    """Statistics about ROM differences"""
    total_bytes_compared: int
    bytes_different: int
    bytes_identical: int
    percent_different: float
    diff_regions: List[DiffRegion]
    
    @property
    def summary(self) -> str:
        lines = [
            f"Total bytes compared: {self.total_bytes_compared:,}",
            f"Bytes different: {self.bytes_different:,} ({self.percent_different:.2f}%)",
            f"Bytes identical: {self.bytes_identical:,}",
            f"Difference regions: {len(self.diff_regions)}",
        ]
        return '\n'.join(lines)


class ROMComparer:
    """Core ROM comparison engine"""
    
    @staticmethod
    def compare_roms(rom1: bytes, rom2: bytes, merge_threshold: int = 16) -> DiffStats:
        """
        Compare two ROMs and return statistics
        
        Args:
            rom1: First ROM data
            rom2: Second ROM data
            merge_threshold: Merge diff regions if separated by fewer bytes
        
        Returns:
            DiffStats object with comparison results
        """
        # Pad shorter ROM
        max_len = max(len(rom1), len(rom2))
        rom1_padded = rom1 + b'\x00' * (max_len - len(rom1))
        rom2_padded = rom2 + b'\x00' * (max_len - len(rom2))
        
        # Find all differences
        raw_regions = []
        i = 0
        while i < max_len:
            if rom1_padded[i] != rom2_padded[i]:
                # Found difference
                start = i
                while i < max_len and rom1_padded[i] != rom2_padded[i]:
                    i += 1
                
                raw_regions.append(DiffRegion(
                    start_offset=start,
                    end_offset=i - 1,
                    original_bytes=rom1_padded[start:i],
                    modified_bytes=rom2_padded[start:i]
                ))
            else:
                i += 1
        
        # Merge nearby regions
        merged_regions = ROMComparer._merge_regions(raw_regions, merge_threshold)
        
        # Calculate stats
        bytes_different = sum(r.size for r in merged_regions)
        bytes_identical = max_len - bytes_different
        percent_different = (bytes_different / max_len * 100) if max_len > 0 else 0
        
        return DiffStats(
            total_bytes_compared=max_len,
            bytes_different=bytes_different,
            bytes_identical=bytes_identical,
            percent_different=percent_different,
            diff_regions=merged_regions
        )
    
    @staticmethod
    def _merge_regions(regions: List[DiffRegion], threshold: int) -> List[DiffRegion]:
        """Merge diff regions that are close together"""
        if not regions:
            return []
        
        merged = [regions[0]]
        
        for region in regions[1:]:
            last = merged[-1]
            gap = region.start_offset - last.end_offset - 1
            
            if gap <= threshold:
                # Merge regions
                merged[-1] = DiffRegion(
                    start_offset=last.start_offset,
                    end_offset=region.end_offset,
                    original_bytes=last.original_bytes + b'\x00' * gap + region.original_bytes,
                    modified_bytes=last.modified_bytes + b'\x00' * gap + region.modified_bytes
                )
            else:
                merged.append(region)
        
        return merged
    
    @staticmethod
    def export_diff_report(rom1_path: str, rom2_path: str, stats: DiffStats, output_path: str):
        """Export comprehensive diff report to text file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write("DRAGON WARRIOR ROM DIFFERENCE REPORT\n")
            f.write("=" * 80 + "\n\n")
            
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            f.write(f"ROM 1: {os.path.basename(rom1_path)}\n")
            f.write(f"ROM 2: {os.path.basename(rom2_path)}\n\n")
            
            f.write("SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(stats.summary + "\n\n")
            
            f.write("DIFFERENCE REGIONS\n")
            f.write("-" * 80 + "\n\n")
            
            for i, region in enumerate(stats.diff_regions, 1):
                f.write(f"Region {i}: {region.description}\n")
                f.write(f"  Offset: 0x{region.start_offset:06X} - 0x{region.end_offset:06X}\n")
                f.write(f"  Size: {region.size} bytes\n")
                
                # Show hex dump (first 64 bytes max)
                max_bytes = min(64, region.size)
                f.write(f"  Original: {region.original_bytes[:max_bytes].hex(' ').upper()}")
                if region.size > max_bytes:
                    f.write(" ...")
                f.write("\n")
                
                f.write(f"  Modified: {region.modified_bytes[:max_bytes].hex(' ').upper()}")
                if region.size > max_bytes:
                    f.write(" ...")
                f.write("\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")


class ROMDiffViewerGUI:
    """GUI for ROM comparison and diff viewing"""
    
    # Color scheme for diff highlighting
    COLOR_DIFFERENT = '#FFE0E0'
    COLOR_IDENTICAL = '#E0FFE0'
    COLOR_HEADER = '#E0E0FF'
    
    def __init__(self, master=None):
        self.master = master or tk.Tk()
        self.master.title("Dragon Warrior ROM Diff Viewer")
        self.master.geometry("1200x800")
        
        # Variables
        self.rom1_path = tk.StringVar()
        self.rom2_path = tk.StringVar()
        self.rom1_data: Optional[bytes] = None
        self.rom2_data: Optional[bytes] = None
        self.diff_stats: Optional[DiffStats] = None
        self.current_region_index = 0
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup GUI layout"""
        # Top panel: File selection
        top_frame = ttk.Frame(self.master)
        top_frame.pack(fill='x', padx=5, pady=5)
        
        # ROM 1
        ttk.Label(top_frame, text="ROM 1:").grid(row=0, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(top_frame, textvariable=self.rom1_path, width=50).grid(row=0, column=1, padx=5, pady=2)
        ttk.Button(top_frame, text="Browse...", command=self.browse_rom1).grid(row=0, column=2, padx=5, pady=2)
        
        # ROM 2
        ttk.Label(top_frame, text="ROM 2:").grid(row=1, column=0, sticky='w', padx=5, pady=2)
        ttk.Entry(top_frame, textvariable=self.rom2_path, width=50).grid(row=1, column=1, padx=5, pady=2)
        ttk.Button(top_frame, text="Browse...", command=self.browse_rom2).grid(row=1, column=2, padx=5, pady=2)
        
        # Compare button
        ttk.Button(top_frame, text="Compare ROMs", command=self.compare_roms, width=15).grid(row=0, column=3, rowspan=2, padx=10, pady=2)
        
        # Notebook for different views
        self.notebook = ttk.Notebook(self.master)
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Summary tab
        summary_frame = ttk.Frame(self.notebook)
        self.notebook.add(summary_frame, text='Summary')
        self.setup_summary_tab(summary_frame)
        
        # Hex Diff tab
        hexdiff_frame = ttk.Frame(self.notebook)
        self.notebook.add(hexdiff_frame, text='Hex Diff')
        self.setup_hexdiff_tab(hexdiff_frame)
        
        # Visual Map tab
        visualmap_frame = ttk.Frame(self.notebook)
        self.notebook.add(visualmap_frame, text='Visual Map')
        self.setup_visualmap_tab(visualmap_frame)
        
        # Regions List tab
        regions_frame = ttk.Frame(self.notebook)
        self.notebook.add(regions_frame, text='Regions')
        self.setup_regions_tab(regions_frame)
    
    def setup_summary_tab(self, parent):
        """Setup Summary tab"""
        # Stats display
        self.summary_text = scrolledtext.ScrolledText(parent, width=100, height=30, font=('Courier', 10))
        self.summary_text.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Export button
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill='x', padx=5, pady=5)
        ttk.Button(button_frame, text="Export Report", command=self.export_report).pack(side='left', padx=5)
    
    def setup_hexdiff_tab(self, parent):
        """Setup Hex Diff tab"""
        # Navigation controls
        nav_frame = ttk.Frame(parent)
        nav_frame.pack(fill='x', padx=5, pady=5)
        
        ttk.Label(nav_frame, text="Jump to offset:").pack(side='left', padx=5)
        self.offset_entry = ttk.Entry(nav_frame, width=10)
        self.offset_entry.pack(side='left', padx=5)
        ttk.Button(nav_frame, text="Go", command=self.jump_to_offset).pack(side='left', padx=5)
        
        ttk.Button(nav_frame, text="Previous Diff", command=self.prev_diff).pack(side='left', padx=20)
        ttk.Button(nav_frame, text="Next Diff", command=self.next_diff).pack(side='left', padx=5)
        
        # Hex display (side-by-side)
        display_frame = ttk.Frame(parent)
        display_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        # ROM 1 hex view
        rom1_frame = ttk.LabelFrame(display_frame, text="ROM 1")
        rom1_frame.pack(side='left', fill='both', expand=True, padx=2)
        self.hex1_text = scrolledtext.ScrolledText(rom1_frame, width=50, height=30, font=('Courier', 9))
        self.hex1_text.pack(fill='both', expand=True)
        
        # ROM 2 hex view
        rom2_frame = ttk.LabelFrame(display_frame, text="ROM 2")
        rom2_frame.pack(side='left', fill='both', expand=True, padx=2)
        self.hex2_text = scrolledtext.ScrolledText(rom2_frame, width=50, height=30, font=('Courier', 9))
        self.hex2_text.pack(fill='both', expand=True)
        
        # Configure tags for highlighting
        self.hex1_text.tag_config('different', background=self.COLOR_DIFFERENT)
        self.hex2_text.tag_config('different', background=self.COLOR_DIFFERENT)
    
    def setup_visualmap_tab(self, parent):
        """Setup Visual Map tab"""
        # Info label
        info_label = ttk.Label(parent, text="Visual representation: Green = identical, Red = different")
        info_label.pack(padx=5, pady=5)
        
        # Canvas for visual map
        canvas_frame = ttk.Frame(parent)
        canvas_frame.pack(fill='both', expand=True, padx=5, pady=5)
        
        self.visual_canvas = tk.Canvas(canvas_frame, bg='white')
        self.visual_canvas.pack(fill='both', expand=True)
        
        # Bind resize
        self.visual_canvas.bind('<Configure>', self.redraw_visual_map)
    
    def setup_regions_tab(self, parent):
        """Setup Regions List tab"""
        # Treeview for regions
        columns = ('Offset', 'Size', 'Description')
        self.regions_tree = ttk.Treeview(parent, columns=columns, show='headings', height=25)
        
        self.regions_tree.heading('Offset', text='Offset')
        self.regions_tree.heading('Size', text='Size')
        self.regions_tree.heading('Description', text='Description')
        
        self.regions_tree.column('Offset', width=150)
        self.regions_tree.column('Size', width=100)
        self.regions_tree.column('Description', width=500)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(parent, orient='vertical', command=self.regions_tree.yview)
        self.regions_tree.configure(yscrollcommand=scrollbar.set)
        
        self.regions_tree.pack(side='left', fill='both', expand=True, padx=5, pady=5)
        scrollbar.pack(side='right', fill='y', pady=5)
        
        # Bind double-click
        self.regions_tree.bind('<Double-1>', self.region_double_click)
    
    def browse_rom1(self):
        filename = filedialog.askopenfilename(
            title="Select ROM 1",
            filetypes=[("NES ROM", "*.nes"), ("All Files", "*.*")]
        )
        if filename:
            self.rom1_path.set(filename)
    
    def browse_rom2(self):
        filename = filedialog.askopenfilename(
            title="Select ROM 2",
            filetypes=[("NES ROM", "*.nes"), ("All Files", "*.*")]
        )
        if filename:
            self.rom2_path.set(filename)
    
    def compare_roms(self):
        """Compare the two selected ROMs"""
        try:
            # Validate
            if not self.rom1_path.get() or not self.rom2_path.get():
                messagebox.showerror("Error", "Please select both ROM files")
                return
            
            # Load ROMs
            with open(self.rom1_path.get(), 'rb') as f:
                self.rom1_data = f.read()
            with open(self.rom2_path.get(), 'rb') as f:
                self.rom2_data = f.read()
            
            # Compare
            self.diff_stats = ROMComparer.compare_roms(self.rom1_data, self.rom2_data)
            
            # Update all views
            self.update_summary()
            self.update_hexdiff(0)
            self.update_visual_map()
            self.update_regions_list()
            
            messagebox.showinfo("Success", f"Comparison complete!\n\n{self.diff_stats.summary}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare ROMs:\n{e}")
    
    def update_summary(self):
        """Update summary tab"""
        if not self.diff_stats:
            return
        
        summary = []
        summary.append("=" * 80)
        summary.append("ROM COMPARISON SUMMARY")
        summary.append("=" * 80)
        summary.append("")
        summary.append(f"ROM 1: {os.path.basename(self.rom1_path.get())} ({len(self.rom1_data):,} bytes)")
        summary.append(f"ROM 2: {os.path.basename(self.rom2_path.get())} ({len(self.rom2_data):,} bytes)")
        summary.append("")
        summary.append(self.diff_stats.summary)
        summary.append("")
        
        if self.diff_stats.diff_regions:
            summary.append("MAJOR DIFFERENCE REGIONS:")
            summary.append("-" * 80)
            for i, region in enumerate(self.diff_stats.diff_regions[:20], 1):  # Show first 20
                summary.append(f"{i:3d}. {region.description}")
            
            if len(self.diff_stats.diff_regions) > 20:
                summary.append(f"... and {len(self.diff_stats.diff_regions) - 20} more regions")
        
        summary.append("")
        summary.append("=" * 80)
        
        self.summary_text.delete('1.0', 'end')
        self.summary_text.insert('1.0', '\n'.join(summary))
    
    def update_hexdiff(self, offset: int, num_bytes: int = 512):
        """Update hex diff view starting at offset"""
        if not self.rom1_data or not self.rom2_data:
            return
        
        # Clear
        self.hex1_text.delete('1.0', 'end')
        self.hex2_text.delete('1.0', 'end')
        
        # Format hex views
        for i in range(offset, min(offset + num_bytes, len(self.rom1_data), len(self.rom2_data)), 16):
            # Address
            addr_str = f"{i:06X}: "
            
            # ROM 1 line
            hex1_bytes = self.rom1_data[i:i+16]
            hex1_str = ' '.join(f"{b:02X}" for b in hex1_bytes)
            ascii1_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in hex1_bytes)
            
            # ROM 2 line
            hex2_bytes = self.rom2_data[i:i+16]
            hex2_str = ' '.join(f"{b:02X}" for b in hex2_bytes)
            ascii2_str = ''.join(chr(b) if 32 <= b < 127 else '.' for b in hex2_bytes)
            
            # Insert with highlighting
            line1_start = self.hex1_text.index('end-1c')
            self.hex1_text.insert('end', addr_str + hex1_str.ljust(48) + '  ' + ascii1_str + '\n')
            
            line2_start = self.hex2_text.index('end-1c')
            self.hex2_text.insert('end', addr_str + hex2_str.ljust(48) + '  ' + ascii2_str + '\n')
            
            # Highlight differences
            if hex1_bytes != hex2_bytes:
                self.hex1_text.tag_add('different', line1_start, f"{line1_start} lineend")
                self.hex2_text.tag_add('different', line2_start, f"{line2_start} lineend")
    
    def update_visual_map(self):
        """Update visual difference map"""
        if not self.rom1_data or not self.rom2_data or not self.diff_stats:
            return
        
        # Clear canvas
        self.visual_canvas.delete('all')
        
        # Get canvas size
        width = self.visual_canvas.winfo_width()
        height = self.visual_canvas.winfo_height()
        
        if width < 10 or height < 10:
            return  # Not ready yet
        
        # Calculate pixel per byte
        max_len = max(len(self.rom1_data), len(self.rom2_data))
        pixels_per_row = 256
        num_rows = (max_len + pixels_per_row - 1) // pixels_per_row
        pixel_size = min(width // pixels_per_row, height // num_rows)
        
        if pixel_size < 1:
            pixel_size = 1
        
        # Draw pixels
        for i in range(max_len):
            row = i // pixels_per_row
            col = i % pixels_per_row
            
            x = col * pixel_size
            y = row * pixel_size
            
            # Determine color
            if i < len(self.rom1_data) and i < len(self.rom2_data):
                if self.rom1_data[i] == self.rom2_data[i]:
                    color = '#00FF00'  # Green = identical
                else:
                    color = '#FF0000'  # Red = different
            else:
                color = '#FFFF00'  # Yellow = size difference
            
            self.visual_canvas.create_rectangle(x, y, x+pixel_size, y+pixel_size, 
                                               fill=color, outline='')
    
    def redraw_visual_map(self, event=None):
        """Redraw visual map on resize"""
        self.update_visual_map()
    
    def update_regions_list(self):
        """Update regions list treeview"""
        if not self.diff_stats:
            return
        
        # Clear
        for item in self.regions_tree.get_children():
            self.regions_tree.delete(item)
        
        # Populate
        for i, region in enumerate(self.diff_stats.diff_regions):
            self.regions_tree.insert('', 'end', values=(
                f"0x{region.start_offset:06X} - 0x{region.end_offset:06X}",
                f"{region.size:,} bytes",
                region.description
            ), tags=(str(i),))
    
    def region_double_click(self, event):
        """Handle double-click on region"""
        selection = self.regions_tree.selection()
        if not selection:
            return
        
        item = selection[0]
        region_index = int(self.regions_tree.item(item, 'tags')[0])
        
        # Jump to this region in hex diff
        region = self.diff_stats.diff_regions[region_index]
        self.current_region_index = region_index
        self.update_hexdiff(region.start_offset)
        
        # Switch to hex diff tab
        self.notebook.select(1)
    
    def jump_to_offset(self):
        """Jump to specific offset in hex view"""
        try:
            offset_str = self.offset_entry.get().strip()
            if offset_str.startswith('0x') or offset_str.startswith('0X'):
                offset = int(offset_str, 16)
            else:
                offset = int(offset_str)
            
            self.update_hexdiff(offset)
            
        except ValueError:
            messagebox.showerror("Error", "Invalid offset")
    
    def prev_diff(self):
        """Jump to previous difference region"""
        if not self.diff_stats or not self.diff_stats.diff_regions:
            return
        
        self.current_region_index = (self.current_region_index - 1) % len(self.diff_stats.diff_regions)
        region = self.diff_stats.diff_regions[self.current_region_index]
        self.update_hexdiff(region.start_offset)
    
    def next_diff(self):
        """Jump to next difference region"""
        if not self.diff_stats or not self.diff_stats.diff_regions:
            return
        
        self.current_region_index = (self.current_region_index + 1) % len(self.diff_stats.diff_regions)
        region = self.diff_stats.diff_regions[self.current_region_index]
        self.update_hexdiff(region.start_offset)
    
    def export_report(self):
        """Export comparison report"""
        if not self.diff_stats:
            messagebox.showerror("Error", "No comparison data to export")
            return
        
        filename = filedialog.asksaveasfilename(
            title="Export Diff Report",
            defaultextension=".txt",
            filetypes=[("Text File", "*.txt"), ("All Files", "*.*")]
        )
        
        if filename:
            try:
                ROMComparer.export_diff_report(
                    self.rom1_path.get(),
                    self.rom2_path.get(),
                    self.diff_stats,
                    filename
                )
                messagebox.showinfo("Success", f"Report exported to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export report:\n{e}")
    
    def run(self):
        """Run the GUI"""
        self.master.mainloop()


def main():
    """Main entry point"""
    app = ROMDiffViewerGUI()
    app.run()


if __name__ == '__main__':
    main()
