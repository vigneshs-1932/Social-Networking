from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User, FriendRequest
from .serializers import UserSignupSerializer, UserSerializer, FriendRequestSerializer, FriendRequestActionSerializer
from rest_framework import filters
from rest_framework.views import APIView

"""
    Generates a common response dictionary with the given success status, data, and error.
    
    Args:
        success (bool): Indicates whether the operation was successful or not.
        data (dict, optional): The data to be included in the response.
        error (str, optional): The error message to be included in the response.
    
    Returns:
        dict: A dictionary containing the success status, data, and error.
    """
def common_response(success, data=None, error=None):
        return {
        "success": success,
        "data": data,
        "error": error
    }

"""
    Provides an API endpoint for user signup.
    
    This view handles the creation of new user accounts. It uses the `UserSignupSerializer` to validate and create the new user.
    
    Args:
        request (Request): The HTTP request object containing the user signup data.
    
    Returns:
        Response: A response containing the success status, created user data, and any errors.
    """
class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(common_response(True, serializer.data), status=status.HTTP_201_CREATED, headers=headers)

"""
    Provides an API endpoint for user login.
    
    This view handles the authentication of users. It uses the `UserSerializer` to validate the user's email and password, and returns a refresh and access token if the credentials are valid.
    
    Args:
        request (Request): The HTTP request object containing the user's email and password.
    
    Returns:
        Response: A response containing the success status, refresh and access tokens, and any errors.
    """
class UserLoginView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email').lower()
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response(common_response(True, {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }))
        return Response(common_response(False, error="Invalid credentials"), status=status.HTTP_400_BAD_REQUEST)

"""
        Provides an API endpoint for searching and listing users.
    
        This view allows authenticated users to search for other users by email or name. It excludes the current user from the search results and paginates the response.
    
        Args:
            request (Request): The HTTP request object containing the search query.
    
        Returns:
            Response: A paginated response containing the list of matching users.
        """
class UserSearchView(generics.ListAPIView):
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'name']
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return User.objects.exclude(id=user.id)

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        if not queryset.exists():
            return Response(common_response(True, data=[], error="No users found"), status=status.HTTP_200_OK)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(common_response(True, serializer.data))

        serializer = self.get_serializer(queryset, many=True)
        return Response(common_response(True, serializer.data))

"""
    Provides an API endpoint for sending and managing friend requests.
    
    This view allows authenticated users to send friend requests to other users, and to accept or reject pending friend requests.
    
    Args:
        request (Request): The HTTP request object containing the friend request data.
        pk (int): The ID of the friend request to be updated.
    
    Returns:
        Response: A response indicating the success or failure of the friend request operation.
    """
class FriendRequestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        from_user = request.user
        to_user_id = request.data.get('to_user')
        if from_user.id == to_user_id:
            return Response(common_response(False, error="Cannot send friend request to yourself"), status=status.HTTP_400_BAD_REQUEST)
        
        try:
            to_user = User.objects.get(id=to_user_id)
            if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status='pending').exists():
                return Response(common_response(False, error="Friend request already sent"), status=status.HTTP_400_BAD_REQUEST)
            friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
            return Response(common_response(True, FriendRequestSerializer(friend_request).data), status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            return Response(common_response(False, error="User does not exist"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(common_response(False, error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, pk):
        try:
            friend_request = FriendRequest.objects.get(id=pk)
            if friend_request.to_user != request.user:
                return Response(common_response(False, error="Not authorized"), status=status.HTTP_403_FORBIDDEN)
            serializer = FriendRequestActionSerializer(friend_request, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(common_response(True, serializer.data))
            return Response(common_response(False, error=serializer.errors), status=status.HTTP_400_BAD_REQUEST)
        except FriendRequest.DoesNotExist:
            return Response(common_response(False, error="Invalid Friend Request"), status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response(common_response(False, error=str(e)), status=status.HTTP_500_INTERNAL_SERVER_ERROR)

"""
        Provides an API endpoint for retrieving a list of a user's friends.
    
        This view allows authenticated users to retrieve a list of their friends. The list includes users that the authenticated user has sent a friend request to and had it accepted, as well as users that have sent the authenticated user a friend request and had it accepted.
    
        Args:
            request (Request): The HTTP request object.
    
        Returns:
            Response: A response containing a list of the authenticated user's friends.
        """
class FriendListView(generics.ListAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        friends = User.objects.filter(
            id__in=FriendRequest.objects.filter(
                from_user=user, status='accepted'
            ).values_list('to_user', flat=True)
        ) | User.objects.filter(
            id__in=FriendRequest.objects.filter(
                to_user=user, status='accepted'
            ).values_list('from_user', flat=True)
        )
        return friends

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(common_response(True, serializer.data))

"""
            Provides an API endpoint for retrieving a list of a user's pending friend requests.
    
            This view allows authenticated users to retrieve a list of their pending friend requests. The list includes users that have sent the authenticated user a friend request, but the request has not been accepted or rejected yet.
    
            Args:
                request (Request): The HTTP request object.
    
            Returns:
                Response: A response containing a list of the authenticated user's pending friend requests.
            """
class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(to_user=user, status='pending')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(common_response(True, serializer.data))
