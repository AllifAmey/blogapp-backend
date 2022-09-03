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


class Blog(models.Model):
    """Handle blog creation"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    content = models.TextField()
    image_type = models.CharField(max_length=255)
    image_url = models.URLField(max_length=255, null=True)
    font_style = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.user}\'s Blog. Title: {self.title}'

class BlockedList(models.Model):
    """Handles block list"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f'{self.user}\'s Block List'

class BlockedUser(models.Model):
    """Handles each blocked user"""

    blocked_list = models.ForeignKey(
        BlockedList,
        on_delete=models.CASCADE
    )

    blocked_user = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.blocked_user} is blocked in {self.blocked_list}'

        
class FriendList(models.Model):
    """Handles friends list"""
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE)
    
    def __str__(self):
        return f'{self.user}\'s Friend List'

class Friend(models.Model):
    """Handles each friend"""
    friend_list = models.ForeignKey(
        FriendList,
        on_delete=models.CASCADE
    )
    # This field will store the username ,
    # use this field to check against database.
    friend = models.CharField(max_length=255)
    # friend status to also indicate request
    friend_status = models.CharField(max_length=255)

    def __str__(self):
        return f'{self.friend} is a friend in {self.friend_list}'


