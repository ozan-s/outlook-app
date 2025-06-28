# Milestone 001: Project Setup + Testing Infrastructure

## Objective
Initialize Python project with uv, set up pytest, and establish TDD workflow for cross-platform Outlook CLI development.

## Current State Analysis
- **Starting Point**: Clean repository with PRD and master plan only
- **Dependencies**: None (foundation milestone)
- **Git Status**: On main branch, need to create project branch
- **Environment**: Mac development targeting Windows runtime

## Success Criteria
- [x] Python project initialized with uv (pyproject.toml created)
- [x] pytest framework configured and working
- [x] Project structure established (src/, tests/ directories)
- [x] Basic test runs successfully (`uv run pytest`)
- [x] pywin32 dependency configured (conditional for Windows)
- [x] Git workflow ready for TDD development

## Implementation Approach

### TDD Sequence
1. **Setup**: Create project branch, initialize uv project
2. **Test**: Write simple test to verify pytest working
3. **Structure**: Create src/ and tests/ directories
4. **Dependencies**: Add pytest, pywin32 (platform-conditional)
5. **Verify**: Run test suite, confirm green state

### Project Structure to Create
```
outlook-app/
├── pyproject.toml          # uv project config
├── src/
│   └── outlook_cli/
│       └── __init__.py
├── tests/
│   └── __init__.py
│   └── test_setup.py       # Basic test to verify framework
├── PRD.md                  # (existing)
└── plans/                  # (existing)
```

### Dependencies to Add
- **pytest**: Testing framework
- **pytest-cov**: Code coverage
- **pywin32**: Windows Outlook COM interface (conditional)
- **typing-extensions**: Type hints support

### Integration Points
- **uv**: Project and dependency management
- **pytest**: Test discovery and execution
- **Git**: Branch workflow for TDD
- **Cross-platform**: Mac dev, Windows runtime

### Evidence for Completion
- Command succeeds: `uv run pytest`
- Command succeeds: `uv run pytest --cov=src`
- Project structure matches expected layout
- pyproject.toml contains correct dependencies
- Ready for Milestone 002 (Email models)

## Platform Considerations
- Development on Mac without Windows dependencies
- pywin32 installed but not imported during tests
- Mock strategy ready for platform-specific code

## Notes
- Keep dependencies minimal for foundation
- Focus on TDD workflow establishment
- Ensure project ready for rapid iteration
- No business logic in this milestone - infrastructure only

## COMPLETION STATUS ✅

### TDD Cycle Executed
1. **RED**: Created failing tests for package import and version
2. **GREEN**: Fixed Python path configuration in pyproject.toml
3. **REFACTOR**: Added proper project description and dependencies

### Evidence of Completion
- ✅ `uv run pytest` passes all 3 tests
- ✅ `uv run pytest --cov=src` shows 100% coverage
- ✅ Project structure matches milestone specification
- ✅ pywin32 conditionally configured for Windows
- ✅ All dependencies installed and working

### Final Project Structure
```
outlook-app/
├── pyproject.toml          # ✅ uv project config with dependencies
├── src/
│   └── outlook_cli/
│       └── __init__.py     # ✅ Package with version
├── tests/
│   └── __init__.py         # ✅ Test package
│   └── test_setup.py       # ✅ Infrastructure tests (3 passing)
├── PRD.md                  # (existing)
└── plans/                  # (existing)
```

**READY FOR MILESTONE 002**: Email models implementation