"""
Rename Lxxxx Labels to Meaningful Names

This script analyzes remaining L[0-9A-Fa-f]{4} labels that are referenced
and renames them based on:
1. What references them (branch target? JSR target? data pointer?)
2. Nearby descriptive labels
3. Context from surrounding code/comments
4. The instruction type at the label

Usage: python tools/rename_l_labels.py [--dry-run]
"""

import re
import sys
from pathlib import Path
from collections import defaultdict
from typing import Optional, Dict, List, Tuple


class LabelRenamer:
    def __init__(self, source_dir: Path):
        self.source_dir = source_dir
        self.file_contents: Dict[str, str] = {}
        self.file_lines: Dict[str, List[str]] = {}
        self.all_labels: Dict[str, str] = {}  # label -> file
        self.references: Dict[str, List[Tuple[str, int, str]]] = defaultdict(list)  # label -> [(file, line, context)]

    def load_files(self):
        """Load all source files."""
        source_files = ['Bank00.asm', 'Bank01.asm', 'Bank02.asm', 'Bank03.asm', 'Dragon_Warrior_Defines.asm']
        for fname in source_files:
            fpath = self.source_dir / fname
            if fpath.exists():
                content = fpath.read_text(encoding='utf-8')
                self.file_contents[fname] = content
                self.file_lines[fname] = content.split('\n')

    def find_all_labels(self):
        """Find all label definitions."""
        label_pattern = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*):', re.MULTILINE)
        for fname, content in self.file_contents.items():
            for match in label_pattern.finditer(content):
                self.all_labels[match.group(1)] = fname

    def find_references(self):
        """Find all references to Lxxxx labels."""
        l_label_pattern = re.compile(r'\b(L[0-9A-Fa-f]{4})\b')

        for fname, lines in self.file_lines.items():
            for i, line in enumerate(lines):
                # Skip label definitions
                if re.match(r'^L[0-9A-Fa-f]{4}:', line):
                    continue

                for match in l_label_pattern.finditer(line):
                    label = match.group(1)
                    if label in self.all_labels:
                        self.references[label].append((fname, i, line.strip()))

    def get_nearby_context(self, fname: str, line_num: int, radius: int = 10) -> str:
        """Get context around a line."""
        lines = self.file_lines[fname]
        start = max(0, line_num - radius)
        end = min(len(lines), line_num + radius + 1)
        return '\n'.join(lines[start:end])

    def find_parent_function(self, fname: str, line_num: int) -> Optional[str]:
        """Find the function/section this label belongs to."""
        lines = self.file_lines[fname]
        # Search backwards for a named label (not Lxxxx)
        named_label_pattern = re.compile(r'^([A-Za-z_][A-Za-z0-9_]*):')

        for i in range(line_num, -1, -1):
            match = named_label_pattern.match(lines[i])
            if match:
                label = match.group(1)
                # Skip Lxxxx labels
                if not re.match(r'^L[0-9A-Fa-f]{4}$', label):
                    return label
        return None

    def analyze_instruction(self, line: str) -> Tuple[str, str]:
        """Analyze the instruction at a label to determine its purpose."""
        line = line.strip()

        # Remove label prefix if present
        if ':' in line:
            line = line.split(':', 1)[1].strip()

        # Common instruction patterns
        if line.startswith('RTS'):
            return 'Exit', 'function exit point'
        elif line.startswith('RTI'):
            return 'InterruptReturn', 'interrupt return'
        elif line.startswith('JMP'):
            return 'Jump', 'unconditional jump'
        elif line.startswith('JSR'):
            return 'Call', 'subroutine call'
        elif line.startswith('LDA'):
            return 'Load', 'load accumulator'
        elif line.startswith('LDX'):
            return 'LoadX', 'load X register'
        elif line.startswith('LDY'):
            return 'LoadY', 'load Y register'
        elif line.startswith('STA'):
            return 'Store', 'store accumulator'
        elif line.startswith('STX'):
            return 'StoreX', 'store X register'
        elif line.startswith('STY'):
            return 'StoreY', 'store Y register'
        elif line.startswith('INC'):
            return 'Increment', 'increment'
        elif line.startswith('DEC'):
            return 'Decrement', 'decrement'
        elif line.startswith('CMP'):
            return 'Compare', 'comparison'
        elif line.startswith('CPX'):
            return 'CompareX', 'compare X'
        elif line.startswith('CPY'):
            return 'CompareY', 'compare Y'
        elif line.startswith('BEQ'):
            return 'BranchEqual', 'branch if equal'
        elif line.startswith('BNE'):
            return 'BranchNotEqual', 'branch if not equal'
        elif line.startswith('BCS'):
            return 'BranchCarrySet', 'branch if carry set'
        elif line.startswith('BCC'):
            return 'BranchCarryClear', 'branch if carry clear'
        elif line.startswith('BMI'):
            return 'BranchMinus', 'branch if minus'
        elif line.startswith('BPL'):
            return 'BranchPlus', 'branch if plus'
        elif line.startswith('ASL'):
            return 'ShiftLeft', 'arithmetic shift left'
        elif line.startswith('LSR'):
            return 'ShiftRight', 'logical shift right'
        elif line.startswith('ROL'):
            return 'RotateLeft', 'rotate left'
        elif line.startswith('ROR'):
            return 'RotateRight', 'rotate right'
        elif line.startswith('AND'):
            return 'And', 'bitwise AND'
        elif line.startswith('ORA'):
            return 'Or', 'bitwise OR'
        elif line.startswith('EOR'):
            return 'Xor', 'bitwise XOR'
        elif line.startswith('ADC'):
            return 'Add', 'add with carry'
        elif line.startswith('SBC'):
            return 'Subtract', 'subtract with borrow'
        elif line.startswith('SEC'):
            return 'SetCarry', 'set carry flag'
        elif line.startswith('CLC'):
            return 'ClearCarry', 'clear carry flag'
        elif line.startswith('SEI'):
            return 'DisableInterrupts', 'disable interrupts'
        elif line.startswith('CLI'):
            return 'EnableInterrupts', 'enable interrupts'
        elif line.startswith('PHA'):
            return 'PushA', 'push accumulator'
        elif line.startswith('PLA'):
            return 'PullA', 'pull accumulator'
        elif line.startswith('PHP'):
            return 'PushStatus', 'push status'
        elif line.startswith('PLP'):
            return 'PullStatus', 'pull status'
        elif line.startswith('TAX'):
            return 'TransferAX', 'transfer A to X'
        elif line.startswith('TAY'):
            return 'TransferAY', 'transfer A to Y'
        elif line.startswith('TXA'):
            return 'TransferXA', 'transfer X to A'
        elif line.startswith('TYA'):
            return 'TransferYA', 'transfer Y to A'
        elif line.startswith('INX'):
            return 'IncrementX', 'increment X'
        elif line.startswith('INY'):
            return 'IncrementY', 'increment Y'
        elif line.startswith('DEX'):
            return 'DecrementX', 'decrement X'
        elif line.startswith('DEY'):
            return 'DecrementY', 'decrement Y'
        elif line.startswith('NOP'):
            return 'NoOp', 'no operation'
        elif line.startswith('.byte'):
            return 'Data', 'data byte'
        elif line.startswith('.word'):
            return 'Pointer', 'data word/pointer'
        elif line.startswith('.text'):
            return 'Text', 'text data'

        return 'Code', 'code'

    def analyze_reference_type(self, ref_line: str) -> str:
        """Determine what type of reference this is."""
        ref_line = ref_line.upper()
        if 'BNE' in ref_line or 'BEQ' in ref_line:
            return 'Loop'
        elif 'BCS' in ref_line or 'BCC' in ref_line:
            return 'Branch'
        elif 'BMI' in ref_line or 'BPL' in ref_line:
            return 'Check'
        elif 'BVS' in ref_line or 'BVC' in ref_line:
            return 'Overflow'
        elif 'JSR' in ref_line:
            return 'Func'
        elif 'JMP' in ref_line:
            return 'Jump'
        elif '.WORD' in ref_line:
            return 'Ptr'
        return 'Ref'

    def generate_name(self, label: str, fname: str, line_num: int) -> str:
        """Generate a meaningful name for an Lxxxx label."""
        lines = self.file_lines[fname]
        label_line = lines[line_num]

        # Get the address from the label
        addr = label[1:]  # Remove 'L' prefix

        # Find parent function
        parent = self.find_parent_function(fname, line_num)

        # Analyze the instruction at this label
        instr_type, _ = self.analyze_instruction(label_line)

        # Get reference types
        refs = self.references.get(label, [])
        ref_types = set()
        for _, _, ref_line in refs:
            ref_types.add(self.analyze_reference_type(ref_line))

        # Extract any comment hints
        comment = ''
        if ';' in label_line:
            comment = label_line.split(';', 1)[1].strip()

        # Try to extract meaningful words from comment
        comment_hint = ''
        if comment:
            # Remove address references like ($XXXX)
            clean_comment = re.sub(r'\(\$[0-9A-Fa-f]+\)', '', comment)
            # Extract first few meaningful words
            words = re.findall(r'[A-Za-z][a-z]+', clean_comment)
            if words:
                # Take up to 3 words, capitalize each
                comment_hint = ''.join(w.capitalize() for w in words[:3])

        # Determine the suffix based on reference type
        suffix = ''
        if 'Loop' in ref_types:
            suffix = 'Loop'
        elif 'Func' in ref_types:
            suffix = 'Sub'
        elif 'Jump' in ref_types:
            suffix = 'Jmp'
        elif 'Ptr' in ref_types:
            suffix = 'Entry'
        elif 'Branch' in ref_types or 'Check' in ref_types:
            suffix = 'Chk'

        # Build the new name
        if comment_hint and len(comment_hint) > 3:
            # Use comment-derived name
            if suffix:
                new_name = f"{comment_hint}{suffix}"
            else:
                new_name = comment_hint
        elif parent:
            # Use parent function with suffix
            short_parent = parent
            if len(parent) > 12:
                short_parent = parent[:10]
            if suffix:
                new_name = f"{short_parent}_{suffix}"
            else:
                new_name = f"{short_parent}_{instr_type}"
        else:
            # Fallback to instruction type
            new_name = f"{instr_type}_{addr}"

        # Ensure valid identifier (no spaces, starts with letter)
        new_name = re.sub(r'[^A-Za-z0-9_]', '', new_name)
        if not new_name or not new_name[0].isalpha():
            new_name = f"L_{addr}"

        return new_name

    def find_lxxxx_labels(self) -> List[Tuple[str, str, int]]:
        """Find all Lxxxx labels with their file and line number."""
        results = []
        l_pattern = re.compile(r'^(L[0-9A-Fa-f]{4}):')

        for fname, lines in self.file_lines.items():
            for i, line in enumerate(lines):
                match = l_pattern.match(line)
                if match:
                    results.append((match.group(1), fname, i))

        return results

    def rename_labels(self, dry_run: bool = False) -> Dict[str, Dict[str, str]]:
        """Rename all Lxxxx labels to meaningful names."""
        print("Loading files...")
        self.load_files()

        print("Finding all labels...")
        self.find_all_labels()

        print("Finding references...")
        self.find_references()

        print("Analyzing Lxxxx labels...")
        lxxxx_labels = self.find_lxxxx_labels()

        # Generate new names
        renames: Dict[str, str] = {}  # old_name -> new_name
        name_counts: Dict[str, int] = defaultdict(int)  # Track name usage for uniqueness

        for label, fname, line_num in lxxxx_labels:
            new_name = self.generate_name(label, fname, line_num)

            # Ensure uniqueness
            base_name = new_name
            while new_name in renames.values() or new_name in self.all_labels:
                name_counts[base_name] += 1
                new_name = f"{base_name}_{name_counts[base_name]}"

            renames[label] = new_name

        print(f"Generated {len(renames)} new names")

        if dry_run:
            print("\nDRY RUN - Sample renames:")
            for i, (old, new) in enumerate(list(renames.items())[:30]):
                print(f"  {old} -> {new}")
            return {}

        # Apply renames to all files
        print("Applying renames...")
        changes_by_file: Dict[str, int] = defaultdict(int)

        for fname in self.file_contents.keys():
            content = self.file_contents[fname]
            original = content

            # Replace each label (definition and references)
            for old_name, new_name in renames.items():
                # Replace definition: "OLD_NAME:" -> "NEW_NAME:"
                content = re.sub(
                    rf'^{re.escape(old_name)}:',
                    f'{new_name}:',
                    content,
                    flags=re.MULTILINE
                )

                # Replace references (word boundaries)
                content = re.sub(
                    rf'\b{re.escape(old_name)}\b',
                    new_name,
                    content
                )

            if content != original:
                fpath = self.source_dir / fname
                fpath.write_text(content, encoding='utf-8')

                # Count changes
                for old_name in renames.keys():
                    changes_by_file[fname] += original.count(old_name)

        return {'renames': renames, 'changes': dict(changes_by_file)}


def main():
    dry_run = '--dry-run' in sys.argv

    source_dir = Path('source_files')
    renamer = LabelRenamer(source_dir)

    result = renamer.rename_labels(dry_run)

    if not dry_run and result:
        print(f"\nRenamed {len(result.get('renames', {}))} labels")
        print("\nChanges by file:")
        for fname, count in result.get('changes', {}).items():
            print(f"  {fname}: {count} occurrences updated")


if __name__ == '__main__':
    main()
