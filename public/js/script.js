const dataInput = document.querySelector("#data-input");
const charCount = document.querySelector("#char-count");
const generationMessage = document.querySelector("#generation-message");
const generateButton = document.querySelector("#generate-button");
const previewSection = document.querySelector("#preview-section");

function showMessage(element, text, type) {
  element.textContent = text;
  element.className = `message ${type}`;
}

function setLoading(loading) {
  generateButton.disabled = loading;
  generateButton.querySelector(".button-label").hidden = loading;
  generateButton.querySelector(".loader").hidden = !loading;
  generateButton.querySelector(".arrow").hidden = loading;
}

dataInput.addEventListener("input", () => {
  charCount.textContent = `${dataInput.value.length} / 2953`;
});

document.querySelector("#clear-input").addEventListener("click", () => {
  dataInput.value = "";
  dataInput.dispatchEvent(new Event("input"));
  dataInput.focus();
});

for (const id of ["foreground", "background"]) {
  const input = document.querySelector(`#${id}`);
  const value = document.querySelector(`#${id}-value`);
  input.addEventListener("input", () => { value.textContent = input.value.toUpperCase(); });
}

generateButton.addEventListener("click", async () => {
  const data = dataInput.value.trim();
  if (!data) {
    showMessage(generationMessage, "Please enter information before generating.", "error");
    dataInput.focus();
    return;
  }
  setLoading(true);
  generationMessage.textContent = "";
  try {
    const response = await fetch("/generate", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({
        data,
        size: document.querySelector("#size").value,
        correction: document.querySelector("#correction").value,
        foreground: document.querySelector("#foreground").value,
        background: document.querySelector("#background").value
      })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Generation failed.");
    document.querySelector("#qr-image").src = `${result.preview_url}?t=${Date.now()}`;
    document.querySelector("#download-button").href = result.download_url;
    document.querySelector("#preview-data").textContent = result.data;
    document.querySelector("#preview-correction").textContent = result.correction;
    previewSection.hidden = false;
    showMessage(generationMessage, "QR code generated successfully.", "success");
    previewSection.scrollIntoView({behavior: "smooth", block: "nearest"});
  } catch (error) {
    showMessage(generationMessage, error.message, "error");
  } finally {
    setLoading(false);
  }
});

document.querySelector("#generate-again").addEventListener("click", () => {
  previewSection.hidden = true;
  dataInput.focus();
  window.scrollTo({top: 0, behavior: "smooth"});
});

document.querySelector("#scan-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const scanMessage = document.querySelector("#scan-message");
  const resultBox = document.querySelector("#decoded-result");
  const file = document.querySelector("#qr-upload").files[0];
  if (!file) return;
  const formData = new FormData();
  formData.append("qr_image", file);
  showMessage(scanMessage, "Reading image...", "success");
  resultBox.hidden = true;
  try {
    const response = await fetch("/scan", {method: "POST", body: formData});
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not decode image.");
    document.querySelector("#decoded-data").textContent = result.data;
    resultBox.hidden = false;
    showMessage(scanMessage, "QR code decoded successfully.", "success");
  } catch (error) {
    showMessage(scanMessage, error.message, "error");
  }
});
