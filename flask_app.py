from flask import Flask, request, jsonify
from pymongo import MongoClient

app = Flask(__name__)

# Koneksi ke MongoDB
MONGO_URI = "mongodb+srv://aizarhafizh:PLAGBpOEb0CkWwJh@codecado-cluster.c0zpy.mongodb.net/?appName=codecado-cluster"

client = MongoClient(MONGO_URI)         # Membuat client
db = client['codecado_Database']        # Membuat database
sensor_collection = db['SensorData']    # Membuat collection

# Landing Page 
@app.route("/")
def home():
    return "<h1>Welcome to the Sensor Data API</h1><p>Use /sensor endpoint to send data.</p>"

# End point ke data sensor
@app.route("/sensor", methods=["POST"])
def save_sensor_data():
    try:
        data = request.get_json()           # Mengambil data dalam bentuk JSON
        print("Received data:", data)       # Debugging untuk melihat apakah data masuk
        sensor_collection.insert_one(data)  # Memasukkan data ke collection (satu)

        # NOtify jika data berhasil disimpan
        return jsonify({"message": "Data saved!"})
    
    # Error handling
    except Exception as e:
        print("Error:", e)
        return jsonify({"error": str(e)}), 500

# Main function
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)