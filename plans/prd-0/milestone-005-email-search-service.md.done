# Milestone 005: Email Search Service + Tests

## Objective
Create EmailSearcher service for sender/subject filtering using the OutlookAdapter interface with client-side search logic.

## Current State Analysis
- Dependency check: ✅ OutlookAdapter interface complete + EmailReader service working
- EmailReader pattern: Constructor takes OutlookAdapter, dependency injection established
- Adapter methods available: get_emails(folder_path), get_all_emails() via EmailReader
- Email model searchable fields: subject, sender_email, sender_name, folder_path
- MockAdapter test data: 6 emails across 3 folders with varied senders/subjects
- Testing pattern: Unit tests + Integration tests, pytest fixtures established

## Success Criteria
- [x] EmailSearcher service takes OutlookAdapter via dependency injection
- [x] Can search emails by sender email address (case-insensitive)
- [x] Can search emails by sender display name (case-insensitive) 
- [x] Can search emails by subject keywords (partial match, case-insensitive)
- [x] Can combine multiple search criteria (AND logic)
- [x] Can limit search to specific folder or search all folders
- [x] Proper error handling for invalid folder paths
- [x] Integration: Leverages EmailReader service for email retrieval

## Implementation Approach

### TDD Sequence
1. **Test**: EmailSearcher constructor takes adapter parameter
2. **Test**: search_by_sender("manager@company.com") returns 1 email from MockAdapter
3. **Test**: search_by_subject("Project") returns 2 emails (case-insensitive partial)
4. **Test**: search_by_sender with display name ("Alice Manager") works
5. **Test**: search_emails() with multiple criteria applies AND logic  
6. **Test**: folder_path parameter limits search to specific folder
7. **Test**: folder_path=None searches all folders via EmailReader
8. **Test**: Case-insensitive matching for all string criteria
9. **Test**: Empty results return [] (not error)
10. **Test**: Invalid folder_path raises ValueError from adapter
11. **Test**: Integration with MockOutlookAdapter end-to-end functionality

### Service Interface Design
```python
class EmailSearcher:
    def __init__(self, adapter: OutlookAdapter)
    def search_by_sender(self, sender: str, folder_path: str = None) -> List[Email]
    def search_by_subject(self, subject: str, folder_path: str = None) -> List[Email]
    def search_emails(self, sender: str = None, subject: str = None, folder_path: str = None) -> List[Email]
```

### Integration Points
- EmailReader: Use existing service for email retrieval (avoid duplication)
- OutlookAdapter: Leverage get_emails() through EmailReader
- Email model: Filter on subject, sender_email, sender_name fields
- Error handling: Consistent with EmailReader ValueError patterns

### Search Logic Strategy
- **Client-side filtering**: No new adapter methods needed
- **Case-insensitive**: Use .lower() for all string comparisons
- **Partial subject matching**: "Project" matches "Project Update Required"
- **Sender flexibility**: Match both email address and display name
- **Folder scoping**: If folder_path specified, search only that folder

## Evidence for Completion
- All tests passing: `uv run pytest tests/services/test_email_searcher.py`
- EmailSearcher works with MockOutlookAdapter
- Can search by sender: `searcher.search_by_sender("manager@company.com")` returns 1 email
- Can search by subject: `searcher.search_by_subject("Project")` returns 2 emails
- Combined search: `searcher.search_emails(sender="pm@company.com", subject="Project")` returns 1 email
- Folder-specific search: `searcher.search_by_sender("user@company.com", "Sent Items")` returns 2 emails
- Error handling: ValueError for invalid folder paths matches EmailReader behavior
- Service follows dependency injection pattern for future CLI integration

## Test Cases Based on MockAdapter Data

### Sender Search Validation
```python
# Email address search (case-insensitive)
results = searcher.search_by_sender("manager@company.com")
assert len(results) == 1
assert results[0].subject == "Weekly Team Meeting"

# Display name search
results = searcher.search_by_sender("Alice Manager") 
assert len(results) == 1

# Folder-specific sender search
results = searcher.search_by_sender("user@company.com", "Sent Items")
assert len(results) == 2
```

### Subject Search Validation
```python
# Partial match (case-insensitive)
results = searcher.search_by_subject("Project")
assert len(results) == 2  # "Project Update Required" + "Re: Project Update Required"

# Exact subject match
results = searcher.search_by_subject("Weekly Team Meeting")
assert len(results) == 1
```

### Combined Search Validation
```python
# Multiple criteria (AND logic)
results = searcher.search_emails(sender="pm@company.com", subject="Project")
assert len(results) == 1
assert results[0].subject == "Project Update Required"
```

## Validation Results

### What Works
- EmailSearcher service integrates cleanly with OutlookAdapter interface
- Dependency injection pattern works correctly with EmailReader reuse
- All search methods handle case-insensitive matching properly
- Folder scoping limits search to specific folders correctly
- Combined search criteria apply AND logic as expected
- Error handling propagates adapter errors properly
- Empty results handled correctly (return empty lists)
- Ready for future CLI command integration

### Evidence
- **Test suite**: 59/59 tests pass with 12 new EmailSearcher tests, no regressions
- **Import test**: `from outlook_cli.services import EmailSearcher` ✅
- **Sender search**: `searcher.search_by_sender("manager@company.com")` returns 1 email ✅
- **Subject search**: `searcher.search_by_subject("Project")` returns 2 emails ✅
- **Combined search**: `searcher.search_emails(sender="pm@company.com", subject="Project")` returns 1 email ✅
- **Folder-specific**: `searcher.search_by_sender("user@company.com", "Sent Items")` returns 2 emails ✅
- **Error handling**: `ValueError: Folder 'NonExistentFolder' not found` ✅
- **Integration scenarios**: All search methods work with MockOutlookAdapter

### Manual Verification Commands
```python
# Import and basic usage
from outlook_cli.services import EmailSearcher
from outlook_cli.adapters.mock_adapter import MockOutlookAdapter

adapter = MockOutlookAdapter()
searcher = EmailSearcher(adapter)

# Search by sender email
results = searcher.search_by_sender("manager@company.com")  # Returns 1 email

# Search by subject (partial, case-insensitive)  
results = searcher.search_by_subject("Project")  # Returns 2 emails

# Combined search with AND logic
results = searcher.search_emails(sender="pm@company.com", subject="Project")  # Returns 1 email

# Folder-specific search
results = searcher.search_by_sender("user@company.com", "Sent Items")  # Returns 2 emails
```

### Issues Fixed
None - integration worked perfectly on first validation.

### Ready for Commit
✅ All integration points validated
✅ EmailSearcher foundation established for CLI commands
✅ Service layer complete for search functionality
✅ Ready for milestone 006 (EmailMover service)

## Notes
- Leverages EmailReader to avoid duplicating email retrieval logic
- Client-side filtering enables rich search without adapter complexity
- Foundation for CLI `find --sender/--subject/--folder` command (milestone 010)
- No pagination logic yet - that's milestone 007
- Search criteria prepared for future extensions (date ranges, importance, etc.)