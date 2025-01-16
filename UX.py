import tkinter as tk
from tkinter import ttk, scrolledtext, filedialog
from testOllama import process_query_with_agent, process_query_with_online_agent, analyze_pdf, \
    combine_analysis_and_query, process_pdf, MODEL
from virusTotal import get_analysis

# Define global colors
light_gray = "#D3D3D3"
derk_blue = "#2c3e50"
BG_COLOR = derk_blue  # Background color of the window
CHAT_BG_COLOR = light_gray  # Background color of the chat window
CHAT_TEXT_COLOR = derk_blue  # Text color in the chat window
INPUT_BOX_BG = light_gray  # Background color of the input box
INPUT_BOX_TEXT = derk_blue  # Text color of the input box
BUTTON_BG = light_gray  # Background color of the send button
BUTTON_TEXT = "black"  # Text color of the send button
BUTTON_ACTIVE_BG = "black"  # Active (hover) background color of the send button
BUTTON_ACTIVE_TEXT = "white"  # Active (hover) text color of the send button
HEADER_BG = "#34495e"  # Background color of the header
HEADER_TEXT = "white"  # Text color of the header
FOOTER_BG = "black"  # Background color of the footer
FOOTER_TEXT = "white"  # Text color of the footer

# Define global sizes and locations
WINDOW_WIDTH = 1000  # Width of the main window
WINDOW_HEIGHT = 600  # Height of the main window
CHAT_WINDOW_HEIGHT = 25  # Height of the chat window
CHAT_WINDOW_WIDTH = 70  # Width of the chat window
INPUT_BOX_WIDTH = 52  # Width of the input box
BUTTON_FONT_SIZE = 14  # Font size for the button
HEADER_FONT_SIZE = 16  # Font size for the header
FOOTER_FONT_SIZE = 10  # Font size for the footer
PADDING_X = 10  # Horizontal padding
PADDING_Y = 10  # Vertical padding

pdf_path = ""  # Initialize pdf_path as empty
pdf_analysis = ""
total_v_short = ""
total_v_full = ""
memory = {}


# Function to open file dialog and select PDF
def select_pdf():
    global pdf_path, memory
    pdf_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    if pdf_path:  # If the user selects a file
        # Proceed with PDF analysis
        print(f"PDF selected: {pdf_path}")
        memory = {"path": pdf_path,
                  "responses": []}  # delete the memory when start working on a new PDF
        get_pdf_data()


    else:
        print("No file selected.")


def get_pdf_data():
    global pdf_path, pdf_analysis, total_v_short, total_v_full, memory
    pdf_analysis = process_pdf(pdf_path)
    total_v_short = get_analysis(pdf_path)
    total_v_full = get_analysis(pdf_path, short=False, full=True)


def get_agent_analysis():
    prompt = pdf_analysis + "\n\nVirus Total Analysis" + total_v_short
    prompt = combine_analysis_and_query(prompt, "Is the PDF malicious?")
    response = process_query_with_agent(prompt)
    memory["responses"].insert(0, response)
    return response


# Chatbot logic (replace with your chatbot logic)
def get_response(user_message):
    global memory
    if pdf_path:  # Ensure the PDF path is not empty
        fprompt = combine_analysis_and_query(pdf_analysis, user_message)
        pqwa_response = process_query_with_agent(fprompt)
        pqwoa_response = process_query_with_online_agent(
            query_=" go to https://en.wikipedia.org/wiki/Main_Page and tell me when did matthew perry die", model=MODEL)
        ans = f"{pqwa_response} \n\n -------------------------ONLINE----------------------- \n {pqwoa_response}"
        memory["responses"].insert(0, ans)
        return ans
    else:
        return "Error: PDF file is not selected."


def get_analysis_btn():
    print("getting analysis....")
    if pdf_path != "":
        send_message(to_analyze=True)
    else:
        chat_window.insert(tk.END, "Chatbot: ", "bold")
        chat_window.insert(tk.END, f"Please upload a PDF file first\n")


# Function to handle sending messages
def send_message(to_analyze=False):
    user_message = input_box.get()
    if user_message.strip() or to_analyze:  # Ensure the input isn't empty
        # Insert "You:" in bold
        chat_window.insert(tk.END, "You: ", "bold")
        # Insert the user's message
        chat_window.insert(tk.END, f"{user_message}\n")

        # Get chatbot response
        if to_analyze:
            chatbot_response = get_agent_analysis()
        else:
            chatbot_response = get_response(user_message)

            # Insert "Chatbot:" (non-bold, default style)
        chat_window.insert(tk.END, "Chatbot: ", "bold")
        # Insert the chatbot's response
        chat_window.insert(tk.END, f"{chatbot_response}\n")

        # Auto-scroll to the bottom
        chat_window.see(tk.END)

    # Clear the input box
    input_box.delete(0, tk.END)


# Create main window
root = tk.Tk()
root.title("Local Chatbot")
root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
root.configure(bg=BG_COLOR)

# Header
header = tk.Label(root, text="Welcome! Please upload a PDF to review", font=("Arial", HEADER_FONT_SIZE, "bold"),
                  bg=HEADER_BG,
                  fg=HEADER_TEXT)
header.pack(fill=tk.X, pady=PADDING_Y)

# Add a button to select PDF file before chat
select_pdf_button = tk.Button(root, text="Select PDF", command=select_pdf, bg=BUTTON_BG, fg=BUTTON_TEXT,
                              font=("Arial", BUTTON_FONT_SIZE),
                              activebackground=BUTTON_ACTIVE_BG, activeforeground=BUTTON_ACTIVE_TEXT)
select_pdf_button.pack(pady=PADDING_Y)
select_pdf_button.place(x=10, y=550)

# Add a button for running analysis
analyze_button = tk.Button(
    root,
    text="Analyze PDF",
    command=get_analysis_btn,  # Function to call when button is clicked
    bg=BUTTON_BG,
    fg=BUTTON_TEXT,
    font=("Arial", BUTTON_FONT_SIZE),
    activebackground=BUTTON_ACTIVE_BG,
    activeforeground=BUTTON_ACTIVE_TEXT
)
# Place the button in the desired position
analyze_button.pack(pady=PADDING_Y)
analyze_button.place(x=10, y=480)  # Adjust position as needed

# Configure Scrollbar Style (change colors)
style = ttk.Style()
style.configure("TScrollbar",
                gripcount=0,
                background="gray",  # Set the background color of the scrollbar
                troughcolor="lightgray",  # Set the trough color (the background of the scrollbar track)
                width=15)  # Adjust the width of the scrollbar

# Chat window (scrollable)
chat_window = scrolledtext.ScrolledText(
    root,
    wrap=tk.WORD,
    state="normal",
    height=CHAT_WINDOW_HEIGHT,
    width=CHAT_WINDOW_WIDTH,
    bg=CHAT_BG_COLOR,
    fg=CHAT_TEXT_COLOR,
    font=("Arial", 12)
)
chat_window.pack(pady=PADDING_Y, padx=PADDING_X)

# Configure text tags for styling
chat_window.tag_config("bold", font=("Arial", 12, "bold"))  # Bold style for "You:"
chat_window.tag_config("normal", font=("Arial", 12))  # Normal style for other text

# Separator
separator = ttk.Separator(root, orient="horizontal")
separator.pack(fill="x", pady=5)

# Input box and send button
frame = tk.Frame(root, bg=BG_COLOR)
input_box = tk.Entry(frame, width=INPUT_BOX_WIDTH, font=("Arial", 14), bg=INPUT_BOX_BG, fg=INPUT_BOX_TEXT)
input_box.pack(side=tk.LEFT, padx=5, pady=5)
send_button = tk.Button(
    frame,
    text="Send",
    command=send_message,
    bg=BUTTON_BG,
    fg=BUTTON_TEXT,
    font=("Arial", BUTTON_FONT_SIZE),
    activebackground=BUTTON_ACTIVE_BG,
    activeforeground=BUTTON_ACTIVE_TEXT
)
send_button.pack(side=tk.RIGHT, padx=5, pady=5)
frame.pack(pady=PADDING_Y)

# Footer
footer = tk.Label(root, text="Type a message and press Enter or click Send", font=("Arial", FOOTER_FONT_SIZE),
                  bg=FOOTER_BG, fg=FOOTER_TEXT)
footer.pack(fill=tk.X, side=tk.BOTTOM)

# Bind Enter key
root.bind("<Return>", lambda event: send_message())

# curser
root.config(cursor="arrow")  # Set the default cursor for the window
input_box.config(cursor="xterm")  # Set the cursor to I-beam (text cursor) for the input box
chat_window.config(cursor="arrow")  # Set a visible cursor type for the chat window
send_button.config(cursor="hand2")
select_pdf_button.config(cursor="hand2")
analyze_button.config(cursor="hand2")

# Run the application
if __name__ == "__main__":
    root.mainloop()
