from drf_yasg.inspectors import SwaggerAutoSchema
from django.contrib.auth import get_user_model
from rest_framework.generics import CreateAPIView
from rest_framework import permissions
from rest_framework_simplejwt.views import TokenObtainPairView
from user_management_app.serializers import UserSerializer

UserModel = get_user_model()


class AuthenticationSchema(SwaggerAutoSchema):
    def get_tags(self, operation_keys: list[str] | None = None) -> list[str]:
        return ["Authentication"]


class CreateUserView(CreateAPIView):
    swagger_schema = AuthenticationSchema
    model = get_user_model()
    authentication_classes = []
    permission_classes = [permissions.AllowAny]
    serializer_class = UserSerializer


class LoginView(TokenObtainPairView):
    swagger_schema = AuthenticationSchema
