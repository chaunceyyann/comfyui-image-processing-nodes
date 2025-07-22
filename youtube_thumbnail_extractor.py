import re
import requests
from io import BytesIO
import torch
import numpy as np
from PIL import Image, ImageSequence
from nodes import PreviewImage
from urllib.parse import urlparse
import os
import string
import imageio  # <-- add this import

class YouTubeThumbnailExtractor(PreviewImage):
    def __init__(self):
        super().__init__()
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "url": ("STRING", {"default": ""}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "extract_thumbnail"
    CATEGORY = "cyan-image"
    OUTPUT_NODE = True
    BACKGROUND_COLOR = "#00FFFF"  # Cyan color

    def extract_thumbnail(self, url, filename_prefix="youtube_thumbnail", prompt=None, extra_pnginfo=None):
        print(f"[YouTubeThumbnailExtractor] Processing URL: {url}")
        is_youtube = False
        is_short = False
        # Check if it's a direct image URL
        if self._is_image_url(url):
            print(f"[YouTubeThumbnailExtractor] Detected direct image URL")
            image_tensor, pil_image, save_name = self._download_image(url, return_pil=True)
            save_dir = r"E:\ComfyUI\input\Internet-Img"
            save_path = self._get_unique_path(save_dir, save_name)
        else:
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                raise ValueError("Could not extract video ID from the provided URL")
            is_youtube = True
            if "youtube.com/shorts/" in url:
                is_short = True
            print(f"[YouTubeThumbnailExtractor] Extracted Video ID: {video_id}")
            # Try to get the largest thumbnail (maxresdefault)
            thumbnail_url = f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg"
            print(f"[YouTubeThumbnailExtractor] Attempting to fetch thumbnail from: {thumbnail_url}")
            # Fetch the image
            response = requests.get(thumbnail_url, timeout=10)
            if response.status_code != 200:
                # Fallback to hqdefault if maxresdefault is not available
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/hqdefault.jpg"
                print(f"[YouTubeThumbnailExtractor] Max resolution not available, falling back to: {thumbnail_url}")
                response = requests.get(thumbnail_url, timeout=10)
                if response.status_code != 200:
                    raise ValueError(f"Failed to fetch thumbnail. Status code: {response.status_code}")
            print(f"[YouTubeThumbnailExtractor] Thumbnail fetched successfully")
            image_tensor, pil_image, _ = self._download_image(thumbnail_url, return_pil=True)
            if is_short:
                # Crop to central 400x720 region (remove extended left/right)
                print(f"[YouTubeThumbnailExtractor] Detected Shorts. Cropping thumbnail to 400x720 from center.")
                left = (1280 - 400) // 2
                upper = 0
                right = left + 400
                lower = 720
                pil_image = pil_image.crop((left, upper, right, lower))
                image_np = np.array(pil_image).astype(np.float32) / 255.0
                image_tensor = torch.from_numpy(image_np).unsqueeze(0)
            save_dir = r"E:\ComfyUI\input\YT-thumbnails"
            # Get video title for filename
            video_title = self._get_youtube_title(video_id)
            if not video_title:
                video_title = video_id
            save_name = self._sanitize_filename(video_title) + ".jpg"
            save_path = os.path.join(save_dir, save_name)
        # Save the image to the appropriate directory
        os.makedirs(save_dir, exist_ok=True)
        pil_image.save(save_path)
        print(f"[YouTubeThumbnailExtractor] Image saved to: {save_path}")
        # Use PreviewImage's save_images method for UI display
        result = self.save_images(image_tensor, filename_prefix, prompt, extra_pnginfo)
        print(f"[YouTubeThumbnailExtractor] Image saved and processed with PreviewImage")
        print(f"[YouTubeThumbnailExtractor] Save result: {result}")
        # Return both tensor for downstream nodes and UI result for display
        return {"ui": result.get("ui", {"images": []}), "result": (image_tensor,)}

    def _is_image_url(self, url):
        """Check if the URL points to an image file, ignoring query parameters."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        path = urlparse(url).path  # Only check the path part
        return any(path.lower().endswith(ext) for ext in image_extensions)

    def _download_image(self, url, return_pil=False):
        """Download and convert image, GIF, or MP4 to tensor. Optionally return PIL image and filename."""
        # Set headers for browser-like request
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"Failed to download image. Status code: {response.status_code}")
        content_type = response.headers.get('Content-Type', '')
        parsed = urlparse(url)
        base = os.path.basename(parsed.path)
        save_name = base if base else "downloaded_image.jpg"
        # Handle GIF
        if url.lower().endswith('.gif') or 'gif' in content_type:
            pil_image = Image.open(BytesIO(response.content))
            pil_image.seek(0)  # First frame
            pil_image = pil_image.convert("RGB")
        # Handle MP4
        elif url.lower().endswith('.mp4') or 'mp4' in content_type:
            # Save to temp file
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.mp4', delete=False) as tmp:
                tmp.write(response.content)
                tmp_path = tmp.name
            # Read first frame
            reader = imageio.get_reader(tmp_path)
            frame = reader.get_data(0)
            reader.close()  # Close the reader before deleting the file
            pil_image = Image.fromarray(frame).convert("RGB")
            os.remove(tmp_path)
        else:
            pil_image = Image.open(BytesIO(response.content)).convert("RGB")
        image_np = np.array(pil_image).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_np).unsqueeze(0)
        print(f"[YouTubeThumbnailExtractor] Image tensor shape: {image_tensor.shape}")
        if return_pil:
            return image_tensor, pil_image, save_name
        return image_tensor

    def _extract_video_id(self, url):
        # Regular expressions to match various YouTube URL formats, including Shorts
        patterns = [
            r"youtube\.com/watch\?v=([\w-]{11})",
            r"youtu\.be/([\w-]{11})",
            r"youtube\.com/embed/([\w-]{11})",
            r"youtube\.com/v/([\w-]{11})",
            r"youtube\.com/shorts/([\w-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

    def _get_youtube_title(self, video_id):
        """Fetch the YouTube video title using oEmbed (no API key required)."""
        try:
            oembed_url = f"https://www.youtube.com/oembed?url=https://www.youtube.com/watch?v={video_id}&format=json"
            resp = requests.get(oembed_url, timeout=10)
            if resp.status_code == 200:
                data = resp.json()
                return data.get("title", None)
        except Exception as e:
            print(f"[YouTubeThumbnailExtractor] Failed to fetch video title: {e}")
        return None

    def _sanitize_filename(self, name):
        """Remove or replace characters not allowed in filenames."""
        valid_chars = f"-_.() {string.ascii_letters}{string.digits}"
        sanitized = ''.join(c if c in valid_chars else '_' for c in name)
        return sanitized.strip()

    def _get_unique_path(self, directory, filename):
        """Append underscores to filename until it is unique in the directory."""
        base, ext = os.path.splitext(filename)
        candidate = filename
        while os.path.exists(os.path.join(directory, candidate)):
            base += '_'
            candidate = base + ext
        return os.path.join(directory, candidate)

# Register the node
NODE_CLASS_MAPPINGS = {
    "YouTubeThumbnailExtractor": YouTubeThumbnailExtractor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YouTubeThumbnailExtractor": "YouTube Thumbnail Extractor"
}

print("[YouTubeThumbnailExtractor] Node registration complete") 