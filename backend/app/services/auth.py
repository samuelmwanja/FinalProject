import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.db.session import get_db
from app.models.user import User
from app.schemas.token import TokenPayload
from app.schemas.user import UserCreate
from app.services.supabase import get_supabase_service

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# OAuth2 password bearer token for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")
settings = get_settings()

def create_user(db: Session, user_data: UserCreate) -> User:
    """
    Create a new user in both Supabase Auth and database
    """
    try:
        # First create the user in Supabase Auth
        supabase_service = get_supabase_service()
        
        if not supabase_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service is not available",
            )
        
        # Create user in Supabase Auth
        auth_response = supabase_service.auth_signup(
            email=user_data.email,
            password=user_data.password,
            metadata={"full_name": user_data.full_name}
        )
        
        if "error" in auth_response:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error creating user in authentication service: {auth_response['error']['message']}",
            )
        
        # Get the user ID from Supabase response
        user_id = auth_response["user"]["id"]
        
        # Create user in our database
        db_user = User(
            id=user_id,
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password="supabase_managed",  # We don't store the password, it's managed by Supabase
            is_active=True,
        )
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        return db_user
        
    except Exception as e:
        logger.error(f"Error creating user: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating user: {str(e)}",
        )

def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user with email and password using Supabase Auth
    """
    try:
        supabase_service = get_supabase_service()
        
        if not supabase_service.is_available():
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Authentication service is not available",
            )
        
        # Authenticate with Supabase
        auth_response = supabase_service.auth_login(email=email, password=password)
        
        if "error" in auth_response:
            logger.warning(f"Authentication failed: {auth_response['error']['message']}")
            return None
        
        # Get the user ID from the response
        user_id = auth_response["user"]["id"]
        
        # Get the user from our database
        user = db.query(User).filter(User.id == user_id).first()
        
        if not user:
            # User exists in Supabase but not in our database, create it
            user = User(
                id=user_id,
                email=email,
                hashed_password="supabase_managed",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        return user
        
    except Exception as e:
        logger.error(f"Error authenticating user: {str(e)}")
        return None

def create_access_token(subject: str) -> str:
    """
    Create a JWT access token for a user
    """
    expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Get the current user from the token
    """
    try:
        # Verify token
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        token_data = TokenPayload(**payload)
        
        # Check if token has expired
        if datetime.fromtimestamp(token_data.exp) < datetime.now():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except (JWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == token_data.sub).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    
    return user 