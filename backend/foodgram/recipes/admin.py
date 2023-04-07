from django.contrib import admin

from users.admin import StaffRequired
from recipes.models import (Ingredient, IngredientAmount, Recipe, Subscription,
                            Tag)


class InrgedientQuantityInline(admin.TabularInline):
    model = IngredientAmount
    fields = ('ingredient', 'amount')
    extra = 0
    verbose_name = 'Ингредиент'


class RecipeAdmin(StaffRequired, admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('author', 'tags',)
    filter_horizontal = ('tags',)
    inlines = (InrgedientQuantityInline,)
    readonly_fields = ('favorite_count',)

    @admin.display(description='Число добавлений в избранное')
    def favorite_count(self, instance):
        return instance.favorited.count()


class IngredientAdmin(StaffRequired, admin.ModelAdmin):
    fields = ('name', 'measurement_unit')
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(StaffRequired, admin.ModelAdmin):
    list_display = ('colored_name', 'slug')
    fileds = ('name', 'color')


admin.site.register(Subscription)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
