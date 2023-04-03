from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('username', 'email')
    filter_horizontal = ('favorites', 'shopping_cart', 'groups')


admin.site.register(User, UserAdmin)
