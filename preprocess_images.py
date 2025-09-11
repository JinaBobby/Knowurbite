import os
import cv2
import numpy as np
from PIL import Image

# Define paths
raw_images_path = 'data/raw/images'
processed_images_path = 'data/processed/images'

# Create the output directories if they don't exist
for category in ['pure', 'adulterated']:
    os.makedirs(os.path.join(processed_images_path, category), exist_ok=True)

# Define image size
image_size = (128, 128)

print("Starting image preprocessing...")
for category in ['pure', 'adulterated']:
    path = os.path.join(raw_images_path, category)
    print(f"Processing images in '{path}'")
    for img_name in os.listdir(path):
        img_path = os.path.join(path, img_name)

        # Check if the file is a valid image and not a hidden file like .DS_Store
        if img_name.endswith(('.jpg', '.jpeg', '.png')):
            try:
                # Use Pillow to open and resize the image
                img = Image.open(img_path).convert('RGB')
                img = img.resize(image_size)
                
                # Convert to a numpy array for normalization
                img_array = np.array(img) / 255.0
                
                # Save the processed image
                processed_img_path = os.path.join(processed_images_path, category, img_name)
                Image.fromarray((img_array * 255).astype(np.uint8)).save(processed_img_path)
            except Exception as e:
                print(f"Could not process image: {img_name}. Error: {e}")
        else:
            print(f"Skipping non-image file: {img_name}")
            continue
            
print("Image preprocessing complete.")