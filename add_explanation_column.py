import sqlite3

conn = sqlite3.connect("analysis.sqlite3")
c = conn.cursor()
try:
    c.execute("ALTER TABLE analysis ADD COLUMN explanation TEXT;")
    print("Column 'explanation' added.")
except Exception as e:
    print("Error:", e)
conn.commit()
conn.close()