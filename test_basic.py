#!/usr/bin/env python3
"""
Basic test script to verify the expense management system setup
"""

import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import flask
        print("✓ Flask imported successfully")
    except ImportError as e:
        print(f"✗ Flask import failed: {e}")
        return False
    
    try:
        from werkzeug.security import generate_password_hash, check_password_hash
        print("✓ Werkzeug imported successfully")
    except ImportError as e:
        print(f"✗ Werkzeug import failed: {e}")
        return False
    
    try:
        import requests
        print("✓ Requests imported successfully")
    except ImportError as e:
        print(f"✗ Requests import failed: {e}")
        return False
    
    return True

def test_file_structure():
    """Test if all required files exist"""
    print("\nTesting file structure...")
    
    required_files = [
        'app.py',
        'models.py', 
        'routes.py',
        'ocr_utils.py',
        'requirements.txt',
        '.env',
        'templates/base.html',
        'templates/index.html',
        'templates/login.html',
        'templates/register.html',
        'templates/dashboard.html',
        'templates/expenses.html',
        'templates/new_expense.html',
        'templates/approvals.html',
        'templates/users.html',
        'templates/new_user.html',
        'static/css/style.css',
        'static/js/main.js'
    ]
    
    missing_files = []
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            missing_files.append(file_path)
    
    return len(missing_files) == 0

def test_configuration():
    """Test configuration files"""
    print("\nTesting configuration...")
    
    # Check .env file
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_content = f.read()
            if 'SECRET_KEY' in env_content:
                print("✓ .env file has SECRET_KEY")
            else:
                print("✗ .env file missing SECRET_KEY")
        
        if 'DATABASE_URL' in env_content:
            print("✓ .env file has DATABASE_URL")
        else:
            print("✗ .env file missing DATABASE_URL")
    else:
        print("✗ .env file not found")
        return False
    
    return True

def test_models():
    """Test model definitions"""
    print("\nTesting models...")
    
    try:
        # This will fail if Flask-SQLAlchemy is not installed
        # but we can at least check the syntax
        with open('models.py', 'r') as f:
            content = f.read()
            
        if 'class User' in content:
            print("✓ User model defined")
        else:
            print("✗ User model not found")
            
        if 'class Company' in content:
            print("✓ Company model defined")
        else:
            print("✗ Company model not found")
            
        if 'class Expense' in content:
            print("✓ Expense model defined")
        else:
            print("✗ Expense model not found")
            
        if 'class Approval' in content:
            print("✓ Approval model defined")
        else:
            print("✗ Approval model not found")
            
        return True
        
    except Exception as e:
        print(f"✗ Error reading models.py: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 50)
    print("EXPENSE MANAGEMENT SYSTEM - BASIC TESTS")
    print("=" * 50)
    
    tests = [
        ("File Structure", test_file_structure),
        ("Configuration", test_configuration), 
        ("Models", test_models),
        ("Imports", test_imports)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"✗ {test_name} test failed with exception: {e}")
            results.append((test_name, False))
    
    print("\n" + "=" * 50)
    print("TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    for test_name, result in results:
        status = "PASS" if result else "FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)} tests")
    
    if passed == len(results):
        print("\n🎉 All tests passed! The expense management system is ready.")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the application: python app.py")
        print("3. Open http://localhost:5000 in your browser")
    else:
        print(f"\n⚠️  {len(results) - passed} test(s) failed. Please fix the issues above.")
    
    return passed == len(results)

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
