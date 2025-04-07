#!/usr/bin/env python3
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import json
import os
import logging
import sys
import subprocess
import numpy as np

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

# Define models
class VideoAnalysisRequest(BaseModel):
    video_url: str
    max_comments: Optional[int] = 100

# Custom JSON encoder for NumPy types
class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, np.bool_):
            return bool(obj)
        return super().default(obj)

app = FastAPI(
    title="YouTube Spam Detection API Simple",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "ok", "version": "0.1.0"}

@app.post("/api/v1/youtube/analyze")
async def analyze_youtube_video(request: VideoAnalysisRequest):
    """
    Analyze YouTube video comments for spam
    """
    try:
        # Example data using NumPy types to test serialization
        data = {
            "title": "Example Video",
            "video_url": request.video_url,
            "max_comments": request.max_comments,
            "total_comments": np.int64(100),
            "spam_comments": np.int64(15),
            "spam_rate": np.float64(15.0),
            "is_spam": np.bool_(True),
            "spam_scores": np.array([0.8, 0.2, 0.9, 0.1, 0.7]),
            "recent_spam": [
                {"text": "Check out my channel!", "probability": np.float32(0.9)},
                {"text": "Subscribe to me!", "probability": np.float32(0.8)},
                {"text": "Free gift cards!", "probability": np.float32(0.95)}
            ]
        }
        
        # Convert NumPy types to Python types
        result = json.loads(json.dumps(data, cls=NumpyEncoder))
        
        return result
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    # Define the port to use
    port = 9000
    
    # Kill any existing process using this port
    try:
        print(f"Checking for any process using port {port}...")
        cmd = f"lsof -i :{port} -t"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"Found processes using port {port}: {pids}")
            
            for pid in pids:
                if pid:
                    try:
                        pid_num = int(pid)
                        print(f"Killing process {pid_num}...")
                        os.kill(pid_num, 9)  # SIGKILL
                        print(f"Killed process {pid_num}")
                    except Exception as e:
                        print(f"Error killing process {pid}: {e}")
        else:
            print(f"No process found using port {port}")
    except Exception as e:
        print(f"Error checking for processes: {e}")
    
    # Start the server
    print(f"Starting server on port {port}...")
    uvicorn.run("simple_api:app", host="0.0.0.0", port=port, reload=True) 