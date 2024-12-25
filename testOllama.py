# import ollama
# desiredmodel = 'llama3.2:1b'
# question = 'What is the capital of France?'

# response = ollama.chat(desiredmodel, messages=[{
#     'role': 'user',
#     'content': question,
# }])

# ollamaResponse = response['message']['content']
# print(ollamaResponse)
# import llm_axe
# import ollama
# import requests
# from bs4 import BeautifulSoup
# import re
# import PyPDF2

# # Function to extract text from PDF
# def extract_text_from_pdf(pdf_path):
#     text = ""
#     with open(pdf_path, 'rb') as file:
#         reader = PyPDF2.PdfReader(file)
#         for page in reader.pages:
#             text += page.extract_text()
#     return text

# # Function to fetch and parse content from URL
# def fetch_and_parse_url_content(url):
#     try:
#         response = requests.get(url, timeout=10)  # Timeout after 10 seconds
#         response.raise_for_status()  # Check for request errors
#         return response.text
#     except requests.RequestException as e:
#         return f"Error fetching URL content: {e}"

# # Function to extract URLs from the text
# def extract_urls_from_text(text):
#     url_pattern = r'(https?://[^\s]+)'  # Matches URLs starting with http or https
#     return re.findall(url_pattern, text)

# # Function to analyze model response with llm_axe Searcher
# def analyze_with_llm_axe_searcher(response_text):
#     searcher = llm_axe.Searcher()  # Create an instance of Searcher
#     analysis_result = searcher.search(response_text)  # Search for issues or patterns
#     return analysis_result

# # Function to process URL content with Ollama
# def process_url_with_ollama(url, question, model):
#     # Step 1: Fetch and parse URL content
#     url_content = fetch_and_parse_url_content(url)
#     if "Error" in url_content:
#         return f"Error fetching URL content: {url_content}"
    
#     # Step 2: Extract meaningful content (like text from paragraphs)
#     soup = BeautifulSoup(url_content, "html.parser")
#     paragraphs = soup.find_all('p')
#     text_content = "\n".join([p.get_text() for p in paragraphs if p.get_text()])
    
#     # Step 3: Ask the model to analyze the content
#     url_question = f"Analyze the following content fetched from {url} and {question}:\n\n{text_content[:1000]}"
#     try:
#         response = ollama.chat(model, messages=[{
#             'role': 'user',
#             'content': url_question,
#         }])
#         model_response = response['message']['content']
        
#         # Analyze the model's response with llm_axe's Searcher
#         axe_analysis = analyze_with_llm_axe_searcher(model_response)
#         return f"Model Response:\n{model_response}\n\nLLM Axe Searcher Analysis:\n{axe_analysis}"
    
#     except Exception as e:
#         return f"Error analyzing content with Ollama: {e}"

# # Function to process PDF content with Ollama and allow interactive Q&A
# def process_pdf_with_ollama_and_searcher(pdf_path, model):
#     while True:
#         # Extract text and URLs from the PDF
#         pdf_text = extract_text_from_pdf(pdf_path)
#         if not pdf_text.strip():
#             print("No readable text found in the PDF.")
#             continue
        
#         # Extract URLs from the text of the PDF
#         urls = extract_urls_from_text(pdf_text)
#         if urls:
#             print("Found the following URLs in the PDF:")
#             for idx, url in enumerate(urls):
#                 print(f"{idx + 1}. {url}")
        
#         # Ask for a question to ask the model about the PDF or URLs
#         question = input("Enter the question you want to ask (or type 'exit' to quit): ")
#         if question.lower() == 'exit':
#             print("Exiting program.")
#             break
        
#         # Process the URLs found in the PDF
#         if question.lower().startswith("url") and urls:
#             url_content_analysis = "URL Analysis:\n"
#             for url in urls:
#                 # Process the URL with Ollama and analyze using llm_axe's Searcher
#                 analysis = process_url_with_ollama(url, question, model)
#                 url_content_analysis += f"\nURL: {url}\nAnalysis: {analysis}\n"
#             print(url_content_analysis)
#         else:
#             # Process the PDF text content
#             pdf_question = f"Analyze the following content from the PDF and {question}:\n\n{pdf_text[:1000]}"
#             try:
#                 response = ollama.chat(model, messages=[{
#                     'role': 'user',
#                     'content': pdf_question,
#                 }])
#                 pdf_analysis = response['message']['content']
                
#                 # Analyze the model's response with llm_axe's Searcher
#                 axe_analysis = analyze_with_llm_axe_searcher(pdf_analysis)
#                 print(f"Model Response:\n{pdf_analysis}\n\nLLM Axe Searcher Analysis:\n{axe_analysis}")
#             except Exception as e:
#                 print(f"Error processing with Ollama: {e}")
        
#         # Ask if the user wants to continue
#         continue_prompt = input("\nDo you want to ask something else? (yes/no): ")
#         if continue_prompt.lower() != 'yes':
#             print("Exiting program.")
#             break

# # Example usage
# pdf_path = "https.pdf"  # Path to your PDF file
# desired_model = "llama3.2:1b"

# # Start the interactive loop
# process_pdf_with_ollama_and_searcher(pdf_path, desired_model)
import ollama
from llm_axe import OnlineAgent, OllamaChat
import PyPDF2
import re

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        for page in reader.pages:
            text += page.extract_text()
    return text

# Function to extract URLs from the text
def extract_urls_from_text(text):
    url_pattern = r'(https?://[^\s]+)'  # Matches URLs starting with http or https
    return re.findall(url_pattern, text)

# Function to process URL content with OnlineAgent and Ollama
def process_url_with_online_agent(url, prompt, model):
    try:
        llm = OllamaChat(model=model)  # Create an Ollama chat instance
        searcher = OnlineAgent(llm)  # Create an OnlineAgent instance
        full_prompt = f"{prompt} {url}"  # Combine the prompt with the URL
        response = searcher.search(full_prompt)  # Perform the search

        # Return the response from the OnlineAgent
        return response
    except Exception as e:
        return f"Error processing with OnlineAgent: {e}"

# Function to process PDF content and allow interactive Q&A
def process_pdf_with_ollama(pdf_path, model):
    while True:
        # Extract text and URLs from the PDF
        pdf_text = extract_text_from_pdf(pdf_path)
        if not pdf_text.strip():
            print("No readable text found in the PDF.")
            continue
        
        # Extract URLs from the text of the PDF
        urls = extract_urls_from_text(pdf_text)
        if urls:
            print("Found the following URLs in the PDF:")
            for idx, url in enumerate(urls):
                print(f"{idx + 1}. {url}")
        else:
            print("No URLs found in the PDF.")
        
        # Ask for a question to ask the model about the PDF or URLs
        question = input("Enter the question you want to ask (or type 'exit' to quit): ")
        if question.lower() == 'exit':
            print("Exiting program.")
            break
        
    # If the question is about a specific URL
        # Let the user choose the URL
        url_index = int(input(f"Which URL would you like to ask about (1-{len(urls)})? "))
        if 1 <= url_index <= len(urls):
            selected_url = urls[url_index - 1]
            url_content_analysis = process_url_with_online_agent(selected_url, question, model)
            print(f"URL Analysis for {selected_url}:\n{url_content_analysis}")
        else:
            print("Invalid URL selection.")
        # Ask if the user wants to continue
        continue_prompt = input("\nDo you want to ask something else? (yes/no): ")
        if continue_prompt.lower() != 'yes':
            print("Exiting program.")
            break

# Example usage
pdf_path = "wee.pdf"  # Path to your PDF file
desired_model = "llama3.2:1b"  # Model for OnlineAgent

# Start the interactive loop
process_pdf_with_ollama(pdf_path, desired_model)
