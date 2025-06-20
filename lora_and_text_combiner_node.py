class LoraAndTextCombinerNode:
    MAX_PAIRS = 3

    @classmethod
    def INPUT_TYPES(cls):
        required_inputs = {}
        optional_inputs = {}
        for i in range(1, cls.MAX_PAIRS + 1):
            optional_inputs[f"toggle_{i}"] = ("BOOLEAN", {"default": True, "label_on": "Enabled", "label_off": "Disabled"})
            optional_inputs[f"text_{i}"] = ("STRING", {"forceInput": True})
            optional_inputs[f"lora_stack_{i}"] = ("LORA_STACK",)

        return {
            "required": required_inputs,
            "optional": optional_inputs
        }

    RETURN_TYPES = ("STRING", "LORA_STACK",)
    RETURN_NAMES = ("combined_text", "combined_lora_stack",)
    FUNCTION = "combine"
    CATEGORY = "Custom Nodes/Combiners"

    def combine(self, **kwargs):
        texts = []
        final_lora_stack = []

        for i in range(1, self.MAX_PAIRS + 1):
            # Check if the toggle for this pair is enabled
            if kwargs.get(f"toggle_{i}", True):
                # Append text if it exists
                text = kwargs.get(f"text_{i}")
                if text:
                    texts.append(str(text))

                # Extend LORA stack if it exists
                lora_stack = kwargs.get(f"lora_stack_{i}")
                if lora_stack:
                    final_lora_stack.extend(lora_stack)

        combined_text = ", ".join(texts)
        return (combined_text, final_lora_stack if final_lora_stack else None,)

NODE_CLASS_MAPPINGS = {
    "LoraAndTextCombiner": LoraAndTextCombinerNode
}
NODE_DISPLAY_NAME_MAPPINGS = {
    "LoraAndTextCombiner": "Lora and Text Combiner"
} 