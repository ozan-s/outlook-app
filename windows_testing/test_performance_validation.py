#!/usr/bin/env python3
"""
Performance Validation for Windows Testing Checkpoint #2

Tests filtering performance with corporate email volumes and validates
memory usage, progressive filtering optimization, and resource limits.

Run this script on Windows machine with Outlook:
    python test_performance_validation.py
"""

import sys
import os
import subprocess
import time
import psutil
import gc
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
import json

class PerformanceValidator:
    """Validates filtering performance with real corporate email volumes"""
    
    def __init__(self):
        self.cli_path = self._find_cli_executable()
        self.test_results = {}
        self.performance_baselines = {
            'basic_filter_max_time': 5.0,  # seconds
            'complex_filter_max_time': 10.0,  # seconds
            'max_memory_increase_mb': 500,  # MB
            'large_result_max_time': 15.0,  # seconds
        }
        self.process = psutil.Process()
        
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
    
    def measure_memory_usage(self) -> Dict[str, float]:
        """Get current memory usage metrics"""
        memory_info = self.process.memory_info()
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,  # Resident Set Size
            'vms_mb': memory_info.vms / 1024 / 1024,  # Virtual Memory Size
        }
    
    def run_performance_test(self, command_args: List[str], test_name: str, timeout: int = 120) -> Dict[str, Any]:
        """Run a performance test with memory and timing measurement"""
        print(f"  🏃 Running: {test_name}")
        
        # Garbage collect before test
        gc.collect()
        
        # Measure baseline memory
        baseline_memory = self.measure_memory_usage()
        
        # Build and execute command
        full_command = f"{self.cli_path} {' '.join(command_args)}"
        
        try:
            start_time = time.time()
            result = subprocess.run(
                full_command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout,
                encoding='utf-8',
                errors='replace'
            )
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Measure post-execution memory
            post_memory = self.measure_memory_usage()
            memory_increase = post_memory['rss_mb'] - baseline_memory['rss_mb']
            
            # Count results if successful
            result_count = 0
            if result.returncode == 0 and result.stdout:
                # Basic heuristic: count lines that look like email results
                lines = result.stdout.split('\n')
                result_count = len([line for line in lines if '@' in line and ('Subject:' in line or 'From:' in line)])
            
            return {
                'test_name': test_name,
                'command': full_command,
                'success': result.returncode == 0,
                'execution_time': execution_time,
                'result_count': result_count,
                'memory_baseline_mb': baseline_memory['rss_mb'],
                'memory_post_mb': post_memory['rss_mb'],
                'memory_increase_mb': memory_increase,
                'stdout_length': len(result.stdout),
                'stderr': result.stderr,
                'returncode': result.returncode,
                'performance_rating': self._calculate_performance_rating(execution_time, memory_increase, test_name)
            }
            
        except subprocess.TimeoutExpired:
            return {
                'test_name': test_name,
                'command': full_command,
                'success': False,
                'execution_time': timeout,
                'error': f'Command timed out after {timeout} seconds',
                'performance_rating': 'TIMEOUT'
            }
        except Exception as e:
            return {
                'test_name': test_name,
                'command': full_command,
                'success': False,
                'execution_time': 0,
                'error': str(e),
                'performance_rating': 'ERROR'
            }
    
    def _calculate_performance_rating(self, execution_time: float, memory_increase: float, test_name: str) -> str:
        """Calculate performance rating based on test type and metrics"""
        if 'basic' in test_name.lower():
            time_threshold = self.performance_baselines['basic_filter_max_time']
        elif 'complex' in test_name.lower():
            time_threshold = self.performance_baselines['complex_filter_max_time']
        elif 'large' in test_name.lower():
            time_threshold = self.performance_baselines['large_result_max_time']
        else:
            time_threshold = self.performance_baselines['basic_filter_max_time']
        
        # Rating based on time performance
        if execution_time <= time_threshold * 0.5:
            time_rating = 'EXCELLENT'
        elif execution_time <= time_threshold:
            time_rating = 'GOOD'
        elif execution_time <= time_threshold * 1.5:
            time_rating = 'ACCEPTABLE'
        else:
            time_rating = 'POOR'
        
        # Rating based on memory usage
        memory_threshold = self.performance_baselines['max_memory_increase_mb']
        if memory_increase <= memory_threshold * 0.5:
            memory_rating = 'EXCELLENT'
        elif memory_increase <= memory_threshold:
            memory_rating = 'GOOD'
        else:
            memory_rating = 'POOR'
        
        # Combined rating (worst of the two)
        ratings = ['EXCELLENT', 'GOOD', 'ACCEPTABLE', 'POOR']
        time_idx = ratings.index(time_rating)
        memory_idx = ratings.index(memory_rating)
        return ratings[max(time_idx, memory_idx)]
    
    def get_performance_test_matrix(self) -> List[Tuple[List[str], str]]:
        """Get comprehensive performance test matrix"""
        return [
            # Basic filtering tests
            (['read', '--limit', '10'], 'Basic Read (10 results)'),
            (['find', '--limit', '20'], 'Basic Find (20 results)'),
            (['folders'], 'Folder Enumeration'),
            
            # Date filtering tests
            (['read', '--since', '7d', '--limit', '50'], 'Date Filter - 7 days'),
            (['find', '--since', '1M', '--limit', '100'], 'Date Filter - 1 month'),
            (['read', '--since', 'yesterday', '--until', 'today'], 'Date Range Filter'),
            
            # Read status filtering
            (['read', '--is-unread', '--limit', '50'], 'Unread Filter'),
            (['find', '--is-read', '--since', '1w'], 'Read + Date Filter'),
            
            # Attachment filtering
            (['read', '--has-attachment', '--limit', '30'], 'Attachment Filter'),
            (['find', '--no-attachment', '--since', '2d'], 'No Attachment Filter'),
            
            # Content filtering
            (['find', '--importance', 'high', '--limit', '20'], 'Importance Filter'),
            (['read', '--not-sender', 'noreply', '--limit', '25'], 'Sender Exclusion Filter'),
            
            # Complex combinations
            (['find', '--since', '1w', '--has-attachment', '--importance', 'high'], 'Complex Filter Combo 1'),
            (['read', '--since', '2d', '--is-unread', '--not-sender', 'noreply'], 'Complex Filter Combo 2'),
            
            # Sorting tests
            (['find', '--sort-by', 'received_date', '--sort-order', 'desc', '--limit', '50'], 'Sort by Date'),
            (['read', '--sort-by', 'sender', '--limit', '40'], 'Sort by Sender'),
            
            # Large result tests
            (['find', '--since', '1M', '--all'], 'Large Results - 1 Month All'),
            (['read', '--since', '1w', '--limit', '500'], 'Large Results - 500 items'),
        ]
    
    def run_comprehensive_performance_tests(self) -> Dict[str, Any]:
        """Run comprehensive performance validation"""
        print("🚀 Running comprehensive performance validation...")
        
        test_matrix = self.get_performance_test_matrix()
        results = {
            'total_tests': len(test_matrix),
            'successful_tests': 0,
            'failed_tests': 0,
            'test_results': {},
            'performance_summary': {},
            'validation_passed': False
        }
        
        # Record overall start time
        overall_start = time.time()
        
        for test_args, test_name in test_matrix:
            test_result = self.run_performance_test(test_args, test_name)
            
            if test_result['success']:
                results['successful_tests'] += 1
                status = f"✅ {test_result['performance_rating']}"
            else:
                results['failed_tests'] += 1
                status = "❌ FAILED"
            
            results['test_results'][test_name] = test_result
            
            print(f"    {status} - {test_result['execution_time']:.2f}s")
            
            # Brief pause between tests
            time.sleep(0.5)
        
        # Calculate overall metrics
        overall_time = time.time() - overall_start
        successful_results = [r for r in results['test_results'].values() if r['success']]
        
        if successful_results:
            avg_execution_time = sum(r['execution_time'] for r in successful_results) / len(successful_results)
            max_execution_time = max(r['execution_time'] for r in successful_results)
            avg_memory_increase = sum(r.get('memory_increase_mb', 0) for r in successful_results) / len(successful_results)
            max_memory_increase = max(r.get('memory_increase_mb', 0) for r in successful_results)
            
            # Count performance ratings
            rating_counts = {}
            for result in successful_results:
                rating = result.get('performance_rating', 'UNKNOWN')
                rating_counts[rating] = rating_counts.get(rating, 0) + 1
        else:
            avg_execution_time = 0
            max_execution_time = 0
            avg_memory_increase = 0
            max_memory_increase = 0
            rating_counts = {}
        
        results['performance_summary'] = {
            'overall_execution_time': overall_time,
            'success_rate_percent': (results['successful_tests'] / results['total_tests']) * 100,
            'avg_execution_time': avg_execution_time,
            'max_execution_time': max_execution_time,
            'avg_memory_increase_mb': avg_memory_increase,
            'max_memory_increase_mb': max_memory_increase,
            'rating_distribution': rating_counts,
            'performance_baseline_met': max_execution_time <= self.performance_baselines['large_result_max_time'] and 
                                      max_memory_increase <= self.performance_baselines['max_memory_increase_mb']
        }
        
        # Validation criteria: 80% success rate + performance baselines met
        results['validation_passed'] = (
            results['performance_summary']['success_rate_percent'] >= 80.0 and
            results['performance_summary']['performance_baseline_met']
        )
        
        return results
    
    def generate_performance_report(self, results: Dict[str, Any]) -> str:
        """Generate comprehensive performance report"""
        report = []
        report.append("=" * 80)
        report.append("PERFORMANCE VALIDATION REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Total Tests: {results['total_tests']}")
        report.append(f"Successful: {results['successful_tests']}")
        report.append(f"Failed: {results['failed_tests']}")
        report.append(f"Success Rate: {results['performance_summary']['success_rate_percent']:.1f}%")
        report.append(f"Overall Validation: {'✅ PASSED' if results['validation_passed'] else '❌ FAILED'}")
        report.append("")
        
        # Performance summary
        summary = results['performance_summary']
        report.append("PERFORMANCE SUMMARY:")
        report.append(f"Overall Test Duration: {summary['overall_execution_time']:.2f}s")
        report.append(f"Average Execution Time: {summary['avg_execution_time']:.2f}s")
        report.append(f"Maximum Execution Time: {summary['max_execution_time']:.2f}s")
        report.append(f"Average Memory Increase: {summary['avg_memory_increase_mb']:.1f}MB")
        report.append(f"Maximum Memory Increase: {summary['max_memory_increase_mb']:.1f}MB")
        report.append(f"Baseline Compliance: {'✅ YES' if summary['performance_baseline_met'] else '❌ NO'}")
        report.append("")
        
        # Performance rating distribution
        if summary['rating_distribution']:
            report.append("PERFORMANCE RATING DISTRIBUTION:")
            for rating, count in sorted(summary['rating_distribution'].items()):
                report.append(f"  {rating}: {count} tests")
            report.append("")
        
        # Detailed test results
        report.append("DETAILED TEST RESULTS:")
        for test_name, result in results['test_results'].items():
            if result['success']:
                status = f"✅ {result.get('performance_rating', 'UNKNOWN')}"
                details = f"{result['execution_time']:.2f}s | {result.get('memory_increase_mb', 0):.1f}MB | {result.get('result_count', 0)} results"
            else:
                status = "❌ FAILED"
                details = result.get('error', 'Unknown error')
                
            report.append(f"  {test_name:<35} | {status:<15} | {details}")
        
        report.append("")
        report.append("PERFORMANCE BASELINES:")
        for key, value in self.performance_baselines.items():
            report.append(f"  {key}: {value}")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)

def test_performance_validation_framework():
    """Test that performance validation framework works"""
    validator = PerformanceValidator()
    
    # Test framework components
    assert hasattr(validator, 'cli_path'), "CLI path not found"
    assert hasattr(validator, 'measure_memory_usage'), "Memory measurement missing"
    assert hasattr(validator, 'run_performance_test'), "Performance test method missing"
    assert hasattr(validator, 'performance_baselines'), "Performance baselines missing"
    
    # Test memory measurement
    memory_info = validator.measure_memory_usage()
    assert 'rss_mb' in memory_info, "RSS memory measurement missing"
    assert 'vms_mb' in memory_info, "VMS memory measurement missing"
    
    print("✅ Performance validation framework test passed")

if __name__ == "__main__":
    print("🚀 Performance Validation for Windows Testing Checkpoint #2")
    print("=" * 60)
    
    # Test framework first
    try:
        test_performance_validation_framework()
    except AssertionError as e:
        print(f"❌ Framework test failed: {e}")
        sys.exit(1)
    
    # Run comprehensive performance validation
    validator = PerformanceValidator()
    results = validator.run_comprehensive_performance_tests()
    
    # Generate and display report
    report = validator.generate_performance_report(results)
    print("\n" + report)
    
    # Save report to file
    report_filename = f"performance_validation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\n📁 Performance report saved to: {report_filename}")
    
    # Exit with appropriate code
    if results['validation_passed']:
        print("\n🎉 Performance validation PASSED!")
        sys.exit(0)
    else:
        print("\n❌ Performance validation FAILED!")
        sys.exit(1)