import sqlite3
import pandas as pd
import streamlit as st
import plotly.express as px
#python -m streamlit run /home/julianv/Schreibtisch/verschiedenes/TransportTracker/analyse.py
conn = sqlite3.connect("transport.db")
from datetime import date, timedelta

df = pd.read_sql_query(
    "SELECT * FROM trips",
    conn
)

conn.close()
st.title("ÖPV Analyse")
st.write("Version: 0.2")

st.subheader("Zeitraum auswählen")
today = date.today()

start_date = st.date_input("Von",today - timedelta(days=30)
)
end_date = st.date_input("Bis", today)

df["date"] = pd.to_datetime(df["date"])

df_filtered = df[
    (df["date"] >= pd.to_datetime(start_date)) &
    (df["date"] <= pd.to_datetime(end_date))
]

st.metric(
    "Anzahl Fahrten",
    len(df_filtered)
)

st.metric(
    "Gesamtfahrzeit",
    f"{df_filtered['duration_min'].sum()} min"
)

st.metric(
    "Geplante Fahrzeit",
    f"{df_filtered['schedule_min'].sum()} min"
)

df_filtered = df_filtered.copy()

df_filtered["delay"] = (
    df_filtered["duration_min"]
    - df_filtered["schedule_min"]
)
st.metric(
    "Durchschnittliche Zeit pro Fahrt",
    f"{round(df_filtered['duration_min'].sum()/len(df_filtered),1)} min"
)
st.metric(
    "Durchschnittliche Verspätung",
    f"{round(df_filtered["delay"].mean(), 1)} min"
)


st.subheader("Häufigste Startorte")

start_counts = (
    df_filtered["start_point"]
    .value_counts(normalize=True)
    .mul(100)
    .head(10)
    .reset_index()
)

start_counts.columns = [
    "Haltestelle",
    "Anteil"
]

fig = px.bar(
    start_counts,
    x="Anteil",
    y="Haltestelle",
    orientation="h",
    text_auto=".1f"
)

fig.update_layout(
    xaxis_title="Anteil aller Fahrten (%)",
    yaxis_title="",
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(fig, width='stretch')


st.subheader("Häufigste Ziele")

destination_counts = (
    df_filtered["destination"]
    .value_counts(normalize=True)
    .mul(100)
    .head(10)
    .reset_index()
)

destination_counts.columns = [
    "Haltestelle",
    "Anteil"
]

fig = px.bar(
    destination_counts,
    x="Anteil",
    y="Haltestelle",
    orientation="h",
    text_auto=".1f"
)

fig.update_layout(
    xaxis_title="Anteil aller Fahrten (%)",
    yaxis_title="",
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(fig, width='stretch')

st.subheader("Häufigste Verkehrsmittel")

transport_counts = (
    df_filtered["transport"]
    .value_counts(normalize=True)
    .mul(100)
    .head(10)
    .reset_index()
)

transport_counts.columns = [
    "Verkehrsmittel",
    "Anteil"
]

fig = px.bar(
    transport_counts,
    x="Anteil",
    y="Verkehrsmittel",
    orientation="h",
    text_auto=".1f"
)

fig.update_layout(
    xaxis_title="Anteil aller Fahrten (%)",
    yaxis_title="",
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(fig, width='stretch')

st.subheader('Durchschnittliche Fahrtzeit pro Verkehrsmittel')
avg_duration_transport = (
    df_filtered
    .groupby("transport")["duration_min"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

avg_duration_transport.columns = [
    "Verkehrsmittel",
    "Durchschnittliche Fahrtdauer"
]

fig = px.bar(
    avg_duration_transport,
    x="Durchschnittliche Fahrtdauer",
    y="Verkehrsmittel",
    orientation="h",
    text_auto=".1f"
)

fig.update_layout(
    xaxis_title="Minuten",
    yaxis_title="",
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(fig,width='stretch')

st.subheader('Durchschnittliche Verspätung während Fahrt pro Verkehrsmittel')
df_filtered["delay"] = (
    df_filtered["duration_min"]
    - df_filtered["schedule_min"]
)
avg_delay_transport = (
    df_filtered
    .groupby("transport")["delay"]
    .mean()
    .sort_values(ascending=False)
    .reset_index()
)

avg_delay_transport.columns = [
    "Verkehrsmittel",
    "Durchschnittliche Verspätung"
]

fig = px.bar(
    avg_delay_transport,
    x="Durchschnittliche Verspätung",
    y="Verkehrsmittel",
    orientation="h",
    text_auto=".1f"
)

fig.update_layout(
    xaxis_title="Minuten",
    yaxis_title="",
    yaxis={"categoryorder": "total ascending"}
)

st.plotly_chart(fig,width='stretch')