; Dragon Warrior Graphics Data
; Generated from edited graphics

.include "Dragon_Warrior_Defines.asm"

.segment "CHR_ROM"

; Graphics Tiles Data
; Each tile is 8x8 pixels, 2 bits per pixel, 16 bytes total

; hero_000 (ID: 0)
	.byte $B0, $BC, $28, $80, $86, $82, $19, $85	; Plane 1
	.byte $13, $87, $4C, $89, $12, $8D, $6E, $90	; Plane 2

; hero_001 (ID: 1)
	.byte $42, $94, $1E, $98, $88, $9C, $3F, $9F	; Plane 1
	.byte $8A, $A2, $DC, $A6, $2E, $AA, $61, $AC	; Plane 2

; hero_002 (ID: 2)
	.byte $28, $AE, $EE, $AF, $8B, $B6, $65, $BA	; Plane 1
	.byte $F4, $5F, $11, $0A, $1D, $11, $5F, $20	; Plane 2

; hero_003 (ID: 3)
	.byte $18, $14, $0E, $17, $5F, $1E, $19, $47	; Plane 1
	.byte $FC, $60, $FD, $37, $11, $18, $1E, $5F	; Plane 2

; hero_004 (ID: 4)
	.byte $0A, $1B, $1D, $5F, $0D, $0E, $0A, $0D	; Plane 1
	.byte $47, $FC, $50, $37, $11, $18, $1E, $5F	; Plane 2

; hero_005 (ID: 5)
	.byte $0A, $1B, $1D, $5F, $1C, $1D, $1B, $18	; Plane 1
	.byte $17, $10, $5F, $0E, $17, $18, $1E, $10	; Plane 2

; hero_006 (ID: 6)
	.byte $11, $4C, $FD, $3A, $11, $22, $5F, $0C	; Plane 1
	.byte $0A, $17, $5F, $1D, $11, $18, $1E, $5F	; Plane 2

; hero_007 (ID: 7)
	.byte $17, $18, $1D, $5F, $0D, $0E, $0F, $0E	; Plane 1
	.byte $0A, $1D, $5F, $1D, $11, $0E, $5F, $27	; Plane 2

; hero_008 (ID: 8)
	.byte $1B, $0A, $10, $18, $17, $15, $18, $1B	; Plane 1
	.byte $0D, $4B, $40, $FB, $FC, $50, $2C, $0F	; Plane 2

; hero_009 (ID: 9)
	.byte $5F, $1D, $11, $18, $1E, $5F, $0A, $1B	; Plane 1
	.byte $1D, $5F, $19, $15, $0A, $17, $17, $12	; Plane 2

; hero_010 (ID: 10)
	.byte $17, $10, $5F, $1D, $18, $5F, $1D, $0A	; Plane 1
	.byte $14, $0E, $5F, $0A, $5F, $1B, $0E, $1C	; Plane 2

; hero_011 (ID: 11)
	.byte $1D, $48, $5F, $0F, $12, $1B, $1C, $1D	; Plane 1
	.byte $5F, $1C, $0E, $0E, $5F, $2E, $12, $17	; Plane 2

; hero_012 (ID: 12)
	.byte $10, $5F, $2F, $18, $1B, $12, $14, $52	; Plane 1
	.byte $FC, $F8, $5F, $11, $0E, $15, $0D, $5F	; Plane 2

; hero_013 (ID: 13)
	.byte $1D, $11, $0E, $5F, $35, $0A, $12, $17	; Plane 1
	.byte $0B, $18, $20, $5F, $27, $1B, $18, $19	; Plane 2

; hero_014 (ID: 14)
	.byte $5F, $1D, $18, $20, $0A, $1B, $0D, $5F	; Plane 1
	.byte $1D, $11, $0E, $5F, $1C, $14, $22, $47	; Plane 2

; hero_015 (ID: 15)
	.byte $FD, $60, $FB, $FC, $25, $1E, $1D, $5F	; Plane 1
	.byte $17, $18, $5F, $1B, $0A, $12, $17, $0B	; Plane 2

; monsters_016 (ID: 16)
	.byte $18, $20, $5F, $0A, $19, $19, $0E, $0A	; Plane 1
	.byte $1B, $0E, $0D, $5F, $11, $0E, $1B, $0E	; Plane 2

; monsters_017 (ID: 17)
	.byte $47, $FC, $50, $2A, $18, $18, $0D, $5F	; Plane 1
	.byte $16, $18, $1B, $17, $12, $17, $10, $47	; Plane 2

; monsters_018 (ID: 18)
	.byte $FD, $37, $11, $18, $1E, $5F, $11, $0A	; Plane 1
	.byte $1C, $1D, $5F, $11, $0A, $0D, $5F, $0A	; Plane 2

; monsters_019 (ID: 19)
	.byte $5F, $10, $18, $18, $0D, $5F, $17, $12	; Plane 1
	.byte $10, $11, $1D, $53, $1C, $5F, $1C, $15	; Plane 2

; monsters_020 (ID: 20)
	.byte $0E, $0E, $19, $5F, $2C, $5F, $11, $18	; Plane 1
	.byte $19, $0E, $52, $FB, $FC, $50, $2C, $5F	; Plane 2

; monsters_021 (ID: 21)
	.byte $1C, $11, $0A, $15, $15, $5F, $1C, $0E	; Plane 1
	.byte $0E, $5F, $1D, $11, $0E, $0E, $5F, $0A	; Plane 2

; monsters_022 (ID: 22)
	.byte $10, $0A, $12, $17, $52, $FC, $50, $2A	; Plane 1
	.byte $18, $18, $0D, $5F, $16, $18, $1B, $17	; Plane 2

; monsters_023 (ID: 23)
	.byte $12, $17, $10, $47, $FD, $37, $11, $18	; Plane 1
	.byte $1E, $5F, $1C, $0E, $0E, $16, $1C, $5F	; Plane 2

; monsters_024 (ID: 24)
	.byte $1D, $18, $5F, $11, $0A, $1F, $0E, $5F	; Plane 1
	.byte $1C, $19, $0E, $17, $1D, $5F, $0A, $5F	; Plane 2

; monsters_025 (ID: 25)
	.byte $10, $18, $18, $0D, $5F, $17, $12, $10	; Plane 1
	.byte $11, $1D, $52, $FB, $FC, $50, $2A, $18	; Plane 2

; monsters_026 (ID: 26)
	.byte $18, $0D, $5F, $17, $12, $10, $11, $1D	; Plane 1
	.byte $52, $FD, $FC, $50, $32, $14, $0A, $22	; Plane 2

; monsters_027 (ID: 27)
	.byte $47, $FD, $2A, $18, $18, $0D, $49, $0B	; Plane 1
	.byte $22, $0E, $48, $5F, $1D, $1B, $0A, $1F	; Plane 2

; monsters_028 (ID: 28)
	.byte $0E, $15, $0E, $1B, $52, $FC, $50, $3A	; Plane 1
	.byte $0E, $15, $0C, $18, $16, $0E, $5F, $1D	; Plane 2

; monsters_029 (ID: 29)
	.byte $18, $5F, $1D, $11, $0E, $5F, $1D, $1B	; Plane 1
	.byte $0A, $1F, $0E, $15, $0E, $1B, $53, $1C	; Plane 2

; monsters_030 (ID: 30)
	.byte $5F, $2C, $17, $17, $47, $FD, $35, $18	; Plane 1
	.byte $18, $16, $5F, $0A, $17, $0D, $5F, $0B	; Plane 2

; monsters_031 (ID: 31)
	.byte $18, $0A, $1B, $0D, $5F, $12, $1C, $5F	; Plane 1
	.byte $F5, $5F, $2A, $32, $2F, $27, $5F, $19	; Plane 2

; monsters_032 (ID: 32)
	.byte $0E, $1B, $5F, $17, $12, $10, $11, $1D	; Plane 1
	.byte $47, $FD, $27, $18, $1C, $1D, $5F, $1D	; Plane 2

; monsters_033 (ID: 33)
	.byte $11, $18, $1E, $5F, $20, $0A, $17, $1D	; Plane 1
	.byte $5F, $0A, $5F, $1B, $18, $18, $16, $4B	; Plane 2

; monsters_034 (ID: 34)
	.byte $40, $FD, $FC, $50, $24, $15, $15, $5F	; Plane 1
	.byte $1D, $11, $0E, $5F, $0B, $0E, $1C, $1D	; Plane 2

; monsters_035 (ID: 35)
	.byte $5F, $1D, $18, $5F, $1D, $11, $0E, $0E	; Plane 1
	.byte $52, $FC, $50, $37, $11, $0E, $1B, $0E	; Plane 2

; monsters_036 (ID: 36)
	.byte $5F, $0A, $1B, $0E, $5F, $17, $18, $5F	; Plane 1
	.byte $1C, $1D, $0A, $12, $1B, $1C, $5F, $11	; Plane 2

; monsters_037 (ID: 37)
	.byte $0E, $1B, $0E, $52, $FC, $50, $37, $11	; Plane 1
	.byte $18, $1E, $5F, $0C, $0A, $17, $17, $18	; Plane 2

; monsters_038 (ID: 38)
	.byte $1D, $5F, $0E, $17, $1D, $0E, $1B, $5F	; Plane 1
	.byte $11, $0E, $1B, $0E, $52, $FC, $50, $37	; Plane 2

; monsters_039 (ID: 39)
	.byte $11, $0E, $1B, $0E, $5F, $12, $1C, $5F	; Plane 1
	.byte $17, $18, $5F, $18, $17, $0E, $5F, $1D	; Plane 2

; monsters_040 (ID: 40)
	.byte $11, $0E, $1B, $0E, $52, $FC, $50, $2C	; Plane 1
	.byte $5F, $1D, $11, $0A, $17, $14, $5F, $1D	; Plane 2

; monsters_041 (ID: 41)
	.byte $11, $0E, $0E, $47, $FD, $3A, $18, $17	; Plane 1
	.byte $53, $1D, $5F, $1D, $11, $18, $1E, $5F	; Plane 2

; monsters_042 (ID: 42)
	.byte $0B, $1E, $22, $5F, $18, $17, $0E, $5F	; Plane 1
	.byte $16, $18, $1B, $0E, $5F, $0B, $18, $1D	; Plane 2

; monsters_043 (ID: 43)
	.byte $1D, $15, $0E, $4B, $40, $FD, $FC, $50	; Plane 1
	.byte $3A, $12, $15, $15, $5F, $1D, $11, $18	; Plane 2

; monsters_044 (ID: 44)
	.byte $1E, $5F, $0B, $1E, $22, $5F, $1C, $18	; Plane 1
	.byte $16, $0E, $5F, $29, $0A, $12, $1B, $22	; Plane 2

; monsters_045 (ID: 45)
	.byte $5F, $3A, $0A, $1D, $0E, $1B, $5F, $0F	; Plane 1
	.byte $18, $1B, $5F, $03, $08, $5F, $2A, $32	; Plane 2

; monsters_046 (ID: 46)
	.byte $2F, $27, $5F, $1D, $18, $5F, $14, $0E	; Plane 1
	.byte $0E, $19, $5F, $1D, $11, $0E, $5F, $27	; Plane 2

; monsters_047 (ID: 47)
	.byte $1B, $0A, $10, $18, $17, $15, $18, $1B	; Plane 1
	.byte $0D, $53, $1C, $5F, $16, $12, $17, $12	; Plane 2

; monsters_048 (ID: 48)
	.byte $18, $17, $1C, $5F, $0A, $20, $0A, $22	; Plane 1
	.byte $4B, $40, $FD, $FC, $50, $2C, $5F, $20	; Plane 2

; monsters_049 (ID: 49)
	.byte $12, $15, $15, $5F, $1C, $0E, $0E, $5F	; Plane 1
	.byte $1D, $11, $0E, $0E, $5F, $15, $0A, $1D	; Plane 2

; monsters_050 (ID: 50)
	.byte $0E, $1B, $52, $FC, $50, $37, $11, $18	; Plane 1
	.byte $1E, $5F, $11, $0A, $1C, $1D, $5F, $17	; Plane 2

; monsters_051 (ID: 51)
	.byte $18, $1D, $5F, $0E, $17, $18, $1E, $10	; Plane 1
	.byte $11, $5F, $16, $18, $17, $0E, $22, $52	; Plane 2

; monsters_052 (ID: 52)
	.byte $FB, $FC, $50, $2C, $5F, $0A, $16, $5F	; Plane 1
	.byte $1C, $18, $1B, $1B, $22, $48, $5F, $0B	; Plane 2

; monsters_053 (ID: 53)
	.byte $1E, $1D, $5F, $2C, $5F, $0C, $0A, $17	; Plane 1
	.byte $17, $18, $1D, $5F, $1C, $0E, $15, $15	; Plane 2

; monsters_054 (ID: 54)
	.byte $5F, $1D, $11, $0E, $0E, $5F, $0A, $17	; Plane 1
	.byte $22, $16, $18, $1B, $0E, $52, $FC, $50	; Plane 2

; monsters_055 (ID: 55)
	.byte $2B, $0E, $1B, $0E, $48, $1D, $0A, $14	; Plane 1
	.byte $0E, $5F, $1D, $11, $12, $1C, $5F, $14	; Plane 2

; monsters_056 (ID: 56)
	.byte $0E, $22, $47, $FD, $27, $18, $1C, $1D	; Plane 1
	.byte $5F, $1D, $11, $18, $1E, $5F, $20, $12	; Plane 2

; monsters_057 (ID: 57)
	.byte $1C, $11, $5F, $1D, $18, $5F, $19, $1E	; Plane 1
	.byte $1B, $0C, $11, $0A, $1C, $0E, $5F, $16	; Plane 2

; monsters_058 (ID: 58)
	.byte $18, $1B, $0E, $4B, $40, $FD, $FC, $50	; Plane 1
	.byte $30, $0A, $10, $12, $0C, $5F, $14, $0E	; Plane 2

; monsters_059 (ID: 59)
	.byte $22, $1C, $4C, $FD, $37, $11, $0E, $22	; Plane 1
	.byte $5F, $20, $12, $15, $15, $5F, $1E, $17	; Plane 2

; monsters_060 (ID: 60)
	.byte $15, $18, $0C, $14, $5F, $0A, $17, $22	; Plane 1
	.byte $5F, $0D, $18, $18, $1B, $47, $FD, $27	; Plane 2

; monsters_061 (ID: 61)
	.byte $18, $1C, $1D, $5F, $1D, $11, $18, $1E	; Plane 1
	.byte $5F, $20, $12, $1C, $11, $5F, $1D, $18	; Plane 2

; monsters_062 (ID: 62)
	.byte $5F, $19, $1E, $1B, $0C, $11, $0A, $1C	; Plane 1
	.byte $0E, $5F, $18, $17, $0E, $5F, $0F, $18	; Plane 2

; monsters_063 (ID: 63)
	.byte $1B, $5F, $F5, $5F, $2A, $32, $2F, $27	; Plane 1
	.byte $4B, $40, $FD, $FC, $50, $2C, $5F, $0A	; Plane 2

; monsters_064 (ID: 64)
	.byte $16, $5F, $1C, $18, $1B, $1B, $22, $52	; Plane 1
	.byte $FB, $FC, $24, $5F, $0C, $1E, $1B, $1C	; Plane 2

; monsters_065 (ID: 65)
	.byte $0E, $5F, $12, $1C, $5F, $1E, $19, $18	; Plane 1
	.byte $17, $5F, $1D, $11, $22, $5F, $0B, $18	; Plane 2

; monsters_066 (ID: 66)
	.byte $0D, $22, $47, $FB, $FC, $50, $37, $11	; Plane 1
	.byte $18, $1E, $5F, $11, $0A, $1C, $1D, $5F	; Plane 2

; monsters_067 (ID: 67)
	.byte $17, $18, $5F, $19, $18, $1C, $1C, $0E	; Plane 1
	.byte $1C, $1C, $12, $18, $17, $1C, $52, $FC	; Plane 2

; monsters_068 (ID: 68)
	.byte $50, $3A, $12, $15, $1D, $5F, $1D, $11	; Plane 1
	.byte $18, $1E, $5F, $1C, $0E, $15, $15, $5F	; Plane 2

; monsters_069 (ID: 69)
	.byte $0A, $17, $22, $1D, $11, $12, $17, $10	; Plane 1
	.byte $5F, $0E, $15, $1C, $0E, $4B, $40, $FD	; Plane 2

; monsters_070 (ID: 70)
	.byte $FC, $50, $2C, $5F, $0C, $0A, $17, $17	; Plane 1
	.byte $18, $1D, $5F, $0B, $1E, $22, $5F, $12	; Plane 2

; monsters_071 (ID: 71)
	.byte $1D, $52, $FC, $50, $37, $11, $18, $1E	; Plane 1
	.byte $5F, $1C, $0A, $12, $0D, $5F, $1D, $11	; Plane 2

; monsters_072 (ID: 72)
	.byte $0E, $5F, $F7, $47, $FD, $2C, $5F, $20	; Plane 1
	.byte $12, $15, $15, $5F, $0B, $1E, $22, $5F	; Plane 2

; monsters_073 (ID: 73)
	.byte $1D, $11, $22, $5F, $F7, $5F, $0F, $18	; Plane 1
	.byte $1B, $5F, $F5, $5F, $2A, $32, $2F, $27	; Plane 2

; monsters_074 (ID: 74)
	.byte $47, $FD, $2C, $1C, $5F, $1D, $11, $0A	; Plane 1
	.byte $1D, $5F, $0A, $15, $15, $5F, $1B, $12	; Plane 2

; monsters_075 (ID: 75)
	.byte $10, $11, $1D, $4B, $40, $FD, $FC, $50	; Plane 1
	.byte $3A, $11, $0A, $1D, $5F, $0A, $1B, $1D	; Plane 2

; monsters_076 (ID: 76)
	.byte $5F, $1D, $11, $18, $1E, $5F, $1C, $0E	; Plane 1
	.byte $15, $15, $12, $17, $10, $4B, $40, $FD	; Plane 2

; monsters_077 (ID: 77)
	.byte $FC, $50, $2C, $5F, $20, $12, $15, $15	; Plane 1
	.byte $5F, $0B, $0E, $5F, $20, $0A, $12, $1D	; Plane 2

; monsters_078 (ID: 78)
	.byte $12, $17, $10, $5F, $0F, $18, $1B, $5F	; Plane 1
	.byte $1D, $11, $22, $5F, $17, $0E, $21, $1D	; Plane 2

; monsters_079 (ID: 79)
	.byte $5F, $1F, $12, $1C, $12, $1D, $52, $FC	; Plane 1
	.byte $50, $27, $18, $1C, $1D, $5F, $1D, $11	; Plane 2

; npcs_080 (ID: 80)
	.byte $18, $1E, $5F, $20, $0A, $17, $1D, $5F	; Plane 1
	.byte $0A, $17, $22, $1D, $11, $12, $17, $10	; Plane 2

; npcs_081 (ID: 81)
	.byte $5F, $0E, $15, $1C, $0E, $4B, $40, $FD	; Plane 1
	.byte $FC, $50, $37, $11, $18, $1E, $5F, $0C	; Plane 2

; npcs_082 (ID: 82)
	.byte $0A, $17, $17, $18, $1D, $5F, $11, $18	; Plane 1
	.byte $15, $0D, $5F, $16, $18, $1B, $0E, $5F	; Plane 2

; npcs_083 (ID: 83)
	.byte $2B, $0E, $1B, $0B, $1C, $52, $FB, $FC	; Plane 1
	.byte $50, $37, $11, $18, $1E, $5F, $0C, $0A	; Plane 2

; npcs_084 (ID: 84)
	.byte $17, $17, $18, $1D, $5F, $0C, $0A, $1B	; Plane 1
	.byte $1B, $22, $5F, $0A, $17, $22, $16, $18	; Plane 2

; npcs_085 (ID: 85)
	.byte $1B, $0E, $52, $FB, $FC, $50, $37, $11	; Plane 1
	.byte $18, $1E, $5F, $11, $0A, $1C, $1D, $5F	; Plane 2

; npcs_086 (ID: 86)
	.byte $17, $18, $1D, $5F, $0E, $17, $18, $1E	; Plane 1
	.byte $10, $11, $5F, $16, $18, $17, $0E, $22	; Plane 2

; npcs_087 (ID: 87)
	.byte $52, $FB, $FC, $50, $37, $11, $0E, $5F	; Plane 1
	.byte $F7, $4B, $FD, $37, $11, $0A, $17, $14	; Plane 2

; npcs_088 (ID: 88)
	.byte $5F, $22, $18, $1E, $5F, $1F, $0E, $1B	; Plane 1
	.byte $22, $5F, $16, $1E, $0C, $11, $52, $FB	; Plane 2

; npcs_089 (ID: 89)
	.byte $FC, $50, $3A, $11, $0A, $1D, $5F, $0D	; Plane 1
	.byte $18, $1C, $1D, $5F, $1D, $11, $18, $1E	; Plane 2

; npcs_090 (ID: 90)
	.byte $5F, $20, $0A, $17, $1D, $4B, $40, $FD	; Plane 1
	.byte $FC, $50, $3A, $0E, $15, $0C, $18, $16	; Plane 2

; npcs_091 (ID: 91)
	.byte $0E, $47, $FD, $3A, $0E, $5F, $0D, $0E	; Plane 1
	.byte $0A, $15, $5F, $12, $17, $5F, $1D, $18	; Plane 2

; npcs_092 (ID: 92)
	.byte $18, $15, $1C, $47, $FD, $3A, $11, $0A	; Plane 1
	.byte $1D, $5F, $0C, $0A, $17, $5F, $2C, $5F	; Plane 2

; npcs_093 (ID: 93)
	.byte $0D, $18, $5F, $0F, $18, $1B, $5F, $1D	; Plane 1
	.byte $11, $0E, $0E, $4B, $40, $FD, $FC, $50	; Plane 2

; npcs_094 (ID: 94)
	.byte $32, $11, $48, $5F, $22, $0E, $1C, $4B	; Plane 1
	.byte $FD, $37, $11, $0A, $1D, $53, $1C, $5F	; Plane 2

; npcs_095 (ID: 95)
	.byte $1D, $18, $18, $5F, $0B, $0A, $0D, $52	; Plane 1
	.byte $FB, $FC, $50, $2C, $1C, $5F, $1D, $11	; Plane 2

; npcs_096 (ID: 96)
	.byte $0A, $1D, $5F, $32, $14, $0A, $22, $47	; Plane 1
	.byte $4B, $40, $FD, $57, $FC, $50, $3A, $0E	; Plane 2

; npcs_097 (ID: 97)
	.byte $5F, $0D, $0E, $0A, $15, $5F, $12, $17	; Plane 1
	.byte $5F, $20, $0E, $0A, $19, $18, $17, $1C	; Plane 2

; npcs_098 (ID: 98)
	.byte $5F, $0A, $17, $0D, $5F, $0A, $1B, $16	; Plane 1
	.byte $18, $1B, $47, $FD, $27, $18, $1C, $1D	; Plane 2

; npcs_099 (ID: 99)
	.byte $5F, $1D, $11, $18, $1E, $5F, $20, $12	; Plane 1
	.byte $1C, $11, $5F, $1D, $18, $5F, $0B, $1E	; Plane 2

; npcs_100 (ID: 100)
	.byte $22, $5F, $0A, $17, $22, $1D, $11, $12	; Plane 1
	.byte $17, $10, $5F, $1D, $18, $0D, $0A, $22	; Plane 2

; npcs_101 (ID: 101)
	.byte $4B, $40, $FD, $FC, $50, $37, $11, $0E	; Plane 1
	.byte $5F, $F7, $4B, $40, $FB, $FC, $50, $37	; Plane 2

; npcs_102 (ID: 102)
	.byte $11, $0E, $17, $5F, $2C, $5F, $20, $12	; Plane 1
	.byte $15, $15, $5F, $0B, $1E, $22, $5F, $1D	; Plane 2

; npcs_103 (ID: 103)
	.byte $11, $22, $5F, $F7, $5F, $0F, $18, $1B	; Plane 1
	.byte $5F, $F5, $5F, $2A, $32, $2F, $27, $52	; Plane 2

; npcs_104 (ID: 104)
	.byte $FB, $FC, $50, $36, $18, $1B, $1B, $22	; Plane 1
	.byte $47, $FD, $37, $11, $18, $1E, $5F, $11	; Plane 2

; npcs_105 (ID: 105)
	.byte $0A, $1C, $1D, $5F, $17, $18, $1D, $5F	; Plane 1
	.byte $0E, $17, $18, $1E, $10, $11, $5F, $16	; Plane 2

; npcs_106 (ID: 106)
	.byte $18, $17, $0E, $22, $52, $FB, $FC, $50	; Plane 1
	.byte $27, $18, $1C, $1D, $5F, $1D, $11, $18	; Plane 2

; npcs_107 (ID: 107)
	.byte $1E, $5F, $20, $12, $1C, $11, $5F, $1D	; Plane 1
	.byte $18, $5F, $0B, $1E, $22, $5F, $0A, $17	; Plane 2

; npcs_108 (ID: 108)
	.byte $22, $1D, $11, $12, $17, $10, $5F, $16	; Plane 1
	.byte $18, $1B, $0E, $4B, $40, $FD, $FC, $50	; Plane 2

; npcs_109 (ID: 109)
	.byte $3A, $11, $0A, $1D, $5F, $0D, $18, $1C	; Plane 1
	.byte $1D, $5F, $1D, $11, $18, $1E, $5F, $20	; Plane 2

; npcs_110 (ID: 110)
	.byte $12, $1C, $11, $5F, $1D, $18, $5F, $0B	; Plane 1
	.byte $1E, $22, $4B, $40, $FD, $FC, $50, $2C	; Plane 2

; npcs_111 (ID: 111)
	.byte $5F, $1D, $11, $0A, $17, $14, $5F, $1D	; Plane 1
	.byte $11, $0E, $0E, $52, $FD, $FC, $50, $33	; Plane 2

; items_112 (ID: 112)
	.byte $15, $0E, $0A, $1C, $0E, $48, $5F, $0C	; Plane 1
	.byte $18, $16, $0E, $5F, $0A, $10, $0A, $12	; Plane 2

; items_113 (ID: 113)
	.byte $17, $52, $FC, $F8, $5F, $0C, $11, $0A	; Plane 1
	.byte $17, $1D, $0E, $0D, $5F, $1D, $11, $0E	; Plane 2

; items_114 (ID: 114)
	.byte $5F, $1C, $19, $0E, $15, $15, $5F, $18	; Plane 1
	.byte $0F, $5F, $F6, $47, $FC, $F8, $5F, $0C	; Plane 2

; items_115 (ID: 115)
	.byte $0A, $17, $17, $18, $1D, $5F, $22, $0E	; Plane 1
	.byte $1D, $5F, $1E, $1C, $0E, $5F, $1D, $11	; Plane 2

; items_116 (ID: 116)
	.byte $0E, $5F, $1C, $19, $0E, $15, $15, $47	; Plane 1
	.byte $FC, $37, $11, $22, $5F, $30, $33, $5F	; Plane 2

; items_117 (ID: 117)
	.byte $12, $1C, $5F, $1D, $18, $18, $5F, $15	; Plane 1
	.byte $18, $20, $47, $FC, $60, $FD, $25, $1E	; Plane 2

; items_118 (ID: 118)
	.byte $1D, $5F, $17, $18, $1D, $11, $12, $17	; Plane 1
	.byte $10, $5F, $11, $0A, $19, $19, $0E, $17	; Plane 2

; items_119 (ID: 119)
	.byte $0E, $0D, $47, $FC, $35, $28, $33, $28	; Plane 1
	.byte $2F, $5F, $11, $0A, $1C, $5F, $15, $18	; Plane 2

; items_120 (ID: 120)
	.byte $1C, $1D, $5F, $12, $1D, $1C, $5F, $0E	; Plane 1
	.byte $0F, $0F, $0E, $0C, $1D, $47, $FC, $24	; Plane 2

; items_121 (ID: 121)
	.byte $5F, $1D, $18, $1B, $0C, $11, $5F, $0C	; Plane 1
	.byte $0A, $17, $5F, $0B, $0E, $5F, $1E, $1C	; Plane 2

; items_122 (ID: 122)
	.byte $0E, $0D, $5F, $18, $17, $15, $22, $5F	; Plane 1
	.byte $12, $17, $5F, $0D, $0A, $1B, $14, $5F	; Plane 2

; items_123 (ID: 123)
	.byte $19, $15, $0A, $0C, $0E, $1C, $47, $FC	; Plane 1
	.byte $F8, $5F, $1C, $19, $1B, $12, $17, $14	; Plane 2

; items_124 (ID: 124)
	.byte $15, $0E, $0D, $5F, $1D, $11, $0E, $5F	; Plane 1
	.byte $29, $0A, $12, $1B, $22, $5F, $3A, $0A	; Plane 2

; items_125 (ID: 125)
	.byte $1D, $0E, $1B, $5F, $18, $1F, $0E, $1B	; Plane 1
	.byte $5F, $11, $12, $1C, $5F, $0B, $18, $0D	; Plane 2

; items_126 (ID: 126)
	.byte $22, $47, $FC, $37, $11, $0E, $5F, $29	; Plane 1
	.byte $0A, $12, $1B, $22, $5F, $3A, $0A, $1D	; Plane 2

; items_127 (ID: 127)
	.byte $0E, $1B, $5F, $11, $0A, $1C, $5F, $15	; Plane 1
	.byte $18, $1C, $1D, $5F, $12, $1D, $1C, $5F	; Plane 2

; ui_128 (ID: 128)
	.byte $0E, $0F, $0F, $0E, $0C, $1D, $47, $FC	; Plane 1
	.byte $37, $11, $0E, $5F, $3A, $12, $17, $10	; Plane 2

; ui_129 (ID: 129)
	.byte $1C, $5F, $18, $0F, $5F, $1D, $11, $0E	; Plane 1
	.byte $5F, $3A, $22, $1F, $0E, $1B, $17, $5F	; Plane 2

; ui_130 (ID: 130)
	.byte $0C, $0A, $17, $17, $18, $1D, $5F, $0B	; Plane 1
	.byte $0E, $5F, $1E, $1C, $0E, $0D, $5F, $11	; Plane 2

; ui_131 (ID: 131)
	.byte $0E, $1B, $0E, $47, $FC, $F8, $5F, $1D	; Plane 1
	.byte $11, $1B, $0E, $20, $5F, $37, $11, $0E	; Plane 2

; ui_132 (ID: 132)
	.byte $5F, $3A, $12, $17, $10, $1C, $5F, $18	; Plane 1
	.byte $0F, $5F, $1D, $11, $0E, $5F, $3A, $22	; Plane 2

; ui_133 (ID: 133)
	.byte $1F, $0E, $1B, $17, $5F, $1E, $19, $5F	; Plane 1
	.byte $12, $17, $1D, $18, $5F, $1D, $11, $0E	; Plane 2

; ui_134 (ID: 134)
	.byte $5F, $1C, $14, $22, $47, $FC, $F8, $5F	; Plane 1
	.byte $0D, $18, $17, $17, $0E, $0D, $5F, $1D	; Plane 2

; ui_135 (ID: 135)
	.byte $11, $0E, $5F, $1C, $0C, $0A, $15, $0E	; Plane 1
	.byte $5F, $18, $0F, $5F, $1D, $11, $0E, $5F	; Plane 2

; ui_136 (ID: 136)
	.byte $0D, $1B, $0A, $10, $18, $17, $47, $FC	; Plane 1
	.byte $37, $11, $18, $1E, $5F, $0A, $1B, $1D	; Plane 2

; ui_137 (ID: 137)
	.byte $5F, $0A, $15, $1B, $0E, $0A, $0D, $22	; Plane 1
	.byte $5F, $20, $0E, $0A, $1B, $12, $17, $10	; Plane 2

; ui_138 (ID: 138)
	.byte $5F, $1D, $11, $0E, $5F, $1C, $0C, $0A	; Plane 1
	.byte $15, $0E, $5F, $18, $0F, $5F, $1D, $11	; Plane 2

; ui_139 (ID: 139)
	.byte $0E, $5F, $0D, $1B, $0A, $10, $18, $17	; Plane 1
	.byte $47, $FC, $F8, $5F, $0B, $15, $0E, $20	; Plane 2

; ui_140 (ID: 140)
	.byte $5F, $1D, $11, $0E, $5F, $29, $0A, $12	; Plane 1
	.byte $1B, $12, $0E, $1C, $53, $5F, $29, $15	; Plane 2

; ui_141 (ID: 141)
	.byte $1E, $1D, $0E, $47, $FC, $31, $18, $1D	; Plane 1
	.byte $11, $12, $17, $10, $5F, $18, $0F, $5F	; Plane 2

; ui_142 (ID: 142)
	.byte $1E, $1C, $0E, $5F, $11, $0A, $1C, $5F	; Plane 1
	.byte $22, $0E, $1D, $5F, $0B, $0E, $0E, $17	; Plane 2

; ui_143 (ID: 143)
	.byte $5F, $10, $12, $1F, $0E, $17, $5F, $1D	; Plane 1
	.byte $18, $5F, $1D, $11, $0E, $0E, $47, $FC	; Plane 2