from django.urls import path
from .views import UserSignupView, UserLoginView,UserSearchView,FriendListView,FriendRequestView,PendingFriendRequestsView

"""
Defines the URL patterns for the user-related views in the Social Networking application.

The following URL patterns are defined:
- 'signup/': Handles user signup.
- 'login/': Handles user login.
- 'search/': Handles searching for users.
- 'friend-requests/': Handles creating and managing friend requests.
- 'friend-requests/<int:pk>/': Handles taking action on a specific friend request.
- 'friends/': Handles displaying the user's friends.
- 'pending-requests/': Handles displaying the user's pending friend requests.
"""
urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-requests/', FriendRequestView.as_view(), name='friend-requests'),
    path('friend-requests/<int:pk>/', FriendRequestView.as_view(), name='friend-request-action'),
    path('friends/', FriendListView.as_view(), name='friends'),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending-requests'),
]


