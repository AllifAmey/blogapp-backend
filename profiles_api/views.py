from tkinter import E
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
        # this is used for user's online.
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
                    # return friend_status_val will be used to filter who is a friend and who has a friend request.
                    friend = models.Friend.objects.get(friend_list=user_requester_friendList, friend=user.username)
                    friend_status_val = getattr(friend, "friend_status")
                    user_status_toRequester = friend_status_val
                    
                
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

        blockedList = models.BlockedUser.objects.filter(blocked_list=user_requester_blockList)

        blockedList_len = blockedList.count()

        if blockedList_len == 0:
            all_blockedUsers.append({
                'message': 'You have no blocked users'
            })
        else:
            for blockedUser in blockedList:
                all_blockedUsers.append({
                    'blockedUser': blockedUser.blocked_user
                })
        return Response(all_blockedUsers)

    def create(self, request):
        """Handles creating new block models"""
        # expected Json file {'username': requester_username, 'block user': block_username} 
        user_block_request = request.data.get('block user')
        user_block = User.objects.get(username=user_block_request)
        user_block_request_friendList = models.FriendList.objects.get(user=user_block)

        user_requester_username = request.data.get('username')
        user_requester = User.objects.get(username=user_requester_username)
        user_requester_friendList = models.FriendList.objects.get(user=user_requester)
        user_requester_blockedList = models.BlockedList.objects.get(user=user_requester)

        response = []

        try:
            # check if the user requesting a block already has the user they're requesting blocked already
            models.BlockedUser.objects.get(blocked_list=user_requester_blockedList, blocked_user=user_block_request)
        except:
            try:
                # check if both the user requesting the block and the user to be blocked a friend of each other.
                models.Friend.objects.get(friend_list=user_requester_friendList, friend__exact=user_block_request)
                models.Friend.objects.get(friend_list=user_block_request_friendList, friend__exact=user_requester_username)
            except:
                # this means either the blocked user is a friend of user requesting the block, 
                # and user requesting the block is not a friend of the blocked user
                # or vice versa. 
                # Check which friend model is causing the issue.
                try:
                    # the user the requester wants blocked is a friend of the requester.
                    # delete that model if true and create blockUserModel to the user that the requester wants blocked.
                    models.Friend.objects.get(friend_list=user_block_request_friendList, friend=user_requester_username)
                except:
                    try: 
                        # checks if the user that the request wants blocked is on the requester's friendlist.
                        models.Friend.objects.get(friend_list=user_requester_friendList, friend=user_block_request)
                    except:
                        # this means both users don't have a friendModel for each other.
                        models.BlockedUser.objects.create(blocked_list=user_requester_blockedList, blocked_user=user_block_request)
                        response.append(
                            {
                                'message': 'User has been blocked'
                            }
                        )
                    else:
                        former_friend = models.Friend.objects.get(friend_list=user_requester_friendList, friend=user_block_request)
                        former_friend.delete()
                        models.BlockedUser.objects.create(blocked_list=user_requester_blockedList, blocked_user=user_block_request)
                        response.append({
                            'message': f'{user_block_request} is removed from your friendlist. User is now blocked.'
                        })
                else:
                    user_requester_friend = models.Friend.objects.get(friend_list=user_block_request_friendList, friend=user_requester_username)
                    user_requester_friend.delete()
                    models.BlockedUser.objects.create(blocked_list=user_requester_blockedList, blocked_user=user_block_request)
                    response.append(
                        {
                            'message': f'Your friendship was removed from {user_block_request}\'s friendslist. User now Blocked.'
                        }
                    )
            else:
                # this means each user is a friend of each other. Destroy both friendModels,
                # and add BlockedUserModel to the user that the user requester wants blocked.
                former_friend = models.Friend.objects.get(friend_list=user_requester_friendList, friend=user_block_request)
                former_friend.delete()
                user_block_friend = models.Friend.objects.get(friend_list=user_block_request_friendList, friend=user_requester_username)
                user_block_friend.delete()
                models.BlockedUser.objects.create(blocked_list=user_requester_blockedList, blocked_user=user_block_request)
                response.append(
                    {
                        'message': 'Both friends removed and user now blocked'
                    }
                )
        else:
            response.append({
                'message': 'User already blocked'
            })

        return Response(response)

    def destroy(self, request):
        """Handles unblocking people. """

        #expected Json file is {'username': user_request_unblock, 'unblock user}

        user_request_unblock_username = request.data.get('username')
        user_unblock_username = request.data.get('unblock user')

        user_request = User.objects.get(username=user_request_unblock_username)
        user_unblock = User.objects.get(username=user_unblock_username)

        user_request_blockList = models.BlockedList.get(user=user_request)
        
        response = []

        try:
            models.BlockedUser.get(block_list=user_request_blockList)
        except:
            response.append(
                {
                    'message': f'{user_unblock_username} is not on your blockList'
                }
                )
        else:
            unblock_user = models.BlockedUser.get(block_list=user_request_blockList)
            unblock_user.delete()


        return Response(response)

class getFriendBlockedApiView(APIView):
    """Simple api that gets id of Friend and block models"""

    def post(self,request):
        """Handles displaying ids of Friend or block models"""
        # expected JSON {'type': model_type, 'username': user_requester, 'target user': user_target}
        # note this api will only be called when a model has already been established.
        user_1_username = request.data.get('username')
        user_2_username = request.data.get('target user')
        user_1 = User.objects.get(username=user_1_username)
        user_2 = User.objects.get(username=user_2_username)
        user_1_friendList = models.FriendList.objects.get(user=user_1)
        user_2_friendList = models.FriendList.objects.get(user=user_2)
        user_1_blockList = models.BlockedList.objects.get(user=user_1)
        user_2_blockList = models.BlockedList.objects.get(user=user_2)
        model_type = request.data.get('type')

        response = []
        if model_type == "friend":
            #return friend model idea of both users
            try:
                #check if there are both models.
                user_1_friend = models.Friend.objects.get(friend_list=user_2_friendList, friend=user_1_username)
                user_2_friend = models.Friend.objects.get(friend_list=user_1_friendList, friend=user_2_username)
            except:
                try:
                    # check if there is one model
                    user_1_friend = models.Friend.objects.get(friend_list=user_2_friendList, friend=user_1_username)
                except:
                    try:
                        # check if the other model exist
                        user_2_friend = models.Friend.objects.get(friend_list=user_1_friendList, friend=user_2_username)
                    except:
                        # no model exist respond with no model exist
                        response.append(
                            {
                                'message':f'No {model_type} exist in {user_1_username} or {user_2_username}'
                            }
                        )
                    else:
                        {
                            'id': f'The id on {user_1_username}\'s friendList is {user_2_friend.id}'
                        }
                else:
                    {
                        'id': f'The id on {user_2_username}\'s friendList is {user_1_friend.id}'
                    }
            else:
                # both models exist return both ids.
                {
                    'id': f'The id on {user_2_username}\'s friendList is {user_1_friend.id}',
                    'id_2': f'The id on {user_1_username}\'s friendList is {user_2_friend.id}'
                }
        if model_type == "block":
            try:
                #check if there are both models.
                user_1_block =  models.BlockedUser.objects.get(blocked_list=user_2_blockList, blocked_user=user_1_username)
                user_2_block = models.BlockedUser.objects.get(blocked_list=user_1_blockList, blocked_user=user_2_username)
            except:
                try:# check if there is one model
                    user_1_block =  models.BlockedUser.objects.get(blocked_list=user_2_blockList, blocked_user=user_1_username)
                except:
                    try:
                        # check if the other model exist
                        user_2_block = models.BlockedUser.objects.get(blocked_list=user_1_blockList, blocked_user=user_2_username)
                    except:
                        # no model exist respond with no model exist
                        response.append(
                                {
                                    'message':f'No {model_type} exist in {user_1_username} or {user_2_username}'
                                }
                            )
                    else:
                        {
                            'id': f'The id on {user_1_username}\'s blockedList is {user_2_block.id}'
                        }
                else:
                    {
                        'id': f'The id on {user_2_username}\'s blockedList is {user_1_block.id}'
                    }
            else:
                {
                    'id': f'The id on {user_2_username}\'s blockedList is {user_1_block.id}',
                    'id_2': f'The id on {user_1_username}\'s blockedList is {user_2_block.id}'
                }
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
        friendList_len = models.Friend.objects.filter(friend_list=user_requester_friendList, friend_status__exact="friend").count()

        if friendList_len == 0:
            all_friendList.append({
                'message': 'You have no friends.'
            })
        else:
            for friend in models.Friend.objects.filter(friend_list=user_requester_friendList, friend_status__exact="friend"):
                all_friendList.append({
                    'friend': friend.friend,
                    'friend_status': friend.friend_status
                })
        return Response(all_friendList)

    def create(self, request):
        """Handles friend request"""
        # Expected Json file {'username':user_requester_username, 'friend request': user_friend_request_username}
        # user requesting
        user_requester_username = request.data.get("username")
        user_requester = User.objects.get(username=user_requester_username)
        user_requester_FriendList = models.FriendList.objects.get(user=user_requester)
        user_requester_blockedList = models.BlockedList.objects.get(user=user_requester)
        # user that is recieving a friend request
        user_friend_request_username = request.data.get('friend request')
        user_friend_request = User.objects.get(username=user_friend_request_username)
        user_friend_request_friendList = models.FriendList.objects.get(user=user_friend_request)
        user_friend_request_blockedList = models.BlockedList.objects.get(user=user_friend_request)

        response = []
        try:
            #check if user_friend_request has user_requester blocked
            models.BlockedUser.objects.get(blocked_list=user_friend_request_blockedList, blocked_user=user_requester_username)
        except:
            # check if user_friend_request is already a friend model. 
            try:
                models.Friend.objects.get(friend_list=user_friend_request_friendList, friend=user_requester_username, friend_status__exact="friend")
                models.Friend.objects.get(friend_list=user_requester_FriendList, friend=user_friend_request_username, friend_status__exact="friend")
            except:
                try:
                    # check if friend request already sent.
                    models.Friend.objects.get(
                        friend_list=user_friend_request_friendList, 
                        friend=user_requester_username, 
                        friend_status__exact="request")
                except:
                    # check if user_requester has user_friend_request blocked and if so remove them from block list, create friend request.
                    try:
                        models.BlockedUser.objects.get(blocked_list=user_requester_blockedList, blocked_user=user_friend_request_username)
                    except:
                        # both users are not on each other's blocked list and both are not friends yet.
                        models.Friend.objects.create(
                            friend_list=user_friend_request_friendList, 
                            friend=user_requester_username,
                            friend_status="request")
                        
                        response.append(
                            {
                                'message': f'Friend request sent to {user_friend_request_username}!'
                            }
                            )
                    else:
                        user_friend_request_blockedUser = models.BlockedUser.objects.get(blocked_list=user_requester_blockedList, blocked_user=user_friend_request_username)
                        user_friend_request_blockedUser.delete()
                        models.Friend.objects.create(
                            friend_list=user_friend_request_friendList, 
                            friend=user_requester_username,
                            friend_status="request")
                        response.append(
                            {
                                'message': f'Friend request sent to {user_friend_request_username}and {user_friend_request_username} was removed from block list!'
                            }
                            )
                else:
                    response.append(
                        {
                            'message': 'You already sent a friend request before'
                        }
                        )

            else:
                response.append(
                    {
                        'message': 'You\'re already friends with each other'
                    }
                )
        else:
            response.append(
                {
                    'message': f'You\'re blocked you can\'t add {user_friend_request_username} as friend'
                }
            )

        return Response(response)
    
    def partial_update(self, request):
        """Handles updating friend_status field in friend model to friend"""
        # 'friend_accepter is basically 
        # expected Json file {'username': friend_accepter_usernamer' : 'friend_requester': friend_requester_username}
        friend_accepter_username = request.data.get('username')
        friend_requester_username = request.data.get('friend_requester')
        friend_accepter_user = User.objects.get(username=friend_accepter_username)
        friend_requester_user = User.objects.get(username=friend_requester_username)
        # both friend list will be used to create Friend
        friend_accepter_friendList = models.FriendList.objects.get(user=friend_accepter_user)
        friend_requester_friendList = models.FriendList.objects.get(user=friend_requester_user)
        #update friend model tied to friend_requester from 'request' to 'friend'
        update_friend_status = models.Friend.objects.get(
            friend_list=friend_accepter_friendList, 
            friend=friend_requester_username,
            friend_status__exact="request")
        update_friend_status.friend_status = "friend"
        update_friend_status.save()
        #create friend model tied to the friend_accepter
        models.Friend.objects.create(friend_list=friend_requester_friendList, friend=friend_accepter_username, friend_status="friend")


        return Response(
            {
                'message': f'{friend_requester_username}\'s friend request accepted!'
            }
            )

    def destroy(self, request):
        """Handles unfriending users"""
        #expected Json file {'username': user_request, 'former_friend': 'friend_username'}
        former_friend_username = request.data.get('username')
        friend_destroyer_username = request.data.get('former_friend')
        friend_friend_user = User.objects.get(username=former_friend_username)
        friend_destroyer_user = User.objects.get(username=friend_destroyer_username)
        former_friend_user_friendList = models.FriendList.objects.get(user=friend_friend_user)
        friend_destroy_user_friendList = models.FriendList.objects.get(user=friend_destroyer_user)

        response = []
        
        try:
            # check if both users have friend models of each other.
            friend_destroyer_friendModel = models.Friend.objects.get(
            friend_list=former_friend_user_friendList, 
            friend__exact=friend_destroyer_username)
            former_friend_friendModel = models.Friend.objects.get(
            friend_list=friend_destroy_user_friendList,
            friend__exact=former_friend_username)
        except:
            # find which friend model is causing an issue
            try:
                friend_destroyer_friendModel = models.Friend.objects.get(
                friend_list=former_friend_user_friendList, 
                friend__exact=friend_destroyer_username)
            except:
                # this means former friend is the issue and their friendmodel is not there.
                response.append({
                    'error_message': 'The user you tried to unfriend does not have you as a friend'
                })
            else:
                # this means friend that wants to destroy friendship (friend_destroyer) does not have to,
                # friendmodel to former friend friendlist
                response.append({
                    'error_message': 'You are not a friend of user and can not unfriend a friend that does not exist'
                })
        else:
            # this means both have friend models of each other in their respective friendlist model
            # delete both to unfriend them.
            friend_destroyer_friendModel = models.Friend.objects.get(
                friend_list=former_friend_user_friendList, 
                friend__exact=friend_destroyer_username)
            former_friend_friendModel = models.Friend.objects.get(
                friend_list=friend_destroy_user_friendList,
                friend__exact=former_friend_username)
            friend_destroyer_friendModel.delete()
            former_friend_friendModel.delete()
            response.append({
                'messsage': 'User has been successfully unfriended'
            })

        return Response(response)

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
