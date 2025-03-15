import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY")
    UPLOAD_FOLDER = os.path.abspath('uploads/')
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # File upload settings
    ALLOWED_EXTENSIONS_VIDEO = {'mp4', 'mov', 'avi', 'mkv'}
    ALLOWED_EXTENSIONS_IMAGE = {'jpeg', 'png', 'jpg'}
    
    # CORS settings
    CORS_ORIGINS = "*"
    CORS_SUPPORTS_CREDENTIALS = True 