



def query_splunk(query, duration_minutes):

    # Build the time range (last `duration_minutes` minutes)
    now = datetime.utcnow()
    earliest = (now - timedelta(minutes=int(duration_minutes))).isoformat() + "Z"
    latest = now.isoformat() + "Z"

    payload = {
        "search": f"search {query}",
        "earliest_time": earliest,
        "latest_time": latest,
        "output_mode": "json"
    }

    response = requests.post(f"{SPLUNK_HOST}/services/search/jobs/export", auth=HTTPBasicAuth(SPLUNK_USERNAME, SPLUNK_PASSWORD), data=payload, verify=False)
    response.raise_for_status()

    return response.json()


def detect_anomalies():
    data = request.get_json()
    model_name = data.get("modelName")
    query = data.get("splunkQuery")
    duration = data.get("durationMinutes")

    if not (model_name and query and duration):
        return jsonify({"success": False, "message": "modelName, splunkQuery, and durationMinutes are required"}), 400

    model_path = os.path.join(MODEL_DIR, f"{model_name}.pkl")
    if not os.path.exists(model_path):
        return jsonify({"success": False, "message": f"Model '{model_name}' not found"}), 404

    # Load model
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    # Query Splunk
    try:
        splunk_data = query_splunk(query, duration)
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

    # Assuming Splunk data contains timestamp and value
    df = pd.DataFrame(splunk_data["results"])
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['value'] = pd.to_numeric(df['value'])

    # Model prediction (update this if your model uses a different method)
    predictions = model.predict(df[['value']])
    
    # Optional: Confidence bounds (you can customize based on model)
    mean = df['value'].mean()
    std = df['value'].std()
    df['lower_bound'] = mean - 2 * std
    df['upper_bound'] = mean + 2 * std

    # Package result
    result = []
    for i, row in df.iterrows():
        result.append({
            "timestamp": row["timestamp"].isoformat(),
            "value": row["value"],
            "anomaly": int(predictions[i]),
            "lower": row["lower_bound"],
            "upper": row["upper_bound"]
        })

    return jsonify({"success": True, "data": result})
