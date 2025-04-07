import logging
import os
from functools import lru_cache
from typing import Optional, Dict, List, Any

from supabase import create_client, Client
from postgrest.exceptions import APIError

from app.core.config import get_settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Get settings
settings = get_settings()

@lru_cache
def get_supabase_client() -> Optional[Client]:
    """
    Get a cached Supabase client
    """
    try:
        supabase_url = settings.SUPABASE_URL
        supabase_key = settings.SUPABASE_KEY
        
        if not supabase_url or not supabase_key:
            logger.warning("Supabase URL or key not set in environment variables")
            return None
        
        return create_client(supabase_url, supabase_key)
    except Exception as e:
        logger.error(f"Error creating Supabase client: {str(e)}")
        return None

class SupabaseService:
    """
    Service to interact with Supabase
    """
    def __init__(self):
        self.client = get_supabase_client()
    
    def is_available(self) -> bool:
        """Check if Supabase client is available"""
        return self.client is not None
    
    def auth_signup(self, email: str, password: str, metadata: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Register a new user with Supabase Auth
        """
        try:
            if not self.is_available():
                return {"error": {"message": "Supabase client not available"}}
            
            # Use the Supabase auth.sign_up method
            result = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": metadata
                }
            })
            
            # Return a dictionary that can be easily checked for errors
            return {
                "user": result.user,
                "session": result.session
            }
        except Exception as e:
            logger.error(f"Error signing up user: {str(e)}")
            return {"error": {"message": str(e)}}
    
    def auth_login(self, email: str, password: str) -> Dict[str, Any]:
        """
        Login a user with Supabase Auth
        """
        try:
            if not self.is_available():
                return {"error": {"message": "Supabase client not available"}}
            
            # Use the Supabase auth.sign_in_with_password method
            result = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            # Return a dictionary that can be easily checked for errors
            return {
                "user": result.user,
                "session": result.session
            }
        except Exception as e:
            logger.error(f"Error logging in user: {str(e)}")
            return {"error": {"message": str(e)}}
    
    def get_data(self, table: str, query=None) -> List[Dict[str, Any]]:
        """
        Get data from a Supabase table with optional query
        
        Example:
            get_data('comments', query=lambda q: q.eq('user_id', user_id).order('created_at', desc=True))
        """
        try:
            if not self.is_available():
                logger.warning("Supabase client not available")
                return []
            
            # Start with the table
            request = self.client.table(table).select('*')
            
            # Apply query if provided
            if query:
                request = query(request)
            
            # Execute the request
            response = request.execute()
            
            if hasattr(response, 'data'):
                return response.data
            return []
            
        except APIError as e:
            logger.error(f"API Error getting data from {table}: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error getting data from {table}: {str(e)}")
            return []
    
    def insert_data(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Insert data into a Supabase table
        """
        try:
            if not self.is_available():
                return {"error": "Supabase client not available"}
            
            response = self.client.table(table).insert(data).execute()
            
            if hasattr(response, 'data') and len(response.data) > 0:
                return response.data[0]
            return {"error": "No data returned"}
            
        except APIError as e:
            logger.error(f"API Error inserting into {table}: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error inserting into {table}: {str(e)}")
            return {"error": str(e)}
    
    def update_data(self, table: str, id_column: str, id_value: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update data in a Supabase table
        """
        try:
            if not self.is_available():
                return {"error": "Supabase client not available"}
            
            response = self.client.table(table).update(data).eq(id_column, id_value).execute()
            
            if hasattr(response, 'data') and len(response.data) > 0:
                return response.data[0]
            return {"error": "No data returned"}
            
        except APIError as e:
            logger.error(f"API Error updating {table}: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error updating {table}: {str(e)}")
            return {"error": str(e)}
    
    def delete_data(self, table: str, id_column: str, id_value: str) -> Dict[str, Any]:
        """
        Delete data from a Supabase table
        """
        try:
            if not self.is_available():
                return {"error": "Supabase client not available"}
            
            response = self.client.table(table).delete().eq(id_column, id_value).execute()
            
            if hasattr(response, 'data'):
                return {"success": True}
            return {"error": "No data returned"}
            
        except APIError as e:
            logger.error(f"API Error deleting from {table}: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error deleting from {table}: {str(e)}")
            return {"error": str(e)}

    def execute_sql(self, sql: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Execute raw SQL
        Warning: Be careful with SQL injection!
        """
        try:
            if not self.is_available():
                return {"error": "Supabase client not available"}
            
            # This is a simple implementation that won't work for all SQL statements
            # Use with caution and adjust as needed
            response = self.client.rpc('_sqlrun', {"query": sql, "params": params}).execute()
            
            if hasattr(response, 'data'):
                return {"data": response.data}
            return {"error": "No data returned"}
            
        except APIError as e:
            logger.error(f"API Error executing SQL: {str(e)}")
            return {"error": str(e)}
        except Exception as e:
            logger.error(f"Error executing SQL: {str(e)}")
            return {"error": str(e)}

@lru_cache()
def get_supabase_service() -> SupabaseService:
    """
    Get a cached Supabase service instance
    """
    return SupabaseService() 