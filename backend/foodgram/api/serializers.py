import base64

from rest_framework import serializers
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from users.models import User
from recipes.models import (Ingredient, IngredientAmount, Recipe,
                            Subscription, Tag)
from .constants import RECIPES_LIMIT


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
    name = serializers.CharField(
        max_length=250,
        validators=[UniqueValidator(
            queryset=Tag.objects,
            message='Тэг с таким именем уже существует.'
        )]
    )

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
        model = IngredientAmount
        fields = (
            'id',
            'name',
            'measurement_unit',
            'amount',
        )


class IngredientAmountCreateSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(queryset=Ingredient.objects,
                                            source='ingredient')
    amount = serializers.IntegerField(write_only=True)

    class Meta:
        model = IngredientAmount
        fields = (
            'id',
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
    tags = TagSerializer(many=True, read_only=True)
    # ВОПРОС ДЛЯ РЕВЬЮ: в ТЗ не указано, что должно происходить при изменении
    # или добавлении рецепта администратором, должен ли автор рецепта
    # оставаться неизменным или меняться на Администратора?
    # Если дать админу возможность указывать автора вручную, то делать
    # через get_fields и из view передавать дополнительно в context поле
    # для исключения, если пользователь является админом?
    author = UserSerializer(many=False, read_only=True,
                            default=serializers.CurrentUserDefault())
    ingredients = IngredientAmountSerializer(
        many=True, source='amounts', read_only=True)
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
        read_only_fields = (
            'author',
            'id',
            'pub_date',
            'is_favorited',
            'is_in_shopping_cart'
        )


class RecipeCreateSerializer(serializers.ModelSerializer):
    tags = serializers.PrimaryKeyRelatedField(many=True, queryset=Tag.objects)
    author = serializers.SlugRelatedField(
        many=False, read_only=True, default=serializers.CurrentUserDefault(),
        slug_field='email')
    ingredients = IngredientAmountCreateSerializer(
        many=True)
    image = Base64ImageField(required=True, allow_null=False)

    class Meta:
        model = Recipe
        fields = (
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
        )
        read_only_fields = ('author',)
        validators = [
            UniqueTogetherValidator(
                queryset=Recipe.objects, fields=['author', 'name'],
                message='Рецепт с таким названием уже есть у этого автора.'
            )
        ]

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        instance.tags.set(tags)
        instance.amounts.all().delete()
        for ingredient_data in ingredients_data:
            IngredientAmount.objects.create(
                recipe=instance,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount'],
            )
        super().update(instance, validated_data)
        return instance

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)
        for ingredient_data in ingredients_data:
            IngredientAmount.objects.create(
                recipe=recipe,
                ingredient=ingredient_data['ingredient'],
                amount=ingredient_data['amount'],
            )
        return recipe


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
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField(source='author.recipes.count')

    def get_recipes(self, obj):
        recipes = obj.author.recipes.all()
        recipes_limit = int(
            self.context['request'].query_params.get(
                'recipes_limit', RECIPES_LIMIT))
        if recipes_limit and len(recipes) > recipes_limit:
            recipes = recipes[:recipes_limit]
        serializer = RecipeListSerializer(instance=recipes, many=True)
        return serializer.data

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
            raise serializers.ValidationError(
                'Уже подписан')
        return super().validate(data)

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
