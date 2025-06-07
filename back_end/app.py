from flask import Flask, render_template, request, redirect, url_for
from flask_cors import CORS

app = Flask(__name__, static_folder='../', template_folder='../login')
CORS(app)

@app.route('/')
def index():
    return render_template('log.html')

@app.route('/login', methods=['POST'])
def login():
    # This is where you would verify the ID token from Google
    # For now, we'll just print it and redirect.
    token = request.form.get('credential')
    print(f"Received ID Token: {token}")
    # In a real application, you would verify this token with Google's API
    # and then create a session for the user.
    return redirect(url_for('dashboard'))

@app.route('/dashboard')
def dashboard():
    return "Welcome to your dashboard!"

if __name__ == '__main__':
    app.run(port=5501) 