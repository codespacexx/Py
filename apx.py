import requests

# RapidAPI credentials
RAPIDAPI_KEY = "9c744b1e04msh43b2dea878f2e0ep196409jsn715043e55446"  # Replace with your RapidAPI key
RAPIDAPI_HOST = "all-media-downloader1.p.rapidapi.com"
RAPIDAPI_URL = "https://all-media-downloader1.p.rapidapi.com/all"

# Define the payload (video URL)
payload = {
    "url": "https://youtu.be/S-2oxLCkm2Y?si=6MxJkauRpophIVeN"  # Replace with a valid video URL
}

# Define headers
headers = {
    "x-rapidapi-key": RAPIDAPI_KEY,
    "x-rapidapi-host": RAPIDAPI_HOST,
    "Content-Type": "application/x-www-form-urlencoded"
}

try:
    # Send the POST request to RapidAPI
    response = requests.post(RAPIDAPI_URL, data=payload, headers=headers)

    # Print the response
    print("Status Code:", response.status_code)
    print("Response JSON:", response.json())

except requests.exceptions.RequestException as e:
    # Handle network errors
    print("Network error occurred:", str(e))
except Exception as e:
    # Handle other errors
    print("An unexpected error occurred:", str(e))
