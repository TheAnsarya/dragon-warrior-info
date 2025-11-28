; Dragon Warrior Build Configuration
; This file controls whether to use generated assets from JSON or original hardcoded data

; Uncomment the line below to enable asset-first workflow (JSON → ASM → ROM)
.define USE_GENERATED_ASSETS

; When USE_GENERATED_ASSETS is defined:
; - Monster data comes from assets/json/monsters_verified.json
; - Shop data comes from assets/json/shops.json
; - Dialog data comes from assets/json/dialogs.json
; - Graphics data comes from assets/json/graphics.json
; - Palette data comes from assets/json/palettes.json
; - Map data comes from assets/json/maps.json
;
; When USE_GENERATED_ASSETS is NOT defined:
; - All data comes from the original hardcoded values in Bank*.asm files
