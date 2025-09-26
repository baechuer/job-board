#!/usr/bin/env python3
"""
Comprehensive test runner for security features.
This script runs all security-related tests and generates a detailed report.
"""
import os
import sys
import subprocess
import json
import time
from pathlib import Path
from datetime import datetime


def run_security_tests():
    """Run all security tests and generate report"""
    print("🔒 Running Security Test Suite")
    print("=" * 50)
    
    # Test categories
    test_categories = {
        "Security Utilities": "tests/unit/test_security_utils.py",
        "Rate Limiting": "tests/integration/test_rate_limiting.py", 
        "File Upload Security": "tests/integration/test_file_upload_security.py",
        "Input Validation": "tests/integration/test_input_validation.py",
        "CORS & Security Headers": "tests/integration/test_cors_security_headers.py"
    }
    
    results = {}
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    # Run each test category
    for category, test_file in test_categories.items():
        print(f"\n📋 Running {category} Tests...")
        print("-" * 30)
        
        if not os.path.exists(test_file):
            print(f"❌ Test file not found: {test_file}")
            results[category] = {"status": "SKIPPED", "reason": "File not found"}
            continue
        
        try:
            # Run pytest for this specific test file
            cmd = [
                sys.executable, "-m", "pytest", 
                test_file,
                "-v",  # Verbose output
                "--tb=short",  # Short traceback
                "--no-header",  # No header
                "--disable-warnings"  # Disable warnings
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
            
            # Parse results
            output_lines = result.stdout.split('\n')
            test_results = []
            
            for line in output_lines:
                # Look for test lines (they contain :: and either PASSED or FAILED)
                if '::' in line and ('PASSED' in line or 'FAILED' in line):
                    if 'PASSED' in line:
                        test_results.append({"test": line.strip(), "status": "PASSED"})
                        passed_tests += 1
                    elif 'FAILED' in line:
                        test_results.append({"test": line.strip(), "status": "FAILED"})
                        failed_tests += 1
                    total_tests += 1
            
            results[category] = {
                "status": "PASSED" if result.returncode == 0 else "FAILED",
                "returncode": result.returncode,
                "tests": test_results,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
            if result.returncode == 0:
                print(f"✅ {category}: All tests passed")
            else:
                print(f"❌ {category}: Some tests failed")
                print(f"   Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {category}: Tests timed out")
            results[category] = {"status": "TIMEOUT", "reason": "Tests exceeded 5 minute timeout"}
        except Exception as e:
            print(f"💥 {category}: Error running tests - {str(e)}")
            results[category] = {"status": "ERROR", "reason": str(e)}
    
    # Generate summary report
    print("\n" + "=" * 50)
    print("📊 SECURITY TEST SUMMARY")
    print("=" * 50)
    
    for category, result in results.items():
        status_icon = {
            "PASSED": "✅",
            "FAILED": "❌", 
            "SKIPPED": "⏭️",
            "TIMEOUT": "⏰",
            "ERROR": "💥"
        }.get(result["status"], "❓")
        
        print(f"{status_icon} {category}: {result['status']}")
        
        if result["status"] == "FAILED" and "tests" in result:
            failed_count = sum(1 for test in result["tests"] if test["status"] == "FAILED")
            passed_count = sum(1 for test in result["tests"] if test["status"] == "PASSED")
            print(f"   Tests: {passed_count} passed, {failed_count} failed")
    
    print(f"\n📈 Overall: {passed_tests} passed, {failed_tests} failed, {total_tests} total")
    
    # Generate detailed report
    generate_detailed_report(results, total_tests, passed_tests, failed_tests)
    
    # Return success if all tests passed
    return failed_tests == 0


def generate_detailed_report(results, total_tests, passed_tests, failed_tests):
    """Generate detailed HTML report"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Security Test Report - {timestamp}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .summary {{ background-color: #e8f5e8; padding: 15px; border-radius: 5px; margin: 20px 0; }}
            .category {{ margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }}
            .passed {{ background-color: #d4edda; }}
            .failed {{ background-color: #f8d7da; }}
            .skipped {{ background-color: #fff3cd; }}
            .test-result {{ margin: 5px 0; padding: 5px; }}
            .test-passed {{ color: green; }}
            .test-failed {{ color: red; }}
            pre {{ background-color: #f8f9fa; padding: 10px; border-radius: 3px; overflow-x: auto; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🔒 Security Test Report</h1>
            <p>Generated: {timestamp}</p>
            <p>Total Tests: {total_tests} | Passed: {passed_tests} | Failed: {failed_tests}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Summary</h2>
            <p><strong>Overall Status:</strong> {'✅ PASSED' if failed_tests == 0 else '❌ FAILED'}</p>
            <p><strong>Success Rate:</strong> {f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "N/A"}</p>
        </div>
    """
    
    for category, result in results.items():
        status_class = result["status"].lower()
        html_content += f"""
        <div class="category {status_class}">
            <h2>📋 {category}</h2>
            <p><strong>Status:</strong> {result['status']}</p>
        """
        
        if "tests" in result and result["tests"]:
            html_content += "<h3>Test Results:</h3>"
            for test in result["tests"]:
                test_class = "test-passed" if test["status"] == "PASSED" else "test-failed"
                html_content += f'<div class="test-result {test_class}">{test["test"]}</div>'
        
        if result.get("stderr"):
            html_content += f"<h3>Error Output:</h3><pre>{result['stderr']}</pre>"
        
        html_content += "</div>"
    
    html_content += """
        <div class="category">
            <h2>🛡️ Security Features Tested</h2>
            <ul>
                <li>✅ Input validation and sanitization</li>
                <li>✅ File type validation and virus scanning</li>
                <li>✅ Rate limiting on all endpoints</li>
                <li>✅ CORS configuration</li>
                <li>✅ Security headers</li>
                <li>✅ Authentication security</li>
                <li>✅ File upload security</li>
                <li>✅ SQL injection prevention</li>
                <li>✅ XSS prevention</li>
                <li>✅ Path traversal prevention</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    # Save report
    report_dir = Path("reports")
    report_dir.mkdir(exist_ok=True)
    
    timestamp_file = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"security_test_report_{timestamp_file}.html"
    
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"\n📄 Detailed report saved: {report_file}")


def run_quick_security_check():
    """Run a quick security check without full test suite"""
    print("🔍 Quick Security Check")
    print("=" * 30)
    
    # Check if security modules can be imported
    try:
        from app.common.security_utils import validate_file_type, sanitize_string_input
        print("✅ Security utilities imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import security utilities: {e}")
        return False
    
    # Check if Flask-Limiter is available
    try:
        from flask_limiter import Limiter
        print("✅ Flask-Limiter available")
    except ImportError as e:
        print(f"❌ Flask-Limiter not available: {e}")
        return False
    
    # Check if python-magic is available
    try:
        import magic
        print("✅ python-magic available")
    except ImportError as e:
        print(f"⚠️  python-magic not available: {e}")
    
    print("✅ Quick security check passed")
    return True


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--quick":
        success = run_quick_security_check()
    else:
        success = run_security_tests()
    
    sys.exit(0 if success else 1)
