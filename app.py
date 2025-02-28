from flask import Flask, request, jsonify, Response, stream_with_context
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
RAPIDAPI_HOST = "social-download-all-in-one.p.rapidapi.com"
RAPIDAPI_URL = "https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"

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
    Endpoint to get the video URL.
    """
    try:
        video_url = request.form.get('url')
        if not video_url or not is_valid_url(video_url):
            logger.error("Invalid or missing URL")
            return jsonify({"error": "A valid URL is required"}), 400

        logger.info(f"Processing request for URL: {video_url}")

        headers = {
            "x-rapidapi-key": RAPIDAPI_KEY,
            "x-rapidapi-host": RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }
        payload = {"url": video_url}

        response = requests.post(RAPIDAPI_URL, json=payload, headers=headers)
        logger.info(f"RapidAPI response status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            logger.info(f"Full RapidAPI response: {data}")

            if "medias" in data and len(data["medias"]) > 0:
                media = data["medias"][0]
                if "url" in media:
                    return jsonify({
                        "status": "success",
                        "data": {
                            "video_url": media["url"]
                        }
                    }), 200
                else:
                    logger.error("No video URL found in the media item")
                    return jsonify({"error": "No video URL found in the media item", "response": data}), 404
            else:
                logger.error("No media found in RapidAPI response")
                return jsonify({"error": "No media found", "response": data}), 404
        else:
            logger.error(f"RapidAPI request failed: {response.status_code}")
            return jsonify({
                "error": "Failed to fetch data from RapidAPI",
                "status_code": response.status_code,
                "message": response.text
            }), response.status_code

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {str(e)}")
        return jsonify({"error": "Network error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

@app.route('/download-file', methods=['POST'])
def download_file():
    """
    Endpoint to stream the video file directly.
    """
    try:
        video_url = request.form.get('url')
        if not video_url or not is_valid_url(video_url):
            logger.error("Invalid or missing URL")
            return jsonify({"error": "A valid URL is required"}), 400

        # Stream the video file from the URL
        response = requests.get(video_url, stream=True)

        # Forward headers to allow the browser to download the file
        headers = {
            "Content-Disposition": f"attachment; filename=video.mp4",
            "Content-Type": response.headers.get("Content-Type", "video/mp4")
        }

        return Response(
            stream_with_context(response.iter_content(chunk_size=8192)),
            headers=headers,
            status=response.status_code
        )

    except requests.exceptions.RequestException as e:
        logger.error(f"Network error: {str(e)}")
        return jsonify({"error": "Network error occurred", "details": str(e)}), 500
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return jsonify({"error": "An unexpected error occurred", "details": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
