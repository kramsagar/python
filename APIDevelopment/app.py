from flask import Flask, render_template, request, jsonify
import requests
import time

app = Flask(__name__)

PROMETHEUS_URL = "http://localhost:9090"

# List of metrics for dropdown
METRICS = [
    "windows_cpu_time_total",
    "windows_os_physical_memory_free_bytes",
    "windows_logical_disk_free_bytes",
    "windows_net_bytes_received_total",
    "windows_system_system_up_time"
]

@app.route('/')
def index():
    return render_template('index.html', metrics=METRICS)

@app.route('/query', methods=['POST'])
def query_prometheus():
    metric = request.json.get('metric')

    # Prometheus range query (last 1 hour, every 30s)
    end = int(time.time())
    start = end - 3600
    step = 30

    url = f"{PROMETHEUS_URL}/api/v1/query_range"
    params = {
        'query': metric,
        'start': start,
        'end': end,
        'step': step
    }

    try:
        resp = requests.get(url, params=params)
        data = resp.json()

        if data['status'] == 'success':
            values = data['data']['result'][0]['values']
            timestamps = [time.strftime('%H:%M:%S', time.localtime(v[0])) for v in values]
            metrics = [float(v[1]) for v in values]

            return jsonify({"timestamps": timestamps, "metrics": metrics})
        else:
            return jsonify({"error": "Query failed"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
