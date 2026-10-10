import os
from datetime import date, datetime

import psycopg
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, ConfigDict


# ============================================================
# ENVIRONMENT
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ENV_FILE = os.path.join(BASE_DIR, ".env")

load_dotenv(ENV_FILE)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title = "MetricMind Backend",
    version = "1.0.0",
)

# ============================================================
# CORS
# ============================================================

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


# ============================================================
# RESPONSE MODELS
# ============================================================

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
    model_config = ConfigDict(str_strip_whitespace=True)
    
    question: str = Field(
        min_length=1,
        max_length=500,
        )


class QuestionResponse(BaseModel):
    id: int
    question: str
    created_at: datetime

class QuestionHistoryResponse(BaseModel):
    total: int
    limit: int
    offset: int
    questions: list[QuestionResponse]

class QuestionAnswerResponse(BaseModel):
    question: str
    answer: str


# ============================================================
# DATABASE CONNECTION
# ============================================================

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


# ============================================================
# ROOT API
# ============================================================

@app.get("/")
def root():
    return {
        "message": "MetricMind backend is running",
        "status": "ok",
    }


# ============================================================
# HEALTH API
# ============================================================

@app.get("/health")
def health():
    return {"status": "healthy"}


# ============================================================
# DATABASE HEALTH API
# ============================================================

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


# ============================================================
# SALES API
# ============================================================

@app.get("/sales", response_model=list[SalesResponse])
def get_sales(
    region: str | None = Query(default=None),
    country: str | None = Query(default=None),
    product_name: str | None = Query(default=None),
    category: str | None = Query(default=None),
    quarter: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=1000),
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


# ============================================================
# SUMMARY API
# ============================================================

@app.get("/summary", response_model=SummaryResponse)
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
            margin_percentage=round(margin_percentage, 2),
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Summary request failed: {exc}",
        )


# ============================================================
# CATEGORY SUMMARY API
# ============================================================

@app.get(
    "/summary/category",
    response_model=list[CategorySummaryResponse],
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

# ============================================================
# QUARTER SUMMARY API
# ============================================================

@app.get("/summary/quarter")
def get_quarter_summary():
    query = """
        SELECT
            quarter,
            COUNT(*) AS total_orders,
            COALESCE(SUM(revenue), 0) AS total_revenue,
            COALESCE(SUM(total_cost), 0) AS total_cost,
            COALESCE(SUM(margin), 0) AS total_margin
        FROM fct_sales
        GROUP BY quarter
        ORDER BY quarter
    """

    try:
        with get_db_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(query)
                rows = cur.fetchall()

        return [
            {
                "quarter": row[0],
                "total_orders": int(row[1]),
                "total_revenue": float(row[2]),
                "total_cost": float(row[3]),
                "total_margin": float(row[4]),
            }
            for row in rows
        ]

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Quarter summary request failed: {exc}",
        )

# ============================================================
# CREATE QUESTION API
# ============================================================

@app.post("/questions", response_model=QuestionResponse)
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
                    RETURNING id, question,created_at
                    """,
                    (question,),
                )

                row = cur.fetchone()
                conn.commit()

        return QuestionResponse(
            id=row[0],
            question=row[1],
            created_at=row[2],
        )

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Question save failed: {exc}",
        )


# ============================================================
# GET SAVED QUESTIONS API
# ============================================================

@app.get("/questions", response_model=QuestionHistoryResponse)
def get_questions(
    search: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
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
                if search:
                    cur.execute(
                        """
                        SELECT
                            id,
                            question,
                            created_at
                        FROM saved_questions
                        WHERE question ILIKE %s
                        ORDER BY created_at DESC, id DESC
                        LIMIT %s OFFSET %s
                        """,
                        (f"%{search}%", limit, offset),
                    )
                else:
                    cur.execute(
                        """
                        SELECT 
                            id,
                            question,
                            created_at
                        FROM saved_questions
                        ORDER BY created_at DESC, id DESC
                        LIMIT %s OFFSET %s
                        """,
                        (limit, offset),
                    )
                rows = cur.fetchall()

                if search:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM saved_questions
                        WHERE question ILIKE %s
                        """,
                        (f"%{search}%",),
                    )
                else:
                    cur.execute(
                        """
                        SELECT COUNT(*)
                        FROM saved_questions
                        """
                    )

                total = cur.fetchone()[0]
                conn.commit()
        

        return QuestionHistoryResponse(
                total=total,
                limit=limit,
                offset=offset,
                questions=[
                    QuestionResponse(
                        id=row[0],
                        question=row[1],
                        created_at=row[2],
                    )
                    for row in rows
                ],
            )
           

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Questions request failed: {exc}",
        )


# ============================================================
# ASK METRICMIND - ANSWER QUESTION API
# ============================================================

def build_question_filters(conn, question_text):
        filter_columns = {
            "region": "region",
            "country": "country",
            "product_name": "product_name",
            "category": "category",
            "quarter": "quarter",
        }

        conditions = []
        params = []

        with conn.cursor() as cur:
            for column, sql_column in filter_columns.items():
                cur.execute(
                    f"SELECT DISTINCT {sql_column} FROM fct_sales WHERE {sql_column} IS NOT NULL"
                )
                values = [row[0] for row in cur.fetchall()]

                matches = [
                    value
                    for value in values
                    if str(value).lower() in question_text
                ]

                if matches:
                    # Use the longest match when values overlap.
                    value = max(matches, key=lambda item: len(str(item)))
                    conditions.append(f"{sql_column} = %s")
                    params.append(value)

        return conditions, params

@app.post(
    "/questions/answer",
    response_model=QuestionAnswerResponse,
)

def answer_question(payload: QuestionCreate):
    question = payload.question.strip()

    if not question:
        raise HTTPException(
            status_code=400,
            detail="Question cannot be empty",
        )

    question_lower = question.lower()
    quarter_match = None

    for quarter_name in ["Q1", "Q2", "Q3", "Q4"]:
        if quarter_name.lower() in question_lower:
            quarter_match = quarter_name
            break

    # --------------------------------------------------------
    # HIGHEST QUARTERLY REVENUE
    # --------------------------------------------------------

    if (
        "quarter" in question_lower
        and "revenue" in question_lower
        and (
            "highest" in question_lower
            or "maximum" in question_lower
            or "most" in question_lower
        )
    ):
        query = """
            SELECT
                quarter,
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM fct_sales
            GROUP BY quarter
            ORDER BY total_revenue DESC
            LIMIT 1
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()

            if not row:
                answer = "No sales data is available to answer this question."
            else:
                quarter = row[0]
                revenue = float(row[1])
                answer = f"{quarter} had the highest revenue with ${revenue:,.2f}."

            return QuestionAnswerResponse(question=question, answer=answer)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # LOWEST QUARTERLY REVENUE
    # --------------------------------------------------------

    if (
        "quarter" in question_lower
        and "revenue" in question_lower
        and (
            "lowest" in question_lower
            or "minimum" in question_lower
            or "least" in question_lower
        )
    ):
        query = """
            SELECT
                quarter,
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM fct_sales
            GROUP BY quarter
            ORDER BY total_revenue ASC
            LIMIT 1
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()

            if not row:
                answer = "No sales data is available to answer this question."
            else:
                quarter = row[0]
                revenue = float(row[1])
                answer = f"{quarter} had the lowest revenue with ${revenue:,.2f}."

            return QuestionAnswerResponse(question=question, answer=answer)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # HIGHEST QUARTERLY MARGIN
    # --------------------------------------------------------

    if (
        "quarter" in question_lower
        and "margin" in question_lower
        and (
            "highest" in question_lower
            or "maximum" in question_lower
            or "most" in question_lower
        )
    ):
        query = """
            SELECT
                quarter,
                COALESCE(SUM(margin), 0) AS total_margin
            FROM fct_sales
            GROUP BY quarter
            ORDER BY total_margin DESC
            LIMIT 1
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()

            if not row:
                answer = "No sales data is available to answer this question."
            else:
                quarter = row[0]
                margin = float(row[1])
                answer = f"{quarter} had the highest margin with ${margin:,.2f}."

            return QuestionAnswerResponse(question=question, answer=answer)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # LOWEST QUARTERLY MARGIN
    # --------------------------------------------------------

    if (
        "quarter" in question_lower
        and "margin" in question_lower
        and (
            "lowest" in question_lower
            or "minimum" in question_lower
            or "least" in question_lower
        )
    ):
        query = """
            SELECT
                quarter,
                COALESCE(SUM(margin), 0) AS total_margin
            FROM fct_sales
            GROUP BY quarter
            ORDER BY total_margin ASC
            LIMIT 1
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()

            if not row:
                answer = "No sales data is available to answer this question."
            else:
                quarter = row[0]
                margin = float(row[1])
                answer = f"{quarter} had the lowest margin with ${margin:,.2f}."

            return QuestionAnswerResponse(question=question, answer=answer)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # HIGHEST CATEGORY REVENUE
    # --------------------------------------------------------

    if (
        "category" in question_lower
        and "revenue" in question_lower
        and (
            "highest" in question_lower
            or "maximum" in question_lower
            or "most" in question_lower
        )
    ):
        query = """
            SELECT
                category,
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM fct_sales
            GROUP BY category
            ORDER BY total_revenue DESC
            LIMIT 1
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()

            if not row:
                answer = "No sales data is available to answer this question."
            else:
                category = row[0]
                revenue = float(row[1])
                answer = f"{category} generated the highest revenue with ${revenue:,.2f}."

            return QuestionAnswerResponse(question=question, answer=answer)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # HIGHEST CATEGORY MARGIN
    # --------------------------------------------------------

    if (
        "category" in question_lower
        and "margin" in question_lower
        and (
            "highest" in question_lower
            or "maximum" in question_lower
            or "most" in question_lower
        )
    ):
        query = """
            SELECT
                category,
                COALESCE(SUM(margin), 0) AS total_margin
            FROM fct_sales
            GROUP BY category
            ORDER BY total_margin DESC
            LIMIT 1
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()

            if not row:
                answer = "No sales data is available to answer this question."
            else:
                category = row[0]
                margin = float(row[1])
                answer = f"{category} generated the highest margin with ${margin:,.2f}."

            return QuestionAnswerResponse(question=question, answer=answer)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # HIGHEST COUNTRY REVENUE
    # --------------------------------------------------------

    if (
        "country" in question_lower
        and "revenue" in question_lower
        and (
            "highest" in question_lower
            or "maximum" in question_lower
            or "most" in question_lower
        )
    ):
        query = """
            SELECT
                country,
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM fct_sales
            GROUP BY country
            ORDER BY total_revenue DESC
            LIMIT 1
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()

            if not row:
                answer = "No sales data is available to answer this question."
            else:
                country = row[0]
                revenue = float(row[1])
                answer = f"{country} generated the highest revenue with ${revenue:,.2f}."

            return QuestionAnswerResponse(question=question, answer=answer)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # HIGHEST REGION REVENUE
    # --------------------------------------------------------

    if (
        "region" in question_lower
        and "revenue" in question_lower
        and (
            "highest" in question_lower
            or "maximum" in question_lower
            or "most" in question_lower
        )
    ):
        query = """
            SELECT
                region,
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM fct_sales
            GROUP BY region
            ORDER BY total_revenue DESC
            LIMIT 1
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()

            if not row:
                answer = "No sales data is available to answer this question."
            else:
                region = row[0]
                revenue = float(row[1])
                answer = f"{region} generated the highest revenue with ${revenue:,.2f}."

            return QuestionAnswerResponse(question=question, answer=answer)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # HIGHEST PRODUCT REVENUE
    # --------------------------------------------------------

    if (
        "product" in question_lower
        and "revenue" in question_lower
        and (
            "highest" in question_lower
            or "maximum" in question_lower
            or "most" in question_lower
        )
    ):
        query = """
            SELECT
                product_name,
                COALESCE(SUM(revenue), 0) AS total_revenue
            FROM fct_sales
            GROUP BY product_name
            ORDER BY total_revenue DESC
            LIMIT 1
        """

        try:
            with get_db_connection() as conn:
                with conn.cursor() as cur:
                    cur.execute(query)
                    row = cur.fetchone()

            if not row:
                answer = "No sales data is available to answer this question."
            else:
                product = row[0]
                revenue = float(row[1])
                answer = f"{product} generated the highest revenue with ${revenue:,.2f}."

            return QuestionAnswerResponse(question=question, answer=answer)

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # TOTAL / FILTERED METRIC HELPERS
    # --------------------------------------------------------

    

    # --------------------------------------------------------
    # FILTERED / TOTAL REVENUE
    # --------------------------------------------------------

    if "revenue" in question_lower and (
        "total" in question_lower
        or " for " in f" {question_lower} "
    ):
        try:
            with get_db_connection() as conn:
                conditions, params = build_question_filters(
                    conn,
                    question_lower,
                )
                if quarter_match and not any(
                    condition.startswith("quarter =")
                    for condition in conditions
                ):
                    conditions.append("quarter = %s")
                    params.append(quarter_match)

                query = """
                    SELECT COALESCE(SUM(revenue), 0)
                    FROM fct_sales
                """

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                with conn.cursor() as cur:
                    cur.execute(query, params)
                    row = cur.fetchone()

            revenue = float(row[0] or 0)

            if conditions:
                answer = f"The total revenue for the requested filters is ${revenue:,.2f}."
            else:
                answer = f"Total revenue is ${revenue:,.2f}."

            return QuestionAnswerResponse(
                question=question,
                answer=answer,
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # FILTERED / TOTAL MARGIN
    # --------------------------------------------------------

    if "margin" in question_lower and (
        "total" in question_lower
        or " for " in f" {question_lower} "
    ):
        try:
            with get_db_connection() as conn:
                conditions, params = build_question_filters(
                    conn,
                    question_lower,
                )

                query = """
                    SELECT COALESCE(SUM(margin), 0)
                    FROM fct_sales
                """

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                with conn.cursor() as cur:
                    cur.execute(query, params)
                    row = cur.fetchone()

            margin = float(row[0] or 0)

            if conditions:
                answer = f"The total margin for the requested filters is ${margin:,.2f}."
            else:
                answer = f"Total margin is ${margin:,.2f}."

            return QuestionAnswerResponse(
                question=question,
                answer=answer,
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # FILTERED / TOTAL ORDERS
    # --------------------------------------------------------

    if "orders" in question_lower and (
        "total" in question_lower
        or "how many" in question_lower
        or "number" in question_lower
        or " for " in f" {question_lower} "
    ):
        try:
            with get_db_connection() as conn:
                conditions, params = build_question_filters(
                    conn,
                    question_lower,
                )

                query = "SELECT COUNT(*) FROM fct_sales"

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)

                with conn.cursor() as cur:
                    cur.execute(query, params)
                    row = cur.fetchone()

            total_orders = int(row[0] or 0)

            if conditions:
                answer = f"The total number of orders for the requested filters is {total_orders}."
            else:
                answer = f"Total number of orders is {total_orders}."

            return QuestionAnswerResponse(
                question=question,
                answer=answer,
            )

        except Exception as exc:
            raise HTTPException(
                status_code=500,
                detail=f"Question analysis failed: {exc}",
            )

    # --------------------------------------------------------
    # FALLBACK
    # --------------------------------------------------------

    return QuestionAnswerResponse(
        question=question,
        answer=(
            "I can currently answer questions about total revenue, "
            "total margin, total orders, highest or lowest quarterly "
            "revenue or margin, highest revenue or margin by category, "
            "country, region, or product, and filtered revenue, margin, "
            "or order questions."
        ),
    )
