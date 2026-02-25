"""
AgroDetect AI - Flask Web Application (Simplified Version for Python 3.7)
This version uses a mock prediction system for demonstration purposes.
For production, upgrade to Python 3.8+ to use the Hugging Face model.
"""

import os
import time
import random
from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
from PIL import Image

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'agrodetect-ai-secret-key-change-in-production'

# Configuration
UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
CONFIDENCE_THRESHOLD = 80.0  # Minimum confidence for reliable predictions

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create uploads directory if it doesn't exist
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
    print(f"✓ Created upload directory: {UPLOAD_FOLDER}")

# Supported crops for low confidence message
SUPPORTED_CROPS = [
    "Tomato", "Potato", "Apple", "Corn/Maize", "Grape", 
    "Cherry", "Peach", "Pepper", "Strawberry", "Squash",
    "Orange", "Blueberry", "Raspberry", "Soybean"
]

# Mock disease classes (same as the real model)
DISEASE_CLASSES = [
    "Apple___Apple_scab",
    "Apple___Black_rot",
    "Apple___Cedar_apple_rust",
    "Apple___healthy",
    "Blueberry___healthy",
    "Cherry_(including_sour)___Powdery_mildew",
    "Cherry_(including_sour)___healthy",
    "Corn_(maize)___Cercospora_leaf_spot Gray_leaf_spot",
    "Corn_(maize)___Common_rust_",
    "Corn_(maize)___Northern_Leaf_Blight",
    "Corn_(maize)___healthy",
    "Grape___Black_rot",
    "Grape___Esca_(Black_Measles)",
    "Grape___Leaf_blight_(Isariopsis_Leaf_Spot)",
    "Grape___healthy",
    "Orange___Haunglongbing_(Citrus_greening)",
    "Peach___Bacterial_spot",
    "Peach___healthy",
    "Pepper,_bell___Bacterial_spot",
    "Pepper,_bell___healthy",
    "Potato___Early_blight",
    "Potato___Late_blight",
    "Potato___healthy",
    "Raspberry___healthy",
    "Soybean___healthy",
    "Squash___Powdery_mildew",
    "Strawberry___Leaf_scorch",
    "Strawberry___healthy",
    "Tomato___Bacterial_spot",
    "Tomato___Early_blight",
    "Tomato___Late_blight",
    "Tomato___Leaf_Mold",
    "Tomato___Septoria_leaf_spot",
    "Tomato___Spider_mites Two-spotted_spider_mite",
    "Tomato___Target_Spot",
    "Tomato___Tomato_Yellow_Leaf_Curl_Virus",
    "Tomato___Tomato_mosaic_virus",
    "Tomato___healthy"
]


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def allowed_file(filename):
    """Check if the uploaded file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_file(file):
    """Save uploaded file with a unique timestamp-prefixed filename."""
    filename = secure_filename(file.filename)
    timestamp = str(int(time.time()))
    unique_filename = f"{timestamp}_{filename}"
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
    file.save(filepath)
    return filepath


def predict_disease_mock(image_path):
    """
    Mock prediction function for demonstration.
    Returns a random disease with confidence score.
    
    NOTE: This is a DEMO version. For real predictions, upgrade to Python 3.8+
    and use the Hugging Face model version.
    """
    # Verify image can be opened
    try:
        img = Image.open(image_path)
        img.verify()
    except Exception as e:
        raise ValueError(f"Invalid image file: {str(e)}")
    
    # Mock prediction - randomly select a disease
    disease_name = random.choice(DISEASE_CLASSES)
    
    # Generate realistic confidence score (higher for healthy plants)
    if 'healthy' in disease_name.lower():
        confidence = random.uniform(85, 98)
    else:
        confidence = random.uniform(75, 95)
    
    return disease_name, confidence


# ============================================================================
# TREATMENT RECOMMENDATIONS
# ============================================================================

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
    """Get treatment recommendation for a disease."""
    return treatment_recommendations.get(
        disease_name,
        "Consult with a local agricultural expert or extension service for specific treatment recommendations. "
        "General advice: Remove affected plant parts, improve air circulation, ensure proper watering practices, "
        "and consider using appropriate fungicides or pesticides as needed."
    )


# ============================================================================
# FLASK ROUTES
# ============================================================================

@app.route('/')
def home():
    """Render the home page."""
    return render_template('home.html')


@app.route('/about')
def about():
    """Render the about page with technical information."""
    return render_template('about.html')


@app.route('/upload')
def upload():
    """Render the upload page with form."""
    return render_template('upload.html')


@app.route('/predict', methods=['POST'])
def predict():
    """Handle image upload and prediction."""
    try:
        # Validate file presence
        if 'file' not in request.files:
            flash('No file selected. Please choose an image.', 'error')
            return redirect(url_for('upload'))
        
        file = request.files['file']
        
        # Validate filename
        if file.filename == '':
            flash('No file selected.', 'error')
            return redirect(url_for('upload'))
        
        # Validate file type
        if not allowed_file(file.filename):
            flash('Invalid file type. Please upload JPG, JPEG, or PNG images.', 'error')
            return redirect(url_for('upload'))
        
        # Save file
        try:
            filepath = save_uploaded_file(file)
            app.logger.info(f"File saved: {filepath}")
        except Exception as e:
            app.logger.error(f"File save error: {str(e)}")
            flash('Failed to save uploaded file. Please try again.', 'error')
            return redirect(url_for('upload'))
        
        # Make prediction (mock version)
        try:
            disease_name, confidence = predict_disease_mock(filepath)
            app.logger.info(f"Prediction: {disease_name} ({confidence:.2f}%)")
        except Exception as e:
            app.logger.error(f"Prediction error: {str(e)}")
            flash('Prediction failed. Please try again.', 'error')
            return redirect(url_for('upload'))
        
        # Get treatment recommendation
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
        # Catch-all for unexpected errors
        app.logger.error(f"Unexpected error: {str(e)}")
        return render_template('error.html', 
            message="An unexpected error occurred. Please try again.")


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error."""
    flash('File is too large. Maximum size is 16MB.', 'error')
    return redirect(url_for('upload'))


@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors."""
    return render_template('error.html', 
        message="Page not found. Please check the URL and try again."), 404


@app.errorhandler(500)
def internal_error(e):
    """Handle 500 errors."""
    app.logger.error(f"Internal server error: {str(e)}")
    return render_template('error.html', 
        message="An internal server error occurred. Please try again later."), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "=" * 60)
    print("AGRODETECT AI - DEMO VERSION (Python 3.7)")
    print("=" * 60)
    print(f"Upload folder: {UPLOAD_FOLDER}")
    print(f"Allowed extensions: {ALLOWED_EXTENSIONS}")
    print("NOTE: This is a DEMO version with mock predictions")
    print("For real AI predictions, upgrade to Python 3.8+")
    print("=" * 60 + "\n")
    
    # Run Flask app
    app.run(debug=True, host='0.0.0.0', port=5000)
