# 📋 Expense Management System - Complete Project Documentation

## Table of Contents
1. [Project Overview](#project-overview)
2. [System Architecture](#system-architecture)
3. [Use Case Diagrams](#use-case-diagrams)
4. [Flow Charts](#flow-charts)
5. [Database Design](#database-design)
6. [Technology Stack](#technology-stack)
7. [Feature Analysis](#feature-analysis)
8. [Security Implementation](#security-implementation)
9. [API Documentation](#api-documentation)
10. [Deployment Guide](#deployment-guide)

---

## 1. Project Overview

### 1.1 Project Description
The Expense Management System is a comprehensive web-based application designed to streamline expense reporting, approval workflows, and financial management for organizations of all sizes. Built with modern web technologies, it provides a scalable, secure, and user-friendly platform for managing business expenses.

### 1.2 Key Features
- **Multi-role Authentication**: Admin, Manager, Employee roles with hierarchical permissions
- **Expense Management**: Create, edit, track expenses with multi-currency support
- **Approval Workflows**: Configurable multi-level approval processes
- **OCR Integration**: Automatic receipt data extraction using Tesseract OCR
- **Real-time Analytics**: Dashboard with spending insights and statistics
- **Responsive Design**: Mobile-first UI with Bootstrap 5

---

## 2. System Architecture

### 2.1 High-Level Architecture

```mermaid
graph TB
    subgraph "Client Layer"
        A[Web Browser]
        B[Mobile Browser]
    end
    
    subgraph "Presentation Layer"
        C[Flask Templates]
        D[Bootstrap UI]
        E[JavaScript/jQuery]
    end
    
    subgraph "Application Layer"
        F[Flask Application]
        G[Route Handlers]
        H[Business Logic]
        I[Authentication]
    end
    
    subgraph "Data Layer"
        J[SQLAlchemy ORM]
        K[Database Models]
        L[SQLite/PostgreSQL]
    end
    
    subgraph "External Services"
        M[OCR Service]
        N[Currency API]
        O[File Storage]
    end
    
    A --> C
    B --> C
    C --> F
    D --> F
    E --> F
    F --> G
    G --> H
    H --> I
    H --> J
    J --> K
    K --> L
    H --> M
    H --> N
    H --> O
```

---

## 3. Use Case Diagrams

### 3.1 Employee Use Cases

```mermaid
graph LR
    Employee((Employee))
    
    Employee --> UC1[Submit Expense]
    Employee --> UC2[Upload Receipt]
    Employee --> UC3[Track Status]
    Employee --> UC4[Edit Profile]
    Employee --> UC5[View History]
    
    UC1 --> UC1a[Fill Details]
    UC1 --> UC1b[Select Category]
    UC1 --> UC1c[Add Receipt]
    
    UC2 --> UC2a[OCR Scan]
    UC2 --> UC2b[Manual Upload]
```

### 3.2 Manager Use Cases

```mermaid
graph LR
    Manager((Manager))
    
    Manager --> UC6[Review Expenses]
    Manager --> UC7[Approve/Reject]
    Manager --> UC8[Add Comments]
    Manager --> UC9[View Team Reports]
    Manager --> UC10[Manage Subordinates]
    
    UC6 --> UC6a[View Details]
    UC6 --> UC6b[Check Receipts]
    UC6 --> UC6c[Verify Amounts]
    
    UC7 --> UC7a[Bulk Actions]
    UC7 --> UC7b[Individual Review]
```

### 3.3 Admin Use Cases

```mermaid
graph LR
    Admin((Administrator))
    
    Admin --> UC11[User Management]
    Admin --> UC12[Company Settings]
    Admin --> UC13[System Configuration]
    Admin --> UC14[Reports & Analytics]
    Admin --> UC15[Approval Rules]
    
    UC11 --> UC11a[Create Users]
    UC11 --> UC11b[Assign Roles]
    UC11 --> UC11c[Set Managers]
    
    UC13 --> UC13a[Categories]
    UC13 --> UC13b[Currencies]
    UC13 --> UC13c[Workflows]
```

---

## 4. Flow Charts

### 4.1 Expense Submission Flow

```mermaid
flowchart TD
    A[Employee Logs In] --> B[Navigate to New Expense]
    B --> C{Use OCR?}
    
    C -->|Yes| D[Upload Receipt]
    C -->|No| E[Manual Entry]
    
    D --> F[OCR Processing]
    F --> G[Extract Data]
    G --> H[Pre-fill Form]
    H --> I[Review & Edit]
    
    E --> I
    I --> J[Select Category]
    J --> K[Add Currency/Amount]
    K --> L[Submit Expense]
    
    L --> M[Create Expense Record]
    M --> N[Generate Approvals]
    N --> O[Notify Approvers]
    O --> P[Update Status]
    P --> Q[End]
```

### 4.2 Approval Workflow

```mermaid
flowchart TD
    A[Expense Submitted] --> B[Check Approval Rules]
    B --> C{Rules Exist?}
    
    C -->|No| D[Auto Approve]
    C -->|Yes| E[Create Approval Chain]
    
    E --> F[Notify First Approver]
    F --> G[Approver Reviews]
    G --> H{Decision}
    
    H -->|Approve| I{More Approvers?}
    H -->|Reject| J[Mark Rejected]
    H -->|Request Info| K[Send Back to Employee]
    
    I -->|Yes| L[Notify Next Approver]
    I -->|No| M[Mark Approved]
    
    L --> G
    J --> N[Notify Employee]
    K --> N
    M --> O[Process Payment]
    N --> P[End]
    O --> P
```

---

## 5. Database Design

### 5.1 Entity Relationship Diagram

```mermaid
erDiagram
    Company ||--o{ User : has
    Company ||--o{ ExpenseCategory : defines
    
    User ||--o{ Expense : submits
    User ||--o{ Approval : approves
    User ||--o{ User : manages
    
    Expense ||--o{ Approval : requires
    Expense }o--|| ExpenseCategory : belongs_to
    
    ApprovalRule ||--o{ Approval : governs
    
    Company {
        int id PK
        string name
        string country
        string currency
        datetime created_at
        datetime updated_at
    }
    
    User {
        int id PK
        string email UK
        string password_hash
        string first_name
        string last_name
        enum role
        int company_id FK
        int manager_id FK
        datetime created_at
        datetime updated_at
    }
    
    Expense {
        int id PK
        string title
        text description
        decimal amount
        string currency
        decimal amount_in_company_currency
        date expense_date
        enum status
        string receipt_filename
        int employee_id FK
        int category_id FK
        int company_id FK
        datetime created_at
        datetime updated_at
    }
    
    Approval {
        int id PK
        int expense_id FK
        int approver_id FK
        enum status
        text comments
        int sequence
        datetime approved_at
        datetime created_at
        datetime updated_at
    }
```

---

## 6. Technology Stack

### 6.1 Backend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **Python** | 3.8+ | Core programming language |
| **Flask** | 2.0+ | Web framework |
| **SQLAlchemy** | 1.4+ | ORM and database abstraction |
| **Flask-Login** | 0.6+ | User session management |
| **Flask-WTF** | 1.0+ | Form handling and CSRF protection |
| **Werkzeug** | 2.0+ | Password hashing and utilities |
| **Pillow** | 8.0+ | Image processing |
| **Requests** | 2.25+ | HTTP client for external APIs |

### 6.2 Frontend Technologies

| Technology | Version | Purpose |
|------------|---------|---------|
| **HTML5** | - | Markup language |
| **CSS3** | - | Styling and layout |
| **Bootstrap** | 5.0+ | UI framework and responsive design |
| **JavaScript** | ES6+ | Client-side scripting |
| **jQuery** | 3.6+ | DOM manipulation and AJAX |
| **Font Awesome** | 6.0+ | Icons and visual elements |

---

## 7. API Documentation

### 7.1 Authentication Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| POST | `/register` | User registration | email, password, company_info |
| POST | `/login` | User authentication | email, password |
| GET | `/logout` | User logout | - |

### 7.2 Expense Management Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/expenses` | List user expenses | page, per_page |
| POST | `/expenses/new` | Create new expense | expense_data, receipt_file |
| GET | `/api/expenses/<id>` | Get expense details | expense_id |
| PUT | `/api/expenses/<id>` | Update expense | expense_id, expense_data |

### 7.3 Approval Endpoints

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/approvals` | List pending approvals | page, per_page |
| POST | `/approvals/<id>/approve` | Approve expense | approval_id, comments |
| POST | `/approvals/<id>/reject` | Reject expense | approval_id, comments |

---

## 8. Security Implementation

### 8.1 Security Layers

- **Authentication**: bcrypt password hashing with salt
- **Authorization**: Role-based access control (RBAC)
- **Session Management**: Secure cookie-based sessions
- **CSRF Protection**: Token-based validation
- **Input Validation**: Server-side validation for all inputs
- **File Upload Security**: Type validation and size limits
- **SQL Injection Prevention**: Parameterized queries via ORM

---

## 9. Deployment Guide

### 9.1 Development Setup

```bash
# Clone repository
git clone <repository-url>
cd expense-management

# Setup virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your configuration

# Run application
python app.py
```

### 9.2 Production Deployment

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
  
  db:
    image: postgres:13
    environment:
      - POSTGRES_DB=expense_db
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

*Document Version: 1.0*  
*Last Updated: October 2025*  
*Author: Development Team*
