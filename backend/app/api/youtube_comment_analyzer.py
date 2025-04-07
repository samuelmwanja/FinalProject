import os
import re
import logging
from typing import Dict, List, Tuple, Any, Optional

import googleapiclient.discovery
import googleapiclient.errors
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

from app.ml.spam_classifier import get_classifier
from app.core.config import get_settings

# Initialize logging
logger = logging.getLogger(__name__)

# Constants
MAX_RESULTS_PER_PAGE = 100

class YouTubeCommentAnalyzer:
    """
    Analyzes YouTube comments for spam/scams using the trained classifier
    """
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.YOUTUBE_API_KEY
        self.youtube = None
        self.oauth_credentials = None
        self.classifier = get_classifier()
        
        # Initialize API client
        self._init_api_client()
        
    def _init_api_client(self) -> None:
        """Initialize the YouTube API client with API key"""
        if not self.api_key:
            logger.error("YouTube API key not found in environment")
            raise ValueError("YouTube API key is required")
            
        try:
            self.youtube = googleapiclient.discovery.build(
                "youtube", "v3", developerKey=self.api_key
            )
            logger.info("YouTube API client initialized")
        except Exception as e:
            logger.error(f"Failed to initialize YouTube API client: {str(e)}")
            raise
    
    def authenticate_oauth(self, client_secrets_file: str, scopes: List[str] = None) -> None:
        """
        Authenticate with OAuth to allow posting comments
        """
        if scopes is None:
            scopes = ["https://www.googleapis.com/auth/youtube.force-ssl"]
            
        try:
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, scopes)
            self.oauth_credentials = flow.run_console()
            
            # Rebuild the API client with OAuth credentials
            self.youtube = googleapiclient.discovery.build(
                "youtube", "v3", credentials=self.oauth_credentials
            )
            logger.info("Authenticated with OAuth successfully")
        except Exception as e:
            logger.error(f"OAuth authentication failed: {str(e)}")
            raise
    
    def analyze_video_comments(self, video_id: str, max_comments: int = 200, 
                               post_warnings: bool = False) -> Dict[str, Any]:
        """
        Analyze comments for a specific YouTube video
        
        Args:
            video_id: YouTube video ID
            max_comments: Maximum number of comments to analyze
            post_warnings: Whether to post warning replies to spam comments
            
        Returns:
            Dict with analysis results
        """
        if not self.youtube:
            self._init_api_client()
            
        # Check if authenticated for posting warnings
        if post_warnings and not self.oauth_credentials:
            logger.warning("OAuth credentials required to post warning comments")
            post_warnings = False
            
        # Get video details first
        try:
            video_info = self._get_video_info(video_id)
        except Exception as e:
            logger.error(f"Failed to get video info: {str(e)}")
            return {"success": False, "error": str(e)}
            
        # Track results
        results = {
            "video_id": video_id,
            "video_title": video_info.get("title", "Unknown"),
            "comment_count": video_info.get("comment_count", 0),
            "spam_detected": 0,
            "comments_analyzed": 0,
            "spam_comments": [],
            "success": True
        }
        
        # Early return if no comments
        if results["comment_count"] == 0:
            logger.info(f"No comments found for video {video_id}")
            return results
            
        # Retrieve and analyze comments
        try:
            comments_analyzed = 0
            spam_detected = 0
            
            next_page_token = None
            
            while comments_analyzed < max_comments:
                # Fetch comments
                response = self.youtube.commentThreads().list(
                    part="snippet,replies",
                    videoId=video_id,
                    maxResults=min(MAX_RESULTS_PER_PAGE, max_comments - comments_analyzed),
                    pageToken=next_page_token
                ).execute()
                
                # Process comments
                items = response.get("items", [])
                if not items:
                    break
                    
                for item in items:
                    # Analyze top-level comment
                    top_comment = item["snippet"]["topLevelComment"]["snippet"]
                    comment_text = top_comment["textDisplay"]
                    author = top_comment["authorDisplayName"]
                    
                    # Check if it's spam
                    probability, risk_level, features = self.classifier.classify(comment_text)
                    comments_analyzed += 1
                    
                    if probability > 0.7:  # High probability threshold
                        spam_detected += 1
                        spam_info = {
                            "text": comment_text,
                            "author": author,
                            "probability": probability,
                            "risk_level": risk_level,
                            "is_reply": False,
                            "comment_id": item["id"]
                        }
                        results["spam_comments"].append(spam_info)
                        
                        # Post warning if enabled
                        if post_warnings and self.oauth_credentials:
                            self._post_warning_reply(
                                parent_id=item["id"],
                                author_name=author
                            )
                    
                    # Check replies if they exist
                    reply_count = item["snippet"]["totalReplyCount"]
                    if reply_count > 0 and "replies" in item:
                        for reply in item["replies"]["comments"]:
                            reply_text = reply["snippet"]["textDisplay"]
                            reply_author = reply["snippet"]["authorDisplayName"]
                            
                            # Check if it's spam
                            probability, risk_level, features = self.classifier.classify(reply_text)
                            comments_analyzed += 1
                            
                            if probability > 0.7:  # High probability threshold
                                spam_detected += 1
                                spam_info = {
                                    "text": reply_text,
                                    "author": reply_author,
                                    "probability": probability,
                                    "risk_level": risk_level,
                                    "is_reply": True,
                                    "comment_id": reply["id"],
                                }
                                results["spam_comments"].append(spam_info)
                                
                                # Post warning if enabled
                                if post_warnings and self.oauth_credentials:
                                    self._post_warning_reply(
                                        parent_id=item["id"],  # Reply to the parent comment thread
                                        author_name=reply_author
                                    )
                
                # Check if we need to get more comments
                next_page_token = response.get("nextPageToken")
                if not next_page_token or comments_analyzed >= max_comments:
                    break
            
            # Update final results
            results["comments_analyzed"] = comments_analyzed
            results["spam_detected"] = spam_detected
            
            logger.info(f"Analysis complete for video {video_id}: {spam_detected} spam comments found")
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing comments: {str(e)}")
            results["success"] = False
            results["error"] = str(e)
            return results
    
    def _get_video_info(self, video_id: str) -> Dict[str, Any]:
        """Get basic information about a YouTube video"""
        try:
            response = self.youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            ).execute()
            
            if not response.get("items"):
                raise ValueError(f"No video found with ID {video_id}")
                
            video = response["items"][0]
            return {
                "title": video["snippet"]["title"],
                "comment_count": int(video["statistics"].get("commentCount", 0)),
                "view_count": int(video["statistics"].get("viewCount", 0)),
                "channel_title": video["snippet"]["channelTitle"]
            }
        except Exception as e:
            logger.error(f"Error getting video info: {str(e)}")
            raise
    
    def _post_warning_reply(self, parent_id: str, author_name: str) -> None:
        """Post a warning reply to a spam comment"""
        if not self.oauth_credentials:
            logger.warning("OAuth credentials required to post comments")
            return
            
        try:
            request = self.youtube.comments().insert(
                part="snippet",
                body={
                    "snippet": {
                        "parentId": parent_id,
                        "textOriginal": f"Warning: The comment by *{author_name}* above may be spam or a scam according to our machine learning model. Please exercise caution."
                    }
                }
            )
            response = request.execute()
            logger.info(f"Posted warning reply to comment {parent_id}")
            return response
        except Exception as e:
            logger.error(f"Failed to post warning reply: {str(e)}")
            return None

# Create a standalone script function for CLI usage
def analyze_youtube_video_comments(video_id: str, max_comments: int = 200, post_warnings: bool = False):
    """
    Command-line function to analyze YouTube video comments
    """
    try:
        analyzer = YouTubeCommentAnalyzer()
        
        # Authenticate if posting warnings
        if post_warnings:
            client_secrets_file = "client_secret.json"
            if os.path.exists(client_secrets_file):
                analyzer.authenticate_oauth(client_secrets_file)
            else:
                logger.warning(f"Client secrets file not found: {client_secrets_file}")
                post_warnings = False
        
        # Run analysis
        results = analyzer.analyze_video_comments(
            video_id=video_id,
            max_comments=max_comments,
            post_warnings=post_warnings
        )
        
        # Print results
        if results["success"]:
            print(f"\nAnalysis of YouTube video: {results['video_title']}")
            print(f"Comments analyzed: {results['comments_analyzed']} out of {results['comment_count']}")
            print(f"Spam comments detected: {results['spam_detected']}")
            
            if results["spam_comments"]:
                print("\nPotential spam comments:")
                for i, comment in enumerate(results["spam_comments"][:10], 1):
                    print(f"\n{i}. Author: {comment['author']} (Spam probability: {comment['probability']:.2f})")
                    print(f"   {comment['text'][:100]}..." if len(comment['text']) > 100 else comment['text'])
                    
                if len(results["spam_comments"]) > 10:
                    print(f"\n... and {len(results['spam_comments']) - 10} more spam comments")
        else:
            print(f"\nAnalysis failed: {results.get('error', 'Unknown error')}")
    
    except Exception as e:
        print(f"Error: {str(e)}")

# For command-line execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Analyze YouTube video comments for spam")
    parser.add_argument("video_id", help="YouTube video ID to analyze")
    parser.add_argument("--max", type=int, default=200, help="Maximum number of comments to analyze")
    parser.add_argument("--warn", action="store_true", help="Post warning replies to spam comments")
    
    args = parser.parse_args()
    analyze_youtube_video_comments(args.video_id, args.max, args.warn) 