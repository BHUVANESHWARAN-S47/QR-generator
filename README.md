# QR Code Generator

A lightweight QR Code Generator web application built with Python, Flask, `qrcode`, Pillow, HTML, CSS, and vanilla JavaScript. It creates static QR codes containing the information entered by the user; no database or cloud service is required.

## Features

- Encode URLs, plain text, contact details, email addresses, phone numbers, and Wi-Fi information.
- Customize QR size, foreground/background colors, and error correction (`L`, `M`, `Q`, `H`).
- Preview and download generated PNG files with unique server-side filenames.
- Upload and decode an existing QR image.
- Live character counter, validation messages, loading state, reset/generate-again controls, and responsive neon-lime dark theme.
- Generated images are stored locally in `generated_qr/`.

## Installation and startup

```bash
pip install -r requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

OpenCV (`opencv-python-headless`) and NumPy are included only for the QR image scanning module. All QR generation and decoding happen locally.

## Project structure

```text
qr-code-generator/
├── app.py
├── requirements.txt
├── README.md
├── templates/index.html
├── static/css/style.css
├── static/js/script.js
└── generated_qr/.gitkeep
```

## Test checklist

Try these values: `https://www.google.com`, `Hello World`, `Test QR Generator 2026`, an email address, a phone number, text with special characters, Unicode text, and empty input. Verify the preview, PNG download, scan the downloaded PNG, color customization, all correction levels, and invalid input messages.
