; Spell Cost Table - Generated from assets/json/spells.json
; To modify spell MP costs, edit the JSON file and rebuild

SpellCostTbl:
.byte $04			   ;HEAL	   4MP.
		.byte $02			   ;($9D54)HURT	   2MP.
		.byte $02			   ;($9D55)SLEEP	  2MP.
.byte $03			   ;RADIANT	3MP.
		.byte $02			   ;($9D57)STOPSPELL  2MP.
		.byte $06			   ;($9D58)OUTSIDE	6MP.
.byte $08			   ;RETURN	 8MP.
		.byte $02			   ;($9D5A)REPEL	  2MP.
		.byte $0A			   ;($9D5B)HEALMORE   10MP.
.byte $05			   ;HURTMORE   5MP.