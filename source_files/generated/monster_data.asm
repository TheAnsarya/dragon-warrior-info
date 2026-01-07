;====================================================================================================
; Dragon Warrior Monster Data Tables
; Generated from assets/json/monsters_verified.json
; This file is auto-generated - do not edit directly
;====================================================================================================

; Monster count: 40

;----------------------------------------------------------------------------------------------------
; Monster Statistics Table
; Format: HP (2), STR, AGI, MaxDmg, Dodge, SleepRes, HurtRes, XP (2), Gold (2)
;----------------------------------------------------------------------------------------------------

MonsterStatsTable:

; Monster 00: Slime
Monster00_Stats:
	.byte $03, $00		; HP: 3
	.byte $05			; Strength: 5
	.byte $0F			; Agility: 15
	.byte $05			; Max Damage: 5
	.byte $07			; Dodge Rate: 7
	.byte $01			; Sleep Resistance: 1
	.byte $01			; Hurt Resistance: 1
	.byte $01, $00		; Experience: 1
	.byte $02, $00		; Gold: 2

; Monster 01: Red Slime
Monster01_Stats:
	.byte $04, $00		; HP: 4
	.byte $07			; Strength: 7
	.byte $0F			; Agility: 15
	.byte $07			; Max Damage: 7
	.byte $07			; Dodge Rate: 7
	.byte $01			; Sleep Resistance: 1
	.byte $01			; Hurt Resistance: 1
	.byte $01, $00		; Experience: 1
	.byte $03, $00		; Gold: 3

; Monster 02: Drakee
Monster02_Stats:
	.byte $06, $00		; HP: 6
	.byte $09			; Strength: 9
	.byte $0F			; Agility: 15
	.byte $09			; Max Damage: 9
	.byte $07			; Dodge Rate: 7
	.byte $01			; Sleep Resistance: 1
	.byte $01			; Hurt Resistance: 1
	.byte $02, $00		; Experience: 2
	.byte $03, $00		; Gold: 3

; Monster 03: Ghost
Monster03_Stats:
	.byte $07, $00		; HP: 7
	.byte $0B			; Strength: 11
	.byte $0F			; Agility: 15
	.byte $0B			; Max Damage: 11
	.byte $07			; Dodge Rate: 7
	.byte $04			; Sleep Resistance: 4
	.byte $04			; Hurt Resistance: 4
	.byte $03, $00		; Experience: 3
	.byte $05, $00		; Gold: 5

; Monster 04: Magician
Monster04_Stats:
	.byte $0D, $00		; HP: 13
	.byte $0B			; Strength: 11
	.byte $00			; Agility: 0
	.byte $0B			; Max Damage: 11
	.byte $00			; Dodge Rate: 0
	.byte $01			; Sleep Resistance: 1
	.byte $01			; Hurt Resistance: 1
	.byte $04, $00		; Experience: 4
	.byte $0C, $00		; Gold: 12

; Monster 05: Magidrakee
Monster05_Stats:
	.byte $0F, $00		; HP: 15
	.byte $0E			; Strength: 14
	.byte $00			; Agility: 0
	.byte $0E			; Max Damage: 14
	.byte $00			; Dodge Rate: 0
	.byte $01			; Sleep Resistance: 1
	.byte $01			; Hurt Resistance: 1
	.byte $05, $00		; Experience: 5
	.byte $0C, $00		; Gold: 12

; Monster 06: Scorpion
Monster06_Stats:
	.byte $14, $00		; HP: 20
	.byte $12			; Strength: 18
	.byte $0F			; Agility: 15
	.byte $12			; Max Damage: 18
	.byte $07			; Dodge Rate: 7
	.byte $01			; Sleep Resistance: 1
	.byte $01			; Hurt Resistance: 1
	.byte $06, $00		; Experience: 6
	.byte $10, $00		; Gold: 16

; Monster 07: Druin
Monster07_Stats:
	.byte $16, $00		; HP: 22
	.byte $14			; Strength: 20
	.byte $0F			; Agility: 15
	.byte $14			; Max Damage: 20
	.byte $07			; Dodge Rate: 7
	.byte $02			; Sleep Resistance: 2
	.byte $02			; Hurt Resistance: 2
	.byte $07, $00		; Experience: 7
	.byte $10, $00		; Gold: 16

; Monster 08: Poltergeist
Monster08_Stats:
	.byte $17, $00		; HP: 23
	.byte $12			; Strength: 18
	.byte $00			; Agility: 0
	.byte $12			; Max Damage: 18
	.byte $00			; Dodge Rate: 0
	.byte $06			; Sleep Resistance: 6
	.byte $06			; Hurt Resistance: 6
	.byte $08, $00		; Experience: 8
	.byte $12, $00		; Gold: 18

; Monster 09: Droll
Monster09_Stats:
	.byte $19, $00		; HP: 25
	.byte $18			; Strength: 24
	.byte $0E			; Agility: 14
	.byte $18			; Max Damage: 24
	.byte $07			; Dodge Rate: 7
	.byte $02			; Sleep Resistance: 2
	.byte $02			; Hurt Resistance: 2
	.byte $0A, $00		; Experience: 10
	.byte $19, $00		; Gold: 25

; Monster 10: Drakeema
Monster10_Stats:
	.byte $14, $00		; HP: 20
	.byte $16			; Strength: 22
	.byte $20			; Agility: 32
	.byte $16			; Max Damage: 22
	.byte $10			; Dodge Rate: 16
	.byte $06			; Sleep Resistance: 6
	.byte $06			; Hurt Resistance: 6
	.byte $0B, $00		; Experience: 11
	.byte $14, $00		; Gold: 20

; Monster 11: Skeleton
Monster11_Stats:
	.byte $1E, $00		; HP: 30
	.byte $1C			; Strength: 28
	.byte $0F			; Agility: 15
	.byte $1C			; Max Damage: 28
	.byte $07			; Dodge Rate: 7
	.byte $04			; Sleep Resistance: 4
	.byte $04			; Hurt Resistance: 4
	.byte $0B, $00		; Experience: 11
	.byte $1E, $00		; Gold: 30

; Monster 12: Warlock
Monster12_Stats:
	.byte $1E, $00		; HP: 30
	.byte $1C			; Strength: 28
	.byte $31			; Agility: 49
	.byte $1C			; Max Damage: 28
	.byte $18			; Dodge Rate: 24
	.byte $02			; Sleep Resistance: 2
	.byte $02			; Hurt Resistance: 2
	.byte $0D, $00		; Experience: 13
	.byte $23, $00		; Gold: 35

; Monster 13: Metal Slime
Monster13_Stats:
	.byte $16, $00		; HP: 22
	.byte $24			; Strength: 36
	.byte $0F			; Agility: 15
	.byte $24			; Max Damage: 36
	.byte $07			; Dodge Rate: 7
	.byte $02			; Sleep Resistance: 2
	.byte $02			; Hurt Resistance: 2
	.byte $0E, $00		; Experience: 14
	.byte $28, $00		; Gold: 40

; Monster 14: Wolf
Monster14_Stats:
	.byte $22, $00		; HP: 34
	.byte $28			; Strength: 40
	.byte $1F			; Agility: 31
	.byte $28			; Max Damage: 40
	.byte $0F			; Dodge Rate: 15
	.byte $02			; Sleep Resistance: 2
	.byte $02			; Hurt Resistance: 2
	.byte $10, $00		; Experience: 16
	.byte $32, $00		; Gold: 50

; Monster 15: Wraith
Monster15_Stats:
	.byte $24, $00		; HP: 36
	.byte $2C			; Strength: 44
	.byte $70			; Agility: 112
	.byte $2C			; Max Damage: 44
	.byte $38			; Dodge Rate: 56
	.byte $04			; Sleep Resistance: 4
	.byte $04			; Hurt Resistance: 4
	.byte $11, $00		; Experience: 17
	.byte $3C, $00		; Gold: 60

; Monster 16: Metal Scorpion
Monster16_Stats:
	.byte $04, $00		; HP: 4
	.byte $0A			; Strength: 10
	.byte $FF			; Agility: 255
	.byte $0A			; Max Damage: 10
	.byte $7F			; Dodge Rate: 127
	.byte $F1			; Sleep Resistance: 241
	.byte $F1			; Hurt Resistance: 241
	.byte $73, $00		; Experience: 115
	.byte $06, $00		; Gold: 6

; Monster 17: Orc
Monster17_Stats:
	.byte $24, $00		; HP: 36
	.byte $28			; Strength: 40
	.byte $31			; Agility: 49
	.byte $28			; Max Damage: 40
	.byte $18			; Dodge Rate: 24
	.byte $04			; Sleep Resistance: 4
	.byte $04			; Hurt Resistance: 4
	.byte $12, $00		; Experience: 18
	.byte $46, $00		; Gold: 70

; Monster 18: Specter
Monster18_Stats:
	.byte $26, $00		; HP: 38
	.byte $32			; Strength: 50
	.byte $47			; Agility: 71
	.byte $32			; Max Damage: 50
	.byte $23			; Dodge Rate: 35
	.byte $02			; Sleep Resistance: 2
	.byte $02			; Hurt Resistance: 2
	.byte $14, $00		; Experience: 20
	.byte $50, $00		; Gold: 80

; Monster 19: Wolflord
Monster19_Stats:
	.byte $23, $00		; HP: 35
	.byte $2F			; Strength: 47
	.byte $F0			; Agility: 240
	.byte $2F			; Max Damage: 47
	.byte $78			; Dodge Rate: 120
	.byte $04			; Sleep Resistance: 4
	.byte $04			; Hurt Resistance: 4
	.byte $14, $00		; Experience: 20
	.byte $55, $00		; Gold: 85

; Monster 20: Druinlord
Monster20_Stats:
	.byte $26, $00		; HP: 38
	.byte $34			; Strength: 52
	.byte $22			; Agility: 34
	.byte $34			; Max Damage: 52
	.byte $11			; Dodge Rate: 17
	.byte $01			; Sleep Resistance: 1
	.byte $01			; Hurt Resistance: 1
	.byte $16, $00		; Experience: 22
	.byte $5A, $00		; Gold: 90

; Monster 21: Drollmagi
Monster21_Stats:
	.byte $2A, $00		; HP: 42
	.byte $38			; Strength: 56
	.byte $4F			; Agility: 79
	.byte $38			; Max Damage: 56
	.byte $27			; Dodge Rate: 39
	.byte $02			; Sleep Resistance: 2
	.byte $02			; Hurt Resistance: 2
	.byte $18, $00		; Experience: 24
	.byte $64, $00		; Gold: 100

; Monster 22: Wyvern
Monster22_Stats:
	.byte $23, $00		; HP: 35
	.byte $3C			; Strength: 60
	.byte $7F			; Agility: 127
	.byte $3C			; Max Damage: 60
	.byte $3F			; Dodge Rate: 63
	.byte $02			; Sleep Resistance: 2
	.byte $02			; Hurt Resistance: 2
	.byte $1A, $00		; Experience: 26
	.byte $6E, $00		; Gold: 110

; Monster 23: Rogue Scorpion
Monster23_Stats:
	.byte $2E, $00		; HP: 46
	.byte $44			; Strength: 68
	.byte $50			; Agility: 80
	.byte $44			; Max Damage: 68
	.byte $28			; Dodge Rate: 40
	.byte $34			; Sleep Resistance: 52
	.byte $34			; Hurt Resistance: 52
	.byte $1C, $00		; Experience: 28
	.byte $78, $00		; Gold: 120

; Monster 24: Wraith Knight
Monster24_Stats:
	.byte $46, $00		; HP: 70
	.byte $78			; Strength: 120
	.byte $FF			; Agility: 255
	.byte $78			; Max Damage: 120
	.byte $7F			; Dodge Rate: 127
	.byte $F0			; Sleep Resistance: 240
	.byte $F0			; Hurt Resistance: 240
	.byte $05, $00		; Experience: 5
	.byte $0A, $00		; Gold: 10

; Monster 25: Golem
Monster25_Stats:
	.byte $32, $00		; HP: 50
	.byte $30			; Strength: 48
	.byte $DF			; Agility: 223
	.byte $30			; Max Damage: 48
	.byte $6F			; Dodge Rate: 111
	.byte $01			; Sleep Resistance: 1
	.byte $01			; Hurt Resistance: 1
	.byte $06, $00		; Experience: 6
	.byte $C8, $00		; Gold: 200

; Monster 26: Goldman
Monster26_Stats:
	.byte $37, $00		; HP: 55
	.byte $4C			; Strength: 76
	.byte $67			; Agility: 103
	.byte $4C			; Max Damage: 76
	.byte $33			; Dodge Rate: 51
	.byte $01			; Sleep Resistance: 1
	.byte $01			; Hurt Resistance: 1
	.byte $21, $00		; Experience: 33
	.byte $82, $00		; Gold: 130

; Monster 27: Knight
Monster27_Stats:
	.byte $3A, $00		; HP: 58
	.byte $4E			; Strength: 78
	.byte $20			; Agility: 32
	.byte $4E			; Max Damage: 78
	.byte $10			; Dodge Rate: 16
	.byte $02			; Sleep Resistance: 2
	.byte $02			; Hurt Resistance: 2
	.byte $22, $00		; Experience: 34
	.byte $8C, $00		; Gold: 140

; Monster 28: Magiwyvern
Monster28_Stats:
	.byte $32, $00		; HP: 50
	.byte $4F			; Strength: 79
	.byte $FF			; Agility: 255
	.byte $4F			; Max Damage: 79
	.byte $7F			; Dodge Rate: 127
	.byte $FF			; Sleep Resistance: 255
	.byte $FF			; Hurt Resistance: 255
	.byte $25, $00		; Experience: 37
	.byte $96, $00		; Gold: 150

; Monster 29: Demon Knight
Monster29_Stats:
	.byte $3C, $00		; HP: 60
	.byte $56			; Strength: 86
	.byte $7F			; Agility: 127
	.byte $56			; Max Damage: 86
	.byte $3F			; Dodge Rate: 63
	.byte $07			; Sleep Resistance: 7
	.byte $07			; Hurt Resistance: 7
	.byte $28, $00		; Experience: 40
	.byte $9B, $00		; Gold: 155

; Monster 30: Werewolf
Monster30_Stats:
	.byte $41, $00		; HP: 65
	.byte $58			; Strength: 88
	.byte $7F			; Agility: 127
	.byte $58			; Max Damage: 88
	.byte $3F			; Dodge Rate: 63
	.byte $22			; Sleep Resistance: 34
	.byte $22			; Hurt Resistance: 34
	.byte $2D, $00		; Experience: 45
	.byte $A0, $00		; Gold: 160

; Monster 31: Green Dragon
Monster31_Stats:
	.byte $41, $00		; HP: 65
	.byte $56			; Strength: 86
	.byte $80			; Agility: 128
	.byte $56			; Max Damage: 86
	.byte $40			; Dodge Rate: 64
	.byte $12			; Sleep Resistance: 18
	.byte $12			; Hurt Resistance: 18
	.byte $2B, $00		; Experience: 43
	.byte $A0, $00		; Gold: 160

; Monster 32: Starwyvern
Monster32_Stats:
	.byte $41, $00		; HP: 65
	.byte $50			; Strength: 80
	.byte $F7			; Agility: 247
	.byte $50			; Max Damage: 80
	.byte $7B			; Dodge Rate: 123
	.byte $F2			; Sleep Resistance: 242
	.byte $F2			; Hurt Resistance: 242
	.byte $32, $00		; Experience: 50
	.byte $A5, $00		; Gold: 165

; Monster 33: Wizard
Monster33_Stats:
	.byte $46, $00		; HP: 70
	.byte $5E			; Strength: 94
	.byte $F3			; Agility: 243
	.byte $5E			; Max Damage: 94
	.byte $79			; Dodge Rate: 121
	.byte $11			; Sleep Resistance: 17
	.byte $11			; Hurt Resistance: 17
	.byte $36, $00		; Experience: 54
	.byte $A5, $00		; Gold: 165

; Monster 34: Axe Knight
Monster34_Stats:
	.byte $46, $00		; HP: 70
	.byte $62			; Strength: 98
	.byte $FF			; Agility: 255
	.byte $62			; Max Damage: 98
	.byte $7F			; Dodge Rate: 127
	.byte $72			; Sleep Resistance: 114
	.byte $72			; Hurt Resistance: 114
	.byte $3C, $00		; Experience: 60
	.byte $96, $00		; Gold: 150

; Monster 35: Blue Dragon
Monster35_Stats:
	.byte $A0, $00		; HP: 160
	.byte $64			; Strength: 100
	.byte $2F			; Agility: 47
	.byte $64			; Max Damage: 100
	.byte $17			; Dodge Rate: 23
	.byte $71			; Sleep Resistance: 113
	.byte $71			; Hurt Resistance: 113
	.byte $41, $00		; Experience: 65
	.byte $8C, $00		; Gold: 140

; Monster 36: Stone Man
Monster36_Stats:
	.byte $5A, $00		; HP: 90
	.byte $69			; Strength: 105
	.byte $F7			; Agility: 247
	.byte $69			; Max Damage: 105
	.byte $7B			; Dodge Rate: 123
	.byte $12			; Sleep Resistance: 18
	.byte $12			; Hurt Resistance: 18
	.byte $46, $00		; Experience: 70
	.byte $8C, $00		; Gold: 140

; Monster 37: Armored Knight
Monster37_Stats:
	.byte $64, $00		; HP: 100
	.byte $78			; Strength: 120
	.byte $F7			; Agility: 247
	.byte $78			; Max Damage: 120
	.byte $7B			; Dodge Rate: 123
	.byte $F2			; Sleep Resistance: 242
	.byte $F2			; Hurt Resistance: 242
	.byte $64, $00		; Experience: 100
	.byte $8C, $00		; Gold: 140

; Monster 38: Red Dragon
Monster38_Stats:
	.byte $64, $00		; HP: 100
	.byte $5A			; Strength: 90
	.byte $FF			; Agility: 255
	.byte $5A			; Max Damage: 90
	.byte $7F			; Dodge Rate: 127
	.byte $F0			; Sleep Resistance: 240
	.byte $F0			; Hurt Resistance: 240
	.byte $00, $00		; Experience: 0
	.byte $00, $00		; Gold: 0

; Monster 39: Dragonlord
Monster39_Stats:
	.byte $82, $00		; HP: 130
	.byte $8C			; Strength: 140
	.byte $FF			; Agility: 255
	.byte $8C			; Max Damage: 140
	.byte $7F			; Dodge Rate: 127
	.byte $F0			; Sleep Resistance: 240
	.byte $F0			; Hurt Resistance: 240
	.byte $00, $00		; Experience: 0
	.byte $00, $00		; Gold: 0

;----------------------------------------------------------------------------------------------------
; Monster Names Table
;----------------------------------------------------------------------------------------------------

MonsterNamesTable:
	.word MonsterName00
	.word MonsterName01
	.word MonsterName02
	.word MonsterName03
	.word MonsterName04
	.word MonsterName05
	.word MonsterName06
	.word MonsterName07
	.word MonsterName08
	.word MonsterName09
	.word MonsterName10
	.word MonsterName11
	.word MonsterName12
	.word MonsterName13
	.word MonsterName14
	.word MonsterName15
	.word MonsterName16
	.word MonsterName17
	.word MonsterName18
	.word MonsterName19
	.word MonsterName20
	.word MonsterName21
	.word MonsterName22
	.word MonsterName23
	.word MonsterName24
	.word MonsterName25
	.word MonsterName26
	.word MonsterName27
	.word MonsterName28
	.word MonsterName29
	.word MonsterName30
	.word MonsterName31
	.word MonsterName32
	.word MonsterName33
	.word MonsterName34
	.word MonsterName35
	.word MonsterName36
	.word MonsterName37
	.word MonsterName38
	.word MonsterName39

MonsterName00:
	.byte $36, $15, $12, $16, $0E, $fc	; "Slime"
MonsterName01:
	.byte $35, $0E, $0D, $5F, $36, $15, $12, $16, $0E, $fc	; "Red Slime"
MonsterName02:
	.byte $27, $1B, $0A, $14, $0E, $0E, $fc	; "Drakee"
MonsterName03:
	.byte $2A, $11, $18, $1C, $1D, $fc	; "Ghost"
MonsterName04:
	.byte $30, $0A, $10, $12, $0C, $12, $0A, $17, $fc	; "Magician"
MonsterName05:
	.byte $30, $0A, $10, $12, $0D, $1B, $0A, $14, $0E, $0E, $fc	; "Magidrakee"
MonsterName06:
	.byte $36, $0C, $18, $1B, $19, $12, $18, $17, $fc	; "Scorpion"
MonsterName07:
	.byte $27, $1B, $1E, $12, $17, $fc	; "Druin"
MonsterName08:
	.byte $33, $18, $15, $1D, $0E, $1B, $10, $0E, $12, $1C, $1D, $fc	; "Poltergeist"
MonsterName09:
	.byte $27, $1B, $18, $15, $15, $fc	; "Droll"
MonsterName10:
	.byte $27, $1B, $0A, $14, $0E, $0E, $16, $0A, $fc	; "Drakeema"
MonsterName11:
	.byte $36, $14, $0E, $15, $0E, $1D, $18, $17, $fc	; "Skeleton"
MonsterName12:
	.byte $3A, $0A, $1B, $15, $18, $0C, $14, $fc	; "Warlock"
MonsterName13:
	.byte $30, $0E, $1D, $0A, $15, $5F, $36, $15, $12, $16, $0E, $fc	; "Metal Slime"
MonsterName14:
	.byte $3A, $18, $15, $0F, $fc	; "Wolf"
MonsterName15:
	.byte $3A, $1B, $0A, $12, $1D, $11, $fc	; "Wraith"
MonsterName16:
	.byte $30, $0E, $1D, $0A, $15, $5F, $36, $0C, $18, $1B, $19, $12, $18, $17, $fc	; "Metal Scorpion"
MonsterName17:
	.byte $32, $1B, $0C, $fc	; "Orc"
MonsterName18:
	.byte $36, $19, $0E, $0C, $1D, $0E, $1B, $fc	; "Specter"
MonsterName19:
	.byte $3A, $18, $15, $0F, $15, $18, $1B, $0D, $fc	; "Wolflord"
MonsterName20:
	.byte $27, $1B, $1E, $12, $17, $15, $18, $1B, $0D, $fc	; "Druinlord"
MonsterName21:
	.byte $27, $1B, $18, $15, $15, $16, $0A, $10, $12, $fc	; "Drollmagi"
MonsterName22:
	.byte $3A, $22, $1F, $0E, $1B, $17, $fc	; "Wyvern"
MonsterName23:
	.byte $35, $18, $10, $1E, $0E, $5F, $36, $0C, $18, $1B, $19, $12, $18, $17, $fc	; "Rogue Scorpion"
MonsterName24:
	.byte $3A, $1B, $0A, $12, $1D, $11, $5F, $2E, $17, $12, $10, $11, $1D, $fc	; "Wraith Knight"
MonsterName25:
	.byte $2A, $18, $15, $0E, $16, $fc	; "Golem"
MonsterName26:
	.byte $2A, $18, $15, $0D, $16, $0A, $17, $fc	; "Goldman"
MonsterName27:
	.byte $2E, $17, $12, $10, $11, $1D, $fc	; "Knight"
MonsterName28:
	.byte $30, $0A, $10, $12, $20, $22, $1F, $0E, $1B, $17, $fc	; "Magiwyvern"
MonsterName29:
	.byte $27, $0E, $16, $18, $17, $5F, $2E, $17, $12, $10, $11, $1D, $fc	; "Demon Knight"
MonsterName30:
	.byte $3A, $0E, $1B, $0E, $20, $18, $15, $0F, $fc	; "Werewolf"
MonsterName31:
	.byte $2A, $1B, $0E, $0E, $17, $5F, $27, $1B, $0A, $10, $18, $17, $fc	; "Green Dragon"
MonsterName32:
	.byte $36, $1D, $0A, $1B, $20, $22, $1F, $0E, $1B, $17, $fc	; "Starwyvern"
MonsterName33:
	.byte $3A, $12, $23, $0A, $1B, $0D, $fc	; "Wizard"
MonsterName34:
	.byte $24, $21, $0E, $5F, $2E, $17, $12, $10, $11, $1D, $fc	; "Axe Knight"
MonsterName35:
	.byte $25, $15, $1E, $0E, $5F, $27, $1B, $0A, $10, $18, $17, $fc	; "Blue Dragon"
MonsterName36:
	.byte $36, $1D, $18, $17, $0E, $5F, $30, $0A, $17, $fc	; "Stone Man"
MonsterName37:
	.byte $24, $1B, $16, $18, $1B, $0E, $0D, $5F, $2E, $17, $12, $10, $11, $1D, $fc	; "Armored Knight"
MonsterName38:
	.byte $35, $0E, $0D, $5F, $27, $1B, $0A, $10, $18, $17, $fc	; "Red Dragon"
MonsterName39:
	.byte $27, $1B, $0A, $10, $18, $17, $15, $18, $1B, $0D, $fc	; "Dragonlord"

;====================================================================================================
; End of Monster Data - 40 monsters, ~440 bytes stats
;====================================================================================================