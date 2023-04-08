from django.contrib import admin

from recipes.models import Ingredient, IngredientAmount, Recipe, Tag


class InrgedientQuantityInline(admin.TabularInline):
    model = IngredientAmount
    fields = ('ingredient', 'amount')
    extra = 0
    verbose_name = 'Ингредиент'


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    search_fields = ('name',)
    list_filter = ('author', 'tags',)
    filter_horizontal = ('tags',)
    inlines = (InrgedientQuantityInline,)
    readonly_fields = ('favorite_count',)

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True

    @admin.display(description='Число добавлений в избранное')
    def favorite_count(self, instance):
        return instance.favorited.count()


class IngredientAdmin(admin.ModelAdmin):
    fields = ('name', 'measurement_unit')
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    fileds = ('name', 'color')

    def has_add_permission(self, request):
        return True

    def has_change_permission(self, request, obj=None):
        return True

    def has_module_permission(self, request):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Tag, TagAdmin)
