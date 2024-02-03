from flask import Flask, jsonify, request
from flask_pymongo import PyMongo, ObjectId
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

# Configure MongoDB URI for MongoDB Atlas
app.config["MONGO_URI"] = "mongodb+srv://vermamonu185:adgauravad@cluster0.r65jrby.mongodb.net/rtspdb"

mongo = PyMongo(app)

@app.route('/overlay', methods=['POST'])
def create_overlay():
    data = request.json

    required_fields = ['content', 'position', 'x', 'y', 'width', 'height']
    for field in required_fields:
        if field not in data:
            return jsonify(success=False, message=f"{field} is required"), 400

    if not data['content'].strip():
        return jsonify(success=False, message="Overlay text cannot be empty"), 400

    valid_positions = ["Top Left", "Top Right", "Bottom Left", "Bottom Right", "Center"]
    if data['position'] not in valid_positions:
        return jsonify(success=False, message="Invalid position selected"), 400

    # Explicitly cast and validate x, y, width, and height
    try:
        x = int(data['x'])
        y = int(data['y'])
        width = int(data['width'])
        height = int(data['height'])
    except ValueError:
        return jsonify(success=False, message="x, y, width, and height must be valid integers"), 400

    if x < 0 or y < 0 or width <= 0 or height <= 0:
        return jsonify(success=False, message="Invalid dimensions or coordinates provided"), 400

    result = mongo.db.overlays.insert_one({
        'content': data['content'],
        'position': data['position'],
        'x': x,
        'y': y,
        'width': width,
        'height': height
    })

    return jsonify(success=True, message="Overlay created successfully", id=str(result.inserted_id)), 201


@app.route('/overlay', methods=['GET'])
def get_overlays():
    overlays = []
    for overlay in mongo.db.overlays.find():
        overlays.append({
            '_id': str(overlay['_id']),
            'content': overlay['content'],
            'position': overlay['position'],
            'x': overlay['x'],
            'y': overlay['y'],
            'width': overlay['width'],
            'height': overlay['height']
        })
    return jsonify(overlays)


@app.route('/overlay/<overlay_id>', methods=['PUT'])
def update_overlay(overlay_id):
    data = request.json
    mongo.db.overlays.update_one({'_id': ObjectId(overlay_id)}, {
        '$set': {
            'content': data['content'],
            'position': data['position'],
            'x': data['x'],
            'y': data['y'],
            'width': data['width'],
            'height': data['height']
        }
    })
    return jsonify({'message': 'Overlay updated successfully'})


@app.route('/overlay/<overlay_id>', methods=['DELETE'])
def delete_overlay(overlay_id):
    mongo.db.overlays.delete_one({'_id': ObjectId(overlay_id)})
    return jsonify({'message': 'Overlay deleted successfully'})


@app.route('/')
def index():
    return "Overlay API is running!"


if __name__ == '__main__':
    app.run(debug=True)
