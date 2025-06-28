# Milestone 013: Windows pywin32 Adapter Implementation

## Objective
Implement real OutlookAdapter using pywin32 COM interface with Exchange DN resolution for production use.

## Current State Analysis

**Dependency Check**: ✅ All CLI commands (read, find, move, open) working with MockOutlookAdapter  
**Interface Contract**: Complete OutlookAdapter abstract class at `src/outlook_cli/adapters/outlook_adapter.py`  
**Research Complete**: Exchange DN resolution patterns proven in `windows_test_007_resolve_exchange_addresses.py`  
**Development Workflow**: File-based Windows testing approach established and validated  

**Exchange Integration Complexity Documented**:
- Exchange Distinguished Name format: `/O=EXCHANGELABS/.../CN=RECIPIENTS/CN=user-identifier`
- Sender SMTP resolution: `CreateRecipient(exchange_dn).Resolve()` → `GetExchangeUser().PrimarySmtpAddress`  
- Recipient SMTP extraction: `AddressEntry.GetExchangeUser().PrimarySmtpAddress`
- COM collections are 1-indexed with array bounds safety required
- Global Address List access enables DN-to-SMTP resolution

**Existing Interface Methods to Implement**:
- `get_folders()` → `List[Folder]`
- `get_folder_info(folder_path: str)` → `Folder`  
- `get_emails(folder_path: str)` → `List[Email]`
- `move_email(email_id: str, target_folder: str)` → `bool`
- `get_email_by_id(email_id: str)` → `Email`

## Success Criteria
- [ ] Real Windows adapter class `PyWin32OutlookAdapter` implements all interface methods
- [ ] Exchange DN resolution works for sender and recipient SMTP extraction
- [ ] All CLI commands work with real Outlook data (read, find, move, open)
- [ ] COM interface safety: 1-indexed collections, array bounds checking
- [ ] Real email data matches model structure used by MockAdapter

## Implementation Approach

### TDD Sequence Using File-Based Development
1. **Test**: Create `windows_test_008_real_adapter.py` to verify basic adapter instantiation and folder access
2. **Test**: Verify `get_folders()` returns actual Outlook folder structure  
3. **Test**: Verify `get_emails()` with Exchange DN resolution for real sender/recipient addresses
4. **Test**: Verify `move_email()` and `get_email_by_id()` with real Outlook operations
5. **Test**: Integration test - CLI commands using real adapter with actual Outlook data

### Implementation Details

**File Structure**:
```python
# src/outlook_cli/adapters/pywin32_adapter.py
class PyWin32OutlookAdapter(OutlookAdapter):
    def __init__(self):
        # Connect to Outlook via win32com.client
    
    def _resolve_exchange_dn_to_smtp(self, exchange_dn: str) -> str:
        # Proven resolution method from research
    
    def _extract_real_sender_smtp(self, outlook_email) -> str:
        # Exchange DN resolution for senders
    
    def _extract_recipient_smtp(self, recipient) -> str:
        # Direct method for recipients
```

**Exchange DN Resolution Pattern** (from research):
```python
# Senders: Exchange DN → SMTP
namespace = outlook_app.GetNamespace("MAPI")
recipient = namespace.CreateRecipient(exchange_dn)
if recipient.Resolve() and recipient.AddressEntry:
    exchange_user = recipient.AddressEntry.GetExchangeUser()
    return exchange_user.PrimarySmtpAddress

# Recipients: Direct method
if recipient.AddressEntry and hasattr(recipient.AddressEntry, 'GetExchangeUser'):
    exchange_user = recipient.AddressEntry.GetExchangeUser()
    return exchange_user.PrimarySmtpAddress
```

**COM Safety Pattern**:
```python
# 1-indexed iteration with bounds checking
for i in range(1, collection.Count + 1):
    try:
        item = collection[i]
        # Process item
    except (IndexError, Exception):
        continue  # Skip inaccessible items
```

### Integration Points
- **pywin32**: `win32com.client.Dispatch("Outlook.Application")`
- **COM Objects**: Outlook namespace, folders, emails, recipients  
- **Data Mapping**: Outlook COM properties → Email/Folder model fields
- **Error Handling**: COM exceptions → ValueError for CLI layer

### File-Based Development Workflow
1. **Generate**: Create Windows test file on Mac with adapter implementation
2. **Execute**: Copy to Windows → `uv run python windows_test_xxx.py`
3. **Iterate**: Share results → Refine implementation → Repeat
4. **Integrate**: Final adapter implementation in src/outlook_cli/adapters/

## Evidence for Completion
- [ ] All Windows test files pass with real Outlook data
- [ ] CLI commands work: `uv run outlook-cli read` shows real emails with proper SMTP addresses
- [ ] Move operation: `uv run outlook-cli move <email_id> "Test Folder"` actually moves email in Outlook
- [ ] Search functionality: `uv run outlook-cli find --sender user@domain.com` finds real emails
- [ ] Integration test: Complete CLI workflow with real Outlook environment

**Manual Verification Commands**:
```bash
# Test real adapter functionality
uv run outlook-cli read  # Shows real inbox emails
uv run outlook-cli find --sender "@company.com"  # Finds company emails  
uv run outlook-cli move inbox-001 "Archive"  # Moves real email
uv run outlook-cli open inbox-002  # Shows full real email content
```

## Notes
- **File-based development**: Proven approach for Windows-only COM interface development
- **Exchange complexity**: DN resolution adds complexity but research complete and patterns proven
- **Safety first**: COM collections require 1-indexed iteration and bounds checking
- **Error handling**: Convert COM exceptions to ValueError for consistent CLI experience
- **No scope creep**: Focus on implementing existing interface contract with real data

## Estimated Time: 6 hours
- Windows test file generation and refinement: 2 hours
- Real adapter implementation with Exchange DN resolution: 3 hours  
- Integration testing and CLI verification: 1 hour

**Dependencies**: All previous milestones complete ✅  
**Next**: Milestone 014 (Error handling + user feedback) after real adapter integration confirmed