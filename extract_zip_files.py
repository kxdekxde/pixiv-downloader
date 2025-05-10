import os
import zipfile
from tqdm import tqdm

class ZipExtractor:
    def __init__(self):
        """Initialize with base directory where animations are stored"""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_directory = os.path.join(script_dir, "Pixiv_Downloads", "Animations")
        os.makedirs(self.base_directory, exist_ok=True)
    
    def find_and_extract_zip_files(self):
        """Iterate through all subfolders, find .zip files, and extract them"""
        for root, dirs, files in os.walk(self.base_directory):
            for file in files:
                if file.lower().endswith('.zip'):
                    zip_path = os.path.join(root, file)
                    self.extract_zip(zip_path)
    
    def extract_zip(self, zip_path):
        """Extract the .zip file to a folder with the same name, show progress bar, then delete .zip"""
        folder_name = os.path.splitext(os.path.basename(zip_path))[0]
        extraction_folder = os.path.join(os.path.dirname(zip_path), folder_name)

        os.makedirs(extraction_folder, exist_ok=True)

        try:
            print(f"\nExtracting {zip_path} to {extraction_folder}")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                files = zip_ref.namelist()
                with tqdm(total=len(files), desc=f"Extracting {folder_name}") as pbar:
                    for file in files:
                        zip_ref.extract(file, extraction_folder)
                        pbar.update(1)
            print(f"Extraction completed: {extraction_folder}")
            self.delete_zip_file(zip_path)
        except Exception as e:
            print(f"Failed to extract {zip_path}: {e}")

    def delete_zip_file(self, zip_path):
        """Delete the .zip file after extraction"""
        try:
            os.remove(zip_path)
            print(f"Deleted {zip_path}")
        except Exception as e:
            print(f"Failed to delete {zip_path}: {e}")

def main():
    print("=== Pixiv Animation ZIP Extractor ===")
    
    extractor = ZipExtractor()
    extractor.find_and_extract_zip_files()

if __name__ == "__main__":
    main()
