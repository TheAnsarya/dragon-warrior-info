#!/usr/bin/env python3
"""
Data Manager for Dragon Warrior ROM Editor

Handles loading, saving, and validation of ROM data.

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import json
import struct
from pathlib import Path
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, asdict


@dataclass
class Monster:
    """Monster data structure"""
    id: int
    name: str
    hp: int
    mp: int
    attack: int
    defense: int
    agility: int
    xp: int
    gold: int
    spell_id: int = 0
    resist_sleep: bool = False
    resist_stopspell: bool = False
    resist_hurt: bool = False
    dodge: int = 0
    sprite_family: str = ""
    palette_index: int = 0


@dataclass
class Spell:
    """Spell data structure"""
    id: int
    name: str
    mp_cost: int
    effect: str
    power: int = 0
    description: str = ""


@dataclass
class Item:
    """Item data structure"""
    id: int
    name: str
    type: str  # weapon, armor, tool, key
    price: int
    sell_price: int
    attack: int = 0
    defense: int = 0
    effect: str = ""
    description: str = ""


class DataManager:
    """
    Manages ROM data loading and saving

    Handles:
        - ROM file I/O
        - Data extraction
        - Data insertion
        - Validation
        - Undo/redo
    """

    # ROM offsets (Dragon Warrior NES)
    MONSTER_DATA_OFFSET = 0x5C10
    MONSTER_COUNT = 39
    MONSTER_SIZE = 16

    SPELL_DATA_OFFSET = 0x1D410
    SPELL_COUNT = 10
    SPELL_SIZE = 4

    ITEM_DATA_OFFSET = 0x1CF70
    ITEM_COUNT = 16
    ITEM_SIZE = 16

    def __init__(self, rom_path: str):
        """
        Initialize data manager

        Args:
            rom_path: Path to ROM file
        """
        self.rom_path = rom_path
        self.rom_data = None

        # Data storage
        self.monsters: List[Monster] = []
        self.spells: List[Spell] = []
        self.items: List[Item] = []

        # Undo/redo stacks
        self.undo_stack: List[Dict] = []
        self.redo_stack: List[Dict] = []

        # Load ROM
        self._load_rom()
        self._extract_data()

    def _load_rom(self):
        """Load ROM file"""
        with open(self.rom_path, 'rb') as f:
            self.rom_data = bytearray(f.read())

        # Verify size (should be 40976 bytes with header)
        if len(self.rom_data) != 40976:
            raise ValueError(
                f"Invalid ROM size: {len(self.rom_data)} bytes "
                f"(expected 40976)"
            )

    def _extract_data(self):
        """Extract all data from ROM"""
        self._extract_monsters()
        self._extract_spells()
        self._extract_items()

    def _extract_monsters(self):
        """Extract monster data"""
        self.monsters = []

        for i in range(self.MONSTER_COUNT):
            offset = self.MONSTER_DATA_OFFSET + (i * self.MONSTER_SIZE)

            # Extract bytes
            hp = struct.unpack('<H', self.rom_data[offset:offset+2])[0]
            mp = self.rom_data[offset+2]
            attack = self.rom_data[offset+3]
            defense = self.rom_data[offset+4]
            agility = self.rom_data[offset+5]
            xp = struct.unpack('<H', self.rom_data[offset+6:offset+8])[0]
            gold = struct.unpack('<H', self.rom_data[offset+8:offset+10])[0]
            spell_id = self.rom_data[offset+10]
            flags = self.rom_data[offset+11]
            sprite_id = self.rom_data[offset+12]
            palette_index = self.rom_data[offset+13]

            # Parse flags
            resist_sleep = bool(flags & 0x01)
            resist_stopspell = bool(flags & 0x02)
            resist_hurt = bool(flags & 0x04)
            dodge = (flags >> 4) & 0x0F

            # Create monster
            monster = Monster(
                id=i,
                name=self._get_monster_name(i),
                hp=hp,
                mp=mp,
                attack=attack,
                defense=defense,
                agility=agility,
                xp=xp,
                gold=gold,
                spell_id=spell_id,
                resist_sleep=resist_sleep,
                resist_stopspell=resist_stopspell,
                resist_hurt=resist_hurt,
                dodge=dodge,
                sprite_family=self._get_sprite_family(sprite_id),
                palette_index=palette_index
            )

            self.monsters.append(monster)

    def _extract_spells(self):
        """Extract spell data"""
        self.spells = []

        for i in range(self.SPELL_COUNT):
            offset = self.SPELL_DATA_OFFSET + (i * self.SPELL_SIZE)

            mp_cost = self.rom_data[offset]
            effect_code = self.rom_data[offset+1]
            power = self.rom_data[offset+2]

            spell = Spell(
                id=i,
                name=self._get_spell_name(i),
                mp_cost=mp_cost,
                effect=self._decode_spell_effect(effect_code),
                power=power,
                description=self._get_spell_description(i)
            )

            self.spells.append(spell)

    def _extract_items(self):
        """Extract item data"""
        self.items = []

        for i in range(self.ITEM_COUNT):
            offset = self.ITEM_DATA_OFFSET + (i * self.ITEM_SIZE)

            type_code = self.rom_data[offset]
            price = struct.unpack('<H', self.rom_data[offset+1:offset+3])[0]
            attack = self.rom_data[offset+3]
            defense = self.rom_data[offset+4]
            effect_code = self.rom_data[offset+5]

            item = Item(
                id=i,
                name=self._get_item_name(i),
                type=self._decode_item_type(type_code),
                price=price,
                sell_price=price // 2,
                attack=attack,
                defense=defense,
                effect=self._decode_item_effect(effect_code),
                description=self._get_item_description(i)
            )

            self.items.append(item)

    def _get_monster_name(self, monster_id: int) -> str:
        """Get monster name by ID"""
        names = [
            "Slime", "Red Slime", "Drakee", "Ghost", "Magician",
            "Magidrakee", "Scorpion", "Druin", "Poltergeist", "Droll",
            "Drakeema", "Skeleton", "Warlock", "Metal Scorpion", "Wolf",
            "Wraith", "Metal Slime", "Specter", "Wolflord", "Druinlord",
            "Drollmagi", "Wyvern", "Rogue Scorpion", "Wraith Knight", "Golem",
            "Goldman", "Knight", "Magiwyvern", "Demon Knight", "Werewolf",
            "Green Dragon", "Starwyvern", "Wizard", "Axe Knight", "Blue Dragon",
            "Stoneman", "Armored Knight", "Red Dragon", "Dragonlord"
        ]
        return names[monster_id] if monster_id < len(names) else f"Monster {monster_id}"

    def _get_spell_name(self, spell_id: int) -> str:
        """Get spell name by ID"""
        names = [
            "HEAL", "HURT", "SLEEP", "RADIANT", "STOPSPELL",
            "OUTSIDE", "RETURN", "REPEL", "HEALMORE", "HURTMORE"
        ]
        return names[spell_id] if spell_id < len(names) else f"Spell {spell_id}"

    def _get_item_name(self, item_id: int) -> str:
        """Get item name by ID"""
        names = [
            "Bamboo Pole", "Club", "Copper Sword", "Hand Axe", "Broad Sword",
            "Flame Sword", "Erdrick's Sword", "Clothes", "Leather Armor", "Chain Mail",
            "Half Plate", "Full Plate", "Magic Armor", "Erdrick's Armor",
            "Small Shield", "Large Shield"
        ]
        return names[item_id] if item_id < len(names) else f"Item {item_id}"

    def _get_sprite_family(self, sprite_id: int) -> str:
        """Get sprite family name"""
        families = {
            0: "slime", 1: "dragon", 2: "knight", 3: "magician",
            4: "beast", 5: "demon", 6: "undead", 7: "metal"
        }
        return families.get(sprite_id, f"sprite_{sprite_id}")

    def _decode_spell_effect(self, code: int) -> str:
        """Decode spell effect code"""
        effects = {
            0: "heal", 1: "damage", 2: "sleep", 3: "light",
            4: "silence", 5: "escape", 6: "return", 7: "repel"
        }
        return effects.get(code, f"effect_{code}")

    def _decode_item_type(self, code: int) -> str:
        """Decode item type code"""
        types = {0: "weapon", 1: "armor", 2: "shield", 3: "tool", 4: "key"}
        return types.get(code, "unknown")

    def _decode_item_effect(self, code: int) -> str:
        """Decode item effect code"""
        effects = {
            0: "none", 1: "heal", 2: "light", 3: "curse_protection",
            4: "hp_regeneration", 5: "mp_regeneration"
        }
        return effects.get(code, f"effect_{code}")

    def _get_spell_description(self, spell_id: int) -> str:
        """Get spell description"""
        descriptions = [
            "Restores HP",
            "Damages enemy",
            "Puts enemy to sleep",
            "Lights dark places",
            "Prevents enemy magic",
            "Escape from dungeon",
            "Return to castle",
            "Repels weak monsters",
            "Restores more HP",
            "Damages enemy more"
        ]
        return descriptions[spell_id] if spell_id < len(descriptions) else ""

    def _get_item_description(self, item_id: int) -> str:
        """Get item description"""
        # Placeholder - extract from ROM text later
        return f"Description for {self._get_item_name(item_id)}"

    def save(self, output_path: str):
        """
        Save modified data to ROM

        Args:
            output_path: Output ROM path
        """
        # Update ROM data
        self._insert_monsters()
        self._insert_spells()
        self._insert_items()

        # Write to file
        with open(output_path, 'wb') as f:
            f.write(self.rom_data)

    def _insert_monsters(self):
        """Insert monster data into ROM"""
        for monster in self.monsters:
            offset = self.MONSTER_DATA_OFFSET + (monster.id * self.MONSTER_SIZE)

            # Pack data
            struct.pack_into('<H', self.rom_data, offset, monster.hp)
            self.rom_data[offset+2] = monster.mp
            self.rom_data[offset+3] = monster.attack
            self.rom_data[offset+4] = monster.defense
            self.rom_data[offset+5] = monster.agility
            struct.pack_into('<H', self.rom_data, offset+6, monster.xp)
            struct.pack_into('<H', self.rom_data, offset+8, monster.gold)
            self.rom_data[offset+10] = monster.spell_id

            # Pack flags
            flags = 0
            if monster.resist_sleep:
                flags |= 0x01
            if monster.resist_stopspell:
                flags |= 0x02
            if monster.resist_hurt:
                flags |= 0x04
            flags |= (monster.dodge & 0x0F) << 4
            self.rom_data[offset+11] = flags

            # Sprite data
            self.rom_data[offset+13] = monster.palette_index

    def _insert_spells(self):
        """Insert spell data into ROM"""
        for spell in self.spells:
            offset = self.SPELL_DATA_OFFSET + (spell.id * self.SPELL_SIZE)

            self.rom_data[offset] = spell.mp_cost
            self.rom_data[offset+2] = spell.power

    def _insert_items(self):
        """Insert item data into ROM"""
        for item in self.items:
            offset = self.ITEM_DATA_OFFSET + (item.id * self.ITEM_SIZE)

            struct.pack_into('<H', self.rom_data, offset+1, item.price)
            self.rom_data[offset+3] = item.attack
            self.rom_data[offset+4] = item.defense

    def validate(self) -> List[str]:
        """
        Validate all data

        Returns:
            List of error messages (empty if valid)
        """
        errors = []

        # Validate monsters
        for monster in self.monsters:
            if not (1 <= monster.hp <= 65535):
                errors.append(f"Monster {monster.name}: Invalid HP {monster.hp}")
            if not (0 <= monster.mp <= 255):
                errors.append(f"Monster {monster.name}: Invalid MP {monster.mp}")
            if not (0 <= monster.attack <= 255):
                errors.append(f"Monster {monster.name}: Invalid attack {monster.attack}")
            if not (0 <= monster.defense <= 255):
                errors.append(f"Monster {monster.name}: Invalid defense {monster.defense}")
            if not (0 <= monster.xp <= 65535):
                errors.append(f"Monster {monster.name}: Invalid XP {monster.xp}")

        # Validate spells
        for spell in self.spells:
            if not (0 <= spell.mp_cost <= 255):
                errors.append(f"Spell {spell.name}: Invalid MP cost {spell.mp_cost}")

        # Validate items
        for item in self.items:
            if not (0 <= item.price <= 65535):
                errors.append(f"Item {item.name}: Invalid price {item.price}")

        return errors

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze ROM data

        Returns:
            Statistics dictionary
        """
        return {
            'size': len(self.rom_data),
            'monsters': len(self.monsters),
            'spells': len(self.spells),
            'items': len(self.items),
            'unused': 500,  # Placeholder
        }

    def export_json(self, path: str):
        """Export data to JSON"""
        data = {
            'monsters': [asdict(m) for m in self.monsters],
            'spells': [asdict(s) for s in self.spells],
            'items': [asdict(i) for i in self.items],
        }

        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def import_json(self, path: str):
        """Import data from JSON"""
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if 'monsters' in data:
            self.monsters = [Monster(**m) for m in data['monsters']]
        if 'spells' in data:
            self.spells = [Spell(**s) for s in data['spells']]
        if 'items' in data:
            self.items = [Item(**i) for i in data['items']]

    def undo(self):
        """Undo last change"""
        # TODO: Implement undo
        pass

    def redo(self):
        """Redo last undone change"""
        # TODO: Implement redo
        pass
