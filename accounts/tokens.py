from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken
import logging

logger = logging.getLogger(__name__)

def generate_tokens(user):
    refresh = RefreshToken.for_user(user)
    
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