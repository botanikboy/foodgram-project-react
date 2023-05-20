from django.db.models import Sum
from django.http import FileResponse, HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet as DjoserUserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .filters import InrgedientFilter, RecipeFilter
from .permissions import IsAdmin, IsAuthorIsAdminOrReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer)
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.models import Subscription


class TagViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (IsAdmin,)
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorIsAdminOrReadOnly,)
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

    def perform_destroy(self, instance):
        instance.image.delete()
        return super().perform_destroy(instance)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        current_user = self.request.user
        if recipe in current_user.shopping_cart.all():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Рецепт уже в списке покупок.'})
        current_user.shopping_cart.add(recipe)
        serializer = RecipeListSerializer(recipe)
        return Response(serializer.data)

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        recipe = self.get_object()
        current_user = self.request.user
        if recipe not in current_user.shopping_cart.all():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Этого рецепта нет в списке покупок.'})
        current_user.shopping_cart.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def download_shopping_cart(self, request):
        recipes_in_cart = self.request.user.shopping_cart.values('id')
        amounts_in_cart = (IngredientAmount.objects.filter(
            recipe__in=recipes_in_cart)
            .values('ingredient__name', 'ingredient__measurement_unit')
            .annotate(total_amount=Sum('amount'))
            .order_by('ingredient__name'))

        user = self.request.user
        filename = f'{user.username}_shopping_list.txt'
        shopping_list = [
            f'Список покупок для:\n\n{user.first_name}\n'
        ]

        for ingredient in amounts_in_cart:
            shopping_list.append(
                f'{ingredient["ingredient__name"].capitalize()} ('
                f'{ingredient["ingredient__measurement_unit"]}) - '
                f'{ingredient["total_amount"]}\n'
            )
        shopping_list = '\n'.join(shopping_list)
        response = HttpResponse(
            shopping_list, content_type='text.txt; charset=utf-8'
        )
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def favorite(self, request, pk=None):
        recipe = self.get_object()
        current_user = self.request.user
        if recipe in current_user.favorites.all():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Рецепт уже в избранном.'})
        current_user.favorites.add(recipe)
        serializer = RecipeListSerializer(recipe)
        return Response(serializer.data)

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        recipe = self.get_object()
        current_user = self.request.user
        if recipe not in current_user.favorites.all():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Этого рецепта нет в избранном.'})
        current_user.favorites.remove(recipe)
        return Response(status=status.HTTP_204_NO_CONTENT)


class IngredientViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAdmin,)
    filter_backends = [DjangoFilterBackend]
    filterset_class = InrgedientFilter
    pagination_class = None


class UserViewSet(DjoserUserViewSet):
    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user_subscriptions = (
            Subscription.objects
            .filter(subscriber=request.user)
            .order_by('author__username')
        )
        page = self.paginate_queryset(user_subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                context={'request': request},
                many=True,
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            user_subscriptions,
            context={'request': request},
            many=True,
        )
        return Response(serializer.data)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = self.get_object()
        serializer = SubscriptionSerializer(
            data={'id': author.id, },
            context={'request': request}
        )
        if serializer.is_valid():
            subscription = serializer.save()
        else:
            return Response(serializer.errors)
        serializer = SubscriptionSerializer(subscription,
                                            context={'request': request})
        return Response(serializer.data)

    @subscribe.mapping.delete
    def delete_subscribe(self, request, id=None):
        author = self.get_object()
        current_user = self.request.user
        if not Subscription.objects.filter(
            subscriber=current_user,
            author=author,
        ).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Этого автора нет в подписках.'})
        Subscription.objects.filter(
            subscriber=current_user,
            author=author
        ).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
