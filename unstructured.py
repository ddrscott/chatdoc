import logging
from urllib.parse import urljoin
from urllib3.response import HTTPResponse
import os
import mimetypes
import requests
from io import BytesIO

UNSTRUCTURED_API_URL = os.getenv('UNSTRUCTURED_API_URL')
UNSTRUCTURED_API_KEY = os.getenv('UNSTRUCTURED_API_KEY')

API_TIMEOUT = 600

def partition_api(bytes_data: BytesIO, file_name: str, strategy: str = 'auto') -> list[dict]:    
    url = urljoin(UNSTRUCTURED_API_URL, 'general/v0/general')
    headers = {
        'accept': 'application/json',
        'unstructured-api-key': UNSTRUCTURED_API_KEY
    }

    mime_type, _ = mimetypes.guess_type(file_name)
    if mime_type is None:
        mime_type = 'application/octet-stream'

    files = {
        'files': (file_name, bytes_data, mime_type)
    }
    params = {
        'strategy': strategy,
        'coordinates': True,
        'max_characters': 8000
    }
    response = requests.post(url, headers=headers, files=files, data=params, timeout=API_TIMEOUT)

    if response.status_code == 200:
        return response.json()
    raise Exception(f"Unexpected response partitioning document: {response.status_code} {response.text}")

