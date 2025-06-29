# Outlook CLI Project Knowledge Base

## Core CLI Patterns

### Service-to-CLI Integration Pattern
- **Pattern**: Three-layer pattern with consistent error handling
- **Implementation**:
  ```python
  def handle_command(args):
      try:
          adapter = AdapterFactory.create_adapter()
          service = SomeService(adapter)
          results = service.get_data(args.param)
          paginator = Paginator(results, page_size=10)
          display_results(paginator)
      except ValueError:
          print(f"Error: {args.param} not found")
      except Exception as e:
          print(f"Error: {str(e)}")
  ```

### CLI Error Handling Strategy  
- **Pattern**: Convert service exceptions to user-friendly CLI messages
- `ValueError` from services → "Error: [specific context] not found"
- Generic exceptions → "Error: [action description]: [message]"
- Never expose raw service exceptions to CLI users

### Configuration System Pattern
- **Implementation**:
  ```python
  class AdapterFactory:
      @staticmethod
      def create_adapter(adapter_type: Optional[str] = None) -> OutlookAdapter:
          if adapter_type is None:
              adapter_type = os.environ.get('OUTLOOK_ADAPTER', 'mock')
          
          if adapter_type.lower() == 'mock':
              return MockOutlookAdapter()
          elif adapter_type.lower() == 'real':
              return PyWin32OutlookAdapter()
          else:
              raise ValueError(f"Invalid adapter type: '{adapter_type}'")
  ```

### CLI Argument Parser Pattern with Mutually Exclusive Groups
- **Problem**: Some CLI flags conflict (e.g., --is-read vs --is-unread, --limit vs --all)
- **Solution**: Use argparse mutually exclusive groups instead of custom validation
- **Implementation**:
  ```python
  # Create mutually exclusive group
  read_status_group = parser.add_mutually_exclusive_group()
  read_status_group.add_argument('--is-read', action='store_true')
  read_status_group.add_argument('--is-unread', action='store_true')
  
  # argparse automatically handles conflicts with clear error messages
  # No custom validation code needed
  ```

## Windows COM Interface Patterns

### Exchange Distinguished Name Resolution Pattern  
- **Problem**: Outlook COM returns Exchange DNs instead of SMTP addresses
- **Exchange DN Format**: `/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP/.../CN=RECIPIENTS/CN=user-identifier`
- **Solution**: Use `CreateRecipient` and `Resolve` methods to get SMTP addresses

### COM Collection Safety Pattern
- **Critical Facts**:
  - COM collections are 1-indexed (not 0-indexed)
  - Collection.Count may exceed actually accessible items
  - Always use try/except when iterating COM collections

### Exchange Email Address Extraction Pattern
- **Recipients**: Direct `AddressEntry.GetExchangeUser().PrimarySmtpAddress` works
- **Senders**: Require Exchange DN resolution via `CreateRecipient` method
- **Anti-Pattern**: `SendUsingAccount` shows mailbox owner, not actual sender

### Date Parser Design Pattern
- **Case Sensitivity Strategy**: Parse case-insensitive for most formats, preserve original string for case-sensitive patterns (e.g., `1M` months vs `1m` minutes)
- **Order-Dependent Parsing**: Check more specific patterns before generic ones (months `1M` before minutes `1m`, case-sensitive before case-insensitive)
- **Month Arithmetic**: Use proper calendar arithmetic with boundary handling rather than approximations (30-day months fail at month boundaries)
- **Timezone Consistency**: Always return UTC timezone-aware datetime objects regardless of input format

### Windows Subprocess Unicode Pattern
- **Problem**: Windows subprocess fails with UnicodeDecodeError when CLI output contains corporate email data with special characters
- **Solution**: Always use `encoding='utf-8'` and `errors='replace'` in subprocess.run calls
- **Implementation**:
  ```python
  result = subprocess.run(
      command,
      capture_output=True,
      text=True,
      timeout=60,
      encoding='utf-8',
      errors='replace'  # Replace invalid characters instead of crashing
  )
  ```
- **Corporate Environment**: Essential for Windows environments with Exchange data containing Unicode characters

## Development Guidelines
- Use `MockOutlookAdapter` for development and testing
- Use `PyWin32OutlookAdapter` for production Windows environment
- Always handle COM exceptions gracefully
- Test CLI commands with both adapters before deployment

## Development Tools and Best Practices

### UV Package Manager Commands
- NEVER use pip or python commands directly. ALWAYS use uv equivalents:
  - ❌ `pip install package` → ✅ `uv add package`
  - ❌ `python script.py` → ✅ `uv run python script.py`
  - ❌ `pip show package` → ✅ `uv list | grep package`
  - ❌ `pytest` → ✅ `uv run pytest`
  - ❌ `python -m pytest` → ✅ `uv run pytest`