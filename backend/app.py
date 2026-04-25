from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from face_logic import processor
import os

app = Flask(__name__, static_folder='static')
CORS(app)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "message": "Face Auth API is running"})

@app.route('/register', methods=['POST'])
def register():
    data = request.json
    user_id = data.get('userId')
    image_data = data.get('image')

    if not user_id or not image_data:
        return jsonify({"error": "Missing userId or image"}), 400

    img = processor.decode_image(image_data)
    if img is None:
        return jsonify({"error": "Invalid image data"}), 400

    success = processor.register_face(user_id, img)
    if success:
        return jsonify({"message": f"User {user_id} registered successfully"})
    else:
        return jsonify({"error": "Registration failed"}), 500

@app.route('/authenticate', methods=['POST'])
def authenticate():
    data = request.json
    image_data = data.get('image')

    if not image_data:
        return jsonify({"error": "Missing image"}), 400

    img = processor.decode_image(image_data)
    if img is None:
        return jsonify({"error": "Invalid image data"}), 400

    result = processor.authenticate(img)
    return jsonify(result)

if __name__ == '__main__':
    if not os.path.exists("database"):
        os.makedirs("database")
    if not os.path.exists("static"):
        os.makedirs("static")
    app.run(host='0.0.0.0', port=5000, debug=True)
