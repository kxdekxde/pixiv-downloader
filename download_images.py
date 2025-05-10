import requests
import os
import re
import json
from tqdm import tqdm
from urllib.parse import urlparse

# Determine the script directory
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config_downloader_images.json")

# Create Pixiv_Downloads/Images folder in the same directory as the script
SAVE_DIR = os.path.join(SCRIPT_DIR, "Pixiv_Downloads", "Images")
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


def extract_artwork_id_from_url(url):
    """Extract artwork ID from various Pixiv URL formats."""
    if "i.pximg.net" in url:
        match = re.search(r'/(\d+)_p\d+\.', url)
        if match:
            return match.group(1)

    if "artworks/" in url:
        return url.split("artworks/")[-1].split("?")[0].split("/")[0]

    return None


def get_pixiv_title(artwork_id, headers):
    """Fetches the post title from Pixiv's API."""
    api_url = f"https://www.pixiv.net/ajax/illust/{artwork_id}"
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            title = data.get("body", {}).get("title", f"Pixiv_{artwork_id}")
            return sanitize_filename(title)
    except Exception as e:
        print(f"Error fetching title: {e}")

    return f"Pixiv_{artwork_id}"


def get_image_urls(input_url, headers):
    """Handle both direct image URLs and artwork page URLs."""
    if "i.pximg.net" in input_url:
        artwork_id = extract_artwork_id_from_url(input_url)
        if not artwork_id:
            return []

        base_url = re.sub(r'_p\d+\.', '_p0.', input_url)
        if not check_url_exists(base_url, headers):
            return [input_url]

        urls = []
        for i in range(0, 10):
            url = input_url.replace(f'_p{artwork_id[-1]}', f'_p{i}')
            if check_url_exists(url, headers):
                urls.append(url)
            else:
                break
        return urls if urls else [input_url]

    artwork_id = extract_artwork_id_from_url(input_url)
    if not artwork_id:
        return []

    try:
        api_url = f"https://www.pixiv.net/ajax/illust/{artwork_id}/pages"
        response = requests.get(api_url, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return [img['urls']['original'] for img in data.get('body', [])]
    except Exception as e:
        print(f"Error using API: {e}")

    try:
        response = requests.get(f"https://www.pixiv.net/artworks/{artwork_id}", headers=headers, timeout=10)
        if response.status_code == 200:
            match = re.search(r'"original":"(https:\\/\\/i\.pximg\.net\\/img-original\\/[^"]+)"', response.text)
            if match:
                base_url = match.group(1).replace('\\/', '/')
                urls = [base_url.replace("_p0", f"_p{i}") for i in range(10)]
                return [url for url in urls if check_url_exists(url, headers)]
    except Exception as e:
        print(f"Error scraping page: {e}")

    return []


def check_url_exists(url, headers):
    """Check if an image URL exists."""
    try:
        response = requests.head(url, headers=headers, timeout=5)
        return response.status_code == 200
    except:
        return False


def download_image(image_url, save_folder, headers):
    """Downloads an image from Pixiv with a progress bar."""
    os.makedirs(save_folder, exist_ok=True)
    filename = os.path.join(save_folder, os.path.basename(urlparse(image_url).path))

    artwork_id = extract_artwork_id_from_url(image_url)
    if artwork_id:
        headers = headers.copy()
        headers["Referer"] = f"https://www.pixiv.net/artworks/{artwork_id}"

    try:
        response = requests.get(image_url, headers=headers, stream=True, timeout=30)
        if response.status_code == 200:
            total_size = int(response.headers.get("content-length", 0))
            with open(filename, "wb") as file, tqdm(
                desc=os.path.basename(filename),
                total=total_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
            ) as bar:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
                    bar.update(len(chunk))
            print(f"Successfully downloaded: {filename}")
            return True
        else:
            print(f"Failed to download (HTTP {response.status_code}): {image_url}")
    except Exception as e:
        print(f"Error downloading {image_url}: {str(e)}")

    return False


def main():
    phpsessid = load_phpsessid()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.pixiv.net/",
        "Cookie": f"PHPSESSID={phpsessid};"
    }

    input_url = input("Enter Pixiv image URL or artwork page URL: ").strip()

    artwork_id = extract_artwork_id_from_url(input_url)
    if not artwork_id:
        print("Invalid Pixiv URL. It should be either an artwork page or direct image URL.")
        return

    title = get_pixiv_title(artwork_id, headers)
    save_folder = os.path.join(SAVE_DIR, f"{title} ({artwork_id})")

    image_urls = get_image_urls(input_url, headers)
    if not image_urls:
        print("No images found or failed to retrieve.")
        return

    print(f"Found {len(image_urls)} images to download...")
    for img_url in image_urls:
        download_image(img_url, save_folder, headers)


if __name__ == "__main__":
    main()
