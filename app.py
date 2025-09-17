import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, session
from tensorflow import keras
import numpy as np
from PIL import Image
import random

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

os.makedirs('uploads', exist_ok=True)

model = keras.models.load_model('models/adulteration_model.h5')
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

def save_submission_to_db(food_image_path, review, proof_image_path, risk_score, result, ingredients_text):
    conn = sqlite3.connect('knowurbite.db')
    c = conn.cursor()
    c.execute("INSERT INTO submissions (image_path, review, proof_image_path, risk_score, status, ingredients_text) VALUES (?, ?, ?, ?, ?, ?)", 
              (food_image_path, review, proof_image_path, risk_score, result, ingredients_text))
    conn.commit()
    conn.close()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    role = request.form['role']
    if role == 'public_user':
        return redirect(url_for('public_dashboard'))
    elif role == 'lab':
        return "Lab Dashboard"
    elif role == 'officer':
        return "Officer Dashboard"

@app.route('/public_dashboard')
def public_dashboard():
    return render_template('public_dashboard.html')

@app.route('/check_adulteration', methods=['POST'])
def check_adulteration():
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
            filepath = os.path.join("uploads", file.filename)
            file.save(filepath)

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

            session['prediction_result'] = result
            session['food_image_path'] = filepath

        except Exception as e:
            print(f"Error during prediction: {e}")
            result = "An error occurred during prediction."
        
        return redirect(url_for('show_result'))

@app.route('/result')
def show_result():
    result = session.get('prediction_result', 'No result found')
    return render_template('prediction_result.html', result=result)

@app.route('/ingredients_page')
def ingredients_page():
    return render_template('ingredients_page.html')

@app.route('/analyze_ingredients', methods=['POST'])
def analyze_ingredients():
    ingredients_photo = request.files.get('ingredients_photo')
    ingredients_text = request.form['ingredients_text']

    analysis_result = analyze_ingredients_nlp(ingredients_text)
    
    session['ingredients_result'] = analysis_result
    
    return redirect(url_for('review_form'))

@app.route('/review_form')
def review_form():
    return render_template('review_form.html')

@app.route('/submit_report', methods=['POST'])
def submit_report():
    review = request.form['review']
    proof_image = request.files.get('proof_image')

    food_image_path = session.get('food_image_path')
    prediction_result = session.get('prediction_result')
    ingredients_result = session.get('ingredients_result')

    risk_score = "0.75"
    
    proof_image_path = None
    if proof_image and proof_image.filename != '':
        proof_image_path = os.path.join("uploads", proof_image.filename)
        proof_image.save(proof_image_path)

    save_submission_to_db(food_image_path, review, proof_image_path, risk_score, prediction_result, ingredients_result)

    if food_image_path and os.path.exists(food_image_path):
        os.remove(food_image_path)
    if 'food_image_path' in session:
        session.pop('food_image_path')
    
    return render_template('report_summary.html', result=prediction_result, review=review, food_image=os.path.basename(food_image_path) if food_image_path else None, proof_image=os.path.basename(proof_image_path) if proof_image_path else None, ingredients_result=ingredients_result)

if __name__ == '__main__':
    app.run(debug=True)