
# PDF Analysis & LLM Integration

This repository demonstrates a **modular architecture** for analyzing PDF files using static analysis and optional external services (e.g., VirusTotal, Ollama LLM).

## Table of Contents

1. [Project Structure](#project-structure)  
2. [Installation](#installation)  
3. [Usage](#usage)  
4. [Configuration](#configuration)  
5. [Extending the Project](#extending-the-project)  
6. [License](#license)

---

## Project Structure

```
my_project/
├── domain/
│   ├── __init__.py
│   ├── base_analyzer.py        # Abstract base class (BaseAnalyzer)
│   ├── pdf_analyzer.py         # Concrete PDFAnalyzer for PDF files
│   ├── analyzer_factory.py     # Factory: returns correct analyzer by file type
│   └── analysis_pipeline.py    # Orchestrates analysis (static + optional services)
├── services/
│   ├── __init__.py
│   ├── virus_total_service.py  # VirusTotal API integration
│   └── ollama_service.py       # Ollama local LLM integration
├── ui/
│   ├── __init__.py
│   ├── ui_controller.py        # Controller between UI & pipeline
│   └── gradio_app.py           # Gradio-based front-end
├── requirements.txt
└── README.md
```

### Layer Breakdown

1. **Domain (`domain/`)**  
   - **`base_analyzer.py`**: Defines an abstract interface `BaseAnalyzer` for analyzing any file type.  
   - **`pdf_analyzer.py`**: Implements PDF-specific logic (extracting links, checking suspicious nodes).  
   - **`analyzer_factory.py`**: Chooses an analyzer class based on file type.  
   - **`analysis_pipeline.py`**: A “pipeline” that orchestrates static analysis and optional external checks (VirusTotal, LLM).

2. **Services (`services/`)**  
   - **`virus_total_service.py`**: Interacts with the VirusTotal API to upload files and retrieve scan reports.  
   - **`ollama_service.py`**: Interacts with a local Ollama server for LLM-based classification or summarization.

3. **UI (`ui/`)**  
   - **`ui_controller.py`**: Middleman that the front-end calls (e.g., `analyze_pdf_static()`, `analyze_pdf_advanced()`).  
   - **`gradio_app.py`**: A Gradio-based front-end that provides a file uploader, buttons, and a chat interface.

---

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/your-repo.git
cd your-repo
```

### 2. Create a Virtual Environment

```bash
python -m venv .venv
source .venv/bin/activate  # For Linux/Mac
# On Windows: .venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

Make sure the `requirements.txt` includes:

- `pdfalyzer`
- `PyPDF2`
- `requests`
- `gradio`
- etc.

If you don’t have a requirements file, manually install:

```bash
pip install pdfalyzer PyPDF2 requests gradio
```

---

## Usage

### 1. Go to the Project Root

Ensure you’re in the top-level directory (where `requirements.txt` and the `ui/`, `domain/`, `services/` folders exist).

### 2. Run the Gradio App

```bash
python ui/gradio_app.py
```

- This launches a local web server on `http://127.0.0.1:7860`.
- A browser tab may open automatically; if not, open it manually.

### 3. Upload a PDF

- Click the “Upload a PDF” box or drag-and-drop a file.
- Click the “Analyze PDF” button (or “Static Analysis” button) to see immediate results.

### 4. Advanced Analysis

- If you have a **VirusTotal API key** set, you can run advanced analysis (VirusTotal + LLM checks).  
- If you have an Ollama server running, you can ask LLM-based questions in the chat area.

---

## Configuration

### VirusTotal
- Obtain an API key from [VirusTotal](https://www.virustotal.com/).  
- Set it in your code or via environment variable. For instance:
  ```bash
  export VT_API_KEY="YOUR_KEY_HERE"
  ```

### Ollama (Local LLM)
- Install Ollama from [ollama.ai](https://ollama.ai/).  
- Ensure it’s running:
  ```bash
  ollama serve
  ```
- The `ollama_service.py` expects the default endpoint `http://localhost:11411/api` and a model like `"llama3:8b"`.

### Environment Variables
You can store secrets like `VT_API_KEY` in `.env` and use `python-dotenv`, or just export them in your shell.

---

## Extending the Project

1. **Add New File Types**  
   - Create `doc_analyzer.py` or `exe_analyzer.py` in `domain/`, subclassing `BaseAnalyzer`.  
   - Update `analyzer_factory.py` to return your new analyzer for “docx,” “exe,” etc.

2. **Custom Services**  
   - If you want to integrate a sandbox or different AI model, create a new file in `services/` and update `analysis_pipeline.py` accordingly.

3. **UI Enhancements**  
   - Customize `gradio_app.py` with additional buttons, text boxes, or forms.  
   - Connect them to new methods in `ui_controller.py`.

---

## License

[MIT License](https://opensource.org/licenses/MIT)

Feel free to modify and adapt this project to your specific needs. Pull requests and contributions are welcome if you have improvements or bug fixes!D