; Dragon Warrior Shop Data
; Generated from edited shop data

.include "Dragon_Warrior_Defines.asm"

.segment "ShopData"

ShopInventories:

; Koll Weapons & Armor (ID: 0)
Shop_00:
	.byte $05				; Item count
	.byte $02, $03, $0A, $0B, $0E

; Brecconary Weapons & Armor (ID: 1)
Shop_01:
	.byte $06				; Item count
	.byte $00, $01, $02, $07, $08, $0E
	.word $0006			 ; Inn price

; Garinham Weapons & Armor (ID: 2)
Shop_02:
	.byte $07				; Item count
	.byte $01, $02, $03, $08, $09, $0A, $0F
	.word $0019			 ; Inn price

; Cantlin Weapons & Armor 1 (ID: 3)
Shop_03:
	.byte $06				; Item count
	.byte $00, $01, $02, $08, $09, $0F
	.word $0064			 ; Inn price

; Cantlin Weapons & Armor 2 (ID: 4)
Shop_04:
	.byte $04				; Item count
	.byte $03, $04, $0B, $0C
	.word $0064			 ; Inn price

; Cantlin Weapons & Armor 3 (ID: 5)
Shop_05:
	.byte $02				; Item count
	.byte $05, $10
	.word $0064			 ; Inn price

; Rimuldar Weapons & Armor (ID: 6)
Shop_06:
	.byte $06				; Item count
	.byte $02, $03, $04, $0A, $0B, $0C
	.word $0037			 ; Inn price

; Koll Item Shop (ID: 7)
Shop_07:
	.byte $04				; Item count
	.byte $11, $13, $16, $15

; Brecconary Item Shop (ID: 8)
Shop_08:
	.byte $03				; Item count
	.byte $11, $13, $16

; Garinham Item Shop (ID: 9)
Shop_09:
	.byte $03				; Item count
	.byte $11, $13, $16

; Cantlin Item Shop 1 (ID: 10)
Shop_10:
	.byte $02				; Item count
	.byte $11, $13

; Cantlin Item Shop 2 (ID: 11)
Shop_11:
	.byte $02				; Item count
	.byte $16, $15