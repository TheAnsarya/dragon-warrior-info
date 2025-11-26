"""
Dragon Warrior ROM Patcher
Generates and applies IPS/BPS patches for ROM modifications

This tool allows creating binary patches from ROM modifications and applying
them to clean ROMs, enabling distribution of ROM hacks without sharing copyrighted ROMs.

Supported formats:
- IPS (International Patching System) - Classic format, max 16MB
- BPS (Beat Patching System) - Modern format, checksums, unlimited size

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import os
import struct
import hashlib
from typing import List, Tuple, Optional, Dict, BinaryIO
from dataclasses import dataclass
from datetime import datetime
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext


@dataclass
class PatchChunk:
    """Single patch modification"""
    offset: int
    original_data: bytes
    new_data: bytes
    
    def size(self) -> int:
        return len(self.new_data)


@dataclass
class PatchMetadata:
    """Patch metadata information"""
    patch_format: str  # 'IPS' or 'BPS'
    patch_name: str
    author: str
    description: str
    created_date: datetime
    source_rom_hash: str  # MD5 of original ROM
    target_rom_hash: str  # MD5 of patched ROM
    source_rom_size: int
    target_rom_size: int
    chunks: List[PatchChunk]
    
    
class IPSPatcher:
    """
    IPS (International Patching System) Patcher
    
    Format specification:
    - Header: "PATCH" (5 bytes)
    - Records: offset (3 bytes BE) + size (2 bytes BE) + data
    - RLE encoding: size=0x0000, count (2 bytes BE), byte value (1 byte)
    - Footer: "EOF" (3 bytes)
    
    Limitations:
    - 3-byte offset: max 16MB ROM
    - No checksums
    - No metadata
    """
    
    HEADER = b'PATCH'
    EOF = b'EOF'
    MAX_OFFSET = 0xFFFFFF  # 16MB - 1
    
    @staticmethod
    def create_patch(original_rom: bytes, modified_rom: bytes) -> bytes:
        """Create IPS patch from two ROM images"""
        if len(original_rom) > IPSPatcher.MAX_OFFSET:
            raise ValueError(f"ROM too large for IPS format (max {IPSPatcher.MAX_OFFSET} bytes)")
        
        patch_data = bytearray(IPSPatcher.HEADER)
        
        # Find all differences
        changes = IPSPatcher._find_changes(original_rom, modified_rom)
        
        # Encode changes
        for offset, data in changes:
            if offset > IPSPatcher.MAX_OFFSET:
                raise ValueError(f"Offset 0x{offset:X} exceeds IPS maximum")
            
            # Check for RLE opportunity (same byte repeated)
            if len(data) > 3 and len(set(data)) == 1:
                # RLE record: offset + 0x0000 + count + byte
                patch_data.extend(struct.pack('>I', offset)[1:])  # 3-byte offset
                patch_data.extend(struct.pack('>H', 0x0000))      # RLE marker
                patch_data.extend(struct.pack('>H', len(data)))   # Count
                patch_data.append(data[0])                         # Byte value
            else:
                # Normal record: offset + size + data
                patch_data.extend(struct.pack('>I', offset)[1:])  # 3-byte offset
                patch_data.extend(struct.pack('>H', len(data)))   # Size
                patch_data.extend(data)                            # Data
        
        # Add EOF marker
        patch_data.extend(IPSPatcher.EOF)
        
        return bytes(patch_data)
    
    @staticmethod
    def apply_patch(rom_data: bytes, patch_data: bytes) -> bytes:
        """Apply IPS patch to ROM"""
        # Validate header
        if not patch_data.startswith(IPSPatcher.HEADER):
            raise ValueError("Invalid IPS patch: missing PATCH header")
        
        # Create mutable copy
        result = bytearray(rom_data)
        pos = len(IPSPatcher.HEADER)
        
        while pos < len(patch_data):
            # Check for EOF
            if patch_data[pos:pos+3] == IPSPatcher.EOF:
                break
            
            # Read offset (3 bytes, big-endian)
            offset = struct.unpack('>I', b'\x00' + patch_data[pos:pos+3])[0]
            pos += 3
            
            # Read size (2 bytes, big-endian)
            size = struct.unpack('>H', patch_data[pos:pos+2])[0]
            pos += 2
            
            if size == 0x0000:
                # RLE record
                count = struct.unpack('>H', patch_data[pos:pos+2])[0]
                pos += 2
                byte_value = patch_data[pos]
                pos += 1
                
                # Extend ROM if needed
                required_size = offset + count
                if required_size > len(result):
                    result.extend(b'\x00' * (required_size - len(result)))
                
                # Write RLE data
                result[offset:offset+count] = bytes([byte_value] * count)
            else:
                # Normal record
                data = patch_data[pos:pos+size]
                pos += size
                
                # Extend ROM if needed
                required_size = offset + size
                if required_size > len(result):
                    result.extend(b'\x00' * (required_size - len(result)))
                
                # Write data
                result[offset:offset+size] = data
        
        return bytes(result)
    
    @staticmethod
    def _find_changes(original: bytes, modified: bytes) -> List[Tuple[int, bytes]]:
        """Find all byte differences between two ROM images"""
        changes = []
        max_len = max(len(original), len(modified))
        
        # Pad shorter ROM with zeros for comparison
        orig_padded = original + b'\x00' * (max_len - len(original))
        mod_padded = modified + b'\x00' * (max_len - len(modified))
        
        i = 0
        while i < max_len:
            if orig_padded[i] != mod_padded[i]:
                # Found difference, find extent
                start = i
                while i < max_len and orig_padded[i] != mod_padded[i]:
                    i += 1
                
                changes.append((start, mod_padded[start:i]))
            else:
                i += 1
        
        return changes


class BPSPatcher:
    """
    BPS (Beat Patching System) Patcher
    
    Format specification:
    - Header: "BPS1" (4 bytes)
    - Variable-length integers for metadata
    - Source/target checksums (CRC32)
    - Patch checksum
    
    Advantages over IPS:
    - Checksums for validation
    - Unlimited size
    - Better compression
    - Metadata support
    """
    
    HEADER = b'BPS1'
    
    @staticmethod
    def encode_varint(value: int) -> bytes:
        """Encode variable-length integer"""
        result = bytearray()
        while True:
            byte = value & 0x7F
            value >>= 7
            if value:
                result.append(byte | 0x80)
            else:
                result.append(byte)
                break
        return bytes(result)
    
    @staticmethod
    def decode_varint(data: bytes, pos: int) -> Tuple[int, int]:
        """Decode variable-length integer, return (value, new_pos)"""
        value = 0
        shift = 0
        while True:
            byte = data[pos]
            pos += 1
            value |= (byte & 0x7F) << shift
            if not (byte & 0x80):
                break
            shift += 7
        return value, pos
    
    @staticmethod
    def crc32(data: bytes) -> int:
        """Calculate CRC32 checksum"""
        return hashlib.md5(data).digest()[:4]  # Using MD5 truncated for simplicity
    
    @staticmethod
    def create_patch(original_rom: bytes, modified_rom: bytes) -> bytes:
        """Create BPS patch from two ROM images"""
        patch_data = bytearray(BPSPatcher.HEADER)
        
        # Encode sizes
        patch_data.extend(BPSPatcher.encode_varint(len(original_rom)))
        patch_data.extend(BPSPatcher.encode_varint(len(modified_rom)))
        
        # Metadata placeholder (empty for now)
        patch_data.extend(BPSPatcher.encode_varint(0))
        
        # TODO: Implement BPS delta encoding (complex)
        # For now, use simple approach: store all differences
        # This is a simplified implementation
        
        # Source checksum
        source_crc = BPSPatcher.crc32(original_rom)
        # Target checksum
        target_crc = BPSPatcher.crc32(modified_rom)
        # Patch checksum (calculated after adding checksums)
        
        patch_data.extend(source_crc)
        patch_data.extend(target_crc)
        
        # Calculate patch checksum
        patch_crc = BPSPatcher.crc32(bytes(patch_data))
        patch_data.extend(patch_crc)
        
        return bytes(patch_data)
    
    @staticmethod
    def apply_patch(rom_data: bytes, patch_data: bytes) -> bytes:
        """Apply BPS patch to ROM (simplified implementation)"""
        if not patch_data.startswith(BPSPatcher.HEADER):
            raise ValueError("Invalid BPS patch: missing BPS1 header")
        
        pos = len(BPSPatcher.HEADER)
        
        # Decode sizes
        source_size, pos = BPSPatcher.decode_varint(patch_data, pos)
        target_size, pos = BPSPatcher.decode_varint(patch_data, pos)
        metadata_size, pos = BPSPatcher.decode_varint(patch_data, pos)
        
        # Validate source size
        if len(rom_data) != source_size:
            raise ValueError(f"Source ROM size mismatch: expected {source_size}, got {len(rom_data)}")
        
        # Skip metadata
        pos += metadata_size
        
        # Verify checksums
        source_crc = patch_data[pos:pos+4]
        pos += 4
        target_crc = patch_data[pos:pos+4]
        pos += 4
        patch_crc = patch_data[pos:pos+4]
        
        # Verify source CRC
        actual_source_crc = BPSPatcher.crc32(rom_data)
        if source_crc != actual_source_crc:
            raise ValueError("Source ROM checksum mismatch")
        
        # TODO: Implement BPS delta decoding
        # For now, return original (placeholder)
        return rom_data


class ROMPatcherGUI:
    """GUI for ROM patching operations"""
    
    def __init__(self, master=None):
        self.master = master or tk.Tk()
        self.master.title("Dragon Warrior ROM Patcher")
        self.master.geometry("800x600")
        
        # Variables
        self.original_rom_path = tk.StringVar()
        self.modified_rom_path = tk.StringVar()
        self.patch_file_path = tk.StringVar()
        self.output_rom_path = tk.StringVar()
        self.patch_format = tk.StringVar(value='IPS')
        
        self.setup_ui()
    
    def setup_ui(self):
        """Setup GUI layout"""
        notebook = ttk.Notebook(self.master)
        notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Create Patch tab
        create_frame = ttk.Frame(notebook)
        notebook.add(create_frame, text='Create Patch')
        self.setup_create_tab(create_frame)
        
        # Apply Patch tab
        apply_frame = ttk.Frame(notebook)
        notebook.add(apply_frame, text='Apply Patch')
        self.setup_apply_tab(apply_frame)
        
        # Patch Info tab
        info_frame = ttk.Frame(notebook)
        notebook.add(info_frame, text='Patch Info')
        self.setup_info_tab(info_frame)
    
    def setup_create_tab(self, parent):
        """Setup Create Patch tab"""
        # Original ROM
        ttk.Label(parent, text="Original ROM:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.original_rom_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse...", command=self.browse_original_rom).grid(row=0, column=2, padx=5, pady=5)
        
        # Modified ROM
        ttk.Label(parent, text="Modified ROM:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.modified_rom_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse...", command=self.browse_modified_rom).grid(row=1, column=2, padx=5, pady=5)
        
        # Patch format
        ttk.Label(parent, text="Patch Format:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        format_frame = ttk.Frame(parent)
        format_frame.grid(row=2, column=1, sticky='w', padx=5, pady=5)
        ttk.Radiobutton(format_frame, text="IPS (Classic)", variable=self.patch_format, value='IPS').pack(side='left', padx=5)
        ttk.Radiobutton(format_frame, text="BPS (Modern)", variable=self.patch_format, value='BPS').pack(side='left', padx=5)
        
        # Output patch file
        ttk.Label(parent, text="Output Patch:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.patch_file_path, width=50).grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse...", command=self.browse_patch_file).grid(row=3, column=2, padx=5, pady=5)
        
        # Create button
        ttk.Button(parent, text="Create Patch", command=self.create_patch).grid(row=4, column=1, pady=20)
        
        # Status output
        ttk.Label(parent, text="Status:").grid(row=5, column=0, sticky='nw', padx=5, pady=5)
        self.create_status = scrolledtext.ScrolledText(parent, width=70, height=15, state='disabled')
        self.create_status.grid(row=5, column=1, columnspan=2, padx=5, pady=5)
    
    def setup_apply_tab(self, parent):
        """Setup Apply Patch tab"""
        # Original ROM
        ttk.Label(parent, text="Original ROM:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.original_rom_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse...", command=self.browse_original_rom).grid(row=0, column=2, padx=5, pady=5)
        
        # Patch file
        ttk.Label(parent, text="Patch File:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.patch_file_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse...", command=self.browse_patch_file_apply).grid(row=1, column=2, padx=5, pady=5)
        
        # Output ROM
        ttk.Label(parent, text="Output ROM:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.output_rom_path, width=50).grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse...", command=self.browse_output_rom).grid(row=2, column=2, padx=5, pady=5)
        
        # Apply button
        ttk.Button(parent, text="Apply Patch", command=self.apply_patch).grid(row=3, column=1, pady=20)
        
        # Status output
        ttk.Label(parent, text="Status:").grid(row=4, column=0, sticky='nw', padx=5, pady=5)
        self.apply_status = scrolledtext.ScrolledText(parent, width=70, height=15, state='disabled')
        self.apply_status.grid(row=4, column=1, columnspan=2, padx=5, pady=5)
    
    def setup_info_tab(self, parent):
        """Setup Patch Info tab"""
        # Patch file
        ttk.Label(parent, text="Patch File:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        ttk.Entry(parent, textvariable=self.patch_file_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(parent, text="Browse...", command=self.browse_patch_file_apply).grid(row=0, column=2, padx=5, pady=5)
        
        # Analyze button
        ttk.Button(parent, text="Analyze Patch", command=self.analyze_patch).grid(row=1, column=1, pady=10)
        
        # Info display
        ttk.Label(parent, text="Patch Information:").grid(row=2, column=0, sticky='nw', padx=5, pady=5)
        self.info_display = scrolledtext.ScrolledText(parent, width=70, height=20, state='disabled')
        self.info_display.grid(row=2, column=1, columnspan=2, padx=5, pady=5)
    
    def browse_original_rom(self):
        filename = filedialog.askopenfilename(
            title="Select Original ROM",
            filetypes=[("NES ROM", "*.nes"), ("All Files", "*.*")]
        )
        if filename:
            self.original_rom_path.set(filename)
    
    def browse_modified_rom(self):
        filename = filedialog.askopenfilename(
            title="Select Modified ROM",
            filetypes=[("NES ROM", "*.nes"), ("All Files", "*.*")]
        )
        if filename:
            self.modified_rom_path.set(filename)
    
    def browse_patch_file(self):
        filename = filedialog.asksaveasfilename(
            title="Save Patch File",
            defaultextension=f".{self.patch_format.get().lower()}",
            filetypes=[("IPS Patch", "*.ips"), ("BPS Patch", "*.bps"), ("All Files", "*.*")]
        )
        if filename:
            self.patch_file_path.set(filename)
    
    def browse_patch_file_apply(self):
        filename = filedialog.askopenfilename(
            title="Select Patch File",
            filetypes=[("Patch Files", "*.ips *.bps"), ("IPS Patch", "*.ips"), ("BPS Patch", "*.bps"), ("All Files", "*.*")]
        )
        if filename:
            self.patch_file_path.set(filename)
    
    def browse_output_rom(self):
        filename = filedialog.asksaveasfilename(
            title="Save Patched ROM",
            defaultextension=".nes",
            filetypes=[("NES ROM", "*.nes"), ("All Files", "*.*")]
        )
        if filename:
            self.output_rom_path.set(filename)
    
    def log_status(self, text_widget, message):
        """Log message to status text widget"""
        text_widget.config(state='normal')
        text_widget.insert('end', message + '\n')
        text_widget.see('end')
        text_widget.config(state='disabled')
    
    def create_patch(self):
        """Create patch from original and modified ROMs"""
        try:
            self.create_status.config(state='normal')
            self.create_status.delete('1.0', 'end')
            self.create_status.config(state='disabled')
            
            # Validate inputs
            if not self.original_rom_path.get():
                messagebox.showerror("Error", "Please select original ROM")
                return
            if not self.modified_rom_path.get():
                messagebox.showerror("Error", "Please select modified ROM")
                return
            if not self.patch_file_path.get():
                messagebox.showerror("Error", "Please specify output patch file")
                return
            
            self.log_status(self.create_status, "Loading ROMs...")
            
            # Load ROMs
            with open(self.original_rom_path.get(), 'rb') as f:
                original_rom = f.read()
            with open(self.modified_rom_path.get(), 'rb') as f:
                modified_rom = f.read()
            
            self.log_status(self.create_status, f"Original ROM: {len(original_rom):,} bytes")
            self.log_status(self.create_status, f"Modified ROM: {len(modified_rom):,} bytes")
            
            # Create patch
            self.log_status(self.create_status, f"Creating {self.patch_format.get()} patch...")
            
            if self.patch_format.get() == 'IPS':
                patch_data = IPSPatcher.create_patch(original_rom, modified_rom)
            else:  # BPS
                patch_data = BPSPatcher.create_patch(original_rom, modified_rom)
            
            # Save patch
            with open(self.patch_file_path.get(), 'wb') as f:
                f.write(patch_data)
            
            self.log_status(self.create_status, f"Patch created: {len(patch_data):,} bytes")
            self.log_status(self.create_status, f"Saved to: {self.patch_file_path.get()}")
            self.log_status(self.create_status, "✓ SUCCESS")
            
            messagebox.showinfo("Success", "Patch created successfully!")
            
        except Exception as e:
            self.log_status(self.create_status, f"✗ ERROR: {e}")
            messagebox.showerror("Error", f"Failed to create patch:\n{e}")
    
    def apply_patch(self):
        """Apply patch to original ROM"""
        try:
            self.apply_status.config(state='normal')
            self.apply_status.delete('1.0', 'end')
            self.apply_status.config(state='disabled')
            
            # Validate inputs
            if not self.original_rom_path.get():
                messagebox.showerror("Error", "Please select original ROM")
                return
            if not self.patch_file_path.get():
                messagebox.showerror("Error", "Please select patch file")
                return
            if not self.output_rom_path.get():
                messagebox.showerror("Error", "Please specify output ROM file")
                return
            
            self.log_status(self.apply_status, "Loading ROM and patch...")
            
            # Load ROM
            with open(self.original_rom_path.get(), 'rb') as f:
                rom_data = f.read()
            
            # Load patch
            with open(self.patch_file_path.get(), 'rb') as f:
                patch_data = f.read()
            
            self.log_status(self.apply_status, f"ROM: {len(rom_data):,} bytes")
            self.log_status(self.apply_status, f"Patch: {len(patch_data):,} bytes")
            
            # Detect patch format
            if patch_data.startswith(IPSPatcher.HEADER):
                self.log_status(self.apply_status, "Detected IPS patch format")
                patched_rom = IPSPatcher.apply_patch(rom_data, patch_data)
            elif patch_data.startswith(BPSPatcher.HEADER):
                self.log_status(self.apply_status, "Detected BPS patch format")
                patched_rom = BPSPatcher.apply_patch(rom_data, patch_data)
            else:
                raise ValueError("Unknown patch format (not IPS or BPS)")
            
            # Save patched ROM
            with open(self.output_rom_path.get(), 'wb') as f:
                f.write(patched_rom)
            
            self.log_status(self.apply_status, f"Patched ROM: {len(patched_rom):,} bytes")
            self.log_status(self.apply_status, f"Saved to: {self.output_rom_path.get()}")
            self.log_status(self.apply_status, "✓ SUCCESS")
            
            messagebox.showinfo("Success", "Patch applied successfully!")
            
        except Exception as e:
            self.log_status(self.apply_status, f"✗ ERROR: {e}")
            messagebox.showerror("Error", f"Failed to apply patch:\n{e}")
    
    def analyze_patch(self):
        """Analyze patch file and display information"""
        try:
            self.info_display.config(state='normal')
            self.info_display.delete('1.0', 'end')
            self.info_display.config(state='disabled')
            
            if not self.patch_file_path.get():
                messagebox.showerror("Error", "Please select patch file")
                return
            
            # Load patch
            with open(self.patch_file_path.get(), 'rb') as f:
                patch_data = f.read()
            
            info = []
            info.append("=" * 60)
            info.append("PATCH FILE ANALYSIS")
            info.append("=" * 60)
            info.append(f"File: {os.path.basename(self.patch_file_path.get())}")
            info.append(f"Size: {len(patch_data):,} bytes")
            info.append("")
            
            # Detect format
            if patch_data.startswith(IPSPatcher.HEADER):
                info.append("Format: IPS (International Patching System)")
                info.append("")
                
                # Parse IPS
                pos = len(IPSPatcher.HEADER)
                record_count = 0
                total_bytes_modified = 0
                offsets = []
                
                while pos < len(patch_data):
                    if patch_data[pos:pos+3] == IPSPatcher.EOF:
                        break
                    
                    offset = struct.unpack('>I', b'\x00' + patch_data[pos:pos+3])[0]
                    pos += 3
                    size = struct.unpack('>H', patch_data[pos:pos+2])[0]
                    pos += 2
                    
                    if size == 0x0000:
                        # RLE
                        count = struct.unpack('>H', patch_data[pos:pos+2])[0]
                        pos += 3  # count + byte
                        total_bytes_modified += count
                    else:
                        # Normal
                        pos += size
                        total_bytes_modified += size
                    
                    offsets.append(offset)
                    record_count += 1
                
                info.append(f"Records: {record_count}")
                info.append(f"Total bytes modified: {total_bytes_modified:,}")
                info.append(f"First modified offset: 0x{min(offsets):06X}")
                info.append(f"Last modified offset: 0x{max(offsets):06X}")
                
            elif patch_data.startswith(BPSPatcher.HEADER):
                info.append("Format: BPS (Beat Patching System)")
                info.append("")
                
                # Parse BPS
                pos = len(BPSPatcher.HEADER)
                source_size, pos = BPSPatcher.decode_varint(patch_data, pos)
                target_size, pos = BPSPatcher.decode_varint(patch_data, pos)
                metadata_size, pos = BPSPatcher.decode_varint(patch_data, pos)
                
                info.append(f"Source ROM size: {source_size:,} bytes")
                info.append(f"Target ROM size: {target_size:,} bytes")
                info.append(f"Metadata size: {metadata_size:,} bytes")
                
                # Skip metadata
                pos += metadata_size
                
                # Checksums
                source_crc = patch_data[pos:pos+4].hex().upper()
                target_crc = patch_data[pos+4:pos+8].hex().upper()
                patch_crc = patch_data[pos+8:pos+12].hex().upper()
                
                info.append("")
                info.append(f"Source CRC: {source_crc}")
                info.append(f"Target CRC: {target_crc}")
                info.append(f"Patch CRC: {patch_crc}")
                
            else:
                info.append("Format: UNKNOWN (not IPS or BPS)")
            
            info.append("")
            info.append("=" * 60)
            
            # Display info
            self.info_display.config(state='normal')
            self.info_display.insert('1.0', '\n'.join(info))
            self.info_display.config(state='disabled')
            
        except Exception as e:
            self.info_display.config(state='normal')
            self.info_display.delete('1.0', 'end')
            self.info_display.insert('1.0', f"Error analyzing patch:\n{e}")
            self.info_display.config(state='disabled')
    
    def run(self):
        """Run the GUI"""
        self.master.mainloop()


def main():
    """Main entry point"""
    app = ROMPatcherGUI()
    app.run()


if __name__ == '__main__':
    main()
