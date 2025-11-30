#!/usr/bin/env python3
"""
Fix Label Inconsistencies

Finds and fixes references to labels that don't match their definitions.
The abbreviation expansion process left some references expanded but not the definitions.
"""

import re
from pathlib import Path
from collections import defaultdict


def find_all_labels(source_dir: Path) -> dict:
	"""Find all label definitions across all ASM files."""
	labels = {}  # label_lower -> (original_case, file, line_num)

	label_pattern = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*)\s*[:=]')

	for asm_file in source_dir.glob('*.asm'):
		with open(asm_file, 'r', encoding='utf-8', errors='replace') as f:
			for line_num, line in enumerate(f, 1):
				match = label_pattern.match(line)
				if match:
					label = match.group(1)
					labels[label.lower()] = (label, asm_file.name, line_num)

	return labels


def find_all_references(source_dir: Path) -> dict:
	"""Find all label references across all ASM files."""
	references = defaultdict(list)  # label_lower -> [(original_case, file, line_num, line)]

	# Pattern to find label references (not definitions)
	# Look for labels after instructions, in .word/.byte directives, etc.
	ref_pattern = re.compile(r'\b([A-Za-z_][A-Za-z0-9_]*)\b')

	for asm_file in source_dir.glob('*.asm'):
		with open(asm_file, 'r', encoding='utf-8', errors='replace') as f:
			for line_num, line in enumerate(f, 1):
				# Skip label definitions (start of line)
				if re.match(r'^[A-Za-z_][A-Za-z0-9_]*\s*[:=]', line):
					# But check rest of line for references
					colon_pos = line.find(':')
					eq_pos = line.find('=')
					if colon_pos > 0:
						line_to_check = line[colon_pos+1:]
					elif eq_pos > 0:
						line_to_check = line[eq_pos+1:]
					else:
						line_to_check = line
				else:
					line_to_check = line

				# Find all identifiers
				for match in ref_pattern.finditer(line_to_check):
					label = match.group(1)
					# Skip obvious non-labels
					if label.upper() in ('LDA', 'STA', 'LDX', 'STX', 'LDY', 'STY', 'JSR', 'JMP',
										'BNE', 'BEQ', 'BCS', 'BCC', 'BMI', 'BPL', 'BVS', 'BVC',
										'CMP', 'CPX', 'CPY', 'AND', 'ORA', 'EOR', 'ADC', 'SBC',
										'INC', 'DEC', 'INX', 'DEX', 'INY', 'DEY', 'ASL', 'LSR',
										'ROL', 'ROR', 'BIT', 'TAX', 'TXA', 'TAY', 'TYA', 'TSX',
										'TXS', 'PHA', 'PLA', 'PHP', 'PLP', 'CLC', 'SEC', 'CLI',
										'SEI', 'CLD', 'SED', 'CLV', 'NOP', 'BRK', 'RTI', 'RTS'):
						continue
					# Skip directives
					if label.startswith('.'):
						continue
					# Skip hex/binary numbers that look like labels
					if re.match(r'^[0-9A-Fa-f]+$', label):
						continue

					references[label.lower()].append((label, asm_file.name, line_num, line.rstrip()))

	return references


def find_inconsistencies(labels: dict, references: dict) -> list:
	"""Find references that don't match their definition's case."""
	issues = []

	for ref_lower, ref_list in references.items():
		if ref_lower in labels:
			defined_label, def_file, def_line = labels[ref_lower]
			for ref_label, ref_file, ref_line, line_content in ref_list:
				if ref_label != defined_label:
					issues.append({
						'defined': defined_label,
						'reference': ref_label,
						'def_file': def_file,
						'ref_file': ref_file,
						'ref_line': ref_line,
						'line_content': line_content
					})
		else:
			# Label is referenced but not defined - could be undefined or in a different form
			for ref_label, ref_file, ref_line, line_content in ref_list:
				# Check if this might be a misnamed reference
				# Look for similar labels that might be the intended target
				similar = []
				for def_lower, (def_label, def_file, def_ln) in labels.items():
					# Check if one is a substring of the other
					if ref_lower in def_lower or def_lower in ref_lower:
						similar.append(def_label)

				if similar:
					issues.append({
						'defined': None,
						'reference': ref_label,
						'similar': similar,
						'ref_file': ref_file,
						'ref_line': ref_line,
						'line_content': line_content
					})

	return issues


def fix_reference(content: str, old_ref: str, new_ref: str) -> str:
	"""Fix a specific reference in the content."""
	# Use word boundary to avoid partial matches
	pattern = re.compile(r'\b' + re.escape(old_ref) + r'\b')
	return pattern.sub(new_ref, content)


def main():
	source_dir = Path(__file__).parent.parent / 'source_files'

	print("Finding all label definitions...")
	labels = find_all_labels(source_dir)
	print(f"Found {len(labels)} labels")

	print("\nFinding all label references...")
	references = find_all_references(source_dir)
	print(f"Found {len(references)} unique referenced labels")

	print("\nFinding inconsistencies...")
	issues = find_inconsistencies(labels, references)

	# Group issues by type
	case_mismatches = [i for i in issues if i.get('defined')]
	undefined_refs = [i for i in issues if not i.get('defined')]

	print(f"\nCase mismatches: {len(case_mismatches)}")
	print(f"Undefined references with similar labels: {len(undefined_refs)}")

	# Common problematic patterns found
	# These are abbreviation expansion inconsistencies
	known_fixes = {
		'VerticalAttribLoop1': 'VertAttribLoop1',
		'VerticalAttribLoop2': 'VertAttribLoop2',
		'VerticalBlockLoop1': 'VertBlockLoop1',
		'VerticalBlockLoop2': 'VertBlockLoop2',
		'VerticalBlockLoop3': 'VertBlockLoop3',
		'VerticalRowLoop1': 'VertRowLoop1',
		'VerticalRowLoop2': 'VertRowLoop2',
		'VerticalRowLoop3': 'VertRowLoop3',
		'VerticalDgnBlockLoop': 'VertDgnBlockLoop',
		'VerticalDgnRowLoop': 'VertDgnRowLoop',
		'attributebufindex': 'AttribBufIndex',
		'AttributeBufIndex': 'AttribBufIndex',
		'npcdatptrub': 'NpcDatPtrUB',
		'randomnumberub': 'RandomNumberUB',
		'updaterandnum': 'UpdateRandNum',
		'windowerasewdth': 'WindowEraseWdth',
	}

	# Check which files need fixes
	files_to_fix = defaultdict(list)

	for asm_file in source_dir.glob('*.asm'):
		with open(asm_file, 'r', encoding='utf-8', errors='replace') as f:
			content = f.read()

		for old, new in known_fixes.items():
			if old in content:
				files_to_fix[asm_file].append((old, new))

	if not files_to_fix:
		print("\nNo known inconsistencies found to fix!")
		return

	print("\nFiles needing fixes:")
	for f, fixes in files_to_fix.items():
		print(f"  {f.name}: {len(fixes)} fixes")
		for old, new in fixes:
			print(f"    {old} -> {new}")

	# Ask for confirmation
	response = input("\nApply fixes? (y/n): ")
	if response.lower() != 'y':
		print("Aborted.")
		return

	# Apply fixes
	for asm_file, fixes in files_to_fix.items():
		with open(asm_file, 'r', encoding='utf-8', errors='replace') as f:
			content = f.read()

		for old, new in fixes:
			content = fix_reference(content, old, new)

		with open(asm_file, 'w', encoding='utf-8') as f:
			f.write(content)

		print(f"Fixed {asm_file.name}")

	print("\nDone! Run build to verify.")


if __name__ == '__main__':
	main()
