from rest_framework import permissions


def is_admin_user(user):
    return bool(user and user.is_authenticated and (user.is_superuser or user.role == "ADMIN"))


def is_manager_user(user):
    return bool(user and user.is_authenticated and user.role == "MANAGER")


def is_customer_user(user):
    return bool(user and user.is_authenticated and user.role == "CUSTOMER")


class IsAdmin(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_admin_user(request.user)


class IsManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_manager_user(request.user)


class IsCustomer(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_customer_user(request.user)


class IsAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return is_admin_user(request.user) or is_manager_user(request.user)


class IsOwnerOrAdmin(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if is_admin_user(request.user):
            return True
        owner = getattr(obj, "user", None)
        return owner == request.user


class IsOwnerOrAdminOrManager(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        if is_admin_user(request.user) or is_manager_user(request.user):
            return True
        owner = getattr(obj, "user", None)
        return owner == request.user


class IsAuthenticatedOrReadOnlyForCatalog(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return is_admin_user(request.user) or is_manager_user(request.user)
