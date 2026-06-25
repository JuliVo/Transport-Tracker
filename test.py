import sqlite3
import pandas as pd

conn = sqlite3.connect("transport.db")

df = pd.read_sql_query("SELECT * FROM trips", conn)

conn.close()

# ID entfernen
df = df.drop(columns=["id"])

df.to_csv("trips.csv", index=False)