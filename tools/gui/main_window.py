#!/usr/bin/env python3
"""
Dragon Warrior ROM Editor - Main Window

PyQt5-based GUI editor for Dragon Warrior data.

Features:
	- Monster editor with stats and sprites
	- Spell editor with effects
	- Item editor with prices
	- Map viewer
	- Text editor
	- Live ROM preview

Requirements:
	pip install PyQt5 Pillow

Author: Dragon Warrior ROM Hacking Toolkit
Version: 1.0
"""

import sys
import os
from pathlib import Path
from typing import Optional

try:
	from PyQt5.QtWidgets import (
		QApplication, QMainWindow, QTabWidget, QWidget,
		QVBoxLayout, QHBoxLayout, QMenuBar, QMenu, QAction,
		QFileDialog, QMessageBox, QStatusBar, QToolBar,
		QLabel, QProgressBar
	)
	from PyQt5.QtCore import Qt, QSettings, QTimer
	from PyQt5.QtGui import QIcon, QKeySequence
except ImportError:
	print("Error: PyQt5 not installed")
	print("Install with: pip install PyQt5")
	sys.exit(1)


# Import editor tabs (will be created next)
try:
	from .monster_editor_tab import MonsterEditorTab
	from .spell_editor_tab import SpellEditorTab
	from .item_editor_tab import ItemEditorTab
	from .data_manager import DataManager
except ImportError:
	# Fallback for standalone execution
	MonsterEditorTab = None
	SpellEditorTab = None
	ItemEditorTab = None
	DataManager = None


class DragonWarriorEditor(QMainWindow):
	"""
	Main editor window

	Manages tabs, menus, and data loading/saving.
	"""

	def __init__(self):
		"""Initialize main window"""
		super().__init__()

		# Window settings
		self.setWindowTitle("Dragon Warrior ROM Editor")
		self.setGeometry(100, 100, 1200, 800)

		# Data manager
		self.data_manager = None
		self.current_rom = None
		self.modified = False

		# Settings
		self.settings = QSettings("DWROMHacking", "DragonWarriorEditor")

		# UI setup
		self._create_menu_bar()
		self._create_tool_bar()
		self._create_status_bar()
		self._create_tabs()

		# Load last opened file
		self._restore_state()

		# Auto-save timer
		self.auto_save_timer = QTimer()
		self.auto_save_timer.timeout.connect(self._auto_save)
		self.auto_save_timer.start(60000)  # Every 60 seconds

	def _create_menu_bar(self):
		"""Create menu bar"""
		menubar = self.menuBar()

		# File menu
		file_menu = menubar.addMenu("&File")

		open_action = QAction("&Open ROM...", self)
		open_action.setShortcut(QKeySequence.Open)
		open_action.triggered.connect(self._open_rom)
		file_menu.addAction(open_action)

		save_action = QAction("&Save", self)
		save_action.setShortcut(QKeySequence.Save)
		save_action.triggered.connect(self._save_rom)
		file_menu.addAction(save_action)

		save_as_action = QAction("Save &As...", self)
		save_as_action.setShortcut(QKeySequence.SaveAs)
		save_as_action.triggered.connect(self._save_rom_as)
		file_menu.addAction(save_as_action)

		file_menu.addSeparator()

		export_action = QAction("&Export Data...", self)
		export_action.triggered.connect(self._export_data)
		file_menu.addAction(export_action)

		import_action = QAction("&Import Data...", self)
		import_action.triggered.connect(self._import_data)
		file_menu.addAction(import_action)

		file_menu.addSeparator()

		exit_action = QAction("E&xit", self)
		exit_action.setShortcut(QKeySequence.Quit)
		exit_action.triggered.connect(self.close)
		file_menu.addAction(exit_action)

		# Edit menu
		edit_menu = menubar.addMenu("&Edit")

		undo_action = QAction("&Undo", self)
		undo_action.setShortcut(QKeySequence.Undo)
		undo_action.triggered.connect(self._undo)
		edit_menu.addAction(undo_action)

		redo_action = QAction("&Redo", self)
		redo_action.setShortcut(QKeySequence.Redo)
		redo_action.triggered.connect(self._redo)
		edit_menu.addAction(redo_action)

		edit_menu.addSeparator()

		find_action = QAction("&Find...", self)
		find_action.setShortcut(QKeySequence.Find)
		find_action.triggered.connect(self._find)
		edit_menu.addAction(find_action)

		# Tools menu
		tools_menu = menubar.addMenu("&Tools")

		validate_action = QAction("&Validate Data", self)
		validate_action.triggered.connect(self._validate_data)
		tools_menu.addAction(validate_action)

		analyze_action = QAction("&Analyze ROM", self)
		analyze_action.triggered.connect(self._analyze_rom)
		tools_menu.addAction(analyze_action)

		tools_menu.addSeparator()

		preferences_action = QAction("&Preferences...", self)
		preferences_action.triggered.connect(self._show_preferences)
		tools_menu.addAction(preferences_action)

		# View menu
		view_menu = menubar.addMenu("&View")

		refresh_action = QAction("&Refresh", self)
		refresh_action.setShortcut(QKeySequence.Refresh)
		refresh_action.triggered.connect(self._refresh)
		view_menu.addAction(refresh_action)

		# Help menu
		help_menu = menubar.addMenu("&Help")

		docs_action = QAction("&Documentation", self)
		docs_action.setShortcut(QKeySequence.HelpContents)
		docs_action.triggered.connect(self._show_docs)
		help_menu.addAction(docs_action)

		about_action = QAction("&About", self)
		about_action.triggered.connect(self._show_about)
		help_menu.addAction(about_action)

	def _create_tool_bar(self):
		"""Create toolbar"""
		toolbar = QToolBar("Main Toolbar")
		self.addToolBar(toolbar)

		# Open
		open_action = QAction("Open", self)
		open_action.triggered.connect(self._open_rom)
		toolbar.addAction(open_action)

		# Save
		save_action = QAction("Save", self)
		save_action.triggered.connect(self._save_rom)
		toolbar.addAction(save_action)

		toolbar.addSeparator()

		# Validate
		validate_action = QAction("Validate", self)
		validate_action.triggered.connect(self._validate_data)
		toolbar.addAction(validate_action)

	def _create_status_bar(self):
		"""Create status bar"""
		self.status_bar = QStatusBar()
		self.setStatusBar(self.status_bar)

		# ROM info label
		self.rom_info_label = QLabel("No ROM loaded")
		self.status_bar.addWidget(self.rom_info_label)

		# Modified indicator
		self.modified_label = QLabel("")
		self.status_bar.addPermanentWidget(self.modified_label)

		# Progress bar (hidden by default)
		self.progress_bar = QProgressBar()
		self.progress_bar.setVisible(False)
		self.status_bar.addPermanentWidget(self.progress_bar)

	def _create_tabs(self):
		"""Create tab widget"""
		self.tabs = QTabWidget()
		self.setCentralWidget(self.tabs)

		# Check if tab classes are available
		if MonsterEditorTab:
			self.monster_tab = MonsterEditorTab(self)
			self.tabs.addTab(self.monster_tab, "Monsters")

		if SpellEditorTab:
			self.spell_tab = SpellEditorTab(self)
			self.tabs.addTab(self.spell_tab, "Spells")

		if ItemEditorTab:
			self.item_tab = ItemEditorTab(self)
			self.tabs.addTab(self.item_tab, "Items")

		# Placeholder tabs if imports failed
		if not MonsterEditorTab:
			placeholder = QWidget()
			layout = QVBoxLayout()
			label = QLabel("Monster editor tab not available\nImplement monster_editor_tab.py")
			label.setAlignment(Qt.AlignCenter)
			layout.addWidget(label)
			placeholder.setLayout(layout)
			self.tabs.addTab(placeholder, "Monsters")

	def _restore_state(self):
		"""Restore window state from settings"""
		# Window geometry
		geometry = self.settings.value("geometry")
		if geometry:
			self.restoreGeometry(geometry)

		# Last opened file
		last_rom = self.settings.value("last_rom")
		if last_rom and os.path.exists(last_rom):
			self._load_rom(last_rom)

	def _save_state(self):
		"""Save window state to settings"""
		self.settings.setValue("geometry", self.saveGeometry())
		if self.current_rom:
			self.settings.setValue("last_rom", self.current_rom)

	def _open_rom(self):
		"""Open ROM file dialog"""
		file_path, _ = QFileDialog.getOpenFileName(
			self,
			"Open Dragon Warrior ROM",
			"",
			"NES ROMs (*.nes);;All Files (*.*)"
		)

		if file_path:
			self._load_rom(file_path)

	def _load_rom(self, file_path: str):
		"""
		Load ROM file

		Args:
			file_path: Path to ROM file
		"""
		try:
			self.progress_bar.setVisible(True)
			self.progress_bar.setValue(0)

			# Create data manager if needed
			if DataManager:
				self.data_manager = DataManager(file_path)
				self.progress_bar.setValue(50)

				# Load data into tabs
				if hasattr(self, 'monster_tab'):
					self.monster_tab.load_data(self.data_manager)
				if hasattr(self, 'spell_tab'):
					self.spell_tab.load_data(self.data_manager)
				if hasattr(self, 'item_tab'):
					self.item_tab.load_data(self.data_manager)

				self.progress_bar.setValue(100)

			self.current_rom = file_path
			self.modified = False
			self._update_ui()

			self.status_bar.showMessage(f"Loaded: {os.path.basename(file_path)}", 5000)

		except Exception as e:
			QMessageBox.critical(
				self,
				"Error",
				f"Failed to load ROM:\n{str(e)}"
			)
		finally:
			self.progress_bar.setVisible(False)

	def _save_rom(self):
		"""Save ROM"""
		if not self.current_rom:
			self._save_rom_as()
			return

		self._save_rom_to(self.current_rom)

	def _save_rom_as(self):
		"""Save ROM as dialog"""
		file_path, _ = QFileDialog.getSaveFileName(
			self,
			"Save Dragon Warrior ROM",
			"",
			"NES ROMs (*.nes);;All Files (*.*)"
		)

		if file_path:
			self._save_rom_to(file_path)

	def _save_rom_to(self, file_path: str):
		"""
		Save ROM to file

		Args:
			file_path: Output path
		"""
		try:
			self.progress_bar.setVisible(True)
			self.progress_bar.setValue(0)

			if self.data_manager:
				# Collect data from tabs
				if hasattr(self, 'monster_tab'):
					self.monster_tab.save_data(self.data_manager)
				self.progress_bar.setValue(33)

				if hasattr(self, 'spell_tab'):
					self.spell_tab.save_data(self.data_manager)
				self.progress_bar.setValue(66)

				if hasattr(self, 'item_tab'):
					self.item_tab.save_data(self.data_manager)
				self.progress_bar.setValue(80)

				# Save ROM
				self.data_manager.save(file_path)
				self.progress_bar.setValue(100)

			self.current_rom = file_path
			self.modified = False
			self._update_ui()

			self.status_bar.showMessage(f"Saved: {os.path.basename(file_path)}", 5000)

		except Exception as e:
			QMessageBox.critical(
				self,
				"Error",
				f"Failed to save ROM:\n{str(e)}"
			)
		finally:
			self.progress_bar.setVisible(False)

	def _export_data(self):
		"""Export data to JSON"""
		file_path, _ = QFileDialog.getSaveFileName(
			self,
			"Export Data",
			"",
			"JSON Files (*.json);;All Files (*.*)"
		)

		if file_path and self.data_manager:
			try:
				self.data_manager.export_json(file_path)
				self.status_bar.showMessage(f"Exported: {os.path.basename(file_path)}", 5000)
			except Exception as e:
				QMessageBox.critical(self, "Error", f"Export failed:\n{str(e)}")

	def _import_data(self):
		"""Import data from JSON"""
		file_path, _ = QFileDialog.getOpenFileName(
			self,
			"Import Data",
			"",
			"JSON Files (*.json);;All Files (*.*)"
		)

		if file_path and self.data_manager:
			try:
				self.data_manager.import_json(file_path)
				self._refresh()
				self.modified = True
				self._update_ui()
				self.status_bar.showMessage(f"Imported: {os.path.basename(file_path)}", 5000)
			except Exception as e:
				QMessageBox.critical(self, "Error", f"Import failed:\n{str(e)}")

	def _validate_data(self):
		"""Validate current data"""
		if not self.data_manager:
			QMessageBox.warning(self, "Warning", "No ROM loaded")
			return

		errors = self.data_manager.validate()

		if errors:
			msg = "Validation errors:\n\n" + "\n".join(f"• {e}" for e in errors[:20])
			if len(errors) > 20:
				msg += f"\n\n... and {len(errors) - 20} more errors"
			QMessageBox.warning(self, "Validation Errors", msg)
		else:
			QMessageBox.information(self, "Validation", "✓ All data is valid!")

	def _analyze_rom(self):
		"""Show ROM analysis"""
		if not self.data_manager:
			QMessageBox.warning(self, "Warning", "No ROM loaded")
			return

		stats = self.data_manager.analyze()

		msg = f"""ROM Analysis:

Size: {stats.get('size', 0):,} bytes
Monsters: {stats.get('monsters', 0)}
Spells: {stats.get('spells', 0)}
Items: {stats.get('items', 0)}

Unused space: {stats.get('unused', 0)} bytes
		"""

		QMessageBox.information(self, "ROM Analysis", msg)

	def _undo(self):
		"""Undo last action"""
		if self.data_manager:
			self.data_manager.undo()
			self._refresh()

	def _redo(self):
		"""Redo last undone action"""
		if self.data_manager:
			self.data_manager.redo()
			self._refresh()

	def _find(self):
		"""Show find dialog"""
		# TODO: Implement find dialog
		pass

	def _refresh(self):
		"""Refresh all tabs"""
		if hasattr(self, 'monster_tab'):
			self.monster_tab.refresh()
		if hasattr(self, 'spell_tab'):
			self.spell_tab.refresh()
		if hasattr(self, 'item_tab'):
			self.item_tab.refresh()

	def _show_preferences(self):
		"""Show preferences dialog"""
		# TODO: Implement preferences
		pass

	def _show_docs(self):
		"""Show documentation"""
		QMessageBox.information(
			self,
			"Documentation",
			"See docs/ directory for comprehensive documentation:\n\n"
			"• BINARY_PIPELINE_TUTORIAL.md\n"
			"• TROUBLESHOOTING.md\n"
			"• OPTIMIZATION_TECHNIQUES.md"
		)

	def _show_about(self):
		"""Show about dialog"""
		QMessageBox.about(
			self,
			"About Dragon Warrior ROM Editor",
			"Dragon Warrior ROM Editor v1.0\n\n"
			"A comprehensive editor for Dragon Warrior (NES) ROM hacks.\n\n"
			"Features:\n"
			"• Monster, spell, and item editing\n"
			"• Map viewer and editor\n"
			"• Text editing with compression\n"
			"• Live preview and validation\n\n"
			"Part of the Dragon Warrior ROM Hacking Toolkit"
		)

	def _auto_save(self):
		"""Auto-save current work"""
		if self.modified and self.current_rom and self.data_manager:
			backup_path = self.current_rom + ".autosave"
			try:
				self.data_manager.save(backup_path)
				print(f"Auto-saved to {backup_path}")
			except Exception as e:
				print(f"Auto-save failed: {e}")

	def _update_ui(self):
		"""Update UI state"""
		if self.current_rom:
			rom_name = os.path.basename(self.current_rom)
			self.rom_info_label.setText(f"ROM: {rom_name}")

			if self.modified:
				self.modified_label.setText("Modified")
				self.setWindowTitle(f"Dragon Warrior ROM Editor - {rom_name} *")
			else:
				self.modified_label.setText("")
				self.setWindowTitle(f"Dragon Warrior ROM Editor - {rom_name}")
		else:
			self.rom_info_label.setText("No ROM loaded")
			self.modified_label.setText("")
			self.setWindowTitle("Dragon Warrior ROM Editor")

	def mark_modified(self):
		"""Mark data as modified"""
		self.modified = True
		self._update_ui()

	def closeEvent(self, event):
		"""Handle window close"""
		if self.modified:
			reply = QMessageBox.question(
				self,
				"Unsaved Changes",
				"You have unsaved changes. Save before closing?",
				QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel
			)

			if reply == QMessageBox.Save:
				self._save_rom()
				self._save_state()
				event.accept()
			elif reply == QMessageBox.Discard:
				self._save_state()
				event.accept()
			else:
				event.ignore()
		else:
			self._save_state()
			event.accept()


def main():
	"""Main entry point"""
	app = QApplication(sys.argv)
	app.setApplicationName("Dragon Warrior ROM Editor")
	app.setOrganizationName("DWROMHacking")

	window = DragonWarriorEditor()
	window.show()

	sys.exit(app.exec_())


if __name__ == '__main__':
	main()
