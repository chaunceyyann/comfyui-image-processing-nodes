import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

console.log("[ImagePreviewCompare] Script loaded");

class ImagePreviewCompareWidget {
    constructor(name, node) {
        console.log("[ImagePreviewCompare] Widget constructor called");
        this.name = name;
        this.node = node;
        this.type = 'custom';
        this.value = null;
        this.mouseDowned = null;
        this.isMouseDownedAndOver = false;
        this.hitAreas = {};
        this.downedHitAreasForMove = [];
    }

    createWidget() {
        const container = document.createElement("div");
        container.style.position = "relative";
        container.style.width = "100%";
        container.style.height = "300px";
        container.style.overflow = "hidden";
        container.style.borderRadius = "8px";
        container.style.marginTop = "8px";
        container.style.backgroundColor = "#1a1a1a"; // Dark background

        // Create containers for both images
        const imagesContainer = document.createElement("div");
        imagesContainer.style.position = "relative";
        imagesContainer.style.width = "100%";
        imagesContainer.style.height = "100%";
        imagesContainer.style.display = "flex"; // Use flexbox for layout
        container.appendChild(imagesContainer);

        // Background image container
        const image1Container = document.createElement("div");
        image1Container.style.position = "absolute";
        image1Container.style.top = "0";
        image1Container.style.left = "0";
        image1Container.style.width = "100%";
        image1Container.style.height = "100%";
        image1Container.style.backgroundSize = "contain";
        image1Container.style.backgroundPosition = "center";
        image1Container.style.backgroundRepeat = "no-repeat";
        image1Container.style.zIndex = "1";
        imagesContainer.appendChild(image1Container);

        // Overlay image container
        const image2Container = document.createElement("div");
        image2Container.style.position = "absolute";
        image2Container.style.top = "0";
        image2Container.style.left = "0";
        image2Container.style.width = "100%";
        image2Container.style.height = "100%";
        image2Container.style.backgroundSize = "contain";
        image2Container.style.backgroundPosition = "center";
        image2Container.style.backgroundRepeat = "no-repeat";
        image2Container.style.zIndex = "2";
        imagesContainer.appendChild(image2Container);

        // Split line
        const splitLine = document.createElement("div");
        splitLine.style.position = "absolute";
        splitLine.style.top = "0";
        splitLine.style.width = "2px";
        splitLine.style.height = "100%";
        splitLine.style.backgroundColor = "#fff";
        splitLine.style.cursor = "ew-resize";
        splitLine.style.zIndex = "3";
        splitLine.style.boxShadow = "0 0 5px rgba(255,255,255,0.5)";
        imagesContainer.appendChild(splitLine);

        // Guide lines for opacity mode
        const guideLines = document.createElement("div");
        guideLines.style.position = "absolute";
        guideLines.style.top = "0";
        guideLines.style.left = "0";
        guideLines.style.width = "100%";
        guideLines.style.height = "100%";
        guideLines.style.pointerEvents = "none";
        guideLines.style.display = "none";
        guideLines.style.zIndex = "3";
        imagesContainer.appendChild(guideLines);

        // Add horizontal guide lines
        for (let i = 0; i < 3; i++) {
            const line = document.createElement("div");
            line.style.position = "absolute";
            line.style.left = "0";
            line.style.width = "100%";
            line.style.height = "1px";
            line.style.backgroundColor = "rgba(255, 255, 255, 0.5)";
            line.style.top = `${(i + 1) * 25}%`;
            guideLines.appendChild(line);
        }

        // Add vertical guide lines
        for (let i = 0; i < 3; i++) {
            const line = document.createElement("div");
            line.style.position = "absolute";
            line.style.top = "0";
            line.style.height = "100%";
            line.style.width = "1px";
            line.style.backgroundColor = "rgba(255, 255, 255, 0.5)";
            line.style.left = `${(i + 1) * 25}%`;
            guideLines.appendChild(line);
        }

        // Store references
        this.container = container;
        this.imagesContainer = imagesContainer;
        this.image1Container = image1Container;
        this.image2Container = image2Container;
        this.splitLine = splitLine;
        this.guideLines = guideLines;

        // Initialize state
        this.mode = "split"; // or "opacity"
        this.splitPosition = 50; // percentage
        this.opacity = 0.5; // 0-1

        // Setup event listeners
        this.setupEventListeners();

        return container;
    }

    setupEventListeners() {
        let isDragging = false;
        let startX = 0;
        let startPosition = 0;

        const onMouseDown = (e) => {
            isDragging = true;
            startX = e.clientX;
            startPosition = this.mode === "split" ? this.splitPosition : this.opacity * 100;
            this.container.style.cursor = "ew-resize";
            e.preventDefault();
        };

        const onMouseMove = (e) => {
            if (!isDragging) return;

            const deltaX = e.clientX - startX;
            const containerWidth = this.imagesContainer.offsetWidth;
            const deltaPercent = (deltaX / containerWidth) * 100;

            if (this.mode === "split") {
                this.splitPosition = Math.max(0, Math.min(100, startPosition + deltaPercent));
                this.updateSplitView();
            } else {
                this.opacity = Math.max(0, Math.min(1, (startPosition + deltaPercent) / 100));
                this.updateOpacityView();
            }
        };

        const onMouseUp = () => {
            isDragging = false;
            this.container.style.cursor = "default";
        };

        this.splitLine.addEventListener("mousedown", onMouseDown);
        document.addEventListener("mousemove", onMouseMove);
        document.addEventListener("mouseup", onMouseUp);
    }

    updateSplitView() {
        this.splitLine.style.left = `${this.splitPosition}%`;
        this.image2Container.style.clipPath = `inset(0 ${100 - this.splitPosition}% 0 0)`;
        this.guideLines.style.display = "none";
        this.splitLine.style.display = "block";
        this.image2Container.style.opacity = "1";
    }

    updateOpacityView() {
        this.splitLine.style.display = "none";
        this.image2Container.style.clipPath = "none";
        this.image2Container.style.opacity = this.opacity;
        this.guideLines.style.display = "block";
    }

    setValue(value) {
        console.log("[ImagePreviewCompare] setValue called with:", value);
        this.value = value;
        if (!value) {
            console.log("[ImagePreviewCompare] No value provided");
            return;
        }

        const { images } = value;
        console.log("[ImagePreviewCompare] Images from value:", images);
        
        if (images && images.length >= 2) {
            console.log("[ImagePreviewCompare] Processing images:", {
                image1: images[0],
                image2: images[1]
            });
            
            try {
                // Get the image URLs from the PreviewImage data
                const image1Url = api.apiURL(`/view?filename=${encodeURIComponent(images[0].filename)}&type=${images[0].type}&subfolder=${encodeURIComponent(images[0].subfolder || '')}${app.getPreviewFormatParam()}${app.getRandParam()}`);
                const image2Url = api.apiURL(`/view?filename=${encodeURIComponent(images[1].filename)}&type=${images[1].type}&subfolder=${encodeURIComponent(images[1].subfolder || '')}${app.getPreviewFormatParam()}${app.getRandParam()}`);
                
                console.log("[ImagePreviewCompare] Generated URLs:", {
                    image1Url,
                    image2Url,
                    image1Data: images[0],
                    image2Data: images[1]
                });
                
                // Set background images
                this.image1Container.style.backgroundImage = `url(${image1Url})`;
                this.image2Container.style.backgroundImage = `url(${image2Url})`;
                
                // Force initial update
                if (this.mode === "split") {
                    this.updateSplitView();
                } else {
                    this.updateOpacityView();
                }
            } catch (error) {
                console.error("[ImagePreviewCompare] Error setting images:", error);
            }
        } else {
            console.log("[ImagePreviewCompare] Not enough images:", images);
        }
    }

    getValue() {
        return this.value;
    }

    show() {
        if (this.container) {
            this.container.style.display = "block";
        }
    }

    hide() {
        if (this.container) {
            this.container.style.display = "none";
        }
    }

    destroy() {
        if (this.container && this.container.parentNode) {
            this.container.parentNode.removeChild(this.container);
        }
        this.container = null;
    }
}

app.registerExtension({
    name: "Comfy.ImagePreviewCompare",
    async beforeRegisterNodeDef(nodeType, nodeData, app) {
        if (nodeData.name === "ImagePreviewCompare") {
            console.log("[ImagePreviewCompare] Registering node");
            
            // Log the original methods
            console.log("[ImagePreviewCompare] Original methods:", {
                hasOnNodeCreated: !!nodeType.prototype.onNodeCreated,
                hasOnExecuted: !!nodeType.prototype.onExecuted,
                hasExecute: !!nodeType.prototype.execute
            });
            
            // Store the original methods
            const originalOnNodeCreated = nodeType.prototype.onNodeCreated;
            const originalOnExecuted = nodeType.prototype.onExecuted;
            const originalExecute = nodeType.prototype.execute;

            // Override onNodeCreated
            nodeType.prototype.onNodeCreated = function() {
                console.log("[ImagePreviewCompare] Node created - START");
                const result = originalOnNodeCreated ? originalOnNodeCreated.apply(this) : undefined;
                
                const widget = new ImagePreviewCompareWidget("preview", this);
                console.log("[ImagePreviewCompare] Widget created", widget);
                this.previewWidget = widget;
                this.addCustomWidget(widget);
                console.log("[ImagePreviewCompare] Widget added to node", this.widgets);
                
                console.log("[ImagePreviewCompare] Node created - END");
                return result;
            };

            // Override onExecuted
            nodeType.prototype.onExecuted = function(message) {
                console.log("[ImagePreviewCompare] Node executed with message - START:", message);
                const result = originalOnExecuted ? originalOnExecuted.apply(this, arguments) : undefined;
                
                // Check if we have images in the message
                if (this.previewWidget) {
                    console.log("[ImagePreviewCompare] Widget exists, checking message:", {
                        messageKeys: Object.keys(message),
                        message: message
                    });
                    
                    // The message might contain an 'images' array directly or nested under ui
                    let images = null;
                    if (message.images && Array.isArray(message.images)) {
                        images = message.images;
                        console.log("[ImagePreviewCompare] Found images array directly:", images);
                    } else if (message.ui && message.ui.images && Array.isArray(message.ui.images)) {
                        images = message.ui.images;
                        console.log("[ImagePreviewCompare] Found images array in ui:", images);
                    }
                    
                    if (images) {
                        console.log("[ImagePreviewCompare] Setting images in widget", images);
                        this.previewWidget.setValue({ images: images });
                    } else {
                        console.log("[ImagePreviewCompare] No images array found in message");
                    }
                } else {
                    console.log("[ImagePreviewCompare] No widget available");
                }
                
                console.log("[ImagePreviewCompare] Node executed - END");
                return result;
            };

            // Override execute
            nodeType.prototype.execute = function() {
                console.log("[ImagePreviewCompare] Execute called");
                const result = originalExecute.apply(this, arguments);
                console.log("[ImagePreviewCompare] Execute result:", result);
                return result;
            };

            // Add a custom method to handle the preview
            nodeType.prototype.getExtraMenuOptions = function(graphCanvas, x, y) {
                return [
                    {
                        content: "Preview",
                        callback: () => {
                            console.log("[ImagePreviewCompare] Preview menu option clicked");
                            if (this.previewWidget) {
                                console.log("[ImagePreviewCompare] Widget exists, showing preview");
                                this.previewWidget.show();
                            }
                        }
                    }
                ];
            };
        }
    }
}); 