import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv("DB_HOST"),
    database=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    port=os.getenv("DB_PORT", 5432)
)

cur = conn.cursor()
cur.execute("SELECT COUNT(*) FROM customer_churn;")
print("Total rows:", cur.fetchone()[0])

cur.execute("SELECT * FROM customer_churn LIMIT 5;")
rows = cur.fetchall()
for row in rows:
    print(row)

cur.close()
conn.close()
