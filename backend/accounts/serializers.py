from rest_framework import serializers
from django.contrib.auth.models import User
from .models import RecentlyViewed
from products.serializers import ProductSerializer


class RegisterSerializer(serializers.ModelSerializer):
    # Extra fields not on the default User model
    phone = serializers.CharField(max_length=20, write_only=True, required=False)
    password = serializers.CharField(write_only=True, min_length=6)

    class Meta:
        model = User
        fields = ["id", "first_name", "email", "username", "password", "phone"]

    def create(self, validated_data):
        # Remove phone — we'll store it in the profile extension if needed
        validated_data.pop("phone", None)
        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)  # hashes the password properly
        user.save()
        return user


class UserProfileSerializer(serializers.ModelSerializer):
    """Used for GET /profile/ and PATCH /profile/"""
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "email", "username", "date_joined"]
        read_only_fields = ["id", "username", "date_joined"]


class RecentlyViewedSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = RecentlyViewed
        fields = ["id", "product", "viewed_at"]