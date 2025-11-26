#!/usr/bin/env python3
"""
Dragon Warrior Text Editor

Extract, edit, and reinsert game dialog text.
Supports word substitutions and text encoding.

Usage:
    python tools/text_editor.py [options]
    
    --rom PATH              Path to ROM file
    --extract               Extract all text to JSON
    --insert PATH           Insert text from JSON
    --analyze               Analyze text compression
    --encode TEXT           Encode text string
    --decode BYTES          Decode byte sequence
    --interactive           Interactive editor

Features:
    - Extract all game dialog
    - Edit text with live preview
    - Automatic word substitution
    - Text length validation
    - Compression analysis
    - Character frequency analysis

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import argparse
import json
import re
import sys
from collections import Counter
from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
from pathlib import Path


@dataclass
class DialogEntry:
    """
    Dialog text entry
    
    Attributes:
        id: Entry ID
        offset: ROM offset
        text: Decoded text
        encoded: Encoded bytes
        length: Byte length
        category: Dialog category (npc, item, menu, etc.)
    """
    id: int
    offset: int
    text: str
    encoded: bytes
    length: int
    category: str = "dialog"
    
    def __repr__(self):
        preview = self.text[:40] + "..." if len(self.text) > 40 else self.text
        return f"Dialog({self.id:03d} @0x{self.offset:05X}: \"{preview}\")"


class TextEncoder:
    """
    Dragon Warrior text encoding/decoding
    
    Supports:
        - Character mapping (A-Z, 0-9, punctuation)
        - Word substitutions (0x80-0x9F)
        - Control codes (newline, delay, etc.)
    """
    
    # Character table (Dragon Warrior NES)
    CHAR_TABLE = {
        # Letters (uppercase only in DW)
        0x00: 'A', 0x01: 'B', 0x02: 'C', 0x03: 'D', 0x04: 'E',
        0x05: 'F', 0x06: 'G', 0x07: 'H', 0x08: 'I', 0x09: 'J',
        0x0A: 'K', 0x0B: 'L', 0x0C: 'M', 0x0D: 'N', 0x0E: 'O',
        0x0F: 'P', 0x10: 'Q', 0x11: 'R', 0x12: 'S', 0x13: 'T',
        0x14: 'U', 0x15: 'V', 0x16: 'W', 0x17: 'X', 0x18: 'Y',
        0x19: 'Z',
        
        # Numbers
        0x1A: '0', 0x1B: '1', 0x1C: '2', 0x1D: '3', 0x1E: '4',
        0x1F: '5', 0x20: '6', 0x21: '7', 0x22: '8', 0x23: '9',
        
        # Punctuation
        0x24: ' ',   # Space
        0x25: ',',   # Comma
        0x26: '.',   # Period
        0x27: '\'',  # Apostrophe
        0x28: '!',   # Exclamation
        0x29: '?',   # Question
        0x2A: '-',   # Hyphen
        0x2B: '/',   # Slash
        0x2C: ':',   # Colon
        0x2D: ';',   # Semicolon
        0x2E: '(',   # Open paren
        0x2F: ')',   # Close paren
        
        # Special characters
        0x30: '\n',  # Newline
        0x31: '<WAIT>',  # Wait for input
        0x32: '<CLEAR>',  # Clear text box
        0x33: '<DELAY>',  # Delay
        0x34: '<PLAYER>',  # Player name
        0x35: '<CHOICE>',  # Yes/No choice
        
        # Word substitutions (0x80-0x9F)
        0x80: "SWORD",
        0x81: "STAFF",
        0x82: "SHIELD",
        0x83: "ARMOR",
        0x84: "HELMET",
        0x85: "MAGIC",
        0x86: "COPPER",
        0x87: "SILVER",
        0x88: "GOLD",
        0x89: "HERB",
        0x8A: "KEY",
        0x8B: "TORCH",
        0x8C: "DRAGON",
        0x8D: "STONES",
        0x8E: "FAIRY",
        0x8F: "WATER",
        0x90: "TANTEGEL",
        0x91: "PRINCESS",
        0x92: "ERDRICK",
        0x93: "DRAGONLORD",
        0x94: "GWAELIN",
        0x95: "CHARLOCK",
        0x96: "RADIANT",
        0x97: "CURSED",
        0x98: "TOKEN",
        0x99: "FLUTE",
        0x9A: "HARP",
        0x9B: "LYRE",
        0x9C: "RING",
        0x9D: "AMULET",
        0x9E: "PENDANT",
        0x9F: "RAINBOW",
        
        # End marker
        0xFF: '<END>',
    }
    
    # Reverse mapping
    REVERSE_TABLE = {v: k for k, v in CHAR_TABLE.items()}
    
    def __init__(self):
        """Initialize encoder"""
        # Build substitution regex
        subs = sorted(
            [(v, k) for k, v in self.CHAR_TABLE.items() if 0x80 <= k <= 0x9F],
            key=lambda x: len(x[0]),
            reverse=True  # Longest first
        )
        self.substitution_pattern = '|'.join(re.escape(word) for word, _ in subs)
        self.substitutions = dict(subs)
    
    def decode(self, data: bytes) -> str:
        """
        Decode bytes to text
        
        Args:
            data: Encoded bytes
            
        Returns:
            Decoded text
        """
        text = []
        i = 0
        
        while i < len(data):
            byte = data[i]
            
            if byte == 0xFF:
                break  # End marker
            
            char = self.CHAR_TABLE.get(byte)
            if char:
                text.append(char)
            else:
                text.append(f'<0x{byte:02X}>')  # Unknown byte
            
            i += 1
        
        return ''.join(text)
    
    def encode(self, text: str) -> bytes:
        """
        Encode text to bytes
        
        Args:
            text: Text to encode
            
        Returns:
            Encoded bytes
        """
        # Convert to uppercase (DW is all caps)
        text = text.upper()
        
        # Apply word substitutions first
        def replace_sub(match):
            word = match.group(0)
            return chr(self.substitutions[word]) if word in self.substitutions else word
        
        if self.substitution_pattern:
            text = re.sub(self.substitution_pattern, replace_sub, text)
        
        # Encode characters
        encoded = []
        for char in text:
            if ord(char) >= 0x80:
                # Already a substitution code
                encoded.append(ord(char))
            elif char in self.REVERSE_TABLE:
                encoded.append(self.REVERSE_TABLE[char])
            else:
                # Unknown character - skip or replace
                print(f"Warning: Unknown character '{char}' - skipping")
        
        # Add end marker
        encoded.append(0xFF)
        
        return bytes(encoded)
    
    def calculate_length(self, text: str) -> int:
        """
        Calculate encoded length
        
        Returns:
            Byte count (including end marker)
        """
        return len(self.encode(text))
    
    def find_substitutions(self, text: str) -> List[Tuple[str, int, int]]:
        """
        Find word substitutions in text
        
        Returns:
            List of (word, count, savings) tuples
        """
        text = text.upper()
        results = []
        
        for word, code in self.substitutions.items():
            count = text.count(word)
            if count > 0:
                savings = (len(word) - 1) * count  # -1 because substitution is 1 byte
                results.append((word, count, savings))
        
        return sorted(results, key=lambda x: x[2], reverse=True)


class DialogExtractor:
    """
    Extract dialog from ROM
    
    Scans ROM for text patterns and extracts dialog entries.
    """
    
    # Known dialog offsets in Dragon Warrior (approximate)
    DIALOG_REGIONS = [
        (0x08000, 0x0A000),  # Main dialog
        (0x0A000, 0x0C000),  # NPC dialog
        (0x0C000, 0x0D000),  # Item descriptions
        (0x0D000, 0x0E000),  # Menu text
    ]
    
    def __init__(self, rom_data: bytes):
        """
        Initialize extractor
        
        Args:
            rom_data: ROM file contents
        """
        self.rom = rom_data
        self.encoder = TextEncoder()
    
    def extract_all(self) -> List[DialogEntry]:
        """
        Extract all dialog entries
        
        Returns:
            List of DialogEntry objects
        """
        entries = []
        entry_id = 0
        
        for start, end in self.DIALOG_REGIONS:
            region_entries = self._scan_region(start, end, entry_id)
            entries.extend(region_entries)
            entry_id += len(region_entries)
        
        return entries
    
    def _scan_region(self, start: int, end: int, 
                     start_id: int) -> List[DialogEntry]:
        """
        Scan region for dialog
        
        Args:
            start: Region start offset
            end: Region end offset
            start_id: Starting entry ID
            
        Returns:
            List of DialogEntry objects
        """
        entries = []
        i = start
        entry_id = start_id
        
        while i < end:
            # Look for text start (heuristic: uppercase letter)
            byte = self.rom[i] if i < len(self.rom) else 0xFF
            
            if byte in range(0x00, 0x1A):  # A-Z
                # Potential text start
                entry = self._extract_entry(i, entry_id)
                if entry and len(entry.text) > 3:  # Minimum length
                    entries.append(entry)
                    entry_id += 1
                    i += entry.length
                else:
                    i += 1
            else:
                i += 1
        
        return entries
    
    def _extract_entry(self, offset: int, entry_id: int) -> Optional[DialogEntry]:
        """
        Extract single dialog entry
        
        Args:
            offset: ROM offset
            entry_id: Entry ID
            
        Returns:
            DialogEntry or None if invalid
        """
        # Find end marker
        i = offset
        while i < len(self.rom) and i < offset + 1000:  # Max length
            if self.rom[i] == 0xFF:
                break
            i += 1
        
        if i >= len(self.rom) or i >= offset + 1000:
            return None  # No end marker found
        
        # Extract and decode
        encoded = self.rom[offset:i+1]
        text = self.encoder.decode(encoded)
        
        # Validate (should be mostly printable)
        if self._is_valid_text(text):
            return DialogEntry(
                id=entry_id,
                offset=offset,
                text=text,
                encoded=encoded,
                length=len(encoded)
            )
        
        return None
    
    def _is_valid_text(self, text: str) -> bool:
        """
        Check if text looks valid
        
        Heuristic: Should have mostly letters and spaces
        """
        if not text:
            return False
        
        letter_count = sum(1 for c in text if c.isalpha() or c.isspace())
        ratio = letter_count / len(text)
        
        return ratio > 0.6  # At least 60% letters/spaces


class TextAnalyzer:
    """
    Analyze text for compression opportunities
    """
    
    def __init__(self, entries: List[DialogEntry]):
        """
        Initialize analyzer
        
        Args:
            entries: Dialog entries to analyze
        """
        self.entries = entries
        self.encoder = TextEncoder()
    
    def analyze_frequency(self) -> Dict:
        """
        Analyze character and word frequency
        
        Returns:
            Statistics dictionary
        """
        # Combine all text
        all_text = ' '.join(entry.text for entry in self.entries)
        
        # Character frequency
        char_freq = Counter(all_text)
        
        # Word frequency (simple split)
        words = re.findall(r'\b[A-Z]+\b', all_text)
        word_freq = Counter(words)
        
        # Calculate total size
        total_bytes = sum(entry.length for entry in self.entries)
        
        stats = {
            'total_entries': len(self.entries),
            'total_characters': len(all_text),
            'total_bytes': total_bytes,
            'unique_characters': len(char_freq),
            'unique_words': len(word_freq),
            'most_common_chars': char_freq.most_common(10),
            'most_common_words': word_freq.most_common(20),
        }
        
        return stats
    
    def find_compression_candidates(self, min_length: int = 4,
                                     min_occurrences: int = 3) -> List[Tuple[str, int, int]]:
        """
        Find words worth adding as substitutions
        
        Args:
            min_length: Minimum word length
            min_occurrences: Minimum occurrence count
            
        Returns:
            List of (word, count, savings) tuples
        """
        # Combine all text
        all_text = ' '.join(entry.text for entry in self.entries)
        
        # Find all words
        words = re.findall(r'\b[A-Z]+\b', all_text)
        word_freq = Counter(words)
        
        # Calculate potential savings
        candidates = []
        for word, count in word_freq.items():
            if len(word) >= min_length and count >= min_occurrences:
                # Savings = (word_length - 1) * count
                # -1 because substitution is 1 byte
                savings = (len(word) - 1) * count
                candidates.append((word, count, savings))
        
        return sorted(candidates, key=lambda x: x[2], reverse=True)
    
    def calculate_compression_ratio(self) -> float:
        """
        Calculate current compression ratio
        
        Returns:
            Compression ratio (< 1.0 = compressed)
        """
        total_original = sum(
            len(entry.text) for entry in self.entries
        )
        total_compressed = sum(
            entry.length for entry in self.entries
        )
        
        return total_compressed / total_original if total_original > 0 else 1.0


class InteractiveEditor:
    """
    Interactive text editor
    
    Commands:
        list [category]      - List dialog entries
        show <id>            - Show entry details
        edit <id> <text>     - Edit entry text
        search <text>        - Search for text
        analyze              - Show compression analysis
        save <path>          - Save to JSON
        load <path>          - Load from JSON
        help                 - Show commands
        quit                 - Exit
    """
    
    def __init__(self, entries: List[DialogEntry]):
        """Initialize editor"""
        self.entries = entries
        self.encoder = TextEncoder()
        self.analyzer = TextAnalyzer(entries)
    
    def run(self):
        """Run interactive editor"""
        print("Dragon Warrior Text Editor")
        print(f"Loaded {len(self.entries)} dialog entries")
        print("Type 'help' for commands\n")
        
        while True:
            try:
                command = input("> ").strip()
                if not command:
                    continue
                
                if not self.process_command(command):
                    break  # Quit
                    
            except KeyboardInterrupt:
                print("\nUse 'quit' to exit")
            except Exception as e:
                print(f"Error: {e}")
    
    def process_command(self, command: str) -> bool:
        """
        Process command
        
        Returns:
            True to continue, False to quit
        """
        parts = command.split(maxsplit=1)
        if not parts:
            return True
        
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        if cmd == 'quit' or cmd == 'exit':
            return False
        
        elif cmd == 'help':
            print(self.__class__.__doc__)
        
        elif cmd == 'list':
            category = args if args else None
            self._list_entries(category)
        
        elif cmd == 'show':
            try:
                entry_id = int(args)
                self._show_entry(entry_id)
            except ValueError:
                print("Usage: show <id>")
        
        elif cmd == 'edit':
            try:
                parts = args.split(maxsplit=1)
                entry_id = int(parts[0])
                new_text = parts[1] if len(parts) > 1 else ""
                self._edit_entry(entry_id, new_text)
            except (ValueError, IndexError):
                print("Usage: edit <id> <text>")
        
        elif cmd == 'search':
            if args:
                self._search(args)
            else:
                print("Usage: search <text>")
        
        elif cmd == 'analyze':
            self._analyze()
        
        elif cmd == 'save':
            if args:
                self._save(args)
            else:
                print("Usage: save <path>")
        
        elif cmd == 'load':
            if args:
                self._load(args)
            else:
                print("Usage: load <path>")
        
        else:
            print(f"Unknown command: {cmd}")
            print("Type 'help' for commands")
        
        return True
    
    def _list_entries(self, category: Optional[str] = None):
        """List dialog entries"""
        filtered = self.entries
        if category:
            filtered = [e for e in self.entries if e.category == category]
        
        print(f"\n{len(filtered)} entries:")
        for entry in filtered[:50]:  # Show first 50
            preview = entry.text[:60].replace('\n', ' ')
            if len(entry.text) > 60:
                preview += "..."
            print(f"  [{entry.id:03d}] {preview}")
        
        if len(filtered) > 50:
            print(f"  ... and {len(filtered) - 50} more")
    
    def _show_entry(self, entry_id: int):
        """Show entry details"""
        if entry_id < 0 or entry_id >= len(self.entries):
            print(f"Invalid ID: {entry_id}")
            return
        
        entry = self.entries[entry_id]
        
        print(f"\nEntry {entry.id}:")
        print(f"  Offset: 0x{entry.offset:05X}")
        print(f"  Category: {entry.category}")
        print(f"  Length: {entry.length} bytes")
        print(f"  Text:\n{entry.text}")
        print(f"\n  Encoded: {entry.encoded.hex()}")
        
        # Show substitutions
        subs = self.encoder.find_substitutions(entry.text)
        if subs:
            print("\n  Substitutions:")
            for word, count, savings in subs:
                print(f"    {word}: {count}× (saves {savings} bytes)")
    
    def _edit_entry(self, entry_id: int, new_text: str):
        """Edit entry text"""
        if entry_id < 0 or entry_id >= len(self.entries):
            print(f"Invalid ID: {entry_id}")
            return
        
        entry = self.entries[entry_id]
        
        # Encode new text
        encoded = self.encoder.encode(new_text)
        
        # Check length
        if len(encoded) > entry.length:
            print(f"Warning: New text is longer ({len(encoded)} vs {entry.length} bytes)")
            print("This may cause issues if inserted into ROM")
        
        # Update entry
        entry.text = new_text
        entry.encoded = encoded
        entry.length = len(encoded)
        
        print(f"Updated entry {entry_id}")
        print(f"New length: {entry.length} bytes")
    
    def _search(self, query: str):
        """Search for text"""
        query_upper = query.upper()
        results = [
            e for e in self.entries 
            if query_upper in e.text.upper()
        ]
        
        print(f"\nFound {len(results)} matches:")
        for entry in results[:20]:
            # Highlight match
            text = entry.text.replace('\n', ' ')
            preview = text[:80]
            if len(text) > 80:
                preview += "..."
            print(f"  [{entry.id:03d}] {preview}")
        
        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more")
    
    def _analyze(self):
        """Show compression analysis"""
        stats = self.analyzer.analyze_frequency()
        
        print("\nText Statistics:")
        print(f"  Total entries: {stats['total_entries']}")
        print(f"  Total characters: {stats['total_characters']}")
        print(f"  Total bytes: {stats['total_bytes']}")
        print(f"  Compression ratio: {stats['total_bytes'] / stats['total_characters']:.2f}")
        
        print("\n  Most common characters:")
        for char, count in stats['most_common_chars']:
            char_repr = repr(char) if char == '\n' else char
            print(f"    {char_repr}: {count}")
        
        print("\n  Most common words:")
        for word, count in stats['most_common_words'][:10]:
            print(f"    {word}: {count}")
        
        # Compression candidates
        candidates = self.analyzer.find_compression_candidates()
        if candidates:
            print("\n  Top compression candidates:")
            for word, count, savings in candidates[:10]:
                print(f"    {word}: {count}× (saves {savings} bytes)")
    
    def _save(self, path: str):
        """Save to JSON"""
        data = {
            'entries': [asdict(e) for e in self.entries]
        }
        
        # Convert bytes to hex
        for entry in data['entries']:
            entry['encoded'] = entry['encoded'].hex()
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        print(f"Saved {len(self.entries)} entries to {path}")
    
    def _load(self, path: str):
        """Load from JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Convert hex to bytes
        entries = []
        for entry_data in data['entries']:
            entry_data['encoded'] = bytes.fromhex(entry_data['encoded'])
            entries.append(DialogEntry(**entry_data))
        
        self.entries = entries
        self.analyzer = TextAnalyzer(entries)
        
        print(f"Loaded {len(entries)} entries from {path}")


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Dragon Warrior Text Editor"
    )
    parser.add_argument(
        '--rom',
        help="Path to Dragon Warrior ROM"
    )
    parser.add_argument(
        '--extract',
        action='store_true',
        help="Extract all text to JSON"
    )
    parser.add_argument(
        '--insert',
        help="Insert text from JSON into ROM"
    )
    parser.add_argument(
        '--analyze',
        action='store_true',
        help="Analyze text compression"
    )
    parser.add_argument(
        '--encode',
        help="Encode text string"
    )
    parser.add_argument(
        '--decode',
        help="Decode hex bytes"
    )
    parser.add_argument(
        '--interactive',
        action='store_true',
        help="Interactive editor mode"
    )
    parser.add_argument(
        '--output',
        default='extracted_text.json',
        help="Output file for extraction (default: extracted_text.json)"
    )
    
    args = parser.parse_args()
    
    encoder = TextEncoder()
    
    # Single-action commands
    if args.encode:
        encoded = encoder.encode(args.encode)
        print(f"Text: {args.encode}")
        print(f"Encoded: {encoded.hex()}")
        print(f"Length: {len(encoded)} bytes")
        return 0
    
    if args.decode:
        try:
            data = bytes.fromhex(args.decode)
            text = encoder.decode(data)
            print(f"Bytes: {args.decode}")
            print(f"Decoded: {text}")
            return 0
        except ValueError:
            print("Error: Invalid hex string")
            return 1
    
    # ROM-based commands
    if not args.rom:
        print("Error: --rom required for this operation")
        return 1
    
    with open(args.rom, 'rb') as f:
        rom = f.read()
    
    if args.extract or args.interactive or args.analyze:
        print("Extracting text from ROM...")
        extractor = DialogExtractor(rom)
        entries = extractor.extract_all()
        print(f"Extracted {len(entries)} dialog entries")
        
        if args.extract:
            # Save to JSON
            data = {
                'entries': [asdict(e) for e in entries]
            }
            for entry in data['entries']:
                entry['encoded'] = entry['encoded'].hex()
            
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
            print(f"Saved to {args.output}")
            return 0
        
        if args.analyze:
            analyzer = TextAnalyzer(entries)
            stats = analyzer.analyze_frequency()
            
            print("\nText Statistics:")
            print(f"  Total entries: {stats['total_entries']}")
            print(f"  Total characters: {stats['total_characters']}")
            print(f"  Total bytes: {stats['total_bytes']}")
            print(f"  Compression ratio: {stats['total_bytes'] / stats['total_characters']:.2f}")
            
            candidates = analyzer.find_compression_candidates()
            if candidates:
                print("\nTop 10 compression candidates:")
                for word, count, savings in candidates[:10]:
                    print(f"  {word}: {count}× (saves {savings} bytes)")
            
            return 0
        
        if args.interactive:
            editor = InteractiveEditor(entries)
            editor.run()
            return 0
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
