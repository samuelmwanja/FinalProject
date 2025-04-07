#!/usr/bin/env python
"""
Script to convert external model files (scam_model and vectorizer) to the format used by our project
"""
import os
import sys
import pickle
import shutil
from pathlib import Path

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.config import get_settings

def convert_external_model():
    """
    Convert external model files to our project format
    """
    print("\n" + "="*80)
    print("External Model Converter")
    print("="*80)
    
    # Check if external model files exist
    external_model_path = input("Path to external model file (scam_model): ") or "scam_model"
    external_vectorizer_path = input("Path to external vectorizer file (vectorizer): ") or "vectorizer"
    
    # Check if files exist
    if not os.path.exists(external_model_path):
        print(f"Error: External model file not found at {external_model_path}")
        return
    
    if not os.path.exists(external_vectorizer_path):
        print(f"Error: External vectorizer file not found at {external_vectorizer_path}")
        return
    
    # Load settings to get model paths
    settings = get_settings()
    
    # Get the model directory
    model_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "app", "ml", "models"
    )
    
    # Create the directory if it doesn't exist
    os.makedirs(model_dir, exist_ok=True)
    
    # Destination paths
    dest_model_path = os.path.join(model_dir, "spam_classifier_model.pkl")
    dest_vectorizer_path = os.path.join(model_dir, "count_vectorizer.pkl")
    
    # Check if destination files already exist and create backups if needed
    if os.path.exists(dest_model_path):
        backup_model_path = dest_model_path + ".backup"
        print(f"Creating backup of existing model: {backup_model_path}")
        shutil.copy2(dest_model_path, backup_model_path)
    
    if os.path.exists(dest_vectorizer_path):
        backup_vectorizer_path = dest_vectorizer_path + ".backup"
        print(f"Creating backup of existing vectorizer: {backup_vectorizer_path}")
        shutil.copy2(dest_vectorizer_path, backup_vectorizer_path)
    
    # Load and convert external model
    try:
        print("\nLoading external model files...")
        
        # Load external model
        with open(external_model_path, 'rb') as f:
            external_model = pickle.load(f)
        
        # Load external vectorizer
        with open(external_vectorizer_path, 'rb') as f:
            external_vectorizer = pickle.load(f)
        
        print("External model files loaded successfully.")
        
        # Save model in our format
        print("\nSaving model files in project format...")
        with open(dest_model_path, 'wb') as f:
            pickle.dump(external_model, f)
        
        with open(dest_vectorizer_path, 'wb') as f:
            pickle.dump(external_vectorizer, f)
        
        print("Model files saved successfully.")
        print(f"Model saved to: {dest_model_path}")
        print(f"Vectorizer saved to: {dest_vectorizer_path}")
        
        print("\nConversion complete! Your model files are now ready to use with the project.")
        print("You can now run 'python scan_youtube_comments.py' to analyze comments.")
        
    except Exception as e:
        print(f"Error converting model: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    convert_external_model() 