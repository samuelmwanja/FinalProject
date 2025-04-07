from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Any

from app.ml.spam_classifier_ml import get_ml_classifier
from app.schemas.youtube import Comment, CommentList

router = APIRouter()

@router.post("/classify", response_model=Dict[str, Any])
async def classify_text(request: Dict[str, str]):
    """
    Classify a single comment for spam
    """
    if "text" not in request:
        raise HTTPException(status_code=400, detail="Text field is required")
    
    text = request["text"]
    classifier = get_ml_classifier()
    
    # Classify the text
    result = classifier.classify(text)
    
    return result

@router.post("/classify_batch", response_model=List[Dict[str, Any]])
async def classify_batch(comments: List[Dict[str, str]]):
    """
    Classify multiple comments for spam
    """
    if not comments:
        raise HTTPException(status_code=400, detail="Comments array is required")
    
    results = []
    classifier = get_ml_classifier()
    
    for comment in comments:
        if "text" not in comment:
            results.append({
                "error": "Text field is required",
                "text": comment.get("text", ""),
                "is_spam": False,
                "spam_probability": 0.0,
                "risk_level": "low",
                "method": "error"
            })
            continue
            
        text = comment["text"]
        
        # Classify the text
        result = classifier.classify(text)
        result["text"] = text
        
        results.append(result)
    
    return results

@router.post("/classify_youtube_comments", response_model=CommentList)
async def classify_youtube_comments(comments: CommentList):
    """
    Classify YouTube comments for spam and return updated CommentList with spam probabilities
    """
    classifier = get_ml_classifier()
    updated_comments = []
    
    for comment in comments.items:
        # Classify the comment text
        result = classifier.classify(comment.text)
        
        # Update the comment with spam probability and risk level
        comment.spam_probability = result["spam_probability"]
        comment.risk_level = result["risk_level"]
        comment.is_spam = result["is_spam"]
        comment.classification_method = result["method"]
        updated_comments.append(comment)
    
    # Return updated comment list
    return CommentList(
        items=updated_comments,
        next_page_token=comments.next_page_token,
        total_results=comments.total_results
    ) 