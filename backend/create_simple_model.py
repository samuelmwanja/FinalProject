#!/usr/bin/env python3
# Script to create simple model files for the YouTube comment spam detector

from sklearn.feature_extraction.text import CountVectorizer
from sklearn.svm import SVC
import pickle
import os
from pathlib import Path

print("Creating simple spam classifier model files...")

# Sample data for training
spam_comments = [
    "Check out my channel for more videos!",
    "Subscribe to my channel and I'll subscribe back!",
    "Check my profile for free money!",
    "Make easy money from home, message me for details",
    "Free followers, just click my link",
    "I made $500 in one day, click here to learn how",
    "Visit my channel for amazing content",
    "Follow me on Instagram @username",
    "DM me for business opportunities",
    "Get rich quick with this simple trick",
    "Watch my latest video and comment below",
    "Subscribe and I'll follow back",
    "Earn passive income from home, comment 'INFO' below",
    "Click the link in my profile for a free gift",
    "Like and share for a chance to win",
]

non_spam_comments = [
    "Great video, thanks for sharing!",
    "I really enjoyed this content",
    "The editing is amazing in this video",
    "This helped me understand the topic better",
    "Very informative, thank you",
    "I've been waiting for this video",
    "Love the background music",
    "Will you be making more videos like this?",
    "The explanation was very clear",
    "I agree with your points",
    "This changed my perspective",
    "Well done on the production quality",
    "I learned something new today",
    "Looking forward to your next video",
    "This video answered all my questions",
]

# Combine data and create labels
all_comments = spam_comments + non_spam_comments
labels = [1] * len(spam_comments) + [0] * len(non_spam_comments)

# Create a simple vectorizer
vectorizer = CountVectorizer(lowercase=True, 
                             ngram_range=(1, 2),
                             stop_words='english')

# Fit and transform the text data
X = vectorizer.fit_transform(all_comments)

# Train a simple SVM model
model = SVC(kernel='linear', probability=True)
model.fit(X, labels)

# Save the model and vectorizer
base_dir = Path(__file__).resolve().parent

# Save model
model_path = base_dir / "spam_classifier_model.pkl"
with open(model_path, 'wb') as f:
    pickle.dump(model, f)

# Save vectorizer
vectorizer_path = base_dir / "count_vectorizer.pkl"
with open(vectorizer_path, 'wb') as f:
    pickle.dump(vectorizer, f)

print(f"Model saved to {model_path}")
print(f"Vectorizer saved to {vectorizer_path}")
print("Done! These files will be used by simple_server.py for spam classification.") 