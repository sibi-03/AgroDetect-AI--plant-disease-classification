"""
AgroDetect AI - Production Flask Application
Real AI predictions using Hugging Face Inference API
Works with Python 3.7+ (no local model installation required)
"""

import os
import time
import requests
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from werkzeug.utils import secure_filename
from PIL import Image
import base64
from io import BytesIO

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'agrodetect-ai-secret-key-change-in-production'

# Configuration
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
CONFIDENCE_THRESHOLD = 80.0

# Hugging Face API Configuration
HF_API_URL = "https://api-inference.huggingface.co/models/nateraw/plant-disease"
HF_API_TOKEN = "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"  # Your Hugging Face token
HF_HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

# Supported crops
SUPPORTED_CROPS = [
    "Tomato", "Potato", "Apple", "Corn/Maize", "Grape", 
    "Cherry", "Peach", "Pepper", "Strawberry", "Squash",
    "Orange", "Blueberry", "Raspberry", "Soybean"
]

# Create uploads directory
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"✓ Created upload directory: {UPLOAD_FOLDER}")


def allowed_file(filename):
    """Check if file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    """Save uploaded file with timestamp."""
    filename = secure_filename(file.filename)
    timestamp = str(int(time.time()))
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    return filepath


def predict_disease_api(image_path):
    """
    Predict disease using Hugging Face Inference API.
    This works with Python 3.7 and doesn't require local model installation.
    """
    try:
        # Read and prepare image
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Try new API endpoint first
        response = requests.post(
            "https://api-inference.huggingface.co/models/nateraw/plant-disease",
            headers=HF_HEADERS,
            data=image_data,
            timeout=30
        )
        
        if response.status_code == 200:
            results = response.json()
            
            if results and len(results) > 0:
                top_prediction = results[0]
                disease_name = top_prediction['label']
                confidence = top_prediction['score'] * 100
                return disease_name, confidence
            else:
                raise Exception("No predictions returned from API")
        else:
            error_msg = f"API Error {response.status_code}: {response.text[:200]}"
            print(error_msg)
            raise Exception(error_msg)
            
    except requests.exceptions.Timeout:
        raise Exception("API request timed out. The model may be loading. Please try again in 20 seconds.")
    except requests.exceptions.RequestException as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        print(f"API Prediction Error: {str(e)}")
        raise


# Treatment recommendations
treatment_recommendations = {
    "Apple___Apple_scab": "Remove and destroy infected leaves. Apply fungicide containing captan or sulfur. Ensure good air circulation by pruning. Avoid overhead watering.",
    "Apple___Black_rot": "Prune infected branches at least 6 inches below visible damage. Apply copper-based fungicide. Remove mummified fruits. Maintain tree health through proper fertilization.",
    "Apple___Cedar_apple_rust": "Remove nearby cedar trees if possible. Apply fungicide with myclobutanil. Prune to improve air circulation. Plant resistant apple varieties.",
    "Apple___healthy": "Your apple plant appears healthy! Continue regular care: water deeply but infrequently, fertilize in spring, prune annually, and monitor for pests.",
    "Blueberry___healthy": "Your blueberry plant looks great! Maintain acidic soil (pH 4.5-5.5), mulch with pine needles, water regularly, and prune old canes annually.",
    "Cherry_(including_sour)___Powdery_mildew": "Apply sulfur or potassium bicarbonate fungicide. Prune to improve air circulation. Remove infected leaves. Water at soil level, not on foliage.",
    "Cherry_(including_sour)___healthy": "Your cherry plant is healthy! Continue proper care: deep watering, annual pruning, bird netting for fruit protection, and pest monitoring.",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot": "Apply fungicide containing azoxystrobin. Practice crop rotation. Remove infected plant debris. Plant resistant varieties. Ensure proper spacing for air circulation.",
    "Corn_(maize)___Common_rust_": "Apply fungicide if severe. Plant resistant hybrids. Remove infected leaves. Ensure adequate plant nutrition. Monitor regularly during humid weather.",
    "Corn_(maize)___Northern_Leaf_Blight": "Use fungicide with active ingredients like propiconazole. Practice 2-year crop rotation. Till under crop residue. Plant resistant varieties. Avoid overhead irrigation.",
    "Corn_(maize)___healthy": "Your corn looks healthy! Continue care: adequate watering (1 inch per week), side-dress with nitrogen fertilizer, control weeds, and watch for pests.",
    "Grape___Black_rot": "Remove and destroy infected fruit and leaves. Apply fungicide (mancozeb or captan) preventively. Prune for air circulation. Remove mummified berries.",
    "Grape___Esca_(Black_Measles)": "Prune out infected wood during dormancy. Apply wound protectants after pruning. No cure exists; focus on prevention. Consider replanting severely affected vines.",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)": "Apply copper-based fungicide. Remove infected leaves. Improve air circulation through pruning. Avoid overhead watering. Ensure proper vine spacing.",
    "Grape___healthy": "Your grapevine is healthy! Maintain care: annual pruning, adequate water, balanced fertilization, and good air circulation to prevent diseases.",
    "Orange___Haunglongbing_(Citrus_greening)": "No cure available. Remove and destroy infected trees to prevent spread. Control psyllid insects with insecticides. Plant disease-free certified nursery stock.",
    "Peach___Bacterial_spot": "Apply copper-based bactericide. Prune to improve air circulation. Avoid overhead irrigation. Plant resistant varieties. Remove severely infected leaves.",
    "Peach___healthy": "Your peach tree is healthy! Continue care: annual pruning, thinning fruit for better size, adequate watering, and spring fertilization.",
    "Pepper,_bell___Bacterial_spot": "Apply copper-based bactericide. Remove infected leaves. Practice crop rotation (3 years). Use disease-free seeds. Avoid overhead watering.",
    "Pepper,_bell___healthy": "Your pepper plant looks great! Continue care: consistent watering, balanced fertilizer, support stakes if needed, and regular harvesting.",
    "Potato___Early_blight": "Apply fungicide containing chlorothalonil or mancozeb. Remove infected leaves. Practice crop rotation. Mulch to prevent soil splash. Ensure adequate spacing.",
    "Potato___Late_blight": "Remove and destroy infected plants immediately. Apply fungicide with active ingredients like chlorothalonil. Avoid overhead watering. Plant certified disease-free seed potatoes.",
    "Potato___healthy": "Your potato plant is healthy! Continue care: hill soil around stems, water consistently, fertilize at planting, and harvest when foliage dies back.",
    "Raspberry___healthy": "Your raspberry plant looks excellent! Maintain care: annual pruning of old canes, mulching, consistent watering, and trellis support.",
    "Soybean___healthy": "Your soybean plant is healthy! Continue care: adequate moisture during pod fill, weed control, monitor for pests, and avoid over-fertilization.",
    "Squash___Powdery_mildew": "Apply fungicide with sulfur or potassium bicarbonate. Remove heavily infected leaves. Improve air circulation. Water at soil level. Plant resistant varieties.",
    "Strawberry___Leaf_scorch": "Remove and destroy infected leaves. Apply fungicide. Ensure good air circulation. Avoid overhead watering. Renovate beds after harvest.",
    "Strawberry___healthy": "Your strawberry plant is healthy! Continue care: remove runners for larger berries, mulch with straw, water regularly, and fertilize after harvest.",
    "Tomato___Bacterial_spot": "Apply copper-based bactericide. Remove infected leaves. Practice crop rotation. Use disease-free transplants. Avoid working with wet plants.",
    "Tomato___Early_blight": "Apply fungicide containing chlorothalonil. Remove lower infected leaves. Mulch to prevent soil splash. Stake plants for air circulation. Water at soil level.",
    "Tomato___Late_blight": "Remove and destroy infected plants immediately. Apply fungicide with chlorothalonil or copper. Avoid overhead watering. Ensure good air circulation. Plant resistant varieties.",
    "Tomato___Leaf_Mold": "Improve air circulation through pruning and spacing. Reduce humidity. Apply fungicide if severe. Remove infected leaves. Avoid overhead watering.",
    "Tomato___Septoria_leaf_spot": "Apply fungicide containing chlorothalonil or copper. Remove infected lower leaves. Mulch to prevent soil splash. Practice crop rotation. Stake plants.",
    "Tomato___Spider_mites Two-spotted_spider_mite": "Spray with insecticidal soap or neem oil. Increase humidity around plants. Remove heavily infested leaves. Introduce predatory mites. Avoid over-fertilizing.",
    "Tomato___Target_Spot": "Apply fungicide with chlorothalonil. Remove infected leaves. Improve air circulation. Avoid overhead watering. Practice crop rotation. Mulch to prevent soil splash.",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus": "No cure available. Remove and destroy infected plants. Control whitefly vectors with insecticides or yellow sticky traps. Use virus-resistant varieties. Cover plants with row covers.",
    "Tomato___Tomato_mosaic_virus": "No cure available. Remove and destroy infected plants. Disinfect tools with bleach solution. Wash hands after handling tobacco products. Plant resistant varieties. Control aphid vectors.",
    "Tomato___healthy": "Your tomato plant is healthy! Continue care: consistent watering, balanced fertilization, pruning suckers, staking for support, and regular harvesting."
}


def get_treatment(disease_name):
    """Get treatment recommendation."""
    return treatment_recommendations.get(
        disease_name,
        "Consult with a local agricultural expert or extension service for specific treatment recommendations."
    )


# Flask Routes
@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/upload')
def upload():
    return render_template('upload.html')


@app.route('/chatbot')
def chatbot_page():
    return render_template('chatbot.html')


@app.route('/predict', methods=['POST'])
def predict():
    """Handle image upload and prediction."""
    try:
        if 'file' not in request.files:
            flash('No file selected. Please choose an image.', 'error')
            return redirect(url_for('upload'))
        
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('upload'))
        
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload JPG, JPEG, or PNG images.', 'error')
            return redirect(url_for('upload'))
        
        # Save file
        filepath = save_uploaded_file(file)
        app.logger.info(f"File saved: {filepath}")
        
        # Make prediction using API
        disease_name, confidence = predict_disease_api(filepath)
        app.logger.info(f"Prediction: {disease_name} ({confidence:.2f}%)")
        
        # Get treatment
        treatment = get_treatment(disease_name)
        
        # Render results
        return render_template('result.html',
            image_path=filepath,
            disease=disease_name,
            confidence=round(confidence, 2),
            treatment=treatment,
            low_confidence=(confidence < CONFIDENCE_THRESHOLD),
            threshold=CONFIDENCE_THRESHOLD,
            supported_crops=", ".join(SUPPORTED_CROPS)
        )
    
    except Exception as e:
        app.logger.error(f"Error: {str(e)}")
        flash(f'Prediction failed: {str(e)}', 'error')
        return redirect(url_for('upload'))


# Chatbot API
@app.route('/api/chatbot', methods=['POST'])
def chatbot():
    """Simple chatbot API for plant disease questions."""
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower()
        
        # Simple keyword-based responses
        if 'tomato' in user_message and ('blight' in user_message or 'disease' in user_message):
            response = "Tomato blight is common. For Late Blight: Remove infected plants immediately and apply fungicide. For Early Blight: Remove lower leaves and apply chlorothalonil fungicide."
        elif 'potato' in user_message:
            response = "Potato diseases include Early Blight and Late Blight. Practice crop rotation, use certified seed potatoes, and apply appropriate fungicides."
        elif 'apple' in user_message:
            response = "Common apple diseases include Apple Scab, Black Rot, and Cedar Apple Rust. Prune for air circulation and apply fungicides as needed."
        elif 'healthy' in user_message or 'care' in user_message:
            response = "For healthy plants: Ensure proper watering, adequate sunlight, good air circulation, regular fertilization, and monitor for early disease signs."
        elif 'confidence' in user_message or 'accuracy' in user_message:
            response = "Our AI model achieves 92-96% accuracy. We use an 80% confidence threshold to warn about uncertain predictions."
        elif 'upload' in user_message or 'how' in user_message:
            response = "To detect disease: Click 'Upload', choose a clear photo of the affected leaf, and submit. Use good lighting and focus for best results."
        else:
            response = "I can help with plant disease questions! Ask about specific crops (tomato, potato, apple), disease symptoms, or how to use the detection system."
        
        return jsonify({
            'success': True,
            'response': response
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 400


@app.errorhandler(413)
def too_large(e):
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload'))


@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', 
        message="Page not found."), 404


@app.errorhandler(500)
def internal_error(e):
    return render_template('error.html', 
        message="An internal server error occurred."), 500


if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("AGRODETECT AI - PRODUCTION VERSION")
    print("=" * 60)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Model: Hugging Face API (nateraw/plant-disease)")
    print(f"Confidence threshold: {CONFIDENCE_THRESHOLD}%")
    print("=" * 60 + "\n")
    
    if HF_API_TOKEN == "hf_YOUR_TOKEN_HERE":
        print("⚠️  WARNING: Please set your Hugging Face API token!")
        print("Get free token at: https://huggingface.co/settings/tokens")
        print("=" * 60 + "\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
