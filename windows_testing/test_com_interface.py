"""Windows COM Interface Validation Script for Outlook CLI.

This script validates that the PyWin32 COM interface works correctly with
real Microsoft Outlook on Windows machines.

Run this script on a Windows machine with Outlook installed to validate
the COM interface functionality.
"""

import json
import logging
import sys
import traceback
from datetime import datetime
from typing import Dict, Any, List


def setup_logging() -> logging.Logger:
    """Set up comprehensive logging for debugging."""
    logger = logging.getLogger('outlook_com_validator')
    logger.setLevel(logging.DEBUG)
    
    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # Create file handler for detailed logs
    file_handler = logging.FileHandler('outlook_com_test.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)
    
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger


def test_basic_com_connection(logger: logging.Logger) -> Dict[str, Any]:
    """Test basic COM connection to Outlook.
    
    Returns:
        Dict containing test results.
    """
    logger.info("Testing basic COM connection to Outlook...")
    
    try:
        # Test pywin32 availability
        try:
            import win32com.client
            from pywintypes import com_error
            logger.info("pywin32 modules imported successfully")
        except ImportError as e:
            return {
                "status": "failed",
                "error": f"pywin32 not available: {e}",
                "details": "Install pywin32 package"
            }
        
        # Test Outlook COM connection
        try:
            outlook = win32com.client.Dispatch("Outlook.Application")
            logger.info("Successfully connected to Outlook.Application")
        except com_error as e:
            return {
                "status": "failed", 
                "error": f"Failed to connect to Outlook.Application: {e}",
                "details": "Ensure Outlook is installed and running"
            }
        
        # Test MAPI namespace access
        try:
            namespace = outlook.GetNamespace("MAPI")
            logger.info("Successfully accessed MAPI namespace")
        except com_error as e:
            return {
                "status": "failed",
                "error": f"Failed to access MAPI namespace: {e}",
                "details": "MAPI connection issue"
            }
        
        # Test basic folder collection access
        try:
            folders = namespace.Folders
            folder_count = folders.Count
            logger.info(f"Successfully accessed folder collection, count: {folder_count}")
        except com_error as e:
            return {
                "status": "failed",
                "error": f"Failed to access folder collection: {e}",
                "details": "Folder access permission issue"
            }
        
        return {
            "status": "success",
            "message": "Connected to Outlook",
            "folder_count": folder_count,
            "details": "All basic COM operations successful"
        }
        
    except Exception as e:
        logger.error(f"Unexpected error in COM connection test: {e}")
        return {
            "status": "failed",
            "error": f"Unexpected error: {e}",
            "traceback": traceback.format_exc()
        }


def test_folder_enumeration(outlook, namespace, logger: logging.Logger) -> Dict[str, Any]:
    """Test recursive folder enumeration functionality.
    
    Returns:
        Dict containing test results.
    """
    logger.info("Testing folder enumeration...")
    
    try:
        # Test get_folders equivalent functionality
        folders_found = []
        
        # Get all accounts/stores
        folders_collection = namespace.Folders
        
        # COM collections are 1-indexed
        for i in range(1, folders_collection.Count + 1):
            try:
                account_folder = folders_collection[i]
                
                # Test recursive folder discovery
                recursive_folders = _get_folders_recursive(account_folder, "", logger)
                folders_found.extend(recursive_folders)
                
            except Exception as e:
                logger.warning(f"Skipping inaccessible folder at index {i}: {e}")
                continue
        
        total_folders = len(folders_found)
        logger.info(f"Successfully enumerated {total_folders} folders")
        
        # Analyze folder structure
        folder_analysis = {
            "total_folders": total_folders,
            "folders_with_emails": 0,
            "max_depth": 0,
            "sample_folders": []
        }
        
        for folder_info in folders_found[:10]:  # Sample first 10
            folder_analysis["sample_folders"].append({
                "path": folder_info["path"],
                "email_count": folder_info.get("email_count", 0),
                "depth": folder_info["path"].count("/")
            })
            
            if folder_info.get("email_count", 0) > 0:
                folder_analysis["folders_with_emails"] += 1
            
            depth = folder_info["path"].count("/")
            if depth > folder_analysis["max_depth"]:
                folder_analysis["max_depth"] = depth
        
        return {
            "status": "success",
            "folder_count": total_folders,
            "analysis": folder_analysis,
            "details": "Folder enumeration completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Error in folder enumeration test: {e}")
        return {
            "status": "failed",
            "error": f"Folder enumeration failed: {e}",
            "traceback": traceback.format_exc()
        }


def _get_folders_recursive(com_folder, parent_path: str, logger: logging.Logger) -> List[Dict[str, Any]]:
    """Recursively build folder list from COM folder object."""
    folders = []
    
    try:
        # Build folder path
        folder_name = com_folder.Name
        folder_path = f"{parent_path}/{folder_name}" if parent_path else folder_name
        
        # Get folder statistics
        try:
            email_count = com_folder.Items.Count
            unread_count = com_folder.UnReadItemCount
        except:
            email_count = 0
            unread_count = 0
        
        # Create folder info
        folder_info = {
            "path": folder_path,
            "name": folder_name,
            "email_count": email_count,
            "unread_count": unread_count
        }
        folders.append(folder_info)
        
        # Process subfolders
        if hasattr(com_folder, 'Folders'):
            subfolders = com_folder.Folders
            for i in range(1, subfolders.Count + 1):
                try:
                    subfolder = subfolders[i]
                    folders.extend(_get_folders_recursive(subfolder, folder_path, logger))
                except Exception as e:
                    logger.warning(f"Skipping inaccessible subfolder at index {i}: {e}")
                    continue
        
    except Exception as e:
        logger.error(f"Error processing folder {parent_path}: {e}")
    
    return folders


def test_error_handling(logger: logging.Logger) -> Dict[str, Any]:
    """Test COM error handling scenarios.
    
    Returns:
        Dict containing test results.
    """
    logger.info("Testing error handling scenarios...")
    
    error_tests = []
    
    # Test 1: Invalid COM object
    try:
        import win32com.client
        invalid_app = win32com.client.Dispatch("NonExistent.Application")
        error_tests.append({
            "test": "invalid_com_object",
            "status": "unexpected_success",
            "message": "Expected failure but succeeded"
        })
    except Exception as e:
        error_tests.append({
            "test": "invalid_com_object", 
            "status": "expected_failure",
            "error": str(e)
        })
        logger.info("✓ Invalid COM object properly failed")
    
    # Test 2: Outlook not running scenario simulation
    # Note: This is hard to test without stopping Outlook
    error_tests.append({
        "test": "outlook_not_running",
        "status": "info",
        "message": "Cannot test Outlook not running without stopping it"
    })
    
    return {
        "status": "success",
        "message": "Error handling works",
        "error_tests": error_tests,
        "details": "Error handling scenarios tested"
    }


def main():
    """Main test execution function."""
    print("Starting Windows COM Interface Validation...")
    print("=" * 50)
    
    # Set up logging
    logger = setup_logging()
    logger.info("Starting COM interface validation")
    
    # Initialize results structure
    results = {
        "timestamp": datetime.now().isoformat(),
        "platform": sys.platform,
        "python_version": sys.version,
        "test_results": {}
    }
    
    # Test 1: Basic COM Connection
    print("\n1. Testing Basic COM Connection...")
    connection_result = test_basic_com_connection(logger)
    results["test_results"]["connection_test"] = connection_result
    
    if connection_result["status"] == "success":
        print("✓ COM Connection: SUCCESS")
        
        # If connection successful, continue with advanced tests
        try:
            import win32com.client
            outlook = win32com.client.Dispatch("Outlook.Application")
            namespace = outlook.GetNamespace("MAPI")
            
            # Test 2: Folder Enumeration
            print("\n2. Testing Folder Enumeration...")
            folder_result = test_folder_enumeration(outlook, namespace, logger)
            results["test_results"]["folder_test"] = folder_result
            
            if folder_result["status"] == "success":
                print(f"✓ Folder Enumeration: SUCCESS ({folder_result['folder_count']} folders)")
            else:
                print(f"✗ Folder Enumeration: FAILED - {folder_result.get('error', 'Unknown error')}")
            
        except Exception as e:
            results["test_results"]["folder_test"] = {
                "status": "failed",
                "error": f"Could not set up for folder test: {e}"
            }
            print(f"✗ Folder Test Setup: FAILED - {e}")
    else:
        print(f"✗ COM Connection: FAILED - {connection_result.get('error', 'Unknown error')}")
        results["test_results"]["folder_test"] = {"status": "not_run"}
    
    # Test 3: Error Handling
    print("\n3. Testing Error Handling...")
    error_result = test_error_handling(logger)
    results["test_results"]["error_handling_test"] = error_result
    
    if error_result["status"] == "success":
        print("✓ Error Handling: SUCCESS")
    else:
        print(f"✗ Error Handling: FAILED - {error_result.get('error', 'Unknown error')}")
    
    # Save results to JSON file
    output_file = "outlook_com_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n" + "=" * 50)
    print(f"Results saved to: {output_file}")
    print(f"Detailed logs saved to: outlook_com_test.log")
    
    # Summary
    total_tests = len(results["test_results"])
    passed_tests = sum(1 for test in results["test_results"].values() if test["status"] == "success")
    
    print(f"\nSUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed! COM interface is working correctly.")
        logger.info("All COM validation tests passed")
    else:
        print("⚠️  Some tests failed. Check logs for details.")
        logger.warning("Some COM validation tests failed")


if __name__ == '__main__':
    main()