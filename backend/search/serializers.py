from rest_framework import serializers


class StoreSerializer(serializers.Serializer):
    site = serializers.CharField()
    price = serializers.FloatField()
    link = serializers.URLField()


class SearchResultSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    name = serializers.CharField()
    image_url = serializers.URLField()   # ← added
    stores = StoreSerializer(many=True)