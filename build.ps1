#!/usr/bin/env powershell
<#
.SYNOPSIS
Dragon Warrior Info Project - Main Build Script

.DESCRIPTION
Comprehensive build system for Dragon Warrior ROM assembly, asset processing, and testing.
Based on FFMQ project build patterns.

.PARAMETER Clean
Clean build directories before building

.PARAMETER Verbose
Show verbose build output

.PARAMETER Test
Run tests after successful build

.PARAMETER Symbols
Generate symbol file for debugging

.PARAMETER Output
Specify output ROM file name

.EXAMPLE
.\build.ps1
Basic build

.EXAMPLE
.\build.ps1 -Clean -Verbose -Test
Clean build with verbose output and testing

.EXAMPLE
.\build.ps1 -Output "dragon_warrior_modified.nes" -Symbols
Build with custom output name and debug symbols
#>

param(
	[switch]$Clean,
	[switch]$Verbose,
	[switch]$Test,
	[switch]$Symbols,
	[string]$Output = "dragon_warrior_rebuilt.nes"
)

# Build configuration
$BuildRoot = $PSScriptRoot
$SourceDir = Join-Path $BuildRoot "source_files"
$BuildDir = Join-Path $BuildRoot "build"
$ToolsDir = Join-Path $BuildRoot "tools"
$AssetDir = Join-Path $BuildRoot "assets"
$ROMDir = Join-Path $BuildRoot "~roms"

# Colors for output
$ColorSuccess = "Green"
$ColorError = "Red"
$ColorWarning = "Yellow"
$ColorInfo = "Cyan"

function Write-BuildLog {
	param(
		[string]$Message,
		[string]$Level = "INFO"
	)

	$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
	$color = switch($Level) {
		"SUCCESS" { $ColorSuccess }
		"ERROR" { $ColorError }
		"WARNING" { $ColorWarning }
		default { $ColorInfo }
	}

	Write-Host "[$timestamp] " -NoNewline -ForegroundColor Gray
	Write-Host "$Level " -NoNewline -ForegroundColor $color
	Write-Host $Message
}

function Test-Prerequisites {
	Write-BuildLog "Checking build prerequisites..."

	# Check for Ophis assembler
	$ophisPath = Join-Path $BuildRoot "Ophis\ophis.exe"
	if (-not (Test-Path $ophisPath)) {
		Write-BuildLog "Ophis assembler not found at $ophisPath" "ERROR"
		return $false
	}

	# Check for Python
	try {
		$pythonVersion = & python --version 2>&1
		Write-BuildLog "Found Python: $pythonVersion"
	} catch {
		Write-BuildLog "Python not found. Please install Python 3.x" "ERROR"
		return $false
	}

	# Check for source files
	if (-not (Test-Path $SourceDir)) {
		Write-BuildLog "Source directory not found: $SourceDir" "ERROR"
		return $false
	}

	Write-BuildLog "Prerequisites check passed" "SUCCESS"
	return $true
}

function Initialize-BuildEnvironment {
	Write-BuildLog "Initializing build environment..."

	# Create build directory
	if ($Clean -and (Test-Path $BuildDir)) {
		Write-BuildLog "Cleaning build directory..."
		Remove-Item $BuildDir -Recurse -Force
	}

	if (-not (Test-Path $BuildDir)) {
		New-Item -ItemType Directory -Path $BuildDir -Force | Out-Null
		Write-BuildLog "Created build directory: $BuildDir"
	}

	# Create assets directory if needed
	if (-not (Test-Path $AssetDir)) {
		New-Item -ItemType Directory -Path $AssetDir -Force | Out-Null
		Write-BuildLog "Created assets directory: $AssetDir"
	}

	Write-BuildLog "Build environment initialized" "SUCCESS"
}

function Invoke-AssemblyBuild {
	Write-BuildLog "Starting assembly build process..."

	# Main assembly file
	$mainAsmFile = Join-Path $SourceDir "DragonWarrior.asm"
	if (-not (Test-Path $mainAsmFile)) {
		Write-BuildLog "Main assembly file not found: $mainAsmFile" "ERROR"
		return $false
	}

	# Output ROM file
	$outputROM = Join-Path $BuildDir $Output

	# Ophis assembler command
	$ophisPath = Join-Path $BuildRoot "Ophis\ophis.exe"
	$buildArgs = @(
		$mainAsmFile,
		$outputROM
	)

	if ($Verbose) {
		$buildArgs = @("-v", "2") + $buildArgs
	}

	Write-BuildLog "Executing: $ophisPath $($buildArgs -join ' ')"

	try {
		$result = & $ophisPath $buildArgs 2>&1

		if ($LASTEXITCODE -eq 0) {
			Write-BuildLog "Assembly build completed successfully" "SUCCESS"
			Write-BuildLog "ROM created: $outputROM"

			# Show ROM size
			if (Test-Path $outputROM) {
				$romSize = (Get-Item $outputROM).Length
				$romSizeKB = [math]::Round($romSize / 1024, 2)
				Write-BuildLog "ROM size: $romSizeKB KB ($romSize bytes)"
			}

			return $true
		} else {
			Write-BuildLog "Assembly build failed with exit code: $LASTEXITCODE" "ERROR"
			if ($result) {
				Write-BuildLog "Build output: $result" "ERROR"
			}
			return $false
		}
	} catch {
		Write-BuildLog "Error executing assembler: $_" "ERROR"
		return $false
	}
}

function Invoke-AssetProcessing {
	Write-BuildLog "Processing game assets..."

	# Check if Python tools are available
	$assetTool = Join-Path $ToolsDir "build" "asset_processor.py"
	if (Test-Path $assetTool) {
		Write-BuildLog "Running asset processor..."
		try {
			$referenceRom = "~roms\Dragon Warrior (U) (PRG1) [!].nes"
			if (Test-Path $referenceRom) {
				& python $assetTool --reference-rom $referenceRom --output-dir $AssetDir 2>&1
				Write-BuildLog "Asset processing completed" "SUCCESS"
			} else {
				Write-BuildLog "Reference ROM not found at $referenceRom - skipping asset processing" "WARNING"
			}
		} catch {
			Write-BuildLog "Asset processing failed: $_" "WARNING"
		}
	} else {
		Write-BuildLog "Asset processor not found, skipping asset processing" "WARNING"
	}
}

function Invoke-Testing {
	if (-not $Test) {
		return
	}

	Write-BuildLog "Running tests..."

	# ROM validation
	$outputROM = Join-Path $BuildDir $Output
	if (Test-Path $outputROM) {
		$romSize = (Get-Item $outputROM).Length

		# Basic size validation (Dragon Warrior should be around 256KB)
		if ($romSize -lt 100KB -or $romSize -gt 1MB) {
			Write-BuildLog "ROM size appears invalid: $romSize bytes" "WARNING"
		} else {
			Write-BuildLog "ROM size validation passed: $romSize bytes" "SUCCESS"
		}

		# Calculate and display ROM checksum
		$hash = Get-FileHash $outputROM -Algorithm MD5
		Write-BuildLog "ROM MD5: $($hash.Hash)"

	} else {
		Write-BuildLog "Cannot run tests: ROM file not found" "ERROR"
		return $false
	}

	# Run Python tests if available
	$testDir = Join-Path $BuildRoot "tests"
	if (Test-Path $testDir) {
		Write-BuildLog "Running Python test suite..."
		try {
			Push-Location $BuildRoot
			& python -m pytest $testDir -v 2>&1
			if ($LASTEXITCODE -eq 0) {
				Write-BuildLog "All tests passed" "SUCCESS"
			} else {
				Write-BuildLog "Some tests failed" "WARNING"
			}
		} catch {
			Write-BuildLog "Error running tests: $_" "WARNING"
		} finally {
			Pop-Location
		}
	}

	Write-BuildLog "Testing completed"
}

function Show-BuildSummary {
	param($BuildSuccess, $StartTime)

	$endTime = Get-Date
	$duration = $endTime - $StartTime

	Write-Host "`n" -NoNewline
	Write-Host "=" * 60 -ForegroundColor Gray
	Write-Host "BUILD SUMMARY" -ForegroundColor White
	Write-Host "=" * 60 -ForegroundColor Gray

	if ($BuildSuccess) {
		Write-Host "Status: " -NoNewline
		Write-Host "SUCCESS" -ForegroundColor $ColorSuccess
	} else {
		Write-Host "Status: " -NoNewline
		Write-Host "FAILED" -ForegroundColor $ColorError
	}

	Write-Host "Duration: $($duration.TotalSeconds.ToString('F2')) seconds"
	Write-Host "Output: $(Join-Path $BuildDir $Output)"

	if (Test-Path (Join-Path $BuildDir $Output)) {
		$romSize = (Get-Item (Join-Path $BuildDir $Output)).Length
		Write-Host "ROM Size: $([math]::Round($romSize / 1024, 2)) KB"
	}

	Write-Host "=" * 60 -ForegroundColor Gray
}

# Main build execution
Write-Host "🏗️ Dragon Warrior Info Project - Build System" -ForegroundColor Yellow
Write-Host "Based on FFMQ project build patterns`n" -ForegroundColor Gray

$startTime = Get-Date
$buildSuccess = $false

try {
	# Prerequisites check
	if (-not (Test-Prerequisites)) {
		exit 1
	}

	# Initialize environment
	Initialize-BuildEnvironment

	# Asset processing
	Invoke-AssetProcessing

	# Main assembly build
	if (Invoke-AssemblyBuild) {
		$buildSuccess = $true

		# Testing
		Invoke-Testing

		Write-BuildLog "Build completed successfully!" "SUCCESS"
	} else {
		Write-BuildLog "Build failed!" "ERROR"
		exit 1
	}

} catch {
	Write-BuildLog "Unexpected error during build: $_" "ERROR"
	exit 1
} finally {
	Show-BuildSummary $buildSuccess $startTime
}

if ($buildSuccess) {
	Write-Host "`n✅ Build completed successfully!" -ForegroundColor $ColorSuccess
	$builtRom = Join-Path $BuildDir $Output
	Write-Host "ROM file: $builtRom" -ForegroundColor $ColorInfo

	if ($Symbols) {
		$symbolFile = $builtRom -replace '\.nes$', '.sym'
		Write-Host "Symbol file: $symbolFile" -ForegroundColor $ColorInfo
	}

	# Compare against reference ROM
	$referenceRom = "~roms\Dragon Warrior (U) (PRG1) [!].nes"
	if (Test-Path $referenceRom) {
		Write-Host "`n📊 Comparing against reference ROM..." -ForegroundColor $ColorInfo

		try {
			$reportDir = Join-Path $BuildDir "reports"
			$reportFile = Join-Path $reportDir "rom_comparison.md"
			$jsonFile = Join-Path $reportDir "rom_comparison.json"

			& python "tools\build\rom_comparator.py" $referenceRom $builtRom --output $reportFile --json-output $jsonFile

			if ($LASTEXITCODE -eq 0) {
				Write-Host "✅ ROM comparison complete - see $reportFile" -ForegroundColor $ColorSuccess
			} else {
				Write-Host "⚠️  ROM differs from reference - see $reportFile for details" -ForegroundColor $ColorWarning
			}
		} catch {
			Write-Host "⚠️  Could not compare ROM: $_" -ForegroundColor $ColorWarning
		}
	} else {
		Write-Host "ℹ️  Reference ROM not found at $referenceRom - skipping comparison" -ForegroundColor $ColorInfo
	}

	# Generate comprehensive build report
	Write-Host "`n📊 Generating build report..." -ForegroundColor $ColorInfo
	try {
		& python "tools\build\build_reporter.py" $BuildDir --format both
		$reportFile = Join-Path $BuildDir "reports" "build_report.html"
		if (Test-Path $reportFile) {
			Write-Host "📄 Build report: $reportFile" -ForegroundColor $ColorSuccess
		}
	} catch {
		Write-Host "⚠️  Could not generate build report: $_" -ForegroundColor $ColorWarning
	}
} else {
	Write-Host "`n❌ Build failed!" -ForegroundColor $ColorError
	exit 1
}
