import streamlit as st

from database import get_all_phcs, get_phc, update_stock

DEMO_PIN = "1234"

def render_staff_portal():
    st.header("🏥 PHC Staff Portal")
    st.caption("Demo portal for the hackathon prototype.")

    with st.expander("🔐 Demo access"):
        st.write("For this prototype, use the demo PIN: **1234**")

    pin = st.text_input("Staff PIN", type="password")
    if pin != DEMO_PIN:
        st.info("Enter the demo PIN to access stock controls.")
        return

    phcs = get_all_phcs()
    options = {f'{p["name"]} — {p["address"]}': p["id"] for p in phcs}
    selected = st.selectbox("Select your PHC", list(options.keys()))
    phc_id = options[selected]
    phc = get_phc(phc_id)

    st.subheader(f'📦 Emergency Stock — {phc["name"]}')

    current = {
        "antivenom": bool(phc["antivenom"]),
        "rabies_vaccine": bool(phc["rabies_vaccine"]),
        "oneg_blood": bool(phc["oneg_blood"]),
        "oxygen": bool(phc["oxygen"]),
    }

    with st.form("stock_form"):
        antivenom = st.toggle("🐍 Anti-venom in stock", value=current["antivenom"])
        rabies = st.toggle("💉 Rabies vaccine in stock", value=current["rabies_vaccine"])
        oneg = st.toggle("🩸 O-negative blood in stock", value=current["oneg_blood"])
        oxygen = st.toggle("🫁 Oxygen available", value=current["oxygen"])

        submitted = st.form_submit_button(
            "✅ Confirm Today's Stock",
            type="primary",
            use_container_width=True
        )

    if submitted:
        update_stock(phc_id, {
            "antivenom": antivenom,
            "rabies_vaccine": rabies,
            "oneg_blood": oneg,
            "oxygen": oxygen,
        })
        st.success("Stock updated successfully. The public locator will use the new status.")
        st.rerun()

    st.divider()
    st.caption(
        "Design principle: one quick daily confirmation is enough for the prototype. "
        "A production system should use authenticated staff accounts and audit logs."
    )
