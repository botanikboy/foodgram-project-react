from django.contrib import admin

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.admin import StaffRequired


class InrgedientQuantityInline(admin.TabularInline):
    model = IngredientAmount
    fields = ('ingredient', 'amount')
    extra = 1
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
    list_display = ('name', 'slug')
    fileds = ('name', 'color')


class IngredientAmountAdmin(StaffRequired, admin.ModelAdmin):
    list_display = ('ingredient', 'recipe')


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(IngredientAmount, IngredientAmountAdmin)
