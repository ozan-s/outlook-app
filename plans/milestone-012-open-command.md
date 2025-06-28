# Milestone 012: Open Command Implementation

## Objective
Implement `open [email_id]` command to display full email content with complete headers and body text

## Current State Analysis
- ✅ **Dependencies met**: CLI framework working, EmailReader service exists, MockOutlookAdapter operational
- ✅ **Patterns established**: Three-layer integration pattern (service → CLI → display) proven across read/find/move commands
- ✅ **Email model complete**: Email.body_text field contains full content, all headers available
- ❌ **Missing infrastructure**: No `get_email_by_id()` method in adapter interface or service layer
- ❌ **CLI usability gap**: Current commands show sequential numbers (1,2,3) but users need email IDs ("inbox-001") for open command

**Existing Email ID System:**
- Format: `"inbox-001"`, `"sent-002"`, `"draft-001"` 
- MockOutlookAdapter has email ID search pattern in `move_email()` method
- CLI stub already exists: `open_parser.add_argument('email_id', help='ID of the email to open')`

## Success Criteria
- [x] User can run `open inbox-001` to display full email content
- [x] Complete email headers displayed (From, To, CC, BCC, Date, Subject, Importance)
- [x] Email body text displayed with clear content separator
- [x] Email ID not found returns helpful error message
- [x] Integration: Works with existing MockOutlookAdapter email data

## Implementation Approach

### TDD Sequence
1. **Test**: Add `get_email_by_id()` to OutlookAdapter interface → method signature exists
2. **Test**: MockOutlookAdapter.get_email_by_id("inbox-001") → returns Email object
3. **Test**: MockOutlookAdapter.get_email_by_id("invalid-id") → raises ValueError
4. **Test**: EmailReader.get_email_by_id() service method → calls adapter correctly  
5. **Test**: CLI `open inbox-001` → displays full email content
6. **Test**: CLI `open invalid-id` → shows "Email 'invalid-id' not found"

### Integration Points
- **Adapter Interface**: Add `get_email_by_id(email_id: str) -> Email` to abstract base
- **MockOutlookAdapter**: Implement email ID search across all folders
- **EmailReader Service**: Add `get_email_by_id()` method calling adapter
- **CLI Handler**: Implement `handle_open()` following established three-layer pattern

### Implementation Files
- `src/outlook_cli/adapters/outlook_adapter.py` - Add abstract method
- `src/outlook_cli/adapters/mock_outlook_adapter.py` - Implement email retrieval
- `src/outlook_cli/services/email_reader.py` - Add service method
- `src/outlook_cli/cli.py` - Replace stub with full implementation
- `tests/` - Unit and integration tests following established patterns

### Evidence for Completion
- All tests passing (unit + integration)
- Manual verification:
  ```bash
  uv run outlook-cli open inbox-001
  # Shows complete email with headers + body
  
  uv run outlook-cli open invalid-123  
  # Shows "Error: Email 'invalid-123' not found"
  ```
- Full email content displayed with professional formatting
- Error handling consistent with other CLI commands

## Notes
- **Pattern Consistency**: Follow exact three-layer pattern from read/find/move commands
- **Error Handling**: Service ValueError → CLI user-friendly message (established pattern)
- **Display Format**: Professional email view with clear content separation
- **No pagination needed**: Single email display, no Paginator required
- **Scope boundary**: Display only - no email modification or response functionality

## Final Status: COMPLETE ✅

### Delivered
- OutlookAdapter.get_email_by_id() abstract interface method
- MockOutlookAdapter.get_email_by_id() implementation with cross-folder search
- EmailReader.get_email_by_id() service layer method
- handle_open() CLI command with three-layer integration pattern
- _display_full_email() professional formatting helper
- 15 new tests (5 unit + 5 integration + 5 end-to-end)
- All 133 tests passing with zero regressions

### Manual Validation Completed
```bash
uv run outlook-cli open inbox-001    # ✅ Shows complete email content
uv run outlook-cli open sent-002     # ✅ Works with attachments/CC fields  
uv run outlook-cli open draft-001    # ✅ Works across all folder types
uv run outlook-cli open invalid-123  # ✅ Shows user-friendly error
```

### Master Plan Updated
- Marked Milestone 012 complete ✅ 2024-06-28
- Reduced Milestone 015 scope (CLI polish essentially complete)
- No new milestones needed (implementation went exactly as planned)
- Phase 3 CLI Layer fully complete - all 4 commands working

### Git Commit
- Hash: [to be added in commit step]
- Message: "feat: complete milestone-012-open-command-implementation"

### Handover Notes
Open command fully working with professional email display formatting. **Phase 3 CLI Layer now 100% complete** - all planned commands (read, find, move, open) implemented and tested. Next session can either:

1. **Option A**: Start Milestone 013 (Windows pywin32 adapter) - requires Windows environment
2. **Option B**: Start Milestone 016 (Integration testing + documentation) - can be done on any platform
3. **Option C**: Skip to final project wrap-up

**Recommendation**: Milestone 016 (documentation) since CLI functionality is complete and proven.

**No blockers**: All CLI patterns established, comprehensive test coverage, zero technical debt.