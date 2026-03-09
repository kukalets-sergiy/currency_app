from typing import Any
from rest_framework import serializers
from django.contrib.auth import get_user_model
from user_management_app.models import UserData

UserModel = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserData
        fields = ("email", "password")

    def validate(self, data: dict[str, Any]) -> dict[str, Any]:
        if not data.get("email"):
            raise serializers.ValidationError("Email is required.")
        if not data.get("password"):
            raise serializers.ValidationError("Password is required.")
        return data

    def create(self, validated_data: dict[str, Any]) -> UserData:
        """Each created user is a superuser to simplify testing."""
        user = UserData.objects.create_superuser(
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user
