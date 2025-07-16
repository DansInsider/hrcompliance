# HR Compliance Platform - Paradigm International

A lightweight HR compliance and consulting web application built with FastAPI and vanilla JavaScript, designed to support SMB clients (10-200 employees) in healthcare, construction, and professional services.

## Features

### Admin Dashboard (Paradigm Team)
- **Client Management**: Add, view, and manage client company profiles
- **Document Management**: Upload, organize, and assign documents to clients
- **Task Tracking**: Create and manage compliance tasks and internal notes
- **User Management**: Create client user accounts and manage access
- **Analytics**: View client activity and compliance status

### Client Portal
- **Document Access**: View and download assigned compliance documents
- **Task Visibility**: See upcoming training dates and compliance tasks
- **HR Inquiries**: Submit questions, incidents, and requests
- **Dashboard**: Overview of assigned documents and pending items

## Technical Stack

- **Backend**: FastAPI with SQLAlchemy ORM
- **Database**: SQLite (production-ready for SMB scale)
- **Frontend**: Server-side rendered HTML with vanilla JavaScript
- **Authentication**: JWT-based with role-based access control
- **File Storage**: Local filesystem with secure download endpoints

## Project Structure

```
hr-compliance-app/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application entry point
│   │   ├── database.py          # Database configuration
│   │   ├── models/              # SQLAlchemy models
│   │   ├── routes/              # API endpoint definitions
│   │   ├── schemas/             # Pydantic data models
│   │   └── utils/               # Helper functions (auth, file handling)
│   ├── uploads/                 # Document storage directory
│   └── requirements.txt         # Python dependencies
├── frontend/
│   ├── static/                  # CSS and JavaScript files
│   └── templates/               # HTML templates (Jinja2)
├── render.yaml                  # Render.com deployment configuration
└── README.md
```

## Quick Start

### Prerequisites
- Python 3.8+
- pip package manager

### Local Development

1. **Clone and setup**:
```bash
git clone <repository-url>
cd hr-compliance-app
```

2. **Install dependencies**:
```bash
cd backend
pip install -r requirements.txt
```

3. **Initialize database**:
```bash
python -c "from app.database import init_db; init_db()"
```

4. **Create admin user** (Python console):
```python
from app.database import SessionLocal
from app.models.user import User
from app.utils.auth import get_password_hash

db = SessionLocal()
admin_user = User(
    email="admin@paradigm.com",
    hashed_password=get_password_hash("secure_password_123"),
    full_name="Admin User",
    is_admin=True
)
db.add(admin_user)
db.commit()
print(f"Admin user created: {admin_user.email}")
```

5. **Run the application**:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

6. **Access the application**:
- Open http://localhost:8000
- Login with admin credentials created above

### First Steps

1. **Create a test client**:
   - Login as admin
   - Go to Admin > Clients
   - Add a new client company

2. **Create a client user**:
   - Go to Admin > Users (you may need to implement this page)
   - Create a user account linked to the client

3. **Upload documents**:
   - Go to Admin > Documents
   - Upload a test PDF or document
   - Assign it to your test client

4. **Test client portal**:
   - Logout and login as the client user
   - Verify documents and portal access

## Deployment

### Render.com Deployment

1. **Connect repository**:
   - Create account on Render.com
   - Connect your GitHub repository
   - Render will automatically detect the `render.yaml` configuration

2. **Environment variables** (automatically configured):
   - `SECRET_KEY`: Auto-generated for JWT security
   - `DATABASE_URL`: SQLite file path
   - `PORT`: Automatically set by Render

3. **Persistent disk**:
   - Render will create a 10GB disk for database and file storage
   - Files persist across deployments

4. **Access deployed app**:
   - Render provides a URL like `https://hr-compliance-app.onrender.com`

### Alternative Deployment (Replit)

1. **Import to Replit**:
   - Create new Repl from GitHub repository
   - Replit will detect Python environment

2. **Install dependencies**:
```bash
cd backend && pip install -r requirements.txt
```

3. **Configure run command**:
```bash
cd backend && uvicorn app.main:app --host 0.0.0.0 --port 8000
```

4. **Environment variables**:
   - Add `SECRET_KEY` in Replit secrets
   - Database and uploads will persist in Replit storage

## Usage Guide

### For Paradigm Administrators

1. **Client Onboarding**:
   - Create client company profile
   - Upload relevant handbooks and policies
   - Create client user accounts
   - Assign documents to client

2. **Document Management**:
   - Organize by type (handbook, training, checklist, etc.)
   - Assign to multiple clients as needed
   - Track assignment dates and notes

3. **Task Management**:
   - Create compliance tasks and deadlines
   - Track internal notes per client
   - Monitor client inquiry responses

### For Client Users

1. **Document Access**:
   - View assigned documents by category
   - Download current versions
   - Track assignment dates

2. **Submit Inquiries**:
   - Ask HR questions or report incidents
   - Track response status
   - View previous inquiry history

## Security Features

- **Authentication**: JWT tokens with expiration
- **Role-based access**: Admin vs client permissions
- **File security**: Authenticated download endpoints
- **Input validation**: Pydantic schemas for data validation
- **SQL injection protection**: SQLAlchemy ORM

## Customization

### Adding Document Types
```python
# In frontend templates, update document type options
common_types = ["handbook", "training", "checklist", "policy", "form", "template", "custom_type"]
```

### Industry-Specific Features
```python
# In models/client.py, extend industry options
industry_choices = ["healthcare", "construction", "professional_services", "manufacturing", "retail"]
```

### Compliance Workflows
```python
# In models/task.py, add custom task types
task_types = ["compliance_audit", "training", "handbook_review", "safety_inspection", "certification"]
```

## Maintenance

### Database Backups
```bash
# SQLite backup
cp hr_compliance.db hr_compliance_backup_$(date +%Y%m%d).db
```

### File Storage Management
```bash
# Clean old uploads (implement retention policy)
find uploads/ -type f -mtime +365 -delete
```

### User Management
```python
# Deactivate users instead of deleting
user.is_active = False
db.commit()
```

## Support

For technical support or feature requests:
- Create GitHub issues for bugs/features
- Contact: [your-support-email]

## License

Proprietary software for Paradigm International use.