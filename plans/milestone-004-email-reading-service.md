# Milestone 004: Email Reading Service + Tests

## Objective
Create EmailReader service to get emails from folders using the OutlookAdapter interface with proper error handling and dependency injection.

## Current State Analysis
- Dependency check: ✅ OutlookAdapter interface complete with MockOutlookAdapter
- Adapter interface methods: get_folders(), get_folder_info(folder_path), get_emails(folder_path), move_email()
- MockAdapter test data: Inbox (3 emails), Sent Items (2 emails), Drafts (1 email)
- Existing pattern: Pydantic models, abc.ABC interfaces, dependency injection ready
- No services directory exists yet - clean slate for service layer

## Success Criteria
- [x] EmailReader service takes OutlookAdapter via dependency injection
- [x] Can get all emails from a specific folder
- [x] Can get emails from all folders
- [x] Proper error handling for invalid folder paths
- [x] Service is adapter-agnostic (works with mock or future real adapter)
- [x] Integration: Works with existing OutlookAdapter interface

## Implementation Approach

### TDD Sequence
1. **Test**: EmailReader constructor takes adapter parameter
2. **Test**: get_emails_from_folder("Inbox") returns List[Email] via adapter
3. **Test**: get_emails_from_folder("NonExistent") raises ValueError
4. **Test**: get_all_emails() returns emails from all folders
5. **Test**: Service works with MockOutlookAdapter integration
6. **Test**: Error handling preserves adapter error messages

### File Structure
```
src/outlook_cli/
├── services/
│   ├── __init__.py
│   └── email_reader.py
tests/
├── services/
│   ├── __init__.py
│   └── test_email_reader.py
```

### Integration Points
- OutlookAdapter: Uses get_emails() and get_folders() methods
- Email model: Returns List[Email] from existing models
- Error handling: Propagates adapter ValueError exceptions

### Service Interface Design
```python
class EmailReader:
    def __init__(self, adapter: OutlookAdapter)
    def get_emails_from_folder(self, folder_path: str) -> List[Email]
    def get_all_emails() -> Dict[str, List[Email]]  # folder_path -> emails
```

## Evidence for Completion
- All tests passing: `uv run pytest tests/services/`
- EmailReader works with MockOutlookAdapter
- Can retrieve emails from specific folders: reader.get_emails_from_folder("Inbox")
- Can retrieve all emails: reader.get_all_emails()
- Error handling works: ValueError for invalid folder paths
- Service follows dependency injection pattern established in milestone 003

## Validation Results

### What Works
- EmailReader service integrates cleanly with OutlookAdapter interface
- Dependency injection pattern works correctly
- Error handling propagates adapter errors properly
- Empty folders handled correctly (return empty lists)
- Data integrity maintained between single-folder and all-folders methods
- Ready for future PyWin32Adapter integration

### Evidence
- **Test suite**: 47/47 tests pass with no regressions
- **Import test**: `from outlook_cli.services import EmailReader` ✅
- **Functionality test**: Retrieved 3 emails from Inbox via MockAdapter
- **Error handling**: `ValueError: Folder 'NonExistentFolder' not found` ✅
- **Integration scenarios**: All 5 realistic scenarios pass
- **Dependency injection**: Accepts any OutlookAdapter implementation

### Manual Verification Commands
```python
# Import and basic usage
from outlook_cli.services import EmailReader
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter

adapter = MockOutlookAdapter()
reader = EmailReader(adapter)

# Get specific folder emails
emails = reader.get_emails_from_folder("Inbox")  # Returns 3 emails

# Get all emails  
all_emails = reader.get_all_emails()  # Returns dict with 6 folders

# Error handling
reader.get_emails_from_folder("DoesNotExist")  # Raises ValueError
```

### Issues Fixed
None - integration worked perfectly on first validation.

### Ready for Commit
✅ All integration points validated
✅ Service layer foundation established for future CLI commands
✅ Dependency injection ready for milestone 013 (PyWin32Adapter)

## Notes
- Service layer enables future CLI commands and business logic
- Adapter-agnostic design supports both mock and real Outlook adapters
- Foundation for EmailSearcher and EmailMover services in future milestones
- No pagination logic yet - that's milestone 007