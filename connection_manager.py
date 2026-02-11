import os
import requests
from dotenv import load_dotenv

load_dotenv()

class MondayManager:
    _instance = None
    URL = "https://api.monday.com/v2"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(MondayManager, cls).__new__(cls)
            cls._instance._headers = None
            cls._instance.is_connected = False
        return cls._instance

    def connect(self):
        """Establishes connection to Monday.com and validates API Key."""
        api_key = os.getenv("MONDAY_API_KEY")
        
        if not api_key:
            return False, "API Key not found in .env file."
        
        self._headers = {
            "Authorization": api_key,
            "API-Version": "2023-10"
        }
        
        # Simple query to validate token
        query = "query { me { name } }"
        
        try:
            response = requests.post(self.URL, json={"query": query}, headers=self._headers)
            data = response.json()
            
            if "errors" in data:
                return False, f"Auth Error: {data['errors'][0]['message']}"
            
            if "data" in data and "me" in data["data"]:
                user_name = data["data"]["me"]["name"]
                self.is_connected = True
                return True, f"Connected as {user_name}"
            
            return False, "Unknown connection error."
                
        except Exception as e:
            return False, f"Connection Error: {str(e)}"

    def execute_query(self, query):
        """Executes a GraphQL query securely."""
        if not self.is_connected:
            self.connect()
            
        if not self._headers:
             raise Exception("Not connected to Monday.com")

        response = requests.post(self.URL, json={"query": query}, headers=self._headers)
        
        if response.status_code != 200:
             raise Exception(f"HTTP Error {response.status_code}: {response.text}")
             
        return response.json()

monday_manager = MondayManager()