from datetime import datetime, timedelta
import random
import uuid
import string
import time
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.session import SessionLocal
from app.models.user import User
from app.models.comment import Comment
from app.models.settings import MLSettings
from app.core.security import get_password_hash

def random_string(length=10):
    """Generate a random string of fixed length."""
    letters = string.ascii_lowercase + string.digits
    return ''.join(random.choice(letters) for _ in range(length))

def add_test_data():
    """Add test data to the database"""
    db = SessionLocal()
    try:
        # Get existing user or create a test user
        user = db.query(User).first()
        if not user:
            # Create a test user if none exists
            print("Creating test user...")
            hashed_password = get_password_hash("admin123")
            user = User(
                email="admin@example.com",
                hashed_password=hashed_password,
                full_name="Admin User",
                is_superuser=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created test user with ID: {user.id}")
        else:
            print(f"Using existing user with ID: {user.id}")
        
        # Check if we have ML settings for the user, create if not
        ml_settings = db.query(MLSettings).filter(MLSettings.user_id == user.id).first()
        if not ml_settings:
            print("Creating ML settings...")
            ml_settings = MLSettings(
                user_id=user.id,
                sensitivity=75,
                keywords=["buy now", "free money", "click here", "discount", "offer"],
                bot_patterns=["http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+"],
                auto_delete=False,
                high_risk_threshold=0.8,
                medium_risk_threshold=0.5,
            )
            db.add(ml_settings)
            db.commit()
            print(f"Created ML settings for user {user.id}")
        else:
            print(f"ML settings already exist for user {user.id}")
        
        # Create test videos
        videos = [
            {"id": "video1", "title": "Tech Reviews #42", "channel_id": "channel1"},
            {"id": "video2", "title": "Product Launch 2023", "channel_id": "channel1"},
            {"id": "video3", "title": "Tutorial: Getting Started", "channel_id": "channel1"},
            {"id": "video4", "title": "Live Q&A Session", "channel_id": "channel1"},
            {"id": "video5", "title": "Behind the Scenes", "channel_id": "channel1"}
        ]
        
        # Create test comments
        spam_comments = [
            "Check out my channel for amazing content! Subscribe now!",
            "Free gift cards here: www.scam-site.com",
            "I made $5000 in one week! Click here to learn my secret: link.malicious.com",
            "Use discount code SPAM for 90% off at www.fakeshop.com",
            "Want more subscribers? Visit my website for cheap services!",
            "I'm giving away free iPhones, just click this link!",
            "Hot girls waiting for you at www.scam-dating.com",
            "Make money fast with this easy trick: www.pyramid-scheme.net",
            "Limited time offer! Buy one get three free!",
            "100% real no fake! Buy followers at followersmarket.com"
        ]
        
        normal_comments = [
            "Great video! I learned a lot from this.",
            "Thanks for the tutorial, it was very helpful.",
            "This is exactly what I needed to understand the concept.",
            "I've been following your channel for a while, always great content!",
            "Could you please do a follow-up video on this topic?",
            "I have a question about the second point you made.",
            "The editing on this video is top-notch.",
            "I shared this with my friends, they found it useful too.",
            "Looking forward to your next upload!",
            "This helped me solve a problem I've been having for weeks."
        ]
        
        # Check if we already have a lot of comments
        existing_comment_count = db.query(Comment).filter(Comment.user_id == user.id).count()
        if existing_comment_count > 50:
            print(f"Already have {existing_comment_count} comments, skipping comment creation")
            return
        
        print(f"Creating test comments (currently have {existing_comment_count})...")
        
        # Generate random comments (30% spam, 70% normal)
        author_names = ["JohnDoe", "JaneSmith", "TechFan22", "GamerGirl", "WebDev42", 
                      "FitnessGuru", "TravelBug", "FoodieLife", "MusicLover", "ArtEnthusiast"]
        
        # Create 100 comments
        comments_to_add = []
        now = datetime.utcnow()
        
        for i in range(100):
            # Decide if this will be a spam comment (30% chance)
            is_spam = random.random() < 0.3
            
            # Select a random video
            video = random.choice(videos)
            
            # Select a random author
            author_name = random.choice(author_names)
            author_id = f"channel_{random_string(8)}"
            
            # Generate random timestamp within the last 30 days
            random_days = random.randint(0, 30)
            random_hours = random.randint(0, 23)
            random_minutes = random.randint(0, 59)
            timestamp = now - timedelta(days=random_days, hours=random_hours, minutes=random_minutes)
            
            # Select comment text
            if is_spam:
                text = random.choice(spam_comments)
                spam_probability = random.uniform(0.65, 0.99)
            else:
                text = random.choice(normal_comments)
                spam_probability = random.uniform(0.01, 0.30)
                
            # Determine risk level
            if spam_probability > 0.8:
                risk_level = "high"
            elif spam_probability > 0.5:
                risk_level = "medium"
            else:
                risk_level = "low"
                
            # Create a unique YouTube comment ID
            youtube_comment_id = f"comment_{random_string(12)}"
            
            # Create the comment
            comment = Comment(
                user_id=user.id,
                youtube_comment_id=youtube_comment_id,
                youtube_video_id=video["id"],
                youtube_channel_id=video["channel_id"],
                content=text,
                author_name=author_name,
                author_channel_id=author_id,
                published_at=timestamp,
                spam_probability=spam_probability,
                risk_level=risk_level,
                is_spam=is_spam,
                detection_features={"keywords": ["channel", "subscribe"] if "channel" in text.lower() else []},
                created_at=timestamp,
                updated_at=timestamp
            )
            
            comments_to_add.append(comment)
            
            # Commit in batches to avoid memory issues
            if len(comments_to_add) >= 20:
                try:
                    db.add_all(comments_to_add)
                    db.commit()
                    print(f"Added batch of {len(comments_to_add)} comments")
                    comments_to_add = []
                except IntegrityError:
                    # If we have a duplicate, roll back and continue
                    db.rollback()
                    print("Integrity error, rolling back batch")
        
        # Add any remaining comments
        if comments_to_add:
            try:
                db.add_all(comments_to_add)
                db.commit()
                print(f"Added final batch of {len(comments_to_add)} comments")
            except IntegrityError:
                db.rollback()
                print("Integrity error, rolling back final batch")
                
        print("Done adding test data!")
        
    except Exception as e:
        db.rollback()
        print(f"Error adding test data: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    print("Adding test data to the database...")
    add_test_data() 