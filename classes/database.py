import requests
import os
import json
from dotenv import load_dotenv

class Database:
    def __init__(self):
        get_url = lambda testing: "https://api.jsonbin.io/v3/b/643d7ea6ace6f33a220d18cc" if testing else "https://api.jsonbin.io/v3/b/6430d9c8c0e7653a059fe6c5"
        self.url = get_url(True)
        self.master_key = os.getenv("X-MASTER-KEY")
        self.access_key = os.getenv("X-ACCESS-KEY")
        self.data = {}

    def init_data(self):
        headers = {
            "X-Master-Key": self.master_key,
            "X-Access-Key": self.access_key
        }
        response = requests.get(self.url, headers=headers)
        self.data = json.loads(response.text)

    def get_data(self):
        return self.data

    def get_record(self):
        return self.data["record"]

    def get_saved_stock_prices(self):
        return self.data["record"]["stock_prices"]

    def update_data(self, data: str):
        headers = {
            "X-Master-Key": self.master_key,
            "X-Access-Key": self.access_key,
            "Content-Type": "application/json"
        }
        requests.put(self.url, headers=headers, data=data)

    