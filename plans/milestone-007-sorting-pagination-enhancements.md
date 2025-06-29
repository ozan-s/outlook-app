# Milestone 007: Sorting and Pagination Service Enhancements

## Objective
Add sorting by multiple fields and pagination control to services for email display commands.

## Current State Analysis
- **Dependencies Check**: ✅ Milestone 006 filtering service completed and working
- **CLI Parser**: Sort flags already defined (`--sort-by`, `--sort-order`) in cli.py:220-222
- **Email Model Fields**: received_date, subject, sender_email, sender_name, importance, is_read, has_attachments
- **Pagination Service**: Basic paginator exists and is used in handle_read() and handle_find()
- **Integration Gap**: CLI flags exist but no sorting logic implemented in services

## Success Criteria
- [x] Sort by received_date, subject, sender, importance works correctly
- [x] Both ascending ('asc') and descending ('desc') order work
- [x] Sorting integrates with existing pagination (sort BEFORE paginate)
- [x] `find` command honors --sort-by and --sort-order flags
- [x] `read` command gains sorting capability with same flags
- [x] Sorting works with all existing filters from Milestone 006

## Implementation Approach

### TDD Sequence ✅ COMPLETED
1. **Test**: EmailSortingService sorts by received_date descending (default) ✅
2. **Test**: EmailSortingService sorts by subject ascending ✅
3. **Test**: EmailSortingService sorts by sender ascending ✅
4. **Test**: EmailSortingService sorts by importance (High→Normal→Low) ✅
5. **Test**: CLI integration - find with --sort-by received_date --sort-order asc ✅
6. **Test**: CLI integration - read command gains sorting flags ✅
7. **Test**: Sorting + filtering + pagination integration works together ✅

### Integration Points
- **EmailSortingService**: New service class for sorting email lists
- **CLI**: Connect existing sort flags to sorting service in handle_find() and handle_read()
- **Pagination**: Apply sorting before pagination in both command handlers
- **EmailSearcher**: Add sorting parameter to search_emails() method

### Architecture Pattern
```python
# Service Layer Enhancement
class EmailSortingService:
    def sort_emails(emails: List[Email], sort_by: str, sort_order: str) -> List[Email]

# CLI Integration Pattern (existing pattern from CLAUDE.md)
def handle_find(args):
    # ... existing search logic ...
    if args.sort_by:
        sorter = EmailSortingService()
        results = sorter.sort_emails(results, args.sort_by, args.sort_order)
    # ... existing pagination logic ...
```

### Evidence for Completion
- All tests passing
- **curl equivalent**: `python -m outlook_cli find --keyword meeting --sort-by subject --sort-order asc`
- **Expected output**: Emails sorted alphabetically by subject, ascending
- **Manual verification**: Compare first/last email subjects to confirm sort order
- **Integration proof**: Sorting + filtering + pagination all work together

## Notes
- Follow Service-to-CLI Integration Pattern from CLAUDE.md
- Sort logic must handle None/empty values gracefully  
- Default sort remains received_date descending for backward compatibility
- Add sorting flags to read command for consistency
- Sorting happens BEFORE pagination for correct page boundaries

## Final Status: COMPLETE ✅

### Delivered
- EmailSortingService with support for received_date, subject, sender, importance sorting
- CLI integration for both `find` and `read` commands with --sort-by and --sort-order flags
- Comprehensive test coverage: 8 tests (4 unit, 2 functional, 2 integration)
- Full integration: sorting + filtering + pagination work together seamlessly

### Master Plan Updated
- Marked Milestone 007 complete ✅ 2025-06-29
- Reduced Milestone 011 scope and time estimate (sorting already integrated)
- Documented Service-to-CLI Integration Pattern effectiveness for sorting features

### Evidence Validated
- Manual CLI testing: `OUTLOOK_ADAPTER=mock uv run outlook-cli find --keyword meeting --sort-by subject --sort-order asc`
- Performance confirmed: All sorting operations maintain sub-second performance
- Integration proven: Works with existing filtering from Milestone 006 and pagination

### Handover Notes
Sorting system fully working with both commands. Next session can:
1. Proceed with Milestone 010: Windows Testing Checkpoint #2 to validate complete filtering+sorting system
2. Or continue with Milestone 011: Enhanced read command with filtering (reduced scope)
3. Sorting infrastructure established and tested - no blockers