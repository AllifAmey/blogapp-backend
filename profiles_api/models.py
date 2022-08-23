from django.db import models
from django.conf import settings  # use settings.AUTH_USER_MODEL recommended .


# blank = True means it is optional.
class UserProfileSetting(models.Model):
    """Handle user customization """
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    font_style = models.CharField(max_length=255, default="Roboto", blank=True)
    has_image = models.CharField(max_length=255, default="No", blank=True)

    def __str__(self):
        return f'{self.user}\'s Profile'


class UserProfilePicture(models.Model):
    """Handles user profile picture"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
    )
    image = models.ImageField(blank=True, null=True,
                              upload_to=f'profileCover/%Y/%m/%D/')

    def __str__(self):
        return "Check this"


class AuthenticatedUser(models.Model):
    """Handles user authentication"""
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return "Authenticating Users"


class Blog(models.Model):
    """Handle blog creation"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()

    def __str__(self):
        return f'{self.user}\'s Blog. Title: {self.title}'


class BlogPicture(models.Model):
    """Handles blog pictures"""
    blog = models.OneToOneField(
        Blog,
        on_delete=models.CASCADE
    )
    image = models.ImageField(blank=True, null=True,
                              upload_to=f'profileCover/1/')
