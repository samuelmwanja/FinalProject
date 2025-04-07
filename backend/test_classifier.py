import sys
import os
import json

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.ml.spam_classifier import SpamClassifier

def test_spam_classifier():
    """
    Test the spam classifier with sample comments
    """
    # Create a classifier instance
    print("Initializing spam classifier...")
    classifier = SpamClassifier()
    
    # Sample comments (mix of likely spam and non-spam)
    sample_comments = [
        "Great video! I really enjoyed it.",
        "Check out my channel for free iPhone giveaway!!! Click the link in my bio!",
        "This was really informative, thanks for sharing your knowledge.",
        "MAKE $5000 FROM HOME DAILY! visitwebsite.com to learn how!!!!",
        "I disagree with your point at 2:45, because the research actually suggests otherwise.",
        "Sub4Sub? I just subscribed! Please return the favor at my channel.",
        "👍 Very well explained. Would love to see more content like this.",
        "Check out my profile to win FREE GIFT CARDS!!! 100% LEGIT NO SCAM",
        "I've been following your work for years and this is your best video yet.",
        "FREE V-BUCKS! Go to my profile and click the link to get FREE V-BUCKS!"
    ]
    
    # Classify each comment
    print("\nClassifying sample comments:")
    print("-" * 80)
    
    results = []
    for i, comment in enumerate(sample_comments):
        probability, risk_level, features = classifier.classify(comment)
        
        result = {
            "comment": comment,
            "spam_probability": probability,
            "risk_level": risk_level,
            "is_spam": probability > 0.5,
            "features": features
        }
        
        results.append(result)
        
        # Print the result
        print(f"Comment {i+1}: {comment}")
        print(f"Spam Probability: {probability:.4f} ({risk_level} risk)")
        print(f"Classified as: {'SPAM' if probability > 0.5 else 'NOT SPAM'}")
        print("-" * 80)
    
    # Save results to a JSON file
    with open("classifier_test_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    print("\nResults saved to classifier_test_results.json")

if __name__ == "__main__":
    test_spam_classifier() 