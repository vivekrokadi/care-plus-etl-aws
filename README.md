<div align="center">

# CarePlus — Serverless AWS ETL Pipeline

**An event-driven, incremental Data Engineering pipeline built on AWS that extracts operational support data, transforms it into Apache Parquet using serverless AWS Lambda functions, loads it into Amazon Redshift Serverless, and powers interactive Power BI dashboards.**

<p align="center">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://custom-icon-badges.demolab.com/badge/AWS-232F3E?style=for-the-badge&logo=aws&logoColor=FF9900" alt="AWS" />
  <img src="https://img.shields.io/badge/Amazon_S3-569A31?style=for-the-badge&logo=amazons3&logoColor=white" alt="Amazon S3" />
  <img src="https://img.shields.io/badge/AWS_Lambda-FF9900?style=for-the-badge&logo=awslambda&logoColor=white" alt="AWS Lambda" />
  <img src="https://img.shields.io/badge/Amazon_Redshift-8C4FFF?style=for-the-badge&logo=amazonredshift&logoColor=white" alt="Amazon Redshift" />
  <img src="https://img.shields.io/badge/MySQL-4479A1?style=for-the-badge&logo=mysql&logoColor=white" alt="MySQL" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/PyArrow_&_Parquet-000000?style=for-the-badge&logo=apache&logoColor=white" alt="PyArrow" />
  <img src="https://img.shields.io/badge/Power_BI-F2C811?style=for-the-badge&logo=powerbi&logoColor=black" alt="Power BI" />
  <img src="https://img.shields.io/badge/Git-F05032?style=for-the-badge&logo=git&logoColor=white" alt="Git" />
</p>

</div>

---

## Architecture

```text
  MySQL (support_tickets)          Application Server Logs (*.log)
            │                                    │
            │  Incremental Daily Ingestion       │
            │  (date trackers + StringIO)        │
            ▼                                    ▼
┌────────────────────────────────────────────────────────────────┐
│                Amazon S3 — Raw Layer (Bronze)                  │
│      raw/tickets/*.csv              support-logs/raw/*.log     │
└──────────────┬──────────────────────────────────┬──────────────┘
               │ S3 ObjectCreated Trigger         │ S3 ObjectCreated Trigger
               ▼                                  ▼
┌─────────────────────────────┐    ┌─────────────────────────────┐
│ AWS Lambda (Tickets ETL)    │    │ AWS Lambda (Logs ETL)       │
│ lambda_process_tickets.py   │    │ lambda_process_logs.py      │
│ • Clean typos & nulls       │    │ • Multi-line Regex parsing  │
│ • Filter negative outliers  │    │ • Standardize log levels    │
│ • Convert to Parquet        │    │ • Convert to Parquet        │
└──────────────┬──────────────┘    └──────────────┬──────────────┘
               │                                  │
               ▼                                  ▼
┌────────────────────────────────────────────────────────────────┐
│             Amazon S3 — Processed Layer (Silver)               │
│  processed/tickets/*.parquet   support-logs/processed/*.parquet│
└──────────────────────────────┬─────────────────────────────────┘
                               │ S3 Event Trigger (lambda_load_redshift.py)
                               │ Bulk Load via Redshift COPY (psycopg2)
                               ▼
┌────────────────────────────────────────────────────────────────┐
│          Amazon Redshift Serverless — Analytics (Gold)         │
│         public.support_tickets   |   public.support_logs       │
└──────────────────────────────┬─────────────────────────────────┘
                               │
                               ▼
                    Power BI Dashboards
```

---

## Tech Stack

| Layer | Technologies |
| :--- | :--- |
| **Source & Ingestion** | ![Python](https://img.shields.io/badge/Python_3.14-3776AB?style=flat-square&logo=python&logoColor=white) ![MySQL](https://img.shields.io/badge/MySQL-4479A1?style=flat-square&logo=mysql&logoColor=white) ![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=flat-square&logo=sqlalchemy&logoColor=white) ![Boto3](https://img.shields.io/badge/Boto3-232F3E?style=flat-square&logo=python&logoColor=FF9900) |
| **Storage (Data Lake)** | ![Amazon S3](https://img.shields.io/badge/Amazon_S3-569A31?style=flat-square&logo=amazons3&logoColor=white) ![Parquet](https://img.shields.io/badge/Apache_Parquet-000000?style=flat-square&logo=apache&logoColor=white) |
| **Serverless Transformation** | ![AWS Lambda](https://img.shields.io/badge/AWS_Lambda-FF9900?style=flat-square&logo=awslambda&logoColor=white) ![Pandas](https://img.shields.io/badge/Pandas-150458?style=flat-square&logo=pandas&logoColor=white) ![PyArrow](https://img.shields.io/badge/PyArrow-000000?style=flat-square&logo=apache&logoColor=white) |
| **Data Warehouse & BI** | ![Amazon Redshift](https://img.shields.io/badge/Amazon_Redshift_Serverless-8C4FFF?style=flat-square&logo=amazonredshift&logoColor=white) ![Power BI](https://img.shields.io/badge/Power_BI-F2C811?style=flat-square&logo=powerbi&logoColor=black) |

---

## Key Features & Transformations

* **Incremental Daily Ingestion:** Stateful Python scripts track high-water marks (`date_tracker.txt`, `log_date_tracker.txt`) and stream daily deltas from MySQL and local server logs straight to S3 in memory (`StringIO`).
* **Serverless Log Transformation (`lambda_process_logs.py`):** Automatically triggered by S3 uploads to parse multi-line `.log` files with Regex, normalize malformed log levels (`INF0` → `INFO`, `DEBG` → `DEBUG`, `warnING` → `WARNING`, `EROR` → `ERROR`), drop `trace_id`, filter negative response times, deduplicate rows, and write `datetime64[ms]` Parquet files in memory (`BytesIO`).
* **Serverless Ticket Transformation (`lambda_process_tickets.py`):** Event-driven AWS Lambda function that cleans raw support ticket CSVs—fixing priority typos (`Lw` → `Low`, `Hgh` → `High`, `Medum` → `Medium`), dropping null `ticket_id` rows and empty columns (`agent_feedback`), filtering corrupted negative interactions (`-999999`), standardizing timestamps, and saving compressed Parquet files to S3.
* **Automated Warehouse Loading (`lambda_load_redshift.py`):** Triggers on new Parquet files in S3 and bulk-loads them into Amazon Redshift Serverless using `psycopg2` and the native `COPY` command.

---

## Power BI Dashboards

### 1. CarePlus Ticket Insights
<p align="center">
  <img src="docs/dashboard_tickets.png" alt="CarePlus Ticket Insights Dashboard" width="100%" />
</p>

* Tracks **206 total tickets** (**164 Resolved**, **34 Open**, **8 Escalated**) across **5 support agents**.
* Monitors **4.45 avg interactions** and **1,039 avg resolution minutes** across cleaned `High`, `Medium`, and `Low` priorities.
* Highlights channel efficiency—**Phone (84.00%)** and **Email (82.54%)** lead resolution rates, while **Chat** records the highest escalation rate (**7.84%**).

### 2. CarePlus Support Logs
<p align="center">
  <img src="docs/dashboard_logs.png" alt="CarePlus Support Logs Dashboard" width="100%" />
</p>

* Interactive daily telemetry view (e.g., `01 July 2025`: **89 cleaned logs**, **30 logged tickets**, **55.12% avg CPU**, **983 ms avg response time**).
* Visualizes standardized log-level distribution (**INFO 51.6%**, **DEBUG 41.5%**, **WARNING 6.74%**), CPU usage over time, user-agent traffic, and response-time latency buckets.

---

## Project Structure

```text
careplus-etl-aws/
├── docs/
│   ├── dashboard_tickets.png          # Ticket Insights Power BI screenshot
│   └── dashboard_logs.png             # Support Logs Power BI screenshot
├── src/
│   ├── ingestion/
│   │   ├── ingest_tickets.py          # Incremental MySQL -> S3 raw CSV
│   │   └── ingest_logs.py             # Incremental local logs -> S3 raw
│   ├── transformation/
│   │   ├── lambda_process_logs.py     # AWS Lambda: Regex log ETL -> Parquet
│   │   └── lambda_process_tickets.py  # AWS Lambda: Ticket cleaning -> Parquet
│   └── loading/
│       └── lambda_load_redshift.py    # AWS Lambda: S3 Parquet -> Redshift COPY
├── sql/
│   ├── create_tables.sql              # Redshift DDL schemas
│   
├── 
├── requirements.txt
└── .gitignore
```

---

## Quick Start

1. **Clone & install dependencies**
   ```bash
   git clone [https://github.com/](https://github.com/)<your-username>/careplus-etl-aws.git
   cd careplus-etl-aws
   python -m venv venv
   venv\Scripts\activate 
   pip install -r requirements.txt
   ```

2. **Configure environment variables** — Create a `.env` file in the root directory:
   ```env
   AWS_ACCESS_KEY_ID="your_access_key"
   AWS_SECRET_ACCESS_KEY="your_secret_key"
   AWS_REGION="ap-south-1"
   S3_BUCKET="careplus-data-store"

   MYSQL_HOST="localhost"
   MYSQL_USER="your_mysql_user"
   MYSQL_PASSWORD="your_mysql_password"
   MYSQL_DATABASE="careplus"
   ```

3. **Deploy & execute**
   * Deploy `lambda_process_logs.py` and `lambda_process_tickets.py` on AWS Lambda (`Python 3.14`, `x86_64`, `256 MB` RAM, `AWSSDKPandas-Python314` layer) with S3 `ObjectCreated` triggers.
   * Run `sql/create_tables.sql` in Amazon Redshift Serverless and deploy `lambda_load_redshift.py`.
   * Run the incremental ingestion scripts:
     ```bash
     python src/ingestion/ingest_tickets.py
     python src/ingestion/ingest_logs.py
     ```