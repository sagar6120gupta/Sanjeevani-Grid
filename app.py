import streamlit as st
from datetime import datetime

from database import init_db, get_dashboard_stats
from pages.user_portal import render_user_portal
from pages.staff_portal import render_staff_portal
from pages.dashboard import render_dashboard

st.set_page_config(
    page_title="Sanjeevani Grid",
    page_icon="🚑",
    layout="wide",
    initial_sidebar_state="expanded",       
)

init_db()

st.markdown("""
<style>
.main-header { 
    padding: 0.8rem 0 0.2rem 0;
}
.badge {
    display:inline-block;
    padding:0.25rem 0.55rem;
    border-radius:999px;
    background:#e8f5e9;
    font-size:0.82rem;
}
.small-muted {
    color:#6b7280;
    font-size:0.85rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">', unsafe_allow_html=True)
st.title("🚑 Sanjeevani Grid")
st.caption("Hyperlocal emergency life-saving supply tracker")
st.markdown("</div>", unsafe_allow_html=True)

with st.sidebar:
    st.header("Navigation")
    page = st.radio(
        "Open",
        ["Emergency Locator", "PHC Staff Portal", "District Dashboard"],
        index=0,
    )
    st.divider()
    stats = get_dashboard_stats()
    st.metric("Connected PHCs", stats["total_phcs"])
    st.caption("Prototype data • refresh after staff stock updates")
    st.divider()
    st.caption("Dev Squad • Deviathon 2.0")

if page == "Emergency Locator":
    try:
        render_user_portal()
    except TypeError as error:
        if "streamlit_geolocation" in str(error):
            st.error(
                "GPS component configuration error. "
                "Open pages/user_portal.py and check the "
                "streamlit_geolocation() arguments."
            )
        else:
            raise
elif page == "PHC Staff Portal":
    render_staff_portal()
else:
    render_dashboard()

