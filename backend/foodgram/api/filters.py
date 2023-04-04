from django_filters import rest_framework as filters
from django.db.models import Q
from recipes.models import Ingredient, Recipe
from users.models import User


class RecipeFilter(filters.FilterSet):
    def __init__(self, *args, **kwargs):
        self.user = kwargs['request'].user
        super(RecipeFilter, self).__init__(*args, **kwargs)

    tags = filters.CharFilter(field_name='tags__slug', lookup_expr='iexact')
    author = filters.ModelChoiceFilter(queryset=User.objects)
    is_favorited = filters.BooleanFilter(method='is_favorited_method')
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_method')

    class Meta:
        model = Recipe
        fields = ['name', 'author', 'is_favorited', 'is_in_shopping_cart']

    def is_favorited_method(self, queryset, name, value):
        if value is True:
            return queryset.filter(favorited=self.user)
        if value is False:
            return queryset.filter(~Q(favorited=self.user))

    def is_in_shopping_cart_method(self, queryset, name, value):
        if value is True:
            return queryset.filter(shopped=self.user)
        if value is False:
            return queryset.filter(~Q(shopped=self.user))


class InrgedientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='istartswith')

    class Meta:
        model = Ingredient
        fields = ['name']
