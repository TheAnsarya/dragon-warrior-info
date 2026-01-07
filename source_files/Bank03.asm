.org $C000

.include "Dragon_Warrior_Defines.asm"

;--------------------------------------[ Forward Declarations ]--------------------------------------

.alias BankPointers			 $8000
.alias UpdateSound			  $8028
.alias NPCMobilePointerTable	$9734
.alias NPCStaticPointerTable	$974C
.alias MapEntryDirectionTable   $9914
.alias ItemCostTable			$9947
.alias KeyCostTable			 $9989
.alias InnCostTable			 $998C
.alias ShopItemsTable		   $9991
.alias WeaponsBonusTable		$99CF
.alias ArmorBonusTable		  $99D7
.alias ShieldBonusTable		 $99DF
.alias BlackPalPointer			  $9A18
.alias OverworldPalPointer		  $9A1A9A1A
.alias TownPalPointer			   $9A1C
.alias RedFlashPalPointer		   $9A229A22
.alias RegSPPalPointer			  $9A24
.alias SplFlshBGPalPointer		  $9A269A26
.alias BadEndBGPalPointer		   $9A28
.alias EnSPPalsPointer			  $9A2A
.alias CombatBckgndGFX		  $9C8F
.alias SpellCostTable		   $9D53
.alias ClearWinBufferRAM2		  $A788
.alias RemoveWindow			 $A7A2
.alias GetBlockID			   $AC17
.alias ModMapBlock			  $AD66
.alias MapChngFadeNoSound	   $B08D
.alias MapChngNoSound		   $B091
.alias MapChngWithSound		 $B097
.alias ResumeMusicTable		 $B1AE
.alias ChkSpecialLoc			$B219
.alias CheckMapExit			 $B228
.alias DoJoyRight			   $B252
.alias PostMoveUpdate		   $B30E
.alias DoJoyLeft				$B34C
.alias DoJoyDown				$B3D8
.alias DoJoyUp				  $B504
.alias SpriteFacingBaseAddress	   $B6C2
.alias DoSprites				$B6DA
.alias DoIntroGFX			   $BD5B

;-----------------------------------------[ Start of code ]------------------------------------------

		JSR $C5E0			   ;($C000)Not used.
		JMP $C009			   ;($C003)

;----------------------------------------------------------------------------------------------------

ModAttribBits:
		JSR CalcAttribAddr	  ;($C006)($C5E4)Calculate attribute table address for given nametable byte.

		TYA					 ;($C009)Save the value of Y on the stack.
		PHA					 ;($C00A)

		LDA NTYPos			  ;($C00B)
		AND #$02				;($C00D)
		ASL					 ;($C00F)Load bit shift counter with proper index to bit pair to
		STA GenByte3D		   ;($C010)change in the attribute table(0, 2, 4 or 6).
		LDA NTXPos			  ;($C012)
		AND #$02				;($C014)
		CLC					 ;($C016)
		ADC GenByte3D		   ;($C017)
		TAY					 ;($C019)

		LDA #$FC				;($C01A)Load bitmask for clearing selected nametable bits.
		CPY #$00				;($C01C)Is bit counter 0?
		BEQ SetAttribBits	   ;($C01E)If so, branch. No need to do any shifting.

AttributeLoop:
		SEC					 ;($C020)
		ROL					 ;($C021)This loop shifts the attribute tabe bit pair into position
		ASL PPUDataByte		 ;($C022)while decrementing the counter.
		DEY					 ;($C024)Do attribute table bits still need to be shifted?
		BNE AttributeLoop	   ;($C025)If so, branch to shift them 1 more bit.

SetAttribBits:
		AND (PPUBufferPointer),Y;($C027)
		ORA PPUDataByte		 ;($C029)Update the attribute table byte in both the PPU buffer and
		STA (PPUBufferPointer),Y;($C02B)the PPU data byte.
		STA PPUDataByte		 ;($C02D)

		PLA					 ;($C02F)
		TAY					 ;($C030)Restore the value of Y from the stack and exit.
		RTS					 ;($C031)

;----------------------------------------------------------------------------------------------------

NPCNewDirection:
		CMP #DIR_UP			 ;($C032)Is player facing up?
		BNE CheckPlayerRight	;($C034)If not, branch to check if facing right.
		LDA #DIR_DOWN		   ;($C036)Set NPC facing down.
		RTS					 ;($C038)

CheckPlayerRight:
		CMP #DIR_RIGHT		  ;($C039)Is player facing right?
		BNE CheckPlayerDown	 ;($C03B)If not, branch to check if facing down.
		LDA #DIR_LEFT		   ;($C03D)Set NPC facing left.
		RTS					 ;($C03F)

CheckPlayerDown:
		CMP #DIR_DOWN		   ;($C040)Is player facing down?
		BNE PlayerLeft		  ;($C042)If not, branch. Player must be facing left.
		LDA #DIR_UP			 ;($C044)Set NPC facing up.
		RTS					 ;($C046)

PlayerLeft:
		LDA #DIR_RIGHT		  ;($C047)Player must be facing left.
		RTS					 ;($C049)Set NPC facing right.

;----------------------------------------------------------------------------------------------------

NPCFacePlayer:
		STA NPCNumber		   ;($C04A)Save a copy of the NPC index.
		TYA					 ;($C04C)
		PHA					 ;($C04D)Save a copy of Y and X on the stack.
		TXA					 ;($C04E)
		PHA					 ;($C04F)

		LDX NPCNumber		   ;($C050)Get index to NPC data.
		LDA CharDirection	   ;($C052)Load player's direction.
		JSR NPCNewDirection	 ;($C055)($C032)Get direction NPC should face to talk to player.
		STA NPCNewFace		  ;($C058)Save value of new NPC's direction.

		LSR					 ;($C05A)
		ROR					 ;($C05B)Move NPC facing bits into the proper location(Bits 5 and 6).
		ROR					 ;($C05C)
		ROR					 ;($C05D)
		STA GenByte24		   ;($C05E)Save the bits temporarily.

		LDA NPCYPos,X		   ;($C060)
		AND #$9F				;($C062)Remove existing NPC direction bits.
		ORA GenByte24		   ;($C064)OR in the new direction bits.
		STA NPCYPos,X		   ;($C066)

		LDA #$00				;($C068)Need to loop twice. Once for NPCs right next to player
		STA NPCSpriteCounter	;($C06A)and once for NPCs behind counters.

		LDY SpriteRAM		   ;($C06C)Get player's Y sprite position.
		LDX SpriteRAM+3		 ;($C06F)Get player's X sprite position.

CheckPlayerDirection:
		LDA CharDirection	   ;($C072)Is player facing up?
		BNE CheckPlayerRight	;($C075)If not, branch to check other player directions.

		TYA					 ;($C077)
		SEC					 ;($C078)Player is facing up. Prepare to search for NPC data
		SBC #$10				;($C079)that is above player.
		TAY					 ;($C07B)
		JMP CheckNPCPosition	;($C07C)

CheckPlayerRight:
		CMP #DIR_RIGHT		  ;($C07F)Is player facing right?
		BNE CheckPlayerDown	 ;($C081)If not, branch to check other player directions.

		TXA					 ;($C083)
		CLC					 ;($C084)Player is facing right. Prepare to search for NPC data
		ADC #$10				;($C085)that is right of player.
		TAX					 ;($C087)
		JMP CheckNPCPosition	;($C088)

CheckPlayerDown:
		CMP #DIR_DOWN		   ;($C08B)Is player facing down?
		BNE PlayerLeft		  ;($C08D)If not, branch. Player must be facing left.

		TYA					 ;($C08F)
		CLC					 ;($C090)Player is facing down. Prepare to search for NPC data
		ADC #$10				;($C091)that is below player.
		TAY					 ;($C093)
		JMP CheckNPCPosition	;($C094)

PlayerLeft:
		TXA					 ;($C097)
		SEC					 ;($C098)Player is facing left. Prepare to search for NPC data
		SBC #$10				;($C099)that is left of player.
		TAX					 ;($C09B)

CheckNPCPosition:
		STX NPCXCheck		   ;($C09C)Save X and Y position data of NPC to change.
		STY NPCYCheck		   ;($C09E)

		LDY #$10				;($C0A0)Prepare to search the NPC sprites for location.

NPCSearchLoop:
		LDA SpriteRAM,Y		 ;($C0A2)Has the sprite Y data for the desired NPC been found?
		CMP NPCYCheck		   ;($C0A5)
		BNE +				   ;($C0A7)If not, branch to move the the next NPC sprite data.

		LDA SpriteRAM+3,Y	   ;($C0A9)Has the sprite X data for the desired NPC been found?
		CMP NPCXCheck		   ;($C0AC)
		BEQ NPCFound			;($C0AE)If not, branch to move the the next NPC sprite data.

		* TYA				   ;($C0B0)This is not the sprite data for the desired NPC.
		CLC					 ;($C0B1)Move to the next set of NPC sprite data.
		ADC #$10				;($C0B2)4 bytes of data and 4 sprites per NPC = 16 bytes.

		TAY					 ;($C0B4)Has all the sprite data been searched?
		BNE NPCSearchLoop	   ;($C0B5)If not, branch to check more sprite data.

		LDX NPCXCheck		   ;($C0B7)Reload the NPC X and Y position data.
		LDY NPCYCheck		   ;($C0B9)

		LDA NPCSpriteCounter	;($C0BB)Is this the second time through the search loop?
		BNE NPCDirEnd		   ;($C0BD)If so, branch to end. NPC not found.

		LDA #$01				;($C0BF)Prepare to run the loop a second time.
		STA NPCSpriteCounter	;($C0C1)
		JMP CheckPlayerDirection;($C0C3)($C072)Need to check for NPCs behind counters.

NPCFound:
		STY NPCSpriteRAMIndex   ;($C0C6)NPC sprites found. Save index to sprites.

		LDA #$04				;($C0C8)Prepare to process 4 sprites for this NPC.
		STA NPCSpriteCounter	;($C0CA)

		LDX NPCNumber		   ;($C0CC)
		JSR GetNPCSpriteIndex   ;($C0CE)($C0F4)Get index into sprite pattern table for NPC.

		TAY					 ;($C0D1)Load index to NPC ROM data.
		LDA NPCNewFace		  ;($C0D2)Get new direction NPC will face.
		JSR SpriteFacingBaseAddress;($C0D4)($B6C2)Calculate entry into char data table based on direction.
		LDX NPCSpriteRAMIndex   ;($C0D7)Load sprite RAM index for current NPC sprite.

NPCLoadNxtSprt:
		LDA (GenPtr22),Y		;($C0D9)Load tile data for NPC sprite.
		STA SpriteRAM+1,X	   ;($C0DB)

		INY					 ;($C0DE)
		LDA (GenPtr22),Y		;($C0DF)Load attribute data for NPC sprite.
		DEY					 ;($C0E1)
		STA SpriteRAM+2,X	   ;($C0E2)

		INX					 ;($C0E5)
		INX					 ;($C0E6)Increment to next sprite in sprite RAM.
		INX					 ;($C0E7)
		INX					 ;($C0E8)

		INY					 ;($C0E9)Have 4 sprites been processed for this NPC?
		INY					 ;($C0EA)
		DEC NPCSpriteCounter	;($C0EB)
		BNE NPCLoadNxtSprt	  ;($C0ED)If not, branch to load more sprite data.

NPCDirEnd:
		PLA					 ;($C0EF)
		TAX					 ;($C0F0)
		PLA					 ;($C0F1)Restore X and Y from the stack.
		TAY					 ;($C0F2)
		RTS					 ;($C0F3)

;----------------------------------------------------------------------------------------------------

;3 NPCs types change depending on the map and game flag. Those types are listed below:
;%101 = Wizard or Dragonlord.
;%110 = Princess Gwaelin or Female villager.
;%111 = Stationary guard or Guard with trumpet.
;The following function looks at the map number and game flags to determine which NPC type to use.

GetNPCSpriteIndex:
		LDA NPCXPos,X		   ;($C0F4)Get NPC type.
		AND #$E0				;($C0F6)

		LSR					 ;($C0F8)/2 to get initial offset into sprite pattern table.
		STA GenByte24		   ;($C0F9)

		CMP #$60				;($C0FB)Is this the princess or a female villager?
		BNE ChkWizardNPC		;($C0FD)If not, branch to check for dragonlord/wizard NPC.

		LDA MapNumber		   ;($C0FF)Is the current map the ground floor of Tantagel castle?
		CMP #MAP_TANTCSTL_GF	;($C101)
		BNE ChkThroneRoomNPC	;($C103)If not, branch to check next map.

		LDA StoryFlags		  ;($C105)Is the dragonlord dead?
		AND #F_DGNLRD_DEAD	  ;($C107)
		BNE SetPrincessNPC	  ;($C109)If so, branch to get princess NPC sprites.

ChkThroneRoomNPC:
		LDA MapNumber		   ;($C10B)Is the current map the throne room?
		CMP #MAP_THRONEROOM	 ;($C10D)
		BNE NPCWalkAnim		 ;($C10F)If not, branch. Get female villager NPC sprites.

SetPrincessNPC:
		LDA #$D0				;($C111)Load index to princess sprites.
		STA GenByte24		   ;($C113)
		BNE NPCWalkAnim		 ;($C115)Branch always.

ChkWizardNPC:
		LDA GenByte24		   ;($C117)Is this the dragon lord or wizard NPC?
		CMP #$50				;($C119)
		BNE ChkGuardNPC		 ;($C11B)If not, branch to check for guard type NPC.

		LDA MapNumber		   ;($C11D)Is the current map the ground floor of Tantagel castle?
		CMP #MAP_TANTCSTL_GF	;($C11F)
		BNE ChkDrgnLordNPC	  ;($C121)If not, branch to check for dragonlord NPC sprites.

		LDA StoryFlags		  ;($C123)Is the dragonlord dead?
		AND #F_DGNLRD_DEAD	  ;($C125)
		BEQ ChkDrgnLordNPC	  ;($C127)If not, branch to check for dragonlord NPC sprites.

		LDA #$F0				;($C129)Load index to wizard sprites.
		STA GenByte24		   ;($C12B)

GetGuardType:
		LDA DisplayedLevel	  ;($C12D)Has the end of the game just been reached?
		CMP #$FF				;($C12F)If so, change guards to guards with trumpets.
		BNE EndNPCSpclType	  ;($C131)

		LDA GenByte24		   ;($C133)
		ORA #$08				;($C135)Get offset to guards with trumpets.
		STA GenByte24		   ;($C137)
		BNE EndNPCSpclType	  ;($C139)Branch always.

ChkDrgnLordNPC:
		LDA MapNumber		   ;($C13B)Is the current map the basement of the dragonlord's castle?
		CMP #MAP_DLCSTL_BF	  ;($C13D)
		BNE NPCWalkAnim		 ;($C13F)If not, branch. Get wizard NPC sprites.

		LDA #$E0				;($C141)Load index to dragonlord sprites.
		STA GenByte24		   ;($C143)
		BNE NPCWalkAnim		 ;($C145)Branch always.

ChkGuardNPC:
		CMP #$70				;($C147)Is this a guard NPC?
		BEQ GetGuardType		;($C149)If so, branch to see if its a trumpet guard.

NPCWalkAnim:
		LDA CharLeftRight	   ;($C14B)
		AND #$08				;($C14D)Add the offset for left or right walking version of NPC.
		ORA GenByte24		   ;($C14F)
		STA GenByte24		   ;($C151)

EndNPCSpclType:
		LDA GenByte24		   ;($C153)Transfer final offset to A.
		RTS					 ;($C155)

;----------------------------------------------------------------------------------------------------

GetPlayerStatPtr:
		LDX #$3A				;($C156)Start at level 30 and point to the end of LevelUpTable.
		LDA #LEVEL_30		   ;($C158)Work backwards to find the proper level.
		STA DisplayedLevel	  ;($C15A)

PlayerStatLoop:
		LDA ExpLB			   ;($C15C)
		SEC					 ;($C15E)Subtract entries in LevelUpTable from player's current exp.
		SBC LevelUpTable,X	  ;($C15F)
		LDA ExpUB			   ;($C162)
		SBC LevelUpTable+1,X	;($C164)Has the correct level for the player been found?
		BCS PlayerStatEnd	   ;($C167)If so, branch to the exit.

		DEC DisplayedLevel	  ;($C169)Move down to the next level and stats table entry.
		DEX					 ;($C16B)
		DEX					 ;($C16C)Are there more levels to descend through?
		BNE PlayerStatLoop	  ;($C16D)If so, loop to check next level down.

PlayerStatEnd:
		RTS					 ;($C16F)End get player stats function.

;----------------------------------------------------------------------------------------------------

WaitMultiNMIs:
		STA GenByte24		   ;($C170)Save number of frames to wait.
		* JSR WaitForNMI		;($C172)($FF74)Wait for VBlank interrupt.
		DEC GenByte24		   ;($C175)Have the defined number of frames passed?
		BPL -				   ;($C177)If not, branch to wait another frame.
		RTS					 ;($C179)

;----------------------------------------------------------------------------------------------------

ClearPPU:
		PHA					 ;($C17A)
		TXA					 ;($C17B)
		PHA					 ;($C17C)Save A, X and Y.
		TYA					 ;($C17D)
		PHA					 ;($C17E)

		JSR WaitForNMI		  ;($C17F)($FF74)Wait for VBlank interrupt.
		LDA #%00001000		  ;($C182)Turn off VBlank interrupt.
		STA PPUControl0		 ;($C184)

		LDA #TL_BLANK_TILE1	 ;($C187)Fill both nametables with blank tiles.
		STA PPUDataByte		 ;($C189)

		LDA PPUStatusus		 ;($C18B)Reset address latch.

		LDA #NT_NAMETBL0_UB	 ;($C18E)
		STA PPUAddress		  ;($C190)Set address to start of nametable 0.
		LDA #NT_NAMETBL0_LB	 ;($C193)
		STA PPUAddress		  ;($C195)

		JSR ClearNameTable	  ;($C198)($C1B9)Write #$5F to nametable 0.

		LDA PPUStatusus		 ;($C19B)Reset address latch.

		LDA #NT_NAMETBL1_UB	 ;($C19E)
		STA PPUAddress		  ;($C1A0)Set address to start of nametable 1.
		LDA #NT_NAMETBL1_LB	 ;($C1A3)
		STA PPUAddress		  ;($C1A5)

		JSR ClearNameTable	  ;($C1A8)($C1B9)Write #$5F to nametable 1.

		LDA #%10001000		  ;($C1AB)Turn on VBlank interrupt.
		STA PPUControl0		 ;($C1AD)

		JSR WaitForNMI		  ;($C1B0)($FF74)Wait for VBlank interrupt.

		PLA					 ;($C1B3)
		TAY					 ;($C1B4)
		PLA					 ;($C1B5)Restore A, X and Y.
		TAX					 ;($C1B6)
		PLA					 ;($C1B7)
		RTS					 ;($C1B8)

;----------------------------------------------------------------------------------------------------

ClearNameTable:
		LDA PPUDataByte		 ;($C1B9)
		LDX #$1E				;($C1BB)

ClearNTOuterLoop:
		LDY #$20				;($C1BD)
		* STA PPUIOReg		  ;($C1BF)
		DEY					 ;($C1C2)Load a blank tile into every address of selected nametable.
		BNE -				   ;($C1C3)
		DEX					 ;($C1C5)
		BNE ClearNTOuterLoop	;($C1C6)
		RTS					 ;($C1C8)

;----------------------------------------------------------------------------------------------------

WordMultiply:
		LDA #$00				;($C1C9)
		STA MultiplyResultLB	;($C1CB)Clear results variables.
		STA MultiplyResultUB	;($C1CD)

MultiplyLoop:
		LDA MultiplyNumber1LB   ;($C1CF)
		ORA MultiplyNumber1UB   ;($C1D1)
		BEQ MultEnd			 ;($C1D3)
		LSR MultiplyNumber1UB   ;($C1D5)
		ROR MultiplyNumber1LB   ;($C1D7)This function multiplies the two
		BCC +				   ;($C1D9)16-bit numbers stored in $3C,$3D
		LDA MultiplyNumber2LB   ;($C1DB)and $3E, $3F and stores the results
		CLC					 ;($C1DD)in $40,$41.
		ADC MultiplyResultLB	;($C1DE)
		STA MultiplyResultLB	;($C1E0)
		LDA MultiplyNumber2UB   ;($C1E2)
		ADC MultiplyResultUB	;($C1E4)
		STA MultiplyResultUB	;($C1E6)
		* ASL MultiplyNumber2LB ;($C1E8)
		ROL MultiplyNumber2UB   ;($C1EA)
		JMP MultiplyLoop		;($C1EC)

MultEnd:
		RTS					 ;($C1EF)Done multiplying.

;----------------------------------------------------------------------------------------------------

ByteDivide:
		LDA #$00				;($C1F0)Set upper byte of dividend to 0
		STA DivideNumber1UB	 ;($C1F2)When only doing 8-bit division.

WordDivide:
		LDY #$10				;($C1F4)
		LDA #$00				;($C1F6)

DivLoop:
		ASL DivideNumber1LB	 ;($C1F8)
		ROL DivideNumber1UB	 ;($C1FA)
		STA DivideRemainder	 ;($C1FC)
		ADC DivideRemainder	 ;($C1FE)
		INC DivideQuotient	  ;($C200)This function takes a 16-bit dividend
		SEC					 ;($C202)stored in $3C,$3D and divides it by
		SBC DivideNumber2	   ;($C203)an 8-bit number stored in $3E.
		BCS +				   ;($C205)
		CLC					 ;($C207)The 8-bit quotient is stored in $3C and
		ADC DivideNumber2	   ;($C208)the 8-bit remainder is stored in $40.
		DEC DivideQuotient	  ;($C20A)
		* DEY				   ;($C20C)
		BNE DivLoop			 ;($C20D)
		STA DivideRemainder	 ;($C20F)
		RTS					 ;($C211)

;----------------------------------------------------------------------------------------------------

PalFadeOut:
		LDA #$00				;($C212)Start at brightest palette.
		STA PalModByte		  ;($C214)

FadeOutLoop:
		LDX #$04				;($C216)Prepare to wait for 4 frames.
		* JSR WaitForNMI		;($C218)($FF74)Wait for VBlank interrupt.
		DEX					 ;($C21B)
		BNE -				   ;($C21C)Has 4 frames elapsed? If not, branch to wait another frame.

		LDA SpritePalettePointerLB;($C21E)
		STA PalettePointerLB	;($C220)Load sprite palette pointers.
		LDA SpritePalettePointerUB;($C222)
		STA PalettePointerUB	;($C224)
		JSR PrepSPPalLoad	   ;($C226)($C632)Load sprite palette data into PPU buffer.

		LDA LoadBGPal		   ;($C229)Is background palette supposed to change?
		BEQ +				   ;($C22B)If not, branch to skip.

		LDA BackgroundPalettePointerLB;($C22D)
		STA PalettePointerLB	;($C22F)Load background palette pointers.
		LDA BackgroundPalettePointerUB;($C231)
		STA PalettePointerUB	;($C233)
		JSR PrepBGPalLoad	   ;($C235)($C63D)Load background palette data into PPU buffer

		* LDA PalModByte		;($C238)
		CLC					 ;($C23A)Move to next palette.
		ADC #$10				;($C23B)
		STA PalModByte		  ;($C23D)

		CMP #$50				;($C23F)Has the fade out effect completed?
		BNE FadeOutLoop		 ;($C241)If not, branch to load the next palette in the sequence.
		RTS					 ;($C243)

;----------------------------------------------------------------------------------------------------

ClearAttribByte:
		LDA NTBlockX			;($C244)Get the offset for the current block in the nametable row.
		ASL					 ;($C246)*2. 2 tiles per block.
		CLC					 ;($C247)
		ADC XPosFromCenter	  ;($C248)Column position of tile(0-63).
		AND #$3F				;($C24A)Max. 64 tiles in a row spanning the 2 nametables.
		PHA					 ;($C24C)Save row position on the stack.

		LDA NTBlockY			;($C24D)Get the offset for the current block in the nametable column.
		ASL					 ;($C24F)*2. 2 tiles per block.
		CLC					 ;($C250)
		ADC YPosFromCenter	  ;($C251)Row position(0-30).
		CLC					 ;($C253)
		ADC #$1E				;($C254)Ensure dividend is positive since YPosFromCenter is signed.

		STA DivideNumber1LB	 ;($C256)
		LDA #$1E				;($C258)Divide by 30 to get proper nametable row to update.
		STA DivideNumber2	   ;($C25A)
		JSR ByteDivide		  ;($C25C)($C1F0)Divide a 16-bit number by an 8-bit number.

		LDA DivideRemainder	 ;($C25F)
		STA NTYPos			  ;($C261)Store row position.
		PLA					 ;($C263)Restore A from stack.

		STA NTXPos			  ;($C264)Store column position.
		JSR PrepClearAttrib	 ;($C266)($C270)Calculate attribute table byte for blanking tiles.
		RTS					 ;($C269)

		JSR $C5E0			   ;($C26A)Not used.
		JMP ClearAttrib		 ;($C26D)($C273)Set black palette for given tiles.

PrepClearAttrib:
		JSR CalcAttribAddr	  ;($C270)($C5E4)Calculate attribute table address for given nametable byte.

ClearAttrib:
		TYA					 ;($C273)Save Y to stack.
		PHA					 ;($C274)

		LDY #$00				;($C275)
		LDA (PPUBufferPointer),Y;($C277)Clear calculated attribute table byte.
		STA PPUDataByte		 ;($C279)

		PLA					 ;($C27B)Restore Y from the stack.
		TAY					 ;($C27C)

		LDA PPUAddrUB		   ;($C27D)
		CLC					 ;($C27F)Add in upper nibble of upper address byte.
		ADC #$20				;($C280)
		STA PPUAddrUB		   ;($C282)

		JSR AddPPUBufferEntry   ;($C284)($C690)Add data to PPU buffer.
		RTS					 ;($C287)

;----------------------------------------------------------------------------------------------------

;This section appears to be unused code from Dragon Quest.

		.byte $20, $74, $FF, $20, $97, $C2, $E6, $99, $D0, $F9, $E6, $9A, $4C, $8B, $C2, $A5;($C288)
		.byte $D6, $F0, $0B, $C6, $D6, $A5, $99, $C6, $99, $A8, $D0, $02, $C6, $9A, $A0, $00;($C298)
		.byte $B1, $99, $C9, $F7, $D0, $13, $C8, $B1, $99, $85, $D6, $A5, $99, $18, $69, $03;($C2A8)
		.byte $85, $99, $90, $02, $E6, $9A, $4C, $97, $C2, $C9, $FF, $F0, $31, $C9, $FC, $D0;($C2B8)
		.byte $30, $A5, $0C, $18, $69, $40, $85, $0C, $85, $42, $A5, $0D, $69, $00, $85, $0D;($C2C8)
		.byte $85, $43, $A5, $9D, $85, $97, $E6, $98, $E6, $98, $A5, $98, $C9, $1E, $D0, $06;($C2D8)
		.byte $A9, $00, $85, $98, $F0, $08, $C9, $1F, $D0, $04, $A9, $01, $85, $98, $68, $68;($C2E8)
		.byte $60, $C9, $FE, $D0, $03, $20, $C9, $C2, $C9, $FB, $D0, $25, $A5, $E5, $0A, $0A;($C2F8)
		.byte $0A, $85, $3C, $0A, $65, $3C, $69, $03, $AA, $A9, $01, $85, $02, $A5, $02, $20;($C308)
		.byte $74, $FF, $D0, $F9, $20, $08, $C6, $A5, $47, $29, $08, $D0, $EC, $CA, $D0, $E9;($C318)
		.byte $60, $C9, $FD, $D0, $13, $A5, $99, $85, $9B, $A5, $9A, $85, $9C, $A9, $A3, $85;($C328)
		.byte $99, $A9, $00, $85, $9A, $4C, $74, $C4, $C9, $FA, $D0, $09, $A5, $9B, $85, $99;($C338)
		.byte $A5, $9C, $85, $9A, $60, $C9, $F0, $D0, $31, $C8, $B1, $99, $85, $3E, $C8, $B1;($C348)
		.byte $99, $85, $3F, $98, $48, $A0, $00, $84, $3D, $B1, $3E, $85, $3C, $68, $A8, $20;($C358)
		.byte $C9, $C6, $A5, $99, $18, $69, $02, $85, $9B, $A5, $9A, $69, $00, $85, $9C, $A9;($C368)
		.byte $00, $85, $9A, $A9, $B1, $85, $99, $4C, $74, $C4, $C9, $F1, $D0, $38, $20, $8C;($C378)
		.byte $C3, $4C, $74, $C4, $C8, $B1, $99, $85, $3E, $C8, $B1, $99, $85, $3F, $98, $48;($C388)
		.byte $A0, $00, $B1, $3E, $85, $3C, $C8, $B1, $3E, $85, $3D, $68, $A8, $20, $C9, $C6;($C398)
		.byte $A5, $99, $18, $69, $02, $85, $9B, $A5, $9A, $69, $00, $85, $9C, $A9, $00, $85;($C3A8)
		.byte $9A, $A9, $AF, $85, $99, $60, $C9, $F3, $D0, $13, $20, $8C, $C3, $A0, $00, $B1;($C3B8)
		.byte $99, $C9, $5F, $D0, $05, $E6, $99, $4C, $C7, $C3, $4C, $74, $C4, $C9, $F2, $D0;($C3C8)
		.byte $13, $A5, $99, $85, $9B, $A5, $9A, $85, $9C, $A9, $00, $85, $9A, $A9, $B5, $85;($C3D8)
		.byte $99, $4C, $74, $C4, $C9, $6D, $90, $3D, $E9, $6D, $AA, $E8, $AD, $50, $F1, $85;($C3E8)
		.byte $3C, $AD, $51, $F1, $85, $3D, $A0, $00, $B1, $3C, $C9, $FA, $F0, $04, $C8, $4C;($C3F8)
		.byte $00, $C4, $CA, $F0, $0D, $98, $38, $65, $3C, $85, $3C, $90, $02, $E6, $3D, $4C;($C408)
		.byte $FE, $C3, $A5, $99, $85, $9B, $A5, $9A, $85, $9C, $A5, $3C, $85, $99, $A5, $3D;($C418)
		.byte $85, $9A, $4C, $74, $C4, $C9, $57, $F0, $03, $4C, $74, $C4, $A5, $D4, $18, $69;($C428)
		.byte $09, $29, $3F, $85, $97, $A9, $00, $85, $4F, $20, $08, $C6, $A5, $47, $29, $03;($C438)
		.byte $F0, $04, $A9, $5F, $D0, $08, $A5, $4F, $29, $10, $D0, $F6, $A9, $57, $85, $08;($C448)
		.byte $20, $74, $FF, $20, $F5, $C4, $20, $90, $C6, $A5, $47, $29, $03, $F0, $DA, $A9;($C458)
		.byte $85, $00, $04, $17, $A5, $D4, $85, $97, $20, $EC, $C7, $60, $A0, $00, $B1, $99;($C468)
		.byte $85, $08, $A5, $09, $F0, $08, $C9, $01, $F0, $04, $A5, $08, $91, $42, $20, $F5;($C478)
		.byte $C4, $20, $90, $C6, $A0, $01, $B1, $99, $C9, $F8, $F0, $0A, $C9, $F9, $D0, $52;($C488)
		.byte $A9, $52, $85, $08, $D0, $04, $A9, $51, $85, $08, $E6, $99, $D0, $02, $E6, $9A;($C498)
		.byte $A5, $42, $18, $69, $E0, $85, $42, $B0, $02, $C6, $43, $A5, $09, $F0, $0A, $C9;($C4A8)
		.byte $01, $F0, $06, $A5, $08, $A0, $00, $91, $42, $A5, $42, $18, $69, $20, $85, $42;($C4B8)
		.byte $90, $02, $E6, $43, $C6, $98, $A5, $98, $C9, $FF, $D0, $04, $A9, $1D, $85, $98;($C4C8)
		.byte $20, $F5, $C4, $20, $90, $C6, $E6, $98, $A5, $98, $C9, $1E, $D0, $04, $A9, $00;($C4D8)
		.byte $85, $98, $E6, $42, $E6, $97, $A5, $97, $29, $3F, $85, $97, $60, $A5, $08, $48;($C4E8)
		.byte $A5, $09, $C9, $01, $F0, $1C, $A5, $98, $4A, $B0, $17, $A5, $97, $4A, $B0, $12;($C4F8)
		.byte $A5, $97, $85, $3C, $A5, $98, $85, $3E, $A9, $00, $85, $08, $20, $06, $C0, $20;($C508)
		.byte $73, $C2, $68, $85, $08, $A5, $97, $85, $3C, $A5, $98, $85, $3E, $20, $AA, $C5;($C518)
		.byte $60			   ;($C528)

;----------------------------------------------------------------------------------------------------

PalFadeIn:
		LDA #$30				;($C529)Prepare to switch through 4 different palettes.
		STA PalModByte		  ;($C52B)This will create a screen fade in effect.

FadeInLoop:
		LDX #$04				;($C52D)Prepare to pause for 4 frames.
		* JSR WaitForNMI		;($C52F)($FF74)Wait for VBlank interrupt.
		DEX					 ;($C532)Have 4 frames passed?
		BNE -				   ;($C533)If not, branch to wait another frame.

		LDA SpritePalettePointerLB;($C535)
		STA PalettePointerLB	;($C537)Load base address of desired sprite palette data.
		LDA SpritePalettePointerUB;($C539)
		STA PalettePointerUB	;($C53B)
		JSR PrepSPPalLoad	   ;($C53D)($C632)Load sprite palette data into PPU buffer.

		LDA LoadBGPal		   ;($C540)Does background need to be faded in?
		BEQ +				   ;($C542)If not, branch to skip.

		LDA BackgroundPalettePointerLB;($C544)
		STA PalettePointerLB	;($C546)Load base address of desired background palette data.
		LDA BackgroundPalettePointerUB;($C548)
		STA PalettePointerUB	;($C54A)
		JSR PrepBGPalLoad	   ;($C54C)($C63D)Load background palette data into PPU buffer

		* LDA PalModByte		;($C54F)
		SEC					 ;($C551)Decrement palette fade in counter.
		SBC #$10				;($C552)
		STA PalModByte		  ;($C554)

		CMP #$F0				;($C556)Is fade in complete?
		BNE FadeInLoop		  ;($C558)If not, branch to continue fade in routine.
		RTS					 ;($C55A)

;----------------------------------------------------------------------------------------------------

UpdateRandNum:
		LDA RandomNumberUB	  ;($C55B)
		STA GenWord3CUB		 ;($C55D)
		LDA RandomNumberLB	  ;($C55F)
		STA GenWord3CLB		 ;($C561)
		ASL RandomNumberLB	  ;($C563)
		ROL RandomNumberUB	  ;($C565)
		CLC					 ;($C567)
		ADC RandomNumberLB	  ;($C568)
		STA RandomNumberLB	  ;($C56A)
		LDA RandomNumberUB	  ;($C56C)
		ADC GenWord3CUB		 ;($C56E)
		STA RandomNumberUB	  ;($C570)Update the random number word.
		LDA RandomNumberLB	  ;($C572)
		CLC					 ;($C574)
		ADC RandomNumberUB	  ;($C575)
		STA RandomNumberUB	  ;($C577)
		LDA RandomNumberLB	  ;($C579)
		CLC					 ;($C57B)
		ADC #$81				;($C57C)
		STA RandomNumberLB	  ;($C57E)
		LDA RandomNumberUB	  ;($C580)
		ADC #$00				;($C582)
		STA RandomNumberUB	  ;($C584)
		RTS					 ;($C586)

;----------------------------------------------------------------------------------------------------

WaitForPPUBufferSpace:
		STA GenByte24		   ;($C587)Save max number bytes that can be used in PPU buffer.

WaitForPPUBufferLoop:
		LDA PPUBufCount		 ;($C589)Is the used space below the max used space?
		CMP GenByte24		   ;($C58B)
		BCC WaitForPPUBufferEnd ;($C58D)If so, branch to end. Done waiting for space.
		JSR WaitForNMI		  ;($C58F)($FF74)Wait for VBlank interrupt.
		JMP WaitForPPUBufferLoop;($C592)($C589)Loop until PPU buffer has enough empty space.

WaitForPPUBufferEnd:
		RTS					 ;($C595)Buffer is free. Stop waiting.

;----------------------------------------------------------------------------------------------------

CalcPPUBufAddr:
		LDA #$40				;($C596)Indicate data is being saved to PPU address buffer.
		ORA XPosFromLeft		;($C598)
		STA XPosFromLeft		;($C59A)Set bit 6 to determine target later.
		BNE Block2TileConv	  ;($C59C)Branch always.

CalcRAMBufAddr:
		LDA #$80				;($C59E)Indicate data is being saved to RAM buffer.
		ORA XPosFromLeft		;($C5A0)
		STA XPosFromLeft		;($C5A2)Set MSB to determine target later.
		BNE DoAddressCalculation;($C5A4)Branch always.

Block2TileConv:
		ASL XPosFromLeft		;($C5A6)*2. Blocks are 2 tiles wide.
		ASL YPosFromTop		 ;($C5A8)*2. Blocks are 2 tiles tall.

DoAddressCalculation:
		LDA YPosFromTop		 ;($C5AA)Put Y position in upper address byte.  This is 8 times the
		STA PPUBufPtrUB		 ;($C5AC)address of the proper row needed so divide it down next.
		LDA #$00				;($C5AE)This saves from having to do the multiplication routine
		STA PPUBufPtrLB		 ;($C5B0)and is faster than shifting up into position.

		LSR PPUBufPtrUB		 ;($C5B2)
		ROR PPUBufPtrLB		 ;($C5B4)
		LSR PPUBufPtrUB		 ;($C5B6)Divide address by 8.
		ROR PPUBufPtrLB		 ;($C5B8)
		LSR PPUBufPtrUB		 ;($C5BA)
		ROR PPUBufPtrLB		 ;($C5BC)

		LDA XPosFromLeft		;($C5BE)
		AND #$1F				;($C5C0)Keep only lower 5 bits and add it to the addres
		CLC					 ;($C5C2)to get the proper offset in the current row.
		ADC PPUBufPtrLB		 ;($C5C3)
		STA PPUBufPtrLB		 ;($C5C5)

		PHP					 ;($C5C7)Save processor status on stack.

		LDA XPosFromLeft		;($C5C8)Is data being saved to the RAM buffer?
		BPL +				   ;($C5CA)If not, branch.

		LDA #$04				;($C5CC)Set upper byte or RAM buffer address.
		BNE EndPPUCalcAddr	  ;($C5CE)Branch always.

		* AND #$20			  ;($C5D0)Is data being written to nametable 1?
		BNE +				   ;($C5D2)If so, branch.

		LDA #NT_NAMETBL0_UB	 ;($C5D4)Load upper address byte of nametable 0.
		BNE EndPPUCalcAddr	  ;($C5D6)Branch always.

		* LDA #NT_NAMETBL1_UB   ;($C5D8)Load upper address byte of namteable 1.

EndPPUCalcAddr:
		PLP					 ;($C5DA)Restore processor status from stack.

		ADC PPUAddrUB		   ;($C5DB)
		STA PPUAddrUB		   ;($C5DD)Save proper PPU upper address byte and exit.
		RTS					 ;($C5DF)

;----------------------------------------------------------------------------------------------------

		ASL NTXPos			  ;($C5E0)Not used.
		ASL NTYPos			  ;($C5E2)

CalcAttribAddr:
		LDA NTYPos			  ;($C5E4)
		AND #$FC				;($C5E6)Drop lower 2 bytes and multiply by 2.
		ASL					 ;($C5E8)Attribute table byte controls 4x4 tile square.
		STA PPUAddrLB		   ;($C5E9)

		LDA NTXPos			  ;($C5EB)
		AND #$1F				;($C5ED)Do not exceed 32 tiles in the row.
		LSR					 ;($C5EF)
		LSR					 ;($C5F0)/4. 1 byte of attrib. table controls 4x4 tile square.
		CLC					 ;($C5F1)
		ADC PPUAddrLB		   ;($C5F2)Add X offset to calculation.
		CLC					 ;($C5F4)
		ADC #$C0				;($C5F5)Offset to attribute table at $23C0 or $27C0. Lower byte now
		STA PPUAddrLB		   ;($C5F7)contains proper address to corresponding attribute table address.

		LDA NTXPos			  ;($C5F9)Are we currently on nametable 0?
		AND #$20				;($C5FB)
		BNE +				   ;($C5FD)If not, branch to use address for nametable 1.

		LDA #$03				;($C5FF)Lower nibble of upper byte(attribute table for nametable 0).
		BNE ExitAttributeCalculation;($C601)Branch always.

		* LDA #$07			  ;($C603)Lower nibble of upper byte(attribute table for nametable 1).

ExitAttributeCalculation:
		STA PPUAddrUB		   ;($C605)Store calculated upper byte.
		RTS					 ;($C607)

;----------------------------------------------------------------------------------------------------

GetJoypadStatus:
		LDA GenByte3C		   ;($C608)
		PHA					 ;($C60A)Prepare to update the random number by first saving registers
		LDA GenByte3D		   ;($C60B)that are affected by the random number calculationa.
		PHA					 ;($C60D)

		JSR UpdateRandNum	   ;($C60E)($C55B)Get random number.

		PLA					 ;($C611)
		STA GenByte3D		   ;($C612)Restore the registers affected by random number calculations.
		PLA					 ;($C614)
		STA GenByte3C		   ;($C615)

		LDA #$01				;($C617)
		STA CPUJoyPad1		  ;($C619)Reset controller port 1 in preparation for 8 reads.
		LDA #$00				;($C61C)
		STA CPUJoyPad1		  ;($C61E)

		LDY #$08				;($C621)Prepare to read 8 bits from controller port 1.

JoypadReadLoop:
		LDA CPUJoyPad1		  ;($C623)Read joypad bit from controller hardwars.
		STA JoypadBit		   ;($C626)
		LSR					 ;($C628)
		ORA JoypadBit		   ;($C629)Read the Famicom expansion bit(not used by NES).
		LSR					 ;($C62B)
		ROR JoypadBtns		  ;($C62C)Rotate bit into the joypad status register.
		DEY					 ;($C62E)Have 8 bits been read from the controller?
		BNE JoypadReadLoop	  ;($C62F)If not, branch to get another bit.

		RTS					 ;($C631)Done reading the controller bits.

;----------------------------------------------------------------------------------------------------

PrepSPPalLoad:
		LDA #$31				;($C632)Max. 48 buffer spots can be used.
		JSR WaitForPPUBufferSpace;($C634)($C587)Wait for space in PPU buffer.

		LDA #PAL_SPR_LB		 ;($C637)Sprite palettes start at address $3F10.
		STA PPUAddrLB		   ;($C639)
		BNE LoadPalData		 ;($C63B)Branch always.

PrepBGPalLoad:
		LDA #$61				;($C63D)Max. 96 buffer spots can be used.
		JSR WaitForPPUBufferSpace;($C63F)($C587)Wait for space in PPU buffer.

		LDA #PAL_BKG_LB		 ;($C642)Background palettes start at address $3F00.
		STA PPUAddrLB		   ;($C644)

LoadPalData:
		LDA #PAL_UB			 ;($C646)Upper byte of palette addresses are all $3F.
		STA PPUAddrUB		   ;($C648)

		LDY #$00				;($C64A)Prepare to add color data to 4 palettes.

PalDataLoop:
		LDA #PAL_BLACK		  ;($C64C)First color of every palette is always black.
		STA PPUDataByte		 ;($C64E)

		JSR AddPPUBufferEntry   ;($C650)($C690)Add data to PPU buffer.
		JSR AddPalByte		  ;($C653)($C661)Add a byte of palette data to the PPU buffer.
		JSR AddPalByte		  ;($C656)($C661)Add a byte of palette data to the PPU buffer.
		JSR AddPalByte		  ;($C659)($C661)Add a byte of palette data to the PPU buffer.
		CPY #$0C				;($C65C)Have all the palettes been processed?
		BNE PalDataLoop		 ;($C65E)If not, branch to add color data to another palette.
		RTS					 ;($C660)

AddPalByte:
		LDA PPUAddrLB		   ;($C661)Is this the palette color used for text box borders?
		CMP #$01				;($C663)
		BEQ ChkLowHPPal		 ;($C665)If so, branch to see if HP is low for special color.

		CMP #$03				;($C667)Is this the third palette color?
		BNE ChkPalFade		  ;($C669)If not, branch to move on.

		LDA EnemyNumber		 ;($C66B)Is player fighting the final boss?
		CMP #EN_DRAGONLORD2	 ;($C66D)If not, branch to move on.
		BNE ChkPalFade		  ;($C66F)Maybe this was used for a special palette no longer in the game?

ChkLowHPPal:
		LDA DisplayedMaxHP	  ;($C671)
		LSR					 ;($C673)
		LSR					 ;($C674)Is player's health less than 1/8 of max HP?
		CLC					 ;($C675)If so, load red palette color instead of white.
		ADC #$01				;($C676)
		CMP HitPoints		   ;($C678)
		BCC ChkPalFade		  ;($C67A)

		LDA #$26				;($C67C)Load red palette color for low health.
		BNE +				   ;($C67E)

ChkPalFade:
		LDA (PalettePointerLB),Y;($C680)Get current palette color.

		* SEC				   ;($C682)If fade in/fade out is currently active, subtract the
		SBC PalModByte		  ;($C683)current fade offset value from color to make it darker.
		BCS +				   ;($C685)

		LDA #PAL_BLACK		  ;($C687)Fully faded out. Set all palette colors to black.

		* STA PPUDataByte	   ;($C689)Save final palette color.
		JSR AddPPUBufferEntry   ;($C68B)($C690)Add data to PPU buffer.
		INY					 ;($C68E)Move to next palette byte.
		RTS					 ;($C68F)

;----------------------------------------------------------------------------------------------------

AddPPUBufferEntry:
		LDX PPUBufCount		 ;($C690)
		CPX #$B0				;($C692)Is the PPU buffer full?
		BCC PutPPUBufferData	;($C694)If not, branch to add data to the PPU buffer.

		JSR WaitForNMI		  ;($C696)($FF74)Wait for VBlank interrupt.
		JMP AddPPUBufferEntry   ;($C699)Loop until buffer has room.

PutPPUBufferData:
		LDX PPUBufCount		 ;($C69C)Copy PPU buffer count to X
		LDA PPUAddrUB		   ;($C69E)
		STA BlockRAM,X		  ;($C6A0)Add upper byte of PPU target address to buffer.
		INX					 ;($C6A3)
		LDA PPUAddrLB		   ;($C6A4)
		STA BlockRAM,X		  ;($C6A6)Add lower byte of PPU target address to buffer.
		INX					 ;($C6A9)
		LDA PPUDataByte		 ;($C6AA)
		STA BlockRAM,X		  ;($C6AC)Add data byte to write to PPU to the buffer.
		INX					 ;($C6AF)

		INC PPUEntryCount	   ;($C6B0)Increase PPU buffer entries by 1(3 bytes per entry).
		STX PPUBufCount		 ;($C6B2)Increase buffer count by 3 bytes.

		INC PPUAddrLB		   ;($C6B4)
		BNE +				   ;($C6B6)Increment PPU target address.
		INC PPUAddrUB		   ;($C6B8)
		* RTS				   ;($C6BA)

;----------------------------------------------------------------------------------------------------

ClearSpriteRAM:
		JSR WaitForNMI		  ;($C6BB)($FF74)Wait for VBlank.
		LDX #$00				;($C6BE)
		LDA #$F0				;($C6C0)
		* STA SpriteRAM,X	   ;($C6C2)Clear 256 bytes of sprite RAM.
		INX					 ;($C6C5)
		BNE -				   ;($C6C6)
		RTS					 ;($C6C8)

;----------------------------------------------------------------------------------------------------

;The following appear to be unused functions from Dragon Quest.

		.byte $A2, $00, $A9, $5F, $95, $AF, $E8, $E0, $05, $D0, $F9, $A9, $FA, $95, $AF, $CA;($C6C9)
		.byte $A9, $0A, $85, $3E, $A9, $00, $85, $3F, $20, $F4, $C1, $A5, $40, $95, $AF, $CA;($C6D9)
		.byte $A5, $3C, $05, $3D, $D0, $EA, $60;($C6E9)

;----------------------------------------------------------------------------------------------------

DoWindow:
		PLA					 ;($C6F0)
		CLC					 ;($C6F1)
		ADC #$01				;($C6F2)
		STA GenPtr3ELB		  ;($C6F4)
		PLA					 ;($C6F6)Get return address from stack and increment it.
		ADC #$00				;($C6F7)The new return address skips the window data byte.
		STA GenPtr3EUB		  ;($C6F9)
		PHA					 ;($C6FB)
		LDA GenPtr3ELB		  ;($C6FC)
		PHA					 ;($C6FE)

		LDY #$00				;($C6FF)Put window data byte in the accumulator.
		LDA (GenPtr3E),Y		;($C701)

_DoWindow:
		BRK					 ;($C703)Display a window.
		.byte $10, $17		  ;($C704)($A194)ShowWindow, bank 1.
		RTS					 ;($C706)

;----------------------------------------------------------------------------------------------------

AddBlocksToScreen:
		LDA BlockClear		  ;($C707)Will always be 0.
		BNE BlankBlock		  ;($C709)Branch never.

		LDY #$00				;($C70B)
		LDA (BlockAddr),Y	   ;($C70D)Is the block data blank?
		CMP #$FF				;($C70F)
		BEQ BlankBlock		  ;($C711)If so, branch.

		CMP #$FE				;($C713)Is the block data blank?
		BEQ BlankBlock		  ;($C715)If so, branch.

		JMP BattleBlock		 ;($C717)Branch always.

;This portion of code should never run under normal circumstances.

BlankBlock:
		LDA #$00				;($C71A)Remove no tiles from the current block.
		STA BlkRemoveFlgs	   ;($C71C)PPU column write.
		STA PPUHorizontalVertical;($C71E)

		JSR ModMapBlock		 ;($C720)($AD66)Change block on map.

		LDY #$00				;($C723)Prepare to clear the block data.
		LDA #$FF				;($C725)

		STA (BlockAddr),Y	   ;($C727)
		INY					 ;($C729)Clear top row of block.
		STA (BlockAddr),Y	   ;($C72A)

		LDY #$20				;($C72C)Move to next row in block.

		STA (BlockAddr),Y	   ;($C72E)
		INY					 ;($C730)Clear bottom row of block.
		STA (BlockAddr),Y	   ;($C731)
		RTS					 ;($C733)

BattleBlock:
		LDA NTBlockY			;($C734)
		ASL					 ;($C736)
		ADC YPosFromCenter	  ;($C737)Get the target tile Y position and convert from a
		CLC					 ;($C739)signed value to an unsigned value and store the results.
		ADC #$1E				;($C73A)
		STA DivideNumber1LB	 ;($C73C)
		LDA #$1E				;($C73E)
		STA DivideNumber2	   ;($C740)
		JSR ByteDivide		  ;($C742)($C1F0)Divide a 16-bit number by an 8-bit number.
		LDA DivideRemainder	 ;($C745)
		STA YPosFromTop		 ;($C747)
		STA YFromTopTemp		;($C749)

		LDA NTBlockX			;($C74B)
		ASL					 ;($C74D)
		CLC					 ;($C74E)Get the target tile X position and convert from a
		ADC XPosFromCenter	  ;($C74F)signed value to an unsigned value and store the results.
		AND #$3F				;($C751)
		STA XPosFromLeft		;($C753)
		STA XFromLeftTemp	   ;($C755)
		JSR DoAddressCalculation;($C757)($C5AA)Calculate destination address for GFX data.

		LDY #$00				;($C75A)Zero out index.

		LDA (BlockAddr),Y	   ;($C75C)Get upper left tile of block.
		STA PPUDataByte		 ;($C75E)
		JSR AddPPUBufferEntry   ;($C760)($C690)Add data to PPU buffer.

		INY					 ;($C763)Move to next tile.

		LDA (BlockAddr),Y	   ;($C764)Get upper right tile of block.
		STA PPUDataByte		 ;($C766)
		JSR AddPPUBufferEntry   ;($C768)($C690)Add data to PPU buffer.

		LDA PPUAddrLB		   ;($C76B)
		CLC					 ;($C76D)
		ADC #$1E				;($C76E)Move to the next row of the block.
		STA PPUAddrLB		   ;($C770)
		BCC +				   ;($C772)
		INC PPUAddrUB		   ;($C774)

		* LDY #$20			  ;($C776)Move to next tile in next row down.

		LDA (BlockAddr),Y	   ;($C778)Get lower left tile of block.
		STA PPUDataByte		 ;($C77A)
		JSR AddPPUBufferEntry   ;($C77C)($C690)Add data to PPU buffer.

		INY					 ;($C77F)Move to next tile.

		LDA (BlockAddr),Y	   ;($C780)Get lower right tile of block.
		STA PPUDataByte		 ;($C782)
		JSR AddPPUBufferEntry   ;($C784)($C690)Add data to PPU buffer.

		LDA XFromLeftTemp	   ;($C787)
		STA XPosFromLeft		;($C789)Restore the X and Y position variables.
		LDA YFromTopTemp		;($C78B)
		STA YPosFromTop		 ;($C78D)

		LDY #$00				;($C78F)Zero out index.

		LDA (BlockAddr),Y	   ;($C791)Sets attribute table value for each block based on its
		CMP #$C1				;($C793)position in the pattern table.
		BCS +				   ;($C795)Is this a sky tile in the battle scene? If not, branch.

		LDA #$00				;($C797)Set attribute table value for battle scene sky tiles.
		BEQ SetAttribVals	   ;($C799)

		* CMP #$CA			  ;($C79B)Is this a green covered mountain tile in the battle scene?
		BCS +				   ;($C79D)If not, branch.

		LDA #$01				;($C79F)Set attribute table value for battle scene green covered
		BNE SetAttribVals	   ;($C7A1)mountain tiles. Branch always.

		* CMP #$DE			  ;($C7A3)Is this a foreground tile in the battle scene?
		BCS +				   ;($C7A5)If not, branch.

		LDA #$02				;($C7A7)Set attribute table value for battle scene foreground tiles.
		BNE SetAttribVals	   ;($C7A9)Branch always.

		* LDA #$03			  ;($C7AB)Set attribute table values for battle scene horizon tiles.

SetAttribVals:
		STA PPUDataByte		 ;($C7AD)Store attribute table data.
		JSR ModAttribBits	   ;($C7AF)($C006)Set the attribute table bits for a nametable block.

		LDA PPUAddrUB		   ;($C7B2)
		CLC					 ;($C7B4)Move to the next position in the column.
		ADC #$20				;($C7B5)
		STA PPUAddrUB		   ;($C7B7)

		JSR AddPPUBufferEntry   ;($C7B9)($C690)Add data to PPU buffer.
		RTS					 ;($C7BC)

;----------------------------------------------------------------------------------------------------

DoMidDialog:
		STA GenByte3C		   ;($C7BD)Save dialog data byte.
		LDA #$00				;($C7BF)Dialog is in lower text blocks.
		STA GenByte3D		   ;($C7C1)
		BEQ SetDialogBytes	  ;($C7C3)($C7E4)Prepare to display on-screen dialog.

;----------------------------------------------------------------------------------------------------
DoDialogHiBlock:
		LDA #$01				;($C7C5)Prepare to get dialog from TextBlock17 or higher.
		STA GenByte3D		   ;($C7C7)
		BNE +				   ;($C7C9)Branch always.

DoDialogLoBlock:
		LDA #$00				;($C7CB)Prepare to get dialog from TextBlock1 to TextBlock16.
		STA GenByte3D		   ;($C7CD)

		* PLA				   ;($C7CF)Pull return address off the stack and increment
		CLC					 ;($C7D0)it.  Then place it back on the stack to skip
		ADC #$01				;($C7D1)the data byte in the calling function.
		STA GenPtr3ELB		  ;($C7D3)
		PLA					 ;($C7D5)
		ADC #$00				;($C7D6)
		STA GenPtr3EUB		  ;($C7D8)
		PHA					 ;($C7DA)Set a pointer to the data byte
		LDA GenPtr3ELB		  ;($C7DB)in the calling function.
		PHA					 ;($C7DD)

		LDY #$00				;($C7DE)
		LDA (GenPtr3E),Y		;($C7E0)Store data byte.
		STA GenByte3C		   ;($C7E2)

SetDialogBytes:
		LDA GenByte3C		   ;($C7E4)Data byte after function call.
		LDX GenByte3D		   ;($C7E6)High/low text block bit.

		BRK					 ;($C7E8)Display dialog on screen.
		.byte $12, $17		  ;($C7E9)($B51D)DoDialog, bank 1.
		RTS					 ;($C7EB)

;----------------------------------------------------------------------------------------------------

;This section appears to be unused code from Dragon Quest.

		.byte $A5, $4B, $0A, $85, $3C, $A5, $98, $18, $69, $2C, $38, $E5, $3C, $85, $3C, $A9;($C7EC)
		.byte $1E, $85, $3E, $20, $F0, $C1, $A5, $40, $85, $3E, $48, $A5, $4A, $0A, $85, $3C;($C7FC)
		.byte $A5, $D4, $18, $69, $10, $38, $E5, $3C, $85, $3C, $20, $9E, $C5, $A5, $0A, $85;($C80C)
		.byte $0C, $A5, $0B, $85, $0D, $68, $85, $3E, $A5, $4A, $0A, $85, $3C, $A5, $D2, $18;($C81C)
		.byte $69, $10, $38, $E5, $3C, $85, $3C, $20, $9E, $C5, $A5, $0A, $85, $42, $A5, $0B;($C82C)
		.byte $85, $43, $60, $A9, $5F, $85, $08, $20, $F5, $C4, $4C, $90, $C6, $A9, $56, $85;($C83C)
		.byte $08, $20, $F5, $C4, $4C, $90, $C6, $A9, $FF, $85, $4F, $20, $74, $FF, $20, $3F;($C84C)
		.byte $C8, $A5, $47, $48, $20, $08, $C6, $68, $F0, $0B, $A5, $4F, $29, $0F, $C9, $0C;($C85C)
		.byte $F0, $03, $4C, $A9, $C9, $A5, $47, $29, $01, $F0, $1C, $20, $49, $C8, $A5, $D8;($C86C)
		.byte $C9, $01, $F0, $04, $A9, $00, $85, $D7, $A5, $D9, $18, $65, $D7, $85, $D7, $A9;($C87C)
		.byte $85, $00, $04, $17, $A5, $D7, $60, $A5, $47, $29, $02, $F0, $0D, $20, $49, $C8;($C88C)
		.byte $A9, $85, $00, $04, $17, $A9, $FF, $85, $D7, $60, $A5, $47, $29, $10, $F0, $42;($C89C)
		.byte $A5, $D8, $C9, $05, $F0, $1D, $A5, $D9, $D0, $03, $4C, $A9, $C9, $C6, $D9, $C6;($C8AC)
		.byte $98, $C6, $98, $A5, $98, $C9, $FE, $F0, $03, $4C, $A5, $C9, $A9, $1C, $85, $98;($C8BC)
		.byte $4C, $A5, $C9, $A5, $D9, $D0, $03, $4C, $A9, $C9, $A9, $00, $85, $D9, $A5, $9D;($C8CC)
		.byte $85, $97, $A5, $9E, $38, $E9, $02, $C9, $FE, $D0, $02, $A9, $1C, $85, $98, $4C;($C8DC)
		.byte $A5, $C9, $A5, $47, $29, $20, $F0, $46, $A5, $D8, $C9, $05, $F0, $21, $E6, $D9;($C8EC)
		.byte $A5, $D9, $C5, $D7, $D0, $05, $C6, $D9, $4C, $A9, $C9, $E6, $98, $E6, $98, $A5;($C8FC)
		.byte $98, $C9, $1E, $F0, $03, $4C, $A5, $C9, $A9, $00, $85, $98, $4C, $A5, $C9, $A9;($C90C)
		.byte $02, $C5, $D9, $D0, $03, $4C, $A9, $C9, $85, $D9, $A5, $9D, $85, $97, $A5, $9E;($C91C)
		.byte $18, $69, $02, $C9, $1E, $D0, $02, $A9, $00, $85, $98, $4C, $A5, $C9, $A5, $47;($C92C)
		.byte $29, $40, $F0, $32, $A5, $D8, $C9, $05, $F0, $14, $A5, $D8, $C9, $01, $D0, $5D;($C93C)
		.byte $C6, $D8, $A5, $97, $38, $E9, $06, $29, $3F, $85, $97, $4C, $A5, $C9, $A9, $03;($C94C)
		.byte $C5, $D9, $F0, $49, $85, $D9, $A5, $9E, $85, $98, $A5, $9D, $38, $E9, $02, $29;($C95C)
		.byte $3F, $85, $97, $4C, $A5, $C9, $A5, $47, $29, $80, $F0, $31, $A5, $D8, $C9, $05;($C96C)
		.byte $F0, $12, $A5, $D8, $D0, $27, $E6, $D8, $A5, $97, $18, $69, $06, $29, $3F, $85;($C97C)
		.byte $97, $4C, $A5, $C9, $A9, $01, $C5, $D9, $F0, $13, $85, $D9, $A5, $9E, $85, $98;($C98C)
		.byte $A5, $9D, $18, $69, $02, $29, $3F, $85, $97, $A9, $00, $85, $4F, $A5, $4F, $29;($C99C)
		.byte $10, $D0, $03, $20, $49, $C8, $4C, $57, $C8;($C9AC)

;----------------------------------------------------------------------------------------------------

ContinueReset:
		LDA #$00				;($C9B5)Switch to PRG bank 0.
		JSR SetPRGBankAndSwitch ;($C9B7)($FF91)Switch to new PRG bank.

		LDA #$00				;($C9BA)
		TAX					 ;($C9BC)Clear more RAM.
		STA DrgnLrdPal		  ;($C9BD)
		STA CharDirection	   ;($C9C0)

		* STA TrsrXPos,X		;($C9C3)
		INX					 ;($C9C6)Clear RAM used for treasure
		CPX #$10				;($C9C7)chest pickup history.
		BCC -				   ;($C9C9)

		BRK					 ;($C9CB)
		.byte $02, $17		  ;($C9CC)($8178)ClearSoundRegisters, bank 1.

		JSR Bank0ToNT0		  ;($C9CE)($FCA3)Load data into nametable 0.
		JSR Bank3ToNT1		  ;($C9D1)($FCB8)Load data into nametable 1.

		LDA #$FF				;($C9D4)Invalidate HP.
		STA HitPoints		   ;($C9D6)

		LDA #$08				;($C9D8)
		STA NTBlockX			;($C9DA)Set player's initial position on the nametable.
		LDA #$07				;($C9DC)
		STA NTBlockY			;($C9DE)
		JSR DoIntroGFX		  ;($C9E0)($BD5B)Load intro graphics.

		LDA #$01				;($C9E3)Wait for PPU buffer to be completely empty.
		JSR WaitForPPUBufferSpace;($C9E5)($C587)Wait for space in PPU buffer.

		LDA #%00011000		  ;($C9E8)Enable sprites and background.
		STA PPUControl1		 ;($C9EA)

		LDA #$00				;($C9ED)Reset sound engine status.
		STA SoundEngineStatus   ;($C9EF)

;----------------------------------------------------------------------------------------------------

;The game is completely reset at this point.  Start the intro routine stuff.

		BRK					 ;($C9F2)
		.byte $00, $27		  ;($C9F3)($BCB0)DoIntroRoutine, bank 2.

		LDA #%00000000		  ;($C9F5)Turn off sprites and background.
		STA PPUControl1		 ;($C9F7)

		JSR WaitForNMI		  ;($C9FA)($FF74)Wait for VBlank interrupt.
		JSR Bank1ToNT0		  ;($C9FD)($FC98)Load CHR ROM bank 1 into nametable 0.
		JSR Bank2ToNT1		  ;($CA00)($FCAD)Load CHR ROM bank 2 into nametable 1.

		LDA #MSC_VILLAGE		;($CA03)Village music.
		BRK					 ;($CA05)
		.byte $04, $17		  ;($CA06)($81A0)InitMusicSFX, bank 1.

		JSR LoadSaveMenus	   ;($CA08)($F678)Intro passed. Show load/save windows.

;----------------------------------------------------------------------------------------------------

;The gameplay has started.

		LDA #$FA				;($CA0B)Indicate game has been started.
		STA GameStarted		 ;($CA0D)

		LDA #$00				;($CA0F)Prepare to clear door and treasure history.
		TAX					 ;($CA11)

		* STA DoorXPos,X		;($CA12)
		INX					 ;($CA15)Clear the door and treasure history.
		CPX #$20				;($CA16)
		BNE -				   ;($CA18)

		JSR StartAtThroneRoom   ;($CA1A)($CB47)Start player at throne room.

		LDA PlayerFlags		 ;($CA1D)Did the player just start the game?
		AND #F_LEFT_THROOM	  ;($CA1F)
		BEQ FirstKingDialog	 ;($CA21)If so, branch for the king's initial dialog.

		JSR DoDialogHiBlock	 ;($CA23)($C7C5)I am glad thou hast returned...
		.byte $17			   ;($CA26)TextBlock18, entry 7.

		LDA DisplayedLevel	  ;($CA27)Is player level 30? If so, show a special message.
		CMP #LEVEL_30		   ;($CA29)
		BNE KingExperienceCalculation;($CA2B)If not, branch for the regular message.

		JSR DoDialogLoBlock	 ;($CA2D)($C7CB)Though art strong enough...
		.byte $02			   ;($CA30)TextBlock1, entry 2.

		JMP EndKingDialog	   ;($CA31)Jump to last king dialog segment.

KingExperienceCalculation:
		JSR GetExperienceRemaining;($CA34)($F134)Calculate experience needed for next level.

		JSR DoDialogLoBlock	 ;($CA37)($C7CB)Before reaching thy next level...
		.byte $C1			   ;($CA3A)TextBlock13, entry 1.

		JSR DoDialogHiBlock	 ;($CA3B)($C7C5)See me again when thy level increases...
		.byte $18			   ;($CA3E)TextBlock18, entry 8.

EndKingDialog:
		JSR DoDialogLoBlock	 ;($CA3F)($C7CB)Goodbye now. Take care...
		.byte $C4			   ;($CA42)TextBlock13, entry 4.

		JMP PlayerInitializeControl;($CA43)($CA4A)Give the player control for the first time.

FirstKingDialog:
		JSR DoDialogHiBlock	 ;($CA46)($C7C5)Descendant of Erdrick, listen to my words...
		.byte $02			   ;($CA49)TextBlock17, entry 2.

PlayerInitializeControl:
		JSR WaitForBtnRelease   ;($CA4A)($CFE4)Wait for player to release then press joypad buttons.

		LDA #WINDOW_DIALOG	  ;($CA4D)Remove the dialog window from the screen.
		JSR RemoveWindow		;($CA4F)($A7A2)Remove window from screen.

		LDA #NPC_MOVE		   ;($CA52)Allow the NPCs to move.
		STA StopNPCMove		 ;($CA54)

;----------------------------------------------------------------------------------------------------

;This is the main loop where the rest of the game originates from.

GameEngineLoop:
		LDA RadiantTimer		;($CA56)Is the radiant timer active?
		BEQ CheckRepelTimer	 ;($CA58)If not, branch to check the repel timer.

		DEC RadiantTimer		;($CA5A)Decrement the radiant timer.
		BNE CheckRepelTimer	 ;($CA5C)Is radiant timer expired? If not, branch to check the repel timer.

		LDA LightDiameter	   ;($CA5E)Radiant timer expired. Check light diameter.
		CMP #$01				;($CA60)Is light diameter at minimum?
		BEQ CheckRepelTimer	 ;($CA62)If so, branch to check the repel timer.

		LDA #$3C				;($CA64)Reload radiant timer. 60 steps.
		STA RadiantTimer		;($CA66)
		DEC LightDiameter	   ;($CA68)Radius is reduced by two squares.
		DEC LightDiameter	   ;($CA6A)

CheckRepelTimer:
		LDA RepelTimer		  ;($CA6C)Is the repel timer active?
		BEQ JoypadCheckLoop	 ;($CA6E)If not, branch to check joypad inputs.

		DEC RepelTimer		  ;($CA70)Decrement the repel timer by 2 every step.
		DEC RepelTimer		  ;($CA72)
		BEQ EndRepelTimer	   ;($CA74)Did repel timer just end? If so, branch to show message.

		LDA RepelTimer		  ;($CA76)Ir repel timer about to end?
		CMP #$01				;($CA78)If not, jump to check user input.
		BNE JoypadCheckLoop	 ;($CA7A)

EndRepelTimer:
		JSR WaitForNMI		  ;($CA7C)($FF74)Wait for VBlank interrupt.
		LDA #NPC_STOP		   ;($CA7F)
		STA StopNPCMove		 ;($CA81)Stop NPC movement.

		JSR Dowindow			;($CA83)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($CA86)Dialog window.

		LDA RepelTimer		  ;($CA87)If repel timer is odd, it is the repel spell. If it is
		BNE RepelEndMessage	 ;($CA89)even, it is from fairy water. Branch accordingly.

		LDA #$37				;($CA8B)TextBlock4, entry 7. The fairy water has lost its effect...
		BNE +				   ;($CA8D)Branch always.

RepelEndMessage:
		LDA #$34				;($CA8F)TextBlock4, entry 4. Repel has lost its effect...
		* JSR DoMidDialog	   ;($CA91)($C7BD)Do any number of Dialogs.

		JSR ResumeGamePlay	  ;($CA94)($CFD9)Give control back to player.
		LDA #$00				;($CA97)
		STA RepelTimer		  ;($CA99)Deactivate the repel timer.

JoypadCheckLoop:
		LDA #$00				;($CA9B)Reset the frame counter.
		STA FrameCounter		;($CA9D)

CheckInputs:
		JSR GetJoypadStatus	 ;($CA9F)($C608)Get input button presses.
		LDA JoypadBtns		  ;($CAA2)
		AND #IN_START		   ;($CAA4)Is game paused?
		BEQ CheckJoyA		   ;($CAA6)If not, branch to check user inputs.

PausePrepareLoop:
		JSR WaitForNMI		  ;($CAA8)($FF74)Wait for VBlank interrupt.
		LDA FrameCounter		;($CAAB)
		AND #$0F				;($CAAD)Sync the pause every 16th frame of the frame counter.
		CMP #$01				;($CAAF)This lines up the NPCs and player on the background tiles.
		BEQ GamePaused		  ;($CAB1)
		JSR DoSprites		   ;($CAB3)($B6DA)Update player and NPC sprites.
		JMP PausePrepareLoop	;($CAB6)($CAA8)Start pressed.  Wait until first frame and then pause game.

GamePaused:
		JSR GetJoypadStatus	 ;($CAB9)($C608)Get input button presses.
		LDA JoypadBtns		  ;($CABC)
		AND #IN_START		   ;($CABE)Stay in this loop until player releases pause button.
		BNE GamePaused		  ;($CAC0)

		* JSR GetJoypadStatus   ;($CAC2)($C608)Get input button presses.
		LDA JoypadBtns		  ;($CAC5)
		AND #IN_START		   ;($CAC7)Stay in this loop until user presses button to unpause game.
		BEQ -				   ;($CAC9)

		* JSR GetJoypadStatus   ;($CACB)($C608)Get input button presses.
		LDA JoypadBtns		  ;($CACE)
		AND #IN_START		   ;($CAD0)Stay in this loop until user releases start button(unpause).
		BNE -				   ;($CAD2)
		JMP JoypadCheckLoop	 ;($CAD4)($CA9B)Loop and check for controller input.

CheckJoyA:
		LDA JoypadBtns		  ;($CAD7)Was A button pressed?
		LSR					 ;($CAD9)If not, branch to check other buttons.
		BCC CheckJoyUp		  ;($CADA)

		JSR DoNonCombatCommandWindow;($CADC)($CF49)Bring up non-combat command window.
		JMP JoypadCheckLoop	 ;($CADF)Loop again to keep checking user inputs.

CheckJoyUp:
		LDA JoypadBtns		  ;($CAE2)Get joypad buttons.
		AND #IN_UP			  ;($CAE4)Is up being pressed?
		BEQ CheckJoyDown		;($CAE6)If not, branch to check next button.

		LDA #DIR_UP			 ;($CAE8)Point character up.
		STA CharDirection	   ;($CAEA)
		JSR DoJoyUp			 ;($CAED)($B504)Do button up pressed checks.
		JSR ChkSpecialLoc	   ;($CAF0)($B219)Check for special locations on the maps.
		JMP GameEngineLoop	  ;($CAF3)($CA56)Return to the start of the game engine loop.

CheckJoyDown:
		LDA JoypadBtns		  ;($CAF6)Get joypad buttons.
		AND #IN_DOWN			;($CAF8)Is down being pressed?
		BEQ CheckJoyLeft		;($CAFA)If not, branch to check next button.

		LDA #DIR_DOWN		   ;($CAFC)Point character down.
		STA CharDirection	   ;($CAFE)
		JSR DoJoyDown		   ;($CB01)($B3D8)Do button down pressed checks.
		JSR ChkSpecialLoc	   ;($CB04)($B219)Check for special locations on the maps.
		JMP GameEngineLoop	  ;($CB07)($CA56)Return to the start of the game engine loop.

CheckJoyLeft:
		LDA JoypadBtns		  ;($CB0A)Get joypad buttons.
		AND #IN_LEFT			;($CB0C)Is left being pressed?
		BEQ CheckJoyRight	   ;($CB0E)If not, branch to check next button.

		LDA #DIR_LEFT		   ;($CB10)Point character left.
		STA CharDirection	   ;($CB12)
		JSR DoJoyLeft		   ;($CB15)($B34C)Do button left pressed checks.
		JSR ChkSpecialLoc	   ;($CB18)($B219)Check for special locations on the maps.
		JMP GameEngineLoop	  ;($CB1B)($CA56)Return to the start of the game engine loop.

CheckJoyRight:
		LDA JoypadBtns		  ;($CB1E)Get joypad buttons.
		BPL IdleUpdate		  ;($CB20)Is right being pressed? If not, branch to update the idle status.

		LDA #DIR_RIGHT		  ;($CB22)Point character right.
		STA CharDirection	   ;($CB24)
		JSR DoJoyRight		  ;($CB27)($B252)Do button right pressed checks.
		JSR ChkSpecialLoc	   ;($CB2A)($B219)Check for special locations on the maps.
		JMP GameEngineLoop	  ;($CB2D)($CA56)Return to the start of the game engine loop.

IdleUpdate:
		JSR WaitForNMI		  ;($CB30)($FF74)Wait for VBlank interrupt.
		LDA FrameCounter		;($CB33)Has the input been idle for 50 frames?
		CMP #$31				;($CB35)
		BNE EngineLoopEnd	   ;($CB37)If not, branch to not bring up the pop-up window.

		JSR Dowindow			;($CB39)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($CB3C)Pop-up window.

		LDA #$32				;($CB3D)Indicate pop-up window is active.
		STA FrameCounter		;($CB3F)

EngineLoopEnd:
		JSR DoSprites		   ;($CB41)($B6DA)Update player and NPC sprites.
		JMP CheckInputs		 ;($CB44)Loop until user presses a button.

;----------------------------------------------------------------------------------------------------

StartAtThroneRoom:
		JSR WaitForNMI		  ;($CB47)($FF74)Wait for VBlank interrupt.
		LDA BlackPalPtr		 ;($CB4A)
		STA PalettePointerLB	;($CB4D)
		LDA BlackPalPtr+1	   ;($CB4F)Point to the all black palette.
		STA PalettePointerUB	;($CB52)

		LDA #$00				;($CB54)No sprite palette fade in.
		STA PalModByte		  ;($CB56)

		JSR PrepSPPalLoad	   ;($CB58)($C632)Load sprite palette data into PPU buffer.
		LDA #$30				;($CB5B)
		STA PalModByte		  ;($CB5D)Prepare to fade in background tiles.

		JSR PrepBGPalLoad	   ;($CB5F)($C63D)Load background palette data into PPU buffer
		JSR WaitForNMI		  ;($CB62)($FF74)Wait for VBlank interrupt.
		JSR LoadStats		   ;($CB65)($F050)Update player attributes.
		JSR Bank1ToNT0		  ;($CB68)($FC98)Load CHR ROM bank 1 into nametable 0.

		LDA ModsnSpells		 ;($CB6B)Is the player cursed?
		AND #IS_CURSED		  ;($CB6D)
		BEQ +				   ;($CB6F)If not, branch to move on.

		LDA #$01				;($CB71)
		STA HitPoints		   ;($CB73)Player is cursed. Set starting hit points to 1.
		JMP SetStartPos		 ;($CB75)

		* LDA ThisStrtStat	  ;($CB78)Should player's HP and MP be restored on start?
		CMP #STRT_FULL_HP	   ;($CB7B)
		BNE SetStartPos		 ;($CB7D)If not, branch to move on.

		TXA					 ;($CB7F)Save X on the stack.
		PHA					 ;($CB80)

		LDA DisplayedMaxHP	  ;($CB81)
		STA HitPoints		   ;($CB83)Max out HP and MP.
		LDA DisplayedMaxMP	  ;($CB85)
		STA MagicPoints		 ;($CB87)

		LDX SaveNumber		  ;($CB89)
		LDA #STRT_NO_HP		 ;($CB8C)Indicate in the save game that the HP and MP
		STA StartStatus1,X	  ;($CB8E)should not be maxed out on the next start.
		STA ThisStrtStat		;($CB91)

		PLA					 ;($CB94)Restore X from the stack.
		TAX					 ;($CB95)

SetStartPos:
		LDA #$03				;($CB96)
		STA CharXPos			;($CB98)Set player's X block position.
		STA _CharXPos		   ;($CB9A)

		LDA #$04				;($CB9C)
		STA CharYPos			;($CB9E)Set player's Y block position.
		STA _CharYPos		   ;($CBA0)

		LDA #$30				;($CBA2)
		STA CharXPixelsLB	   ;($CBA4)Set player's X and Y map pixel positions.
		LDA #$40				;($CBA6)
		STA CharYPixelsLB	   ;($CBA8)

		LDA #$00				;($CBAA)
		STA RepeatCounter	   ;($CBAC)Clear any active timers and the upper byte
		STA RepelTimer		  ;($CBAE)of the map pixel positions.
		STA CharXPixelsUB	   ;($CBB0)
		STA CharYPixelsUB	   ;($CBB2)

		LDA #$08				;($CBB4)
		STA NTBlockX			;($CBB6)Set nametable X and Y position of the player.
		LDA #$07				;($CBB8)
		STA NTBlockY			;($CBBA)

		LDA #MAP_THRONEROOM	 ;($CBBC)Prepare to load the throne room map.
		STA MapNumber		   ;($CBBE)

		JSR ClearWinBufRAM2	 ;($CBC0)($A788)Clear RAM buffer used for drawing text windows.
		JSR MapChngNoSound	  ;($CBC3)($B091)Change maps with no stairs sound.
		JSR WaitForNMI		  ;($CBC6)($FF74)Wait for VBlank interrupt.

		LDA #$00				;($CBC9)Reset the frame counter.
		STA FrameCounter		;($CBCB)

FirstInputLoop:
		JSR GetJoypadStatus	 ;($CBCD)($C608)Get input button presses.
		LDA JoypadBtns		  ;($CBD0)Has player pressed a button?
		BNE FrameSyncLoop	   ;($CBD2)If not, loop until they do.

		JSR WaitForNMI		  ;($CBD4)($FF74)Wait for VBlank interrupt.
		JSR DoSprites		   ;($CBD7)($B6DA)Update player and NPC sprites.
		JMP FirstInputLoop	  ;($CBDA)Wait for player to press a button.

FrameSyncLoop:
		JSR WaitForNMI		  ;($CBDD)($FF74)Wait for VBlank interrupt.

		LDA FrameCounter		;($CBE0)
		AND #$0F				;($CBE2)Make sure the frame counter is synchronized. Actions will
		CMP #$01				;($CBE4)not occur until frame counter is on frame 1.
		BEQ +				   ;($CBE6)

		JSR DoSprites		   ;($CBE8)($B6DA)Update player and NPC sprites.
		JMP FrameSyncLoop	   ;($CBEB)($CBDD)Wait for frame 1 before loading dialog windows.

		* LDA #NPC_STOP		 ;($CBEE)Stop NPCs from moving on the screen.
		STA StopNPCMove		 ;($CBF0)

		JSR Dowindow			;($CBF2)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($CBF5)Dialog window.
		RTS					 ;($CBF6)

;----------------------------------------------------------------------------------------------------

CheckForTriggers:
		LDA StoryFlags		  ;($CBF7)Is the dragonlord dead?
		AND #F_DGNLRD_DEAD	  ;($CBF9)
		BNE ChkCstlEnd		  ;($CBFB)If so, branch to check end game trigger.

		JMP MovementUpdates	 ;($CBFD)($CCF6)Do routine movement checks.

ChkCstlEnd:
		LDA MapNumber		   ;($CC00)Is player on the ground floor of Tantagel castle?
		CMP #MAP_TANTCSTL_GF	;($CC02)
		BNE +				   ;($CC04)If not, branch to check other things.

		LDA CharYPos			;($CC06)Is player in the right Y coordinate to trigger the end game?
		CMP #$08				;($CC08)
		BNE +				   ;($CC0A)If not, branch to check other things.

		LDA CharXPos			;($CC0C)Is player at the first of 2 possible X coordinates to
		CMP #$0A				;($CC0E)trigger the end game?
		BEQ EndGameTriggered	;($CC10)If not, check second trigger.

		CMP #$0B				;($CC12)Is player at the second of 2 possible X coordinates to
		BEQ EndGameTriggered	;($CC14)trigger the end game? If so, branch to end game sequence.

		* JMP CheckBlockDmg	 ;($CC16)Check to see if current map tile will damage player.

EndGameTriggered:
		LDA #MSC_NOSOUND		;($CC19)Silence music.
		BRK					 ;($CC1B)
		.byte $04, $17		  ;($CC1C)($81A0)InitMusicSFX, bank 1.

		LDA #NPC_STOP		   ;($CC1E)Stop the NPCs from moving.
		STA StopNPCMove		 ;($CC20)

		JSR Dowindow			;($CC22)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($CC25)Dialog window.

		JSR DoDialogHiBlock	 ;($CC26)($C7C5)The legends have proven true...
		.byte $1B			   ;($CC29)TextBlock18, entry 11.

		LDA PlayerFlags		 ;($CC2A)Has the player returned princess Gwaelin?
		AND #F_RTN_GWAELIN	  ;($CC2C)
		BEQ ChkCarryGwaelin	 ;($CC2E)If not, branch to see if the player is carrying Gwaelin.

		LDA #$C7				;($CC30)Set princess Gwaelin at stairs, X position.
		STA GwaelinXPos		 ;($CC32)
		LDA #$27				;($CC34)Set princess Gwaelin at stairs, Y position, facing right.
		STA GwaelinYPos		 ;($CC36)
		LDA #$00				;($CC38)Align princess Gwaelin in stairs before movement.
		STA GwaelinOffset	   ;($CC3A)

		JSR WaitForNMI		  ;($CC3C)($FF74)Wait for VBlank interrupt.
		JSR DoSprites		   ;($CC3F)($B6DA)Update player and NPC sprites.

		JSR DoDialogHiBlock	 ;($CC42)($C7C5)Gwaelin said: please wait...
		.byte $1C			   ;($CC45)TextBlock18, entry 12.

GwaelinMoveLoop:
		JSR WaitForNMI		  ;($CC46)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($CC49)($FF74)Wait for VBlank interrupt.

		LDA GwaelinOffset	   ;($CC4C)
		CLC					 ;($CC4E)Move Gwaelin 1 pixel right.
		ADC #$10				;($CC4F)
		STA GwaelinOffset	   ;($CC51)Has Gwaelin moved 16 pixels?
		BCC +				   ;($CC53)If so, time to increment her X position.

		INC GwaelinXPos		 ;($CC55)increment Gwaelin's X position.

		* JSR DoSprites		 ;($CC57)($B6DA)Update player and NPC sprites.

		LDA GwaelinXPos		 ;($CC5A)Has Gwaelin moved next to the king?
		CMP #$CA				;($CC5C)
		BNE GwaelinMoveLoop	 ;($CC5E)If not, branch to move Gwaelin some more.

		LDA #$47				;($CC60)Change Gwaelin NPC to down facing direction.
		STA GwaelinYPos		 ;($CC62)
		JSR DoSprites		   ;($CC64)($B6DA)Update player and NPC sprites.
		JMP GwaelinJoin		 ;($CC67)Jump to Gwaelin dialog.

ChkCarryGwaelin:
		LDA PlayerFlags		 ;($CC6A)Is player carrying Gwaelin?
		LSR					 ;($CC6C)
		BCC TaleEnd			 ;($CC6D)If not, branch to skip Gwaelin ending sequence.

		LDA PlayerFlags		 ;($CC6F)
		AND #$FE				;($CC71)Clear the flag indicating the player is holding Gwaelin.
		STA PlayerFlags		 ;($CC73)

		LDA #$CA				;($CC75)
		STA GwaelinXPos		 ;($CC77)
		LDA #$47				;($CC79)Place princess Gwaelin next to the king and facing down.
		STA GwaelinYPos		 ;($CC7B)
		LDA #$00				;($CC7D)
		STA GwaelinOffset	   ;($CC7F)

		JSR WaitForNMI		  ;($CC81)($FF74)Wait for VBlank interrupt.
		JSR DoSprites		   ;($CC84)($B6DA)Update player and NPC sprites.

		JSR DoDialogHiBlock	 ;($CC87)($C7C5)Gwaelin said: please wait...
		.byte $1C			   ;($CC8A)TextBlock18, entry 12.

GwaelinJoin:
		JSR DoDialogHiBlock	 ;($CC8B)($C7C5)I wish to go with thee...
		.byte $1D			   ;($CC8E)TextBlock18, entry 13.

GwaelinDecline:
		JSR DoDialogHiBlock	 ;($CC8F)($C7C5)May I travel as your companion...
		.byte $1E			   ;($CC92)TextBlock18, entry 14.

		JSR Dowindow			;($CC93)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($CC94)Yes/No window.

		BEQ GwaelinAccept	   ;($CC97)Branch if player says yes to Gwaelin.

		JSR DoDialogLoBlock	 ;($CC99)($C7CB)But thou must...
		.byte $B6			   ;($CC9C)TextBlock12, entry 6.

		JMP GwaelinDecline	  ;($CC9D)Branch to loop until player accepts.

GwaelinAccept:
		JSR DoDialogLoBlock	 ;($CCA0)($C7CB)I'm so happy...
		.byte $B8			   ;($CCA3)TextBlock12, entry 8.

		LDA #$00				;($CCA4)
		STA GwaelinXPos		 ;($CCA6)Remove the princess Gwaelin NPC from the screen.
		STA GwaelinYPos		 ;($CCA8)She will be drawn in the player's arms.
		STA GwaelinOffset	   ;($CCAA)

		LDA PlayerFlags		 ;($CCAC)
		ORA #F_GOT_GWAELIN	  ;($CCAE)Set flag indicating player is carrying Gwaelin.
		STA PlayerFlags		 ;($CCB0)

		JSR WaitForNMI		  ;($CCB2)($FF74)Wait for VBlank interrupt.
		JSR DoSprites		   ;($CCB5)($B6DA)Update player and NPC sprites.

TaleEnd:
		JSR DoDialogHiBlock	 ;($CCB8)($C7C5)And thus the tale comes to an end...
		.byte $22			   ;($CCBB)TextBlock19, entry 2.

		LDX #$78				;($CCBC)Wait 120 frames before continuing.
		* JSR WaitForNMI		;($CCBE)($FF74)Wait for VBlank interrupt.
		DEX					 ;($CCC1)Has 120 frames passed?
		BNE -				   ;($CCC2)If not, branch to wait another frame.

		LDA #WINDOW_DIALOG	  ;($CCC4)Remove the dialog window.
		JSR RemoveWindow		;($CCC6)($A7A2)Remove window from screen.

		LDA #$01				;($CCC9)Show the player facing right.
		STA CharDirection	   ;($CCCB)
		JSR DoSprites		   ;($CCCE)($B6DA)Update player and NPC sprites.

		LDA #$1E				;($CCD1)Prepare to wait 30 frames(1/2 second).
		JSR WaitMultiNMIs	   ;($CCD3)($C170)Wait for a defined number of frames.

		LDA #$02				;($CCD6)Draw the player facing down.
		STA CharDirection	   ;($CCD8)
		JSR DoSprites		   ;($CCDB)($B6DA)Update player and NPC sprites.

		LDX #$1E				;($CCDE)Prepare to wait 30 frames(1/2 second).
		* JSR WaitForNMI		;($CCE0)($FF74)Wait for VBlank interrupt.
		DEX					 ;($CCE3)Has 30 frames passed?
		BNE -				   ;($CCE4)If not, branch to wait another frame.

		LDA #$FF				;($CCE6)Indicate the guards with trumpets should be shown.
		STA DisplayedLevel	  ;($CCE8)
		JSR DoSprites		   ;($CCEA)($B6DA)Update player and NPC sprites.

		BRK					 ;($CCED)Show end credits.
		.byte $0E, $17		  ;($CCEE)($939A)DoEndCredits, bank 1.

		JSR MMCShutdown		 ;($CCF0)($FC88)Switch to PRG bank 3 and disable PRG RAM.

Spinlock1:
		JMP Spinlock1		   ;($CCF3)($CCF3)Spinlock the game. Reset required to do anything else.

;----------------------------------------------------------------------------------------------------

MovementUpdates:
		LDA EqippedItems		;($CCF6)Is the player wearing Erdrick's armor?
		AND #AR_ARMOR		   ;($CCF8)
		CMP #AR_ERDK_ARMR	   ;($CCFA)
		BEQ MovmtIncHP		  ;($CCFC)If so, branch.

		CMP #AR_MAGIC_ARMR	  ;($CCFE)Is the player wearing magic armor?
		BNE CheckTantCursed	 ;($CD00)If not, branch.

		INC MjArmrHP			;($CD02)Player is wearing magic armor.
		LDA MjArmrHP			;($CD04)
		AND #$03				;($CD06)Is player on their 3rd step?
		BNE CheckTantCursed	 ;($CD08)If not, branch to exit check.

MovmtIncHP:
		INC HitPoints		   ;($CD0A)Player recovers 1 HP.

		LDA HitPoints		   ;($CD0C)Has player exceeded their max HP?
		CMP DisplayedMaxHP	  ;($CD0E)
		BCC ChkLowHP			;($CD10)If not, branch.

		LDA DisplayedMaxHP	  ;($CD12)Set player HP to max.
		STA HitPoints		   ;($CD14)

ChkLowHP:
		LDA DisplayedMaxHP	  ;($CD16)Does the player have less than 1/8th their max HP?
		LSR					 ;($CD18)
		LSR					 ;($CD19)
		CLC					 ;($CD1A)
		ADC #$01				;($CD1B)
		CMP HitPoints		   ;($CD1D)
		BCS CheckTantCursed	 ;($CD1F)If so, branch.

		LDA #$01				;($CD21)Player is not badly hurt.
		STA PPUAddrLB		   ;($CD23)
		LDA #$3F				;($CD25)
		STA PPUAddrUB		   ;($CD27)Make sure low HP palette is not active.
		LDA #$30				;($CD29)
		STA PPUDataByte		 ;($CD2B)
		JSR AddPPUBufferEntry   ;($CD2D)($C690)Add data to PPU buffer.

;----------------------------------------------------------------------------------------------------

CheckTantCursed:
		LDA MapNumber		   ;($CD30)Is the player in Tantagel castle, ground floor?
		CMP #MAP_TANTCSTL_GF	;($CD32)
		BNE CheckAxeKnight	  ;($CD34)If not, exit this check.

		LDA ModsnSpells		 ;($CD36)Is the player cursed?
		AND #$C0				;($CD38)
		BEQ CheckAxeKnight	  ;($CD3A)If not, branch to exit this check.

		LDA CharYPos			;($CD3C)Is the player's Y position 27?
		CMP #$1B				;($CD3E)
		BNE CheckAxeKnight	  ;($CD40)If not, exit this check.

		LDA #NPC_STOP		   ;($CD42)Stop the NPCs from moving.
		STA StopNPCMove		 ;($CD44)

		JSR Dowindow			;($CD46)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($CD49)Dialog window.

		JSR DoDialogLoBlock	 ;($CD4A)($C7CB)Cursed one, be gone...
		.byte $44			   ;($CD4D)TextBlock5, entry 4.

		JMP CheckMapExit		;($CD4E)($B228)Force player to exit the map.

;----------------------------------------------------------------------------------------------------

CheckAxeKnight:
		LDA MapNumber		   ;($CD51)Is the player in Hauksness?
		CMP #MAP_HAUKSNESS	  ;($CD53)
		BNE CheckGrnDragon	  ;($CD55)If not, exit this check.

		LDA CharXPos			;($CD57)Is the player at position 18, 12?
		CMP #$12				;($CD59)
		BNE CheckGrnDragon	  ;($CD5B)
		LDA CharYPos			;($CD5D)
		CMP #$0C				;($CD5F)
		BNE CheckGrnDragon	  ;($CD61)If not, exit this check.

		LDA #EN_AXEKNIGHT	   ;($CD63)Fight the axe knight!
		JMP InitFight		   ;($CD65)($E4DF)Begin fight sequence.

;----------------------------------------------------------------------------------------------------

CheckGrnDragon:
		LDA MapNumber		   ;($CD68)Is the player in the swamp cave?
		CMP #MAP_SWAMPCAVE	  ;($CD6A)
		BNE CheckGolem		  ;($CD6C)If not, exit this check.

		LDA CharXPos			;($CD6E)Is the player at position 4,14?
		CMP #$04				;($CD70)
		BNE CheckGolem		  ;($CD72)
		LDA CharYPos			;($CD74)
		CMP #$0E				;($CD76)
		BNE CheckGolem		  ;($CD78)If not, exit this check.

		LDA StoryFlags		  ;($CD7A)Has the green dragon already been defeated?
		AND #F_GDRG_DEAD		;($CD7C)
		BNE CheckGolem		  ;($CD7E)If so, exit this check.

		LDA #EN_GDRAGON		 ;($CD80)Fight the green dragon!
		JMP InitFight		   ;($CD82)($E4DF)Begin fight sequence.

;----------------------------------------------------------------------------------------------------

CheckGolem:
		LDA MapNumber		   ;($CD85)Is the player on the overworld map?
		CMP #MAP_OVERWORLD	  ;($CD87)
		BNE CheckBlockDmg	   ;($CD89)If not, exit this check.

		LDA CharXPos			;($CD8B)Is the player at position 73, 100?
		CMP #$49				;($CD8D)
		BNE CheckBlockDmg	   ;($CD8F)
		LDA CharYPos			;($CD91)
		CMP #$64				;($CD93)
		BNE CheckBlockDmg	   ;($CD95)If not, exit this check.

		LDA StoryFlags		  ;($CD97)Has golem already been defeated?
		AND #F_GOLEM_DEAD	   ;($CD99)
		BNE CheckBlockDmg	   ;($CD9B)If so, exit this check.

		LDA #EN_GOLEM		   ;($CD9D)Fight golem!
		JMP InitFight		   ;($CD9F)($E4DF)Begin fight sequence.

;----------------------------------------------------------------------------------------------------

CheckBlockDmg:
		JSR UpdateRandNum	   ;($CDA2)($C55B)Get random number.
		LDA CharXPos			;($CDA5)
		STA XTarget			 ;($CDA7)Get the player's X and Y position.
		LDA CharYPos			;($CDA9)
		STA YTarget			 ;($CDAB)

		JSR GetBlockID		  ;($CDAD)($AC17)Get description of block.
		LDA TargetResults	   ;($CDB0)
		STA ThisTile			;($CDB2)Get the current tile type player is standing on.

		CMP #BLK_TOWN		   ;($CDB4)Is the player on a map changing tile?
		BCC ChkOtherBlocks	  ;($CDB6)Town, castle or cave.
		CMP #BLK_BRIDGE		 ;($CDB8)
		BCS ChkOtherBlocks	  ;($CDBA)If not, branch.

		JMP CalcNextMap		 ;($CDBC)($D941)Calculate next map to load.

ChkOtherBlocks:
		LDA StoryFlags		  ;($CDBF)Is the dragonlord dead?
		AND #F_DGNLRD_DEAD	  ;($CDC1)If so, can't get hurt by map blocks.
		BEQ NextBlockCheck	  ;($CDC3)If not, branch to make more block checks.
		RTS					 ;($CDC5)

NextBlockCheck:
		LDA ThisTile			;($CDC6)Is player standing on a swampp block?
		CMP #BLK_SWAMP		  ;($CDC8)
		BNE ChkBlkSand		  ;($CDCA)If not, branch.

		LDA EqippedItems		;($CDCC)Player is standing on a swamp block.
		AND #AR_ARMOR		   ;($CDCE)Is the player wearing Erdrick's armor?
		CMP #AR_ERDK_ARMR	   ;($CDD0)
		BEQ ChkFight			;($CDD2)If so, branch. Take no damage.

		LDA #SFX_SWMP_DMG	   ;($CDD4)Swamp damage SFX.
		BRK					 ;($CDD6)
		.byte $04, $17		  ;($CDD7)($81A0)InitMusicSFX, bank 1.

		JSR RedFlashScreen	  ;($CDD9)($EE14)Flash the screen red.
		JSR WaitForNMI		  ;($CDDC)($FF74)Wait for VBlank interrupt.

		LDA HitPoints		   ;($CDDF)Player takes 2 points of damage.
		SEC					 ;($CDE1)
		SBC #$02				;($CDE2)Did player's HP go negative?
		BCS DoSwampDamage	   ;($CDE4)If not, branch to update HP.

		LDA #$00				;($CDE6)Player is dead. set HP to 0.

DoSwampDamage:
		STA HitPoints		   ;($CDE8)Update player HP.
		JSR WaitForNMI		  ;($CDEA)($FF74)Wait for VBlank interrupt.
		JSR LoadRegularBGPal	;($CDED)($EE28)Load the normal background palette.

		LDA HitPoints		   ;($CDF0)Is player still alive?
		BNE ChkFight			;($CDF2)If so, branch to check for random encounter.

		JSR Dowindow			;($CDF4)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($CDF7)Pop-up window.

		JMP InitDeathSequence   ;($CDF8)($EDA7)Player has died.

ChkFight:
		LDA #$0F				;($CDFB)Get random number.

ChkFight2:
		AND RandomNumberUB	  ;($CDFD)Is lower nibble 0?
		BEQ DoRandomFight	   ;($CDFF)If so, branch to start a random fight.
		RTS					 ;($CE01)

ChkBlkSand:
		CMP #BLK_SAND		   ;($CE02)Is the player on a sand block?
		BEQ ChkSandFight		;($CE04)If so, branch to check for a fight.

		CMP #BLK_HILL		   ;($CE06)Is the player on a hill block?
		BNE ChkBlkTrees		 ;($CE08)If not, branch to check for other block types.

		JSR WaitForNMI		  ;($CE0A)($FF74)Three frame pause when walking on hill block.
		JSR WaitForNMI		  ;($CE0D)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($CE10)($FF74)Wait for VBlank interrupt.

ChkSandFight:
		LDA #$07				;($CE13)Twice as likely to get into a fight in the sandy areas!
		BNE ChkFight2		   ;($CE15)Branch always to Recheck if a fight will happen.

ChkBlkTrees:
		CMP #BLK_TREES		  ;($CE17)Is player on a tree block?
		BEQ ChkRandomFight	  ;($CE19)if so, branch to check for enemy encounter.

		CMP #BLK_BRICK		  ;($CE1B)Is player on a brick block?
		BEQ ChkRandomFight	  ;($CE1D)if so, branch to check for enemy encounter.

		CMP #BLK_FFIELD		 ;($CE1F)Is player on a force field block?
		BNE ChkFight6		   ;($CE21)If not, branch to check for a random fight.

		LDA EqippedItems		;($CE23)Player is on a force field blck.
		AND #AR_ARMOR		   ;($CE25)Is player wearing Erdrick's armor?
		CMP #AR_ERDK_ARMR	   ;($CE27)If not, branch to do force field damage to player.
		BEQ ChkRandomFight	  ;($CE29)($CE5F)Check for enemy encounter.

		LDA #SFX_FFDAMAGE	   ;($CE2B)Force field damage SFX.
		BRK					 ;($CE2D)
		.byte $04, $17		  ;($CE2E)($81A0)InitMusicSFX, bank 1.

		LDA #$03				;($CE30)Prepare to flash the screen red for 3 frames.
		STA GenByte42		   ;($CE32)

		* JSR WaitForNMI		;($CE34)($FF74)Wait for VBlank interrupt.
		JSR RedFlashScreen	  ;($CE37)($EE14)Flash the screen red.
		JSR WaitForNMI		  ;($CE3A)($FF74)Wait for VBlank interrupt.
		JSR LoadRegularBGPal	;($CE3D)($EE28)Load the normal background palette.
		DEC GenByte42		   ;($CE40)Has 3 frames passed?
		BNE -				   ;($CE42)If not, branch to wait another frame.

		LDA HitPoints		   ;($CE44)Player takes 15 points of force field damage.
		SEC					 ;($CE46)
		SBC #$0F				;($CE47)Has the player HP gone negative?
		BCS +				   ;($CE49)If not, branch to move on.

		LDA #$00				;($CE4B)Set player HP to 0.
		BEQ +				   ;($CE4D)Branch always.

		* STA HitPoints		 ;($CE4F)Is player's HP 0?
		CMP #$00				;($CE51)If not, branch to check for a random fight.
		BNE ChkRandomFight	  ;($CE53)($CE5F)Check for enemy encounter.
		JSR LoadRegularBGPal	;($CE55)($EE28)Load the normal background palette.

		JSR Dowindow			;($CE58)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($CE5B)Pop-up window.

		JMP InitDeathSequence   ;($CE5C)($EDA7)Player has died.

;----------------------------------------------------------------------------------------------------

ChkRandomFight:
		LDA #$0F				;($CE5F)Prepare to check lower nibble of random number for a random fight.
		BNE ChkFight2		   ;($CE61)Branch always.

ChkFight6:
		LDA CharXPos			;($CE63)Is character on an odd X map position?
		LSR					 ;($CE65)
		BCS ChkFight5		   ;($CE66)If not, branch to check for normal chance for a fight.

		LDA CharYPos			;($CE68)Is character on an odd Y map position?
		LSR					 ;($CE6A)
		BCC HighFightChance	 ;($CE6B)Even X and even Y map location is higher fight chance.
		BCS NormFightChance	 ;($CE6D)Odd Y position. Check for normal fight chance.

ChkFight5:
		LDA CharYPos			;($CE6F)Is character on an odd Y map position?
		LSR					 ;($CE71)If not, branch for normal fight chance.
		BCC NormFightChance	 ;($CE72)Odd X and odd Y map location is higher fight chance.

HighFightChance:
		LDA #$1F				;($CE74)Higher chance for fight. Check 5 bits instead of 4.
		* BNE ChkFight2		 ;($CE76)Branch always.

NormFightChance:
		LDA #$0F				;($CE78)Prepare to check lower nibble of random number for a fight.
		BNE -				   ;($CE7A)Branch always.

;At this point, the player had initiated a fight. Need to check which map and where.

DoRandomFight:
		LDA MapNumber		   ;($CE7C)Is player on the overworld map?
		CMP #MAP_OVERWORLD	  ;($CE7E)
		BNE ChkDungeonFights	;($CE80)If not, branch to check other maps.

;This section of code calculates the proper enemies for the player's world map position.

		LDA CharYPos			;($CE82)Divide player's Y location on overworkd map by 15.
		STA DivideNumber1LB	 ;($CE84)This gives a number ranging from 0 to 7.
		LDA #$0F				;($CE86)The enemy zones on the overworld map are an 8X8 grid.
		STA DivideNumber2	   ;($CE88)
		JSR ByteDivide		  ;($CE8A)($C1F0)Divide a 16-bit number by an 8-bit number.

		LDA DivideNumber1LB	 ;($CE8D)Save Y data for enemy zone calculation.
		STA GenByte42		   ;($CE8F)

		LDA CharXPos			;($CE91)Divide player's X location on overworkd map by 15.
		STA DivideNumber1LB	 ;($CE93)This gives a number ranging from 0 to 7.
		LDA #$0F				;($CE95)The enemy zones on the overworld map are an 8X8 grid.
		STA DivideNumber2	   ;($CE97)
		JSR ByteDivide		  ;($CE99)($C1F0)Divide a 16-bit number by an 8-bit number.

		LDA GenByte42		   ;($CE9C)*4. 4 bytes per row in overworld enemy grid.
		ASL					 ;($CE9E)
		ASL					 ;($CE9F)The proper row in OvrWrldEnGrid is now known.
		STA EnemyOffsetset	  ;($CEA0)Next, calculate the desired byte from the row.

		LDA DivideNumber1LB	 ;($CEA2)Get the X position again for the overworld enemy grid.
		LSR					 ;($CEA4)/2 at the enemy data is stored in nibble wide data.
		CLC					 ;($CEA5)Add value to the Y position calculation.
		ADC EnemyOffsetset	  ;($CEA6)
		TAX					 ;($CEA8)We now have the proper byte index into OvrWrldEnGrid.

		LDA OvrWrldEnGrid,X	 ;($CEA9)Get the enemy zone data from OvrWrldEnGrid.
		STA EnemyOffsetset	  ;($CEAC)

		LDA DivideNumber1LB	 ;($CEAE)Since the enemy zone data is stored in nibbles, we need
		LSR					 ;($CEB0)to get the right nibble in the byte. Is this the right
		BCS +				   ;($CEB1)byte? If so, branch.

		LSR EnemyOffsetset	  ;($CEB3)
		LSR EnemyOffsetset	  ;($CEB5)Transfer upper nibble into the lower nibble.
		LSR EnemyOffsetset	  ;($CEB7)
		LSR EnemyOffsetset	  ;($CEB9)

		* LDA EnemyOffsetset	;($CEBB)Keep only the lower nibble. We now have the proper
		AND #$0F				;($CEBD)data from OvrWrldEnGrid.
		BNE GetEnemyRow		 ;($CEBF)

		JSR UpdateRandNum	   ;($CEC1)($C55B)Get random number.

		LDA ThisTile			;($CEC4)Is player in hilly terrain?
		CMP #BLK_HILL		   ;($CEC6)If not, branch. Another check will be done to avoid a
		BNE NormFightModifier   ;($CEC8)fight. 50% chance the fight may not happen.

		LDA RandomNumberUB	  ;($CECA)Player is in hilly terrain. Increased chance of fight!
		AND #$03				;($CECC)Do another check to avoid the fight. 25% chance the fight
		BEQ GetEnemyRow		 ;($CECE)may not happen. Is fight going to happen?
		RTS					 ;($CED0)If so, branch to calculate which enemy.

NormFightModifier:
		LDA RandomNumberUB	  ;($CED1)Player is not on hilly terrain.
		AND #$01				;($CED3)Do another check to avoid the fight. 50% chance the fight
		BEQ GetEnemyRow		 ;($CED5)may not happen. Is fight going to happen?
		RTS					 ;($CED7)If so, branch to calculate which enemy.

;This section of code calculates the proper enemies for the player's dungeon map position.

ChkDungeonFights:
		CMP #MAP_DLCSTL_GF	  ;($CED8)Is player on ground floor of the dragonlord's castle?
		BNE ChkHauksnessFight   ;($CEDA)
		LDA #$10				;($CEDC)If so, load proper offset to enemy data row in EnemyGroupsTbl.
		BNE GetEnemyRow		 ;($CEDE)Branch always.

ChkHauksnessFight:
		CMP #MAP_HAUKSNESS	  ;($CEE0)Is player in Hauksness?
		BNE ChkDLCastleFight	;($CEE2)
		LDA #$0D				;($CEE4)If so, load proper offset to enemy data row in EnemyGroupsTbl.
		BNE GetEnemyRow		 ;($CEE6)Branch always.

ChkDLCastleFight:
		CMP #MAP_DLCSTL_BF	  ;($CEE8)Is player on bottom floor of the dragonlord's castle?
		BNE ChkErdrickFight	 ;($CEEA)
		LDA #$12				;($CEEC)If so, load proper offset to enemy data row in EnemyGroupsTbl.
		BNE GetEnemyRow		 ;($CEEE)Branch always.

ChkErdrickFight:
		CMP #MAP_ERDRCK_B1	  ;($CEF0)Is player in Erdrick's cave?
		BCS NoEnemyMap		  ;($CEF2)If so, branch to exit. No enemies here.

		LDA MapType			 ;($CEF4)Is player in any one of the other dungeons?
		CMP #MAP_DUNGEON		;($CEF6)If so, branch to calculate proper enemy row.
		BEQ DoDungeonEnemy	  ;($CEF8)

NoEnemyMap:
		RTS					 ;($CEFA)No enemies on this map. Return without a fight.

DoDungeonEnemy:
		LDA MapNumber		   ;($CEFB)
		SEC					 ;($CEFD)Convert map number into a value that can be used to find
		SBC #$0F				;($CEFE)the index to the enemy data.
		TAX					 ;($CF00)
		LDA CaveEnIndexTbl,X	;($CF01)Get enemy index data byte. points to a row in EnemyGroupsTbl.

GetEnemyRow:
		STA EnemyOffsetset	  ;($CF04)This calculates the proper row of enemies to
		ASL					 ;($CF06)choose a fight from in EnemyGroupsTbl.
		ASL					 ;($CF07)
		CLC					 ;($CF08)
		ADC EnemyOffsetset	  ;($CF09)EnemyOffsetset * 5. 5 enemy entries per row.
		STA EnemyOffsetset	  ;($CF0B)

;All chances to evade the enemy has failed(except repel). Figure out which enemy to fight.
;At this point, we have the index to the row of enemies in EnemyGroupsTbl.

GetEnemyInRow:
		JSR UpdateRandNum	   ;($CF0D)($C55B)Get random number.
		LDA RandomNumberUB	  ;($CF10)
		AND #$07				;($CF12)Keep only 3 LSBs. Is number between 0 and 4? If not, branch
		CMP #$05				;($CF14)to get another random number as there are only 5 enemy slots
		BCS GetEnemyInRow	   ;($CF16)per enemy zone.

		ADC EnemyOffsetset	  ;($CF18)Add offset to the enemy row to get the specific enemy.
		TAX					 ;($CF1A)
		LDA EnemyGroupsTbl,X	;($CF1B)
		STA _EnNumber		   ;($CF1E)Store the enemy number and continue the fight preparations.

		LDA MapNumber		   ;($CF20)Is player on the overworld map?
		CMP #MAP_OVERWORLD	  ;($CF22)If so, there is a chance the fight can be repelled.
		BNE ReadyFight		  ;($CF24)If not, branch to prepare the fight.

		LDA RepelTimer		  ;($CF26)Is the repel spell active?
		BEQ ReadyFight		  ;($CF28)If not, branch to start fight.

		LDA DisplayedDefense	;($CF2A)
		LSR					 ;($CF2C)Get a copy of the player's defense / 2.
		STA GenByte3E		   ;($CF2D)

		LDX _EnNumber		   ;($CF2F)Get enemy's repel value from RepelTable.
		LDA RepelTable,X		;($CF31)
		SEC					 ;($CF34)Is enemy's repel value less than DisplayedDefense/2?
		SBC GenByte3E		   ;($CF35)
		BCC RepelSucceeded	  ;($CF37)If so, branch.  Enemy was successfully repeled.

		STA GenByte3E		   ;($CF39)Save difference between repel value and DisplayedDefense/2
		LDA RepelTable,X		;($CF3B)
		LSR					 ;($CF3E)
		CMP GenByte3E		   ;($CF3F)Is repel value/2 < repel value - DisplayedDefense/2?
		BCC ReadyFight		  ;($CF41)If not, branch to start fight. Repel unsuccessful.

RepelSucceeded:
		RTS					 ;($CF43)Repel scucceeded. Return without starting a fight.

ReadyFight:
		LDA _EnNumber		   ;($CF44)Load random enemy to fight.
		JMP InitFight		   ;($CF46)($E4DF)Begin fight sequence.

;----------------------------------------------------------------------------------------------------

DoNonCombatCommandWindow:
		JSR WaitForNMI		  ;($CF49)($FF74)Wait for VBlank interrupt.
		LDA FrameCounter		;($CF4C)
		AND #$0F				;($CF4E)Sync window with frame counter.
		CMP #$01				;($CF50)Is frame counter on the 16th frame?
		BEQ ShowNCCmdWindow	 ;($CF52)If so, branch to show the non-combat command window.
		JSR DoSprites		   ;($CF54)($B6DA)Update player and NPC sprites.
		JMP DoNonCombatCommandWindow;($CF57)($CF49)Loop until ready to show non-combat command window.

ShowNCCmdWindow:
		LDA #NPC_STOP		   ;($CF5A)Stop NPCs from moving.
		STA StopNPCMove		 ;($CF5C)

		JSR Dowindow			;($CF5E)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($CF61)Pop-up window.

		JSR Dowindow			;($CF62)($C6F0)display on-screen window.
		.byte WINDOW_CMD_NONCMB ;($CF65)Command window, non-combat.

		CMP #WINDOW_ABORT	   ;($CF66)Did player abort the menu?
		BNE NonCombatCommandSelected;($CF68)If not, branch.

ClearNonCombatCommandWindow:
		LDA #WINDOW_CMD_NONCMB  ;($CF6A)Remove command window from screen.
		JSR RemoveWindow		;($CF6C)($A7A2)Remove window from screen.

		LDA #NPC_MOVE		   ;($CF6F)
		STA StopNPCMove		 ;($CF71)Allow NPCs to start moving around again.
		RTS					 ;($CF73)

NonCombatCommandSelected:
		LDA WindowSelResults	;($CF74)Did player select STATUS?
		CMP #NCC_STATUS		 ;($CF76)If not, branch to check other selections.
		BNE CheckCmdWndResults  ;($CF78)($CFAF)Check some command window selection results.

		JSR LoadStats		   ;($CF7A)($F050)Update player attributes.
		JSR IncDescBuffer	   ;($CF7D)($D92E)Write #$01-#$0A to the description buffer

		LDA EqippedItems		;($CF80)
		LSR					 ;($CF82)
		LSR					 ;($CF83)
		LSR					 ;($CF84)Move equipped weapon to 3 LSBs.
		LSR					 ;($CF85)Value range is #$09-#$10.
		LSR					 ;($CF86)
		CLC					 ;($CF87)
		ADC #$09				;($CF88)
		STA DescBuf+$8		  ;($CF8A)

		LDA EqippedItems		;($CF8C)
		LSR					 ;($CF8E)
		LSR					 ;($CF8F)Move equipped armor to 3 LSBs.
		AND #$07				;($CF90)Value range is #$11-#$18.
		CLC					 ;($CF92)
		ADC #$11				;($CF93)
		STA DescBuf+$9		  ;($CF95)

		LDA EqippedItems		;($CF97)
		AND #$03				;($CF99)Move equipped shield to 2 LSBs.
		CLC					 ;($CF9B)Value range is #$19-#$1C.
		ADC #$19				;($CF9C)
		STA DescBuf+$A		  ;($CF9E)

		JSR Dowindow			;($CFA0)($C6F0)display on-screen window.
		.byte WINDOW_STATUS	 ;($CFA3)Status window.

		JSR WaitForBtnRelease   ;($CFA4)($CFE4)Wait for player to release then press joypad buttons.

		LDA #WINDOW_STATUS	  ;($CFA7)Remove status window from screen.
		JSR RemoveWindow		;($CFA9)($A7A2)Remove window from screen.
		JMP ClearNonCombatCommandWindow;($CFAC)($CF6A)Remove non-combat command window from screen.

;----------------------------------------------------------------------------------------------------

CheckCmdWndResults:
		CMP #NCC_TALK		   ;($CFAF)Did player select TALK from menu? If so, branch.
		BEQ CheckTalk		   ;($CFB1)($CFF9)Talk selected from command menu.

		CMP #NCC_STAIRS		 ;($CFB3)Did player select STAIRS from menu?
		BNE +				   ;($CFB5)If not, branch.
		JMP CheckStairs		 ;($CFB7)($D9AF)Stairs selected from command window.

		* CMP #NCC_DOOR		 ;($CFBA)Did player select DOOR from menu?
		BNE +				   ;($CFBC)If not, branch.
		JMP CheckDoor		   ;($CFBE)($DC42)Door selected from command menu.

		* CMP #NCC_SPELL		;($CFC1)Did player select SPELL from menu?
		BNE +				   ;($CFC3)If not, branch.
		JMP DoSpell			 ;($CFC5)($DA11)Spell selected from command menu.

		* CMP #NCC_ITEM		 ;($CFC8)Did player select ITEM from menu?
		BNE +				   ;($CFCA)If not, branch.
		JMP CheckInventory	  ;($CFCC)($DC1B)Item selected from command window.

		* CMP #NCC_SEARCH	   ;($CFCF)Did player select SEARCH from menu?
		BNE +				   ;($CFD1)If not, branch.
		JMP DoSearch			;($CFD3)($E103)Search selected from command window.

		* JMP DoTake			;($CFD6)($E1E3)Take selected from command window.

ResumeGamePlay:
		JSR WaitForBtnRelease   ;($CFD9)($CFE4)Wait for player to release then press joypad buttons.
		LDA #WINDOW_DIALOG	  ;($CFDC)Remove dialog window from screen.
		JSR RemoveWindow		;($CFDE)($A7A2)Remove window from screen.
		JMP ClearNonCombatCommandWindow;($CFE1)($CF6A)Remove non-combat command window from screen.

;----------------------------------------------------------------------------------------------------

WaitForBtnRelease:
		JSR WaitForNMI		  ;($CFE4)($FF74)Wait for VBlank interrupt.
		JSR GetJoypadStatus	 ;($CFE7)($C608)Get input button presses.
		LDA JoypadBtns		  ;($CFEA)
		BNE WaitForBtnRelease   ;($CFEC)Loop until no joypad buttons are pressed.

WaitForBtnPress:
		JSR WaitForNMI		  ;($CFEE)($FF74)Wait for VBlank interrupt.
		JSR GetJoypadStatus	 ;($CFF1)($C608)Get input button presses.
		LDA JoypadBtns		  ;($CFF4)
		BEQ WaitForBtnPress	 ;($CFF6)Loop until any joypad button is pressed.
		RTS					 ;($CFF8)

;----------------------------------------------------------------------------------------------------

CheckTalk:
		LDA CharDirection	   ;($CFF9)Get current direction player is facing.
		PHA					 ;($CFFC)

		JSR Dowindow			;($CFFD)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($D000)Dialog window.

		LDA CharXPos			;($D001)
		STA XTarget			 ;($D003)Make a copy of the player's X and Y coordinates.
		LDA CharYPos			;($D005)
		STA YTarget			 ;($D007)

		PLA					 ;($D009)Get player's direction.
		BNE CheckFacingRight	;($D00A)Is player facing up? If not branch to check other directions.

		DEC YTarget			 ;($D00C)Get position above player.
		JSR GetBlockID		  ;($D00E)($AC17)Get description of block.
		LDA TargetResults	   ;($D011)
		CMP #BLK_LRG_TILE	   ;($D013)Is player facing a store counter?
		BNE DoTalkResults	   ;($D015)If not, branch to check for an NPC.

		DEC _TargetY			;($D017)Set talk target for block beyond shop counter.
		JMP DoTalkResults	   ;($D019)

CheckFacingRight:
		CMP #DIR_RIGHT		  ;($D01C)Is player facing right?
		BNE CheckFacingDown	 ;($D01E)If not branch to check other directions.

		INC XTarget			 ;($D020)Get position to right of player.
		JSR GetBlockID		  ;($D022)($AC17)Get description of block.
		LDA TargetResults	   ;($D025)
		CMP #BLK_LRG_TILE	   ;($D027)Is player facing a store counter?
		BNE DoTalkResults	   ;($D029)

		INC _TargetX			;($D02B)Set talk target for block beyond shop counter.
		JMP DoTalkResults	   ;($D02D)

CheckFacingDown:
		CMP #DIR_DOWN		   ;($D030)Is player facing down?
		BNE DoFacingLeft		;($D032)If not branch to check other directions.

		INC YTarget			 ;($D034)Get position below player.
		JSR GetBlockID		  ;($D036)($AC17)Get description of block.
		LDA TargetResults	   ;($D039)
		CMP #BLK_LRG_TILE	   ;($D03B)Is player facing a store counter?
		BNE DoTalkResults	   ;($D03D)If not, branch to check for an NPC.

		INC _TargetY			;($D03F)Set talk target for block beyond shop counter.
		JMP DoTalkResults	   ;($D041)

DoFacingLeft:
		DEC XTarget			 ;($D044)Player must be facing left.
		JSR GetBlockID		  ;($D046)($AC17)Get description of block.
		LDA TargetResults	   ;($D049)
		CMP #BLK_LRG_TILE	   ;($D04B)Is player facing a store counter?
		BNE DoTalkResults	   ;($D04D)If not, branch to check for an NPC.

		DEC _TargetX			;($D04F)Set talk target for block beyond shop counter.

;----------------------------------------------------------------------------------------------------

DoTalkResults:
		LDA TargetResults	   ;($D051)Is the player talking to the princess in the swamp cave?
		CMP #BLK_PRINCESS	   ;($D053)
		BNE CheckNPCTalk		;($D055)If not, branch to check the NPCs.

		LDA _TargetX			;($D057)
		PHA					 ;($D059)Save the X and Y coordinates of princess Gwaelin.
		LDA _TargetY			;($D05A)
		PHA					 ;($D05C)

		JSR DoDialogLoBlock	 ;($D05D)($C7CB)Though art brave to rescue me, I'm Gwaelin...
		.byte $B5			   ;($D060)TextBlock12, entry 5.

PrincessRescueLoop:
		JSR DoDialogLoBlock	 ;($D061)($C7CB)Will thou take me to the castle...
		.byte $C5			   ;($D064)TextBlock13, entry 5.

		JSR Dowindow			;($D065)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D068)Yes/No selection window.

		BEQ +				   ;($D069)Branch if player agrees to take Gwaelin along.

		JSR DoDialogLoBlock	 ;($D06B)($C7CB)But thou must...
		.byte $B6			   ;($D06E)TextBlock12, entry 6.

JMP PrincessRescueLoop		  ;($D061)Loop until the player agrees to take Gwaelin.

		* LDA PlayerFlags	   ;($D072)
		ORA #F_GOT_GWAELIN	  ;($D074)Set flag indicating player is holding Gwaelin.
		STA PlayerFlags		 ;($D076)
		JSR WaitForNMI		  ;($D078)($FF74)Wait for VBlank interrupt.

		JSR DoSprites		   ;($D07B)($B6DA)Update player and NPC sprites.

		PLA					 ;($D07E)Restore Gwaelin's Y position.
		SEC					 ;($D07F)
		SBC CharYPos			;($D080)Get the Y position difference from player.
		ASL					 ;($D082)Convert block position to tile position.
		STA YPosFromCenter	  ;($D083)Y position of block to remove.

		PLA					 ;($D085)Restore Gwaelin's X position.
		SEC					 ;($D086)
		SBC CharXPos			;($D087)Get the X position difference from player.
		ASL					 ;($D089)Convert block position to tile position.
		STA XPosFromCenter	  ;($D08A)X position of block to remove.

		LDA #$00				;($D08C)Remove all 4 princess blocks from screen.
		STA BlkRemoveFlgs	   ;($D08E)
		JSR ModMapBlock		 ;($D090)($AD66)Change block on map.

		JSR DoDialogLoBlock	 ;($D093)($C7CB)Princess Gwaelin embraces thee...
		.byte $B7			   ;($D096)TextBlock12, entry 7.

		LDA #MSC_PRNCS_LOVE	 ;($D097)Gwaelin's love music.
		BRK					 ;($D099)
		.byte $04, $17		  ;($D09A)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($D09C)Wait for the music clip to end.
		.byte $03, $17		  ;($D09D)($815E)WaitForMusicEnd, bank 1.

		LDA #MSC_DUNGEON1	   ;($D09F)Dungeon 1 music.
		BRK					 ;($D0A1)
		.byte $04, $17		  ;($D0A2)($81A0)InitMusicSFX, bank 1.

		LDA #$B8				;($D0A4)TextBlock12, entry 8.
		JMP DoFinalDialog	   ;($D0A6)($D242)I'm so happy...

;----------------------------------------------------------------------------------------------------

CheckNPCTalk:
		LDY #$00				;($D0A9)Prepare to loop through all NPC slots.

NPCTalkLoop:
		LDA _NPCXPos,Y		  ;($D0AB)Check NPCs Y position.
		AND #$1F				;($D0AE)Widest map is only 32 blocks.
		CMP _TargetX			;($D0B0)Is the X position valid?
		BNE CheckNextNPC		;($D0B2)If not, branch to check the next NPC slot.

		LDA _NPCYPos,Y		  ;($D0B4)Check NPCs X position.
		AND #$1F				;($D0B7)Tallest map is only 32 blocks.
		CMP _TargetY			;($D0B9)Is the Y position valid?
		BNE CheckNextNPC		;($D0BB)If not, branch to check the next NPC slot.

		LDA _NPCXPos,Y		  ;($D0BD)Make sure the NPC slot contains a valid NPC and
		BNE JmpValidateNPC	  ;($D0C0)is not empty.  If all 3 bytes are 0, the slot is
		LDA _NPCYPos,Y		  ;($D0C2)empty.
		BNE JmpValidateNPC	  ;($D0C5)
		LDA _NPCMidPos,Y		;($D0C7)
		BNE JmpValidateNPC	  ;($D0CA)
		JMP NoTalk			  ;($D0CC)($D1ED)No one to talk to in that direction.

JmpValidateNPC:
		JMP ValidateNPC		 ;($D0CF)($D0DC)Do more checks to ensure valid NPC.

CheckNextNPC:
		INY					 ;($D0D2)
		INY					 ;($D0D3)Move to next NPC(3 bytes per NPC).
		INY					 ;($D0D4)

		CPY #$3C				;($D0D5)Have all 20 NPC slots been checked?
		BNE NPCTalkLoop		 ;($D0D7)If not, branch to check the next slot.

		JMP NoTalk			  ;($D0D9)($D1ED)No one to talk to in that direction.

;----------------------------------------------------------------------------------------------------

ValidateNPC:
		STY NPCOffsetset		;($D0DC)Get NPC offset.
		CPY #$1E				;($D0DE)Lower NPC slots are for moving NPCs.
		BCC CheckMobNPC		 ;($D0E0)If lower slot, branch to check for valid mobile NPC.

		TYA					 ;($D0E2)
		SEC					 ;($D0E3)This is a static NPC.  Move offset down in preparation
		SBC #$1C				;($D0E4)to calculate the index into the NPCStaticPointerTable.
		TAY					 ;($D0E6)

		LDA MapNumber		   ;($D0E7)Subtract 4 from the map number and make sure it is
		SEC					 ;($D0E9)less than or equal to 11.
		SBC #$04				;($D0EA)This is because valid NPCs are only on map numbers
		CMP #$0B				;($D0EC)4 through 14.
		BCC GetStatNPCPtr	   ;($D0EE)Check for valid static NPC.

		JMP NoTalk			  ;($D0F0)($D1ED)No one to talk to in that direction.

GetStatNPCPtr:
		ASL					 ;($D0F3)*2. Pointers into NPC tables are 2 bytes.
		TAX					 ;($D0F4)

		LDA NPCStaticPointerTable,X;($D0F5)
		STA GenPtr3CLB		  ;($D0F8)Get pointer to static NPC for the current map.
		LDA NPCStaticPointerTable+1,X;($D0FA)
		STA GenPtr3CUB		  ;($D0FD)
		JMP PrepTalk			;($D0FF)($D11C)Do next phase of NPC dialog.

CheckMobNPC:
		INY					 ;($D102)+2. Need to check 3rd byte in table entry.
		INY					 ;($D103)

		LDA MapNumber		   ;($D104)Subtract 4 from the map number and make sure it is
		SEC					 ;($D106)less than or equal to 11.
		SBC #$04				;($D107)This is because valid NPCs are only on map numbers
		CMP #$0B				;($D109)4 through 14.
		BCC GetMobNPCPtr		;($D10B)Check for valid mobile NPC.

		JMP NoTalk			  ;($D10D)($D1ED)No one to talk to in that direction.

GetMobNPCPtr:
		ASL					 ;($D110)*2. Pointers into NPC tables are 2 bytes.
		TAX					 ;($D111)

		LDA NPCMobilePointerTable,X;($D112)
		STA GenPtr3CLB		  ;($D115)Get pointer to mobile NPC for the current map.
		LDA NPCMobilePointerTable+1,X;($D117)
		STA GenPtr3CUB		  ;($D11A)

PrepTalk:
		LDA NPCOffsetset		;($D11C)Get target NPC number.
		JSR NPCFacePlayer	   ;($D11E)($C04A)Make the NPC face the player.

		TYA					 ;($D121)Save NPC index on stack.
		PHA					 ;($D122)

		LDA GenPtr3CLB		  ;($D123)
		PHA					 ;($D125)Save NPC data pointer on stack.
		LDA GenPtr3CUB		  ;($D126)
		PHA					 ;($D128)

		JSR DoSprites		   ;($D129)($B6DA)Update player and NPC sprites.

		PLA					 ;($D12C)
		STA GenPtr3CUB		  ;($D12D)Restore NPC data pointer from stack.
		PLA					 ;($D12F)
		STA GenPtr3CLB		  ;($D130)

		PLA					 ;($D132)Restore NPC index from stack.
		TAY					 ;($D133)

		LDA StoryFlags		  ;($D134)Is the dragonlord dead?
		AND #F_DGNLRD_DEAD	  ;($D136)
		BEQ RegularDialog	   ;($D138)If not, branch for normal dialog.

		LDA MapNumber		   ;($D13A)Is player in Tantgel castle after defeating the dragonlord?
		CMP #MAP_TANTCSTL_GF	;($D13C)
		BNE TantEndDialog	   ;($D13E)If not, branch to do other post dragonlord dialog.

		JSR DoDialogHiBlock	 ;($D140)($C7C5)King Lorik awaits...
		.byte $21			   ;($D143)TextBlock19, entry 1

		JMP ResumeGamePlay	  ;($D144)($CFD9)Give control back to player.

TantEndDialog:
		LDA (GenPtr3C),Y		;($D147)There is a NPC who was looking for Gwaelin and is almost
		CMP #$64				;($D149)dead.  I guess he finally dies when the dragonlord is defeated.
		BNE RandEndDialog	   ;($D14B)Branch if not talking to that one specific NPC.

		JSR DoDialogHiBlock	 ;($D14D)($C7C5)"...."
		.byte $15			   ;($D150)TextBlock18, entry 5.

		JMP ResumeGamePlay	  ;($D151)($CFD9)Give control back to player.

RandEndDialog:
		JSR UpdateRandNum	   ;($D154)($C55B)Get a random number.
		LDA RandomNumberUB	  ;($D157)
		LSR					 ;($D159)Randomly choose text based on the LSB of
		BCC AlternateDialog	 ;($D15A)the number if the dragonlord is dead.

		JSR DoDialogHiBlock	 ;($D15C)($C7C5)Hurray! Hurray!...
		.byte $1F			   ;($D15F)TextBlock18, entry 15.

		JMP ResumeGamePlay	  ;($D160)($CFD9)Give control back to player.

AlternateDialog:
		JSR DoDialogHiBlock	 ;($D163)($C7C5)Thou has brought us peace...
		.byte $20			   ;($D166)TextBlock19, entry 0.

		JMP ResumeGamePlay	  ;($D167)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

RegularDialog:
		LDA (GenPtr3C),Y		;($D16A)Is this weapon shop dialog?
		CMP #$07				;($D16C)If so, jump to do weapon shop dialog.
		BCS +				   ;($D16E)
		JMP WeaponsDialog	   ;($D170)($D553)Weapon shop dialog.

		* CMP #$0C			  ;($D173)Is this tool shop dialog?
		BCS +				   ;($D175)If so, jump to do tool shop dialog.
		JMP ToolsDialog		 ;($D177)($D6A7)Tool shop dialog.

		* CMP #$0F			  ;($D17A)Is this key shop dialog?
		BCS +				   ;($D17C)If so, jump to do key shop dialog.
		JMP KeysDialog		  ;($D17E)($D7ED)Key shop dialog.

		* CMP #$11			  ;($D181)Is this fairy water shop dialog?
		BCS +				   ;($D183)If so, jump to do fairy water shop dialog.
		JMP FairyDialog		 ;($D185)($D843)Fairy water shop dialog.

		* CMP #$16			  ;($D188)Is this inn dialog?
		BCS +				   ;($D18A)If so, jump to do inn dialog.
		JMP InnDialog		   ;($D18C)($D895)Inn dialog.

		* CMP #$5E			  ;($D18F)Is this other misc. dialog?
		BCS CheckYesNoDialog	;($D191)($D1C5)If so, branch to break the dialog down further.

;----------------------------------------------------------------------------------------------------

;From here, dialog between #$16 and #$5D is processed.

		PHA					 ;($D193)Save dialog control byte on stack.

		LDA PlayerFlags		 ;($D194)Has the player left the throne room for the first time yet?
		AND #F_LEFT_THROOM	  ;($D196)
		BNE DoVariousDialog1	;($D198)If so, branch.

		PLA					 ;($D19A)Is this one of the throne room stationary guards?
		CMP #$23				;($D19B)
		BNE ThrnRmDialog2	   ;($D19D)If not, branch to check other guard.

		JSR DoDialogHiBlock	 ;($D19F)($C7C5)East of this castle is a town...
		.byte $01			   ;($D1A2)TextBlock17, entry 1.

		JMP ResumeGamePlay	  ;($D1A3)($CFD9)Give control back to player.

ThrnRmDialog2:
		CMP #$24				;($D1A6)Is this the other throne room stationary guard?
		BNE DoVariousDialog2	;($D1A8)If not, branch.

		JSR DoDialogHiBlock	 ;($D1AA)($C7C5)In a treasure chest a key will be found...
		.byte $00			   ;($D1AD)TextBlock17, entry 0.

		JMP ResumeGamePlay	  ;($D1AE)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

DoVariousDialog1:
		PLA					 ;($D1B1)Save a copy of the dialog control byte on the stack.

DoVariousDialog2:
		PHA					 ;($D1B2)Restore dialog control byte.
		CLC					 ;($D1B3)
		ADC #$2F				;($D1B4)Add offset to the byte to find proper text block entry.
		JSR DoMidDialog		 ;($D1B6)($C7BD)Do any number of Dialogs.

		PLA					 ;($D1B9)Is this TextBlock5, entry 9 which talks about the legend
		CMP #$1A				;($D1BA)of the rainbow bridge?
		BNE EndVariousDialog	;($D1BC)If not, branch to exit dialog routine.

		JSR DoDialogLoBlock	 ;($D1BE)($C7CB)It's a legend...
		.byte $B0			   ;($D1C1)TextBlock12, entry 0.

EndVariousDialog:
		JMP ResumeGamePlay	  ;($D1C2)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

CheckYesNoDialog:
		CMP #$62				;($D1C5)Is this Dialog wih a yes/no window?
		BCS ChkPrncsDialog1	 ;($D1C7)If not, branch to check for various princess dialog.

		CLC					 ;($D1C9)Calculate proper text block for yes/no dialog.
		ADC #$2F				;($D1CA)Store a copy of the dialog control byte.
		STA DialogTemp		  ;($D1CC)
		JSR DoMidDialog		 ;($D1CE)($C7BD)TextBlock9, entry 13 - TextBlock10, entry 0.

		JSR Dowindow			;($D1D1)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D1D4)Yes/no selection window.

		BNE NoRespDialog		;($D1D5)Did player select yes? If so, branch.

		LDA DialogTemp		  ;($D1D7)Get "yes" dialog response.
		CLC					 ;($D1D9)
		ADC #$05				;($D1DA)
		JSR DoMidDialog		 ;($D1DC)($C7BD)TextBlock10, entries 1 - 4.

		JMP ResumeGamePlay	  ;($D1DF)($CFD9)Give control back to player.

NoRespDialog:
		LDA DialogTemp		  ;($D1E2)Get "no" dialog response.
		CLC					 ;($D1E4)
		ADC #$0A				;($D1E5)
		JSR DoMidDialog		 ;($D1E7)($C7BD)TextBlock10, entries 5 - 8.

		JMP ResumeGamePlay	  ;($D1EA)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

NoTalk:
		JSR DoDialogLoBlock	 ;($D1ED)($C7CB)There is no one there...
		.byte $0F			   ;($D1F0)TextBlock1, entry 15.

		JMP ResumeGamePlay	  ;($D1F1)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

ChkPrncsDialog1:
		BNE ChkPrncsDialog2	 ;($D1F4)Talkging to the guard looking for Gwaelin? if not, branch.

		LDA PlayerFlags		 ;($D1F6)Has Gwaelin been returned or being carried?
		AND #F_DONE_GWAELIN	 ;($D1F8)
		BNE PrincessSaved1	  ;($D1FA)If so, branch.

PrincessNotSaved:
		LDA #$9B				;($D1FC)TextBlock10, entry 11.
		BNE DoFinalDialog	   ;($D1FE)($D242)Where oh where can I find princess Gwaelin...

PrincessSaved1:
		LDA #$9C				;($D200)TextBlock10, entry 12.
		BNE DoFinalDialog	   ;($D202)($D242)Thank you for saving the princess...

ChkPrncsDialog2:
		CMP #$63				;($D204)Check for another princess dialog.
		BNE ChkPrncsDialog3	 ;($D206)

		LDA PlayerFlags		 ;($D208)Has the princess been saved?
		AND #F_DONE_GWAELIN	 ;($D20A)
		BEQ PrincessNotSaved	;($D20C)If not, branch.

		LDA #$9D				;($D20E)TextBlock10, entry 13.
		BNE DoFinalDialog	   ;($D210)($D242)My dearest Gwaelin! I hate thee...

ChkPrncsDialog3:
		CMP #$64				;($D212)Check for another princess dialog.
		BNE ChkPrncsDialog4	 ;($D214)

		LDA PlayerFlags		 ;($D216)Has the princess been saved?
		AND #F_DONE_GWAELIN	 ;($D218)
		BNE PrincessSaved2	  ;($D21A)If so, branch.

		LDA #$9E				;($D21C)TextBlock10, entry 14.
		BNE DoFinalDialog	   ;($D21E)($D242)Tell the king the search for his daughter has failed...

PrincessSaved2:
		LDA #$9F				;($D220)TextBlock10, entry 15.
		BNE DoFinalDialog	   ;($D222)($D242)Who touches me? I cannot see or hear...

ChkPrncsDialog4:
		CMP #$65				;($D224)Check for another princess dialog.
		BNE WzdGuardDialog	  ;($D226)If not princess dialog, branch to next dialog type.

		LDA PlayerFlags		 ;($D228)Has the princess been saved?
		AND #F_DONE_GWAELIN	 ;($D22A)
		BNE PrincessSaved3	  ;($D22C)If so, branch.

		JSR DoDialogLoBlock	 ;($D22E)($C7CB)Dost thou know about princess Gwaelin...
		.byte $A0			   ;($D231)TextBlock11, entry 0.

		JSR Dowindow			;($D232)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D235)Yes/No selection window.

		BEQ SavePrincessDialog  ;($D236)Player has heard about the princess.  Branch to skip.

		JSR DoDialogLoBlock	 ;($D238)($C7CB)Half a year has passed since the princess was kidnapped...
		.byte $A1			   ;($D23B)TextBlock11, entry 1.

SavePrincessDialog:
		LDA #$A2				;($D23C)TextBlock11, entry 2.
		BNE DoFinalDialog	   ;($D23E)($D242)Please save the princess...

PrincessSaved3:
		LDA #$A3				;($D240)TextBlock11, entry 3. Oh, brave player...

;----------------------------------------------------------------------------------------------------

DoFinalDialog:
		JSR DoMidDialog		 ;($D242)($C7BD)Call dialog function.
		JMP ResumeGamePlay	  ;($D245)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

WzdGuardDialog:
		CMP #$66				;($D248)Is the player talking to a chest guarding wizard?
		BNE ChkCursedDialog	 ;($D24A)If not, branch.

		LDA #ITM_STNS_SNLGHT	;($D24C)Check if stones of sunlight are already in possesion.
		JSR CheckForInvItem	 ;($D24E)($E055)Check inventory for item.
		CMP #ITM_NOT_FOUND	  ;($D251)
		BNE HaveUniqueItem	  ;($D253)If so, branch to display "go away" message.

		LDA #ITM_RNBW_DROP	  ;($D255)Check if rainbow drop is already in possesion.
		JSR CheckForInvItem	 ;($D257)($E055)Check inventory for item.
		CMP #ITM_NOT_FOUND	  ;($D25A)
		BNE HaveUniqueItem	  ;($D25C)If so, branch to display "go away" message.

		JSR DoDialogLoBlock	 ;($D25E)($C7CB)I have been waiting long for someone such as thee...
		.byte $A4			   ;($D261)TextBlock11, entry 4.

		LDA #$C6				;($D262)TextBlock13, entry 6.
		BNE DoFinalDialog	   ;($D264)($D242)Take the treasure chest...

HaveUniqueItem:
		LDA #$A5				;($D266)TextBlock11, entry 5.
		BNE DoFinalDialog	   ;($D268)($D242)Though hast no business here. Go away...

;----------------------------------------------------------------------------------------------------

ChkCursedDialog:
		CMP #$67				;($D26A)Is the player talking to the curse remover?
		BNE ChkWeaponDialog	 ;($D26C)If not, branch.

		LDA ModsnSpells		 ;($D26E)Is the player cursed?
		AND #$C0				;($D270)
		BNE CursedDialog		;($D272)If so, branch to curse removal dialog.

		LDA #$A6				;($D274)TextBlock11, entry 6.
		BNE DoFinalDialog	   ;($D276)($D242)If thou art cursed, come again...

CursedDialog:
		JSR DoDialogLoBlock	 ;($D278)($C7CB)I will free thee from thy curse...
		.byte $A7			   ;($D27B)TextBlock11, entry 7.

		LDA ModsnSpells		 ;($D27C)Is player cursed by the death necklace?
		BPL RemoveCrsBelt	   ;($D27E)If not, branch.

		LDA #ITM_DTH_NEKLACE	;($D280)Remove death necklace from inventory.
		JSR RemoveInvItem	   ;($D282)($E04B)Remove item from inventory.

RemoveCrsBelt:
		BIT ModsnSpells		 ;($D285)Is player cursed by the cursed belt?
		BVC ClearCurseFlags	 ;($D287)If not, branch.

		LDA #ITM_CRSD_BELT	  ;($D289)Remove cursed belt from inventory.
		JSR RemoveInvItem	   ;($D28B)($E04B)Remove item from inventory.

ClearCurseFlags:
		LDA ModsnSpells		 ;($D28E)
		AND #$3F				;($D290)Clear cursed status flags from player.
		STA ModsnSpells		 ;($D292)

		LDA #$A8				;($D294)TextBlock11, entry 8.
		BNE DoFinalDialog	   ;($D296)($D242)Now, go...

;----------------------------------------------------------------------------------------------------

ChkWeaponDialog:
		CMP #$68				;($D298)Is the player talking to the weapon identifying wizard?
		BNE ChkRingDialog	   ;($D29A)If not, branch.

		LDA EqippedItems		;($D29C)Does the player have Erdrick's sword?
		AND #WP_WEAPONS		 ;($D29E)
		CMP #WP_ERDK_SWRD	   ;($D2A0)
		BEQ GotSwordDialog	  ;($D2A2)If so, branch.

		LDA #$A9				;($D2A4)TextBlock11, entry 9.
		BNE DoFinalDialog	   ;($D2A6)($D242)Thou cannot defeat the dragonlord with such weapons...

GotSwordDialog:
		LDA #$AA				;($D2A8)TextBlock11, entry 10.
		BNE DoFinalDialog	   ;($D2AA)($D242)Finally, thou hast obtained it, player...

;----------------------------------------------------------------------------------------------------

ChkRingDialog:
		CMP #$69				;($D2AC)Is player talking to the ring identifying NPC?
		BNE ChkMagicDialog	  ;($D2AE)If not, branch.

		LDA #ITM_FTR_RING	   ;($D2B0)Does player have the fighter's ring in inventory?
		JSR CheckForInvItem	 ;($D2B2)($E055)Check inventory for item.
		CMP #ITM_NOT_FOUND	  ;($D2B5)
		BNE RingInInventory	 ;($D2B7)If so, branch.

		LDA ModsnSpells		 ;($D2B9)
		AND #$DF				;($D2BB)Remove fighter's ring equipped status if it is not in inventory.
		STA ModsnSpells		 ;($D2BD)

RingInInventory:
		LDA ModsnSpells		 ;($D2BF)
		AND #F_FTR_RING		 ;($D2C1)Branch if wearing the fighter's ring.
		BNE WearingRing		 ;($D2C3)

		LDA #$AC				;($D2C5)TextBlock11, entry 12.
		JMP DoFinalDialog	   ;($D2C7)($D242)All true warriors wear a ring...

WearingRing:
		LDA #$AB				;($D2CA)TextBlock11, entry 11.
		JMP DoFinalDialog	   ;($D2CC)($D242)Is that a wedding ring...

;----------------------------------------------------------------------------------------------------

ChkMagicDialog:
		CMP #$6A				;($D2CF)Is player talking to the MP restoring wizard?
		BNE ErdTknDialog		;($D2D1)If not, branch.

		JSR DoDialogLoBlock	 ;($D2D3)($C7CB)Player's coming was foretold by legend...
		.byte $AD			   ;($D2D6)TextBlock11, entry 13.

		JSR BWScreenFlash	   ;($D2D7)($DB37)Flash screen in black and white.
		LDA DisplayedMaxMP	  ;($D2DA)
		STA MagicPoints		 ;($D2DC)Max out player's MP.

		JSR Dowindow			;($D2DE)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($D2E1)Pop-up window.

		JMP ResumeGamePlay	  ;($D2E2)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

ErdTknDialog:
		CMP #$6B				;($D2E5)Is the player talking to the Erdrick's token NPC?
		BNE RainStaffDialog	 ;($D2E7)If not, branch.

		JSR DoDialogLoBlock	 ;($D2E9)($C7CB)Let us wish the warrior well...
		.byte $4C			   ;($D2EC)TextBlock5, entry 12.

		JSR DoDialogLoBlock	 ;($D3ED)($C7CB)Thou may go and search...
		.byte $AE			   ;($D2F0)TextBlock11, entry 14

		JSR DoDialogLoBlock	 ;($D2F1)($C7CB)
		.byte $AF			   ;($D2F4)TextBlock11, entry 15.

		JMP ResumeGamePlay	  ;($D2F5)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

RainStaffDialog:
		CMP #$6C				;($D2F8)Is the player talking to the staff of rain guardian?
		BNE RnbwDrpDialog	   ;($D2FA)If not, branch.

		LDA #ITM_RNBW_DROP	  ;($D2FC)Does the player already have the rainbow drop?
		JSR CheckForInvItem	 ;($D2FE)($E055)Check inventory for item.
		CMP #ITM_NOT_FOUND	  ;($D301)
		BNE HaveItemDialog	  ;($D303)If so, branch.

		LDA #ITM_STFF_RAIN	  ;($D305)Does the player already have the staff of rain?
		JSR CheckForInvItem	 ;($D307)($E055)Check inventory for item.
		CMP #ITM_NOT_FOUND	  ;($D30A)
		BEQ ChkSlvrHarp		 ;($D30C)If so, branch.

HaveItemDialog:
		LDA #$A5				;($D30E)TextBlock11, entry 5. Thou hast no business here...

NoItemGive:
		JSR DoMidDialog		 ;($D310)($C7BD)Display dialog on screen.
		JMP ResumeGamePlay	  ;($D313)($CFD9)Give control back to player.

ChkSlvrHarp:
		LDA #ITM_SLVR_HARP	  ;($D316)Does the player have the silver harp?
		JSR CheckForInvItem	 ;($D318)($E055)Check inventory for item.
		CMP #ITM_NOT_FOUND	  ;($D31B)
		BEQ HarpNotFound		;($D31D)If not, branch.

		JSR DoDialogLoBlock	 ;($D31F)($C7CB)It's a legend...
		.byte $B2			   ;($D322)TextBlock12, entry 2.

		JSR DoDialogLoBlock	 ;($D323)($C7CB)I have been waiting long for thee...
		.byte $A4			   ;($D326)TextBlock11, entry 4.

		JSR DoDialogLoBlock	 ;($D327)($C7CB)Take the treasure chest...
		.byte $C6			   ;($D32A)TextBlock13, entry 6.

		LDA #ITM_SLVR_HARP	  ;($D32B)Remove silver harp from inventory.
		JSR RemoveInvItem	   ;($D32D)($E04B)Remove item from inventory.

		LDA #$00				;($D330)
		STA NPCXPos+$1E		 ;($D332)Remove NPC from screen.
		STA NPCYPos+$1E		 ;($D334)
		STA NPCMidPos+$1E	   ;($D336)

		JSR WaitForNMI		  ;($D338)($FF74)Wait for VBlank interrupt.
		JSR DoSprites		   ;($D33B)($B6DA)Update player and NPC sprites.

		JMP ResumeGamePlay	  ;($D33E)($CFD9)Give control back to player.

HarpNotFound:
		LDA #$B1				;($D341)TextBlock12, entry 1.
		BNE NoItemGive		  ;($D343)Thy bravery must be proven, thus I propose a test...

;----------------------------------------------------------------------------------------------------

RnbwDrpDialog:
		CMP #$6D				;($D345)Is the player talking to the rainbow drop guardian?
		BNE KingDialog		  ;($D347)If not, branch.

		LDA #ITM_RNBW_DROP	  ;($D349)Does player already have the rainbow drop?
		JSR CheckForInvItem	 ;($D34B)($E055)Check inventory for item.
		CMP #ITM_NOT_FOUND	  ;($D34E)
		BNE HaveItemDialog	  ;($D350)If so, branch.

		LDA #ITM_ERDRICK_TKN	;($D352)Does the player have Erdrick's token?
		JSR CheckForInvItem	 ;($D354)($E055)Check inventory for item.
		CMP #ITM_NOT_FOUND	  ;($D357)
		BNE HaveErdToken		;($D359)If so, branch.

		JSR DoDialogLoBlock	 ;($D35B)($C7CB)In thy task thou hast failed...
		.byte $B3			   ;($D35E)TextBlock12, entry 3.

		JSR BWScreenFlash	   ;($D35F)($DB37)Flash screen in black and white.
		JMP CheckMapExit		;($D362)($B228)Force player to exit the map.

HaveErdToken:
		LDA #ITM_STNS_SNLGHT	;($D365)Does the player have the stones of sunlight?
		JSR CheckForInvItem	 ;($D367)($E055)Check inventory for item.
		CMP #ITM_NOT_FOUND	  ;($D36A)
		BEQ NoRnbwDrpDialog	 ;($D36C)If not, branch.

		LDA #ITM_STFF_RAIN	  ;($D36E)Does the player have the staff of rain?
		JSR CheckForInvItem	 ;($D370)($E055)Check inventory for item.
		CMP #ITM_NOT_FOUND	  ;($D373)
		BEQ NoRnbwDrpDialog	 ;($D375)If not, branch.

		JSR DoDialogLoBlock	 ;($D377)($C7CB)Now the sun and rain shall meet...
		.byte $B4			   ;($D37A)TextBlock12, entry 4.

		LDA #ITM_STNS_SNLGHT	;($D37B)Remove the stones of sunlight from inventory.
		JSR RemoveInvItem	   ;($D37D)($E04B)Remove item from inventory.

		LDA #ITM_STFF_RAIN	  ;($D380)Remove the staff of rain from inventory.
		JSR RemoveInvItem	   ;($D382)($E04B)Remove item from inventory.

		LDA #ITM_RNBW_DROP	  ;($D385)Add rainbow drop to inventory.
		JSR AddInvItem		  ;($D387)($E01B)Add item to inventory.

		JSR WaitForNMI		  ;($D38A)($FF74)Wait for VBlank interrupt.
		LDA #%00011001		  ;($D38D)
		STA PPUControl1		 ;($D38F)Set display to greyscale colors.

		LDX #$1E				;($D392)make screen greyscale for 30 frames.
		* JSR WaitForNMI		;($D394)($FF74)Wait for VBlank interrupt.
		DEX					 ;($D397)Done with black and white screen?
		BNE -				   ;($D398)If not, branch to do another frame.

		LDA #%00011000		  ;($D39A)Set display to RGB colors.
		STA PPUControl1		 ;($D39C)

		JMP ResumeGamePlay	  ;($D39F)($CFD9)Give control back to player.

NoRnbwDrpDialog:
		JSR DoDialogLoBlock	 ;($D3A2)($C7CB)When the sun and rain meet, a bridge will appear...
		.byte $49			   ;($D3A5)TextBlock5, entry 9.

		LDA #$AE				;($D3A6)TextBlock11, entry 14. I have been waiting long for thee...
		JMP NoItemGive		  ;($D3A8)($D310)Player does not meet requirements to get rainbow drop.

;----------------------------------------------------------------------------------------------------

KingDialog:
		CMP #$6E				;($D3AB)Is the player talking to the king?
		BEQ DoKingDialog		;($D3AD)If so, branch.
		JMP PrincessDialog	  ;($D3AF)Else check if player is talking to the princess.

DoKingDialog:
		LDA PlayerFlags		 ;($D3B2)Is the player carrying Gwaelin?
		AND #F_GOT_GWAELIN	  ;($D3B4)
		BEQ KingDialog2		 ;($D3B6)If not, branch.

		JSR DoDialogLoBlock	 ;($D3B8)($C7CB)I am grateful for my daughter's return...
		.byte $B9			   ;($D3BB)TextBlock12, entry 9.

		LDA #ITM_GWAELIN_LVE	;($D3BC)Try to give player Gwaelin's love.
		JSR AddInvItem		  ;($D3BE)($E01B)Add item to inventory.

		CPX #INV_FULL		   ;($D3C1)Was Gwaelin's love successfully given?
		BNE KingPrncsDialog	 ;($D3C3)If so, branch.

		LDX #$00				;($D3C5)Inventory full.  Prepare to take an item.

TakeItemLoop:
		LDA InvListTbl,X		;($D3C7)Check for inventory item.
		JSR CheckForInvItem	 ;($D3CA)($E055)Check inventory for item.

		CMP #ITM_NOT_FOUND	  ;($D3CD)Is it in the player's inventory?
		BNE TakeItemFound	   ;($D3CF)If so, branch to remove it.

		INX					 ;($D3D1)Has all 8 inventory slots been checked?
		CPX #$07				;($D3D2)
		BNE TakeItemLoop		;($D3D4)If not, branch to check the next one.

		BEQ KingPrncsDialog	 ;($D3D6)No non-critical items found, branch.

TakeItemFound:
		LDA InvListTbl,X		;($D3D8)Save a copy of item to take from player's inventory.
		PHA					 ;($D3DB)
		JSR RemoveInvItem	   ;($D3DC)($E04B)Remove item from inventory.
		PLA					 ;($D3DF)Restore a copy of item taken.

		CLC					 ;($D3E0)Get description of item taken.
		ADC #$31				;($D3E1)
		JSR GetDescriptionByte  ;($D3E3)($DBF0)Load byte for item dialog description.

		LDA #ITM_GWAELIN_LVE	;($D3E6)Add Gwaelin's love to player's inventory.
		JSR AddInvItem		  ;($D3E8)($E01B)Add item to inventory.

		JSR DoDialogLoBlock	 ;($D3EB)($C7CB)And I would like to have something of thine...
		.byte $BA			   ;($D3EE)TextBlock12, entry 10.

KingPrncsDialog:
		JSR DoDialogLoBlock	 ;($D3EF)($C7CB)Even when we are parted by great distances...
		.byte $BB			   ;($D3F2)TextBlock12, entry 11.

		JSR DoDialogLoBlock	 ;($D3F3)($C7CB)Farewell, player...
		.byte $BC			   ;($D3F6)TextBlock12, entry 12.

		LDA PlayerFlags		 ;($D3F7)
		AND #$FC				;($D3F9)Clear flag indicating player is carrying Gwaelin.
		ORA #F_RTN_GWAELIN	  ;($D3FB)Set flag indicating Gwaelin has been returned.
		STA PlayerFlags		 ;($D3FD)

		LDA #$C6				;($D3FF)
		STA NPCXPos+$27		 ;($D401)Place princess Gwaelin NPC on the screen.
		LDA #$43				;($D403)
		STA NPCYPos+$27		 ;($D405)

		JSR WaitForNMI		  ;($D407)($FF74)Wait for VBlank interrupt.
		JSR DoSprites		   ;($D40A)($B6DA)Update player and NPC sprites.
		JMP SaveDialog		  ;($D40D)($D433)Jump to save dialog.

KingDialog2:
		LDA PlayerFlags		 ;($D410)Has the player left the throne room for the first time?
		AND #F_LEFT_THROOM	  ;($D412)
		BNE LeftThRoom		  ;($D414)If so, branch.

		LDA #$BF				;($D416)TextBlock12, entry 15.
		JMP DoFinalDialog	   ;($D418)($D242)When thou art finished preparing, please see me...

LeftThRoom:
		JSR DoDialogLoBlock	 ;($D41B)($C7CB)I am greatly pleased that thou hast returned...
		.byte $C0			   ;($D41E)TextBlock13, entry 0.

		LDA DisplayedLevel	  ;($D41F)Is the player level 30?
		CMP #LEVEL_30		   ;($D421)
		BNE CalculateExp		;($D423)If not, branch.

		JSR DoDialogLoBlock	 ;($D425)($C7CB)Thou art strong enough...
		.byte $02			   ;($D428)TextBlock1, entry 2.

		JMP SaveDialog		  ;($D429)($D433)Jump to save dialog.

CalculateExp:
		JSR GetExperienceRemaining;($D42C)($F134)Calculate experience needed for next level.

		JSR DoDialogLoBlock	 ;($D42F)($C7CB)Before reaching thy next level of experience...
		.byte $C1			   ;($D432)TextBlock13, entry 1.

SaveDialog:
		JSR DoDialogHiBlock	 ;($D433)($C7C5)Will thou tell me now of thy deeds...
		.byte $23			   ;($D436)TextBlock19, entry 3.

		JSR Dowindow			;($D437)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D43A)Yes/no selection window.

		CMP #WINDOW_YES		 ;($D43B)Does the player wish to save their game?
		BNE ContQuestDialog	 ;($D43D)If not, branch.

		JSR PrepSaveGame		;($D43F)($F148)Prepare to save the current game.

		JSR DoDialogHiBlock	 ;($D442)($C7C5)Thy deeds have been recorded...
		.byte $24			   ;($D445)TextBlock19, entry 4.

ContQuestDialog:
		JSR DoDialogHiBlock	 ;($D446)($C7C5)Dost thou wish to continue thy quest...
		.byte $25			   ;($D449)TextBlock19, entry 5.

		JSR Dowindow			;($D44A)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D44D)Yes/no selection window.

		CMP #$00				;($D44E)Does player want to continue playing?
		BEQ KingEndTalk		 ;($D450)If so, branch.

		JSR DoDialogHiBlock	 ;($D452)($C7C5)Rest then for a while...
		.byte $26			   ;($D455)TextBlock19, entry 6.

		BRK					 ;($D456)Shut down game after player chooses not to continue.
		.byte $05, $17		  ;($D457)($9362)ExitGame, bank 1.

		JSR MMCShutdown		 ;($D459)($FC88)Switch to PRG bank 3 and disable PRG RAM.

Spinlock2:
		JMP Spinlock2		   ;($D45C)($D45C)Spinlock the game.  Reset required to do anything else.

KingEndTalk:
		LDA #$C4				;($D45F)TextBlock13, Entry4.
		JMP DoFinalDialog	   ;($D461)($D242)Goodbye and tempt not the fates...

;----------------------------------------------------------------------------------------------------

PrincessDialog:
		CMP #$6F				;($D464)Is the player talking to the princess?
		BNE DgrnLrdDialog	   ;($D466)If not, branch.

		JSR UpdateRandNum	   ;($D468)($C55B)Get random number.
		LDA RandomNumberUB	  ;($D46B)
		AND #$60				;($D46D)Choose a random number to vary what princess Gwaelin says
		BNE PrncsRndDialog1	 ;($D46F)to the player when she is talked to.

		LDA #$BB				;($D471)TextBlock12, entry 11.
		JMP DoFinalDialog	   ;($D473)($D242)Even when we are parted by great distances...

PrncsRndDialog1:
		CMP #$60				;($D476)Are the 2 random bits set?
		BNE PrncsRndDialog2	 ;($D478)If so, show a little extra bit of dialog.

		LDA #$BD				;($D47A)TextBlock12, entry 13.
		JMP DoFinalDialog	   ;($D47C)($D242)I love thee, player...

PrncsRndDialog2:
		JSR DoDialogLoBlock	 ;($D47F)($C7CB)Dost thou love me, player...
		.byte $BE			   ;($D482)TextBlock12, entry 14.

		JSR Dowindow			;($D483)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D486)Yes/no selection window.

		BEQ PrncsLoveDialog	 ;($D487)Branch if player loves the princess.

		JSR DoDialogLoBlock	 ;($D489)($C7CB)But thou must...
		.byte $B6			   ;($D48C)TextBlock12, entry 6.

		JMP PrncsRndDialog2	 ;($D48D)Loop until player says they love the princess.

PrncsLoveDialog:
		JSR DoDialogLoBlock	 ;($D490)($C7CB)I'm so happy...
		.byte $B8			   ;($D493)TextBlock12, entry 8.

		LDA #MSC_PRNCS_LOVE	 ;($D494)Gwaelin's love music.
		BRK					 ;($D496)
		.byte $04, $17		  ;($D497)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($D499)Wait for the music clip to end.
		.byte $03, $17		  ;($D49A)($815E)WaitForMusicEnd, bank 1.

		LDA #MSC_THRN_ROOM	  ;($D49C)Throne room castle music.
		BRK					 ;($D49E)
		.byte $04, $17		  ;($D49F)($81A0)InitMusicSFX, bank 1.

		JMP ResumeGamePlay	  ;($D4A1)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

DgrnLrdDialog:
		CMP #$70				;($D4A4)Is the player talking to the dragonlord?
		BEQ DoDrgnLrdDialog	 ;($D4A6)If so, branch to do dragonlord dialog.
		JMP MiscDialog		  ;($D4A8)($D533)Else jump to check some misc. dialog

DoDrgnLrdDialog:
		JSR DoDialogLoBlock	 ;($D4AB)($C7CB)Welcome player, I am the dragonlord...
		.byte $C7			   ;($D4AE)TextBlock13, entry 7.

		JSR DoDialogLoBlock	 ;($D4AF)($C7CB)I have been waiting for one such as thee...
		.byte $A4			   ;($D4B2)TextBlock11, entry 4.

		JSR DoDialogLoBlock	 ;($D4B3)($C7CB)I give thee now a chance to share this world...
		.byte $C8			   ;($D4B6)TextBlock13, entry 8.

		JSR Dowindow			;($D4B7)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D4BA)Yes/no selection window.

		BNE RefuseDglrdDialog   ;($D4BB)Refuse to join the dragonlord. Branch to fight!

		JSR DoDialogHiBlock	 ;($D4BD)($C7C5)Really?...
		.byte $16			   ;($D4C0)TextBlock18, entry 6.

		JSR Dowindow			;($D4C1)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D4C4)Yes/no selection window.

		BEQ ChooseDrgnLrd	   ;($D4C5)Branch if player chooses to join the dragonlord.

RefuseDglrdDialog:
		JSR DoDialogLoBlock	 ;($D4C7)($C7CB)Thou art a fool...
		.byte $C9			   ;($D4CA)TextBlock13, entry 9.

		LDX #$28				;($D4CB)Prepare to wait 40 frames before continuing.
		* JSR WaitForNMI		;($D4CD)($FF74)Wait for VBlank interrupt.
		DEX					 ;($D4D0)Has 40 frames passed?
		BNE -				   ;($D4D1)If not, branch to wait more.

		LDA #WINDOW_DIALOG	  ;($D4D3)Remove dialog window.
		JSR RemoveWindow		;($D4D5)($A7A2)Remove window from screen.

		LDA #WINDOW_CMD_NONCMB  ;($D4D8)Remove command window.
		JSR RemoveWindow		;($D4DA)($A7A2)Remove window from screen.

		LDA #WINDOW_POPUP	   ;($D4DD)Remove pop-up window.
		JSR RemoveWindow		;($D4DF)($A7A2)Remove window from screen.

		LDA #EN_DRAGONLORD1	 ;($D4E2)Dragonlord, initial form.
		JMP InitFight		   ;($D4E4)($E4DF)Fight the dragonlord.

ChooseDrgnLrd:
		JSR DoDialogLoBlock	 ;($D4E7)($C7CB)Then half of this world is thine...
		.byte $CA			   ;($D4EA)TextBlock13, entry 10.

		JSR DoDialogLoBlock	 ;($D4EB)($C7CB)If thou dies I can bring thee back...
		.byte $C2			   ;($D4EE)TextBlock13, entry 2.

		LDA #$00				;($D4EF)
		STA ExpLB			   ;($D4F1)
		STA ExpUB			   ;($D4F3)
		STA GoldLB			  ;($D4F5)
		STA GoldUB			  ;($D4F7)
		STA InventorySlot12	 ;($D4F9)
		STA InventorySlot34	 ;($D4FB)Zero out stats. The player chose to join
		STA InventorySlot56	 ;($D4FD)the dragonlord.  The game is over.
		STA InventorySlot78	 ;($D4FF)
		STA InventoryKeys	   ;($D501)
		STA InventoryHerbs	  ;($D503)
		STA EqippedItems		;($D505)
		STA ModsnSpells		 ;($D507)
		STA PlayerFlags		 ;($D509)
		STA StoryFlags		  ;($D50B)

		JSR DoDialogLoBlock	 ;($D50D)($C7CB)Empty dialog.
		.byte $C3			   ;($D510)TextBlock13, entry 3.

		JSR DoDialogLoBlock	 ;($D511)($C7CB)Thy journey is over. Take now a long rest...
		.byte $CB			   ;($D514)TextBlock13, entry 11.

		LDA BadEndBGPalPtr	  ;($D515)
		STA PalettePointerLB	;($D518)Get pointer to palette data.
		LDA BadEndBGPalPtr+1	;($D51A)
		STA PalettePointerUB	;($D51D)

		LDA #$00				;($D51F)Disable palette fade effect.
		STA PalModByte		  ;($D521)

		JSR PrepBGPalLoad	   ;($D523)($C63D)Load background palette data into PPU buffer
		JSR WaitForNMI		  ;($D526)($FF74)Wait for VBlank interrupt.

		JSR Dowindow			;($D529)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($D52C)Pop-up window.

		JSR WaitForNMI		  ;($D52D)($FF74)Wait for VBlank interrupt.

Spinlock3:
		JMP Spinlock3		   ;($D530)($D530)Spinlock the game.  Reset required to do anything else.

;----------------------------------------------------------------------------------------------------

MiscDialog:
		CMP #$71				;($D533)Tantagel ground floor guard dialog 1?
		BEQ GuardDialog1		;($D535)If so, branch.

		CMP #$72				;($D537)Tantagel ground floor guard dialog 2?
		BEQ GuardDialog2		;($D539)If so, branch.

		JMP NoTalk			  ;($D53B)($D1ED)No Valid NPC to talk to.

GuardDialog1:
		JSR DoDialogLoBlock	 ;($D53E)($C7CB)If you are planning to take a rest, see king Lorik...
		.byte $03			   ;($D541)TextBlock1, entry 3.

		JMP ResumeGamePlay	  ;($D542)($CFD9)Give control back to player.

GuardDialog2:
		JSR DoDialogLoBlock	 ;($D545)($C7CB)When entering the cave, take a torch...
		.byte $91			   ;($D548)TextBlock10, entry 1.

		JMP ResumeGamePlay	  ;($D549)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

InvListTbl:
		.byte ITM_TORCH		 ;($D54C)
		.byte ITM_DRG_SCALE	 ;($D54D)If Gwaelin is returned and the player's inventory
		.byte ITM_FTR_RING	  ;($D54E)is full, one of the following items will be taken
		.byte ITM_FRY_WATER	 ;($D54F)from the inventory and replaced with Gwaelin's love.
		.byte ITM_WINGS		 ;($D550)If the inventory is full and none of these things
		.byte ITM_CRSD_BELT	 ;($D551)are present, Gwaelin's love will not be added to inventory.
		.byte ITM_STFF_RAIN	 ;($D552)

;----------------------------------------------------------------------------------------------------

WeaponsDialog:
		STA DialogTemp		  ;($D553)Save dialog control byte.

		JSR DoDialogLoBlock	 ;($D555)($C7CB)We deal in weapons and armor...
		.byte $28			   ;($D558)TextBlock3, entry 8.

WpnDialogLoop:
		JSR Dowindow			;($D559)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D55C)Yes/no selection window.

		BEQ WeapYesDialog	   ;($D55D)Does the player want weapons? If so, branch.
		JMP WeapNoDialog		;($D55F)($D66B)Finish weapons shop dialog.

WeapYesDialog:
		JSR DoDialogLoBlock	 ;($D562)($C7CB)What dost thou wish to buy?...
		.byte $2D			   ;($D565)TextBlock3, entry 13.

		JSR GetShopItems		;($D566)($D672)Get items for sale in this shop.

		LDA WindowSelResults	;($D569)Did the player abort the shop dialog?
		CMP #WINDOW_ABORT	   ;($D56B)
		BNE CheckBuyWeapon	  ;($D56D)If not, branch to try to buy weapon.

		JMP WeapNoDialog		;($D56F)($D66B)Finish weapons shop dialog.

CheckBuyWeapon:
		LDA ShopItemsTbl,X	  ;($D572)Save the index to the item selected on the stack.
		PHA					 ;($D575)

		CLC					 ;($D576)Get the description for the weapon selected.
		ADC #$1B				;($D577)
		JSR GetDescriptionByte  ;($D579)($DBF0)Load byte for item dialog description.

		JSR DoDialogLoBlock	 ;($D57C)($C7CB)The item?...
		.byte $29			   ;($D57F)TextBlock 3, entry 9.

		LDA #$00				;($D580)
		STA GenWrd00LB		  ;($D582)Zero out price calculating variables.
		STA GenWrd00UB		  ;($D584)

		PLA					 ;($D586)Restore selected item index.
		ASL					 ;($D587)*2. each entry in the table is 2 bytes.

		TAX					 ;($D588)
		LDA GoldLB			  ;($D589)
		SEC					 ;($D58B)Subtract item price from player's gold to
		SBC ItemCostTbl,X	   ;($D58C)see if player has enough money.
		LDA GoldUB			  ;($D58F)
		SBC ItemCostTbl+1,X	 ;($D591)

		BCS DoWeapPurchase	  ;($D594)Does player have enough money? if so, branch.
		JMP NoMoneyDialog	   ;($D596)($D660)Player does not have enough money.

DoWeapPurchase:
		TXA					 ;($D599)Save a copy of the item index into the ItemCostTable.
		PHA					 ;($D59A)

		CMP #$0E				;($D59B)Is the selected item anything but a weapon?
		BCS ChkItem			 ;($D59D)If so, branch.

		LDA EqippedItems		;($D59F)Get player's equipped weapons.
		LSR					 ;($D5A1)
		LSR					 ;($D5A2)
		LSR					 ;($D5A3)
		LSR					 ;($D5A4)
		LSR					 ;($D5A5)Does the player have a weapon?
		BEQ ConfSaleDialog	  ;($D5A6)Does player have a weapon equipped?

		BNE GetBuybackPrice	 ;($D5A8)If so, branch to offer money for existing weapon.

ChkItem:
		CMP #$1C				;($D5AA)Is the selected item armor?
		BCS ChkShield		   ;($D5AC)If not, branch.

		LDA EqippedItems		;($D5AE)Get player's equipped armor.
		LSR					 ;($D5B0)
		LSR					 ;($D5B1)
		AND #$07				;($D5B2)Is the player wearing armor?
		BEQ ConfSaleDialog	  ;($D5B4)If not, branch to confirm purchase.

		CLC					 ;($D5B6)Set the index for armor prices.
		ADC #$07				;($D5B7)
		BNE GetBuybackPrice	 ;($D5B9)Branch to offer money for existing armor.

ChkShield:
		LDA EqippedItems		;($D5BB)Is player carrying a shield?
		AND #SH_SHIELDS		 ;($D5BD)
		BEQ ConfSaleDialog	  ;($D5BF)If not, branch to confirm purchase.

		CLC					 ;($D5C1)Set index for shield prices.
		ADC #$0E				;($D5C2)

GetBuybackPrice:
		ASL					 ;($D5C4)*2. each entry in the table is 2 bytes.
		TAY					 ;($D5C5)

		LDA ItemCostTbl-2,Y	 ;($D5C6)Get item cost from ItemCostTbl
		STA GenWrd00LB		  ;($D5C9)
		LDA ItemCostTbl-1,Y	 ;($D5CB)
		STA GenWrd00UB		  ;($D5CE)Save cost.

		LSR GenWrd00UB		  ;($D5D0)Divide cost by 2.
		ROR GenWrd00LB		  ;($D5D2)Sell item back for half of its cost.

		TYA					 ;($D5D4)Restore item index to original value.
		LSR					 ;($D5D5)

		CLC					 ;($D5D6)Get description index for selected item.
		ADC #$1A				;($D5D7)
		JSR GetDescriptionByte  ;($D5D9)($DBF0)Load byte for item dialog description.

		JSR DoDialogLoBlock	 ;($D5DC)($C7CB)Then I will buy thy item...
		.byte $2A			   ;($D5DF)TextBlock3, entry 10.

ConfSaleDialog:
		JSR DoDialogLoBlock	 ;($D5E0)($C7CB)Is that ok...
		.byte $27			   ;($D5E3)TextBlock3, entry 7.

		JSR Dowindow			;($D5E4)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D5E7)Yes/no selection window.

		PLA					 ;($D5E8)Restore copy of the item index into the ItemCostTable.
		TAX					 ;($D5E9)

		LDA WindowSelResults	;($D5EA)Did player choose to buy the item?
		BEQ ComitWeapPurchase   ;($D5EC)If so, branch to commit to purchase.

		JSR DoDialogLoBlock	 ;($D5EE)($C7CB)Oh yes? That's too bad...
		.byte $26			   ;($D5F1)TextBlock3, entry 6.

		JMP NextWeapDialog	  ;($D5F2)($D664)Jump to see if player wants to buy something else.

ComitWeapPurchase:
		LDA GoldLB			  ;($D5F5)
		SEC					 ;($D5F7)
		SBC ItemCostTbl,X	   ;($D5F8)
		STA GoldLB			  ;($D5FB)Subtract the cost of the item from the player's gold.
		LDA GoldUB			  ;($D5FD)
		SBC ItemCostTbl+1,X	 ;($D5FF)
		STA GoldUB			  ;($D602)
		LDA GoldLB			  ;($D604)

		CLC					 ;($D606)
		ADC GenWrd00LB		  ;($D607)
		STA GoldLB			  ;($D609)Add the buyback price of the old item to the player's gold.
		LDA GoldUB			  ;($D60B)
		ADC GenWrd00UB		  ;($D60D)
		STA GoldUB			  ;($D60F)

		BCC ApplyPurchase	   ;($D611)Has player maxed out gold? If not, branch.

		LDA #$FF				;($D613)
		STA GoldLB			  ;($D615)Set players gold to max value of 65535.
		STA GoldUB			  ;($D617)

ApplyPurchase:
		TXA					 ;($D619)/2. Restore index to original value.
		LSR					 ;($D61A)

		CMP #$07				;($D61B)Is the purchased item a weapon?
		BCS $D63C			   ;($D61D)If not, branch.

		CLC					 ;($D61F)Add 1 to weapon to get proper EqippedItems value.
		ADC #$01				;($D620)

		ASL					 ;($D622)
		ASL					 ;($D623)
		ASL					 ;($D624)Move weapon to proper bit location for EqippedItems.
		ASL					 ;($D625)
		ASL					 ;($D626)

		STA GenByte3C		   ;($D627)Temp storage of new weapon.

		LDA EqippedItems		;($D629)Remove old weapon.
		AND #$1F				;($D62B)

		ORA GenByte3C		   ;($D62D)Equip new weapon.
		STA EqippedItems		;($D62F)

CompWeapPurchase:
		JSR DoDialogLoBlock	 ;($D631)($C7CB)I thank thee...
		.byte $2E			   ;($D634)TextBlock3, entry 14.

		JSR Dowindow			;($D635)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($D638)Pop-up window.
		JMP NextWeapDialog	  ;($D639)($D664)Jump to see if player wants to buy something else.

		CMP #$0E				;($D63C)Is the purchased item armor?
		BCS ApplyShield		 ;($D63E)If not branch to apply the new shield(the only one left).

		SEC					 ;($D640)
		SBC #$06				;($D641)Subtract 6 and *4 to move armor to proper bit
		ASL					 ;($D643)location for EqippedItems.
		ASL					 ;($D644)

		STA GenByte3C		   ;($D645)Temp storage of new armor.

		LDA EqippedItems		;($D647)Remove old armor.
		AND #$E3				;($D649)

		ORA GenByte3C		   ;($D64B)Equip new armor.
		STA EqippedItems		;($D64D)

		BNE CompWeapPurchase	;($D64F)Branch always to complete process.

ApplyShield:
		SEC					 ;($D651)Subtract 13 to move shield to proper bit
		SBC #$0D				;($D652)location for EqippedItems.

		STA GenByte3C		   ;($D654)Temp storage of new shield.

		LDA EqippedItems		;($D656)Remove old shield.
		AND #$FC				;($D658)

		ORA GenByte3C		   ;($D65A)Equip new shield.
		STA EqippedItems		;($D65C)

		BNE CompWeapPurchase	;($D65E)Branch always to complete process.

NoMoneyDialog:
		JSR DoDialogLoBlock	 ;($D660)($C7CB)Sorry. Thou hast not enough money...
		.byte $2B			   ;($D663)TextBlock3, entry 11.

NextWeapDialog:
		JSR DoDialogLoBlock	 ;($D664)($C7CB)Dost thou wish to buy anything more...
		.byte $2C			   ;($D667)TextBlock3, entry 12.

		JMP WpnDialogLoop	   ;($D668)($D559)Branch to see if player wants to buy more.

WeapNoDialog:
		JSR DoDialogLoBlock	 ;($D66B)($C7CB)Please come again...
		.byte $2F			   ;($D66E)TextBlock3, entry 15.

		JMP ResumeGamePlay	  ;($D66F)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

GetShopItems:
		LDX #$00				;($D672)The dialog control byte is the entry
		LDA DialogTemp		  ;($D674)into the ShopItemsTbl.
		STA ShopIndex		   ;($D676)Store a copy of the table index.
		BEQ ShopEntryFound	  ;($D678)Is the index 0? If so, no need to search the table.

ShopEntryLoop:
		LDA ShopItemsTbl,X	  ;($D67A)
		INX					 ;($D67D)Increment through ShopItemsTbl to find end of
		CMP #ITM_TBL_END		;($D67E)current shop index.
		BNE ShopEntryLoop	   ;($D680)

		DEC ShopIndex		   ;($D682)Have we found the proper index for this shop?
		BNE ShopEntryLoop	   ;($D684)If not, branch to move to next index.

ShopEntryFound:
		TXA					 ;($D686)Use current offset as index into table for specific item.
		PHA					 ;($D687)Save base offset of this shop's table.

		LDY #$01				;($D688)Load #$01 into the description buffer.
		STY DescBuf			 ;($D68A)

ShopEntryLoad:
		LDA ShopItemsTbl,X	  ;($D68C)Store description byte for item in the description buffer.
		CLC					 ;($D68F)The description byte will be converted to the proper
		ADC #$02				;($D690)value in the window engine.
		STA _DescBuf,Y		  ;($D692)

		CMP #ITM_TBL_END+2	  ;($D695)Have all the description bytes been loaded?
		BEQ ShowShopInvWnd	  ;($D697)If so, branch.

		INX					 ;($D699)Move to next byte in the ShopItemsTbl
		INY					 ;($D69A)move to next spot in the description buffer.
		BNE ShopEntryLoad	   ;($D69B)Branch to get next item.

ShowShopInvWnd:
		JSR Dowindow			;($D69D)($C6F0)display on-screen window.
		.byte WND_INVTRY2	   ;($D6A0)Shop inventory window.

		PLA					 ;($D6A1)Restore base index into ShopItemsTbl.
		CLC					 ;($D6A2)
		ADC WindowSelResults	;($D6A3)Add selected item to value.
		TAX					 ;($D6A5)
		RTS					 ;($D6A6)The value in X is the index for the specific item in ShopItemsTbl.

;----------------------------------------------------------------------------------------------------

ToolsDialog:
		STA DialogTemp		  ;($D6A7)Save a copy of the dialog byte.

		JSR DoDialogLoBlock	 ;($D6A9)($C7CB)Welcome. We deal in tools...
		.byte $25			   ;($D6AC)TextBlock3, entry 5.

		JSR Dowindow			;($D6AD)($C6F0)display on-screen window.
		.byte WINDOW_BUY_SELL   ;($D6B0)Buy/sell window.

		BEQ DoToolPurchase	  ;($D6B1)Did player choose to buy something? if so, branch.

		CMP #WINDOW_SELL		;($D6B3)Did player choose to sell something?
		BNE ToolExitDialog	  ;($D6B5)If not, branch to exit tool dialog.
		JMP DoToolSell		  ;($D6B7)($D739)Sell tools routines.

ToolExitDialog:
		JSR DoDialogLoBlock	 ;($D6BA)($C7CB)I will be waiting for thy next visit...
		.byte $1E			   ;($D6BD)TextBlock2, entry 14.

		JMP ResumeGamePlay	  ;($D6BE)($CFD9)Give control back to player.

DoToolPurchase:
		JSR DoDialogLoBlock	 ;($D6C1)($C7CB)What dost thou want...
		.byte $24			   ;($D6C4)TextBlock3, entry 4.

		JSR GetShopItems		;($D6C5)($D672)Display items for sale in this shop.

		LDA WindowSelResults	;($D6C8)Did player cancel out of item window?
		CMP #WINDOW_ABORT	   ;($D6CA)If so, branch to exit tool dialog.
		BEQ ToolExitDialog	  ;($D6CC)($D6BA)Exit tool buy/sell dialog.

		LDA ShopItemsTbl,X	  ;($D6CE)Load selected item from shop item table.
		PHA					 ;($D6D1)Save a copy of the item on the stack.

		CLC					 ;($D6D2)Add 32 to get proper index for item description.
		ADC #$1F				;($D6D3)
		JSR GetDescriptionByte  ;($D6D5)($DBF0)Load byte for item dialog description.

		PLA					 ;($D6D8)Restore index to selected item.
		ASL					 ;($D6D9)*2. Cost of item is 2 byte in ItemCostTbl.

		TAX					 ;($D6DA)Subtract item price from player's current gold.
		LDA GoldLB			  ;($D6DB)
		SEC					 ;($D6DD)
		SBC ItemCostTbl,X	   ;($D6DE)
		STA GenWord3CLB		 ;($D6E1)
		LDA GoldUB			  ;($D6E3)
		SBC ItemCostTbl+1,X	 ;($D6E5)Does player have enough gold to
		STA GenWord3CUB		 ;($D6E8)purchase the selected item?
		BCS ChkToolPurchase	 ;($D6EA)If so, branch.

		JSR DoDialogLoBlock	 ;($D6EC)($C7CB)Thou hast not enough money...
		.byte $22			   ;($D6EF)TextBlock3, entry 2.

		JMP NextToolDialog	  ;($D6F0)($D716)Check if player wants to buy something else.

ChkToolPurchase:
		CPX #$22				;($D6F3)Is player trying to buy herbs?
		BNE DoOthrToolPurchase  ;($D6F5)If not, branch.

		LDA InventoryHerbs	  ;($D6F7)Does player already have the maximum herbs?
		CMP #$06				;($D6F9)
		BNE PurchaseHerb		;($D6FB)If not, branch to add herb to inventory.

		JSR DoDialogLoBlock	 ;($D6FD)($C7CB)Thou cannot hold more herbs...
		.byte $20			   ;($D700)TextBlock3, entry 0.

		JMP NextToolDialog	  ;($D701)($D716)Check if player wants to buy something else.

PurchaseHerb:
		INC InventoryHerbs	  ;($D704)Add 1 herb.

PurchaseTool:
		LDA GenWord3CLB		 ;($D706)
		STA GoldLB			  ;($D708)Save updated gold amount.
		LDA GenWord3CUB		 ;($D70A)
		STA GoldUB			  ;($D70C)

		JSR DoDialogLoBlock	 ;($D70E)($C7CB)The item? Thank you very much...
		.byte $23			   ;($D711)TextBlock3, entry 3.

		JSR Dowindow			;($D712)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($D715)Pop-up window.

NextToolDialog:
		JSR DoDialogLoBlock	 ;($D716)($C7CB)Dost thou want anything else...
		.byte $1F			   ;($D719)TextBlock2, entry 15.

		JSR Dowindow			;($D71A)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D71D)Yes/no selection window.

		BNE DoToolExit		  ;($D71E)Exit tool dialog.
		JMP DoToolPurchase	  ;($D720)($D6C1)Loop do to another purchase.

DoToolExit:
		JMP ToolExitDialog	  ;($D723)($D6BA)Exit tool buy/sell dialog.

DoOthrToolPurchase:
		TXA					 ;($D726)
		LSR					 ;($D727)Set proper index for corresponding item.
		SEC					 ;($D728)
		SBC #$12				;($D729)

		JSR AddInvItem		  ;($D72B)($E01B)Add item to inventory.
		CPX #INV_FULL		   ;($D72E)Is player's inventory full?
		BNE PurchaseTool		;($D730)If not, branch to purchase tool.

		JSR DoDialogLoBlock	 ;($D732)($C7CB)Thou cannot carry anymore...
		.byte $21			   ;($D735)TextBlock3, entry 1.

		JMP NextToolDialog	  ;($D736)($D716)Check if player wants to buy something else.

DoToolSell:
		JSR CreateInvList	   ;($D739)($DF77)Create inventory list in description buffer.
		CPX #$01				;($D73C)Does player have any tools to sell?
		BNE HaveToolsToSell	 ;($D73E)If so, branch.

		JSR DoDialogLoBlock	 ;($D740)($C7CB)Thou hast no possesions...
		.byte $19			   ;($D743)TextBlock2, entry 9.

		JMP ToolExitDialog	  ;($D744)($D6BA)Exit tool buy/sell dialog.

HaveToolsToSell:
		JSR DoDialogLoBlock	 ;($D747)($C7CB)What art thou selling...
		.byte $1D			   ;($D74A)TextBlock2, entry 13.

		JSR Dowindow			;($D74B)($C6F0)display on-screen window.
		.byte WND_INVTRY1	   ;($D74E)Player inventory window.

		CMP #WINDOW_ABORT	   ;($D74F)Did player abort from inventory window?
		BNE GetSellDesc		 ;($D751)
		JMP ToolExitDialog	  ;($D753)($D6BA)Exit tool buy/sell dialog.

GetSellDesc:
		TAX					 ;($D756)
		LDA DescBuf+1,X		 ;($D757)Get description byte from the description buffer.
		STA DescTemp			;($D759)

		CLC					 ;($D75B)Convert it to the proper index in DescTable.
		ADC #$2E				;($D75C)

		JSR GetDescriptionByte  ;($D75E)($DBF0)Load byte for item dialog description.

		LDA DescTemp			;($D761)Get item description byte again.
		CLC					 ;($D763)
		ADC #$0F				;($D764)Convert it into proper pointer for ItemCostTbl.
		ASL					 ;($D766)

		TAX					 ;($D767)
		LDA ItemCostTbl,X	   ;($D768)
		STA GenWrd00LB		  ;($D76B)Get item cost.
		LDA ItemCostTbl+1,X	 ;($D76D)
		STA GenWrd00UB		  ;($D770)

		ORA GenWrd00LB		  ;($D772)Is tool value greater than 0?
		BNE SellableTool		;($D774)If so, branch.  It is sellable.

		JSR DoDialogLoBlock	 ;($D776)($C7CB)I cannot buy it...
		.byte $1B			   ;($D779)TextBlock2, entry 11.

ItemSellLoop:
		JSR DoDialogLoBlock	 ;($D77A)($C7CB)Will thou sell anything else...
		.byte $1A			   ;($D77D)TextBlock2, entry 10.

		JSR Dowindow			;($D77E)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D781)Yes/no selection window.

		BNE $D787			   ;($D782)
		JMP DoToolSell		  ;($D784)($D739)Sell tools routines.
		JMP ToolExitDialog	  ;($D787)($D6BA)Exit tool buy/sell dialog.

SellableTool:
		LSR $01				 ;($D78A)/2. Tool sell cost is only half its purchase cost.
		ROR $00				 ;($D78C)

		JSR DoDialogLoBlock	 ;($D78E)($C7CB)Thou said the item. I will buy the item...
		.byte $1C			   ;($D791)TextBlock2, entry 12.

		JSR Dowindow			;($D792)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D795)Yes/no selection window.

		BNE ItemSellLoop		;($D796)($D77A)No sale. Branch to see if player wants to sell more.

		LDA DescTemp			;($D798)Is player selling a key?
		CMP #$03				;($D79A)
		BNE ChkSellHerb		 ;($D79C)If not, branch.

		DEC InventoryKeys	   ;($D79E)Decrement Player's keys.

GetSellGold:
		LDA GoldLB			  ;($D7A0)Add item's sell value to Player's gold.
		CLC					 ;($D7A2)
		ADC GenWrd00LB		  ;($D7A3)
		STA GoldLB			  ;($D7A5)
		LDA GoldUB			  ;($D7A7)
		ADC GenWrd00UB		  ;($D7A9)
		STA GoldUB			  ;($D7AB)Did player's gold go beyond the max amount?
		BCC DoneSellingTool	 ;($D7AD)If not, branch to conclude transaction.

		LDA #$FF				;($D7AF)
		STA GoldLB			  ;($D7B1)Set gold to max value(65535).
		STA GoldUB			  ;($D7B3)

DoneSellingTool:
		JSR Dowindow			;($D7B5)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($D7B8)Pop-up window.

		JMP ItemSellLoop		;($D7B9)($D77A)Branch to see if player wants to sell more.

ChkSellHerb:
		CMP #$02				;($D7BC)Is player trying to sell an herb?
		BNE ChkSellBelt		 ;($D7BE)If not, branch.

		DEC InventoryHerbs	  ;($D7C0)Decrement herbs.
		JMP GetSellGold		 ;($D7C2)($D7A0)Update gold after selling item.

ChkSellBelt:
		CMP #$0C				;($D7C5)Is player trying to sell the cursed belt?
		BNE ChkSellNecklace	 ;($D7C7)If not, branch.

		PHA					 ;($D7C9)Save a copy of item to sell.
		BIT ModsnSpells		 ;($D7CA)Is player wearing the belt?
		BVC SellBelt			;($D7CC)If not, branch to sell it.

CantSellCrsdItm:
		PLA					 ;($D7CE)Pull cursed item ID off stack.

		JSR DoDialogLoBlock	 ;($D7CF)($C7CB)A curse is on thy body...
		.byte $18			   ;($D7D2)TextBlock2, entry 8.

		JSR DoDialogLoBlock	 ;($D7D3)($C7CB)I am sorry...
		.byte $17			   ;($D7D6)TextBlock2, entry 7.

		JMP ItemSellLoop		;($D7D7)($D77A)Branch to see if player wants to sell more.

ChkSellNecklace:
		CMP #$0E				;($D7DA)Is player trying to sell the death necklace?
		BNE DoSellTool		  ;($D7DC)If not, branch.

		PHA					 ;($D7DE)Is player wearing the death necklace?
		LDA ModsnSpells		 ;($D7DF)
		BMI CantSellCrsdItm	 ;($D7E1)If so, branch. Can't sell it.

SellBelt:
		PLA					 ;($D7E3)Pull cursed item ID off stack.

DoSellTool:
		SEC					 ;($D7E4)Convert item description byte to proper index value.
		SBC #$03				;($D7E5)

		JSR RemoveInvItem	   ;($D7E7)($E04B)Remove item from inventory.
		JMP GetSellGold		 ;($D7EA)($D7A0)Update gold after selling item.

;----------------------------------------------------------------------------------------------------

KeysDialog:
		SEC					 ;($D7ED)There are three key shops. The dialog control byte
		SBC #$0C				;($D7EE)determines what the price of the key is.

		TAX					 ;($D7F0)Convert control byte to index for KeyCostTbl.
		LDA KeyCostTbl,X		;($D7F1)

		STA GenWrd00LB		  ;($D7F4)
		LDA #$00				;($D7F6)Save key cost.  Upper byte is always 0.
		STA GenWrd00UB		  ;($D7F8)

		JSR DoDialogLoBlock	 ;($D7FA)($C7CB)Magic keys! They will unlock any door...
		.byte $16			   ;($D7FD)TextBlock2, entry 6.

KeyDialogLoop:
		JSR Dowindow			;($D7FE)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D801)Yes/no selection window.

		BEQ ChkBuyKey		   ;($D802)Did player choose to buy a key? If so, branch.

EndKeyDialog:
		JSR DoDialogLoBlock	 ;($D804)($C7CB)I will see thee later...
		.byte $12			   ;($D807)TextBlock2, entry 2.
		JMP ResumeGamePlay	  ;($D808)($CFD9)Give control back to player.

ChkBuyKey:
		LDA InventoryKeys	   ;($D80B)Does player already have the maximum 6 keys?
		CMP #$06				;($D80D)
		BNE ChkBuyKeyGold	   ;($D80F)If not, branch.

		JSR DoDialogLoBlock	 ;($D811)($C7CB)I am sorry, but I cannot sell thee anymore...
		.byte $14			   ;($D814)TextBlock2, entry 4.

		JMP EndKeyDialog		;($D815)($D804)End key shop dialog.

ChkBuyKeyGold:
		LDA GoldLB			  ;($D818)
		SEC					 ;($D81A)
		SBC GenWrd00LB		  ;($D81B)
		STA GenWord3CLB		 ;($D81D)Does player have enough gold to buy a key?
		LDA GoldUB			  ;($D81F)If so, branch to commit key purchase.
		SBC GenWrd00UB		  ;($D821)
		STA GenWord3CUB		 ;($D823)
		BCS BuyKey			  ;($D825)

		JSR DoDialogLoBlock	 ;($D827)($C7CB)Thou hast not enough money.
		.byte $13			   ;($D82A)TextBlock2, entry 3.

		JMP EndKeyDialog		;($D82B)($D804)End key shop dialog.

BuyKey:
		LDA GenWord3CLB		 ;($D82E)
		STA GoldLB			  ;($D830)
		LDA GenWord3CUB		 ;($D832)Subtract key cost from player's gold.
		STA GoldUB			  ;($D834)
		INC InventoryKeys	   ;($D836)

		JSR Dowindow			;($D838)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($D83B)Pop-up window.

		JSR DoDialogLoBlock	 ;($D83C)($C7CB)Here, take this key...
		.byte $15			   ;($D83F)TextBlock2, entry 5.

		JMP KeyDialogLoop	   ;($D840)($D7FE)Loop to see if player wants another key.

;----------------------------------------------------------------------------------------------------

FairyDialog:
		LDA #$26				;($D843)
		STA GenWrd00LB		  ;($D845)Set fairy water price of 38 gold.
		LDA #$00				;($D847)
		STA GenWrd00UB		  ;($D849)

		JSR DoDialogLoBlock	 ;($D84B)($C7CB)Will thou buy some fairy water...
		.byte $11			   ;($D84E)TextBlock2, entry 1.

FairyDialogLoop:
		JSR Dowindow			;($D84F)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D852)Yes/no selection window.

		BEQ ChkBuyFryWtr		;($D853)Did player choose to buy some? If so, branch.

EndFairyDialog:
		JSR DoDialogLoBlock	 ;($D855)($C7CB)All the best to thee...
		.byte $0C			   ;($D858)TextBlock1, entry 12.

		JMP ResumeGamePlay	  ;($D859)($CFD9)Give control back to player.

ChkBuyFryWtr:
		LDA GoldLB			  ;($D85C)
		SEC					 ;($D85E)
		SBC GenWrd00LB		  ;($D85F)
		STA GenWord3CLB		 ;($D861)Does player have enough money for fairy water?
		LDA GoldUB			  ;($D863)If so, branch to see if it will fit in inventory.
		SBC GenWrd00UB		  ;($D865)
		STA GenWord3CUB		 ;($D867)
		BCS ChkFryWtrInv		;($D869)

		JSR DoDialogLoBlock	 ;($D86B)($C7CB)Thou hast not enough money.
		.byte $22			   ;($D86E)TextBlock3, entry 2.

		JMP EndFairyDialog	  ;($D86F)($D855)End fairy water dialog.

ChkFryWtrInv:
		LDA #ITM_FRY_WATER	  ;($D872)Attempt to add a fairy water to the player's inventory.
		JSR AddInvItem		  ;($D874)($E01B)Add item to inventory.
		CPX #INV_FULL		   ;($D877)Is the players inventory full?
		BNE BuyFairyWater	   ;($D879)If not, branch to commit to purchase.

		JSR DoDialogLoBlock	 ;($D87B)($C7CB)Thou cannot carry anymore.
		.byte $21			   ;($D87E)TextBlock3, entry 1.

		JMP EndFairyDialog	  ;($D87F)($D855)End fairy water dialog.

BuyFairyWater:
		LDA GenWord3CLB		 ;($D882)
		STA GoldLB			  ;($D884)Subtract fairy water price from player's gold.
		LDA GenWord3CUB		 ;($D886)
		STA GoldUB			  ;($D888)

		JSR Dowindow			;($D88A)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($D88D)Pop-up window.

		JSR DoDialogLoBlock	 ;($D88E)($C7CB)I thank thee. Won't thou buy another bottle...
		.byte $10			   ;($D891)TextBlock2, entry 0.

		JMP FairyDialogLoop	 ;($D892)($D84F)Loop to see if player wants to buy another.

;----------------------------------------------------------------------------------------------------

InnDialog:
		SEC					 ;($D895)Convert dialog control byte to
		SBC #$11				;($D896)proper index in InnCostTbl.

		TAX					 ;($D898)Get inn cost from InnCostTbl.
		LDA InnCostTbl,X		;($D899)

		STA GenWrd00LB		  ;($D89C)
		LDA #$00				;($D89E)Store inn cost. Upper byte is always 0.
		STA GenWrd00UB		  ;($D8A0)

		JSR DoDialogLoBlock	 ;($D8A2)($C7CB)Welcome to the traveler's inn...
		.byte $0B			   ;($D8A5)TextBlock1, entry 11.

		JSR Dowindow			;($D8A6)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($D8A9)Yes/no selection window.

		BEQ ChkBuyInnStay	   ;($D8AA)Did player choose to stay at the inn? if so, branch.

		JSR DoDialogLoBlock	 ;($D8AC)($C7CB)Ok. Good-bye, traveler...

InnExitDialog2:
		.byte $0A			   ;($D8AF)TextBlock1, entry 10.

		JMP ResumeGamePlay	  ;($D8B0)($CFD9)Give control back to player.

ChkBuyInnStay:
		LDA GoldLB			  ;($D8B3)
		SEC					 ;($D8B5)
		SBC GenWrd00LB		  ;($D8B6)
		STA GenWord3CLB		 ;($D8B8)Does player have enough money to buy a night at the inn?
		LDA GoldUB			  ;($D8BA)If so, branch to commit to purchase.
		SBC GenWrd00UB		  ;($D8BC)
		STA GenWord3CUB		 ;($D8BE)
		BCS BuyInnStay		  ;($D8C0)

		JSR DoDialogLoBlock	 ;($D8C2)($C7CB)Though hast not enough money...
		.byte $22			   ;($D8C5)TextBlock3, entry 2.

		JMP InnExitDialog2	  ;($D8C6)($D8AF)Exit inn dialog.

BuyInnStay:
		LDA GenWord3CLB		 ;($D8C9)
		STA GoldLB			  ;($D8CB)Subtract cost of inn stay from player's gold.
		LDA GenWord3CUB		 ;($D8CD)
		STA GoldUB			  ;($D8CF)

		JSR Dowindow			;($D8D1)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($D8D4)Pop-up window.

		JSR DoDialogLoBlock	 ;($D8D5)($C7CB)Good night...
		.byte $09			   ;($D8D8)TextBlock1, entry 9.

		JSR $D915			   ;($D8D9)
		JSR PalFadeOut		  ;($D8DC)($C212)Fade out both background and sprite palettes.

		LDA #MSC_INN			;($D8DF)Inn music.
		BRK					 ;($D8E1)
		.byte $04, $17		  ;($D8E2)($81A0)InitMusicSFX, bank 1.

		LDA DisplayedMaxHP	  ;($D8E4)
		STA HitPoints		   ;($D8E6)Stayed at an inn. Restore full HP and MP.
		LDA DisplayedMaxMP	  ;($D8E8)
		STA MagicPoints		 ;($D8EA)

		JSR Dowindow			;($D8EC)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($D8EF)Pop-up window.

		JSR GetRegularPalPtrs   ;($D8F0)($D915)Get pointers to the standard palettes.

		BRK					 ;($D8F3)Wait for the music clip to end.
		.byte $03, $17		  ;($D8F4)($815E)WaitForMusicEnd, bank 1.

		LDA #MSC_VILLAGE		;($D8F6)Village music.
		BRK					 ;($D8F8)
		.byte $04, $17		  ;($D8F9)($81A0)InitMusicSFX, bank 1.

		JSR PalFadeIn		   ;($D8FB)($C529)Fade in both background and sprite palettes.

		LDA PlayerFlags		 ;($D8FE)Is player carrying Gwaelin?
		LSR					 ;($D900)
		BCC SpecialInnDialog	;($D901)If not, branch for normal Inn dialog.

		JSR DoDialogLoBlock	 ;($D903)($C7CB)Good morning. Thou has had a good night's sleep...
		.byte $06			   ;($D906)TextBlock1, entry 6.

		JMP InnExitDialog	   ;($D907)($D90E)Finish Inn dialog.

SpecialInnDialog:
		JSR DoDialogLoBlock	 ;($D90A)($C7CB)Good morning. Thou seems to have had a good night...
		.byte $08			   ;($D90D)TextBlock1, entry 8.

InnExitDialog:
		JSR DoDialogLoBlock	 ;($D90E)($C7CB)I shall see thee again.
		.byte $07			   ;($D911)TextBlock1, entry 7.

		JMP ResumeGamePlay	  ;($D912)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

GetRegularPalPtrs:
		LDA RegSPPalPtr		 ;($D915)
		STA SpritePalettePointerLB;($D918)Get a pointer to the standard sprite palettes.
		LDA RegSPPalPtr+1	   ;($D91A)
		STA SpritePalettePointerUB;($D91D)

		LDA TownPalPtr		  ;($D91F)
		STA BackgroundPalettePointerLB;($D922)Get a pointer to the standard background palettes.
		LDA TownPalPtr+1		;($D924)
		STA BackgroundPalettePointerUB;($D927)

		LDA #PAL_LOAD_BG		;($D929)
		STA LoadBGPal		   ;($D92B)Indicate background palette data should be loaded.
		RTS					 ;($D92D)

;----------------------------------------------------------------------------------------------------

IncDescBuffer:
		LDX #$00				;($D92E)Prepare to write incrementing numbers
		LDA #$01				;($D930)to the description buffer.

		* STA DescBuf,X		 ;($D932)
		INX					 ;($D934)Write the values #$01 to #$0A to the description buffer.
		CLC					 ;($D935)
		ADC #$01				;($D936)
		CPX #$0B				;($D938)Have all the bytes been written?
		BNE -				   ;($D93A)If not, branch to write another byte.
		RTS					 ;($D93C)

;----------------------------------------------------------------------------------------------------

StairDownFound:
		LDA #$00				;($D93D)Indicate player came down stairs. Always faces right.
		BEQ +				   ;($D93F)Branch always.

CalcNextMap:
		LDA #$01				;($D941)Indicate player new facing direction is table lookup.

		* STA GenByte2C		 ;($D943)Store player direction source flag.

		LDX #$00				;($D945)Zero out indexes.
		LDY #$00				;($D947)

MapCheckLoop1:
		LDA MapNumber		   ;($D949)Has the right map been found in the table?
		CMP MapEntryTbl,X	   ;($D94B)
		BNE NextMapEntry1	   ;($D94E)If not, branch to check next table entry.

		LDA CharXPos			;($D950)Does the X position in the table match the player's position?
		CMP MapEntryTbl+1,X	 ;($D952)
		BNE NextMapEntry1	   ;($D955)If not, branch to check next table entry.

		LDA CharYPos			;($D957)Does the Y position in the table match the player's position?
		CMP MapEntryTbl+2,X	 ;($D959)
		BNE NextMapEntry1	   ;($D95C)If not, branch to check next table entry.

		LDA MapTargetTbl,X	  ;($D95E)Set the player's new map.
		STA MapNumber		   ;($D961)

		LDA MapTargetTbl+1,X	;($D963)
		STA CharXPos			;($D966)Set player's new X position.
		STA _CharXPos		   ;($D968)
		STA CharXPixelsLB	   ;($D96A)Pixel value will be processed more later.

		LDA MapTargetTbl+2,X	;($D96C)
		STA CharYPos			;($D96F)Set player's new Y position.
		STA _CharYPos		   ;($D971)
		STA CharYPixelsLB	   ;($D973)Pixel value will be processed more later.

		LDA GenByte2C		   ;($D975)Did player just come down stairs?
		BEQ StairsFaceRight	 ;($D977)If so, branch to make player face right.

		LDA MapEntryDirectionTable,Y;($D979)Get player's new facing direction from table.
		JMP SetPlyrPixelLoc	 ;($D97C)($D981)Set player's X and Y pixel location.

StairsFaceRight:
		LDA #DIR_RIGHT		  ;($D97F)Came down stairs. Player always faces right.

SetPlyrPixelLoc:
		AND #$03				;($D981)Save the bits representing the player's facing direction.
		STA CharDirection	   ;($D983)

		LDA #$00				;($D986)
		STA CharXPixelsUB	   ;($D988)Clear out upper byte of player's pixel location.
		STA CharYPixelsUB	   ;($D98A)

		LDX #$04				;($D98C)Prepare to loop 4 times.

		* ASL CharXPixelsLB	 ;($D98E)
		ROL CharXPixelsUB	   ;($D990)Multiply given pixel position by 16 as the block position
		ASL CharYPixelsLB	   ;($D992)has been given. Each block is 16X16 pixels.
		ROL CharYPixelsUB	   ;($D994)
		DEX					 ;($D996)Done multiplying?
		BNE -				   ;($D997)If not, branch to shift again.

		JMP MapChngWithSound	;($D999)($B097)Change maps with stairs sound.

NextMapEntry1:
		INX					 ;($D99C)
		INX					 ;($D99D)Increment to next entry in MapEntryTbl.
		INX					 ;($D99E)

		INY					 ;($D99F)Increment to next entry in MapEntryDirectionTable.

		CPX #$99				;($D9A0)Have all the entries been checked?
		BNE MapCheckLoop1	   ;($D9A2)If not, loop to check another entry.

		JSR Dowindow			;($D9A4)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($D9A7)Dialog window.

		JSR DoDialogLoBlock	 ;($D9A8)($C7CB)Thou cannot enter here...
		.byte $0E			   ;($D9AB)TextBlock 1, entry 14.

		JMP ResumeGamePlay	  ;($D9AC)($CFD9)Give control back to player.

CheckStairs:
		LDA CharXPos			;($D9AF)
		STA XTarget			 ;($D9B1)Get X and Y location of block player is standing on.
		LDA CharYPos			;($D9B3)
		STA YTarget			 ;($D9B5)
		JSR GetBlockID		  ;($D9B7)($AC17)Get description of block.

		LDA TargetResults	   ;($D9BA)Is player standing on a stair down block?
		CMP #BLK_STAIR_DN	   ;($D9BC)
		BNE ChkStairsUp		 ;($D9BE)If not, branch to check for a stair up block.

		JMP StairDownFound	  ;($D9C0)Jump to go down stairs.

ChkStairsUp:
		CMP #BLK_STAIR_UP	   ;($D9C3)Is player standing on stair up block?
		BNE NoStairsFound	   ;($D9C5)If not, branch to tell player no stairs are here.

		LDX #$00				;($D9C7)Zero out indexes.
		LDY #$00				;($D9C9)

MapCheckLoop2:
		LDA MapNumber		   ;($D9CB)Has the right map been found in the table?
		CMP MapTargetTbl,X	  ;($D9CD)
		BNE NextMapEntry2	   ;($D9D0)If not, branch to check next table entry.

		LDA CharXPos			;($D9D2)Does the X position in the table match the player's position?
		CMP MapTargetTbl+1,X	;($D9D4)
		BNE NextMapEntry2	   ;($D9D7)If not, branch to check next table entry.

		LDA CharYPos			;($D9D9)Does the Y position in the table match the player's position?
		CMP MapTargetTbl+2,X	;($D9DB)
		BNE NextMapEntry2	   ;($D9DE)If not, branch to check next table entry.

		LDA #DIR_LEFT		   ;($D9E0)Came up stairs. Player always faces left.

ChangeMaps:
		PHA					 ;($D9E2)Save A on stack.

		LDA MapEntryTbl,X	   ;($D9E3)Set the player's new map.
		STA MapNumber		   ;($D9E6)

		LDA MapEntryTbl+1,X	 ;($D9E8)
		STA CharXPos			;($D9EB)Set player's new X position.
		STA _CharXPos		   ;($D9ED)
		STA CharXPixelsLB	   ;($D9EF)Pixel value will be processed more later.

		LDA MapEntryTbl+2,X	 ;($D9F1)
		STA CharYPos			;($D9F4)Set player's new Y position.
		STA _CharYPos		   ;($D9F6)
		STA CharYPixelsLB	   ;($D9F8)Pixel value will be processed more later.

		PLA					 ;($D9FA)Restore A from stack.
		JMP SetPlyrPixelLoc	 ;($D9FB)($D981)Set player's X and Y pixel location.

NextMapEntry2:
		INX					 ;($D9FE)
		INX					 ;($D9FF)Increment to next entry in MapTargetTbl.
		INX					 ;($DA00)

		INY					 ;($DA01)Increment to next entry in MapEntryDirectionTable.

		CPX #$99				;($DA02)Have all the entries been checked?
		BNE MapCheckLoop2	   ;($DA04)If not, loop to check another entry.

NoStairsFound:
		JSR Dowindow			;($DA06)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DA09)Dialog window.

		JSR DoDialogLoBlock	 ;($DA0A)($C7CB)There are no stairs here...
		.byte $0D			   ;($DA0D)TextBlock1, entry 13.

		JMP ResumeGamePlay	  ;($DA0E)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

;These functions handle non-combat spell casting.

DoSpell:
		LDA SpellFlags		  ;($DA11)
		STA SpellFlagsLB		;($DA13)
		LDA ModsnSpells		 ;($DA15)Get a copy of all the spells the player has.
		AND #$03				;($DA17)
		STA SpellFlagsUB		;($DA19)

		ORA SpellFlagsLB		;($DA1B)Does the player have any spells at all?
		BNE +				   ;($DA1D)If so, branch to bring up spell window.

		JSR Dowindow			;($DA1F)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DA22)Dialog window.

		JSR DoDialogLoBlock	 ;($DA23)($C7CB)Player cannot use the spell...
		.byte $31			   ;($DA26)TextBlock4, entry 1.

		JMP ResumeGamePlay	  ;($DA27)($CFD9)Give control back to player.

		* JSR ShowSpells		;($DA2A)($DB56)Bring up the spell window.

		CMP #WINDOW_ABORT	   ;($DA2D)Was the spell cancelled?
		BNE +				   ;($DA2F)If not, branch.

		JMP ClearNonCombatCommandWindow;($DA31)($CF6A)Remove non-combat command window from screen.

		* PHA				   ;($DA34)Save the spell cast on the stack for now.

		JSR Dowindow			;($DA35)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DA38)Dialog window.

		PLA					 ;($DA39)Load A with the spell cast.
		JSR CheckMP			 ;($DA3A)($DB85)Check if MP is high enough to cast the spell.

		CMP #$32				;($DA3D)TextBlock4, entry 2.
		BNE ChkHeal			 ;($DA3F)($DA47)Check which spell was cast.
		JSR DoMidDialog		 ;($DA41)($C7BD)Thy MP is too low...

		JMP ResumeGamePlay	  ;($DA44)($CFD9)Give control back to player.

ChkHeal:
		CMP #SPL_HEAL		   ;($DA47)Was heal spell cast?
		BNE ChkHurt			 ;($DA49)If not, branch to move on.

		JSR DoHeal			  ;($DA4B)($DBB8)Add points to HP from heal spell.
		JMP ResumeGamePlay	  ;($DA4E)($CFD9)Give control back to player.

ChkHurt:
		CMP #SPL_HURT		   ;($DA51)Was hurt spell cast?
		BNE +				   ;($DA53)If not, branch to move on.

SpellFizzle:
		JSR DoDialogLoBlock	 ;($DA55)($C7CB)But nothing happened...
		.byte $33			   ;($DA58)TextBlock4, entry 3.

		JMP ResumeGamePlay	  ;($DA59)($CFD9)Give control back to player.

		* CMP #SPL_SLEEP		;($DA5C)Was sleep spell cast?
		BEQ SpellFizzle		 ;($DA5E)If so, branch to indicate nothing happened.

		CMP #SPL_RADIANT		;($DA60)Was radiant spell cast?
		BNE ChkRepel			;($DA62)If not, branch to move on.

		LDA MapType			 ;($DA64)Is the player in a dungeon?
		CMP #MAP_DUNGEON		;($DA66)
		BNE SpellFizzle		 ;($DA68)If not, branch to indicate nothing happened.

		LDA #$50				;($DA6A)Set the radiant timer.
		STA RadiantTimer		;($DA6C)

		LDA #WINDOW_DIALOG	  ;($DA6E)Remove the dialog window from the screen.
		JSR RemoveWindow		;($DA70)($A7A2)Remove window from screen.
		LDA #WINDOW_CMD_NONCMB  ;($DA73)Remove the command window from the screen.
		JSR RemoveWindow		;($DA75)($A7A2)Remove window from screen.
		LDA #WINDOW_POPUP	   ;($DA78)Remove the pop-up window from the screen.
		JSR RemoveWindow		;($DA7A)($A7A2)Remove window from screen.

LightIncreaseLoop:
		LDA LightDiameter	   ;($DA7D)Radiant cast. Is the radiant diameter already maxed?
		CMP #$07				;($DA7F)
		BNE +				   ;($DA81)If not, branch to increase the light diameter.
		RTS					 ;($DA83)Else exit.

		* CLC				   ;($DA84)
		ADC #$02				;($DA85)Increase the light diameter by 2 blocks.
		STA LightDiameter	   ;($DA87)

		LDA #SFX_RADIANT		;($DA89)Radiant spell SFX.
		BRK					 ;($DA8B)
		.byte $04, $17		  ;($DA8C)($81A0)InitMusicSFX, bank 1.

		JSR PostMoveUpdate	  ;($DA8E)($B30E)Update nametables after player moves.
		JMP LightIncreaseLoop   ;($DA91)Loop to keep increasing light diameter to maximum.

ChkRepel:
		CMP #SPL_REPEL		  ;($DA94)Was repel cast?
		BNE ChkOutside		  ;($DA96)If not, branch to move on.

		LDA #$FF				;($DA98)Max out the repel timer.
		STA RepelTimer		  ;($DA9A)
		JMP ResumeGamePlay	  ;($DA9C)($CFD9)Give control back to player.

ChkOutside:
		CMP #SPL_OUTSIDE		;($DA9F)Was outside cast?
		BNE ChkHealmore		 ;($DAA1)If not, branch to move on.

		LDA MapNumber		   ;($DAA3)Is player in Erdrick's cave?
		CMP #MAP_ERDRCK_B1	  ;($DAA5)
		BCC ChkGarinhamCave	 ;($DAA7)If not, branch.

		LDX #$27				;($DAA9)Overworld at Erdrick's cave entrance.
		LDA #DIR_DOWN		   ;($DAAB)Player will be facing down.
		JMP ChangeMaps		  ;($DAAD)($D9E2)Load a new map.

ChkGarinhamCave:
		* CMP #MAP_CVGAR_B1	 ;($DAB0)Is player in Garinham cave?
		BCC ChkRockMtn		  ;($DAB2)If not, branch.

		LDX #$39				;($DAB4)Overworld at Garinham cave entrance.
		LDA #DIR_DOWN		   ;($DAB6)Player will be facing down.
		JMP ChangeMaps		  ;($DAB8)($D9E2)Load a new map.

ChkRockMtn:
		CMP #MAP_RCKMTN_B1	  ;($DABB)Is player in the rock mountain cave?
		BCC ChkSwampCave		;($DABD)If not, branch.

		LDX #$18				;($DABF)Overworld at rock mountain cave entrance.
		LDA #DIR_DOWN		   ;($DAC1)Player will be facing down.
		JMP ChangeMaps		  ;($DAC3)($D9E2)Load a new map.

ChkSwampCave:
		CMP #MAP_SWAMPCAVE	  ;($DAC6)Is player in the swamp cave?
		BNE ChkDLCastle		 ;($DAC8)If not, branch.

		LDX #$0F				;($DACA)Overworld at swamp cave entrance.
		LDA #DIR_DOWN		   ;($DACC)Player will be facing down.
		JMP ChangeMaps		  ;($DACE)($D9E2)Load a new map.

ChkDLCastle:
		CMP #MAP_DLCSTL_SL1	 ;($DAD1)Is player in the Dragon Lord's castle?
		BCS OutsideDLCastle	 ;($DAD3)If so, branch to exit castle.

		CMP #MAP_DLCSTL_BF	  ;($DAD5)Is player in the basement of the Dragon Lord's castle?
		BEQ OutsideDLCastle	 ;($DAD7)If so, branch to exit castle.

		JMP SpellFizzle		 ;($DAD9)($DA55)Print text indicating spell did not work.

OutsideDLCastle:
		LDX #$12				;($DADC)Overworld at dragon lord's castle.
		LDA #DIR_DOWN		   ;($DADE)Player will be facing down.
		JMP ChangeMaps		  ;($DAE0)($D9E2)Load a new map.

ChkHealmore:
		CMP #SPL_HEALMORE	   ;($DAE3)Was healmore spell cast?
		BNE ChkReturn		   ;($DAE5)If not, branch to move on.

		JSR DoHealmore		  ;($DAE7)($DBD7)Increase health from healmore spell.
		JMP ResumeGamePlay	  ;($DAEA)($CFD9)Give control back to player.

ChkReturn:
		CMP #SPL_RETURN		 ;($DAED)Was return spell cast?
		BNE UnknownSpell		;($DAEF)If not, branch to exit. Unknown spell. Something went wrong.

		LDA MapType			 ;($DAF1)Is the player in a dungeon?
		CMP #MAP_DUNGEON		;($DAF3)
		BEQ ReturnFail		  ;($DAF5)If so, branch. Spell fails.

		LDA MapNumber		   ;($DAF7)Is the player in the bottom of the Dragon Lord's castle?
		CMP #MAP_DLCSTL_BF	  ;($DAF9)
		BNE DoReturn			;($DAFB)If so, branch. Spell fails.

ReturnFail:
		JMP SpellFizzle		 ;($DAFD)($DA55)Print text indicating spell did not work.

DoReturn:
		LDA #MAP_OVERWORLD	  ;($DB00)Set player's current map as the overworld map.
		STA MapNumber		   ;($DB02)

		LDA #$2A				;($DB04)Set player's new X position right next to the castle.
		STA CharXPos			;($DB06)
		STA _CharXPos		   ;($DB08)
		STA CharXPixelsLB	   ;($DB0A)Pixel value will be processed more later.

		LDA #$2B				;($DB0C)Set player's new Y position right next to the castle.
		STA CharYPos			;($DB0E)
		STA _CharYPos		   ;($DB10)
		STA CharYPixelsLB	   ;($DB12)Pixel value will be processed more later.

		LDA #$00				;($DB14)
		STA CharXPixelsUB	   ;($DB16)Clear out upper byte of player's pixel location.
		STA CharYPixelsUB	   ;($DB18)

		LDX #$04				;($DB1A)Prepare to loop 4 times.

		* ASL CharXPixelsLB	 ;($DB1C)
		ROL CharXPixelsUB	   ;($DB1E)Multiply given pixel position by 16 as the block position
		ASL CharYPixelsLB	   ;($DB20)has been given. Each block is 16X16 pixels.
		ROL CharYPixelsUB	   ;($DB22)
		DEX					 ;($DB24)Done multiplying?
		BNE -				   ;($DB25)If not, branch to shift again.

		LDA #SFX_WVRN_WNG	   ;($DB27)Wyvern wing SFX.
		BRK					 ;($DB29)
		.byte $04, $17		  ;($DB2A)($81A0)InitMusicSFX, bank 1.

		LDA #DIR_DOWN		   ;($DB2C)Set player facing direction to down.
		STA CharDirection	   ;($DB2E)
		JMP MapChngFadeNoSound  ;($DB31)($B08D)Change map with fade out and no stairs sound.

UnknownSpell:
		JMP SpellFizzle		 ;($DB34)($DA55)Print text indicating spell did not work.

;----------------------------------------------------------------------------------------------------

BWScreenFlash:
		LDX #$08				;($DB37)Prepare to flash screen 8 times.
		* JSR WaitForNMI		;($DB39)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($DB3C)($FF74)Wait for VBlank interrupt.

		LDA #%00011001		  ;($DB3F)Change screen to greyscale colors.
		STA PPUControl1		 ;($DB41)

		JSR WaitForNMI		  ;($DB44)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($DB47)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($DB4A)($FF74)Wait for VBlank interrupt.

		LDA #%00011000		  ;($DB4D)Change screen to RGB colors.
		STA PPUControl1		 ;($DB4F)

		DEX					 ;($DB52)Has the screen been flashed 8 times?
		BNE -				   ;($DB53)If not, branch to flash again.
		RTS					 ;($DB55)

;----------------------------------------------------------------------------------------------------

ShowSpells:
		JSR IncDescBuffer	   ;($DB56)($D92E)Write #$01-#$0A to the description buffer.
		LDA #$02				;($DB59)Start description bytes for spells at #$02. 2 will be
		STA SpellDescByte	   ;($DB5B)subtracted before the function returns.
		LDX #$01				;($DB5D)Start at index 1 in the description buffer.

GetSpellsLoop:
		LSR SpellFlagsUB		;($DB5F)Rotate spell flags through the carry bit to see if the
		ROR SpellFlagsLB		;($DB61)player has a given spell. Does the player have the spell?
		BCC nextSpell		   ;($DB63)If not, branch to check the next spell.

		LDA SpellDescByte	   ;($DB65)
		STA DescBuf,X		   ;($DB67)Player has the spell. Put it in the description buffer.
		INX					 ;($DB69)

nextSpell:
		INC SpellDescByte	   ;($DB6A)Increment to next spell description byte.
		LDA SpellDescByte	   ;($DB6C)
		CMP #$0C				;($DB6E)Have all the spells been checked?
		BNE GetSpellsLoop	   ;($DB70)If not, branch to check the next spell.

		LDA #DSC_END			;($DB72)Mark the end of the description buffer.
		STA DescBuf,X		   ;($DB74)

		JSR Dowindow			;($DB76)($C6F0)display on-screen window.
		.byte WND_SPELL2		;($DB79)Spell window.

		CMP #WINDOW_ABORT	   ;($DB7A)Did the player abort the spell selection?
		BEQ ShowSpellEnd		;($DB7C)If so, branch to exit.

		TAX					 ;($DB7E)
		LDA DescBuf+1,X		 ;($DB7F)The value from the description buffer needs to have 2
		SEC					 ;($DB81)subtracted from it to get the proper value for the spell
		SBC #$02				;($DB82)description text. Do that here.

ShowSpellEnd:
		RTS					 ;($DB84)Exit with the spell chosen in the accumulator.

;----------------------------------------------------------------------------------------------------

CheckMP:
		STA SpellToCast		 ;($DB85)
		LDX SpellToCast		 ;($DB87)Does player have enough MP to cast the spell?
		LDA MagicPoints		 ;($DB89)
		CMP SpellCostTbl,X	  ;($DB8B)
		BCS PlayerCastSpell	 ;($DB8E)If so, branch.

		LDA #$32				;($DB90)TextBlock4, entry 2.
		RTS					 ;($DB92)Player does not have enough MP. Return.

PlayerCastSpell:
		SBC SpellCostTbl,X	  ;($DB93)Subtract the spell's required MP from player's MP.
		STA MagicPoints		 ;($DB96)

		LDA SpellToCast		 ;($DB98)
		CLC					 ;($DB9A)Add offset to find spell description.
		ADC #$10				;($DB9B)
		JSR GetDescriptionByte  ;($DB9D)($DBF0)Load byte for item dialog description.

		JSR DoDialogLoBlock	 ;($DBA0)($C7CB)Player chanted the spell...
		.byte $30			   ;($DBA3)TextBlock4, entry 0.

		LDA #SFX_SPELL		  ;($DBA4)Spell cast SFX.
		BRK					 ;($DBA6)
		.byte $04, $17		  ;($DBA7)($81A0)InitMusicSFX, bank 1.

		JSR BWScreenFlash	   ;($DBA9)($DB37)Flash screen in black and white.

		BRK					 ;($DBAC)Wait for the music clip to end.
		.byte $03, $17		  ;($DBAD)($815E)WaitForMusicEnd, bank 1.

		LDA SpellToCast		 ;($DBAF)Save the cast spell number on the stack.
		PHA					 ;($DBB1)

		JSR Dowindow			;($DBB2)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($DBB5)Pop-up window.

		PLA					 ;($DBB6)Return with the cast spell number in the accumulator.
		RTS					 ;($DBB7)

;----------------------------------------------------------------------------------------------------

DoHeal:
		JSR UpdateRandNum	   ;($DBB8)($C55B)Get random number.
		LDA RandomNumberUB	  ;($DBBB)
		AND #$07				;($DBBD)Keep lower 3 bits.
		CLC					 ;($DBBF)Add to 10.
		ADC #$0A				;($DBC0)Heal adds 10 to 17 points to HP.

PlayerAddHP:
		CLC					 ;($DBC2)Did HP value roll over to 0?
		ADC HitPoints		   ;($DBC3)
		BCS PlayerMaxHP		 ;($DBC5)If so, branch to set maxHP.

		CMP DisplayedMaxHP	  ;($DBC7)Did HP value exceed player's max HP?
		BCC +				   ;($DBC9)If not, branch to update HP.

PlayerMaxHP:
		LDA DisplayedMaxHP	  ;($DBCB)Max out player's HP.

		* STA HitPoints		 ;($DBCD)Store player's new HP value.
		JSR LoadRegularBGPal	;($DBCF)($EE28)Load the normal background palette.

		JSR Dowindow			;($DBD2)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($DBD5)Pop-up window.
		RTS					 ;($DBD6)

DoHealmore:
		JSR UpdateRandNum	   ;($DBD7)($C55B)Get random number.
		LDA RandomNumberUB	  ;($DBDA)
		AND #$0F				;($DBDC)Keep lower 4 bits.
		CLC					 ;($DBDE)
		ADC #$55				;($DBDF)Add to 85
		JMP PlayerAddHP		 ;($DBE1)Healmore adds 85 to 100 points to HP.

;----------------------------------------------------------------------------------------------------

CopyEnUpperBytes:
		LDA #$08				;($DBE4)
		STA GenPtr3CLB		  ;($DBE6)Copy the unused enemy bytes into the description buffer.
		LDA #$01				;($DBE8)
		STA GenPtr3CUB		  ;($DBEA)

		LDY #$00				;($DBEC)Index is always 0.
		BEQ GetThisDescLoop	 ;($DBEE)Branch always.

GetDescriptionByte:
		CLC					 ;($DBF0)
		ADC #$03				;($DBF1)Add 4 to the item description entry number and save in X.
		TAX					 ;($DBF3)
		INX					 ;($DBF4)

		LDA DescTblPtr		  ;($DBF5)
		STA GenPtr3CLB		  ;($DBF8)Get the base address of the description table.
		LDA DescTblPtr+1		;($DBFA)
		STA GenPtr3CUB		  ;($DBFD)

		LDY #$00				;($DBFF)Index is always 0. Increment pointer address instead.

DescriptionLoop:
		LDA (GenPtr3C),Y		;($DC01)
		INC GenPtr3CLB		  ;($DC03)Increment through the current description data looking
		BNE +				   ;($DC05)for the end marker.
		INC GenPtr3CUB		  ;($DC07)

		* CMP #TXT_SUBEND	   ;($DC09)Has the end marker been found?
		BNE DescriptionLoop	 ;($DC0B)If not, branch to get another byte of the description.

		DEX					 ;($DC0D)Found the end of the current description. Are we now aligned
		BNE DescriptionLoop	 ;($DC0E)with the desired description? If not, branch.

;At this point, the pointer is pointed at the description byte.
;The byte now needs to be transferred into the description buffer.

GetThisDescLoop:
		LDA (GenPtr3C),Y		;($DC10)
		STA _DescBuf,Y		  ;($DC12)
		INY					 ;($DC15)Get a byte of the desired description.
		CMP #TXT_SUBEND		 ;($DC16)
		BNE GetThisDescLoop	 ;($DC18)Have we found the end marker for the description entry?
		RTS					 ;($DC1A)If not, branch to get next byte in the description.

;----------------------------------------------------------------------------------------------------

CheckInventory:
		JSR CreateInvList	   ;($DC1B)($DF77)Create inventory list in description buffer.
		CPX #INV_NONE		   ;($DC1E)Does player have any inventory?
		BNE ShowInventory	   ;($DC20)If so, branch to show inventory.

		JSR Dowindow			;($DC22)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DC25)Dialog window.

		JSR DoDialogLoBlock	 ;($DC26)($C7CB)Nothing of use has yet been given to thee...
		.byte $3D			   ;($DC29)TextBlock4, entry 13.

		JMP ResumeGamePlay	  ;($DC2A)($CFD9)Give control back to player.

ShowInventory:
		JSR Dowindow			;($DC2D)($C6F0)display on-screen window.
		.byte WND_INVTRY1	   ;($DC30)Player inventory window.

		CMP #WINDOW_ABORT	   ;($DC31)Did player cancel out of inventory window?
		BNE ChkItemUsed		 ;($DC33)If not, branch to check item they selected.

		JMP ClearNonCombatCommandWindow;($DC35)($CF6A)Remove non-combat command window from screen.

ChkItemUsed:
		TAX					 ;($DC38)Load item description byte into A.
		LDA DescBuf+1,X		 ;($DC39)

;----------------------------------------------------------------------------------------------------

		CMP #INV_KEY			;($DC3B)Did player select a key?
		BEQ CheckDoor		   ;($DC3D)If so, branch to check if a door is near.
		JMP ChkHerb			 ;($DC3F)($DCEA)Check if player used an herb.

CheckDoor:
		LDA CharXPos			;($DC42)
		STA XTarget			 ;($DC44)
		LDA CharYPos			;($DC46)Check for a door above the player.
		STA YTarget			 ;($DC48)
		DEC YTarget			 ;($DC4A)
		JSR GetBlockID		  ;($DC4C)($AC17)Get description of block.

		LDA TargetResults	   ;($DC4F)Is there a door above the player?
		CMP #BLK_DOOR		   ;($DC51)
		BEQ DoorFound		   ;($DC53)If so, branch.

		LDA CharXPos			;($DC55)
		STA XTarget			 ;($DC57)
		LDA CharYPos			;($DC59)Check for a door below the player.
		STA YTarget			 ;($DC5B)
		INC YTarget			 ;($DC5D)
		JSR GetBlockID		  ;($DC5F)($AC17)Get description of block.

		LDA TargetResults	   ;($DC62)Is there a door below the player?
		CMP #BLK_DOOR		   ;($DC64)
		BEQ DoorFound		   ;($DC66)If so, branch.

		LDA CharXPos			;($DC68)
		STA XTarget			 ;($DC6A)
		LDA CharYPos			;($DC6C)Check for a door to the left of the player.
		STA YTarget			 ;($DC6E)
		DEC XTarget			 ;($DC70)
		JSR GetBlockID		  ;($DC72)($AC17)Get description of block.

		LDA TargetResults	   ;($DC75)Id there a door to the left of the player?
		CMP #BLK_DOOR		   ;($DC77)
		BEQ DoorFound		   ;($DC79)If so, branch.

		LDA CharXPos			;($DC7B)
		STA XTarget			 ;($DC7D)
		LDA CharYPos			;($DC7F)Check for a door to the right of the player.
		STA YTarget			 ;($DC81)
		INC XTarget			 ;($DC83)
		JSR GetBlockID		  ;($DC85)($AC17)Get description of block.

		LDA TargetResults	   ;($DC88)Is there a door to the right of the player?
		CMP #BLK_DOOR		   ;($DC8A)
		BEQ DoorFound		   ;($DC8C)If so, branch.

		JSR Dowindow			;($DC8E)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DC91)Dialog window.

		JSR DoDialogHiBlock	 ;($DC92)($C7C5)There is no door here...
		.byte $0B			   ;($DC95)TextBlock17, entry 11.

		JMP ResumeGamePlay	  ;($DC96)($CFD9)Give control back to player.

DoorFound:
		LDA InventoryKeys	   ;($DC99)Does the player have a key to use?
		BNE UseKey			  ;($DC9B)If so, branch.

		JSR Dowindow			;($DC9D)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DCA0)Dialog window.

		JSR DoDialogHiBlock	 ;($DCA1)($C7C5)Thou has not a key to use...
		.byte $0C			   ;($DCA4)TextBlock17, entry 12.

		JMP ResumeGamePlay	  ;($DCA5)($CFD9)Give control back to player.

UseKey:
		DEC InventoryKeys	   ;($DCA8)Remove a key from the player's inventory.

		LDX #$00				;($DCAA)Zero out the index.

DoorCheckLoop:
		LDA DoorXPos,X		  ;($DCAC)Is this an empty spot to record the opened door?
		BEQ DoorOpened		  ;($DCAF)If so, branch.

		INX					 ;($DCB1)Move to next open door slot.
		INX					 ;($DCB2)
		CPX #$10				;($DCB3)Have 5 slots been searched?
		BNE DoorCheckLoop	   ;($DCB5)If not, branch to check next door slot.

		JMP ResumeGamePlay	  ;($DCB7)($CFD9)Give control back to player.

DoorOpened:
		LDA _TargetX			;($DCBA)
		STA DoorXPos,X		  ;($DCBC)Save the position of the door to indicate it has been opened.
		LDA _TargetY			;($DCBF)
		STA DoorYPos,X		  ;($DCC1)

		LDA _TargetX			;($DCC4)
		SEC					 ;($DCC6)
		SBC CharXPos			;($DCC7)Calculate the block X position to remove the door.
		ASL					 ;($DCC9)
		STA XPosFromCenter	  ;($DCCA)

		LDA _TargetY			;($DCCC)
		SEC					 ;($DCCE)
		SBC CharYPos			;($DCCF)Calculate the block Y position to remove the door.
		ASL					 ;($DCD1)
		STA YPosFromCenter	  ;($DCD2)

		LDA #$00				;($DCD4)Remove no tiles from the changed block.
		STA BlkRemoveFlgs	   ;($DCD6)

		LDA #SFX_DOOR		   ;($DCD8)Door SFX.
		BRK					 ;($DCDA)
		.byte $04, $17		  ;($DCDB)($81A0)InitMusicSFX, bank 1.

		JSR ModMapBlock		 ;($DCDD)($AD66)Change block on map.

		* JSR GetJoypadStatus   ;($DCE0)($C608)Get input button presses.
		LDA JoypadBtns		  ;($DCE3)Have any buttons been pressed?
		BNE -				   ;($DCE5)If not, loop until something is pressed.

		JMP ClearNonCombatCommandWindow;($DCE7)($CF6A)Clear non-combat command window.

;----------------------------------------------------------------------------------------------------

ChkHerb:
		CMP #INV_HERB		   ;($DCEA)Did player use an herb?
		BNE ChkTorch			;($DCEC)If not, branch.

		JSR Dowindow			;($DCEE)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DCF1)Dialog window.

		JSR DoDialogLoBlock	 ;($DCF2)($C7CB)Player used the herb.
		.byte $F7			   ;($DCF5)TextBlock16, entry 7.

		DEC InventoryHerbs	  ;($DCF6)Remove an herb from the player's inventory.

		JSR HerbHeal			;($DCF8)($DCFE)Heal player from an herb.
		JMP ResumeGamePlay	  ;($DCFB)($CFD9)Give control back to player.

HerbHeal:
		JSR UpdateRandNum	   ;($DCFE)($C55B)Get random number.

		LDA RandomNumberUB	  ;($DD01)Get lower 3 bits of a random number.
		AND #$07				;($DD03)

		CLC					 ;($DD05)
		ADC #$17				;($DD06)Herb will heal 23-30 HP.
		ADC HitPoints		   ;($DD08)

		CMP DisplayedMaxHP	  ;($DD0A)Did the player's HP exceed the maximum?
		BCC +				   ;($DD0C)If not, banch.

		LDA DisplayedMaxHP	  ;($DD0E)Max out player's HP.

		* STA HitPoints		 ;($DD10)Update player's HP.
		JSR LoadRegularBGPal	;($DD12)($EE28)Load the normal background palette.

		JSR Dowindow			;($DD15)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($DD18)Pop-up window.
		RTS					 ;($DD19)

;----------------------------------------------------------------------------------------------------

ChkTorch:
		CMP #INV_TORCH		  ;($DD1A)Did player use a torch?
		BNE ChkFryWtr		   ;($DD1C)If not, branch.

		LDA MapType			 ;($DD1E)Is the player in a dungeon?
		CMP #MAP_DUNGEON		;($DD20)
		BEQ UseTorch			;($DD22)if so, branch.

		JSR Dowindow			;($DD24)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DD27)Dialog window.

		JSR DoDialogLoBlock	 ;($DD28)($C7CB)A torch can only be used in dark places...
		.byte $35			   ;($DD2B)TextBlock4, entry 5.

		JMP ResumeGamePlay	  ;($DD2C)($CFD9)Give control back to player.

UseTorch:
		LDA #ITM_TORCH		  ;($DD2F)Remove torch from inventory.
		JSR RemoveInvItem	   ;($DD31)($E04B)Remove item from inventory.

		LDA #$00				;($DD34)Clear any remaining time in the radiant timer.
		STA RadiantTimer		;($DD36)

		LDA #WINDOW_DIALOG	  ;($DD38)Remove the dialog window.
		JSR RemoveWindow		;($DD3A)($A7A2)Remove window from screen.
		LDA #WINDOW_CMD_NONCMB  ;($DD3D)Remove command window.
		JSR RemoveWindow		;($DD3F)($A7A2)Remove window from screen.
		LDA #WINDOW_POPUP	   ;($DD42)Remove pop-up window.
		JSR RemoveWindow		;($DD44)($A7A2)Remove window from screen.

		LDA #$03				;($DD47)Set the light diameter to 3 blocks.
		STA LightDiameter	   ;($DD49)

		LDA #SFX_RADIANT		;($DD4B)Radiant spell SFX.
		BRK					 ;($DD4D)
		.byte $04, $17		  ;($DD4E)($81A0)InitMusicSFX, bank 1.

		JMP PostMoveUpdate	  ;($DD50)($B30E)Update nametables after player moves.

;----------------------------------------------------------------------------------------------------

ChkFryWtr:
		CMP #INV_FAIRY		  ;($DD53)Did player use fairy water?
		BNE ChkWings			;($DD55)If not, branch.

		JSR Dowindow			;($DD57)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DD5A)Dialog window.

		JSR DoDialogLoBlock	 ;($DD5B)($C7CB)Player sprinkled the fairy water over his body...
		.byte $36			   ;($DD5E)TextBlock4, entry 6.

		LDA #ITM_FRY_WATER	  ;($DD5F)Remove the fairy water from the player's inventory.
		JSR RemoveInvItem	   ;($DD61)($E04B)Remove item from inventory.

		LDA #$FE				;($DD64)Set the repel timer.
		STA RepelTimer		  ;($DD66)
		JMP ResumeGamePlay	  ;($DD68)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

ChkWings:
		CMP #INV_WINGS		  ;($DD6B)Did player use the wyvern wings?
		BNE ChkDrgnScl		  ;($DD6D)If not, branch.

		JSR Dowindow			;($DD6F)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DD72)Dialog window.

		LDA MapType			 ;($DD73)Is player in a dungeon?
		CMP #MAP_DUNGEON		;($DD75)
		BEQ WingsFail		   ;($DD77)If so, branch to not use the wing.

		LDA MapNumber		   ;($DD79)Is player in basement of the dragon lord's castle?
		CMP #MAP_DLCSTL_BF	  ;($DD7B)
		BNE UseWings			;($DD7D)If not, branch to use the wing.

WingsFail:
		JSR DoDialogLoBlock	 ;($DD7F)($C7CB)TextBlock4, entry 8.
		.byte $38			   ;($DD82)The wings cannot be used here...

		JMP ResumeGamePlay	  ;($DD83)($CFD9)Give control back to player.

UseWings:
		LDA #ITM_WINGS		  ;($DD86)Remove wings from inventory.
		JSR RemoveInvItem	   ;($DD88)($E04B)Remove item from inventory.

		JSR DoDialogLoBlock	 ;($DD8B)($C7CB)TextBlock4, entry 9.
		.byte $39			   ;($DD8E)Player threw the wings into the air...

		JSR BWScreenFlash	   ;($DD8F)($DB37)Flash screen in black and white.
		JMP DoReturn			;($DD92)($DB00)Return player back to the castle.

;----------------------------------------------------------------------------------------------------

ChkDrgnScl:
		CMP #INV_SCALE		  ;($DD95)Did player use the dragon's scale?
		BNE ChkFryFlt		   ;($DD97)If not, branch.

		JSR Dowindow			;($DD99)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DD9C)Dialog window.

		JSR ChkDragonScale	  ;($DD9D)($DFB9)Check if player is wearing the dragon's scale.
		JMP ResumeGamePlay	  ;($DDA0)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

ChkFryFlt:
		CMP #INV_FLUTE		  ;($DDA3)Did player use the fairy's flute?
		BNE ChkFghtrRng		 ;($DDA5)If not, branch.

		JSR Dowindow			;($DDA7)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DDAA)Dialog window.

		JSR DoDialogLoBlock	 ;($DDAB)($C7CB)Player blew the faries' flute...
		.byte $3C			   ;($DDAE)TextBlock4, entry 12.

		LDA #MSC_FRY_FLUTE	  ;($DDAF)Fairy flute music.
		BRK					 ;($DDB1)
		.byte $04, $17		  ;($DDB2)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($DDB4)Wait for the music clip to end.
		.byte $03, $17		  ;($DDB5)($815E)WaitForMusicEnd, bank 1.

		LDX MapNumber		   ;($DDB7)Get current map number.
		LDA ResumeMusicTable,X  ;($DDB9)Use current map number to resume music.
		BRK					 ;($DDBC)
		.byte $04, $17		  ;($DDBD)($81A0)InitMusicSFX, bank 1.

		JSR DoDialogLoBlock	 ;($DDBF)($C7CB)But nothing happened...
		.byte $33			   ;($DDC2)TextBlock4, entry 3.

		JMP ResumeGamePlay	  ;($DDC3)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

ChkFghtrRng:
		CMP #INV_RING		   ;($DDC6)Did player use the fighter's ring?
		BNE ChkToken			;($DDC8)If not, branch.

		JSR Dowindow			;($DDCA)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DDCD)Dialog window.

		JSR ChkRing			 ;($DDCE)($DFD1)Check if player is wearing the ring.
		JMP ResumeGamePlay	  ;($DDD1)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

ChkToken:
		CMP #INV_TOKEN		  ;($DDD4)Did the player use Erdrick's token?
		BNE ChkStones		   ;($DDD6)If not, branch.

		JSR Dowindow			;($DDD8)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DDDB)Dialog window.

		LDA #$38				;($DDDC)Index to Erdrick's token description.

DoItemDescription:
		JSR GetDescriptionByte  ;($DDDE)($DBF0)Load byte for item dialog description.

		JSR DoDialogLoBlock	 ;($DDE1)($C7CB)Player held the item tightly...
		.byte $40			   ;($DDE4)TextBox5, entry 0.

		JSR DoDialogLoBlock	 ;($DDE5)($C7CB)But nothing happened...
		.byte $33			   ;($DDE8)TextBlock4, entry 3.

		JMP ResumeGamePlay	  ;($DDE9)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

ChkStones:
		CMP #INV_STONES		 ;($DDEC)Did the player use the stones of sunlight?
		BNE ChkStaff			;($DDEE)If not, branch.

		JSR Dowindow			;($DDF0)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DDF3)Dialog window.

		LDA #$3D				;($DDF4)Index to stones of sunlight description.
		BNE DoItemDescription   ;($DDF6)Branch always.

;----------------------------------------------------------------------------------------------------

ChkStaff:
		CMP #INV_STAFF		  ;($DDF8)Did the player use the staff of rain?
		BNE ChkHarp			 ;($DDFA)If not, branch.

		JSR Dowindow			;($DDFC)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DDFF)Dialog window.

		LDA #$3E				;($DE00)Index to staff of rain description.
		BNE DoItemDescription   ;($DE02)Branch always.

;----------------------------------------------------------------------------------------------------

ChkHarp:
		CMP #INV_HARP		   ;($DE04)Did the player use the harp?
		BNE ChkBelt			 ;($DE06)If not, branch.

		JSR Dowindow			;($DE08)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DE0B)Dialog window.

		JSR DoDialogLoBlock	 ;($DE0C)($C7CB)Player played a sweet melody on the harp...
		.byte $41			   ;($DE0F)TextBox5, entry 1.

		LDA #MSC_SILV_HARP	  ;($DE10)Silver harp music.
		BRK					 ;($DE12)
		.byte $04, $17		  ;($DE13)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($DE15)Wait for the music clip to end.
		.byte $03, $17		  ;($DE16)($815E)WaitForMusicEnd, bank 1.

		LDA MapNumber		   ;($DE18)Is the player on the overworld map?
		CMP #MAP_OVERWORLD	  ;($DE1A)
		BNE HarpFail			;($DE1C)If not, branch. Harp only work in the overworld.

HarpRNGLoop:
		JSR UpdateRandNum	   ;($DE1E)($C55B)Get random number.
		LDA RandomNumberUB	  ;($DE21)
		AND #$07				;($DE23)Choose a random number that is 0, 1, 2, 3, 4 or 6.
		CMP #$05				;($DE25)
		BEQ HarpRNGLoop		 ;($DE27)The harp will summon either a slime, red slime, drakee
		CMP #$07				;($DE29)ghost, magician or scorpion.
		BEQ HarpRNGLoop		 ;($DE2B)Works even after the dragon lord is dead.

		PHA					 ;($DE2D)Store the random enemy number on the stack.

		LDA #WINDOW_DIALOG	  ;($DE2E)Remove the dialog window.
		JSR RemoveWindow		;($DE30)($A7A2)Remove window from screen.
		LDA #WINDOW_CMD_NONCMB  ;($DE33)Remove the command window.
		JSR RemoveWindow		;($DE35)($A7A2)Remove window from screen.
		LDA #WINDOW_POPUP	   ;($DE38)Remove the popup window.
		JSR RemoveWindow		;($DE3A)($A7A2)Remove window from screen.

		PLA					 ;($DE3D)Restore the enemy number back to A.
		JMP InitFight		   ;($DE3E)($E4DF)Begin fight sequence.

HarpFail:
		LDX MapNumber		   ;($DE41)Get current map number.
		LDA ResumeMusicTbl,X	;($DE43)Use current map number to resume music.
		BRK					 ;($DE46)
		.byte $04, $17		  ;($DE47)($81A0)InitMusicSFX, bank 1.

		JSR DoDialogLoBlock	 ;($DE49)($C7CB)But nothing happened...
		.byte $33			   ;($DE4C)TextBox4, entry 3.

		JMP ResumeGamePlay	  ;($DE4D)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

ChkBelt:
		CMP #INV_BELT		   ;($DE50)Did the player use the cursed belt?
		BNE ChkNecklace		 ;($DE52)If not, branch.

		JSR Dowindow			;($DE54)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DE57)Dialog window.

		JSR WearCursedItem	  ;($DE58)($DFE7)Player puts on cursed item.

		LDX MapNumber		   ;($DE5B)Get current map number.
		LDA ResumeMusicTbl,X	;($DE5D)Use current map number to resume music.
		BRK					 ;($DE60)
		.byte $04, $17		  ;($DE61)($81A0)InitMusicSFX, bank 1.

		JMP ResumeGamePlay	  ;($DE63)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

ChkNecklace:
		CMP #INV_NECKLACE	   ;($DE66)Did the player use the death necklace?
		BNE ChkDrop			 ;($DE68)If not, branch.

		JSR Dowindow			;($DE6A)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DE6D)Dialog window.

		JSR ChkDeathNecklace	;($DE6E)($E00A)Check if player is wearking the death necklace.

		LDX MapNumber		   ;($DE71)Get current map number.
		LDA ResumeMusicTbl,X	;($DE73)Use current map number to resume music.
		BRK					 ;($DE76)
		.byte $04, $17		  ;($DE77)($81A0)InitMusicSFX, bank 1.

		JMP ResumeGamePlay	  ;($DE79)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

ChkDrop:
		CMP #INV_DROP		   ;($DE7C)Did the player use the rainbow drop?
		BEQ +				   ;($DE7E)If so, branch.

		JMP ChkLove			 ;($DE80)Jump to see if player used Gwaelin's love.

		* JSR Dowindow		  ;($DE83)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DE86)Dialog window.

		JSR DoDialogLoBlock	 ;($DE87)($C7CB)Player held the rainbow drop toward the sky...
		.byte $04			   ;($DE8A)TextBox1, entry 4.

		LDA MapNumber		   ;($DE8B)Is the player on the overworld map?
		CMP #MAP_OVERWORLD	  ;($DE8D)
		BNE RainbowFail		 ;($DE8F)If not, branch. The rainbow bridge creation failed.

		LDA CharXPos			;($DE91)Is the player in the correct X position?
		CMP #$41				;($DE93)
		BNE RainbowFail		 ;($DE95)If not, branch. The rainbow bridge creation failed.

		LDA CharYPos			;($DE97)Is the player in the correct Y position?
		CMP #$31				;($DE99)
		BNE RainbowFail		 ;($DE9B)If not, branch. The rainbow bridge creation failed.

		LDA ModsnSpells		 ;($DE9D)Has the rainbow bridge already been built?
		AND #F_RNBW_BRDG		;($DE9F)
		BNE RainbowFail		 ;($DEA1)If not, branch. The rainbow bridge creation failed.

		LDA #WINDOW_DIALOG	  ;($DEA3)Remove the dialog window.
		JSR RemoveWindow		;($DEA5)($A7A2)Remove window from screen.
		LDA #WINDOW_CMD_NONCMB  ;($DEA8)Remove the command window.
		JSR RemoveWindow		;($DEAA)($A7A2)Remove window from screen.
		LDA #WINDOW_POPUP	   ;($DEAD)remove the pop-up window.
		JSR RemoveWindow		;($DEAF)($A7A2)Remove window from screen.

		LDA #MSC_RNBW_BRDG	  ;($DEB2)Rainbow bridge music.
		BRK					 ;($DEB4)
		.byte $04, $17		  ;($DEB5)($81A0)InitMusicSFX, bank 1.

		LDA ModsnSpells		 ;($DEB7)
		ORA #F_RNBW_BRDG		;($DEB9)Indicate rainbow bridge has been made.
		STA ModsnSpells		 ;($DEBB)

		LDA #$FE				;($DEBD)
		STA XPosFromCenter	  ;($DEBF)Prepare to create the rainbow bridge 2
		LDA #$00				;($DEC1)tiles to the left of the player.
		STA YPosFromCenter	  ;($DEC3)

		LDA #$04				;($DEC5)Prepare to cycle the rainbow flash colors 4 times.
		STA BridgeFlashCounter  ;($DEC7)

BuildBridgeLoop2:
		LDA #$21				;($DEC9)Load the initial color for rainbow flash.
		STA PPUDataByte		 ;($DECB)

BuildBridgeLoop1:
		JSR WaitForNMI		  ;($DECD)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($DED0)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($DED3)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($DED6)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($DED9)($FF74)Wait for VBlank interrupt.

		LDA #$03				;($DEDC)Prepare to change a background palette color.
		STA PPUAddrLB		   ;($DEDE)This is the palette location that creates the
		LDA #$3F				;($DEE0)multicolor water effect when the rainbow bridge
		STA PPUAddrUB		   ;($DEE2)animation is occurring.

		JSR AddPPUBufferEntry   ;($DEE4)($C690)Add data to PPU buffer.

		INC PPUDataByte		 ;($DEE7)Increment to next palette color.

		LDA PPUDataByte		 ;($DEE9)Has the last palette color ben shown?
		CMP #$12				;($DEEB)
		BEQ BridgeAnimDone	  ;($DEED)If so, branch to end the animation.

		CMP #$2D				;($DEEF)Has the last palette color in the flash cycle completed?
		BNE BuildBridgeLoop1	;($DEF1)If not, branch to do the next color.

		DEC BridgeFlashCounter  ;($DEF3)Has 4 cycles of flashing colors finished?
		BNE BuildBridgeLoop2	;($DEF5)If not, branch to do another cycle.

		LDA #$11				;($DEF7)Move to the next colors in the palette.
		STA PPUDataByte		 ;($DEF9)
		BNE BuildBridgeLoop1	;($DEFB)Branch always.

BridgeAnimDone:
		BRK					 ;($DEFD)Wait for the music clip to end.
		.byte $03, $17		  ;($DEFE)($815E)WaitForMusicEnd, bank 1.

		LDA #MSC_OUTDOOR		;($DF00)Outdoor music.
		BRK					 ;($DF02)
		.byte $04, $17		  ;($DF03)($81A0)InitMusicSFX, bank 1.

		JMP ModMapBlock		 ;($DF05)($AD66)Change block on map.

RainbowFail:
		LDA #$05				;($DF08)TextBlock1, entry 5.
		JMP DoFinalDialog	   ;($DF0A)($D242)But no rainbow appeared here...

;----------------------------------------------------------------------------------------------------

ChkLove:
		CMP #INV_LOVE		   ;($DF0D)Did player use Gwaelin's love?
		BNE EndItemChecks	   ;($DF0F)If not, branch to end. No more items to check.

		JSR Dowindow			;($DF11)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($DF14)Dialog window.

		LDA DisplayedLevel	  ;($DF15)Is player at the max level?
		CMP #LEVEL_30		   ;($DF17)
		BNE DoLoveExp		   ;($DF19)If so, branch to skip showing experience for next level.

		JSR DoDialogHiBlock	 ;($DF1B)($C7C5)Know thou hast reached the final level...
		.byte $05			   ;($DF1E)TextBlock17, entry 5.

		JMP ChkLoveMap		  ;($DF1F)Max level already reached. Skip experience dialog.

DoLoveExp:
		JSR GetExperienceRemaining;($DF22)($F134)Calculate experience needed for next level.

		JSR DoDialogLoBlock	 ;($DF25)($C7CB)To reach the next level...
		.byte $DB			   ;($DF28)TextBlock14, entry 11.

ChkLoveMap:
		LDA MapNumber		   ;($DF29)Is player not on the overworld?
		CMP #MAP_OVERWORLD	  ;($DF2B)
		BNE LastLoveDialog	  ;($DF2D)If not, branch to skip showing distance to castle.

		JSR DoDialogLoBlock	 ;($DF2F)($C7CB)From where thou art now, my castle lies...
		.byte $DC			   ;($DF32)TextBlock14, entry 12.

		JSR DoDialogLoBlock	 ;($DF33)($C7CB)Empty text.
		.byte $DD			   ;($DF36)TextBlock14, entry 13.

		LDA CharYPos			;($DF37)Calculate player's Y distance from castle.
		SEC					 ;($DF39)
		SBC #$2B				;($DF3A)Is distance a positive value?
		BCS YDiffDialog		 ;($DF3C)If so, branch to display value to player.

		EOR #$FF				;($DF3E)
		STA GenByte00		   ;($DF40)Do 2's compliment on number to turn it positive.
		INC GenByte00		   ;($DF42)

		LDA #$DF				;($DF44)TextBlock14, entry 15. To the south...
		BNE DoNorthSouthDialog  ;($DF46)Branch always.

YDiffDialog:
		STA GenByte00		   ;($DF48)Store Y distance from the castle.

		LDA #$DE				;($DF4A)TextBlock14, entry 14. To the north...

DoNorthSouthDialog:
		LDX #$00				;($DF4C)Zero out register. Never used.
		STX GenByte01		   ;($DF4E)
		JSR DoMidDialog		 ;($DF50)($C7BD)Show north/south dialog.

		LDA CharXPos			;($DF53)Calculate player's X distance from castle.
		SEC					 ;($DF55)
		SBC #$2B				;($DF56)Is distance a positive value?
		BCS XDiffDialog		 ;($DF58)If so, branch to display value to player.

		EOR #$FF				;($DF5A)
		STA GenByte00		   ;($DF5C)Do 2's compliment on number to turn it positive.
		INC GenByte00		   ;($DF5E)

		LDA #$E0				;($DF60)TextBlock15, entry 0. To the east...
		BNE DoEastWestDialog	;($DF62)Branch always.

XDiffDialog:
		STA GenByte00		   ;($DF64)Store X distance from the castle.

		LDA #$E1				;($DF66)TextBlock15, entry 1. To the west...

DoEastWestDialog:
		LDX #$00				;($DF68)Zero out register. Never used.
		STX GenByte01		   ;($DF6A)
		JSR DoMidDialog		 ;($DF6C)($C7BD)Show east/west dialog.

LastLoveDialog:
		LDA #$BD				;($DF6F)TextBlock12, entry 13.
		JMP DoFinalDialog	   ;($DF71)($D242)I love thee...

EndItemChecks:
		JMP ResumeGamePlay	  ;($DF74)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

CreateInvList:
		LDX #$00				;($DF77)
		LDA #$01				;($DF79)Start the buffer with the value #$01.
		STA DescBuf,X		   ;($DF7B)

		INX					 ;($DF7D)Does the player have herbs?
		LDA InventoryHerbs	  ;($DF7E)
		BEQ +				   ;($DF80)If not branch to check for keys.

		LDA #$02				;($DF82)
		STA DescBuf,X		   ;($DF84)Add herbs description pointer to buffer.
		INX					 ;($DF86)

		* LDA InventoryKeys	 ;($DF87)Does the player have keys?
		BEQ +				   ;($DF89)If not, branch.

		LDA #$03				;($DF8B)
		STA DescBuf,X		   ;($DF8D)Add keys description pointer to buffer.
		INX					 ;($DF8F)

		* LDY #$00			  ;($DF90)Set pointer to first inventory byte.

InvListLoop:
		LDA InventoryPtr,Y	  ;($DF92)Get inventory byte.
		AND #$0F				;($DF95)Extract lower inventory item.
		BEQ +				   ;($DF97)Branch to upper item if empty.
		CLC					 ;($DF99)
		ADC #$03				;($DF9A)
		STA DescBuf,X		   ;($DF9C)Add 3 to pointer value and add to description buffer.
		INX					 ;($DF9E)

		* LDA InventoryPtr,Y	;($DF9F)Get inventory byte.
		AND #$F0				;($DFA2)
		BEQ +				   ;($DFA4)Branch to check next byte if empty.
		LSR					 ;($DFA6)
		LSR					 ;($DFA7)Move upper nibble to lower nibble.
		LSR					 ;($DFA8)
		LSR					 ;($DFA9)
		ADC #$03				;($DFAA)Add 3 to pointer value and add to description buffer.
		STA DescBuf,X		   ;($DFAC)

		INX					 ;($DFAE)Move to next slot in description buffer.
		* INY				   ;($DFAF)Move to next slot in inventory.
		CPY #$04				;($DFB0)Have 4 inventory bytes been processed?
		BNE InvListLoop		 ;($DFB2)If not, branch to process more.

		LDA #$FF				;($DFB4)
		STA DescBuf,X		   ;($DFB6)End description buffer with #$FF.
		RTS					 ;($DFB8)

;----------------------------------------------------------------------------------------------------

ChkDragonScale:
		LDA ModsnSpells		 ;($DFB9)Is player alreay wearing the dragon scale?
		AND #F_DRGSCALE		 ;($DFBB)
		BNE DrgScaleDialog	  ;($DFBD)If so, branch.

		LDA ModsnSpells		 ;($DFBF)
		ORA #F_DRGSCALE		 ;($DFC1)Set dragon's scale flag.
		STA ModsnSpells		 ;($DFC3)

		JSR DoDialogLoBlock	 ;($DFC5)($C7CB)Player donned the scale of the dragon...
		.byte $3A			   ;($DFC8)TextBlock4, entry 10.

		JMP LoadStats		   ;($DFC9)($F050)Update player attributes.

DrgScaleDialog:
		JSR DoDialogLoBlock	 ;($DFCC)($C7CB)Thou art already wearing the scale...
		.byte $3B			   ;($DFCF)TextBlock4, entry 11.
		RTS					 ;($DFD0)

;----------------------------------------------------------------------------------------------------

ChkRing:
		LDA ModsnSpells		 ;($DFD1)
		AND #F_FTR_RING		 ;($DFD3)Check if already wearing the fighter's ring.
		BNE AlreadyWearingRing  ;($DFD5)If so, branch to adjustment message.
		LDA ModsnSpells		 ;($DFD7)Else set flag and indicate ring is worn.
		ORA #F_FTR_RING		 ;($DFD9)
		STA ModsnSpells		 ;($DFDB)

		JSR DoDialogLoBlock	 ;($DFDD)($C7CB)Player put on the fighter's ring...
		.byte $3E			   ;($DFE0)TextBlock4, entry 14.
		RTS					 ;($DFE1)

AlreadyWearingRing:
		JSR DoDialogLoBlock	 ;($DFE2)($C7CB)Player adjusted the position of the ring...
		.byte $3F			   ;($DFE5)TextBlock4, entry 15.
		RTS					 ;($DFE6)

WearCursedItem:
		LDA #$3A				;($DFE7)Description index for the cursed belt.
		JSR GetDescriptionByte  ;($DFE9)($DBF0)Load byte for item dialog description.
		BIT ModsnSpells		 ;($DFEC)Is the player already wearing a cursed belt?
		BVS DoCursedDialog	  ;($DFEE)If so, branch.

		LDA ModsnSpells		 ;($DFF0)
		ORA #F_CRSD_BELT		;($DFF2)Indicate player is cursed.
		STA ModsnSpells		 ;($DFF4)

PlayerCursed:
		JSR DoDialogLoBlock	 ;($DFF6)($C7CB)Player put on the item and was cursed...
		.byte $42			   ;($DFF9)TextBlock5, entry 2.

PlayCursedMusic:
		LDA #MSC_CURSED		 ;($DFFA)Cursed music.
		BRK					 ;($DFFC)
		.byte $04, $17		  ;($DFFD)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($DFFF)Wait for the music clip to end.
		.byte $03, $17		  ;($E000)($815E)WaitForMusicEnd, bank 1.
		RTS					 ;($E002)

DoCursedDialog:
		JSR DoDialogLoBlock	 ;($E003)($C7CB)The item is squeezing thy body...
		.byte $43			   ;($E006)TextBlock5, entry 3.

		JMP PlayCursedMusic	 ;($E007)($DFFA)Player equipped a cursed object.

ChkDeathNecklace:
		LDA #$3C				;($E00A)Description index for the death necklace.
		JSR GetDescriptionByte  ;($E00C)($DBF0)Load byte for item dialog description.

		LDA ModsnSpells		 ;($E00F)Is the player wearing the death necklace.
		BMI DoCursedDialog	  ;($E011)If so, branch to tell player they are cursed.

		LDA ModsnSpells		 ;($E013)Set the bit indicating the player is wearing the death necklace.
		ORA #F_DTH_NECKLACE	 ;($E015)
		STA ModsnSpells		 ;($E017)
		BNE PlayerCursed		;($E019)Branch always to tell player they are cursed.

;----------------------------------------------------------------------------------------------------

AddInvItem:
		STA GenByte3E		   ;($E01B)Store a copy of the inventory item and zero out index.
		LDX #$00				;($E01D)

AddInvLoop:
		LDA InventorySlot12,X   ;($E01F)Is the lower nibble inventory slot already occupied?
		AND #$0F				;($E021)
		BNE ChkUpperInvNibble   ;($E023)If so, branch to check the upper nibble.

		LDA InventorySlot12,X   ;($E025)
		AND #$F0				;($E027)
		ORA GenByte3E		   ;($E029)Add new inventory item to lower nibble slot.
		STA InventorySlot12,X   ;($E02B)
		RTS					 ;($E02D)

ChkUpperInvNibble:
		LDA InventorySlot12,X   ;($E02E)Is the upper nibble inventory slot already occupied?
		AND #$F0				;($E030)
		BNE ChkNextInvSlot	  ;($E032)If so, branch to check the next inventory byte.

		ASL GenByte3E		   ;($E034)
		ASL GenByte3E		   ;($E036)Slot is open. Move item to upper nibble.
		ASL GenByte3E		   ;($E038)
		ASL GenByte3E		   ;($E03A)

		LDA InventorySlot12,X   ;($E03C)
		AND #$0F				;($E03E)
		ORA GenByte3E		   ;($E040)Add new inventory item to upper nibble slot.
		STA InventorySlot12,X   ;($E042)
		RTS					 ;($E044)

ChkNextInvSlot:
		INX					 ;($E045)Have all 4 bytes of inventory been checked(8 items)?
		CPX #INV_FULL		   ;($E046)
		BNE AddInvLoop		  ;($E048)If not, branch to check another byte.

		RTS					 ;($E04A)Inventory is full. Return.

;----------------------------------------------------------------------------------------------------

RemoveInvItem:
		JSR CheckForInvItem	 ;($E04B)($E055)Get pointer to item in inventory.
		AND InventoryPtr,Y	  ;($E04E)
		STA InventoryPtr,Y	  ;($E051)Clear item from inventory slot.
		RTS					 ;($E054)

;----------------------------------------------------------------------------------------------------

CheckForInvItem:
		LDY #$00				;($E055)Zero out inventory index.
		STA GenByte3C		   ;($E057)Keep a copy of item to find.

InvCheckLoop:
		LDA InventoryPtr,Y	  ;($E059)Check lower inventory item.
		AND #NBL_LOWER		  ;($E05C)
		CMP GenByte3C		   ;($E05E)Is this the desired item?
		BNE +				   ;($E060)If not branch to check next slot.

		LDA #ITM_FOUND_LO	   ;($E062)Item found in the low nibble.
		RTS					 ;($E064)

		* LDA InventoryPtr,Y	;($E065)Reload inventory byte.
		LSR					 ;($E068)
		LSR					 ;($E069)Shift upper item down to lower nibble.
		LSR					 ;($E06A)
		LSR					 ;($E06B)
		CMP GenByte3C		   ;($E06C)Is this the desired item?
		BNE +				   ;($E06E)If not, branch to check if at end of inventory.

		LDA #ITM_FOUND_HI	   ;($E070)Item found in the high nibble.
		RTS					 ;($E072)

		* INY				   ;($E073)Has all the inventory been checked?
		CPY #$04				;($E074)
		BNE InvCheckLoop		;($E076)If not, branch to check next two slots.

		LDA #ITM_NOT_FOUND	  ;($E078)The item was not in the inventory.
		RTS					 ;($E07A)

;----------------------------------------------------------------------------------------------------

DiscardItem:
		STA DialogTemp		  ;($E07B)Store dialog control byte.

		JSR DoDialogLoBlock	 ;($E07D)($C7CB)If thou will take the item, thou must discard something...
		.byte $CC			   ;($E080)TextBlock13, entry 12.

		JSR Dowindow			;($E081)($C6F0)display on-screen window.
		.byte WND_YES_NO1	   ;($E084)Yes/No window.

		BEQ PlayerDiscards	  ;($E085)Branch if player chooses to discard an item.

PlayerNoDiscard:
		LDA DialogTemp		  ;($E087)Player will not discard an item.
		CLC					 ;($E089)
		ADC #$31				;($E08A)
		JSR GetDescriptionByte  ;($E08C)($DBF0)Load byte for item dialog description.

		LDA #$CD				;($E08F)TextBlock13, entry 13.
		JMP DoFinalDialog	   ;($E091)($D242)Thou hast given up thy item...

PlayerDiscards:
		JSR DoDialogLoBlock	 ;($E094)($C7CB)What shall thou drop..
		.byte $CE			   ;($E097)TextBlock13, entry 14.

		JSR CreateInvList	   ;($E098)($DF77)Create inventory list in description buffer.

		JSR Dowindow			;($E09B)($C6F0)display on-screen window.
		.byte WND_INVTRY1	   ;($E09E)Player inventory window.

		CMP #WINDOW_ABORT	   ;($E09F)Did player abort the discard process?
		BEQ PlayerNoDiscard	 ;($E0A1)If so, branch.

		TAX					 ;($E0A3)Prepare a check to see if player is trying to discard
		LDA DescBuf+1,X		 ;($E0A4)an important item that cannot be discarded.
		LDY #$00				;($E0A6)

DiscardCheckLoop:
		CMP NonDiscardTbl,Y	 ;($E0A8)Does the item match a non-discarable item?
		BNE NextDiscardCheck	;($E0AB)If not, branch to check next non-discardable item.

		JSR DoDialogLoBlock	 ;($E0AD)($C7CB)That is much to important to throw away...
		.byte $D1			   ;($E0B0)TextBlock14, entry 1.

		JMP PlayerDiscards	  ;($E0B1)Jump so player can choose another item to discard.

NextDiscardCheck:
		INY					 ;($E0B4)Has the item been checked against all non-discardable items?
		CPY #$09				;($E0B5)
		BNE DiscardCheckLoop	;($E0B7)If not, branch to check against another item.

		CMP #INV_BELT		   ;($E0B9)Is player trying to discard the cursed belt?
		BNE ChkDiscardNecklace  ;($E0BB)If not, branch to check if its the death necklace.

		BIT ModsnSpells		 ;($E0BD)Is the player wearing the cursed belt?
		BVC ChkDiscardNecklace  ;($E0BF)If so, branch to check if player is discarding death necklace.

BodyCursedDialog:
		JSR DoDialogLoBlock	 ;($E0C1)($C7CB)A curse is upon thy body...
		.byte $18			   ;($E0C4)TextBlock2, entry 8.

		JMP PlayerDiscards	  ;($E0C5)Jump so player can choose another item to discard.

ChkDiscardNecklace:
		LDA DescBuf+1,X		 ;($E0C8)Is player trying to discard the death necklace?
		CMP #INV_NECKLACE	   ;($E0CA)
		BNE +				   ;($E0CC)If not, branch.

		LDA ModsnSpells		 ;($E0CE)Is the player wearing the death necklace?
		BMI BodyCursedDialog	;($E0D0)If so, branch to display cursed dialog.

		* LDA DescBuf+1,X	   ;($E0D2)Save a copy of the description of the item.
		PHA					 ;($E0D4)

		CLC					 ;($E0D5)Add offset to find proper description of discarded item.
		ADC #$2E				;($E0D6)
		JSR GetDescriptionByte  ;($E0D8)($DBF0)Load byte for item dialog description.

		JSR DoDialogLoBlock	 ;($E0DB)($C7CB)Thou hast dropped thy item...
		.byte $CF			   ;($E0DE)TextBlock13, entry 15.

		LDA DialogTemp		  ;($E0DF)Add offset to find proper description of gained item.
		CLC					 ;($E0E1)
		ADC #$31				;($E0E2)
		JSR GetDescriptionByte  ;($E0E4)($DBF0)Load byte for item dialog description.

		JSR DoDialogLoBlock	 ;($E0E7)($C7CB)And obtained the item...
		.byte $D0			   ;($E0EA)TextBlock14, entry 0

		PLA					 ;($E0EB)Add offset to get proper item to remove from inventory.
		SEC					 ;($E0EC)
		SBC #$03				;($E0ED)
		JSR RemoveInvItem	   ;($E0EF)($E04B)Remove item from inventory.

		LDA DescTemp			;($E0F2)Prepare to add new item to inventory.
		JSR AddInvItem		  ;($E0F4)($E01B)Add item to inventory.

		JMP ResumeGamePlay	  ;($E0F7)($CFD9)Give control back to player.

;The following table contains items that cannot be discarded by the player.

NonDiscardTbl:
		.byte INV_HERB, INV_KEY,	INV_FLUTE, INV_TOKEN, INV_LOVE;($E0FA)
		.byte INV_HARP, INV_STONES, INV_STAFF, INV_DROP;($E0FF)

;----------------------------------------------------------------------------------------------------

DoSearch:
		JSR Dowindow			;($E103)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($E106)Dialog window.

		JSR DoDialogLoBlock	 ;($E107)($C7CB)Player searched the ground all about...
		.byte $D2			   ;($E10A)TextBlock14, entry 2.

		LDA MapNumber		   ;($E10B)Is player on the overworld map?
		CMP #MAP_OVERWORLD	  ;($E10D)
		BNE NextSearch		  ;($E10F)If not, branch to do other searches.

		LDA CharXPos			;($E111)
		CMP #$53				;($E113)Is player in the proper X any Y position to find Erdrick's token?
		BNE NextSearch		  ;($E115)
		LDA CharYPos			;($E117)If not, branch to do other searches. Erdrick's token is the
		CMP #$71				;($E119)only item to find on the overworld map.
		BNE NextSearch		  ;($E11B)

		LDA #ITM_ERDRICK_TKN	;($E11D)Check to see if the player already has Erdrick's token.

FoundItem:
		STA DescTemp			;($E11F)Prepare to check for existing inventory item.
		JSR CheckForInvItem	 ;($E121)($E055)Check inventory for item.

		CMP #ITM_NOT_FOUND	  ;($E124)Does player already have Erdrick's token?
		BEQ ErdrickTknFound	 ;($E126)If not, branch to try to add it to player's inventory.

ItemAlreadyFound:
		LDA #$D3				;($E128)TextBlock14, entry 3.
		JMP DoFinalDialog	   ;($E12A)($D242)But there found nothing...

ErdrickTknFound:
		LDA DescTemp			;($E12D)Get offset to description byte for Erdrick's token.
		CLC					 ;($E12F)
		ADC #$31				;($E130)
		JSR GetDescriptionByte  ;($E132)($DBF0)Load byte for item dialog description.

		JSR DoDialogLoBlock	 ;($E135)($C7CB)Player discovered the item...
		.byte $D5			   ;($E138)TextBlock14, entry 5.

		LDA DescTemp			;($E139)Prepare to try to add item to inventory.
		JSR AddInvItem		  ;($E13B)($E01B)Add item to inventory.

		CPX #INV_FULL		   ;($E13E)Is player's inventory full?
		BEQ +				   ;($E140)If so, branch.

		JMP ResumeGamePlay	  ;($E142)($CFD9)Give control back to player.

		* LDA DescTemp		  ;($E145)Prepare to tell player inventory is full.
		JMP DiscardItem		 ;($E147)($E07B)Inventory full. Ask player to discard an item.

;----------------------------------------------------------------------------------------------------

NextSearch:
		LDA MapNumber		   ;($E14A)Is player in the town of Kol?
		CMP #MAP_KOL			;($E14C)
		BNE SrchEdrckArmor	  ;($E14E)If not, branch.

		LDA CharXPos			;($E150)
		CMP #$09				;($E152)Is player in the proper location to find the fairy flute?
		BNE SrchEdrckArmor	  ;($E154)
		LDA CharYPos			;($E156)
		CMP #$06				;($E158)If not, branch to move on.
		BNE SrchEdrckArmor	  ;($E15A)

		LDA #ITM_FRY_FLUTE	  ;($E15C)Indicate playe may find the fairy flute.
		BNE FoundItem		   ;($E15E)branch always.

SrchEdrckArmor:
		LDA MapNumber		   ;($E160)Is the player in Huksness?
		CMP #MAP_HAUKSNESS	  ;($E162)
		BNE SrchPassage		 ;($E164)If not, branch.

		LDA CharXPos			;($E166)
		CMP #$12				;($E168)Is player in the proper location to find Erdrick's armor?
		BNE SrchPassage		 ;($E16A)
		LDA CharYPos			;($E16C)
		CMP #$0C				;($E16E)If not, branch to move on.
		BNE SrchPassage		 ;($E170)

		LDA EqippedItems		;($E172)Does player already have Erdrick's armor?
		AND #AR_ARMOR		   ;($E174)
		CMP #AR_ERDK_ARMR	   ;($E176)
		BEQ ItemAlreadyFound	;($E178)If so, branch.

		LDA EqippedItems		;($E17A)
		ORA #AR_ERDK_ARMR	   ;($E17C)Equip player with Erdrick's armor.
		STA EqippedItems		;($E17E)

		LDA #$28				;($E180)Erdrick's armor description byte.
		JSR GetDescriptionByte  ;($E182)($DBF0)Load byte for item dialog description.

		LDA #$D5				;($E185)TextBlock14, entry 5.
		JMP DoFinalDialog	   ;($E187)($D242)Player discovered the item...

SrchPassage:
		LDA MapNumber		   ;($E18A)Is player on the ground floor of the dragonlord's castle?
		CMP #MAP_DLCSTL_GF	  ;($E18C)
		BNE ChkSearchTrsr	   ;($E18E)If not, branch.

		LDA CharXPos			;($E190)
		CMP #$0A				;($E192)Is the player standing in the dragonlord's throne?
		BNE ChkSearchTrsr	   ;($E194)
		LDA CharYPos			;($E196)If so, branch to tell player wind is comming
		CMP #$03				;($E198)from behind the throne.
		BNE +				   ;($E19A)Else branch.

		LDA #$D6				;($E19C)TextBlock14, entry 6.
		JMP DoFinalDialog	   ;($E19E)($D242)Feel the wind behind the throne...

		* CMP #$01			  ;($E1A1)Is player standing behind dragonlord's throne?
		BNE ChkSearchTrsr	   ;($E1A3)If not, branch.

		LDA ModsnSpells		 ;($E1A5)Has player already found the secret passage?
		AND #F_PSG_FOUND		;($E1A7)
		BNE ChkSearchTrsr	   ;($E1A9)If so, branch to move on.

		LDA ModsnSpells		 ;($E1AB)
		ORA #F_PSG_FOUND		;($E1AD)Indicate the player discvered the secret passage.
		STA ModsnSpells		 ;($E1AF)

		LDA #$0F				;($E1B1)Description byte for the secret passage.
		JSR GetDescriptionByte  ;($E1B3)($DBF0)Load byte for item dialog description.

		JSR DoDialogLoBlock	 ;($E1B6)($C7CB)TextBlock14, entry 5.
		.byte $D5			   ;($E1B9)Player discovered the item...

		LDA #$00				;($E1BA)
		STA YPosFromCenter	  ;($E1BC)Change the block the player is standing on to stairs down.
		STA XPosFromCenter	  ;($E1BE)
		STA BlkRemoveFlgs	   ;($E1C0)Remove no tiles from the block.
		JSR ModMapBlock		 ;($E1C2)($AD66)Change block on map.
		JMP ResumeGamePlay	  ;($E1C5)($CFD9)Give control back to player.

ChkSearchTrsr:
		LDA CharXPos			;($E1C8)
		STA XTarget			 ;($E1CA)Get the block description of the block the player is standing on.
		LDA CharYPos			;($E1CC)
		STA YTarget			 ;($E1CE)
		JSR GetBlockID		  ;($E1D0)($AC17)Get description of block.

		LDA TargetResults	   ;($E1D3)Is player standing on a treasure chest?
		CMP #BLK_CHEST		  ;($E1D5)
		BNE +				   ;($E1D7)If not, branch.

		LDA #$D4				;($E1D9)TextBlock14, entry 4.
		JMP DoFinalDialog	   ;($E1DB)($D242)There is a treasure box...

		* LDA #$D3			  ;($E1DE)TextBlock14, entry 3.
		JMP DoFinalDialog	   ;($E1E0)($D242)But there found nothing...

;----------------------------------------------------------------------------------------------------

DoTake:
		JSR Dowindow			;($E1E3)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($E1E6)Dialog window.

		LDA CharXPos			;($E1E7)
		STA XTarget			 ;($E1E9)Get the block description of the block the player is standing on.
		LDA CharYPos			;($E1EB)
		STA YTarget			 ;($E1ED)
		JSR GetBlockID		  ;($E1EF)($AC17)Get description of block.

		LDA TargetResults	   ;($E1F2)Is player standing on a treasure chest?
		CMP #BLK_CHEST		  ;($E1F4)
		BEQ FoundTreasure	   ;($E1F6)If so, branch.

NoTreasureChest:
		LDA #$D7				;($E1F8)TextBlock14, entry 7.
		JMP DoFinalDialog	   ;($E1FA)($D242)There is nothing to take here...

FoundTreasure:
		BRK					 ;($E1FD)Copy treasure table into RAM.
		.byte $08, $17		  ;($E1FE)($994F)CopyTrsrTbl, bank 1.

		LDY #$00				;($E200)Treasure table starts at address $0320.

ChkTrsrTblLoop:
		LDA MapNumber		   ;($E202)Does player map match current treasure chest map?
		CMP TrsrArray,Y		 ;($E204)
		BNE NextTreasureChest   ;($E207)If not, branch to increment to next treasure chest.

		LDA CharXPos			;($E209)Does player X position match treasure chest X position?
		CMP TrsrArray+1,Y	   ;($E20B)
		BNE NextTreasureChest   ;($E20E)If not, branch to increment to next treasure chest.

		LDA CharYPos			;($E210)Does player Y position match treasure chest X position?
		CMP TrsrArray+2,Y	   ;($E212)
		BEQ ChkTrsrKey		  ;($E215)If so, branch. Treasure chest found!

NextTreasureChest:
		INY					 ;($E217)
		INY					 ;($E218)Increment to next entry in treasure chest data array.
		INY					 ;($E219)
		INY					 ;($E21A)

		CPY #$7C				;($E21B)Has the whole treasure chest data array been checked?
		BNE ChkTrsrTblLoop	  ;($E21D)If not, branch to check the next entry.

		BEQ NoTreasureChest	 ;($E21F)No treasure chest found at this location by the player.

;----------------------------------------------------------------------------------------------------

ChkTrsrKey:
		LDA TrsrArray+3,Y	   ;($E221)Did player just find a treasure chest containing a key?
		STA DialogTemp		  ;($E224)
		CMP #TRSR_KEY		   ;($E226)
		BNE ChkTrsrHerb		 ;($E228)If not, branch to check the next treasure type.

		LDA InventoryKeys	   ;($E22A)Does player have the max of 5 keys?
		CMP #$06				;($E22C)
		BNE TrsrGetKey		  ;($E22E)If not, branch to increment keys in inventory.

GetTreasureChest1:
		JSR GetTreasure		 ;($E230)($E39A)Check for valid treasure and get it.

		LDA #$DA				;($E233)TextBlock14, entry 10.
		JMP DoFinalDialog	   ;($E235)($D242)Unfortunately, it is empty...

TrsrGetKey:
		INC InventoryKeys	   ;($E238)Player got a key. Increment keys in inventory.

GetTreasureChest2:
		JSR GetTreasure		 ;($E23A)($E39A)Check for valid treasure and get it.

		LDA #$D9				;($E23D)TextBlock14, entry 9.
		JMP DoFinalDialog	   ;($E23F)($D242)Fortune smiles upon thee...

;----------------------------------------------------------------------------------------------------

ChkTrsrHerb:
		CMP #TRSR_HERB		  ;($E242)Did player just find a treasure chest containing an herb?
		BNE ChkTrsrNecklace	 ;($E244)If not, branch to check the next treasure type.

		LDA InventoryHerbs	  ;($E246)Does player have the max of 5 herbs?
		CMP #$06				;($E248)
		BEQ GetTreasureChest1   ;($E24A)If so, branch to get treasure and exit without incrementing herbs.

		INC InventoryHerbs	  ;($E24C)Increment player's herb inventory.
		BNE GetTreasureChest2   ;($E24E)branch always.

;----------------------------------------------------------------------------------------------------

ChkTrsrNecklace:
		CMP #TRSR_NCK		   ;($E250)Did player just find a treasure chest containing the death necklace?
		BNE ChkTrsrErdSword	 ;($E252)If not, branch to check the next treasure type.

		LDA PlayerFlags		 ;($E254)Did the player already find the death necklace?
		AND #F_DTH_NCK_FOUND	;($E256)
		BNE GetDthNeckGold	  ;($E258)If so, branch to get gold instead.

		JSR UpdateRandNum	   ;($E25A)($C55B)Get random number.
		LDA RandomNumberUB	  ;($E25D)If lower 5 bits are 0, player will receive the
		AND #$1F				;($E25F)death necklace(1 in 32 chance).
		BNE GetDthNeckGold	  ;($E261)($E288)Lower 5 zeros? if not, branch to get gold instead.

		LDA PlayerFlags		 ;($E263)
		ORA #F_DTH_NCK_FOUND	;($E265)Indicate player has found the death necklace.
		STA PlayerFlags		 ;($E267)

;----------------------------------------------------------------------------------------------------

SetTrsrDescByte:
		JSR GetTreasure		 ;($E269)($E39A)Check for valid treasure and get it.
		LDA DescTemp			;($E26C)
		SEC					 ;($E26E)Set the proper index to the description byte for the item.
		SBC #$03				;($E26F)
		STA DescTemp			;($E271)

		JSR DoDialogLoBlock	 ;($E273)($C7CB)Fortune smiles upon thee. Thou hast found the item...
		.byte $D9			   ;($E276)TextBlock14, entry 9.

		LDA DescTemp			;($E277)Add the item to the player's inventory.
		JSR AddInvItem		  ;($E279)($E01B)Add item to inventory.

		CPX #INV_FULL		   ;($E27C)Is the player's inventory full?
		BEQ TrsrInvFull		 ;($E27E)If so, branch to give player the option to drop an item.

		JMP ResumeGamePlay	  ;($E280)($CFD9)Give control back to player.

TrsrInvFull:
		LDA DescTemp			;($E283)Get index to item player is trying to pick up.
		JMP DiscardItem		 ;($E285)($E07B)Inventory full. Ask player to discard an item.

;----------------------------------------------------------------------------------------------------

GetDthNeckGold:
		LDA #$1F				;($E288)Up to 31 extra gold randomly added.
		STA RndGoldBits		 ;($E28A)

		LDA #$64				;($E28C)
		STA TrsrGoldLB		  ;($E28E)100 base gold for this treasure.
		LDA #$00				;($E290)
		STA TrsrGoldUB		  ;($E292)

		JMP GetTrsrGold		 ;($E294)($E365)Calculate treasure gold received.

;----------------------------------------------------------------------------------------------------

ChkTrsrErdSword:
		CMP #TRSR_ERSD		  ;($E297)Did player just find a treasure chest containing Erdrick's sword?
		BNE ChkTrsrHarp		 ;($E299)If not, branch to check the next treasure type.

		LDA EqippedItems		;($E29B)Does the player already have Erdrick's sword?
		AND #WP_WEAPONS		 ;($E29D)
		CMP #WP_ERDK_SWRD	   ;($E29F)
		BNE +				   ;($E2A1)If not, branch.

GetTreasureChest3:
		JMP GetTreasureChest1   ;($E2A3)The treasure chest is empty.

		* LDA EqippedItems	  ;($E2A6)Indicate the player is equipped with Erdrick's sword.
		ORA #WP_ERDK_SWRD	   ;($E2A8)
		STA EqippedItems		;($E2AA)
		JSR GetTreasure		 ;($E2AC)($E39A)Check for valid treasure and get it.

		LDA #$21				;($E2AF)Description byte for Erdrick's sword.
		JSR GetDescriptionByte  ;($E2B1)($DBF0)Load byte for item dialog description.

		LDA #$D9				;($E2B4)TextBlock14, entry 9.
		JMP DoFinalDialog	   ;($E2B6)($D242)Fortune smiles upon thee...

;----------------------------------------------------------------------------------------------------

ChkTrsrHarp:
		CMP #TRSR_HARP		  ;($E2B9)Did player just get chest with the harp, staff or rainbow drop?
		BNE ChkTrsrStones	   ;($E2BB)If not, branch to check the next treasure type.

		LDA #ITM_SLVR_HARP	  ;($E2BD)Check if player has the silver harp.
		JSR CheckForInvItem	 ;($E2BF)($E055)Check if item is already in inventory.

		CMP #ITM_NOT_FOUND	  ;($E2C2)Does player have the silver harp?
		BNE GetTreasureChest3   ;($E2C4)if so, branch got get empty treasure chest.

		LDA #ITM_STFF_RAIN	  ;($E2C6)Check if the player has the staff of rain.
		JSR CheckForInvItem	 ;($E2C8)($E055)Check if item is already in inventory.

		CMP #ITM_NOT_FOUND	  ;($E2CB)Does the player have the staff of rain?
		BNE GetTreasureChest3   ;($E2CD)if so, branch got get empty treasure chest.

ChkRnbwDrop:
		LDA #ITM_RNBW_DROP	  ;($E2CF)Check if the player has the rainbow drop.
		JSR CheckForInvItem	 ;($E2D1)($E055)Check if item is already in inventory.

		CMP #ITM_NOT_FOUND	  ;($E2D4)Does the player have the rainbow drop?
		BNE GetTreasureChest3   ;($E2D6)if so, branch got get empty treasure chest.

		JMP SetTrsrDescByte	 ;($E2D8)Display a message to player about getting the silver harp.

;----------------------------------------------------------------------------------------------------

ChkTrsrStones:
		CMP #TRSR_SUN		   ;($E2DB)Did player just get chest with the stones of sunlight?
		BNE ChkTrsrNonGold	  ;($E2DD)If not, branch to check the next treasure type.

		LDA #ITM_STNS_SNLGHT	;($E2DF)Check if player already has the stones of sunlight.
		JSR CheckForInvItem	 ;($E2E1)($E055)Check if item is already in inventory.

		CMP #ITM_NOT_FOUND	  ;($E2E4)Does the player have the stones of sunlight?
		BNE GetTreasureChest3   ;($E2E6)if so, branch got get empty treasure chest.

		BEQ ChkRnbwDrop		 ;($E2E8)Branch always to check for the rainbow drop.

;----------------------------------------------------------------------------------------------------

ChkTrsrNonGold:
		CMP #TRSR_ERSD		  ;($E2EA)Did player get a non-gold treasure not already checked for?
		BCS ChkTrsrGold1		;($E2EC)If not, branch to check for a gold based treasure.

		JMP SetTrsrDescByte	 ;($E2EE)Branch always to get the treasure and inform the player.

;----------------------------------------------------------------------------------------------------

ChkTrsrGold1:
		CMP #TRSR_GLD1		  ;($E2F1)Did player just get a treasure chest with gold 1 treasure?
		BNE ChkTrsrGold2		;($E2F3)If not, branch to check for gold 2 treasure.

		LDA #$0F				;($E2F5)Max 15 gold randomly added to treasure.
		STA RndGoldBits		 ;($E2F7)

		LDA #$05				;($E2F9)
		STA TrsrGoldLB		  ;($E2FB)Base gold amount of treasure is 5.
		LDA #$00				;($E2FD)
		STA TrsrGoldUB		  ;($E2FF)

		BEQ GetTrsrGold		 ;($E301)($E365)Calculate treasure gold received.

;----------------------------------------------------------------------------------------------------

ChkTrsrGold2:
		CMP #TRSR_GLD2		  ;($E303)Did player just get a treasure chest with gold 2 treasure?
		BNE ChkTrsrGold3		;($E305)If not, branch to check for gold 3 treasure.

		LDA #$07				;($E307)Max 7 gold randomly added to treasure.
		STA RndGoldBits		 ;($E309)

		LDA #$06				;($E30B)
		STA TrsrGoldLB		  ;($E30D)Base gold amount of treasure is 6.
		LDA #$00				;($E30F)
		STA TrsrGoldUB		  ;($E311)

		BEQ GetTrsrGold		 ;($E313)($E365)Calculate treasure gold received.

;----------------------------------------------------------------------------------------------------

ChkTrsrGold3:
		CMP #TRSR_GLD3		  ;($E315)Did player just get a treasure chest with gold 3 treasure?
		BNE ChkTrsrGold4		;($E317)If not, branch to check for gold 4 treasure.

		LDA #$07				;($E319)Max 7 gold randomly added to treasure.
		STA RndGoldBits		 ;($E31B)

		LDA #$0A				;($E31D)
		STA TrsrGoldLB		  ;($E31F)Base gold amount of treasure is 10.
		LDA #$00				;($E321)
		STA TrsrGoldUB		  ;($E323)

		BEQ GetTrsrGold		 ;($E325)($E365)Calculate treasure gold received.

;----------------------------------------------------------------------------------------------------

ChkTrsrGold4:
		CMP #TRSR_GLD4		  ;($E327)Did player just get a treasure chest with gold 4 treasure?
		BNE ChkTrsrGold5		;($E329)If not, branch to check for gold 5 treasure.

		LDA #$FF				;($E32B)Max 255 gold randomly added to treasure.
		STA RndGoldBits		 ;($E32D)

		LDA #$F4				;($E32F)
		STA TrsrGoldLB		  ;($E331)Base gold amount of treasure is 500.
		LDA #$01				;($E333)
		STA TrsrGoldUB		  ;($E335)

		BNE GetTrsrGold		 ;($E337)($E365)Calculate treasure gold received.

;----------------------------------------------------------------------------------------------------

ChkTrsrGold5:
		CMP #TRSR_GLD5		  ;($E339)Did player just get a treasure chest with gold 5 treasure?
		BNE ChkTrsrErdTablet	;($E33B)If not, branch to get Erdrick's tablet(only remianing treasure).

		LDA #$00				;($E33D)No random amount added to treasure.
		STA RndGoldBits		 ;($E33F)

		STA TrsrGoldUB		  ;($E341)
		LDA #$78				;($E343)Base gold amount of treasure is 120.
		STA TrsrGoldLB		  ;($E345)

		BNE GetTrsrGold		 ;($E347)($E365)Calculate treasure gold received.

;----------------------------------------------------------------------------------------------------

ChkTrsrErdTablet:
		JSR GetTreasure		 ;($E349)($E39A)Check for valid treasure and get it.

		LDX #$00				;($E34C)Only thing left is Erdrick's tablet.
		* LDA ErdrkTabletTbl,X  ;($E34E)
		STA DescBuf,X		   ;($E351)Get description bytes from table below.
		INX					 ;($E353)
		CPX #$02				;($E354)Got second byte?
		BNE -				   ;($E356)If not, branch to get it.

		JSR DoDialogLoBlock	 ;($E358)($C7CB)TextBlock14, entry 9.
		.byte $D9			   ;($E35B)Fortune smiles upon thee. Thou hast found the item...

		JSR DoDialogHiBlock	 ;($E35C)($C7C5)TextBlock17, entry 3.
		.byte $03			   ;($E35F)The tablet reads as follows...

		JMP ResumeGamePlay	  ;($E360)($CFD9)Give control back to player.

ErdrkTabletTbl:
		.byte $19, $FA		  ;($E363)Description index for Erdrick's tablet.

;----------------------------------------------------------------------------------------------------

GetTrsrGold:
		JSR UpdateRandNum	   ;($E365)($C55B)Get random number.
		LDA RandomNumberUB	  ;($E368)
		AND RndGoldBits		 ;($E36A)Get random anount of gold to add to treasure gold.

		CLC					 ;($E36C)
		ADC TrsrGoldLB		  ;($E36D)
		STA TrsrGoldLB		  ;($E36F)Add the random amount of gold to the treasure gold.
		LDA TrsrGoldUB		  ;($E371)
		ADC #$00				;($E373)
		STA TrsrGoldUB		  ;($E375)
		JSR GetTreasure		 ;($E377)($E39A)Check for valid treasure and get it.

		LDA GoldLB			  ;($E37A)
		CLC					 ;($E37C)
		ADC TrsrGoldLB		  ;($E37D)
		STA GoldLB			  ;($E37F)Add treasure gold to player's gold.
		LDA GoldUB			  ;($E381)
		ADC TrsrGoldUB		  ;($E383)
		STA GoldUB			  ;($E385)Did player's gold overflow?
		BCC GainGoldDialog	  ;($E387)If not, branch to display message and exit.

		LDA #$FF				;($E389)
		STA GoldLB			  ;($E38B)Set player's gold to max(65535).
		STA GoldUB			  ;($E38D)

GainGoldDialog:
		JSR DoDialogLoBlock	 ;($E38F)($C7CB)Of gold thou hast gained...
		.byte $D8			   ;($E392)TextBlock14, entry 8.

		JSR Dowindow			;($E393)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($E396)Pop-up window.

		JMP ResumeGamePlay	  ;($E397)($CFD9)Give control back to player.

;----------------------------------------------------------------------------------------------------

GetTreasure:
		LDX #$00				;($E39A)Start at beginning of treasure table.

ChkTrsrLoop:
		LDA TrsrXPos,X		  ;($E39C)Is treasure slot empty?
		ORA TrsrYPos,X		  ;($E39F)
		BEQ TakeTreasure		;($E3A2)If so, branch to take treasure.

		INX					 ;($E3A4)Move to next spot in treasure table to see if its empty.
		INX					 ;($E3A5)
		CPX #$10				;($E3A6)At the end of the table?
		BNE ChkTrsrLoop		 ;($E3A8)If not, branch to check next entry.
		RTS					 ;($E3AA)Treasure table is full.  Can't get treasure.

TakeTreasure:
		LDA CharXPos			;($E3AB)
		STA TrsrXPos,X		  ;($E3AD)Store player's position in treasure table.
		LDA CharYPos			;($E3B0)This is how the game keeps track of taken treasure.
		STA TrsrYPos,X		  ;($E3B2)

		LDA #$00				;($E3B5)
		STA XPosFromCenter	  ;($E3B7)Remove treasure chest block directly under player.
		STA YPosFromCenter	  ;($E3B9)
		STA BlkRemoveFlgs	   ;($E3BB)Remove all 4 tiles of treasure chest.

		LDA #SFX_TRSR_CHEST	 ;($E3BD)Treasure chest SFX.
		BRK					 ;($E3BF)
		.byte $04, $17		  ;($E3C0)($81A0)InitMusicSFX, bank 1.

		JSR ModMapBlock		 ;($E3C2)($AD66)Change block on map.

		LDA DescTemp			;($E3C5)Load description byte.
		CLC					 ;($E3C7)Add offset to locate item descriptions.
		ADC #$2E				;($E3C8)
		JMP GetDescriptionByte  ;($E3CA)($DBF0)Load byte for item dialog description.

;----------------------------------------------------------------------------------------------------

LoadCombatBckgrnd:
		LDA EnemyNumber		 ;($E3CD)
		CMP #EN_DRAGONLORD2	 ;($E3CF)Is this the final boss?
		BNE +				   ;($E3D1)If so, skip drawing the background.
		RTS					 ;($E3D3)

		* LDX #$00			  ;($E3D4)
		STX BlockClear		  ;($E3D6)Initialize variables.
		STX BlockCounter		;($E3D8)

		LDA #$0A				;($E3DA)
		STA GenPtr3CLB		  ;($E3DC)Buffer combat background graphics in
		LDA #$05				;($E3DE)RAM starting at $050A.
		STA GenPtr3CUB		  ;($E3E0)

BGGFXLoadLoop:
		LDY #$00				;($E3E2)Keeps track of current location in row.

BGLoadRow:
		LDA MapNumber		   ;($E3E4)Is the combat happening on the overworld?
		CMP #MAP_OVERWORLD	  ;($E3E6)
		BEQ +				   ;($E3E8)If so, branch to load outside graphics.

		LDA #TL_BLANK_TILE1	 ;($E3EA)Not on overworld, load black background.
		BNE ++				  ;($E3EC)

		* LDA CombatBckgndGFX,X ;($E3EE)Get background data and load it into RAM.
		* STA (GenPtr3C),Y	  ;($E3F1)

		INX					 ;($E3F3)Increment to next values in data table and RAM.
		INY					 ;($E3F4)

		CPY #$0E				;($E3F5)Have 14 tiles been loaded?
		BNE BGLoadRow		   ;($E3F7)If not, branch to keep loading row.

		LDA GenPtr3CLB		  ;($E3F9)
		CLC					 ;($E3FB)
		ADC #$20				;($E3FC)
		STA GenPtr3CLB		  ;($E3FE)Move to beginning of the next row.
		LDA GenPtr3CUB		  ;($E400)
		ADC #$00				;($E402)
		STA GenPtr3CUB		  ;($E404)

		CPX #$C4				;($E406)Have 194 tiles been loaded (14*14)?
		BNE BGGFXLoadLoop	   ;($E408)If not, branch to load more.

		JSR WaitForNMI		  ;($E40A)($FF74)Wait for VBlank interrupt.
		JSR DoSprites		   ;($E40D)($B6DA)Update player and NPC sprites.

BGGFXScreenLoop:
		LDX BlockCounter		;($E410)Use the block counter as the index into the table.

		LDA CmbtBGPlcmntTbl,X   ;($E412)
		LSR					 ;($E415)Get byte from table and extract
		LSR					 ;($E416)x displacement (upper nibble).
		LSR					 ;($E417)
		LSR					 ;($E418)

		CLC					 ;($E419)Need to convert from combat background coords
		ADC #$FA				;($E41A)to screen tile coords.  The formula is:
		STA XPosFromCenter	  ;($E41C)x = combatBGX + #$0A.
		CLC					 ;($E41E)
		ADC #$10				;($E41F)Here they are basing off the center so they actually use:
		STA XPosFromLeft		;($E421)x = combatBGX + #$10 - #$6.

		LDA CmbtBGPlcmntTbl,X   ;($E423)Get same byte from table and extract
		AND #$0F				;($E426)y displacement (lower nibble).

		CLC					 ;($E428)The y position needs to be converted as well.
		ADC #$FA				;($E429)the formula is:
		STA YPosFromCenter	  ;($E42B)y = combatBGY + #$09.
		CLC					 ;($E42D)
		ADC #$0E				;($E42E)Here they are basing off the center so they actually use:
		STA YPosFromTop		 ;($E430)y = combatBGY + #$0E - #$6.

		JSR CalcRAMBufAddr	  ;($E432)($C59E)Calculate RAM buffer address for block placement.

		LDA PPUBufPtrLB		 ;($E435)
		STA BlockAddrLB		 ;($E437)Save a copy of the block address.
		LDA PPUBufPtrUB		 ;($E439)
		STA BlockAddrUB		 ;($E43B)

		JSR WaitForNMI		  ;($E43D)($FF74)Wait for VBlank interrupt.
		JSR AddBlocksToScreen   ;($E440)($C707)Calculate 4x4 tile addresses and move data to PPU.

		INC BlockCounter		;($E443)Have 49 blocks been placed?
		LDA BlockCounter		;($E445)If not, loop to load more.
		CMP #$31				;($E447)
		BNE BGGFXScreenLoop	 ;($E449)
		JSR WaitForNMI		  ;($E44B)($FF74)Wait for VBlank interrupt.
		RTS					 ;($E44E)

;----------------------------------------------------------------------------------------------------

LoadEnemyGFX:
		LDA EnemyNumber		 ;($E44F)Is this the final boss?
		CMP #EN_DRAGONLORD2	 ;($E451)
		BNE +				   ;($E453)If not branch to load regular enemy graphics.

		LDA #$00				;($E455)Clear enemy number.
		STA EnemyNumber		 ;($E457)

		BRK					 ;($E459)Load the final boss!
		.byte $02, $07		  ;($E45A)($BABD)DoEndFight, bank 0.
		RTS					 ;($E45C)

		* LDA #$00			  ;($E45D)
		STA RAMTrgtPtrLB		;($E45F)
		STA CopyCounterUB	   ;($E461)Copy enemy sprite data into $0300 to $03A0.
		LDA #$03				;($E463)Always copy 160 bytes(53 sprites worth of data).
		STA RAMTrgtPtrUB		;($E465)Not all the data copied may be used.
		LDA #$A0				;($E467)
		STA CopyCounterLB	   ;($E469)

		BRK					 ;($E46B)Copy ROM table into RAM.
		.byte $0A, $17		  ;($E46C)($9981)CopyROMToRAM, bank 1.

		LDX #$10				;($E46E)Index to store enemy sprites. Starts after player sprites.

		LDY #$00				;($E470)
		STY EnSpritePtrLB	   ;($E472)Copy enemy sprite data from base address $0300.
		LDA #$03				;($E474)
		STA EnSpritePtrUB	   ;($E476)

EnSpriteLoop:
		LDA (EnSpritePtr),Y	 ;($E478)Null terminated sprite data. Has end been reached?
		BEQ EnLoadPalData	   ;($E47A)If so, branch to stop loading sprite data.

		STA SpriteRAM+1,X	   ;($E47C)Store tile pattern for sprite.

		INY					 ;($E47F)Move to next sprite byte.

		LDA (EnSpritePtr),Y	 ;($E480)Get the 6 bits of Y position data for the enemy sprite.
		AND #$3F				;($E482)

		CLC					 ;($E484)
		ADC #$44				;($E485)Move the sprite down to the central region of the screen.
		STA SpriteRAM,X		 ;($E487)

		LDA (EnSpritePtr),Y	 ;($E48A)
		AND #$C0				;($E48C)Get the horizontal and vertical mirrioring bits for the sprite.
		STA EnemySpriteAttributeData;($E48E)

		INY					 ;($E490)Move to next sprite byte.

		LDA (EnSpritePtr),Y	 ;($E491)
		AND #$03				;($E493)Get the palette data for the sprite.
		ORA EnemySpriteAttributeData;($E495)
		STA EnemySpriteAttributeData;($E497)

		LDA (EnSpritePtr),Y	 ;($E499)
		LSR					 ;($E49B)Get the X position data of the prite.
		LSR					 ;($E49C)

		SEC					 ;($E49D)Move sprite 28 pixels left. Not sure
		SBC #$1C				;($E49E)why data was formatted this way.
		STA EnemySpriteXPosition;($E4A0)

		LDA IsEnMirrored		;($E4A2)Is the enemy mirrored?
		BEQ SetEnemySpriteAttribute;($E4A4)If not, branch to skip inverting the X position of the sprite.

		LDA EnemySpriteXPosition;($E4A6)
		EOR #$FF				;($E4A8)Enemy is mirrored. 2's compliment the X position of the sprite.
		STA EnemySpriteXPosition;($E4AA)
		INC EnemySpriteXPosition;($E4AC)

		LDA EnemySpriteAttributeData;($E4AE)Since the enemy is mirrored in the X direction, the
		EOR #$40				;($E4B0)horizontal mirroring of the sprite needs to be inverted.
		STA EnemySpriteAttributeData;($E4B2)

SetEnemySpriteAttribute:
		LDA EnemySpriteAttributeData;($E4B4)Store the attribute data for the enemy sprite.
		STA SpriteRAM+2,X	   ;($E4B6)

		LDA EnemySpriteXPosition;($E4B9)
		CLC					 ;($E4BB)Move the sprite to the central region of the screen.
		ADC #$84				;($E4BC)
		STA SpriteRAM+3,X	   ;($E4BE)

		INX					 ;($E4C1)
		INX					 ;($E4C2)Move to next sprite in sprite RAM.
		INX					 ;($E4C3)Each sprite is 4 bytes.
		INX					 ;($E4C4)

		INY					 ;($E4C5)More sprite data to load?
		BNE EnSpriteLoop		;($E4C6)If so, branch to do another enemy sprite.

EnLoadPalData:
		JSR LoadEnPalette	   ;($E4C8)($EEFD)Load enemy palette data.
		JSR Bank3ToNT1		  ;($E4CB)($FCB8)Load data into nametable 1.

		LDA #$00				;($E4CE)
		STA EnemySpriteXPosition;($E4D0)Clear out sprite working variables.
		LDA #$30				;($E4D2)Doesn't appear to have an effect.
		STA EnemySpriteAttributeData;($E4D4)

		JSR PrepSPPalLoad	   ;($E4D6)($C632)Load sprite palette data into PPU buffer.
		JSR PalFadeIn		   ;($E4D9)($C529)Fade in both background and sprite palettes.
		JMP PalFadeIn		   ;($E4DC)($C529)Fade in both background and sprite palettes.

;----------------------------------------------------------------------------------------------------

InitFight:
		STA EnemyNumber		 ;($E4DF)Prepare to point to enemy data table entry.
		STA EnemyDataPointer	;($E4E1)

		CMP #EN_DRAGONLORD2	 ;($E4E3)Is this the final boss?
		BNE +				   ;($E4E5)If not, branch to play enter fight music.

		LDA #MSC_END_BOSS	   ;($E4E7)End boss music.
		BNE LoadFightMusic	  ;($E4E9)Branch always.

		* LDA #MSC_ENTR_FGHT	;($E4EB)Enter fight music.

LoadFightMusic:
		BRK					 ;($E4ED)Start the fight music.
		.byte $04, $17		  ;($E4EE)($81A0)InitMusicSFX, bank 1.

		LDA #$00				;($E4F0)
		STA EnDatPtrUB		  ;($E4F2)
		ASL EnDatPtrLB		  ;($E4F4)
		ROL EnDatPtrUB		  ;($E4F6)
		ASL EnDatPtrLB		  ;($E4F8)Enemy data pointer * 16.
		ROL EnDatPtrUB		  ;($E4FA)Each entry in the table is 16 bytes.
		ASL EnDatPtrLB		  ;($E4FC)
		ROL EnDatPtrUB		  ;($E4FE)
		ASL EnDatPtrLB		  ;($E500)
		ROL EnDatPtrUB		  ;($E502)

		LDA EnemyNumber		 ;($E504)Save a copy of the enemy number.
		PHA					 ;($E506)

		LDA #$00				;($E507)Zero out enemy number.
		STA EnemyNumber		 ;($E509)

		BRK					 ;($E50B)
		.byte $0C, $17		  ;($E50C)($9961)LoadEnemyStats, bank 1.

		PLA					 ;($E50E)
		STA EnemyNumber		 ;($E50F)
		CMP #EN_RDRAGON		 ;($E511)
		BNE +				   ;($E513)
		LDA #$46				;($E515)Load additional description bytes for the red dragon.
		STA Stack			   ;($E517)These bytes do not appear to be used for any enemy.
		LDA #$FA				;($E51A)
		STA Stack+1			 ;($E51C)
		BNE ContInitializeFight ;($E51F)
		* LDA #$FA			  ;($E521)
		STA Stack			   ;($E523)

ContInitializeFight:
		JSR DoSprites		   ;($E526)($B6DA)Update player and NPC sprites.

		LDA PlayerFlags		 ;($E529)
		AND #$0F				;($E52B)Clear combat status flags.
		STA PlayerFlags		 ;($E52D)

		LDA EnemyNumber		 ;($E52F)
		PHA					 ;($E531)Save the enemy number on the stack and
		LDA #$00				;($E532)then clear the EnemyNumber variable.
		STA EnemyNumber		 ;($E534)

		JSR LoadStats		   ;($E536)($F050)Update player attributes.

		PLA					 ;($E539)Restore enemy number data.
		STA EnemyNumber		 ;($E53A)

		ASL					 ;($E53C)*2 Pointer to enemy sprite data is 2 bytes.
		TAY					 ;($E53D)Use Y as index into EnSpritesPtrTbl.

		LDX #$22				;($E53E)Save base address for EnSpritesPtrTbl in GenPtr22.

		BRK					 ;($E540)Table of pointers to enemy sprites.
		.byte $8B, $17		  ;($E541)($99E4)EnSpritesPtrTbl, bank 1.

		LDA #PRG_BANK_1		 ;($E543)Get lower byte of sprite data pointer
		JSR GetBankDataByte	 ;($E545)($FD1C)from PRG bank 1 and store in A.

		CLC					 ;($E548)Add with carry does nothing.
		ADC #$00				;($E549)
		STA ROMSourcePtrLB	  ;($E54B)Store lower byte of enemy sprite data pointer.

		PHP					 ;($E54D)Carry should always be clear.

		INY					 ;($E54E)Increment to next byte in EnSpritesPtrTbl
		LDA #PRG_BANK_1		 ;($E54F)Get upper byte of sprite data pointer
		JSR GetBankDataByte	 ;($E551)($FD1C)from PRG bank 1 and store in A.

		TAY					 ;($E554)Save a copy of upper byte to check enemy mirroring later.

		AND #$7F				;($E555)
		PLP					 ;($E557)Set MSB of upper byte if not already set.
		ADC #$80				;($E558)Carry should always be clear.
		STA ROMSourcePtrUB	  ;($E55A)

		TYA					 ;($E55C)Store enemy mirroring bit on stack.
		PHA					 ;($E55D)

		LDA ROMSourcePtrLB	  ;($E55E)
		STA NotUsed26		   ;($E560)Save a copy of the ROM location of eney sprite data, lower byte.
		PHA					 ;($E562)

		LDA ROMSourcePtrUB	  ;($E563)
		STA NotUsed27		   ;($E565)Save a copy of the ROM location of eney sprite data, upper byte.
		PHA					 ;($E567)

		JSR LoadCombatBckgrnd   ;($E568)($E3CD)Show combat scene background.

		PLA					 ;($E56B)Restore ROM location of eney sprite data, upper byte.
		STA ROMSourcePtrUB	  ;($E56C)

		PLA					 ;($E56E)Restore ROM location of eney sprite data, lower byte.
		STA ROMSourcePtrLB	  ;($E56F)

		PLA					 ;($E571)
		AND #$80				;($E572)Get byte containing mirrored bit and keep only mirroring bit.
		STA IsEnMirrored		;($E574)

		LDA NPCUpdateCounter	;($E576)
		ORA #$80				;($E578)This appears to have no effect and is cleared when fight ends.
		STA NPCUpdateCounter	;($E57A)

		JSR LoadEnemyGFX		;($E57C)($E44F)Display enemy sprites.

		JSR Dowindow			;($E57F)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($E582)Dialog window.

		LDA EnemyNumber		 ;($E583)Is this the end boss?
		CMP #EN_DRAGONLORD2	 ;($E585)
		BNE EnAppearText		;($E587)If not, branch to display standard enemy approaching text.

		JSR DoDialogHiBlock	 ;($E589)($C7C5)The dragonlord reveals his true self...
		.byte $19			   ;($E58C)TextBlock18, entry 9.

		LDA EnBaseHP			;($E58D)Dragonlord's HP is set to a constant value every time.
		BNE SetEnHP			 ;($E590)Branch always.

EnAppearText:
		JSR CopyEnUpperBytes	;($E592)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($E595)($C7CB)An enemy draws near...
		.byte $E2			   ;($E598)TextBlock15, entry 2.

		LDA EnBaseHP			;($E599)Prepare to multiply enemy HP by random number(0 to 255).
		STA MultiplyNumber2LB   ;($E59C)
		JSR UpdateRandNum	   ;($E59E)($C55B)Get random number.

		LDA RandomNumberUB	  ;($E5A1)
		STA MultiplyNumber1LB   ;($E5A3)
		LDA #$00				;($E5A5)Multiply enemy HP by random byte.
		STA MultiplyNumber1UB   ;($E5A7)
		STA MultiplyNumber2UB   ;($E5A9)
		JSR WordMultiply		;($E5AB)($C1C9)Multiply 2 16-bit words.

		LDA MultiplyResultUB	;($E5AE)
		LSR					 ;($E5B0)Take upper byte of result and divide it by 4.
		LSR					 ;($E5B1)
		STA MultiplyResultLB	;($E5B2)

		LDA EnBaseHP			;($E5B4)
		SEC					 ;($E5B7)Subtract resulting upper byte from enemy HP.
		SBC MultiplyResultLB	;($E5B8)

SetEnHP:
		STA EnCurntHP		   ;($E5BA)Store final enemy HP calculation.

		JSR CheckEnRun		  ;($E5BC)($EFB7)Check if enemy is going to run away.
		JSR CalcWhoIsNext	   ;($E5BF)($EEC0)Randomly calculate who attacks next.

		BCS StartPlayerTurn	 ;($E5C2)($E5CE)It's the player's turn to attack.

		JSR CopyEnUpperBytes	;($E5C4)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($E5C7)($C7CB)The enemy attacked before player ready...
		.byte $E4			   ;($E5CA)TextBlock15, entry 4.

		JMP StartEnemyTurn	  ;($E5CB)($EB1B)It's the enemy's turn to attack.

;----------------------------------------------------------------------------------------------------

StartPlayerTurn:
		JSR Dowindow			;($E5CE)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($E5D1)Pop-up window.

		LDA PlayerFlags		 ;($E5D2)Is player asleep?
		BPL ShowCombatCommand   ;($E5D4)If not, branch.

		JSR UpdateRandNumber	;($E5D6)($C55B)Get random number.
		LDA RandomNumberUB	  ;($E5D9)
		LSR					 ;($E5DB)Player is asleep. 50% chance they wake up.
		BCS PlayerAwakes		;($E5DC)Did player wake up? If so, branch.

PlayerAsleepDialog:
		JSR DoDialogHiBlock	 ;($E5DE)($C7C5)Thou art still asleep...
		.byte $07			   ;($E5E1)TextBlock17, entry 7.

		JMP StartEnemyTurn	  ;($E5E2)($EB1B)It's the enemy's turn to attack.

PlayerAwakes:
		LDA PlayerFlags		 ;($E5E5)
		AND #$7F				;($E5E7)Clear player sleeping flag.
		STA PlayerFlags		 ;($E5E9)

		JSR DoDialogHiBlock	 ;($E5EB)($C7C5)Player awakes...
		.byte $08			   ;($E5EE)TextBlock17, entry 8.

ShowCombatCommand:
		JSR DoDialogLoBlock	 ;($E5EF)($C7CB)Command?...
		.byte $E8			   ;($E5F2)TextBlock15, entry 8.

		JSR Dowindow			;($E5F3)($C6F0)display on-screen window.
		.byte WINDOW_CMD_CMB	;($E5F6)Combat command window.

		LDA WindowSelResults	;($E5F7)Is player choosing to attack enemy?
		BEQ PlayerFight		 ;($E5F9)If so, branch.

		JMP CheckPlayerSpell	;($E5FB)($E6B6)Check if player attempted to cast a spell.

;----------------------------------------------------------------------------------------------------

PlayerFight:
		LDA #WINDOW_CMD_CMB	 ;($E5FE)Remove combat window from screen.
		JSR RemoveWindow		;($E600)($A7A2)Remove window from screen.

		LDA #SFX_ATTACK		 ;($E603)Player attack SFX.
		BRK					 ;($E605)
		.byte $04, $17		  ;($E606)($81A0)InitMusicSFX, bank 1.

		JSR DoDialogLoBlock	 ;($E608)($C7CB)Player attacks...
		.byte $E5			   ;($E60B)TextBlock15, entry 5.

		LDA DisplayedAttack	 ;($E60C)
		STA AttackStat		  ;($E60E)Save a copy of the player's attack and enemy's defense.
		LDA EnBaseDef		   ;($E610)
		STA DefenseStat		 ;($E613)

		LDA EnemyNumber		 ;($E615)Is player fighting the dragonlord's first form?
		CMP #EN_DRAGONLORD1	 ;($E617)
		BEQ CheckPlayerMiss	 ;($E619)If so, branch. no excellent moves permitted.

		CMP #EN_DRAGONLORD2	 ;($E61B)Is player fighting the dragonlord's final form?
		BEQ CheckPlayerMiss	 ;($E61D)If so, branch. no excellent moves permitted.

		JSR UpdateRandNum	   ;($E61F)($C55B)Get random number.
		LDA RandomNumberUB	  ;($E622)
		AND #$1F				;($E624)Did player get an excellent move(1/32 chance)?
		BNE CheckPlayerMiss	 ;($E626)If not, branch to see if player missed.

		LDA #SFX_EXCLNT_MOVE	;($E628)Excellent move SFX
		BRK					 ;($E62A)
		.byte $04, $17		  ;($E62B)($81A0)InitMusicSFX, bank 1.

		JSR CopyEnUpperBytes	;($E62D)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogHiBlock	 ;($E630)($C7C5)Excellent move...
		.byte $04			   ;($E633)TextBlock17, entry 4.

		JSR UpdateRandNum	   ;($E634)($C55B)Get random number.
		LDA RandomNumberUB	  ;($E637)
		STA MultiplyNumber1LB   ;($E639)
		LDA DisplayedAttack	 ;($E63B)
		LSR					 ;($E63D)A = DisplayedAttack/2 * rnd(255).
		STA MultiplyNumber2LB   ;($E63E)
		LDA #$00				;($E640)
		STA MultiplyNumber1UB   ;($E642)
		STA MultiplyNumber2UB   ;($E644)
		JSR WordMultiply		;($E646)($C1C9)Multiply 2 16-bit words.

		LDA DisplayedAttack	 ;($E649)Total equation for excellent move damage:
		SEC					 ;($E64B)Damage=DisplayedAttack-(DisplayedAttack/2 * rnd(255))/256.
		SBC MultiplyResultUB	;($E64C)
		JMP SetEnDmg1		   ;($E64E)($E664)Set the amount of damage player did to the enemy.

CheckPlayerMiss:
		JSR PlayerCalcHitDmg	;($E651)($EFE5)Calculate the damage player will do to the enemy.
		LDA CalcDamage		  ;($E654)Did player do damage to the enemy?
		BNE SetEnDmg1		   ;($E656)If so, branch.

		LDA #SFX_MISSED1		;($E658)Player missed 1 SFX.
		BRK					 ;($E65A)
		.byte $04, $17		  ;($E65B)($81A0)InitMusicSFX, bank 1.

		JSR DoDialogLoBlock	 ;($E65D)($C7CB)The attack failed...
		.byte $E7			   ;($E660)TextBlock15, entry 7.

		JMP StartEnemyTurn	  ;($E661)($EB1B)It's the enemy's turn to attack.

SetEnDmg1:
		STA EnDamage			;($E664)
		LDA #$00				;($E666)Set the damage the player will do if enemy does not dodge.
		STA DmgNotUsed		  ;($E668)

		BIT PlayerFlags		 ;($E66A)Is the enemy asleep?
		BVS PlayerHitEn		 ;($E66C)If so, branch. Enemy can't dodge.

		JSR UpdateRandNum	   ;($E66E)($C55B)Get random number.

		LDA RandomNumberUB	  ;($E671)
		AND #$3F				;($E673)Get a random number and keep lower 6 bits(0-63).
		STA RandomNumberUB	  ;($E675)

		LDA EnBaseMDef		  ;($E677)Does enemy have magic defense?
		AND #$0F				;($E67A)
		BEQ PlayerHitEn		 ;($E67C)If not, branch. Enemy can't dodge.

		SEC					 ;($E67E)Magic defense will be 0-14.
		SBC #$01				;($E67F)If random number is equal or greater than this, player will hit.
		CMP RandomNumberUB	  ;($E681)
		BCC PlayerHitEn		 ;($E683)22% chance enemy will dodge(14/63).

		JSR CopyEnUpperBytes	;($E685)($DBE4)Copy enemy upper bytes to description RAM.

		LDA #SFX_MISSED1		;($E688)Player missed 1 SFX.
		BRK					 ;($E68A)
		.byte $04, $17		  ;($E68B)($81A0)InitMusicSFX, bank 1.

		JSR DoDialogHiBlock	 ;($E68D)($C7C5)It is dodging!...
		.byte $0A			   ;($E690)TextBlock17, entry 10.

		JMP StartEnemyTurn	  ;($E691)($EB1B)It's the enemy's turn to attack.

SetSpellDmg:
		STA EnDamage			;($E694)
		LDA #$00				;($E696)Set the damage the player will do. Enemy can't dodge spells.
		STA DmgNotUsed		  ;($E698)

PlayerHitEn:
		LDA #SFX_ENMY_HIT	   ;($E69A)Enemy hit SFX.
		BRK					 ;($E69C)
		.byte $04, $17		  ;($E69D)($81A0)InitMusicSFX, bank 1.

		LDA RedFlashPalPtr	  ;($E69F)
		STA GenPtr42LB		  ;($E6A2)Save a pointer to the red flash palette.
		LDA RedFlashPalPtr+1	;($E6A4)
		STA GenPtr42UB		  ;($E6A7)

		JSR PaletteFlash		;($E6A9)($EF38)Palette flashing effect.
		JSR CopyEnUpperBytes	;($E6AC)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($E6AF)($C7CB)The enemy's HP has been reduced...
		.byte $E6			   ;($E6B2)TextBlock15, entry 6.

		JMP UpdateEnHP		  ;($E6B3)($E95D)Subtract damage from enemy HP.

;----------------------------------------------------------------------------------------------------

CheckPlayerSpell:
		CMP #CC_SPELL		   ;($E6B6)Did player try to cast a spell?
		BEQ PlayerSpell		 ;($E6B8)If so, branch.

		JMP CheckPlayerItem	 ;($E6BA)($E7A2)Check if player is trying to use an item.

PlayerSpell:
		LDA SpellFlags		  ;($E6BD)
		STA SpellFlagsLB		;($E6BF)
		LDA ModsnSpells		 ;($E6C1)
		AND #$03				;($E6C3)Does player have any spells yet?
		STA SpellFlagsUB		;($E6C5)If so, branch to show available spells.
		ORA SpellFlagsLB		;($E6C7)
		BNE ShowSpellWnd		;($E6C9)

		LDA #WINDOW_CMD_CMB	 ;($E6CB)Remove command window.
		JSR RemoveWindow		;($E6CD)($A7A2)Remove window from screen.

		JSR DoDialogLoBlock	 ;($E6D0)($C7CB)Player cannot yet use the spell.
		.byte $31			   ;($E6D3)TextBlock4, entry 1.

		JMP StartPlayerTurn	 ;($E6D4)($E5CE)It's the player's turn to attack.

ShowSpellWnd:
		JSR ShowSpells		  ;($E6D7)($DB56)Bring up the spell window.
		CMP #WINDOW_ABORT	   ;($E6DA)Did player abort spell?
		BNE PlayerSpellChosen   ;($E6DC)If not, branch.

		LDA #WINDOW_CMD_CMB	 ;($E6DE)Remove command window from the screen.
		JSR RemoveWindow		;($E6E0)($A7A2)Remove window from screen.
		JMP StartPlayerTurn	 ;($E6E3)($E5CE)It's the player's turn to attack.

PlayerSpellChosen:
		PHA					 ;($E6E6)Save a copy of the spell chosen on the stack.

		LDA #WINDOW_CMD_CMB	 ;($E6E7)Remove the command window from the screen.
		JSR RemoveWindow		;($E6E9)($A7A2)Remove window from screen.

		PLA					 ;($E6EC)Restore the spell chosen from the stack.

		CMP #SPL_RADIANT		;($E6ED)Did player cast radiant?
		BEQ InvalidCombatSpell  ;($E6EF)If so, branch. Invalid combat spell.

		CMP #SPL_REPEL		  ;($E6F1)Did player cast repel?
		BEQ InvalidCombatSpell  ;($E6F3)If so, branch. Invalid combat spell.

		CMP #SPL_OUTSIDE		;($E6F5)Did player cast outside?
		BEQ InvalidCombatSpell  ;($E6F7)If so, branch. Invalid combat spell.

		CMP #SPL_RETURN		 ;($E6F9)Did player cast return?
		BNE ValidCombatSpell	;($E6FB)If not, branch. Remaining spells are valid.

InvalidCombatSpell:
		JSR DoDialogLoBlock	 ;($E6FD)($C7CB)That cannot be used in battle...
		.byte $E9			   ;($E700)TextBlock15, entry 9.

		JMP StartPlayerTurn	 ;($E701)($E5CE)It's the player's turn to attack.

ValidCombatSpell:
		JSR CheckMP			 ;($E704)($DB85)Check if MP is high enough to cast the spell.
		CMP #$32				;($E707)TextBlock4, entry 2.
		BNE +				   ;($E709)
		JSR DoMidDialog		 ;($E70B)($C7BD)Thy MP is too low...
		JMP StartPlayerTurn	 ;($E70E)($E5CE)It's the player's turn to attack.

		* STA SpellToCast	   ;($E711)Has stop spell been cast on player?
		LDA PlayerFlags		 ;($E713)
		AND #F_PLR_STOPSPEL	 ;($E715)
		BEQ PlayerPrepareSpell  ;($E717)If not, branch.

		JSR DoDialogLoBlock	 ;($E719)($C7CB)But that spell hath been blocked...
		.byte $EA			   ;($E71C)TextBlock15, entry 10.

		JMP StartEnemyTurn	  ;($E71D)($EB1B)It's the enemy's turn to attack.

PlayerPrepareSpell:
		LDA SpellToCast		 ;($E720)Get cast spell.

		CMP #SPL_HEAL		   ;($E722)Was the heal spell cast?
		BNE +				   ;($E724)If not, branch to move on.

		JSR DoHeal			  ;($E726)($DBB8)Increase HP from heal spell.
		JMP StartEnemyTurn	  ;($E729)($EB1B)It's the enemy's turn to attack.

		* CMP #SPL_HEALMORE	 ;($E72C)Was the healmore spell cast?
		BNE +				   ;($E72E)If not, branch to move on.

		JSR DoHealmore		  ;($E730)($DBD7)Increase health from healmore spell.
		JMP StartEnemyTurn	  ;($E733)($EB1B)It's the enemy's turn to attack.

		* CMP #SPL_HURT		 ;($E736)Was the hurt spell cast?
		BNE +				   ;($E738)If not, branch to move on.

		LDA EnBaseMDef		  ;($E73A)
		LSR					 ;($E73D)
		LSR					 ;($E73E)Get the enemy's magical defense and divide by 16.
		LSR					 ;($E73F)
		LSR					 ;($E740)

		JSR ChkSpellFail		;($E741)($E946)Check if the spell will fail or succeed.
		JSR UpdateRandNum	   ;($E744)($C55B)Get random number.

		LDA RandomNumberUB	  ;($E747)
		AND #$07				;($E749)Hurt will do between 5 and 12 damage.
		CLC					 ;($E74B)
		ADC #$05				;($E74C)

		JMP SetSpellDmg		 ;($E74E)($E694)Set damage enemy will take.

		* CMP #SPL_HURTMORE	 ;($E751)Was the hurtmore spell cast?
		BNE +				   ;($E753)If not, branch to move on.

		LDA EnBaseMDef		  ;($E755)
		LSR					 ;($E758)
		LSR					 ;($E759)Get the enemy's magical defense and divide by 16.
		LSR					 ;($E75A)
		LSR					 ;($E75B)

		JSR ChkSpellFail		;($E75C)($E946)Check if the spell will fail or succeed.
		JSR UpdateRandNum	   ;($E75F)($C55B)Get random number.

		LDA RandomNumberUB	  ;($E762)
		AND #$07				;($E764)Hurtmore will do between 58 and 65 damage.
		CLC					 ;($E766)
		ADC #$3A				;($E767)

		JMP SetSpellDmg		 ;($E769)($E694)Set damage enemy will take.

		* CMP #SPL_SLEEP		;($E76C)Was the sleep spell cast?
		BNE +				   ;($E76E)

		LDA EnBaseAgi		   ;($E770)
		LSR					 ;($E773)
		LSR					 ;($E774)Get the enemy's magical defense and divide by 16.
		LSR					 ;($E775)
		LSR					 ;($E776)

		JSR ChkSpellFail		;($E777)($E946)Check if the spell will fail or succeed.
		JSR CopyEnUpperBytes	;($E77A)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($E77D)($C7CB)Thou hast put the enemy to sleep...
		.byte $EC			   ;($E780)TextBlock15, entry 12.

		LDA PlayerFlags		 ;($E781)Set flag indicating the enemy is asleep.
		ORA #F_EN_ASLEEP		;($E783)
		STA PlayerFlags		 ;($E785)
		JMP EnStillAsleep	   ;($E787)($EB3E)Indicate enemy is asleep.

		* LDA EnBaseAgi		 ;($E78A)The only spell left is stopspell.
		AND #$0F				;($E78D)Get the enemy's agility and keep the 4 MSBs(0-15).
		JSR ChkSpellFail		;($E78F)($E946)Check if the spell will fail or succeed.

		JSR CopyEnUpperBytes	;($E792)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($E795)($C7CB)The enemy's spell hath been blocked...
		.byte $ED			   ;($E798)TextBlock15, entry 13.

		LDA PlayerFlags		 ;($E799)Set flag indicating the enemy has been stopspelled.
		ORA #F_EN_STOPSPEL	  ;($E79B)
		STA PlayerFlags		 ;($E79D)
		JMP StartEnemyTurn	  ;($E79F)($EB1B)It's the enemy's turn to attack.

;----------------------------------------------------------------------------------------------------

CheckPlayerItem:
		CMP #CC_ITEM			;($E7A2)Is player trying to use an item?
		BEQ PlayerItem		  ;($E7A4)If so, branch.

		JMP CheckPlayerRun	  ;($E7A6)($E87F)Check if player is trying to run.

PlayerItem:
		JSR CreateInvList	   ;($E7A9)($DF77)Create inventory list in description buffer.

		CPX #INV_NONE		   ;($E7AC)Does the player have any inventory?
		BNE PlayerShowInv	   ;($E7AE)If so, branch to show inventory window.

		LDA #WINDOW_CMD_CMB	 ;($E7B0)Remove command window.
		JSR RemoveWindow		;($E7B2)($A7A2)Remove window from screen.

		JSR DoDialogLoBlock	 ;($E7B5)($C7CB)Nothing of use has yet been given to thee...
		.byte $3D			   ;($E7B8)TextBlock4, entry 13.

		JMP StartPlayerTurn	 ;($E7B9)($E5CE)It's the player's turn to attack.

PlayerShowInv:
		JSR Dowindow			;($E7BC)($C6F0)display on-screen window.
		.byte WND_INVTRY1	   ;($E7BF)Player inventory window.

		CMP #WINDOW_ABORT	   ;($E7C0)Did player abort the item window?
		BNE ChkCmbtItemUsed	 ;($E7C2)If not, branch to figure out which item player used.

		LDA #WINDOW_CMD_CMB	 ;($E7C4)Remove command window from the screen.
		JSR RemoveWindow		;($E7C6)($A7A2)Remove window from screen.
		JMP StartPlayerTurn	 ;($E7C9)($E5CE)It's the player's turn to attack.

ChkCmbtItemUsed:
		PHA					 ;($E7CC)Store copy of item used.

		LDA #WINDOW_CMD_CMB	 ;($E7CD)Remove command window.
		JSR RemoveWindow		;($E7CF)($A7A2)Remove window from screen.

		PLA					 ;($E7D2)Restore item used.

		TAX					 ;($E7D3)Get description of item used.
		LDA DescBuf+1,X		 ;($E7D4)

		CMP #INV_HERB		   ;($E7D6)Did player use an herb?
		BNE ChkUseFlute		 ;($E7D8)If not, branch to check next item.

		DEC InventoryHerbs	  ;($E7DA)Remove 1 herb from player's inventory.

		JSR DoDialogLoBlock	 ;($E7DC)($C7CB)Player used the herb...
		.byte $F7			   ;($E7DF)TextBlock16, entry 7.

		JSR HerbHeal			;($E7E0)($DCFE)Heal player from an herb.
		JMP StartEnemyTurn	  ;($E7E3)($EB1B)It's the enemy's turn to attack.

ChkUseFlute:
		CMP #INV_FLUTE		  ;($E7E6)Did player use the flute?
		BNE ChkUseHarp		  ;($E7E8)If not, branch to check next item.

		JSR DoDialogLoBlock	 ;($E7EA)($C7CB)Player blew the fairie's flute...
		.byte $3C			   ;($E7ED)TextBlock4, entry 12.

		LDA #MSC_FRY_FLUTE	  ;($E7EE)Fairy flute music.
		BRK					 ;($E7F0)
		.byte $04, $17		  ;($E7F1)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($E7F3)Wait for the music clip to end.
		.byte $03, $17		  ;($E7F4)($815E)WaitForMusicEnd, bank 1.

		LDA EnemyNumber		 ;($E7F6)Restart fight music.
		CMP #EN_DRAGONLORD2	 ;($E7F8)Is player fighting the end boss?
		BEQ PlayEndBossMusic1   ;($E7FA)If so, branch to restart end boss music.

		LDA #MSC_REG_FGHT	   ;($E7FC)Regular fight music.
		JMP +				   ;($E7FE)

PlayEndBossMusic1:
		LDA #MSC_END_BOSS	   ;($E801)End boss music.

		* BRK				   ;($E803)
		.byte $04, $17		  ;($E804)($81A0)InitMusicSFX, bank 1.

		LDA EnemyNumber		 ;($E806)Is player fighting the golem?
		CMP #EN_GOLEM		   ;($E808)
		BNE FluteFail		   ;($E80A)If not, branch. Flute has no effect.

		JSR DoDialogLoBlock	 ;($E80C)($C7CB)Quietly golem closes his eyes...
		.byte $F3			   ;($E80F)TextBlock16, entry 3.

		LDA PlayerFlags		 ;($E810)Set flag indicating golem is asleep.
		ORA #F_EN_ASLEEP		;($E812)
		STA PlayerFlags		 ;($E814)
		JMP EnStillAsleep	   ;($E816)($EB3E)Indicate enemy is asleep.

FluteFail:
		JSR DoDialogLoBlock	 ;($E819)($C7CB)But nothing happened...
		.byte $33			   ;($E81C)TextBlock4, entry 3.

		JMP StartEnemyTurn	  ;($E81D)($EB1B)It's the enemy's turn to attack.

ChkUseHarp:
		CMP #INV_HARP		   ;($E820)Did player use the harp?
		BNE ChkUseScale		 ;($E822)If not, branch.

		JSR DoDialogLoBlock	 ;($E824)($C7CB)Player played sweet melody on the harp...
		.byte $41			   ;($E827)TextBlock5, entry 1.

		LDA #MSC_SILV_HARP	  ;($E828)Silver harp music.
		BRK					 ;($E829)
		.byte $04, $17		  ;($E82B)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($E82D)Wait for the music clip to end.
		.byte $03, $17		  ;($E82E)($815E)WaitForMusicEnd, bank 1.

		LDA EnemyNumber		 ;($E830)Is the player fighting the end boss?
		CMP #EN_DRAGONLORD2	 ;($E832)
		BEQ PlayEndBossMusic2   ;($E834)If so, branch to restart end boss music.

		LDA #MSC_REG_FGHT	   ;($E836)Restart regular fight music.
		JMP +				   ;($E838)

PlayEndBossMusic2:
		LDA #MSC_END_BOSS	   ;($E83B)End boss music.

		* BRK				   ;($E83D)
		.byte $04, $17		  ;($E83E)($81A0)InitMusicSFX, bank 1.

		JSR CopyEnUpperBytes	;($E840)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($E843)($C7CB)Enemy looks happy...
		.byte $F4			   ;($E846)TextBlock16, entry 4.

		JMP StartEnemyTurn	  ;($E847)($EB1B)It's the enemy's turn to attack.

ChkUseScale:
		CMP #INV_SCALE		  ;($E84A)Did player use the dragon's scale?
		BNE ChkUseRing		  ;($E84C)If not, branch.

		JSR ChkDragonScale	  ;($E84E)($DFB9)Check if player is wearing the dragon's scale.
		JMP StartEnemyTurn	  ;($E851)($EB1B)It's the enemy's turn to attack.

ChkUseRing:
		CMP #INV_RING		   ;($E854)Did player use the fighter's ring?
		BNE ChkUseBelt		  ;($E856)If not, branch.

		JSR ChkRing			 ;($E858)($DFD1)Check if player is wearing the ring.
		JMP StartEnemyTurn	  ;($E85B)($EB1B)It's the enemy's turn to attack.

ChkUseBelt:
		CMP #INV_BELT		   ;($E85E)Did player use the cursed belt?
		BNE ChkUseNecklace	  ;($E860)If not, branch.

		JSR WearCursedItem	  ;($E862)($DFE7)Player puts on cursed item.

		LDA #MSC_REG_FGHT	   ;($E865)Regular fight music.
		BRK					 ;($E867)
		.byte $04, $17		  ;($E868)($81A0)InitMusicSFX, bank 1.

		JMP StartEnemyTurn	  ;($E86A)($EB1B)It's the enemy's turn to attack.

ChkUseNecklace:
		CMP #INV_NECKLACE	   ;($E86D)Did player use the death necklace?
		BNE UseInvalidItem	  ;($E86F)If not, branch. No more items can be used in battle.

		JSR ChkDeathNecklace	;($E871)($E00A)Check if player is wearking the death necklace.

		LDA #MSC_REG_FGHT	   ;($E874)Regular fight music.
		BRK					 ;($E876)
		.byte $04, $17		  ;($E877)($81A0)InitMusicSFX, bank 1.

		JMP StartEnemyTurn	  ;($E879)($EB1B)It's the enemy's turn to attack.

UseInvalidItem:
		JMP InvalidCombatSpell  ;($E87C)($E6FD)Tell player item cannot be used in combat.

;----------------------------------------------------------------------------------------------------

CheckPlayerRun:
		CMP #CC_RUN			 ;($E87F)Did player try to run?
		BEQ PlayerRun		   ;($E881)If so, branch.

		JMP ShowCombatCommand   ;($E883)($E5EF)Show command dialog.

PlayerRun:
		LDA #WINDOW_CMD_CMB	 ;($E886)Remove the command window from the screen.
		JSR RemoveWindow		;($E888)($A7A2)Remove window from screen.

		LDA #SFX_RUN			;($E88B)Run away SFX.
		BRK					 ;($E88D)
		.byte $04, $17		  ;($E88E)($81A0)InitMusicSFX, bank 1.

		JSR DoDialogLoBlock	 ;($E890)($C7CB)Player started to run away...
		.byte $F5			   ;($E893)TextBlock16, entry 5.

		BIT PlayerFlags		 ;($E894)Is the enemy asleep?
		BVS RunSuccessful	   ;($E896)If so, branch for a successful run.

		JSR TryRun			  ;($E898)($EE91)Determine if player can run.
		BCS RunSuccessful	   ;($E89B)Was player able to run? If so, branch.

		JSR DoDialogLoBlock	 ;($E89D)($C7CB)But was blocked in front...
		.byte $F6			   ;($E8A0)TextBlock16, entry 6.

		JMP StartEnemyTurn	  ;($E8A1)($EB1B)It's the enemy's turn to attack.

RunSuccessful:
		LDX MapNumber		   ;($E8A4)Get current map number.
		LDA ResumeMusicTbl,X	;($E8A6)Use current map number to resume music.
		BRK					 ;($E8A9)
		.byte $04, $17		  ;($E8AA)($81A0)InitMusicSFX, bank 1.

		LDA EnemyNumber		 ;($E8AC)Was player fighting the end boss?
		CMP #EN_DRAGONLORD2	 ;($E8AE)
		BNE ChkMapHauksness	 ;($E8B0)If not, branch.

		JSR WaitForNMI		  ;($E8B2)($FF74)Wait for VBlank interrupt.

		LDA BlackPalPtr		 ;($E8B5)
		STA PalettePointerLB	;($E8B8)Prepare to load the black palette.
		LDA BlackPalPtr+1	   ;($E8BA)
		STA PalettePointerUB	;($E8BD)

		LDA #$00				;($E8BF)
		STA PalModByte		  ;($E8C1)Disable fande-in/fade-out.
		STA EnemyNumber		 ;($E8C3)

		JSR PrepSPPalLoad	   ;($E8C5)($C632)Load sprite palette data into PPU buffer.
		JSR PrepBGPalLoad	   ;($E8C8)($C63D)Load background palette data into PPU buffer
		JSR WaitForNMI		  ;($E8CB)($FF74)Wait for VBlank interrupt.
		JSR ClearWinBufRAM2	 ;($E8CE)($A788)Clear RAM buffer used for drawing text windows.
		JMP MapChngNoSound	  ;($E8D1)($B091)Change maps with no stairs sound.

ChkMapHauksness:
		LDA MapNumber		   ;($E8D4)Is player in Hauksness?
		CMP #MAP_HAUKSNESS	  ;($E8D6)
		BNE ChkMapSwampCave	 ;($E8D8)If not, branch to check other maps.

		LDA CharXPos			;($E8DA)
		CMP #$12				;($E8DC)
		BNE ChkMapSwampCave	 ;($E8DE)Was the player fighting the fixed axe knight fight?
		LDA CharYPos			;($E8E0)
		CMP #$0C				;($E8E2)
		BNE ChkMapSwampCave	 ;($E8E4)If not, branch to move on.

		JSR ClearSpriteRAM	  ;($E8E6)($C6BB)Clear sprite RAM.

		DEC CharXPos			;($E8E9)Move player 1 block left so they cannot search
		DEC _CharXPos		   ;($E8EB)for Erdrick's armor after running.

		LDA CharXPixelsLB	   ;($E8ED)
		SEC					 ;($E8EF)
		SBC #$10				;($E8F0)Move player's X pixel position 1 block to the left.
		STA CharXPixelsLB	   ;($E8F2)
		BCS +				   ;($E8F4)
		DEC CharXPixelsUB	   ;($E8F6)
		* JMP MapChngWithSound  ;($E8F8)($B097)Change maps with stairs sound.

ChkMapSwampCave:
		LDA MapNumber		   ;($E8FB)Is player in the swamp cave?
		CMP #MAP_SWAMPCAVE	  ;($E8FD)
		BNE ChkMapOverworld	 ;($E8FF)If not, branch to check other maps.

		LDA CharXPos			;($E901)
		CMP #$04				;($E903)
		BNE ChkMapOverworld	 ;($E905)Was player fighting the fixed green dragon fight?
		LDA CharYPos			;($E907)
		CMP #$0E				;($E909)
		BNE ChkMapOverworld	 ;($E90B)If not, branch to move on.

		LDA StoryFlags		  ;($E90D)Has player already killed the green dragon?
		AND #F_GDRG_DEAD		;($E90F)
		BNE ChkMapOverworld	 ;($E911)If so, branch.

MovePlyrUp1Block:
		JSR ClearSpriteRAM	  ;($E913)($C6BB)Clear sprite RAM.

		DEC CharYPos			;($E916)Move player 1 block up so they cannot bypass
		DEC _CharYPos		   ;($E918)the green dragon fight and save Gwaelin after running.

		LDA CharYPixelsLB	   ;($E91A)
		SEC					 ;($E91C)
		SBC #$10				;($E91D)Move player's Y pixel position 1 block up.
		STA CharYPixelsLB	   ;($E91F)
		BCS +				   ;($E921)
		DEC CharYPixelsUB	   ;($E923)
		* JMP MapChngWithSound  ;($E925)($B097)Change maps with stairs sound.

ChkMapOverworld:
		LDA MapNumber		   ;($E928)Is player on the overworld map?
		CMP #MAP_OVERWORLD	  ;($E92A)
		BNE ChkMapsDone		 ;($E92C)If not, branch to end checks for special map locations.

		LDA CharXPos			;($E92E)
		CMP #$49				;($E930)
		BNE ChkMapsDone		 ;($E932)Is player running from the golem fight?
		LDA CharYPos			;($E934)
		CMP #$64				;($E936)
		BNE ChkMapsDone		 ;($E938)If not, branch to end special map checks.

		LDA StoryFlags		  ;($E93A)Has player already killed golem?
		AND #F_GOLEM_DEAD	   ;($E93C)
		BEQ MovePlyrUp1Block	;($E93E)If not, branch. Move player so they cannot enter town on run.

ChkMapsDone:
		JSR ClearSpriteRAM	  ;($E940)($C6BB)Clear sprite RAM.
		JMP ExitFight2		  ;($E943)($EE5A)Exit the combat engine.

;----------------------------------------------------------------------------------------------------

ChkSpellFail:
		STA GenByte3E		   ;($E946)Store spell test byte.
		JSR UpdateRandNum	   ;($E948)($C55B)Get random number.

		LDA RandomNumberUB	  ;($E94B)Get 4 bits from the random number(0-15).
		AND #$0F				;($E94D)

		CMP GenByte3E		   ;($E94F)Is the spell test byte greater than the random number?
		BCC SpellFailed		 ;($E951)If so, branch. The spell failed.

		RTS					 ;($E953)Spell succeeded. Return.

SpellFailed:
		PLA					 ;($E954)Spell failed. Remove return address from
		PLA					 ;($E955)stack and start enemy's turn.

		JSR DoDialogLoBlock	 ;($E956)($C7CB)The spell will not work...
		.byte $EB			   ;($E959)TextBlock15, entry 11.

		JMP StartEnemyTurn	  ;($E95A)($EB1B)It's the enemy's turn to attack.

;----------------------------------------------------------------------------------------------------

UpdateEnHP:
		LDA EnCurntHP		   ;($E95D)
		SEC					 ;($E95F)Subtract damage caused by player from the enemy HP.
		SBC EnDamage			;($E960)
		STA EnCurntHP		   ;($E962)

		BCC EnemyDefeated	   ;($E964)($E96B)Enemy overkill! Branch to end fight.
		BEQ EnemyDefeated	   ;($E966)($E96B)Enemy dead! Branch to end fight.
		JMP StartEnemyTurn	  ;($E968)($EB1B)It's the enemy's turn to attack.

;----------------------------------------------------------------------------------------------------

EnemyDefeated:
		LDA EnemyNumber		 ;($E96B)Check what enemy was just killed.
		CMP #EN_GDRAGON		 ;($E96D)Was it a green dragon?
		BNE ChkGolemKilled	  ;($E96F)If not, move on.

		LDA MapNumber		   ;($E971)Green dragon just killed.
		CMP #MAP_SWAMPCAVE	  ;($E973)Was it in the swamp cave?
		BNE ChkGolemKilled	  ;($E975)If not, move on.

		LDA StoryFlags		  ;($E977)Green dragon in the swamp cave
		ORA #F_GDRG_DEAD		;($E979)was defeated.  Set story flag.
		STA StoryFlags		  ;($E97B)
		BNE ContEnDefeated	  ;($E97D)Branch always.

ChkGolemKilled:
		CMP #EN_GOLEM		   ;($E97F)Was it a golem?
		BNE ContEnDefeated	  ;($E981)If not, move on.

		LDA MapNumber		   ;($E983)Golem just killed.
		CMP #MAP_OVERWORLD	  ;($E985)Was it on the overworld map?
		BNE ContEnDefeated	  ;($E987)If not, move on.

		LDA StoryFlags		  ;($E989)Golem on the overworld was
		ORA #F_GOLEM_DEAD	   ;($E98B)defeated.  Set story flag.
		STA StoryFlags		  ;($E98D)

ContEnDefeated:
		JSR CopyEnUpperBytes	;($E98F)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($E992)($C7CB)Thy experience increased by amount...
		.byte $EE			   ;($E995)TextBlock15, entry 14.

		JSR ClearSpriteRAM	  ;($E996)($C6BB)Clear sprite RAM.

		LDA #MSC_VICTORY		;($E999)Victory music.
		BRK					 ;($E99B)
		.byte $04, $17		  ;($E99C)($81A0)InitMusicSFX, bank 1.

		LDA EnemyNumber		 ;($E99E)Was it the first dragonlord that was defeated?
		CMP #EN_DRAGONLORD1	 ;($E9A0)
		BNE NotDL1Defeated	  ;($E9A2)If not, branch to move on.

		LDX #$50				;($E9A4)Wait for 80 frames.
		* JSR WaitForNMI		;($E9A6)($FF74)Wait for VBlank interrupt.
		DEX					 ;($E9A9)
		BNE -				   ;($E9AA)80 frames elapsed? If not, branch to wait more.

		LDA #EN_DRAGONLORD2	 ;($E9AC)Fight the final boss!
		JMP InitFight		   ;($E9AE)($E4DF)Load the final fight.

NotDL1Defeated:
		CMP #EN_DRAGONLORD2	 ;($E9B1)Was it the end boss that was defeated?
		BNE RegEnDefeated	   ;($E9B3)If not, branch.

		STA DrgnLrdPal		  ;($E9B5)Indicate the final boss was just defeated.

		LDA #DIR_DOWN		   ;($E9B8)Player will be facing down when map is loaded.
		STA CharDirection	   ;($E9BA)

		LDA #$2C				;($E9BD)Prepare to erase the background blocks of the end boss.
		STA PPUAddrLB		   ;($E9BF)
		LDA #$21				;($E9C1)The starting address is $212C on nametable 0.
		STA PPUAddrUB		   ;($E9C3)

		LDA #TL_BLANK_TILE1	 ;($E9C5)Load a blank block as the replacement tile.
		STA PPUDataByte		 ;($E9C7)

		LDA #$06				;($E9C9)6 rows of end boss tiles need to be erased.
		STA GenByte3C		   ;($E9CB)

EndBossEraseLoop:
		LDY #$07				;($E9CD)7 tiles per row.

		* JSR AddPPUBufferEntry ;($E9CF)($C690)Add data to PPU buffer.
		DEY					 ;($E9D2)Have all the tiles in the row been cleared?
		BNE -				   ;($E9D3)If not, branch to delete another tile.

		LDA PPUAddrLB		   ;($E9D5)
		CLC					 ;($E9D7)
		ADC #$19				;($E9D8)Move to the start of the next row to clear.
		STA PPUAddrLB		   ;($E9DA)
		BCC +				   ;($E9DC)
		INC PPUAddrUB		   ;($E9DE)

		* DEC GenByte3C		 ;($E9E0)Does another row need to be cleared?
		BNE EndBossEraseLoop	;($E9E2)If so, branch to clear the row.

		JSR WaitForNMI		  ;($E9E4)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($E9E7)($FF74)

		LDA #$00				;($E9EA)Clear enemy number.
		STA EnemyNumber		 ;($E9EC)

		JSR DoDialogHiBlock	 ;($E9EE)($C7C5)Thou hast found the ball of light...
		.byte $1A			   ;($E9F1)TextBlock18, entry 10.

		LDA StoryFlags		  ;($E9F2)
		ORA #F_DGNLRD_DEAD	  ;($E9F4)Set flag indicating the dragonlord has been defeated.
		STA StoryFlags		  ;($E9F6)

		JSR WaitForBtnRelease   ;($E9F8)($CFE4)Wait for player to release then press joypad buttons.

		LDA DisplayedMaxHP	  ;($E9FB)
		STA HitPoints		   ;($E9FD)Max out the player's HP and MP.
		LDA DisplayedMaxMP	  ;($E9FF)
		STA MagicPoints		 ;($EA01)

		LDX #$12				;($EA03)Overworld at Dragonlord's castle entrance.
		LDA #DIR_DOWN		   ;($EA05)Player will be facing down.
		JMP ChangeMaps		  ;($EA07)($D9E2)Load a new map.

RegEnDefeated:
		LDA EnBaseExp		   ;($EA0A)
		STA FightExperienceLB   ;($EA0D)Save the experience gained from the fight.
		LDA #$00				;($EA0F)
		STA FightExperienceUB   ;($EA11)

		JSR DoDialogLoBlock	 ;($EA13)($C7CB)Thy experience increases by...
		.byte $EF			   ;($EA16)TextBlock15, entry 15.

		LDA FightExperienceLB   ;($EA17)
		CLC					 ;($EA19)
		ADC ExpLB			   ;($EA1A)Add fight experience to player's total experience.
		STA ExpLB			   ;($EA1C)
		BCC CalcPlyrGold		;($EA1E)
		INC ExpUB			   ;($EA20)Did player's experience roll over?
		BNE CalcPlyrGold		;($EA22)If not, branch.

		LDA #$FF				;($EA24)
		STA ExpLB			   ;($EA26)Max out player's experience.
		STA ExpUB			   ;($EA28)

CalcPlyrGold:
		LDA EnBaseGld		   ;($EA2A)Prepare to multiply enemy's base gold by a random number.
		STA MultiplyNumber2LB   ;($EA2D)

		JSR UpdateRandNum	   ;($EA2F)($C55B)Get random number.
		LDA RandomNumberUB	  ;($EA32)Keep only 6 bytes(0-63).
		AND #$3F				;($EA34)

		CLC					 ;($EA36)
		ADC #$C0				;($EA37)Add 192 to random number(63-255).
		STA MultiplyNumber1LB   ;($EA39)

		LDA #$00				;($EA3B)Multiply enemy's base gold with random number.
		STA MultiplyNumber1UB   ;($EA3D)
		STA MultiplyNumber2UB   ;($EA3F)
		JSR WordMultiply		;($EA41)($C1C9)Multiply 2 16-bit words.

		LDA MultiplyResultUB	;($EA44)
		STA FightGoldLB		 ;($EA46)Final equation for gained gold:
		LDA #$00				;($EA48)Gold=EnBaseGold*(192+rnd(63))/256.
		STA FightGoldUB		 ;($EA4A)

		JSR DoDialogLoBlock	 ;($EA4C)($C7CB)Thy gold increases by...
		.byte $F0			   ;($EA4F)TextBlock16, entry 0.

		LDA $00				 ;($EA50)
		CLC					 ;($EA52)
		ADC GoldLB			  ;($EA53)Add fight gold to player's total gold.
		STA GoldLB			  ;($EA55)
		BCC ChkLevelUp		  ;($EA57)
		INC GoldUB			  ;($EA59)Did player's gold roll over?
		BNE ChkLevelUp		  ;($EA5B)If not, branch.

		LDA #$FF				;($EA5D)
		STA GoldLB			  ;($EA5F)Max out player's gold.
		STA GoldUB			  ;($EA61)

ChkLevelUp:
		JSR Dowindow			;($EA63)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($EA66)Pop-up window.

		LDA DisplayedMaxMP	  ;($EA67)
		PHA					 ;($EA69)
		LDA DisplayedMaxHP	  ;($EA6A)
		PHA					 ;($EA6C)
		LDA DisplayedAgility	;($EA6D)Save the player's current stats on the stack.
		PHA					 ;($EA6F)
		LDA DisplayedStrength   ;($EA70)
		PHA					 ;($EA72)
		LDA DisplayedLevel	  ;($EA73)
		PHA					 ;($EA75)
		JSR LoadStats		   ;($EA76)($F050)Update player attributes.

		PLA					 ;($EA79)Did player level up?
		CMP DisplayedLevel	  ;($EA7A)
		BNE DoLevelUp		   ;($EA7C)If so, branch.

		BRK					 ;($EA7E)Wait for the music clip to end.
		.byte $03, $17		  ;($EA7F)($815E)WaitForMusicEnd, bank 1.

		LDX MapNumber		   ;($EA81)Get current map number.
		LDA ResumeMusicTbl,X	;($EA83)Use current map number to resume music.
		BRK					 ;($EA86)
		.byte $04, $17		  ;($EA87)($81A0)InitMusicSFX, bank 1.

		PLA					 ;($EA89)
		PLA					 ;($EA8A)Remove player's stored stats from the stack.
		PLA					 ;($EA8B)
		PLA					 ;($EA8C)

		JMP ExitFight		   ;($EA8D)($EE54)Return to map after fight.

DoLevelUp:
		LDA #MSC_LEVEL_UP	   ;($EA90)Level up music.
		BRK					 ;($EA92)
		.byte $04, $17		  ;($EA93)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($EA95)Wait for the music clip to end.
		.byte $03, $17		  ;($EA96)($815E)WaitForMusicEnd, bank 1.

		LDX MapNumber		   ;($EA98)Get current map number.
		LDA ResumeMusicTbl,X	;($EA9A)Use current map number to resume music.
		BRK					 ;($EA9D)
		.byte $04, $17		  ;($EA9E)($81A0)InitMusicSFX, bank 1.

		JSR DoDialogLoBlock	 ;($EAA0)($C7CB)Thou hast been promoted to the next level...
		.byte $F1			   ;($EAA3)TextBlock16, entry 1.

		LDA #$00				;($EAA4)Always set upper amount to 0.
		STA AmountUB			;($EAA6)

		PLA					 ;($EAA8)
		STA PlayerTempStat	  ;($EAA9)
		LDA DisplayedStr		;($EAAB)Did the player's strength increase this level?
		SEC					 ;($EAAD)
		SBC PlayerTempStat	  ;($EAAE)
		BEQ ChkAgilityUp		;($EAB0)If not, branch.

		STA AmountLB			;($EAB2)Store the amount the player's strength increased.

		JSR DoDialogHiBlock	 ;($EAB4)($C7C5)Thy power increases by...
		.byte $0E			   ;($EAB7)TextBlock17, entry 14.

ChkAgilityUp:
		PLA					 ;($EAB8)
		STA PlayerTempStat	  ;($EAB9)
		LDA DisplayedAgility	;($EABB)Did the player's agility increase this level?
		SEC					 ;($EABD)
		SBC PlayerTempStat	  ;($EABE)
		BEQ ChkHPUp			 ;($EAC0)If not, branch.

		STA AmountLB			;($EAC2)Store the amount the player's agility increased.

		JSR DoDialogHiBlock	 ;($EAC4)($C7C5)Thy response speed increases by...
		.byte $0F			   ;($EAC7)TextBlock17, entry 15.

ChkHPUp:
		PLA					 ;($EAC8)
		STA PlayerTempStat	  ;($EAC9)
		LDA DisplayedMaxHP	  ;($EACB)Player's HP goes up every level.
		SEC					 ;($EACD)
		SBC PlayerTempStat	  ;($EACE)
		STA AmountLB			;($EAD0)Store the amount the player's HP increased.

		JSR DoDialogHiBlock	 ;($EAD2)($C7C5)Thy maximum hit points Increase by...
		.byte $10			   ;($EAD5)TextBlock18, entry 0.

		PLA					 ;($EAD6)
		STA PlayerTempStat	  ;($EAD7)
		LDA DisplayedMaxMP	  ;($EAD9)Did the player's MP increase this level?
		SEC					 ;($EADB)
		SBC PlayerTempStat	  ;($EADC)
		BEQ ChkNewSpell		 ;($EADE)If not, branch.

		STA AmountLB			;($EAE0)Store the amount the player's MP increased.

		JSR DoDialogHiBlock	 ;($EAE2)($C7C5)Thy maximum magic points increased...
		.byte $11			   ;($EAE5)TextBlock18, entry 1.

ChkNewSpell:
		LDA DisplayedLevel	  ;($EAE6)
		CMP #LEVEL_03		   ;($EAE8)
		BEQ NewSpellDialog	  ;($EAEA)
		CMP #LEVEL_04		   ;($EAEC)
		BEQ NewSpellDialog	  ;($EAEE)
		CMP #LEVEL_07		   ;($EAF0)
		BEQ NewSpellDialog	  ;($EAF2)
		CMP #LEVEL_09		   ;($EAF4)
		BEQ NewSpellDialog	  ;($EAF6)A new spell has been learned.  New spells are
		CMP #LEVEL_10		   ;($EAF8)learned on levels 3, 4, 7, 9, 10, 12, 13, 15,
		BEQ NewSpellDialog	  ;($EAFA)17 and 19.
		CMP #LEVEL_12		   ;($EAFC)
		BEQ NewSpellDialog	  ;($EAFE)
		CMP #LEVEL_13		   ;($EB00)
		BEQ NewSpellDialog	  ;($EB02)
		CMP #LEVEL_15		   ;($EB04)
		BEQ NewSpellDialog	  ;($EB06)
		CMP #LEVEL_17		   ;($EB08)
		BEQ NewSpellDialog	  ;($EB0A)
		CMP #LEVEL_19		   ;($EB0C)

		BNE +				   ;($EB0E)No new spell learned. Branch to skip new spell dialog.

NewSpellDialog:
		JSR DoDialogLoBlock	 ;($EB10)($C7CB)Thou hast learned a new spell...
		.byte $F2			   ;($EB13)TextBlock16, entry 2.

		* JSR Dowindow		  ;($EB14)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($EB17)Pop-up window.

		JMP ExitFight		   ;($EB18)($EE54)Return to map after fight.

;----------------------------------------------------------------------------------------------------

StartEnemyTurn:
		LDA PlayerFlags		 ;($EB1B)Check if enemy is asleep.
		AND #F_EN_ASLEEP		;($EB1D)
		BEQ DoEnemyAttack	   ;($EB1F)($EB48)Enemy is not asleep.  Branch to continue.

		* JSR UpdateRandNum	 ;($EB21)($C55B)Get random number.
		LDA RandomNumberUB	  ;($EB24)
		AND #$03				;($EB26)Get random number until at least one of the 2 LSBs is set.
		BEQ -				   ;($EB28)

		CMP #$01				;($EB2A)1 in 4 chance enemy will wake up.
		BNE EnStillAsleep	   ;($EB2C)Is enemy still asleep if so, branch.

		LDA PlayerFlags		 ;($EB2E)
		AND #$BF				;($EB30)Clear enemy asleep flag.
		STA PlayerFlags		 ;($EB32)
		JSR CopyEnUpperBytes	;($EB34)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($EB37)($C7CB)Enemy hath woken up...
		.byte $00			   ;($EB3A)TextBlock 1, entry 0.

		JMP DoEnemyAttack	   ;($EB3B)($EB48)Enemy woke up.  Jump to continue.

EnStillAsleep:
		JSR CopyEnUpperBytes	;($EB3E)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($EB41)($C7CB)The enemy is asleep...
		.byte $F8			   ;($EB44)TextBlock16, entry 8.

		JMP StartPlayerTurn	 ;($EB45)($E5CE)It's the player's turn to attack.

;----------------------------------------------------------------------------------------------------

DoEnemyAttack:
		JSR CheckEnRun		  ;($EB48)($EFB7)Check if enemy is going to run away.
		JSR UpdateRandNum	   ;($EB4B)($C55B)Get random number.
		LDA EnSpell			 ;($EB4E)
		AND #$30				;($EB51)Get upper spells control bits.
		STA GenByte3C		   ;($EB53)
		LDA RandomNumberUB	  ;($EB55)Make random check to see if an upper spell will be cast.
		AND #$30				;($EB57)
		CMP GenByte3C		   ;($EB59)Will upper spell be cast?
		BCS EnCheckHurtFire	 ;($EB5B)If not, branch to check if lower spell will be cast.

		LDA EnSpell			 ;($EB5D)Get upper spell bits.
		AND #$C0				;($EB60)Some spell other than sleep?
		BNE +				   ;($EB62)If so, branch to check which spell.

		LDA PlayerFlags		 ;($EB64)Is the player asleep?
		BMI EnCheckHurtFire	 ;($EB66)If so, branch to check if lower spell will be cast.
		JMP EnCastSleep		 ;($EB68)($EC92)Enemy casts sleep.

		* CMP #$40			  ;($EB6B)Does enemy have stopspell?
		BNE +				   ;($EB6D)If not, branch to check for heal.

		LDA PlayerFlags		 ;($EB6F)Is the player stopspelled?
		AND #F_PLR_STOPSPEL	 ;($EB71)
		BNE EnCheckHurtFire	 ;($EB73)If so, branch to check if lower spell will be cast.
		JMP EnCastStopspell	 ;($EB75)($EC69)Enemy casts stopspell.

		* CMP #$80			  ;($EB78)Does enemy have heal?
		BNE +				   ;($EB7A)If not, branch to check for healmore.

		LDA EnBaseHP			;($EB7C)Is enemies current hit points less than 1/4
		LSR					 ;($EB7F)of base hit points?
		LSR					 ;($EB80)If not, branch to check if lower spell will be cast.
		CMP EnCurntHP		   ;($EB81)
		BCC EnCheckHurtFire	 ;($EB83)
		JMP EnCastHeal		  ;($EB85)($ECA6)Enemy casts heal.

		* LDA EnBaseHP		  ;($EB88)Is enemies current hit points less than 1/4
		LSR					 ;($EB8B)of base hit points?
		LSR					 ;($EB8C)If not, branch to check if lower spell will be cast.
		CMP EnCurntHP		   ;($EB8D)
		BCC EnCheckHurtFire	 ;($EB8F)
		JMP EnCastHealmore	  ;($EB91)($ECCE)Enemy casts healmore.

EnCheckHurtFire:
		JSR UpdateRandNum	   ;($EB94)($C55B)Get random number.
		LDA EnSpell			 ;($EB97)
		AND #$03				;($EB9A)Get lower spells control bits.
		STA GenByte3C		   ;($EB9C)
		LDA RandomNumberUB	  ;($EB9E)
		AND #$03				;($EBA0)Make random check to see if a lower spell will be cast.
		CMP GenByte3C		   ;($EBA2)Will lower spell be cast?
		BCS EnPhysAttack		;($EBA4)If not, branch. Enemy going to do a physical attack.

		LDA EnSpell			 ;($EBA6)Get upper spell bits.
		AND #$0C				;($EBA9)Some spell other than hurt?
		BNE +				   ;($EBAB)If so, branch to check which spell.
		JMP EnCastHurt		  ;($EBAD)($EC23)Enemy casts hurt.

		* CMP #$04			  ;($EBB0)Does enemy have hurtmore spell?
		BNE +				   ;($EBB2)If not, branch.
		JMP EnCastHurtmore	  ;($EBB4)($EC55)Enemy casts hurtmore.

		* CMP #$08			  ;($EBB7)Does enemy have fire1?
		BNE +				   ;($EBB9)If not, branch to do fire2.
		JMP EnCastFire1		 ;($EBBB)($ECED)Enemy casts fire1.

		* JMP EnCastFire2	   ;($EBBE)($ECE1)Enemy casts fire2(end boss only).

EnPhysAttack:
		LDA #SFX_ATCK_PREP	  ;($EBC1)Prepare to attack SFX.
		BRK					 ;($EBC3)
		.byte $04, $17		  ;($EBC4)($81A0)InitMusicSFX, bank 1.

		JSR CopyEnUpperBytes	;($EBC6)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($EBC9)($C7CB)The enemy attacks...
		.byte $F9			   ;($EBCC)TextBlock16, entry 9.

		LDA EnBaseAtt		   ;($EBCD)Make a copy of enemy's attack stat.
		STA AttackStat		  ;($EBD0)
		LDA DisplayedDefense	;($EBD2)Make a copy of player's defense stat.
		STA DefenseStat		 ;($EBD4)
		JSR EnCalcHitDmg		;($EBD6)($EFF4)Calculate enemy hit damage on player.

		LDA CalcDamage		  ;($EBD9)Did enemy do damage to the player?
		BNE EnHitsPlayer		;($EBDB)If so, branch to subtract damage from player's HP.

		LDA #SFX_MISSED2		;($EBDD)Attack missed 2 SFX.
		BRK					 ;($EBDF)
		.byte $04, $17		  ;($EBE0)($81A0)InitMusicSFX, bank 1.

		JSR DoDialogLoBlock	 ;($EBE2)($C7CB)A miss! no damage hath been scored...
		.byte $FB			   ;($EBE5)TextBlock16, entry 11.

		JMP StartPlayerTurn	 ;($EBE6)($E5CE)It's the player's turn to attack.

EnHitsPlayer:
		STA GenByte00		   ;($EBE9)Store damage to subtract from player's hit points.
		JMP PlayerHit		   ;($EBEB)($ED20)Player takes damage.

EnCastSpell:
		JSR CopyEnUpperBytes	;($EBEE)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($EBF1)($C7CB)enemy...
		.byte $FC			   ;($EBF4)TextBlock16, entry 12.

		LDA SpellToCast		 ;($EBF5)Get description byte for spell to cast.
		JSR GetDescriptionByte  ;($EBF7)($DBF0)Load byte for item dialog description.

		JSR DoDialogLoBlock	 ;($EBFA)($C7CB)Chants the spell of spell...
		.byte $FD			   ;($EBFD)TextBlock16, entry 13.

		LDA #SFX_SPELL		  ;($EBFE)Spell cast SFX.
		BRK					 ;($EC00)
		.byte $04, $17		  ;($EC01)($81A0)InitMusicSFX, bank 1.

		LDA SplFlshBGPalPtr	 ;($EC03)Get pointer to background flashing palettes.
		STA GenPtr42LB		  ;($EC06)
		LDA SplFlshBGPalPtr+1   ;($EC08)
		STA GenPtr42UB		  ;($EC0B)
		JSR PaletteFlash		;($EC0D)($EF38)Palette flashing effect.

		BRK					 ;($EC10)Wait for the music clip to end.
		.byte $03, $17		  ;($EC11)($815E)WaitForMusicEnd, bank 1.

		LDA PlayerFlags		 ;($EC13)
		AND #F_EN_STOPSPEL	  ;($EC15)Has the enemy been stopspelled?
		BNE EnStopSplDialog	 ;($EC17)If so, branch to display blocked dialog.
		RTS					 ;($EC19)

EnStopSplDialog:
		JSR DoDialogLoBlock	 ;($EC1A)($C7CB)But the spell has been blocked...
		.byte $EA			   ;($EC1D)TextBlock15, entry 10.

		PLA					 ;($EC1E)Remove return address from last function.
		PLA					 ;($EC1F)
		JMP StartPlayerTurn	 ;($EC20)($E5CE)It's the player's turn to attack.

EnCastHurt:
		LDA #DSC_HURT-4		 ;($EC23)Prepare to cast hurt spell.
		STA SpellToCast		 ;($EC25)
		JSR EnCastSpell		 ;($EC27)($EBEE)Enemy casts a spell.

		JSR UpdateRandNum	   ;($EC2A)($C55B)Get random number.
		LDA RandomNumberUB	  ;($EC2D)
		AND #$07				;($EC2F)Keep 3 bits of random number(0-7).
		CLC					 ;($EC31)
		ADC #$03				;($EC32)Hurt spel will do between 7 and 10 damage.

EnCalcSpllDmg:
		STA PlayerDamage		;($EC34)Store base damage player will take.

		LDA EqippedItems		;($EC36)
		AND #AR_ARMOR		   ;($EC38)Does player have Erdrick's armor?
		CMP #AR_ERDK_ARMR	   ;($EC3A)If so, branch to reduce damage to 2/3.
		BEQ ReducedSpellDmg	 ;($EC3C)

		CMP #AR_MAGIC_ARMR	  ;($EC3E)Does player have magic armor?
		BNE DoPlyrDmg		   ;($EC40)If not, branch. Player takes regular damage.

ReducedSpellDmg:
		LDA PlayerDamage		;($EC42)
		STA DivideNumber1LB	 ;($EC44)Divide player damage by 3.
		LDA #$03				;($EC46)
		STA DivideNumber2	   ;($EC48)
		JSR ByteDivide		  ;($EC4A)($C1F0)Divide a 16-bit number by an 8-bit number.

		LDA DivideQuotient	  ;($EC4D)
		ASL					 ;($EC4F)Multiply player damage by 2. Result is 2/3 damage.
		STA PlayerDamage		;($EC50)

DoPlyrDmg:
		JMP PlayerHit		   ;($EC52)($ED20)Player takes damage.

EnCastHurtmore:
		LDA #DSC_HURTMORE-4	 ;($EC55)Prepare to cast hurtmore spell.
		STA SpellToCast		 ;($EC57)
		JSR EnCastSpell		 ;($EC59)($EBEE)Enemy casts a spell.

		JSR UpdateRandNum	   ;($EC5C)($C55B)Get random number.
		LDA RandomNumberUB	  ;($EC5F)Get random number and keep lower 4 bits.
		AND #$0F				;($EC61)
		CLC					 ;($EC63)Add 30.
		ADC #$1E				;($EC64)Enemy damages for 30HP min and 45HP max(base damage).
		JMP EnCalcSpllDmg	   ;($EC66)($EC34)Calculate player damage.

EnCastStopspell:
		LDA #DSC_STOPSPELL-4	;($EC69)Prepare to cast stopspell.
		STA SpellToCast		 ;($EC6B)
		JSR EnCastSpell		 ;($EC6D)($EBEE)Enemy casts a spell.

		LDA EqippedItems		;($EC70)If player is wearing Erdrick's armor,
		AND #AR_ARMOR		   ;($EC72)stopspell will not work.
		CMP #AR_ERDK_ARMR	   ;($EC74)
		BEQ BlockStopSpell	  ;($EC76)Branch to block.

		JSR UpdateRandNum	   ;($EC78)($C55B)Get random number.
		LDA RandomNumberUB	  ;($EC7B)50% chance it will stopspell the player.
		LSR					 ;($EC7D)
		BCC BlockStopSpell	  ;($EC7E)Branch if stopspell was blocked.

		LDA PlayerFlags		 ;($EC80)
		ORA #F_PLR_STOPSPEL	 ;($EC82)Stopspell on player was successful.
		STA PlayerFlags		 ;($EC84)

		LDA #$FE				;($EC86)TextBlock16, entry 14. Spell is blocked...
		* JSR DoMidDialog	   ;($EC88)($C7BD)

		JMP StartPlayerTurn	 ;($EC8B)($E5CE)It's the player's turn to attack.

BlockStopSpell:
		LDA #$EB				;($EC8E)TextBlock15, Entry 11. The spell will not work...
		BNE -				   ;($EC90)Branch always.

EnCastSleep:
		LDA #DSC_SLEEP-4		;($EC92)Prepare to cast sleep spell.
		STA SpellToCast		 ;($EC94)
		JSR EnCastSpell		 ;($EC96)($EBEE)Enemy casts a spell.

		LDA PlayerFlags		 ;($EC99)
		ORA #F_PLR_ASLEEP	   ;($EC9B)Set player flag for sleep.
		STA PlayerFlags		 ;($EC9D)

		JSR DoDialogHiBlock	 ;($EC9F)($C7C5)Thou art asleep...
		.byte $06			   ;($ECA2)TextBlock17, entry 6.

		JMP PlayerAsleepDialog  ;($ECA3)($E5DE)Show dialog that player is still asleep.

EnCastHeal:
		LDA #DSC_HEAL-4		 ;($ECA6)Prepare to cast heal spell.
		STA SpellToCast		 ;($ECA8)
		JSR EnCastSpell		 ;($ECAA)($EBEE)Enemy casts a spell.

		JSR UpdateRandNum	   ;($ECAD)($C55B)Get random number.
		LDA RandomNumberUB	  ;($ECB0)Get random number and keep lower 3 bits.
		AND #$07				;($ECB2)
		CLC					 ;($ECB4)Add 20.
		ADC #$14				;($ECB5)Enemy recovers 20HP min and 27HP max.

EnemyAddHP:
		CLC					 ;($ECB7)
		ADC EnCurntHP		   ;($ECB8)Add recovered amount to enemy hit points.
		CMP EnBaseHP			;($ECBA)
		BCC +				   ;($ECBD)Is new amount higher than max amount? If not, branch.

		LDA EnBaseHP			;($ECBF)Enemy hit points fully recovered.

		* STA EnCurntHP		 ;($ECC2)Update enemy hit points.
		JSR CopyEnUpperBytes	;($ECC4)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogHiBlock	 ;($ECC7)($C7C5)The enemy hath recovered...
		.byte $09			   ;($ECCA)TextBlock17, entry 9.

		JMP StartPlayerTurn	 ;($ECCB)($E5CE)It's the player's turn to attack.

EnCastHealmore:
		LDA #DSC_HEALMORE-4	 ;($ECCE)Prepare to cast healmore spell.
		STA SpellToCast		 ;($ECD0)
		JSR EnCastSpell		 ;($ECD2)($EBEE)Enemy casts a spell.

		JSR UpdateRandNum	   ;($ECD5)($C55B)Get random number.
		LDA RandomNumberUB	  ;($ECD8)Get random number and keep lower 4 bits.
		AND #$0F				;($ECDA)
		CLC					 ;($ECDC)Add 85.
		ADC #$55				;($ECDD)Enemy recovers 85HP min and 100HP max.
		BNE EnemyAddHP		  ;($ECDF)Branch always.

EnCastFire2:
		JSR UpdateRandNum	   ;($ECE1)($C55B)Get random number.
		LDA RandomNumberUB	  ;($ECE4)Keep 3 bits(0-7).
		AND #$07				;($ECE6)
		CLC					 ;($ECE8)
		ADC #$41				;($ECE9)Fire2 damage ranges from 65 to 72.
		BNE CalcPlyrDmg		 ;($ECEB)

EnCastFire1:
		JSR UpdateRandNum	   ;($ECED)($C55B)Get random number.
		LDA RandomNumberUB	  ;($ECF0)Keep 3 bits(0-7).
		AND #$07				;($ECF2)
		ORA #$10				;($ECF4)Fire1 damage ranges from 16 to 23.

CalcPlyrDmg:
		STA PlayerDamage		;($ECF6)
		LDA #$00				;($ECF8)Store base damage player will take.
		STA DmgNotUsed		  ;($ECFA)

		LDA EqippedItems		;($ECFC)
		AND #AR_ARMOR		   ;($ECFE)Does player have Erdrick's armor?
		CMP #AR_ERDK_ARMR	   ;($ED00)If so, branch to reduce damage to 2/3.
		BNE DoFireSFX		   ;($ED02)

		LDA $00				 ;($ED04)
		STA DivideNumber1LB	 ;($ED06)Divide player damage by 3.
		LDA #$03				;($ED08)
		STA DivideNumber2	   ;($ED0A)
		JSR ByteDivide		  ;($ED0C)($C1F0)Divide a 16-bit number by an 8-bit number.

		LDA DivideQuotient	  ;($ED0F)
		ASL					 ;($ED11)Multiply player damage by 2. Result is 2/3 damage.
		STA $00				 ;($ED12)

DoFireSFX:
		LDA #SFX_FIRE		   ;($ED14)Fire SFX.
		BRK					 ;($ED16)
		.byte $04, $17		  ;($ED17)($81A0)InitMusicSFX, bank 1.

		JSR CopyEnUpperBytes	;($ED19)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($ED1C)($C7CB)The enemy is breathing fire...
		.byte $FF			   ;($ED1F)TextBlock16, entry 15.

;----------------------------------------------------------------------------------------------------

PlayerHit:
		LDA #SFX_PLYR_HIT1	  ;($ED20)Player hit 1 SFX.
		BRK					 ;($ED22)
		.byte $04, $17		  ;($ED23)($81A0)InitMusicSFX, bank 1.

		LDA #$00				;($ED25)
		STA DmgNotUsed		  ;($ED27)Subtract damage from player's HP.
		LDA HitPoints		   ;($ED29)
		SEC					 ;($ED2B)
		SBC PlayerDamage		;($ED2C)Did HP go below 0?
		BCS +				   ;($ED2E)If not, branch.

		LDA #$00				;($ED30)Set player HP to zero. Player died.

		* STA HitPoints		 ;($ED32)Update player HP.

		LDA #$08				;($ED34)Prepare to run the shake counter loop 8 times.
		STA ShakeCounter		;($ED36)

		LDA ScrollX			 ;($ED38)
		STA ShakeX			  ;($ED3A)Ititialize the shake X and Y with current scroll positions.
		LDA ScrollY			 ;($ED3C)
		STA ShakeY			  ;($ED3E)

ShakeScreenLoop:
		JSR WaitForNMI		  ;($ED40)($FF74)Wait for VBlank interrupt.

		LDA HitPoints		   ;($ED43)Did player just die?
		BEQ +				   ;($ED45)If so, branch.

		JSR WaitForNMI		  ;($ED47)($FF74)Wait for VBlank interrupt.
		JMP ChkShakeCounter	 ;($ED4A)Player did not die. Update screen shake.

		* LDA EnemyNumber	   ;($ED4D)Player died. Is player fighting the end boss?
		CMP #EN_DRAGONLORD2	 ;($ED4F)
		BEQ ChkShakeCounter	 ;($ED51)If so, branch to update the screen shake.

		JSR RedFlashScreen	  ;($ED53)($EE14)Flash the screen red.

ChkShakeCounter:
		LDA ShakeCounter		;($ED56)
		AND #$01				;($ED58)Shake screen in X or Y directions every other counter decrement.
		BNE UpdateShakeY		;($ED5A)

		LDA ShakeX			  ;($ED5C)
		CLC					 ;($ED5E)
		ADC #$02				;($ED5F)Shake screen 2 pixels to the right.
		STA ScrollX			 ;($ED61)
		JMP DoShake			 ;($ED63)

UpdateShakeY:
		LDA ShakeY			  ;($ED66)
		CLC					 ;($ED68)Shake screen 2 pixels down.
		ADC #$02				;($ED69)
		STA ScrollY			 ;($ED6B)

DoShake:
		LDA EnemyNumber		 ;($ED6D)Is player fighting the end boss?
		CMP #EN_DRAGONLORD2	 ;($ED6F)
		BNE +				   ;($ED71)If not, branch.

		LDA ShakeX			  ;($ED73)
		STA ScrollX			 ;($ED75)Reset scroll registers to original values if fighting
		LDA ShakeY			  ;($ED77)the end boss. Screen does not shake while fighting end boss.
		STA ScrollY			 ;($ED79)

		* JSR WaitForNMI		;($ED7B)($FF74)Wait for VBlank interrupt.
		JSR LoadRegularBGPal	;($ED7E)($EE28)Load the normal background palette.

		LDA ShakeX			  ;($ED81)
		STA ScrollX			 ;($ED83)Reset scroll registers to original values.
		LDA ShakeY			  ;($ED85)
		STA ScrollY			 ;($ED87)

		DEC ShakeCounter		;($ED89)Does screen shake need to continue?
		BNE ShakeScreenLoop	 ;($ED8B)If so, branch to keep shaking the screen.

		JSR DoDialogLoBlock	 ;($ED8D)($C7CB)Thy hit points decreased...
		.byte $FA			   ;($ED90)TextBlock16, entry 10.

		JSR Dowindow			;($ED91)($C6F0)display on-screen window.
		.byte WINDOW_POPUP	  ;($ED94)Show pop-up window.

		LDA HitPoints		   ;($ED95)Has player died?
		BEQ PlayerHasDied	   ;($ED97)
		JMP StartPlayerTurn	 ;($ED99)($E5CE)It's the player's turn to attack.

PlayerHasDied:
		LDA #MSC_DEATH		  ;($ED9C)Death music.
		BRK					 ;($ED9E)
		.byte $04, $17		  ;($ED9F)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($EDA1)Wait for the music clip to end.
		.byte $03, $17		  ;($EDA2)($815E)WaitForMusicEnd, bank 1.

		JMP DeathText		   ;($EDA4)($EDB4)Tell player they have died.

InitDeathSequence:
		LDA #MSC_DEATH		  ;($EDA7)Death music.
		BRK					 ;($EDA9)
		.byte $04, $17		  ;($EDAA)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($EDAC)Wait for the music clip to end.
		.byte $03, $17		  ;($EDAD)($815E)WaitForMusicEnd, bank 1.

		LDA #WINDOW_DIALOG	  ;($EDAF)Dialog window.
		JSR _DoWindow		   ;($EDB1)($C703)Show dialog window.

DeathText:
		JSR DoDialogLoBlock	 ;($EDB4)($C7CB)Thou art dead...
		.byte $01			   ;($EDB7)TextBlock1, entry 1.

		LDA #STRT_FULL_HP	   ;($EDB8)Player's HP and MP should be maxed out on next start.
		STA ThisStrtStat		;($EDBA)

		LDA #$00				;($EDBD)Character will be facing up on next restart.
		STA CharDirection	   ;($EDBF)

		* JSR GetJoypadStatus   ;($EDC2)($C608)Get input button presses.
		LDA JoypadBtns		  ;($EDC5)
		AND #$09				;($EDC7)Wait for player to press start or A.
		BEQ -				   ;($EDC9)

		LSR GoldUB			  ;($EDCB)Cut the player's gold in half.
		ROR GoldLB			  ;($EDCD)

		LDA PlayerFlags		 ;($EDCF)
		AND #$FE				;($EDD1)Clear flag indicating player is carrying Gwaelin.
		STA PlayerFlags		 ;($EDD3)

		LDA EnemyNumber		 ;($EDD5)Appears to have no effect.
		STA DrgnLrdPal		  ;($EDD7)

		LDA #$00				;($EDDA)Clear out enemy number.
		STA EnemyNumber		 ;($EDDC)

		JSR StartAtThroneRoom   ;($EDDE)($CB47)Start player at throne room.

		LDA ModsnSpells		 ;($EDE1)Is player cursed?
		AND #$C0				;($EDE3)
		BEQ KingDeathDialog	 ;($EDE5)If not, branch so player can start in the throne room.

		JSR DoDialogHiBlock	 ;($EDE7)($C7C5)Thou hast failed and thou art cursed...
		.byte $14			   ;($EDEA)TextBlock18, entry 4.

		LDX #$0C				;($EDEB)Start player outside of Tantagel castle because they are cursed.
		LDA #DIR_DOWN		   ;($EDED)Player will be facing down.
		JMP ChangeMaps		  ;($EDEF)($D9E2)Load a new map.

KingDeathDialog:
		JSR DoDialogHiBlock	 ;($EDF2)($C7C5)Death should not have taken thee...
		.byte $0D			   ;($EDF5)TextBlock17, entry 13.

		LDA DisplayedLevel	  ;($EDF6)Is player the maximum level?
		CMP #LEVEL_30		   ;($EDF8)
		BEQ NowGoText		   ;($EDFA)If so, branch to skip experience dialog.

		JSR GetExperienceRemaining;($EDFC)($F134)Calculate experience needed for next level.

		JSR DoDialogHiBlock	 ;($EDFF)($C7C5)To reach the next level, thy experience must increase...
		.byte $12			   ;($EE02)TextBlock18, entry 2.

NowGoText:
		JSR DoDialogHiBlock	 ;($EE03)($C7C5)Now go player...
		.byte $13			   ;($EE06)TextBlock18, entry 3.

		JSR WaitForBtnRelease   ;($EE07)($CFE4)Wait for player to release then press joypad buttons.
		LDA #WINDOW_DIALOG	  ;($EE0A)Remove dialog window from the screen.
		JSR RemoveWindow		;($EE0C)($A7A2)Remove window from screen.

		LDA #NPC_MOVE		   ;($EE0F)
		STA StopNPCMove		 ;($EE11)Allow the NPCs to move.
		RTS					 ;($EE13)

;----------------------------------------------------------------------------------------------------

RedFlashScreen:
		JSR WaitForNMI		  ;($EE14)($FF74)Wait for VBlank interrupt.

		LDA RedFlashPalPtr	  ;($EE17)
		STA PalettePointerLB	;($EE1A)Set palette pointer to the red flash palette.
		LDA RedFlashPalPtr+1	;($EE1C)
		STA PalettePointerUB	;($EE1F)

		LDA #$00				;($EE21)No palette modification.
		STA PalModByte		  ;($EE23)
		JMP PrepBGPalLoad	   ;($EE25)($C63D)Load background palette data into PPU buffer

;----------------------------------------------------------------------------------------------------

LoadRegularBGPal:
		JSR WaitForNMI		  ;($EE28)($FF74)Wait for VBlank interrupt.

		LDA EnemyNumber		 ;($EE2B)Is player fighting the end boss?
		CMP #EN_DRAGONLORD2	 ;($EE2D)
		BNE LoadRegularMapPal   ;($EE2F)If not, branch.

		LDA FnlNormBGPalPtr	 ;($EE31)
		STA PalettePointerLB	;($EE34)Load regular background palette for end boss.
		LDA FnlNormBGPalPtr+1   ;($EE36)
		STA PalettePointerUB	;($EE39)

		JMP FinishRegularPalLoad;($EE3B)Jump to finish loading palette.

LoadRegularMapPal:
		LDA OverworldPalPtr	 ;($EE3E)
		CLC					 ;($EE41)Get index to proper palette for the current map.
		ADC MapType			 ;($EE42)

		STA PalettePointerLB	;($EE44)
		LDA OverworldPalPtr+1   ;($EE46)Load regular background palette for current map.
		ADC #$00				;($EE49)
		STA PalettePointerUB	;($EE4B)

FinishRegularPalLoad:
		LDA #$00				;($EE4D)No palette modification.
		STA PalModByte		  ;($EE4F)
		JMP PrepBGPalLoad	   ;($EE51)($C63D)Load background palette data into PPU buffer

;----------------------------------------------------------------------------------------------------

ExitFight:
		JSR ClearSpriteRAM	  ;($EE54)($C6BB)Clear sprite RAM.
		JSR WaitForBtnRelease   ;($EE57)($CFE4)Wait for player to release then press joypad buttons.

ExitFight2:
		JSR WaitForNMI		  ;($EE5A)($FF74)Wait for VBlank interrupt.

		LDA RegSPPalPtr		 ;($EE5D)
		STA PalettePointerLB	;($EE60)Load standard palette while on map.
		LDA RegSPPalPtr+1	   ;($EE62)
		STA PalettePointerUB	;($EE65)

		LDA #$00				;($EE67)Disable fade-in/fade-out.
		STA PalModByte		  ;($EE69)
		JSR PrepSPPalLoad	   ;($EE6B)($C632)Load sprite palette data into PPU buffer.

		LDA NPCUpdateCounter	;($EE6E)Are NPCs on the current map?
		AND #$70				;($EE70)
		BEQ +				   ;($EE72)If so, branch. to reset counter.

		LDA #$FF				;($EE74)Indicate no NPCs on the current map.
		* STA NPCUpdateCounter  ;($EE76)Update NPCUpdateCounter.

		LDA #WINDOW_DIALOG	  ;($EE78)Remove dialog window from screen.
		JSR RemoveWindow		;($EE7A)($A7A2)Remove window from screen.
		LDA #WINDOW_ALPHBT	  ;($EE7D)Remove alphabet window from screen.
		JSR RemoveWindow		;($EE7F)($A7A2)Remove window from screen.

		LDA #DIR_DOWN		   ;($EE82)Player will be facing down.
		STA CharDirection	   ;($EE84)

		JSR WaitForNMI		  ;($EE87)($FF74)Wait for VBlank interrupt.
		JSR Bank2ToNT1		  ;($EE8A)($FCAD)Load CHR ROM bank 2 into nametable 1.
		JSR DoSprites		   ;($EE8D)($B6DA)Update player and NPC sprites.
		RTS					 ;($EE90)

;----------------------------------------------------------------------------------------------------

TryRun:
		JSR UpdateRandNum	   ;($EE91)($C55B)Get random number.

		LDA EnemyNumber		 ;($EE94)Is player running from an Armored Knight, Red Dragon,
		CMP #EN_STONEMAN		;($EE96)Dragonlord 1 or Dragonlord 2?
		BCC ChkGrDrgnRun		;($EE98)If not, branch.

		LDA RandomNumberUB	  ;($EE9A)Load a random number and keep all the bits(0-255).
		JMP CalcNextOdds		;($EE9C)

ChkGrDrgnRun:
		CMP #EN_GDRAGON		 ;($EE9F)Is player running from a Starwyvern, Wizard, Axe Knight,
		BCC ChkDrollMRun		;($EEA1)Blue Dragon or Stoneman? If not, branch.

		LDA RandomNumberUB	  ;($EEA3)
		AND #$7F				;($EEA5)Load a random number and keep lower 7 bits(0-127).
		JMP CalcNextOdds		;($EEA7)

ChkDrollMRun:
		CMP #EN_DROLLMAGI	   ;($EEAA)Is player running from a Wyvern to a Green Dragon?
		BCC CalcWhoIsNext	   ;($EEAC)If not, branch.

		LDA RandomNumberUB	  ;($EEAE)Get a random nuber and keep lower 6 bits.
		AND #$3F				;($EEB0)
		STA MultiplyNumber2LB   ;($EEB2)
		JSR UpdateRandNum	   ;($EEB4)($C55B)Get random number.

		LDA RandomNumberUB	  ;($EEB7)Get a random number and keep lower 5 bits. Add it to
		AND #$1F				;($EEB9)previous number to get a range of 0-95.
		ADC MultiplyNumber2LB   ;($EEBB)
		JMP CalcNextOdds		;($EEBD)

;----------------------------------------------------------------------------------------------------

CalcWhoIsNext:
		JSR UpdateRandNum	   ;($EEC0)($C55B)Get random number.
		LDA RandomNumberUB	  ;($EEC3)
		AND #$3F				;($EEC5)Keep only lower 6 bits(0-63).

CalcNextOdds:
		STA MultiplyNumber1LB   ;($EEC7)Store random number as a multiplier.
		LDA EnBaseDef		   ;($EEC9)
		STA MultiplyNumber2LB   ;($EECC)
		LDA #$00				;($EECE)Multiply the random number by the enemy's defense.
		STA MultiplyNumber1UB   ;($EED0)
		STA MultiplyNumber2UB   ;($EED2)
		JSR WordMultiply		;($EED4)($C1C9)Multiply 2 16-bit words.

		LDA MultiplyResultLB	;($EED7)
		STA GenWord42LB		 ;($EED9)Save the results for later.
		LDA MultiplyResultUB	;($EEDB)
		STA GenWord42UB		 ;($EEDD)

		JSR UpdateRandNum	   ;($EEDF)($C55B)Get random number.

		LDA RandomNumberUB	  ;($EEE2)Store random number as a multiplier.
		STA MultiplyNumber1LB   ;($EEE4)
		LDA DisplayedAgility	;($EEE6)
		STA MultiplyNumber2LB   ;($EEE8)Multiply the random number by the player's agility.
		LDA #$00				;($EEEA)
		STA MultiplyNumber1UB   ;($EEEC)
		STA MultiplyNumber2UB   ;($EEEE)
		JSR WordMultiply		;($EEF0)($C1C9)Multiply 2 16-bit words.

		LDA MultiplyResultLB	;($EEF3)
		SEC					 ;($EEF5)Subtract the enemy's defense*rnd from player's agility*rnd.
		SBC GenWord42LB		 ;($EEF6)If number comes out negative, that's bad for the
		LDA MultiplyResultUB	;($EEF8)player(carry clear). The higher the enemy's defense, the
		SBC GenWord42UB		 ;($EEFA)harder it is for the player to come out on top.
		RTS					 ;($EEFC)

;----------------------------------------------------------------------------------------------------

LoadEnPalette:
		LDA EnemyNumber		 ;($EEFD)
		STA MultiplyNumber1LB   ;($EEFF)
		LDA #$0C				;($EF01)
		STA MultiplyNumber2LB   ;($EF03)Multiply the enemy number by 12. There are 12 bytes of
		LDA #$00				;($EF05)palette data per enemy. The result contains the index to
		STA MultiplyNumber1UB   ;($EF07)the desired enemy palette data.
		STA MultiplyNumber2UB   ;($EF09)
		JSR WordMultiply		;($EF0B)($C1C9)Multiply 2 16-bit words.

		LDA MultiplyResultLB	;($EF0E)
		CLC					 ;($EF10)
		ADC EnSPPalsPtr		 ;($EF11)Add the base address of the enemy palette data
		STA GenPtr3CLB		  ;($EF14)to the calculated index from above. The pointer
		LDA MultiplyResultUB	;($EF16)Now points to the proper enemy palette data.
		ADC EnSPPalsPtr+1	   ;($EF18)
		STA GenPtr3CUB		  ;($EF1B)

		TYA					 ;($EF1D)Save Y on the stack.
		PHA					 ;($EF1E)

		LDY #$0B				;($EF1F)Prepare to transfer 12 bytes of palette data.

EnPalLoop:
		LDA (GenPtr3C),Y		;($EF21)Copy enemy palette data byte to buffer.
		STA EnPalData,Y		 ;($EF23)

		DEY					 ;($EF26)Have all palette bytes been transferred?
		BPL EnPalLoop		   ;($EF27)If not, branch to get another byte.

		PLA					 ;($EF29)Restore Y from the stack.
		TAY					 ;($EF2A)

		LDA #$03				;($EF2B)
		STA SpritePalettePointerUB;($EF2D)
		STA PalettePointerUB	;($EF2F)
		LDA #$A0				;($EF31)Set copy pointers to buffered data.
		STA SpritePalettePointerLB;($EF33)
		STA PalettePointerLB	;($EF35)
		RTS					 ;($EF37)

;----------------------------------------------------------------------------------------------------

PaletteFlash:
		LDA #$05				;($EF38)Prepare to flash palette 5 times.
		STA PaletteFlashCounter ;($EF3A)

PalFlashLoop:
		LDA GenPtr42LB		  ;($EF3C)
		STA PalettePointerLB	;($EF3E)Copy red flash palette pointer to the working palette pointer.
		LDA GenPtr42UB		  ;($EF40)
		STA PalettePointerUB	;($EF42)

		JSR WaitForNMI		  ;($EF44)($FF74)
		JSR WaitForNMI		  ;($EF47)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($EF4A)($FF74)

		LDA #$00				;($EF4D)Disable fade-in/fade-out.
		STA PalModByte		  ;($EF4F)

		JSR PrepSPPalLoad	   ;($EF51)($C632)Load sprite palette data into PPU buffer.

		LDA EnemyNumber		 ;($EF54)Is the player fighting the end boss?
		CMP #EN_DRAGONLORD2	 ;($EF56)
		BNE +				   ;($EF58)If not, branch.

		LDA FnlRedBGPalPtr	  ;($EF5A)
		STA PalettePointerLB	;($EF5D)Red flash the background palette for the end boss.
		LDA FnlRedBGPalPtr+1	;($EF5F)
		STA PalettePointerUB	;($EF62)

		JSR PrepBGPalLoad	   ;($EF64)($C63D)Load background palette data into PPU buffer

		* JSR WaitForNMI		;($EF67)($FF74)Wait for VBlank interrupt.
		JSR WaitForNMI		  ;($EF6A)($FF74)

		LDA GenPtr42LB		  ;($EF6D)
		PHA					 ;($EF6F)Save pointer to red flash palette on stack.
		LDA GenPtr42UB		  ;($EF70)
		PHA					 ;($EF72)

		JSR LoadEnPalette	   ;($EF73)($EEFD)Load enemy palette data.

		PLA					 ;($EF76)
		STA GenPtr42UB		  ;($EF77)Restore pointer to red flash palette from stack.
		PLA					 ;($EF79)
		STA GenPtr42LB		  ;($EF7A)

		LDA #$00				;($EF7C)Disable fade-in/fade-out.
		STA PalModByte		  ;($EF7E)

		JSR PrepSPPalLoad	   ;($EF80)($C632)Load sprite palette data into PPU buffer.

		LDA EnemyNumber		 ;($EF83)Is the player fighting the end boss?
		CMP #EN_DRAGONLORD2	 ;($EF85)
		BNE +				   ;($EF87)If not, branch.

		LDA FnlNormBGPalPtr	 ;($EF89)
		STA PalettePointerLB	;($EF8C)Restore the normal background palette for the end boss.
		LDA FnlNormBGPalPtr+1   ;($EF8E)
		STA PalettePointerUB	;($EF91)

		JSR PrepBGPalLoad	   ;($EF93)($C63D)Load background palette data into PPU buffer

		* DEC PaletteFlashCounter;($EF96)Does the palette need to be flashed again?
		BNE PalFlashLoop		;($EF98)
		RTS					 ;($EF9A)If so, branch to flash again.

FnlRedBGPalPtr:
		.word FinalRedBGPal	 ;($EF9B)Pointer to BG palette red flash for end boss.

FnlNormBGPalPtr:
		.word FinalNormBGPal	;($EF9D)Pointer to BG plaette normal colors for end boss.

;The following palettes are for the end boss. The background is supposed to flash red when
;the end boss is hit. The only problem is there is no background on the final boss. Maybe
;at one time there was a background but it was cut from the final game.

FinalRedBGPal:
		.byte $30, $0E, $30, $16, $16, $16, $16, $16, $16, $16, $16, $16;($EF9F)

FinalNormBGPal:
		.byte $30, $0E, $30, $17, $15, $30, $21, $22, $27, $0F, $27, $27;($EFAB)

;----------------------------------------------------------------------------------------------------

CheckEnRun:
		LDA DisplayedStr		;($EFB7)Is player's strength at least double the enemy's attack?
		LSR					 ;($EFB9)
		CMP EnBaseAtt		   ;($EFBA)
		BCC EnRunExit		   ;($EFBD)If not, branch. Enemy will not run.

		JSR UpdateRandNum	   ;($EFBF)($C55B)Get random number.
		LDA RandomNumberUB	  ;($EFC2)
		AND #$03				;($EFC4)Player is very strong. 25% chance enemy will run.
		BNE EnRunExit		   ;($EFC6)

		JSR ClearSpriteRAM	  ;($EFC8)($C6BB)Clear sprite RAM.

		LDA #SFX_RUN			;($EFCB)Run away SFX.
		BRK					 ;($EFCD)
		.byte $04, $17		  ;($EFCE)($81A0)InitMusicSFX, bank 1.

		JSR CopyEnUpperBytes	;($EFD0)($DBE4)Copy enemy upper bytes to description RAM.

		JSR DoDialogLoBlock	 ;($EFD3)($C7CB)The enemy is running away.
		.byte $E3			   ;($EFD6)TextBlock15, entry 3.

		LDX MapNumber		   ;($EFD7)Get current map number.
		LDA ResumeMusicTbl,X	;($EFD9)Use current map number to resume music.
		BRK					 ;($EFDC)
		.byte $04, $17		  ;($EFDD)($81A0)InitMusicSFX, bank 1.

		PLA					 ;($EFDF)Pull return address from stack and exit to map.
		PLA					 ;($EFE0)
		JMP ExitFight		   ;($EFE1)($EE54)Return to map after fight.

EnRunExit:
		RTS					 ;($EFE4)Enemy did not run away. Return.

;----------------------------------------------------------------------------------------------------

PlayerCalcHitDmg:
		LSR DefenseStat		 ;($EFE5)
		LDA AttackStat		  ;($EFE7)
		SEC					 ;($EFE9) A = AttackStat - DefenseStat/2.
		SBC DefenseStat		 ;($EFEA)
		BCC PlayerWeakAttack	;($EFEC)

		CMP #$02				;($EFEE)Did A go negative or is only 1 greater than enemy defense/2?
		BCS NormalAttack		;($EFF0)If so, branch to do a weak attack. enemy is strong!
		BCC PlayerWeakAttack	;($EFF2)Else branch to do a normal attack.

EnCalcHitDmg:
		LSR DefenseStat		 ;($EFF4)
		LDA AttackStat		  ;($EFF6)
		LSR					 ;($EFF8)A = AttackStat - DefenseStat/2.
		STA MultiplyNumber2LB   ;($EFF9)
		INC MultiplyNumber2LB   ;($EFFB)
		LDA AttackStat		  ;($EFFD)Save a compy of AttackStat/2.
		SEC					 ;($EFFF)
		SBC DefenseStat		 ;($F000)
		BCC +				   ;($F002)Enemy will do a weak attack if player is much stronger.

		CMP MultiplyNumber2LB   ;($F004)Is enemy AttackStat more than 2X player DefenseStat?
		BCS NormalAttack		;($F006)If so, branch to do normal attack damage.

		* JSR UpdateRandNum	 ;($F008)($C55B)Get random number.
		LDA RandomNumberUB	  ;($F00B)
		STA MultiplyNumber1LB   ;($F00D)
		LDA #$00				;($F00F)A = A * rnd(255).
		STA MultiplyNumber1UB   ;($F011)
		STA MultiplyNumber2UB   ;($F013)
		JSR WordMultiply		;($F015)($C1C9)Multiply 2 16-bit words.

		LDA MultiplyResultUB	;($F018)
		CLC					 ;($F01A)A = (A/256+2)/3.
		ADC #$02				;($F01B)
		STA DivideNumber1LB	 ;($F01D)Total equation for weak enemy attack:
		LDA #$03				;($F01F)Damage=(((AttackStat-DefenseStat/2)*rnd(255))/256+2)/3.
		STA DivideNumber2	   ;($F021)
		JMP ByteDivide		  ;($F023)($C1F0)Divide a 16-bit number by an 8-bit number.

PlayerWeakAttack:
		JSR UpdateRandNum	   ;($F026)($C55B)Get random number.

		LDA RandomNumberUB	  ;($F029)
		AND #$01				;($F02B)Player is too weak to fight this enemy. 50% chance
		STA CalcDamage		  ;($F02D)of doing 1 point of damage or 50% chance of missing.
		RTS					 ;($F02F)

NormalAttack:
		STA BaseAttack		  ;($F030)
		STA MultiplyNumber2LB   ;($F032)A = A+1.
		INC MultiplyNumber2LB   ;($F034)
		JSR UpdateRandNum	   ;($F036)($C55B)Get random number.

		LDA RandomNumberUB	  ;($F039)
		STA MultiplyNumber1LB   ;($F03B)
		LDA #$00				;($F03D)A = rand(0-255) * A.
		STA MultiplyNumber1UB   ;($F03F)
		STA MultiplyNumber2UB   ;($F041)
		JSR WordMultiply		;($F043)($C1C9)Multiply 2 16-bit words.

		LDA MultiplyResultUB	;($F046)A = (A/256 + BaseAttack) / 4.
		CLC					 ;($F048)
		ADC BaseAttack		  ;($F049)
		ROR					 ;($F04B)Total equation for normal attack damage:
		LSR					 ;($F04C)Damage=(((AttackStat+1-DefenseStat/2)*rnd(255))/256+BaseAttack)/4.
		STA CalcDamage		  ;($F04D)
		RTS					 ;($F04F)

;----------------------------------------------------------------------------------------------------

LoadStats:
		LDX #LVL_TBL_LAST	   ;($F050)Point to level 30 in LevelUpTbl.
		LDA #LEVEL_30		   ;($F052)
		STA DisplayedLevel	  ;($F054)Set displayed level to 30.

GetLevelLoop:
		LDA ExpLB			   ;($F056)
		SEC					 ;($F058)
		SBC LevelUpTbl,X		;($F059)
		LDA ExpUB			   ;($F05C)Get current experience and subtract the values in LevelUpTbl
		SBC LevelUpTbl+1,X	  ;($F05E)If the value goes negative, then the player's current level
		BCS LevelFound		  ;($F061)has been found.  Keep looping until the player's current
		DEC DisplayedLevel	  ;($F063)level is determined.
		DEX					 ;($F065)
		DEX					 ;($F066)
		BNE GetLevelLoop		;($F067)

LevelFound:
		LDA DisplayedLevel	  ;($F069)
		SEC					 ;($F06B)Subtract 1 from level as index into table starts at 0.
		SBC #$01				;($F06C)

		ASL					 ;($F06E)Index*2.
		STA LevelDataPointer	;($F06F)
		ASL					 ;($F071)Index*4.
		CLC					 ;($F072)
		ADC LevelDataPointer	;($F073)Final table pointer = 2*(level-1)+4*(level-1).
		STA LevelDataPointer	;($F075)6 bytes per table entry.

		LDA #$FF				;($F077)Indicate not in VBlank.
		STA NMIStatusus		 ;($F079)

		* JSR WaitForNMI		;($F07B)($FF74)Wait for VBlank interrupt.
		LDA NMIStatusus		 ;($F07E)
		BNE -				   ;($F080)Wait for VBlank to end before continuing.

		BRK					 ;($F082)Get player's base stats for their level.
		.byte $0D, $17		  ;($F083)($99B4)SetBaseStats, bank 1.

		LDX #$04				;($F085)Prepare to get lower 4 characers of name.
		LDA #$00				;($F087)Prepare to add their numerical values together.

NameAddLoop:
		CLC					 ;($F089)Add the 4 values of the name characters together.
		.byte $7D, $B4, $00	 ;($F08A)ADC $00B4,X. Assembling as ADC $B4,X. Replaced with binary.
		DEX					 ;($F08D)Have all 4 characters been added together?
		BNE NameAddLoop		 ;($F08E)If not, loop to add another one.

		STA StatBonus		   ;($F090)Save off total value for later.
		AND #$03				;($F092)
		STA StatPenalty		 ;($F094)Get 2 LSBs for stat penalty calculations.

		LDA StatBonus		   ;($F096)
		LSR					 ;($F098)Get bits 2 and 3 for stat bonus calculations and
		LSR					 ;($F099)move them to bits 0 and 1.
		AND #$03				;($F09A)
		STA StatBonus		   ;($F09C)

		LDA StatPenalty		 ;($F09E)If LSB is set, penalize max MP.
		LSR					 ;($F0A0)
		BCS MaxMPPenalty		;($F0A1)Penalize max MP? If so, branch.

		LDA DisplayedStrength   ;($F0A3)Penalize strength by 10%.
		JSR ReduceStat		  ;($F0A5)($F10C)Multiply stat by 9/10.
		STA DisplayedStrength   ;($F0A8)

		JMP ChkAgiPenalty	   ;($F0AA)Check agility, max HP penalties.

MaxMPPenalty:
		LDA DisplayedMaxMP	  ;($F0AD)Only penalize MP if player has any MP to penalize.
		BEQ ChkAgiPenalty	   ;($F0AF)

		JSR ReduceStat		  ;($F0B1)($F10C)Multiply stat by 9/10.
		STA DisplayedMaxMP	  ;($F0B4)Penalize max MP.

ChkAgiPenalty:
		LDA StatPenalty		 ;($F0B6)if bit 1 is set, penalize agility.
		AND #$02				;($F0B8)
		BNE MaxHPPenalty		;($F0BA)Penalize max HP? If so, branch.

		LDA DisplayedAgility	;($F0BC)Penalize agility by 10%.
		JSR ReduceStat		  ;($F0BE)($F10C)Multiply stat by 9/10.
		STA DisplayedAgility	;($F0C1)

		JMP AddItemBonuses	  ;($F0C3)($F0CD)Add bonuses for player's equipped items.

MaxHPPenalty:
		LDA DisplayedMaxHP	  ;($F0C6)Penalize max HP.
		JSR ReduceStat		  ;($F0C8)($F10C)Multiply stat by 9/10.
		STA DisplayedMaxHP	  ;($F0CB)

AddItemBonuses:
		LDA EqippedItems		;($F0CD)Get equipped items.
		LSR					 ;($F0CF)
		LSR					 ;($F0D0)
		LSR					 ;($F0D1)Shift weapons down to lower 3 bits.
		LSR					 ;($F0D2)
		LSR					 ;($F0D3)

		TAX					 ;($F0D4)Use the 3 bits above as index into the WeaponsBonusTable.
		LDA WeaponsBonusTable,X ;($F0D5)

		CLC					 ;($F0D8)
		ADC DisplayedStrength   ;($F0D9)Add bonus from weapons table to strength attribute.
		STA DisplayedAttack	 ;($F0DB)

		LDA DisplayedAgility	;($F0DD)
		LSR					 ;($F0DF)Divide agility by 2 and add to defense attribute.
		STA DisplayedDefense	;($F0E0)

		LDA EqippedItems		;($F0E2)Get equipped armor and move to lower 3 bits.
		LSR					 ;($F0E4)
		LSR					 ;($F0E5)
		AND #AR_ARMOR/4		 ;($F0E6)Remove weapon bits.

		TAX					 ;($F0E8)Use the 3 bits above as index into the ArmorBonusTable.
		LDA ArmorBonusTable,X   ;($F0E9)

		CLC					 ;($F0EC)
		ADC DisplayedDefense	;($F0ED)Add bonus from armor table to defense attribute.
		STA DisplayedDefense	;($F0EF)

		LDA EqippedItems		;($F0F1)Mask off shield bits.
		AND #SH_SHIELDS		 ;($F0F3)

		TAX					 ;($F0F5)Use the 2 bits above as index into the ShieldBonusTable.
		LDA ShieldBonusTable,X  ;($F0F6)

		CLC					 ;($F0F9)
		ADC DisplayedDefense	;($F0FA)Add bonus from shield table to defense attribute.
		STA DisplayedDefense	;($F0FC)

		LDA ModsnSpells		 ;($F0FE)Is dragon's scale equipped?
		AND #F_DRGSCALE		 ;($F100)
		BEQ +				   ;($F102)If not, branch to exit.

		LDA DisplayedDefense	;($F104)
		CLC					 ;($F106)
		ADC #$02				;($F107)Dragon's scale equipped. Add 2 to defense.
		STA DisplayedDefense	;($F109)
		* RTS				   ;($F10B)

;----------------------------------------------------------------------------------------------------

;The name of the character is critical in determining how the stats are penalized.  There are two
;pairs of stats that will always be penalized.  If a character has normal strength growth, then their
;max MP will be penalized by 10%.  The opposite is true: if a character has normal MP growth, then
;their strength will be penalized by 10%.  The other pair of stats is agility and max HP.  If agility
;has normal growth, the max HP will be penalized by 10% and vice versa.  The important thing to take
;away is that two stats will always be penalized while the other two are not.  A bonus of 0 to 3
;points will be added to the 2 penalized stats.  This gives the effect of having the penalized stat
;slightly stronger at the beginning of the game but becomes weaker as the player progresses levels.
;
;Only the first 4 letters in the name are used for the stat penalties and bonus calculations. Here
;is how it works:
;
;The numeric value of the first four letters of the name are added together.  the following
;is a list of the numeric values of the characters:
;A=$24, B=$25, C=$26, D=$27, E=$28, F=$29, G=$2A, H=$2B, I=$2C, J=$2D,
;K=$2E, L=$2F, M=$30, N=$31, O=$32, P=$33, Q=$34, R=$35, S=$36, T=$37,
;U=$38, V=$39, W=$3A, X=$3B, Y=$3C, Z=$3D, -=$49, '=$40, !=$4C, ?=$4B,
;(=$4F, )=$4E, a=0A$, b=$0B, c=$0C, d=$0D, e=$0E, f=$0F, g=$10, h=$11,
;i=$12, j=$13, k=$14, l=$15, m=$16, n=$17, o=$18, p=$19, q=$1A, r=$1B,
;s=$1C, t=$1D, u=$1E, v=$1F, w=$20, x=$21, y=$22, z=$23, ,=$48, .=$47,
;space=$60
;
;Bits 0 and 1 are used to determine the stat penalties. Bits 2 and 3 are the stats bonus.
;
;If bit 0 is clear, strength is penalized by 10%. If bit 0 is set, max MP is penalized by 10%.
;if bit 1 is clear, agility is penalized by 10%. If bit 1 is set, max HP is penalized by 10%.
;
;Bits 2 and 3 are shifted down to bits 0 and 1 and added to the penalized stats.
;
;Some examples:
;JAKE = $2D+$24+$2E+$28 = $A7. Max MP penalized, max HP penalized, +1 added to max MP, HP.
;Deez = $27+$0E+$0E+$23 = $66. Strength penalized, max HP penalized, +1 added to strength, max HP.
;
;The best combination would be to have the lowest 4 bits be 1111. This would reduce max HP and MP
;but give a bonus of 3 points to each. Strength and agility would have normal growth.

ReduceStat:
		STA MultiplyNumber1LB   ;($F10C)
		LDA #$09				;($F10E)
		STA MultiplyNumber2LB   ;($F110)
		LDA #$00				;($F112)Multiply stat by 9.
		STA MultiplyNumber1UB   ;($F114)
		STA MultiplyNumber2UB   ;($F116)
		JSR WordMultiply		;($F118)($C1C9)Multiply 2 16-bit words.

		LDA MultiplyResultLB	;($F11B)
		STA DivideNumber1LB	 ;($F11D)Save results of multiplication.
		LDA MultiplyResultUB	;($F11F)
		STA DivideNumber1UB	 ;($F121)

		LDA #$0A				;($F123)prepare to Divide stat by 10.
		STA DivideNumber2	   ;($F125)
		LDA #$00				;($F127)
		STA DivideNumber2NU	 ;($F129)
		JSR WordDivide		  ;($F12B)($C1F4)Divide a 16-bit word by an 8-bit byte.
		LDA DivideQuotient	  ;($F12E)Net result is stat*9/10.

		CLC					 ;($F130)Add in any stat bonus that may have been calculated.
		ADC StatBonus		   ;($F131)Stat bonus may be in the range of 0-3.
		RTS					 ;($F133)

;----------------------------------------------------------------------------------------------------

GetExperienceRemaining:
		LDA DisplayedLevel	  ;($F134)Get player's current level.
		ASL					 ;($F136)*2
		TAX					 ;($F137)
		LDA LevelUpTbl,X		;($F138)
		SEC					 ;($F13B)
		SBC ExpLB			   ;($F13C)Subtract current experience from value in table
		STA GenWrd00LB		  ;($F13E)to get remaining experience until level up.
		LDA LevelUpTbl+1,X	  ;($F140)
		SBC ExpUB			   ;($F143)
		STA GenWrd00UB		  ;($F145)
		RTS					 ;($F147)

;----------------------------------------------------------------------------------------------------

PrepSaveGame:
		LDA #$01				;($F148)Wait for PPU buffer to be completely empty.
		JSR WaitForPPUBufferSpace;($F14A)($C587)Wait for space in PPU buffer.
		JMP SaveCurrentGame	 ;($F14D)($F9DF)Save current game.

;----------------------------------------------------------------------------------------------------

		.word DescTable+1	   ;($F150)($F155)Unused pointer into table below.

DescTblPtr:
		.word DescTable		 ;($F152)($F154)Pointer into table below.

DescTable:

;Unused.
		.byte $FA, $55, $62, $FA, $41, $4E, $40, $62, $FA, $FA, $40, $47, $F8, $6B, $4E, $4D;($F154)
		.byte $FA, $0C, $35, $14, $1C, $F8, $23, $FA, $2F, $0C, $13, $18, $FA, $0A, $38, $19;($F164)
		.byte $FA, $4C, $F8, $40, $4A, $22, $23, $0F, $FA, $1B, $19, $0D, $1C, $11, $33, $FA;($F174)
		.byte $42, $4D, $42, $4E, $40, $FA, $31, $4D, $43, $47, $F8, $4E, $43, $FA, $28, $16;($F184)
		.byte $4F, $FA, $15, $F8, $39, $4F, $FA, $1C, $F8, $16, $0F, $60, $FA, $28, $16, $0F;($F194)
		.byte $60, $FA, $13, $F8, $14, $F8, $0B, $28, $16, $4F, $FA, $00, $FA, $00, $FA;($F1A4)

		.byte DSC_SCRT_PSG,	  TXT_SUBEND;($F1B3)Secret passage text.
		.byte DSC_HEAL-$13,	  TXT_SUBEND;($F1B5)Heal spell text.
		.byte DSC_HURT-$13,	  TXT_SUBEND;($F1B7)Hurt spell text.
		.byte DSC_SLEEP-$13,	 TXT_SUBEND;($F1B9)Sleep spell text.
		.byte DSC_RADIANT-$13,   TXT_SUBEND;($F1BB)Radiant spell text.
		.byte DSC_STOPSPELL-$13, TXT_SUBEND;($F1BD)Stopspell spell text.
		.byte DSC_OUTSIDE-$13,   TXT_SUBEND;($F1BF)Outside spell text.
		.byte DSC_RETURN-$13,	TXT_SUBEND;($F1C1)Return spell text.
		.byte DSC_REPEL-$13,	 TXT_SUBEND;($F1C3)Repel spell text.
		.byte DSC_HEALMORE-$13,  TXT_SUBEND;($F1C5)Healmore spell text.
		.byte DSC_HURTMORE-$13,  TXT_SUBEND;($F1C7)Hurtmore spell text.

;Unused.
		.byte $44, $26, $F8, $43, $FA;($F1C9)

		.byte DSC_BMB_POLE,	  TXT_SUBEND;($F1CE)Bamboo pole text.
		.byte DSC_CLUB,		  TXT_SUBEND;($F1D0)Club text.
		.byte DSC_CPR_SWD,	   TXT_SUBEND;($F1D2)Copper sword text.
		.byte DSC_HND_AXE,	   TXT_SUBEND;($F1D4)Hand axe text.
		.byte DSC_BROAD_SWD,	 TXT_SUBEND;($F1D6)Broad sword text.
		.byte DSC_FLAME_SWD,	 TXT_SUBEND;($F1D8)Flame sword text.
		.byte DSC_ERD_SWD,	   TXT_SUBEND;($F1DA)Erdrick's sword text.
		.byte DSC_CLOTHES,	   TXT_SUBEND;($F1DC)Clothes text.
		.byte DSC_LTHR_ARMR,	 TXT_SUBEND;($F1DE)Leather armor text.
		.byte DSC_CHAIN_ML,	  TXT_SUBEND;($F1E0)Chain mail text.
		.byte DSC_HALF_PLT,	  TXT_SUBEND;($F1E2)Half plate text.
		.byte DSC_FULL_PLT,	  TXT_SUBEND;($F1E4)Full plate text.
		.byte DSC_MAG_ARMR,	  TXT_SUBEND;($F1E6)Magic armor text.
		.byte DSC_ERD_ARMR,	  TXT_SUBEND;($F1E8)Erdrick's armor text.
		.byte DSC_SM_SHLD,	   TXT_SUBEND;($F1EA)Small shield text.
		.byte DSC_LG_SHLD,	   TXT_SUBEND;($F1EC)Large shield text.
		.byte DSC_SLVR_SHLD,	 TXT_SUBEND;($F1EE)Silver shield text.

;Unused.
		.byte $3C, $5F, $5F, $25, $F8, $10, $58, $FA, $3C, $5F, $2F, $34, $0B, $58, $FA, $28;($F1F0)
		.byte $13, $1D, $22, $5F, $FA, $41, $6B, $22, $5F, $1A, $36, $24, $11, $FA;($F200)

		.byte DSC_HERB,		  TXT_SUBEND;($F20E)Herb text.
		.byte DSC_KEY,		   TXT_SUBEND;($F210)Magic key text.
		.byte DSC_TORCH,		 TXT_SUBEND;($F212)Torch text.
		.byte DSC_FRY_WATER,	 TXT_SUBEND;($F214)Fairy water text.
		.byte DSC_WINGS,		 TXT_SUBEND;($F216)Wings text.
		.byte DSC_DRGN_SCL,	  TXT_SUBEND;($F218)Dragon's scale text.
		.byte DSC_FRY_FLUTE,	 TXT_SUBEND;($F21A)Fairy flute text.
		.byte DSC_FGHTR_RNG,	 TXT_SUBEND;($F21C)Fighter's ring text.
		.byte DSC_ERD_TKN,	   TXT_SUBEND;($F21E)Erdrick's token text.
		.byte DSC_GWLN_LOVE,	 TXT_SUBEND;($F220)Gwaelin's love text.
		.byte DSC_CRSD_BLT,	  TXT_SUBEND;($F222)Cursed belt text.
		.byte DSC_SLVR_HARP,	 TXT_SUBEND;($F224)Silver harp text.
		.byte DSC_DTH_NCK,	   TXT_SUBEND;($F226)Death necklace text.
		.byte DSC_STN_SUN,	   TXT_SUBEND;($F228)Stones of sunlight text.
		.byte DSC_RN_STAFF,	  TXT_SUBEND;($F22A)Staff of rain text.
		.byte DSC_RNBW_DRP,	  TXT_SUBEND;($F22C)Rainbow drop text.

;Unused.
		.byte $15, $0F, $15, $FA, $15, $F8, $3A, $2C, $37, $FA, $0A, $1E, $19, $FA, $28, $19;($F22E)
		.byte $F8, $FA, $18, $33, $0B, $15, $F8, $3B, $0C, $FA, $2C, $1C, $28, $17, $37, $0F;($F23E)
		.byte $F8, $6C, $FA, $0E, $0F, $21, $0F, $F8, $5F, $19, $31, $28, $17, $37, $0F, $F8;($F24E)
		.byte $6C, $FA, $1E, $1F, $0F, $FA, $1D, $F8, $33, $36, $FA, $1E, $1F, $36, $FA, $1C;($F25E)
		.byte $1F, $0B, $33, $19, $FA, $29, $1B, $12, $19, $FA, $35, $19, $15, $FA, $41, $4E;($F26E)
		.byte $40, $FA, $24, $2B, $FA, $1C, $F8, $16, $4F, $FA, $0A, $2B, $1D, $5F, $19, $0B;($F27E)
		.byte $2F, $0C, $0F, $F8, $5F, $0A, $35, $14, $32, $FA, $19, $16, $12, $19, $F8, $15;($F28E)
		.byte $1C, $FA, $13, $F8, $14, $F8, $0B, $28, $16, $FA, $11, $19, $F8, $14, $0B, $FA;($F29E)
		.byte $14, $28, $FA, $0E, $0C, $14, $28, $FA, $13, $13, $23, $FA, $18, $1E, $19, $FA;($F2AE)
		.byte $0A, $30, $35, $33, $FA, $0F, $F8, $2F, $0B, $52, $FA, $1D, $F8, $0C, $0F, $FA;($F2BE)
		.byte $2E, $0C, $15, $39, $FA, $23, $16, $F8, $FA, $14, $0F, $F8, $16, $FA, $0A, $32;($F2CE)
		.byte $30, $15, $0B, $FA, $1D, $F8, $13, $0F, $1F, $FA, $24, $1B, $2F, $0C, $FA, $0E;($F2DE)
		.byte $28, $0D, $FA, $0E, $15, $34, $FA, $25, $32, $0B, $5F, $0B, $0B, $1B, $19, $0D;($F2EE)
		.byte $FA, $28, $1A, $FA, $28, $2C, $22, $19, $1A, $FA, $0A, $31, $0F, $F8, $1D, $0C;($F2FE)
		.byte $FA, $0F, $F8, $FA, $10, $F8, $FA, $11, $F8, $FA, $12, $F8, $FA, $13, $F8, $FA;($F30E)
		.byte $14, $F8, $FA, $15, $F8, $FA, $16, $F8, $FA, $17, $F8, $FA, $18, $F8, $FA, $19;($F31E)
		.byte $F8, $FA, $1A, $F8, $FA, $1B, $F8, $FA, $1C, $F8, $FA, $1D, $F8, $FA, $23, $F8;($F32E)
		.byte $FA, $24, $F8, $FA, $25, $F8, $FA, $26, $F8, $FA, $27, $F8, $FA, $23, $F9, $FA;($F33E)
		.byte $24, $F9, $FA, $25, $F9, $FA, $26, $F9, $FA, $27, $F9, $FA, $FA;($F34E)

;----------------------------------------------------------------------------------------------------

LevelUpTbl:
		.word $0000			 ;($F35B)Level 1  - 0	 exp.
		.word $0007			 ;($F35D)Level 2  - 7	 exp.
		.word $0017			 ;($F35F)Level 3  - 23	exp.
		.word $002F			 ;($F361)Level 4  - 47	exp.
		.word $006E			 ;($F363)Level 5  - 110   exp.
		.word $00DC			 ;($F365)Level 6  - 220   exp.
		.word $01C2			 ;($F367)Level 7  - 450   exp.
		.word $0320			 ;($F369)Level 8  - 800   exp.
		.word $0514			 ;($F36B)Level 9  - 1300  exp.
		.word $07D0			 ;($F36D)Level 10 - 2000  exp.
		.word $0B54			 ;($F36F)Level 11 - 2900  exp.
		.word $0FA0			 ;($F371)Level 12 - 4000  exp.
		.word $157C			 ;($F373)Level 13 - 5500  exp.
		.word $1D4C			 ;($F375)Level 14 - 7500  exp.
		.word $2710			 ;($F377)Level 15 - 10000 exp.
		.word $32C8			 ;($F379)Level 16 - 13000 exp.
		.word $3E80			 ;($F37B)Level 17 - 16000 exp.
		.word $4A38			 ;($F37D)Level 18 - 19000 exp.
		.word $55F0			 ;($F37F)Level 19 - 22000 exp.
		.word $6590			 ;($F381)Level 20 - 26000 exp.
		.word $7530			 ;($F383)Level 21 - 30000 exp.
		.word $84D0			 ;($F385)Level 22 - 34000 exp.
		.word $9470			 ;($F387)Level 23 - 38000 exp.
		.word $A410			 ;($F389)Level 24 - 42000 exp.
		.word $B3B0			 ;($F38B)Level 25 - 46000 exp.
		.word $C350			 ;($F38D)Level 26 - 50000 exp.
		.word $D2F0			 ;($F38F)Level 27 - 54000 exp.
		.word $E290			 ;($F391)Level 28 - 58000 exp.
		.word $F230			 ;($F393)Level 29 - 62000 exp.
		.word $FFFF			 ;($F395)Level 30 - 65535 exp.

;----------------------------------------------------------------------------------------------------

;This table is used to place the combat background on the screen when a fight starts.  It lays
;the graphic blocks out in a spiral fashion.  The upper left corner of the background is considered
;coordinates 0,0.  The combat background is 14 by 14 tiles.  Each graphic block is 2x2 tiles. The
;upper nibble in the byte is the x position in the grid while the lower nibble is the y position.
;Since the first byte in the table is $66, this means the first block appears when the background
;at position 6,6 (the center of the background).  The next block appears at coordinates 6,8 (just
;below the first block).  Since each block is 2x2 tiles, they appear at even coordinates only.

CmbtBGPlcmntTbl:
		.byte $66, $68, $48, $46, $44, $64, $84, $86, $88, $8A, $6A, $4A, $2A, $28, $26, $24;($F397)
		.byte $22, $42, $62, $82, $A2, $A4, $A6, $A8, $AA, $AC, $8C, $6C, $4C, $2C, $0C, $0A;($F3A7)
		.byte $08, $06, $04, $02, $00, $20, $40, $60, $80, $A0, $C0, $C2, $C4, $C6, $C8, $CA;($F3B7)
		.byte $CC			   ;($F3C7)

;----------------------------------------------------------------------------------------------------

;This table contains data that links one map to another. The first byte is the current map number.
;The next two bytes are the x and y positions respectively on the current map that connect to the
;target map.  The coordinates are based on the upper left corner of the map and start at 0,0.

MapEntryTbl:
		.byte MAP_OVERWORLD,   $02, $02;($F3C8)Overworld(2,2)		  -> Garinham(0,14).
		.byte MAP_OVERWORLD,   $51, $01;($F3CB)Overworld(81,1)		 -> Staff of rain cave(4,9).
		.byte MAP_OVERWORLD,   $68, $0A;($F3CD)Overworld(104,10)	   -> Koll(19,23).
		.byte MAP_OVERWORLD,   $30, $29;($F3D1)Overworld(48,41)		-> Brecconary(0,15).
		.byte MAP_OVERWORLD,   $2B, $2B;($F3D4)Overworld(43,43)		-> Tant castle GF(11,29).
		.byte MAP_OVERWORLD,   $68, $2C;($F3D7)Overworld(104,44)	   -> Swamp cave(0,0).
		.byte MAP_OVERWORLD,   $30, $30;($F3DA)Overworld(48,48)		-> DL castle GF(10,19).
		.byte MAP_OVERWORLD,   $68, $31;($F3DD)Overworld(104,49)	   -> Swamp cave(0,29).
		.byte MAP_OVERWORLD,   $1D, $39;($F3E0)Overworld(29,57)		-> Rock mtn B1(0,7).
		.byte MAP_OVERWORLD,   $66, $48;($F3E3)Overworld(102,72)	   -> Rimuldar(29,14).
		.byte MAP_OVERWORLD,   $19, $59;($F3E6)Overworld(25,89)		-> Hauksness(0,10).
		.byte MAP_OVERWORLD,   $49, $66;($F3E9)Overworld(73,102)	   -> Cantlin(15,0).
		.byte MAP_OVERWORLD,   $6C, $6D;($F3EC)Overworld(108,109)	  -> Rnbw drp cave(0,4).
		.byte MAP_OVERWORLD,   $1C, $0C;($F3EF)Overworld(28,12)		-> Erdrick cave B1(0,0).
		.byte MAP_DLCSTL_GF,   $0A, $01;($F3F2)DL castle GF(10,1)	  -> DL castle SL1(9,0).
		.byte MAP_DLCSTL_GF,   $04, $0E;($F3F5)DL castle GF(4,14)	  -> DL castle SL1(8,13).
		.byte MAP_DLCSTL_GF,   $0F, $0E;($F3F8)DL castle GF(15,14)	 -> DL castle SL1(17,15).
		.byte MAP_TANTCSTL_GF, $1D, $1D;($F3FB)Tant castle GF(29,29)   -> Tant castle SL(0,4).
		.byte MAP_THRONEROOM,  $08, $08;($F3FE)Throneroom(8,8)		 -> Tant castle GF(7,7).
		.byte MAP_GARINHAM,	$13, $00;($F401)Garinham(19,0)		  -> Garinham cave B1(6,11).
		.byte MAP_DLCSTL_SL1,  $0F, $01;($F404)DL castle SL1(15,1)	 -> DL castle SL2(8,0).
		.byte MAP_DLCSTL_SL1,  $0D, $07;($F407)DL castle SL1(13,7)	 -> DL castle SL2(4,4).
		.byte MAP_DLCSTL_SL1,  $13, $07;($F40A)DL castle SL1(19,7)	 -> DL castle SL2(9,8).
		.byte MAP_DLCSTL_SL1,  $0E, $09;($F40D)DL castle SL1(14,9)	 -> DL castle SL2(8,9).
		.byte MAP_DLCSTL_SL1,  $02, $0E;($F410)DL castle SL1(2,14)	 -> DL castle SL2(0,1).
		.byte MAP_DLCSTL_SL1,  $02, $04;($F413)DL castle SL1(2,4)	  -> DL castle SL2(0,0).
		.byte MAP_DLCSTL_SL1,  $08, $13;($F416)DL castle SL1(8,19)	 -> DL castle SL2(5,0).
		.byte MAP_DLCSTL_SL2,  $03, $00;($F419)DL castle SL2(3,0)	  -> DL castle SL3(7,0).
		.byte MAP_DLCSTL_SL2,  $09, $01;($F41C)DL castle SL2(9,1)	  -> DL castle SL3(2,2).
		.byte MAP_DLCSTL_SL2,  $00, $08;($F41F)DL castle SL2(0,8)	  -> DL castle SL3(5,4).
		.byte MAP_DLCSTL_SL2,  $01, $09;($F422)DL castle SL2(1,9)	  -> DL castle SL3(0,9).
		.byte MAP_DLCSTL_SL3,  $01, $06;($F425)DL castle SL3(1,6)	  -> DL castle SL4(0,9).
		.byte MAP_DLCSTL_SL3,  $07, $07;($F428)DL castle SL3(7,7)	  -> DL castle SL4(7,7).
		.byte MAP_DLCSTL_SL4,  $02, $02;($F42B)DL castle SL4(2,2)	  -> DL castle SL5(9,0).
		.byte MAP_DLCSTL_SL4,  $08, $01;($F42E)DL castle SL4(8,1)	  -> DL castle SL5(4,0).
		.byte MAP_DLCSTL_SL5,  $05, $05;($F431)DL castle SL5(5,5)	  -> DL castle SL6(0,0).
		.byte MAP_DLCSTL_SL5,  $00, $00;($F434)DL castle SL5(0,0)	  -> DL castle SL6(0,6).
		.byte MAP_DLCSTL_SL6,  $09, $00;($F437)DL castle SL6(9,0)	  -> DL castle SL6(0,0).
		.byte MAP_DLCSTL_SL6,  $09, $06;($F43A)DL castle SL6(9,6)	  -> DL castle BF(10,29).
		.byte MAP_RCKMTN_B1,   $00, $00;($F43D)Rock mtn B1(0,0)		-> Rock mtn B2(0,0).
		.byte MAP_RCKMTN_B1,   $06, $05;($F440)Rock mtn B1(6,5)		-> Rock mtn B2(6,5).
		.byte MAP_RCKMTN_B1,   $0C, $0C;($F443)Rock mtn B1(12,12)	  -> Rock mtn B2(12,12).
		.byte MAP_CVGAR_B1,	$01, $12;($F446)Garinham cave B1(1,18)  -> Garinham cave B2(11,2).
		.byte MAP_CVGAR_B2,	$01, $01;($F449)Garinham cave B2(1,1)   -> Garinham cave B3(14,1).
		.byte MAP_CVGAR_B2,	$0C, $01;($F44C)Garinham cave B2(12,1)  -> Garinham cave B3(18,1).
		.byte MAP_CVGAR_B2,	$05, $06;($F44F)Garinham cave B2(5,6)   -> Garinham cave B3(6,11).
		.byte MAP_CVGAR_B2,	$01, $0A;($F452)Garinham cave B2(1,10)  -> Garinham cave B3(2,17).
		.byte MAP_CVGAR_B2,	$0C, $0A;($F455)Garinham cave B2(12,10) -> Garinham cave B3(18,13).
		.byte MAP_CVGAR_B3,	$09, $05;($F458)Garinham cave B3(9,5)   -> Garinham cave B4(0,4).
		.byte MAP_CVGAR_B3,	$0A, $09;($F45B)Garinham cave B3(10,9)  -> Garinham cave B4(5,4).
		.byte MAP_ERDRCK_B1,   $09, $09;($F45D)Erdrick cave B1(9,9)	-> Erdrick cave B2(8,9).

;This table is the same size as the table above and each entry is the destination from the exits
;above. Entry 1 in the table above corresponds to entry 1 in the table below. Stairs up use this
;table for the current map and use the table above for the destination.

MapTargetTbl:
		.byte MAP_GARINHAM,	$00, $0E;($F461)Garinham(0,14)		  <- Overworld(2,2)
		.byte MAP_RAIN,		$04, $09;($F465)Staff of rain cave(4,9) <- Overworld(81,1).
		.byte MAP_KOL,		 $13, $17;($F467)Koll(19,23)			 <- Overworld(104,10).
		.byte MAP_BRECCONARY,  $00, $0F;($F46A)Brecconary(0,15)		<- Overworld(48,41).
		.byte MAP_TANTCSTL_GF, $0B, $1D;($F46D)Tant castle GF(11,29)   <- Overworld(43,43).
		.byte MAP_SWAMPCAVE,   $00, $00;($F471)Swamp cave(0,0)		 <- Overworld(104,44).
		.byte MAP_DLCSTL_GF,   $0A, $13;($F473)DL castle GF(10,19)	 <- Overworld(48,48).
		.byte MAP_SWAMPCAVE,   $00, $1D;($F476)Swamp cave(0,29)		<- Overworld(104,49).
		.byte MAP_RCKMTN_B1,   $00, $07;($F479)Rock mtn B1(0,7)		<- Overworld(29,57).
		.byte MAP_RIMULDAR,	$1D, $0E;($F47C)Rimuldar(29,14)		 <- Overworld(102,72).
		.byte MAP_HAUKSNESS,   $00, $0A;($F47E)Hauksness(0,10)		 <- Overworld(25,89).
		.byte MAP_CANTLIN,	 $0F, $00;($F482)Cantlin(15,0)		   <- Overworld(73,102).
		.byte MAP_RAINBOW,	 $00, $04;($F485)Rnbw drp cave(0,4)	  <- Overworld(108,109).
		.byte MAP_ERDRCK_B1,   $00, $00;($F488)Erdrick cave B1(0,0)	<- Overworld(28,12).
		.byte MAP_DLCSTL_SL1,  $09, $00;($F48B)DL castle SL1(9,0)	  -> DL castle GF(10,1).
		.byte MAP_DLCSTL_SL1,  $08, $0D;($F48E)DL castle SL1(8,13)	 -> DL castle GF(4,14).
		.byte MAP_DLCSTL_SL1,  $11, $0F;($F491)DL castle SL1(17,15)	-> DL castle GF(15,14).
		.byte MAP_TANTCSTL_SL, $00, $04;($F494)Tant castle SL(0,4)	 -> Tant castle GF(29,29).
		.byte MAP_TANTCSTL_GF, $07, $07;($F497)Tant castle GF(7,7)	 -> Throneroom(8,8).
		.byte MAP_CVGAR_B1,	$06, $0B;($F49A)Garinham cave B1(6,11)  -> Garinham(19,0).
		.byte MAP_DLCSTL_SL2,  $08, $00;($F49D)DL castle SL2(8,0)	  -> DL castle SL1(15,1).
		.byte MAP_DLCSTL_SL2,  $04, $04;($F4A0)DL castle SL2(4,4)	  -> DL castle SL1(13,7).
		.byte MAP_DLCSTL_SL2,  $09, $08;($F4A3)DL castle SL2(9,8)	  -> DL castle SL1(19,7).
		.byte MAP_DLCSTL_SL2,  $08, $09;($F4A6)DL castle SL2(8,9)	  -> DL castle SL1(14,9).
		.byte MAP_DLCSTL_SL2,  $00, $01;($F4A9)DL castle SL2(0,1)	  -> DL castle SL1(2,14).
		.byte MAP_DLCSTL_SL2,  $00, $00;($F4AC)DL castle SL2(0,0)	  -> DL castle SL1(2,4).
		.byte MAP_DLCSTL_SL2,  $05, $00;($F4AF)DL castle SL2(5,0)	  -> DL castle SL1(8,19).
		.byte MAP_DLCSTL_SL3,  $07, $00;($F4B2)DL castle SL3(7,0)	  -> DL castle SL2(3,0).
		.byte MAP_DLCSTL_SL3,  $02, $02;($F4B5)DL castle SL3(2,2)	  -> DL castle SL2(9,1).
		.byte MAP_DLCSTL_SL3,  $05, $04;($F4B8)DL castle SL3(5,4)	  -> DL castle SL2(0,8).
		.byte MAP_DLCSTL_SL3,  $00, $09;($F4BB)DL castle SL3(0,9)	  -> DL castle SL2(1,9).
		.byte MAP_DLCSTL_SL4,  $00, $09;($F4BE)DL castle SL4(0,9)	  -> DL castle SL3(1,6).
		.byte MAP_DLCSTL_SL4,  $07, $07;($F4C1)DL castle SL4(7,7)	  -> DL castle SL3(7,7).
		.byte MAP_DLCSTL_SL5,  $09, $00;($F4C4)DL castle SL5(9,0)	  -> DL castle SL4(2,2).
		.byte MAP_DLCSTL_SL5,  $04, $00;($F4C7)DL castle SL5(4,0)	  -> DL castle SL4(8,1).
		.byte MAP_DLCSTL_SL6,  $00, $00;($F4CA)DL castle SL6(0,0)	  -> DL castle SL5(5,5).
		.byte MAP_DLCSTL_SL6,  $00, $06;($F4CD)DL castle SL6(0,6)	  -> DL castle SL5(0,0).
		.byte MAP_DLCSTL_SL6,  $00, $00;($F4D0)DL castle SL6(0,0)	  -> DL castle SL6(9,0).
		.byte MAP_DLCSTL_BF,   $0A, $1D;($F4D3)DL castle BF(10,29)	 -> DL castle SL6(9,6).
		.byte MAP_RCKMTN_B2,   $00, $00;($F4F6)Rock mtn B2(0,0)		-> Rock mtn B1(0,0).
		.byte MAP_RCKMTN_B2,   $06, $05;($F4D9)Rock mtn B2(6,5)		-> Rock mtn B1(6,5).
		.byte MAP_RCKMTN_B2,   $0C, $0C;($F4DC)Rock mtn B2(12,12)	  -> Rock mtn B1(12,12).
		.byte MAP_CVGAR_B2,	$0B, $02;($F4DF)Garinham cave B2(11,2)  -> Garinham cave B1(1,18).
		.byte MAP_CVGAR_B3,	$0E, $01;($F4E2)Garinham cave B3(14,1)  -> Garinham cave B2(1,1).
		.byte MAP_CVGAR_B3,	$12, $01;($F4E5)Garinham cave B3(18,1)  -> Garinham cave B2(12,1).
		.byte MAP_CVGAR_B3,	$06, $0B;($F4E8)Garinham cave B3(6,11)  -> Garinham cave B2(5,6).
		.byte MAP_CVGAR_B3,	$02, $11;($F4EB)Garinham cave B3(2,17)  -> Garinham cave B2(1,10).
		.byte MAP_CVGAR_B3,	$12, $0D;($F4EE)Garinham cave B3(18,13) -> Garinham cave B2(12,10).
		.byte MAP_CVGAR_B4,	$00, $04;($F4F1)Garinham cave B4(0,4)   -> Garinham cave B3(9,5).
		.byte MAP_CVGAR_B4,	$05, $04;($F4F4)Garinham cave B4(5,4)   -> Garinham cave B3(10,9).
		.byte MAP_ERDRCK_B2,   $08, $09;($F4F7)Erdrick cave B2(8,9)	-> Erdrick cave B1(9,9).

;----------------------------------------------------------------------------------------------------

;The following table is used during the random fight generation to determine if the player is
;strong enought to repel an enemy when the repel spell is active.  each entry in the table
;corresponds to an enemy and the index is the same as the enemy number. We can call each entry
;in the table the enemy's RepelVal.  The formula for figuring out if repel will work is as
;follows: IF [RepelVal - DisplayedDefense/2 < 0] OR [RepelVal/2 < (RepelVal - DisplayedDefense/2)]
;Then repel will be successful.

RepelTable:
		.byte $05, $07, $09, $0B, $0B, $0E, $12, $14, $12, $18, $16, $1C, $1C, $24, $28, $2C;($F4FA)
		.byte $0A, $28, $32, $2F, $34, $38, $3C, $44, $78, $30, $4C, $4E, $4F, $56, $58, $56;($F50A)
		.byte $50, $5E, $62, $64, $69, $78, $5A, $8C;($F51A)

;The following table dictates which random encounters occur in which part of the overworld map.
;The map is divided into an 8X8 grid.  Each nibble from the table below corresponds to a grid.
;The nibble corresponds to a row in the EnemyGroupsTbl below.

OvrWrldEnGrid:
		.byte $33, $22, $35, $45;($F522)
		.byte $32, $12, $33, $45;($F526)
		.byte $41, $00, $23, $45;($F52A)
		.byte $51, $1C, $66, $66;($F52E)
		.byte $55, $4C, $97, $77;($F532)
		.byte $A9, $8C, $CC, $87;($F536)
		.byte $AA, $BC, $DD, $98;($F53A)
		.byte $BB, $CD, $DC, $99;($F53E)

;The following table dictates what random encounters will happen in the dungeons. The indexes
;into the table correspond to the order of the caves starting with map number #$0F and ending
;with map number #$1B. Each byte corresponds to a row in the EnemyGroupsTbl below.

CaveEnIndexTbl:
		.byte $10, $11, $11, $11, $12, $12, $13, $13, $0E, $0E, $07, $0F, $0F;($F542)

;The following table controls the random enemy encounters.  Each dungeon or zone on the overworld
;map can have up to 5 different enemies to encounter.  Each row in the table represents those
;enemies.  The first 14 rows are the overworld enemies and correspond to nibbles in the
;OvrWrldEnGrid table.  The remaining entries are for the various dungeons as described above.

EnemyGroupsTbl:
		.byte EN_SLIME,	   EN_RSLIME,	  EN_SLIME,	   EN_RSLIME,	  EN_SLIME;($F54F)
		.byte EN_RSLIME,	  EN_SLIME,	   EN_RSLIME,	  EN_DRAKEE,	  EN_RSLIME;($F554)
		.byte EN_SLIME,	   EN_GHOST,	   EN_DRAKEE,	  EN_GHOST,	   EN_RSLIME;($F559)
		.byte EN_RSLIME,	  EN_RSLIME,	  EN_DRAKEE,	  EN_GHOST,	   EN_MAGICIAN;($F55E)
		.byte EN_GHOST,	   EN_MAGICIAN,	EN_MAGIDRAKE,   EN_MAGIDRAKE,   EN_SCORPION;($F563)
		.byte EN_GHOST,	   EN_MAGICIAN,	EN_MAGIDRAKE,   EN_SCORPION,	EN_SKELETON;($F568)
		.byte EN_MAGIDRAKE,   EN_SCORPION,	EN_SKELETON,	EN_WARLOCK,	 EN_WOLF;($F56D)
		.byte EN_SKELETON,	EN_WARLOCK,	 EN_MSCORPION,   EN_WOLF,		EN_WOLF;($F572)
		.byte EN_MSCORPION,   EN_WRAITH,	  EN_WOLFLORD,	EN_WOLFLORD,	EN_GOLDMAN;($F577)
		.byte EN_WRAITH,	  EN_WYVERN,	  EN_WOLFLORD,	EN_WYVERN,	  EN_GOLDMAN;($F57C)
		.byte EN_WYVERN,	  EN_RSCORPION,   EN_WKNIGHT,	 EN_KNIGHT,	  EN_DKNIGHT;($F581)
		.byte EN_WKNIGHT,	 EN_KNIGHT,	  EN_MAGIWYVERN,  EN_DKNIGHT,	 EN_MSLIME;($F586)
		.byte EN_KNIGHT,	  EN_MAGIWYVERN,  EN_DKNIGHT,	 EN_WEREWOLF,	EN_STARWYVERN;($F58B)
		.byte EN_WEREWOLF,	EN_GDRAGON,	 EN_STARWYVERN,  EN_STARWYVERN,  EN_WIZARD;($F590)

;These are dungeon enemy zones.
		.byte EN_POLTERGEIST, EN_DROLL,	   EN_DRAKEEMA,	EN_SKELETON,	EN_WARLOCK;($F595)
		.byte EN_SPECTER,	 EN_WOLFLORD,	EN_DRUINLORD,   EN_DROLLMAGI,   EN_WKNIGHT;($F59A)
		.byte EN_WEREWOLF,	EN_GDRAGON,	 EN_STARWYVERN,  EN_WIZARD,	  EN_AXEKNIGHT;($F59F)
		.byte EN_WIZARD,	  EN_AXEKNIGHT,   EN_BDRAGON,	 EN_BDRAGON,	 EN_STONEMAN;($F5A4)
		.byte EN_WIZARD,	  EN_STONEMAN,	EN_ARMORKNIGHT, EN_ARMORKNIGHT, EN_RDRAGON;($F5A9)
		.byte EN_GHOST,	   EN_MAGICIAN,	EN_SCORPION,	EN_DRUIN,	   EN_DRUIN;($F5AE)

;----------------------------------------------------------------------------------------------------

GFXTilesPtr:
		.word GFXTilesTbl	   ;($F5B3)Pointer to table below.

GFXTilesTbl:
		.byte $A0, $A0, $A0, $A0, $02;($F5B5)Grass.									 Block $00
		.byte $A1, $A1, $A1, $A1, $03;($F5BA)Sand.									  Block $01
		.byte $A2, $A3, $A4, $A5, $03;($F5BF)Hill.									  Block $02
		.byte $73, $74, $75, $76, $01;($F5C4)Stairs up.								 Block $03
		.byte $77, $77, $77, $77, $01;($F5C9)Bricks.									Block $04
		.byte $7B, $7C, $7D, $7E, $01;($F5CE)Stairs down.							   Block $05
		.byte $81, $81, $81, $81, $02;($F5D3)Swamp.									 Block $06
		.byte $82, $83, $84, $85, $00;($F5D8)Town									   Block $07
		.byte $86, $87, $88, $89, $01;($F5DD)Cave.									  Block $08
		.byte $8A, $8B, $8C, $8D, $00;($F5E2)Castle.									Block $09
		.byte $9B, $9C, $9D, $9E, $00;($F5E7)Bridge.									Block $0A
		.byte $7F, $7F, $80, $80, $02;($F5EC)Trees.									 Block $0B
		.byte $F8, $FA, $F9, $FB, $01;($F5F1)Treasure chest.							Block $0C
		.byte $8E, $8E, $8E, $8E, $03;($F5F6)Force field.							   Block $0D
		.byte $F7, $F3, $6D, $6E, $02;($F5FB)Large tile.								Block $0E
		.byte $F6, $A8, $A8, $F6, $00;($F600)Water - no shore.						  Block $0F
		.byte $6F, $70, $71, $72, $01;($F605)Stone block.							   Block $10
		.byte $8F, $90, $91, $92, $01;($F60A)Door.									  Block $11
		.byte $A6, $A7, $F4, $F5, $01;($F60F)Mountain.								  Block $12
		.byte $93, $94, $95, $96, $01;($F614)Weapon shop sign.						  Block $13
		.byte $97, $98, $99, $9A, $01;($F619)Inn sign.								  Block $14
		.byte $9F, $9F, $9F, $9F, $01;($F61E)Small tiles.							   Block $15
		.byte $5F, $5F, $5F, $5F, $01;($F623)Black square.							  Block $16
		.byte $A9, $AB, $AA, $AC, $01;($F628)Princess Gwaelin.						  Block $17
		.byte $46, $4A, $A8, $F6, $00;($F62D)Water - shore at top.					  Block $18
		.byte $5A, $A8, $5B, $F6, $00;($F632)Water - shore at left.					 Block $19
		.byte $5E, $4A, $5B, $F6, $00;($F637)Water - shore at top, left.				Block $1A
		.byte $F6, $5C, $A8, $5D, $00;($F63C)Water - shore at right.					Block $1B
		.byte $46, $6A, $A8, $5D, $00;($F641)Water - shore at top, right.			   Block $1C
		.byte $5A, $5C, $5B, $5D, $00;($F646)Water - shore at left, right.			  Block $1D
		.byte $5E, $6A, $5B, $5D, $00;($F64B)Water - shore at top, left, right.		 Block $1E
		.byte $F6, $A8, $58, $59, $00;($F650)Water - shore at bottom.				   Block $1F
		.byte $46, $4A, $58, $59, $00;($F655)Water - shore at top, bottom.			  Block $20
		.byte $5A, $A8, $6B, $59, $00;($F65A)Water - shore at left, bottom.			 Block $21
		.byte $5E, $4A, $6B, $59, $00;($F65F)Water - shore at top, left, bottom.		Block $22
		.byte $F6, $5C, $58, $6C, $00;($F664)Water - shore at right, bottom.			Block $23
		.byte $46, $6A, $58, $6C, $00;($F669)Water - shore at top, right, bottom.	   Block $24
		.byte $5A, $5C, $6B, $6C, $00;($F66E)Water - shore at left, right and bottom.   Block $25
		.byte $5E, $6A, $6B, $6C, $00;($F673)Water - shore at all sides.				Block $26

;----------------------------------------------------------------------------------------------------

LoadSaveMenus:
		JSR ShowStartGame	   ;($F678)($F842)Show initial windows for managing saved games.
		LDX SaveNumber		  ;($F67B)
		LDA StartStatus1,X	  ;($F67E)Get start status for selected game.
		STA ThisStrtStat		;($F681)
		RTS					 ;($F684)

;----------------------------------------------------------------------------------------------------

WindowLoadGameDat:
		LDA SaveSelected		;($F685)Get selected saved game.
		JSR Copy100Times		;($F688)($FAC1)Make up to 100 copies of saved game to validate.
		JSR GetPlayerStatPtr	;($F68B)($C156)Get pointer to player's level base stats.
		RTS					 ;($F68E)

;----------------------------------------------------------------------------------------------------

SGZeroStats:
		LDA #$00				;($F68F)
		STA ExpLB			   ;($F691)
		STA ExpUB			   ;($F693)
		STA GoldLB			  ;($F695)
		STA GoldUB			  ;($F697)
		STA InventorySlot12	 ;($F699)
		STA InventorySlot34	 ;($F69B)
		STA InventorySlot56	 ;($F69D)
		STA InventorySlot78	 ;($F69F)
		STA InventoryKeys	   ;($F6A1)
		STA InventoryHerbs	  ;($F6A3)Zero out all the character's data as a new game is starting.
		STA EqippedItems		;($F6A5)
		STA ModsnSpells		 ;($F6A7)
		STA PlayerFlags		 ;($F6A9)
		STA StoryFlags		  ;($F6AB)
		STA HitPoints		   ;($F6AD)
		STA MagicPoints		 ;($F6AF)
		LDX SaveNumber		  ;($F6B1)
		LDA #STRT_FULL_HP	   ;($F6B4)
		STA StartStatus1,X	  ;($F6B6)
		RTS					 ;($F6B9)

;----------------------------------------------------------------------------------------------------

CopyGame:
		LDA OpnSltSelected	  ;($F6BA)Prepare to get address of target game slot.
		JSR GetSaveGameBase	 ;($F6BD)($FC00)Get base address of target game slot data.

		LDA GameDataPointerLB   ;($F6C0)
		STA RAMTrgtPtrLB		;($F6C2)Set target pointer to target game slot.
		LDA GameDataPointerUB   ;($F6C4)
		STA RAMTrgtPtrUB		;($F6C6)

		LDA SaveNumber		  ;($F6C8)Prepare to get address of source game slot.
		JSR GetSaveGameBase	 ;($F6CB)($FC00)Get base address of source game slot data.

		LDY #$00				;($F6CE)Need to copy a total of 320 bytes(32*10).
		* LDA (GameDataPointer),Y;($F6D0)Copy data byte from source to target.
		STA (RAMTrgtPtr),Y	  ;($F6D2)
		DEY					 ;($F6D4)Have the first 256 bytes been copied?
		BNE -				   ;($F6D5)If not, branch to copy another byte.

		LDX GameDataPointerUB   ;($F6D7)
		INX					 ;($F6D9)
		STX GameDataPointerUB   ;($F6DA)Increment upper byte of source and target addresses.
		LDX RAMTrgtPtrUB		;($F6DC)
		INX					 ;($F6DE)
		STX RAMTrgtPtrUB		;($F6DF)

		* LDA (GameDataPointer),Y;($F6E1)Copy final 64 bytes of save game data.
		STA (RAMTrgtPtr),Y	  ;($F6E3)Copy data byte from source to target.
		INY					 ;($F6E5)
		CPY #$40				;($F6E6)Have 64 bytes been copied?
		BNE -				   ;($F6E8)If not, branch to copy another byte.

		LDA OpnSltSelected	  ;($F6EA)Set the newly created game slot as a valid save game slot.
		STA SaveNumber		  ;($F6ED)
		JSR CreateNewSave	   ;($F6F0)($F7DA)Prep save game slot.
		RTS					 ;($F6F3)

;----------------------------------------------------------------------------------------------------

GetValidSaves:
		LDX #$09				;($F6F4)Prepare to check for Ken Masuta's name in battery backed RAM.
		* LDA KenMasuta1,X	  ;($F6F6)
		CMP KenMasutaTbl,X	  ;($F6F9)Check if Ken's name is intact in the battery backed RAM.
		BNE InitSaves		   ;($F6FC)Is the name correct? If not, branch to invalidae all saved games.
		DEX					 ;($F6FE)Have all 9 characters of ken's name been checked in RAM?
		BPL -				   ;($F6FF)If not, branch to verify another character.

		JMP WriteKenStrings	 ;($F701)($F753)Write "Ken Masuta" to RAM to validate memory.

InitSaves:
		LDX #$09				;($F704)Prepare to check for Ken Masuta's name in battery backed RAM.
		* LDA KenMasuta2,X	  ;($F706)

		CMP KenMasutaTbl,X	  ;($F709)Does the character in RAM match the ROM table?
		BNE ClearSaveGameRAM	;($F70C)If not, RAM values are corrupt. Branch to rease saved games.

		DEX					 ;($F70E)Done comparing entire Ken Masuta string?
		BPL -				   ;($F70F)If not, branch to check next byte in string.

		BMI WriteKenStrings	 ;($F711)Battery backed RAM integrity checks out. Rewrite Ken string.

ClearSaveGameRAM:
		INC Unused6435		  ;($F713)
		LDA #$00				;($F716)Initialize variables used for clearing game data.
		LDX #$00				;($F718)

		* STA SavedGame1,X	  ;($F71A)Clear first 256 bytes of save game data for all slots.
		STA SavedGame2,X		;($F71D)
		STA SavedGame3,X		;($F720)
		DEX					 ;($F723)Are 256 bytes cleared?
		BNE -				   ;($F724)If not, branch to clear more bytes.

		LDX #$00				;($F726)Clear remaining 64 bytes of save game data for all slots.
		* STA SavedGame1+$100,X ;($F728)
		STA SavedGame2+$100,X   ;($F72B)
		STA SavedGame3+$100,X   ;($F72E)
		INX					 ;($F731)
		CPX #$40				;($F732)Are 64 bytes cleared?
		BCC -				   ;($F734)If not, branch to clear more bytes.

		LDA #$00				;($F736)
		STA ValidSave1		  ;($F738)
		STA ValidSave2		  ;($F73B)
		STA ValidSave3		  ;($F73E)
		STA StartStatus1		;($F741)Clear various save game variables.
		STA StartStatus2		;($F744)
		STA StartStatus3		;($F747)
		STA CRCFail1			;($F74A)
		STA CRCFail2			;($F74D)
		STA CRCFail3			;($F750)

WriteKenStrings:
		LDX #$09				;($F753)Write Ken Masuta's name to 2 different RAM locations.
		* LDA KenMasutaTbl,X	;($F755)
		STA KenMasuta1,X		;($F758)
		STA KenMasuta2,X		;($F75B)
		DEX					 ;($F75E)Have all bytes of his name been written?
		BPL -				   ;($F75F)If not, branch to write the next byte.

		LDA #$00				;($F761)Clear saved game bit mask and manually revalidate.
		STA SaveBitMask		 ;($F763)
		JSR VerifyValidSaves	;($F766)($F7B5)Update saved game bit mask to match ValidSave variables.

		LDA SaveBitMask		 ;($F769)Make a copy of valid saved games bitmask.
		STA OpnSltSelected	  ;($F76C)

		LDA #$02				;($F76F)Prepare to check all 3 saved games.
		STA SaveGameCounter	 ;($F771)

		LDA #$00				;($F774)Start at saved game 1.
		STA SaveNumber		  ;($F776)

CheckValidSlot:
		LSR OpnSltSelected	  ;($F779)Does the current saved game slot contain a saved game?
		BCC DoneValidateSave	;($F77C)If not, branch to check the next slot.

		LDA SaveNumber		  ;($F77E)Prepare to test the RAM for the selected save slot.
		JSR Copy100Times		;($F781)($FAC1)Make up to 100 copies of saved game to validate.
		CMP #$00				;($F784)Is RAM for saved game valid?
		BEQ DoneValidateSave	;($F786)If so, branch to check next saved game.

		LDA SaveNumber		  ;($F788)Saved game RAM was corrupted. Erase game.
		JSR ClearValidSaves	 ;($F78B)($F80F)Clear ValidSave variable for selected game.

		JSR Dowindow			;($F78E)($C6F0)display on-screen window.
		.byte WINDOW_DIALOG	 ;($F791)Dialog window.

		LDA SaveNumber		  ;($F792)
		CLC					 ;($F795)
		ADC #$01				;($F796)Save number of failed saved game slots found.
		STA GenWrd00LB		  ;($F798)Seems to have no effect.
		LDA #$00				;($F79A)
		STA GenWrd00UB		  ;($F79C)

		JSR DoDialogHiBlock	 ;($F79E)($C7C5)Unfortunately no deeds were recorded...
		.byte $29			   ;($F7A1)TextBlock19, entry 9.

		LDA #$1E				;($F7A2)Prepare to wait 30 frames(1/2 second).
		JSR WaitMultiNMIs	   ;($F7A4)($C170)Wait a dfined number of frames.

		LDA #$02				;($F7A7)Prepare to remove the dialog window.

		BRK					 ;($F7A9)Remove window from screen.
		.byte $05, $07		  ;($F7AA)($A7A2)RemoveWindow, bank 0.

DoneValidateSave:
		INC SaveNumber		  ;($F7AC)Move to next saved game.
		DEC SaveGameCounter	 ;($F7AF)Have all 3 game slots been checked?
		BPL CheckValidSlot	  ;($F7B2)If not, branch to check the next one.
		RTS					 ;($F7B4)

;----------------------------------------------------------------------------------------------------

VerifyValidSaves:
		TXA					 ;($F7B5)Save X on stack.
		PHA					 ;($F7B6)

		LDA #$00				;($F7B7)Assume no valid save games.
		LDX ValidSave1		  ;($F7B9)
		CPX #$C8				;($F7BC)Is valid byte value correct for saved game 1?
		BNE ChkBitMask2		 ;($F7BE)If not, branch to check saved game 2.

		ORA #$01				;($F7C0)Set game 1 as a valid save game.

ChkBitMask2:
		LDX ValidSave2		  ;($F7C2)Is valid byte value correct for saved game 2?
		CPX #$C8				;($F7C5)
		BNE ChkBitMask3		 ;($F7C7)If not, branch to check saved game 3.

		ORA #$02				;($F7C9)Set game 2 as a valid save game.

ChkBitMask3:
		LDX ValidSave3		  ;($F7CB)Is valid byte value correct for saved game 3?
		CPX #$C8				;($F7CE)
		BNE UpdtSaveBitMask	 ;($F7D0)If not, branch to save saved games bit masks.

		ORA #$04				;($F7D2)Set game 3 as a valid save game.

UpdtSaveBitMask:
		STA SaveBitMask		 ;($F7D4)Save bit mask for valid saved games.

		PLA					 ;($F7D7)
		TAX					 ;($F7D8)Restore X from stack and return.
		RTS					 ;($F7D9)

;----------------------------------------------------------------------------------------------------

CreateNewSave:
		PHA					 ;($F7DA)
		TXA					 ;($F7DB)Save A and X on the stack.
		PHA					 ;($F7DC)

		LDA SaveBitMask		 ;($F7DD)Get save bit mask and save number.
		LDX SaveNumber		  ;($F7E0)
		BEQ SaveAtSlot1		 ;($F7E3)Save slot 1? If so, branch to create.

		CPX #$01				;($F7E5)
		BEQ SaveAtSlot2		 ;($F7E7)Save slot 2? If so, branch to create.

		CPX #$02				;($F7E9)Does nothing. Has to be save slot 3.
		ORA #$04				;($F7EB)Set valid bit in bit mask.
		LDX #$C8				;($F7ED)
		STX ValidSave3		  ;($F7EF)Indicate save slot 3 is valid.
		JMP UpdateSaveBitMask   ;($F7F2)($F806)Keep only lower 3 bits and exit.

SaveAtSlot2:
		ORA #$02				;($F7F5)Set valid bit in bit mask.
		LDX #$C8				;($F7F7)
		STX ValidSave2		  ;($F7F9)Indicate save slot 2 is valid.
		JMP UpdateSaveBitMask   ;($F7FC)($F806)Keep only lower 3 bits and exit.

SaveAtSlot1:
		ORA #$01				;($F7FF)Set valid bit in bit mask.
		LDX #$C8				;($F801)
		STX ValidSave1		  ;($F803)Indicate save slot 1 is valid.

UpdateSaveBitMask:
		AND #$07				;($F806)Keep only lower 3 bits in bit mask.
		STA SaveBitMask		 ;($F808)

		PLA					 ;($F80B)
		TAX					 ;($F80C)Restore A and X.
		PLA					 ;($F80D)
		RTS					 ;($F80E)

;----------------------------------------------------------------------------------------------------

ClearValidSaves:
		PHA					 ;($F80F)
		TXA					 ;($F810)Save A and X on the stack.
		PHA					 ;($F811)

		LDA SaveBitMask		 ;($F812)Is the first save game selected?
		LDX SaveNumber		  ;($F815)
		BEQ ClearValidSave1	 ;($F818)If so, branch to clear first save game valid bits.

		CPX #$01				;($F81A)Is the second save game selected?
		BEQ ClearValidSave2	 ;($F81C)If so, branch to clear second save game valid bits.

		CPX #$02				;($F81E)Compare has no function here.
		AND #$03				;($F820)Clear bit 2 of saved game bit mask.
		LDX #$00				;($F822)Clear ValidSave3.
		STX ValidSave3		  ;($F824)
		JMP ClearValisSaveDone  ;($F827)($F83B)Update save game bit mask.

ClearValidSave2:
		AND #$05				;($F82A)Clear bit 1 of saved game bit mask.
		LDX #$00				;($F82C)Clear ValidSave2.
		STX ValidSave2		  ;($F82E)
		JMP ClearValisSaveDone  ;($F831)($F83B)Update save game bit mask.

ClearValidSave1:
		AND #$06				;($F834)Clear LSB of saved game bit mask.
		LDX #$00				;($F836)Clear ValidSave1.
		STX ValidSave1		  ;($F838)

ClearValisSaveDone:
		STA SaveBitMask		 ;($F83B)Update valid save game bit mask.

		PLA					 ;($F83E)
		TAX					 ;($F83F)Restore A and X from the stack.
		PLA					 ;($F840)
		RTS					 ;($F841)

;----------------------------------------------------------------------------------------------------

ShowStartGame:
		JSR ClearWinBufRAM	  ;($F842)($FC4D)Clear RAM $0400-$07BF;
		JSR ClearSpriteRAM	  ;($F845)($C6BB)Clear sprite RAM.
		JSR ClearPPU			;($F848)($C17A)Clear the PPU.
		LDA #%00011000		  ;($F84B)Turn on background and sprites.
		STA PPUControl1		 ;($F84D)
		JSR WaitForNMI		  ;($F850)($FF74)Wait for VBlank interrupt.

		BRK					 ;($F853)Load BG and sprite palettes for selecting saved game.
		.byte $01, $07		  ;($F854)($AA7E)LoadStartPals, bank 0.

		JSR GetValidSaves	   ;($F856)($F6F4)Get valid save game slots.
		LDA SaveBitMask		 ;($F859)Get save games bitmask.
		AND #$07				;($F85C)Are there any saved games?
		BEQ PreNoSaves		  ;($F85E)If not, branch.

		CMP #$07				;($F860)Is there at least 1 empty save slot?
		BNE PreUnusedSaves	  ;($F862)If so, branch.

;----------------------------------------------------------------------------------------------------

PreSavesUsed:
		JSR Dowindow			;($F864)($C6F0)display on-screen window.
		.byte WINDOW_CNT_CH_ER  ;($F867)Continue, change, erase window.

		CMP #$00				;($F868)Was continue saved game selected?
		BNE ChkChngMsgSpeed	 ;($F86A)If not, branch to check next selection.
		JMP DoContinueGame	  ;($F86C)($F8AF)Select existing game to continue.

ChkChngMsgSpeed:
		CMP #$01				;($F86F)Was change message speed selected?
		BNE ChkEraseGame		;($F871)If not, branch to check next selection.
		JMP DoChngMsgSpeed	  ;($F873)($F8EC)Select game to change message speed.

ChkEraseGame:
		CMP #$02				;($F876)Was erase game selected?
		BNE PreSavesUsed		;($F878)If not, branch to stay on current menu.
		JMP DoEraseGame		 ;($F87A)($F911)Select game to erase.

;----------------------------------------------------------------------------------------------------

PreUnusedSaves:
		JSR Dowindow			;($F87D)($C6F0)display on-screen window.
		.byte WINDOW_FULL_MNU   ;($F880)Full menu window.

		CMP #$00				;($F881)Was continue saved game selected?
		BNE ChkChngMsgSpeed2	;($F883)If not, branch to check next selection.
		JMP DoContinueGame	  ;($F885)($F8AF)Select existing game to continue.

ChkChngMsgSpeed2:
		CMP #$01				;($F888)Was change message speed selected?
		BNE ChkNewQuest		 ;($F88A)If not, branch to check next selection.
		JMP DoChngMsgSpeed	  ;($F88C)($F8EC)Select game to change message speed.

ChkNewQuest:
		CMP #$02				;($F88F)Was start a new game selected?
		BNE ChkCopyQuest		;($F891)If not, branch to check next selection.
		JMP DoNewQuest		  ;($F893)($F8C2)Start a new game.

ChkCopyQuest:
		CMP #$03				;($F896)Was copy a game selected?
		BNE ChkEraseGame2	   ;($F898)If not, branch to check next selection.
		JMP DoCopyGame		  ;($F89A)($F93B)Copy a saved game.

ChkEraseGame2:
		CMP #$04				;($F89D)Was erase game selected?
		BNE PreUnusedSaves	  ;($F89F)If not, branch to stay on current menu.
		JMP DoEraseGame		 ;($F8A1)($F911)Select game to erase.

;----------------------------------------------------------------------------------------------------

PreNoSaves:
		JSR Dowindow			;($F8A4)($C6F0)display on-screen window.
		.byte WINDOW_NEW_QST	;($F8A7)Begin new quest window.

		CMP #$00				;($F8A8)Was continue saved game selected?
		BNE PreNoSaves		  ;($F8AA)If not, branch to stay on current menu.
		JMP DoNewQuest		  ;($F8AC)($F8C2)Start a new game.

;----------------------------------------------------------------------------------------------------

DoContinueGame:
		LDA #$00				;($F8AF)Prepare to get valid saved games.
		JSR ShowUsedLogs		;($F8B1)($F99F)Show occupied adventure logs.
		CMP #WINDOW_ABORT	   ;($F8B4)Was B button pressed?
		BNE PrepContinueGame	;($F8B6)If not, branch to continue saved game.
		JMP WindowBackToMain	;($F8B8)($F96A)Go back to main pre-game window.

PrepContinueGame:
		STA SaveNumber		  ;($F8BB)Get a copy of the selected saved game number.
		JSR Copy100Times		;($F8BE)($FAC1)Make up to 100 copies of saved game to validate.
		RTS					 ;($F8C1)

;----------------------------------------------------------------------------------------------------

DoNewQuest:
		LDA #$FF				;($F8C2)Prepare to show available adventure log spots.
		JSR ShowOpenLogs		;($F8C4)($F983)Show open adventure log spots.
		CMP #WINDOW_ABORT	   ;($F8C7)Was B button pressed?
		BNE NewQuest			;($F8C9)If not, branch to input character name of new game.

		JMP WindowBackToMain	;($F8CB)($F96A)Go back to main pre-game window.

NewQuest:
		STA SaveNumber		  ;($F8CE)Save the game slot for the new game.

		BRK					 ;($F8D1)Do name entering functions.
		.byte $11, $17		  ;($F8D2)($AE02)WindowEnterName, bank 1.

		LDA #MSG_NORMAL		 ;($F8D4)Set normal message speed.
		STA MessageSpeed		;($F8D6)

		JSR Dowindow			;($F8D8)($C6F0)display on-screen window.
		.byte WINDOW_MSG_SPEED  ;($F8DB)Message speed window.

		CMP #WINDOW_ABORT	   ;($F8DC)Was B button pressed?
		BNE InitNewGame		 ;($F8DE)If not, branch to initialize the new game.

		JMP WindowBackToMain	;($F8E0)($F96A)Go back to main pre-game window.

;----------------------------------------------------------------------------------------------------

InitNewGame:
		STA MessageSpeed		;($F8E3)Save the selected message speed.
		JSR SGZeroStats		 ;($F8E5)($F68F)Zero out all save game stats.
		JSR SaveCurrentGame	 ;($F8E8)($F9DF)Save game data in the selected slot.
		RTS					 ;($F8EB)

;----------------------------------------------------------------------------------------------------

DoChngMsgSpeed:
		LDA #$00				;($F8EC)Prepare to show occupied adventure log spots.
		JSR ShowUsedLogs		;($F8EE)($F99F)Show occupied adventure logs.
		CMP #WINDOW_ABORT	   ;($F8F1)Was B button pressed?
		BNE ShowChngMsgSpeed	;($F8F3)If not, branch to show change message speed window.

		JMP WindowBackToMain	;($F8F5)($F96A)Go back to main pre-game window.

ShowChngMsgSpeed:
		STA SaveNumber		  ;($F8F8)Store desired game number.
		JSR Copy100Times		;($F8FB)($FAC1)Make up to 100 copies of saved game to validate.

		JSR Dowindow			;($F8FE)($C6F0)display on-screen window.
		.byte WINDOW_MSG_SPEED  ;($F901)Message speed window.

		CMP #WINDOW_ABORT	   ;($F902)Was B button pressed?
		BNE ChngMsgSpeed		;($F904)If not, branch to change message speed.

		JMP WindowBackToMain	;($F906)($F96A)Go back to main pre-game window.

ChngMsgSpeed:
		STA MessageSpeed		;($F909)Update message speed.
		JSR SaveCurrentGame	 ;($F90B)($F9DF)Save game data in the selected slot.
		JMP WindowBackToMain	;($F90E)($F96A)Go back to main pre-game window.

;----------------------------------------------------------------------------------------------------

DoEraseGame:
		LDA #$00				;($F911)Prepare to get used save game slots.
		JSR ShowUsedLogs		;($F913)($F99F)Show occupied adventure logs.
		CMP #WINDOW_ABORT	   ;($F916)Was B button pressed?
		BNE VerifyErase		 ;($F918)If not, branch to show verify window.
		JMP WindowBackToMain	;($F91A)($F96A)Go back to main pre-game window.

VerifyErase:
		STA SaveNumber		  ;($F91D)Make copies of save slot selected(0 to 2).
		STA SaveSelected		;($F920)

		JSR Dowindow			;($F923)($C6F0)display on-screen window.
		.byte WINDOW_ERASE	  ;($F926)Erase log window.

		JSR Dowindow			;($F927)($C6F0)display on-screen window.
		.byte WND_YES_NO2	   ;($F92A)Yes/No selection window.

		CMP #WINDOW_YES		 ;($F92B)Was chosen from selection window?
		BEQ EraseGame		   ;($F92D)If so, branch to erase selected game.
		JMP WindowBackToMain	;($F92F)($F96A)Go back to main pre-game window.

EraseGame:
		LDA SaveNumber		  ;($F932)Get save slot to erase.
		JSR ClearValidSaves	 ;($F935)($F80F)Clear ValidSave variable for selected game.
		JMP WindowBackToMain	;($F938)($F96A)Go back to main pre-game window.

;----------------------------------------------------------------------------------------------------

DoCopyGame:
		LDA #$00				;($F93B)Prepare to get used save game slots.
		JSR ShowUsedLogs		;($F93D)($F99F)Show occupied adventure logs.
		CMP #WINDOW_ABORT	   ;($F940)Was B button pressed?
		BNE ShowOpenSlots	   ;($F942)If not, branch to show open save game slots.

		JMP WindowBackToMain	;($F944)($F96A)Go back to main pre-game window.

ShowOpenSlots:
		STA SaveNumber		  ;($F947)Save a copy of the selected slot.
		LDA #$FF				;($F94A)Prepare to get open save game slots.
		JSR ShowOpenLogs		;($F94C)($F983)Show open adventure log spots.
		CMP #WINDOW_ABORT	   ;($F94F)Was B button pressed?
		BNE ConfirmCopy		 ;($F951)If not, branch to confirm save game copy.

		JMP WindowBackToMain	;($F953)($F96A)Go back to main pre-game window.

ConfirmCopy:
		STA OpnSltSelected	  ;($F956)Save target slot to copy game into.

		JSR Dowindow			;($F959)($C6F0)display on-screen window.
		.byte WND_YES_NO2	   ;($F95C)Yes/No selection window.

		CMP #$00				;($F95D)was game copy finalized?
		BEQ DoCopyGameDat	   ;($F95F)If so, branch to copy game data.

		JMP WindowBackToMain	;($F961)($F96A)Go back to main pre-game window.

DoCopyGameDat:
		JSR CopyGame			;($F964)($F6BA)Copy game data from save slot to another.
		JMP WindowBackToMain	;($F967)($F96A)Go back to main pre-game window.

WindowBackToMain:
		LDA #$FF				;($F96A)Prepare to remove window from screen.

		BRK					 ;($F96C)Remove window from screen.
		.byte $05, $07		  ;($F96D)($A7A2)RemoveWindow, bank 0.

		LDA SaveBitMask		 ;($F96F)Is there still a spot open after copy?
		AND #$07				;($F972)
		BEQ JmpNoSaves		  ;($F974)If not, branch to show appropriate main menu.

		CMP #$07				;($F976)Is there still a spot open after copy?
		BNE JmpSomeSaves		;($F978)If so, branch to show appropriate main menu. Should always branch.

		JMP PreSavesUsed		;($F97A)($F864)Show main menu with no open game slots.

JmpSomeSaves:
		JMP PreUnusedSaves	  ;($F97D)($F87D)Show main menu with used and unused game slots.

JmpNoSaves:
		JMP PreNoSaves		  ;($F980)($F8A4)Show main menu with no occupied game slots.

;----------------------------------------------------------------------------------------------------

ShowOpenLogs:
		EOR SaveBitMask		 ;($F983)Get 1's compliment of valid game bit masks.
		AND #$07				;($F986)Keep only lower 3 bits. Only 3 save slots.
		BEQ NoOpenGames		 ;($F988)Are any open slots present? If not, branch to exit.

		STA _SaveBitMask		;($F98A)
		CLC					 ;($F98D)Use bitmasks to find proper log list window to show.
		ADC #$11				;($F98E)

		BRK					 ;($F990)Display empty adventure logs window (windows #$12 to #$18).
		.byte $10, $17		  ;($F991)($A194)ShowWindow, bank 1.

		CMP #WINDOW_ABORT	   ;($F993)Was B button pressed?
		BNE ShowOpenLogsExit	;($F995)If not, exit with selected log results.

NoOpenGames:
		PLA					 ;($F997)Pull last return address.
		PLA					 ;($F998)
		JMP WindowBackToMain	;($F999)($F96A)Go back to main pre-game window.

ShowOpenLogsExit:
		JMP CalcSelectedSlot	;($F99C)($F9BB)Calculate save slot selected.

;----------------------------------------------------------------------------------------------------

ShowUsedLogs:
		EOR SaveBitMask		 ;($F99F)Get saved games bitmask.
		AND #$07				;($F9A2)Keep only lower 3 bits. Only 3 save slots.
		BEQ NoSavedGames		;($F9A4)Are any saved games present? If not, branch to exit.

		STA _SaveBitMask		;($F9A6)
		CLC					 ;($F9A9)Use bitmasks to find proper log list window to show.
		ADC #$18				;($F9AA)

		BRK					 ;($F9AC)Display used adventure logs window (windows #$19 to #$1F).
		.byte $10, $17		  ;($F9AD)($A194)ShowWindow, bank 1.

		CMP #WINDOW_ABORT	   ;($F9AF)Was B button pressed?
		BNE ShowUsedLogsExit	;($F9B1)If not, exit with selected log results.

NoSavedGames:
		PLA					 ;($F9B3)Pull last return address.
		PLA					 ;($F9B4)
		JMP WindowBackToMain	;($F9B5)($F96A)Go back to main pre-game window.

ShowUsedLogsExit:
		JMP CalcSelectedSlot	;($F9B8)($F9BB)Calculate save slot selected.

;----------------------------------------------------------------------------------------------------

CalcSelectedSlot:
		LDX _SaveBitMask		;($F9BB)Get bit mask for saved game slots.

		CPX #$02				;($F9BE)Was used game slot 2 selected?
		BNE ChkUsedSlot3		;($F9C0)If not branch to check next.

		LDA #$01				;($F9C2)Return 2nd game slot (count starts at 0).
		RTS					 ;($F9C4)

ChkUsedSlot3:
		CPX #$04				;($F9C5)Was used game slot 3 selected?
		BNE ChkOpenSlot2		;($F9C7)If not branch to check next.

		LDA #$02				;($F9C9)Return 3rd game slot (count starts at 0).
		RTS					 ;($F9CB)

ChkOpenSlot2:
		CPX #$05				;($F9CC)Are slots 3 and 1 open?
		BNE ChkOpenSlot1		;($F9CE)If not, branch to check next.

		CMP #$01				;($F9D0)Was second selection in window chosen(slot 3)?
		BNE CalcSlotExit		;($F9D2)If not, branch to exit.  Must have been slot 1.

		LDA #$02				;($F9D4)Return 3rd game slot (count starts at 0).
		RTS					 ;($F9D6)

ChkOpenSlot1:
		CPX #$06				;($F9D7)Are slots 3 and 2 open?
		BNE CalcSlotExit		;($F9D9)Must be slot 1 selected. Return 1st slot(0).

		CLC					 ;($F9DB)Return 2nd game slot (count starts at 0).
		ADC #$01				;($F9DC)

CalcSlotExit:
		RTS					 ;($F9DE)Return value of 0, 1 or 2 for selected game slot.

;----------------------------------------------------------------------------------------------------

SaveCurrentGame:
		PHA					 ;($F9DF)
		TXA					 ;($F9E0)
		PHA					 ;($F9E1)Preserve A, X, and Y on the stack.
		TYA					 ;($F9E2)
		PHA					 ;($F9E3)

		LDA SaveNumber		  ;($F9E4)
		AND #$07				;($F9E7)Only keep lower 3 bits of save game number.
		STA SaveNumber		  ;($F9E9)

		JSR CreateNewSave	   ;($F9EC)($F7DA)Prep save game slot.
		LDA CrntGamePtr		 ;($F9EF)
		STA GameDataPointerLB   ;($F9F2)Setup game data pointer.
		LDA CrntGamePtr+1	   ;($F9F4)
		STA GameDataPointerUB   ;($F9F7)

		JSR SaveData			;($F9F9)($FA18)Save player's data to battery backed RAM.
		JSR GetCRC			  ;($F9FC)($FBE0)Get CRC for selected game data.

		LDA CrntGamePtr		 ;($F9FF)
		STA ROMSourcePtrLB	  ;($FA02)Setup game data pointer to save game 10 times.
		LDA CrntGamePtr+1	   ;($FA04)
		STA ROMSourcePtrUB	  ;($FA07)

		LDA SaveNumber		  ;($FA09)Get saved game index.
		JSR GetSaveGameBase	 ;($FA0C)($FC00)Get base address of selected save game data.
		JSR Save10Times		 ;($FA0F)($FAA3)Save game data 10 times accross different addresses.

		PLA					 ;($FA12)
		TAY					 ;($FA13)
		PLA					 ;($FA14)Restore A, X and Y from the stack.
		TAX					 ;($FA15)
		PLA					 ;($FA16)
		RTS					 ;($FA17)

;----------------------------------------------------------------------------------------------------

SaveData:
		LDY #$00				;($FA18)Zero out index.

		LDA ExpLB			   ;($FA1A)
		STA (GameDataPointer),Y ;($FA1C)
		INY					 ;($FA1E)Save player's experience points.
		LDA ExpUB			   ;($FA1F)
		STA (GameDataPointer),Y ;($FA21)

		INY					 ;($FA23)
		LDA GoldLB			  ;($FA24)
		STA (GameDataPointer),Y ;($FA26)Save player's gold.
		INY					 ;($FA28)
		LDA GoldUB			  ;($FA29)
		STA (GameDataPointer),Y ;($FA2B)

		INY					 ;($FA2D)
		LDA InventorySlot12	 ;($FA2E)
		STA (GameDataPointer),Y ;($FA30)
		INY					 ;($FA32)
		LDA InventorySlot34	 ;($FA33)
		STA (GameDataPointer),Y ;($FA35)Save player's inventory items.
		INY					 ;($FA37)
		LDA InventorySlot56	 ;($FA38)
		STA (GameDataPointer),Y ;($FA3A)
		INY					 ;($FA3C)
		LDA InventorySlot78	 ;($FA3D)
		STA (GameDataPointer),Y ;($FA3F)

		INY					 ;($FA41)
		LDA InventoryKeys	   ;($FA42)Get player's keys.
		AND #$0F				;($FA44)
		CMP #$07				;($FA46)Does player have more than 6 keys?
		BCC +				   ;($FA48)If not, branch to move on.

		LDA #$06				;($FA4A)6 keys max.
		* STA (GameDataPointer),Y;($FA4C)Save player's magic keys.

		INY					 ;($FA4E)
		LDA InventoryHerbs	  ;($FA4F)Save player's herbs.
		STA (GameDataPointer),Y ;($FA51)

		INY					 ;($FA53)
		LDA EqippedItems		;($FA54)Save player's armor, shield and weapon.
		STA (GameDataPointer),Y ;($FA56)

		INY					 ;($FA58)
		LDA ModsnSpells		 ;($FA59)save player's upper 2 spells and other flags.
		STA (GameDataPointer),Y ;($FA5B)

		INY					 ;($FA5D)
		LDA PlayerFlags		 ;($FA5E)save other player flags.
		STA (GameDataPointer),Y ;($FA60)

		INY					 ;($FA62)
		LDA StoryFlags		  ;($FA63)Save player's story flags.
		STA (GameDataPointer),Y ;($FA65)

		INY					 ;($FA67)Prepare to save 4 lower name characters.
		LDX #$03				;($FA68)

		* LDA DispName0,X	   ;($FA6A)Save lower name character.
		STA (GameDataPointer),Y ;($FA6C)
		INY					 ;($FA6E)
		DEX					 ;($FA6F)More characters to save?
		BPL -				   ;($FA70)If so, branch to get next character.

		LDX #$03				;($FA72)Prepare to save 4 upper name characters.

		* LDA DispName4,X	   ;($FA74)Save upper name character.
		STA (GameDataPointer),Y ;($FA77)
		INY					 ;($FA79)
		DEX					 ;($FA7A)More characters to save?
		BPL -				   ;($FA7B)If so, branch to get next character.

		LDA MessageSpeed		;($FA7D)Save player's message speed.
		STA (GameDataPointer),Y ;($FA7F)

		INY					 ;($FA81)
		LDA HitPoints		   ;($FA82)Save player's hit points.
		STA (GameDataPointer),Y ;($FA84)

		INY					 ;($FA86)
		LDA MagicPoints		 ;($FA87)Save player's magic points.
		STA (GameDataPointer),Y ;($FA89)

		LDX SaveNumber		  ;($FA8B)
		LDA StartStatus1,X	  ;($FA8E)Save player's restart status.
		INY					 ;($FA91)
		STA (GameDataPointer),Y ;($FA92)

		LDA #$C8				;($FA94)
		INY					 ;($FA96)
		STA (GameDataPointer),Y ;($FA97)
		INY					 ;($FA99)
		STA (GameDataPointer),Y ;($FA9A)Fill spare bytes.
		INY					 ;($FA9C)
		STA (GameDataPointer),Y ;($FA9D)
		INY					 ;($FA9F)
		STA (GameDataPointer),Y ;($FAA0)
		RTS					 ;($FAA2)

;----------------------------------------------------------------------------------------------------

Save10Times:
		LDX #$09				;($FAA3)Prepare to save games 10 times.

Save10Loop:
		JSR StoreGamedData	  ;($FAA5)($FAB7)Write game data to save game slot RAM.

		LDA GameDataPointerLB   ;($FAA8)
		CLC					 ;($FAAA)
		ADC #$20				;($FAAB)Move to next save spot. Each spot is 32 bytes.
		STA GameDataPointerLB   ;($FAAD)
		BCC +				   ;($FAAF)
		INC GameDataPointerUB   ;($FAB1)

		* DEX				   ;($FAB3)Has the save game been written to 10 different addresses?
		BPL Save10Loop		  ;($FAB4)
		RTS					 ;($FAB6)If not, branch to write another copy of the save game data.

StoreGamedData:
		LDY #$1F				;($FAB7)Prepare to write 32 bytes.  Each save game is 32 bytes.
		* LDA (ROMSourcePtr),Y  ;($FAB9)
		STA (GameDataPointer),Y ;($FABB)
		DEY					 ;($FABD)
		BPL -				   ;($FABE)Has 32 bytes been written?
		RTS					 ;($FAC0)If not, branch to write another save game data byte.

;----------------------------------------------------------------------------------------------------
Copy100Times:
		STA GenByte3E		   ;($FAC1)Save index to desired save game.

		TXA					 ;($FAC3)
		PHA					 ;($FAC4)Preserve values of X and Y on the stack.
		TYA					 ;($FAC5)
		PHA					 ;($FAC6)

		LDA GenByte3E		   ;($FAC7)
		AND #$07				;($FAC9)Keep only lower 3 bits of save game index.
		STA GenByte3E		   ;($FACB)

		JSR GetSaveGameBase	 ;($FACD)($FC00)Get base address of selected save game data.

		LDX #$0A				;($FAD0)Prepare to copy game data to 10 different locations.

GameCopyLoop:
		TXA					 ;($FAD2)Save number of copies left to make on stack.
		PHA					 ;($FAD3)

		JSR CheckValidCRC	   ;($FAD4)($FB4A)Check if the CRC for the selected save game is valid.
		BCS CRCCheckFail		;($FAD7)Is data valid? If not, branch.

		JSR LoadSavedData	   ;($FAD9)($FB6B)Load save game data into game engine registers.

		LDA CrntGamePtr		 ;($FADC)Set a pointer to copy save game data. Makes
		STA GenPtr3CLB		  ;($FADF)a working copy of saved game data but does not
		LDA CrntGamePtr+1	   ;($FAE1)put the data into the game engine registers.
		STA GenPtr3CUB		  ;($FAE4)

		JSR MakeWorkingCopy	 ;($FAE6)($FB40)Make a working copy of selected saved game.
		JSR Copy10Times		 ;($FAE9)($FB15)Copy of saved game data 10 times to same addresses.

		PLA					 ;($FAEC)Indicate saved game data successfully copied.
		LDA #$00				;($FAED)
		JMP FinishGameCopy	  ;($FAEF)($FB0C)Done making copies of the saved game.

CRCCheckFail:
		TXA					 ;($FAF2)
		LDX SaveNumber		  ;($FAF3)Increment CRC fail counter.
		INC CRCFail1,X		  ;($FAF6)
		TAX					 ;($FAF9)

		LDA GameDataPointerLB   ;($FAFA)
		CLC					 ;($FAFC)
		ADC #$20				;($FAFD)Move to next address slots to copy saved game into.
		STA GameDataPointerLB   ;($FAFF)
		BCC NextCopy			;($FB01)
		INC GameDataPointerUB   ;($FB03)

NextCopy:
		PLA					 ;($FB05)Get number of copies left to make.
		TAX					 ;($FB06)
		DEX					 ;($FB07)Have 10 copies been made?
		BNE GameCopyLoop		;($FB08)If not, branch to make another copy.

		LDA #$FF				;($FB0A)Indicate saved game data cannot be successfully copied.

FinishGameCopy:
		STA GenByte3E		   ;($FB0C)Store valid status of saved game(#$00-good, #$FF-bad).

		PLA					 ;($FB0E)
		TAY					 ;($FB0F)Restore values of X and Y from the stack.
		PLA					 ;($FB10)
		TAX					 ;($FB11)

		LDA GenByte3E		   ;($FB12)A indicates whether selected game is valid or not.
		RTS					 ;($FB14)

;----------------------------------------------------------------------------------------------------

Copy10Times:
		LDA GenByte3E		   ;($FB15)Load save game number to work on.
		JSR GetSaveGameBase	 ;($FB17)($FC00)Get base address of selected save game data.

		LDA GameDataPointerLB   ;($FB1A)
		STA GenPtr3CLB		  ;($FB1C)Copy destination is saved game slot.
		LDA GameDataPointerUB   ;($FB1E)
		STA GenPtr3CUB		  ;($FB20)

		LDA CrntGamePtr		 ;($FB22)
		STA GameDataPointerLB   ;($FB25)Copy source is working copy of saved game.
		LDA CrntGamePtr+1	   ;($FB27)
		STA GameDataPointerUB   ;($FB2A)

		LDX #$0A				;($FB2C)Prepare to make 10 copies of the saved game data.

Copy10Loop:
		JSR MakeWorkingCopy	 ;($FB2E)($FB40)Make a working copy of a selected saved game.

		LDA GenByte3C		   ;($FB31)
		CLC					 ;($FB33)
		ADC #$20				;($FB34)Keep track of how many bytes total have been copied.
		STA GenByte3C		   ;($FB36)
		BCC Check10Copies	   ;($FB38)
		INC GenByte3D		   ;($FB3A)

Check10Copies:
		DEX					 ;($FB3C)Have 10 copies been made?
		BNE Copy10Loop		  ;($FB3D)
		RTS					 ;($FB3F)If not, branch to make a new copy.

;----------------------------------------------------------------------------------------------------

MakeWorkingCopy:
		LDY #$1F				;($FB40)Copy 32 bytes of data.
		* LDA (GameDataPointer),Y;($FB42)Copy byte of saved game data.
		STA (GenPtr3C),Y		;($FB44)
		DEY					 ;($FB46)Have all 32 bytes of data been copied?
		BPL -				   ;($FB47)If not, branch to copy next byte.
		RTS					 ;($FB49)

;----------------------------------------------------------------------------------------------------

CheckValidCRC:
		LDY #$1E				;($FB4A)
		LDA (GameDataPointer),Y ;($FB4C)
		STA CRCCopyLB		   ;($FB4E)Save a copy of the existing CRC in the save game.
		INY					 ;($FB50)
		LDA (GameDataPointer),Y ;($FB51)
		STA CRCCopyUB		   ;($FB53)

		JSR GetCRC			  ;($FB55)($FBE0)Recalculate CRC for selected game data.

		LDY #$1E				;($FB58)Compare lower bytes of the old and new CRC.
		LDA CRCCopyLB		   ;($FB5A)
		CMP (GameDataPointer),Y ;($FB5C)Are they the same?
		BNE InvalidCRC		  ;($FB5E)If not, branch.  Save game data is not valid.

		INY					 ;($FB60)Compare lower bytes of the old and new CRC.
		LDA CRCCopyUB		   ;($FB61)
		CMP (GameDataPointer),Y ;($FB63)Are they the same?
		BEQ ValidCRC			;($FB65)If so, branch.  Save game data is valid.

InvalidCRC:
		SEC					 ;($FB67)Set the carry and return.
		RTS					 ;($FB68)The CRC is invalid.

ValidCRC:
		CLC					 ;($FB69)Clear the carry and return.
		RTS					 ;($FB6A)The CRC is valid.

;----------------------------------------------------------------------------------------------------

LoadSavedData:
		LDY #$00				;($FB6B)Start at beginning of save game data.

		LDA (GameDataPointer),Y ;($FB6D)
		STA ExpLB			   ;($FB6F)
		INY					 ;($FB71)Load player's experience.
		LDA (GameDataPointer),Y ;($FB72)
		STA ExpUB			   ;($FB74)

		INY					 ;($FB76)
		LDA (GameDataPointer),Y ;($FB77)
		STA GoldLB			  ;($FB79)Load player's gold.
		INY					 ;($FB7B)
		LDA (GameDataPointer),Y ;($FB7C)
		STA GoldUB			  ;($FB7E)

		INY					 ;($FB80)
		LDA (GameDataPointer),Y ;($FB81)
		STA InventorySlot12	 ;($FB83)
		INY					 ;($FB85)
		LDA (GameDataPointer),Y ;($FB86)
		STA InventorySlot34	 ;($FB88)Load player's inventory items.
		INY					 ;($FB8A)
		LDA (GameDataPointer),Y ;($FB8B)
		STA InventorySlot56	 ;($FB8D)
		INY					 ;($FB8F)
		LDA (GameDataPointer),Y ;($FB90)
		STA InventorySlot78	 ;($FB92)

		INY					 ;($FB94)
		LDA (GameDataPointer),Y ;($FB95)Load player's keys.
		STA InventoryKeys	   ;($FB97)

		INY					 ;($FB99)
		LDA (GameDataPointer),Y ;($FB9A)Load player's herbs.
		STA InventoryHerbs	  ;($FB9C)

		INY					 ;($FB9E)
		LDA (GameDataPointer),Y ;($FB9F)Load player's weapons and armor.
		STA EqippedItems		;($FBA1)

		INY					 ;($FBA3)
		LDA (GameDataPointer),Y ;($FBA4)Load player's upper spells and misc. flags.
		STA ModsnSpells		 ;($FBA6)

		INY					 ;($FBA8)
		LDA (GameDataPointer),Y ;($FBA9)
		STA PlayerFlags		 ;($FBAB)Load all other story and player flags.
		INY					 ;($FBAD)
		LDA (GameDataPointer),Y ;($FBAE)
		STA StoryFlags		  ;($FBB0)

		INY					 ;($FBB2)Load player's lower 4 characters of their name.
		LDX #$03				;($FBB3)
		* LDA (GameDataPointer),Y;($FBB5)
		STA DispName0,X		 ;($FBB7)
		INY					 ;($FBB9)
		DEX					 ;($FBBA)Have 4 characters been loaded?
		BPL -				   ;($FBBB)If not, branch to load another character.

		LDX #$03				;($FBBD)Load player's upper 4 characters of their name.
		* LDA (GameDataPointer),Y;($FBBF)
		STA DispName4,X		 ;($FBC1)
		INY					 ;($FBC4)
		DEX					 ;($FBC5)Have 4 characters been loaded?
		BPL -				   ;($FBC6)If not, branch to load another character.

		LDA (GameDataPointer),Y ;($FBC8)Load message speed.
		STA MessageSpeed		;($FBCA)

		INY					 ;($FBCC)
		LDA (GameDataPointer),Y ;($FBCD)Load player's current HP.
		STA HitPoints		   ;($FBCF)

		INY					 ;($FBD1)
		LDA (GameDataPointer),Y ;($FBD2)Load player's current MP.
		STA MagicPoints		 ;($FBD4)

		INY					 ;($FBD6)
		LDA (GameDataPointer),Y ;($FBD7)Load player's start status
		LDX SaveNumber		  ;($FBD9)(should HP and MP be restored).
		STA StartStatus1,X	  ;($FBDC)
		RTS					 ;($FBDF)

;----------------------------------------------------------------------------------------------------

GetCRC:
		JSR DoCRC			   ;($FBE0)($FBEF)Calculate CRC on saved game.
		LDY #$1E				;($FBE3)CRC is stored in bytes 31 and 32 of saved game data.

		LDA CRCLB			   ;($FBE5)
		STA (GameDataPointer),Y ;($FBE7)
		INY					 ;($FBE9)Save CRC in saved game data slot.
		LDA CRCUB			   ;($FBEA)
		STA (GameDataPointer),Y ;($FBEC)
		RTS					 ;($FBEE)

;----------------------------------------------------------------------------------------------------

DoCRC:
		LDY #$1D				;($FBEF)30 bytes of saved game data.

		STY CRCLB			   ;($FBF1)Seed the LFSR.
		STY CRCUB			   ;($FBF3)

		* LDA (GameDataPointer),Y;($FBF5)Loop until all saved data bytes are processed.
		STA GenByte3C		   ;($FBF7)
		JSR DoLFSR			  ;($FBF9)($FC2A)Put data through an LFSR.
		DEY					 ;($FBFC)
		BPL -				   ;($FBFD)More bytes to process? If so, branch to continue.
		RTS					 ;($FBFF)

;----------------------------------------------------------------------------------------------------

GetSaveGameBase:
		STA GenByte22		   ;($FC00)Save value of A
		TXA					 ;($FC02)Preserve value of X on the stack.
		PHA					 ;($FC03)
		LDA GenByte22		   ;($FC04)Restore value of A.

		LDX SvdGamePtr		  ;($FC06)
		STX GameDataPointerLB   ;($FC09)Get base address for save game 1 data.
		LDX SvdGamePtr+1		;($FC0B)
		STX GameDataPointerUB   ;($FC0E)

		TAX					 ;($FC10)Is the base address for game 1 desired?
		BEQ FoundSaveGameBase   ;($FC11)If so, nothing mre to do.  Branch to exit.

		* JSR GetNxtSvGameBase  ;($FC13)($FC1C)Get the base address for the next save game data.
		DEX					 ;($FC16)Is this the base address for the save game desired?
		BNE -				   ;($FC17)If not, branch to go to next save game.

FoundSaveGameBase:
		PLA					 ;($FC19)
		TAX					 ;($FC1A)Restore value of X from the stack.
		RTS					 ;($FC1B)

;----------------------------------------------------------------------------------------------------

GetNxtSvGameBase:
		LDA GameDataPointerLB   ;($FC1C)
		CLC					 ;($FC1E)
		ADC #$40				;($FC1F)
		STA GameDataPointerLB   ;($FC21)Add #$140 to current save game base addres
		LDA GameDataPointerUB   ;($FC23)to find the base of the next saved game.
		ADC #$01				;($FC25)
		STA GameDataPointerUB   ;($FC27)
		RTS					 ;($FC29)

;----------------------------------------------------------------------------------------------------

DoLFSR:
		TYA					 ;($FC2A)Save Y.
		PHA					 ;($FC2B)

		LDY #$08				;($FC2C)
		* LDA CRCUB			 ;($FC2E)
		EOR GenByte3C		   ;($FC30)
		ASL CRCLB			   ;($FC32)
		ROL CRCUB			   ;($FC34)
		ASL GenByte3C		   ;($FC36)
		ASL					 ;($FC38)Some kind of linear feedback shift register I think.
		BCC +				   ;($FC39)The saved data is run though this function and a 16-bit
		LDA CRCLB			   ;($FC3B)CRC appears to be generated.
		EOR #$21				;($FC3D)
		STA CRCLB			   ;($FC3F)
		LDA CRCUB			   ;($FC41)
		EOR #$10				;($FC43)
		STA CRCUB			   ;($FC45)
		* DEY				   ;($FC47)
		BNE --				  ;($FC48)

		PLA					 ;($FC4A)
		TAY					 ;($FC4B)Restore Y.
		RTS					 ;($FC4C)

;----------------------------------------------------------------------------------------------------

ClearWinBufRAM:
		LDA #TL_BLANK_TILE1	 ;($FC4D)Fill buffer with Blank tiles.

		LDX #$00				;($FC4F)
		* STA WinBufRAM,X	   ;($FC51)Clear RAM $0400-$04FF
		DEX					 ;($FC54)
		BNE -				   ;($FC55)

		LDX #$00				;($FC57)
		* STA WinBufRAM+$100,X  ;($FC59)Clear RAM $0500-$05FF
		DEX					 ;($FC5C)
		BNE -				   ;($FC5D)

		LDX #$00				;($FC5F)
		* STA WinBufRAM+$200,X  ;($FC61)Clear RAM $0600-$06FF
		DEX					 ;($FC64)
		BNE -				   ;($FC65)

		LDX #$00				;($FC67)
		* STA WinBufRAM+$300,X  ;($FC69)
		INX					 ;($FC6C)Clear RAM $0700-$07BF
		CPX #$C0				;($FC6D)
		BCC -				   ;($FC6F)
		RTS					 ;($FC71)

;----------------------------------------------------------------------------------------------------

CrntGamePtr:
		.word CurrentGameDat	;($FC72)($6048)Data collection point for current game.

SvdGamePtr:
		.word SavedGame1		;($FC74)($6068)Base address for the 3 save game slots.

KenMasutaTbl:
;			  K	E	N	_	M	A	S	U	T	A
		.byte $4B, $45, $4E, $20, $4D, $41, $53, $55, $54, $41;($FC76)

;----------------------------------------------------------------------------------------------------

LoadMMCPRGBank3:
		PHA					 ;($FC80)Save A.
		LDA #PRG_BANK_3		 ;($FC81)Prepare to load PRG bank 3.
		JSR MMC1LoadPRG		 ;($FC83)($FF96)Load PRG bank 3.
		PLA					 ;($FC86)Restore A.
		RTS					 ;($FC87)

;----------------------------------------------------------------------------------------------------

MMCShutdown:
		PHA					 ;($FC88)Save A.

		LDA #PRG_B3_NO_RAM	  ;($FC89)Prepare to load PRG bank 3 and disable the PRG RAM.
		STA ActiveBank		  ;($FC8B)
		JSR MMC1LoadPRG		 ;($FC8E)($FF96)Load bank 3.

		LDA #%00001000		  ;($FC91)Disable NMI.
		STA PPUControl0		 ;($FC93)

		PLA					 ;($FC96)Restore A.
		RTS					 ;($FC97)

;----------------------------------------------------------------------------------------------------

Bank1ToNT0:
		PHA					 ;($FC98)Save A on stack.
		LDA #CHR_BANK_1		 ;($FC99)Indicate CHR ROM bank 1 to be loaded.

SetActiveNT0:
		STA ActiveNT0		   ;($FC9B)
		JSR MMC1LoadNT0		 ;($FC9E)($FFAC)load nametable 0 with CHR ROM bank 1.
		PLA					 ;($FCA1)
		RTS					 ;($FCA2)Restore A before returning.

Bank0ToNT0:
		PHA					 ;($FCA3)Save A on stack.
		LDA #CHR_BANK_0		 ;($FCA4)Indicate CHR ROM bank 0 to be loaded.
		BEQ SetActiveNT0		;($FCA6)Load it into nametable 0.

		PHA					 ;($FCA8)Indicate CHR ROM bank 0 to be loaded.
		LDA #CHR_BANK_0		 ;($FCA9)
		BEQ SetActiveNT1		;($FCAB)Load it into nametable 1.

Bank2ToNT1:
		PHA					 ;($FCAD)Indicate CHR ROM bank 2 to be loaded.
		LDA #CHR_BANK_2		 ;($FCAE)

SetActiveNT1:
		STA ActiveNT1		   ;($FCB0)
		JSR MMC1LoadNT1		 ;($FCB3)($FFC2)load nametable 1.
		PLA					 ;($FCB6)Restore A and return.
		RTS					 ;($FCB7)

Bank3ToNT1:
		PHA					 ;($FCB8)
		LDA #CHR_BANK_3		 ;($FCB9)Indicate CHR ROM bank 3 to be loaded.
		BNE SetActiveNT1		;($FCBB)

;----------------------------------------------------------------------------------------------------

RunBankFunction:
		STA IRQStoreA		   ;($FCBD)
		STX IRQStoreX		   ;($FCBF)
		LDA ActiveBank		  ;($FCC1)Save register values and active PRG bank on stack.
		PHA					 ;($FCC4)
		PHP					 ;($FCC5)

		LDA ActiveBank		  ;($FCC6)Unused variable.
		STA WindowUnused6006	;($FCC9)

		JSR GetDataPtr		  ;($FCCC)($FCEC)Get pointer to desired data.
		LDA #$4C				;($FCCF)Prepare to jump. #$4C is the opcode for JUMP.
		STA _JMPFuncPtr		 ;($FCD1)

		LDX IRQStoreX		   ;($FCD3)
		LDA IRQStoreA		   ;($FCD5)Restore registers and processor status.
		PLP					 ;($FCD7)

		JSR JMPFuncPtr		  ;($FCD8)Call bank function.

		PHP					 ;($FCDB)Save A and processor status.
		STA IRQStoreA		   ;($FCDC)

		PLA					 ;($FCDE)Load bank number to return to.
		STA NewPRGBank		  ;($FCDF)

		PLA					 ;($FCE1)Prepare to load original PRG bank back into memory.
		JSR SetPRGBankAndSwitch ;($FCE2)($FF91)Restore original PRG bank.

		LDA NewPRGBank		  ;($FCE5)Load active PRG bank number.
		PHA					 ;($FCE7)
		LDA IRQStoreA		   ;($FCE8)
		PLP					 ;($FCEA)Restore variables before returning.
		RTS					 ;($FCEB)

;----------------------------------------------------------------------------------------------------

GetDataPtr:
		LDA NewPRGBank		  ;($FCEC)Load bank number to switch to.
		JSR SetPRGBankAndSwitch ;($FCEE)($FF91)Switch to new PRG bank.
		LDA BankPtrIndex		;($FCF1)Load index into BankPointer table.
		ASL					 ;($FCF3)*2.

		TAX					 ;($FCF4)
		LDA BankPointers,X	  ;($FCF5)
		STA BankPntrLB		  ;($FCF8)Get base address of desired data.
		LDA BankPointers+1,X	;($FCFA)
		STA BankPntrUB		  ;($FCFD)
		RTS					 ;($FCFF)

GetAndStrDatPtr:
		STA IRQStoreA		   ;($FD00)Save current values of A and X.
		STX IRQStoreX		   ;($FD02)

		LDA ActiveBank		  ;($FD04)Store current active PRG bank.
		PHA					 ;($FD07)
		JSR GetDataPtr		  ;($FD08)($FCEC)Get pointer to desired data.

		PLA					 ;($FD0B)Switch back to original PRG bank.
		JSR SetPRGBankAndSwitch ;($FD0C)($FF91)Switch to new PRG bank.

		LDX IRQStoreX		   ;($FD0F)Restore X.
		LDA BankPntrLB		  ;($FD11)
		STA GenPtr00LB,X		;($FD13)Transfer retreived pointer to a
		LDA BankPntrUB		  ;($FD15)general purpose pointer address.
		STA GenPtr00UB,X		;($FD17)
		LDA IRQStoreA		   ;($FD19)Restore A.
		RTS					 ;($FD1B)

GetBankDataByte:
		STA IRQStoreA		   ;($FD1C)Save current value of A.
		LDA ActiveBank		  ;($FD1E)Store current active PRG bank.
		PHA					 ;($FD21)
		LDA IRQStoreA		   ;($FD22)Restore A. It contains the bank to switch to.
		JSR SetPRGBankAndSwitch ;($FD24)($FF91)Switch to new PRG bank.

		LDA GenPtr00LB,X		;($FD27)
		STA BankDatPtrLB		;($FD29)
		LDA GenPtr00UB,X		;($FD2B)Get data byte from desired bank and store in A.
		STA BankDatPtrUB		;($FD2D)
		LDA (BankDatPtr),Y	  ;($FD2F)

		STA IRQStoreA		   ;($FD31)Save current value of A.

		PLA					 ;($FD33)Switch back to original PRG bank.
		JSR SetPRGBankAndSwitch ;($FD34)($FF91)Switch to PRG bank function is on.

		LDA IRQStoreA		   ;($FD37)Place data byte retreived in A.
		RTS					 ;($FD39)

;----------------------------------------------------------------------------------------------------

IRQ:
		SEI					 ;($FD3A)Disable IRQs.
		PHP					 ;($FD3B)Push processor status. Not necessary. Done by interrupt.
		BIT APUCommonControl0   ;($FD3C)Appears to have no effect.

		STA IRQStoreA		   ;($FD3F)
		STX IRQStoreX		   ;($FD41)Save A, X, and Y.
		STY IRQStoreY		   ;($FD43)

		TSX					 ;($FD45)Get stack pointer.
		LDA BankFuncDatLB,X	 ;($FD46)
		SEC					 ;($FD49)Get return address from the stack
		SBC #$01				;($FD4A)and subtract 1.  This points to the
		STA _BankFuncDatLB	  ;($FD4C)first data byte after the BRK
		LDA BankFuncDatUB,X	 ;($FD4E)instruction.
		SBC #$00				;($FD51)
		STA _BankFuncDatUB	  ;($FD53)Save pointer to this byte in $33 and $34.

		LDY #$01				;($FD55)
		LDA (_BankFuncDatPtr),Y ;($FD57)Get Second byte after BRK and save on stack.
		PHA					 ;($FD59)

		AND #$08				;($FD5A)If bit 3 is set, set the carry bit.
		CMP #$08				;($FD5C)If carry bit set, get data only, do not run function.

		PLA					 ;($FD5E)Restore data byte.
		ROR					 ;($FD5F)
		LSR					 ;($FD60)
		LSR					 ;($FD61)Get upper nibble. It contains PRG bank to switch to.
		LSR					 ;($FD62)
		STA NewPRGBank		  ;($FD63)

		DEY					 ;($FD65)Get first byte after the BRK instruction.
		LDA (_BankFuncDatPtr),Y ;($FD66)
		BMI GetBankData		 ;($FD68)Branch if MSB set. Only get data byte.

		STA BankPtrIndex		;($FD6A)Save index into BankPointers table.

		LDY IRQStoreY		   ;($FD6C)Restore Y.
		LDX IRQStoreX		   ;($FD6E)Restore X.
		PLP					 ;($FD70)Restore processor status.
		PLA					 ;($FD71)Discard extra processor status byte.
		LDA IRQStoreA		   ;($FD72)Restore A
		JMP RunBankFunction	 ;($FD74)($FCBD)Run the desired bank function.

GetBankData:
		* AND #$3F			  ;($FD77)Remove upper bit.
		STA BankPtrIndex		;($FD79)Save index into BankPointers table.

		LDY IRQStoreY		   ;($FD7B)Restore Y.
		LDX IRQStoreX		   ;($FD7D)Restore X.
		PLP					 ;($FD7F)Restore processor status.
		PLA					 ;($FD80)Discard extra processor status byte.
		LDA IRQStoreA		   ;($FD81)Restore A
		JMP GetAndStrDatPtr	 ;($FD83)($FD00)Get data pointer.

;----------------------------------------------------------------------------------------------------

DoReset:
		CLD					 ;($FD86)Put processor in binary mode.
		LDA #%00010000		  ;($FD87)Turn off VBlank interrupt, BG pattern table 1.
		STA PPUControl0		 ;($FD89)

		* LDA PPUStatusus	   ;($FD8C)
		BMI -				   ;($FD8F)Loop until not in VBlank. Clears the address latch.
		* LDA PPUStatusus	   ;($FD91)
		BPL -				   ;($FD94)Wait until VBlank starts.
		* LDA PPUStatusus	   ;($FD96)
		BMI -				   ;($FD99)In VBlank.  Bit should be clear on second read.

		LDA #%00000000		  ;($FD9B)Turn off the display.
		STA PPUControl1		 ;($FD9D)

		LDX #$FF				;($FDA0)Manually reset stack pointer.
		TXS					 ;($FDA2)

		TAX					 ;($FDA3)
		STA UpdateBGTiles	   ;($FDA4)Clear update background tiles byte.
		* STA $00,X			 ;($FDA7)
		STA BlockRAM,X		  ;($FDA9)
		STA WinBufRAM,X		 ;($FDAC)Clear internal NES RAM.
		STA WinBufRAM+$0100,X   ;($FDAF)
		STA WinBufRAM+$0200,X   ;($FDB2)
		STA WinBufRAM+$0300,X   ;($FDB5)
		INX					 ;($FDB8)
		BNE -				   ;($FDB9)

		JSR LoadMMCPRGBank3	 ;($FDBB)($FC80)Make sure PRG bank 3 is loaded.
		STA ActiveBank		  ;($FDBE)Should always store PRG bank 0 as active bank.

		LDA #%00011110		  ;($FDC1)16KB PRG banks, 4KB CHR banks, vertical mirroring.
		STA MMC1Config		  ;($FDC3)

		LDA #$00				;($FDC6)
		STA ActiveNT0		   ;($FDC8)Prepare to load the nametables.
		STA ActiveNT1		   ;($FDCB)
		JSR DoMMC1			  ;($FDCE)($FDF4)Program the MMC1 chip.

		LDA PPUStatusus		 ;($FDD1)Clear PPU address latch.
		LDA #$10				;($FDD4)
		STA PPUAddress		  ;($FDD6)
		LDA #$00				;($FDD9)Set PPU address to start of pattern table 1.
		STA PPUAddress		  ;($FDDB)

		LDX #$10				;($FDDE)
		* STA PPUIOReg		  ;($FDE0)Clear lower 16 bytes of pattern table 1.
		DEX					 ;($FDE3)
		BNE -				   ;($FDE4)

		LDA #%10001000		  ;($FDE6)Turn on VBlank interrupts, set sprites
		STA PPUControl0		 ;($FDE8)to pattern table 1.
		JSR ClearSpriteRAM	  ;($FDEB)($C6BB)Clear sprite RAM.
		JSR WaitForNMI		  ;($FDEE)($FF74)Wait for VBlank.
		JMP ContinueReset	   ;($FDF1)($C9B5)Continue the reset process.

;----------------------------------------------------------------------------------------------------

DoMMC1:
		INC $FFDF			   ;($FDF4)Reset MMC1 chip.
		LDA MMC1Config		  ;($FDF7)Configure MMC1 chip.
		JSR MMC1LoadConfig	  ;($FDFA)($FE09)Load the configuration for the MMC1 controller.
		LDA ActiveNT0		   ;($FDFD)Get CHR ROM bank to load into nametable 0.
		JSR MMC1LoadNT0		 ;($FE00)($FFAC)load nametable 0.
		LDA ActiveNT1		   ;($FE03)Get CHR ROM bank to load into nametable 1.
		JMP MMC1LoadNT1		 ;($FE06)($FFC2)load nametable 1.

MMC1LoadConfig:
		STA MMC1Config		  ;($FE09)
		STA MMCCfg			  ;($FE0C)
		LSR					 ;($FE0F)
		STA MMCCfg			  ;($FE10)
		LSR					 ;($FE13)
		STA MMCCfg			  ;($FE14)Load the configuration for the MMC1 controller.
		LSR					 ;($FE17)
		STA MMCCfg			  ;($FE18)
		LSR					 ;($FE1B)
		STA MMCCfg			  ;($FE1C)
		RTS					 ;($FE1F)

UpdateBG:
		LDY #$01				;($FE20)MSB set indicates PPU control byte.
		LDA BlockRAM,X		  ;($FE22)Is this a PPU control byte?
		BPL LoadBGDat		   ;($FE25)If not, branch to load as PPU data byte.

		TAY					 ;($FE27)This PPU data byte has PPU control info in it.
		LSR					 ;($FE28)
		LSR					 ;($FE29)Move upper nibble to lower nibble.
		LSR					 ;($FE2A)
		LSR					 ;($FE2B)
		AND #$04				;($FE2C)
		ORA #$88				;($FE2E)Isolate bit used to control address increment
		STA PPUControl0		 ;($FE30)and apply it to the current PPU settings.

		TYA					 ;($FE33)Next data byte is a counter for repeating tile data loads.
		INX					 ;($FE34)Store that byte in Y. only applicable if control bit flag is set.
		LDY BlockRAM,X		  ;($FE35)

LoadBGDat:
		INX					 ;($FE38)Move to next index in buffer.
		AND #$3F				;($FE39)Remove any PPU control bits from byte.

		STA PPUAddress		  ;($FE3B)
		LDA BlockRAM,X		  ;($FE3E)Set PPU address for data load.
		INX					 ;($FE41)
		STA PPUAddress		  ;($FE42)

		* LDA BlockRAM,X		;($FE45)Get next data byte for PPU load.
		INX					 ;($FE48)
		STA PPUIOReg			;($FE49)Store byte in PPU.
		DEY					 ;($FE4C)More data to load for this entry?
		BNE -				   ;($FE4D)If so, branch to get next byte.

		DEC PPUEntryCount	   ;($FE4F)Is there another PPU entry to load?
		BNE UpdateBG			;($FE51)If so, branch to get the next entry.

		BEQ ProcessVBlank2	  ;($FE53)Done with Background updates. Move on.

;----------------------------------------------------------------------------------------------------

NotVBlankReady:
		JSR SetPPUValues		;($FE55)($FF2D)Set scroll values, background color and active nametable.
		LDA #$02				;($FE58)Set sprite RAM to address $0200.
		STA SPRDMAReg		   ;($FE5A)
		JMP DoFrameUpdates	  ;($FE5D)($FEE0)Do mandatory frame checks and updates.

;----------------------------------------------------------------------------------------------------

SetSprtRAM:
		LDA #$02				;($FE60)Set sprite RAM to address $0200.
		STA SPRDMAReg		   ;($FE62)
		BNE ProcessVBlank2	  ;($FE65)Jump to do more VBlank stuff.

;----------------------------------------------------------------------------------------------------

NMI:
		PHA					 ;($FE67)
		TXA					 ;($FE68)
		PHA					 ;($FE69)Store register values on the stack.
		TYA					 ;($FE6A)
		PHA					 ;($FE6B)
		TSX					 ;($FE6C)

		LDA Stack-10,X		  ;($FE6D)
		CMP #>WaitForNMI		;($FE70)
		BNE NotVBlankReady	  ;($FE72)Get return address from the stack and check
		LDA Stack-11,X		  ;($FE74)If program was not idle waiting for VBlank.
		CMP #<WaitForNMI+3	  ;($FE77)
		BCC NotVBlankReady	  ;($FE79)
		CMP #<WaitForNMI+9	  ;($FE7B)Do less processing if not VBlank ready.
		BCS NotVBlankReady	  ;($FE7D)

		LDA PPUStatusus		 ;($FE7F)No effect.
		INC FrameCounter		;($FE82)Increment frame counter.

		LDA PPUEntryCount	   ;($FE84)Are there PPU entries waiting to be loaded into the PPU?
		BEQ SetSprtRAM		  ;($FE86)If not, branch to do sprite stuff.

		CMP #$08				;($FE88)Are there more than 8 PPU entries to load?
		BCS ChkBGUpdates		;($FE8A)If so, branch.

		LDA #$02				;($FE8C)Set sprite RAM to address $0200.
		STA SPRDMAReg		   ;($FE8E)

ChkBGUpdates:
		LDX #$00				;($FE91)Set index to beginning of buffer.
		LDA UpdateBGTiles	   ;($FE93)Do background tiles need to be updated?
		BMI UpdateBG			;($FE96)If so, branch.

		* LDA BlockRAM,X		;($FE98)
		STA PPUAddress		  ;($FE9B)
		LDA BlockRAM+1,X		;($FE9E)
		STA PPUAddress		  ;($FEA1)
		LDA BlockRAM+2,X		;($FEA4)
		STA PPUIOReg			;($FEA7)Load PPU buffer contents into PPU.
		INX					 ;($FEAA)
		INX					 ;($FEAB)
		INX					 ;($FEAC)
		CPX PPUBufCount		 ;($FEAD)
		BNE -				   ;($FEAF)

ProcessVBlank2:
		LDA #$3F				;($FEB1)Prepare to write to the PPU palettes.
		STA PPUAddress		  ;($FEB3)

		LDA #$00				;($FEB6)
		STA NMIStatusus		 ;($FEB8)
		STA PPUEntryCount	   ;($FEBA)Clear status variables.
		STA PPUBufCount		 ;($FEBC)
		STA UpdateBGTiles	   ;($FEBE)

		STA PPUAddress		  ;($FEC1)
		LDA #$0F				;($FEC4)Set universal background color to black.
		STA PPUIOReg			;($FEC6)

		LDA ActiveNmTbl		 ;($FEC9)
		BNE +				   ;($FECB)
		LDA #%10001000		  ;($FECD)Set active name table.
		BNE ++				  ;($FECF)
		* LDA #%10001001		;($FED1)
		* STA PPUControl0	   ;($FED3)

		LDA ScrollX			 ;($FED6)
		STA PPUScroll		   ;($FED8)Set scroll registers.
		LDA ScrollY			 ;($FEDB)
		STA PPUScroll		   ;($FEDD)

DoFrameUpdates:
		JSR DoMMC1			  ;($FEE0)($FDF4)Program the MMC1 chip.
		LDA SoundEngineStatus   ;($FEE3)Is sound engine busy?
		BNE DoFrameUpdates2	 ;($FEE6)If so, branch to skip updating sounds.

		LDA #PRG_BANK_1		 ;($FEE8)Prepare to access sound engine.
		JSR MMC1LoadPRG		 ;($FEEA)($FF96)Load PRG bank 1.
		JSR UpdateSound		 ;($FEED)($8028)Update music or SFX.

DoFrameUpdates2:
		LDA ActiveBank		  ;($FEF0)Get active PRG bank.
		JSR SetPRGBankAndSwitch ;($FEF3)($FF91)Switch to new PRG bank.

		TSX					 ;($FEF6)
		LDA Stack-$A,X		  ;($FEF7)Get upper byte of interrupt return address.
		STA NMIPtrUB			;($FEFA)

		CMP #>MMC1LoadPRG	   ;($FEFC)Is upper byte of return address within the range of the
		BNE ChkValidInst		;($FEFE)MMC PRG functions? If not, branch to move on.

		LDA Stack-$B,X		  ;($FF00)Get lower byte of interrupt return address.

		CMP #<MMC1LoadPRG	   ;($FF03)Is lower byte of return address within the range of the
		BCC ChkValidInst		;($FF05)MMC PRG functions? If not, branch to move on.

		CMP #<MMC1LoadNT1+$14   ;($FF07)Is lower byte of return address within the range of the
		BCS ChkValidInst		;($FF09)MMC PRG functions? If not, branch to move on.

		LDA #<MMC1LoadNT1+$14   ;($FF0B)MMC was being accessed when interrupt happened.
		STA Stack-$B,X		  ;($FF0D)Set return address to end of MMC functions.

ChkValidInst:
		LDA Stack-$B,X		  ;($FF10)Get lower byte of interrupt return address.
		STA NMIPtrLB			;($FF13)

		LDY #$00				;($FF15)Does data at return address have 7 as the lower nibble?
		LDA (NMIPtr),Y		  ;($FF17)
		AND #$0F				;($FF19)
		CMP #$07				;($FF1B)If so, do not do IRQ routines.  No valid instruction
		BEQ PrepForIRQFuncs	 ;($FF1D)has 7 as the lower nibble.  Could be a data byte.

		PLA					 ;($FF1F)
		TAY					 ;($FF20)
		PLA					 ;($FF21)Restore register values and return.
		TAX					 ;($FF22)
		PLA					 ;($FF23)
		RTI					 ;($FF24)

PrepForIRQFuncs:
		PLA					 ;($FF25)
		TAY					 ;($FF26)
		PLA					 ;($FF27)Restore values before running IRQ routines.
		TAX					 ;($FF28)
		PLA					 ;($FF29)
		JMP IRQ				 ;($FF2A)($FD3A)IRQ vector.

;----------------------------------------------------------------------------------------------------

SetPPUValues:
		LDA #$3F				;($FF2D)
		STA PPUAddress		  ;($FF2F)
		LDA #$00				;($FF32)Set universal background color to black.
		STA PPUAddress		  ;($FF34)
		LDA #$0F				;($FF37)
		STA PPUIOReg			;($FF39)

		LDA ActiveNmTbl		 ;($FF3C)Get which nametable is supposed to be active.
		BNE SetNT1			  ;($FF3E)Is it nametable 1? If so, branch to set.

		LDA #%10001000		  ;($FF40)Set nametable 0 as active nametable.
		BNE SetScrollRegisters  ;($FF42)Branch always.

SetNT1:
		LDA #%10001001		  ;($FF44)Set nametable 1 as active nametable.

SetScrollRegisters:
		STA PPUControl0		 ;($FF46)
		LDA ScrollX			 ;($FF49)
		STA PPUScroll		   ;($FF4B)Set scroll registers.
		LDA ScrollY			 ;($FF4E)
		STA PPUScroll		   ;($FF50)
		RTS					 ;($FF53)

;----------------------------------------------------------------------------------------------------

;Unused.
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($FF54)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($FF64)

;----------------------------------------------------------------------------------------------------

WaitForNMI:
		LDA #$01				;($FF74)
		STA NMIStatusus		 ;($FF76)
		* LDA NMIStatusus	   ;($FF78)Loop until NMI has completed.
		BNE -				   ;($FF7A)
		RTS					 ;($FF7C)

;----------------------------------------------------------------------------------------------------

;Unused.
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($FF7D)
		.byte $FF			   ;($FF8D)

;----------------------------------------------------------------------------------------------------

_DoReset:
		JMP DoReset			 ;($FF8E)($FD86)Reset game.

;----------------------------------------------------------------------------------------------------

SetPRGBankAndSwitch:
		STA ActiveBank		  ;($FF91)
		NOP					 ;($FF94)Store active PRG bank number
		NOP					 ;($FF95)and drop into the routine below.

MMC1LoadPRG:
		STA MMCPRG			  ;($FF96)
		LSR					 ;($FF99)
		STA MMCPRG			  ;($FF9A)
		LSR					 ;($FF9D)
		STA MMCPRG			  ;($FF9E)
		LSR					 ;($FFA1)Change the program ROM bank.
		STA MMCPRG			  ;($FFA2)
		LSR					 ;($FFA5)
		STA MMCPRG			  ;($FFA6)
		NOP					 ;($FFA9)
		NOP					 ;($FFAA)
		RTS					 ;($FFAB)

MMC1LoadNT0:
		STA MMCCHR0			 ;($FFAC)
		LSR					 ;($FFAF)
		STA MMCCHR0			 ;($FFB0)
		LSR					 ;($FFB3)
		STA MMCCHR0			 ;($FFB4)
		LSR					 ;($FFB7)Change nametable 0.
		STA MMCCHR0			 ;($FFB8)
		LSR					 ;($FFBB)
		STA MMCCHR0			 ;($FFBC)
		NOP					 ;($FFBF)
		NOP					 ;($FFC0)
		RTS					 ;($FFC1)

MMC1LoadNT1:
		STA MMCCHR1			 ;($FFC2)
		LSR					 ;($FFC5)
		STA MMCCHR1			 ;($FFC6)
		LSR					 ;($FFC9)
		STA MMCCHR1			 ;($FFCA)
		LSR					 ;($FFCD)Change nametable 1.
		STA MMCCHR1			 ;($FFCE)
		LSR					 ;($FFD1)
		STA MMCCHR1			 ;($FFD2)
		NOP					 ;($FFD5)
		NOP					 ;($FFD6)
		RTS					 ;($FFD7)

;----------------------------------------------------------------------------------------------------

RESET:
		SEI					 ;($FFD8)Disable interrupts.
		INC MMCReset2		   ;($FFD9)Reset MMC1 chip.
		JMP DoReset			 ;($FFDC)($FD86)Continue with the reset process.

;----------------------------------------------------------------------------------------------------

;				   D	R	A	G	O	N	_	W	A	R	R	I	O	R
		.byte $80, $44, $52, $41, $47, $4F, $4E, $20, $57, $41, $52, $52, $49, $4F, $52, $20;($FFDF)
		.byte $20, $56, $DE, $30, $70, $01, $04, $01, $0F, $07, $44;($FFEF)

		.word NMI			   ;($FFFA)($FE67)NMI vector.
		.word RESET			 ;($FFFC)($FFD8)Reset vector.
		.word IRQ			   ;($FFFE)($FD3A)IRQ vector.