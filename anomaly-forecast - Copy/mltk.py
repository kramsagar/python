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
def run_splunk_query(query, earliest="-15m@m", latest="now"):
    SEARCH_QUERY = 'search index="summary_transactions" | table _time, avg_response_time, source'
    
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


def train_model_from_splunk(query,detector_id="default_model"):
    results = run_splunk_query(query)
    if results is None or len(results) == 0:
        print("No results returned from Splunk query.")
        return

    times = []
    values = []

    for row in results:
        timestamp = row.get("_time")
        val = row.get("avg_response_time")
        if timestamp and val:
            try:
                times.append(date_parser.parse(timestamp).timestamp())  # convert _time to timestamp
                values.append(float(val))
            except ValueError:
                continue

    if not values:
        print("No data to train model.")
        return

    # Convert to numpy arrays
    X = np.array(times).reshape(-1, 1)
    y = np.array(values)

    model_path = Path(f"./models/{detector_id}.pkl")
    model_path.parent.mkdir(parents=True, exist_ok=True)

    # Load existing model or create new one
    if model_path.exists():
        model = joblib.load(model_path)
        print(f"Loaded existing model for {detector_id}")
    else:
        model = LinearRegression()
        print(f"Creating new model for {detector_id}")

    # Train model
    model.fit(X, y)
    joblib.dump(model, model_path)
    print(f"Model trained and saved for {detector_id}")

    # Simple prediction & anomaly detection
    predictions = model.predict(X)
    errors = np.abs(predictions - y)
    mean_error = np.mean(errors)
    anomalies = [(t, actual, pred) for t, actual, pred, err in zip(times, y, predictions, errors) if err > 1.5 * mean_error]
    
    print(f"Trained on {len(values)} points. Found {len(anomalies)} anomalies.")

# --------------------- JOB HANDLER ---------------------
def process_job(job_data,detector_id):
    data = job_data["data"]
    interval_str = data.get("trainInterval")
    query = data.get("trainSplunkQuery")

    if not query or interval_str not in INTERVAL_FORMAT:
        print("Skipping invalid job config.")
        return

    train_model_from_splunk(query,detector_id)


# --------------------- SCHEDULER ---------------------
def schedule_job(filepath, job):
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
            for line in f:
                try:
                    job = json.loads(line.strip())
                    schedule_job(job_file, job)
                except json.JSONDecodeError as e:
                    print(f"Error decoding line in {job_file.name}: {e}")

    print("Scheduler started. Waiting for jobs...")
    while True:
        time.sleep(1)


# --------------------- MAIN ---------------------
if __name__ == "__main__":
    start_scheduler()
    print("Scheduler stopped.")
