;----------------------------------------------------------------------------------------------------
; NPC Tables - Generated from assets/json/npcs.json
; To modify NPC data, edit the JSON file and rebuild
;----------------------------------------------------------------------------------------------------

;The tables below control the characteristics of the NPCs. There are 3 bytes per entry and are
;formatted as follows:

;NNNXXXXX _DDYYYYY CCCCCCCC
;
;NNN	  - NPC graphic: 0=Male villager, 1=Fighter, 2=Guard, 3=Shopkeeper, 4=King Lorik,
;			 5=Wizard/Dragonlord, 6=Princess Gwaelin/Female villager
;			 7=Stationary guard/Guard with trumpet.
;XXXXX	- NPC X position.
;_		- Unused.
;DD	   - NPC direction: 0=Facing up, 1=Facing right, 2=Facing down, 3=Facing left.
;YYYYY	- NPC Y position.
;CCCCCCCC - Dialog control byte.

;----------------------------------------------------------------------------------------------------

TantagelMobileTable:
		.byte $C8, $4D, $62	 ;Female villager at  8,13.
		.byte $53, $42, $17	 ;Guard at 19, 2.
		.byte $0B, $4B, $1C	 ;Male villager at 11,11.
		.byte $B1, $4B, $1D	 ;Wizard at 17,11.
		.byte $64, $55, $1F	 ;Shopkeeper at  4,21.
		.byte $39, $4B, $16	 ;Fighter at 25,11.
		.byte $52, $52, $72	 ;Guard at 18,18.
		.byte $42, $4C, $1B	 ;Guard at  2,12.
		.byte $66, $59, $20	 ;Shopkeeper at  6,25.
		.byte $38, $55, $22	 ;Fighter at 24,21.
		.byte $ff			   ;End of table.

TantStatTbl:
		.byte $78, $41, $0E	 ;Shopkeeper at 24, 1.
		.byte $DB, $45, $1A	 ;Female villager at 27, 5.
		.byte $48, $46, $19	 ;Guard at  8, 6.
		.byte $02, $48, $18	 ;Male villager at  2, 8.
		.byte $48, $08, $71	 ;Guard at  8, 8.
		.byte $5A, $0F, $1E	 ;Guard at 26,15.
		.byte $4F, $34, $63	 ;Guard at 15,20.
		.byte $B4, $7A, $6A	 ;Wizard at 20,26.
		.byte $49, $3B, $21	 ;Guard at  9,27.
		.byte $4C, $7B, $21	 ;Guard at 12,27.
		.byte $ff			   ;End of table.

ThRmMobTbl:
		.byte $47, $45, $65	 ;Guard at  7, 5.
		.byte $ff			   ;End of table.

ThRmStatTbl:
		.byte $83, $43, $6E	 ;King Lorik at  3, 3.
		.byte $43, $26, $23	 ;Guard at  3, 6.
		.byte $45, $66, $24	 ;Guard at  5, 6.
		.byte $C6, $43, $6F	 ;Female villager at  6, 3.
		.byte $ff			   ;End of table.

TaSLMobTbl:
		.byte $ff			   ;No NPCs.

TaSLStatTbl:
		.byte $A4, $46, $66	 ;Wizard at  4, 6.
		.byte $ff			   ;End of table.

TaDLMobTbl:
		.byte $53, $42, $17	 ;Guard at 19, 2.
		.byte $0E, $57, $1C	 ;Male villager at 14,23.
		.byte $39, $4B, $16	 ;Fighter at 25,11.
		.byte $52, $52, $72	 ;Guard at 18,18.
		.byte $42, $4C, $1B	 ;Guard at  2,12.
		.byte $66, $59, $20	 ;Shopkeeper at  6,25.
		.byte $38, $55, $22	 ;Fighter at 24,21.
		.byte $ff			   ;End of table.

TaDLStatTbl:
		.byte $8B, $47, $FE	 ;King Lorik at 11, 7.
		.byte $E9, $49, $FD	 ;Trumpet guard at  9, 9.
		.byte $E9, $4B, $FD	 ;Trumpet guard at  9,11.
		.byte $E9, $4D, $FD	 ;Trumpet guard at  9,13.
		.byte $AC, $49, $FD	 ;Wizard at 12, 9.
		.byte $AC, $4B, $FD	 ;Wizard at 12,11.
		.byte $AC, $4D, $FD	 ;Wizard at 12,13.
		.byte $49, $3B, $FD	 ;Guard at  9,27.
		.byte $4C, $7B, $FD	 ;Guard at 12,27.
		.byte $ff			   ;End of table.

DLBFMobTbl:
		.byte $ff			   ;No NPCs.

DLBFStatTbl:
		.byte $B0, $58, $70	 ;Wizard at 16,24.
		.byte $ff			   ;End of table.

RainMobTbl:
		.byte $ff			   ;No NPCs.

RainStatTbl:
		.byte $A4, $24, $6C	 ;Wizard at  4, 4.
		.byte $ff			   ;End of table.

RnbwMobTbl:
		.byte $ff			   ;No NPCs.

RnbwStatTbl:
		.byte $A4, $65, $6D	 ;Wizard at  4, 5.
		.byte $ff			   ;End of table.

CantMobTbl:
		.byte $14, $4F, $4B	 ;Male villager at 20,15.
		.byte $45, $46, $60	 ;Guard at  5, 6.
		.byte $79, $51, $4C	 ;Shopkeeper at 25,17.
		.byte $C4, $4E, $49	 ;Female villager at  4,14.
		.byte $76, $45, $03	 ;Shopkeeper at 22, 5.
		.byte $C9, $50, $4A	 ;Female villager at  9,16.
		.byte $AE, $5C, $6B	 ;Wizard at 14,28.
		.byte $4F, $46, $48	 ;Guard at 15, 6.
		.byte $63, $5A, $4E	 ;Shopkeeper at  3,26.
		.byte $56, $49, $4D	 ;Guard at 22, 9.
		.byte $ff			   ;End of table.

CantStatTbl:
		.byte $68, $43, $14	 ;Shopkeeper at  8, 3.
		.byte $BB, $46, $0C	 ;Wizard at 27, 6.
		.byte $02, $27, $0A	 ;Male villager at  2, 7.
		.byte $62, $2C, $45	 ;Shopkeeper at  2,12.
		.byte $67, $6C, $0B	 ;Shopkeeper at  7,12.
		.byte $58, $2C, $05	 ;Guard at 24,12.
		.byte $D6, $6D, $10	 ;Female villager at 22,13.
		.byte $AF, $50, $46	 ;Wizard at 15,16.
		.byte $B6, $56, $47	 ;Wizard at 22,22.
		.byte $7B, $7A, $04	 ;Shopkeeper at 27,26.
		.byte $ff			   ;End of table.

RimMobTbl:
		.byte $C6, $55, $59	 ;Female villager at  6,21.
		.byte $0B, $48, $30	 ;Male villager at 11, 8.
		.byte $06, $57, $5A	 ;Male villager at  6,23.
		.byte $D6, $4E, $56	 ;Female villager at 22,14.
		.byte $25, $59, $5B	 ;Fighter at  5,25.
		.byte $37, $4B, $52	 ;Fighter at 23,11.
		.byte $0E, $4B, $55	 ;Male villager at 14,11.
		.byte $30, $5A, $69	 ;Fighter at 16,26.
		.byte $48, $50, $54	 ;Guard at  8,16.
		.byte $38, $53, $57	 ;Fighter at 24,19.
		.byte $ff			   ;End of table.

RimStatTbl:
		.byte $1B, $40, $51	 ;Male villager at 27, 0.
		.byte $62, $04, $4F	 ;Shopkeeper at  2, 4.
		.byte $A4, $07, $0D	 ;Wizard at  4, 7.
		.byte $77, $47, $06	 ;Shopkeeper at 23, 7.
		.byte $CF, $08, $50	 ;Female villager at 15, 8.
		.byte $A6, $6D, $53	 ;Wizard at  6,13.
		.byte $70, $32, $15	 ;Shopkeeper at 16,18.
		.byte $A3, $37, $61	 ;Wizard at  3,23.
		.byte $B4, $57, $58	 ;Wizard at 20,23.
		.byte $C0, $5A, $5C	 ;Female villager at  0,26.
		.byte $ff			   ;End of table.

BrecMobTbl:
		.byte $A9, $44, $2B	 ;Wizard at  9, 4.
		.byte $2C, $53, $5D	 ;Fighter at 12,19.
		.byte $6F, $49, $2E	 ;Shopkeeper at 15, 9.
		.byte $19, $56, $31	 ;Male villager at 25,22.
		.byte $0A, $4E, $2C	 ;Male villager at 10,14.
		.byte $D8, $44, $0F	 ;Female villager at 24, 4.
		.byte $5A, $4F, $2F	 ;Guard at 26,15.
		.byte $CF, $58, $2D	 ;Female villager at 15,24.
		.byte $33, $52, $30	 ;Fighter at 19,18.
		.byte $23, $5A, $27	 ;Fighter at  3,26.
		.byte $ff			   ;End of table.

BrecStatTbl:
		.byte $65, $44, $01	 ;Shopkeeper at  5, 4.
		.byte $3C, $41, $25	 ;Fighter at 28, 1.
		.byte $C4, $47, $29	 ;Female villager at  4, 7.
		.byte $14, $4A, $26	 ;Male villager at 20,10.
		.byte $B8, $4A, $67	 ;Wizard at 24,10.
		.byte $01, $4D, $2A	 ;Male villager at  1,13.
		.byte $6A, $75, $12	 ;Shopkeeper at 10,21.
		.byte $14, $17, $28	 ;Male villager at 20,23.
		.byte $79, $79, $08	 ;Shopkeeper at 25,25.
		.byte $4A, $1A, $64	 ;Guard at 10,26.
		.byte $ff			   ;End of table.

KolMobTbl:
		.byte $0E, $4D, $36	 ;Male villager at 14,13.
		.byte $05, $4C, $30	 ;Male villager at  5,12.
		.byte $4C, $4A, $37	 ;Guard at 12,10.
		.byte $A2, $4C, $5E	 ;Wizard at  2,12.
		.byte $B4, $53, $38	 ;Wizard at 20,19.
		.byte $26, $47, $35	 ;Fighter at  6, 7.
		.byte $CB, $4E, $2E	 ;Female villager at 11,14.
		.byte $67, $53, $5F	 ;Shopkeeper at  7,19.
		.byte $B4, $48, $39	 ;Wizard at 20, 8.
		.byte $ff			   ;End of table.

KolStatTbl:
		.byte $A1, $41, $68	 ;Wizard at  1, 1.
		.byte $CC, $41, $32	 ;Female villager at 12, 1.
		.byte $73, $04, $11	 ;Shopkeeper at 19, 4.
		.byte $76, $6C, $00	 ;Shopkeeper at 22,12.
		.byte $34, $4D, $33	 ;Fighter at 20,13.
		.byte $6E, $75, $07	 ;Shopkeeper at 14,21.
		.byte $41, $57, $34	 ;Guard at  1,23.
		.byte $ff			   ;End of table.

GarMobTbl:
		.byte $CC, $44, $3E	 ;Female villager at 12, 4.
		.byte $CC, $4C, $43	 ;Female villager at 12,12.
		.byte $AC, $48, $3F	 ;Wizard at 12, 8.
		.byte $A2, $4A, $42	 ;Wizard at  2,10.
		.byte $0B, $47, $3D	 ;Male villager at 11, 7.
		.byte $12, $4C, $44	 ;Male villager at 18,12.
		.byte $27, $51, $41	 ;Fighter at  7,17.
		.byte $ff			   ;End of table.

GarStatTbl:
		.byte $AE, $41, $3A	 ;Wizard at 14, 1.
		.byte $43, $25, $3B	 ;Guard at  3, 5.
		.byte $45, $65, $3B	 ;Guard at  5, 5.
		.byte $69, $46, $3C	 ;Shopkeeper at  9, 6.
		.byte $65, $6B, $09	 ;Shopkeeper at  5,11.
		.byte $71, $6F, $13	 ;Shopkeeper at 17,15.
		.byte $A2, $31, $40	 ;Wizard at  2,17.
		.byte $6A, $12, $02	 ;Shopkeeper at 10,18.
		.byte $ff			   ;End of table.
