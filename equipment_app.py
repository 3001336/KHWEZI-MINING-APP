"""
equipment_app.py - STANDALONE test app for the Equipment + Maintenance part.
Run with:  streamlit run equipment_app.py
(The group's real app will use the login portal instead of the role selector.)
"""
import streamlit as st
from equipment_page import render_equipment_module

st.set_page_config(page_title="Equipment & Maintenance", layout="wide")
role = st.sidebar.selectbox("Test as role (demo only)",
    ["Administrator", "Safety Officer", "Mining Engineer", "Maintenance Engineer", "Manager"],
    index=3)
render_equipment_module(role)
