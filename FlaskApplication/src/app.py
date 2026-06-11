import os
from pathlib import Path
#from dotenv import load_dotenv
from flask import Flask, jsonify, request
#load_dotenv(Path(".env"))
import pandas as pd
import os
import json
import psycopg2

#if os.environ.get("ENV", "dev") == "prod":
    #load_dotenv(Path(".env.prod"))
#if os.environ.get("ENV", "dev") == "dev":
    #load_dotenv(Path(".env.dev"))


from logging_module import logger
from predictor import predict

app = Flask(__name__)

def get_connection():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT", 5432)
    )

@app.route("/health-status")
def get_health_status():
    logger.debug("Health check API version 2")
    resp = jsonify({"status": "I am alive, version 2"})
    resp.status_code = 200
    return resp

@app.route("/churn-prediction", methods=['POST'])
def churn_prediction():
    logger.debug("Churn Prediction API Called")

    try:
        # Connect to PostgreSQL RDS
        conn = get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM customer_churn LIMIT 5;"
        cursor.execute(query)
        colnames = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        # Convert to DataFrame
        df = pd.DataFrame(rows, columns=colnames)

        # Drop columns model doesn't use
        drop_cols = ['id', 'RowNumber', 'CustomerId', 'Exited']
        df = df.drop(columns=[col for col in drop_cols if col in df.columns])

        # Convert numeric columns to proper types
        numeric_cols = ['CreditScore', 'Age', 'Tenure', 'Balance', 'NumOfProducts',
                        'HasCrCard', 'IsActiveMember', 'EstimatedSalary']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')

        # Save input JSON
        input_json = json.loads(df.to_json(orient="records"))

        # Call ML prediction (predictor.py unchanged)
        status, result = predict(df)

        if status == 200:
            # Convert only the filtered high-churn DataFrame to JSON
            output_json = json.loads(result.to_json(orient="records"))
            resp = jsonify({
                "input": input_json,
                "output": output_json
            })
        else:
            resp = jsonify({
                "input": input_json,
                "errorDetails": result
            })

        resp.status_code = status
        return resp

    except Exception as e:
        logger.error(f"Error in churn_prediction: {str(e)}")
        resp = jsonify({"errorDetails": str(e)})
        resp.status_code = 500
        return resp

if __name__ == "__main__":
    app.run(debug=True)
