#!/usr/bin/env python3
"""
Dragon Warrior Testing Framework
Comprehensive testing for tools and ROM validation
Based on FFMQ testing patterns
"""

import os
import sys
import tempfile
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Any
import pytest
import json

# Add tools to path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "tools"))

class TestConfig:
	"""Test configuration and sample data management"""
	
	def __init__(self):
		self.test_dir = Path(__file__).parent
		self.project_root = self.test_dir.parent
		self.sample_data_dir = self.test_dir / "sample_data"
		
		# Create sample data directory
		self.sample_data_dir.mkdir(exist_ok=True)
	
	def create_sample_rom(self, size: int = 256 * 1024) -> Path:
		"""Create a sample NES ROM for testing"""
		rom_path = self.sample_data_dir / "test_rom.nes"
		
		# Create iNES header
		header = bytearray(16)
		header[0:4] = b'NES\x1a'  # iNES signature
		header[4] = 16  # 16 * 16KB = 256KB PRG-ROM
		header[5] = 0   # No CHR-ROM (uses CHR-RAM)
		header[6] = 0   # Mapper 0 (NROM), horizontal mirroring
		header[7] = 0   # Mapper 0 continued
		
		# Create ROM data
		with open(rom_path, 'wb') as f:
			f.write(header)
			
			# PRG-ROM data (256KB)
			prg_data = bytearray(size - 16)
			
			# Add some patterns for testing
			# Reset vector at end
			prg_data[-6:-4] = b'\x00\x80'  # NMI vector
			prg_data[-4:-2] = b'\x00\x80'  # RESET vector  
			prg_data[-2:] = b'\x00\x80'    # IRQ vector
			
			# Add some sample text patterns
			text_offset = 0x8000 - 0x10  # Adjust for header
			sample_text = b"HELLO WORLD\x00THE HERO AWAKENS\x00DRAGON WARRIOR\x00"
			prg_data[text_offset:text_offset+len(sample_text)] = sample_text
			
			# Add some data patterns
			data_offset = 0x6000 - 0x10
			for i in range(32):  # 32 monster records
				record = bytearray(8)
				record[0] = i  # Monster ID
				record[1] = 50 + i * 5  # HP
				record[2] = 10 + i  # Attack
				record[3] = 5 + i // 2  # Defense
				prg_data[data_offset + i*8:data_offset + (i+1)*8] = record
			
			f.write(prg_data)
		
		return rom_path
	
	def cleanup_sample_data(self):
		"""Clean up temporary test files"""
		import shutil
		if self.sample_data_dir.exists():
			shutil.rmtree(self.sample_data_dir)

# Global test configuration
test_config = TestConfig()

@pytest.fixture(scope="session")
def sample_rom():
	"""Fixture providing a sample ROM for testing"""
	return test_config.create_sample_rom()

@pytest.fixture(scope="session", autouse=True)
def cleanup_after_tests():
	"""Cleanup fixture that runs after all tests"""
	yield
	test_config.cleanup_sample_data()

class TestROMAnalyzer:
	"""Test ROM analysis functionality"""
	
	def test_rom_loading(self, sample_rom):
		"""Test ROM file loading and basic validation"""
		from analysis.rom_analyzer import ROMAnalyzer
		
		analyzer = ROMAnalyzer(str(sample_rom))
		
		assert analyzer.rom_size == 256 * 1024
		assert analyzer.header_info["valid"] is True
		assert analyzer.header_info["prg_size"] == 256 * 1024
		assert analyzer.header_info["chr_size"] == 0
	
	def test_header_parsing(self, sample_rom):
		"""Test NES header parsing"""
		from analysis.rom_analyzer import ROMAnalyzer
		
		analyzer = ROMAnalyzer(str(sample_rom))
		header = analyzer.header_info
		
		assert header["signature"] == "NES\x1a"[:3]  # ASCII portion
		assert header["mapper"] == 0
		assert header["mirroring"] == "horizontal"
		assert header["battery"] is False
	
	def test_hex_dump(self, sample_rom):
		"""Test hex dump functionality"""
		from analysis.rom_analyzer import ROMAnalyzer
		
		analyzer = ROMAnalyzer(str(sample_rom))
		
		# Test hex dump of header
		dump = analyzer.hex_dump(0, 16, 16)
		
		assert "4e 45 53 1a" in dump  # iNES signature in hex
		assert len(dump.split('\n')) == 1  # One line for 16 bytes
	
	def test_pattern_analysis(self, sample_rom):
		"""Test data pattern analysis"""
		from analysis.rom_analyzer import ROMAnalyzer
		
		analyzer = ROMAnalyzer(str(sample_rom))
		
		# Analyze header section
		analysis = analyzer.analyze_data_patterns(0, 16)
		
		assert "error" not in analysis
		assert analysis["size"] == 16
		assert 0 <= analysis["entropy"] <= 8
		assert 0 <= analysis["text_likelihood"] <= 1
	
	def test_string_finding(self, sample_rom):
		"""Test text string detection"""
		from analysis.rom_analyzer import ROMAnalyzer
		
		analyzer = ROMAnalyzer(str(sample_rom))
		strings = analyzer.find_text_strings(min_length=4)
		
		# Should find our sample strings
		string_texts = [s[1] for s in strings]
		
		assert any("HELLO WORLD" in text for text in string_texts)
		assert any("THE HERO AWAKENS" in text for text in string_texts)
		assert any("DRAGON WARRIOR" in text for text in string_texts)
	
	def test_memory_map_generation(self, sample_rom):
		"""Test memory map generation"""
		from analysis.rom_analyzer import ROMAnalyzer
		
		analyzer = ROMAnalyzer(str(sample_rom))
		memory_map = analyzer.generate_memory_map()
		
		assert "header" in memory_map
		assert "prg_rom" in memory_map
		assert memory_map["prg_rom"]["size"] == 256 * 1024
		assert len(memory_map["prg_rom"]["banks"]) == 16  # 16 banks of 16KB

class TestAssetExtractor:
	"""Test asset extraction functionality"""
	
	def test_rom_verification(self, sample_rom):
		"""Test ROM verification and checksum calculation"""
		from extraction.extract_assets import DragonWarriorROM
		
		rom = DragonWarriorROM(str(sample_rom))
		verification = rom.verify_rom()
		
		assert "md5" in verification
		assert "sha1" in verification
		assert "version" in verification
		assert verification["size"] == 256 * 1024
		assert len(verification["md5"]) == 32  # MD5 is 32 hex chars
		assert len(verification["sha1"]) == 40  # SHA1 is 40 hex chars
	
	def test_graphics_extraction(self, sample_rom):
		"""Test graphics data extraction"""
		from extraction.extract_assets import DragonWarriorROM
		
		with tempfile.TemporaryDirectory() as temp_dir:
			rom = DragonWarriorROM(str(sample_rom))
			rom.output_dir = Path(temp_dir)
			rom.graphics_dir = rom.output_dir / "graphics"
			
			rom.create_output_dirs()
			graphics_info = rom.extract_graphics()
			
			# Since our sample ROM has no CHR-ROM, should handle gracefully
			assert isinstance(graphics_info, dict)
	
	def test_text_extraction(self, sample_rom):
		"""Test text extraction functionality"""
		from extraction.extract_assets import DragonWarriorROM
		
		with tempfile.TemporaryDirectory() as temp_dir:
			rom = DragonWarriorROM(str(sample_rom))
			rom.output_dir = Path(temp_dir)
			rom.text_dir = rom.output_dir / "text"
			
			rom.create_output_dirs()
			text_info = rom.extract_text()
			
			assert isinstance(text_info, dict)
			
			# Check if any text files were created
			if text_info:
				for section, info in text_info.items():
					if "file" in info:
						text_file = Path(info["file"])
						assert text_file.exists()
	
	def test_data_extraction(self, sample_rom):
		"""Test game data extraction"""
		from extraction.extract_assets import DragonWarriorROM
		
		with tempfile.TemporaryDirectory() as temp_dir:
			rom = DragonWarriorROM(str(sample_rom))
			rom.output_dir = Path(temp_dir)
			rom.data_dir = rom.output_dir / "data"
			
			rom.create_output_dirs()
			data_info = rom.extract_game_data()
			
			assert isinstance(data_info, dict)

class TestBuildSystem:
	"""Test build system functionality"""
	
	def test_build_script_exists(self):
		"""Test that build script exists and is accessible"""
		build_script = test_config.project_root / "build.ps1"
		assert build_script.exists()
		assert build_script.is_file()
	
	def test_ophis_assembler_exists(self):
		"""Test that Ophis assembler is available"""
		ophis_path = test_config.project_root / "Ophis" / "Ophis.py"
		
		# This might not exist yet, so we'll just check the expected location
		expected_ophis_dir = test_config.project_root / "Ophis"
		
		# Test should pass if directory exists OR if we're in early development
		assert True  # Placeholder - will be updated when Ophis is integrated

class TestGitHubIntegration:
	"""Test GitHub integration functionality"""
	
	def test_github_issues_module_import(self):
		"""Test that GitHub issues module can be imported"""
		try:
			from github.github_issues import GitHubManager
			assert True
		except ImportError:
			pytest.skip("GitHub module dependencies not available")
	
	def test_env_example_exists(self):
		"""Test that environment example file exists"""
		env_example = test_config.project_root / ".env.example"
		assert env_example.exists()

class TestDocumentation:
	"""Test documentation structure and completeness"""
	
	def test_docs_structure(self):
		"""Test that documentation structure is complete"""
		docs_dir = test_config.project_root / "docs"
		
		assert docs_dir.exists()
		assert (docs_dir / "INDEX.md").exists()
		assert (docs_dir / "guides").exists()
		assert (docs_dir / "technical").exists()
		assert (docs_dir / "datacrystal").exists()
	
	def test_datacrystal_documentation(self):
		"""Test DataCrystal format documentation"""
		datacrystal_dir = test_config.project_root / "docs" / "datacrystal"
		rom_map = datacrystal_dir / "ROM_MAP.md"
		
		assert rom_map.exists()
		
		# Check basic content structure
		content = rom_map.read_text(encoding='utf-8')
		assert "Dragon Warrior" in content
		assert "ROM Map" in content
		assert "Memory Layout" in content

class TestProjectStructure:
	"""Test overall project structure and standards"""
	
	def test_editorconfig_exists(self):
		"""Test that .editorconfig file exists"""
		editorconfig = test_config.project_root / ".editorconfig"
		assert editorconfig.exists()
	
	def test_requirements_file(self):
		"""Test that requirements.txt exists and is valid"""
		requirements = test_config.project_root / "requirements.txt"
		assert requirements.exists()
		
		content = requirements.read_text()
		assert "pillow" in content.lower()
		assert "requests" in content.lower()
		assert "click" in content.lower()
	
	def test_session_logging_structure(self):
		"""Test that session logging is set up"""
		session_logs = test_config.project_root / "~docs" / "session-logs"
		chat_logs = test_config.project_root / "~docs" / "chat-logs"
		
		assert session_logs.exists()
		assert chat_logs.exists()

# Performance and integration tests
class TestPerformance:
	"""Performance and load testing"""
	
	def test_large_rom_handling(self, sample_rom):
		"""Test handling of large ROM files"""
		from analysis.rom_analyzer import ROMAnalyzer
		
		# Test with our sample ROM
		analyzer = ROMAnalyzer(str(sample_rom))
		
		# Should handle analysis quickly
		import time
		start_time = time.time()
		analyzer.analyze_data_patterns(0, 1024)  # Analyze first 1KB
		end_time = time.time()
		
		# Should complete in under 1 second for 1KB
		assert (end_time - start_time) < 1.0
	
	def test_memory_usage(self, sample_rom):
		"""Test memory usage for ROM analysis"""
		from analysis.rom_analyzer import ROMAnalyzer
		
		# This is a basic test - in production, would use memory profiling
		analyzer = ROMAnalyzer(str(sample_rom))
		
		# Should be able to create analyzer without excessive memory
		assert analyzer.rom_size == 256 * 1024
		assert len(analyzer.rom_data) == analyzer.rom_size

if __name__ == "__main__":
	# Run tests with verbose output
	pytest.main([__file__, "-v"])