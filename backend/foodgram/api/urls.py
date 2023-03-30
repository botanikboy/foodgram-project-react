from django.urls import include, path
from rest_framework.routers import SimpleRouter

from .views import (IngredientViewSet, RecipeViewSet, SubscriptionsListViewSet,
                    TagViewSet, SubscriprionCreateDestroyViewSet)

router = SimpleRouter()
router.register('tags', TagViewSet)
router.register('recipes', RecipeViewSet)
router.register('ingredients', IngredientViewSet)
router.register('subscriptions', SubscriptionsListViewSet,
                basename='subscriptions')
router.register(r'users/(?P<author_id>[\d]+)/subscribe',
                SubscriprionCreateDestroyViewSet,
                basename='new_subscription')


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include(router.urls))
]
