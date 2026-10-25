from rest_framework import serializers

from .models import Case, Category, GalleryItem, Product, Service


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ('id', 'name', 'slug', 'description')


class CaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Case
        fields = (
            'id',
            'title',
            'slug',
            'summary',
            'description',
            'category',
            'image_url',
            'created_at',
        )
        read_only_fields = ('created_at',)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = (
            'id',
            'title',
            'slug',
            'description',
            'category',
            'image_url',
            'price',
        )


class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ('id', 'title', 'slug', 'description', 'category', 'image_url')


class GalleryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = GalleryItem
        fields = ('id', 'title', 'image_url', 'alt_text')
