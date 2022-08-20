from django.contrib import admin
from profiles_api import models

# Register your models here.

admin.site.register(models.UserProfileSetting)
admin.site.register(models.UserProfilePicture)
admin.site.register(models.AuthenticatedUser)
admin.site.register(models.Blog)