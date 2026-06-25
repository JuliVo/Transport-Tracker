import streamlit as st
import pandas as pd

from datetime import date, datetime
from supabase import create_client

# ----------------------------
# Supabase
# ----------------------------

url = st.secrets["SUPABASE_URL"]
key = st.secrets["SUPABASE_KEY"]

supabase = create_client(url, key)

# ----------------------------
# Konfiguration
# ----------------------------
user = st.text_input("Password")

if user != st.secrets["APP_PASSWORD"]:
    st.stop()
    
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
    "Weilheim Marktplatz",
]

LINES = [
    "U12",
    "U13",
    "U7",
    "S1",
    "RE200",
    "RE9",
]

# ----------------------------
# Hilfsfunktionen
# ----------------------------

def valid_time(time_string):
    if time_string == "":
        return False

    try:
        datetime.strptime(time_string, "%H:%M")
        return True
    except ValueError:
        return False


# ----------------------------
# Oberfläche
# ----------------------------

st.title("ÖPNV Tracker")
st.write("Version 0.2")

trip_type = st.selectbox(
    "Art der Fahrt",
    [
        "Direktverbindung",
        "Beginn der Fahrt",
        "In der Fahrt",
        "Ende der Fahrt",
    ],
)

journey_map = {
    "Direktverbindung": 0,
    "Beginn der Fahrt": 1,
    "In der Fahrt": 2,
    "Ende der Fahrt": 3,
}

journey = journey_map[trip_type]

trip_date = st.date_input(
    "Datum",
    value=date.today(),
)

schedule_start = st.text_input(
    "Geplante Startzeit (HH:MM)"
)

start = st.text_input(
    "Tatsächliche Startzeit (HH:MM)"
)

# ----------------------------
# Start
# ----------------------------

start_option = st.selectbox(
    "Start",
    ["Andere..."] + STATIONS,
)

if start_option == "Andere...":
    start_point = st.text_input(
        "Start-Haltestelle"
    )
else:
    start_point = start_option

# ----------------------------
# Ziel
# ----------------------------

destination_option = st.selectbox(
    "Ziel",
    ["Andere..."] + STATIONS,
)

if destination_option == "Andere...":
    destination = st.text_input(
        "Ziel-Haltestelle"
    )
else:
    destination = destination_option

# ----------------------------
# Verkehrsmittel
# ----------------------------

transport = st.selectbox(
    "Verkehrsmittel",
    TRANSPORTS,
)

# ----------------------------
# Linie
# ----------------------------

line_option = st.selectbox(
    "Linie",
    ["Andere..."] + LINES,
)

if line_option == "Andere...":
    line = st.text_input(
        "Linienbezeichnung"
    )
else:
    line = line_option

# ----------------------------
# Zeiten
# ----------------------------

schedule_min = st.number_input(
    "Fahrplandauer (min)",
    min_value=0,
)

duration_min = st.number_input(
    "Tatsächliche Dauer (min)",
    min_value=0,
)

# ----------------------------
# Geplante Ankunft
# ----------------------------

schedule_arrival = None

if trip_type in ["Direktverbindung", "Ende der Fahrt"]:
    schedule_arrival = st.text_input(
        "Geplante Ankunft (HH:MM)"
    )

# ----------------------------
# Speichern
# ----------------------------

if st.button("Speichern"):

    error = False

    if not valid_time(schedule_start):
        st.error("Geplante Startzeit muss im Format HH:MM angegeben werden.")
        error = True

    if not valid_time(start):
        st.error("Tatsächliche Startzeit muss im Format HH:MM angegeben werden.")
        error = True

    if trip_type in ["Direktverbindung", "Ende der Fahrt"]:
        if not valid_time(schedule_arrival):
            st.error("Geplante Ankunft muss im Format HH:MM angegeben werden.")
            error = True

    if not error:

        supabase.table("trips").insert(
            {
                "journey": journey,
                "date": str(trip_date),
                "schedule_start": schedule_start,
                "schedule_arrival": schedule_arrival,
                "start": start,
                "start_point": start_point,
                "destination": destination,
                "transport": transport,
                "line": line,
                "schedule_min": int(schedule_min),
                "duration_min": int(duration_min),
            }
        ).execute()

        st.success("Fahrt gespeichert!")

# ----------------------------
# Letzte Einträge anzeigen
# ----------------------------

st.subheader("Letzte Einträge")

response = (
    supabase
    .table("trips")
    .select("*")
    .order("id", desc=True)
    .limit(10)
    .execute()
)

df = pd.DataFrame(response.data)

if not df.empty:
    st.dataframe(df)
else:
    st.info("Noch keine Fahrten vorhanden.")
