from rest_framework.permissions import BasePermission, SAFE_METHODS


class AdminPermission(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user.groups.filter(name='Administrators').exists()

class SubscriptionPermission(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        return obj.subscriber == request.user