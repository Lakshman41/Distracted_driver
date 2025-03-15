import os
from werkzeug.utils import secure_filename
from app.config.config import Config
from app.utils.file_utils import allowed_file, save_file, create_directory
from app.models.model import Model
from app.models.database import Database
from flask import request

class FileService:
    def __init__(self):
        self.model = Model()
        self.db = Database()
    
    def process_video(self, file, user_id, token_service):
        """Process uploaded video file"""
        if not allowed_file(file.filename, Config.ALLOWED_EXTENSIONS_VIDEO):
            return {"error": "File type not allowed"}, 400
            
        filename = secure_filename(file.filename)
        video_folder = os.path.join(Config.UPLOAD_FOLDER, 'videos')
        create_directory(video_folder)
        
        # Save video file
        main_file_path = save_file(file, video_folder, filename)
        
        # Insert file record and get file_id
        file_id = self.db.file_insert(user_id, "video", filename, video_folder)
        token_service.set_file_id(request.headers.get("Authorization"), file_id)
        
        # Setup processing folders
        frames_folder = os.path.join(Config.UPLOAD_FOLDER, 'frames')
        video_frames_folder = os.path.join(frames_folder, filename)
        result_folder = os.path.join(Config.UPLOAD_FOLDER, 'result')
        
        create_directory(frames_folder)
        create_directory(video_frames_folder)
        create_directory(result_folder)
        
        # Process video
        count = self.model.predict_distracted_driver_on_video(
            main_file_path, 
            video_frames_folder, 
            result_folder,
            file_id
        )
        
        return {"message": f"Video processed successfully", "count": count}, 200
    
    def process_image(self, file, user_id, token_service):
        """Process uploaded image file"""
        if not allowed_file(file.filename, Config.ALLOWED_EXTENSIONS_IMAGE):
            return {"error": "File type not allowed"}, 400
            
        filename = secure_filename(file.filename)
        image_folder = os.path.join(Config.UPLOAD_FOLDER, 'images')
        create_directory(image_folder)
        
        # Save image file
        main_file_path = save_file(file, image_folder, filename)
        
        # Insert file record and get file_id
        file_id = self.db.file_insert(user_id, "image", filename, image_folder)
        token_service.set_file_id(request.headers.get("Authorization"), file_id)
        
        # Process image
        results = self.model.predict_distracted_driver_on_image(image_folder, filename, file_id)
        
        # Determine distraction status
        if results == 0:
            status = "Undistracted"
        elif 1 <= results <= 10:
            status = "Distracted"
        else:
            return {"error": "Model prediction failed"}, 500
        
        # Create result folder and save processed image
        result_folder = os.path.join(Config.UPLOAD_FOLDER, 'result')
        result_subfolder = os.path.join(result_folder, str(results))
        create_directory(result_subfolder)
        
        result_file_path = os.path.join(result_subfolder, filename)
        with open(result_file_path, 'wb') as f:
            f.write(file.read())
        
        # Insert result record
        self.db.result_insert(file_id, filename, result_folder, status, results)
        
        return {"message": f"Image processed successfully", "count": 1}, 200 