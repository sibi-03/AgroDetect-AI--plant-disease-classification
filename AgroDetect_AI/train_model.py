"""
AgroDetect AI - Model Training Script
This script trains a plant disease classification model using transfer learning with MobileNetV2.
Designed to run in Google Colab with GPU acceleration.
"""

import os
import json
import tensorflow as tf
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.callbacks import ModelCheckpoint, ReduceLROnPlateau, EarlyStopping

# Configuration
TRAIN_DIR = 'train/'
VALID_DIR = 'valid/'
IMAGE_SIZE = (224, 224)
BATCH_SIZE = 32
EPOCHS = 10
MIN_EPOCHS = 5
LEARNING_RATE = 1e-4
NUM_CLASSES = 38

def download_dataset():
    """
    Download the New Plant Diseases Dataset from Kaggle.
    Requires Kaggle API credentials to be configured.
    """
    print("=" * 60)
    print("DATASET DOWNLOAD")
    print("=" * 60)
    print("\nTo download the dataset, you need to:")
    print("1. Install Kaggle API: pip install kaggle")
    print("2. Upload your kaggle.json credentials file")
    print("3. Run: kaggle datasets download -d vipoooool/new-plant-diseases-dataset")
    print("4. Unzip the dataset")
    print("\nAlternatively, manually download from:")
    print("https://www.kaggle.com/datasets/vipoooool/new-plant-diseases-dataset")
    print("=" * 60)
    
    # Uncomment the following lines if running in Colab with Kaggle API configured:
    # !kaggle datasets download -d vipoooool/new-plant-diseases-dataset
    # !unzip -q new-plant-diseases-dataset.zip
    # !rm new-plant-diseases-dataset.zip

def setup_data_generators():
    """
    Create ImageDataGenerator instances for training and validation.
    Training data includes augmentation, validation data only rescaling.
    """
    print("\n" + "=" * 60)
    print("SETTING UP DATA GENERATORS")
    print("=" * 60)
    
    # Training data generator with augmentation
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        zoom_range=0.2,
        shear_range=0.2,
        fill_mode='nearest'
    )
    
    # Validation data generator with only rescaling
    valid_datagen = ImageDataGenerator(rescale=1./255)
    
    # Load training data
    train_generator = train_datagen.flow_from_directory(
        TRAIN_DIR,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=True
    )
    
    # Load validation data
    valid_generator = valid_datagen.flow_from_directory(
        VALID_DIR,
        target_size=IMAGE_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        shuffle=False
    )
    
    print(f"\nTraining samples: {train_generator.samples}")
    print(f"Validation samples: {valid_generator.samples}")
    print(f"Number of classes: {train_generator.num_classes}")
    
    return train_generator, valid_generator

def build_model():
    """
    Build the MobileNetV2-based transfer learning model.
    Architecture: MobileNetV2 (frozen) -> GlobalAvgPool -> Dropout -> Dense -> Dropout -> Output
    """
    print("\n" + "=" * 60)
    print("BUILDING MODEL ARCHITECTURE")
    print("=" * 60)
    
    # Load pre-trained MobileNetV2 base model
    base_model = MobileNetV2(
        input_shape=(224, 224, 3),
        include_top=False,
        weights='imagenet'
    )
    
    # Freeze base model layers
    base_model.trainable = False
    
    print(f"Base model: MobileNetV2 (frozen)")
    print(f"Base model parameters: {base_model.count_params():,}")
    
    # Build complete model
    model = Sequential([
        base_model,
        GlobalAveragePooling2D(),
        Dropout(0.35),
        Dense(256, activation='relu'),
        Dropout(0.25),
        Dense(NUM_CLASSES, activation='softmax')
    ])
    
    print(f"\nComplete model architecture:")
    model.summary()
    
    return model

def compile_model(model):
    """
    Compile the model with Adam optimizer and categorical crossentropy loss.
    """
    print("\n" + "=" * 60)
    print("COMPILING MODEL")
    print("=" * 60)
    
    model.compile(
        optimizer=Adam(learning_rate=LEARNING_RATE),
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )
    
    print(f"Optimizer: Adam (lr={LEARNING_RATE})")
    print(f"Loss: categorical_crossentropy")
    print(f"Metrics: accuracy")
    
    return model

def setup_callbacks():
    """
    Configure training callbacks for model checkpointing, learning rate reduction, and early stopping.
    """
    print("\n" + "=" * 60)
    print("CONFIGURING CALLBACKS")
    print("=" * 60)
    
    callbacks = [
        ModelCheckpoint(
            'plant_disease_model.h5',
            monitor='val_accuracy',
            save_best_only=True,
            mode='max',
            verbose=1
        ),
        ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_lr=1e-7,
            verbose=1
        ),
        EarlyStopping(
            monitor='val_loss',
            patience=3,
            restore_best_weights=True,
            verbose=1
        )
    ]
    
    print("✓ ModelCheckpoint: Save best model based on val_accuracy")
    print("✓ ReduceLROnPlateau: Reduce LR by 0.5 if val_loss plateaus for 2 epochs")
    print("✓ EarlyStopping: Stop if val_loss doesn't improve for 3 epochs")
    
    return callbacks

def train_model(model, train_generator, valid_generator, callbacks):
    """
    Train the model with the configured generators and callbacks.
    """
    print("\n" + "=" * 60)
    print("STARTING TRAINING")
    print("=" * 60)
    print(f"Epochs: {EPOCHS} (minimum {MIN_EPOCHS})")
    print(f"Batch size: {BATCH_SIZE}")
    print("=" * 60 + "\n")
    
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=valid_generator,
        callbacks=callbacks,
        verbose=1
    )
    
    return history

def save_class_names(train_generator):
    """
    Save class name mappings to JSON file for use during inference.
    """
    print("\n" + "=" * 60)
    print("SAVING CLASS NAMES")
    print("=" * 60)
    
    # Extract class names from generator
    class_indices = train_generator.class_indices
    # Invert dictionary to map index -> name
    class_names = {str(v): k for k, v in class_indices.items()}
    
    # Save to JSON
    with open('class_names.json', 'w') as f:
        json.dump(class_names, f, indent=2)
    
    print(f"✓ Saved {len(class_names)} class names to class_names.json")
    print(f"\nSample classes:")
    for i, (idx, name) in enumerate(list(class_names.items())[:5]):
        print(f"  {idx}: {name}")
    print(f"  ...")

def main():
    """
    Main training pipeline.
    """
    print("\n" + "=" * 60)
    print("AGRODETECT AI - MODEL TRAINING")
    print("=" * 60)
    
    # Step 1: Dataset download instructions
    download_dataset()
    
    # Check if data directories exist
    if not os.path.exists(TRAIN_DIR) or not os.path.exists(VALID_DIR):
        print("\n⚠️  ERROR: Training and validation directories not found!")
        print(f"   Expected: {TRAIN_DIR} and {VALID_DIR}")
        print("   Please download and extract the dataset first.")
        return
    
    # Step 2: Setup data generators
    train_generator, valid_generator = setup_data_generators()
    
    # Step 3: Build model architecture
    model = build_model()
    
    # Step 4: Compile model
    model = compile_model(model)
    
    # Step 5: Setup callbacks
    callbacks = setup_callbacks()
    
    # Step 6: Train model
    history = train_model(model, train_generator, valid_generator, callbacks)
    
    # Step 7: Save class names
    save_class_names(train_generator)
    
    # Training complete
    print("\n" + "=" * 60)
    print("TRAINING COMPLETE!")
    print("=" * 60)
    print(f"✓ Model saved: plant_disease_model.h5")
    print(f"✓ Class names saved: class_names.json")
    print("\nFinal metrics:")
    print(f"  Training accuracy: {history.history['accuracy'][-1]:.4f}")
    print(f"  Validation accuracy: {history.history['val_accuracy'][-1]:.4f}")
    print(f"  Training loss: {history.history['loss'][-1]:.4f}")
    print(f"  Validation loss: {history.history['val_loss'][-1]:.4f}")
    print("=" * 60)

if __name__ == '__main__':
    main()
