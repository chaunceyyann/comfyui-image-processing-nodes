import cv2
import torch
import numpy as np
from nodes import PreviewImage
import folder_paths
import os

# Register videos folder
video_extensions = ['.mp4', '.avi', '.mov', '.mkv']
folder_paths.add_model_folder_path("videos", os.path.join(folder_paths.base_path, "videos"))
folder_paths.supported_pt_extensions.update(video_extensions)

class VideoThumbnailExtractor(PreviewImage):
    def __init__(self):
        super().__init__()
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "video": ("STRING", {"default": "", "multiline": False}),
                "frame_number": ("INT", {"default": 1, "min": 1, "step": 1}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "extract_thumbnail"
    CATEGORY = "cyan-image"
    OUTPUT_NODE = True
    BACKGROUND_COLOR = "#00FFFF"  # Cyan color

    def extract_thumbnail(self, video, frame_number=1, filename_prefix="video_thumbnail", prompt=None, extra_pnginfo=None):
        print(f"[VideoThumbnailExtractor] Processing video: {video}")
        
        # Get full path to video file
        video_path = os.path.join(folder_paths.base_path, "videos", video)
        if not os.path.exists(video_path):
            raise ValueError(f"Could not find video file: {video_path}")
        
        # Read the video using OpenCV
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")
        
        # Get total number of frames
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_number > total_frames:
            frame_number = total_frames
            print(f"[VideoThumbnailExtractor] Requested frame exceeds video length, using last frame: {frame_number}")
        
        # Set the frame position
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number - 1)
        
        # Read the frame
        ret, frame = cap.read()
        if not ret:
            cap.release()
            raise ValueError(f"Failed to read frame {frame_number} from video")
        
        cap.release()
        print(f"[VideoThumbnailExtractor] Frame {frame_number} extracted successfully")
        
        # Convert BGR (OpenCV format) to RGB
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        
        # Convert to tensor for ComfyUI
        frame_np = frame_rgb.astype(np.float32) / 255.0
        frame_tensor = torch.from_numpy(frame_np).unsqueeze(0)  # Shape: [1, height, width, channels]
        print(f"[VideoThumbnailExtractor] Thumbnail tensor shape: {frame_tensor.shape}")
        
        # Use PreviewImage's save_images method for UI display
        result = self.save_images(frame_tensor, filename_prefix, prompt, extra_pnginfo)
        print(f"[VideoThumbnailExtractor] Thumbnail saved and processed with PreviewImage")
        print(f"[VideoThumbnailExtractor] Save result: {result}")
        
        # Return both tensor for downstream nodes and UI result for display
        return {"ui": result.get("ui", {"images": []}), "result": (frame_tensor,)}

# Register the node
NODE_CLASS_MAPPINGS = {
    "VideoThumbnailExtractor": VideoThumbnailExtractor
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "VideoThumbnailExtractor": "Video Thumbnail Extractor"
}

print("[VideoThumbnailExtractor] Node registration complete") 