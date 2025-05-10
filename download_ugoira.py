import requests
import os
import json
import re
from tqdm import tqdm

# Determine the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config_downloader_animations.json")

# Create Pixiv_Downloads/Animations folder relative to script
SAVE_DIR = os.path.join(SCRIPT_DIR, "Pixiv_Downloads", "Animations")
os.makedirs(SAVE_DIR, exist_ok=True)


def load_phpsessid():
    """Load PHPSESSID from config.json or ask the user for input."""
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            config = json.load(f)
        return config.get("PHPSESSID")

    phpsessid = input("Enter your Pixiv PHPSESSID: ").strip()
    save_phpsessid(phpsessid)
    return phpsessid


def save_phpsessid(phpsessid):
    """Save PHPSESSID to config.json."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"PHPSESSID": phpsessid}, f, indent=4)
    print("PHPSESSID saved successfully!")


def sanitize_filename(filename):
    """Removes invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', "", filename)


def get_pixiv_metadata(artwork_id, headers):
    """Fetches the post title and ZIP URL from Pixiv’s API."""
    api_url = f"https://www.pixiv.net/ajax/illust/{artwork_id}"
    response = requests.get(api_url, headers=headers)

    if response.status_code != 200:
        print("Failed to fetch metadata.")
        return None, None

    data = response.json()
    title = data["body"].get("title", f"Pixiv_{artwork_id}")
    title = sanitize_filename(title)

    ugoira_api_url = f"https://www.pixiv.net/ajax/illust/{artwork_id}/ugoira_meta"
    ugoira_response = requests.get(ugoira_api_url, headers=headers)

    if ugoira_response.status_code != 200:
        print("Failed to fetch Ugoira ZIP URL.")
        return title, None

    ugoira_data = ugoira_response.json()
    zip_url = ugoira_data["body"].get("originalSrc", None)

    return title, zip_url


def download_zip(zip_url, artwork_id, title, headers):
    """Downloads the ZIP file and saves it inside a dedicated subfolder named after the post title."""
    subfolder_name = f"{title} ({artwork_id})"
    subfolder_path = os.path.join(SAVE_DIR, subfolder_name)
    os.makedirs(subfolder_path, exist_ok=True)

    zip_path = os.path.join(subfolder_path, f"{title}.zip")

    response = requests.get(zip_url, headers=headers, stream=True)

    if response.status_code != 200:
        print("Failed to download ZIP file.")
        return

    total_size = int(response.headers.get("content-length", 0))

    with open(zip_path, "wb") as file, tqdm(
        desc=f"Downloading {title}.zip",
        total=total_size,
        unit="B",
        unit_scale=True,
        unit_divisor=1024,
    ) as bar:
        for chunk in response.iter_content(1024):
            file.write(chunk)
            bar.update(len(chunk))

    print(f"Downloaded: {zip_path}")


def main():
    phpsessid = load_phpsessid()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.pixiv.net/",
        "Cookie": f"PHPSESSID={phpsessid}"
    }

    artwork_url = input("Enter Pixiv animation URL: ").strip()

    if "artworks/" in artwork_url:
        artwork_id = artwork_url.split("artworks/")[-1].split("?")[0]
    else:
        print("Invalid Pixiv URL.")
        return

    title, zip_url = get_pixiv_metadata(artwork_id, headers)
    if not zip_url:
        print("Failed to get Ugoira ZIP URL.")
        return

    download_zip(zip_url, artwork_id, title, headers)


if __name__ == "__main__":
    main()
