import httpx

from app.config import GOOGLE_MAPS_API_KEY

from app.models.store import DiscoveredStore
from app.discovery.supported_retailers import normalize_retailer_name

GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"

def geocode_location(location: str) -> tuple[float, float]:
    response = httpx.get(
        GEOCODE_URL,
        params={
            "address": location,
            "key": GOOGLE_MAPS_API_KEY,
        },
        timeout=10.0,
    )

    response.raise_for_status()
    data = response.json()
    
    if data.get("status") != "OK" or not data.get("results"):
        raise ValueError(f"Could not geocode location: {location}")

    coords = data["results"][0]["geometry"]["location"]

    return coords["lat"], coords["lng"]


PLACES_NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"

def discover_stores(location: str, radius_km: float) -> list[DiscoveredStore]:
    latitude, longitude = geocode_location(location)

    headers = {
        "Content-Type": "application/json",
        "X-Goog-Api-Key": GOOGLE_MAPS_API_KEY,
        "X-Goog-FieldMask": (
            "places.id,"
            "places.displayName,"
            "places.formattedAddress,"
            "places.location,"
            "places.regularOpeningHours"
        ),
    }

    body = {
        "includedTypes": ["supermarket"],
        "maxResultCount": 20,
        "locationRestriction": {
            "circle": {
                "center": {
                    "latitude": latitude,
                    "longitude": longitude,
                },
                "radius": radius_km * 1000,
            }
        },
    }

    response = httpx.post(
        PLACES_NEARBY_URL,
        headers=headers,
        json=body,
        timeout=10.0,
    )

    response.raise_for_status()
    data = response.json()

    stores = []

    for place in data.get("places", []):
        raw_name = place.get("displayName", {}).get("text", "")
        retailer_name = normalize_retailer_name(raw_name)

        if retailer_name is None:
            continue

        location_data = place.get("location", {})

        store = DiscoveredStore(
            retailer_name=retailer_name,
            address=place["formattedAddress"],
            external_place_id=place["id"],
            latitude=location_data.get("latitude"),
            longitude=location_data.get("longitude"),
            opening_hours=place.get("regularOpeningHours"),
        )

        stores.append(store)
    
    return stores