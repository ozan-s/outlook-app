# Milestone 007: Pagination Logic + Navigation

## Objective
Implement Paginator class for 10-item batches with next/prev navigation.

## Current State Analysis
- Dependency check: ✅ Email models complete with full field set
- EmailReader service: Returns List[Email] from folders
- EmailSearcher service: Returns filtered List[Email] results  
- EmailMover service: Works with email lists
- Existing pattern: Services return full lists, need pagination wrapper

## Success Criteria
- [x] Paginator class handles any List[Email] input
- [x] Fixed page size of 10 emails per page
- [x] Navigation: next_page(), prev_page(), get_current_page()
- [x] Boundary handling: first/last page edge cases
- [x] Integration: Works with EmailReader and EmailSearcher results

## Progress
- [x] Created test file `tests/services/test_paginator.py`
- [x] Implemented all failing tests for TDD cycle
- [x] Implemented `src/outlook_cli/services/paginator.py` 
- [x] All unit tests passing (8/8)
- [x] Integration tests with EmailReader and EmailSearcher passing (2/2)
- [x] Updated `services/__init__.py` to export Paginator
- [x] Full test suite passing (78/78) - no regressions
- [x] Paginator ready for CLI integration in milestone 008

## Implementation Approach

### TDD Sequence
1. **Test**: Create paginator with 25 emails → 3 pages, page 1 active
2. **Test**: get_current_page() returns first 10 emails
3. **Test**: next_page() moves to page 2, returns emails 11-20
4. **Test**: prev_page() from page 2 returns to page 1
5. **Test**: next_page() from last page does nothing
6. **Test**: prev_page() from first page does nothing
7. **Test**: Empty list handling
8. **Test**: List with <= 10 items (single page)

### Integration Points
- Input: List[Email] from EmailReader.get_emails_from_folder()
- Input: List[Email] from EmailSearcher.search_emails()
- Navigation: User commands for next/previous
- Output: List[Email] batches of 10 or fewer

### Evidence for Completion
- All tests passing
- Integration test: EmailReader → Paginator → 10-item pages
- Integration test: EmailSearcher → Paginator → filtered pages
- Edge cases: empty results, single page, boundary navigation
- Clean API: paginator.get_current_page(), paginator.next_page(), etc.

## Implementation Details

### Paginator Class Structure
```python
class Paginator:
    def __init__(self, items: List[Email], page_size: int = 10)
    def get_current_page() -> List[Email]
    def next_page() -> bool  # Returns True if moved, False if at end
    def prev_page() -> bool  # Returns True if moved, False at start
    def get_page_info() -> dict  # Current page, total pages, total items
```

### File Location
- Create: `src/outlook_cli/services/paginator.py`
- Update: `src/outlook_cli/services/__init__.py` to export Paginator
- Tests: `tests/services/test_paginator.py`

## Notes
- Page size hardcoded to 10 per PRD requirements
- Paginator is stateful (tracks current page)
- Works with any List[Email], not tied to specific service
- Ready for CLI integration in milestone 008