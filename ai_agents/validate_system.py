#!/usr/bin/env python3
"""
System Validation Script

This script validates the structure and basic functionality of the multi-agent system
without requiring external dependencies. It checks:
1. File structure
2. Code syntax
3. Import structure
4. Class definitions
5. Method signatures

Run this to verify the system is properly set up.
"""

import os
import sys
import ast
import importlib.util
from pathlib import Path

def print_status(message, status="INFO"):
    """Print a status message with formatting"""
    symbols = {"INFO": "ℹ️", "SUCCESS": "✅", "WARNING": "⚠️", "ERROR": "❌"}
    symbol = symbols.get(status, "ℹ️")
    print(f"{symbol} {message}")

def check_file_structure():
    """Check if all required files exist"""
    print_status("Checking file structure...", "INFO")
    
    required_files = [
        "agent_system.py",
        "test_agent_system.py", 
        "example_usage.py",
        "requirements.txt",
        ".env.sample",
        "README.md"
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print_status(f"Missing files: {', '.join(missing_files)}", "ERROR")
        return False
    else:
        print_status("All required files present", "SUCCESS")
        return True

def check_python_syntax(filename):
    """Check if a Python file has valid syntax"""
    try:
        with open(filename, 'r') as f:
            source = f.read()
        ast.parse(source)
        return True, None
    except SyntaxError as e:
        return False, str(e)
    except Exception as e:
        return False, str(e)

def analyze_agent_system():
    """Analyze the main agent system file"""
    print_status("Analyzing agent_system.py...", "INFO")
    
    # Check syntax
    valid, error = check_python_syntax("agent_system.py")
    if not valid:
        print_status(f"Syntax error in agent_system.py: {error}", "ERROR")
        return False
    
    # Parse the AST to check class definitions
    with open("agent_system.py", 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    # Expected classes
    expected_classes = [
        "AgentConfig",
        "DaytonaExecutor", 
        "PlannerAgent",
        "ExecutorAgent",
        "ReviewerAgent",
        "Orchestrator"
    ]
    
    # Expected functions
    expected_functions = [
        "create_agent_system",
        "main"
    ]
    
    found_classes = []
    found_functions = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            found_classes.append(node.name)
        elif isinstance(node, ast.FunctionDef):
            found_functions.append(node.name)
    
    # Check classes
    missing_classes = [cls for cls in expected_classes if cls not in found_classes]
    if missing_classes:
        print_status(f"Missing classes: {', '.join(missing_classes)}", "ERROR")
        return False
    else:
        print_status("All expected classes found", "SUCCESS")
    
    # Check functions
    missing_functions = [func for func in expected_functions if func not in found_functions]
    if missing_functions:
        print_status(f"Missing functions: {', '.join(missing_functions)}", "ERROR")
        return False
    else:
        print_status("All expected functions found", "SUCCESS")
    
    return True

def check_test_structure():
    """Check the test file structure"""
    print_status("Analyzing test_agent_system.py...", "INFO")
    
    # Check syntax
    valid, error = check_python_syntax("test_agent_system.py")
    if not valid:
        print_status(f"Syntax error in test_agent_system.py: {error}", "ERROR")
        return False
    
    # Parse for test classes
    with open("test_agent_system.py", 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    expected_test_classes = [
        "TestDaytonaExecutor",
        "TestPlannerAgent", 
        "TestExecutorAgent",
        "TestReviewerAgent",
        "TestOrchestrator",
        "TestCreateAgentSystem",
        "TestAgentConfig"
    ]
    
    found_classes = [node.name for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
    
    missing_test_classes = [cls for cls in expected_test_classes if cls not in found_classes]
    if missing_test_classes:
        print_status(f"Missing test classes: {', '.join(missing_test_classes)}", "WARNING")
    else:
        print_status("All expected test classes found", "SUCCESS")
    
    return True

def check_requirements():
    """Check requirements.txt content"""
    print_status("Checking requirements.txt...", "INFO")
    
    with open("requirements.txt", 'r') as f:
        requirements = f.read().strip().split('\n')
    
    expected_packages = [
        "langchain",
        "langchain-openai",
        "python-dotenv",
        "openai",
        "daytona-sdk",
        "pytest"
    ]
    
    missing_packages = []
    for package in expected_packages:
        if not any(package in req for req in requirements):
            missing_packages.append(package)
    
    if missing_packages:
        print_status(f"Missing packages in requirements: {', '.join(missing_packages)}", "WARNING")
    else:
        print_status("All expected packages in requirements.txt", "SUCCESS")
    
    return len(missing_packages) == 0

def check_env_sample():
    """Check .env.sample file"""
    print_status("Checking .env.sample...", "INFO")
    
    with open(".env.sample", 'r') as f:
        env_content = f.read()
    
    expected_vars = [
        "OPENAI_API_KEY",
        "DAYTONA_API_KEY", 
        "DAYTONA_SERVER_URL"
    ]
    
    missing_vars = []
    for var in expected_vars:
        if var not in env_content:
            missing_vars.append(var)
    
    if missing_vars:
        print_status(f"Missing environment variables: {', '.join(missing_vars)}", "WARNING")
    else:
        print_status("All expected environment variables in .env.sample", "SUCCESS")
    
    return len(missing_vars) == 0

def validate_class_methods():
    """Validate that classes have expected methods"""
    print_status("Validating class methods...", "INFO")
    
    with open("agent_system.py", 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    class_methods = {}
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            methods = [n.name for n in node.body if isinstance(n, ast.FunctionDef)]
            class_methods[node.name] = methods
    
    # Expected methods for key classes
    expected_methods = {
        "PlannerAgent": ["__init__", "run"],
        "ExecutorAgent": ["__init__", "run"],
        "ReviewerAgent": ["__init__", "run"],
        "Orchestrator": ["__init__", "run"],
        "DaytonaExecutor": ["__init__", "execute_command"]
    }
    
    all_valid = True
    for class_name, expected in expected_methods.items():
        if class_name in class_methods:
            found = class_methods[class_name]
            missing = [method for method in expected if method not in found]
            if missing:
                print_status(f"{class_name} missing methods: {', '.join(missing)}", "ERROR")
                all_valid = False
            else:
                print_status(f"{class_name} has all expected methods", "SUCCESS")
        else:
            print_status(f"Class {class_name} not found", "ERROR")
            all_valid = False
    
    return all_valid

def main():
    """Main validation function"""
    print("🔍 Multi-Agent System Validation")
    print("=" * 50)
    
    checks = [
        ("File Structure", check_file_structure),
        ("Agent System Analysis", analyze_agent_system),
        ("Test Structure", check_test_structure),
        ("Requirements", check_requirements),
        ("Environment Sample", check_env_sample),
        ("Class Methods", validate_class_methods)
    ]
    
    results = {}
    for check_name, check_func in checks:
        print(f"\n📋 {check_name}")
        print("-" * 30)
        try:
            results[check_name] = check_func()
        except Exception as e:
            print_status(f"Error during {check_name}: {e}", "ERROR")
            results[check_name] = False
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    passed = sum(results.values())
    total = len(results)
    
    for check_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check_name}")
    
    print(f"\n🎯 Overall: {passed}/{total} checks passed")
    
    if passed == total:
        print_status("🎉 All validations passed! System is ready to use.", "SUCCESS")
        print_status("Next steps:", "INFO")
        print("   1. Set up your .env file with API keys")
        print("   2. Install dependencies: pip install -r requirements.txt")
        print("   3. Run: python agent_system.py")
        return True
    else:
        print_status("❌ Some validations failed. Please fix the issues above.", "ERROR")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)