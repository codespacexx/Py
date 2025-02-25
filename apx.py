import requests

url = "https://social-download-all-in-one.p.rapidapi.com/v1/social/autolink"

payload = { "url": "https://www.tiktok.com/@yeuphimzz/video/7237370304337628442" }
headers = {
	"x-rapidapi-key": "9c744b1e04msh43b2dea878f2e0ep196409jsn715043e55446",
	"x-rapidapi-host": "social-download-all-in-one.p.rapidapi.com",
	"Content-Type": "application/json"
}

response = requests.post(url, json=payload, headers=headers)

print(response.json())
