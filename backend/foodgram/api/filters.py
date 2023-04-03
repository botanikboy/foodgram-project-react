from django_filters import rest_framework as filters
from recipes.models import Ingredient, Recipe
from users.models import User


class RecipeFilter(filters.FilterSet):
    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')
    author = filters.ModelChoiceFilter(queryset=User.objects)
    is_favorited = filters.BooleanFilter(field_name='favorited', )
    # is_in_shopping_cart = filters.BooleanFilter(field_name='favorited', )

    class Meta:
        model = Recipe
        fields = ['name', 'author']


class InrgedientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
