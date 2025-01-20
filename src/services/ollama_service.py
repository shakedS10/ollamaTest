# ollama_service.py

import requests
import ast
import json
import time

from pdfalyzer.decorators.pdf_tree_node import PdfTreeNode
from yaralyzer import *
from pdfalyzer import *
import requests  # For Ollama API interactions
import llm_axe
from llm_axe import OnlineAgent, OllamaChat, Agent
import ollama

MODEL = "llama3:8b"
class OllamaService:
    """
    Encapsulates interactions with the Ollama API (local LLM).
    Allows sending a prompt and retrieving the model's response.
    """

    def __init__(self, model: str = "llama3:8b", api_url: str = "http://localhost:11411/api"):
        self.model = model
        self.api_url = api_url

    def process_query_with_agent(query, model=MODEL):
        """
        Processes a query using the OnlineAgent and returns the response.
        """
        try:
            # Return the response from the OnlineAgent
            llm = OllamaChat(model=model)  # Create an Ollama chat instance
            agent = Agent(llm, custom_system_prompt="read the analysis provided and answer the question")
            response = agent.ask(query)

            return response
        except Exception as e:
            return f"Error processing with OnlineAgent: {e}"

    def process_query_with_online_agent(query_, model=MODEL):
        """
        Processes a query using the OnlineAgent and returns the response.
        """
        try:
            llm = OllamaChat(model=model)  # Create an Ollama chat instance
            searcher = OnlineAgent(llm)  # Create an OnlineAgent instance
            response = searcher.search(query_)  # Perform the search
            if response is None:
                return "No results found from the search."
            return response
        except Exception as e:
            return f"Error processing with OnlineAgent: {e}"
