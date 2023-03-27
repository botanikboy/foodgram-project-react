from rest_framework.viewsets import ModelViewSet

from recipes.models import Tag
from .serializers import TagSerializer
from .permissions import AdminPermission


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AdminPermission,)
    pagination_class = None
