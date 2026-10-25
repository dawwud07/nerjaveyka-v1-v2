from rest_framework.routers import DefaultRouter

from .views import (
    CaseViewSet,
    CategoryViewSet,
    GalleryItemViewSet,
    ProductViewSet,
    ServiceViewSet,
)

router = DefaultRouter()
router.register('cases', CaseViewSet, basename='case')
router.register('categories', CategoryViewSet, basename='category')
router.register('gallery-items', GalleryItemViewSet, basename='gallery-item')
router.register('products', ProductViewSet, basename='product')
router.register('services', ServiceViewSet, basename='service')

urlpatterns = router.urls
