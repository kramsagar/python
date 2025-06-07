from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
import glob
import requests
import pandas as pd
import pickle
from flask import request, jsonify
from datetime import datetime, timedelta
from datetime import timezone
from requests.auth import HTTPBasicAuth
import os
import json
from datetime import datetime
import joblib
import re


# Directory where model files are stored
MODEL_DIR = 'models'  # Change this to your model directory

app = Flask(__name__)

# Ensure the train_jobs folder exists
TRAIN_JOBS_DIR = 'train_jobs'
if not os.path.exists(TRAIN_JOBS_DIR):
    os.makedirs(TRAIN_JOBS_DIR)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/train', methods=['POST'])
def train():
    data = request.get_json()
    print("Received data:", data)

    train_app_id = data.get("trainAppId", "unknown_app")
    train_detector_id = data.get("trainDetectorId", "unknown_detector")

    # Define app-specific .json file
    filename = os.path.join(TRAIN_JOBS_DIR, f"training_master_{train_app_id}.jsonl")

    # Load existing records or start new
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            records = json.load(f)
    else:
        records = {}

    # Check if detector already exists
    if train_detector_id in records:
        return jsonify({"success": False, "message": f"trainDetectorId '{train_detector_id}' already exists"}), 400

    # Add new record
    timestamp_est = datetime.now(ZoneInfo("America/New_York")).isoformat()
    new_record = {
        "timestamp": timestamp_est,
        "trainAppId": train_app_id,
        "trainDetectorId": train_detector_id,
        "data": data
    }

    records[train_detector_id] = new_record

    # Write back to JSON file
    with open(filename, 'w') as f:
        json.dump(records, f, indent=2)
        f.flush()
        os.fsync(f.fileno())

    return jsonify({"success": True, "message": f"Data received and logged to {filename}", "data": data})


# Endpoint to retrieve model names
@app.route('/models', methods=['GET'])
def get_models():
    # Get the detectAppId from query parameters
    detectAppId = request.args.get('detectAppId')

    if not detectAppId:
        return jsonify({"success": False, "message": "detectAppId is required"}), 400

    # Get list of model files in the 'models' directory
    model_files = glob.glob(os.path.join(MODEL_DIR, f"{detectAppId}*.pkl"))  # Filter models by detectAppId

    # Extract model names without extension
    model_names = [os.path.splitext(os.path.basename(file))[0] for file in model_files]

    # Return an empty list if no models are found
    return jsonify({"models": model_names})





# Example Splunk API config
# Example Splunk API config
SPLUNK_HOST = "https://localhost:8089"
SPLUNK_USERNAME = "rkyasan44"
SPLUNK_PASSWORD = "password01"

def query_splunk(query, duration_minutes):


    # Build the time range (last `duration_minutes` minutes)
    
    now = datetime.now(timezone.utc)
    earliest = (now - timedelta(minutes=int(duration_minutes))).isoformat() + "Z"
    latest = now.isoformat() + "Z"
    url = f"{SPLUNK_HOST}/services/search/jobs"
    payload = {
        "search": query,
        "earliest_time": "-1200m@m",
        "latest_time": "now",
        "output_mode": "json"
    }
    print("Splunk query:", payload)
    response = requests.post(url, auth=HTTPBasicAuth(SPLUNK_USERNAME, SPLUNK_PASSWORD), data=payload, verify=False)
    response.raise_for_status()
    print("Splunk response status code:", response.status_code)

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
            verify=False
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
        verify=False
    )

    if results_response.status_code != 200:
        print(f"Failed to fetch results: {results_response.text}")
        return None  # Return None instead of raising an exception

    return results_response.json().get("results", [])

    

@app.route('/detect', methods=['POST'])
def detect_anomalies():
    data = request.get_json()
    model_name = data.get("modelID")
    model_data = get_model_data_internal(data.get("detectAppId"), model_name)
    print("Model data:", model_data)
    query = model_data.get("data").get("trainSplunkQuery")
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



    print("Splunk query:", query)

    #duration = data.get("durationMinutes")
    SEARCHQUERY = f'search {query}'
    duration = 1200

    if not (model_name and query and duration):
        return jsonify({"success": False, "message": "modelName, splunkQuery, and durationMinutes are required"}), 400

    model_path = os.path.abspath(os.path.join(MODEL_DIR, f"{model_name}.pkl"))
    if not os.path.exists(model_path):
        return jsonify({"success": False, "message": f"Model '{model_name}' not found"}), 404

    print("Model path:", model_path)


    # Query Splunk
    try:
        splunk_data = query_splunk(SEARCHQUERY, duration)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    print("Splunk data:", splunk_data)

    # Convert Splunk JSON to DataFrame
    df = pd.DataFrame(splunk_data)
    df['timestamp'] = pd.to_datetime(df['_time'], utc=True).dt.tz_localize(None)
    df = df.sort_values(by='timestamp')
    df['value'] = pd.to_numeric(df['metric_value'], errors='coerce')

    # Prepare DataFrame in Prophet format
    df_prophet = pd.DataFrame({
        'ds': df['timestamp'],
        'y': df['value']
    })

    # Load model
    model= None
    with open(model_path, 'rb') as f:
        model = joblib.load(model_path)

    # Predict
    forecast = model.predict(df_prophet[['ds']])

    # Add actual values
    forecast['y'] = df_prophet['y'].values

    # Determine anomalies (outside prediction interval)
    forecast['anomaly'] = (
        (forecast['y'] < forecast['yhat_lower']) |
        (forecast['y'] > forecast['yhat_upper'])
    ).astype(int)

    # Package result for UI or JSON output
    result = []
    for _, row in forecast.iterrows():
        result.append({
            "timestamp": row["ds"].isoformat(),
            "value": row["y"],
            "predicted": row["yhat"],
            "lower": row["yhat_lower"],
            "upper": row["yhat_upper"],
            "anomaly": int(row["anomaly"])
        })

    print("Detection result:", result)
    return jsonify({"success": True, "data": result})


@app.route('/get_model_data',methods=['GET'])
def get_model_data():
    app_id = request.args.get('appId')
    model_id = request.args.get('modelId')
    model_data = get_model_data_internal(app_id, model_id)
    if not model_data:
        return jsonify({"error": "Model not found"}), 404
    
    return jsonify(model_data)

def get_model_data_internal(app_id, model_id):
    print("App ID:", app_id)
    print("Model ID:", model_id)
    file_path = f'train_jobs/training_master_{app_id}.jsonl'
    if not os.path.exists(file_path):
        return jsonify({"error": "File not found"}), 404
    with open(file_path, 'r') as f:
        data = json.load(f)
    model_data = data.get(model_id)

    print("Model data1:", model_data)

    return model_data

if __name__ == '__main__':
    app.run(debug=True)