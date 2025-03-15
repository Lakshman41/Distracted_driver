from flask import Blueprint, request, jsonify, session
from app.models.database import Database
from app.services.token_service import TokenService

auth_bp = Blueprint('auth', __name__)
db = Database()
token_service = TokenService()

@auth_bp.route('/test-session', methods=['GET'])
def test_session():
    return jsonify({
        "message": 'working',
    })

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400
        
    if 'username' in data:
        result = db.data_username(data['username'])
    elif 'email' in data:
        result = db.data_email_id(data['email'])
    else:
        return jsonify({"message": "Invalid credentials"}), 400
        
    if result:
        session['id'] = result['id']
        tokens = token_service.generate_tokens(result['id'])
        result.update(tokens)
        return jsonify(result), 200
        
    return jsonify({"message": "Credentials not found"}), 400

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.json
    if not data or not all(key in data for key in ['username', 'email_id']):
        return jsonify({"message": "Missing required fields"}), 400
        
    result = db.insert(data['username'], data['email_id'])
    session['id'] = result
    
    tokens = token_service.generate_tokens(result)
    return jsonify({
        "message": "User registered Successfully",
        "token": tokens['token']
    }), 200

@auth_bp.route('/google', methods=['POST'])
def google_auth():
    data = request.json
    if not data or 'email' not in data:
        return jsonify({"message": "No data provided"}), 400
        
    result = db.data_email_id(data['email'])
    
    if result['message'] == 'Data Found':
        session['id'] = result['id']
        tokens = token_service.generate_tokens(result['id'])
        result.update(tokens)
        session.modified = True
        
        return jsonify({
            'message': 'Exist',
            'username': result['username'],
            'id': result['id'],
            'token': result['token']
        }), 200
        
    return jsonify({'message': 'Not exist'}), 200

@auth_bp.route('/logout', methods=['GET'])
def logout():
    token_service.termination(request.headers.get("Authorization"))
    return jsonify({"message": "Logout successful"}), 200 