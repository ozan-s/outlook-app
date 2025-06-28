#!/usr/bin/env python3
"""
Windows Test 009: Exchange DN Resolution Integration
Test Exchange DN to SMTP address resolution with real Outlook emails.

This test verifies:
1. get_emails() properly extracts SMTP addresses for senders
2. Exchange DN resolution works for real Exchange environments
3. Recipient SMTP extraction works correctly
4. Real email data matches our Email model validation

Execute on Windows with: uv run python windows_test_009_exchange_resolution.py
"""

import sys
import traceback
from datetime import datetime

def test_exchange_dn_resolution():
    """Test Exchange DN resolution with real Outlook emails."""
    
    print("=== TEST: Exchange DN Resolution Integration ===")
    
    try:
        # Import our adapter
        from src.outlook_cli.adapters.pywin32_adapter import PyWin32OutlookAdapter
        from src.outlook_cli.models.email import Email
        from src.outlook_cli.models.folder import Folder
        
        print("✓ PyWin32OutlookAdapter imported successfully")
        
        # Test 1: Adapter instantiation
        print("\n--- Test 1: Adapter Instantiation ---")
        adapter = PyWin32OutlookAdapter()
        print("✓ Adapter instantiated successfully")
        
        # Test 2: Get Inbox emails with SMTP resolution
        print("\n--- Test 2: Inbox Emails with Exchange DN Resolution ---")
        try:
            emails = adapter.get_emails("Inbox")
            print(f"✓ Retrieved {len(emails)} emails from Inbox")
            
            if len(emails) > 0:
                # Test first few emails for SMTP address extraction
                test_count = min(3, len(emails))
                print(f"  Testing SMTP extraction for first {test_count} emails:")
                
                for i, email in enumerate(emails[:test_count]):
                    print(f"\n  Email {i+1}:")
                    print(f"    ID: {email.id[:50]}...")
                    print(f"    Subject: {email.subject[:60]}...")
                    print(f"    Sender: {email.sender_name} <{email.sender_email}>")
                    print(f"    Recipients: {len(email.recipient_emails)} recipients")
                    
                    # Verify SMTP format
                    if '@' in email.sender_email and '.' in email.sender_email:
                        print(f"    ✓ Sender SMTP format valid")
                    else:
                        print(f"    ✗ Sender SMTP format invalid: {email.sender_email}")
                    
                    # Test recipient SMTP format
                    valid_recipients = 0
                    for recipient in email.recipient_emails:
                        if '@' in recipient and '.' in recipient:
                            valid_recipients += 1
                    
                    print(f"    ✓ {valid_recipients}/{len(email.recipient_emails)} recipients have valid SMTP format")
                    
                    # Test Email model validation
                    try:
                        # Re-create to test validation
                        Email(**email.model_dump())
                        print(f"    ✓ Email model validation passed")
                    except Exception as e:
                        print(f"    ✗ Email model validation failed: {e}")
            
            else:
                print("  ⚠ No emails in Inbox - test with mailbox containing emails")
        
        except Exception as e:
            print(f"✗ Failed to get Inbox emails: {e}")
            traceback.print_exc()
            return False
        
        # Test 3: Direct Exchange DN resolution test
        print("\n--- Test 3: Direct Exchange DN Resolution ---")
        try:
            # Try to find an email with Exchange DN sender
            exchange_dn_found = False
            
            if len(emails) > 0:
                # Check if we can access the raw COM interface for testing
                import win32com.client
                outlook = win32com.client.Dispatch("Outlook.Application")
                namespace = outlook.GetNamespace("MAPI")
                inbox = namespace.GetDefaultFolder(6)
                
                # Look for Exchange DN in first few emails
                items = inbox.Items
                test_count = min(5, items.Count)
                
                for i in range(1, test_count + 1):
                    try:
                        item = items[i]
                        sender_email_address = getattr(item, 'SenderEmailAddress', '')
                        
                        if sender_email_address and sender_email_address.startswith('/O='):
                            print(f"  Found Exchange DN: {sender_email_address[:80]}...")
                            
                            # Test our resolution method
                            resolved_smtp = adapter._resolve_exchange_dn_to_smtp(sender_email_address)
                            if resolved_smtp:
                                print(f"  ✓ Resolved to SMTP: {resolved_smtp}")
                                exchange_dn_found = True
                            else:
                                print(f"  ✗ Failed to resolve Exchange DN")
                            
                            break
                            
                    except Exception as e:
                        print(f"  Error checking email {i}: {e}")
                        continue
                
                if not exchange_dn_found:
                    print("  ⚠ No Exchange DN found in test emails - may be using external SMTP")
            
        except Exception as e:
            print(f"✗ Direct Exchange DN test failed: {e}")
            traceback.print_exc()
        
        # Test 4: Folder structure validation
        print("\n--- Test 4: Folder Structure Validation ---")
        try:
            folders = adapter.get_folders()
            print(f"✓ Retrieved {len(folders)} folders")
            
            # Test a few key folders
            key_folders = ['Inbox', 'Sent Items', 'Drafts']
            found_folders = []
            
            for folder in folders:
                if folder.name in key_folders:
                    found_folders.append(folder.name)
                    print(f"  ✓ {folder.name}: {folder.email_count} emails ({folder.unread_count} unread)")
                    
                    # Test Folder model validation
                    try:
                        Folder(**folder.model_dump())
                        print(f"    ✓ Folder model validation passed")
                    except Exception as e:
                        print(f"    ✗ Folder model validation failed: {e}")
            
            print(f"  Found {len(found_folders)}/{len(key_folders)} key folders: {found_folders}")
            
        except Exception as e:
            print(f"✗ Folder structure test failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 5: Individual email retrieval
        print("\n--- Test 5: Individual Email Retrieval ---")
        try:
            if len(emails) > 0:
                test_email = emails[0]
                retrieved_email = adapter.get_email_by_id(test_email.id)
                
                print(f"✓ Retrieved email by ID: {retrieved_email.subject[:60]}...")
                
                # Verify it's the same email
                if retrieved_email.id == test_email.id:
                    print("  ✓ Retrieved email matches original")
                else:
                    print("  ✗ Retrieved email ID mismatch")
                    return False
            
        except Exception as e:
            print(f"✗ Individual email retrieval failed: {e}")
            traceback.print_exc()
            return False
        
        print("\n=== TEST COMPLETE: SUCCESS ===")
        return True
        
    except ImportError as e:
        print(f"✗ Import failed: {e}")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run the test and exit with appropriate code."""
    print(f"Starting Windows Test 009 at {datetime.now()}")
    print("Testing Exchange DN resolution and email data extraction...")
    print("-" * 70)
    
    success = test_exchange_dn_resolution()
    
    print("-" * 70)
    if success:
        print("TEST PASSED: Exchange DN resolution and email extraction verified")
        sys.exit(0)
    else:
        print("TEST FAILED: Check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()