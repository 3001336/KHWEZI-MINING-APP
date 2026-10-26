import streamlit as st
import pandas as pd
import altair as alt
import importlib
from pathlib import Path

# IMPORTANT: Each team member owns a separate .py file.
# Each file must define a render_... function that takes role as input.
# No st.set_page_config(), login, or app execution inside member files.
BASE = Path(__file__).resolve().parent

MEMBER_MODULES = {
    "Worker Safety Logs": ("person1_worker_safety_module", "render_worker_safety"),
    "Incident Reports": ("safety_incidents", "render_incident_reports"),
    "Risk Matrix": ("risk_assessment", "render_risk_assessment"),
    "Equipment Telemetry": ("equipment_page", "render_equipment_module"),
    "Maintenance Schedules": ("equipment_page", "render_equipment_module"),
    "Equipment Database": ("equipment_page", "render_equipment_module"),
    "Condition Monitoring": ("equipment_page", "render_equipment_module"),
    "Equipment Alerts": ("equipment_page", "render_equipment_module"),
    "Equipment Analysis": ("equipment_page", "render_equipment_module"),
    "Operational Reports": ("person4_dashboard", "render_dashboard"),
    "User Control Panel": ("user_control", "render_user_control"),
}


def render_member_page(page_name, role):
    """Call one person's code without breaking the rest of the application."""
    filename, function_name = MEMBER_MODULES[page_name]
    if not (BASE / f"{filename}.py").exists():
        st.info(f"{page_name} is not connected yet. Upload {filename}.py to GitHub.")
        st.code(f"def {function_name}(role):\n    st.title('{page_name}')")
        return
    try:
        module = importlib.import_module(filename)
        function = getattr(module, function_name, None)
        if function is None or not callable(function):
            st.error(f"{filename}.py must define {function_name}(role).")
            return
        function(role)
    except Exception as exc:
        st.error(f"Error in {filename}.py: {exc}")
        st.exception(exc)


def load_equipment_summary():
    try:
        em = importlib.import_module("equipment_module")
        data = em.prepare(em.load_equipment())
        alerts = em.generate_alerts(data)
        stats = em.equipment_kpis(data, alerts)
        return data, stats
    except Exception:
        return None, None


def load_worker_count():
    try:
        worker_module = importlib.import_module("person1_worker_safety_module")
        return len(worker_module.load_workers())
    except Exception:
        return None


# KHWEZI MINING - COAL MINE DASHBOARD

st.set_page_config(
    page_title="Khwezi Mining | Coal Operations",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# COAL MINING COLOURS AND DESIGN
st.markdown("""
<style>
:root {
    --coal: #171d23;
    --coal-deep: #10151b;
    --coal-mid: #27333b;
    --gold: #d9a435;
    --gold-light: #f1c86e;
    --copper: #ad7041;
    --stone: #f6f3ec;
    --ink: #26313a;
}

/* MAIN BACKGROUND */
[data-testid="stAppViewContainer"] {
    background:
        radial-gradient(
            circle at 93% 8%,
            #f7ebc9 0%,
            transparent 31%
        ),
        linear-gradient(
            115deg,
            #f7f3eb 0%,
            #fffdfa 49%,
            #edf1ee 100%
        );
}

[data-testid="stHeader"] {
    background: rgba(248,246,241,0.92);
}

[data-testid="stMain"] .block-container {
    max-width: 1400px;
    padding-top: 1.8rem;
    padding-bottom: 3rem;
}

/* FIX TEXT VISIBILITY */
[data-testid="stMain"] h1,
[data-testid="stMain"] h2,
[data-testid="stMain"] h3,
[data-testid="stMain"] h4,
[data-testid="stMain"] p,
[data-testid="stMain"] label {
    color: #26313a;
}

/* COAL BLACK LEFT SIDEBAR */
[data-testid="stSidebar"] {
    background:
        repeating-linear-gradient(
            168deg,
            transparent 0px,
            transparent 28px,
            rgba(255,255,255,0.025) 29px,
            rgba(255,255,255,0.025) 31px
        ),
        linear-gradient(
            170deg,
            #12171e 0%,
            #27313a 65%,
            #151b22 100%
        );
    border-right: 4px solid #d9a435;
}

@media (min-width: 900px) {
    [data-testid="stSidebar"] {
        min-width: 305px !important;
        width: 305px !important;
    }

    [data-testid="stSidebar"] > div {
        width: 305px !important;
    }
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: #f1c86e !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] label {
    color: #f6f0e2 !important;
}

/* NAVIGATION DROPDOWN */
[data-testid="stSidebar"]
[data-baseweb="select"] > div {
    background: #fffdf7;
    border: 1px solid #ba9044;
    border-radius: 9px;
    color: #202932;
}

[data-testid="stSidebar"]
[data-baseweb="select"] span {
    color: #202932 !important;
}

/* GOLD LOGOUT BUTTON */
[data-testid="stSidebar"] .stButton button {
    background: linear-gradient(
        110deg,
        #f1c767,
        #d6a033
    );
    border: 1px solid #bd8c2c;
    border-radius: 9px;
    color: #192128;
    font-weight: 700;
    padding: 0.55rem 1.2rem;
}

[data-testid="stSidebar"] .stButton button:hover {
    background: #ad7041;
    color: white;
}

/* COAL-MINE HEADER */
.mine-hero {
    position: relative;
    overflow: hidden;
    border-radius: 15px;
    padding: 23px 28px;
    margin-bottom: 20px;
    background:
        repeating-linear-gradient(
            166deg,
            transparent 0,
            transparent 25px,
            rgba(255,255,255,0.035) 26px,
            rgba(255,255,255,0.035) 28px
        ),
        linear-gradient(
            107deg,
            #121820 0%,
            #29343c 73%,
            #3b3326 100%
        );
    border-left: 7px solid #d9a435;
    box-shadow: 0 8px 20px rgba(26,29,32,0.15);
}

.mine-eyebrow {
    color: #ebbb54;
    font-size: 0.83rem;
    font-weight: 800;
    letter-spacing: 0.14em;
}

.mine-title {
    color: white !important;
    font-size: 2rem;
    font-weight: 800;
    line-height: 1.22;
    margin-top: 5px;
}

.mine-subtitle {
    color: #e5ded0 !important;
    font-size: 0.95rem;
    margin-top: 8px;
}

.mine-school {
    margin-bottom: 5px;
    font-weight: 750;
    color: #28343b;
}

.mine-intro {
    font-style: italic;
    color: #57616a;
    margin-bottom: 23px;
}

.mine-section {
    font-size: 1.55rem;
    font-weight: 800;
    color: #242f36;
    margin: 29px 0 12px;
}

/* FOUR DASHBOARD KPI CARDS */
[data-testid="stMetric"] {
    background: white;
    border-left: 6px solid #d9a435;
    border-radius: 15px;
    padding: 18px 17px;
    min-height: 141px;
    box-shadow: 0 6px 16px rgba(27,33,36,0.09);
}

[data-testid="stMetricLabel"] p {
    color: #58636a !important;
    font-size: 0.88rem;
}

[data-testid="stMetricValue"] {
    color: #263139 !important;
    font-weight: 780;
}

.guide-banner {
    background: #f5e9d0;
    border-left: 4px solid #d9a435;
    color: #665125;
    border-radius: 9px;
    padding: 16px 18px;
    margin: 18px 0 20px;
}

/* EQUIPMENT CHART */
[data-testid="stVerticalBlockBorderWrapper"] {
    background: white;
    border-radius: 13px;
    border-color: #e7dfd0;
}

@media (max-width: 750px) {
    .mine-title {
        font-size: 1.4rem;
    }

    .mine-hero {
        padding: 19px;
    }
}
</style>
""", unsafe_allow_html=True)


# DEMONSTRATION DATA
# REPLACE WITH ACTUAL MINING RECORDS WHEN AVAILABLE

DEMO_KPIS = {
    "total_workers": 142,
    "safety_incidents": 3,
    "equipment_availability": 96.6,
    "critical_alerts": 1
}

DEMO_EQUIPMENT = pd.DataFrame({
    "Equipment_ID": [
        "EQ-101",
        "EQ-102",
        "EQ-103",
        "EQ-104",
        "EQ-105"
    ],
    "Equipment": [
        "Haul Truck",
        "Excavator",
        "Loader",
        "Drill Rig",
        "Dozer"
    ],
    "Availability": [
        99.0,
        97.8,
        98.1,
        94.8,
        93.3
    ],
    "Condition": [
        "Operational",
        "Operational",
        "Operational",
        "Attention",
        "Critical"
    ]
})


# ORIGINAL LOGIN INTERFACE
def render_access_gate():

    st.markdown("""
    <div class="mine-hero">
        <div class="mine-eyebrow">
            ⛏️ KHWEZI MINING • COAL OPERATIONS
        </div>
        <div class="mine-title">
            Health, Safety &amp; Equipment Portal
        </div>
        <div class="mine-subtitle">
            School of Mining Engineering |
            University of the Witwatersrand
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.subheader("🔐 Security & Access Control Gateway")

    st.write(
        "Enter a staff ID and select a demo clearance "
        "group to view the available modules."
    )

    operator_id = st.text_input(
    "Enter Staff Identification Number:",
    key="khwezi_staff_id"
)
    access_level = st.selectbox(
        "Select Clearance Group (Table 1):",
        [
            "Administrator",
            "Safety Officer",
            "Mining Engineer",
            "Maintenance Engineer",
            "Manager"
        ]
    )

    if st.button("Unlock Dashboard Interface"):

        if not operator_id.strip():
            st.warning(
                "Validation Error: Identification field "
                "cannot be empty."
            )

        else:
            st.session_state["auth_token"] = True
            st.session_state["id_tag"] = operator_id.strip()
            st.session_state["tier"] = access_level
            st.rerun()


# ORIGINAL ROLE PERMISSIONS
def permitted_modules(tier):

    choices = ["View Dashboard"]

    if tier in [
        "Administrator",
        "Safety Officer",
        "Mining Engineer",
        "Manager"
    ]:
        choices.extend([
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
        choices.extend([
            "Equipment Telemetry",
            "Equipment Database",
            "Condition Monitoring",
            "Equipment Alerts",
            "Maintenance Schedules",
            "Equipment Analysis"
        ])

    choices.append("Operational Reports")

    if tier == "Administrator":
        choices.append("User Control Panel")

    return choices


# EQUIPMENT MONITORING CHART
def render_equipment_chart():

    df = st.session_state.get(
        "equipment_data",
        DEMO_EQUIPMENT
    )

    df = pd.DataFrame(df)

    required = {"Equipment_ID", "Availability"}

    if not required.issubset(df.columns):
        st.info(
            "Equipment data needs Equipment_ID "
            "and Availability columns."
        )
        return

    df["Availability"] = pd.to_numeric(
        df["Availability"],
        errors="coerce"
    )

    df = df.dropna(subset=["Availability"])

    if df.empty:
        st.info("Equipment readings are not available yet.")
        return

    if "Condition" not in df.columns:
        df["Condition"] = "Operational"

    if "Equipment" not in df.columns:
        df["Equipment"] = df["Equipment_ID"]

    with st.container(border=True):

        st.markdown("**Equipment Availability (%)**")

        chart = (
            alt.Chart(df)
            .mark_bar(
                cornerRadiusTopLeft=4,
                cornerRadiusTopRight=4
            )
            .encode(
                x=alt.X(
                    "Equipment_ID:N",
                    title="Equipment ID",
                    sort=None,
                    axis=alt.Axis(labelAngle=0)
                ),

                y=alt.Y(
                    "Availability:Q",
                    title="Availability (%)",
                    scale=alt.Scale(domain=[0, 100])
                ),

                color=alt.Color(
                    "Condition:N",
                    title="Equipment Condition",
                    scale=alt.Scale(
                        domain=[
                            "Operational",
                            "Attention",
                            "Critical"
                        ],
                        range=[
                            "#d9a435",
                            "#ad7041",
                            "#c54c43"
                        ]
                    )
                ),

                tooltip=[
                    "Equipment_ID:N",
                    "Equipment:N",
                    "Availability:Q",
                    "Condition:N"
                ]
            )
            .properties(height=285)
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )


# MAIN DASHBOARD WITH LEFT NAVIGATION
def render_main_interface():

    tag = st.session_state["id_tag"]
    tier = st.session_state["tier"]

    # LEFT SIDEBAR
    with st.sidebar:

        st.markdown("## ⛏️ Navigation Menu")

        st.write(f"**User:** {tag}")
        st.write(f"**Role:** {tier}")

        st.markdown(
            "<div style='height:68px'></div>",
            unsafe_allow_html=True
        )

        selected = st.selectbox(
            "Select Function",
            permitted_modules(tier)
        )

        st.markdown(
            "<div style='height:50px'></div>",
            unsafe_allow_html=True
        )

        if st.button("Log Out"):

            st.session_state["auth_token"] = False
            st.session_state.pop("id_tag", None)
            st.session_state.pop("tier", None)

            st.rerun()

        st.caption("KHWEZI MINING • COAL OPERATIONS")

    # COAL MINE BANNER
    st.markdown("""
    <div class="mine-hero">
        <div class="mine-eyebrow">
            ⛏️ KHWEZI MINING • COAL OPERATIONS
        </div>
        <div class="mine-title">
            Health, Safety &amp; Equipment Portal
        </div>
        <div class="mine-subtitle">
            Operational monitoring • Worker safety • Mine equipment
        </div>
    </div>

    <div class="mine-school">
        School of Mining Engineering |
        University of the Witwatersrand
    </div>

    <div class="mine-intro">
        A centralized digital monitoring platform
        for operational decision-making.
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    # MAIN DASHBOARD
    if selected == "View Dashboard":

        st.markdown(
            '<div class="mine-section">'
            '📊 Central Monitoring Dashboard'
            '</div>',
            unsafe_allow_html=True
        )

        data, stats = load_equipment_summary()
        worker_count = load_worker_count()
        kpis = {
            "total_workers": worker_count if worker_count is not None else "No data",
            "safety_incidents": "Not connected",
            "equipment_availability": (f"{stats['avg_availability']:.1f}%" if stats else "No data"),
            "critical_alerts": (stats["critical_alerts"] if stats else "No data"),
        }
        if data is not None:
            st.session_state["equipment_data"] = data

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric(
                "Total Workers",
                kpis["total_workers"],
                "Active"
            )

        with col2:
            st.metric(
                "Safety Incidents",
                kpis["safety_incidents"],
            )

        with col3:
            st.metric(
                "Equipment Availability",
                kpis["equipment_availability"]
            )

        with col4:
            st.metric(
                "Critical Alerts",
                kpis["critical_alerts"],
            )

        st.markdown(
            '<div class="guide-banner">'
            '💡 Use the sidebar navigation menu '
            'to access specific system modules.'
            '</div>',
            unsafe_allow_html=True
        )

        st.markdown(
            '<div class="mine-section">'
            '🚜 Equipment Monitoring Analysis'
            '</div>',
            unsafe_allow_html=True
        )

        if data is not None:
            render_equipment_chart()
        else:
            st.info("Equipment data will appear here when equipment_module.py and equipment_data.csv are available.")

        # ORIGINAL SYSTEM KPI VALUES
        with st.expander(
            "Original System Performance Indicators"
        ):

            a, b, c = st.columns(3)

            a.metric(
                "System Operational Status",
                "Online",
                "Demo"
            )

            b.metric(
                "Data Feed Latency",
                "12 ms",
                "Sample"
            )

            c.metric(
                "Active Safety Compliance",
                "96.5%",
                "+1.1%"
            )

        st.caption(
            "Dashboard and equipment values are "
            "demonstration data until connected "
            "to actual mine records."
        )

    # -----------------------------------------------------------------
    # INTEGRATION POINT: each member supplies a callable Python module.
    # This handles safety, incidents, risks, equipment, and analytics.
    # -----------------------------------------------------------------
    elif selected in MEMBER_MODULES:
        render_member_page(selected, tier)

    else:
        st.warning(f"No page has been configured for: {selected}")


# Only app.py owns page configuration, session routing and sidebar.
if "auth_token" not in st.session_state:
    st.session_state["auth_token"] = False

if not st.session_state["auth_token"]:
    render_access_gate()
else:
    render_main_interface()
