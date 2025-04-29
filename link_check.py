import re
import requests

def check_youtube_link(link):

    rex_link = re.compile(r'(https?:\/\/)?(www\.)?(youtube\.com|youtu\.be)')

    res = rex_link.search(link)

    if(res==None):
        return False
    
    oembed_url = f"https://www.youtube.com/oembed?url={link}&format=json"
    response = requests.get(oembed_url)

    return response.status_code == 200
