import torch
import numpy as np
from PIL import Image
import folder_paths

class ImagePreviewCompare:
    mode = "overlay"  # Class variable to track current mode
    
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "mode": (["overlay", "split"], {"default": "overlay"}),
            },
            "optional": {
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
                "line_color": (["white", "black"], {"default": "white"}),
                "glow_intensity": ("FLOAT", {
                    "default": 0.3,
                    "min": 0.0,
                    "max": 1.0,
                    "step": 0.01,
                    "display": "slider"
                })
            }
        }
    
    def __init__(self):
        self.split_position = 0.5
        self.opacity = 0.5
    
    RETURN_TYPES = ("IMAGE",)
    FUNCTION = "preview_compare"
    CATEGORY = "cyan-image"
    
    def resize_image(self, image, target_height, target_width):
        # Convert tensor to PIL Image
        if isinstance(image, torch.Tensor):
            # Handle batch dimension
            if len(image.shape) == 4:
                image = image[0]  # Take first image from batch
            image = (image.cpu().numpy() * 255).astype(np.uint8)
            image = Image.fromarray(image)
        
        # Resize image
        resized = image.resize((target_width, target_height), Image.Resampling.LANCZOS)
        
        # Convert back to tensor
        resized = np.array(resized).astype(np.float32) / 255.0
        resized = torch.from_numpy(resized).unsqueeze(0)  # Add batch dimension
        return resized
    
    def preview_compare(self, image1, image2, mode, opacity=0.5, split_position=0.5, line_color="white", glow_intensity=0.3):
        # Update the mode
        self.__class__.mode = mode
        
        # Get dimensions
        batch_size1, height1, width1, channels1 = image1.shape
        batch_size2, height2, width2, channels2 = image2.shape
        
        # Check if dimensions are different
        if height1 != height2 or width1 != width2:
            print(f"Resizing processed image from {width1}x{height1} to {width2}x{height2}")
            # Resize image1 to match image2's dimensions
            image1 = self.resize_image(image1, height2, width2)
        
        if mode == "overlay":
            # Overlay mode: blend images based on opacity
            result = image1 * (1 - opacity) + image2 * opacity
        else:
            # Split view mode: combine images with a vertical split
            batch_size, height, width, channels = image2.shape  # Use image2's dimensions
            split_x = int(width * split_position)
            
            # Create a copy of image1
            result = image1.clone()
            
            # Replace the right portion with image2
            result[:, :, split_x:] = image2[:, :, split_x:]
            
            # Create glow effect
            glow_width = 6  # Width of the glow effect
            line_width = 2  # Width of the solid line
            
            # Create a gradient for the glow
            x = torch.arange(-glow_width, glow_width + 1, device=result.device)
            glow = torch.exp(-(x ** 2) / (2 * (glow_width/2) ** 2))  # Gaussian distribution
            glow = glow / glow.max()  # Normalize to 0-1
            glow = glow * glow_intensity  # Apply intensity
            
            # Create the glow mask
            glow_mask = torch.zeros((height, width), device=result.device)
            for i, g in enumerate(glow):
                pos = split_x - glow_width + i
                if 0 <= pos < width:
                    glow_mask[:, pos] = g
            
            # Set line color based on selection
            line_color_value = torch.tensor([1.0, 1.0, 1.0], device=result.device) if line_color == "white" else torch.tensor([0.0, 0.0, 0.0], device=result.device)
            
            # Apply glow effect
            for c in range(channels):  # Apply to each color channel
                result[:, :, :, c] = torch.where(
                    glow_mask.unsqueeze(0) > 0,
                    torch.lerp(result[:, :, :, c], line_color_value[c], glow_mask.unsqueeze(0)),
                    result[:, :, :, c]
                )
            
            # Add the solid line
            result[:, :, split_x-line_width//2:split_x+line_width//2] = line_color_value
        
        # Convert the result to a PIL Image for display
        if isinstance(result, torch.Tensor):
            # Take the first image from the batch
            img = result[0].cpu().numpy()
            # Convert from [0,1] to [0,255] range
            img = (img * 255).astype(np.uint8)
            return (result, {"ui": {"images": [Image.fromarray(img)]}})
        
        return (result, {"ui": {}})

# Register the node
NODE_CLASS_MAPPINGS = {
    "ImagePreviewCompare": ImagePreviewCompare
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagePreviewCompare": "Image Preview Compare"
} 