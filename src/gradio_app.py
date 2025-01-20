# gradio_app.py

import gradio as gr
from ui_controller import UIController

# Create a controller instance (provide your VirusTotal key if needed).
VT_API_KEY = "9ff3189a6bf3f6e6cc7c5aaee486d4808b3d7d1747bcf0b396182e755392cfc1"  # Or None if you don't have one
controller = UIController(vt_api_key=VT_API_KEY)


def select_pdf_action(pdf_file, state):
    """
    This function is triggered when a user uploads a PDF.
    We run a quick static analysis (no VirusTotal),
    then store the results in the Gradio state.
    """
    if not pdf_file:
        return state, [("System", "No file provided!")]

    pdf_path = pdf_file.name
    state["pdf_path"] = pdf_path

    # Perform static PDF analysis:
    analysis_results = controller.analyze_pdf_static(pdf_path)

    # Save results in state
    state["analysis"] = analysis_results

    # Add a message to chat history
    chat_msg = f"Static analysis complete for {pdf_path}"
    return state, [("System", chat_msg)]


def analyze_advanced_action(state, chat_history):
    """
    Runs a more advanced analysis (VirusTotal, etc.) on the PDF.
    """
    pdf_path = state.get("pdf_path", "")
    if not pdf_path:
        chat_history.append(("System", "Please upload a PDF first."))
        return state, chat_history

    advanced_results = controller.analyze_pdf_advanced(pdf_path)
    state["analysis"] = advanced_results

    chat_msg = f"Advanced analysis complete. Results:\n{advanced_results}"
    chat_history.append(("System", chat_msg))
    return state, chat_history


def ask_llm_action(user_question, state, chat_history):
    """
    Merges the user question with the PDF analysis, calls LLM, and appends the response.
    """
    pdf_path = state.get("pdf_path", "")
    if not pdf_path:
        chat_history.append(("User", user_question))
        chat_history.append(("System", "No PDF is loaded to analyze."))
        return state, chat_history

    chat_history.append(("User", user_question))
    llm_answer = controller.ask_llm_about_pdf(pdf_path, user_question)

    # Show the LLM's response
    chat_history.append(("System", llm_answer))
    return state, chat_history


##################################
# Build the Gradio interface
##################################
def build_app():
    with gr.Blocks() as demo:
        gr.Markdown("## PDF Analysis with VirusTotal & LLM (Gradio Demo)")

        # We store all necessary data in a shared dictionary 'state'
        state = gr.State({"pdf_path": "", "analysis": {}})

        with gr.Row():
            pdf_input = gr.File(label="Upload a PDF", file_types=[".pdf"])
            analyze_static_btn = gr.Button("Static Analysis")
            analyze_advanced_btn = gr.Button("Advanced Analysis")

        # Display a chatbot area to show messages
        chat_display = gr.Chatbot(label="Chat History")

        # A textbox for user to ask LLM questions about the PDF
        user_input = gr.Textbox(label="Ask the LLM about the PDF")
        send_btn = gr.Button("Send")

        # Link actions:
        # 1) When a PDF is uploaded, run select_pdf_action
        pdf_input.upload(fn=select_pdf_action, inputs=[pdf_input, state], outputs=[state, chat_display])

        # 2) When "Static Analysis" is clicked
        analyze_static_btn.click(fn=select_pdf_action, inputs=[pdf_input, state], outputs=[state, chat_display])

        # 3) When "Advanced Analysis" is clicked
        analyze_advanced_btn.click(fn=analyze_advanced_action, inputs=[state, chat_display], outputs=[state, chat_display])

        # 4) Send user query to LLM
        send_btn.click(fn=ask_llm_action, inputs=[user_input, state, chat_display], outputs=[state, chat_display])

    return demo


if __name__ == "__main__":
    demo = build_app()
    demo.launch(server_name="127.0.0.1", server_port=7860)
