"""
Test Center Service
Manages test execution for unit, integration, and E2E tests
"""
import os
import subprocess
import json
from datetime import datetime
from typing import List, Dict, Any, Optional


class TestCenter:
    """Central test execution and reporting service"""
    
    def __init__(self):
        self.test_results = []
    
    def run_all_tests(self, project_path: str, test_type: str = 'all') -> Dict[str, Any]:
        """Run all tests for a project"""
        results = {
            'unit': None,
            'integration': None,
            'e2e': None,
            'summary': {}
        }
        
        if test_type in ['all', 'unit']:
            results['unit'] = self.run_unit_tests(project_path)
        
        if test_type in ['all', 'integration']:
            results['integration'] = self.run_integration_tests(project_path)
        
        if test_type in ['all', 'e2e']:
            results['e2e'] = self.run_e2e_tests(project_path)
        
        # Generate summary
        results['summary'] = self._generate_summary(results)
        results['timestamp'] = datetime.utcnow().isoformat()
        
        return results
    
    def run_unit_tests(self, project_path: str) -> Dict[str, Any]:
        """Run unit tests using pytest"""
        test_dir = os.path.join(project_path, 'tests', 'unit')
        
        if not os.path.exists(test_dir):
            return {
                'success': True,
                'message': 'No unit tests found',
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
        
        try:
            result = subprocess.run(
                ['pytest', test_dir, '--json-report', '-v'],
                capture_output=True,
                text=True,
                cwd=project_path,
                timeout=300
            )
            
            # Parse output
            passed = result.stdout.count('PASSED')
            failed = result.stdout.count('FAILED')
            skipped = result.stdout.count('SKIPPED')
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'total': passed + failed + skipped
            }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Unit tests timed out',
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'total': 0
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'total': 0
            }
    
    def run_integration_tests(self, project_path: str) -> Dict[str, Any]:
        """Run integration tests"""
        test_dir = os.path.join(project_path, 'tests', 'integration')
        
        if not os.path.exists(test_dir):
            return {
                'success': True,
                'message': 'No integration tests found',
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
        
        try:
            result = subprocess.run(
                ['pytest', test_dir, '--json-report', '-v'],
                capture_output=True,
                text=True,
                cwd=project_path,
                timeout=600
            )
            
            passed = result.stdout.count('PASSED')
            failed = result.stdout.count('FAILED')
            skipped = result.stdout.count('SKIPPED')
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'total': passed + failed + skipped
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'total': 0
            }
    
    def run_e2e_tests(self, project_path: str) -> Dict[str, Any]:
        """Run end-to-end tests"""
        test_dir = os.path.join(project_path, 'tests', 'e2e')
        
        if not os.path.exists(test_dir):
            return {
                'success': True,
                'message': 'No E2E tests found',
                'passed': 0,
                'failed': 0,
                'skipped': 0
            }
        
        try:
            result = subprocess.run(
                ['pytest', test_dir, '--json-report', '-v'],
                capture_output=True,
                text=True,
                cwd=project_path,
                timeout=900
            )
            
            passed = result.stdout.count('PASSED')
            failed = result.stdout.count('FAILED')
            skipped = result.stdout.count('SKIPPED')
            
            return {
                'success': result.returncode == 0,
                'output': result.stdout,
                'error': result.stderr,
                'passed': passed,
                'failed': failed,
                'skipped': skipped,
                'total': passed + failed + skipped
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'passed': 0,
                'failed': 0,
                'skipped': 0,
                'total': 0
            }
    
    def _generate_summary(self, results: Dict) -> Dict[str, Any]:
        """Generate test summary"""
        total_passed = 0
        total_failed = 0
        total_skipped = 0
        
        for test_type in ['unit', 'integration', 'e2e']:
            result = results.get(test_type)
            if result and isinstance(result, dict):
                total_passed += result.get('passed', 0)
                total_failed += result.get('failed', 0)
                total_skipped += result.get('skipped', 0)
        
        total = total_passed + total_failed + total_skipped
        
        return {
            'total_tests': total,
            'passed': total_passed,
            'failed': total_failed,
            'skipped': total_skipped,
            'pass_rate': (total_passed / total * 100) if total > 0 else 0,
            'success': total_failed == 0
        }
    
    def generate_report(self, results: Dict[str, Any], output_path: str) -> str:
        """Generate test report in markdown format"""
        report = f"""# Test Report

**Generated**: {datetime.utcnow().isoformat()}

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {results['summary']['total_tests']} |
| Passed | {results['summary']['passed']} |
| Failed | {results['summary']['failed']} |
| Skipped | {results['summary']['skipped']} |
| Pass Rate | {results['summary']['pass_rate']:.1f}% |
| Status | {'✅ PASS' if results['summary']['success'] else '❌ FAIL'} |

## Unit Tests

"""
        if results['unit']:
            report += f"- Passed: {results['unit'].get('passed', 0)}\n"
            report += f"- Failed: {results['unit'].get('failed', 0)}\n"
            report += f"- Skipped: {results['unit'].get('skipped', 0)}\n\n"
        else:
            report += "Not executed\n\n"
        
        report += """## Integration Tests

"""
        if results['integration']:
            report += f"- Passed: {results['integration'].get('passed', 0)}\n"
            report += f"- Failed: {results['integration'].get('failed', 0)}\n"
            report += f"- Skipped: {results['integration'].get('skipped', 0)}\n\n"
        else:
            report += "Not executed\n\n"
        
        report += """## E2E Tests

"""
        if results['e2e']:
            report += f"- Passed: {results['e2e'].get('passed', 0)}\n"
            report += f"- Failed: {results['e2e'].get('failed', 0)}\n"
            report += f"- Skipped: {results['e2e'].get('skipped', 0)}\n\n"
        else:
            report += "Not executed\n\n"
        
        # Save report
        with open(output_path, 'w') as f:
            f.write(report)
        
        return output_path


# Global instance
test_center = TestCenter()
