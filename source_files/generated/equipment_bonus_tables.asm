;----------------------------------------------------------------------------------------------------
; Equipment Bonus Tables - Generated from assets/json/equipment_bonuses.json
; To modify equipment stats, edit the JSON file and rebuild
;----------------------------------------------------------------------------------------------------

;This table contains weapon bonuses added to the
;strength score to produce the attack power stat.

WeaponsBonusTbl:
		.byte $00			   ;None			 +0.
		.byte $02			   ;Bamboo Pole	  +2.
		.byte $04			   ;Club			 +4.
		.byte $0A			   ;Copper Sword	 +10.
		.byte $0F			   ;Hand Axe		 +15.
		.byte $14			   ;Broad Sword	  +20.
		.byte $1C			   ;Flame Sword	  +28.
		.byte $28			   ;Erdrick's Sword  +40.

;This table contains armor bonuses added to the
;agility score to produce the defense power stat.

ArmorBonusTbl:
		.byte $00			   ;None			 +0.
		.byte $02			   ;Clothes		  +2.
		.byte $04			   ;Leather Armor	+4.
		.byte $0A			   ;Chain Mail	   +10.
		.byte $10			   ;Half Plate	   +16.
		.byte $18			   ;Full Plate	   +24.
		.byte $18			   ;Magic Armor	  +24.
		.byte $1C			   ;Erdrick's Armor  +28.

;This table contains shield bonuses added to the
;agility score to produce the defense power stat.

ShieldBonusTbl:
		.byte $00			   ;None			 +0.
		.byte $04			   ;Small Shield	 +4.
		.byte $0A			   ;Large Shield	 +10.
		.byte $14			   ;Silver Shield	+20.
