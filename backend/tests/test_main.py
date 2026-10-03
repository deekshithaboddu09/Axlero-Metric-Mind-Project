from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


# ============================================================
# EXISTING BACKEND TESTS
# ============================================================

def test_health():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_sales():
    response = client.get("/sales")

    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_summary():
    response = client.get("/summary")

    assert response.status_code == 200

    data = response.json()

    assert "total_orders" in data
    assert "total_revenue" in data
    assert "total_cost" in data
    assert "total_margin" in data


def test_sales_region_filter():
    response = client.get("/sales?region=Europe")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    for record in data:
        assert record["region"].lower() == "europe"


def test_sales_country_filter():
    response = client.get("/sales?country=Germany")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    for record in data:
        assert record["country"].lower() == "germany"


def test_sales_product_filter():
    response = client.get(
        "/sales?product_name=Analytics%20Suite"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    for record in data:
        assert record["product_name"].lower() == "analytics suite"


def test_sales_category_filter():
    response = client.get("/sales?category=Software")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    for record in data:
        assert record["category"].lower() == "software"


def test_sales_quarter_filter():
    response = client.get("/sales?quarter=Q2")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    for record in data:
        assert record["quarter"].upper() == "Q2"


def test_summary_region_filter():
    response = client.get("/summary?region=Europe")

    assert response.status_code == 200

    data = response.json()

    assert "total_orders" in data
    assert "total_revenue" in data
    assert "total_cost" in data
    assert "total_margin" in data


def test_summary_country_filter():
    response = client.get("/summary?country=Germany")

    assert response.status_code == 200

    data = response.json()

    assert "total_orders" in data
    assert "total_revenue" in data
    assert "total_cost" in data
    assert "total_margin" in data


def test_summary_product_filter():
    response = client.get(
        "/summary?product_name=Analytics%20Suite"
    )

    assert response.status_code == 200

    data = response.json()

    assert "total_orders" in data
    assert "total_revenue" in data
    assert "total_cost" in data
    assert "total_margin" in data


def test_summary_category_filter():
    response = client.get("/summary?category=Software")

    assert response.status_code == 200

    data = response.json()

    assert "total_orders" in data
    assert "total_revenue" in data
    assert "total_cost" in data
    assert "total_margin" in data


def test_summary_quarter_filter():
    response = client.get("/summary?quarter=Q2")

    assert response.status_code == 200

    data = response.json()

    assert "total_orders" in data
    assert "total_revenue" in data
    assert "total_cost" in data
    assert "total_margin" in data


def test_combined_filters():
    response = client.get(
        "/sales?region=Europe&country=Germany&quarter=Q2"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    for record in data:
        assert record["region"].lower() == "europe"
        assert record["country"].lower() == "germany"
        assert record["quarter"].upper() == "Q2"


def test_sales_pagination():
    response = client.get("/sales?limit=5&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 5


def test_sales_pagination_offset():
    response = client.get("/sales?limit=5&offset=5")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 5


# ============================================================
# QUESTION API TESTS
# ============================================================

def test_create_question():
    response = client.post(
        "/questions",
        json={
            "question": "Which quarter had the highest revenue?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "id" in data
    assert data["question"] == (
        "Which quarter had the highest revenue?"
    )


def test_get_questions():
    response = client.get("/questions")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert "total" in data
    assert "limit" in data
    assert "offset" in data
    assert "questions" in data

    assert isinstance(data["total"], int)
    assert isinstance(data["limit"], int)
    assert isinstance(data["offset"], int)
    assert isinstance(data["questions"], list)

    if len(data["questions"]) > 0:
        assert "id" in data["questions"][0]
        assert "question" in data["questions"][0]
        assert "created_at" in data["questions"][0]


def test_get_questions_pagination():
    response = client.get("/questions?limit=10&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert isinstance(data["total"], int)
    assert isinstance(data["questions"], list)
    assert len(data["questions"]) <= 10

    for question in data["questions"]:
        assert "id" in question
        assert "question" in question
        assert "created_at" in question


def test_get_questions_invalid_limit():
    response = client.get("/questions?limit=0&offset=0")

    assert response.status_code == 422


def test_get_questions_invalid_offset():
    response = client.get("/questions?limit=10&offset=-1")

    assert response.status_code == 422


def test_get_questions_search():
    response = client.get("/questions?search=revenue&limit=10&offset=0")

    assert response.status_code == 200

    data = response.json()

    assert isinstance(data, dict)
    assert data["limit"] == 10
    assert data["offset"] == 0
    assert isinstance(data["total"], int)
    assert isinstance(data["questions"], list)
    assert data["total"] >= len(data["questions"])

    for question in data["questions"]:
        assert "revenue" in question["question"].lower()


def test_get_questions_search_no_match():
    response = client.get(
        "/questions?search=xyz_nonexistent_question_12345&limit=10&offset=0"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["total"] == 0
    assert data["questions"] == []


def test_answer_question_highest_revenue():
    response = client.post(
        "/questions/answer",
        json={
            "question": "Which quarter had the highest revenue?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "Which quarter had the highest revenue?"
    )
    assert "highest revenue" in data["answer"].lower()
    assert "Q" in data["answer"]


def test_answer_question_total_revenue():
    response = client.post(
        "/questions/answer",
        json={
            "question": "What is the total revenue?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == "What is the total revenue?"
    assert "total revenue" in data["answer"].lower()
    assert "$" in data["answer"]


# ============================================================
# ASK METRICMIND - EXISTING TESTS
# ============================================================

def test_answer_question_highest_category_revenue():
    response = client.post(
        "/questions/answer",
        json={
            "question": "Which category generated the highest revenue?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "Which category generated the highest revenue?"
    )
    assert "highest revenue" in data["answer"].lower()
    assert "$" in data["answer"]


def test_answer_question_highest_category_margin():
    response = client.post(
        "/questions/answer",
        json={
            "question": "Which category generated the highest margin?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "Which category generated the highest margin?"
    )
    assert "highest margin" in data["answer"].lower()
    assert "$" in data["answer"]


def test_answer_question_highest_country_revenue():
    response = client.post(
        "/questions/answer",
        json={
            "question": "Which country generated the highest revenue?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "Which country generated the highest revenue?"
    )
    assert "highest revenue" in data["answer"].lower()
    assert "$" in data["answer"]


def test_answer_question_highest_region_revenue():
    response = client.post(
        "/questions/answer",
        json={
            "question": "Which region generated the highest revenue?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "Which region generated the highest revenue?"
    )
    assert "highest revenue" in data["answer"].lower()
    assert "$" in data["answer"]


def test_answer_question_highest_product_revenue():
    response = client.post(
        "/questions/answer",
        json={
            "question": "Which product generated the highest revenue?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "Which product generated the highest revenue?"
    )
    assert "highest revenue" in data["answer"].lower()
    assert "$" in data["answer"]


# ============================================================
# ASK METRICMIND - FILTER-AWARE TESTS
# ============================================================

def test_answer_question_total_revenue_region():
    response = client.post(
        "/questions/answer",
        json={
            "question": "What is the total revenue for Europe?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What is the total revenue for Europe?"
    )
    assert "total revenue" in data["answer"].lower()
    assert "3,219,668.93" in data["answer"]


def test_answer_question_total_revenue_country():
    response = client.post(
        "/questions/answer",
        json={
            "question": "What is the total revenue for Germany?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What is the total revenue for Germany?"
    )
    assert "total revenue" in data["answer"].lower()
    assert "521,583.10" in data["answer"]


def test_answer_question_total_margin_category():
    response = client.post(
        "/questions/answer",
        json={
            "question": "What is the total margin for Software?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What is the total margin for Software?"
    )
    assert "total margin" in data["answer"].lower()
    assert "1,991,304.02" in data["answer"]


def test_answer_question_total_revenue_quarter():
    response = client.post(
        "/questions/answer",
        json={
            "question": "What is the total revenue for Q2?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What is the total revenue for Q2?"
    )
    assert "total revenue" in data["answer"].lower()
    assert "1,484,038.25" in data["answer"]


def test_answer_question_total_revenue_product():
    response = client.post(
        "/questions/answer",
        json={
            "question": "What is the total revenue for Analytics Suite?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What is the total revenue for Analytics Suite?"
    )
    assert "total revenue" in data["answer"].lower()
    assert "2,399,815.71" in data["answer"]


def test_answer_question_total_orders_region():
    response = client.post(
        "/questions/answer",
        json={
            "question": "What is the total number of orders for Europe?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What is the total number of orders for Europe?"
    )
    assert "total number of orders" in data["answer"].lower()
    assert "576" in data["answer"]


def test_answer_question_total_revenue_combined_filters():
    response = client.post(
        "/questions/answer",
        json={
            "question": "What is the total revenue for Germany in Q2?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What is the total revenue for Germany in Q2?"
    )
    assert "total revenue" in data["answer"].lower()
    assert "132,141.48" in data["answer"]


# ============================================================
# ASK METRICMIND - FALLBACK TEST
# ============================================================

def test_answer_question_unsupported():
    response = client.post(
        "/questions/answer",
        json={
            "question": "What is the average revenue by customer?"
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert data["question"] == (
        "What is the average revenue by customer?"
    )
    assert "currently answer questions" in data["answer"].lower()
    assert "total revenue" in data["answer"].lower()
    assert "filtered revenue" in data["answer"].lower()