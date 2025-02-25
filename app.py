from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from transformers import AutoTokenizer, AutoModelForCausalLM
import torch
import os

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Load Hugging Face model and tokenizer
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"  # Replace with your desired Llama 2 model
HUGGING_FACE_TOKEN = os.getenv("HUGGING_FACE_TOKEN")  # Hugging Face API token

if not HUGGING_FACE_TOKEN:
    raise ValueError("HUGGING_FACE_TOKEN environment variable is not set.")

# Load the tokenizer and model
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=HUGGING_FACE_TOKEN)
model = AutoModelForCausalLM.from_pretrained(MODEL_NAME, use_auth_token=HUGGING_FACE_TOKEN)

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

# Function to generate AI response using Hugging Face Llama 2
def generate_ai_response(user_message):
    try:
        # Prepare the input prompt
        prompt = f"{SYSTEM_PROMPT}\n\nUser: {user_message}\nNexusAI:"

        # Tokenize the input
        inputs = tokenizer(prompt, return_tensors="pt")

        # Generate the response
        with torch.no_grad():
            outputs = model.generate(
                inputs.input_ids,
                max_length=1024,  # Adjust response length
                temperature=0.7,  # Adjust for creativity
                top_p=0.9,        # Adjust for diversity
                do_sample=True,
            )

        # Decode the response
        response = tokenizer.decode(outputs[0], skip_special_tokens=True)

        # Extract only the assistant's response
        response = response.split("NexusAI:")[-1].strip()
        return response
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
