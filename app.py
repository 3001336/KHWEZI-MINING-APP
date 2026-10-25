import streamlit as st

# --- MEMBER 1: FRONT-END & UI (DEMONSTRATION SHELL) ---
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
                m1.metric("System Operational Status", "Online", "Demo")
                m2.metric("Data Feed Latency", "12 ms", "Sample")
                m3.metric("Active Safety Compliance", "96.5%", "+1.1%")
                st.info("Dashboard shell loaded. KPI values are examples; backend telemetry integration is pending.")
            else:
                st.subheader(f"Module View: {tab_name}")
                st.write(
                    f"The structural layout for **{tab_name}** is visible under "
                    f"**{tier}** demo permissions. Backend data hooks pending."
                )


# --- APP FLOW ROUTING ---
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = False

if not st.session_state["auth_token"]:
    render_access_gate()
else:
    render_main_interface()

# ADD THIS CODE ABOVE YOUR EXISTING APP FLOW ROUTING
# ORIGINAL FUNCTIONS AND KPI VALUES ARE NOT CHANGED

import pandas as pd
import altair as alt

st.markdown("""
<style>

/* MAIN MINING DASHBOARD BACKGROUND */
[data-testid="stAppViewContainer"] {
    background: linear-gradient(
        115deg,
        #f8f6f2,
        #fffaf2,
        #eef1ee
    );
}

/* COAL BLACK NAVIGATION SIDEBAR */
[data-testid="stSidebar"] {
    background: linear-gradient(
        160deg,
        #151b22,
        #252e38,
        #11171d
    );
    border-right: 4px solid #d9a441;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #f4c96a !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] .stCaption {
    color: #f5f2e9 !important;
}

/* NAVIGATION SELECTION */
[data-testid="stSidebar"] [data-baseweb="select"] {
    border-radius: 9px;
}

/* SIDEBAR LOGOUT BUTTON */
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(
        110deg,
        #f0c66a,
        #d6a037
    );
    color: #1b242b;
    border: none;
    border-radius: 9px;
    font-weight: bold;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: #b97845;
    color: white;
}

/* DASHBOARD METRIC CARDS */
[data-testid="stMetric"] {
    background: white;
    border-left: 6px solid #d6a037;
    border-radius: 15px;
    padding: 20px;
    min-height: 145px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.08);
    transition: transform 0.2s ease;
}

[data-testid="stMetric"]:hover {
    transform: translateY(-4px);
}

[data-testid="stMetricLabel"] {
    color: #535d63;
    font-weight: 500;
}

[data-testid="stMetricValue"] {
    color: #202a30;
    font-weight: bold;
}

/* DASHBOARD HEADINGS */
h1, h2, h3 {
    color: #202a30;
}

/* INFORMATION BANNER */
[data-testid="stAlert"] {
    border-radius: 10px;
}

/* CHART CONTAINER */
[data-testid="stVerticalBlockBorderWrapper"] {
    border-radius: 14px;
}

/* MAIN DASHBOARD SPACING */
.block-container {
    max-width: 1500px;
    padding-top: 2rem;
    padding-bottom: 2rem;
}

</style>
""", unsafe_allow_html=True)


# KEEP A REFERENCE TO THE ORIGINAL INTERFACE
original_render_main_interface = render_main_interface


def render_mining_dashboard():

    tag = st.session_state["id_tag"]
    tier = st.session_state["tier"]

    # ORIGINAL ROLE PERMISSIONS
    available_modules = ["View Dashboard"]

    if tier in [
        "Administrator",
        "Safety Officer",
        "Mining Engineer",
        "Manager"
    ]:
        available_modules.extend([
            "Worker Safety Logs",
            "Incident Reports",
            "Risk Matrix"
        ])

    if tier in [
        "Administrator",
        "Mining Engineer",
        "Maintenance Engineer",
        "Manager"
    ]:
        available_modules.extend([
            "Equipment Telemetry",
            "Maintenance Schedules"
        ])

    available_modules.append("Operational Reports")

    if tier == "Administrator":
        available_modules.append("User Control Panel")

    available_modules.append("Original Interface")

    # LEFT NAVIGATION MENU
    with st.sidebar:

        st.markdown("## ⛏️ Navigation Menu")

        st.write(f"**User:** {tag}")
        st.write(f"**Role:** {tier}")

        st.divider()

        selected_module = st.selectbox(
            "Select Function",
            available_modules
        )

        st.divider()

        if st.button("Log Out"):

            st.session_state["auth_token"] = False
            st.session_state.pop("id_tag", None)
            st.session_state.pop("tier", None)

            st.rerun()

        st.caption("KHWEZI MINING OPERATIONS PORTAL")

    # CENTRAL MONITORING DASHBOARD
    if selected_module == "View Dashboard":

        st.markdown(
            "**School of Mining Engineering | "
            "University of the Witwatersrand**"
        )

        st.markdown(
            "*A centralized digital monitoring platform "
            "for operational decision-making.*"
        )

        st.divider()

        st.subheader("📊 Central Monitoring Dashboard")

        # READ ACTUAL KPI DATA WHEN AVAILABLE
        # NO DEMONSTRATION NUMBERS ARE INSERTED
        kpis = st.session_state.get("mining_kpis", {})

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Workers",
                kpis.get("total_workers", "—")
            )

        with col2:
            st.metric(
                "Safety Incidents",
                kpis.get("safety_incidents", "—")
            )

        with col3:
            st.metric(
                "Equipment Availability",
                kpis.get("equipment_availability", "—")
            )

        with col4:
            st.metric(
                "Critical Alerts",
                kpis.get("critical_alerts", "—")
            )

        st.info(
            "💡 Use the sidebar navigation menu "
            "to access specific system modules."
        )

        # EQUIPMENT MONITORING
        st.subheader("🚜 Equipment Monitoring Analysis")

        with st.container(border=True):

            st.markdown("**Equipment Availability (%)**")

            equipment_source = st.session_state.get(
                "equipment_data"
            )

            if equipment_source is not None:

                equipment_df = pd.DataFrame(equipment_source)

                required_columns = {
                    "Equipment_ID",
                    "Availability"
                }

                if required_columns.issubset(
                    equipment_df.columns
                ):

                    equipment_df["Availability"] = (
                        pd.to_numeric(
                            equipment_df["Availability"],
                            errors="coerce"
                        )
                    )

                    equipment_df = equipment_df.dropna(
                        subset=["Availability"]
                    )

                    if not equipment_df.empty:

                        chart = (
                            alt.Chart(equipment_df)
                            .mark_bar(
                                color="#d6a037",
                                cornerRadiusTopLeft=5,
                                cornerRadiusTopRight=5
                            )
                            .encode(
                                x=alt.X(
                                    "Equipment_ID:N",
                                    title="Equipment ID",
                                    sort=None
                                ),
                                y=alt.Y(
                                    "Availability:Q",
                                    title="Availability (%)",
                                    scale=alt.Scale(
                                        domain=[0, 100]
                                    )
                                ),
                                tooltip=[
                                    "Equipment_ID:N",
                                    "Availability:Q"
                                ]
                            )
                            .properties(height=350)
                        )

                        st.altair_chart(
                            chart,
                            use_container_width=True
                        )

                    else:
                        st.info(
                            "Equipment readings are not "
                            "available yet."
                        )

                else:
                    st.info(
                        "Equipment data must include "
                        "Equipment_ID and Availability."
                    )

            else:
                st.info(
                    "Connect equipment monitoring data "
                    "to display the availability chart."
                )

        # ORIGINAL SYSTEM INDICATORS
        with st.expander(
            "Original System Performance Indicators"
        ):

            m1, m2, m3 = st.columns(3)

            m1.metric(
                "System Operational Status",
                "Online",
                "Demo"
            )

            m2.metric(
                "Data Feed Latency",
                "12 ms",
                "Sample"
            )

            m3.metric(
                "Active Safety Compliance",
                "96.5%",
                "+1.1%"
            )

    # KEEP ORIGINAL INTERFACE AVAILABLE
    elif selected_module == "Original Interface":

        original_render_main_interface()

    # ORIGINAL MODULE ACCESS STRUCTURE
    else:

        st.subheader(f"Module View: {selected_module}")

        st.write(
            f"The structural layout for "
            f"**{selected_module}** is visible under "
            f"**{tier}** demo permissions. "
            f"Backend data hooks pending."
        )


# CONNECT THE NEW LAYOUT TO THE ORIGINAL APP ROUTING
render_main_interface = render_mining_dashboard
