import gradio as gr
from testOllama import (
    process_query_with_agent,
    process_query_with_online_agent,
    analyze_pdf,
    combine_analysis_and_query,
    process_pdf,
    MODEL,
    get_unique_links_from_pdf
)
from virusTotal import get_analysis

# We replicate the same global variables you had in the tkinter code,
# but we'll store them inside Gradio's state instead of actual global scope.
# This way the state will travel between function calls in the interface.

def select_pdf(pdf_file, state):
    """
    Handles uploading/choosing a PDF file.
    Once the file is selected, we analyze it and store results in the state.
    """
    if not pdf_file:
        return (
            state,
            [("System", "No file selected. Please upload a PDF file.")]
        )

    # The file object is a temporary file in Gradio; get its path:
    pdf_path = pdf_file.name
    state["pdf_path"] = pdf_path

    # Process PDF:
    pdf_analysis = process_pdf(pdf_path)
    total_v_short = get_analysis(pdf_path)
    total_v_full = get_analysis(pdf_path, short=False, full=True)

    # Save results in state
    state["pdf_analysis"] = pdf_analysis
    state["total_v_short"] = total_v_short
    state["total_v_full"] = total_v_full
    # Reset memory for a fresh PDF
    state["memory"] = {"path": pdf_path, "responses": []}

    return (
        state,
        [("System", f"PDF selected and analyzed: {pdf_path}")]
    )

def get_agent_analysis(state):
    """
    This replicates your get_agent_analysis() logic from the Tkinter code.
    It uses the already analyzed PDF (pdf_analysis, virus total data, etc.)
    and calls the LLM to see if the PDF is malicious.
    """
    pdf_path = state["pdf_path"]
    pdf_analysis = state["pdf_analysis"]
    total_v_short = state["total_v_short"]

    # Build the prompt from the PDF analysis
    prompt = pdf_analysis

    # Evaluate links inside the PDF
    links = get_unique_links_from_pdf(pdf_path)
    if len(links) > 0:
        prompt += "\n\nThe PDF contains some links. Here is their evaluation:\n"
    for link in links:
        link_evaluation = process_query_with_online_agent(
            f"is this link malicious?: {link}"
        )
        link_evaluation = f"Evaluation for link {link}: {link_evaluation}"
        prompt += f"\n{link_evaluation}"

    prompt += "\n\nVirus Total Analysis:\n" \
              "Be suspicious! If some of the VirusTotal reports point out it is malicious, " \
              "then assume it definitely is malicious. "
    prompt += total_v_short

    # Combine final user query (which is effectively "Is the PDF malicious?")
    final_prompt = combine_analysis_and_query(prompt, "Is the PDF malicious?")

    # Get response from local agent
    response = process_query_with_agent(final_prompt)
    state["memory"]["responses"].insert(0, response)
    return response

def analyze_pdf_btn(state, chat_history):
    """
    This function is called when the 'Analyze PDF' button is clicked.
    It calls get_agent_analysis and appends the result into the chat history.
    """
    if not state["pdf_path"]:
        chat_history.append(
            ("System", "Please upload a PDF file first.")
        )
        return state, chat_history

    response = get_agent_analysis(state)
    chat_history.append(
        ("System", response)
    )
    return state, chat_history

def get_response_from_chatbot(user_message, state, chat_history):
    """
    This replicates your get_response() logic from tkinter:
    - We combine the PDF analysis with the user's query.
    - We call the local agent and the online agent, then combine their answers.
    - We add everything to the chat history.
    """
    if not state["pdf_path"]:
        chat_history.append(
            ("User", user_message)
        )
        chat_history.append(
            ("System", "Error: PDF file is not selected.")
        )
        return state, chat_history

    # Add the user message to the chat
    chat_history.append(("User", user_message))

    # Prepare the prompt from PDF analysis and user input
    fprompt = combine_analysis_and_query(state["pdf_analysis"], user_message)
    pqwa_response = process_query_with_agent(fprompt)

    # Example call to the online agent (the same from your code)
    # This is a dummy prompt. Adjust as you see fit:
    pqwoa_response = process_query_with_online_agent(
        query_="go to https://en.wikipedia.org/wiki/Main_Page and tell me when did matthew perry die",
        model=MODEL
    )

    ans = (
        f"{pqwa_response}\n\n"
        "-------------------ONLINE-------------------\n"
        f"{pqwoa_response}"
    )

    # Insert the combined response at the top of memory
    state["memory"]["responses"].insert(0, ans)

    # Add the chatbot's response to history
    chat_history.append(("System", ans))

    return state, chat_history

#########################
# Build the Gradio UI
#########################

with gr.Blocks() as demo:
    # We'll keep track of everything in a single state dictionary
    # instead of separate global variables.
    # chat_history is a list of tuples (speaker, text).
    state = gr.State({
        "pdf_path": "",
        "pdf_analysis": "",
        "total_v_short": "",
        "total_v_full": "",
        "memory": {}
    })

    gr.Markdown("## Local PDF Analysis Chatbot\n"
                "1. **Upload a PDF** via the file uploader.\n"
                "2. Click **Analyze PDF** to check if it's malicious.\n"
                "3. Ask questions about the PDF.\n"
                "---")

    with gr.Row():
        pdf_input = gr.File(
            label="Upload a PDF",
            file_types=[".pdf"]
        )
        analyze_btn = gr.Button("Analyze PDF", variant="primary")

    # The Chatbot component to display conversation
    chat_display = gr.Chatbot(label="Chat History")

    # A textbox for user queries
    user_input = gr.Textbox(
        label="Type your question here and click 'Send'",
        placeholder="E.g. 'What does the PDF talk about?'"
    )
    send_btn = gr.Button("Send")

    # When a PDF is uploaded, we run `select_pdf`:
    pdf_input.upload(
        fn=select_pdf,
        inputs=[pdf_input, state],
        outputs=[state, chat_display]
    )

    # When "Analyze PDF" is clicked, we run `analyze_pdf_btn`:
    analyze_btn.click(
        fn=analyze_pdf_btn,
        inputs=[state, chat_display],
        outputs=[state, chat_display]
    )

    # When the user clicks "Send", we call get_response_from_chatbot:
    send_btn.click(
        fn=get_response_from_chatbot,
        inputs=[user_input, state, chat_display],
        outputs=[state, chat_display]
    )

demo.launch(server_name="0.0.0.0", server_port=7860)
