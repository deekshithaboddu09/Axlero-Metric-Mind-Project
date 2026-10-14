# MetricMind — Agentic Semantic BI Engine

An AI-powered Business Intelligence platform that helps users explore sales data, understand business performance, and get answers to business questions through a conversational dashboard. Built as part of the Axlero internship project.

## 1. The Problem

Businesses collect large amounts of sales data, but understanding that data often requires SQL knowledge, manual analysis, and multiple dashboard filters.

Users may want to ask simple questions like:
- What is our total revenue?
- Which country has the highest sales?
- Which quarter generated the most revenue?
- What are our total costs and profit margins?

MetricMind aims to make this information easier to access through a dashboard and natural-language questions.

## 2. Our Solution — How It Works

1. Sales data is stored in a PostgreSQL database.
2. Data transformation models organize the data for analysis using dbt.
3. Cube provides a semantic layer with approved business metrics and dimensions.
4. The FastAPI backend processes dashboard requests and questions.
5. The AI agent helps interpret supported business questions and creates validated queries.
6. The Next.js dashboard displays KPIs, charts, filtered sales data, and answers.

The goal is to connect users to trusted business metrics without requiring them to write SQL manually.

## 3. Key Features

| Feature | Description |
|---|---|
| Business Dashboard | View important sales performance information |
| KPI Cards | Display total orders, revenue, cost, and margin |
| Interactive Filters | Filter data by region, country, product, category, and quarter |
| Date Filters | Select a start date and end date |
| Ask MetricMind | Ask business questions in natural language |
| Semantic Layer | Use approved business metrics through Cube |
| Sales Table | Explore filtered sales records |
| Quarterly Analysis | Compare revenue across quarters |
| Pagination | Browse sales records in manageable pages |
| CSV Export | Export the filtered sales data |
| Backend APIs | Provide data and answers to the frontend |
| Automated Tests | Verify backend functionality and query validation |

## 4. Architecture

```text
             User
              |
              v
      Next.js Dashboard
              |
              v
        FastAPI Backend
              |
              v
         AI Agent
              |
              v
       Query Validation
              |
              v
       Cube Semantic Layer
              |
              v
       PostgreSQL Database

       dbt Data Models
       organize and
       transform data
```

The AI query flow validates supported metrics and dimensions before sending queries to Cube. A deterministic fallback is available when the AI service is unavailable or not configured.

## 5. Technology Stack

| Layer | Technology |
|---|---|
| Frontend | Next.js, React, TypeScript |
| Backend | Python, FastAPI |
| Database | PostgreSQL |
| Semantic Layer | Cube |
| Data Transformation | dbt |
| AI Integration | Gemini API |
| Testing | Pytest |
| Version Control | Git and GitHub |

## 6. Project Structure

```text
Axlero-Metric-Mind-Project/
├── backend/
│   ├── ai_agent/
│   ├── tests/
│   ├── main.py
│   └── cube_client.py
├── cube/
│   ├── model/
│   │   └── cubes/
│   │       └── Sales.js
│   └── docker-compose.yml
├── data/
│   └── raw/
├── dbt/
│   └── metricmind_dbt/
├── docs/
└── frontend/
    └── src/
        └── app/
```

## 7. Running the Project

### Prerequisites

- Python 3.13
- Node.js and npm
- PostgreSQL
- Docker Desktop
- Git

### Step 1 — Start the Backend

Open a terminal at the project root:

```powershell
.\backend\venv\Scripts\activate
py -m uvicorn backend.main:app --reload
```

Backend API documentation:

http://127.0.0.1:8000/docs

### Step 2 — Start Cube

Configure the required database environment variables and start the Cube service using the project's Docker Compose configuration.

From the project root:

```powershell
cd cube
docker compose up -d
```

Cube API:

http://localhost:4000

### Step 3 — Start the Frontend

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Open the local URL shown in the terminal, usually:

http://localhost:3000

Make sure PostgreSQL, Cube, and the backend are running before testing the complete application.

## 8. Backend API Overview

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Check the root endpoint |
| GET | `/health` | Check backend health |
| GET | `/db-health` | Check database connectivity |
| GET | `/sales` | Retrieve sales records with supported filters and pagination |
| GET | `/summary` | Retrieve sales summary information |
| GET | `/summary/quarter` | Retrieve quarterly revenue information |
| GET | `/filters/options` | Retrieve available filter options |
| POST | `/questions/answer` | Answer a supported business question |
| POST | `/questions` | Save a question |

Open `/docs` on the running backend for the current API schemas and parameters.

## 9. Testing

The project includes automated backend tests for APIs, filters, pagination, AI query validation, and Cube integration.

Run the backend tests from the project root:

```powershell
$env:PYTHONPATH="."
.\backend\venv\Scripts\pytest backend\tests -v
```

Build the frontend:

```powershell
cd frontend
npm run build
```

## 10. Team

| Team Member | Responsibility |
|---|---|
| Boddu Deekshitha | Backend development and integration |
| Sikili Avinash | Data preparation and data engineering |
| Atul Bhosale | Semantic layer and AI-related work |
| Pranjal Patil | Frontend development |

## 11. Future Improvements

- Improve AI response reliability and handling of unavailable AI services.
- Expand business question coverage.
- Improve dashboard visualizations and analytics.
- Add more data quality checks.
- Strengthen deployment and production configuration.
- Improve end-to-end testing.

## 12. Project Goal

MetricMind aims to make business intelligence easier to use by connecting a conversational interface with validated business metrics, a semantic layer, and a structured sales database.
