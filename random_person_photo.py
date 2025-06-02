import requests
import torch
import numpy as np
from PIL import Image
from io import BytesIO
from nodes import PreviewImage
import os

class RandomPersonPhoto(PreviewImage):
    def __init__(self):
        super().__init__()
        # Get API key from environment variable
        self.api_key = os.getenv("UNSPLASH_ACCESS_KEY", "")
        if not self.api_key:
            print("[RandomPersonPhoto] Warning: No UNSPLASH_ACCESS_KEY found in environment variables")
            print("[RandomPersonPhoto] Please set UNSPLASH_ACCESS_KEY to use this node")
            print("[RandomPersonPhoto] You can get a free Access Key from https://unsplash.com/developers")
            print("[RandomPersonPhoto] Note: Use the Access Key (Client ID), not the Secret Key")

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "width": ("INT", {"default": 800, "min": 100, "max": 2000, "step": 100}),
                "height": ("INT", {"default": 1200, "min": 100, "max": 2000, "step": 100}),
                "gender": (["random", "male", "female"], {"default": "random"}),
                "query": ("STRING", {"default": "portrait"}),
                "seed": ("INT", {"default": -1, "min": -1, "max": 0xffffffff}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "get_random_person"
    CATEGORY = "cyan-image"
    OUTPUT_NODE = True
    BACKGROUND_COLOR = "#00FFFF"  # Cyan color

    def get_random_person(self, width=800, height=1200, gender="random", query="portrait", seed=-1, filename_prefix="random_person", prompt=None, extra_pnginfo=None):
        print(f"[RandomPersonPhoto] Fetching random person photo ({width}x{height}, gender: {gender})")
        
        if not self.api_key:
            raise ValueError("No Unsplash Access Key found. Please set UNSPLASH_ACCESS_KEY environment variable.")
        
        # Construct search query based on gender
        search_query = query
        if gender != "random":
            search_query = f"{query} {gender}"
        
        # Handle seed for reproducible results
        if seed == -1:
            page = np.random.randint(1, 10)  # Random page between 1-10
        else:
            np.random.seed(seed)
            page = np.random.randint(1, 10)
            np.random.seed(None)
        
        # Search for photos
        search_url = "https://api.unsplash.com/search/photos"
        headers = {
            "Authorization": f"Client-ID {self.api_key}",
            "Accept-Version": "v1"
        }
        params = {
            "query": search_query,
            "per_page": 30,
            "page": page,
            "orientation": "portrait"
        }
        
        print(f"[RandomPersonPhoto] Searching Unsplash with query: {search_query}")
        response = requests.get(search_url, headers=headers, params=params)
        
        if response.status_code != 200:
            raise ValueError(f"Failed to search photos. Status code: {response.status_code}")
        
        data = response.json()
        if not data["results"]:
            raise ValueError("No photos found for the given query")
        
        # Select a random photo from results
        photo = np.random.choice(data["results"])
        photo_url = photo["urls"]["raw"]
        
        # Add size parameters to URL
        photo_url = f"{photo_url}&w={width}&h={height}&fit=crop"
        
        print(f"[RandomPersonPhoto] Fetching photo from URL: {photo_url}")
        
        # Download the image
        response = requests.get(photo_url, timeout=10)
        if response.status_code != 200:
            raise ValueError(f"Failed to download image. Status code: {response.status_code}")
        
        # Convert image to tensor for ComfyUI
        image = Image.open(BytesIO(response.content)).convert("RGB")
        image_np = np.array(image).astype(np.float32) / 255.0
        image_tensor = torch.from_numpy(image_np).unsqueeze(0)  # Shape: [1, height, width, channels]
        print(f"[RandomPersonPhoto] Image tensor shape: {image_tensor.shape}")
        
        # Use PreviewImage's save_images method for UI display
        result = self.save_images(image_tensor, filename_prefix, prompt, extra_pnginfo)
        print(f"[RandomPersonPhoto] Image saved and processed with PreviewImage")
        
        # Return both tensor for downstream nodes and UI result for display
        return {"ui": result.get("ui", {"images": []}), "result": (image_tensor,)}

# Register the node
NODE_CLASS_MAPPINGS = {
    "RandomPersonPhoto": RandomPersonPhoto
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "RandomPersonPhoto": "Random Person Photo"
}

print("[RandomPersonPhoto] Node registration complete") 