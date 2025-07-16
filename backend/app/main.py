from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db
from app.routes import auth, admin, client, documents
import os

# Initialize FastAPI app
app = FastAPI(
    title="HR Compliance Platform",
    description="Paradigm International HR Compliance and Consulting Platform",
    version="1.0.0"
)

# CORS middleware for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth.router, prefix="/api")
app.include_router(admin.router, prefix="/api")
app.include_router(client.router, prefix="/api")
app.include_router(documents.router, prefix="/api")

# Serve static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

# Frontend routes (HTML pages)
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Home page with login form"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/admin/dashboard", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Admin dashboard page"""
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})

@app.get("/admin/clients", response_class=HTMLResponse)
async def admin_clients(request: Request):
    """Admin clients management page"""
    return templates.TemplateResponse("admin/clients.html", {"request": request})

@app.get("/admin/documents", response_class=HTMLResponse)
async def admin_documents(request: Request):
    """Admin documents management page"""
    return templates.TemplateResponse("admin/documents.html", {"request": request})

@app.get("/client/portal", response_class=HTMLResponse)
async def client_portal(request: Request):
    """Client portal dashboard"""
    return templates.TemplateResponse("client/portal.html", {"request": request})

@app.get("/client/documents", response_class=HTMLResponse)
async def client_documents(request: Request):
    """Client documents page"""
    return templates.TemplateResponse("client/documents.html", {"request": request})

@app.get("/client/submit-inquiry", response_class=HTMLResponse)
async def client_submit_inquiry(request: Request):
    """Client inquiry submission page"""
    return templates.TemplateResponse("client/submit_inquiry.html", {"request": request})

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint for deployment monitoring"""
    return {"status": "healthy", "message": "HR Compliance Platform is running"}

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database tables on startup"""
    init_db()
    
    # Create uploads directory if it doesn't exist
    os.makedirs("uploads", exist_ok=True)
    
    print("HR Compliance Platform started successfully!")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)