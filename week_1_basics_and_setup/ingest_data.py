#!/usr/bin/env python
# coding: utf-8

import argparse
import time
import pandas as pd
import urllib.request
from sqlalchemy import create_engine
from pathlib import Path


def main(params):

    user = params.user
    password = params.password
    host = params.host
    port = params.port
    db = params.db
    table_name_1 = params.table_name_1
    table_name_2 = params.table_name_2
    url_1 = params.url_1
    url_2 = params.url_2

    csv_name_1 = 'output_taxi.csv'
    csv_name_2 = 'output_zones.csv'

    # Download Taxi CSV if not already present
    if not Path(csv_name_1).exists():
        print(f"Downloading Taxi CSV from {url_1}...")
        try:
            urllib.request.urlretrieve(url_1, csv_name_1)
            print(f"Successfully downloaded {csv_name_1}")
        except Exception as e:
            print(f"Error downloading taxi data: {e}")
            return
    else:
        print(f"{csv_name_1} already exists, skipping download")

    # Download Zones CSV if not already present
    if not Path(csv_name_2).exists():
        print(f"Downloading Zones CSV from {url_2}...")
        try:
            urllib.request.urlretrieve(url_2, csv_name_2)
            print(f"Successfully downloaded {csv_name_2}")
        except Exception as e:
            print(f"Error downloading zones data: {e}")
            return
    else:
        print(f"{csv_name_2} already exists, skipping download")

    # Connect to PostgreSQL
    engine = create_engine(f'postgresql://{user}:{password}@{host}:{port}/{db}')

    # --- Ingest Taxi Data in chunks ---
    taxi_iter = pd.read_csv(csv_name_1, iterator=True, chunksize=100000)
    taxi = next(taxi_iter)

    # Convert datetime columns
    taxi.tpep_pickup_datetime = pd.to_datetime(taxi.tpep_pickup_datetime)
    taxi.tpep_dropoff_datetime = pd.to_datetime(taxi.tpep_dropoff_datetime)

    # Create the table using the header, then insert first chunk
    taxi.head(0).to_sql(name=table_name_1, con=engine, if_exists='replace')
    taxi.to_sql(name=table_name_1, con=engine, if_exists='append')

    count = 1
    for chunk in taxi_iter:
        t_start = time.time()

        chunk.tpep_pickup_datetime = pd.to_datetime(chunk.tpep_pickup_datetime)
        chunk.tpep_dropoff_datetime = pd.to_datetime(chunk.tpep_dropoff_datetime)
        chunk.to_sql(name=table_name_1, con=engine, if_exists='append')

        t_end = time.time()
        print(f"Chunk {count} inserted in {round(t_end - t_start, 2)} seconds")
        count += 1

    print(f"Completed ingestion for {table_name_1}")

    # --- Ingest Zones Data (small file, no chunking needed) ---
    print(f"\nIngesting zones data into {table_name_2}...")
    zones = pd.read_csv(csv_name_2)
    zones.head(0).to_sql(name=table_name_2, con=engine, if_exists='replace')
    zones.to_sql(name=table_name_2, con=engine, if_exists='append')
    print(f"Completed ingestion for {table_name_2}")
    
    # Clean up database connection
    engine.dispose()


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Ingest CSV data to Postgres')
    parser.add_argument('--user', help='Username for Postgres')
    parser.add_argument('--password', help='Password for Postgres')
    parser.add_argument('--host', help='Host for Postgres')
    parser.add_argument('--port', help='Port for Postgres')
    parser.add_argument('--db', help='Database name for Postgres')
    parser.add_argument('--table_name_1', help='Table name for taxi data')
    parser.add_argument('--table_name_2', help='Table name for zones data')
    parser.add_argument('--url_1', help='URL of taxi CSV')
    parser.add_argument('--url_2', help='URL of zones CSV')

    args = parser.parse_args()
    main(args)