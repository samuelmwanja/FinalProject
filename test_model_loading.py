import pickle
import os
import sys

print("Python version:", sys.version)
print("Current working directory:", os.getcwd())

model_path = "/Users/samuel/Documents/toDO/backend/app/ml/models/spam_classifier_model.pkl"
vectorizer_path = "/Users/samuel/Documents/toDO/backend/app/ml/models/count_vectorizer.pkl"

print("Checking if model file exists:", os.path.exists(model_path))
print("Checking if vectorizer file exists:", os.path.exists(vectorizer_path))

try:
    print("Attempting to load model...")
    with open(model_path, 'rb') as file:
        model = pickle.load(file)
    print("Model loaded successfully!")
    print("Model type:", type(model))
    
    print("\nAttempting to load vectorizer...")
    with open(vectorizer_path, 'rb') as file:
        vectorizer = pickle.load(file)
    print("Vectorizer loaded successfully!")
    print("Vectorizer type:", type(vectorizer))
    
    # Test the model with a simple example
    print("\nTesting model with a sample text...")
    sample_text = "Check out my channel and subscribe!"
    vectorized_text = vectorizer.transform([sample_text]).toarray()
    prediction = model.predict(vectorized_text)[0]
    prediction_proba = model.predict_proba(vectorized_text)[0]
    
    print("Sample text:", sample_text)
    print("Prediction:", prediction)
    print("Prediction probability:", prediction_proba)
    
except Exception as e:
    print("Error loading model or vectorizer:", str(e))
    import traceback
    traceback.print_exc() 