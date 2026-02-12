from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import viewsets, permissions, filters, generics
from django_filters.rest_framework import DjangoFilterBackend
from .models import Trail, Review, TransportLink, CarPark
from .serializers import (
    TrailSerializer, 
    ReviewSerializer, 
    TransportSerializer, 
    CarParkSerializer
)

@api_view(['GET'])
def hello_world(request):
    return Response({"message": "Hello from your hiking API!"})

# 1. List all trails (GET /trails/)
class TrailList(generics.ListCreateAPIView):
    queryset = Trail.objects.all()
    serializer_class = TrailSerializer

# 2. Get one trail (GET /trails/5/)
class TrailDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Trail.objects.all()
    serializer_class = TrailSerializer

# --- CUSTOM PERMISSIONS ---

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request (GET, HEAD, OPTIONS)
        if request.method in permissions.SAFE_METHODS:
            return True
        
        print(f"LOGGED IN USER: {request.user} (ID: {request.user.id})")
        print(f"REVIEW OWNER:   {obj.user} (ID: {obj.user.id})")
        print(f"MATCH?          {obj.user == request.user}")

        # Write permissions are only allowed to the owner of the review
        return obj.user == request.user


# --- VIEWSETS ---

class TrailViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows trails to be viewed or searched.
    - GET /api/trails/: List all trails
    - GET /api/trails/{id}/: Retrieve specific trail
    """
    queryset = Trail.objects.all()
    serializer_class = TrailSerializer
    permission_classes = [permissions.AllowAny] # Open to everyone
    
    # Enable search and filtering
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['name', 'region']      # Search by name (e.g., ?search=Mam Tor)
    filterset_fields = ['region', 'difficulty'] # Filter (e.g., ?difficulty=Easy)


class ReviewViewSet(viewsets.ModelViewSet):
    """
    API endpoint for User Reviews.
    - POST: Create a review (Auth required)
    - PUT/PATCH: Update a review (Owner only)
    - DELETE: Delete a review (Owner only)
    """
    queryset = Review.objects.all()
    serializer_class = ReviewSerializer
    
    # Security: Auth required to post, Owner required to edit
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    # Filtering: Get reviews for a specific trail
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['trail', 'rating']  # Usage: /api/reviews/?trail=5
    ordering_fields = ['created_at', 'rating'] # Usage: /api/reviews/?ordering=-rating

    def perform_create(self, serializer):
        # Automatically attach the logged-in user as the author
        serializer.save(user=self.request.user)


class TransportViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Public Transport links (Bus/Train).
    Read-only reference data.
    """
    queryset = TransportLink.objects.all()
    serializer_class = TransportSerializer
    permission_classes = [permissions.AllowAny]
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['trail', 'type'] # Usage: /api/transport/?type=Train


class CarParkViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for Car Parks.
    Read-only reference data.
    """
    queryset = CarPark.objects.all()
    serializer_class = CarParkSerializer
    permission_classes = [permissions.AllowAny]
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['trail', 'is_free', 'has_disabled_parking'] # Usage: /api/carparks/?is_free=true