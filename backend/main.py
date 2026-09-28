import os
from datetime import date

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel


# =========================================================
# ENVIRONMENT
# =========================================================

load_dotenv(os.path.join(os.path.dirname(__file__), ".env"))


# =========================================================
# FASTAPI APP
# =========================================================

app = FastAPI(title="MetricMind Backend")


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# RESPONSE MODELS
# =========================================================

class SalesResponse(BaseModel):
    order_id: str
    order_date: date
    customer_id: str
    country: str
    region: str
    product_id: str
    product_name: str
    category: str
    quantity: int
    unit_price: float
    revenue: float
    material_cost: float
    shipping_cost: float
    total_cost: float
    margin: float
    quarter: str


class SummaryResponse(BaseModel):
    total_orders: int
    total_revenue: float
    total_cost: float
    total_margin: float
    margin_percentage: float


class CategorySummaryResponse(BaseModel):
    category: str
    total_orders: int
    total_revenue: float
    total_cost: float
    total_margin: float


class QuestionCreate(BaseModel):
    question: str


class QuestionResponse(BaseModel):
    id: int
    question: str


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    try:
        return psycopg.connect(
            host=os.getenv("DB_HOST"),
            port=os.getenv("DB_PORT"),
            dbname=os.getenv("DB_NAME"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
        )
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {exc}",
        )


# =========================================================
# ROOT
# =========================================================

@app.get("/")
def root():
    return {
        "message": "MetricMind backend is running",
        "status": "ok",
    }


# =========================================================
# HEALTH
# =========================================================

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }


# =========================================================
# DATABASE HEALTH
# =========================================================

@app.get("/db-health")
def db_health():
    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()

        return {
            "status": "healthy",
            "database": "connected",
        }

    except Exception as exc:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(exc),
        }


# =========================================================
# SALES API
# =========================================================

@app.get(
    "/sales",
    response_model=list[SalesResponse]
)
def get_sales(
    region: str | None = Query(default=None),
    country: str | None = Query(default=None),
    product_name: str | None = Query(default=None),
    category: str | None = Query(default=None),
    quarter: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):

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
        WHERE 1=1
    """

    params = []

    if region:
        query += " AND region = %s"
        params.append(region)

    if country:
        query += " AND country = %s"
        params.append(country)

    if product_name:
        query += " AND product_name = %s"
        params.append(product_name)

    if category:
        query += " AND category = %s"
        params.append(category)

    if quarter:
        query += " AND quarter = %s"
        params.append(quarter)

    query += """
        ORDER BY order_date, order_id
        LIMIT %s
        OFFSET %s
    """

    params.extend([limit, offset])

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(query, params)

                rows = cur.fetchall()

        return [
            SalesResponse(
                order_id=row[0],
                order_date=row[1],
                customer_id=row[2],
                country=row[3],
                region=row[4],
                product_id=row[5],
                product_name=row[6],
                category=row[7],
                quantity=row[8],
                unit_price=float(row[9]),
                revenue=float(row[10]),
                material_cost=float(row[11]),
                shipping_cost=float(row[12]),
                total_cost=float(row[13]),
                margin=float(row[14]),
                quarter=row[15],
            )
            for row in rows
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Sales request failed: {exc}",
        )


# =========================================================
# SUMMARY API
# =========================================================

@app.get(
    "/summary",
    response_model=SummaryResponse
)
def get_summary(
    region: str | None = Query(default=None),
    country: str | None = Query(default=None),
    product_name: str | None = Query(default=None),
    category: str | None = Query(default=None),
    quarter: str | None = Query(default=None),
):

    query = """
        SELECT
            COUNT(*) AS total_orders,
            COALESCE(SUM(revenue), 0) AS total_revenue,
            COALESCE(SUM(total_cost), 0) AS total_cost,
            COALESCE(SUM(margin), 0) AS total_margin
        FROM fct_sales
        WHERE 1=1
    """

    params = []

    if region:
        query += " AND region = %s"
        params.append(region)

    if country:
        query += " AND country = %s"
        params.append(country)

    if product_name:
        query += " AND product_name = %s"
        params.append(product_name)

    if category:
        query += " AND category = %s"
        params.append(category)

    if quarter:
        query += " AND quarter = %s"
        params.append(quarter)

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(query, params)

                row = cur.fetchone()

        total_orders = int(row[0] or 0)
        total_revenue = float(row[1] or 0)
        total_cost = float(row[2] or 0)
        total_margin = float(row[3] or 0)

        margin_percentage = (
            (total_margin / total_revenue) * 100
            if total_revenue
            else 0
        )

        return SummaryResponse(
            total_orders=total_orders,
            total_revenue=total_revenue,
            total_cost=total_cost,
            total_margin=total_margin,
            margin_percentage=round(
                margin_percentage,
                2
            ),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Summary request failed: {exc}",
        )


# =========================================================
# CATEGORY SUMMARY API
# =========================================================

@app.get(
    "/summary/category",
    response_model=list[CategorySummaryResponse]
)
def get_category_summary(
    region: str | None = Query(default=None),
    country: str | None = Query(default=None),
    quarter: str | None = Query(default=None),
):

    query = """
        SELECT
            category,
            COUNT(*) AS total_orders,
            COALESCE(SUM(revenue), 0) AS total_revenue,
            COALESCE(SUM(total_cost), 0) AS total_cost,
            COALESCE(SUM(margin), 0) AS total_margin
        FROM fct_sales
        WHERE 1=1
    """

    params = []

    if region:
        query += " AND region = %s"
        params.append(region)

    if country:
        query += " AND country = %s"
        params.append(country)

    if quarter:
        query += " AND quarter = %s"
        params.append(quarter)

    query += """
        GROUP BY category
        ORDER BY total_revenue DESC
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(query, params)

                rows = cur.fetchall()

        return [
            CategorySummaryResponse(
                category=row[0],
                total_orders=int(row[1]),
                total_revenue=float(row[2]),
                total_cost=float(row[3]),
                total_margin=float(row[4]),
            )
            for row in rows
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Category summary request failed: {exc}",
        )


# =========================================================
# QUESTIONS API - SAVE QUESTION
# =========================================================

@app.post(
    "/questions",
    response_model=QuestionResponse
)
def create_question(payload: QuestionCreate):

    question = payload.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS saved_questions (
                        id SERIAL PRIMARY KEY,
                        question TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                cur.execute(
                    """
                    INSERT INTO saved_questions (question)
                    VALUES (%s)
                    RETURNING id, question
                    """,
                    (question,),
                )

                row = cur.fetchone()

                conn.commit()

        return QuestionResponse(
            id=row[0],
            question=row[1],
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Question save failed: {exc}",
        )


# =========================================================
# QUESTIONS API - GET SAVED QUESTIONS
# =========================================================

@app.get(
    "/questions",
    response_model=list[QuestionResponse]
)
def get_questions():

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:

                cur.execute(
                    """
                    CREATE TABLE IF NOT EXISTS saved_questions (
                        id SERIAL PRIMARY KEY,
                        question TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                    """
                )

                cur.execute(
                    """
                    SELECT
                        id,
                        question
                    FROM saved_questions
                    ORDER BY created_at DESC, id DESC
                    """
                )

                rows = cur.fetchall()

                conn.commit()

        return [
            QuestionResponse(
                id=row[0],
                question=row[1],
            )
            for row in rows
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Questions request failed: {exc}",
        )