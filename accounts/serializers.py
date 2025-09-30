from rest_framework import serializers
from .models import User
from django.core.exceptions import ValidationError

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    pass


# User registration serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True, required=True)
    
    Meta = User
    fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'password', 'password_confirmation']
    
    def validate(self, data):
        """Ensure password and password confirmation match"""
        if data['password'] != data['password_confirmation']:
            raise serializers.ValidationError('Passwords must match.')
        return data
    
    def create(self, validated_data):
        """Create a new user instance with hashed password"""
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password) # Hash the password
        user.save()
        return user