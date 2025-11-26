# Contributing to Dragon Warrior ROM Hacking Toolkit

Thank you for your interest in contributing! This document provides guidelines for contributing to the Dragon Warrior ROM Hacking Toolkit.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Commit Message Guidelines](#commit-message-guidelines)
- [Testing Requirements](#testing-requirements)
- [Documentation Standards](#documentation-standards)
- [Pull Request Process](#pull-request-process)
- [Issue Reporting](#issue-reporting)
- [Feature Requests](#feature-requests)

## Code of Conduct

This project adheres to a Code of Conduct that all contributors are expected to follow. Please read [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) before contributing.

Key principles:
- **Be respectful** - Treat all contributors with respect and courtesy
- **Be inclusive** - Welcome contributors of all skill levels and backgrounds
- **Be collaborative** - Work together to improve the toolkit
- **Be constructive** - Provide helpful feedback and suggestions

## Getting Started

### Prerequisites

Before contributing, ensure you have:

1. **Python 3.8+** installed
2. **Git** for version control
3. **Dragon Warrior (U) (PRG1) ROM** (legally obtained)
4. **NES emulator** (FCEUX or Mesen recommended) for testing

### Setting Up Development Environment

```powershell
# Clone the repository
git clone https://github.com/yourusername/dragon-warrior-info.git
cd dragon-warrior-info

# Install Python dependencies
pip install -r requirements.txt

# Install development dependencies
pip install pytest pytest-cov black flake8 mypy

# Verify setup
python tools/extract_all_data.py --help
```

### Repository Structure

```
dragon-warrior-info/
├── tools/              # Python scripts and utilities
├── docs/               # Documentation
├── assets/             # Asset storage (JSON, PNG, etc.)
├── tests/              # Unit and integration tests
├── build/              # Build output directory
├── roms/               # ROM files (not committed)
└── extracted_assets/   # Extracted game data
```

## Development Workflow

### 1. Fork and Branch

```powershell
# Fork the repository on GitHub
# Clone your fork
git clone https://github.com/YOUR_USERNAME/dragon-warrior-info.git
cd dragon-warrior-info

# Add upstream remote
git remote add upstream https://github.com/ORIGINAL_OWNER/dragon-warrior-info.git

# Create a feature branch
git checkout -b feature/your-feature-name
```

### 2. Make Changes

- Write code following the [Coding Standards](#coding-standards)
- Add/update tests as needed
- Update documentation to reflect changes
- Test your changes thoroughly

### 3. Commit Changes

```powershell
# Stage your changes
git add .

# Commit with descriptive message (see Commit Message Guidelines)
git commit -m "feat(monsters): add support for custom monster sprites"
```

### 4. Push and Create Pull Request

```powershell
# Push to your fork
git push origin feature/your-feature-name

# Create Pull Request on GitHub
# Follow the Pull Request Template
```

## Coding Standards

### Python Style Guide

We follow **PEP 8** with some customizations:

#### Formatting

- **Indentation**: 4 spaces (no tabs)
- **Line length**: 100 characters maximum (code), 80 for docstrings
- **Blank lines**: 2 between top-level definitions, 1 between methods
- **Imports**: Organized in order (standard library, third-party, local)

```python
# Good example
import sys
import os
from pathlib import Path

import PIL.Image
import numpy as np

from tools.extract_to_binary import ROMExtractor
```

#### Naming Conventions

- **Functions/variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private members**: `_leading_underscore`

```python
# Good example
class MonsterEditor:
    MAX_MONSTERS = 39
    
    def __init__(self, rom_path: str):
        self._rom_data = None
        self.monster_count = 0
    
    def load_monsters(self) -> List[Dict]:
        """Load monster data from ROM"""
        pass
```

#### Type Hints

Use type hints for all function parameters and return values:

```python
from typing import List, Dict, Optional, Tuple

def extract_monsters(rom_data: bytes, offset: int) -> List[Dict[str, int]]:
    """
    Extract monster data from ROM
    
    Args:
        rom_data: ROM file contents
        offset: Start offset for monster data
        
    Returns:
        List of monster dictionaries
    """
    pass
```

#### Docstrings

Use Google-style docstrings for all modules, classes, and functions:

```python
def modify_monster_stats(
    monster_id: int,
    hp: Optional[int] = None,
    attack: Optional[int] = None
) -> bool:
    """
    Modify monster statistics
    
    Args:
        monster_id: Monster ID (0-38)
        hp: New HP value (1-255), None to keep current
        attack: New attack value (0-255), None to keep current
        
    Returns:
        True if modification successful, False otherwise
        
    Raises:
        ValueError: If monster_id is out of range
        
    Examples:
        >>> modify_monster_stats(0, hp=50)  # Boost Slime HP
        True
        >>> modify_monster_stats(99)  # Invalid ID
        ValueError: monster_id must be 0-38
    """
    pass
```

### Code Formatting

Use **Black** for automatic formatting:

```powershell
# Format all Python files
black tools/ tests/

# Check formatting without modifying
black --check tools/
```

### Linting

Use **flake8** for linting:

```powershell
# Run linter
flake8 tools/ tests/

# Configuration in setup.cfg
```

### Type Checking

Use **mypy** for static type checking:

```powershell
# Run type checker
mypy tools/

# Configuration in mypy.ini
```

## Commit Message Guidelines

We follow **Conventional Commits** specification:

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic change)
- **refactor**: Code refactoring (no feature change)
- **perf**: Performance improvements
- **test**: Adding or updating tests
- **build**: Build system changes
- **ci**: CI/CD changes
- **chore**: Maintenance tasks

### Scopes

- **monsters**: Monster data/editing
- **spells**: Spell data/editing
- **items**: Item data/editing
- **maps**: Map data/editing
- **text**: Text/dialog editing
- **graphics**: Graphics/sprites
- **binary**: Binary pipeline
- **rom**: ROM building/modification
- **tools**: General tools
- **docs**: Documentation

### Examples

```
feat(monsters): add sprite sharing analysis tool

Implemented analyze_monster_sprites.py to identify sprite
reuse patterns across all 39 monsters. Generates JSON and
Markdown reports showing sprite families and tile counts.

Closes #123
```

```
fix(binary): correct CRC32 validation in binary_to_assets

Fixed bug where CRC32 checksum validation was using wrong
byte order. Now properly validates little-endian checksums.

Fixes #456
```

```
docs(readme): add binary pipeline workflow diagram

Added ASCII diagram showing the complete binary pipeline
flow from ROM extraction to reinsertion.
```

## Testing Requirements

### Unit Tests

All new code must include unit tests:

```python
# tests/test_monster_editor.py
import pytest
from tools.monster_editor import MonsterEditor

def test_load_monsters():
    """Test monster loading from JSON"""
    editor = MonsterEditor('extracted_assets')
    monsters = editor.load_monsters()
    
    assert len(monsters) == 39
    assert monsters[0]['name'] == 'Slime'
    assert 1 <= monsters[0]['hp'] <= 255

def test_validate_monster_stats():
    """Test monster stat validation"""
    editor = MonsterEditor('extracted_assets')
    
    # Valid stats
    assert editor.validate_monster({'hp': 50, 'attack': 20})
    
    # Invalid HP
    assert not editor.validate_monster({'hp': 0, 'attack': 20})
    assert not editor.validate_monster({'hp': 300, 'attack': 20})
```

### Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=tools --cov-report=html

# Run specific test file
pytest tests/test_monster_editor.py

# Run specific test
pytest tests/test_monster_editor.py::test_load_monsters
```

### Test Coverage Requirements

- **Minimum coverage**: 80% for new code
- **Critical paths**: 100% coverage required
- **Edge cases**: Must be tested
- **Error handling**: Must include negative tests

### Emulator Testing

For ROM modifications, include emulator testing instructions:

```markdown
## Emulator Testing

1. Build modified ROM: `python dragon_warrior_build.py`
2. Load in FCEUX emulator
3. Test specific features:
   - [ ] Monster stats match expected values
   - [ ] Sprites display correctly
   - [ ] No crashes during gameplay
4. Attach screenshots showing changes
```

## Documentation Standards

### Code Documentation

- **All modules** must have a module docstring
- **All classes** must have a class docstring
- **All public functions** must have docstrings with:
	- Brief description
	- Args section
	- Returns section
	- Raises section (if applicable)
	- Examples section (recommended)

### User Documentation

When adding features, update:

1. **README.md** - If it affects main workflow
2. **docs/** - Create/update relevant guide documents
3. **Tool help text** - Update `--help` output
4. **Example scripts** - Add usage examples

### Documentation Examples

```python
"""
Dragon Warrior Monster Editor

This module provides functionality for editing monster statistics,
including HP, attack, defense, and rewards.

Usage:
    from tools.monster_editor import MonsterEditor
    
    editor = MonsterEditor('extracted_assets')
    editor.modify_monster(0, hp=100)  # Power up Slime
    editor.save_monsters()

Author: Dragon Warrior ROM Hacking Toolkit
"""
```

## Pull Request Process

### Before Submitting

**Checklist:**
- [ ] Code follows style guide (run `black` and `flake8`)
- [ ] All tests pass (`pytest`)
- [ ] Coverage meets minimum 80% (`pytest --cov`)
- [ ] Documentation updated (docstrings, README, guides)
- [ ] Commit messages follow convention
- [ ] Branch is up to date with main branch
- [ ] No unrelated changes included

### Pull Request Template

When creating a PR, use this template:

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [ ] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to break)
- [ ] Documentation update

## Testing
Describe testing performed:
- [ ] Unit tests added/updated
- [ ] Manual testing completed
- [ ] Emulator testing performed (for ROM changes)

## Screenshots (if applicable)
Add screenshots showing changes

## Checklist
- [ ] Code follows style guide
- [ ] Self-review completed
- [ ] Comments added for complex code
- [ ] Documentation updated
- [ ] Tests pass
- [ ] No new warnings

## Related Issues
Closes #(issue number)
```

### Review Process

1. **Automated checks** must pass (CI/CD)
2. **Code review** by at least one maintainer
3. **Testing verification** by reviewer
4. **Documentation review** for completeness
5. **Approval** by maintainer(s)
6. **Merge** to main branch

### Review Timeline

- Initial review: Within 3-5 days
- Follow-up reviews: Within 1-2 days
- Merge after approval: Within 1 day

## Issue Reporting

### Bug Reports

Use the **Bug Report** template and include:

1. **ROM Version**: Dragon Warrior (U) (PRG1) or other
2. **Steps to Reproduce**: Detailed steps
3. **Expected Behavior**: What should happen
4. **Actual Behavior**: What actually happens
5. **Screenshots**: If applicable
6. **Error Messages**: Full error text
7. **Environment**: OS, Python version, dependencies

### Example Bug Report

```markdown
**ROM Version:** Dragon Warrior (U) (PRG1)

**Steps to Reproduce:**
1. Run `python tools/extract_to_binary.py`
2. Run `python tools/binary_to_assets.py`
3. Observe CRC32 mismatch error

**Expected:** Assets extract successfully
**Actual:** ValidationError: CRC32 mismatch

**Environment:**
- OS: Windows 11
- Python: 3.10.5
- Dependencies: See requirements.txt
```

## Feature Requests

When requesting features:

1. **Use case**: Describe the problem
2. **Proposed solution**: Your idea
3. **Alternatives**: Other approaches considered
4. **Priority**: How important is this?
5. **Willing to contribute**: Can you implement it?

## Questions and Support

- **GitHub Discussions**: For questions and general discussion
- **Issues**: For bug reports and feature requests
- **Pull Requests**: For code contributions

## Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **Documentation** for major features

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to the Dragon Warrior ROM Hacking Toolkit! 🎮**
