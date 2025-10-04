#!/usr/bin/env python3
"""
Test script to demonstrate multi-level approval workflow
"""

from extensions import app, db
from models import *
from werkzeug.security import generate_password_hash
from decimal import Decimal
from datetime import datetime, date

def create_test_hierarchy():
    """Create a test management hierarchy"""
    with app.app_context():
        # Create company
        company = Company(
            name="Test Company",
            country="United States", 
            currency="USD"
        )
        db.session.add(company)
        db.session.flush()
        
        # Create CEO (top level)
        ceo = User(
            email="ceo@company.com",
            password_hash=generate_password_hash("password123"),
            first_name="John",
            last_name="CEO",
            role=UserRole.ADMIN,
            company_id=company.id,
            manager_id=None  # No manager above CEO
        )
        db.session.add(ceo)
        db.session.flush()
        
        # Create Director (reports to CEO)
        director = User(
            email="director@company.com",
            password_hash=generate_password_hash("password123"),
            first_name="Jane",
            last_name="Director",
            role=UserRole.MANAGER,
            company_id=company.id,
            manager_id=ceo.id
        )
        db.session.add(director)
        db.session.flush()
        
        # Create Manager (reports to Director)
        manager = User(
            email="manager@company.com",
            password_hash=generate_password_hash("password123"),
            first_name="Bob",
            last_name="Manager",
            role=UserRole.MANAGER,
            company_id=company.id,
            manager_id=director.id
        )
        db.session.add(manager)
        db.session.flush()
        
        # Create Employee (reports to Manager)
        employee = User(
            email="employee@company.com",
            password_hash=generate_password_hash("password123"),
            first_name="Alice",
            last_name="Employee",
            role=UserRole.EMPLOYEE,
            company_id=company.id,
            manager_id=manager.id
        )
        db.session.add(employee)
        db.session.flush()
        
        # Create expense category
        category = ExpenseCategory(
            name="Travel",
            company_id=company.id
        )
        db.session.add(category)
        db.session.flush()
        
        # Create test expense
        expense = Expense(
            title="Business Trip to New York",
            description="Flight and hotel for client meeting",
            amount=Decimal("1500.00"),
            currency="USD",
            amount_in_company_currency=Decimal("1500.00"),
            exchange_rate=Decimal("1.0"),
            expense_date=date.today(),
            employee_id=employee.id,
            company_id=company.id,
            category_id=category.id,
            status=ExpenseStatus.SUBMITTED
        )
        db.session.add(expense)
        db.session.flush()
        
        db.session.commit()
        
        return {
            'company': company,
            'ceo': ceo,
            'director': director,
            'manager': manager,
            'employee': employee,
            'expense': expense
        }

def test_approval_workflow():
    """Test the multi-level approval workflow"""
    from routes import create_approval_workflow, get_management_hierarchy
    
    with app.app_context():
        # Create test data
        test_data = create_test_hierarchy()
        expense = test_data['expense']
        employee = test_data['employee']
        
        print("=" * 60)
        print("MULTI-LEVEL APPROVAL WORKFLOW TEST")
        print("=" * 60)
        
        # Test management hierarchy
        hierarchy = get_management_hierarchy(employee)
        print(f"\nManagement Hierarchy for {employee.full_name}:")
        for i, manager in enumerate(hierarchy, 1):
            print(f"  Level {i}: {manager.full_name} ({manager.role.value})")
        
        # Create approval workflow
        create_approval_workflow(expense)
        db.session.commit()
        
        # Show approval workflow
        approvals = Approval.query.filter_by(expense_id=expense.id).order_by(Approval.sequence).all()
        print(f"\nApproval Workflow for Expense: {expense.title}")
        print(f"Amount: ${expense.amount}")
        print(f"Employee: {expense.employee.full_name}")
        print("\nApproval Steps:")
        
        for approval in approvals:
            print(f"  Step {approval.sequence}: {approval.approver.full_name} ({approval.approver.role.value}) - {approval.status}")
        
        print(f"\nExpense Status: {expense.status.value}")
        
        # Test approval ready logic
        from routes import is_approval_ready_for_processing
        print("\nApproval Readiness:")
        for approval in approvals:
            ready = is_approval_ready_for_processing(approval)
            print(f"  {approval.approver.full_name}: {'Ready' if ready else 'Waiting'}")
        
        print("\n" + "=" * 60)
        print("TEST COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        
        print("\nTo test the workflow:")
        print("1. Start the Flask app: python app.py")
        print("2. Login with these test accounts:")
        print("   - Employee: employee@company.com / password123")
        print("   - Manager: manager@company.com / password123") 
        print("   - Director: director@company.com / password123")
        print("   - CEO: ceo@company.com / password123")
        print("3. Submit expenses as Employee")
        print("4. Approve sequentially as Manager → Director → CEO")

if __name__ == "__main__":
    test_approval_workflow()
