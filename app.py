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
st.write("Version 0.3")

mode = st.radio(
    "Modus",
    [
        "Neue Fahrt",
        "Letzten Eintrag bearbeiten"
    ]
)

last_trip = None

if mode == "Letzten Eintrag bearbeiten":
    response = (
        supabase
        .table("trips")
        .select("*")
        .order("id", desc=True)
        .limit(1)
        .execute()
    )

    if len(response.data) == 0:
        st.warning("Es existiert noch keine Fahrt.")
        st.stop()

    last_trip = response.data[0]
if last_trip is None:

    default_journey = 0
    default_date = date.today()
    default_schedule_start = ""
    default_schedule_arrival = ""
    default_start = ""
    default_start_point = ""
    default_destination = ""
    default_transport = TRANSPORTS[0]
    default_line = ""
    default_schedule_min = 0
    default_duration_min = 0
    default_schedule_arrival = ""

else:

    default_journey = last_trip["journey"]
    default_date = datetime.strptime(
        last_trip["date"],
        "%Y-%m-%d"
    ).date()

    default_schedule_start = last_trip["schedule_start"] or ""
    default_schedule_arrival = last_trip["schedule_arrival"] or ""
    default_start = last_trip["start"] or ""
    default_start_point = last_trip["start_point"] or ""
    default_destination = last_trip["destination"] or ""
    default_transport = last_trip["transport"]
    default_line = last_trip["line"] or ""
    default_schedule_min = last_trip["schedule_min"]
    default_duration_min = last_trip["duration_min"]
    default_schedule_arrival = last_trip["schedule_arrival"]



trip_type = st.selectbox(
    "Art der Fahrt",
    [
        "Direktverbindung",
        "Beginn der Fahrt",
        "In der Fahrt",
        "Ende der Fahrt",
    ],
    index=default_journey
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
    value=default_date
)

schedule_start = st.text_input(
    "Geplante Startzeit",
    value=default_schedule_start
)
start = st.text_input(
    "Tatsächliche Startzeit",
    value=default_start
)

# ----------------------------
# Start
# ----------------------------

start_choices = ["Andere..."] + STATIONS

if default_start_point in STATIONS:
    start_index = start_choices.index(default_start_point)
else:
    start_index = 0

start_option = st.selectbox(
    "Start",
    start_choices,
    index=start_index
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

destination_choices = ["Andere..."] + STATIONS

if default_destination_point in STATIONS:
    destination_index = destination_choices.index(default_destination_point)
else:
    destination_index = 0

destination_option = st.selectbox(
    "Ziel",
    destination_choices,
    index=destination_index
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
    index=TRANSPORTS.index(default_transport)
)

# ----------------------------
# Linie
# ----------------------------

line_choices = ["Andere..."] + LINES

if default_line in LINES:
    line_index = line_choices.index(default_line)
else:
    line_index = 0

line_option = st.selectbox(
    "Linie",
    line_choices,
    index=line_index
)

if line_option == "Andere...":
    line = st.text_input(
        "Linienbezeichnung",
        value="" if default_line in LINES else default_line
    )
else:
    line = line_option

# ----------------------------
# Zeiten
# ----------------------------

schedule_min = st.number_input(
    "Fahrplandauer",
    min_value=0,
    value=int(default_schedule_min)
)

duration_min = st.number_input(
    "Tatsächliche Dauer (min)",
    min_value=0,
    value=int(default_duration_min)
)

# ----------------------------
# Geplante Ankunft
# ----------------------------

schedule_arrival = None

if trip_type in ["Direktverbindung", "Ende der Fahrt"]:
    schedule_arrival = st.text_input(
        "Geplante Ankunft (HH:MM)",
        value=default_schedule_arrival
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

        values = {
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

        if mode == "Neue Fahrt":
        
            supabase.table("trips").insert(values).execute()
        
            st.success("Fahrt gespeichert!")

        else:
        
            supabase.table("trips").update(values).eq(
                "id",
                last_trip["id"]
            ).execute()
        
            st.success("Letzte Fahrt aktualisiert!")


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
