import requests
import urllib3
from pathlib import Path


def download_image(image_url,
                   directory_for_save='images',
                   file_name=""):
    Path(f'{directory_for_save}').mkdir(parents=True, exist_ok=True)
    image_file_name = file_name if file_name else Path(image_url).name
    path_for_saving = f'{directory_for_save}/{image_file_name}'
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    response = requests.get(image_url, verify=False)
    response.raise_for_status()
    with open(path_for_saving, 'wb') as file:
        file.write(response.content)
    return path_for_saving
