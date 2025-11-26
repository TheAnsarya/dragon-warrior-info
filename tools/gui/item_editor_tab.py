#!/usr/bin/env python3
"""
Item Editor Tab

PyQt5 tab for editing item data with price calculator.

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QLabel, QSpinBox, QComboBox, QGroupBox,
    QFormLayout, QTextEdit, QHeaderView, QLineEdit
)
from PyQt5.QtCore import Qt, pyqtSignal


class ItemEditorTab(QWidget):
    """Item editor tab with price calculator"""

    data_modified = pyqtSignal()

    def __init__(self, parent=None):
        """Initialize item editor"""
        super().__init__(parent)

        self.parent_window = parent
        self.data_manager = None
        self.current_item_id = None

        self._create_ui()

    def _create_ui(self):
        """Create UI"""
        layout = QVBoxLayout()

        # Table
        self.item_table = QTableWidget()
        self.item_table.setColumnCount(6)
        self.item_table.setHorizontalHeaderLabels([
            "ID", "Name", "Type", "Price", "Attack", "Defense"
        ])

        header = self.item_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.Stretch)

        self.item_table.itemSelectionChanged.connect(self._on_item_selected)
        layout.addWidget(self.item_table)

        # Detail editor
        detail_group = QGroupBox("Item Details")
        detail_layout = QFormLayout()

        self.name_label = QLabel("(No item selected)")
        detail_layout.addRow("Name:", self.name_label)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["weapon", "armor", "shield", "tool", "key"])
        detail_layout.addRow("Type:", self.type_combo)

        self.price_spin = QSpinBox()
        self.price_spin.setRange(0, 65535)
        self.price_spin.valueChanged.connect(self._update_price_calc)
        detail_layout.addRow("Price:", self.price_spin)

        self.sell_price_label = QLabel("0")
        detail_layout.addRow("Sell Price:", self.sell_price_label)

        self.attack_spin = QSpinBox()
        self.attack_spin.setRange(0, 255)
        detail_layout.addRow("Attack:", self.attack_spin)

        self.defense_spin = QSpinBox()
        self.defense_spin.setRange(0, 255)
        detail_layout.addRow("Defense:", self.defense_spin)

        detail_group.setLayout(detail_layout)
        layout.addWidget(detail_group)

        # Price calculator
        calc_group = QGroupBox("Price Calculator")
        calc_layout = QVBoxLayout()

        self.price_info = QTextEdit()
        self.price_info.setReadOnly(True)
        self.price_info.setMaximumHeight(80)
        calc_layout.addWidget(self.price_info)

        calc_group.setLayout(calc_layout)
        layout.addWidget(calc_group)

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

        self.item_table.setRowCount(len(self.data_manager.items))

        for i, item in enumerate(self.data_manager.items):
            self.item_table.setItem(i, 0, QTableWidgetItem(str(item.id)))
            self.item_table.setItem(i, 1, QTableWidgetItem(item.name))
            self.item_table.setItem(i, 2, QTableWidgetItem(item.type))
            self.item_table.setItem(i, 3, QTableWidgetItem(str(item.price)))
            self.item_table.setItem(i, 4, QTableWidgetItem(str(item.attack)))
            self.item_table.setItem(i, 5, QTableWidgetItem(str(item.defense)))

    def save_data(self, data_manager):
        """Save data"""
        pass

    def _on_item_selected(self):
        """Handle selection"""
        selected = self.item_table.selectedItems()
        if not selected:
            return

        row = selected[0].row()
        item = self.data_manager.items[row]
        self.current_item_id = item.id

        self.name_label.setText(item.name)
        self.price_spin.setValue(item.price)
        self.attack_spin.setValue(item.attack)
        self.defense_spin.setValue(item.defense)

        self._update_price_calc()

    def _update_price_calc(self):
        """Update price calculator"""
        price = self.price_spin.value()
        sell_price = price // 2

        self.sell_price_label.setText(str(sell_price))

        info = f"""Buy: {price} gold
Sell: {sell_price} gold
Net loss: {price - sell_price} gold
        """

        self.price_info.setText(info)

    def _apply_changes(self):
        """Apply changes"""
        if self.current_item_id is None:
            return

        item = self.data_manager.items[self.current_item_id]
        item.price = self.price_spin.value()
        item.sell_price = item.price // 2
        item.attack = self.attack_spin.value()
        item.defense = self.defense_spin.value()

        self.refresh()

        if self.parent_window:
            self.parent_window.mark_modified()

        self.data_modified.emit()
