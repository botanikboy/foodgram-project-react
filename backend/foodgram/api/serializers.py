import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404

from users.models import User
from recipes.models import (Ingredient, InrgedientAmount, Recipe,
                            Subscription, Tag)


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        if self.context['request'].user.is_authenticated:
            current_user = self.context['request'].user
            return Subscription.objects.filter(
                subscriber=current_user, author=obj).exists()
        return False

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = (
            'id',
            'name',
            'color',
            'slug',
        )


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngredientAmountSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = InrgedientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            data = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        return super().to_internal_value(data)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(many=False, read_only=True)
    ingredients = IngredientAmountSerializer(many=True, source='amounts')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True, allow_null=True)

    def get_is_favorited(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj in self.context['request'].user.favorites.all()
        return False

    def get_is_in_shopping_cart(self, obj):
        if self.context['request'].user.is_authenticated:
            return obj in self.context['request'].user.shopping_cart.all()
        return False

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author', 'id', 'pub_date')


class RecipeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = (
            'id',
            'name',
            'image',
            'cooking_time',
        )


class SubscriptionSerialiser(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.ReadOnlyField(source='author.id')
    username = serializers.ReadOnlyField(source='author.username')
    first_name = serializers.ReadOnlyField(source='author.first_name')
    last_name = serializers.ReadOnlyField(source='author.last_name')
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeListSerializer(many=True, read_only=True,
                                   source='author.recipes')
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    def get_is_subscribed(self, obj):
        current_user = self.context['request'].user
        return Subscription.objects.filter(
                subscriber=current_user, author=obj.author).exists()

    def validate(self, data):
        user = self.context['request'].user
        author = get_object_or_404(
            User, pk=self.context['view'].kwargs['author_id'])
        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя')
        if Subscription.objects.filter(subscriber=user,
                                       author=author).exists():
            raise serializers.ValidationError('Уже подписан')
        return super().validate(data)

    def create(self, validated_data):
        return Subscription.objects.create(**validated_data)

    class Meta:
        model = Subscription
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
        read_only_fields = (
            'recipes_count',
        )
