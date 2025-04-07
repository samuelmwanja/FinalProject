#!/usr/bin/env python
"""
Debug script to test YouTube API for comment counts and actual comments.
This script focuses on verifying accurate comment counts.
"""
import os
import sys
import json
import googleapiclient.discovery
import googleapiclient.errors
from dotenv import load_dotenv

# Load API key from .env file
load_dotenv()
API_KEY = os.environ.get("YOUTUBE_API_KEY")

def debug_youtube_video(video_id):
    """Debug a specific YouTube video to check comment count and actual comments"""
    if not API_KEY:
        print("ERROR: YouTube API key not found in environment")
        sys.exit(1)
        
    print(f"\n{'='*80}")
    print(f"Testing video ID: {video_id}")
    print(f"Using API key: {API_KEY[:5]}...")
    
    try:
        # Initialize the YouTube API client
        youtube = googleapiclient.discovery.build(
            "youtube", "v3", developerKey=API_KEY)
            
        # 1. First get video details including comment count
        print("\n1. FETCHING VIDEO DETAILS")
        video_request = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        )
        
        video_response = video_request.execute()
        
        if not video_response.get('items'):
            print(f"ERROR: No video found with ID {video_id}")
            return
            
        video_item = video_response['items'][0]
        video_title = video_item['snippet']['title']
        
        # Extract and verify comment count
        comment_count = int(video_item['statistics'].get('commentCount', 0))
        print(f"Video title: {video_title}")
        print(f"Comment count from statistics: {comment_count}")
        
        if comment_count == 0:
            print("WARNING: This video has no comments according to statistics")
            return
        
        # 2. Fetch actual comments to verify
        print("\n2. FETCHING ACTUAL COMMENTS")
        comments_request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=100  # Request maximum allowed per request
        )
        
        comments_response = comments_request.execute()
        comments = comments_response.get('items', [])
        
        total_fetched = len(comments)
        print(f"Number of comments fetched in first request: {total_fetched}")
        
        # Check for nextPageToken - indicates more comments exist
        has_more = 'nextPageToken' in comments_response
        print(f"More comments available: {has_more}")
        
        # 3. Fetch multiple pages if needed (up to 3 pages for demonstration)
        page_count = 1
        next_page_token = comments_response.get('nextPageToken')
        
        # Fetch up to 2 more pages to check consistency
        while next_page_token and page_count < 3:
            print(f"\nFetching page {page_count + 1}...")
            page_count += 1
            
            next_request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=100,
                pageToken=next_page_token
            )
            
            next_response = next_request.execute()
            next_comments = next_response.get('items', [])
            
            print(f"Comments on page {page_count}: {len(next_comments)}")
            total_fetched += len(next_comments)
            
            next_page_token = next_response.get('nextPageToken')
        
        # 4. Summary
        print("\n3. SUMMARY")
        print(f"Total comments according to statistics: {comment_count}")
        print(f"Total comments fetched across {page_count} pages: {total_fetched}")
        
        # Calculate expected total based on pagination
        if has_more and page_count >= 3:
            print(f"Note: Only fetched {page_count} pages, more comments exist")
            average_per_page = total_fetched / page_count
            estimated_pages = comment_count / 100 if average_per_page > 90 else comment_count / average_per_page
            print(f"Estimated pages needed for all comments: ~{estimated_pages:.1f}")

        if total_fetched < comment_count:
            print("\nNOTE: The actual fetched comment count is less than the statistics count.")
            print("This is normal as YouTube statistics include all comments, while the API may")
            print("exclude deleted comments, spam comments filtered by YouTube, or disabled comments.")
        
        # 5. Sample comments
        if comments:
            print("\n4. SAMPLE COMMENTS")
            print(f"Showing 5 sample comments of {total_fetched} fetched:")
            for i, item in enumerate(comments[:5]):
                comment_text = item['snippet']['topLevelComment']['snippet']['textDisplay']
                author = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                print(f"{i+1}. {author}: {comment_text[:100]}...")
        
    except googleapiclient.errors.HttpError as e:
        print(f"YouTube API Error: {e}")
        try:
            error_content = json.loads(e.content.decode())
            print(f"Error details: {json.dumps(error_content, indent=2)}")
        except:
            print(f"Error content: {e.content.decode() if hasattr(e, 'content') else 'No details'}")
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) > 1:
        # Use the video ID provided as command-line argument
        debug_youtube_video(sys.argv[1])
    else:
        # Use a default video with known comments
        default_video = "2HRBJCp9XkI"  # Change to a video with known comments
        print(f"No video ID provided. Using default video: {default_video}")
        debug_youtube_video(default_video) 