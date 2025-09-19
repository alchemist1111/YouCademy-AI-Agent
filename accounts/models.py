from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager

# User model
class User(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    def __str__(self):
        return f'Name: {self.first_name} {self.last_name} Email: ({self.email})'
    
# User profile
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='userprofile')
    profile_picture = models.ImageField(upload_to="profile_pictures/", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.CharField(max_length=255, blank=True)
    country = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True, null=True)
    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    
    def __str__(self):
        return f'User profile for {self.user.email}'    
