#!/usr/bin/env python3
"""
Dragon Warrior Patch Generator
Creates IPS and BPS patches when built ROM differs from reference ROM
"""

import struct
import hashlib
from pathlib import Path
from typing import Optional, List, Tuple
import click
from rich.console import Console

console = Console()

class PatchGenerator:
    """Generate IPS and BPS patches for ROM differences"""
    
    def __init__(self, reference_rom: str, built_rom: str, patches_dir: str = "patches"):
        self.reference_rom = Path(reference_rom)
        self.built_rom = Path(built_rom)
        self.patches_dir = Path(patches_dir)
        self.patches_dir.mkdir(exist_ok=True)
    
    def compare_roms(self) -> bool:
        """Compare two ROMs and determine if patches are needed"""
        if not self.reference_rom.exists():
            console.print(f"[red]❌ Reference ROM not found: {self.reference_rom}[/red]")
            return False
            
        if not self.built_rom.exists():
            console.print(f"[red]❌ Built ROM not found: {self.built_rom}[/red]")
            return False
        
        # Read both ROMs
        with open(self.reference_rom, 'rb') as f:
            ref_data = f.read()
        with open(self.built_rom, 'rb') as f:
            built_data = f.read()
        
        if ref_data == built_data:
            console.print("[green]✅ ROMs are identical - no patches needed[/green]")
            return False
        
        console.print("[yellow]⚠️ ROMs differ - generating patches...[/yellow]")
        return True
    
    def generate_ips_patch(self) -> Optional[Path]:
        """Generate IPS patch file"""
        try:
            with open(self.reference_rom, 'rb') as f:
                ref_data = f.read()
            with open(self.built_rom, 'rb') as f:
                built_data = f.read()
            
            # Find differences
            differences = self._find_differences(ref_data, built_data)
            if not differences:
                return None
            
            # Create IPS patch
            ips_data = bytearray(b'PATCH')
            
            for offset, original, modified in differences:
                # IPS format: [3-byte offset][2-byte length][data]
                if len(modified) > 65535:
                    console.print(f"[yellow]⚠️ Skipping large change at {offset:06X} (too big for IPS)[/yellow]")
                    continue
                
                ips_data.extend(struct.pack('>I', offset)[1:])  # 3-byte big-endian offset
                ips_data.extend(struct.pack('>H', len(modified)))  # 2-byte big-endian length
                ips_data.extend(modified)
            
            ips_data.extend(b'EOF')
            
            # Write IPS file
            ips_file = self.patches_dir / f"dragon_warrior_modifications.ips"
            with open(ips_file, 'wb') as f:
                f.write(ips_data)
            
            console.print(f"[green]✅ Generated IPS patch: {ips_file}[/green]")
            return ips_file
            
        except Exception as e:
            console.print(f"[red]❌ Error generating IPS patch: {e}[/red]")
            return None
    
    def generate_bps_patch(self) -> Optional[Path]:
        """Generate BPS patch file (simplified implementation)"""
        try:
            with open(self.reference_rom, 'rb') as f:
                ref_data = f.read()
            with open(self.built_rom, 'rb') as f:
                built_data = f.read()
            
            # Simple BPS implementation - store differences
            bps_data = bytearray(b'BPS1')
            
            # Source file length
            bps_data.extend(self._encode_varint(len(ref_data)))
            # Target file length  
            bps_data.extend(self._encode_varint(len(built_data)))
            # Metadata length (0)
            bps_data.extend(self._encode_varint(0))
            
            # Find and encode differences
            differences = self._find_differences(ref_data, built_data)
            
            current_offset = 0
            for offset, original, modified in differences:
                # Skip to position
                skip_length = offset - current_offset
                if skip_length > 0:
                    # Source read command
                    bps_data.extend(self._encode_varint((skip_length << 2) | 0))
                
                # Target read command for modified data
                bps_data.extend(self._encode_varint((len(modified) << 2) | 1))
                bps_data.extend(modified)
                
                current_offset = offset + len(original)
            
            # CRC32 checksums (simplified - just use 0 for now)
            bps_data.extend(struct.pack('<L', 0))  # Source CRC32
            bps_data.extend(struct.pack('<L', 0))  # Target CRC32
            bps_data.extend(struct.pack('<L', 0))  # Patch CRC32
            
            # Write BPS file
            bps_file = self.patches_dir / f"dragon_warrior_modifications.bps"
            with open(bps_file, 'wb') as f:
                f.write(bps_data)
            
            console.print(f"[green]✅ Generated BPS patch: {bps_file}[/green]")
            return bps_file
            
        except Exception as e:
            console.print(f"[red]❌ Error generating BPS patch: {e}[/red]")
            return None
    
    def _find_differences(self, ref_data: bytes, built_data: bytes) -> List[Tuple[int, bytes, bytes]]:
        """Find byte-level differences between two ROMs"""
        differences = []
        max_len = max(len(ref_data), len(built_data))
        
        i = 0
        while i < max_len:
            # Check if bytes differ
            ref_byte = ref_data[i] if i < len(ref_data) else 0x00
            built_byte = built_data[i] if i < len(built_data) else 0x00
            
            if ref_byte != built_byte:
                # Found start of difference - find end
                start_offset = i
                original_bytes = bytearray()
                modified_bytes = bytearray()
                
                while i < max_len:
                    ref_byte = ref_data[i] if i < len(ref_data) else 0x00
                    built_byte = built_data[i] if i < len(built_data) else 0x00
                    
                    if ref_byte == built_byte:
                        break  # End of difference block
                    
                    original_bytes.append(ref_byte)
                    modified_bytes.append(built_byte)
                    i += 1
                
                differences.append((start_offset, bytes(original_bytes), bytes(modified_bytes)))
            else:
                i += 1
        
        return differences
    
    def _encode_varint(self, value: int) -> bytes:
        """Encode variable-length integer for BPS format"""
        result = bytearray()
        while value >= 0x80:
            result.append((value & 0x7F) | 0x80)
            value >>= 7
        result.append(value & 0x7F)
        return bytes(result)
    
    def generate_patches(self) -> Tuple[Optional[Path], Optional[Path]]:
        """Generate both IPS and BPS patches if ROMs differ"""
        if not self.compare_roms():
            return None, None
        
        console.print("[blue]🔧 Generating patches for ROM differences...[/blue]")
        
        ips_file = self.generate_ips_patch()
        bps_file = self.generate_bps_patch()
        
        return ips_file, bps_file

@click.command()
@click.argument('reference_rom', type=click.Path(exists=True))
@click.argument('built_rom', type=click.Path(exists=True))
@click.option('--patches-dir', default='patches', help='Output directory for patches')
def generate_patches(reference_rom: str, built_rom: str, patches_dir: str):
    """Generate IPS and BPS patches for ROM differences"""
    
    generator = PatchGenerator(reference_rom, built_rom, patches_dir)
    ips_file, bps_file = generator.generate_patches()
    
    if ips_file or bps_file:
        console.print("[green]🎯 Patch generation complete![/green]")
        if ips_file:
            console.print(f"[cyan]📄 IPS patch: {ips_file}[/cyan]")
        if bps_file:
            console.print(f"[cyan]📄 BPS patch: {bps_file}[/cyan]")
    else:
        console.print("[yellow]ℹ️ No patches needed - ROMs are identical[/yellow]")

if __name__ == "__main__":
    generate_patches()