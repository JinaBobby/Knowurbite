import os
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.preprocessing import image_dataset_from_directory

# Load the processed data from the directory
batch_size = 32
image_size = (128, 128)

# Note: This loads the data directly from the folders you just created
train_ds = image_dataset_from_directory(
    'data/processed/images',
    validation_split=0.2,
    subset="training",
    seed=123,
    image_size=image_size,
    batch_size=batch_size
)
val_ds = image_dataset_from_directory(
    'data/processed/images',
    validation_split=0.2,
    subset="validation",
    seed=123,
    image_size=image_size,
    batch_size=batch_size
)

# Build a simple CNN model
model = keras.Sequential([
    keras.layers.Conv2D(32, 3, activation='relu', input_shape=(128, 128, 3)),
    keras.layers.MaxPooling2D(),
    keras.layers.Conv2D(64, 3, activation='relu'),
    keras.layers.MaxPooling2D(),
    keras.layers.Flatten(),
    keras.layers.Dense(128, activation='relu'),
    keras.layers.Dense(1, activation='sigmoid')  # Sigmoid for binary classification
])

# Compile the model
model.compile(optimizer='adam',
              loss='binary_crossentropy',
              metrics=['accuracy'])

# Train the model
print("Starting model training...")
model.fit(
    train_ds,
    validation_data=val_ds,
    epochs=10
)

# Save the trained model to a file
model.save('models/adulteration_model.h5')
print("Model training and saving complete!")