(function () {
    "use strict";

    // ── DOM refs ──────────────────────────────────────────────────────────────
    const dropZone      = document.getElementById("drop-zone");
    const fileInput     = document.getElementById("file-input");
    const preview       = document.getElementById("preview");
    const dropHint      = document.getElementById("drop-hint");
    const instruction   = document.getElementById("instruction");
    const submitBtn     = document.getElementById("submit-btn");
    const statusEl      = document.getElementById("status");
    const reasoningBlock= document.getElementById("reasoning-block");
    const reasoningJson = document.getElementById("reasoning-json");
    const resultSection = document.getElementById("result-section");
    const beforeImg     = document.getElementById("before-img");
    const afterImg      = document.getElementById("after-img");

    let selectedFile = null;

    // ── File selection ────────────────────────────────────────────────────────
    dropZone.addEventListener("click", () => fileInput.click());

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        const file = e.dataTransfer.files[0];
        if (file) loadFile(file);
    });

    fileInput.addEventListener("change", () => {
        if (fileInput.files[0]) loadFile(fileInput.files[0]);
    });

    function loadFile(file) {
        if (!file.type.startsWith("image/")) {
            showStatus("Please select an image file.", true);
            return;
        }
        selectedFile = file;

        // Show preview immediately; set before-img src so it's ready after edit
        const objectUrl = URL.createObjectURL(file);
        preview.src = objectUrl;
        preview.hidden = false;
        dropHint.hidden = true;
        beforeImg.src = objectUrl;

        hideStatus();
    }

    // ── Submit ────────────────────────────────────────────────────────────────
    submitBtn.addEventListener("click", async () => {
        if (!selectedFile) {
            showStatus("Please select an image first.", true);
            return;
        }
        const instructionText = instruction.value.trim();
        if (!instructionText) {
            showStatus("Please enter an edit instruction.", true);
            return;
        }

        // Disable UI while running
        submitBtn.disabled = true;
        resultSection.hidden = true;
        reasoningBlock.hidden = true;
        showStatus("Analysing and editing\u2026 this may take ~20\u202fs", false);

        const formData = new FormData();
        formData.append("image", selectedFile);
        formData.append("instruction", instructionText);

        try {
            const response = await fetch("/edit", {
                method: "POST",
                body: formData,
            });

            if (!response.ok) {
                let detail = `HTTP ${response.status}`;
                try {
                    const errBody = await response.json();
                    if (errBody.detail) detail += `: ${errBody.detail}`;
                } catch (_) { /* ignore parse error */ }
                showStatus(detail, true);
                return;
            }

            const data = await response.json();

            // Populate reasoning block
            reasoningJson.textContent = JSON.stringify(data.analysis, null, 2);
            reasoningBlock.hidden = false;
            // Leave open state to user — do NOT set reasoningBlock.open

            // Populate after image
            afterImg.src = data.edited_image;

            // Show result panel
            resultSection.hidden = false;
            hideStatus();

        } catch (err) {
            showStatus(`Network error: ${err.message}`, true);
        } finally {
            submitBtn.disabled = false;
        }
    });

    // ── Helpers ───────────────────────────────────────────────────────────────
    function showStatus(message, isError) {
        statusEl.textContent = message;
        statusEl.hidden = false;
        if (isError) {
            statusEl.classList.add("error");
        } else {
            statusEl.classList.remove("error");
        }
    }

    function hideStatus() {
        statusEl.hidden = true;
        statusEl.textContent = "";
        statusEl.classList.remove("error");
    }
})();
