#!/usr/bin/env python3
"""
Setup script for Expense Management System
"""

import os
import sys
import subprocess
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed:")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"✗ Python 3.8+ required. Current version: {version.major}.{version.minor}")
        return False
    print(f"✓ Python version {version.major}.{version.minor} is compatible")
    return True

def create_virtual_environment():
    """Create virtual environment"""
    if os.path.exists('venv'):
        print("✓ Virtual environment already exists")
        return True
    
    return run_command('python -m venv venv', 'Creating virtual environment')

def activate_and_install():
    """Activate virtual environment and install dependencies"""
    system = platform.system().lower()
    
    if system == 'windows':
        activate_cmd = 'venv\\Scripts\\activate'
        pip_cmd = 'venv\\Scripts\\pip'
    else:
        activate_cmd = 'source venv/bin/activate'
        pip_cmd = 'venv/bin/pip'
    
    # Install dependencies
    install_cmd = f'{pip_cmd} install -r requirements.txt'
    return run_command(install_cmd, 'Installing dependencies')

def setup_database():
    """Initialize database"""
    system = platform.system().lower()
    
    if system == 'windows':
        python_cmd = 'venv\\Scripts\\python'
    else:
        python_cmd = 'venv/bin/python'
    
    # Create database tables
    init_script = '''
import sys
sys.path.append('.')
from app import app, db
with app.app_context():
    db.create_all()
    print("Database tables created successfully")
'''
    
    with open('init_db.py', 'w') as f:
        f.write(init_script)
    
    result = run_command(f'{python_cmd} init_db.py', 'Initializing database')
    
    # Clean up
    if os.path.exists('init_db.py'):
        os.remove('init_db.py')
    
    return result

def create_env_file():
    """Create .env file if it doesn't exist"""
    if os.path.exists('.env'):
        print("✓ .env file already exists")
        return True
    
    env_content = '''SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///expense_management.db
FLASK_ENV=development
EXCHANGE_RATE_API_KEY=your-api-key-here
'''
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ Created .env file")
        return True
    except Exception as e:
        print(f"✗ Failed to create .env file: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 60)
    print("EXPENSE MANAGEMENT SYSTEM - SETUP")
    print("=" * 60)
    
    steps = [
        ("Checking Python version", check_python_version),
        ("Creating .env file", create_env_file),
        ("Creating virtual environment", create_virtual_environment),
        ("Installing dependencies", activate_and_install),
        ("Setting up database", setup_database)
    ]
    
    failed_steps = []
    
    for step_name, step_func in steps:
        print(f"\n{'='*20} {step_name} {'='*20}")
        try:
            if not step_func():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"✗ {step_name} failed with exception: {e}")
            failed_steps.append(step_name)
    
    print("\n" + "=" * 60)
    print("SETUP SUMMARY")
    print("=" * 60)
    
    if not failed_steps:
        print("🎉 Setup completed successfully!")
        print("\nYour Expense Management System is ready to use!")
        print("\nTo start the application:")
        
        system = platform.system().lower()
        if system == 'windows':
            print("1. Activate virtual environment: venv\\Scripts\\activate")
            print("2. Run the application: python app.py")
        else:
            print("1. Activate virtual environment: source venv/bin/activate")
            print("2. Run the application: python app.py")
        
        print("3. Open your browser and go to: http://localhost:5000")
        print("\nFirst time setup:")
        print("- Register as an admin user")
        print("- Add your company information")
        print("- Create manager and employee accounts")
        print("- Start submitting and approving expenses!")
        
    else:
        print(f"⚠️  Setup failed at {len(failed_steps)} step(s):")
        for step in failed_steps:
            print(f"  - {step}")
        print("\nPlease fix the issues above and run setup again.")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
