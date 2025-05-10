import os
import shutil
import subprocess
import time
from tqdm import tqdm
from PIL import Image, ImageOps

class VideoCreator:
    def __init__(self, input_folder, output_folder, ffmpeg_path=None, target_bitrate="15M", target_fps=15):
        self.input_folder = os.path.abspath(input_folder)
        self.output_folder = os.path.abspath(output_folder)

        script_dir = os.path.dirname(os.path.abspath(__file__))
        self.base_directory = os.path.join(script_dir, "Pixiv_Downloads", "Animations")
        self.output_directory = os.path.join(script_dir, "Pixiv_Downloads", "MP4_OUTPUT")

        os.makedirs(self.base_directory, exist_ok=True)
        os.makedirs(self.output_directory, exist_ok=True)

        self.ffmpeg_path = ffmpeg_path or os.path.join(script_dir, "ffmpeg", "bin", "ffmpeg.exe")
        self.target_bitrate = target_bitrate
        self.target_fps = target_fps

    def ensure_even_dimensions(self):
        image_files = sorted(
            f for f in os.listdir(self.input_folder)
            if f.lower().endswith('.jpg') and f.split('.')[0].isdigit()
        )

        for image_file in image_files:
            image_path = os.path.join(self.input_folder, image_file)
            try:
                with Image.open(image_path) as img:
                    width, height = img.size
                    new_width, new_height = width, height

                    if width % 2 != 0:
                        new_width += 1
                    if height % 2 != 0:
                        new_height += 1

                    if new_width != width or new_height != height:
                        padded_img = ImageOps.pad(img, (new_width, new_height), color=(0, 0, 0))
                        padded_img.save(image_path)
                        print(f"Added padding to {image_file}: {width}x{height} → {new_width}x{new_height}")
            except Exception as e:
                print(f"Error processing {image_file}: {e}")

    def resize_images_to_720p(self):
        image_files = sorted(
            f for f in os.listdir(self.input_folder)
            if f.lower().endswith('.jpg') and f.split('.')[0].isdigit()
        )

        for image_file in image_files:
            image_path = os.path.join(self.input_folder, image_file)
            try:
                with Image.open(image_path) as img:
                    width, height = img.size

                    if width > 1280 or height > 720:
                        if width > height:
                            new_width = 1280
                            new_height = int((height / width) * new_width)
                        else:
                            new_height = 720
                            new_width = int((width / height) * new_height)

                        img = img.resize((new_width, new_height))
                        img = img.convert("RGB")

                        if new_width % 2 != 0:
                            new_width += 1
                        if new_height % 2 != 0:
                            new_height += 1

                        resized_img = img.resize((new_width, new_height))
                        resized_img.save(image_path)
                        print(f"Resized {image_file} to {new_width}x{new_height}")
            except Exception as e:
                print(f"Error resizing {image_file}: {e}")

    def create_video(self):
        self.resize_images_to_720p()
        self.ensure_even_dimensions()

        image_files = sorted(
            f for f in os.listdir(self.input_folder)
            if f.lower().endswith('.jpg') and f.split('.')[0].isdigit()
        )

        if not image_files:
            print(f"No images found in {self.input_folder}. Skipping video creation.")
            return

        relative_folder_name = os.path.relpath(self.input_folder, start=self.base_directory)
        output_video_folder = os.path.join(self.output_directory, os.path.dirname(relative_folder_name))
        os.makedirs(output_video_folder, exist_ok=True)

        video_name = f"{os.path.basename(self.input_folder)}.mp4"
        output_video_path = os.path.join(output_video_folder, video_name)

        cmd = [
            self.ffmpeg_path,
            "-framerate", str(self.target_fps),
            "-i", os.path.join(self.input_folder, "%06d.jpg"),
            "-vf", "scale=iw:ih",
            "-c:v", "libx264",
            "-b:v", self.target_bitrate,
            "-maxrate", self.target_bitrate,
            "-bufsize", "2M",
            "-preset", "medium",
            "-pix_fmt", "yuv420p",
            "-movflags", "+faststart",
            "-y",
            output_video_path
        ]

        try:
            print(f"\nCreating video {output_video_path}...")
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode != 0:
                print(f"FFmpeg Error: {result.stderr}")
            else:
                print(f"Video successfully created: {output_video_path}")
        except Exception as e:
            print(f"Error creating video: {e}")

def process_folders(base_folder, output_folder, ffmpeg_path, target_bitrate, target_fps):
    for root, dirs, files in os.walk(base_folder):
        image_files = [f for f in files if f.lower().endswith('.jpg') and f.split('.')[0].isdigit()]
        if image_files:
            video_creator = VideoCreator(root, output_folder, ffmpeg_path, target_bitrate, target_fps)
            video_creator.create_video()

def main():
    print("=== Pixiv Image to Video Creator ===")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    base_folder = os.path.join(script_dir, "Pixiv_Downloads", "Animations")
    output_folder = os.path.join(script_dir, "Pixiv_Downloads", "MP4_OUTPUT")
    ffmpeg_path = os.path.join(script_dir, "ffmpeg", "bin", "ffmpeg.exe")

    os.makedirs(base_folder, exist_ok=True)
    os.makedirs(output_folder, exist_ok=True)

    target_bitrate = "15M"
    print(f"\nUsing default bitrate: {target_bitrate}")

    target_fps = 15
    print(f"\nUsing framerate: {target_fps} FPS")

    process_folders(base_folder, output_folder, ffmpeg_path, target_bitrate, target_fps)

    # Give FFmpeg time to close file handles
    print("\nWaiting for final file handles to release...")
    time.sleep(2)

    # Safe cleanup
    if os.path.exists(base_folder):
        try:
            shutil.rmtree(base_folder)
            print(f"\nDeleted folder: {base_folder}")
        except Exception as e:
            print(f"\nError during cleanup: {e}")
    else:
        print(f"\nFolder already removed: {base_folder}")

if __name__ == "__main__":
    main()
