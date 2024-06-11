from rest_framework import serializers
from .models import User, FriendRequest

"""
    Serializer for the User model.
    
    This serializer is used to serialize and deserialize the User model, which represents a user of the social networking application. It includes fields for the user's ID, email, and name.
    """
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name')

"""
        Serializer for creating a new user.
    
        This serializer is used to create a new `User` instance. It includes fields for the user's email, password, and name. The `password` field is marked as `write_only` to ensure it is not returned in the serialized output. The `name` field is required.
    
        The `create` method is overridden to create the new user using the `create_user` method of the `User` model manager.
    """
class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password', 'name')
        extra_kwargs = {'password': {'write_only': True}, 'name': {'required': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
"""
        Serializer for the FriendRequest model.
    
        This serializer is used to serialize and deserialize the FriendRequest model, which represents a friend request between two users. It includes fields for the requesting user, the requested user, the status of the request, and the creation timestamp.
    """
class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'status', 'created_at')

"""
    Serializer for updating the status of a FriendRequest instance.
    
    This serializer is used to update the `status` field of a `FriendRequest` model instance. It is typically used when accepting or rejecting a friend request.
    """
class FriendRequestActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('status',)
