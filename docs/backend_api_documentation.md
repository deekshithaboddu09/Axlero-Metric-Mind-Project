# MetricMind Backend API Documentation

## 1. Overview

MetricMind backend is developed using FastAPI and connects to a PostgreSQL database. It provides APIs for application health checks, sales data, business summaries, and Ask MetricMind question answering.

**Base URL:** `http://127.0.0.1:8000`

**API testing:** `http://127.0.0.1:8000/docs`

## 2. API Endpoints

| Method | Endpoint            | Purpose                                                      |
| ------ | ------------------- | ------------------------------------------------------------ |
| GET    | `/`                 | Check whether the backend is running                         |
| GET    | `/health`           | Check backend health                                         |
| GET    | `/db-health`        | Check database connectivity                                  |
| GET    | `/sales`            | Retrieve sales records with optional filters and pagination  |
| GET    | `/summary`          | Retrieve overall sales summary                               |
| GET    | `/summary/category` | Retrieve sales summaries grouped by category                 |
| GET    | `/summary/quarter`  | Retrieve sales summaries grouped by quarter                  |
| POST   | `/questions`        | Save a question                                              |
| GET    | `/questions`        | Retrieve saved questions with optional search and pagination |
| POST   | `/questions/answer` | Answer supported business questions                          |

## 3. Health APIs

### GET `/`

Checks whether the backend application is running.

### GET `/health`

Returns the backend health status.

### GET `/db-health`

Checks whether the backend can connect to the PostgreSQL database.

## 4. Sales API

### GET `/sales`

Retrieves sales records.

**Optional query parameters:**

* `region`
* `country`
* `product_name`
* `category`
* `quarter`
* `limit`
* `offset`

Example:

`GET /sales?quarter=Q2&limit=20&offset=0`

## 5. Summary APIs

### GET `/summary`

Returns overall sales metrics, including order count, revenue, cost, margin, and margin percentage.

Optional filters: `region`, `country`, `product_name`, `category`, `quarter`.

### GET `/summary/category`

Returns sales metrics grouped by category.

Optional filters: `region`, `country`, `quarter`.

### GET `/summary/quarter`

Returns sales metrics grouped by quarter.

## 6. Ask MetricMind APIs

### POST `/questions`

Saves a question in the database.

Example request:

```
{
  "question": "What is the total revenue?"
}
```

### GET `/questions`

Retrieves saved questions.

Optional parameters: `search`, `limit`, `offset`.

### POST `/questions/answer`

Answers supported business questions about revenue, margin, order counts, quarterly performance, and available filters.

Example request:

```
{
  "question": "What is the total revenue in Q2?"
}
```

The response contains the submitted question and the generated answer.

## 7. Testing

Use the interactive Swagger UI at `http://127.0.0.1:8000/docs` to explore endpoints, enter parameters, submit requests, and inspect responses.

## 8. Technology Stack

* Python
* FastAPI
* PostgreSQL
* Psycopg
* Pydantic
* Uvicorn
* Pytest (for backend tests)
