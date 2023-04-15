import base64

from django.core.files.base import ContentFile
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator, UniqueValidator

from .constants import RECIPES_LIMIT
from recipes.models import Ingredient, IngredientAmount, Recipe, Tag
from users.models import Subscription, User


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
        validators = [
            UniqueValidator(
                queryset=IngredientAmount.objects,
                message='Ингредиент повторяется в рецепте.'
            )
        ]


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
    author = UserSerializer(many=False, read_only=True,
                            default=serializers.CurrentUserDefault())
    ingredients = IngredientAmountSerializer(
        many=True, source='amounts', read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField(required=True,)

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
    ingredients = IngredientAmountCreateSerializer(many=True)
    image = Base64ImageField(required=True,)

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
                queryset=Recipe.objects,
                fields=['author', 'name'],
                message='Рецепт с таким названием уже есть у этого автора.'
            ),
        ]

    def update(self, instance, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        if tags:
            instance.tags.set(tags)
        if ingredients_data:
            instance.amounts.all().delete()
            IngredientAmount.objects.bulk_create(
                [IngredientAmount(
                    recipe=instance,
                    ingredient=entry['ingredient'],
                    amount=entry['amount']
                ) for entry in ingredients_data],
            )
            super().update(instance, validated_data)
        return instance

    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients', None)
        tags = validated_data.pop('tags', None)
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags)

        IngredientAmount.objects.bulk_create(
            [IngredientAmount(
                recipe=recipe,
                ingredient=entry['ingredient'],
                amount=entry['amount']
            ) for entry in ingredients_data],
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


class SubscriptionSerializer(serializers.ModelSerializer):
    email = serializers.ReadOnlyField(source='author.email')
    id = serializers.PrimaryKeyRelatedField(queryset=User.objects,
                                            source='author.id')
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
        if data['author']['id'] == self.context['request'].user:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на самого себя'})
        if Subscription.objects.filter(subscriber=self.context['request'].user,
                                       author=data['author']['id']).exists():
            raise serializers.ValidationError(
                {'errors': 'Уже подписан'})
        return super().validate(data)

    def create(self, validated_data):
        subscriber = self.context['request'].user
        author = validated_data['author']['id']
        subscription = Subscription.objects.create(
            subscriber=subscriber,
            author=author
        )
        return subscription

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
            'email',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
        )
