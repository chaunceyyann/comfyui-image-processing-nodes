from nodes import PreviewImage
import folder_paths

print("[ImagePreviewCompare] Loading node module")

class ImagePreviewCompare(PreviewImage):
    def __init__(self):
        print("[ImagePreviewCompare] Initializing node")
        super().__init__()
        self.mode = "overlay"
    
    @classmethod
    def INPUT_TYPES(s):
        print("[ImagePreviewCompare] Getting input types")
        return {
            "required": {
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "mode": (["overlay", "split"], {"default": "overlay"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "preview_compare"
    CATEGORY = "cyan-image"
    OUTPUT_NODE = True
    BACKGROUND_COLOR = "#00FFFF"  # Cyan color
    WEB_DIRECTORY = "./web/comfyui"
    
    def preview_compare(self, image1, image2, mode="overlay", opacity=0.5, split_position=0.5, split_line_color="white", split_line_glow=0.0, filename_prefix="preview_compare", prompt=None, extra_pnginfo=None):
        print(f"[ImagePreviewCompare] Starting preview_compare with mode: {mode}")
        print(f"[ImagePreviewCompare] Image1 shape: {image1.shape if image1 is not None else None}")
        print(f"[ImagePreviewCompare] Image2 shape: {image2.shape if image2 is not None else None}")
        
        # Update state
        self.mode = mode
        
        # Initialize result with empty images array
        result = {
            "images": []
        }
        
        # Save first image
        if image1 is not None and len(image1) > 0:
            print("[ImagePreviewCompare] Saving image1")
            image1_result = self.save_images(image1, filename_prefix + "_1", prompt, extra_pnginfo)
            print(f"[ImagePreviewCompare] Image1 save result: {image1_result}")
            if 'ui' in image1_result and 'images' in image1_result['ui']:
                result['images'].extend(image1_result['ui']['images'])
        
        # Save second image
        if image2 is not None and len(image2) > 0:
            print("[ImagePreviewCompare] Saving image2")
            image2_result = self.save_images(image2, filename_prefix + "_2", prompt, extra_pnginfo)
            print(f"[ImagePreviewCompare] Image2 save result: {image2_result}")
            if 'ui' in image2_result and 'images' in image2_result['ui']:
                result['images'].extend(image2_result['ui']['images'])
        
        print(f"[ImagePreviewCompare] Final result: {result}")
        return result

print("[ImagePreviewCompare] Registering node class")
# Register the node
NODE_CLASS_MAPPINGS = {
    "ImagePreviewCompare": ImagePreviewCompare
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagePreviewCompare": "Image Preview Compare"
}

print("[ImagePreviewCompare] Node registration complete") 