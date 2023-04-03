from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import (IsAuthenticatedOrReadOnly,
                                        IsAuthenticated)
# from rest_framework.mixins import (DestroyModelMixin, CreateModelMixin,
#                                    ListModelMixin)
from rest_framework import status
from rest_framework.decorators import action
from django_filters.rest_framework import DjangoFilterBackend
# from django.shortcuts import get_object_or_404
from django.db.models import Sum
from djoser.views import UserViewSet as DjoserUserViewSet
from django.http import FileResponse

from recipes.models import (Ingredient, Recipe, Subscription, Tag,
                            IngredientAmount)
# from users.models import User
from .serializers import (IngredientSerializer,
                          RecipeSerializer, RecipeCreateSerializer,
                          RecipeListSerializer, SubscriptionSerialiser,
                          TagSerializer)
from .permissions import (AdminPermission,
                          #   SubscriptionPermission,
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
        with open('media/shopping_cart.txt', 'w', encoding="utf-8") as f:
            for ingredient in amounts_in_cart:
                f.write(
                    f'{ingredient["ingredient__name"].capitalize()} ('
                    f'{ingredient["ingredient__measurement_unit"]}) - '
                    f'{ingredient["total_amount"]}\n'
                )
        f = open('media/shopping_cart.txt', 'rb')
        response = FileResponse(f, content_type='text/plain; charset=UTF-8')
        response['Content-Disposition'] = (
            'attachment;filename="shopping_cart.txt"')
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


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (IsAuthenticatedOrReadOnly, AdminPermission)
    filter_backends = [DjangoFilterBackend]
    filterset_class = InrgedientFilter


# class SubscriptionsListViewSet(GenericViewSet, ListModelMixin):
#     serializer_class = SubscriptionSerialiser
#     permission_classes = (SubscriptionPermission,)

#     def get_queryset(self):
#         current_user = self.request.user
#         return Subscription.objects.filter(subscriber=current_user)


# class SubscriprionCreateDestroyViewSet(GenericViewSet,
#                                        CreateModelMixin,
#                                        DestroyModelMixin):
#     serializer_class = SubscriptionSerialiser
#     permission_classes = (SubscriptionPermission,)

#     def get_object(self):
#         current_user = self.request.user
#         author = get_object_or_404(User, pk=self.kwargs.get('author_id'))
#         return get_object_or_404(
#             Subscription, subscriber=current_user, author=author)

#     def perform_create(self, serializer):
#         current_user = self.request.user
#         author = get_object_or_404(User, pk=self.kwargs.get('author_id'))
#         return serializer.save(subscriber=current_user, author=author)

#     def delete(self, request, *args, **kwargs):
#         return self.destroy(request, *args, **kwargs)


class UserViewSet(DjoserUserViewSet):
    @action(detail=False, methods=['get'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        serializer = SubscriptionSerialiser(
            Subscription.objects.filter(subscriber=self.request.user))
        return Response(serializer.data)

    @action(detail=True, methods=['post'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = self.get_object()
        current_user = self.request.user
        print(author)
        print(Subscription.objects.filter(
            subscriber=current_user, author=author).exists())
        if Subscription.objects.filter(
            subscriber=current_user,
            author=author,
        ).exists():
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={'errors': 'Уже подписан.'})
        subscription = Subscription.objects.create(
            subscriber=current_user,
            author=author
        )
        serializer = SubscriptionSerialiser(subscription,
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
