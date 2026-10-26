
import streamlit as st
import base64
import pandas as pd
import altair as alt
import importlib
from pathlib import Path

# =====================================================
# KHWEZI MINING - MAIN APPLICATION
# =====================================================

BASE = Path(__file__).resolve().parent

# =====================================================
# ALL GROUP MEMBERS' MODULES
# =====================================================

MEMBER_MODULES = {
    "Worker Safety Logs": (
        "person1_worker_safety_module",
        "render_worker_safety"
    ),
    "Incident Reports": (
        "safety_incidents",
        "render_incident_reports"
    ),
    "Risk Matrix": (
        "risk_assessment",
        "render_risk_assessment"
    ),
    "Equipment Telemetry": (
        "equipment_page",
        "render_equipment_module"
    ),
    "Equipment Database": (
        "equipment_page",
        "render_equipment_module"
    ),
    "Condition Monitoring": (
        "equipment_page",
        "render_equipment_module"
    ),
    "Equipment Alerts": (
        "equipment_page",
        "render_equipment_module"
    ),
    "Maintenance Schedules": (
        "equipment_page",
        "render_equipment_module"
    ),
    "Equipment Analysis": (
        "equipment_page",
        "render_equipment_module"
    ),
    "Operational Reports": (
        "person4_dashboard",
        "render_dashboard"
    ),
    "User Control Panel": (
        "user_control",
        "render_user_control"
    ),
}

SAFETY_ROLES = {
    "Administrator",
    "Safety Officer",
    "Mining Engineer",
    "Manager"
}

EQUIPMENT_ROLES = {
    "Administrator",
    "Mining Engineer",
    "Maintenance Engineer",
    "Manager"
}

# =====================================================
# STREAMLIT PAGE CONFIGURATION
# =====================================================

st.set_page_config(
    page_title="KHWEZI MINING | Coal Operations",
    page_icon="⛏️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# COAL MINING COLOURS AND DESIGN
# =====================================================

st.markdown("""
<style>

:root {
    --coal: #161e25;
    --gold: #d9a435;
    --copper: #ad7041;
}

[data-testid="stAppViewContainer"] {
    background:
        linear-gradient(
            110deg,
            #f7f3eb,
            #fffdfa 50%,
            #edf1ee
        );
}

[data-testid="stHeader"] {
    background: rgba(250,248,244,.92);
}

[data-testid="stMain"] .block-container {
    max-width: 1400px;
    padding-top: 1.6rem;
}

[data-testid="stSidebar"] {
    background:
        linear-gradient(
            165deg,
            #111820 0%,
            #29343c 64%,
            #151c23 100%
        );
    border-right: 4px solid #d9a435;
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

[data-testid="stSidebar"]
[data-baseweb="select"] span {
    color: #26313a !important;
}

[data-testid="stSidebar"] .stButton button {
    background:
        linear-gradient(
            110deg,
            #f1c767,
            #d6a033
        );
    color: #172028;
    border-radius: 9px;
    font-weight: 700;
}

[data-testid="stMetric"] {
    background: white;
    border-left: 6px solid #d9a435;
    border-radius: 14px;
    padding: 18px;
    min-height: 125px;
    box-shadow:
        0 6px 16px rgba(25,34,39,.09);
}

.mine-hero {
    border-radius: 15px;
    padding: 27px 30px;
    margin-bottom: 18px;
    min-height: 195px;
    border-left: 7px solid #d9a435;
    background:
        linear-gradient(
            110deg,
            #121820,
            #29343c 70%,
            #3b3326
        );
    box-shadow:
        0 8px 22px rgba(26,29,32,.16);
}

.mine-eyebrow {
    color: #ebbb54;
    font-size: .86rem;
    letter-spacing: .12em;
    font-weight: 800;
}

.mine-title {
    color: white !important;
    font-size: 2rem;
    font-weight: 800;
    margin: 8px 0;
}

.mine-subtitle {
    color: #f0e9d9 !important;
    font-size: 1rem;
}

.mine-school {
    font-weight: 750;
    color: #28343b;
}

.mine-intro {
    font-style: italic;
    color: #57616a;
    margin: 5px 0 20px;
}

.mine-section {
    font-size: 1.45rem;
    font-weight: 800;
    color: #242f36;
    margin: 24px 0 14px;
}

.guide-banner {
    background: #f5e9d0;
    border-left: 4px solid #d9a435;
    border-radius: 9px;
    padding: 16px 18px;
    margin: 18px 0;
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

# =====================================================
# OPEN PIT MINING SUNSET IMAGE
# =====================================================

SUNSET_IMAGE = BASE / "mining_sunset.jpg"

if SUNSET_IMAGE.is_file():

    encoded = base64.b64encode(
        SUNSET_IMAGE.read_bytes()
    ).decode("ascii")

    st.markdown(
        f"""
        <style>
        .mine-hero {{
            background:
                linear-gradient(
                    90deg,
                    rgba(10,17,23,.88),
                    rgba(10,17,23,.18)
                ),
                url('data:image/jpeg;base64,{encoded}')
                center 55% / cover no-repeat !important;
        }}

        .mine-title,
        .mine-subtitle {{
            text-shadow:
                0 2px 5px rgba(0,0,0,.8);
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

# =====================================================
# MINING BANNER
# =====================================================

def show_banner():

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

# =====================================================
# ROLE-BASED NAVIGATION
# =====================================================

def permitted_modules(role):

    pages = ["View Dashboard"]

    if role in SAFETY_ROLES:
        pages.extend([
            "Worker Safety Logs",
            "Incident Reports",
            "Risk Matrix"
        ])

    if role in EQUIPMENT_ROLES:
        pages.extend([
            "Equipment Telemetry",
            "Equipment Database",
            "Condition Monitoring",
            "Equipment Alerts",
            "Maintenance Schedules",
            "Equipment Analysis"
        ])

    pages.append("Operational Reports")

    if role == "Administrator":
        pages.append("User Control Panel")

    return pages

# =====================================================
# CALL EACH GROUP MEMBER'S CODE
# =====================================================

def render_member_page(page_name, role):

    filename, function_name = MEMBER_MODULES[page_name]

    if not (BASE / f"{filename}.py").is_file():

        st.info(
            f"{page_name} is not connected yet. "
            f"Upload {filename}.py to GitHub."
        )

        st.code(
            f"def {function_name}(role):\n"
            f"    st.title('{page_name}')",
            language="python"
        )

        return

    try:

        module = importlib.import_module(filename)

        function = getattr(
            module,
            function_name,
            None
        )

        if not callable(function):

            st.error(
                f"{filename}.py must define "
                f"{function_name}(role)."
            )

            return

        function(role)

    except Exception as error:

        st.error(
            f"Error loading {page_name}: {error}"
        )

        st.exception(error)

# =====================================================
# EQUIPMENT DATA AND STATISTICS
# =====================================================

def load_equipment_summary():

    try:

        em = importlib.import_module(
            "equipment_module"
        )

        data = em.prepare(
            em.load_equipment()
        )

        alerts = em.generate_alerts(data)

        stats = em.equipment_kpis(
            data,
            alerts
        )

        return data, stats

    except Exception:
        return None, None

# =====================================================
# WORKER DATA
# =====================================================

def load_worker_count():

    try:

        module = importlib.import_module(
            "person1_worker_safety_module"
        )

        return len(module.load_workers())

    except Exception:
        return None

# =====================================================
# SAFETY INCIDENT DATA
# =====================================================

def load_incident_count():

    try:

        module = importlib.import_module(
            "safety_incidents"
        )

        if hasattr(module, "incident_summary"):

            return int(
                module.incident_summary()[
                    "total_incidents"
                ]
            )

        if hasattr(module, "list_incidents"):

            return len(
                module.list_incidents()
            )

    except Exception:
        pass

    return None

# =====================================================
# EQUIPMENT AVAILABILITY CHART
# =====================================================

def render_equipment_chart(data):

    if data is None:

        st.info(
            "Equipment data is unavailable. "
            "Check equipment_module.py "
            "and equipment_data.csv."
        )

        return

    df = pd.DataFrame(data).copy()

    required = {
        "Equipment_ID",
        "Availability"
    }

    if not required.issubset(df.columns):

        st.info(
            "Equipment data must contain "
            "Equipment_ID and Availability."
        )

        return

    df["Availability"] = pd.to_numeric(
        df["Availability"],
        errors="coerce"
    )

    df = df.dropna(
        subset=["Availability"]
    )

    if df.empty:

        st.info(
            "No valid equipment availability "
            "readings are available."
        )

        return

    if "Condition" not in df.columns:
        df["Condition"] = "Operational"

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
                sort=None
            ),

            y=alt.Y(
                "Availability:Q",
                title="Availability (%)",
                scale=alt.Scale(
                    domain=[0, 100]
                )
            ),

            color=alt.Color(
                "Condition:N",
                title="Condition"
            ),

            tooltip=[
                "Equipment_ID:N",
                "Availability:Q",
                "Condition:N"
            ]
        )
        .properties(height=285)
    )

    with st.container(border=True):

        st.markdown(
            "**Equipment Availability (%)**"
        )

        st.altair_chart(
            chart,
            use_container_width=True
        )

# =====================================================
# LOGIN SYSTEM
# =====================================================

def render_access_gate():

    show_banner()

    st.subheader(
        "🔐 Security & Access Control Gateway"
    )

    st.caption(
        "Academic demonstration login. "
        "Role selection is not secure authentication."
    )

    with st.form("demo_login"):

        operator_id = st.text_input(
            "Staff Identification Number"
        )

        role = st.selectbox(
            "Select Clearance Group",
            [
                "Administrator",
                "Safety Officer",
                "Mining Engineer",
                "Maintenance Engineer",
                "Manager"
            ]
        )

        submitted = st.form_submit_button(
            "Unlock Dashboard Interface"
        )

    if submitted:

        if not operator_id.strip():

            st.error(
                "Staff Identification Number "
                "cannot be empty."
            )

        else:

            st.session_state["auth_token"] = True

            st.session_state["id_tag"] = (
                operator_id.strip()
            )

            st.session_state["tier"] = role

            st.rerun()

# =====================================================
# MAIN INTERFACE
# =====================================================

def render_main_interface():

    role = st.session_state.get("tier", "")
    operator = st.session_state.get("id_tag", "")

    # =================================================
    # LEFT NAVIGATION
    # =================================================

    with st.sidebar:

        st.markdown(
            "## ⛏️ Navigation Menu"
        )

        st.write(
            f"**User:** {operator}"
        )

        st.write(
            f"**Role:** {role}"
        )

        st.markdown("---")

        selected = st.selectbox(
            "Select Function",
            permitted_modules(role)
        )

        st.markdown("---")

        if st.button("Log Out"):

            for key in (
                "auth_token",
                "tier",
                "id_tag"
            ):
                st.session_state.pop(
                    key,
                    None
                )

            st.rerun()

        st.caption(
            "KHWEZI MINING • COAL OPERATIONS"
        )

    show_banner()

    st.divider()

    # =================================================
    # MAIN DASHBOARD
    # =================================================

    if selected == "View Dashboard":

        st.markdown(
            '<div class="mine-section">'
            '📊 Central Monitoring Dashboard'
            '</div>',
            unsafe_allow_html=True
        )

        equipment, stats = load_equipment_summary()

        workers = load_worker_count()

        incidents = load_incident_count()

        availability = "No data"
        alerts = "No data"

        if stats is not None:

            if stats.get("avg_availability") is not None:

                availability = (
                    f"{float(stats['avg_availability']):.1f}%"
                )

            alerts = stats.get(
                "critical_alerts",
                "No data"
            )

        col1, col2, col3, col4 = st.columns(4)

        with col1:

            st.metric(
                "Total Workers",
                workers if workers is not None
                else "No data"
            )

        with col2:

            st.metric(
                "Safety Incidents",
                incidents if incidents is not None
                else "No data"
            )

        with col3:

            st.metric(
                "Equipment Availability",
                availability
            )

        with col4:

            st.metric(
                "Critical Equipment Alerts",
                alerts
            )

        st.markdown(
            '<div class="guide-banner">'
            '💡 Select a function from the sidebar '
            'to open each team member’s work.'
            '</div>',
            unsafe_allow_html=True
        )

        # =============================================
        # EQUIPMENT MONITORING
        # =============================================

        st.markdown(
            '<div class="mine-section">'
            '🚜 Equipment Monitoring Analysis'
            '</div>',
            unsafe_allow_html=True
        )

        render_equipment_chart(
            equipment
        )

        if equipment is not None:

            with st.expander(
                "View Equipment Records"
            ):

                st.dataframe(
                    equipment,
                    use_container_width=True,
                    hide_index=True
                )

        st.caption(
            "Connected counts are obtained from "
            "project records, not live mine telemetry."
        )

    # =================================================
    # OPERATIONAL REPORTS
    # =================================================

    elif (
        selected == "Operational Reports"
        and not (
            BASE / "person4_dashboard.py"
        ).is_file()
    ):

        st.subheader(
            "📥 Operational Reports"
        )

        st.info(
            "Upload person4_dashboard.py to display "
            "Member 4's analytics."
        )

        equipment, _ = load_equipment_summary()

        if equipment is not None:

            st.download_button(
                "Download Equipment CSV",
                pd.DataFrame(equipment).to_csv(
                    index=False
                ),
                file_name="khwezi_equipment.csv",
                mime="text/csv"
            )

        try:

            module = importlib.import_module(
                "safety_incidents"
            )

            if hasattr(module, "list_incidents"):

                incident_records = (
                    module.list_incidents()
                )

                st.download_button(
                    "Download Incidents CSV",
                    incident_records.to_csv(
                        index=False
                    ),
                    file_name="khwezi_incidents.csv",
                    mime="text/csv"
                )

        except Exception:
            pass

    # =================================================
    # CALL ALL GROUP MEMBERS
    # =================================================

    elif selected in MEMBER_MODULES:

        render_member_page(
            selected,
            role
        )

    else:

        st.warning(
            f"No page configured for: {selected}"
        )

# =====================================================
# APPLICATION STARTUP
# =====================================================

if not st.session_state.get(
    "auth_token",
    False
):

    render_access_gate()

else:

    render_main_interface()
