# Git Workflow Guide for Expense Management System

## 📁 Repository Structure & Push Sequence

### 1. Initial Repository Setup
```bash
git init
git add .gitignore
git commit -m "Initial commit: Add .gitignore"
```

### 2. Core Application Files (Push in this order)

#### Phase 1: Project Foundation
```bash
# Add core configuration and requirements
git add requirements.txt
git add app.py
git add extensions.py
git commit -m "Add core application setup and dependencies"
```

#### Phase 2: Database Models
```bash
# Add database models
git add models.py
git commit -m "Add database models for users, expenses, and approvals"
```

#### Phase 3: Core Routes and Logic
```bash
# Add main application routes
git add routes.py
git commit -m "Add core routes and business logic"
```

#### Phase 4: Base Templates and Static Files
```bash
# Add base template and CSS
git add templates/base.html
git add static/css/style.css
git commit -m "Add base template and styling"

# Add JavaScript functionality
git add static/js/main.js
git commit -m "Add client-side JavaScript functionality"
```

#### Phase 5: Authentication Templates
```bash
# Add authentication pages
git add templates/index.html
git add templates/login.html
git add templates/register.html
git commit -m "Add authentication and landing pages"
```

#### Phase 6: Core Functionality Templates
```bash
# Add dashboard
git add templates/dashboard.html
git commit -m "Add dashboard functionality"

# Add expense management
git add templates/expenses.html
git add templates/new_expense.html
git commit -m "Add expense management pages"

# Add approval system
git add templates/approvals.html
git commit -m "Add approval workflow pages"
```

#### Phase 7: User and Company Management
```bash
# Add user management
git add templates/users.html
git add templates/new_user.html
git add templates/profile.html
git add templates/edit_profile.html
git commit -m "Add user management functionality"

# Add company settings
git add templates/company_settings.html
git add templates/edit_company.html
git commit -m "Add company management pages"
```

#### Phase 8: Utility Files
```bash
# Add OCR and utility functions
git add ocr_utils.py
git commit -m "Add OCR processing utilities"

# Add any additional utility files
git add utils/
git commit -m "Add utility functions and helpers"
```

### 3. Documentation and Project Files
```bash
# Add documentation
git add README.md
git add GIT_WORKFLOW.md
git commit -m "Add project documentation"
```

## 🚫 Files to NEVER Push (Already in .gitignore)

### Critical - Never Push These:
- **Database files** (`*.db`, `*.sqlite`)
- **Virtual environment** (`venv/`, `env/`)
- **Environment variables** (`.env`, `config.py` with secrets)
- **API keys and secrets** (`*.key`, `secrets.json`)
- **Upload directories** (`uploads/`, `receipts/`)
- **Cache and temporary files** (`__pycache__/`, `*.pyc`)

### IDE and OS Files:
- **IDE settings** (`.vscode/`, `.idea/`)
- **OS files** (`.DS_Store`, `Thumbs.db`)
- **Log files** (`*.log`)

## 📋 Recommended Commit Message Format

### Format: `<type>: <description>`

#### Types:
- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, etc.)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

#### Examples:
```bash
git commit -m "feat: Add multi-currency expense support"
git commit -m "fix: Resolve manager hierarchy authorization issue"
git commit -m "docs: Update API documentation"
git commit -m "style: Improve dashboard responsive design"
```

## 🔄 Development Workflow

### Daily Development:
```bash
# Start work
git pull origin main

# Make changes
# ... code changes ...

# Stage and commit
git add .
git commit -m "feat: Add expense filtering functionality"

# Push to remote
git push origin main
```

### Feature Development:
```bash
# Create feature branch
git checkout -b feature/expense-categories

# Make changes and commit
git add .
git commit -m "feat: Add expense category management"

# Push feature branch
git push origin feature/expense-categories

# Merge back to main (after review)
git checkout main
git merge feature/expense-categories
git push origin main
```

## 📦 Environment Setup for New Developers

### 1. Clone Repository:
```bash
git clone <your-repo-url>
cd Expense-Management
```

### 2. Create Virtual Environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies:
```bash
pip install -r requirements.txt
```

### 4. Create Environment File:
```bash
# Create .env file with:
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///expense_management.db
FLASK_ENV=development
```

### 5. Initialize Database:
```bash
python app.py
# Database will be created automatically
```

## 🔒 Security Best Practices

### Never Commit:
1. **Database files** with real data
2. **API keys** (use environment variables)
3. **Passwords** or **secret keys**
4. **Personal information** in test data
5. **Production configuration** files

### Use Environment Variables:
```python
# In your code, use:
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-key-only')
DATABASE_URL = os.environ.get('DATABASE_URL', 'sqlite:///dev.db')
```

## 📊 Repository Structure
```
Expense-Management/
├── .gitignore                 # Git ignore rules
├── README.md                  # Project documentation
├── requirements.txt           # Python dependencies
├── app.py                     # Main application entry
├── extensions.py              # Flask extensions
├── models.py                  # Database models
├── routes.py                  # Application routes
├── ocr_utils.py              # OCR utilities
├── templates/                 # HTML templates
│   ├── base.html
│   ├── dashboard.html
│   ├── expenses.html
│   └── ...
├── static/                    # Static assets
│   ├── css/
│   │   └── style.css
│   └── js/
│       └── main.js
└── uploads/                   # User uploads (ignored)
```

## 🚀 Deployment Considerations

### For Production:
1. **Use environment variables** for all secrets
2. **Set up proper database** (PostgreSQL/MySQL)
3. **Configure proper logging**
4. **Set up SSL certificates**
5. **Use production WSGI server** (Gunicorn)

### Environment Variables for Production:
```bash
FLASK_ENV=production
SECRET_KEY=<strong-random-key>
DATABASE_URL=postgresql://user:pass@host:port/dbname
UPLOAD_FOLDER=/var/www/uploads
```
