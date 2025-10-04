from extensions import db
from flask_login import UserMixin
from datetime import datetime
from enum import Enum
import json

class UserRole(Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    EMPLOYEE = "employee"

class ExpenseStatus(Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    PENDING_APPROVAL = "pending_approval"
    APPROVED = "approved"
    REJECTED = "rejected"
    PAID = "paid"

class ApprovalRuleType(Enum):
    PERCENTAGE = "percentage"
    SPECIFIC_APPROVER = "specific_approver"
    HYBRID = "hybrid"

class Company(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    country = db.Column(db.String(50), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    users = db.relationship('User', backref='company', lazy=True)
    expenses = db.relationship('Expense', backref='company', lazy=True)
    approval_rules = db.relationship('ApprovalRule', backref='company', lazy=True)

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.EMPLOYEE)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    manager_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    subordinates = db.relationship('User', backref=db.backref('manager', remote_side=[id]))
    
    submitted_expenses = db.relationship('Expense', foreign_keys='Expense.employee_id', backref='employee', lazy=True)
    approvals = db.relationship('Approval', backref='approver', lazy=True)

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

class ExpenseCategory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.String(200))
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    expenses = db.relationship('Expense', backref='category', lazy=True)

class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), nullable=False)
    amount_in_company_currency = db.Column(db.Numeric(10, 2))
    exchange_rate = db.Column(db.Numeric(10, 6))
    expense_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.Enum(ExpenseStatus), default=ExpenseStatus.DRAFT)
    receipt_filename = db.Column(db.String(255))
    
    employee_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('expense_category.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    approvals = db.relationship('Approval', backref='expense', lazy=True, cascade='all, delete-orphan')

class ApprovalRule(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    rule_type = db.Column(db.Enum(ApprovalRuleType), nullable=False)
    min_amount = db.Column(db.Numeric(10, 2), default=0)
    max_amount = db.Column(db.Numeric(10, 2))
    percentage_required = db.Column(db.Integer)
    specific_approver_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    is_manager_required = db.Column(db.Boolean, default=True)
    sequence = db.Column(db.Integer, default=1)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    specific_approver = db.relationship('User', foreign_keys=[specific_approver_id])
    approvers = db.relationship('ApprovalRuleApprover', backref='rule', lazy=True)

class ApprovalRuleApprover(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    rule_id = db.Column(db.Integer, db.ForeignKey('approval_rule.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    sequence = db.Column(db.Integer, nullable=False)
    
    approver = db.relationship('User')

class Approval(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    expense_id = db.Column(db.Integer, db.ForeignKey('expense.id'), nullable=False)
    approver_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='pending')
    comments = db.Column(db.Text)
    sequence = db.Column(db.Integer, nullable=False)
    approved_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class CurrencyRate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    from_currency = db.Column(db.String(3), nullable=False)
    to_currency = db.Column(db.String(3), nullable=False)
    rate = db.Column(db.Numeric(10, 6), nullable=False)
    date = db.Column(db.Date, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    __table_args__ = (db.UniqueConstraint('from_currency', 'to_currency', 'date'),)
