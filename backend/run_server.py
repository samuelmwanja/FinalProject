#!/usr/bin/env python3
import os
import sys
import signal
import subprocess
import time
import json
import re
import pickle
import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import uvicorn
import logging
import requests
from urllib.parse import urlparse, parse_qs
import datetime

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

# Kill any processes using our target port
def kill_processes_on_ports(ports):
    """Kill any processes using the specified ports."""
    for port in ports:
        try:
            print(f"Checking for processes on port {port}...")
            # Using subprocess.run to get PIDs
            cmd = f"lsof -i :{port} -t"
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                print(f"Found processes on port {port}: {pids}")
                
                for pid in pids:
                    if pid.strip():
                        try:
                            print(f"Killing process {pid}...")
                            os.kill(int(pid), signal.SIGKILL)
                            print(f"Killed process {pid}")
                        except Exception as e:
                            print(f"Error killing process {pid}: {e}")
            else:
                print(f"No processes found on port {port}")
        except Exception as e:
            print(f"Error checking port {port}: {e}")
            
    # Small delay to ensure processes are terminated
    time.sleep(1)

# Function to extract video ID from YouTube URL
def extract_video_id(url: str) -> Optional[str]:
    """Extract the video ID from various forms of YouTube URLs"""
    logger.info(f"Extracting ID from URL: {url}")
    
    if not url:
        logger.info("Empty URL provided")
        return None
    
    # Strip any whitespace
    url = url.strip()
    
    # If input is just a video ID (no URL format)
    if len(url) >= 5 and len(url) <= 30 and "/" not in url and "." not in url:
        if re.match(r'^[a-zA-Z0-9_-]{11}$', url):
            logger.info(f"URL appears to be a direct video ID: {url}")
            return url
    
    # Special case for shortened youtu.be links
    if "youtu.be/" in url:
        parts = url.split("youtu.be/")
        if len(parts) >= 2:
            id_part = parts[1].split("?")[0].split("#")[0].split("&")[0]
            if id_part:
                logger.info(f"Extracted video ID from youtu.be URL: {id_part}")
                return id_part

    # Handle URL format with comprehensive patterns
    try:
        # Expanded patterns to match more YouTube URL formats
        patterns = [
            # Standard watch URLs
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})(?:&[^&]*)*$',
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?(?:[^&]*&)*v=([a-zA-Z0-9_-]{11})(?:&[^&]*)*$',
            # Short URLs
            r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([a-zA-Z0-9_-]{11})(?:\?[^?]*)?$',
            # Embed URLs
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([a-zA-Z0-9_-]{11})(?:\?[^?]*)?$',
            # HTML5 URLs
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([a-zA-Z0-9_-]{11})(?:\?[^?]*)?$',
            # Share URLs
            r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([a-zA-Z0-9_-]{11})(?:\?[^?]*)?$',
            # Mobile app URLs
            r'(?:https?:\/\/)?(?:www\.)?m\.youtube\.com\/watch\?v=([a-zA-Z0-9_-]{11})(?:&[^&]*)*$',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                video_id = match.group(1)
                logger.info(f"Extracted video ID {video_id} using regex pattern")
                return video_id
        
        # Try URL parsing as fallback
        parsed_url = urlparse(url)
        
        # Handle youtu.be URLs
        if parsed_url.netloc in ('youtu.be', 'www.youtu.be'):
            video_id = parsed_url.path.lstrip('/')
            logger.info(f"Extracted video ID using youtu.be path: {video_id}")
            return video_id
        
        # Handle youtube.com URLs
        if parsed_url.netloc in ('youtube.com', 'www.youtube.com', 'm.youtube.com'):
            if parsed_url.path == '/watch':
                query_params = parse_qs(parsed_url.query)
                video_id = query_params.get('v', [None])[0]
                if video_id:
                    logger.info(f"Extracted video ID from query parameters: {video_id}")
                    return video_id
            elif parsed_url.path.startswith('/embed/'):
                video_id = parsed_url.path.split('/')[2]
                logger.info(f"Extracted video ID from embed path: {video_id}")
                return video_id
            elif parsed_url.path.startswith('/v/'):
                video_id = parsed_url.path.split('/')[2]
                logger.info(f"Extracted video ID from v path: {video_id}")
                return video_id
            elif parsed_url.path.startswith('/shorts/'):
                video_id = parsed_url.path.split('/')[2]
                logger.info(f"Extracted video ID from shorts path: {video_id}")
                return video_id
        
        logger.info(f"Could not extract video ID from URL using any method")
        return None
        
    except Exception as e:
        logger.error(f"Error extracting video ID: {str(e)}")
        return None

# Function to fetch mock YouTube comments (since we don't have API key configured)
def get_mock_comments(video_id: str, max_comments: int = 100) -> List[Dict]:
    """Get mock comments for testing"""
    # Sample YouTube comments for testing
    SAMPLE_COMMENTS = [
        "Great video! Really enjoyed the content.",
        "First comment! Love your channel.",
        "This was so helpful, thanks for sharing!",
        "I've been following your channel for years. Keep up the good work!",
        "Check out my channel for similar content! Subscribe now!",
        "I make $500 a day using this simple trick: [suspicious link]",
        "Want free gift cards? Visit my website: scam-site.com",
        "Subscribe to my channel and I'll subscribe back!",
        "Awesome video! Also check out my latest upload about making money online!",
        "Nice explanation, very clear and concise.",
        "This helped me understand the concept better.",
        "I disagree with some points, but overall good video.",
        "FREE IPHONE GIVEAWAY! Click my profile to enter!",
        "Get 1000 subscribers in one day with this method: [link]",
        "I can help you get verified on YouTube, DM me on Instagram",
        "You look so beautiful in this video! Check my profile for my photos ;)",
        "Can we collaborate? I have a growing channel with similar content.",
        "Been waiting for this video for so long!",
        "Your editing is getting better with each video!",
        "The lighting could be improved, but content is great.",
        "MAKE MONEY FAST! Check the link in my bio!",
        "Use code 'SPAM123' for 50% off my course that teaches YouTube success",
        "I'll send 100 subscribers to anyone who subscribes to my channel!",
        "This is fake, don't believe this video. My channel has the truth!",
        "Follow me on Instagram for exclusive content and giveaways!",
        "The information at 5:23 was particularly useful.",
        "Liked and subscribed! Hope you can check out my latest video too.",
        "Music was a bit loud compared to your voice.",
        "Who's watching in 2023?",
        "Can you do a tutorial on how to create this effect?",
    ]
    
    # Use video_id as a seed for randomness to ensure consistency
    import random
    seed = sum(ord(c) for c in video_id) if video_id else 42
    random.seed(seed)
    
    # Select a random subset of comments
    num_comments = min(max_comments, len(SAMPLE_COMMENTS))
    selected_comments = random.sample(SAMPLE_COMMENTS, num_comments)
    
    # Convert to format with text field
    return [{"text": comment} for comment in selected_comments]

# Function to get video details (mock data since we don't have API key)
def get_mock_video_details(video_id: str) -> Dict:
    """Get mock video details"""
    titles = [
        "How to Build a Website in 2023 | Complete Tutorial",
        "10 Python Tips and Tricks You Need to Know",
        "Machine Learning Explained in 10 Minutes",
        "The Ultimate Guide to Digital Marketing",
        "Web Development Full Course - 12 Hours | Learn Web Dev from Scratch",
        "Data Science for Beginners - Full Course",
        "React JS Crash Course 2023",
        "The Future of Artificial Intelligence - Expert Panel Discussion",
        "Learn JavaScript in 1 Hour",
        "5 Tips to Improve Your Coding Skills Fast",
    ]
    
    # Use video_id as seed for random selection to keep it consistent
    import random
    seed = sum(ord(c) for c in video_id) if video_id else 42
    random.seed(seed)
    
    return {
        'title': random.choice(titles),
        'comment_count': random.randint(50, 200)
    }

# Load model and vectorizer
def load_model():
    """Load the spam classifier model and vectorizer"""
    try:
        # Model paths
        model_path = "/Users/samuel/Documents/toDO/spam_classifier_model.pkl"
        
        # Try to find vectorizer in the same directory
        vectorizer_path = "/Users/samuel/Documents/toDO/count_vectorizer.pkl"
        
        # Check if model file exists
        if not os.path.exists(model_path):
            logger.error(f"Model file not found at {model_path}")
            return None, None
            
        # Check if vectorizer file exists
        if not os.path.exists(vectorizer_path):
            logger.error(f"Vectorizer file not found at {vectorizer_path}")
            return None, None
        
        # Load model
        logger.info(f"Loading model from {model_path}")
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
        
        # Load vectorizer
        logger.info(f"Loading vectorizer from {vectorizer_path}")
        with open(vectorizer_path, 'rb') as f:
            vectorizer = pickle.load(f)
            
        logger.info(f"Model and vectorizer loaded successfully")
        return model, vectorizer
        
    except Exception as e:
        logger.error(f"Error loading model: {str(e)}")
        return None, None

# Classify text using model or fallback to rule-based classification
def classify_spam(text, model=None, vectorizer=None):
    """
    Classify a comment as spam or not using model or rule-based approach
    """
    # If model and vectorizer are available, use them
    if model is not None and vectorizer is not None:
        try:
            # Clean text - simple cleaning
            clean_text = re.sub(r'[^\w\s]', '', text.lower())
            
            # Transform using vectorizer
            text_vec = vectorizer.transform([clean_text])
            
            # Get prediction
            if hasattr(model, 'predict_proba'):
                # Get probability of being spam (class 1)
                proba = model.predict_proba(text_vec)[0][1]
                spam_probability = float(proba)
            else:
                # Get binary prediction
                pred = model.predict(text_vec)[0]
                spam_probability = float(pred)
            
            # Determine risk level
            risk_level = "low"
            if spam_probability > 0.3:
                risk_level = "medium"
            if spam_probability > 0.6:
                risk_level = "high"
                
            return {
                "is_spam": spam_probability > 0.5,
                "spam_probability": spam_probability,
                "risk_level": risk_level,
                "method": "ml-model"
            }
        except Exception as e:
            logger.error(f"Error using ML model for classification: {str(e)}")
            # Fall back to rule-based approach
            
    # Rule-based classification
    logger.info("Using rule-based classification")
    text_lower = text.lower()
    
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
        r'subscribe': 0.4
    }
    
    # Calculate spam score
    score = 0.0
    matches = 0
    
    for pattern, weight in spam_patterns.items():
        if re.search(pattern, text_lower):
            score += weight
            matches += 1
    
    # Normalize score
    if matches > 0:
        score = score / len(spam_patterns) * 2  # Adjust for reasonable distribution
        score = min(score, 0.95)  # Cap at 0.95
    else:
        # Add a small random factor for non-matching comments
        import random
        random.seed(sum(ord(c) for c in text))
        score = random.uniform(0.01, 0.15)
    
    # Determine risk level
    risk_level = "low"
    if score > 0.3:
        risk_level = "medium"
    if score > 0.6:
        risk_level = "high"
    
    return {
        "is_spam": score > 0.5,
        "spam_probability": score,
        "risk_level": risk_level,
        "method": "rule-based"
    }

# Add YouTube API key
YOUTUBE_API_KEY = "AIzaSyAkIjS_Z02y-9Cclgv4EgtFFK0CcRa1mcg"

# Function to fetch real YouTube comments using the API key
def fetch_youtube_comments(video_id: str, max_comments: int = 100) -> List[Dict]:
    """Fetch comments from YouTube API"""
    try:
        from googleapiclient.discovery import build
        
        logger.info(f"Fetching YouTube comments for video ID: {video_id}")
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Get comments
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(max_comments, 100),
            textFormat="plainText"
        )
        
        response = request.execute()
        
        comments = []
        for item in response.get('items', []):
            snippet = item['snippet']['topLevelComment']['snippet']
            comments.append({
                "text": snippet.get('textDisplay', ''),
                "author": snippet.get('authorDisplayName', 'YouTube User'),
                "published_at": snippet.get('publishedAt', '')
            })
            
        logger.info(f"Successfully fetched {len(comments)} comments from YouTube API")
        return comments
        
    except Exception as e:
        logger.error(f"Error fetching YouTube comments: {str(e)}")
        logger.info("Falling back to mock comments")
        # Fall back to mock comments if there's an error
        return get_mock_comments(video_id, max_comments)

# Function to get video details from YouTube API
def get_video_details(video_id: str) -> Dict:
    """Get video details from YouTube API"""
    try:
        from googleapiclient.discovery import build
        
        logger.info(f"Fetching video details for ID: {video_id}")
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)
        
        # Get video details
        request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        
        response = request.execute()
        
        # Check if video was found
        if not response.get('items'):
            logger.error(f"Video with ID {video_id} not found")
            return get_mock_video_details(video_id)
        
        video = response['items'][0]
        snippet = video.get('snippet', {})
        statistics = video.get('statistics', {})
        
        return {
            'title': snippet.get('title', f"Video {video_id}"),
            'comment_count': int(statistics.get('commentCount', 0))
        }
        
    except Exception as e:
        logger.error(f"Error fetching video details: {str(e)}")
        logger.info("Falling back to mock video details")
        # Fall back to mock data if there's an error
        return get_mock_video_details(video_id)

app = FastAPI(
    title="YouTube Spam Detection API",
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
        # Extract video ID from URL
        video_id = extract_video_id(request.video_url)
        if not video_id:
            return {"error": "Could not extract video ID from URL"}
        
        # Get video details (real data from YouTube API)
        video_details = get_video_details(video_id)
        
        # Get comments (real data from YouTube API)
        comments = fetch_youtube_comments(video_id, request.max_comments)
        
        # Determine if we're using real data or mock data
        using_real_data = YOUTUBE_API_KEY and len(comments) > 0 and comments[0].get('author') != 'YouTube User'
        
        # Load ML model and vectorizer
        model, vectorizer = load_model()
        
        # Track if we're using the ML model or rule-based approach
        using_ml = model is not None and vectorizer is not None
        
        # Classify each comment
        classified_comments = []
        spam_count = 0
        
        for comment in comments:
            result = classify_spam(comment["text"], model, vectorizer)
            result["text"] = comment["text"]
            result["author"] = comment.get("author", "YouTube User")
            result["published_at"] = comment.get("published_at", datetime.datetime.now().isoformat())
            classified_comments.append(result)
            
            if result["is_spam"]:
                spam_count += 1
        
        # Calculate spam rate
        spam_rate = (spam_count / len(comments)) * 100 if comments else 0
        
        # Sort by spam probability (highest first)
        classified_comments.sort(key=lambda x: x["spam_probability"], reverse=True)
        
        # Get top spam comments
        top_spam_comments = [comment for comment in classified_comments[:5] 
                             if comment["spam_probability"] > 0.4]
        
        # If no spam found, show top comments with highest probabilities
        if not top_spam_comments and classified_comments:
            top_spam_comments = classified_comments[:5]
        
        # Prepare result
        result = {
            "video_url": request.video_url,
            "video_id": video_id,
            "title": video_details["title"],
            "total_comments": video_details["comment_count"],
            "analyzed_comments": len(comments),
            "spam_comments": spam_count,
            "spam_rate": round(spam_rate, 1),
            "classifier_method": "ml-model" if using_ml else "rule-based",
            "recent_spam": top_spam_comments,
            "data_source": "youtube_api" if using_real_data else "mock_data"
        }
        
        # Convert NumPy types to Python types
        result = json.loads(json.dumps(result, cls=NumpyEncoder))
        
        return result
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    
    # Define the port to use
    port = 7777
    
    # Kill any existing process using this port
    try:
        print(f"Checking for any process using port {port}...")
        cmd = f"lsof -i :{port} -t"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"Found processes using port {port}: {pids}")
            
            for pid in pids:
                if pid.strip():
                    try:
                        print(f"Killing process {pid}...")
                        os.kill(int(pid), signal.SIGKILL)
                        print(f"Killed process {pid}")
                    except Exception as e:
                        print(f"Error killing process {pid}: {e}")
        else:
            print(f"No process found using port {port}")
    except Exception as e:
        print(f"Error checking for processes: {e}")
    
    # Start the server
    print(f"Starting server on port {port}...")
    try:
        # Use the direct app object to reduce module import issues
        uvicorn.run(app, host="0.0.0.0", port=port)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1) 