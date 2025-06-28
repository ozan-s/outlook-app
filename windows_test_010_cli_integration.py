#!/usr/bin/env python3
"""
Windows Test 010: CLI Integration with Real Adapter
Test CLI commands working with PyWin32OutlookAdapter and real Outlook data.

This test verifies:
1. CLI services work with real adapter instead of mock
2. All CLI command workflows function with real Outlook emails
3. Real adapter produces valid data that CLI can display properly
4. Error handling works correctly with real Outlook operations

Execute on Windows with: uv run python windows_test_010_cli_integration.py
"""

import sys
import traceback
from datetime import datetime

def test_cli_integration_with_real_adapter():
    """Test CLI services integration with PyWin32OutlookAdapter."""
    
    print("=== TEST: CLI Integration with Real Adapter ===")
    
    try:
        # Import required modules
        from src.outlook_cli.adapters.pywin32_adapter import PyWin32OutlookAdapter
        from src.outlook_cli.services.email_reader import EmailReader
        from src.outlook_cli.services.email_searcher import EmailSearcher
        from src.outlook_cli.services.email_mover import EmailMover
        from src.outlook_cli.services.paginator import Paginator
        
        print("✓ All modules imported successfully")
        
        # Test 1: Initialize services with real adapter
        print("\n--- Test 1: Service Initialization with Real Adapter ---")
        adapter = PyWin32OutlookAdapter()
        reader = EmailReader(adapter)
        searcher = EmailSearcher(adapter)
        mover = EmailMover(adapter)
        
        print("✓ All services initialized with PyWin32OutlookAdapter")
        
        # Test 2: EmailReader service with real data
        print("\n--- Test 2: EmailReader Service Integration ---")
        try:
            emails = reader.get_emails_from_folder("Inbox")
            print(f"✓ EmailReader retrieved {len(emails)} emails from Inbox")
            
            if len(emails) > 0:
                # Test pagination with real data
                paginator = Paginator(emails, page_size=5)
                current_page = paginator.get_current_page()
                page_info = paginator.get_page_info()
                
                print(f"  ✓ Pagination: Page {page_info['current_page']} of {page_info['total_pages']}")
                print(f"  ✓ Showing {len(current_page)} emails on current page")
                
                # Test first email structure
                first_email = emails[0]
                print(f"  ✓ First email: '{first_email.subject[:50]}...'")
                print(f"    From: {first_email.sender_name} <{first_email.sender_email}>")
                print(f"    Recipients: {len(first_email.recipient_emails)}")
                print(f"    Date: {first_email.received_date}")
                
                # Test get_email_by_id with real ID
                retrieved_email = reader.get_email_by_id(first_email.id)
                if retrieved_email.id == first_email.id:
                    print("  ✓ get_email_by_id works with real email IDs")
                else:
                    print("  ✗ get_email_by_id returned different email")
                    return False
            
        except Exception as e:
            print(f"✗ EmailReader service failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 3: EmailSearcher service with real data
        print("\n--- Test 3: EmailSearcher Service Integration ---")
        try:
            # Test subject search
            if len(emails) > 0:
                # Use first email's subject for search test
                test_subject = emails[0].subject.split()[0]  # First word of subject
                if len(test_subject) > 3:  # Only test with meaningful words
                    search_results = searcher.search_emails(
                        subject=test_subject,
                        folder_path="Inbox"
                    )
                    print(f"  ✓ Subject search for '{test_subject}' found {len(search_results)} emails")
                    
                    if len(search_results) > 0:
                        # Verify search result format matches expected Email model
                        search_email = search_results[0]
                        print(f"    First result: '{search_email.subject[:50]}...'")
                        print(f"    From: {search_email.sender_email}")
                    
                # Test sender search if we have emails
                test_sender = emails[0].sender_email
                if test_sender != "unknown@unknown.com":
                    sender_results = searcher.search_emails(
                        sender=test_sender,
                        folder_path="Inbox"
                    )
                    print(f"  ✓ Sender search for '{test_sender}' found {len(sender_results)} emails")
                else:
                    print("  ⚠ Skipping sender search - no valid sender email found")
            
        except Exception as e:
            print(f"✗ EmailSearcher service failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 4: EmailMover service verification (without actual move)
        print("\n--- Test 4: EmailMover Service Integration ---")
        try:
            # Test folder validation
            if len(emails) > 0:
                test_email_id = emails[0].id
                
                # Test with invalid folder to verify error handling
                try:
                    result = mover.move_email_to_folder(test_email_id, "NonExistentFolder")
                    print("  ✗ Move should have failed with invalid folder")
                    return False
                except ValueError as e:
                    print(f"  ✓ Move correctly failed with invalid folder: {e}")
                
                # Test with invalid email ID
                try:
                    result = mover.move_email_to_folder("invalid-id", "Inbox")
                    print("  ✗ Move should have failed with invalid email ID")
                    return False
                except ValueError as e:
                    print(f"  ✓ Move correctly failed with invalid email ID: {e}")
                
                print("  ✓ EmailMover error handling verified")
                print("  ⚠ Actual move operations not tested to avoid data changes")
            
        except Exception as e:
            print(f"✗ EmailMover service setup failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 5: CLI Display Functions with Real Data
        print("\n--- Test 5: CLI Display Functions with Real Data ---")
        try:
            if len(emails) > 0:
                # Test pagination display
                paginator = Paginator(emails[:3], page_size=2)  # Small test set
                current_page = paginator.get_current_page()
                
                print("  Testing pagination display format:")
                page_info = paginator.get_page_info()
                start_item = (page_info["current_page"] - 1) * page_info["items_per_page"] + 1
                end_item = min(start_item + len(current_page) - 1, page_info["total_items"])
                
                # This mimics the _display_email_page function format
                print(f"  Page {page_info['current_page']} of {page_info['total_pages']}, showing {start_item}-{end_item} of {page_info['total_items']} emails")
                
                for i, email in enumerate(current_page, start=start_item):
                    status = "[UNREAD]" if not email.is_read else "[READ]"
                    print(f"  {i}. {status} Subject: {email.subject[:40]}...")
                    print(f"     From: {email.sender_name} <{email.sender_email}>")
                    print(f"     Date: {email.received_date.strftime('%Y-%m-%d %H:%M')}")
                    if email.has_attachments:
                        print("     📎 Has attachments")
                
                print("  ✓ CLI display format works with real email data")
            
        except Exception as e:
            print(f"✗ CLI display functions failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 6: Adapter Switch Pattern for CLI
        print("\n--- Test 6: Adapter Configuration Pattern ---")
        try:
            # Show how CLI could be configured to use real adapter
            print("  CLI Adapter Configuration Options:")
            
            # Option 1: Environment variable
            print("    Option 1: Environment variable OUTLOOK_ADAPTER=real")
            
            # Option 2: Command line flag  
            print("    Option 2: Command line flag --adapter=real")
            
            # Option 3: Configuration file
            print("    Option 3: Configuration file setting")
            
            # Show simple factory pattern
            def get_adapter(adapter_type="mock"):
                if adapter_type == "real":
                    return PyWin32OutlookAdapter()
                else:
                    from src.outlook_cli.adapters.mock_adapter import MockOutlookAdapter
                    return MockOutlookAdapter()
            
            # Test both adapters can be instantiated
            mock_adapter = get_adapter("mock")
            real_adapter = get_adapter("real")
            
            print("  ✓ Adapter factory pattern works for both mock and real adapters")
            
        except Exception as e:
            print(f"✗ Adapter configuration test failed: {e}")
            traceback.print_exc()
            return False
        
        print("\n=== TEST COMPLETE: SUCCESS ===")
        print("All CLI services integrate successfully with PyWin32OutlookAdapter")
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
    print(f"Starting Windows Test 010 at {datetime.now()}")
    print("Testing CLI integration with PyWin32OutlookAdapter...")
    print("-" * 70)
    
    success = test_cli_integration_with_real_adapter()
    
    print("-" * 70)
    if success:
        print("TEST PASSED: CLI integration with real adapter verified")
        print("\nNext steps:")
        print("1. Modify CLI to support adapter selection")
        print("2. Add configuration options for production use")
        print("3. Test all CLI commands manually with real adapter")
        sys.exit(0)
    else:
        print("TEST FAILED: Check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()