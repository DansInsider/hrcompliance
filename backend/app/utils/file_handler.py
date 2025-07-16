import os
import shutil
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException
from pathlib import Path

# Configuration
UPLOAD_DIR = "uploads"
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB
ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", 
    ".ppt", ".pptx", ".txt", ".jpg", ".jpeg", 
    ".png", ".gif", ".zip"
}

def ensure_upload_directory():
    """Ensure upload directory exists"""
    Path(UPLOAD_DIR).mkdir(exist_ok=True)

def generate_unique_filename(original_filename: str) -> str:
    """Generate unique filename while preserving extension"""
    file_extension = Path(original_filename).suffix.lower()
    unique_id = str(uuid.uuid4())
    return f"{unique_id}{file_extension}"

def validate_file(file: UploadFile) -> bool:
    """Validate uploaded file"""
    # Check file extension
    file_extension = Path(file.filename or "").suffix.lower()
    if file_extension not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    return True

async def save_upload_file(file: UploadFile, destination_path: str) -> int:
    """Save uploaded file to destination and return file size"""
    file_size = 0
    
    with open(destination_path, "wb") as buffer:
        while chunk := await file.read(8192):  # Read in 8KB chunks
            file_size += len(chunk)
            
            # Check file size limit
            if file_size > MAX_FILE_SIZE:
                # Clean up partial file
                os.remove(destination_path)
                raise HTTPException(
                    status_code=400,
                    detail=f"File too large. Maximum size: {MAX_FILE_SIZE // (1024*1024)}MB"
                )
            
            buffer.write(chunk)
    
    return file_size

async def handle_file_upload(file: UploadFile) -> tuple[str, str, int]:
    """
    Handle file upload and return (unique_filename, file_path, file_size)
    """
    # Validate file
    validate_file(file)
    
    # Ensure upload directory exists
    ensure_upload_directory()
    
    # Generate unique filename
    unique_filename = generate_unique_filename(file.filename or "unknown")
    file_path = os.path.join(UPLOAD_DIR, unique_filename)
    
    # Save file
    file_size = await save_upload_file(file, file_path)
    
    return unique_filename, file_path, file_size

def delete_file(file_path: str) -> bool:
    """Delete file from filesystem"""
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False

def get_file_info(file_path: str) -> Optional[dict]:
    """Get file information"""
    try:
        if os.path.exists(file_path):
            stat = os.stat(file_path)
            return {
                "size": stat.st_size,
                "created": stat.st_ctime,
                "modified": stat.st_mtime
            }
        return None
    except Exception:
        return None