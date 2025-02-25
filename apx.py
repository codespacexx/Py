import requests

url = "https://all-media-downloader1.p.rapidapi.com/all"

payload = { "url": "https://youtu.be/S-2oxLCkm2Y?si=6MxJkauRpophIVeN" }
headers = {
    "x-rapidapi-key": "9c744b1e04msh43b2dea878f2e0ep196409jsn715043e55446",
    "x-rapidapi-host": "all-media-downloader1.p.rapidapi.com",
    "Content-Type": "application/x-www-form-urlencoded"
}

try:
    response = requests.post(url, data=payload, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors
    data = response.json()
    print("RapidAPI Response:", data)
except requests.exceptions.RequestException as e:
    print("Error making request to RapidAPI:", e)
