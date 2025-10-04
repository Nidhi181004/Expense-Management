from flask import render_template, request, jsonify, redirect, url_for, flash, session, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import requests
import json
from datetime import datetime, date
from decimal import Decimal
import os
from ocr_utils import get_ocr_instance

from extensions import app, db
from models import *

def get_countries_and_currencies():
    """Fetch countries and their currencies from REST Countries API"""
    try:
        response = requests.get('https://restcountries.com/v3.1/all?fields=name,currencies')
        if response.status_code == 200:
            countries_data = response.json()
            countries = []
            for country in countries_data:
                if 'currencies' in country and country['currencies']:
                    currency_code = list(country['currencies'].keys())[0]
                    countries.append({
                        'name': country['name']['common'],
                        'currency': currency_code
                    })
            return sorted(countries, key=lambda x: x['name'])
    except Exception as e:
        print(f"Error fetching countries: {e}")
    
    # Fallback data
    return [
        {'name': 'United States', 'currency': 'USD'},
        {'name': 'India', 'currency': 'INR'},
        {'name': 'United Kingdom', 'currency': 'GBP'},
        {'name': 'European Union', 'currency': 'EUR'}
    ]

def get_exchange_rate(from_currency, to_currency):
    """Get exchange rate between two currencies"""
    if from_currency == to_currency:
        return 1.0
    
    try:
        response = requests.get(f'https://api.exchangerate-api.com/v4/latest/{from_currency}')
        if response.status_code == 200:
            data = response.json()
            return data['rates'].get(to_currency, 1.0)
    except Exception as e:
        print(f"Error fetching exchange rate: {e}")
    
    return 1.0

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        company_name = data.get('company_name')
        country = data.get('country')
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'error': 'Email already registered'}), 400
            flash('Email already registered')
            return redirect(url_for('register'))
        
        # Get currency for the selected country
        try:
            countries = get_countries_and_currencies()
            currency = next((c['currency'] for c in countries if c['name'] == country), 'USD')
        except Exception as e:
            print(f"Error fetching countries: {e}")
            # Fallback currency mapping
            currency_map = {
                'United States': 'USD',
                'India': 'INR', 
                'United Kingdom': 'GBP',
                'Germany': 'EUR',
                'France': 'EUR',
                'Canada': 'CAD',
                'Australia': 'AUD',
                'Japan': 'JPY'
            }
            currency = currency_map.get(country, 'USD')
        
        try:
            # Create company
            company = Company(
                name=company_name,
                country=country,
                currency=currency
            )
            db.session.add(company)
            db.session.flush()  # Get the company ID
            
            # Create admin user
            user = User(
                email=email,
                password_hash=generate_password_hash(password),
                first_name=first_name,
                last_name=last_name,
                role=UserRole.ADMIN,
                company_id=company.id
            )
            db.session.add(user)
            
            # Create default expense categories
            default_categories = [
                'Travel', 'Meals', 'Office Supplies', 'Software', 'Training', 'Other'
            ]
            for cat_name in default_categories:
                category = ExpenseCategory(
                    name=cat_name,
                    company_id=company.id
                )
                db.session.add(category)
            
            db.session.commit()
            
            login_user(user)
            
            if request.is_json:
                return jsonify({'message': 'Registration successful', 'redirect': url_for('dashboard')})
            
            flash('Registration successful!')
            return redirect(url_for('dashboard'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Registration error: {e}")
            if request.is_json:
                return jsonify({'error': f'Registration failed: {str(e)}'}), 500
            flash(f'Registration failed: {str(e)}')
            return redirect(url_for('register'))
    
    try:
        countries = get_countries_and_currencies()
    except Exception as e:
        print(f"Error loading countries: {e}")
        # Fallback countries list
        countries = [
            {'name': 'United States', 'currency': 'USD'},
            {'name': 'India', 'currency': 'INR'},
            {'name': 'United Kingdom', 'currency': 'GBP'},
            {'name': 'Germany', 'currency': 'EUR'},
            {'name': 'France', 'currency': 'EUR'},
            {'name': 'Canada', 'currency': 'CAD'},
            {'name': 'Australia', 'currency': 'AUD'},
            {'name': 'Japan', 'currency': 'JPY'}
        ]
    return render_template('register.html', countries=countries)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email')
        password = data.get('password')
        
        user = User.query.filter_by(email=email).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            if request.is_json:
                return jsonify({'message': 'Login successful', 'redirect': url_for('dashboard')})
            return redirect(url_for('dashboard'))
        
        if request.is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        flash('Invalid credentials')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    # Debug: Print hierarchy information
    if current_user.role == UserRole.MANAGER:
        all_subordinates = get_all_subordinates(current_user)
        print(f"DEBUG: Manager {current_user.full_name} has {len(all_subordinates)} total subordinates:")
        for sub in all_subordinates:
            print(f"  - {sub.full_name} ({sub.role.value})")
    
    # Get expenses based on user role
    if current_user.role == UserRole.ADMIN:
        # Admin sees all company expenses
        expenses = Expense.query.filter_by(company_id=current_user.company_id).order_by(Expense.created_at.desc()).limit(5).all()
    elif current_user.role == UserRole.MANAGER:
        # Manager sees their own expenses and ALL subordinates' expenses (including indirect)
        all_subordinates = get_all_subordinates(current_user)
        subordinate_ids = [user.id for user in all_subordinates]
        subordinate_ids.append(current_user.id)  # Include manager's own expenses
        expenses = Expense.query.filter(Expense.employee_id.in_(subordinate_ids)).order_by(Expense.created_at.desc()).limit(5).all()
    else:
        # Employee sees only their own expenses
        expenses = Expense.query.filter_by(employee_id=current_user.id).order_by(Expense.created_at.desc()).limit(5).all()
    
    # Get pending approvals if user is manager/admin
    pending_approvals = []
    if current_user.role in [UserRole.MANAGER, UserRole.ADMIN]:
        # Get all pending approvals for current user that are ready for processing
        all_pending = Approval.query.filter_by(
            approver_id=current_user.id,
            status='pending'
        ).join(Expense).all()
        
        # Filter to only ready approvals
        ready_approvals = []
        for approval in all_pending:
            if is_approval_ready_for_processing(approval):
                ready_approvals.append(approval)
        
        pending_approvals = sorted(ready_approvals, key=lambda x: x.expense.created_at, reverse=True)[:5]
    
    # Get statistics based on user role
    if current_user.role == UserRole.ADMIN:
        # Admin stats for all company expenses
        stats = {
            'total_expenses': Expense.query.filter_by(company_id=current_user.company_id).count(),
            'pending_expenses': Expense.query.filter_by(
                company_id=current_user.company_id,
                status=ExpenseStatus.PENDING_APPROVAL
            ).count(),
            'approved_expenses': Expense.query.filter_by(
                company_id=current_user.company_id,
                status=ExpenseStatus.APPROVED
            ).count(),
            'pending_approvals': len(pending_approvals)
        }
    elif current_user.role == UserRole.MANAGER:
        # Manager stats for their entire team (including indirect subordinates)
        all_subordinates = get_all_subordinates(current_user)
        subordinate_ids = [user.id for user in all_subordinates]
        subordinate_ids.append(current_user.id)
        stats = {
            'total_expenses': Expense.query.filter(Expense.employee_id.in_(subordinate_ids)).count(),
            'pending_expenses': Expense.query.filter(
                Expense.employee_id.in_(subordinate_ids),
                Expense.status == ExpenseStatus.PENDING_APPROVAL
            ).count(),
            'approved_expenses': Expense.query.filter(
                Expense.employee_id.in_(subordinate_ids),
                Expense.status == ExpenseStatus.APPROVED
            ).count(),
            'pending_approvals': len(pending_approvals)
        }
    else:
        # Employee stats for their own expenses
        stats = {
            'total_expenses': Expense.query.filter_by(employee_id=current_user.id).count(),
            'pending_expenses': Expense.query.filter_by(
                employee_id=current_user.id,
                status=ExpenseStatus.PENDING_APPROVAL
            ).count(),
            'approved_expenses': Expense.query.filter_by(
                employee_id=current_user.id,
                status=ExpenseStatus.APPROVED
            ).count(),
            'pending_approvals': 0  # Employees don't approve expenses
        }
    
    return render_template('dashboard.html', 
                         expenses=expenses, 
                         pending_approvals=pending_approvals,
                         stats=stats)

@app.route('/expenses')
@login_required
def expenses():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    if current_user.role == UserRole.ADMIN:
        expenses_query = Expense.query.filter_by(company_id=current_user.company_id)
    elif current_user.role == UserRole.MANAGER:
        # Manager can see their own expenses and ALL subordinates' expenses (including indirect)
        all_subordinates = get_all_subordinates(current_user)
        subordinate_ids = [user.id for user in all_subordinates]
        subordinate_ids.append(current_user.id)
        expenses_query = Expense.query.filter(Expense.employee_id.in_(subordinate_ids))
    else:
        expenses_query = Expense.query.filter_by(employee_id=current_user.id)
    
    expenses_pagination = expenses_query.order_by(Expense.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('expenses.html', expenses=expenses_pagination)

@app.route('/expenses/new', methods=['GET', 'POST'])
@login_required
def new_expense():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        title = data.get('title')
        description = data.get('description')
        amount = Decimal(str(data.get('amount')))
        currency = data.get('currency')
        expense_date = datetime.strptime(data.get('expense_date'), '%Y-%m-%d').date()
        category_id = int(data.get('category_id'))
        
        # Convert amount to company currency
        company_currency = current_user.company.currency
        exchange_rate = get_exchange_rate(currency, company_currency)
        amount_in_company_currency = amount * Decimal(str(exchange_rate))
        
        expense = Expense(
            title=title,
            description=description,
            amount=amount,
            currency=currency,
            amount_in_company_currency=amount_in_company_currency,
            exchange_rate=Decimal(str(exchange_rate)),
            expense_date=expense_date,
            employee_id=current_user.id,
            company_id=current_user.company_id,
            category_id=category_id,
            status=ExpenseStatus.SUBMITTED
        )
        
        db.session.add(expense)
        db.session.flush()
        
        # Create approval workflow
        create_approval_workflow(expense)
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Expense submitted successfully', 'expense_id': expense.id})
        
        flash('Expense submitted successfully!')
        return redirect(url_for('expenses'))
    
    categories = ExpenseCategory.query.filter_by(company_id=current_user.company_id, is_active=True).all()
    return render_template('new_expense.html', categories=categories)

def create_approval_workflow(expense):
    """Create multi-level approval workflow for an expense"""
    approvals = []
    sequence = 1
    
    # Step 1: Create management hierarchy chain
    management_chain = get_management_hierarchy(expense.employee)
    
    # Step 2: Add approvals for each level in the management chain
    for manager in management_chain:
        approval = Approval(
            expense_id=expense.id,
            approver_id=manager.id,
            sequence=sequence
        )
        approvals.append(approval)
        sequence += 1
    
    # Step 3: Apply additional approval rules based on amount (after management chain)
    rules = ApprovalRule.query.filter(
        ApprovalRule.company_id == expense.company_id,
        ApprovalRule.is_active == True,
        ApprovalRule.min_amount <= expense.amount_in_company_currency
    ).filter(
        db.or_(
            ApprovalRule.max_amount.is_(None),
            ApprovalRule.max_amount >= expense.amount_in_company_currency
        )
    ).order_by(ApprovalRule.sequence).all()
    
    for rule in rules:
        if rule.rule_type == ApprovalRuleType.SPECIFIC_APPROVER:
            # Only add if not already in management chain
            if rule.specific_approver_id not in [m.id for m in management_chain]:
                approval = Approval(
                    expense_id=expense.id,
                    approver_id=rule.specific_approver_id,
                    sequence=sequence
                )
                approvals.append(approval)
                sequence += 1
        elif rule.rule_type in [ApprovalRuleType.PERCENTAGE, ApprovalRuleType.HYBRID]:
            # Add all approvers from the rule (excluding those already in chain)
            for rule_approver in rule.approvers:
                if rule_approver.approver_id not in [m.id for m in management_chain]:
                    approval = Approval(
                        expense_id=expense.id,
                        approver_id=rule_approver.approver_id,
                        sequence=sequence
                    )
                    approvals.append(approval)
            sequence += 1
    
    # Add all approvals to the session
    for approval in approvals:
        db.session.add(approval)
    
    # Update expense status
    if approvals:
        expense.status = ExpenseStatus.PENDING_APPROVAL

def get_management_hierarchy(employee):
    """Get the management hierarchy for an employee (bottom-up)"""
    hierarchy = []
    current_employee = employee
    visited = set()  # Prevent infinite loops
    
    while current_employee and current_employee.manager_id and current_employee.id not in visited:
        visited.add(current_employee.id)
        manager = User.query.get(current_employee.manager_id)
        
        if manager and manager.id not in visited:
            hierarchy.append(manager)
            current_employee = manager
        else:
            break
    
    return hierarchy

def get_all_subordinates(manager):
    """Get all subordinates in the hierarchy (including indirect subordinates)"""
    all_subordinates = []
    visited = set()
    
    def collect_subordinates(user):
        if user.id in visited:
            return
        visited.add(user.id)
        
        # Add direct subordinates
        for subordinate in user.subordinates:
            if subordinate.id not in visited:
                all_subordinates.append(subordinate)
                # Recursively collect their subordinates
                collect_subordinates(subordinate)
    
    collect_subordinates(manager)
    return all_subordinates

@app.route('/approvals')
@login_required
def approvals():
    if current_user.role == UserRole.EMPLOYEE:
        return redirect(url_for('dashboard'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    # Get all pending approvals for current user
    pending_approvals = Approval.query.filter_by(
        approver_id=current_user.id,
        status='pending'
    ).join(Expense).all()
    
    # Filter to only show approvals that are ready for processing
    ready_approvals = []
    for approval in pending_approvals:
        if is_approval_ready_for_processing(approval):
            ready_approvals.append(approval)
    
    # Paginate the ready approvals
    total = len(ready_approvals)
    start = (page - 1) * per_page
    end = start + per_page
    paginated_approvals = ready_approvals[start:end]
    
    # Create a simple pagination object
    class SimplePagination:
        def __init__(self, items, page, per_page, total):
            self.items = items
            self.page = page
            self.per_page = per_page
            self.total = total
            self.pages = (total + per_page - 1) // per_page
            self.has_prev = page > 1
            self.has_next = page < self.pages
            self.prev_num = page - 1 if self.has_prev else None
            self.next_num = page + 1 if self.has_next else None
        
        def iter_pages(self):
            for num in range(1, self.pages + 1):
                yield num
    
    approvals_pagination = SimplePagination(paginated_approvals, page, per_page, total)
    
    return render_template('approvals.html', approvals=approvals_pagination)

def is_approval_ready_for_processing(approval):
    """Check if an approval is ready for processing (all previous approvals are completed)"""
    # Get all approvals for this expense
    all_approvals = Approval.query.filter_by(expense_id=approval.expense_id).order_by(Approval.sequence).all()
    
    # Check if all previous approvals in sequence are approved
    for other_approval in all_approvals:
        if other_approval.sequence < approval.sequence:
            if other_approval.status != 'approved':
                return False  # Previous approval not yet approved
        elif other_approval.sequence == approval.sequence:
            break  # We've reached the current approval
    
    return True  # All previous approvals are approved

@app.route('/approvals/<int:approval_id>/approve', methods=['POST'])
@login_required
def approve_expense(approval_id):
    approval = Approval.query.get_or_404(approval_id)
    
    if approval.approver_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() if request.is_json else request.form
    comments = data.get('comments', '')
    
    approval.status = 'approved'
    approval.comments = comments
    approval.approved_at = datetime.utcnow()
    
    # Check if all required approvals are complete
    expense = approval.expense
    check_expense_approval_status(expense)
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({'message': 'Expense approved successfully'})
    
    flash('Expense approved successfully!')
    return redirect(url_for('approvals'))

@app.route('/approvals/<int:approval_id>/reject', methods=['POST'])
@login_required
def reject_expense(approval_id):
    approval = Approval.query.get_or_404(approval_id)
    
    if approval.approver_id != current_user.id:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.get_json() if request.is_json else request.form
    comments = data.get('comments', '')
    
    approval.status = 'rejected'
    approval.comments = comments
    approval.approved_at = datetime.utcnow()
    
    # Reject the entire expense
    expense = approval.expense
    expense.status = ExpenseStatus.REJECTED
    
    db.session.commit()
    
    if request.is_json:
        return jsonify({'message': 'Expense rejected successfully'})
    
    flash('Expense rejected successfully!')
    return redirect(url_for('approvals'))

def check_expense_approval_status(expense):
    """Check if expense should be approved based on sequential multi-level approval rules"""
    all_approvals = Approval.query.filter_by(expense_id=expense.id).order_by(Approval.sequence).all()
    
    # Check for any rejections first
    rejected_approvals = [a for a in all_approvals if a.status == 'rejected']
    if rejected_approvals:
        expense.status = ExpenseStatus.REJECTED
        return expense.status
    
    # Sequential approval logic
    approved_approvals = [a for a in all_approvals if a.status == 'approved']
    pending_approvals = [a for a in all_approvals if a.status == 'pending']
    
    if not pending_approvals:
        # All approvals are complete (approved)
        expense.status = ExpenseStatus.APPROVED
    else:
        # Check if we need to activate the next approval in sequence
        activate_next_approval_in_sequence(expense, all_approvals)
        expense.status = ExpenseStatus.PENDING_APPROVAL
    
    return expense.status

def activate_next_approval_in_sequence(expense, all_approvals):
    """Activate the next approval in the sequence if the current one is completed"""
    # Find the next pending approval that should be activated
    for approval in all_approvals:
        if approval.status == 'pending':
            # Check if all previous approvals in sequence are approved
            previous_approvals = [a for a in all_approvals if a.sequence < approval.sequence]
            
            if all(a.status == 'approved' for a in previous_approvals):
                # This approval is ready to be processed
                # (It's already pending, so no status change needed)
                break
            else:
                # This approval is not ready yet, mark it as waiting
                # We could add a 'waiting' status if needed
                pass

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', user=current_user)

@app.route('/profile/edit', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Update user information
        current_user.first_name = data.get('first_name', current_user.first_name)
        current_user.last_name = data.get('last_name', current_user.last_name)
        
        # Only allow email change if it's not already taken
        new_email = data.get('email')
        if new_email and new_email != current_user.email:
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user:
                if request.is_json:
                    return jsonify({'error': 'Email already in use'}), 400
                flash('Email already in use')
                return redirect(url_for('edit_profile'))
            current_user.email = new_email
        
        # Update password if provided
        new_password = data.get('password')
        if new_password:
            current_user.password_hash = generate_password_hash(new_password)
        
        try:
            db.session.commit()
            if request.is_json:
                return jsonify({'message': 'Profile updated successfully'})
            flash('Profile updated successfully!')
            return redirect(url_for('profile'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash('Error updating profile')
            return redirect(url_for('edit_profile'))
    
    return render_template('edit_profile.html', user=current_user)

@app.route('/company')
@login_required
def company_settings():
    if current_user.role != UserRole.ADMIN:
        return redirect(url_for('dashboard'))
    
    return render_template('company_settings.html', company=current_user.company)

@app.route('/company/edit', methods=['GET', 'POST'])
@login_required
def edit_company():
    if current_user.role != UserRole.ADMIN:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        # Update company information
        company = current_user.company
        company.name = data.get('company_name', company.name)
        company.country = data.get('country', company.country)
        company.currency = data.get('currency', company.currency)
        
        try:
            db.session.commit()
            if request.is_json:
                return jsonify({'message': 'Company settings updated successfully'})
            flash('Company settings updated successfully!')
            return redirect(url_for('company_settings'))
        except Exception as e:
            db.session.rollback()
            if request.is_json:
                return jsonify({'error': str(e)}), 500
            flash('Error updating company settings')
            return redirect(url_for('edit_company'))
    
    try:
        countries = get_countries_and_currencies()
    except Exception as e:
        print(f"Error loading countries: {e}")
        countries = [
            {'name': 'United States', 'currency': 'USD'},
            {'name': 'India', 'currency': 'INR'},
            {'name': 'United Kingdom', 'currency': 'GBP'},
            {'name': 'Germany', 'currency': 'EUR'},
            {'name': 'France', 'currency': 'EUR'},
            {'name': 'Canada', 'currency': 'CAD'},
            {'name': 'Australia', 'currency': 'AUD'},
            {'name': 'Japan', 'currency': 'JPY'}
        ]
    
    return render_template('edit_company.html', company=current_user.company, countries=countries)

@app.route('/users')
@login_required
def users():
    if current_user.role != UserRole.ADMIN:
        return redirect(url_for('dashboard'))
    
    users = User.query.filter_by(company_id=current_user.company_id).all()
    return render_template('users.html', users=users)

@app.route('/users/new', methods=['GET', 'POST'])
@login_required
def new_user():
    if current_user.role != UserRole.ADMIN:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        data = request.get_json() if request.is_json else request.form
        
        email = data.get('email')
        password = data.get('password')
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        role = UserRole(data.get('role'))
        manager_id = data.get('manager_id') if data.get('manager_id') else None
        
        # Check if user already exists
        if User.query.filter_by(email=email).first():
            if request.is_json:
                return jsonify({'error': 'Email already registered'}), 400
            flash('Email already registered')
            return redirect(url_for('new_user'))
        
        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            first_name=first_name,
            last_name=last_name,
            role=role,
            company_id=current_user.company_id,
            manager_id=manager_id
        )
        
        db.session.add(user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'User created successfully'})
        
        flash('User created successfully!')
        return redirect(url_for('users'))
    
    managers = User.query.filter(
        User.company_id == current_user.company_id,
        User.role.in_([UserRole.MANAGER, UserRole.ADMIN])
    ).all()
    
    return render_template('new_user.html', managers=managers)

@app.route('/api/countries')
def api_countries():
    return jsonify(get_countries_and_currencies())

@app.route('/api/test')
@login_required
def api_test():
    return jsonify({'status': 'ok', 'user': current_user.full_name})

@app.route('/api/debug/hierarchy')
@login_required
def api_debug_hierarchy():
    if current_user.role == UserRole.MANAGER:
        all_subordinates = get_all_subordinates(current_user)
        return jsonify({
            'manager': current_user.full_name,
            'role': current_user.role.value,
            'direct_subordinates': [{'name': sub.full_name, 'role': sub.role.value} for sub in current_user.subordinates],
            'all_subordinates': [{'name': sub.full_name, 'role': sub.role.value} for sub in all_subordinates],
            'total_subordinates': len(all_subordinates)
        })
    else:
        return jsonify({
            'user': current_user.full_name,
            'role': current_user.role.value,
            'message': 'Not a manager'
        })

@app.route('/api/exchange-rate/<from_currency>/<to_currency>')
def api_exchange_rate(from_currency, to_currency):
    rate = get_exchange_rate(from_currency, to_currency)
    return jsonify({'rate': float(rate)})

@app.route('/api/expenses/<int:expense_id>')
@login_required
def api_expense_details(expense_id):
    try:
        expense = Expense.query.get_or_404(expense_id)
        
        # Check permissions
        has_permission = False
        
        if current_user.role == UserRole.ADMIN:
            # Admin can see all expenses in their company
            has_permission = (expense.company_id == current_user.company_id)
        elif current_user.role == UserRole.MANAGER:
            # Manager can see their own expenses and ALL subordinates' expenses (including indirect)
            all_subordinates = get_all_subordinates(current_user)
            subordinate_ids = [u.id for u in all_subordinates] + [current_user.id]
            has_permission = (expense.employee_id in subordinate_ids)
        elif current_user.role == UserRole.EMPLOYEE:
            # Employee can only see their own expenses
            has_permission = (expense.employee_id == current_user.id)
        
        if not has_permission:
            print(f"DEBUG: User {current_user.full_name} ({current_user.role.value}) denied access to expense {expense_id} (owner: {expense.employee.full_name})")
            return jsonify({'error': 'Unauthorized'}), 403
        
        approvals = Approval.query.filter_by(expense_id=expense.id).order_by(Approval.sequence).all()
    except Exception as e:
        print(f"Error in api_expense_details: {e}")
        return jsonify({'error': 'Internal server error'}), 500
    
    try:
        return jsonify({
            'id': expense.id,
            'title': expense.title,
            'description': expense.description,
            'amount': float(expense.amount),
            'currency': expense.currency,
            'amount_in_company_currency': float(expense.amount_in_company_currency) if expense.amount_in_company_currency else float(expense.amount),
            'expense_date': expense.expense_date.isoformat(),
            'status': expense.status.value,
            'employee': expense.employee.full_name,
            'category': expense.category.name,
            'receipt_url': f"/uploads/{expense.receipt_filename}" if expense.receipt_filename else None,
            'management_hierarchy': get_management_hierarchy_info(expense.employee),
            'approvals': [{
                'id': approval.id,
                'approver': approval.approver.full_name,
                'approver_role': approval.approver.role.value,
                'status': approval.status,
                'comments': approval.comments,
                'sequence': approval.sequence,
                'is_ready': is_approval_ready_for_processing(approval),
                'approved_at': approval.approved_at.isoformat() if approval.approved_at else None
            } for approval in approvals]
        })
    except Exception as e:
        print(f"Error creating JSON response: {e}")
        return jsonify({'error': 'Failed to serialize expense data'}), 500

def get_management_hierarchy_info(employee):
    """Get management hierarchy information for display"""
    hierarchy = get_management_hierarchy(employee)
    return [{
        'id': manager.id,
        'name': manager.full_name,
        'role': manager.role.value,
        'level': idx + 1
    } for idx, manager in enumerate(hierarchy)]

@app.route('/api/ocr/process', methods=['POST'])
@login_required
def process_ocr():
    """Process receipt image using OCR"""
    if 'receipt' not in request.files:
        return jsonify({'error': 'No receipt file provided'}), 400
    
    file = request.files['receipt']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Process receipt with OCR
            ocr = get_ocr_instance()
            result = ocr.process_receipt(filepath)
            
            # Clean up uploaded file
            os.remove(filepath)
            
            if result['success']:
                return jsonify(result['data'])
            else:
                return jsonify({'error': result['error']}), 400
                
        except Exception as e:
            # Clean up uploaded file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'OCR processing failed: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type'}), 400

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
