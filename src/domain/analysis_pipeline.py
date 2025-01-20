# analysis_pipeline.py

from typing import Dict, Optional

# Domain
from .analyzer_factory import get_analyzer

from services.virus_total_service import VirusTotalService
from services.ollama_service import OllamaService


class AnalysisPipeline:
    """
    High-level orchestrator that:
      1) Identifies the correct file analyzer from the factory (e.g., PDFAnalyzer).
      2) Performs static analysis (safe/unsafe, suspicious objects, etc.).
      3) Optionally integrates extra steps like VirusTotal, LLM checks.
      4) Returns a final consolidated results dictionary.
    """

    def __init__(self,
                 vt_api_key: Optional[str] = None,
                 ollama_model: str = "llama3:8b"):
        """
        :param vt_api_key: (Optional) VirusTotal API key. If None, VirusTotal steps will be skipped unless handled differently.
        :param ollama_model: Name of the Ollama model (e.g., "llama3:8b")
        """
        self.vt_api_key = vt_api_key
        self.ollama_model = ollama_model

        # Create service instances only if you want them available by default
        self.virus_total_service = (VirusTotalService(api_key=vt_api_key)
                                    if vt_api_key else None)
        self.ollama_service = OllamaService(model=ollama_model)

    def analyze_file(self,
                     file_path: str,
                     file_type: str,
                     run_vt: bool = False,
                     run_llm: bool = False) -> Dict:
        """
        Orchestrates the entire analysis flow:
          - 1) Gets the right analyzer from the factory
          - 2) Runs static analysis
          - 3) (Optional) runs VirusTotal checks
          - 4) (Optional) runs LLM-based analysis
          - 5) Returns final dictionary with all combined info

        :param file_path: The path to the file (e.g., PDF)
        :param file_type: "pdf", "docx", "exe", etc. (for the factory)
        :param run_vt: If True, call VirusTotal
        :param run_llm: If True, generate an LLM-based summary or classification
        :return: A dictionary that aggregates static analysis + optional external checks
        """

        # ==================
        # 1) Static Analysis
        # ==================
        analyzer = get_analyzer(file_path, file_type)
        analyzer.analyze()
        static_results = analyzer.get_results()  # e.g., { "is_safe": bool, "nodes": [...], "links": [...] }

        # Store all results in a final dict
        final_results = {
            "file_path": file_path,
            "file_type": file_type,
            "analysis": static_results
        }

        # ============================
        # 2) Optional VirusTotal Scan
        # ============================
        if run_vt and self.virus_total_service:
            vt_data = self.run_virus_total(file_path)
            final_results["virus_total"] = vt_data
        elif run_vt and not self.virus_total_service:
            final_results["virus_total"] = {
                "error": "No VT API key set, but run_vt=True"
            }

        # =====================
        # 3) Optional LLM Check
        # =====================
        if run_llm:
            llm_data = self.run_llm_check(static_results)
            final_results["ollama"] = llm_data

        return final_results

    def run_virus_total(self, file_path: str) -> Dict:
        """
        Calls the VirusTotal service to upload and retrieve the scan report.
        Returns a dictionary with short_report, full_report, etc.
        """
        try:
            # You can adjust the arguments (short=True, full=False) as needed.
            vt_result = self.virus_total_service.analyze_file(
                file_path=file_path,
                short=True,
                full=False
            )
            return vt_result
        except Exception as e:
            return {"error": f"VirusTotal failed: {e}"}

    def run_llm_check(self, static_results: Dict) -> Dict:
        """
        Calls the OllamaService to do an LLM-based check or classification.

        :param static_results: The dictionary from static analysis (e.g. suspicious nodes).
        :return: A dict with the LLM response or error.
        """
        try:
            # Build a prompt from the static analysis data
            # For example:
            prompt = (
                f"Analysis data:\n{static_results}\n\n"
                "Determine if this file might be malicious or suspicious.\n"
                "Explain your reasoning."
            )
            response_text = self.ollama_service.ask(prompt)
            return {"response": response_text}
        except Exception as e:
            return {"error": f"LLM check failed: {e}"}
