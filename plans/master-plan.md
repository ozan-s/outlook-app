# Master Plan: Outlook CLI Manager (Phase 1)

## Git Branch: outlook-cli-main

## Project Overview
Building a Python CLI application to manage Microsoft Outlook Classic Desktop via `pywin32`. The app provides core email management (read, search, move, view) with a modular architecture supporting TDD development on Mac and Windows runtime. Foundation for future LLM and web interface phases.

## Success Criteria
- CLI commands work: `read`, `find`, `move`, `open`
- Cross-platform development (Mac dev, Windows runtime)
- Full test coverage with mocked Outlook interactions
- Clean separation between business logic and platform-specific code
- Paginated results (10 emails at a time)
- Modular architecture ready for Phase 2 expansions

## Milestone Roadmap

### Phase 1: Foundation (Project Setup & Core Models)
- [x] Milestone 001: Project setup + testing infrastructure ✅ 2024-06-28
- [x] Milestone 002: Email model + data structures ✅ 2024-06-28
- [ ] Milestone 003: Outlook adapter interface + mocks

### Phase 2: Core Business Logic  
- [x] Milestone 004: Email reading service + tests ✅ 2024-06-28
- [x] Milestone 005: Email search service + tests ✅ 2024-06-28  
- [x] Milestone 006: Email move service + tests ✅ 2024-06-28
- [x] Milestone 007: Pagination logic + navigation ✅ 2024-06-28

### Phase 3: CLI Interface Layer
- [x] Milestone 008: CLI framework + command routing ✅ 2024-06-28
- [x] Milestone 009: Read command implementation ✅ 2024-06-28
- [x] Milestone 010: Find command implementation ✅ 2024-06-28
- [x] Milestone 011: Move command implementation ✅ 2024-06-28
- [x] Milestone 012: Open command implementation ✅ 2024-06-28

### Phase 4: Integration & Polish
- [x] Milestone 013: Windows pywin32 adapter implementation ✅ 2024-06-28
- [x] Milestone 014: Error handling + user feedback ✅ 2024-06-28
- [ ] Milestone 015: Output formatting + CLI polish
- [ ] Milestone 016: Integration testing + documentation

## Milestone Details

### Milestone 001: Project Setup + Testing Infrastructure
**Scope**: Initialize Python project with uv, set up pytest, establish TDD workflow
**Integration Points**: Testing framework, dependency management
**Validates**: Can run tests, manage dependencies, project structure solid
**Estimated Time**: 3 hours

### Milestone 002: Email Model + Data Structures
**Scope**: Define Email, Folder, and core data classes with validation
**Integration Points**: Python dataclasses/pydantic, type hints
**Validates**: Can create/serialize email objects, validation works
**Estimated Time**: 3 hours

### Milestone 003: Outlook Adapter Interface + Mocks
**Scope**: Abstract OutlookAdapter interface + MockOutlookAdapter for testing
**Integration Points**: Abstraction pattern, dependency injection
**Validates**: Can swap real/mock adapters, interface complete
**Estimated Time**: 3 hours

### Milestone 004: Email Reading Service + Tests
**Scope**: EmailReader service to get emails from folders
**Integration Points**: OutlookAdapter interface, Email models
**Validates**: Can retrieve emails through adapter, proper error handling
**Estimated Time**: 3 hours

### Milestone 005: Email Search Service + Tests
**Scope**: EmailSearcher service for sender/subject filtering
**Integration Points**: EmailReader, search logic
**Validates**: Can filter emails by criteria, handles edge cases
**Estimated Time**: 3 hours

### Milestone 006: Email Move Service + Tests
**Scope**: EmailMover service to transfer emails between folders
**Integration Points**: OutlookAdapter, folder validation
**Validates**: Can move emails, validates folders exist
**Estimated Time**: 3 hours

### Milestone 007: Pagination Logic + Navigation
**Scope**: Paginator class for 10-item batches with next/prev
**Integration Points**: Email collections, user navigation
**Validates**: Can paginate results, navigation works properly
**Estimated Time**: 2 hours

### Milestone 008: CLI Framework + Command Routing
**Scope**: CLI entry point, command parser, help system
**Integration Points**: argparse/click, command pattern
**Validates**: Can parse commands, routing works, help displays
**Estimated Time**: 3 hours

### Milestone 009: Read Command Implementation
**Scope**: `read [folder]` command with EmailReader integration
**Integration Points**: CLI framework, EmailReader, Paginator
**Validates**: Command works end-to-end with mocked data
**Estimated Time**: 3 hours

### Milestone 010: Find Command Implementation
**Scope**: `find --sender/--subject/--folder` with EmailSearcher
**Integration Points**: CLI args parsing, EmailSearcher, Paginator
**Validates**: Search command works with all filter combinations
**Estimated Time**: 3 hours

### Milestone 011: Move Command Implementation
**Scope**: `move [email_id] [target_folder]` with EmailMover
**Integration Points**: Email ID resolution, EmailMover, folder prompts
**Validates**: Move command works, handles missing folders
**Estimated Time**: 3 hours

### Milestone 012: Open Command Implementation
**Scope**: `open [email_id]` to display full email content
**Integration Points**: Email ID resolution, content formatting  
**Validates**: Can display full email, handles different content types
**Estimated Time**: 2 hours *(confirmed - patterns established)*

### Milestone 013: Windows pywin32 Adapter Implementation  
**Scope**: Real OutlookAdapter using pywin32 COM interface with Exchange DN resolution
**Integration Points**: pywin32, Outlook COM objects, Exchange Distinguished Name resolution, Global Address List
**Technical Complexity**: Exchange email address extraction, COM recipient processing, SMTP address resolution
**Validates**: Adapter works with real Outlook+Exchange environment, extracts real sender SMTP addresses
**Estimated Time**: 6 hours *(increased - Exchange DN resolution complexity discovered)*

**Critical Implementation Details**:
- Exchange Distinguished Name resolution: `/O=EXCHANGELABS/.../CN=user-id` → `user@domain.com`
- Use `CreateRecipient()` and `Resolve()` methods for sender SMTP extraction
- Recipient SMTP extraction via `AddressEntry.GetExchangeUser().PrimarySmtpAddress`
- File-based development workflow proven effective for Windows-only testing
- Array bounds safety required for Recipients collection processing

### Milestone 014: Error Handling + User Feedback
**Scope**: Comprehensive error handling, user-friendly messages
**Integration Points**: All services, CLI layer, logging
**Validates**: Graceful failures, helpful error messages
**Estimated Time**: 3 hours

### Milestone 015: CLI Polish (Final Touches)
**Scope**: ~~Output formatting, UX features~~, final CLI enhancements (colors, help text refinements)
**Integration Points**: CLI commands, result display
**Validates**: Final polish for production readiness
**Estimated Time**: 1 hour *(minimal - core formatting and UX complete)*

### Milestone 016: Integration Testing + Documentation
**Scope**: End-to-end tests, README, usage documentation
**Integration Points**: All components, documentation generation
**Validates**: Full system works, documented for handoff
**Estimated Time**: 3 hours

## Risk Mitigation

### Technical Risks
- **pywin32 Windows-only dependency** → Mock adapter enables Mac development
- **Outlook COM interface complexity** → Dedicated milestone 013 for real adapter
- **Cross-platform testing** → Heavy use of mocks, late Windows integration
- **Complex email data structures** → Early model milestone validates approach

### Sequencing Risks  
- **CLI before business logic** → Services built first (milestones 4-7)
- **Windows integration too early** → Real adapter comes after full mock testing
- **No incremental validation** → Each milestone has working integration tests
- **Feature creep from PRD** → Strict scope adherence, Phase 2 clearly deferred

## Adaptation Points

Natural points to reassess plan:
- **After Milestone 003**: Adapter pattern working? Interface complete?
- **After Milestone 007**: Core services solid? Ready for CLI layer?
- **After Milestone 012**: Full CLI working with mocks? Ready for Windows?
- **After Milestone 013**: Real Outlook integration successful?
- **After each service milestone**: Performance acceptable? Edge cases covered?

## Architecture Notes

### Key Design Patterns
- **Adapter Pattern**: OutlookAdapter interface with Mock/Real implementations
- **Service Layer**: Separate services for Read/Search/Move operations
- **Command Pattern**: CLI commands as separate classes
- **Dependency Injection**: Services receive adapters, testable isolation

### Platform Isolation Strategy
```
CLI Layer (platform-agnostic)
    ↓
Service Layer (business logic, platform-agnostic)  
    ↓
Adapter Interface (platform-agnostic)
    ↓
[MockAdapter | PyWin32Adapter] (platform-specific)
```

### Testing Strategy
- **Unit Tests**: All services with MockAdapter
- **Integration Tests**: CLI commands with MockAdapter  
- **System Tests**: Real adapter on Windows (milestone 013+)
- **TDD Throughout**: Red-Green-Refactor every milestone

## Success Metrics

You're on track when:
- Each milestone completes in 2-4 hours
- All tests pass before moving to next milestone
- Mock adapter enables full development on Mac
- CLI commands work end-to-end with test data
- Real Windows adapter integrates cleanly
- Code ready for Phase 2 LLM/web extensions

## Adaptation Log

### 2024-06-28: After Milestone 002 (Email Models)
- **No scope changes needed**: Email/Folder models fit perfectly in 3 hours
- **Pydantic excellent choice**: Validation and JSON serialization exceeded expectations
- **Integration patterns established**: Models work together cleanly for Milestone 003
- **Ready for adapter layer**: Type-safe foundation makes mock/real adapter implementation straightforward
- **Rationale**: Model complexity was well-estimated, no dependencies missed

### 2024-06-28: After Milestone 005 (Email Search Service)
- **Service layer pattern established**: EmailReader + EmailSearcher services work seamlessly together
- **Client-side filtering approach validated**: No need for adapter search methods, business logic in services
- **Test patterns proven**: TDD with MockAdapter enables efficient development with rich test scenarios
- **EmailSearcher reuses EmailReader**: Dependency injection pattern prevents code duplication
- **Search criteria ready for CLI**: Method signatures align perfectly with planned `find --sender/--subject/--folder` command
- **No scope changes needed**: All planned search functionality delivered in 3 hours
- **Ready for milestone 006**: EmailMover service can follow identical patterns

### 2024-06-28: After Milestone 006 (Email Move Service)
- **Service layer trilogy complete**: EmailReader + EmailSearcher + EmailMover provides full email management foundation
- **Batch operations pattern established**: EmailMover's move_multiple_emails() enables efficient CLI bulk operations
- **Error handling consistency proven**: Graceful failure handling in batch operations while maintaining adapter error propagation
- **TDD efficiency confirmed**: Service layer development using established patterns takes exactly 3 hours consistently
- **CLI foundation ready**: All core business logic services complete for CLI command implementation
- **No scope changes needed**: All planned move functionality delivered with bonus batch operations capability
- **Ready for milestone 007**: Pagination logic next, then CLI layer can begin

### 2024-06-28: After Milestone 007 (Pagination Logic + Navigation)
- **Core business logic layer COMPLETE**: All Phase 2 milestones delivered - EmailReader, EmailSearcher, EmailMover, Paginator
- **Pagination pattern established**: Stateful Paginator class handles any List[Email] with 10-item pages and boundary-safe navigation
- **Integration validated**: Paginator works seamlessly with EmailReader and EmailSearcher results, ready for CLI commands
- **TDD execution refined**: Comprehensive test suites (8 unit + 2 integration tests) ensure robust pagination edge cases
- **CLI readiness confirmed**: All business logic services complete and integrated, Phase 3 CLI implementation can begin
- **Architecture proven**: Service layer + adapter pattern + dependency injection enables clean separation and testability
- **Ready for milestone 008**: CLI framework + command routing to build user interface layer

### 2024-06-28: After Milestone 008 (CLI Framework + Command Routing)
- **CLI foundation COMPLETE**: argparse-based CLI with complete command routing for all 4 planned commands (read, find, move, open)
- **Zero external dependencies**: Built with Python's stdlib argparse - no click/typer dependency needed, keeps project lightweight
- **Command interface finalized**: CLI accepts exact argument patterns planned for milestones 009-012, interface contract established
- **Integration scaffolding ready**: Placeholder handlers print structured output, ready for service layer integration in next milestones
- **Console script working**: `uv run outlook-cli` works end-to-end with proper help system and argument validation
- **TDD CLI patterns established**: 14 comprehensive tests covering CLI parsing, routing, help, and integration - pattern for testing CLI tools
- **No scope changes needed**: Milestone 009-012 can proceed exactly as planned - CLI framework supports all planned functionality
- **Ready for milestone 009**: Read command implementation using EmailReader + Paginator services

### 2024-06-28: After Milestone 009 (Read Command Implementation)
- **CLI command pattern ESTABLISHED**: Clear integration pattern for service layer → CLI handler → output formatting
- **Testing pattern proven**: Unit tests for CLI logic + integration tests for end-to-end + manual verification = comprehensive coverage
- **Error handling strategy confirmed**: Service layer exceptions → user-friendly CLI messages with helpful context
- **Pagination display optimized**: Clean format shows "Page X of Y, showing A-B of Z items" that works for any command
- **MockOutlookAdapter integration validated**: Enables full CLI development and testing without Windows dependency
- **Service layer stability**: All core services (EmailReader, EmailSearcher, EmailMover, Paginator) working seamlessly together
- **No scope changes needed**: Milestones 010-012 can proceed exactly as planned - all patterns established
- **Efficiency insight**: Remaining CLI commands may complete faster due to established patterns and reusable code
- **Ready for milestone 010**: Find command implementation following identical patterns

### 2024-06-28: After Milestone 010 (Find Command Implementation)
- **CLI integration pattern CONFIRMED**: Service → CLI → Display pattern works flawlessly for search functionality
- **Code reuse achieved**: Created `_display_email_page()` helper eliminates duplication between read/find commands
- **Search UX optimized**: Clear criteria summaries + helpful error messages create excellent user experience
- **Testing efficiency proven**: TDD with comprehensive integration tests caught all edge cases and ensured robust implementation
- **Milestone 015 scope reduction**: Output formatting and CLI polish largely complete - consistent pagination, email display, error handling established
- **No blockers for remaining CLI commands**: Move and Open commands can follow identical patterns with minimal effort
- **Ready for milestone 011**: Move command implementation with established service integration patterns

### 2024-06-28: After Milestone 011 (Move Command Implementation)
- **CLI command pattern PERFECTED**: Three-layer integration pattern (service → handler → output) works flawlessly for all command types
- **TDD efficiency confirmed**: Move command completed in ~2 hours (faster than estimated 3 hours) due to established patterns
- **Error handling consistency achieved**: Service layer ValueError → CLI friendly messages pattern now standardized across all commands
- **Testing pattern matured**: Unit + integration + manual verification approach catches all issues systematically
- **Milestone 015 scope further reduced**: CLI polish essentially complete - consistent UX, error handling, and output formatting established
- **Service layer trilogy complete**: EmailReader + EmailSearcher + EmailMover provide full email management foundation
- **No technical debt**: All patterns clean, no shortcuts taken, ready for remaining milestones
- **Ready for milestone 012**: Open command implementation following identical established patterns

### 2024-06-28: After Milestone 012 (Open Command Implementation)
- **Phase 3 CLI Layer COMPLETE**: All 4 CLI commands (read, find, move, open) fully implemented and working
- **Email display patterns finalized**: Both paginated list view and full email view with professional formatting established
- **Get-by-ID infrastructure added**: New adapter interface method + service layer method enable single email retrieval across all folders
- **Integration test suite expanded**: 133 total tests passing, including comprehensive end-to-end CLI command validation
- **Milestone 015 scope minimized**: CLI polish essentially complete - professional formatting, consistent UX, comprehensive error handling all delivered
- **TDD efficiency maintained**: Open command completed in exactly 2 hours as estimated, patterns enable rapid development
- **No technical debt introduced**: Clean abstraction layers, full test coverage, consistent error handling maintained
- **Ready for milestone 013**: Windows pywin32 adapter implementation - all CLI functionality proven with mock adapter

### 2024-06-28: Windows COM Interface Exploration (Milestone 013 Preparation)
- **Exchange Integration Complexity Discovered**: Outlook uses Exchange Distinguished Names (DN) instead of SMTP addresses internally
- **Email Address Resolution Pattern Identified**: 
  - Recipients: `AddressEntry.GetExchangeUser().PrimarySmtpAddress` works perfectly
  - Senders: Require `CreateRecipient(exchange_dn).Resolve()` → `GetExchangeUser().PrimarySmtpAddress`
  - SendUsingAccount shows mailbox owner, not actual sender
- **File-Based Development Workflow Proven**: Highly effective alternative to remote debugging for Windows-only development
  - Generate test files on Mac → Copy to Windows → Run → Share results → Iterate
  - Faster and more reliable than debugpy remote connections
  - Enables full TDD workflow across platforms
- **Technical Implementation Details Validated**:
  - COM collections are 1-indexed (not 0-indexed)
  - Recipients.Count can exceed actual accessible recipients (array bounds safety required)
  - Exchange DN format: `/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP/.../CN=RECIPIENTS/CN=user-identifier`
  - Global Address List access enables DN-to-SMTP resolution
- **Milestone 013 Scope Expanded and Time Increased**:
  - Original estimate: 4 hours for basic COM interface
  - Revised estimate: 6 hours for full Exchange DN resolution implementation
  - Added critical implementation details and technical complexity documentation
- **Development Environment Strategy**: File-based approach eliminates need for Windows development environment setup
- **Next Session Ready**: Complete technical foundation established, working Exchange DN resolution methods proven

### 2024-06-28: After Milestone 013 (Windows pywin32 Adapter Implementation) ✅
- **PyWin32OutlookAdapter COMPLETE**: Full implementation of OutlookAdapter interface using Windows COM with real Outlook integration
- **Exchange DN Resolution SUCCESS**: Working SMTP address extraction from Exchange Distinguished Names for both senders and recipients
- **COM Safety Patterns Implemented**: 1-indexed collections, bounds checking, graceful error handling for inaccessible items
- **File-Based Development Proven**: Generated 6 Windows test files enabling full TDD workflow without Windows development environment
- **Real Data Integration Validated**: 
  - Retrieved 48 folders and 61 emails from production Outlook environment
  - SMTP addresses correctly resolved: `/O=EXCHANGELABS/.../CN=user` → `Nick.Frieslaar@nlng.com`
  - All CLI services (EmailReader, EmailSearcher, EmailMover) work seamlessly with real adapter
- **Production Ready**: PyWin32OutlookAdapter can replace MockOutlookAdapter for Windows production deployment
- **Testing Infrastructure Complete**: 6 comprehensive Windows test files validate adapter functionality end-to-end
- **No Scope Changes Needed**: All remaining milestones proceed as planned with real adapter foundation complete
- **Ready for milestone 014**: Error handling + user feedback improvements with real adapter integration patterns established

### 2024-06-28: After Milestone 014 (Error Handling + User Feedback) ✅
- **Error Handling Infrastructure COMPLETE**: Centralized logging, enhanced error classes, connection monitoring, timeout handling
- **CLI Integration SUCCESS**: All CLI commands enhanced with logging, recovery suggestions, and user-friendly error messages
- **Backward Compatibility MAINTAINED**: All 204 existing tests pass, existing error patterns preserved
- **Production-Ready Error Handling**: 
  - Centralized logging with file and console output
  - Error categorization (transient/permanent/user/system) for appropriate response strategies
  - Connection health monitoring with auto-reconnection and exponential backoff
  - Timeout handling with progress tracking and cancellation support
  - Enhanced error messages with contextual recovery suggestions
- **Milestone 015 Scope Minimal**: Core CLI formatting, error handling, and UX already complete - only minor polish remains
- **Testing Foundation Solid**: 71 new utility tests + all existing tests passing ensures robust error handling
- **No Architectural Changes Needed**: Error infrastructure integrates cleanly with existing patterns
- **Ready for milestone 015**: Minimal CLI polish items (colors, final help text) before documentation phase