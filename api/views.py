from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from .serializers import ProductSnapshotSerializer, SEOKeywordTrackingSerializer, ProductSerializer, SellerSerializer, PlatformSerializer
from tracking.models import ProductSnapshot, SEOKeywordTracking
from scrape.models import Product, Seller, Platform

class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

class SellerViewSet(viewsets.ModelViewSet):
    queryset = Seller.objects.all()
    serializer_class = SellerSerializer

class PlatformViewSet(viewsets.ModelViewSet):
    queryset = Platform.objects.all()
    serializer_class = PlatformSerializer

class ProductSnapshotViewSet(viewsets.ModelViewSet):
    queryset = ProductSnapshot.objects.all()
    serializer_class = ProductSnapshotSerializer

class SEOKeywordTrackingViewSet(viewsets.ModelViewSet):
    queryset = SEOKeywordTracking.objects.all()
    serializer_class = SEOKeywordTrackingSerializer

