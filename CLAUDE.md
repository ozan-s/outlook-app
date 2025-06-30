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

### Progressive Filtering Pattern
- **Problem**: Multiple filter criteria need to be applied efficiently with maintainable code
- **Solution**: Apply filters in sequence using dedicated filter methods, allowing each to operate on the result of the previous
- **Implementation**:
  ```python
  def search_with_filters(self, emails, **filters):
      filtered_emails = emails
      
      # Apply each filter progressively
      filtered_emails = self.filter_by_read_status(filtered_emails, filters.get('is_read'), filters.get('is_unread'))
      filtered_emails = self.filter_by_attachments(filtered_emails, filters.get('has_attachment'), filters.get('no_attachment'))
      filtered_emails = self.filter_by_importance(filtered_emails, filters.get('importance'))
      filtered_emails = self.filter_by_exclusions(filtered_emails, filters.get('not_sender'), filters.get('not_subject'))
      
      return filtered_emails
  ```
- **Benefits**: Each filter method is testable in isolation, easy to add/remove filters, clear separation of concerns

### Service Extraction Pattern for Code Deduplication
- **Problem**: Identical logic blocks duplicated across CLI handlers (date parsing, parameter building, common processing)
- **Solution**: Extract shared logic into dedicated service classes with single responsibilities
- **Implementation**:
  ```python
  # Extract parameter parsing
  class FilterParsingService:
      def parse_date_filters(self, args) -> Tuple[datetime, datetime]:
          # Centralized date parsing logic
      
      def build_search_params(self, args, since_date, until_date) -> Dict:
          # Centralized parameter building
  
  # Extract common processing patterns  
  class CommandProcessingService:
      def process_email_command(self, args, search_params, operation_name):
          # Common pattern: search -> sort -> paginate -> return
  ```
- **Benefits**: Eliminates duplication, improves testability, maintains single responsibility principle, reduces maintenance burden

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

## Performance and Monitoring Patterns

### Enterprise CLI Monitoring Pattern
- **Pattern**: Three-component monitoring infrastructure for enterprise applications
- **Implementation**:
  ```python
  # Module-level singletons for consistent monitoring
  performance_monitor = PerformanceMonitor()
  audit_logger = AuditLogger()
  resource_monitor = ResourceMonitor()
  
  def handle_command(args):
      performance_monitor.start_monitoring("command_name")
      try:
          resource_monitor.check_memory_usage()
          # ... command logic ...
          metrics = performance_monitor.stop_monitoring("command_name")
          
          audit_logger.log_filter_operation(
              operation="command",
              filters=params,
              user=os.environ.get('USER', 'unknown'),
              result_count=len(results)
          )
      except ResourceExceededError as e:
          print(f"Error: {str(e)}")
  ```

### Progressive Filtering Optimization Pattern
- **Problem**: Complex filter operations need performance optimization with minimal code changes
- **Solution**: Apply most selective filters first using estimated selectivity scoring
- **Implementation**:
  ```python
  class ProgressiveFilterOptimizer:
      def apply_filters_progressively(self, emails, filters):
          # Calculate selectivity: sender(0.05) > importance(0.1) > folder(0.8)
          selectivities = self.calculate_filter_selectivity(filters)
          ordered = self.order_filters_by_selectivity(selectivities)
          
          filtered_emails = emails
          for selectivity in ordered:
              filtered_emails = self._apply_single_filter(filtered_emails, ...)
              if not filtered_emails:  # Early termination
                  break
          return filtered_emails
  ```

### Environment-Configurable Resource Limits Pattern
- **Pattern**: Resource protection with environment variable configuration
- **Implementation**:
  ```python
  class ResourceLimits:
      def __init__(self):
          self.max_memory_mb = float(os.environ.get('APP_MAX_MEMORY_MB', '1024'))
          self.max_processing_time = float(os.environ.get('APP_MAX_PROCESSING_TIME', '300'))
          self.max_result_count = int(os.environ.get('APP_MAX_RESULT_COUNT', '50000'))
  
  # Usage: Configurable via environment without code changes
  # OUTLOOK_CLI_MAX_MEMORY_MB=2048 OUTLOOK_CLI_MAX_PROCESSING_TIME=120 ocli read --folder Inbox
  ```

### Performance Baseline and Regression Detection Pattern
- **Pattern**: Automated performance regression detection with tolerance thresholds
- **Implementation**:
  ```python
  baseline = PerformanceBaseline(threshold_factor=1.2)  # 20% tolerance
  
  # Record baseline during development/testing
  baseline.record_baseline("operation", duration=1.0, memory=100.0)
  
  # Check for regression in production/CI
  is_regression = baseline.check_regression("operation", 
                                          current_duration=1.3,  # OK: 30% increase < 20% threshold
                                          current_memory=130.0)
  ```

## Development Tools and Best Practices

### UV Package Manager Commands
- NEVER use pip or python commands directly. ALWAYS use uv equivalents:
  - ❌ `pip install package` → ✅ `uv add package`
  - ❌ `python script.py` → ✅ `uv run python script.py`
  - ❌ `pip show package` → ✅ `uv list | grep package`
  - ❌ `pytest` → ✅ `uv run pytest`
  - ❌ `python -m pytest` → ✅ `uv run pytest`