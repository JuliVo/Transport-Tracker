import streamlit as st
import pandas as pd
import sqlite3
from datetime import date
from datetime import datetime
from supabase import create_client

#python -m streamlit run /home/julianv/Schreibtisch/verschiedenes/TransportTracker/app.py
test = 0
if test == 1:
    name = "test.db"
else:
    name = "transport.db"

st.title("ÖPV Tracker")
st.write("Version: 0.2")

TRANSPORTS = [
    "DB Fern",
    "Nahverkehr",
    "S-Bahn",
    "U-Bahn",
    "Bus",
    "Fernbus",
    "SNCF Fern",
    "SNCF Nah",
]

STATIONS = [
    "Riethmüllerhaus",
    "Glockenstraße",
    "Nordbahnhof",
    "Universität",
    "Stuttgart Hbf",
    "Waldau",
    "Kirchheim",
    "Weilheim Kirchheimerstraße/-hegelstraße",
    "Weilheim Marktplatz"
] 
LINES = [
    "U12",
    "U13",
    "U7",
    "S1",
    "RE200",
    "RE9"
]

trip_type = st.selectbox(
    "Art der Fahrt",
    [
        "Direktverbindung",
        "Beginn der Fahrt",
        "In der Fahrt",
        "Ende der Fahrt"
    ]
)

journey_map = {
    "Direktverbindung": 0,
    "Beginn der Fahrt": 1,
    "In der Fahrt": 2,
    "Ende der Fahrt": 3
}

journey = journey_map[trip_type]

trip_date = st.date_input(
    "Datum",
    value=date.today()
)

schedule_start = st.text_input(
    "Geplante Startzeit"
)
try:
    datetime.strptime(schedule_start, "%H:%M")
except ValueError:
    st.error("Bitte Uhrzeit im Format HH:MM eingeben.")

start = st.text_input(
    "Tatsächliche Startzeit"
)
try:
    datetime.strptime(start, "%H:%M")
except ValueError:
    st.error("Bitte Uhrzeit im Format HH:MM eingeben.")

start_option = st.selectbox(
    "Start",
    ["Andere..."] + STATIONS
)

if start_option == "Andere...":
    start_point = st.text_input(
        "Start-Haltestelle"
    )
else:
    start_point = start_option

destination_option = st.selectbox(
    "Ziel",
    ["Andere..."] + STATIONS
)

if destination_option == "Andere...":
    destination = st.text_input(
        "End-Haltestelle"
    )
else:
    destination = destination_option

transport = st.selectbox(
    "Verkehrsmittel",
    TRANSPORTS
)

line_option = st.selectbox(
    "Linie",
    ["Andere..."] + LINES
)
if line_option == "Andere...":
    line = st.text_input(
        "Linienbezeichnung"
    )
else:
    line = line_option

schedule_min = st.number_input(
    "Fahrplandauer",
    min_value=0
)

duration_min = st.number_input(
    "Tatsächliche Dauer",
    min_value=0
)
if trip_type in ["Direktverbindung", "Ende der Fahrt"]:
    schedule_arrival = st.text_input(
    "Geplante Ankunft (HH:MM)",
    )
    try:
        datetime.strptime(schedule_arrival, "%H:%M")
    except ValueError:
        st.error("Bitte Uhrzeit im Format HH:MM eingeben.")
else:
    schedule_arrival = None



if st.button("Speichern"):

    from supabase import create_client

    url = "transport-tracker.streamlit.app"
    key = "1234"

    supabase = create_client(url, key)
    supabase.table("trips").insert({
    "journey": journey,
    "date": str(trip_date),
    "schedule_start": schedule_start,
    "schedule_arrival": schedule_arrival,
    "start": start,
    "start_point": start_point,
    "destination": destination,
    "transport": transport,
    "line": line,
    "schedule_min": schedule_min,
    "duration_min": duration_min
    }).execute()

    st.success("Fahrt gespeichert!")
print (name)
conn = sqlite3.connect(name)

df = response = (
    supabase
    .table("trips")
    .select("*")
    .execute()
)

df = pd.DataFrame(response.data)

st.dataframe(df)

conn.close()
