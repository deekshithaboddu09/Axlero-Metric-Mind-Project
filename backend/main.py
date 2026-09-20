import os

from dotenv import load_dotenv
from fastapi import FastAPI
import psycopg


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


app = FastAPI()


def get_db_connection():
    return psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
    )


@app.get("/")
def home():
    return {"message": "MetricMind Backend is running!"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.get("/db-health")
def db_health_check():
    try:
        conn = get_db_connection()
        conn.close()

        return {"database": "connected"}

    except Exception as e:
        return {
            "database": "connection failed",
            "error": str(e)
        }


@app.get("/sales")
def get_sales():
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    order_id,
                    order_date,
                    customer_id,
                    country,
                    region,
                    product_id,
                    product_name,
                    category,
                    quantity,
                    unit_price,
                    revenue,
                    material_cost,
                    shipping_cost,
                    total_cost,
                    margin,
                    quarter
                FROM fct_sales
                ORDER BY order_date
                LIMIT 20;
            """)

            rows = cursor.fetchall()

            columns = [description.name for description in cursor.description]

            return [dict(zip(columns, row)) for row in rows]

    finally:
        conn.close()


@app.get("/summary")
def get_summary():
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT
                    COUNT(*) AS total_orders,
                    COALESCE(SUM(revenue), 0) AS total_revenue,
                    COALESCE(SUM(total_cost), 0) AS total_cost,
                    COALESCE(SUM(margin), 0) AS total_margin
                FROM fct_sales;
            """)

            row = cursor.fetchone()

            return {
                "total_orders": row[0],
                "total_revenue": float(row[1]),
                "total_cost": float(row[2]),
                "total_margin": float(row[3])
            }

    finally:
        conn.close()