from rest_framework.permissions import BasePermission

class IsAdminOrAuthor(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.user.is_superuser:
            return True
        return obj.created_by == request.user