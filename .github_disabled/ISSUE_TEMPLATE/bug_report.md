---
name: Bug Report
about: Report a bug or issue with the toolkit
title: '[BUG] '
labels: bug
assignees: ''
---

## Bug Description

**Clear and concise description of the bug:**


## Environment

**ROM Information:**
- ROM Version: [e.g., Dragon Warrior (U) (PRG1)]
- ROM Size: [e.g., 81936 bytes]
- ROM MD5: [if known]

**System Information:**
- OS: [e.g., Windows 11, macOS 13, Ubuntu 22.04]
- Python Version: [e.g., 3.10.5]
- Shell: [e.g., PowerShell, Bash, Zsh]

**Toolkit Version:**
- Git Commit: [e.g., 814c9b4]
- Branch: [e.g., main, feature/binary-pipeline]

**Dependencies:**
```
# Output of: pip list | findstr -i "pillow numpy"
Pillow==10.0.0
numpy==1.24.0
# etc.
```

## Steps to Reproduce

**Detailed steps to reproduce the behavior:**

1. Run command: `python tools/...`
2. With arguments: `--rom path/to/rom.nes`
3. Observe error at: `...`
4. See error message: `...`

**Minimal reproducible example (if applicable):**

```python
# Code that reproduces the issue
from tools.extract_to_binary import ROMExtractor

extractor = ROMExtractor('path/to/rom.nes')
# ...
```

## Expected Behavior

**What you expected to happen:**


## Actual Behavior

**What actually happened:**


## Error Messages

**Full error output:**

```
# Paste complete error traceback here
Traceback (most recent call last):
  File "tools/...", line X, in <module>
    ...
Error: ...
```

## Screenshots

**If applicable, add screenshots:**

<!-- Drag and drop images here -->

## Additional Context

**ROM Modifications:**
- [ ] Using original, unmodified ROM
- [ ] Using previously modified ROM
- [ ] Applied custom patches: [describe]

**Recent Changes:**
- [ ] First time running this tool
- [ ] Worked previously, broke after: [describe change]
- [ ] Following a tutorial: [link]

**Related Issues:**
- Possibly related to #[issue number]

**Attempted Solutions:**
<!-- What have you tried to fix this? -->
- [ ] Cleared extracted_assets directory
- [ ] Re-downloaded ROM file
- [ ] Reinstalled dependencies
- [ ] Tried different ROM file
- [ ] Other: [describe]

## Files

**Relevant files (if small enough to attach):**

<!-- 
Attach relevant files:
- Configuration files
- Small JSON data files
- Build reports
- Log files

DO NOT attach ROM files or large binary files
-->

## Severity

**Impact of this bug:**
- [ ] Critical - Prevents core functionality
- [ ] High - Major feature broken
- [ ] Medium - Feature partially broken
- [ ] Low - Minor issue or cosmetic

**Workaround Available:**
- [ ] Yes: [describe workaround]
- [ ] No

## Checklist

Before submitting, please check:

- [ ] I searched existing issues and this is not a duplicate
- [ ] I am using a legally obtained ROM file
- [ ] I included complete error messages and traceback
- [ ] I described steps to reproduce clearly
- [ ] I tested with the latest version from main branch
- [ ] I included relevant system/environment information

---

**Additional Information:**

<!-- Any other context, observations, or notes -->
