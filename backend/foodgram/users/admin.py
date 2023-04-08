from django.contrib import admin

from users.models import Subscription, User


class UserAdmin(admin.ModelAdmin):
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

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(User, UserAdmin)
admin.site.register(Subscription)
