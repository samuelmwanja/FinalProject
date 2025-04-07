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
        Fetch comments for a specific video ID with unlimited pagination
        
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
                print(f"Fetching page {page_count}, comments so far: {len(comments)}")
                
                # Make API request
                request = self.youtube.commentThreads().list(
                    part="snippet",
                    videoId=video_id,
                    maxResults=100,  # API max per page
                    pageToken=next_page_token if next_page_token else None
                )
                response = request.execute()
                
                # Extract and format comments
                items = response.get('items', [])
                if not items:
                    print("No comments returned in this page")
                    break
                    
                for item in response.get('items', []):
                    snippet = item.get('snippet', {}).get('topLevelComment', {}).get('snippet', {})
                    if snippet:
                        comments.append({
                            'id': item.get('id', ''),
                            'text': snippet.get('textDisplay', ''),
                            'author': snippet.get('authorDisplayName', ''),
                            'author_profile_image': snippet.get('authorProfileImageUrl', ''),
                            'author_channel_url': snippet.get('authorChannelUrl', ''),
                            'like_count': snippet.get('likeCount', 0),
                            'published_at': snippet.get('publishedAt', '')
                        })
                
                # Check if we've reached the max_results limit (if specified)
                if max_results is not None and len(comments) >= max_results:
                    print(f"Reached specified limit of {max_results} comments")
                    break
                    
                # Get next page token
                next_page_token = response.get('nextPageToken')
                
                # If no more pages, exit the loop
                if not next_page_token:
                    print("No more pages of comments available")
                    break
                
                # Add a small delay to avoid rate limiting
                time.sleep(0.3)
            
            print(f"Successfully fetched {len(comments)} comments for video {video_id}")
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