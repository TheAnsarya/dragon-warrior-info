; Dragon Warrior Item Data
; Generated from edited JSON data

.include "Dragon_Warrior_Defines.asm"

.segment "ItemData"

; Item Statistics Table
; Format: ATK(1), DEF(1), BUY_PRICE(2), SELL_PRICE(2), FLAGS(1), TYPE(1), SPRITE(1)

; Torch (ID: 0)
Item_00_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0008				 ; Buy Price: 8
	.word $0004				; Sell Price: 4
	.byte $02							 ; Flags: Equip=False, Use=True
	.byte $03				 ; Item Type: 3
	.byte $00				 ; Sprite ID: 0

; Club (ID: 1)
Item_01_Stats:
	.byte $04			; Attack Power: 4
	.byte $00			 ; Defense Power: 0
	.word $003C				 ; Buy Price: 60
	.word $001E				; Sell Price: 30
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $00				 ; Item Type: 0
	.byte $01				 ; Sprite ID: 1

; Copper Sword (ID: 2)
Item_02_Stats:
	.byte $0A			; Attack Power: 10
	.byte $00			 ; Defense Power: 0
	.word $00B4				 ; Buy Price: 180
	.word $005A				; Sell Price: 90
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $00				 ; Item Type: 0
	.byte $02				 ; Sprite ID: 2

; Hand Axe (ID: 3)
Item_03_Stats:
	.byte $0F			; Attack Power: 15
	.byte $00			 ; Defense Power: 0
	.word $0230				 ; Buy Price: 560
	.word $0118				; Sell Price: 280
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $00				 ; Item Type: 0
	.byte $03				 ; Sprite ID: 3

; Broad Sword (ID: 4)
Item_04_Stats:
	.byte $14			; Attack Power: 20
	.byte $00			 ; Defense Power: 0
	.word $04B0				 ; Buy Price: 1200
	.word $0258				; Sell Price: 600
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $00				 ; Item Type: 0
	.byte $04				 ; Sprite ID: 4

; Flame Sword (ID: 5)
Item_05_Stats:
	.byte $1C			; Attack Power: 28
	.byte $00			 ; Defense Power: 0
	.word $2648				 ; Buy Price: 9800
	.word $1324				; Sell Price: 4900
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $00				 ; Item Type: 0
	.byte $05				 ; Sprite ID: 5

; Erdrick's Sword (ID: 6)
Item_06_Stats:
	.byte $28			; Attack Power: 40
	.byte $00			 ; Defense Power: 0
	.word $0000				 ; Buy Price: 0
	.word $0000				; Sell Price: 0
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $00				 ; Item Type: 0
	.byte $06				 ; Sprite ID: 6

; Clothes (ID: 7)
Item_07_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0014				 ; Buy Price: 20
	.word $000A				; Sell Price: 10
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $01				 ; Item Type: 1
	.byte $07				 ; Sprite ID: 7

; Leather Armor (ID: 8)
Item_08_Stats:
	.byte $00			; Attack Power: 0
	.byte $02			 ; Defense Power: 2
	.word $0046				 ; Buy Price: 70
	.word $0023				; Sell Price: 35
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $01				 ; Item Type: 1
	.byte $08				 ; Sprite ID: 8

; Chain Mail (ID: 9)
Item_09_Stats:
	.byte $00			; Attack Power: 0
	.byte $04			 ; Defense Power: 4
	.word $012C				 ; Buy Price: 300
	.word $0096				; Sell Price: 150
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $01				 ; Item Type: 1
	.byte $09				 ; Sprite ID: 9

; Half Plate (ID: 10)
Item_10_Stats:
	.byte $00			; Attack Power: 0
	.byte $0A			 ; Defense Power: 10
	.word $03E8				 ; Buy Price: 1000
	.word $01F4				; Sell Price: 500
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $01				 ; Item Type: 1
	.byte $0A				 ; Sprite ID: 10

; Full Plate (ID: 11)
Item_11_Stats:
	.byte $00			; Attack Power: 0
	.byte $10			 ; Defense Power: 16
	.word $0BB8				 ; Buy Price: 3000
	.word $05DC				; Sell Price: 1500
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $01				 ; Item Type: 1
	.byte $0B				 ; Sprite ID: 11

; Magic Armor (ID: 12)
Item_12_Stats:
	.byte $00			; Attack Power: 0
	.byte $18			 ; Defense Power: 24
	.word $1E14				 ; Buy Price: 7700
	.word $0F0A				; Sell Price: 3850
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $01				 ; Item Type: 1
	.byte $0C				 ; Sprite ID: 12

; Erdrick's Armor (ID: 13)
Item_13_Stats:
	.byte $00			; Attack Power: 0
	.byte $18			 ; Defense Power: 24
	.word $0000				 ; Buy Price: 0
	.word $0000				; Sell Price: 0
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $01				 ; Item Type: 1
	.byte $0D				 ; Sprite ID: 13

; Small Shield (ID: 14)
Item_14_Stats:
	.byte $00			; Attack Power: 0
	.byte $04			 ; Defense Power: 4
	.word $005A				 ; Buy Price: 90
	.word $002D				; Sell Price: 45
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $02				 ; Item Type: 2
	.byte $0E				 ; Sprite ID: 14

; Large Shield (ID: 15)
Item_15_Stats:
	.byte $00			; Attack Power: 0
	.byte $0A			 ; Defense Power: 10
	.word $0320				 ; Buy Price: 800
	.word $0190				; Sell Price: 400
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $02				 ; Item Type: 2
	.byte $0F				 ; Sprite ID: 15

; Silver Shield (ID: 16)
Item_16_Stats:
	.byte $00			; Attack Power: 0
	.byte $14			 ; Defense Power: 20
	.word $39D0				 ; Buy Price: 14800
	.word $1CE8				; Sell Price: 7400
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $02				 ; Item Type: 2
	.byte $10				 ; Sprite ID: 16

; Erdrick's Shield (ID: 17)
Item_17_Stats:
	.byte $00			; Attack Power: 0
	.byte $19			 ; Defense Power: 25
	.word $0000				 ; Buy Price: 0
	.word $0000				; Sell Price: 0
	.byte $01							 ; Flags: Equip=True, Use=False
	.byte $02				 ; Item Type: 2
	.byte $11				 ; Sprite ID: 17

; Herb (ID: 18)
Item_18_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0018				 ; Buy Price: 24
	.word $000C				; Sell Price: 12
	.byte $02							 ; Flags: Equip=False, Use=True
	.byte $03				 ; Item Type: 3
	.byte $12				 ; Sprite ID: 18

; Key (ID: 19)
Item_19_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0019				 ; Buy Price: 25
	.word $000C				; Sell Price: 12
	.byte $00							 ; Flags: Equip=False, Use=False
	.byte $04				 ; Item Type: 4
	.byte $13				 ; Sprite ID: 19

; Magic Key (ID: 20)
Item_20_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0035				 ; Buy Price: 53
	.word $001A				; Sell Price: 26
	.byte $00							 ; Flags: Equip=False, Use=False
	.byte $04				 ; Item Type: 4
	.byte $14				 ; Sprite ID: 20

; Erdrick's Token (ID: 21)
Item_21_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0000				 ; Buy Price: 0
	.word $0000				; Sell Price: 0
	.byte $00							 ; Flags: Equip=False, Use=False
	.byte $04				 ; Item Type: 4
	.byte $15				 ; Sprite ID: 21

; Gwaelin's Love (ID: 22)
Item_22_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0000				 ; Buy Price: 0
	.word $0000				; Sell Price: 0
	.byte $02							 ; Flags: Equip=False, Use=True
	.byte $04				 ; Item Type: 4
	.byte $16				 ; Sprite ID: 22

; Cursed Belt (ID: 23)
Item_23_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0000				 ; Buy Price: 0
	.word $0000				; Sell Price: 0
	.byte $00							 ; Flags: Equip=False, Use=False
	.byte $04				 ; Item Type: 4
	.byte $17				 ; Sprite ID: 23

; Silver Harp (ID: 24)
Item_24_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $01F4				 ; Buy Price: 500
	.word $00FA				; Sell Price: 250
	.byte $02							 ; Flags: Equip=False, Use=True
	.byte $04				 ; Item Type: 4
	.byte $18				 ; Sprite ID: 24

; Death Necklace (ID: 25)
Item_25_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0000				 ; Buy Price: 0
	.word $0000				; Sell Price: 0
	.byte $00							 ; Flags: Equip=False, Use=False
	.byte $04				 ; Item Type: 4
	.byte $19				 ; Sprite ID: 25

; Stones of Sunlight (ID: 26)
Item_26_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0000				 ; Buy Price: 0
	.word $0000				; Sell Price: 0
	.byte $00							 ; Flags: Equip=False, Use=False
	.byte $04				 ; Item Type: 4
	.byte $1A				 ; Sprite ID: 26

; Staff of Rain (ID: 27)
Item_27_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0000				 ; Buy Price: 0
	.word $0000				; Sell Price: 0
	.byte $00							 ; Flags: Equip=False, Use=False
	.byte $04				 ; Item Type: 4
	.byte $1B				 ; Sprite ID: 27

; Rainbow Drop (ID: 28)
Item_28_Stats:
	.byte $00			; Attack Power: 0
	.byte $00			 ; Defense Power: 0
	.word $0000				 ; Buy Price: 0
	.word $0000				; Sell Price: 0
	.byte $02							 ; Flags: Equip=False, Use=True
	.byte $04				 ; Item Type: 4
	.byte $1C				 ; Sprite ID: 28

; Item Stats Pointer Table
	.word Item_00_Stats
	.word Item_01_Stats
	.word Item_02_Stats
	.word Item_03_Stats
	.word Item_04_Stats
	.word Item_05_Stats
	.word Item_06_Stats
	.word Item_07_Stats
	.word Item_08_Stats
	.word Item_09_Stats
	.word Item_10_Stats
	.word Item_11_Stats
	.word Item_12_Stats
	.word Item_13_Stats
	.word Item_14_Stats
	.word Item_15_Stats
	.word Item_16_Stats
	.word Item_17_Stats
	.word Item_18_Stats
	.word Item_19_Stats
	.word Item_20_Stats
	.word Item_21_Stats
	.word Item_22_Stats
	.word Item_23_Stats
	.word Item_24_Stats
	.word Item_25_Stats
	.word Item_26_Stats
	.word Item_27_Stats
	.word Item_28_Stats