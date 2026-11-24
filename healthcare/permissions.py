from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsCreatorOrReadOnly(BasePermission):
    """Any authenticated user can read; only the creator can modify or delete."""

    message = "You can only modify records that you created."

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return obj.created_by_id == request.user.id
