from django.urls import path, include

from rest_framework.routers import DefaultRouter

from profiles_api import views 

router = DefaultRouter()
router.register('register-viewset', views.RegisterViewSet)
router.register('userblog-viewset', views.UserBlogViewSet)
router.register('profilesetting-viewset', views.UserProfileSettingViewSet)
router.register('friendlist-viewset', views.FriendListViewSet)
router.register('friend-viewset', views.FriendViewSet)
router.register('blockedlist-viewset', views.BlockedListViewSet)
router.register('blockeduser-viewset', views.BlockedUserViewSet)

urlpatterns = [
	path('', include(router.urls)),
	path('signup/', views.UserSignUpApiView.as_view()),
	path('auth/login/', views.UserLoginApiView.as_view()),
	path('grab/id/', views.getFriendBlockedApiView.as_view())
]