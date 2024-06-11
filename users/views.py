from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User,FriendRequest
from .serializers import UserSignupSerializer, UserSerializer
from rest_framework import generics, filters
from django_filters.rest_framework import DjangoFilterBackend
from .models import User
from .serializers import UserSerializer
from rest_framework import status
from rest_framework.views import APIView
from .serializers import FriendRequestSerializer, FriendRequestActionSerializer

class UserSignupView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSignupSerializer
    permission_classes = (permissions.AllowAny,)

class UserLoginView(generics.GenericAPIView):
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        email = request.data.get('email').lower()
        password = request.data.get('password')
        user = User.objects.filter(email=email).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        return Response({"error": "Invalid credentials"}, status=400)


class UserSearchView(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [filters.SearchFilter]
    search_fields = ['email', 'name']
    permission_classes = (permissions.IsAuthenticated,)


class FriendRequestView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request):
        from_user = request.user
        to_user_id = request.data.get('to_user')
        to_user = User.objects.get(id=to_user_id)
        if FriendRequest.objects.filter(from_user=from_user, to_user=to_user, status='pending').exists():
            return Response({"error": "Friend request already sent"}, status=status.HTTP_400_BAD_REQUEST)
        friend_request = FriendRequest.objects.create(from_user=from_user, to_user=to_user)
        return Response(FriendRequestSerializer(friend_request).data, status=status.HTTP_201_CREATED)

    def put(self, request, pk):
        try:
            friend_request = FriendRequest.objects.get(id=pk)
        except FriendRequest.DoesNotExist:
            return Response({"error": "Invalid Friend Request"}, status=status.HTTP_404_NOT_FOUND)
        if friend_request.to_user != request.user:
            return Response({"error": "Not authorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer = FriendRequestActionSerializer(friend_request, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


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

class PendingFriendRequestsView(generics.ListAPIView):
    serializer_class = FriendRequestSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        user = self.request.user
        return FriendRequest.objects.filter(to_user=user, status='pending')
