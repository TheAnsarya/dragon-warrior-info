.org $8000

.include "Dragon_Warrior_Defines.asm"

;--------------------------------------[ Forward declarations ]--------------------------------------

.alias ModAttribBits			$C006
.alias GetNPCSpriteIndex		$C0F4
.alias WordMultiply			 $C1C9
.alias ByteDivide			   $C1F0
.alias PalFadeOut			   $C212
.alias PalFadeIn				$C529
.alias ClearAttribByte		  $C244
.alias UpdateRandNumber			$C55B
.alias CalcPPUBufferAddr		   $C596
.alias CalcPPUBufAddr		   CalcPPUBufferAddr	;Abbreviated alias
.alias DoAddressCalculation			   $C5AA
.alias PrepSPPalLoad			$C632
.alias PrepBGPalLoad			$C63D
.alias AddPPUBufferEntry		   $C690
.alias ClearSpriteRAM		   $C6BB
.alias IdleUpdate			   $CB30
.alias CheckForTriggers		 $CBF7
.alias ChangeMaps			   $D9E2
.alias MapTargetTbl			 $F461
.alias GFXTilesPointer			  $F5B3
.alias GFXTilesPtr			  GFXTilesPointer  ;Abbreviated alias
.alias Bank1ToCHR0			  $FC98
.alias Bank0ToCHR0			  $FCA3
.alias Bank0ToCHR1			  $FCA8
.alias Bank2ToCHR1			  $FCAD
.alias WaitForNMI			   $FF74
.alias _DoReset				 $FF8E

;--------------------------------[ Table name aliases ]--------------------------------------
; Map full table names (used in references) to abbreviated names (actual labels)

.alias ThroneRoomMobileTable	ThRmMobTbl
.alias ThroneRoomStaticTable	ThRmStatTbl
.alias DrgnLrdBFMobileTable	 DLBFMobTbl
.alias DrgnLrdBFStaticTable	 DLBFStatTbl
.alias KolMobileTable		   KolMobTbl
.alias KolStaticTable		   KolStatTbl
.alias BrecconaryMobileTable	BrecMobTbl
.alias BrecconaryStaticTable	BrecStatTbl
.alias GarinhamMobileTable	  GarMobTbl
.alias GarinhamStaticTable	  GarStatTbl
.alias CantlinMobileTable	   CantMobTbl
.alias CantlinStaticTable	   CantStatTbl
.alias RimuldarMobileTable	  RimMobTbl
.alias RimuldarStaticTable	  RimStatTbl
.alias TantSLMobileTable		TaSLMobTbl
.alias TantSLStaticTable		TaSLStatTbl
.alias RainCaveMobileTable	  RainMobTbl
.alias RainCaveStaticTable	  RainStatTbl
.alias RainbowCaveMobileTable   RnbwMobTbl
.alias RainbowCaveStaticTable   RnbwStatTbl
.alias TantDLMobileTable		TaDLMobTbl
.alias TantDLStaticTable		TaDLStatTbl
.alias TantagelStaticTable	  TantStatTbl
.alias MapDatTbl				MapDataTable		 ;Abbreviated alias for internal table
.alias NPCMobPtrTbl			 NPCMobilePointerTable ;Abbreviated alias for internal table
.alias BrecCvrdDatPtr		   BrecCvrdDatPointer   ;Abbreviated alias for internal label

;-----------------------------------------[ Start of code ]------------------------------------------

;The following table contains functions called from bank 3 through the IRQ interrupt.

BankPointers:
BankPtr_Word_8000:  .word $0000			 ;Unused.
BankPtr_Word_8002:  .word LoadStartPals	 ;($AA7E)Load BG and sprite palettes for selecting saved game.
BankPtr_Word_8004:  .word LoadEndBossGFX	;($BABD)Load final battle graphics.
BankPtr_Word_8006:  .word ItemCostTbl	   ;($9947)Table of costs for shop items.
BankPtr_Word_8008:  .word DoSprites		 ;($B6DA)Update player and NPC sprites.
BankPtr_Word_800A:  .word RemoveWindow	  ;($A7A2)Remove window from screen.
BankPtr_Word_800C:  .word LoadCreditsPals   ;($AA62)Load palettes for end credits.
BankPtr_Word_800E:  .word DoPalFadeIn	   ;($AA3D)Fade in palettes.
BankPtr_Word_8010:  .word DoPalFadeOut	  ;($AA43)Fade out palettes.

BrecCvrdDatPointer:
.word TantSLDat		 ;($8D24)Pointer to Brecconary covered areas data.

GarinCvrdDatPtr:
.word DgnLrdSL4Dat	  ;($8EE6)Pointer to Garinham covered areas data.

CantCvrdDatPtr:
.word SwampCaveDat+$32  ;($8FAE)Pointer to Cantlin covered areas data.

RimCvrdDatPtr:
.word GarinCaveB3Dat+$E ;($9170)Pointer to Rimuldar covered areas data.

;----------------------------------------------------------------------------------------------------

MapDataTable:				   ;Data for game maps.

;Unused. Map #$00.
.word NULL			  ;Map data pointer.
.byte $00			   ;Columns.
		.byte $00			   ;($801D)Rows.
.byte $00			   ;Boundary block.

;Overworld. Map #$01.
		.word WrldMapPtrTbl	 ;($801F)($A653)Pointer to row pointers.
		.byte $77			   ;($8021)120 colums.
.byte $77			   ;120 rows.
		.byte $0F			   ;($8023)Water.

;Dragonlord's castle - ground floor. Map #$02.
.word DLCstlGFDat	   ;($80B0)Pointer to map data.
.byte $13			   ;20 columns.
		.byte $13			   ;($8027)20 rows.
.byte $06			   ;Swamp.

;Hauksness. Map #$03.
.word HauksnessDat	  ;($8178)Pointer to map data.
.byte $13			   ;20 columns.
.byte $13			   ;20 rows.
.byte $01			   ;Sand.

;Tantagel castle ground floor. Map #$04.
		.word TantGFDat		 ;($802E)($8240)Pointer to map data.
		.byte $1D			   ;($8030)30 columns.
.byte $1D			   ;30 rows.
		.byte $00			   ;($8032)Grass.

;Throne room. Map #$05.
.word ThrnRoomDat	   ;($8402)Pointer to map data.
.byte $09			   ;10 columns.
		.byte $09			   ;($8036)10 rows.
.byte $15			   ;Small tiles.

;Dragonlord's castle - bottom level. Map #$06.
.word DgnLrdBLDat	   ;($8434)Pointer to map data.
.byte $1D			   ;30 columns.
		.byte $1D			   ;($803B)30 rows.
.byte $0F			   ;Water.

;Kol. Map #$07.
		.word KolDat			;($803D)($85F6)Pointer to map data.
.byte $17			   ;24 columns.
.byte $17			   ;24 rows.
.byte $0B			   ;Trees.

;Brecconary. Map #$08.
		.word BrecconaryDat	 ;($8042)($8716)Pointer to map data.
.byte $1D			   ;30 columns.
		.byte $1D			   ;($8045)30 rows.
.byte $00			   ;Grass.

;Garinham. Map #$09.
		.word GarinhamDat	   ;($8047)($8A9A)ointer to map data.
.byte $13			   ;20 columns.
.byte $13			   ;20 rows.
.byte $00			   ;Grass.

;Cantlin. Map #$0A.
		.word CantlinDat		;($804C)($88D8)Pointer to map data.
		.byte $1D			   ;($804E)30 columns.
		.byte $1D			   ;($804F)30 rows.
.byte $04			   ;Brick.

;Rimuldar. Map #$0B.
		.word RimuldarDat	   ;($8051)($8B62)Pointer to map data.
		.byte $1D			   ;($8053)30 columns.
		.byte $1D			   ;($8054)30 rows.
.byte $00			   ;Grass.

;Tantagel castle - sublevel. Map #$0C.
		.word TantSLDat		 ;($8056)($8D24)Pointer to map data.
		.byte $09			   ;($8058)10 columns.
		.byte $09			   ;($8059)10 rows.
.byte $10			   ;Stone.

;Staff of rain cave. Map #$0D.
		.word RainCaveDat	   ;($805B)($8D56)Pointer to map data.
		.byte $09			   ;($805D)10 columns.
		.byte $09			   ;($805E)10 rows.
.byte $10			   ;Stone.

;Rainbow drop cave. Map #$0E.
		.word DropCaveDat	   ;($8060)($8D88)Pointer to map data.
.byte $09			   ;10 columns.
		.byte $09			   ;($8063)10 rows.
.byte $10			   ;Stone.

;Dragonlord's castle - sublevel 1. Map #$0F.
		.word DgnLrdSL1Dat	  ;($8065)($8DBA)Pointer to map data.
		.byte $13			   ;($8067)20 columns.
.byte $13			   ;20 rows.
		.byte $10			   ;($8069)Stone.

;Dragonlord's castle - sublevel 2. Map #$10.
.word DgnLrdSL2Dat	  ;($8E82)Pointer to map data.
.byte $09			   ;10 columns.
		.byte $09			   ;($806D)10 rows.
.byte $10			   ;Stone.

;Dragonlord's castle - sublevel 3. Map #$11.
		.word DgnLrdSL3Dat	  ;($806F)($8EB4)Pointer to map data.
		.byte $09			   ;($8071)10 columns.
		.byte $09			   ;($8072)10 rows.
.byte $10			   ;Stone.

;Dragonlord's castle - sublevel 4. Map #$12.
		.word DgnLrdSL4Dat	  ;($8074)($8EE6)Pointer to map data.
		.byte $09			   ;($8076)10 columns.
.byte $09			   ;10 rows.
		.byte $10			   ;($8078)Stone.

;Dragonlord's castle - sublevel 5. Map #$13.
.word DgnLrdSL5Dat	  ;($8F18)Pointer to map data.
.byte $09			   ;10 columns.
		.byte $09			   ;($807C)10 rows.
.byte $10			   ;Stone.

;Dragonlord's castle - sublevel 6. Map #$14.
		.word DgnLrdSL6Dat	  ;($807E)($8F4A)Pointer to map data.
.byte $09			   ;10 columns.
		.byte $09			   ;($8081)10 rows.
.byte $10			   ;Stone.

;Swamp cave. Map #$15.
		.word SwampCaveDat	  ;($8083)($8F7C)Pointer to map data.
		.byte $05			   ;($8085)6 columns.
		.byte $1D			   ;($8086)30 rows.
.byte $10			   ;Stone.

;Rock mountain cave - B1. Map #$16.
		.word RckMtnB1Dat	   ;($8088)($8FD6)Pointer to map data.
.byte $0D			   ;14 columns.
.byte $0D			   ;14 rows.
		.byte $10			   ;($808C)Stone.

;Rock mountain cave - B2. Map #$17.
.word RckMtnB2Dat	   ;($9038)Pointer to map data.
.byte $0D			   ;14 columns.
.byte $0D			   ;14 rows.
.byte $10			   ;Stone.

;Cave of garinham - B1. Map #$18.
.word GarinCaveB1Dat	;($909A)Pointer to map data.
.byte $13			   ;20 columns.
		.byte $13			   ;($8095)20 rows.
.byte $10			   ;Stone.

;Cave of garinham - B2. Map #$19.
		.word GarinCaveB2Dat	;($8097)($925C)Pointer to map data.
		.byte $0D			   ;($8099)14 columns.
.byte $0B			   ;12 rows.
		.byte $10			   ;($809B)Stone.

;Cave of garinham - B3. Map #$1A.
.word GarinCaveB3Dat	;($9162)Pointer to map data.
.byte $13			   ;20 columns.
.byte $13			   ;20 rows.
		.byte $10			   ;($80A0)Stone.

;Cave of garinham - B4. Map #$1B.
.word GarinCaveB4Dat	;($922A)Pointer to map data.
		.byte $09			   ;($80A3)10 columns.
.byte $09			   ;10 rows.
.byte $10			   ;Stone.

;Erdrick's cave - B1. Map #$1C.
		.word ErdCaveB1Dat	  ;($80A6)($92B0)Pointer to map data.
.byte $09			   ;10 columns.
		.byte $09			   ;($80A9)10 rows.
		.byte $10			   ;($80AA)Stone.

;Erdrick's cave - B2. Map #$1D.
.word ErdCaveB2Dat	  ;($92E2)Pointer to map data.
.byte $09			   ;10 columns.
.byte $09			   ;10 rows.
		.byte $10			   ;($80AF)Stone.

;----------------------------------------------------------------------------------------------------

;Each byte represents 2 tiles of information (upper nibble and lower nibble).  a total of 16
;different tile types are possible per map.  The tile mapping is different for different
;maps so the tile mapping is present above each map entry.

;An interesting thing about the map data is that the covered area data is also mixed in with it.
;The covered area data is for unrelated maps and has different dimensions. If the MSB of the
;nibble is set in the map data, that means it is used to potentially indicate a covered area in
;a map. Thats why the blocks repeat in the dungeon maps. The blocks with the upper bit of each
;nibble set are used for covered area data in town maps. For example, the Tantagel sublevel map
;has some blocks with the MSB of some of the nibbles set. This is actually covered area data for
;Brecconary. The Brecconary covered map data continues through the rain cave and drop cave map
;data as well as others.  This is because Brecconary is much bigger than those other maps combined.
;The map data in for Tantagel sublevel, rain cave and drop cave all have some map data where the
;MSB of the nibbles are set. This is covered map data for the upper right building in Brecconary.

;Dragonlord's castle - ground floor. Map #$02.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Trees, $9-Poison, $A-Force Field,
;$B-Door, $C-Weapon Shop Sign, $D-Inn Sign, $E-Bridge, $F-Large Tile.
DLCstlGFDat:
		.byte $99, $44, $49, $94, $44, $44, $44, $44, $44, $99;($80B0)
		.byte $94, $46, $44, $94, $AA, $7A, $A4, $66, $64, $49;($80BA)
		.byte $44, $66, $64, $44, $AF, $FF, $A4, $64, $66, $44;($80C4)
		.byte $46, $64, $66, $64, $AF, $6F, $A4, $66, $66, $64;($80CE)
.byte $46, $44, $44, $64, $AA, $AA, $A4, $46, $44, $64
.byte $46, $46, $66, $64, $AA, $AA, $A4, $66, $64, $64
.byte $46, $44, $64, $64, $46, $66, $44, $64, $66, $64
.byte $46, $46, $66, $66, $44, $A4, $46, $66, $64, $64
		.byte $46, $44, $B4, $46, $46, $66, $44, $4B, $44, $64;($8100)
.byte $46, $4A, $AA, $46, $44, $A4, $44, $AA, $A4, $64
		.byte $46, $4A, $4A, $46, $46, $66, $44, $A4, $A4, $64;($8114)
		.byte $46, $4A, $AA, $46, $44, $A4, $44, $AA, $A4, $64;($811E)
		.byte $46, $4A, $4A, $46, $66, $66, $44, $A4, $A4, $64;($8128)
.byte $46, $4A, $AA, $44, $44, $44, $44, $AA, $A4, $64
		.byte $46, $44, $74, $46, $66, $66, $64, $47, $44, $64;($813C)
		.byte $46, $64, $44, $66, $46, $64, $66, $44, $46, $64;($8146)
		.byte $44, $66, $66, $66, $66, $66, $66, $66, $66, $44;($8150)
		.byte $94, $46, $66, $44, $46, $64, $44, $66, $64, $49;($815A)
		.byte $99, $44, $44, $49, $46, $64, $94, $44, $44, $99;($8164)
		.byte $99, $99, $99, $99, $46, $64, $99, $99, $99, $99;($816E)

;Hauksness. Map #$03.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Trees, $9-Poison, $A-Force Field,
;$B-Door, $C-Weapon Shop Sign, $D-Inn Sign, $E-Bridge, $F-Large Tile.
HauksnessDat:
.byte $44, $11, $04, $41, $44, $44, $44, $46, $64, $94
		.byte $41, $10, $84, $16, $6F, $64, $80, $01, $69, $94;($8182)
.byte $11, $18, $04, $46, $64, $64, $00, $06, $99, $14
.byte $10, $00, $99, $44, $64, $44, $09, $06, $69, $11
.byte $11, $00, $09, $90, $60, $00, $80, $06, $60, $14
		.byte $40, $66, $61, $91, $66, $61, $16, $61, $60, $04;($81AA)
		.byte $40, $66, $66, $16, $61, $11, $66, $66, $60, $80;($81B4)
		.byte $00, $66, $01, $11, $08, $00, $00, $00, $60, $08;($81BE)
.byte $40, $66, $01, $44, $44, $14, $66, $64, $64, $40
.byte $66, $16, $04, $66, $61, $14, $90, $46, $F9, $41
.byte $61, $66, $04, $44, $F4, $44, $09, $46, $99, $49
.byte $88, $66, $84, $11, $66, $64, $80, $44, $94, $49
.byte $80, $16, $84, $14, $64, $14, $88, $11, $99, $84
		.byte $40, $61, $84, $66, $61, $11, $81, $04, $44, $41;($81FA)
.byte $40, $66, $04, $46, $64, $44, $10, $04, $11, $14
		.byte $49, $16, $01, $18, $61, $66, $66, $16, $6F, $14;($820E)
		.byte $99, $66, $00, $10, $68, $00, $00, $04, $64, $11;($8218)
		.byte $19, $61, $66, $66, $10, $00, $90, $04, $44, $44;($8222)
		.byte $49, $99, $00, $00, $00, $09, $99, $01, $11, $11;($822C)
		.byte $11, $94, $44, $40, $49, $99, $94, $44, $14, $44;($8236)

;Tantegel castle ground floor. Map #$04.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Trees, $9-Poison, $A-Force Field,
;$B-Door, $C-Weapon Shop Sign, $D-Inn Sign, $E-Bridge, $F-Large Tile.
TantGFDat:
		.byte $44, $44, $44, $40, $00, $00, $00, $04, $44, $44, $44, $04, $44, $08, $00;($8240)
.byte $46, $66, $66, $40, $80, $88, $08, $04, $66, $66, $64, $04, $64, $00, $00
		.byte $46, $66, $66, $40, $00, $00, $00, $04, $66, $66, $64, $04, $F4, $00, $00;($825E)
.byte $46, $64, $66, $44, $44, $66, $44, $44, $66, $46, $64, $00, $08, $80, $00
		.byte $46, $66, $66, $66, $66, $66, $66, $66, $66, $66, $64, $08, $88, $00, $00;($827C)
.byte $46, $66, $66, $44, $44, $44, $44, $44, $66, $66, $64, $00, $00, $00, $00
		.byte $44, $44, $46, $46, $66, $66, $66, $64, $44, $B4, $44, $44, $64, $44, $00;($829A)
.byte $46, $66, $46, $45, $66, $66, $64, $64, $66, $66, $66, $66, $66, $64, $00
		.byte $46, $66, $66, $46, $66, $66, $66, $64, $66, $66, $66, $66, $66, $64, $00;($82B8)
.byte $46, $66, $46, $44, $46, $66, $64, $44, $44, $44, $44, $44, $46, $64, $00
		.byte $44, $44, $46, $48, $86, $66, $68, $84, $66, $46, $64, $66, $46, $64, $00;($82D6)
.byte $46, $66, $46, $48, $86, $66, $68, $84, $66, $46, $64, $66, $46, $64, $00
		.byte $46, $66, $46, $48, $06, $66, $60, $84, $66, $66, $66, $66, $66, $64, $00;($82F4)
.byte $43, $66, $B6, $40, $06, $66, $60, $04, $66, $66, $66, $66, $66, $64, $00
		.byte $46, $36, $46, $40, $06, $66, $60, $04, $66, $46, $64, $66, $46, $64, $00;($8312)
.byte $43, $63, $46, $40, $66, $66, $66, $04, $66, $46, $64, $66, $46, $64, $00
		.byte $44, $44, $46, $40, $62, $22, $26, $04, $44, $44, $44, $44, $46, $44, $00;($8330)
.byte $46, $66, $66, $66, $62, $AA, $26, $66, $66, $66, $64, $66, $66, $64, $00
		.byte $46, $66, $66, $66, $62, $AA, $26, $66, $66, $66, $64, $AA, $AA, $A4, $00;($834E)
.byte $44, $46, $64, $44, $62, $22, $26, $44, $66, $66, $64, $AA, $AA, $A4, $00
		.byte $46, $66, $66, $64, $66, $66, $66, $46, $66, $66, $64, $66, $66, $64, $00;($836C)
.byte $46, $66, $66, $64, $46, $66, $64, $44, $44, $46, $64, $66, $66, $64, $20
.byte $46, $64, $66, $66, $46, $66, $64, $66, $66, $66, $64, $44, $44, $44, $20
		.byte $46, $66, $66, $66, $46, $66, $64, $66, $66, $66, $64, $22, $22, $22, $20;($8399)
		.byte $46, $22, $66, $46, $46, $66, $64, $66, $44, $44, $44, $22, $22, $22, $20;($83A8)
.byte $42, $22, $26, $66, $46, $66, $64, $66, $46, $64, $64, $22, $22, $22, $20
.byte $42, $22, $26, $66, $44, $66, $44, $66, $66, $6F, $64, $22, $22, $22, $20
		.byte $42, $22, $22, $66, $46, $66, $64, $66, $46, $64, $64, $22, $22, $22, $20;($83D5)
		.byte $44, $44, $44, $44, $44, $66, $44, $44, $44, $44, $44, $22, $22, $22, $20;($83E4)
.byte $22, $00, $00, $00, $00, $66, $00, $00, $00, $00, $22, $22, $22, $22, $27

;Throne room. Map #$05.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Trees, $9-Poison, $A-Force Field,
;$B-Door, $C-Weapon Shop Sign, $D-Inn Sign, $E-Bridge, $F-Large Tile.
ThrnRoomDat:
		.byte $44, $44, $44, $44, $44;($8402)
		.byte $46, $66, $66, $36, $64;($8407)
.byte $46, $FF, $FF, $FF, $64
.byte $46, $F6, $FF, $6F, $64
		.byte $46, $66, $33, $66, $64;($8416)
.byte $46, $66, $66, $66, $64
.byte $46, $66, $66, $66, $64
.byte $44, $44, $B4, $44, $44
.byte $46, $66, $66, $66, $74
		.byte $44, $44, $44, $44, $44;($842F)

;Dragonlord's castle - bottom level. Map #$06.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Trees, $9-Poison, $A-Force Field,
;$B-Door, $C-Weapon Shop Sign, $D-Inn Sign, $E-Bridge, $F-Large Tile.
DgnLrdBLDat:
.byte $22, $22, $22, $22, $22, $22, $22, $22, $22, $22, $22, $22, $22, $22, $22
.byte $22, $24, $44, $42, $22, $22, $22, $44, $44, $44, $44, $42, $44, $42, $22
.byte $22, $44, $66, $44, $44, $44, $44, $46, $66, $46, $66, $44, $46, $44, $22
.byte $24, $46, $66, $64, $46, $66, $64, $66, $66, $66, $66, $64, $66, $64, $42
.byte $24, $66, $66, $66, $44, $66, $44, $66, $66, $46, $66, $64, $64, $66, $42
.byte $24, $66, $46, $66, $46, $66, $66, $66, $64, $44, $66, $66, $66, $66, $42
.byte $24, $66, $66, $66, $46, $66, $64, $44, $44, $64, $44, $44, $64, $66, $42
		.byte $24, $46, $66, $64, $46, $66, $64, $66, $64, $44, $66, $64, $66, $64, $42;($849D)
		.byte $22, $44, $66, $44, $66, $66, $64, $46, $66, $66, $66, $44, $46, $44, $12;($84AC)
		.byte $22, $24, $64, $46, $64, $44, $44, $44, $66, $46, $64, $41, $46, $41, $12;($84BB)
.byte $22, $24, $66, $66, $64, $66, $66, $64, $46, $66, $44, $11, $11, $11, $22
		.byte $22, $24, $64, $44, $44, $63, $66, $64, $44, $64, $41, $12, $11, $12, $22;($84D9)
.byte $22, $24, $64, $66, $64, $63, $36, $66, $6B, $64, $11, $22, $22, $1E, $12
		.byte $22, $24, $64, $64, $64, $63, $33, $64, $44, $64, $41, $22, $22, $22, $02;($84F7)
.byte $22, $24, $64, $66, $64, $66, $66, $64, $46, $66, $42, $22, $12, $29, $02
		.byte $22, $24, $64, $64, $64, $44, $44, $44, $66, $64, $42, $12, $91, $E1, $22;($8515)
		.byte $22, $24, $64, $66, $64, $46, $66, $66, $66, $44, $22, $22, $00, $22, $22;($8524)
.byte $22, $24, $64, $64, $64, $66, $64, $44, $64, $42, $22, $12, $29, $12, $22
		.byte $22, $24, $64, $66, $64, $66, $44, $24, $44, $22, $21, $12, $19, $02, $12;($8542)
		.byte $22, $24, $64, $64, $64, $64, $42, $22, $22, $22, $11, $22, $11, $01, $12;($8551)
		.byte $22, $24, $64, $66, $64, $64, $22, $24, $44, $22, $22, $21, $19, $91, $22;($8560)
.byte $22, $44, $64, $46, $44, $64, $42, $44, $64, $42, $22, $11, $00, $91, $12
.byte $24, $46, $66, $46, $46, $66, $44, $46, $66, $44, $22, $14, $46, $44, $12
		.byte $24, $66, $66, $66, $66, $66, $44, $6F, $F6, $64, $44, $44, $66, $64, $12;($858D)
.byte $24, $66, $46, $64, $46, $66, $46, $6F, $66, $66, $66, $66, $66, $64, $02
		.byte $24, $66, $66, $64, $44, $64, $44, $6F, $F6, $64, $44, $44, $66, $64, $02;($85AB)
.byte $24, $46, $66, $44, $24, $64, $24, $46, $66, $44, $22, $94, $44, $44, $12
.byte $22, $44, $64, $42, $24, $64, $22, $44, $64, $42, $22, $11, $99, $91, $12
.byte $22, $24, $44, $22, $94, $64, $92, $24, $44, $22, $22, $21, $11, $11, $22
.byte $22, $22, $22, $29, $94, $54, $99, $22, $22, $22, $22, $22, $22, $22, $22

;Kol. Map #$07.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Trees, $9-Poison, $A-Force Field,
;$B-Door, $C-Weapon Shop Sign, $D-Inn Sign, $E-Bridge, $F-Large Tile.
KolDat:
		.byte $44, $40, $88, $84, $44, $44, $88, $88, $88, $88, $44, $44;($85F6)
		.byte $46, $40, $08, $84, $66, $64, $88, $88, $88, $4D, $46, $64;($8602)
		.byte $4F, $49, $08, $86, $62, $66, $11, $11, $11, $66, $66, $64;($860E)
		.byte $96, $99, $08, $84, $66, $64, $81, $88, $88, $4F, $44, $44;($861A)
		.byte $99, $90, $04, $44, $46, $44, $81, $88, $88, $46, $48, $88;($8626)
.byte $09, $00, $04, $88, $88, $88, $81, $88, $88, $44, $48, $88
.byte $00, $00, $84, $88, $88, $88, $81, $88, $88, $88, $88, $08
.byte $80, $08, $84, $88, $88, $88, $81, $88, $88, $80, $00, $08
		.byte $88, $44, $44, $44, $88, $88, $11, $18, $88, $00, $08, $00;($8656)
.byte $88, $88, $88, $84, $88, $81, $11, $11, $88, $80, $80, $08
.byte $44, $44, $48, $84, $88, $11, $11, $11, $18, $44, $44, $44
.byte $46, $66, $48, $84, $81, $11, $11, $11, $11, $46, $64, $64
.byte $46, $66, $48, $1B, $11, $11, $11, $11, $11, $66, $6F, $64
.byte $46, $66, $48, $14, $81, $11, $11, $11, $11, $46, $64, $64
		.byte $4B, $44, $46, $14, $88, $11, $11, $11, $18, $44, $44, $44;($869E)
		.byte $46, $46, $66, $64, $88, $81, $11, $11, $88, $88, $88, $88;($86AA)
		.byte $46, $46, $44, $44, $44, $48, $11, $18, $88, $88, $88, $88;($86B6)
		.byte $46, $66, $46, $66, $66, $48, $81, $88, $88, $44, $44, $88;($86C2)
.byte $46, $46, $46, $06, $06, $48, $81, $11, $11, $11, $14, $88
		.byte $46, $46, $66, $66, $66, $48, $44, $44, $48, $11, $14, $88;($86DA)
		.byte $46, $66, $46, $66, $66, $44, $46, $63, $48, $11, $14, $88;($86E6)
.byte $44, $64, $46, $06, $06, $66, $6F, $63, $48, $81, $88, $88
.byte $80, $00, $46, $66, $66, $44, $46, $63, $48, $81, $88, $88
		.byte $88, $00, $44, $44, $44, $48, $44, $44, $48, $81, $88, $88;($870A)

;Brecconary. Map #$08.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Trees, $9-Poison, $A-Force Field,
;$B-Door, $C-Weapon Shop Sign, $D-Inn Sign, $E-Bridge, $F-Large Tile.
BrecconaryDat:
.byte $44, $44, $44, $44, $44, $44, $41, $66, $14, $44, $44, $44, $44, $44, $44
.byte $48, $88, $00, $00, $88, $88, $11, $66, $11, $88, $88, $88, $88, $88, $84
		.byte $48, $80, $00, $00, $08, $08, $01, $66, $10, $08, $44, $44, $44, $44, $84;($8734)
		.byte $48, $04, $44, $44, $00, $00, $00, $66, $00, $08, $46, $64, $62, $24, $84;($8743)
.byte $48, $04, $66, $64, $00, $00, $00, $66, $10, $00, $46, $6F, $62, $24, $84
		.byte $48, $04, $6F, $64, $00, $00, $00, $66, $10, $80, $46, $64, $62, $24, $84;($8761)
.byte $48, $04, $46, $44, $00, $11, $00, $66, $11, $80, $4B, $44, $44, $44, $04
		.byte $48, $00, $06, $C0, $01, $11, $10, $66, $10, $80, $00, $08, $00, $80, $04;($877F)
.byte $48, $80, $06, $00, $11, $81, $10, $66, $10, $00, $00, $88, $88, $88, $04
.byte $48, $00, $06, $00, $18, $88, $11, $66, $00, $44, $44, $44, $44, $48, $04
		.byte $48, $00, $06, $01, $11, $88, $81, $66, $00, $46, $66, $46, $66, $40, $04;($87AC)
		.byte $40, $00, $06, $01, $18, $88, $10, $66, $00, $46, $66, $46, $66, $40, $04;($87BB)
.byte $48, $80, $06, $00, $11, $11, $10, $66, $00, $44, $64, $44, $64, $40, $84
.byte $88, $00, $06, $00, $00, $11, $00, $66, $00, $00, $60, $00, $60, $00, $88
.byte $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66
		.byte $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66;($87F7)
.byte $88, $00, $00, $00, $60, $00, $08, $06, $00, $08, $00, $00, $02, $22, $88
		.byte $48, $80, $00, $00, $60, $00, $88, $06, $08, $88, $80, $22, $22, $22, $28;($8815)
		.byte $48, $00, $00, $00, $60, $08, $80, $06, $88, $80, $02, $22, $22, $22, $22;($8824)
.byte $40, $00, $00, $4D, $64, $00, $00, $06, $08, $00, $22, $22, $22, $22, $22
.byte $40, $44, $44, $44, $64, $44, $00, $06, $80, $02, $22, $20, $02, $22, $22
		.byte $40, $46, $64, $66, $6F, $64, $00, $06, $00, $22, $00, $00, $00, $02, $22;($8851)
.byte $40, $46, $64, $64, $44, $44, $08, $06, $66, $E0, $00, $00, $00, $00, $02
		.byte $40, $46, $6B, $66, $66, $64, $08, $00, $00, $20, $04, $64, $44, $48, $02;($886F)
		.byte $40, $46, $44, $64, $46, $64, $08, $80, $02, $20, $04, $66, $46, $48, $02;($887E)
		.byte $40, $46, $64, $66, $46, $64, $88, $88, $02, $22, $04, $66, $F6, $40, $22;($888D)
		.byte $40, $46, $64, $66, $46, $64, $08, $80, $02, $20, $04, $66, $46, $40, $82;($889C)
		.byte $40, $44, $44, $44, $44, $44, $08, $00, $22, $22, $04, $44, $44, $48, $82;($88AB)
.byte $40, $00, $00, $00, $00, $00, $00, $02, $22, $22, $00, $00, $02, $28, $22
		.byte $44, $44, $44, $44, $44, $44, $44, $44, $44, $44, $22, $22, $22, $22, $22;($88C9)

;Cantlin. Map #$0A.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Trees, $9-Poison, $A-Force Field,
;$B-Door, $C-Weapon Shop Sign, $D-Inn Sign, $E-Bridge, $F-Large Tile.
CantlinDat:
.byte $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66
		.byte $64, $44, $66, $44, $44, $44, $44, $66, $C1, $11, $11, $11, $16, $44, $46;($88E7)
.byte $64, $66, $66, $46, $64, $66, $64, $66, $11, $44, $44, $44, $16, $46, $46
.byte $64, $44, $66, $46, $64, $66, $64, $66, $88, $46, $64, $64, $16, $46, $46
		.byte $66, $66, $66, $44, $F4, $64, $44, $66, $66, $66, $6F, $64, $16, $66, $66;($8914)
		.byte $66, $66, $66, $46, $66, $66, $64, $66, $66, $66, $6F, $64, $16, $44, $46;($8923)
.byte $64, $44, $66, $44, $64, $46, $64, $66, $88, $46, $64, $64, $16, $46, $46
		.byte $64, $6F, $66, $1D, $11, $46, $64, $66, $11, $44, $44, $44, $16, $4F, $46;($8941)
.byte $64, $44, $66, $11, $11, $44, $44, $66, $11, $11, $11, $11, $16, $46, $46
		.byte $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $B6, $46;($895F)
.byte $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $66, $64, $46, $46
		.byte $64, $44, $66, $44, $46, $60, $22, $20, $00, $06, $64, $44, $44, $66, $46;($897D)
.byte $64, $6F, $66, $F6, $46, $62, $22, $22, $00, $06, $64, $64, $6F, $66, $46
.byte $64, $44, $66, $44, $46, $62, $28, $22, $20, $06, $6F, $64, $64, $66, $46
		.byte $64, $6F, $66, $66, $66, $60, $22, $20, $22, $06, $64, $44, $44, $44, $46;($89AA)
.byte $64, $44, $64, $44, $46, $60, $00, $00, $0E, $06, $66, $66, $66, $66, $66
.byte $64, $66, $64, $66, $46, $60, $00, $00, $02, $06, $66, $66, $66, $66, $66
.byte $64, $66, $66, $66, $46, $60, $00, $00, $22, $06, $64, $44, $66, $44, $46
.byte $64, $44, $44, $44, $46, $60, $00, $22, $22, $26, $6F, $64, $66, $66, $46
.byte $66, $66, $66, $66, $66, $60, $02, $22, $82, $26, $64, $44, $66, $46, $46
.byte $66, $66, $66, $66, $66, $60, $22, $28, $82, $26, $66, $66, $66, $44, $46
.byte $64, $44, $B4, $44, $46, $60, $22, $88, $22, $06, $64, $44, $66, $66, $66
.byte $64, $11, $11, $11, $46, $60, $02, $22, $20, $06, $64, $64, $44, $46, $46
.byte $64, $11, $11, $11, $46, $60, $00, $22, $00, $06, $64, $F4, $66, $66, $46
.byte $64, $44, $44, $11, $46, $66, $46, $66, $64, $66, $64, $64, $46, $44, $46
.byte $64, $66, $64, $11, $B6, $44, $44, $BB, $44, $44, $66, $64, $66, $43, $46
.byte $64, $66, $6F, $11, $46, $4A, $AA, $AA, $AA, $A4, $64, $66, $66, $F6, $46
.byte $64, $36, $64, $11, $46, $4A, $44, $44, $44, $A4, $64, $64, $66, $43, $46
.byte $64, $44, $44, $44, $46, $4A, $AA, $66, $AA, $A4, $64, $44, $44, $44, $46
.byte $66, $66, $66, $66, $66, $44, $44, $44, $44, $44, $66, $66, $66, $66, $66

;Garinham. Map #$09.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Trees, $9-Poison, $A-Force Field,
;$B-Door, $C-Weapon Shop Sign, $D-Inn Sign, $E-Bridge, $F-Large Tile.
GarinhamDat:
		.byte $22, $46, $66, $66, $66, $66, $66, $66, $22, $47;($8A9A)
		.byte $22, $46, $11, $11, $11, $11, $11, $16, $6E, $66;($8AA4)
		.byte $44, $46, $44, $44, $44, $44, $44, $44, $42, $44;($8AAE)
		.byte $46, $66, $66, $66, $66, $66, $64, $44, $42, $22;($8AB8)
		.byte $46, $44, $44, $46, $66, $66, $62, $22, $42, $44;($8AC2)
		.byte $46, $46, $66, $46, $33, $66, $64, $22, $22, $24;($8ACC)
		.byte $46, $44, $B4, $46, $36, $66, $64, $24, $24, $24;($8AD6)
		.byte $46, $66, $66, $66, $66, $66, $66, $66, $66, $64;($8AE0)
.byte $46, $66, $66, $66, $66, $66, $66, $66, $66, $64
.byte $44, $44, $44, $44, $44, $44, $44, $44, $66, $64
		.byte $24, $66, $46, $48, $88, $88, $88, $84, $4B, $44;($8AFE)
.byte $24, $66, $F6, $48, $80, $66, $60, $88, $86, $88
.byte $44, $64, $44, $48, $00, $68, $66, $66, $66, $66
		.byte $00, $60, $00, $00, $66, $66, $60, $06, $00, $00;($8B1C)
.byte $66, $66, $66, $66, $60, $60, $00, $D6, $44, $48
.byte $88, $80, $60, $80, $00, $6C, $00, $46, $F6, $44
		.byte $44, $44, $64, $81, $44, $64, $40, $46, $44, $44;($8B3A)
.byte $24, $66, $64, $41, $46, $F6, $40, $46, $46, $64
		.byte $24, $44, $44, $24, $46, $66, $40, $46, $66, $64;($8B4E)
		.byte $22, $22, $22, $22, $44, $44, $40, $44, $44, $44;($8B58)

;Rimuldar. Map #$0B.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Trees, $9-Poison, $A-Force Field,
;$B-Door, $C-Weapon Shop Sign, $D-Inn Sign, $E-Bridge, $F-Large Tile.
RimuldarDat:
.byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
.byte $00, $02, $22, $22, $22, $22, $22, $22, $22, $00, $00, $00, $00, $00, $00
.byte $02, $22, $44, $48, $80, $00, $00, $00, $02, $22, $20, $00, $00, $00, $00
.byte $0E, $00, $66, $48, $00, $00, $08, $88, $00, $08, $22, $22, $00, $00, $00
.byte $22, $00, $66, $40, $00, $06, $66, $66, $66, $68, $80, $02, $22, $20, $00
.byte $28, $46, $66, $40, $80, $06, $08, $06, $11, $60, $00, $00, $88, $20, $00
.byte $28, $44, $F4, $40, $04, $46, $44, $46, $44, $60, $04, $44, $44, $20, $00
.byte $20, $46, $66, $40, $04, $66, $64, $66, $64, $60, $04, $66, $64, $22, $00
.byte $20, $44, $44, $40, $04, $66, $64, $66, $64, $68, $04, $4F, $44, $12, $00
.byte $20, $00, $00, $00, $04, $44, $44, $44, $44, $66, $66, $66, $64, $12, $00
.byte $20, $00, $00, $02, $28, $00, $00, $08, $00, $60, $C4, $66, $64, $12, $00
.byte $20, $80, $22, $22, $22, $00, $06, $66, $66, $66, $04, $66, $64, $12, $20
		.byte $21, $02, $28, $88, $22, $08, $66, $66, $66, $66, $04, $44, $44, $80, $20;($8C16)
		.byte $21, $22, $80, $08, $20, $06, $66, $00, $00, $66, $00, $00, $88, $88, $20;($8C25)
		.byte $21, $11, $80, $82, $20, $66, $60, $08, $00, $66, $66, $66, $66, $66, $E6;($8C34)
		.byte $21, $22, $88, $22, $00, $66, $00, $88, $00, $66, $66, $66, $66, $66, $E6;($8C43)
.byte $21, $02, $22, $20, $00, $66, $08, $80, $4D, $60, $08, $80, $08, $88, $20
.byte $20, $80, $00, $08, $00, $66, $00, $84, $44, $64, $44, $44, $44, $80, $20
		.byte $20, $00, $00, $88, $80, $66, $08, $84, $6F, $64, $66, $46, $64, $02, $20;($8C70)
.byte $20, $44, $44, $44, $44, $66, $40, $84, $44, $66, $66, $66, $64, $02, $00
		.byte $20, $46, $66, $66, $66, $66, $40, $04, $66, $66, $66, $46, $64, $82, $00;($8C8E)
		.byte $20, $46, $66, $64, $66, $66, $40, $84, $46, $44, $4B, $44, $44, $82, $00;($8C9D)
.byte $20, $44, $46, $64, $66, $66, $40, $14, $66, $64, $66, $46, $64, $22, $00
		.byte $28, $46, $F6, $66, $64, $46, $40, $14, $66, $64, $66, $B6, $34, $20, $00;($8CBB)
.byte $28, $44, $46, $64, $66, $66, $40, $14, $44, $44, $44, $44, $44, $20, $00
.byte $22, $46, $66, $64, $66, $66, $48, $11, $11, $80, $08, $82, $22, $20, $00
.byte $02, $46, $66, $66, $66, $66, $48, $80, $08, $00, $22, $22, $00, $00, $00
		.byte $02, $44, $44, $44, $44, $44, $48, $88, $82, $22, $20, $00, $00, $00, $00;($8CF7)
		.byte $00, $02, $22, $22, $22, $22, $22, $22, $22, $00, $00, $00, $00, $00, $00;($8D06)
		.byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00;($8D15)

;----------------------------------------------------------------------------------------------------

;Below is the covered area data for Tantagel. The covered areas are shown with _.
;The starting address is $8D24.

;$46, $66, $66, $66, $64, $64, $66, $66, $66, $46, $66, $66, $66, $66, $66
;$66, $64, $44, $46, $66, $56, $64, $66, $46, $66, $66, $64, $36, $46, $66
;$66, $64, $66, $46, $66, $66, $66, $66, $66, $66, ___, ___, ___, ___, $46
;$46, $66, $66, $66, $64, $46, $66, $66, $66, $64, ___, ___, ___, ___, $66
;$66, $44, $44, $44, $66, $66, $46, $64, $64, $66, ___, ___, ___, ___, $66
;$66, $46, $64, $64, $66, $66, $44, $44, $44, $66, __6, ___, ___, ___, $66
;$46, $66, $66, $66, $64, $44, $44, $56, $44, $44, $22, $22, $22, $22, $01
;$02, $22, $02, $22, $22, $20, $00, $00, $22, $02, $22, $02, $03, $00, $02
;$20, $22, $20, $02, $00, $00, $02, $00, $02, $22, $20, $22, $22, $02, $22
;$22, $22, $00, $22, $02, $20, $32, $02, $00, $22, $22, $20, $02, $20, $00
;$20, $00, $02, $20, $00, $00, $00, $22, $00, $22, $22, $22, $00, $20, $22
;$22, $02, $20, $02, $22, $00, $22, $02, $20, $02, $20, $03, $20, $22, $03
;$20, $02, $02, $00, $22, $22, $00, $00, $22, $00, $22, $22, $02, $02, $20
;$02, $20, $30, $02, $02, $20, $00, $02, $02, $20, $02, $20, $22, $02, $02
;$20, $22, $22, $00, $22, $22, $00, $22, $02, $02, $20, $20, $22, $20, $02
;$20, $02, $20, $02, $02, $20, $20, $00, $20, $12, $22, $02, $22, $22, $02
;$20, $30, $22, $20, $00, $00, $00, $02, $00, $02, $20, $00, $20, $00, $22
;$22, $22, $22, $01, $22, $20, $22, $22, $22, $20, $00, $02, $00, $02, $22
;$20, $22, $00, $00, $22, $20, $22, $22, $02, $22, $20, $00, $02, $20, $00
;$20, $00, $02, $22, $02, $22, $22, $22, $22, $30, $22, $22, $22, $02, $22
;$12, $03, $01, $20, $12, $1_, $0_, ___, __0, $03, $00, $22, $20, $22, $00
;$22, $20, $00, $02, $22, $2_, ___, ___, __2, $02, $20, $20, $24, $00, $02
;$22, $20, $00, $02, $22, $0_, ___, ___, __2, $00, $30, $02, $00, $20, $01
;$23, $02, $22, $20, $12, $2_, ___, ___, __1, $22, $20, $00, $22, $00, $02
;$20, $10, $22, $22, $22, $2_, ___, ___, __0, $02, $20, $22, $01, $22, $02
;$20, $02, $00, $02, $02, $23, $02, $22, $00, $02, $00, $00, $02, $23, $02
;$22, $22, $00, $00, $02, $12, $02, $22, $22, $22, $22, $22, $22, $22, $22

;----------------------------------------------------------------------------------------------------

;Tantagel castle - sublevel. Map #$0C.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Grass, $9-Sand, $A-Water,
;$B-Treasure Chest, $C-Stone, $D-Stairs Up, $E-Brick, $F-Stairs Down.
TantSLDat:
.byte $46, $66, $66, $66, $64
.byte $64, $66, $66, $66, $46
		.byte $66, $66, $66, $66, $66;($8D2E)
		.byte $66, $64, $44, $46, $66;($8D33)
		.byte $56, $64, $66, $46, $66;($8D38)
		.byte $66, $64, $36, $46, $66;($8D3D)
.byte $66, $64, $66, $46, $66
		.byte $66, $66, $66, $66, $66;($8D47)
		.byte $EC, $EE, $EE, $EE, $46;($8D4C)
.byte $46, $66, $66, $66, $64

;Staff of rain cave. Map #$0D.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Grass, $9-Sand, $A-Water,
;$B-Treasure Chest, $C-Stone, $D-Stairs Up, $E-Brick, $F-Stairs Down.
RainCaveDat:
		.byte $46, $66, $66, $66, $64;($8D56)
.byte $EE, $EE, $EE, $EE, $66
.byte $66, $44, $44, $44, $66
		.byte $66, $46, $64, $64, $66;($8D65)
.byte $EE, $CB, $EE, $EE, $66
.byte $66, $46, $64, $64, $66
		.byte $66, $44, $44, $44, $66;($8D74)
		.byte $EE, $EE, $EE, $EE, $66;($8D79)
		.byte $46, $66, $66, $66, $64;($8D7E)
.byte $44, $44, $56, $44, $44

;Rainbow drop cave. Map #$0E.
;Tile mapping: $0-Grass, $1-Sand, $2-Water, $3-Treasure Chest, $4-Stone,
;$5-Stairs Up, $6-Brick, $7-Stairs Down, $8-Grass, $9-Sand, $A-Water,
;$B-Treasure Chest, $C-Stone, $D-Stairs Up, $E-Brick, $F-Stairs Down.
DropCaveDat:
		.byte $C6, $EE, $EE, $EE, $66;($8D88)
.byte $46, $64, $64, $64, $66
		.byte $46, $44, $66, $64, $46;($8D92)
.byte $46, $66, $44, $46, $66
		.byte $56, $46, $46, $46, $46;($8D9C)
.byte $66, $46, $63, $46, $46
.byte $46, $66, $44, $46, $66
		.byte $46, $44, $66, $64, $46;($8DAB)
		.byte $46, $64, $64, $64, $66;($8DB0)
.byte $46, $66, $66, $66, $66

;Dragonlord's castle - sublevel 1. Map #$0F.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
DgnLrdSL1Dat:
		.byte $22, $22, $22, $22, $01, $02, $22, $02, $22, $22;($8DBA)
		.byte $20, $00, $00, $22, $02, $22, $02, $03, $00, $02;($8DC4)
.byte $20, $22, $20, $02, $00, $00, $02, $00, $02, $22
.byte $20, $22, $22, $02, $22, $22, $22, $00, $22, $02
.byte $20, $32, $02, $00, $22, $22, $20, $02, $20, $00
.byte $20, $00, $02, $20, $00, $00, $00, $22, $00, $22
.byte $22, $22, $00, $20, $22, $22, $02, $20, $02, $22
.byte $00, $22, $02, $20, $02, $20, $03, $20, $22, $03
.byte $20, $02, $02, $00, $22, $22, $00, $00, $22, $00
		.byte $22, $22, $02, $02, $20, $02, $20, $30, $02, $02;($8E14)
.byte $20, $00, $02, $02, $20, $02, $20, $22, $02, $02
.byte $20, $22, $22, $00, $22, $22, $00, $22, $02, $02
		.byte $20, $20, $22, $20, $02, $20, $02, $20, $02, $02;($8E32)
		.byte $20, $20, $00, $20, $12, $22, $02, $22, $22, $02;($8E3C)
		.byte $20, $30, $22, $20, $00, $00, $00, $02, $00, $02;($8E46)
.byte $20, $00, $20, $00, $22, $22, $22, $22, $01, $22
		.byte $20, $22, $22, $22, $20, $00, $02, $00, $02, $22;($8E5A)
.byte $20, $22, $00, $00, $22, $20, $22, $22, $02, $22
		.byte $20, $00, $02, $20, $00, $20, $00, $02, $22, $02;($8E6E)
.byte $22, $22, $22, $22, $30, $22, $22, $22, $02, $22

;Dragonlord's castle - sublevel 2. Map #$10.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
DgnLrdSL2Dat:
.byte $12, $03, $01, $20, $12
		.byte $18, $0A, $88, $A0, $03;($8E87)
.byte $00, $22, $20, $22, $00
.byte $22, $20, $00, $02, $22
		.byte $28, $88, $9A, $82, $02;($8E96)
.byte $20, $20, $24, $00, $02
		.byte $22, $20, $00, $02, $22;($8EA0)
.byte $08, $AA, $8A, $A2, $00
		.byte $30, $02, $00, $20, $01;($8EAA)
.byte $23, $02, $22, $20, $12

;Dragonlord's castle - sublevel 3. Map #$11.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
DgnLrdSL3Dat:
		.byte $2A, $AA, $AA, $81, $22;($8EB4)
.byte $20, $00, $22, $00, $02
		.byte $20, $10, $22, $22, $22;($8EBE)
.byte $28, $A8, $88, $A0, $02
		.byte $20, $22, $01, $22, $02;($8EC8)
.byte $20, $02, $00, $02, $02
.byte $23, $02, $22, $00, $02
.byte $00, $00, $02, $23, $02
.byte $22, $22, $00, $00, $02
.byte $12, $02, $22, $22, $22

;----------------------------------------------------------------------------------------------------

;Below is the covered area data for Garinham. The covered areas are shown with _.
;The starting address is $8EE6.

;$22, $22, $22, $22, $22, $20, $00, $00, $02, $32
;$20, $32, $22, $22, $22, $20, $00, $02, $22, $02
;$22, $22, $02, $22, $02, $20, $02, $00, $02, $02
;___, ___, ___, ___, ___, ___, ___, ___, ___, ___
;___, ___, ___, ___, ___, ___, ___, ___, ___, ___
;___, ___, ___, ___, ___, ___, ___, ___, ___, ___
;___, ___, ___, ___, ___, ___, ___, ___, ___, ___
;___, ___, ___, ___, ___, ___, ___, ___, ___, ___
;___, ___, ___, ___, ___, ___, ___, ___, ___, ___
;___, ___, ___, ___, ___, ___, ___, ___, ___, ___
;$12, $22, $22, $22, $23, $00, $00, $0_, __0, ___
;$00, $00, $00, $00, $00, $00, $00, $00, $00, $00
;$02, $22, $22, $22, $20, $02, $22, $22, $22, $20
;$12, $22, $22, $22, $23, $02, $22, $22, $22, $20
;$02, $22, $22, $22, $20, $00, $00, $00, $00, $00
;$12, $22, $22, $20, $02, $00, $20, $22, $02, $20
;$02, $22, $22, $22, $02, $20, $20, $02, $22, $00
;$22, $20, $02, $22, $22, $22, $02, $20, $20, $02
;$20, $22, $22, $20, $22, $02, $20, $20, $02, $20
;$22, $22, $20, $00, $20, $20, $22, $22, $20, $20

;----------------------------------------------------------------------------------------------------

;Dragonlord's castle - sublevel 4. Map #$12.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
DgnLrdSL4Dat:
.byte $22, $22, $22, $22, $22
.byte $20, $00, $00, $02, $32
.byte $20, $32, $22, $22, $22
		.byte $20, $00, $02, $22, $02;($8EF5)
.byte $22, $22, $02, $22, $02
		.byte $20, $02, $00, $02, $02;($8EFF)
.byte $88, $AA, $AA, $8A, $8A
		.byte $8A, $AA, $8A, $89, $8A;($8F09)
.byte $AA, $A8, $8A, $88, $8A
.byte $9A, $88, $AA, $AA, $AA

;Dragonlord's castle - sublevel 5. Map #$13.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
DgnLrdSL5Dat:
		.byte $B8, $A8, $9A, $AA, $89;($8F18)
.byte $A8, $A8, $88, $8A, $8A
		.byte $A8, $AA, $AA, $8A, $8A;($8F22)
.byte $A8, $A8, $8A, $8A, $8A
.byte $A8, $A8, $AA, $8A, $8A
		.byte $A8, $A8, $AB, $8A, $8A;($8F31)
		.byte $A8, $A8, $88, $8A, $8A;($8F36)
.byte $A8, $AA, $AA, $AA, $8A
		.byte $A8, $88, $88, $88, $8A;($8F40)
.byte $AA, $AA, $AA, $AA, $AA

;Dragonlord's castle - sublevel 6. Map #$14.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
DgnLrdSL6Dat:
.byte $12, $22, $22, $22, $23
		.byte $00, $00, $08, $80, $88;($8F4F)
		.byte $00, $00, $00, $00, $00;($8F54)
.byte $00, $00, $00, $00, $00
.byte $02, $22, $22, $22, $20
		.byte $02, $22, $22, $22, $20;($8F63)
		.byte $12, $22, $22, $22, $23;($8F68)
.byte $02, $22, $22, $22, $20
		.byte $02, $22, $22, $22, $20;($8F72)
.byte $00, $00, $00, $00, $00

;----------------------------------------------------------------------------------------------------

;Below is the covered area data for Cantlin. The covered areas are shown with _.
;The starting address is $AFAE.

;$00, $20, $20, $22, $20, $20, $26, $20, $20, $22, $20, $20, $05, $20, $22
;$2_, ___, $00, $00, $22, $22, $02, $20, $02, $02, $22, $02, $22, ___, __2
;$0_, __0, $02, $22, $22, $02, $02, $12, $22, $02, $32, $22, $00, ___, __2
;$2_, ___, $20, $02, $22, $22, $20, $20, $02, $20, $20, $00, $00, __0, __0
;$22, $22, $22, $22, $22, $20, $20, $22, $00, $00, $20, $00, $00, $20, $22
;$22, $22, $20, $32, $22, $20, $24, $00, $20, $02, $00, $00, $00, $00, $12
;$22, $22, $22, $20, $22, $20, $00, $20, $00, $00, $22, $20, $20, $22, $22
;$20, $22, $20, $22, $22, $20, $00, $20, $20, $20, $00, $20, $22, $22, $22
;$20, $22, $22, $22, $20, $20, $20, $00, $20, $22, $32, $22, $22, $22, $22
;$20, $22, $22, $12, $02, $22, $22, $22, $22, $22, $22, $02, $02, $02, $00
;$20, $02, $00, $44, $02, $02, $02, $22, $02, $20, $00, $22, $00, $02, $22
;$22, $22, $22, $20, $22, $0_, ___, ___, ___, __0, $20, $12, $22, $22, $22
;$24, $20, $20, $22, $00, $2_, ___, ___, ___, __0, $00, $02, $20, $22, $02
;$00, $22, $22, $02, $20, $2_, ___, ___, ___, __2, $22, $40, $02, $20, $00
;$22, $20, $00, $02, $00, $2_, ___, ___, ___, __0, $22, $22, $20, $00, $00
;$00, $20, $20, $12, $22, $2_, ___, ___, ___, __2, $22, $22, $22, $22, $22
;$02, $04, $44, $02, $22, $2_, ___, ___, ___, __2, $22, $02, $22, $22, $00
;$22, $20, $22, $22, $02, $0_, ___, ___, ___, __2, $02, $20, $20, $02, $22
;$02, $02, $00, $00, $02, $0_, ___, ___, ___, __0, $02, $00, $02, $02, $02
;$22, $20, $00, $02, $22, $0_, ___, ___, ___, __2, $02, $22, $22, $00, $00
;$02, $02, $02, $02, $02, $0_, ___, ___, ___, __2, $22, $22, $22, $22, $22
;$22, $20, $20, $02, $00, $0_, ___, ___, ___, __0, $02, $20, $20, $22, $22
;$22, $02, $22, $22, $02, $2_, ___, ___, ___, __0, $02, $00, $00, $02, $22
;$22, $20, $22, $20, $12, $2_, ___, ___, ___, __0, $22, $20, $20, $20, $22
;$22, $02, $02, $22, $00, $20, $20, $20, $00, $00, $02, $00, $00, $02, $20
;$22, $20, $22, $20, $22, $22, $22, $22, $00, $00, $02, $00, $00, $20, $00
;$00, $02, $02, $02, $02, $02, $22, $20, $00, $22, $22, $22, $22, $02, $22
;$22, $22, $02, $02, $20, $20, $00, $00, $00, $05, $00, $23, $22, $00, $00
;$00, $20, $22, $20, $22, $22, $22, $22, $22, $22, $22, $22, $20, $22, $20
;$22, $22, $20, $22, $20, $22, $22, $22, $22, $02, $22, $24, $20, $22, $22

;----------------------------------------------------------------------------------------------------

;Swamp cave. Map #$15.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
SwampCaveDat:
		.byte $12, $22, $22	 ;($8F7C)
.byte $20, $02, $00
		.byte $20, $22, $02	 ;($8F82)
.byte $20, $02, $22
		.byte $22, $22, $02	 ;($8F88)
		.byte $20, $20, $02	 ;($8F8B)
		.byte $22, $00, $22	 ;($8F8E)
.byte $20, $02, $22
.byte $22, $22, $02
		.byte $20, $20, $02	 ;($8F97)
		.byte $20, $22, $22	 ;($8F9A)
.byte $20, $22, $02
.byte $20, $20, $02
.byte $20, $22, $22
.byte $20, $00, $20
.byte $20, $22, $22
.byte $20, $20, $00
.byte $20, $20, $22
		.byte $20, $20, $26	 ;($8FB2)
.byte $20, $20, $22
		.byte $20, $20, $05	 ;($8FB8)
.byte $20, $22, $2A
.byte $A8, $00, $00
.byte $22, $22, $02
		.byte $20, $02, $02	 ;($8FC4)
.byte $22, $02, $22
		.byte $8A, $A2, $08	 ;($8FCA)
.byte $80, $02, $22
		.byte $22, $02, $02	 ;($8FD0)
.byte $12, $22, $02

;Rock mountain cave - B1. Map #$16.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
RckMtnB1Dat:
		.byte $32, $22, $00, $88, $A2, $2A, $AA;($8FD6)
.byte $20, $02, $22, $22, $20, $20, $02
.byte $20, $20, $00, $00, $80, $A0, $22
		.byte $22, $22, $22, $22, $20, $20, $22;($8FEB)
.byte $00, $00, $20, $00, $00, $20, $22
.byte $22, $22, $20, $32, $22, $20, $24
.byte $00, $20, $02, $00, $00, $00, $00
.byte $12, $22, $22, $22, $20, $22, $20
.byte $00, $20, $00, $00, $22, $20, $20
		.byte $22, $22, $20, $22, $20, $22, $22;($9015)
.byte $20, $00, $20, $20, $20, $00, $20
		.byte $22, $22, $22, $20, $22, $22, $22;($9023)
.byte $20, $20, $20, $00, $20, $22, $32
		.byte $22, $22, $22, $22, $20, $22, $22;($9031)

;Rock mountain cave - B2. Map #$17.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
RckMtnB2Dat:
.byte $12, $02, $22, $22, $22, $22, $22
		.byte $22, $02, $02, $02, $00, $20, $02;($903F)
.byte $00, $44, $02, $02, $02, $22, $02
		.byte $20, $00, $22, $00, $02, $22, $22;($904D)
		.byte $22, $22, $20, $22, $08, $A8, $88;($9054)
.byte $88, $80, $20, $12, $22, $22, $22
.byte $24, $20, $20, $22, $00, $28, $8A
.byte $AA, $A8, $A0, $00, $02, $20, $22
.byte $02, $00, $22, $22, $02, $20, $2A
.byte $AA, $A8, $88, $A2, $22, $40, $02
.byte $20, $00, $22, $20, $00, $02, $00
		.byte $28, $AA, $A8, $AA, $A0, $22, $22;($9085)
.byte $20, $00, $00, $00, $20, $20, $12
.byte $22, $2A, $AA, $AA, $A8, $A2, $22

;Cave of garinham - B1. Map #$18.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
GarinCaveB1Dat:
		.byte $22, $22, $22, $22, $02, $04, $44, $02, $22, $28;($909A)
		.byte $A8, $88, $88, $82, $22, $02, $22, $22, $00, $22;($90A4)
.byte $20, $22, $22, $02, $0A, $8A, $AA, $8A, $A2, $02
		.byte $20, $20, $02, $22, $02, $02, $00, $00, $02, $0A;($90B8)
		.byte $A8, $AA, $AA, $80, $02, $00, $02, $02, $02, $22;($90C2)
.byte $20, $00, $02, $22, $0A, $AA, $8A, $8A, $82, $02
		.byte $22, $22, $00, $00, $02, $02, $02, $02, $02, $0A;($90D6)
		.byte $A8, $AA, $8A, $A2, $22, $22, $22, $22, $22, $22;($90E0)
		.byte $20, $20, $02, $00, $0A, $88, $88, $8A, $80, $02;($90EA)
		.byte $20, $20, $22, $22, $22, $02, $22, $22, $02, $2A;($90F4)
.byte $A8, $A8, $A8, $A0, $02, $00, $00, $02, $22, $22
		.byte $20, $22, $20, $12, $2A, $8A, $AA, $8A, $80, $22;($9108)
		.byte $20, $20, $20, $22, $22, $02, $02, $22, $00, $20;($9112)
.byte $20, $20, $00, $00, $02, $00, $00, $02, $20, $22
		.byte $20, $22, $20, $22, $22, $22, $22, $00, $00, $02;($9126)
.byte $00, $00, $20, $00, $00, $02, $02, $02, $02, $02
.byte $22, $20, $00, $22, $22, $22, $22, $02, $22, $22
		.byte $22, $02, $02, $20, $20, $00, $00, $00, $05, $00;($9144)
		.byte $23, $22, $00, $00, $00, $20, $22, $20, $22, $22;($914E)
.byte $22, $22, $22, $22, $22, $22, $20, $22, $20, $22

;----------------------------------------------------------------------------------------------------

;Below is the covered area data for Rimuldar. The covered areas are shown with _.
;The starting address is $9170.

;$20, $20, $20, $12, $02, $12, $22, $20, $20, $00, $00, $22, $22, $22, $02
;$22, $20, $00, $20, $20, $20, $00, $00, $00, $00, $00, $20, $22, $20, $22
;$22, $00, ___, __0, $02, $22, $20, $20, $00, $20, $23, $02, $22, $22, $00
;$02, $22, $2_, __2, $20, $00, $02, $24, $22, $02, $02, $20, $00, $20, $20
;$20, $02, ___, __2, $02, $02, $20, $20, $20, $20, $20, $22, $22, $20, $02
;$22, ___, ___, __2, $20, $20, $32, $00, $00, $02, $02, $20, $20, $20, $00
;$20, ___, ___, __2, $22, $02, $20, $20, $20, $12, $22, $22, $22, $02, $20
;$02, ___, ___, __0, $00, $00, $00, $00, $00, $20, $22, $20, $20, $20, $22
;$22, ___, ___, __2, $20, $12, $20, $22, $20, $22, $02, $02, $00, $02, $00
;$02, $20, $02, $20, $22, $02, $02, $22, $22, $02, $22, $20, $22, $00, $00
;$02, $00, $00, $02, $02, $02, $20, $12, $22, $22, $22, $02, $22, $22, $02
;$02, $20, $00, $00, $00, $00, $00, $00, $02, $00, $02, $22, $22, $22, $22
;$22, $22, $22, $22, $22, $22, $00, $00, $02, $00, $00, $00, $00, $22, $20
;$00, $00, $02, $20, $22, $00, $00, $22, $00, $02, $20, $12, $20, $01, $22
;$22, $00, $22, $00, $02, $20, $00, $02, $20, $22, $00, $00, $00, $22, $20
;$00, $00, $00, $02, $00, $00, $00, $00, $00, $00, $00, $22, $22, $22, $22
;$22, $22, $22, $23, $02, $00, $00, $00, $02, $32, $20, $02, $22, $22, $22
;$01, $22, $22, $00, $00, $00, $02, $00, $02, $22, $02, $22, $22, $22, $22
;$02, $22, $02, $02, $02, $02, $02, $02, $22, $02, $23, $22, $02, $02, $02
;$22, ___, ___, ___, ___, $00, __2, $22, $02, $22, $22, $02, $22, $22, $20
;$00, ___, ___, ___, ___, ___, __3, $02, $22, $22, $22, $20, $32, $22, $22
;$22, ___, ___, ___, ___, ___, __2, $22, $20, $02, $02, $02, $00, $22, $22
;$22, ___, ___, ___, ___, ___, __0, $02, $00, $22, $22, $02, $22, $02, $20
;$20, ___, ___, ___, ___, ___, __2, $22, $02, $02, $00, $20, $20, $02, $22
;$02, ___, ___, ___, ___, ___, __2, $02, $22, $03, $22, $22, $22, $22, $22
;$20, ___, ___, ___, ___, ___, __2, $20, $20, $22, $00, $02, $00, $22, $24
;$22, ___, ___, ___, ___, ___, __0, $02, $02, $00, $20, $02, $02, $22, $22
;$22, ___, ___, ___, ___, ___, __2, $20, $20, $22, $22, $20, $22, $20, $12
;$00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
;$00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

;----------------------------------------------------------------------------------------------------

;Cave of garinham - B3. Map #$1A.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
GarinCaveB3Dat:
.byte $22, $20, $22, $20, $22, $22, $22, $22, $02, $22
.byte $24, $20, $22, $22, $20, $20, $20, $12, $02, $12
.byte $22, $20, $20, $00, $00, $22, $22, $22, $02, $22
.byte $20, $00, $20, $20, $20, $00, $00, $00, $00, $00
.byte $20, $22, $20, $22, $22, $00, $AA, $A0, $02, $22
		.byte $20, $20, $00, $20, $23, $02, $22, $22, $00, $02;($9194)
.byte $22, $28, $A2, $20, $00, $02, $24, $22, $02, $02
		.byte $20, $00, $20, $20, $20, $02, $AA, $A2, $02, $02;($91A8)
.byte $20, $20, $20, $20, $20, $22, $22, $20, $02, $22
		.byte $A8, $A8, $A2, $20, $20, $32, $00, $00, $02, $02;($91BC)
.byte $20, $20, $20, $00, $20, $88, $8A, $82, $22, $02
		.byte $20, $20, $20, $12, $22, $22, $22, $02, $20, $02;($91D0)
.byte $A8, $A8, $A0, $00, $00, $00, $00, $00, $20, $22
		.byte $20, $20, $20, $22, $22, $8A, $AA, $A2, $20, $12;($91E4)
.byte $20, $22, $20, $22, $02, $02, $00, $02, $00, $02
		.byte $20, $02, $20, $22, $02, $02, $22, $22, $02, $22;($91F8)
.byte $20, $22, $00, $00, $02, $00, $00, $02, $02, $02
		.byte $20, $12, $22, $22, $22, $02, $22, $22, $02, $02;($920C)
.byte $20, $00, $00, $00, $00, $00, $00, $02, $00, $02
		.byte $22, $22, $22, $22, $22, $22, $22, $22, $22, $22;($9220)

;Cave of garinham - B4. Map #$1B.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
GarinCaveB4Dat:
.byte $00, $00, $02, $00, $00
		.byte $00, $00, $22, $20, $00;($922F)
.byte $00, $02, $20, $22, $00
		.byte $00, $22, $00, $02, $20;($9239)
		.byte $12, $20, $01, $22, $22;($923E)
.byte $00, $22, $00, $02, $20
		.byte $00, $02, $20, $22, $00;($9248)
		.byte $00, $00, $22, $20, $00;($924D)
		.byte $00, $00, $02, $00, $00;($9252)
.byte $00, $00, $00, $00, $00

;Cave of garinham - B2. Map #$19.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
GarinCaveB2Dat:
.byte $22, $22, $22, $22, $22, $22, $22
.byte $23, $02, $00, $00, $00, $02, $32
.byte $20, $02, $22, $22, $22, $01, $22
.byte $22, $00, $00, $00, $02, $00, $02
		.byte $22, $02, $22, $22, $22, $22, $02;($9278)
		.byte $22, $02, $02, $02, $02, $02, $02;($927F)
		.byte $22, $02, $23, $22, $02, $02, $02;($9286)
.byte $22, $8A, $8A, $8A, $88, $00, $82
		.byte $22, $02, $22, $22, $02, $22, $22;($9294)
.byte $20, $00, $88, $88, $88, $88, $8A
		.byte $A3, $02, $22, $22, $22, $20, $32;($92A2)
		.byte $22, $22, $22, $AA, $AA, $AA, $AA;($92A9)

;Erdrick's cave - B1. Map #$1C.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
ErdCaveB1Dat:
		.byte $9A, $82, $22, $20, $02;($92B0)
.byte $02, $02, $00, $22, $22
.byte $22, $AA, $AA, $A8, $8A
.byte $8A, $80, $02, $00, $22
		.byte $22, $02, $22, $02, $20;($92C4)
		.byte $20, $88, $8A, $AA, $88;($92C9)
		.byte $AA, $A2, $22, $02, $02;($92CE)
		.byte $00, $20, $20, $02, $22;($92D3)
		.byte $02, $AA, $AA, $8A, $8A;($92D8)
		.byte $8A, $82, $02, $22, $03;($92DD)

;Erdrick's cave - B2. Map #$1D.
;Tile mapping: $0-Stone, $1-Stairs Up, $2-Brick, $3-Stairs Down,
;$4-Treasure Chest, $5-Door, $6-Gwaelin, $7-Blank, $8-Stone, $9-Stairs Up,
;$A-Brick, $B-Stairs Down, $C-Treasure Chest, $D-Door, $E-Gwaelin, $F-Blank.
ErdCaveB2Dat:
.byte $22, $22, $22, $22, $22
		.byte $20, $88, $88, $A8, $88;($92E7)
		.byte $AA, $A2, $20, $20, $22;($92EC)
.byte $00, $02, $00, $22, $24
.byte $22, $AA, $8A, $88, $AA
.byte $A8, $A0, $02, $02, $00
.byte $20, $02, $02, $22, $22
.byte $22, $AA, $88, $A8, $8A
.byte $8A, $82, $20, $20, $22
.byte $22, $20, $22, $20, $12

;----------------------------------------------------------------------------------------------------

;Left over covered map data for Rimuldar.
.byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00
.byte $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00, $00

;----------------------------------------------------------------------------------------------------

;The following table contains all the sprites that compose the characters in the game.
;There are two bytes assiciated with each sprite.  The first byte is the tile pattern number
;and the second byte is the sprite attribute byte and controls the palette, mirroring and
;background/foreground attributes.

CharSpriteTblPtr:
.word CharSpriteTbl	 ;Pointer to the table below.

CharSpriteTbl:
;Male villager, facing back, right side extended.
.byte $00, $00
.byte $00, $40
.byte $02, $00
		.byte $03, $00		  ;($933A)

;Male villager, facing back, left side extended.
.byte $00, $00
		.byte $00, $40		  ;($933E)
.byte $03, $40
.byte $02, $40

;Fighter, facing back, right side extended.
.byte $D8, $03
.byte $D9, $03
.byte $DA, $03
.byte $DB, $03

;Fighter, facing back, left side extended.
		.byte $D8, $03		  ;($934C)
		.byte $DC, $03		  ;($934E)
.byte $DD, $03
.byte $DE, $03

;Guard, facing back, right side extended.
.byte $58, $02
.byte $59, $02
		.byte $5A, $02		  ;($9358)
		.byte $5B, $02		  ;($935A)

;Guard, facing back, left side extended.
.byte $58, $02
.byte $5D, $02
		.byte $5E, $02		  ;($9360)
.byte $5F, $02

;Shopkeeper, facing back, right side extended.
.byte $22, $01
		.byte $22, $41		  ;($9366)
.byte $2A, $01
.byte $2B, $01

;Shopkeeper, facing back, left side extended.
.byte $22, $01
.byte $22, $41
.byte $2B, $41
.byte $2A, $41

;King Lorik, facing front, right side extended.
.byte $70, $03
.byte $72, $03
.byte $74, $03
.byte $76, $03

;King Lorik, facing front, left side extended.
		.byte $88, $03		  ;($937C)
		.byte $89, $03		  ;($937E)
		.byte $8A, $03		  ;($9380)
.byte $8B, $03

;Wizard, facing back, right side extended.
.byte $F0, $02
		.byte $F1, $02		  ;($9386)
		.byte $F2, $02		  ;($9388)
.byte $F3, $02

;Wizard, facing back, left side extended.
.byte $F0, $02
.byte $F4, $02
		.byte $F5, $02		  ;($9390)
.byte $F6, $02

;Female villager, facing back, right side extended.
.byte $0C, $00
		.byte $0C, $40		  ;($9396)
.byte $0F, $40
.byte $0E, $40

;Female villager, facing back, left side extended.
		.byte $0C, $00		  ;($939C)
		.byte $0C, $40		  ;($939E)
.byte $0E, $00
.byte $0F, $00

;Guard, facing right, front foot up.
		.byte $68, $02		  ;($93A4)
.byte $69, $02
.byte $6A, $02
		.byte $6B, $02		  ;($93AA)

;Guard, facing right, holding trumpet.
		.byte $8D, $42		  ;($93AC)
		.byte $8C, $41		  ;($93AE)
.byte $8F, $42
		.byte $8E, $41		  ;($93B2)

;Player, facing up, right side extended, no shield, no weapon.
		.byte $20, $00		  ;($93B4)
		.byte $21, $00		  ;($93B6)
		.byte $24, $00		  ;($93B8)
		.byte $25, $00		  ;($93BA)

;Player, facing up, left side extended, no shield, no weapon.
		.byte $21, $40		  ;($93BC)
		.byte $20, $40		  ;($93BE)
		.byte $25, $40		  ;($93C0)
		.byte $24, $40		  ;($93C2)

;Player, facing up, right side extended, no shield, weapon.
.byte $40, $00
		.byte $41, $00		  ;($93C6)
		.byte $42, $00		  ;($93C8)
		.byte $43, $00		  ;($93CA)

;Player, facing up, left side extended, no shield, weapon.
		.byte $44, $00		  ;($93CC)
		.byte $45, $00		  ;($93CE)
.byte $46, $00
		.byte $47, $00		  ;($93D2)

;Player, facing up, right side extended, shield, no weapon.
		.byte $60, $00		  ;($93D4)
		.byte $21, $00		  ;($93D6)
.byte $62, $00
		.byte $25, $00		  ;($93DA)

;Player, facing up, left side extended, shield, no weapon.
		.byte $64, $00		  ;($93DC)
		.byte $20, $40		  ;($93DE)
.byte $66, $00
		.byte $24, $40		  ;($93E2)

;Player, facing up, right side extended, shield, weapon.
.byte $80, $00
		.byte $41, $00		  ;($93E6)
		.byte $82, $00		  ;($93E8)
.byte $43, $00

;Player, facing up, left side extended, shield, weapon.
		.byte $84, $00		  ;($93EC)
		.byte $45, $00		  ;($93EE)
.byte $86, $00
.byte $47, $00

;Player, facing up, right side extended, carrying Gwaelin.
.byte $A4, $00
		.byte $A5, $00		  ;($93F6)
		.byte $A2, $00		  ;($93F8)
.byte $A3, $00

;Player, facing up, left side extended, carrying Gwaelin.
.byte $A4, $00
.byte $A5, $00
.byte $A6, $00
		.byte $A7, $00		  ;($9402)

;Gwaelin, facing up, right side extended.
.byte $18, $03
		.byte $18, $43		  ;($9406)
		.byte $1A, $03		  ;($9408)
		.byte $1B, $03		  ;($940A)

;Gwaelin, facing up, left side extended.
		.byte $18, $03		  ;($940C)
		.byte $18, $43		  ;($940E)
.byte $1B, $43
.byte $1A, $43

;Dragonlord, facing up, right side extended.
.byte $C4, $00
		.byte $C5, $00		  ;($9416)
		.byte $C6, $00		  ;($9418)
		.byte $C7, $00		  ;($941A)

;Dragonlord, facing up, left side extended.
.byte $C4, $00
.byte $C8, $00
.byte $C9, $00
		.byte $CA, $00		  ;($9422)

;Guard, facing left, front leg up.
.byte $69, $42
		.byte $68, $42		  ;($9426)
		.byte $6B, $42		  ;($9428)
		.byte $6A, $42		  ;($942A)

;Guard, facing left, holding trumpet.
		.byte $8C, $01		  ;($942C)
.byte $8D, $02
		.byte $8E, $01		  ;($9430)
.byte $8F, $02

;Male villager, facing right, front foot up.
.byte $04, $00
.byte $05, $00
.byte $06, $00
.byte $07, $00

;Male villager, facing right, front foot down.
.byte $04, $00
.byte $05, $00
.byte $08, $00
.byte $09, $00

;Fighter, facing right, front foot up.
		.byte $DF, $03		  ;($9444)
.byte $E0, $03
.byte $E1, $03
.byte $E2, $03

;Fighter, facing right, front foot down.
.byte $DF, $03
.byte $E3, $03
.byte $E4, $03
.byte $E5, $03

;Guard, facing right, front foot up.
.byte $68, $02
.byte $69, $02
.byte $6A, $02
.byte $6B, $02

;Guard, facing right, front foot down.
.byte $68, $02
.byte $5C, $02
.byte $6C, $02
.byte $6D, $02

;Shopkeeper, facing right, front foot up.
.byte $2C, $01
.byte $2D, $01
.byte $2E, $01
.byte $2F, $01

;Shopkeeper, facing right, front foot down.
.byte $2C, $01
.byte $2D, $01
.byte $23, $01
.byte $1C, $01

;King Lorik, facing front, right side extended.
.byte $70, $03
.byte $72, $03
		.byte $74, $03		  ;($9478)
		.byte $76, $03		  ;($947A)

;King Lorik, facing front, left side extended.
		.byte $88, $03		  ;($947C)
.byte $89, $03
.byte $8A, $03
		.byte $8B, $03		  ;($9482)

;Wizard, facing right, front foot up.
		.byte $F7, $02		  ;($9484)
.byte $F8, $02
.byte $F9, $02
		.byte $FA, $02		  ;($948A)

;Wizard, facing right, front foot down.
		.byte $F7, $02		  ;($948C)
		.byte $FB, $02		  ;($948E)
		.byte $FC, $02		  ;($9490)
		.byte $FD, $02		  ;($9492)

;Female villager, facing right, front foot up.
		.byte $10, $00		  ;($9494)
		.byte $11, $00		  ;($9496)
		.byte $14, $00		  ;($9498)
		.byte $15, $00		  ;($949A)

;Female villager, facing right, front foot down.
		.byte $10, $00		  ;($949C)
		.byte $11, $00		  ;($949E)
.byte $12, $00
.byte $13, $00

;Guard, facing right, front foot up.
		.byte $68, $02		  ;($94A4)
		.byte $69, $02		  ;($94A6)
		.byte $6A, $02		  ;($94A8)
		.byte $6B, $02		  ;($94AA)

;Guard, facing right, holding trumpet.
		.byte $8D, $42		  ;($94AC)
		.byte $8C, $41		  ;($94AE)
		.byte $8F, $42		  ;($94B0)
.byte $8E, $41

;Player, facing right, front foot up, no shield, no weapon.
		.byte $26, $00		  ;($94B4)
		.byte $27, $00		  ;($94B6)
		.byte $28, $00		  ;($94B8)
		.byte $29, $00		  ;($94BA)

;Player, facing right, front foot down, no shield, no weapon.
		.byte $30, $00		  ;($94BC)
		.byte $31, $00		  ;($94BE)
		.byte $32, $00		  ;($94C0)
		.byte $33, $00		  ;($94C2)

;Player, facing right, front foot up, no shield, weapon.
		.byte $48, $00		  ;($94C4)
		.byte $49, $00		  ;($94C6)
		.byte $4A, $00		  ;($94C8)
		.byte $4B, $00		  ;($94CA)

;Player, facing right, front foot down, no shield, weapon.
		.byte $4C, $00		  ;($94CC)
		.byte $4D, $00		  ;($94CE)
		.byte $4E, $00		  ;($94D0)
.byte $4F, $00

;Player, facing right, front foot up, shield, no weapon.
		.byte $26, $00		  ;($94D4)
		.byte $27, $00		  ;($94D6)
		.byte $28, $00		  ;($94D8)
		.byte $29, $00		  ;($94DA)

;Player, facing right, front foot down, shield, no weapon.
		.byte $30, $00		  ;($94DC)
		.byte $31, $00		  ;($94DE)
		.byte $32, $00		  ;($94E0)
.byte $33, $00

;Player, facing right, front foot up, shield, weapon.
		.byte $48, $00		  ;($94E4)
		.byte $49, $00		  ;($94E6)
.byte $4A, $00
.byte $4B, $00

;Player, facing right, front foot down, shield, weapon.
		.byte $4C, $00		  ;($94EC)
		.byte $4D, $00		  ;($94EE)
		.byte $4E, $00		  ;($94F0)
.byte $4F, $00

;Player, facing right, front foot up, carrying Gwaelin.
		.byte $A8, $00		  ;($94F4)
		.byte $A9, $03		  ;($94F6)
		.byte $AA, $00		  ;($94F8)
		.byte $AB, $03		  ;($94FA)

;Player, facing right, front foot down, carrying Gwaelin.
		.byte $AC, $00		  ;($94FC)
		.byte $AD, $03		  ;($94FE)
		.byte $AE, $00		  ;($9500)
.byte $AF, $03

;Gwaelin, facing right, front foot up.
		.byte $38, $03		  ;($9504)
		.byte $19, $43		  ;($9506)
.byte $3C, $03
		.byte $3D, $03		  ;($950A)

;Gwaelin, facing right, front foot down.
		.byte $38, $03		  ;($950C)
		.byte $19, $43		  ;($950E)
		.byte $3A, $03		  ;($9510)
		.byte $3B, $03		  ;($9512)

;Dragonlord, facing right, front foot up.
		.byte $CE, $00		  ;($9514)
		.byte $CB, $00		  ;($9516)
.byte $CC, $00
		.byte $CD, $00		  ;($951A)

;Dragonlord, facing right, front foot down.
.byte $CE, $00
.byte $CF, $00
		.byte $D0, $00		  ;($9520)
		.byte $D1, $00		  ;($9522)

;Guard, facing left, front foot up.
		.byte $69, $42		  ;($9524)
		.byte $68, $42		  ;($9526)
.byte $6B, $42
		.byte $6A, $42		  ;($952A)

;Guard, facing left, holding trumpet.
		.byte $8C, $01		  ;($952C)
		.byte $8D, $02		  ;($952E)
		.byte $8E, $01		  ;($9530)
		.byte $8F, $02		  ;($9532)

;Male villager, facing down, right side extended.
		.byte $01, $00		  ;($9534)
		.byte $01, $40		  ;($9536)
.byte $0A, $00
		.byte $0B, $00		  ;($953A)

;Male villager, facing down, left side extended.
		.byte $01, $00		  ;($953C)
		.byte $01, $40		  ;($953E)
		.byte $0B, $40		  ;($9540)
		.byte $0A, $40		  ;($9542)

;Fighter, facing down, right side extended.
		.byte $E6, $03		  ;($9544)
		.byte $B0, $03		  ;($9546)
.byte $B1, $03
		.byte $E7, $03		  ;($954A)

;Fighter, facing down, left side extended.
		.byte $E8, $03		  ;($954C)
		.byte $B0, $03		  ;($954E)
		.byte $E9, $03		  ;($9550)
		.byte $EA, $03		  ;($9552)

;Guard, facing down, right side extended.
		.byte $78, $02		  ;($9554)
		.byte $79, $02		  ;($9556)
.byte $7A, $02
		.byte $7B, $02		  ;($955A)

;Guard, facing down, left side extended.
		.byte $7C, $02		  ;($955C)
.byte $79, $02
.byte $7E, $02
		.byte $7F, $02		  ;($9562)

;Shopkeeper, facing front, right side extended.
.byte $1D, $01
.byte $1D, $41
.byte $1E, $01
		.byte $1F, $01		  ;($956A)

;Shopkeeper, facing front, left side extended.
		.byte $1D, $01		  ;($956C)
		.byte $1D, $41		  ;($956E)
		.byte $1F, $41		  ;($9570)
		.byte $1E, $41		  ;($9572)

;King Lorik, facing front, right side extended.
		.byte $70, $03		  ;($9574)
.byte $72, $03
.byte $74, $03
		.byte $76, $03		  ;($957A)

;King Lorik, facing front, left side extended.
.byte $88, $03
.byte $89, $03
		.byte $8A, $03		  ;($9580)
		.byte $8B, $03		  ;($9582)

;Wizard, facing front, right side extended.
		.byte $FE, $02		  ;($9584)
		.byte $FF, $02		  ;($9586)
.byte $C2, $02
		.byte $C3, $02		  ;($958A)

;Wizard, facing front, left side extended.
		.byte $A0, $02		  ;($958C)
		.byte $FF, $02		  ;($958E)
		.byte $A1, $02		  ;($9590)
.byte $85, $02

;Female villager, facing front, right side extended.
		.byte $0D, $00		  ;($9594)
		.byte $0D, $40		  ;($9596)
		.byte $16, $00		  ;($9598)
		.byte $17, $00		  ;($959A)

;Female villager, facing front, left side extended.
		.byte $0D, $00		  ;($959C)
		.byte $0D, $40		  ;($959E)
		.byte $17, $40		  ;($95A0)
.byte $16, $40

;Guard, facing right, front foot up.
		.byte $68, $02		  ;($95A4)
		.byte $69, $02		  ;($95A6)
		.byte $6A, $02		  ;($95A8)
		.byte $6B, $02		  ;($95AA)

;Guard, facing right, holding trumpet.
		.byte $8D, $42		  ;($95AC)
		.byte $8C, $41		  ;($95AE)
		.byte $8F, $42		  ;($95B0)
.byte $8E, $41

;Player, facing down, right side extended, no shield, no weapon.
		.byte $34, $00		  ;($95B4)
		.byte $35, $00		  ;($95B6)
		.byte $36, $00		  ;($95B8)
		.byte $37, $00		  ;($95BA)

;Player, facing down, left side extended, no shield, no weapon.
		.byte $35, $40		  ;($95BC)
		.byte $34, $40		  ;($95BE)
		.byte $37, $40		  ;($95C0)
.byte $36, $40

;Player, facing down, right side extended, no shield, weapon.
		.byte $50, $00		  ;($95C4)
		.byte $51, $00		  ;($95C6)
		.byte $52, $00		  ;($95C8)
		.byte $53, $00		  ;($95CA)

;Player, facing down, left side extended, no shield, weapon.
		.byte $54, $00		  ;($95CC)
.byte $55, $00
.byte $56, $00
.byte $57, $00

;Player, facing down, right side extended, shield, no weapon.
		.byte $34, $00		  ;($95D4)
		.byte $71, $00		  ;($95D6)
		.byte $36, $00		  ;($95D8)
		.byte $73, $00		  ;($95DA)

;Player, facing down, left side extended, shield, no weapon.
		.byte $35, $40		  ;($95DC)
		.byte $75, $00		  ;($95DE)
.byte $37, $40
.byte $77, $00

;Player, facing down, right side extended, shield, weapon.
		.byte $50, $00		  ;($95E4)
		.byte $91, $00		  ;($95E6)
		.byte $52, $00		  ;($95E8)
		.byte $93, $00		  ;($95EA)

;Player, facing down, left side extended, shield, weapon.
		.byte $54, $00		  ;($95EC)
		.byte $95, $00		  ;($95EE)
		.byte $56, $00		  ;($95F0)
.byte $97, $00

;Player, facing down, right side extended, carrying Gwaelin.
		.byte $B4, $03		  ;($95F4)
		.byte $B5, $00		  ;($95F6)
		.byte $B2, $03		  ;($95F8)
		.byte $B3, $03		  ;($95FA)

;Player, facing down, left side extended, carrying Gwaelin.
.byte $B4, $03
		.byte $B5, $00		  ;($95FE)
		.byte $B6, $03		  ;($9600)
		.byte $B7, $03		  ;($9602)

;Gwaelin, facing down, right side extended.
		.byte $3E, $03		  ;($9604)
		.byte $3F, $03		  ;($9606)
		.byte $C0, $03		  ;($9608)
		.byte $C1, $03		  ;($960A)

;Gwaelin, facing down, left side extended.
.byte $3E, $03
.byte $3F, $03
		.byte $C1, $43		  ;($9610)
		.byte $C0, $43		  ;($9612)

;Dragonlord, facing down, right side extended.
		.byte $D2, $00		  ;($9614)
		.byte $D3, $00		  ;($9616)
		.byte $D4, $00		  ;($9618)
		.byte $D5, $00		  ;($961A)

;Dragonlord, facing down, left side extended.
.byte $D6, $00
		.byte $D3, $00		  ;($961E)
		.byte $D7, $00		  ;($9620)
		.byte $92, $00		  ;($9622)

;Guard, facing left, front foot up.
		.byte $69, $42		  ;($9624)
		.byte $68, $42		  ;($9626)
		.byte $6B, $42		  ;($9628)
		.byte $6A, $42		  ;($962A)

;Guard, facing left, holding trumpet.
.byte $8C, $01
.byte $8D, $02
.byte $8E, $01
		.byte $8F, $02		  ;($9632)

;Male villager, facing left, front foot up.
.byte $05, $40
.byte $04, $40
		.byte $07, $40		  ;($9638)
		.byte $06, $40		  ;($963A)

;Male villager, facing left, front foot down.
		.byte $05, $40		  ;($963C)
.byte $04, $40
.byte $09, $40
		.byte $08, $40		  ;($9642)

;Fighter, facing left, front foot up.
		.byte $EB, $03		  ;($9644)
		.byte $DF, $43		  ;($9646)
		.byte $EC, $03		  ;($9648)
		.byte $ED, $03		  ;($964A)

;Fighter, facing left, front foot down.
		.byte $EB, $03		  ;($964C)
		.byte $DF, $43		  ;($964E)
.byte $EE, $03
		.byte $EF, $03		  ;($9652)

;Guard, facing left, front foot down.
		.byte $7D, $02		  ;($9654)
.byte $68, $42
		.byte $81, $02		  ;($9658)
		.byte $83, $02		  ;($965A)

;Guard, facing left, front foot up.
		.byte $7D, $02		  ;($965C)
		.byte $68, $42		  ;($965E)
		.byte $6E, $02		  ;($9660)
		.byte $6F, $02		  ;($9662)

;Shopkeeper, facing left, front foot down.
		.byte $2D, $41		  ;($9664)
.byte $2C, $41
		.byte $1C, $41		  ;($9668)
		.byte $23, $41		  ;($966A)

;Shopkeeper, facing left, front foot up.
		.byte $2D, $41		  ;($966C)
		.byte $2C, $41		  ;($966E)
		.byte $2F, $41		  ;($9670)
		.byte $2E, $41		  ;($9672)

;King Lorik, facing front, right side extended.
		.byte $70, $03		  ;($9674)
.byte $72, $03
		.byte $74, $03		  ;($9678)
		.byte $76, $03		  ;($967A)

;King Lorik, facing front, left side extended.
		.byte $88, $03		  ;($967C)
		.byte $89, $03		  ;($967E)
		.byte $8A, $03		  ;($9680)
		.byte $8B, $03		  ;($9682)

;Wizard, facing left, front foot up.
		.byte $87, $02		  ;($9684)
		.byte $F7, $42		  ;($9686)
		.byte $65, $02		  ;($9688)
.byte $67, $02

;Wizard, facing left, front foot down.
		.byte $87, $02		  ;($968C)
		.byte $F7, $42		  ;($968E)
		.byte $61, $02		  ;($9690)
.byte $63, $02

;Female villager, facing left, front foot up.
.byte $11, $40
		.byte $10, $40		  ;($9696)
		.byte $15, $40		  ;($9698)
.byte $14, $40

;Female villager, facing left, front foot down.
		.byte $11, $40		  ;($969C)
		.byte $10, $40		  ;($969E)
		.byte $13, $40		  ;($96A0)
		.byte $12, $40		  ;($96A2)

;Guard, facing right, front foot up.
		.byte $68, $02		  ;($96A4)
		.byte $69, $02		  ;($96A6)
		.byte $6A, $02		  ;($96A8)
.byte $6B, $02

;Guard, facing right, holding trumpet.
		.byte $8D, $42		  ;($96AC)
		.byte $8C, $41		  ;($96AE)
		.byte $8F, $42		  ;($96B0)
		.byte $8E, $41		  ;($96B2)

;Player, facing left, front foot up, no shield, no weapon.
		.byte $27, $40		  ;($96B4)
		.byte $26, $40		  ;($96B6)
		.byte $29, $40		  ;($96B8)
.byte $28, $40

;Player, facing left, front foot down, no shield, no weapon.
.byte $31, $40
		.byte $30, $40		  ;($96BE)
		.byte $33, $40		  ;($96C0)
		.byte $32, $40		  ;($96C2)

;Player, facing left, front foot up, no shield, weapon.
.byte $27, $40
.byte $26, $40
		.byte $29, $40		  ;($96C8)
.byte $28, $40

;Player, facing left, front foot down, no shield, weapon.
.byte $31, $40
		.byte $30, $40		  ;($96CE)
		.byte $33, $40		  ;($96D0)
		.byte $32, $40		  ;($96D2)

;Player, facing left, front foot up, shield, no weapon.
		.byte $98, $00		  ;($96D4)
		.byte $99, $00		  ;($96D6)
.byte $9A, $00
.byte $9B, $00

;Player, facing left, front foot down, shield, no weapon.
.byte $9C, $00
		.byte $9D, $00		  ;($96DE)
.byte $9E, $00
.byte $9F, $00

;Player, facing left, front foot up, shield, weapon.
		.byte $98, $00		  ;($96E4)
.byte $99, $00
.byte $9A, $00
		.byte $9B, $00		  ;($96EA)

;Player, facing left, front foot down, shield, weapon.
.byte $9C, $00
		.byte $9D, $00		  ;($96EE)
		.byte $9E, $00		  ;($96F0)
		.byte $9F, $00		  ;($96F2)

;Player, facing left, front foot up, carrying Gwaelin.
		.byte $B8, $03		  ;($96F4)
.byte $B9, $00
.byte $BA, $03
		.byte $BB, $03		  ;($96FA)

;Player, facing left, front foot down, carrying Gwaelin.
.byte $BC, $03
		.byte $BD, $00		  ;($96FE)
		.byte $BE, $03		  ;($9700)
		.byte $BF, $03		  ;($9702)

;Gwaelin, facing left, front foot up.
		.byte $38, $03		  ;($9704)
		.byte $39, $03		  ;($9706)
		.byte $3A, $03		  ;($9708)
		.byte $3B, $03		  ;($970A)

;Gwaelin, facing left, front foot down.
.byte $39, $43
		.byte $38, $43		  ;($970E)
		.byte $3C, $03		  ;($9710)
		.byte $3D, $03		  ;($9712)

;Dragonlord, facing left, front foot up.
		.byte $D0, $00		  ;($9714)
		.byte $D1, $00		  ;($9716)
		.byte $D2, $00		  ;($9718)
		.byte $D3, $00		  ;($971A)

;Dragonlord, facing left, front foot down.
.byte $D4, $00
		.byte $D5, $00		  ;($971E)
		.byte $D6, $00		  ;($9720)
		.byte $D7, $00		  ;($9722)

;Guard, facing left, front foot up.
		.byte $69, $42		  ;($9724)
		.byte $68, $42		  ;($9726)
		.byte $6B, $42		  ;($9728)
		.byte $6A, $42		  ;($972A)

;Guard, facing left, holding trumpet.
.byte $8C, $01
		.byte $8D, $02		  ;($972E)
		.byte $8E, $01		  ;($9730)
		.byte $8F, $02		  ;($9732)

;----------------------------------------------------------------------------------------------------

;The following 2 tables are used to find NPC data for the various maps.  The first table
;points to NPC data for modile NPCs.  The second table points to NPC data for static NPCs.

NPCMobilePointerTable:
		.word TantagelMobileTable;($9734)($9764)Tantagel castle, ground floor mobile NPCs.
		.word ThroneRoomMobileTable;($9736)($97A2)Throne room mobile NPCs.
		.word DrgnLrdBFMobileTable;($9738)($97EA)Dragonlord's castle, bottom floor mobile NPCs. NPCs.
		.word KolMobileTable	;($973A)($98B3)Kol mobile NPCs.
		.word BrecconaryMobileTable;($973C)($9875)Brecconary mobile NPCs.
		.word GarinhamMobileTable;($973E)($98E5)Garinham mobile NPCs. NPCs.
.word CantlinMobileTable	  ;($97F9)Cantlin mobile NPCs.
.word RimuldarMobileTable	 ;($9837)Rimuldar mobile NPCs.
		.word TantSLMobileTable ;($9744)($97B3)Tantagel castle, sublevel mobile NPCs. NPCs.
		.word RainCaveMobileTable;($9746)($97EF)Staff of rain cave mobile NPCs.
		.word RainbowCaveMobileTable;($9748)($97F4)Rainbow drop cave mobile NPCs.
		.word TantDLMobileTable ;($974A)($97B8)Tantagel castle, after dragonlord defeat mobile NPCs.

NPCStaticPointerTable:
		.word TantagelStaticTable;($974C)($9783)Tantagel castle, ground floor static NPCs.
		.word ThroneRoomStaticTable;($974E)($97A6)Throne room, static NPCs.
		.word DrgnLrdBFStaticTable;($9750)($97EB)Dragonlord's castle, bottom floor static NPCs. NPCs.
		.word KolStaticTable	;($9752)($98CF)Kol, static NPCs.
		.word BrecconaryStaticTable;($9754)($9894)Brecconary, static NPCs.
		.word GarinhamStaticTable;($9756)($98FB)Garinham, static NPCs. NPCs.
		.word CantlinStaticTable;($9758)($9818)Cantlin, static NPCs.
		.word RimuldarStaticTable;($975A)($9856)Rimuldar, static NPCs.
.word TantSLStaticTable	   ;($97B4)Tantagel castle, sublevel static NPCs. NPCs.
.word RainCaveStaticTable	 ;($97F0)Staff of rain cave static NPCs.
		.word RainbowCaveStaticTable;($9760)($97F5)Rainbow drop cave static NPCs.
		.word TantDLStaticTable ;($9762)($97CE)Tantagel castle, after dragonlord defeat static NPCs.

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
		.byte $C8, $4D, $62	 ;($9764)Female villager at  8,13.
.byte $53, $42, $17	 ;Guard at		   19, 2.
		.byte $0B, $4B, $1C	 ;($976A)Male villager at   11,11.
.byte $B1, $4B, $1D	 ;Wizard at		  17,11.
		.byte $64, $55, $1F	 ;($9770)Shopkeeper at	   4,21.
		.byte $39, $4B, $16	 ;($9773)Fighter at		 25,11.
		.byte $52, $52, $72	 ;($9776)Guard at		   18,18.
		.byte $42, $4C, $1B	 ;($9779)Guard at			2,12.
.byte $66, $59, $20	 ;Shopkeeper at	   6,25.
		.byte $38, $55, $22	 ;($977F)Fighter at		 24,21.
		.byte $FF			   ;($9782)

TantStatTbl:
		.byte $78, $41, $0E	 ;($9783)Shopkeeper at	  24, 1.
		.byte $DB, $45, $1A	 ;($9786)Female villager at 27, 5.
		.byte $48, $46, $19	 ;($9789)Guard at			8, 6.
.byte $02, $48, $18	 ;Male villager at	2, 8.
		.byte $48, $08, $71	 ;($978F)Guard at			8, 8.
		.byte $5A, $0F, $1E	 ;($9792)Guard at		   26,15.
.byte $4F, $34, $63	 ;Guard at		   15,20.
		.byte $B4, $7A, $6A	 ;($9798)Wizard at		  20,26.
		.byte $49, $3B, $21	 ;($979B)Guard at			9,27.
		.byte $4C, $7B, $21	 ;($979E)Guard at		   12,27.
		.byte $FF			   ;($97A1)

;----------------------------------------------------------------------------------------------------

ThRmMobTbl:
		.byte $47, $45, $65	 ;($97A2)Guard at			7, 5.
		.byte $FF			   ;($97A5)

ThRmStatTbl:
.byte $83, $43, $6E	 ;King Lorik at	   3, 3.
		.byte $43, $26, $23	 ;($97A9)Guard at			3, 6.
		.byte $45, $66, $24	 ;($97AC)Guard at			5, 6.
		.byte $C6, $43, $6F	 ;($97AF)Princess Gwaelin at 6, 3.
		.byte $FF			   ;($97B2)

;----------------------------------------------------------------------------------------------------

TaSLMobTbl:
		.byte $FF			   ;($97B3)No mobile NPCs.

TaSLStatTbl:
		.byte $A4, $46, $66	 ;($97B4)Wizard at		   4, 6.
.byte $FF			   ;

;----------------------------------------------------------------------------------------------------

TaDLMobTbl:
		.byte $53, $42, $17	 ;($97B8)Guard at		   19, 2.
		.byte $0E, $57, $1C	 ;($97BB)Male villager at   14,23.
		.byte $39, $4B, $16	 ;($97BE)Fighter at		 25,11.
		.byte $52, $52, $72	 ;($97C1)Guard at		   18,18.
		.byte $42, $4C, $1B	 ;($97C4)Guard at			2,12.
.byte $66, $59, $20	 ;Shopkeeper at	   6,25.
		.byte $38, $55, $22	 ;($97CA)Fighter at		 24,21.
.byte $FF			   ;

TaDLStatTbl:
		.byte $8B, $47, $FE	 ;($97CE)King Lorik at	  11, 7.
		.byte $E9, $49, $FD	 ;($97D1)Trumpet guard at	9, 9.
		.byte $E9, $4B, $FD	 ;($97D4)Trumpet guard at	9,11.
.byte $E9, $4D, $FD	 ;Trumpet guard at	9,13.
		.byte $AC, $49, $FD	 ;($97DA)Trumpet guard at   12, 9.
.byte $AC, $4B, $FD	 ;Trumpet guard at   12,11.
		.byte $AC, $4D, $FD	 ;($97E0)Trumpet guard at   12,13.
		.byte $49, $3B, $FD	 ;($97E3)Guard at			9,11.
.byte $4C, $7B, $FD	 ;Guard at		   12,11.
.byte $FF			   ;

;----------------------------------------------------------------------------------------------------

DLBFMobTbl:
		.byte $FF			   ;($97EA)No mobile NPCs.

DLBFStatTbl:
.byte $B0, $58, $70	 ;Dragonlord at	  16,24.
		.byte $FF			   ;($97EE)

;----------------------------------------------------------------------------------------------------

RainMobTbl:
		.byte $FF			   ;($97EF)No mobile NPCs.

RainStatTbl:
		.byte $A4, $24, $6C	 ;($97F0)Wizard at		   4, 4.
		.byte $FF			   ;($97F3)

;----------------------------------------------------------------------------------------------------

RnbwMobTbl:
		.byte $FF			   ;($97F4)No mobile NPCs.

RnbwStatTbl:
		.byte $A4, $65, $6D	 ;($97F5)Wizard at		   4, 5.
		.byte $FF			   ;($97F8)

;----------------------------------------------------------------------------------------------------

CantMobTbl:
.byte $14, $4F, $4B	 ;Male villager at   20,15.
		.byte $45, $46, $60	 ;($97FC)Guard at			5, 6.
		.byte $79, $51, $4C	 ;($97FF)Shopkeeper at	  25,17.
		.byte $C4, $4E, $49	 ;($9802)Female villager at  4,14.
		.byte $76, $45, $03	 ;($9805)Shopkeeper at	  22, 5.
		.byte $C9, $50, $4A	 ;($9808)Female villager at  9,16.
.byte $AE, $5C, $6B	 ;Wizard at		  14,28.
		.byte $4F, $46, $48	 ;($980E)Guard at		   15, 6.
.byte $63, $5A, $4E	 ;Shopkeeper at	   3,26.
		.byte $56, $49, $4D	 ;($9814)Guard at		   22, 9.
		.byte $FF			   ;($9817)

CantStatTbl:
		.byte $68, $43, $14	 ;($9818)Shopkeeper at	   8, 3.
		.byte $BB, $46, $0C	 ;($981B)Wizard at		  27, 6.
.byte $02, $27, $0A	 ;Male villager at	2, 7.
		.byte $62, $2C, $45	 ;($9821)Shopkeeper at	   2,12.
		.byte $67, $6C, $0B	 ;($9824)Shopkeeper at	   7,12.
		.byte $58, $2C, $05	 ;($9827)Guard at		   24,12.
		.byte $D6, $6D, $10	 ;($982A)Female villager at 22,13.
		.byte $AF, $50, $46	 ;($982D)Wizard at		  15,16.
.byte $B6, $56, $47	 ;Wizard at		  22,22.
		.byte $7B, $7A, $04	 ;($9833)Shopkeeper at	  27,26.
.byte $FF			   ;

;----------------------------------------------------------------------------------------------------

RimMobTbl:
		.byte $C6, $55, $59	 ;($9837)Female villager at  6,21.
		.byte $0B, $48, $30	 ;($983A)Male villager at   11, 8.
		.byte $06, $57, $5A	 ;($983D)Male villager at	6,23.
		.byte $D6, $4E, $56	 ;($9840)Female villager at 22,14.
		.byte $25, $59, $5B	 ;($9843)Fighter at		  5,25.
.byte $37, $4B, $52	 ;Fighter at		 23,11.
		.byte $0E, $4B, $55	 ;($9849)Male villager at   14,11.
.byte $30, $5A, $69	 ;Fighter at		 16,26.
		.byte $48, $50, $54	 ;($984F)Guard at			8,16.
		.byte $38, $53, $57	 ;($9852)Fighter at		 24,19.
		.byte $FF			   ;($9855)

RimStatTbl:
		.byte $1B, $40, $51	 ;($9856)Male villager at   27, 0.
		.byte $62, $04, $4F	 ;($9859)Shopkeeper at	   2, 4.
		.byte $A4, $07, $0D	 ;($985C)Wizard at		   4, 7.
		.byte $77, $47, $06	 ;($985F)Shopkeeper at	  23, 7.
		.byte $CF, $08, $50	 ;($9862)Female villager at 15, 8.
		.byte $A6, $6D, $53	 ;($9865)Wizard at		   6,13.
.byte $70, $32, $15	 ;Shopkeeper at	  16,18.
		.byte $A3, $37, $61	 ;($986B)Wizard at		   3,23.
		.byte $B4, $57, $58	 ;($986E)Wizard at		  20,23.
.byte $C0, $5A, $5C	 ;Female villager at  0,26
.byte $FF			   ;

;----------------------------------------------------------------------------------------------------

BrecMobTbl:
		.byte $A9, $44, $2B	 ;($9875)Wizard at		   9, 4.
		.byte $2C, $53, $5D	 ;($9878)Fighter at		 12,19.
		.byte $6F, $49, $2E	 ;($987B)Shopkeeper at	  15, 9.
		.byte $19, $56, $31	 ;($987E)Male villager at   25,22.
.byte $0A, $4E, $2C	 ;Male villager at   10,14.
.byte $D8, $44, $0F	 ;Female villager at 24, 4.
		.byte $5A, $4F, $2F	 ;($9887)Guard at		   26,15.
		.byte $CF, $58, $2D	 ;($988A)Female villager at 15,24.
		.byte $33, $52, $30	 ;($988D)Fighter at		 19,18.
.byte $23, $5A, $27	 ;Fighter at		  3,26.
		.byte $FF			   ;($9893)

BrecStatTbl:
		.byte $65, $44, $01	 ;($9894)Shopkeeper at	   5, 4.
		.byte $3C, $41, $25	 ;($9897)Fighter at		 28, 1.
		.byte $C4, $47, $29	 ;($989A)Female villager	 4, 7.
		.byte $14, $4A, $26	 ;($989D)Male villager at   20,10.
.byte $B8, $4A, $67	 ;Wizard at		  24,10.
		.byte $01, $4D, $2A	 ;($98A3)Male villager at	1,13.
		.byte $6A, $75, $12	 ;($98A6)Shopkeeper at	  10,21.
		.byte $14, $17, $28	 ;($98A9)Male villager at   20,23.
.byte $79, $79, $08	 ;Shopkeeper at	  25,25.
		.byte $4A, $1A, $64	 ;($98AF)Guard at		   10,26.
		.byte $FF			   ;($98B2)

;----------------------------------------------------------------------------------------------------

KolMobTbl:
		.byte $0E, $4D, $36	 ;($98B3)Male villager at   14,13.
		.byte $05, $4C, $30	 ;($98B6)Male villager at	5,12.
		.byte $4C, $4A, $37	 ;($98B9)Guard at		   12,10.
		.byte $A2, $4C, $5E	 ;($98BC)Wizard at		   2,12.
		.byte $B4, $53, $38	 ;($98BF)Wizard at		  20,19.
		.byte $26, $47, $35	 ;($98C2)Fighter at		  6, 7.
.byte $CB, $4E, $2E	 ;Female villager	11,14.
		.byte $67, $53, $5F	 ;($98C8)Shopkeeper at	   7,19.
.byte $B4, $48, $39	 ;Wizard at		  20, 8.
		.byte $FF			   ;($98CE)

KolStatTbl:
		.byte $A1, $41, $68	 ;($98CF)Wizard at		   1, 1.
		.byte $CC, $41, $32	 ;($98D2)Female villager	12, 1.
.byte $73, $04, $11	 ;Shopkeeper at	  19, 4.
		.byte $76, $6C, $00	 ;($98D8)Shopkeeper at	  22,12.
		.byte $34, $4D, $33	 ;($98DB)Fighter at		 20,13.
		.byte $6E, $75, $07	 ;($98DE)Shopkeeper at	  14,21.
		.byte $41, $57, $34	 ;($98E1)Guard at			1,23.
		.byte $FF			   ;($98E4)

;----------------------------------------------------------------------------------------------------

GarMobTbl:
.byte $CC, $44, $3E	 ;Female villager at 12, 4.
		.byte $CC, $4C, $43	 ;($98E8)Female villager at 12,12.
		.byte $AC, $48, $3F	 ;($98EB)Wizard at		  12, 8.
		.byte $A2, $4A, $42	 ;($98EE)Wizard at		   2,10.
		.byte $0B, $47, $3D	 ;($98F1)Male villager at   11, 7.
		.byte $12, $4C, $44	 ;($98F4)Male villager at   18,12.
		.byte $27, $51, $41	 ;($98F7)Fighter at		  7,17.
		.byte $FF			   ;($98FA)

GarStatTbl:
		.byte $AE, $41, $3A	 ;($98FB)Wizard at		  14, 1.
		.byte $43, $25, $3B	 ;($98FE)Guard at			3, 5.
		.byte $45, $65, $3B	 ;($9901)Guard at			5, 5.
		.byte $69, $46, $3C	 ;($9904)Shopkeeper at	   9, 6.
		.byte $65, $6B, $09	 ;($9907)Shopkeeper at	   5,11.
		.byte $71, $6F, $13	 ;($990A)Shopkeeper at	  17,15.
		.byte $A2, $31, $40	 ;($990D)Wizard at		   2,17.
.byte $6A, $12, $02	 ;Shopkeeper at	  10,18.
		.byte $FF			   ;($9913)

;----------------------------------------------------------------------------------------------------

;This table indicates which direction player is facing when changing maps.
;Each entry in this table corresponds to an entry in MapTargetTbl.
;Player's facing direction: 0-up, 1-right, 2-down, 3-left.

MapEntryDirectionTable:
		.byte DIR_RIGHT, DIR_DOWN, DIR_UP,	DIR_RIGHT, DIR_UP,   DIR_RIGHT, DIR_UP,   DIR_RIGHT;($9914)
		.byte DIR_RIGHT, DIR_LEFT, DIR_RIGHT, DIR_DOWN,  DIR_DOWN, DIR_RIGHT, DIR_DOWN, DIR_DOWN;($991C)
		.byte DIR_DOWN,  DIR_DOWN, DIR_RIGHT, DIR_DOWN,  DIR_DOWN, DIR_DOWN,  DIR_DOWN, DIR_DOWN;($9924)
		.byte DIR_DOWN,  DIR_DOWN, DIR_DOWN,  DIR_DOWN,  DIR_DOWN, DIR_DOWN,  DIR_DOWN, DIR_DOWN;($992C)
		.byte DIR_DOWN,  DIR_DOWN, DIR_DOWN,  DIR_DOWN,  DIR_DOWN, DIR_DOWN,  DIR_DOWN, DIR_DOWN;($9934)
.byte DIR_DOWN,  DIR_DOWN, DIR_DOWN,  DIR_DOWN,  DIR_DOWN, DIR_DOWN,  DIR_DOWN, DIR_DOWN
		.byte DIR_DOWN,  DIR_DOWN, DIR_DOWN;($9944)

;----------------------------------------------------------------------------------------------------

;There is another cost table in bank 1. It is used for displaying the costs in the shop
;inventory window.  This table is used to calculate the cost when items are bought and
;sold. The order of the items is slightly different between tables.

;----------------------------------------------------------------------------------------------------
; Item Cost Table - Generated from assets/json/items_corrected.json
; To modify item prices, edit the JSON file and rebuild
;----------------------------------------------------------------------------------------------------
.include "generated/item_cost_table.asm"

;----------------------------------------------------------------------------------------------------

KeyCostTbl:
		.byte $62			   ;($9989)Cantlin			- 98	gold.
.byte $35			   ;Rimuldar		   - 53	gold.
		.byte $55			   ;($998B)Tantagel castle	- 85	gold.

;----------------------------------------------------------------------------------------------------

InnCostTbl:
.byte $14			   ;Kol				- 20	gold.
		.byte $06			   ;($998D)Brecconary		 - 6	 gold.
.byte $19			   ;Garinham		   - 25	gold.
		.byte $64			   ;($998F)Cantlin			- 100   gold.
.byte $37			   ;Rimuldar		   - 55	gold.

;----------------------------------------------------------------------------------------------------
; Shop Items Table - Generated from assets/json/shops.json
; To modify shop inventories, edit the JSON file and rebuild
;----------------------------------------------------------------------------------------------------
.include "generated/shop_items_table.asm"

;----------------------------------------------------------------------------------------------------
; Equipment Bonus Tables - Generated from assets/json/equipment_bonuses.json
; To modify equipment stats, edit the JSON file and rebuild
;----------------------------------------------------------------------------------------------------
.include "generated/equipment_bonus_tables.asm"

;----------------------------------------------------------------------------------------------------

;The following table converts the overworld map block types to standard block IDs. The
;index in the table represents the map block type while the value in the table is the
;standard block ID.

WrldBlkConvTbl:
.byte BLK_GRASS		 ;Index $00 - G = Grass.
.byte BLK_SAND		  ;Index $01 - D = Desert.
		.byte BLK_HILL		  ;($99E5)Index $02 - H = Hills.
.byte BLK_MOUNTAIN	  ;Index $03 - M = Mountain.
		.byte BLK_WATER		 ;($99E7)Index $04 - W = Water.
.byte BLK_STONE		 ;Index $05 - R = Rock Wall.
		.byte BLK_TREES		 ;($99E9)Index $06 - F = Forest
.byte BLK_SWAMP		 ;Index $07 - P = Poison.
.byte BLK_TOWN		  ;Index $08 - T = Town.
.byte BLK_CAVE		  ;Index $09 - U = Underground Tunnel.
		.byte BLK_CASTLE		;($99ED)Index $0A - C = Castle.
.byte BLK_BRIDGE		;Index $0B - B = Bridge.
		.byte BLK_STAIR_DN	  ;($99EF)Index $0C - S = Stairs.

;----------------------------------------------------------------------------------------------------

;The following table converts blocks from the various maps into standard block IDs. The table
;has 3 parts.  The first part converts the overworld water blocks into the various blocks with
;a shore pattern. The second part does town block conversions while the third part does dungeon
;block conversions. As in the table above, the index into the table is the map block type while
;the vale in the table is the standard block ID.

GenBlkConvTbl:

;Overworld water block conversions.
.byte BLK_WATER		 ;Water - no shore.
		.byte BLK_WTR_T		 ;($99F1)Water - shore at top.
.byte BLK_WTR_L		 ;Water - shore at left.
		.byte BLK_WTR_TL		;($99F3)Water - shore at top, left.
.byte BLK_WTR_R		 ;Water - shore at right.
		.byte BLK_WTR_TR		;($99F5)Water - shore at top, right.
.byte BLK_WTR_LR		;Water - shore at left, right.
		.byte BLK_WTR_TLR	   ;($99F7)Water - shore at top, left, right.
.byte BLK_WTR_B		 ;Water - shore at bottom.
		.byte BLK_WTR_TB		;($99F9)Water - shore at top, bottom.
.byte BLK_WTR_LB		;Water - shore at left, bottom.
.byte BLK_WTR_TLB	   ;Water - shore at top, left, bottom.
.byte BLK_WTR_RB		;Water - shore at right, bottom.
		.byte BLK_WTR_TRB	   ;($99FD)Water - shore at top, right, bottom.
.byte BLK_WTR_LRB	   ;Water - shore at left, right and bottom.
		.byte BLK_WTR_TLRB	  ;($99FF)Water - shore at all sides.

;Town block conversions.
.byte BLK_GRASS		 ;Index $00 - Grass.
		.byte BLK_SAND		  ;($9A01)Index $01 - Sand.
.byte BLK_WATER		 ;Index $02 - Water.
		.byte BLK_CHEST		 ;($9A03)Index $03 - Treasure chest.
.byte BLK_STONE		 ;Index $04 - Stone.
		.byte BLK_STAIR_UP	  ;($9A05)Index $05 - Stairs up.
.byte BLK_BRICK		 ;Index $06 - Brick.
		.byte BLK_STAIR_DN	  ;($9A07)Index $07 - Stairs down.
.byte BLK_TREES		 ;Index $08 - Trees.
		.byte BLK_SWAMP		 ;($9A09)Index $09 - Poison.
.byte BLK_FFIELD		;Index $0A - Force field.
.byte BLK_DOOR		  ;Index $0B - Door.
.byte BLK_SHOP		  ;Index $0C - Weapon shop sign.
		.byte BLK_INN		   ;($9A0D)Index $0D - Inn sign.
.byte BLK_BRIDGE		;Index $0E - Bridge.
		.byte BLK_LRG_TILE	  ;($9A0F)Index $0F - Large tile.

;Dungeon block conversions.
.byte BLK_STONE		 ;Index $00 - Stone.
		.byte BLK_STAIR_UP	  ;($9A11)Index $01 - Stairs Up.
.byte BLK_BRICK		 ;Index $02 - Brick.
		.byte BLK_STAIR_DN	  ;($9A13)Index $03 - Stairs Down.
.byte BLK_CHEST		 ;Index $04 - Treasure Chest.
		.byte BLK_DOOR		  ;($9A15)Index $05 - Door.
.byte BLK_PRINCESS	  ;Index $0E - Gwaelin.
		.byte BLK_BLANK		 ;($9A17)Index $0F - Blank.

;----------------------------------------------------------------------------------------------------

;Palette data pointers.

BlackPalPtr:
.word BlackPal		  ;($9A3A)Palette where all colors are black.

OverworldPalPtr:
.word OverworldPal	  ;($9A46)Background palette used on the overworld map.

TownPalPtr:
.word TownPal		   ;($9A56)Background palette used in towns.

.word DungeonPal		;($9A66)Background palette used in dungeons.

PreGamePalPtr:
.word PreGamePal		;($9A73)Background palette for pre-game windows.

RedFlashPalPtr:
.word RedFlashPal	   ;(9A7F)Palette used to flash red when damage occurs.

RegSPPalPtr:
.word RegSPPal		  ;(9A8B)Normal sprite palette used while walking on map.

SplFlshBGPalPtr:
.word SplFlshBGPal	  ;(9A7F)Palette used when enemy is casting a spell.

BadEndBGPalPtr:
.word BadEndBGPal	   ;($9AA3)Palette when choosing to join the dragonlord.

EnSPPalsPtr:
.word EnSPPals		  ;($9AAF)Enemy sprite palettes.

FadePalPtr:
.word FadePal		   ;($9A2E)Palette used for fade in/fade out.

;----------------------------------------------------------------------------------------------------

;Palette data.

FadePal:
.byte $0E, $30, $30, $0E, $24, $24, $0E, $27, $27, $0E, $2A, $2A

BlackPal:
		.byte $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E;($9A3A)

OverworldPal:
		.byte $30, $10, $11, $10, $00, $29, $29, $1A, $27, $29, $37, $11;($9A46)

		.byte $0E, $0E, $0E, $0E;($9A52)Unused palette data.

TownPal:
.byte $30, $10, $11, $10, $00, $16, $29, $1A, $27, $29, $37, $11

.byte $0E, $0E, $0E, $0E	;Unused palette data.

DungeonPal:
		.byte $30, $0E, $0E, $10, $00, $16, $0E, $0E, $0E, $0E, $0E, $0E;($9A66)

		.byte $0E			   ;($9A72)Unused palette data.

PreGamePal:
		.byte $30, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E;($9A73)

RedFlashPal:
		.byte $16, $16, $16, $16, $16, $16, $16, $16, $16, $16, $16, $16;($9A7F)

RegSPPal:
		.byte $35, $30, $12, $35, $27, $1A, $35, $30, $00, $35, $30, $07;($9A8B)

SplFlshBGPal:
		.byte $10, $10, $10, $10, $10, $10, $10, $10, $10, $10, $10, $10;($9A97)

BadEndBGPal:
		.byte $16, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E;($9AA3)

;----------------------------------------------------------------------------------------------------

EnSPPals:					   ;Enemy sprite palettes.
		.byte $1C, $15, $30, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E;($9AAF)

		.byte $16, $0D, $30, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E;($9ABB)

.byte $01, $15, $30, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E

.byte $13, $15, $0C, $26, $0C, $0E, $26, $30, $0E, $26, $15, $0E

.byte $00, $36, $0F, $00, $30, $0F, $26, $14, $29, $0E, $0E, $00

		.byte $15, $0E, $30, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E;($9AEB)

		.byte $26, $13, $1E, $0E, $0E, $30, $0E, $0E, $0E, $0E, $0E, $0E;($9AF7)

		.byte $26, $03, $30, $15, $27, $07, $03, $15, $0E, $0E, $0E, $0E;($9B03)

		.byte $2B, $15, $1B, $23, $1B, $0E, $23, $30, $0E, $23, $15, $0E;($9B0F)

		.byte $34, $15, $30, $34, $15, $13, $34, $07, $13, $07, $15, $13;($9B1B)

.byte $36, $0E, $25, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E

.byte $30, $00, $0D, $27, $0C, $07, $30, $1C, $0D, $30, $0C, $1C

.byte $06, $0C, $0F, $06, $30, $0F, $17, $15, $21, $0E, $0E, $06

.byte $10, $15, $1E, $0E, $0E, $30, $0E, $0E, $0E, $0E, $0E, $0E

.byte $2C, $06, $0E, $2C, $30, $0E, $26, $06, $30, $2C, $06, $0C

.byte $30, $00, $0D, $0E, $17, $1B, $30, $18, $0D, $30, $17, $1C

		.byte $00, $0D, $30, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E;($9B6F)

		.byte $27, $15, $07, $1C, $07, $0E, $1C, $30, $0E, $1C, $15, $0E;($9B7B)

		.byte $06, $10, $0E, $06, $30, $0E, $26, $15, $30, $06, $10, $15;($9B87)

		.byte $13, $05, $30, $1A, $2C, $0C, $05, $1A, $0E, $0E, $0E, $0E;($9B93)

		.byte $10, $05, $30, $10, $05, $00, $10, $10, $00, $10, $05, $00;($9B9F)

		.byte $0C, $10, $30, $0C, $15, $26, $10, $26, $0E, $30, $26, $0E;($9BAB)

		.byte $1C, $06, $1E, $0E, $0E, $35, $0E, $0E, $0E, $0E, $0E, $0E;($9BB7)

		.byte $30, $00, $0D, $27, $06, $03, $30, $25, $0D, $30, $06, $1C;($9BC3)

		.byte $26, $16, $0E, $0E, $0E, $30, $0E, $0E, $0E, $0E, $0E, $0E;($9BCF)

.byte $37, $27, $0E, $0E, $0E, $25, $0E, $0E, $0E, $0E, $0E, $0E

.byte $21, $1C, $0E, $15, $1C, $0E, $17, $0C, $21, $21, $15, $0E

.byte $06, $37, $30, $06, $15, $26, $37, $26, $0E, $30, $26, $0E

.byte $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E, $0E

.byte $27, $02, $0E, $27, $30, $0E, $30, $06, $30, $27, $02, $06

		.byte $1A, $27, $0E, $10, $27, $1A, $30, $26, $0C, $1A, $10, $0E;($9C17)

		.byte $15, $34, $31, $15, $30, $27, $34, $27, $0E, $30, $26, $0E;($9C23)

		.byte $37, $10, $0F, $37, $30, $0F, $00, $26, $1C, $0E, $0E, $37;($9C2F)

		.byte $10, $00, $0E, $22, $00, $0E, $15, $0C, $30, $10, $22, $0E;($9C3B)

		.byte $1C, $25, $0E, $17, $25, $1C, $30, $16, $07, $1C, $17, $0E;($9C47)

		.byte $10, $00, $0E, $0E, $0E, $25, $0E, $0E, $0E, $0E, $0E, $0E;($9C53)

		.byte $25, $16, $0E, $27, $16, $0E, $10, $37, $27, $25, $27, $0E;($9C5F)

		.byte $17, $10, $0E, $22, $10, $17, $30, $16, $0C, $17, $22, $0E;($9C6B)

		.byte $03, $21, $0F, $26, $21, $0C, $30, $15, $0C, $30, $15, $26;($9C77)

		.byte $21, $22, $27, $17, $0C, $30, $07, $15, $30, $21, $27, $15;($9C83)

;----------------------------------------------------------------------------------------------------

;The following data block is the nametable pointers for the overworld combat
;background graphics.  The graphical area is 14 rows by 14 columns.  The data
;below starts at the upper left corner of the background and progresses left
;to right, top to bottom.

CombatBckgndGFX:
		.byte $BA, $BC, $BC, $BC, $BC, $BC, $BC, $BC, $BC, $BC, $BC, $BC, $BC, $BD;($9C8F)
.byte $BB, $B2, $AF, $AD, $AE, $B2, $B2, $B2, $B2, $B2, $B2, $AD, $B1, $BE
		.byte $BB, $B2, $EE, $E1, $B2, $B2, $B2, $AF, $B0, $B1, $B2, $B2, $B2, $BE;($9CAB)
		.byte $BB, $B2, $DE, $E2, $B2, $B2, $B2, $B2, $B2, $B2, $B2, $B5, $B2, $BE;($9CB9)
.byte $EB, $EA, $CA, $CE, $E5, $E3, $E3, $E3, $DF, $E4, $B3, $B6, $B8, $BE
		.byte $EC, $ED, $CC, $D0, $E6, $E9, $E9, $E7, $E0, $E8, $B4, $B7, $B9, $BF;($9CD5)
.byte $DC, $D1, $D2, $D7, $DB, $CD, $CD, $CD, $CD, $D3, $CB, $CF, $CF, $D4
		.byte $DD, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $D3, $D4;($9CF1)
		.byte $C9, $C2, $C4, $C6, $CD, $CD, $CD, $CD, $CD, $CD, $C6, $C6, $CD, $D5;($9CFF)
		.byte $C1, $C3, $C5, $C6, $CD, $CD, $CD, $CD, $CD, $CD, $C6, $C8, $CD, $D5;($9D0D)
		.byte $D9, $CD, $C7, $C6, $CD, $CD, $CD, $CD, $C6, $C6, $CD, $CD, $CD, $D5;($9D1B)
.byte $D9, $CD, $C6, $C8, $CD, $CD, $CD, $CD, $C6, $C6, $CD, $CD, $CD, $D5
		.byte $D9, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $CD, $D5;($9D37)
		.byte $D8, $DA, $DA, $DA, $DA, $DA, $DA, $DA, $DA, $DA, $DA, $DA, $DA, $D6;($9D45)

;----------------------------------------------------------------------------------------------------

; Spell Cost Table - Generated from assets/json/spells.json
; To modify spell MP costs, edit the JSON file and rebuild
;----------------------------------------------------------------------------------------------------
.include "generated/spell_cost_table.asm"

;----------------------------------------------------------------------------------------------------

;Start of world map data.

;The world map uses run length encoding because it would be too big for the memory otherwise.
;Each byte is broken down into the upper and lower nibble.  The upper nibble is the type of tile
;and can be decided from the table below.  The second nibble+1 is the number of times the tile is
;repeated.  Some rows have less than 120 tiles in them and use data from the next row until 120
;tiles have been calculated for the row.

;0 - G = Grass.
;1 - D = Desert.
;2 - H = Hills.
;3 - M = Mountain.
;4 - W = Water.
;5 - R = Rock Wall.
;6 - F = Forest
;7 - P = Poison.
;8 - T = Town.
;9 - U = Underground Tunnel.
;A - C = Castle.
;B - B = Bridge.
;C - S = Stairs.
;D - N/A.
;E - N/A.
;F - N/A.

Row000:	  ;W02  G06  W12  G07  W15  G08  W16  W09  F05  G03  W14  G10  W13
		.byte $41, $05, $4B, $06, $4E, $07, $4F, $48, $64, $02, $4D, $09, $4C;($9D5D)

Row001:	  ;W01  G03  F04  G02  W08  G11  W11  G06  H08  W16  W02  F08  G01  S01  G01  W09
		.byte $40, $02, $63, $01, $47, $0A, $4A, $05, $27, $4F, $41, $67, $00, $C0, $00, $48;($9D6A)
;			 M07  H05  G07  W09
.byte $36, $24, $06, $48

Row002:	  ;G02  T01  F06  G02  W05  G06  F05  G03  W09  G06  F05  H06  W14  F09  G03  W09
.byte $01, $80, $65, $01, $44, $05, $64, $02, $48, $05, $64, $25, $4D, $68, $02, $48
;			 M04  H10  G07  W08
		.byte $33, $29, $06, $47;($9D8E)

Row003:	  ;G01  F09  G11  F08  G02  W08  G05  F09  H04  W12  F10  M02  W09  M03  H13  G09
		.byte $00, $68, $0A, $67, $01, $47, $04, $68, $23, $4B, $69, $31, $48, $32, $2C, $08;($9D92)
;			 W05
.byte $44

Row004:	  ;F06  H05  M03  G06  F10  G02  W06  G05  F10  H05  W11  F09  M03  W07  M03  H09
		.byte $65, $24, $32, $05, $69, $01, $45, $04, $69, $24, $4A, $68, $32, $46, $32, $28;($9DA3)
;			 F08  G08  W04
		.byte $67, $07, $43	 ;($9DB3)

Row005:	  ;F05  H05  M05  G05  F10  G04  W02  G05  F05  W03  F05  H04  W10  F09  M03  W07
		.byte $64, $24, $34, $04, $69, $03, $41, $04, $64, $42, $64, $23, $49, $68, $32, $46;($9DB6)
;			 M03  H08  F12  G07  W03
.byte $32, $27, $6B, $06, $42

Row006:	  ;F03  H05  M08  G03  F13  G09  F04  W05  F03  H04  W09  M03  F07  M03  W07  H11
		.byte $62, $24, $37, $02, $6C, $08, $63, $44, $62, $23, $48, $32, $66, $32, $46, $2A;($9DCB)
;			 F14  G06  W03
		.byte $6D, $05, $42	 ;($9DDB)

Row007:	  ;H06  M05  F04  M04  F12  G09  F06  W03  H07  W09  M03  F09  M03  W07  H09  F06
		.byte $25, $34, $63, $33, $6B, $08, $65, $42, $26, $48, $32, $68, $32, $46, $28, $65;($9DDE)
;			 M05  F06  G05  W02
		.byte $34, $65, $04, $41;($9DEE)

Row008:	  ;H04  M04  F09  M03  F13  G06  F06  W03  H08  W10  M03  F09  M03  W05  H08  F06
		.byte $23, $33, $68, $32, $6C, $05, $65, $42, $27, $49, $32, $68, $32, $44, $27, $65;($9DF2)
;			 M03  F03  M03  F06  G03  W02
		.byte $32, $62, $32, $65, $02, $41;($9E02)

Row009:	  ;H04  M02  F12  M02  F06  D04  F05  G05  F07  H08  W09  F03  M03  F10  M02  W04
.byte $23, $31, $6B, $31, $65, $13, $64, $04, $66, $27, $48, $62, $32, $69, $31, $43
;			 H08  F05  M02  F06  M02  F07  G03  W01
.byte $27, $64, $31, $65, $31, $66, $02, $40

Row010:	  ;H02  G03  F12  M03  F05  D06  F06  G05  F06  H06  W09  F03  M04  F11  M02  W04
		.byte $21, $02, $6B, $32, $64, $15, $65, $04, $65, $25, $48, $62, $33, $6A, $31, $43;($9E20)
;			 H07  F10  T01  F03  M02  F08
		.byte $26, $69, $80, $62, $31, $67;($9E30)

Row011:	  ;W02  G04  F12  M03  F03  D08  F06  G05  F07  H03  W10  F04  M04  F10  M02  W05
		.byte $41, $03, $6B, $32, $62, $17, $65, $04, $66, $22, $49, $63, $33, $69, $31, $44;($9E36)
;			 H07  F16  F08
		.byte $26, $6F, $67	 ;($9E46)

Row012:	  ;W03  G05  F10  M04  F02  D04  U01  D03  F05  G06  F07  H05  W07  F05  M04  F11
.byte $42, $04, $69, $33, $61, $13, $90, $12, $64, $05, $66, $24, $46, $64, $33, $6A
;			 M01  W05  H08  F16  F08
		.byte $30, $44, $27, $6F, $67;($9E59)

Row013:	  ;W04  G08  F07  M04  F02  D07  F06  G06  F07  H05  W05  F07  M06  F08  M02  W04
		.byte $43, $07, $66, $33, $61, $16, $65, $05, $66, $24, $44, $66, $35, $67, $31, $43;($9E5E)
;			 H10  F16  F06
		.byte $29, $6F, $65	 ;($9E6E)

Row014:	  ;W05  F04  G05  F06  M04  F03  D04  F08  G04  F08  H04  G02  W03  F09  M06  F07
		.byte $44, $63, $04, $65, $33, $62, $13, $67, $03, $67, $23, $01, $42, $68, $35, $66;($9E71)
;			 M03  W04  H07  G04  F16  F04
		.byte $32, $43, $26, $03, $6F, $63;($9E81)

Row015:	  ;W04  F05  G06  F07  M03  F13  G06  F08  H02  G03  W02  F07  G07  M03  F07  M03
		.byte $43, $64, $05, $66, $32, $6C, $05, $67, $21, $02, $41, $66, $06, $32, $66, $32;($9E87)
;			 W04  H05  G06  F16
		.byte $43, $24, $05, $6F;($9E97)

Row016:	  ;W06  F02  G07  F06  G04  F13  G05  F10  G04  W02  F04  G12  M04  F05  M03  W05
		.byte $45, $61, $06, $65, $03, $6C, $04, $69, $03, $41, $63, $0B, $33, $64, $32, $44;($9E9B)
;			 F02  G07  F12  W07
		.byte $61, $06, $6B, $46;($9EAB)

Row017:	  ;W03  F06  G07  F04  G05  F12  G05  F10  G06  W02  G16  G01  M03  F05  M03  W02
		.byte $42, $65, $06, $63, $04, $6B, $04, $69, $05, $41, $0F, $00, $32, $64, $32, $41;($9EAF)
;			 F03  G07  F08  M04  W08
		.byte $62, $06, $67, $33, $47;($9EBF)

Row018:	  ;W02  F09  G13  F13  G06  F08  G08  W02  G16  G01  M04  F04  W03  F04  G07  F04
		.byte $41, $68, $0C, $6C, $05, $67, $07, $41, $0F, $00, $33, $63, $42, $63, $06, $63;($9EC4)
;			 M06  F04  W06
		.byte $35, $63, $45	 ;($9ED4)

Row019:	  ;W02  F09  G13  F14  G06  F06  G10  B01  G06  F06  G06  M04  F09  G07  F02  M07
		.byte $41, $68, $0C, $6D, $05, $65, $09, $B0, $05, $65, $05, $33, $68, $06, $61, $36;($9ED7)
;			 F03  D04  W05
		.byte $62, $13, $44	 ;($9EE7)

Row020:	  ;W01  F11  G14  F12  G07  F03  G12  W02  G04  F08  G06  M10  F02  W01  G05  F02
		.byte $40, $6A, $0D, $6B, $06, $62, $0B, $41, $03, $67, $05, $39, $61, $40, $04, $61;($9EEA)
;			 M05  F05  D07  W03
		.byte $34, $64, $16, $42;($9EFA)

Row021:	  ;F12  G15  F10  G16  G08  W01  G03  F10  G05  F02  M09  W02  G05  F01  M06  D13
		.byte $6B, $0E, $69, $0F, $07, $40, $02, $69, $04, $61, $38, $41, $04, $60, $35, $1C;($9EFE)
;			 W02
		.byte $41			   ;($9F0E)

Row022:	  ;F13  G12  H04  F07  G16  G09  W01  G02  F05  H04  F03  G03  F07  H03  W05  G05
		.byte $6C, $0B, $23, $66, $0F, $08, $40, $01, $64, $23, $62, $02, $66, $22, $44, $04;($9F0F)
;			 M05  D16
		.byte $34, $1F		  ;($9F1F)

Row023:	  ;F14  G07  W03  H07  F04  G15  F04  G07  W02  F04  H06  F04  G03  F05  H05  W04
		.byte $6D, $06, $42, $26, $63, $0E, $63, $06, $41, $63, $25, $63, $02, $64, $24, $43;($9F21)
;			 G06  M03  D10  F02  D05
		.byte $05, $32, $19, $61, $14;($9F31)

Row024:	  ;F15  G04  W07  H06  F04  G10  F09  G07  W02  F03  H07  F04  G04  F02  H07  W04
		.byte $6E, $03, $46, $25, $63, $09, $68, $06, $41, $62, $26, $63, $03, $61, $26, $43;($9F36)
;			 G08  D09  F04  D04
		.byte $07, $18, $63, $13;($9F46)

Row025:	  ;F16  G02  W09  H05  F04  G08  F10  H03  G06  W02  F03  H07  F04  G06  H07  W04
		.byte $6F, $01, $48, $24, $63, $07, $69, $22, $05, $41, $62, $26, $63, $05, $26, $43;($9F4A)
;			 G07  D09  F04  D04
		.byte $06, $18, $63, $13;($9F5A)

Row026:	  ;F16  F01  W10  H04  F04  G08  F10  H06  G05  W02  F03  H05  F05  G07  F07  W03
		.byte $6F, $60, $49, $23, $63, $07, $69, $25, $04, $41, $62, $24, $64, $06, $66, $42;($9F5E)
;			 G07  D10  F02  D05
		.byte $06, $19, $61, $14;($9F6E)

Row027:	  ;W02  F15  W09  M03  F06  G07  F10  H08  G05  W05  F10  G05  F07  W05  G07  D15
		.byte $41, $6E, $48, $32, $65, $06, $69, $27, $04, $44, $69, $04, $66, $44, $06, $1E;($9F72)

Row028:	  ;W03  F13  W09  M07  F02  G06  F12  H09  G07  W05  F08  G05  F05  W05  G09  D13
		.byte $42, $6C, $48, $36, $61, $05, $6B, $28, $06, $44, $67, $04, $64, $44, $08, $1C;($9F82)

Row029:	  ;W08  F07  W06  M12  G07  F13  H08  G04  M04  W05  F07  G06  F03  W05  G11  D11
		.byte $47, $66, $45, $3B, $06, $6C, $27, $03, $33, $44, $66, $05, $62, $44, $0A, $1A;($9F92)

Row030:	  ;W04  H03  W03  F04  W05  M15  G05  F09  M06  H06  G03  M05  W07  F07  G06  W06
		.byte $43, $22, $42, $63, $44, $3E, $04, $68, $35, $25, $02, $34, $46, $66, $05, $45;($9FA2)
;			 G14  D07  W05
		.byte $0D, $16, $44	 ;($9FB2)

Row031:	  ;W03  H06  B01  F02  W03  M16  M01  G06  F07  M10  H06  M06  W09  F06  G07  W06
		.byte $42, $25, $B0, $61, $42, $3F, $30, $05, $66, $39, $25, $35, $48, $65, $06, $45;($9FB5)
;			 G13  H06  W06
		.byte $0C, $25, $45	 ;($9FC5)

Row032:	  ;W02  H07  W05  H04  M12  G09  F03  M14  H05  M07  W07  F06  G08  W07  G10  H10
		.byte $41, $26, $44, $23, $3B, $08, $62, $3D, $24, $36, $46, $65, $07, $46, $09, $29;($9FC8)
;			 W04
		.byte $43			   ;($9FD8)

Row033:	  ;W02  H16  H03  M07  G12  M07  H04  M06  F03  M09  W05  F08  G08  W05  G10  H08
.byte $41, $2F, $22, $36, $0B, $36, $23, $35, $62, $38, $44, $67, $07, $44, $09, $27
;			 F04  W03
.byte $63, $42

Row034:	  ;W02  H16  H05  M04  G12  M04  H11  M02  F10  M04  W03  F10  G08  W03  G10  H07
		.byte $41, $2F, $24, $33, $0B, $33, $2A, $31, $69, $33, $42, $69, $07, $42, $09, $26;($9FEB)
;			 F07
		.byte $66			   ;($9FFB)

Row035:	  ;W03  H10  G04  H07  M02  G14  H15  M02  F05  D05  M07  F08  G09  W02  G10  H07
		.byte $42, $29, $03, $26, $31, $0D, $2E, $31, $64, $14, $36, $67, $08, $41, $09, $26;($9FFC)
;			 F09
		.byte $68			   ;($A00C)

Row036:	  ;W04  H03  F04  G08  H05  W02  G13  F07  H08  M04  F02  D09  M06  F06  G09  W02
		.byte $43, $22, $63, $07, $24, $41, $0C, $66, $27, $33, $61, $18, $35, $65, $08, $41;($A00D)
;			 G05  M04  H08  F11
		.byte $04, $33, $27, $6A;($A01D)

Row037:	  ;W02  F08  G10  H03  W04  G11  F11  H06  M04  D09  P03  F09  G10  B01  G03  F02
		.byte $41, $67, $09, $22, $43, $0A, $6A, $25, $33, $18, $72, $68, $09, $B0, $02, $61;($A021)
;			 M06  H06  F11
		.byte $35, $25, $6A	 ;($A031)

Row038:	  ;W01  F07  G11  H04  W05  G08  F14  H08  W04  D05  P05  F09  G06  W04  F05  M07
.byte $40, $66, $0A, $23, $44, $07, $6D, $27, $43, $14, $74, $68, $05, $43, $64, $36
;			 H04  F12  W01
.byte $23, $6B, $40

Row039:	  ;F07  G10  F05  W05  G08  F14  G04  H04  W08  P08  F07  G04  W07  F08  M05  H02
		.byte $66, $09, $64, $44, $07, $6D, $03, $23, $47, $77, $66, $03, $46, $67, $34, $21;($A047)
;			 F12  W02
		.byte $6B, $41		  ;($A057)

Row040:	  ;F05  G09  F07  W06  G07  F11  G10  W09  P08  F07  W13  F04  P04  M04  F13  W03
		.byte $64, $08, $66, $45, $06, $6A, $09, $48, $77, $66, $4C, $63, $73, $33, $6C, $42;($A059)

Row041:	  ;F04  G07  F08  W09  G07  F07  G06  T01  G05  W12  P05  F06  W16  W01  P08  M05
		.byte $63, $06, $67, $48, $06, $66, $05, $80, $04, $4B, $74, $65, $4F, $40, $77, $34;($A069)
;			 F06  W07
		.byte $65, $46		  ;($A079)

Row042:	  ;F05  G05  F05  W10  G11  F04  G09  W16  W04  F05  W16  W07  P06  M07  W10
.byte $64, $04, $64, $49, $0A, $63, $08, $4F, $43, $64, $4F, $46, $75, $36, $49

Row043:	  ;W01  F05  G03  F04  W11  G16  G03  C01  G03  W16  W16  W16  W04  P07  M03  W11
		.byte $40, $64, $02, $63, $4A, $0F, $02, $A0, $02, $4F, $4F, $4F, $43, $76, $32, $4A;($A08A)

Row044:	  ;W02  F10  W09  G16  G08  W16  W16  W16  W10  P01  U01  P01  M02  W12
		.byte $41, $69, $48, $0F, $07, $4F, $4F, $4F, $49, $70, $90, $70, $31, $4B;($A09A)

Row045:	  ;W02  F09  W09  F06  G16  G01  W08  M03  W16  W15  F06  W16  W13
		.byte $41, $68, $48, $65, $0F, $00, $47, $32, $4F, $4E, $65, $4F, $4C;($A0A8)

Row046:	  ;W04  F09  W06  F08  G14  W08  M06  W16  W08  F11  G05  W16  W04  H04
		.byte $43, $68, $45, $67, $0D, $47, $35, $4F, $47, $6A, $04, $4F, $43, $23;($A0B5)

Row047:	  ;W03  F11  W08  F07  G11  W07  P03  M07  W16  W01  F15  G09  W16  H06
		.byte $42, $6A, $47, $66, $0A, $46, $72, $36, $4F, $40, $6E, $08, $4F, $25;($A0C3)

Row048:	  ;W02  F13  W08  F08  G08  W07  M01  P01  C01  P01  M08  W13  D04  F14  G12  W12
		.byte $41, $6C, $47, $67, $07, $46, $30, $70, $A0, $70, $37, $4C, $13, $6D, $0B, $4B;($A0D1)
;			 H07
		.byte $26			   ;($A0E1)

Row049:	  ;W03  F11  W10  F08  G08  W05  M02  P03  D02  M07  W02  D03  W01  D03  W02  D07
		.byte $42, $6A, $49, $67, $07, $44, $31, $72, $11, $36, $41, $12, $40, $12, $41, $16;($A0E2)
;			 F13  G13  P01  U01  P01  W06  H08
		.byte $6C, $0C, $70, $90, $70, $45, $27;($A0F2)

Row050:	  ;W03  F10  M04  W05  F11  G07  W04  M07  D02  M04  D06  W04  D11  F14  G11  P03
.byte $42, $69, $33, $44, $6A, $06, $43, $36, $11, $33, $15, $43, $1A, $6D, $0A, $72
;			 W05  F04  H05
.byte $44, $63, $24

Row051:	  ;W05  F06  M13  F08  G08  W05  M04  D04  M03  D05  M02  W04  M02  D10  F16  F01
		.byte $44, $65, $3C, $67, $07, $44, $33, $13, $32, $14, $31, $43, $31, $19, $6F, $60;($A10C)
;			 G06  H06  W02  F10
		.byte $05, $25, $41, $69;($A11C)

Row052:	  ;W04  G02  F02  M16  M01  F08  G06  W05  M04  D04  M05  D03  M02  W06  M03  D10
		.byte $43, $01, $61, $3F, $30, $67, $05, $44, $33, $13, $34, $12, $31, $45, $32, $19;($A120)
;			 F15  M03  H10  F11
		.byte $6E, $32, $29, $6A;($A130)

Row053:	  ;W02  G04  M16  M04  F08  G04  W07  M02  D06  M05  D01  M02  W08  M04  D09  F07
		.byte $41, $03, $3F, $33, $67, $03, $46, $31, $15, $34, $10, $31, $47, $33, $18, $66;($A134)
;			 W04  M06  H09  F12
		.byte $43, $35, $28, $6B;($A144)

Row054:	  ;W01  G04  M04  F07  M13  F05  H03  W08  M03  D06  M04  H02  M02  W09  M03  D08
		.byte $40, $03, $33, $66, $3C, $64, $22, $47, $32, $15, $33, $21, $31, $48, $32, $17;($A148)
;			 F05  W07  M07  H08  F11
		.byte $64, $46, $36, $27, $6A;($A158)

Row055:	  ;G04  M03  F10  M14  F04  H03  W08  M02  D06  M03  H02  M03  W10  M04  D05  F04
.byte $03, $32, $69, $3D, $63, $22, $47, $31, $15, $32, $21, $32, $49, $33, $14, $63
;			 W08  M13  H03  F11
		.byte $47, $3C, $22, $6A;($A16D)

Row056:	  ;G04  F07  P04  F04  M13  F04  H03  W07  M02  D05  M03  H03  M02  W13  M03  H05
		.byte $03, $66, $73, $63, $3C, $63, $22, $46, $31, $14, $32, $22, $31, $4C, $32, $24;($A171)
;			 F04  W04  M04  F05  M08  F12  W01
.byte $63, $43, $33, $64, $37, $6B, $40

Row057:	  ;G03  F06  P07  F05  M04  G04  U01  M02  F03  H04  W07  M03  D03  M03  H04  M02
.byte $02, $65, $76, $64, $33, $03, $90, $31, $62, $23, $46, $32, $12, $32, $23, $31
;			 W13  M02  H08  F16  M10  F07  W03
		.byte $4C, $31, $27, $6F, $39, $66, $42;($A198)

Row058:	  ;G04  F04  P08  F06  G06  M03  H08  W08  M02  D02  M03  H06  M02  W11  M03  H08
		.byte $03, $63, $77, $65, $05, $32, $27, $47, $31, $11, $32, $25, $31, $4A, $32, $27;($A19F)
;			 F16  M09  D03  F04  W04
		.byte $6F, $38, $12, $63, $43;($A1AF)

Row059:	  ;G03  F06  P06  F07  G05  M03  H08  W09  M02  P01  M06  H01  M05  W12  M02  H06
.byte $02, $65, $75, $66, $04, $32, $27, $48, $31, $70, $35, $20, $34, $4B, $31, $25
;			 G09  F08  M08  D06  F02  W05
.byte $08, $67, $37, $15, $61, $44

Row060:	  ;G03  F07  P04  F07  G06  M04  H06  W09  M02  P02  M05  G03  M03  W14  M02  H04
.byte $02, $66, $73, $66, $05, $33, $25, $48, $31, $71, $34, $02, $32, $4D, $31, $23
;			 G14  F11  D08  F02  W04
.byte $0D, $6A, $17, $61, $43

Row061:	  ;G03  F16  F01  M15  W12  M02  P02  M03  G03  M03  W14  M03  H03  G16  F09  D08
.byte $02, $6F, $60, $3E, $4B, $31, $71, $32, $02, $32, $4D, $32, $22, $0F, $68, $17
;			 F04  W03
		.byte $63, $42		  ;($A1EF)

Row062:	  ;G04  F14  M11  F04  W15  M02  P02  M03  G03  M03  W14  M03  H03  G15  F10  D06
.byte $03, $6D, $3A, $63, $4E, $31, $71, $32, $02, $32, $4D, $32, $22, $0E, $69, $15
;			 F05  W03
.byte $64, $42

Row063:	  ;W01  G04  F09  H03  M06  F09  G02  W14  M02  P04  M02  G03  M02  W15  M03  H08
		.byte $40, $03, $68, $22, $35, $68, $01, $4D, $31, $73, $31, $02, $31, $4E, $32, $27;($A203)
;			 F03  G05  F12  D04  F07
.byte $62, $04, $6B, $13, $66

Row064:	  ;W02  G04  F07  H06  M03  F09  G05  W13  M02  P06  M03  W16  W01  M02  H07  F05
		.byte $41, $03, $66, $25, $32, $68, $04, $4C, $31, $75, $32, $4F, $40, $31, $26, $64;($A218)
;			 G03  F04  M08  F13
.byte $02, $63, $37, $6C

Row065:	  ;W04  G04  F08  H05  F09  G07  W13  M03  P02  M03  W16  W06  H05  F11  M03  G05
.byte $43, $03, $67, $24, $68, $06, $4C, $32, $71, $32, $4F, $45, $24, $6A, $32, $04
;			 M06  F10
.byte $35, $69

Row066:	  ;W06  G04  F07  H06  F05  G08  W16  M04  W16  W10  F13  M03  G09  M04  F09
		.byte $45, $03, $66, $25, $64, $07, $4F, $33, $4F, $49, $6C, $32, $08, $33, $68;($A23E)

Row067:	  ;W07  G05  F06  H03  F06  G08  W16  W16  W16  W01  F11  M02  G03  F05  G03  M05
.byte $46, $04, $65, $22, $65, $07, $4F, $4F, $4F, $40, $6A, $31, $02, $64, $02, $34
;			 F07
		.byte $66			   ;($A25D)

Row068:	  ;W08  G06  F12  G07  W05  F07  W16  W16  W09  F08  G05  F07  G04  M03  F07
.byte $47, $05, $6B, $06, $44, $66, $4F, $4F, $48, $67, $04, $66, $03, $32, $66

Row069:	  ;W09  G06  F10  G05  W06  F07  W16  W16  W09  F09  G05  F02  W05  F02  G04  M03
		.byte $48, $05, $69, $04, $45, $66, $4F, $4F, $48, $68, $04, $61, $44, $61, $03, $32;($A26D)
;			 F06
.byte $65

Row070:	  ;W11  G06  F08  G06  W04  G02  F05  W16  W16  W08  F10  G05  F02  W07  F02  G03
		.byte $4A, $05, $67, $05, $43, $01, $64, $4F, $4F, $47, $69, $04, $61, $46, $61, $02;($A27E)
;			 M02  F07
		.byte $31, $66		  ;($A28E)

Row071:	  ;W12  G07  F08  G11  F03  W16  W16  W10  F10  G03  F02  W03  G03  W03  F02  G02
		.byte $4B, $06, $67, $0A, $62, $4F, $4F, $49, $69, $02, $61, $42, $02, $42, $61, $01;($A290)
;			 M03  F06
.byte $32, $65

Row072:	  ;W14  G06  F09  G10  W16  W16  W15  F08  G02  F02  W03  G01  T01  G01  D03  F02
.byte $4D, $05, $68, $09, $4F, $4F, $4E, $67, $01, $61, $42, $00, $80, $00, $12, $61
;			 G02  M02  F07
		.byte $01, $31, $66	 ;($A2B2)

Row073:	  ;W06  M06  W09  F12  G04  W16  W16  W16  F13  W03  G03  W03  F02  G02  M02  F07
		.byte $45, $35, $48, $6B, $03, $4F, $4F, $4F, $6C, $42, $02, $42, $61, $01, $31, $66;($A2B5)

Row074:	  ;W05  M03  F06  W09  F11  G04  W16  W16  W16  F13  W07  F02  G02  M02  F07
.byte $44, $32, $65, $48, $6A, $03, $4F, $4F, $4F, $6C, $46, $61, $01, $31, $66

Row075:	  ;W04  M03  F10  W05  F11  G06  W16  W15  M08  W09  F13  W05  F03  M04  F06
.byte $43, $32, $69, $44, $6A, $05, $4F, $4E, $37, $48, $6C, $44, $62, $33, $65

Row076:	  ;W03  M03  F08  G04  W06  F08  G10  W16  W10  M05  D07  W09  F09  M05  F15
.byte $42, $32, $67, $03, $45, $67, $09, $4F, $49, $34, $16, $48, $68, $34, $6E

Row077:	  ;W02  M03  F06  G10  W04  F07  G11  W16  W08  D08  M04  D02  W07  F11  M05  F13
		.byte $41, $32, $65, $09, $43, $66, $0A, $4F, $47, $17, $33, $11, $46, $6A, $34, $6C;($A2F2)
;			 W03
		.byte $42			   ;($A302)

Row078:	  ;W01  M03  F06  G13  W01  F07  G06  F02  G05  W16  W06  M14  D02  W07  F12  M04
		.byte $40, $32, $65, $0C, $40, $66, $05, $61, $04, $4F, $45, $3D, $11, $46, $6B, $33;($A303)
;			 H03  F08  G02  W02
		.byte $22, $67, $01, $41;($A313)

Row079:	  ;M03  F04  G09  F04  G03  B01  F07  G05  F04  G05  W14  M10  D06  M06  D01  W09
.byte $32, $63, $08, $63, $02, $B0, $66, $04, $63, $04, $4D, $39, $15, $35, $10, $48
;			 F11  M03  H04  F06  G05
.byte $6A, $32, $23, $65, $04

Row080:	  ;M03  F03  G08  F09  W02  F05  G05  F06  G04  W11  M08  D14  M03  D01  M02  W06
.byte $32, $62, $07, $68, $41, $64, $04, $65, $03, $4A, $37, $1D, $32, $10, $31, $45
;			 F14  M02  H03  F05  G06
		.byte $6D, $31, $22, $64, $05;($A33C)

Row081:	  ;M02  F05  G05  F12  W02  F04  G04  F08  G04  W08  M09  D02  M12  D02  M02  D01
		.byte $31, $64, $04, $6B, $41, $63, $03, $67, $03, $47, $38, $11, $3B, $11, $31, $10;($A341)
;			 M02  W07  F14  M02  H03  F05  G05
		.byte $31, $46, $6D, $31, $22, $64, $04;($A351)

Row082:	  ;F05  G06  H02  F11  M04  F03  G04  F06  G05  W07  M09  D02  M04  D08  M02  D01
.byte $64, $05, $21, $6A, $33, $62, $03, $65, $04, $46, $38, $11, $33, $17, $31, $10
;			 M02  D01  M03  W08  F13  M02  H02  F05  G05
.byte $31, $10, $32, $47, $6C, $31, $21, $64, $04

Row083:	  ;F04  G06  H04  F09  M08  G05  F04  G06  W08  M08  D01  M09  D03  M03  D02  M01
		.byte $63, $05, $23, $68, $37, $04, $63, $05, $47, $37, $10, $38, $12, $32, $11, $30;($A371)
;			 D01  M04  W07  F13  M03  H02  F05  G04
.byte $10, $33, $46, $6C, $32, $21, $64, $03

Row084:	  ;F05  G04  H04  F09  M11  G12  W11  H02  D05  M10  D01  M05  D04  M03  W08  F13
		.byte $64, $03, $23, $68, $3A, $0B, $4A, $21, $14, $39, $10, $34, $13, $32, $47, $6C;($A389)
;			 M02  H03  F05  G02  W01
		.byte $31, $22, $64, $01, $40;($A399)

Row085:	  ;F05  G02  H05  F09  M14  G08  W11  H05  M03  D02  M09  D01  M08  F01  M04  W08
.byte $64, $01, $24, $68, $3D, $07, $4A, $24, $32, $11, $38, $10, $37, $60, $33, $47
;			 F13  M02  F08
.byte $6C, $31, $67

Row086:	  ;W02  F05  H06  F05  M05  D07  M07  G04  W09  F03  H07  M03  D05  M05  D01  M07
		.byte $41, $64, $25, $64, $34, $16, $36, $03, $48, $62, $26, $32, $14, $34, $10, $36;($A3B1)
;			 F03  M03  W11  F08  H04  F08
.byte $62, $32, $4A, $67, $23, $67

Row087:	  ;W03  F05  H06  F02  M03  D12  M05  W13  F05  H05  M14  D07  F05  M03  W12  F05
		.byte $42, $64, $25, $61, $32, $1B, $34, $4C, $64, $24, $3D, $16, $64, $32, $4B, $64;($A3C7)
;			 H05  F08
		.byte $24, $67		  ;($A3D7)

Row088:	  ;W02  F06  H09  D15  M03  W12  F06  H06  M07  G03  M10  F07  M02  W13  F06  H04
.byte $41, $65, $28, $1E, $32, $4B, $65, $25, $36, $02, $39, $66, $31, $4C, $65, $23
;			 F06  W03
.byte $65, $42

Row089:	  ;F09  H07  D09  T01  D05  M02  W12  F06  H08  M02  F03  G04  W04  M08  F05  M02
.byte $68, $26, $18, $80, $14, $31, $4B, $65, $27, $31, $62, $03, $43, $37, $64, $31
;			 W15  F06  H04  F03  W05
		.byte $4E, $65, $23, $62, $44;($A3FB)

Row090:	  ;F11  H05  D14  W06  F13  H09  M02  F05  G05  W03  P05  M04  F02  M02  W14  F07
		.byte $6A, $24, $1D, $45, $6C, $28, $31, $64, $04, $42, $74, $33, $61, $31, $4D, $66;($A400)
;			 H06  F03  W04
.byte $25, $62, $43

Row091:	  ;W01  F12  H02  D12  W07  F07  W07  H07  M04  F06  G05  B01  P05  G04  M03  F01
.byte $40, $6B, $21, $1B, $46, $66, $46, $26, $33, $65, $04, $B0, $74, $03, $32, $60
;			 W16  W01  F07  H04  F05
		.byte $4F, $40, $66, $23, $64;($A423)

Row092:	  ;W05  F09  D11  W07  F04  W04  F06  H07  M03  F10  G03  W02  P04  G06  M02  G02
		.byte $44, $68, $1A, $46, $63, $43, $65, $26, $32, $69, $02, $41, $73, $05, $31, $01;($A428)
;			 W16  F07  H03  F05
		.byte $4F, $66, $22, $64;($A438)

Row093:	  ;W11  F02  D13  W05  F08  W08  H05  M02  F11  W04  P05  G06  M04  G02  W16  F04
.byte $4A, $61, $1C, $44, $67, $47, $24, $31, $6A, $43, $74, $05, $33, $01, $4F, $63
;			 H04  F05
.byte $23, $64

Row094:	  ;W08  D15  W10  F15  H03  M02  F08  W07  P05  G06  M05  G01  W14  F02  W02  F04
		.byte $47, $1E, $49, $6E, $22, $31, $67, $46, $74, $05, $34, $00, $4D, $61, $41, $63;($A44E)
;			 H04  F05
		.byte $23, $64		  ;($A45E)

Row095:	  ;W04  D16  D05  W05  F08  W04  F07  M03  F05  W12  P03  G07  F02  M02  G03  W12
		.byte $43, $1F, $14, $44, $67, $43, $66, $32, $64, $4B, $72, $06, $61, $31, $02, $4B;($A460)
;			 F04  W01  F05  H02  F05  W05
		.byte $63, $40, $64, $21, $64, $44;($A470)

Row096:	  ;W02  D06  H06  D11  F05  W13  F04  M03  F05  W13  G11  F03  M02  G03  W10  F05
		.byte $41, $15, $25, $1A, $64, $4C, $63, $32, $64, $4C, $0A, $62, $31, $02, $49, $64;($A476)
;			 W02  F10  W06
		.byte $41, $69, $45	 ;($A486)

Row097:	  ;W03  D03  H04  F05  D09  F15  W03  F03  M02  F07  W11  F04  G09  F05  M03  G02
		.byte $42, $12, $23, $64, $18, $6E, $42, $62, $31, $66, $4A, $63, $08, $64, $32, $01;($A489)
;			 W11  F04  W02  F09  W06
.byte $4A, $63, $41, $68, $45

Row098:	  ;W02  H06  F10  D05  F16  F01  B01  F02  M03  F07  W07  F10  G07  F08  M02  G02
		.byte $41, $25, $69, $14, $6F, $60, $B0, $61, $32, $66, $46, $69, $06, $67, $31, $01;($A49E)
;			 W09  F06  W02  F07  W07
.byte $48, $65, $41, $66, $46

Row099:	  ;W01  H05  F14  D04  F14  W04  M02  F04  G04  W10  F09  G06  F07  M02  G03  W09
.byte $40, $24, $6D, $13, $6D, $43, $31, $63, $03, $49, $68, $05, $66, $31, $02, $48
;			 F02  P01  F04  B01  F06  W08
.byte $61, $70, $63, $B0, $65, $47

Row100:	  ;H07  F14  D04  F11  W09  G06  W10  F10  R02  G01  R02  F07  M04  G03  W07  F02
.byte $26, $6D, $13, $6A, $48, $05, $49, $69, $51, $00, $51, $66, $33, $02, $46, $61
;			 P03  F03  W02  F04  W09
.byte $72, $62, $41, $63, $48

Row101:	  ;H05  M04  F12  D05  F07  W11  G06  W12  F09  R01  G03  R01  F07  M05  G03  W06
		.byte $24, $33, $6B, $14, $66, $4A, $05, $4B, $68, $50, $02, $50, $66, $34, $02, $45;($A4DE)
;			 F03  P03  F02  W02  F03  W10
.byte $62, $72, $61, $41, $62, $49

Row102:	  ;H06  M05  F09  D07  F06  M02  W04  M05  G06  W14  F07  R01  G01  T01  G01  R01
		.byte $25, $34, $68, $16, $65, $31, $43, $34, $05, $4D, $66, $50, $00, $80, $00, $50;($A4F4)
;			 F08  M05  H03  W06  F03  P02  F03  W14
		.byte $67, $34, $22, $45, $62, $71, $62, $4D;($A504)

Row103:	  ;H08  M05  F07  D08  F05  M03  W02  M04  F02  G05  W02  G04  W11  F05  R01  G03
		.byte $27, $34, $66, $17, $64, $32, $41, $33, $61, $04, $41, $03, $4A, $64, $50, $02;($A50C)
;			 R01  F10  M02  H05  W05  F02  G04  F03  W13
.byte $50, $69, $31, $24, $44, $61, $03, $62, $4C

Row104:	  ;H07  M09  F04  D08  H02  F04  M07  F04  G04  B01  G05  F05  W07  F04  R05  F09
		.byte $26, $38, $63, $17, $21, $63, $36, $63, $03, $B0, $04, $64, $46, $63, $54, $68;($A525)
;			 M03  H06  W05  F02  G03  H04  G03  W09
.byte $32, $25, $44, $61, $02, $23, $02, $48

Row105:	  ;H07  M02  F05  M07  D05  H06  F03  M05  F05  G03  W02  G04  F10  M04  F16  M03
		.byte $26, $31, $64, $36, $14, $25, $62, $34, $64, $02, $41, $03, $69, $33, $6F, $32;($A53D)
;			 H06  W08  G02  H07  G06  W04
.byte $25, $47, $01, $26, $05, $43

Row106:	  ;W01  H05  M02  F08  M07  D02  H08  M06  F07  W03  F03  G05  F08  M06  F10  M06
		.byte $40, $24, $31, $67, $36, $11, $27, $35, $66, $42, $62, $04, $67, $35, $69, $35;($A553)
;			 H05  W10  H03  M05  H03  G05
		.byte $24, $49, $22, $34, $22, $04;($A563)

Row107:	  ;W03  H03  M02  F05  G05  M04  H12  M06  F05  W03  F05  G06  F08  M08  F04  M07
.byte $42, $22, $31, $64, $04, $33, $2B, $35, $64, $42, $64, $05, $67, $37, $63, $36
;			 H07  W08  H03  M03  F02  M03  H02  G04
.byte $26, $47, $22, $32, $61, $32, $21, $03

Row108:	  ;W05  H02  M02  F03  G07  H13  M07  F05  W03  F07  G06  F08  M16  M01  H09  W06
		.byte $44, $21, $31, $62, $06, $2C, $36, $64, $42, $66, $05, $67, $3F, $30, $28, $45;($A581)
;			 H03  M03  F04  M02  H03  G01
		.byte $22, $32, $63, $31, $22, $00;($A591)

Row109:	  ;W04  H04  M03  G07  H13  M07  F05  W04  F06  G09  F05  P03  M11  P05  H06  W07
		.byte $43, $23, $32, $06, $2C, $36, $64, $43, $65, $08, $64, $72, $3A, $74, $25, $46;($A597)
;			 H03  M03  F03  S01  F02  M02  G02  W05
		.byte $22, $32, $62, $C0, $61, $31, $01, $44;($A5A7)

Row110:	  ;W03  H05  M02  G09  H10  M06  F08  W05  F04  G10  F03  P08  M07  P07  H06  W07
		.byte $42, $24, $31, $08, $29, $35, $67, $44, $63, $09, $62, $77, $36, $76, $25, $46;($A5AF)
;			 H03  M02  F05  M04  G04
.byte $22, $31, $64, $33, $03

Row111:	  ;W04  H04  M02  G10  H08  M06  F09  W04  F05  G10  F03  P09  M05  P09  H04  W09
		.byte $43, $23, $31, $09, $27, $35, $68, $43, $64, $09, $62, $78, $34, $78, $23, $48;($A5C4)
;			 H03  M02  F04  M02  H03  G03
		.byte $22, $31, $63, $31, $22, $02;($A5D4)

Row112:	  ;W05  H05  G10  H09  M04  F09  W06  F05  G08  F03  P11  M03  P11  H02  W10  H03
		.byte $44, $24, $09, $28, $33, $68, $45, $64, $07, $62, $7A, $32, $7A, $21, $49, $22;($A5DA)
;			 M03  F01  M03  H03  G03
		.byte $32, $60, $32, $22, $02;($A5EA)

Row113:	  ;W07  H04  G08  H08  M05  F09  W07  F07  G06  F04  P16  P09  W12  H03  M02  F01
.byte $46, $23, $07, $27, $34, $68, $46, $66, $05, $63, $7F, $78, $4B, $22, $31, $60
;			 M02  H03  G03
.byte $31, $22, $02

Row114:	  ;W06  H06  G06  H04  W03  M08  F07  W09  F08  G03  F05  P11  W02  P11  W13  H09
		.byte $45, $25, $05, $23, $42, $37, $66, $48, $67, $02, $64, $7A, $41, $7A, $4C, $28;($A602)
;			 G04
		.byte $03			   ;($A612)

Row115:	  ;W07  H06  G04  H04  W05  F13  W12  F13  P11  W04  P09  W14  H06  P03  W09
.byte $46, $25, $03, $23, $44, $6C, $4B, $6C, $7A, $43, $78, $4D, $25, $72, $48

Row116:	  ;W08  H14  W03  F12  W16  F10  P11  W08  P04  W16  W01  H04  P02  W11
.byte $47, $2D, $42, $6B, $4F, $69, $7A, $47, $73, $4F, $40, $23, $71, $4A

Row117:	  ;W09  H13  B01  H06  F05  W16  W05  F05  P13  W16  W15  H02  P02  W12
		.byte $48, $2C, $B0, $25, $64, $4F, $44, $64, $7C, $4F, $4E, $21, $71, $4B;($A630)

Row118:	  ;W11  H10  W03  H07  W16  W12  P13  W16  W16  P04
		.byte $4A, $29, $42, $26, $4F, $4B, $7C, $4F, $4F, $73;($A63E)

Row119:	  ;W12  H07  W16  W16  W09  P10  W16  W16  W02  P03  W13
.byte $4B, $26, $4F, $4F, $48, $79, $4F, $4F, $41, $72, $4C

;Pointers to world map rows.
WrldMapPtrTbl:
		.word Row000, Row001, Row002, Row003, Row004, Row005, Row006, Row007;($A653)
.word Row008, Row009, Row010, Row011, Row012, Row013, Row014, Row015
		.word Row016, Row017, Row018, Row019, Row020, Row021, Row022, Row023;($A673)
		.word Row024, Row025, Row026, Row027, Row028, Row029, Row030, Row031;($A683)
		.word Row032, Row033, Row034, Row035, Row036, Row037, Row038, Row039;($A693)
		.word Row040, Row041, Row042, Row043, Row044, Row045, Row046, Row047;($A6A3)
.word Row048, Row049, Row050, Row051, Row052, Row053, Row054, Row055
.word Row056, Row057, Row058, Row059, Row060, Row061, Row062, Row063
.word Row064, Row065, Row066, Row067, Row068, Row069, Row070, Row071
.word Row072, Row073, Row074, Row075, Row076, Row077, Row078, Row079
.word Row080, Row081, Row082, Row083, Row084, Row085, Row086, Row087
		.word Row088, Row089, Row090, Row091, Row092, Row093, Row094, Row095;($A703)
.word Row096, Row097, Row098, Row099, Row100, Row101, Row102, Row103
		.word Row104, Row105, Row106, Row107, Row108, Row109, Row110, Row111;($A723)
.word Row112, Row113, Row114, Row115, Row116, Row117, Row118, Row119

;----------------------------------------------------------------------------------------------------

ScreenFadeOut:
LDA DrgnLrdPal		  ;Is player about to fight the end boss?
		CMP #EN_DRAGONLORD2	 ;($A746)
		BEQ LoadEndPals		 ;($A748)If so, branch.

		LDA #PAL_LOAD_BG		;($A74A)Indicate background palette should be loaded.
STA LoadBGPal		   ;

LDA RegSPPalPtr		 ;
		STA SpritePalettePointerLB;($A751)Set pointer for sprite palettes.
LDA RegSPPalPtr+1	   ;
		STA SpritePalettePointerUB;($A756)

LDA OverworldPalPtr	 ;
		CLC					 ;($A75B)
		ADC MapType			 ;($A75C)
STA BackgroundPalettePointerLB		  ;Calculate background palette pointer based on map type.
LDA OverworldPalPtr+1   ;
ADC #$00				;
		STA BackgroundPalettePointerUB;($A765)

JSR PalFadeOut		  ;($C212)Fade out both background and sprite palettes.
		JMP ClearWindowBufferRAM2;($A76A)($A788)Clear RAM buffer used for drawing text windows.

LoadEndPals:
LDA #PAL_LOAD_BG		;Indicate background palette should be loaded.
STA LoadBGPal		   ;

		LDA EndBossPal1Ptr	  ;($A771)
		STA BackgroundPalettePointerLB;($A774)Set pointer for background palettes.
LDA EndBossPal1Ptr+1	;
STA BackgroundPalettePointerUB		  ;

LDA EndBossPal2Ptr	  ;
		STA SpritePalettePointerLB;($A77E)Set pointer for sprite palettes.
LDA EndBossPal2Ptr+1	;
STA SpritePalettePointerUB		;

JSR PalFadeOut		  ;($C212)Fade out both background and sprite palettes.

;----------------------------------------------------------------------------------------------------

ClearWindowBufferRAM2:
		LDA #$00				;($A788)
STA GeneralPointer3CLB		  ;Set base address to $0400(start of window buffer RAM).
LDA #$04				;
STA GeneralPointer3CUB		  ;

WindowBufferRAMLoop:
LDY #$00				;Initialize offset.
		LDA #$FF				;($A792)Indicates window tile is empty.

		* STA (GeneralPointer3C),Y;($A794)Have 256 bytes been cleared?
INY					 ;
		BNE -				   ;($A797)If not, branch to clear another byte.

INC GeneralPointer3CUB		  ;
LDA GeneralPointer3CUB		  ;
CMP #$08				;Has all the window RAM buffer been cleared?
BNE WindowBufferRAMLoop	   ;If not, branch to clear another 256 bytes.
		RTS					 ;($A7A1)

;----------------------------------------------------------------------------------------------------

RemoveWindow:
		STA WindowTypeCopy	  ;($A7A2)Save a copy of the window type.

		BRK					 ;($A7A4)Get parameters for removing windows from the screen.
.byte $00, $17		  ;($AF24)WindowEraseParams, bank 1.

		LDA WindowEraseWidth	;($A7A7)
LSR					 ;Convert wiindow erase position from tiles to blocks.
		ORA #$10				;($A7AB)Does not appear to be used anywhere.
STA WindowWidthTemp		;

		LDA WindowEraseHeight   ;($A7B0)
		SEC					 ;($A7B3)
SBC #$01				;
		ASL					 ;($A7B6)Perform a calculation on the window erase height and
ASL					 ;store it. It is referenced below but does no useful work.
		ASL					 ;($A7B8)
ASL					 ;
		ADC WindowErasePosition ;($A7BA)
STA _WindowPosition		;

LDA WindowErasePosition		 ;Get the X position of the window in blocks.
AND #$0F				;

STA XPosFromLeft		;
SEC					 ;Convert the X positon into a signed value. then, multiply
SBC #$08				;by 2 to convert to tiles.
ASL					 ;
STA StartSignedXPos	 ;

LDA WindowEraseHeight		;Store the window erase height. Does not appera to be used.
		STA BlockCounter		;($A7D0)
SEC					 ;Get the height of the window in blocks - 1.
		SBC #$01				;($A7D3)

		PHA					 ;($A7D5)Save the height for later.

		LDA WindowErasePosition ;($A7D6)
		LSR					 ;($A7D9)
LSR					 ;Get the Y position of the window, in blocks.
		LSR					 ;($A7DB)
LSR					 ;
STA WindowLineBufferIndex	   ;

		PLA					 ;($A7DF)Get the height calculation again.

		CLC					 ;($A7E0)Add the height of the window to the offset of
ADC WindowLineBufferIndex	   ;the window on the screen. Result is in blocks.
		STA WindowLineBufferIndex;($A7E3)

SEC					 ;
		SBC #$07				;($A7E6)Convert the Y positon into a signed value. then, multiply
ASL					 ;by 2 to convert to tiles.
		STA YPosFromCenter	  ;($A7E9)

LDA WindowEraseWidth		;
		LSR					 ;($A7EE)Store the width of the window in blocks.
STA WindowBlockWidth	   ;

LDA WindowLineBufferIndex	   ;Set the start of the removal to the bottom of the window.
		STA YPosFromTop		 ;($A7F3)

		JSR CalcPPUBufAddr	  ;($A7F5)($C596)Calculate PPU address.

LDA PPUAddrLB		   ;
		STA BlockAddrLB		 ;($A7FA)Copy PPU address pointer to block address pointer.
		LDA PPUAddrUB		   ;($A7FC)
		STA BlockAddrUB		 ;($A7FE)

LDA WindowTypeCopy		 ;Get the window type.
		BEQ SetWndBack		  ;($A802)Is this the pop-up window? If so. branch. Background window.

		CMP #WINDOW_DIALOG	  ;($A804)Is this a dialog window?
		BEQ SetWndBack		  ;($A806)If so, branch. Background window.

CMP #WINDOW_CMD_NONCMB	 ;Is this a non-combat command window?
		BEQ SetWndBack		  ;($A80A)If so, branch. Background window.

CMP #WINDOW_CMD_CMB		;Is this a combat command window?
BEQ SetWndBack		  ;If so, branch. Background window.

		CMP #WINDOW_ALPHBT	  ;($A810)Is this the alphabet selection window?
		BEQ SetWndBack		  ;($A812)If so, branch. Background window.

LDA #WINDOW_FOREGROUND	 ;Set the window as a foreground window(covers other windows).
BEQ SetWndBackFore	  ;

SetWndBack:
LDA #WINDOW_BACKGROUND	 ;Set the window as a background window(covered by other windows).

SetWndBackFore:
		STA WindowForeBack	  ;($A81A)Set window as foreground/background window.

WindowRemoveRowLoop:
LDA #$00				;
		STA AttribBufIndex   ;($A81E)Reset buffer index to remove a new row.
STA WindowLineBufferIndex	   ;

		LDA StartSignedXPos	 ;($A822)Set the X position to start erasing row.
STA XPosFromCenter	  ;

		LDA WindowBlockWidth	;($A826)Set the width of the window in blocks.
STA WindowColumnPosition		   ;

WindowRemoveBlockLoop:
JSR ClearWndBuf		 ;($A880)Clear window block from buffers and uncover windows.

LDA BlockAddrLB		 ;
CLC					 ;
ADC #$02				;Increment the block address pointer by 2. points at WindowBufferRAM.
STA BlockAddrLB		 ;
BCC +				   ;
INC BlockAddrUB		 ;

* INC WindowLineBufferIndex	   ;Increment the window line buffer index by 2.
INC WindowLineBufferIndex	   ;

INC AttribBufIndex	  ;Increment the attribute table buffer index.

INC XPosFromCenter	  ;Increment to the next block in the row(2X2 tiles per block).
INC XPosFromCenter	  ;

DEC WindowColumnPosition		   ;Are there more blocks in this window row to process?
		BNE WindowRemoveBlockLoop;($A844)If so, branch to do another block.

BRK					 ;Show/hide window on the screen.
		.byte $01, $17		  ;($A847)($ABC4)WindowShowHide.

		LDA BlockAddrLB		 ;($A849)
		CLC					 ;($A84B)
ADC #$C0				;Subtract 64 tiles from pointer. (2 rows up the nametables).
STA BlockAddrLB		 ;This moves to the next block up.
		BCS +				   ;($A850)
		DEC BlockAddrUB		 ;($A852)

		* LDA WindowBlockWidth  ;($A854)Start at beginnig of row by converting block width
ASL					 ;into tiles.
		STA XPosFromLeft		;($A857)

		LDA BlockAddrLB		 ;($A859)
		SEC					 ;($A85B)
SBC XPosFromLeft		;Move back to the beginning of the row of blocks to erase next.
STA BlockAddrLB		 ;
BCS +				   ;
DEC BlockAddrUB		 ;

* LDA _WndPosition		;
		SEC					 ;($A867)Decrement the Y position of the window by 1 block.
SBC #$10				;Does not appear to be used for anything.
		STA _WndPosition		;($A86A)

DEC YPosFromCenter	  ;Move to next block row down(2X2 tiles per block).
DEC YPosFromCenter	  ;

DEC WindowRowPos		   ;Move to next window row(in blocks).
		BNE WindowRemoveRowLoop ;($A873)More rows to erase? If so, branch to do another row.

LDA StopNPCMove		 ;Are NPCs moving?
		BEQ DoneRemoveWindow	;($A877)If so, branch to exit routine. Nothing left to do.

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.
JSR DoSprites		   ;($B6DA)Update player and NPC sprites.

DoneRemoveWindow:
RTS					 ;Window is now removed. Exit.

;----------------------------------------------------------------------------------------------------

ClearWndBuf:
		LDA WindowForeBack	  ;($A880)Is this a background window?
		BNE ClrWindowBlock	  ;($A882)If so, branch.

		LDY #$00				;($A884)Is this a foreground window over a blank block?
LDA (BlockAddr),Y	   ;
CMP #$FF				;
BEQ ClrWindowBlock	  ;If so, branch to clear window block.

CMP #$FE				;Is this a foreground window block not covering other window?
BEQ ClrWindowBlock	  ;If so, branch to clear window block.

JMP UncoverWindow	   ;($A8AD)Uncover a window hidden by a foreground window.

ClrWindowBlock:
LDA #$00				;
STA BlkRemoveFlgs	   ;Remove no tiles from the current block.
STA AddAttribData	   ;Indicate attrib data needs to be moved to buffer.
		JSR ModWindowBlock	  ;($A899)($A921)Replace window block with map block.

LDY #$00				;
LDA #$FF				;
STA (BlockAddr),Y	   ;Clear upper row of window block.
INY					 ;
		STA (BlockAddr),Y	   ;($A8A3)

		LDY #$20				;($A8A5)
STA (BlockAddr),Y	   ;
INY					 ;Clear lower row of window block.
		STA (BlockAddr),Y	   ;($A8AA)
RTS					 ;

UncoverWindow:
LDA NTBlockY			;*2. Convert the block position to tile position.
ASL					 ;
ADC YPosFromCenter	  ;Calculate the nametable Y block that needs to be replaced.
CLC					 ;Add signed location of block to unsigned nametable location.
		ADC #$1E				;($A8B3)Add Screen height in tiles to ensure result is always positive.
STA DivideNumber1LB		   ;

LDA #$1E				;Divide out tile height and get remainder. Result will be
		STA DivideNumber2	   ;($A8B9)between #$00-#$1E(height of screen in tiles).
		JSR ByteDivide		  ;($A8BB)($C1F0)Divide a 16-bit number by an 8-bit number.

		LDA DivideRemainder	 ;($A8BE)The final result is the unsigned Y position of the block
		STA YPosFromTop		 ;($A8C0)to replace, measured in tiles. #$00-#$1E.
		STA YFromTopTemp		;($A8C2)

		LDA NTBlockX			;($A8C4)*2. Convert the block position to tile position.
		ASL					 ;($A8C6)Calculate the nametable X block that needs to be replaced.
CLC					 ;Add signed location of block to unsigned nametable location.
		ADC XPosFromCenter	  ;($A8C8)Keep only lower 6 bits. The row is 64 tiles wide as it spans
		AND #$3F				;($A8CA)both nametables. The final result is the unsigned X position
		STA XPosFromLeft		;($A8CC)of the block to replace, measured in tiles. #$00-#$3F. No
STA XFromLeftTemp	   ;division necessary. value rolls over naturally.

		JSR DoAddressCalculation;($A8D0)($C5AA)Calculate destination address for GFX data.

		LDX WindowLineBufferIndex;($A8D3)Initialize indexes.
		LDY #$00				;($A8D5)

		LDA (BlockAddr),Y	   ;($A8D7)
STA WindowLineBuffer,X		;
		INY					 ;($A8DC)Transfer upper row of block data into window line buffer.
		LDA (BlockAddr),Y	   ;($A8DD)
		STA WindowLineBuffer+1,X;($A8DF)

		TXA					 ;($A8E2)
CLC					 ;Move to next row in window line buffer.
ADC WindowEraseWdth		;
TAX					 ;

		LDY #$20				;($A8E8)
LDA (BlockAddr),Y	   ;
		STA WindowLineBuffer,X  ;($A8EC)
		INY					 ;($A8EF)Transfer upper row of block data into window line buffer.
LDA (BlockAddr),Y	   ;
		STA WindowLineBuffer+1,X;($A8F2)

LDA XFromLeftTemp	   ;
STA XPosFromLeft		;Update X and Y position for next window block.
LDA YFromTopTemp		;
STA YPosFromTop		 ;

LDY #$00				;Zero out index.

		LDA (BlockAddr),Y	   ;($A8FF)Sets attribute table value for each block based on its
		CMP #$C1				;($A901)position in the pattern table.
BCS +				   ;Is this a sky tile in the battle scene? If not, branch.

		LDA #$00				;($A905)Set attribute table value for battle scene sky tiles.
		BEQ StoreAttribByte	 ;($A907)

		* CMP #$CA			  ;($A909)Is this a green covered mountain tile in the battle scene?
BCS +				   ;If not, branch.

LDA #$01				;Set attribute table value for battle scene green covered
		BNE StoreAttribByte	 ;($A90F)mountain tiles. Branch always.

		* CMP #$DE			  ;($A911)Is this a foreground tile in the battle scene?
		BCS +				   ;($A913)If not, branch.

LDA #$02				;Set attribute table value for battle scene foreground tiles.
BNE StoreAttribByte	 ;Branch always.

		* LDA #$03			  ;($A919)Set attribute table values for battle scene horizon tiles.

StoreAttribByte:
		LDX AttribBufIndex   ;($A91B)
		STA AttributeTblBuf,X   ;($A91D)Store the attribute table byte in the buffer.
RTS					 ;

;----------------------------------------------------------------------------------------------------

ModWindowBlock:
		LDA NTBlockY			;($A921)*2. Convert the block position to tile position.
ASL					 ;
		CLC					 ;($A924)Calculate the nametable Y block that needs to be replaced.
		ADC YPosFromCenter	  ;($A925)Add signed location of block to unsigned nametable location.
		CLC					 ;($A927)
		ADC #$1E				;($A928)Add Screen height in tiles to ensure result is always positive.
		STA DivideNumber1LB	 ;($A92A)

LDA #$1E				;Divide out tile height and get remainder. Result will be
STA DivideNumber2			 ;between #$00-#$1E(height of screen in tiles).
JSR ByteDivide		  ;($C1F0)Divide a 16-bit number by an 8-bit number.

		LDA DivideRemainder	 ;($A933)The final result is the unsigned Y position of the block
		STA YPosFromTop		 ;($A935)to replace, measured in tiles. #$00-#$1E.
STA YFromTopTemp		;

		LDA NTBlockX			;($A939)*2. Convert the block position to tile position.
		ASL					 ;($A93B)Calculate the nametable X block that needs to be replaced.
CLC					 ;Add signed location of block to unsigned nametable location.
		ADC XPosFromCenter	  ;($A93D)Keep only lower 6 bits. The row is 64 tiles wide as it spans
		AND #$3F				;($A93F)both nametables. The final result is the unsigned X position
		STA XPosFromLeft		;($A941)of the block to replace, measured in tiles. #$00-#$3F. No
STA XFromLeftTemp	   ;division necessary. value rolls over naturally.

		JSR DoAddressCalculation;($A945)($C5AA)Calculate destination address for GFX data.

		LDA XPosFromCenter	  ;($A948)
ASL					 ;/2 with sign extension to convert block X location.
LDA XPosFromCenter	  ;
ROR					 ;

		CLC					 ;($A94E)
		ADC CharXPos			;($A94F)Add the player's X position in preparation to get block type.
STA XTarget			 ;

		LDA YPosFromCenter	  ;($A953)
		ASL					 ;($A955)/2 with sign extension to convert to block Y location.
		LDA YPosFromCenter	  ;($A956)
ROR					 ;

CLC					 ;
ADC CharYPos			;Add the player's Y position in preparation to get block type.
STA YTarget			 ;

JSR GetBlockID		  ;($AC17)Get description of block.

LDA MapType			 ;Is the player in a dungeon?
		CMP #MAP_DUNGEON		;($A963)
		BNE ChkCoveredArea	  ;($A965)If not, branch.

LDA XPosFromCenter	  ;Is X position a positive value?
BPL +				   ;If so, branch.

EOR #$FF				;
		CLC					 ;($A96D)
ADC #$01				;2s compliment. Convert X position to a positive number.
STA GenByte3E		   ;
JMP ChkLightDiameterX   ;

		* LDA XPosFromCenter	;($A975)Store the unsigned tile X position.
		STA GenByte3E		   ;($A977)

ChkLightDiameterX:
LDA LightDiameter	   ;Is target block outside the visible area in a dungeon?
		CMP GenByte3E		   ;($A97B)
BCS ChkLightXEdge	   ;If not, branch.

		LDA #BLK_BLANK		  ;($A97F)Target block is outside visible area.
		STA TargetResults	   ;($A981)Load a blank block.

LDA #$00				;Remove no tiles from the current block.
STA BlkRemoveFlgs	   ;
		BEQ CalcBlockIndex	  ;($A987)Branch always.

ChkLightXEdge:
BNE ChkLightY		   ;Branch if block is not at the very edge of the lighted area.

		LDA XPosFromCenter	  ;($A98B)Is block on the right edge of lighted area?
		BPL LightXRight		 ;($A98D)If so, branch.

LDA #$05				;Black out left side of block.
		STA BlkRemoveFlgs	   ;($A991)Block is on the left edge of lighted area.
		BNE ChkLightY		   ;($A993)Branch always.

LightXRight:
LDA #$0A				;Black out right side of block.
		STA BlkRemoveFlgs	   ;($A997)Block is on the right edge of lighted area.

ChkLightY:
LDA YPosFromCenter	  ;Is Y position a positive value?
BPL LightYBottom		;If so, branch.

EOR #$FF				;
		CLC					 ;($A99F)
ADC #$01				;2s compliment. Convert Y position to a positive number.
		STA GenByte3E		   ;($A9A2)
JMP ChkLightDiameterY   ;

LightYBottom:
LDA YPosFromCenter	  ;Store the unsigned tile Y position.
STA GenByte3E		   ;

ChkLightDiameterY:
		LDA LightDiameter	   ;($A9AB)Is target block outside the visible area in a dungeon?
		CMP GenByte3E		   ;($A9AD)
BCS ChkLightYEdge	   ;If not, branch.

LDA #BLK_BLANK		  ;Target block is outside visible area.
		STA TargetResults	   ;($A9B3)Load a blank block.

LDA #$00				;Remove no tiles from the current block.
STA BlkRemoveFlgs	   ;
BEQ CalcBlockIndex	  ;Branch always.

ChkLightYEdge:
		BNE CalcBlockIndex	  ;($A9BB)Branch if block is not at the very edge of the lighted area.

		LDA YPosFromCenter	  ;($A9BD)Is block on the bottom edge of lighted area?
		BPL +				   ;($A9BF)If so, branch.

		LDA #$03				;($A9C1)Black out upper half of block.
		STA BlkRemoveFlgs	   ;($A9C3)Block is on the upper edge of lighted area.
BNE CalcBlockIndex	  ;Branch always.

* LDA #$0C				;Black out lower half of block.
STA BlkRemoveFlgs	   ;Block is on the lower edge of lighted area.
BNE CalcBlockIndex	  ;Branch always.

ChkCoveredArea:
		JSR HasCoverData		;($A9CD)($AAE1)Check if current map has covered areas.
		LDA CoverStatusus	   ;($A9D0)
		EOR CoveredStsNext	  ;($A9D2)Did player just enter/exit covered area?
AND #$08				;
BEQ CalcBlockIndex	  ;If not, beanch to move on.

LDA CoverStatusus		 ;Did the player just enter cover?
BNE +				   ;If so, branch.

		LDA #BLK_SML_TILES	  ;($A9DC)Area under cover will be replaced with small tile blocks.
		STA TargetResults	   ;($A9DE)
BNE CalcBlockIndex	  ;Branch always.

* LDA #BLK_BLANK		  ;Areas outside cover will be replaced with blank blocks.
STA TargetResults	   ;

CalcBlockIndex:
		LDA TargetResults	   ;($A9E6)
		ASL					 ;($A9E8)*5. Data for the graphic block is 5 bytes.
		ASL					 ;($A9E9)
ADC TargetResults	   ;

CalcBlockI_AddPtrLo:  ADC GFXTilesPtr		 ;
		STA BlockDataPtrLB	  ;($A9EF)
LDA GFXTilesPtr+1	   ;Calculate the address to the proper GFX block data row.
ADC #$00				;
		STA BlockDataPtrUB	  ;($A9F6)

		LDX WindowLineBufferIndex;($A9F8)Initialize indexes for transferring GFX block data.
LDY #$00				;

LDA (BlockDataPtr),Y	;
		STA WindowLineBuffer,X  ;($A9FE)
INY					 ;Transfer upper row of block data into window line buffer.
		LDA (BlockDataPtr),Y	;($AA02)
		STA WindowLineBuffer+1,X;($AA04)

		TXA					 ;($AA07)
CLC					 ;Move to the next row in the window line buffer.
		ADC WindowEraseWdth	 ;($AA09)
		TAX					 ;($AA0C)

		LDA PPUAddrLB		   ;($AA0D)
CLC					 ;
ADC #$1E				;Move to the next row int the nametable.
STA PPUAddrLB		   ;
BCC +				   ;
INC PPUAddrUB		   ;

* INY					 ;
		LDA (BlockDataPtr),Y	;($AA19)
		STA WindowLineBuffer,X  ;($AA1B)
		INY					 ;($AA1E)Transfer lower row of block data into window line buffer.
		LDA (BlockDataPtr),Y	;($AA1F)
		STA WindowLineBuffer+1,X;($AA21)
		INY					 ;($AA24)

LDA XFromLeftTemp	   ;
STA XPosFromLeft		;Update X and Y position for next window block.
		LDA YFromTopTemp		;($AA29)
		STA YPosFromTop		 ;($AA2B)

LDA (BlockDataPtr),Y	;Get attribute table byte.
STA PPUDataByte		 ;

LDA AddAttribData	   ;Should always be 0. Add attribute table data to buffer.
		BNE ModWndExit		  ;($AA33)Never branch.

		LDX AttribBufIndex   ;($AA35)
LDA PPUDataByte		 ;Add attribute table data to buffer for the corresponding block.
STA AttributeTblBuf,X	  ;

ModWndExit:
RTS					 ;Done removing window block. Return.

;----------------------------------------------------------------------------------------------------

DoPalFadeIn:
		JSR LoadFadePals		;($AA3D)($AA49)Load fade in/fade out palettes.
		JMP PalFadeIn		   ;($AA40)($C529)Fade in both background and sprite palettes.

DoPalFadeOut:
		JSR LoadFadePals		;($AA43)($AA49)Load fade in/fade out palettes.
		JMP PalFadeOut		  ;($AA46)($C212)Fade out both background and sprite palettes.

LoadFadePals:
LDA BlackPalPtr		 ;
STA SpritePalettePointerLB		;Set pointer for sprite palettes.
		LDA BlackPalPtr+1	   ;($AA4E)
STA SpritePalettePointerUB		;

LDA FadePalPtr		  ;
STA BackgroundPalettePointerLB		  ;Set pointer for background palettes.
LDA FadePalPtr+1		;
		STA BackgroundPalettePointerUB;($AA5B)

		LDA #PAL_LOAD_BG		;($AA5D)
STA LoadBGPal		   ;Indicate background palette should be loaded.
RTS					 ;

LoadCreditsPals:
LDA #PAL_LOAD_BG		;Indicate background palette should be loaded.
STA LoadBGPal		   ;

		LDA RegSPPalPtr		 ;($AA66)
STA SpritePalettePointerLB		;Set pointer for sprite palettes.
		LDA RegSPPalPtr+1	   ;($AA6B)
		STA SpritePalettePointerUB;($AA6E)

		LDA TownPalPtr		  ;($AA70)
STA BackgroundPalettePointerLB		  ;Set pointer for background palettes.
LDA TownPalPtr+1		;
		STA BackgroundPalettePointerUB;($AA78)

JSR PalFadeOut		  ;($C212)Fade out both background and sprite palettes.
		RTS					 ;($AA7D)

LoadStartPals:
LDA RegSPPalPtr		 ;
		STA SpritePalettePointerLB;($AA81)Set pointer for sprite palettes.
		LDA RegSPPalPtr+1	   ;($AA83)
STA SpritePalettePointerUB		;

LDA PreGamePalPtr	   ;
		STA BackgroundPalettePointerLB;($AA8B)Set pointer for background palettes.
		LDA PreGamePalPtr+1	 ;($AA8D)
		STA BackgroundPalettePointerUB;($AA90)

		LDA #PAL_LOAD_BG		;($AA92)Indicate background palette should be loaded.
		STA LoadBGPal		   ;($AA94)
		JMP PalFadeIn		   ;($AA96)($C529)Fade in both background and sprite palettes.

LoadIntroPals:
		LDA BlackPalPtr		 ;($AA99)
		STA PalettePointerLB	;($AA9C)Get pointer to palette data.
		LDA BlackPalPtr+1	   ;($AA9E)
STA PalettePointerUB

		LDA #$00				;($AAA3)Indicate no fade in/fade out.
STA PalModByte		  ;

JSR PrepBGPalLoad	   ;($C63D)Load background palette data into PPU buffer
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

LDA BlackPalPtr		 ;
STA PalettePointerLB			;Get pointer to palette data.
LDA BlackPalPtr+1	   ;
		STA PalettePointerUB	;($AAB5)

LDA #$00				;Indicate no fade in/fade out.
STA PalModByte		  ;
JMP PrepSPPalLoad	   ;($C632)Wait for PPU buffer to be open.

;----------------------------------------------------------------------------------------------------

CheckCoveredArea:
		LDA MapWidth			;($AABE)Convert the map width into the number of bytes used to
CLC					 ;represent a map row. 1 nibble represents a block. The
ADC #$01				;increment starts the counting at 1 instead of 0. 2 blocks
		LSR					 ;($AAC3)are represented in a single byte, hence the divide by 2.
		STA MultiplyNumber1LB   ;($AAC4)

		LDA #$00				;($AAC6)
STA MultiplyNumber1UB		  ;Upper byte of first word is always 0.
STA MultiplyNumber2UB		  ;Upper byte of second word is always 0.

		LDA _TargetY			;($AACC)Target Y is player's Y position. Calculate number of map
		STA MultiplyNumber2LB   ;($AACE)bytes to player's current row.
JSR WordMultiply		;($C1C9)Multiply 2 words.

		LDA _TargetX			;($AAD3)Target X is player's X position. Add offset in current row
		LSR					 ;($AAD5)to byte count value for exact byte offset in covered area
		CLC					 ;($AAD6)map data.
ADC MultiplyResultLB		  ;

STA GenWord3ELB		 ;
		LDA MultiplyResultUB	;($AADB)The player's index into the covered map data is now
		ADC #$00				;($AADD)stored in GenWord3E. This is byte level. Nibble level
		STA GenWord3EUB		 ;($AADF)is required and calculated below.

HasCoverData:
		LDA CoverDatLB		  ;($AAE1)Does the current map even have covered areas?
		ORA CoverDatUB		  ;($AAE3)
		BNE CalcCoveredBlock	;($AAE5)If so, branch to calculate those areas.

NoCover:
		LDA #$00				;($AAE7)
		STA CoveredStsNext	  ;($AAE9)Not in covered area. Exit.
		RTS					 ;($AAEB)

CalcCoveredBlock:
LDA MapWidth			;
CMP _TargetX			;
		BCC NoCover			 ;($AAF0)Is the player beyond the map boundaries?
		LDA MapHeight		   ;($AAF2)If so, branch to exit the cover check function.
CMP _TargetY			;
		BCC NoCover			 ;($AAF6)

		LDA GenWord3ELB		 ;($AAF8)
		CLC					 ;($AAFA)
		ADC CoverDatLB		  ;($AAFB)Add the player's index into the covered map data
STA GenWord3ELB		 ;to the base address of the covered map data for
LDA GenWord3EUB		 ;the current map.
ADC CoverDatUB		  ;
		STA GenWord3EUB		 ;($AB03)

		TYA					 ;($AB05)Save any previous value of Y on the stack.
PHA					 ;

		LDY #$00				;($AB07)
LDA (GenWord3E),Y	   ;Get a byte from the covered map data.
STA CoveredStsNext	  ;

		PLA					 ;($AB0D)Restore the previous value of Y from the stack.
		TAY					 ;($AB0E)

LDA _TargetX			;Odd X position stores data in lower nibble while even position
		AND #$01				;($AB11)stores data in upper nibble.
		BNE FinishCoverCheck	;($AB13)Does upper nibble need to be accessed? If not, branch.

LSR CoveredStsNext	  ;
		LSR CoveredStsNext	  ;($AB17)Get upper nibble data and move it to the lower nibble.
		LSR CoveredStsNext	  ;($AB19)
		LSR CoveredStsNext	  ;($AB1B)

FinishCoverCheck:
		LDA CoveredStsNext	  ;($AB1D)
AND #$08				;Keep only bit 3. This bit determines if the player
STA CoveredStsNext	  ;is under cover or not.
RTS					 ;

;----------------------------------------------------------------------------------------------------

DoWtrConv:
TAX					 ;Save A on stack(water block ID, not used).
PHA					 ;

		LDX #$00				;($AB26)Zero out index into conversion table.

LDY XTarget			 ;Make a copy of the X target coord.
STY GenByte2C		   ;

		CPY #$77				;($AB2C)Is target the last block in the row?
		BEQ ChkWtrBlkRght	   ;($AB2E)If so, branch. Block to right is always another water block.

INY					 ;Get block ID of block to the right of target block.
		STY XTarget			 ;($AB31)
		JSR FindRowBlock		;($AB33)($ABF4)Find block ID of target block in world map row.

ChkWtrBlkRght:
		BEQ PrepBlockLeft	   ;($AB36)Is block to right of target block water? If so, branch.

		TXA					 ;($AB38)Block to right of target is not a water block.
CLC					 ;Set bit 2 in index byte. Shore will be on the right
		ADC #$04				;($AB3A)of the current water block.
TAX					 ;

PrepBlockLeft:
		LDY GenByte2C		   ;($AB3D)Restore the original block X coord. Is target first block row?
BEQ ChkWtrBlkLft		;If so, branch. Block to left is always another water block.

DEY					 ;Get block ID of block to the left of target block.
		STY XTarget			 ;($AB42)
		JSR FindRowBlock		;($AB44)($ABF4)Find block ID of target block in world map row.

ChkWtrBlkLft:
BEQ PrepBlockUp		 ;Is block to left of target block water? If so, branch.

INX					 ;Block to left of target is not a water block.
		INX					 ;($AB4A)set bit 1 in index byte. Shore to left.

PrepBlockUp:
LDA GenByte2C		   ;Restore the original block X coord.
STA XTarget			 ;
LDY YTarget			 ;Is target the first block in the column?
BEQ ChkWtrBlkUp		 ;If so, branch.

DEY					 ;Get block ID of block above target block.
		TYA					 ;($AB54)
JSR ChkWtrOrBrdg		;($ABE8)If target block is water or bridge, set zero flag.

ChkWtrBlkUp:
* BEQ +				   ;Is block above target block water? If so, branch.

INX					 ;Block above is not a water block. Set LSB of index.

		* LDY YTarget		   ;($AB5B)Is target the last block in the column?
		CPY #$77				;($AB5D)
BEQ +				   ;If so, branch.

		INY					 ;($AB61)Get block ID of block below target block.
		TYA					 ;($AB62)
JSR ChkWtrOrBrdg		;($ABE8)If target block is water or bridge, set zero flag.

		* BEQ +				 ;($AB66)Is block below target block water? If so, branch.

		TXA					 ;($AB68)
CLC					 ;Block below is not a water block. calculate final index.
		ADC #$08				;($AB6A)
		TAX					 ;($AB6C)

SetBlockID:
* LDA GenBlkConvTbl,X	 ;Get final block ID from conversion table.
		STA TargetResults	   ;($AB70)

		PLA					 ;($AB72)
TAX					 ;
PLA					 ;Restore X and Y from stack.
		TAY					 ;($AB75)
		RTS					 ;($AB76)

;----------------------------------------------------------------------------------------------------

TrgtOutOfBounds:
TYA					 ;
		PHA					 ;($AB78)Save Y and X on stack.
TXA					 ;
PHA					 ;

LDX #$00				;Assume water with no shore is the out of bounds block.

LDA MapNumber		   ;Is player on overworld map?
CMP #MAP_OVERWORLD	  ;
		BNE BoundsChkEnd		;($AB81)If not, branch. Just use out of bounds block.

;The following code is used to check what kind of water block should be displayed on the far
;edges of the overworld map. The out of bounds block will always be a water block but it may
;border with the land so the shoreline must be caclulated.

LDA YTarget			 ;Is Y value beyond visible screen area?
BMI ChkYBounds		  ;If so, branch.

CMP #$78				;Is the Y within the map bounds?
BCS ChkYBounds		  ;If not, branch to check Y position.

		LDA XTarget			 ;($AB8B)Is the X position 1 left of the map bounds?
		CMP #$FF				;($AB8D)
BEQ ChkRightBounds	  ;If so, branch.

CMP #$78				;Is the X position 1 right of the map bounds?
BNE ChkYBounds		  ;If not, branch.

DEC XTarget			 ;Check if block to the left of the water is land.
LDA YTarget			 ;
JSR ChkWtrOrBrdg		;($ABE8)If target block is water or bridge, set zero flag.
		BEQ +				   ;($AB9C)Is the target land? If not, branch.
LDX #$02				;Water with shore at the left.
		* JMP SetBlockID		;($ABA0)Set the water boundary block with shore on the left.

ChkRightBounds:
INC XTarget			 ;Check if block to the right of the water is land.
		LDA YTarget			 ;($ABA5)
		JSR ChkWtrOrBrdg		;($ABA7)($ABE8)If target block is water or bridge, set zero flag.
		BEQ +				   ;($ABAA)Is the target land? If not, branch.
		LDX #$04				;($ABAC)Water with shore on the right.
		* JMP SetBlockID		;($ABAE)Set the water boundary block with shore on the right.

ChkYBounds:
LDA XTarget			 ;Is X value beyond visible screen area?
		BMI BoundsChkEnd		;($ABB3)If so, branch.

CMP #$78				;Is the X within the map bounds?
		BCS BoundsChkEnd		;($ABB7)If not, branch to exit.

		LDA YTarget			 ;($ABB9)Is the Y position 1 above of the map bounds?
CMP #$FF				;
BEQ ChkDownBounds	   ;If so, branch.

CMP #$78				;Is the Y position 1 below of the map bounds?
		BNE BoundsChkEnd		;($ABC1)If not, branch.

		DEC YTarget			 ;($ABC3)Check if block above the water is land.
		LDA YTarget			 ;($ABC5)
		JSR ChkWtrOrBrdg		;($ABC7)($ABE8)If target block is water or bridge, set zero flag.
		BEQ +				   ;($ABCA)Is the target land? If not, branch.
LDX #$01				;Water with shore at the top.
		* JMP SetBlockID		;($ABCE)Set the water boundary block with shore on the top.

ChkDownBounds:
		INC YTarget			 ;($ABD1)Check if block below the water is land.
		LDA YTarget			 ;($ABD3)
JSR ChkWtrOrBrdg		;($ABE8)If target block is water or bridge, set zero flag.
		BEQ +				   ;($ABD8)Is the target land? If not, branch.
LDX #$08				;Water with shore at the bottom.
		* JMP SetBlockID		;($ABDC)Set the water boundary block with shore on the bottom.

BoundsChkEnd:
LDA BoundryBlock		;Target is beyond map boundary.
		STA TargetResults	   ;($ABE1)Load results with boundary block value.

PLA					 ;
		TAX					 ;($ABE4)
		PLA					 ;($ABE5)Restore X and Y from stack and return.
TAY					 ;
		RTS					 ;($ABE7)

;----------------------------------------------------------------------------------------------------

ChkWtrOrBrdg:
		ASL					 ;($ABE8)*2. Each row entry in WrldMapPtrTbl is 2 bytes.

TAY					 ;
LDA WrldMapPtrTbl,Y	 ;
STA WrldMapPtrLB		;Get a pointer to beginning of desired world map row data.
LDA WrldMapPtrTbl+1,Y   ;
STA WrldMapPtrUB		;

FindRowBlock:
		LDY #$00				;($ABF4)Start at beginning of row.
STY WrldMapXPos		 ;

FindMapBlkLoop2:
		LDA (WrldMapPtr),Y	  ;($ABF8)Get number of times map block repeats.
		AND #$0F				;($ABFA)

SEC					 ;
		ADC WrldMapXPos		 ;($ABFD)Add repeat number to world map X position calculation.
STA WrldMapXPos		 ;

LDA XTarget			 ;Has target block been found?
		CMP WrldMapXPos		 ;($AC03)
		BCC MapBlkFound2		;($AC05)If so, branch.

		INY					 ;($AC07)Increment to next entry in world map row table.
		JMP FindMapBlkLoop2	 ;($AC08)($ABF8)Loop until target block is found.

MapBlkFound2:
LDA (WrldMapPtr),Y	  ;Get target block type.
		AND #$F0				;($AC0D)

		CMP #$40				;($AC0F)Is target block a water block?
BNE ChkBrdgBlk		  ;If not, branch to check for a bridge block.
		RTS					 ;($AC13)Water block. Zero flag set.

ChkBrdgBlk:
CMP #$B0				;Set zero flag if block is a bridge block.
		RTS					 ;($AC16)

;----------------------------------------------------------------------------------------------------

GetBlockID:
LDA XTarget			 ;
		STA _TargetX			;($AC19)Store a copy of the target coordinates.
LDA YTarget			 ;
		STA _TargetY			;($AC1D)

		LDA MapWidth			;($AC1F)Is the target X coordinate within the map bounds?
CMP XTarget			 ;
BCS BlkIDCheckEn		;If so, branch to keep processing.

JmpOutOfBounds:
JMP TrgtOutOfBounds	 ;($AB77)Target out of bounds. Jump for boundary block.

BlkIDCheckEn:
LDA EnemyNumber			;Is player fighting the end boss?
		CMP #EN_DRAGONLORD2	 ;($AC2A)
BNE BlkIDChkYCoord	  ;If not, branch to keep processing.

LDA #BLK_BLANK		  ;
		STA TargetResults	   ;($AC30)Fighting end boss. Return blank tile.
		RTS					 ;($AC32)

BlkIDChkYCoord:
		LDA MapHeight		   ;($AC33)Is the target Y coordinate within the map bounds?
		CMP YTarget			 ;($AC35)
BCC JmpOutOfBounds	  ;If not, branch to get boundary block.

TYA					 ;Save Y on the stack.
		PHA					 ;($AC3A)

		LDA MapNumber		   ;($AC3B)Is the player on the overworld map?
		CMP #MAP_OVERWORLD	  ;($AC3D)
		BNE ChkOthrMaps		 ;($AC3F)If not, branch to check other maps.

LDA XTarget			 ;Is the X position 64?
		CMP #$40				;($AC43)
BNE GetOvrWldTarget	 ;If not, branch.

LDA YTarget			 ;Is the Y position 49?
		CMP #$31				;($AC49)
BNE GetOvrWldTarget	 ;If not, branch.

		LDA ModsnSpells		 ;($AC4D)Has the rainbow bridge been created?
		AND #F_RNBW_BRDG		;($AC4F)
BEQ GetOvrWldTarget	 ;If not, branch.

		LDA #BLK_BRIDGE		 ;($AC53)The target is the rainbow bridge.
		STA TargetResults	   ;($AC55)

		PLA					 ;($AC57)
TAY					 ;Restore Y from stack.
		RTS					 ;($AC59)

GetOvrWldTarget:
LDA YTarget			 ;*2. Each row entry in WrldMapPtrTbl is 2 bytes.
ASL					 ;

		TAY					 ;($AC5D)
LDA WrldMapPtrTbl,Y	 ;
STA WrldMapPtrLB		;Get a pointer to beginning of desired world map row data.
		LDA WrldMapPtrTbl+1,Y   ;($AC63)
STA WrldMapPtrUB		;

LDY #$00				;Start at beginning of row.
STY WrldMapXPos		 ;

FindMapBlkLoop:
		LDA (WrldMapPtr),Y	  ;($AC6C)Get number of times map block repeats.
		AND #$0F				;($AC6E)

SEC					 ;
ADC WrldMapXPos		 ;Add repeat number to world map X position calculation.
		STA WrldMapXPos		 ;($AC73)

		LDA XTarget			 ;($AC75)Has target block been found?
		CMP WrldMapXPos		 ;($AC77)
		BCC MapBlkFound		 ;($AC79)If so, branch.

		INY					 ;($AC7B)Increment to next entry in world map row table.
		JMP FindMapBlkLoop	  ;($AC7C)($AC6C)Loop until target block is found.

MapBlkFound:
LDA (WrldMapPtr),Y	  ;
		LSR					 ;($AC81)
LSR					 ;Get map block type and move to lower nibble.
LSR					 ;
		LSR					 ;($AC84)

		CLC					 ;($AC85)Is target an overworld water block?
ADC MapType			 ;
CMP #$04				;
		BNE ConvBlkID		   ;($AC8A)If not, branch to get other block ID types.

		JMP DoWtrConv		   ;($AC8C)($AB24)Get specific outdoor water block ID.

ConvBlkID:
		TAY					 ;($AC8F)Use block type as index into table.
		LDA WrldBlkConvTbl,Y	;($AC90)Convert world map block to standard block ID.
		STA TargetResults	   ;($AC93)Store table value in results register.

		PLA					 ;($AC95)
		TAY					 ;($AC96)Restore Y from stack. Done.
RTS					 ;

;----------------------------------------------------------------------------------------------------

ChkOthrMaps:
LDA #$00				;Set upper bytes to 0 for multiplication prep.
STA MultiplyNumber1UB		  ;
		STA MultiplyNumber2UB   ;($AC9C)The lower byte of MultiplyNumber2 is TargetY.

LDA MapWidth			;Divide by 2 as 1 byte represents 2 blocks.
		LSR					 ;($ACA0)

ADC #$00				;Prep multiplication.  The result is the start of the
		STA MultiplyNumber1LB   ;($ACA3)row that the target block is on.
		JSR WordMultiply		;($ACA5)($C1C9)Multiply 2 words.

LDA _TargetX			;Divide by 2 as 1 byte represents 2 blocks.
		LSR					 ;($ACAA)

CLC					 ;Add X offset for final address value.
ADC MultiplyResultLB		  ;

STA MapBytePtrLB		;
		STA GenPtr3ELB		  ;($ACB0)
LDA MultiplyResultUB		  ;Store address value results in map byte pointer
		ADC #$00				;($ACB4)and save a copy in a general use pointer.
STA MapBytePtrUB		;
		STA GenPtr3EUB		  ;($ACB8)

		LDA MapBytePtrLB		;($ACBA)
		CLC					 ;($ACBC)
ADC MapDatPtrLB		 ;Add value just calculated to the
		STA MapBytePtrLB		;($ACBF)current map data base address.
		LDA MapBytePtrUB		;($ACC1)
ADC MapDatPtrUB		 ;
		STA MapBytePtrUB		;($ACC5)

		LDY #$00				;($ACC7)
LDA (MapBytePtr),Y	  ;Use new index to retreive desired data byte from memory.
STA TargetResults	   ;

LDA _TargetX			;Is target block have an even numbered X position?
LSR					 ;If so, the upper nibble needs to
BCS ChkRemovedBlks	  ;be shifted to the lower nibble.

		LSR TargetResults	   ;($ACD2)
LSR TargetResults	   ;Shift upper nibble to the lower nibble.
		LSR TargetResults	   ;($ACD6)
		LSR TargetResults	   ;($ACD8)

ChkRemovedBlks:
LDA MapNumber		   ;Is the player currently in a dungeon or town?
		CMP #MAP_TANTCSTL_SL	;($ACDC)
BCC TownBlockMask	   ;If in a town, branch. 16 possible tiles in towns.

		LDA #$07				;($ACE0)8 possible tiles in dungeons.
BNE GetBaseBlockID	  ;Branch always.

TownBlockMask:
LDA #$0F				;16 possible tiles in towns.

GetBaseBlockID:
		AND XTarget			 ;($ACE6)
CLC					 ;Add in the proper offset for the block to find.
		ADC MapType			 ;($ACE9)The offset can either point to town blocks or dungeon
TAY					 ;blocks. A now contains the block ID but special blocks
LDA GenBlkConvTbl,Y	 ;have not yet been considered. That happens next.
STA TargetResults	   ;

		CMP #BLK_PRINCESS	   ;($ACF1)Is the target block princess Gwaelin in the swamp cave?
BNE ChkStairBlock	   ;If not, branch to check for other blocks.

		LDA PlayerFlags		 ;($ACF5)Has Gwaelin been saved or is she being carried?
		AND #F_DONE_GWAELIN	 ;($ACF7)
BEQ ReturnBlockID	   ;If not, branch to return Gwaelin block ID.

LDA #BLK_BRICK		  ;Gwaelin has already been saved or is being carried.
		STA TargetResults	   ;($ACFD)Return target block as a brick floor.
		BNE ReturnBlockID	   ;($ACFF)Branch always.

ChkStairBlock:
CMP #BLK_STAIR_DN	   ;Is the target block stairs down?
		BNE ChkTrsrBlock		;($AD03)If not, branch to check for other blocks.

		LDA MapNumber		   ;($AD05)Is the player in the ground floor of the dragonlord's castle?
CMP #MAP_DLCSTL_GF	  ;
BNE ReturnBlockID	   ;If not, branch to return stair down block ID.

		LDA _TargetX			;($AD0B)Is the target X,Y position that of the secret passage
		CMP #$0A				;($AD0D)behind the dragonlord's throne?
BNE ReturnBlockID	   ;
LDA _TargetY			;
		CMP #$01				;($AD13)
BNE ReturnBlockID	   ;If not, branch to return stair down block ID.

LDA ModsnSpells		 ;Has the secret paggase already been found?
		AND #F_PSG_FOUND		;($AD19)
		BNE ReturnBlockID	   ;($AD1B)If so, branch to return stairs down block ID.

		LDA #BLK_FFIELD		 ;($AD1D)Hidden stairs have not been found yet.
STA TargetResults	   ;Return force field block ID.
		BNE ReturnBlockID	   ;($AD21)Branch always.

ChkTrsrBlock:
CMP #BLK_CHEST		  ;Is the target block a treasure chest?
BNE ChkDoorBlock		;If not, branch to check for other blocks.

		LDY #$00				;($AD27)Zero out index to treasure chest taken array.

ChkTreasureLoop:
		LDA _TargetX			;($AD29)Is there an X position record of this treasure taken?
CMP TrsrXPos,Y		  ;
BNE NextTrsr1		   ;If not, branch to check next item in treasure taken array.

INY					 ;Prepare to check Y position of treasure chest.

		LDA _TargetY			;($AD31)Is there a Y position record of this treasure taken?
CMP TrsrXPos,Y		  ;
BNE NextTrsr2		   ;If not, branch to check next item in treasure taken array.

SetBrickID:
		LDA #BLK_BRICK		  ;($AD38)This treasure has already been taken. Return brick block ID.
		STA TargetResults	   ;($AD3A)

ReturnBlockID:
		PLA					 ;($AD3C)Restore Y from stack.
		TAY					 ;($AD3D)
RTS					 ;TargetResults now contains the block ID.

NextTrsr1:
INY					 ;Move to next treasure position.

NextTrsr2:
INY					 ;Move to next treasure position.

		CPY #$10				;($AD41)Max 8 treasures per map. Have all treasures been checked?
BNE ChkTreasureLoop	 ;If not, branch to check if another has been taken already.

ChkDoorBlock:
LDA TargetResults	   ;Is the target block a door?
		CMP #BLK_DOOR		   ;($AD47)
BNE ReturnBlockID	   ;If not, branch to exit. No more special blocks to check.

LDY #$00				;Zero out index to door opened array.

ChkDoorLoop:
		LDA _TargetX			;($AD4D)Is there an X position record of this door opened?
CMP DoorXPos,Y		  ;
BNE NextDoor1		   ;If not, branch to check next item in door opened array.

INY					 ;Prepare to check Y position of door.

		LDA _TargetY			;($AD55)Is there a Y position record of this door opened?
CMP DoorXPos,Y		  ;
BNE NextDoor2		   ;If not, branch to check next item in door opened array.

		BEQ SetBrickID		  ;($AD5C)This door has already been opened. Return brick block ID.

NextDoor1:
		INY					 ;($AD5E)Move to next door position.

NextDoor2:
		INY					 ;($AD5F)Move to next door position.

CPY #$10				;Max 8 doors per map. Have all doors been checked?
		BNE ChkDoorLoop		 ;($AD62)If not, branch to check if another has been opened already.
		BEQ ReturnBlockID	   ;($AD64)Else exit.

;----------------------------------------------------------------------------------------------------

ModMapBlock:
		LDA NTBlockY			;($AD66)*2. Convert the block position to tile position.
ASL					 ;
		CLC					 ;($AD69)Calculate the nametable Y block that needs to be replaced.
ADC YPosFromCenter	  ;Add signed location of block to unsigned nametable location.
CLC					 ;
		ADC #$1E				;($AD6D)Add Screen height in tiles to ensure result is always positive.
		STA DivideNumber1LB	 ;($AD6F)

LDA #$1E				;Divide out tile height and get remainder. Result will be
		STA DivideNumber2	   ;($AD73)between #$00-#$1E(height of screen in tiles).
		JSR ByteDivide		  ;($AD75)($C1F0)Divide a 16-bit number by an 8-bit number.

LDA DivideRemainder		;The final result is the unsigned Y position of the block
STA YPosFromTop		 ;to replace, measured in tiles. #$00-#$1E.
		STA YFromTopTemp		;($AD7C)

		LDA NTBlockX			;($AD7E)*2. Convert the block position to tile position.
ASL					 ;Calculate the nametable X block that needs to be replaced.
CLC					 ;Add signed location of block to unsigned nametable location.
ADC XPosFromCenter	  ;Keep only lower 6 bits. The row is 64 tiles wide as it spans
		AND #$3F				;($AD84)both nametables. The final result is the unsigned X position
		STA XPosFromLeft		;($AD86)of the block to replace, measured in tiles. #$00-#$3F. No
STA XFromLeftTemp	   ;division necessary. value rolls over naturally.

		JSR DoAddressCalculation;($AD8A)($C5AA)Calculate destination address for GFX data.

LDA XPosFromCenter	  ;
		ASL					 ;($AD8F)/2 with sign extension to convert block X location.
LDA XPosFromCenter	  ;
ROR					 ;

		CLC					 ;($AD93)
ADC CharXPos			;Add the player's X position in preparation to get block type.
STA XTarget			 ;

LDA YPosFromCenter	  ;
ASL					 ;/2 with sign extension to convert to block Y location.
		LDA YPosFromCenter	  ;($AD9B)
		ROR					 ;($AD9D)

CLC					 ;
		ADC CharYPos			;($AD9F)Add the player's Y position in preparation to get block type.
		STA YTarget			 ;($ADA1)

		JSR GetBlockID		  ;($ADA3)($AC17)Get description of block.

		LDA MapType			 ;($ADA6)Is the player in a dungeon?
		CMP #MAP_DUNGEON		;($ADA8)
BNE ChkCoveredArea2	 ;If not, branch.

LDA XPosFromCenter	  ;Is X position a positive value?
BPL +				   ;If so, branch.

EOR #$FF				;
		CLC					 ;($ADB2)
ADC #$01				;2s compliment. Convert X position to a positive number.
STA GenByte3E		   ;
		JMP ChkLightDiameterX2  ;($ADB7)

		* LDA XPosFromCenter	;($ADBA)Store the unsigned tile X position.
STA GenByte3E		   ;

ChkLightDiameterX2:
		LDA LightDiameter	   ;($ADBE)Is target block outside the visible area in a dungeon?
CMP GenByte3E		   ;
BCS ChkLightXEdge2	  ;If not, branch.

LDA #BLK_BLANK		  ;Target block is outside visible area.
STA TargetResults	   ;Load a blank block.

LDA #$00				;Remove no tiles from the current block.
STA BlkRemoveFlgs	   ;
BEQ CalcBlockIndex2	 ;Branch always.

ChkLightXEdge2:
BNE ChkLightY2		  ;Branch if block is not at the very edge of the lighted area.

LDA XPosFromCenter	  ;Is block on the right edge of lighted area?
		BPL LightXRight2		;($ADD2)If so, branch.

		LDA #$05				;($ADD4)Black out left side of block.
		STA BlkRemoveFlgs	   ;($ADD6)Block is on the left edge of lighted area.
		BNE ChkLightY2		  ;($ADD8)Branch always.

LightXRight2:
		LDA #$0A				;($ADDA)Black out right side of block.
STA BlkRemoveFlgs	   ;Block is on the right edge of lighted area.

ChkLightY2:
		LDA YPosFromCenter	  ;($ADDE)Is Y position a positive value?
BPL LightYBottom2	   ;If so, branch.

EOR #$FF				;
		CLC					 ;($ADE4)
		ADC #$01				;($ADE5)2s compliment. Convert Y position to a positive number.
		STA GenByte3E		   ;($ADE7)
		JMP ChkLightDiameterY2  ;($ADE9)

LightYBottom2:
LDA YPosFromCenter	  ;Store the unsigned tile Y position.
		STA GenByte3E		   ;($ADEE)

ChkLightDiameterY2:
LDA LightDiameter	   ;Is target block outside the visible area in a dungeon?
CMP GenByte3E		   ;
		BCS ChkLightYEdge2	  ;($ADF4)If not, branch.

		LDA #BLK_BLANK		  ;($ADF6)Target block is outside visible area.
		STA TargetResults	   ;($ADF8)Load a blank block.

LDA #$00				;Remove no tiles from the current block.
STA BlkRemoveFlgs	   ;
		BEQ CalcBlockIndex2	 ;($ADFE)Branch always.

ChkLightYEdge2:
		BNE CalcBlockIndex2	 ;($AE00)Branch if block is not at the very edge of the lighted area.

LDA YPosFromCenter	  ;Is block on the bottom edge of lighted area?
		BPL +				   ;($AE04)If so, branch.

		LDA #$03				;($AE06)Black out upper half of block.
STA BlkRemoveFlgs	   ;Block is on the upper edge of lighted area.
		BNE CalcBlockIndex2	 ;($AE0A)Branch always.

		* LDA #$0C			  ;($AE0C)Black out lower half of block.
STA BlkRemoveFlgs	   ;Block is on the lower edge of lighted area.
		BNE CalcBlockIndex2	 ;($AE10)Branch always.

ChkCoveredArea2:
		JSR HasCoverData		;($AE12)($AAE1)Check if current map has covered areas.
		LDA CoverStatusus	   ;($AE15)
		EOR CoveredStsNext	  ;($AE17)Did player just enter/exit covered area?
AND #$08				;
BEQ CalcBlockIndex2	 ;If not, branch.

		LDA CoverStatusus	   ;($AE1D)Did player just enter cover?
		BNE ModUnderCover	   ;($AE1F)If so branch to load blank tiles.

		LDA #BLK_SML_TILES	  ;($AE21)Player just left covered area.
STA GenByte3C		   ;Prepare to hide covered areas with small tiles.
		BNE CalcBlockIndex2	 ;($AE25)Branch always.

ModUnderCover:
LDA #BLK_BLANK		  ;Player just entered covered area.
STA GenByte3C		   ;Prepeare to hide outside with blank tiles.

CalcBlockIndex2:
LDA TargetResults	   ;
		ASL					 ;($AE2D)*5. Data for the graphic block is 5 bytes.
ASL					 ;
		ADC TargetResults	   ;($AE2F)

CalcBlockI_AddPtrLo:  ADC GFXTilesPtr		 ;
STA BlockDataPtrLB	  ;
LDA GFXTilesPtr+1	   ;Calculate the address to the proper GFX block data row.
ADC #$00				;
STA BlockDataPtrUB	  ;

		LDY #$00				;($AE3D)Initialize index for transferring GFX block data.

		LDA (BlockDataPtr),Y	;($AE3F)Store the Upper left tile data of block in buffer.
STA PPUDataByte		 ;
JSR AddPPUBufferEntry	  ;($C690)Add data to PPU buffer.

		LDA BlkRemoveFlgs	   ;($AE46)Is the flag set for removing the upper left tile of block?
LSR					 ;
		BCC DoUpperRightTile	;($AE49)If not, branch.

		LDA MapType			 ;($AE4B)Is player in a dungeon?
		CMP #MAP_DUNGEON		;($AE4D)
BNE RmvNonDngnTileUL	;If not, branch.

LDX PPUBufCount		 ;Load a blank tile in the upper left corner of block.
DEX					 ;
		LDA #TL_BLANK_TILE1	 ;($AE54)
		STA BlockRAM,X		  ;($AE56)
BNE DoUpperRightTile	;Branch always.

RmvNonDngnTileUL:
DEC PPUBufCount		 ;
DEC PPUBufCount		 ;Each tile is 3 bytes. Remove those 3 bytes.
DEC PPUBufCount		 ;

DEC PPUEntryCount		 ;Remove a tile entry from the counter.

DoUpperRightTile:
INY					 ;Store the Upper right tile data of block in buffer.
		LDA (BlockDataPtr),Y	;($AE64)
		STA PPUDataByte		 ;($AE66)
		JSR AddPPUBufferEntry   ;($AE68)($C690)Add data to PPU buffer.

LDA BlkRemoveFlgs	   ;Is the flag set for removing the upper right tile of block?
AND #BLK_UPPER_RIGHT	;
		BEQ DoLowerLeftTile	 ;($AE6F)If not, branch.

LDA MapType			 ;Is player in a dungeon?
		CMP #MAP_DUNGEON		;($AE73)
		BNE RmvNonDngnTileUR	;($AE75)If not, branch.

LDX PPUBufCount		 ;Load a blank tile in the upper right corner of block.
DEX					 ;
		LDA #TL_BLANK_TILE1	 ;($AE7A)
STA BlockRAM,X		  ;
BNE DoLowerLeftTile	 ;Branch always.

RmvNonDngnTileUR:
DEC PPUBufCount		 ;
		DEC PPUBufCount		 ;($AE83)Each tile is 3 bytes. Remove those 3 bytes.
DEC PPUBufCount		 ;

DEC PPUEntryCount		 ;Remove a tile entry from the counter.

DoLowerLeftTile:
		INY					 ;($AE89)
LDA PPUAddrLB		   ;
CLC					 ;
		ADC #$1E				;($AE8D)Move to next tile row in the PPU nametable.
STA PPUAddrLB		   ;
BCC +				   ;
		INC PPUAddrUB		   ;($AE93)

* LDA (BlockDataPtr),Y	;Store the lower left tile data of block in buffer.
STA PPUDataByte		 ;
		JSR AddPPUBufferEntry   ;($AE99)($C690)Add data to PPU buffer.

		LDA BlkRemoveFlgs	   ;($AE9C)Is the flag set for removing the lower left tile of block?
AND #BLK_LOWER_LEFT	 ;
		BEQ DoLowerRightTile	;($AEA0)If not, branch.

		LDA MapType			 ;($AEA2)Is player in a dungeon?
CMP #MAP_DUNGEON		;
		BNE RmvNonDngnTileLL	;($AEA6)If not, branch.

		LDX PPUBufCount		 ;($AEA8)Load a blank tile in the lower left corner of block.
DEX					 ;
		LDA #TL_BLANK_TILE1	 ;($AEAB)
		STA BlockRAM,X		  ;($AEAD)
		BNE DoLowerRightTile	;($AEB0)Branch always.

RmvNonDngnTileLL:
DEC PPUBufCount		 ;
		DEC PPUBufCount		 ;($AEB4)Each tile is 3 bytes. Remove those 3 bytes.
		DEC PPUBufCount		 ;($AEB6)

DEC PPUEntryCount		 ;Remove a tile entry from the counter.

DoLowerRightTile:
INY					 ;Store the lower right tile data of block in buffer.
		LDA (BlockDataPtr),Y	;($AEBB)
		STA PPUDataByte		 ;($AEBD)
		JSR AddPPUBufferEntry   ;($AEBF)($C690)Add data to PPU buffer.

LDA BlkRemoveFlgs	   ;Is the flag set for removing the lower right tile of block?
AND #BLK_LOWER_RIGHT	;
		BEQ DoAttribByte		;($AEC6)If not, branch.

LDA MapType			 ;Is player in a dungeon?
		CMP #MAP_DUNGEON		;($AECA)
BNE RmvNonDngnTileLR	;If not, branch.

		LDX PPUBufCount		 ;($AECE)Load a blank tile in the lower right corner of block.
		DEX					 ;($AED0)
		LDA #TL_BLANK_TILE1	 ;($AED1)
		STA BlockRAM,X		  ;($AED3)
		BNE DoAttribByte		;($AED6)Branch always.

RmvNonDngnTileLR:
DEC PPUBufCount		 ;
		DEC PPUBufCount		 ;($AEDA)Each tile is 3 bytes. Remove those 3 bytes.
DEC PPUBufCount		 ;

		DEC PPUEntryCount	   ;($AEDE)Remove a tile entry from the counter.

DoAttribByte:
INY					 ;Increment to attribute table byte.

LDA XFromLeftTemp	   ;
		STA XPosFromLeft		;($AEE3)Update X and Y position for next block.
		LDA YFromTopTemp		;($AEE5)
STA YPosFromTop		 ;

LDA (BlockDataPtr),Y	;Get attribute table byte.
		STA PPUDataByte		 ;($AEEB)

		JSR ModAttribBits	   ;($AEED)($C006)Set the attribute table bits for a nametable block.

		LDA PPUHorizontalVertical;($AEF0)Is PPU set up to write in rows?
		BNE ModBlockExit		;($AEF2)If so, branch to exit.

		LDA PPUAddrUB		   ;($AEF4)
		CLC					 ;($AEF6)Add in upper nibble of upper address byte.
		ADC #$20				;($AEF7)
STA PPUAddrUB		   ;
		JSR AddPPUBufferEntry   ;($AEFB)($C690)Add data to PPU buffer.

ModBlockExit:
RTS					 ;Done modifying graphics block. Return.

;----------------------------------------------------------------------------------------------------

GetBlockNoTrans:
		LDA CharXPos			;($AEFF)
		STA XTarget			 ;($AF01)Get block ID player is currently standing on.
		LDA CharYPos			;($AF03)
		STA YTarget			 ;($AF05)

		JSR GetBlockID		  ;($AF07)($AC17)Get description of block.

JSR HasCoverData		;($AAE1)Check if current map has covered areas.
LDA CoveredStsNext	  ;
		STA CoverStatusus	   ;($AF0F)Set variables to indicate no transition in/out of covered area.
		RTS					 ;($AF11)

;----------------------------------------------------------------------------------------------------

InitMapData:
		LDA MapNumber		   ;($AF12)Did player enter a dungeon?
CMP #MAP_DLCSTL_SL1	 ;
BCS ChkThRoomMap		;If not, branch.

		LDA #$01				;($AF18)
		STA LightDiameter	   ;($AF1A)Player entered a dungeon. Minimize light diameter
LSR					 ;and clear the radiant timer.
		STA RadiantTimer		;($AF1D)

ChkThRoomMap:
LDA MapNumber		   ;Is player in the throne room?
CMP #MAP_THRONEROOM	 ;
BEQ ChkOverworldMap	 ;If so, branch.

		LDA PlayerFlags		 ;($AF25)
		ORA #F_LEFT_THROOM	  ;($AF27)Set flag indicating player has left throne room.
		STA PlayerFlags		 ;($AF29)

ChkOverworldMap:
		LDA MapNumber		   ;($AF2B)Is player on the overworld map?
CMP #MAP_OVERWORLD	  ;
		BNE ChkLeftThRoom	   ;($AF2F)If not, branch.

LDX #$00				;Prepare to clear open door history.
TXA					 ;

ClrOpenDoorsLoop:
		STA DoorXPos,X		  ;($AF34)Reset the history of opened doors.
		INX					 ;($AF37)
CPX #$20				;Has the opened doors history been completely cleared?
BNE ClrOpenDoorsLoop	;If not, branch to clear another byte.

ChkLeftThRoom:
LDA PlayerFlags		 ;Has player left the throne room?
		AND #F_LEFT_THROOM	  ;($AF3E)
BEQ SetNTAndScroll	  ;If not, branch. Keep treasures and door in place.

LDA MapNumber		   ;Is player in the throne room?
		CMP #MAP_THRONEROOM	 ;($AF44)
BNE SetNTAndScroll	  ;If not, branch.

LDA #$04				;
		STA TrsrXPos+14		 ;($AF4A)
		STA TrsrYPos+14		 ;($AF4D)
		STA TrsrYPos+12		 ;($AF50)
STA DoorXPos+14		 ;
LDA #$05				;Remove the 3 treasures and door from the throne room.
STA TrsrXPos+12		 ;
LDA #$06				;
		STA TrsrXPos+10		 ;($AF5D)
		LDA #$01				;($AF60)
		STA TrsrYPos+10		 ;($AF62)
LDA #$07				;
		STA DoorYPos+14		 ;($AF67)

SetNTAndScroll:
		LDA #$08				;($AF6A)
STA NTBlockX			;Set nametable block position at 8,7.
LDA #$07				;
STA NTBlockY			;

LDA #$00				;
STA ScrollX			 ;Reset the scroll registers.
STA ScrollY			 ;

STA ActiveNmTbl		 ;Set active nametable as nametable 0.

LDA MapNumber		   ;
ASL					 ;
		ASL					 ;($AF7D)*5. Map data is 5 bytes per map.
ADC MapNumber		   ;
TAY					 ;

		LDA MapDatTbl,Y		 ;($AF81)
STA MapDatPtrLB		 ;
INY					 ;Get the pointer to the map layout data.
		LDA MapDatTbl,Y		 ;($AF87)
STA MapDatPtrUB		 ;

INY					 ;
		LDA MapDatTbl,Y		 ;($AF8D)Get the map width.
STA MapWidth			;

INY					 ;
		LDA MapDatTbl,Y		 ;($AF93)Get the map height.
STA MapHeight		   ;

INY					 ;
		LDA MapDatTbl,Y		 ;($AF99)Get the block used for out of bounds graphic.
STA BoundryBlock		;

LDA #$FF				;Assume no NPCs on the map.
STA NPCUpdateCounter	   ;

LDA StoryFlags		  ;Is the dragonlord dead?
AND #F_DGNLRD_DEAD	  ;
BEQ ChkMapDungeon	   ;If not, branch.

LDA MapNumber		   ;Is player on the ground floor of Tantagel castle?
CMP #MAP_TANTCSTL_GF	;
BNE ChkMapDungeon	   ;If not, branch.

LDA #$0B				;Special NPC data pointer index for Tantagel castle
BNE GetNPCDataPointer   ;ground floor after end boss defeated. Branch always.

ChkMapDungeon:
LDA MapNumber		   ;First 3 maps don't have NPCs
SEC					 ;
SBC #MAP_TANTCSTL_GF	;Tantagel castle ground floor is first map with NPCs.

CMP #MAP_RAINBOW-3	  ;Does the current map have NPCs?
BCS ChkGwaelinNPC	   ;If not, branch.

GetNPCDataPointer:
ASL					 ;*2. Pointer to NPC data is 2 bytes.
		TAY					 ;($AFBC)

LDA #$00				;Reset NPC update counter.
STA NPCUpdateCounter	   ;

LDA NPCMobPtrTbl,Y	  ;
STA NPCDatPtrLB		 ;Get pointer to NPC data for current map.
LDA NPCMobPtrTbl+1,Y	;
STA NPCDatPtrUB		 ;

LDA #$00				;Prepare to clear all NPC data.
TAX					 ;

NPCClearLoop:
		STA NPCXPos,X		   ;($AFCE)Has all NPC data been cleared?
		INX					 ;($AFD0)
		CPX #$3C				;($AFD1)
BNE NPCClearLoop		;If not, branch to clear another byte.

LDA MapNumber		   ;Is player in the basement of the dragonlord's castle?
		CMP #MAP_DLCSTL_BF	  ;($AFD7)
		BNE PrepMobNPCDatLoad   ;($AFD9)If not, branch.

		LDA StoryFlags		  ;($AFDB)Is dragonlord defeated?
		AND #F_DGNLRD_DEAD	  ;($AFDD)
BNE ChkGwaelinNPC	   ;If so, branch. Skip loading dragonlord NPC.

PrepMobNPCDatLoad:
LDY #$00				;Zero out read and write indexes.
LDX #$00				;

LoadMobNPCDataLoop:
		LDA (NPCDatPtr),Y	   ;($AFE5)Has all the mobile NPC data for this map been loaded?
		CMP #$FF				;($AFE7)
BEQ PrepStatNPCDatLoad  ;If so, branch to exit loop.

STA NPCXPos,X		   ;Get NPC X position and type byte.

		INX					 ;($AFED)Increment to next NPC byte.
INY					 ;

		LDA (NPCDatPtr),Y	   ;($AFEF)Get NPC Y position and facing direction byte.
		STA NPCXPos,X		   ;($AFF1)

INX					 ;Increment to next NPC byte.
INY					 ;

		LDA #$00				;($AFF5)Set NPC mid-block position to 0 (Center NPC on block).
STA NPCXPos,X		   ;

INX					 ;Increment to next NPC byte.
INY					 ;

		JMP LoadMobNPCDataLoop  ;($AFFB)($AFE5)Loop to load mobile NPC data for this map.

PrepStatNPCDatLoad:
INY					 ;Static NPC data table follows NPC modile data table.
		LDX #$1E				;($AFFF)Set pointer to beginning of static NPC data buffer.

LoadStatNPCDataLoop:
LDA (NPCDatPtr),Y	   ;Has all the static NPC data for this map been loaded?
		CMP #$FF				;($B003)
BEQ ChkGwaelinNPC	   ;If so, branch to exit loop.

STA NPCXPos,X		   ;Get NPC X position and type byte.

		INX					 ;($B009)Increment to next NPC byte.
		INY					 ;($B00A)

		LDA (NPCDatPtr),Y	   ;($B00B)Get NPC Y position and facing direction byte.
		STA NPCXPos,X		   ;($B00D)

INX					 ;Increment to next NPC byte.
		INY					 ;($B010)

		LDA #$00				;($B011)Set NPC mid-block position to 0 (Center NPC on block).
		STA NPCXPos,X		   ;($B013)

INX					 ;Increment to next NPC byte.
INY					 ;

JMP LoadStatNPCDataLoop ;($B001)Loop to load static NPC data for this map.

ChkGwaelinNPC:
		LDA MapNumber		   ;($B01A)Is player in the throne room?
		CMP #MAP_THRONEROOM	 ;($B01C)
BNE ChkCoveredData	  ;If not, branch.

LDA PlayerFlags		 ;Has player rescued Princess Gwaelin?
		AND #F_RTN_GWAELIN	  ;($B022)
		BNE ChkCoveredData	  ;($B024)If so, branch.

LDA #$00				;
STA NPCXPos+$27		 ;Gwaelin has not been saved. Remove her from the NPCs.
		STA NPCYPos+$27		 ;($B02A)
		STA NPCMidPos+$27	   ;($B02C)

ChkCoveredData:
LDA MapNumber		   ;Is player in a dungeon?
CMP #MAP_DLCSTL_SL1	 ;
BCC ChkWorldMap		 ;If not, branch.

LDA #MAP_DUNGEON		;Indicate player is in a dungeon.
		STA MapType			 ;($B036)

NoCoveredData:
		LDA #$00				;($B038)
		STA CoverDatLB		  ;($B03A)There is no covered area data for this map.
STA CoverDatUB		  ;
RTS					 ;

ChkWorldMap:
LDA MapNumber		   ;Is player on the overworl map?
		CMP #MAP_OVERWORLD	  ;($B041)
		BNE TownMap			 ;($B043)If not, branch.

		LDA #MAP_OVRWLD		 ;($B045)Indicate the player is on the overworld map.
STA MapType			 ;
BEQ NoCoveredData	   ;Branch always.

TownMap:
LDA #MAP_TOWN		   ;Indicate player is in a town.
STA MapType			 ;

LDA MapNumber		   ;Is the player in Brecconary?
CMP #MAP_BRECCONARY	 ;
BNE ChkMapGarinham	  ;If not, branch to check another map.

LDA BrecCvrdDatPtr	  ;
STA CoverDatLB		  ;
LDA BrecCvrdDatPtr+1	;Load covered area data pointer for Brecconary.
		STA CoverDatUB		  ;($B05D)
		RTS					 ;($B05F)

ChkMapGarinham:
		CMP #MAP_GARINHAM	   ;($B060)Is the player in Garinham?
BNE ChkMapCantlin	   ;If not, branch to check another map.

LDA GarinCvrdDatPtr	 ;
		STA CoverDatLB		  ;($B067)
LDA GarinCvrdDatPtr+1   ;Load covered area data pointer for Garin.
		STA CoverDatUB		  ;($B06C)
RTS					 ;

ChkMapCantlin:
CMP #MAP_CANTLIN		;Is the player in Cantlin?
		BNE ChkMapRimuldar	  ;($B071)If not, branch to check another map.

		LDA CantCvrdDatPtr	  ;($B073)
STA CoverDatLB		  ;
		LDA CantCvrdDatPtr+1	;($B078)Load covered area data pointer for Cantlin.
STA CoverDatUB		  ;
		RTS					 ;($B07D)

ChkMapRimuldar:
CMP #MAP_RIMULDAR	   ;Is the player in Rimuldar?
		BNE NoCoveredData	   ;($B080)If not, branch. No covered area data for this map.

LDA RimCvrdDatPtr	   ;
		STA CoverDatLB		  ;($B085)
LDA RimCvrdDatPtr+1	 ;Load covered area data pointer for Rimuldar.
		STA CoverDatUB		  ;($B08A)
		RTS					 ;($B08C)

;----------------------------------------------------------------------------------------------------

MapChngFadeNoSound:
		LDA #$00				;($B08D)Indicate no stairs SFX should play on map change.
BEQ SetSoundAndFade	 ;Branch always to fade out screen.

MapChngNoSound:
		LDA #$00				;($B091)Indicate no stairs SFX should play on map change.
		STA GenByte25		   ;($B093)
BEQ ClearSprites		;Branch always and skip fade out.

MapChngWithSound:
LDA #$01				;Indicate stairs SFX should play on map change.

SetSoundAndFade:
STA GenByte25		   ;Store stair SFX flag.
JSR ScreenFadeOut	   ;($A743)Fade out screen.

ClearSprites:
JSR ClearSpriteRAM	  ;($C6BB)Clear sprite RAM.

		LDA #%00000000		  ;($B0A1)Turn off the display.
STA PPUControl1		 ;
		STA DrgnLrdPal		  ;($B0A6)Clear dragonlord palette register.

		JSR Bank1ToCHR0		 ;($B0A9)($FC98)Load CHR bank 1 into CHR0 memory.
		JSR Bank2ToCHR1		 ;($B0AC)($FCAD)Load CHR bank 2 into CHR1 memory.

		LDA GenByte25		   ;($B0AF)Shoud stair SFX be played on map change?
BEQ +				   ;If not, branch.

		LDA #SFX_STAIRS		 ;($B0B3)Stairs SFX.
BRK					 ;
		.byte $04, $17		  ;($B0B6)($81A0)InitMusicSFX, bank 1.

		* LDA #%00011000		;($B0B8)Enable sprites and background.
STA PPUControl1		 ;

JSR InitMapData		 ;($AF12)Initialize map data.
JSR GetBlockNoTrans	 ;($AEFF)Get block player is on and set no covered transition.

		LDA #$F2				;($B0C3)Start changing blocks to current map -14 tiles above center.
		STA YPosFromCenter	  ;($B0C5)

ChngMapRowLoop:
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

LDA #$EE				;Start changing blocks to current map -18 tiles left of center.
STA XPosFromCenter	  ;

ChngMapLeftLoop:
LDA #$00				;
STA BlkRemoveFlgs	   ;Remove no tiles from the current block.
STA PPUHorizontalVertical		 ;PPU column write.

JSR ModMapBlock		 ;($AD66)Change block on map.

INC XPosFromCenter	  ;Move to next block in row.
INC XPosFromCenter	  ;

BNE ChngMapLeftLoop	 ;Is left half of row changed? If not, branch to do another block.

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

ChngMapRightLoop:
LDA #$00				;
STA BlkRemoveFlgs	   ;Remove no tiles from the current block.
STA PPUHorizontalVertical		 ;PPU column write.

JSR ModMapBlock		 ;($AD66)Change block on map.

INC XPosFromCenter	  ;Move to next block in row.
INC XPosFromCenter	  ;

LDA XPosFromCenter	  ;Is right half of row changed?
CMP #$12				;
BNE ChngMapRightLoop	;If not, branch to do another block.

INC YPosFromCenter	  ;Move to the next row.
		INC YPosFromCenter	  ;($B0F5)

LDA YPosFromCenter	  ;Have all the rows for this view of the map been changed?
		CMP #$10				;($B0F9)
BNE ChngMapRowLoop	  ;If not, branch to do another row.

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

LDA #NPC_STOP		   ;Stop the NPCs from moving.
STA StopNPCMove		 ;
		JSR DoSprites		   ;($B104)($B6DA)Update player and NPC sprites.

LDA #NPC_MOVE		   ;Allow the NPCs to move again.
		STA StopNPCMove		 ;($B109)
		JSR WaitForNMI		  ;($B10B)($FF74)Wait for VBlank interrupt.

LDX MapNumber		   ;Get current map number.
LDA ResumeMusicTbl,X	;Use current map number to resume music.

		BRK					 ;($B113)
		.byte $04, $17		  ;($B114)($81A0)InitMusicSFX, bank 1.

		LDA RegSPPalPtr		 ;($B116)
		STA SpritePalettePointerLB;($B119)Set pointer for sprite palettes.
		LDA RegSPPalPtr+1	   ;($B11B)
STA SpritePalettePointerUB		;

		LDA #$FF				;($B120)Indicate player has not just moved in//out of cover.
STA CoveredStsNext	  ;

		LDA OverworldPalPtr	 ;($B124)
		CLC					 ;($B127)
		ADC MapType			 ;($B128)
		STA BackgroundPalettePointerLB;($B12A)Get proper background palette for current map type.
		LDA OverworldPalPtr+1   ;($B12C)
		ADC #$00				;($B12F)
		STA BackgroundPalettePointerUB;($B131)

		JSR PalFadeIn		   ;($B133)($C529)Fade in both background and sprite palettes.

		LDA #$02				;($B136)Prepare to erase the background blocks of nametable 1.
		STA PPUAddrLB		   ;($B138)
		LDA #$24				;($B13A)
		STA PPUAddrUB		   ;($B13C)The starting address is $2402 on nametable 1.

LDA #TL_BLANK_TILE1	 ;Load a blank block as the replacement tile.
		STA PPUDataByte		 ;($B140)

LDA #$0F				;Prepare to clear 15 rows of blocks.
		STA RowCounter		  ;($B144)

NTClearLoop:
		JSR WaitForNMI		  ;($B146)($FF74)Wait for VBlank interrupt.

		LDY PPUBufCount		 ;($B149)Get current index into block RAM buffer.

		LDA #$80				;($B14B)Indicate background tiles need to be updated.
		STA UpdateBGTiles	   ;($B14D)

		LDA PPUAddrUB		   ;($B150)Set PPU control byte. Tell PPU to do row writes.
ORA #$80				;That means increment address by 1 after every
		STA BlockRAM,Y		  ;($B154)tile write. This byte also stores PPU address upper byte.

		LDA #$1C				;($B157)Prepare to clear 27 tiles in the current nametable row.
		TAX					 ;($B159)

		STA BlockRAM+1,Y		;($B15A)Store counter byte in buffer.

		LDA PPUAddrLB		   ;($B15D)Store PPU address lower byte.
		STA BlockRAM+2,Y		;($B15F)

		LDA PPUDataByte		 ;($B162)Get pattern table index byte(blank tile).

		* STA BlockRAM+3,Y	  ;($B164)
		INY					 ;($B167)Save blank tile to PPU buffer.
		DEX					 ;($B168)
		BNE -				   ;($B169)More blank tiles to store? if so, branch to store another one.

		INC PPUEntryCount	   ;($B16B)Increment PPU buffer entry count.

		LDA PPUAddrLB		   ;($B16D)
		CLC					 ;($B16F)
		ADC #$20				;($B170)Move to next row in nametable.
		STA PPUAddrLB		   ;($B172)
		BCC +				   ;($B174)
		INC PPUAddrUB		   ;($B176)

		* LDA PPUAddrUB		 ;($B178)Set PPU control byte. Tell PPU to do row writes.
		ORA #$80				;($B17A)That means increment address by 1 after every
		STA BlockRAM+3,Y		;($B17C)tile write. This byte also stores PPU address upper byte.

		LDA #$1C				;($B17F)Prepare to clear 27 tiles in the current nametable row.
		TAX					 ;($B181)

		STA BlockRAM+4,Y		;($B182)Store counter byte in buffer.

		LDA PPUAddrLB		   ;($B185)Store PPU address lower byte.
		STA BlockRAM+5,Y		;($B187)

		LDA PPUDataByte		 ;($B18A)Get pattern table index byte(blank tile).

		* STA BlockRAM+6,Y	  ;($B18C)
		INY					 ;($B18F)Save blank tile to PPU buffer.
DEX					 ;
BNE -				   ;More blank tiles to store? if so, branch to store another one.

		INC PPUEntryCount	   ;($B193)Increment PPU buffer entry count.

TYA					 ;This should not be necessary as the buffer gets emptied
CLC					 ;out every vblank. It moves ahead 2 entries for all PPU
ADC #$06				;data that does not have control bits set.
STA PPUBufCount		 ;

LDA PPUAddrLB		   ;
		CLC					 ;($B19D)
ADC #$20				;Move to next row in nametable.
		STA PPUAddrLB		   ;($B1A0)
		BCC +				   ;($B1A2)
		INC PPUAddrUB		   ;($B1A4)

		* DEC RowCounter		;($B1A6)Have all 15 rows of blocks been cleared?
		BNE NTClearLoop		 ;($B1A8)If not, branch to clear another row of blocks.

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt. This loads last row of
		RTS					 ;($B1AD)blocks onto the screen.

;----------------------------------------------------------------------------------------------------

;The following table is used to pick what music to resume after an event occurs.  The index in
;the table represents the map number and the value in the table is the music number to resume.

ResumeMusicTbl:
.byte MSC_NOSOUND	   ;Unused.							  Silence music.
		.byte MSC_OUTDOOR	   ;($B1AF)overworld.						   Resume overworld music.
		.byte MSC_DUNGEON1	  ;($B1B0)dragonlord castle, ground floor map. Resume dungeon 1 music.
		.byte MSC_DUNGEON4	  ;($B1B1)Hauksness.						   Resume dungeon 4 music.
		.byte MSC_TANTAGEL2	 ;($B1B2)Tantagel castle, ground floor.	   Resume tantagel 2 music.
		.byte MSC_THRN_ROOM	 ;($B1B3)Tantagel castle, throne room.		Resume tantagel 1 music.
		.byte MSC_DUNGEON8	  ;($B1B4)Dragonlord castle, bottom floor.	 Resume dungeon 8 music.
		.byte MSC_VILLAGE	   ;($B1B5)Kol.								 Resume village music.
		.byte MSC_VILLAGE	   ;($B1B6)Brecconary.						  Resume village music.
		.byte MSC_VILLAGE	   ;($B1B7)Garinham.							Resume village music.
.byte MSC_VILLAGE	   ;Cantlin.							 Resume village music.
.byte MSC_VILLAGE	   ;Rimuldar.							Resume village music.
.byte MSC_TANTAGEL2	 ;Tantagel castle, sublevel.		   Resume tantagel 2 music.
		.byte MSC_TANTAGEL2	 ;($B1BB)Staff of rain cave.				  Resume tantagel 2 music.
		.byte MSC_TANTAGEL2	 ;($B1BC)Rainbow drop cave.				   Resume tantagel 2 music.
		.byte MSC_DUNGEON2	  ;($B1BD)Dragonlord castle, sublevel 1.	   Resume dungeon 2 music.
.byte MSC_DUNGEON3	  ;Dragonlord castle, sublevel 2.	   Resume dungeon 3 music.
		.byte MSC_DUNGEON4	  ;($B1BF)Dragonlord castle, sublevel 3.	   Resume dungeon 4 music.
		.byte MSC_DUNGEON5	  ;($B1C0)Dragonlord castle, sublevel 4.	   Resume dungeon 5 music.
		.byte MSC_DUNGEON6	  ;($B1C1)Dragonlord castle, sublevel 5.	   Resume dungeon 6 music.
		.byte MSC_DUNGEON7	  ;($B1C2)Dragonlord castle, sublevel 6.	   Resume dungeon 7 music.
		.byte MSC_DUNGEON1	  ;($B1C3)Swamp cave.						  Resume dungeon 1 music.
		.byte MSC_DUNGEON1	  ;($B1C4)Rock mountain cave, B1.			  Resume dungeon 1 music.
		.byte MSC_DUNGEON2	  ;($B1C5)Rock mountain cave, B2.			  Resume dungeon 2 music.
		.byte MSC_DUNGEON1	  ;($B1C6)Cave of Garinham, B1.				Resume dungeon 1 music.
.byte MSC_DUNGEON2	  ;Cave of Garinham, B2.				Resume dungeon 2 music.
.byte MSC_DUNGEON3	  ;Cave of Garinham, B3.				Resume dungeon 3 music.
.byte MSC_DUNGEON4	  ;Cave of Garinham, B4.				Resume dungeon 4 music.
.byte MSC_DUNGEON1	  ;Erdrick's cave B1.				   Resume dungeon 1 music.
.byte MSC_DUNGEON2	  ;Erdrick's cave B2.				   Resume dungeon 2 music.

;----------------------------------------------------------------------------------------------------

CheckCollision:
		LDA _CharXPos		   ;($B1CC)Get potential new position of character and transfer
STA XTarget			 ;it to thx and y target registers.
LDA _CharYPos		   ;
		STA YTarget			 ;($B1D2)Check to see what kind of block is at the destination.
		JSR GetBlockID		  ;($B1D4)($AC17)Get description of block.

LDA TargetResults	   ;Is target block an obstruction?
CMP #BLK_LRG_TILE	   ;
		BCC CheckNPCCollision   ;($B1DB)If not, branch to check for NPC collisions.

DirectionBlocked:
		LDA CharXPos			;($B1DD)Direction blocked!
STA _CharXPos		   ;
LDA CharYPos			;Undo the potential character movement.
STA _CharYPos		   ;

PLA					 ;
		PLA					 ;($B1E6)Pull the last two return addresses off the stack.
		PLA					 ;($B1E7)Movement aborted.
		PLA					 ;($B1E8)

		LDA #SFX_WALL_BUMP	  ;($B1E9)Wall bump SFX
		BRK					 ;($B1EB)
		.byte $04, $17		  ;($B1EC)($81A0)InitMusicSFX, bank 1.

LDA #$00				;Reset frame counter.
		STA FrameCounter		;($B1F0)
		JMP IdleUpdate		  ;($B1F2)($CB30)Update NPC movement and pop-up window.

CheckNPCCollision:
LDA NPCUpdateCounter	   ;Are there NPCs on the current map?
CMP #$FF				;
BNE InitNPCCheck		;If so, branch to check their locations.
RTS					 ;

InitNPCCheck:
LDX #$00				;Prepare to loop through all the NPC locations.

NPCCheckLoop:
LDA NPCXPos,X		   ;Extract NPC's X position and compare it to character's X position.
AND #$1F				;Are they the same?
		CMP _CharXPos		   ;($B202)
		BNE NextNPC			 ;($B204)If not, branch to check next NPC.

		LDA NPCYPos,X		   ;($B206)Extract NPC's Y position and compare it to character's Y position.
		AND #$1F				;($B208)Are they the same?
CMP _CharYPos		   ;
BNE NextNPC			 ;If not, branch to check next NPC.

JMP DirectionBlocked	;NPC collision!

NextNPC:
INX					 ;
INX					 ;Increment to the next NPC.
		INX					 ;($B213)

		CPX #$3C				;($B214)Have all the NPC locations been checked?
		BNE NPCCheckLoop		;($B216)If not, branch to check the next NPC.
		RTS					 ;($B218)Done checking, return indicating no collisions detected.

;----------------------------------------------------------------------------------------------------

ChkSpecialLoc:
		LDA MapWidth			;($B219)Is player X position beyond map boundaries?
		CMP CharXPos			;($B21B)
		BCC CheckMapExit		;($B21D)If so, branch to change maps.

		LDA MapHeight		   ;($B21F)Is player Y position beyond map boundaries?
		CMP CharYPos			;($B221)
BCC CheckMapExit		;If so, branch to change maps.

		JMP CheckForTriggers	;($B225)($CBF7)Check movement updates.

CheckMapExit:
		LDX #$00				;($B228)Prepare to search for the proper target map.
		LDA MapNumber		   ;($B22A)

		* CMP MapTargetTbl,X	;($B22C)Has the target map been found?
		BEQ NewMapFound		 ;($B22F)If so, branch to change maps.

		INX					 ;($B231)
		INX					 ;($B232)Increment to next target map entry.
		INX					 ;($B233)

CPX #$93				;Have all the map entries been checked?
		BNE -				   ;($B236)If not, branch to check the next map entry.

		RTS					 ;($B238)Error! Did not find the target map. Exit.

NewMapFound:
LDA #DIR_DOWN		   ;Point character down by default.
		JMP ChangeMaps		  ;($B23B)($D9E2)Load a new map.

;----------------------------------------------------------------------------------------------------

ChkRemovePopUp:
LDA WindowBufferRAM+$84	   ;
		CMP #$FF				;($B241)This tile will be blank unless the pop-up window is active.
		BNE DoRemovePopUp	   ;($B243)If it is active, branch to remove it from the screen.
		RTS					 ;($B245)

DoRemovePopUp:
		LDA FrameCounter		;($B246)Save the frame counter on the stack.
PHA					 ;

LDA #WINDOW_POPUP		  ;Remove the pop-up window.
JSR RemoveWindow		;($A7A2)Remove window from screen.

PLA					 ;
STA FrameCounter		;Restore the frame counter on the stack.
		RTS					 ;($B251)

;----------------------------------------------------------------------------------------------------

DoJoyRight:
		JSR ChkRemovePopUp	  ;($B252)($B23E)Check if pop-up window needs to be removed.
		LDA FrameCounter		;($B255)
		AND #$0F				;($B257)
		BEQ RightSynced		 ;($B259)Only move if on the first frame of the frame counter.

		PLA					 ;($B25B)Not on first frame. Remove return address from stack and
		PLA					 ;($B25C)update the idle status instead.
		JMP IdleUpdate		  ;($B25D)($CB30)Update NPC movement and pop-up window.

RightSynced:
INC _CharXPos		   ;Prepare to check for collisions on the right.
JSR CheckCollision	  ;($B1CC)Check if character will run into wall or NPC.

		LDA MapType			 ;($B265)Is player in a dungeon?
		CMP #MAP_DUNGEON		;($B267)
		BNE UpdtRNonDungeon	 ;($B269)If not, branch to update non-dungeon map.

		INC CharXPos			;($B26B)Move player 1 block to the right.
		JSR UpdateHorizontalDungeon;($B26D)($B2D4)Update left/right side of dungeon map.

		LDA CharXPixelsLB	   ;($B270)
CLC					 ;
		ADC #$08				;($B273)Move player 8 pixels to the right.
		STA CharXPixelsLB	   ;($B275)
BCC +				   ;Update upper byte of X position, if necessary.
		INC CharXPixelsUB	   ;($B279)

		* JSR PostMoveUpdate	;($B27B)($B30E)Update nametables after player moves.

LDA CharXPixelsLB	   ;
		CLC					 ;($B280)
		ADC #$08				;($B281)Move player 8 pixels to the right.
		STA CharXPixelsLB	   ;($B283)
		BCC +				   ;($B285)Update upper byte of X position, if necessary.
		INC CharXPixelsUB	   ;($B287)

		* JMP DoSprites		 ;($B289)($B6DA)Update player and NPC sprites.

UpdtRNonDungeon:
		LDA #$12				;($B28C)Prepare to write a nametable column starting 18
STA XPosFromCenter	  ;tiles right(#$12) and -14 tiles up(#$F2) from
		LDA #$F2				;($B290)player's current location.
		STA YPosFromCenter	  ;($B292)

RightColumnLoop:
		JSR WaitForNMI		  ;($B294)($FF74)Wait for VBlank interrupt.

		LDA #$00				;($B297)
STA BlkRemoveFlgs	   ;Remove no tiles from the current block.
		STA PPUHorizontalVertical;($B29B)PPU column write.

		JSR ModMapBlock		 ;($B29D)($AD66)Change block on map.

		INC YPosFromCenter	  ;($B2A0)Move to next block position in the column.
		INC YPosFromCenter	  ;($B2A2)

		INC ScrollX			 ;($B2A4)Update the X scroll register.
		INC CharXPixelsLB	   ;($B2A6)Update player's X pixel position.

JSR DoSprites		   ;($B6DA)Update player and NPC sprites.

LDA YPosFromCenter	  ;Have 16 blocks been written?
CMP #$10				;
BNE RightColumnLoop	 ;If not, branch to write another block to the map.

		JSR WaitForNMI		  ;($B2B1)($FF74)Wait for VBlank interrupt.
		INC ScrollX			 ;($B2B4)Increment scroll register and switch to
		BNE UpdtRNTBlock		;($B2B6)other nametable, if necessary.

		LDA ActiveNmTbl		 ;($B2B8)
		EOR #$01				;($B2BA)Swap to other nametable.
		STA ActiveNmTbl		 ;($B2BC)

UpdtRNTBlock:
INC NTBlockX			;Move pointer for the nametable blocks 1 block
		LDA #$1F				;($B2C0)position to the right.
AND NTBlockX			;Ensure position wraps around, if necessary.
STA NTBlockX			;

INC CharXPos			;
INC CharXPixelsLB	   ;Move player 1 pixel to the right.
		BNE +				   ;($B2CA)
		INC CharXPixelsUB	   ;($B2CC)

* JSR DoSprites		   ;($B6DA)Update player and NPC sprites.
		JMP DoCoveredArea	   ;($B2D1)($B5FA)Handle covered areas of the map, if necessary.

;----------------------------------------------------------------------------------------------------

UpdateHorizontalDungeon:
		LDA NTBlockX			;($B2D4)
		EOR #$10				;($B2D6)Update data on the other nametable.
		AND #$1F				;($B2D8)
STA NTBlockX			;

LDA #$FA				;Prepare to update blocks starting -6 tiles above player.
STA YPosFromCenter	  ;

HorzDgnRowLoop:
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

		LDA #$F9				;($B2E3)Prepare to update blocks starting -7 tiles left of player.
		STA XPosFromCenter	  ;($B2E5)

HorzDgnBlockLoop:
		LDA #$00				;($B2E7)
		STA BlkRemoveFlgs	   ;($B2E9)Remove no tiles from the current block.
		STA PPUHorizontalVertical;($B2EB)PPU column write.

		JSR ModMapBlock		 ;($B2ED)($AD66)Change block on map.

		INC XPosFromCenter	  ;($B2F0)Move to next block in row. Block is 2 tiles wide.
INC XPosFromCenter	  ;

LDA XPosFromCenter	  ;Have all the blocks in the row been changed?
CMP #$09				;
BNE HorzDgnBlockLoop	;If not, branch to do another block.

		INC YPosFromCenter	  ;($B2FA)Move to next row. Row is 2 tiles tall.
		INC YPosFromCenter	  ;($B2FC)

LDA YPosFromCenter	  ;Have all the rows been changed?
		CMP #$08				;($B300)
		BNE HorzDgnRowLoop	  ;($B302)If not, branch to do another row.

		JSR WaitForNMI		  ;($B304)($FF74)Wait for VBlank interrupt.

		LDA ActiveNmTbl		 ;($B307)
EOR #$01				;Swap nametables.
		STA ActiveNmTbl		 ;($B30B)
		RTS					 ;($B30D)

;----------------------------------------------------------------------------------------------------

PostMoveUpdate:
LDA NTBlockX			;
		CLC					 ;($B310)
		ADC #$10				;($B311)Update data on the other nametable.
		AND #$1F				;($B313)
		STA NTBlockX			;($B315)

		LDA #$FA				;($B317)Prepare to update blocks starting -6 tiles above player.
		STA YPosFromCenter	  ;($B319)

JSR DoSprites		   ;($B6DA)Update player and NPC sprites.

TickColLoop:
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

LDA #$FA				;Prepare to update blocks starting -6 tiles left of player.
		STA XPosFromCenter	  ;($B323)

TickBlockLoop:
		LDA #$00				;($B325)
		STA BlkRemoveFlgs	   ;($B327)Remove no tiles from the current block.
		STA PPUHorizontalVertical;($B329)PPU column write.

		JSR ModMapBlock		 ;($B32B)($AD66)Change block on map.

INC XPosFromCenter	  ;Move to next block in row. Block is 2 tiles wide.
		INC XPosFromCenter	  ;($B330)

LDA XPosFromCenter	  ;Have all the blocks in the row been changed?
CMP #$08				;
BNE TickBlockLoop	   ;If not, branch to do another block.

INC YPosFromCenter	  ;Move to next row. Row is 2 tiles tall.
INC YPosFromCenter	  ;

		LDA YPosFromCenter	  ;($B33C)Have all the rows been changed?
CMP #$08				;
		BNE TickColLoop		 ;($B340)If not, branch to do another row.

		LDA ActiveNmTbl		 ;($B342)
		EOR #$01				;($B344)Swap nametables.
		STA ActiveNmTbl		 ;($B346)

		JSR WaitForNMI		  ;($B348)($FF74)Wait for VBlank interrupt.
RTS					 ;

;----------------------------------------------------------------------------------------------------

DoJoyLeft:
JSR ChkRemovePopUp	  ;($B23E)Check if pop-up window needs to be removed.
		LDA FrameCounter		;($B34F)
		AND #$0F				;($B351)
		BEQ LeftSynced		  ;($B353)Only move if on the first frame of the frame counter.

		PLA					 ;($B355)Not on first frame. Remove return address from stack and
		PLA					 ;($B356)update the idle status instead.
		JMP IdleUpdate		  ;($B357)($CB30)Update NPC movement and pop-up window.

LeftSynced:
		DEC _CharXPos		   ;($B35A)Prepare to check for collisions on the left.
JSR CheckCollision	  ;($B1CC)Check if character will run into wall or NPC.

LDA MapType			 ;Is player in a dungeon?
CMP #MAP_DUNGEON		;
BNE UpdtLNonDungeon	 ;If not, branch to update non-dungeon map.

		JSR UpdateHorizontalDungeon;($B365)($B2D4)Update left/right side of dungeon map.
		DEC CharXPos			;($B368)Move player 1 block to the left.

		LDA CharXPixelsLB	   ;($B36A)
SEC					 ;
		SBC #$08				;($B36D)Move player 8 pixels to the left.
		STA CharXPixelsLB	   ;($B36F)
		BCS +				   ;($B371)Update upper byte of X position, if necessary.
DEC CharXPixelsUB	   ;

		* JSR PostMoveUpdate	;($B375)($B30E)Update nametables after player moves.

		LDA CharXPixelsLB	   ;($B378)
		SEC					 ;($B37A)
		SBC #$08				;($B37B)Move player 8 pixels to the left.
		STA CharXPixelsLB	   ;($B37D)
		BCS +				   ;($B37F)Update upper byte of X position, if necessary.
		DEC CharXPixelsUB	   ;($B381)

		* JMP DoSprites		 ;($B383)($B6DA)Update player and NPC sprites.

UpdtLNonDungeon:
LDA #$EC				;Prepare to write a nametable column starting -20
STA XPosFromCenter	  ;tiles left(#$EC) and -14 tiles up(#$F2) from
LDA #$F2				;player's current location.
STA YPosFromCenter	  ;

UpdateLeftLoop:
		JSR WaitForNMI		  ;($B38E)($FF74)Wait for VBlank interrupt.

		LDA #$00				;($B391)
		STA BlkRemoveFlgs	   ;($B393)Remove no tiles from the current block.
		STA PPUHorizontalVertical;($B395)PPU column write.

		JSR ModMapBlock		 ;($B397)($AD66)Change block on map.

		INC YPosFromCenter	  ;($B39A)Move to next block position in the column.
INC YPosFromCenter	  ;

		LDA ScrollX			 ;($B39E)
		SEC					 ;($B3A0)Decrement scroll register and switch to
		SBC #$01				;($B3A1)other nametable, if necessary.
		STA ScrollX			 ;($B3A3)
		BCS UpdtLNTBlock		;($B3A5)

		LDA ActiveNmTbl		 ;($B3A7)
		EOR #$01				;($B3A9)Swap to other nametable.
		STA ActiveNmTbl		 ;($B3AB)

UpdtLNTBlock:
LDA CharXPixelsLB	   ;
		SEC					 ;($B3AF)
		SBC #$01				;($B3B0)Move pointer for the nametable blocks 1 block
		STA CharXPixelsLB	   ;($B3B2)position to the left.
		BCS +				   ;($B3B4)
		DEC CharXPixelsUB	   ;($B3B6)

		* JSR DoSprites		 ;($B3B8)($B6DA)Update player and NPC sprites.

		LDA YPosFromCenter	  ;($B3BB)Have all the rows of blocks been updated?
		CMP #$10				;($B3BD)
BNE UpdateLeftLoop	  ;If not, branch to update another row.

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.
DEC ScrollX			 ;Decrement scroll register.

DEC NTBlockX			;Move pointer for the nametable blocks 1 block
		LDA #$1F				;($B3C8)position to the left.
		AND NTBlockX			;($B3CA)Ensure position wraps around, if necessary.
STA NTBlockX			;

		DEC CharXPos			;($B3CE)Move player 1 pixel to the left.
		DEC CharXPixelsLB	   ;($B3D0)

		JSR DoSprites		   ;($B3D2)($B6DA)Update player and NPC sprites.
		JMP DoCoveredArea	   ;($B3D5)($B5FA)Handle covered areas of the map, if necessary.

;----------------------------------------------------------------------------------------------------

DoJoyDown:
JSR ChkRemovePopUp	  ;($B23E)Check if pop-up window needs to be removed.
LDA FrameCounter		;
AND #$0F				;
BEQ DownSynced		  ;Only move if on the first frame of the frame counter.

		PLA					 ;($B3E1)Not on first frame. Remove return address from stack and
		PLA					 ;($B3E2)update the idle status instead.
		JMP IdleUpdate		  ;($B3E3)($CB30)Update NPC movement and pop-up window.

DownSynced:
		INC _CharYPos		   ;($B3E6)Prepare to check for collisions to the bottom.
		JSR CheckCollision	  ;($B3E8)($B1CC)Check if character will run into wall or NPC.

		LDA MapType			 ;($B3EB)Is player in a dungeon?
		CMP #MAP_DUNGEON		;($B3ED)
		BNE UpdtDNonDungeon	 ;($B3EF)If not, branch to update non-dungeon map.

INC CharYPos			;Move player 1 block down.
JSR UpdtVertDungeon	 ;($B4C9)Update top/bottom side of dungeon map.

LDA CharYPixelsLB	   ;
CLC					 ;
ADC #$08				;Move player 8 pixels down.
		STA CharYPixelsLB	   ;($B3FB)
		BCC +				   ;($B3FD)Update upper byte of Y position, if necessary.
		INC CharYPixelsUB	   ;($B3FF)

		* JSR PostMoveUpdate	;($B401)($B30E)Update nametables after player moves.

		LDA CharYPixelsLB	   ;($B404)
		CLC					 ;($B406)
		ADC #$08				;($B407)Move player 8 pixels down.
		STA CharYPixelsLB	   ;($B409)
BCC +				   ;Update upper byte of Y position, if necessary.
INC CharYPixelsUB	   ;

		* JMP DoSprites		 ;($B40F)($B6DA)Update player and NPC sprites.

UpdtDNonDungeon:
		JSR WaitForNMI		  ;($B412)($FF74)Wait for VBlank interrupt.

		INC ScrollY			 ;($B415)Increment vertical scroll and player Y pixel position.
		INC CharYPixelsLB	   ;($B417)
		JSR DoSprites		   ;($B419)($B6DA)Update player and NPC sprites.

LDA #$10				;Prepare to update blocks starting 16 tiles below the player.
STA YPosFromCenter	  ;
LDA #$EE				;Prepare to update blocks starting -18 tiles left of the player.
STA XPosFromCenter	  ;

RowOuterLoop1:
LDA #$03				;Prepare to remove 3 tiles in the current row.
STA TileCounter		 ;

		JSR WaitForNMI		  ;($B428)($FF74)Wait for VBlank interrupt.

RowInnerLoop1:
		LDA #$0C				;($B42B)Remove bottom half of the current block.
		STA BlkRemoveFlgs	   ;($B42D)
		STA PPUHorizontalVertical;($B42F)PPU row write.
		JSR ModMapBlock		 ;($B431)($AD66)Change block on map.

		INC XPosFromCenter	  ;($B434)Move to the next block in the row.
		INC XPosFromCenter	  ;($B436)

DEC TileCounter		 ;Are there more tile columns to update?
BNE RowInnerLoop1	   ;If so, branch to do another column.

INC ScrollY			 ;Increment vertical scroll and player Y pixel position.
INC CharYPixelsLB	   ;
JSR DoSprites		   ;($B6DA)Update player and NPC sprites.

		LDA XPosFromCenter	  ;($B443)
		CMP #$12				;($B445)Is the current row of blocks done being processed?
		BNE RowOuterLoop1	   ;($B447)If not, branch to do another group of blocks.

		LDA #$10				;($B449)Prepare to update blocks starting 16 tiles below the player.
		STA YPosFromCenter	  ;($B44B)
		LDA #$EC				;($B44D)Prepare to update blocks starting -20 tiles left of the player.
		STA XPosFromCenter	  ;($B44F)

VertAttribLoop1:
LDA #$05				;Prepare to change the attribute table for a given row.
STA TileCounter		 ;
		JSR WaitForNMI		  ;($B455)($FF74)Wait for VBlank interrupt.

AttributeClearLoop1:
		JSR ClearAttribByte	 ;($B458)($C244)Set black palette for 4x4 block area.

		LDA XPosFromCenter	  ;($B45B)
		CLC					 ;($B45D)Move to the next 4x4 block area.
		ADC #$04				;($B45E)
		STA XPosFromCenter	  ;($B460)

		DEC TileCounter		 ;($B462)Done clearing this section?
BNE AttributeClearLoop1	;If not, branch to clear another attrib byte.

INC ScrollY			 ;Increment vertical scroll and player Y pixel position.
INC CharYPixelsLB	   ;
JSR DoSprites		   ;($B6DA)Update player and NPC sprites.

LDA XPosFromCenter	  ;
		CMP #$14				;($B46F)Done clearing this row?
		BNE VertAttribLoop1 ;($B471)If not, branch to clear another section.

		LDA #$10				;($B473)Prepare to update blocks starting 16 tiles below the player.
		STA YPosFromCenter	  ;($B475)
		LDA #$EE				;($B477)Prepare to update blocks starting -18 tiles left of the player.
		STA XPosFromCenter	  ;($B479)

VertRowLoop1:
		LDA #$03				;($B47B)Prepare to change a 3 block section.
		STA TileCounter		 ;($B47D)
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

VertBlockLoop1:
		LDA #$03				;($B482)Remove upper tiles in block.
		STA BlkRemoveFlgs	   ;($B484)
		STA PPUHorizontalVertical;($B486)PPU row write.
		JSR ModMapBlock		 ;($B488)($AD66)Change block on map.

		INC XPosFromCenter	  ;($B48B)Increment to next block in row.
		INC XPosFromCenter	  ;($B48D)

		DEC TileCounter		 ;($B48F)Done changing block section?
BNE VertBlockLoop1	  ;If not, branch to do more.

INC ScrollY			 ;Move player down 1 pixel.
INC CharYPixelsLB	   ;

JSR DoSprites		   ;($B6DA)Update player and NPC sprites.
LDA XPosFromCenter	  ;
CMP #$12				;Done changing block row?
		BNE VertRowLoop1	;($B49E)If not, branch to do more.

		JSR WaitForNMI		  ;($B4A0)($FF74)Wait for VBlank interrupt.

		INC ScrollY			 ;($B4A3)
		LDA ScrollY			 ;($B4A5)Increment vertical scroll register and make sure
		CMP #$F0				;($B4A7)It doesn't go too far.
		BNE +				   ;($B4A9)

LDA #$00				;Loop scrool register back to top.
STA ScrollY			 ;

		* INC NTBlockY		  ;($B4AF)
		LDA NTBlockY			;($B4B1)Increment nametable Y block position and make sure
		CMP #$0F				;($B4B3)It doesn't go too far.
		BNE +				   ;($B4B5)

		LDA #$00				;($B4B7)Loop nametable Y block position back to top.
		STA NTBlockY			;($B4B9)

		* INC CharYPos		  ;($B4BB)
		INC CharYPixelsLB	   ;($B4BD)Move player 1 pixel down.
BNE +				   ;
INC CharYPixelsUB	   ;

		* JSR DoSprites		 ;($B4C3)($B6DA)Update player and NPC sprites.
		JMP DoCoveredArea	   ;($B4C6)($B5FA)Handle covered areas of the map, if necessary.

;----------------------------------------------------------------------------------------------------

UpdtVertDungeon:
		LDA NTBlockX			;($B4C9)
		CLC					 ;($B4CB)
ADC #$10				;Update data on the other nametable.
		AND #$1F				;($B4CE)
		STA NTBlockX			;($B4D0)

LDA #$FA				;Prepare to update blocks starting -6 tiles left of player.
STA XPosFromCenter	  ;

VertDgnRowLoop:
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

LDA #$F9				;Prepare to update blocks starting -7 tiles above player.
STA YPosFromCenter	  ;

VertDgnBlockLoop:
		LDA #$00				;($B4DD)
		STA BlkRemoveFlgs	   ;($B4DF)Remove no tiles from the current block.
		STA PPUHorizontalVertical;($B4E1)PPU column write.

JSR ModMapBlock		 ;($AD66)Change block on map.

		INC YPosFromCenter	  ;($B4E6)Move to next block in column. Block is 2 tiles wide.
		INC YPosFromCenter	  ;($B4E8)

		LDA YPosFromCenter	  ;($B4EA)Have all the rows been changed?
CMP #$09				;
		BNE VertDgnBlockLoop;($B4EE)If not, branch to do another row.

		INC XPosFromCenter	  ;($B4F0)Move to next block in row. Block is 2 tiles wide.
		INC XPosFromCenter	  ;($B4F2)

LDA XPosFromCenter	  ;Have all the columns been changed?
		CMP #$08				;($B4F6)
		BNE VertDgnRowLoop  ;($B4F8)If not, branch to do another column.

		JSR WaitForNMI		  ;($B4FA)($FF74)Wait for VBlank interrupt.

		LDA ActiveNmTbl		 ;($B4FD)
		EOR #$01				;($B4FF)Swap nametables.
STA ActiveNmTbl		 ;
		RTS					 ;($B503)

;----------------------------------------------------------------------------------------------------

DoJoyUp:
		JSR ChkRemovePopUp	  ;($B504)($B23E)Check if pop-up window needs to be removed.
		LDA FrameCounter		;($B507)
		AND #$0F				;($B509)
		BEQ UpSynced			;($B50B)Only move if on the first frame of the frame counter.

PLA					 ;Not on first frame. Remove return address from stack and
PLA					 ;update the idle status instead.
JMP IdleUpdate		  ;($CB30)Update NPC movement and pop-up window.

UpSynced:
DEC _CharYPos		   ;Prepare to check for collisions to the top.
JSR CheckCollision	  ;($B1CC)Check if character will run into wall or NPC.

		LDA MapType			 ;($B517)Is player in a dungeon?
CMP #MAP_DUNGEON		;
		BNE UpdtUNonDungeon	 ;($B51B)If not, branch to update non-dungeon map.

JSR UpdtVertDungeon	 ;($B4C9)Vertically update dungeons.
DEC CharYPos			;Move player 1 block up.

		LDA CharYPixelsLB	   ;($B522)
		SEC					 ;($B524)
		SBC #$08				;($B525)Move player 8 pixels down.
		STA CharYPixelsLB	   ;($B527)
BCS +				   ;Update upper byte of Y position, if necessary.
		DEC CharYPixelsUB	   ;($B52B)

		* JSR PostMoveUpdate	;($B52D)($B30E)Update nametables after player moves.

		LDA CharYPixelsLB	   ;($B530)
SEC					 ;
SBC #$08				;Move player 8 pixels up.
		STA CharYPixelsLB	   ;($B535)
BCS +				   ;Update upper byte of Y position, if necessary.
DEC CharYPixelsUB	   ;

		* JMP DoSprites		 ;($B53B)($B6DA)Update player and NPC sprites.

UpdtUNonDungeon:
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

DEC ScrollY			 ;Decrement vertical scroll.
LDA ScrollY			 ;
		CMP #$FF				;($B545)If the scroll value rolls over, set it
		BNE +				   ;($B547)to the proper maximum value.
		LDA #$EF				;($B549)
		STA ScrollY			 ;($B54B)

		* LDA CharYPixelsLB	 ;($B54D)
		SEC					 ;($B54F)
		SBC #$01				;($B550)Update the player's Y pixel position.
		STA CharYPixelsLB	   ;($B552)
		BCS +				   ;($B554)
		DEC CharYPixelsUB	   ;($B556)

* JSR DoSprites		   ;($B6DA)Update player and NPC sprites.

		LDA #$F0				;($B55B)Prepare to update blocks starting -16 tiles above the player.
		STA YPosFromCenter	  ;($B55D)
		LDA #$EE				;($B55F)Prepare to update blocks starting -18 tiles left of the player.
		STA XPosFromCenter	  ;($B561)

VertRowLoop2:
LDA #$03				;Prepare to change a 3 block section.
STA TileCounter		 ;
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

VertBlockLoop2:
		LDA #$03				;($B56A)Remove upper tiles in block.
		STA BlkRemoveFlgs	   ;($B56C)
		STA PPUHorizontalVertical;($B56E)PPU row write.
		JSR ModMapBlock		 ;($B570)($AD66)Change block on map.

INC XPosFromCenter	  ;Increment to next block in row.
INC XPosFromCenter	  ;

		DEC TileCounter		 ;($B577)Done changing block section?
		BNE VertBlockLoop2  ;($B579)If not, branch to do more.

DEC ScrollY			 ;Decrement vertical scroll register and pixel position.
		DEC CharYPixelsLB	   ;($B57D)
		JSR DoSprites		   ;($B57F)($B6DA)Update player and NPC sprites.

		LDA XPosFromCenter	  ;($B582)
CMP #$12				;Done clearing this row?
BNE VertRowLoop2		;If not, branch to clear another section.

		LDA #$F0				;($B588)Prepare to update blocks starting -16 tiles above the player.
		STA YPosFromCenter	  ;($B58A)
		LDA #$EC				;($B58C)Prepare to update blocks starting -20 tiles left of the player.
STA XPosFromCenter	  ;

VertAttribLoop2:
LDA #$05				;Prepare to change a 5 block section.
		STA TileCounter		 ;($B592)
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

AttributeClearLoop2:
JSR ClearAttribByte	 ;($C244)Set black palette for 4x4 block area.

LDA $0F				 ;
		CLC					 ;($B59C)Move to the next 4x4 block area.
ADC #$04				;
		STA XPosFromCenter	  ;($B59F)

		DEC TileCounter		 ;($B5A1)Done clearing this section?
		BNE AttributeClearLoop2 ;($B5A3)If not, branch to clear another attrib byte.

DEC ScrollY			 ;Decrement vertical scroll and player Y pixel position.
		DEC CharYPixelsLB	   ;($B5A7)
		JSR DoSprites		   ;($B5A9)($B6DA)Update player and NPC sprites.

LDA XPosFromCenter	  ;
CMP #$14				;Done clearing this row?
		BNE VertAttribLoop2 ;($B5B0)If not, branch to clear another section.

LDA #$F0				;Prepare to update blocks starting -16 tiles above the player.
		STA YPosFromCenter	  ;($B5B4)
		LDA #$EE				;($B5B6)Prepare to update blocks starting -18 tiles left of the player.
		STA XPosFromCenter	  ;($B5B8)

VertRowLoop3:
		LDA #$03				;($B5BA)Prepare to change a 3 block section.
STA TileCounter		 ;
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

VertBlockLoop3:
LDA #$0C				;
		STA BlkRemoveFlgs	   ;($B5C3)Remove lower 2 tiles from the block
		STA PPUHorizontalVertical;($B5C5)PPU row write.

JSR ModMapBlock		 ;($AD66)Change block on map.

INC XPosFromCenter	  ;Increment to next block in row.
INC XPosFromCenter	  ;

DEC TileCounter		 ;Done changing block section?
BNE VertBlockLoop3	  ;If not, branch to do more.

		DEC ScrollY			 ;($B5D2)Move player up 1 pixel.
		DEC CharYPixelsLB	   ;($B5D4)

		JSR DoSprites		   ;($B5D6)($B6DA)Update player and NPC sprites.
		LDA XPosFromCenter	  ;($B5D9)
		CMP #$12				;($B5DB)Done changing block row?
BNE VertRowLoop3		;If not, branch to do more.

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

DEC ScrollY			 ;Decrement vertical scroll register.

		DEC NTBlockY			;($B5E4)
LDA NTBlockY			;
CMP #$FF				;Decrement Y block position on nametable.
		BNE +				   ;($B5EA)If it rolls over, make sure its set to the proper value.
		LDA #$0E				;($B5EC)
STA NTBlockY			;

		* DEC CharYPos		  ;($B5F0)Move player 1 pixel up.
		DEC CharYPixelsLB	   ;($B5F2)

JSR DoSprites		   ;($B6DA)Update player and NPC sprites.
		JMP DoCoveredArea	   ;($B5F7)($B5FA)Handle covered areas of the map, if necessary.

;----------------------------------------------------------------------------------------------------

DoCoveredArea:
		LDA CharXPos			;($B5FA)Make a copy of the player's X and Y position.
STA _TargetX			;It will be used to calculate an index into the
		LDA CharYPos			;($B5FE)covered map data.
STA _TargetY			;
JSR CheckCoveredArea	;($AABE)Check if player is in a covered map area.

LDA CoveredStsNext	  ;Did the player just enter/exit a covered area?
CMP CoverStatusus		 ;
BNE ToggleCoveredArea   ;If so, branch to toggle going in/out of cover.
RTS					 ;

ToggleCoveredArea:
		STA CoverStatusus	   ;($B60C)Update current cover status.
		LDA CoverStatusus	   ;($B60E)Is player moving into covered area?
		BEQ PrepToggleCover	 ;($B610)If not, branch to skip hiding player.
		JSR WaitForNMI		  ;($B612)($FF74)Wait for VBlank interrupt.

LDA #$F0				;
		STA SpriteRAM		   ;($B617)Hide the player as they enter a covered area.
		STA SpriteRAM+4		 ;($B61A)This simulates the player going under the covered area.
		STA SpriteRAM+8		 ;($B61D)
		STA SpriteRAM+12		;($B620)

PrepToggleCover:
		LDA NTBlockX			;($B623)Prepare to add/remove blocks from opposite one screen
CLC					 ;over from the active area of the nametab;es.
		ADC #$10				;($B626)
		AND #$1F				;($B628)Ensure result does not go past 31 blocks.
STA NTBlockX			;

		LDA #$F2				;($B62C)Start replacing blocks -14 tiles above player's position.
STA YPosFromCenter	  ;

CoverOuterLoop:
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

		LDA #$F0				;($B633)Start replacing blocks -16 tiles to the left of the player.
STA XPosFromCenter	  ;

CoverLeftLoop:
LDA #$00				;
		STA BlkRemoveFlgs	   ;($B639)Remove no tiles from the current block.
		STA PPUHorizontalVertical;($B63B)PPU column write.

JSR ModMapBlock		 ;($AD66)Change block on map.
		INC XPosFromCenter	  ;($B640)Move to next block. A block is 2 tiles wide.
		INC XPosFromCenter	  ;($B642)

LDA XPosFromCenter	  ;Have all the blocks left of the player's poistion been changed?
CMP #$00				;
BNE CoverLeftLoop	   ;If not, branch to change another block.

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

CoverRightLoop:
		LDA #$00				;($B64D)
		STA BlkRemoveFlgs	   ;($B64F)Remove no tiles from the current block.
		STA PPUHorizontalVertical;($B651)PPU column write.

JSR ModMapBlock		 ;($AD66)Change block on map.
INC XPosFromCenter	  ;Move to next block. A block is 2 tiles wide.
		INC XPosFromCenter	  ;($B658)

		LDA XPosFromCenter	  ;($B65A)Have all the blocks right of the player's poistion been changed?
CMP #$10				;
BNE CoverRightLoop	  ;If not, branch to remove another block.

		INC YPosFromCenter	  ;($B660)Move to the next row of blocks. A block is 2 tiles tall.
INC YPosFromCenter	  ;

		LDA YPosFromCenter	  ;($B664)Have all the rows of blocks been changed?
		CMP #$10				;($B666)
BNE CoverOuterLoop	  ;If not, branch to change another row.

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

LDA #$01				;Reset the frame counter.
STA FrameCounter		;

LDA #NPC_STOP		   ;Stop the NPCs from moving.
STA StopNPCMove		 ;

		JSR DoSprites		   ;($B675)($B6DA)Update player and NPC sprites.

LDA #NPC_MOVE		   ;Allow the NPCs to move again.
		STA StopNPCMove		 ;($B67A)

		LDA ActiveNmTbl		 ;($B67C)
		EOR #$01				;($B67E)Swap nametables. This is where the blocks were all changed.
		STA ActiveNmTbl		 ;($B680)

LDA #$EE				;Start replacing blocks -18 tiles to the left of the player.
		STA XPosFromCenter	  ;($B684)This second run deletes a single column of blocks.

ColumnOuterLoop:
		JSR WaitForNMI		  ;($B686)($FF74)Wait for VBlank interrupt.

LDA #$F2				;Start replacing blocks -14 tiles above player's position.
STA YPosFromCenter	  ;

CoverHiColumnLoop:
LDA #$00				;
STA BlkRemoveFlgs	   ;Remove no tiles from the current block.
STA PPUHorizontalVertical		 ;PPU column write.

JSR ModMapBlock		 ;($AD66)Change block on map.

		INC YPosFromCenter	  ;($B696)Move to the next block in the column. A block is 2 tiles tall.
		INC YPosFromCenter	  ;($B698)

		LDA YPosFromCenter	  ;($B69A)Has the upper half of the column been changed?
		CMP #$02				;($B69C)
		BNE CoverHiColumnLoop   ;($B69E)If not, branch to change another block.

		JSR WaitForNMI		  ;($B6A0)($FF74)Wait for VBlank interrupt.

CoverLoColumnLoop:
LDA #$00				;
STA BlkRemoveFlgs	   ;Remove no tiles from the current block.
STA PPUHorizontalVertical		 ;PPU column write.

JSR ModMapBlock		 ;($AD66)Change block on map.

		INC YPosFromCenter	  ;($B6AC)Move to the next block in the column. A block is 2 tiles tall.
		INC YPosFromCenter	  ;($B6AE)

		LDA YPosFromCenter	  ;($B6B0)Has the lower half of the column been changed?
CMP #$10				;
		BNE CoverLoColumnLoop   ;($B6B4)If not, branch to change another block.

		LDA XPosFromCenter	  ;($B6B6)This has to loop 3 times.  Not sure why.  Maybe the
CLC					 ;time it takes to change all the blocks is too long so
		ADC #$22				;($B6B9)it has to be broken up into multiple passes.
STA XPosFromCenter	  ;

CMP #$32				;Have 3 passes been completed for changing the block columns?
		BNE ColumnOuterLoop	 ;($B6BF)If not, branch to do another column.
RTS					 ;

;----------------------------------------------------------------------------------------------------

SpriteFacingBaseAddress:
		STA NPCCounter		  ;($B6C2)Save a copy of character direction.

LDA CharSpriteTblPtr	;
STA GenPtr22LB		  ;Get base address of character sprite table.
		LDA CharSpriteTblPtr+1  ;($B6C9)
		STA GenPtr22UB		  ;($B6CC)

		* LDA NPCCounter		;($B6CE)Increment upper byte of pointer while decrementing the
BEQ SprtFacingEnd	   ;NPC counter to find the base address of the character
INC GenPtr22UB		  ;sprites for the proper facing direction.  The table
		DEC NPCCounter		  ;($B6D4)is organized by the direction the character is facing.
		JMP -				   ;($B6D6)Has proper direction been found? If not, branch to decrement.

SprtFacingEnd:
		RTS					 ;($B6D9)End sprite direction calculations.

;----------------------------------------------------------------------------------------------------

DoSprites:
LDA EnemyNumber			;Is this the final fight?
CMP #EN_DRAGONLORD2	 ;If so, exit, else branch
		BNE SpriteCheckFrameCounter;($B6DE)to continue processing.
		RTS					 ;($B6E0)

SpriteCheckFrameCounter:
LDA FrameCounter		;Is this the 16th frame?
AND #$0F				;
BNE ChkGotGwaelin	   ;If not, branch.

LDA CharLeftRight	   ;Every 16th frame, alternate character animations. This
CLC					 ;creates the walking effect for characters. bit 3 is
		ADC #$08				;($B6EA)the only bit considered.
		STA CharLeftRight	   ;($B6EC)

ChkGotGwaelin:
LDA PlayerFlags		 ;Is the player carrying Gwaelin?
		AND #F_GOT_GWAELIN	  ;($B6F0)if not, branch.
		BEQ CheckPlayerWeapons  ;($B6F2)

		LDA #$C0				;($B6F4)Offset to carrying Gwaelin tile patterns.
STA GenByte3C		   ;
		BNE GetPlayerAnim	   ;($B6F8)Branch always.

CheckPlayerWeapons:
LDA #$80				;Offset to not carrying weapon tile patterns.
		STA GenByte3C		   ;($B6FC)

LDA EqippedItems		;Is player carrying a weapon?
AND #WP_WEAPONS		 ;
		BEQ CheckPlayerShields  ;($B702)If not, branch to check if they are carrying a shield.

		LDA #$90				;($B704)Offset to carrying weapon tile patterns.
		STA GenByte3C		   ;($B706)Player is carrying a weapon.

CheckPlayerShields:
		LDA EqippedItems		;($B708)Is player carrying a shield?
AND #SH_SHIELDS		 ;
BEQ GetPlayerAnim	   ;If not, branch.

LDA #$20				;Offset to carrying shield tile patterns.
ORA GenByte3C		   ;
		STA GenByte3C		   ;($B712)Combine it with weapon carrying sprite offset.

GetPlayerAnim:
		LDA CharLeftRight	   ;($B714)
AND #$08				;Add in the walking animation tile patterns for the player.
		ORA GenByte3C		   ;($B718)
		TAY					 ;($B71A)

LDX #$00				;Index to first player sprite is 0.

		LDA #$6F				;($B71D)First sprite tile of player is 111 pixels from top of screen.
		STA CharacterYScreenPosition;($B71F)

		LDA CharDirection	   ;($B721)Use character facing direction for char table index calc.
JSR SpriteFacingBaseAddress  ;($B6C2)Calculate entry into char data table based on direction.

GetPlayerTileLoop1:
LDA #$80				;First sprite tile of player is 128 pixels from left of screen.
		STA CharacterXScreenPosition;($B729)

GetPlayerTileLoop2:
LDA WindowBufferRAM+$1D0	  ;Check if window is covering player's position.
CMP #$FF				;If not, branch to hide player sprites.
BEQ +				   ;

LDA #$F0				;Hide the player sprite.
		BNE PlayerSetXCord	  ;($B734)Branch always.

		* LDA CharacterYScreenPosition;($B736)Load the player sprite Y position.

PlayerSetXCord:
STA SpriteRAM,X		 ;Store player sprite Y screen position.

		INX					 ;($B73B)
LDA (GenPtr22),Y		;Store player sprite tile pattern byte.
STA SpriteRAM,X		 ;

		INX					 ;($B741)
INY					 ;Store player sprite attribute byte.
LDA (GenPtr22),Y		;
STA SpriteRAM,X		 ;

		INX					 ;($B748)
		INY					 ;($B749)Store player sprite X screen position.
LDA CharacterXScreenPosition		 ;
		STA SpriteRAM,X		 ;($B74C)

		INX					 ;($B74F)Move to next sprite.

		LDA CharacterXScreenPosition;($B750)
		CLC					 ;($B752)Next sprite is 8 pixels to the right.
		ADC #$08				;($B753)
		STA CharacterXScreenPosition;($B755)

CMP #$90				;Have the 2 sprites in the row been processed?
		BNE GetPlayerTileLoop2  ;($B759)If not, branch to process second sprite.

		LDA CharacterYScreenPosition;($B75B)
CLC					 ;Move down 1 row for next player sprite tiles(8 pixels).
		ADC #$08				;($B75E)
		STA CharacterYScreenPosition;($B760)

CMP #$7F				;Have all 4 sprite tiles for the player been placed?
		BNE GetPlayerTileLoop1  ;($B764)If not, branch to place another tile.

		LDA NPCUpdateCounter	;($B766)Are NPCs on the current map?
AND #$F0				;
BEQ UpdateNPCs1		 ;If so, branch to update NPCs.

		JMP UpdateNPCCounter	;($B76C)($B9FB)Update NPC counter and exit.

;This code calculates the movement of 2 NPCs whenever its entered. Which 2 NPCs is based on
;NPCUpdateCounter.  There are a max of 20 NPCs but only 10 can move. Valid ranges for NPCUpdateCounter
;are 0 to 4.  There are 3 bytes of data per NPC.

UpdateNPCs1:
LDA NPCUpdateCounter	   ;
		ASL					 ;($B771)
		STA GenByte3C		   ;($B772)Calculate the offset to the NPCs to do movement calculations for.
		ASL					 ;($B774)
		ADC GenByte3C		   ;($B775)
TAX					 ;

		LDA #$02				;($B778)Prepare to calculate movements for 2 NPCs.
STA NPCLoopCounter	  ;

NPCMoveLoop:
		LDA NPCXPos,X		   ;($B77C)Extract the NPC X location data.
AND #$1F				;Is NPC X coordinate on screen?
BNE +				   ;If so, branch to move to next step of calculation.

		LDA NPCYPos,X		   ;($B782)Extract the NPC Y location data.
		AND #$1F				;($B784)Is NPC Y coordinate on screen?
		BNE +				   ;($B786)If so, branch to move to next step of calculation.

JMP EndNPCMoveLoop	  ;($B8EA)Check for next NPC movement.

		* LDA FrameCounter	  ;($B78B)
AND #$0F				;NPC movement can only be processed on frame 1.
CMP #$01				;Is the frame counter on frame 1?
BEQ +				   ;If so, branch to keep processing movement for this NPC.

		JMP NPCProcessCont	  ;($B793)($B861)Can't move NPC. Jump to do other processing.

		* LDA StopNPCMove	   ;($B796)Can NPC move?
		BEQ SetNPCDir		   ;($B798)If so, branch to choose random facing direction.

HaltNPCMoveCalcs:
ASL NPCYPos,X		   ;Clear MSB to indicate movement is stopped for NPC.
		LSR NPCYPos,X		   ;($B79C)
		JMP EndNPCMoveLoop	  ;($B79E)($B8EA)Check for next NPC movement.

SetNPCDir:
		JSR UpdateRandNum	   ;($B7A1)($C55B)Get random number.
		LDA NPCYPos,X		   ;($B7A4)
		AND #$9F				;($B7A6)Set NPC direction facing up.
		STA NPCYPos,X		   ;($B7A8)

		LDA RandomNumberUB	  ;($B7AA)
		AND #$60				;($B7AC)Randomly set direction of NPC.
		ORA NPCYPos,X		   ;($B7AE)
		STA NPCYPos,X		   ;($B7B0)

		JSR GetNPCPosCopy	   ;($B7B2)($BA15)Get a copy of the NPCs X and Y block position.

JSR ChkNPCWndwBlock	 ;($BA22)Check if window blocking NPC movement.
		LDA NPCOnScreen		 ;($B7B8)Is the NPC on the screen?
		BEQ +				   ;($B7BA)If not, branch to skip window block check.

LDA WindowBlock		 ;Is a window blocking the NPC from moving?
		CMP #$FF				;($B7BE)
BNE HaltNPCMoveCalcs	;If so, branch to stop movement.

* JSR CheckCoveredArea	;($AABE)Check if player is in a covered map area.

LDA NPCYPos,X		   ;Extract NPC direction facing data.
AND #$60				;Is NPC facing up?
BNE +				   ;If not, branch to check next direction.

DEC ThisNPCYPos		 ;Prepare to move NPC up 1 block.
JMP ChkNPCMapLimit	  ;($B7E4)Check if NPC will move off end of map.

* CMP #NPC_RIGHT		  ;Is NPC facing right?
		BNE +				   ;($B7D2)If not, branch to check next direction.

INC ThisNPCXPos		 ;Prepare to move NPC right 1 block.
JMP ChkNPCMapLimit	  ;($B7E4)Check if NPC will move off end of map.

		* CMP #NPC_DOWN		 ;($B7D9)Is NPC facing down?
		BNE +				   ;($B7DB)If not, branch to move NPC left.

INC ThisNPCYPos		 ;Prepare to move NPC down 1 block.
JMP ChkNPCMapLimit	  ;($B7E4)Check if NPC will move off end of map.

* DEC ThisNPCXPos		 ;Prepare to move NPC left 1 block.

ChkNPCMapLimit:
		LDA MapHeight		   ;($B7E4)Is NPC trying to move beyond map height?
CMP ThisNPCYPos		 ;
BCS +				   ;If not, branch to check map width.

JMP HaltNPCMoveCalcs	;($B79A)Can't move NPC. Stop movement calculations.

		* LDA MapWidth		  ;($B7ED)Is NPC trying to move beyond map width?
CMP ThisNPCXPos		 ;
		BCC HaltNPCMoveCalcs	;($B7F1)If so, branch to stop movement.

		JSR ChkNPCWndwBlock	 ;($B7F3)($BA22)Check if window blocking NPC movement.
LDA NPCOnScreen		 ;Is the NPC on the screen?
		BEQ +				   ;($B7F8)If not, branch to skip window block check.

		LDA WindowBlock		 ;($B7FA)Is a window blocking the NPC from moving?
CMP #$FF				;
		BNE HaltNPCMoveCalcs	;($B7FE)If so, branch to stop movement.

		* LDA ThisNPCXPos	   ;($B800)
		CMP CharXPos			;($B802)
BNE +				   ;Is NPC trying to move to player's current position?
LDA ThisNPCYPos		 ;
		CMP CharYPos			;($B808)If so, branch to stop movement.
		BEQ HaltNPCMoveCalcs	;($B80A)

* LDA ThisNPCXPos		 ;
		CMP _CharXPos		   ;($B80E)Is NPC trying to move to player's next position?
		BNE +				   ;($B810)
		LDA ThisNPCYPos		 ;($B812)If so, jump to stop movement.
CMP _CharYPos		   ;
		BNE +				   ;($B816)
		JMP HaltNPCMoveCalcs	;($B818)($B79A)Can't move NPC. Stop movement calculations.

		* LDY #$00			  ;($B81B)Prepare to check collisions with other NPCs.

NPCCollideLoop:
LDA _NPCXPos,Y		  ;Does this NPC X position match another NPC X position?
		AND #$1F				;($B820)
CMP ThisNPCXPos		 ;
		BNE +				   ;($B824)If not, branch to check the next NPC.

LDA _NPCYPos,Y		  ;Does this NPC Y position match another NPC Y position?
		AND #$1F				;($B829)
CMP ThisNPCYPos		 ;
BNE +				   ;If not, branch to check the next NPC.

		JMP HaltNPCMoveCalcs	;($B82F)($B79A)Can't move NPC. Stop movement calculations.

		* INY				   ;($B832)
INY					 ;Increment to next NPC data set.
		INY					 ;($B834)

CPY #$3C				;Have all 20 NPCs been checked?
BNE NPCCollideLoop	  ;If not, branch to check another NPC.

LDA GenByte3D		   ;Save current status of $3D on stack.
		PHA					 ;($B83B)

LDA ThisNPCXPos		 ;
		STA XTarget			 ;($B83E)Prepare to get the block type the NPC is standing on.
		LDA ThisNPCYPos		 ;($B840)
STA YTarget			 ;
JSR GetBlockID		  ;($AC17)Get description of block.
		JSR HasCoverData		;($B847)($AAE1)Check if current map has covered areas.

		PLA					 ;($B84A)Did player just enter/exit covered area?
CMP CoveredStsNext	  ;If so, jump to stop NPC movement.
BEQ +				   ;
JMP HaltNPCMoveCalcs	;($B79A)Can't move NPC. Stop movement calculations.

* LDA TargetResults	   ;Is NPC trying to move onto a non-walkable block?
CMP #BLK_FFIELD		 ;If so, jump to stop NPC movement.
		BCC +				   ;($B856)
JMP HaltNPCMoveCalcs	;($B79A)Can't move NPC. Stop movement calculations.

		* LDA NPCYPos,X		 ;($B85B)
ORA #$80				;Indicate NPC is in the process of moving.
STA NPCYPos,X		   ;

NPCProcessCont:
LDA NPCYPos,X		   ;Is NPC in process of moving?
BMI +				   ;If so, branch to update NPC movement.
JMP EndNPCMoveLoop	  ;($B8EA)Check for next NPC movement.

		* LDA StopNPCMove	   ;($B868)Is NPC status prohibiting them from moving?
		BEQ +				   ;($B86A)If not, branch to keep processing NPC movement.

JMP EndNPCMoveLoop	  ;($B8EA)Check for next NPC movement.

* LDA NPCYPos,X		   ;Is NPC facing up?
AND #$60				;
BNE +				   ;If not, branch to check the next direction.

LDA NPCMidPos,X		 ;
AND #$0F				;
SEC					 ;Move NPC 1 pixel up.
SBC #$01				;
AND #$0F				;
STA GenByte3C		   ;

		LDA NPCMidPos,X		 ;($B880)
		AND #$F0				;($B882)Get any upper nibble data and save it(should be none).
		ORA GenByte3C		   ;($B884)
		STA NPCMidPos,X		 ;($B886)

LDA GenByte3C		   ;Has NPC moved 16 pixels?
		CMP #$0F				;($B88A)If not, branch to keep moving NPC.
		BNE EndNPCMoveLoop	  ;($B88C)($B8EA)Check for next NPC movement.

DEC NPCYPos,X		   ;NPC is done moving. Update current Y position.
JMP EndNPCMoveLoop	  ;($B8EA)Check for next NPC movement.

		* CMP #NPC_RIGHT		;($B893)Is NPC facing right?
		BNE +				   ;($B895)If not, branch to check the next direction.

		LDA NPCMidPos,X		 ;($B897)
AND #$F0				;
CLC					 ;Move NPC 1 pixel right.
		ADC #$10				;($B89C)
STA GenByte3C		   ;

LDA NPCMidPos,X		 ;
AND #$0F				;Get any lower nibble data and save it(should be none).
		ORA GenByte3C		   ;($B8A4)
		STA NPCMidPos,X		 ;($B8A6)

LDA GenByte3C		   ;Has NPC moved 16 pixels? If not, branch to keep moving NPC.
BNE EndNPCMoveLoop	  ;Check for next NPC movement.

		INC NPCXPos,X		   ;($B8AC)NPC is done moving. Update current X position.
JMP EndNPCMoveLoop	  ;($B8EA)Check for next NPC movement.

* CMP #NPC_DOWN		   ;Is NPC facing down?
BNE +				   ;If not, branch to move NPC left.

		LDA NPCMidPos,X		 ;($B8B5)
		AND #$0F				;($B8B7)
CLC					 ;Move NPC 1 pixel down.
		ADC #$01				;($B8BA)
		AND #$0F				;($B8BC)
STA GenByte3C		   ;

LDA NPCMidPos,X		 ;
		AND #$F0				;($B8C2)Get any upper nibble data and save it(should be none).
ORA GenByte3C		   ;
STA NPCMidPos,X		 ;

LDA GenByte3C		   ;Has NPC moved 16 pixels? If not, branch to keep moving NPC.
		BNE EndNPCMoveLoop	  ;($B8CA)Check for next NPC movement.

		INC NPCYPos,X		   ;($B8CC)NPC is done moving. Update current Y position.
JMP EndNPCMoveLoop	  ;($B8EA)Check for next NPC movement.

		* LDA NPCMidPos,X	   ;($B8D1)
AND #$F0				;
		SEC					 ;($B8D5)Move NPC 1 pixel left.
SBC #$10				;
STA GenByte3C		   ;

		LDA NPCMidPos,X		 ;($B8DA)
AND #$0F				;Get any lower nibble data and save it(should be none).
ORA GenByte3C		   ;
STA NPCMidPos,X		 ;

LDA GenByte3C		   ;Has NPC moved 16 pixels? If not, branch to keep moving NPC.
CMP #$F0				;
		BNE EndNPCMoveLoop	  ;($B8E6)Check for next NPC movement.

DEC NPCXPos,X		   ;NPC is done moving. Update current X position.

EndNPCMoveLoop:
INX					 ;
		INX					 ;($B8EB)Move to next set of NPC data.
		INX					 ;($B8EC)

DEC NPCLoopCounter	  ;Does the movement of another NPC need to be calculated?
		BEQ UpdateNPCs2		 ;($B8EF)If not, branch to move on to other calculations.

		JMP NPCMoveLoop		 ;($B8F1)($B77C)Calculate movement for an NPC.

UpdateNPCs2:
LDX #$00				;Zero out index into NPC data.

		LDA #$10				;($B8F6)Skip first 16 bytes of sprite RAM. This RAM is reserved
STA SpriteRAMIndex	  ;for the player's sprites.

NPCSpritesLoop:
		LDA NPCXPos,X		   ;($B8FA)Get the NPC X and Y position data. If both are not 0,
		AND #$1F				;($B8FC)the NPC is valid and and should be drawn on the screen.
		BNE CalcNPCSprites	  ;($B8FE)Branch to draw NPC sprites. An intersting effect is that
		LDA NPCYPos,X		   ;($B900)An NPC can be pushed to 0,0 on the map and they will
		AND #$1F				;($B902)disappear. This can only happen in Rimuldar as position
		BNE CalcNPCSprites	  ;($B904)0,0 can only be reached in this town.

		JMP NextNPCSprites	  ;($B906)($B9DF)Increment to next NPC.

CalcNPCSprites:
JSR NPCXScreenCord	  ;($BA52)Get NPC pixel X coord on the screen.

		LDA NPCXPixelsLB		;($B90C)
		CLC					 ;($B90E)Add 7 to calculated difference value.
ADC #$07				;
STA NPCXPixelsLB		;

LDA NPCXPixelsUB		;
ADC #$00				;If upper byte is 0, NPC X position is in visible range.
		BEQ ChkNPCYLoc		  ;($B917)

		CMP #$01				;($B919)If upper byte is 1, NPC X position may be in visible range.
		BEQ +				   ;($B91B)

JMP NextNPCSprites	  ;($B9DF)Increment to next NPC. This NPC not visible.

		* LDA NPCXPixelsLB	  ;($B920)Is upper byte 1 and lower byte 7 or below?
CMP #$07				;
BCC ChkNPCYLoc		  ;If so, branch. NPC X position is in visible range.

JMP NextNPCSprites	  ;($B9DF)Increment to next NPC.

ChkNPCYLoc:
JSR NPCYScreenCord	  ;($BA84)Get NPC pixel Y coord on the screen.

		LDA NPCYPixelsLB		;($B92C)
CLC					 ;Add 17 to calculated difference value.
ADC #$11				;
		STA NPCYPixelsLB		;($B931)

LDA NPCYPixelsUB		;
ADC #$00				;If upper byte is 0, NPC X position is in visible range.
BEQ +				   ;

		JMP NextNPCSprites	  ;($B939)($B9DF)Increment to next NPC.

		* JSR GetNPCPosCopy	 ;($B93C)($BA15)Get a copy of the NPCs X and Y block position.

JSR ChkNPCWndwBlock	 ;($BA22)Check if window is covering the NPC or NPC is off screen.
		LDA NPCOnScreen		 ;($B942)Is this NPC on screen?
BEQ +				   ;If not, branch.

		LDA WindowBlock		 ;($B946)Is there a window covering the NPC?
CMP #$FF				;
		BEQ +				   ;($B94A)If not, branch.

		JMP NextNPCSprites	  ;($B94C)($B9DF)Increment to next NPC.

		* LDA ThisNPCXPos	   ;($B94F)Store a copy of the NPC's X and Y block location
		STA GenByte3C		   ;($B951)Has no apparent use as it is overwritten in the
LDA ThisNPCYPos		 ;CheckCoveredArea function below.
STA GenByte3E		   ;

		JSR CheckCoveredArea	;($B957)($AABE)Check if player is in a covered map area.
		LDA CoveredStsNext	  ;($B95A)
		CMP CoverStatusus	   ;($B95C)Did player just transition in/out of cover?
BEQ +				   ;If not, branch.

		JMP NextNPCSprites	  ;($B960)($B9DF)Increment to next NPC.

* JSR GetNPCSpriteIndex   ;($C0F4)Get index into sprite pattern table data for NPC.
		STA GenByte3C		   ;($B966)Save index to sprite pattern table data for NPC.

JSR NPCXScreenCord	  ;($BA52)Get NPC pixel X coord on the screen.
		JSR NPCYScreenCord	  ;($B96B)($BA84)Get NPC pixel Y coord on the screen.

LDY SpriteRAMIndex	  ;Transfer Sprite RAM index into Y.
STX NPCROMIndex		 ;Store index to current NPC being processed.

LDX GenByte3C		   ;Load X with index into CharSpriteTbl for current NPC .

		LDA #$00				;($B974)Start a first sprite row in NPC.
STA CharacterYScreenPosition		 ;

NPCSpriteRowLoop:
LDA #$00				;Start a first sprite column in NPC.
STA NPCSpriteXOfst	  ;

NPCSpriteColLoop:
		LDA NPCXPixelsLB		;($B97C)
		CLC					 ;($B97E)Find X position of this NPC sprite by adding
		ADC NPCSpriteXOfst	  ;($B97F)together the NPC position with the current tile X offset.
STA ThisNPCXPos		 ;

LDA NPCXPixelsUB		;Did this NPC sprite go beyond the screen bounds?
ADC #$00				;
BNE NextNPCSprite	   ;If so, branch to check next NPC sprite.

		TYA					 ;($B989)Before:
STX NPCOffsetset		   ;X-CharSpriteTbl, Y-Index into sprite(OAM) RAM.
		TAX					 ;($B98C)After:
LDY NPCROMIndex		 ;X-Index into sprite(OAM) RAM, Y-Index into NPC data from ROM.

LDA _NPCYPos,Y		  ;Extract NPC facing direction data.
		AND #$60				;($B992)

		ASL					 ;($B994)
		ROL					 ;($B995)Move facing direction to LSBs.
ROL					 ;
		ROL					 ;($B997)

JSR SpriteFacingBaseAddress  ;($B6C2)Calculate entry into char data table based on direction.

		LDY NPCOffsetset		;($B99B)

		LDA ThisNPCXPos		 ;($B99D)Save updated X position of NPC sprite.
STA SpriteRAM+3,X	   ;

		LDA NPCYPixelsLB		;($B9A2)Find Y position of this NPC sprite by adding
		CLC					 ;($B9A4)together the NPC position with the current tile Y offset.
		ADC NPCSpriteYOfst	  ;($B9A5)

		STA SpriteRAM,X		 ;($B9A7)Save updated Y position of NPC sprite.

		LDA (GenPtr22),Y		;($B9AA)Store pattern table byte for this sprite.
		STA SpriteRAM+1,X	   ;($B9AC)

		INY					 ;($B9AF)Increment to attribute byte index.

		LDA (GenPtr22),Y		;($B9B0)Get attribute table byte for this sprite.

		DEY					 ;($B9B2)Decrement index because it will be incremented by 2 later.

STA SpriteRAM+2,X	   ;Store attribute table byte for this sprite.

TYA					 ;Before:
		STX GenByte22		   ;($B9B7)X-Index into sprite RAM, Y-Index into CharSpriteTbl.
TAX					 ;After:
		LDY GenByte22		   ;($B9BA)X-Index into CharSpriteTbl, Y-Index into sprite RAM.

INY					 ;
		INY					 ;($B9BD)Move to next sprite in sprite(OAM) RAM.
		INY					 ;($B9BE)
INY					 ;

NextNPCSprite:
		INX					 ;($B9C0)Move to next entry in CharSpriteTbl.
		INX					 ;($B9C1)2 bytes-tile pattern byte and attribute byte.

TYA					 ;Have all 64 possible sprites been processed?
		BEQ NPCLoopDone		 ;($B9C3)If so, branch to stop processing.

		LDA NPCSpriteXOfst	  ;($B9C5)
CLC					 ;Move to next tile in NPC sprite row.
ADC #$08				;
STA NPCSpriteXOfst	  ;

		CMP #$10				;($B9CC)Have both tiles in this sprite row been processed?
		BNE NPCSpriteColLoop	;($B9CE)If not, branch to do second tile.

LDA NPCSpriteYOfst	  ;
CLC					 ;Move to next row in NPC sprite.
		ADC #$08				;($B9D3)
STA CharacterYScreenPosition		 ;

CMP #$10				;ave both rows in this sprite been processed?
BNE NPCSpriteRowLoop	;If not, branch to do second row.

LDX NPCROMIndex		 ;Load X with index to NPC data.
STY SpriteRAMIndex	  ;Load Y with index into sprite RAM.

NextNPCSprites:
INX					 ;
		INX					 ;($B9E0)Move to next NPC. 3 bytes of data per NPC.
INX					 ;

		CPX #$3C				;($B9E2)Have all the NPCs been processed?
		BEQ NPCLoopDone		 ;($B9E4)If so, branch to exit loop.

		JMP NPCSpritesLoop	  ;($B9E6)($B8FA)Jump to calculate sprites for next NPC.

NPCLoopDone:
		LDY SpriteRAMIndex	  ;($B9E9)Get index to current sprite in sprite RAM.
LDA #$F0				;Set Y value out of screen range.

HideSpriteLoop:
		CPY #$00				;($B9ED)Have all remaining sprites been hidden?
		BEQ UpdateNPCCounter	;($B9EF)If so, branch.

		STA SpriteRAM,Y		 ;($B9F1)Store Y position of sprite outside of screen bounds.

		INY					 ;($B9F4)
INY					 ;Move to next sprite. 4 bytes per sprite.
INY					 ;
		INY					 ;($B9F7)

		JMP HideSpriteLoop	  ;($B9F8)Jump to check the next sprite.

UpdateNPCCounter:
LDA FrameCounter		;Is the frame counter on frame 0?
AND #$0F				;
BEQ +				   ;If so, branch to updater the NPC counter.
RTS					 ;

		* LDA NPCUpdateCounter  ;($BA02)Are there no NPCs on this map?
CMP #$FF				;
BEQ SpritesEnd		  ;If none, branch to exit.

		INC NPCUpdateCounter	;($BA08)Increment NPC counter.
LDA NPCUpdateCounter	   ;
		CMP #$05				;($BA0C)Should be a value 0 to 4.
		BNE SpritesEnd		  ;($BA0E)If outside valid value, wrap counter.

		LDA #$00				;($BA10)Reset update NPC update counter.
		STA NPCUpdateCounter	;($BA12)

SpritesEnd:
RTS					 ;End sprite processing.

;----------------------------------------------------------------------------------------------------

GetNPCPosCopy:
		LDA NPCXPos,X		   ;($BA15)
		AND #$1F				;($BA17)Save a copy of the current NPC's X block position.
STA ThisNPCXPos		 ;

LDA NPCYPos,X		   ;
AND #$1F				;Save a copy of the current NPC's Y block position.
		STA ThisNPCYPos		 ;($BA1F)
		RTS					 ;($BA21)

;----------------------------------------------------------------------------------------------------

ChkNPCWndwBlock:
		LDA #$00				;($BA22)Assume the NPC is off screen.
		STA NPCOnScreen		 ;($BA24)

LDA ThisNPCXPos		 ;
SEC					 ;Get the difference between NPC and player X position.
		SBC CharXPos			;($BA29)

CLC					 ;
		ADC #$08				;($BA2C)Add 8 to make the value positive.
STA XPosFromLeft		;

		CMP #$10				;($BA30)Is NPC out of visible range in the X direction?
		BCC +				   ;($BA32)
		RTS					 ;($BA34)If so, exit. NPC is off screen.

		* LDA ThisNPCYPos	   ;($BA35)
SEC					 ;Get the difference between NPC and player Y position.
		SBC CharYPos			;($BA38)

		CLC					 ;($BA3A)
ADC #$07				;Add 7 to make the value positive.
		STA YPosFromTop		 ;($BA3D)

		CMP #$0F				;($BA3F)Is NPC out of visible range in the Y direction?
		BCC +				   ;($BA41)
RTS					 ;If so, exit. NPC is off screen.

		* JSR CalcPPUBufAddr	;($BA44)($C596)Calculate PPU address.
		LDY #$00				;($BA47)
		LDA (PPUBufferPointer),Y;($BA49)Get the any window data over the given block.
		STA WindowBlock		 ;($BA4B)

		LDA #$FF				;($BA4D)
		STA NPCOnScreen		 ;($BA4F)Indicate the NPC is on the screen.
RTS					 ;

;----------------------------------------------------------------------------------------------------

NPCXScreenCord:
LDA NPCXPos,X		   ;
AND #$1F				;Extract NPC X position data.
		STA NPCXPixelsUB		;($BA56)

		LDA NPCMidPos,X		 ;($BA58)Save NPC mid-movement X pixel position.
		STA NPCXPixelsLB		;($BA5A)

LSR NPCXPixelsUB		;
ROR NPCXPixelsLB		;
LSR NPCXPixelsUB		;
ROR NPCXPixelsLB		;Calculate NPC X pixel location on the map.
		LSR NPCXPixelsUB		;($BA64)
		ROR NPCXPixelsLB		;($BA66)
LSR NPCXPixelsUB		;
		ROR NPCXPixelsLB		;($BA6A)

		LDA NPCXPixelsLB		;($BA6C)
		SEC					 ;($BA6E)
		SBC CharXPixelsLB	   ;($BA6F)Subtract player's X pixel location from the NPC's X pixel
		STA NPCXPixelsLB		;($BA71)location. Save the result in the NPC's X pixel location.
LDA NPCXPixelsUB		;The NPC's X location is a signed value of the difference
SBC CharXPixelsUB	   ;between the player and NPC X coordinates.
		STA NPCXPixelsUB		;($BA77)

		LDA NPCXPixelsLB		;($BA79)
		EOR #$80				;($BA7B)A wierd way of adding 128. Saves 1 instruction(CLC).
		STA NPCXPixelsLB		;($BA7D)Add 128 to the result. If the number is between 0 and 256
		BMI +				   ;($BA7F)then the NPC may be visible.
		INC NPCXPixelsUB		;($BA81)

		* RTS				   ;($BA83)Exit NPC X difference calculation.

;----------------------------------------------------------------------------------------------------

NPCYScreenCord:
LDA NPCYPos,X		   ;
AND #$1F				;Extract NPC Y position data.
		STA NPCYPixelsUB		;($BA88)

		LDA #$00				;($BA8A)Zero out lower byte.
STA NPCYPixelsLB		;

LSR NPCYPixelsUB		;
		ROR NPCYPixelsLB		;($BA90)
		LSR NPCYPixelsUB		;($BA92)
ROR NPCYPixelsLB		;Calculate NPC Y pixel location on the map.
		LSR NPCYPixelsUB		;($BA96)
		ROR NPCYPixelsLB		;($BA98)
LSR NPCYPixelsUB		;
ROR NPCYPixelsLB		;

LDA NPCMidPos,X		 ;Save NPC mid-movement Y pixel position.
		AND #$0F				;($BAA0)

		ORA NPCYPixelsLB		;($BAA2)Add in the NPC mid-movement Y pixel position.
		STA NPCYPixelsLB		;($BAA4)

SEC					 ;
SBC CharYPixelsLB	   ;Subtract player's Y pixel location from the NPC's Y pixel
		STA NPCYPixelsLB		;($BAA9)location. Save the result in the NPC's Y pixel location.
		LDA NPCYPixelsUB		;($BAAB)The NPC's Y location is a signed value of the difference
		SBC CharYPixelsUB	   ;($BAAD)between the player and NPC X coordinates.
		STA NPCYPixelsUB		;($BAAF)

		LDA NPCYPixelsLB		;($BAB1)
CLC					 ;
		ADC #$6F				;($BAB4)Add 111 to the result. If the number is between 0 and 240
STA NPCYPixelsLB		;then the NPC may be visible.
		BCC +				   ;($BAB8)
		INC NPCYPixelsUB		;($BABA)

		* RTS				   ;($BABC)Exit NPC Y difference calculation.

;----------------------------------------------------------------------------------------------------

LoadEndBossGFX:
		LDA #PAL_LOAD_BG		;($BABD)Prepare to load both sprite and background palettes.
		STA LoadBGPal		   ;($BABF)
		JSR WaitForNMI		  ;($BAC1)($FF74)Wait for VBlank interrupt.

		LDA TownPalPtr		  ;($BAC4)
STA BackgroundPalettePointerLB		  ;Get background palette pointer.
		LDA TownPalPtr+1		;($BAC9)
		STA BackgroundPalettePointerUB;($BACC)

		LDA BlackPalPtr		 ;($BACE)
		STA SpritePalettePointerLB;($BAD1)Get sprite palette pointer.
		LDA BlackPalPtr+1	   ;($BAD3)
		STA SpritePalettePointerUB;($BAD6)

		JSR PalFadeOut		  ;($BAD8)($C212)Fade out both background and sprite palettes.

LDA #NT_NAMETBL0_LB	 ;
		STA PPUAddrLB		   ;($BADD)Load base address of nametable 0.
		LDA #NT_NAMETBL0_UB	 ;($BADF)
		STA PPUAddrUB		   ;($BAE1)

		LDA #$1E				;($BAE3)Prepare to load 30 nametable buffer rows.
STA BufferByteCounter		 ;
LDA #TL_BLANK_TILE1	 ;Prepare to load blank tiles into the buffer.
		STA PPUDataByte		 ;($BAE9)

		JSR LoadBufferRows	  ;($BAEB)($BBAE)Load a string of the same byte into nametable buffer rows.

		LDA #$00				;($BAEE)Prepare to clear out the attribute table.
		STA PPUDataByte		 ;($BAF0)

		LDA #$02				;($BAF2)Load 2 rows of zeros into the attribute table.
		STA BufferByteCounter   ;($BAF4)

		JSR LoadBufferRows	  ;($BAF6)($BBAE)Load a string of the same byte into nametable buffer rows.
		JSR WaitForNMI		  ;($BAF9)($FF74)Wait for VBlank interrupt.

		LDA #$FF				;($BAFC)Prepare to clear NES RAM.
		LDY #$00				;($BAFE)256 bytes.

* STA WindowBufferRAM,Y		 ;
		STA WindowBufferRAM+$100,Y;($BB03)
		STA WindowBufferRAM+$200,Y;($BB06)Clear NES RAM.
		STA WindowBufferRAM+$300,Y;($BB09)
		DEY					 ;($BB0C)
		BNE -				   ;($BB0D)

		LDA #%00000000		  ;($BB0F)Turn off sprites and background.
STA PPUControl1		 ;

		JSR Bank0ToCHR0		 ;($BB14)($FCA3)Load CHR bank 0 to CHR ROM 0.
		JSR Bank0ToCHR1		 ;($BB17)($FCA8)Load CHR bank 0 to CHR ROM 1.

		LDY #$00				;($BB1A)Start at beginning of table.

EBTileLoadLoop:
		LDA EndBossBGTiles,Y	;($BB1C)Get tile number from table
		STA PPUDataByte		 ;($BB1F)

INY					 ;
		LDA EndBossBGTiles,Y	;($BB22)Get lower address byte from table.
		STA PPUAddrLB		   ;($BB25)

		INY					 ;($BB27)
LDA EndBossBGTiles,Y	;Get upper address byte from table.
		STA PPUAddrUB		   ;($BB2B)

INY					 ;Last 4 entries are attribute table entries.
		CPY #$3C				;($BB2E)Is this one of the last 4 entries?
		BCS EBTileBufLoad	   ;($BB30)If not, branch.

		LDA PPUAddrLB		   ;($BB32)
		SEC					 ;($BB34)
		SBC #$02				;($BB35)Attribute table entry. Subtract 2 from address.
		STA PPUAddrLB		   ;($BB37)
		BCS EBTileBufLoad	   ;($BB39)
		DEC PPUAddrUB		   ;($BB3B)

EBTileBufLoad:
		JSR LoadBufferByte	  ;($BB3D)($BBDF)Load a single byte into the nametable buffer.
		CPY #$45				;($BB40)
BNE EBTileLoadLoop

		LDX #$00				;($BB44)Zero out index for sprite data table.

EBSpriteLoadLoop:
		LDA EndBossSPTiles,X	;($BB46)
		CMP #$FF				;($BB49)Look for end #$FF to see if at end of sprites.
		BNE EBSpriteSave		;($BB4B)#$FF found? If not, branch to get next byte.

		LDA EndBossSPTiles+1,X  ;($BB4D)Get next byte. Overwrites last byte. a bug.
		CMP #$FF				;($BB50)
		BEQ EBSpriteLoadDone	;($BB52)Second #$FF found? If not, branch to get next byte.

EBSpriteSave:
		STA SpriteRAM,X		 ;($BB54)Save sprite data byte.
		INX					 ;($BB57)Have all the sprite bytes been loaded?
		BNE EBSpriteLoadLoop	;($BB58)If not, branch to get more.

EBSpriteLoadDone:
		JSR WaitForNMI		  ;($BB5A)($FF74)Wait for VBlank interrupt.
LDA #%00011000		  ;
		STA PPUControl1		 ;($BB5F)Turn on sprites and background.

		LDA EndBossPal2Ptr	  ;($BB62)
		STA SpritePalettePointerLB;($BB65)Get sprite palette pointer for end boss.
		LDA EndBossPal2Ptr+1	;($BB67)
STA SpritePalettePointerUB		;

		LDA EndBossPal1Ptr	  ;($BB6C)
		STA BackgroundPalettePointerLB;($BB6F)Get background palette pointer for end boss.
		LDA EndBossPal1Ptr+1	;($BB71)
		STA BackgroundPalettePointerUB;($BB74)

		LDA #$00				;($BB76)
		STA ScrollX			 ;($BB78)Zero out the scroll registers.
		STA ScrollY			 ;($BB7A)
		STA ActiveNmTbl		 ;($BB7C)Use nametable 0.

		LDA #$08				;($BB7E)
		STA NTBlockX			;($BB80)Set block position to the center of the screen.
		LDA #$07				;($BB82)
STA NTBlockY			;

		LDA #SFX_FIRE		   ;($BB86)Fire SFX.
		BRK					 ;($BB88)
		.byte $04, $17		  ;($BB89)($81A0)InitMusicSFX, bank 1.

		LDA #EN_DRAGONLORD2	 ;($BB8B)Indicate fighting the end boss.
		STA EnemyNumber		 ;($BB8D)
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

		LDA #PAL_LOAD_BG		;($BB92)Indicate both sprite and background palettes will be written.
STA LoadBGPal		   ;

JSR PalFadeIn		   ;($C529)Fade in both background and sprite palettes.
		JSR PalFadeIn		   ;($BB99)($C529)Fade in both background and sprite palettes.
JSR PalFadeIn		   ;($C529)Fade in both background and sprite palettes.
		JSR PalFadeIn		   ;($BB9F)($C529)Fade in both background and sprite palettes.

		JSR WaitForNMI		  ;($BBA2)($FF74)Wait for VBlank interrupt.

		LDX #$28				;($BBA5)Wait 40 frames before continuing.
		* JSR WaitForNMI		;($BBA7)($FF74)Wait for VBlank interrupt.
		DEX					 ;($BBAA)
		BNE -				   ;($BBAB)Have 40 frames passed?
RTS					 ;If not, branch to wait another frame.

;----------------------------------------------------------------------------------------------------

LoadBufferRows:
		JSR WaitForNMI		  ;($BBAE)($FF74)Wait for VBlank interrupt.
		LDY #$20				;($BBB1)1 row is 32 tiles.

		* JSR LoadBufferByte	;($BBB3)($BBDF)Load a single byte into the nametable buffer.
		DEY					 ;($BBB6)
BNE -				   ;Has the whole row been loaded? If not, branch to do another byte.

		DEC BufferByteCounter   ;($BBB9)Move to next row.
		BNE LoadBufferRows	  ;($BBBB)Is there another row to load?
RTS					 ;If so, branch to to another row.

;----------------------------------------------------------------------------------------------------

		LDA NTBlockY			;($BBBE)
		ASL					 ;($BBC0)
		CLC					 ;($BBC1)
		ADC YPosFromCenter	  ;($BBC2)
		CLC					 ;($BBC4)
ADC #$1E				;
STA DivideNumber1LB		   ;
		LDA #$1E				;($BBC9)
		STA DivideNumber2	   ;($BBCB)Unused function.
JSR ByteDivide		  ;($C1F0)Divide a 16-bit number by an 8-bit number.
		LDA $40				 ;($BBD0)
		STA $3E				 ;($BBD2)
LDA NTBlockX			;
		ASL					 ;($BBD6)
		CLC					 ;($BBD7)
		ADC $0F				 ;($BBD8)
AND #$3F				;
		STA $3C				 ;($BBDC)
		RTS					 ;($BBDE)

;----------------------------------------------------------------------------------------------------

LoadBufferByte:
		TYA					 ;($BBDF)Save Y on the stack.
PHA					 ;

		LDA PPUAddrLB		   ;($BBE1)
		STA GenPtr22LB		  ;($BBE3)
LDA PPUAddrUB		   ;Get PPU address and minus #$1C to find the corresponding
		SEC					 ;($BBE7)point in the nametable buffer.
		SBC #$1C				;($BBE8)
		STA GenPtr22UB		  ;($BBEA)

		LDY #$00				;($BBEC)Zero out the offset.
		LDA PPUDataByte		 ;($BBEE)Store byte in the buffer.
		STA (GenPtr22),Y		;($BBF0)
		JSR AddPPUBufferEntry   ;($BBF2)($C690)Add data to PPU buffer.

		PLA					 ;($BBF5)
		TAY					 ;($BBF6)Restore Y from the stack.
RTS					 ;

;----------------------------------------------------------------------------------------------------

;The following table contains the background tiles used to make the end boss.
;There are three bytes per tile.  The first byte is the tile pattern.  The
;next two bytes are the PPU address for the tile pattern.

EndBossBGTiles:
		.byte $58, $2F, $21	 ;($BBF8)PPUAddress $212F.
		.byte $59, $4F, $21	 ;($BBFB)PPUAddress $214F.
		.byte $5A, $70, $21	 ;($BBFE)PPUAddress $2170.
		.byte $5B, $71, $21	 ;($BC01)PPUAddress $2171.
.byte $5C, $8E, $21	 ;PPUAddress $218E.
		.byte $5D, $8F, $21	 ;($BC07)PPUAddress $218F.
		.byte $5E, $90, $21	 ;($BC0A)PPUAddress $2190.
.byte $6A, $91, $21	 ;PPUAddress $2191.
		.byte $6B, $92, $21	 ;($BC10)PPUAddress $2192.
.byte $6C, $AE, $21	 ;PPUAddress $21AE.
		.byte $6D, $AF, $21	 ;($BC16)PPUAddress $21AF.
		.byte $6E, $B0, $21	 ;($BC19)PPUAddress $21B0.
		.byte $6F, $B1, $21	 ;($BC1C)PPUAddress $21B1.
.byte $70, $B2, $21	 ;PPUAddress $21B2.
		.byte $71, $B3, $21	 ;($BC22)PPUAddress $21B3.
.byte $72, $CE, $21	 ;PPUAddress $21CE.
		.byte $73, $CF, $21	 ;($BC28)PPUAddress $21CF.
.byte $0A, $D0, $21	 ;PPUAddress $21D0.
		.byte $0B, $D1, $21	 ;($BC2E)PPUAddress $21D1.
		.byte $91, $D3, $23	 ;($BC31)PPUAddress $23D3.
		.byte $C0, $DA, $23	 ;($BC34)PPUAddress $23DA.
.byte $EA, $DB, $23	 ;PPUAddress $23DB.
		.byte $02, $DC, $23	 ;($BC3A)PPUAddress $23DC.

;----------------------------------------------------------------------------------------------------

;The end boss uses all 64 sprites. 256 bytes total.  The sprites
;are loaded directly into sprite RAM without any processing.

EndBossSPTiles:
.byte $6F, $C0, $00, $80
		.byte $77, $C1, $00, $60;($BC41)
.byte $77, $C2, $00, $68
		.byte $77, $C3, $00, $70;($BC49)
.byte $77, $C4, $00, $78
		.byte $77, $C5, $00, $80;($BC51)
		.byte $7F, $C6, $00, $60;($BC55)
		.byte $7F, $C7, $00, $68;($BC59)
.byte $7F, $C8, $00, $70
		.byte $7F, $C9, $00, $78;($BC61)
		.byte $7F, $CA, $00, $80;($BC65)
		.byte $87, $CB, $00, $65;($BC69)
		.byte $87, $CC, $00, $6D;($BC6D)
		.byte $87, $CD, $00, $78;($BC71)
		.byte $87, $CE, $00, $80;($BC75)
		.byte $8A, $CF, $01, $61;($BC79)
		.byte $8E, $D0, $01, $74;($BC7D)
.byte $8F, $D1, $00, $64
		.byte $8F, $D2, $00, $6D;($BC85)
		.byte $8F, $D3, $00, $7B;($BC89)
		.byte $8F, $D4, $00, $83;($BC8D)
		.byte $92, $D5, $00, $8B;($BC91)
		.byte $94, $D6, $01, $8A;($BC95)
		.byte $97, $D7, $00, $83;($BC99)
		.byte $64, $D8, $01, $4E;($BC9D)
		.byte $60, $D9, $01, $56;($BCA1)
		.byte $68, $DA, $01, $56;($BCA5)
		.byte $5B, $DB, $01, $5E;($BCA9)
		.byte $63, $DC, $01, $5E;($BCAD)
		.byte $6B, $DD, $01, $5E;($BCB1)
		.byte $5B, $DE, $01, $66;($BCB5)
		.byte $63, $DF, $01, $66;($BCB9)
.byte $6B, $E0, $01, $66
.byte $6F, $E1, $00, $58
.byte $59, $E2, $01, $80
.byte $61, $E3, $01, $80
		.byte $6B, $E4, $01, $80;($BCCD)
		.byte $59, $E5, $01, $88;($BCD1)
		.byte $61, $E6, $01, $88;($BCD5)
		.byte $69, $E7, $01, $88;($BCD9)
.byte $5F, $E8, $01, $90
.byte $67, $E9, $01, $90
		.byte $67, $EA, $01, $98;($BCE5)
.byte $6F, $EB, $01, $8F
		.byte $3E, $EC, $02, $51;($BCED)
		.byte $3E, $ED, $02, $59;($BCF1)
.byte $46, $EE, $02, $4E
.byte $46, $EF, $02, $56
.byte $46, $F0, $02, $5E
.byte $40, $F1, $00, $68
		.byte $48, $F2, $00, $68;($BD05)
.byte $50, $F3, $00, $68
		.byte $47, $F4, $00, $70;($BD0D)
		.byte $4E, $F5, $02, $70;($BD11)
.byte $4F, $F6, $00, $70
.byte $47, $F7, $00, $78
.byte $4F, $F8, $00, $78
.byte $4A, $F9, $02, $7B
.byte $52, $FA, $02, $7B
.byte $4C, $FB, $02, $83
.byte $4F, $FC, $02, $8B
.byte $56, $FD, $03, $54
.byte $56, $FE, $03, $5C
		.byte $5E, $FF, $03, $5C;($BD39)A bug. Actually displays part of a 3. Where tail meets wing.
		.byte $FF, $FF		  ;($BD3D)Look at code under EBSpriteLoadLoop for reason why.

;----------------------------------------------------------------------------------------------------

EndBossPal1Ptr:
		.word EndBossPal1	   ;($BD3F)($BD41)Pointer to palette data below.
EndBossPal1:
		.byte $30, $0E, $30, $17, $15, $30, $21, $22, $27, $0F, $27, $27;($BD41)

EndBossPal2Ptr:
.word EndBossPal2	   ;($BD4F)Pointer to palette data below.
EndBossPal2:
		.byte $21, $22, $27, $17, $0C, $30, $07, $15, $30, $21, $27, $15;($BD4F)

;----------------------------------------------------------------------------------------------------

DoIntroGFX:
		JSR WaitForNMI		  ;($BD5B)($FF74)Wait for VBlank interrupt.
JSR LoadIntroPals	   ;($AA99)Load palettes for end fight.
		JSR ClearSpriteRAM	  ;($BD61)($C6BB)Clear sprite RAM.

LDA #%00001000		  ;Set sprite pattern table 1 and nametable 0.
		STA PPUControl0		 ;($BD66)

		LDA IntroGFXTblPtr+1	;($BD69)
STA DatPntrlUB		  ;Point to beginning of data table.
LDA IntroGFXTblPtr	  ;
		STA DatPntr1LB		  ;($BD71)

LDA #NT_NAMETBL0_UB	 ;
		STA PPUAddrUB		   ;($BD75)
STA PPUAddress		  ;Set PPU address to nametable 0.
LDA #NT_NAMETBL0_LB	 ;
STA PPUAddrLB		   ;
		STA PPUAddress		  ;($BD7E)

IntroGFXLoop:
JSR IntroGFXPtrInc	  ;($BDBF)Get nametable data.
		CMP #END_TXT_END		;($BD84)Check for end of data block indicator.
		BEQ ChkNTEnd			;($BD86)If found, branch to check if done.

CMP #END_RPT			;Check for repeated data indicator.
		BNE IncToNextByte	   ;($BD8A)Branch to skip if not repeating data.

JSR IntroGFXPtrInc	  ;($BDBF)Get number of times to repeat byte.
STA RepeatCounter	   ;Load number of times to repeat data byte.
		JSR IntroGFXPtrInc	  ;($BD91)($BDBF)Get nametable data.
		STA PPUDataByte		 ;($BD94)Store data byte to display.

		* JSR LoadGFXAndInc	 ;($BD96)($BDB3)Load byte on to nametable.
DEC RepeatCounter	   ;Decrement repeat counter.
BNE -				   ;Branch if more to repeat.
BEQ IntroGFXLoop		;Done repeating. Branch always.

IncToNextByte:
STA PPUDataByte		 ;Load byte into nametable.
JSR LoadGFXAndInc	   ;($BDB3)Load byte and increment pointer.
		JMP IntroGFXLoop		;($BDA4)Loop to get more data.

ChkNTEnd:
LDA PPUAddrUB		   ;
CMP #NT_NAMETBL1_UB	 ;Check to see if at the end of the nametable.
BNE IntroGFXLoop		;If not, branch to load more graphics.

LDA #%10001000		  ;
STA PPUControl0		 ;Turn VBlank interrupt back on and return.
RTS					 ;

LoadGFXAndInc:
LDA PPUDataByte		 ;Load nametable data into the PPU.
		STA PPUIOReg			;($BDB5)
INC PPUAddrLB		   ;
BNE +				   ;Increment to next address.
		INC PPUAddrUB		   ;($BDBC)
* RTS					 ;

IntroGFXPtrInc:
LDY #$00				;Load nametable data from PRG ROM.
		LDA (DatPntr1),Y		;($BDC1)
		INC DatPntr1LB		  ;($BDC3)
BNE +				   ;Increment pointer to next data byte.
INC DatPntrlUB		  ;
* RTS					 ;

;----------------------------------------------------------------------------------------------------

IntroGFXTblPtr:
.word IntroGFXTbl	   ;($BDCC)Pointer to beginning of table below.

IntroGFXTbl:
		.byte $F7, $80, $5F, $FC;($BDCC)4 rows of blank tiles.
.byte $F7, $20, $5F, $FC	;1 row of blank tiles.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $20, $AD, $FC;($BDD4)Dragon Warrior graphic starts here.

		.byte $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA;($BDD8)
.byte $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA
		.byte $FC			   ;($BDF8)

		.byte $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC;($BDF9)
		.byte $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC;($BE09)
		.byte $FC			   ;($BE19)

.byte $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA
.byte $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA
.byte $FC

.byte $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC
		.byte $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC;($BE4B)
.byte $FC

		.byte $A9, $AA, $A9, $74, $75, $76, $77, $78, $79, $7A, $7B, $7C, $7D, $7E, $7F, $80;($BE5C)
		.byte $81, $82, $83, $84, $85, $86, $85, $86, $87, $88, $89, $8A, $8B, $8C, $A9, $AA;($BE6C)
.byte $FC

		.byte $AB, $AC, $AB, $8D, $8E, $8F, $90, $91, $92, $93, $94, $95, $96, $97, $98, $99;($BE7D)
.byte $9A, $9B, $9C, $9D, $9E, $9F, $9E, $9F, $A0, $A1, $A2, $A3, $AB, $AC, $AB, $AC
		.byte $FC			   ;($BE9D)

.byte $A9, $AA, $A9, $AA, $A9, $AA, $A4, $A5, $A9, $A6, $A7, $AA, $A9, $AA, $A9, $AA
		.byte $A9, $A8, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA;($BEAE)
		.byte $FC			   ;($BEBE)

.byte $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC
.byte $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC
.byte $FC

		.byte $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA;($BEE0)
		.byte $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA, $A9, $AA;($BEF0)
		.byte $FC			   ;($BF00)

.byte $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC
.byte $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC, $AB, $AC
.byte $FC

		.byte $F7, $20, $AE, $FC;($BF22)Dragon Warrior graphic ends here.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $20, $5F, $FC;($BF26)1 row of blank tiles.
		.byte $F7, $20, $5F, $FC;($BF2A)1 row of blank tiles.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $0A, $5F	 ;($BF2E)10 blank tiles.
;			  -	P	U	S	H	_	S	T	A	R	T	-
.byte $63, $33, $38, $36, $2B, $5F, $36, $37, $24, $35, $37, $63
		.byte $F7, $0A, $5F, $FC;($BF3D)10 blank tiles.

;----------------------------------------------------------------------------------------------------

.byte $F7, $20, $5F, $FC	;1 row of blank tiles.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $0B, $5F	 ;($BF45)11 blank tiles.
;			 COPY  1	9	8	6	_	E	N	I	X
		.byte $62, $01, $09, $08, $06, $5F, $28, $31, $2C, $3B;($BF48)
		.byte $F7, $0B, $5F, $FC;($BF52)11 blank tiles.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $20, $5F, $FC;($BF56)1 row of blank tiles.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $0B, $5F	 ;($BF5A)11 blank tiles.
;			 COPY  1	9	8	9	_	E	N	I	X
		.byte $62, $01, $09, $08, $09, $5F, $28, $31, $2C, $3B;($BF5D)
		.byte $F7, $0B, $5F, $FC;($BF67)11 blank tiles.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $20, $5F, $FC;($BF6B)1 row of blank tiles.

;----------------------------------------------------------------------------------------------------

.byte $F7, $06, $5F		 ;6 blank tiles.
;			  L	I	C	E	N	S	E	D	_	T	O	_	N	I	N	T
		.byte $2F, $2C, $26, $28, $31, $36, $28, $27, $5F, $37, $32, $5F, $31, $2C, $31, $37;($BF72)
;			  E	N	D	O
		.byte $28, $31, $27, $32;($BF82)
		.byte $F7, $06, $5F, $FC;($BF86)6 blank tiles.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $20, $5F, $FC;($BF8A)1 row of blank tiles.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $04, $5F	 ;($BF8E)4 blank tiles.
;
; ROM Version difference: "TO" encoding differs between PRG0 and PRG1
; PRG0: $37, $32 (file offset 0x3FAE-0x3FAF)  <-- Original line
; PRG1: $32, $29 (file offset 0x3FAE-0x3FAF)  <-- Modified for PRG1
;
;			  T	M	_	T	R	A	D	E	M	A	R	K	_	T	O	_
IntroGFXTbl_Byte_BF91:  .byte $37, $30, $5F, $37, $35, $24, $27, $28, $30, $24, $35, $2E, $5F, $32, $29, $5F  ;PRG1 version
;IntroGFXTbl_Byte_BF91:  .byte $37, $30, $5F, $37, $35, $24, $27, $28, $30, $24, $35, $2E, $5F, $37, $32, $5F  ;PRG0 version (comment out for PRG1)
;			  N	I	N	T	E	N	D	O
.byte $31, $2C, $31, $37, $28, $31, $27, $32
		.byte $F7, $04, $5F, $FC;($BFA9)4 blank tiles.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $20, $5F, $FC;($BFAD)1 row of blank tiles.
.byte $F7, $20, $5F, $FC	;1 row of blank tiles.

;----------------------------------------------------------------------------------------------------

		.byte $F7, $08, $FF, $F7, $08, $05, $F7, $10, $00, $FC;($BFB5)1 row of attribute table data.
.byte $F7, $08, $A5, $F7, $08, $FF, $FC, $F7, $10, $FF, $FC ;1 row of attribute table data.

;----------------------------------------------------------------------------------------------------

;Unused.
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BFCA)

;----------------------------------------------------------------------------------------------------

NMI:
RESET:
IRQ:
SEI					 ;Disable interrupts.
IRQ_Count_BFD9:  INC MMCReset1		   ;Reset MMC1 chip.
IRQ_Jmp_BFDC:  JMP _DoReset			;($FF8E)Continue with the reset process.

;				   D	R	A	G	O	N	_	W	A	R	R	I	O	R	_
IRQ_Byte_BFDF:  .byte $80, $44, $52, $41, $47, $4F, $4E, $20, $57, $41, $52, $52, $49, $4F, $52, $20
IRQ_Byte_BFEF:  .byte $20, $56, $DE, $30, $70, $01, $04, $01, $0F, $07, $00

IRQ_Word_BFFA:  .word NMI			   ;($BFD8)NMI vector.
IRQ_Word_BFFC:  .word RESET			 ;($BFD8)Reset vector.
IRQ_Word_BFFE:  .word IRQ			   ;($BFD8)IRQ vector.