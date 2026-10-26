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

