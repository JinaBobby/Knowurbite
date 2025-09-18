import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
from tensorflow import keras
import numpy as np
from PIL import Image
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure upload folder
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Serve uploaded files
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# Load model if available
try:
    model = keras.models.load_model('models/adulteration_model.h5')
    image_size = (128, 128)
    print("Model loaded successfully.")
except Exception as e:
    print(f"Model not found or error loading model: {e}")
    print("Running without image analysis capabilities.")
    model = None
    image_size = (128, 128)

def analyze_ingredients_nlp(text):
    if not text:
        return "No ingredients provided for analysis."
    
    # We will use placeholder keywords for the demo
    analysis = "The ingredients list appears to be standard. However, a full analysis would check for synthetic additives and known allergens. \n"
    
    if "sugar" in text.lower() or "syrup" in text.lower():
        analysis += "The presence of sugar or syrup is noted, which could be a concern for diabetic individuals or in products like honey."
    if "dye" in text.lower() or "color" in text.lower():
        analysis += "The presence of artificial dyes is noted. Some dyes are not safe for children or pregnant women."
    
    # Placeholder for pregnancy and children
    analysis += "The product is generally safe for all age groups, but consult a doctor if you are pregnant."
    
    return analysis

def save_submission_to_db(food_image_path, audio_path, ingredients_text, review, proof_image_path, risk_score, result):
    try:
        conn = sqlite3.connect('knowurbite.db')
        c = conn.cursor()
        
        # Check if the table has the required columns
        c.execute("PRAGMA table_info(submissions)")
        columns = [column[1] for column in c.fetchall()]
        
        # If the table doesn't have the new columns, use a fallback insert
        if 'audio_path' not in columns or 'ingredients_text' not in columns:
            print("Warning: Using fallback database insert (old schema)")
            c.execute("INSERT INTO submissions (image_path, review, proof_image_path, risk_score, status) VALUES (?, ?, ?, ?, ?)", 
                     (food_image_path, review, proof_image_path, risk_score, result))
        else:
            # Use the new schema with all columns
            c.execute("INSERT INTO submissions (image_path, audio_path, ingredients_text, review, proof_image_path, risk_score, status) VALUES (?, ?, ?, ?, ?, ?, ?)", 
                     (food_image_path, audio_path, ingredients_text, review, proof_image_path, risk_score, result))
        
        conn.commit()
        conn.close()
        return True
    except sqlite3.Error as e:
        print(f"Database error: {e}")
        return False

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    role = request.form['role']
    if role == 'public_user':
        return redirect(url_for('public_dashboard'))
    elif role == 'lab':
        return "Lab Dashboard (To be implemented)"
    elif role == 'officer':
        return "Officer Dashboard (To be implemented)"

@app.route('/public_dashboard')
def public_dashboard():
    return render_template('public_dashboard.html')

@app.route('/check_method')
def check_method():
    return render_template('check_method.html')

@app.route('/upload_image')
def upload_image():
    return render_template('upload_image.html')

@app.route('/upload_audio')
def upload_audio():
    return render_template('upload_audio.html')

@app.route('/upload_ingredients')
def upload_ingredients():
    return render_template('upload_ingredients.html')

@app.route('/check_adulteration', methods=['POST'])
def check_adulteration():
    check_type = request.form.get('check_type', 'image')
    
    if check_type == 'image':
        if 'food_image' not in request.files:
            session['prediction_result'] = "No image submitted for prediction."
            session['food_image_path'] = None
            return redirect(url_for('show_result'))
        
        file = request.files['food_image']
        if file.filename == '':
            session['prediction_result'] = "No image submitted for prediction."
            session['food_image_path'] = None
            return redirect(url_for('show_result'))

        if file:
            filepath = None
            result = "An error occurred during prediction."
            try:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)

                if model:
                    img = Image.open(filepath).convert('RGB')
                    img = img.resize(image_size)
                    img_array = np.array(img) / 255.0
                    img_array = np.expand_dims(img_array, axis=0)
                    prediction = model.predict(img_array)

                    risk_score = float(prediction[0])
                    if risk_score >= 0.4:
                        result = "The food sample appears to be ADULTERATED."
                    elif risk_score <= 0.3:
                        result = "The food sample appears to be PURE."
                    else:
                        result = "The model is UNSURE. A lab check is recommended."
                else:
                    # Demo mode - random result
                    result = random.choice([
                        "The food sample appears to be ADULTERATED.",
                        "The food sample appears to be PURE.",
                        "The model is UNSURE. A lab check is recommended."
                    ])

                session['prediction_result'] = result
                session['food_image_path'] = filepath

            except Exception as e:
                print(f"Error during prediction: {e}")
                result = "An error occurred during prediction."
    
    elif check_type == 'audio':
        if 'audio_sample' not in request.files:
            session['prediction_result'] = "No audio sample submitted."
            return redirect(url_for('show_result'))
        
        file = request.files['audio_sample']
        if file.filename == '':
            session['prediction_result'] = "No audio sample submitted."
            return redirect(url_for('show_result'))

        if file:
            try:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                session['audio_path'] = filepath
                
                # Placeholder for audio analysis
                result = random.choice([
                    "Audio analysis: Potential adulteration detected",
                    "Audio analysis: No signs of adulteration",
                    "Audio analysis: Inconclusive results"
                ])
                session['prediction_result'] = result
            except Exception as e:
                print(f"Error during audio processing: {e}")
                session['prediction_result'] = "An error occurred during audio analysis."
    
    elif check_type == 'ingredients':
        ingredients_text = request.form.get('ingredients_text', '')
        ingredients_photo = request.files.get('ingredients_photo')
        
        if ingredients_photo and ingredients_photo.filename != '':
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], ingredients_photo.filename)
            ingredients_photo.save(filepath)
            session['ingredients_image_path'] = filepath
        
        # Process text with NLP
        analysis_result = analyze_ingredients_nlp(ingredients_text)
        session['ingredients_result'] = analysis_result
        
        # Generate a result based on the analysis
        if "sugar" in ingredients_text.lower() or "syrup" in ingredients_text.lower() or "dye" in ingredients_text.lower():
            result = "Ingredients analysis: Suspicious components found"
        else:
            result = "Ingredients analysis: No obvious issues detected"
        
        session['prediction_result'] = result
    
    return redirect(url_for('show_result'))

@app.route('/result')
def show_result():
    result = session.get('prediction_result', 'No result found')
    return render_template('prediction_result.html', result=result)

@app.route('/review_form')
def review_form():
    return render_template('review_form.html')

@app.route('/submit_review', methods=['POST'])
def submit_review():
    review = request.form['review']
    proof_image = request.files.get('proof_image')
    vendor_info = request.form.get('vendor_info', '')

    # Store the review and vendor info in session
    session['review'] = review
    session['vendor_info'] = vendor_info

    # Handle proof image upload
    proof_image_path = None
    if proof_image and proof_image.filename != '':
        proof_image_path = os.path.join(app.config['UPLOAD_FOLDER'], proof_image.filename)
        proof_image.save(proof_image_path)
        session['proof_image_path'] = proof_image_path

    # Get other session data
    food_image_path = session.get('food_image_path')
    audio_path = session.get('audio_path')
    prediction_result = session.get('prediction_result')
    ingredients_result = session.get('ingredients_result', '')

    risk_score = "0.75"  # Placeholder

    # Save to database
    success = save_submission_to_db(
        food_image_path, 
        audio_path, 
        ingredients_result, 
        review, 
        proof_image_path, 
        risk_score, 
        prediction_result
    )
    
    if not success:
        # Handle database error gracefully
        session['database_error'] = True
    
    return redirect(url_for('report_summary'))

@app.route('/report_summary')
def report_summary():
    # Get all data from session before clearing it
    result = session.get('prediction_result', 'No analysis performed')
    review = session.get('review', 'No review provided')
    food_image_path = session.get('food_image_path')
    proof_image_path = session.get('proof_image_path')
    ingredients_result = session.get('ingredients_result', 'No ingredients analysis performed.')
    vendor_info = session.get('vendor_info', 'No vendor information provided')
    database_error = session.get('database_error', False)
    
    # Extract filenames for display
    food_image = os.path.basename(food_image_path) if food_image_path else None
    proof_image = os.path.basename(proof_image_path) if proof_image_path else None
    
    # Clear session data after retrieving it
    session_keys = ['prediction_result', 'review', 'food_image_path', 'proof_image_path', 
                   'ingredients_result', 'audio_path', 'ingredients_image_path', 'vendor_info', 'database_error']
    for key in session_keys:
        if key in session:
            session.pop(key)
    
    return render_template('report_summary.html', 
                         result=result, 
                         review=review, 
                         food_image=food_image, 
                         proof_image=proof_image, 
                         ingredients_result=ingredients_result,
                         vendor_info=vendor_info,
                         database_error=database_error)

if __name__ == '__main__':
    app.run(debug=True)