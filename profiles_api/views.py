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
        """Get all authenticated users and display their status related to requester"""
        usernames = []
        # 2 lines below is user requesting 
        user_requester_username = request.headers['username']
        user_requester = User.objects.get(username=user_requester_username)
        # models of Friend and blocked list are checked
        # these models will be used to check if user is friend or blocked by requester 
        user_requester_friendList = models.FriendList.objects.get(user=user_requester)
        user_requester_blockedList = models.BlockedList.objects.get(user=user_requester)
        
        for user in User.objects.all():
            if user.is_superuser:
                continue
            if user.is_authenticated and user.username != user_requester_username:
                #check if userprofilesetting to get profile picture
                try:
                    models.Friend.objects.get(friend_list=user_requester_friendList, friend=user.username)
                except:
                    try:
                        models.BlockedUser.objects.get(blocked_list=user_requester_blockedList, blocked_user=user.username)
                    except:
                        user_status_toRequester = "neutral"
                    else:
                        user_status_toRequester = "blocked"
                else:
                    user_status_toRequester = "friend"
                    
                
                user_image_info = models.UserProfileSetting.objects.get(user=user)
                usernames.append(
                    {
                        'username': user.username,
                        'has_image': user_image_info.has_image,
                        'user_relation_status' : user_status_toRequester
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

    def list(self, request):
        """Displays a list of all blocked users attached to the requester's blocklist"""
        user_requester_username = request.headers['username']
        user_requester = User.objects.get(username=user_requester_username)
        user_requester_blockList = models.BlockedList.objects.get(user=user_requester)

        all_blockedUsers = []

        try:
            models.BlockedUser.objects.get(blocked_list=user_requester_blockList)
        except:
            all_blockedUsers.append({
                'message': 'Empty'
            })
        else:
            for blockedUser in models.BlockedUser.objects.get(blocked_list=user_requester_blockList):
                all_blockedUsers.append({
                    'blockedUser': blockedUser.blocked_user
                })
        return Response(all_blockedUsers)

    def create(self, request):
        """Handles creating new block models"""
        # expected Json file {'username': requester_username, 'block user': block_username} 
        user_block_request = request.data.get('blocked_user')
        print(request.data)
        print(user_block_request)
        user_block = User.objects.get(username=user_block_request)
        user_block_request_friendList = models.FriendList.objects.get(user=user_block)
        user_requester_username = request.data.get('username')
        user_requester = User.objects.get(username=user_requester_username)
        user_requester_friendList = models.FriendList.objects.get(user=user_requester)
        user_requester_blockedList = models.BlockedList.objects.get(user=user_requester)

        response = []

        try:
            models.BlockedUser.objects.get(blocked_list=user_requester_blockedList, blocked_user=user_block_request)
        except:
            try:
                models.Friend.objects.get(friend_list=user_requester_friendList, friend=user_block_request)
            except:
                # block user is not a friend nor blocked
                models.BlockedUser.objects.create(blocked_list=user_requester_blockedList, blocked_user=user_block_request)
                response.append(
                    {
                        'message': 'User has been blocked'
                    }
                )
            else:
                # block user is a friend of user requester and not blocked
                # block user is removed from user requester's friend list and block user's friendlist removed user requester
                try:
                    # the block user is not a friend of the user requester but requester is a friend.
                    models.Friend.objects.get(friend_list=user_block_request_friendList, friend=user_requester_username)
                except:
                    former_friend = models.Friend.objects.get(friend_list=user_requester_friendList, friend=user_block_request)
                    former_friend.delete()
                    models.BlockedUser.objects.create(blocked_list=user_requester_blockedList, blocked_user=user_block_request)
                    response.append({
                        'message': 'user was never a friend anyway, user is now blocked.'
                    })
                else:
                    former_friend = models.Friend.objects.get(friend_list=user_requester_friendList, friend=user_block_request)
                    former_friend.delete()
                    user_block_friend = models.Friend.objects.get(friend_list=user_block_request_friendList, friend=user_requester_username)
                    user_block_friend.delete()
                    models.BlockedUser.objects.create(blocked_list=user_requester_blockedList, blocked_user=user_block_request)
                    response.append(
                        {
                            'message': 'Friend removed and user blocked'
                        }
                    )
        else:
            response.append({
                'message': 'User already blocked'
            })

        return Response(response)

class FriendListViewSet(viewsets.ModelViewSet):
    """Handles creating and updating Friend list"""
    serializer_class = serializers.FriendListSerializer
    queryset = models.FriendList.objects.all()

class FriendViewSet(viewsets.ModelViewSet):
    """Handles creating and updating Friend list"""
    serializer_class = serializers.FriendSerializer
    queryset = models.Friend.objects.all()

    def list(self, request):
        """Handles displaying all friend models attached to friendlist's model linked to the requester"""
        user_requester_username = request.headers['username']
        user_requester = User.objects.get(username=user_requester_username)
        user_requester_friendList = models.FriendList.objects.get(user=user_requester)

        all_friendList = []

        try:
            models.Friend.objects.get(friend_list=user_requester_friendList)
        except:
            all_friendList.append({
                'message': 'Empty'
            })
        else:
            print("hello")
            for friend in models.Friend.objects.get(blocked_list=user_requester_friendList):
                all_friendList.append({
                    'friend': friend.friend,
                    'friend_status': friend.friend_status
                })
        
        return Response(all_friendList)
    
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
