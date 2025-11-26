"""
pytest configuration and shared fixtures

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import pytest
import tempfile
import shutil
import struct
import json
from pathlib import Path


@pytest.fixture(scope='session')
def test_rom():
    """Create a minimal test ROM file"""
    temp_dir = Path(tempfile.mkdtemp())
    rom_path = temp_dir / "test.nes"
    
    # NES header (16 bytes)
    header = bytes([
        0x4E, 0x45, 0x53, 0x1A,  # "NES" + DOS EOF
        0x02,  # 2 × 16KB PRG-ROM
        0x01,  # 1 × 8KB CHR-ROM
        0x00, 0x00,  # Flags
        0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
    ])
    
    # PRG-ROM (32KB)
    prg_rom = bytes([0xFF] * (2 * 16384))
    
    # CHR-ROM (8KB)
    chr_rom = bytes([0xAA] * (1 * 8192))
    
    with open(rom_path, 'wb') as f:
        f.write(header + prg_rom + chr_rom)
    
    yield rom_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture(scope='session')
def test_monster_data():
    """Sample monster data"""
    return [
        {
            "id": 0,
            "name": "Slime",
            "hp": 3,
            "attack": 5,
            "defense": 2,
            "agility": 3,
            "spell": 0,
            "m_defense": 0,
            "xp": 1,
            "gold": 2
        },
        {
            "id": 1,
            "name": "Red Slime",
            "hp": 4,
            "attack": 7,
            "defense": 2,
            "agility": 4,
            "spell": 0,
            "m_defense": 0,
            "xp": 2,
            "gold": 3
        }
    ]


@pytest.fixture(scope='session')
def test_spell_data():
    """Sample spell data"""
    return [
        {
            "id": 0,
            "name": "HEAL",
            "mp_cost": 4,
            "power": 10
        },
        {
            "id": 1,
            "name": "HURT",
            "mp_cost": 2,
            "power": 5
        }
    ]


@pytest.fixture(scope='session')
def test_item_data():
    """Sample item data"""
    return [
        {
            "id": 0,
            "name": "Bamboo Pole",
            "buy_price": 10,
            "sell_price": 5,
            "attack_bonus": 2,
            "defense_bonus": 0
        },
        {
            "id": 1,
            "name": "Clothes",
            "buy_price": 20,
            "sell_price": 10,
            "attack_bonus": 0,
            "defense_bonus": 2
        }
    ]


@pytest.fixture
def temp_workspace():
    """Create temporary workspace directory"""
    temp_dir = Path(tempfile.mkdtemp())
    
    # Create directory structure
    (temp_dir / "extracted_assets" / "json").mkdir(parents=True)
    (temp_dir / "extracted_assets" / "binary").mkdir(parents=True)
    (temp_dir / "extracted_assets" / "graphics").mkdir(parents=True)
    (temp_dir / "build").mkdir(parents=True)
    (temp_dir / "roms").mkdir(parents=True)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_json_files(temp_workspace, test_monster_data, test_spell_data, test_item_data):
    """Create sample JSON files"""
    json_dir = temp_workspace / "extracted_assets" / "json"
    
    # Save monsters
    with open(json_dir / "monsters.json", 'w') as f:
        json.dump(test_monster_data, f, indent=2)
    
    # Save spells
    with open(json_dir / "spells.json", 'w') as f:
        json.dump(test_spell_data, f, indent=2)
    
    # Save items
    with open(json_dir / "items.json", 'w') as f:
        json.dump(test_item_data, f, indent=2)
    
    return json_dir


@pytest.fixture
def sample_binary_files(temp_workspace):
    """Create sample .dwdata files"""
    binary_dir = temp_workspace / "extracted_assets" / "binary"
    
    # Create monster binary
    monster_data = struct.pack('<BBBBBBBHH', 0, 3, 5, 2, 3, 0, 0, 1, 2)
    
    import zlib
    crc = zlib.crc32(monster_data)
    
    header = struct.pack(
        '<4sBBHIIHHI',
        b'DWDT',  # Magic
        1, 0,     # Version
        0,        # Reserved
        0x01,     # Data type (monsters)
        crc,      # CRC32
        0x5C00,   # ROM offset
        len(monster_data),  # Data size
        0,        # Reserved
        0         # Timestamp
    )
    
    with open(binary_dir / "monsters.dwdata", 'wb') as f:
        f.write(header + monster_data)
    
    return binary_dir


@pytest.fixture
def validation_rules():
    """Validation rules for game data"""
    return {
        'monster': {
            'hp': (1, 255),
            'attack': (0, 255),
            'defense': (0, 255),
            'agility': (0, 255),
            'spell': (0, 9),
            'm_defense': (0, 255),
            'xp': (0, 65535),
            'gold': (0, 65535)
        },
        'spell': {
            'mp_cost': (0, 255),
            'power': (0, 255)
        },
        'item': {
            'buy_price': (0, 65535),
            'sell_price': (0, 65535),
            'attack_bonus': (-128, 127),
            'defense_bonus': (-128, 127)
        }
    }


def pytest_configure(config):
    """Configure pytest"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "requires_rom: marks tests that require actual ROM file"
    )
