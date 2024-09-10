from flask import Flask, request, jsonify
import sqlite3
import secrets

app = Flask(__name__)

# This should be replaced with a more secure method of storing API keys
API_KEYS = set()

def generate_api_key():
    return secrets.token_urlsafe(32)

# Function to create a new API key
def create_api_key():
    api_key = generate_api_key()
    API_KEYS.add(api_key)
    return api_key

# Your existing functions (simplified for this example)
def get_student_info(student_id):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM students WHERE id = ?", (student_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'name': result[1],
            'email': result[2]
        }
    return None

def get_degree_info(degree_id):
    conn = sqlite3.connect('your_database.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM degrees WHERE id = ?", (degree_id,))
    result = cursor.fetchone()
    conn.close()
    
    if result:
        return {
            'id': result[0],
            'name': result[1],
            'department': result[2]
        }
    return None

# Decorator for checking API key
def require_api_key(view_function):
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key and api_key in API_KEYS:
            return view_function(*args, **kwargs)
        else:
            return jsonify({"error": "Invalid or missing API key"}), 401
    return decorated_function

# API endpoints
@app.route('/api/student/<int:student_id>', methods=['GET'])
@require_api_key
def api_get_student_info(student_id):
    student_info = get_student_info(student_id)
    if student_info:
        return jsonify(student_info)
    else:
        return jsonify({"error": "Student not found"}), 404

@app.route('/api/degree/<int:degree_id>', methods=['GET'])
@require_api_key
def api_get_degree_info(degree_id):
    degree_info = get_degree_info(degree_id)
    if degree_info:
        return jsonify(degree_info)
    else:
        return jsonify({"error": "Degree not found"}), 404

# Endpoint to generate a new API key (this should be secured in a real application)
@app.route('/api/generate_key', methods=['POST'])
def api_generate_key():
    new_key = create_api_key()
    return jsonify({"api_key": new_key})

if __name__ == '__main__':
    app.run(debug=True)

