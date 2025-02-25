import requests

url = "https://instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com/get-info-rapidapi"

querystring = {"url":"https://www.instagram.com/reel/C1U6tQLu1vv/"}

headers = {
	"x-rapidapi-key": "9c744b1e04msh43b2dea878f2e0ep196409jsn715043e55446",
	"x-rapidapi-host": "instagram-downloader-download-instagram-videos-stories1.p.rapidapi.com"
}

response = requests.get(url, headers=headers, params=querystring)

print(response.json())
