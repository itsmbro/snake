import json
import streamlit as st

def visualizza_json(user_info):
    st.subheader("Contenuto del JSON")
    st.json(user_info)
