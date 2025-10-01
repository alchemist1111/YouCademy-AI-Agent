from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
import logging
import uuid

logger = logging.getLogger(__name__)

# Custom RefreshToken class to handle UUIDs as user ids
class CustomRefreshToken(RefreshToken):
    @classmethod
    def for_user(cls, user):
        """
            Override for_user method to handle UUIDs for the user ID. 
            
        """
        try:
            if hasattr(user, 'user_id') and isinstance(user.user_id, uuid.UUID):
                # UUID is converted to string for token generation
                user_id = str(user.user_id)
            else:
                user_id = str(user.pk) # Default behavior for integer ids
            
            refresh = super().for_user(user)
            refresh.payload['user_id'] = user_id   # Add uuid to the payload
            return refresh  
         
        except AttributeError:
            logger.error(f"User object has no attribute 'user_id'. Please check the user model.")
            raise  

def generate_tokens(user):
    refresh = CustomRefreshToken.for_user(user)
    
    # Use the settings for token expiration times
    refresh.set_exp(lifetime=settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'])
    refresh.access_token.set_exp(lifetime=settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'])
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token)
    }
    
# Function to blacklist token
def blacklist_token(refresh_token):
    try:
        # Create a new BlacklistedToken entry with the refresh token
        BlacklistedToken.objects.create(token=refresh_token)
        return True
    except Exception as e:
        # Log the error for debugging
        logger.error(f"Error blacklisting token: {str(e)}")
        return False