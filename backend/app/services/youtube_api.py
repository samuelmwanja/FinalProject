from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional
import time

class YouTubeAPI:
    """
    Service class for interacting with the YouTube API
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=api_key)
    
    def get_video_comments(self, video_id: str, max_results: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Fetch comments for a specific video ID with unlimited pagination, including replies
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to return (None = all comments)
            
        Returns:
            List of comment data dictionaries
        """
        try:
            comments = []
            next_page_token = None
            page_count = 0
            
            print(f"Fetching {'all' if max_results is None else max_results} comments for video {video_id}")
            
            # Continue fetching pages until there are no more
            while True:
                page_count += 1
                print(f"Fetching page {page_count} of comments, total so far: {len(comments)}")
                
                # Make API request for top-level comments
                request = self.youtube.commentThreads().list(
                    part="snippet,replies",  # Add 'replies' to get reply data
                    videoId=video_id,
                    maxResults=100,  # API max per page
                    pageToken=next_page_token if next_page_token else None,
                    textFormat="plainText"
                )
                response = request.execute()
                
                # Extract and format comments
                items = response.get('items', [])
                if not items:
                    print("No comments returned in this page")
                    break
                
                for item in items:
                    # Get top-level comment
                    top_level_comment = item['snippet']['topLevelComment']['snippet']
                    comments.append({
                        'id': item.get('id', ''),
                        'text': top_level_comment.get('textDisplay', ''),
                        'author': top_level_comment.get('authorDisplayName', ''),
                        'author_profile_image': top_level_comment.get('authorProfileImageUrl', ''),
                        'author_channel_url': top_level_comment.get('authorChannelUrl', ''),
                        'like_count': top_level_comment.get('likeCount', 0),
                        'published_at': top_level_comment.get('publishedAt', ''),
                        'is_reply': False,
                        'parent_id': None
                    })
                    
                    # Get replies if there are any
                    reply_count = item['snippet'].get('totalReplyCount', 0)
                    if reply_count > 0 and 'replies' in item:
                        for reply in item['replies']['comments']:
                            reply_snippet = reply['snippet']
                            comments.append({
                                'id': reply.get('id', ''),
                                'text': reply_snippet.get('textDisplay', ''),
                                'author': reply_snippet.get('authorDisplayName', ''),
                                'author_profile_image': reply_snippet.get('authorProfileImageUrl', ''),
                                'author_channel_url': reply_snippet.get('authorChannelUrl', ''),
                                'like_count': reply_snippet.get('likeCount', 0),
                                'published_at': reply_snippet.get('publishedAt', ''),
                                'is_reply': True,
                                'parent_id': item.get('id', '')
                            })
                
                # Check if we've reached the max_results limit (if specified)
                if max_results is not None and len(comments) >= max_results:
                    print(f"Reached specified limit of {max_results} comments")
                    return comments[:max_results]
                    
                # Get next page token
                next_page_token = response.get('nextPageToken')
                
                # If no more pages, exit the loop
                if not next_page_token:
                    print("No more pages of comments available")
                    break
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.3)
            
            print(f"Successfully fetched {len(comments)} comments (including replies) for video {video_id}")
            return comments
            
        except HttpError as e:
            print(f"An HTTP error occurred: {e}")
            return []
        except Exception as e:
            print(f"An error occurred: {e}")
            return []

# Function to create a YouTube API instance with API key
def get_youtube_api(api_key: str) -> YouTubeAPI:
    """
    Create and return a YouTubeAPI instance with the provided API key
    """
    return YouTubeAPI(api_key=api_key) 