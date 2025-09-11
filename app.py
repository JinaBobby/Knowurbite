import os
from flask import Flask, render_template, request
from tensorflow import keras
import numpy as np
from PIL import Image

app = Flask(__name__)

# This line ensures the 'uploads' folder exists
os.makedirs('uploads', exist_ok=True)

# Load the trained AI model
model = keras.models.load_model('models/adulteration_model.h5')

# Define the size of the images the model expects
image_size = (128, 128)

@app.route('/')
def home():
    # This route will show the upload form to the user
    return render_template('upload.html')

@app.route('/predict', methods=['POST'])
def predict():
    # This route will handle the file upload and prediction
    if 'file' not in request.files:
        return 'No file part'

    file = request.files['file']

    if file.filename == '':
        return 'No selected file'

    if file:
        filepath = None
        result = "An error occurred during prediction."
        try:
            # Save the uploaded file temporarily
            filepath = os.path.join("uploads", file.filename)
            file.save(filepath)

            # Preprocess the image
            img = Image.open(filepath).convert('RGB')
            img = img.resize(image_size)
            img_array = np.array(img) / 255.0
            
            # The model expects a batch of images, so we add a new dimension
            img_array = np.expand_dims(img_array, axis=0)

            # Make the prediction
            prediction = model.predict(img_array)
            
            # Get the result
            if prediction[0] >= 0.4:
                result = "The food sample appears to be ADULTERATED."
            elif prediction[0] <= 0.3:
                result = "The food sample appears to be PURE."
            else:
                result = "The model is UNSURE. A lab check is recommended."

        finally:
            # This block ensures the temporary file is deleted even if an error occurs
            if filepath and os.path.exists(filepath):
                os.remove(filepath)
        
        # Render the result on a new page
        return render_template('result.html', prediction=result)

if __name__ == '__main__':
    app.run(debug=True)