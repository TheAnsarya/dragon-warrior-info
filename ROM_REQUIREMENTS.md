# ROM Requirements

## Primary Reference ROM

The Dragon Warrior build system uses **Dragon Warrior (U) (PRG1) [!].nes** as the primary reference ROM for:

- Asset extraction and analysis
- Patch generation (IPS/BPS files)
- Build verification and comparison

### Why PRG1?

- **PRG1** is the most commonly used version for ROM hacking and modding
- Better compatibility with existing tools and documentation  
- Stable reference point for the community
- Contains the final released version of the game

### ROM File Structure

```text
roms/
├── Dragon Warrior (U) (PRG1) [!].nes  ← Primary reference ROM
└── Dragon Warrior (U) (PRG0) [!].nes  ← Alternative version (if available)
```

### Automatic Patch Generation

When building ROMs, the system automatically generates timestamped patches comparing your built ROM against the PRG1 reference:

```text
patches/
├── dragon_warrior_20241119_143022.ips  ← Timestamped IPS patch
└── dragon_warrior_20241119_143022.bps  ← Timestamped BPS patch
```

### File Naming Convention

- **Reference ROM**: `Dragon Warrior (U) (PRG1) [!].nes`
- **Built ROM**: `dragon_warrior_modified.nes`
- **Patches**: `dragon_warrior_YYYYMMDD_HHMMSS.{ips|bps}`

### Setting Up ROMs

1. Create a `roms/` directory in the project root
2. Place `Dragon Warrior (U) (PRG1) [!].nes` in the `roms/` directory
3. Ensure the filename matches exactly (case-sensitive on some systems)

### Verification

Use the build system to verify your ROM setup:

```bash
python dragon_warrior_build.py --help
```

The system will check for the reference ROM during asset extraction and patch generation.
