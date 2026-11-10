from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    message = 'Змінювати ці дані може лише адміністратор.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_staff)


class IssuePermission(BasePermission):
    message = 'Видаляти задачі може лише адміністратор.'

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        if not request.user or not request.user.is_authenticated:
            return False
        if request.method == 'DELETE':
            return request.user.is_staff
        return True
