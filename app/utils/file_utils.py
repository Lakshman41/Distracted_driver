import os
from werkzeug.utils import secure_filename
from app.config.config import Config

def allowed_file(filename, allowed_extensions):
    """Check if the file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def create_directory(path):
    """Create directory if it doesn't exist"""
    if not os.path.exists(path):
        os.makedirs(path)

def save_file(file, folder, filename):
    """Save uploaded file to specified folder"""
    file_content = file.read()
    file_path = os.path.join(folder, filename)
    with open(file_path, 'wb') as f:
        f.write(file_content)
    return file_path

def setup_upload_folders():
    """Create all necessary upload folders"""
    folders = [
        Config.UPLOAD_FOLDER,
        os.path.join(Config.UPLOAD_FOLDER, 'videos'),
        os.path.join(Config.UPLOAD_FOLDER, 'images'),
        os.path.join(Config.UPLOAD_FOLDER, 'frames'),
        os.path.join(Config.UPLOAD_FOLDER, 'result')
    ]
    
    for folder in folders:
        create_directory(folder) 