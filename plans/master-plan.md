# Master Plan: Outlook CLI "Find 2.0" Enhancement

## Git Branch: prd-1

## Project Overview
Enhance the existing Outlook CLI with powerful filtering capabilities and folder discovery. Adding a new `folders` command to list all available Outlook folders, plus comprehensive filtering options for `find`/`read` commands including date filters, attachment handling, read status, importance levels, exclusions, and result control.

## Success Criteria
- [ ] `ocli folders` command lists all user-visible folders reliably (flat and tree views)
- [ ] `find` and `read` support all new filters with comprehensive test coverage
- [ ] Ambiguous/conflicting flags are warned with clear messaging
- [ ] Date filters accept both explicit (YYYY-MM-DD) and relative (7d, 2w) input
- [ ] Performance: sub-2s for 1,000 emails; streaming mode for large sets
- [ ] All commands accept `--limit` and `--all` for result control

## Milestone Roadmap

### Phase 1: Foundation (CLI Parser & Infrastructure)
- [x] Milestone 001: Enhanced CLI argument parser with new filter flags ✅ 2025-06-29
- [ ] ~Milestone 002: Flag conflict detection and warning system~ (Completed in 001)
- [x] Milestone 003: Relative date parsing and validation ✅ 2025-06-29

### Phase 2: Service Layer (Data Access & Processing)
- [x] Milestone 004: Folder enumeration service and adapter methods ✅ 2025-06-29
- [x] **Milestone 005: Windows Testing Checkpoint #1 - COM Interface Validation** ✅ 2025-06-29
- [x] **Milestone 005C: Actual Windows Environment Validation** ✅ 2025-06-29
- [x] **Milestone 006: Email filtering service with attachment/read status filters** ✅ 2025-06-29
- [ ] Milestone 007: Sorting and pagination service enhancements

### Phase 3: Core Commands (New Functionality)
- [ ] ~Milestone 008: `folders` command with flat output~ (Partially completed in 001)
- [ ] ~Milestone 009: Enhanced `find` command with all new filters~ (Completed in 006)
- [ ] **Milestone 010: Windows Testing Checkpoint #2 - Core Filtering Validation**
- [ ] Milestone 011: Enhanced `read` command with filtering support

### Phase 4: Advanced Features (Performance & UX)
- [ ] ~Milestone 012: Tree view for `folders` command~ (Completed in 001)
- [ ] Milestone 013: Streaming output for large result sets
- [ ] Milestone 014: Performance optimization and large mailbox handling

### Phase 5: Integration & Polish
- [ ] **Milestone 015: Windows Testing Checkpoint #3 - Full System Validation**
- [ ] Milestone 016: Error handling and edge case coverage
- [ ] Milestone 017: Documentation and usage examples

## Milestone Details

### Milestone 001: Enhanced CLI Argument Parser with New Filter Flags
**Scope**: Add all new command-line flags to argparse configuration
**Integration Points**: CLI entry points, existing command handlers
**Validates**: All new flags parse correctly, help text displays properly
**Estimated Time**: 3 hours
**Flags to Add**: `--since`, `--until`, `--is-unread`, `--is-read`, `--has-attachment`, `--no-attachment`, `--attachment-type`, `--importance`, `--folders`, `--not-sender`, `--not-subject`, `--limit`, `--all`, `--sort-by`, `--sort-order`, `--tree`

### Milestone 002: Flag Conflict Detection and Warning System  
**Scope**: Implement logic to detect mutually exclusive flags and warn users
**Integration Points**: Argument validation, CLI error handling
**Validates**: Conflicting flags trigger warnings but don't crash, first flag wins
**Estimated Time**: 2 hours
**Conflicts**: `--is-read` vs `--is-unread`, `--has-attachment` vs `--no-attachment`, `--limit` vs `--all`

### Milestone 003: Relative Date Parsing and Validation ✅ COMPLETE
**Scope**: Comprehensive date vocabulary (30+ formats) including time units, natural language, weekdays
**Integration Points**: CLI argument processing, EmailSearcher service, date validation
**Validates**: All date formats work end-to-end, error handling, full integration with search
**Actual Time**: 4 hours (expanded scope)
**Delivered**: Minutes/hours/days/weeks/months/years (7d, 2h, 1M), natural language (today, yesterday, tomorrow), weekdays (monday, last-friday), relative references (last-week, this-month)

### Milestone 004: Folder Enumeration Service and Adapter Methods
**Scope**: Add methods to OutlookAdapter for recursive folder discovery
**Integration Points**: Adapter pattern, COM interface for PyWin32, Mock adapter
**Validates**: Can enumerate all accessible folders, handles nested structures
**Estimated Time**: 4 hours

### Milestone 005: Windows Testing Checkpoint #1 - COM Interface Validation
**Scope**: Generate comprehensive test script for Windows machine to validate COM interface
**Integration Points**: PyWin32 adapter, real Outlook COM interface
**Validates**: Folder enumeration works with real Outlook, COM errors handled properly
**Estimated Time**: 2 hours

**Test Script Generated**:
- Folder enumeration tests (flat structure, nested folders, edge cases)
- COM interface connection tests
- Error handling tests (Outlook not running, permissions, etc.)
- Output capture for debugging

**Manual Process**:
1. Generate test script with expected outputs
2. User runs on Windows machine with real Outlook
3. User pastes results back to Mac
4. Debug any COM interface issues before proceeding

### Milestone 005C: Actual Windows Environment Validation ✅ COMPLETE
**Scope**: Replace simulation-based testing with actual Windows environment validation to prove foundation solid
**Integration Points**: Real COM interface, CLI commands, corporate Exchange environment
**Validates**: All core functionality proven working in real Windows corporate environment
**Actual Time**: 3 hours

**Delivered**:
- COM Interface Validation: 3/3 tests passed (48 real corporate folders enumerated)
- Application Integration: 5/5 tests passed (all CLI commands working with real data)
- Unicode encoding fixes for Windows subprocess calls
- Performance validation with 60-second timeouts for corporate environments
- Cross-adapter compatibility confirmed (mock vs real adapters)
- Exchange DN resolution patterns validated and ready

**Critical Breakthrough**: Replaced false confidence from simulation with proven validation using actual Windows corporate Outlook environment. All core functionality confirmed working.

### Milestone 006: Email Filtering Service with Attachment/Read Status Filters  
**Scope**: Extend filtering logic in EmailService for new filter types
**Integration Points**: Existing email search, adapter filter methods
**Validates**: All filter combinations work correctly, maintains performance
**Estimated Time**: 4 hours

### Milestone 007: Sorting and Pagination Service Enhancements
**Scope**: Add sorting by multiple fields and pagination control to services
**Integration Points**: Email retrieval, result formatting, CLI display
**Validates**: Sorting works for all fields, pagination limits respected
**Estimated Time**: 3 hours

### Milestone 008: `folders` Command with Flat Output
**Scope**: Implement new CLI command to list all folders in flat format
**Integration Points**: CLI command routing, folder service, display formatting
**Validates**: Command works with both adapters, output format matches spec
**Estimated Time**: 3 hours

### Milestone 009: Enhanced `find` Command with All New Filters ✅ COMPLETED IN 006
**Scope**: Integrate all new filters into existing find command handler
**Integration Points**: Existing find logic, service layer filters, error handling
**Validates**: All filter combinations work, maintains backward compatibility
**Actual Time**: Completed as part of Milestone 006 (integrated approach)

### Milestone 010: Windows Testing Checkpoint #2 - Core Filtering Validation
**Scope**: Generate comprehensive test script for all new filtering functionality
**Integration Points**: All new filters, real Outlook data, performance testing
**Validates**: All filters work with real data, performance meets targets
**Estimated Time**: 2 hours

**Test Script Generated**:
- All filter combinations (`--since`, `--until`, `--is-unread`, etc.)
- Date parsing tests (relative and absolute dates)
- Attachment filtering tests
- Conflict detection tests
- Performance tests with large result sets
- Edge case tests (empty folders, special characters, etc.)

**Manual Process**:
1. Generate comprehensive test matrix
2. User runs full test suite on Windows
3. User captures timing and output data
4. Debug any filter or performance issues

### Milestone 011: Enhanced `read` Command with Filtering Support
**Scope**: Add filtering capabilities to read command using same service layer
**Integration Points**: Existing read logic, shared filtering service
**Validates**: Read command supports all filters, consistent with find behavior
**Estimated Time**: 3 hours

### Milestone 012: Tree View for `folders` Command  
**Scope**: Add `--tree` flag to display folders in hierarchical tree format
**Integration Points**: Folder service, output formatting, CLI display
**Validates**: Tree output is readable and accurate, preserves folder relationships
**Estimated Time**: 2 hours

### Milestone 013: Streaming Output for Large Result Sets
**Scope**: Implement streaming display for `--all` flag with large result sets
**Integration Points**: Result pagination, CLI display, memory management
**Validates**: Large result sets don't crash, warning shown for >1000 results
**Estimated Time**: 3 hours

### Milestone 014: Performance Optimization and Large Mailbox Handling
**Scope**: Optimize filtering and sorting for large mailboxes, meet performance targets
**Integration Points**: Service layer queries, COM interface optimization
**Validates**: Sub-2s response for 1000 emails, graceful handling of huge mailboxes
**Estimated Time**: 4 hours

### Milestone 015: Windows Testing Checkpoint #3 - Full System Validation
**Scope**: Generate final comprehensive test suite for complete system validation
**Integration Points**: All commands, all features, real-world scenarios
**Validates**: Entire system works reliably with real Outlook data
**Estimated Time**: 2 hours

**Test Script Generated**:
- End-to-end workflow tests
- Complex filter combination scenarios
- Large mailbox stress tests
- Tree view and streaming output tests
- Error recovery and edge case tests
- Performance validation under realistic conditions

**Manual Process**:
1. Generate real-world usage scenarios
2. User runs comprehensive acceptance tests
3. User captures final performance and reliability data
4. Address any remaining issues before documentation

### Milestone 016: Error Handling and Edge Case Coverage
**Scope**: Comprehensive error handling for all new features and edge cases
**Integration Points**: All command handlers, service layer, adapter methods
**Validates**: Graceful handling of COM errors, network issues, invalid input
**Estimated Time**: 3 hours

### Milestone 017: Documentation and Usage Examples
**Scope**: Update help text, add usage examples, document all new features
**Integration Points**: CLI help system, command documentation
**Validates**: All features are documented with clear examples
**Estimated Time**: 2 hours

## Risk Mitigation

### Technical Risks
- **COM Interface Complexity** → Strategic Windows testing checkpoints catch issues early
- **Performance with Large Mailboxes** → Dedicated performance milestone with benchmarking
- **Date Parsing Edge Cases** → Comprehensive test suite for all date formats in milestone 003
- **Flag Conflict Complexity** → Simple "first wins" strategy with clear warnings

### Cross-Platform Development Risks
- **Mac/Windows COM Differences** → Windows testing checkpoints at critical integration points
- **Real vs Mock Adapter Gaps** → Validation with real Outlook at each checkpoint
- **Performance Variations** → Windows-specific performance testing in checkpoints
- **Error Handling Differences** → COM error testing on actual Windows environment

### Sequencing Risks
- **Service Before CLI** → Build filtering logic before integrating with commands
- **Mock Before Real** → Validate all logic with MockAdapter before Windows testing
- **Core Before Advanced** → Basic functionality before tree view and streaming
- **Validation Before Building** → Windows checkpoints prevent building on broken foundations

## Windows Testing Strategy

### Checkpoint #1 (After Milestone 004)
**Focus**: COM interface and folder enumeration
**Critical Because**: Foundation for all subsequent work
**Test Coverage**: Basic COM connectivity, folder discovery, error handling

### Checkpoint #2 (After Milestone 009)  
**Focus**: All new filtering functionality
**Critical Because**: Core feature validation before advanced features
**Test Coverage**: All filters, performance, complex combinations

### Checkpoint #3 (After Milestone 014)
**Focus**: Complete system validation
**Critical Because**: Final validation before release
**Test Coverage**: End-to-end workflows, stress testing, real-world scenarios

## Adaptation Log

### 2025-06-29: After Milestone 001 (Enhanced CLI Parser)
- **Removed 002**: Flag conflict detection implemented in Milestone 001 using argparse mutually exclusive groups
- **Removed 008**: `folders` command basic functionality completed in Milestone 001
- **Removed 012**: Tree view for folders implemented alongside basic command in Milestone 001
- **Rationale**: TDD implementation revealed argparse handles flag conflicts elegantly, and folders command was simpler than expected

### 2025-06-29: After Milestone 003 (Relative Date Parsing)
- **Scope Expansion**: Date vocabulary expanded far beyond plan (4 → 30+ formats)
- **Implementation**: Added comprehensive time units (m, h, d, w, M, y), natural language (today, tomorrow, weekdays), relative references
- **Impact**: Date filtering now matches modern CLI tool expectations - no future milestones need date parsing work
- **Rationale**: TDD implementation revealed user expectations for comprehensive date vocabulary; minimal effort for major UX improvement

### 2025-06-29: After Milestone 004 (Folder Enumeration Service)
- **No Scope Changes**: Milestone delivered exactly as planned
- **Implementation**: FolderService class handles hierarchy organization, tree view displays perfect nested structure with Unicode characters
- **Pattern Established**: Service-to-CLI Integration Pattern works well for folder display logic
- **Impact**: Folder tree view already working - no additional milestones needed for folder functionality
- **Rationale**: Clean separation of concerns between adapter (data), service (organization), and CLI (display) proved effective

### 2025-06-29: After Milestone 005 (Windows Testing Checkpoint #1)
- **No Scope Changes**: Milestone delivered exactly as planned
- **Implementation**: Generated comprehensive Windows COM validation script with full test matrix, detailed user instructions, and result analysis framework
- **Testing Infrastructure**: Created reusable testing module pattern for future Windows checkpoints
- **Foundation Validated**: Ready to proceed with filtering features once Windows COM interface confirmed stable
- **Rationale**: TDD approach ensured comprehensive validation script that thoroughly tests COM interface before building advanced features on top

### 2025-06-29: After Milestone 005C (Windows Environment Validation)
- **Milestone Renamed**: 005B → 005C to reflect actual Windows validation vs planned simulation
- **100% Success Rate**: COM interface (3/3) + Application integration (5/5) tests passed
- **Critical Fixes Applied**: Unicode encoding fix for Windows subprocess calls, 60-second timeouts for corporate environments
- **Foundation Proven**: All core functionality validated with real Windows corporate Outlook (48 folders, real Exchange data)
- **Production Ready**: Application confirmed working in target deployment environment
- **Impact**: Can proceed to advanced filtering features with confidence in solid foundation
- **Rationale**: Real validation replaced simulation, providing genuine deployment confidence instead of false test success

### 2025-06-29: After Milestone 006 (Email Filtering Service)
- **Removed 009**: Enhanced `find` command integration completed within Milestone 006
- **Scope Integration**: Service layer and CLI integration done together for efficiency
- **Performance Validated**: Sub-second filtering with 1000+ emails meets requirements
- **Test Coverage**: 25 tests passing, comprehensive filtering functionality delivered
- **Impact**: Milestone 010 (Windows Testing Checkpoint #2) now ready to validate complete filtering system
- **Rationale**: TDD implementation revealed that service and CLI integration were naturally coupled; separating them would have been artificial and inefficient

## Adaptation Points

Natural points to reassess plan:
- **After Phase 1**: CLI parsing solid? Flag conflicts handled properly? ✅ Completed  
- **After Checkpoint #1**: COM interface stable? Folder enumeration reliable? ✅ Completed (Windows validation successful)
- **After Checkpoint #2**: Core filtering working? Performance acceptable?
- **After Checkpoint #3**: System ready for production use?

## Integration Testing Strategy

Each milestone includes validation with:
- **Unit Tests**: Mock adapter for rapid iteration
- **Integration Tests**: PyWin32 adapter with real Outlook (at checkpoints)
- **CLI Tests**: End-to-end command execution with expected outputs
- **Performance Tests**: Timing validation for large result sets
- **Windows Manual Tests**: Real COM interface validation at strategic points

## Development Notes

- Follow existing Service-to-CLI Integration Pattern from CLAUDE.md
- Use AdapterFactory pattern for consistent mock/real adapter switching
- Maintain COM Collection Safety Pattern for PyWin32 interactions
- Apply CLI Error Handling Strategy for all new commands
- Leverage existing configuration system for adapter selection
- Windows testing checkpoints generate detailed test scripts with expected outputs for manual validation