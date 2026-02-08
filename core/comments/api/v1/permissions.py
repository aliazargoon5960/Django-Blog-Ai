from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsOwnerOrAdminOrCreate(BasePermission):
    def has_permission(self, request, view):
        if request.method == "POST":
            return request.user.is_authenticated
        if request.method in SAFE_METHODS:
            return True
        return True  

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return (
            request.user.is_authenticated
            and (
                obj.author.user == request.user
                or request.user.role == "ADMIN"
            )
        )

