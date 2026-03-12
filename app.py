import os
import uuid
import json
import io
import base64
import socket
import qrcode
from flask import (
    Flask, request, render_template,
    send_from_directory, jsonify, abort
)
from werkzeug.utils import secure_filename

app = Flask(__name__)


def get_icon(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    icons = {
        ".pdf": "📄", ".doc": "📝", ".docx": "📝", ".xls": "📊",
        ".xlsx": "📊", ".ppt": "📋", ".pptx": "📋",
        ".zip": "🗜", ".rar": "🗜", ".tar": "🗜", ".gz": "🗜",
        ".jpg": "🖼", ".jpeg": "🖼", ".png": "🖼", ".gif": "🖼",
        ".svg": "🖼", ".webp": "🖼",
        ".mp4": "🎬", ".mov": "🎬", ".avi": "🎬", ".mkv": "🎬",
        ".mp3": "🎵", ".wav": "🎵", ".flac": "🎵", ".ogg": "🎵",
        ".py": "🐍", ".js": "📜", ".ts": "📜", ".html": "🌐",
        ".css": "🎨", ".json": "📋", ".csv": "📊",
        ".txt": "📃", ".md": "📃",
    }
    return icons.get(ext, "📁")

app.jinja_env.globals["get_icon"] = get_icon

# ── Config ──────────────────────────────────────────────────────────────
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR  = os.path.join(BASE_DIR, "uploads")
META_FILE   = os.path.join(BASE_DIR, "metadata.json")
MAX_MB      = 100
app.config["MAX_CONTENT_LENGTH"] = MAX_MB * 1024 * 1024

os.makedirs(UPLOAD_DIR, exist_ok=True)


# ── Metadata helpers ─────────────────────────────────────────────────────
def load_meta() -> dict:
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            return json.load(f)
    return {}


def save_meta(data: dict):
    with open(META_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Utilities ────────────────────────────────────────────────────────────
def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


def make_qr_b64(url: str) -> str:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=8,
        border=3,
    )
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0a0a0f", back_color="#f0f4ff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()


def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"


# ── Routes ───────────────────────────────────────────────────────────────
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload():
    file = request.files.get("file")
    description = request.form.get("description", "").strip()[:200]

    if not file or file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    original_name = secure_filename(file.filename)
    file_id       = uuid.uuid4().hex
    ext           = os.path.splitext(original_name)[1]
    stored_name   = f"{file_id}{ext}"
    save_path     = os.path.join(UPLOAD_DIR, stored_name)

    file.save(save_path)
    size = os.path.getsize(save_path)

    meta = load_meta()
    meta[file_id] = {
        "original_name": original_name,
        "stored_name":   stored_name,
        "description":   description,
        "size":          size,
        "size_human":    human_size(size),
    }
    save_meta(meta)

    ip       = get_local_ip()
    port     = request.environ.get("SERVER_PORT", 5000)
    base_url = f"http://{ip}:{port}"
    dl_url   = f"{base_url}/d/{file_id}"
    qr_b64   = make_qr_b64(dl_url)

    return jsonify({
        "file_id":       file_id,
        "original_name": original_name,
        "description":   description,
        "size_human":    human_size(size),
        "download_url":  dl_url,
        "qr_b64":        qr_b64,
    })


@app.route("/d/<file_id>")
def download_page(file_id):
    meta = load_meta()
    if file_id not in meta:
        abort(404)
    info = meta[file_id]

    ip       = get_local_ip()
    port     = request.environ.get("SERVER_PORT", 5000)
    base_url = f"http://{ip}:{port}"
    dl_url   = f"{base_url}/d/{file_id}"
    qr_b64   = make_qr_b64(dl_url)

    return render_template(
        "download.html",
        info=info,
        file_id=file_id,
        qr_b64=qr_b64,
        dl_url=dl_url,
    )


@app.route("/d/<file_id>/file")
def download_file(file_id):
    meta = load_meta()
    if file_id not in meta:
        abort(404)
    info = meta[file_id]
    return send_from_directory(
        UPLOAD_DIR,
        info["stored_name"],
        as_attachment=True,
        download_name=info["original_name"],
    )


# ── Entry point ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    ip   = get_local_ip()
    port = 5000
    print(f"\n  ✦  FileShare running at  http://{ip}:{port}\n")
    app.run(host="0.0.0.0", port=port, debug=False)
