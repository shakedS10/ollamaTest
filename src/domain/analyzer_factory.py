# analyzer_factory.py

from .pdf_analyzer import PDFAnalyzer
# from .doc_analyzer import DocAnalyzer  # (For future DOCX support)
# from .exe_analyzer import ExeAnalyzer  # (For future EXE support)
# ... add more imports if you create other analyzers

def get_analyzer(file_path: str, file_type: str):
    """
    Returns an instance of the appropriate analyzer subclass
    based on the file_type (e.g., 'pdf', 'doc', etc.).
    
    Currently only 'pdf' is supported.
    """
    file_type_lower = file_type.lower()
    
    if file_type_lower == "pdf":
        return PDFAnalyzer(file_path)
    # elif file_type_lower in ("doc", "docx"):
    #     return DocAnalyzer(file_path)
    # elif file_type_lower == "exe":
    #     return ExeAnalyzer(file_path)

    raise ValueError(f"Unsupported file type: {file_type}")
