# AI-Powered Analytics Platform

An end-to-end analytics platform developed using Python, Streamlit, DuckDB, Parquet, SQL, and Google Gemini API to automate data processing, monitor operational KPIs, and provide AI-powered business insights.

## 1. Project Overview

The AI-Powered Analytics Platform provides a centralized interface for operational data analysis and performance monitoring.

It combines automated data processing, analytical querying, interactive dashboards, and an AI assistant to simplify business reporting and decision-making.

## 2. System Architecture

```text
                  DATA SOURCES
                       |
             NB / SB / NMI Datasets
                       |
                       v
              PYTHON DATA LAYER
             Pandas / Data Processing
                       |
                       v
                PARQUET STORAGE
              Incremental Data Files
                       |
                       v
                 DUCKDB ENGINE
              SQL Queries / Data Views
                       |
             +---------+----------+
             |                    |
             v                    v
       ANALYTICS ENGINE       AI ASSISTANT
       KPI Calculations       Google Gemini API
       Date Analysis          Natural Language
       Dashboard Queries      SQL Generation
             |                    |
             +---------+----------+
                       |
                       v
                STREAMLIT APP
                       |
          Interactive Analytics Dashboard
                       |
          KPIs / Trends / Productivity
                       |
                       v
                BUSINESS INSIGHTS
```

## 3. Key Features

### Interactive Analytics Dashboard
- Centralized operational performance monitoring.
- Dynamic KPI cards and business metrics.
- Utility-wise and division-wise analysis.
- Monthly installation trends.
- Field-worker productivity monitoring.
- Interactive filters for data exploration.

### Automated Data Processing
- Python-based data processing workflows.
- Incremental data processing.
- Parquet-based analytical storage.
- Efficient data querying using DuckDB.
- Structured data transformation and preparation.

### AI-Powered Analytics Assistant
- Natural-language interaction with business data.
- Google Gemini API integration.
- Natural-language-to-SQL querying.
- AI-assisted data exploration.
- Automated analytical responses based on available data.

### Operational Performance Monitoring
- Installation progress tracking.
- Division-wise performance analysis.
- Field-worker productivity analysis.
- Date-wise installation monitoring.
- Business KPI reporting.

## 4. Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core programming and ETL |
| Streamlit | Dashboard and web application |
| Pandas | Data processing and transformation |
| DuckDB | Analytical SQL engine |
| Parquet | Efficient columnar data storage |
| SQL | Analytical queries |
| Google Gemini API | AI-powered data interaction |
| GitHub | Version control and source management |

## 5. Project Structure

```text
Analytics-Platform/
│
├── analytics/
│   ├── dashboard_engine.py
│   ├── data_loader.py
│   ├── date_analysis.py
│   ├── kpi_engine.py
│   └── question_engine.py
│
├── config/
│   ├── __init__.py
│   └── settings.py
│
├── app.py
├── ai_assistant.py
├── requirements.txt
├── README.md
└── .gitignore
```

## 6. Installation and Setup

### Step 1: Clone the Repository

```bash
git clone https://github.com/adarshjha8/Analytics-Platform.git
```

### Step 2: Navigate to the Project

```bash
cd Analytics-Platform
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 4: Configure Gemini API

Set your Gemini API key as an environment variable:

```text
GEMINI_API_KEY=your_api_key
```

For Streamlit Cloud, configure the key using the application's Secrets settings.

Never commit API keys or credentials to GitHub.

### Step 5: Configure Data Sources

Configure the NB, SB, and NMI Parquet file paths in:

```text
config/settings.py
```

The datasets are maintained separately from the source-code repository. Use authorized and secure storage for production data.

### Step 6: Run the Application

```bash
streamlit run app.py
```

## 7. Deployment

The application is designed for deployment using Streamlit Community Cloud.

Deployment requirements:
- GitHub repository containing application code.
- Python dependencies defined in `requirements.txt`.
- Secure Gemini API configuration.
- Accessible and authorized Parquet data sources.
- Correct application entry point (`app.py`).

## 8. Security and Data Privacy

- API keys and credentials must be stored securely.
- Confidential datasets must not be committed to public repositories.
- Production data access should follow organizational security policies.
- Use sanitized datasets for demonstrations and portfolio showcases.

## 9. Project Objective

To develop a centralized, scalable analytics solution that combines automated data processing, interactive business intelligence, SQL-based analytics, and AI-assisted querying to improve operational visibility and reporting efficiency.

## 10. Author

**Adarsh Jha**

AI-Powered Analytics Platform

**Core Skills:** Python | SQL | Pandas | DuckDB | Parquet | Streamlit | ETL | Google Gemini API
