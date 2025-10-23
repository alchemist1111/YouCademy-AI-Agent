from typing import Any
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.request import Request
from django.contrib.auth import get_user_model, authenticate
from rest_framework.exceptions import ValidationError, APIException
from rest_framework import permissions
from social_django.utils import psa
from .serializers import UserRegistrationSerializer
from .tokens import generate_tokens
import logging

logger = logging.getLogger(__name__)


User = get_user_model()

class UserRegistrationAPIView(APIView):
    """
        Handles user registration.
        - Takes data from the request body and creates a new user in the system.
        - Returns a success message and limited user data on successful registration.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST request for user registration.
        
        Args:
            request: HTTP request object containing user data
            
        Returns:
            Response object with registration status and user data
        """
        logger.info(f"Registration attempt for email: {request.data.get('email')}")
        
        try:
            serializer = UserRegistrationSerializer(data=request.data)
            if serializer.is_valid():
                user = serializer.save()
                
                # Return limited user details excluding password
                user_data = {
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email,
                    'phone_number': user.phone_number
                }
                response_data = {
                    'status': 'success',
                    'message': 'User registered successfully.',
                    'data': user_data
                }
                logger.info(f"Successfully registered user: {user.email}")
                return Response(response_data, status=status.HTTP_201_CREATED)
            
            logger.warning(f"Registration failed due to validation errors: {serializer.errors}")
            response_data = {
                'status': 'error',
                'message': 'Registration failed.',
                'errors': serializer.errors
            }
            return Response(response_data, status=status.HTTP_400_BAD_REQUEST)
            
        except Exception as e:
            logger.error(f"Registration failed with error: {str(e)}")
            raise APIException("An error occurred during registration")


class UserLoginAPIView(APIView):
    """
        Handles user login.
        - Authenticates the user with email and password.
        - Returns JWT tokens (access and refresh tokens) on successful login.
    """ 
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
           
    def post(self, request: Request, *args: Any, **kwargs: Any) -> Response:
        """
        Handle POST request for user login.
        
        Args:
            request: HTTP request object containing login credentials
            
        Returns:
            Response object with authentication tokens and user data
        """
        email = request.data.get('email')
        password = request.data.get('password')
        
        logger.info(f"Login attempt for email: {email}")
        
        if not email or not password:
            logger.warning("Login attempt with missing credentials")
            raise ValidationError("Email and password are required fields.")
            
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            logger.warning(f"Login attempt with non-existent email: {email}")
            return Response(
                {'status': 'error', 'message': 'Invalid credentials.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            ) 
        
        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        
        if user is None:
            logger.warning(f"Failed login attempt for email: {email}")
            return Response(
                {'status': 'error', 'message': 'Invalid credentials.'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Generate JWT tokens for the authenticated user
        token = generate_tokens(user)
        logger.info(f"Successful login for user: {email}")
        
        # Return response with tokens and user details
        response_data = {
            'status': 'success',
            'message': 'Login successful.',
            'data': {
                'refresh': token['refresh'],
                'access': token['access'],
                'user': {
                    'user_id': user.user_id,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'email': user.email
                }
                
            }
        }
            
        # Return response with tokens and user details
        return Response(response_data, status=status.HTTP_200_OK)   
            
            
                  

