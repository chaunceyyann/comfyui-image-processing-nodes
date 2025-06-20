import re
import requests
from io import BytesIO
import torch
import numpy as np
from PIL import Image
from nodes import PreviewImage

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
        
        # Check if it's a direct image URL
        if self._is_image_url(url):
            print(f"[YouTubeThumbnailExtractor] Detected direct image URL")
            image_tensor = self._download_image(url)
        else:
            # Extract video ID from URL
            video_id = self._extract_video_id(url)
            if not video_id:
                raise ValueError("Could not extract video ID from the provided URL")
            
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
            image_tensor = self._download_image(thumbnail_url)
        
        # Use PreviewImage's save_images method for UI display
        result = self.save_images(image_tensor, filename_prefix, prompt, extra_pnginfo)
        print(f"[YouTubeThumbnailExtractor] Image saved and processed with PreviewImage")
        print(f"[YouTubeThumbnailExtractor] Save result: {result}")
        
        # Return both tensor for downstream nodes and UI result for display
        return {"ui": result.get("ui", {"images": []}), "result": (image_tensor,)}

    def _is_image_url(self, url):
        """Check if the URL points to an image file."""
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']
        return any(url.lower().endswith(ext) for ext in image_extensions)

    def _download_image(self, url):
        """Download and convert image to tensor."""
        response = requests.get(url, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"Failed to download image. Status code: {response.status_code}")
        
        # Convert image to tensor for ComfyUI
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image_np = np.array(image).astype(np.float32) / 255.0
        # ComfyUI expects tensors in format [batch, height, width, channels]
        image_tensor = torch.from_numpy(image_np).unsqueeze(0)
        print(f"[YouTubeThumbnailExtractor] Image tensor shape: {image_tensor.shape}")
        return image_tensor

    def _extract_video_id(self, url):
        # Regular expressions to match various YouTube URL formats
        patterns = [
            r"youtube\.com/watch\?v=([\w-]{11})",
            r"youtu\.be/([\w-]{11})",
            r"youtube\.com/embed/([\w-]{11})",
            r"youtube\.com/v/([\w-]{11})",
        ]
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        return None

# Register the node
NODE_CLASS_MAPPINGS = {
    "YouTubeThumbnailExtractor": YouTubeThumbnailExtractor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YouTubeThumbnailExtractor": "YouTube Thumbnail Extractor"
}

print("[YouTubeThumbnailExtractor] Node registration complete") 