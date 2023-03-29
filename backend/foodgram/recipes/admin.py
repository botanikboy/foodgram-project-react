from django.contrib import admin
from recipes.models import (Ingredient, InrgedientAmount, Recipe,
                            Subscription, Tag)


class InrgedientQuantityInline(admin.TabularInline):
    model = InrgedientAmount
    fields = ('ingredient', 'amount')
    extra = 1
    verbose_name = 'Ингредиент'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('author', 'tags',)
    filter_horizontal = ('tags',)
    inlines = (InrgedientQuantityInline,)


class IngredientAdmin(admin.ModelAdmin):
    fields = ('name', 'measurement_unit')
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)


class TagAdmin(admin.ModelAdmin):
    list_display = ('colored_name', 'slug')
    fileds = ('name', 'color')


admin.site.register(Subscription)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
