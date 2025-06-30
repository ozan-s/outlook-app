#!/usr/bin/env python3
"""
Security Validation for Windows Testing Checkpoint #2

Tests injection prevention, input sanitization, and security hardening
with real corporate email content and malicious inputs.

Run this script on Windows machine with Outlook:
    python test_security_validation.py
"""

import sys
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json
import re

class SecurityValidator:
    """Validates security features with injection prevention and input sanitization"""
    
    def __init__(self):
        self.cli_path = self._find_cli_executable()
        self.test_results = {}
        self.security_violations = []
        
    def _find_cli_executable(self) -> str:
        """Locate the ocli executable"""
        try:
            result = subprocess.run(['ocli', '--help'], 
                                  capture_output=True, text=True, timeout=10)
            if result.returncode == 0:
                return 'ocli'
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        return 'python -m outlook_cli.main'
    
    def run_security_test(self, command_args: List[str], test_name: str, expected_safe: bool = True) -> Dict[str, Any]:
        """Run a security test and analyze the results"""
        print(f"  🔒 Testing: {test_name}")
        
        full_command = f"{self.cli_path} {' '.join(command_args)}"
        
        try:
            start_time = time.time()
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,  # Shorter timeout for security tests
                encoding='utf-8',
                errors='replace'
            )
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Analyze security implications
            security_analysis = self._analyze_security_response(result, expected_safe)
            
            return {
                'test_name': test_name,
                'command': full_command,
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'security_safe': security_analysis['safe'],
                'security_issues': security_analysis['issues'],
                'expected_safe': expected_safe,
                'validation_passed': security_analysis['safe'] == expected_safe
            }
            
        except subprocess.TimeoutExpired:
            return {
                'test_name': test_name,
                'command': full_command,
                'success': False,
                'execution_time': 30,
                'error': 'Security test timed out (potential DoS vulnerability)',
                'security_safe': False,
                'validation_passed': False
            }
        except Exception as e:
            return {
                'test_name': test_name,
                'command': full_command,
                'success': False,
                'execution_time': 0,
                'error': str(e),
                'security_safe': False,
                'validation_passed': False
            }
    
    def _analyze_security_response(self, result: subprocess.CompletedProcess, expected_safe: bool) -> Dict[str, Any]:
        """Analyze command response for security implications"""
        issues = []
        safe = True
        
        # Check for command injection indicators
        if result.returncode == 0:
            # Check stdout for dangerous patterns
            dangerous_patterns = [
                r'system\s*\(',  # System calls
                r'exec\s*\(',    # Exec calls
                r'eval\s*\(',    # Eval calls
                r'__import__',   # Import statements
                r'subprocess',   # Subprocess usage
                r'os\.system',   # OS system calls
                r'shell=True',   # Shell execution
            ]
            
            combined_output = (result.stdout + result.stderr).lower()
            for pattern in dangerous_patterns:
                if re.search(pattern, combined_output, re.IGNORECASE):
                    issues.append(f"Dangerous pattern detected: {pattern}")
                    safe = False
        
        # Check for error handling - malicious inputs should be rejected gracefully
        if not expected_safe:
            if result.returncode == 0:
                issues.append("Malicious input was accepted (should be rejected)")
                safe = False
            elif 'error' not in result.stderr.lower() and 'invalid' not in result.stderr.lower():
                issues.append("Malicious input not properly validated")
                safe = False
        
        # Check for information disclosure
        sensitive_patterns = [
            r'password',
            r'token',
            r'secret',
            r'key',
            r'auth',
            r'credential'
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, result.stdout, re.IGNORECASE):
                issues.append(f"Potential information disclosure: {pattern}")
                safe = False
        
        return {
            'safe': safe,
            'issues': issues
        }
    
    def get_security_test_matrix(self) -> List[Tuple[List[str], str, bool]]:
        """Get security test matrix with command, description, and expected safety"""
        return [
            # SQL Injection attempts (should be safe - parameters are not SQL)
            (['find', '--sender', "'; DROP TABLE emails; --"], 'SQL Injection - DROP TABLE', True),
            (['read', '--subject', "' OR '1'='1"], 'SQL Injection - OR condition', True),
            (['find', '--since', "'; DELETE FROM users; --"], 'SQL Injection - DELETE', True),
            
            # Command injection attempts (should be rejected)
            (['read', '--sender', '; ls -la'], 'Command Injection - ls command', False),
            (['find', '--subject', '`whoami`'], 'Command Injection - backticks', False),
            (['read', '--since', '$(id)'], 'Command Injection - command substitution', False),
            (['find', '--sender', '| cat /etc/passwd'], 'Command Injection - pipe', False),
            (['read', '--subject', '&& rm -rf /'], 'Command Injection - dangerous rm', False),
            
            # Path traversal attempts (should be rejected)
            (['find', '--folder', '../../../etc/passwd'], 'Path Traversal - etc/passwd', False),
            (['read', '--folder', '..\\..\\windows\\system32'], 'Path Traversal - Windows system', False),
            (['find', '--folder', '/../../../../'], 'Path Traversal - root access', False),
            
            # Script injection attempts (should be rejected)
            (['read', '--sender', '<script>alert("xss")</script>'], 'Script Injection - XSS', False),
            (['find', '--subject', 'javascript:alert(1)'], 'Script Injection - JavaScript', False),
            (['read', '--sender', '${7*7}'], 'Template Injection - Math', False),
            
            # Buffer overflow attempts (should be handled gracefully)
            (['find', '--sender', 'A' * 10000], 'Buffer Overflow - Long sender', True),
            (['read', '--subject', 'B' * 50000], 'Buffer Overflow - Long subject', True),
            
            # Unicode and encoding attacks (should be safe)
            (['find', '--sender', 'admin\\u0000'], 'Unicode Null Byte', False),
            (['read', '--subject', '%2e%2e%2f'], 'URL Encoding Attack', False),
            (['find', '--sender', '\\x00\\x01\\x02'], 'Binary Data Injection', False),
            
            # LDAP injection (relevant for Exchange environments)
            (['read', '--sender', '(cn=*))(|(cn=*'], 'LDAP Injection - Wildcard', False),
            (['find', '--sender', '*)(uid=*))(|(uid=*'], 'LDAP Injection - Complex', False),
            
            # Resource exhaustion attempts (should timeout gracefully)
            (['find', '--since', '1900-01-01', '--all'], 'Resource Exhaustion - All historic', True),
            (['read', '--sender', '*', '--all'], 'Resource Exhaustion - All senders', True),
            
            # Valid inputs (should be safe and work)
            (['folders'], 'Valid Command - Folders', True),
            (['read', '--limit', '5'], 'Valid Command - Read Limited', True),
            (['find', '--since', '1d'], 'Valid Command - Find Recent', True),
        ]
    
    def run_comprehensive_security_tests(self) -> Dict[str, Any]:
        """Run comprehensive security validation"""
        print("🔒 Running comprehensive security validation...")
        
        test_matrix = self.get_security_test_matrix()
        results = {
            'total_tests': len(test_matrix),
            'passed_tests': 0,
            'failed_tests': 0,
            'security_violations': 0,
            'test_results': {},
            'security_summary': {},
            'validation_passed': False
        }
        
        for test_args, test_name, expected_safe in test_matrix:
            test_result = self.run_security_test(test_args, test_name, expected_safe)
            
            if test_result['validation_passed']:
                results['passed_tests'] += 1
                status = "✅ SECURE"
            else:
                results['failed_tests'] += 1
                status = "❌ VULNERABLE"
                if not test_result['security_safe']:
                    results['security_violations'] += 1
                    self.security_violations.append({
                        'test_name': test_name,
                        'command': test_result['command'],
                        'issues': test_result.get('security_issues', [])
                    })
            
            results['test_results'][test_name] = test_result
            
            print(f"    {status} - {test_result['execution_time']:.2f}s")
            
            # Brief pause between security tests
            time.sleep(0.2)
        
        # Calculate security metrics
        pass_rate = (results['passed_tests'] / results['total_tests']) * 100
        vulnerability_rate = (results['security_violations'] / results['total_tests']) * 100
        
        results['security_summary'] = {
            'pass_rate_percent': pass_rate,
            'vulnerability_rate_percent': vulnerability_rate,
            'total_vulnerabilities': results['security_violations'],
            'security_rating': self._calculate_security_rating(pass_rate, vulnerability_rate),
            'critical_security_issues': len(self.security_violations)
        }
        
        # Validation criteria: 95% pass rate and 0% vulnerability rate
        results['validation_passed'] = (
            pass_rate >= 95.0 and 
            vulnerability_rate == 0.0
        )
        
        return results
    
    def _calculate_security_rating(self, pass_rate: float, vulnerability_rate: float) -> str:
        """Calculate overall security rating"""
        if vulnerability_rate > 0:
            return 'CRITICAL'
        elif pass_rate >= 98.0:
            return 'EXCELLENT'
        elif pass_rate >= 95.0:
            return 'GOOD'
        elif pass_rate >= 90.0:
            return 'ACCEPTABLE'
        else:
            return 'POOR'
    
    def generate_security_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive security report"""
        report = []
        report.append("=" * 80)
        report.append("SECURITY VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Security Tests: {results['total_tests']}")
        report.append(f"Passed: {results['passed_tests']}")
        report.append(f"Failed: {results['failed_tests']}")
        report.append(f"Security Violations: {results['security_violations']}")
        report.append(f"Pass Rate: {results['security_summary']['pass_rate_percent']:.1f}%")
        report.append(f"Security Rating: {results['security_summary']['security_rating']}")
        report.append(f"Overall Validation: {'✅ PASSED' if results['validation_passed'] else '❌ FAILED'}")
        report.append("")
        
        # Security summary
        summary = results['security_summary']
        report.append("SECURITY SUMMARY:")
        report.append(f"Vulnerability Rate: {summary['vulnerability_rate_percent']:.1f}%")
        report.append(f"Critical Issues: {summary['critical_security_issues']}")
        report.append(f"Security Rating: {summary['security_rating']}")
        report.append("")
        
        # Critical vulnerabilities
        if self.security_violations:
            report.append("🚨 CRITICAL SECURITY VULNERABILITIES:")
            for violation in self.security_violations:
                report.append(f"  • {violation['test_name']}")
                report.append(f"    Command: {violation['command']}")
                for issue in violation['issues']:
                    report.append(f"    Issue: {issue}")
                report.append("")
        
        # Detailed test results
        report.append("DETAILED SECURITY TEST RESULTS:")
        for test_name, result in results['test_results'].items():
            if result['validation_passed']:
                status = "✅ SECURE"
            else:
                status = "❌ VULNERABLE"
                
            safety = "SAFE" if result.get('security_safe', False) else "UNSAFE"
            expected = "SAFE" if result.get('expected_safe', True) else "UNSAFE"
            
            report.append(f"  {test_name:<40} | {status:<12} | Expected: {expected} | Actual: {safety}")
            
            if result.get('security_issues'):
                for issue in result['security_issues']:
                    report.append(f"    Issue: {issue}")
        
        report.append("")
        report.append("SECURITY TEST CATEGORIES:")
        report.append("  • SQL Injection Prevention")
        report.append("  • Command Injection Prevention")
        report.append("  • Path Traversal Prevention")
        report.append("  • Script Injection Prevention")
        report.append("  • Buffer Overflow Handling")
        report.append("  • Unicode/Encoding Attack Prevention")
        report.append("  • LDAP Injection Prevention")
        report.append("  • Resource Exhaustion Protection")
        report.append("  • Input Validation and Sanitization")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def test_security_validation_framework():
    """Test that security validation framework works"""
    validator = SecurityValidator()
    
    # Test framework components
    assert hasattr(validator, 'cli_path'), "CLI path not found"
    assert hasattr(validator, 'run_security_test'), "Security test method missing"
    assert hasattr(validator, '_analyze_security_response'), "Security analysis missing"
    
    # Test security test matrix
    test_matrix = validator.get_security_test_matrix()
    assert len(test_matrix) >= 20, f"Expected at least 20 security tests, got {len(test_matrix)}"
    
    print("✅ Security validation framework test passed")

if __name__ == "__main__":
    print("🔒 Security Validation for Windows Testing Checkpoint #2")
    print("=" * 60)
    
    # Test framework first
    try:
        test_security_validation_framework()
    except AssertionError as e:
        print(f"❌ Framework test failed: {e}")
        sys.exit(1)
    
    # Run comprehensive security validation
    validator = SecurityValidator()
    results = validator.run_comprehensive_security_tests()
    
    # Generate and display report
    report = validator.generate_security_report(results)
    print("\n" + report)
    
    # Save report to file
    report_filename = f"security_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📁 Security report saved to: {report_filename}")
    
    # Exit with appropriate code
    if results['validation_passed']:
        print("\n🎉 Security validation PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Security validation FAILED!")
        print("🚨 CRITICAL SECURITY ISSUES DETECTED!")
        sys.exit(1)