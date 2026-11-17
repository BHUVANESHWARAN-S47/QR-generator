from __future__ import annotations

import re
import secrets
import os
from pathlib import Path

import cv2
import numpy as np
import qrcode
from flask import Flask, jsonify, render_template, request, send_from_directory
from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_L, ERROR_CORRECT_M, ERROR_CORRECT_Q
from werkzeug.utils import secure_filename


BASE_DIR = Path(__file__).resolve().parent
GENERATED_DIR = BASE_DIR / "generated_qr"
GENERATED_DIR.mkdir(exist_ok=True)

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024

ERROR_CORRECTION = {
    "L": ERROR_CORRECT_L,
    "M": ERROR_CORRECT_M,
    "Q": ERROR_CORRECT_Q,
    "H": ERROR_CORRECT_H,
}
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{6}$")
MAX_DATA_LENGTH = 2_953


def valid_color(value: str) -> bool:
    return bool(HEX_COLOR.fullmatch(value or ""))


def create_qr_image(data: str, size: int, foreground: str, background: str, correction: str):
    qr = qrcode.QRCode(
        version=None,
        error_correction=ERROR_CORRECTION[correction],
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    return qr.make_image(fill_color=foreground, back_color=background).convert("RGB")


@app.get("/")
def home():
    return render_template("index.html")


@app.post("/generate")
def generate():
    payload = request.get_json(silent=True) or request.form
    data = str(payload.get("data", "")).strip()
    if not data:
        return jsonify(error="Please enter information before generating a QR code."), 400
    if len(data) > MAX_DATA_LENGTH:
        return jsonify(error=f"Input is too long. Please keep it under {MAX_DATA_LENGTH} characters."), 400

    try:
        size = int(payload.get("size", 10))
    except (TypeError, ValueError):
        return jsonify(error="QR code size must be a whole number."), 400
    foreground = str(payload.get("foreground", "#000000"))
    background = str(payload.get("background", "#ffffff"))
    correction = str(payload.get("correction", "M")).upper()

    if not 4 <= size <= 20:
        return jsonify(error="QR code size must be between 4 and 20."), 400
    if not valid_color(foreground) or not valid_color(background):
        return jsonify(error="Please provide valid six-digit colors."), 400
    if correction not in ERROR_CORRECTION:
        return jsonify(error="Invalid error correction level."), 400
    if foreground.lower() == background.lower():
        return jsonify(error="Foreground and background colors must be different."), 400

    filename = f"qr_{secrets.token_urlsafe(12)}.png"
    try:
        image = create_qr_image(data, size, foreground, background, correction)
        image.save(GENERATED_DIR / filename, format="PNG")
    except (OSError, ValueError) as exc:
        app.logger.error("QR image generation failed: %s", exc)
        return jsonify(error="The QR code could not be generated. Please try again."), 500

    return jsonify(
        filename=filename,
        preview_url=f"/generated_qr/{filename}",
        download_url=f"/download/{filename}",
        data=data,
        correction=correction,
    )


@app.get("/download/<filename>")
def download(filename: str):
    safe_name = secure_filename(filename)
    if safe_name != filename or not safe_name.endswith(".png"):
        return jsonify(error="Invalid file name."), 400
    file_path = GENERATED_DIR / safe_name
    if not file_path.is_file():
        return jsonify(error="QR code file not found."), 404
    return send_from_directory(GENERATED_DIR, safe_name, as_attachment=True, download_name="qr_code.png")


@app.get("/generated_qr/<filename>")
def generated_image(filename: str):
    safe_name = secure_filename(filename)
    if safe_name != filename or not safe_name.endswith(".png"):
        return jsonify(error="Invalid file name."), 400
    return send_from_directory(GENERATED_DIR, safe_name)


@app.post("/scan")
def scan():
    uploaded = request.files.get("qr_image")
    if uploaded is None or not uploaded.filename:
        return jsonify(error="Please choose a QR code image to scan."), 400
    if not (uploaded.mimetype or "").startswith("image/"):
        return jsonify(error="Please upload a valid image file."), 400

    raw_image = uploaded.read()
    image = cv2.imdecode(np.frombuffer(raw_image, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        return jsonify(error="The uploaded file is not a readable image."), 400

    decoded, _, _ = cv2.QRCodeDetector().detectAndDecode(image)
    if not decoded:
        return jsonify(error="No readable QR code was found in that image."), 422
    return jsonify(data=decoded)


@app.errorhandler(413)
def request_too_large(_error):
    return jsonify(error="The uploaded image is too large. Maximum size is 5 MB."), 413


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
