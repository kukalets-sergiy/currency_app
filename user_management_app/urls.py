from django.urls import path

from user_management_app.views import CreateUserView, LoginView

app_name = "user_management_app"

urlpatterns = [
    path("register/", CreateUserView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
]
