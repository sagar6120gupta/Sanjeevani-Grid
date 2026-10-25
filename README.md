# 🚑 Sanjeevani Grid

**Hyperlocal Emergency Life-Saving Supply Tracker for Rural India**


## What it does

Sanjeevani Grid helps a user find nearby healthcare facilities that report availability of:

- Anti-venom
- Rabies vaccine
- O-negative blood
- Oxygen

The prototype:

1. Gets the user's browser GPS location after permission.
2. Calculates distance to demo PHCs using the Haversine formula.
3. Filters facilities within 30 km.
4. Prioritizes currently confirmed available stock.
5. Shows stock freshness.
6. Displays facilities on a map.
7. Provides directions and click-to-call links.
8. Provides browser-based Hindi spoken guidance.
9. Gives PHC staff a one-step stock update portal.
10. Provides a district-level dashboard.

## Tech stack

- Python
- Streamlit
- SQLite
- Folium / streamlit-folium
- Browser Geolocation API through streamlit-geolocation
- Haversine distance calculation

## Run locally

### 1. Create virtual environment

```bash
python -m venv venv
```

### 2. Activate on Windows

```bash
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
streamlit run app.py
```

The database is created automatically at:

```text
database/sanjeevani.db
```

## GPS notes

- Click the location button in the Emergency Locator.
- Allow location permission in the browser.
- Browser geolocation normally requires a secure context (HTTPS) when deployed.
- If GPS permission is unavailable, the prototype provides manual latitude/longitude input.

## Demo staff PIN

```text
1234
```

This is intentionally a simple hackathon demo. It is NOT production authentication.

## Important prototype limitation

The PHC locations and inventory are demo data. They must be replaced by verified government/health-system data before real-world deployment.

## Suggested production upgrades

- Authenticated PHC accounts
- OTP / institutional login
- Server-side PostgreSQL database
- Audit logs
- SMS fallback
- Verified inventory synchronization
- Role-based access
- Rate limiting
- Encryption
- Monitoring
- Government health-system integration
- Clinically reviewed multilingual emergency guidance

## Demo flow

1. Open Emergency Locator.
2. Select Anti-venom.
3. Click the location button and allow GPS.
4. Click Find Emergency Help.
5. Show the 30 km results and map.
6. Open PHC Staff Portal.
7. Enter `1234`.
8. Change a stock toggle.
9. Confirm the update.
10. Return to Emergency Locator / District Dashboard.
11. Show the updated status and timestamp.

## Safety

This is a hackathon prototype, not a medical diagnosis or emergency-response service. Stock information may be stale or incorrect. In a real emergency, users should contact appropriate local emergency/medical services and verify availability by phone.
