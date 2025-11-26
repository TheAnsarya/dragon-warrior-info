#!/usr/bin/env python3
"""
Spell Editor Tab

PyQt5 tab for editing spell data.

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QSpinBox, QComboBox, QGroupBox,
    QFormLayout, QTextEdit, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal


class SpellEditorTab(QWidget):
    """Spell editor tab"""

    data_modified = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize spell editor"""
        super().__init__(parent)

        self.parent_window = parent
        self.data_manager = None
        self.current_spell_id = None

        self._create_ui()

    def _create_ui(self):
        """Create UI"""
        layout = QVBoxLayout()

        # Table
        self.spell_table = QTableWidget()
        self.spell_table.setColumnCount(5)
        self.spell_table.setHorizontalHeaderLabels([
            "ID", "Name", "MP Cost", "Effect", "Power"
        ])

        header = self.spell_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.spell_table.itemSelectionChanged.connect(self._on_spell_selected)
        layout.addWidget(self.spell_table)

        # Detail editor
        detail_group = QGroupBox("Spell Details")
        detail_layout = QFormLayout()

        self.name_label = QLabel("(No spell selected)")
        detail_layout.addRow("Name:", self.name_label)

        self.mp_cost_spin = QSpinBox()
        self.mp_cost_spin.setRange(0, 255)
        detail_layout.addRow("MP Cost:", self.mp_cost_spin)

        self.effect_combo = QComboBox()
        self.effect_combo.addItems([
            "heal", "damage", "sleep", "light", "silence",
            "escape", "return", "repel"
        ])
        detail_layout.addRow("Effect:", self.effect_combo)

        self.power_spin = QSpinBox()
        self.power_spin.setRange(0, 255)
        detail_layout.addRow("Power:", self.power_spin)

        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)

        # Description
        desc_group = QGroupBox("Description")
        desc_layout = QVBoxLayout()

        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        desc_layout.addWidget(self.description_edit)

        desc_group.setLayout(desc_layout)
        layout.addWidget(desc_group)

        # Apply button
        apply_btn = QPushButton("Apply Changes")
        apply_btn.clicked.connect(self._apply_changes)
        layout.addWidget(apply_btn)

        self.setLayout(layout)

    def load_data(self, data_manager):
        """Load data"""
        self.data_manager = data_manager
        self.refresh()

    def refresh(self):
        """Refresh table"""
        if not self.data_manager:
            return

        self.spell_table.setRowCount(len(self.data_manager.spells))

        for i, spell in enumerate(self.data_manager.spells):
            self.spell_table.setItem(i, 0, QTableWidgetItem(str(spell.id)))
            self.spell_table.setItem(i, 1, QTableWidgetItem(spell.name))
            self.spell_table.setItem(i, 2, QTableWidgetItem(str(spell.mp_cost)))
            self.spell_table.setItem(i, 3, QTableWidgetItem(spell.effect))
            self.spell_table.setItem(i, 4, QTableWidgetItem(str(spell.power)))

    def save_data(self, data_manager):
        """Save data"""
        pass

    def _on_spell_selected(self):
        """Handle selection"""
        selected = self.spell_table.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        spell = self.data_manager.spells[row]
        self.current_spell_id = spell.id

        self.name_label.setText(spell.name)
        self.mp_cost_spin.setValue(spell.mp_cost)
        self.power_spin.setValue(spell.power)
        self.description_edit.setText(spell.description)

    def _apply_changes(self):
        """Apply changes"""
        if self.current_spell_id is None:
            return

        spell = self.data_manager.spells[self.current_spell_id]
        spell.mp_cost = self.mp_cost_spin.value()
        spell.power = self.power_spin.value()
        spell.description = self.description_edit.toPlainText()

        self.refresh()

        if self.parent_window:
            self.parent_window.mark_modified()

        self.data_modified.emit()
