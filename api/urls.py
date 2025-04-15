from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductSnapshotViewSet, SEOKeywordTrackingViewSet, ProductViewSet, SellerViewSet, PlatformViewSet

router = DefaultRouter()
router.register(r'snapshots', ProductSnapshotViewSet)
router.register(r'seo-keywords', SEOKeywordTrackingViewSet)
router.register(r'products', ProductViewSet)
router.register(r'sellers', SellerViewSet)
router.register(r'platforms', PlatformViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
