import json
import textwrap
import time
from pprint import pprint

import requests

API_KEY = "9ff3189a6bf3f6e6cc7c5aaee486d4808b3d7d1747bcf0b396182e755392cfc1"
pdf_file_path = "B.pdf"


def upload_pdf_to_virustotal(pdf_file_path):
    """
    Uploads a PDF file to VirusTotal for scanning and retrieves the report.

    :param pdf_file_path: Path to the PDF file you want to scan
    :return: Full scan report or error message
    """
    upload_url = "https://www.virustotal.com/api/v3/files"
    headers = {"x-apikey": API_KEY}

    try:
        # Open the PDF file in binary mode
        with open(pdf_file_path, "rb") as pdf_file:
            files = {"file": (pdf_file_path, pdf_file)}
            print("Uploading file to VirusTotal...")

            # Send POST request to upload the file
            response = requests.post(upload_url, headers=headers, files=files)
            response.raise_for_status()  # Raise exception for HTTP errors

        # Get the analysis ID from the response
        json_response = response.json()
        analysis_id = json_response["data"]["id"]

        # Retrieve the full report
        return analysis_id

    except requests.exceptions.RequestException as e:
        return f"An error occurred: {e}"
    except KeyError:
        return "Unexpected response structure. File may not have been uploaded successfully."


def get_scan_report(analysis_id):
    """
    Retrieves the scan report for the uploaded file.

    :param analysis_id: The analysis ID returned after uploading the file
    :return: Full scan report as a string
    """
    report_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    headers = {"x-apikey": API_KEY}

    print("Waiting for analysis to complete...")

    # Poll the API until the analysis is complete
    while True:
        response = requests.get(report_url, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors
        json_response = response.json()

        status = json_response["data"]["attributes"]["status"]
        if status == "completed":
            print("Analysis completed.")
            return format_scan_report(json_response)
        else:
            print("Analysis in progress, waiting...")
            time.sleep(10)  # Wait before checking again


def format_scan_report(json_response):
    """
    Formats the VirusTotal scan report for easy reading.

    :param json_response: The JSON response containing the scan results
    :return: Formatted scan report as a string
    """
    results = json_response["data"]["attributes"]["results"]
    formatted_report = "VirusTotal Scan Report:\n"
    formatted_report += "=" * 40 + "\n"

    for engine, details in results.items():
        formatted_report += f"{engine}: {details['category']}\n"

    formatted_report += "=" * 40
    return formatted_report


def fetch_full_report(analysis_id):
    """
    Fetches the full detailed report for the given analysis ID.

    :param analysis_id: The analysis ID returned after uploading the file
    :return: Full detailed report as a JSON object
    """
    report_url = f"https://www.virustotal.com/api/v3/analyses/{analysis_id}"
    headers = {"x-apikey": API_KEY}

    try:
        print("Fetching full detailed report...")
        response = requests.get(report_url, headers=headers)
        response.raise_for_status()  # Raise exception for HTTP errors

        # Return the full JSON response for detailed analysis
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": f"An error occurred: {e}"}


def get_analysis(path, short=True, full=False):
    analysis_id = upload_pdf_to_virustotal(path)  # Pass the path to upload function
    formatted_result = ""
    full_report = ""

    if short:
        formatted_result = get_scan_report(analysis_id)

    if full:
        formatted_result += "\nFULL RESULT:\n"
        full_report = fetch_full_report(analysis_id)

        # Convert the dictionary to a pretty-printed string
        full_report_string = json.dumps(full_report, indent=40)

        # Wrap the string to 40 characters width
        full_report_string = textwrap.fill(full_report_string, width=40)

        return formatted_result + "\n" + full_report_string

    return formatted_result


# Example Usage
if __name__ == "__main__":
    report = get_analysis(pdf_file_path, short=True, full=True)
    print(report)

