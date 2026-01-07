# Find unreferenced labels in DW1 disassembly files
# Labels are defined as "LabelName:" at the start of a line
# We need to check if each label is referenced anywhere else

$sourceDir = "c:\Users\me\source\repos\dragon-warrior-info\source_files"
$files = Get-ChildItem -Path $sourceDir -Filter "*.asm" -Recurse -File

# Step 1: Collect all label definitions (lines starting with identifier followed by colon)
$labelDefinitions = @{}
$allContent = ""

foreach ($file in $files) {
	$content = Get-Content -Path $file.FullName -Raw -Encoding UTF8
	$allContent += "`n" + $content

	# Match labels: start of line, identifier (letters/numbers/_), colon
	$matches = [regex]::Matches($content, '(?m)^([A-Za-z_][A-Za-z0-9_]*):')
	foreach ($match in $matches) {
		$labelName = $match.Groups[1].Value
		if (-not $labelDefinitions.ContainsKey($labelName)) {
			$labelDefinitions[$labelName] = @{
				File = $file.Name
				Count = 0
			}
		}
	}
}

Write-Host "Found $($labelDefinitions.Count) label definitions"

# Step 2: Count references to each label (exclude the definition itself)
$unreferenced = @()
foreach ($label in $labelDefinitions.Keys) {
	# Count all occurrences (including definition)
	$pattern = [regex]::Escape($label)
	$allMatches = [regex]::Matches($allContent, "\b$pattern\b")

	# If count is 1, it's only the definition - no references
	if ($allMatches.Count -le 1) {
		$unreferenced += [PSCustomObject]@{
			Label = $label
			File = $labelDefinitions[$label].File
		}
	}
}

Write-Host "`nFound $($unreferenced.Count) unreferenced labels:`n"

# Group by file
$grouped = $unreferenced | Group-Object -Property File | Sort-Object Name

foreach ($group in $grouped) {
	Write-Host "=== $($group.Name) ===" -ForegroundColor Cyan
	foreach ($item in ($group.Group | Sort-Object -Property Label)) {
		Write-Host "  $($item.Label)"
	}
	Write-Host ""
}

# Export to file for review
$unreferenced | Sort-Object File, Label | Export-Csv -Path "c:\Users\me\source\repos\dragon-warrior-info\unreferenced_labels.csv" -NoTypeInformation
Write-Host "`nExported to unreferenced_labels.csv"
