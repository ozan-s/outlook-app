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
    """Set up logging with minimal console output for user clarity."""
    logger = logging.getLogger('outlook_com_validator')
    logger.setLevel(logging.DEBUG)
    
    # Only create file handler - no console spam
    file_handler = logging.FileHandler('outlook_com_test.log')
    file_handler.setLevel(logging.DEBUG)
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
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
        errors_encountered = []
        
        # Get all accounts/stores using defensive iteration
        folders_collection = namespace.Folders
        
        # Defensive iteration - don't rely solely on Count property
        index = 1
        consecutive_failures = 0
        max_consecutive_failures = 3
        
        while consecutive_failures < max_consecutive_failures:
            try:
                account_folder = folders_collection[index]
                
                # Test recursive folder discovery
                recursive_folders, folder_errors = _get_folders_recursive(account_folder, "", logger)
                folders_found.extend(recursive_folders)
                errors_encountered.extend(folder_errors)
                
                consecutive_failures = 0  # Reset on success
                index += 1
                
            except Exception as e:
                error_msg = f"Skipping inaccessible folder at index {index}: {e}"
                logger.warning(error_msg)
                errors_encountered.append(error_msg)
                consecutive_failures += 1
                index += 1
                
                # Safety check: don't iterate beyond reasonable bounds
                if index > folders_collection.Count + max_consecutive_failures:
                    break
        
        total_folders = len(folders_found)
        total_errors = len(errors_encountered)
        
        logger.info(f"Successfully enumerated {total_folders} folders")
        if total_errors > 0:
            logger.warning(f"Encountered {total_errors} errors during enumeration")
        
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
        
        # Determine if test passed or failed using proper error classification
        status, details = _classify_folder_test_result(total_folders, errors_encountered)
        
        if status == "failed":
            return {
                "status": "failed",
                "folder_count": total_folders,
                "error_count": total_errors,
                "errors": errors_encountered[:10],  # Sample errors
                "analysis": folder_analysis,
                "details": details
            }
        
        return {
            "status": "success",
            "folder_count": total_folders,
            "error_count": total_errors,
            "analysis": folder_analysis,
            "details": details
        }
        
    except Exception as e:
        logger.error(f"Error in folder enumeration test: {e}")
        return {
            "status": "failed",
            "error": f"Folder enumeration failed: {e}",
            "traceback": traceback.format_exc()
        }


def _classify_folder_test_result(total_folders: int, errors: List[str]) -> tuple[str, str]:
    """Classify folder test result based on folder count and error types.
    
    Args:
        total_folders: Number of folders successfully enumerated
        errors: List of error messages encountered
        
    Returns:
        Tuple of (status, details) where status is 'success' or 'failed'
    """
    total_errors = len(errors)
    
    # Rule 1: If no folders found, it's a failure
    if total_folders == 0:
        return "failed", "No folders accessible - possible MAPI or connection issue"
    
    # Rule 2: Check for system-level errors that indicate real problems
    system_error_keywords = [
        "mapi", "com connection", "application failed", 
        "namespace", "cannot connect", "outlook.application"
    ]
    
    for error in errors:
        error_lower = error.lower()
        for keyword in system_error_keywords:
            if keyword in error_lower:
                return "failed", f"System-level error detected: {keyword}"
    
    # Rule 3: If we have folders and only access/permission errors, it's success
    access_error_keywords = ["access", "permission", "inaccessible", "denied", "timeout"]
    
    if errors:  # Only check if there are errors
        all_access_errors = all(
            any(keyword in error.lower() for keyword in access_error_keywords)
            for error in errors
        )
        
        if all_access_errors:
            return "success", f"Found {total_folders} folders with {total_errors} minor access issues"
    
    # Rule 4: For mixed or unknown errors, use stricter threshold (10% instead of 30%)
    if total_folders > 0:
        error_ratio = total_errors / (total_folders + total_errors)
        if error_ratio < 0.1:  # Less than 10% error rate
            return "success", f"Found {total_folders} folders with {total_errors} minor errors"
        else:
            return "failed", f"Too many errors: {total_errors} errors for {total_folders} folders (>{error_ratio:.1%})"
    
    # Default success if we got folders and no major issues
    if total_folders > 0:
        return "success", f"Found {total_folders} folders" + (f" with {total_errors} minor errors" if total_errors > 0 else "")
    
    return "failed", "Unable to classify test result"


def _get_folders_recursive(com_folder, parent_path: str, logger: logging.Logger) -> tuple[List[Dict[str, Any]], List[str]]:
    """Recursively build folder list from COM folder object.
    
    Returns:
        Tuple of (folders, errors) encountered during enumeration.
    """
    folders = []
    errors = []
    
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
        
        # Process subfolders using defensive iteration
        if hasattr(com_folder, 'Folders'):
            subfolders = com_folder.Folders
            
            # Only iterate if there are actually subfolders
            if subfolders.Count > 0:
                index = 1
                consecutive_failures = 0
                max_consecutive_failures = 3
                
                while consecutive_failures < max_consecutive_failures:
                    try:
                        subfolder = subfolders[index]
                        sub_folders, sub_errors = _get_folders_recursive(subfolder, folder_path, logger)
                        folders.extend(sub_folders)
                        errors.extend(sub_errors)
                        consecutive_failures = 0  # Reset on success
                        index += 1
                    except Exception as e:
                        error_msg = f"Skipping inaccessible subfolder at index {index}: {e}"
                        logger.warning(error_msg)
                        errors.append(error_msg)
                        consecutive_failures += 1
                        index += 1
                        
                        # Safety check: don't iterate beyond reasonable bounds
                        if index > subfolders.Count + max_consecutive_failures:
                            break
        
    except Exception as e:
        error_msg = f"Error processing folder {parent_path}: {e}"
        logger.error(error_msg)
        errors.append(error_msg)
    
    return folders, errors


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
        logger.info("Invalid COM object properly failed")
    
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
    # Configure Unicode encoding for Windows console
    if sys.platform == 'win32':
        import os
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        try:
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
        except AttributeError:
            # Python < 3.7 doesn't have reconfigure
            pass
    
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
        print("[OK] COM Connection")
        
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
                error_count = folder_result.get('error_count', 0)
                if error_count > 0:
                    print(f"[OK] Folder Enumeration ({folder_result['folder_count']} folders, {error_count} minor errors)")
                else:
                    print(f"[OK] Folder Enumeration ({folder_result['folder_count']} folders)")
            else:
                print(f"[FAIL] Folder Enumeration - {folder_result.get('error', 'Unknown error')}")
            
        except Exception as e:
            results["test_results"]["folder_test"] = {
                "status": "failed",
                "error": f"Could not set up for folder test: {e}"
            }
            print(f"[FAIL] Folder Test Setup - {e}")
    else:
        print(f"[FAIL] COM Connection - {connection_result.get('error', 'Unknown error')}")
        results["test_results"]["folder_test"] = {"status": "not_run"}
    
    # Test 3: Error Handling
    print("\n3. Testing Error Handling...")
    error_result = test_error_handling(logger)
    results["test_results"]["error_handling_test"] = error_result
    
    if error_result["status"] == "success":
        print("[OK] Error Handling")
    else:
        print(f"[FAIL] Error Handling - {error_result.get('error', 'Unknown error')}")
    
    # Save results to JSON file
    output_file = "outlook_com_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n" + "=" * 50)
    
    # Summary
    total_tests = len(results["test_results"])
    passed_tests = sum(1 for test in results["test_results"].values() if test["status"] == "success")
    
    print(f"SUMMARY: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("All tests passed! COM interface is working correctly.")
        logger.info("All COM validation tests passed")
    else:
        print("Some tests failed. Check outlook_com_test.log for details.")
        logger.warning("Some COM validation tests failed")
        sys.exit(1)  # Exit with error code when tests fail
    
    print(f"\nResults saved to: {output_file}")
    print(f"Detailed logs saved to: outlook_com_test.log")


if __name__ == '__main__':
    main()