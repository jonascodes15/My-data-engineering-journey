# My Data Engineering Journey

## Week 1: Docker & PostgreSQL Basics

This week covers foundational data engineering concepts: containerization with Docker, PostgreSQL databases, and data ingestion pipelines.

---

## Architecture Overview

The project uses Docker to containerize PostgreSQL and PgAdmin, with a Python ingestion script that loads taxi data into the database. All services are orchestrated using `docker-compose`.

---

## Components

### 1. **Dockerfile**
- Builds a custom Docker image based on Python 3.11-slim
- Installs dependencies: pandas, sqlalchemy, psycopg2-binary
- Copies and runs the `ingest_data.py` script

### 2. **ingest_data.py**
- Command-line ingestion script that downloads and processes CSV data
- Chunks large files (100,000 rows per chunk) for memory efficiency
- Accepts arguments via argparse for flexibility:
  - `--user`, `--password`, `--host`, `--port`, `--db`
  - `--table_name_1`, `--table_name_2` (supports two tables)
  - `--url_1`, `--url_2` (download URLs)
- Includes error handling for failed downloads

### 3. **docker-compose.yaml**
Orchestrates two services:
- **pgdatabase**: PostgreSQL 16 with persistent volume storage
- **pgadmin**: PgAdmin 8.6 web UI for database management
- Automatic networking between services on `pg_network`

### 4. **upload-data.ipynb**
Jupyter notebook for interactive data exploration and testing. Contains:
- CSV loading and inspection
- Data type conversions (datetime parsing)
- Chunked insertion into PostgreSQL
- DDL generation for table schema

---

## Quick Start

### Prerequisites
- Docker Desktop installed
- Working directory: `week_1_basics_and_setup/`

### Step 1: Start Services
```bash
docker-compose up -d
```
This starts PostgreSQL and PgAdmin in the background.

### Step 2: Access PgAdmin
- Open browser: `http://localhost:8080`
- Login: `admin@admin.com` / `root`
- Add new server connection to `pgdatabase:5432`

### Step 3: Build Ingestion Image
```bash
docker build -t taxi_ingest:v001 .
```

### Step 4: Find Network Name
First, find the network created by docker-compose:
```bash
docker network ls
```
Look for a network with a name like `week_1_basics_and_setup_pg_network` or similar.

### Step 5: Run Data Ingestion
Replace `<network-name>` with the network name from Step 4:
```bash
docker run -it \
  --network=<network-name> \
  taxi_ingest:v001 \
    --user=root \
    --password=root \
    --host=pgdatabase \
    --port=5432 \
    --db=ny_taxi \
    --table_name_1=yellow_taxi_data \
    --table_name_2=yellow_taxi_zone_data \
    --url_1="https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_2024-01.csv" \
    --url_2="https://d37ci6vzurychx.cloudfront.net/misc/taxi_zone_lookup.csv"
```

### Step 5: Verify Data
In PgAdmin, run:
```sql
SELECT COUNT(*) FROM yellow_taxi_data;
SELECT COUNT(*) FROM yellow_taxi_zone_data;
```

---

## Docker Commands Reference

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start services in background |
| `docker-compose down` | Stop and remove containers |
| `docker-compose logs -f pgdatabase` | View database logs |
| `docker ps -a` | List all containers |
| `docker build -t taxi_ingest:v001 .` | Build custom image |
| `docker rm $(docker ps -q -f status=exited)` | Clean up stopped containers |

---

## Key Concepts

**Docker Volumes**: The `-v` flag in docker-compose mounts `ny_taxi_postgres_data/` to persist data beyond container lifecycle.

**Networking**: docker-compose automatically creates an isolated network (`pg_network`) allowing services to communicate by service name (e.g., `pgdatabase`).

**Data Chunking**: Large CSV files are processed in 100k-row chunks to avoid memory issues.

---

## Troubleshooting

### Windows Compatibility
Both the ingestion script and notebook now use Python's `urllib` instead of `wget`, making them Windows-compatible. The code automatically downloads CSVs if they don't exist locally.

### Connection Issues
If you get "could not connect to server", verify:
1. Docker services are running: `docker ps`
2. PostgreSQL container is healthy: `docker logs pgdatabase`
3. You're using the correct network name from `docker network ls`
4. Host is set to `pgdatabase` (not `localhost`)

### Download Failures
- Check internet connection
- Verify URLs are accessible in your browser
- The script will skip downloads if files already exist locally
- Check available disk space for large datasets

### Port Conflicts
If port 5432 is already in use, edit `docker-compose.yaml`:
```yaml
ports:
  - "5433:5432"  # Use 5433 instead
```
Then update connection strings to use port 5433.
