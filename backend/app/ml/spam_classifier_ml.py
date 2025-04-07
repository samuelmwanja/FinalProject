import os
import pickle
from typing import List, Dict, Tuple, Optional
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import NumPy with proper error handling
try:
    import numpy as np
    numpy_available = True
    logger.info("NumPy imported successfully")
except ImportError as e:
    logger.error(f"Error importing NumPy: {e}")
    logger.warning("NumPy not available - ML classification will be disabled")
    numpy_available = False

# Define paths
BASE_DIR = Path(__file__).resolve().parent
MODELS_DIR = BASE_DIR / "models"

# Add additional common locations to search for models
ADDITIONAL_MODEL_PATHS = [
    Path(__file__).resolve().parent.parent.parent / "ml" / "models",
    Path(__file__).resolve().parent.parent.parent / "models",
    Path(__file__).resolve().parent.parent / "models",
]

# Log the search paths
logger.info(f"Searching for models in primary location: {MODELS_DIR}")
for path in ADDITIONAL_MODEL_PATHS:
    logger.info(f"Additional model search location: {path}")

# Safe import for scikit-learn
try:
    from sklearn.feature_extraction.text import CountVectorizer
    sklearn_available = True
    logger.info("scikit-learn imported successfully")
except ImportError as e:
    logger.error(f"Error importing scikit-learn: {e}")
    logger.warning("scikit-learn not available - ML classification will be disabled")
    sklearn_available = False

class MLSpamClassifier:
    """
    Machine Learning based spam classifier for YouTube comments
    """
    
    def __init__(self):
        """Initialize the classifier with model and vectorizer paths"""
        self.model = None
        self.vectorizer = None
        self._model_loaded = False
        
        # Only attempt to load the model if numpy is available
        if numpy_available and sklearn_available:
            self._load_model()
        else:
            logger.warning("ML dependencies not available - using rule-based classification instead")
    
    @property
    def model_loaded(self):
        """Check if the model was successfully loaded"""
        return self._model_loaded
        
    @property
    def is_ml_enabled(self):
        """Check if ML classification is enabled"""
        return self.model_loaded
    
    def _load_model(self) -> None:
        """Load the model and vectorizer from disk"""
        try:
            # Check all potential model locations
            model_path = None
            vectorizer_path = None
            
            # Try the primary location first
            primary_model_path = MODELS_DIR / "spam_classifier_model.pkl"
            primary_vectorizer_path = MODELS_DIR / "count_vectorizer.pkl"
            
            if primary_model_path.exists() and primary_vectorizer_path.exists():
                model_path = primary_model_path
                vectorizer_path = primary_vectorizer_path
                logger.info(f"Found model files in primary location: {MODELS_DIR}")
            else:
                # Try additional locations
                for dir_path in ADDITIONAL_MODEL_PATHS:
                    potential_model = dir_path / "spam_classifier_model.pkl"
                    potential_vectorizer = dir_path / "count_vectorizer.pkl"
                    
                    if potential_model.exists() and potential_vectorizer.exists():
                        model_path = potential_model
                        vectorizer_path = potential_vectorizer
                        logger.info(f"Found model files in alternative location: {dir_path}")
                        break
            
            # If no model files found, create fallback models
            if model_path is None or vectorizer_path is None:
                logger.warning("No model files found in any location. Creating fallback models.")
            
                # Safer, simpler model loading to avoid compatibility issues
                try:
                    # Create basic ML models to ensure compatibility
                    from sklearn.linear_model import LogisticRegression
                    from sklearn.feature_extraction.text import CountVectorizer
                    
                    # Create model instances
                    self.model = LogisticRegression(max_iter=1000)
                    self.vectorizer = CountVectorizer(max_features=5000)
                    
                    # Train with sample data to ensure they're usable
                    sample_spam = [
                        "Check out my channel for free giveaways",
                        "Subscribe to my channel",
                        "Make money fast with this method",
                        "Free gift cards, click my profile",
                        "I'll subscribe back if you subscribe to me"
                    ]
                    sample_not_spam = [
                        "Great video, really enjoyed it",
                        "Thanks for sharing this information",
                        "I learned a lot from this",
                        "What do you think about this topic?",
                        "Looking forward to your next video"
                    ]
                    
                    X_sample = sample_spam + sample_not_spam
                    y_sample = [1] * len(sample_spam) + [0] * len(sample_not_spam)
                    
                    # Fit the models
                    X_vec = self.vectorizer.fit_transform(X_sample)
                    self.model.fit(X_vec, y_sample)
                    
                    logger.info("Fallback models created and trained successfully")
                    self._model_loaded = True
                    self._using_backup = True
                        
                except Exception as e:
                    logger.error(f"Error setting up fallback models: {e}")
                    logger.exception("Exception traceback:")
                    self._model_loaded = False
                    
            else:
                # Use found model files
                try:
                    with open(model_path, 'rb') as f:
                        self.model = pickle.load(f)
                    
                    with open(vectorizer_path, 'rb') as f:
                        self.vectorizer = pickle.load(f)
                        
                    logger.info("Pretrained models loaded successfully from files")
                    self._model_loaded = True
                except Exception as e:
                    logger.error(f"Error loading model files: {e}")
                    logger.exception("Exception traceback:")
                    self._model_loaded = False
                
        except Exception as e:
            logger.error(f"Unexpected error loading ML model: {e}")
            logger.exception("Exception traceback:")
            self._model_loaded = False
    
    def rule_based_detection(self, text: str) -> Tuple[float, str]:
        """
        Rule-based spam detection as fallback
        Returns spam probability and risk level
        """
        # Spam indicators with weighted scores
        spam_patterns = {
            r'check.*my.*channel': 0.7,
            r'subscribe.*back': 0.6,
            r'follow.*instagram': 0.4,
            r'check.*profile': 0.5,
            r'free.*subscribe': 0.8,
            r'make money': 0.7,
            r'earn \$\d+': 0.8,
            r'\$\d+.*day': 0.8,
            r'giveaway': 0.5,
            r'suspicious link': 0.9,
            r'click.*link': 0.7,
            r'www\.': 0.6,
            r'http': 0.6,
            r'discount.*code': 0.6,
            r'free.*gift': 0.8,
            r'check.*bio': 0.6,
            r'followers.*free': 0.8,
            r'subscribers.*free': 0.8,
            r'verify.*account': 0.7,
            r'dating': 0.7,
            r'dm me': 0.5,
            r'click.*profile': 0.8,
            r'cheap': 0.3,
            r'subscribe': 0.4,
            r'check out': 0.5,
            r'visit': 0.4,
            r'bitcoin': 0.7,
            r'crypto': 0.6,
            r'investment': 0.6
        }
        
        import re
        import random
        
        # Calculate spam score
        score = 0.0
        matches = 0
        text_lower = text.lower()
        
        for pattern, weight in spam_patterns.items():
            if re.search(pattern, text_lower):
                score += weight
                matches += 1
        
        # Normalize score - increased to make more aggressive
        if matches > 0:
            # Make detection more aggressive - single match is significant
            score = min(0.9, score * 1.5)  # More aggressive scaling
            if matches >= 2:
                score = min(0.98, score * 1.2)  # Multiple matches strongly suggest spam
        else:
            # Add a small random factor for non-matching comments
            random.seed(sum(ord(c) for c in text))
            score = random.uniform(0.01, 0.15)
        
        # Determine risk level
        risk_level = "low"
        if score > 0.3:
            risk_level = "medium"
        if score > 0.6:
            risk_level = "high"
            
        return score, risk_level
    
    def classify(self, comment: str) -> Dict:
        """
        Classify a comment as spam or not
        Returns a dict with classification results
        """
        if not comment or not isinstance(comment, str):
            # Handle empty or invalid comments
            return {
                "is_spam": False,
                "spam_probability": 0.0,
                "risk_level": "low",
                "method": "rule-based"
            }
        
        # First get rule-based detection result
        rule_based_prob, rule_based_risk = self.rule_based_detection(comment)
        rule_based_result = {
            "is_spam": rule_based_prob > 0.4,
            "spam_probability": rule_based_prob,
            "risk_level": rule_based_risk,
            "method": "rule-based"
        }
        
        # If model not loaded, return rule-based result
        if not self.model_loaded or not numpy_available or not sklearn_available:
            return rule_based_result
            
        # Try ML classification
        try:
            # Use ML model for classification
            logger.debug(f"Using ML model to classify: {comment[:30]}...")
            
            # Transform the text
            try:
                comment_vec = self.vectorizer.transform([comment])
            except Exception as e:
                logger.error(f"Error in vectorizer transform: {e}")
                return rule_based_result
            
            # Make prediction - handle different model types
            try:
                if hasattr(self.model, 'predict_proba'):
                    spam_prob = self.model.predict_proba(comment_vec)[0][1]
                else:
                    # For models without predict_proba
                    pred = self.model.predict(comment_vec)[0]
                    spam_prob = float(pred)
            except Exception as e:
                logger.error(f"Error in model prediction: {e}")
                return rule_based_result
            
            # Determine risk level
            risk_level = "low"
            if spam_prob > 0.3:
                risk_level = "medium"
            if spam_prob > 0.6:
                risk_level = "high"
            
            model_type = "pretrained-model" if not hasattr(self, '_using_backup') else "backup-model"
            
            # Compare with rule-based detection and use the higher spam probability
            # This ensures we catch spam that the ML model might miss
            if rule_based_prob > spam_prob + 0.3:  # Rule-based is significantly higher
                logger.info(f"Rule-based detection found spam that ML missed: {comment[:30]}...")
                return {
                    "is_spam": True,
                    "spam_probability": rule_based_prob,
                    "risk_level": rule_based_risk,
                    "method": "hybrid-detection"
                }
            
            # Use ML model result
            return {
                "is_spam": spam_prob > 0.4,
                "spam_probability": float(spam_prob),  # Convert to Python float
                "risk_level": risk_level,
                "method": model_type
            }
            
        except Exception as e:
            logger.error(f"Error using ML model for classification: {e}")
            logger.exception("Exception traceback:")
            # Fall back to rule-based detection
            return rule_based_result
    
    def process_comments(self, comments: List[str]) -> Dict:
        """
        Process a list of comments and return classification results
        """
        if not comments:
            return {
                "classified_comments": [],
                "spam_count": 0,
                "spam_rate": 0.0
            }
            
        classified_comments = []
        spam_count = 0
        
        for comment in comments:
            # Skip empty comments
            if not comment or not isinstance(comment, str):
                continue
                
            result = self.classify(comment)
            result["text"] = comment  # Add the original text
            classified_comments.append(result)
            
            if result["is_spam"]:
                spam_count += 1
        
        # Calculate spam rate
        total_comments = len(classified_comments)
        spam_rate = (spam_count / total_comments) * 100 if total_comments > 0 else 0
        
        return {
            "classified_comments": classified_comments,
            "spam_count": spam_count,
            "spam_rate": spam_rate
        }

# Singleton instance
_ml_classifier = None

def get_ml_classifier():
    """
    Get or create singleton instance of MLSpamClassifier
    """
    global _ml_classifier
    if _ml_classifier is None:
        _ml_classifier = MLSpamClassifier()
        
        # Log the status of the ML classifier
        if _ml_classifier.model_loaded:
            logger.info("ML-based spam classifier initialized successfully")
        else:
            logger.warning("ML-based spam classifier model could not be loaded. Classification may not be optimal.")
            # Try to import models if they exist in a known location but are not in the models directory
            try:
                from .import_models import import_models
                # Check common locations for model files
                potential_model_paths = [
                    os.path.join(os.path.dirname(BASE_DIR), "models", "spam_classifier_model.pkl"),
                    os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "models", "spam_classifier_model.pkl"),
                ]
                potential_vectorizer_paths = [
                    os.path.join(os.path.dirname(BASE_DIR), "models", "count_vectorizer.pkl"),
                    os.path.join(os.path.dirname(os.path.dirname(BASE_DIR)), "models", "count_vectorizer.pkl"),
                ]
                
                # Try each potential path
                for model_path in potential_model_paths:
                    if os.path.exists(model_path):
                        for vectorizer_path in potential_vectorizer_paths:
                            if os.path.exists(vectorizer_path):
                                logger.info(f"Found model files in alternative location. Importing...")
                                import_models(model_path, vectorizer_path)
                                # Try loading the model again
                                _ml_classifier._load_model()
                                if _ml_classifier.model_loaded:
                                    logger.info("ML-based spam classifier model imported and loaded successfully")
                                    break
                        if _ml_classifier.model_loaded:
                            break
            except Exception as e:
                logger.error(f"Error trying to import models from alternative locations: {e}")
                                
    return _ml_classifier

def train_model(X_train, y_train, output_dir: Optional[str] = None):
    """
    Train a new spam classifier model
    
    Args:
        X_train: List of comment texts
        y_train: List of labels (1 for spam, 0 for not spam)
        output_dir: Directory to save the model, defaults to models dir
    """
    if not sklearn_available or not numpy_available:
        logger.error("Cannot train model - dependencies not available")
        return False
        
    from sklearn.feature_extraction.text import CountVectorizer
    from sklearn.naive_bayes import MultinomialNB
    
    try:
        # Create vectorizer
        vectorizer = CountVectorizer(stop_words='english')
        X_train_vec = vectorizer.fit_transform(X_train)
        
        # Train model
        model = MultinomialNB()
        model.fit(X_train_vec, y_train)
        
        # Save model and vectorizer
        if not output_dir:
            output_dir = MODELS_DIR
            
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        model_path = os.path.join(output_dir, "spam_classifier_model.pkl")
        vectorizer_path = os.path.join(output_dir, "count_vectorizer.pkl")
        
        with open(model_path, 'wb') as f:
            pickle.dump(model, f)
            
        with open(vectorizer_path, 'wb') as f:
            pickle.dump(vectorizer, f)
            
        logger.info(f"Model and vectorizer saved to {output_dir}")
        return True
        
    except Exception as e:
        logger.error(f"Error training model: {e}")
        logger.exception("Exception traceback:")
        return False 