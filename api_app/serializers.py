from rest_framework import serializers
from .models import Trail
import requests

class TrailSerializer(serializers.ModelSerializer):
    # This field is calculated on-the-fly
    safety_score = serializers.SerializerMethodField()
    current_weather = serializers.SerializerMethodField()

    class Meta:
        model = Trail
        fields = '__all__'

    def get_current_weather(self, obj):
        # Fetch live weather for this trail's coordinates
        # (In production, you would cache this to save API calls)
        api_key = "YOUR_OPENWEATHER_KEY"
        url = f"https://api.openweathermap.org/data/2.5/weather?lat={obj.latitude}&lon={obj.longitude}&appid={api_key}&units=metric"
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        return None

    def get_safety_score(self, obj):
        weather = self.get_current_weather(obj)
        if not weather:
            return None # Could not calculate
            
        # --- YOUR ALGORITHM GOES HERE ---
        score = 100
        
        # Extract data
        temp = weather['main']['temp']
        wind = weather['wind']['speed']
        condition = weather['weather'][0]['main'].lower()

        # Penalties
        if wind > 20: score -= 30 # Windy
        if temp < 5: score -= 20  # Cold
        if 'rain' in condition: score -= 25
        if 'snow' in condition: score -= 40
        
        return max(score, 0)