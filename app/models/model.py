import cv2
import os
import numpy as np
from keras.preprocessing import image
import json
from tensorflow.keras.models import model_from_json,load_model
from app.models.database import Database

class Model():
    def __init__(self):
        pass
    def preprocess_image(self,img_path):
        img = image.load_img(img_path, target_size=(128, 128))
        img_array = image.img_to_array(img)
        img_tensor = np.expand_dims(img_array, axis=0)
        img_tensor = img_tensor.astype('float32') / 255 - 0.5
        return img_tensor

    def extract_frames(self,video_path, output_dir,file_id):
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
        obj = Database()
        #file_id = obj.get_file_id()
        #file_id=session['file_id']
        
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

    def predict_distracted_driver_on_video(self,video_path, output_dir,result_folder,file_id, threshold=0.5):
        global frames_list
        global cn
        self.extract_frames(video_path, output_dir,file_id)
        frame_predictions = []
        timestamps = []
        obj=Database()
        #file_id=obj.get_file_id()
        #file_id=session['file_id']
        with open('cnn.keras/config.json', 'r') as config_file:
            model_config = json.load(config_file)
        model = model_from_json(json.dumps(model_config))
        model.load_weights('cnn.keras/model.weights.h5')

        cn=0
        for frame_filename in os.listdir(output_dir):
            frame_path = os.path.join(output_dir, frame_filename)
            img_tensor = self.preprocess_image(frame_path)
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

        return cn

    def predict_distracted_driver_on_image(self,image_path, filename,file_id, threshold=0.5):
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
        img_tensor = self.preprocess_image(frame_path)
        prediction = model.predict(img_tensor)
        predicted_class_index = np.argmax(prediction, axis=1)[0]
        predicted_probability = prediction[0][predicted_class_index]

        if predicted_probability >= threshold:
            #timestamp = filename.split("_")[1].split(".")[0]
            predictions=predicted_class_index
            print(predictions)
            print(predicted_probability)
        
        return predictions

if __name__ == "__main__":
    # Example video path and output directory for frames
    image_path = "/home/lakshman/Downloads"
    filename = "0434.jpg"

    # Run prediction
    timestamps = predict_distracted_driver_on_image(image_path, filename)

    # Output the timestamps and predictions
    #for timestamp in timestamps:
    #    print(f"Frame {timestamp[0]}: Class Index {timestamp[1]}, Probability {timestamp[2]}")