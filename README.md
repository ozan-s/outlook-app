# Outlook CLI Application

A sophisticated cross-platform command-line interface for Microsoft Outlook email management, built with Python and designed for professional workflows.

## 🌟 Overview

The Outlook CLI is a production-ready email management tool that bridges cross-platform development with Windows-specific Outlook integration. It demonstrates modern Python development practices including Test-Driven Development (TDD), dependency injection, and clean architecture patterns.

### Key Features

- **Cross-Platform Development**: Develop on Mac/Linux, deploy on Windows
- **Real Outlook Integration**: Direct COM interface integration with Microsoft Outlook
- **Professional CLI Experience**: Rich command interface with colors, pagination, and helpful error messages
- **Smart Configuration**: Platform-aware defaults with flexible override options
- **Comprehensive Testing**: 220+ tests with full coverage including integration tests
- **TDD-Driven Development**: All features built using Red-Green-Refactor methodology

## 🚀 Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/ozan-s/outlook-app.git
cd outlook-app

# Install dependencies
uv sync

# Verify installation
ocli --help
```

### Basic Usage

```bash
# Windows (uses real Outlook by default)
ocli read --folder Inbox
ocli find --keyword "meeting"
ocli move <email-id> "Archive"

# Mac/Linux (uses mock data by default)  
ocli read --folder Inbox
ocli find --subject "project"
```

## 📚 Complete Command Reference

### Global Options

```bash
--adapter {mock,real}    # Override default adapter (real on Windows, mock elsewhere)
```

### Read Command
List emails from a specific folder with pagination.

```bash
ocli read --folder <folder-name>

# Examples
ocli read --folder Inbox
ocli read --folder "Sent Items"
ocli read --folder Drafts
```

**Output**: Paginated email list with subjects, senders, dates, and attachment indicators.

### Find Command  
Search for emails using multiple criteria with OR/AND logic.

```bash
# Keyword search (searches both subject AND sender)
ocli find --keyword <term>

# Specific field searches
ocli find --subject <term>
ocli find --sender <email-or-name>

# Combined search (AND logic)
ocli find --subject <term> --sender <email>

# Specify folder
ocli find --keyword <term> --folder "Sent Items"

# Examples
ocli find --keyword "meeting"                    # Search subject and sender
ocli find --subject "project update"             # Search subject only  
ocli find --sender "john@company.com"            # Search sender only
ocli find --subject "review" --sender "alice"    # Combined AND search
```

**Search Logic**:
- `--keyword`: OR logic (finds emails with keyword in subject OR sender)
- `--subject` + `--sender`: AND logic (finds emails matching both criteria)

### Move Command
Move emails between folders.

```bash
ocli move <email-id> <target-folder>

# Examples
ocli move inbox-001 "Archive"
ocli move drafts-123 "Sent Items"
```

**Email IDs**: Use the IDs displayed in the email list from `read` or `find` commands.

### Open Command
Display full email content including headers and body.

```bash
ocli open <email-id>

# Examples  
ocli open inbox-001
ocli open sent-456
```

## ⚙️ Configuration System

### Adapter Types

The application uses a **factory pattern** for email data sources:

- **Mock Adapter** (`mock`): Simulated email data for development and testing
- **Real Adapter** (`real`): Direct integration with Microsoft Outlook via COM interface

### Configuration Precedence

1. **CLI Argument** (highest priority): `--adapter real`
2. **Environment Variable**: `$env:OUTLOOK_ADAPTER="real"`  
3. **Platform Default** (lowest priority): `real` on Windows, `mock` elsewhere

### Configuration Examples

```bash
# Use environment variable (persistent)
$env:OUTLOOK_ADAPTER = "real"
ocli read --folder Inbox

# Override with CLI argument (one-time)
ocli --adapter mock read --folder Inbox

# Windows default behavior (no configuration needed)
ocli read --folder Inbox  # Automatically uses real adapter

# Mac/Linux default behavior
ocli read --folder Inbox  # Automatically uses mock adapter
```

## 🏗️ Architecture

### High-Level Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   CLI Layer     │    │  Service Layer  │    │  Adapter Layer  │
│                 │    │                 │    │                 │
│ • Command       │    │ • EmailReader   │    │ • MockAdapter   │
│   Parsing       │───▶│ • EmailSearcher │───▶│ • PyWin32       │
│ • Argument      │    │ • EmailMover    │    │   Adapter       │
│   Validation    │    │ • Paginator     │    │                 │
│ • Output        │    │                 │    │                 │
│   Formatting    │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Core Components

#### 1. CLI Layer (`src/outlook_cli/cli.py`)
- **Responsibility**: User interface, command parsing, output formatting
- **Key Features**: 
  - Argument parsing with subcommands
  - Platform-aware help text
  - Color-coded error/success messages
  - Pagination display logic

#### 2. Service Layer (`src/outlook_cli/services/`)
- **EmailReader**: Retrieves emails from folders
- **EmailSearcher**: Implements search functionality with multiple criteria
- **EmailMover**: Handles email relocation between folders  
- **Paginator**: Provides consistent pagination across commands

#### 3. Adapter Layer (`src/outlook_cli/adapters/`)
- **OutlookAdapter** (interface): Defines contract for email operations
- **MockOutlookAdapter**: Provides realistic test data for development
- **PyWin32OutlookAdapter**: Real Outlook integration via COM interface

#### 4. Configuration (`src/outlook_cli/config/`)
- **AdapterFactory**: Creates appropriate adapters based on configuration
- **Platform Detection**: Automatic Windows/non-Windows adapter selection

#### 5. Models (`src/outlook_cli/models/`)
- **Email**: Validated data model using Pydantic
- **Type Safety**: Full type annotations throughout

#### 6. Utilities (`src/outlook_cli/utils/`)
- **Logging**: File-based logging for debugging
- **Error Handling**: Enhanced error messages with recovery suggestions

### Design Patterns

- **Factory Pattern**: `AdapterFactory` for adapter creation
- **Dependency Injection**: Services receive adapters without knowing their source
- **Strategy Pattern**: Different adapters implement same interface
- **Command Pattern**: CLI commands map to service operations

## 🧪 Testing Strategy

### Test Structure (220+ Tests)

```
tests/
├── test_cli.py                 # CLI interface tests
├── test_keyword_search.py      # TDD keyword search tests  
├── test_config_system.py       # Configuration system tests
├── test_email_reader.py        # Service layer tests
├── test_email_searcher.py      # Search functionality tests
├── test_email_mover.py         # Move operation tests
├── test_mock_adapter.py        # Mock adapter tests
└── test_models.py              # Data model validation tests
```

### Testing Philosophy

**Test-Driven Development (TDD)**: All features follow Red-Green-Refactor cycle:

1. **RED**: Write failing test that defines expected behavior
2. **GREEN**: Write minimal code to make test pass  
3. **REFACTOR**: Clean up implementation while keeping tests green

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with coverage
uv run pytest --cov=outlook_cli

# Run specific test file
uv run pytest tests/test_keyword_search.py

# Run tests verbosely
uv run pytest -v

# Run tests for specific functionality
uv run pytest -k "keyword"
```

### Test Categories

- **Unit Tests**: Individual component testing with mocks
- **Integration Tests**: Full command workflow testing
- **CLI Tests**: End-to-end command interface validation
- **Configuration Tests**: Platform-specific behavior validation

## 💻 Development Setup

### Prerequisites

- **Python 3.11+**
- **uv** (Python package manager)
- **Windows** (for real Outlook integration)

### Development Workflow

```bash
# 1. Set up development environment
git clone https://github.com/ozan-s/outlook-app.git
cd outlook-app
uv sync

# 2. Run tests to ensure everything works
uv run pytest

# 3. Make changes following TDD
# 4. Run tests again
uv run pytest

# 5. Code quality checks
uv run black .
uv run ruff check . --fix
```

### Cross-Platform Development

**Develop on Mac/Linux, Deploy on Windows**:

1. **Development**: Use mock adapter for fast iteration
2. **Testing**: Comprehensive test suite ensures Windows compatibility  
3. **Deployment**: Push to git, pull on Windows, use real adapter

### TDD Development Process

1. **Write failing test** that describes desired behavior
2. **Run test** to confirm it fails (RED)
3. **Write minimal code** to make test pass (GREEN)
4. **Refactor** for cleanliness while keeping tests green
5. **Commit** with clear TDD indicators in commit message

## 🚀 Deployment

### Windows Production Setup

```bash
# 1. Clone repository on Windows machine
git clone https://github.com/ozan-s/outlook-app.git
cd outlook-app

# 2. Install dependencies  
uv sync

# 3. Add to PATH for easy access
$env:PATH += ";C:\path\to\outlook-app\.venv\Scripts"

# 4. Use real adapter (automatic on Windows)
ocli read --folder Inbox
```

### Environment Configuration

```bash
# Optional: Set default adapter
$env:OUTLOOK_ADAPTER = "real"

# Optional: Set custom timeout values
$env:OUTLOOK_CLI_DEFAULT_TIMEOUT = "30"
$env:OUTLOOK_CLI_SEARCH_TIMEOUT = "60"
```

## 📁 Project Structure

```
outlook-app/
├── src/outlook_cli/           # Main application code
│   ├── adapters/             # Email data source adapters
│   │   ├── __init__.py
│   │   ├── outlook_adapter.py      # Base interface
│   │   ├── mock_adapter.py         # Development adapter
│   │   └── pywin32_adapter.py      # Windows Outlook adapter
│   ├── config/               # Configuration management
│   │   ├── __init__.py
│   │   └── adapter_factory.py     # Adapter creation logic
│   ├── models/               # Data models
│   │   ├── __init__.py
│   │   └── email.py               # Email data model
│   ├── services/             # Business logic layer
│   │   ├── __init__.py
│   │   ├── email_reader.py        # Email reading operations
│   │   ├── email_searcher.py      # Search functionality
│   │   ├── email_mover.py         # Email moving operations
│   │   └── paginator.py           # Pagination logic
│   ├── utils/                # Utility functions
│   │   ├── __init__.py
│   │   ├── logging_config.py      # Logging setup
│   │   └── errors.py              # Error handling
│   ├── __init__.py
│   └── cli.py                # CLI entry point
├── tests/                    # Comprehensive test suite
├── pyproject.toml           # Project configuration
├── uv.lock                  # Dependency lock file
├── CLAUDE.md               # Project knowledge base
└── README.md               # This file
```

## 🔧 Technical Details

### Email Model

```python
class Email(BaseModel):
    id: str                           # Unique Outlook identifier
    subject: str                      # Email subject line
    sender_email: EmailStr            # Sender's email address
    sender_name: str                  # Sender's display name
    recipient_emails: List[EmailStr]  # Recipients
    cc_emails: List[EmailStr]         # CC recipients
    bcc_emails: List[EmailStr]        # BCC recipients
    received_date: datetime           # When email was received
    body_text: str                    # Plain text content
    body_html: Optional[str]          # HTML content
    has_attachments: bool             # Attachment indicator
    attachment_count: int             # Number of attachments
    folder_path: str                  # Source folder
    is_read: bool                     # Read status
    importance: Literal["High", "Normal", "Low"]  # Priority level
```

### Windows COM Integration

The real adapter uses **pywin32** to interface with Outlook:

- **COM Objects**: Direct access to Outlook application and data
- **Exchange DN Resolution**: Converts internal addresses to SMTP format
- **Error Handling**: Graceful degradation when Outlook is unavailable
- **Thread Safety**: Proper COM object lifecycle management

### Search Implementation

- **Keyword Search**: OR logic across sender and subject fields
- **Field Search**: AND logic for specific criteria
- **Deduplication**: Removes duplicate results by email ID
- **Folder Scoping**: Search within specific folders or all folders

## 🐛 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|--------|----------|
| `python not found` | Python not in PATH | Use `uv run ocli` instead |
| `pywin32 not available` | Wrong platform | Use `--adapter mock` on non-Windows |
| `Folder not found` | Incorrect folder name | Check exact folder spelling in Outlook |
| `No module named 'outlook_cli'` | Import issue | Ensure you're in project directory |

### Debug Information

- **Log File**: `outlook_cli.log` (detailed operation logs)
- **Verbose Mode**: Use `-v` flag with pytest for detailed test output
- **Error Colors**: Red for errors, green for success messages

### Development Debugging

```bash
# Run single test with full output
uv run pytest tests/test_keyword_search.py -v -s

# Check test coverage
uv run pytest --cov=outlook_cli --cov-report=html

# Validate code quality
uv run black . && uv run ruff check . --fix
```

## 📈 Performance Characteristics

- **Startup Time**: ~200ms (mock), ~1-2s (real Outlook connection)
- **Search Performance**: Linear with email count, optimized with folder scoping
- **Memory Usage**: Minimal, processes emails in batches
- **Network**: No network calls (local Outlook integration only)

## 🔮 Future Expansion Areas

This solid foundation enables many expansion possibilities:

- **Advanced Search**: Date ranges, attachment types, priority levels
- **Bulk Operations**: Mass email management, rule-based processing
- **Integration APIs**: REST API, webhook support, external system integration  
- **Web Interface**: Browser-based UI for remote email management
- **AI Features**: Email summarization, smart categorization, sentiment analysis
- **Multi-Account**: Support for multiple Outlook profiles
- **Calendar Integration**: Meeting management, appointment scheduling

## 📄 License

[Add your license information here]

## 🤝 Contributing

This project follows strict TDD methodology:

1. **Write failing tests first** (RED phase)
2. **Write minimal implementation** (GREEN phase)  
3. **Refactor while maintaining tests** (REFACTOR phase)
4. **All commits should indicate TDD phase** in commit messages

For detailed development patterns and knowledge base, see `CLAUDE.md`.

---

**Built with Test-Driven Development principles and modern Python practices.**