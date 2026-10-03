from rest_framework.permissions import BasePermission


class IsAdminUserRole(BasePermission):
    """
    Allows access only to RetroDoc administrators.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role == "A"
        )


class IsOfficerOrAdmin(BasePermission):
    """
    Allows access to RetroDoc officers and administrators.
    """

    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.role in {"O", "A"}
        )