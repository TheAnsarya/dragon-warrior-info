.org $8000

.include "Dragon_Warrior_Defines.asm"

;--------------------------------------[ Forward declarations ]--------------------------------------

.alias ClearPPU				 $C17A
.alias CalcPPUBufferAddr		   $C596
.alias GetJoypadStatus		  $C608
.alias AddPPUBufferEntry		   $C690
.alias ClearSpriteRAM		   $C6BB
.alias DoWindow				 $C6F0
.alias DoDialogHiBlock		  $C7C5
.alias WindowLoadGameDat		   $F685
.alias Bank0ToCHR0			  $FCA3
.alias GetAndStrDatPtr		  $FD00
.alias GetBankDataByte		  $FD1C
.alias WaitForNMI			   $FF74
.alias _DoReset				 $FF8E

;-----------------------------------------[ Start of code ]------------------------------------------

;The following table contains functions called from bank 3 through the IRQ interrupt.

BankPointers:
BankPtr_Word_8000:  .word WindowEraseParams	;($AF24)Get parameters for removing windows from the screen.
BankPtr_Word_8002:  .word WindowShowHide	   ;($ABC4)Show/hide window on the screen.
BankPtr_Word_8004:  .word ClearSoundRegisters	;($8178)Silence all sound.
BankPtr_Word_8006:  .word WaitForMusicEnd   ;($815E)Wait for the music clip to end.
BankPtr_Word_8008:  .word InitMusicSFX	  ;($81A0)Initialize new music/SFX.
BankPtr_Word_800A:  .word ExitGame		  ;($9362)Shut down game after player chooses not to continue.
BankPtr_Word_800C:  .word NULL			  ;Unused.
BankPtr_Word_800E:  .word NULL			  ;Unused.
BankPtr_Word_8010:  .word CopyTreasureTable	   ;($994F)Copy treasure table into RAM.
BankPtr_Word_8012:  .word NULL					;Unused.
BankPtr_Word_8014:  .word CopyROMToRAM			;($9981)Copy a ROM table into RAM.
.word EnemySpritesPointerTable   ;($99E4)Table of pointers to enemy sprites.
BankPtr_Word_8018:  .word LoadEnemyStats	;($9961)Load enemy stats when initiaizing a battle.
BankPtr_Word_801A:  .word SetBaseStats	  ;($99B4)Get player's base stats for their level.
BankPtr_Word_801C:  .word DoEndCredits	  ;($939A)Show end credits.
BankPtr_Word_801E:  .word NULL			  ;Unused.
BankPtr_Word_8020:  .word ShowWindow		;($A194)Display a window.
BankPtr_Word_8022:  .word WindowEnterName	  ;($AE02)Do name entering functions.
BankPtr_Word_8024:  .word DoDialog		  ;($B51D)Display in-game dialog.
BankPtr_Word_8026:  .word NULL			  ;Unused.

;-------------------------------------------[Sound Engine]-------------------------------------------

UpdateSound:
PHA					 ;
TXA					 ;
		PHA					 ;($802A)Store X, Y and A.
TYA					 ;
PHA					 ;

LDX #MCTL_NOIS_SW	   ;Noise channel software regs index.
		LDY #MCTL_SQ2_HW		;($802F)SQ2 channel hardware regs index.
LDA SFXActive		   ;Is an SFX active?
BEQ +				   ;If not, branch to skip SFX processing.

LDA NoteOffset		  ;
PHA					 ;Save a copy of note offset and then clear
LDA #$00				;it as it is not used in SFX processing.
STA NoteOffset		  ;

JSR GetNextNote		 ;($80CB)Check to see if time to get next channel note.
TAX					 ;

PLA					 ;Restore note offset value.
STA NoteOffset		  ;

		TXA					 ;($8043)Is SFX still processing?
BNE +				   ;If so, branch to continue or else reset noise and SQ2.

LDA #%00000101		  ;Silence SQ2 and noise channels.
		STA APUCommonControl0   ;($8048)
LDA #%00001111		  ;Enable SQ1, SQ2, TRI and noise channels.
		STA APUCommonControl0   ;($804D)

LDA SQ2Config		   ;Update SQ2 control byte 0.
		STA SQ2Cntrl0		   ;($8052)

LDA #%00001000		  ;Disable sweep generator on SQ2.
		STA SQ2Cntrl1		   ;($8057)

LDA #%00110000		  ;Turn off volume for noise channel.
		STA NoiseControl0	   ;($805C)

* LDA TempoCounter		   ;Tempo counter has the effect of slowing down the length
		CLC					 ;($8061)The music plays.  If the tempo is less than 150, the
ADC Tempo			   ;amount it slows down is linear.  For example, if tempo is
STA TempoCounter		   ;125, the music will slow down by 150/125 = 1.2 times.
		BCC SoundUpdateEnd	  ;($8066)The values varies if tempo is greater than 150.

SBC #$96				;Subtract 150 from tempo counter.
STA TempoCounter		   ;

LDX #MCTL_TRI_SW		;TRI channel software regs index.
LDY #MCTL_TRI_HW		;TRI channel hardware regs index.
		JSR GetNextNote		 ;($8070)($80CB)Check to see if time to get next channel note.

LDX #MCTL_SQ2_SW		;SQ2 channel software regs index.
		LDY #MCTL_SQ2_HW		;($8075)SQ2 channel hardware regs index.
LDA SFXActive		   ;Is an SFX currenty active?
BEQ +				   ;If not, branch.

LDY #MCTL_DMC_HW		;Set hardware register index to DMC regs (not used).
* JSR GetNextNote		 ;($80CB)Check to see if time to get next channel note.

LDX #MCTL_SQ1_SW		;SQ1 channel software regs index.
LDY #MCTL_SQ1_HW		;SQ1 channel hardware regs index.
		JSR GetNextNote		 ;($8084)($80CB)Check to see if time to get next channel note.

SoundUpdateEnd:
LDY #$00				;
		LDA (SQ1IndexLB),Y	  ;($8089)Update music trigger value.
STA MusicTrigger		;

		PLA					 ;($808E)
TAY					 ;
PLA					 ;Restore X, Y and A.
TAX					 ;
PLA					 ;
		RTS					 ;($8093)

;----------------------------------------------------------------------------------------------------

MusicReturn:
LDA SQ1ReturnLB,X	   ;
STA SQ1IndexLB,X		;Load return address into sound channel
		LDA SQ1ReturnUB,X	   ;($8098)data address.  Process byte if not $00.
STA SQ1IndexUB,X		;
BNE ProcessAudioByte	;

;----------------------------------------------------------------------------------------------------

LoadMusicNote:
CLC					 ;Add any existing offset into note table.
ADC NoteOffset		  ;Used to change the sound of various dungeon levels.

ASL					 ;*2.  Each table value is 2 bytes.
		STX MusicTemp		   ;($80A2)Save X.
TAX					 ;Use calculated value as index into note table.

LDA MusicalNotesTbl,X   ;
STA SQ1Cntrl2,Y		 ;Store note data bytes into its
LDA MusicalNotesTbl+1,X ;corresponding hardware registers.
STA SQ1Cntrl3,Y		 ;

		LDX MusicTemp		   ;($80B1)Restore X.
		CPX #MCTL_NOIS_SW	   ;($80B3)Is noise channel being processed?
		BEQ ProcessAudioByte	;($80B5)If so, branch to get next audio data byte.

		LDA ChannelQuiet,X	  ;($80B7)Is any quiet time between notes expired?
		BEQ ProcessAudioByte	;($80B9)If so, branch to get next audio byte.

		BNE UpdateChnlUsage	 ;($80BB)Wait for quiet time between notes to end. Branch always.

;----------------------------------------------------------------------------------------------------

ChannelQuietTime:
JSR GetAudioData		;($8155)Get next music data byte.
		STA ChannelQuiet,X	  ;($80C0)Store quiet time byte.
		JMP ProcessAudioByte	;($80C2)($80D3)Determine what to do with music data byte.

;----------------------------------------------------------------------------------------------------

EndChnlQuietTime:
		LDA #$00				;($80C5)Clear quiet time byte.
		STA ChannelQuiet,X	  ;($80C7)
BEQ ProcessAudioByte	;($80D3)Determine what to do with music data byte.

;----------------------------------------------------------------------------------------------------

GetNextNote:
		LDA ChannelLength,X	 ;($80CB)Is channel enabled?
		BEQ UpdateReturn		;($80CD)If not, branch to exit.

		DEC ChannelLength,X	 ;($80CF)Decrement length remaining.
		BNE UpdateReturn		;($80D1)Time to get new data? if not, branch to exit.

;----------------------------------------------------------------------------------------------------

ProcessAudioByte:
		JSR GetAudioData		;($80D3)($8155)Get next music data byte.
		CMP #MCTL_JUMP		  ;($80D6)
BEQ MusicJump		   ;Check if need to jump to new music data address.

		BCS ChangeTempo		 ;($80DA)Check if tempo needs to be changed.

		CMP #MCTL_NO_OP		 ;($80DC)Check if no-op byte.
		BEQ ProcessAudioByte	;($80DE)If so, branch to get next byte.

		BCS MusicReturn		 ;($80E0)Check if need to jump back to previous music data adddress.

CMP #MCTL_CNTRL1		;Check if channel control 1 byte.
		BEQ ChannelControl1	 ;($80E4)If so, branch to load config byte.

		BCS ChannelControl0	 ;($80E6)Check if channel control 0 byte.

		CMP #MCTL_NOISE_VOL	 ;($80E8)Check if noise channel volume control byte.
		BEQ NoiseVolume		 ;($80EA)If so, branch to load noise volume.

BCS GetNoteOffset	   ;Is this a note offset byte? If so, branch.

		CMP #MCTL_END_SPACE	 ;($80EE)Check if end quiet time between notes byte.
		BEQ EndChnlQuietTime	;($80F0)If so, branch to end quiet time.

		BCS ChannelQuietTime	;($80F2)Add quiet time between notes? if so branch to get quiet time.

CMP #MCTL_NOISE_CFG	 ;Is byte a noise channel config byte?
BCS LoadNoise		   ;If so, branch to configure noise channel.

		CMP #MCTL_NOTE		  ;($80F8)Is byte a musical note?
		BCS LoadMusicNote	   ;($80FA)If so, branch to load note.

;If no control bytes match the cases above, byte Is note length counter.

UpdateChnlUsage:
		STA ChannelLength,X	 ;($80FC)Update channel note counter.

UpdateReturn:
		RTS					 ;($80FE)Finished with current processing.

;----------------------------------------------------------------------------------------------------

ChangeTempo:
		JSR GetAudioData		;($80FF)($8155)Get next music data byte.
		STA Tempo			   ;($8102)Update music speed.
JMP ProcessAudioByte	;($80D3)Determine what to do with music data byte.

;----------------------------------------------------------------------------------------------------

MusicJump:
		JSR GetAudioData		;($8107)($8155)Get next music data byte.
PHA					 ;
		JSR GetAudioData		;($810B)($8155)Get next music data byte.
		PHA					 ;($810E)Get jump address from music data.
		LDA SQ1IndexLB,X		;($810F)
		STA SQ1ReturnLB,X	   ;($8111)
		LDA SQ1IndexUB,X		;($8113)Save current address in return address variables.
		STA SQ1ReturnUB,X	   ;($8115)
		PLA					 ;($8117)
		STA SQ1IndexUB,X		;($8118)Jump to new music data address and get data byte.
		PLA					 ;($811A)
		STA SQ1IndexLB,X		;($811B)
		JMP ProcessAudioByte	;($811D)($80D3)Determine what to do with music data byte.

;----------------------------------------------------------------------------------------------------

ChannelControl0:
		JSR GetAudioData		;($8120)($8155)Get next music data byte.
		CPX #$02				;($8123)Is SQ2 currently being handled?
		BNE +				   ;($8125)If not, branch to load into corresponding SQ register.

		STA SQ2Config		   ;($8127)Else store a copy of the data byte in SQ2 config register.

		* STA SQ1Cntrl0,Y	   ;($8129)Load control byte into corresponding control register.
		JMP ProcessAudioByte	;($812C)($80D3)Determine what to do with music data byte.

;----------------------------------------------------------------------------------------------------

NoiseVolume:
		JSR GetAudioData		;($812F)($8155)Get next music data byte.
STA NoiseControl0		 ;Set noise volume byte.
		JMP ProcessAudioByte	;($8135)($80D3)Determine what to do with music data byte.

;----------------------------------------------------------------------------------------------------

LoadNoise:
		AND #$0F				;($8138)Set noise period.
		STA NoiseControl2	   ;($813A)
		LDA #%00001000		  ;($813D)Set length counter to 1.
		STA NoiseControl3	   ;($813F)
BNE ProcessAudioByte	;($80D3)Determine what to do with music data byte.

;----------------------------------------------------------------------------------------------------

GetNoteOffset:
		JSR GetAudioData		;($8144)($8155)Get next music data byte.
		STA NoteOffset		  ;($8147)Get note offset byte.
		JMP ProcessAudioByte	;($8149)($80D3)Determine what to do with music data byte.

;----------------------------------------------------------------------------------------------------

ChannelControl1:
		JSR GetAudioData		;($814C)($8155)Get next music data byte.
		STA SQ1Cntrl1,Y		 ;($814F)Store byte in square wave config register.
		JMP ProcessAudioByte	;($8152)($80D3)Determine what to do with music data byte.

;----------------------------------------------------------------------------------------------------

GetAudioData:
		LDA (SQ1IndexLB,X)	  ;($8155)Get data byte from ROM.

IncAudioPtr:
		INC SQ1IndexLB,X		;($8157)
		BNE +				   ;($8159)Increment data pointer.
		INC SQ1IndexUB,X		;($815B)
* RTS					 ;

;----------------------------------------------------------------------------------------------------

WaitForMusicEnd:
		JSR WaitForNMI		  ;($815E)($FF74)Wait for VBlank interrupt.
		LDA #MCTL_NO_OP		 ;($8161)Load no-op character. Its also used for end of music segment.
		LDX #MCTL_SQ1_SW		;($8163)
		CMP (SQ1IndexLB,X)	  ;($8165)Is no-op found in SQ1 data? if so, end found.  Branch to end.
		BEQ +				   ;($8167)

		LDX #MCTL_NOIS_SW	   ;($8169)
		CMP (SQ1IndexLB,X)	  ;($816B)Is no-op found in noise data? if so, end found.  Branch to end.
		BEQ +				   ;($816D)

		LDX #MCTL_TRI_SW		;($816F)
		CMP (SQ1IndexLB,X)	  ;($8171)Is no-op found in triangel data? if so, end found.  Branch to end.
		BNE WaitForMusicEnd	 ;($8173)
		* JMP IncAudioPtr	   ;($8175)($8157)Increment audio data pointer.

;----------------------------------------------------------------------------------------------------

ClearSoundRegisters:
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

		LDA #$00				;($817B)
		STA DMCControl0		 ;($817D)Clear hardware control registers.
		STA APUCommonControl1   ;($8180)
		STA APUCommonControl0   ;($8183)

STA SQ1Length		   ;
		STA SQ2Length		   ;($8188)Indicate the channels are not in use.
		STA TRILength		   ;($818A)

STA SFXActive		   ;No SFX active.

		LDA #%00001111		  ;($818E)
		STA APUCommonControl0   ;($8190)Enable sound channels.

		LDA #$FF				;($8193)Initialize tempo.
		STA Tempo			   ;($8195)

		LDA #$08				;($8197)
		STA SQ1Cntrl1		   ;($8199)Disable SQ1 and SQ2 sweep units.
		STA SQ2Cntrl1		   ;($819C)
		RTS					 ;($819F)

;----------------------------------------------------------------------------------------------------

InitMusicSFX:
LDX #$FF				;Indicate the sound engine is active.
		STX SoundEngineStatus   ;($81A2)
		TAX					 ;($81A5)
		BMI DoSFX			   ;($81A6)If MSB set, branch to process SFX.

		ASL					 ;($81A8)Index into table is 4*n + 4. Points to last word in table entry.
		STA MusicTemp		   ;($81A9)
ASL					 ;There are 3 words for each music entry in the table.
		ADC MusicTemp		   ;($81AC)The entries are for SQ1, SQ2 and TRI from left to right.
		ADC #$04				;($81AE)
		TAY					 ;($81B0)Use Y as index into table.

		LDX #$04				;($81B1)Prepare to loop 3 times.

ChannelInitializeLoop:
		LDA MusicStartIndexTable+1,Y;($81B3)Get upper byte of pointer from table.
		BNE +				   ;($81B6)Is there a valid pointer? If so branch to save pointer.

		LDA MusicStartIndexTable+1,X;($81B8)
STA SQ1IndexUB,X		;No music data for this chnnel in the table.  Load
		LDA MusicStartIndexTable,X;($81BD)the "no sound" data instead.
		JMP ++				  ;($81C0)

		* STA SQ1IndexUB,X	  ;($81C3)
		LDA MusicStartIndexTable,Y;($81C5)Store pointer to audio data.
* STA SQ1IndexLB,X		;

		LDA #$01				;($81CA)Indicate the channel has valid sound data.
		STA ChannelLength,X	 ;($81CC)

		DEY					 ;($81CE)Move to the next pointer in the pointer table and in the RAM.
		DEY					 ;($81CF)
		DEX					 ;($81D0)
		DEX					 ;($81D1)Have three pointers been picked up?
BPL ChannelInitializeLoop		;If not, branch to get the next pointer.

		LDA #$00				;($81D4)
STA NoteOffset		  ;
		STA SQ1Quiet			;($81D8)
		STA SQ2Quiet			;($81DA)Clear various status variables.
STA TRIQuiet			;
		STA SoundEngineStatus   ;($81DE)
		RTS					 ;($81E1)

;----------------------------------------------------------------------------------------------------

DoSFX:
		ASL					 ;($81E2)*2. Pointers in table are 2 bytes.
		TAX					 ;($81E3)

		LDA #$01				;($81E4)Indicate a SFX is active.
STA SFXActive		   ;

		LDA SFXStartIndexTable,X;($81E8)
		STA NoisIndexLB		 ;($81EB)Get pointer to SFX data from table.
		LDA SFXStartIndexTable+1,X;($81ED)
STA NoisIndexUB		 ;

		LDA #$08				;($81F2)Disable SQ2 sweep unit.
		STA SQ2Cntrl1		   ;($81F4)

		LDA #$30				;($81F7)Disable length counter and set constant
		STA SQ2Cntrl0		   ;($81F9)volume for SQ2 and noise channels.
		STA NoiseControl0	   ;($81FC)

		LDA #$00				;($81FF)
		STA SoundEngineStatus   ;($8201)Indicate sound engine finished.
RTS					 ;

;----------------------------------------------------------------------------------------------------

;The LSB of the length counter is always written when loading the frequency data into the
;counter registers.  This plays the note for the longest possible time if the halt flag is
;cleared.  The first byte contains the low bits of the timer while the second byte contains
;the upper 3 bits.  The formula for figuring out the frequency is as follows:
;1790000/16/(hhhllllllll + 1).

		.byte $AD, $0E		  ;($8205)65.4Hz  (C2),  Entry #$80.
		.byte $4D, $0E		  ;($8207)69.3Hz  (C#2), Entry #$81.
		.byte $F3, $0D		  ;($8209)73.4Hz  (D2),  Entry #$82.
		.byte $9D, $0D		  ;($820B)77.8Hz  (D#2), Entry #$83.
		.byte $4C, $0D		  ;($820D)82.4Hz  (E2),  Entry #$84.
		.byte $00, $0D		  ;($820F)87.3Hz  (F2),  Entry #$85.
		.byte $B8, $0C		  ;($8211)92.5Hz  (F#2), Entry #$86.
		.byte $74, $0C		  ;($8213)98.0Hz  (G2),  Entry #$87.
		.byte $34, $0C		  ;($8215)103.9Hz (Ab2), Entry #$88.
		.byte $F8, $0B		  ;($8217)110.0Hz (A2),  Entry #$89.
		.byte $BF, $0B		  ;($8219)116.5Hz (A#2), Entry #$8A.
		.byte $89, $0B		  ;($821B)123.5Hz (B2),  Entry #$8B.
		.byte $56, $0B		  ;($821D)130.8Hz (C3),  Entry #$8C.
		.byte $26, $0B		  ;($821F)138.6Hz (C#3), Entry #$8D.
		.byte $F9, $0A		  ;($8221)146.8Hz (D3),  Entry #$8E.
.byte $CE, $0A		  ;155.6Hz (D#3), Entry #$8F.
		.byte $A6, $0A		  ;($8225)164.8Hz (E3),  Entry #$90.
		.byte $80, $0A		  ;($8227)174.5Hz (F3),  Entry #$91.
		.byte $5C, $0A		  ;($8229)184.9Hz (F#3), Entry #$92.
		.byte $3A, $0A		  ;($822B)196.0Hz (G3),  Entry #$93.
		.byte $1A, $0A		  ;($822D)207.6Hz (Ab3), Entry #$94.
		.byte $FB, $09		  ;($822F)220.2Hz (A3),  Entry #$95.
		.byte $DF, $09		  ;($8231)233.1Hz (A#3), Entry #$96.
.byte $C4, $09		  ;247.0Hz (B3),  Entry #$97.
		.byte $AB, $09		  ;($8235)261.4Hz (C4),  Entry #$98.
		.byte $93, $09		  ;($8237)276.9Hz (C#4), Entry #$99.
		.byte $7C, $09		  ;($8239)293.6Hz (D4),  Entry #$9A.
		.byte $67, $09		  ;($823B)310.8Hz (D#4), Entry #$9B.
		.byte $52, $09		  ;($823D)330.0Hz (E4),  Entry #$9C.
		.byte $3F, $09		  ;($823F)349.6Hz (F4),  Entry #$9D.
		.byte $2D, $09		  ;($8241)370.4Hz (F#4), Entry #$9E.
		.byte $1C, $09		  ;($8243)392.5Hz (G4),  Entry #$9F.
		.byte $0C, $09		  ;($8245)414.4Hz (Ab4), Entry #$A0.
		.byte $FD, $08		  ;($8247)440.4Hz (A4),  Entry #$A1.
		.byte $EF, $08		  ;($8249)466.1Hz (A#4), Entry #$A2.
		.byte $E1, $08		  ;($824B)495.0Hz (B4),  Entry #$A3.
		.byte $D5, $08		  ;($824D)522.8Hz (C5),  Entry #$A4.
.byte $C9, $08		  ;553.8Hz (C#5), Entry #$A5.
		.byte $BD, $08		  ;($8251)588.8Hz (D5),  Entry #$A6.
		.byte $B3, $08		  ;($8253)621.5Hz (D#5), Entry #$A7.
.byte $A9, $08		  ;658.1Hz (E5),  Entry #$A8.
		.byte $9F, $08		  ;($8257)699.2Hz (F5),  Entry #$A9.
		.byte $96, $08		  ;($8259)740.9Hz (F#5), Entry #$AA.
		.byte $8E, $08		  ;($825B)782.3Hz (G5),  Entry #$AB.
		.byte $86, $08		  ;($825D)828.7Hz (Ab5), Entry #$AC.
		.byte $7E, $08		  ;($825F)880.9HZ (A5),  Entry #$AD.
		.byte $77, $08		  ;($8261)932.3Hz (A#5), Entry #$AE.
		.byte $70, $08		  ;($8263)990.0Hz (B5),  Entry #$AF.
.byte $6A, $08		  ;1046Hz  (C6),  Entry #$B0.
		.byte $64, $08		  ;($8267)1108Hz  (C#6), Entry #$B1.
		.byte $5E, $08		  ;($8269)1178Hz  (D6),  Entry #$B2.
		.byte $59, $08		  ;($826B)1243Hz  (D#6), Entry #$B3.
.byte $54, $08		  ;1316Hz  (E6),  Entry #$B4.
		.byte $4F, $08		  ;($826F)1398Hz  (F6),  Entry #$B5.
		.byte $4B, $08		  ;($8271)1472Hz  (F#6), Entry #$B6.
		.byte $46, $08		  ;($8273)1576Hz  (G6),  Entry #$B7.
		.byte $42, $08		  ;($8275)1670Hz  (Ab6), Entry #$B8.
		.byte $3F, $08		  ;($8277)1748Hz  (A6),  Entry #$B9.
		.byte $3B, $08		  ;($8279)1865Hz  (A#6), Entry #$BA.
		.byte $38, $08		  ;($827B)1963Hz  (B6),  Entry #$BB.
		.byte $34, $08		  ;($827D)2111Hz  (C7),  Entry #$BC.
		.byte $31, $08		  ;($827F)2238Hz  (C#7), Entry #$BD.
		.byte $2F, $08		  ;($8281)2331Hz  (D7),  Entry #$BE.
		.byte $2C, $08		  ;($8283)2486Hz  (D#7), Entry #$BF.
		.byte $29, $08		  ;($8285)2664Hz  (E7),  Entry #$C0.
		.byte $27, $08		  ;($8287)2796Hz  (F7),  Entry #$C1.
		.byte $25, $08		  ;($8289)2944Hz  (F#7), Entry #$C2.
.byte $23, $08		  ;3107Hz  (G7),  Entry #$C3.
		.byte $21, $08		  ;($828D)3290Hz  (G#7), Entry #$C4.
		.byte $1F, $08		  ;($828F)3496Hz  (A7),  Entry #$C5.
		.byte $1D, $08		  ;($8291)3729Hz  (A#7), Entry #$C6.
		.byte $1B, $08		  ;($8293)3996Hz  (B7),  Entry #$C7.
		.byte $1A, $08		  ;($8295)4144Hz  (C8),  Entry #$C8.

;----------------------------------------------------------------------------------------------------

MusicStartIndexTable:
		.word SQNoSnd,	 SQNoSnd,	 TRINoSnd;($8297)($84CB, $84CB, $84CE)No sound.
		.word SQ1Intro,	SQ2Intro,	TriIntro;($829D)($8D6D, $8E3D, $8F06)Intro.
		.word SQ1ThrnRm,   NULL,		TRIThrnRm;($82A3)($84D3, $0000, $853E)Throne room.
.word SQ1Tantagel, NULL,		TRITantagel ;($85AA, $0000, $85B4)Tantagel castle.
		.word SQ1Village,  NULL,		TRIVillage;($82AF)($872F, $0000, $87A2)Village/pre-game.
		.word SQ1Outdoor,  NULL,		TRIOutdoor;($82B5)($8844, $0000, $8817)Outdoors.
		.word SQ1Dngn,	 NULL,		TRIDngn1;($82BB)($888B, $0000, $891D)Dungeon 1.
		.word SQ1Dngn,	 NULL,		TRIDngn2;($82C1)($888B, $0000, $8924)Dungeon 2.
.word SQ1Dngn,	 NULL,		TRIDngn3	;($888B, $0000, $892B)Dungeon 3.
		.word SQ1Dngn,	 NULL,		TRIDngn4;($82CD)($888B, $0000, $8932)Dungeon 4.
		.word SQ1Dngn,	 NULL,		TRIDngn5;($82D3)($888B, $0000, $8937)Dungeon 5.
		.word SQ1Dngn,	 NULL,		TRIDngn6;($82D9)($888B, $0000, $893E)Dungeon 6.
		.word SQ1Dngn,	 NULL,		TRIDngn7;($82DF)($888B, $0000, $8945)Dungeon 7.
.word SQ1Dngn,	 NULL,		TRIDngn8	;($888B, $0000, $894C)Dungeon 8.
		.word SQ1EntFight, NULL,		TRIEntFight;($82EB)($89A9, $0000, $8ACF)Enter fight.
		.word SQ1EndBoss,  SQ2EndBoss,  TRIEndBoss;($82F1)($8B62, $8BE6, $8C1A)End boss.
.word SQ1EndGame,  SQ2EndGame,  TRIEndGame  ;($8F62, $90B2, $922E)End game.
		.word SQ1SlvrHrp,  SQ2SlvrHrp,  NULL;($82FD)($8C3F, $8C3E, $0000)Silver harp.
.word NULL,		NULL,		TRIFryFlute ;($0000, $0000, $8C9A)Fairy flute.
		.word SQ1RnbwBrdg, SQ2RnbwBrdg, NULL;($8309)($8CE2, $8CE1, $0000)Rainbow bridge.
		.word SQ1Death,	SQ2Death,	NULL;($830F)($8D24, $8D23, $0000)Player death.
		.word SQ1Inn,	  SQ2Inn,	  NULL;($8315)($86CC, $86EB, $0000)Inn.
		.word SQ1Princess, SQ2Princess, TRIPrincess;($831B)($8653, $867B, $86AC)Princess Gwaelin.
.word SQ1Cursed,   SQ2Cursed,   NULL		;($8D4B, $8D4A, $0000)Cursed.
		.word SQ1Fight,	NULL,		TRIFight;($8327)($89BF, $0000, $8AE1)Regular fight.
		.word SQ1Victory,  SQ2Victory,  NULL;($832D)($870E, $8707, $0000)Victory.
		.word SQ1LevelUp,  SQ2LevelUp,  NULL;($8333)($862A, $8640, $0000)Level up.

;----------------------------------------------------------------------------------------------------

SFXStartIndexTable:
		.word FFDamageSFX	   ;($8339)($836E)Force field damage.
		.word WyvernWngSFX	  ;($833B)($8377)Wyvern wing.
		.word StairsSFX		 ;($833D)($839E)Stairs.
.word RunSFX								;($83C2)Run away.
		.word SwmpDmgSFX		;($8341)($83F8)Swamp damage.
		.word MenuSFX		   ;($8343)($8401)Menu button.
		.word ConfirmSFX		;($8345)($8406)Confirmation.
		.word EnHitSFX		  ;($8347)($8411)Enemy hit.
		.word ExclntMvSFX	   ;($8349)($8420)Excellent move.
		.word AttackSFX		 ;($834B)($843B)Attack.
		.word HitSFX			;($834D)($844A)Player hit 1.
		.word HitSFX			;($834F)($844A)Player hit 2.
		.word AttackPrepareSFX  ;($8351)($8459)Attack prep.
		.word Missed1SFX		;($8353)($8468)Missed 1.
		.word Missed2SFX		;($8355)($8471)Missed 2.
		.word WallSFX		   ;($8357)($847A)Wall bump.
		.word TextSFX		   ;($8359)($8486)Text.
		.word SpellSFX		  ;($835B)($848E)Spell cast.
.word RadiantSFX							;($84A0)Radiant.
		.word OpnChestSFX	   ;($835F)($84AB)Open chest.
		.word OpnDoorSFX		;($8361)($84B6)Open door.
		.word FireSFX		   ;($8363)($8365)Breath fire.

;----------------------------------------------------------------------------------------------------

FireSFX:
		.byte MCTL_CNTRL0,	 $B3;($8365)50% duty, len counter no, env no, vol=3.
		.byte MCTL_NOISE_VOL,  $3F;($8367)len counter no, env no, vol=15.
		.byte $ED, $0C		  ;($8369)Noise timer period = 1016, 12 counts.
		.byte $EE, $30		  ;($836B)Noise timer period = 2034, 48 counts.
		.byte $00			   ;($836D)End SFX.

;----------------------------------------------------------------------------------------------------

FFDamageSFX:
		.byte MCTL_NOISE_VOL,  $0F;($836E)len counter yes, env yes, vol=15.
		.byte $E7, $04		  ;($8370)Noise timer period = 160, 4 counts.
		.byte $E8, $04		  ;($8372)Noise timer period = 202, 4 counts.
		.byte $E9, $04		  ;($8374)Noise timer period = 254, 4 counts.
		.byte $00			   ;($8376)End SFX.

;----------------------------------------------------------------------------------------------------

WyvernWngSFX:
		.byte MCTL_NOISE_VOL,  $01;($8377)len counter yes, env yes, vol=1.
		.byte MCTL_CNTRL0,	 $7F;($8379)25% duty, len counter no, env no, vol=15.
.byte MCTL_CNTRL1,	 $9B  ;Setup sweep generator.
		.byte $8C			   ;($837D)C3.
		.byte $EF, $06		  ;($837E)Noise timer period = 4068, 6 counts.
		.byte $EE, $06		  ;($8380)Noise timer period = 2034, 6 counts.
		.byte $0C			   ;($8382)12 counts.
		.byte MCTL_CNTRL1,	 $94;($8383)Setup sweep generator.
		.byte $06			   ;($8385)6 counts.
		.byte MCTL_CNTRL1,	 $9B;($8386)Setup sweep generator.
		.byte MCTL_NOISE_VOL,  $01;($8388)len counter yes, env yes, vol=1.
.byte $8C				   ;C3.
		.byte $EF, $06		  ;($838B)Noise timer period = 4068, 6 counts.
		.byte $EE, $06		  ;($838D)Noise timer period = 2034, 6 counts.
.byte $0C				   ;12 counts.
		.byte MCTL_CNTRL1,	 $94;($8390)Setup sweep generator.
		.byte $06			   ;($8392)6 counts.
		.byte MCTL_CNTRL1,	 $9B;($8393)Setup sweep generator.
		.byte MCTL_NOISE_VOL,  $01;($8395)len counter yes, env yes, vol=1.
		.byte $8C			   ;($8397)C3.
		.byte $EF, $06		  ;($8398)Noise timer period = 4068, 6 counts.
		.byte $EE, $06		  ;($839A)Noise timer period = 2034, 6 counts.
		.byte $0C			   ;($839C)12 counts.
		.byte $00			   ;($839D)End SFX.

;----------------------------------------------------------------------------------------------------

StairsSFX:
		.byte MCTL_NOISE_VOL,  $3F;($839E)len counter no, env no, vol=15.
		.byte $EE, $02		  ;($83A0)Noise timer period = 2034, 2 counts.
		.byte $ED, $02		  ;($83A1)Noise timer period = 1016, 2 counts.
		.byte MCTL_NOISE_VOL,  $30;($83A4)len counter no, env no, vol=0.
		.byte $0C			   ;($83A6)12 counts.
.byte MCTL_NOISE_VOL,  $3F  ;len counter no, env no, vol=15.
		.byte $ED, $02		  ;($83A9)Noise timer period = 1016, 2 counts.
		.byte $EC, $02		  ;($83AB)Noise timer period = 762,  2 counts.
		.byte MCTL_NOISE_VOL,  $30;($83AD)len counter no, env no, vol=0.
		.byte $0C			   ;($83AF)12 counts.
		.byte MCTL_NOISE_VOL,  $3F;($83B0)len counter no, env no, vol=15.
		.byte $EE, $02		  ;($83B2)Noise timer period = 2034, 2 counts.
		.byte $ED, $02		  ;($83B4)Noise timer period = 1016, 2 counts.
		.byte MCTL_NOISE_VOL,  $30;($83B6)len counter no, env no, vol=0.
		.byte $0C			   ;($83B8)12 counts.
		.byte MCTL_NOISE_VOL,  $3F;($83B9)len counter no, env no, vol=15.
		.byte $ED, $02		  ;($83BB)Noise timer period = 1016, 2 counts.
		.byte $EC, $02		  ;($83BD)Noise timer period = 762,  2 counts.
		.byte MCTL_NOISE_VOL,  $30;($83BF)len counter no, env no, vol=0.
		.byte $00			   ;($83C1)End SFX.

;----------------------------------------------------------------------------------------------------

RunSFX:
		.byte MCTL_NOISE_VOL,  $3F;($83C2)len counter no, env no, vol=15.
		.byte $EE, $02		  ;($83C4)Noise timer period = 2034, 2 counts.
.byte $ED, $02			  ;Noise timer period = 1016, 2 counts.
		.byte MCTL_NOISE_VOL,  $30;($83C8)len counter no, env no, vol=0.
		.byte $03			   ;($83CA)3 counts.
		.byte MCTL_NOISE_VOL,  $3F;($83CB)len counter no, env no, vol=15.
		.byte $ED, $02		  ;($83CD)Noise timer period = 1016, 2 counts.
		.byte $EC, $02		  ;($83CF)Noise timer period = 762,  2 counts.
		.byte MCTL_NOISE_VOL,  $30;($83D1)len counter no, env no, vol=0.
		.byte $03			   ;($83D3)3 counts.
		.byte MCTL_NOISE_VOL,  $3F;($83D4)len counter no, env no, vol=15.
		.byte $EE, $02		  ;($83D6)Noise timer period = 2034, 2 counts.
		.byte $ED, $02		  ;($83D8)Noise timer period = 1016, 2 counts.
		.byte MCTL_NOISE_VOL,  $30;($83DA)len counter no, env no, vol=0.
		.byte $03			   ;($83DC)3 counts.
		.byte MCTL_NOISE_VOL,  $3F;($83DD)len counter no, env no, vol=15.
		.byte $ED, $02		  ;($83DF)Noise timer period = 1016, 2 counts.
		.byte $EC, $02		  ;($83E1)Noise timer period = 762,  2 counts.
		.byte MCTL_NOISE_VOL,  $30;($83E3)len counter no, env no, vol=0.
		.byte $03			   ;($83E5)3 counts.
		.byte MCTL_NOISE_VOL,  $3F;($83E6)len counter no, env no, vol=15.
		.byte $EE, $02		  ;($83E8)Noise timer period = 2034, 2 counts.
		.byte $ED, $02		  ;($83EA)Noise timer period = 1016, 2 counts.
		.byte MCTL_NOISE_VOL,  $30;($83EC)len counter no, env no, vol=0.
		.byte $03			   ;($83EE)3 counts.
		.byte MCTL_NOISE_VOL,  $3F;($83EF)len counter no, env no, vol=15.
		.byte $ED, $02		  ;($83F1)Noise timer period = 1016, 2 counts.
.byte $EC, $02			  ;Noise timer period = 762,  2 counts.
		.byte MCTL_NOISE_VOL,  $30;($83F5)len counter no, env no, vol=0.
.byte $00				   ;End SFX.

;----------------------------------------------------------------------------------------------------

SwmpDmgSFX:
		.byte MCTL_NOISE_VOL,  $01;($83F8)len counter yes, env yes, vol=1.
		.byte $EF, $06		  ;($83FA)Noise timer period = 4068, 6 counts.
.byte $ED, $06			  ;Noise timer period = 1016, 6 counts.
		.byte MCTL_NOISE_VOL,  $30;($83FE)len counter no, env no, vol=0.
		.byte $00			   ;($8400)End SFX.

;----------------------------------------------------------------------------------------------------

MenuSFX:
		.byte MCTL_CNTRL0,	 $89;($8401)50% duty, len counter yes, env yes, vol=9.
		.byte $C5, $06		  ;($8403)A7,  6 counts.
		.byte $00			   ;($8405)End SFX.

;----------------------------------------------------------------------------------------------------

ConfirmSFX:
		.byte MCTL_CNTRL0,	 $89;($8406)50% duty, len counter yes, env yes, vol=9.
		.byte $BC, $04		  ;($8408)C7,  4 counts.
.byte $C2, $04			  ;F#7, 4 counts.
.byte $BC, $04			  ;C7,  4 counts.
		.byte $C2, $04		  ;($840E)F#7, 4 counts.
		.byte $00			   ;($8410)End SFX.

;----------------------------------------------------------------------------------------------------

EnHitSFX:
.byte MCTL_NOISE_VOL,  $0F  ;len counter yes, env yes, vol=15.
		.byte $EA, $02		  ;($8413)Noise timer period = 380,  2 counts.
		.byte $EB, $02		  ;($8415)Noise timer period = 508,  2 counts.
		.byte $EC, $02		  ;($8417)Noise timer period = 762,  2 counts.
		.byte $ED, $02		  ;($8419)Noise timer period = 1016, 2 counts.
.byte $EE, $02			  ;Noise timer period = 2034, 2 counts.
		.byte $EF, $02		  ;($841D)Noise timer period = 4068, 2 counts.
		.byte $00			   ;($841F)End SFX.

;----------------------------------------------------------------------------------------------------

ExclntMvSFX:
.byte MCTL_NOISE_VOL,  $0F  ;len counter yes, env yes, vol=15.
		.byte $E8, $02		  ;($8422)Noise timer period = 202,  2 counts.
		.byte $E9, $02		  ;($8424)Noise timer period = 254,  2 counts.
		.byte $EA, $02		  ;($8426)Noise timer period = 380,  2 counts.
		.byte $EB, $02		  ;($8428)Noise timer period = 508,  2 counts.
.byte $E8, $02			  ;Noise timer period = 202,  2 counts.
		.byte $E9, $02		  ;($842C)Noise timer period = 254,  2 counts.
		.byte $EA, $02		  ;($842E)Noise timer period = 380,  2 counts.
		.byte $EB, $02		  ;($8430)Noise timer period = 508,  2 counts.
		.byte $EA, $02		  ;($8432)Noise timer period = 380,  2 counts.
.byte $E9, $02			  ;Noise timer period = 254,  2 counts.
		.byte $E8, $02		  ;($8436)Noise timer period = 202,  2 counts.
		.byte $E7, $02		  ;($8438)Noise timer period = 160,  2 counts.
		.byte $00			   ;($843A)End SFX.

;----------------------------------------------------------------------------------------------------

AttackSFX:
		.byte MCTL_CNTRL0,	 $43;($843B)25% duty, len counter yes, env yes, vol=3.
		.byte $B7, $02		  ;($843D)G6,  2 counts.
		.byte $B8, $02		  ;($843F)Ab6, 2 counts.
		.byte $B6, $02		  ;($8441)F#6, 2 counts.
.byte $B7, $02			  ;G6,  2 counts.
		.byte $B8, $02		  ;($8445)Ab6, 2 counts.
		.byte $B6, $02		  ;($8447)F#6, 2 counts.
		.byte $00			   ;($8449)End SFX.

;----------------------------------------------------------------------------------------------------

HitSFX:
		.byte MCTL_NOISE_VOL,  $0F;($844A)len counter yes, env yes, vol=15.
		.byte $EF, $02		  ;($844C)Noise timer period = 4068, 2 counts.
		.byte $EE, $02		  ;($844E)Noise timer period = 2034, 2 counts.
.byte $ED, $02			  ;Noise timer period = 1016, 2 counts.
.byte $EC, $02			  ;Noise timer period = 762,  2 counts.
		.byte $EB, $02		  ;($8454)Noise timer period = 508,  2 counts.
		.byte $EA, $02		  ;($8456)Noise timer period = 380,  2 counts.
		.byte $00			   ;($8458)End SFX.

;----------------------------------------------------------------------------------------------------

AttackPrepareSFX:
		.byte MCTL_CNTRL0,	 $43;($8459)25% duty, len counter yes, env yes, vol=3.
		.byte $A6, $02		  ;($845B)D5,  2 counts.
		.byte $A3, $02		  ;($845D)B4,  2 counts.
		.byte $A7, $02		  ;($845F)D#5, 2 counts.
.byte $A6, $02			  ;D5,  2 counts.
		.byte $A3, $02		  ;($8463)B4,  2 counts.
		.byte $A7, $02		  ;($8465)D#5, 2 counts.
		.byte $00			   ;($8467)End SFX.

;----------------------------------------------------------------------------------------------------

Missed1SFX:
		.byte MCTL_CNTRL0,	 $0F;($8468)12.5% duty, len counter yes, env yes, vol=15.
		.byte $AD, $04		  ;($846A)A5,  4 counts.
		.byte $AB, $04		  ;($846C)G5,  4 counts.
		.byte $A7, $04		  ;($846E)D#5, 4 counts.
.byte $00				   ;End SFX.

;----------------------------------------------------------------------------------------------------

Missed2SFX:
.byte MCTL_CNTRL0,	 $0F  ;12.5% duty, len counter yes, env yes, vol=15.
.byte $AF, $04			  ;B5,  4 counts.
		.byte $AD, $04		  ;($8475)A5,  4 counts.
		.byte $A9, $04		  ;($8477)F5,  4 counts.
		.byte $00			   ;($8479)End SFX.

;----------------------------------------------------------------------------------------------------

WallSFX:
		.byte MCTL_CNTRL0,	 $8F;($847A)50% duty, len counter yes, env yes, vol=15.
		.byte MCTL_NOISE_VOL,  $00;($847C)len counter yes, env yes, vol=0.
		.byte $EE			   ;($847E)Noise timer period = 2034.
.byte $8F, $03			  ;D#3, 3 counts.
		.byte $8E, $03		  ;($8481)D3,  3 counts.
.byte $8C, $03			  ;C3,  3 counts.
		.byte $00			   ;($8485)End SFX.

;----------------------------------------------------------------------------------------------------

TextSFX:
		.byte MCTL_NOISE_VOL,  $32;($8486)len counter no, env no, vol=2.
		.byte MCTL_CNTRL0,	 $00;($8488)12.5% duty, len counter yes, env yes, vol=0.
		.byte $AD			   ;($848A)A5.
		.byte $EE, $08		  ;($848B)Noise timer period = 2034, 8 counts.
		.byte $00			   ;($848D)End SFX.

;----------------------------------------------------------------------------------------------------

SpellSFX:
.byte MCTL_CNTRL0,	 $4F  ;25% duty, len counter yes, env yes, vol=15.
		.byte $98, $06		  ;($8490)C4,  6 counts.
		.byte $9A, $06		  ;($8492)D4,  6 counts.
		.byte $99, $06		  ;($8494)C#4, 6 counts.
		.byte $9C, $06		  ;($8496)E4,  6 counts.
		.byte $9B, $06		  ;($8498)D#4, 6 counts.
		.byte $9D, $06		  ;($849A)F4,  6 counts.
		.byte $9E, $06		  ;($849C)F#4, 6 counts.
		.byte $00			   ;($849E)End SFX.
		.byte MCTL_NO_OP		;($849F)Continue previous music.

;----------------------------------------------------------------------------------------------------

RadiantSFX:
		.byte MCTL_NOISE_VOL,  $3F;($84A0)len counter no, env no, vol=15.
		.byte $EF, $03		  ;($84A2)Noise timer period = 4068, 3 counts.
		.byte $EE, $02		  ;($84A4)Noise timer period = 2034, 2 counts.
		.byte $ED, $01		  ;($84A6)Noise timer period = 1016, 1 count.
		.byte $EC, $02		  ;($84A8)Noise timer period = 762,  2 counts.
		.byte $00			   ;($84AA)End SFX.

;----------------------------------------------------------------------------------------------------

OpnChestSFX:
		.byte MCTL_CNTRL0,	 $8F;($84AB)50% duty, len counter yes, env yes, vol=15.
		.byte $92, $03		  ;($84AD)F#3, 3 counts.
		.byte $98, $03		  ;($84AF)C4,  3 counts.
		.byte $93, $03		  ;($84B1)G3,  3 counts.
.byte $99, $03			  ;C#4, 3 counts.
		.byte $00			   ;($84B5)End SFX.

;----------------------------------------------------------------------------------------------------

OpnDoorSFX:
		.byte MCTL_CNTRL0,	 $00;($84B6)12.5% duty, len counter yes, env yes, vol=0.
		.byte $B0, $02		  ;($84B8)C6,  2 counts.
		.byte $A5, $02		  ;($84BA)C#5, 2 counts.
		.byte $B2, $02		  ;($84BC)D6,  2 counts.
		.byte $A7, $02		  ;($84BE)D#5, 2 counts.
		.byte $B4, $06		  ;($84C0)E6,  6 counts.
		.byte $A6, $02		  ;($84C2)D5,  2 counts.
		.byte $B3, $02		  ;($84C4)D#6, 2 counts.
		.byte $A8, $02		  ;($84C6)E5,  2 counts.
		.byte $B5, $06		  ;($84C8)F6,  6 counts.
.byte $00				   ;End SFX.

;----------------------------------------------------------------------------------------------------

SQNoSnd:
		.byte MCTL_CNTRL0,	$30;($84CB)12.5% duty, len counter no, env no, vol=0.
		.byte $00			   ;($84CD)End music.

;----------------------------------------------------------------------------------------------------

TRINoSnd:
		.byte MCTL_NOTE_OFST, $00;($84CE)Note offset of 0 notes.
		.byte MCTL_CNTRL0,	$00;($84D0)Silence the trianlge channel.
		.byte $00			   ;($84D2)End music.

;----------------------------------------------------------------------------------------------------

SQ1ThrnRm:
		.byte MCTL_TEMPO,	 $7E;($84D3)60/1.19=50 counts per second.

SQ1ThrnRmLoop:
		.byte MCTL_CNTRL0,	$8F;($84D5)50% duty, len counter yes, env yes, vol=15.
		.byte MCTL_JUMP		 ;($84D7)Jump to new music address.
		.word SQ1Tantagel2	  ;($84D8)($85BA).
		.byte MCTL_CNTRL0,	$82;($84DA)50% duty, len counter yes, env yes, vol=2.
		.byte MCTL_ADD_SPACE, $06;($84DC)6 counts between notes.
		.byte $95			   ;($84DE)A3.
		.byte MCTL_JUMP		 ;($84DF)Jump to new music address.
		.word SQ1ThrnRm2		;($84E0)($851E).
		.byte $93			   ;($84E2)G3.
		.byte MCTL_JUMP		 ;($84E3)Jump to new music address.
		.word SQ1ThrnRm2		;($84E4)($851E).
		.byte MCTL_CNTRL0,	$87;($84E6)50% duty, len counter yes, env yes, vol=7.
.byte MCTL_ADD_SPACE, $0C   ;12 counts between notes.
		.byte $A3, $9F, $A4, $9F;($84EA)B4,  G4,  C5,  G4.
		.byte $A9, $A1, $A4, $A1;($84EE)F5,  A4,  C5,  A4.
		.byte $A8, $9C, $A0, $A3;($84F2)E5,  E4,  Ab4, B4.
		.byte $A8, $9F, $A5, $A8;($84F6)E5,  G4,  C#5, E5.
		.byte MCTL_CNTRL0,	$82;($84FA)50% duty, len counter yes, env yes, vol=2.
		.byte MCTL_ADD_SPACE, $06;($84FC)6 counts between notes.
		.byte $8E			   ;($84FE)D3.
		.byte MCTL_JUMP		 ;($84FF)Jump to new music address.
		.word SQ1ThrnRm3		;($8500)($852E).
		.byte $8C			   ;($8502)C3.
		.byte MCTL_JUMP		 ;($8503)Jump to new music address.
		.word SQ1ThrnRm3		;($8504)($852E).
.byte MCTL_CNTRL0,	$87   ;50% duty, len counter yes, env yes, vol=7.
.byte MCTL_ADD_SPACE, $0C   ;12 counts between notes.
		.byte $A3, $9F, $A4, $9F;($850A)B4,  G4,  C5,  G4.
		.byte $A9, $A1, $A4, $A9;($850E)F5,  A4,  C5,  F5.
		.byte $A8, $A1, $A0, $9D;($8512)E5,  A4,  Ab4, F4.
		.byte $9C, $9A, $98, $97;($8516)E4,  D4,  C4,  B3.
		.byte MCTL_END_SPACE	;($851A)Disable counts between notes.
		.byte MCTL_JUMP		 ;($851B)Jump to new music address.
		.word SQ1ThrnRmLoop	 ;($851C)($84D5).

SQ1ThrnRm2:
		.byte $06			   ;($851E)6 counts.
		.byte $AD, $AC		  ;($851F)A5, 172 counts.
		.byte $AD, $06		  ;($8521)A5,   6 counts.
		.byte $A8, $A7		  ;($8523)E5, 167 counts.
		.byte $A8, $06		  ;($8525)E5,   6 counts.
		.byte $A4, $A3		  ;($8527)C5, 163 counts.
.byte $A4, $06			  ;C5,   6 counts.
		.byte $A1, $06		  ;($852B)A4,   6 counts.
		.byte MCTL_RETURN	   ;($852D)Return to previous music block.

SQ1ThrnRm3:
		.byte $06			   ;($852E)6 counts.
		.byte $AD, $AC		  ;($852F)A5, 172 counts.
		.byte $AD, $06		  ;($8531)A5,   6 counts.
.byte $A9, $A8			  ;F5, 168 counts.
		.byte $A9, $06		  ;($8535)F5,   6 counts.
		.byte $A6, $A5		  ;($8537)D5, 165 counts.
		.byte $A6, $06		  ;($8539)D5,   6 counts.
		.byte $A1, $06		  ;($853B)A4,   6 counts.
		.byte MCTL_RETURN	   ;($853D)Return to previous music block.

;----------------------------------------------------------------------------------------------------

TRIThrnRm:
		.byte MCTL_JUMP		 ;($853E)Jump to new music address.
		.word TRITantagel2	  ;($853F)($85EB).
		.byte MCTL_CNTRL0,	$18;($8541)12.5% duty, len counter yes, env no, vol=8.
		.byte MCTL_ADD_SPACE, $06;($8543)6 counts between notes.
		.byte $95			   ;($8545)A3.
		.byte $06			   ;($8546)6 counts.
		.byte $A4, $A3, $A4	 ;($8547)C5,  B4,  C5.
		.byte $06			   ;($854A)6 counts.
		.byte $A4, $A3, $A4	 ;($854B)C5,  B4,  C5.
		.byte $06			   ;($854E)6 counts.
		.byte $A8, $A7, $A8	 ;($854F)E5,  D#5, E5.
		.byte $06			   ;($8552)6 counts.
		.byte $A4			   ;($8553)C5.
		.byte $06			   ;($8554)6 counts.
.byte $93				   ;G3.
		.byte $06			   ;($8556)6 counts.
		.byte $A4, $A3, $A4	 ;($8557)C5,  B4,  C5.
		.byte $06			   ;($855A)6 counts.
		.byte $A4, $A3, $9E	 ;($855B)C5,  B4,  F#4.
		.byte $06			   ;($855E)6 counts.
		.byte $A8, $A7, $A8	 ;($855F)E5,  D#5, E5.
		.byte $06			   ;($8562)6 counts.
		.byte $A4			   ;($8563)C5.
		.byte $06			   ;($8564)6 counts.
.byte MCTL_CNTRL0,	$FF   ;75% duty, len counter no, env no, vol=15.
		.byte $9D			   ;($8567)F4.
		.byte $12			   ;($8568)18 counts.
		.byte $9C			   ;($8569)E4.
		.byte $12			   ;($856A)18 counts.
		.byte $9A			   ;($856B)D4.
		.byte $12			   ;($856C)18 counts.
		.byte $9B			   ;($856D)D#4.
		.byte $12			   ;($856E)18 counts.
.byte $9C				   ;E4.
		.byte $2A			   ;($8570)42 counts.
		.byte $A1			   ;($8571)A4.
		.byte $2A			   ;($8572)42 counts.
.byte MCTL_CNTRL0,	$18   ;12.5% duty, len counter yes, env no, vol=8.
		.byte $9A			   ;($8575)D4.
		.byte $06			   ;($8576)6 counts.
		.byte $A9, $A8, $A9	 ;($8577)F5,  E5,  F5.
		.byte $06			   ;($857A)6 counts.
		.byte $A6, $A5, $A6	 ;($857B)D5,  C#5, D5.
.byte $06				   ;6 counts.
		.byte $A9, $A8, $A9	 ;($857F)F5,  E5,  F5.
		.byte $06			   ;($8582)6 counts.
.byte $A6				   ;D5.
		.byte $06			   ;($8584)6 counts.
		.byte $98			   ;($8585)C4.
		.byte $06			   ;($8586)6 counts.
		.byte $A9, $A8, $A9	 ;($8587)F5,  E5,  F5.
		.byte $06			   ;($858A)6 counts.
		.byte $A6, $A5, $97	 ;($858B)D5,  C#5, B3.
		.byte $06			   ;($858E)6 counts.
		.byte $A9, $A8, $A9	 ;($858F)F5,  E5,  F5.
		.byte $06			   ;($8592)6 counts.
		.byte $A6			   ;($8593)D5.
		.byte $06			   ;($8594)6 counts.
		.byte MCTL_CNTRL0,	$FF;($8595)75% duty, len counter no, env no, vol=15.
		.byte $9D			   ;($8597)F4.
		.byte $12			   ;($8598)18 counts.
		.byte $9C			   ;($8599)E4.
		.byte $12			   ;($859A)18 counts.
		.byte $9A			   ;($859B)D4.
.byte $2A				   ;42 counts.
		.byte MCTL_ADD_SPACE, $0C;($859D)12 counts between notes.
		.byte $9C, $A9, $A8, $A6;($859F)E4,  F5,  E5,  D5.
		.byte $A4, $A3, $A1, $A0;($85A3)C5,  B4,  A4,  Ab4.
		.byte MCTL_JUMP		 ;($85A7)Jump to new music address.
		.word TRIThrnRm		 ;($85A8)($853E).

;----------------------------------------------------------------------------------------------------

SQ1Tantagel:
		.byte MCTL_TEMPO,	 $7D;($85AA)60/1.2=50 counts per second.
		.byte MCTL_CNTRL0,	$4F;($85AC)25% duty, len counter yes, env yes, vol=15.
		.byte MCTL_JUMP		 ;($85AE)Jump to new music address.
		.word SQ1Tantagel2	  ;($85AF)($85BA).
		.byte MCTL_JUMP		 ;($85B1)Jump to new music address.
		.word SQ1Tantagel	   ;($85B2)($85AA).

;----------------------------------------------------------------------------------------------------

TRITantagel:
		.byte MCTL_JUMP		 ;($85B4)Jump to new music address.
		.word TRITantagel2	  ;($85B5)($85EB).
		.byte MCTL_JUMP		 ;($85B7)Jump to new music address.
		.word TRITantagel	   ;($85B8)($85B4).

;----------------------------------------------------------------------------------------------------

SQ1Tantagel2:
.byte MCTL_ADD_SPACE, $0C   ;12 counts between notes.
		.byte $95, $A8, $A6, $A8;($85BC)A3,  E5,  D5,  E5.
		.byte $A4, $A8, $A3, $A8;($85C0)C5,  E5,  B4,  E5.
		.byte $A1			   ;($85C4)A4.
		.byte $54			   ;($85C5)84 counts.
		.byte $8E, $A9, $A8, $A9;($85C6)D3,  F5,  E5,  F5.
		.byte $A6, $A9, $A4, $A9;($85CA)D5,  F5,  C5,  F5.
		.byte $A3			   ;($85CE)B4.
		.byte $54			   ;($85CF)84 counts.
		.byte $95, $AB, $A9, $AB;($85D0)A3,  G5,  F5,  G5.
		.byte $A8, $AB, $A5, $AB;($85D4)E5,  G5,  C#5, G5.
.byte $A9				   ;F5.
.byte $0C				   ;12 counts.
		.byte $AB			   ;($85DA)G5.
		.byte $0C			   ;($85DB)12 counts.
		.byte $AD			   ;($85DC)A5.
		.byte $0C			   ;($85DD)12 counts.
		.byte $AB, $A9, $A8	 ;($85DE)G5,  F5,  E5.
		.byte $0C			   ;($85E1)12 counts.
		.byte $A4, $A8, $A6	 ;($85E2)C5,  E5,  D5.
		.byte $0C			   ;($85E5)12 counts.
		.byte $A7			   ;($85E6)D#5.
.byte $0C				   ;12 counts.
		.byte $A8			   ;($85E8)E5.
		.byte $54			   ;($85E9)84 counts.
		.byte MCTL_RETURN	   ;($85EA)Return to previous music block.

;----------------------------------------------------------------------------------------------------

TRITantagel2:
		.byte MCTL_ADD_SPACE, $0C;($85EB)12 counts between notes.
		.byte MCTL_CNTRL0,	$60;($85ED)25% duty, len counter no, env yes, vol=0.
.byte $95				   ;A3.
		.byte $54			   ;($85F0)84 counts.
		.byte $A1, $95, $98, $9C;($85F1)A4  A3  C4  E4.
		.byte $A1, $9F, $9D, $9C;($85F5)A4  G4  F4  E4.
		.byte $9A, $A6, $A4, $A6;($85F9)D4  D5  C5  D5.
		.byte $A3, $A6, $A1, $A6;($85FD)B4  D5  A4  D5.
		.byte $A0, $9C, $A0, $A3;($8601)Ab4 E4  Ab4 B4.
		.byte $A8, $9C, $9E, $A0;($8605)E5  E4  F#4 Ab4.
		.byte $A1, $A8, $A6, $A8;($8609)A4  E5  D5  E5.
.byte $A5, $A8, $A1, $A8	;C#5 E5  A4  E5.
		.byte $A6, $A1, $A8, $A1;($8611)D5  A4  E5  A4.
		.byte $A9, $A1, $A8, $A6;($8615)F5  A4  E5  D5.
		.byte $A4, $9F, $A8, $9F;($8619)C5  G4  E5  G4.
.byte $A3, $A9, $A1, $AA	;B4  F5  A4  F#.
		.byte $AC, $9C, $A0, $A3;($8621)Ab5 E4  Ab4 B4.
		.byte $A8, $A6, $A4, $A3;($8625)E5  D5  C5  B4.
		.byte MCTL_RETURN	   ;($8629)Return to previous music block.

;----------------------------------------------------------------------------------------------------

SQ1LevelUp:
		.byte MCTL_TEMPO,	 $50;($862A)60/1.88=32 counts per second.
		.byte MCTL_CNTRL0,	$42;($862C)25% duty, len counter yes, env yes, vol=2.
		.byte $A9, $04		  ;($862E)F5,   4 counts.
		.byte $A9, $04		  ;($8630)F5,   4 counts.
.byte $A9, $04			  ;F5,   4 counts.
		.byte $A9, $08		  ;($8634)F5,   8 counts.
		.byte $A7, $08		  ;($8636)D#5,  8 counts.
		.byte $AB, $08		  ;($8638)G5,   8 counts.
		.byte MCTL_CNTRL0,	$4F;($863A)25% duty, len counter yes, env yes, vol=15.
		.byte $A9, $18		  ;($863C)F5,  24 counts.
.byte $00				   ;End music.
		.byte MCTL_NO_OP		;($863F)Continue last music.

;----------------------------------------------------------------------------------------------------

SQ2LevelUp:
		.byte MCTL_CNTRL0, $42  ;($8640)25% duty, len counter yes, env yes, vol=2.
		.byte $A4, $04		  ;($8642)C5,   4 counts.
		.byte $A3, $04		  ;($8644)B4,   4 counts.
		.byte $A2, $04		  ;($8646)A#4,  4 counts.
		.byte $A1, $08		  ;($8648)A4,   8 counts.
.byte $9F, $08			  ;G4,   8 counts.
		.byte $A2, $08		  ;($864C)A#4,  8 counts.
		.byte MCTL_CNTRL0, $4F  ;($864E)25% duty, len counter yes, env yes, vol=15.
		.byte $A1, $18		  ;($8650)A4,  24 counts.
		.byte $00			   ;($8652)End music.

;----------------------------------------------------------------------------------------------------

SQ1Princess:
		.byte MCTL_TEMPO,	 $6E;($8653)60/1.36=44 counts per second.
		.byte MCTL_CNTRL0,	$30;($8655)12.5% duty, len counter no, env no, vol=0.
		.byte $06			   ;($8657)6 counts.
		.byte MCTL_CNTRL0,	$8F;($8658)50% duty, len counter yes, env yes, vol=15.
		.byte $B0, $12		  ;($865A)C6,  18 counts.
		.byte $AD, $06		  ;($865C)A5,   6 counts.
.byte $AB, $06			  ;G5,   6 counts.
		.byte $A9, $06		  ;($8660)F5,   6 counts.
.byte $A8, $0C			  ;E5,  12 counts.
		.byte $A6, $18		  ;($8664)D5,  24 counts.
		.byte $AE, $12		  ;($8666)A#5, 18 counts.
		.byte $AB, $06		  ;($8668)G5,   6 counts.
		.byte $A8, $06		  ;($866A)E5,   6 counts.
		.byte $A6, $06		  ;($866C)D5,   6 counts.
.byte $A5, $18			  ;C#5, 24 counts.
		.byte $AD, $0C		  ;($8670)A5,  12 counts.
		.byte MCTL_CNTRL0,	$BF;($8672)50% duty, len counter no, env no, vol=15.
		.byte $B0, $30		  ;($8674)C6,  48 counts.
		.byte MCTL_CNTRL0,	$8F;($8676)50% duty, len counter yes, env yes, vol=15.
		.byte $3C			   ;($8678)60 counts.
		.byte $00			   ;($8679)End music.
.byte MCTL_NO_OP			;Continue last music.

;----------------------------------------------------------------------------------------------------

SQ2Princess:
		.byte MCTL_CNTRL0,	$30;($867B)12.5% duty, len counter no, env no, vol=0.
		.byte $12			   ;($867D)18 counts.
.byte MCTL_CNTRL0,	$8F   ;50% duty, len counter yes, env yes, vol=15.
		.byte $A4, $0C		  ;($8680)C5,  12 counts.
.byte $A1, $0C			  ;A4,  12 counts.
		.byte MCTL_CNTRL0,	$30;($8684)12.5% duty, len counter no, env no, vol=0.
.byte $0C				   ;12 counts.
		.byte MCTL_CNTRL0,	$8F;($8687)50% duty, len counter yes, env yes, vol=15.
		.byte $A0, $0C		  ;($8689)Ab4, 12 counts.
		.byte $9D, $0C		  ;($868B)F4,  12 counts.
		.byte MCTL_CNTRL0,	$30;($868D)12.5% duty, len counter no, env no, vol=0.
		.byte $0C			   ;($868F)12 counts.
		.byte MCTL_CNTRL0,	$8F;($8690)50% duty, len counter yes, env yes, vol=15.
.byte $A6, $0C			  ;D5,  12 counts.
		.byte $A2, $0C		  ;($8694)A#4, 12 counts.
		.byte MCTL_CNTRL0,	$30;($8696)12.5% duty, len counter no, env no, vol=0.
		.byte $0C			   ;($8698)12 counts.
		.byte MCTL_CNTRL0,	$8F;($8699)50% duty, len counter yes, env yes, vol=15.
		.byte MCTL_ADD_SPACE, $06;($869B)6 counts between notes.
		.byte $9C, $9F, $A2, $9C;($869D)E4,  G4,  A#4, E4.
		.byte $A1, $A4, $A8, $A4;($86A1)A4,  C5,  E5,  C5.
		.byte $A1, $A4, $A1	 ;($86A5)A4,  C5,  A4.
		.byte $06			   ;($86A8)6 counts.
		.byte MCTL_CNTRL0,	$8F;($86A9)50% duty, len counter yes, env yes, vol=15.
		.byte $00			   ;($86AB)End music.

;----------------------------------------------------------------------------------------------------

TRIPrincess:
		.byte MCTL_CNTRL0,	$00;($86AC)12.5% duty, len counter yes, env yes, vol=0.
		.byte $06			   ;($86AE)6 counts.
		.byte MCTL_CNTRL0,	$FF;($86AF)75% duty, len counter no, env no, vol=15.
		.byte MCTL_ADD_SPACE, $0C;($86B1)12 counts between notes.
		.byte $9D, $A1, $A4, $A0;($86B3)F4,  A4,  C5,  Ab4.
.byte $A3, $A0, $9F, $A2	;B4,  Ab4, G4,  A#4.
		.byte $9F, $98, $A4, $98;($86BB)G4,  C4,  C5,  C4.
		.byte MCTL_ADD_SPACE, $06;($86BF)6 counts between notes.
		.byte $9D, $A1, $A4, $A1;($86C1)F4,  A4,  C5,  A4.
		.byte $9D, $98, $91	 ;($86C5)F4,  C4,  F3.
		.byte $12			   ;($86C8)18 counts.
		.byte MCTL_CNTRL0,	$00;($86C9)12.5% duty, len counter yes, env yes, vol=0.
		.byte $00			   ;($86CB)End music.

;----------------------------------------------------------------------------------------------------

SQ1Inn:
		.byte MCTL_TEMPO,	 $78;($86CC)60/1.25=48 counts per second.
.byte MCTL_CNTRL0,	$30   ;12.5% duty, len counter no, env no, vol=0.
		.byte $18			   ;($86D0)24 counts.
		.byte MCTL_CNTRL0,	$82;($86D1)50% duty, len counter yes, env yes, vol=2.
		.byte $A4, $06		  ;($86D3)C5,   6 counts.
		.byte $A6, $06		  ;($86D5)D5,   6 counts.
		.byte $A4, $06		  ;($86D7)C5,   6 counts.
		.byte $A6, $06		  ;($86D9)D5,   6 counts.
		.byte $A8, $0C		  ;($86DB)E5,  12 counts.
		.byte $AB, $0C		  ;($86DD)G5,  12 counts.
.byte $A4, $02			  ;C5,   2 counts.
		.byte $A8, $02		  ;($86E1)E5,   2 counts.
		.byte $AB, $02		  ;($86E3)G5,   2 counts.
		.byte MCTL_CNTRL0,	$8F;($86E5)50% duty, len counter yes, env yes, vol=15.
		.byte $B0, $42		  ;($86E7)C6,  66 counts.
		.byte $00			   ;($86E9)End music.
		.byte MCTL_NO_OP		;($86EA)Continue last music.

;----------------------------------------------------------------------------------------------------

SQ2Inn:
		.byte MCTL_CNTRL0,	$30;($86EB)12.5% duty, len counter no, env no, vol=0.
		.byte $18			   ;($86ED)24 counts.
.byte MCTL_CNTRL0,	$82   ;50% duty, len counter yes, env yes, vol=2.
		.byte $9C, $06		  ;($86F0)E4m   6 counts.
.byte $9D, $06			  ;F4m   6 counts.
		.byte $9C, $06		  ;($86F4)E4m   6 counts.
		.byte $9D, $06		  ;($86F6)F4,   6 counts.
		.byte $9F, $0C		  ;($86F8)G4m  12 counts.
		.byte $A2, $0C		  ;($86FA)A#4m 12 counts.
		.byte $9C, $02		  ;($86FC)E4m   2 counts.
.byte $9F, $02			  ;G4,   2 counts.
		.byte $A2, $02		  ;($8700)A#4,  2 counts.
		.byte MCTL_CNTRL0,	$8F;($8702)50% duty, len counter yes, env yes, vol=15.
		.byte $A8, $42		  ;($8704)E5,  66 counts.
		.byte $00			   ;($8706)End music.

;----------------------------------------------------------------------------------------------------

SQ2Victory:
		.byte $06			   ;($8707)6 counts.
		.byte MCTL_JUMP		 ;($8708)Jump to new music address.
		.word SQVictory		 ;($8709)($8717).
		.byte MCTL_CNTRL0,	$30;($870B)12.5% duty, len counter no, env no, vol=0.
		.byte $00			   ;($870D)End music.

;----------------------------------------------------------------------------------------------------

SQ1Victory:
.byte MCTL_TEMPO,	 $78   ;60/1.25=48 counts per second.
		.byte MCTL_JUMP		 ;($8710)Jump to new music address.
		.word SQVictory		 ;($8711)($8717).
.byte $B0, $2F			  ;C6,  47 counts.
		.byte $00			   ;($8715)End music.
.byte MCTL_NO_OP			;Continue last music.

SQVictory:
		.byte MCTL_CNTRL0,	$8F;($8717)50% duty, len counter yes, env yes, vol=15.
		.byte $8C, $07		  ;($8719)C3,   7 counts.
		.byte $93, $06		  ;($871B)G3,   6 counts.
		.byte $98, $06		  ;($871D)C4,   6 counts.
		.byte MCTL_ADD_SPACE, $01;($871F)1 counts between notes.
		.byte $9A, $9C, $9D, $9F;($8721)D4,  E4,  F4,  G4.
.byte $A1, $A2, $A4, $A6	;A4,  A#4, C5,  D5.
		.byte $A8, $A9, $AB, $AD;($8729)E5,  F5,  G5,  A5.
.byte $AE				   ;A#5
		.byte MCTL_RETURN	   ;($872E)Return to previous music block.

;----------------------------------------------------------------------------------------------------

SQ1Village:
		.byte MCTL_TEMPO,	 $73;($872F)60/1.3=46 counts per second.

SQ1VillageLoop:
		.byte MCTL_ADD_SPACE, $0C;($8731)12 counts between notes.
		.byte MCTL_CNTRL0,	$8F;($8733)50% duty, len counter yes, env yes, vol=15.
		.byte $A1, $A2, $A4, $A9;($8735)A4,  A#4, C5,  F5.
		.byte $A8, $A6, $A4	 ;($8739)E5,  D5,  C5.
		.byte $0C			   ;($873C)12 counts.
.byte $A6, $A1, $A2		 ;D5,  A4,  A#4.
		.byte $3C			   ;($8740)60 counts.
		.byte $9F, $A1, $A2, $A8;($8741)G4,  A4,  A#4, E5.
		.byte $A6, $A4, $A4, $A2;($8745)D5,  C5,  C5,  A#4.
.byte $9F, $A2, $A1		 ;G4,  A#4, A4.
		.byte $0C			   ;($874C)12 counts.
		.byte $A2			   ;($874D)A#4.
		.byte $0C			   ;($874E)12 counts.
		.byte MCTL_JUMP		 ;($874F)Jump to new music address.
		.word SQ1Village2	   ;($8750)($8772).
.byte $0C				   ;12 counts.
		.byte $9D, $A1, $9F	 ;($8753)F4,  A4,  G4.
		.byte $0C			   ;($8756)12 counts.
		.byte $A9			   ;($8757)F5.
		.byte $0C			   ;($8758)12 counts.
.byte $A8, $A9, $A6, $A8	;E5,  F5,  D5,  E5.
		.byte MCTL_JUMP		 ;($875D)Jump to new music address.
		.word SQ1Village2	   ;($875E)($8772).
		.byte $A2, $A3, $A6, $A4;($8760)A#4, B4,  D5,  C5.
		.byte $A2, $A1, $9F	 ;($8764)A#4, A4,  G4.
		.byte MCTL_CNTRL0,	$85;($8767)50% duty, len counter yes, env yes, vol=5.
		.byte $A1			   ;($8769)A4.
		.byte $0C			   ;($876A)12 counts.
		.byte $9F			   ;($876B)G4.
.byte $0C				   ;12 counts.
		.byte $9D			   ;($876D)F4.
		.byte $0C			   ;($876E)12 counts.
		.byte MCTL_JUMP		 ;($876F)Jump to new music address.
.word SQ1VillageLoop		;($8731).

SQ1Village2:
		.byte $A4			   ;($8772)C5.
		.byte $0C			   ;($8773)12 counts.
.byte $A6, $A8			  ;D5,  E5.
		.byte MCTL_CNTRL0,	$82;($8776)50% duty, len counter yes, env yes, vol=2.
		.byte $A9			   ;($8778)F5.
		.byte MCTL_END_SPACE	;($8779)Disable counts between notes.
		.byte MCTL_CNTRL0,	$82;($877A)50% duty, len counter yes, env yes, vol=2.
		.byte $A2, $06		  ;($877C)A#4,  6 counts.
		.byte $A2, $06		  ;($877E)A#4,  6 counts.
		.byte $A2, $0C		  ;($8780)A#4, 12 counts.
		.byte $A6, $0C		  ;($8782)D5,  12 counts.
.byte MCTL_CNTRL0,	$8F   ;50% duty, len counter yes, env yes, vol=15.
		.byte $A9, $18		  ;($8786)F5,  24 counts.
		.byte $A8, $0C		  ;($8788)E5,  12 counts.
		.byte $A6, $0C		  ;($878A)D5,  12 counts.
		.byte MCTL_CNTRL0,	$82;($878C)50% duty, len counter yes, env yes, vol=2.
.byte $A4, $0C			  ;C5,  12 counts.
		.byte MCTL_CNTRL0,	$82;($8790)50% duty, len counter yes, env yes, vol=2.
		.byte $A1, $06		  ;($8792)A4,   6 counts.
		.byte $A1, $06		  ;($8794)A4,   6 counts.
		.byte MCTL_ADD_SPACE, $0C;($8796)12 counts between notes.
		.byte $A1, $A4		  ;($8798)A4,  C5.
		.byte MCTL_CNTRL0,	$8F;($879A)50% duty, len counter yes, env yes, vol=15.
		.byte $A9			   ;($879C)F5.
.byte $0C				   ;12 counts.
		.byte $A4, $A2, $A1	 ;($879E)C5,  A#4, A4.
		.byte MCTL_RETURN	   ;($87A1)Return to previous music block.

;----------------------------------------------------------------------------------------------------

TRIVillage:
		.byte MCTL_CNTRL0,	$00;($87A2)12.5% duty, len counter yes, env yes, vol=0.
		.byte $18			   ;($87A4)24 counts.
		.byte MCTL_CNTRL0,	$FF;($87A5)75% duty, len counter no, env no, vol=15.
		.byte MCTL_ADD_SPACE, $0C;($87A7)12 counts between notes.
		.byte $9D, $A1, $A4, $A9;($87A9)F4,  A4,  C5,  F5.
		.byte $9E, $A1, $A4, $A6;($87AD)F#4, A4,  C5,  D5.
		.byte $9F, $A2, $A6, $AB;($87B1)G4,  A#4, D5,  G5.
		.byte $9E, $A6, $9D, $A6;($87B5)F#4, D5,  F4,  D5.
		.byte $9C, $A4, $A2, $A4;($87B9)E4,  C5,  A#4, C5.
		.byte $98, $9F, $9C, $9F;($87BD)C4,  G4,  E4,  G4.
		.byte $9D, $A4, $9F, $A4;($87C1)F4,  C5,  G4,  C5.
		.byte $A1, $A7		  ;($87C5)A4,  D#5.
		.byte MCTL_JUMP		 ;($87C7)Jump to new music address.
.word TRIVillage2		   ;($87EE).
.byte $A3				   ;B4.
		.byte $0C			   ;($87CB)12 counts.
		.byte $A6			   ;($87CC)D5.
		.byte $0C			   ;($87CD)12 counts.
		.byte $A3			   ;($87CE)B4.
		.byte $0C			   ;($87CF)12 counts.
		.byte $A4, $A6, $A4	 ;($87D0)C5,  D5,  C5.
		.byte $0C			   ;($87D3)12 counts.
		.byte $A6			   ;($87D4)D5.
		.byte $0C			   ;($87D5)12 counts.
		.byte $A8			   ;($87D6)E5.
		.byte $0C			   ;($87D7)12 counts.
.byte MCTL_JUMP			 ;Jump to new music address.
.word TRIVillage2		   ;($87EE).
		.byte $9D, $9F, $A0, $A3;($87DB)F4,  G4,  Ab4, B4.
		.byte $A4, $A5, $A6, $A8;($87DF)C5,  C#5, D5,  E5.
.byte MCTL_CNTRL0,	$18   ;12.5% duty, len counter yes, env no, vol=8.
		.byte $A9			   ;($87E5)F5.
		.byte $0C			   ;($87E6)12 counts.
		.byte $A4			   ;($87E7)C5.
.byte $0C				   ;12 counts.
		.byte $A1			   ;($87E9)A4.
		.byte $0C			   ;($87EA)12 counts.
		.byte MCTL_JUMP		 ;($87EB)Jump to new music address.
		.word TRIVillage		;($87EC)($87A2).

TRIVillage2:
		.byte $AE, $B0		  ;($87EE)A#5, C6.
		.byte MCTL_CNTRL0,	$18;($87F0)12.5% duty, len counter yes, env no, vol=8.
		.byte $B2			   ;($87F2)D6.
.byte MCTL_END_SPACE		;Disable counts between notes.
		.byte $9D, $06		  ;($87F4)F4,   6 counts.
		.byte $9D, $06		  ;($87F6)F4,   6 counts.
		.byte $9D, $0C		  ;($87F8)F4,  12 counts.
		.byte $A2, $0C		  ;($87FA)A#4, 12 counts.
		.byte MCTL_CNTRL0,	$FF;($87FC)75% duty, len counter no, env no, vol=15.
		.byte $A6, $18		  ;($87FE)D5,  24 counts.
		.byte $B0, $0C		  ;($8800)C6,  12 counts.
		.byte $AE, $0C		  ;($8802)A#5, 12 counts.
		.byte MCTL_CNTRL0,	$18;($8804)12.5% duty, len counter yes, env no, vol=8.
.byte $98, $0C			  ;C4,  12 counts.
.byte $9D, $06			  ;F4,   6 counts.
		.byte $9D, $06		  ;($880A)F4,   6 counts.
		.byte MCTL_ADD_SPACE, $0C;($880C)12 counts between notes.
		.byte $9D, $A1		  ;($880E)F4,  A4.
		.byte MCTL_CNTRL0,	$60;($8810)25% duty, len counter no, env yes, vol=0.
		.byte $A4			   ;($8812)C5.
		.byte $24			   ;($8813)36 counts.
		.byte MCTL_CNTRL0,	$FF;($8814)75% duty, len counter no, env no, vol=15.
		.byte MCTL_RETURN	   ;($8816)Return to previous music block.

;----------------------------------------------------------------------------------------------------

TRIOutdoor:
		.byte MCTL_TEMPO,	 $96;($8817)60/1=60 counts per second.
		.byte MCTL_ADD_SPACE, $10;($8819)16 counts between notes.

TRIOutdoorLoop:
		.byte MCTL_CNTRL0,	$FF;($881B)75% duty, len counter no, env no, vol=15.
		.byte $B2			   ;($881D)D6.
		.byte $10			   ;($881E)16 counts.
		.byte $B9			   ;($881F)A6.
		.byte $10			   ;($8820)16 counts.
		.byte $B7			   ;($8821)G6.
		.byte $50			   ;($8822)80 counts.
		.byte $B5, $B4, $B2	 ;($8823)F6  E6  D6.
		.byte $10			   ;($8826)16 counts.
		.byte $B0, $AE, $B0, $AD;($8827)C6  A#5, C6,  A5.
		.byte $B4			   ;($882B)E6.
		.byte $10			   ;($882C)16 counts.
		.byte $B2			   ;($882D)D6.
		.byte $30			   ;($882E)48 counts.
		.byte $40			   ;($882F)64 counts.
		.byte $40			   ;($8830)64 counts.
		.byte $B9			   ;($8831)A6.
		.byte $10			   ;($8832)16 counts.
.byte $BC				   ;C7.
		.byte $10			   ;($8834)16 counts.
.byte $BB				   ;B6.
		.byte $50			   ;($8836)80 counts.
		.byte $B7, $B5, $B4	 ;($8837)G6,  F6,  E6.
		.byte $10			   ;($883A)16 counts.
		.byte $B5, $B7, $B9	 ;($883B)F6,  G6,  A6.
		.byte $70			   ;($883E)112 counts.
		.byte $40			   ;($883F)64 counts.
		.byte $40			   ;($8840)64 counts.
		.byte MCTL_JUMP		 ;($8841)Jump to new music address.
.word TRIOutdoorLoop		;($881B).

;----------------------------------------------------------------------------------------------------

SQ1Outdoor:
		.byte MCTL_ADD_SPACE, $10;($8844)16 counts between notes.
		.byte MCTL_CNTRL0,	$81;($8846)50% duty, len counter yes, env yes, vol=1.

SQ1OutdoorLoop:
		.byte $9A, $A1, $9D, $A1;($8848)D4,  A4,  F4,  A4.
		.byte $9A, $A3, $9F, $A3;($884C)D4,  B4,  G4,  B4.
		.byte $9A, $A4, $A1, $A4;($8850)D4,  C5,  A4,  C5.
		.byte $9A, $A2, $9D, $A2;($8854)D4,  A#4, F4,  A#4.
		.byte $9C, $A4, $A1, $A4;($8858)E4,  C5,  A4,  C5.
		.byte $9A, $A1, $9E, $A1;($885C)D4,  A4,  F#4, A4.
.byte $9A, $A1, $9E, $A1	;D4,  A4,  F#4, A4.
		.byte $9F, $A2, $A1, $A4;($8864)G4,  A#4, A4,  C5.
		.byte $9A, $A4, $A1, $A4;($8868)D4,  C5,  A4,  C5.
		.byte $9A, $A3, $9F, $A3;($886C)D4,  B4,  G4,  B4.
		.byte $9A, $A3, $9F, $A3;($8870)D4,  B4,  G4,  B4.
		.byte $9A, $A2, $A0, $A2;($8874)D4,  A#4, Ab4, A#4.
		.byte $99, $A1, $9C, $A1;($8878)C#4, A4,  E4,  A4.
		.byte $9A, $A1, $9C, $A1;($887C)D4,  A4,  E4,  A4.
		.byte $99, $A1, $9C, $A1;($8880)C#4, A4,  E4,  A4.
		.byte $97, $A1, $99, $A1;($8884)B3,  A4,  C#4, A4.
.byte MCTL_JUMP			 ;Jump to new music address.
		.word SQ1OutdoorLoop	;($8889)($8848).

;----------------------------------------------------------------------------------------------------

SQ1Dngn:
		.byte MCTL_JUMP		 ;($888B)Jump to new music address.
		.word SQ1Dngn2		  ;($888C)($88CA).
		.byte MCTL_JUMP		 ;($888E)Jump to new music address.
		.word SQ1Dngn2		  ;($888F)($88CA).
		.byte MCTL_JUMP		 ;($8891)Jump to new music address.
		.word SQ1Dngn2		  ;($8892)($88CA).
		.byte MCTL_JUMP		 ;($8894)Jump to new music address.
		.word SQ1Dngn2		  ;($8895)($88CA).
		.byte MCTL_JUMP		 ;($8897)Jump to new music address.
.word SQ1Dngn3			  ;($88E1).
		.byte MCTL_JUMP		 ;($889A)Jump to new music address.
		.word SQ1Dngn3		  ;($889B)($88E1).
		.byte MCTL_JUMP		 ;($889D)Jump to new music address.
		.word SQ1Dngn4		  ;($889E)($88ED).
		.byte MCTL_JUMP		 ;($88A0)Jump to new music address.
		.word SQ1Dngn4		  ;($88A1)($88ED).
		.byte MCTL_JUMP		 ;($88A3)Jump to new music address.
		.word SQ1Dngn5		  ;($88A4)($88F9).
		.byte MCTL_JUMP		 ;($88A6)Jump to new music address.
		.word SQ1Dngn5		  ;($88A7)($88F9).
		.byte MCTL_JUMP		 ;($88A9)Jump to new music address.
		.word SQ1Dngn5		  ;($88AA)($88F9).
		.byte MCTL_JUMP		 ;($88AC)Jump to new music address.
		.word SQ1Dngn5		  ;($88AD)($88F9).
		.byte MCTL_JUMP		 ;($88AF)Jump to new music address.
		.word SQ1Dngn6		  ;($88B0)($8905).
		.byte MCTL_JUMP		 ;($88B2)Jump to new music address.
		.word SQ1Dngn6		  ;($88B3)($8905).
		.byte $96, $0C		  ;($88B5)A#3, 12 counts.
		.byte MCTL_CNTRL0,	$30;($88B7)12.5% duty, len counter no, env no, vol=0.
		.byte $24			   ;($88B9)36 counts.
.byte MCTL_CNTRL0,	$B6   ;50% duty, len counter no, env no, vol=6.
		.byte MCTL_JUMP		 ;($88BC)Jump to new music address.
		.word SQ1Dngn7		  ;($88BD)($8911).
		.byte MCTL_JUMP		 ;($88BF)Jump to new music address.
		.word SQ1Dngn7		  ;($88C0)($8911).
		.byte $95, $0C		  ;($88C2)A3,  12 counts.
		.byte MCTL_CNTRL0,	$30;($88C4)12.5% duty, len counter no, env no, vol=0.
		.byte $24			   ;($88C6)36 counts.
		.byte MCTL_JUMP		 ;($88C7)Jump to new music address.
		.word SQ1Dngn		   ;($88C8)($888B).

SQ1Dngn2:
.byte MCTL_CNTRL0,	$30   ;12.5% duty, len counter no, env no, vol=0.
		.byte $05			   ;($88CC)5 counts.
		.byte MCTL_CNTRL0,	$B6;($88CD)50% duty, len counter no, env no, vol=6.
		.byte $97, $07		  ;($88CF)B3,   7 counts.
		.byte $9A, $06		  ;($88D1)D4,   6 counts.
		.byte $9F, $06		  ;($88D3)G4,   6 counts.
.byte MCTL_CNTRL0,	$30   ;12.5% duty, len counter no, env no, vol=0.
		.byte $05			   ;($88D7)5 counts.
.byte MCTL_CNTRL0,	$B6   ;50% duty, len counter no, env no, vol=6.
		.byte $97, $07		  ;($88DA)B3,   7 counts.
		.byte $9A, $06		  ;($88DC)D4,   6 counts.
		.byte $9F, $06		  ;($88DE)G4,   6 counts.
		.byte MCTL_RETURN	   ;($88E0)Return to previous music block.

SQ1Dngn3:
		.byte MCTL_CNTRL0,	$30;($88E1)12.5% duty, len counter no, env no, vol=0.
		.byte $05			   ;($88E3)5 counts.
		.byte MCTL_CNTRL0,	$B6;($88E4)50% duty, len counter no, env no, vol=6.
		.byte $96, $07		  ;($88E6)A#3,  7 counts.
		.byte $99, $06		  ;($88E8)C#4,  6 counts.
		.byte $9C, $06		  ;($88EA)E4,   6 counts.
		.byte MCTL_RETURN	   ;($88EC)Return to previous music block.

SQ1Dngn4:
		.byte MCTL_CNTRL0,	$30;($88ED)12.5% duty, len counter no, env no, vol=0.
		.byte $05			   ;($88EF)5 counts.
		.byte MCTL_CNTRL0,	$B6;($88F0)50% duty, len counter no, env no, vol=6.
		.byte $97, $07		  ;($88F2)B3,   7 counts.
		.byte $9A, $06		  ;($88F4)D4,   6 counts.
.byte $9D, $06			  ;F4,   6 counts.
		.byte MCTL_RETURN	   ;($88F8)Return to previous music block.

SQ1Dngn5:
		.byte MCTL_CNTRL0,	$30;($88F9)12.5% duty, len counter no, env no, vol=0.
		.byte $05			   ;($88FB)5 counts.
		.byte MCTL_CNTRL0,	$B6;($88FC)50% duty, len counter no, env no, vol=6.
		.byte $91, $07		  ;($88FE)F3,   7 counts.
.byte $94, $06			  ;Ab3,  6 counts.
		.byte $98, $06		  ;($8902)C4,   6 counts.
		.byte MCTL_RETURN	   ;($8904)Return to previous music block.

SQ1Dngn6:
.byte MCTL_ADD_SPACE, $03   ;3 counts between notes.
		.byte $96, $98, $96, $98;($8907)A#3, C4,  A#3, C4.
		.byte $96, $98, $96, $98;($890B)A#3, C4,  A#3, C4.
		.byte MCTL_END_SPACE	;($890F)Disable counts between notes.
.byte MCTL_RETURN		   ;Return to previous music block.

SQ1Dngn7:
		.byte MCTL_ADD_SPACE, $03;($8911)3 counts between notes.
		.byte $95, $97, $95, $97;($8913)A3,  B3,  A3,  B3.
		.byte $95, $97, $95, $97;($8917)A3,  B3,  A3,  B3.
		.byte MCTL_END_SPACE	;($891B)Disable counts between notes.
		.byte MCTL_RETURN	   ;($891C)Return to previous music block.

;----------------------------------------------------------------------------------------------------

TRIDngn1:
.byte MCTL_NOTE_OFST, $09   ;Note offset of 9 notes.
		.byte MCTL_TEMPO,	 $69;($891F)60/1.43=42 counts per second.
		.byte MCTL_JUMP		 ;($8921)Jump to new music address.
		.word TRIDngn		   ;($8922)($8950).

TRIDngn2:
		.byte MCTL_NOTE_OFST, $06;($8924)Note offset of 6 notes.
		.byte MCTL_TEMPO,	 $64;($8926)60/1.5=40 counts per second.
		.byte MCTL_JUMP		 ;($8928)Jump to new music address.
		.word TRIDngn		   ;($8929)($8950).

TRIDngn3:
		.byte MCTL_NOTE_OFST, $03;($892B)Note offset of 3 notes.
.byte MCTL_TEMPO,	 $5F   ;60/1.58=38 counts per second.
		.byte MCTL_JUMP		 ;($892F)Jump to new music address.
		.word TRIDngn		   ;($8930)($8950).

TRIDngn4:
.byte MCTL_TEMPO,	 $5A   ;60/1.67=36 counts per second.
		.byte MCTL_JUMP		 ;($8934)Jump to new music address.
		.word TRIDngn		   ;($8935)($8950).

TRIDngn5:
		.byte MCTL_NOTE_OFST, $FD;($8937)Note offset of 253 notes.
		.byte MCTL_TEMPO,	 $55;($8939)60/1.76=34 counts per second.
		.byte MCTL_JUMP		 ;($893B)Jump to new music address.
		.word TRIDngn		   ;($893C)($8950).

TRIDngn6:
		.byte MCTL_NOTE_OFST, $FA;($893E)Note offset of 250 notes.
		.byte MCTL_TEMPO,	 $50;($8940)60/1.88=32 counts per second.
		.byte MCTL_JUMP		 ;($8942)Jump to new music address.
		.word TRIDngn		   ;($8943)($8950).

TRIDngn7:
		.byte MCTL_NOTE_OFST, $F7;($8945)Note offset of 247 notes.
		.byte MCTL_TEMPO,	 $4B;($8947)60/2.0=30 counts per second.
		.byte MCTL_JUMP		 ;($8949)Jump to new music address.
		.word TRIDngn		   ;($894A)($8950).

TRIDngn8:
.byte MCTL_NOTE_OFST, $F4   ;Note offset of 244 notes.
		.byte MCTL_TEMPO,	 $46;($894E)60/2.14=28 counts per second.

TRIDngn:
.byte MCTL_CNTRL0,	$FF   ;75% duty, len counter no, env no, vol=15.
		.byte $AC, $18		  ;($8952)Ab5, 24 counts.
		.byte $AE, $18		  ;($8954)A#5, 24 counts.
		.byte $AC, $18		  ;($8956)Ab5, 24 counts.
		.byte $AE, $18		  ;($8958)A#5, 24 counts.
		.byte $B1, $18		  ;($895A)C#6, 24 counts.
.byte $AE, $18			  ;A#5, 24 counts.
		.byte $AC, $18		  ;($895E)Ab5, 24 counts.
		.byte $AE, $0C		  ;($8960)A#5, 12 counts.
.byte $AC, $0C			  ;Ab5, 12 counts.
		.byte $AB, $18		  ;($8964)G5,  24 counts.
		.byte $A9, $0C		  ;($8966)F5,  12 counts.
		.byte $AB, $0C		  ;($8968)G5,  12 counts.
		.byte $AE, $0C		  ;($896A)A#5, 12 counts.
		.byte $AC, $0C		  ;($896C)Ab5, 12 counts.
.byte $AB, $0C			  ;G5,  12 counts.
		.byte $A9, $0C		  ;($8970)F5,  12 counts.
.byte $A8, $18			  ;E5,  24 counts.
		.byte $A6, $0C		  ;($8974)D5,  12 counts.
		.byte $A8, $0C		  ;($8976)E5,  12 counts.
		.byte $AB, $18		  ;($8978)G5,  24 counts.
		.byte $A4, $18		  ;($897A)C5,  24 counts.
		.byte MCTL_CNTRL0,	$30;($897C)12.5% duty, len counter no, env no, vol=0.
		.byte MCTL_JUMP		 ;($897E)Jump to new music address.
		.word TRIDngn9		  ;($897F)($8991).
		.byte MCTL_JUMP		 ;($8981)Jump to new music address.
.word TRIDngn9			  ;($8991).
		.byte $AA, $30		  ;($8984)F#5, 48 counts.
		.byte MCTL_JUMP		 ;($8986)Jump to new music address.
.word TRIDngn10			 ;($899D).
		.byte MCTL_JUMP		 ;($8989)Jump to new music address.
		.word TRIDngn10		 ;($898A)($899D).
.byte $A9, $30			  ;F5,  48 counts.
		.byte MCTL_JUMP		 ;($898E)Jump to new music address.
		.word TRIDngn		   ;($898F)($8950).

TRIDngn9:
		.byte MCTL_ADD_SPACE, $03;($8991)3 counts between notes.
		.byte $AA, $A8, $AA, $A8;($8993)F#5, E5,  F#5, E5.
.byte $AA, $A8, $AA, $A8	;F#5, E5,  F#5, E5.
.byte MCTL_END_SPACE		;Disable counts between notes.
		.byte MCTL_RETURN	   ;($899C)Return to previous music block.

TRIDngn10:
		.byte MCTL_ADD_SPACE, $03;($899D)3 counts between notes.
		.byte $A9, $A7, $A9, $A7;($899F)F5,  D#5, F5,  D#5.
		.byte $A9, $A7, $A9, $A7;($89A3)F5,  D#5, F5,  D#5.
.byte MCTL_END_SPACE		;Disable counts between notes.
		.byte MCTL_RETURN	   ;($89A8)Return to previous music block.

;----------------------------------------------------------------------------------------------------

SQ1EntFight:
		.byte MCTL_TEMPO,	 $50;($89A9)60/1.88=32 counts per second.
		.byte MCTL_CNTRL0,	$4F;($89AB)25% duty, len counter yes, env yes, vol=15.
		.byte MCTL_JUMP		 ;($89AD)Jump to new music address.
		.word EntFight		  ;($89AE)($8AAB).
		.byte MCTL_JUMP		 ;($89B0)Jump to new music address.
		.word EntFight		  ;($89B1)($8AAB).
		.byte MCTL_TEMPO,	 $78;($89B3)60/1.25=48 counts per second.
		.byte $98, $24		  ;($89B5)C4,  36 counts.
.byte $98, $06			  ;C4,   6 counts.
.byte $99, $06			  ;C#4,  6 counts.
		.byte $9A, $06		  ;($89BB)D4,   6 counts.
		.byte $9C, $06		  ;($89BD)E4,   6 counts.

;----------------------------------------------------------------------------------------------------

SQ1Fight:
		.byte MCTL_TEMPO,	 $78;($89BF)60/1.25=48 counts per second.

SQ1FightLoop:
		.byte MCTL_CNTRL0,	$7F;($89C1)25% duty, len counter no, env no, vol=15.
		.byte $9D, $18		  ;($89C3)F4, 24 counts.
		.byte MCTL_CNTRL0,	$4F;($89C5)25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($89C7)16 counts.
.byte MCTL_CNTRL0,	$7F   ;25% duty, len counter no, env no, vol=15.
		.byte $9F, $02		  ;($89CA)G4,   2 counts.
		.byte $A0, $02		  ;($89CC)Ab4,  2 counts.
		.byte $A1, $02		  ;($89CE)A4,   2 counts.
		.byte $A2, $02		  ;($89D0)A#4,  2 counts.
		.byte $A3, $18		  ;($89D2)B4,  24 counts.
.byte MCTL_CNTRL0,	$4F   ;25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($89D6)16 counts.
.byte MCTL_JUMP			 ;Jump to new music address.
		.word SQ1Fight2		 ;($89D8)($8ABF).
		.byte MCTL_CNTRL0,	$7F;($89DA)25% duty, len counter no, env no, vol=15.
		.byte $9D, $02		  ;($89DC)F4,   2 counts.
		.byte $9E, $02		  ;($89DE)F#4,  2 counts.
		.byte $9F, $02		  ;($89E0)G4,   2 counts.
		.byte $A0, $02		  ;($89E2)Ab4,  2 counts.
		.byte $A1, $18		  ;($89E4)A4,  24 counts.
.byte MCTL_CNTRL0,	$4F   ;25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($89E8)16 counts.
		.byte MCTL_CNTRL0,	$7F;($89E9)25% duty, len counter no, env no, vol=15.
		.byte $A0, $02		  ;($89EB)Ab4,  2 counts.
		.byte $A1, $02		  ;($89ED)A4,   2 counts.
		.byte $A2, $02		  ;($89EF)A#4,  2 counts.
.byte $A3, $02			  ;B4,   2 counts.
		.byte $A4, $18		  ;($89F3)C5,  24 counts.
.byte MCTL_CNTRL0,	$4F   ;25% duty, len counter yes, env yes, vol=15.
.byte $10				   ;16 counts.
		.byte MCTL_JUMP		 ;($89F8)Jump to new music address.
		.word SQ1Fight2		 ;($89F9)($8ABF).
		.byte MCTL_JUMP		 ;($89FB)Jump to new music address.
		.word SQ1Fight2		 ;($89FC)($8ABF).
		.byte MCTL_CNTRL0,	$7F;($89FE)25% duty, len counter no, env no, vol=15.
		.byte $9D, $02		  ;($8A00)F4,   2 counts.
		.byte $9E, $02		  ;($8A02)F#4,  2 counts.
.byte $9F, $02			  ;G4,   2 counts.
		.byte $A0, $02		  ;($8A06)Ab4,  2 counts.
		.byte $A1, $18		  ;($8A08)A4,  24 counts.
		.byte MCTL_CNTRL0,	$4F;($8A0A)25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($8A0C)16 counts.
		.byte MCTL_CNTRL0,	$7F;($8A0D)25% duty, len counter no, env no, vol=15.
		.byte $9B, $02		  ;($8A0F)D#4,  2 counts.
		.byte $9C, $02		  ;($8A11)E4,   2 counts.
.byte $9D, $02			  ;F4,   2 counts.
		.byte $9E, $02		  ;($8A15)F#4,  2 counts.
.byte $9F, $18			  ;G4,  24 counts.
		.byte MCTL_CNTRL0,	$4F;($8A19)25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($8A1B)16 counts.
		.byte MCTL_CNTRL0,	$7F;($8A1C)25% duty, len counter no, env no, vol=15.
		.byte $A5, $02		  ;($8A1E)C#5,  2 counts.
		.byte $A6, $02		  ;($8A20)D5,   2 counts.
.byte $A7, $02			  ;D#5,  2 counts.
		.byte $A8, $02		  ;($8A24)E5,   2 counts.
		.byte $A9, $18		  ;($8A26)F5,  24 counts.
		.byte MCTL_CNTRL0,	$4F;($8A28)25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($8A2A)16 counts.
		.byte MCTL_CNTRL0,	$7F;($8A2B)25% duty, len counter no, env no, vol=15.
		.byte $A4, $02		  ;($8A2D)C5,   2 counts.
		.byte $A5, $02		  ;($8A2F)C#5,  2 counts.
.byte $A6, $02			  ;D5,   2 counts.
		.byte $A7, $02		  ;($8A33)D#5,  2 counts.
		.byte $A8, $18		  ;($8A35)E5,  24 counts.
.byte MCTL_CNTRL0,	$4F   ;25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($8A39)16 counts.
		.byte MCTL_CNTRL0,	$7F;($8A3A)25% duty, len counter no, env no, vol=15.
.byte $A3, $02			  ;B4,   2 counts.
		.byte $A4, $02		  ;($8A3E)C5,   2 counts.
.byte $A5, $02			  ;C#5,  2 counts.
		.byte $A6, $02		  ;($8A42)D5,   2 counts.
		.byte $A7, $18		  ;($8A44)D#5, 24 counts.
		.byte MCTL_CNTRL0,	$4F;($8A46)25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($8A48)16 counts.
		.byte MCTL_CNTRL0,	$7F;($8A49)25% duty, len counter no, env no, vol=15.
		.byte $A3, $02		  ;($8A4B)B4,   2 counts.
		.byte $A4, $02		  ;($8A4D)C5,   2 counts.
.byte $A5, $02			  ;C#5,  2 counts.
		.byte $A6, $02		  ;($8A51)D5,   2 counts.
		.byte $A7, $18		  ;($8A53)D#5, 24 counts.
		.byte MCTL_CNTRL0,	$4F;($8A55)25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($8A57)16 counts.
		.byte MCTL_CNTRL0,	$7F;($8A58)25% duty, len counter no, env no, vol=15.
		.byte $A2, $02		  ;($8A5A)A#4,  2 counts.
.byte $A3, $02			  ;B4,   2 counts.
.byte $A4, $02			  ;C5,   2 counts.
		.byte $A5, $02		  ;($8A60)C#5,  2 counts.
.byte $A6, $18			  ;D5,  24 counts.
		.byte MCTL_CNTRL0,	$4F;($8A64)25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($8A66)16 counts.
		.byte MCTL_CNTRL0,	$7F;($8A67)25% duty, len counter no, env no, vol=15.
		.byte $A1, $02		  ;($8A69)A4,   2 counts.
		.byte $A2, $02		  ;($8A6B)A#4,  2 counts.
.byte $A3, $02			  ;B4,   2 counts.
		.byte $A4, $02		  ;($8A6F)C5,   2 counts.
		.byte $A5, $18		  ;($8A71)C#5, 24 counts.
		.byte MCTL_CNTRL0,	$4F;($8A73)25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($8A75)16 counts.
		.byte MCTL_CNTRL0,	$7F;($8A76)25% duty, len counter no, env no, vol=15.
		.byte $A2, $02		  ;($8A78)A#4,  2 counts.
		.byte $A3, $02		  ;($8A7A)B4,   2 counts.
.byte $A4, $02			  ;C5,   2 counts.
		.byte $A5, $02		  ;($8A7E)C#5,  2 counts.
		.byte $A6, $18		  ;($8A80)D5,  24 counts.
.byte MCTL_CNTRL0,	$4F   ;25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($8A84)16 counts.
		.byte $A7, $02		  ;($8A85)D#5,  2 counts.
		.byte $A8, $02		  ;($8A87)E5,   2 counts.
		.byte $A9, $02		  ;($8A89)F5,   2 counts.
.byte $AA, $02			  ;F#5,  2 counts.
		.byte MCTL_ADD_SPACE, $08;($8A8D)8 counts between notes.
		.byte $AB, $A6, $AB, $AA;($8A8F)G5,  D5,  G5,  F#5.
		.byte $A7, $AA, $A9, $A6;($8A93)D#5, F#5, F5,  D5.
		.byte $A9, $A8, $A5, $A8;($8A97)F5,  E5,  C#5, E5.
		.byte $A7, $A4, $A1, $9E;($8A9B)D#5, C5,  A4,  F#4.
		.byte $9B, $98, $99, $90;($8A9F)D#4, C4,  C#4, E3.
		.byte $93, $96, $99, $9C;($8AA3)G3,  A#3, C#4, E4.
		.byte MCTL_END_SPACE	;($8AA7)Disable counts between notes.
		.byte MCTL_JUMP		 ;($8AA8)Jump to new music address.
		.word SQ1FightLoop	  ;($8AA9)($89C1).

;----------------------------------------------------------------------------------------------------

EntFight:
		.byte MCTL_ADD_SPACE, $01;($8AAB)1 counts between notes.
		.byte $98, $9C, $9F, $A2;($8AAD)C4,  E4,  G4,  A#4.
		.byte $A5, $A8, $AB, $AE;($8AB1)C#5, E5,  G5,  A#5.
		.byte $B1, $AE, $AB, $A8;($8AB5)C#6, A#5, G5,  E5.
		.byte $A4, $A2, $9F, $9C;($8AB9)C5,  A#4, G4,  E4.
		.byte MCTL_END_SPACE	;($8ABD)Disable counts between notes.
		.byte MCTL_RETURN	   ;($8ABE)Return to previous music block.

;----------------------------------------------------------------------------------------------------

SQ1Fight2:
		.byte MCTL_CNTRL0,	$7F;($8ABF)25% duty, len counter no, env no, vol=15.
		.byte $9E, $02		  ;($8AC1)F#4,  2 counts.
.byte $9F, $02			  ;G4,   2 counts.
		.byte $A0, $02		  ;($8AC5)Ab4,  2 counts.
		.byte $A1, $02		  ;($8AC7)A4,   2 counts.
		.byte $A2, $18		  ;($8AC9)A#4, 24 counts.
		.byte MCTL_CNTRL0,	$4F;($8ACB)25% duty, len counter yes, env yes, vol=15.
		.byte $10			   ;($8ACD)16 counts.
		.byte MCTL_RETURN	   ;($8ACE)Return to previous music block.

;----------------------------------------------------------------------------------------------------

TRIEntFight:
		.byte MCTL_CNTRL0,	$30;($8ACF)12.5% duty, len counter no, env no, vol=0.
		.byte MCTL_JUMP		 ;($8AD1)Jump to new music address.
		.word EntFight		  ;($8AD2)($8AAB).
		.byte MCTL_JUMP		 ;($8AD4)Jump to new music address.
		.word EntFight		  ;($8AD5)($8AAB).
		.byte $98, $24		  ;($8AD7)C4,  36 counts.
		.byte $98, $06		  ;($8AD9)C4,   6 counts.
		.byte $99, $06		  ;($8ADB)C#4,  6 counts.
		.byte $9A, $06		  ;($8ADD)D4,   6 counts.
		.byte $9C, $06		  ;($8ADF)E4,   6 counts.

;----------------------------------------------------------------------------------------------------

TRIFight:
		.byte MCTL_CNTRL0,	$10;($8AE1)12.5% duty, len counter yes, env no, vol=0.
.byte MCTL_ADD_SPACE, $06   ;6 counts between notes.
		.byte $9D, $A0, $A4	 ;($8AE5)F4,  Ab4, C5.
		.byte $12			   ;($8AE8)18 counts.
		.byte $A6			   ;($8AE9)D5.
.byte $06				   ;6 counts.
		.byte $9D, $A0, $A3	 ;($8AEB)F4,  Ab4, B4.
		.byte $12			   ;($8AEE)18 counts.
		.byte $A6			   ;($8AEF)D5.
		.byte $06			   ;($8AF0)6 counts.
		.byte $9F, $A2, $A5	 ;($8AF1)G4,  A#4, C#5.
.byte $12				   ;18 counts.
		.byte $A8			   ;($8AF5)E5.
		.byte $06			   ;($8AF6)6 counts.
		.byte $9B, $9E, $A1	 ;($8AF7)D#4, F#4, A4.
		.byte $12			   ;($8AFA)18 counts.
		.byte $A4			   ;($8AFB)C5.
		.byte $06			   ;($8AFC)6 counts.
		.byte $A1, $A4, $A7	 ;($8AFD)A4,  C5,  D#5.
		.byte $12			   ;($8B00)18 counts.
		.byte $AB			   ;($8B01)G5.
		.byte $06			   ;($8B02)6 counts.
.byte $9B, $9F, $A5		 ;D#4, G4,  C#5.
		.byte $12			   ;($8B06)18 counts.
		.byte $A8			   ;($8B07)E5.
.byte $06				   ;6 counts.
		.byte $9E, $A2, $A6	 ;($8B09)F#4, A#4, D5.
		.byte $12			   ;($8B0C)18 counts.
		.byte $AA			   ;($8B0D)F#5.
		.byte $06			   ;($8B0E)6 counts.
		.byte $9A, $9E, $A1	 ;($8B0F)D4,  F#4, A4.
.byte $12				   ;18 counts.
.byte $A6				   ;D5.
		.byte $06			   ;($8B14)6 counts.
		.byte $9F, $A2, $A6	 ;($8B15)G4,  A#4, D5.
		.byte $12			   ;($8B18)18 counts.
		.byte $A8			   ;($8B19)E5.
		.byte $06			   ;($8B1A)6 counts.
		.byte $9F, $A3, $A6	 ;($8B1B)G4,  B4,  D5.
		.byte $12			   ;($8B1E)18 counts.
		.byte $A9			   ;($8B1F)F5.
		.byte $06			   ;($8B20)6 counts.
		.byte $98, $9F, $A2	 ;($8B21)C4,  G4,  A#4.
		.byte $12			   ;($8B24)18 counts.
		.byte $A5			   ;($8B25)C#5.
.byte $06				   ;6 counts.
		.byte $9D, $9E, $A1	 ;($8B27)F4,  F#4, A4.
		.byte $12			   ;($8B2A)18 counts.
		.byte $A4			   ;($8B2B)C5.
		.byte $06			   ;($8B2C)6 counts.
		.byte $96, $9D, $A0	 ;($8B2D)A#3, F4,  Ab4.
.byte $12				   ;18 counts.
		.byte $A7			   ;($8B31)D#5.
		.byte $06			   ;($8B32)6 counts.
.byte $96, $9D, $A0		 ;A#3, F4,  Ab4.
		.byte $12			   ;($8B36)18 counts.
		.byte $A6			   ;($8B37)D5.
		.byte $06			   ;($8B38)6 counts.
		.byte $95, $9C, $9F	 ;($8B39)A3,  E4,  G4.
		.byte $12			   ;($8B3C)18 counts.
		.byte $A2			   ;($8B3D)A#4.
		.byte $06			   ;($8B3E)6 counts.
		.byte $9A, $9E, $A1	 ;($8B3F)D4,  F#4, A4.
		.byte $12			   ;($8B42)18 counts.
.byte $A6				   ;D5.
.byte $06				   ;6 counts.
		.byte MCTL_ADD_SPACE, $08;($8B45)8 counts between notes.
		.byte $AE, $AB, $AE, $AD;($8B47)A#5, G5,  A#5, A5.
		.byte $AA, $AD, $AC, $A9;($8B4B)F#5, A5,  Ab5, F5.
.byte $AC, $AB, $A8, $AB	;Ab5, G5,  E5,  G5.
		.byte $AA, $AD, $AA, $A7;($8B53)F#5, A5,  F#5, D#5.
		.byte $A4, $A1, $A2, $99;($8B57)C5,  A4,  A#4, C#4.
		.byte $9C, $9F, $A2, $A5;($8B5B)E4,  G4,  A#4, C#5.
.byte MCTL_JUMP			 ;Jump to new music address.
		.word $8AE3			 ;($8B60)

;----------------------------------------------------------------------------------------------------

SQ1EndBoss:
.byte MCTL_TEMPO,	 $50   ;60/1.88=32 counts per second.

SQ1EndBoss2:
		.byte MCTL_JUMP		 ;($8B64)Jump to new music address.
		.word SQ1EndBoss3	   ;($8B65)($8BA1).
		.byte MCTL_JUMP		 ;($8B67)Jump to new music address.
		.word SQEndBoss		 ;($8B68)($8BB4).
		.byte MCTL_JUMP		 ;($8B6A)Jump to new music address.
		.word SQ1EndBoss3	   ;($8B6B)($8BA1).
		.byte MCTL_ADD_SPACE, $06;($8B6D)6 counts between notes.
.byte MCTL_CNTRL0,	$0F   ;12.5% duty, len counter yes, env yes, vol=15.
.byte $99, $9B, $9C, $9E	;C#4, D#4, E4,  F#4.
		.byte $9F			   ;($8B75)G4.
		.byte $1E			   ;($8B76)30 counts.
		.byte $A2, $9F, $A5	 ;($8B77)A#4, G4,  C#5.
		.byte $06			   ;($8B7A)6 counts.
		.byte $A4, $A2, $A1	 ;($8B7B)C5,  A#4, A4.
		.byte $06			   ;($8B7E)6 counts.
		.byte $9F			   ;($8B7F)G4.
.byte $06				   ;6 counts.
.byte $A1				   ;A4.
		.byte $06			   ;($8B82)6 counts.
		.byte $A2			   ;($8B83)A#4.
		.byte $12			   ;($8B84)18 counts.
		.byte $A4, $A2, $A1	 ;($8B85)C5,  A#4, A4.
		.byte $06			   ;($8B88)6 counts.
		.byte $9F			   ;($8B89)G4.
		.byte $06			   ;($8B8A)6 counts.
		.byte $A1, $A2, $A1, $9F;($8B8B)A4,  A#4, A4,  G4.
.byte $9E				   ;F#4.
		.byte $06			   ;($8B90)6 counts.
.byte $9C				   ;E4.
		.byte $06			   ;($8B92)6 counts.
		.byte $A1, $9F, $9E, $9C;($8B93)A4,  G4,  F#4, E4.
		.byte MCTL_CNTRL0,	$3F;($8B97)12.5% duty, len counter no, env no, vol=15.
		.byte $9B			   ;($8B99)D#4.
		.byte $2A			   ;($8B9A)42 counts.
		.byte MCTL_CNTRL0,	$0F;($8B9B)12.5% duty, len counter yes, env yes, vol=15.
		.byte $18			   ;($8B9D)24 counts.
.byte MCTL_JUMP			 ;Jump to new music address.
		.word SQ1EndBoss2	   ;($8B9F)($8B64).

SQ1EndBoss3:
.byte MCTL_ADD_SPACE, $0C   ;12 counts between notes.
		.byte MCTL_CNTRL0,	$82;($8BA3)50% duty, len counter yes, env yes, vol=2.
		.byte $95, $97		  ;($8BA5)A3,  B3.
		.byte MCTL_CNTRL0,	$02;($8BA7)12.5% duty, len counter yes, env yes, vol=2.
		.byte $95, $97		  ;($8BA9)A3,  B3.
		.byte MCTL_CNTRL0,	$82;($8BAB)50% duty, len counter yes, env yes, vol=2.
.byte $95, $97			  ;A3,  B3.
		.byte MCTL_CNTRL0,	$02;($8BAF)12.5% duty, len counter yes, env yes, vol=2.
.byte $95, $97			  ;A3,  B3.
		.byte MCTL_RETURN	   ;($8BB3)Return to previous music block.

;----------------------------------------------------------------------------------------------------

SQEndBoss:
		.byte MCTL_ADD_SPACE, $06;($8BB4)6 counts between notes.
		.byte MCTL_CNTRL0,	$0F;($8BB6)12.5% duty, len counter yes, env yes, vol=15.
		.byte $95, $97, $98, $9A;($8BB8)A3,  B3,  C4,  D4.
.byte $9B				   ;D#4.
		.byte $1E			   ;($8BBD)30 counts.
		.byte $9E, $9B, $A1	 ;($8BBE)F#4, D#4, A4.
.byte $06				   ;6 counts.
		.byte $A0, $9E, $9D	 ;($8BC2)Ab4, F#4, F4.
		.byte $06			   ;($8BC5)6 counts.
		.byte $9B			   ;($8BC6)D#4.
.byte $06				   ;6 counts.
		.byte $9D			   ;($8BC8)F4.
		.byte $06			   ;($8BC9)6 counts.
		.byte $9E			   ;($8BCA)F#4.
.byte $12				   ;18 counts.
		.byte $A0, $9E, $9D	 ;($8BCC)Ab4, F#4, F4.
		.byte $06			   ;($8BCF)6 counts.
		.byte $9B			   ;($8BD0)D#4.
		.byte $06			   ;($8BD1)6 counts.
		.byte $9D, $9E, $9D, $9B;($8BD2)F4,  F#4, F4,  D#4.
		.byte $9A			   ;($8BD6)D4.
.byte $06				   ;6 counts.
		.byte $98			   ;($8BD8)C4.
		.byte $06			   ;($8BD9)6 counts.
.byte $9D, $9B, $9A, $98	;F4,  D#4, D4,  C4.
		.byte MCTL_CNTRL0,	$3F;($8BDE)12.5% duty, len counter no, env no, vol=15.
		.byte $97			   ;($8BE0)B3.
		.byte $2A			   ;($8BE1)42 counts.
		.byte MCTL_CNTRL0,	$0F;($8BE2)12.5% duty, len counter yes, env yes, vol=15.
		.byte $18			   ;($8BE4)24 counts.
		.byte MCTL_RETURN	   ;($8BE5)Return to previous music block.

;----------------------------------------------------------------------------------------------------

SQ2EndBoss:
		.byte MCTL_ADD_SPACE, $0C;($8BE6)12 counts between notes.
		.byte MCTL_JUMP		 ;($8BE8)Jump to new music address.
.word SQ2EndBoss2		   ;($8C00).
		.byte MCTL_JUMP		 ;($8BEB)Jump to new music address.
		.word SQ2EndBoss3	   ;($8BEC)($8C11).
		.byte MCTL_JUMP		 ;($8BEE)Jump to new music address.
		.word SQ2EndBoss3	   ;($8BEF)($8C11).
		.byte MCTL_JUMP		 ;($8BF1)Jump to new music address.
		.word SQ2EndBoss3	   ;($8BF2)($8C11).
		.byte MCTL_JUMP		 ;($8BF4)Jump to new music address.
		.word SQ2EndBoss4	   ;($8BF5)($8C15).
.byte MCTL_JUMP			 ;Jump to new music address.
.word SQ2EndBoss2		   ;($8C00).
		.byte MCTL_JUMP		 ;($8BFA)Jump to new music address.
		.word SQEndBoss		 ;($8BFB)($8BB4).
		.byte MCTL_JUMP		 ;($8BFD)Jump to new music address.
		.word SQ2EndBoss		;($8BFE)($8BE6).

SQ2EndBoss2:
		.byte MCTL_CNTRL0,	$82;($8C00)50% duty, len counter yes, env yes, vol=2.
		.byte $90, $8E		  ;($8C02)E3,  D3.
		.byte MCTL_CNTRL0,	$02;($8C04)12.5% duty, len counter yes, env yes, vol=2.
		.byte $89, $8E		  ;($8C06)A2,  D3.
		.byte MCTL_CNTRL0,	$82;($8C08)50% duty, len counter yes, env yes, vol=2.
		.byte $90, $8E		  ;($8C0A)E3,  D3.
		.byte MCTL_CNTRL0,	$02;($8C0C)12.5% duty, len counter yes, env yes, vol=2.
		.byte $89, $8E		  ;($8C0E)A2,  D3.
		.byte MCTL_RETURN	   ;($8C10)Return to previous music block.

SQ2EndBoss3:
		.byte $92, $8F, $92, $8F;($8C11)F#3, D#3, F#3, D#3.

SQ2EndBoss4:
		.byte $92, $8F, $92, $8F;($8C15)F#3, D#3, F#3, D#3.
.byte MCTL_RETURN		   ;Return to previous music block.

;----------------------------------------------------------------------------------------------------

TRIEndBoss:
		.byte MCTL_CNTRL0,	$30;($8C1A)12.5% duty, len counter no, env no, vol=0.
		.byte MCTL_ADD_SPACE, $0C;($8C1C)12 counts between notes.

TRIEndBossLoop:
		.byte $9A, $98, $9A, $98;($8C1E)D4,  C4,  D4,  C4.
		.byte $9A, $98, $9A, $98;($8C22)D4,  C4,  D4,  C4.
		.byte MCTL_JUMP		 ;($8C26)Jump to new music address.
		.word TRIEndBoss2	   ;($8C27)($8C35).
.byte MCTL_JUMP			 ;Jump to new music address.
		.word TRIEndBoss2	   ;($8C2A)($8C35).
		.byte MCTL_JUMP		 ;($8C2C)Jump to new music address.
		.word TRIEndBoss2	   ;($8C2D)($8C35).
		.byte MCTL_JUMP		 ;($8C2F)Jump to new music address.
		.word TRIEndBoss3	   ;($8C30)($8C39).
		.byte MCTL_JUMP		 ;($8C32)Jump to new music address.
		.word TRIEndBossLoop	;($8C33)($8C1E).

TRIEndBoss2:
		.byte $9E, $9B, $9E, $9B;($8C35)F#4, D#4, F#4, D#4.

TRIEndBoss3:
.byte $9E, $9B, $9E, $9B	;F#4, D#4, F#4, D#4.
		.byte MCTL_RETURN	   ;($8C3D)Return to previous music block.

;----------------------------------------------------------------------------------------------------

SQ2SlvrHrp:
		.byte $03			   ;($8C3E)3 counts.

SQ1SlvrHrp:
		.byte MCTL_CNTRL0,	$30;($8C3F)12.5% duty, len counter no, env no, vol=0.
		.byte $06			   ;($8C41)6 counts.
.byte MCTL_CNTRL0,	$89   ;50% duty, len counter yes, env yes, vol=9.
		.byte MCTL_TEMPO,	 $3C;($8C44)60/2.5=24 counts per second.
		.byte $B9, $06		  ;($8C46)A6, 6 counts.
		.byte $B5, $05		  ;($8C48)F6, 5 counts.
		.byte $B2, $04		  ;($8C4A)D6, 4 counts.
		.byte MCTL_ADD_SPACE, $03;($8C4C)3 counts between notes.
		.byte $AF			   ;($8C4D)B5.
		.byte MCTL_TEMPO,	 $46;($8C4F)60/2.14=28 counts per second.
		.byte $B5, $B2, $AF, $AD;($8C51)F6,  D6,  B5,  A5.
		.byte MCTL_TEMPO,	 $50;($8C55)60/1.88=32 counts per second.
		.byte $B2, $AF, $AD, $A9;($8C57)D6,  B5,  A5,  F5.
		.byte MCTL_TEMPO,	 $5A;($8C5B)60/1.67=36 counts per second.
		.byte $AD, $A9, $A6, $A3;($8C5D)A5,  F5,  D5,  B4.
.byte MCTL_TEMPO,	 $64   ;60/1.5=40 counts per second.
		.byte $A9, $A6, $A3, $A1;($8C63)F5,  D5,  B4,  A4.
		.byte MCTL_TEMPO,	 $6D;($8C67)60/1.38=43 counts per second.
		.byte $A6, $A3, $A1, $9D;($8C69)D5,  B4,  A4,  F4.
		.byte MCTL_TEMPO,	 $76;($8C6D)60/1.27=47 counts per second.
		.byte $A1, $9D, $9A, $97;($8C6F)A4,  F4,  D4,  B3.
		.byte MCTL_TEMPO,	 $7F;($8C73)60/1.18=51 counts per second.
		.byte $9D, $9A, $97, $95;($8C75)F4,  D4,  B3,  A3.
		.byte MCTL_TEMPO,	 $88;($8C79)60/1.1=55 counts per second.
		.byte $9A, $97, $95, $91;($8C7B)D4,  B3,  A3,  F3.
.byte MCTL_TEMPO,	 $90   ;60/1.04=58 counts per second.
		.byte $87, $8E, $91, $95;($8C81)G2,  D3,  F3,  A3.
		.byte $97, $9A, $97, $9A;($8C85)B3,  D4,  B3,  D4.
		.byte $9D, $A1, $A3, $A6;($8C89)F4,  A4,  B4,  D5.
		.byte $A3, $A6, $A9, $AD;($8C8D)B4,  D5,  F5,  A5.
		.byte $AF, $B2		  ;($8C91)B5,  D6.
		.byte MCTL_END_SPACE	;($8C93)Disable counts between notes.
		.byte MCTL_CNTRL0,	$8F;($8C94)50% duty, len counter yes, env yes, vol=15.
		.byte $B7, $30		  ;($8C96)G6, 48 counts.
		.byte $00			   ;($8C98)End music.
		.byte MCTL_NO_OP		;($8C99)Continue previous music.

;----------------------------------------------------------------------------------------------------

TRIFryFlute:
		.byte MCTL_NOTE_OFST, $0C;($8C9A)Note offset of 12 notes.
		.byte MCTL_TEMPO,	 $78;($8C9C)60/1.25=48 counts per second.
		.byte MCTL_CNTRL0,	$FF;($8C9E)75% duty, len counter no, env no, vol=15.
		.byte $9F, $18		  ;($8CA0)G4, 24 counts.
.byte MCTL_ADD_SPACE, $03   ;3 counts between notes.
		.byte $A1, $A3, $A4, $A6;($8CA4)A4,  B4,  C5,  D5.
		.byte $A8, $A9, $AB, $AD;($8CA8)E5,  F5,  G5,  A5.
.byte $AF, $B0, $B2, $B4	;B5,  C6,  D6,  E6.
		.byte $B5			   ;($8CB0)F6.
		.byte MCTL_END_SPACE	;($8CB1)Disable counts between notes.
.byte MCTL_CNTRL0,	$20   ;12.5% duty, len counter no, env yes, vol=0.
		.byte $B7, $11		  ;($8CB4)G6, 17 counts.
		.byte $B7, $10		  ;($8CB6)G6, 16 counts.
		.byte $B7, $10		  ;($8CB8)G6, 16 counts.
		.byte MCTL_CNTRL0,	$FF;($8CBA)75% duty, len counter no, env no, vol=15.
		.byte MCTL_ADD_SPACE, $02;($8CBC)2 counts between notes.
		.byte $B7, $B9, $B7, $B9;($8CBE)G6,  A6,  G6,  A6.
		.byte $B7, $B9, $B7, $B9;($8CC2)G6,  A6,  G6,  A6.
		.byte $B7, $B9, $B7, $B9;($8CC6)G6,  A6,  G6,  A6.
.byte $B7, $B9, $B7, $B9	;G6,  A6,  G6,  A6.
		.byte $B7, $B9		  ;($8CCE)G6,  A6.
.byte MCTL_END_SPACE		;Disable counts between notes.
		.byte $B7, $0D		  ;($8CD1)G6, 13 counts.
		.byte $B5, $0D		  ;($8CD3)F6, 13 counts.
		.byte $B2, $08		  ;($8CD5)D6,  8 counts.
		.byte $AF, $08		  ;($8CD7)B5,  8 counts.
.byte $AD, $08			  ;A5,  8 counts.
		.byte $AB, $30		  ;($8CDB)G5, 48 counts.
		.byte MCTL_CNTRL0,	$00;($8CDD)12.5% duty, len counter yes, env yes, vol=0.
		.byte $00			   ;($8CDF)End music.
.byte MCTL_NO_OP			;Continue previous music.

;----------------------------------------------------------------------------------------------------

SQ2RnbwBrdg:
		.byte $03			   ;($8CE1)3 counts.

SQ1RnbwBrdg:
		.byte MCTL_TEMPO,	 $50;($8CE2)60/1.88=32 counts per second.
		.byte MCTL_CNTRL0,	$8F;($8CE4)50% duty, len counter yes, env yes, vol=15.
		.byte $8C, $09		  ;($8CE6)C3, 9 counts.
.byte $93, $08			  ;G3, 8 counts.
		.byte $97, $07		  ;($8CEA)B3, 7 counts.
		.byte $9C, $06		  ;($8CEC)E4, 6 counts.
		.byte $8E, $05		  ;($8CEE)D3, 5 counts.
.byte $95, $04			  ;A3, 4 counts.
		.byte MCTL_ADD_SPACE, $03;($8CF2)3 counts between notes.
		.byte $98, $9D		  ;($8CF4)C4,  F4.
		.byte MCTL_TEMPO,	 $58;($8CF6)60/1.7=35 counts per second.
		.byte $90, $97, $9A, $9F;($8CF8)E3,  B3,  D4,  G4.
		.byte MCTL_TEMPO,	 $60;($8CFC)60/1.56=38 counts per second.
		.byte $91, $98, $9C, $A1;($8CFE)F3,  C4,  E4,  A4.
		.byte MCTL_TEMPO,	 $68;($8D02)60/1.44=42 counts per second.
		.byte $87, $8E, $93, $98;($8D04)G2,  D3,  G3,  C4.
		.byte MCTL_TEMPO,	 $70;($8D08)60/1.34=45 counts per second.
		.byte $9C, $A1, $A4, $A9;($8D0A)E4,  A4,  C5,  F5.
		.byte $AD, $B0, $B5, $B4;($8D0E)A5,  C6,  F6,  E6.
.byte MCTL_TEMPO,	 $64   ;60/1.5=40 counts per second.
		.byte $AF, $AB, $A8, $A3;($8D14)B5,  G5,  E5,  B4.
		.byte MCTL_TEMPO,	 $5A;($8D18)60/1.67=36 counts per second.
		.byte $9F, $9C, $97, $93;($8D1A)G4,  E4,  B3,  G3.
		.byte MCTL_END_SPACE	;($8D1E)Disable counts between notes.
		.byte $8C, $30		  ;($8D1F)C3, 48 counts.
		.byte $00			   ;($8D21)End music.
.byte MCTL_NO_OP			;Continue previous music.

;----------------------------------------------------------------------------------------------------

SQ2Death:
		.byte $02			   ;($8D23)2 counts.

SQ1Death:
.byte MCTL_TEMPO,	 $96   ;60/1 = 60 counts per second.
		.byte MCTL_CNTRL0,	$30;($8D26)12.5% duty, len counter no, env no, vol=0.
		.byte $18			   ;($8D28)24 counts.
.byte MCTL_CNTRL0,	$4F   ;25% duty, len counter yes, env yes, vol=15.
		.byte MCTL_ADD_SPACE, $0C;($8D2B)12 counts between notes.
		.byte $A9, $9A, $A1, $A9;($8D2D)F5,  D4,  A4,  F5.
		.byte $A8, $99, $A1, $A8;($8D31)E5,  C#4, A4,  E5.
		.byte $A6, $96, $9F, $A6;($8D35)D5,  A#3, G4,  D5.
		.byte MCTL_END_SPACE	;($8D39)Disable counts between notes.
		.byte $A5, $0D		  ;($8D3A)C#5, 13 counts.
		.byte $A2, $0E		  ;($8D3C)A#4, 14 counts.
		.byte $A1, $0F		  ;($8D3E)A4,  15 counts.
		.byte $A0, $0F		  ;($8D40)Ab4, 15 counts.
.byte $A1, $04			  ;A4,   4 counts.
		.byte $A0, $04		  ;($8D44)Ab4,  4 counts.
		.byte $A1, $30		  ;($8D46)A4,  48 counts.
		.byte $00			   ;($8D48)End music.
		.byte MCTL_NO_OP		;($8D49)Continue previous music.

;----------------------------------------------------------------------------------------------------

SQ2Cursed:
		.byte $01			   ;($8D4A)1 count.

SQ1Cursed:
		.byte MCTL_TEMPO,	 $96;($8D4B)60/1 = 60 counts per second.
		.byte MCTL_CNTRL0,	$45;($8D4D)25% duty, len counter yes, env yes, vol=5.
.byte MCTL_ADD_SPACE, $06   ;6 counts between notes.
.byte MCTL_JUMP			 ;Jump to new music address.
		.word SQCursed2		 ;($8D52)($8D68).
		.byte MCTL_JUMP		 ;($8D54)Jump to new music address.
		.word SQCursed2		 ;($8D55)($8D68).
		.byte MCTL_JUMP		 ;($8D57)Jump to new music address.
		.word SQCursed2		 ;($8D58)($8D68).
		.byte MCTL_JUMP		 ;($8D5A)Jump to new music address.
.word SQCursed2			 ;($8D68).
		.byte MCTL_END_SPACE	;($8D5D)Disable counts between notes.
		.byte $90, $14		  ;($8D5E)E3,  20 counts.
.byte $91, $02			  ;F3,   2 counts.
		.byte $92, $02		  ;($8D62)F#3,  2 counts.
		.byte $8A, $30		  ;($8D64)A#2, 48 counts.
		.byte $00			   ;($8D66)End music.
		.byte MCTL_NO_OP		;($8D67)Continue previous music.

SQCursed2:
		.byte $8C, $97		  ;($8D68)C3, 151 counts.
.byte $8B, $96			  ;B2, 150 counts.
		.byte MCTL_RETURN	   ;($8D6C)Return to previous music block.

;----------------------------------------------------------------------------------------------------

SQ1Intro:

		.byte MCTL_TEMPO,	 $7D;($8D6D)60/1.2=50 counts per second.
.byte MCTL_CNTRL0,	$06   ;12.5% duty, len counter yes, env yes, vol=6.
		.byte $A1, $13		  ;($8D71)B4, 19 counts.
		.byte $A1, $05		  ;($8D73)A4,  5 counts.
		.byte MCTL_ADD_SPACE, $0C;($8D75)12 counts between notes.
		.byte $A1, $9F, $9F, $9F;($8D77)A4,  G4,  G4,  G4.
		.byte $9D, $9F, $A1, $A2;($8D7B)F4,  G4,  A4,  A#4.
.byte $A1, $9F, $A1, $A2	;A4,  G4,  A4,  A#4.
.byte $A4, $A6, $A9, $A6	;C5,  D5,  F5,  D5.
		.byte $A4, $A2, $A1	 ;($8D87)C5,  A#4, A4.
		.byte MCTL_END_SPACE	;($8D8A)Disable counts between notes.
		.byte $9F, $13		  ;($8D8B)G4, 19 counts.
.byte $9F, $05			  ;G4,  5 counts.
		.byte $9F, $0C		  ;($8D8F)G4, 12 counts.
		.byte $A1, $13		  ;($8D91)B4, 19 counts.
		.byte $A1, $05		  ;($8D93)B4,  5 counts.
.byte $A1, $0C			  ;B4, 12 counts.
.byte $A1, $0C			  ;B4, 12 counts.
		.byte $9D, $0C		  ;($8D99)F4, 12 counts.
		.byte $A1, $0C		  ;($8D9B)B4, 12 counts.
		.byte MCTL_CNTRL0,	$3F;($8D9D)12.5% duty, len counter no, env no, vol=15.
		.byte $9F, $60		  ;($8D9F)G4, 96 counts.
.byte MCTL_CNTRL0,	$30   ;12.5% duty, len counter no, env no, vol=0.
		.byte $18			   ;($8DA3)24 counts.
		.byte MCTL_TEMPO,	 $78;($8DA4)60/1.25=48 counts per second.

SQ1IntroLoop:
.byte MCTL_CNTRL0,	$4F   ;25% duty, len counter yes, env yes, vol=15.
		.byte $A4, $13		  ;($8DA8)C5, 19 counts.
		.byte $A4, $05		  ;($8DAA)C5,  5 counts.
		.byte $A9, $18		  ;($8DAC)F5, 24 counts.
		.byte MCTL_NO_OP		;($8DAE)Skip byte.
		.byte $AB, $18		  ;($8DAF)G5,  24 counts.
		.byte $AD, $18		  ;($8DB1)A5,  24 counts.
		.byte $AE, $18		  ;($8DB3)A#5, 24 counts.
.byte MCTL_CNTRL0,	$7F   ;25% duty, len counter no, env no, vol=15.
		.byte $B0, $18		  ;($8DB7)C6,  24 counts.
		.byte $B5, $30		  ;($8DB9)F6,  48 counts.
		.byte MCTL_CNTRL0,	$4F;($8DBB)25% duty, len counter yes, env yes, vol=15.
		.byte $B4, $13		  ;($8DBD)E6,  19 counts.
		.byte $B2, $05		  ;($8DBF)D6,   5 counts.
		.byte $B2, $24		  ;($8DC1)D6,  36 counts.
.byte $B0, $0C			  ;C6,  12 counts.
		.byte MCTL_CNTRL0,	$40;($8DC5)25% duty, len counter yes, env yes, vol=0.
		.byte $0C			   ;($8DC7)12 counts.
		.byte MCTL_CNTRL0,	$4F;($8DC8)25% duty, len counter yes, env yes, vol=15.
		.byte $AF, $0C		  ;($8DCA)B5,  12 counts.
		.byte $AF, $0C		  ;($8DCC)B5,  12 counts.
.byte $B2, $0C			  ;D6,  12 counts.
		.byte $B0, $18		  ;($8DD0)C6,  24 counts.
		.byte $AD, $30		  ;($8DD2)A5,  48 counts.
		.byte $A1, $13		  ;($8DD4)A4,  19 counts.
		.byte $A1, $05		  ;($8DD6)A4,   5 counts.
.byte $A1, $18			  ;A4,  24 counts.
		.byte $A1, $18		  ;($8DDA)A4,  24 counts.
		.byte $A3, $18		  ;($8DDC)B5,  24 counts.
		.byte $A5, $18		  ;($8DDE)C#5, 24 counts.
		.byte MCTL_CNTRL0,	$7F;($8DE0)25% duty, len counter no, env no, vol=15.
.byte $A6, $30			  ;D5,  48 counts.
		.byte MCTL_CNTRL0,	$4F;($8DE4)25% duty, len counter yes, env yes, vol=15.
		.byte $0C			   ;($8DE6)12 counts.
		.byte MCTL_ADD_SPACE, $0C;($8DE7)12 counts between notes.
		.byte $A6, $A8, $A9	 ;($8DE9)D5,  E5,  F5.
.byte MCTL_CNTRL0,	$7F   ;25% duty, len counter no, env no, vol=15.
		.byte $AB, $24		  ;($8DEE)G5,  36 counts.
		.byte MCTL_CNTRL0,	$4F;($8DF0)25% duty, len counter yes, env yes, vol=15.
		.byte $0C			   ;($8DF2)12 counts.
.byte $A6, $A6, $A9, $A9	;D5,  D5,  F5,  F5.
.byte $0C				   ;12 counts.
		.byte $A8			   ;($8DF7)E5.
.byte $0C				   ;12 counts.
		.byte $A6			   ;($8DF9)D5.
		.byte $0C			   ;($8DFA)12 counts.
		.byte $A4			   ;($8DFB)C5.
		.byte $0C			   ;($8DFC)12 counts.
		.byte MCTL_CNTRL0,	$7F;($8DFE)25% duty, len counter no, env no, vol=15.
.byte $AD				   ;A5.
		.byte $30			   ;($8E01)48 counts.
		.byte MCTL_CNTRL0,	$4F;($8E02)25% duty, len counter yes, env yes, vol=15.
		.byte $AE, $AD, $AB	 ;($8E04)A#5, A5, G5.
		.byte MCTL_CNTRL0,	$7F;($8E07)25% duty, len counter no, env no, vol=15.
		.byte $A9			   ;($8E09)F5.
.byte $24				   ;36 counts.
		.byte $A6			   ;($8E0B)D5.
		.byte $0C			   ;($8E0C)12 counts.
		.byte $A9			   ;($8E0D)F5.
		.byte $0C			   ;($8E0E)12 counts.
		.byte $AB			   ;($8E0F)G5.
		.byte $30			   ;($8E10)48 counts.
		.byte MCTL_CNTRL0,	$4F;($8E11)25% duty, len counter yes, env yes, vol=15.
		.byte $AD, $AB, $A9	 ;($8E13)A5,  G5,  F5.
		.byte MCTL_CNTRL0,	$7F;($8E16)25% duty, len counter no, env no, vol=15.
.byte $A9				   ;F5.
		.byte $24			   ;($8E19)36 counts.
		.byte $A8			   ;($8E1A)E5.
		.byte $0C			   ;($8E1B)12 counts.
		.byte $A4			   ;($8E1C)C5.
		.byte $0C			   ;($8E1D)12 counts.
.byte $B0				   ;C6.
		.byte $30			   ;($8E1F)48 counts.
		.byte MCTL_CNTRL0,	$4F;($8E20)25% duty, len counter yes, env yes, vol=15.
		.byte $AD, $AE, $B0	 ;($8E22)A5,  A#5, C6.
		.byte MCTL_CNTRL0,	$7F;($8E25)25% duty, len counter no, env no, vol=15.
		.byte $B2			   ;($8E27)D6.
.byte $30				   ;48 counts.
		.byte MCTL_CNTRL0,	$4F;($8E29)25% duty, len counter yes, env yes, vol=15.
		.byte $A6, $A8, $A9	 ;($8E2B)D5,  E5,  F5.
		.byte MCTL_END_SPACE	;($8E2E)Disable counts between notes.
		.byte MCTL_CNTRL0,	$7F;($8E2F)25% duty, len counter no, env no, vol=15.
		.byte $AE, $30		  ;($8E31)A#5, 48 counts.
		.byte $AD, $30		  ;($8E33)A5,  48 counts.
		.byte $A9, $3C		  ;($8E35)F5,  60 counts.
		.byte MCTL_CNTRL0,	$45;($8E37)25% duty, len counter yes, env yes, vol=5.
		.byte $0C			   ;($8E39)12 counts.
		.byte MCTL_JUMP		 ;($8E3A)Jump to new music address.
		.word SQ1IntroLoop	  ;($8E3B)($8DA6).

;----------------------------------------------------------------------------------------------------

SQ2Intro:
		.byte MCTL_CNTRL0,	$06;($8E3D)12.5% duty, len counter yes, env yes, vol=6.
		.byte $98, $13		  ;($8E3F)C4, 19 counts.
		.byte $9D, $05		  ;($8E41)F4,  5 counts.
		.byte MCTL_ADD_SPACE, $0C;($8E43)12 counts between notes.
		.byte $9D, $98, $98, $98;($8E45)F4,  C4,  C4,  C4.
		.byte $95, $98, $9D, $9F;($8E49)A3,  C4,  F4,  G4.
		.byte $9D, $98, $9D, $9F;($8E4D)F4,  C4,  F4,  G4.
		.byte $A1, $A2, $A6, $A2;($8E51)A4,  A#4, D5,  A#4.
		.byte $A1, $9F, $9D	 ;($8E55)A4,  G4,  F4.
		.byte MCTL_END_SPACE	;($8E58)Disable counts between notes.
		.byte $98, $13		  ;($8E59)C4, 19 counts.
		.byte $98, $05		  ;($8E5B)C4,  5 counts.
		.byte $98, $0C		  ;($8E5D)C4, 12 counts.
		.byte $9D, $13		  ;($8E5F)F4, 19 counts.
		.byte $9D, $05		  ;($8E61)F4,  5 counts.
		.byte $9D, $0C		  ;($8E63)F4, 12 counts.
		.byte $9D, $0C		  ;($8E65)F4, 12 counts.
		.byte $95, $0C		  ;($8E67)A3, 12 counts.
		.byte $9D, $0C		  ;($8E69)F4, 12 counts.
		.byte MCTL_CNTRL0,	$3F;($8E6B)12.5% duty, len counter no, env no, vol=15.
		.byte $98, $60		  ;($8E6D)C4, 96 counts.
		.byte MCTL_CNTRL0,	$30;($8E6F)12.5% duty, len counter no, env no, vol=0.
		.byte $18			   ;($8E71)24 counts.

SQ2IntroLoop:
		.byte MCTL_CNTRL0,	$4F;($8E72)25% duty, len counter yes, env yes, vol=15.
.byte $A2, $13			  ;A#4, 19 counts.
		.byte $A2, $05		  ;($8E76)A#4,  5 counts.
.byte $A1, $18			  ;A4,  24 counts.
		.byte $A4, $18		  ;($8E7A)C5,  24 counts.
		.byte $A9, $18		  ;($8E7C)F5,  24 counts.
		.byte $A9, $18		  ;($8E7E)F5,  24 counts.
		.byte MCTL_CNTRL0,	$7F;($8E80)25% duty, len counter no, env no, vol=15.
.byte $A9, $30			  ;F5,  48 counts.
.byte $A9, $30			  ;F5,  48 counts.
		.byte $AE, $24		  ;($8E86)A#5, 36 counts.
		.byte $AD, $0C		  ;($8E88)A5,  12 counts.
		.byte MCTL_CNTRL0,	$40;($8E8A)25% duty, len counter yes, env yes, vol=0.
.byte $0C				   ;12 counts.
		.byte MCTL_CNTRL0,	$4F;($8E8D)25% duty, len counter yes, env yes, vol=15.
		.byte $AC, $0C		  ;($8E8F)Ab5, 12 counts.
.byte $AC, $0C			  ;Ab5, 12 counts.
		.byte $AF, $0C		  ;($8E93)B5,  12 counts.
		.byte MCTL_CNTRL0,	$7F;($8E95)25% duty, len counter no, env no, vol=15.
		.byte $AD, $18		  ;($8E97)A5,  24 counts.
		.byte $A9, $30		  ;($8E99)F5,  48 counts.
.byte MCTL_CNTRL0,	$4F   ;25% duty, len counter yes, env yes, vol=15.
		.byte $95, $13		  ;($8E9D)A3,  19 counts.
		.byte $95, $05		  ;($8E9F)A3,   5 counts.
		.byte $99, $18		  ;($8EA1)C#4, 24 counts.
		.byte $99, $18		  ;($8EA3)C#4, 24 counts.
.byte $9A, $18			  ;D4,  24 counts.
		.byte $9C, $18		  ;($8EA7)E4,  24 counts.
		.byte MCTL_CNTRL0,	$7F;($8EA9)25% duty, len counter no, env no, vol=15.
.byte $9D, $30			  ;F4,  48 counts.
		.byte MCTL_CNTRL0,	$4F;($8EAD)25% duty, len counter yes, env yes, vol=15.
.byte $0C				   ;12 counts.
		.byte MCTL_ADD_SPACE, $0C;($8EB0)12 counts between notes.
.byte $9D, $9F, $A1		 ;F4, G4, A4.
		.byte MCTL_CNTRL0,	$7F;($8EB5)25% duty, len counter no, env no, vol=15.
		.byte $A6			   ;($8EB7)D5.
		.byte $24			   ;($8EB8)36 counts.
.byte MCTL_CNTRL0,	$4F   ;25% duty, len counter yes, env yes, vol=15.
		.byte $0C			   ;($8EBB)12 counts.
		.byte $A3, $A3, $A6, $A6;($8EBC)B4, B4, D5, D5.
		.byte $0C			   ;($8EC0)12 counts.
		.byte $A4			   ;($8EC1)C5.
.byte $0C				   ;12 counts.
.byte $A2				   ;A#4.
		.byte $0C			   ;($8EC4)12 counts.
		.byte $A2			   ;($8EC5)A#4.
		.byte $0C			   ;($8EC6)12 counts.
		.byte MCTL_CNTRL0,	$7F;($8EC7)25% duty, len counter no, env no, vol=15.
		.byte $A5			   ;($8EC9)C#5.
		.byte $30			   ;($8ECA)48 counts.
		.byte MCTL_CNTRL0,	$4F;($8ECB)25% duty, len counter yes, env yes, vol=15.
.byte $A5, $A5, $A5		 ;C#5, C#5, C#5.
		.byte MCTL_CNTRL0,	$7F;($8ED0)25% duty, len counter no, env no, vol=15.
.byte $A6				   ;D5.
		.byte $24			   ;($8ED3)36 counts.
		.byte $A1			   ;($8ED4)A4.
		.byte $0C			   ;($8ED5)12 counts.
		.byte $A1			   ;($8ED6)A4.
.byte $0C				   ;12 counts.
		.byte $A6			   ;($8ED8)D5.
		.byte $30			   ;($8ED9)48 counts.
		.byte MCTL_CNTRL0,	$4F;($8EDA)25% duty, len counter yes, env yes, vol=15.
.byte $A3, $A3, $A3		 ;B4,  B4, B4.
		.byte MCTL_CNTRL0,	$7F;($8EDF)25% duty, len counter no, env no, vol=15.
.byte $A2				   ;A#4.
.byte $24				   ;36 counts.
		.byte $A2			   ;($8EE3)A#4.
		.byte $0C			   ;($8EE4)12 counts.
		.byte $A2			   ;($8EE5)A#4.
.byte $0C				   ;12 counts.
		.byte $AA			   ;($8EE7)F#5.
		.byte $30			   ;($8EE8)48 counts.
		.byte MCTL_CNTRL0,	$4F;($8EE9)25% duty, len counter yes, env yes, vol=15.
.byte $AA, $AB, $AD		 ;F#5, G5,  A5.
		.byte MCTL_CNTRL0,	$7F;($8EEE)25% duty, len counter no, env no, vol=15.
.byte $AE				   ;A#5.
		.byte $30			   ;($8EF1)48 counts.
.byte MCTL_CNTRL0,	$4F   ;25% duty, len counter yes, env yes, vol=15.
.byte $A2, $A4, $A6		 ;A#4, C5,  D5.
		.byte MCTL_END_SPACE	;($8EF7)Disable counts between notes.
		.byte MCTL_CNTRL0,	$7F;($8EF8)25% duty, len counter no, env no, vol=15.
.byte $A6, $30			  ;D5, 48 counts.
		.byte $A8, $30		  ;($8EFC)E5, 48 counts.
		.byte $A1, $3C		  ;($8EFE)A4, 60 counts.
		.byte MCTL_CNTRL0,	$45;($8F00)25% duty, len counter yes, env yes, vol=5.
		.byte $0C			   ;($8F02)12 counts.
		.byte MCTL_JUMP		 ;($8F03)Jump to new music address.
.word SQ2IntroLoop		  ;($8E72).

;----------------------------------------------------------------------------------------------------

TriIntro:
		.byte MCTL_CNTRL0,	$60;($8F06)25% duty, len counter no, env yes, vol=0.
		.byte $9D, $60		  ;($8F08)F4, 96 counts.
		.byte $60			   ;($8F0A)96 counts.
		.byte $60			   ;($8F0B)96 counts.
		.byte $60			   ;($8F0C)96 counts.
		.byte $60			   ;($8F0D)96 counts.
.byte $18				   ;24 counts.
		.byte MCTL_CNTRL0,	$60;($8F0F)25% duty, len counter no, env yes, vol=0.
		.byte MCTL_ADD_SPACE, $18;($8F11)24 counts between notes.

TRIIntroLoop:
.byte $9D, $9C, $9B, $9A	;F4,  E4,  D#4, D4.
		.byte MCTL_CNTRL0,	$7F;($8F17)25% duty, len counter no, env no, vol=15.
		.byte $95			   ;($8F19)A3.
.byte $18				   ;24 counts.
		.byte $96			   ;($8F1B)A#3.
		.byte $18			   ;($8F1C)24 counts.
.byte MCTL_CNTRL0,	$60   ;25% duty, len counter no, env yes, vol=0.
		.byte $9D, $98, $91, $9D;($8F1F)F4,  C4,  F3,  F4.
		.byte $9D, $95, $98, $9D;($8F23)F4,  A3,  C4,  F4.
.byte MCTL_CNTRL0,	$7F   ;25% duty, len counter no, env no, vol=15.
		.byte $95			   ;($8F29)A3.
.byte $18				   ;24 counts.
		.byte $95			   ;($8F2B)A3.
.byte $18				   ;24 counts.
		.byte MCTL_CNTRL0,	$60;($8F2D)25% duty, len counter no, env yes, vol=0.
		.byte $9A, $95, $9D, $9A;($8F2F)D4,  A3,  F4,  D4.
		.byte $97, $9A, $9F, $93;($8F33)B3,  D4,  G4,  G3.
		.byte MCTL_CNTRL0,	$7F;($8F37)25% duty, len counter no, env no, vol=15.
		.byte $98			   ;($8F39)C4.
.byte $18				   ;24 counts.
.byte MCTL_CNTRL0,	$60   ;25% duty, len counter no, env yes, vol=0.
		.byte $98, $9C, $95, $99;($8F3D)C4,  E4,  A3,  C#4.
		.byte $9C, $95, $9A, $9C;($8F41)E4,  A3,  D4,  E4.
.byte $9D, $9A, $97, $9A	;F4,  D4,  B3,  D4.
		.byte $9F, $93, $98, $98;($8F49)G4,  G3,  C4,  C4.
.byte $9F, $A2, $A1, $9E	;G4,  A#4, A4,  F#4.
		.byte $9A, $95, $93, $95;($8F51)D4,  A3,  G3,  A3.
		.byte $96, $93, $9F, $98;($8F55)A#3, G3,  G4,  C4.
.byte $A2, $98, $9D, $98	;A#4, C4,  F4,  C4.
.byte $9D				   ;F4.
.byte $18				   ;24 counts.
		.byte MCTL_JUMP		 ;($8F5F)Jump to new music address.
		.word TRIIntroLoop	  ;($8F60)($8F13).

;----------------------------------------------------------------------------------------------------

SQ1EndGame:
		.byte MCTL_TEMPO,	 $82;($8F62)60/1.15=52 counts per second.
		.byte MCTL_CNTRL0,	$30;($8F64)12.5% duty, len counter no, env no, vol=0.
		.byte $30			   ;($8F66)48 counts.
		.byte MCTL_CNTRL0,	$46;($8F67)25% duty, len counter yes, env yes, vol=6.
		.byte $AB, $13		  ;($8F69)G5, 19 counts.
		.byte $AB, $05		  ;($8F6B)G5,  5 counts.
.byte MCTL_ADD_SPACE, $0C   ;12 counts between notes.
		.byte $AB, $AB, $AB, $AB;($8F6F)G5,  G5,  G5,  G5.
		.byte $AB, $AB, $AB, $AB;($8F73)G5,  G5,  G5,  G5.
.byte $AB, $AB, $A9, $AB	;G5,  G5,  F5,  G5.
		.byte $AD, $AB, $A9, $A8;($8F7B)A5,  G5,  F5,  E5.
.byte $A9, $AB, $AD, $AB	;F5,  G5,  A5,  G5.
		.byte $A9, $A8		  ;($8F83)F5,  E5.
.byte MCTL_TEMPO,	 $7D   ;60/1.2=50 counts per second.
		.byte $A9, $A9, $A9	 ;($8F87)F5,  F5,  F5.
		.byte MCTL_TEMPO,	 $7A;($8F8A)60/1.23=49 counts per second.
		.byte $AC, $AC, $AC	 ;($8F8C)Ab5 Ab5 Ab5.
		.byte MCTL_TEMPO,	 $76;($8F8F)60/1.27=47 counts per second.
.byte $AF, $AF, $AF		 ;B5,  B5,  B5.
.byte MCTL_TEMPO,	 $71   ;60/1.33=45 counts per second.
		.byte $B2, $B2, $B2	 ;($8F96)D6,  D6,  D6.
		.byte MCTL_CNTRL0,	$7F;($8F99)25% duty, len counter no, env no, vol=15.
		.byte $B7			   ;($8F9B)G6.
		.byte $54			   ;($8F9C)84 counts.
.byte MCTL_CNTRL0,	$30   ;12.5% duty, len counter no, env no, vol=0.
		.byte $10			   ;($8F9F)16 counts.
.byte MCTL_TEMPO,	 $6E   ;60/1.36=44 counts per second.
		.byte MCTL_JUMP		 ;($8FA2)Jump to new music address.
.word SQ1EndGame2		   ;($902F).
		.byte MCTL_JUMP		 ;($8FA5)Jump to new music address.
.word SQ1EndGame3		   ;($9072).
		.byte MCTL_JUMP		 ;($8FA8)Jump to new music address.
.word SQ1EndGame2		   ;($902F).
		.byte MCTL_JUMP		 ;($8FAB)Jump to new music address.
.word SQ1EndGame3		   ;($9072).
		.byte MCTL_JUMP		 ;($8FAE)Jump to new music address.
.word SQ1EndGame2		   ;($902F).
		.byte $A8, $A9, $AB	 ;($8FB1)E5,  F5,  G5.
		.byte $24			   ;($8FB4)36 counts.
.byte $A8, $A5, $A6, $A8	;E5,  C#5, D5,  E5.
.byte $A9				   ;F5.
		.byte $0C			   ;($8FBA)12 counts.
.byte $AB				   ;G5.
		.byte $0C			   ;($8FBC)12 counts.
		.byte $AD			   ;($8FBD)A5.
.byte $0C				   ;12 counts.
		.byte $AB, $A9		  ;($8FBF)G5,  F5.
.byte MCTL_CNTRL0,	$49   ;25% duty, len counter yes, env yes, vol=9.
		.byte $A8, $9C		  ;($8FC3)E5,  E4.
		.byte MCTL_TEMPO,	 $71;($8FC5)60/1.33=45 counts per second.
.byte $9C, $A1			  ;E4,  A4.
		.byte MCTL_TEMPO,	 $74;($8FC9)60/1.29=47 counts per second.
		.byte $A1, $A4		  ;($8FCB)A4,  C5.
.byte MCTL_TEMPO,	 $77   ;60/1.26=48 counts per second.
		.byte $A8, $AD		  ;($8FCF)E5,  A5.
		.byte MCTL_TEMPO,	 $79;($8FD1)60/1.24=48 counts per second.
.byte $A6, $9D			  ;D5,  F4.
		.byte MCTL_TEMPO,	 $7C;($8FD5)60/1.21=50 counts per second.
		.byte $9D, $9F		  ;($8FD7)F4,  G4.
		.byte MCTL_TEMPO,	 $7F;($8FD9)60/1.18=51 counts per second.
		.byte $9F, $A3		  ;($8FDB)G4,  B4.
.byte MCTL_TEMPO,	 $82   ;60/1.15=52 counts per second.
		.byte $A6, $AB		  ;($8FDF)D5,  G5.
		.byte MCTL_END_SPACE	;($8FE1)Disable counts between notes.
		.byte MCTL_TEMPO,	 $78;($8FE2)60/1.25=48 counts per second.
.byte $B0, $18			  ;C6, 24 counts.
		.byte $A4, $08		  ;($8FE6)C5,  8 counts.
.byte $A4, $08			  ;C5,  8 counts.
		.byte $A4, $08		  ;($8FEA)C5,  8 counts.
		.byte $A4, $18		  ;($8FEC)C5, 24 counts.
		.byte $A6, $18		  ;($8FEE)D5, 24 counts.
		.byte MCTL_TEMPO,	 $64;($8FF0)60/1.5=40 counts per second.
.byte MCTL_CNTRL0,	$7E   ;25% duty, len counter no, env no, vol=14.
		.byte MCTL_ADD_SPACE, $03;($8FF4)3 counts between notes.
		.byte MCTL_JUMP		 ;($8FF6)Jump to new music address.
		.word SQ1EndGame4	   ;($8FF7)($901D).
.byte MCTL_JUMP			 ;Jump to new music address.
		.word SQ1EndGame4	   ;($8FFA)($901D).
.byte MCTL_JUMP			 ;Jump to new music address.
		.word SQ1EndGame4	   ;($8FFD)($901D).
		.byte MCTL_JUMP		 ;($8FFF)Jump to new music address.
.word SQ1EndGame4		   ;($901D).
		.byte MCTL_TEMPO,	 $69;($9002)60/1.43=42 counts per second.
		.byte MCTL_JUMP		 ;($9004)Jump to new music address.
		.word SQ1EndGame5	   ;($9005)($9026).
.byte MCTL_JUMP			 ;Jump to new music address.
		.word SQ1EndGame5	   ;($9008)($9026).
		.byte MCTL_JUMP		 ;($900A)Jump to new music address.
		.word SQ1EndGame5	   ;($900B)($9026).
		.byte MCTL_JUMP		 ;($900D)Jump to new music address.
.word SQ1EndGame5		   ;($9026).
		.byte MCTL_TEMPO,	 $66;($9010)60/1.47=41 counts per second.
		.byte MCTL_CNTRL0,	$49;($9012)25% duty, len counter yes, env yes, vol=9.
		.byte MCTL_ADD_SPACE, $08;($9014)8 counts between notes.
		.byte $A8			   ;($9016)E5.
		.byte $10			   ;($9017)16 counts.
		.byte $98, $98, $98, $98;($9018)C4,  C4,  C4,  C4.
.byte $00				   ;End music.

SQ1EndGame4:
		.byte $A4, $A0, $A4, $A0;($901D)C5,  Ab4, C5,  Ab4.
		.byte $A4, $A0, $A4, $A0;($9021)C5,  Ab4, C5,  Ab4.
		.byte MCTL_RETURN	   ;($9025)Return to previous music block.

SQ1EndGame5:
		.byte $A8, $A4, $A8, $A4;($9026)E5,  C5,  E5,  C5.
.byte $A8, $A4, $A8, $A4	;E5,  C5,  E5,  C5.
		.byte MCTL_RETURN	   ;($902E)Return to previous music block.

SQ1EndGame2:
		.byte MCTL_END_SPACE	;($902F)Disable counts between notes.
		.byte MCTL_CNTRL0,	$8F;($9030)50% duty, len counter yes, env yes, vol=15.
		.byte $9F, $18		  ;($9032)G4,  24 counts.
		.byte $A8, $14		  ;($9034)E5,  20 counts.
		.byte $A8, $02		  ;($9036)E5,   2 counts.
.byte $A7, $02			  ;D#5,  2 counts.
		.byte $A8, $0C		  ;($903A)E5,  12 counts.
		.byte $AB, $0C		  ;($903C)G5,  12 counts.
		.byte $A6, $14		  ;($903E)D5,  20 counts.
		.byte $A6, $02		  ;($9040)D5,   2 counts.
		.byte $A5, $02		  ;($9042)C#5,  2 counts.
		.byte MCTL_ADD_SPACE, $0C;($9044)12 counts between notes.
.byte $A6, $AB, $A4		 ;D5,  G5,  C5.
		.byte $30			   ;($9049)48 counts.
		.byte $A4, $A6, $A8, $A9;($904A)C5,  D5,  E5,  F5.
		.byte $0C			   ;($904E)12 counts.
		.byte $AB, $A9, $A8	 ;($904F)G5,  F5,  E5.
		.byte $0C			   ;($9052)12 counts.
.byte $A9, $A8, $A6		 ;F5,  E5,  D5.
		.byte $30			   ;($9056)48 counts.
		.byte $A6, $A8, $A9, $AB;($9057)D5,  E5,  F5,  G5.
.byte $24				   ;36 counts.
		.byte $A8, $A5, $A6, $A8;($905C)E5,  C#5, D5,  E5.
		.byte $A9			   ;($9060)F5.
		.byte $0C			   ;($9061)12 counts.
.byte $AB				   ;G5.
.byte $0C				   ;12 counts.
		.byte $AD			   ;($9064)A5.
		.byte $0C			   ;($9065)12 counts.
		.byte $AB, $A9, $A8	 ;($9066)G5,  F5,  E5.
.byte $18				   ;24 counts.
		.byte $A8, $A4		  ;($906A)E5,  C5.
		.byte $0C			   ;($906C)12 counts.
		.byte $A1			   ;($906D)A4.
.byte $0C				   ;12 counts.
		.byte $A6			   ;($906F)D5.
.byte $3C				   ;60 counts.
		.byte MCTL_RETURN	   ;($9071)Return to previous music block.

SQ1EndGame3:
		.byte MCTL_CNTRL0,	$BF;($9072)50% duty, len counter no, env no, vol=15.
		.byte $AB			   ;($9074)G5.
		.byte $0C			   ;($9075)12 counts.
		.byte $AC			   ;($9076)Ab5.
.byte $30				   ;48 counts.
		.byte $A6, $A7, $A9, $AE;($9078)D5,  D#5, F5,  A#5.
		.byte $24			   ;($907C)36 counts.
		.byte $AB			   ;($907D)G5.
.byte $0C				   ;12 counts.
		.byte $A7			   ;($907F)D#5.
		.byte $0C			   ;($9080)12 counts.
		.byte $A9			   ;($9081)F5.
		.byte $30			   ;($9082)48 counts.
		.byte $AC, $AB, $A9	 ;($9083)Ab5, G5,  F5.
		.byte MCTL_CNTRL0,	$8F;($9086)50% duty, len counter yes, env yes, vol=15.
		.byte $A7			   ;($9088)D#5.
		.byte $0C			   ;($9089)12 counts.
		.byte $A9			   ;($908A)F5.
		.byte $0C			   ;($908B)12 counts.
.byte $AB				   ;G5.
		.byte $0C			   ;($908D)12 counts.
.byte MCTL_CNTRL0,	$BF   ;50% duty, len counter no, env no, vol=15.
		.byte $AC, $AE, $B0	 ;($9090)Ab5, A#5, C6.
.byte $30				   ;48 counts.
		.byte $B3, $B2, $B0	 ;($9094)D#6, D6,  C6.
		.byte MCTL_CNTRL0,	$8E;($9097)50% duty, len counter yes, env yes, vol=14.
		.byte MCTL_ADD_SPACE, $10;($9099)16 counts between notes.
		.byte $AE, $AC, $AB, $AB;($909B)A#5, Ab5, G5,  G5.
		.byte $A9, $A7		  ;($909F)F5,  D#5.
		.byte MCTL_ADD_SPACE, $0C;($90A1)12 counts between notes.
		.byte MCTL_CNTRL0,	$BF;($90A3)50% duty, len counter no, env no, vol=15.
		.byte $A9			   ;($90A5)F5.
		.byte $30			   ;($90A6)48 counts.
		.byte $A4, $A6, $A7, $A7;($90A7)C5,  D5,  D#5, D#5.
		.byte $54			   ;($90AB)84 counts.
		.byte $A6			   ;($90AC)D5.
		.byte $30			   ;($90AD)48 counts.
.byte MCTL_CNTRL0,	$8F   ;50% duty, len counter yes, env yes, vol=15.
		.byte $0C			   ;($90B0)12 counts.
		.byte MCTL_RETURN	   ;($90B1)Return to previous music block.

;----------------------------------------------------------------------------------------------------

SQ2EndGame:
		.byte MCTL_CNTRL0,	$30;($90B2)12.5% duty, len counter no, env no, vol=0.
		.byte $30			   ;($90B4)48 counts.
		.byte MCTL_CNTRL0,	$46;($90B5)25% duty, len counter yes, env yes, vol=6.
		.byte $A3, $13		  ;($90B7)B4, 19 counts.
		.byte $A3, $05		  ;($90B9)B4,  5 counts.
		.byte MCTL_ADD_SPACE, $0C;($90BB)12 counts between notes.
		.byte $A3, $A9, $A9, $A9;($90BD)B4,  F5,  F5,  F5.
		.byte $A8, $A8, $A8, $A6;($90C1)E5,  E5,  E5,  D5.
		.byte $A4, $A3, $A1, $A3;($90C5)C5,  B4,  A4,  B4.
		.byte $A4, $A3, $A1, $9F;($90C9)C5,  B4,  A4,  G4.
		.byte $A1, $A3, $A4, $A3;($90CD)A4,  B4,  C5,  B4.
		.byte $A1, $9F, $A4, $A4;($90D1)A4,  G4,  C5,  C5.
		.byte $A4, $A7, $A7, $A7;($90D5)C5,  D#5, D#5, D#5.
		.byte $AA, $AA, $AA, $AD;($90D9)F#5, F#5, F#5, A5.
		.byte $AD, $AD		  ;($90DD)A5,  A5.
		.byte MCTL_CNTRL0,	$7F;($90DF)25% duty, len counter no, env no, vol=15.
		.byte $B0			   ;($90E1)C6.
		.byte $3C			   ;($90E2)60 counts.
		.byte $AF			   ;($90E3)B5.
		.byte $0C			   ;($90E4)12 counts.
		.byte MCTL_CNTRL0,	$30;($90E5)12.5% duty, len counter no, env no, vol=0.
		.byte $28			   ;($90E7)40 counts.
		.byte MCTL_JUMP		 ;($90E8)Jump to new music address.
.word SQ2EndGame2		   ;($9159).
		.byte MCTL_CNTRL0,	$8F;($90EB)50% duty, len counter yes, env yes, vol=15.
		.byte MCTL_JUMP		 ;($90ED)Jump to new music address.
		.word SQ2EndGame3	   ;($90EE)($91A0).
		.byte MCTL_JUMP		 ;($90F0)Jump to new music address.
		.word SQ2EndGame2	   ;($90F1)($9159).
		.byte MCTL_CNTRL0,	$4F;($90F3)25% duty, len counter yes, env yes, vol=15.
		.byte MCTL_JUMP		 ;($90F5)Jump to new music address.
		.word SQ2EndGame3	   ;($90F6)($91A0).
		.byte MCTL_JUMP		 ;($90F8)Jump to new music address.
.word SQ2EndGame2		   ;($9159).
		.byte $A4			   ;($90FB)C5.
		.byte $24			   ;($90FC)36 counts.
		.byte $9F			   ;($90FD)G4.
.byte $24				   ;36 counts.
		.byte $A1			   ;($90FF)A4.
		.byte $54			   ;($9100)84 counts.
		.byte MCTL_CNTRL0,	$49;($9101)25% duty, len counter yes, env yes, vol=9.
		.byte $A1, $95, $95, $9C;($9103)A4,  A3,  A3,  E4.
		.byte $9C, $A1, $A1, $A8;($9107)E4,  A4,  A4,  E5.
		.byte $9D, $97, $97, $9A;($910B)F4,  B3,  B3,  D4.
		.byte $9A, $9D, $A3, $A6;($910F)D4,  F4,  B4,  D5.
		.byte MCTL_END_SPACE	;($9113)Disable counts between notes.
		.byte $A8, $18		  ;($9114)E5,  24 counts.
		.byte $9B, $08		  ;($9116)D#4,  8 counts.
		.byte $9B, $08		  ;($9118)D#4,  8 counts.
		.byte $9B, $08		  ;($911A)D#4,  8 counts.
.byte $9B, $18			  ;D#4, 24 counts.
		.byte $9D, $18		  ;($911E)F4,  24 counts.
		.byte MCTL_CNTRL0,	$7E;($9120)25% duty, len counter no, env no, vol=14.
		.byte MCTL_ADD_SPACE, $03;($9122)3 counts between notes.
		.byte MCTL_JUMP		 ;($9124)Jump to new music address.
		.word SQ2EndGame4	   ;($9125)($9147).
		.byte MCTL_JUMP		 ;($9127)Jump to new music address.
		.word SQ2EndGame4	   ;($9128)($9147).
		.byte MCTL_JUMP		 ;($912A)Jump to new music address.
		.word SQ2EndGame4	   ;($912B)($9147).
		.byte MCTL_JUMP		 ;($912D)Jump to new music address.
		.word SQ2EndGame4	   ;($912E)($9147).
.byte MCTL_JUMP			 ;Jump to new music address.
		.word SQ2EndGame5	   ;($9131)($9150).
		.byte MCTL_JUMP		 ;($9133)Jump to new music address.
		.word SQ2EndGame5	   ;($9134)($9150).
		.byte MCTL_JUMP		 ;($9136)Jump to new music address.
		.word SQ2EndGame5	   ;($9137)($9150).
.byte MCTL_JUMP			 ;Jump to new music address.
.word SQ2EndGame5		   ;($9150).
		.byte MCTL_CNTRL0,	$49;($913C)25% duty, len counter yes, env yes, vol=9.
		.byte MCTL_ADD_SPACE, $08;($913E)8 counts between notes.
		.byte $9F			   ;($9140)G4.
		.byte $10			   ;($9141)16 counts.
		.byte $8C, $8C, $8C, $8C;($9142)C3,  C3,  C3,  C3.
		.byte $00			   ;($9146)End music.

SQ2EndGame4:
		.byte $9B, $98, $9B, $98;($9147)D#4, C4,  D#4, C4.
		.byte $9B, $98, $9B, $98;($914B)D#4, C4,  D#4, C4.
		.byte MCTL_RETURN	   ;($914F)Return to previous music block.

SQ2EndGame5:
		.byte $9F, $9C, $9F, $9C;($9150)G4,  E4,  G4,  E4.
		.byte $9F, $9C, $9F, $9C;($9154)G4,  E4,  G4,  E4.
.byte MCTL_RETURN		   ;Return to previous music block.

SQ2EndGame2:
		.byte MCTL_END_SPACE	;($9159)Disable counts between notes.
		.byte MCTL_CNTRL0,	$8F;($915A)50% duty, len counter yes, env yes, vol=15.
		.byte $9F, $14		  ;($915C)G4,  20 counts.
		.byte $9F, $02		  ;($915E)G4,   2 counts.
		.byte $9E, $02		  ;($9160)F#4,  2 counts.
.byte $9F, $06			  ;G4,   6 counts.
		.byte $9F, $06		  ;($9164)G4,   6 counts.
		.byte $9C, $06		  ;($9166)E4,   6 counts.
		.byte $9F, $06		  ;($9168)G4,   6 counts.
		.byte $9F, $1E		  ;($916A)G4,  30 counts.
.byte $9F, $06			  ;G4,   6 counts.
		.byte $9D, $06		  ;($916E)F4,   6 counts.
		.byte $9F, $06		  ;($9170)G4,   6 counts.
		.byte $9C, $14		  ;($9172)E4,  20 counts.
		.byte $9C, $02		  ;($9174)E4,   2 counts.
.byte $9B, $02			  ;D#4,  2 counts.
		.byte MCTL_ADD_SPACE, $0C;($9178)12 counts between notes.
		.byte $9C, $9F, $9D	 ;($917A)E4,  G4,  F4.
		.byte $24			   ;($917D)36 counts.
		.byte $A4			   ;($917E)C5.
		.byte $24			   ;($917F)36 counts.
.byte $A4				   ;C5.
		.byte $0C			   ;($9181)12 counts.
		.byte $A5			   ;($9182)C#5.
		.byte $18			   ;($9183)24 counts.
		.byte $A4, $A3, $A1, $A3;($9184)C5,  B4,  A4,  B4.
		.byte $24			   ;($9188)36 counts.
		.byte $A4			   ;($9189)C5.
.byte $24				   ;36 counts.
		.byte $9F			   ;($918B)G4.
		.byte $24			   ;($918C)36 counts.
		.byte $A1			   ;($918D)A4.
		.byte $54			   ;($918E)84 counts.
		.byte $A1, $9C, $98, $9C;($918F)A4,  E4,  C4,  E4.
		.byte $A1, $9C, $98, $9C;($9193)A4,  E4,  C4,  E4.
		.byte $0C			   ;($9197)12 counts.
		.byte $A4, $A1, $A4, $A3;($9198)C5,  A4,  C5,  B4.
		.byte MCTL_CNTRL0,	$89;($919C)50% duty, len counter yes, env yes, vol=9.
.byte $24				   ;36 counts.
		.byte MCTL_RETURN	   ;($919F)Return to previous music block.

SQ2EndGame3:
		.byte MCTL_ADD_SPACE, $06;($91A0)6 counts between notes.
		.byte $9B, $98, $9B, $98;($91A2)D#4, C4,  D#4, C4.
		.byte $9B, $98, $9B, $98;($91A6)D#4, C4,  D#4, C4.
		.byte $A0, $9D, $A0, $9D;($91AA)Ab4, F4,  Ab4, F4.
		.byte $A0, $9D, $9A, $9D;($91AE)Ab4, F4,  D4,  F4.
.byte $9F, $9A, $9F, $9A	;G4,  D4,  G4,  D4.
		.byte $9F, $9A, $9F, $9A;($91B6)G4,  D4,  G4,  D4.
		.byte $9B, $98, $9B, $98;($91BA)D#4, C4,  D#4, C4.
		.byte $9B, $98, $9B, $98;($91BE)D#4, C4,  D#4, C4.
		.byte $A4, $A1, $A4, $A1;($91C2)C5,  A4,  C5,  A4.
.byte $A4, $A1, $A4, $A1	;C5,  A4,  C5,  A4.
		.byte $A6, $A3, $A6, $A3;($91CA)D5,  B4,  D5,  B4.
		.byte $A6, $A3, $A6, $A3;($91CE)D5,  B4,  D5,  B4.
		.byte $A2, $9F, $A2, $9F;($91D2)A#4, G4,  A#4, G4.
		.byte $A2, $9D, $A2, $9D;($91D6)A#4, F4,  A#4, F4.
.byte $A2, $9F, $A2, $9F	;A#4, G4,  A#4, G4.
		.byte $A4, $A2, $A4, $A2;($91DE)C5,  A#4, C5,  A#4.
		.byte $9B, $A0, $A4, $A0;($91E2)D#4, Ab4, C5,  Ab4.
		.byte $9B, $A0, $A4, $A0;($91E6)D#4, Ab4, C5,  Ab4.
		.byte $9B, $A0, $A4, $A0;($91EA)D#4, Ab4, C5,  Ab4.
.byte $9D, $A2, $9B, $A0	;F4,  A#4, D#4, Ab4.
		.byte $9F, $9A, $96, $9A;($91F2)G4,  D4,  A#3, D4.
		.byte $9F, $9A, $96, $9A;($91F6)G4,  D4,  A#3, D4.
		.byte $9F, $9B, $98, $9B;($91FA)G4,  D#4, C4,  D#4.
		.byte $9F, $9B, $98, $9B;($91FE)G4,  D#4, C4,  D#4.
.byte $98, $95, $98, $9D	;C4,  A3,  C4,  F4.
		.byte $98, $95, $98, $9D;($9206)C4,  A3,  C4,  F4.
		.byte $98, $95, $98, $9D;($920A)C4,  A3,  C4,  F4.
		.byte $98, $95, $98, $9B;($920E)C4,  A3,  C4,  D#4.
		.byte $A3, $9F, $9D, $9F;($9212)B4,  G4,  F4,  G4.
.byte $A3, $9F, $9D, $9F	;B4,  G4,  F4,  G4.
		.byte $A3, $9F, $9D, $9F;($921A)B4,  G4,  F4,  G4.
		.byte $A3, $9F, $9D, $9F;($921E)B4,  G4,  F4,  G4.
		.byte MCTL_ADD_SPACE, $0C;($9222)12 counts between notes.
.byte $A4				   ;C5.
		.byte $0C			   ;($9225)12 counts.
		.byte $A3, $A1, $A3	 ;($9226)B4,  A4,  B4.
		.byte $0C			   ;($9229)12 counts.
.byte MCTL_CNTRL0,	$89   ;50% duty, len counter yes, env yes, vol=9.
		.byte $18			   ;($922C)24 counts.
		.byte MCTL_RETURN	   ;($922D)Return to previous music block.

;----------------------------------------------------------------------------------------------------

TRIEndGame:
		.byte MCTL_CNTRL0,	$00;($922E)12.5% duty, len counter yes, env yes, vol=0.
		.byte $30			   ;($9230)48 counts.
		.byte MCTL_CNTRL0,	$30;($9231)12.5% duty, len counter no, env no, vol=0.
		.byte $93, $6C		  ;($9233)G3, 108 counts.
		.byte MCTL_ADD_SPACE, $0C;($9235)12 counts between notes.
		.byte $93, $9A, $9F, $A4;($9237)G3,  D4,  G4,  C5.
		.byte $A6, $A9, $A6, $A4;($923B)D5,  F5,  D5,  C5.
		.byte $A3, $A4, $A6, $A9;($923F)B4,  C5,  D5,  F5.
.byte $A6, $A4, $A3, $A1	;D5,  C5,  B4,  A4.
		.byte $A1, $A1, $A4, $A4;($9247)A4,  A4,  C5,  C5.
		.byte $A4, $A7, $A7, $A7;($924B)C5,  D#5, D#5, D#5.
		.byte $AA, $AA, $AA, $93;($924F)F#5, F#5, F#5, G3.
		.byte $98, $9A, $9F, $A4;($9253)C4,  D4,  G4,  C5.
.byte $A6				   ;D5.
		.byte MCTL_CNTRL0,	$60;($9258)25% duty, len counter no, env yes, vol=0.
		.byte $AB			   ;($925A)G5.
		.byte $34			   ;($925B)52 counts.
.byte MCTL_NO_OP			;Skip byte.
		.byte MCTL_JUMP		 ;($925D)Jump to new music address.
.word TRIEndGame2		   ;($92BF).
		.byte MCTL_JUMP		 ;($9260)Jump to new music address.
		.word TRIEndGame3	   ;($9261)($92F2).
.byte MCTL_JUMP			 ;Jump to new music address.
		.word TRIEndGame2	   ;($9264)($92BF).
		.byte MCTL_JUMP		 ;($9266)Jump to new music address.
		.word TRIEndGame3	   ;($9267)($92F2).
		.byte MCTL_JUMP		 ;($9269)Jump to new music address.
.word TRIEndGame2		   ;($92BF).
		.byte MCTL_CNTRL0,	$FF;($926C)75% duty, len counter no, env no, vol=15.
		.byte $A8, $9C, $A1	 ;($926E)E5,  E4,  A4.
.byte MCTL_NO_OP			;Skip byte.
		.byte $95, $9A, $9C, $9D;($9272)A3,  D4,  E4,  F4.
		.byte MCTL_NO_OP		;($9276)Skip byte.
		.byte MCTL_CNTRL0,	$00;($9277)12.5% duty, len counter yes, env yes, vol=0.
		.byte $18			   ;($9279)24 counts.
		.byte MCTL_CNTRL0,	$30;($927A)12.5% duty, len counter no, env no, vol=0.
		.byte MCTL_ADD_SPACE, $0C;($927C)12 counts between notes.
		.byte $92, $9E, $9E, $A4;($927E)F#3, F#4, F#4, C5.
		.byte $A4			   ;($9282)C5.
		.byte MCTL_NO_OP		;($9283)Skip byte.
		.byte $A8, $9E, $B0, $93;($9284)E5,  F#4, C6,  G3.
		.byte $9F, $9F, $A3, $A3;($9288)G4,  G4,  B4,  B4.
		.byte MCTL_NO_OP		;($928C)Skip byte.
.byte $A6, $A9, $AF		 ;D5,  F5,  B5.
		.byte MCTL_END_SPACE	;($9290)Disable counts between notes.
		.byte $98, $18		  ;($9291)C4,  24 counts.
		.byte $A0, $08		  ;($9293)Ab4,  8 counts.
		.byte $A0, $08		  ;($9295)Ab4,  8 counts.
		.byte $A0, $08		  ;($9297)Ab4,  8 counts.
		.byte $A0, $18		  ;($9299)Ab4, 24 counts.
.byte MCTL_NO_OP			;Skip byte.
		.byte $A2, $18		  ;($929C)A#4, 24 counts.
		.byte MCTL_ADD_SPACE, $0C;($929E)12 counts between notes.
		.byte $A0, $94, $A0, $94;($92A0)Ab4, Ab3, Ab4, Ab3.
		.byte MCTL_NOTE_OFST, $02;($92A4)Note offset of 2 notes.
		.byte $A0			   ;($92A6)Ab4.
		.byte MCTL_NO_OP		;($92A7)Skip byte.
		.byte $94, $A0, $94	 ;($92A8)Ab3, Ab4, Ab3.
.byte MCTL_NOTE_OFST, $00   ;Note offset of 0 notes.
		.byte $98, $93, $98, $93;($92AD)C4,  G3,  C4,  G3.
		.byte $98, $93, $98	 ;($92B1)C4,  G3,  C4.
		.byte MCTL_NO_OP		;($92B4)Skip byte.
.byte $93				   ;G3.
		.byte MCTL_ADD_SPACE, $08;($92B6)8 counts between notes.
		.byte $98			   ;($92B8)C4.
		.byte $10			   ;($92B9)16 counts.
.byte $98, $98, $98, $98	;C4,  C4,  C4,  C4.
		.byte $00			   ;($92BE)End music.

TRIEndGame2:
.byte MCTL_CNTRL0,	$FF   ;75% duty, len counter no, env no, vol=15.
		.byte MCTL_ADD_SPACE, $18;($92C1)24 counts between notes.
		.byte $98, $A4, $A3	 ;($92C3)C4,  C5,  B4.
		.byte MCTL_NO_OP		;($92C6)Skip byte.
		.byte $97, $96, $A2, $A1;($92C7)B3,  A#3, A#4, A4.
		.byte MCTL_NO_OP		;($92CB)Skip byte.
		.byte $95, $94, $A0, $9F;($92CC)A3,  Ab3, Ab4, G4.
		.byte MCTL_NO_OP		;($92D0)Skip byte.
		.byte $93, $92, $9E, $9D;($92D1)G3,  F#3, F#4, F4.
		.byte MCTL_NO_OP		;($92D5)Skip byte.
		.byte $A9, $A8, $9C, $A1;($92D6)F5,  E5,  E4,  A4.
		.byte MCTL_NO_OP		;($92DA)Skip byte.
		.byte $95, $9A, $9C, $9D;($92DB)A3,  D4,  E4,  F4.
.byte MCTL_NO_OP			;Skip byte.
		.byte MCTL_CNTRL0,	$00;($92E0)12.5% duty, len counter yes, env yes, vol=0.
.byte $18				   ;24 counts.
		.byte MCTL_CNTRL0,	$FF;($92E3)75% duty, len counter no, env no, vol=15.
		.byte $9E, $92, $9E	 ;($92E5)F#4 F#3 F#4.
		.byte MCTL_NO_OP		;($92E8)Skip byte.
		.byte $18			   ;($92E9)24 counts.
		.byte $9F, $9A, $93	 ;($92EA)G4,  D4,  G3.
		.byte MCTL_NO_OP		;($92ED)Skip byte.
		.byte MCTL_CNTRL0,	$00;($92EE)12.5% duty, len counter yes, env yes, vol=0.
		.byte $18			   ;($92F0)24 counts.
.byte MCTL_RETURN		   ;Return to previous music block.

TRIEndGame3:
		.byte MCTL_ADD_SPACE, $0C;($92F2)12 counts between notes.
		.byte MCTL_CNTRL0,	$60;($92F4)25% duty, len counter no, env yes, vol=0.
.byte $9D				   ;F4.
		.byte $18			   ;($92F7)24 counts.
		.byte $9D			   ;($92F8)F4.
		.byte MCTL_CNTRL0,	$30;($92F9)12.5% duty, len counter no, env no, vol=0.
.byte $96				   ;A#3.
		.byte MCTL_NO_OP		;($92FC)Skip byte.
		.byte $96			   ;($92FD)A#3.
		.byte $0C			   ;($92FE)12 counts.
		.byte $96			   ;($92FF)A#3.
.byte MCTL_CNTRL0,	$60   ;25% duty, len counter no, env yes, vol=0.
		.byte $9B			   ;($9302)D#4.
		.byte $18			   ;($9303)24 counts.
		.byte $9B			   ;($9304)D#4.
.byte MCTL_CNTRL0,	$30   ;12.5% duty, len counter no, env no, vol=0.
		.byte $A0			   ;($9307)Ab4.
		.byte MCTL_NO_OP		;($9308)Skip byte.
		.byte $A0			   ;($9309)Ab4.
.byte $0C				   ;12 counts.
		.byte $94			   ;($930B)Ab3.
		.byte MCTL_CNTRL0,	$60;($930C)25% duty, len counter no, env yes, vol=0.
		.byte $9A			   ;($930E)D4.
.byte $18				   ;24 counts.
		.byte $9A			   ;($9310)D4.
.byte MCTL_CNTRL0,	$30   ;12.5% duty, len counter no, env no, vol=0.
		.byte $9F			   ;($9313)G4.
.byte MCTL_NO_OP			;Skip byte.
.byte $9F				   ;G4.
		.byte $0C			   ;($9316)12 counts.
		.byte $93, $98, $A4, $9A;($9317)G3,  C4,  C5,  D4.
		.byte $A6, $9B		  ;($931B)D5,  D#4.
		.byte MCTL_NO_OP		;($931D)Skip byte.
		.byte $A7, $9C, $A8	 ;($931E)D#5, E4,  E5.
		.byte MCTL_CNTRL0,	$60;($9321)25% duty, len counter no, env yes, vol=0.
		.byte $9D			   ;($9323)F4.
.byte $18				   ;24 counts.
.byte $9D				   ;F4.
		.byte MCTL_CNTRL0,	$30;($9326)12.5% duty, len counter no, env no, vol=0.
		.byte $A2			   ;($9328)A#4.
		.byte MCTL_NO_OP		;($9329)Skip byte.
		.byte $A2			   ;($932A)A#4.
		.byte $0C			   ;($932B)12 counts.
		.byte $96			   ;($932C)A#3.
		.byte MCTL_CNTRL0,	$60;($932D)25% duty, len counter no, env yes, vol=0.
		.byte $9B			   ;($932F)D#4.
		.byte $18			   ;($9330)24 counts.
		.byte $9B			   ;($9331)D#4.
.byte MCTL_CNTRL0,	$30   ;12.5% duty, len counter no, env no, vol=0.
.byte $A0				   ;Ab4.
.byte MCTL_NO_OP			;Skip byte.
.byte $A0				   ;Ab4.
		.byte $0C			   ;($9337)12 counts.
.byte $94				   ;Ab3.
		.byte MCTL_CNTRL0,	$60;($9339)25% duty, len counter no, env yes, vol=0.
		.byte $9A			   ;($933B)D4.
.byte $18				   ;24 counts.
		.byte MCTL_CNTRL0,	$30;($933D)12.5% duty, len counter no, env no, vol=0.
		.byte $9A			   ;($933F)D4.
.byte MCTL_ADD_SPACE, $18   ;24 counts between notes.
.byte MCTL_CNTRL0,	$FF   ;75% duty, len counter no, env no, vol=15.
.byte $9A				   ;D4.
.byte MCTL_NO_OP			;Skip byte.
.byte $9E, $9F			  ;F#4, G4.
.byte $18				   ;24 counts.
		.byte $9A			   ;($9349)D4.
.byte MCTL_NO_OP			;Skip byte.
		.byte $9F, $9F, $9A, $93;($934B)G4,  G4,  D4,  G3.
		.byte MCTL_NO_OP		;($934F)Skip byte.
.byte MCTL_CNTRL0,	$00   ;12.5% duty, len counter yes, env yes, vol=0.
.byte $18				   ;24 counts.
		.byte MCTL_RETURN	   ;($9353)Return to previous music block.

;-------------------------------------------[End Credits]--------------------------------------------

EndGameClearPPU:
LDA #%00000000		  ;Turn off sprites and background.
STA PPUControl1		 ;

		JSR ClearPPU			;($9359)($C17A)Clear the PPU.

LDA #%00011000		  ;
STA PPUControl1		 ;Turn on sprites and background.
		RTS					 ;($9361)

;----------------------------------------------------------------------------------------------------

ExitGame:
LDA #MSC_NOSOUND		;Silence music.
BRK					 ;
		.byte $04, $17		  ;($9365)($81A0)InitMusicSFX, bank 1.

		BRK					 ;($9367)Load palettes for end credits.
.byte $06, $07		  ;($AA62)LoadCreditsPals, bank 0.

LDA #$00				;
STA ExpLB			   ;
STA ScrollX			 ;Clear various RAM values.
STA ScrollY			 ;
STA ActiveNmTbl		 ;
STA NPCUpdateCounter	   ;

LDX #$3B				;Prepare to clear NPC position RAM.

* STA NPCXPos,X		   ;
DEX					 ;Clear NPC map position RAM (60 bytes).
		BPL -				   ;($937B)

		LDA #EN_DRAGONLORD2	 ;($937D)Set enemy number.
		STA EnemyNumber		 ;($937F)

		JSR ClearSpriteRAM	  ;($9381)($C6BB)Clear sprite RAM.
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.
		JSR EndGameClearPPU	 ;($9387)($9354)Clear the display contents of the PPU.

LDA #$FF				;Set hit points.
STA HitPoints		   ;

BRK					 ;Load BG and sprite palettes for selecting saved game.
		.byte $01, $07		  ;($938F)($AA7E)LoadStartPals, bank 0.

		JSR Dowindow			;($9391)($C6F0)display on-screen window.
.byte WINDOW_DIALOG		;Dialog window.

		JSR DoDialogHiBlock	 ;($9395)($C7C5)Please press reset, hold it in...
.byte $28			   ;TextBlock19, entry 8.
		RTS					 ;($9399)

;----------------------------------------------------------------------------------------------------

DoEndCredits:
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

		LDA #MSC_END			;($939D)End music.
		BRK					 ;($939F)
.byte $04, $17		  ;($81A0)InitMusicSFX, bank 1.

BRK					 ;Wait for the music clip to end.
		.byte $03, $17		  ;($93A3)($815E)WaitForMusicEnd, bank 1.

		BRK					 ;($93A5)Load palettes for end credits.
.byte $06, $07		  ;($AA62)LoadCreditsPals, bank 0.

JSR ClearSpriteRAM	  ;($C6BB)Clear sprites.

		LDA #%00000000		  ;($93AB)Turn off sprites and background.
		STA PPUControl1		 ;($93AD)

JSR Bank0ToCHR0		 ;($FCA3)Load data into CHR0.

		LDA #$00				;($93B3)
		STA ExpLB			   ;($93B5)
		STA ScrollX			 ;($93B7)
		STA ScrollY			 ;($93B9)Clear various RAM values.
		STA ActiveNmTbl		 ;($93BB)
		LDA #EN_DRAGONLORD2	 ;($93BD)
		STA EnemyNumber		 ;($93BF)

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.
JSR EndGameClearPPU	 ;($9354)Clear the display contents of the PPU.

		LDA #$23				;($93C7)
		STA PPUAddrUB		   ;($93C9)
		LDA #$C8				;($93CB)Set attribute table bytes for nametable 0.
		STA PPUAddrLB		   ;($93CD)
		LDA #$55				;($93CF)
		STA PPUDataByte		 ;($93D1)

		LDY #$08				;($93D3)Load 8 bytes of attribute table data.
		* JSR AddPPUBufferEntry ;($93D5)($C690)Add data to PPU buffer.
DEY					 ;Done loading attribute table bytes?
		BNE -				   ;($93D9)If not, branch to load more.

		LDA #$AA				;($93DB)Load different attribute table data.
		STA PPUDataByte		 ;($93DD)

		LDY #$20				;($93DF)Fill the remainder of the attribute table with the data.
		* JSR AddPPUBufferEntry ;($93E1)($C690)Add data to PPU buffer.
DEY					 ;Done loading attribute table bytes?
		BNE -				   ;($93E5)If not, branch to load more.

		JSR WaitForNMI		  ;($93E7)($FF74)Wait for VBlank interrupt.

LDA EndCreditsDataPointer	 ;
		STA DatPntr1LB		  ;($93ED)Get pointer to end credits data.
		LDA EndCreditsDataPointer+1;($93EF)
STA DatPntrlUB		  ;

JMP RollCredits		 ;($93FA)Display credits on the screen.

DoClearPPU:
		JSR EndGameClearPPU	 ;($93F7)($9354)Clear the display contents of the PPU.

RollCredits:
LDY #$00				;
LDA (DatPntr1),Y		;First 2 bytes of data block are the PPU address.
STA PPUAddrLB		   ;Load those bytes into the PPU data buffer as the
INY					 ;target address for the data write.
		LDA (DatPntr1),Y		;($9401)
		STA PPUAddrUB		   ;($9403)

		LDY #$02				;($9405)Move to data after PPU address.

GetNextEndByte:
		LDA (DatPntr1),Y		;($9407)
		STA PPUDataByte		 ;($9409)Is the byte a repeat control byte?
		CMP #END_RPT			;($940B)
		BNE DoNonRepeatedValue  ;($940D)If not, branch to check for other byte types.

		INY					 ;($940F)
LDA (DatPntr1),Y		;Get next byte. It is the number of times to repeat.
STA GenByte3C		   ;
INY					 ;
		LDA (DatPntr1),Y		;($9415)Get next byte. It is the byte to repeatedly load.
		STA PPUDataByte		 ;($9417)Store byte in PPU buffer.

		* JSR AddPPUBufferEntry ;($9419)($C690)Add data to PPU buffer.
DEC GenByte3C		   ;More data to load?
BNE -				   ;If so, branch to load next byte.

INY					 ;Increment data index.
		BNE GetNextEndByte	  ;($9421)Get next data byte.

DoNonRepeatedValue:
		CMP #END_TXT_END		;($9423)
		BEQ FinishEndDataBlock  ;($9425)Has an end of data block byte been found?
		CMP #END_RPT_END		;($9427)If so, display credits and move to next data block.
		BEQ FinishEndDataBlock  ;($9429)

		JSR AddPPUBufferEntry   ;($942B)($C690)Add data to PPU buffer.

INY					 ;Increment data index.
		BNE GetNextEndByte	  ;($942F)Get next data byte.

FinishEndDataBlock:
		INY					 ;($9431)Increment data index and prepare to add
TYA					 ;it to the data pointer.

		CLC					 ;($9433)
ADC DatPntr1LB		  ;Move pointer to start of next block of credits.
STA DatPntr1LB		  ;
BCC +				   ;Does upper byte of pointer need to be incremented?
INC DatPntrlUB		  ;If not, branch to skip.

* LDA PPUDataByte		 ;Has the end of this segment been found?
CMP #END_TXT_END		;If so, branch to get next segment.
BEQ RollCredits		 ;($93FA)Loop to keep rolling credits.

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

		BRK					 ;($9445)Fade in credits.
.byte $07, $07		  ;($AA3D)DoPalFadeIn, bank 0.

LDA EndCreditCount	  ;Get the number of credit screens that have been shown.
BNE CheckCredits1	   ;Is this the first one? If not, branch.

LDY #$08				;First credit screen.  Wait for 8 music timing events.
BNE WaitForMusTmng	  ;Branch always.

CheckCredits1:
CMP #$01				;Is this the second credit screen?
BNE CheckCredits2	   ;If not, branch.

LDY #$02				;Second credit screen.  Wait for 2 music timing events.
BNE WaitForMusTmng	  ;Branch always.

CheckCredits2:
CMP #$02				;Is this the third credit screen?
BEQ CheckCreditEnd	  ;if so, branch to wait for 3 music timing events.

CMP #$03				;Is this the fourth credit screen?
BEQ CheckCreditEnd	  ;if so, branch to wait for 3 music timing events.

CMP #$04				;Is this the fifth credit screen?
BEQ CheckCreditEnd	  ;if so, branch to wait for 3 music timing events.

CMP #$0D				;Is this the 14th or less credit screen?
BEQ MusicTiming2		;
BCC MusicTiming2		;if so, branch to wait for 2 music timing events.

CheckCreditEnd:
CMP #$12				;Have all 18 screens of credits been shown?
BCC MusicTiming3		;If not, branch to do more.

LDY #$A0				;Wait 160 frames.
* JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.
		DEY					 ;($9473)Done waiting 160 frames?
BNE -				   ;If not, branch to wait more.
RTS					 ;

MusicTiming3:
		LDY #$03				;($9477)Wait for 3 music timing events.
		BNE WaitForMusTmng	  ;($9479)Branch always.

MusicTiming2:
		LDY #$02				;($947B)Wait for 2 music timing events.

WaitForMusTmng:
		* BRK				   ;($947D)Wait for timing queue in music.
.byte $03, $17		  ;($815E)WaitForMusicEnd, bank 1.

DEY					 ;Is it time to move to the next set of credits?
BNE -				   ;If not, branch to wait more.
		INC EndCreditCount	  ;($9483)Increment credit screen counter.

		BRK					 ;($9485)Fade out credits.
.byte $08, $07		  ;($AA43)DoPalFadeOut, bank 0.

JMP DoClearPPU		  ;($93F7)Prepare to load next screen of credits.

;----------------------------------------------------------------------------------------------------

EndCreditsDataPointer:
		.word EndCreditDat	  ;($948B)($948D)Start of data below.

;----------------------------------------------------------------------------------------------------

EndCreditDat:
		.word $20E8			 ;($948D)PPU address.
;			  C	O	N	G	R	A	T	U	L	A	T	I	O	N	S	_
		.byte $26, $32, $31, $2A, $35, $24, $37, $38, $2F, $24, $37, $2C, $32, $31, $36, $60;($948F)
;			 END
		.byte $FC			   ;($949F)

;----------------------------------------------------------------------------------------------------

.word $2147			 ;PPU address.
;			  T	H	O	U	_	H	A	S	T	_	R	E	S	T	O	R
.byte $37, $2B, $32, $38, $5F, $2B, $24, $36, $37, $5F, $35, $28, $36, $37, $32, $35
;			  E	D   END
.byte $28, $27, $FC

;----------------------------------------------------------------------------------------------------

		.word $2186			 ;($94B5)PPU address.
;			  P	E	A	C	E	_	U	N	T	O	_	T	H	E	_	W
		.byte $33, $28, $24, $26, $28, $5F, $38, $31, $37, $32, $5F, $37, $2B, $28, $5F, $3A;($94B7)
;			  O	R	L	D	_   END
		.byte $32, $35, $2F, $27, $60, $FC;($94C7)

;----------------------------------------------------------------------------------------------------

		.word $21E4			 ;($94CD)PPU address.
;			  B	U	T	_	T	H	E	R	E	_	A	R	E	_	M	A
		.byte $25, $38, $37, $5F, $37, $2B, $28, $35, $28, $5F, $24, $35, $28, $5F, $30, $24;($94CF)
;			  N	Y	_	R	O	A	D	S   END
		.byte $31, $3C, $5F, $35, $32, $24, $27, $36, $FC;($94DF)

;----------------------------------------------------------------------------------------------------

.word $2229			 ;PPU address.
;			  Y	E	T	_	T	O	_	T	R	A	V	E	L	.   END
.byte $3C, $28, $37, $5F, $37, $32, $5F, $37, $35, $24, $39, $28, $2F, $61, $FC

;----------------------------------------------------------------------------------------------------

		.word $2289			 ;($94F9)PPU address.
;			  M	A	Y	_	T	H	E	_	L	I	G	H	T   END
		.byte $30, $24, $3C, $5F, $37, $2B, $28, $5F, $2F, $2C, $2A, $2B, $37, $FC;($94FB)

;----------------------------------------------------------------------------------------------------

		.word $22C8			 ;($9509)PPU address.
;			  S	H	I	N	E	_	U	P	O	N	_	T	H	E	E	.
		.byte $36, $2B, $2C, $31, $28, $5F, $38, $33, $32, $31, $5F, $37, $2B, $28, $28, $61;($950B)
;			 END
		.byte $FD			   ;($951B)

;----------------------------------------------------------------------------------------------------

.word $2188			 ;PPU address.
;			  D	R	A	G	O	N	_	W	A	R	R	I	O	R   END
.byte $27, $35, $24, $2A, $32, $31, $5F, $3A, $24, $35, $35, $2C, $32, $35, $FC

;----------------------------------------------------------------------------------------------------

		.word $21ED			 ;($952D)PPU address.
;			  S	T	A	F	F   END
		.byte $36, $37, $24, $29, $29, $FC;($952F)

;----------------------------------------------------------------------------------------------------

		.word $23C0			 ;($9535)PPU address.
;1 row of attribute table data.
		.byte $F7, $20, $FF, $FD;($9537)

;----------------------------------------------------------------------------------------------------

		.word $2186			 ;($953B)PPU address.
;			  S	C	E	N	A	R	I	O	_	W	R	I	T	T	E	N
		.byte $36, $26, $28, $31, $24, $35, $2C, $32, $5F, $3A, $35, $2C, $37, $37, $28, $31;($953D)
;			  _	B	Y   END
		.byte $5F, $25, $3C, $FC;($954D)

;----------------------------------------------------------------------------------------------------

		.word $21EB			 ;($9551)PPU address.
;			  Y	U	J	I	_	H	O	R	I	I   END
		.byte $3C, $38, $2D, $2C, $5F, $2B, $32, $35, $2C, $2C, $FC;($9553)

;----------------------------------------------------------------------------------------------------

.word $23C0			 ;PPU address.
;1 row of attribute table data.
.byte $F7, $20, $05, $FD

;----------------------------------------------------------------------------------------------------

.word $2185			 ;PPU address.
;			  C	H	A	R	A	C	T	E	 R   _	D	E	S	I	G	N
.byte $26, $2B, $24, $35, $24, $26, $37, $28, $35, $5F, $27, $28, $36, $2C, $2A, $31
;			  E	D	_	B	Y   END
.byte $28, $27, $5F, $25, $3C, $FC

;----------------------------------------------------------------------------------------------------

.word $21E9			 ;PPU address.
;			  A	K	I	R	A	_	T	O	R	I	Y	A	M	A   END
.byte $24, $2E, $2C, $35, $24, $5F, $37, $32, $35, $2C, $3C, $24, $30, $24, $FC

;----------------------------------------------------------------------------------------------------

		.word $23C0			 ;($958D)PPU address.
;1 row of attribute table data.
		.byte $F7, $20, $0A, $FD;($958F)

;----------------------------------------------------------------------------------------------------

		.word $2187			 ;($9593)PPU address.
;			  M	U	S	I	C	_	C	O	M	P	O	S	E	D	_	B
		.byte $30, $38, $36, $2C, $26, $5F, $26, $32, $30, $33, $32, $36, $28, $27, $5F, $25;($9595)
;			  Y   END
		.byte $3C, $FC		  ;($95A5)

;----------------------------------------------------------------------------------------------------

		.word $21E8			 ;($95A7)PPU address
;			  K	O	I	C	H	I	_	S	U	G	I	Y	A	M	A   END
		.byte $2E, $32, $2C, $26, $2B, $2C, $5F, $36, $38, $2A, $2C, $3C, $24, $30, $24, $FC;($95A9)

;----------------------------------------------------------------------------------------------------

		.word $23C0			 ;($95B9)PPU address.
;1 row of attribute table data.
		.byte $F7, $20, $0F, $FD;($95BB)

;----------------------------------------------------------------------------------------------------

		.word $212A			 ;($95BF)PPU address.
;			  P	R	O	G	R	A	M	E	D	_	B	Y   END
		.byte $33, $35, $32, $2A, $35, $24, $30, $28, $27, $5F, $25, $3C, $FC;($95C1)

;----------------------------------------------------------------------------------------------------

.word $21A8			 ;PPU address.
;			  K	O	I	C	H	I	_	N	A	K	A	M	U	R	A   END
.byte $2E, $32, $2C, $26, $2B, $2C, $5F, $31, $24, $2E, $24, $30, $38, $35, $24, $FC

;----------------------------------------------------------------------------------------------------

.word $220A			 ;PPU address.
;			  K	O	J	I	_	Y	O	S	H	I	D	A   END
.byte $2E, $32, $2D, $2C, $5F, $3C, $32, $36, $2B, $2C, $27, $24, $FC

;----------------------------------------------------------------------------------------------------

		.word $2267			 ;($95EF)PPU address.
;			  T	A	K	E	N	O	R	I	_	Y	A	M	A	M	O	R
		.byte $37, $24, $2E, $28, $31, $32, $35, $2C, $5F, $3C, $24, $30, $24, $30, $32, $35;($95F1)
;			  I   END
		.byte $2C, $FC		  ;($9601)

;----------------------------------------------------------------------------------------------------

		.word $23D0			 ;($9603)PPU address.
;Attribute table data.
		.byte $F7, $08, $05, $F7, $10, $00, $FD;($9605)

;----------------------------------------------------------------------------------------------------

.word $2189			 ;PPU address.
;			  C	G	_	D	E	S	I	G	N	E	D	_	B	Y   END
.byte $26, $2A, $5F, $27, $28, $36, $2C, $2A, $31, $28, $27, $5F, $25, $3C, $FC

;----------------------------------------------------------------------------------------------------

		.word $21E9			 ;($961D)PPU address.
;			  T	A	K	A	S	H	I	_	Y	A	S	U	N	O   END
		.byte $37, $24, $2E, $24, $36, $2B, $2C, $5F, $3C, $24, $36, $38, $31, $32, $FC;($961F)

;----------------------------------------------------------------------------------------------------

.word $23D8			 ;PPU address.
;Attribute table data.
.byte $F7, $08, $0A, $FD

;----------------------------------------------------------------------------------------------------

.word $2186			 ;PPU address.
;			  S	C	E	N	A	R	I	O	_	A	S	S	I	S	T	E
.byte $36, $26, $28, $31, $24, $35, $2C, $32, $5F, $24, $36, $36, $2C, $36, $37, $28
;			  D	_	B	Y   END
.byte $27, $5F, $25, $3C, $FC

;----------------------------------------------------------------------------------------------------

		.word $21E8			 ;($964B)PPU address.
;			  H	I	R	O	S	H	I	_	M	I	Y	A	O	K	A   END
		.byte $2B, $2C, $35, $32, $36, $2B, $2C, $5F, $30, $2C, $3C, $24, $32, $2E, $24, $FC;($964D)

;----------------------------------------------------------------------------------------------------

		.word $23C0			 ;($965D)PPU address.
;Attribute table data.
		.byte $F7, $20, $0F, $FD;($965F)

;----------------------------------------------------------------------------------------------------

		.word $214A			 ;($9663)PPU address.
;			  A	S	S	I	S	T	E	D	_	B	Y   END
		.byte $24, $36, $36, $2C, $36, $37, $28, $27, $5F, $25, $3C, $FC;($9665)

;----------------------------------------------------------------------------------------------------

		.word $21CA			 ;($9671)PPU address.
;			  R	I	K	A	_	S	U	Z	U	K	I   END
		.byte $35, $2C, $2E, $24, $5F, $36, $38, $3D, $38, $2E, $2C, $FC;($9673)

;----------------------------------------------------------------------------------------------------

		.word $2228			 ;($967F)PPU address.
;			  T	A	D	A	S	H	I	_	F	U	K	U	Z	A	W	A
		.byte $37, $24, $27, $24, $36, $2B, $2C, $5F, $29, $38, $2E, $38, $3D, $24, $3A, $24;($9681)
;			 END
		.byte $FC			   ;($9691)

;----------------------------------------------------------------------------------------------------

.word $23D0			 ;PPU address.
;Attribute table data.
.byte $F7, $08, $50, $F7, $10, $00, $FD

;----------------------------------------------------------------------------------------------------

		.word $2187			 ;($969B)PPU address.
;			  S	P	E	C	I	A	L	_	T	H	A	N	K	S	_	T
		.byte $36, $33, $28, $26, $2C, $24, $2F, $5F, $37, $2B, $24, $31, $2E, $36, $5F, $37;($969D)
;			  O   END
		.byte $32, $FC		  ;($96AD)

;----------------------------------------------------------------------------------------------------

		.word $21E7			 ;($96AF)PPU address.
;			  K	A	Z	U	H	I	K	O	_	T	O	R	I	S	H	I
		.byte $2E, $24, $3D, $38, $2B, $2C, $2E, $32, $5F, $37, $32, $35, $2C, $36, $2B, $2C;($96B1)
;			  M	A   END
		.byte $30, $24, $FC	 ;($96C1)

;----------------------------------------------------------------------------------------------------

.word $23C0			 ;PPU address.
;1 row of attribute table data.
.byte $F7, $20, $05, $FD

;----------------------------------------------------------------------------------------------------

.word $218A			 ;PPU address.
;			  T	R	A	N	S	L	A	T	I	O	N   END
.byte $37, $35, $24, $31, $36, $2F, $24, $37, $2C, $32, $31, $FC

;----------------------------------------------------------------------------------------------------

.word $21ED			 ;PPU address.
;			  S	T	A	F	F   END
.byte $36, $37, $24, $29, $29, $FC

;----------------------------------------------------------------------------------------------------

.word $23C0			 ;PPU address.
;1 row of attribute table data.
.byte $F7, $20, $FF, $FD

;----------------------------------------------------------------------------------------------------

.word $20C6			 ;PPU address.
;T	R	A	N	S	L	A	T	E	D	_	B	Y   END
.byte $37, $35, $24, $31, $36, $2F, $24, $37, $28, $27, $5F, $25, $3C, $FC

;----------------------------------------------------------------------------------------------------

.word $2108			 ;PPU address.
;			  T	O	S	H	I	K	O	_	W	A	T	S	O	N   END
.byte $37, $32, $36, $2B, $2C, $2E, $32, $5F, $3A, $24, $37, $36, $32, $31, $FC

;----------------------------------------------------------------------------------------------------

		.word $2186			 ;($9707)PPU address.
;			  R	E	V	I	S	E	D	_	T	E	X	T	_	B	Y   END
		.byte $35, $28, $39, $2C, $36, $28, $27, $5F, $37, $28, $3B, $37, $5F, $25, $3C, $FC;($9709)

;----------------------------------------------------------------------------------------------------

		.word $21C8			 ;($9719)PPU address.
;			  S	C	O	T	T	_	P	E	L	L	A	N	D   END
		.byte $36, $26, $32, $37, $37, $5F, $33, $28, $2F, $2F, $24, $31, $27, $FC;($971B)

;----------------------------------------------------------------------------------------------------

		.word $2246			 ;($9729)PPU address.
;			  T	E	C	H	N	I	C	A	L	_	S	U	P	P	O	R
		.byte $37, $28, $26, $2B, $31, $2C, $26, $24, $2F, $5F, $36, $38, $33, $33, $32, $35;($972B)
;			  T	_	B	Y   END
		.byte $37, $5F, $25, $3C, $FC;($973B)

;----------------------------------------------------------------------------------------------------

.word $2288			 ;PPU address.
;			  D	O	U	G	_	B	A	K	E	R   END
.byte $27, $32, $38, $2A, $5F, $25, $24, $2E, $28, $35, $FC

;----------------------------------------------------------------------------------------------------

		.word $23C0			 ;($974D)PPU address.
;Attribute table data.
		.byte $F7, $10, $FF, $F7, $08, $00, $F7, $08, $0F, $F7, $10, $F0, $FD;($974F)

;----------------------------------------------------------------------------------------------------

.word $2148			 ;PPU address.
;			  P	R	O	G	R	A	M	E	D	_	B	Y   END
.byte $33, $35, $32, $2A, $35, $24, $30, $28, $27, $5F, $25, $3C, $FC

;----------------------------------------------------------------------------------------------------

		.word $21CA			 ;($976B)PPU address.
;			  K	E	N	I	C	H	I	_	M	A	S	U	T	A   END
.byte $2E, $28, $31, $2C, $26, $2B, $2C, $5F, $30, $24, $36, $38, $37, $24, $FC

;----------------------------------------------------------------------------------------------------

.word $222A			 ;PPU address.
;			  M	A	N	A	B	U	_	Y	A	M	A	N	A   END
		.byte $30, $24, $31, $24, $25, $38, $5F, $3C, $24, $30, $24, $31, $24, $FC;($977E)

;----------------------------------------------------------------------------------------------------

.word $23D0			 ;PPU address.
;Attribute table data.
		.byte $F7, $08, $50, $F7, $10, $00, $FD;($978E)

;----------------------------------------------------------------------------------------------------

.word $2125			 ;PPU address.
;			  C	G	_	D	E	S	I	G	N	E	D	_	B	Y   END
.byte $26, $2A, $5F, $27, $28, $36, $2C, $2A, $31, $28, $27, $5F, $25, $3C, $FC

;----------------------------------------------------------------------------------------------------

.word $218A			 ;PPU address.
;			  S	A	T	O	S	H	I	_	F	U	D	A	B	A   END
		.byte $36, $24, $37, $32, $36, $2B, $2C, $5F, $29, $38, $27, $24, $25, $24, $FC;($97A8)

;----------------------------------------------------------------------------------------------------

.word $2205			 ;PPU address.
;			  S	P	E	C	I	A	L	_	T	H	A	N	K	S	_	T
		.byte $36, $33, $28, $26, $2C, $24, $2F, $5F, $37, $2B, $24, $31, $2E, $36, $5F, $37;($97B9)
;			  O   END
		.byte $32, $FC		  ;($97C9)
;----------------------------------------------------------------------------------------------------

		.word $226A			 ;($97CB)PPU address.
;			  H	O	W	A	R	D	_	P	H	I	L	L	I	P	S   END
.byte $2B, $32, $3A, $24, $35, $27, $5F, $33, $2B, $2C, $2F, $2F, $2C, $33, $36, $FC

;----------------------------------------------------------------------------------------------------

.word $23D0			 ;PPU address.
;Attribute table data.
		.byte $F7, $08, $0A, $F7, $08, $00, $F7, $08, $0F, $FD;($97DF)

;----------------------------------------------------------------------------------------------------

.word $218A			 ;PPU address.
;			  D	I	R	E	C	T	E	D	_	B	Y   END
.byte $27, $2C, $35, $28, $26, $37, $28, $27, $5F, $25, $3C, $FC

;----------------------------------------------------------------------------------------------------

		.word $21E8			 ;($97F7)PPU address.
;			  K	O	I	C	H	I	_	N	A	K	A	M	U	R	A   END
.byte $2E, $32, $2C, $26, $2B, $2C, $5F, $31, $24, $2E, $24, $30, $38, $35, $24, $FC

;----------------------------------------------------------------------------------------------------

		.word $23C0			 ;($9809)PPU address.
;1 row of attribute table data.
.byte $F7, $20, $0A, $FD

;----------------------------------------------------------------------------------------------------

		.word $218A			 ;($980F)PPU address.
;			  P	R	O	D	U	C	E	D	_	B	Y   END
.byte $33, $35, $32, $27, $38, $26, $28, $27, $5F, $25, $3C, $FC

;----------------------------------------------------------------------------------------------------

		.word $21E9			 ;($981D)PPU address.
;			  Y	U	K	I	N	O	B	U	_	C	H	I	D	A   END
		.byte $3C, $38, $2E, $2C, $31, $32, $25, $38, $5F, $26, $2B, $2C, $27, $24, $FC;($981F)
;----------------------------------------------------------------------------------------------------

.word $23C0			 ;PPU address.
;1 row of attribute table data.
.byte $F7, $20, $0F, $FD

;----------------------------------------------------------------------------------------------------

		.word $2085			 ;($9834)PPU address.
;			  B	A	S	E	D	_	O	N	_	D	R	A	G	O	N	_
.byte $25, $24, $36, $28, $27, $5F, $32, $31, $5F, $27, $35, $24, $2A, $32, $31, $5F
;			  Q	U	E	S	T   END
.byte $34, $38, $28, $36, $37, $FC

;----------------------------------------------------------------------------------------------------

.word $210B			 ;PPU address.
;			  C	O	P	Y	R	I	G	H	T   END
.byte $26, $32, $33, $3C, $35, $2C, $2A, $2B, $37, $FC

;----------------------------------------------------------------------------------------------------

		.word $2163			 ;($9858)PPU address.
;			  A	R	M	O	R	_	P	R	O	J	E	C	T   END
		.byte $24, $35, $30, $32, $35, $5F, $33, $35, $32, $2D, $28, $26, $37, $FC;($985A)

;----------------------------------------------------------------------------------------------------

.word $2174			 ;PPU address.
;			  1	9	8	6	_	1	9	8	9   END
		.byte $01, $09, $08, $06, $5F, $01, $09, $08, $09, $FC;($986A)

;----------------------------------------------------------------------------------------------------

.word $21C3			 ;PPU address.
;			  B	I	R	D	_	S	T	U	D	I	O   END
		.byte $25, $2C, $35, $27, $5F, $36, $37, $38, $27, $2C, $32, $FC;($9876)

;----------------------------------------------------------------------------------------------------

		.word $21D4			 ;($9882)PPU address.
;			  1	9	8	6	_	1	9	8	9   END
.byte $01, $09, $08, $06, $5F, $01, $09, $08, $09, $FC

;----------------------------------------------------------------------------------------------------

		.word $2223			 ;($988E)PPU address.
;			  K	O	I	C	H	I	_	S	U	G	I	Y	A	M	A   END
.byte $2E, $32, $2C, $26, $2B, $2C, $5F, $36, $38, $2A, $2C, $3C, $24, $30, $24, $FC

;----------------------------------------------------------------------------------------------------

.word $2234			 ;PPU address.
;			  1	9	8	6	_	1	9	8	9   END
		.byte $01, $09, $08, $06, $5F, $01, $09, $08, $09, $FC;($98A2)

;----------------------------------------------------------------------------------------------------

.word $2283			 ;PPU address.
;							CHUN  _	S	O	F	T   END
		.byte $0C, $0D, $0E, $0F, $5F, $36, $32, $29, $37, $FC;($98AE)

;----------------------------------------------------------------------------------------------------

		.word $2294			 ;($98B8)PPU address.
;			  1	9	8	6	_	1	9	8	9   END
		.byte $01, $09, $08, $06, $5F, $01, $09, $08, $09, $FC;($98BA)

;----------------------------------------------------------------------------------------------------

		.word $2309			 ;($98C4)PPU address.
;			  E	N	I	X   END
		.byte $28, $31, $2C, $3B, $FC;($98C6)

;----------------------------------------------------------------------------------------------------

.word $2310			 ;PPU address.
;			  1	9	8	6	_	1	9	8	9   END
		.byte $01, $09, $08, $06, $5F, $01, $09, $08, $09, $FC;($98CD)

;----------------------------------------------------------------------------------------------------

		.word $23C8			 ;($98D7)PPU address.
;Attribute table data.
		.byte $F7, $03, $FF, $07, $F7, $06, $05, $F7, $03, $0F, $F7, $03, $AA, $F7, $05, $00;($98D9)
		.byte $F7, $05, $AA, $FC;($98E9)

;----------------------------------------------------------------------------------------------------

		.word $23E0			 ;($98ED)PPU address.
;Attribute table data.
		.byte $F7, $05, $00, $F7, $03, $AA, $04, $F7, $04, $00, $F7, $03, $AA, $F7, $04, $00;($98EF)
		.byte $F7, $03, $AA, $FD;($98FF)

;----------------------------------------------------------------------------------------------------

		.word $218F			 ;($9903)PPU address.
;Enix "e" Top row.
.byte $10, $11, $12, $FC

;----------------------------------------------------------------------------------------------------

		.word $21AE			 ;($9909)PPU address.
;Enix "e" second row.
		.byte $13, $14, $15, $16, $FC;($990B)

;----------------------------------------------------------------------------------------------------

.word $21CE			 ;PPU address.
;Enix "e" third row.
		.byte $17, $18, $19, $1A, $FC;($9912)

;----------------------------------------------------------------------------------------------------

		.word $21EE			 ;($9917)PPU address.
;Enix "e" bottom row.
		.byte $1B, $1C, $1D, $1E, $FC;($9919)

;----------------------------------------------------------------------------------------------------

		.word $220E			 ;($991E)PPU address.
;"ENIX" text.
		.byte $1F, $20, $21, $22, $FC;($9920)

;----------------------------------------------------------------------------------------------------

.word $23D8			 ;PPU address.
;Half a row of blank tiles.
		.byte $F7, $10, $FF, $FD;($9927)

;----------------------------------------------------------------------------------------------------

		.word $21AA			 ;($992B)PPU address.
;"THE END" top row.
		.byte $3E, $3F, $40, $41, $42, $43, $44, $45, $46, $47, $48, $49, $FC;($992D)

;----------------------------------------------------------------------------------------------------

.word $21CA			 ;PPU address.
;"THE END" bottom row.
.byte $4A, $4B, $4C, $4D, $4E, $4F, $50, $51, $52, $53, $54, $55, $FC

;----------------------------------------------------------------------------------------------------

		.word $23D0			 ;($9949)PPU address.
;1 row of blank tiles.
		.byte $F7, $20, $00, $FD;($994B)

;----------------------------------------------------------------------------------------------------

CopyTreasureTable:
		PHA					 ;($994F)
		TXA					 ;($9950)Save A and X.
		PHA					 ;($9951)

		LDX #$7B				;($9952)Prepare to copy 124 bytes.

		* LDA TreasureTable,X   ;($9954)Copy treasure table into RAM starting at $0320.
		STA BlockRAM+$20,X	  ;($9957)
DEX					 ;Have 124 bytes been copied?
		BPL -				   ;($995B)If not, branch to copy more.

		PLA					 ;($995D)
		TAX					 ;($995E)Restore X and A.
		PLA					 ;($995F)
		RTS					 ;($9960)

;----------------------------------------------------------------------------------------------------

LoadEnemyStats:
		PHA					 ;($9961)
		TYA					 ;($9962)Store A and Y.
		PHA					 ;($9963)

		LDY #$0F				;($9964)16 bytes per enemy in EnemyStatsTable.
		LDA EnDatPtrLB		  ;($9966)
		CLC					 ;($9968)
		ADC EnemyStatsTablePointer;($9969)Add enemy data offset to the table pointer.
		STA GenPtr3CLB		  ;($996C)
		LDA EnDatPtrUB		  ;($996E)
		ADC EnemyStatsTablePointer+1;($9970)Save a copy of the pointer in a general use pointer.
		STA GenPtr3CUB		  ;($9973)

		* LDA (GenPtr3C),Y	  ;($9975)Use the general pointer to load the enemy data.
		STA EnBaseAtt,Y		 ;($9977)
DEY					 ;
		BPL -				   ;($997B)More data to load? If so, branch to load more.

		PLA					 ;($997D)
		TAY					 ;($997E)Restore A and Y and return.
		PLA					 ;($997F)
		RTS					 ;($9980)

;----------------------------------------------------------------------------------------------------

CopyROMToRAM:
		PHA					 ;($9981)
		TYA					 ;($9982)Save A and Y.
		PHA					 ;($9983)

		LDY #$00				;($9984)
LDA CopyCounterLB	   ;Is copy counter = 0?
		ORA CopyCounterUB	   ;($9988)If so, branch.  Nothing to copy.
BEQ CopyROMDone		 ;

CopyROMLoop:
LDA (ROMSourcePtr),Y	   ;Get byte from ROM and put it into RAM.
STA (RAMTrgtPtr),Y	  ;

LDA CopyCounterLB	   ;
		SEC					 ;($9992)
		SBC #$01				;($9993)
		STA CopyCounterLB	   ;($9995)Decrement copy counter.
LDA CopyCounterUB	   ;
		SBC #$00				;($9999)
		STA CopyCounterUB	   ;($999B)

		ORA CopyCounterLB	   ;($999D)Is copy counter = 0?
		BEQ CopyROMDone		 ;($999F)If so, branch.  Done copying.

		INC ROMSourcePtrLB	  ;($99A1)
		BNE +				   ;($99A3)Increment ROM source pointer.
		INC ROMSourcePtrUB	  ;($99A5)

		* INC RAMTrgtPtrLB	  ;($99A7)
		BNE +				   ;($99A9)Increment RAM target pointer.
		INC RAMTrgtPtrUB		;($99AB)

* JMP CopyROMLoop		 ;($998C)Loop to copy more data.

CopyROMDone:
		PLA					 ;($99B0)
		TAY					 ;($99B1)Restore Y and A and return.
PLA					 ;
		RTS					 ;($99B3)

;----------------------------------------------------------------------------------------------------

SetBaseStats:
		TYA					 ;($99B4)Save Y on the stack.
PHA					 ;

		LDA BaseStatsTable-2	;($99B6)
		STA PlayerDatPtrLB	  ;($99B9)Load base address for the BaseStatsTable.
		LDA BaseStatsTable-1	;($99BB)
		STA PlayerDatPtrUB	  ;($99BE)
		LDY LevelDataPointer	;($99C0)Load offset for player's level in the table.

		LDA (PlayerDatPtr),Y	;($99C2)
		STA DisplayedStrength   ;($99C4)Load player's base strength.
		INY					 ;($99C6)

		LDA (PlayerDatPtr),Y	;($99C7)
STA DisplayedAgility		;Load player's base agility.
		INY					 ;($99CB)

LDA (PlayerDatPtr),Y	;
		STA DisplayedMaxHP	  ;($99CE)Load player's base max HP.
INY					 ;

LDA (PlayerDatPtr),Y	;
STA DisplayedMaxMP	  ;Load player's base MP.
INY					 ;

LDA (PlayerDatPtr),Y	;
ORA ModsnSpells		 ;Load player's healmore/hurtmore spells.
STA ModsnSpells		 ;
INY					 ;

LDA (PlayerDatPtr),Y	;Load player's other spells.
STA SpellFlags		  ;

PLA					 ;
TAY					 ;Restore Y and return.
RTS					 ;

;----------------------------------------------------------------------------------------------------

;The following table contains the pointers to the enemy sprites.  The MSB for the pointer is not
;set for some entries.  The enemies that have the MSB set in the table below are mirrored from left
;to right on the display.  For example, the knight and armored knight have the same foot forward
;while the axe knight has the opposite foot forward.  This is because the axe knight is mirrored
;while the other two are not. The code that accesses the table sets the MSB when it accesses it.

EnemySpritesPointerTable:
.word SlimeSprts -$8000 ;($1B0E)Slime.
.word SlimeSprts -$8000 ;($1B0E)Red slime.
.word DrakeeSprts-$8000 ;($1AC4)Drakee.
.word GhstSprts  -$8000 ;($1BAA)Ghost.
.word MagSprts   -$8000 ;($1B30)Magician.
.word DrakeeSprts-$8000 ;($1AC4)Magidrakee.
.word ScorpSprts -$8000 ;($1CD1)Scorpion.
.word DruinSprts -$8000 ;($1AE0)Druin.
.word GhstSprts  -$8000 ;($1BAA)Poltergeist.
.word DrollSprts -$8000 ;($1A87)Droll.
.word DrakeeSprts-$8000 ;($1AC4)Drakeema.
.word SkelSprts		 ;($9A3E)Skeleton.
.word WizSprts   -$8000 ;($1B24)Warlock.
.word ScorpSprts		;($9CD1)Metal scorpion.
.word WolfSprts  -$8000 ;($1C15)Wolf.
.word SkelSprts  -$8000 ;($1A3E)Wraith.
.word SlimeSprts -$8000 ;($1B0E)Metal slime.
.word GhstSprts		 ;($9BAA)Specter.
.word WolfSprts		 ;($9C15)Wolflord.
.word DruinSprts		;($9AE0)Druinlord.
.word DrollSprts -$8000 ;($1A87)Drollmagi.
.word WyvrnSprts -$8000 ;($1BD5)Wyvern.
.word ScorpSprts -$8000 ;($1CD1)Rouge scorpion.
.word DKnightSprts	  ;($9A32)Wraith knight.
.word GolemSprts		;($9C70)Golem.
.word GolemSprts -$8000 ;($1C70)Goldman.
.word KntSprts   -$8000 ;($1D20)Knight.
.word WyvrnSprts		;($9BD5)Magiwyvern.
.word DKnightSprts	  ;($9A32)Demon knight.
.word WolfSprts  -$8000 ;($1C15)Werewolf.
.word DgnSprts   -$8000 ;($1D81)Green dragon.
.word WyvrnSprts -$8000 ;($1BD5)Starwyvern.
.word WizSprts		  ;($9B24)Wizard.
.word AxKntSprts		;($9D0E)Axe knight.
.word RBDgnSprts -$8000 ;($1D7B)Blue dragon.
.word GolemSprts -$8000 ;($1C70)Stoneman.
.word ArKntSprts -$8000 ;($1D02)Armored knight.
.word RBDgnSprts -$8000 ;($1D7B)Red dragon.
		.word DgLdSprts  -$8000 ;($9A30)($1B67)Dragonlord, initial form.

;----------------------------------------------------------------------------------------------------

;The following tables contain the sprite information for the enemies in the game(except the end
;boss). Each sprite is represented by 3 bytes.  The format for the bytes is as follows:

;TTTTTTTT VHYYYYYY XXXXXXPP

;TTTTTTTT-Tile pattern number for sprite.
;YYYYYY-Y position of sprite.
;XXXXXX-X position of sprite.
;V-Vertical mirroring bit.
;H-Horizontal mirroring bit.
;PP-Palette number.

DKnightSprts:
		.byte $30, $2A, $9F	 ;($9A32)
		.byte $2F, $27, $7F	 ;($9A35)Wraith knight and demon knight sword sprites.
		.byte $2F, $23, $5F	 ;($9A38)
.byte $2E, $1F, $3F	 ;

SkelSprts:
		.byte $20, $17, $70	 ;($9A3E)
		.byte $21, $1F, $70	 ;($9A41)
		.byte $23, $1E, $3B	 ;($9A44)
		.byte $26, $26, $3A	 ;($9A47)
		.byte $22, $1E, $59	 ;($9A4A)
		.byte $27, $26, $61	 ;($9A4D)
		.byte $28, $2E, $61	 ;($9A50)
		.byte $29, $33, $55	 ;($9A53)
.byte $2A, $37, $56
		.byte $22, $5E, $89	 ;($9A59)
		.byte $23, $5E, $AB	 ;($9A5C)
		.byte $27, $66, $81	 ;($9A5F)
.byte $28, $6E, $81
		.byte $24, $26, $A6	 ;($9A65)
		.byte $25, $2D, $A6	 ;($9A68)
		.byte $2B, $33, $9D	 ;($9A6B)
		.byte $2C, $3B, $8E	 ;($9A6E)
		.byte $2D, $3B, $AE	 ;($9A71)
.byte $FE, $3B, $4A
		.byte $FF, $3B, $6A	 ;($9A77)
		.byte $FE, $7B, $8A	 ;($9A7A)
		.byte $FE, $7D, $AA	 ;($9A7D)
		.byte $FE, $3F, $86	 ;($9A80)
		.byte $FE, $7F, $A6	 ;($9A83)
		.byte $00			   ;($9A86)

DrollSprts:
		.byte $31, $59, $62	 ;($9A87)
		.byte $32, $61, $63	 ;($9A8A)
		.byte $33, $69, $62	 ;($9A8D)
		.byte $34, $71, $61	 ;($9A90)
		.byte $35, $77, $60	 ;($9A93)
		.byte $31, $19, $82	 ;($9A96)
		.byte $32, $21, $83	 ;($9A99)
		.byte $33, $29, $82	 ;($9A9C)
		.byte $34, $31, $81	 ;($9A9F)
		.byte $35, $37, $80	 ;($9AA2)
		.byte $36, $5E, $40	 ;($9AA5)
.byte $38, $66, $42
		.byte $39, $6E, $43	 ;($9AAB)
		.byte $3A, $76, $40	 ;($9AAE)
		.byte $36, $1E, $A0	 ;($9AB1)
		.byte $38, $26, $A2	 ;($9AB4)
		.byte $39, $2E, $A3	 ;($9AB7)
		.byte $3A, $36, $A0	 ;($9ABA)
		.byte $E6, $22, $5A	 ;($9ABD)
		.byte $E6, $62, $8A	 ;($9AC0)
		.byte $00			   ;($9AC3)

DrakeeSprts:
		.byte $3B, $1F, $50	 ;($9AC4)
.byte $3C, $27, $50
		.byte $3D, $1F, $70	 ;($9ACA)
		.byte $3E, $27, $70	 ;($9ACD)
		.byte $3B, $5F, $90	 ;($9AD0)
.byte $3C, $67, $90
		.byte $3F, $2C, $7C	 ;($9AD6)
		.byte $FE, $39, $62	 ;($9AD9)
		.byte $FE, $79, $82	 ;($9ADC)
		.byte $00			   ;($9ADF)

DruinSprts:
.byte $42, $1C, $40
		.byte $45, $24, $40	 ;($9AE3)
		.byte $4A, $29, $41	 ;($9AE6)
		.byte $4D, $31, $41	 ;($9AE9)
		.byte $43, $1C, $60	 ;($9AEC)
		.byte $46, $24, $60	 ;($9AEF)
.byte $4B, $29, $61
		.byte $4E, $31, $61	 ;($9AF5)
		.byte $40, $18, $6C	 ;($9AF8)
		.byte $41, $18, $8C	 ;($9AFB)
		.byte $44, $1C, $80	 ;($9AFE)
		.byte $47, $24, $82	 ;($9B01)
		.byte $4C, $2A, $81	 ;($9B04)
		.byte $48, $24, $A1	 ;($9B07)
		.byte $49, $28, $C1	 ;($9B0A)
		.byte $00			   ;($9B0D)

SlimeSprts:
		.byte $55, $32, $64	 ;($9B0E)
		.byte $53, $2B, $60	 ;($9B11)
		.byte $54, $33, $60	 ;($9B14)
		.byte $53, $6B, $7C	 ;($9B17)
		.byte $54, $73, $7C	 ;($9B1A)
		.byte $FF, $35, $72	 ;($9B1D)
		.byte $FE, $F6, $92	 ;($9B20)
		.byte $00			   ;($9B23)

WizSprts:
		.byte $5C, $19, $96	 ;($9B24)
.byte $5D, $20, $96	 ;Wizard and warlock staff sprites.
		.byte $5D, $2E, $9A	 ;($9B2A)
		.byte $5D, $35, $9E	 ;($9B2D)

MagSprts:
		.byte $5A, $1B, $61	 ;($9B30)
.byte $5B, $23, $61
		.byte $5A, $5B, $81	 ;($9B36)
		.byte $5B, $63, $81	 ;($9B39)
		.byte $56, $24, $30	 ;($9B3C)
.byte $57, $23, $50
		.byte $58, $2B, $50	 ;($9B42)
		.byte $59, $33, $50	 ;($9B45)
		.byte $5F, $23, $90	 ;($9B48)
.byte $60, $2B, $90
		.byte $61, $33, $90	 ;($9B4E)
		.byte $5E, $33, $70	 ;($9B51)
		.byte $5E, $2C, $70	 ;($9B54)
.byte $FF, $A7, $73
		.byte $FE, $37, $48	 ;($9B5A)
		.byte $FF, $37, $68	 ;($9B5D)
		.byte $FF, $77, $88	 ;($9B60)
.byte $FE, $77, $A8
		.byte $00			   ;($9B66)

DgLdSprts:
		.byte $62, $1E, $9F	 ;($9B67)
		.byte $63, $26, $9F	 ;($9B6A)
		.byte $63, $74, $9B	 ;($9B6D)
		.byte $5D, $3B, $95	 ;($9B70)
		.byte $67, $1C, $62	 ;($9B73)
		.byte $68, $23, $61	 ;($9B76)
		.byte $69, $23, $5A	 ;($9B79)
		.byte $6A, $2B, $63	 ;($9B7C)
		.byte $67, $5C, $82	 ;($9B7F)
		.byte $68, $63, $81	 ;($9B82)
		.byte $69, $63, $8A	 ;($9B85)
.byte $6A, $6B, $83
		.byte $64, $29, $50	 ;($9B8B)
		.byte $65, $31, $50	 ;($9B8E)
		.byte $66, $39, $50	 ;($9B91)
		.byte $5F, $29, $90	 ;($9B94)
		.byte $60, $31, $90	 ;($9B97)
		.byte $61, $39, $90	 ;($9B9A)
		.byte $5E, $39, $70	 ;($9B9D)
		.byte $5E, $32, $70	 ;($9BA0)
		.byte $5E, $2B, $80	 ;($9BA3)
		.byte $5E, $2B, $70	 ;($9BA6)
		.byte $00			   ;($9BA9)

GhstSprts:
		.byte $70, $27, $52	 ;($9BAA)
		.byte $73, $2F, $52	 ;($9BAD)
		.byte $71, $27, $72	 ;($9BB0)
		.byte $74, $2F, $73	 ;($9BB3)
		.byte $72, $27, $91	 ;($9BB6)
		.byte $75, $2F, $92	 ;($9BB9)
		.byte $6D, $21, $50	 ;($9BBC)
		.byte $6E, $21, $70	 ;($9BBF)
		.byte $6F, $21, $90	 ;($9BC2)
		.byte $6B, $19, $70	 ;($9BC5)
.byte $6C, $19, $90
		.byte $FE, $3C, $55	 ;($9BCB)
		.byte $FF, $3C, $6D	 ;($9BCE)
		.byte $FE, $7C, $8D	 ;($9BD1)
		.byte $00			   ;($9BD4)

WyvrnSprts:
		.byte $83, $1A, $4F	 ;($9BD5)
		.byte $81, $15, $60	 ;($9BD8)
.byte $82, $1D, $60
		.byte $7F, $18, $42	 ;($9BDE)
		.byte $80, $20, $41	 ;($9BE1)
		.byte $7C, $12, $9C	 ;($9BE4)
.byte $7A, $1A, $80
		.byte $7B, $22, $80	 ;($9BEA)
		.byte $7D, $1A, $A0	 ;($9BED)
		.byte $7E, $22, $A0	 ;($9BF0)
.byte $76, $2D, $2C
.byte $77, $2D, $4C
		.byte $78, $2D, $6C	 ;($9BF9)
		.byte $79, $25, $60	 ;($9BFC)
.byte $6B, $25, $70
		.byte $55, $1F, $39	 ;($9C02)
		.byte $55, $21, $61	 ;($9C05)
		.byte $63, $A1, $45	 ;($9C08)
.byte $FE, $3D, $3E
		.byte $FF, $3D, $5E	 ;($9C0E)
		.byte $FE, $7D, $7E	 ;($9C11)
		.byte $00			   ;($9C14)

WolfSprts:
		.byte $2A, $37, $56	 ;($9C15)
		.byte $8D, $21, $98	 ;($9C18)
		.byte $8E, $29, $90	 ;($9C1B)
		.byte $84, $1A, $81	 ;($9C1E)
		.byte $85, $22, $81	 ;($9C21)
		.byte $86, $2A, $80	 ;($9C24)
		.byte $87, $31, $83	 ;($9C27)
		.byte $88, $21, $A0	 ;($9C2A)
		.byte $8F, $29, $A0	 ;($9C2D)
.byte $8A, $31, $A3
		.byte $8B, $22, $C0	 ;($9C33)
		.byte $8C, $2A, $C0	 ;($9C36)
		.byte $2C, $39, $8E	 ;($9C39)
		.byte $2D, $39, $AE	 ;($9C3C)
		.byte $84, $5A, $61	 ;($9C3F)
		.byte $85, $62, $61	 ;($9C42)
		.byte $86, $6A, $60	 ;($9C45)
		.byte $87, $71, $63	 ;($9C48)
		.byte $88, $61, $40	 ;($9C4B)
		.byte $89, $69, $40	 ;($9C4E)
		.byte $90, $71, $43	 ;($9C51)
		.byte $8B, $62, $20	 ;($9C54)
		.byte $8C, $6A, $20	 ;($9C57)
		.byte $FF, $2A, $72	 ;($9C5A)
		.byte $91, $1D, $A8	 ;($9C5D)
.byte $FE, $39, $40
		.byte $FF, $39, $60	 ;($9C63)
		.byte $FF, $7A, $80	 ;($9C66)
		.byte $FE, $3D, $88	 ;($9C69)
		.byte $FE, $7D, $A8	 ;($9C6C)
		.byte $00			   ;($9C6F)

GolemSprts:
.byte $0E, $1C, $24
		.byte $B6, $24, $24	 ;($9C73)
		.byte $BD, $3C, $24	 ;($9C76)
		.byte $BB, $34, $38	 ;($9C79)
		.byte $B7, $14, $44	 ;($9C7C)
		.byte $B8, $1C, $44	 ;($9C7F)
		.byte $B9, $24, $44	 ;($9C82)
		.byte $BA, $2C, $44	 ;($9C85)
.byte $BE, $3C, $44
		.byte $BC, $34, $58	 ;($9C8B)
		.byte $C1, $1C, $64	 ;($9C8E)
		.byte $C2, $24, $64	 ;($9C91)
		.byte $C3, $2C, $64	 ;($9C94)
		.byte $BF, $3C, $64	 ;($9C97)
		.byte $C0, $14, $6C	 ;($9C9A)
.byte $C4, $18, $84
		.byte $C5, $20, $84	 ;($9CA0)
		.byte $C6, $28, $84	 ;($9CA3)
		.byte $C7, $30, $84	 ;($9CA6)
		.byte $CF, $38, $88	 ;($9CA9)
		.byte $C8, $18, $A4	 ;($9CAC)
		.byte $C9, $20, $A4	 ;($9CAF)
		.byte $CA, $28, $A4	 ;($9CB2)
		.byte $CB, $30, $A4	 ;($9CB5)
.byte $D0, $38, $A8
		.byte $CC, $20, $C4	 ;($9CBB)
		.byte $CD, $28, $C4	 ;($9CBE)
		.byte $CE, $30, $C4	 ;($9CC1)
		.byte $58, $96, $64	 ;($9CC4)
.byte $FF, $B8, $78
		.byte $FE, $3C, $94	 ;($9CCA)
		.byte $FE, $7C, $B4	 ;($9CCD)
		.byte $00			   ;($9CD0)

ScorpSprts:
		.byte $D4, $38, $38	 ;($9CD1)
		.byte $D5, $32, $50	 ;($9CD4)
		.byte $D6, $2F, $70	 ;($9CD7)
		.byte $D7, $37, $70	 ;($9CDA)
		.byte $D8, $3F, $8C	 ;($9CDD)
		.byte $D9, $2F, $90	 ;($9CE0)
.byte $DA, $37, $90
		.byte $DB, $2F, $B0	 ;($9CE6)
		.byte $DC, $37, $B0	 ;($9CE9)
		.byte $D3, $27, $A8	 ;($9CEC)
		.byte $D2, $23, $9C	 ;($9CEF)
.byte $D1, $23, $7C
		.byte $3F, $63, $74	 ;($9CF5)
		.byte $FF, $32, $71	 ;($9CF8)
		.byte $FE, $37, $54	 ;($9CFB)
		.byte $FE, $73, $C0	 ;($9CFE)
		.byte $00			   ;($9D01)

ArKntSprts:
		.byte $F6, $19, $C6	 ;($9D02)
		.byte $F7, $21, $C6	 ;($9D05)Armored knight shield sprites.
		.byte $F8, $29, $C6	 ;($9D08)
		.byte $F9, $31, $C6	 ;($9D0B)

AxKntSprts:
		.byte $FA, $11, $1E	 ;($9D0E)
		.byte $FB, $19, $1E	 ;($9D11)
		.byte $FC, $15, $3E	 ;($9D14)Axe knight and armored knight sprites.
		.byte $FD, $20, $2E	 ;($9D17)
		.byte $5D, $18, $32	 ;($9D1A)
		.byte $B5, $2E, $26	 ;($9D1D)

KntSprts:
		.byte $B3, $31, $6E	 ;($9D20)
		.byte $B4, $31, $8E	 ;($9D23)
		.byte $37, $17, $6B	 ;($9D26)
.byte $9C, $19, $8B
		.byte $9F, $1F, $54	 ;($9D2C)
.byte $9D, $1F, $74
		.byte $9E, $1F, $94	 ;($9D32)
		.byte $A0, $1F, $B4	 ;($9D35)
		.byte $A1, $27, $29	 ;($9D38)
		.byte $A2, $27, $48	 ;($9D3B)
		.byte $A3, $27, $68	 ;($9D3E)
		.byte $A4, $27, $88	 ;($9D41)
		.byte $A5, $27, $A8	 ;($9D44)
		.byte $A7, $29, $B5	 ;($9D47)
		.byte $A8, $2F, $5C	 ;($9D4A)
		.byte $A9, $2F, $7C	 ;($9D4D)
		.byte $AA, $2F, $9C	 ;($9D50)
.byte $AB, $33, $3C
.byte $AD, $37, $5C
.byte $AE, $37, $7C
.byte $AF, $37, $9C
		.byte $B1, $37, $BC	 ;($9D5F)
		.byte $AC, $3B, $41	 ;($9D62)
		.byte $B0, $3F, $9C	 ;($9D65)
		.byte $B2, $3F, $BD	 ;($9D68)
		.byte $B2, $3A, $4D	 ;($9D6B)
		.byte $A6, $27, $C8	 ;($9D6E)
		.byte $FE, $7F, $CC	 ;($9D71)
		.byte $FE, $3D, $5C	 ;($9D74)
		.byte $FF, $3D, $7C	 ;($9D77)
.byte $00

RBDgnSprts:
		.byte $F3, $3F, $B6	 ;($9D7B)Red dragon and blue dragon fireball sprites.
.byte $F4, $3F, $D6	 ;

DgnSprts:
.byte $E6, $34, $00
		.byte $EC, $3C, $0C	 ;($9D84)
		.byte $E2, $2C, $20	 ;($9D87)
		.byte $E7, $34, $20	 ;($9D8A)
		.byte $ED, $3C, $2C	 ;($9D8D)
		.byte $DD, $1C, $39	 ;($9D90)
		.byte $DE, $24, $39	 ;($9D93)
		.byte $E3, $2C, $43	 ;($9D96)
		.byte $E8, $34, $40	 ;($9D99)
		.byte $DF, $24, $5B	 ;($9D9C)
		.byte $F0, $36, $5D	 ;($9D9F)
.byte $E4, $2C, $63
		.byte $E9, $34, $60	 ;($9DA5)
		.byte $EE, $3C, $6C	 ;($9DA8)
		.byte $E0, $24, $79	 ;($9DAB)
		.byte $E5, $2C, $80	 ;($9DAE)
.byte $EA, $34, $80
		.byte $F1, $30, $8E	 ;($9DB4)
		.byte $EF, $3C, $8C	 ;($9DB7)
		.byte $F2, $3A, $92	 ;($9DBA)
.byte $E1, $23, $99
		.byte $EB, $34, $A0	 ;($9DC0)
		.byte $F5, $24, $29	 ;($9DC3)
.byte $F5, $BC, $4C
		.byte $FE, $EB, $94	 ;($9DC9)
		.byte $00			   ;($9DCC)

;----------------------------------------------------------------------------------------------------

;The following table contains all the treasure chest contents in the game. Each entry is
;4 bytes.  The first byte is the map number.  The second and third bytes are the X and Y
;positions on the map of the treasure, respectively.  The fourth byte is the treasure type.

TreasureTable:
.byte MAP_TANTCSTL_GF, $01, $0D, TRSR_GLD2  ;Tant castle, GF at 1,13: 6-13g.
		.byte MAP_TANTCSTL_GF, $01, $0F, TRSR_GLD2;($9DD1)Tant castle, GF at 1,15: 6-13g.
		.byte MAP_TANTCSTL_GF, $02, $0E, TRSR_GLD2;($9DD5)Tant castle, GF at 2,14: 6-13g.
		.byte MAP_TANTCSTL_GF, $03, $0F, TRSR_GLD2;($9DD9)Tant castle, GF at 3,15: 6-13g.
.byte MAP_THRONEROOM,  $04, $04, TRSR_GLD5  ;Throne room at 4,4: 120g.
		.byte MAP_THRONEROOM,  $05, $04, TRSR_TORCH;($9DE1)Throne room at 5,4: Torch.
		.byte MAP_THRONEROOM,  $06, $01, TRSR_KEY;($9DE5)Throne room at 6,1: Magic key.
		.byte MAP_RIMULDAR,	$18, $17, TRSR_WINGS;($9DE9)Rumuldar at 24,23: wings.
.byte MAP_GARINHAM,	$08, $05, TRSR_GLD3  ;Garingham at 8,5: 10-17g.
		.byte MAP_GARINHAM,	$08, $06, TRSR_HERB;($9DF1)Garingham at 8,6: Herb.
		.byte MAP_GARINHAM,	$09, $05, TRSR_TORCH;($9DF5)Garingham at 9,5: Torch.
		.byte MAP_DLCSTL_BF,   $0B, $0B, TRSR_HERB;($9DF9)Drgnlrd castle BF at 11,11: Herb.
		.byte MAP_DLCSTL_BF,   $0B, $0C, TRSR_GLD4;($9DFD)Drgnlrd castle BF at 11,12: 500-755g.
		.byte MAP_DLCSTL_BF,   $0B, $0D, TRSR_WINGS;($9E01)Drgnlrd castle BF at 11,13: wings.
		.byte MAP_DLCSTL_BF,   $0C, $0C, TRSR_KEY;($9E04)Drgnlrd castle BF at 12,12: Key.
		.byte MAP_DLCSTL_BF,   $0C, $0D, TRSR_BELT;($9E09)Drgnlrd castle BF at 12,13: Cursed belt.
		.byte MAP_DLCSTL_BF,   $0D, $0D, TRSR_HERB;($9E0D)Drgnlrd castle BF at 13,13: Herb.
		.byte MAP_TANTCSTL_SL, $04, $05, TRSR_SUN;($9E11)Tant castle, SL at 4,5: Stones of sunlight.
		.byte MAP_RAIN,		$03, $04, TRSR_RAIN;($9E15)Staff of rain cave at 3,4: Staff of rain.
		.byte MAP_CVGAR_B1,	$0B, $00, TRSR_HERB;($9E19)Gar cave B1 at 11,0: Herb.
		.byte MAP_CVGAR_B1,	$0C, $00, TRSR_GLD1;($9E1D)Gar cave B1 at 12,0: 5-20g.
		.byte MAP_CVGAR_B1,	$0D, $00, TRSR_GLD2;($9E21)Gar cave B1 at 13,0: 6-13g.
		.byte MAP_CVGAR_B3,	$01, $01, TRSR_BELT;($9E25)Gar cave B3 at 1,1: Cursed belt.
.byte MAP_CVGAR_B3,	$0D, $06, TRSR_HARP  ;Gar cave B3 at 13,6: Silver harp.
		.byte MAP_DLCSTL_SL2,  $05, $05, TRSR_ERSD;($9E2D)Drgnlrd castle SL2 at 5,5: Erdrick's sword.
		.byte MAP_RCKMTN_B2,   $01, $06, TRSR_NCK;($9E31)Rock mtn B2 at 1,6: Death nck or 100-131g.
		.byte MAP_RCKMTN_B2,   $03, $02, TRSR_TORCH;($9E35)Rock mtn B2 at 3,2: Torch.
.byte MAP_RCKMTN_B2,   $02, $02, TRSR_RING  ;Rock mtn B2 at 2,2: Fighter's ring.
		.byte MAP_RCKMTN_B2,   $0A, $09, TRSR_GLD3;($9E3D)Rock mtn B2 at 10,9: 10-17g.
		.byte MAP_RCKMTN_B1,   $0D, $05, TRSR_HERB;($9E41)Rock mtn B1 at 13,5: Herb.
		.byte MAP_ERDRCK_B2,   $09, $03, TRSR_TBLT;($9E45)Erd cave B2 at 9,3: Erdrick's tablet.

;----------------------------------------------------------------------------------------------------

;The following table contains the stats for the enemies.  There are 16 bytes per enemy.  The
;upper 8 bytes do not appear to be used.  The lower 8 bytes are the following:
;Att  - Enemy's attack power.
;Def  - Enemy's defense power.
;HP   - Enemy's base hit points.
;Spel - Enemy's spells.
;Agi  - Enemy's agility.
;Mdef - Enemy's magical defense.
;Exp  - Experience received from defeating enemy.
;Gld  - Gold received from defeating enemy.

EnemyStatsTablePointer:				   ;Pointer to the table below.
.word EnemyStatsTable

;----------------------------------------------------------------------------------------------------
; Monster Statistics Table - Generated from assets/json/monsters_verified.json
; To modify monster stats, edit the JSON file and rebuild
;----------------------------------------------------------------------------------------------------
.include "generated/monster_data.asm"

;----------------------------------------------------------------------------------------------------

;The table below provides the base stats per level.  The bytes represent the following stats:
;Byte 1-Strength, byte 2-Agility, byte 3-Max HP, byte 4-Max MP, byte 5-Healmore and Hurtmore
;spell flags, byte 6-All other spell flags.

		.word BaseStatsTable	;($A0CB)

BaseStatsTable:
		.byte $04, $04, $0F, $00, $00, $00;($A0CD)Level 1.
		.byte $05, $04, $16, $00, $00, $00;($A0D3)Level 2.
.byte $07, $06, $18, $05, $00, $01  ;Level 3.
		.byte $07, $08, $1F, $10, $00, $03;($A0DF)Level 4.
		.byte $0C, $0A, $23, $14, $00, $03;($A0E5)Level 5.
		.byte $10, $0A, $26, $18, $00, $03;($A0EB)Level 6.
		.byte $12, $11, $28, $1A, $00, $07;($A0F1)Level 7.
		.byte $16, $14, $2E, $1D, $00, $07;($A0F7)Level 8.
		.byte $1E, $16, $32, $24, $00, $0F;($A0FD)Level 9.
		.byte $23, $1F, $36, $28, $00, $1F;($A103)Level 10.
.byte $28, $23, $3E, $32, $00, $1F  ;Level 11.
		.byte $30, $28, $3F, $3A, $00, $3F;($A10F)Level 12.
		.byte $34, $30, $46, $40, $00, $7F;($A115)Level 13.
		.byte $3C, $37, $4E, $46, $00, $7F;($A11B)Level 14.
		.byte $44, $40, $56, $48, $00, $FF;($A121)Level 15.
		.byte $48, $46, $5C, $5F, $00, $FF;($A127)Level 16.
		.byte $48, $4E, $64, $64, $01, $FF;($A12D)Level 17.
		.byte $55, $54, $73, $6C, $01, $FF;($A133)Level 18.
.byte $57, $56, $82, $73, $03, $FF  ;Level 19.
		.byte $5C, $58, $8A, $80, $03, $FF;($A13F)Level 20.
		.byte $5F, $5A, $95, $87, $03, $FF;($A145)Level 21.
		.byte $61, $5A, $9E, $92, $03, $FF;($A14B)Level 22.
		.byte $63, $5E, $A5, $99, $03, $FF;($A151)Level 23.
		.byte $67, $62, $AA, $A1, $03, $FF;($A157)Level 24.
.byte $71, $64, $AE, $A1, $03, $FF  ;Level 25.
.byte $75, $69, $B4, $A8, $03, $FF  ;Level 26.
		.byte $7D, $6B, $BD, $AF, $03, $FF;($A169)Level 27.
		.byte $82, $73, $C3, $B4, $03, $FF;($A16F)Level 28.
		.byte $87, $78, $C8, $BE, $03, $FF;($A175)Level 29.
		.byte $8C, $82, $D2, $C8, $03, $FF;($A17B)Level 30.

;----------------------------------------------------------------------------------------------------

;This function appears to not be used.  It is not directly called through any other function
;or the IRQ interrupt.

PLA					 ;Pull the value off the stack.

		CLC					 ;($A182)
		ADC #$01				;($A183)
		STA GenPtr3ELB		  ;($A185)Add the value to the pointer.
		PLA					 ;($A187)
ADC #$00				;
		STA GenPtr3EUB		  ;($A18A)

		PHA					 ;($A18C)
		LDA GenPtr3ELB		  ;($A18D)Push the new pointer value on the stack.
		PHA					 ;($A18F)

		LDY #$00				;($A190)Use the pointer to retreive a byte from memory.
		LDA (GenPtr3E),Y		;($A192)

;----------------------------------------------------------------------------------------------------

ShowWindow:
		JSR DoWindowPrep		;($A194)($AEE1)Do some initial prep before window is displayed.
		JSR WindowSequence	  ;($A197)($A19B)run the window building sequence.
		RTS					 ;($A19A)

;----------------------------------------------------------------------------------------------------

WindowSequence:
		STA WindowType		  ;($A19B)Save the window type.

		LDA WindowBuildPhase	;($A19E)Indicate first phase of window build is ocurring.
		ORA #$80				;($A1A1)
		STA WindowBuildPhase	;($A1A3)

JSR WindowConstruct		;($A1B1)Do the first phase of window construction.
		JSR WindowCalcBufAddr   ;($A1A9)($A879)Calculate screen buffer address for data.

		LDA #$40				;($A1AC)Indicate second phase of window build is ocurring.
		STA WindowBuildPhase	;($A1AE)

WindowConstruct:
		JSR GetWndDatPtr		;($A1B1)($A1D0)Get pointer to window data.
JSR GetWndConfig		;($A1E4)Get window configuration data.
		JSR WindowEngine		;($A1B7)($A230)The guts of the window engine.

		BIT WindowBuildPhase	;($A1BA)Finishing up the first phase?
		BMI WindowConstructDone ;($A1BD)If so, branch to

		LDA WindowType		  ;($A1BF)
		CMP #WND_SPELL1		 ;($A1C2)Special case. Don't destroy these windows when done.
BCC WindowConstructDone	;The spell 1 window is never used and the alphabet
		CMP #WINDOW_ALPHBT	  ;($A1C6)window does not disappear when an item is selected.
		BCS WindowConstructDone ;($A1C8)

BRK					 ;Remove window from screen.
		.byte $05, $07		  ;($A1CB)($A7A2)RemoveWindow, bank 0.

WindowConstructDone:
		LDA WindowSelResults	;($A1CD)Return window selection results, if any.
		RTS					 ;($A1CF)

;----------------------------------------------------------------------------------------------------

GetWndDatPtr:
		LDA #$00				;($A1D0)First entry in description table is for windows.
		JSR GetDescPtr		  ;($A1D2)($A823)Get pointer into description table.

LDA WindowType		  ;*2. Pointer is 2 bytes.
		ASL					 ;($A1D8)

		TAY					 ;($A1D9)
LDA (DescPtr),Y		 ;
		STA WindowDataPointerLB ;($A1DC)Get pointer to desired window data table.
		INY					 ;($A1DE)
LDA (DescPtr),Y		 ;
		STA WindowDataPointerUB ;($A1E1)
		RTS					 ;($A1E3)

;----------------------------------------------------------------------------------------------------

GetWndConfig:
		LDY #$00				;($A1E4)Set pointer at base of data table.
		LDA (WindowDataPointer),Y;($A1E6)
		STA WindowOptions	   ;($A1E8)Get window options byte from table.

		INY					 ;($A1EB)
		LDA (WindowDataPointer),Y;($A1EC)
		STA WindowHeightBlocks  ;($A1EE)Get window height in block from table.
ASL					 ;
		STA WindowHeight		;($A1F2)Convert window height to tiles,

INY					 ;
		LDA (WindowDataPointer),Y;($A1F6)Get window width from table.
		STA WindowWidth		 ;($A1F8)

		INY					 ;($A1FB)
		LDA (WindowDataPointer),Y;($A1FC)Get window position from table.
		STA WindowPosition	  ;($A1FE)
PHA					 ;

		AND #$0F				;($A202)
		ASL					 ;($A204)Extract and save column position nibble.
STA WindowColumnPosition		   ;

		PLA					 ;($A207)
		AND #$F0				;($A208)
		LSR					 ;($A20A)Extract and save row position nibble.
		LSR					 ;($A20B)
		LSR					 ;($A20C)
		STA WindowRowPosition   ;($A20D)

		INY					 ;($A20F)MSB set in window options byte indicates its
		LDA WindowOptions	   ;($A210)a selection window. Is this a selection window?
BPL +				   ;If not, branch to skip selection window bytes.

LDA (WindowDataPointer),Y	   ;A selection window.  Get byte containing
		STA WindowColumns	   ;($A217)column width in tiles.

		INY					 ;($A21A)A selection window. Get byte with cursor
		LDA (WindowDataPointer),Y;($A21B)home position. X in upper nibble, Y in lower.
		STA WindowCursorHome	;($A21D)

		INY					 ;($A220)
		* BIT WindowOptions	 ;($A221)
		BVC +				   ;($A224)This bit is never set. Branch always.
LDA (WindowDataPointer),Y	   ;
STA WindowUnused1		  ;

		INY					 ;($A22B)
* STY WindowDataIndex		 ;Save index into current window data table.
		RTS					 ;($A22F)

;----------------------------------------------------------------------------------------------------

WindowEngine:
		JSR InitWindowEngine	;($A230)($A248)Initialize variables used by the window engine.

BuildWindowLoop:
		JSR WindowUpdateWrkTile ;($A233)($A26A)Update the working tile pattern.
JSR GetNxtWndByte	   ;($A2B7)Process next window data byte.
		JSR JumpToWndFunc	   ;($A239)($A30A)Use data byte for indirect function jump.
JSR WindowShowLine		 ;($A5CE)Show window line on the screen.
		JSR WindowChkFullHeight ;($A23F)($A5F9)Check if window build is done.
		BCC BuildWindowLoop	 ;($A242)Is window build done? If not, branch to do another row.

		JSR DoBlinkingCursor	;($A244)($A63D)Show blinking cursor on selection windows.
		RTS					 ;($A247)

;----------------------------------------------------------------------------------------------------

InitWindowEngine:
		JSR ClearWndLineBuf	 ;($A248)($A646)Clear window line buffer.
		LDA #$FF				;($A24B)
STA WindowUnused64FB	   ;Written to but never accessed.

LDA #$00				;
		STA WindowXPosition	 ;($A252)
		STA WindowYPosition	 ;($A255)Zero out window variables.
		STA WindowThisDescription;($A258)
		STA WindowDescriptionHalf;($A25B)
STA WindowBuildRow		 ;

		LDX #$0F				;($A261)
		* STA AttributeTblBuf,X ;($A263)
		DEX					 ;($A266)Zero out attribute table buffer.
		BPL -				   ;($A267)
		RTS					 ;($A269)

;----------------------------------------------------------------------------------------------------

WindowUpdateWrkTile:
		LDA #TL_BLANK_TILE1	 ;($A26A)Assume working tile will be a blank tile.
		STA WorkTile			;($A26C)

		LDX WindowXPosition	 ;($A26F)Is position in left most column?
		BEQ CheckWndRow		 ;($A272)If so, branch to check row.

		INX					 ;($A274)Is position not at right most column?
		CPX WindowWidth		 ;($A275)
		BNE CheckWndBottom	  ;($A278)If not, branch to check if in bottom rom.

		LDX WindowYPosition	 ;($A27A)In left most column.  In top row?
BEQ WindowUpperRightCorner	  ;If so, branch to load upper right corner tile.

		INX					 ;($A27F)
CPX WindowHeight		   ;In left most column. in bottom row?
		BEQ WindowBotRightCorner;($A283)If so, branch to load lower right corner tile.

		LDA #TL_RIGHT		   ;($A285)Border pattern - right border.
		BNE UpdateWndWrkTile	;($A287)Done. Branch to update working tile and exit.

WindowUpperRightCorner:
		LDA #TL_UPPER_RIGHT	 ;($A289)Border pattern - upper right corner.
		BNE UpdateWndWrkTile	;($A28B)Done. Branch to update working tile and exit.

WindowBotRightCorner:
		LDA #TL_BOT_RIGHT	   ;($A28D)Border pattern - lower right corner.
		BNE UpdateWndWrkTile	;($A28F)Done. Branch to update working tile and exit.

CheckWndRow:
		LDX WindowYPosition	 ;($A291)In top row. In left most ccolumn?
		BEQ WindowUpperLeftCorner;($A294)If so, branch to load upper left corner tile.

		INX					 ;($A296)
		CPX WindowHeight		;($A297)In top row.  In left most column?
BEQ WindowBotLeftCorner	  ;If so, branch to load lower left corner tile.
		LDA #TL_LEFT			;($A29C)Border pattern - left border.
		BNE UpdateWndWrkTile	;($A29E)Done. Branch to update working tile and exit.

WindowUpperLeftCorner:
LDA #TL_UPPER_LEFT	  ;Border pattern - Upper left corner.
BNE UpdateWndWrkTile	;Done. Branch to update working tile and exit.

WindowBotLeftCorner:
		LDA #TL_BOT_LEFT		;($A2A4)Border pattern - Lower left corner.
		BNE UpdateWndWrkTile	;($A2A6)Done. Branch to update working tile and exit.

CheckWndBottom:
		LDX WindowYPosition	 ;($A2A8)Not in left most or right most columns.
INX					 ;
		CPX WindowHeight		;($A2AC)In bottom column?
		BNE +				   ;($A2AF)If not, branch to keep blank tile as working tile.
		LDA #TL_BOTTOM		  ;($A2B1)Border pattern - bottom border.

UpdateWndWrkTile:
		STA WorkTile			;($A2B3)Update working tile and exit.
		* RTS				   ;($A2B6)

;----------------------------------------------------------------------------------------------------

GetNxtWndByte:
		LDA WorkTile			;($A2B7)
		CMP #TL_BLANK_TILE1	 ;($A2BA)Is current working byte not a blank tile?
		BNE WorkTileNotBlank	;($A2BC)if so, branch, nothing to do right now.

		LDA WindowOptions	   ;($A2BE)Is this a single spaced window?
		AND #$20				;($A2C1)
		BNE GetNextWndByte	  ;($A2C3)If so, branch to get next byte from window data table.

LDA WindowYPosition			 ;This is a double spaced window.
		LSR					 ;($A2C8)Are we at an even row?
		BCC GetNextWndByte	  ;($A2C9)If so, branch to get next data byte, else nothing to do.

LDA WindowBuildRow		 ;Is the window being built and on the first block row?
		CMP #$01				;($A2CE)
		BNE ClearWindowControlByte;($A2D0)If not branch.

		LDA #$00				;($A2D2)Window just started being built.
STA WindowXPosition			 ;
		LDX WindowYPosition	 ;($A2D7)Clear x and y position variables.
		INX					 ;($A2DA)
STX WindowHeight		   ;Set window height to 1.

		PLA					 ;($A2DE)Remove last return address.
		PLA					 ;($A2DF)
		JMP BuildWindowLoop	 ;($A2E0)($A233)continue building the window.

ClearWindowControlByte:
LDA #$00				;Prepare to load a row of empty tiles.
		BEQ SeparateControlByte ;($A2E5)

GetNextWndByte:
		LDY WindowDataIndex	 ;($A2E7)
		INC WindowDataIndex	 ;($A2EA)Get next byte from window data table and increment index.
		LDA (WindowDataPointer),Y;($A2ED)
		BPL GotCharDat		  ;($A2EF)Is retreived byte a control byte? if not branch.

SeparateControlByte:
		AND #$7F				;($A2F1)Control byte found.  Discard bit indicating its a control byte.
		PHA					 ;($A2F3)

		AND #$07				;($A2F4)Extract and save repeat counter bits.
		STA WindowParameter	 ;($A2F6)

		PLA					 ;($A2F9)
		LSR					 ;($A2FA)
LSR					 ;Shift control bits to lower end of byte and save.
		LSR					 ;($A2FC)
		STA WindowCcontrol	  ;($A2FD)
		RTS					 ;($A300)

GotCharDat:
		STA WorkTile			;($A301)Store current byte in working tile variable.

WorkTileNotBlank:
		LDA #$10				;($A304)
		STA WindowCcontrol	  ;($A306)Indicate character byte being processed.
		RTS					 ;($A309)

;----------------------------------------------------------------------------------------------------

JumpToWndFunc:
		LDA WindowCcontrol	  ;($A30A)Use window control byte as pointer
		ASL					 ;($A30D)into window control function table.

		TAX					 ;($A30E)
		LDA WindowControlPointerTable,X;($A30F)
		STA WindowFunctionLB	;($A312)Get function address from table and jump.
		LDA WindowControlPointerTable+1,X;($A314)
STA WindowFunctionUB			;
		JMP (WindowFunctionPointer);($A319)

;----------------------------------------------------------------------------------------------------

WindowBlankTiles:
		LDA #TL_BLANK_TILE1	 ;($A31C)Prepare to place blank tiles.
		STA WorkTile			;($A31E)

		JSR SetCountLength	  ;($A321)($A600)Calculate the required length of the counter.
		* BIT WindowBuildPhase  ;($A324)In the second phase of window building?
BVS +				   ;If so, branch to skip building buffer.

		JSR BuildWndLine		;($A329)($A546)Transfer data into window line buffer.
JMP NextBlankTile	   ;($A332)Move to next blank tile.

		* JSR WindowNextXPos	;($A32F)($A573)Increment x position in current window row.

NextBlankTile:
		DEC WindowCounter	   ;($A332)More tiles to process?
		BNE --				  ;($A335)If so, branch to do another.
		RTS					 ;($A337)

;----------------------------------------------------------------------------------------------------

WindowHorizontalTiles:
		BIT WindowOptions	   ;($A338)Branch always.  This bit is never set for any of the windows.
BVC DoHorizontalTiles		 ;

		LDA #TL_BLANK_TILE1	 ;($A33D)Blank tile.
		STA WorkTile			;($A33F)
		JSR BuildWndLine		;($A342)($A546)Transfer data into window line buffer.
		LDA #TL_TOP2			;($A345)Border pattern - upper border.
		STA WorkTile			;($A347)
		JSR BuildWndLine		;($A34A)($A546)Transfer data into window line buffer.

DoHorizontalTiles:
		LDA #TL_TOP1			;($A34D)Border pattern - upper border.
		STA WorkTile			;($A34F)
		JSR SetCountLength	  ;($A352)($A600)Calculate the required length of the counter.

HorzTilesLoop:
		JSR BuildWndLine		;($A355)($A546)Transfer data into window line buffer.
DEC WindowCounter		  ;More tiles to process?
BNE HorzTilesLoop	   ;If so, branch to do another.
		RTS					 ;($A35D)

;----------------------------------------------------------------------------------------------------

WindowHitMgcPoints:
LDA #$03				;Max number is 3 digits.
		STA SubBufLength		;($A360)Set buffer length to 3.

		LDX #HitPoints		  ;($A363)Prepare to convert hitpoints to BCD.
		LDA WindowParam		 ;($A365)
AND #$04				;Is bit 2 of parameter byte set?
		BEQ +				   ;($A36A)If so, branch to convert hit points.

		LDX #MagicPoints		;($A36C)Convert magic points to BCD.

* LDY #$01				;1 byte to convert.
		JMP WindowBinToBCD	  ;($A370)($A61C)Convert binary word to BCD.

;----------------------------------------------------------------------------------------------------

WindowGold:
		LDA #$05				;($A373)Max number is 5 digits.
		STA SubBufLength		;($A375)Set buffer length to 5.
		JSR GoldToBCD		   ;($A378)($A8BA)Convert player's gold to BCD.
		JMP WindowTempToLineBuf ;($A37B)($A62B)Transfer value from temp buf to window line buffer.

;----------------------------------------------------------------------------------------------------

WindowShowLevel:
LDA WindowParam			;Is parameter not 0? If so, get level from a saved game.
BNE WindowGetSavedGame	 ;Branch to get saved game level.

WindowConvertLevel:
		LDA #$02				;($A383)Set buffer length to 2.
		STA SubBufLength		;($A385)
		LDX #DisplayedLevel	 ;($A388)Load player's level.

		LDY #$01				;($A38A)1 byte to convert.
		JMP WindowBinToBCD	  ;($A38C)($A61C)Convert binary word to BCD.

WindowGetSavedGame:
		JSR WindowLoadGameDat   ;($A38F)($F685)Load selected game into memory.
JMP WindowConvertLevel		;($A383)Convert player level to BCD.

;----------------------------------------------------------------------------------------------------

WindowShowExp:
		LDA #$05				;($A395)Set buffer length to 5.
		STA SubBufLength		;($A397)

		LDX #ExpLB			  ;($A39A)Load index for player's experience.

		LDY #$02				;($A39C)2 bytes to convert.
JMP WindowBinToBCD		 ;($A61C)Convert binary word to BCD.

;----------------------------------------------------------------------------------------------------

WindowShowName:
		LDA WindowParam		 ;($A3A1)
		CMP #$01				;($A3A4)Get the full name of the current player.
		BEQ WindowGetfullName   ;($A3A6)

		CMP #$04				;($A3A8)Get the full name of a saved character.
		BEQ WindowFullSaved	 ;($A3AA)The SaveSelected variable is set before this function is called.

		CMP #$05				;($A3AC)Get the lower 4 letters of a saved character.
BCS WndLwr4Saved		;The SaveSelected variable is set with the WindowParam variable.

WindowPrepareGetLower:
		LDA #$04				;($A3B0)Set buffer length to 4.
STA SubBufLength		;

		LDX #$00				;($A3B5)Start at beginning of name registers.
		LDY SubBufLength		;($A3B7)

WindowGetLowerName:
		LDA DispName0,X		 ;($A3BA)Load name character and save it in the buffer.
		STA TempBuffer-1,Y	  ;($A3BC)
		INX					 ;($A3BF)
		DEY					 ;($A3C0)Have 4 characters been loaded?
BNE WindowGetLowerName	   ;If not, branch to get next character.

		JMP WindowTempToLineBuf ;($A3C3)($A62B)Transfer value from temp buf to window line buffer.

WindowGetfullName:
		JSR WindowPrepareGetLower;($A3C6)($A3B0)Get lower 4 characters of name.

		LDA #$04				;($A3C9)Set buffer length to 4.
		STA SubBufLength		;($A3CB)

		LDX #$00				;($A3CE)Start at beginning of name registers.
		LDY SubBufLength		;($A3D0)

WindowGetUpperName:
		LDA DispName4,X		 ;($A3D3)Load name character and save it in the buffer.
		STA TempBuffer-1,Y	  ;($A3D6)
INX					 ;
		DEY					 ;($A3DA)Have 4 characters been loaded?
		BNE WindowGetUpperName  ;($A3DB)If not, branch to get next character.

		JMP WindowTempToLineBuf ;($A3DD)($A62B)Transfer value from temp buf to window line buffer.

WndLwr4Saved:
		LDA #$04				;($A3E0)Set buffer length to 4.
STA SubBufLength		;

		LDA WindowParameter	 ;($A3E5)
		SEC					 ;($A3E8)Select the desired save game by subtracting 5
SBC #$05				;from the WindowParameter variable.
STA SaveSelected		;

		JSR WindowLoadGameDat   ;($A3EE)($F685)Load selected game into memory.
		JMP WindowPrepareGetLower;($A3F1)($A3B0)Get lower 4 letters of saved character's name.

WindowFullSaved:
		LDA #$08				;($A3F4)Set buffer length to 8.
		STA SubBufLength		;($A3F6)
		JSR WindowLoadGameDat   ;($A3F9)($F685)Load selected game into memory.
		JMP WindowGetfullName   ;($A3FC)($A3C6)Get full name of saved character.

;----------------------------------------------------------------------------------------------------

WindowItemDesc:
LDA #$09				;Max buffer length is 9 characters.
		STA SubBufLength		;($A401)

		LDA WindowParameter	 ;($A404)Is this description for player or shop inventory?
		CMP #$03				;($A407)
		BCS WindowDoInvItem	 ;($A409)If so, branch.

		LDA WindowParameter	 ;($A40B)
		ADC #$08				;($A40E)Add 8 to the description buffer
TAX					 ;index and get description byte.
		LDA DescBuf,X		   ;($A411)

JSR WpnArmrConv		 ;($A685)Convert index to proper weapon/armor description byte.
		JSR LookupDescriptions  ;($A416)($A790)Get description from tables.
		JSR WindowTempToLineBuf ;($A419)($A62B)Transfer value from temp buf to window line buffer.
		JMP SecondDescHalf	  ;($A41C)($A7D7)Change to second description half.

WindowDoInvItem:
JSR WindowGetDescByte	  ;($A651)Get byte from description buffer, store in A.
		JSR DoInvConv		   ;($A422)($A657)Get inventory description byte.
		PHA					 ;($A425)Push description byte on stack.

		LDA WindowParam		 ;($A426)Is the player's inventory the target?
		CMP #$03				;($A429)
		BNE WindowDescNum	   ;($A42B)If not, branch.

		PLA					 ;($A42D)Place a copy of the description byte in A.
		PHA					 ;($A42E)

CMP #DSC_HERB		   ;Is the description byte for herbs?
		BEQ WindowDecDescLength ;($A431)If so, branch.

		CMP #DSC_KEY			;($A433)Is the description byte for keys?
		BNE WindowDescNum	   ;($A435)If not, branch.

WindowDecDescLength:
		DEC SubBufLength		;($A437)Decrement length of description buffer.

WindowDescNum:
		PLA					 ;($A43A)Put description byte in A.
		JSR LookupDescriptions  ;($A43B)($A790)Get description from tables.
		JSR WindowTempToLineBuf ;($A43E)($A62B)Transfer value from temp buf to window line buffer.
		LDA WindowDescriptionHalf;($A441)Is the first description half being worked on?
		BNE WndDesc2ndHalf	  ;($A444)If so, branch to work on second description half.

		LDA WindowParameter	 ;($A446)Is this the player's inventory?
		CMP #$03				;($A449)
		BNE WndDesc2ndHalf	  ;($A44B)If not, branch to work on second description half.

		LDA WindowDescIndex	 ;($A44D)Is the current description byte for herbs?
		CMP #DSC_HERB		   ;($A450)
		BEQ WindowNumHerbs	  ;($A452)If so, branch to get number of herbs in player's inventory.

		CMP #DSC_KEY			;($A454)Is the current description byte for keys?
		BEQ WindowNumKeys	   ;($A456)If so, branch.

WndDesc2ndHalf:
		JMP SecondDescHalf	  ;($A458)($A7D7)Change to second description half.

WindowNumHerbs:
		LDA InventoryHerbs	  ;($A45B)Get nuber of herbs player has in inventory.
		BNE WindowPrepareBCD	;($A45D)More than 0? If so, branch to convert and display amount.

WindowNumKeys:
		LDA InventoryKeys	   ;($A45F)Get number of keys player has in inventory.

WindowPrepareBCD:
		STA BCDByte0			;($A461)Load value into first BCD conversion byte.
		LDA #$00				;($A463)
		STA BCDByte1			;($A465)The other 2 BCD conversion bytes are not used.
		STA BCDByte2			;($A467)
		JSR ClearTempBuffer	 ;($A469)($A776)Write blank tiles to buffer.

LDA #$01				;Set buffer length to 1.
		STA SubBufLength		;($A46E)

		JSR BinWordToBCD_	   ;($A471)($A625)Convert word to BCD.
		JSR WindowTempToLineBuf ;($A474)($A62B)Transfer value from temp buf to window line buffer.
		JMP SecondDescHalf	  ;($A477)($A7D7)Change to second description half.

;----------------------------------------------------------------------------------------------------

WindowOneSpellDesc:
		LDA #$09				;($A47A)Set max buffer length for description to 9 bytes.
STA SubBufLength		;
		JSR WindowGetDescByte   ;($A47F)($A651)Get byte from description buffer and store in A.

		SEC					 ;($A482)Subtract 1 from description byte to get correct offset.
		SBC #$01				;($A483)

		JSR WindowGetSpellDesc  ;($A485)($A7EB)Get spell description.
JSR WindowTempToLineBuf	;($A62B)Transfer value from temp buf to window line buffer.
		INC WindowThisDescription;($A48B)Increment pointer to next position in description buffer.
		RTS					 ;($A48E)

;----------------------------------------------------------------------------------------------------

WindowItemCost:
		JSR ClearTempBuffer	 ;($A48F)($A776)Write blank tiles to buffer.
		LDA #$05				;($A492)
		STA SubBufLength		;($A494)Buffer is max. 5 characters long.

		LDA #$06				;($A497)WindowCostTbl is the table to use for item costs.
JSR GetDescPtr		  ;($A823)Get pointer into description table.

		LDA WindowDescIndex	 ;($A49C)Is the description index 0?
		BEQ WindowCstToLineBuf  ;($A49F)If so, branch to skip getting item cost.

		ASL					 ;($A4A1)*2. Item costs are 2 bytes.
		TAY					 ;($A4A2)

		LDA (DescPtr),Y		 ;($A4A3)Get lower byte of item cost.
		STA BCDByte0			;($A4A5)

		INY					 ;($A4A7)
		LDA (DescPtr),Y		 ;($A4A8)Get middle byte of item cost.
		STA BCDByte1			;($A4AA)

		LDA #$00				;($A4AC)Third byte is not used.
STA BCDByte2			;

		JSR BinWordToBCD_	   ;($A4B0)($A625)Convert word to BCD.

WindowCstToLineBuf:
JMP WindowTempToLineBuf	;($A62B)Transfer value from temp buf to window line buffer.

;----------------------------------------------------------------------------------------------------

WindowVariableHeight:
		LDA #$00				;($A4B6)Zero out description index.
		STA WindowThisDescription;($A4B8)
LDA #$00				;Start at first half of description.
		STA WindowDescriptionHalf;($A4BD)

		JSR CalcNumItems		;($A4C0)($A4CD)Get number of items to display in window.
STA WindowBuildRow		 ;Save the number of items.

		LDA WindowDataIndex	 ;($A4C6)
STA WindowRepeatIndex	  ;Set this data index as loop point until all rows are built.
		RTS					 ;($A4CC)

;----------------------------------------------------------------------------------------------------

;When a spell is cast, the description buffer is loaded with pointers for the descriptions
;of spells that the player has.  The buffer is terminated with #$FF.  For example, if the
;player has the first three spells, the buffer will contain: #$01, #$02, #$03, #$FF.
;If the item list is for an inventory window, The window will start with #$01 and end with #$FF.

CalcNumItems:
		LDX #$01				;($A4CD)Point to second byte in the item description buffer.
		* LDA DescBuf,X		 ;($A4CF)
		CMP #ITM_END			;($A4D1)Has the end been found? If so, branch to move on.
		BEQ NumItemsEnd		 ;($A4D3)
		INX					 ;($A4D5)Go to the next index. Has the max been reached?
		BNE -				   ;($A4D6)If not, branch to look at the next byte.

NumItemsEnd:
		DEX					 ;($A4D8)
LDA DescBuf			 ;If buffer starts with 1, return item count unmodified.
CMP #$01				;
		BEQ ReturnNumItems	  ;($A4DD)

		INX					 ;($A4DF)
		CMP #$02				;($A4E0)If buffer starts with 2, increment item count.
		BEQ ReturnNumItems	  ;($A4E2)

		INX					 ;($A4E4)Increment item count again if anything other than 1 or 2.

ReturnNumItems:
		TXA					 ;($A4E5)Transfer item count to A.
		RTS					 ;($A4E6)

;----------------------------------------------------------------------------------------------------

WindowBuildVariable:
		LDA WindowParameter	 ;($A4E7)A parameter value of 2 will end the window
		CMP #$02				;($A4EA)without handling the last line.
		BEQ WindowBuildVarDone  ;($A4EC)

AND #$03				;Is the parameter anything but 0 or 2?
		BNE WindowBuildEnd	  ;($A4F0)If so, branch to finish window.

		LDA WindowBuildRow	  ;($A4F2)Is this the last row?
		BEQ WindowBuildVarDone  ;($A4F5)If so, branch to exit. No more repeating.

		DEC WindowBuildRow	  ;($A4F7)Is this the second to last row?
		BEQ WindowBuildVarDone  ;($A4FA)If so, branch to exit. No more repeating.

		LDA WindowRepeatIndex   ;($A4FC)Repeat this data index until all rows are built.
		STA WindowDataIndex	 ;($A4FF)

WindowBuildVarDone:
		RTS					 ;($A502)Done building row of variable height window.

;----------------------------------------------------------------------------------------------------

WindowBuildEnd:
		LDA #$00				;($A503)Start at beginning of window row.
		STA WindowXPosition	 ;($A505)
		STA WindowParameter	 ;($A508)Prepare to place blank tiles to end of row.

LDA WindowYPosition			 ;If Y position of window line is even, add 2 to the position
		AND #$01				;($A50E)and make it the window height.
		EOR #$01				;($A510)
		CLC					 ;($A512)If Y position of window line is odd, add 1 to the position
		ADC #$01				;($A513)and make it the window height.
		ADC WindowYPosition	 ;($A515)
		STA WindowHeight		;($A518)Required to properly form inventory windows.

LSR					 ;
STA WindowHeightBlocks	   ;/2. Block height is half the tile height.
		LDA WindowYPosition	 ;($A51F)

		AND #$01				;($A522)Does the last item only use a single row?
		BNE WindowEndBuild	  ;($A524)If not, branch to skip a blank line on bottom of window.

		LDA #TL_LEFT			;($A526)Border pattern - left border.
		STA WorkTile			;($A528)
JSR BuildWndLine		;($A546)Transfer data into window line buffer.
		JMP WindowBlankTiles	;($A52E)($A31C)Place blank tiles to end of row.

WindowEndBuild:
		RTS					 ;($A531)End building last row.

;----------------------------------------------------------------------------------------------------

WindowShowStat:
		LDX WindowParameter	 ;($A532)
LDA AttributeVariableTable,X	  ;Load desired player attribute from table.
		TAX					 ;($A538)

		LDA #$03				;($A539)Set buffer length to 3.
STA SubBufLength		;

		LDY #$01				;($A53E)1 byte to convert.
		JMP WindowBinToBCD	  ;($A540)($A61C)Convert binary word to BCD.

;----------------------------------------------------------------------------------------------------

WindowAddToBuf:
		JMP BuildWndLine		;($A543)($A546)Transfer data into window line buffer.

;----------------------------------------------------------------------------------------------------

BuildWndLine:
		LDA WindowYPosition	 ;($A546)Is this an even numbered window tile row?
		AND #$01				;($A549)
BEQ BldLoadWrkTile	  ;If so, branch.

LDA WindowWidth			;Odd row.  Prepare to save tile at end of window row.

BldLoadWrkTile:
		CLC					 ;($A550)
		ADC WindowXPosition	 ;($A551)Move to next index in the window line buffer.
		TAX					 ;($A554)

		LDA WorkTile			;($A555)Store working tile in the window line buffer.
		STA WindowLineBuffer,X  ;($A558)
JSR WindowStorePPUDat	  ;($A58B)Store window data byte in PPU buffer.

		CMP #TL_LEFT			;($A55E)Is this tile a left border or a space?
		BCS WindowNextXPos	  ;($A560)If so, branch to move to next column.

		LDA WindowLineBuffer-1,X;($A562)Was the last tile a top border tile?
		CMP #TL_TOP1			;($A565)
		BNE WindowNextXPos	  ;($A567)If not, branch to move to next column.

LDA WindowXPosition			 ;Is this the first column of this row?
		BEQ WindowNextXPos	  ;($A56C)If so, branch to move to next column.

		LDA #TL_TOP2			;($A56E)Replace last tile with a top border tile.
		STA WindowLineBuffer-1,X;($A570)

WindowNextXPos:
		INC WindowXPosition	 ;($A573)Increment position in window row.
		LDA WindowXPosition	 ;($A576)Still more space in current row?
CMP WindowWidth			;If so, branch to exit.
		BCC +				   ;($A57C)

		LDX #$01				;($A57E)At the end of the row.  Ensure the counter agrees.
		STX WindowCounter	   ;($A580)

		DEX					 ;($A583)
		STX WindowXPosition	 ;($A584)Move to the beginning of the next row.
		INC WindowYPosition	 ;($A587)
		* RTS				   ;($A58A)

;----------------------------------------------------------------------------------------------------

WindowStorePPUDat:
PHA					 ;
		TXA					 ;($A58C)
		PHA					 ;($A58D)Save a current copy of X,Y and A on the stack.
		TYA					 ;($A58E)
		PHA					 ;($A58F)

		BIT WindowBuildPhase	;($A590)Is this the second window building phase?
		BVS WindowStorePPUDatEnd;($A593)If so, skip. Only save data on first phase.

		JSR PrepPPUAddressCalc  ;($A595)($A8AD)Address offset for start of current window row.
		LDA #$20				;($A598)
		STA PPURowBytesLB	   ;($A59A)32 bytes per screen row.
		LDA #$00				;($A59C)
		STA PPURowBytesUB	   ;($A59E)

		LDA WindowYPosition	 ;($A5A0)Multiply 32 by current window row number.
		LDX #PPURowBytesLB	  ;($A5A3)
		JSR IndexedMult		 ;($A5A5)($A6EB)Calculate winidow row address offset.

		LDA PPURowBytesLB	   ;($A5A8)
		CLC					 ;($A5AA)
ADC WindowXPosition			 ;Add X position of window to calculated value.
		STA PPURowBytesLB	   ;($A5AE)Increment upper byte on a carry.
		BCC WindowAddOffsetToAddr;($A5B0)
		INC PPURowBytesUB	   ;($A5B2)

WindowAddOffsetToAddr:
		CLC					 ;($A5B4)
		LDA PPURowBytesLB	   ;($A5B5)Calculate lower byte of final PPU address.
		ADC PPUAddrLB		   ;($A5B7)
STA PPUAddrLB		   ;

		LDA PPURowBytesUB	   ;($A5BB)
		ADC PPUAddrUB		   ;($A5BD)Calculate upper byte of final PPU address.
STA PPUAddrUB		   ;

		LDY #$00				;($A5C1)
		LDA WorkTile			;($A5C3)Store window tile byte in the PPU buffer.
		STA (PPUBufferPointer),Y;($A5C6)

WindowStorePPUDatEnd:
		PLA					 ;($A5C8)
TAY					 ;
		PLA					 ;($A5CA)Restore X,Y and A from the stack.
		TAX					 ;($A5CB)
		PLA					 ;($A5CC)
		RTS					 ;($A5CD)

;----------------------------------------------------------------------------------------------------

WindowShowLine:
		LDA WindowYPosition	 ;($A5CE)Is this the beginning of an even numbered line?
		AND #$01				;($A5D1)
		ORA WindowXPosition	 ;($A5D3)
		BNE WindowExitShowLine  ;($A5D6)If not, branch to exit. This row already rendered.

		LDA WindowBuildPhase	;($A5D8)Is this the second phase of window building?
		BMI WindowExitShowLine  ;($A5DB)If so, branch to exit. Nothing to do here.

		LDA WindowWidth		 ;($A5DD)
		LSR					 ;($A5E0)Make a copy of window width and divide by 2.
		ORA #$10				;($A5E1)Set bit 4. translated to 2(two tile rows ber block row).
		STA WindowWidthTemp	 ;($A5E3)

		LDA WindowPosition	  ;($A5E6)Create working copy of current window position.
STA _WindowPosition		;Window position is represented in blocks.

		CLC					 ;($A5EC)Update window position of next row.
		ADC #$10				;($A5ED)
STA WindowPosition		 ;16 blocks per row.

		JSR WindowShowHide	  ;($A5F2)($ABC4)Show/hide window on the screen.
		JSR ClearWndLineBuf	 ;($A5F5)($A646)Clear window line buffer.

WindowExitShowLine:
		RTS					 ;($A5F8)Done showing window line.

;----------------------------------------------------------------------------------------------------

WindowChkFullHeight:
LDA WindowYPosition			 ;Get current window height.
		CMP WindowHeight		;($A5FC)Compare with final window height.
RTS					 ;

;----------------------------------------------------------------------------------------------------

SetCountLength:
		LDA WindowParameter	 ;($A600)Get parameter data for current window control byte.
		BNE +				   ;($A603)Is it zero?
		LDA #$FF				;($A605)If so, set counter length to maximum.

		* STA SubBufLength	  ;($A607)Set counter length.

		CLC					 ;($A60A)
		LDA WindowWidth		 ;($A60B)Is the current x position beyond the window width?
		SBC WindowXPosition	 ;($A60E)If so, branch to exit.
		BCC +				   ;($A611)

CMP SubBufLength		;Is window row remainder greater than counter length?
		BCS +				   ;($A616)If so, branch to exit.

STA SubBufLength		;Limit counter to remainder of current window row.
		* RTS				   ;($A61B)

;----------------------------------------------------------------------------------------------------

WindowBinToBCD:
		JSR _BinWordToBCD	   ;($A61C)($A622)To binary to BCD conversion.
		JMP WindowTempToLineBuf ;($A61F)($A62B)Transfer value from temp buf to window line buffer.

_BinWordToBCD:
JSR GetBinBytesBCD	  ;($A741)Load binary word to convert to BCD.

BinWordToBCD_:
		JSR ConvertToBCD		;($A625)($A753)Convert binary word to BCD.
JMP ClearBCDLeadZeros   ;($A764)Remove leading zeros from BCD value.

;----------------------------------------------------------------------------------------------------

WindowTempToLineBuf:
		* LDX SubBufLength	  ;($A62B)Get last unprocessed entry in temp buffer.
		LDA TempBuffer-1,X	  ;($A62E)
		STA WorkTile			;($A631)Load value into work tile byte.

		JSR BuildWndLine		;($A634)($A546)Transfer data into window line buffer.
		DEC SubBufLength		;($A637)
		BNE -				   ;($A63A)More bytes to process? If so, branch to process another byte.
		RTS					 ;($A63C)

;----------------------------------------------------------------------------------------------------

DoBlinkingCursor:
		LDA WindowOptions	   ;($A63D)Is the current window a selection window?
		BPL +				   ;($A640)If not, branch to exit.
		JSR WindowDoSelect	  ;($A642)($A8D1)Do selection window routines.
		* RTS				   ;($A645)

;----------------------------------------------------------------------------------------------------

ClearWndLineBuf:
		LDA #TL_BLANK_TILE1	 ;($A646)Blank tile index in pattern table.
LDX #$3B				;60 bytes in buffer.

		* STA WindowLineBuffer,X;($A64A)Clear window line buffer.
		DEX					 ;($A64D)Has 60 bytes been written?
		BPL -				   ;($A64E)If not, branch to clear more bytes.
		RTS					 ;($A650)

;----------------------------------------------------------------------------------------------------

WindowGetDescByte:
		LDX WindowThisDescription;($A651)
		LDA DescBuf+1,X		 ;($A654)Get description byte from buffer.
		RTS					 ;($A656)

;----------------------------------------------------------------------------------------------------

DoInvConv:
		PHA					 ;($A657)Is player's inventory the target?
		LDA WindowParameter	 ;($A658)
		CMP #$03				;($A65B)
		BEQ PlayerInvConv	   ;($A65D)If so, branch.

CMP #$04				;Is item shop inventory the target?
		BEQ ShopInvConv		 ;($A661)If so, branch.

PLA					 ;No other matches. Return description
		RTS					 ;($A664)buffer byte as description byte.

PlayerInvConv:
		PLA					 ;($A665)
		TAX					 ;($A666)Get proper description byte for player's inventory.
		LDA PlayerInventoryConversionTable-2,X;($A667)
		RTS					 ;($A66A)

ShopInvConv:
		PLA					 ;($A66B)Is tool shop inventory the description?
		CMP #$13				;($A66C)
		BCS ToolInvConv		 ;($A66E)If so, branch.

		TAX					 ;($A670)
LDA WeaponShopConversionTable-2,X  ;Get proper description byte for weapon shop inventory.
		RTS					 ;($A674)

ToolInvConv:
		SEC					 ;($A675)
		SBC #$13				;($A676)Is this the description byte for the dragon's scale?
		CMP #$05				;($A678)If so, branch to return dragon's scale description byte.
		BEQ DgnSclConv		  ;($A67A)

		LSR					 ;($A67C)
		TAX					 ;($A67D)Get proper description byte for tool shop inventory.
		LDA ItemShopConversionTable,X;($A67E)
RTS					 ;

DgnSclConv:
		LDA #DSC_DRGN_SCL	   ;($A682)Return dragon's scale description byte.
		RTS					 ;($A684)

WpnArmrConv:
		TAX					 ;($A685)
		LDA WeaponArmorConversionTable-9,X;($A686)Get proper description byte for weapon, armor and shield.
		RTS					 ;($A689)

PlayerInventoryConversionTable:
.byte DSC_HERB,	  DSC_KEY,	   DSC_TORCH,	 DSC_FRY_WATER
		.byte DSC_WINGS,	 DSC_DRGN_SCL,  DSC_FRY_FLUTE, DSC_FGHTR_RNG;($A68E)
		.byte DSC_ERD_TKN,   DSC_GWLN_LOVE, DSC_CRSD_BLT,  DSC_SLVR_HARP;($A692)
		.byte DSC_DTH_NCK,   DSC_STN_SUN,   DSC_RN_STAFF,  DSC_RNBW_DRP;($A696)

ItemShopConversionTable:
.byte DSC_HERB,	  DSC_TORCH,	 DSC_WINGS,	 DSC_DRGN_SCL

WeaponShopConversionTable:
		.byte DSC_BMB_POLE,  DSC_CLUB,	  DSC_CPR_SWD,   DSC_HND_AXE;($A69E)
		.byte DSC_BROAD_SWD, DSC_FLAME_SWD, DSC_ERD_SWD,   DSC_CLOTHES;($A6A2)
		.byte DSC_LTHR_ARMR, DSC_CHAIN_ML,  DSC_HALF_PLT,  DSC_FULL_PLT;($A6A6)
.byte DSC_MAG_ARMR,  DSC_ERD_ARMR,  DSC_SM_SHLD,   DSC_LG_SHLD
		.byte DSC_SLVR_SHLD	 ;($A6AE)

WeaponArmorConversionTable:
		.byte DSC_NONE,	  DSC_BMB_POLE,  DSC_CLUB,	  DSC_CPR_SWD;($A6AF)
.byte DSC_HND_AXE,   DSC_BROAD_SWD, DSC_FLAME_SWD, DSC_ERD_SWD
		.byte DSC_NONE,	  DSC_CLOTHES,   DSC_LTHR_ARMR, DSC_CHAIN_ML;($A6B7)
		.byte DSC_HALF_PLT,  DSC_FULL_PLT,  DSC_MAG_ARMR,  DSC_ERD_ARMR;($A6BB)
		.byte DSC_NONE,	  DSC_SM_SHLD,   DSC_LG_SHLD,   DSC_SLVR_SHLD;($A6BF)

;----------------------------------------------------------------------------------------------------

;This table runs the functions associated with the window control bytes.  The control bytes have the
;following format: 1CCCCPPP.  The MSB is always set to indicate it is a control byte.  The next 4
;bits are the index into the table below and dictate which function to run.  The 3 MSBs are the
;parameter bits and do various things for various functions.  Below is a list of the control bits
;and their functions.
;
; Byte range | Function							 | Parameter bits
;++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
;  $80-$87   | Place blank spaces in window.		| Number of blank spaces to place.			|
;			|									  | 0 = blanks to end of row.				   |
;  $88-$8F   | Place horizontal border in window.   | Number of border tiles to place.			|
;			|									  | 0 = border tiles to end of row.			 |
;  $90-$97   | Show hit points or magic points.	 | MSB set-show MP, MSB clear-show HP.		 |
;  $98-$9F   | Show player's gold.				  | None.									   |
;  $A0-$A7   | Show active/saved player's level.	| 0 = current game, 1 = saved game.		   |
;  $A8-$AF   | Show player's experience.			| None.									   |
;  $B0-$B7   | Show active/saved player's name.	 | 0 = current player, lower 4 letters.		|
;			|									  | 1 = current player, full name.			  |
;			|									  | 4 = Saved player, full name.				|
;			|									  | 5-7 = saved player, lower 4 letters.		|
;  $B8-$BF   | Show item/weapon/armor description.  | 0 = weapon, 1 = armor, 2 = shield,		  |
;			|									  | 3 = player's inventory, 4 = shop inventory. |
;  $C0-$C7   | Show description for selected spell. | None.									   |
;  $C8-$CF   | Show item cost.					  | None.									   |
;  $D0-$D7   | Calculate variable window height.	| None.									   |
;  $D8-$DF   | Show player stat.					| 0 = strength, 1 = agility, 2 = attack,	  |
;			|									  | 3 = defense,  4 = max HP,  5 = Max MP	   |
;  $E0-$E7   | N/A								  | N/A										 |
;  $E8-$EF   | Display items in variable window.	| 0 = show items in window, 2 = end window,   |
;			|									  | 1,3,5,6,7 = Properly end window.			|
;  $F0-$F7   | N/A								  | N/A										 |
;  $F8-$FF   | N/A								  | N/A										 |
;++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

WindowControlPointerTable:
.word WindowBlankTiles	 ;($A31C)Place blank tiles.
		.word WindowHorizontalTiles;($A6C5)($A338)Place horizontal border tiles.
		.word WindowHitMgcPoints;($A6C7)($A35E)Show hit points, magic points.
		.word WindowGold		;($A6C9)($A373)Show gold.
		.word WindowShowLevel   ;($A6CB)($A37E)Show current/save game character level.
		.word WindowShowExp	 ;($A6CD)($A395)Show experience.
		.word WindowShowName	;($A6CF)($A3A1)Show name, 4 or 8 characters.
		.word WindowItemDesc	;($A6D1)($A3FF)Show weapon, armor, shield and item descriptions.
.word WindowOneSpellDesc   ;($A47A)Get spell description for current window row.
		.word WindowItemCost	;($A6D5)($A48F)Get item cost for store inventory windows.
		.word WindowVariableHeight;($A6D7)($A4B6)Calculate spell/inventory window height.
		.word WindowShowStat	;($A6D9)($A532)Show strength, agility max HP, max MP, attack pwr, defense pwr
		.word WindowAddToBuf	;($A6DB)($A543)Non-control character processing.
		.word WindowBuildVariable;($A6DD)($A4E7)Do all entries in variable height windows.
		.word WindowAddToBuf	;($A6DF)($A543)Non-control character processing.
		.word WindowAddToBuf	;($A6E1)($A543)Non-control character processing.
.word WindowAddToBuf	   ;($A543)Non-control character processing.

;----------------------------------------------------------------------------------------------------

AttributeVariableTable:
		.byte DisplayedStrength,   DisplayedAgility,   DisplayedAttack;($A6E5)
		.byte DisplayedDefense, DisplayedMaxHP, DisplayedMaxMP;($A6E8)

;----------------------------------------------------------------------------------------------------

IndexedMult:
		STA IndexedMultiplyByte ;($A6EB)
		LDA #$00				;($A6EE)
		STA IndexedMultiplyNum1 ;($A6F0)
STA IndexedMultiplyNum2		 ;
		* LSR IndexedMultiplyByte;($A6F6)
		BCC +				   ;($A6F9)The indexed register contains the multiplication word.
		LDA GenPtr00LB,X		;($A6FB)The accumulator contains the multiplication byte.
		CLC					 ;($A6FD)
		ADC IndexedMultiplyNum1 ;($A6FE)
		STA IndexedMultiplyNum1 ;($A701)
		LDA GenPtr00UB,X		;($A704)This function takes 2 bytes and multiplies them together.
		ADC IndexedMultiplyNum2 ;($A706)The 16-bit result is stored in the registers indexed by X.
		STA IndexedMultiplyNum2 ;($A709)
* ASL GenPtr00LB,X		;
		ROL GenPtr00UB,X		;($A70E)
		LDA IndexedMultiplyByte ;($A710)
BNE --				  ;
		LDA IndexedMultiplyNum1 ;($A715)
		STA GenPtr00LB,X		;($A718)
		LDA IndexedMultiplyNum2 ;($A71A)
		STA GenPtr00UB,X		;($A71D)
RTS					 ;

;----------------------------------------------------------------------------------------------------

GetBCDByte:
		TXA					 ;($A720)Save X
		PHA					 ;($A721)

		LDA #$00				;($A722)
		STA BCDResult		   ;($A724)
		LDX #$18				;($A726)
		* ASL BCDByte0		  ;($A728)
		ROL BCDByte1			;($A72A)
		ROL BCDByte2			;($A72C)
		ROL BCDResult		   ;($A72E)
		SEC					 ;($A730)Convert binary number in BCDByte0 to BCDByte2 to BCD.
		LDA BCDResult		   ;($A731)
SBC #$0A				;
		BCC +				   ;($A735)
		STA BCDResult		   ;($A737)
		INC BCDByte0			;($A739)
		* DEX				   ;($A73B)
		BNE --				  ;($A73C)

		PLA					 ;($A73E)
TAX					 ;Restore X and return.
		RTS					 ;($A740)

;----------------------------------------------------------------------------------------------------

GetBinBytesBCD:
		LDA #$00				;($A741)
STA BCDByte2			;
		STA BCDByte1			;($A745)Assume only one byte to convert to BCD.
		LDA GenWrd00LB,X		;($A747)
		STA BCDByte0			;($A749)Store byte.
		DEY					 ;($A74B)Y counts how many binary bytes to convert.
BEQ +				   ;
LDA GenWrd00UB,X		;Load second byte to convert if it is present.
STA BCDByte1			;
		* RTS				   ;($A752)

;----------------------------------------------------------------------------------------------------

ConvertToBCD:
LDY #$00				;No bytes converted yet.
		* JSR GetBCDByte		;($A755)($A720)Get BCD byte.

LDA BCDResult		   ;Store result byte in BCD buffer.
		STA TempBuffer,Y		;($A75A)

		INY					 ;($A75D)Is conversion done?
CPY SubBufLength		;
		BNE -				   ;($A761)If not, branch to convert another byte.
RTS					 ;

;----------------------------------------------------------------------------------------------------

ClearBCDLeadZeros:
		LDX SubBufLength		;($A764)Point to end of BCD buffer.
DEX					 ;

		* LDA TempBuffer,X	  ;($A768)Decrement through buffer replacing all
		BNE +				   ;($A76B)leading zeros with blank tiles.
LDA #TL_BLANK_TILE1	 ;
STA TempBuffer,X		;
		DEX					 ;($A772)
		BNE -				   ;($A773)At start of buffer? if not, branch to keep looking.
		* RTS				   ;($A775)

;----------------------------------------------------------------------------------------------------

ClearTempBuffer:
PHA					 ;
		TXA					 ;($A777)Save A and X.
		PHA					 ;($A778)

LDX #$0C				;
LDA #TL_BLANK_TILE1	 ;
		* STA TempBuffer,X	  ;($A77D)Load the entire 13 bytes of the buffer with blank tiles.
DEX					 ;
		BPL -				   ;($A781)

PLA					 ;
		TAX					 ;($A784)Restore X and A.
PLA					 ;
		RTS					 ;($A786)

;----------------------------------------------------------------------------------------------------

		JSR ClearAndSetBufferLen;($A787)($A7AE)Initialize buffer.

CPX #$FF				;End of description?
BEQ ++				  ;If so, branch to exit.

LDA DescBuf,X		   ;Load description index.

;----------------------------------------------------------------------------------------------------

LookupDescriptions:
STA WindowDescriptionIndex		;Save a copy of description table index.
		JSR ClearAndSetBufferLen;($A793)($A7AE)Initialize buffer.

LDA WindowDescriptionHalf		 ;If on first half of description, load Y with 0.
AND #$01				;
BEQ +				   ;If on second half of description, load Y with 1.
LDA #$01				;
* TAY					 ;

LDA WindowDescriptionIndex		;
		AND #$3F				;($A7A3)Remove upper 2 bits of index.
STA WindowDescriptionIndex		;

		BEQ +				   ;($A7A8)Is index 0? If so exit, no description to display.
JSR PrepIndexes		 ;($A7BD)Prep description index and DescriptionPointerTable index.
* RTS					 ;

;----------------------------------------------------------------------------------------------------

ClearAndSetBufferLen:
		JSR ClearTempBuffer	 ;($A7AE)($A7AE)Write blank tiles to buffer.
		LDA WindowDescriptionHalf;($A7B1)

LSR					 ;On first half of description? If so, buffer length
		BCC +				   ;($A7B5)is fine.  Branch to return.

LDA #$08				;
STA SubBufLength		;If on second half of description, buffer can be 1 byte smaller.
		* RTS				   ;($A7BC)

;----------------------------------------------------------------------------------------------------

PrepIndexes:
PHA					 ;Is item description on second table?
		CMP #$20				;($A7BE)
BCC +				   ;If not, branch to use indexes as is.

		PLA					 ;($A7C2)Need to recompute index for ItemNames21Table.
SBC #$1F				;Subtract 31(first table has 31 entries).
PHA					 ;

		TYA					 ;($A7C6)Need to recompute index into DescPtrTbl.
CLC					 ;
ADC #$02				;Add 2 to index to point to table 2.
TAY					 ;

* INY					 ;Add 2 to pointer for DescPtrTbl. Index is now ready for use.
		INY					 ;($A7CC)

TYA					 ;A is used as the index.
		JSR GetDescPtr		  ;($A7CE)($A823)Get pointer into description table.

		PLA					 ;($A7D1)Restore index into description table.
BEQ --				  ;Is index 0? If so, branch to exit. No description.
		JMP WindowBuildTempBuf  ;($A7D4)($A842)Place description in temp buffer.

;----------------------------------------------------------------------------------------------------

SecondDescHalf:
		LDA WindowDescriptionHalf;($A7D7)Get which description half we are currently on.
EOR #$01				;
BNE +				   ;Branch if value is set to 1.

		INC WindowThisDescription;($A7DE)Set value to 1.

* STA WindowDescriptionHalf		 ;Store the value of 1 for second half of description.
		RTS					 ;($A7E4)

;----------------------------------------------------------------------------------------------------

STA WorkTile			;Set the value in the working tile.
JMP BuildWndLine		;($A546)Transfer data into window line buffer.

;----------------------------------------------------------------------------------------------------

WindowGetSpellDesc:
PHA					 ;
		JSR ClearTempBuffer	 ;($A7EC)($A776)Write blank tiles to buffer.
PLA					 ;

		STA DescriptionEntry	;($A7F0)Store a copy of the description entry byte.
		CMP #$FF				;($A7F2)Has the end of the buffer been reached?
		BEQ +				   ;($A7F4)If so, branch to exit.

		LDA #$01				;($A7F6)Spell description table.
JSR GetDescPtr		  ;($A823)Get pointer into description table.
		LDA DescriptionEntry	;($A7FB)Get index into description table.
		JMP WindowBuildTempBuf  ;($A7FD)($A842)Place description in temp buffer.
* RTS					 ;

;----------------------------------------------------------------------------------------------------

GetEnDescHalf:
STA DescriptionEntry		   ;Save index into enemy descriptions.

		LDY #$07				;($A803)Start at index to first half of enemy names.
LDA WindowDescriptionHalf		 ;Get indicator to which name half to retreive.

LSR					 ;Do we want the first half of the name?
		BCC +				   ;($A809)If so branch.

		INY					 ;($A80B)We want second half of the enemy name. Increment index.

* LDA DescriptionEntry		   ;
PHA					 ;
		CMP #$33				;($A80F)This part of the code should never be executed because
		BCC +				   ;($A811)it is incrementing to another table entry for enemy
		PLA					 ;($A813)numbers greater than 51 but there are only 40 different
SBC #$32				;enemies in the entire game.
PHA					 ;
		INY					 ;($A817)

* TYA					 ;A now contains entry number into DescriptionPointerTable.
		JSR GetDescPtr		  ;($A819)($A823)Get pointer into description table.
JSR ClearTempBuffer	 ;($A776)Write blank tiles to buffer.
PLA
JMP WindowBuildTempBuf	 ;($A842)Place description in temp buffer.

;----------------------------------------------------------------------------------------------------

GetDescPtr:
		ASL					 ;($A823)*2. words in table are two bytes.
TAX					 ;

		LDA DescPtrTbl,X		;($A825)
STA DescPtrLB		   ;Get desired address from table below.
LDA DescPtrTbl+1,X	  ;Save in description pointer.
STA DescPtrUB		   ;
RTS					 ;

;----------------------------------------------------------------------------------------------------

DescriptionPointerTable:
.word WindowDataPointerTable	;($AF6C)Pointers to window type data bytes.
.word SpellNamesTable	  ;($BE56)Spell names.
.word ItemNames11Table	;($BAB7)Item descriptions, first table, first half.
.word ItemNames12Table	;($BBB7)Item descriptions, first table, second half.
.word ItemNames21Table	;($BB8F)Item descriptions, second table, first half.
.word ItemNames22Table	;($BC4F)Item descriptions, second table, second half.
.word WindowCostTblPtr	 ;($BE0E)Item costs, used in shop inventory windows.
.word EnemyNames1Table	   ;($BC70)Enemy names, first half.
.word EnemyNames2Table	   ;($BDA2)Enemy names, second half.

;----------------------------------------------------------------------------------------------------

WindowBuildTempBuf:
TAX					 ;Transfer description table index to X.
		LDY #$00				;($A843)

DescSearchOuterLoop:
		DEX					 ;($A845)Subtract 1 as 0 was used to for no description.
BEQ BaseDescFound	   ;At proper index? If so, no more searching required.

DescSearchInnerLoop:
		LDA (DescPtr),Y		 ;($A848)Get next byte in ROM.
		CMP #$FF				;($A84A)Is it an end of description marker?
BEQ NextDescription	 ;If so, branch to update pointers.

INY					 ;Increment index.
BNE DescSearchInnerLoop   ;Is it 0?
INC DescPtrUB		   ;If so, increment upper byte.
		BNE DescSearchInnerLoop ;($A853)Should always branch.

NextDescription:
		INY					 ;($A855)Increment index.
BNE DescSearchOuterLoop   ;Is it 0?
		INC DescPtrUB		   ;($A858)If so, increment upper byte.
		BNE DescSearchOuterLoop ;($A85A)Should always branch.

BaseDescFound:
* TYA					 ;
		CLC					 ;($A85D)
ADC DescPtrLB		   ;Set description pointer to base of the description.
STA DescPtrLB		   ;
BCC +				   ;
INC DescPtrUB		   ;

		* LDY #$00			  ;($A866)Zero out current index into description.
LDX SubBufLength		;Load buffer length.

LoadDescLoop:
		LDA (DescPtr),Y		 ;($A86B)Get next byte in description.
CMP #$FF				;Is it the end of description marker?
BEQ +				   ;If so, branch to end.

STA TempBuffer-1,X	  ;Store byte in the temp buffer.
		INY					 ;($A874)Increment ROM pointer.
DEX					 ;Decrement RAM pointer.
		BNE LoadDescLoop		;($A876)Is temp buffer full? If not, branch to get more.
		* RTS				   ;($A878)

;----------------------------------------------------------------------------------------------------

WindowCalcBufAddr:
JSR PrepPPUAddressCalc	  ;($A8AD)Prepare and calculate PPU address.

LDA WindowHeight		   ;Get window height in tiles.  Need to replace any end of text
STA RowsRemaining	   ;control characters with no-ops so window can be processed properly.

ControlCharSwapRow:
LDY #$00				;Start at beginning of window tile row.

		LDA WindowWidth		 ;($A883)Set remaining columns to window width.
STA _ColumnsRemaining	  ;

ControlCharSwapCol:
LDA (PPUBufferPointer),Y	   ;Was the end text control character found?
CMP #TXT_END2		   ;
BNE ControlNextCol		;If not, branch to check next window character.

LDA #TXT_NOP			;Replace text control character with a no-op.
STA (PPUBufferPointer),Y	   ;

ControlNextCol:
		INY					 ;($A892)Move to next columns.
DEC _ColumnsRemaining	  ;was that the last column?
BNE ControlCharSwapCol	;If not, branch to move to next column.

CLC					 ;
		LDA PPUAddrLB		   ;($A898)
		ADC #$20				;($A89A)Move buffer address to next row.
STA PPUAddrLB		   ;Handle carry, if necessary.
BCC ControlNextRow		;
INC PPUAddrUB		   ;

ControlNextRow:
DEC RowsRemaining	   ;Are there more rows to check?
		BNE ControlCharSwapRow  ;($A8A4)If so, branch.

		BRK					 ;($A8A6)Update sprites.
.byte $04, $07		  ;($B6DA)DoSprites, bank 0.

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.
RTS					 ;

PrepPPUAddressCalc:
LDA WindowColPos		   ;Convert column tile position into block position.
LSR					 ;
STA XPosFromLeft		;

LDA WindowRowPos		   ;Convert row tile position into block position.
		LSR					 ;($A8B4)
STA YPosFromTop		 ;
JMP CalcPPUBufAddr	  ;($C596)Calculate PPU address.

;----------------------------------------------------------------------------------------------------

GoldToBCD:
		LDA #$05				;($A8BA)Set results buffer length to 5.
		STA SubBufLength		;($A8BC)

		LDA GoldLB			  ;($A8BF)
STA BCDByte0			;
		LDA GoldUB			  ;($A8C3)Transfer gold value to conversion variables.
		STA BCDByte1			;($A8C5)
LDA #$00				;
		STA BCDByte2			;($A8C9)

		JSR ConvertToBCD		;($A8CB)($A753)Convert gold to BCD value.
JMP ClearBCDLeadZeros   ;($A764)Remove leading zeros from BCD value.

;----------------------------------------------------------------------------------------------------

WindowDoSelect:
LDA WindowBuildPhase	   ;Is the window in the first build phase?
		BMI WindowDoSelectExit  ;($A8D4)If so, branch to exit.

		JSR WindowInitializeSelect;($A8D6)($A918)Initialize window selection variables.

LDA #IN_RIGHT		   ;Disable right button retrigger.
		STA WindowBtnRetrig	 ;($A8DB)
		STA JoypadBtns		  ;($A8DE)Initialize joypad presses to a known value.

_WndDoSelectLoop:
		JSR WindowDoSelectLoop  ;($A8E0)($A8E4)Loop while selection window is active.

WindowDoSelectExit:
RTS					 ;Exit window selection and return results.

WindowDoSelectLoop:
JSR WindowGetButtons	   ;($A8ED)Keep track of player button presses.
JSR WindowProcessInput	 ;($A992)Update window based on user input.
JMP WindowDoSelectLoop	 ;($A8E4)Loop while selection window is active.

WindowGetButtons:
		JSR WaitForNMI		  ;($A8ED)($FF74)Wait for VBlank interrupt.
JSR UpdateCursorGFX	 ;($A96C)Update cursor graphic in selection window.

		LDA JoypadBtns		  ;($A8F3)Are any buttons being pressed?
BEQ SetRetrigger		;If not, branch to reset the retrigger.

LDA FrameCounter		;Reset the retrigger every 15 frames.
AND #$0F				;Is it time to reset the retrigger?
BNE NoRetrigger		 ;If not, branch.

SetRetrigger:
STA WindowBtnRetrig		;Clear all bits. Retrigger.

NoRetrigger:
		JSR GetJoypadStatus	 ;($A900)($C608)Get input button presses.
LDA WindowBtnRetrig		;Is there a retrigger event waiting to timeout?
BNE WindowGetButtons	   ;($A8ED)If so, branch to get any button presses.

		LDA WindowBtnRetrig	 ;($A908)
AND JoypadBtns		  ;Remove any button status bits that have chanegd.
STA WindowBtnRetrig		;

		EOR JoypadBtns		  ;($A910)Have any buttons changed?
		STA WindowBtnPresses	;($A912)
BEQ WindowGetButtons	   ;($A8ED)If so, branch to get button presses.
RTS					 ;

;----------------------------------------------------------------------------------------------------

WindowInitializeSelect:
		LDA #$00				;($A918)
		STA WindowColumn		;($A91A)
		STA WindowRow		   ;($A91C)
		STA WindowSelectionResults;($A91E)Clear various window selection control registers.
STA WindowCursorXPosition	   ;
STA WindowCursorYPosition	   ;
STA WindowButtonRetrigger		;

		LDA WindowColumns	   ;($A929)
LSR					 ;Use WindowColumns to determine how many columns there
		LSR					 ;($A92D)should be in multi column windows.  The only windows
LSR					 ;with multiple columns are the command windows and
		LSR					 ;($A92F)the alphabet window.  The command windows have 2
TAX					 ;columns while the alphabet window has 11.
		LDA NumberColumnTable,X ;($A931)
		STA WindowSelectionNumberColumns;($A934)

LDA WindowType		  ;Is this a message speed window?
		CMP #WINDOW_MSG_SPEED   ;($A93A)
BNE WindowSetCrsrHome	  ;If not, branch to skip setting message speed.

		LDX MessageSpeed		;($A93E)Use current message speed to set the cursor in the window.
		STX WindowRow		   ;($A940)Set the window row the same as the message speed(0,1 or 2).
		TXA					 ;($A942)
ASL					 ;Multiply by 2 and set the Y cursor position.
		STA WindowCursorYPosition;($A944)

WindowSetCrsrHome:
		LDA WindowCursorHome	;($A947)Save a copy of the cursor X,Y home position.
PHA					 ;

AND #$0F				;Save a copy of the home X coord but it is never used.
STA WindowUnused64F4	   ;

		CLC					 ;($A950)
ADC WindowCursorXPosition	   ;Convert home X coord from window coord to screen coord.
		STA WindowCursorXPosition;($A954)

		PLA					 ;($A957)Restore cursor X,Y home position.
AND #$F0				;
LSR					 ;
		LSR					 ;($A95B)Keep only Y coord and shift to lower nibble.
LSR					 ;
		LSR					 ;($A95D)
STA WindowCursorYHome	  ;This is the Y coord home position for the cursor.

ADC WindowCursorYPosition	   ;Convert home Y coord from window coord to screen coord.
		STA WindowCursorYPosition;($A964)

LDA #$05				;
STA FrameCounter		;Set framee counter to ensure cursor is initially visible.
RTS					 ;

;----------------------------------------------------------------------------------------------------

UpdateCursorGFX:
		LDX #TL_BLANK_TILE1	 ;($A96C)Set cursor tile as blank tile.

LDA FrameCounter		;Get lower 5 bits of the frame counter.
AND #$1F				;

CMP #$10				;Is count halfway through?
		BCS SetCursorTile	   ;($A974)If not, load cursor tile as right pointing arrow.

ArrowCursorGFX:
		LDX #TL_RIGHT_ARROW	 ;($A976)Set cursor tile as right pointing arrow.

SetCursorTile:
		STX PPUDataByte		 ;($A978)Store cursor tile.

		LDA WindowColumnPosition;($A97A)
		CLC					 ;($A97C)Calculate cursor X position on screen, in tiles.
ADC WindowCursorXPosition	   ;
		STA ScreenTextXCoordinate;($A980)

LDA WindowRowPosition		   ;
CLC					 ;Calculate cursor Y position on screen, in tiles.
		ADC WindowCursorYPosition;($A986)
STA ScreenTextYCoordinate	   ;

		JSR WindowCalcPPUAddr   ;($A98C)($ADC0)Calculate PPU address for window/text byte.
JMP AddPPUBufferEntry	  ;($C690)Add data to PPU buffer.

;----------------------------------------------------------------------------------------------------

WindowProcessInput:
		LDA WindowButtonPresses ;($A992)Get any buttons that have been pressed by the player.

LSR					 ;Has the A button been pressed?
		BCS WindowAPressed	  ;($A996)If so, branch.

		LSR					 ;($A998)Has the B button been pressed?
BCS WindowBPressed		 ;If so, branch.

LSR					 ;Skip select and start while in selection window.
		LSR					 ;($A99C)

LSR					 ;Has the up button been pressed?
		BCS WindowUpPressed	 ;($A99E)If so, branch.

LSR					 ;Has the down button been pressed?
		BCS WindowDownPressed   ;($A9A1)If so, branch.

		LSR					 ;($A9A3)Has the left button been pressed?
BCS WindowLeftPressed	  ;If so, branch.

		LSR					 ;($A9A6)Has no button been pressed?
BCC WindowEndUpPressed	 ;If so, branch to exit.

JMP WindowRightPressed	 ;($AAC8)Process right button press.

WindowLeftPressed:
		JMP WindowDoLeftPressed ;($A9AC)($AA67)Process left button press.

;----------------------------------------------------------------------------------------------------

WindowAPressed:
LDA #IN_A			   ;Disable A button retrigger.
STA WindowButtonRetrigger		;
		JSR WindowUpdateCrsrPos ;($A9B4)($AB35)Update cursor position on screen.

LDA #SFX_MENU_BTN	   ;Menu button SFX.
BRK					 ;
		.byte $04, $17		  ;($A9BA)($81A0)InitMusicSFX, bank 1.

		LDA WindowColumn		;($A9BC)
		STA _WindowColumn	   ;($A9BE)Make a working copy of the cursor column and row.
		LDA WindowRow		   ;($A9C0)
		STA _WindowRow		  ;($A9C2)

		JSR WindowCalcSelResult ;($A9C4)($AB64)Calculate selection result based on col and row.

PLA					 ;Pull last return address off of stack.
		PLA					 ;($A9C8)

LDA WindowSelectionResults	   ;Load the selection results into A.
RTS					 ;

;----------------------------------------------------------------------------------------------------

WindowBPressed:
		LDA #IN_B			   ;($A9CC)Disable B button retrigger.
		STA WindowButtonRetrigger;($A9CE)
		JSR WindowUpdateCrsrPos ;($A9D1)($AB35)Update cursor position on screen.

PLA					 ;Pull last return address off of stack.
PLA					 ;

LDA #WINDOW_ABORT		  ;Load abort indicator into A
STA WindowSelectionResults	   ;Store abort indicator in the selection results.
RTS					 ;

;----------------------------------------------------------------------------------------------------

WindowUpPressed:
		LDA #IN_UP			  ;($A9DB)Disable up button retrigger.
		STA WindowButtonRetrigger;($A9DD)

LDA WindowRow			  ;Is cursor already on the top row?
BEQ WindowEndUpPressed	 ;If so, branch to exit.  Nothing to do.

JSR WindowClearCursor	  ;($AB30)Blank out cursor tile.

		LDA WindowType		  ;($A9E7)Is this the SPELL1 window?
CMP #WND_SPELL1		 ;Not used in the game.
BEQ WndSpell1Up		 ;If so, branch for special cursor update.

		JSR WindowMoveCursorUp  ;($A9EE)($ABB2)Move cursor position up 1 row.
JSR WindowUpdateCrsrPos	;($AB35)Update cursor position on screen.

WindowEndUpPressed:
RTS					 ;Up button press processed. Return.

WndSpell1Up:
LDA #$03				;
		STA WindowCursorXPos	;($A9F7)Move cursor tile position to 3,2.
LDA #$02				;
STA WindowCursorYPos	   ;

LDA #$00				;Set cursor row position to 0.
STA WindowRow			  ;
		JMP WindowUpdateCrsrPos ;($AA03)($AB35)Update cursor position on screen.

;----------------------------------------------------------------------------------------------------

WindowDownPressed:
		LDA #IN_DOWN			;($AA06)Disable down button retrigger.
STA WindowBtnRetrig		;

		LDA WindowType		  ;($AA0B)Is this the SPELL1 window?
		CMP #WND_SPELL1		 ;($AA0E)Not used in the game.
BEQ WndSpell1Down	   ;If so, branch for special cursor update.

CMP #WINDOW_MSG_SPEED	  ;Is this the message speed window?
BNE WndDownCont1		;If not, branch to continue processing.

LDA WindowRow			  ;Is thos the last row of the message speed window?
CMP #$02				;
		BEQ WindowDownDone	  ;($AA1A)If so, branch to exit. Cannot go down anymore.

WndDownCont1:
		SEC					 ;($AA1C)Get window height.
		LDA WindowHeight		;($AA1D)Subtract 3 to get bottom most row the cursor can be on.
		SBC #$03				;($AA20)
		LSR					 ;($AA22)/2. Cursor moves 2 tile rows when going up or down.

		CMP WindowRow		   ;($AA23)Is the cursor on the bottom row?
BEQ WindowDownDone		 ;If so, branch to exit. Cannot go down anymore.

JSR WindowClearCursor	  ;($AB30)Blank out cursor tile as it has moved.

		LDA WindowType		  ;($AA2A)Is this the alphabet window?
CMP #WINDOW_ALPHBT		 ;
BNE WndDownCont2		;If not, branch to continue processing.

JSR WindowSpclMoveCrsr	 ;($AB3F)Move cursor to next position if next row is bottom.

WndDownCont2:
		LDA WindowCursorYPosition;($AA34)Is the cursor Y cord at the top?
BNE WndDownCont3		;If not, branch to continue processing.

LDA WindowCursorYHome	  ;Set cursor Y coord to the Y home position.
STA WindowCursorYPosition	   ;Is cursor Y position at 0?
		BNE WindowDownUpdate	;($AA3F)If not, branch.

WndDownCont3:
		CLC					 ;($AA41)
ADC #$02				;Update cursor Y position and cursor row.
		STA WindowCursorYPosition;($AA44)
		INC WindowRow		   ;($AA47)

WindowDownUpdate:
JSR WindowUpdateCrsrPos	;($AB35)Update cursor position on screen.

WindowDownDone:
RTS					 ;Down button press processed. Return.

WndSpell1Down:
		LDA WindowRow		   ;($AA4D)Is this the last row(not used)?
		CMP #$02				;($AA4F)
BEQ WindowDownDone		 ;If so, branch to exit.

JSR WindowClearCursor	  ;($AB30)Blank out cursor tile.
LDA #$02				;
STA WindowRow			  ;Update window row.

		LDA #$03				;($AA5A)Update cursor X pos.
		STA WindowCursorXPosition;($AA5C)

LDA #$06				;Update cursor Y pos.
STA WindowCursorYPosition	   ;
JMP WindowUpdateCrsrPos	;($AB35)Update cursor position on screen.

;----------------------------------------------------------------------------------------------------

WindowDoLeftPressed:
		LDA #IN_LEFT			;($AA67)Disable left button retrigger.
STA WindowButtonRetrigger		;

LDA WindowType		  ;Is this the SPELL1 window?
		CMP #WND_SPELL1		 ;($AA6F)Not used in the game.
		BEQ WndSpell1Left	   ;($AA71)If so, branch for special cursor update.

LDA WindowColumn			  ;Is cursor already at the far left?
BEQ WindowLeftDone		 ;If so, branch to exit. Cannot go left anymore.

		LDA WindowType		  ;($AA77)Is this the alphabet window?
CMP #WINDOW_ALPHBT		 ;
BNE WindowLeftUpdate	   ;If not, branch to continue processing.

LDA WindowRow			  ;Is this the bottom row of the alphabet window?
		CMP #$05				;($AA80)
		BNE WindowLeftUpdate	;($AA82)If not, branch to continue processing.

		LDA WindowColumn		;($AA84)Is the cursor pointing to END?
CMP #$09				;
BNE WindowLeftUpdate	   ;If not, branch to continue processing.

		LDA #$06				;($AA8A)Move cursor to point to BACK.
STA WindowColumn			  ;
		JSR WindowClearCursor   ;($AA8E)($AB30)Blank out cursor tile.

		LDA #$0D				;($AA91)Prepare new cursor X position.
		BNE WindowLeftUpdateFinish;($AA93)

WindowLeftUpdate:
		JSR WindowClearCursor   ;($AA95)($AB30)Blank out cursor tile.
		DEC WindowColumn		;($AA98)Decrement cursor column position.

		LDA WindowColumns	   ;($AA9A)
		AND #$0F				;($AA9D)Get number of tiles per column.
STA WindowColumnLowerByte			;

LDA WindowCursorXPosition	   ;
		SEC					 ;($AAA4)Subtract tiles to get final cursor X position.
SBC WindowColumnLowerByte			;

WindowLeftUpdateFinish:
STA WindowCursorXPosition	   ;Update cursor X position.
JSR WindowUpdateCrsrPos	;($AB35)Update cursor position on screen.

WindowLeftDone:
RTS					 ;Left button press processed. Return.

WndSpell1Left:
		LDA WindowRow		   ;($AAAE)Is this the 4th row in the SPELL1 window?
CMP #$03				;Not used in game.
BEQ WindowLeftDone		 ;If so, branch to exit.

		JSR WindowClearCursor   ;($AAB4)($AB30)Blank out cursor tile.
LDA #$03				;
STA WindowRow			  ;Update cursor row.

LDA #$01				;Update cursor X position.
		STA WindowCursorXPosition;($AABD)

LDA #$04				;Update cursor Y position.
		STA WindowCursorYPosition;($AAC2)
		JMP WindowUpdateCrsrPos ;($AAC5)($AB35)Update cursor position on screen.

;----------------------------------------------------------------------------------------------------

WindowRightPressed:
LDA #IN_RIGHT		   ;Disable right button retrigger.
STA WindowButtonRetrigger		;

		LDA WindowType		  ;($AACD)Is this the SPELL1 window?
CMP #WND_SPELL1		 ;Not used in the game.
		BEQ WndSpell1Right	  ;($AAD2)If so, branch for special cursor update.

LDA WindowColumns		  ;Is there only a single column in this window?
BEQ WindowEndRghtPressed   ;If so, branch to exit. Nothing to process.

LDA WindowType		  ;Is this the alphabet window?
		CMP #WINDOW_ALPHBT	  ;($AADC)
		BNE WndRightCont1	   ;($AADE)If not, branch to continue processing.

		LDA WindowRow		   ;($AAE0)Is this the bottom row of the alphabet window?
		CMP #$05				;($AAE2)
BNE WndRightCont1	   ;If not, branch to continue processing.

		LDA WindowColumn		;($AAE6)Is the cursor pointing to BACK or END?
		CMP #$06				;($AAE8)
		BCC WndRightCont1	   ;($AAEA)If not, branch to continue processing.

BNE WindowEndRghtPressed   ;Is the cursor pointing to BACK? If not, must be END. Done.

JSR WindowClearCursor	  ;($AB30)Blank out cursor tile.
		LDA #$09				;($AAF1)
		STA WindowColumn		;($AAF3)Move cursor to point to END.

		LDA #$13				;($AAF5)Prepare new cursor X position.
		BNE WindowRightUpdateFinish;($AAF7)

WndRightCont1:
		LDX WindowSelectionNumberColumns;($AAF9)Is cursor in right most column?
		DEX					 ;($AAFC)
CPX WindowColumn			  ;
BEQ WindowEndRghtPressed   ;If so, branch to exit. Nothing to process.

JSR WindowClearCursor	  ;($AB30)Blank out cursor tile.
		INC WindowColumn		;($AB04)Increment cursor column position.

LDA WindowColumns		  ;Get number of tiles per column for this window.
AND #$0F				;

CLC					 ;Use tiles per column from above to update cursor X pos.
		ADC WindowCursorXPosition;($AB0C)

WindowRightUpdateFinish:
STA WindowCursorXPosition	   ;Update cursor X position.
JSR WindowUpdateCrsrPos	;($AB35)Update cursor position on screen.

WindowEndRghtPressed:
RTS					 ;Right button press processed. Return.

WndSpell1Right:
		LDA WindowRow		   ;($AB16)Is this the 2nd row in the SPELL1 window?
		CMP #$01				;($AB18)Not used in game.
		BEQ WindowEndRghtPressed;($AB1A)If so, branch to exit.

		JSR WindowClearCursor   ;($AB1C)($AB30)Blank out cursor tile.
LDA #$01				;
STA WindowRow			  ;Update cursor row.

LDA #$07				;Update cursor X position.
STA WindowCursorXPosition	   ;

LDA #$04				;Update cursor Y position.
STA WindowCursorYPosition	   ;
		JMP WindowUpdateCrsrPos ;($AB2D)($AB35)Update cursor position on screen.

;----------------------------------------------------------------------------------------------------

WindowClearCursor:
LDX #TL_BLANK_TILE1	 ;Replace cursor with a blank tile.
		JMP SetCursorTile	   ;($AB32)($A978)Set cursor tile to blank tile.

;----------------------------------------------------------------------------------------------------

WindowUpdateCrsrPos:
		LDA #$05				;($AB35)Set cursor to arrow tile for 10 frames.
		STA FrameCounter		;($AB37)
JSR ArrowCursorGFX	  ;($A976)Set cursor graphic to the arrow.
JMP WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

;----------------------------------------------------------------------------------------------------

WindowSpclMoveCrsr:
LDA WindowRow			  ;Is this the second to bottom row?
CMP #$04				;
		BNE WindowEndUpdateCrsr ;($AB43)If not, branch to exit.

		LDA WindowColumn		;($AB45)Is this the 8th column?
CMP #$07				;
BEQ WindowSetCrsrBack	  ;If so, branch to set cursor to BACK selection.

CMP #$08				;is this the 9th, 10th or 11th column?
BCC WindowEndUpdateCrsr	;If so, branch to set cursor to END selection.

LDA #$09				;Set cursor to END selection in alphabet window.
STA WindowColumn			  ;
LDA #$13				;
STA WindowCursorXPosition	   ;
BNE WindowEndUpdateCrsr	;Branch always.

WindowSetCrsrBack:
LDA #$06				;
		STA WindowColumn		;($AB5C)Set cursor to BACK selection in alphabet window.
		LDA #$0D				;($AB5E)
		STA WindowCursorXPosition;($AB60)

WindowEndUpdateCrsr:
RTS					 ;Cursor update complete. Return.

;----------------------------------------------------------------------------------------------------

WindowCalcSelResult:
		LDA WindowType		  ;($AB64)Is this the alphabet window for entering name?
		CMP #WINDOW_ALPHBT	  ;($AB67)
BEQ WindowCalcAlphaResult  ;If so, branch for special results processing.

		LDA _WindowColumn	   ;($AB6B)
STA WindowColumnLowerByte			;Store number of columns as first multiplicand.
LDA #$00				;
		STA WindowColumnUpperByte;($AB71)

SEC					 ;
LDA WindowHeight		   ;
SBC #$03				;Value of first multiplicand is:
LSR					 ;(window height in tiles-3)/2 + 1.
TAX					 ;
INX					 ;
		TXA					 ;($AB7C)

LDX #WindowColumnLowerByte			;Multiply values for selection result.
JSR IndexedMult		 ;($A6EB)Get first part of selection result.

		LDA WindowColumnLowerByte;($AB82)
		CLC					 ;($AB84)
ADC _WindowRow			 ;Add the window row to get final value of selection result.
STA WindowSelectionResults	   ;
RTS					 ;

WindowCalcAlphaResult:
		LDA _WindowRow		  ;($AB8A)Get current window row selected.

		LDX WindowColumns	   ;($AB8C)Branch never.
BEQ WindowSetAlphaResult   ;

AND #$0F				;
STA WindowColumnLowerByte			;Save only lower 4 bits of window row.
LDA #$00				;
STA WindowColumnUpperByte			;

LDX #WindowColumnLowerByte			;Multiply the current selected row
		LDA WindowSelectionNumberColumns;($AB9B)with the total window columns.
JSR IndexedMult		 ;($A6EB)Get multiplied value.

		LDA WindowColumnLowerByte;($ABA1)
CLC					 ;Add current selected column to result for final answer.
		ADC _WindowColumn	   ;($ABA4)

WindowSetAlphaResult:
		STA WindowSelectionResults;($ABA6)Return alphabet window selection result.
		RTS					 ;($ABA8)

		LDA WindowColumn		;($ABA9)
		STA _WindowColumn	   ;($ABAB)
		LDA WindowRow		   ;($ABAD)Reset working copies of the window column and row variables.
STA _WindowRow			 ;
RTS					 ;

;----------------------------------------------------------------------------------------------------

WindowMoveCursorUp:
		LDA WindowCursorYPosition;($ABB2)
SEC					 ;Decrease Cursor tile position in the Y direction by 2.
		SBC #$02				;($ABB6)
		STA WindowCursorYPosition;($ABB8)

DEC WindowRow			  ;Decrease Cursor row position by 1.
RTS					 ;

;----------------------------------------------------------------------------------------------------

;This table contains the number of columns for selection windows with more than a single column.

NumberColumnTable:
		.byte $02			   ;($ABBE)Command windows columns.
.byte $0B			   ;Alphabet window columns.

;----------------------------------------------------------------------------------------------------

		LDA #$00				;($ABC0)Unused window function.
		BNE WindowShowHide+2	;($ABC2)

;----------------------------------------------------------------------------------------------------

WindowShowHide:
		LDA #$00				;($ABC4)Zero out A.
		JSR WindowDoRow		 ;($ABC6)($ABCC)Fill PPU buffer with window row contents.
		JMP WindowUpdateTiles   ;($ABC9)($ADFA)Update background tiles next NMI.

WindowDoRow:
PHA					 ;Save A. Always 0.
		.byte $AD, $03, $00	 ;($ABCD)LDA $0003(PPUEntryCount)Is PPU buffer empty?
		BEQ WindowDoRowReady	;($ABD0)If so, branch to fill it with window row data.

		JSR WindowUpdateTiles   ;($ABD2)($ADFA)Wait until next NMI for buffer to be empty.

WindowDoRowReady:
LDA #$00				;Zero out unused variable.
		STA WindowUnused64AB	;($ABD7)

PLA					 ;Restore A. Always 0.
		JSR WindowStartRow	  ;($ABDB)($AD10)Set nametable and X,Y start position of window line.

		LDA #$00				;($ABDE)
		STA WindowLineBufferIndex;($ABE0)Zero buffer indexes.
STA WindowAtrbBufIndex	 ;

LDA WindowWidthTemp		;
PHA					 ;
AND #$F0				;Will always set WindowBlkTileRow to 2.
		LSR					 ;($ABEC)Two rows of tiles in a window row.
LSR					 ;
		LSR					 ;($ABEE)
STA WindowBlkTileRow	   ;

PLA					 ;
		AND #$0F				;($ABF3)Make a copy of window width.
		ASL					 ;($ABF5)
STA _WndWidth		   ;

		STA WindowUnused64AE	;($ABF9)Not used.
.byte $AE, $04, $00	 ;LDX $0004(PPUBufCount)Get index for next buffer entry.

WindowRowLoop:
LDA PPUAddrUB		   ;
STA WindowPPUAddrUB		;Get a copy of the address to start of window row(block).
		LDA PPUAddrLB		   ;($AC04)
		STA WindowPPUAddrLB	 ;($AC06)

		AND #$1F				;($AC09)Get row offset on nametable for start of window
STA WindowNTRowOffset	  ;(row is 32 tiles long, 0-31).

		LDA #$20				;($AC0E)Each row is 32 tiles.
		SEC					 ;($AC10)
SBC WindowNTRowOffset	  ;Calculate the difference between start of window
STA WindowThisNTRow		;row and end of nametable row.

LDA _WndWidth		   ;Subtract window width from difference above
		SEC					 ;($AC1A)If the value is negative, the window spans
SBC WindowThisNTRow		;both nametables.
		STA WindowNextNTRow	 ;($AC1E)
BEQ WindowNoCrossNT		;Does window run to end of this NT? if so, branch.

BCS WindowCrossNT		  ;Does window span both nametables? if so, branch.

WindowNoCrossNT:
LDA _WndWidth		   ;Entire window row is on this nametable.
STA WindowThisNTRow		;Store number of tiles to process on this nametable.
		JMP WindowSingleNT	  ;($AC2B)($AC51)Window is contained on a single nametable.

WindowCrossNT:
JSR WindowLoadRowBuf	   ;($AC83)Load buffer with window row(up to overrun).

		LDA WindowPPUAddrUB	 ;($AC31)
		EOR #$04				;($AC34)Change upper address byte to other nametable.
STA WindowPPUAddrUB		;

LDA WindowPPUAddrLB		;
		AND #$1F				;($AC3C)Save lower 5 bits of lower PPU address.
		STA WindowNTRowOffset   ;($AC3E)

LDA WindowPPUAddrLB		;
		SEC					 ;($AC44)Subtract the saved value above to set the nametable->
SBC WindowNTRowOffset	  ;address to the beginning of the nametable row.
		STA WindowPPUAddrLB	 ;($AC48)

LDA WindowNextNTRow		;Completed window row portion on first nametable.
		STA WindowThisNTRow	 ;($AC4E)Tansfer remainder for next nametable calcs.

WindowSingleNT:
JSR WindowLoadRowBuf	   ;($AC83)Load buffer with window row data.

		LDA PPUAddrUB		   ;($AC54)
		AND #$FB				;($AC56)Is there at least 2 full rows before bottom of nametable?
CMP #$23				;If so, branch to increment row. Won't hit attribute table.
BCC WindowIncPPURow		;

LDA PPUAddrLB		   ;Is there 1 row before bottom of nametable?
CMP #$A0				;If so, branch to increment row. Won't hit attribute table.
		BCC WindowIncPPURow	 ;($AC60)

		AND #$1F				;($AC62)Save row offset for next row.
		STA PPUAddrLB		   ;($AC64)

LDA PPUAddrUB		   ;Address is off bottom of nametable. discard lower bits
AND #$FC				;to wrap window around to the top of the nametable.
JMP UpdateNTAddr		;Update nametable address.

WindowIncPPURow:
		LDA PPUAddrLB		   ;($AC6D)
		CLC					 ;($AC6F)
ADC #$20				;Add 32 to PPU address to move to next row.
STA PPUAddrLB		   ;32 blocks per row.
		LDA PPUAddrUB		   ;($AC74)
		ADC #$00				;($AC76)

UpdateNTAddr:
		STA PPUAddrUB		   ;($AC78)Update PPU upper PPU address byte.

		DEC WindowBlkTileRow	;($AC7A)Does the second row of tiles still need to be done?
		BNE WindowRowLoop	   ;($AC7D)If so, branch to do second half of window row.

.byte $8E, $04, $00	 ;STX $0004(PPUBufCount)Update buffer index.
RTS					 ;

;----------------------------------------------------------------------------------------------------

WindowLoadRowBuf:
LDA WindowPPUAddrUB		;Get upper ddress byte.
ORA #$80				;MSB set = PPU control byte(counter next byte).
STA BlockRAM,X		  ;Store in buffer.

		LDA WindowThisNTRow	 ;($AC8B)Load counter value for remainder of this NT row.
		STA BlockRAM+1,X		;($AC8E)

		LDA WindowPPUAddrLB	 ;($AC91)Load lower PPU address byte into buffer.
		STA BlockRAM+2,X		;($AC94)

INX					 ;
INX					 ;Move to data portion of buffer.
		INX					 ;($AC99)

LDA WindowThisNTRow		;Save a copy of the count of tiles on this NT.
		PHA					 ;($AC9D)

LDY WindowLineBufferIndex	 ;Load index into line buffer.

WindowBufLoadLoop:
LDA WindowLineBuffer,Y		;
		STA BlockRAM,X		  ;($ACA4)Load line buffer into PPU buffer.
		INX					 ;($ACA7)
INY					 ;
		DEC WindowThisNTRow	 ;($ACA9)Is there more buffer data for this nametable?
BNE WindowBufLoadLoop	  ;If so, branch to get the next byte.

STY WindowLineBufferIndex	 ;Update line buffer index.

		PLA					 ;($ACB1)/2. Use this now to load attribute table bytes.
LSR					 ;1 attribute table byte per 2X2 block.
		STA WindowThisNTRow	 ;($ACB3)

LDA WindowBlkTileRow	   ;Is this the second tile row that just finished?
		AND #$01				;($ACB9)If so, load attribute table data.
BEQ WindowLoadRowBufEnd	;Else branch to skip attribute table data for now.

LDY WindowAtrbBufIndex	 ;
		LDA WindowPPUAddrUB	 ;($ACC0)Prepare to calculate attribute table addresses
STA _WndPPUAddrUB	   ;by first starting with the nametable addresses.
		LDA WindowPPUAddrLB	 ;($ACC6)
STA _WndPPUAddrLB	   ;

WindowLoadAttribLoop:
		TXA					 ;($ACCC)
PHA					 ;Save BlockRAM index and AttributeTblBuf index on stack.
		TYA					 ;($ACCE)
PHA					 ;

LDA WindowPPUAddrUB		;Save upper byte of PPU address on stack.
		PHA					 ;($ACD3)

LDA AttributeTblBuf,Y	  ;Get attibute table bits from buffer.
		JSR WindowCalcAttribAddr;($ACD7)($AD36)Update attribute table values.
STA WindowAtribDat		 ;Save a copy of the completed attribute table data byte.

		PLA					 ;($ACDD)Restore upper byte of PPU address from stack.
STA WindowPPUAddrUB		;

		PLA					 ;($ACE1)
TAY					 ;Restore BlockRAM index and AttributeTblBuf index from stack.
		PLA					 ;($ACE3)
TAX					 ;

		LDA WindowAtribAdrUB	;($ACE5)
STA BlockRAM,X		  ;
INX					 ;Save attribute table data address in buffer.
LDA WindowAtribAdrLB	   ;
STA BlockRAM,X		  ;

		INX					 ;($ACF2)
LDA WindowAtribDat		 ;Save attribute table data byte in buffer.
		STA BlockRAM,X		  ;($ACF6)

INX					 ;Increment BlockRAM index and AttributeTblBuf index.
		INY					 ;($ACFA)

INC _WndPPUAddrLB	   ;Increment to next window block.
		INC _WndPPUAddrLB	   ;($ACFE)

.byte $EE, $03, $00	 ;INC $0003(PPUEntryCount)Update buffer entry count.

		DEC WindowThisNTRow	 ;($AD04)Is there still more attribute table data to load?
BNE WindowLoadAttribLoop   ;If so, branch to do more.

STY WindowAtrbBufIndex	 ;Update attribute table buffer index.

WindowLoadRowBufEnd:
		.byte $EE, $03, $00	 ;($AD0C)INC $0003(PPUEntryCount)Update buffer entry count.
RTS					 ;

;----------------------------------------------------------------------------------------------------

WindowStartRow:
PHA					 ;Save A. Always 0.
JSR WindowGetRowStartPos   ;($AD1F)Load X and Y start position of window row.
		PLA					 ;($AD14)Restore A. Always 0.
BNE WindowNTSwap		   ;Branch never.
RTS					 ;

WindowNTSwap:
		LDA PPUAddrUB		   ;($AD18)
		EOR #$04				;($AD1A)Never used. Swaps between #$20 and #$24.
		STA PPUAddrUB		   ;($AD1C)
		RTS					 ;($AD1E)

;----------------------------------------------------------------------------------------------------

WindowGetRowStartPos:
LDA _WndPosition		;
		ASL					 ;($AD22)Get start X position in tiles
AND #$1E				;relative to screen for window row.
STA ScreenTextXCoordinate	   ;

		LDA _WndPosition		;($AD28)
LSR					 ;
		LSR					 ;($AD2C)Get start Y position in tiles
		LSR					 ;($AD2D)relative to screen for window row.
AND #$1E				;
STA ScreenTextYCoordinate	   ;
JMP WindowCalcPPUAddr	  ;($ADC0)Calculate PPU address for window/text byte.

;----------------------------------------------------------------------------------------------------

WindowCalcAttribAddr:
STA WindowAttribVal		;Save a copy of the attibute table value.

		LDA #$1F				;($AD39)Get tile offset in row and divide by 4. This gives
		AND _WndPPUAddrLB	   ;($AD3B)a value of 0-7. There are 8 bytes of attribute
LSR					 ;table data per nametable row. WindowPPUAddrUB now has
LSR					 ;the byte number in the attribute table for this
STA WindowPPUAddrUB		;row offset.

LDA #$80				;
AND _WndPPUAddrLB	   ;
		LSR					 ;($AD48)Get MSB of lower address byte and shift it to the
LSR					 ;lower nibble.  This cuts the rows of the attribute
		LSR					 ;($AD4A)table in half.  There are now 4 possible addreses
LSR					 ;in the attribute table that correspond to the target
		ORA WindowPPUAddrUB	 ;($AD4C)in the nametable.
STA WindowPPUAddrUB		;

LDA #$03				;
AND _WndPPUAddrUB	   ;Getting the 2 LSB of the upper address selects the
ASL					 ;proper byte from the 4 remaining from above. Move
		ASL					 ;($AD58)The 2 bits to the upper nibble and or them with the
		ASL					 ;($AD59)lower byte of the base address of the attribute
ASL					 ;table.  Finally, or the result with the other
		ORA #$C0				;($AD5B)result to get the final result of the lower address
		ORA WindowPPUAddrUB	 ;($AD5D)byte of the attribute table byte.
STA WindowAtribAdrLB	   ;

		LDX #AT_ATRBTBL0_UB	 ;($AD63)Assume we are working on nametable 0.
		LDA _WndPPUAddrUB	   ;($AD65)
CMP #NT_NAMETBL1_UB	 ;Are we actually working on nametable 1?
BCC WindowSetAtribUB	   ;If not, branch to save upper address byte.

LDX #AT_ATRBTBL1_UB	 ;Set attribute table upper address for nametable 1.

WindowSetAtribUB:
		STX WindowAtribAdrUB	;($AD6E)Save upper address byte for the attribute table.

LDA _WndPPUAddrLB	   ;
		AND #$40				;($AD74)
		LSR					 ;($AD76)Get bit 6 of address and move to lower nibble.
		LSR					 ;($AD77)This sets the upper bit for offset shifting.
LSR					 ;
		LSR					 ;($AD79)
STA AtribBitsOfst	   ;

		LDA _WndPPUAddrLB	   ;($AD7D)
AND #$02				;Get bit 1 of lower address bit.
ORA AtribBitsOfst	   ;This sets the lower bit for offset shifting.
STA AtribBitsOfst	   ;

LDA WindowAtribAdrLB	   ;Set attrib table pointer to lower byte of attrib table address.
		STA AttributePtrLB	  ;($AD8B)

LDA WindowAtribAdrUB	   ;Set upper byte for attribute table buffer. The atrib
AND #$07				; table buffer starts at either $0300 or $0700, depending
STA AttributePtrUB		 ;on the active nametable.

LDA EnemyNumber			;Is player fighting the end boss?
CMP #EN_DRAGONLORD2	 ;If so, force atribute table buffer to base address $0700.
BNE ModAtribByte		;If not, branch to get attribute table byte.

LDA #$07				;Force atribute table buffer to base address $0700.
		STA AttributePtrUB	  ;($AD9C)

ModAtribByte:
LDY #$00				;
		LDA (AttributePtr),Y	;($ADA0)Get attribute byte to modify from buffer.
		STA AttributeByte	   ;($ADA2)

		LDA #$03				;($ADA5)Initialize bitmask.
		LDY AtribBitsOfst	   ;($ADA7)Set shift amount.
BEQ AddNewAtribVal	  ;Is there no shifting needed? If none, branch. done.

AtribValShiftLoop:
ASL					 ;Shift bitmask into proper position.
		ASL WindowAttribVal	 ;($ADAD)Shift new attribute bits into proper position.
DEY					 ;Is shifting done?
		BNE AtribValShiftLoop   ;($ADB1)If not branch to shift by another bit.

AddNewAtribVal:
EOR #$FF				;Clear the two bits to be modified.
AND AttributeByte		  ;

		ORA WindowAttribVal	 ;($ADB8)Insert the 2 new bits.
		LDY #$00				;($ADBB)

		STA (AttributePtr),Y	;($ADBD)Save attribute table data byte back into the buffer.
		RTS					 ;($ADBF)

;----------------------------------------------------------------------------------------------------

WindowCalcPPUAddr:
LDA ActiveNmTbl		 ;
ASL					 ;
		ASL					 ;($ADC3)Calculate base upper address byte of current
AND #$04				;name table. It will be either #$20 or #$24.
ORA #$20				;
STA PPUAddrUB		   ;

LDA ScreenTextXCoordinate	   ;
		ASL					 ;($ADCD)*8. Convert X tile coord to X pixel coord.
ASL					 ;
		ASL					 ;($ADCF)

CLC					 ;Add scroll offset.  It is a pixel offset.
		ADC ScrollX			 ;($ADD1)

		STA PPUAddrLB		   ;($ADD3)The X coordinate in pixels is now calculated.
		BCC WindowAddY		  ;($ADD5)Did X position go past nametable boundary? If not, branch.

		LDA PPUAddrUB		   ;($ADD7)Window tile ran beyond end of nametable.
		EOR #$04				;($ADD9)Move to next nametable to continue window line.
		STA PPUAddrUB		   ;($ADDB)

WindowAddY:
LDA ScrollY			 ;
		LSR					 ;($ADDF)/8. Convert Y scroll pixel coord to tile coord.
LSR					 ;
		LSR					 ;($ADE1)

CLC					 ;Add Tile Y coord of window. A now
		ADC ScreenTextYCoordinate;($ADE3)contains Y coordinate in tiles.

		CMP #$1E				;($ADE6)Did Y position go below nametable boundary?
		BCC WindowAddressCombine;($ADE8)If not, branch.

		SBC #$1E				;($ADEA)Window tile went below end of nametable. Loop back to top.

WindowAddressCombine:
LSR					 ;A is upper byte of result and PPUAddrLB is lower byte.
ROR PPUAddrLB		   ;
		LSR					 ;($ADEF)Need to divide by 8 because X coord is still in pixel
ROR PPUAddrLB		   ;coords.
LSR					 ;
		ROR PPUAddrLB		   ;($ADF3)Result is now calculated with respect to screen.

		ORA PPUAddrUB		   ;($ADF5)Combine A with PPUAddrUB to convert from
		STA PPUAddrUB		   ;($ADF7)screen coord to nametable coords.
		RTS					 ;($ADF9)

;----------------------------------------------------------------------------------------------------

WindowUpdateTiles:
LDA #$80				;Indicate background tiles need to be updated.
STA UpdateBGTiles	   ;
		JMP WaitForNMI		  ;($ADFF)($FF74)Wait for VBlank interrupt.

;----------------------------------------------------------------------------------------------------

WindowEnterName:
JSR InitNameWindow	  ;($AE2C)Initialize window used while entering name.
		JSR WindowShowUnderscore;($AE05)($AEB8)Show underscore below selected letter in name window.
JSR WindowDoSelect		 ;($A8D1)Do selection window routines.

ProcessNameLoop:
		JSR WindowProcessChar   ;($AE0B)($AE53)Process name character selected by the player.
JSR WindowMaxNameLength	;($AEB2)Set carry if max length name has been reached.
		BCS WindowStorePlyrName ;($AE11)Has player finished entering name? If so, branch to exit loop.
		JSR _WndDoSelectLoop	;($AE13)($A8E0)Wait for player to select the next character.
		JMP ProcessNameLoop	 ;($AE16)($AE0B)Loop to get name selected by player.

WindowStorePlyrName:
LDX #$00				;Set index to 0 for storing the player's name.

StoreNameLoop:
LDA TempBuffer,X		;Save the 8 characters of the player's name to the name registers.
		STA DispName0,X		 ;($AE1E)
		LDA TempBuffer+4,X	  ;($AE20)
STA DispName4,X		 ;
		INX					 ;($AE26)
CPX #$04				;Have all 8 characters been saved?
BNE StoreNameLoop	   ;If not, branch to save the next 2.
RTS					 ;

;----------------------------------------------------------------------------------------------------

InitNameWindow:
		LDA #$00				;($AE2C)
STA WindowNameIndex		;Zero out name variables.
STA WindowUnused6505	   ;

LDA #WINDOW_NM_ENTRY	   ;Show name entry window.
JSR ShowWindow		  ;($A194)Display window.

LDA #WINDOW_ALPHBT		 ;Show alphabet window.
JSR ShowWindow		  ;($A194)Display window.

		LDA #$12				;($AE3E)Set window columns to 18. Special value for the alphabet window.
		STA WindowColumns	   ;($AE40)

LDA #$21				;Set starting cursor position to 2,1.
		STA WindowCursorHome	;($AE45)

LDA #TL_BLANK_TILE2	 ;Prepare to clear temp buffer.
		LDX #$0C				;($AE4A)

ClearNameBufLoop:
		STA TempBuffer,X		;($AE4C)Place blank tile value in temp buffer.
DEX					 ;
		BPL ClearNameBufLoop	;($AE50)Have 12 values been written to the buffer?
		RTS					 ;($AE52)If not, branch to write another.

;----------------------------------------------------------------------------------------------------

WindowProcessChar:
CMP #WINDOW_ABORT		  ;Did player press the B button?
		BEQ WindowDoBackspace   ;($AE55)If so, back up 1 character.

		CMP #$1A				;($AE57)Did player select character A-Z?
BCC WindowUpperCaseConvert   ;If so, branch to covert to nametables values.

CMP #$21				;Did player select symbol -'!?() or _?
BCC WndSymbConvert1	 ;If so, branch to covert to nametables values.

CMP #$3B				;Did player select character a-z?
BCC WindowLowerCaseConvert   ;If so, branch to covert to nametables values.

CMP #$3D				;Did player select symbol , or .?
		BCC WndSymbConvert2	 ;($AE65)If so, branch to covert to nametables values.

		CMP #$3D				;($AE67)Did player select BACK?
		BEQ WindowDoBackspace   ;($AE69)If so, back up 1 character.

LDA #$08				;Player must have selected END.
STA WindowNameIndex		;Set name index to max value to indicate the end.
		RTS					 ;($AE70)

WindowUpperCaseConvert:
CLC					 ;
		ADC #TXT_UPR_A		  ;($AE72)Add value to convert to nametable character.
		BNE WindowUpdateName	;($AE74)

WindowLowerCaseConvert:
		SEC					 ;($AE76)
SBC #$17				;Subtract value to convert to nametable character.
BNE WindowUpdateName	   ;

WndSymbConvert1:
		TAX					 ;($AE7B)
LDA SymbolConvTbl-$1A,X ;Use table to convert to nametable character.
BNE WindowUpdateName	   ;

WndSymbConvert2:
TAX					 ;
		LDA SymbolConvTbl-$34,X ;($AE82)Use table to convert to nametable character.
BNE WindowUpdateName	   ;

WindowDoBackspace:
LDA WindowNameIndex		;Is the name index already 0?
BEQ WndProcessCharEnd1  ;If so, branch to exit, can't go back any further.

JSR WindowHideUnderscore   ;($AEBC)Remove underscore character from screen.
DEC WindowNameIndex		;Move underscore back 1 character.
		JSR WindowShowUnderscore;($AE92)($AEB8)Show underscore below selected letter in name window.

WndProcessCharEnd1:
RTS					 ;End character processing.

WindowUpdateName:
		PHA					 ;($AE96)Save name character on stack.
JSR WindowHideUnderscore   ;($AEBC)Remove underscore character from screen.

		PLA					 ;($AE9A)Restore name character and add it to the buffer.
		LDX WindowNameIndex	 ;($AE9B)
STA TempBuffer,X		;
		JSR WindowNameCharYPos  ;($AEA1)($AEC2)Place selected name character on screen.

INC WindowNameIndex		;Increment index for player's name.
LDA WindowNameIndex		;
CMP #$08				;Have 8 character been entered for player's name?
		BCS WndProcessCharEnd2  ;($AEAC)If so, branch to end.

		JSR WindowShowUnderscore;($AEAE)($AEB8)Show underscore below selected letter in name window.

WndProcessCharEnd2:
		RTS					 ;($AEB1)End character processing.

;----------------------------------------------------------------------------------------------------

WindowMaxNameLength:
LDA WindowNameIndex		;Have 8 name characters been inputted?
		CMP #$08				;($AEB5)
RTS					 ;If so, set carry.

;----------------------------------------------------------------------------------------------------

WindowShowUnderscore:
LDA #TL_TOP1			;Border pattern - upper border(Underscore below selected entry).
BNE WindowUndrscrYPos	  ;Branch always.

WindowHideUnderscore:
		LDA #TL_BLANK_TILE1	 ;($AEBC)Prepare to erase underscore character.

WindowUndrscrYPos:
		LDX #$09				;($AEBE)Set Y position for underscore character.
		BNE WindowShowNameChar  ;($AEC0)Branch always.

WindowNameCharYPos:
LDX #$08				;Set Y position for name character.

WindowShowNameChar:
STX ScreenTextYCoordinate	   ;Calculate X position for character to add to name window.
		STA PPUDataByte		 ;($AEC7)

		LDA WindowNameIndex	 ;($AEC9)
CLC					 ;Calculate Y position for character to add to name window.
		ADC #$0C				;($AECD)
		STA ScreenTextXCoordinate;($AECF)

		JSR WindowCalcPPUAddr   ;($AED2)($ADC0)Calculate PPU address for window/text byte.
		JMP AddPPUBufferEntry   ;($AED5)($C690)Add data to PPU buffer.

;----------------------------------------------------------------------------------------------------

;The following table converts to the symbols in the alphabet
;window to the corresponding symbols in the nametable.

.byte TXT_DASH,	  TXT_APOS,	  TXT_EXCLAIM,   TXT_QUESTION
.byte TXT_OPN_PAREN, TXT_CLS_PAREN, TXT_BLANK1,	TXT_COMMA
.byte TXT_PERIOD

;----------------------------------------------------------------------------------------------------

DoWindowPrep:
PHA					 ;Save window type byte on the stack.

		LDX #$40				;($AEE2)Initialize WindowBuildPhase variable.
		STX WindowBuildPhase	;($AEE4)

LDX #$03				;Prepare to look through table below for window type.
* CMP WindowType1Table,X	;
		BEQ +				   ;($AEEC)
DEX					 ;If working on one of the 4 windows from the table below,
		BPL -				   ;($AEEF)Set the WindowBuildPhase variable to 0.  This seems to have
		BMI ++				  ;($AEF1)no effect as the MSB is set after this function is run.
		* LDA #$00			  ;($AEF3)
		STA WindowBuildPhase	;($AEF5)

		* PLA				   ;($AEF8)Get window type byte again.
PHA					 ;

		CMP #WINDOW_CMD_NONCMB  ;($AEFA)Is this the command, non-combat window?
		BEQ DoBeepSFX		   ;($AEFC)If so, branch to make menu button SFX.

CMP #WINDOW_CMD_CMB		;Is this the command, combat window?
		BEQ DoBeepSFX		   ;($AF00)If so, branch to make menu button SFX.

		CMP #WND_YES_NO1		;($AF02)Is this the yes/no selection window?
		BEQ DoConfirmSFX		;($AF04)If so, branch to make confirm SFX.

		CMP #WINDOW_DIALOG	  ;($AF06)Is this a dialog window?
		BNE +				   ;($AF08)If not, branch to exit.

LDA #$00				;Dialog window being created. Set cursor to top left.
		STA WindowTextXCoordinate;($AF0C)
		STA WindowTextYCoordinate;($AF0E)
		JSR ClearDialogOutBuf   ;($AF10)($B850)Clear dialog window buffer.

		* PLA				   ;($AF13)Restore window type byte in A and return.
RTS					 ;

DoBeepSFX:
		LDA #SFX_MENU_BTN	   ;($AF15)Menu button SFX.
		BNE +				   ;($AF17)Branch always.

DoConfirmSFX:
		LDA #SFX_CONFIRM		;($AF19)Confirmation SFX.
		* BRK				   ;($AF1B)
.byte $04, $17		  ;($81A0)InitMusicSFX, bank 1.

		PLA					 ;($AF1E)Restore window type byte in A and return.
RTS					 ;

;----------------------------------------------------------------------------------------------------

WindowType1Table:
		.byte WINDOW_CMD_NONCMB ;($AF20)Command window, non-combat.
.byte WINDOW_CMD_CMB	   ;Combat window, combat.
		.byte WINDOW_DIALOG	 ;($AF22)Dialog window.
.byte WINDOW_POPUP		 ;Pop-up window.

;----------------------------------------------------------------------------------------------------

WindowEraseParams:
		CMP #WINDOW_ALPHBT	  ;($AF24)Special case. Erase alphabet window.
BEQ WindowErsAlphabet	  ;

		CMP #$FF				;($AF28)Special case. Erase unspecified window.
		BEQ WindowErsOther	  ;($AF2A)

		ASL					 ;($AF2C)*2. Widow data pointer is 2 bytes.
TAY					 ;

		LDA WindowwDataPtrTbl,Y ;($AF2E)
STA GenPtr3ELB		  ;Get pointer base of window data.
LDA WindowwDataPtrTbl+1,Y  ;
		STA GenPtr3EUB		  ;($AF36)

LDY #$01				;
LDA (GenPtr3E),Y		;Get window height in blocks.
STA WindowEraseHght		;

		INY					 ;($AF3F)
LDA (GenPtr3E),Y		;Get window width in tiles.
STA WindowEraseWdth		;

		INY					 ;($AF45)
LDA (GenPtr3E),Y		;Get window X,Y position in blocks.
STA WindowErasePos		 ;
		RTS					 ;($AF4B)

WindowErsAlphabet:
		LDA #$07				;($AF4C)Window height = 7 blocks.
		STA WindowEraseHght	 ;($AF4E)

LDA #$16				;Window width = 22 tiles.
STA WindowEraseWdth		;

LDA #$21				;
STA WindowErasePos		 ;Window position = 2,1.
RTS					 ;

WindowErsOther:
		LDA #$0C				;($AF5C)Window height = 12 blocks.
		STA WindowEraseHght	 ;($AF5E)

		LDA #$1A				;($AF61)Window width =  26 tiles.
		STA WindowEraseWdth	 ;($AF63)

		LDA #$22				;($AF66)
		STA WindowErasePos	  ;($AF68)Window position = 2,2.
		RTS					 ;($AF6B)

;----------------------------------------------------------------------------------------------------

WindowDataPointerTable:
.word PopupData		  ;($AFB0)Pop-up window.
.word StatusData		 ;($AFC7)Status window.
.word DialogData		 ;($B04B)Dialog window.
.word CmdNonCmbtDat	 ;($B054)Command window, non-combat.
.word CmdCmbtDat		;($B095)Command window, combat.
.word SpellData		  ;($B0BA)Spell window.
.word SpellData		  ;($B0BA)Spell window.
.word PlayerInvDat	  ;($B0CC)Player inventory window.
.word ShopInvDat		;($B0DA)Shop inventory window.
.word YesNo1Dat		 ;($B0EB)Yes/no selection window, variant 1.
.word BuySellDat		;($B0FB)Buy/sell selection window.
		.word AlphabetData	  ;($AF82)($B10D)Alphabet window.
.word MsgSpeedDat	   ;($B194)Message speed window.
.word InputNameDat	  ;($B1E0)Input name window.
		.word NameEntryDat	  ;($AF88)($B1F7)Name entry window.
.word ContChngErsDat	;($B20B)Continue, change, erase window.
.word FullMenuDat	   ;($B249)Full pre-game menu window.
.word NewQuestDat	   ;($B2A8)Begin new quest window.
.word LogList1Dat1	  ;($B2C2)Log list, entry 1 window 1.
.word LogList2Dat1	  ;($B2DA)Log list, entry 2 window 1.
		.word LogList12Dat1	 ;($AF94)($B2F2)Log list, entry 1,2 window 1.
.word LogList3Dat1	  ;($B31B)Log list, entry 3 window 1.
.word LogList13Dat1	 ;($B333)Log list, entry 1,3 window 1.
		.word LogList23Dat1	 ;($AF9A)($B35C)Log list, entry 2,3 window 1.
.word LogList123Dat1	;($B385)Log list, entry 1,2,3 window 1.
.word LogList1Dat2	  ;($B3BF)Log list, entry 1 window 2.
.word LogList2Dat2	  ;($B3D9)Log list, entry 2 window 2.
.word LogList12Dat2	 ;($B3F3)Log list, entry 1,2 window 2.
.word LogList3Dat2	  ;($B420)Log list, entry 3 window 2.
.word LogList13Dat2	 ;($B43A)Log list, entry 1,3 window 2.
.word LogList23Dat2	 ;($B467)Log list, entry 2,3 window 2.
.word LogList123Dat2	;($B494)Log list, entry 1,2,3 window 2.
.word EraseLogDat	   ;($B4D4)Erase log window.
.word YesNo2Dat		 ;($B50D)Yes/no selection window, variant 2.

;----------------------------------------------------------------------------------------------------

PopupData:
.byte $01			   ;Window options.  Display window.
		.byte $06			   ;($AFB1)Window height.   6 blocks.
.byte $08			   ;Window Width.	8 tiles.
		.byte $21			   ;($AFB3)Window Position. Y = 2 blocks, X = 1 block.
.byte $89			   ;Horizontal border, 1 space.
.byte $B0			   ;Show name, 4 characters.
.byte $88			   ;Horizontal border, remainder of row.
;			  L	V
.byte $2F, $39
.byte $82			   ;Blank tiles, 2 spaces.
		.byte $A0			   ;($AFBA)Show level.
;			  H	P
.byte $2B, $33
.byte $81			   ;Blank tile, 1 space.
		.byte $90			   ;($AFBE)Show hit points.
;			  M	P
.byte $30, $33
.byte $81			   ;Blank tile, 1 space.
		.byte $94			   ;($AFC2)Show magic points.
;			  G
		.byte $2A			   ;($AFC3)
.byte $98			   ;Show gold.
;			  E
		.byte $28			   ;($AFC5)
.byte $A8			   ;Show experience.

;----------------------------------------------------------------------------------------------------

StatusData:
		.byte $21			   ;($AFC7)Display window, single spaced.
		.byte $0B			   ;($AFC8)Window height.   11 blocks.
.byte $14			   ;Window Width.	20 tiles.
		.byte $35			   ;($AFCA)Window Position. Y = 3 blocks, X = 5 blocks.
.byte $88			   ;Horizontal border, remainder of row.
		.byte $85			   ;($AFCC)Blank tiles, 5 spaces.
;			  N	A	M	E	:
.byte $31, $24, $30, $28, $44
		.byte $B1			   ;($AFD2)Show name, 8 characters.
.byte $80			   ;Blank tiles, remainder of row.
		.byte $86			   ;($AFD4)Blank tiles, 6 spaces.
;			  S	T	R	E	N	G	T	H	:
.byte $36, $37, $35, $28, $31, $2A, $37, $2B, $44
		.byte $D8			   ;($AFDE)Show strength.
.byte $80			   ;Blank tiles, remainder of row.
		.byte $87			   ;($AFE0)Blank tiles, 7 spaces.
;			  A	G	I	L	I	T	Y	:
.byte $24, $2A, $2C, $2F, $2C, $37, $3C, $44
.byte $D9			   ;Show agility.
		.byte $80			   ;($AFEA)Blank tiles, remainder of row.
.byte $84			   ;Blank tiles, 4 spaces.
;			  M	A	X	I	M	U	M
		.byte $30, $24, $3B, $2C, $30, $38, $30;($AFEC)
.byte $81			   ;Blank tile, 1 space.
;			  H	P	:
.byte $2B, $33, $44
.byte $DC			   ;Show maximum hit points.
		.byte $80			   ;($AFF8)Blank tiles, remainder of row.
.byte $84			   ;Blank tiles, 4 spaces.
;			  M	A	X	I	M	U	M
.byte $30, $24, $3B, $2C, $30, $38, $30
.byte $81			   ;Blank tile, 1 space.
;			  M	P	:
		.byte $30, $33, $44	 ;($B002)
.byte $DD			   ;Show maximum magic points.
		.byte $80			   ;($B006)Blank tiles, remainder of row.
.byte $82			   ;Blank tiles, 2 spaces.
;			  A	T	T	A	C	K
		.byte $24, $37, $37, $24, $26, $2E;($B008)
.byte $81			   ;Blank tile, 1 space.
;			  P	O	W	E	R	:
.byte $33, $32, $3A, $28, $35, $44
.byte $DA			   ;Show attack power.
.byte $80			   ;Blank tiles, remainder of row.
.byte $81			   ;Blank tile, 1 space.
;			  D	E	F	E	N	S	E
		.byte $27, $28, $29, $28, $31, $36, $28;($B018)
		.byte $81			   ;($B01F)Blank tile, 1 space.
;			  P	O	W	E	R	:
.byte $33, $32, $3A, $28, $35, $44
.byte $DB			   ;Show defense power.
		.byte $80			   ;($B027)Blank tiles, remainder of row.
.byte $82			   ;Blank tiles, 2 spaces.
;			  W	E	A	P	O	N	:
		.byte $3A, $28, $24, $33, $32, $31, $44;($B029)
.byte $B8			   ;Show weapon, first half.
		.byte $87			   ;($B031)Blank tiles, 7 spaces.
.byte $83			   ;Blank tiles, 3 spaces.
		.byte $B8			   ;($B033)Show weapon, second half.
.byte $83			   ;Blank tiles, 3 spaces.
;			  A	R	M	O	R	:
		.byte $24, $35, $30, $32, $35, $44;($B035)
		.byte $B9			   ;($B03B)Show armor, first half.
.byte $87			   ;Blank tiles, 7 spaces.
		.byte $83			   ;($B03D)Blank tiles, 3 spaces.
.byte $B9			   ;Show armor, second half.
.byte $82			   ;Blank tiles, 2 spaces.
;			  S	H	I	E	L	D	:
		.byte $36, $2B, $2C, $28, $2F, $27, $44;($B040)
.byte $BA			   ;Show shield, first half.
		.byte $87			   ;($B048)Blank tiles, 7 spaces.
.byte $83			   ;Blank tiles, 3 spaces.
		.byte $BA			   ;($B04A)Show shield, second half.

;----------------------------------------------------------------------------------------------------

DialogData:
.byte $01			   ;Window options.  Display window.
		.byte $05			   ;($B04C)Window height.   5 blocks.
.byte $18			   ;Window Width.	24 tiles.
.byte $92			   ;Window Position. Y = 9 blocks, X = 2 blocks.
.byte $88			   ;Horizontal border, remainder of row.
		.byte $80			   ;($B050)Blank tiles, remainder of row.
.byte $80			   ;Blank tiles, remainder of row.
		.byte $80			   ;($B052)Blank tiles, remainder of row.
.byte $80			   ;Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

CmdNonCmbtDat:
		.byte $80			   ;($B054)Window options.  Selection window.
.byte $05			   ;Window height.   5 blocks.
		.byte $10			   ;($B056)Window Width.	16 tiles.
		.byte $16			   ;($B057)Window Position. Y = 1 block, X = 6 blocks.
.byte $08			   ;Window columns.  2 columns 8 tiles apart.
		.byte $21			   ;($B059)Cursor home.	 Y = 2 tiles, X = 1 tile.
.byte $8B			   ;Horizontal border, 3 spaces.
;			  C	O	M	M	A	N	D
		.byte $26, $32, $30, $30, $24, $31, $27;($B05B)
.byte $88			   ;Horizontal border, remainder of row.
		.byte $81			   ;($B063)Blank tile, 1 space.
;			  T	A	L	K
.byte $37, $24, $2F, $2E
		.byte $84			   ;($B068)Blank tiles, 4 spaces.
;			  S	P	E	L	L
.byte $36, $33, $28, $2F, $2F
.byte $81			   ;Blank tile, 1 space.
;			  S	T	A	T	U	S
.byte $36, $37, $24, $37, $38, $36
		.byte $82			   ;($B075)Blank tiles, 2 spaces.
;			  I	T	E	M
.byte $2C, $37, $28, $30
		.byte $80			   ;($B07A)Blank tiles, remainder of row.
.byte $81			   ;Blank tile, 1 space.
;			  S	T	A	I	R	S
		.byte $36, $37, $24, $2C, $35, $36;($B07C)
.byte $82			   ;Blank tiles, 2 spaces.
;			  D	O	O	R
		.byte $27, $32, $32, $35;($B083)
.byte $80			   ;Blank tiles, remainder of row.
		.byte $81			   ;($B088)Blank tile, 1 space.
;			  S	E	A	R	C	H
		.byte $36, $28, $24, $35, $26, $2B;($B089)
.byte $82			   ;Blank tiles, 2 spaces.
;			  T	A	K	E
		.byte $37, $24, $2E, $28;($B090)
		.byte $80			   ;($B094)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

CmdCmbtDat:
.byte $80			   ;Window options.  Selection window.
		.byte $03			   ;($B096)Window height.   3 blocks.
.byte $10			   ;Window Width.	16 tiles.
		.byte $16			   ;($B098)Window Position. Y = 1 block, X = 6 blocks.
.byte $08			   ;Window columns.  2 columns 8 tiles apart.
		.byte $21			   ;($B09A)Cursor home.	 Y = 2 tiles, X = 1 tile.
.byte $8B			   ;Horizontal border, 3 spaces.
;			  C	O	M	M	A	N	D
		.byte $26, $32, $30, $30, $24, $31, $27;($B09C)
.byte $88			   ;Horizontal border, remainder of row.
		.byte $81			   ;($B0A4)Blank tile, 1 space.
;			  F	I	G	H	T
		.byte $29, $2C, $2A, $2B, $37;($B0A5)
		.byte $83			   ;($B0AA)Blank tiles, 3 spaces.
;			  S	P	E	L	L
		.byte $36, $33, $28, $2F, $2F;($B0AB)
		.byte $81			   ;($B0B0)Blank tile, 1 space.
;			  R	U	N
.byte $35, $38, $31
		.byte $85			   ;($B0B4)Blank tiles, 5 spaces.
;			  I	T	E	M
.byte $2C, $37, $28, $30
		.byte $80			   ;($B0B9)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

SpellData:
.byte $80			   ;Window options.  Selection window.
		.byte $0B			   ;($B0BB)Window height.   11 blocks.
		.byte $0C			   ;($B0BC)Window Width.	12 tiles.
.byte $29			   ;Window Position. Y = 2 block, X = 9 blocks.
.byte $00			   ;Window columns.  1 column.
		.byte $21			   ;($B0BF)Cursor home.	 Y = 2 tiles, X = 1 tile.
.byte $8B			   ;Horizontal border, 3 spaces.
;			  S	P	E	L	L
		.byte $36, $33, $28, $2F, $2F;($B0C1)
		.byte $88			   ;($B0C6)Horizontal border, remainder of row.
.byte $D6			   ;Calculate number of spells player has.
		.byte $81			   ;($B0C8)Blank tile, 1 space.
		.byte $C0			   ;($B0C9)Get spell for current window row.
.byte $E8			   ;Display spells in window.
		.byte $E9			   ;($B0CB)Finish variable length window.

;----------------------------------------------------------------------------------------------------

PlayerInvDat:
.byte $A0			   ;Window options.  Selection window, single spaced.
		.byte $0B			   ;($B0CD)Window height.   11 blocks.
.byte $0C			   ;Window Width.	12 tiles.
		.byte $39			   ;($B0CF)Window Position. Y = 3 block, X = 9 blocks.
.byte $00			   ;Window columns.  1 column.
		.byte $11			   ;($B0D1)Cursor home.	 Y = 1 tile, X = 1 tile.
.byte $88			   ;Horizontal border, remainder of row.
		.byte $D4			   ;($B0D3)Calculate number of items player has.
.byte $81			   ;Blank tile, 1 space.
		.byte $BB			   ;($B0D5)Display item, first half.
		.byte $82			   ;($B0D6)Blank tile, 2 spaces.
.byte $BB			   ;Display item, second half.
		.byte $E8			   ;($B0D8)Display items in window.
.byte $E9			   ;Finish variable length window.

;----------------------------------------------------------------------------------------------------

ShopInvDat:
		.byte $A0			   ;($B0DA)Window options.  Selection window, single spaced.
.byte $08			   ;Window height.   8 blocks.
		.byte $12			   ;($B0DC)Window Width.	18 tiles.
.byte $25			   ;Window Position. Y = 2 block, X = 5 blocks.
.byte $00			   ;Window columns.  1 column.
		.byte $11			   ;($B0DF)Cursor home.	 Y = 1 tile, X = 1 tile.
.byte $88			   ;Horizontal border, remainder of row.
		.byte $D5			   ;($B0E1)Calculate number of items shop has.
.byte $81			   ;Blank tile, 1 space.
		.byte $BC			   ;($B0E3)Display item, first half.
.byte $81			   ;Blank tile, 1 space.
		.byte $C8			   ;($B0E5)Display item cost.
.byte $82			   ;Blank tile, 2 spaces.
		.byte $BC			   ;($B0E7)Display item, second half.
		.byte $80			   ;($B0E8)Blank tiles, remainder of row.
.byte $E8			   ;Display items in window.
		.byte $E9			   ;($B0EA)Finish variable length window.

;----------------------------------------------------------------------------------------------------

YesNo1Dat:
.byte $80			   ;Window Options.  Selection window.
		.byte $03			   ;($B0EC)Window Height.   3 blocks.
.byte $08			   ;Window Width.	8 tiles.
.byte $25			   ;Window Position. Y = 2 blocks, X = 5 blocks.
.byte $00			   ;Window columns.  1 column.
		.byte $21			   ;($B0F0)Cursor home.	 Y = 2 tiles, X = 1 tile.
.byte $88			   ;Horizontal border, remainder of row.
		.byte $81			   ;($B0F2)Blank tile, 1 space.
;			  Y	E	S
.byte $3C, $28, $36
		.byte $80			   ;($B0F6)Blank tiles, remainder of row.
.byte $81			   ;Blank tile, 1 space.
;			  N	O
		.byte $31, $32		  ;($B0F8)
		.byte $80			   ;($B0FA)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

BuySellDat:
.byte $80			   ;Window Options.  Selection window.
		.byte $03			   ;($B0FC)Window Height.   3 blocks.
.byte $08			   ;Window Width.	8 tiles.
.byte $25			   ;Window Position. Y = 2 blocks, X = 5 blocks.
		.byte $00			   ;($B0FF)Window columns.  1 column.
.byte $21			   ;Cursor home.	 Y = 2 tiles, X = 1 tile.
		.byte $88			   ;($B101)Horizontal border, remainder of row.
.byte $81			   ;Blank tile, 1 space.
;			  B	U	Y
		.byte $25, $38, $3C	 ;($B103)
		.byte $80			   ;($B106)Blank tiles, remainder of row.
.byte $81			   ;Blank tile, 1 space.
;			  S	E	L	L
		.byte $36, $28, $2F, $2F;($B108)
		.byte $80			   ;($B10C)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

AlphabetData:
		.byte $01			   ;($B10D)Window options.  Display window.
.byte $07			   ;Window height.   7 blocks.
		.byte $18			   ;($B10F)Window Width.	24 tiles.
.byte $52			   ;Window Position. Y = 5 blocks, X = 2 blocks.
		.byte $88			   ;($B111)Horizontal border, remainder of row.
;			  _	A	_	B	_	C	_	D	_	E	_	F	_	G	_	H
		.byte $81, $24, $81, $25, $81, $26, $81, $27, $81, $28, $81, $29, $81, $2A, $81, $2B;($B112)
;			  _	I	_	J	_	K	_	L	_	M	_	N	_	O	_	P
.byte $81, $2C, $81, $2D, $81, $2E, $81, $2F, $81, $30, $81, $31, $81, $32, $81, $33
;			  _	Q	_	R	_	S	_	T	_	U	_	V	_	W	_	X
		.byte $81, $34, $81, $35, $81, $36, $81, $37, $81, $38, $81, $39, $81, $3A, $81, $3B;($B132)
;			  _	Y	_	Z	_	-	_	'	_	!	_	?	_	(	_	)
.byte $81, $3C, $81, $3D, $81, $49, $81, $40, $81, $4C, $81, $4B, $81, $4F, $81, $4E
.byte $80			   ;Blank tiles, remainder of row.
;			  _	a	_	b	_	c	_	d	_	e	_	f	_	g	_	h
		.byte $81, $0A, $81, $0B, $81, $0C, $81, $0D, $81, $0E, $81, $0F, $81, $10, $81, $11;($B153)
;			  _	i	_	j	_	k	_	l	_	m	_	n	_	o	_	p
		.byte $81, $12, $81, $13, $81, $14, $81, $15, $81, $16, $81, $17, $81, $18, $81, $19;($B163)
;			  _	q	_	r	_	s	_	t	_	u	_	v	_	w	_	x
		.byte $81, $1A, $81, $1B, $81, $1C, $81, $1D, $81, $1E, $81, $1F, $81, $20, $81, $21;($B173)
;			  _	y	_	z	_	,	_	.	_	B	A	C	K
		.byte $81, $22, $81, $23, $81, $48, $81, $47, $81, $25, $24, $26, $2E;($B183)
.byte $82			   ;Blank tiles, 2 spaces.
;			  E	N	D
.byte $28, $31, $27

;----------------------------------------------------------------------------------------------------

MsgSpeedDat:
		.byte $A1			   ;($B194)Window options.  Selection window, single spaced.
.byte $07			   ;Window Height.   7 blocks.
.byte $12			   ;Window Width.	18 tiles.
.byte $74			   ;Window Position. Y = 7 blocks, X = 4 blocks.
		.byte $00			   ;($B198)Window columns.  1 column.
.byte $86			   ;Cursor home.	 Y = 8 tiles, X = 6 tiles.
		.byte $88			   ;($B19A)Horizontal border, remainder of row.
;			  _	W	h	i	c	h	_	M	e	s	s	a	g	e
.byte $81, $3A, $11, $12, $0C, $11, $81, $30, $0E, $1C, $1C, $0A, $10, $0E
		.byte $80			   ;($B1A9)Blank tiles, remainder of row.
.byte $80			   ;Blank tiles, remainder of row.
;			  _	S	p	e	e	d	_	D	o	_	Y	o	u
		.byte $81, $36, $19, $0E, $0E, $0D, $81, $27, $18, $81, $3C, $18, $1E;($B1AB)
.byte $80			   ;Blank tiles, remainder of row.
.byte $80			   ;Blank tiles, remainder of row.
;			  _	W	a	n	t	_	T	o	_	U	s	e	?
.byte $81, $3A, $0A, $17, $1D, $81, $37, $18, $81, $38, $1C, $0E, $4B
.byte $80			   ;Blank tiles, remainder of row.
.byte $80			   ;Blank tiles, remainder of row.
.byte $80			   ;Blank tiles, remainder of row.
.byte $86			   ;Blank tiles, 6 spaces.
;			  F	A	S	T
.byte $29, $24, $36, $37
		.byte $80			   ;($B1CF)Blank tiles, remainder of row.
.byte $80			   ;Blank tiles, remainder of row.
		.byte $86			   ;($B1D1)Blank tiles, 6 spaces.
;			  N	O	R	M	A	L
.byte $31, $32, $35, $30, $24, $2F
		.byte $80			   ;($B1D8)Blank tiles, remainder of row.
.byte $80			   ;Blank tiles, remainder of row.
		.byte $86			   ;($B1DA)Blank tiles, 6 spaces.
;			  S	L	O	W
.byte $36, $2F, $32, $3A
.byte $80			   ;Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

InputNameDat:
		.byte $01			   ;($B1E0)Window options.  Display window.
.byte $02			   ;Window Height.   2 blocks.
		.byte $14			   ;($B1E2)Window Width.	20 tiles.
.byte $73			   ;Window Position. Y = 7 blocks, X = 3 blocks.
		.byte $88			   ;($B1E4)Horizontal border, remainder of row.
;			  _	I	N	P	U	T	_	Y	O	U	R	_	N	A	M	E
.byte $81, $2C, $31, $33, $38, $37, $81, $3C, $32, $38, $35, $81, $31, $24, $30, $28
;			  !
.byte $4C
		.byte $80			   ;($B1F6)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

NameEntryDat:
.byte $01			   ;Window options.  Display window.
		.byte $03			   ;($B1F8)Window Height.   3 blocks.
.byte $0C			   ;Window Width.	12 tiles.
		.byte $35			   ;($B1FA)Window Position. Y = 3 blocks, X = 5 blocks.
.byte $8B			   ;Horizontal border, 3 spaces.
;			  N	A	M	E
.byte $31, $24, $30, $28
.byte $88			   ;Horizontal border, remainder of row.
;			  _	*	*	*	*	*	*	*	*
		.byte $81, $41, $41, $41, $41, $41, $41, $41, $41;($B201)
.byte $80			   ;Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

ContChngErsDat:
		.byte $81			   ;($B20B)Window Options.  Selection window.
.byte $04			   ;Window Height.   4 blocks.
		.byte $18			   ;($B20D)Window Width.	24 tiles.
.byte $42			   ;Window Position. Y = 4 blocks, X = 2 blocks.
		.byte $00			   ;($B20F)Window columns.  1 column.
		.byte $21			   ;($B210)Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	C	O	N	T	I	N	U	E	_	A	_	Q	U	E	S
.byte $81, $26, $32, $31, $37, $2C, $31, $38, $28, $81, $24, $81, $34, $38, $28, $36
;			  T
		.byte $37			   ;($B222)
.byte $80			   ;Blank tiles, remainder of row.
;			  _	C	H	A	N	G	E	_	M	E	S	S	A	G	E	_
		.byte $81, $26, $2B, $24, $31, $2A, $28, $81, $30, $28, $36, $36, $24, $2A, $28, $81;($B224)
;			  S	P	E	E	D
.byte $36, $33, $28, $28, $27
.byte $80			   ;Blank tiles, remainder of row.
;			  _	E	R	A	S	E	_	A	_	Q	U	E	S	T
		.byte $81, $28, $35, $24, $36, $28, $81, $24, $81, $34, $38, $28, $36, $37;($B23A)
.byte $80			   ;Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

FullMenuDat:
.byte $81			   ;Window Options.  Selection window.
		.byte $06			   ;($B24A)Window Height.   6 blocks.
.byte $18			   ;Window Width.	24 tiles.
		.byte $42			   ;($B24C)Window Position. Y = 4 blocks, X = 2 blocks.
		.byte $00			   ;($B24D)Window columns.  1 column.
.byte $21			   ;Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	C	O	N	T	I	N	U	E	_	A	_	Q	U	E	S
		.byte $81, $26, $32, $31, $37, $2C, $31, $38, $28, $81, $24, $81, $34, $38, $28, $36;($B250)
;			  T
.byte $37
		.byte $80			   ;($B261)Blank tiles, remainder of row.
;			  _	C	H	A	N	G	E	_	M	E	S	S	A	G	E	_
.byte $81, $26, $2B, $24, $31, $2A, $28, $81, $30, $28, $36, $36, $24, $2A, $28, $81
;			  S	P	E	E	D
.byte $36, $33, $28, $28, $27
.byte $80			   ;Blank tiles, remainder of row.
;			  _	B	E	G	I	N	_	A	_	N	E	W	_	Q	U	E
		.byte $81, $25, $28, $2A, $2C, $31, $81, $24, $81, $31, $28, $3A, $81, $34, $38, $28;($B278)
;			  S	T
		.byte $36, $37		  ;($B288)
		.byte $80			   ;($B28A)Blank tiles, remainder of row.
;			  _	C	O	P	Y	_	A	_	Q	U	E	S	T
		.byte $81, $26, $32, $33, $3C, $81, $24, $81, $34, $38, $28, $36, $37;($B28B)
		.byte $80			   ;($B298)Blank tiles, remainder of row.
;			  _	E	R	A	S	E	_	A	_	Q	U	E	S	T
.byte $81, $28, $35, $24, $36, $28, $81, $24, $81, $34, $38, $28, $36, $37
		.byte $80			   ;($B2A7)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

NewQuestDat:
.byte $81			   ;Window Options.  Selection window.
		.byte $02			   ;($B2A9)Window Height.   2 blocks.
		.byte $18			   ;($B2AA)Window Width.	24 tiles.
.byte $42			   ;Window Position. Y = 4 blocks, X = 2 blocks.
		.byte $00			   ;($B2AC)Window columns.  1 column.
.byte $21			   ;Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	B	E	G	I	N	_	A	_	N	E	W	_	Q	U	E
.byte $81, $25, $28, $2A, $2C, $31, $81, $24, $81, $31, $28, $3A, $81, $34, $38, $28
;			  S	T
		.byte $36, $37		  ;($B2BF)
		.byte $80			   ;($B2C1)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList1Dat1:
.byte $81			   ;Window Options.  Selection window.
		.byte $02			   ;($B2C3)Window Height.   2 blocks.
.byte $14			   ;Window Width.	20 tiles.
		.byte $95			   ;($B2C5)Window Position. Y = 9 blocks, X = 5 blocks.
.byte $00			   ;Window columns.  1 column.
		.byte $21			   ;($B2C7)Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	1
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $01;($B2C9)
		.byte $80			   ;($B2D9)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList2Dat1:
.byte $81			   ;Window Options.  Selection window.
		.byte $02			   ;($B2DB)Window Height.   2 blocks.
.byte $14			   ;Window Width.	20 tiles.
		.byte $95			   ;($B2DD)Window Position. Y = 9 blocks, X = 5 blocks.
.byte $00			   ;Window columns.  1 column.
		.byte $21			   ;($B2DF)Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	2
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $02;($B2E1)
		.byte $80			   ;($B2F1)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList12Dat1:
.byte $81			   ;Window Options.  Selection window.
		.byte $03			   ;($B2F3)Window Height.   3 blocks.
.byte $14			   ;Window Width.	20 tiles.
		.byte $95			   ;($B2F5)Window Position. Y = 9 blocks, X = 5 blocks.
.byte $00			   ;Window columns.  1 column.
		.byte $21			   ;($B2F7)Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	1
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $01;($B2F9)
.byte $80			   ;Blank tiles, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	2
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $02;($B30A)
		.byte $80			   ;($B31A)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList3Dat1:
.byte $81			   ;Window Options.  Selection window.
		.byte $02			   ;($B31C)Window Height.   2 blocks.
		.byte $14			   ;($B31D)Window Width.	20 tiles.
.byte $95			   ;Window Position. Y = 9 blocks, X = 5 blocks.
		.byte $00			   ;($B31F)Window columns.  1 column.
		.byte $21			   ;($B320)Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	3
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $03;($B322)
.byte $80			   ;Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList13Dat1:
		.byte $81			   ;($B333)Window Options.  Selection window.
.byte $03			   ;Window Height.   3 blocks.
		.byte $14			   ;($B335)Window Width.	20 tiles.
.byte $95			   ;Window Position. Y = 9 blocks, X = 5 blocks.
		.byte $00			   ;($B337)Window columns.  1 column.
.byte $21			   ;Cursor home.	 Y = 2 tiles, X = 1 tiles.
		.byte $88			   ;($B339)Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	1
.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $01
		.byte $80			   ;($B34A)Blank tiles, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	3
.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $03
		.byte $80			   ;($B35B)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList23Dat1:
.byte $81			   ;Window Options.  Selection window.
		.byte $03			   ;($B35D)Window Height.   3 blocks.
		.byte $14			   ;($B35E)Window Width.	20 tiles.
.byte $95			   ;Window Position. Y = 9 blocks, X = 5 blocks.
		.byte $00			   ;($B360)Window columns.  1 column.
.byte $21			   ;Cursor home.	 Y = 2 tiles, X = 1 tiles.
		.byte $88			   ;($B362)Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	2
.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $02
.byte $80			   ;Blank tiles, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	3
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $03;($B374)
		.byte $80			   ;($B384)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList123Dat1:
		.byte $81			   ;($B385)Window Options.  Selection window.
.byte $04			   ;Window Height.   4 blocks.
		.byte $14			   ;($B387)Window Width.	20 tiles.
.byte $95			   ;Window Position. Y = 9 blocks, X = 5 blocks.
		.byte $00			   ;($B389)Window columns.  1 column.
.byte $21			   ;Cursor home.	 Y = 2 tiles, X = 1 tiles.
		.byte $88			   ;($B38B)Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	1
.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $01
.byte $80			   ;Blank tiles, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	2
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $02;($B39D)
.byte $80			   ;Blank tiles, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	3
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $03;($B3AE)
		.byte $80			   ;($B3BE)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList1Dat2:
.byte $81			   ;Window Options.  Selection window.
		.byte $02			   ;($B3C0)Window Height.   2 blocks.
.byte $18			   ;Window Width.	24 tiles.
		.byte $63			   ;($B3C2)Window Position. Y = 6 blocks, X = 3 blocks.
		.byte $00			   ;($B3C3)Window columns.  1 column.
.byte $21			   ;Cursor home.	 Y = 2 tiles, X = 1 tiles.
		.byte $88			   ;($B3C5)Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	1
.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $01
;			  :
		.byte $44			   ;($B3D6)
		.byte $B5			   ;($B3D7)Display Log 1 character's name.
.byte $80			   ;Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList2Dat2:
		.byte $81			   ;($B3D9)Window Options.  Selection window.
		.byte $02			   ;($B3DA)Window Height.   2 blocks.
.byte $18			   ;Window Width.	24 tiles.
.byte $63			   ;Window Position. Y = 6 blocks, X = 3 blocks.
.byte $00			   ;Window columns.  1 column.
		.byte $21			   ;($B3DE)Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	2
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $02;($B3E0)
;			  :
		.byte $44			   ;($B3F0)
.byte $B6			   ;Display Log 2 character's name.
		.byte $80			   ;($B3F2)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList12Dat2:
.byte $81			   ;Window Options.  Selection window.
		.byte $03			   ;($B3F4)Window Height.   3 blocks.
		.byte $18			   ;($B3F5)Window Width.	24 tiles.
.byte $63			   ;Window Position. Y = 6 blocks, X = 3 blocks.
		.byte $00			   ;($B3F7)Window columns.  1 column.
.byte $21			   ;Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	1
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $01;($B3FA)
;			  :
		.byte $44			   ;($B40A)
.byte $B5			   ;Display Log 1 character's name.
		.byte $80			   ;($B30C)Blank tiles, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	2
.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $02
;			  :
		.byte $44			   ;($B41D)
.byte $B6			   ;Display Log 2 character's name.
		.byte $80			   ;($B41F)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList3Dat2:
.byte $81			   ;Window Options.  Selection window.
		.byte $02			   ;($B421)Window Height.   2 blocks.
.byte $18			   ;Window Width.	24 tiles.
		.byte $63			   ;($B423)Window Position. Y = 6 blocks, X = 3 blocks.
.byte $00			   ;Window columns.  1 column.
		.byte $21			   ;($B425)Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	3
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $03;($B427)
;			  :
		.byte $44			   ;($B437)
.byte $B7			   ;Display Log 3 character's name.
		.byte $80			   ;($B439)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList13Dat2:
.byte $81			   ;Window Options.  Selection window.
		.byte $03			   ;($B43B)Window Height.   3 blocks.
.byte $18			   ;Window Width.	24 tiles.
		.byte $63			   ;($B43D)Window Position. Y = 6 blocks, X = 3 blocks.
.byte $00			   ;Window columns.  1 column.
		.byte $21			   ;($B43F)Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	1
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $01;($B441)
;			  :
.byte $44
		.byte $B5			   ;($B452)Display Log 1 character's name.
.byte $80			   ;Blank tiles, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	3
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $03;($B454)
;			  :
.byte $44
		.byte $B7			   ;($B465)Display Log 3 character's name.
.byte $80			   ;Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList23Dat2:
		.byte $81			   ;($B467)Window Options.  Selection window.
.byte $03			   ;Window Height.   3 blocks.
		.byte $18			   ;($B469)Window Width.	24 tiles.
.byte $63			   ;Window Position. Y = 6 blocks, X = 3 blocks.
		.byte $00			   ;($B46B)Window columns.  1 column.
.byte $21			   ;Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	2
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $02;($B46E)
;			  :
		.byte $44			   ;($B47E)
.byte $B6			   ;Display Log 2 character's name.
		.byte $80			   ;($B480)Blank tiles, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	3
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $03;($B481)
;			  :
.byte $44
		.byte $B7			   ;($B492)Display Log 3 character's name.
.byte $80			   ;Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

LogList123Dat2:
		.byte $81			   ;($B494)Window Options.  Selection window.
.byte $04			   ;Window Height.   4 blocks.
		.byte $18			   ;($B496)Window Width.	24 tiles.
.byte $63			   ;Window Position. Y = 6 blocks, X = 3 blocks.
		.byte $00			   ;($B498)Window columns.  1 column.
		.byte $21			   ;($B499)Cursor home.	 Y = 2 tiles, X = 1 tiles.
.byte $88			   ;Horizontal border, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	1
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $01;($B49B)
;			  :
.byte $44
.byte $B5			   ;Display Log 1 character's name.
.byte $80			   ;Blank tiles, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	2
		.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $02;($B4AE)
;			  :
		.byte $44			   ;($B4BE)
.byte $B6			   ;Display Log 2 character's name.
		.byte $80			   ;($B4C0)Blank tiles, remainder of row.
;			  _	A	D	V	E	N	T	U	R	E	_	L	O	G	_	3
.byte $81, $24, $27, $39, $28, $31, $37, $38, $35, $28, $81, $2F, $32, $2A, $81, $03
;			  :
		.byte $44			   ;($B4D1)
.byte $B7			   ;Display Log 3 character's name.
		.byte $80			   ;($B4D3)Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

EraseLogDat:
.byte $01			   ;Window options.  Display window.
		.byte $06			   ;($B4D5)Window height.   6 blocks.
.byte $14			   ;Window Width.	20 tiles.
		.byte $73			   ;($B4D7)Window Position. Y = 7 blocks, X = 3 blocks.
		.byte $88			   ;($B4D8)Horizontal border, remainder of row.
.byte $81			   ;Blank tile, 1 space.
		.byte $B4			   ;($B4DA)Display character's name.
.byte $80			   ;Blank tiles, remainder of row.
;			  _	L	E	V	E	L
.byte $81, $2F, $28, $39, $28, $2F
		.byte $82			   ;($B4E2)Blank tile, 2 spaces.
.byte $A1			   ;Display character's level.
		.byte $80			   ;($B4E4)Blank tiles, remainder of row.
;			  _	D	o	_	Y	o	u	_	W	a	n	t	_	T	o
		.byte $81, $27, $18, $81, $3C, $18, $1E, $81, $3A, $0A, $17, $1D, $81, $37, $18;($B4E5)
.byte $80			   ;Blank tiles, remainder of row.
;			  _	E	r	a	s	e	_	T	h	i	s
		.byte $81, $28, $1B, $0A, $1C, $0E, $81, $37, $11, $12, $1C;($B4F5)
		.byte $80			   ;($B500)Blank tiles, remainder of row.
;			  _	C	h	a	r	a	c	t	e	r	?
.byte $81, $26, $11, $0A, $1B, $0A, $0C, $1D, $0E, $1B, $4B
.byte $80			   ;Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

YesNo2Dat:
.byte $80			   ;Window Options.  Selection window.
.byte $03			   ;Window Height.   3 blocks.
.byte $08			   ;Window Width.	8 tiles.
		.byte $3A			   ;($B510)Window Position. Y = 3 blocks, X = 10 blocks.
		.byte $00			   ;($B511)Window columns.  1 column.
.byte $21			   ;Cursor home.	 Y = 2 tiles, X = 1 tile.
		.byte $88			   ;($B513)Horizontal border, remainder of row.
.byte $81			   ;Blank tile, 1 space.
;			  Y	E	S
		.byte $3C, $28, $36	 ;($B515)
		.byte $80			   ;($B518)Blank tiles, remainder of row.
.byte $81			   ;Blank tile, 1 space.
;			  N	O
		.byte $31, $32		  ;($B51A)
.byte $80			   ;Blank tiles, remainder of row.

;----------------------------------------------------------------------------------------------------

DoDialog:
JSR FindDialogEntry	 ;($B532)Get pointer to desired dialog text.
JSR InitDialogVars	  ;($B576)Initialize the dialog variables.

* JSR CalcWordCoord	   ;($B5AF)Calculate coordinates of word in text window.
		JSR WordToScreen		;($B526)($B5E6)Send dialog word to the screen.
JSR CheckDialogEnd	  ;($B594)Check if dialog buffer is complete.
		BCC -				   ;($B52C)

		JSR DialogToScreenBuf   ;($B52E)($B85D)Copy dialog buffer to screen buffer.
		RTS					 ;($B531)

;----------------------------------------------------------------------------------------------------

FindDialogEntry:
STA TextEntry		   ;Store byte and process later.

		AND #NBL_UPPER		  ;($B534)
		LSR					 ;($B536)
LSR					 ;Keep upper nibble and shift it to lower nibble.
		LSR					 ;($B538)
LSR					 ;
		STA TextBlock		   ;($B53A)

		TXA					 ;($B53C)Get upper/lower text block bit and move to upper nibble.
		ASL					 ;($B53D)
ASL					 ;
		ASL					 ;($B53F)
		ASL					 ;($B540)
ADC TextBlock		   ;Add to text block byte. Text block calculation complete.

CLC					 ;
		ADC #$01				;($B544)Use TextBlock as pointer into bank table. Incremented
		STA BankPtrIndex		;($B546)by 1 as first pointer is for intro routine.

		LDA #PRG_BANK_2		 ;($B548)Prepare to switch to PRG bank 2.
		STA NewPRGBank		  ;($B54A)

		LDX #$9F				;($B54C)Store data pointer in $9F,$A0
		JSR GetAndStrDatPtr	 ;($B54E)($FD00)

		LDA TextEntry		   ;($B551)
AND #NBL_LOWER		  ;Keep only lower nibble for text entry number.
		STA TextEntry		   ;($B555)

		TAX					 ;($B557)Keep copy of entry number in X.
BEQ ++++				;Entry 0? If so, done! branch to exit.

		LDY #$00				;($B55A)No offset from pointer.
		* LDX #DialogPtr		;($B55C)DialogPtr is the pointer to use.
		LDA #PRG_BANK_2		 ;($B55E)PRG bank 2 is where the text is stored.

		JSR GetBankDataByte	 ;($B560)($FD1C)Retreive data byte.

INC DialogPtrLB		 ;
BNE +				   ;Increment dialog pointer.
INC DialogPtrUB		 ;

		* CMP #TXT_END1		 ;($B569)At the end of current text entry?
		BEQ +				   ;($B56B)If so, branch to check nect entry.

		CMP #TXT_END2		   ;($B56D)Also used as end of entry marker.
		BNE --				  ;($B56F)Branch if not end of entry.

		* DEC TextEntry		 ;($B571)Incremented past current text entry.
BNE ---				 ;Are we at right entry? if not, branch to try next entry.

* RTS					 ;Done. DialogPtr points to desired text entry.

;----------------------------------------------------------------------------------------------------

InitDialogVars:
LDA #$00				;
		STA TxtIndent		   ;($B578)
STA Dialog00			;
		STA DialogEnd		   ;($B57E)
		STA WrkBufBytsDone	  ;($B581)
LDA #$08				;Initialize the dialog variables.
STA TxtLineSpace		;
		LDA WindowTextXCoordinate;($B589)
		STA Unused6510		  ;($B58B)
LDA WindowTextYCoordinate		;
STA Unused6511		  ;
		RTS					 ;($B593)

;----------------------------------------------------------------------------------------------------

CheckDialogEnd:
LDA DialogEnd		   ;
BNE +				   ;Is dialog buffer complete?
		CLC					 ;($B599)If so, clear the carry flag.
RTS					 ;

		* LDX WindowTextYCoordinate;($B59B)
LDA Unused6512		  ;
BNE +				   ;
		STX Unused6512		  ;($B5A2)Dialog buffer not complete. Set carry.
* LDA Unused6513		  ;The other variables have no effect.
		BNE +				   ;($B5A8)
		STX Unused6513		  ;($B5AA)
		* SEC				   ;($B5AD)
RTS					 ;

;----------------------------------------------------------------------------------------------------

CalcWordCoord:
		JSR GetTxtWord		  ;($B5AF)($B635)Get the next word of text.

BIT Dialog00			;Should never branch.
		BMI CalcCoordEnd		;($B5B5)

		LDA WindowTextXCoordinate;($B5B7)Make sure x coordinate after word is
		STA WindowXPositionAfterWord;($B5B9)the same as current x coordinate.

LDA #$00				;Zero out word buffer index.
STA WordBufIndex		;

SearchWordBuf:
LDX WordBufIndex		;
		LDA WordBuffer,X		;($B5C4)Get next character in the word buffer.
INC WordBufIndex		;

CMP #TL_BLANK_TILE1	 ;Has a space in the word buffer been found?
BEQ WordBufBreakFound   ;If so, branch to see if it will fit it into text window.

CMP #TXT_SUBEND		 ;Has a sub-buffer end character been found?
BCS WordBufBreakFound   ;If so, branch to see if word will fit it into text window.

		INC WindowXPositionAfterWord;($B5D2)Increment window position pointer.

		JSR CheckBetweenWords   ;($B5D5)($B8F9)Check for non-word character.
		BCS SearchWordBuf	   ;($B5D8)Still in word? If so, branch.

WordBufBreakFound:
		LDX WindowXPositionAfterWord;($B5DA)Is X position at beginning of line?
BEQ +				   ;If so, branch to skip modifying X position.

DEC WindowXPositionAfterWord		   ;Dcrement index so it points to last character position.

* JSR CheckForNewLine	 ;($B915)Move text to new line, if necessary.

CalcCoordEnd:
		RTS					 ;($B5E5)End coordinate calculations.

;----------------------------------------------------------------------------------------------------

WordToScreen:
LDX #$00				;Zero out word buffer index.
STX WordBufferLength		  ;

		* LDX WordBufferLength  ;($B5EB)
LDA WordBuffer,X		;Get next character in the word buffer.
		INC WordBufferLength	;($B5F1)

CMP #TXT_SUBEND		 ;Is character a control character that will cause a newline?
		BCS TextControlChars	;($B5F6)If so, branch to determine the character.

PHA					 ;
		JSR TextToPPU		   ;($B5F9)($B9C7)Send dialog text character to the screen.
PLA					 ;

		JSR CheckBetweenWords   ;($B5FD)($B8F9)Check for non-word character.
BCS -				   ;Was the character a text character?
RTS					 ;If so, branch to get another character.

TextControlChars:
		CMP #TXT_WAIT		   ;($B603)Was wait found?
BEQ WaitFound		   ;If so, branch to wait.

CMP #TXT_END1		   ;Was the end character found?
BEQ DialogEndFound	  ;If so, branch to end dialog.

CMP #TXT_NEWL		   ;Was a newline character found?
		BEQ NewLineFound		;($B60D)If so, branch to do newline routine.

		CMP #TXT_NOP			;($B60F)Was a no-op found?
		BEQ NewLineFound		;($B611)If so, branch to do newline routine.

DoDialogEnd:
		LDA #TXT_END2		   ;($B613)Dialog is done. Load end of dialog marker.
STA DialogEnd		   ;Set end of dialog flag.
		RTS					 ;($B618)

NewLineFound:
		JMP DoNewline		   ;($B619)($B91D)Go to next line in dialog window.

WaitFound:
		JSR DoNewline		   ;($B61C)($B91D)Go to next line in dialog window.
		JSR DoWait			  ;($B61F)($BA59)Wait for user interaction.

		LDA TxtIndent		   ;($B622)Is an indent active?
BNE +				   ;If so, branch to skip newline.

		JSR MoveToNextLine	  ;($B627)($B924)Move to the next line in the text window.
* RTS					 ;

DialogEndFound:
		JSR DoNewline		   ;($B62B)($B91D)Go to next line in dialog window.
LDA #$00				;Set cursor X position to beginning of line.
STA WindowTextXCoordinate		;
		JMP DoDialogEnd		 ;($B632)($B613)End current dialog.

;----------------------------------------------------------------------------------------------------

GetTxtWord:
LDA #$00				;Zero out word buffer length.
STA WordBufLen		  ;

GetTxtByteLoop:
		JSR GetTextByte		 ;($B63A)($B662)Get text byte from ROM or work buffer.
CMP #TXT_NOP			;Is character a no-op character?
		BNE BuildWordBuf		;($B63F)If not, branch to add to word buffer.

		BIT Dialog00			;($B641)Branch always.
BPL GetTxtByteLoop	  ;Get next character.

BuildWordBuf:
CMP #TXT_OPN_QUOTE	  ;"'"(open quotes).
BEQ TxtSetIndent		;Has open quotes been found? If so, branch to set indent.

CMP #TXT_INDENT		 ;" "(Special indent blank space).
		BNE +				   ;($B64C)Has indent character been found? If not, branch to skip indent.

TxtSetIndent:
LDX #$01				;Set text indent to 1 space.
		STX TxtIndent		   ;($B650)

* LDX WordBufferLength		  ;Add character to word buffer.
STA WordBuffer,X		;
		INC WordBufferLength	;($B659)Increment buffer length.
JSR CheckBetweenWords   ;($B8F9)Check for non-word character.
		BCS GetTxtByteLoop	  ;($B65F)End of word? If not, branch to get next byte.
		RTS					 ;($B661)

;----------------------------------------------------------------------------------------------------

GetTextByte:
LDX WrkBufBytsDone	  ;Are work buffer bytes waiting to be returned?
		BEQ GetROMByte		  ;($B665)If not, branch to retreive a ROM byte instead.

WorkBufDone:
		LDA WorkBuffer,X		;($B667)Grab the next byte from the work buffer.
INC WrkBufBytsDone	  ;
CMP #TXT_SUBEND		 ;Is it the end marker for the work buffer?
BNE +				   ;If not, branch to return another work buffer byte.

LDX #$00				;Work buffer bytes all processed.
STX WrkBufBytsDone	  ;
		BEQ GetROMByte		  ;($B676)Branch always and grab a byte from ROM.

* RTS					 ;Return work buffer byte.

GetROMByte:
		LDA #PRG_BANK_2		 ;($B679)PRG bank 2 is where the text is stored.
		LDX #DialogPtr		  ;($B67B)DialogPtr is the pointer to use.
		LDY #$00				;($B67D)No offset from pointer.

		JSR GetBankDataByte	 ;($B67F)($FD1C)Get text byte from PRG bank 2 and store in A.
JSR IncDialogPtr		;($BA9F)Increment DialogPtr.

		CMP #TXT_PLRL		   ;($B685)Plural control character?
		BEQ JmpDoPLRL		   ;($B687)If so, branch to process.

CMP #TXT_DESC		   ;Object description control character?
BEQ JmpDoDESC		   ;If so, branch to process.

CMP #TXT_PNTS		   ;"Points" control character?
BEQ JmpDoPNTS		   ;If so, brach to process.

CMP #TXT_AMTP		   ;Numeric amount + "Points" control character?
BEQ JmpDoAMTP		   ;If so, branch to process.

		CMP #TXT_AMNT		   ;($B695)Numeric amount control character?
		BEQ JmpDoAMNT		   ;($B697)If so, branch to process.

		CMP #TXT_SPEL		   ;($B699)Spell description control character?
BEQ JmpDoSPEL		   ;If so, branch to process.

		CMP #TXT_NAME		   ;($B69D)Name description control character?
		BEQ JmpDoNAME		   ;($B69F)If so, branch to process.

		CMP #TXT_ITEM		   ;($B6A1)Item description control character?
BEQ JmpDoITEM		   ;If so, branch to process.

CMP #TXT_COPY		   ;Buffer copy control character?
BEQ JmpDoCOPY		   ;If so, branch to process.

CMP #TXT_ENMY		   ;Enemy name control character?
BEQ JmpDoENMY		   ;If so, branch to process.

CMP #TXT_ENM2		   ;Enemy name control character?
		BEQ JmpDoENM2		   ;($B6AF)If so, branch to process.

		RTS					 ;($B6B1)No control character. Return ROM byte.

;----------------------------------------------------------------------------------------------------

JmpDoCOPY:
JMP DoCOPY			  ;($B7E8)Copy description buffer straight into work buffer.

JmpDoNAME:
		JMP DoNAME			  ;($B6B5)($B7F9)Jump to get player's name.

JmpDoENMY:
JMP DoENMY			  ;($B804)Jump to get enemy name.

JmpDoSPEL:
JMP DoSPEL			  ;($B7D8)Jump to get spell description.

JmpDoDESC:
		JMP DoDESC			  ;($B6BE)($B794)Jump do get object description proceeded by 'a' or 'an'.

JmpDoENM2:
JMP DoENM2			  ;(B80F)Jump to get enemy name preceeded by 'a' or 'an'.

JmpDoITEM:
JMP DoITEM			  ;($B757)Jump to get item description.

JmpDoPNTS:
JMP DoPNTS			  ;($B71E)Jump to write "Points" to buffer.

JmpDoAMTP:
		JMP DoAMTP			  ;($B6CA)($B724)Jump to do BCD converion and write "Points" to buffer.

;----------------------------------------------------------------------------------------------------

JmpDoAMNT:
JSR BinWordToBCD		;($B6DA)Convert word in $00/$01 to BCD.

WorkBufEndChar:
LDA #TXT_SUBEND		 ;Place termination character at end of work buffer.
STA WorkBuffer,Y		;

		LDX #$00				;($B6D5)Set index to beginning of work buffer.
		JMP WorkBufDone		 ;($B6D7)($B667)Done building work buffer.

;----------------------------------------------------------------------------------------------------

BinWordToBCD:
LDA #$05				;Largest BCD from two bytes is 5 digits.
STA SubBufLength		;

		LDA GenWrd00LB		  ;($B6DF)
STA BCDByte0			;Load word to convert to BCD.
LDA GenWrd00UB		  ;
STA BCDByte1			;
LDA #$00				;3rd byte is always 0.
STA BCDByte2			;

		JSR ConvertToBCD		;($B6EB)($A753)Convert binary word to BCD.
JSR ClearBCDLeadZeros   ;($A764)Remove leading zeros from BCD value.

LDY #$00				;
		* LDA TempBuffer,X	  ;($B6F3)Transfer contents of BCD buffer to work buffer.
STA WorkBuffer,Y		;
		INY					 ;($B6F9)BCD buffer is backwards so it needs to be
DEX					 ;written in reverse into the work buffer.
		BPL -				   ;($B6FB)
		RTS					 ;($B6FD)

;----------------------------------------------------------------------------------------------------

JmpDoPLRL:
LDA #$01				;Start with a single byte in the buffer.
STA SubBufLength		;

		LDA GenWrd00UB		  ;($B703)
		BNE +				   ;($B705)Is the numeric value greater than 1?
		LDX GenWrd00LB		  ;($B707)
		DEX					 ;($B709)If so, add an 's' to the end of the buffer.
BEQ EndPlrl			 ;

* LDA #$1C				;'s' character.
STA WorkBuffer		  ;

		LDY #$01				;($B711)Increment buffer size.
		INC SubBufLength		;($B713)
JMP WorkBufEndChar	  ;($B6D0)Place termination character on work buffer.

EndPlrl:
		LDY #$00				;($B719)
JMP WorkBufEndChar	  ;($B6D0)Place termination character on work buffer.

;----------------------------------------------------------------------------------------------------

DoPNTS:
LDY #$00				;BCD value is 5 bytes max.
		LDA #$05				;($B720)
		BNE +				   ;($B722)Branch always.

DoAMTP:
JSR BinWordToBCD		;($B6DA)Convert word in $00/$01 to BCD.

LDA SubBufLength		;
		CLC					 ;($B72A)Increase buffer length by 6.
ADC #$06				;

		* STA SubBufLength	  ;($B72D)Set initial buffer length.

LDX #$05				;
* LDA PointsTable,X		   ;
		STA WorkBuffer,Y		;($B735)Load "Point" into work buffer.
INY					 ;
		DEX					 ;($B739)
		BPL -				   ;($B73A)

LDA GenWrd00UB		  ;
BNE +				   ;Is number to convert to BCD greater than 1?
		LDX GenWrd00LB		  ;($B740)If so, add an "s" to the end of "Point".
DEX					 ;
BEQ ++				  ;

* LDA #TXT_LWR_S		  ;Add "s" to the end of the buffer.
		STA WorkBuffer,Y		;($B747)
INY					 ;
		INC SubBufLength		;($B74B)Increment buffer length.
* JMP WorkBufEndChar	  ;($B6D0)Place termination character on work buffer.

PointsTable:						;(Point backwards).
;			  t	n	i	o	P   BLNK
		.byte $1D, $17, $12, $18, $33, $5F;($B751)

;----------------------------------------------------------------------------------------------------

DoITEM:
JSR GetDescHalves	   ;($B75D)Get full description and store in work buffer.
		JMP WorkBufEndChar	  ;($B75A)($B6D0)Place termination character on work buffer.

GetDescHalves:
LDA #$00				;Start with first half of description.
		STA WindowDescHalf	  ;($B75F)

JSR PrepGetDesc		 ;($B77E)Do some prep then locate description.
		JSR UpdateDescBufferLen ;($B765)($B82B)Save desc buffer length and zero index.
LDA #TL_BLANK_TILE1	 ;
STA WorkBuffer,Y		;Place a blank space between words.

		INY					 ;($B76D)
		TYA					 ;($B76E)Save pointer into work buffer.
PHA					 ;

		INC WindowDescHalf	  ;($B770)Do second half of description.
		JSR PrepGetDesc		 ;($B773)($B77E)Do some prep then locate description.
		STY DescriptionLength   ;($B776)Store length of description string.

		PLA					 ;($B779)Restore current index into the work buffer.
TAY					 ;
		JMP XferTempToWork	  ;($B77B)($B830)Transfer temp buffer contents to work buffer.

PrepGetDesc:
LDA #$09				;Set max buffer length to 9.
STA SubBufLength		;

		LDA #$20				;($B783)
		STA WindowOptions	   ;($B785)Set some window parameters.
LDA #$04				;
		STA WindowParam		 ;($B78A)

LDA DescBuf			 ;Load first byte from description buffer and remove upper 2 bits.
AND #$3F				;
JMP LookupDescriptions  ;($A790)Get description from tables.

DoDESC:
		JSR GetDescHalves	   ;($B794)($B75D)Get full description and store in work buffer.
JSR CheckAToAn		  ;($B79D)Check if item starts with vowel and convert 'a' to 'an'.
JMP WorkBufEndChar	  ;($B6D0)Place termination character on work buffer.

CheckAToAn:
		JSR WorkBufShift		;($B79D)($B7CB)Shift work buffer to insert character.
		LDA WorkBuffer		  ;($B7A0)Get first character in work buffer.
		CMP #TXT_UPR_A		  ;($B7A3)'A'.
		BEQ VowelFound		  ;($B7A5)A found?  If so, branch to add 'n'.
CMP #TXT_UPR_I		  ;'I'.
BEQ VowelFound		  ;I found?  If so, branch to add 'n'.
		CMP #TXT_UPR_U		  ;($B7AB)'U'.
		BEQ VowelFound		  ;($B7AD)U found?  If so, branch to add 'n'.
		CMP #TXT_UPR_E		  ;($B7AF)'E'.
		BEQ VowelFound		  ;($B7B1)E found?  If so, branch to add 'n'.
		CMP #TXT_UPR_O		  ;($B7B3)'O'.
BNE VowelNotFound	   ;O found?  If so, branch to add 'n'.

VowelNotFound:
		LDA #TL_BLANK_TILE1	 ;($B7B7)
STA WorkBuffer		  ;No vowel at start of description.  Just insert space.
RTS					 ;

VowelFound:
		JSR WorkBufShift		;($B7BD)($B7CB)Shift work buffer to insert character.
LDA #TXT_LWR_N		  ;'n'.
STA WorkBuffer		  ;Insert 'n' into work buffer.
LDA #TL_BLANK_TILE1	 ;
STA WorkBuffer+1		;Insert space into work buffer after 'n'.
		RTS					 ;($B7CA)

WorkBufShift:
LDX #$26				;Prepare to shift 39 bytes.

* LDA WorkBuffer,X		;Move buffer value over 1 byte.
STA WorkBuffer+1,X	  ;
		DEX					 ;($B7D3)More to shift?
BPL -				   ;If so, branch to shift next byte.

INY					 ;Done shifting. Buffer is now 1 byte longer.
		RTS					 ;($B7D7)

;----------------------------------------------------------------------------------------------------

DoSPEL:
		LDA #$09				;($B7D8)Max. buffer length is 9.
		STA SubBufLength		;($B7DA)

LDA DescBuf			 ;Get spell description byte.
JSR WindowGetSpellDesc	 ;($A7EB)Get spell description.
JSR UpdateDescBufferLen	;($B82B)Save desc buffer length and zero index.
		JMP WorkBufEndChar	  ;($B7E5)($B6D0)Place termination character on work buffer.

;----------------------------------------------------------------------------------------------------

DoCOPY:
LDX #$00				;Start at beginning of buffers.

* LDA DescBuf,X		   ;Copy description buffer byte into work buffer.
		STA WorkBuffer,X		;($B7EC)
INX					 ;
		CMP #TXT_SUBEND		 ;($B7F0)End of buffer reached? If not, branch to copy more.
		BNE -				   ;($B7F2)

		LDX #$00				;($B7F4)Reset index.
JMP WorkBufDone		 ;($B667)Done building work buffer.

;----------------------------------------------------------------------------------------------------

DoNAME:
		JSR NameToNameBuf	   ;($B7F9)($B87F)Copy all 8 name bytes to name buffer.
JSR NameBufToWorkBuf	;($B81D)Copy name buffer to work buffer.

BufFinished:
		LDX #$00				;($B7FF)Zero out index.
		JMP WorkBufDone		 ;($B801)($B667)Done building work buffer.

;----------------------------------------------------------------------------------------------------

DoENMY:
LDA EnemyNumber			;Get current enemy number.
JSR GetEnName		   ;($B89F)Put enemy name into name buffer.
		JSR NameBufToWorkBuf	;($B809)($B81D)Copy name buffer to work buffer.
JMP BufFinished		 ;($B7FF)Finish building work buffer.

DoENM2:
		LDA EnemyNumber		 ;($B80F)Get current enemy number.
		JSR GetEnName		   ;($B811)($B89F)Put enemy name into name buffer.
JSR NameBufToWorkBuf	;($B81D)Copy name buffer to work buffer.
		JSR CheckAToAn		  ;($B817)($B79D)Check if item starts with vowel and convert 'a' to 'an'.
		JMP BufFinished		 ;($B81A)($B7FF)Finish building work buffer.

;----------------------------------------------------------------------------------------------------

NameBufToWorkBuf:
LDX #$00				;Zero out index.
		* LDA NameBuffer,X	  ;($B81F)Copy name buffer byte to work buffer.
STA WorkBuffer,X		;

		INX					 ;($B825)
CMP #TXT_SUBEND		 ;Has end of buffer marker been reached?
		BNE -				   ;($B828)If not, branch to copy another byte.
		RTS					 ;($B82A)

;----------------------------------------------------------------------------------------------------

UpdateDescBufferLen:
STY DescriptionLength		  ;Save length of description buffer.
		LDY #$00				;($B82E)Zero index.

;----------------------------------------------------------------------------------------------------

XferTempToWork:
		LDX DescriptionLength   ;($B830)Is there data to transfer?
BEQ NoXfer			  ;If not, branch to exit.

LDA #$00				;Start current index at 0.
STA ThisTempIndex	   ;
LDX SubBufLength		;X stores end index.

* LDA TempBuffer-1,X	  ;Transfer temp buffer byte into work buffer.
		STA WorkBuffer,Y		;($B83F)

DEX					 ;
		INY					 ;($B843)Update indexes.
INC ThisTempIndex	   ;

		LDA ThisTempIndex	   ;($B846)At end of buffer?
		CMP DescriptionLength   ;($B848)
BNE -				   ;If not, branch to get another byte.
RTS					 ;

NoXfer:
		DEY					 ;($B84E)Nothing to transfer. Decrement index and exit.
RTS					 ;

;----------------------------------------------------------------------------------------------------

ClearDialogOutBuf:
		LDX #$00				;($B850)Base of buffer.
LDA #TL_BLANK_TILE1	 ;Blank tile pattern table index.

* STA DialogOutBuf,X	  ;Loop to load blank tiles into the dialog out buffer.
		INX					 ;($B857)
CPX #$B0				;Have 176 bytes been written?
		BCC -				   ;($B85A)If not, branch to continue writing.
		RTS					 ;($B85C)

;----------------------------------------------------------------------------------------------------

DialogToScreenBuf:
LDA #$08				;Total rows=8.
STA RowsRemaining	   ;

LDX #$00				;Zero out WinBufRAM index.
LDY #$00				;Zero out DialogOutBuf index.

NewDialogRow:
LDA #$16				;Total columns = 22.
		STA ColumnsRemaining	;($B867)

CopyDialogByte:
		LDA DialogOutBuf,Y	  ;($B869)Copy dialog buffer to background screen buffer.
STA WinBufRAM+$0265,X   ;

INX					 ;Increment screen buffer index.
		INY					 ;($B870)Increment dialog buffer index.

DEC ColumnsRemaining	   ;Are there stil characters left in current row?
BNE CopyDialogByte	  ;If so, branch to get next character.

TXA					 ;
		CLC					 ;($B876)Move to next row in WinBufRAM by adding
ADC #$0A				;10 to the WinBufRAM index.
TAX					 ;

DEC RowsRemaining	   ;One more row completed.
BNE NewDialogRow		;More rows left to get? If so, branch to get more.
RTS					 ;

;----------------------------------------------------------------------------------------------------

NameToNameBuf:
		LDY #$00				;($B87F)Zero indexes.
		LDX #$00				;($B881)

		* LDA DispName0,X	   ;($B883)
		STA NameBuffer,Y		;($B885)Copy name 2 bytes at a time into name buffer.
LDA DispName4,X		 ;
		STA NameBuffer+4,Y	  ;($B88B)

INX					 ;Increment namme index.
		INY					 ;($B88F)Increment buffer index.

CPY #$04				;Has all 8 bytes been copied?
		BNE -				   ;($B892)If not, branch to copy 2 more bytes.

		LDY #$08				;($B894)Start at last index in name buffer.
		JSR FindNameEnd		 ;($B896)($B8D9)Find index of last character in name buffer.

EndNameBuf:
LDA #TXT_SUBEND		 ;
STA NameBuffer,Y		;Put end of buffer marker after last character in name buffer.
RTS					 ;

;----------------------------------------------------------------------------------------------------

GetEnName:
		CLC					 ;($B89F)
ADC #$01				;Increment enemy number and save it on the stack.
PHA					 ;

		LDA #$00				;($B8A3)Start with first half of name.
		STA WindowDescHalf	  ;($B8A5)

LDA #$0B				;Max buf length of first half of name is 11 characters.
STA SubBufLength		;

PLA					 ;Restore enemy number.
JSR GetEnDescHalf	   ;($A801)Get first half of enemy name.

LDY #$00				;Start at beginning of name buffer.
JSR AddTempBufToNameBuf ;($B8EA)Add temp buffer to name buffer.
		JSR FindNameEnd		 ;($B8B6)($B8D9)Find index of last character in name buffer.

LDA #TL_BLANK_TILE1	 ;Store a blank tile after first half.
		STA NameBuffer,Y		;($B8BB)

INY					 ;
		TYA					 ;($B8BF)Move to next spot in name buffer and store the index.
PHA					 ;

		INC WindowDescHalf	  ;($B8C1)Move to second half of enemy name.

LDA #$09				;Max buf length of second half of name is 9 characters.
STA SubBufLength		;

		LDA DescriptionEntry	;($B8C9)Not used in this set of functions.
		JSR GetEnDescHalf	   ;($B8CB)($A801)Get second half of enemy name.

PLA					 ;Restore index to end of namme buffer.
		TAY					 ;($B8CF)

		JSR AddTempBufToNameBuf ;($B8D0)($B8EA)Add temp buffer to name buffer.
JSR FindNameEnd		 ;($B8D9)Find index of last character in name buffer.
JMP EndNameBuf		  ;($B899)Put end of buffer character in name buffer.

;----------------------------------------------------------------------------------------------------

FindNameEnd:
		LDA NameBuffer-1,Y	  ;($B8D9)Sart at end of name buffer.

CMP #TL_BLANK_TILE2	 ;Is current character not a blank space?
BEQ +				   ;
CMP #TL_BLANK_TILE1	 ;
BNE ++				  ;If not, branch to end.  Last character found.

* DEY					 ;Blank character space found.
		BMI +				   ;($B8E5)If no characters in buffer, branch to end.
		BNE FindNameEnd		 ;($B8E7)If more characters in buffer, branch to process next character.
		* RTS				   ;($B8E9)

;----------------------------------------------------------------------------------------------------

AddTempBufToNameBuf:
LDX SubBufLength		;Get pointer to end of temp buffer.

* LDA TempBuffer-1,X	  ;Append temp buffer to name buffer.
		STA NameBuffer,Y		;($B8F0)

		INY					 ;($B8F3)Increment index in name buffer.
DEX					 ;Decrement index in temp buffer.

		BNE -				   ;($B8F5)More byte to append? if so branch to do more.
		RTS					 ;($B8F7)
RTS					 ;

;----------------------------------------------------------------------------------------------------

CheckBetweenWords:
		CMP #TXT_SUBEND		 ;($B8F9)End of buffer marker.
		BCS NonWordChar		 ;($B8FB)
		CMP #TL_BLANK_TILE1	 ;($B8FD)Blank space.
		BEQ NonWordChar		 ;($B8FF)
		CMP #TXT_PERIOD		 ;($B901)"."(period).
		BEQ NonWordChar		 ;($B903)
		CMP #TXT_COMMA		  ;($B905)","(comma).
		BEQ NonWordChar		 ;($B907)
CMP #TXT_APOS		   ;"'"(apostrophe).
		BEQ NonWordChar		 ;($B90B)
		CMP #TXT_PRD_QUOTE	  ;($B90D)".'"(Period end-quote).
BEQ NonWordChar		 ;

SEC					 ;Alpha-numberic character found. Set carry and return.
		RTS					 ;($B912)

NonWordChar:
CLC					 ;Non-word character found. Clear carry and return.
		RTS					 ;($B914)

;----------------------------------------------------------------------------------------------------

CheckForNewLine:
LDA WindowXPositionAfterWord		   ;Will this word extend to the end of the current text row?
CMP #$16				;If so, branch to move to the next line.
		BCS MoveToNextLine	  ;($B91A)($B924)Move to the next line in the text window.
		RTS					 ;($B91C)

DoNewline:
LDA WindowTextXCoordinate		;Update position after text word with current
		STA WindowXPositionAfterWord;($B91F)cursor position.
BEQ NewlineEnd		  ;At beginning of text line? If so, branch to exit.

MoveToNextLine:
LDX WindowTextYCoordinate		;Move to the next line in the text window.
INX					 ;

		CPX #$08				;($B927)Are we at or beyond the last row in the dialog box?
BCS ScrollDialog		;If so, branch to scroll the dialog window.

		LDA TxtLineSpace		;($B92B)
LSR					 ;
LSR					 ;It looks like there used to be some code for controlling
		EOR #$03				;($B930)how many lines to skip when going to a new line. The value
		CLC					 ;($B932)in TxtLineSpace is always #$08 so the line always increments
ADC WindowTextYCoordinate		;by 1.
STA WindowTextYCoordinate		;

LineDone:
LDA TxtIndent		   ;
		STA WindowXPositionAfterWord;($B93A)Add the indent value to the cursor X position.
		STA WindowTextXCoordinate;($B93D)

CLC					 ;Clear carry to indicate the line was incremented.

NewlineEnd:
		RTS					 ;($B940)End line increment.

;----------------------------------------------------------------------------------------------------

ScrollDialog:
		JSR Scroll1Line		 ;($B941)($B967)Scroll dialog text up by one line.

LDA TxtLineSpace		;Is text double spaced?
		CMP #$04				;($B947)If so, scroll up an additional line.
		BNE ScrollUpdate		;($B949)Else update display with scrolled text.
		JSR Scroll1Line		 ;($B94B)($B967)Scroll dialog text up by one line.

ScrollUpdate:
		LDA #$13				;($B94E)Start dialog scrolling at line 19 on the screen.
		STA DialogScrlY		 ;($B950)

LDA #$00				;Zero out buffer index.
STA DialogScrlInd	   ;

JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.

		* JSR Display2ScrollLines;($B95B)($B990)Display two scrolled lines on screen.
LDA DialogScrlY		 ;
		CMP #$1B				;($B961)Has entire dialog window been updated?
BCC -				   ;If not, branch to update more.
		BCS LineDone			;($B965)($B937)Scroll done, branch to exit.

Scroll1Line:
		LDX #$00				;($B967)Prepare to scroll dialog text.

ScrollDialogLoop:
		LDA DialogOutBuf+$16,X  ;($B969)Get byte to move up one row.
		AND #$7F				;($B96C)
CMP #$76				;Is it a text byte?
BCS NextScrollByte	  ;If not, branch to skip moving it up.

PHA					 ;Get byte to be replaced.
		LDA DialogOutBuf,X	  ;($B973)
AND #$7F				;
CMP #$76				;Is it a text byte?
PLA					 ;
		BCS NextScrollByte	  ;($B97B)If not, branch to skip replacing byte.

		STA DialogOutBuf,X	  ;($B97D)Move text byte up one row.

NextScrollByte:
		INX					 ;($B980)Increment to next byte.
CPX #$9A				;Have all the bytes been moved up?
BNE ScrollDialogLoop	;If not, branch to get next dialog byte.

LDA #TL_BLANK_TILE1	 ;Blank tile,
* STA DialogOutBuf,X	  ;Write blank tiles to the entire text buffer.
INX					 ;
		CPX #$B0				;($B98B)Has 176 bytes been written?
BNE -				   ;If not, branch to write more.
RTS					 ;

;----------------------------------------------------------------------------------------------------

Display2ScrollLines:
		JSR Display1ScrollLine  ;($B990)($B9A0)Write one line of scrolled text to the screen.
		INC DialogScrlY		 ;($B993)Move to next dialog line to scroll up.
JSR Display1ScrollLine  ;($B9A0)Write one line of scrolled text to the screen.
		JSR WaitForNMI		  ;($B999)($FF74)Wait for VBlank interrupt.
		INC DialogScrlY		 ;($B99C)Move to next dialog line to scroll up.
RTS					 ;

Display1ScrollLine:
		LDA DialogScrlY		 ;($B9A0)
		STA ScreenTextYCoordinate;($B9A3)Set indexes to the beginning of the line to scroll.
		LDA #$05				;($B9A6)Dialog line starts on 5th screen tile.
STA ScreenTextXCoordinate	   ;

DisplayScrollLoop:
		LDX DialogScrlInd	   ;($B9AB)
		LDA DialogOutBuf,X	  ;($B9AE)Get dialog buffer byte to update.
		STA PPUDataByte		 ;($B9B1)Put it in the PPU buffer.
JSR WindowCalcPPUAddr	  ;($ADC0)Calculate PPU address for window/text byte.
JSR AddPPUBufferEntry	  ;($C690)Add data to PPU buffer.

INC DialogScrlInd	   ;
INC ScreenTextXCoordinate	   ;Update buffer pointer and x cursor position.
LDA ScreenTextXCoordinate	   ;

CMP #$1B				;Have all 22 text byte in the line been scrolled up?
		BNE DisplayScrollLoop   ;($B9C4)If not, branch to do the next one.
		RTS					 ;($B9C6)

;----------------------------------------------------------------------------------------------------

TextToPPU:
PHA					 ;Save word buffer character.

LDA WindowTextXCoordinate		;Make sure x position before and after a word are the same.
STA WindowXPositionAfterWord		   ;

		JSR CheckForNewLine	 ;($B9CD)($B915)Move text to new line, if necessary.

LDA WindowTextYCoordinate		;Get row number.
JSR CalcWndYByteNum	 ;($BAA6)Calculate the byte number of row start in dialog window.
ADC WindowTextXCoordinate		;Add x position to get final buffer index value.
TAX					 ;Save the index in X.

PLA					 ;Restore the word buffer character.
CMP #TL_BLANK_TILE1	 ;Is it a blank tile?
BEQ CheckXCoordIndent   ;If so, branch to check if the x position is at the indent mark.

CMP #TXT_OPN_QUOTE	  ;Is character an open quote?
BNE CheckNextBufByte	;If so, branch to skip any following spaces.

LDY WindowTextXCoordinate		;
		CPY #$01				;($B9E3)Is the X coord at the indent?
		BNE CheckNextBufByte	;($B9E5)If so, branch to skip any following spaces.

		DEY					 ;($B9E7)Move back a column to line things up properly.
		STY WindowTextXCoordinate;($B9E8)
		DEX					 ;($B9EA)
JMP CheckNextBufByte	;($B9F5)Check next buffer byte.

CheckXCoordIndent:
		LDY WindowTextXCoordinate;($B9EE)Is X position at the indent mark?
		CPY TxtIndent		   ;($B9F0)
		BEQ EndTextToPPU		;($B9F3)If so, branch to end.

CheckNextBufByte:
PHA					 ;Save the word buffer character.
LDA DialogOutBuf,X	  ;Get next word in Dialog buffer
		STA PPUDataByte		 ;($B9F9)and prepare to save it in the PPU.
TAY					 ;
		PLA					 ;($B9FC)Restore original text byte. Is it a blank tile?
CPY #TL_BLANK_TILE1	 ;If so, branch.  This keeps the indent even.
BNE +

STA DialogOutBuf,X	  ;Store original character in PPU data byte.
STA PPUDataByte		 ;

* LDA TxtIndent		   ;Is the text indented?
		BEQ CalcTextWndPos	  ;($BA09)If not, branch to skip text SFX.

		LDA PPUDataByte		 ;($BA0B)Is current PPU data byte a window non-character tile?
		CMP #TL_BLANK_TILE1	 ;($BA0D)
		BCS CalcTextWndPos	  ;($BA0F)If so, branch to skip text SFX.

		LDA WindowTextXCoordinate;($BA11)
		LSR					 ;($BA13)Only play text SFX every other printable character.
BCC CalcTextWndPos	  ;

		LDA #SFX_TEXT		   ;($BA16)Text SFX.
		BRK					 ;($BA18)
.byte $04, $17		  ;($81A0)InitMusicSFX, bank 1.

CalcTextWndPos:
LDA WindowTextXCoordinate		;
CLC					 ;Dialog text columns start on the 5th screen column.
		ADC #$05				;($BA1E)Need to add current dialog column to this offset.
		STA ScreenTextXCoordinate;($BA20)

LDA WindowTextYCoordinate		;
		CLC					 ;($BA25)Dialog text lines start on the 19th screen line.
ADC #$13				;Need to add current dialog line to this offset.
STA ScreenTextYCoordinate	   ;

JSR WindowCalcPPUAddr	  ;($ADC0)Calculate PPU address for window/text byte.
JSR AddPPUBufferEntry	  ;($C690)Add data to PPU buffer.

		LDX MessageSpeed		;($BA31)Load text speed to use as counter to slow text.
* JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.
		DEX					 ;($BA36)Delay based on message speed.
BPL -				   ;Loop to slow text speed.

		INC WindowTextXCoordinate;($BA39)Set pointer to X position for next character.

EndTextToPPU:
RTS					 ;Done witing text character to PPU.

;----------------------------------------------------------------------------------------------------

;This code does not appear to be used.  It looks at a text byte and sets the carry if the character
;is a lowercase vowel or uppercase or a non-alphanumeric character. It clears the carry otherwise.

		LDA PPUDataByte		 ;($BA3C)Prepare to look through vowel table below.
		LDX #$04				;($BA3E)

		* CMP VowelTable,X	  ;($BA40)Is text character a lowercase vowel?
BEQ TextSetCarry		;If so, branch to set carry and exit.
DEX					 ;Done looking through vowel table?
		BPL -				   ;($BA46)If not, branch to look at next entry.

		CMP #$24				;($BA48)Lowercase letters.
		BCC TextClearCarry	  ;($BA4A)Is character lower case? If so, branch to clear carry.

		CMP #$56				;($BA4C)non-alphanumeric characters.
		BCC TextSetCarry		;($BA4E)If uppercase of other character, set carry.

TextClearCarry:
		CLC					 ;($BA50)Clear carry and return.
RTS					 ;

TextSetCarry:
SEC					 ;Set carry and return.
		RTS					 ;($BA53)

VowelTable:
;			  a	i	u	e	o
.byte $0A, $12, $1E, $0E, $18

;----------------------------------------------------------------------------------------------------

DoWait:
		JSR TxtCheckInput	   ;($BA59)($BA97)Check for player button press.
BNE TxtBtnPressed	   ;Has A or B been pressed? If so, branch.

LDA #$10				;Initialize animation with down arrow visible.
STA FrameCounter		;

TxtWaitLoop:
JSR TxtWaitAnim		 ;($BA76)
JSR WaitForNMI		  ;($FF74)Wait for VBlank interrupt.
JSR TxtCheckInput	   ;($BA97)Check for player button press.
		BEQ TxtWaitLoop		 ;($BA6B)Has A or B been pressed? If not, branch to loop.

TxtBtnPressed:
		JSR TxtClearArrow	   ;($BA6D)($BA80)Clear down arrow animation.
		LDA TxtIndent		   ;($BA70)
STA WindowTextXCoordinate		;Start a new line with any active indentation.
RTS					 ;

TxtWaitAnim:
		LDX #$43				;($BA76)Down arrow tile.
		LDA FrameCounter		;($BA78)
		AND #$1F				;($BA7A)Get bottom 5 bits of frame counter.
		CMP #$10				;($BA7C)Is value >= 16?
		BCS +				   ;($BA7E)If so, branch to show down arrow tile.

TxtClearArrow:
		LDX #TL_BLANK_TILE1	 ;($BA80)Blank tile.

		* STX PPUDataByte	   ;($BA82)Prepare to load arrow animation tile into PPU.

LDA #$10				;Place wait animation tile in the middle X position on the screen.
STA ScreenTextXCoordinate	   ;

LDA WindowTextYCoordinate		;
		CLC					 ;($BA8B)Dialog window starts 19 tiles from top of screen.
ADC #$13				;This converts window Y coords to screen Y coords.
STA ScreenTextYCoordinate	   ;

		JSR WindowCalcPPUAddr   ;($BA91)($ADC0)Calculate PPU address for window/text byte.
JMP AddPPUBufferEntry	  ;($C690)Add data to PPU buffer.

TxtCheckInput:
		JSR GetJoypadStatus	 ;($BA97)($C608)Get input button presses.
LDA JoypadBtns		  ;Get joypad button presses.
AND #IN_A_OR_B		  ;Mask off everything except A and B buttons.
RTS					 ;

;----------------------------------------------------------------------------------------------------

IncDialogPtr:
		INC DialogPtrLB		 ;($BA9F)
		BNE +				   ;($BAA1)Increment dialog pointer.
		INC DialogPtrUB		 ;($BAA3)
		* RTS				   ;($BAA5)

;----------------------------------------------------------------------------------------------------

CalcWndYByteNum:
STA TextRowNum		   ;Store row number in lower byte of multiplicand word.
		LDA #$00				;($BAA8)
		STA TextRowStart		;($BAAA)Upper byte is always 0. Always start at beginning of row.

		LDX #TextRowNum		 ;($BAAC)Index to multiplicand word.
		LDA #$16				;($BAAE)22 text characters per line.
		JSR IndexedMult		 ;($BAB0)($A6EB)Find buffer index for start of row.

LDA TextRowNum		   ;
		CLC					 ;($BAB5)Store results in A and return.
RTS					 ;

;----------------------------------------------------------------------------------------------------

;Item descriptions, first table, first half.
ItemNames11Table:
;			  B	a	m	b	o	o
.byte $25, $0A, $16, $0B, $18, $18, $FF
;			  C	l	u	b
		.byte $26, $15, $1E, $0B, $FF;($BABE)
;			  C	o	p	p	e	r
		.byte $26, $18, $19, $19, $0E, $1B, $FF;($BAC3)
;			  H	a	n	d
		.byte $2B, $0A, $17, $0D, $FF;($BACA)
;			  B	r	o	a	d
		.byte $25, $1B, $18, $0A, $0D, $FF;($BACF)
;			  F	l	a	m	e
		.byte $29, $15, $0A, $16, $0E, $FF;($BAD5)
;			  E	r	d	r	i	c	k	'	s
.byte $28, $1B, $0D, $1B, $12, $0C, $14, $40, $1C, $FF
;			  C	l	o	t	h	e	s
.byte $26, $15, $18, $1D, $11, $0E, $1C, $FF
;			  L	e	a	t	h	e	r
		.byte $2F, $0E, $0A, $1D, $11, $0E, $1B, $FF;($BAED)
;			  C	h	a	i	n
		.byte $26, $11, $0A, $12, $17, $FF;($BAF5)
;			  H	a	l	f
		.byte $2B, $0A, $15, $0F, $FF;($BAFB)
;			  F	u	l	l
.byte $29, $1E, $15, $15, $FF
;			  M	a	g	i	c
		.byte $30, $0A, $10, $12, $0C, $FF;($BB05)
;			  E	r	d	r	i	c	k	'	s
		.byte $28, $1B, $0D, $1B, $12, $0C, $14, $40, $1C, $FF;($BB0B)
;			  S	m	a	l	l
		.byte $36, $16, $0A, $15, $15, $FF;($BB15)
;			  L	a	r	g	e
		.byte $2F, $0A, $1B, $10, $0E, $FF;($BB1B)
;			  S	i	l	v	e	r
.byte $36, $12, $15, $1F, $0E, $1B, $FF
;			  H	e	r	b
.byte $2B, $0E, $1B, $0B, $FF
;			  T	o	r	c	h
.byte $37, $18, $1B, $0C, $11, $FF
;			  D	r	a	g	o	n	'	s
		.byte $27, $1B, $0A, $10, $18, $17, $40, $1C, $FF;($BB33)
;			  W	i	n	g	s
		.byte $3A, $12, $17, $10, $1C, $FF;($BB3C)
;			  M	a	g	i	c
.byte $30, $0A, $10, $12, $0C, $FF
;			  F	a	i	r	y
		.byte $29, $0A, $12, $1B, $22, $FF;($BB48)
;			  B	a	l	l	_	o	f
		.byte $25, $0A, $15, $15, $5F, $18, $0F, $FF;($BB4E)
;			  T	a	b	l	e	t
		.byte $37, $0A, $0B, $15, $0E, $1D, $FF;($BB56)
;			  F	a	i	r	y
.byte $29, $0A, $12, $1B, $22, $FF
;			  S	i	l	v	e	r
.byte $36, $12, $15, $1F, $0E, $1B, $FF
;			  S	t	a	f	f	_	o	f
.byte $36, $1D, $0A, $0F, $0F, $5F, $18, $0F, $FF
;			  S	t	o	n	e	s	_	o	f
.byte $36, $1D, $18, $17, $0E, $1C, $5F, $18, $0F, $FF
;			  G	w	a	e	l	i	n	'	s
		.byte $2A, $20, $0A, $0E, $15, $12, $17, $40, $1C, $FF;($BB7D)
;			  R	a	i	n	b	o	w
		.byte $35, $0A, $12, $17, $0B, $18, $20, $FF;($BB87)

;----------------------------------------------------------------------------------------------------

;Item descriptions, second table, first half.
ItemNames21Table:
;			  C	u	r	s	e	d
.byte $26, $1E, $1B, $1C, $0E, $0D, $FF
;			  D	e	a	t	h
.byte $27, $0E, $0A, $1D, $11, $FF
;			  F	i	g	h	t	e	r	'	s
.byte $29, $12, $10, $11, $1D, $0E, $1B, $40, $1C, $FF
;			  E	r	d	r	i	c	k	'	s
		.byte $28, $1B, $0D, $1B, $12, $0C, $14, $40, $1C, $FF;($BBA6)
;			  S	e	c	r	e	t
		.byte $36, $0E, $0C, $1B, $0E, $1D, $FF;($BBB0)

;----------------------------------------------------------------------------------------------------

;Item descriptions, first table, second half.
ItemNames12Table:
;			  P	o	l	e
.byte $33, $18, $15, $0E, $FF
;			 None
		.byte $FF			   ;($BBBC)
;			  S	w	o	r	d
.byte $36, $20, $18, $1B, $0D, $FF
;			  A	x	e
		.byte $24, $21, $0E, $FF;($BBC3)
;			  S	w	o	r	d
.byte $36, $20, $18, $1B, $0D, $FF
;			  S	w	o	r	d
.byte $36, $20, $18, $1B, $0D, $FF
;			  S	w	o	r	d
		.byte $36, $20, $18, $1B, $0D, $FF;($BBD3)
;			 None
.byte $FF
;			  A	r	m	o	r
.byte $24, $1B, $16, $18, $1B, $FF
;			  M	a	i	l
.byte $30, $0A, $12, $15, $FF
;			  P	l	a	t	e
.byte $33, $15, $0A, $1D, $0E, $FF
;			  P	l	a	t	e
		.byte $33, $15, $0A, $1D, $0E, $FF;($BBEB)
;			  A	r	m	o	r
		.byte $24, $1B, $16, $18, $1B, $FF;($BBF1)
;			  A	r	m	o	r
.byte $24, $1B, $16, $18, $1B, $FF
;			  S	h	i	e	l	d
.byte $36, $11, $12, $0E, $15, $0D, $FF
;			  S	h	i	e	l	d
.byte $36, $11, $12, $0E, $15, $0D, $FF
;			  S	h	i	e	l	d
		.byte $36, $11, $12, $0E, $15, $0D, $FF;($BC0B)
;			 None
		.byte $FF			   ;($BC12)
;			 None
.byte $FF
;			  S	c	a	l	e
		.byte $36, $0C, $0A, $15, $0E, $FF;($BC14)
;			 None
		.byte $FF			   ;($BC1A)
;			  K	e	y
		.byte $2E, $0E, $22, $FF;($BC1B)
;			  W	a	t	e	r
.byte $3A, $0A, $1D, $0E, $1B, $FF
;			  L	i	g	h	t
.byte $2F, $12, $10, $11, $1D, $FF
;			 None
.byte $FF
;			  F	l	u	t	e
		.byte $29, $15, $1E, $1D, $0E, $FF;($BC2C)
;			  H	a	r	p
		.byte $2B, $0A, $1B, $19, $FF;($BC32)
;			  R	a	i	n
.byte $35, $0A, $12, $17, $FF
;			  S	u	n	l	i	g	h	t
		.byte $36, $1E, $17, $15, $12, $10, $11, $1D, $FF;($BC3C)
;			  L	o	v	e
.byte $2F, $18, $1F, $0E, $FF
;			  D	r	o	p
		.byte $27, $1B, $18, $19, $FF;($BC4A)

;----------------------------------------------------------------------------------------------------

;Item descriptions, second table, second half.
ItemNames22Table:
;			  B	e	l	t
		.byte $25, $0E, $15, $1D, $FF;($BC4F)
;			  N	e	c	k	l	a	c	e
		.byte $31, $0E, $0C, $14, $15, $0A, $0C, $0E, $FF;($BC54)
;			  R	i	n	g
.byte $35, $12, $17, $10, $FF
;			  T	o	k	e	n
		.byte $37, $18, $14, $0E, $17, $FF;($BC62)
;			  P	a	s	s	a	g	e
		.byte $33, $0A, $1C, $1C, $0A, $10, $0E, $FF;($BC68)

;----------------------------------------------------------------------------------------------------

;Enemy names, first half.
EnemyNames1Table:
;			  S	l	i	m	e
		.byte $36, $15, $12, $16, $0E, $FF;($BC70)
;			  R	e	d
		.byte $35, $0E, $0D, $FF;($BC76)
;			  D	r	a	k	e	e
		.byte $27, $1B, $0A, $14, $0E, $0E, $FF;($BC7A)
;			  G	h	o	s	t
.byte $2A, $11, $18, $1C, $1D, $FF
;			  M	a	g	i	c	i	a	n
		.byte $30, $0A, $10, $12, $0C, $12, $0A, $17, $FF;($BC87)
;			  M	a	g	i	d	r	a	k	e	e
		.byte $30, $0A, $10, $12, $0D, $1B, $0A, $14, $0E, $0E, $FF;($BC90)
;			  S	c	o	r	p	i	o	n
		.byte $36, $0C, $18, $1B, $19, $12, $18, $17, $FF;($BC9B)
;			  D	r	u	i	n
		.byte $27, $1B, $1E, $12, $17, $FF;($BCA4)
;			  P	o	l	t	e	r	g	e	i	s	t
		.byte $33, $18, $15, $1D, $0E, $1B, $10, $0E, $12, $1C, $1D, $FF;($BCAA)
;			  D	r	o	l	l
.byte $27, $1B, $18, $15, $15, $FF
;			  D	r	a	k	e	e	m	a
		.byte $27, $1B, $0A, $14, $0E, $0E, $16, $0A, $FF;($BCBC)
;			  S	k	e	l	e	t	o	n
.byte $36, $14, $0E, $15, $0E, $1D, $18, $17, $FF
;			  W	a	r	l	o	c	k
		.byte $3A, $0A, $1B, $15, $18, $0C, $14, $FF;($BCCE)
;			  M	e	t	a	l
.byte $30, $0E, $1D, $0A, $15, $FF
;			  W	o	l	f
		.byte $3A, $18, $15, $0F, $FF;($BCDC)
;			  W	r	a	i	t	h
.byte $3A, $1B, $0A, $12, $1D, $11, $FF
;			  M	e	t	a	l
		.byte $30, $0E, $1D, $0A, $15, $FF;($BCE8)
;			  S	p	e	c	t	e	r
.byte $36, $19, $0E, $0C, $1D, $0E, $1B, $FF
;			  W	o	l	f	l	o	r	d
		.byte $3A, $18, $15, $0F, $15, $18, $1B, $0D, $FF;($BCF6)
;			  D	r	u	i	n	l	o	r	d
.byte $27, $1B, $1E, $12, $17, $15, $18, $1B, $0D, $FF
;			  D	r	o	l	l	m	a	g	i
.byte $27, $1B, $18, $15, $15, $16, $0A, $10, $12, $FF
;			  W	y	v	e	r	n
.byte $3A, $22, $1F, $0E, $1B, $17, $FF
;			  R	o	g	u	e
		.byte $35, $18, $10, $1E, $0E, $FF;($BD1A)
;			  W	r	a	i	t	h
		.byte $3A, $1B, $0A, $12, $1D, $11, $FF;($BD20)
;			  G	o	l	e	m
.byte $2A, $18, $15, $0E, $16, $FF
;			  G	o	l	d	m	a	n
.byte $2A, $18, $15, $0D, $16, $0A, $17, $FF
;			  K	n	i	g	h	t
.byte $2E, $17, $12, $10, $11, $1D, $FF
;			  M	a	g	i	w	y	v	e	r	n
.byte $30, $0A, $10, $12, $20, $22, $1F, $0E, $1B, $17, $FF
;			  D	e	m	o	n
		.byte $27, $0E, $16, $18, $17, $FF;($BD47)
;			  W	e	r	e	w	o	l	f
.byte $3A, $0E, $1B, $0E, $20, $18, $15, $0F, $FF
;			  G	r	e	e	n
.byte $2A, $1B, $0E, $0E, $17, $FF
;			  S	t	a	r	w	y	v	e	r	n
.byte $36, $1D, $0A, $1B, $20, $22, $1F, $0E, $1B, $17, $FF
;			  W	i	z	a	r	d
.byte $3A, $12, $23, $0A, $1B, $0D, $FF
;			  A	x	e
.byte $24, $21, $0E, $FF
;			  B	l	u	e
.byte $25, $15, $1E, $0E, $FF
;			  S	t	o	n	e	m	a	n
.byte $36, $1D, $18, $17, $0E, $16, $0A, $17, $FF
;			  A	r	m	o	r	e	d
		.byte $24, $1B, $16, $18, $1B, $0E, $0D, $FF;($BD80)
;			  R	e	d
.byte $35, $0E, $0D, $FF
;			  D	r	a	g	o	n	l	o	r	d
.byte $27, $1B, $0A, $10, $18, $17, $15, $18, $1B, $0D, $FF
;			  D	r	a	g	o	n	l	o	r	d
.byte $27, $1B, $0A, $10, $18, $17, $15, $18, $1B, $0D, $FF

;----------------------------------------------------------------------------------------------------

;Enemy names, second half.
EnemyNames2Table:
;			 None
		.byte $FF			   ;($BDA2)
;			  S	l	i	m	e
.byte $36, $15, $12, $16, $0E, $FF
;			 None
.byte $FF
;			 None
		.byte $FF			   ;($BDAA)
;			 None
.byte $FF
;			 None
		.byte $FF			   ;($BDAC)
;			 None
.byte $FF
;			 None
.byte $FF
;			 None
.byte $FF
;			 None
		.byte $FF			   ;($BDB0)
;			 None
.byte $FF
;			 None
.byte $FF
;			 None
.byte $FF
;			  S	c	o	r	p	i	o	n
.byte $36, $0C, $18, $1B, $19, $12, $18, $17, $FF
;			 None
.byte $FF
;			 None
.byte $FF
;			  S	l	i	m	e
.byte $36, $15, $12, $16, $0E, $FF
;			 None
.byte $FF
;			 None
.byte $FF
;			 None
.byte $FF
;			 None
.byte $FF
;			 None
.byte $FF
;			  S	c	o	r	p	i	o	n
.byte $36, $0C, $18, $1B, $19, $12, $18, $17, $FF
;			  K	n	i	g	h	t
.byte $2E, $17, $12, $10, $11, $1D, $FF
;			 None
		.byte $FF			   ;($BDDA)
;			 None
		.byte $FF			   ;($BDDB)
;			 None
.byte $FF
;			 None
.byte $FF
;			  K	n	i	g	h	t
		.byte $2E, $17, $12, $10, $11, $1D, $FF;($BDDE)
;			 None
		.byte $FF			   ;($BDE5)
;			  D	r	a	g	o	n
.byte $27, $1B, $0A, $10, $18, $17, $FF
;			 None
		.byte $FF			   ;($BDED)
;			 None
		.byte $FF			   ;($BDEE)
;			  K	n	i	g	h	t
.byte $2E, $17, $12, $10, $11, $1D, $FF
;			  D	r	a	g	o	n
		.byte $27, $1B, $0A, $10, $18, $17, $FF;($BDF6)
;			 None
.byte $FF
;			  K	n	i	g	h	t
		.byte $2E, $17, $12, $10, $11, $1D, $FF;($BDFE)
;			  D	r	a	g	o	n
		.byte $27, $1B, $0A, $10, $18, $17, $FF;($BE05)
;			 None
		.byte $FF			   ;($BE0C)
;			 None
		.byte $FF			   ;($BE0D)

;----------------------------------------------------------------------------------------------------

WindowCostTblPtr:
		.word WindowCostTbl	 ;($BE0E)($BE10)Pointer to table below.

WindowCostTbl:
		.word $000A			 ;($BE10)Bamboo pole		- 10	gold.
		.word $003C			 ;($BE12)Club			   - 60	gold.
		.word $00B4			 ;($BE14)Copper sword	   - 180   gold.
		.word $0230			 ;($BE16)Hand axe		   - 560   gold.
		.word $05DC			 ;($BE18)Broad sword		- 1500  gold.
.word $2648			 ;Flame sword		- 9800  gold.
		.word $0002			 ;($BE1C)Erdrick's sword	- 2	 gold.
		.word $0014			 ;($BE1E)Clothes			- 20	gold.
		.word $0046			 ;($BE20)Leather armor	  - 70	gold.
		.word $012C			 ;($BE22)Chain mail		 - 300   gold.
		.word $03E8			 ;($BE24)Half plate		 - 1000  gold.
		.word $0BB8			 ;($BE26)Full plate		 - 3000  gold.
		.word $1E14			 ;($BE28)Magic armor		- 7700  gold.
.word $0002			 ;Erdrick's armor	- 2	 gold.
		.word $005A			 ;($BE2C)Small shield	   - 90	gold.
		.word $0320			 ;($BE2E)Large shield	   - 800   gold.
		.word $39D0			 ;($BE30)Silver shield	  - 14800 gold.
		.word $0018			 ;($BE32)Herb			   - 24	gold.
		.word $0008			 ;($BE34)Torch			  - 8	 gold.
		.word $0014			 ;($BE36)Dragon's scale	 - 20	gold.
		.word $0046			 ;($BE38)Wings			  - 70	gold.
.word $0035			 ;Magic key		  - 53	gold.
		.word $0026			 ;($BE3C)Fairy water		- 38	gold.
		.word $0000			 ;($BE3E)Ball of light	  - 0	 gold.
		.word $0000			 ;($BE40)Tablet			 - 0	 gold.
		.word $0000			 ;($BE42)Fairy flute		- 0	 gold.
		.word $0000			 ;($BE44)Silver harp		- 0	 gold.
		.word $0000			 ;($BE46)Staff of rain	  - 0	 gold.
		.word $0000			 ;($BE48)Stones of sunlight - 0	 gold.
.word $0000			 ;Gwaelin's love	 - 0	 gold.
		.word $0000			 ;($BE4C)Stones of sunlight - 0	 gold.
.word $0168			 ;Cursed belt		- 360   gold.
		.word $0960			 ;($BE50)Death necklace	 - 2400  gold.
		.word $001E			 ;($BE52)Fighter's ring	 - 30	gold.
.word $0000			 ;Erdrick's token	- 0	 gold.

;----------------------------------------------------------------------------------------------------

;Spell nammes.  Unlike the other tables, the spell names do not have a second half.

;			  H	E	A	L
		.byte $2B, $28, $24, $2F, $FF;($BE56)
;			  H	U	R	T
.byte $2B, $38, $35, $37, $FF
;			  S	L	E	E	P
.byte $36, $2F, $28, $28, $33, $FF
;			  R	A	D	I	A	N	T
		.byte $35, $24, $27, $2C, $24, $31, $37, $FF;($BE66)
;			  S	T	O	P	S	P	E	L	L
		.byte $36, $37, $32, $33, $36, $33, $28, $2F, $2F, $FF;($BE6E)
;			  O	U	T	S	I	D	E
		.byte $32, $38, $37, $36, $2C, $27, $28, $FF;($BE78)
;			  R	E	T	U	R	N
		.byte $35, $28, $37, $38, $35, $31, $FF;($BE80)
;			  R	E	P	E	L
		.byte $35, $28, $33, $28, $2F, $FF;($BE87)
;			  H	E	A	L	M	O	R	E
.byte $2B, $28, $24, $2F, $30, $32, $35, $28, $FF
;			  H	U	R	T	M	O	R	E
		.byte $2B, $38, $35, $37, $30, $32, $35, $28, $FF;($BE96)

;----------------------------------------------------------------------------------------------------

;Unused.
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BE9F)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BEAF)
.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BEEF)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BEFF)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BF0F)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BF1F)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BF2F)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BF3F)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BF4F)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BF5F)
.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BF7F)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BF8F)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BF9F)
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BFAF)
.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF
		.byte $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF, $FF;($BFCF)

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