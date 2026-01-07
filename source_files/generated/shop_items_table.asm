;----------------------------------------------------------------------------------------------------
; Shop Items Table - Generated from assets/json/shops.json
; To modify shop inventories, edit the JSON file and rebuild
;----------------------------------------------------------------------------------------------------

;The following table contains the items available in the shops. The first 7 rows are the items
;in the weapons and armor shops while the remaining rows are for the tool shops. The values in
;the table correspond to the item indexes in the ItemCostTbl above.

ShopItemsTbl:

;Koll Weapons & Armor.
        .byte $02, $03, $0A, $0B, $0E, $fd  ;Copper Sword, Hand Axe, Half Plate, Full Plate, Small Shield

;Brecconary Weapons & Armor.
        .byte $00, $01, $02, $07, $08, $0E, $fd  ;Bamboo Pole, Club, Copper Sword, Clothes, Leather Armor, Small Shield

;Garinham Weapons & Armor.
        .byte $01, $02, $03, $08, $09, $0A, $0F, $fd  ;Club, Copper Sword, Hand Axe, Leather Armor, Chain Mail, Half Plate, Large Shield

;Cantlin Weapons & Armor 1.
        .byte $00, $01, $02, $08, $09, $0F, $fd  ;Bamboo Pole, Club, Copper Sword, Leather Armor, Chain Mail, Large Shield

;Cantlin Weapons & Armor 2.
        .byte $03, $04, $0B, $0C, $fd  ;Hand Axe, Broad Sword, Full Plate, Magic Armor

;Cantlin Weapons & Armor 3.
        .byte $05, $10, $fd  ;Flame Sword, Silver Shield

;Rimuldar Weapons & Armor.
        .byte $02, $03, $04, $0A, $0B, $0C, $fd  ;Copper Sword, Hand Axe, Broad Sword, Half Plate, Full Plate, Magic Armor

;Koll Item Shop.
        .byte $11, $13, $16, $15, $fd  ;Herb, Torch, Dragon's Scale, Wings

;Brecconary Item Shop.
        .byte $11, $13, $16, $fd  ;Herb, Torch, Dragon's Scale

;Garinham Item Shop.
        .byte $11, $13, $16, $fd  ;Herb, Torch, Dragon's Scale

;Cantlin Item Shop 1.
        .byte $11, $13, $fd  ;Herb, Torch

;Cantlin Item Shop 2.
        .byte $16, $15, $fd  ;Dragon's Scale, Wings
