import torch
import numpy as np
from PIL import Image
import folder_paths

class ImagePreviewCompare:
    def __init__(self):
        self.mode = "overlay"  # "overlay" or "split"
        self.split_position = 0.5  # 0.0 to 1.0
        self.opacity = 0.5  # 0.0 to 1.0
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "mode": (["overlay", "split"], {"default": "overlay"}),
                "opacity": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
                "split_position": ("FLOAT", {
                    "default": 0.5,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                }),
            },
        }
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "preview_compare"
    CATEGORY = "image/preview"
    
    def preview_compare(self, image1, image2, mode, opacity, split_position):
        # Ensure both images have the same dimensions
        if image1.shape != image2.shape:
            raise ValueError("Both images must have the same dimensions")
        
        # Store the current settings
        self.mode = mode
        self.opacity = opacity
        self.split_position = split_position
        
        if mode == "overlay":
            # Overlay mode: blend images based on opacity
            result = image1 * (1 - opacity) + image2 * opacity
            return (result,)
        else:
            # Split view mode: combine images with a vertical split
            height, width = image1.shape[1:3]
            split_x = int(width * split_position)
            
            # Create a copy of image1
            result = image1.clone()
            
            # Replace the right portion with image2
            result[:, :, split_x:] = image2[:, :, split_x:]
            
            # Add a vertical line at the split position
            line_width = 2
            line_color = torch.tensor([1.0, 0.0, 0.0], device=result.device)  # Red line
            result[:, :, split_x-line_width//2:split_x+line_width//2] = line_color
            
            return (result,)

# Register the node
NODE_CLASS_MAPPINGS = {
    "ImagePreviewCompare": ImagePreviewCompare
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagePreviewCompare": "Image Preview Compare"
} 