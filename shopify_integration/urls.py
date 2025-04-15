from django.urls import path
from .views import ShopifyProductListView

urlpatterns = [
    path('shopify/products/', ShopifyProductListView.as_view(), name='shopify-products'),
]