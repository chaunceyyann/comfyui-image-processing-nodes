import { app } from "../../scripts/app.js";

/**
 * Gets the number of visible dynamic inputs based on connections.
 * A slot is visible if it's connected, or it's the first unconnected slot.
 * @param {object} node The node instance.
 * @param {string} prefix The prefix for the dynamic inputs (e.g., "text_").
 * @param {number} maxCount The maximum number of inputs.
 * @returns {number} The number of inputs that should be visible.
 */
function getVisibleInputCount(node, prefix, maxCount) {
	let visible = 1;
	for (let i = 1; i <= maxCount; i++) {
		const inputName = `${prefix}${i}`;
		const input = node.inputs?.find((inp) => inp.name === inputName);
		if (input?.link != null) { // Check for not null/undefined
			visible = i + 1;
		}
	}
	return Math.min(visible, maxCount);
}

/**
 * Adds or removes inputs dynamically based on visibility.
 * @param {object} node The node instance.
 * @param {string} prefix The input prefix.
 * @param {number} maxCount The maximum number of inputs.
 * @param {string} type The ComfyUI type of the input.
 * @param {object} options Additional options for the input.
 */
function updateDynamicInputs(node, prefix, maxCount, type, options = {}) {
	const visibleCount = getVisibleInputCount(node, prefix, maxCount);

	for (let i = 1; i <= maxCount; i++) {
		const inputName = `${prefix}${i}`;
		const input = node.inputs?.find((inp) => inp.name === inputName);

		if (i <= visibleCount) {
			if (!input) {
				node.addInput(inputName, type, options);
			}
		} else {
			if (input && input.link == null) {
				node.removeInput(node.findInputSlot(inputName));
			}
		}
	}
}

/**
 * Gets the number of visible dynamic input/output pairs.
 * A pair is visible if its input or output is connected, or it's the first unconnected pair.
 * @param {object} node The node instance.
 * @param {string} inputPrefix The prefix for the dynamic inputs.
 * @param {string} outputPrefix The prefix for the dynamic outputs.
 * @param {number} maxCount The maximum number of pairs.
 * @returns {number} The number of pairs that should be visible.
 */
function getVisiblePairCount(node, inputPrefix, outputPrefix, maxCount) {
	let visible = 1;
	for (let i = 1; i <= maxCount; i++) {
		const inputName = `${inputPrefix}${i}`;
		const outputName = `${outputPrefix}${i}`;
		const input = node.inputs?.find((inp) => inp.name === inputName);
		const output = node.outputs?.find((out) => out.name === outputName);
		if (input?.link != null || output?.links?.length) {
			visible = i + 1;
		}
	}
	return Math.min(visible, maxCount);
}

/**
 * Adds or removes input/output pairs dynamically.
 * @param {object} node The node instance.
 * @param {string} inputPrefix The input prefix.
 * @param {string} outputPrefix The output prefix.
 * @param {number} maxCount The maximum number of pairs.
 * @param {string} type The ComfyUI type for the pair.
 * @param {object} options Additional options for the input.
 */
function updateDynamicPairs(node, inputPrefix, outputPrefix, maxCount, type, options = {}) {
	const visibleCount = getVisiblePairCount(node, inputPrefix, outputPrefix, maxCount);
	for (let i = 1; i <= maxCount; i++) {
		const inputName = `${inputPrefix}${i}`;
		const outputName = `${outputPrefix}${i}`;
		const input = node.inputs?.find((inp) => inp.name === inputName);
		const output = node.outputs?.find((out) => out.name === outputName);

		if (i <= visibleCount) {
			if (!input) node.addInput(inputName, type, options);
			if (!output) node.addOutput(outputName, type);
		} else {
			if (input && input.link == null) {
				node.removeInput(node.findInputSlot(inputName));
			}
			if (output && !output.links?.length) {
				const slot = node.findOutputSlot(outputName);
				if (slot !== -1) node.removeOutput(slot);
			}
		}
	}
}

/**
 * For LoraAndTextCombiner: Manages visibility of triads (toggle widget, text input, lora input).
 * A triad is visible if its text or lora input is connected, or it's the first unconnected triad.
 */
function updateCombinerNode(node) {
	let visibleCount = 1;
	const maxCount = 10;
	for (let i = 1; i <= maxCount; i++) {
		const textInput = node.inputs?.find((inp) => inp.name === `text_${i}`);
		const loraInput = node.inputs?.find((inp) => inp.name === `lora_stack_${i}`);
		if (textInput?.link != null || loraInput?.link != null) {
			visibleCount = i + 1;
		}
	}
	visibleCount = Math.min(visibleCount, maxCount);

	for (let i = 1; i <= maxCount; i++) {
		const toggleWidget = node.widgets?.find((w) => w.name === `toggle_${i}`);
		const textInput = node.inputs?.find((inp) => inp.name === `text_${i}`);
		const loraInput = node.inputs?.find((inp) => inp.name === `lora_stack_${i}`);

		const shouldBeVisible = i <= visibleCount;

		// Add/remove toggle widget
		if (shouldBeVisible) {
			if (!toggleWidget) {
				const widget = node.addWidget("toggle", `toggle_${i}`, true, () => {}, {
					on: "Enabled",
					off: "Disabled"
				});
				widget.name = `toggle_${i}`;
			}
			if (!textInput) node.addInput(`text_${i}`, "STRING", { forceInput: true });
			if (!loraInput) node.addInput(`lora_stack_${i}`, "LORA_STACK", {});
		} else {
			if (toggleWidget) {
				const widgetIndex = node.widgets.indexOf(toggleWidget);
				if (widgetIndex !== -1) {
					node.widgets.splice(widgetIndex, 1);
				}
			}
			if (textInput && textInput.link == null) {
				node.removeInput(node.findInputSlot(`text_${i}`));
			}
			if (loraInput && loraInput.link == null) {
				node.removeInput(node.findInputSlot(`lora_stack_${i}`));
			}
		}
	}
}

const nodeUpdateBehaviors = {
	"ToggleTextNode": (node) => {
		updateDynamicPairs(node, "input_", "output_", 10, "STRING", { forceInput: true });
	},
	"ToggleLoraStackNode": (node) => {
		updateDynamicPairs(node, "input_", "output_", 10, "LORA_STACK", {});
	},
	"LoraAndTextCombiner": (node) => {
		updateCombinerNode(node);
	},
};

app.registerExtension({
	name: "comfyui.dynamic_toggles",
	async beforeRegisterNodeDef(nodeType, nodeData, app) {
		// Handler for nodes that update based on input/output connections
		if (nodeData.name === "ToggleTextNode" || nodeData.name === "ToggleLoraStackNode") {
			const onConnectionsChange = nodeType.prototype.onConnectionsChange;
			nodeType.prototype.onConnectionsChange = function (type, index, connected, link_info) {
				const res = onConnectionsChange?.apply(this, arguments);
				if (nodeUpdateBehaviors[nodeData.name]) {
					nodeUpdateBehaviors[nodeData.name](this);
				}
				this.size = this.computeSize();
				return res;
			};

			const onNodeCreated = nodeType.prototype.onNodeCreated;
			nodeType.prototype.onNodeCreated = function () {
				const res = onNodeCreated?.apply(this, arguments);
				if (nodeUpdateBehaviors[nodeData.name]) {
					nodeUpdateBehaviors[nodeData.name](this);
				}
				this.size = this.computeSize();
				return res;
			};
		}
	}
}); 