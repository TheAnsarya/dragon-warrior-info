; Dragon Warrior Shop Data
; Generated from edited shop data

.include "Dragon_Warrior_Defines.asm"

.segment "ShopData"

ShopInventories:

; Koll Weapons & Armor (ID: 0)
Shop_00:
	.byte $08				; Item count
	.byte $60, $62, $35, $55, $14, $19, $64, $37

; Brecconary Weapons & Armor (ID: 1)
Shop_01:
	.byte $07				; Item count
	.byte $62, $35, $55, $14, $19, $64, $37
	.word $0068			 ; Inn price

; Garinham Weapons & Armor (ID: 2)
Shop_02:
	.byte $03				; Item count
	.byte $19, $64, $37
	.word $0001			 ; Inn price

; Cantlin Weapons & Armor 1 (ID: 3)
Shop_03:
	.byte $00				; Item count

; Cantlin Weapons & Armor 2 (ID: 4)
Shop_04:
	.byte $00				; Item count

; Cantlin Weapons & Armor 3 (ID: 5)
Shop_05:
	.byte $00				; Item count

; Rimuldar Weapons & Armor (ID: 6)
Shop_06:
	.byte $00				; Item count

; Koll Item Shop (ID: 7)
Shop_07:
	.byte $00				; Item count

; Brecconary Item Shop (ID: 8)
Shop_08:
	.byte $00				; Item count

; Garinham Item Shop (ID: 9)
Shop_09:
	.byte $00				; Item count

; Cantlin Item Shop 1 (ID: 10)
Shop_10:
	.byte $00				; Item count

; Cantlin Item Shop 2 (ID: 11)
Shop_11:
	.byte $04				; Item count
	.byte $11, $13, $16, $15