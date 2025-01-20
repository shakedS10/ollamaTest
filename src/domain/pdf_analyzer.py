# pdf_analyzer.py
from typing import Dict
from PyPDF2 import PdfReader

# Imports from your pdfalyzer library
from pdfalyzer import Pdfalyzer, PdfalyzerPresenter
from pdfalyzer.decorators.pdf_tree_node import PdfTreeNode

from .base_analyzer import BaseAnalyzer

class PDFAnalyzer(BaseAnalyzer):
    """
    Concrete implementation for analyzing PDF files using Pdfalyzer, PyPDF2, etc.
    """

    def analyze(self):
        """
        Analyze the PDF file and populate self.analysis_results.
        - Uses Pdfalyzer to parse the internal structure.
        - Checks for suspicious nodes (JavaScript, EmbeddedFile, etc.).
        - Also supports link extraction via PyPDF2.
        """
        try:
            pdfalyzer_instance = Pdfalyzer(self.file_path)
            pdf_tree = pdfalyzer_instance.pdf_tree

            # (Optional) If you want to visualize the structure in console
            PdfalyzerPresenter(pdfalyzer_instance).print_rich_table_tree()

            # Basic structure for storing results
            pdf_report = {
                "file_path": self.file_path,
                "nodes": [],
                "is_safe": True,
                "links": [] # todo: no duplicates!
            }

            # 1) Check internal nodes for malicious content
            for node in pdfalyzer_instance.node_iterator():
                node_details = {
                    "type": node.sub_type,
                    "object_str": str(node.obj)
                }
                pdf_report["nodes"].append(node_details)

                # Example heuristic:
                if node.sub_type in ["/JavaScript", "/Launch", "/EmbeddedFile"]:
                    pdf_report["is_safe"] = False

            # 2) Extract external links using PyPDF2
            extracted_links = self._extract_pdf_links()
            pdf_report["links"].extend(extracted_links)

            # Save final results
            self.analysis_results = pdf_report

        except Exception as e:
            # If there's an error, store it in the results
            self.analysis_results = {
                "error": str(e),
                "is_safe": False
            }

    def _extract_pdf_links(self) -> list:
        """
        Utility method to extract links from the PDF using PyPDF2.
        Returns a list of unique links.
        """
        links = set()
        try:
            reader = PdfReader(self.file_path)
            for page in reader.pages:
                if "/Annots" in page:
                    annotations = page["/Annots"]
                    for annotation in annotations:
                        annotation_obj = annotation.get_object()
                        if "/A" in annotation_obj and "/URI" in annotation_obj["/A"]:
                            link = annotation_obj["/A"]["/URI"]
                            links.add(link)
        except Exception as e:
            # You could add an "error" field to analysis if you like
            pass
        return list(links)
