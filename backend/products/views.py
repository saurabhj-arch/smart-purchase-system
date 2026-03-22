from rest_framework import viewsets
from rest_framework.permissions import AllowAny   # ← add this
from .models import Product, Website, Price
from .serializers import ProductSerializer, WebsiteSerializer, PriceSerializer
from django_filters.rest_framework import DjangoFilterBackend

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]   # ← add this

class WebsiteViewSet(viewsets.ModelViewSet):
    queryset = Website.objects.all()
    serializer_class = WebsiteSerializer
    permission_classes = [AllowAny]   # ← add this

class PriceViewSet(viewsets.ModelViewSet):
    queryset = Price.objects.all()
    serializer_class = PriceSerializer
    permission_classes = [AllowAny]   # ← add this
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ["product", "website"]