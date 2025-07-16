#!/usr/bin/env python3
"""
Setup script for HR Compliance Platform on Replit
Run this script to initialize the database and create an admin user
"""

import os
import sys
from pathlib import Path

def setup_environment():
    """Setup basic environment"""
    print("🔧 Setting up HR Compliance Platform...")
    
    # Create uploads directory
    os.makedirs("uploads", exist_ok=True)
    print("✅ Created uploads directory")
    
    # Set environment variables for Replit
    os.environ.setdefault("SECRET_KEY", "replit-dev-secret-key-change-in-production")
    os.environ.setdefault("DATABASE_URL", "sqlite:///./hr_compliance.db")
    print("✅ Environment variables set")

def initialize_database():
    """Initialize database tables"""
    print("🗄️ Initializing database...")
    
    try:
        from backend.app.database import init_db
        init_db()
        print("✅ Database tables created")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    return True

def create_admin_user():
    """Create default admin user"""
    print("👤 Creating admin user...")
    
    try:
        from backend.app.database import SessionLocal
        from backend.app.models.user import User
        from backend.app.utils.auth import get_password_hash
        
        db = SessionLocal()
        
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.email == "admin@paradigm.com").first()
        if existing_admin:
            print("⚠️ Admin user already exists")
            db.close()
            return True
        
        # Create admin user
        admin_user = User(
            email="admin@paradigm.com",
            hashed_password=get_password_hash("paradigm123"),
            full_name="Paradigm Admin",
            is_admin=True
        )
        
        db.add(admin_user)
        db.commit()
        db.close()
        
        print("✅ Admin user created:")
        print("   Email: admin@paradigm.com")
        print("   Password: paradigm123")
        print("   🔒 Change this password after first login!")
        
    except Exception as e:
        print(f"❌ Admin user creation failed: {e}")
        return False
    
    return True

def create_sample_client():
    """Create a sample client for testing"""
    print("🏢 Creating sample client...")
    
    try:
        from backend.app.database import SessionLocal
        from backend.app.models.client import Client
        from backend.app.models.user import User
        from backend.app.utils.auth import get_password_hash
        
        db = SessionLocal()
        
        # Create sample client company
        sample_client = Client(
            company_name="ABC Healthcare Services",
            industry="healthcare",
            employee_count=45,
            point_of_contact="Jane Smith",
            contact_email="jane@abchealthcare.com",
            contact_phone="(555) 123-4567",
            address="123 Medical Plaza, Health City, HC 12345",
            notes="Sample client for testing the platform"
        )
        
        db.add(sample_client)
        db.commit()
        db.refresh(sample_client)
        
        # Create client user
        client_user = User(
            email="jane@abchealthcare.com",
            hashed_password=get_password_hash("client123"),
            full_name="Jane Smith",
            is_admin=False,
            client_id=sample_client.id
        )
        
        db.add(client_user)
        db.commit()
        db.close()
        
        print("✅ Sample client created:")
        print("   Company: ABC Healthcare Services")
        print("   Client Login - Email: jane@abchealthcare.com")
        print("   Client Login - Password: client123")
        
    except Exception as e:
        print(f"⚠️ Sample client creation failed (may already exist): {e}")
        return False
    
    return True

def main():
    """Main setup function"""
    print("=" * 50)
    print("🏥 HR COMPLIANCE PLATFORM SETUP")
    print("=" * 50)
    
    # Add backend to Python path
    backend_path = Path(__file__).parent / "backend"
    sys.path.insert(0, str(backend_path))
    
    # Run setup steps
    setup_environment()
    
    if not initialize_database():
        print("❌ Setup failed at database initialization")
        return
    
    if not create_admin_user():
        print("❌ Setup failed at admin user creation")
        return
    
    create_sample_client()  # This is optional, so we don't fail if it doesn't work
    
    print("=" * 50)
    print("🎉 SETUP COMPLETE!")
    print("=" * 50)
    print("🌐 Your app is ready to run!")
    print("📝 Next steps:")
    print("   1. Click the 'Run' button")
    print("   2. Open the web preview")
    print("   3. Login with admin credentials above")
    print("   4. Start adding your clients!")
    print("=" * 50)

if __name__ == "__main__":
    main()