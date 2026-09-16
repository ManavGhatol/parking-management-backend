from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient

app = Flask(__name__)
CORS(app)

# 1. Exact Database se connect karein jo Compass me dikh raha hai
client = MongoClient("mongodb://localhost:27017/")
db = client["parking_audit_db"]        # Aapka DB name
collection = db["vehicles_test"]       # Aapka Collection name

# 2. Data insert karne ka API endpoint
@app.route('/add_vehicle', methods=['POST'])
def add_vehicle():
    try:
        data = request.json
        
        # Generate a dummy ticket_id for the UI to display
        ticket_id = data.get("ticket_id", f"TKT-FLASK-{len(list(collection.find()))}")
        
        # Frontend se aaya data MongoDB me insert karein
        collection.insert_one({
            "ticket_id": ticket_id,
            "reg_number": data.get("reg_number", ""), # UI ka REG. NUMBER
            "type": data.get("type", "Car"),
            "entry_time": data.get("entry_time", ""),
            "status": "PENDING"
        })
        
        # Returning dummy ticket_id and slot_id so the frontend doesn't crash on success display
        return jsonify({
            "message": "Success! Data MongoDB me chala gaya",
            "ticket_id": ticket_id,
            "slot_id": "FLASK-SLOT-1"
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5000, debug=True)
