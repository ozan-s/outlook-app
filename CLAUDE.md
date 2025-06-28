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