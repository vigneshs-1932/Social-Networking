from rest_framework import serializers
from .models import User,FriendRequest

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'name')

class UserSignupSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('email', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'from_user', 'to_user', 'status', 'created_at')

class FriendRequestActionSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('status',)
