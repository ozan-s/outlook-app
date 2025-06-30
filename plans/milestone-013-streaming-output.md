# Milestone 013: Streaming Output for Large Result Sets

## Objective
Implement streaming display for `--all` flag with large result sets to prevent memory crashes and improve user experience.

## Current State Analysis
- **Critical Gap Identified**: `--all` flag exists in CLI parser but is completely ignored in `handle_find()` 
- **Infrastructure Available**: ResourceMonitor, PerformanceMonitor, AuditLogger, ProgressiveFilterOptimizer
- **Display Pattern**: `_display_email_page()` function ready for extension to streaming display
- **Memory Management**: ResourceMonitor tracks memory usage with configurable limits (default 1024MB)
- **Result Limits**: Current max_result_count limit is 50,000 emails (configurable via OUTLOOK_CLI_MAX_RESULT_COUNT)

## Success Criteria ✅ ALL COMPLETE
- [x] `--all` flag activates streaming output instead of pagination
- [x] Warning shown for result sets >1000 emails before streaming begins
- [x] Memory usage stays within ResourceMonitor limits during streaming
- [x] Each "chunk" displays immediately without waiting for complete results
- [x] Backward compatibility: `--limit` flag continues using existing pagination

## Implementation Approach

### TDD Sequence
1. **Test**: `--all` flag with small result set (50 emails) → streams all results  
2. **Test**: `--all` flag with >1000 results → shows warning then streams
3. **Test**: `--all` flag respects memory limits → stops with ResourceExceededError if needed
4. **Test**: Streaming display shows results incrementally (not all at once)
5. **Test**: `--limit` flag still uses pagination (backward compatibility)

### Architecture Design
**Streaming Implementation Strategy**:
- **Chunk Size**: Process and display 50 emails at a time (balance memory vs responsiveness)
- **Memory Monitoring**: Check ResourceMonitor.check_memory_usage() between chunks
- **Early Warning**: Display warning if total result count >1000 before streaming
- **Progress Indication**: Show "Streaming results..." progress message
- **Graceful Termination**: Honor Ctrl+C and memory limits during streaming

**New Components**:
```python
class StreamingResultDisplay:
    def stream_results(self, emails: List[Email], chunk_size: int = 50)
    def show_large_result_warning(self, total_count: int)  
    def display_streaming_chunk(self, chunk: List[Email], chunk_num: int)

class StreamingPaginator:
    def stream_all_results(self, items: List[Email]) -> Iterator[List[Email]]
    def get_chunk_size(self) -> int  # Based on memory constraints
```

### Integration Points
- **handle_find()**: Add `if args.all:` branch that bypasses existing Paginator
- **CommandProcessingService**: Add `process_streaming_command()` method
- **ResourceMonitor**: Monitor memory usage during streaming operations
- **Display Functions**: Extend `_display_email_page()` for streaming chunks

### Evidence for Completion
- **Functional Tests**: All streaming tests passing
- **Integration Test**: `ocli find --folder Inbox --all` with >1000 results shows warning then streams
- **Memory Test**: Large result streaming stays within memory limits
- **Backward Compatibility**: `ocli find --folder Inbox --limit 5` still uses pagination
- **Manual Test**: Real streaming output visible during command execution (not batch at end)

## Technical Implementation Plan

### Phase 1: Streaming Infrastructure (TDD) ✅ COMPLETE
1. ✅ Create `StreamingResultDisplay` class with chunk display logic
2. ✅ Add `StreamingPaginator` class for chunked iteration  
3. ✅ Test memory monitoring integration during streaming
**Status**: All 8 tests passing, classes implemented following TDD discipline

### Phase 2: CLI Integration (TDD) ✅ COMPLETE 
1. ✅ Modify `handle_find()` to detect `--all` flag
2. ✅ Add streaming branch that bypasses existing Paginator
3. ✅ Integrate ResourceMonitor checks between chunks
**Status**: All 3 CLI integration tests passing, --all flag now works

### Phase 3: User Experience (TDD) ✅ COMPLETE
1. ✅ Add large result set warning (>1000 emails)
2. ✅ Add progress indication during streaming (>100 emails)
3. ✅ Ctrl+C graceful termination (built-in KeyboardInterrupt handling)
**Status**: All UX features implemented with comprehensive test coverage

### Phase 4: Validation (TDD) ✅ COMPLETE
1. ✅ Verify backward compatibility with `--limit` flag
2. ✅ Test memory limits with very large result sets (ResourceMonitor integration)
3. ✅ Validate streaming performance vs pagination performance (<1s for 500 emails)
**Status**: All validation tests passing, comprehensive test coverage achieved

## Notes
- **No UI Changes**: This is streaming output for CLI, not web interface
- **Memory Safety**: ResourceMonitor provides existing infrastructure for safe memory management
- **Performance**: Chunked streaming should improve perceived performance for large results
- **Resource Limits**: Respect existing OUTLOOK_CLI_MAX_RESULT_COUNT environment variable
- **Monitoring**: Leverage existing PerformanceMonitor and AuditLogger for streaming metrics

## Dependencies Satisfied
- ✅ ResourceMonitor infrastructure (Milestone 011C)  
- ✅ CLI argument standardization (Milestone 012)
- ✅ Display formatting patterns established
- ✅ Performance monitoring infrastructure available