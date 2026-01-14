import streamlit as st
from datetime import date
from streamlit_calendar import calendar
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOGO_PATH = BASE_DIR / "img" / "logo_koperasi.png"

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.image(str(LOGO_PATH), width=500)

st.caption("")

with st.form("add_project"):
    st.markdown('<div class="form-card">', unsafe_allow_html=True)

    st.subheader("Add Project")
    title = st.text_input("Project Name")
    start = st.date_input("Start Date", date.today())
    end = st.date_input("End Date", date.today())

    submitted = st.form_submit_button("Save Project")

    st.markdown('</div>', unsafe_allow_html=True)
    
if "events" not in st.session_state:
    st.session_state.events = []

if submitted:
    st.session_state.events.append({
        "title": f"{title}",
        "start": start.isoformat(),
        "end": end.isoformat(),
    })

calendar(
    events=st.session_state.events,
    options={
        "initialView": "dayGridMonth",
        "height": 650
    }
)













