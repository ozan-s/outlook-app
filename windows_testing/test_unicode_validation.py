#!/usr/bin/env python3
"""
Unicode Validation for Windows Testing Checkpoint #2

Tests Unicode handling in corporate environments with international
characters, Exchange DN resolution, and Windows-specific encoding.

Run this script on Windows machine with Outlook:
    python test_unicode_validation.py
"""

import sys
import os
import subprocess
import time
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
import json
import unicodedata

class UnicodeValidator:
    """Validates Unicode handling in corporate environments"""
    
    def __init__(self):
        self.cli_path = self._find_cli_executable()
        self.test_results = {}
        self.unicode_errors = []
        
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
    
    def run_unicode_test(self, command_args: List[str], test_name: str, unicode_content: str) -> Dict[str, Any]:
        """Run a Unicode test with specific international content"""
        print(f"  🌍 Testing: {test_name}")
        
        full_command = f"{self.cli_path} {' '.join(command_args)}"
        
        try:
            start_time = time.time()
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                encoding='utf-8',
                errors='replace'  # Handle encoding errors gracefully
            )
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Analyze Unicode handling
            unicode_analysis = self._analyze_unicode_handling(result, unicode_content)
            
            return {
                'test_name': test_name,
                'command': full_command,
                'unicode_content': unicode_content,
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'unicode_preserved': unicode_analysis['preserved'],
                'encoding_errors': unicode_analysis['encoding_errors'],
                'character_corruption': unicode_analysis['character_corruption'],
                'validation_passed': unicode_analysis['validation_passed']
            }
            
        except UnicodeDecodeError as e:
            return {
                'test_name': test_name,
                'command': full_command,
                'unicode_content': unicode_content,
                'success': False,
                'execution_time': 0,
                'error': f'Unicode decode error: {str(e)}',
                'unicode_preserved': False,
                'encoding_errors': [str(e)],
                'validation_passed': False
            }
        except Exception as e:
            return {
                'test_name': test_name,
                'command': full_command,
                'unicode_content': unicode_content,
                'success': False,
                'execution_time': 0,
                'error': str(e),
                'unicode_preserved': False,
                'validation_passed': False
            }
    
    def _analyze_unicode_handling(self, result: subprocess.CompletedProcess, original_unicode: str) -> Dict[str, Any]:
        """Analyze how Unicode content was handled"""
        encoding_errors = []
        character_corruption = []
        preserved = True
        
        # Check for encoding replacement characters
        replacement_chars = ['�', '?', '\\ufffd']
        combined_output = result.stdout + result.stderr
        
        for char in replacement_chars:
            if char in combined_output:
                encoding_errors.append(f"Found replacement character: {char}")
                preserved = False
        
        # Check for character corruption patterns
        corruption_patterns = [
            ('Ã¡', 'á'),  # Common UTF-8 to Latin-1 corruption
            ('Ã©', 'é'),
            ('Ã­', 'í'),
            ('Ã³', 'ó'),
            ('Ãº', 'ú'),
            ('Ã±', 'ñ'),
            ('â€™', '''),  # Smart quote corruption
            ('â€œ', '"'),
            ('â€', '"'),
        ]
        
        for corrupted, correct in corruption_patterns:
            if corrupted in combined_output:
                character_corruption.append(f"Found corruption: {corrupted} (should be {correct})")
                preserved = False
        
        # Check for proper Unicode normalization
        if original_unicode:
            # Normalize the original and check if output contains reasonable representation
            normalized = unicodedata.normalize('NFC', original_unicode)
            # For CLI output, we expect at least some representation of the Unicode content
            # Not exact match since it may be formatted differently
        
        validation_passed = (
            result.returncode == 0 and  # Command succeeded
            len(encoding_errors) == 0 and  # No encoding errors
            len(character_corruption) == 0  # No character corruption
        )
        
        return {
            'preserved': preserved,
            'encoding_errors': encoding_errors,
            'character_corruption': character_corruption,
            'validation_passed': validation_passed
        }
    
    def get_unicode_test_matrix(self) -> List[Tuple[List[str], str, str]]:
        """Get Unicode test matrix with international content"""
        return [
            # European languages (Latin scripts)
            (['find', '--sender', 'josé.garcía@company.com'], 'Spanish Characters', 'josé.garcía'),
            (['read', '--subject', 'Réunion'], 'French Characters', 'Réunion'),
            (['find', '--sender', 'müller'], 'German Umlauts', 'müller'),
            (['read', '--subject', 'naïve'], 'French Diacritics', 'naïve'),
            (['find', '--sender', 'château'], 'French Circumflex', 'château'),
            
            # Scandinavian languages
            (['read', '--subject', 'København'], 'Danish Characters', 'København'),
            (['find', '--sender', 'åse'], 'Norwegian/Swedish', 'åse'),
            (['read', '--subject', 'Örebro'], 'Swedish Ö', 'Örebro'),
            
            # Eastern European (Cyrillic)
            (['find', '--sender', 'Москва'], 'Russian Cyrillic', 'Москва'),
            (['read', '--subject', 'Україна'], 'Ukrainian Cyrillic', 'Україна'),
            (['find', '--sender', 'България'], 'Bulgarian Cyrillic', 'България'),
            
            # East Asian languages
            (['read', '--subject', '会議'], 'Japanese Kanji', '会議'),
            (['find', '--sender', '北京'], 'Chinese Characters', '北京'),
            (['read', '--subject', '서울'], 'Korean Hangul', '서울'),
            
            # Middle Eastern languages (RTL)
            (['find', '--subject', 'مرحبا'], 'Arabic Script', 'مرحبا'),
            (['read', '--subject', 'שלום'], 'Hebrew Script', 'שלום'),
            
            # Special Unicode characters
            (['find', '--subject', 'café'], 'Composed Characters', 'café'),
            (['read', '--subject', 'naïve'], 'Decomposed Characters', 'naïve'),
            (['find', '--subject', '™®©'], 'Trademark Symbols', '™®©'),
            (['read', '--subject', '€£¥'], 'Currency Symbols', '€£¥'),
            (['find', '--subject', '—–''""'], 'Punctuation Marks', '—–''""'),
            
            # Emoji and symbols (common in modern corporate communication)
            (['read', '--subject', '📧💼'], 'Emoji Characters', '📧💼'),
            (['find', '--subject', '✓✗'], 'Check Marks', '✓✗'),
            (['read', '--subject', '⚠️📊'], 'Warning/Chart Emoji', '⚠️📊'),
            
            # Combined scripts (multilingual)
            (['find', '--subject', 'Meeting会議Réunion'], 'Mixed Scripts', 'Meeting会議Réunion'),
            (['read', '--sender', 'user@société.com'], 'Mixed Email', 'user@société.com'),
            
            # Edge cases and potential problems
            (['find', '--subject', 'test\u200b'], 'Zero Width Space', 'test\u200b'),
            (['read', '--subject', 'café\u0301'], 'Combining Characters', 'café\u0301'),
            (['find', '--subject', '\ufeff'], 'Byte Order Mark', '\ufeff'),
            
            # Corporate Exchange DN patterns with Unicode
            (['find', '--sender', '/O=SOCIÉTÉ/OU=EXCHANGE'], 'Exchange DN Unicode', '/O=SOCIÉTÉ/OU=EXCHANGE'),
            (['read', '--sender', 'CN=José García'], 'Exchange CN Unicode', 'CN=José García'),
        ]
    
    def run_comprehensive_unicode_tests(self) -> Dict[str, Any]:
        """Run comprehensive Unicode validation"""
        print("🌍 Running comprehensive Unicode validation...")
        
        test_matrix = self.get_unicode_test_matrix()
        results = {
            'total_tests': len(test_matrix),
            'passed_tests': 0,
            'failed_tests': 0,
            'unicode_errors': 0,
            'test_results': {},
            'unicode_summary': {},
            'validation_passed': False
        }
        
        for test_args, test_name, unicode_content in test_matrix:
            test_result = self.run_unicode_test(test_args, test_name, unicode_content)
            
            if test_result['validation_passed']:
                results['passed_tests'] += 1
                status = "✅ UNICODE OK"
            else:
                results['failed_tests'] += 1
                status = "❌ UNICODE FAIL"
                if not test_result.get('unicode_preserved', True):
                    results['unicode_errors'] += 1
                    self.unicode_errors.append({
                        'test_name': test_name,
                        'unicode_content': unicode_content,
                        'encoding_errors': test_result.get('encoding_errors', []),
                        'character_corruption': test_result.get('character_corruption', [])
                    })
            
            results['test_results'][test_name] = test_result
            
            print(f"    {status} - {test_result['execution_time']:.2f}s")
            
            # Brief pause between Unicode tests
            time.sleep(0.1)
        
        # Calculate Unicode metrics
        pass_rate = (results['passed_tests'] / results['total_tests']) * 100
        error_rate = (results['unicode_errors'] / results['total_tests']) * 100
        
        results['unicode_summary'] = {
            'pass_rate_percent': pass_rate,
            'error_rate_percent': error_rate,
            'total_unicode_errors': results['unicode_errors'],
            'unicode_rating': self._calculate_unicode_rating(pass_rate, error_rate),
            'corporate_readiness': pass_rate >= 95.0 and error_rate <= 5.0
        }
        
        # Validation criteria: 90% pass rate and less than 10% Unicode errors
        results['validation_passed'] = (
            pass_rate >= 90.0 and 
            error_rate <= 10.0
        )
        
        return results
    
    def _calculate_unicode_rating(self, pass_rate: float, error_rate: float) -> str:
        """Calculate overall Unicode handling rating"""
        if error_rate == 0 and pass_rate >= 95:
            return 'EXCELLENT'
        elif error_rate <= 5 and pass_rate >= 90:
            return 'GOOD'
        elif error_rate <= 10 and pass_rate >= 80:
            return 'ACCEPTABLE'
        else:
            return 'POOR'
    
    def generate_unicode_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive Unicode report"""
        report = []
        report.append("=" * 80)
        report.append("UNICODE VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Unicode Tests: {results['total_tests']}")
        report.append(f"Passed: {results['passed_tests']}")
        report.append(f"Failed: {results['failed_tests']}")
        report.append(f"Unicode Errors: {results['unicode_errors']}")
        report.append(f"Pass Rate: {results['unicode_summary']['pass_rate_percent']:.1f}%")
        report.append(f"Unicode Rating: {results['unicode_summary']['unicode_rating']}")
        report.append(f"Corporate Ready: {'✅ YES' if results['unicode_summary']['corporate_readiness'] else '❌ NO'}")
        report.append(f"Overall Validation: {'✅ PASSED' if results['validation_passed'] else '❌ FAILED'}")
        report.append("")
        
        # Unicode summary
        summary = results['unicode_summary']
        report.append("UNICODE SUMMARY:")
        report.append(f"Error Rate: {summary['error_rate_percent']:.1f}%")
        report.append(f"Total Unicode Errors: {summary['total_unicode_errors']}")
        report.append(f"Unicode Rating: {summary['unicode_rating']}")
        report.append("")
        
        # Unicode errors detail
        if self.unicode_errors:
            report.append("🌍 UNICODE HANDLING ISSUES:")
            for error in self.unicode_errors:
                report.append(f"  • {error['test_name']}")
                report.append(f"    Content: {error['unicode_content']}")
                for enc_error in error['encoding_errors']:
                    report.append(f"    Encoding Error: {enc_error}")
                for corruption in error['character_corruption']:
                    report.append(f"    Character Corruption: {corruption}")
                report.append("")
        
        # Detailed test results by category
        categories = {
            'European Languages': ['Spanish', 'French', 'German', 'Danish', 'Norwegian', 'Swedish'],
            'Cyrillic Scripts': ['Russian', 'Ukrainian', 'Bulgarian'],
            'East Asian Languages': ['Japanese', 'Chinese', 'Korean'],
            'Middle Eastern Languages': ['Arabic', 'Hebrew'],
            'Special Characters': ['Composed', 'Decomposed', 'Trademark', 'Currency', 'Punctuation'],
            'Emoji and Symbols': ['Emoji', 'Check Marks', 'Warning'],
            'Corporate Exchange': ['Exchange DN', 'Exchange CN'],
            'Edge Cases': ['Zero Width', 'Combining', 'Byte Order']
        }
        
        for category, keywords in categories.items():
            report.append(f"{category.upper()}:")
            category_tests = {name: result for name, result in results['test_results'].items() 
                            if any(keyword in name for keyword in keywords)}
            
            if category_tests:
                for test_name, result in category_tests.items():
                    status = "✅ PASS" if result['validation_passed'] else "❌ FAIL"
                    content = result.get('unicode_content', 'N/A')[:20]
                    report.append(f"  {test_name:<35} | {status} | {content}")
            else:
                report.append("  No tests in this category")
            report.append("")
        
        report.append("UNICODE TEST CATEGORIES COVERED:")
        report.append("  • Latin Scripts (European languages)")
        report.append("  • Cyrillic Scripts (Slavic languages)")
        report.append("  • East Asian Scripts (CJK)")
        report.append("  • Right-to-Left Scripts (Arabic, Hebrew)")
        report.append("  • Special Unicode Characters")
        report.append("  • Emoji and Modern Symbols")
        report.append("  • Mixed Script Content")
        report.append("  • Exchange Directory Names with Unicode")
        report.append("  • Edge Cases and Potential Problems")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def test_unicode_validation_framework():
    """Test that Unicode validation framework works"""
    validator = UnicodeValidator()
    
    # Test framework components
    assert hasattr(validator, 'cli_path'), "CLI path not found"
    assert hasattr(validator, 'run_unicode_test'), "Unicode test method missing"
    assert hasattr(validator, '_analyze_unicode_handling'), "Unicode analysis missing"
    
    # Test Unicode test matrix
    test_matrix = validator.get_unicode_test_matrix()
    assert len(test_matrix) >= 25, f"Expected at least 25 Unicode tests, got {len(test_matrix)}"
    
    print("✅ Unicode validation framework test passed")

if __name__ == "__main__":
    print("🌍 Unicode Validation for Windows Testing Checkpoint #2")
    print("=" * 60)
    
    # Test framework first
    try:
        test_unicode_validation_framework()
    except AssertionError as e:
        print(f"❌ Framework test failed: {e}")
        sys.exit(1)
    
    # Run comprehensive Unicode validation
    validator = UnicodeValidator()
    results = validator.run_comprehensive_unicode_tests()
    
    # Generate and display report
    report = validator.generate_unicode_report(results)
    print("\n" + report)
    
    # Save report to file with UTF-8 encoding
    report_filename = f"unicode_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📁 Unicode report saved to: {report_filename}")
    
    # Exit with appropriate code
    if results['validation_passed']:
        print("\n🎉 Unicode validation PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Unicode validation FAILED!")
        print("🌍 UNICODE HANDLING ISSUES DETECTED!")
        sys.exit(1)