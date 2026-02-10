import requests
from math import radians, cos, sin, asin, sqrt, ceil
from django.core.management.base import BaseCommand
from api_app.models import Trail
from django.contrib.gis.geos import LineString, MultiLineString

# --- CONFIGURATION ---
FETCH_ELEVATION = True 
SKIP_EXTREME_TRAILS = True
MAX_TRAIL_LENGTH = 60

class Command(BaseCommand):
    help = 'Imports trails with Difficulty and Duration estimates'

    def haversine_length(self, points):
        """Calculates length in km"""
        if len(points) < 2: return 0.0
        total_km = 0.0
        R = 6371 
        for i in range(len(points) - 1):
            lon1, lat1 = points[i]
            lon2, lat2 = points[i+1]
            lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
            dlon = lon2 - lon1
            dlat = lat2 - lat1
            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * asin(sqrt(a))
            total_km += c * R
        return total_km

    def calculate_metrics(self, length_km, elevation_gain_m):
        """
        Returns (Difficulty, Duration String) based on Naismith's Rule
        Rule: 1 hr per 5km + 1 hr per 600m ascent
        """
        # 1. Estimate Time (Hours)
        time_hours = (length_km / 5.0) + (elevation_gain_m / 600.0)
        
        # Format duration string
        if time_hours < 1:
            duration_str = f"{int(time_hours * 60)} mins"
        elif time_hours > 24:
            days = ceil(time_hours / 8) # Assuming 8 hours hiking per day
            duration_str = f"{days} days"
        else:
            duration_str = f"{round(time_hours, 1)} hours"

        # 2. Determine Difficulty
        # Multi-day check
        if length_km > 40:
            difficulty = "Multi-day Trek"
        # Steepness check (m per km)
        elif (elevation_gain_m / length_km) > 50: 
            difficulty = "Hard"
        elif length_km > 15:
            difficulty = "Challenging"
        elif length_km > 8:
            difficulty = "Moderate"
        else:
            difficulty = "Easy"

        return difficulty, duration_str

    def calculate_elevation(self, points):
        """Gets rough elevation gain"""
        if not FETCH_ELEVATION or not points: return 0.0
        sampled = points[::50] 
        if not sampled: return 0.0
        
        locations = [{"latitude": lat, "longitude": lon} for lon, lat in sampled]
        try:
            url = 'https://api.open-elevation.com/api/v1/lookup'
            response = requests.post(url, json={'locations': locations}, timeout=2)
            data = response.json()
            elevs = [r['elevation'] for r in data['results']]
            return round(max(elevs) - min(elevs), 2)
        except:
            return 0.0

    def get_region_name(self, latitude):
        if latitude < 53.65: return "Peak District"
        else: return "Leeds & Yorkshire"

    def handle(self, *args, **kwargs):
        self.stdout.write("Fetching trails...")

        # Same query as before (Nature + Relations)
        overpass_url = "http://overpass-api.de/api/interpreter"
        bbox = "(53.15, -2.10, 54.00, -1.30)"
        keywords = "Walk|Trail|Way|Loop|Circuit|Circular|Reservoir|Edge|Pike|Tor"
        
        query = f"""
            [out:json][timeout:300];
            (
              relation["route"~"hiking|foot"]["name"]{bbox};
              way["highway"~"path|track"]["name"~"{keywords}"]{bbox};
            );
            out geom;
        """

        try:
            resp = requests.get(overpass_url, params={'data': query})
            resp.raise_for_status()
            data = resp.json()
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Download Failed: {e}"))
            return

        elements = data.get('elements', [])
        count = 0
        
        for element in elements:
            tags = element.get('tags', {})
            name = tags.get('name', 'Unknown')

            if "Public Footpath" in name or "Bridleway" in name: continue
            if tags.get('highway') in ['residential', 'service', 'primary']: continue

            # --- Geometry Collection ---
            lines_list = [] 
            all_points = []
            
            if element['type'] == 'relation' and 'members' in element:
                for member in element['members']:
                    if member.get('type') == 'way' and 'geometry' in member:
                        pts = [(pt['lon'], pt['lat']) for pt in member['geometry']]
                        if len(pts) >= 2:
                            lines_list.append(LineString(pts))
                            all_points.extend(pts)
            elif element['type'] == 'way' and 'geometry' in element:
                pts = [(pt['lon'], pt['lat']) for pt in element['geometry']]
                if len(pts) >= 2:
                    lines_list.append(LineString(pts))
                    all_points.extend(pts)
            
            if not lines_list: continue

            # --- Stitching ---
            raw_geom = MultiLineString(lines_list)
            try:
                merged_geom = raw_geom.unary_union
            except:
                merged_geom = raw_geom 

            if isinstance(merged_geom, LineString):
                final_geom = MultiLineString([merged_geom])
            elif isinstance(merged_geom, MultiLineString):
                final_geom = merged_geom
            else:
                final_geom = raw_geom

            # --- Stats Calculation ---
            total_len = 0.0
            for line in final_geom:
                total_len += self.haversine_length(line.coords)

            # FILTER 1: Too short?
            if total_len < 1.5: continue
            
            # FILTER 2: Too long? (Optional)
            if SKIP_EXTREME_TRAILS and total_len > MAX_TRAIL_LENGTH:
                continue

            gain = self.calculate_elevation(all_points)
            
            # --- CALCULATE DIFFICULTY ---
            difficulty, duration = self.calculate_metrics(total_len, gain)

            centroid = final_geom.centroid
            detected_region = self.get_region_name(centroid.y)

            try:
                Trail.objects.update_or_create(
                    name=name,
                    defaults={
                        'latitude': centroid.y,
                        'longitude': centroid.x,
                        'path': final_geom,
                        'length': round(total_len, 2),
                        'elevation_gain': gain,
                        'region': detected_region, 
                        
                        # NEW FIELDS
                        'difficulty': difficulty,
                        'estimated_duration': duration,
                        
                        'popularity': 0.0,
                    }
                )
                count += 1
                self.stdout.write(f"  + {name} ({round(total_len, 2)}km) - {difficulty} [{duration}]")
            except Exception as e:
                pass

        self.stdout.write(self.style.SUCCESS(f'Done! Imported {count} trails.'))