#!/usr/bin/env powershell
<#
.SYNOPSIS
Enhanced Dragon Warrior ROM Builder with PRG0/PRG1 auto-detection and comprehensive reporting

.DESCRIPTION
Builds Dragon Warrior NES ROM with:
- Automatic PRG0/PRG1 version detection
- Detailed assembly reports
- Byte-level comparison analysis
- Build verification
- Error handling and logging

.PARAMETER Version
Target ROM version (PRG0 or PRG1). Auto-detected if not specified.

.PARAMETER Verbose
Enable detailed logging

.PARAMETER Report
Generate detailed build report

.EXAMPLE
.\build_enhanced.ps1 -Version PRG1 -Report
#>

[CmdletBinding()]
param(
    [ValidateSet("PRG0", "PRG1", "Auto")]
    [string]$Version = "Auto",
    
    [switch]$Report,
    [switch]$Clean
)

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

# === Configuration ===
$RootDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
$SourceDir = Join-Path $RootDir "source_files"
$BuildDir = Join-Path $RootDir "build"
$ReportsDir = Join-Path $BuildDir "reports"
$OpopisExe = Join-Path $RootDir "Ophis" "ophis.exe"
$RomsDir = Join-Path $RootDir "roms"
$PRG0_ROM = Join-Path $RomsDir "Dragon Warrior (U) (PRG0) [!].nes"
$PRG1_ROM = Join-Path $RomsDir "Dragon Warrior (U) (PRG1) [!].nes"

# Build time tracking
$BuildStartTime = Get-Date

# === Helper Functions ===
function Write-BuildLog {
    param([string]$Message, [string]$Level = "INFO")
    
    $timestamp = Get-Date -Format "HH:mm:ss.fff"
    $color = switch ($Level) {
        "ERROR" { "Red" }
        "WARN"  { "Yellow" }
        "SUCCESS" { "Green" }
        "INFO"  { "Cyan" }
        default { "White" }
    }
    
    Write-Host "[$timestamp] " -NoNewline -ForegroundColor DarkGray
    Write-Host "$Level " -NoNewline -ForegroundColor $color
    Write-Host $Message -ForegroundColor White
}

function Test-Prerequisites {
    Write-BuildLog "Checking prerequisites..." "INFO"
    
    # Check Ophis
    if (-not (Test-Path $OpopisExe)) {
        Write-BuildLog "Ophis assembler not found at: $OpopisExe" "ERROR"
        return $false
    }
    
    # Check source files
    $requiredFiles = @("Header.asm", "Bank00.asm", "Bank01.asm", "Bank02.asm", "Bank03.asm")
    foreach ($file in $requiredFiles) {
        $path = Join-Path $SourceDir $file
        if (-not (Test-Path $path)) {
            Write-BuildLog "Required source file not found: $file" "ERROR"
            return $false
        }
    }
    
    Write-BuildLog "All prerequisites satisfied" "SUCCESS"
    return $true
}

function Get-ROMVersion {
    param([string]$RomPath)
    
    if (-not (Test-Path $RomPath)) {
        return $null
    }
    
    $data = [System.IO.File]::ReadAllBytes($RomPath)
    
    # Check PRG0 vs PRG1 signature bytes
    # PRG0: 0x3FAE=0x37, 0x3FAF=0x32, 0xAF7C=0xEF
    # PRG1: 0x3FAE=0x32, 0x3FAF=0x29, 0xAF7C=0xF0
    
    if ($data[0x3FAE] -eq 0x32 -and $data[0x3FAF] -eq 0x29 -and $data[0xAF7C] -eq 0xF0) {
        return "PRG1"
    }
    elseif ($data[0x3FAE] -eq 0x37 -and $data[0x3FAF] -eq 0x32 -and $data[0xAF7C] -eq 0xEF) {
        return "PRG0"
    }
    else {
        return "Unknown"
    }
}

function Compare-ROMs {
    param(
        [byte[]]$Reference,
        [byte[]]$Built,
        [string]$OutputPath
    )
    
    $differences = @()
    
    for ($i = 0; $i -lt $Reference.Length; $i++) {
        if ($Reference[$i] -ne $Built[$i]) {
            $differences += [PSCustomObject]@{
                Offset = "0x{0:X6}" -f $i
                Reference = "0x{0:X2}" -f $Reference[$i]
                Built = "0x{0:X2}" -f $Built[$i]
                Bank = if ($i -lt 0x10) { "Header" } 
                       elseif ($i -lt 0x4010) { "Bank00" }
                       elseif ($i -lt 0x8010) { "Bank01" }
                       elseif ($i -lt 0xC010) { "Bank02" }
                       elseif ($i -lt 0x10010) { "Bank03" }
                       else { "CHR-ROM" }
            }
        }
    }
    
    # Generate comparison report
    if ($OutputPath -and $differences.Count -gt 0) {
        $report = @"
Dragon Warrior ROM Comparison Report
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
================================================================================

Total Differences: $($differences.Count)

"@
        
        foreach ($diff in $differences) {
            $report += "Offset: $($diff.Offset) | Bank: $($diff.Bank) | Ref: $($diff.Reference) | Built: $($diff.Built)`n"
        }
        
        $report | Out-File $OutputPath -Encoding UTF8
    }
    
    return $differences
}

function New-BuildReport {
    param(
        [hashtable]$BuildInfo,
        [string]$OutputPath
    )
    
    $duration = $BuildInfo.EndTime - $BuildInfo.StartTime
    
    $report = @"
================================================================================
DRAGON WARRIOR ROM BUILD REPORT
================================================================================
Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")
Build Duration: $($duration.TotalSeconds.ToString("F2"))s

TARGET CONFIGURATION
--------------------
ROM Version: $($BuildInfo.TargetVersion)
Reference ROM: $($BuildInfo.ReferenceROM)
Output ROM: $($BuildInfo.OutputROM)

BUILD COMPONENTS
----------------
Header:  $($BuildInfo.HeaderSize) bytes
Bank00:  $($BuildInfo.Bank00Size) bytes ($(if($BuildInfo.Bank00Size -eq 16384){"✓"}else{"✗"}))
Bank01:  $($BuildInfo.Bank01Size) bytes ($(if($BuildInfo.Bank01Size -eq 16384){"✓"}else{"✗"}))
Bank02:  $($BuildInfo.Bank02Size) bytes ($(if($BuildInfo.Bank02Size -eq 16384){"✓"}else{"✗"}))
Bank03:  $($BuildInfo.Bank03Size) bytes ($(if($BuildInfo.Bank03Size -eq 16384){"✓"}else{"✗"}))
CHR-ROM: $($BuildInfo.CHRSize) bytes ($(if($BuildInfo.CHRSize -eq 16384){"✓"}else{"✗"}))

TOTAL SIZE
----------
Built ROM: $($BuildInfo.TotalSize) bytes ($([math]::Round($BuildInfo.TotalSize/1024, 2)) KB)

VERIFICATION
------------
Differences: $($BuildInfo.Differences)
Status: $(if($BuildInfo.Differences -eq 0){"✅ PERFECT MATCH"}else{"⚠️ MISMATCHES FOUND"})

ASSEMBLY LOG
------------
$($BuildInfo.AssemblyLog)

================================================================================
"@
    
    $report | Out-File $OutputPath -Encoding UTF8
    Write-BuildLog "Report saved: $OutputPath" "SUCCESS"
}

# === Main Build Process ===
try {
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
    Write-Host "║          DRAGON WARRIOR ENHANCED ROM BUILDER                   ║" -ForegroundColor Cyan
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
    Write-Host ""
    
    # Clean build directory if requested
    if ($Clean -and (Test-Path $BuildDir)) {
        Write-BuildLog "Cleaning build directory..." "INFO"
        Remove-Item $BuildDir -Recurse -Force
    }
    
    # Create directories
    @($BuildDir, $ReportsDir) | ForEach-Object {
        if (-not (Test-Path $_)) {
            New-Item -ItemType Directory -Path $_ | Out-Null
        }
    }
    
    # Prerequisites check
    if (-not (Test-Prerequisites)) {
        throw "Prerequisites check failed"
    }
    
    # Determine target version
    $targetVersion = $Version
    if ($Version -eq "Auto") {
        if (Test-Path $PRG1_ROM) {
            $targetVersion = "PRG1"
            $ReferenceROM = $PRG1_ROM
        }
        elseif (Test-Path $PRG0_ROM) {
            $targetVersion = "PRG0"
            $ReferenceROM = $PRG0_ROM
        }
        else {
            Write-BuildLog "No reference ROM found for auto-detection" "WARN"
            $targetVersion = "PRG1"  # Default to PRG1
            $ReferenceROM = $null
        }
    }
    else {
        $ReferenceROM = if ($Version -eq "PRG1") { $PRG1_ROM } else { $PRG0_ROM }
    }
    
    Write-BuildLog "Target version: $targetVersion" "INFO"
    if ($ReferenceROM -and (Test-Path $ReferenceROM)) {
        $detectedVersion = Get-ROMVersion $ReferenceROM
        Write-BuildLog "Reference ROM detected as: $detectedVersion" "INFO"
    }
    
    # Build tracking
    $buildInfo = @{
        StartTime = $BuildStartTime
        TargetVersion = $targetVersion
        ReferenceROM = if ($ReferenceROM) { $ReferenceROM } else { "None" }
        AssemblyLog = ""
    }
    
    # === Assembly Phase ===
    Write-Host ""
    Write-BuildLog "Starting assembly phase..." "INFO"
    
    # 1. Header
    Write-BuildLog "[1/6] Assembling iNES header..." "INFO"
    $headerOutput = Join-Path $BuildDir "header.bin"
    Push-Location $SourceDir
    $opisisOutput = & $OpopisExe "Header.asm" $headerOutput 2>&1 | Out-String
    Pop-Location
    $buildInfo.AssemblyLog += "Header: $opisisOutput`n"
    $buildInfo.HeaderSize = (Get-Item $headerOutput).Length
    
    if ($buildInfo.HeaderSize -ne 16) {
        throw "Header size incorrect: $($buildInfo.HeaderSize) bytes (expected 16)"
    }
    Write-BuildLog "Header assembled: $($buildInfo.HeaderSize) bytes ✓" "SUCCESS"
    
    # 2-5. Banks
    $banks = @("Bank00", "Bank01", "Bank02", "Bank03")
    $bankOutputs = @()
    
    foreach ($bank in $banks) {
        $stepNum = $banks.IndexOf($bank) + 2
        Write-BuildLog "[$stepNum/6] Assembling $bank..." "INFO"
        
        $bankOutput = Join-Path $BuildDir "$($bank.ToLower()).bin"
        Push-Location $SourceDir
        $opisisOutput = & $OpopisExe "$bank.asm" $bankOutput 2>&1 | Out-String
        Pop-Location
        $buildInfo.AssemblyLog += "$bank`: $opisisOutput`n"
        
        $bankSize = (Get-Item $bankOutput).Length
        $buildInfo["${bank}Size"] = $bankSize
        $bankOutputs += $bankOutput
        
        if ($bankSize -eq 16384) {
            Write-BuildLog "$bank assembled: $bankSize bytes ✓" "SUCCESS"
        }
        else {
            Write-BuildLog "$bank size warning: $bankSize bytes (expected 16384)" "WARN"
        }
    }
    
    # 6. CHR-ROM
    Write-BuildLog "[6/6] Processing CHR-ROM..." "INFO"
    $chrOutput = Join-Path $BuildDir "chr_rom.bin"
    
    if ($ReferenceROM -and (Test-Path $ReferenceROM)) {
        $romData = [System.IO.File]::ReadAllBytes($ReferenceROM)
        $chrStart = 0x10010
        $chrSize = 0x4000
        $chrData = $romData[$chrStart..($chrStart + $chrSize - 1)]
        [System.IO.File]::WriteAllBytes($chrOutput, $chrData)
        Write-BuildLog "CHR-ROM extracted from reference: $chrSize bytes ✓" "SUCCESS"
    }
    else {
        $chrData = New-Object byte[] 16384
        [System.IO.File]::WriteAllBytes($chrOutput, $chrData)
        Write-BuildLog "CHR-ROM placeholder created: 16384 bytes" "WARN"
    }
    
    $buildInfo.CHRSize = (Get-Item $chrOutput).Length
    
    # === Concatenation Phase ===
    Write-Host ""
    Write-BuildLog "Concatenating ROM components..." "INFO"
    
    $OutputROM = Join-Path $BuildDir "dragon_warrior_rebuilt.nes"
    $buildInfo.OutputROM = $OutputROM
    
    $parts = @($headerOutput) + $bankOutputs + @($chrOutput)
    $finalData = @()
    foreach ($part in $parts) {
        $finalData += [System.IO.File]::ReadAllBytes($part)
    }
    
    [System.IO.File]::WriteAllBytes($OutputROM, $finalData)
    $buildInfo.TotalSize = (Get-Item $OutputROM).Length
    
    Write-BuildLog "ROM created: $($buildInfo.TotalSize) bytes" "SUCCESS"
    
    # === Verification Phase ===
    if ($ReferenceROM -and (Test-Path $ReferenceROM)) {
        Write-Host ""
        Write-BuildLog "Verifying against reference ROM..." "INFO"
        
        $refData = [System.IO.File]::ReadAllBytes($ReferenceROM)
        $builtData = [System.IO.File]::ReadAllBytes($OutputROM)
        
        $comparisonReportPath = Join-Path $ReportsDir "comparison_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
        $differences = Compare-ROMs -Reference $refData -Built $builtData -OutputPath $comparisonReportPath
        $buildInfo.Differences = $differences.Count
        
        if ($differences.Count -eq 0) {
            Write-BuildLog "✅ PERFECT MATCH! ROM is byte-identical to reference." "SUCCESS"
        }
        else {
            Write-BuildLog "⚠️  Found $($differences.Count) byte differences" "WARN"
            Write-BuildLog "First difference at: $($differences[0].Offset) (Bank: $($differences[0].Bank))" "WARN"
            Write-BuildLog "Comparison report: $comparisonReportPath" "INFO"
        }
    }
    else {
        $buildInfo.Differences = "N/A"
        Write-BuildLog "No reference ROM available for verification" "WARN"
    }
    
    # === Build Report ===
    $buildInfo.EndTime = Get-Date
    
    if ($Report) {
        $reportPath = Join-Path $ReportsDir "build_report_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt"
        New-BuildReport -BuildInfo $buildInfo -OutputPath $reportPath
    }
    
    # === Summary ===
    Write-Host ""
    Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Green
    Write-Host "║                    BUILD SUCCESSFUL                            ║" -ForegroundColor Green
    Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Green
    Write-Host ""
    Write-Host "Output ROM: " -NoNewline; Write-Host $OutputROM -ForegroundColor Yellow
    Write-Host "Size: " -NoNewline; Write-Host "$($buildInfo.TotalSize) bytes" -ForegroundColor Yellow
    
    if ($buildInfo.Differences -eq 0) {
        Write-Host "Status: " -NoNewline; Write-Host "✅ BYTE-PERFECT MATCH" -ForegroundColor Green
    }
    elseif ($buildInfo.Differences -ne "N/A") {
        Write-Host "Status: " -NoNewline; Write-Host "⚠️  $($buildInfo.Differences) differences" -ForegroundColor Yellow
    }
    
    Write-Host ""
}
catch {
    Write-Host ""
    Write-BuildLog "Build failed: $_" "ERROR"
    Write-BuildLog $_.ScriptStackTrace "ERROR"
    exit 1
}
