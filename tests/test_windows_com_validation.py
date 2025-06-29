"""Tests for Windows COM interface validation script.

This test file validates that the Windows testing script properly tests
the PyWin32Adapter COM interface connection to real Outlook.
"""

import unittest
import os
import tempfile
from datetime import datetime


class TestWindowsCOMValidationScript(unittest.TestCase):
    """Test cases for the Windows COM validation script generator."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = tempfile.mkdtemp()
        self.script_path = os.path.join(self.test_dir, "test_com_interface.py")
        
    def test_script_generation_creates_file(self):
        """Test that script generation creates the validation file."""
        # Import the script generator that should be created
        # This will fail initially as we haven't implemented it yet
        from src.outlook_cli.testing.windows_com_validator import generate_test_script
        
        generate_test_script(self.script_path)
        
        # Verify script file was created
        self.assertTrue(os.path.exists(self.script_path))
        
    def test_script_contains_basic_connection_tests(self):
        """Test that generated script contains basic COM connection tests."""
        from src.outlook_cli.testing.windows_com_validator import generate_test_script
        
        generate_test_script(self.script_path)
        
        # Read generated script content
        with open(self.script_path, 'r') as f:
            script_content = f.read()
        
        # Verify script contains essential COM connection tests
        self.assertIn("win32com.client.Dispatch", script_content)
        self.assertIn("Outlook.Application", script_content)
        self.assertIn("GetNamespace", script_content)
        self.assertIn("MAPI", script_content)
        
    def test_script_contains_folder_enumeration_tests(self):
        """Test that generated script contains folder enumeration tests."""
        from src.outlook_cli.testing.windows_com_validator import generate_test_script
        
        generate_test_script(self.script_path)
        
        with open(self.script_path, 'r') as f:
            script_content = f.read()
        
        # Verify script tests folder enumeration
        self.assertIn("get_folders", script_content)
        self.assertIn("Folders", script_content)
        self.assertIn("recursive", script_content)
        
    def test_script_contains_error_handling_tests(self):
        """Test that generated script contains error handling tests."""
        from src.outlook_cli.testing.windows_com_validator import generate_test_script
        
        generate_test_script(self.script_path)
        
        with open(self.script_path, 'r') as f:
            script_content = f.read()
        
        # Verify script tests error scenarios
        self.assertIn("try:", script_content)
        self.assertIn("except", script_content)
        self.assertIn("com_error", script_content)
        self.assertIn("Outlook not running", script_content)
        
    def test_script_generates_json_output(self):
        """Test that script is designed to generate structured JSON output."""
        from src.outlook_cli.testing.windows_com_validator import generate_test_script
        
        generate_test_script(self.script_path)
        
        with open(self.script_path, 'r') as f:
            script_content = f.read()
        
        # Verify script generates JSON output for analysis
        self.assertIn("json", script_content)
        self.assertIn("results", script_content)
        self.assertIn("timestamp", script_content)
        
    def test_script_executable_standalone(self):
        """Test that generated script is executable as standalone Python script."""
        from src.outlook_cli.testing.windows_com_validator import generate_test_script
        
        generate_test_script(self.script_path)
        
        with open(self.script_path, 'r') as f:
            script_content = f.read()
        
        # Verify script has proper structure for standalone execution
        self.assertIn("if __name__ == '__main__':", script_content)
        self.assertIn("def main():", script_content)
        
    def test_script_includes_detailed_logging(self):
        """Test that script includes comprehensive logging for debugging."""
        from src.outlook_cli.testing.windows_com_validator import generate_test_script
        
        generate_test_script(self.script_path)
        
        with open(self.script_path, 'r') as f:
            script_content = f.read()
        
        # Verify script has logging infrastructure
        self.assertIn("logging", script_content)
        self.assertIn("logger", script_content)
        self.assertIn("info", script_content)
        self.assertIn("error", script_content)


class TestWindowsCOMValidationResults(unittest.TestCase):
    """Test cases for validating COM validation script results."""
    
    def test_result_analyzer_validates_success(self):
        """Test that result analyzer can validate successful COM tests."""
        from src.outlook_cli.testing.windows_com_validator import analyze_test_results
        
        # Mock successful test results
        mock_results = {
            "timestamp": datetime.now().isoformat(),
            "connection_test": {"status": "success", "message": "Connected to Outlook"},
            "folder_test": {"status": "success", "folder_count": 15},
            "error_handling_test": {"status": "success", "message": "Error handling works"}
        }
        
        analysis = analyze_test_results(mock_results)
        
        self.assertEqual(analysis["overall_status"], "success")
        self.assertTrue(analysis["com_interface_working"])
        
    def test_result_analyzer_detects_failures(self):
        """Test that result analyzer properly detects COM failures."""
        from src.outlook_cli.testing.windows_com_validator import analyze_test_results
        
        # Mock failed test results  
        mock_results = {
            "timestamp": datetime.now().isoformat(),
            "connection_test": {"status": "failed", "error": "Outlook not found"},
            "folder_test": {"status": "not_run"},
            "error_handling_test": {"status": "not_run"}
        }
        
        analysis = analyze_test_results(mock_results)
        
        self.assertEqual(analysis["overall_status"], "failed")
        self.assertFalse(analysis["com_interface_working"])
        self.assertIn("Connection failed: Outlook not found", analysis["issues"])


if __name__ == '__main__':
    unittest.main()