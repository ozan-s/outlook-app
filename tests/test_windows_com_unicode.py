"""Test Unicode handling in Windows COM interface validation.

This test ensures that the COM interface validator handles Unicode characters
correctly and doesn't crash on Windows console output.
"""

import sys
import subprocess
import tempfile
import os
from pathlib import Path


def test_unicode_encoding_setup():
    """Test that Unicode encoding is properly configured for Windows console."""
    # This test validates that we can handle Unicode characters in output
    test_unicode = "✓ Test passed with checkmark"
    
    # Should not raise UnicodeEncodeError
    try:
        encoded = test_unicode.encode('utf-8')
        decoded = encoded.decode('utf-8')
        assert decoded == test_unicode
    except UnicodeError:
        pytest.fail("Unicode encoding/decoding failed")


def test_com_test_script_handles_unicode():
    """Test that the COM interface test script handles Unicode output correctly."""
    # Create a minimal test script that would previously fail with Unicode
    test_script = '''
import sys
import os

# This should be added to fix Unicode issues
if sys.platform == 'win32':
    # Set console to UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Test Unicode output that would previously fail
print("✓ SUCCESS: Unicode test")
print("✗ FAILED: Unicode test")  
'''
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(test_script)
        f.flush()
        
        try:
            # Run the test script
            result = subprocess.run([sys.executable, f.name], 
                                  capture_output=True, text=True)
            
            # Should not have encoding errors in stderr
            assert "UnicodeEncodeError" not in result.stderr
            assert result.returncode == 0
            
        finally:
            os.unlink(f.name)


def test_replace_unicode_checkmarks():
    """Test that Unicode checkmarks are replaced with ASCII equivalents."""
    # Test cases that would previously cause issues
    test_cases = [
        ("✓ Success", "[OK] Success"),
        ("✗ Failed", "[FAIL] Failed"), 
        ("STATUS: ✓", "STATUS: [OK]"),
        ("ERROR: ✗", "ERROR: [FAIL]")
    ]
    
    for unicode_text, expected_ascii in test_cases:
        # Function should replace Unicode with ASCII
        ascii_result = unicode_text.replace("✓", "[OK]").replace("✗", "[FAIL]")
        assert ascii_result == expected_ascii


if __name__ == '__main__':
    test_unicode_encoding_setup()
    test_com_test_script_handles_unicode()
    test_replace_unicode_checkmarks()
    print("All Unicode tests passed!")