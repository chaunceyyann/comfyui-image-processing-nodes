import torch
import numpy as np
from PIL import Image
import folder_paths
import os
import hashlib

def log_message(message):
    print(f"[ImageSizeProcessor] {message}")

# Cache for upscaled images
class ImageCache:
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
        self.access_count = {}
    
    def get_key(self, image, scale_factor):
        # Create a hash of the image data and scale factor
        if isinstance(image, torch.Tensor):
            image_np = image.cpu().numpy()
        else:
            image_np = np.array(image)
        image_bytes = image_np.tobytes()
        return hashlib.md5(image_bytes + str(scale_factor).encode()).hexdigest()
    
    def get(self, image, scale_factor):
        key = self.get_key(image, scale_factor)
        if key in self.cache:
            self.access_count[key] += 1
            log_message(f"Cache hit for image with scale {scale_factor}")
            return self.cache[key]
        return None
    
    def put(self, image, scale_factor, processed_image):
        key = self.get_key(image, scale_factor)
        
        # If cache is full, remove least accessed item
        if len(self.cache) >= self.max_size:
            min_key = min(self.access_count.items(), key=lambda x: x[1])[0]
            del self.cache[min_key]
            del self.access_count[min_key]
        
        self.cache[key] = processed_image
        self.access_count[key] = 1
        log_message(f"Cached image with scale {scale_factor}")

# Initialize global cache
image_cache = ImageCache()

# Predefined Stable Diffusion dimensions organized by model and orientation
SD_DIMENSIONS = {
    # SD 1.x
    "SD 1.x - Square (512x512)": 512 * 512,
    "SD 1.x - Portrait (512x768)": 512 * 768,
    "SD 1.x - Landscape (768x512)": 768 * 512,
    
    # SD 2.x
    "SD 2.x - Square (768x768)": 768 * 768,
    
    # SDXL
    "SDXL - Square (1024x1024)": 1024 * 1024,
    "SDXL - Portrait (1024x1536)": 1024 * 1536,
    "SDXL - Landscape (1536x1024)": 1536 * 1024,
    
    # SDXL 1.0
    "SDXL 1.0 - Portrait (1152x896)": 1152 * 896,
    "SDXL 1.0 - Landscape (896x1152)": 896 * 1152,
    "SDXL 1.0 - Portrait Alt (1216x832)": 1216 * 832,
    "SDXL 1.0 - Landscape Alt (832x1216)": 832 * 1216,
    
    # High Resolution
    "High Res - Square (1536x1536)": 1536 * 1536,
    "High Res - Portrait (1536x2304)": 1536 * 2304,
    "High Res - Landscape (2304x1536)": 2304 * 1536,
    "High Res - Square (2048x2048)": 2048 * 2048,
    "High Res - Portrait (2048x3072)": 2048 * 3072,
    "High Res - Landscape (3072x2048)": 3072 * 2048,
}

# Aspect ratio ranges for automatic selection
ASPECT_RATIO_RANGES = {
    "portrait": (0.5, 0.8),    # Height/Width between 0.5 and 0.8
    "landscape": (1.2, 2.0),   # Height/Width between 1.2 and 2.0
    "square": (0.8, 1.2)       # Height/Width between 0.8 and 1.2
}

def get_dimension_from_aspect_ratio(width, height):
    aspect_ratio = height / width
    
    # Determine orientation
    if ASPECT_RATIO_RANGES["portrait"][0] <= aspect_ratio <= ASPECT_RATIO_RANGES["portrait"][1]:
        # Portrait
        if width <= 512:
            return "SD 1.x - Portrait (512x768)"
        elif width <= 1024:
            return "SDXL - Portrait (1024x1536)"
        elif width <= 1536:
            return "High Res - Portrait (1536x2304)"
        else:
            return "High Res - Portrait (2048x3072)"
    elif ASPECT_RATIO_RANGES["landscape"][0] <= aspect_ratio <= ASPECT_RATIO_RANGES["landscape"][1]:
        # Landscape
        if width <= 512:
            return "SD 1.x - Landscape (768x512)"
        elif width <= 1024:
            return "SDXL - Landscape (1536x1024)"
        elif width <= 1536:
            return "High Res - Landscape (2304x1536)"
        else:
            return "High Res - Landscape (3072x2048)"
    else:
        # Square
        if width <= 512:
            return "SD 1.x - Square (512x512)"
        elif width <= 768:
            return "SD 2.x - Square (768x768)"
        elif width <= 1024:
            return "SDXL - Square (1024x1024)"
        elif width <= 1536:
            return "High Res - Square (1536x1536)"
        else:
            return "High Res - Square (2048x2048)"

class ImageSizeProcessor:
    def __init__(self):
        self.max_pixels = SD_DIMENSIONS["High Res - Square (1536x1536)"]  # Default to SDXL square
        self.min_pixels = SD_DIMENSIONS["SD 2.x - Square (768x768)"]  # Default minimum size
    
    def process_image(self, image, upscale_model=None, resize_method="lanczos", scale_factor=2.0):
        # Convert to PIL Image if it's not already
        if isinstance(image, torch.Tensor):
            image = Image.fromarray((image.cpu().numpy() * 255).astype(np.uint8))
        
        # Calculate total pixels
        width, height = image.size
        total_pixels = width * height
        
        log_message(f"Input image size: {width}x{height} (total pixels: {total_pixels})")
        log_message(f"Max pixels: {self.max_pixels}, Min pixels: {self.min_pixels}")
        
        # Process based on size
        if total_pixels > self.max_pixels:
            # Downscale
            scale_factor = np.sqrt(self.max_pixels / total_pixels)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            log_message(f"Downscaling image to {new_width}x{new_height} (scale factor: {scale_factor})")
            image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        elif total_pixels < self.min_pixels:
            # Upscale
            if upscale_model is not None:
                # Use upscaler model
                log_message(f"Using upscaler model for scaling")
                # Convert to tensor for upscaling
                img_tensor = torch.from_numpy(np.array(image)).float() / 255.0
                img_tensor = img_tensor.permute(2, 0, 1).unsqueeze(0)
                
                log_message(f"Upscaling image with provided upscaler...")
                # Upscale using the model
                with torch.no_grad():
                    upscaled = upscale_model(img_tensor)
                
                # Convert back to PIL
                upscaled = upscaled.squeeze(0).permute(1, 2, 0).cpu().numpy()
                upscaled = np.clip(upscaled * 255, 0, 255).astype(np.uint8)
                image = Image.fromarray(upscaled)
                
                # If we need more scaling, do it with selected method
                if scale_factor > 4.0:
                    final_scale = scale_factor / 4.0
                    new_width = int(image.width * final_scale)
                    new_height = int(image.height * final_scale)
                    log_message(f"Additional scaling to {new_width}x{new_height} (scale factor: {final_scale})")
                    image = image.resize((new_width, new_height), self._get_resize_method(resize_method))
            else:
                # Simple resize without upscaler
                new_width = int(width * scale_factor)
                new_height = int(height * scale_factor)
                log_message(f"Simple resize to {new_width}x{new_height} using {resize_method} method (scale factor: {scale_factor})")
                image = image.resize((new_width, new_height), self._get_resize_method(resize_method))
        else:
            log_message("Image is within size limits, no processing needed")
        
        log_message(f"Final image size: {image.size}")
        return image
    
    def _get_resize_method(self, method):
        """Convert string resize method to PIL Resampling enum"""
        methods = {
            "lanczos": Image.Resampling.LANCZOS,
            "bicubic": Image.Resampling.BICUBIC,
            "bilinear": Image.Resampling.BILINEAR,
            "nearest": Image.Resampling.NEAREST
        }
        return methods.get(method.lower(), Image.Resampling.LANCZOS)

class ImageSizeProcessorNode:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image": ("IMAGE",),
                "max_dimension": (list(SD_DIMENSIONS.keys()), {"default": "SDXL - Square (1024x1024)"}),
                "min_dimension": (list(SD_DIMENSIONS.keys()), {"default": "SD 1.x - Square (512x512)"}),
                "upscale_model": ("UPSCALE_MODEL", {"default": None}),
                "auto_select": ("BOOLEAN", {"default": False}),
                "use_upscaler": ("BOOLEAN", {"default": True}),
                "resize_method": (["lanczos", "bicubic", "bilinear", "nearest"], {"default": "lanczos"}),
                "scale_factor": ("FLOAT", {"default": 2.0, "min": 1.0, "max": 8.0, "step": 0.1}),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "process"
    CATEGORY = "cyan-image"
    BACKGROUND_COLOR = "#00FFFF"  # Cyan color
    
    def process(self, image, max_dimension, min_dimension, upscale_model, auto_select, use_upscaler, resize_method, scale_factor):
        log_message(f"Processing batch of {len(image)} images")
        processor = ImageSizeProcessor()
        
        # Set dimensions
        processor.max_pixels = SD_DIMENSIONS[max_dimension]
        processor.min_pixels = SD_DIMENSIONS[min_dimension]
        
        # Process each image in the batch
        processed_images = []
        for i, img in enumerate(image):
            if auto_select:
                # Convert to PIL Image to get dimensions
                if isinstance(img, torch.Tensor):
                    pil_img = Image.fromarray((img.cpu().numpy() * 255).astype(np.uint8))
                    width, height = pil_img.size
                    selected_dimension = get_dimension_from_aspect_ratio(width, height)
                    log_message(f"Auto-selected dimension: {selected_dimension}")
                    processor.max_pixels = SD_DIMENSIONS[selected_dimension]
            
            log_message(f"Processing image {i+1}/{len(image)}")
            processed = processor.process_image(img, upscale_model if use_upscaler else None, resize_method, scale_factor)
            processed_images.append(np.array(processed))
        
        # Convert to tensor
        processed_tensor = torch.from_numpy(np.stack(processed_images)).float() / 255.0
        return (processed_tensor,)

# Register the node
NODE_CLASS_MAPPINGS = {
    "ImageSizeProcessor": ImageSizeProcessorNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImageSizeProcessor": "Image Size Processor"
} 