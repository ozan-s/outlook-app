# Milestone 006: Email Move Service + Tests

## Objective
Create EmailMover service to transfer emails between folders using the OutlookAdapter interface with proper validation and error handling.

## Current State Analysis
- Dependency check: ✅ OutlookAdapter interface complete + EmailReader/EmailSearcher services working
- Service patterns established: Constructor takes OutlookAdapter, dependency injection, consistent error handling
- OutlookAdapter method available: `move_email(email_id: str, target_folder: str) -> bool`
- MockAdapter test data: 6 emails with known IDs across 6 folders with move_email() implemented
- Testing pattern: Unit tests + Integration tests, pytest fixtures established
- Email model: `id` field for identification, `folder_path` field updated by move operations

## Success Criteria
- [x] EmailMover service takes OutlookAdapter via dependency injection
- [x] Can move single email by ID to target folder (returns bool success)
- [x] Can move multiple emails in batch operation
- [x] Proper error handling for invalid email IDs (raises ValueError)
- [x] Proper error handling for invalid target folders (raises ValueError)
- [x] Integration: Works seamlessly with MockOutlookAdapter test data
- [x] Follows established service patterns (constructor, method naming, typing)

## Implementation Approach

### TDD Sequence
1. **Test**: EmailMover constructor takes adapter parameter
2. **Test**: move_email_to_folder("inbox-001", "Drafts") returns True with MockAdapter
3. **Test**: move_email_to_folder with invalid email_id raises ValueError
4. **Test**: move_email_to_folder with invalid target_folder raises ValueError
5. **Test**: move_multiple_emails() batch operation returns Dict[str, bool] status
6. **Test**: Successful move updates email folder_path via adapter
7. **Test**: Error handling preserves adapter error messages
8. **Test**: Integration with MockOutlookAdapter proves end-to-end functionality

### Service Interface Design
```python
class EmailMover:
    def __init__(self, adapter: OutlookAdapter)
    def move_email_to_folder(self, email_id: str, target_folder: str) -> bool
    def move_multiple_emails(self, email_ids: List[str], target_folder: str) -> Dict[str, bool]
```

### Integration Points
- OutlookAdapter: Uses existing `move_email(email_id, target_folder)` method
- Error handling: Lets adapter ValueError exceptions bubble up (consistent with other services)
- Email identification: Uses Email.id field for operations
- Batch operations: Enables efficient CLI command implementation

### Move Logic Strategy
- **Single email move**: Direct delegation to `adapter.move_email()`
- **Batch operations**: Loop over email IDs, collect success/failure status
- **Error handling**: Don't catch adapter errors - let ValueError propagate
- **Return types**: bool for single moves, Dict[email_id -> bool] for batch

## Evidence for Completion
- All tests passing: `uv run pytest tests/services/test_email_mover.py`
- EmailMover works with MockOutlookAdapter
- Can move email: `mover.move_email_to_folder("inbox-001", "Drafts")` returns True
- Batch move: `mover.move_multiple_emails(["inbox-001", "inbox-002"], "Archive")` returns status dict
- Error handling: ValueError for invalid email IDs and folder paths matches adapter behavior
- Service follows dependency injection pattern for future CLI integration

## Test Cases Based on MockAdapter Data

### Single Email Move Validation
```python
# Valid move operation
result = mover.move_email_to_folder("inbox-001", "Drafts")
assert result is True

# Invalid email ID
with pytest.raises(ValueError, match="Email 'nonexistent' not found"):
    mover.move_email_to_folder("nonexistent", "Drafts")

# Invalid target folder
with pytest.raises(ValueError, match="Target folder 'BadFolder' not found"):
    mover.move_email_to_folder("inbox-001", "BadFolder")
```

### Batch Move Validation
```python
# Multiple emails to same folder
results = mover.move_multiple_emails(["inbox-001", "inbox-002"], "Archive")
assert results == {"inbox-001": True, "inbox-002": True}

# Mixed success/failure scenario
results = mover.move_multiple_emails(["inbox-001", "badid"], "Archive")
assert results["inbox-001"] is True
assert results["badid"] is False  # Graceful handling of bad IDs
```

### Integration Validation
```python
# Verify email actually moved in adapter
mover.move_email_to_folder("inbox-001", "Archive")
moved_email = adapter.get_emails("Archive")[0]  # Should find the moved email
assert moved_email.id == "inbox-001"
assert moved_email.folder_path == "Archive"
```

## Validation Results

### What Works
- EmailMover service integrates cleanly with OutlookAdapter interface
- Dependency injection pattern works correctly following established service patterns
- Single email moves return boolean success status as expected
- Batch operations handle mixed success/failure scenarios gracefully
- Error handling propagates adapter errors properly for invalid IDs and folders
- Empty batch operations handled correctly (return empty dict)
- Email moves actually update folder_path via adapter integration

### Evidence
- **Test suite**: 68/68 tests pass with 9 new EmailMover tests, no regressions
- **Import test**: `from outlook_cli.services import EmailMover` ✅
- **Single move**: `mover.move_email_to_folder("inbox-001", "Drafts")` returns True ✅
- **Batch move**: `mover.move_multiple_emails(["inbox-002", "inbox-003"], "Custom/Archive")` returns status dict ✅
- **Mixed results**: `mover.move_multiple_emails(["sent-001", "badid"], "Drafts")` handles failures gracefully ✅
- **Error handling**: ValueError for invalid email IDs and folder paths matches adapter behavior ✅
- **Integration scenarios**: All move operations work end-to-end with MockOutlookAdapter

### Manual Verification Commands
```python
# Import and basic usage
from outlook_cli.services import EmailMover
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter

adapter = MockOutlookAdapter()
mover = EmailMover(adapter)

# Single email move
result = mover.move_email_to_folder("inbox-001", "Drafts")  # Returns True

# Batch email move
results = mover.move_multiple_emails(["inbox-002", "inbox-003"], "Custom/Archive")  # Returns status dict

# Mixed success/failure handling
mixed_results = mover.move_multiple_emails(["sent-001", "badid"], "Drafts")  # Graceful error handling
```

### Issues Fixed
None - integration worked perfectly on first validation.

### Ready for Commit
✅ All integration points validated
✅ EmailMover foundation established for CLI commands
✅ Service layer complete for email management operations
✅ Ready for milestone 007 (Pagination logic + navigation)

## Notes
- Leverages existing OutlookAdapter move_email() method (no new adapter functionality needed)
- Batch operations enable efficient CLI command implementation (`move email1 email2 target`)
- Foundation for CLI `move [email_id] [target_folder]` command (milestone 011)
- Error handling consistent with EmailReader/EmailSearcher patterns
- Service composition opportunities with EmailSearcher (find emails, then move them)