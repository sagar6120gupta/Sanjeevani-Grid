import streamlit as st
import streamlit.components.v1 as components
import folium
from streamlit_folium import st_folium
from streamlit_geolocation import streamlit_geolocation

from database import get_all_phcs
from distance import find_nearby

SUPPLIES = {
    "🐍 Anti-venom": "antivenom",
    "💉 Rabies vaccine": "rabies_vaccine",
    "🩸 O-negative blood": "oneg_blood",
    "🫁 Oxygen": "oxygen",
}

def speak_hindi(text):
    # Browser-native speech synthesis: no audio API key required.
    safe = text.replace("\\", "\\\\").replace("'", "\\'")
    html = f"""
    <script>
    const text = '{safe}';
    const u = new SpeechSynthesisUtterance(text);
    u.lang = 'hi-IN';
    u.rate = 0.9;
    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(u);
    </script>
    """
    components.html(html, height=0)

def render_user_portal():
    st.header("🚨 Emergency Locator")
    st.write("Find nearby facilities carrying the emergency supply you need.")

    supply_label = st.selectbox(
        "What emergency supply do you need?",
        list(SUPPLIES.keys())
    )
    supply_key = SUPPLIES[supply_label]

    st.subheader("📍 Your Location")

    location = streamlit_geolocation()
    st.write("GPS response:", location)
    gps_ok = (
        isinstance(location, dict)
        and location.get("latitude") is not None
        and location.get("longitude") is not None
    )

    if gps_ok:
        user_lat = float(location["latitude"])
        user_lon = float(location["longitude"])
        accuracy = location.get("accuracy")
        st.success(
            f"GPS location detected: {user_lat:.5f}, {user_lon:.5f}"
            + (f" • accuracy ~{accuracy:.0f} m" if accuracy else "")
        )
    else:
        st.info("If GPS is unavailable, enter coordinates manually for the demo.")
        c1, c2 = st.columns(2)
        user_lat = c1.number_input("Latitude", value=27.4924, format="%.6f")
        user_lon = c2.number_input("Longitude", value=77.6737, format="%.6f")

    if st.button("🔎 Find Emergency Help", type="primary", use_container_width=True):
        st.session_state["search"] = {
            "lat": user_lat,
            "lon": user_lon,
            "supply": supply_key,
            "label": supply_label,
        }

    search = st.session_state.get("search")
    if not search:
        st.divider()
        st.info("Press “Find Emergency Help” to search within 30 km.")
        return

    user_lat = search["lat"]
    user_lon = search["lon"]
    supply_key = search["supply"]
    supply_label = search["label"]

    phcs = get_all_phcs()
    results = find_nearby(phcs, user_lat, user_lon, supply_key, radius_km=30)

    st.subheader(f"📡 Results for {supply_label}")

    available = [r for r in results if r["available"] and r["freshness"] == "CURRENT"]

    if not available:
        st.warning(
            "No nearby facility is currently confirmed with this supply. "
            "Facilities with other or unverified status are shown below."
        )

    if results:
        # Map
        m = folium.Map(location=[user_lat, user_lon], zoom_start=10)
        folium.Marker(
            [user_lat, user_lon],
            tooltip="Your location",
            popup="You",
            icon=folium.Icon(color="blue", icon="user", prefix="fa"),
        ).add_to(m)

        for r in results:
            color = "green" if r["available"] and r["freshness"] == "CURRENT" else (
                "red" if not r["available"] else "orange"
            )
            folium.Marker(
                [r["latitude"], r["longitude"]],
                tooltip=f'{r["name"]} • {r["distance_km"]:.1f} km',
                popup=(
                    f'<b>{r["name"]}</b><br>'
                    f'{supply_label}: {"AVAILABLE" if r["available"] else "OUT OF STOCK"}<br>'
                    f'{r["freshness_text"]}'
                ),
                icon=folium.Icon(color=color, icon="plus", prefix="fa"),
            ).add_to(m)

        st_folium(m, width=None, height=420, returned_objects=[])

        st.subheader("🏥 Nearby Facilities")

        for r in results:
            if r["available"] and r["freshness"] == "CURRENT":
                status = "🟢 AVAILABLE"
            elif not r["available"]:
                status = "🔴 OUT OF STOCK"
            else:
                status = "🟡 UNVERIFIED"

            st.markdown(f"### {status}  {r['name']}")
            c1, c2, c3 = st.columns([2, 2, 2])
            c1.write(f"📍 **{r['distance_km']:.1f} km** away")
            c2.write(f"🕒 {r['freshness_text']}")
            c3.write(r["address"])

            b1, b2 = st.columns(2)
            maps_url = (
                "https://www.google.com/maps/dir/?api=1"
                f"&origin={user_lat},{user_lon}"
                f"&destination={r['latitude']},{r['longitude']}"
            )
            b1.link_button("🗺️ Get Directions", maps_url, use_container_width=True)
            b2.link_button("📞 Call PHC", f"tel:+{r['phone']}", use_container_width=True)

            if st.button(
                f"🔊 Hindi emergency guidance — {r['name']}",
                key=f"audio_{r['id']}"
            ):
                speak_hindi(
                    "कृपया शांत रहें। नजदीकी स्वास्थ्य केंद्र की ओर जाएं। "
                    "आपात स्थिति में स्थानीय आपातकालीन सेवा से संपर्क करें।"
                )

            st.divider()
    else:
        st.error("No PHCs were found within 30 km of the selected location.")
