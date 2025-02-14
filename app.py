# app.py
from flask import Flask, request, jsonify
from supabase import create_client, Client
from dotenv import load_dotenv
from flask_cors import CORS  # Import CORS
import os
# Load environment variables
load_dotenv()

app = Flask(__name__)

CORS(app)  # This will allow all domains, you can restrict it if needed
# Supabase client
supabase_url = os.getenv('SUPABASE_URL')
supabase_key = os.getenv('SUPABASE_KEY')
supabase: Client = create_client(supabase_url, supabase_key)

# Register endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    try:
        # Sign up the user with Supabase Auth
        auth_response = supabase.auth.sign_up({
            'email': email,
            'password': password,
        })

        # Save additional user data to the profiles table
        supabase.table('profiles').insert({
            'id': auth_response.user.id,
            'name': name,
            'email': email,
        }).execute()

        return jsonify({'message': 'Registration successful'}), 201
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Login endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    try:
        # Sign in the user with Supabase Auth
        auth_response = supabase.auth.sign_in_with_password({
            'email': email,
            'password': password,
        })

        return jsonify({
            'message': 'Login successful',
            'token': auth_response.session.access_token,
        }), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 400

# Profile endpoint
@app.route('/profile', methods=['GET'])
def profile():
    token = request.headers.get('Authorization')

    try:
        # Get the user from the token
        user = supabase.auth.get_user(token)

        # Fetch user details from the profiles table
        profile_data = supabase.table('profiles') \
            .select('name, email') \
            .eq('id', user.user.id) \
            .single() \
            .execute()

        return jsonify(profile_data.data), 200
    except Exception as e:
        return jsonify({'message': str(e)}), 401

# Run the server
if __name__ == '__main__':
    app.run(debug=True)
