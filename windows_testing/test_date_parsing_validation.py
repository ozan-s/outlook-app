#!/usr/bin/env python3
"""
Date Parsing Validation for Windows Testing Checkpoint #2

Tests all 20+ date formats with real Outlook data to ensure
proper parsing in corporate environments.

Run this script on Windows machine with Outlook:
    python test_date_parsing_validation.py
"""

import sys
import os
import subprocess
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json

class DateParsingValidator:
    """Validates all date parsing formats with real Windows Outlook data"""
    
    def __init__(self):
        self.cli_path = self._find_cli_executable()
        self.test_results = {}
        self.validation_errors = []
        
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
    
    def run_cli_with_date_filter(self, date_filter_arg: str, timeout: int = 60) -> Dict[str, Any]:
        """Run CLI command with specific date filter"""
        command = f"{self.cli_path} find --since {date_filter_arg} --limit 5"
        
        try:
            start_time = time.time()
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            end_time = time.time()
            
            return {
                'command': command,
                'date_filter': date_filter_arg,
                'returncode': result.returncode,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'execution_time': end_time - start_time,
                'success': result.returncode == 0
            }
        except Exception as e:
            return {
                'command': command,
                'date_filter': date_filter_arg,
                'returncode': -1,
                'stdout': '',
                'stderr': f'Error: {str(e)}',
                'execution_time': 0,
                'success': False
            }
    
    def get_comprehensive_date_formats(self) -> List[Tuple[str, str]]:
        """Get all date formats to test with descriptions"""
        return [
            # Time units - relative
            ('1m', 'One minute ago'),
            ('5m', 'Five minutes ago'),
            ('30m', 'Thirty minutes ago'),
            ('1h', 'One hour ago'),
            ('2h', 'Two hours ago'),
            ('12h', 'Twelve hours ago'),
            ('1d', 'One day ago'),
            ('2d', 'Two days ago'),
            ('7d', 'Seven days ago'),
            ('1w', 'One week ago'),
            ('2w', 'Two weeks ago'),
            ('1M', 'One month ago'),
            ('2M', 'Two months ago'),
            ('6M', 'Six months ago'),
            ('1y', 'One year ago'),
            
            # Named dates
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('tomorrow', 'Tomorrow'),
            
            # Weekdays
            ('monday', 'Monday'),
            ('tuesday', 'Tuesday'),
            ('wednesday', 'Wednesday'),
            ('thursday', 'Thursday'),
            ('friday', 'Friday'),
            ('saturday', 'Saturday'),
            ('sunday', 'Sunday'),
            ('last-monday', 'Last Monday'),
            ('last-friday', 'Last Friday'),
            
            # Periods
            ('this-week', 'This week'),
            ('last-week', 'Last week'),
            ('this-month', 'This month'),
            ('last-month', 'Last month'),
            ('this-year', 'This year'),
            ('last-year', 'Last year'),
            
            # Absolute dates
            ('2025-01-01', 'Absolute date: January 1, 2025'),
            ('2024-12-25', 'Absolute date: December 25, 2024'),
            ('2024-06-15', 'Absolute date: June 15, 2024'),
        ]
    
    def validate_all_date_formats(self) -> Dict[str, Any]:
        """Validate all date formats with real Outlook data"""
        print("🔍 Testing comprehensive date parsing formats...")
        
        date_formats = self.get_comprehensive_date_formats()
        results = {
            'total_formats': len(date_formats),
            'successful_formats': 0,
            'failed_formats': 0,
            'format_results': {},
            'performance_metrics': {},
            'validation_summary': {}
        }
        
        for date_format, description in date_formats:
            print(f"  Testing: {date_format} ({description})")
            
            result = self.run_cli_with_date_filter(date_format)
            
            # Analyze result
            success = result['success']
            if success:
                results['successful_formats'] += 1
                status = "✅ PASS"
            else:
                results['failed_formats'] += 1
                status = "❌ FAIL"
                self.validation_errors.append({
                    'date_format': date_format,
                    'description': description,
                    'error': result['stderr']
                })
            
            results['format_results'][date_format] = {
                'description': description,
                'success': success,
                'execution_time': result['execution_time'],
                'stdout_length': len(result['stdout']),
                'error_message': result['stderr'] if not success else None
            }
            
            print(f"    {status} - {result['execution_time']:.2f}s")
            
            # Brief pause to avoid overwhelming Outlook COM interface
            time.sleep(0.1)
        
        # Calculate success rate
        success_rate = (results['successful_formats'] / results['total_formats']) * 100
        results['validation_summary'] = {
            'success_rate_percent': success_rate,
            'total_execution_time': sum(r['execution_time'] for r in results['format_results'].values()),
            'average_execution_time': sum(r['execution_time'] for r in results['format_results'].values()) / len(results['format_results']),
            'validation_passed': success_rate >= 90.0  # 90% success rate required
        }
        
        return results
    
    def generate_validation_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append("=" * 80)
        report.append("DATE PARSING VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Formats Tested: {results['total_formats']}")
        report.append(f"Successful: {results['successful_formats']}")
        report.append(f"Failed: {results['failed_formats']}")
        report.append(f"Success Rate: {results['validation_summary']['success_rate_percent']:.1f}%")
        report.append(f"Overall Validation: {'✅ PASSED' if results['validation_summary']['validation_passed'] else '❌ FAILED'}")
        report.append("")
        
        # Performance metrics
        report.append("PERFORMANCE METRICS:")
        report.append(f"Total Execution Time: {results['validation_summary']['total_execution_time']:.2f}s")
        report.append(f"Average Time per Format: {results['validation_summary']['average_execution_time']:.2f}s")
        report.append("")
        
        # Detailed results
        report.append("DETAILED RESULTS:")
        for date_format, details in results['format_results'].items():
            status = "✅ PASS" if details['success'] else "❌ FAIL"
            report.append(f"  {date_format:15} | {status} | {details['execution_time']:.2f}s | {details['description']}")
            if not details['success'] and details['error_message']:
                report.append(f"                    Error: {details['error_message'][:100]}...")
        
        # Failed formats summary
        if self.validation_errors:
            report.append("")
            report.append("FAILED FORMATS SUMMARY:")
            for error in self.validation_errors:
                report.append(f"  • {error['date_format']} ({error['description']})")
                report.append(f"    Error: {error['error']}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def test_date_parsing_validation_framework():
    """Test that date parsing validation framework works"""
    validator = DateParsingValidator()
    
    # Test framework components
    assert hasattr(validator, 'cli_path'), "CLI path not found"
    assert hasattr(validator, 'get_comprehensive_date_formats'), "Date formats method missing"
    assert hasattr(validator, 'validate_all_date_formats'), "Validation method missing"
    
    # Test that we have comprehensive date formats
    formats = validator.get_comprehensive_date_formats()
    assert len(formats) >= 30, f"Expected at least 30 date formats, got {len(formats)}"
    
    print("✅ Date parsing validation framework test passed")

if __name__ == "__main__":
    print("🔍 Date Parsing Validation for Windows Testing Checkpoint #2")
    print("=" * 60)
    
    # Test framework first
    try:
        test_date_parsing_validation_framework()
    except AssertionError as e:
        print(f"❌ Framework test failed: {e}")
        sys.exit(1)
    
    # Run comprehensive validation
    validator = DateParsingValidator()
    results = validator.validate_all_date_formats()
    
    # Generate and display report
    report = validator.generate_validation_report(results)
    print("\n" + report)
    
    # Save report to file
    report_filename = f"date_parsing_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📁 Detailed report saved to: {report_filename}")
    
    # Exit with appropriate code
    if results['validation_summary']['validation_passed']:
        print("\n🎉 Date parsing validation PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Date parsing validation FAILED!")
        sys.exit(1)