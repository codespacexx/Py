from flask import Flask, request, jsonify
from flask_cors import CORS
from groq import Groq
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Initialize Groq client
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    raise ValueError("GROQ_API_KEY environment variable is not set.")

# Initialize Groq client (ensure no extra arguments like 'proxies' are passed)
client = Groq(api_key=GROQ_API_KEY)

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

# Function to generate AI response using Groq API
def generate_ai_response(user_message):
    try:
        # Send the user message to Groq API
        response = client.chat.completions.create(
            model="llama3-8b-8192",  # Use the Llama 3 model
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,  # Adjust for creativity
            max_tokens=1024,   # Limit response length
        )
        # Extract the AI's response
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error generating AI response: {e}")
        return "Sorry, I encountered an error while processing your request."

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
