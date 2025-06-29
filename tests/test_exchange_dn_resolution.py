"""Test Exchange DN resolution patterns for corporate environments.

This test validates the critical Exchange Distinguished Name resolution
functionality that's required in corporate Outlook environments.
"""

def test_exchange_dn_pattern_recognition():
    """Test that Exchange DN patterns are correctly identified."""
    
    test_cases = [
        {
            "email_address": "user@company.com",
            "is_exchange_dn": False,
            "description": "Normal SMTP address"
        },
        {
            "email_address": "/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP/CN=RECIPIENTS/CN=12345678-1234-1234-1234-123456789012-user",
            "is_exchange_dn": True,
            "description": "Standard Exchange DN format"
        },
        {
            "email_address": "/o=company/ou=exchange administrative group/cn=recipients/cn=user123",
            "is_exchange_dn": True,
            "description": "Lowercase Exchange DN"
        },
        {
            "email_address": "/O=COMPANY/OU=FIRST ADMINISTRATIVE GROUP/CN=RECIPIENTS/CN=DISPLAYNAME",
            "is_exchange_dn": True,
            "description": "Legacy Exchange DN format"
        },
        {
            "email_address": "",
            "is_exchange_dn": False,
            "description": "Empty string"
        },
        {
            "email_address": "not-an-email",
            "is_exchange_dn": False,
            "description": "Invalid format"
        }
    ]
    
    def is_exchange_dn(email_address: str) -> bool:
        """Check if email address is an Exchange DN."""
        return bool(email_address) and email_address.upper().startswith('/O=')
    
    for case in test_cases:
        result = is_exchange_dn(case["email_address"])
        print(f"Testing: {case['description']}")
        print(f"  Input: {case['email_address'][:50]}...")
        print(f"  Expected: {case['is_exchange_dn']}, Got: {result}")
        
        assert result == case["is_exchange_dn"], f"Failed for {case['description']}"


def test_exchange_dn_resolution_workflow():
    """Test the Exchange DN resolution workflow pattern."""
    
    class MockOutlook:
        """Mock Outlook namespace for testing DN resolution."""
        
        def __init__(self, resolution_success=True, smtp_result="user@company.com"):
            self.resolution_success = resolution_success
            self.smtp_result = smtp_result
        
        def CreateRecipient(self, exchange_dn):
            return MockRecipient(self.resolution_success, self.smtp_result)
    
    class MockRecipient:
        """Mock recipient object."""
        
        def __init__(self, resolution_success, smtp_result):
            self.resolution_success = resolution_success
            self.smtp_result = smtp_result
            if resolution_success:
                self.AddressEntry = MockAddressEntry(smtp_result)
            else:
                self.AddressEntry = None
        
        def Resolve(self):
            return self.resolution_success
    
    class MockAddressEntry:
        """Mock address entry object."""
        
        def __init__(self, smtp_result):
            self.smtp_result = smtp_result
        
        def GetExchangeUser(self):
            return MockExchangeUser(self.smtp_result)
    
    class MockExchangeUser:
        """Mock exchange user object."""
        
        def __init__(self, smtp_result):
            self.PrimarySmtpAddress = smtp_result
    
    def resolve_exchange_dn_to_smtp(namespace, exchange_dn: str) -> str:
        """Resolve Exchange DN to SMTP address using the pattern."""
        try:
            # Step 1: CreateRecipient with Exchange DN
            recipient = namespace.CreateRecipient(exchange_dn)
            
            # Step 2: Resolve the recipient
            if recipient and recipient.Resolve():
                
                # Step 3: Get AddressEntry
                if hasattr(recipient, 'AddressEntry') and recipient.AddressEntry:
                    address_entry = recipient.AddressEntry
                    
                    # Step 4: Get ExchangeUser
                    if hasattr(address_entry, 'GetExchangeUser'):
                        exchange_user = address_entry.GetExchangeUser()
                        
                        # Step 5: Get PrimarySmtpAddress
                        if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                            return exchange_user.PrimarySmtpAddress
            
            return None
            
        except Exception as e:
            print(f"Resolution failed: {e}")
            return None
    
    # Test successful resolution
    mock_outlook = MockOutlook(resolution_success=True, smtp_result="john.doe@company.com")
    exchange_dn = "/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP/CN=RECIPIENTS/CN=john.doe"
    
    result = resolve_exchange_dn_to_smtp(mock_outlook, exchange_dn)
    assert result == "john.doe@company.com", f"Expected successful resolution, got {result}"
    
    # Test failed resolution
    mock_outlook_fail = MockOutlook(resolution_success=False, smtp_result=None)
    result_fail = resolve_exchange_dn_to_smtp(mock_outlook_fail, exchange_dn)
    assert result_fail is None, f"Expected failed resolution, got {result_fail}"
    
    print("Exchange DN resolution workflow tests passed!")


def test_sender_extraction_with_exchange_dn():
    """Test sender email extraction that handles Exchange DN resolution."""
    
    def extract_sender_smtp(com_email_mock, namespace_mock):
        """Extract sender SMTP with Exchange DN resolution."""
        try:
            # Step 1: Try direct SMTP address first
            sender_email = getattr(com_email_mock, 'SenderEmailAddress', '')
            if sender_email and '@' in sender_email:
                return sender_email
            
            # Step 2: Handle Exchange DN resolution
            if sender_email and sender_email.startswith('/O='):
                # Use the resolution pattern
                recipient = namespace_mock.CreateRecipient(sender_email)
                if recipient and recipient.Resolve():
                    if hasattr(recipient, 'AddressEntry') and recipient.AddressEntry:
                        address_entry = recipient.AddressEntry
                        if hasattr(address_entry, 'GetExchangeUser'):
                            exchange_user = address_entry.GetExchangeUser()
                            if exchange_user and hasattr(exchange_user, 'PrimarySmtpAddress'):
                                return exchange_user.PrimarySmtpAddress
            
            # Step 3: Fallback to sender name
            sender_name = getattr(com_email_mock, 'SenderName', '')
            if sender_name and '@' in sender_name:
                return sender_name
            
            # Step 4: Final fallback
            return "unknown@unknown.com"
            
        except Exception:
            return "unknown@unknown.com"
    
    # Mock classes from previous test
    class MockOutlook:
        def __init__(self, resolution_success=True, smtp_result="user@company.com"):
            self.resolution_success = resolution_success
            self.smtp_result = smtp_result
        
        def CreateRecipient(self, exchange_dn):
            return MockRecipient(self.resolution_success, self.smtp_result)
    
    class MockRecipient:
        def __init__(self, resolution_success, smtp_result):
            self.resolution_success = resolution_success
            if resolution_success:
                self.AddressEntry = MockAddressEntry(smtp_result)
            else:
                self.AddressEntry = None
        
        def Resolve(self):
            return self.resolution_success
    
    class MockAddressEntry:
        def __init__(self, smtp_result):
            self.smtp_result = smtp_result
        
        def GetExchangeUser(self):
            return MockExchangeUser(self.smtp_result)
    
    class MockExchangeUser:
        def __init__(self, smtp_result):
            self.PrimarySmtpAddress = smtp_result
    
    class MockComEmail:
        def __init__(self, sender_email, sender_name="John Doe"):
            self.SenderEmailAddress = sender_email
            self.SenderName = sender_name
    
    # Test Case 1: Direct SMTP address (no resolution needed)
    email_smtp = MockComEmail("user@company.com")
    namespace = MockOutlook()
    result = extract_sender_smtp(email_smtp, namespace)
    assert result == "user@company.com", f"Direct SMTP failed: {result}"
    
    # Test Case 2: Exchange DN that resolves successfully
    exchange_dn = "/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP/CN=RECIPIENTS/CN=user123"
    email_dn = MockComEmail(exchange_dn)
    namespace_success = MockOutlook(resolution_success=True, smtp_result="resolved@company.com")
    result_dn = extract_sender_smtp(email_dn, namespace_success)
    assert result_dn == "resolved@company.com", f"Exchange DN resolution failed: {result_dn}"
    
    # Test Case 3: Exchange DN that fails to resolve (fallback to name)
    email_dn_fail = MockComEmail(exchange_dn, sender_name="fallback@company.com")
    namespace_fail = MockOutlook(resolution_success=False)
    result_fallback = extract_sender_smtp(email_dn_fail, namespace_fail)
    assert result_fallback == "fallback@company.com", f"Fallback failed: {result_fallback}"
    
    # Test Case 4: Complete failure (use unknown)
    email_no_data = MockComEmail("", sender_name="No Email")
    result_unknown = extract_sender_smtp(email_no_data, namespace_fail)
    assert result_unknown == "unknown@unknown.com", f"Unknown fallback failed: {result_unknown}"
    
    print("Sender extraction with Exchange DN tests passed!")


if __name__ == '__main__':
    test_exchange_dn_pattern_recognition()
    test_exchange_dn_resolution_workflow()
    test_sender_extraction_with_exchange_dn()
    print("All Exchange DN resolution tests passed!")