from django.contrib import admin

from users.models import User


class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email')
    search_fields = ('name', 'email')
    filter_horizontal = ('favorites', 'shopping_cart')

admin.site.register(User, UserAdmin)
