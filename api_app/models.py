from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator

# Create your models here.

class Trail(models.Model):

    title = models.CharField(max_length=100)
    elevation_gain = models.FloatField()
    region = models.CharField(max_length=50)

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