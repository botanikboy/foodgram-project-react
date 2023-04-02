from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.mixins import (DestroyModelMixin, CreateModelMixin,
                                   ListModelMixin)
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404

from recipes.models import Ingredient, Recipe, Subscription, Tag
from users.models import User
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeCreateSerializer, SubscriptionSerialiser,
                          TagSerializer)
from .permissions import (AdminPermission, SubscriptionPermission,
                          IsAuthorOrAdmin)
from .filters import InrgedientFilter, RecipeFilter


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminPermission,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (
        IsAuthenticatedOrReadOnly,
        IsAuthorOrAdmin,
    )
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.action in ['update', 'partial_update', 'create']:
            return RecipeCreateSerializer
        return RecipeSerializer

    def perform_create(self, serializer):
        current_user = self.request.user
        return serializer.save(author=current_user)

    def perform_update(self, serializer):
        current_user = self.request.user
        return serializer.save(author=current_user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        instance_serializer = RecipeSerializer(
            instance, context={'request': request})
        return Response(instance_serializer.data)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         instance=self.get_object(),)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_update(serializer)
        instance_serializer = RecipeSerializer(
            instance, context={'request': request})
        return Response(instance_serializer.data)


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AdminPermission)
    filter_backends = [DjangoFilterBackend]
    filterset_class = InrgedientFilter


class SubscriptionsListViewSet(GenericViewSet, ListModelMixin):
    serializer_class = SubscriptionSerialiser
    permission_classes = (SubscriptionPermission,)

    def get_queryset(self):
        current_user = self.request.user
        return Subscription.objects.filter(subscriber=current_user)


class SubscriprionCreateDestroyViewSet(GenericViewSet,
                                       CreateModelMixin,
                                       DestroyModelMixin):
    serializer_class = SubscriptionSerialiser
    permission_classes = (SubscriptionPermission,)

    def get_object(self):
        current_user = self.request.user
        author = get_object_or_404(User, pk=self.kwargs.get('author_id'))
        return get_object_or_404(
            Subscription, subscriber=current_user, author=author)

    def perform_create(self, serializer):
        current_user = self.request.user
        author = get_object_or_404(User, pk=self.kwargs.get('author_id'))
        return serializer.save(subscriber=current_user, author=author)

    def delete(self, request, *args, **kwargs):
        return self.destroy(request, *args, **kwargs)
