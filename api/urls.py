from django.urls import include, path

urlpatterns = [
    path('', include('apps.catalog.urls')),
    path('', include('apps.inquiries.urls')),
    path('', include('api.yasg')),
]
