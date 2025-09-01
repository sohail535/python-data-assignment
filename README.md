# Data Pipeline Project

A robust data pipeline that extracts product data from multiple sources, transforms it through bronze, silver, and gold layers, and loads it into a PostgreSQL database. The pipeline is containerized with Docker and orchestrated using Prefect.

## 🏗 Architecture

### Data Flow
```
                        Bronze              Silver              Gold
┌──────────────┐
│ JSON/CSV/XML ├─┐
└──────────────┘ │   ┌──────────┐        ┌──────────┐        ┌──────────┐
                 ├──►│  Raw     │        │Validated │        │Category  │
┌──────────────┐ │   │  JSONL   ├───────►│Normalized├───────►│Aggregates│
│  REST API    ├─┤   │  Files   │        │Parquet   │        │          │
└──────────────┘ │   └────┬─────┘        └────┬─────┘        └────┬─────┘
                 │        │                   │                   │
┌──────────────┐ │        │                   │                   │
│Web Scraping  ├─┘        │                   │                   │
└──────────────┘          ▼                   ▼                   ▼
                   ┌──────────────────────────────────────────────────┐
                   │                   PostgreSQL                     │
                   └──────────────────────────────────────────────────┘
```

### System Architecture
```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Mock API   │     │ Mock Website│     │  Pipeline   │     │  Database   │
│  Service    │     │  Service    │     │  Container  │     │  (Postgres) │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │                   │
       │                   │                   │                   │
       └───────────────────┴────────┬──────────┴────────┬──────────┘
                                    │                   │
                           ┌────────┴──────────┐ ┌──────┴──────┐
                           │    Data Volume    │ │   Postgres  │
                           │                   │ │    Volume   │
                           └───────────────────┘ └─────────────┘
```

### Components
- **Extract Layer**: Handles data ingestion from multiple sources
  - File parsers (JSON, CSV, XML)
  - REST API client with pagination and retry logic
  - Web scraper for dynamic content
- **Transform Layer**: 
  - Bronze: Raw data in JSONL format
  - Silver: Validated, normalized data in Parquet
  - Gold: Category-level aggregations
- **Load Layer**:
  - PostgreSQL database with idempotent upserts
  - Separate tables for silver and gold data

## 🚀 Quick Start

### Prerequisites
- Docker (20.10 or newer)
- Docker Compose (v2.x)
- Make (optional, but recommended)
- At least 4GB of available RAM (for Spark processing)
- Python 3.12+ (if running locally without Docker)

### Setup and Run

1. Clone the repository:
```bash
git clone https://github.com/pankaj7822/python-data-assignment.git
cd python-data-assignment
```

2. Start the services:
```bash
make build  # Build all Docker images
make up     # Start all services
```

3. Run the pipeline:
```bash
make run-pipeline
```

4. Monitor the pipeline:
```bash
make logs
```

5. Clean up:
```bash
make clean  # Stop services and clean data
```

## 🛠 Development Setup

For local development without Docker:

1. Set up Python environment (requires Python 3.12+):
```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install build dependencies first
pip install --upgrade pip setuptools wheel cython

# Install project dependencies
pip install -r requirements.txt
```

Alternatively, you can use the setup script:
```bash
chmod +x setup.sh
./setup.sh
```

2. Verify installation:
```bash
python -c "import prefect; print(prefect.__version__)"
python -c "import pendulum; print(pendulum.__version__)"
```

3. Run services locally:
```bash
# Terminal 1: Run mock API
make api

# Terminal 2: Run mock website
make site
```

4. Run tests:
```bash
make test
```

Note: If you encounter any dependency issues, ensure you have the following system packages:
- Python 3.12 development files
- PostgreSQL development files (for psycopg2)
- System build tools (gcc, make, etc.)

## 📁 Project Structure

```
.
├── data/                    # Data directory
│   ├── raw/                # Raw input files
│   ├── bronze/             # Bronze layer JSONL files
│   ├── silver/             # Silver layer Parquet files
│   └── gold/               # Gold layer aggregations
├── pipeline/               # Core pipeline components
│   ├── io/                 # Data input/output handlers
│   ├── transforms/         # Data transformation logic
│   ├── quality/           # Data validation
│   ├── storage/           # Database operations
│   └── spark_jobs/        # Spark transformation jobs
├── services/              # Mock services
│   ├── mock_api/         # REST API service
│   └── mock_site/        # Dynamic website
├── orchestration/         # Pipeline orchestration
│   └── prefect/          # Prefect flows and tasks
├── migrations/           # Database migrations
├── tests/               # Test suite
├── docker-compose.yml   # Service orchestration
├── Dockerfile          # Pipeline image definition
└── Makefile           # Common commands
```

## ⚙️ Configuration

Environment variables (can be set in docker-compose.yml):

```yaml
# Database
POSTGRES_HOST: Database host (default: postgres)
POSTGRES_PORT: Database port (default: 5432)
POSTGRES_DB: Database name (default: products)
POSTGRES_USER: Database user (default: postgres)
POSTGRES_PASSWORD: Database password (default: postgres)

# Services
API_BASE_URL: Mock API URL (default: http://mock_api:5000)
WEBSITE_URL: Mock website URL (default: http://mock_website:80)

# Scraper
SCRAPER_WAIT_TIMEOUT: Page load timeout (default: 10)
SCRAPER_DYNAMIC_WAIT: Dynamic content wait (default: 2)
```

## 🔄 Data Models

### Silver Layer (products_silver)
- product_id (PK)
- name
- category
- price
- currency
- rating
- in_stock
- last_updated
- source
- ingested_at

### Gold Layer (category_price_summary_gold)
- category (PK)
- avg_price
- avg_rating
- item_count
- last_refresh_ts

## 📊 Monitoring

- Pipeline logs available via `make logs`
- Failed validations in `data/silver/rejected.jsonl`
- Database schema migrations tracked in `migrations/`

# Test Coverage

Run the test suite to verify functionality:
```bash
make test
```

Key test areas:
- File parsers (JSON, CSV, XML)
- API client with pagination and retry logic
- Data validation and normalization
- Database operations
- End-to-end pipeline flow
