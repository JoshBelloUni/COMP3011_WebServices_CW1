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
3. **Windows Specific SpaciaLite**
    * Download the SpatiaLite binaries (mod_spatialite-5.0.1-win-amd64.7z).
    * Extract contents into the root directory of the project.
    * The settings.py is configured to automatically detect this folder using BASE_DIR / 'spatialite'.

---

## Installation & Setup

1.  **Clone the repository**
    ```bash
    git clone https://github.com/JoshBelloUni/COMP3011_WebServices_CW1.git
    cd COMP3011_WebServices_CW1
    ```

2.  **Create and Activate Virtual Environment**
    *Because GeoDjango relies on system-level C-libraries (GDAL), the installation process differs based on your operating system:*

    **For Linux / Mac:**
    These environments natively support the GDAL libraries. Use the standard requirements file:
    ```bash
    pip install -r requirements.txt
    ```

    **For Windows (Local Development):**
    Windows requires a pre-compiled `.whl` file for GDAL to install correctly without throwing a C++ compiler error. Use the Windows-specific requirements file (which automatically includes the standard requirements):
    ```bash
    pip install -r requirements-win.txt
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
    You need a superuser to access the Admin panel and manage data. A superuser user has been created for Marker use.
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
* `GET /api/transport/{id}/` - Get details on specific car park or public transport stop

### **Reviews (CRUD)**
* `GET /api/reviews/` - List all reviews.
* `POST /api/reviews/` - Create a review (**Auth required**).
* `PUT /api/reviews/{id}/` - Edit your own review (**Owner only**).
* `DELETE /api/reviews/{id}/` - Delete your own review (**Owner only**).

### **Trail Logbook**
* `GET /api/logbook/` - List all logs in your logbook (**Auth required**).
* `POST /api/logbook/` - Create a log (**Auth required**).
* `PUT /api/logbook/{id}/` - Edit a single log (**Owner only**).
* `DELETE /api/logbook/{id}/` - Delete your own log (**Owner only**).

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
    To link thousands of car parks to trails efficiently, the import script uses a "Pre-check" subtraction filter. If a point is >5km away based on simple coordinate subtraction, the expensive Haversine trigonometric calculation is skipped.

2.  **Data Honesty (Nullable Fields):**
    OpenStreetMap data is often incomplete. Instead of defaulting missing values (like `capacity` or `cost`) to "0" or "Free", this API uses `Nullable` fields. This allows the frontend to distinguish between "Zero Capacity" (closed) and "Unknown Capacity" (data missing), preventing misleading information.

3.  **Naismith's Rule Implementation:**
    Trail difficulty is not arbitrary; it is calculated programmatically based on length and elevation gain using Naismith's Rule (1 hour per 5km + 1 hour per 600m ascent).

4. **Safety Score Calculation:**
    The safety score is a metric that determines how safe a trail is. It combines many factors: temperature, weather and wind speed. These factors are derived from the open-metro API.

---

# Deployment

This application has been deployed on https://joshbellouol.eu.pythonanywhere.com. Replace the localhost url with this.

To ensure a smooth transition from local development to PythonAnywhere, the following adjustments were made:

* Library Paths: Dynamic selection of mod_spatialite.so (Linux) vs mod_spatialite.dll (Windows).

* Security: Updated ALLOWED_HOSTS to include the pythonanywhere.com domain.

* Database: Utilized absolute pathing for db.sqlite3 to maintain persistence across web worker restarts.

---
## API Documentation

The full technical specification for this API is provided in the accompanying PDF manual. This includes endpoint definitions, authentication requirements, and JSON request/response examples.

**[Download API Documentation (PDF)](./docs/API_Documentation.pdf)**

*Note: For an interactive version of this documentation, you can also visit the [Postman Web Portal](https://documenter.getpostman.com/view/52318963/2sBXcLhJEH).*

---
## Use of Generative AI

- **Dataset Discovery** - AI tools found necessary external APIs such as OpenStreetMap, elevation API and Weather API.

- **Import Script Generation** - Due to the nature of OpenStreetMap, AI tools were used to help generate the scripts for data importing. OSM contains many blank values which needed to be handled. AI was also used to help develop the Haversine Optimization and Naismith rule functions. 

- **Idea Generation** - As a mainly informational API, there is little opportunities besides the 'Reviews' section that utilise CRUD operations besides GET. AI was used to give ideas which led to the implementation of Trail Reports.

- **Code Debugging** - AI tools were used to debug code and Non-Success Status Codes.