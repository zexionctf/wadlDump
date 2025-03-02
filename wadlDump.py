import xml.etree.ElementTree as ET
import argparse
import requests
import tempfile
import os

def fetch_wadl_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()

        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".wadl")
        temp_file.write(response.content)
        temp_file.close()

        return temp_file.name
    except requests.RequestException as e:
        print(f"Error fetching WADL file from URL: {e}")
        return None

def parse_wadl(file_path):
    try:
        tree = ET.parse(file_path)
        root = tree.getroot()

        namespace = {'wadl': 'http://wadl.dev.java.net/2009/02'}

        base_url_element = root.find(".//wadl:resources", namespace)
        base_url = base_url_element.get("base") if base_url_element is not None else ""

        endpoints = []
        for resource in root.findall(".//wadl:resource", namespace):
            path = resource.get("path")

            for method in resource.findall("wadl:method", namespace):
                method_type = method.get("name")
                full_path = f"{base_url.rstrip('/')}/{path.lstrip('/')}" if base_url else path
                endpoints.append((method_type, full_path))

        return endpoints
    except Exception as e:
        print(f"Error parsing WADL file: {e}")
        return []

def colored_method(method):
    colors = {
        "GET": "\033[92m",
        "POST": "\033[94m",
        "PUT": "\033[93m",
        "DELETE": "\033[91m",
        "PATCH": "\033[95m",
        "HEAD": "\033[96m"
    }
    reset_color = "\033[0m"
    return f"{colors.get(method, '\033[97m')}[{method}]{reset_color}"

def main():
    parser = argparse.ArgumentParser(description="Extract endpoints from a WADL file or URL")
    parser.add_argument("source", help="Path to the WADL file or URL")
    args = parser.parse_args()

    file_path = args.source

    if file_path.startswith("http://") or file_path.startswith("https://"):
        file_path = fetch_wadl_from_url(file_path)
        if not file_path:
            print("Failed to retrieve WADL from URL.")
            return

    endpoints = parse_wadl(file_path)

    if file_path and file_path.startswith(tempfile.gettempdir()):
        os.remove(file_path)

    if endpoints:
        for method, path in endpoints:
            print(f"{colored_method(method)} {path}")
    else:
        print("No endpoints found or error in parsing.")

if __name__ == "__main__":
    main()
