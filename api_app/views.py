from django.shortcuts import render, get_object_or_404

# Create your views here.

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import generics
from .models import Trail
from .serializers import TrailSerializer

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