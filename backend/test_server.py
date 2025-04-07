#!/usr/bin/env python3
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging
from typing import Dict, Any, Optional, List
import numpy as np
import json
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Define models
class VideoAnalysisRequest(BaseModel):
    video_url: str
    max_comments: Optional[int] = 100

# Create app
app = FastAPI(
    title="YouTube Spam Detection API",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom JSON encoder to handle NumPy types
class NumpyJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.bool_):
            return bool(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

# Add middleware for request logging
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request path: {request.url.path}")
    logger.info(f"Request method: {request.method}")
    logger.info(f"Request headers: {request.headers}")
    
    try:
        # Try to log request body for POST/PUT requests
        if request.method in ["POST", "PUT"]:
            body = await request.body()
            if body:
                try:
                    logger.info(f"Request body: {body.decode()}")
                except Exception:
                    logger.info(f"Request body (binary): {len(body)} bytes")
    except Exception as e:
        logger.error(f"Error logging request body: {e}")
    
    # Process the request
    try:
        response = await call_next(request)
        logger.info(f"Response status: {response.status_code}")
        return response
    except Exception as e:
        logger.error(f"Unhandled exception: {str(e)}")
        raise

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "0.1.0"}

# Test API endpoint
@app.post("/api/v1/youtube/analyze")
async def analyze_youtube_video(request: VideoAnalysisRequest):
    """
    Analyze YouTube video comments for spam
    """
    try:
        # Example of data that includes NumPy values
        example_data = {
            "title": "Example Video",
            "total_comments": 100,
            "spam_comments": np.int64(25),  # NumPy integer
            "spam_rate": np.float64(25.5),  # NumPy float
            "is_spam": np.bool_(True),      # NumPy boolean
            "array_data": np.array([1, 2, 3, 4, 5]),  # NumPy array
            "nested": {
                "value": np.float32(42.5)   # Nested NumPy value
            }
        }
        
        # Convert NumPy values to Python native types
        result = json.loads(json.dumps(example_data, cls=NumpyJSONEncoder))
        
        # Add request info
        result["video_url"] = request.video_url
        result["max_comments"] = request.max_comments
        
        return result
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    uvicorn.run("test_server:app", host="0.0.0.0", port=8082, reload=True) 