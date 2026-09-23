import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import psycopg


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


app = FastAPI()


# Allow the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def get_db_connection():
    try:
        return psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Database connection failed."
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

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Database health check failed."
        )


@app.get("/sales")
def get_sales(
    region: str | None = None,
    country: str | None = None,
    product_name: str | None = None,
    category: str | None = None,
    quarter: str | None = None
):
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:

            query = """
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
            """

            conditions = []
            parameters = []

            if region:
                conditions.append("LOWER(region) = LOWER(%s)")
                parameters.append(region)

            if country:
                conditions.append("LOWER(country) = LOWER(%s)")
                parameters.append(country)

            if product_name:
                conditions.append("LOWER(product_name) = LOWER(%s)")
                parameters.append(product_name)

            if category:
                conditions.append("LOWER(category) = LOWER(%s)")
                parameters.append(category)

            if quarter:
                conditions.append("UPPER(quarter) = UPPER(%s)")
                parameters.append(quarter)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += """
                ORDER BY order_date
                LIMIT 20;
            """

            cursor.execute(query, parameters)

            rows = cursor.fetchall()

            columns = [
                description.name
                for description in cursor.description
            ]

            return [
                dict(zip(columns, row))
                for row in rows
            ]

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch sales data."
        )

    finally:
        conn.close()


@app.get("/summary")
def get_summary(
    region: str | None = None,
    country: str | None = None,
    product_name: str | None = None,
    category: str | None = None,
    quarter: str | None = None
):
    conn = get_db_connection()

    try:
        with conn.cursor() as cursor:

            query = """
                SELECT
                    COUNT(*) AS total_orders,
                    COALESCE(SUM(revenue), 0) AS total_revenue,
                    COALESCE(SUM(total_cost), 0) AS total_cost,
                    COALESCE(SUM(margin), 0) AS total_margin
                FROM fct_sales
            """

            conditions = []
            parameters = []

            if region:
                conditions.append("LOWER(region) = LOWER(%s)")
                parameters.append(region)

            if country:
                conditions.append("LOWER(country) = LOWER(%s)")
                parameters.append(country)

            if product_name:
                conditions.append("LOWER(product_name) = LOWER(%s)")
                parameters.append(product_name)

            if category:
                conditions.append("LOWER(category) = LOWER(%s)")
                parameters.append(category)

            if quarter:
                conditions.append("UPPER(quarter) = UPPER(%s)")
                parameters.append(quarter)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            query += ";"

            cursor.execute(query, parameters)

            row = cursor.fetchone()

            return {
                "total_orders": row[0],
                "total_revenue": float(row[1]),
                "total_cost": float(row[2]),
                "total_margin": float(row[3])
            }

    except HTTPException:
        raise

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to generate sales summary."
        )

    finally:
        conn.close()