# Expense Management System

A comprehensive web-based expense management system built with Flask, featuring multi-role authentication, approval workflows, currency conversion, and OCR receipt scanning.

## Features

### 🔐 Authentication & User Management
- **Multi-role system**: Admin, Manager, Employee roles with appropriate permissions
- **Auto-company creation**: On first signup, a new company is created with country-based currency
- **User management**: Admins can create, edit, and manage users
- **Manager relationships**: Define hierarchical manager-employee relationships

### 💰 Expense Management
- **Multi-currency support**: Submit expenses in different currencies with automatic conversion
- **Expense categories**: Organize expenses by categories (Travel, Meals, Office Supplies, etc.)
- **Receipt uploads**: Attach receipt images to expense claims
- **Expense history**: View and track all submitted expenses

### ✅ Approval Workflows
- **Multi-level approvals**: Define complex approval workflows with multiple steps
- **Manager approval**: Automatic routing to employee's manager
- **Conditional rules**: 
  - Percentage-based approval (e.g., 60% of approvers must approve)
  - Specific approver rules (e.g., CFO approval required)
  - Hybrid rules combining both approaches
- **Sequential processing**: Expenses move through approval steps in order
- **Comments system**: Approvers can add comments when approving/rejecting

### 🤖 OCR Receipt Scanning
- **Automatic data extraction**: Upload receipt images to auto-populate expense details
- **Smart categorization**: Automatically categorize expenses based on merchant type
- **Multi-format support**: Supports PNG, JPG, PDF, and other image formats

### 🌍 Multi-Currency & Localization
- **Real-time exchange rates**: Integration with external APIs for current exchange rates
- **Country-based setup**: Automatic currency selection based on company country
- **Currency conversion**: Automatic conversion to company's base currency

### 📊 Dashboard & Analytics
- **Comprehensive dashboard**: Overview of expenses, approvals, and statistics
- **Role-based views**: Different dashboard views for different user roles
- **Quick actions**: Fast access to common tasks

## Technology Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite (easily configurable for PostgreSQL/MySQL)
- **Frontend**: Bootstrap 5, jQuery, Font Awesome
- **OCR**: Tesseract OCR (with mock fallback for development)
- **APIs**: REST Countries API, Exchange Rate API

## Installation

### Prerequisites
- Python 3.8+
- pip (Python package manager)
- Optional: Tesseract OCR for receipt scanning

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Expense-Management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env file with your configuration
   ```

5. **Initialize database**
   ```bash
   python app.py
   ```

6. **Access the application**
   Open your browser and go to `http://localhost:5000`

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
SECRET_KEY=your-super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///expense_management.db
FLASK_ENV=development
EXCHANGE_RATE_API_KEY=your-api-key-here
```

### OCR Setup (Optional)

For receipt scanning functionality:

1. **Install Tesseract OCR**
   - Windows: Download from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
   - macOS: `brew install tesseract`
   - Ubuntu: `sudo apt install tesseract-ocr`

2. **Configure path** (if needed)
   Update the tesseract path in `ocr_utils.py`

## Usage

### First Time Setup

1. **Register as Admin**
   - Visit the registration page
   - Fill in your details and company information
   - Select your country (currency will be set automatically)
   - You'll be created as the Admin user

2. **Add Users**
   - Go to Users → Add User
   - Create Manager and Employee accounts
   - Set up manager relationships

3. **Configure Categories**
   - Default categories are created automatically
   - Admins can add/modify expense categories

### Submitting Expenses

1. **Manual Entry**
   - Go to "New Expense"
   - Fill in expense details
   - Upload receipt (optional)
   - Submit for approval

2. **OCR Scanning**
   - Use the "Quick Receipt Scan" feature
   - Upload or take a photo of your receipt
   - Click "Extract Details" to auto-populate fields
   - Review and submit

### Approval Process

1. **For Managers/Admins**
   - View pending approvals on dashboard
   - Go to "Approvals" for detailed view
   - Add comments and approve/reject expenses

2. **Workflow Rules**
   - Expenses follow defined approval rules
   - Sequential processing ensures proper authorization
   - Conditional rules provide flexibility

## API Endpoints

### Authentication
- `POST /register` - User registration
- `POST /login` - User login
- `GET /logout` - User logout

### Expenses
- `GET /expenses` - List expenses
- `POST /expenses/new` - Create new expense
- `GET /api/expenses/<id>` - Get expense details

### Approvals
- `GET /approvals` - List pending approvals
- `POST /approvals/<id>/approve` - Approve expense
- `POST /approvals/<id>/reject` - Reject expense

### OCR
- `POST /api/ocr/process` - Process receipt image

### Utilities
- `GET /api/countries` - Get countries and currencies
- `GET /api/exchange-rate/<from>/<to>` - Get exchange rate

## Database Schema

### Key Models
- **User**: User accounts with roles and relationships
- **Company**: Company information and settings
- **Expense**: Expense records with amounts and metadata
- **Approval**: Approval workflow steps
- **ApprovalRule**: Configurable approval rules
- **ExpenseCategory**: Expense categorization

## Security Features

- **Password hashing**: Secure password storage using bcrypt
- **Session management**: Flask-Login for secure sessions
- **Role-based access**: Proper authorization checks
- **Input validation**: Form validation and sanitization
- **File upload security**: Secure file handling for receipts

## Development

### Running in Development Mode

```bash
export FLASK_ENV=development
python app.py
```

### Database Migrations

```bash
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

### Testing

```bash
python -m pytest tests/
```

## Deployment

### Production Considerations

1. **Environment Variables**
   - Set strong SECRET_KEY
   - Use production database (PostgreSQL recommended)
   - Configure proper CORS settings

2. **Web Server**
   - Use Gunicorn or uWSGI
   - Configure reverse proxy (Nginx)
   - Set up SSL certificates

3. **Database**
   - Use PostgreSQL or MySQL for production
   - Set up regular backups
   - Configure connection pooling

### Docker Deployment

```dockerfile
# Dockerfile example
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API endpoints

## Roadmap

- [ ] Mobile app development
- [ ] Advanced reporting and analytics
- [ ] Integration with accounting systems
- [ ] Bulk expense import/export
- [ ] Advanced OCR with machine learning
- [ ] Multi-language support
- [ ] Audit trail and compliance features
