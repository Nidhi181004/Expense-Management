# 🔧 Technical Specification - Expense Management System

## Table of Contents
1. [System Requirements](#system-requirements)
2. [Architecture Patterns](#architecture-patterns)
3. [Code Structure](#code-structure)
4. [Database Schema](#database-schema)
5. [API Specifications](#api-specifications)
6. [Security Specifications](#security-specifications)
7. [Performance Requirements](#performance-requirements)
8. [Integration Specifications](#integration-specifications)

---

## 1. System Requirements

### 1.1 Functional Requirements

#### FR-001: User Authentication
- **Description**: System shall provide secure user authentication
- **Priority**: High
- **Acceptance Criteria**:
  - Users can register with email and password
  - Password must meet complexity requirements (8+ chars, mixed case, numbers)
  - Session management with automatic timeout
  - Role-based access control (Admin, Manager, Employee)

#### FR-002: Expense Management
- **Description**: Users can create, edit, and manage expense reports
- **Priority**: High
- **Acceptance Criteria**:
  - Create expense with title, amount, date, category
  - Upload receipt images (PNG, JPG, PDF)
  - Multi-currency support with automatic conversion
  - Expense status tracking (Draft, Pending, Approved, Rejected, Paid)

#### FR-003: Approval Workflow
- **Description**: Configurable multi-level approval process
- **Priority**: High
- **Acceptance Criteria**:
  - Automatic routing to appropriate approvers
  - Sequential approval processing
  - Approval comments and rejection reasons
  - Email notifications for status changes

#### FR-004: OCR Processing
- **Description**: Automatic data extraction from receipt images
- **Priority**: Medium
- **Acceptance Criteria**:
  - Extract amount, date, merchant name
  - Auto-categorize based on merchant type
  - Pre-fill expense form with extracted data
  - Manual override capability

### 1.2 Non-Functional Requirements

#### NFR-001: Performance
- **Response Time**: < 2 seconds for standard operations
- **Throughput**: Support 100 concurrent users
- **Scalability**: Horizontal scaling capability
- **Availability**: 99.5% uptime

#### NFR-002: Security
- **Authentication**: Strong password hashing (bcrypt)
- **Authorization**: Role-based access control
- **Data Protection**: Encrypted data transmission (HTTPS)
- **Audit Trail**: Complete action logging

#### NFR-003: Usability
- **Responsive Design**: Mobile-first approach
- **Browser Support**: Chrome, Firefox, Safari, Edge
- **Accessibility**: WCAG 2.1 AA compliance
- **Internationalization**: Multi-language support ready

---

## 2. Architecture Patterns

### 2.1 Model-View-Controller (MVC)

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│      View       │    │   Controller    │    │      Model      │
│   (Templates)   │◄──►│    (Routes)     │◄──►│   (Database)    │
│                 │    │                 │    │                 │
│ - HTML Templates│    │ - Route Handlers│    │ - SQLAlchemy    │
│ - JavaScript    │    │ - Business Logic│    │ - Data Models   │
│ - CSS Styles    │    │ - Validation    │    │ - Relationships │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 2.2 Repository Pattern

```python
# Abstract Repository
class BaseRepository:
    def __init__(self, model):
        self.model = model
    
    def get_by_id(self, id):
        return self.model.query.get(id)
    
    def get_all(self):
        return self.model.query.all()
    
    def create(self, **kwargs):
        instance = self.model(**kwargs)
        db.session.add(instance)
        db.session.commit()
        return instance

# Concrete Repository
class ExpenseRepository(BaseRepository):
    def __init__(self):
        super().__init__(Expense)
    
    def get_by_employee(self, employee_id):
        return self.model.query.filter_by(employee_id=employee_id).all()
```

### 2.3 Service Layer Pattern

```python
class ExpenseService:
    def __init__(self):
        self.expense_repo = ExpenseRepository()
        self.approval_service = ApprovalService()
    
    def create_expense(self, expense_data, user):
        # Business logic
        expense = self.expense_repo.create(**expense_data)
        self.approval_service.create_approval_workflow(expense)
        return expense
```

---

## 3. Code Structure

### 3.1 Project Structure

```
expense-management/
├── app.py                      # Application entry point
├── extensions.py               # Flask extensions initialization
├── models.py                   # Database models
├── routes.py                   # Route handlers
├── ocr_utils.py               # OCR processing utilities
├── config.py                   # Configuration settings
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables
├── .gitignore                  # Git ignore rules
├── README.md                   # Project documentation
├── templates/                  # Jinja2 templates
│   ├── base.html              # Base template
│   ├── dashboard.html         # Dashboard page
│   ├── expenses.html          # Expense listing
│   ├── new_expense.html       # Expense creation form
│   ├── approvals.html         # Approval interface
│   └── ...                    # Other templates
├── static/                     # Static assets
│   ├── css/
│   │   └── style.css          # Custom styles
│   ├── js/
│   │   └── main.js            # JavaScript functionality
│   └── images/                # Static images
├── uploads/                    # User uploaded files
├── tests/                      # Test files
│   ├── test_models.py         # Model tests
│   ├── test_routes.py         # Route tests
│   └── test_utils.py          # Utility tests
└── docs/                       # Documentation
    ├── api.md                 # API documentation
    └── deployment.md          # Deployment guide
```

### 3.2 Code Organization Principles

#### 3.2.1 Separation of Concerns
- **Models**: Data structure and business rules
- **Views**: User interface and presentation
- **Controllers**: Request handling and coordination
- **Services**: Business logic and operations
- **Utilities**: Helper functions and tools

#### 3.2.2 Dependency Injection
```python
# Dependency injection pattern
class ExpenseController:
    def __init__(self, expense_service, approval_service):
        self.expense_service = expense_service
        self.approval_service = approval_service
    
    def create_expense(self, request_data):
        return self.expense_service.create(request_data)
```

---

## 4. Database Schema

### 4.1 Table Specifications

#### 4.1.1 Users Table
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK (role IN ('admin', 'manager', 'employee')),
    company_id INTEGER NOT NULL,
    manager_id INTEGER,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (company_id) REFERENCES companies (id),
    FOREIGN KEY (manager_id) REFERENCES users (id)
);
```

#### 4.1.2 Expenses Table
```sql
CREATE TABLE expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    amount DECIMAL(10,2) NOT NULL,
    currency VARCHAR(3) NOT NULL,
    amount_in_company_currency DECIMAL(10,2),
    expense_date DATE NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'draft',
    receipt_filename VARCHAR(255),
    employee_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (employee_id) REFERENCES users (id),
    FOREIGN KEY (category_id) REFERENCES expense_categories (id),
    FOREIGN KEY (company_id) REFERENCES companies (id)
);
```

### 4.2 Indexing Strategy

```sql
-- Performance indexes
CREATE INDEX idx_expenses_employee_id ON expenses(employee_id);
CREATE INDEX idx_expenses_status ON expenses(status);
CREATE INDEX idx_expenses_date ON expenses(expense_date);
CREATE INDEX idx_approvals_approver_status ON approvals(approver_id, status);
CREATE INDEX idx_users_company_role ON users(company_id, role);
```

### 4.3 Data Constraints

```sql
-- Business rule constraints
ALTER TABLE expenses ADD CONSTRAINT chk_amount_positive 
    CHECK (amount > 0);

ALTER TABLE expenses ADD CONSTRAINT chk_status_valid 
    CHECK (status IN ('draft', 'pending_approval', 'approved', 'rejected', 'paid'));

ALTER TABLE users ADD CONSTRAINT chk_email_format 
    CHECK (email LIKE '%@%.%');
```

---

## 5. API Specifications

### 5.1 RESTful API Design

#### 5.1.1 Expense Endpoints

```yaml
# OpenAPI 3.0 Specification
paths:
  /api/expenses:
    get:
      summary: List expenses
      parameters:
        - name: page
          in: query
          schema:
            type: integer
            default: 1
        - name: per_page
          in: query
          schema:
            type: integer
            default: 10
        - name: status
          in: query
          schema:
            type: string
            enum: [draft, pending_approval, approved, rejected, paid]
      responses:
        200:
          description: List of expenses
          content:
            application/json:
              schema:
                type: object
                properties:
                  expenses:
                    type: array
                    items:
                      $ref: '#/components/schemas/Expense'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
    
    post:
      summary: Create new expense
      requestBody:
        required: true
        content:
          multipart/form-data:
            schema:
              type: object
              properties:
                title:
                  type: string
                amount:
                  type: number
                currency:
                  type: string
                expense_date:
                  type: string
                  format: date
                category_id:
                  type: integer
                receipt:
                  type: string
                  format: binary
      responses:
        201:
          description: Expense created
        400:
          description: Validation error
```

### 5.2 Response Formats

#### 5.2.1 Success Response
```json
{
  "status": "success",
  "data": {
    "id": 123,
    "title": "Business Lunch",
    "amount": 45.50,
    "currency": "USD",
    "status": "pending_approval"
  },
  "message": "Expense created successfully"
}
```

#### 5.2.2 Error Response
```json
{
  "status": "error",
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid input data",
    "details": {
      "amount": ["Amount must be greater than 0"],
      "title": ["Title is required"]
    }
  }
}
```

---

## 6. Security Specifications

### 6.1 Authentication & Authorization

#### 6.1.1 Password Security
```python
from werkzeug.security import generate_password_hash, check_password_hash

class User(db.Model):
    password_hash = db.Column(db.String(255), nullable=False)
    
    def set_password(self, password):
        # bcrypt with salt rounds = 12
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256', salt_length=16)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
```

#### 6.1.2 Session Management
```python
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.session_protection = 'strong'
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Session configuration
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=2)
```

### 6.2 Input Validation

#### 6.2.1 Form Validation
```python
from flask_wtf import FlaskForm
from wtforms import StringField, DecimalField, SelectField
from wtforms.validators import DataRequired, NumberRange, Length

class ExpenseForm(FlaskForm):
    title = StringField('Title', validators=[
        DataRequired(),
        Length(min=3, max=200)
    ])
    amount = DecimalField('Amount', validators=[
        DataRequired(),
        NumberRange(min=0.01, max=999999.99)
    ])
    currency = SelectField('Currency', validators=[DataRequired()])
```

#### 6.2.2 File Upload Security
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def secure_filename_custom(filename):
    # Custom secure filename implementation
    filename = secure_filename(filename)
    # Add timestamp to prevent conflicts
    name, ext = os.path.splitext(filename)
    return f"{name}_{int(time.time())}{ext}"
```

---

## 7. Performance Requirements

### 7.1 Response Time Targets

| Operation | Target Response Time | Maximum Acceptable |
|-----------|---------------------|-------------------|
| Page Load | < 1.5 seconds | < 3 seconds |
| Form Submission | < 2 seconds | < 5 seconds |
| File Upload | < 5 seconds | < 10 seconds |
| OCR Processing | < 10 seconds | < 30 seconds |
| Database Query | < 500ms | < 2 seconds |

### 7.2 Scalability Requirements

```python
# Database connection pooling
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

engine = create_engine(
    DATABASE_URL,
    poolclass=QueuePool,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,
    pool_recycle=300
)
```

### 7.3 Caching Strategy

```python
from flask_caching import Cache

# Cache configuration
cache = Cache(config={
    'CACHE_TYPE': 'redis',
    'CACHE_REDIS_URL': 'redis://localhost:6379/0',
    'CACHE_DEFAULT_TIMEOUT': 300
})

# Cache usage
@cache.cached(timeout=300, key_prefix='countries')
def get_countries():
    return expensive_api_call()
```

---

## 8. Integration Specifications

### 8.1 External API Integration

#### 8.1.1 Currency Exchange API
```python
import requests
from typing import Optional

class CurrencyService:
    BASE_URL = "https://api.exchangerate-api.com/v4/latest"
    
    def get_exchange_rate(self, from_currency: str, to_currency: str) -> Optional[float]:
        try:
            response = requests.get(
                f"{self.BASE_URL}/{from_currency}",
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data['rates'].get(to_currency)
        except requests.RequestException as e:
            logger.error(f"Currency API error: {e}")
            return None
```

#### 8.1.2 OCR Service Integration
```python
import pytesseract
from PIL import Image
import re

class OCRService:
    def __init__(self):
        # Configure tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def extract_text(self, image_path: str) -> str:
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image)
            return text
        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            return ""
    
    def parse_receipt(self, text: str) -> dict:
        # Extract amount
        amount_pattern = r'\$?(\d+\.?\d*)'
        amounts = re.findall(amount_pattern, text)
        
        # Extract date
        date_pattern = r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        dates = re.findall(date_pattern, text)
        
        return {
            'amounts': amounts,
            'dates': dates,
            'raw_text': text
        }
```

### 8.2 Email Notification Service

```python
from flask_mail import Mail, Message

class NotificationService:
    def __init__(self, mail: Mail):
        self.mail = mail
    
    def send_approval_notification(self, approver_email: str, expense: Expense):
        msg = Message(
            subject=f"Expense Approval Required: {expense.title}",
            recipients=[approver_email],
            html=render_template('emails/approval_notification.html', expense=expense)
        )
        self.mail.send(msg)
```

---

## 9. Testing Specifications

### 9.1 Unit Testing

```python
import unittest
from app import create_app, db
from models import User, Expense

class ExpenseModelTest(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def test_expense_creation(self):
        user = User(email='test@example.com', first_name='Test', last_name='User')
        db.session.add(user)
        db.session.commit()
        
        expense = Expense(
            title='Test Expense',
            amount=100.00,
            currency='USD',
            employee_id=user.id
        )
        db.session.add(expense)
        db.session.commit()
        
        self.assertEqual(expense.title, 'Test Expense')
        self.assertEqual(expense.amount, 100.00)
```

### 9.2 Integration Testing

```python
class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
    
    def test_expense_creation_api(self):
        # Login user
        response = self.client.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        # Create expense
        response = self.client.post('/api/expenses', data={
            'title': 'Test Expense',
            'amount': 100.00,
            'currency': 'USD'
        })
        
        self.assertEqual(response.status_code, 201)
        data = response.get_json()
        self.assertEqual(data['status'], 'success')
```

---

## 10. Deployment Specifications

### 10.1 Production Environment

```yaml
# docker-compose.yml
version: '3.8'
services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/expense_db
    depends_on:
      - db
      - redis
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=expense_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data
  
  redis:
    image: redis:6-alpine
    
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/ssl
    depends_on:
      - web

volumes:
  postgres_data:
```

### 10.2 Configuration Management

```python
import os
from datetime import timedelta

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///expense.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # File upload settings
    UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER') or 'uploads'
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
    
    # Session settings
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    
    # Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 587)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')

class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///expense_dev.db'

class ProductionConfig(Config):
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

---

This technical specification provides a comprehensive overview of the system's technical implementation, serving as a guide for developers, architects, and stakeholders involved in the project.

*Document Version: 1.0*  
*Last Updated: October 2025*
