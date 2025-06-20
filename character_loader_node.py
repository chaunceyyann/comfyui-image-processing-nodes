import os
import folder_paths
import json

class CharacterLoaderNode:
    """
    A node for loading character presets with text and two fixed LORA inputs.
    """
    
    @classmethod
    def INPUT_TYPES(cls):
        # Get available LORA files
        lora_files = folder_paths.get_filename_list("loras")
        lora_options = ["None"] + lora_files
        
        inputs = {
            "required": {
                "character_text": ("STRING", {"default": "", "multiline": True}),
                "enable_text": ("BOOLEAN", {"default": True, "label_on": "Text On", "label_off": "Text Off"}),
                "enable_lora": ("BOOLEAN", {"default": True, "label_on": "LORA On", "label_off": "LORA Off"}),
                "lora_name_1": (lora_options,),
                "lora_strength_1": ("FLOAT", {"default": 1.0, "min": -2.0, "max": 2.0, "step": 0.01}),
                "lora_name_2": (lora_options,),
                "lora_strength_2": ("FLOAT", {"default": 1.0, "min": -2.0, "max": 2.0, "step": 0.01}),
            },
        }
        
        return inputs

    RETURN_TYPES = ("STRING", "LORA_STACK")
    RETURN_NAMES = ("text_output", "lora_stack_output")
    FUNCTION = "load_character"
    CATEGORY = "Custom Nodes/Character"

    def load_character(self, character_text, enable_text, enable_lora, lora_name_1, lora_strength_1, lora_name_2, lora_strength_2):
        # Handle text output
        text_output = character_text if enable_text else ""
        
        # Handle LORA stack output
        lora_stack = []
        if enable_lora:
            if lora_name_1 != "None":
                lora_stack.append((lora_name_1, lora_strength_1, lora_strength_1))
            if lora_name_2 != "None":
                lora_stack.append((lora_name_2, lora_strength_2, lora_strength_2))
        
        return (text_output, lora_stack)

# Node mappings
NODE_CLASS_MAPPINGS = {
    "CharacterLoaderNode": CharacterLoaderNode
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "CharacterLoaderNode": "Character Loader"
} 