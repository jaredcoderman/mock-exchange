import requests
import os
import json
from dotenv import load_dotenv

async def make_request():
  response = requests.get(url, headers=headers)

class Database:
    def __init__(self):
        self.url = "https://api.jsonbin.io/v3/b/6430d9c8c0e7653a059fe6c5"
        self.master_key = os.getenv("X-MASTER-KEY")
        self.access_key = os.getenv("X-ACCESS-KEY")

    def get_data(self):
        headers = {
            "X-Master-Key": self.master_key,
            "X-Access-Key": self.access_key
        }
        response = requests.get(self.url, headers=headers)
        return json.loads(response.text)

    def update_data(self, data):
        headers = {
            "X-Master-Key": self.master_key,
            "X-Access-Key": self.access_key,
            "Content-Type": "application/json"
        }
        response = requests.put(self.url, headers=headers, data=data)

    