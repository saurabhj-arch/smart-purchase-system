from rest_framework import serializers
from .models import Product, Website, Price

class PriceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Price
        fields = "__all__"
        
class ProductSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many = True, read_only = True)
    class Meta:
        model = Product
        fields = "__all__"

class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = "__all__"

