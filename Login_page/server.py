from flask import Flask, request, jsonify, make_response, send_from_directory
from flask_cors import CORS, cross_origin
import os
from google.oauth2 import id_token
from google.auth.transport import requests

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Get the directory of the current script (server.py)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# The project root is one level up from BASE_DIR (i.e., 'last')
PROJECT_ROOT = os.path.join(BASE_DIR, '..')

# Mock user data (in production, this should be replaced with a database)
USERS = {
    "admin@example.com": {"password": "password123"},
    "user@example.com": {"password": "userpass"}
}

@app.route('/api/login', methods=['POST'])
@cross_origin()
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({"error": "Email and password are required"}), 400

        user = USERS.get(email)
        if user and user['password'] == password:
            # In a real application, generate a JWT token here
            return jsonify({
                "access_token": "your-jwt-token-here",
                "user": {
                    "email": email
                }
            })
        else:
            return jsonify({"error": "Invalid email or password"}), 401

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/register', methods=['POST'])
@cross_origin()
def register():
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return jsonify({'msg': 'Email and password are required'}), 400

        if email in USERS:
            return jsonify({'msg': 'User already exists with this email'}), 400

        USERS[email] = {'password': password, 'username': username}
        return jsonify({'msg': 'User registered successfully'}), 201
    except Exception as e:
        return jsonify({'msg': str(e)}), 500

@app.route('/protected', methods=['GET', 'OPTIONS'])
@cross_origin()
def protected():
    auth = request.headers.get('Authorization')
    if not auth:
        return jsonify({'msg': 'Missing token'}), 401
    # Mock user info
    return jsonify({'msg': f'Welcome, {auth.split()[-1]}!'}), 200

@app.route('/history', methods=['GET', 'OPTIONS'])
@cross_origin()
def history():
    auth = request.headers.get('Authorization')
    if not auth:
        return jsonify({'msg': 'Missing token'}), 401
    # Mock history data
    return jsonify({'history': [
        {'type': 'Heart Checkup', 'result': 'Normal', 'date': '2024-06-01'},
        {'type': 'Skin Checkup', 'result': 'No issues', 'date': '2024-05-15'}
    ]}), 200

@app.route('/api/google-login', methods=['POST'])
@cross_origin()
def google_login():
    try:
        # Receive the Google ID token from the frontend
        data = request.get_json()
        id_token_str = data.get('id_token')

        if not id_token_str:
            return jsonify({"error": "Missing ID token"}), 400

        # Specify the CLIENT_ID of the app that accesses the backend:
        CLIENT_ID = "1079807273598-30ckhicnf0frv26r17q84putrh9946md.apps.googleusercontent.com"

        try:
            # Verify the token. This also fetches the token's information from Google.
            # You can get user information like email, name, etc., from the payload.
            payload = id_token.verify_oauth2_token(id_token_str, requests.Request(), CLIENT_ID)

            user_email = payload['email']
            user_name = payload.get('name', user_email.split('@')[0]) # Use name if available, else part of email

            # At this point, the token is verified and you have user_email and user_name.
            # You would typically check if this user exists in your database.
            # If not, you might create a new user account.
            # If yes, log them in.

            # For now, we'll simulate successful login/registration
            return jsonify({
                "msg": "Google login successful",
                "user": {"email": user_email, "name": user_name},
                "access_token": "your-backend-generated-token" # Generate your own session token/JWT
            }), 200

        except ValueError:
            # Invalid token
            return jsonify({"error": "Invalid Google ID token"}), 401
        except Exception as e:
            # Other potential errors during verification
            return jsonify({"error": f"Token verification failed: {str(e)}"}), 500

    except Exception as e:
        # Catch any other unexpected errors in the request handling
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/')
def index_page():
    # Serve index.html from the project root directory
    return send_from_directory(PROJECT_ROOT, 'index.html')

@app.route('/Login_page/login.html')
def login_page():
    response = make_response(send_from_directory(os.path.join(PROJECT_ROOT, 'Login_page'), 'login.html'))
    # Remove Cross-Origin-Opener-Policy and Cross-Origin-Embedder-Policy headers
    response.headers['Cross-Origin-Opener-Policy'] = 'same-origin'
    response.headers['Cross-Origin-Embedder-Policy'] = 'credentialless'
    return response

@app.route('/image/<path:filename>')
def serve_image(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, 'image'), filename)

@app.route('/css/<path:filename>')
def serve_css(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, 'css'), filename)

@app.route('/js/<path:filename>')
def serve_js(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, 'js'), filename)

@app.route('/bootstrap-5.3.6-dist/<path:filename>')
def serve_bootstrap(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, 'bootstrap-5.3.6-dist'), filename)

@app.route('/Login_page/<path:filename>')
def serve_login_page_assets(filename):
    return send_from_directory(os.path.join(PROJECT_ROOT, 'Login_page'), filename)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5500))
    app.run(debug=True, port=port)