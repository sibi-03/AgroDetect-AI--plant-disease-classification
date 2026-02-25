# 🌱 AgroDetect AI - Plant Disease Detection System

AgroDetect AI is a web-based plant disease detection system that uses deep learning to identify plant diseases from uploaded images. The system leverages transfer learning with MobileNetV2 to classify images into 38 disease categories and provides actionable treatment recommendations to help farmers and gardeners protect their plants.

## 🎯 Features

- **Fast & Accurate Detection**: Instant disease identification using state-of-the-art deep learning
- **38 Disease Categories**: Covers multiple crops including tomato, potato, corn, grape, apple, and more
- **Treatment Recommendations**: Get specific, actionable advice for each detected disease
- **Confidence Threshold**: Warns when predictions are below 80% confidence
- **User-Friendly Interface**: Clean, intuitive web interface with green-themed design
- **Mobile Responsive**: Works seamlessly on desktop, tablet, and mobile devices

## 🏆 For Hackathon Participants

### Quick Demo Setup

**For immediate testing with Python 3.7:**
```bash
pip install -r requirements_simple.txt
python app_simple.py
```

**For real AI predictions (requires Python 3.8+):**
```bash
pip install -r requirements.txt
python app.py
```

### 📸 Getting High Confidence Results (95%+)

1. **Use Test Images from Kaggle Dataset**
   - Download: https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset
   - These images guarantee high confidence!

2. **Best Disease Classes for Demo**:
   - ⭐ Tomato Late Blight (easiest, 95%+ confidence)
   - ⭐ Tomato Early Blight (distinctive target spots)
   - ⭐ Potato Late Blight (very recognizable)
   - ⭐ Apple Scab (unique scabby lesions)
   - ⭐ Healthy Tomato (always high confidence)

3. **Read Our Guides**:
   - 📋 **DISEASE_CLASSES_AND_IMAGES.md** - All 38 classes with image sources
   - 📸 **PHOTOGRAPHY_TIPS.md** - How to capture perfect plant photos
   - 🔧 **PYTHON37_SOLUTION.md** - Solutions for Python 3.7 users

### 🎓 Photography Tips for Best Results

- ✅ Use bright, natural daylight
- ✅ Ensure sharp focus on the leaf
- ✅ Fill 70-80% of frame with the leaf
- ✅ Use plain, neutral background
- ✅ Photograph top surface of leaf
- ✅ Capture clear disease symptoms

**See PHOTOGRAPHY_TIPS.md for complete guide!**

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Virtual environment (recommended)

### Installation

1. **Clone or download this repository**

```bash
cd AgroDetect_AI
```

2. **Create and activate a virtual environment** (recommended)

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

This will install:
- Flask (web framework)
- TensorFlow (deep learning)
- NumPy (numerical operations)
- Pillow (image processing)
- Werkzeug (utilities)

### Training the Model

**Important**: Before running the application, you need to train the model or download a pre-trained model.

#### Option 1: Train Your Own Model (Recommended for Google Colab)

1. Open `train_model.py` in Google Colab
2. Upload your Kaggle API credentials (kaggle.json)
3. Run the following commands in Colab:

```python
# Install Kaggle API
!pip install kaggle

# Upload kaggle.json and set permissions
!mkdir -p ~/.kaggle
!cp kaggle.json ~/.kaggle/
!chmod 600 ~/.kaggle/kaggle.json

# Download dataset
!kaggle datasets download -d vipoooool/new-plant-diseases-dataset
!unzip -q new-plant-diseases-dataset.zip

# Run training script
!python train_model.py
```

4. Download the generated files:
   - `plant_disease_model.h5` (trained model)
   - `class_names.json` (class mappings)

5. Place both files in the root directory of this project

#### Option 2: Manual Dataset Download

1. Visit [New Plant Diseases Dataset on Kaggle](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset)
2. Download and extract the dataset
3. Ensure you have `train/` and `valid/` directories
4. Run `python train_model.py` locally (requires significant computational resources)

**Training Details**:
- Architecture: MobileNetV2 with transfer learning
- Training time: 30-60 minutes on GPU (Google Colab)
- Expected accuracy: 92-96% on validation set
- Model size: ~14-20 MB

### Running the Application

Once you have the model files in place:

```bash
python app.py
```

The application will start on `http://localhost:5000`

Open your web browser and navigate to:
- Home page: `http://localhost:5000/`
- Upload page: `http://localhost:5000/upload`
- About page: `http://localhost:5000/about`

## 📁 Project Structure

```
AgroDetect_AI/
│
├── app.py                          # Main Flask application
├── train_model.py                  # Model training script
├── requirements.txt                # Python dependencies
├── README.md                       # This file
├── .gitignore                      # Git ignore rules
│
├── plant_disease_model.h5          # Trained model (generated)
├── class_names.json                # Class mappings (generated)
│
├── static/                         # Static assets
│   ├── style.css                   # Main stylesheet
│   └── uploads/                    # Uploaded images (created at runtime)
│
└── templates/                      # HTML templates
    ├── home.html                   # Landing page
    ├── about.html                  # About/technical info page
    ├── upload.html                 # Upload form page
    ├── result.html                 # Prediction results page
    └── error.html                  # Error page
```

## 🧠 How It Works: Transfer Learning Explained

**Transfer learning** is like teaching someone who already knows how to identify objects to specialize in plant diseases. Instead of starting from scratch, we use a model (MobileNetV2) that has already learned to recognize patterns in millions of images.

### The 1-Minute Pitch:

1. **Pre-trained Knowledge**: MobileNetV2 was trained on ImageNet (1.4M images, 1000 categories) and learned to detect edges, shapes, textures, and complex patterns.

2. **Adaptation**: We freeze these learned features and add custom layers on top to specialize in plant disease detection.

3. **Efficiency**: This approach requires:
   - Less training data (87K images vs millions)
   - Less training time (1 hour vs days/weeks)
   - Less computational power (can run on modest GPUs)

4. **High Accuracy**: Despite using less resources, we achieve 92-96% accuracy because the model already understands visual patterns.

### Technical Architecture:

```
Input Image (224x224x3)
        ↓
MobileNetV2 Base (frozen)
        ↓
Global Average Pooling
        ↓
Dropout (0.35)
        ↓
Dense Layer (256 units, ReLU)
        ↓
Dropout (0.25)
        ↓
Output Layer (38 units, Softmax)
        ↓
Disease Prediction + Confidence
```

## 🌿 Supported Plants & Diseases

The system can identify diseases in the following crops:

- **Apple**: Apple Scab, Black Rot, Cedar Apple Rust, Healthy
- **Blueberry**: Healthy
- **Cherry**: Powdery Mildew, Healthy
- **Corn**: Cercospora Leaf Spot, Common Rust, Northern Leaf Blight, Healthy
- **Grape**: Black Rot, Esca (Black Measles), Leaf Blight, Healthy
- **Orange**: Huanglongbing (Citrus Greening)
- **Peach**: Bacterial Spot, Healthy
- **Pepper**: Bacterial Spot, Healthy
- **Potato**: Early Blight, Late Blight, Healthy
- **Raspberry**: Healthy
- **Soybean**: Healthy
- **Squash**: Powdery Mildew
- **Strawberry**: Leaf Scorch, Healthy
- **Tomato**: Bacterial Spot, Early Blight, Late Blight, Leaf Mold, Septoria Leaf Spot, Spider Mites, Target Spot, Yellow Leaf Curl Virus, Mosaic Virus, Healthy

**Total**: 38 classes across 14 plant species

## 💡 Usage Tips

For best results when uploading images:

1. ✅ Use clear, well-lit photos
2. ✅ Focus on affected leaves or diseased areas
3. ✅ Avoid blurry or low-quality images
4. ✅ Capture close-up shots of symptoms
5. ✅ Supported formats: JPG, JPEG, PNG
6. ✅ Maximum file size: 16MB

## 🔧 Troubleshooting

### Model file not found error

**Error**: `Model file not found: plant_disease_model.h5`

**Solution**: You need to train the model first using `train_model.py` or download a pre-trained model. See the "Training the Model" section above.

### Import errors

**Error**: `ModuleNotFoundError: No module named 'tensorflow'`

**Solution**: Make sure you've installed all dependencies:
```bash
pip install -r requirements.txt
```

### Port already in use

**Error**: `Address already in use`

**Solution**: Either stop the process using port 5000, or change the port in `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # Change to 5001 or any available port
```

### Upload directory permissions

**Error**: `Unable to create upload directory`

**Solution**: Ensure the application has write permissions in the project directory. The `static/uploads/` directory will be created automatically.

## 🚀 Deployment

For production deployment:

1. **Disable debug mode** in `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=5000)
```

2. **Use a production WSGI server** (e.g., Gunicorn):
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

3. **Set up environment variables** for sensitive configuration

4. **Configure HTTPS** for secure file uploads

5. **Implement upload cleanup** to manage disk space

6. **Consider cloud storage** (AWS S3, Google Cloud Storage) for uploaded images

## 📊 Model Performance

- **Validation Accuracy**: 92-96%
- **Inference Time**: ~100-500ms on CPU, ~10-50ms on GPU
- **Model Size**: ~14-20 MB
- **Input Size**: 224x224 pixels
- **Training Dataset**: 87,000+ images

## 🤝 Contributing

Contributions are welcome! Areas for improvement:

- Add more plant species and diseases
- Implement batch image processing
- Add user authentication and history
- Create REST API for mobile apps
- Improve model accuracy with fine-tuning
- Add multi-language support

## 📝 License

This project is for educational and research purposes. The dataset is from Kaggle and subject to its terms of use.

## 🙏 Acknowledgments

- **Dataset**: [New Plant Diseases Dataset](https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset) on Kaggle
- **Model Architecture**: MobileNetV2 by Google
- **Framework**: TensorFlow and Keras
- **Web Framework**: Flask

## 📧 Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section above
2. Review the code comments in `app.py` and `train_model.py`
3. Ensure all dependencies are correctly installed

---

**Made with 🌱 for farmers and gardeners worldwide**

*Helping protect plants through the power of AI*
