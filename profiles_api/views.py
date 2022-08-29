from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.settings import api_settings
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from profiles_api import serializers
from profiles_api import models


# Create your views here.

class RegisterViewSet(viewsets.ModelViewSet):
    """Handle creating and updating profiles"""
    serializer_class = serializers.RegisterSerializer
    queryset = User.objects.all()
    


class UserSignUpApiView(ObtainAuthToken):
    """Handle creating user authentication tokens"""
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES


class UserLoginApiView(APIView):
    """Handles checking if User is authenticated"""

    def get(self, request):
        """Get all AuthenticatedUsers"""
        # Return all the users that are friends and use that for the backend
        usernames = []
        for user in User.objects.all():
            if user.is_superuser:
                continue
            if user.is_authenticated:
                usernames.append(
                    {
                        'username': user.username
                    }
                )
            
        return Response(usernames)

    def post(self, request):
        """Check if User is authenticated and displays values attached to user"""

        user_auth_status = authenticate(username=request.data.get('username'),
                                        password=request.data.get('password'))
        if user_auth_status is not None:
            try:
                User.objects.get(username=request.data.get('username'))
            except:
                print("user does not exist!")
            else:
                user = User.objects.get(username=request.data.get('username'))
                user_settings = models.UserProfileSetting.objects.get(user=user.id)

                return Response({'auth_status': 'Authenticated',
                                    "user_id": user.id,
                                    "setting_id": user_settings.id,
                                    "font_style": user_settings.font_style,
                                    "has_image": user_settings.has_image})
        else:
            return Response({'auth_status': 'Not authenticated!'})

class BlockedListViewSet(viewsets.ModelViewSet):
    """Handles creating and updating blocked list"""
    serializer_class = serializers.BlockedListSerializer
    queryset = models.BlockedList.objects.all()

class BlockedUserViewSet(viewsets.ModelViewSet):
    """Handles creating and updating blocked user"""
    serializer_class = serializers.BlockedUserSerializer
    queryset = models.BlockedUser.objects.all()

    """
    Idea of getting a user Blocked:

    Post method-
    Check to see if the user blocked is on the friend model attached to the user requesting block,
    if it is then delete the user soon-to-be blocked friend model attached to the requester ,

    If not then create blockedUser model.  

    Get Method:

    Check if all models attached to the blocked list to see and return the usernames.
    
    """

class FriendListViewSet(viewsets.ModelViewSet):
    """Handles creating and updating Friend list"""
    serializer_class = serializers.FriendListSerializer
    queryset = models.FriendList.objects.all()

class FriendViewSet(viewsets.ModelViewSet):
    """Handles creating and updating Friend list"""
    serializer_class = serializers.FriendSerializer
    queryset = models.Friend.objects.all()

    """

    Idea for friend request:
    Post method - 
    Check if friend request made to a user is on the BlockedUserModel attached to the user's block list,
    if it is then return Response with message "You can not friend request a blocked person,
     unblock them to do so"
    Check if friend request mode to a user does not have the friend requester on their blocked list, 
    if they do then return Response with message "you have been blocked and can not message". 

    if no errors, then Post method will create a model with the friend_status = "request"

    Idea for accepting friend and recognising friendship:
    Patch method - 

    Patch method will update the friend_status field to = "official" or some words to indicate friend.

    Idea for seeing who is the user's friend:

    Get method - 

    Get method will recieve a header of username,
    This info will allow django to query database to check if user exist then, 
    grab the Friend models attached to FriendList model which is attached to user,
    all friend models will be checked related to user's friend model,
    if user_status is "official" it is then added to a list which is returned as a Response.
    """


class UserBlogViewSet(viewsets.ModelViewSet):
    """Handle creating and updating blogs"""
    serializer_class = serializers.UserBlogSerializer
    queryset = models.Blog.objects.all()

    def list(self, request):
        """fetches Blog objects"""
        blog_list = []
        for blog in models.Blog.objects.all().values():
            user_id = blog["user_id"]
            for user in User.objects.all().values():
                if user["id"] == user_id:
                    blog_list.append({
                        "author": user["username"],
                        "title": blog["title"],
                        "content": blog["content"],
                        "image_type": blog['image_type'],
                        "image_url": blog['image_url'],
                        "font_style": blog['font_style']
                    })
                    break
        return Response(blog_list)


class UserProfileSettingViewSet(viewsets.ModelViewSet):
    """Handle creating and updating profile settings"""
    serializer_class = serializers.UserProfileSettingSerializer
    queryset = models.UserProfileSetting.objects.all()
