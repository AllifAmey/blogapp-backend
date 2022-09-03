from django.contrib import admin
from profiles_api import models

# Register your models here.

admin.site.register(models.UserProfileSetting)
admin.site.register(models.Blog)
admin.site.register(models.Friend)
admin.site.register(models.FriendList)
admin.site.register(models.BlockedUser)
admin.site.register(models.BlockedList)