from rest_framework import serializers

class ShopifyProductSerializer(serializers.Serializer):
    id = serializers.CharField()
    title = serializers.CharField()
    body_html = serializers.CharField()
    vendor = serializers.CharField()
    price = serializers.CharField(source='variants.0.price')  # assuming first variant
