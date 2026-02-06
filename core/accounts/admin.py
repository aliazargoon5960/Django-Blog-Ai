from django.contrib import admin

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models.users import User
from .models.profiles import Profile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ["email", "role", "is_staff", "is_active", "is_verified"]
    list_filter = ["role", "is_staff", "is_active", "is_verified"]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Permissions", {"fields": ("role", "is_staff", "is_active", "is_verified", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login",)}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "password1", "password2", "role", "is_staff", "is_active", "is_verified"),
        }),
    )

    search_fields = ("email",)
    readonly_fields = ("last_login",)

    filter_horizontal = ("groups", "user_permissions")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ["user", "first_name", "last_name", "created_date"]
    search_fields = ["user__email", "first_name", "last_name"]
