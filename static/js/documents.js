/**
 * LegacyLens Document Upload
 * Handles drag-and-drop and file input upload to /api/documents/upload/
 */

(function () {
  "use strict";

  const dropZone    = document.getElementById("drop-zone");
  const fileInput   = document.getElementById("file-input");
  const progressWrap = document.getElementById("upload-progress");
  const progressBar = document.getElementById("progress-bar");
  const statusEl    = document.getElementById("upload-status");

  if (!dropZone) return;

  // Drag and drop handlers
  dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    dropZone.classList.add("drag-over");
  });

  dropZone.addEventListener("dragleave", () => {
    dropZone.classList.remove("drag-over");
  });

  dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("drag-over");
    const files = e.dataTransfer.files;
    if (files.length > 0) uploadFile(files[0]);
  });

  // File input change
  fileInput?.addEventListener("change", () => {
    if (fileInput.files.length > 0) uploadFile(fileInput.files[0]);
  });

  async function uploadFile(file) {
    const allowed = [".pdf", ".docx", ".md", ".txt"];
    const ext = "." + file.name.split(".").pop().toLowerCase();
    if (!allowed.includes(ext)) {
      showToast(`Unsupported file type: ${ext}. Allowed: PDF, DOCX, MD, TXT`, "error");
      return;
    }

    // Show progress
    if (progressWrap) progressWrap.style.display = "block";
    setProgress(10, `Uploading ${file.name}...`);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const xhr = new XMLHttpRequest();
      xhr.open("POST", "/api/documents/upload/");
      xhr.setRequestHeader("X-CSRFToken", getCsrfToken());

      xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
          const pct = Math.round((e.loaded / e.total) * 80) + 10;
          setProgress(pct, `Uploading... ${pct}%`);
        }
      };

      xhr.onload = () => {
        try {
          const data = JSON.parse(xhr.responseText);
          if (data.status === "ok") {
            setProgress(100, "Upload complete!");
            showToast(`Document "${data.data.title}" uploaded successfully.`, "success");
            // Reload after short delay to show new document
            setTimeout(() => location.reload(), 1500);
          } else {
            setProgress(0, "Upload failed");
            showToast("Upload failed: " + (data.message || "Unknown error"), "error");
          }
        } catch (e) {
          setProgress(0, "Parse error");
          showToast("Upload failed: unexpected server response", "error");
        }
      };

      xhr.onerror = () => {
        setProgress(0, "Network error");
        showToast("Upload failed: network error", "error");
      };

      xhr.send(formData);
    } catch (err) {
      setProgress(0, err.message);
      showToast("Upload error: " + err.message, "error");
    }
  }

  function setProgress(pct, message) {
    if (progressBar) progressBar.style.width = pct + "%";
    if (statusEl)    statusEl.textContent = message;
  }
})();

// Global delete function (called from onclick)
function deleteDocument(docId) {
  if (!confirm("Delete this document? This cannot be undone.")) return;

  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/api/documents/" + docId + "/delete/");
  xhr.setRequestHeader("X-CSRFToken", getCsrfToken());
  xhr.onload = function () {
    try {
      var data = JSON.parse(xhr.responseText);
      if (data.status === "ok") {
        var row = document.getElementById("doc-row-" + docId);
        if (row) row.remove();
        showToast(data.message || "Document deleted", "success");
      } else {
        showToast("Delete failed: " + (data.message || "Unknown error"), "error");
      }
    } catch (e) {
      console.error("Delete parse error:", e);
      showToast("Delete failed", "error");
    }
  };
  xhr.onerror = function () {
    showToast("Delete failed: network error", "error");
  };
  xhr.send();
}
