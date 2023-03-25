from django.contrib import admin
from recipes.models import (Ingredient, InrgedientQuantity, Recipe,
                            Subscription, Tag)


class InrgedientQuantityInline(admin.TabularInline):
    model = InrgedientQuantity
    fields = ('ingredient', 'quantity')
    extra = 1
    verbose_name = 'Ингредиент'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('author', 'tags',)
    inlines = (InrgedientQuantityInline,)


class IngredientAdmin(admin.ModelAdmin):
    fields = ('name', 'measurement_unit')
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('colored', 'slug')


admin.site.register(Subscription)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
