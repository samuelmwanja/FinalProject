#!/usr/bin/env python
"""
Script to scan YouTube comments for spam/scams using the YouTube comment analyzer
"""
import os
import sys
import time

# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the analyzer
from app.api.youtube_comment_analyzer import analyze_youtube_video_comments

def main():
    """Main function to run the analyzer"""
    print("\n" + "="*80)
    print("YouTube Comment Spam Scanner")
    print("="*80)
    
    # Get video ID from args or prompt
    if len(sys.argv) > 1:
        video_id = sys.argv[1]
    else:
        video_id = input("\nEnter YouTube video ID: ")
    
    # Confirm max comments to scan
    max_comments_input = input("Maximum comments to scan [default: 200]: ")
    max_comments = int(max_comments_input) if max_comments_input else 200
    
    # Confirm if should post warning replies
    post_warnings_input = input("Post warning replies to spam comments? (y/N): ")
    post_warnings = post_warnings_input.lower() in ['y', 'yes']
    
    if post_warnings:
        print("\nNOTE: Posting warning replies requires OAuth authentication.")
        print("You will need to follow the authentication flow in the terminal.")
        time.sleep(2)
    
    print("\nStarting analysis...")
    print(f"Video ID: {video_id}")
    print(f"Max comments: {max_comments}")
    print(f"Post warnings: {'Yes' if post_warnings else 'No'}")
    print("-"*80)
    
    # Run the analyzer
    analyze_youtube_video_comments(video_id, max_comments, post_warnings)
    
    print("\nAnalysis complete!")

if __name__ == "__main__":
    main() 