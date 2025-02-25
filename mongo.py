from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Koneksi ke MongoDB
MONGO_URI = "mongodb+srv://kbagusm:JfIdrt0eTHsXtGEG@cluster-bagus.fbjve.mongodb.net/?retryWrites=true&w=majority&appName=Cluster-Bagus"

client = MongoClient(MONGO_URI)
db = client['MyDatabase']
sensor_collection = db['SensorData']

# route home
@app.route("/", methods=["GET"])
def home():
    return "Hello, World!"

@app.route("/sensor", methods=["POST"])
def save_sensor_data():
    try:
        data = request.get_json()
        sensor_collection.insert_one(data)
        return jsonify({"message": "Data saved!"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
