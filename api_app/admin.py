from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Trail, Review, TransportLink

# Register your models here
admin.site.register(Trail)
admin.site.register(Review)
admin.site.register(TransportLink)