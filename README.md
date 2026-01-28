# 🚗 Distracted Driver Detection System

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)](https://www.python.org/)
[![TensorFlow](https://img.shields.io/badge/TensorFlow-2.x-orange.svg)](https://www.tensorflow.org/)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.x-green.svg)](https://opencv.org/)

> An end-to-end deep learning application for real-time detection of driver distraction behaviors using Convolutional Neural Networks (CNN).

## 📋 Table of Contents

- [Overview](#overview)
- [Problem Statement](#problem-statement)
- [Features](#features)
- [System Architecture](#system-architecture)
- [Dataset](#dataset)
- [Model Architecture](#model-architecture)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Technical Details](#technical-details)
- [Results](#results)
- [Future Enhancements](#future-enhancements)
- [Contributing](#contributing)
- [License](#license)

## 🎯 Overview

This project implements a complete machine learning pipeline that detects and classifies driver distraction behaviors from video footage. The system combines computer vision, deep learning, and web technologies to create a practical driver monitoring solution.

**Key Components:**
- 🧠 **Training Pipeline**: CNN model training on labeled driver behavior images
- ⚙️ **Backend System**: Video processing and real-time inference engine
- 🌐 **Frontend Interface**: Interactive visualization and user interface

## 🚨 Problem Statement

Distracted driving is a leading cause of road accidents worldwide. This system aims to automatically identify risky driver behaviors using camera footage captured from inside a vehicle, enabling:

- Real-time driver monitoring
- Accident prevention through early warning systems
- Fleet management and safety analytics
- Insurance risk assessment

## ✨ Features

- **Multi-class Classification**: Detects 10 different driver behaviors
- **Frame-by-Frame Analysis**: Processes video streams efficiently
- **Temporal Consistency**: Aggregates predictions to reduce noise
- **Real-time Inference**: Optimized for near real-time performance
- **User-Friendly Interface**: Intuitive frontend for video upload and visualization
- **Scalable Architecture**: Designed for deployment in production environments

## 🏗️ System Architecture

```
┌─────────────────┐
│  Video Upload   │
└────────┬────────┘
         │
         ▼
┌─────────────────────────┐
│  OpenCV Frame Extraction│
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Frame Preprocessing    │
│  (Resize + Normalize)   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  CNN Model Inference    │
│  (10-class prediction)  │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Prediction Aggregation │
│  (Temporal Smoothing)   │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Backend Response       │
└────────┬────────────────┘
         │
         ▼
┌─────────────────────────┐
│  Frontend Visualization │
└─────────────────────────┘
```

## 📊 Dataset

**Source**: [State Farm Distracted Driver Detection Dataset](https://www.kaggle.com/c/state-farm-distracted-driver-detection) (Kaggle)

**Data Characteristics:**
- Dashboard-mounted camera images
- 10 predefined driver behavior classes
- Labeled images for supervised learning

**Classes:**
1. **c0**: Safe driving
2. **c1**: Texting (right hand)
3. **c2**: Talking on phone (right hand)
4. **c3**: Texting (left hand)
5. **c4**: Talking on phone (left hand)
6. **c5**: Operating radio
7. **c6**: Drinking
8. **c7**: Reaching behind
9. **c8**: Hair and makeup
10. **c9**: Talking to passenger

## 🧠 Model Architecture

**Type**: Convolutional Neural Network (CNN)

**Architecture Components:**

```
Input Layer (224x224x3)
    ↓
Conv2D + ReLU
    ↓
MaxPooling2D
    ↓
Conv2D + ReLU
    ↓
MaxPooling2D
    ↓
Conv2D + ReLU
    ↓
MaxPooling2D
    ↓
Flatten
    ↓
Dense (Fully Connected)
    ↓
Dropout
    ↓
Dense (Fully Connected)
    ↓
Softmax (10 classes)
```

**Training Configuration:**
- **Loss Function**: Categorical Cross-Entropy
- **Optimizer**: Adam
- **Metrics**: Accuracy
- **Validation Split**: 80/20 train-validation split

**Key Features Learned:**
- Hand position and gestures
- Head orientation
- Arm movement patterns
- Object interaction (phone, radio, etc.)

## 🛠️ Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager
- Virtual environment (recommended)

### Setup Instructions

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/distracted-driver-detection.git
cd distracted-driver-detection
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Download dataset**
```bash
# Download from Kaggle using kaggle CLI
kaggle competitions download -c state-farm-distracted-driver-detection
unzip state-farm-distracted-driver-detection.zip -d data/
```

5. **Download pre-trained model** (if available)
```bash
# Place model file in models/ directory
# Or train from scratch using the training script
```

## 🚀 Usage

### Training the Model

```bash
python train.py --data_dir data/train --epochs 50 --batch_size 32
```

**Arguments:**
- `--data_dir`: Path to training data directory
- `--epochs`: Number of training epochs (default: 50)
- `--batch_size`: Batch size for training (default: 32)
- `--learning_rate`: Learning rate for optimizer (default: 0.001)
- `--save_path`: Path to save trained model (default: models/model.h5)

### Running Inference (Backend)

```bash
python inference.py --video_path path/to/video.mp4 --model_path models/model.h5
```

**Arguments:**
- `--video_path`: Path to input video file
- `--model_path`: Path to trained model
- `--frame_skip`: Number of frames to skip (default: 5)
- `--output_path`: Path to save results (optional)

### Starting the Frontend

```bash
cd frontend
npm install
npm start
```

The application will be available at `http://localhost:3000`

### Running the Full Application

```bash
# Terminal 1 - Start backend server
python app.py

# Terminal 2 - Start frontend
cd frontend && npm start
```

## 📁 Project Structure

```
distracted-driver-detection/
│
├── data/
│   ├── train/              # Training images
│   ├── test/               # Test images
│   └── validation/         # Validation images
│
├── models/
│   ├── model.h5            # Trained model weights
│   └── model_architecture.json
│
├── backend/
│   ├── train.py            # Model training script
│   ├── inference.py        # Video inference engine
│   ├── preprocess.py       # Preprocessing utilities
│   ├── model.py            # Model architecture definition
│   └── app.py              # Backend API server
│
├── frontend/
│   ├── src/
│   │   ├── components/     # React components
│   │   ├── utils/          # Utility functions
│   │   └── App.js          # Main application
│   ├── public/
│   └── package.json
│
├── notebooks/
│   ├── exploratory_analysis.ipynb
│   └── model_evaluation.ipynb
│
├── requirements.txt
├── README.md
└── LICENSE
```

## 🔧 Technical Details

### Video Processing Pipeline

**Why Frame-by-Frame Analysis?**
- CNNs are inherently image-based models
- Frame sampling reduces computational overhead
- Enables near real-time processing
- Scalable for live camera feeds

**Frame Sampling Strategy:**
```python
# Process every Nth frame to balance performance and accuracy
frame_skip = 5  # Process 1 out of every 5 frames
```

### Inference Optimization

1. **Batch Processing**: Multiple frames processed simultaneously
2. **Frame Sampling**: Selective frame analysis to reduce latency
3. **Temporal Aggregation**: Smoothing predictions across time
4. **GPU Acceleration**: Leverages CUDA for faster inference

### Preprocessing Pipeline

```python
def preprocess_frame(frame):
    # Resize to model input size
    frame = cv2.resize(frame, (224, 224))
    
    # Normalize pixel values
    frame = frame.astype('float32') / 255.0
    
    # Expand dimensions for batch processing
    frame = np.expand_dims(frame, axis=0)
    
    return frame
```

### Temporal Consistency

```python
def aggregate_predictions(predictions, window_size=10):
    """
    Aggregate predictions over a sliding window
    to reduce noisy/flickering predictions
    """
    return mode(predictions[-window_size:])
```

## 📈 Results

### Model Performance

- **Training Accuracy**: ~95%
- **Validation Accuracy**: ~93%
- **Inference Speed**: ~30 FPS (with frame skip = 5)
- **Model Size**: ~50 MB

### Confusion Matrix Insights

- High accuracy on "safe driving" and "texting" classes
- Some confusion between similar hand positions
- Excellent generalization across different drivers

## 🚀 Future Enhancements

- [ ] Implement LSTM for temporal sequence modeling
- [ ] Add multi-person detection in vehicle
- [ ] Deploy model to edge devices (Raspberry Pi, Jetson Nano)
- [ ] Integrate with IoT alert systems
- [ ] Add driver fatigue detection
- [ ] Implement model quantization for faster inference
- [ ] Create mobile application (iOS/Android)
- [ ] Add voice/audio alerts for real-time monitoring

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- State Farm for providing the dataset
- Kaggle for hosting the competition
- TensorFlow and OpenCV communities
- All contributors and supporters

---

⭐ If you find this project helpful, please consider giving it a star!

**Built with ❤️ for safer roads**
