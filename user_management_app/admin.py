from django.contrib import admin

from user_management_app.models import UserData


@admin.register(UserData)
class UserDataAdmin(admin.ModelAdmin):
    list_display = (
        "email",
        "username",
        "first_name",
        "last_name",
        "is_active",
        "is_staff",
    )
    search_fields = ("email", "username", "first_name", "last_name")
    list_filter = ("is_active", "is_staff")
