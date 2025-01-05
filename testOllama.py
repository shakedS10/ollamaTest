

import json
from pdfalyzer.decorators.pdf_tree_node import PdfTreeNode
from yaralyzer import *
from pdfalyzer import *
import requests  # For Ollama API interactions
import llm_axe
from llm_axe import OnlineAgent, OllamaChat, Agent
import ollama

YaralyzerConfig.set_default_args()


def analyze_pdf(pdf_path):
    """
    Analyzes a PDF using Pdfalyzer and returns results as a dictionary,
    focusing on overall analytics to assess safety.
    """
    pdfalyzer1 = Pdfalyzer(pdf_path)
    actual_pdf_tree: PdfTreeNode = pdfalyzer1.pdf_tree

    # Print the PDF tree
    PdfalyzerPresenter(pdfalyzer1).print_rich_table_tree()

    results = {"nodes": [], "is_safe": True}

    for node in pdfalyzer1.node_iterator():
        node_info = {"type": node.sub_type, "details": str(node.obj)}
        results["nodes"].append(node_info)

        # Check for suspicious nodes (add more conditions as needed)
        if node.sub_type in ["/JavaScript", "/Launch", "/EmbeddedFile"]:
            results["is_safe"] = False

    return results


def ask_ollama(prompt, model="default", api_url="http://localhost:11411/api"):
    """
    Sends a prompt to Ollama's API and retrieves the response.
    """
    headers = {"Content-Type": "application/json"}
    data = {"model": model, "prompt": prompt}
    response = requests.post(api_url, headers=headers, json=data)
    if response.status_code == 200:
        return response.json().get("response", "No response")
    else:
        return f"Error: {response.status_code} - {response.text}"


def process_pdf_and_query(pdf_path, query):
    """
    Combines PDF analysis and querying Ollama for insights based on the analysis results.
    """
    # Analyze the PDF
    print("Analyzing the PDF...")
    analysis_results = analyze_pdf(pdf_path)

    # Save results to JSON for clarity
    results_path = f"{pdf_path}.json"
    with open(results_path, "w") as file:
        json.dump(analysis_results, file, indent=4)
    print(f"Analysis results saved to {results_path}.")

    # Prepare a summary for Ollama
    safety_status = "safe" if analysis_results["is_safe"] else "unsafe"
    summary = f"The PDF analysis indicates that the document is {safety_status}."
    ollama_prompt = f"The following is the analysis of a PDF:\n\n{json.dumps(analysis_results, indent=2)}\n\n{query} "
    
    return ollama_prompt


def process_query_with_agent(query, model="llama3.2:1b"):
    """
    Processes a query using the OnlineAgent and returns the response.
    """
    try:
        # Return the response from the OnlineAgent
        llm = OllamaChat(model=model)  # Create an Ollama chat instance
        agent = Agent(llm, custom_system_prompt="read the analysis provided in json data and answer the question")
        response = agent.ask(query)

        return response
    except Exception as e:
        return f"Error processing with OnlineAgent: {e}"

def process_query_with_online_agent(query, model="llama3.2:1b"):
    """
    Processes a query using the OnlineAgent and returns the response.
    """
    try:
        llm = OllamaChat(model=model)  # Create an Ollama chat instance
        searcher = OnlineAgent(llm)  # Create an OnlineAgent instance
        response = searcher.search(query)  # Perform the search

        # Return the response from the OnlineAgent
        return response
    except Exception as e:
        return f"Error processing with OnlineAgent: {e}"

# Example usage
if __name__ == "__main__":
    pdf_path = "B.pdf"  # Replace with the actual PDF path
    query = "in the json object you received show all the nodes that are of type /link and provide a summary of the document" 
    fprompt = process_pdf_and_query(pdf_path, query)
    print(process_query_with_agent(fprompt))
    print(process_query_with_online_agent("go to https://en.wikipedia.org/wiki/Main_Page and tell me when did matthew perry die"))
