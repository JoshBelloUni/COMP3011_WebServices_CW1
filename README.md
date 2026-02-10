# COMP3011_WebServices_CW1

# OpenTrail API (Django + OSM)

A specialized REST API that ingests raw hiking data from **OpenStreetMap (OSM)** and processes it into "AllTrails-quality" route data.

Unlike standard OSM tools, this project uses **topology preservation** logic to stitch fragmented trail segments, calculates **real elevation profiles** using external APIs, and automatically grades trails by **difficulty and duration** (using Naismith's Rule).

## 🚀 Features

* **Smart Ingestion:** Fetches hiking relations and named paths from OSM (Overpass API).
* **Topology Stitching:** Uses `unary_union` to merge hundreds of disconnected segments into clean `MultiLineString` geometries, preventing "spiderweb" visual glitches.
* **Auto-Grading:** Automatically calculates:
    * **Difficulty:** (Easy, Moderate, Hard, Multi-day Trek) based on steepness and length.
    * **Duration:** Estimates hiking time using *Naismith's Rule* (distance + elevation gain).
* **Elevation Data:** Integrates with **Open-Elevation API** to determine vertical range (Gain/Loss).
* **Region Detection:** Automatically assigns trails to regions (e.g., "Peak District", "Lake District", "Leeds") based on latitude.
* **GeoJSON API:** Exposes processed trails via a standard REST API for frontend mapping applications (Leaflet, Mapbox, etc.).

---

## Prerequisites & Installation

This project uses **GeoDjango** and **SpatiaLite**. Unlike standard Django apps, you must install specific system binaries for the spatial features to work on Windows.

### 1. Python Dependencies
Clone the repository and install the required packages:

```bash
git clone 
cd opentrail-api
pip install -r requirements.txt