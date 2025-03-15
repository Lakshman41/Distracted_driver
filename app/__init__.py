from flask import Flask
from flask_cors import CORS
from app.config.config import Config
from app.routes.auth import auth_bp
from app.routes.files import files_bp
from app.utils.file_utils import setup_upload_folders

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize CORS
    CORS(app, 
         resources={r"/*": {"origins": Config.CORS_ORIGINS, 
                          "supports_credentials": Config.CORS_SUPPORTS_CREDENTIALS}})
    
    # Create upload folders
    setup_upload_folders()
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(files_bp)
    
    return app 