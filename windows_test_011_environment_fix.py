#!/usr/bin/env python3
"""
Windows Test 011: Environment Setup Fix
Fix Python path to allow importing outlook_cli module on Windows.

This test:
1. Adds src directory to Python path
2. Verifies all imports work
3. Tests basic PyWin32OutlookAdapter functionality

Execute on Windows with: uv run python windows_test_011_environment_fix.py
"""

import sys
import os
import traceback
from datetime import datetime

# Add src directory to Python path to allow importing outlook_cli
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

print(f"Added to Python path: {src_dir}")

def test_windows_environment_and_adapter():
    """Test Windows environment setup and basic adapter functionality."""
    
    print("=== TEST: Windows Environment & PyWin32OutlookAdapter ===")
    
    try:
        # Test 1: Import verification
        print("\n--- Test 1: Import Verification ---")
        
        try:
            from outlook_cli.adapters.pywin32_adapter import PyWin32OutlookAdapter
            print("✓ PyWin32OutlookAdapter imported successfully")
        except ImportError as e:
            print(f"✗ PyWin32OutlookAdapter import failed: {e}")
            return False
            
        try:
            from outlook_cli.models.email import Email
            from outlook_cli.models.folder import Folder
            print("✓ Email and Folder models imported successfully")
        except ImportError as e:
            print(f"✗ Model imports failed: {e}")
            return False
            
        try:
            from outlook_cli.services.email_reader import EmailReader
            from outlook_cli.services.email_searcher import EmailSearcher
            from outlook_cli.services.email_mover import EmailMover
            print("✓ Service classes imported successfully")
        except ImportError as e:
            print(f"✗ Service imports failed: {e}")
            return False
        
        # Test 2: Windows COM availability
        print("\n--- Test 2: Windows COM Availability ---")
        try:
            import win32com.client
            from pywintypes import com_error
            print("✓ pywin32 modules available")
            
            # Test Outlook COM connection
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            print("✓ Outlook COM connection successful")
            print(f"  Namespace: {namespace}")
            
        except ImportError as e:
            print(f"✗ pywin32 not available: {e}")
            return False
        except com_error as e:
            print(f"✗ Outlook COM connection failed: {e}")
            print("  Ensure Outlook is running and accessible")
            return False
        
        # Test 3: PyWin32OutlookAdapter instantiation
        print("\n--- Test 3: PyWin32OutlookAdapter Instantiation ---")
        try:
            adapter = PyWin32OutlookAdapter()
            print("✓ PyWin32OutlookAdapter instantiated successfully")
        except Exception as e:
            print(f"✗ Adapter instantiation failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 4: Basic folder access
        print("\n--- Test 4: Basic Folder Access ---")
        try:
            folders = adapter.get_folders()
            print(f"✓ Retrieved {len(folders)} folders from Outlook")
            
            if len(folders) > 0:
                # Show first few folders
                print("  Sample folders:")
                for i, folder in enumerate(folders[:5]):
                    print(f"    {i+1}. {folder.path} ({folder.email_count} emails, {folder.unread_count} unread)")
                
                # Verify folder structure
                first_folder = folders[0]
                print(f"  ✓ First folder type: {type(first_folder)}")
                print(f"  ✓ First folder has required fields: path={first_folder.path}, name={first_folder.name}")
                
            else:
                print("  ⚠ No folders found - check Outlook configuration")
        
        except Exception as e:
            print(f"✗ Folder access failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 5: Basic email access
        print("\n--- Test 5: Basic Email Access ---")
        try:
            # Try to get emails from Inbox
            emails = adapter.get_emails("Inbox")
            print(f"✓ Retrieved {len(emails)} emails from Inbox")
            
            if len(emails) > 0:
                # Show first email details
                first_email = emails[0]
                print(f"  First email: '{first_email.subject[:50]}...'")
                print(f"  From: {first_email.sender_name} <{first_email.sender_email}>")
                print(f"  Recipients: {len(first_email.recipient_emails)}")
                print(f"  Date: {first_email.received_date}")
                print(f"  Read: {first_email.is_read}")
                print(f"  Attachments: {first_email.has_attachments} ({first_email.attachment_count})")
                
                # Verify email structure
                print(f"  ✓ Email type: {type(first_email)}")
                print(f"  ✓ Email ID: {first_email.id[:30]}...")
                
                # Test SMTP addresses
                sender_valid = '@' in first_email.sender_email and '.' in first_email.sender_email
                print(f"  ✓ Sender SMTP format: {sender_valid} ({first_email.sender_email})")
                
                recipients_valid = all('@' in r and '.' in r for r in first_email.recipient_emails)
                print(f"  ✓ Recipients SMTP format: {recipients_valid}")
                
            else:
                print("  ⚠ No emails in Inbox - test with mailbox containing emails")
        
        except Exception as e:
            print(f"✗ Email access failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 6: Service integration
        print("\n--- Test 6: Service Integration ---")
        try:
            # Test EmailReader service
            reader = EmailReader(adapter)
            service_emails = reader.get_emails_from_folder("Inbox")
            print(f"✓ EmailReader service: {len(service_emails)} emails")
            
            # Test EmailSearcher service  
            searcher = EmailSearcher(adapter)
            if len(service_emails) > 0:
                # Search by first email's sender
                test_sender = service_emails[0].sender_email
                if test_sender != "unknown@unknown.com":
                    search_results = searcher.search_emails(sender=test_sender, folder_path="Inbox")
                    print(f"✓ EmailSearcher service: {len(search_results)} results for sender '{test_sender}'")
                else:
                    print("✓ EmailSearcher service: Available (no valid sender to test)")
            
            # Test EmailMover service (just instantiation, don't actually move emails)
            mover = EmailMover(adapter)
            print("✓ EmailMover service: Instantiated successfully")
            
        except Exception as e:
            print(f"✗ Service integration failed: {e}")
            traceback.print_exc()
            return False
        
        print("\n=== TEST COMPLETE: SUCCESS ===")
        print("Windows environment is properly configured!")
        print("PyWin32OutlookAdapter is working with real Outlook data!")
        return True
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run the test and exit with appropriate code."""
    print(f"Starting Windows Test 011 at {datetime.now()}")
    print("Testing Windows environment setup and PyWin32OutlookAdapter...")
    print("-" * 70)
    
    success = test_windows_environment_and_adapter()
    
    print("-" * 70)
    if success:
        print("TEST PASSED: Windows environment and PyWin32OutlookAdapter working!")
        print("\nNow you can test CLI commands:")
        print("1. Modify CLI to use PyWin32OutlookAdapter instead of MockOutlookAdapter")
        print("2. Test: uv run outlook-cli read")
        print("3. Test: uv run outlook-cli find --sender @company.com")
        print("4. Test: uv run outlook-cli open <email_id>")
        sys.exit(0)
    else:
        print("TEST FAILED: Check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()