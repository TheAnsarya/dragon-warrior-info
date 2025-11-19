#!/usr/bin/env python3
"""
Dragon Warrior Data Structures
Define all game data structures for JSON serialization and editing
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum, IntEnum
import json

class MonsterType(IntEnum):
    """Monster classification types"""
    SLIME = 0
    DRAGON = 1
    BEAST = 2
    DEMON = 3
    UNDEAD = 4
    METAL = 5

class SpellType(IntEnum):
    """Spell classification"""
    OFFENSIVE = 0
    DEFENSIVE = 1
    HEALING = 2
    UTILITY = 3

class ItemType(IntEnum):
    """Item classification"""
    WEAPON = 0
    ARMOR = 1
    SHIELD = 2
    TOOL = 3
    KEY_ITEM = 4

class TerrainType(IntEnum):
    """Map terrain types"""
    GRASS = 0
    WATER = 1
    MOUNTAIN = 2
    FOREST = 3
    SWAMP = 4
    DESERT = 5
    TOWN = 6
    CASTLE = 7
    CAVE = 8
    SHRINE = 9

@dataclass
class Position:
    """2D position"""
    x: int
    y: int

@dataclass
class Color:
    """RGB color"""
    r: int
    g: int
    b: int

@dataclass
class Palette:
    """NES palette (4 colors)"""
    name: str
    colors: List[Color]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'name': self.name,
            'colors': [{'r': c.r, 'g': c.g, 'b': c.b} for c in self.colors]
        }

@dataclass
class MonsterStats:
    """Monster battle statistics"""
    id: int
    name: str
    hp: int
    strength: int
    agility: int
    max_damage: int
    dodge_rate: int
    sleep_resistance: int
    hurt_resistance: int
    experience: int
    gold: int
    monster_type: MonsterType
    sprite_id: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ItemData:
    """Item definition"""
    id: int
    name: str
    item_type: ItemType
    attack_bonus: int
    defense_bonus: int
    buy_price: int
    sell_price: int
    equippable: bool
    useable: bool
    sprite_id: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class SpellData:
    """Spell definition"""
    id: int
    name: str
    spell_type: SpellType
    mp_cost: int
    power: int
    learn_level: int
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class ShopData:
    """Shop inventory"""
    id: int
    name: str
    location: str
    items: List[int]  # Item IDs
    weapons: List[int]  # Weapon IDs
    armor: List[int]  # Armor IDs
    inn_price: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class DialogEntry:
    """NPC dialog text"""
    id: int
    npc_name: str
    location: str
    text: str
    pointer: int  # ROM pointer
    compressed: bool

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class MapTile:
    """Individual map tile"""
    tile_id: int
    terrain_type: TerrainType
    walkable: bool
    encounter_rate: int = 0

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class MapData:
    """Map information"""
    id: int
    name: str
    width: int
    height: int
    tiles: List[List[MapTile]]
    encounters: List[int]  # Monster group IDs
    music_id: int
    palette_id: int

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'width': self.width,
            'height': self.height,
            'tiles': [[tile.to_dict() for tile in row] for row in self.tiles],
            'encounters': self.encounters,
            'music_id': self.music_id,
            'palette_id': self.palette_id
        }

@dataclass
class NPCData:
    """NPC definition"""
    id: int
    name: str
    map_id: int
    position: Position
    sprite_id: int
    dialog_id: int
    shop_id: Optional[int] = None
    gives_item: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'map_id': self.map_id,
            'position': asdict(self.position),
            'sprite_id': self.sprite_id,
            'dialog_id': self.dialog_id,
            'shop_id': self.shop_id,
            'gives_item': self.gives_item
        }

@dataclass
class GraphicsData:
    """Graphics tile data"""
    id: int
    name: str
    width: int
    height: int
    tile_data: List[int]  # CHR-ROM data
    palette_id: int

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class GameData:
    """Complete game data structure"""
    monsters: Dict[int, MonsterStats]
    items: Dict[int, ItemData]
    spells: Dict[int, SpellData]
    shops: Dict[int, ShopData]
    dialogs: Dict[int, DialogEntry]
    maps: Dict[int, MapData]
    npcs: Dict[int, NPCData]
    graphics: Dict[int, GraphicsData]
    palettes: Dict[int, Palette]

    def to_dict(self) -> Dict[str, Any]:
        return {
            'monsters': {str(k): v.to_dict() for k, v in self.monsters.items()},
            'items': {str(k): v.to_dict() for k, v in self.items.items()},
            'spells': {str(k): v.to_dict() for k, v in self.spells.items()},
            'shops': {str(k): v.to_dict() for k, v in self.shops.items()},
            'dialogs': {str(k): v.to_dict() for k, v in self.dialogs.items()},
            'maps': {str(k): v.to_dict() for k, v in self.maps.items()},
            'npcs': {str(k): v.to_dict() for k, v in self.npcs.items()},
            'graphics': {str(k): v.to_dict() for k, v in self.graphics.items()},
            'palettes': {str(k): v.to_dict() for k, v in self.palettes.items()}
        }

    def save_json(self, filepath: str):
        """Save game data to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, indent=2, ensure_ascii=False)

    @classmethod
    def load_json(cls, filepath: str) -> 'GameData':
        """Load game data from JSON file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Convert back to dataclass instances
        monsters = {int(k): MonsterStats(**v) for k, v in data.get('monsters', {}).items()}
        items = {int(k): ItemData(**v) for k, v in data.get('items', {}).items()}
        spells = {int(k): SpellData(**v) for k, v in data.get('spells', {}).items()}
        shops = {int(k): ShopData(**v) for k, v in data.get('shops', {}).items()}
        dialogs = {int(k): DialogEntry(**v) for k, v in data.get('dialogs', {}).items()}

        # Maps need special handling for nested structures
        maps = {}
        for k, v in data.get('maps', {}).items():
            tiles = []
            for row in v['tiles']:
                tile_row = []
                for tile_data in row:
                    tile_row.append(MapTile(**tile_data))
                tiles.append(tile_row)

            map_data = MapData(
                id=v['id'],
                name=v['name'],
                width=v['width'],
                height=v['height'],
                tiles=tiles,
                encounters=v['encounters'],
                music_id=v['music_id'],
                palette_id=v['palette_id']
            )
            maps[int(k)] = map_data

        # NPCs with position handling
        npcs = {}
        for k, v in data.get('npcs', {}).items():
            npc = NPCData(
                id=v['id'],
                name=v['name'],
                map_id=v['map_id'],
                position=Position(**v['position']),
                sprite_id=v['sprite_id'],
                dialog_id=v['dialog_id'],
                shop_id=v.get('shop_id'),
                gives_item=v.get('gives_item')
            )
            npcs[int(k)] = npc

        graphics = {int(k): GraphicsData(**v) for k, v in data.get('graphics', {}).items()}

        # Palettes with color handling
        palettes = {}
        for k, v in data.get('palettes', {}).items():
            colors = [Color(**color_data) for color_data in v['colors']]
            palette = Palette(name=v['name'], colors=colors)
            palettes[int(k)] = palette

        return cls(
            monsters=monsters,
            items=items,
            spells=spells,
            shops=shops,
            dialogs=dialogs,
            maps=maps,
            npcs=npcs,
            graphics=graphics,
            palettes=palettes
        )

# Dragon Warrior specific data constants
DW_MONSTERS = {
    0: "Slime", 1: "Red Slime", 2: "Drakee", 3: "Ghost", 4: "Magician",
    5: "Magidrakee", 6: "Scorpion", 7: "Druin", 8: "Poltergeist",
    9: "Droll", 10: "Drakeema", 11: "Skeleton", 12: "Warlock",
    13: "Metal Slime", 14: "Wolf", 15: "Wraith", 16: "Metal Scorpion",
    17: "Orc", 18: "Specter", 19: "Wolflord", 20: "Druinlord",
    21: "Drollmagi", 22: "Wyvern", 23: "Rogue Scorpion", 24: "Wraith Knight",
    25: "Golem", 26: "Goldman", 27: "Knight", 28: "Magiwyvern",
    29: "Demon Knight", 30: "Werewolf", 31: "Green Dragon",
    32: "Starwyvern", 33: "Wizard", 34: "Axe Knight", 35: "Blue Dragon",
    36: "Stone Man", 37: "Armored Knight", 38: "Red Dragon", 39: "Dragonlord"
}

DW_ITEMS = {
    0: "Torch", 1: "Club", 2: "Copper Sword", 3: "Hand Axe",
    4: "Broad Sword", 5: "Flame Sword", 6: "Erdrick's Sword",
    7: "Clothes", 8: "Leather Armor", 9: "Chain Mail", 10: "Half Plate",
    11: "Full Plate", 12: "Magic Armor", 13: "Erdrick's Armor",
    14: "Small Shield", 15: "Large Shield", 16: "Silver Shield",
    17: "Erdrick's Shield", 18: "Herb", 19: "Key", 20: "Magic Key",
    21: "Erdrick's Token", 22: "Gwaelin's Love", 23: "Cursed Belt",
    24: "Silver Harp", 25: "Death Necklace", 26: "Stones of Sunlight",
    27: "Staff of Rain", 28: "Rainbow Drop"
}

DW_SPELLS = {
    0: "Heal", 1: "Hurt", 2: "Sleep", 3: "Radiant", 4: "Stopspell",
    5: "Outside", 6: "Return", 7: "Repel", 8: "Healmore", 9: "Hurtmore"
}

DW_MAPS = {
    0: "Overworld", 1: "Tantegel Castle", 2: "Brecconary",
    3: "Charlock Castle", 4: "Hauksness", 5: "Cantlin",
    6: "Rimuldar", 7: "Kol", 8: "Garinham"
}
