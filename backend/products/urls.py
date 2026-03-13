from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet, WebsiteViewSet, PriceViewSet

router = DefaultRouter()

router.register(r'products', ProductViewSet)
router.register(r'websites', WebsiteViewSet)
router.register(r'prices', PriceViewSet)

urlpatterns = [
    path('', include(router.urls)),
]