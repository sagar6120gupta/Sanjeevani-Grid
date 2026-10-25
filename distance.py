from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta

EARTH_RADIUS_KM = 6371.0

def haversine_km(lat1, lon1, lat2, lon2):
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return EARTH_RADIUS_KM * c

def freshness_status(last_updated):
    if not last_updated:
        return "UNVERIFIED", "No update recorded"

    try:
        dt = datetime.fromisoformat(last_updated)
        age = datetime.now() - dt
    except Exception:
        return "UNVERIFIED", "Invalid timestamp"

    if age <= timedelta(hours=24):
        if age.total_seconds() < 3600:
            mins = max(1, int(age.total_seconds() // 60))
            return "CURRENT", f"Updated {mins} min ago"
        hours = max(1, int(age.total_seconds() // 3600))
        return "CURRENT", f"Updated {hours} hr ago"

    return "UNVERIFIED", f"Last update {age.days} day(s) ago"

def find_nearby(phcs, user_lat, user_lon, supply_key, radius_km=30):
    results = []

    for phc in phcs:
        distance = haversine_km(
            user_lat, user_lon,
            phc["latitude"], phc["longitude"]
        )

        if distance <= radius_km:
            freshness, freshness_text = freshness_status(phc["last_updated"])
            available = bool(phc[supply_key])

            results.append({
                **phc,
                "distance_km": distance,
                "available": available,
                "freshness": freshness,
                "freshness_text": freshness_text,
            })

    # Available + fresh facilities are prioritized, then distance.
    results.sort(
        key=lambda x: (
            not x["available"],
            x["freshness"] != "CURRENT",
            x["distance_km"]
        )
    )
    return results
