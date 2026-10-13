import requests


def get_data(url):
    response = requests.get(url, timeout=15)
    response.raise_for_status()
    return response.json()