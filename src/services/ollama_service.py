# ollama_service.py

import requests

class OllamaService:
    """
    Encapsulates interactions with the Ollama API (local LLM).
    Allows sending a prompt and retrieving the model's response.
    """

    def __init__(self, model: str = "llama3:8b", api_url: str = "http://localhost:11411/api"):
        self.model = model
        self.api_url = api_url

    def ask(self, prompt: str) -> str:
        """
        Sends a prompt to the Ollama API and returns the model's response.
        """
        try:
            headers = {"Content-Type": "application/json"}
            data = {"model": self.model, "prompt": prompt}
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()

            # The API should return JSON with a 'response' field.
            json_resp = response.json()
            return json_resp.get("response", "No response available.")
        except Exception as e:
            return f"Error calling Ollama API: {e}"
