; Dragon Warrior Spell Data
; Generated from edited spell data

.include "Dragon_Warrior_Defines.asm"

.segment "SpellData"

; Spell MP Cost Table
SpellMPCosts:
	.byte $04				; HEAL: 4 MP
	.byte $02				; HURT: 2 MP
	.byte $02				; SLEEP: 2 MP
	.byte $03				; RADIANT: 3 MP
	.byte $02				; STOPSPELL: 2 MP
	.byte $06				; OUTSIDE: 6 MP
	.byte $08				; RETURN: 8 MP
	.byte $02				; REPEL: 2 MP
	.byte $0A				; HEALMORE: 10 MP
	.byte $05				; HURTMORE: 5 MP

; Spell Effect Types
SpellEffectTypes:
	.byte $00				; HEAL: heal
	.byte $01				; HURT: damage
	.byte $02				; SLEEP: status
	.byte $01				; RADIANT: damage
	.byte $02				; STOPSPELL: status
	.byte $03				; OUTSIDE: teleport
	.byte $03				; RETURN: teleport
	.byte $04				; REPEL: field
	.byte $00				; HEALMORE: heal
	.byte $01				; HURTMORE: damage