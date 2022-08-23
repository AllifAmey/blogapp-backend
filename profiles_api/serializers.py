from rest_framework import serializers
from django.contrib.auth.models import User

from .models import UserProfileSetting, AuthenticatedUser, Blog, UserProfilePicture, BlogPicture


class RegisterSerializer(serializers.ModelSerializer):
    """Serializes User data"""

    class Meta:
        model = User
        fields = ('id', 'username', 'password',)
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        """Handles creating User"""

        user = User.objects.create_user(validated_data['username'], password=validated_data['password'])
        user.set_password(validated_data['password'])
        new_user = User.objects.get(username=validated_data['username'])
        # add defaults here
        UserProfileSetting.objects.create(user=new_user, font_style='Roboto', has_image="No")
        return user


class UserProfileSettingSerializer(serializers.ModelSerializer):
    """Serializes profile settings of user"""

    class Meta:
        model = UserProfileSetting
        fields = ("id", "user", "font_style", "has_image")


class UserProfileImageSettingSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfilePicture
        fields = ("id", "user", "image")


class UserSerializer(serializers.ModelSerializer):
    """Serializers User data"""

    class Meta:
        model = AuthenticatedUser
        fields = ('username', 'password',)


class UserBlogSerializer(serializers.ModelSerializer):
    """Serializes the UserBlog object"""

    class Meta:
        model = Blog
        fields = ('id', 'user', 'title', 'content',)
