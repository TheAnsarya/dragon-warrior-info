#!/usr/bin/env powershell
<#
.SYNOPSIS
Dragon Warrior Asset-First ROM Builder

.DESCRIPTION
Builds Dragon Warrior ROM with asset-first workflow:
1. Generate ASM from JSON assets (items, monsters, spells)
2. Generate CHR-ROM from PNG graphics (optional)
3. Assemble ROM from generated ASM + original ASM
4. Your JSON/PNG edits WILL affect the final ROM

.PARAMETER UseAssets
Use JSON assets to generate game data (default: true)

.PARAMETER UseGraphics
Use PNG graphics to generate CHR-ROM (default: false, needs implementation)

.PARAMETER Clean
Clean build directories before building

.EXAMPLE
.\build_with_assets.ps1
Build ROM with JSON assets integrated

.EXAMPLE
.\build_with_assets.ps1 -UseAssets:$false
Build ROM without asset integration (same as build_rom.ps1)
#>

param(
    [switch]$UseAssets = $true,
    [switch]$UseGraphics = $false,
    [switch]$Clean = $false
)

$ErrorActionPreference = "Stop"

# Paths
$RootDir = if ($PSScriptRoot) { $PSScriptRoot } else { (Get-Location).Path }
$SourceDir = Join-Path $RootDir "source_files"
$BuildDir = Join-Path $RootDir "build"
$AssetsDir = Join-Path $RootDir "assets"
$ToolsDir = Join-Path $RootDir "tools"
$OpopisExe = Join-Path $RootDir "Ophis" | Join-Path -ChildPath "ophis.exe"
$ReferenceROM = "$RootDir\roms\Dragon Warrior (U) (PRG1) [!].nes"
$OutputROM = Join-Path $BuildDir "dragon_warrior_rebuilt.nes"

# Python executable
$Python = "python"

# Clean build directory if requested
if ($Clean) {
    Write-Host "🧹 Cleaning build directory..." -ForegroundColor Yellow
    if (Test-Path $BuildDir) {
        Remove-Item -Path $BuildDir -Recurse -Force
    }
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

# Create build directory
if (-not (Test-Path $BuildDir)) {
    New-Item -ItemType Directory -Path $BuildDir | Out-Null
}

Write-Host "🏗️  Dragon Warrior Asset-First ROM Builder" -ForegroundColor Cyan
Write-Host "==========================================`n" -ForegroundColor Cyan

# NEW STEP: Generate ASM from JSON assets
if ($UseAssets) {
    Write-Host "[ASSET] Generating ASM from JSON assets..." -ForegroundColor Magenta

    $assetReinserter = Join-Path $ToolsDir "asset_reinserter.py"
    $itemsJson = Join-Path $AssetsDir "json" | Join-Path -ChildPath "items_corrected.json"
    $monstersJson = Join-Path $AssetsDir "json" | Join-Path -ChildPath "monsters_verified.json"
    $spellsJson = Join-Path $AssetsDir "json" | Join-Path -ChildPath "spells.json"

    # Check if JSON files exist
    $hasItems = Test-Path $itemsJson
    $hasMonsters = Test-Path $monstersJson
    $hasSpells = Test-Path $spellsJson

    if ($hasItems -or $hasMonsters -or $hasSpells) {
        # Create generated ASM directory
        $generatedDir = Join-Path $SourceDir "generated"
        if (-not (Test-Path $generatedDir)) {
            New-Item -ItemType Directory -Path $generatedDir | Out-Null
        }

        if ($hasItems) {
            Write-Host "   → Items: $itemsJson" -ForegroundColor DarkCyan
        }
        if ($hasMonsters) {
            Write-Host "   → Monsters: $monstersJson" -ForegroundColor DarkCyan
        }
        if ($hasSpells) {
            Write-Host "   → Spells: $spellsJson" -ForegroundColor DarkCyan
        }

        # Call asset_reinserter.py to generate ASM files
        try {
            & $Python $assetReinserter $AssetsDir -o $generatedDir 2>&1 | ForEach-Object {
                Write-Host "   $_" -ForegroundColor DarkCyan
            }

            $masterInclude = Join-Path $generatedDir "dragon_warrior_assets.asm"
            if (Test-Path $masterInclude) {
                Write-Host "   ✓ Generated ASM files in $generatedDir" -ForegroundColor Green
                Write-Host "   ✓ Master include: dragon_warrior_assets.asm" -ForegroundColor Green
            } else {
                Write-Host "   ⚠️  Warning: No master include file generated" -ForegroundColor Yellow
            }
        } catch {
            Write-Host "   ❌ Error running asset_reinserter: $_" -ForegroundColor Red
            Write-Host "   ℹ️  Continuing with original ASM data" -ForegroundColor DarkGray
        }

    } else {
        Write-Host "   ⚠️  No JSON assets found, using original ASM data" -ForegroundColor Yellow
    }
}

# NEW STEP: Generate CHR-ROM from PNG graphics (optional, future feature)
if ($UseGraphics) {
    Write-Host "[GRAPHICS] Generating CHR-ROM from PNG sprites..." -ForegroundColor Magenta
    Write-Host "   ⚠️  Graphics reinsertion not yet implemented" -ForegroundColor Yellow
    Write-Host "   ℹ️  Using existing chr_rom.bin" -ForegroundColor DarkGray

    # Future implementation:
    # $graphicsToChr = Join-Path $ToolsDir "graphics_to_chr.py"
    # $spritesDir = Join-Path $AssetsDir "graphics" | Join-Path -ChildPath "sprites"
    # $chrOutput = Join-Path $BuildDir "chr_rom_generated.bin"
    # & $Python $graphicsToChr --sprites-dir $spritesDir --output $chrOutput
}

# Step 1: Assemble Header
Write-Host "`n[1/6] Assembling iNES header..." -ForegroundColor Yellow
Push-Location $SourceDir
& $OpopisExe Header.asm (Join-Path $BuildDir "header.bin") 2>&1 | Out-Null
Pop-Location

$headerSize = (Get-Item (Join-Path $BuildDir "header.bin")).Length
if ($headerSize -ne 16) {
    Write-Host "   ❌ Error: Header should be 16 bytes, got $headerSize" -ForegroundColor Red
    exit 1
}
Write-Host "   ✓ Header: $headerSize bytes" -ForegroundColor Green

# Step 2-5: Assemble PRG Banks
$banks = @("Bank00", "Bank01", "Bank02", "Bank03")
$bankFiles = @()

# Check if we have generated assets
$generatedMonstersASM = Join-Path $SourceDir "generated" | Join-Path -ChildPath "monster_data.asm"
$generatedItemCostASM = Join-Path $SourceDir "generated" | Join-Path -ChildPath "item_cost_table.asm"
$generatedSpellCostASM = Join-Path $SourceDir "generated" | Join-Path -ChildPath "spell_cost_table.asm"
$useGeneratedMonsters = $UseAssets -and (Test-Path $generatedMonstersASM)
$useGeneratedItems = $UseAssets -and (Test-Path $generatedItemCostASM)
$useGeneratedSpells = $false

# Generate item cost table if using assets
if ($UseAssets) {
    $itemCostGenerator = Join-Path $ToolsDir "generate_item_cost_table.py"
    if (Test-Path $itemCostGenerator) {
        Write-Host "`n💰 Generating item cost table..." -ForegroundColor Cyan
        try {
            & $Python $itemCostGenerator 2>&1 | Out-Null
            if (Test-Path $generatedItemCostASM) {
                Write-Host "   ✓ Item cost table generated" -ForegroundColor Green
                $useGeneratedItems = $true
            }
        } catch {
            Write-Host "   ⚠️  Could not generate item cost table: $_" -ForegroundColor Yellow
            $useGeneratedItems = $false
        }
    }

    # Generate spell cost table
    $spellCostGenerator = Join-Path $ToolsDir "generate_spell_cost_table.py"
    if (Test-Path $spellCostGenerator) {
        Write-Host "🔮 Generating spell cost table..." -ForegroundColor Cyan
        try {
            & $Python $spellCostGenerator 2>&1 | Out-Null
            if (Test-Path $generatedSpellCostASM) {
                Write-Host "   ✓ Spell cost table generated" -ForegroundColor Green
                $useGeneratedSpells = $true
            }
        } catch {
            Write-Host "   ⚠️  Could not generate spell cost table: $_" -ForegroundColor Yellow
            $useGeneratedSpells = $false
        }
    }

    # Generate shop items table
    $shopItemsGenerator = Join-Path $ToolsDir "generate_shop_items_table.py"
    $generatedShopItemsASM = Join-Path $SourceDir "generated" | Join-Path -ChildPath "shop_items_table.asm"
    if (Test-Path $shopItemsGenerator) {
        Write-Host "🏪 Generating shop items table..." -ForegroundColor Cyan
        try {
            & $Python $shopItemsGenerator 2>&1 | Out-Null
            if (Test-Path $generatedShopItemsASM) {
                Write-Host "   ✓ Shop items table generated" -ForegroundColor Green
            }
        } catch {
            Write-Host "   ⚠️  Could not generate shop items table: $_" -ForegroundColor Yellow
        }
    }

    # Generate equipment bonus tables
    $equipmentBonusGenerator = Join-Path $ToolsDir "generate_equipment_bonus_tables.py"
    $generatedEquipmentBonusASM = Join-Path $SourceDir "generated" | Join-Path -ChildPath "equipment_bonus_tables.asm"
    if (Test-Path $equipmentBonusGenerator) {
        Write-Host "⚔️  Generating equipment bonus tables..." -ForegroundColor Cyan
        try {
            & $Python $equipmentBonusGenerator 2>&1 | Out-Null
            if (Test-Path $generatedEquipmentBonusASM) {
                Write-Host "   ✓ Equipment bonus tables generated" -ForegroundColor Green
            }
        } catch {
            Write-Host "   ⚠️  Could not generate equipment bonus tables: $_" -ForegroundColor Yellow
        }
    }

    # Generate NPC tables
    $npcTableGenerator = Join-Path $ToolsDir "generate_npc_tables.py"
    $generatedNpcTablesASM = Join-Path $SourceDir "generated" | Join-Path -ChildPath "npc_tables.asm"
    if (Test-Path $npcTableGenerator) {
        Write-Host "👤 Generating NPC tables..." -ForegroundColor Cyan
        try {
            & $Python $npcTableGenerator 2>&1 | Out-Null
            if (Test-Path $generatedNpcTablesASM) {
                Write-Host "   ✓ NPC tables generated" -ForegroundColor Green
            }
        } catch {
            Write-Host "   ⚠️  Could not generate NPC tables: $_" -ForegroundColor Yellow
        }
    }
}

# Item cost table is now included via .include directive in Bank00.asm
# No need to modify the ASM file - the generated file will be automatically included during assembly
if ($useGeneratedItems) {
    Write-Host "`n💡 Generated item cost data: $generatedItemCostASM" -ForegroundColor Cyan
    Write-Host "   ✓ Will be included during Bank00 assembly via .include directive" -ForegroundColor Green
}# Monster data is now included via .include directive in Bank01.asm
# No need to modify the ASM file - the generated file will be automatically included during assembly
if ($useGeneratedMonsters) {
    Write-Host "`n💡 Generated monster data: $generatedMonstersASM" -ForegroundColor Cyan
    Write-Host "   ✓ Will be included during Bank01 assembly via .include directive" -ForegroundColor Green
}

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

# No need to restore Bank00.asm - we never modified it!
# The .include directive pulls in generated data automatically

# No need to restore Bank01.asm - we never modified it!
# The .include directive pulls in generated data automatically

# Step 6: Extract CHR-ROM
Write-Host "[6/6] Extracting CHR-ROM..." -ForegroundColor Yellow

# Priority order:
# 1. Generated CHR from PNG (if UseGraphics and file exists)
# 2. Pre-extracted chr_rom.bin in source_files
# 3. Extract from reference ROM
# 4. Empty placeholder

$generatedChr = Join-Path $BuildDir "chr_rom_generated.bin"
$sourceChrRom = Join-Path $SourceDir "chr_rom.bin"
$chrOutput = Join-Path $BuildDir "chr_rom.bin"

if ($UseGraphics -and (Test-Path $generatedChr)) {
    # Use generated CHR from PNG graphics
    Copy-Item $generatedChr $chrOutput -Force
    $chrSize = (Get-Item $chrOutput).Length
    Write-Host "   ✓ CHR-ROM (from PNG graphics): $chrSize bytes" -ForegroundColor Green
} elseif (Test-Path $sourceChrRom) {
    # Use pre-extracted CHR
    Copy-Item $sourceChrRom $chrOutput -Force
    $chrSize = (Get-Item $chrOutput).Length
    Write-Host "   ✓ CHR-ROM (from source_files): $chrSize bytes" -ForegroundColor Green
} elseif ($ReferenceROM -and (Test-Path $ReferenceROM)) {
    # Extract from reference ROM
    $romData = [System.IO.File]::ReadAllBytes($ReferenceROM)
    $chrStart = 0x10010
    $chrSize = 0x4000  # 16KB
    $chrData = $romData[$chrStart..($chrStart + $chrSize - 1)]
    [System.IO.File]::WriteAllBytes($chrOutput, $chrData)
    Write-Host "   ✓ CHR-ROM (from reference ROM): $chrSize bytes" -ForegroundColor Green
} else {
    # Empty placeholder
    Write-Host "   ⚠️  No CHR-ROM source found, using placeholder" -ForegroundColor Yellow
    $chrData = New-Object byte[] 16384
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
            if ($UseAssets) {
                Write-Host "   ℹ️  This is expected when using modified JSON assets" -ForegroundColor DarkGray
            }
        }
    }
}

Write-Host "`n✅ Build complete!" -ForegroundColor Green
Write-Host "Output: $OutputROM" -ForegroundColor White

if ($UseAssets) {
    Write-Host "`nℹ️  Asset Integration Status:" -ForegroundColor Cyan
    if ($useGeneratedMonsters) {
        Write-Host "   ✅ Monster Data: Integrated from assets/json/monsters_verified.json" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Monster Data: Not integrated" -ForegroundColor Yellow
    }
    if ($useGeneratedItems) {
        Write-Host "   ✅ Item Cost Data: Integrated from assets/json/items_corrected.json" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Item Cost Data: Not integrated" -ForegroundColor Yellow
    }
    if ($useGeneratedSpells) {
        Write-Host "   ✅ Spell Cost Data: Integrated from assets/json/spells.json" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Spell Cost Data: Not integrated" -ForegroundColor Yellow
    }
    if (Test-Path (Join-Path $SourceDir "generated" | Join-Path -ChildPath "shop_items_table.asm")) {
        Write-Host "   ✅ Shop Data: Integrated from assets/json/shops.json" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Shop Data: Not integrated" -ForegroundColor Yellow
    }
    if (Test-Path (Join-Path $SourceDir "generated" | Join-Path -ChildPath "equipment_bonus_tables.asm")) {
        Write-Host "   ✅ Equipment Bonuses: Integrated from assets/json/equipment_bonuses.json" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  Equipment Bonuses: Not integrated" -ForegroundColor Yellow
    }
    Write-Host "   ⚠️  PNG → CHR: Not yet implemented" -ForegroundColor Yellow
}

Write-Host ""
