import cv2
import os
import numpy as np
from keras.preprocessing import image
import json
from tensorflow.keras.models import model_from_json,load_model


def preprocess_image(img_path):
    img = image.load_img(img_path, target_size=(128, 128))
    img_array = image.img_to_array(img)
    img_tensor = np.expand_dims(img_array, axis=0)
    img_tensor = img_tensor.astype('float32') / 255 - 0.5
    return img_tensor

def extract_frames(video_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    cap = cv2.VideoCapture(video_path)
    frame_count = 0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break
        frame_filename = os.path.join(output_dir, f"frame_{frame_count:04d}.jpg")
        cv2.imwrite(frame_filename, frame)
        frame_count += 1

    cap.release()
    print(f"Extracted {frame_count} frames from {video_path}")

def predict_distracted_driver_on_video(video_path, output_dir, threshold=0.5):
    extract_frames(video_path, output_dir)
    frame_predictions = []
    timestamps = []

    for frame_filename in os.listdir(output_dir):
        frame_path = os.path.join(output_dir, frame_filename)
        img_tensor = preprocess_image(frame_path)
        prediction = model.predict(img_tensor)
        predicted_class_index = np.argmax(prediction, axis=1)[0]
        predicted_probability = prediction[0][predicted_class_index]

        if predicted_probability >= threshold:
            timestamp = frame_filename.split("_")[1].split(".")[0]
            timestamps.append((timestamp, predicted_class_index, predicted_probability))

    return timestamps

def predict_distracted_driver_on_image(image_path, filename, threshold=0.5):
    #extract_frames(video_path, output_dir)
    frame_predictions = []
    timestamps = []
    # Step 1: Load the model configuration from config.json
    with open('final_model/config.json', 'r') as config_file:
        model_config = json.load(config_file)

    # Step 2: Recreate the model from the configuration
    model = model_from_json(json.dumps(model_config))

    # Step 3: Load the model weights
    model.load_weights('final_model/model.weights.h5')

    #for frame_filename in os.listdir(output_dir):
    frame_path = os.path.join(image_path, filename)
    img_tensor = preprocess_image(frame_path)
    prediction = model.predict(img_tensor)
    predicted_class_index = np.argmax(prediction, axis=1)[0]
    predicted_probability = prediction[0][predicted_class_index]

    if predicted_probability >= threshold:
        #timestamp = filename.split("_")[1].split(".")[0]
        print(predicted_class_index, predicted_probability)

    return timestamps

# Example video path and output directory for frames
image_path = "/home/lakshman/Downloads"
filename = "0434.jpg"

# Run prediction
timestamps = predict_distracted_driver_on_image(image_path, filename)

# Output the timestamps and predictions
#for timestamp in timestamps:
#    print(f"Frame {timestamp[0]}: Class Index {timestamp[1]}, Probability {timestamp[2]}")