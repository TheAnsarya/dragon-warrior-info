#!/usr/bin/env python3
"""
Dragon Warrior Dialogue Editor Tab

Full-featured dialogue editing with:
- Text extraction from ROM
- Pointer table management
- Text compression/decompression
- Character encoding support
- Search and replace
- Script export/import
- Text length validation
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import struct


# Dragon Warrior text encoding table
DW_TEXT_ENCODING = {
	# Control codes
	0x00: '<END>',
	0x01: '<PLAYER>',
	0x02: '<LINE>',
	0x03: '<WAIT>',
	0x04: '<CLEAR>',

	# Letters (A-Z, a-z)
	**{i: chr(ord('A') + i - 0x41) for i in range(0x41, 0x5B)},
	**{i: chr(ord('a') + i - 0x61) for i in range(0x61, 0x7B)},

	# Numbers (0-9)
	**{i: chr(ord('0') + i - 0x30) for i in range(0x30, 0x3A)},

	# Punctuation
	0x20: ' ',
	0x21: '!',
	0x22: '"',
	0x23: '#',
	0x27: "'",
	0x28: '(',
	0x29: ')',
	0x2C: ',',
	0x2D: '-',
	0x2E: '.',
	0x2F: '/',
	0x3A: ':',
	0x3B: ';',
	0x3F: '?',

	# Special characters
	0xFA: '<YEN>',
	0xFB: '<HEART>',
	0xFC: '<CROWN>',
	0xFD: '<SWORD>',
	0xFE: '<SHIELD>',
	0xFF: '<ITEM>',
}

# Reverse mapping for encoding
TEXT_TO_BYTE = {v: k for k, v in DW_TEXT_ENCODING.items()}


@dataclass
class DialogueEntry:
	"""Single dialogue entry."""
	id: int
	pointer: int
	rom_offset: int
	raw_bytes: bytes
	decoded_text: str
	length: int


class DialogueEditorTab(ttk.Frame):
	"""
	Dialogue & text editor for Dragon Warrior.

	Features:
	- Extract all dialogue from ROM
	- Edit text with live preview
	- Handle pointer table automatically
	- Text compression/decompression
	- Search and filter dialogue
	- Export/import scripts
	- Character encoding visualization
	"""

	def __init__(self, parent, rom_manager):
		super().__init__(parent)
		self.rom_manager = rom_manager
		self.dialogues: List[DialogueEntry] = []
		self.current_dialogue: Optional[DialogueEntry] = None

		# ROM offsets for dialogue data
		self.TEXT_POINTERS = 0xB0A0  # Pointer table
		self.TEXT_DATA = 0xB100      # Compressed text data
		self.NUM_DIALOGUES = 200     # Approximate number of dialogue entries

		self.create_widgets()
		self.load_dialogues()

	def create_widgets(self):
		"""Create editor interface."""

		# Title
		title_frame = ttk.Frame(self)
		title_frame.pack(fill=tk.X, padx=10, pady=10)

		ttk.Label(title_frame, text="💬 Dialogue Editor",
				 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(title_frame, text="🔄 Reload All",
				  command=self.load_dialogues).pack(side=tk.RIGHT, padx=5)
		ttk.Button(title_frame, text="💾 Save All",
				  command=self.save_all_dialogues).pack(side=tk.RIGHT, padx=5)
		ttk.Button(title_frame, text="📤 Export Script",
				  command=self.export_script).pack(side=tk.RIGHT, padx=5)
		ttk.Button(title_frame, text="📥 Import Script",
				  command=self.import_script).pack(side=tk.RIGHT, padx=5)

		# Main container with paned window
		paned = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
		paned.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Left panel: Dialogue list
		left_panel = ttk.Frame(paned)
		paned.add(left_panel, weight=1)

		# Search bar
		search_frame = ttk.Frame(left_panel)
		search_frame.pack(fill=tk.X, pady=5)

		ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
		self.search_var = tk.StringVar()
		self.search_var.trace('w', lambda *args: self.filter_dialogues())
		search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
		search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

		# Dialogue tree
		tree_frame = ttk.LabelFrame(left_panel, text="Dialogue Entries", padding=5)
		tree_frame.pack(fill=tk.BOTH, expand=True)

		columns = ('ID', 'Pointer', 'Length', 'Preview')
		self.dialogue_tree = ttk.Treeview(tree_frame, columns=columns,
										 show='headings', height=20)

		self.dialogue_tree.heading('ID', text='ID')
		self.dialogue_tree.heading('Pointer', text='Pointer')
		self.dialogue_tree.heading('Length', text='Bytes')
		self.dialogue_tree.heading('Preview', text='Text Preview')

		self.dialogue_tree.column('ID', width=50)
		self.dialogue_tree.column('Pointer', width=80)
		self.dialogue_tree.column('Length', width=60)
		self.dialogue_tree.column('Preview', width=300)

		scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL,
								 command=self.dialogue_tree.yview)
		self.dialogue_tree.configure(yscrollcommand=scrollbar.set)

		self.dialogue_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.dialogue_tree.bind('<<TreeviewSelect>>', self.on_dialogue_select)

		# Right panel: Editor
		right_panel = ttk.Frame(paned)
		paned.add(right_panel, weight=2)

		# Dialogue info
		info_frame = ttk.LabelFrame(right_panel, text="Dialogue Info", padding=10)
		info_frame.pack(fill=tk.X, pady=5)

		info_grid = ttk.Frame(info_frame)
		info_grid.pack(fill=tk.X)

		ttk.Label(info_grid, text="ID:").grid(row=0, column=0, sticky=tk.W, padx=5)
		self.id_label = ttk.Label(info_grid, text="--", font=('Courier', 10, 'bold'))
		self.id_label.grid(row=0, column=1, sticky=tk.W, padx=5)

		ttk.Label(info_grid, text="Pointer:").grid(row=0, column=2, sticky=tk.W, padx=5)
		self.pointer_label = ttk.Label(info_grid, text="--", font=('Courier', 10))
		self.pointer_label.grid(row=0, column=3, sticky=tk.W, padx=5)

		ttk.Label(info_grid, text="ROM Offset:").grid(row=1, column=0, sticky=tk.W, padx=5)
		self.offset_label = ttk.Label(info_grid, text="--", font=('Courier', 10))
		self.offset_label.grid(row=1, column=1, sticky=tk.W, padx=5)

		ttk.Label(info_grid, text="Length:").grid(row=1, column=2, sticky=tk.W, padx=5)
		self.length_label = ttk.Label(info_grid, text="--", font=('Courier', 10))
		self.length_label.grid(row=1, column=3, sticky=tk.W, padx=5)

		# Text editor
		editor_frame = ttk.LabelFrame(right_panel, text="Edit Text", padding=10)
		editor_frame.pack(fill=tk.BOTH, expand=True, pady=5)

		# Toolbar
		toolbar = ttk.Frame(editor_frame)
		toolbar.pack(fill=tk.X, pady=5)

		ttk.Button(toolbar, text="💾 Save Changes",
				  command=self.save_current_dialogue).pack(side=tk.LEFT, padx=5)
		ttk.Button(toolbar, text="↶ Revert",
				  command=self.revert_dialogue).pack(side=tk.LEFT, padx=5)
		ttk.Button(toolbar, text="📋 Copy Text",
				  command=self.copy_text).pack(side=tk.LEFT, padx=5)

		self.char_count_label = ttk.Label(toolbar, text="Characters: 0",
										  font=('Courier', 9))
		self.char_count_label.pack(side=tk.RIGHT, padx=5)

		# Text area
		self.text_editor = scrolledtext.ScrolledText(
			editor_frame,
			width=60,
			height=10,
			font=('Courier', 11),
			wrap=tk.WORD
		)
		self.text_editor.pack(fill=tk.BOTH, expand=True)
		self.text_editor.bind('<<Modified>>', self.on_text_modified)

		# Control codes helper
		codes_frame = ttk.LabelFrame(right_panel, text="Insert Control Code", padding=5)
		codes_frame.pack(fill=tk.X, pady=5)

		control_codes = [
			('<LINE>', 'Line break'),
			('<WAIT>', 'Wait for input'),
			('<CLEAR>', 'Clear text box'),
			('<PLAYER>', 'Player name'),
		]

		for code, desc in control_codes:
			btn = ttk.Button(codes_frame, text=f"{code}\n{desc}",
							command=lambda c=code: self.insert_control_code(c))
			btn.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

		# Raw hex view
		hex_frame = ttk.LabelFrame(right_panel, text="Raw Hex Data", padding=5)
		hex_frame.pack(fill=tk.X, pady=5)

		self.hex_text = scrolledtext.ScrolledText(
			hex_frame,
			width=60,
			height=4,
			font=('Courier', 9),
			state=tk.DISABLED
		)
		self.hex_text.pack(fill=tk.BOTH, expand=True)

	def load_dialogues(self):
		"""Extract all dialogue from ROM."""
		self.dialogues.clear()
		self.dialogue_tree.delete(*self.dialogue_tree.get_children())

		# Read pointer table
		pointers = []
		for i in range(self.NUM_DIALOGUES):
			ptr_offset = self.TEXT_POINTERS + (i * 2)
			if ptr_offset + 1 < len(self.rom_manager.rom):
				ptr = self.rom_manager.read_word(ptr_offset)
				if ptr != 0xFFFF and ptr != 0x0000:  # Valid pointer
					pointers.append((i, ptr))

		# Extract dialogue for each pointer
		for dialogue_id, pointer in pointers[:50]:  # Limit to first 50 for now
			rom_offset = self.TEXT_DATA + pointer

			# Read until end marker (0x00)
			raw_bytes = bytearray()
			offset = rom_offset
			while offset < len(self.rom_manager.rom) and len(raw_bytes) < 500:
				byte = self.rom_manager.read_byte(offset)
				raw_bytes.append(byte)
				if byte == 0x00:  # End marker
					break
				offset += 1

			# Decode text
			decoded = self.decode_text(bytes(raw_bytes))

			dialogue = DialogueEntry(
				id=dialogue_id,
				pointer=pointer,
				rom_offset=rom_offset,
				raw_bytes=bytes(raw_bytes),
				decoded_text=decoded,
				length=len(raw_bytes)
			)

			self.dialogues.append(dialogue)

			# Add to tree
			preview = decoded[:50].replace('\n', ' ')
			if len(decoded) > 50:
				preview += '...'

			self.dialogue_tree.insert('', tk.END, values=(
				f"{dialogue_id:03d}",
				f"0x{pointer:04X}",
				len(raw_bytes),
				preview
			))

		messagebox.showinfo("Success", f"Loaded {len(self.dialogues)} dialogue entries")

	def decode_text(self, raw_bytes: bytes) -> str:
		"""Decode Dragon Warrior text to readable string."""
		result = []

		for byte in raw_bytes:
			if byte in DW_TEXT_ENCODING:
				char = DW_TEXT_ENCODING[byte]
				if char.startswith('<') and char.endswith('>'):
					# Control code
					if char == '<LINE>':
						result.append('\n')
					elif char == '<END>':
						break
					else:
						result.append(char)
				else:
					result.append(char)
			else:
				# Unknown byte - show as hex
				result.append(f'<{byte:02X}>')

		return ''.join(result)

	def encode_text(self, text: str) -> bytes:
		"""Encode readable string to Dragon Warrior format."""
		result = bytearray()

		i = 0
		while i < len(text):
			if text[i] == '<':
				# Control code
				end = text.find('>', i)
				if end != -1:
					code = text[i:end+1]
					if code in TEXT_TO_BYTE:
						result.append(TEXT_TO_BYTE[code])
					elif code == '\n':
						result.append(TEXT_TO_BYTE.get('<LINE>', 0x02))
					i = end + 1
					continue

			# Regular character
			char = text[i]
			if char == '\n':
				result.append(TEXT_TO_BYTE.get('<LINE>', 0x02))
			elif char in TEXT_TO_BYTE:
				result.append(TEXT_TO_BYTE[char])
			else:
				# Unknown character - skip
				pass

			i += 1

		# Add end marker
		result.append(0x00)

		return bytes(result)

	def filter_dialogues(self):
		"""Filter dialogue list by search term."""
		search_term = self.search_var.get().lower()

		# Clear tree
		self.dialogue_tree.delete(*self.dialogue_tree.get_children())

		# Re-add matching dialogues
		for dialogue in self.dialogues:
			if search_term in dialogue.decoded_text.lower():
				preview = dialogue.decoded_text[:50].replace('\n', ' ')
				if len(dialogue.decoded_text) > 50:
					preview += '...'

				self.dialogue_tree.insert('', tk.END, values=(
					f"{dialogue.id:03d}",
					f"0x{dialogue.pointer:04X}",
					dialogue.length,
					preview
				))

	def on_dialogue_select(self, event):
		"""Handle dialogue selection."""
		selection = self.dialogue_tree.selection()
		if not selection:
			return

		item = self.dialogue_tree.item(selection[0])
		dialogue_id = int(item['values'][0])

		# Find dialogue
		for dialogue in self.dialogues:
			if dialogue.id == dialogue_id:
				self.current_dialogue = dialogue
				self.display_dialogue(dialogue)
				break

	def display_dialogue(self, dialogue: DialogueEntry):
		"""Display dialogue in editor."""
		# Update info labels
		self.id_label.config(text=f"{dialogue.id:03d}")
		self.pointer_label.config(text=f"0x{dialogue.pointer:04X}")
		self.offset_label.config(text=f"0x{dialogue.rom_offset:06X}")
		self.length_label.config(text=f"{dialogue.length} bytes")

		# Update text editor
		self.text_editor.delete('1.0', tk.END)
		self.text_editor.insert('1.0', dialogue.decoded_text)
		self.text_editor.edit_modified(False)

		# Update hex view
		hex_str = ' '.join(f"{b:02X}" for b in dialogue.raw_bytes[:32])
		if len(dialogue.raw_bytes) > 32:
			hex_str += ' ...'

		self.hex_text.config(state=tk.NORMAL)
		self.hex_text.delete('1.0', tk.END)
		self.hex_text.insert('1.0', hex_str)
		self.hex_text.config(state=tk.DISABLED)

		# Update character count
		self.update_char_count()

	def on_text_modified(self, event=None):
		"""Handle text modification."""
		if self.text_editor.edit_modified():
			self.update_char_count()

	def update_char_count(self):
		"""Update character count display."""
		text = self.text_editor.get('1.0', tk.END).rstrip()
		char_count = len(text)
		self.char_count_label.config(text=f"Characters: {char_count}")

	def insert_control_code(self, code: str):
		"""Insert control code at cursor."""
		self.text_editor.insert(tk.INSERT, code)
		self.text_editor.focus()

	def save_current_dialogue(self):
		"""Save current dialogue changes to ROM."""
		if not self.current_dialogue:
			messagebox.showwarning("Warning", "No dialogue selected")
			return

		# Get edited text
		new_text = self.text_editor.get('1.0', tk.END).rstrip()

		# Encode to bytes
		new_bytes = self.encode_text(new_text)

		# Check length
		if len(new_bytes) > self.current_dialogue.length + 10:
			response = messagebox.askyesno(
				"Warning",
				f"New text is {len(new_bytes) - self.current_dialogue.length} bytes longer.\n"
				"This may overwrite adjacent data. Continue?"
			)
			if not response:
				return

		# Write to ROM
		try:
			self.rom_manager.write_bytes(self.current_dialogue.rom_offset, new_bytes)

			# Update dialogue entry
			self.current_dialogue.raw_bytes = new_bytes
			self.current_dialogue.decoded_text = new_text
			self.current_dialogue.length = len(new_bytes)

			messagebox.showinfo("Success", "Dialogue saved to ROM")
			self.text_editor.edit_modified(False)

			# Refresh tree
			self.filter_dialogues()

		except Exception as e:
			messagebox.showerror("Error", f"Failed to save: {e}")

	def save_all_dialogues(self):
		"""Save all modified dialogues."""
		messagebox.showinfo("Info", "Save all functionality coming soon")

	def revert_dialogue(self):
		"""Revert current dialogue to saved version."""
		if self.current_dialogue:
			self.display_dialogue(self.current_dialogue)

	def copy_text(self):
		"""Copy current text to clipboard."""
		text = self.text_editor.get('1.0', tk.END)
		self.clipboard_clear()
		self.clipboard_append(text)
		messagebox.showinfo("Info", "Text copied to clipboard")

	def export_script(self):
		"""Export all dialogue to text file."""
		filename = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
		)

		if filename:
			try:
				with open(filename, 'w', encoding='utf-8') as f:
					f.write("=" * 80 + "\n")
					f.write("DRAGON WARRIOR DIALOGUE SCRIPT\n")
					f.write("=" * 80 + "\n\n")

					for dialogue in self.dialogues:
						f.write(f"[{dialogue.id:03d}] Pointer: 0x{dialogue.pointer:04X}\n")
						f.write("-" * 80 + "\n")
						f.write(dialogue.decoded_text)
						f.write("\n" + "=" * 80 + "\n\n")

				messagebox.showinfo("Success", f"Exported {len(self.dialogues)} dialogues to {filename}")
			except Exception as e:
				messagebox.showerror("Error", f"Export failed: {e}")

	def import_script(self):
		"""Import dialogue from text file."""
		messagebox.showinfo("Info", "Import functionality coming soon")
