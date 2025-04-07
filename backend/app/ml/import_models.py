#!/usr/bin/env python3
"""
Import pre-trained ML models for YouTube comment spam detection.
This script imports existing model files into the system.

Usage:
    python import_models.py /path/to/spam_classifier_model.pkl /path/to/count_vectorizer.pkl

The models will be copied to the app/ml/models directory.
"""

import os
import sys
import shutil
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Define paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = os.path.join(BASE_DIR, "models")
MODEL_TARGET_PATH = os.path.join(MODELS_DIR, "spam_classifier_model.pkl")
VECTORIZER_TARGET_PATH = os.path.join(MODELS_DIR, "count_vectorizer.pkl")

def import_models(model_path, vectorizer_path):
    """Import model and vectorizer files into the system"""
    try:
        # Create models directory if it doesn't exist
        os.makedirs(MODELS_DIR, exist_ok=True)
        
        # Validate input files
        if not os.path.exists(model_path):
            logger.error(f"Model file not found: {model_path}")
            return False
            
        if not os.path.exists(vectorizer_path):
            logger.error(f"Vectorizer file not found: {vectorizer_path}")
            return False
            
        # Copy files to models directory
        logger.info(f"Copying model from {model_path} to {MODEL_TARGET_PATH}")
        shutil.copy2(model_path, MODEL_TARGET_PATH)
        
        logger.info(f"Copying vectorizer from {vectorizer_path} to {VECTORIZER_TARGET_PATH}")
        shutil.copy2(vectorizer_path, VECTORIZER_TARGET_PATH)
        
        logger.info("Models imported successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Error importing models: {str(e)}")
        return False
        
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python import_models.py /path/to/spam_classifier_model.pkl /path/to/count_vectorizer.pkl")
        sys.exit(1)
        
    model_path = sys.argv[1]
    vectorizer_path = sys.argv[2]
    
    if import_models(model_path, vectorizer_path):
        print("Models imported successfully!")
        print(f"Models saved to: {MODELS_DIR}")
    else:
        print("Failed to import models. Check the log for details.")
        sys.exit(1) 