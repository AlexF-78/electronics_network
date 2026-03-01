from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import NetworkNodeViewSet

# Создаём роутер для автоматической генерации URL
router = DefaultRouter()
router.register(r"node", NetworkNodeViewSet, basename="node")

urlpatterns = [
    # Все URL от роутера(nodes/, nodes/1/, etc.)
    path("", include(router.urls)),
]
