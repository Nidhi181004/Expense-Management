#!/bin/bash

# Git Setup Script for Expense Management System
# Run this script to initialize your Git repository properly

echo "🚀 Setting up Git repository for Expense Management System..."

# Initialize Git repository
git init

echo "📝 Adding .gitignore..."
git add .gitignore

echo "📚 Adding documentation..."
git add README.md GIT_WORKFLOW.md

echo "⚙️ Adding core application files..."
git add requirements.txt app.py extensions.py

echo "🗄️ Adding database models..."
git add models.py

echo "🛣️ Adding routes and business logic..."
git add routes.py ocr_utils.py

echo "🎨 Adding templates and static files..."
git add templates/ static/

echo "📦 Creating initial commit..."
git commit -m "Initial commit: Complete expense management system

Features:
- Multi-role authentication (Admin, Manager, Employee)
- Hierarchical approval workflows
- Multi-currency expense support
- OCR receipt scanning
- Responsive web interface
- Company and user management"

echo "✅ Git repository initialized successfully!"
echo ""
echo "Next steps:"
echo "1. Create a GitHub repository"
echo "2. Add remote: git remote add origin <your-repo-url>"
echo "3. Push to GitHub: git push -u origin main"
echo ""
echo "📖 See GIT_WORKFLOW.md for detailed Git usage guidelines"
