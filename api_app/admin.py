from django.contrib.gis import admin
from .models import Trail, Review, TransportLink, CarPark
from leaflet.admin import LeafletGeoAdmin

@admin.register(Trail)
class TrailAdmin(LeafletGeoAdmin):
    # This gives you the map on the Edit/Detail page
    list_display = ('name', 'region', 'popularity')

@admin.register(Review)
class ReviewAdmin(LeafletGeoAdmin):
    # This gives you the map on the Edit/Detail page
    list_display = ('title', 'rating')

@admin.register(TransportLink)
class TransportAdmin(LeafletGeoAdmin):
    # This gives you the map on the Edit/Detail page
    list_display = ('name', 'type')

@admin.register(CarPark)
class CarParkAdmin(LeafletGeoAdmin):
    # This gives you the map on the Edit/Detail page
    list_display = ('name', 'capacity')