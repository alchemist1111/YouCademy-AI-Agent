from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer
from django.contrib.auth import authenticate
from rest_framework.exceptions import ValidationError
from .tokens import generate_tokens
from rest_framework import permissions


User = get_user_model()

class UserRegistrationAPIView(APIView):
    """
        Handles user registration.
        - Takes data from the request body and creates a new user in the system.
        - Returns a success message and limited user data on successful registration.
    """
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    
    def post(self, request, *args, **kwargs):
        """
          Handles the POST request to register a new user.
          
        """
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
            return Response(response_data, status=status.HTTP_201_CREATED)
        
        response_data = {
            'status': 'error',
            'message': 'Registration failed.',
            'errors': serializer.errors
        }
        return Response(response_data, status=status.HTTP_400_BAD_REQUEST)


class UserLoginAPIView(APIView):
    """
        Handles user login.
        - Authenticates the user with email and password.
        - Returns JWT tokens (access and refresh tokens) on successful login.
    """ 
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
           
    def post(self, request, *args, **kwargs):
        # Extract email and password from request data
        email = request.data.get('email')
        password = request.data.get('password')
        
        # Check if email and password are provided
        if not email or not password:
            raise ValidationError("Email and password are required fields.")
            
        try:
            # Get the user by email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Ivalid email or password
            response_data = {
                'status': 'error',
                'message': 'Invalid credentials.'
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED) 
        
        # Authenticate the user
        user = authenticate(request, email=email, password=password)
        
        if user is None:
            # Invalid email or password
            response_data = {
                'status': 'error',
                'message': 'Invalid credentials.'
            }
            return Response(response_data, status=status.HTTP_401_UNAUTHORIZED)
        
            
        # Generate the tokens for the authenticated user
        # Create JWT tokens for the authenticated user
        token = generate_tokens(user)
        
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
            
            
                  

