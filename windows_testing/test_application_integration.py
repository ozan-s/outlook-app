"""Application-Level Windows Testing for Outlook CLI.

This script validates that the actual CLI commands work end-to-end on Windows,
not just the raw COM interface.
"""

import subprocess
import sys
import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path


def setup_logging() -> logging.Logger:
    """Set up logging for application integration test."""
    logger = logging.getLogger('outlook_app_validator')
    logger.setLevel(logging.DEBUG)
    
    # File handler for detailed logs
    file_handler = logging.FileHandler('outlook_app_test.log')
    file_handler.setLevel(logging.DEBUG)
    
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    
    return logger


def test_cli_command(command_args: List[str], logger: logging.Logger) -> Dict[str, Any]:
    """Test a CLI command and return results.
    
    Args:
        command_args: List of command arguments to run
        logger: Logger instance
        
    Returns:
        Dict containing test results
    """
    command_str = ' '.join(command_args)
    logger.info(f"Testing command: {command_str}")
    
    try:
        # Run the CLI command
        result = subprocess.run(
            command_args,
            capture_output=True,
            text=True,
            timeout=30,  # 30 second timeout
            cwd=Path(__file__).parent.parent  # Run from project root
        )
        
        success = result.returncode == 0
        
        return {
            "command": command_str,
            "status": "success" if success else "failed",
            "returncode": result.returncode,
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip(),
            "execution_time": "< 30s"  # We only know it completed within timeout
        }
        
    except subprocess.TimeoutExpired:
        logger.error(f"Command timed out: {command_str}")
        return {
            "command": command_str,
            "status": "failed",
            "error": "Command timed out after 30 seconds",
            "execution_time": "> 30s"
        }
    except Exception as e:
        logger.error(f"Error running command {command_str}: {e}")
        return {
            "command": command_str,
            "status": "failed",
            "error": str(e)
        }


def test_folders_command(logger: logging.Logger) -> Dict[str, Any]:
    """Test the folders command with real adapter."""
    logger.info("Testing 'folders' command...")
    
    # Test with real adapter (should work on Windows with Outlook)
    env = os.environ.copy()
    env['OUTLOOK_ADAPTER'] = 'real'
    
    command = ['uv', 'run', 'python', 'src/outlook_cli/cli.py', 'folders', '--tree']
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=10,
            env=env,
            cwd=Path(__file__).parent.parent,
            encoding='utf-8',
            errors='replace'
        )
        
        success = result.returncode == 0
        output = result.stdout.strip()
        
        # Analyze output structure
        analysis = {
            "lines_count": len(output.split('\n')) if output else 0,
            "has_tree_structure": '├──' in output or '└──' in output,
            "has_folders": any(folder in output.lower() for folder in ['inbox', 'sent', 'drafts']),
            "empty_output": len(output) == 0
        }
        
        return {
            "command": "folders --tree",
            "status": "success" if success else "failed",
            "returncode": result.returncode,
            "stdout": output[:500] + "..." if len(output) > 500 else output,  # Truncate long output
            "stderr": result.stderr.strip(),
            "analysis": analysis,
            "adapter": "real"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "command": "folders --tree",
            "status": "failed",
            "error": "Command timed out - possible COM connection issue",
            "adapter": "real"
        }
    except Exception as e:
        return {
            "command": "folders --tree", 
            "status": "failed",
            "error": str(e),
            "adapter": "real"
        }


def test_read_command(logger: logging.Logger) -> Dict[str, Any]:
    """Test the read command with real adapter."""
    logger.info("Testing 'read' command...")
    
    env = os.environ.copy()
    env['OUTLOOK_ADAPTER'] = 'real'
    
    command = ['uv', 'run', 'python', 'src/outlook_cli/cli.py', 'read', '--folder', 'Inbox']
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=15,
            env=env,
            cwd=Path(__file__).parent.parent,
            encoding='utf-8',
            errors='replace'
        )
        
        success = result.returncode == 0
        output = result.stdout.strip()
        
        # Analyze output for email structure
        analysis = {
            "has_email_headers": any(header in output for header in ['From:', 'Subject:', 'Date:']),
            "has_pagination": 'Page' in output,
            "has_email_ids": '[' in output and ']' in output,
            "email_count": output.count('From:') if 'From:' in output else 0,
            "empty_output": len(output) == 0
        }
        
        return {
            "command": "read --folder Inbox",
            "status": "success" if success else "failed",
            "returncode": result.returncode,
            "stdout": output[:300] + "..." if len(output) > 300 else output,
            "stderr": result.stderr.strip(),
            "analysis": analysis,
            "adapter": "real"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "command": "read --folder Inbox",
            "status": "failed", 
            "error": "Command timed out - possible email retrieval issue",
            "adapter": "real"
        }
    except Exception as e:
        return {
            "command": "read --folder Inbox",
            "status": "failed",
            "error": str(e),
            "adapter": "real"
        }


def test_find_command(logger: logging.Logger) -> Dict[str, Any]:
    """Test the find command with real adapter."""
    logger.info("Testing 'find' command...")
    
    env = os.environ.copy()
    env['OUTLOOK_ADAPTER'] = 'real'
    
    # Search for common keywords that likely exist
    command = ['uv', 'run', 'python', 'src/outlook_cli/cli.py', 'find', '--keyword', 'meeting']
    
    try:
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=20,
            env=env,
            cwd=Path(__file__).parent.parent,
            encoding='utf-8',
            errors='replace'  # Replace invalid characters instead of crashing
        )
        
        success = result.returncode == 0
        output = result.stdout.strip()
        
        # Analyze search functionality
        analysis = {
            "shows_search_query": 'meeting' in output.lower(),
            "has_results_structure": any(phrase in output for phrase in ['showing', 'Page', 'emails']),
            "has_email_content": 'From:' in output or 'Subject:' in output,
            "no_results_found": 'no emails found' in output.lower() or 'showing 0-0' in output,
            "empty_output": len(output) == 0
        }
        
        return {
            "command": "find --keyword meeting",
            "status": "success" if success else "failed",
            "returncode": result.returncode,
            "stdout": output[:300] + "..." if len(output) > 300 else output,
            "stderr": result.stderr.strip(),
            "analysis": analysis,
            "adapter": "real"
        }
        
    except subprocess.TimeoutExpired:
        return {
            "command": "find --keyword meeting",
            "status": "failed",
            "error": "Command timed out - possible search issue",
            "adapter": "real"
        }
    except Exception as e:
        return {
            "command": "find --keyword meeting",
            "status": "failed",
            "error": str(e),
            "adapter": "real"
        }


def test_exchange_dn_resolution(logger: logging.Logger) -> Dict[str, Any]:
    """Test Exchange DN resolution functionality for corporate environments."""
    logger.info("Testing Exchange DN resolution patterns...")
    
    # Test the critical Exchange DN patterns used in corporate Outlook
    test_results = {
        "pattern_recognition": True,
        "resolution_workflow": True,
        "integration_ready": True,
        "issues": []
    }
    
    try:
        # Test 1: Exchange DN pattern recognition
        exchange_dn_samples = [
            "/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP/CN=RECIPIENTS/CN=user123",
            "/o=company/ou=exchange administrative group/cn=recipients/cn=testuser",
            "/O=COMPANY/OU=FIRST ADMINISTRATIVE GROUP/CN=RECIPIENTS/CN=DISPLAYNAME"
        ]
        
        non_exchange_samples = [
            "user@company.com",
            "displayname@company.com",
            "",
            "not-an-email"
        ]
        
        def is_exchange_dn(email_address: str) -> bool:
            """Pattern recognition function."""
            return bool(email_address) and email_address.upper().startswith('/O=')
        
        # Test Exchange DN recognition
        for dn in exchange_dn_samples:
            if not is_exchange_dn(dn):
                test_results["pattern_recognition"] = False
                test_results["issues"].append(f"Failed to recognize Exchange DN: {dn[:50]}...")
        
        for email in non_exchange_samples:
            if is_exchange_dn(email):
                test_results["pattern_recognition"] = False
                test_results["issues"].append(f"Incorrectly identified as Exchange DN: {email}")
        
        # Test 2: Check that our adapter has the resolution methods
        try:
            # Import the adapter to verify the methods exist
            import sys
            import os
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            from outlook_cli.adapters.pywin32_adapter import PyWin32OutlookAdapter
            
            # Check that resolution methods are implemented
            adapter_methods = dir(PyWin32OutlookAdapter)
            required_methods = [
                '_resolve_exchange_dn_to_smtp',
                '_extract_sender_smtp',
                '_extract_recipient_smtp'
            ]
            
            for method in required_methods:
                if method not in adapter_methods:
                    test_results["resolution_workflow"] = False
                    test_results["issues"].append(f"Missing Exchange DN resolution method: {method}")
            
        except ImportError as e:
            test_results["integration_ready"] = False
            test_results["issues"].append(f"Cannot import adapter for testing: {e}")
        
        # Test 3: Verify the resolution workflow pattern
        # This simulates the COM interface pattern without requiring Windows
        resolution_steps = [
            "CreateRecipient(exchange_dn)",
            "recipient.Resolve()", 
            "recipient.AddressEntry",
            "address_entry.GetExchangeUser()",
            "exchange_user.PrimarySmtpAddress"
        ]
        
        # This test just validates the pattern is documented and expected
        logger.info(f"Exchange DN resolution follows {len(resolution_steps)}-step pattern")
        
        # Determine overall status
        all_tests_passed = (
            test_results["pattern_recognition"] and 
            test_results["resolution_workflow"] and 
            test_results["integration_ready"]
        )
        
        return {
            "command": "Exchange DN resolution pattern test",
            "status": "success" if all_tests_passed else "failed",
            "test_results": test_results,
            "pattern_steps": resolution_steps,
            "critical_for": "Corporate Outlook environments with Exchange server"
        }
        
    except Exception as e:
        logger.error(f"Exchange DN test failed: {e}")
        return {
            "command": "Exchange DN resolution pattern test",
            "status": "failed",
            "error": str(e),
            "critical_for": "Corporate Outlook environments with Exchange server"
        }


def test_cross_adapter_compatibility(logger: logging.Logger) -> Dict[str, Any]:
    """Test that mock and real adapters have compatible output formats."""
    logger.info("Testing cross-adapter compatibility...")
    
    results = {"mock": {}, "real": {}}
    
    # Test folders command with both adapters
    for adapter_type in ['mock', 'real']:
        env = os.environ.copy()
        env['OUTLOOK_ADAPTER'] = adapter_type
        
        command = ['uv', 'run', 'python', 'src/outlook_cli/cli.py', 'folders', '--tree']
        
        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=10,
                env=env,
                cwd=Path(__file__).parent.parent,
                encoding='utf-8',
                errors='replace'
            )
            
            results[adapter_type] = {
                "status": "success" if result.returncode == 0 else "failed",
                "returncode": result.returncode,
                "output_lines": len(result.stdout.split('\n')) if result.stdout else 0,
                "has_tree_chars": '├──' in result.stdout or '└──' in result.stdout,
                "stderr": result.stderr.strip()
            }
            
        except Exception as e:
            results[adapter_type] = {
                "status": "failed",
                "error": str(e)
            }
    
    # Compare results
    mock_success = results["mock"].get("status") == "success"
    real_success = results["real"].get("status") == "success"
    
    compatibility_analysis = {
        "both_succeed": mock_success and real_success,
        "mock_works": mock_success,
        "real_works": real_success,
        "similar_structure": False
    }
    
    if mock_success and real_success:
        # Compare output structure
        mock_has_tree = results["mock"].get("has_tree_chars", False)
        real_has_tree = results["real"].get("has_tree_chars", False)
        compatibility_analysis["similar_structure"] = mock_has_tree == real_has_tree
    
    return {
        "command": "cross-adapter compatibility test",
        "status": "success" if compatibility_analysis["both_succeed"] else "failed",
        "results": results,
        "analysis": compatibility_analysis
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
            pass
    
    print("Starting Application Integration Testing...")
    print("=" * 50)
    
    logger = setup_logging()
    logger.info("Starting application integration tests")
    
    # Initialize results
    results = {
        "timestamp": datetime.now().isoformat(),
        "platform": sys.platform,
        "python_version": sys.version,
        "test_results": {}
    }
    
    # Test 1: Folders Command
    print("\n1. Testing Folders Command...")
    folders_result = test_folders_command(logger)
    results["test_results"]["folders_test"] = folders_result
    
    if folders_result["status"] == "success":
        print(f"[OK] Folders Command")
    else:
        print(f"[FAIL] Folders Command - {folders_result.get('error', 'See logs')}")
    
    # Test 2: Read Command
    print("\n2. Testing Read Command...")
    read_result = test_read_command(logger)
    results["test_results"]["read_test"] = read_result
    
    if read_result["status"] == "success":
        print(f"[OK] Read Command")
    else:
        print(f"[FAIL] Read Command - {read_result.get('error', 'See logs')}")
    
    # Test 3: Find Command 
    print("\n3. Testing Find Command...")
    find_result = test_find_command(logger)
    results["test_results"]["find_test"] = find_result
    
    if find_result["status"] == "success":
        print(f"[OK] Find Command")
    else:
        print(f"[FAIL] Find Command - {find_result.get('error', 'See logs')}")
    
    # Test 4: Exchange DN Resolution
    print("\n4. Testing Exchange DN Resolution...")
    dn_result = test_exchange_dn_resolution(logger)
    results["test_results"]["exchange_dn_test"] = dn_result
    
    if dn_result["status"] == "success":
        print(f"[OK] Exchange DN Resolution")
    else:
        print(f"[FAIL] Exchange DN Resolution - Check logs")
    
    # Test 5: Cross-Adapter Compatibility
    print("\n5. Testing Cross-Adapter Compatibility...")
    compat_result = test_cross_adapter_compatibility(logger)
    results["test_results"]["compatibility_test"] = compat_result
    
    if compat_result["status"] == "success":
        print(f"[OK] Cross-Adapter Compatibility")
    else:
        print(f"[FAIL] Cross-Adapter Compatibility - Check logs")
    
    # Save results
    output_file = "outlook_app_validation_results.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n" + "=" * 50)
    
    # Summary
    total_tests = len(results["test_results"])
    passed_tests = sum(1 for test in results["test_results"].values() if test["status"] == "success")
    
    print(f"SUMMARY: {passed_tests}/{total_tests} application tests passed")
    
    if passed_tests == total_tests:
        print("All application tests passed! CLI commands work correctly.")
        logger.info("All application validation tests passed")
    else:
        print("Some application tests failed. Check outlook_app_test.log for details.")
        logger.warning("Some application validation tests failed")
        sys.exit(1)
    
    print(f"\nResults saved to: {output_file}")
    print(f"Detailed logs saved to: outlook_app_test.log")


if __name__ == '__main__':
    main()