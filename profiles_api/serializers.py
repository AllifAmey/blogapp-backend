from rest_framework import serializers
from django.contrib.auth.models import User

from .models import UserProfileSetting, Blog, FriendList, Friend, BlockedUser, BlockedList


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
        FriendList.objects.create(user=new_user)
        BlockedList.objects.create(user=new_user)
        return user


class BlockedListSerializer(serializers.ModelSerializer):
    """Serializes blocked list data"""

    class Meta:
        model = BlockedList
        fields = ('user',)

class BlockedUserSerializer(serializers.ModelSerializer):
    """Serializes blocked user data"""

    class Meta:
        model = BlockedUser
        fields = ('blocked_list', 'blocked_user',)

class FriendListSerializer(serializers.ModelSerializer):
    """Serializes friend list data"""

    class Meta:
        model = FriendList
        fields = ('user',)

class FriendSerializer(serializers.ModelSerializer):
    """Serializes friend list data"""

    class Meta:
        model = Friend
        fields = ('friend_list', 'friend', 'friend_status',)


class UserProfileSettingSerializer(serializers.ModelSerializer):
    """Serializes profile settings of user"""

    class Meta:
        model = UserProfileSetting
        fields = ("id", "user", "font_style", "has_image")


class UserBlogSerializer(serializers.ModelSerializer):
    """Serializes the UserBlog object"""

    class Meta:
        model = Blog
        fields = ('id', 'user', 'title', 'content', 'image_type', 'image_url', 'font_style')
