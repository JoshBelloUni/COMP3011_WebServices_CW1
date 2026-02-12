import requests
import time
from math import radians, cos, sin, asin, sqrt
from django.core.management.base import BaseCommand
from api_app.models import Trail, TransportLink, CarPark

# --- CONFIGURATION ---
SEARCH_RADIUS_KM = 1.0  # Max distance to link a stop/park to a trail
BBOX = "(53.15, -2.10, 54.00, -1.30)" # Peak District / Leeds Area

class Command(BaseCommand):
    help = 'Imports Car Parks and Transport links using optimized nearest-neighbor search'

    def haversine(self, lat1, lon1, lat2, lon2):
        """
        Standard Haversine Formula for distance between two points
        """
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1 
        dlat = lat2 - lat1 
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        return c * 6371 

    def get_nearest_trail(self, lat, lon, all_trails):
        """
        Optimized Nearest Neighbor Search.
        Uses a 'Pre-Check' to skip heavy math for trails that are obviously too far.
        """
        closest_trail = None
        min_dist = float('inf')

        # OPTIMIZATION: 
        # 0.05 degrees is approx 5.5km. If a trail is further than this in pure 
        # lat/lon difference, we don't even bother calculating the precise Haversine distance.
        lat_threshold = 0.05 
        lon_threshold = 0.08 

        for trail in all_trails:

            t_lat = float(trail.latitude)
            t_lon = float(trail.longitude)

            # 1. Cheap Pre-Check
            if abs(t_lat - lat) > lat_threshold: continue
            if abs(t_lon - lon) > lon_threshold: continue

            # 2. Expensive Check (Trigonometry)
            dist = self.haversine(lat, lon, t_lat, t_lon)
            
            if dist < min_dist:
                min_dist = dist
                closest_trail = trail
        
        return closest_trail, min_dist

    def fetch_overpass_data(self, query):
        """
        Robust Fetcher: Uses a faster mirror, retries on failure, and handles rate limits.
        """
        # Using kumi.systems mirror because it is much faster for heavy queries
        url = "https://overpass.kumi.systems/api/interpreter"
        headers = {
            'User-Agent': 'LeedsHikingApp/1.0',
            'Referer': 'http://localhost:8000/'
        }
        
        self.stdout.write("  > Downloading data...")
        
        for attempt in range(3):
            try:
                # 120s timeout for large datasets
                resp = requests.get(url, headers=headers, params={'data': query}, timeout=120)
                
                if resp.status_code == 429:
                    self.stdout.write(self.style.WARNING(f"    Rate limited. Waiting 15s... (Attempt {attempt+1})"))
                    time.sleep(15)
                    continue
                
                resp.raise_for_status()
                return resp.json()
                
            except Exception as e:
                self.stdout.write(self.style.WARNING(f"    Attempt {attempt+1} failed: {e}"))
                time.sleep(5)
                
        return None
    
    def is_public_parking(self, tags):
        """
        Returns False if the car park looks private, restricted, or is for customers only.
        """
        # 1. Check Access Tag (Stricter)
        # Block: Private, Customers, Permit Holders, Delivery, Residents, etc.
        access = tags.get('access', 'yes').lower()
        if access in ['private', 'customers', 'no', 'permit', 'delivery', 'residence', 'employees']:
            return False

        # 2. Check Name for "Red Flag" keywords
        name = tags.get('name', '').lower()
        banned_words = [
            'staff', 'private', 'residents', 'permit holders', 
            'reserved', 'customer', 'school', 'university', 'college',
            'surgery', 'clinic', 'hotel', 'guests only', 'employees',
            'supermarket', 'retail park'
        ]
        
        if any(word in name for word in banned_words):
            return False
            
        return True

    def import_carparks(self):
        self.stdout.write(self.style.SUCCESS("\n--- STEP 1: CAR PARKS ---"))
        
        # Load all trails into memory ONCE (Vital for speed)
        all_trails = list(Trail.objects.all())
        self.stdout.write(f"  > Loaded {len(all_trails)} trails for comparison.")
        
        # Fetch Data
        query = f"""
            [out:json][timeout:180];
            (
              node["amenity"="parking"]["access"!="private"]{BBOX};
              way["amenity"="parking"]["access"!="private"]{BBOX};
            );
            out center;
        """
        data = self.fetch_overpass_data(query)
        if not data: return

        elements = data.get('elements', [])
        total = len(elements)
        self.stdout.write(f"  > Downloaded {total} potential car parks. Processing...")

        count = 0
        saved = 0

        for element in elements:
            tags = element.get('tags', {})

            # Check for public parking
            if not self.is_public_parking(tags):
                continue

            count += 1
            if count % 50 == 0:
                self.stdout.write(f"    Processing {count}/{total}...", ending='\r')

            # Get Coords
            lat = element.get('lat') or element.get('center', {}).get('lat')
            lon = element.get('lon') or element.get('center', {}).get('lon')
            if not lat or not lon: continue

            # Find Trail
            trail, dist = self.get_nearest_trail(lat, lon, all_trails)
            
            if trail and dist <= SEARCH_RADIUS_KM:
                
                # Parse name
                name = tags.get('name', 'Unnamed Car Park')
                
                # Parse capacity
                cap_str = tags.get('capacity')
                if cap_str and cap_str.isdigit():
                    capacity = int(cap_str)
                else:
                    capacity = None
                
                # Parse is_free
                fee_tag = tags.get('fee')
                
                if fee_tag:
                    # 'no' means no fee (Free)
                    if fee_tag.lower() == 'no':
                        is_free = True
                    else:
                        # 'yes', 'interval', 'permissive' -> Not Free
                        is_free = False
                else:
                    is_free = None # Unknown

                # Parse disabled parking
                raw_disabled = tags.get('disabled_parking') or tags.get('capacity:disabled')
                
                if raw_disabled:
                    # If explicitly marked 'no', '0', or 'none' -> False
                    if raw_disabled.lower() in ['no', '0', 'none']:
                        has_disabled = False
                    else:
                        has_disabled = True
                else:
                    has_disabled = None

                # Save
                CarPark.objects.update_or_create(
                    name=name,
                    trail=trail,
                    defaults={
                        'latitude': lat,
                        'longitude': lon,
                        'capacity': capacity,
                        'is_free': is_free,
                        'has_disabled_parking': has_disabled,
                    }
                )
                saved += 1
                
        self.stdout.write(self.style.SUCCESS(f"  > DONE! Linked {saved} Car Parks."))

    def import_transport(self):
        self.stdout.write(self.style.SUCCESS("\n--- STEP 2: TRANSPORT LINKS ---"))
        
        all_trails = list(Trail.objects.all())
        
        query = f"""
            [out:json][timeout:180];
            (
              node["railway"="station"]{BBOX};
              node["highway"="bus_stop"]{BBOX};
            );
            out body;
        """

        data = self.fetch_overpass_data(query)
        if not data: return

        elements = data.get('elements', [])
        total = len(elements)
        self.stdout.write(f"  > Downloaded {total} transport stops. Processing...")

        count = 0
        saved = 0
        
        for element in elements:
            count += 1
            if count % 100 == 0:
                self.stdout.write(f"    Processing {count}/{total}...", ending='\r')

            lat = element.get('lat')
            lon = element.get('lon')
            if not lat: continue

            tags = element.get('tags', {})
            if tags.get('railway') == 'station': t_type = 'Train'
            elif tags.get('highway') == 'bus_stop': t_type = 'Bus'
            else: continue

            # Find Trail
            trail, dist = self.get_nearest_trail(lat, lon, all_trails)

            if trail and dist <= SEARCH_RADIUS_KM:
                name = tags.get('name', f"{t_type} Stop")
                
                TransportLink.objects.update_or_create(
                    name=name,
                    trail=trail,
                    type=t_type,
                    defaults={
                        'latitude': lat,
                        'longitude': lon,
                    }
                )
                saved += 1
        
        self.stdout.write(self.style.SUCCESS(f"  > DONE! Linked {saved} Transport Links."))

    def handle(self, *args, **kwargs):
        self.import_carparks()
        self.import_transport()
        self.stdout.write(self.style.SUCCESS("\nAll services imported successfully!"))