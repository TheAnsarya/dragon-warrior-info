;=================================================================================
; Dragon Warrior - Complete ROM Assembly
; Master file that assembles header + all PRG banks + CHR-ROM
;=================================================================================

; iNES Header (16 bytes at file offset 0x0000)
.include "Header.asm"

;=================================================================================
; PRG-ROM (64KB = 4 banks of 16KB each)
;=================================================================================

; Ensure we're at correct file position after header
.advance $0010

; PRG Bank 0: CPU $8000-$BFFF (file $0010-$400F) - Fixed bank
.include "Bank00.asm"

; Move to Bank 1 file position
.advance $4010

; PRG Bank 1: CPU $8000-$BFFF when assembled (file $4010-$800F) - Switchable bank
.include "Bank01.asm"

; Move to Bank 2 file position
.advance $8010

; PRG Bank 2: CPU $8000-$BFFF when assembled (file $8010-$C00F) - Switchable bank
.include "Bank02.asm"

; Move to Bank 3 file position
.advance $C010

; PRG Bank 3: CPU $C000-$FFFF when assembled (file $C010-$1000F) - Switchable bank
.include "Bank03.asm"

;=================================================================================
; CHR-ROM (16KB = 2 banks of 8KB each) - File offset $10010-$14010
;=================================================================================

; Move to CHR-ROM file position
.advance $10010

; Extract CHR-ROM from reference ROM and include it
; For now we'll use incbin to copy the CHR data directly
.incbin "chr_rom.bin"

; Expected end: file offset $14010 (81,936 bytes total)
