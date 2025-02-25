from flask import Flask, request, jsonify
from dotenv import load_dotenv
from urllib.parse import urlparse
import requests
import os
import logging
from flask_cors import CORS

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# RapidAPI credentials
RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")
RAPIDAPI_HOST = "instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com"
RAPIDAPI_URL = "https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/get-info-rapidapi"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Helper function to validate URLs
def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except:
        return False

@app.route('/download', methods=['POST'])
def download_media():
    """
    Endpoint to handle media download requests.
    """
    try:
        # Get the URL from the client request
        video_url = request.form.get('url')

        # Validate the URL
        if not video_url or not is_valid_url(video_url):
            logger.error("Invalid or missing URL")
            return jsonify({"error": "A valid URL is required"}), 400

        # Log the request
        logger.info(f"Processing request for URL: {video_url}")

        # Prepare the headers and query parameters for the RapidAPI request
        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST
        }
        querystring = {"url": video_url}

        # Make the request to RapidAPI
        response = requests.get(RAPIDAPI_URL, headers=headers, params=querystring)
        logger.info(f"RapidAPI response status: {response.status_code}")
        logger.info(f"RapidAPI response: {response.text}")

        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()

            # Extract the video URL from the RapidAPI response
            if "video" in data:
                return jsonify({
                    "status": "success",
                    "data": {
                        "video_url": data["video"]
                    }
                }), 200
            else:
                logger.error("No video URL found in RapidAPI response")
                return jsonify({"error": "No video URL found"}), 404
        else:
            logger.error(f"RapidAPI request failed: {response.status_code}")
            return jsonify({"error": "Failed to fetch data from RapidAPI", "status_code": response.status_code}), response.status_code

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {str(e)}")
        return jsonify({"error": "Network error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    # Run the app in production mode
    app.run(host='0.0.0.0', port=5000)
