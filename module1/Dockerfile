FROM python:3.11-slim

RUN apt-get update -y && apt-get install -y wget

RUN pip install pandas sqlalchemy psycopg2-binary

WORKDIR /app
COPY ingest_data.py ingest_data.py

ENTRYPOINT [ "python", "ingest_data.py" ]