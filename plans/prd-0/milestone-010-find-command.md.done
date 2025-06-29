# Milestone 010: Find Command Implementation

## Objective
Implement `find --sender/--subject/--folder` command with EmailSearcher integration for comprehensive email searching functionality.

## Current State Analysis
- ✅ **Dependency Check**: EmailSearcher service fully implemented and tested
- ✅ **CLI Framework**: Arguments parsed (`--sender`, `--subject`, `--folder`) with placeholder handler
- ✅ **Service Methods Available**:
  - `search_emails(sender, subject, folder_path)` - combined criteria search
  - `search_by_sender(sender, folder_path)` - sender-only search  
  - `search_by_subject(subject, folder_path)` - subject-only search
- ✅ **Pagination Pattern**: Established in read command with 10-item pages
- ✅ **Error Handling**: Service→CLI conversion pattern from read command
- ✅ **Mock Data**: Rich test scenarios available in MockOutlookAdapter

### CLI Arguments Already Defined
```bash
outlook-cli find --sender user@email.com          # Search by sender
outlook-cli find --subject "meeting"              # Search by subject
outlook-cli find --folder "Sent Items"            # Search specific folder
outlook-cli find --sender bob --subject project   # Combined criteria
```

### Integration Points Identified
- **EmailSearcher**: Use `search_emails()` method for unified search logic
- **Paginator**: Wrap results for consistent CLI display
- **CLI Framework**: Replace `handle_find()` placeholder in `/src/outlook_cli/cli.py`
- **MockOutlookAdapter**: Enables full testing without Windows dependency

## Success Criteria
- [x] Find command works with single criteria (sender OR subject)
- [x] Find command works with combined criteria (sender AND subject)  
- [x] Folder scoping works (default Inbox, configurable with --folder)
- [x] Empty search results handled gracefully
- [x] Invalid folder names show user-friendly error
- [x] Pagination displays consistently with read command
- [x] Search criteria summary shown in output

## Implementation Approach

### TDD Sequence
1. **Test**: Find by sender only → displays filtered emails with pagination
2. **Test**: Find by subject only → displays filtered emails with pagination  
3. **Test**: Find with combined sender + subject → displays AND-filtered results
4. **Test**: Find in specific folder → scopes search correctly
5. **Test**: Find with no results → shows "No emails found" message
6. **Test**: Find with invalid folder → shows "Folder 'X' not found" error
7. **Test**: Find with no criteria → shows helpful usage message

### Implementation Strategy
Replace placeholder `handle_find(args)` function with:
```python
def handle_find(args):
    try:
        # Validate at least one search criteria provided
        if not args.sender and not args.subject:
            print("Error: Please specify --sender and/or --subject to search")
            return
            
        # Initialize EmailSearcher with adapter
        adapter = MockOutlookAdapter()
        searcher = EmailSearcher(adapter)
        
        # Perform search with provided criteria
        results = searcher.search_emails(
            sender=args.sender,
            subject=args.subject, 
            folder_path=args.folder
        )
        
        # Display search summary
        criteria = []
        if args.sender:
            criteria.append(f"sender '{args.sender}'")
        if args.subject:
            criteria.append(f"subject '{args.subject}'")
        print(f"Searching for emails with {' and '.join(criteria)} in folder '{args.folder}':")
        print()
        
        # Handle empty results
        if not results:
            print("No emails found matching your criteria.")
            return
            
        # Paginate and display results
        paginator = Paginator(results, page_size=10)
        current_page = paginator.get_current_page()
        
        # Display pagination info and emails
        display_email_page(paginator, current_page)
        
    except ValueError as e:
        print(f"Error: Folder '{args.folder}' not found")
    except Exception as e:
        print(f"Error searching emails: {str(e)}")
```

### Integration Points
- **Database**: EmailSearcher → EmailReader → MockOutlookAdapter
- **Search Logic**: Case-insensitive partial matching (existing)
- **Pagination**: Identical pattern to read command  
- **Display**: Same email format with status, sender, subject, date

### Evidence for Completion
- All tests passing (unit + integration)
- **Manual Verification Commands**:
  ```bash
  # Single criteria searches
  uv run outlook-cli find --sender manager
  uv run outlook-cli find --subject "project"
  
  # Combined criteria search  
  uv run outlook-cli find --sender bob --subject update
  
  # Folder scoping
  uv run outlook-cli find --sender user --folder "Sent Items"
  
  # Error cases
  uv run outlook-cli find --folder "NonExistent"
  uv run outlook-cli find  # No criteria
  ```
- **Expected Outputs**:
  - Search results with pagination info
  - Clear search criteria summary
  - Proper error messages for edge cases
  - Identical email display format as read command

## Test Implementation Plan

### Unit Tests (extend existing CLI test class)
```python
def test_find_command_parsing():
    # Test argument parsing for all find scenarios

def test_find_command_help():
    # Test help text displays correctly
```

### Integration Tests (new test class)
```python
class TestFindCommandIntegration:
    def test_find_by_sender_only(self):
        # Test --sender with expected email matches
        
    def test_find_by_subject_only(self):
        # Test --subject with expected email matches
        
    def test_find_combined_criteria(self):
        # Test --sender AND --subject together
        
    def test_find_with_folder_scoping(self):
        # Test --folder parameter changes search scope
        
    def test_find_no_results(self):
        # Test search with no matching emails
        
    def test_find_invalid_folder(self):
        # Test ValueError handling for bad folder
        
    def test_find_no_criteria_error(self):
        # Test error when no search criteria provided
```

## Notes
- **Reuse Patterns**: Follow exact implementation pattern from read command
- **Search Logic**: EmailSearcher handles all complexity, CLI just orchestrates
- **User Experience**: Clear search criteria display, helpful error messages
- **Performance**: Client-side filtering through EmailSearcher is sufficient for this milestone
- **Future**: Search functionality ready for real Outlook integration in Milestone 013

## Files Modified
- `/src/outlook_cli/cli.py` - Replace `handle_find()` placeholder
- `/tests/test_cli.py` - Add integration test class

## Final Status: COMPLETE ✅

### Delivered
- Working find command with EmailSearcher integration
- Comprehensive integration tests (7 new test cases)
- Consistent pagination and email display formatting
- Robust error handling for all edge cases
- Code reuse through `_display_email_page()` helper function

### Master Plan Updated
- Marked Milestone 010 complete ✅ 2024-06-28
- Reduced Milestone 015 scope (output formatting largely complete)
- Confirmed CLI integration patterns for remaining commands

### Lessons Learned
- Service → CLI → Display pattern works flawlessly for complex search functionality
- TDD with comprehensive integration tests catches all edge cases efficiently
- Code reuse through helper functions eliminates duplication while maintaining consistency
- User experience benefits from clear search criteria summaries and helpful error messages

### Handover Notes
Find command fully working with all planned functionality. Next session can:
1. Start Milestone 011: Move command implementation
2. Follow identical service integration patterns
3. Reuse `_display_email_page()` for consistent output
4. No blockers - all patterns established and validated