# Leeds Hiking Companion API

A GeoDjango-based REST API designed to provide hiking trails, car parks, and transport links for the Leeds and Peak District area. This project features geospatial data ingestion from OpenStreetMap, nearest-neighbor calculation for amenities, and a fully functional review system with authentication.

## Features

* **Geospatial Data:** Uses GeoDjango and PostGIS/SQLite (Spatiolite) to handle locational data.
* **Automated Ingestion:** Custom management commands to fetch and parse data from OpenStreetMap via the Overpass API.
* **Smart Linking:** Automatically links car parks and transport stops to the nearest trail using optimized Haversine distance calculations.
* **Search & Filtering:** Filter trails by difficulty, region, and search by name.
* **User Reviews:** Full CRUD system for users to rate and review trails (with permission handling).
* **Data Integrity:** Handles missing external data gracefully (e.g., distinguishing between "0 capacity" and "unknown capacity").

---

## Prerequisites

Before running this project, ensure you have the following installed:

1.  **Python 3.8+**
2.  **GDAL Library** (Required for GeoDjango)
    * *Windows:* Install via OSGeo4W or use a pre-built wheel.
    * *Mac:* `brew install gdal`
    * *Linux:* `sudo apt-get install binutils libproj-dev gdal-bin`

---

## Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/JoshBelloUni/COMP3011_WebServices_CW1.git
    cd COMP3011_WebServices_CW1
    ```

2.  **Create and Activate Virtual Environment**
    ```bash
    # Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Mac/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Migration**
    Initialize the database with geospatial support.
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

5.  **Create Admin User**
    You need a superuser to access the Admin panel and manage data.
    ```bash
    python manage.py createsuperuser
    ```

    - Username: Marker
    - Password: COMP3011Marker

---

## Data Import Scripts

This API relies on external data. You **must** run these commands in the following order to populate the database. The scripts currently gather trail data from the peak district and Leeds area.

### 1. Import Hiking Trails
Fetches walking routes, calculates difficulty using Naismith's Rule, and saves geometry.
```bash
python manage.py import_trails
```

### 2. Import Services (Car Parks & Transport)
Fetches amenities and links them to the *nearest* trail
```bash
python manage.py import_services
```

### Utility Commands
To reset data if needed:
```bash
python manage.py clear_trails # Clears Trails
python manage.py clear_carparks # Clears Car Parks
python manage.py clear_transport # Clears Transport links
```

---

## API Endpoints

Once the server is running (`python manage.py runserver`), access the API at `http://127.0.0.1:8000/api`.

### **Trails**
* `GET /api/trails/` - List all trails.
* `GET /api/trails/{id}/` - Get details (including linked car parks).
* **Filtering:**
    * `?difficulty=Easy` (Options: Easy, Moderate, Hard)
    * `?region=Peak District`
    * `?search=Reservoir` (Search by name)
    * `?ordering=-length` (Sort by length)

### **Services**
* `GET /api/carparks/` - List all car parks.
* `GET /api/transport/` - List bus/train stops.
* `/{id}/` - Get details on specific car park or public transport stop

### **Reviews (CRUD)**
* `GET /api/reviews/` - List all reviews.
* `POST /api/reviews/` - Create a review (**Auth required**).
* `PUT /api/reviews/{id}/` - Edit your own review (**Owner only**).
* `DELETE /api/reviews/{id}/` - Delete your own review (**Owner only**).

### **Trail Reports**
*To be implemented*
* *Will contain all CRUD operations*

---

## Authentication & Permissions

* **Admin Panel:** `http://127.0.0.1:8000/admin/`
* **API Auth:** The API uses **Basic Authentication**.
    * **Anonymous Users:** Read-only access to Trails and Reviews.
    * **Authenticated Users:** Can create reviews.
    * **Review Owners:** Can edit/delete their own reviews (`IsOwnerOrReadOnly` permission).

---

## Key Design Decisions

1.  **Haversine Optimization:**
    To link thousands of car parks to trails efficiently, the import script uses a "Pre-check" subtraction filter. If a point is >5km away based on simple coordinate subtraction, the expensive Haversine trigonometric calculation is skipped. This improves import speed by ~90%.

2.  **Data Honesty (Nullable Fields):**
    OpenStreetMap data is often incomplete. Instead of defaulting missing values (like `capacity` or `cost`) to "0" or "Free", this API uses `Nullable` fields. This allows the frontend to distinguish between "Zero Capacity" (closed) and "Unknown Capacity" (data missing), preventing misleading information.

3.  **Naismith's Rule Implementation:**
    Trail difficulty is not arbitrary; it is calculated programmatically based on length and elevation gain using Naismith's Rule (1 hour per 5km + 1 hour per 600m ascent).

---

## Testing

To run the automated test suite:
```bash
python manage.py test
```

---
## Use of Generative AI

- **Dataset Discovery** - AI tools found necessary external APIs such as OpenStreetMap, elevation API and Weather API.

- **Import Script Generation** - Due to the nature of OpenStreetMap, AI tools were used to help generate the scripts for data importing. OSM contains many blank values which needed to be handled. AI was also used to help develop the Haversine Optimization and Naismith rule functions. 

- **Idea Generation** - As a mainly informational API, there is little opportunities besides the 'Reviews' section that utilise CRUD operations besides GET. AI was used to give ideas which led to the implementation of Trail Reports.

- **Code Debugging** - AI tools were used to debug code and Non-Success Status Codes.