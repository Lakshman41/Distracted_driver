import os
from flask import Flask, request, jsonify, send_file,session
from werkzeug.utils import secure_filename
from database import database
from app.services.tokens import Tokens
import cv2
import numpy as np
import io
from flask_cors import CORS
from keras.preprocessing import image
import json
from tensorflow.keras.models import model_from_json,load_model
#from flask_ngrok import run_with_ngrok
from dotenv import load_dotenv
import stat
from model import Model

load_dotenv()

app = Flask(__name__)
#run_with_ngrok(app)
app.secret_key=os.getenv("SECRET_KEY")

app.config['SESSION_COOKIE_SECURE'] = True  # If using HTTPS
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# Apply CORS to all routes
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

UPLOAD_FOLDER = 'uploads/'
#user_id=-1
app.config['UPLOAD_FOLDER'] = os.path.abspath(UPLOAD_FOLDER)  # Use absolute path

users_list=[]
frames_list={}
permission=0
cn=0

ALLOWED_EXTENSIONS_V = {'mp4', 'mov', 'avi', 'mkv'}
ALLOWED_EXTENSIONS_I = {'jpeg', 'png', 'jpg'}
main_file_path = None  # Store the file path of the uploaded file

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file_V(filename_v):
    return '.' in filename_v and filename_v.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_V

def allowed_file_I(filename_i):
    return '.' in filename_i and filename_i.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_I


@app.route('/login', methods=['POST'])
def login():
    global users_list
    #global user_id
    global permission
    data=request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400
    required_keys_u = ['username']
    required_keys_e = ['email']

    valid_keys_u=[key for key in required_keys_u if key in data]
    valid_keys_e=[key for key in required_keys_e if key in data]

    if valid_keys_u:
        obj=database()
        result=obj.data_username(data['username'])
        #obj.set_id(result['id'])
        session['id']=result['id']
        objc=Tokens()
        tk=objc.generate_tokens(result['id'])
        result.update(tk)
        return jsonify(result),200

    elif valid_keys_e:
        obj=database()
        result=obj.data_email_id(data['email'])
        #obj.set_id(result['id'])
        objc=Tokens()
        tk=objc.generate_tokens(result['id'])
        result.update(tk)
        return jsonify(result),200

    else:
        return jsonify({"message": "Credentials provided are not matching"}), 400
    
@app.route('/register', methods=['POST'])
def register():
    global users_list
    global permission
    data=request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400
    required_keys = ['username','email_id']

    valid_keys=[key for key in required_keys if key in data]
    if valid_keys:
        obj=database()
        result=obj.insert(data['username'],data['email_id'])
        #obj.set_id(result)
        session['id']=result
        objc=Tokens()
        tk=objc.generate_tokens(result)
        #result.update(tk)
        return jsonify({"message":"User registered Succesfully","token":tk['token']})
        # for records in users_list:
        #     if(records.username==data['username']):
        #         return jsonify({"message": "username already exists"}), 400
        #     elif(records.email_id==data['email_id']):
        #         return jsonify({"message": "email_id is already registered"}), 400

        # temp_obj=users(data['username'],data['email_id'],data['password'])
        # temp_obj.insertion()
        # users_list.append(temp_obj)
        # permission=1
        # return jsonify({"message": "Registered Succesfully"}), 200   

@app.route('/google', methods=['POST'])
def google():
    data = request.json
    if not data or 'email' not in data:
        return jsonify({"message": "No data provided"}), 400
    
    try:
        obj = database()
        result = obj.data_email_id(data['email'])
        
        if result['message'] == 'Data Found':
            # Store user info in session
            session['id'] = result['id']
            objc=Tokens()
            tk=objc.generate_tokens(result['id'])
            result.update(tk)
            print(result)
            session.modified = True  # Ensure session is saved
            
            return jsonify({
                'message': 'Exist',
                'username': result['username'],
                'id': result['id'],  # Send ID back to client
                'token': result['token']
            }), 200
        else:
            # Handle new user case if needed
            # obj.insert(data['username'], data['email'])
            return jsonify({'message': 'Not exist'}), 200
            
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        return jsonify({"message": "Authentication failed"}), 500
    
@app.route('/test-session', methods=['GET'])
def test_session():
    return jsonify({
        "message": 'working',
    })

@app.route('/upload', methods=['POST'])
def upload_files():
    objc=Tokens()
    fl=objc.validation(request.headers.get("Authorization"))
    print(fl)
    user_id=""
    file_id=""
    if (fl['message']=='session found'):
        user_id=fl['data']['id']
        file_id=fl['data']['file_id']
    else:
        return jsonify(fl)
    global main_file_path
    global cn
    
    # Check if user is logged in
    
    #user_id = session['id']
    
    # Check if file exists in request
    if 'video' in request.files:
        file = request.files['video']
        file_type = "video"
    elif 'image' in request.files:
        file = request.files['image']
        file_type = "image"
    else:
        return jsonify({"message": "No file part"}), 400
    
    # Check if filename is empty
    if file.filename == '':
        return jsonify({"message": "No selected file"}), 400
    
    filename = secure_filename(file.filename)
    obj = database()
    #obj.set_id(user_id)  # Set the user_id in database object
    
    try:
        # Handle video upload
        if file_type == "video" and allowed_file_V(file.filename):
            video_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
            os.makedirs(video_folder, exist_ok=True)
            
            # Read file content before saving
            file_content = file.read()
            
            # Save original file
            main_file_path = os.path.join(video_folder, filename)
            with open(main_file_path, 'wb') as f:
                f.write(file_content)
            
            # Insert file record and get file_id
            file_id = obj.file_insert(user_id, "video", filename, video_folder)
            objc.set_file_id(request.headers.get("Authorization"),file_id)
            # session['file_id'] = file_id
            
            # Create necessary folders
            frames_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'frames')
            video_frames_folder = os.path.join(frames_folder, filename)
            result_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'result')
            
            os.makedirs(frames_folder, exist_ok=True)
            os.makedirs(video_frames_folder, exist_ok=True)
            os.makedirs(result_folder, exist_ok=True)
            
            models=Model()
            count = models.predict_distracted_driver_on_video(main_file_path, video_frames_folder, result_folder,file_id)
            
            return jsonify({"message": f"Video file {filename} uploaded successfully!", "count": count}), 200
        
        # Handle image upload
        elif file_type == "image" and allowed_file_I(file.filename):
            image_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'images')
            os.makedirs(image_folder, exist_ok=True)
            
            # Read file content before saving
            file_content = file.read()
            
            # Save original file
            main_file_path = os.path.join(image_folder, filename)
            with open(main_file_path, 'wb') as f:
                f.write(file_content)
            
            # Insert file record and get file_id
            file_id = obj.file_insert(user_id, "image", filename, image_folder)
            objc.set_file_id(request.headers.get("Authorization"),file_id)
            #session['file_id'] = file_id
            
            # Process image and get results
            models=Model()
            results = models.predict_distracted_driver_on_image(image_folder, filename,file_id)
            
            # Create result folder
            result_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'result')
            os.makedirs(result_folder, exist_ok=True)
            
            # Determine distraction status
            print(results)
            if results == 0:
                status = "Undistracted"
            elif 1 <= results <= 10:
                status = "Distracted"
            else:
                #print(results)
                return jsonify({"message": "Model prediction failed"}), 500
            
            # Insert result record
            result_id = obj.result_insert(file_id, filename, result_folder, status, results)
            
            # Save copy in result folder
            result_subfolder = os.path.join(result_folder, str(results))
            os.makedirs(result_subfolder, exist_ok=True)
            
            result_file_path = os.path.join(result_subfolder, filename)
            with open(result_file_path, 'wb') as f:
                f.write(file_content)
            
            return jsonify({"message": f"Image file {filename} uploaded successfully!", "count": 1}), 200
        
        else:
            return jsonify({"message": "File type not allowed"}), 400
            
    except Exception as e:
        # Log the error for debugging
        print(f"Error during file upload: {str(e)}")
        return jsonify({"message": "An error occurred during file upload"}), 500
    
@app.route('/user-files',methods=['GET'])
def user_files():
    objc=Tokens()
    fl=objc.validation(request.headers.get("Authorization"))
    user_id=""
    file_id=""
    if (fl['message']=='session found'):
        user_id=fl['data']['id']
        file_id=fl['data']['file_id']
    else:
        return jsonify(fl)
    obj=database()
    


@app.route('/send_data/<int:no>', methods=['GET'])
def send_data(no):
    global main_file_path
    objc=Tokens()
    fl=objc.validation(request.headers.get("Authorization"))
    user_id=""
    file_id=""
    if (fl['message']=='session found'):
        user_id=fl['data']['id']
        file_id=fl['data']['file_id']
    else:
        return jsonify(fl)
    if main_file_path is None:
        return jsonify({"message": "No file uploaded yet"}), 400

    #print(f"Attempting to send file from: {main_file_path}")  # Debugging line

    # Serve the file using send_file with the absolute file path
    obj=database()
    #id=session['file_id']
    data=obj.result_get(file_id)
    return jsonify({'result':data[no]['result'],'category':data[no]['category']})

@app.route('/send_file/<int:no>', methods=['GET'])
def send_file_db(no):
    objc=Tokens()
    fl=objc.validation(request.headers.get("Authorization"))
    user_id=""
    file_id=""
    if (fl['message']=='session found'):
        user_id=fl['data']['id']
        file_id=fl['data']['file_id']
    else:
        return jsonify(fl)
    #if isinstance(no,int)==False:
    #   raise Exception("Error")
    global main_file_path

    if main_file_path is None:
        return jsonify({"message": "No file uploaded yet"}), 400

    # Serve the file using send_file with the absolute file path
    obj=database()
    #id=obj.get_file_id()
    #id=session['file_id']
    print(type(no))
    data=obj.result_get(file_id)
    #no=int(no)
    print(data[no]['path'])
    print(str(data[no]['category']))
    path=os.path.join(data[no]['path'],data[no]['category'])
    path=os.path.join(path,data[no]['name'])
    print(f"Attempting to send file from: {path}")
    return send_file(path), 200

@app.route('/logout', methods=['GET'])
def logout():
    objc=Tokens()
    fl=objc.validation(request.headers.get("Authorization"))
    user_id=""
    file_id=""
    if (fl['message']=='session found'):
        user_id=fl['data']['id']
        file_id=fl['data']['file_id']
    else:
        return jsonify(fl)
    objc.termination(request.headers.get("Authorization"))
    #objc=database()
    #obj.set_id(-1)
    #session.pop('id', None)
    #obj.set_file_id(-1)
    #session.pop('file_id', None)
    return jsonify({"message":"Logout sucessfull"})

if __name__ == '__main__':
    app.run(debug=True)