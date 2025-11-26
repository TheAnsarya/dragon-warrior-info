---
name: Pull Request
about: Submit code contributions
title: ''
labels: ''
assignees: ''
---

## Description

**Summary of changes:**


**Related issue(s):**
- Closes #[issue number]
- Relates to #[issue number]

## Type of Change

- [ ] 🐛 Bug fix (non-breaking change fixing an issue)
- [ ] ✨ New feature (non-breaking change adding functionality)
- [ ] 💥 Breaking change (fix or feature causing existing functionality to break)
- [ ] 📚 Documentation update
- [ ] 🎨 Code style/refactoring (no functional changes)
- [ ] ⚡ Performance improvement
- [ ] ✅ Test updates
- [ ] 🔧 Build/tooling changes

## Changes Made

**Detailed description of changes:**

### Files Added
- `path/to/new_file.py` - [purpose]

### Files Modified
- `path/to/modified_file.py` - [what changed]

### Files Deleted
- `path/to/removed_file.py` - [why removed]

## Implementation Details

**Technical approach:**


**Design decisions:**


**Trade-offs considered:**


## Testing

### Unit Tests

**Tests added/updated:**
```python
# Example test
def test_new_feature():
    result = new_function()
    assert result == expected_value
```

**Test coverage:**
```
# Output of: pytest --cov
Module                  Coverage
----------------------- --------
tools/new_module.py        95%
```

### Manual Testing

**Manual test procedure:**

1. Step 1:
   - Command: `python tools/...`
   - Expected: [result]
   - Actual: [result]

2. Step 2:
   - Command: `...`
   - Expected: [result]
   - Actual: [result]

**Test results:**
- [ ] All unit tests pass
- [ ] Manual testing completed
- [ ] No regressions found

### ROM/Emulator Testing

**For ROM modifications only:**

**Test ROM:**
- ROM Version: Dragon Warrior (U) (PRG1)
- Modified sections: [list]

**Emulator testing:**
- [ ] Tested in FCEUX
- [ ] Tested in Mesen
- [ ] No crashes observed
- [ ] Changes verified in-game

**Test scenarios:**
1. [Scenario 1] - ✅ Passed
2. [Scenario 2] - ✅ Passed
3. [Scenario 3] - ✅ Passed

## Screenshots

**Before/After comparisons (if applicable):**

### Before
<!-- Add screenshots or code showing before state -->

### After
<!-- Add screenshots or code showing after state -->

## Documentation

**Documentation updated:**

- [ ] Code docstrings added/updated
- [ ] README.md updated
- [ ] Guide documents updated (docs/)
- [ ] Help text updated (`--help`)
- [ ] Examples added
- [ ] API documentation updated
- [ ] Comments added for complex code

**Documentation locations:**
- Updated: [list files]
- Added: [list files]

## Code Quality

### Style Compliance

```powershell
# Black formatting
black --check tools/ tests/
✓ Code formatted correctly

# Flake8 linting  
flake8 tools/ tests/
✓ No linting errors

# Mypy type checking
mypy tools/
✓ Type hints valid
```

**Code quality checklist:**
- [ ] Follows PEP 8 style guide
- [ ] Code formatted with Black
- [ ] Passes flake8 linting
- [ ] Type hints added
- [ ] Passes mypy type checking
- [ ] No hardcoded values (uses constants)
- [ ] Error handling implemented
- [ ] Edge cases handled

### Code Review

**Self-review checklist:**
- [ ] Reviewed all changes before submitting
- [ ] Removed debug code and print statements
- [ ] No commented-out code
- [ ] No TODOs without issue tracking
- [ ] Variable names are descriptive
- [ ] Functions have single responsibility
- [ ] Complex logic is commented

## Breaking Changes

**Does this introduce breaking changes?**
- [ ] No breaking changes
- [ ] Yes - breaking changes described below

**Breaking change details:**

**Migration guide:**


## Performance Impact

**Performance testing:**
- [ ] No performance impact
- [ ] Performance improved
- [ ] Performance degraded (justified below)

**Benchmark results (if applicable):**

| Operation | Before | After | Change |
|-----------|--------|-------|--------|
| Extract   | 2.5s   | 1.8s  | +28%   |
| Transform | 1.2s   | 1.1s  | +8%    |

## Backwards Compatibility

**Compatibility considerations:**
- [ ] Fully backwards compatible
- [ ] Requires data migration
- [ ] Changes configuration format
- [ ] Updates file format

**Migration required?**
- [ ] No migration needed
- [ ] Automatic migration provided
- [ ] Manual migration required (documented)

## Dependencies

**New dependencies added:**
- `package==version` - [reason]

**Dependencies updated:**
- `package` from `old_version` to `new_version` - [reason]

**Dependencies removed:**
- `package` - [reason for removal]

## Deployment Notes

**Special deployment considerations:**
- [ ] Requires new environment variables
- [ ] Requires configuration updates
- [ ] Requires data migration
- [ ] Requires clean rebuild

**Deployment checklist:**
- [ ] Updated requirements.txt
- [ ] Updated installation instructions
- [ ] Tested clean install
- [ ] Tested upgrade path

## Rollback Plan

**If issues arise after merge:**

1. Revert steps:
2. Notify users:
3. Fix forward approach:

## Additional Context

**Context for reviewers:**


**Design references:**
- [Link to design document]
- [Link to discussion]

**Questions for reviewers:**
1. 
2. 

## Reviewer Checklist

**For reviewers:**

- [ ] Code follows project style guide
- [ ] Changes are well-documented
- [ ] Tests are adequate and pass
- [ ] No security concerns
- [ ] No performance regressions
- [ ] Documentation is clear
- [ ] Breaking changes are justified
- [ ] Commit messages follow convention

## Follow-up Work

**Future improvements (not in this PR):**
- [ ] Create issue: [description] #[issue]
- [ ] Create issue: [description] #[issue]

---

## Pre-submission Checklist

**Before submitting this PR:**

- [ ] Branch is up to date with main
- [ ] All tests pass locally
- [ ] Code is properly formatted
- [ ] Documentation is complete
- [ ] Self-review completed
- [ ] No merge conflicts
- [ ] Commit messages are descriptive
- [ ] Ready for review

---

**Additional Notes:**

<!-- Any other information for reviewers -->
