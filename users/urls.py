from django.urls import path
from .views import UserSignupView, UserLoginView,UserSearchView,FriendListView,FriendRequestView,PendingFriendRequestsView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('search/', UserSearchView.as_view(), name='user-search'),
    path('friend-requests/', FriendRequestView.as_view(), name='friend-requests'),
    path('friend-requests/<int:pk>/', FriendRequestView.as_view(), name='friend-request-action'),
    path('friends/', FriendListView.as_view(), name='friends'),
    path('pending-requests/', PendingFriendRequestsView.as_view(), name='pending-requests'),
]


