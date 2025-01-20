# ui_controller.py

from typing import Dict
from domain.analysis_pipeline import AnalysisPipeline

class UIController:
    """
    A 'middleman' between the Gradio UI and  AnalysisPipeline.
    It holds references to any pipeline or services it needs.
    """

    def __init__(self, vt_api_key: str = None):
        """
        You can pass in any config you need, such as a VirusTotal API key.
        """
        self.pipeline = AnalysisPipeline(vt_api_key)

    def analyze_pdf_static(self, pdf_path: str) -> Dict:
        """
        Runs just the static PDF analysis (no VirusTotal, no LLM).
        """
        results = self.pipeline.analyze_file(
            file_path=pdf_path,
            file_type="pdf",
            run_vt=False,
            run_llm=False
        )
        return results

    def analyze_pdf_advanced(self, pdf_path: str) -> Dict:
        """
        Runs a more advanced analysis:
         - static PDF checks
         - plus VirusTotal
         - plus (optional) LLM if you like
        """
        results = self.pipeline.analyze_file(
            file_path=pdf_path,
            file_type="pdf",
            run_vt=True,   # Run VirusTotal
            run_llm=True  # Or True if you want LLM checks
        )
        return results

    def ask_llm_about_pdf(self, pdf_path: str, user_question: str) -> str:
        """
        Example method: merges static analysis results + user question,
        calls the LLM (via pipeline) to get a response.
        """
        # You might do something like:
        # 1) Re-run static analysis
        # 2) Build a prompt from analysis data + user_question
        # 3) Pipeline calls the LLM, returns string
        results = self.pipeline.analyze_file(
            file_path=pdf_path,
            file_type="pdf",
            run_vt=False,
            run_llm=True
        )

        # The pipeline might store the LLM response in results["ollama"]
        llm_text = results.get("ollama", "No LLM response found.")
        return llm_text
