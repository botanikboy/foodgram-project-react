from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (IngredientViewSet, RecipeViewSet,
                    TagViewSet, UserViewSet)

router = SimpleRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register('users/subscriptions', UserViewSet,
                basename='subscriptions')
router.register('users', UserViewSet,
                basename='subscriptions')

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
