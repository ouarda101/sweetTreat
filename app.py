from flask import Flask, request, jsonify, send_from_directory, session, redirect, url_for
from flask_cors import CORS
from flask_bcrypt import Bcrypt
import mysql.connector
import os

app = Flask(__name__, static_folder='frontend')
CORS(app)

app.config['SECRET_KEY'] = 'your_secret_key_for_sessions_very_important_change_me_in_production'
bcrypt = Bcrypt(app)

DB_CONFIG = {
    'host': 'localhost',
    'user': 'bakery_user',
    'password': 'your_secure_password', # IMPORTANT: Use the password you set in MySQL
    'database': 'bakery_db'
}

def get_db_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        return conn
    except mysql.connector.Error as err:
        print(f"Database connection error: {err}")
        return None

@app.route('/')
def serve_index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/login')
def serve_login_page():
    return send_from_directory(app.static_folder, 'login.html')

@app.route('/register')
def serve_register_page():
    return send_from_directory(app.static_folder, 'register.html')

# NEW: Route to serve the shop page
@app.route('/shop')
def serve_shop_page():
    return send_from_directory(app.static_folder, 'shop.html')

@app.route('/<path:path>')
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)

@app.route('/api/donuts', methods=['GET'])
def get_donuts():
    search_query = request.args.get('search', '')
    
    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        if search_query:
            query = "SELECT id, name, description, price, image_url FROM donuts WHERE name LIKE CONCAT('%%', %s, '%%')"
            cursor.execute(query, (search_query,))
        else:
            cursor.execute("SELECT id, name, description, price, image_url FROM donuts")
        
        donuts = cursor.fetchall()
        return jsonify(donuts), 200
    except mysql.connector.Error as err:
        print(f"Error fetching donuts: {err}")
        return jsonify({"error": "Failed to fetch donuts"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/donuts', methods=['POST'])
def add_donut():
    data = request.get_json()
    name = data.get('name')
    description = data.get('description')
    price = data.get('price')
    image_url = data.get('image_url')

    if not all([name, price]):
        return jsonify({"error": "Name and price are required"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    try:
        query = "INSERT INTO donuts (name, description, price, image_url) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (name, description, price, image_url))
        conn.commit()
        return jsonify({"message": "Donut added successfully", "id": cursor.lastrowid}), 201
    except mysql.connector.Error as err:
        print(f"Error adding donut: {err}")
        return jsonify({"error": "Failed to add donut"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/login', methods=['POST'])
def login_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT id, username, password_hash FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and bcrypt.check_password_hash(user['password_hash'], password):
            return jsonify({"message": "Login successful", "username": user['username']}), 200
        else:
            return jsonify({"error": "Invalid username or password"}), 401
    except mysql.connector.Error as err:
        print(f"Error during login: {err}")
        return jsonify({"error": "Internal server error during login"}), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/api/register', methods=['POST'])
def register_user():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password are required"}), 400

    conn = get_db_connection()
    if conn is None:
        return jsonify({"error": "Database connection failed"}), 500

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify({"error": "Username already exists"}), 409 # Conflict
        
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        query = "INSERT INTO users (username, password_hash) VALUES (%s, %s)"
        cursor.execute(query, (username, hashed_password))
        conn.commit()
        return jsonify({"message": "Registration successful", "username": username}), 201 # Created
    except mysql.connector.Error as err:
        print(f"Error during registration: {err}")
        return jsonify({"error": "Internal server error during registration"}), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == '__main__':
    frontend_dir = 'frontend'
    if not os.path.exists(frontend_dir):
        os.makedirs(frontend_dir)
        print(f"Created '{frontend_dir}' directory.")
    app.run(debug=True)
