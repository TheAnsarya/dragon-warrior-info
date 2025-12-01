#!/usr/bin/env python3
"""
Generate music and sound effect tables from JSON definitions.

This tool takes music.json and generates assembly code for:
- Music pointer tables (MusicStartIndexTable)
- Sound effect pointer tables (SFXStartIndexTable)
- Musical note frequency table (MusicalNotesTable)
- Control byte definitions

Usage:
    python generate_music_tables.py [--output build/reinsertion/music_tables.asm]
"""

import json
import sys
from pathlib import Path


def load_music_data(json_path: str) -> dict:
    """Load music data from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def generate_control_byte_definitions(data: dict) -> str:
    """Generate assembly definitions for music control bytes."""
    lines = []
    lines.append("; =============================================================================")
    lines.append("; MUSIC CONTROL BYTE DEFINITIONS")
    lines.append("; =============================================================================")
    lines.append("; These control bytes are used in music data streams")
    lines.append("; Values $F6-$FF are reserved for control functions")
    lines.append("; =============================================================================")
    lines.append("")

    control_bytes = data.get('_metadata', {}).get('control_bytes', {})

    # Define control bytes with descriptive names
    ctrl_defs = [
        ('MUSICCTL_END_SPACE',  0xF6, 'Stop adding quiet time between notes'),
        ('MUSICCTL_ADD_SPACE',  0xF7, 'Add quiet time (next byte = count)'),
        ('MUSICCTL_NOISE_VOL',  0xF8, 'Noise volume (next byte = volume)'),
        ('MUSICCTL_NOTE_OFFSET',0xF9, 'Note pitch offset'),
        ('MUSICCTL_CNTRL1',     0xFA, 'Channel control 1 (sweep register)'),
        ('MUSICCTL_CNTRL0',     0xFB, 'Channel control 0 (duty/volume)'),
        ('MUSICCTL_NO_OP',      0xFC, 'No operation / skip'),
        ('MUSICCTL_RETURN',     0xFD, 'Return to previous address'),
        ('MUSICCTL_JUMP',       0xFE, 'Jump to address (next 2 bytes)'),
        ('MUSICCTL_TEMPO',      0xFF, 'Set tempo (next byte = tempo value)'),
    ]

    for name, value, desc in ctrl_defs:
        lines.append(f"{name:<24} = ${value:02X}    ; {desc}")

    lines.append("")

    # Note range constants
    lines.append("; Note value range")
    lines.append("NOTE_VALUE_MIN          = $80    ; Lowest note (C2)")
    lines.append("NOTE_VALUE_MAX          = $C8    ; Highest note (C8)")
    lines.append("NOTE_TABLE_SIZE         = $49    ; 73 notes total")
    lines.append("")

    return '\n'.join(lines)


def generate_music_pointer_table(data: dict) -> str:
    """Generate music start index pointer table."""
    lines = []
    lines.append("; =============================================================================")
    lines.append("; MUSIC START INDEX TABLE")
    lines.append("; Address: $8297 (Bank01)")
    lines.append("; Format: 2 bytes per track (SQ1 pointer, SQ2 pointer, TRI pointer)")
    lines.append("; =============================================================================")
    lines.append("")
    lines.append("MusicStartIndexTable:")

    tracks = data.get('music_tracks', {})

    # Sort by track_id
    sorted_tracks = sorted(tracks.items(), key=lambda x: x[1].get('track_id', 0))

    for track_name, track_data in sorted_tracks:
        track_id = track_data.get('track_id', 0)
        name = track_data.get('name', 'Unknown')
        channels = track_data.get('channels', {})

        sq1_label = channels.get('sq1', {}).get('label', f'SQ1Track{track_id}')
        sq2_label = channels.get('sq2', {}).get('label', f'SQ2Track{track_id}')
        tri_label = channels.get('tri', {}).get('label', f'TRITrack{track_id}')

        lines.append(f"    ; Track ${track_id:02X}: {track_name} - {name}")
        lines.append(f"    .word {sq1_label}         ; SQ1 channel")
        lines.append(f"    .word {sq2_label}         ; SQ2 channel")
        lines.append(f"    .word {tri_label}         ; TRI channel")

    lines.append("")
    lines.append(f"; Total tracks: {len(sorted_tracks)}")
    lines.append("")

    return '\n'.join(lines)


def generate_sfx_pointer_table(data: dict) -> str:
    """Generate sound effect start index pointer table."""
    lines = []
    lines.append("; =============================================================================")
    lines.append("; SOUND EFFECT START INDEX TABLE")
    lines.append("; Address: $8339 (Bank01)")
    lines.append("; Format: 2 bytes per effect (SQ1 pointer, SQ2 pointer, TRI pointer)")
    lines.append("; =============================================================================")
    lines.append("")
    lines.append("SFXStartIndexTable:")

    sfx = data.get('sound_effects', {})

    # Sort by sfx_id
    sorted_sfx = sorted(sfx.items(), key=lambda x: x[1].get('sfx_id', 0))

    for sfx_name, sfx_data in sorted_sfx:
        sfx_id = sfx_data.get('sfx_id', 0)
        name = sfx_data.get('name', 'Unknown')
        channels = sfx_data.get('channels', {})

        sq1_label = channels.get('sq1', {}).get('label', f'SQ1SFX{sfx_id}')
        sq2_label = channels.get('sq2', {}).get('label', f'SQ2SFX{sfx_id}')
        tri_label = channels.get('tri', {}).get('label', f'TRISFX{sfx_id}')

        lines.append(f"    ; SFX ${sfx_id:02X}: {sfx_name} - {name}")
        lines.append(f"    .word {sq1_label}         ; SQ1 channel")
        lines.append(f"    .word {sq2_label}         ; SQ2 channel")
        lines.append(f"    .word {tri_label}         ; TRI channel")

    lines.append("")
    lines.append(f"; Total SFX: {len(sorted_sfx)}")
    lines.append("")

    return '\n'.join(lines)


def generate_note_frequency_table(data: dict) -> str:
    """Generate musical notes frequency lookup table."""
    lines = []
    lines.append("; =============================================================================")
    lines.append("; MUSICAL NOTES FREQUENCY TABLE")
    lines.append("; Address: $8205 (Bank01)")
    lines.append("; Format: 2 bytes per note (NES APU timer low, timer high)")
    lines.append("; Note values range from $80 (C2) to $C8 (C8)")
    lines.append("; =============================================================================")
    lines.append("")
    lines.append("MusicalNotesTable:")

    notes = data.get('musical_notes', {})

    # Sort by hex value
    sorted_notes = sorted(notes.items(), key=lambda x: int(x[0], 16))

    current_octave = None
    for hex_val, note_data in sorted_notes:
        note_name = note_data.get('note', '?')
        octave = note_data.get('octave', 0)
        freq_hz = note_data.get('frequency_hz', 0)

        # Add octave header
        if octave != current_octave:
            if current_octave is not None:
                lines.append("")
            lines.append(f"    ; --- Octave {octave} ---")
            current_octave = octave

        # Calculate NES APU timer value from frequency
        # APU timer = (CPU_FREQ / (16 * freq)) - 1
        # Where CPU_FREQ = 1789773 Hz (NTSC)
        if freq_hz > 0:
            timer_val = int((1789773 / (16 * freq_hz)) - 1)
            timer_low = timer_val & 0xFF
            timer_high = (timer_val >> 8) & 0x07
        else:
            timer_low = 0
            timer_high = 0

        # Note index (subtract $80 to get table offset)
        note_idx = int(hex_val, 16) - 0x80
        lines.append(f"    .byte ${timer_low:02X}, ${timer_high:02X}    ; ${hex_val[2:]}: {note_name:<4} ({freq_hz:7.1f} Hz)")

    lines.append("")
    lines.append(f"; Total notes: {len(sorted_notes)}")
    lines.append("")

    return '\n'.join(lines)


def generate_map_music_table(data: dict) -> str:
    """Generate map-to-music assignment reference."""
    lines = []
    lines.append("; =============================================================================")
    lines.append("; MAP MUSIC ASSIGNMENTS (Reference)")
    lines.append("; =============================================================================")

    map_music = data.get('map_music', {})
    tracks = data.get('music_tracks', {})

    lines.append("; Map Area              Music Track")
    lines.append("; ---------------       -----------")

    for area, track in sorted(map_music.items()):
        if isinstance(track, list):
            for i, t in enumerate(track):
                track_id = tracks.get(t, {}).get('track_id', 0)
                lines.append(f"; {area}[{i}]          ${track_id:02X} ({t})")
        else:
            track_id = tracks.get(track, {}).get('track_id', 0)
            lines.append(f"; {area:<20} ${track_id:02X} ({track})")

    lines.append("")
    return '\n'.join(lines)


def generate_tempo_reference(data: dict) -> str:
    """Generate tempo calculation reference."""
    lines = []
    lines.append("; =============================================================================")
    lines.append("; TEMPO REFERENCE")
    lines.append("; =============================================================================")

    tempo_ref = data.get('tempo_reference', {})
    formula = tempo_ref.get('formula', '')
    examples = tempo_ref.get('examples', {})

    lines.append(f"; Formula: {formula}")
    lines.append(";")
    lines.append("; Common tempo values:")
    for val, desc in sorted(examples.items()):
        lines.append(f";   {val}: {desc}")

    lines.append("")
    return '\n'.join(lines)


def generate_full_assembly(data: dict) -> str:
    """Generate complete music tables assembly file."""
    header = [
        "; =============================================================================",
        "; DRAGON WARRIOR - MUSIC AND SOUND EFFECT TABLES",
        "; =============================================================================",
        "; Auto-generated from assets/json/music.json",
        "; Generator: tools/generate_music_tables.py",
        "; ",
        "; This file contains:",
        ";   - Music control byte definitions",
        ";   - Music pointer table (MusicStartIndexTable)",
        ";   - Sound effect pointer table (SFXStartIndexTable)",
        ";   - Musical notes frequency table (MusicalNotesTable)",
        ";   - Map music assignments reference",
        "; ",
        "; To modify music data, edit the JSON file and run:",
        ";   python tools/generate_music_tables.py",
        "; =============================================================================",
        "",
    ]

    sections = [
        '\n'.join(header),
        generate_control_byte_definitions(data),
        generate_tempo_reference(data),
        generate_map_music_table(data),
        generate_music_pointer_table(data),
        generate_sfx_pointer_table(data),
        generate_note_frequency_table(data),
    ]

    return '\n'.join(sections)


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    json_path = project_root / 'assets' / 'json' / 'music.json'
    output_path = project_root / 'build' / 'reinsertion' / 'music_tables.asm'

    # Allow command line override
    if len(sys.argv) > 2 and sys.argv[1] == '--output':
        output_path = Path(sys.argv[2])

    # Load data
    if not json_path.exists():
        print(f"Error: JSON file not found: {json_path}")
        sys.exit(1)

    print(f"Loading music data from: {json_path}")
    data = load_music_data(str(json_path))

    # Generate assembly
    assembly = generate_full_assembly(data)

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(assembly)

    tracks = data.get('music_tracks', {})
    sfx = data.get('sound_effects', {})
    notes = data.get('musical_notes', {})

    print(f"Generated assembly file: {output_path}")
    print(f"  - {len(tracks)} music tracks")
    print(f"  - {len(sfx)} sound effects")
    print(f"  - {len(notes)} musical notes")


if __name__ == '__main__':
    main()
