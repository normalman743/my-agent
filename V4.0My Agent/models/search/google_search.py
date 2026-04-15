# models/search/google_search.py
import requests
from config.config import config

class GoogleSearch:
    def __init__(self):
        self.api_key = config['apis']['Google_Search_API']
        self.cx = config['apis']['SCE_ID']
        self.base_url = 'https://www.googleapis.com/customsearch/v1'

    def search(self, query):
        params = {
            'key': self.api_key,
            'cx': self.cx,
            'q': query
        }
        response = requests.get(self.base_url, params=params)
        if response.status_code == 200:
            results = response.json()
            # 处理搜索结果
            return results
        else:
            return f"Error: {response.status_code}"
