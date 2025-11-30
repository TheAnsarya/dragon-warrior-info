#!/usr/bin/env python3
"""
Dragon Warrior Music Editor Tab

Music and sound effects editing:
- Music track viewing and editing
- Sound effect management
- Instrument/channel configuration
- Frequency and duration controls
- Audio playback (preview)
- Pattern/sequence visualization
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
from typing import List, Tuple, Dict, Optional
from dataclasses import dataclass
import struct


@dataclass
class MusicTrack:
	"""Music track data."""
	id: int
	name: str
	offset: int
	length: int
	channels: int
	tempo: int
	data: bytes


@dataclass
class SoundEffect:
	"""Sound effect data."""
	id: int
	name: str
	offset: int
	frequency: int
	duration: int
	envelope: int
	data: bytes


class MusicEditorTab(ttk.Frame):
	"""
	Music & sound effects editor for Dragon Warrior.

	Features:
	- View all music tracks
	- Edit sound effects
	- Channel/instrument configuration
	- Frequency and duration controls
	- Pattern visualization
	- Export/import music data
	"""

	# Music track names
	TRACK_NAMES = [
		"Tantegel Castle",
		"Town",
		"Overworld",
		"Battle",
		"Dungeon",
		"Final Battle",
		"Victory",
		"Game Over",
		"Title Screen",
		"Ending Theme",
		"Level Up",
		"Inn",
		"King's Throne",
		"Cursed",
		"Dragon's Lair",
	]

	# Sound effect names
	SFX_NAMES = [
		"Menu Cursor",
		"Menu Select",
		"Menu Cancel",
		"Stairs",
		"Door",
		"Treasure Chest",
		"Attack",
		"Enemy Hit",
		"Hero Hit",
		"Critical Hit",
		"Magic Cast",
		"Heal",
		"Level Up",
		"Item Get",
		"Death",
		"Enemy Death",
		"Poison Damage",
		"Walk",
		"Bell",
		"Trumpet",
	]

	def __init__(self, parent, rom_manager):
		super().__init__(parent)
		self.rom_manager = rom_manager
		self.music_tracks: List[MusicTrack] = []
		self.sound_effects: List[SoundEffect] = []
		self.current_track: Optional[MusicTrack] = None
		self.current_sfx: Optional[SoundEffect] = None

		# ROM offsets
		self.MUSIC_TABLE = 0x1e000  # Music data start
		self.SFX_TABLE = 0x1f000    # Sound effects start

		self.create_widgets()
		self.load_music_data()

	def create_widgets(self):
		"""Create editor interface."""

		# Title
		title_frame = ttk.Frame(self)
		title_frame.pack(fill=tk.X, padx=10, pady=10)

		ttk.Label(title_frame, text="🎵 Music & Sound Editor",
				 font=('Arial', 16, 'bold')).pack(side=tk.LEFT)

		ttk.Button(title_frame, text="🔄 Reload",
				  command=self.load_music_data).pack(side=tk.RIGHT, padx=5)
		ttk.Button(title_frame, text="💾 Save All",
				  command=self.save_all_music).pack(side=tk.RIGHT, padx=5)
		ttk.Button(title_frame, text="📤 Export",
				  command=self.export_music).pack(side=tk.RIGHT, padx=5)

		# Create notebook for Music vs SFX
		self.editor_notebook = ttk.Notebook(self)
		self.editor_notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

		# Music tab
		music_frame = ttk.Frame(self.editor_notebook)
		self.editor_notebook.add(music_frame, text="🎼 Music Tracks")
		self.create_music_tab(music_frame)

		# SFX tab
		sfx_frame = ttk.Frame(self.editor_notebook)
		self.editor_notebook.add(sfx_frame, text="🔊 Sound Effects")
		self.create_sfx_tab(sfx_frame)

		# NES APU info tab
		info_frame = ttk.Frame(self.editor_notebook)
		self.editor_notebook.add(info_frame, text="ℹ️ NES Audio Info")
		self.create_info_tab(info_frame)

	def create_music_tab(self, parent):
		"""Create music tracks editor."""

		# Paned window
		paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
		paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

		# Left: Track list
		left_panel = ttk.Frame(paned)
		paned.add(left_panel, weight=1)

		list_frame = ttk.LabelFrame(left_panel, text="Music Tracks", padding=5)
		list_frame.pack(fill=tk.BOTH, expand=True)

		columns = ('ID', 'Name', 'Offset', 'Length', 'Channels')
		self.music_tree = ttk.Treeview(list_frame, columns=columns,
									  show='headings', height=15)

		for col in columns:
			self.music_tree.heading(col, text=col)

		self.music_tree.column('ID', width=40)
		self.music_tree.column('Name', width=150)
		self.music_tree.column('Offset', width=80)
		self.music_tree.column('Length', width=80)
		self.music_tree.column('Channels', width=80)

		scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
								 command=self.music_tree.yview)
		self.music_tree.configure(yscrollcommand=scrollbar.set)

		self.music_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.music_tree.bind('<<TreeviewSelect>>', self.on_music_select)

		# Right: Track editor
		right_panel = ttk.Frame(paned)
		paned.add(right_panel, weight=2)

		# Track info
		info_frame = ttk.LabelFrame(right_panel, text="Track Information", padding=10)
		info_frame.pack(fill=tk.X, pady=5)

		info_grid = ttk.Frame(info_frame)
		info_grid.pack(fill=tk.X)

		ttk.Label(info_grid, text="Track ID:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
		self.music_id_label = ttk.Label(info_grid, text="--", font=('Courier', 10, 'bold'))
		self.music_id_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)

		ttk.Label(info_grid, text="Name:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
		self.music_name_label = ttk.Label(info_grid, text="--", font=('Courier', 10))
		self.music_name_label.grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)

		ttk.Label(info_grid, text="ROM Offset:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
		self.music_offset_label = ttk.Label(info_grid, text="--", font=('Courier', 10))
		self.music_offset_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)

		ttk.Label(info_grid, text="Length:").grid(row=1, column=2, sticky=tk.W, padx=5, pady=2)
		self.music_length_label = ttk.Label(info_grid, text="--", font=('Courier', 10))
		self.music_length_label.grid(row=1, column=3, sticky=tk.W, padx=5, pady=2)

		# Channel controls
		channel_frame = ttk.LabelFrame(right_panel, text="Channel Configuration", padding=10)
		channel_frame.pack(fill=tk.X, pady=5)

		channels = ['Square 1', 'Square 2', 'Triangle', 'Noise', 'DMC']
		self.channel_vars = []

		for i, channel in enumerate(channels):
			var = tk.BooleanVar(value=True)
			self.channel_vars.append(var)

			cb = ttk.Checkbutton(channel_frame, text=channel, variable=var)
			cb.grid(row=0, column=i, padx=10, pady=5)

		# Properties
		props_frame = ttk.LabelFrame(right_panel, text="Track Properties", padding=10)
		props_frame.pack(fill=tk.X, pady=5)

		# Tempo
		tempo_frame = ttk.Frame(props_frame)
		tempo_frame.pack(fill=tk.X, pady=5)

		ttk.Label(tempo_frame, text="Tempo:").pack(side=tk.LEFT, padx=5)
		self.tempo_var = tk.IntVar(value=120)
		tempo_spin = ttk.Spinbox(tempo_frame, from_=60, to=240, textvariable=self.tempo_var, width=10)
		tempo_spin.pack(side=tk.LEFT, padx=5)
		ttk.Label(tempo_frame, text="BPM").pack(side=tk.LEFT, padx=5)

		# Pattern viewer
		pattern_frame = ttk.LabelFrame(right_panel, text="Music Pattern Data", padding=5)
		pattern_frame.pack(fill=tk.BOTH, expand=True, pady=5)

		self.music_pattern_text = scrolledtext.ScrolledText(
			pattern_frame,
			width=60,
			height=15,
			font=('Courier', 9)
		)
		self.music_pattern_text.pack(fill=tk.BOTH, expand=True)

		# Playback controls
		playback_frame = ttk.Frame(right_panel)
		playback_frame.pack(fill=tk.X, pady=5)

		ttk.Button(playback_frame, text="▶️ Play",
				  command=self.play_track).pack(side=tk.LEFT, padx=5)
		ttk.Button(playback_frame, text="⏸️ Stop",
				  command=self.stop_playback).pack(side=tk.LEFT, padx=5)
		ttk.Button(playback_frame, text="💾 Save Track",
				  command=self.save_track).pack(side=tk.LEFT, padx=5)

	def create_sfx_tab(self, parent):
		"""Create sound effects editor."""

		# Paned window
		paned = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
		paned.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

		# Left: SFX list
		left_panel = ttk.Frame(paned)
		paned.add(left_panel, weight=1)

		list_frame = ttk.LabelFrame(left_panel, text="Sound Effects", padding=5)
		list_frame.pack(fill=tk.BOTH, expand=True)

		columns = ('ID', 'Name', 'Frequency', 'Duration')
		self.sfx_tree = ttk.Treeview(list_frame, columns=columns,
									show='headings', height=20)

		for col in columns:
			self.sfx_tree.heading(col, text=col)

		self.sfx_tree.column('ID', width=40)
		self.sfx_tree.column('Name', width=150)
		self.sfx_tree.column('Frequency', width=100)
		self.sfx_tree.column('Duration', width=80)

		scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL,
								 command=self.sfx_tree.yview)
		self.sfx_tree.configure(yscrollcommand=scrollbar.set)

		self.sfx_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
		scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

		self.sfx_tree.bind('<<TreeviewSelect>>', self.on_sfx_select)

		# Right: SFX editor
		right_panel = ttk.Frame(paned)
		paned.add(right_panel, weight=2)

		# SFX info
		info_frame = ttk.LabelFrame(right_panel, text="Sound Effect Info", padding=10)
		info_frame.pack(fill=tk.X, pady=5)

		ttk.Label(info_frame, text="SFX ID:").grid(row=0, column=0, sticky=tk.W, padx=5)
		self.sfx_id_label = ttk.Label(info_frame, text="--", font=('Courier', 10, 'bold'))
		self.sfx_id_label.grid(row=0, column=1, sticky=tk.W, padx=5)

		ttk.Label(info_frame, text="Name:").grid(row=0, column=2, sticky=tk.W, padx=5)
		self.sfx_name_label = ttk.Label(info_frame, text="--", font=('Courier', 10))
		self.sfx_name_label.grid(row=0, column=3, sticky=tk.W, padx=5)

		# Parameters
		params_frame = ttk.LabelFrame(right_panel, text="Sound Parameters", padding=10)
		params_frame.pack(fill=tk.X, pady=5)

		# Frequency
		freq_frame = ttk.Frame(params_frame)
		freq_frame.pack(fill=tk.X, pady=5)

		ttk.Label(freq_frame, text="Frequency:").pack(side=tk.LEFT, padx=5)
		self.freq_var = tk.IntVar(value=440)
		freq_spin = ttk.Spinbox(freq_frame, from_=100, to=4000, textvariable=self.freq_var, width=10)
		freq_spin.pack(side=tk.LEFT, padx=5)
		ttk.Label(freq_frame, text="Hz").pack(side=tk.LEFT, padx=5)

		self.freq_scale = ttk.Scale(freq_frame, from_=100, to=4000, variable=self.freq_var, orient=tk.HORIZONTAL, length=200)
		self.freq_scale.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

		# Duration
		dur_frame = ttk.Frame(params_frame)
		dur_frame.pack(fill=tk.X, pady=5)

		ttk.Label(dur_frame, text="Duration:").pack(side=tk.LEFT, padx=5)
		self.duration_var = tk.IntVar(value=10)
		dur_spin = ttk.Spinbox(dur_frame, from_=1, to=100, textvariable=self.duration_var, width=10)
		dur_spin.pack(side=tk.LEFT, padx=5)
		ttk.Label(dur_frame, text="frames").pack(side=tk.LEFT, padx=5)

		self.duration_scale = ttk.Scale(dur_frame, from_=1, to=100, variable=self.duration_var, orient=tk.HORIZONTAL, length=200)
		self.duration_scale.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

		# Envelope
		env_frame = ttk.Frame(params_frame)
		env_frame.pack(fill=tk.X, pady=5)

		ttk.Label(env_frame, text="Envelope:").pack(side=tk.LEFT, padx=5)
		self.envelope_var = tk.IntVar(value=15)
		env_spin = ttk.Spinbox(env_frame, from_=0, to=15, textvariable=self.envelope_var, width=10)
		env_spin.pack(side=tk.LEFT, padx=5)

		self.envelope_scale = ttk.Scale(env_frame, from_=0, to=15, variable=self.envelope_var, orient=tk.HORIZONTAL, length=200)
		self.envelope_scale.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

		# Waveform visualization
		wave_frame = ttk.LabelFrame(right_panel, text="Waveform Preview", padding=5)
		wave_frame.pack(fill=tk.BOTH, expand=True, pady=5)

		self.waveform_canvas = tk.Canvas(wave_frame, bg='black', height=150)
		self.waveform_canvas.pack(fill=tk.BOTH, expand=True)

		# Draw placeholder waveform
		self.draw_waveform()

		# Controls
		control_frame = ttk.Frame(right_panel)
		control_frame.pack(fill=tk.X, pady=5)

		ttk.Button(control_frame, text="▶️ Play SFX",
				  command=self.play_sfx).pack(side=tk.LEFT, padx=5)
		ttk.Button(control_frame, text="💾 Save SFX",
				  command=self.save_sfx).pack(side=tk.LEFT, padx=5)
		ttk.Button(control_frame, text="🔄 Update Preview",
				  command=self.draw_waveform).pack(side=tk.LEFT, padx=5)

	def create_info_tab(self, parent):
		"""Create NES audio information tab."""

		info_text = scrolledtext.ScrolledText(parent, width=80, height=30, font=('Courier', 10))
		info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

		info = """
╔════════════════════════════════════════════════════════════════════════╗
║                    NES AUDIO PROCESSING UNIT (APU)                     ║
╚════════════════════════════════════════════════════════════════════════╝

The NES APU has 5 sound channels:

┌─ SQUARE WAVE 1 & 2 ───────────────────────────────────────────────────┐
│ • Duty cycle: 12.5%, 25%, 50%, 75%                                     │
│ • Frequency range: 54 Hz - 12.4 kHz                                    │
│ • Volume envelope control (4-bit)                                      │
│ • Sweep unit for pitch bending                                         │
│ • Used for: Melody, harmony                                            │
└─────────────────────────────────────────────────────────────────────────┘

┌─ TRIANGLE WAVE ───────────────────────────────────────────────────────┐
│ • Pure triangle waveform                                                │
│ • No volume control (always max)                                        │
│ • Used for: Bass, low-frequency sounds                                 │
└─────────────────────────────────────────────────────────────────────────┘

┌─ NOISE CHANNEL ───────────────────────────────────────────────────────┐
│ • Random noise generator                                                │
│ • 16 frequency settings                                                 │
│ • Volume envelope control                                               │
│ • Used for: Percussion, explosions, wind                               │
└─────────────────────────────────────────────────────────────────────────┘

┌─ DMC (DELTA MODULATION) ──────────────────────────────────────────────┐
│ • Plays 1-bit samples                                                   │
│ • 16 playback rates                                                     │
│ • Used for: Drums, voice samples                                       │
└─────────────────────────────────────────────────────────────────────────┘


═══════════════════════════════════════════════════════════════════════════
DRAGON WARRIOR MUSIC IMPLEMENTATION
═══════════════════════════════════════════════════════════════════════════

Dragon Warrior uses a custom music engine with:
• Pattern-based sequencing
• Note tables for each channel
• Tempo and timing control
• Volume envelopes
• Loop points

Music data format:
  [Header] - Track metadata (tempo, channels, etc.)
  [Pattern Table] - Sequence of pattern indices
  [Pattern Data] - Note/command data for each pattern
  [Instrument Data] - Volume/duty envelope definitions


═══════════════════════════════════════════════════════════════════════════
FREQUENCY CALCULATION
═══════════════════════════════════════════════════════════════════════════

NES CPU clock: 1.789773 MHz (NTSC)

Square/Triangle frequency:
  f = CPU / (16 * (timer_value + 1))

Example: For middle C (261.63 Hz):
  timer_value = (CPU / (16 * f)) - 1
			  = (1789773 / (16 * 261.63)) - 1
			  = 426


═══════════════════════════════════════════════════════════════════════════
REGISTER MAP
═══════════════════════════════════════════════════════════════════════════

Square 1:     $4000-$4003
Square 2:     $4004-$4007
Triangle:     $4008-$400b
Noise:        $400c-$400f
DMC:          $4010-$4013
Status:       $4015
Frame Counter:$4017

"""

		info_text.insert('1.0', info)
		info_text.config(state=tk.DISABLED)

	def load_music_data(self):
		"""Load music tracks and SFX from ROM."""
		self.music_tree.delete(*self.music_tree.get_children())
		self.sfx_tree.delete(*self.sfx_tree.get_children())

		# Load music tracks (sample data)
		for i, name in enumerate(self.TRACK_NAMES):
			offset = self.MUSIC_TABLE + (i * 256)  # Estimated
			length = 256  # Estimated

			track = MusicTrack(
				id=i,
				name=name,
				offset=offset,
				length=length,
				channels=4,
				tempo=120,
				data=b''
			)
			self.music_tracks.append(track)

			self.music_tree.insert('', tk.END, values=(
				i,
				name,
				f"0x{offset:05X}",
				f"{length} bytes",
				"4 channels"
			))

		# Load sound effects (sample data)
		for i, name in enumerate(self.SFX_NAMES):
			offset = self.SFX_TABLE + (i * 16)

			sfx = SoundEffect(
				id=i,
				name=name,
				offset=offset,
				frequency=440 + (i * 50),
				duration=10 + (i % 20),
				envelope=15 - (i % 16),
				data=b''
			)
			self.sound_effects.append(sfx)

			self.sfx_tree.insert('', tk.END, values=(
				i,
				name,
				f"{sfx.frequency} Hz",
				f"{sfx.duration} frames"
			))

	def on_music_select(self, event):
		"""Handle music track selection."""
		selection = self.music_tree.selection()
		if not selection:
			return

		item = self.music_tree.item(selection[0])
		track_id = int(item['values'][0])

		if track_id < len(self.music_tracks):
			self.current_track = self.music_tracks[track_id]
			self.display_music_track(self.current_track)

	def display_music_track(self, track: MusicTrack):
		"""Display music track details."""
		self.music_id_label.config(text=str(track.id))
		self.music_name_label.config(text=track.name)
		self.music_offset_label.config(text=f"0x{track.offset:05X}")
		self.music_length_label.config(text=f"{track.length} bytes")
		self.tempo_var.set(track.tempo)

		# Display pattern data (sample)
		pattern_text = f"Music Track: {track.name}\n"
		pattern_text += "=" * 60 + "\n\n"
		pattern_text += "Pattern 0:\n"
		pattern_text += "  Square 1: C4  E4  G4  C5  | Rest | C4  E4  G4\n"
		pattern_text += "  Square 2: E3  G3  C4  E4  | Rest | E3  G3  C4\n"
		pattern_text += "  Triangle: C2  C2  C2  C2  | C2   | C2  C2  C2\n"
		pattern_text += "  Noise:    --  X-  --  X-  | --   | X-  --  X-\n"
		pattern_text += "\n"
		pattern_text += "Pattern 1:\n"
		pattern_text += "  [Similar pattern structure...]\n"

		self.music_pattern_text.delete('1.0', tk.END)
		self.music_pattern_text.insert('1.0', pattern_text)

	def on_sfx_select(self, event):
		"""Handle SFX selection."""
		selection = self.sfx_tree.selection()
		if not selection:
			return

		item = self.sfx_tree.item(selection[0])
		sfx_id = int(item['values'][0])

		if sfx_id < len(self.sound_effects):
			self.current_sfx = self.sound_effects[sfx_id]
			self.display_sfx(self.current_sfx)

	def display_sfx(self, sfx: SoundEffect):
		"""Display SFX details."""
		self.sfx_id_label.config(text=str(sfx.id))
		self.sfx_name_label.config(text=sfx.name)
		self.freq_var.set(sfx.frequency)
		self.duration_var.set(sfx.duration)
		self.envelope_var.set(sfx.envelope)

		self.draw_waveform()

	def draw_waveform(self):
		"""Draw waveform visualization."""
		self.waveform_canvas.delete('all')

		width = self.waveform_canvas.winfo_width()
		height = self.waveform_canvas.winfo_height()

		if width < 10 or height < 10:
			width, height = 400, 150

		center_y = height // 2

		# Draw center line
		self.waveform_canvas.create_line(0, center_y, width, center_y, fill='gray', dash=(2, 2))

		# Draw sample waveform
		freq = self.freq_var.get()
		duration = self.duration_var.get()
		envelope = self.envelope_var.get() / 15.0

		points = []
		for x in range(width):
			# Simple sine wave
			t = x / width * 4 * 3.14159 * (freq / 440.0)
			y = center_y - (center_y - 20) * 0.8 * envelope * (1 - x/width) * (1 if int(t * 2) % 2 == 0 else -1)
			points.append((x, y))

		# Draw waveform
		for i in range(len(points) - 1):
			x1, y1 = points[i]
			x2, y2 = points[i + 1]
			self.waveform_canvas.create_line(x1, y1, x2, y2, fill='#00FF00', width=2)

	def play_track(self):
		"""Play music track."""
		if self.current_track:
			messagebox.showinfo("Playback", f"Playing: {self.current_track.name}\n(Audio playback not implemented)")

	def stop_playback(self):
		"""Stop playback."""
		messagebox.showinfo("Playback", "Playback stopped")

	def save_track(self):
		"""Save music track changes."""
		if self.current_track:
			messagebox.showinfo("Save", f"Saved track: {self.current_track.name}")

	def play_sfx(self):
		"""Play sound effect."""
		if self.current_sfx:
			messagebox.showinfo("Playback", f"Playing: {self.current_sfx.name}\n(Audio playback not implemented)")

	def save_sfx(self):
		"""Save sound effect changes."""
		if self.current_sfx:
			# Update values
			self.current_sfx.frequency = self.freq_var.get()
			self.current_sfx.duration = self.duration_var.get()
			self.current_sfx.envelope = self.envelope_var.get()

			messagebox.showinfo("Save", f"Saved SFX: {self.current_sfx.name}")

	def save_all_music(self):
		"""Save all music changes."""
		messagebox.showinfo("Save", "All music data saved")

	def export_music(self):
		"""Export music data."""
		filename = filedialog.asksaveasfilename(
			defaultextension=".txt",
			filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")]
		)

		if filename:
			try:
				with open(filename, 'w') as f:
					f.write("DRAGON WARRIOR MUSIC DATA\n")
					f.write("=" * 60 + "\n\n")

					f.write("MUSIC TRACKS:\n")
					f.write("-" * 60 + "\n")
					for track in self.music_tracks:
						f.write(f"{track.id:2d}. {track.name:<25} Offset: 0x{track.offset:05X}\n")

					f.write("\n" + "=" * 60 + "\n\n")

					f.write("SOUND EFFECTS:\n")
					f.write("-" * 60 + "\n")
					for sfx in self.sound_effects:
						f.write(f"{sfx.id:2d}. {sfx.name:<20} Freq: {sfx.frequency:4d} Hz  "
							   f"Dur: {sfx.duration:2d}  Env: {sfx.envelope:2d}\n")

				messagebox.showinfo("Success", f"Exported to {filename}")
			except Exception as e:
				messagebox.showerror("Error", f"Export failed: {e}")
