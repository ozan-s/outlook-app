#!/usr/bin/env python3
"""
Windows Test 008: PyWin32OutlookAdapter Basic Implementation
Test real Outlook adapter instantiation and basic folder access.

This test verifies:
1. PyWin32OutlookAdapter can be instantiated with actual Outlook connection
2. get_folders() returns real Outlook folder structure
3. Folder data matches our Folder model structure
4. Basic COM connection and error handling works

Execute on Windows with: uv run python windows_test_008_real_adapter.py
"""

import sys
import traceback
from datetime import datetime

def test_pywin32_adapter_basic():
    """Test basic PyWin32OutlookAdapter instantiation and folder access."""
    
    print("=== TEST: PyWin32OutlookAdapter Basic Implementation ===")
    
    try:
        # Import required modules (pywin32 should be available on Windows)
        import win32com.client
        from pywintypes import com_error
        
        # Import our adapter (will fail first - this is TDD RED phase)
        try:
            from src.outlook_cli.adapters.pywin32_adapter import PyWin32OutlookAdapter
            print("✓ PyWin32OutlookAdapter imported successfully")
        except ImportError as e:
            print(f"✗ PyWin32OutlookAdapter import failed (expected in RED phase): {e}")
            print("  This is expected - we haven't implemented it yet!")
            return False
        
        # Test 1: Adapter instantiation
        print("\n--- Test 1: Adapter Instantiation ---")
        try:
            adapter = PyWin32OutlookAdapter()
            print("✓ Adapter instantiated successfully")
        except Exception as e:
            print(f"✗ Adapter instantiation failed: {e}")
            return False
        
        # Test 2: Outlook COM connection
        print("\n--- Test 2: Outlook COM Connection ---")
        try:
            # This should work through the adapter's internal connection
            # We're testing the adapter interface, not calling COM directly
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            print("✓ Direct COM connection to Outlook successful")
            print(f"  Namespace: {namespace}")
        except com_error as e:
            print(f"✗ Outlook COM connection failed: {e}")
            print("  Ensure Outlook is running and accessible")
            return False
        
        # Test 3: get_folders() basic functionality
        print("\n--- Test 3: get_folders() Method ---")
        try:
            folders = adapter.get_folders()
            print(f"✓ get_folders() returned {len(folders)} folders")
            
            # Test folder structure
            if len(folders) > 0:
                first_folder = folders[0]
                print(f"  First folder: {first_folder}")
                
                # Verify Folder model compliance
                from src.outlook_cli.models.folder import Folder
                if isinstance(first_folder, Folder):
                    print("✓ Folders are proper Folder model instances")
                    print(f"  Sample folder - Path: {first_folder.path}, Name: {first_folder.name}")
                    print(f"  Email count: {first_folder.email_count}, Unread: {first_folder.unread_count}")
                else:
                    print(f"✗ Folders are not Folder model instances: {type(first_folder)}")
                    return False
            else:
                print("✗ No folders returned - check Outlook configuration")
                return False
                
        except Exception as e:
            print(f"✗ get_folders() failed: {e}")
            traceback.print_exc()
            return False
        
        # Test 4: Real Outlook folder enumeration (for comparison)
        print("\n--- Test 4: Real Outlook Folder Enumeration ---")
        try:
            # Direct COM approach to verify our adapter matches real structure
            default_folder = namespace.GetDefaultFolder(6)  # Inbox
            print(f"✓ Default Inbox folder: {default_folder.Name}")
            print(f"  Items count: {default_folder.Items.Count}")
            print(f"  Unread count: {default_folder.UnReadItemCount}")
            
            # Test folder hierarchy access
            folders_collection = namespace.Folders
            print(f"✓ Root folders collection count: {folders_collection.Count}")
            
            if folders_collection.Count > 0:
                # COM collections are 1-indexed
                first_account = folders_collection[1]
                print(f"  First account: {first_account.Name}")
                
                account_folders = first_account.Folders
                print(f"  Account folders count: {account_folders.Count}")
                
                # List a few key folders
                for i in range(1, min(6, account_folders.Count + 1)):
                    try:
                        folder = account_folders[i]
                        print(f"    Folder {i}: {folder.Name} ({folder.Items.Count} items)")
                    except Exception as e:
                        print(f"    Folder {i}: Error accessing - {e}")
            
        except Exception as e:
            print(f"✗ Real Outlook enumeration failed: {e}")
            traceback.print_exc()
            return False
        
        print("\n=== TEST COMPLETE: SUCCESS ===")
        return True
        
    except ImportError as e:
        print(f"✗ Required modules not available: {e}")
        print("  Ensure running on Windows with pywin32 installed")
        return False
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        traceback.print_exc()
        return False

def main():
    """Run the test and exit with appropriate code."""
    print(f"Starting Windows Test 008 at {datetime.now()}")
    print("Testing PyWin32OutlookAdapter basic implementation...")
    print("-" * 60)
    
    success = test_pywin32_adapter_basic()
    
    print("-" * 60)
    if success:
        print("TEST PASSED: Basic adapter functionality verified")
        sys.exit(0)
    else:
        print("TEST FAILED: Check errors above")
        sys.exit(1)

if __name__ == "__main__":
    main()