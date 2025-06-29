# Milestone 001: Enhanced CLI Argument Parser with New Filter Flags

## Objective
Add all new command-line flags to argparse configuration for advanced filtering, sorting, and folder operations.

## Current State Analysis
- **CLI Structure**: argparse with subcommands (`read`, `find`, `move`, `open`)
- **Existing Flags**: `--folder`, `--keyword`, `--sender`, `--subject`, `--adapter`
- **Email Model Fields**: `received_date`, `is_read`, `has_attachments`, `attachment_count`, `importance`, `sender_email`, `subject`, `folder_path` 
- **Adapter Interface**: `get_folders()` method already exists for folder enumeration
- **Pattern**: Service-to-CLI integration with consistent error handling

## Success Criteria
- [x] All new flags parse correctly without breaking existing functionality
- [x] New `folders` command added with proper help text
- [x] Help text displays properly for all new flags
- [x] Argument validation works for all flag combinations
- [x] Backward compatibility maintained with existing commands

## Implementation Approach

### TDD Sequence
1. **Test**: Parse `--since` flag with various date formats → accepts input
2. **Test**: Parse `--until` flag with date validation → accepts input  
3. **Test**: Parse `--is-read` and `--is-unread` flags → mutually exclusive flags work
4. **Test**: Parse `--has-attachment` and `--no-attachment` flags → mutually exclusive flags work
5. **Test**: Parse `--attachment-type` flag → accepts file extensions
6. **Test**: Parse `--importance` flag → accepts high/normal/low values
7. **Test**: Parse `--folders` flag → accepts multiple folder names
8. **Test**: Parse `--not-sender` and `--not-subject` flags → exclusion filters work
9. **Test**: Parse `--limit` and `--all` flags → result control works
10. **Test**: Parse `--sort-by` and `--sort-order` flags → sorting options work
11. **Test**: New `folders` command with `--tree` flag → folder command works
12. **Test**: Backward compatibility → existing commands still work

### New Flags to Add

**Date Filters:**
- `--since`: Start date (YYYY-MM-DD, relative: 7d, 2w, yesterday)
- `--until`: End date (same formats as --since)

**Read Status Filters:**
- `--is-unread`: Show only unread emails
- `--is-read`: Show only read emails

**Attachment Filters:**
- `--has-attachment`: Show only emails with attachments
- `--no-attachment`: Show only emails without attachments  
- `--attachment-type`: Filter by file extension (pdf, doc, jpg, etc.)

**Content Filters:**
- `--importance`: Filter by importance (high, normal, low)
- `--folders`: Search multiple folders (replaces single --folder)
- `--not-sender`: Exclude emails from specific sender
- `--not-subject`: Exclude emails with subject keywords

**Result Control:**
- `--limit`: Number of results per page (default: 10)
- `--all`: Return all results, no paging

**Sorting:**
- `--sort-by`: Field to sort by (received_date, subject, sender, importance)
- `--sort-order`: Sort direction (desc [default], asc)

**New Command:**
- `folders`: List all available folders
  - `--tree`: Display folders in tree format (default: flat)

### Integration Points
- **Argument Parsing**: Extend existing argparse configuration in `main()` function
- **Command Routing**: Add `folders` command to existing router in `main()`
- **Help System**: Update help text and examples for all commands
- **Error Validation**: Basic argument validation within argparse

### Evidence for Completion
- All tests passing for argument parsing
- Help command shows all new flags: `ocli --help`, `ocli find --help`, `ocli folders --help`
- Manual verification: `ocli find --since 2025-06-01 --is-unread --has-attachment` parses without error
- Manual verification: `ocli folders --tree` parses without error
- Existing commands work: `ocli read --folder Inbox`, `ocli find --keyword test`

## Final Status: COMPLETE ✅

### Delivered
- 16 new CLI flags implemented with proper validation
- New `folders` command with `--tree` flag
- Mutually exclusive groups handling conflicts automatically
- Comprehensive test suite (13 tests) with 100% pass rate
- Backward compatibility maintained for all existing commands

### Implementation Highlights
- Used argparse mutually exclusive groups for flag conflict handling
- Implemented basic `folders` command functionality alongside parser
- Added tree view formatting for folders (simple implementation)
- TDD approach with RED → GREEN → REFACTOR discipline

### Master Plan Updated
- Marked Milestone 001 complete
- Removed Milestone 002 (flag conflicts handled in 001)
- Removed Milestone 008 (folders command completed in 001)  
- Removed Milestone 012 (tree view completed in 001)
- Added adaptation log explaining scope changes

### Evidence of Completion
- All new flags parse correctly: `ocli find --help` shows all 16 new options
- Complex multi-flag commands work: `ocli find --keyword test --since 2025-06-01 --is-unread --has-attachment --sort-by received_date`
- Folders command functional: `ocli folders` and `ocli folders --tree` both work
- Backward compatibility: `ocli read --folder Inbox` still works exactly as before
- Test suite: 13 new tests + 36 existing tests all passing

### Notes
- Flags are parsed and stored in args object but not yet used for filtering (next milestone)
- Date parsing logic still needed for relative dates (Milestone 003)
- Service layer integration happens in Phase 2 milestones