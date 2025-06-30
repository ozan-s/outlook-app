# Milestone 011: Enhanced Read Command with Filtering Support

## Objective
Add comprehensive filtering capabilities to read command using existing service layer (sorting already complete from Milestone 007).

## Current State Analysis
- **Dependency check**: ✅ EmailSearcher.search_emails() fully implemented with all filter types
- **Sorting integration**: ✅ EmailSortingService complete, read command already supports --sort-by/--sort-order
- **Filter patterns**: ✅ All filter arguments established in find command parser
- **Display logic**: ✅ Shared _display_email_page() function working

**Current read command limitations**:
- Uses EmailReader.get_emails_from_folder() - no filtering beyond sorting
- Missing filter arguments: --since, --until, --is-read/--is-unread, --has-attachment/--no-attachment, --importance, --not-sender, --not-subject
- Single folder only (vs find command's multi-folder --folders support)

**Existing pattern (from find command)**:
```python
results = searcher.search_emails(
    sender=args.sender, subject=args.subject, folder_path=args.folder,
    since=since_date, until=until_date, is_read=args.is_read, is_unread=args.is_unread,
    has_attachment=args.has_attachment, no_attachment=args.no_attachment,
    importance=args.importance, not_sender=args.not_sender, not_subject=args.not_subject
)
```

## Success Criteria
- [x] Read command supports all filter arguments from find command
- [x] Read command uses EmailSearcher instead of EmailReader for filtering
- [x] All filter combinations work correctly with read command
- [x] Sorting integration preserved and working with filters
- [x] Consistent behavior with find command (except no search criteria requirement)
- [x] Existing folder reading functionality maintained

## Implementation Approach

### TDD Sequence
1. **Test**: Read with --since filter → emails from last 7 days only
2. **Test**: Read with --is-unread filter → unread emails only  
3. **Test**: Read with --has-attachment filter → emails with attachments only
4. **Test**: Read with combined filters → --since + --is-unread working together
5. **Test**: Read with sorting + filtering → filters + sort-by working together

### Integration Points
- **CLI Parser**: Add filter arguments to read_parser (copy from find_parser)
- **Command Handler**: Update handle_read() to use EmailSearcher.search_emails()
- **Date Processing**: Use same parse_relative_date() and validate_date_range() logic
- **Display**: Continue using shared _display_email_page() function

### Implementation Steps
1. **Add filter arguments**: Copy all filter args from find_parser to read_parser
2. **Update handle_read()**: Replace EmailReader with EmailSearcher approach
3. **Date parsing**: Add same date processing logic as handle_find()
4. **Filter integration**: Use EmailSearcher.search_emails() with filter parameters
5. **Preserve sorting**: Maintain existing EmailSortingService integration

### Evidence for Completion
- All tests passing with TDD sequence
- Manual validation commands:
  ```bash
  # Basic filtering
  uv run python -m outlook_cli.cli read --folder Inbox --since 7d
  uv run python -m outlook_cli.cli read --folder Inbox --is-unread
  
  # Combined filters
  uv run python -m outlook_cli.cli read --folder Inbox --since 7d --is-unread --has-attachment
  
  # Filters + sorting
  uv run python -m outlook_cli.cli read --folder Inbox --is-unread --sort-by received_date --sort-order asc
  ```
- Read command help shows all filter options
- Filter behavior identical to find command (except no search criteria requirement)

## Notes
- No search criteria validation needed (unlike find command)
- Preserve existing --folder default behavior (single folder vs find's multi-folder --folders)
- Maintain backward compatibility - existing read functionality unchanged
- Reuse all existing filter logic from EmailSearcher service
- Integration time reduced due to sorting already complete from Milestone 007