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

def test_api_version():
    response = client.get("/openapi.json")

    assert response.status_code == 200
    data = response.json()

    assert data["info"]["title"] == "MetricMind Backend"
    assert data["info"]["version"] == "1.0.0"

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
# DATE FILTER TESTS
# ============================================================

def test_sales_and_summary_start_date_only():
    response = client.get("/sales?start_date=2025-07-01")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    for record in data:
        assert record["order_date"] >= "2025-07-01"

    summary_response = client.get("/summary?start_date=2025-07-01")
    assert summary_response.status_code == 200
    summary_data = summary_response.json()
    assert summary_data["total_orders"] > 0
    assert summary_data["total_revenue"] > 0


def test_sales_and_summary_end_date_only():
    response = client.get("/sales?end_date=2025-06-30")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    for record in data:
        assert record["order_date"] <= "2025-06-30"

    summary_response = client.get("/summary?end_date=2025-06-30")
    assert summary_response.status_code == 200
    summary_data = summary_response.json()
    assert summary_data["total_orders"] > 0
    assert summary_data["total_revenue"] > 0


def test_sales_and_summary_both_dates():
    response = client.get(
        "/sales?start_date=2025-04-01&end_date=2025-06-30"
    )

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    for record in data:
        assert "2025-04-01" <= record["order_date"] <= "2025-06-30"

    summary_response = client.get(
        "/summary?start_date=2025-04-01&end_date=2025-06-30"
    )
    assert summary_response.status_code == 200
    summary_data = summary_response.json()
    assert summary_data["total_orders"] > 0
    assert summary_data["total_revenue"] > 0


def test_invalid_date_range():
    sales_response = client.get(
        "/sales?start_date=2025-12-31&end_date=2025-01-01"
    )

    assert sales_response.status_code == 400
    assert (
        sales_response.json()["detail"]
        == "start_date must be on or before end_date."
    )

    summary_response = client.get(
        "/summary?start_date=2025-12-31&end_date=2025-01-01"
    )

    assert summary_response.status_code == 400
    assert (
        summary_response.json()["detail"]
        == "start_date must be on or before end_date."
    )


def test_date_filter_without_quarter():
    # Verify start_date filters correctly without specifying quarter
    response = client.get("/sales?start_date=2025-10-01")

    assert response.status_code == 200

    data = response.json()

    assert len(data) > 0

    for record in data:
        assert record["order_date"] >= "2025-10-01"
        assert record["quarter"].upper() == "Q4"

    # Verify both dates without quarter parameter
    range_response = client.get(
        "/sales?start_date=2025-01-01&end_date=2025-03-31"
    )

    assert range_response.status_code == 200

    range_data = range_response.json()

    assert len(range_data) > 0

    for record in range_data:
        assert record["order_date"] <= "2025-03-31"
        assert record["quarter"].upper() == "Q1"


# ============================================================
# FILTER OPTIONS API TESTS
# ============================================================

def test_filter_options_structure():
    response = client.get("/filters/options")

    assert response.status_code == 200

    data = response.json()

    assert "regions" in data
    assert "countries" in data
    assert "products" in data
    assert "categories" in data
    assert "quarters" in data
    assert "min_date" in data
    assert "max_date" in data

    assert isinstance(data["regions"], list)
    assert isinstance(data["countries"], list)
    assert isinstance(data["products"], list)
    assert isinstance(data["categories"], list)
    assert isinstance(data["quarters"], list)

    assert len(data["regions"]) > 0
    assert len(data["countries"]) > 0
    assert len(data["products"]) > 0
    assert len(data["categories"]) > 0
    assert len(data["quarters"]) > 0

    # Verify lists are sorted
    assert data["regions"] == sorted(data["regions"])
    assert data["countries"] == sorted(data["countries"])
    assert data["products"] == sorted(data["products"])
    assert data["categories"] == sorted(data["categories"])
    assert data["quarters"] == sorted(data["quarters"])


def test_filter_options_values_and_date_boundaries():
    response = client.get("/filters/options")

    assert response.status_code == 200

    data = response.json()

    # Verify presence of expected core domain entities
    assert "Europe" in data["regions"]
    assert "Germany" in data["countries"]
    assert "Software" in data["categories"]
    assert "Analytics Suite" in data["products"]
    assert set(["Q1", "Q2", "Q3", "Q4"]).issubset(set(data["quarters"]))

    # Verify date boundaries are present and valid
    assert data["min_date"] is not None
    assert data["max_date"] is not None
    assert data["min_date"] <= data["max_date"]


# ============================================================
# QUESTION API TESTS
# ============================================================

def test_create_question():
    response = client.post(
        "/questions",
        json={
            "question": "    "},
    )

    assert response.status_code == 422

def test_create_question_too_long():
    response = client.post(
        "/questions",
        json={"question": "a" * 501},
    )

    assert response.status_code == 422

def test_create_question_success():
    response = client.post(
        "/questions",
        json={
            "question": "Which quarter had the highest revenue?"
        }
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


def test_answer_question_revenue_by_quarter():
    response = client.post(
        "/questions/answer",
        json={
            "question": "What is the total revenue by quarter?"
        },
    )

    assert response.status_code == 200

    answer = response.json()["answer"]

    assert "Q1" in answer
    assert "1,389,392.57" in answer
    assert "Q2" in answer
    assert "1,484,038.25" in answer
    assert "Q3" in answer
    assert "1,464,768.02" in answer
    assert "Q4" in answer
    assert "1,382,331.77" in answer


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
    assert "q2" in data["answer"].lower()
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


def test_answer_question_empty():
    response = client.post(
        "/questions/answer",
        json={"question": "   "},
    )

    assert response.status_code == 422


def test_answer_question_too_long():
    response = client.post(
        "/questions/answer",
        json={"question": "a" * 501},
    )

    assert response.status_code == 422