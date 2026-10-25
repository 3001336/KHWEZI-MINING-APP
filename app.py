import streamlit as st


st.set_page_config(
    page_title="Khwezi Mining Portal - UI Shell",
    page_icon="⚙️",
    layout="wide",
)

# Custom structural styling (card-based layout)
st.markdown(
    """
    <style>
    .card {
        padding: 20px;
        border-radius: 10px;
        background-color: #ffffff;
        box-shadow: 2px 2px 10px rgba(0, 0, 0, 0.05);
        margin-bottom: 20px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Application banner
st.title("Khwezi Mining | Health, Safety & Equipment UI")
st.caption("System Architecture & Front-End Interface Shell (Member 1 Deliverable)")
st.divider()


# --- FUNCTION FOR ACCESS CONTROL (DEMO RBAC UI) ---
def render_access_gate():
    st.markdown("### 🔐 Security & Access Control Gateway")
    st.write("Enter a staff ID and select a demo clearance group to view the available modules.")

    operator_id = st.text_input("Enter Staff Identification Number:")
    access_level = st.selectbox(
        "Select Clearance Group (Table 1):",
        [
            "Administrator",
            "Safety Officer",
            "Mining Engineer",
            "Maintenance Engineer",
            "Manager",
        ],
    )

    if st.button("Unlock Dashboard Interface"):
        if not operator_id.strip():
            st.warning("Validation Error: Identification field cannot be empty.")
        else:
            st.session_state["auth_token"] = True
            st.session_state["id_tag"] = operator_id.strip()
            st.session_state["tier"] = access_level
            st.rerun()


# --- FUNCTION FOR MAIN DASHBOARD SHELL ---
def render_main_interface():
    tag = st.session_state["id_tag"]
    tier = st.session_state["tier"]

    # Top bar control panel
    top_col1, top_col2 = st.columns([8, 2])
    top_col1.success(f"Active Demo Session: **{tag}** | Clearance: **{tier}**")
    if top_col2.button("Terminate Session"):
        st.session_state["auth_token"] = False
        st.session_state.pop("id_tag", None)
        st.session_state.pop("tier", None)
        st.rerun()

    st.divider()
    st.markdown("#### Operational Workspace Navigation")

    # Build tabs dynamically based on selected demo clearance
    tab_labels = ["Main KPI Dashboard"]

    if tier in ["Administrator", "Safety Officer", "Mining Engineer", "Manager"]:
        tab_labels.extend(["Worker Safety Logs", "Incident Reports", "Risk Matrix"])

    if tier in ["Administrator", "Mining Engineer", "Maintenance Engineer", "Manager"]:
        tab_labels.extend(["Equipment Telemetry", "Maintenance Schedules"])

    tab_labels.append("Operational Reports")

    if tier == "Administrator":
        tab_labels.append("User Control Panel")

    created_tabs = st.tabs(tab_labels)

    for i, tab_name in enumerate(tab_labels):
        with created_tabs[i]:
            if tab_name == "Main KPI Dashboard":
                st.subheader("Central Performance Indicators")
                m1, m2, m3 = st.columns(3)
