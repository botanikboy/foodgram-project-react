from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
from django_filters.rest_framework import DjangoFilterBackend

from recipes.models import Ingredient, Recipe, Subscription, Tag
from .serializers import (IngredientSerializer, RecipeSerializer,
                          SubscriptionSerialiser, TagSerializer)
from .permissions import AdminPermission
from .filters import InrgedientFilter, RecipeFilter


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminPermission,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AdminPermission)
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AdminPermission)
    filter_backends = [DjangoFilterBackend]
    filterset_class = InrgedientFilter


class SubscriptionViewSet(ModelViewSet):
    serializer_class = SubscriptionSerialiser
    permission_classes = (IsAuthenticated, AdminPermission)

    def get_queryset(self):
        current_user = self.request.user
        return Subscription.objects.filter(subscriber=current_user)
