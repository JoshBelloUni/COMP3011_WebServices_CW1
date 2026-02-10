from django.contrib.gis.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Trail(models.Model):

    name = models.CharField(max_length=100)
    elevation_gain = models.FloatField(default=0.0)
    length = models.FloatField(default=0.0)

    region = models.CharField(
        max_length=50,
        default=0.0)

    latitude = models.DecimalField(
        max_digits=8, 
        decimal_places=6,
        validators=[MinValueValidator(-90), MaxValueValidator(90)]
    )
    
    longitude = models.DecimalField(
        max_digits=9, 
        decimal_places=6,
        validators=[MinValueValidator(-180), MaxValueValidator(180)]
    )

    popularity = models.FloatField(
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        default=0.0
    )

    path = models.MultiLineStringField(null=True)

    difficulty = models.CharField(max_length=50, default="Moderate")
    estimated_duration = models.CharField(max_length=50, default="0h")

    def __str__(self):
        return self.name

class Review(models.Model):

    trail = models.ForeignKey(Trail, on_delete=models.CASCADE, related_name='reviews')
    title = models.CharField(max_length=100)
    user = models.CharField(max_length=20)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

class TransportLink(models.Model):
    
    trail = models.ForeignKey(Trail, on_delete=models.CASCADE, related_name='transport_links')
    
    TRANSPORT_TYPES = [
        ('BUS', 'Bus Stop'),
        ('TRAIN', 'Train Station'),
        ('PARK', 'Car Park'),
    ]
    
    type = models.CharField(max_length=10, choices=TRANSPORT_TYPES)
    station_name = models.CharField(max_length=100)
    distance_from_trailhead_km = models.FloatField()
