# backend/products/serializers.py
# Add image_url to your existing ProductSerializer so it appears
# on the ProductPage, home page, and anywhere products are fetched.

from rest_framework import serializers
from .models import Product, Website, Price


class WebsiteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Website
        fields = ["id", "name", "base_url"]


class PriceSerializer(serializers.ModelSerializer):
    website = WebsiteSerializer(read_only=True)

    class Meta:
        model = Price
        fields = ["website", "price", "product_url", "last_updated"]


class ProductSerializer(serializers.ModelSerializer):
    prices = PriceSerializer(many=True, read_only=True)
    image_url = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ["id", "name", "description", "image_url", "prices", "created_at"]

    def get_image_url(self, obj):
        # Return placeholder if no image has been scraped yet
        return obj.image_url if obj.image_url else "https://placehold.co/300x300?text=No+Image"