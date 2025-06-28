# Milestone 011: Move Command Implementation

## Objective
Implement `move [email_id] [target_folder]` CLI command with EmailMover service integration

## Current State Analysis
- Dependency check: ✅ EmailMover service complete and tested
- CLI framework: ✅ Command parser setup with email_id/target_folder arguments  
- Integration patterns: ✅ Three-layer pattern established (read/find commands)
- MockOutlookAdapter: ✅ Test data includes valid email IDs and folders

## Success Criteria
- [x] User can move emails: `outlook-cli move inbox-001 Drafts`
- [x] Invalid email ID returns user-friendly error
- [x] Invalid folder returns user-friendly error  
- [x] Success message confirms move operation
- [x] Integration: Follows established CLI service pattern

## Implementation Approach

### TDD Sequence
1. **Test**: Move valid email to valid folder → success message
2. **Test**: Move nonexistent email → "Email 'xyz' not found" error
3. **Test**: Move to nonexistent folder → "Target folder 'xyz' not found" error
4. **Test**: CLI argument parsing works correctly

### Integration Points
- Service: EmailMover.move_email_to_folder(email_id, target_folder)
- Adapter: MockOutlookAdapter (established pattern)
- CLI: Replace stub at src/outlook_cli/cli.py:154

### Evidence for Completion
- All tests passing
- Manual commands work:
  ```bash
  outlook-cli move inbox-001 Drafts
  outlook-cli move sent-001 "Custom/Archive"  
  outlook-cli move nonexistent Drafts    # Shows error
  outlook-cli move inbox-001 BadFolder   # Shows error
  ```
- Consistent error handling with read/find commands

## Implementation Details

### EmailMover Service Interface
```python
# Service already complete with these methods:
mover.move_email_to_folder(email_id: str, target_folder: str) -> bool
# Raises ValueError for invalid email_id or target_folder
```

### Available Test Data
- **Valid Email IDs**: inbox-001, inbox-002, inbox-003, sent-001, sent-002
- **Valid Folders**: Inbox, Sent Items, Drafts, Deleted Items, Custom/Projects, Custom/Archive

### CLI Implementation Pattern
Replace current stub with three-layer pattern:
1. Initialize EmailMover with MockOutlookAdapter
2. Call move_email_to_folder() with CLI arguments
3. Convert results/exceptions to user-friendly output

## Notes
- EmailMover service fully tested and working
- CLI framework already parses arguments correctly
- Error handling follows established ValueError → friendly message pattern
- No new dependencies required - purely CLI integration milestone