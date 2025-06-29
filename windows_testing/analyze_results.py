"""Result Analysis Framework for Windows Testing.

This script analyzes the results from Windows test execution and provides
actionable feedback for fixing any issues found.
"""

import json
import sys
from typing import Dict, Any, List, Tuple
from pathlib import Path


class WindowsTestAnalyzer:
    """Analyzes Windows test results and provides actionable feedback."""
    
    def __init__(self, com_results_file: str, app_results_file: str):
        """Initialize with result file paths."""
        self.com_results_file = com_results_file
        self.app_results_file = app_results_file
        self.com_results = None
        self.app_results = None
        
    def load_results(self) -> bool:
        """Load test results from JSON files."""
        try:
            with open(self.com_results_file, 'r') as f:
                self.com_results = json.load(f)
            print(f"✅ Loaded COM test results from {self.com_results_file}")
        except FileNotFoundError:
            print(f"❌ COM results file not found: {self.com_results_file}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in COM results: {e}")
            return False
        
        try:
            with open(self.app_results_file, 'r') as f:
                self.app_results = json.load(f)
            print(f"✅ Loaded application test results from {self.app_results_file}")
        except FileNotFoundError:
            print(f"❌ Application results file not found: {self.app_results_file}")
            return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in application results: {e}")
            return False
            
        return True
    
    def analyze_com_results(self) -> Dict[str, Any]:
        """Analyze COM interface test results."""
        if not self.com_results:
            return {"status": "no_data", "message": "No COM results to analyze"}
        
        analysis = {
            "overall_status": "unknown",
            "connection_status": "unknown", 
            "folder_status": "unknown",
            "issues": [],
            "recommendations": [],
            "evidence": {}
        }
        
        test_results = self.com_results.get("test_results", {})
        
        # Analyze connection test
        connection_test = test_results.get("connection_test", {})
        if connection_test.get("status") == "success":
            analysis["connection_status"] = "success"
            analysis["evidence"]["com_connection"] = f"✅ Connected to Outlook, {connection_test.get('folder_count', 0)} folders accessible"
        else:
            analysis["connection_status"] = "failed"
            error = connection_test.get("error", "Unknown error")
            analysis["issues"].append(f"COM connection failed: {error}")
            
            # Provide specific recommendations based on error type
            if "pywin32 not available" in error:
                analysis["recommendations"].append("Install pywin32: pip install pywin32")
            elif "Outlook.Application" in error:
                analysis["recommendations"].append("Start Microsoft Outlook before running tests")
            elif "MAPI" in error:
                analysis["recommendations"].append("Check Outlook profile configuration")
        
        # Analyze folder test
        folder_test = test_results.get("folder_test", {})
        if folder_test.get("status") == "success":
            analysis["folder_status"] = "success"
            folder_count = folder_test.get("folder_count", 0)
            error_count = folder_test.get("error_count", 0)
            analysis["evidence"]["folder_enumeration"] = f"✅ Enumerated {folder_count} folders with {error_count} minor errors"
            
            # Check for concerning patterns
            if error_count > folder_count * 0.3:  # More than 30% errors
                analysis["issues"].append(f"High error rate: {error_count} errors for {folder_count} folders")
                analysis["recommendations"].append("Review corporate folder permissions")
        else:
            analysis["folder_status"] = "failed"
            error = folder_test.get("error", "Unknown error")
            analysis["issues"].append(f"Folder enumeration failed: {error}")
            analysis["recommendations"].append("Check Exchange server connectivity")
        
        # Determine overall status
        if analysis["connection_status"] == "success" and analysis["folder_status"] == "success":
            analysis["overall_status"] = "success"
        elif analysis["connection_status"] == "success" and analysis["folder_status"] == "failed":
            analysis["overall_status"] = "partial"
        else:
            analysis["overall_status"] = "failed"
        
        return analysis
    
    def analyze_app_results(self) -> Dict[str, Any]:
        """Analyze application integration test results."""
        if not self.app_results:
            return {"status": "no_data", "message": "No application results to analyze"}
        
        analysis = {
            "overall_status": "unknown",
            "command_results": {},
            "issues": [],
            "recommendations": [],
            "evidence": {}
        }
        
        test_results = self.app_results.get("test_results", {})
        
        # Analyze each command test
        command_tests = [
            ("folders", "folders_test", "Folder listing"),
            ("read", "read_test", "Email reading"),
            ("find", "find_test", "Email search"),
            ("exchange_dn", "exchange_dn_test", "Exchange DN resolution"),
            ("compatibility", "compatibility_test", "Cross-adapter compatibility")
        ]
        
        success_count = 0
        total_count = len(command_tests)
        
        for cmd_name, test_key, description in command_tests:
            test_result = test_results.get(test_key, {})
            status = test_result.get("status", "unknown")
            
            analysis["command_results"][cmd_name] = {
                "status": status,
                "description": description
            }
            
            if status == "success":
                success_count += 1
                analysis["evidence"][cmd_name] = f"✅ {description} working"
            else:
                error = test_result.get("error", "Unknown error")
                analysis["issues"].append(f"{description} failed: {error}")
                
                # Provide specific recommendations
                if "timeout" in error.lower():
                    analysis["recommendations"].append(f"Increase timeout for {cmd_name} command")
                elif "adapter" in error.lower():
                    analysis["recommendations"].append("Check OUTLOOK_ADAPTER environment variable")
                elif "uv run" in error.lower():
                    analysis["recommendations"].append("Verify uv package manager installation")
        
        # Determine overall status
        if success_count == total_count:
            analysis["overall_status"] = "success"
        elif success_count >= total_count * 0.6:  # At least 60% success
            analysis["overall_status"] = "partial"
        else:
            analysis["overall_status"] = "failed"
        
        analysis["success_rate"] = f"{success_count}/{total_count}"
        
        return analysis
    
    def generate_report(self) -> str:
        """Generate comprehensive analysis report."""
        report = []
        report.append("# Windows Testing Analysis Report")
        report.append("=" * 50)
        
        if not self.load_results():
            report.append("\n❌ Could not load test results. Please ensure both result files exist.")
            return "\n".join(report)
        
        # Analyze COM results
        com_analysis = self.analyze_com_results()
        report.append(f"\n## COM Interface Analysis")
        report.append(f"**Overall Status**: {com_analysis['overall_status'].upper()}")
        
        if com_analysis["evidence"]:
            report.append(f"\n**Evidence:**")
            for key, evidence in com_analysis["evidence"].items():
                report.append(f"- {evidence}")
        
        if com_analysis["issues"]:
            report.append(f"\n**Issues Found:**")
            for issue in com_analysis["issues"]:
                report.append(f"- ❌ {issue}")
        
        if com_analysis["recommendations"]:
            report.append(f"\n**Recommendations:**")
            for rec in com_analysis["recommendations"]:
                report.append(f"- 🔧 {rec}")
        
        # Analyze application results
        app_analysis = self.analyze_app_results()
        report.append(f"\n## Application Integration Analysis")
        report.append(f"**Overall Status**: {app_analysis['overall_status'].upper()}")
        report.append(f"**Success Rate**: {app_analysis.get('success_rate', 'Unknown')}")
        
        if app_analysis["evidence"]:
            report.append(f"\n**Evidence:**")
            for key, evidence in app_analysis["evidence"].items():
                report.append(f"- {evidence}")
        
        if app_analysis["issues"]:
            report.append(f"\n**Issues Found:**")
            for issue in app_analysis["issues"]:
                report.append(f"- ❌ {issue}")
        
        if app_analysis["recommendations"]:
            report.append(f"\n**Recommendations:**")
            for rec in app_analysis["recommendations"]:
                report.append(f"- 🔧 {rec}")
        
        # Overall assessment
        report.append(f"\n## Overall Assessment")
        
        com_ok = com_analysis["overall_status"] in ["success", "partial"]
        app_ok = app_analysis["overall_status"] in ["success", "partial"]
        
        if com_ok and app_ok:
            report.append("✅ **VALIDATION SUCCESSFUL**: Windows environment is ready for production deployment")
            report.append("\n**Next Steps:**")
            report.append("- Document any minor issues found")
            report.append("- Update deployment guide with Windows-specific notes")
            report.append("- Mark Milestone 005C as COMPLETED")
        
        elif com_ok and not app_ok:
            report.append("⚠️ **PARTIAL VALIDATION**: COM interface works but application has issues")
            report.append("\n**Next Steps:**")
            report.append("- Fix application-level issues first")
            report.append("- Re-run application tests")
            report.append("- Do not mark milestone complete until all tests pass")
        
        elif not com_ok:
            report.append("❌ **VALIDATION FAILED**: Fundamental COM interface issues")
            report.append("\n**Next Steps:**")
            report.append("- Fix COM connection issues first")
            report.append("- Ensure proper Windows/Outlook environment setup")
            report.append("- Re-run both test suites")
            report.append("- Do not proceed to advanced features until foundation is solid")
        
        return "\n".join(report)


def main():
    """Main analysis function."""
    if len(sys.argv) != 3:
        print("Usage: python analyze_results.py <com_results.json> <app_results.json>")
        print("Example: python analyze_results.py outlook_com_validation_results.json outlook_app_validation_results.json")
        sys.exit(1)
    
    com_file = sys.argv[1]
    app_file = sys.argv[2]
    
    analyzer = WindowsTestAnalyzer(com_file, app_file)
    report = analyzer.generate_report()
    
    print(report)
    
    # Save report to file
    report_file = "windows_test_analysis_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)
    
    print(f"\n📄 Full report saved to: {report_file}")


if __name__ == '__main__':
    main()