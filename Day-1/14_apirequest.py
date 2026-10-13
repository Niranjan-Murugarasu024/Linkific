import requests

url = "https://jsonplaceholder.typicode.com/posts"

try:
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    posts = response.json()

    print("Number of posts:", len(posts))

    for post in posts[:5]:
        print({
            "id": post["id"],
            "title": post["title"],
            "user_id": post["userId"],
        })

except requests.exceptions.Timeout:
    print("The API request timed out.")

except requests.exceptions.HTTPError as error:
    print(f"HTTP error: {error}")

except requests.exceptions.RequestException as error:
    print(f"Request failed: {error}")

except ValueError as error:
    print(f"Response was not valid JSON: {error}")