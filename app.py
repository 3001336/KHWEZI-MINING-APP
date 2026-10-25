import streamlit as st

# --- MEMBER 1: FRONT-END & UI (UNIQUE STRUCTURAL DESIGN) ---
st.set_page_config(
page_title="Khwezi Mining Portal - UI Shell",
page_icon="⚙️",
layout="wide"
)

# Custom structural styling (Card-based layout)
st.markdown("""
<style>
.card {
padding: 20px;
border-radius: 10px;
background-color: #ffffff;
box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
margin-bottom: 20px;
}
</style>
""", unsafe_allow_html=True)

# Application Banner (Khwezi Mining Statement Context - Page 2)
st.title("Khwezi Mining | Health, Safety & Equipment UI")
st.caption("System Architecture & Front-End Interface Shell (Member 1 Deliverable)")
st.divider()

# --- FUNCTION FOR ACCESS CONTROL (RBAC) ---
def render_access_gate():
st.markdown("### 🔐 Security & Access Control Gateway")
st.write("Authenticate user clearance to unlock designated Khwezi Mining modules.")

# Using text input and selectbox without a 'form' wrapper (Different structure)
operator_id = st.text_input("Enter Staff Identification Number:")
access_level = st.selectbox(
"Select Clearance Group (Table 1):",
["Administrator", "Safety Officer", "Mining Engineer", "Maintenance Engineer", "Manager"]
)

if st.button("Unlock Dashboard Interface"):
# Error Prevention (Section 5)
if len(operator_id.strip()) == 0:
st.warning("Validation Error: Identification field cannot be empty.")
else:
st.session_state['auth_token'] = True
st.session_state['id_tag'] = operator_id
st.session_state['tier'] = access_level
st.rerun()

# --- FUNCTION FOR MAIN DASHBOARD SHELL ---
def render_main_interface():
tag = st.session_state['id_tag']
tier = st.session_state['tier']

# Top bar control panel
top_col1, top_col2 = st.columns([8, 2])
top_col1.success(f"Active Session: **{tag}** | Clearance: **{tier}**")
if top_col2.button("Terminate Session"):
st.session_state['auth_token'] = False
st.rerun()

st.divider()

# Intuitive Navigation Layout using Tabs instead of a Sidebar (Distinct UI Architecture)
st.markdown("#### Operational Workspace Navigation")

# Building tabs dynamically based on Table 1 clearance logic
tab_labels = ["Main KPI Dashboard"]

if tier in ["Administrator", "Safety Officer", "Mining Engineer", "Manager"]:
tab_labels.extend(["Worker Safety Logs", "Incident Reports", "Risk Matrix"])

if tier in ["Administrator", "Mining Engineer", "Maintenance Engineer", "Manager"]:
tab_labels.extend(["Equipment Telemetry", "Maintenance Schedules"])

tab_labels.append("Operational Reports")

if tier == "Administrator":
tab_labels.append("User Control Panel")

# Render tabbed containers
created_tabs = st.tabs(tab_labels)

for i, tab_name in enumerate(tab_labels):
with created_tabs[i]:
if tab_name == "Main KPI Dashboard":
st.subheader("Central Performance Indicators")
m1, m2, m3 = st.columns(3)
m1.metric("System Operational Status", "Online", "Secure")
m2.metric("Data Feed Latency", "12 ms", "Optimal")
m3.metric("Active Safety Compliance", "96.5%", "+1.1%")
st.info("Dashboard shell loaded successfully. Ready for backend telemetry integration.")
else:
st.subheader(f"Module View: {tab_name}")
st.write(f"The structural layout for **{tab_name}** is active under **{tier}** permissions. Backend data hooks pending.")

# --- APP FLOW ROUTING ---
if 'auth_token' not in st.session_state:
st.session_state['auth_token'] = False

if not st.session_state['auth_token']:
render_access_gate()
else:
render_main_interface()