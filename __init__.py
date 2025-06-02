from .image_preview_compare import NODE_CLASS_MAPPINGS as preview_mappings
from .image_preview_compare import NODE_DISPLAY_NAME_MAPPINGS as preview_display_mappings
from .image_size_processor import NODE_CLASS_MAPPINGS as size_mappings
from .image_size_processor import NODE_DISPLAY_NAME_MAPPINGS as size_display_mappings
import os

# Get the absolute path to the web directory
current_dir = os.path.dirname(os.path.abspath(__file__))
web_dir = os.path.join(current_dir, "web/comfyui")

print(f"Custom node directory: {current_dir}")
print(f"Web directory: {web_dir}")
print(f"Web directory exists: {os.path.exists(web_dir)}")
if os.path.exists(web_dir):
    print(f"Web files: {os.listdir(web_dir)}")

# Combine all node mappings
NODE_CLASS_MAPPINGS = {
    **preview_mappings,
    **size_mappings
}

# Combine all display name mappings
NODE_DISPLAY_NAME_MAPPINGS = {
    **preview_display_mappings,
    **size_display_mappings
}

# Register web directory for JavaScript files
WEB_DIRECTORY = "./web/comfyui"

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY'] 