from flask import Flask
import time

app = Flask(__name__)

@app.route("/")
def home():
    return "Service is running."

@app.route("/delay")
def delay():
    time.sleep(10)
    return "Delayed response."

@app.route("/error")
def error():
    raise Exception("Simulated error!")

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0')
