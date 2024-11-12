import os
from flask import Flask, request, jsonify, send_file
from werkzeug.utils import secure_filename
from users import users
from backup import Backup
from database import database
import cv2
import numpy as np
import io
from flask_cors import CORS
from keras.preprocessing import image
import json
from tensorflow.keras.models import model_from_json,load_model

app = Flask(__name__)

CORS(app)

cors_config = {
    "origins": [
        "http://localhost:3000",  # React development server
        "http://127.0.0.1:3000",  # Alternative React development URL
        # Add your production URLs here
        # "https://yourdomain.com"
    ],
    "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    "allow_headers": ["Content-Type", "Authorization"],
    "expose_headers": ["Content-Range", "X-Content-Range"],
    "supports_credentials": True,  # Enable if you need to send cookies
    "max_age": 600,  # Cache preflight requests for 10 minutes
}

CORS(app, resources={
    r"/*": cors_config  # Apply to all routes
})

UPLOAD_FOLDER = 'uploads/'
#user_id=-1
app.config['UPLOAD_FOLDER'] = os.path.abspath(UPLOAD_FOLDER)  # Use absolute path

users_list=[]
frames_list={}
permission=0
cn=0

temp_obj=Backup()
users_list=temp_obj.show()

ALLOWED_EXTENSIONS_V = {'mp4', 'mov', 'avi', 'mkv'}
ALLOWED_EXTENSIONS_I = {'jpeg', 'png', 'jpg'}
main_file_path = None  # Store the file path of the uploaded file

if not os.path.exists(app.config['UPLOAD_FOLDER']):
    os.makedirs(app.config['UPLOAD_FOLDER'])

def allowed_file_V(filename_v):
    return '.' in filename_v and filename_v.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_V

def allowed_file_I(filename_i):
    return '.' in filename_i and filename_i.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_I

def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_tensor = np.expand_dims(img_array, axis=0)
    img_tensor = img_tensor.astype('float32') / 255 - 0.5
    return img_tensor

def extract_frames(video_path, output_dir):
    global frames_list
    frames_list = {}  # Reset frames list
    os.makedirs(output_dir, exist_ok=True)
    
    # Open the video file
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Could not open video file")
        return
    
    # Get video properties
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_interval = int(fps)  # Number of frames to skip to get 1-second intervals
    
    frame_count = 0
    saved_count = 0
    obj = database()
    file_id = obj.get_file_id()
    
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
            
        # Process frame only at 1-second intervals
        if frame_count % frame_interval == 0:
            # Generate frame name
            name = f"frame_{saved_count:04d}.jpg"
            frame_filename = os.path.join(output_dir, name)
            
            # Save the frame using cv2.imwrite
            success = cv2.imwrite(frame_filename, frame)
            
            if success:
                frames_list[name] = frame
                obj.frame_insert(file_id, name, output_dir)
                saved_count += 1
                
        frame_count += 1
    
    cap.release()
    print(f"Extracted {saved_count} frames at 1-second intervals from {video_path}")

def predict_distracted_driver_on_video(video_path, output_dir,result_folder, threshold=0.5):
    global frames_list
    global cn
    extract_frames(video_path, output_dir)
    frame_predictions = []
    timestamps = []
    obj=database()
    file_id=obj.get_file_id()
    with open('cnn.keras/config.json', 'r') as config_file:
        model_config = json.load(config_file)
    model = model_from_json(json.dumps(model_config))
    model.load_weights('cnn.keras/model.weights.h5')

    cn=0
    for frame_filename in os.listdir(output_dir):
        frame_path = os.path.join(output_dir, frame_filename)
        img_tensor = preprocess_image(frame_path)
        prediction = model.predict(img_tensor)
        predicted_class_index = np.argmax(prediction, axis=1)[0]
        predicted_probability = prediction[0][predicted_class_index]

        if predicted_probability >= threshold:
            timestamp = frame_filename.split("_")[1].split(".")[0]
            timestamps.append((timestamp, predicted_class_index, predicted_probability))
            result_folder_temp=os.path.join(result_folder,str(predicted_class_index))
            if not os.path.exists(result_folder_temp):
                os.makedirs(result_folder_temp)
            result_file_path=os.path.join(result_folder_temp,frame_filename)
            cv2.imwrite(result_file_path, frames_list[frame_filename])
            #with open(result_file_path, 'wb') as f:
            #    f.write(frames_list[frame_filename])
            result=None
            if predicted_class_index==0:
                result="Distracted"
                cn+=1
            elif predicted_class_index>=1 and predicted_class_index<=10:
                result="Undistracted"
            obj.result_insert(file_id,frame_filename,result_folder,result,predicted_class_index)

    return timestamps

def predict_distracted_driver_on_image(image_path, filename, threshold=0.5):
    #extract_frames(video_path, output_dir)
    predictions=-1
    # Step 1: Load the model configuration from config.json
    with open('cnn.keras/config.json', 'r') as config_file:
        model_config = json.load(config_file)

    # Step 2: Recreate the model from the configuration
    model = model_from_json(json.dumps(model_config))

    # Step 3: Load the model weights
    model.load_weights('cnn.keras/model.weights.h5')

    #for frame_filename in os.listdir(output_dir):
    frame_path = os.path.join(image_path, filename)
    img_tensor = preprocess_image(frame_path)
    prediction = model.predict(img_tensor)
    predicted_class_index = np.argmax(prediction, axis=1)[0]
    predicted_probability = prediction[0][predicted_class_index]

    if predicted_probability >= threshold:
        #timestamp = filename.split("_")[1].split(".")[0]
        predictions=predicted_class_index
        print(predictions)
        print(predicted_probability)
    
    return predictions


if True:
    @app.route('/upload', methods=['POST'])
    def upload_files():
        global main_file_path
        global cn
        
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
        user_id = obj.get_id()
        
        # Handle video upload
        if file_type == "video" and allowed_file_V(file.filename):
            video_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
            if not os.path.exists(video_folder):
                os.makedirs(video_folder)
                
             # Read file content before saving
            file_content = file.read()
            
            # Create a BytesIO object to save the content
            file_copy = io.BytesIO(file_content)
            file_copy.filename = filename
            file_copy.name = filename
            
            # Save original file
            main_file_path = os.path.join(video_folder, filename)
            with open(main_file_path, 'wb') as f:
                f.write(file_content)
                
            # Insert file record and get file_id
            file_id = obj.file_insert(user_id, "video", filename, video_folder)
            obj.set_file_id(file_id)
            
            print(f"File saved at: {main_file_path}")

            frames_folder=os.path.join(app.config['UPLOAD_FOLDER'], 'frames')
            if not os.path.exists(frames_folder):
                os.makedirs(frames_folder)
            video_frames_folder=os.path.join(frames_folder, filename)
            if not os.path.exists(video_frames_folder):
                os.makedirs(video_frames_folder)
            result_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'result')
            if not os.path.exists(result_folder):
                os.makedirs(result_folder)
            predictions=predict_distracted_driver_on_video(main_file_path,video_frames_folder,result_folder)
            
            return jsonify({"message": f"Video file {filename} uploaded successfully!","count":cn}), 200
        
        # Handle image upload
        elif file_type == "image" and allowed_file_I(file.filename):
            # Save original file
            image_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'images')
            if not os.path.exists(image_folder):
                os.makedirs(image_folder)
                
            # Read file content before saving
            file_content = file.read()
            
            # Create a BytesIO object to save the content
            file_copy = io.BytesIO(file_content)
            file_copy.filename = filename
            file_copy.name = filename
            
            # Save original file
            main_file_path = os.path.join(image_folder, filename)
            with open(main_file_path, 'wb') as f:
                f.write(file_content)
                
            # Insert file record and get file_id
            file_id = obj.file_insert(user_id, "image", filename, image_folder)
            obj.set_file_id(file_id)
            
            print(f"File saved at: {main_file_path}")
            
            # Process image and get results
            results = predict_distracted_driver_on_image(image_folder, filename)
            
            # Create result folder
            result_folder = os.path.join(app.config['UPLOAD_FOLDER'], 'result')
            if not os.path.exists(result_folder):
                os.makedirs(result_folder)
                
            # Determine distraction status
            if results == 0:
                status = "Undistracted"
            elif 1 <= results <= 9:
                status = "Distracted"
            else:
                return jsonify({"message": "Model didnt work"}), 400
                
            # Insert result record
            result_id = obj.result_insert(file_id, filename, result_folder, status, results)
            
            # Save copy in result folder
            result_subfolder = os.path.join(result_folder, str(results))
            if not os.path.exists(result_subfolder):
                os.makedirs(result_subfolder)
                
            result_file_path = os.path.join(result_subfolder, filename)
            with open(result_file_path, 'wb') as f:
                f.write(file_content)
                
            return jsonify({"message": f"Image file {filename} uploaded successfully!", "count": 1}), 200
        
        else:
            return jsonify({"message": "File type not allowed"}), 400

    @app.route('/send_data/<int:no>', methods=['GET'])
    def send_data(no):
        global main_file_path

        if main_file_path is None:
            return jsonify({"message": "No file uploaded yet"}), 400

        #print(f"Attempting to send file from: {main_file_path}")  # Debugging line

        # Serve the file using send_file with the absolute file path
        obj=database()
        id=obj.get_file_id()
        data=obj.result_get(id)
        return jsonify({'result':data[no]['result'],'category':data[no]['category']})
    
    @app.route('/send_file/<int:no>', methods=['GET'])
    def send_file_db(no):
        #if isinstance(no,int)==False:
        #   raise Exception("Error")
        global main_file_path

        if main_file_path is None:
            return jsonify({"message": "No file uploaded yet"}), 400

        # Serve the file using send_file with the absolute file path
        obj=database()
        id=obj.get_file_id()
        print(type(no))
        data=obj.result_get(id)
        #no=int(no)
        print(data[no]['path'])
        print(str(data[no]['category']))
        path=os.path.join(data[no]['path'],data[no]['category'])
        path=os.path.join(path,data[no]['name'])
        print(f"Attempting to send file from: {path}")
        return send_file(path), 200

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
        obj.set_id(result['id'])
        return jsonify(result),200

    elif valid_keys_e:
        obj=database()
        result=obj.data_email_id(data['email'])
        obj.set_id(result['id'])
        return jsonify(result),200

    else:
        return jsonify({"message": "Files provided are not matching"}), 400
    
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
        res=obj.data_username(data['username'])
        if(res['message']=='Data Found'):
            return jsonify({"message":"User Already Exists"}),400
        else:
            result=obj.insert(data['username'],data['email_id'])
            obj.set_id(result)
            return jsonify({"message":"User registered Succesfully"})
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

@app.route('/google',methods=['POST'])
def google():
    data=request.json
    if not data:
        return jsonify({"message": "No data provided"}), 400
    
    # print(data)
    obj=database()
    result=obj.data_email_id(data['email'])
    print(result)
    if(result['message']=='Data Found'):
        obj.set_id(result['id'])
        return jsonify({'message':'Exist','username':result['username']}),200
    else:
        # obj.insert(data['username'],data['email_id'])
        return jsonify({'message':'Not exist'}),200

@app.route('/logout', methods=['GET'])
def logout():
    obj=database()
    obj.set_id(-1)
    obj.set_file_id(-1)
    return jsonify({"message":"Logout sucessfull"})

if __name__ == '__main__':
    app.run(debug=True)