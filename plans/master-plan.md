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
- [ ] Milestone 004: Email reading service + tests
- [ ] Milestone 005: Email search service + tests
- [ ] Milestone 006: Email move service + tests
- [ ] Milestone 007: Pagination logic + navigation

### Phase 3: CLI Interface Layer
- [ ] Milestone 008: CLI framework + command routing
- [ ] Milestone 009: Read command implementation
- [ ] Milestone 010: Find command implementation
- [ ] Milestone 011: Move command implementation
- [ ] Milestone 012: Open command implementation

### Phase 4: Integration & Polish
- [ ] Milestone 013: Windows pywin32 adapter implementation
- [ ] Milestone 014: Error handling + user feedback
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
**Estimated Time**: 2 hours

### Milestone 013: Windows pywin32 Adapter Implementation
**Scope**: Real OutlookAdapter using pywin32 COM interface
**Integration Points**: pywin32, Outlook COM objects, error handling
**Validates**: Adapter works with real Outlook on Windows
**Estimated Time**: 4 hours

### Milestone 014: Error Handling + User Feedback
**Scope**: Comprehensive error handling, user-friendly messages
**Integration Points**: All services, CLI layer, logging
**Validates**: Graceful failures, helpful error messages
**Estimated Time**: 3 hours

### Milestone 015: Output Formatting + CLI Polish
**Scope**: Clean table formatting, colors, consistent UX
**Integration Points**: CLI commands, result display
**Validates**: Professional CLI appearance, readable output
**Estimated Time**: 3 hours

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

**Next Step**: Use `/plan` to detail Milestone 003