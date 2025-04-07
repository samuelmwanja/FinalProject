from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from typing import List, Dict, Any, Optional

class YouTubeAPI:
    """
    Service class for interacting with the YouTube API
    """
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.youtube = build("youtube", "v3", developerKey=api_key)
    
    def get_video_comments(self, video_id: str, max_results: int = 100) -> List[Dict[str, Any]]:
        """
        Fetch comments for a specific video ID
        
        Args:
            video_id: YouTube video ID
            max_results: Maximum number of comments to return (default: 100)
            
        Returns:
            List of comment data dictionaries
        """
        try:
            # Make API request
            request = self.youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=max_results
            )
            response = request.execute()
            
            # Extract and format comments
            comments = []
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