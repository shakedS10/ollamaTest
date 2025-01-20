# virus_total_service.py

import requests
import time
import json
import textwrap

class VirusTotalService:
    """
    Encapsulates interactions with the VirusTotal API:
      - Uploading a file for scanning
      - Polling for the analysis report
      - Returning a formatted summary
    """

    def __init__(self, api_key: str):
        self.api_key = api_key

    def upload_file_to_virustotal(self, file_path: str) -> str:
        """
        Uploads the file to VirusTotal and returns the analysis ID.
        """
        upload_url = "https://www.virustotal.com/api/v3/files"
        headers = {"x-apikey": self.api_key}

        with open(file_path, "rb") as f:
            files = {"file": (file_path, f)}
            response = requests.post(upload_url, headers=headers, files=files)
            response.raise_for_status()  # Raise exception for 4xx/5xx
            json_resp = response.json()
            return json_resp["data"]["id"]  # Extract analysis ID

    def poll_scan_report(self, analysis_id: str, poll_interval: int = 5) -> dict:
        """
        Polls VirusTotal until the scan is completed, then returns the JSON report.
        """
        report_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
        headers = {"x-apikey": self.api_key}

        while True:
            resp = requests.get(report_url, headers=headers)
            resp.raise_for_status()
            data = resp.json()
            status = data["data"]["attributes"]["status"]

            if status == "completed":
                return data  # Full JSON report
            time.sleep(poll_interval)

    def format_short_report(self, report_json: dict) -> str:
        """
        Creates a brief textual summary of the engines' detection.
        """
        results = report_json["data"]["attributes"]["results"]
        lines = ["VirusTotal Scan Report", "=" * 40]
        for engine, details in results.items():
            category = details.get("category", "unknown")
            lines.append(f"{engine}: {category}")
        lines.append("=" * 40)
        return "\n".join(lines)

    def analyze_file(self, file_path: str, short: bool = True, full: bool = False) -> dict:
        """
        High-level method to:
          1) Upload file -> get analysis ID
          2) Poll for scan report
          3) Return optional short summary + full JSON if requested
        """
        try:
            analysis_id = self.upload_file_to_virustotal(file_path)
            full_report = self.poll_scan_report(analysis_id)

            short_report_str = self.format_short_report(full_report) if short else None
            full_report_str = None
            if full:
                # Convert the JSON to a nicely printed string
                pretty_json = json.dumps(full_report, indent=2)
                full_report_str = textwrap.fill(pretty_json, width=70)

            return {
                "short_report": short_report_str,
                "full_report": full_report_str,
                "raw_json": full_report if full else None
            }
        except Exception as e:
            return {
                "error": str(e),
                "short_report": None,
                "full_report": None
            }
