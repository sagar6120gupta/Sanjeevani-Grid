import streamlit as st
from database import get_dashboard_stats, get_all_phcs
from distance import freshness_status

def render_dashboard():
    st.header("📊 District Dashboard")
    st.caption("Prototype operational view for Sanjeevani Grid.")

    if st.button("🔄 Refresh Dashboard"):
        st.rerun()

    stats = get_dashboard_stats()

    cols = st.columns(5)
    cols[0].metric("Connected PHCs", stats["total_phcs"])
    cols[1].metric("Anti-venom", stats["antivenom"])
    cols[2].metric("Rabies vaccine", stats["rabies_vaccine"])
    cols[3].metric("O-negative", stats["oneg_blood"])
    cols[4].metric("Oxygen", stats["oxygen"])

    st.divider()
    st.subheader("🩺 Facility status")

    phcs = get_all_phcs()
    rows = []
    for p in phcs:
        freshness, text = freshness_status(p["last_updated"])
        rows.append({
            "PHC": p["name"],
            "Anti-venom": "🟢" if p["antivenom"] else "🔴",
            "Rabies": "🟢" if p["rabies_vaccine"] else "🔴",
            "O-negative": "🟢" if p["oneg_blood"] else "🔴",
            "Oxygen": "🟢" if p["oxygen"] else "🔴",
            "Verification": "🟢 Current" if freshness == "CURRENT" else "🟡 Unverified",
            "Last update": text,
        })

    st.dataframe(rows, use_container_width=True, hide_index=True)

    st.info(
        "Green means the selected supply is reported in stock. "
        "Yellow means the facility has not confirmed its inventory within 24 hours."
    )
