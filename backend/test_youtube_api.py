#!/usr/bin/env python
"""
Simple test script for testing the YouTube API connectivity and comment retrieval.
"""

import os
import json
import traceback
import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def test_youtube_api():
    # Set up API key
    api_key = os.environ.get("YOUTUBE_API_KEY")
    if not api_key:
        print("ERROR: No YouTube API key found in environment variables")
        return
    
    print(f"Using API key: {api_key[:5]}... (length: {len(api_key)})")
    
    # Test video IDs - ensure these are real public YouTube videos
    test_videos = [
        "2HRBJCp9XkI",  # A popular video that should have comments
        "hmFitk-9ds"    # This is the problematic ID from the screenshot
    ]
    
    for video_id in test_videos:
        print("\n" + "="*80)
        print(f"Testing video ID: {video_id}")
        
        try:
            # Initialize the YouTube API client
            youtube = googleapiclient.discovery.build(
                "youtube", "v3", developerKey=api_key)
            
            # First get video details
            print("\nFetching video details...")
            video_request = youtube.videos().list(
                part="snippet,statistics",
                id=video_id
            )
            
            video_response = video_request.execute()
            
            if not video_response.get('items'):
                print(f"ERROR: No video found with ID {video_id}")
                continue
                
            video_title = video_response['items'][0]['snippet']['title']
            comment_count = int(video_response['items'][0]['statistics'].get('commentCount', 0))
            
            print(f"Video title: {video_title}")
            print(f"Comment count: {comment_count}")
            
            if comment_count == 0:
                print("WARNING: This video has no comments")
                continue
                
            # Now get comments
            print("\nFetching comments...")
            comments_request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=10
            )
            
            comments_response = comments_request.execute()
            comment_items = comments_response.get('items', [])
            
            print(f"Retrieved {len(comment_items)} comments")
            
            if comment_items:
                print("\nSample comments:")
                for i, item in enumerate(comment_items[:3], 1):
                    comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
                    author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                    print(f"{i}. {author}: {comment_text[:100]}...")
            else:
                print("No comments retrieved despite comment count > 0")
                
        except googleapiclient.errors.HttpError as e:
            print(f"YouTube API HttpError: {str(e)}")
            error_content = e.content.decode('utf-8') if hasattr(e, 'content') else "No error content"
            print(f"Error details: {error_content}")
            
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            traceback.print_exc()
    
    print("\n" + "="*80)
    print("Test complete!")

if __name__ == "__main__":
    test_youtube_api() 