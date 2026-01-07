; Dragon Warrior Palette Data
; Generated from edited palettes

.include "Dragon_Warrior_Defines.asm"

.segment "PaletteData"

; Palette Data Table
; Each palette has 4 colors (NES standard)

; Overworld Palette (ID: 0)
Palette_00:
	.byte $0F, $30, $10, $00

; Dungeon Palette (ID: 1)
Palette_01:
	.byte $0F, $00, $10, $30

; Town Palette (ID: 2)
Palette_02:
	.byte $0F, $00, $10, $30

; Battle Palette (ID: 3)
Palette_03:
	.byte $0F, $00, $10, $30

; Menu Palette (ID: 4)
Palette_04:
	.byte $0F, $00, $10, $30

; Character Palette (ID: 5)
Palette_05:
	.byte $0F, $00, $10, $30

; Monster Palette (ID: 6)
Palette_06:
	.byte $0F, $0F, $00, $30

; Dialog Palette (ID: 7)
Palette_07:
	.byte $0F, $00, $10, $30

; Palette Pointer Table
	.word Palette_00
	.word Palette_01
	.word Palette_02
	.word Palette_03
	.word Palette_04
	.word Palette_05
	.word Palette_06
	.word Palette_07