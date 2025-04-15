from rest_framework import serializers
from tracking.models import ProductSnapshot, SEOKeywordTracking
from scrape.models import Product, Seller, Platform

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class SellerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seller
        fields = '__all__'

class ProductSnapshotSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductSnapshot
        fields = '__all__'

class SEOKeywordTrackingSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOKeywordTracking
        fields = '__all__'
