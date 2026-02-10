from django.contrib.gis import admin
from .models import Trail, Review, TransportLink
from leaflet.admin import LeafletGeoAdmin

admin.site.register(Review)
admin.site.register(TransportLink)

@admin.register(Trail)
class TrailAdmin(LeafletGeoAdmin):
    # This gives you the map on the Edit/Detail page
    list_display = ('name', 'region', 'popularity')