class ToggleLoraStackNode:
    MAX_PAIRS = 10

    @classmethod
    def INPUT_TYPES(cls):
        optional_inputs = {f"input_{i}": ("LORA_STACK",) for i in range(1, cls.MAX_PAIRS + 1)}
        return {
            "required": {
                "enabled": ("BOOLEAN", {"default": True}),
            },
            "optional": optional_inputs
        }

    RETURN_TYPES = tuple("LORA_STACK" for _ in range(10))
    RETURN_NAMES = tuple(f"output_{i}" for i in range(1, 10 + 1))
    FUNCTION = "process"
    CATEGORY = "Custom Nodes/Toggles"

    def process(self, enabled, **kwargs):
        outputs = []
        for i in range(1, self.MAX_PAIRS + 1):
            input_key = f"input_{i}"
            value = kwargs.get(input_key)
            outputs.append(value if enabled else None)
        return tuple(outputs)

NODE_CLASS_MAPPINGS = {
    "ToggleLoraStackNode": ToggleLoraStackNode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "ToggleLoraStackNode": "Toggle Lora Stack"
} 