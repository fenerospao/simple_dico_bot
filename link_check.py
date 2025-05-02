import re
import requests

def check_youtube_link(link):
    regex = re.compile(
        r'(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)'
    )
    if not regex.match(link):
        return False

    oembed_url = f"https://www.youtube.com/oembed?url={link}&format=json"
    try:
        response = requests.get(oembed_url, timeout=5)
        return response.status_code == 200
    except requests.RequestException:
        return False
