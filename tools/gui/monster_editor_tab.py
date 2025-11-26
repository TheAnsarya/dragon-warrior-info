#!/usr/bin/env python3
"""
Monster Editor Tab

PyQt5 tab for editing monster data with live preview.

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QSpinBox, QCheckBox, QComboBox, QGroupBox,
    QFormLayout, QSplitter, QTextEdit, QHeaderView, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor


class MonsterEditorTab(QWidget):
    """
    Monster editor tab with table view and detail editor

    Features:
        - Table view of all monsters
        - Detail editor for selected monster
        - Sprite preview
        - Stat calculator
        - Validation
    """

    data_modified = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize monster editor tab"""
        super().__init__(parent)

        self.parent_window = parent
        self.data_manager = None
        self.current_monster_id = None

        self._create_ui()

    def _create_ui(self):
        """Create UI layout"""
        layout = QHBoxLayout()

        # Splitter for table and detail view
        splitter = QSplitter(Qt.Horizontal)

        # Left: Monster table
        table_widget = self._create_table()
        splitter.addWidget(table_widget)

        # Right: Detail editor
        detail_widget = self._create_detail_editor()
        splitter.addWidget(detail_widget)

        # Set splitter sizes (30% table, 70% details)
        splitter.setSizes([300, 700])

        layout.addWidget(splitter)
        self.setLayout(layout)

    def _create_table(self) -> QWidget:
        """Create monster table"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Table
        self.monster_table = QTableWidget()
        self.monster_table.setColumnCount(7)
        self.monster_table.setHorizontalHeaderLabels([
            "ID", "Name", "HP", "Attack", "Defense", "XP", "Gold"
        ])

        # Resize columns
        header = self.monster_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        # Selection
        self.monster_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.monster_table.setSelectionMode(QTableWidget.SingleSelection)
        self.monster_table.itemSelectionChanged.connect(self._on_monster_selected)

        layout.addWidget(self.monster_table)

        # Buttons
        button_layout = QHBoxLayout()

        add_btn = QPushButton("Add Monster")
        add_btn.clicked.connect(self._add_monster)
        button_layout.addWidget(add_btn)

        delete_btn = QPushButton("Delete")
        delete_btn.clicked.connect(self._delete_monster)
        button_layout.addWidget(delete_btn)

        clone_btn = QPushButton("Clone")
        clone_btn.clicked.connect(self._clone_monster)
        button_layout.addWidget(clone_btn)

        layout.addLayout(button_layout)

        widget.setLayout(layout)
        return widget

    def _create_detail_editor(self) -> QWidget:
        """Create detail editor"""
        widget = QWidget()
        layout = QVBoxLayout()

        # Monster info group
        info_group = QGroupBox("Monster Information")
        info_layout = QFormLayout()

        self.name_label = QLabel("(No monster selected)")
        info_layout.addRow("Name:", self.name_label)

        self.id_label = QLabel("-")
        info_layout.addRow("ID:", self.id_label)

        info_group.setLayout(info_layout)
        layout.addWidget(info_group)

        # Stats group
        stats_group = QGroupBox("Base Stats")
        stats_layout = QFormLayout()

        self.hp_spin = QSpinBox()
        self.hp_spin.setRange(1, 65535)
        self.hp_spin.valueChanged.connect(self._on_stat_changed)
        stats_layout.addRow("HP:", self.hp_spin)

        self.mp_spin = QSpinBox()
        self.mp_spin.setRange(0, 255)
        self.mp_spin.valueChanged.connect(self._on_stat_changed)
        stats_layout.addRow("MP:", self.mp_spin)

        self.attack_spin = QSpinBox()
        self.attack_spin.setRange(0, 255)
        self.attack_spin.valueChanged.connect(self._on_stat_changed)
        stats_layout.addRow("Attack:", self.attack_spin)

        self.defense_spin = QSpinBox()
        self.defense_spin.setRange(0, 255)
        self.defense_spin.valueChanged.connect(self._on_stat_changed)
        stats_layout.addRow("Defense:", self.defense_spin)

        self.agility_spin = QSpinBox()
        self.agility_spin.setRange(0, 255)
        self.agility_spin.valueChanged.connect(self._on_stat_changed)
        stats_layout.addRow("Agility:", self.agility_spin)

        stats_group.setLayout(stats_layout)
        layout.addWidget(stats_group)

        # Rewards group
        rewards_group = QGroupBox("Rewards")
        rewards_layout = QFormLayout()

        self.xp_spin = QSpinBox()
        self.xp_spin.setRange(0, 65535)
        self.xp_spin.valueChanged.connect(self._on_stat_changed)
        rewards_layout.addRow("XP:", self.xp_spin)

        self.gold_spin = QSpinBox()
        self.gold_spin.setRange(0, 65535)
        self.gold_spin.valueChanged.connect(self._on_stat_changed)
        rewards_layout.addRow("Gold:", self.gold_spin)

        rewards_group.setLayout(rewards_layout)
        layout.addWidget(rewards_group)

        # Abilities group
        abilities_group = QGroupBox("Abilities")
        abilities_layout = QFormLayout()

        self.spell_combo = QComboBox()
        self.spell_combo.addItems([
            "None", "HEAL", "HURT", "SLEEP", "RADIANT", "STOPSPELL",
            "OUTSIDE", "RETURN", "REPEL", "HEALMORE", "HURTMORE"
        ])
        self.spell_combo.currentIndexChanged.connect(self._on_stat_changed)
        abilities_layout.addRow("Spell:", self.spell_combo)

        self.dodge_spin = QSpinBox()
        self.dodge_spin.setRange(0, 15)
        self.dodge_spin.valueChanged.connect(self._on_stat_changed)
        abilities_layout.addRow("Dodge:", self.dodge_spin)

        abilities_group.setLayout(abilities_layout)
        layout.addWidget(abilities_group)

        # Resistances group
        resist_group = QGroupBox("Resistances")
        resist_layout = QVBoxLayout()

        self.resist_sleep_check = QCheckBox("Resist SLEEP")
        self.resist_sleep_check.stateChanged.connect(self._on_stat_changed)
        resist_layout.addWidget(self.resist_sleep_check)

        self.resist_stopspell_check = QCheckBox("Resist STOPSPELL")
        self.resist_stopspell_check.stateChanged.connect(self._on_stat_changed)
        resist_layout.addWidget(self.resist_stopspell_check)

        self.resist_hurt_check = QCheckBox("Resist HURT")
        self.resist_hurt_check.stateChanged.connect(self._on_stat_changed)
        resist_layout.addWidget(self.resist_hurt_check)

        resist_group.setLayout(resist_layout)
        layout.addWidget(resist_group)

        # Graphics group
        graphics_group = QGroupBox("Graphics")
        graphics_layout = QVBoxLayout()

        self.sprite_preview = QLabel()
        self.sprite_preview.setMinimumSize(64, 64)
        self.sprite_preview.setAlignment(Qt.AlignCenter)
        self.sprite_preview.setStyleSheet("QLabel { background-color: #000; }")
        graphics_layout.addWidget(self.sprite_preview)

        palette_layout = QHBoxLayout()
        palette_layout.addWidget(QLabel("Palette:"))
        self.palette_combo = QComboBox()
        self.palette_combo.addItems([f"Palette {i}" for i in range(8)])
        self.palette_combo.currentIndexChanged.connect(self._on_palette_changed)
        palette_layout.addWidget(self.palette_combo)
        graphics_layout.addLayout(palette_layout)

        graphics_group.setLayout(graphics_layout)
        layout.addWidget(graphics_group)

        # Stat calculator
        calc_group = QGroupBox("Stat Calculator")
        calc_layout = QVBoxLayout()

        self.stat_info = QTextEdit()
        self.stat_info.setReadOnly(True)
        self.stat_info.setMaximumHeight(150)
        calc_layout.addWidget(self.stat_info)

        calc_group.setLayout(calc_layout)
        layout.addWidget(calc_group)

        # Stretch
        layout.addStretch()

        # Apply button
        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self._apply_changes)
        layout.addWidget(apply_btn)

        widget.setLayout(layout)
        return widget

    def load_data(self, data_manager):
        """
        Load data from data manager

        Args:
            data_manager: DataManager instance
        """
        self.data_manager = data_manager
        self.refresh()

    def refresh(self):
        """Refresh table from data manager"""
        if not self.data_manager:
            return

        self.monster_table.setRowCount(len(self.data_manager.monsters))

        for i, monster in enumerate(self.data_manager.monsters):
            self.monster_table.setItem(i, 0, QTableWidgetItem(str(monster.id)))
            self.monster_table.setItem(i, 1, QTableWidgetItem(monster.name))
            self.monster_table.setItem(i, 2, QTableWidgetItem(str(monster.hp)))
            self.monster_table.setItem(i, 3, QTableWidgetItem(str(monster.attack)))
            self.monster_table.setItem(i, 4, QTableWidgetItem(str(monster.defense)))
            self.monster_table.setItem(i, 5, QTableWidgetItem(str(monster.xp)))
            self.monster_table.setItem(i, 6, QTableWidgetItem(str(monster.gold)))

    def save_data(self, data_manager):
        """
        Save data to data manager

        Args:
            data_manager: DataManager instance
        """
        # Data is already updated in _apply_changes
        pass

    def _on_monster_selected(self):
        """Handle monster selection"""
        selected = self.monster_table.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        if row < 0 or row >= len(self.data_manager.monsters):
            return

        monster = self.data_manager.monsters[row]
        self.current_monster_id = monster.id

        # Update detail editor
        self.name_label.setText(monster.name)
        self.id_label.setText(str(monster.id))

        self.hp_spin.setValue(monster.hp)
        self.mp_spin.setValue(monster.mp)
        self.attack_spin.setValue(monster.attack)
        self.defense_spin.setValue(monster.defense)
        self.agility_spin.setValue(monster.agility)

        self.xp_spin.setValue(monster.xp)
        self.gold_spin.setValue(monster.gold)

        self.spell_combo.setCurrentIndex(monster.spell_id)
        self.dodge_spin.setValue(monster.dodge)

        self.resist_sleep_check.setChecked(monster.resist_sleep)
        self.resist_stopspell_check.setChecked(monster.resist_stopspell)
        self.resist_hurt_check.setChecked(monster.resist_hurt)

        self.palette_combo.setCurrentIndex(monster.palette_index)

        # Update stat calculator
        self._update_stat_calculator()

        # Update sprite preview
        self._update_sprite_preview()

    def _on_stat_changed(self):
        """Handle stat change"""
        self._update_stat_calculator()

    def _on_palette_changed(self):
        """Handle palette change"""
        self._update_sprite_preview()

    def _update_stat_calculator(self):
        """Update stat calculator info"""
        if self.current_monster_id is None:
            return

        hp = self.hp_spin.value()
        attack = self.attack_spin.value()
        defense = self.defense_spin.value()
        xp = self.xp_spin.value()
        gold = self.gold_spin.value()

        # Calculate difficulty rating
        difficulty = (hp / 10) + attack + defense

        # Calculate reward efficiency
        reward = xp + (gold / 2)
        efficiency = reward / difficulty if difficulty > 0 else 0

        info = f"""Difficulty Rating: {difficulty:.1f}
(Based on HP, Attack, Defense)

Reward Value: {reward:.1f}
(XP + Gold/2)

Efficiency: {efficiency:.2f}
(Reward per Difficulty point)

Category: {self._get_difficulty_category(difficulty)}
        """

        self.stat_info.setText(info)

    def _get_difficulty_category(self, difficulty: float) -> str:
        """Get difficulty category"""
        if difficulty < 20:
            return "Very Easy (Early game)"
        elif difficulty < 40:
            return "Easy (Mid-early game)"
        elif difficulty < 80:
            return "Medium (Mid game)"
        elif difficulty < 150:
            return "Hard (Late game)"
        else:
            return "Very Hard (End game)"

    def _update_sprite_preview(self):
        """Update sprite preview"""
        # Placeholder - would load actual sprite graphics
        pixmap = QPixmap(64, 64)
        pixmap.fill(QColor(40, 40, 40))

        painter = QPainter(pixmap)

        # Draw placeholder sprite
        palette_index = self.palette_combo.currentIndex()
        colors = [
            QColor(255, 100, 100),  # Red
            QColor(100, 100, 255),  # Blue
            QColor(100, 255, 100),  # Green
            QColor(255, 255, 100),  # Yellow
            QColor(255, 100, 255),  # Magenta
            QColor(100, 255, 255),  # Cyan
            QColor(200, 200, 200),  # White
            QColor(150, 150, 150),  # Gray
        ]

        color = colors[palette_index]
        painter.setBrush(color)
        painter.drawEllipse(16, 16, 32, 32)
        painter.end()

        self.sprite_preview.setPixmap(pixmap)

    def _apply_changes(self):
        """Apply changes to current monster"""
        if self.current_monster_id is None:
            return

        monster = self.data_manager.monsters[self.current_monster_id]

        # Update monster
        monster.hp = self.hp_spin.value()
        monster.mp = self.mp_spin.value()
        monster.attack = self.attack_spin.value()
        monster.defense = self.defense_spin.value()
        monster.agility = self.agility_spin.value()

        monster.xp = self.xp_spin.value()
        monster.gold = self.gold_spin.value()

        monster.spell_id = self.spell_combo.currentIndex()
        monster.dodge = self.dodge_spin.value()

        monster.resist_sleep = self.resist_sleep_check.isChecked()
        monster.resist_stopspell = self.resist_stopspell_check.isChecked()
        monster.resist_hurt = self.resist_hurt_check.isChecked()

        monster.palette_index = self.palette_combo.currentIndex()

        # Refresh table
        self.refresh()

        # Mark as modified
        if self.parent_window:
            self.parent_window.mark_modified()

        self.data_modified.emit()

    def _add_monster(self):
        """Add new monster"""
        if not self.data_manager:
            return

        # TODO: Implement add monster
        QMessageBox.information(self, "Add Monster", "Add monster not yet implemented")

    def _delete_monster(self):
        """Delete selected monster"""
        if self.current_monster_id is None:
            return

        reply = QMessageBox.question(
            self,
            "Delete Monster",
            f"Delete monster {self.current_monster_id}?",
            QMessageBox.Yes | QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # TODO: Implement delete
            QMessageBox.information(self, "Delete", "Delete not yet implemented")

    def _clone_monster(self):
        """Clone selected monster"""
        if self.current_monster_id is None:
            return

        # TODO: Implement clone
        QMessageBox.information(self, "Clone", "Clone not yet implemented")
