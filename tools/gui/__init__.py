"""
Dragon Warrior ROM Editor GUI Package

PyQt5-based editor for Dragon Warrior ROM hacks.
"""

__version__ = "1.0.0"
__author__ = "Dragon Warrior ROM Hacking Toolkit"

from .main_window import DragonWarriorEditor
from .data_manager import DataManager, Monster, Spell, Item
from .monster_editor_tab import MonsterEditorTab
from .spell_editor_tab import SpellEditorTab
from .item_editor_tab import ItemEditorTab

__all__ = [
    'DragonWarriorEditor',
    'DataManager',
    'Monster',
    'Spell',
    'Item',
    'MonsterEditorTab',
    'SpellEditorTab',
    'ItemEditorTab',
]
