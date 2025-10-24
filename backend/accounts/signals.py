from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.conf import settings
from .models import UserProfile
import logging

# For handling error reporting
logger = logging.getLogger(__name__)

# Signal to automatically create a UserProfile when a new user is created
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    """
    This function is triggered after a User instance is saved. 
    If the user is newly created (created=True), a corresponding UserProfile is also created.
    
    Args:
        sender: The model class that sent the signal (in this case, the custom user model).
        instance: The actual instance of the user model that was saved.
        created: A boolean indicating whether the instance was created (True) or updated (False).
    """
    try:
        if created:  # Only create the profile if the user is newly created
            UserProfile.objects.create(user=instance)  # Create a new UserProfile associated with the user
    except Exception as e:
        logger.error(f"Error creating UserProfile for {instance}: {e}")

# Signal to save the UserProfile whenever the associated User instance is saved
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    """
    This function is triggered after a User instance is saved. 
    It ensures that the associated UserProfile is saved whenever the User is saved.
    
    Args:
        sender: The model class that sent the signal (in this case, the custom user model).
        instance: The actual instance of the user model that was saved.
    """
    try:
        instance.userprofile.save()  # Save the related UserProfile instance to reflect changes
    except UserProfile.DoesNotExist:
        logger.warning(f"UserProfile for {instance} does not exist, skipping save.")

# Automatically delete UserProfile when CustomUser is deleted
@receiver(post_delete, sender=settings.AUTH_USER_MODEL)
def delete_user_profile(sender, instance, **kwargs):
    """
    This function is triggered after a User instance is deleted. 
    It ensures that the associated UserProfile is deleted when the User is deleted.
    
    Args:
        sender: The model class that sent the signal (in this case, the custom user model).
        instance: The actual instance of the user model that was deleted.
    """
    try:
        instance.userprofile.delete()  # Delete the associated UserProfile
    except UserProfile.DoesNotExist:
        logger.info(f"UserProfile for {instance} does not exist, nothing to delete.")  # Log if the profile doesn't exist