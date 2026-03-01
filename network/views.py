from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets
from rest_framework.permissions import IsAdminUser

from .models import NetworkNode
from .serializers import NetworkNodeSerializer


class NetworkNodeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для CRUD операций со звеньями сети.
    Доступ только для активных сотрудников (IsAdminUser).
    Поддержка фильтрации по стране (регистронезависимая).
    """

    queryset = NetworkNode.objects.all()
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsAdminUser]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        "contact__country": ["icontains"],
    }
