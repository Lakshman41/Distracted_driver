from flask import Blueprint, request, jsonify, send_file
from app.services.file_service import FileService
from app.services.token_service import TokenService
from app.models.database import Database
import os

files_bp = Blueprint('files', __name__)
file_service = FileService()
token_service = TokenService()
db = Database()

@files_bp.route('/upload', methods=['POST'])
def upload_files():
    # Validate token and get user info
    token_data = token_service.validation(request.headers.get("Authorization"))
    if token_data['message'] != 'session found':
        return jsonify(token_data)
        
    user_id = token_data['data']['id']
    
    # Check for file in request
    if 'video' in request.files:
        file = request.files['video']
        return file_service.process_video(file, user_id, token_service)
    elif 'image' in request.files:
        file = request.files['image']
        return file_service.process_image(file, user_id, token_service)
    else:
        return jsonify({"message": "No file part"}), 400

@files_bp.route('/user-files', methods=['GET'])
def user_files():
    token_data = token_service.validation(request.headers.get("Authorization"))
    if token_data['message'] != 'session found':
        return jsonify(token_data)
        
    user_id = token_data['data']['id']
    return jsonify(db.get_user_files(user_id))

@files_bp.route('/send_data/<int:no>', methods=['GET'])
def send_data(no):
    token_data = token_service.validation(request.headers.get("Authorization"))
    if token_data['message'] != 'session found':
        return jsonify(token_data)
        
    file_id = token_data['data']['file_id']
    data = db.result_get(file_id)
    
    if not data or no >= len(data):
        return jsonify({"message": "Data not found"}), 404
        
    return jsonify({
        'result': data[no]['result'],
        'category': data[no]['category']
    })

@files_bp.route('/send_file/<int:no>', methods=['GET'])
def send_file_db(no):
    token_data = token_service.validation(request.headers.get("Authorization"))
    if token_data['message'] != 'session found':
        return jsonify(token_data)
        
    file_id = token_data['data']['file_id']
    data = db.result_get(file_id)
    
    if not data or no >= len(data):
        return jsonify({"message": "File not found"}), 404
        
    path = os.path.join(data[no]['path'], data[no]['category'], data[no]['name'])
    return send_file(path), 200 