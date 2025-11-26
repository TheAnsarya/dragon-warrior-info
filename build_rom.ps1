#!/usr/bin/env powershell
<#
.SYNOPSIS
Dragon Warrior ROM Builder - Assemble from source ASM files

.DESCRIPTION
Builds a complete Dragon Warrior NES ROM by:
1. Assembling the iNES header
2. Assembling each PRG bank separately (Bank00, Bank01, Bank02, Bank03)
3. Extracting CHR-ROM from reference ROM
4. Concatenating everything into final ROM file
5. Comparing against reference ROM

.EXAMPLE
.\build_rom.ps1
#>

$ErrorActionPreference = "Stop"

# Paths
$RootDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
$SourceDir = Join-Path $RootDir "source_files"
$BuildDir = Join-Path $RootDir "build"
$OpopisExe = Join-Path $RootDir "Ophis" | Join-Path -ChildPath "ophis.exe"
$RomsDir = Join-Path $RootDir "roms"
# Hardcoded reference ROM path (bracket escaping issue with dynamic discovery)
$ReferenceROM = "$RootDir\roms\Dragon Warrior (U) (PRG1) [!].nes"
$OutputROM = Join-Path $BuildDir "dragon_warrior_rebuilt.nes"

# Create build directory
if (-not (Test-Path $BuildDir)) {
	New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

Write-Host "🏗️  Dragon Warrior ROM Builder" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

# Step 1: Assemble Header
Write-Host "[1/6] Assembling iNES header..." -ForegroundColor Yellow
Push-Location $SourceDir
& $OpopisExe Header.asm (Join-Path $BuildDir "header.bin") 2>&1 | Out-Null
Pop-Location

$headerSize = (Get-Item (Join-Path $BuildDir "header.bin")).Length
if ($headerSize -ne 16) {
	Write-Host "❌ Error: Header should be 16 bytes, got $headerSize" -ForegroundColor Red
	exit 1
}
Write-Host "   ✓ Header: $headerSize bytes" -ForegroundColor Green

# Step 2: Assemble PRG Banks
$banks = @("Bank00", "Bank01", "Bank02", "Bank03")
$bankFiles = @()

foreach ($bank in $banks) {
	$stepNum = $banks.IndexOf($bank) + 2
	Write-Host "[$stepNum/6] Assembling $bank..." -ForegroundColor Yellow

	$bankOutput = Join-Path $BuildDir "$($bank.ToLower()).bin"
	Push-Location $SourceDir
	& $OpopisExe "$bank.asm" $bankOutput 2>&1 | Out-Null
	Pop-Location

	$bankSize = (Get-Item $bankOutput).Length
	$expectedSize = 16384  # 16KB

	if ($bankSize -ne $expectedSize) {
		Write-Host "   ⚠️  Warning: $bank is $bankSize bytes (expected $expectedSize)" -ForegroundColor Yellow
	} else {
		Write-Host "   ✓ ${bank}: $bankSize bytes" -ForegroundColor Green
	}

	$bankFiles += $bankOutput
}

# Step 6: Extract CHR-ROM from reference
Write-Host "[6/6] Extracting CHR-ROM from reference ROM..." -ForegroundColor Yellow

# First check if chr_rom.bin already exists in source_files
$sourceChrRom = Join-Path $SourceDir "chr_rom.bin"
if (Test-Path $sourceChrRom) {
	# Copy from source_files
	$chrOutput = Join-Path $BuildDir "chr_rom.bin"
	Copy-Item $sourceChrRom $chrOutput -Force
	$chrSize = (Get-Item $chrOutput).Length
	Write-Host "   ✓ CHR-ROM (from source_files): $chrSize bytes" -ForegroundColor Green
} elseif ($ReferenceROM -and (Test-Path $ReferenceROM)) {
	# Extract CHR-ROM from reference (starts at 0x10010, 16KB)
	$romData = [System.IO.File]::ReadAllBytes($ReferenceROM)
	$chrStart = 0x10010
	$chrSize = 0x4000  # 16KB
	$chrData = $romData[$chrStart..($chrStart + $chrSize - 1)]

	$chrOutput = Join-Path $BuildDir "chr_rom.bin"
	[System.IO.File]::WriteAllBytes($chrOutput, $chrData)
	Write-Host "   ✓ CHR-ROM: $chrSize bytes" -ForegroundColor Green
} else {
	Write-Host "   ⚠️  No CHR-ROM source found" -ForegroundColor Yellow
	Write-Host "   Using placeholder CHR-ROM" -ForegroundColor Yellow

	# Create empty CHR-ROM
	$chrData = New-Object byte[] 16384
	$chrOutput = Join-Path $BuildDir "chr_rom.bin"
	[System.IO.File]::WriteAllBytes($chrOutput, $chrData)
}

# Step 7: Concatenate all parts
Write-Host "`n📦 Creating final ROM..." -ForegroundColor Cyan

$parts = @(
	(Join-Path $BuildDir "header.bin"),
	$bankFiles[0],
	$bankFiles[1],
	$bankFiles[2],
	$bankFiles[3],
	$chrOutput
)

$finalROM = @()
foreach ($part in $parts) {
	$data = [System.IO.File]::ReadAllBytes($part)
	$finalROM += $data
}

[System.IO.File]::WriteAllBytes($OutputROM, $finalROM)

$totalSize = (Get-Item $OutputROM).Length
Write-Host "   ✓ Final ROM: $totalSize bytes ($([math]::Round($totalSize/1024, 2)) KB)" -ForegroundColor Green

# Step 8: Compare with reference
if (Test-Path $ReferenceROM) {
	Write-Host "`n📊 Comparing with reference ROM..." -ForegroundColor Cyan

	$refData = [System.IO.File]::ReadAllBytes($ReferenceROM)
	$builtData = [System.IO.File]::ReadAllBytes($OutputROM)

	if ($refData.Length -ne $builtData.Length) {
		Write-Host "   ⚠️  Size mismatch: Reference=$($refData.Length) Built=$($builtData.Length)" -ForegroundColor Yellow
	} else {
		$differences = 0
		$firstDiff = -1

		for ($i = 0; $i -lt $refData.Length; $i++) {
			if ($refData[$i] -ne $builtData[$i]) {
				$differences++
				if ($firstDiff -eq -1) {
					$firstDiff = $i
				}
			}
		}

		if ($differences -eq 0) {
			Write-Host "   ✅ PERFECT MATCH! ROM is identical to reference." -ForegroundColor Green
		} else {
			Write-Host "   ⚠️  Found $differences byte differences" -ForegroundColor Yellow
			Write-Host "   First difference at offset 0x$($firstDiff.ToString('X6'))" -ForegroundColor Yellow
		}
	}
}

Write-Host "`n✅ Build complete!" -ForegroundColor Green
Write-Host "Output: $OutputROM`n" -ForegroundColor White
