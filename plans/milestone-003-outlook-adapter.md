# Milestone 003: Outlook Adapter Interface + Mocks

## Objective
Create abstract OutlookAdapter interface + MockOutlookAdapter for testing to enable dependency injection and cross-platform development.

## Current State Analysis
- Dependency check: ✅ Email and Folder models complete with Pydantic validation
- Email model fields: id, subject, sender_email, sender_name, recipient_emails, cc_emails, bcc_emails, received_date, body_text, body_html, has_attachments, attachment_count, folder_path, is_read, importance
- Folder model fields: path, name, email_count, unread_count
- Existing pattern: Pydantic models with validation, src/outlook_cli package structure
- No adapter code exists yet - clean slate for interface design

## Success Criteria
- [x] OutlookAdapter abstract interface defines all needed operations
- [x] MockOutlookAdapter implements interface with test data
- [x] Can list folders, get emails from folder, get folder info
- [x] Interface supports all operations needed for future services
- [x] Dependency injection pattern works (adapter passed to services)

## Implementation Approach

### TDD Sequence
1. **Test**: Can create MockOutlookAdapter instance
2. **Test**: MockOutlookAdapter.get_folders() returns List[Folder]
3. **Test**: MockOutlookAdapter.get_emails(folder_path) returns List[Email]
4. **Test**: MockOutlookAdapter.get_folder_info(path) returns Folder
5. **Test**: MockOutlookAdapter supports move operations for future
6. **Test**: Interface prevents direct instantiation (ABC pattern)

### Integration Points
- Models: Uses Email and Folder from existing models package
- Architecture: Abstract base class with concrete mock implementation
- Future: Interface ready for PyWin32Adapter in milestone 013

### File Structure
```
src/outlook_cli/
├── adapters/
│   ├── __init__.py
│   ├── outlook_adapter.py    # Abstract interface
│   └── mock_adapter.py       # Mock implementation
```

### Interface Design
```python
# OutlookAdapter methods needed:
- get_folders() -> List[Folder]
- get_folder_info(folder_path: str) -> Folder
- get_emails(folder_path: str) -> List[Email]
- move_email(email_id: str, target_folder: str) -> bool
```

### Mock Data Strategy
- 3-4 test folders (Inbox, Sent Items, Draft, Custom/Subfolder)
- 10-15 test emails across folders
- Realistic data using Faker patterns from milestone 002
- Support pagination (returns all emails, services will paginate)

## Evidence for Completion
- All tests passing: `uv run pytest tests/adapters/`
- Mock adapter provides realistic test data
- Interface complete for all planned CLI operations
- Can instantiate mock adapter and call all methods
- Clear separation: interface in one file, implementation in another

## Notes
- Abstract base class pattern ensures interface contract
- Mock adapter enables Mac development without Windows Outlook
- Interface designed for future PyWin32Adapter integration
- Test data realistic enough for full CLI testing in later milestones