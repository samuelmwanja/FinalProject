import os
import re
import pickle
import numpy as np
import logging
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path

from app.core.config import get_settings

# Initialize logging
logger = logging.getLogger(__name__)

class SpamClassifier:
    """
    A simple spam classifier for YouTube comments
    """
    def __init__(self, model_path: Optional[str] = None, vectorizer_path: Optional[str] = None):
        settings = get_settings()
        # Update to use your specific model files
        self.model_path = model_path or os.path.join(os.path.dirname(settings.ML_MODEL_PATH), "spam_classifier_model.pkl")
        self.vectorizer_path = vectorizer_path or os.path.join(os.path.dirname(settings.ML_MODEL_PATH), "count_vectorizer.pkl")
        
        self.model = None
        self.vectorizer = None
        self.is_model_loaded = False
        
        # Try to load model if it exists
        try:
            self._load_model()
        except Exception as e:
            logger.warning(f"Could not load model: {str(e)}")
            # Use fallback rules-based classification if model can't be loaded
    
    def _load_model(self) -> None:
        """
        Load the model and vectorizer from disk
        """
        if not os.path.exists(self.model_path):
            logger.warning(f"Model file not found at {self.model_path}")
            return
        
        if not os.path.exists(self.vectorizer_path):
            logger.warning(f"Vectorizer file not found at {self.vectorizer_path}")
            return
        
        try:
            # Load model
            with open(self.model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load vectorizer separately
            with open(self.vectorizer_path, 'rb') as f:
                self.vectorizer = pickle.load(f)
            
            if self.model and self.vectorizer:
                self.is_model_loaded = True
                logger.info("Spam classification model and vectorizer loaded successfully")
            else:
                logger.warning("Model or vectorizer failed to load")
        except Exception as e:
            logger.error(f"Error loading model or vectorizer: {str(e)}")
            raise
    
    def _extract_features(self, text: str) -> Dict[str, Any]:
        """
        Extract features from text for rules-based classification
        """
        # Basic features
        features = {
            'text_length': len(text),
            'contains_url': 1 if re.search(r'https?://\S+', text) else 0,
            'contains_email': 1 if re.search(r'\S+@\S+\.\S+', text) else 0,
            'contains_phone': 1 if re.search(r'\b(\+\d{1,2}\s?)?\(?\d{3}\)?[\s.-]?\d{3}[\s.-]?\d{4}\b', text) else 0,
            'all_caps_ratio': sum(1 for c in text if c.isupper()) / max(len(text), 1),
            'exclamation_count': text.count('!'),
            'question_count': text.count('?'),
            'spam_phrases': 0
        }
        
        # Check for common spam phrases
        spam_phrases = [
            'check out my', 'subscribe', 'sub4sub', 'follow me', 'check my channel',
            'check out this', 'make money', 'earn money', 'click here', 'free gift',
            'giveaway', 'winner', 'congratulations', 'lucky winner', 'lottery',
            'free robux', 'free vbucks', 'get free', 'easy money', 'work from home'
        ]
        
        text_lower = text.lower()
        for phrase in spam_phrases:
            if phrase in text_lower:
                features['spam_phrases'] += 1
        
        return features
    
    def _rules_based_classification(self, text: str) -> Tuple[float, Dict[str, Any]]:
        """
        Rules-based classification for when ML model is not available
        Returns spam probability and features used for classification
        """
        features = self._extract_features(text)
        
        # Simple scoring system
        score = 0.0
        
        # Length-based rules
        if features['text_length'] < 5:
            score += 0.1
        elif features['text_length'] > 500:
            score += 0.2
        
        # Content-based rules
        if features['contains_url']:
            score += 0.3
        if features['contains_email']:
            score += 0.5
        if features['contains_phone']:
            score += 0.4
        if features['all_caps_ratio'] > 0.5:
            score += 0.2
        if features['exclamation_count'] > 3:
            score += 0.2
        
        # Spam phrases
        score += min(features['spam_phrases'] * 0.15, 0.6)
        
        # Ensure score is between 0 and 1
        score = min(max(score, 0.0), 1.0)
        
        return score, features
    
    def classify(self, text: str) -> Tuple[float, str, Dict[str, Any]]:
        """
        Classify text as spam or not
        Returns:
            - probability: float between 0 and 1
            - risk_level: 'low', 'medium', or 'high'
            - features: dict of features used for classification
        """
        # Use ML model if available
        if self.is_model_loaded:
            try:
                # Transform text using vectorizer
                text_features = self.vectorizer.transform([text])
                
                # Get probability from model
                try:
                    # For models with predict_proba (like LogisticRegression)
                    probability = self.model.predict_proba(text_features)[0, 1]
                except AttributeError:
                    # For models without predict_proba, use decision function scaled to [0,1]
                    decision = self.model.decision_function(text_features)[0]
                    probability = 1.0 / (1.0 + np.exp(-decision))  # Sigmoid function
                
                # Extract basic features for explanation
                features = self._extract_features(text)
                
            except Exception as e:
                logger.error(f"Error using ML model: {str(e)}")
                # Fall back to rules-based classification
                probability, features = self._rules_based_classification(text)
        else:
            # Use rules-based classification
            probability, features = self._rules_based_classification(text)
        
        # Determine risk level based on probability
        if probability >= 0.8:
            risk_level = 'high'
        elif probability >= 0.4:
            risk_level = 'medium'
        else:
            risk_level = 'low'
        
        return probability, risk_level, features


# Singleton instance
_classifier = None

def get_classifier() -> SpamClassifier:
    """
    Get or create the spam classifier instance
    """
    global _classifier
    if _classifier is None:
        _classifier = SpamClassifier()
    return _classifier 