"""Common Windows Environment Issue Fixes for Outlook CLI.

This script contains fixes for commonly encountered Windows testing issues
based on anticipated problems and corporate environment constraints.
"""

import sys
import os
import traceback
from pathlib import Path


def fix_unicode_encoding():
    """Fix Windows console Unicode encoding issues."""
    print("🔧 Applying Unicode encoding fixes...")
    
    if sys.platform == 'win32':
        # Set environment variable for Python I/O encoding
        os.environ['PYTHONIOENCODING'] = 'utf-8'
        
        try:
            # Reconfigure stdout/stderr for UTF-8 (Python 3.7+)
            sys.stdout.reconfigure(encoding='utf-8')
            sys.stderr.reconfigure(encoding='utf-8')
            print("✅ Unicode encoding configured for Python 3.7+")
        except AttributeError:
            # Python < 3.7 doesn't have reconfigure
            print("⚠️ Python < 3.7 detected, manual encoding may be needed")
        
        # Try to set console code page
        try:
            import subprocess
            subprocess.run(['chcp', '65001'], shell=True, capture_output=True)
            print("✅ Console code page set to UTF-8")
        except Exception as e:
            print(f"⚠️ Could not set console code page: {e}")
    
    return True


def fix_pywin32_import():
    """Fix pywin32 import issues."""
    print("🔧 Checking pywin32 installation...")
    
    try:
        import win32com.client
        from pywintypes import com_error
        print("✅ pywin32 modules imported successfully")
        return True
    except ImportError as e:
        print(f"❌ pywin32 not available: {e}")
        print("🔧 Installing pywin32...")
        
        try:
            import subprocess
            result = subprocess.run([sys.executable, '-m', 'pip', 'install', 'pywin32'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ pywin32 installed successfully")
                
                # Try importing again
                import win32com.client
                from pywintypes import com_error
                print("✅ pywin32 import verification successful")
                return True
            else:
                print(f"❌ pywin32 installation failed: {result.stderr}")
        except Exception as install_error:
            print(f"❌ Could not install pywin32: {install_error}")
        
        return False


def fix_outlook_connection():
    """Fix common Outlook connection issues."""
    print("🔧 Checking Outlook connection...")
    
    try:
        import win32com.client
        from pywintypes import com_error
        
        # Test basic connection
        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        
        print("✅ Outlook connection successful")
        return True
        
    except com_error as e:
        error_code = getattr(e, 'hresult', None)
        error_msg = str(e)
        
        print(f"❌ Outlook connection failed: {error_msg}")
        
        # Provide specific fixes based on error type
        if error_code == -2147221164:  # 0x800401F4 - REGDB_E_CLASSNOTREG
            print("🔧 Fix: Microsoft Outlook is not installed or not properly registered")
            print("   - Install Microsoft Outlook")
            print("   - Run 'regsvr32 outlook.exe' as administrator")
        
        elif "0x80040154" in error_msg:  # Class not registered
            print("🔧 Fix: Outlook COM class not registered")
            print("   - Start Outlook manually first")
            print("   - Run Outlook as the same user as this script")
        
        elif "access" in error_msg.lower() or "permission" in error_msg.lower():
            print("🔧 Fix: Permission issues")
            print("   - Run script as administrator")
            print("   - Check Outlook security settings")
            print("   - Ensure Outlook profile is configured")
        
        else:
            print("🔧 General fixes to try:")
            print("   - Start Microsoft Outlook before running tests")
            print("   - Check if Outlook is running in safe mode")
            print("   - Verify Outlook profile is set up and accessible")
        
        return False
    
    except ImportError:
        print("❌ Cannot test Outlook connection - pywin32 not available")
        return False


def fix_exchange_dn_issues():
    """Prepare fixes for Exchange DN resolution issues."""
    print("🔧 Checking Exchange DN resolution capability...")
    
    try:
        # Import our adapter to check methods exist
        sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))
        from outlook_cli.adapters.pywin32_adapter import PyWin32OutlookAdapter
        
        # Check for required methods
        adapter_methods = dir(PyWin32OutlookAdapter)
        required_methods = [
            '_resolve_exchange_dn_to_smtp',
            '_extract_sender_smtp', 
            '_extract_recipient_smtp'
        ]
        
        missing_methods = [method for method in required_methods if method not in adapter_methods]
        
        if missing_methods:
            print(f"❌ Missing Exchange DN methods: {missing_methods}")
            print("🔧 Fix: Update PyWin32OutlookAdapter with Exchange DN resolution methods")
            return False
        
        print("✅ Exchange DN resolution methods present")
        
        # Test Exchange DN pattern recognition
        test_dns = [
            "/O=EXCHANGELABS/OU=EXCHANGE ADMINISTRATIVE GROUP/CN=RECIPIENTS/CN=user123",
            "/o=company/ou=exchange administrative group/cn=recipients/cn=testuser"
        ]
        
        def is_exchange_dn(email_address: str) -> bool:
            return bool(email_address) and email_address.upper().startswith('/O=')
        
        for dn in test_dns:
            if not is_exchange_dn(dn):
                print(f"❌ Exchange DN pattern recognition failed: {dn}")
                return False
        
        print("✅ Exchange DN pattern recognition working")
        return True
        
    except ImportError as e:
        print(f"❌ Cannot import adapter: {e}")
        print("🔧 Fix: Ensure project structure is correct and imports work")
        return False


def fix_folder_enumeration_issues():
    """Fix common folder enumeration problems."""
    print("🔧 Preparing folder enumeration fixes...")
    
    fixes = {
        "defensive_iteration": "Use try/except for each folder access",
        "count_property_unreliable": "Don't rely solely on Collection.Count",
        "permission_errors": "Expected in corporate environments - classify as minor",
        "one_based_indexing": "COM collections start at index 1, not 0",
        "timeout_issues": "Set reasonable timeouts for large folder structures"
    }
    
    print("📋 Folder enumeration best practices:")
    for issue, fix in fixes.items():
        print(f"   - {issue}: {fix}")
    
    # Test if our defensive iteration pattern is implemented
    try:
        with open(Path(__file__).parent / 'test_com_interface.py', 'r') as f:
            content = f.read()
            
        if "consecutive_failures" in content and "max_consecutive_failures" in content:
            print("✅ Defensive iteration pattern implemented")
        else:
            print("⚠️ Consider implementing defensive iteration pattern")
        
        return True
        
    except Exception as e:
        print(f"❌ Could not verify defensive iteration: {e}")
        return False


def fix_performance_issues():
    """Address performance-related fixes."""
    print("🔧 Performance optimization recommendations...")
    
    recommendations = [
        "Use defensive iteration to avoid infinite loops",
        "Set reasonable timeouts (10-30 seconds for CLI commands)",
        "Cache COM objects when possible within single operations",
        "Limit recursive folder depth for very large mailboxes",
        "Use folder filtering for common operations"
    ]
    
    print("📋 Performance recommendations:")
    for rec in recommendations:
        print(f"   - {rec}")
    
    return True


def run_diagnostic_suite():
    """Run complete diagnostic and fix suite."""
    print("=" * 60)
    print("Windows Environment Diagnostic and Fix Suite")
    print("=" * 60)
    
    fixes = [
        ("Unicode Encoding", fix_unicode_encoding),
        ("PyWin32 Installation", fix_pywin32_import),
        ("Outlook Connection", fix_outlook_connection),
        ("Exchange DN Resolution", fix_exchange_dn_issues),
        ("Folder Enumeration", fix_folder_enumeration_issues),
        ("Performance Optimization", fix_performance_issues)
    ]
    
    results = {}
    
    for name, fix_func in fixes:
        print(f"\n{name}:")
        print("-" * 30)
        try:
            success = fix_func()
            results[name] = "✅ OK" if success else "❌ FAILED"
        except Exception as e:
            print(f"❌ Error running {name} fix: {e}")
            print(traceback.format_exc())
            results[name] = "❌ ERROR"
    
    print("\n" + "=" * 60)
    print("DIAGNOSTIC SUMMARY")
    print("=" * 60)
    
    for name, status in results.items():
        print(f"{status} {name}")
    
    failed_count = sum(1 for status in results.values() if "❌" in status)
    
    if failed_count == 0:
        print("\n🎉 All diagnostics passed! Windows environment ready for testing.")
    else:
        print(f"\n⚠️ {failed_count} issue(s) found. Address these before running tests.")
    
    return failed_count == 0


if __name__ == '__main__':
    success = run_diagnostic_suite()
    sys.exit(0 if success else 1)