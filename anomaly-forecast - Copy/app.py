from flask import Flask, render_template, request, jsonify
import json
import os
from datetime import datetime
from zoneinfo import ZoneInfo  # Python 3.9+
import glob
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

    train_app_id = data.get("trainAppId", "unknown_app")  # fallback to avoid error
    train_detector_id = data.get("trainDetectorId", "unknown_app")  # fallback to avoid error

    
    # Define the filename with the train_jobs directory
    filename = os.path.join(TRAIN_JOBS_DIR, f"training_master_{train_app_id}.jsonl")

   # Check if trainDetectorId already exists in the file
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            for line in f:
                record = json.loads(line)
                if record.get("trainDetectorId") == train_detector_id:
                    return jsonify({"success": False, "message": f"trainDetectorName '{train_detector_id}' already exists in {filename}"}), 400
    
    # Eastern Time (automatically handles EST/EDT depending on date)
    timestamp_est = datetime.now(ZoneInfo("America/New_York")).isoformat()

    record = {
        "timestamp": timestamp_est,
        "trainAppId": train_app_id,
        "trainDetectorId": train_detector_id,
        "data": data
    }

    # Append to app-specific JSONL master file inside the train_jobs folder
    with open(filename, 'a') as f:
        f.write(json.dumps(record) + '\n')
        f.flush()  # flush ensures data is written to disk
        os.fsync(f.fileno())  # ensure it's synced for Windows

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

if __name__ == '__main__':
    app.run(debug=True)