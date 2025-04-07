import requests

def scrape_github_metadata(username):
    url = f"https://api.github.com/users/{username}"
    headers = {"User-Agent": "ReconSpectre"}
    
    try:
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "username": username,
                "name": data.get("name"),
                "bio": data.get("bio"),
                "location": data.get("location"),
                "public_repos": data.get("public_repos"),
                "followers": data.get("followers"),
                "following": data.get("following"),
                "profile_image": data.get("avatar_url"),
                "profile_url": data.get("html_url"),
                "created_at": data.get("created_at")
            }
        elif response.status_code == 404:
            return {"error": "GitHub user not found"}
        else:
            return {"error": f"Unexpected error: {response.status_code}"}
    except requests.RequestException as e:
        return {"error": str(e)}
