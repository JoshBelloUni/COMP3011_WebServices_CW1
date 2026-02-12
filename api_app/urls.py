from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    TrailViewSet, 
    ReviewViewSet, 
    TransportViewSet, 
    CarParkViewSet
)

# Create a router and register our viewsets with it.
router = DefaultRouter()

# Register the resources
# The string argument (e.g., r'trails') determines the URL prefix.
router.register(r'trails', TrailViewSet)       # http://127.0.0.1:8000/api/trails/
router.register(r'reviews', ReviewViewSet)     # http://127.0.0.1:8000/api/reviews/
router.register(r'transport', TransportViewSet)# http://127.0.0.1:8000/api/transport/
router.register(r'carparks', CarParkViewSet)   # http://127.0.0.1:8000/api/carparks/

urlpatterns = [
    # Include the router URLs
    path('api/', include(router.urls)),
]