# Remove unreferenced labels from DW1 disassembly files
# This script reads the CSV file of unreferenced labels and removes them from the source files

$csvPath = "c:\Users\me\source\repos\dragon-warrior-info\unreferenced_labels.csv"
$sourceDir = "c:\Users\me\source\repos\dragon-warrior-info\source_files"

$unreferencedLabels = Import-Csv -Path $csvPath

# Group labels by file
$labelsByFile = $unreferencedLabels | Group-Object -Property File

Write-Host "Found $($unreferencedLabels.Count) unreferenced labels across $($labelsByFile.Count) files"

foreach ($fileGroup in $labelsByFile) {
	$fileName = $fileGroup.Name
	$filePath = Get-ChildItem -Path $sourceDir -Filter $fileName -Recurse | Select-Object -First 1 -ExpandProperty FullName
	
	if (-not $filePath) {
		Write-Host "File not found: $fileName" -ForegroundColor Yellow
		continue
	}
	
	Write-Host "Processing: $fileName ($($fileGroup.Count) labels)"
	
	# Read file content as lines
	$lines = Get-Content -Path $filePath -Encoding UTF8
	$newLines = @()
	$removedCount = 0
	
	# Create a set of labels to remove for fast lookup
	$labelsToRemove = @{}
	foreach ($item in $fileGroup.Group) {
		$labelsToRemove[$item.Label] = $true
	}
	
	foreach ($line in $lines) {
		# Check if line starts with a label definition
		if ($line -match '^([A-Za-z_][A-Za-z0-9_]*):') {
			$labelName = $Matches[1]
			if ($labelsToRemove.ContainsKey($labelName)) {
				# Check if this is a label-only line or if there's code after the colon
				$afterColon = $line.Substring($line.IndexOf(':') + 1).Trim()
				if ($afterColon -eq '' -or $afterColon.StartsWith(';')) {
					# Label-only line (possibly with comment) - skip it
					$removedCount++
					continue
				} else {
					# There's code after the label - just remove the label portion
					$newLine = $afterColon
					$newLines += $newLine
					$removedCount++
					continue
				}
			}
		}
		
		$newLines += $line
	}
	
	# Write back
	Set-Content -Path $filePath -Value ($newLines -join "`n") -NoNewline -Encoding UTF8
	Write-Host "  Removed $removedCount labels"
}

Write-Host "`nDone!"
