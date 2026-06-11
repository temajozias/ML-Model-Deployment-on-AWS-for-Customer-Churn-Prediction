import os
import psycopg2
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_PORT = os.getenv("DB_PORT", 5432)

CSV_FILE = "../input/Churn_Modelling.csv"
TABLE_NAME = "customer_churn"

def upload_csv_to_rds():
    try:
        # Connect to PostgreSQL RDS
        conn = psycopg2.connect(
            host=DB_HOST,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD,
            port=DB_PORT
        )
        cursor = conn.cursor()
        print("Connected to RDS PostgreSQL")

        # Load CSV using pandas (only to get columns for table creation)
        df = pd.read_csv(CSV_FILE)

        # Create table dynamically (adjust datatypes as needed)
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            id SERIAL PRIMARY KEY,
            {", ".join([f'"{col}" TEXT' for col in df.columns])}
        );
        """
        cursor.execute(create_table_query)
        conn.commit()
        print(f"Table {TABLE_NAME} is ready")

        # --- FAST BULK INSERT USING COPY ---
        with open(CSV_FILE, 'r') as f:
            cols = ', '.join([f'"{col}"' for col in df.columns])
            cursor.copy_expert(f"COPY {TABLE_NAME} ({cols}) FROM STDIN WITH CSV HEADER", f)

        conn.commit()
        print(f"Data from {CSV_FILE} uploaded to {TABLE_NAME} successfully")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            print("Connection closed")

if __name__ == "__main__":
    upload_csv_to_rds()
