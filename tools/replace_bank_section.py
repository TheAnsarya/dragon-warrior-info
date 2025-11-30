"""Replace marked sections in assembly files with generated content."""
import re
import sys
from pathlib import Path

def replace_marked_section(bank_file, generated_file, start_marker, end_marker):
	"""Replace content between markers in bank_file with content from generated_file."""

	# Read files
	bank_path = Path(bank_file)
	gen_path = Path(generated_file)

	with open(bank_path, 'r', encoding='utf-8') as f:
		bank_content = f.read()

	with open(gen_path, 'r', encoding='utf-8') as f:
		generated_content = f.read().strip()

	# Create pattern to match section between markers
	pattern = re.compile(
		f'{re.escape(start_marker)}.*?{re.escape(end_marker)}',
		re.DOTALL
	)

	# Create replacement string with markers
	replacement = f"{start_marker}\n{generated_content}\n{end_marker}"

	# Check if pattern matches
	match = pattern.search(bank_content)
	if not match:
		print(f"ERROR: Could not find markers in {bank_file}")
		print(f"  Start: {start_marker}")
		print(f"  End: {end_marker}")
		return False

	# Do replacement
	new_content, count = pattern.subn(replacement, bank_content)

	if count != 1:
		print(f"WARNING: Expected 1 replacement, got {count}")

	# Report changes
	old_size = len(bank_content)
	new_size = len(new_content)
	matched_size = len(match.group())
	replacement_size = len(replacement)

	print(f"Original size: {old_size}")
	print(f"Matched section: {matched_size} bytes")
	print(f"Replacement: {replacement_size} bytes")
	print(f"New size: {new_size}")
	print(f"Size change: {new_size - old_size:+d} bytes (expected {replacement_size - matched_size:+d})")

	# Write modified file (don't specify newline parameter - let Python use system default CRLF on Windows)
	with open(bank_path, 'w', encoding='utf-8') as f:
		f.write(new_content)

	print(f"SUCCESS: Replaced section in {bank_file}")
	return True

if __name__ == '__main__':
	if len(sys.argv) != 5:
		print("Usage: replace_bank_section.py <bank_file> <generated_file> <start_marker> <end_marker>")
		sys.exit(1)

	success = replace_marked_section(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
	sys.exit(0 if success else 1)
