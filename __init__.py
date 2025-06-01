from .image_preview_compare import NODE_CLASS_MAPPINGS as preview_mappings
from .image_preview_compare import NODE_DISPLAY_NAME_MAPPINGS as preview_display_mappings
from .image_size_processor import NODE_CLASS_MAPPINGS as size_mappings
from .image_size_processor import NODE_DISPLAY_NAME_MAPPINGS as size_display_mappings

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

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS'] 