#!/usr/bin/env python3
"""
Test script for spam classification
"""
import os
import sys

# Add the parent directory to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the classifier
from app.ml.spam_classifier_ml import get_ml_classifier

def test_spam_classification():
    """Test spam classification with various examples"""
    # Get the classifier
    classifier = get_ml_classifier()
    
    # Test cases - known spam and non-spam examples
    test_cases = [
        # Known spam examples
        "Check out my channel for free giveaways",
        "Subscribe to my channel",
        "Make money fast with this method",
        "Free gift cards, click my profile",
        "I'll subscribe back if you subscribe to me",
        "Check my bitcoin investment strategy",
        "Get rich quick with crypto",
        
        # Known non-spam examples
        "Great video, really enjoyed it",
        "Thanks for sharing this information",
        "I learned a lot from this",
        "What do you think about this topic?",
        "Looking forward to your next video"
    ]
    
    print("\nTesting spam classification with various examples:")
    print("-" * 80)
    print(f"{'RESULT':<10} {'ML PROB':<10} {'RULE PROB':<10} {'METHOD':<15} TEXT")
    print("-" * 80)
    
    for text in test_cases:
        # Classify the text with ML
        ml_result = classifier.classify(text)
        
        # Also get rule-based detection result directly
        rule_prob, rule_risk = classifier.rule_based_detection(text)
        
        # Print the results side by side
        label = "SPAM" if ml_result["is_spam"] else "NOT SPAM"
        print(f"{label:<10} {ml_result['spam_probability']:.2f}      {rule_prob:.2f}       {ml_result['method']:<15} {text}")
    
    print("-" * 80)
    print(f"Model loaded: {classifier.model_loaded}")
    print(f"Detection method: {'ML enabled' if classifier.is_ml_enabled else 'Rule-based only'}")

if __name__ == "__main__":
    test_spam_classification() 