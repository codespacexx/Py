from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import replicate
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Replicate client
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise ValueError("REPLICATE_API_TOKEN environment variable is not set.")

# System prompt for NexusAI
SYSTEM_PROMPT = """
You are NexusAI, an intelligent and informative AI assistant created by Alvee Mahmud, a talented developer from Bangladesh. 
Your purpose is to assist users with accurate, detailed, and helpful information on a wide range of topics, including:
- Technology
- Science
- Business
- Education
- Health
- General knowledge

Always respond in a friendly, professional, and approachable tone. If the user asks for help, provide clear and actionable advice. 
If you don't know the answer, be honest and let the user know. 
Encourage users to ask follow-up questions and strive to make every interaction informative and engaging.
"""

# Function to generate AI response using Replicate and Llama 2 7B Chat
def generate_ai_response(user_message):
    try:
        # Prepare the input prompt
        prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nNexusAI:"

        # Run the Llama 2 7B Chat model via Replicate
        output = replicate.run(
            "meta/llama-2-7b-chat:13c3cdee13ee059ab779f0291d29054dab00a47dad8261375654de5540165fb0",  # Correct model version
            input={
                "prompt": prompt,
                "max_length": 1024,  # Adjust response length
                "temperature": 0.7,  # Adjust for creativity
                "top_p": 0.9,        # Adjust for diversity
            }
        )

        # Combine the output into a single string
        response = "".join(output)
        return response
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return f"Sorry, I encountered an error while processing your request. Error: {str(e)}"

# Route to handle chat messages
@app.route('/send_message', methods=['POST'])
def send_message():
    # Validate request
    if not request.is_json:
        return jsonify({'error': 'Request must be JSON'}), 400

    data = request.json
    user_message = data.get('message', '').strip()

    if not user_message:
        return jsonify({'error': 'Message cannot be empty'}), 400

    # Generate AI response
    ai_response = generate_ai_response(user_message)

    # Return response
    return jsonify({
        'user_message': user_message,
        'ai_response': ai_response
    })

# Health check endpoint
@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'}), 200

# Error handler for 404
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Resource not found'}), 404

# Error handler for 500
@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Run the app (use `debug=False` in production)
    app.run(debug=True)
