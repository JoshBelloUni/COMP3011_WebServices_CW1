from rest_framework import serializers
from .models import Trail
import requests
from django.core.cache import cache

class TrailSerializer(serializers.ModelSerializer):

    safety_score = serializers.SerializerMethodField()
    current_weather = serializers.SerializerMethodField()

    class Meta:
        model = Trail
        fields = '__all__'

    def get_current_weather(self, obj):
        cache_key = f"weather_trail_{obj.id}"
        cached_weather = cache.get(cache_key)

        if cached_weather:
            return cached_weather

        # If not in cache, fetch it
        url = f"https://api.open-meteo.com/v1/forecast?latitude={obj.latitude}&longitude={obj.longitude}&current_weather=true"
        try:
            response = requests.get(url, timeout=3)
            if response.status_code == 200:
                data = response.json().get('current_weather')
                # Save to cache for 3600 seconds (1 hour)
                cache.set(cache_key, data, 3600)
                return data
        except:
            pass
        return None

    def get_safety_score(self, obj):
            weather = self.get_current_weather(obj)
            if not weather:
                return None  # No data, no score
                
            score = 100
            
            # --- 1. Extract Data safely (Open-Meteo Format) ---
            # Use .get() to avoid crashing if a key is missing
            temp = weather.get('temperature', 10)   # Default to 10°C if missing
            wind = weather.get('windspeed', 0)      # Default to 0 if missing
            code = weather.get('weathercode', 0)    # WMO code (0 = Clear sky)

            # --- 2. Penalties based on Weather Code ---
            # WMO Codes: https://open-meteo.com/en/docs
            
            if 51 <= code <= 67: score -= 25  # Rain/Drizzle
            elif 80 <= code <= 82: score -= 30  # Heavy Showers
            elif 71 <= code <= 77: score -= 40  # Snow
            elif code >= 95: score -= 50      # Thunderstorm

            # --- 3. Penalties based on Conditions ---
            if wind > 30: score -= 30    # Strong wind (>30 km/h)
            elif wind > 20: score -= 15  # Moderate wind
            
            if temp < 5: score -= 20     # Cold
            if temp > 30: score -= 20    # Too Hot

            return max(score, 0)