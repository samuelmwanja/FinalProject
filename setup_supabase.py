#!/usr/bin/env python3
import os
import sys
import logging
from supabase import create_client
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Supabase credentials
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    logger.error("Supabase URL or key not found. Please set them in .env file.")
    sys.exit(1)

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def setup_supabase():
    """
    Sets up Supabase by executing SQL from the supabase_init.sql file
    """
    logger.info("Setting up Supabase tables...")
    
    try:
        # Read SQL script
        with open('supabase_init.sql', 'r') as f:
            sql = f.read()
        
        # Split SQL by semicolons (to handle multiple statements)
        # This is a simple approach and may not work for complex SQL
        statements = [s.strip() for s in sql.split(';') if s.strip()]
        
        # Execute each statement
        for statement in statements:
            logger.info(f"Executing: {statement[:50]}...")  # Log just the start of each statement
            result = supabase.table("_sqlrun").insert({"query": statement}, count="exact").execute()
            logger.info(f"Result: {result}")
    
    except Exception as e:
        logger.error(f"Error setting up Supabase: {str(e)}")
        raise
    
    logger.info("Supabase setup completed successfully!")

def create_default_ml_settings():
    """
    Creates default ML settings for testing
    """
    logger.info("Adding default ML settings...")
    
    default_keywords = [
        "check my channel", 
        "sub4sub", 
        "subscribe to my channel",
        "free robux",
        "free vbucks",
        "make money fast",
        "I made $1000",
        "click my profile",
        "check my bio",
        "dating site"
    ]
    
    default_bot_patterns = [
        "^[A-Za-z0-9]+bot$",
        ".*\\d{3}$"
    ]
    
    try:
        # We can't add this directly as it requires a user_id
        # In a real setup, this would be done as part of user creation
        logger.info("Note: Default ML settings would be created when a user registers")
        
    except Exception as e:
        logger.error(f"Error creating default ML settings: {str(e)}")

if __name__ == "__main__":
    try:
        setup_supabase()
        create_default_ml_settings()
        logger.info("Setup complete!")
    except Exception as e:
        logger.error(f"Setup failed: {str(e)}")
        sys.exit(1) 