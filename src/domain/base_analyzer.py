# base_analyzer.py
from abc import ABC, abstractmethod

class BaseAnalyzer(ABC):
    """
    Abstract/base class for file analyzers (PDF, DOC, EXE, etc.).
    Each specific file type will subclass this.
    """

    def __init__(self, file_path: str):
        self.file_path = file_path
        # We'll store analysis results here (e.g., is_safe, metadata, etc.)
        self.analysis_results = {}

    @abstractmethod
    def analyze(self):
        """
        Perform file-specific analysis and populate self.analysis_results.
        """
        pass

    def get_results(self):
        """
        Returns the analysis results dictionary.
        Could be used by other components to retrieve the final data.
        """
        return self.analysis_results
