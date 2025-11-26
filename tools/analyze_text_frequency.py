#!/usr/bin/env python3
"""
Dragon Warrior Text Frequency Analyzer

Analyzes text and dialog frequency to identify compression opportunities.

Features:
- Extract all text strings from ROM
- Count word and phrase frequencies
- Identify top compression candidates
- Calculate potential byte savings
- Generate word substitution recommendations

Usage:
    python tools/analyze_text_frequency.py
    python tools/analyze_text_frequency.py --rom custom_rom.nes
    python tools/analyze_text_frequency.py --min-length 4
    python tools/analyze_text_frequency.py --export candidates.json

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
import re
from pathlib import Path
from typing import List, Dict, Tuple, Set
from collections import Counter
import argparse
import json

# Default ROM path
DEFAULT_ROM = "roms/Dragon Warrior (U) (PRG1) [!].nes"

# Dragon Warrior character encoding (simplified)
# In actual ROM, text uses custom encoding with control codes
DW_CHARSET = {
    0x41: 'A', 0x42: 'B', 0x43: 'C', 0x44: 'D', 0x45: 'E', 0x46: 'F', 0x47: 'G',
    0x48: 'H', 0x49: 'I', 0x4A: 'J', 0x4B: 'K', 0x4C: 'L', 0x4D: 'M', 0x4E: 'N',
    0x4F: 'O', 0x50: 'P', 0x51: 'Q', 0x52: 'R', 0x53: 'S', 0x54: 'T', 0x55: 'U',
    0x56: 'V', 0x57: 'W', 0x58: 'X', 0x59: 'Y', 0x5A: 'Z',
    0x20: ' ', 0x2C: ',', 0x2E: '.', 0x21: '!', 0x3F: '?', 0x27: "'",
    # Control codes
    0xFC: '{HERO}',
    0xFD: '{WAIT}',
    0xFE: '{NEWLINE}',
    0xFF: '{END}',
}

# Current word substitutions (0x80-0x8F in ROM)
CURRENT_SUBSTITUTIONS = {
    0x80: "SWORD",
    0x81: "STAFF", 
    0x82: "SHIELD",
    0x83: "ARMOR",
    0x84: "DRAGON",
    0x85: "WARRIOR",
    0x86: "CASTLE",
    0x87: "KING",
    0x88: "MONSTER",
    0x89: "MAGIC",
    0x8A: "WEAPON",
    0x8B: "HEALING",
    0x8C: "BATTLE",
    0x8D: "TOWN",
    0x8E: "DUNGEON",
    0x8F: "TREASURE",
}

# Text data region (estimated)
TEXT_START = 0x6400
TEXT_END = 0x8FFF


class TextFrequencyAnalyzer:
    """Analyze text frequency for compression opportunities"""
    
    def __init__(self, rom_path: str):
        """
        Initialize analyzer
        
        Args:
            rom_path: Path to Dragon Warrior ROM
        """
        self.rom_path = rom_path
        self.rom_data = None
        self.text_data = None
        self.decoded_text = ""
        
    def load_rom(self) -> bool:
        """Load and validate ROM file"""
        if not os.path.exists(self.rom_path):
            print(f"❌ ROM file not found: {self.rom_path}")
            return False
        
        with open(self.rom_path, 'rb') as f:
            self.rom_data = f.read()
        
        if len(self.rom_data) != 81936:
            print(f"⚠ Warning: ROM size is {len(self.rom_data)} bytes (expected 81936)")
        
        if self.rom_data[0:4] != b'NES\x1A':
            print(f"❌ Invalid NES header")
            return False
        
        print(f"✓ Loaded ROM: {self.rom_path}")
        print(f"  Size: {len(self.rom_data):,} bytes")
        
        # Extract text region
        self.text_data = self.rom_data[TEXT_START:TEXT_END]
        print(f"  Text region: 0x{TEXT_START:04X}-0x{TEXT_END:04X} ({len(self.text_data):,} bytes)")
        
        return True
    
    def decode_text(self) -> str:
        """
        Decode text from ROM using character map
        
        Returns:
            Decoded text string
        """
        decoded = []
        i = 0
        
        while i < len(self.text_data):
            byte = self.text_data[i]
            
            # Check for character in charset
            if byte in DW_CHARSET:
                char = DW_CHARSET[byte]
                decoded.append(char)
            elif 0x80 <= byte <= 0x8F:
                # Word substitution
                word = CURRENT_SUBSTITUTIONS.get(byte, f"{{SUB{byte:02X}}}")
                decoded.append(word)
            elif byte == 0x00:
                # Skip null bytes
                pass
            elif 0x41 <= byte <= 0x5A or 0x61 <= byte <= 0x7A:
                # Printable ASCII (fallback)
                decoded.append(chr(byte))
            else:
                # Other bytes (control codes, etc.)
                pass
            
            i += 1
        
        self.decoded_text = ''.join(decoded)
        return self.decoded_text
    
    def extract_words(self, min_length: int = 3) -> List[str]:
        """
        Extract words from decoded text
        
        Args:
            min_length: Minimum word length
            
        Returns:
            List of words
        """
        # Extract words (letters only, uppercase)
        words = re.findall(r'[A-Z]{' + str(min_length) + r',}', self.decoded_text.upper())
        return words
    
    def count_word_frequency(self, min_length: int = 3) -> Counter:
        """
        Count word frequencies
        
        Args:
            min_length: Minimum word length
            
        Returns:
            Counter object with word frequencies
        """
        words = self.extract_words(min_length)
        return Counter(words)
    
    def find_phrases(self, phrase_length: int = 2) -> Counter:
        """
        Find repeated phrases (n-grams)
        
        Args:
            phrase_length: Number of words in phrase
            
        Returns:
            Counter object with phrase frequencies
        """
        words = self.extract_words(min_length=2)
        
        phrases = []
        for i in range(len(words) - phrase_length + 1):
            phrase = ' '.join(words[i:i + phrase_length])
            phrases.append(phrase)
        
        return Counter(phrases)
    
    def calculate_savings(self, word: str, count: int, sub_code_size: int = 1) -> int:
        """
        Calculate potential byte savings for a word substitution
        
        Args:
            word: Word to substitute
            count: Number of occurrences
            sub_code_size: Size of substitution code (1 byte)
            
        Returns:
            Bytes saved
        """
        original_bytes = len(word) * count
        substituted_bytes = sub_code_size * count
        return original_bytes - substituted_bytes
    
    def find_compression_candidates(
        self,
        min_length: int = 4,
        top_n: int = 50
    ) -> List[Tuple[str, int, int]]:
        """
        Find top compression candidates
        
        Args:
            min_length: Minimum word length
            top_n: Number of top candidates to return
            
        Returns:
            List of (word, count, savings) tuples
        """
        freq = self.count_word_frequency(min_length)
        
        # Calculate savings for each word
        candidates = []
        for word, count in freq.items():
            savings = self.calculate_savings(word, count)
            
            # Only include if saves bytes (length > 1)
            if savings > 0:
                candidates.append((word, count, savings))
        
        # Sort by savings (descending)
        candidates.sort(key=lambda x: x[2], reverse=True)
        
        return candidates[:top_n]
    
    def recommend_substitutions(
        self,
        num_codes: int = 16,
        min_length: int = 4
    ) -> List[Dict]:
        """
        Recommend new word substitutions
        
        Args:
            num_codes: Number of substitution codes available
            min_length: Minimum word length
            
        Returns:
            List of recommendation dicts
        """
        candidates = self.find_compression_candidates(min_length, num_codes)
        
        recommendations = []
        total_savings = 0
        
        for i, (word, count, savings) in enumerate(candidates):
            code = 0x90 + i  # Next available codes after 0x8F
            
            rec = {
                'code': f"0x{code:02X}",
                'word': word,
                'length': len(word),
                'occurrences': count,
                'savings_bytes': savings,
                'savings_percent': (savings / (len(word) * count)) * 100 if count > 0 else 0
            }
            
            recommendations.append(rec)
            total_savings += savings
        
        return recommendations, total_savings
    
    def analyze_current_substitutions(self) -> List[Dict]:
        """
        Analyze effectiveness of current substitutions
        
        Returns:
            List of analysis dicts
        """
        freq = self.count_word_frequency(min_length=3)
        
        analysis = []
        total_current_savings = 0
        
        for code, word in CURRENT_SUBSTITUTIONS.items():
            count = freq.get(word, 0)
            savings = self.calculate_savings(word, count) if count > 0 else 0
            
            analysis.append({
                'code': f"0x{code:02X}",
                'word': word,
                'occurrences': count,
                'savings': savings,
                'efficiency': 'high' if count > 20 else 'medium' if count > 10 else 'low'
            })
            
            total_current_savings += savings
        
        return analysis, total_current_savings
    
    def generate_report(self) -> Dict:
        """
        Generate comprehensive frequency analysis report
        
        Returns:
            Report dict
        """
        print("\n" + "=" * 70)
        print("Dragon Warrior Text Frequency Analysis Report")
        print("=" * 70)
        
        # Decode text
        print("\n--- Decoding Text Data ---")
        self.decode_text()
        
        print(f"Total characters decoded: {len(self.decoded_text):,}")
        
        # Word frequency
        print("\n--- Word Frequency Analysis ---")
        words = self.extract_words(min_length=3)
        unique_words = len(set(words))
        
        print(f"Total words: {len(words):,}")
        print(f"Unique words: {unique_words:,}")
        
        # Current substitutions
        print("\n--- Current Substitution Effectiveness ---")
        current_analysis, current_savings = self.analyze_current_substitutions()
        
        print(f"Current substitution codes: {len(CURRENT_SUBSTITUTIONS)}")
        print(f"Total bytes saved: {current_savings:,}")
        
        print("\nTop Current Substitutions:")
        sorted_current = sorted(current_analysis, key=lambda x: x['savings'], reverse=True)
        for item in sorted_current[:10]:
            if item['occurrences'] > 0:
                print(f"  {item['word']:12} ({item['code']}): {item['occurrences']:3} uses → {item['savings']:4} bytes saved")
        
        # New recommendations
        print("\n--- New Substitution Recommendations ---")
        recommendations, new_savings = self.recommend_substitutions(num_codes=16, min_length=4)
        
        print(f"Potential new codes: {len(recommendations)}")
        print(f"Additional savings: {new_savings:,} bytes")
        
        print("\nTop Recommendations:")
        for rec in recommendations[:15]:
            print(f"  {rec['word']:12} ({rec['code']}): {rec['occurrences']:3} uses → {rec['savings_bytes']:4} bytes saved")
        
        # Phrase analysis
        print("\n--- Common Phrases (2-word) ---")
        phrases = self.find_phrases(phrase_length=2)
        top_phrases = phrases.most_common(10)
        
        print("Top phrases:")
        for phrase, count in top_phrases:
            # Calculate savings if we made this a single substitution
            savings = self.calculate_savings(phrase.replace(' ', ''), count)
            print(f"  '{phrase}': {count} times → {savings} bytes saved")
        
        # Summary
        print("\n" + "=" * 70)
        print("Compression Summary")
        print("=" * 70)
        
        total_potential = current_savings + new_savings
        
        print(f"\nCurrent Savings:    {current_savings:7,} bytes")
        print(f"Potential Savings:  {new_savings:7,} bytes")
        print(f"Total Potential:    {total_potential:7,} bytes")
        
        text_size = len(self.text_data)
        print(f"\nText region size:   {text_size:7,} bytes")
        print(f"Compression ratio:  {(1 - total_potential/text_size)*100:6.2f}%")
        
        print("\n" + "=" * 70)
        
        # Build report dict
        report = {
            'rom_path': self.rom_path,
            'text_region': {
                'start': f"0x{TEXT_START:04X}",
                'end': f"0x{TEXT_END:04X}",
                'size': text_size
            },
            'statistics': {
                'total_characters': len(self.decoded_text),
                'total_words': len(words),
                'unique_words': unique_words
            },
            'current_substitutions': {
                'count': len(CURRENT_SUBSTITUTIONS),
                'savings': current_savings,
                'analysis': current_analysis
            },
            'recommendations': {
                'count': len(recommendations),
                'potential_savings': new_savings,
                'substitutions': recommendations
            },
            'phrases': {
                'top_2word': [
                    {'phrase': phrase, 'count': count}
                    for phrase, count in top_phrases
                ]
            },
            'summary': {
                'current_savings': current_savings,
                'potential_new_savings': new_savings,
                'total_potential': total_potential,
                'compression_percent': (total_potential / text_size) * 100 if text_size > 0 else 0
            }
        }
        
        return report
    
    def export_report(self, output_path: str, report: Dict) -> bool:
        """
        Export report to JSON
        
        Args:
            output_path: Output file path
            report: Report dict
            
        Returns:
            True if successful
        """
        try:
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            print(f"\n✓ Report exported to: {output_path}")
            return True
        except Exception as e:
            print(f"\n❌ Failed to export: {e}")
            return False


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Analyze Dragon Warrior text frequency for compression opportunities',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/analyze_text_frequency.py
  python tools/analyze_text_frequency.py --rom custom_rom.nes
  python tools/analyze_text_frequency.py --min-length 5
  python tools/analyze_text_frequency.py --export text_analysis.json
        """
    )
    
    parser.add_argument(
        '--rom',
        default=DEFAULT_ROM,
        help=f'Path to Dragon Warrior ROM (default: {DEFAULT_ROM})'
    )
    
    parser.add_argument(
        '--min-length',
        type=int,
        default=4,
        help='Minimum word length for analysis (default: 4)'
    )
    
    parser.add_argument(
        '--export',
        metavar='PATH',
        help='Export report to JSON file'
    )
    
    args = parser.parse_args()
    
    # Initialize analyzer
    analyzer = TextFrequencyAnalyzer(args.rom)
    
    if not analyzer.load_rom():
        return 1
    
    # Generate report
    report = analyzer.generate_report()
    
    # Export if requested
    if args.export:
        default_path = 'extracted_assets/reports/text_frequency_analysis.json'
        output_path = args.export if args.export != 'True' else default_path
        analyzer.export_report(output_path, report)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
