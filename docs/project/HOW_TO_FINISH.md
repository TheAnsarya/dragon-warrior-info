# Dragon Warrior I (NES) - How to Finish This Project

**Project Completion Roadmap & Status**

This document tracks what's needed to consider the Dragon Warrior I disassembly and documentation project "complete."

## 📊 Current Status: ~75% Complete

### ✅ Completed Work

#### Disassembly & Source
- [x] PRG ROM fully disassembled (4 banks x 16KB)
- [x] CHR ROM extracted and organized
- [x] Bank00.asm - Bank03.asm source files created
- [x] Build system (Ophis assembler) functional
- [x] ROM rebuilds successfully and matches original

#### Asset Extraction
- [x] All 39 monsters extracted with stats (JSON)
- [x] All 10 spells extracted with MP costs (JSON)
- [x] All 32 items/equipment extracted (JSON)
- [x] Shop inventories extracted (JSON)
- [x] Experience table extracted (JSON)
- [x] Dialog text extracted (JSON)
- [x] Graphics CHR tiles organized (PNG)
- [x] World map extracted (PNG)
- [x] Palettes extracted (PNG/JSON)

#### Tools Created
- [x] Universal editor GUI (monster/item/spell/shop editors)
- [x] Asset extraction pipeline (ROM → JSON)
- [x] Asset reinsertion pipeline (JSON → ROM)
- [x] Graphics CHR extractor/organizer
- [x] ROM analyzer and comparison tools
- [x] Build system with verification

#### Documentation
- [x] ROM map basics
- [x] RAM map basics
- [x] Asset catalog HTML
- [x] Video production guides
- [x] Session logs

---

## 🔲 Remaining Work

### 1. Disassembly Refinement (Priority: HIGH)
**Estimated effort: 20-40 hours**

- [ ] **Label all unknown labels** - Replace `Lxxxx` labels with descriptive names
  - Current: ~500+ unnamed labels remain
  - Review exported label inventory
  - Document what each label does
  
- [ ] **Document all subroutines** - Add comments explaining each function
  - Battle system routines
  - Menu handling routines
  - Map/world navigation
  - Sound/music routines
  - NPC AI and dialog handling

- [ ] **Data tables** - Identify and label all data tables
  - Tile mapping tables
  - Palette tables
  - Pointer tables
  - String tables

### 2. Dark Repos Wiki (Priority: HIGH)
**Estimated effort: 10-20 hours**

Wiki pages exist in `GameInfo/DarkRepos/Wiki/NES/Dragon_Warrior/`:

- [ ] **ROM_Map.wikitext** - Add all missing address ranges
  - Bank 0 code/data breakdown
  - Bank 1 code/data breakdown  
  - Bank 2 code/data breakdown
  - Bank 3 code/data breakdown
  - CHR ROM tile layout

- [ ] **RAM_Map.wikitext** - Document all RAM addresses
  - Player stats locations
  - Game state flags
  - Temporary variables
  - NPC positions

- [ ] **Monster_Data.wikitext** - Verify all 39 monsters documented
- [ ] **Items.wikitext** - Complete equipment list
- [ ] **Magic.wikitext** - Document all spell effects and formulas
- [ ] **Battle_System.wikitext** - Document damage formulas, accuracy
- [ ] **Glitches.wikitext** - Known glitches and exploits
- [ ] **Secrets.wikitext** - Hidden features, easter eggs

### 3. Build System Improvements (Priority: MEDIUM)
**Estimated effort: 5-10 hours**

- [ ] **Clean build verification** - Build from source only (no binary includes)
- [ ] **Modular includes** - Split source into organized include files
- [ ] **Asset pipeline integration** - JSON → ASM generation automated
- [ ] **Test suite** - Automated ROM verification tests

### 4. Tool Enhancements (Priority: MEDIUM)
**Estimated effort: 10-15 hours**

- [ ] **Map editor** - Visual world map editor
- [ ] **NPC placement editor** - Place NPCs visually
- [ ] **Encounter zone editor** - Edit random encounter zones
- [ ] **Dialog editor improvements** - Better text encoding support
- [ ] **Music/sound editor** - NSF-style music editing

### 5. Advanced Documentation (Priority: LOW)
**Estimated effort: 5-10 hours**

- [ ] **Compression analysis** - Document any compressed data
- [ ] **Music format** - Complete music engine documentation
- [ ] **Map encoding** - Interior map format specification
- [ ] **NPC behavior** - AI and movement patterns

---

## 🎯 Definition of "Complete"

The project is considered complete when:

1. **100% Label Coverage** - No `Lxxxx` style labels remain; all are named descriptively
2. **Complete ROM Map** - Every byte from $0000-$FFFF in each bank documented
3. **Complete RAM Map** - All RAM addresses $0000-$07FF documented
4. **Wiki Complete** - All Dark Repos wiki pages fully populated
5. **Clean Build** - ROM builds from source without binary blobs
6. **Full Commenting** - Every subroutine has explanatory comments
7. **Tool Suite Complete** - Can modify any game aspect via tools

---

## 📋 Task Priority Matrix

| Task | Impact | Effort | Priority |
|------|--------|--------|----------|
| Label remaining Lxxxx | High | High | **P1** |
| Complete ROM Map wiki | High | Medium | **P1** |
| Complete RAM Map wiki | High | Medium | **P1** |
| Document battle system | High | Medium | **P2** |
| Build system cleanup | Medium | Low | **P2** |
| Map editor | Medium | High | **P3** |
| Music documentation | Low | Medium | **P3** |

---

## 🗓️ Suggested Completion Timeline

### Phase 1: Core Documentation (Weeks 1-2)
- Focus on ROM Map and RAM Map wiki pages
- Label most important routines (battle, menu, map)
- Update existing wiki pages with verified data

### Phase 2: Disassembly Cleanup (Weeks 3-4)
- Systematic label replacement
- Add comments to all major subroutines
- Identify and document all data tables

### Phase 3: Tool & Build Polish (Week 5)
- Clean build verification
- Tool enhancements
- Final wiki updates

### Phase 4: Review & Release (Week 6)
- Comprehensive review
- Generate final documentation
- Create release package

---

## 📁 Key File Locations

| Content | Location |
|---------|----------|
| Disassembly source | `source_files/Bank*.asm` |
| Extracted assets | `assets/json/*.json` |
| Wiki content | `GameInfo/DarkRepos/Wiki/NES/Dragon_Warrior/` |
| Tools | `tools/` |
| Build output | `build/` |
| Documentation | `docs/` |

---

## 🔗 Related Resources

- [Data Crystal - Dragon Warrior](https://datacrystal.tcrf.net/wiki/Dragon_Warrior) - Reference source
- [nmikstas Dragon Warrior Disassembly](https://github.com/nmikstas/dragon-warrior-disassembly) - Original disassembly
- [RHDN Dragon Warrior](https://www.romhacking.net/games/304/) - Community hacks/docs

---

## 📝 GitHub Issues to Create

1. `epic: Complete DW1 Disassembly Documentation`
2. `task: Replace all Lxxxx labels with descriptive names`
3. `task: Complete ROM Map wiki page`
4. `task: Complete RAM Map wiki page`
5. `task: Document battle system formulas`
6. `task: Document all 39 monster entries`
7. `task: Clean build from source only`
8. `task: Create map editor tool`

---

*Last updated: 2025*
