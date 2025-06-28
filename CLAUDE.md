# Outlook CLI Project Knowledge Base

## CLI Command Implementation Patterns

### Service-to-CLI Integration Pattern
- **Problem**: CLI commands need to integrate business logic services with user interface
- **Solution**: Three-layer pattern with consistent error handling
- **Implementation**:
  ```python
  def handle_command(args):
      try:
          # 1. Initialize services with adapter
          adapter = MockOutlookAdapter()  # or RealOutlookAdapter in production
          service = SomeService(adapter)
          
          # 2. Call service layer (business logic)
          results = service.get_data(args.param)
          
          # 3. Format for CLI output with pagination
          paginator = Paginator(results, page_size=10)
          display_results(paginator)
          
      except ValueError:
          # Convert service errors to user-friendly messages
          print(f"Error: {args.param} not found")
      except Exception as e:
          print(f"Error: {str(e)}")
  ```

### CLI Error Handling Strategy  
- **Problem**: Service layer exceptions should become user-friendly CLI messages
- **Solution**: Catch specific service exceptions and convert to helpful output
- **Pattern**:
  - `ValueError` from services → "Error: [specific context] not found"
  - Generic exceptions → "Error: [action description]: [message]"
  - Never expose raw service exceptions to CLI users

### CLI Testing Strategy
- **Problem**: CLI commands need comprehensive testing without external dependencies
- **Solution**: Three-layer test approach
- **Layers**:
  1. **Unit Tests**: Test CLI argument parsing and routing logic
  2. **Integration Tests**: Test complete command flow with MockOutlookAdapter
  3. **Manual Verification**: Actual CLI commands for final validation
- **MockOutlookAdapter**: Enables full CLI testing with realistic data

### Pagination Display Pattern
- **Problem**: Consistent pagination info display across all CLI commands
- **Solution**: Standardized format with item counting
- **Format**: `"Page X of Y, showing A-B of Z items"`
- **Implementation**:
  ```python
  page_info = paginator.get_page_info()
  start_item = (page_info["current_page"] - 1) * page_info["items_per_page"] + 1
  end_item = min(start_item + len(current_page) - 1, page_info["total_items"])
  print(f"Page {page_info['current_page']} of {page_info['total_pages']}, showing {start_item}-{end_item} of {page_info['total_items']} items")
  ```

### CLI Display Code Reuse Pattern
- **Problem**: Multiple CLI commands need identical result display formatting
- **Solution**: Extract display logic into reusable helper functions
- **Pattern**:
  ```python
  def _display_email_page(paginator, current_page):
      """Display paginated emails with consistent formatting."""
      # Pagination info + formatted item display
      # Called by multiple commands: read, find, etc.
  
  def handle_command(args):
      # Business logic...
      paginator = Paginator(results, page_size=10)
      current_page = paginator.get_current_page()
      _display_email_page(paginator, current_page)  # Reused display
  ```
- **Benefits**: Consistent UX, reduced code duplication, single source of formatting truth

## Windows COM Interface Integration Patterns

### File-Based Cross-Platform Development Pattern
- **Problem**: Developing Windows-only components (COM interfaces) from non-Windows development environment
- **Solution**: Generate test files on primary platform → Execute on target platform → Share results
- **Workflow**:
  ```python
  # On Mac (Claude development environment):
  def generate_windows_test(test_name, test_code):
      # Create complete test file with error handling
      # Commit and push to repository
  
  # On Windows (target environment):
  # Copy test file from repository
  # uv run python windows_test_xxx.py
  # Share output back to development environment
  ```
- **Benefits**: Faster than remote debugging, enables full TDD workflow, no environment setup complexity

### Exchange Distinguished Name Resolution Pattern  
- **Problem**: Outlook COM interface returns Exchange internal addresses instead of SMTP addresses
- **Exchange DN Format**: `/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP/.../CN=RECIPIENTS/CN=user-identifier`
- **Solution**: Multi-step resolution process
- **Implementation**:
  ```python
  def resolve_exchange_dn_to_smtp(outlook_app, exchange_dn):
      # Method 1: CreateRecipient and Resolve
      namespace = outlook_app.GetNamespace("MAPI")
      recipient = namespace.CreateRecipient(exchange_dn)
      if recipient and recipient.Resolve():
          if recipient.AddressEntry and hasattr(recipient.AddressEntry, 'GetExchangeUser'):
              exchange_user = recipient.AddressEntry.GetExchangeUser()
              if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                  return exchange_user.PrimarySmtpAddress
      return None
  ```

### COM Collection Safety Pattern
- **Problem**: COM collections have different indexing and bounds behavior than Python
- **Critical Differences**:
  - COM collections are 1-indexed (not 0-indexed)
  - Collection.Count may exceed actually accessible items
  - Array bounds exceptions common
- **Solution**: Safe iteration with bounds checking
- **Implementation**:
  ```python
  def safe_com_iteration(com_collection):
      results = []
      if hasattr(com_collection, 'Count') and com_collection.Count > 0:
          for i in range(1, com_collection.Count + 1):  # 1-indexed
              try:
                  item = com_collection[i]
                  # Process item safely
                  results.append(process_item(item))
              except (IndexError, Exception):
                  # Skip inaccessible items gracefully
                  continue
      return results
  ```

### Exchange Email Address Extraction Pattern
- **Problem**: Different methods needed for sender vs recipient SMTP address extraction
- **Recipients**: Direct `AddressEntry.GetExchangeUser().PrimarySmtpAddress` works
- **Senders**: Require Exchange DN resolution (CreateRecipient method)
- **Anti-Pattern**: `SendUsingAccount` shows mailbox owner, not actual sender
- **Implementation**:
  ```python
  def extract_sender_smtp(outlook_email):
      # Get Exchange DN from SenderEmailAddress
      sender_dn = outlook_email.SenderEmailAddress
      if sender_dn and sender_dn.startswith('/O='):
          return resolve_exchange_dn_to_smtp(outlook_app, sender_dn)
      return None
  
  def extract_recipient_smtp(recipient):
      # Direct method works for recipients
      if recipient.AddressEntry and hasattr(recipient.AddressEntry, 'GetExchangeUser'):
          exchange_user = recipient.AddressEntry.GetExchangeUser()
          if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
              return exchange_user.PrimarySmtpAddress
      return None
  ```

## Development Guidelines
- When you generate a Windows only test, immediately git commit and git push.