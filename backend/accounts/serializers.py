from typing import Dict, Any
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.contrib.auth.hashers import make_password
from django.core.validators import EmailValidator
import re
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'created_at', 'updated_at', 'is_active', 'is_staff']
    
    def validate_email(self, value: str) -> str:
        """
        Validate email format and uniqueness.
        
        Args:
            value: Email address to validate
            
        Returns:
            Validated email address
            
        Raises:
            ValidationError: If email is invalid or already in use
        """
        email_validator = EmailValidator()
        try:
            email_validator(value)
            if User.objects.filter(email=value).exists():
                logger.warning(f"Attempted to use existing email: {value}")
                raise ValidationError('Email is already in use.')
            return value
        except ValidationError as e:
            logger.warning(f"Invalid email format: {value}")
            raise ValidationError('Enter a valid email address.')
    
    def validate_phone_number(self, value: str) -> str:
        """
        Validate phone number format.
        
        Args:
            value: Phone number to validate
            
        Returns:
            Validated phone number
            
        Raises:
            ValidationError: If phone number format is invalid
        """
        phone_pattern = r'^\+?1?\d{9,15}$'
        if not value or not re.match(phone_pattern, value):
            logger.warning(f"Invalid phone number format: {value}")
            raise ValidationError('Enter a valid phone number (9-15 digits, optionally starting with +).')
        return value


# User registration serializer
class UserRegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration with password validation.
    """
    username = None  # Exclude username field
    password = serializers.CharField(write_only=True, required=True)
    password_confirmation = serializers.CharField(write_only=True, required=True)
    
    class Meta: 
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'password', 'password_confirmation']
    
    def validate_password(self, value: str) -> str:
        """
        Validate password strength against security requirements.
        
        Args:
            value: Password to validate
            
        Returns:
            Validated password
            
        Raises:
            ValidationError: If password doesn't meet security requirements
        """
        errors = []
        if len(value) < 8:
            errors.append('Password must be at least 8 characters.')
        if not re.search(r"[A-Z]", value):
            errors.append("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            errors.append("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", value):
            errors.append("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            errors.append("Password must contain at least one special character.")
        
        if errors:
            logger.warning("Password validation failed: %s", ", ".join(errors))
            raise serializers.ValidationError(errors)
            
        return value    
    
    def validate(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Ensure password and password confirmation match.
        
        Args:
            data: Dictionary containing the serializer data
            
        Returns:
            Validated data dictionary
            
        Raises:
            ValidationError: If passwords don't match
        """
        if data['password'] != data['password_confirmation']:
            logger.warning("Password confirmation mismatch during registration")
            raise serializers.ValidationError('Passwords must match.')
        return data
    
    
    def create(self, validated_data: Dict[str, Any]):
        """
        Create a new user instance with hashed password.
        
        Args:
            validated_data: Dictionary containing validated user data
            
        Returns:
            Newly created User instance
        """
        try:
            validated_data.pop('password_confirmation')
            password = validated_data.pop('password')
            user = User.objects.create(**validated_data)
            user.set_password(password)
            user.save()
            logger.info(f"Successfully created new user: {user.email}")
            return user
        except Exception as e:
            logger.error(f"Failed to create user: {str(e)}")
            raise

# User update serializer
class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user information.
    """
    password = serializers.CharField(write_only=True, required=False)
    password_confirmation = serializers.CharField(write_only=True, required=False)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'password', 'password_confirmation', 'is_active', 'is_staff']
        
    def validate_email(self, value: str) -> str:
        """
        Validate email format and uniqueness for updates.
        
        Args:
            value: Email address to validate
            
        Returns:
            Validated email address
        """
        if value != self.instance.email:
            email_validator = EmailValidator()
            try:
                email_validator(value)
                if User.objects.filter(email=value).exists():
                    logger.warning(f"Update attempted with existing email: {value}")
                    raise ValidationError('Email is already in use.')
                return value
            except ValidationError:
                logger.warning(f"Invalid email format in update: {value}")
                raise ValidationError('Enter a valid email address.')
        return value
    
    def validate_phone_number(self, value: str) -> str:
        """
        Validate phone number format for updates.
        
        Args:
            value: Phone number to validate
            
        Returns:
            Validated phone number
        """
        if value:
            phone_pattern = r'^\+?1?\d{9,15}$'
            if not re.match(phone_pattern, value):
                logger.warning(f"Invalid phone number format in update: {value}")
                raise ValidationError('Enter a valid phone number (9-15 digits, optionally starting with +).')
        return value
    
    def validate_password(self, value):
        """Check password strength"""
        if len(value) < 8:
            raise serializers.ValidationError('Password must be at least 8 characters.')
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("Password must contain at least one number.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value
    
    def validate(self, data):
        """Ensure that password and password_confirmation match"""
        password = data.get('password')
        password_confirmation = data.get('password_confirmation')
        
        # Check if both password and password_confirmation are provided
        if password and password_confirmation:
            if password != password_confirmation:
                raise serializers.ValidationError('Passwords must match.')
        return data
            
        
    
    def update(self, instance, validated_data):
        """Update the user instance with new data"""
        
        # Handle password hash before saving it, if password is provided
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)
            
        instance.first_name = validated_data.get('first_name', instance.first_name)
        instance.last_name = validated_data.get('last_name', instance.last_name)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.is_active = validated_data.get('is_active', instance.is_active)
        instance.is_staff = validated_data.get('is_staff', instance.is_staff)
        instance.save()
        return instance        