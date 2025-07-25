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

## Development Guidelines
- Use `MockOutlookAdapter` for development and testing
- Use `PyWin32OutlookAdapter` for production Windows environment
- Always handle COM exceptions gracefully
- Test CLI commands with both adapters before deployment