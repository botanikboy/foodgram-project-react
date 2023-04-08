from django.contrib import admin

from users.models import User, Subscription


class StaffRequired(object):

    def check_perm(self, user_obj):
        if not user_obj.is_active or user_obj.is_anonymous:
            return False
        if user_obj.is_superuser or user_obj.is_staff:
            return True
        return False

    def has_view_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_module_permission(self, request):
        return self.check_perm(request.user)

    def has_add_permission(self, request):
        return self.check_perm(request.user)

    def has_change_permission(self, request, obj=None):
        return self.check_perm(request.user)

    def has_delete_permission(self, request, obj=None):
        return self.check_perm(request.user)


class UserAdmin(StaffRequired, admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')
    filter_horizontal = ('favorites', 'shopping_cart')
    fields = (
        'first_name',
        'last_name',
        'username',
        'email',
        'favorites',
        'shopping_cart',
        'is_staff',
        'is_active',
        'password',
    )


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
