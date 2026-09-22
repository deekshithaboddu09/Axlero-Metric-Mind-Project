from fastapi.testclient import TestClient

from backend.main import app


client = TestClient(app)


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
    response = client.get("/sales?product_name=Analytics%20Suite")

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