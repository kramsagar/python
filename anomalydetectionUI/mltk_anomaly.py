import os
import json
import time
import threading
from datetime import datetime, timedelta
from dateutil import parser as date_parser
from pathlib import Path
import requests
from requests.auth import HTTPBasicAuth
import numpy as np
from sklearn.linear_model import LinearRegression
import joblib
import logging
import logging.config 
import yaml
import sys
import warnings
import traceback
import pandas as pd
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import IsolationForest
from sklearn.metrics import mean_absolute_error
import matplotlib.pyplot as plt
from datetime import datetime, timedelta, timezone
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import re
import h2o
from prophet import Prophet
from pathlib import Path
import pandas as pd
import numpy as np
from dateutil import parser as date_parser

# Start H2O
h2o.init()

MODEL_DIR = 'models'  # Change this to your model directory

# --------------------- SPLUNK CONFIG ---------------------
SPLUNK_HOST = "https://localhost:8089"
SPLUNK_USERNAME = "rkyasan44"
SPLUNK_PASSWORD = "password01"
VERIFY_SSL = False  # Change to True in production
STATUS_REGISTRY_FILE = Path("./status_registry.json")
status_registry = {}
registry_lock = threading.Lock()


# --------------------- CONFIG ---------------------
JOB_DIR = Path("./train_jobs")
INTERVAL_FORMAT = {
    "1hr": timedelta(hours=1),
    "30min": timedelta(minutes=30),
    "15min": timedelta(minutes=15),
    "5min": timedelta(minutes=5),
    "1min": timedelta(minutes=1),    
    "1day": timedelta(minutes=1440)
}

def load_status_registry():
    global status_registry
    print(f"Loading status_registry from {STATUS_REGISTRY_FILE}")
    try:
        if STATUS_REGISTRY_FILE.exists():
            with STATUS_REGISTRY_FILE.open() as f:
                status_registry = json.load(f)
        else:
            status_registry = {}
        print(f"Loaded status_registry: {status_registry}")
    except Exception as e:
        print(f"Error loading status_registry: {e}")
        status_registry = {}



def save_status_registry():
    global status_registry
    try:
        with registry_lock:
            with STATUS_REGISTRY_FILE.open("w") as f:
                json.dump(status_registry, f, indent=2, default=str)
        print(f"[INFO] Status registry saved to: {STATUS_REGISTRY_FILE.resolve()}")
    except Exception as e:
        print(f"[ERROR] Failed to save registry: {e}")


# --------------------- UTILITY FUNCTIONS ---------------------
def run_splunk_query(data):
    detector_id = data.get("trainDetectorId", "Unknown")
    interval_str = data.get("trainInterval")
    interval = INTERVAL_FORMAT.get(interval_str)
    query = data.get("trainSplunkQuery")
    now = datetime.now(timezone.utc)
    earliest = (now - interval).strftime("%Y-%m-%dT%H:%M:%S")
    latest = now.strftime("%Y-%m-%dT%H:%M:%S")
    print(f"Running Splunk query for {detector_id} from {earliest} to {latest}")
    query = re.sub(r'index=([\w_]+)', r'index="\1"', query)
        # Extract the column names from the table command
    table_match = re.search(r'\|\s*table\s+([^|]+)', query)
    
    if not table_match:
        raise ValueError("No `table` clause found in the query.")

    columns = [col.strip() for col in table_match.group(1).split(',')]
    
    if len(columns) < 2:
        raise ValueError("Query must contain at least two columns (e.g. _time, metric_field).")
    
    time_col = columns[0]
    metric_col = columns[1]

    # Insert rename before table
    rename_stmt = f'rename {metric_col} as metric_value'
    query = query.replace(f'table {time_col}, {metric_col}', f'{rename_stmt} | table {time_col}, metric_value')


    print(f"Splunk query: {query}")
    

    SEARCH_QUERY = f'search {query}'
    url = f"{SPLUNK_HOST}/services/search/jobs"
    data = {
        'search': SEARCH_QUERY,
        'output_mode': 'json',
        "earliest_time": earliest,
        "latest_time": latest
    }
    response = requests.post(url, auth=HTTPBasicAuth(SPLUNK_USERNAME, SPLUNK_PASSWORD), data=data, verify=VERIFY_SSL)
    response.raise_for_status()
    print(response.status_code)

    sid = response.json()['sid']
    if not sid:
        print("Failed to retrieve search ID (SID).")
        return None

    # Polling the search job until it's done
    while True:
        results_url = f"{SPLUNK_HOST}/services/search/jobs/{sid}"
        status_response = requests.get(
            results_url,
            auth=HTTPBasicAuth(SPLUNK_USERNAME, SPLUNK_PASSWORD),
            params={"output_mode": "json"},
            verify=VERIFY_SSL
        )

        if status_response.status_code != 200:
            print(f"Failed to check search job status: {status_response.text}")
            return None

        job_status = status_response.json()['entry'][0]['content']['isDone']
        if job_status:
            print(f"Search job {sid} is complete.")
            break
        else:
            print(f"Search job {sid} is still running. Waiting...")
            time.sleep(2)

    # Fetch the search results once it's done
    results_url = f"{SPLUNK_HOST}/services/search/jobs/{sid}/results"
    results_response = requests.get(
        results_url,
        auth=HTTPBasicAuth(SPLUNK_USERNAME, SPLUNK_PASSWORD),
        params={"output_mode": "json"},
        verify=VERIFY_SSL
    )

    if results_response.status_code != 200:
        print(f"Failed to fetch results: {results_response.text}")
        return None  # Return None instead of raising an exception

    return results_response.json().get("results", [])


def train_model_from_splunk(data):
    detector_id = data.get("trainDetectorId", "Unknown")
    results = run_splunk_query(data)
    if results is None or len(results) == 0:
        print("No results returned from Splunk query.")
        return

    times = []
    values = []

    for row in results:
        timestamp = row.get("_time")
        val = row.get("metric_value")
        if timestamp and val:
            try:
                times.append(date_parser.parse(timestamp))  # datetime for Prophet
                values.append(float(val))
            except ValueError:
                continue

    if not values:
        print("No data to train model.")
        return []
    
    # Create DataFrame in Prophet format
    df = pd.DataFrame({
        "ds": pd.to_datetime(times),
        "y": values
    })

    # Remove timezone information (make datetime naive)
    df["ds"] = df["ds"].dt.tz_localize(None)
    

     # Define model path
    model_path = Path(f"./models/{detector_id}.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing model if present (retrain anyway - Prophet doesn't support incremental fitting)
    if model_path.exists():
        print(f"Loaded existing model for {detector_id}, retraining with new data")
    else:
        print(f"Creating new model for {detector_id}")

    model = Prophet()
    model.fit(df)

    # Save model
    joblib.dump(model, model_path)
    print(f"Model trained and saved at {model_path}")

    # Forecast on historical points
    future = df[["ds"]]
    forecast = model.predict(future)

    df["yhat"] = forecast["yhat"]
    df["error"] = np.abs(df["y"] - df["yhat"])
    mean_error = df["error"].mean()

    anomalies_df = df[df["error"] > 1.5 * mean_error]
    anomalies = list(zip(anomalies_df["ds"], anomalies_df["y"], anomalies_df["yhat"]))

    print(f"Trained on {len(values)} points. Found {len(anomalies)} anomalies.")

# --------------------- JOB HANDLER ---------------------
def process_job(job_data,detector_id):
    data = job_data["data"]
    interval_str = data.get("trainInterval")
    query = data.get("trainSplunkQuery")

    if not query or interval_str not in INTERVAL_FORMAT:
        print("Skipping invalid job config.")
        return

    train_model_from_splunk(data)


# --------------------- SCHEDULER ---------------------
def schedule_job(filepath, job):
    print(f"[INFO] Scheduling job: {job}")
    print(f"[INFO] Job file: {filepath}")

    data = job["data"]
    interval_str = data.get("trainInterval")
    interval = INTERVAL_FORMAT.get(interval_str)
    detector_id = job.get("trainDetectorId", "Unknown")

    def job_thread():
        while True:
            now = datetime.now(timezone.utc).isoformat() 
            print(f"[INFO] Running job: {detector_id} at {now}")
            try:
                process_job(job, detector_id)
                status = "success"
            except Exception as e:
                print(f"[ERROR] Job {detector_id} failed: {e}")
                traceback.print_exc()
                status = "failed"

            next_run_time = (datetime.now(timezone.utc) + interval).isoformat()
            new_status = {
                "detector_id": detector_id,
                "last_run_time": now,
                "next_run_time": next_run_time,
                "status": status
            }

            with registry_lock:
                status_registry[detector_id] = new_status

            save_status_registry()
            time.sleep(interval.total_seconds())

    thread = threading.Thread(target=job_thread, daemon=True)
    thread.start()


def start_scheduler():
    load_status_registry()
    if not JOB_DIR.exists():
        print(f"Job directory not found: {JOB_DIR}")
        return

    for job_file in JOB_DIR.glob("*.jsonl"):
        with job_file.open() as f:
            try:
                jobs = json.load(f)  # loads entire file as a single JSON object
                for job_id, job_data in jobs.items():
                    schedule_job(job_file, job_data)
            except json.JSONDecodeError as e:
                print(f"Error decoding line in {job_file.name}: {e}")

    print("Scheduler started. Waiting for jobs...")
    while True:
        time.sleep(1)

class JobHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)
        if file_path.suffix != ".jsonl":
            return  # Ignore non-jsonl files

        print(f"[INFO] New .jsonl file detected: {file_path.name}")
        try:
            with file_path.open() as f:
                
                    jobs = json.load(f)  # loads entire file as a single JSON object
                    for job_id, job_data in jobs.items():
                        schedule_job(file_path.name, job_data)

        except Exception as e:
            print(f"Error reading new job file {file_path}: {e}")


# --------------------- MAIN ---------------------
if __name__ == "__main__":
    # Start scheduler in a separate thread
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    # Start watchdog observer to monitor for new .jsonl files
    event_handler = JobHandler()
    observer = Observer()
    observer.schedule(event_handler, str(JOB_DIR), recursive=False)
    observer.start()

    print("Started job scheduler and file observer.")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()