// web/comfyui/youtube_thumbnail_extractor.js
(function() {
    // Wait for ComfyUI to be ready
    if (typeof app === 'undefined' || !app.ui) {
        setTimeout(arguments.callee, 500);
        return;
    }

    // Patch the node UI rendering for YouTubeThumbnailExtractor
    const origRender = app.ui.renderNodeInputs;
    app.ui.renderNodeInputs = function(node, ...args) {
        origRender.call(this, node, ...args);
        if (node.type === 'YouTubeThumbnailExtractor') {
            // Find the URL input
            const urlInput = node.el.querySelector('input[type="text"]');
            if (urlInput && !urlInput._clipboardButtonAdded) {
                // Create the button
                const pasteBtn = document.createElement('button');
                pasteBtn.textContent = 'Paste from Clipboard';
                pasteBtn.style.marginLeft = '8px';
                pasteBtn.onclick = async () => {
                    try {
                        const text = await navigator.clipboard.readText();
                        urlInput.value = text;
                        urlInput.dispatchEvent(new Event('input', { bubbles: true }));
                    } catch (err) {
                        alert('Failed to read clipboard: ' + err);
                    }
                };
                urlInput.parentNode.insertBefore(pasteBtn, urlInput.nextSibling);
                urlInput._clipboardButtonAdded = true;
            }
        }
    };
})(); 