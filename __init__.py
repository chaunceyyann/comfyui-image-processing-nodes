from .image_preview_compare import ImagePreviewCompare
from .image_size_processor import ImageSizeProcessorNode
from .youtube_thumbnail_extractor import YouTubeThumbnailExtractor
from .random_person_photo import RandomPersonPhoto
from .toggle_text_node import ToggleTextNode
from .toggle_lora_stack_node import ToggleLoraStackNode
from .lora_and_text_combiner_node import LoraAndTextCombinerNode
from .character_loader_node import CharacterLoaderNode
import os

# Get the absolute path to the web directory
current_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(current_dir, "web/comfyui")

print(f"Custom node directory: {current_dir}")
print(f"Web directory: {web_dir}")
print(f"Web directory exists: {os.path.exists(web_dir)}")
if os.path.exists(web_dir):
    print(f"Web files: {os.listdir(web_dir)}")

NODE_CLASS_MAPPINGS = {
    "ImagePreviewCompare": ImagePreviewCompare,
    "ImageSizeProcessor": ImageSizeProcessorNode,
    "YouTubeThumbnailExtractor": YouTubeThumbnailExtractor,
    "RandomPersonPhoto": RandomPersonPhoto,
    "ToggleTextNode": ToggleTextNode,
    "ToggleLoraStackNode": ToggleLoraStackNode,
    "LoraAndTextCombiner": LoraAndTextCombinerNode,
    "CharacterLoaderNode": CharacterLoaderNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "ImagePreviewCompare": "Image Preview Compare",
    "ImageSizeProcessor": "Image Size Processor",
    "YouTubeThumbnailExtractor": "YouTube Thumbnail Extractor",
    "RandomPersonPhoto": "Random Person Photo",
    "ToggleTextNode": "Toggle Text",
    "ToggleLoraStackNode": "Toggle Lora Stack",
    "LoraAndTextCombiner": "Lora and Text Combiner",
    "CharacterLoaderNode": "Character Loader",
}

# Register web directory for JavaScript files
WEB_DIRECTORY = "./web/comfyui"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"] 