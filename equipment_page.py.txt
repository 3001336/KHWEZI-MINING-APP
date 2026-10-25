"""
equipment_page.py
=================
Streamlit interface for the Equipment + Maintenance part.

HOW THE GROUP INTEGRATES THIS:
    from equipment_page import render_equipment_module
    ...
    if choice == "Equipment & Maintenance":
        render_equipment_module(st.session_state["role"])

`role` must be one of the group's role names:
    Administrator, Safety Officer, Mining Engineer, Maintenance Engineer, Manager
"""

import streamlit as st
import pandas as pd
import plotly.express as px

import equipment_module as em

COLORS = {"NORMAL": "#2E7D32", "WARNING": "#F9A825", "CRITICAL": "#C62828",
          "OK": "#2E7D32", "Due Soon": "#F9A825", "Overdue": "#C62828",
          "Under Maintenance": "#1565C0"}


def _style_state(val):
    """Colour a cell by its state text (colour + text, not colour alone)."""
    c = COLORS.get(val)
    return f"background-color: {c}; color: white; font-weight: 600" if c else ""


def _load():
    """Keep the working table in session_state so edits survive reruns."""
    if "eq_raw" not in st.session_state:
        st.session_state["eq_raw"] = em.load_equipment()
    return st.session_state["eq_raw"]


# ----------------------------------------------------------------------
# TABS
# ----------------------------------------------------------------------
def _tab_overview(data, alerts):
    k = em.equipment_kpis(data, alerts)
    c = st.columns(4)
    c[0].metric("Total equipment", k["total_equipment"])
    c[1].metric("Equipment available", k["equipment_available"])
    c[2].metric("Under maintenance", k["under_maintenance"])
    c[3].metric("Overdue maintenance", k["overdue"])
    c = st.columns(4)
    c[0].metric("Equipment alerts", k["total_alerts"])
    c[1].metric("Critical alerts", k["critical_alerts"])
    c[2].metric("Avg availability", f"{k['avg_availability']} %")
    c[3].metric("Operating normally", f"{k['pct_normal']} %")

    left, right = st.columns(2)
    cond = data["condition"].value_counts().reset_index()
    cond.columns = ["Condition", "Count"]
    fig = px.pie(cond, names="Condition", values="Count", color="Condition",
                 color_discrete_map=COLORS, title="Equipment condition", hole=0.45)
    left.plotly_chart(fig, use_container_width=True)

    avg = data.groupby("equipment_type")["availability"].mean().reset_index()
    fig = px.bar(avg.sort_values("availability"), x="availability", y="equipment_type",
                 orientation="h", title="Average availability by type (%)",
                 labels={"availability": "Availability (%)", "equipment_type": ""})
    fig.add_vline(x=em.LOW_AVAILABILITY, line_dash="dash",
                  annotation_text=f"Minimum {em.LOW_AVAILABILITY}%")
    right.plotly_chart(fig, use_container_width=True)


def _tab_database(role, data):
    st.subheader("Equipment database")
    f = st.columns([2, 1, 1])
    text = f[0].text_input("Search (ID, manufacturer, location)")
    eq_type = f[1].selectbox("Type", ["All"] + em.EQUIPMENT_TYPES)
    state = f[2].selectbox("Maintenance state",
                           ["All", "OK", "Due Soon", "Overdue", "Under Maintenance"])
    view = em.search_equipment(data, text, eq_type, state)
    show = view[["equipment_id", "equipment_type", "manufacturer", "location",
                 "operating_hours", "downtime_hours", "availability",
                 "temperature_c", "vibration_mms", "fuel_lph", "brake_status",
                 "tyre_status", "engine_status", "maint_state", "condition"]]
    st.caption(f"{len(view)} of {len(data)} machines shown")
    st.dataframe(show.style.map(_style_state, subset=["maint_state", "condition"]),
                 use_container_width=True, hide_index=True)

    st.divider()
    st.subheader("Add equipment")
    if not em.can_edit_equipment(role):
        st.info("Your role can view equipment data but cannot add or edit it.")
        return
    with st.form("add_equipment", clear_on_submit=False):
        a, b, c = st.columns(3)
        eid = a.text_input("Equipment ID (e.g. TRK-020)")
        etype = b.selectbox("Equipment type", em.EQUIPMENT_TYPES)
        maker = c.text_input("Manufacturer")
        a, b, c = st.columns(3)
        op = a.number_input("Operating hours", min_value=0.0, value=500.0)
        down = b.number_input("Downtime hours", min_value=0.0, value=40.0)
        loc = c.text_input("Location", value="Pit A")
        a, b, c = st.columns(3)
        temp = a.number_input("Temperature (°C)", value=75.0)
        vib = b.number_input("Vibration (mm/s)", min_value=0.0, value=3.0)
        fuel = c.number_input("Fuel (L/h)", min_value=0.0, value=100.0)
        a, b, c, d = st.columns(4)
        brake = a.selectbox("Brakes", em.COMPONENT_STATUS)
        tyre = b.selectbox("Tyres", em.COMPONENT_STATUS)
        eng = c.selectbox("Engine", em.COMPONENT_STATUS)
        mstat = d.selectbox("Maintenance status", em.MAINT_STATUS_OPTIONS)
        a, b = st.columns(2)
        last = a.date_input("Last maintenance", value=pd.Timestamp.today().date() - pd.Timedelta(days=30))
        nxt = b.date_input("Next maintenance", value=pd.Timestamp.today().date() + pd.Timedelta(days=30))
        submitted = st.form_submit_button("Add equipment")

    if submitted:
        rec = dict(equipment_id=eid, equipment_type=etype, manufacturer=maker,
                   operating_hours=op, downtime_hours=down, temperature_c=temp,
                   vibration_mms=vib, fuel_lph=fuel, brake_status=brake,
                   tyre_status=tyre, engine_status=eng, maintenance_status=mstat,
                   last_maintenance=last, next_maintenance=nxt, alerts_30d=0,
                   location=loc)
        errors = em.validate_equipment_input(rec, set(data["equipment_id"]))
        if errors:
            for e in errors:
                st.error(e)
        else:
            new = em.add_equipment(st.session_state["eq_raw"], rec)
            em.save_equipment(new)
            st.session_state["eq_raw"] = new
            st.success(f"Equipment {rec['equipment_id'].upper()} added and saved.")
            st.rerun()


def _tab_condition(data):
    st.subheader("Temperature and vibration monitoring")
    st.caption("Educational prototype thresholds only. They are not manufacturer "
               "or mine safety limits.")
    t = st.columns(2)
    t[0].markdown(f"**Temperature:** normal < {em.TEMP_LIMITS[0]:.0f} °C, "
                  f"warning {em.TEMP_LIMITS[0]:.0f}–{em.TEMP_LIMITS[1]:.0f} °C, "
                  f"critical > {em.TEMP_LIMITS[1]:.0f} °C")
    t[1].markdown(f"**Vibration:** normal < {em.VIB_LIMITS[0]:.0f} mm/s, "
                  f"warning {em.VIB_LIMITS[0]:.0f}–{em.VIB_LIMITS[1]:.0f} mm/s, "
                  f"critical > {em.VIB_LIMITS[1]:.0f} mm/s")

    fig = px.scatter(data, x="temperature_c", y="vibration_mms", color="condition",
                     color_discrete_map=COLORS, hover_name="equipment_id",
                     symbol="condition", title="Temperature vs vibration",
                     labels={"temperature_c": "Temperature (°C)",
                             "vibration_mms": "Vibration (mm/s)"})
    fig.add_vline(x=em.TEMP_LIMITS[0], line_dash="dot", line_color="#F9A825")
    fig.add_vline(x=em.TEMP_LIMITS[1], line_dash="dash", line_color="#C62828")
    fig.add_hline(y=em.VIB_LIMITS[0], line_dash="dot", line_color="#F9A825")
    fig.add_hline(y=em.VIB_LIMITS[1], line_dash="dash", line_color="#C62828")
    st.plotly_chart(fig, use_container_width=True)

    sel = st.selectbox("Check one machine", data["equipment_id"])
    r = data[data["equipment_id"] == sel].iloc[0]
    msg = r["condition_msg"]
    if r["condition"] == "CRITICAL":
        st.error(msg)
    elif r["condition"] == "WARNING":
        st.warning(msg)
    else:
        st.success(msg)
    c = st.columns(2)
    c[0].metric("Temperature", f"{r['temperature_c']} °C", r["temp_state"], delta_color="off")
    c[1].metric("Vibration", f"{r['vibration_mms']} mm/s", r["vib_state"], delta_color="off")


def _tab_alerts(alerts):
    st.subheader("Equipment alerts")
    if alerts.empty:
        st.success("No active equipment alerts.")
        return
    sev = st.multiselect("Severity", ["CRITICAL", "WARNING"], default=["CRITICAL", "WARNING"])
    shown = alerts[alerts["severity"].isin(sev)]
    st.caption(f"{len(shown)} alert(s) shown")
    st.dataframe(shown.style.map(_style_state, subset=["severity"]),
                 use_container_width=True, hide_index=True)

    if len(shown):
        st.markdown("**Alert preview**")
        idx = st.number_input("Alert number", 1, len(shown), 1)
        st.code(em.format_alert(shown.iloc[idx - 1]), language=None)
        st.download_button("Download alerts (CSV)", shown.to_csv(index=False),
                           "equipment_alerts.csv", "text/csv")


def _tab_maintenance(data):
    st.subheader("Maintenance monitoring")
    c = st.columns(6)
    c[0].metric("Due soon", int(data["flag_due"].sum()))
    c[1].metric("Overdue", int(data["flag_overdue"].sum()))
    c[2].metric("Under maintenance", int(data["flag_under_maint"].sum()))
    c[3].metric("Excess downtime", int(data["flag_excess_downtime"].sum()))
    c[4].metric("Repeated alerts", int(data["flag_repeated_alerts"].sum()))
    c[5].metric("Low availability", int(data["flag_low_availability"].sum()))

    st.markdown("**Maintenance warnings (highest priority first)**")
    flagged = data[data["warnings"] != ""].sort_values("priority_score", ascending=False)
    for _, r in flagged.head(8).iterrows():
        text = f"**{r['equipment_id']}** ({r['equipment_type']}): {r['warnings']}"
        if r["flag_overdue"] or r["condition"] == "CRITICAL":
            st.error(text)
        else:
            st.warning(text)
    if flagged.empty:
        st.success("No maintenance warnings.")

    st.markdown("**Availability and downtime**")
    fig = px.bar(data.sort_values("availability"), x="equipment_id", y="availability",
                 color="availability", color_continuous_scale="RdYlGn",
                 range_color=[60, 100], title="Availability by equipment (%)",
                 labels={"availability": "Availability (%)", "equipment_id": "Equipment"})
    fig.add_hline(y=em.LOW_AVAILABILITY, line_dash="dash",
                  annotation_text=f"Minimum {em.LOW_AVAILABILITY}%")
    st.plotly_chart(fig, use_container_width=True)

    fig = px.bar(data.groupby("equipment_type")["downtime_hours"].sum().reset_index(),
                 x="equipment_type", y="downtime_hours",
                 title="Total downtime by equipment type (hours)",
                 labels={"downtime_hours": "Downtime (h)", "equipment_type": ""})
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("**Maintenance schedule**")
    sched = data[["equipment_id", "equipment_type", "last_maintenance", "next_maintenance",
                  "days_to_maint", "maint_state", "priority_score"]].sort_values("days_to_maint")
    st.dataframe(sched.style.map(_style_state, subset=["maint_state"]),
                 use_container_width=True, hide_index=True)


def _tab_analysis(data, alerts):
    st.subheader("Interactive data analysis")
    q = st.selectbox("Choose a question", em.ANALYSIS_QUESTIONS)
    answer, table = em.answer_question(q, data, alerts)
    st.info(answer)
    if table is not None and len(table):
        st.dataframe(table, use_container_width=True, hide_index=True)
    st.markdown("**Recommendations**")
    for r in em.generate_recommendations(data, alerts):
        st.markdown(f"- {r}")


# ----------------------------------------------------------------------
# PUBLIC ENTRY POINT
# ----------------------------------------------------------------------
def render_equipment_module(role):
    """Draw the whole Equipment & Maintenance section for the given role."""
    if not em.can_access_equipment(role):
        st.error(f"Access denied: the {role} role cannot view equipment and maintenance data.")
        return
    try:
        raw = _load()
        data = em.prepare(raw)
        alerts = em.generate_alerts(data)
    except Exception as exc:                     # error prevention: never crash
        st.error(f"Could not load equipment data: {exc}")
        return

    st.title("Equipment and Maintenance Monitoring")
    tabs = st.tabs(["Overview", "Equipment database", "Condition monitoring",
                    "Alerts", "Maintenance", "Analysis"])
    with tabs[0]:
        _tab_overview(data, alerts)
    with tabs[1]:
        _tab_database(role, data)
    with tabs[2]:
        _tab_condition(data)
    with tabs[3]:
        _tab_alerts(alerts)
    with tabs[4]:
        _tab_maintenance(data)
    with tabs[5]:
        _tab_analysis(data, alerts)
