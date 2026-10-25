from rest_framework import viewsets

from .models import Case, Category, GalleryItem, Product, Service
from .serializers import (
    CaseSerializer,
    CategorySerializer,
    GalleryItemSerializer,
    ProductSerializer,
    ServiceSerializer,
)


class PublicReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    pass


class CaseViewSet(PublicReadOnlyViewSet):
    queryset = Case.objects.filter(is_active=True).select_related('category')
    serializer_class = CaseSerializer
    filterset_fields = ('category',)
    search_fields = ('title', 'summary', 'description')
    ordering_fields = ('created_at', 'title')


class CategoryViewSet(PublicReadOnlyViewSet):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    search_fields = ('name', 'description')
    ordering_fields = ('sort_order', 'name')


class GalleryItemViewSet(PublicReadOnlyViewSet):
    queryset = GalleryItem.objects.filter(is_active=True)
    serializer_class = GalleryItemSerializer
    search_fields = ('title', 'alt_text')
    ordering_fields = ('sort_order', 'id')


class ProductViewSet(PublicReadOnlyViewSet):
    queryset = Product.objects.filter(is_active=True).select_related('category')
    serializer_class = ProductSerializer
    filterset_fields = ('category',)
    search_fields = ('title', 'description')
    ordering_fields = ('title', 'price')


class ServiceViewSet(PublicReadOnlyViewSet):
    queryset = Service.objects.filter(is_active=True).select_related('category')
    serializer_class = ServiceSerializer
    filterset_fields = ('category',)
    search_fields = ('title', 'description')
    ordering_fields = ('title',)
