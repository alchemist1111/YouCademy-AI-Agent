from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from .serializers import UserRegistrationSerializer


User = get_user_model()

class UserRegistrationAPIView(APIView):
    """
        Handles user registration.
        - Takes data from the request body and creates a new user in the system.
        - Returns a success message and limited user data on successful registration.
    """
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




