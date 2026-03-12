# 🧠 Code Explanation — File Sharing App
> **Project:** `file_sharing_using_flask`  
> **Stack:** Python · Flask · HTML · CSS · JavaScript  
> **Explained by:** Claude (Anthropic)

---

## 📋 Table of Contents

| # | Section |
|---|---------|
| 1 | [📦 Libraries Used](#-section-1--libraries-used) |
| 2 | [🐍 app.py — Line by Line](#-section-2--apppy-line-by-line) |
| 3 | [🌐 index.html — Upload Page](#-section-3--indexhtml--upload-page) |
| 4 | [⬇️ download.html — Download Page](#-section-4--downloadhtml--download-page) |
| 5 | [🚨 GitHub Push Problem & Fix](#-section-5--github-push-problem--fix) |
| 6 | [🔄 Full App Flow Summary](#-section-6--full-app-flow-summary) |

---

## 📦 Section 1 — Libraries Used

### 🔧 Python Standard Libraries *(built-in, no install needed)*

| Library | Purpose | Example |
|---------|---------|---------|
| `os` | File paths, folder creation, file sizes | `os.path.join("uploads", "file.pdf")` → works on Windows & Linux |
| `uuid` | Generate unique random IDs for each file | `uuid.uuid4().hex` → `"bdba8e9b69464126..."` |
| `json` | Read & write metadata to a `.json` file | `json.dump(data, f)` writes · `json.load(f)` reads |
| `io` | In-memory byte buffer (virtual file in RAM) | `io.BytesIO()` → holds the QR image without saving to disk |
| `base64` | Encode binary image data into plain text | `base64.b64encode(bytes).decode()` → `"iVBORw0KGgo..."` |
| `socket` | Detect local IP address automatically | `socket.socket(AF_INET, SOCK_DGRAM)` → creates a UDP socket |

### 📦 Third-Party Libraries *(install via `requirements.txt`)*

#### 🌶️ Flask
A lightweight web framework for Python. It handles everything web-related.

```python
from flask import Flask, request, render_template, send_from_directory, jsonify, abort
```

| Import | What it does |
|--------|-------------|
| `Flask` | Creates the web app instance |
| `request` | Reads incoming data — uploaded files, form fields |
| `render_template` | Loads an HTML file from `/templates/` and sends it |
| `send_from_directory` | Safely sends a file as a download attachment |
| `jsonify` | Converts a Python `dict` into a JSON HTTP response |
| `abort` | Triggers HTTP error pages like `404 Not Found` |

#### 🔒 Werkzeug
Flask uses this internally. We use one function from it:

```python
from werkzeug.utils import secure_filename
```

> Cleans up dangerous filenames before saving them.  
> Example: `secure_filename("../../evil.exe")` → `"evil.exe"` *(prevents path traversal attacks)*

#### 📱 qrcode
Generates QR code images from any URL or text string.

```python
qr = qrcode.QRCode(version=1, error_correction=ERROR_CORRECT_H, box_size=8, border=3)
```

| Setting | Meaning |
|---------|---------|
| `version=1` | Smallest QR size, auto-grows if needed |
| `ERROR_CORRECT_H` | QR still scans even if 30% is damaged/dirty |
| `box_size=8` | Each QR square = 8 pixels |
| `border=3` | 3-square white border around the QR |

#### 🖼️ Pillow
Python Imaging Library. We don't call it directly — `qrcode` uses it in the background when we call `qr.make_image()` to create the PNG.

---

## 🐍 Section 2 — `app.py` Line by Line

### Lines 1–12 · Imports

```python
import os, uuid, json, io, base64, socket
import qrcode
from flask import Flask, request, render_template, send_from_directory, jsonify, abort
from werkzeug.utils import secure_filename
```

Each import brings in a tool we need. Explained fully in Section 1 above.

---

### Line 14 · Create the Flask App

```python
app = Flask(__name__)
```

> `__name__` is Python's special variable holding the current module's name.  
> Passing it to Flask tells Flask **where to look** for the `templates/` folder and static files — relative to `app.py`'s location.

---

### Lines 17–33 · `get_icon()` Function

```python
def get_icon(filename: str) -> str:
    ext = os.path.splitext(filename)[1].lower()
    icons = { ".pdf": "📄", ".docx": "📝", ".zip": "🗜", ".mp4": "🎬", ... }
    return icons.get(ext, "📁")

app.jinja_env.globals["get_icon"] = get_icon
```

**Logic step by step:**
1. `os.path.splitext("report.PDF")` → returns `("report", ".PDF")`
2. `[1]` picks only the extension → `".PDF"`
3. `.lower()` → `".pdf"` *(lowercase for consistent matching)*
4. `icons.get(ext, "📁")` → looks up the emoji, returns `"📁"` if extension not found

**Last line — why it matters:**  
`app.jinja_env.globals["get_icon"] = get_icon` registers the Python function into Jinja2 (Flask's template engine), so we can call it directly inside HTML:
```html
{{ get_icon(info.original_name) }}
```

---

### Lines 36–42 · Configuration

```python
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
META_FILE  = os.path.join(BASE_DIR, "metadata.json")
MAX_MB     = 100
app.config["MAX_CONTENT_LENGTH"] = MAX_MB * 1024 * 1024
os.makedirs(UPLOAD_DIR, exist_ok=True)
```

| Line | Explanation |
|------|------------|
| `os.path.abspath(__file__)` | Full path of `app.py` → e.g. `C:/Projects/app.py` |
| `os.path.dirname(...)` | Strips the filename → `C:/Projects/` |
| `os.path.join(BASE_DIR, "uploads")` | Cross-platform path → works on Windows `\` and Linux `/` |
| `MAX_MB * 1024 * 1024` | `100 × 1024 × 1024 = 104,857,600 bytes` = 100 MB limit |
| `MAX_CONTENT_LENGTH` | Flask auto-rejects uploads larger than this with `413 Too Large` |
| `exist_ok=True` | Creates `uploads/` folder — won't crash if it already exists |

---

### Lines 46–55 · Metadata Helpers

```python
def load_meta() -> dict:
    if os.path.exists(META_FILE):
        with open(META_FILE, "r") as f:
            return json.load(f)
    return {}

def save_meta(data: dict):
    with open(META_FILE, "w") as f:
        json.dump(data, f, indent=2)
```

- **`load_meta()`** → Reads `metadata.json` into a Python dict. Returns `{}` on first run (file doesn't exist yet).
- **`save_meta()`** → Writes the dict back to `metadata.json`. `indent=2` makes it human-readable (pretty-printed).

---

### Lines 59–67 · `get_local_ip()` Function

```python
def get_local_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"
```

**The trick here:**
- `SOCK_DGRAM` = UDP — no real connection is made, no data is sent
- `s.connect(("8.8.8.8", 80))` → pretends to connect to Google's DNS
- This forces the OS to choose the correct network interface and fills in your local IP as the source address
- `s.getsockname()[0]` → returns just the IP part → `"192.168.1.9"`
- Falls back to `"127.0.0.1"` if no network is available

---

### Lines 70–82 · `make_qr_b64()` Function

```python
def make_qr_b64(url: str) -> str:
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_H, box_size=8, border=3)
    qr.add_data(url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0a0a0f", back_color="#f0f4ff")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return base64.b64encode(buf.getvalue()).decode()
```

**Step by step:**
1. `qr.add_data(url)` → feeds the URL into the QR encoder
2. `qr.make(fit=True)` → auto-selects size if `version=1` is too small
3. `qr.make_image(...)` → creates a PIL image with custom colors
4. `io.BytesIO()` → empty in-memory buffer (like a RAM file)
5. `img.save(buf, format="PNG")` → writes PNG bytes into RAM (not disk)
6. `buf.getvalue()` → reads all bytes from the buffer
7. `base64.b64encode(...).decode()` → converts bytes → Base64 string

**Why Base64?** So we can embed the image directly in HTML without a separate file:
```html
<img src="data:image/png;base64,iVBORw0KGgo..." />
```

---

### Lines 85–90 · `human_size()` Function

```python
def human_size(n: int) -> str:
    for unit in ("B", "KB", "MB", "GB"):
        if n < 1024:
            return f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} TB"
```

**Example trace:** `human_size(1536)`
- `1536 < 1024`? ❌ → `n = 1536 / 1024 = 1.5`
- `1.5 < 1024`? ✅ → returns `"1.5 KB"`

---

### Lines 94–96 · Home Route `"/"`

```python
@app.route("/")
def index():
    return render_template("index.html")
```

> The `@app.route("/")` decorator tells Flask: *"when someone visits `http://ip:5000/`, call `index()`"*.  
> `render_template` loads `templates/index.html` and sends it as the HTTP response.

---

### Lines 99–139 · Upload Route `"/upload"`

```python
@app.route("/upload", methods=["POST"])
def upload():
```

> `methods=["POST"]` → only accepts form submissions. A `GET` request here returns `405 Method Not Allowed`.

```python
file        = request.files.get("file")
description = request.form.get("description", "").strip()[:200]
```
- `request.files` → dict of uploaded files from the HTML form
- `.strip()` removes whitespace · `[:200]` caps at 200 characters

```python
original_name = secure_filename(file.filename)   # sanitize
file_id       = uuid.uuid4().hex                 # unique ID
ext           = os.path.splitext(original_name)[1]
stored_name   = f"{file_id}{ext}"               # e.g. "bdba8e9b...pdf"
```
> Storing with UUID name means **two users can upload `report.pdf`** without overwriting each other.

```python
file.save(save_path)
size = os.path.getsize(save_path)
```
> Saves file to disk, then reads its size in bytes.

```python
meta = load_meta()
meta[file_id] = { "original_name": ..., "description": ..., "size": ... }
save_meta(meta)
```
> Loads existing metadata → adds new entry → saves back to `metadata.json`.

```python
dl_url = f"http://{ip}:{port}/d/{file_id}"
qr_b64 = make_qr_b64(dl_url)
return jsonify({ "download_url": dl_url, "qr_b64": qr_b64, ... })
```
> Builds the download link with the real local IP, generates QR, returns everything as JSON to the browser's JavaScript.

---

### Lines 142–161 · Download Page Route `"/d/<file_id>"`

```python
@app.route("/d/<file_id>")
def download_page(file_id):
```

> `<file_id>` is a **URL variable** — Flask captures whatever is in that position and passes it as `file_id`.  
> Example: `/d/bdba8e9b...` → `file_id = "bdba8e9b..."`

```python
if file_id not in meta:
    abort(404)
```
> If the ID doesn't exist in metadata, the file doesn't exist → show 404.

```python
return render_template("download.html", info=info, qr_b64=qr_b64, dl_url=dl_url)
```
> Renders the download page, passing file info as template variables accessible in HTML as `{{ info.original_name }}`.

---

### Lines 164–175 · File Download Route `"/d/<file_id>/file"`

```python
return send_from_directory(
    UPLOAD_DIR,
    info["stored_name"],
    as_attachment=True,
    download_name=info["original_name"],
)
```

| Parameter | Effect |
|-----------|--------|
| `as_attachment=True` | Adds `Content-Disposition: attachment` header → browser **downloads** instead of displaying |
| `download_name=info["original_name"]` | Browser saves as `report.pdf`, not the UUID filename |

---

### Lines 179–183 · Entry Point

```python
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
```

| Setting | Meaning |
|---------|---------|
| `if __name__ == "__main__"` | Only runs when you do `python app.py`, not when imported as a module |
| `host="0.0.0.0"` | Listens on **all** network interfaces → other devices on Wi-Fi can connect |
| `host="127.0.0.1"` | Would only allow the same machine (localhost) |
| `debug=False` | Production-safe — `True` would auto-reload but exposes security risks |

---

## 🌐 Section 3 — `index.html` — Upload Page

### CSS Design System

```css
:root {
  --bg: #04050a;  --accent: #4f8eff;  --accent2: #00e5c0;
}
```
> CSS custom properties (variables). Change `--accent` once → updates the blue color everywhere on the page.

```css
body::before {
  background-image: linear-gradient(rgba(79,142,255,.04) 1px, transparent 1px), ...;
  pointer-events: none;
}
```
> The subtle dot-grid background. `pointer-events: none` means it doesn't block mouse clicks.

```css
.orb { filter: blur(120px); animation: float 12s infinite; }
```
> Large glowing circles in the background. `blur(120px)` makes them soft. The `float` keyframe gently moves them up and down endlessly.

```css
@keyframes slideUp {
  from { opacity: 0; transform: translateY(32px); }
  to   { opacity: 1; transform: translateY(0); }
}
```
> The card slides up + fades in on page load. `translateY(32px)` starts 32px below the final position.

```css
.dropzone input[type="file"] {
  position: absolute; inset: 0; opacity: 0;
}
```
> The real file input is **invisible** but covers the entire dropzone div. This is a classic trick — style a nice-looking div, hide the ugly default browser input on top of it. Clicking anywhere triggers the hidden input.

---

### JavaScript Logic

#### Step 1 — Drag & Drop

```javascript
dropzone.addEventListener('dragover', e => {
    e.preventDefault();                      // REQUIRED — without this, browser opens the file
    dropzone.classList.add('dragover');      // adds blue highlight CSS
});

dropzone.addEventListener('drop', e => {
    const f = e.dataTransfer.files[0];      // get the dropped file
    if (f) setFile(f);
});
```

#### Step 2 — `setFile(f)`

```javascript
function setFile(f) {
    selectedFile = f;                                        // store for later
    fileChosen.textContent = `✓ ${f.name} (${humanSize(f.size)})`;  // show filename
    fileChosen.style.display = 'block';
    uploadBtn.disabled = false;                             // enable the button
}
```

#### Step 3 — XHR Upload with Progress Bar

```javascript
const fd = new FormData();
fd.append('file', selectedFile);
fd.append('description', descEl.value.trim());
```
> `FormData` builds a multipart form in JavaScript. Flask reads these with `request.files.get('file')` and `request.form.get('description')`.

```javascript
// WHY XHR and not fetch()?
// XHR supports upload progress events. fetch() does NOT.
const xhr = new XMLHttpRequest();

xhr.upload.addEventListener('progress', e => {
    const pct = Math.round((e.loaded / e.total) * 100);  // e.loaded = bytes done, e.total = file size
    progressFill.style.width = pct + '%';                 // update progress bar
});
```

#### Step 4 — Show Result

```javascript
document.getElementById('qrImg').src = 'data:image/png;base64,' + d.qr_b64;
```
> Embeds the Base64 QR string as an inline image — **no separate image file needed**.

```javascript
result.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
```
> Smoothly scrolls the page so the result card is visible after upload.

#### Step 5 — Copy Link Button

```javascript
navigator.clipboard.writeText(url).then(() => {
    copyBtn.textContent = '✓';
    setTimeout(() => copyBtn.textContent = '⎘', 1500);  // restore icon after 1.5s
});
```

---

## ⬇️ Section 4 — `download.html` — Download Page

### Jinja2 Template Syntax

Flask uses **Jinja2** as its template engine — it lets you use Python variables inside HTML.

| Syntax | Meaning |
|--------|---------|
| `{{ info.original_name }}` | Outputs the value of `info["original_name"]` |
| `{% if info.description %}` | Only renders the block if description is not empty |
| `{% endif %}` | Ends the `if` block |
| `{{ get_icon(info.original_name) }}` | Calls the Python `get_icon()` function from HTML |

### Key Elements

```html
<img src="data:image/png;base64,{{ qr_b64 }}" />
```
> Embeds the QR code Base64 string directly — no external image file needed.

```html
<a href="/d/{{ file_id }}/file">Download</a>
```
> Links to Flask's `/d/<file_id>/file` route → triggers `send_from_directory` → file downloads.

---

## 🚨 Section 5 — GitHub Push Problem & Fix

### The Errors You Got

```
error: RPC failed; curl 55 Send failure: Connection was reset
error: RPC failed; HTTP 408 curl 22 The requested URL returned error: 408
```

There were **3 separate problems** happening at the same time:

---

### ❌ Problem 1 — `uploads/` folder was tracked by Git

When you ran `git add .` the **first time** (before creating `.gitignore`), Git included the test PDF you had uploaded — **21 MB** of binary data.

Pushing 21 MB over a slow connection caused:
- `curl 55` → TCP connection reset mid-transfer
- `HTTP 408` → GitHub's server timed out waiting

**✅ The Fix:**

```bash
# 1. Create .gitignore to tell Git what to ignore in future
echo uploads/ > .gitignore
echo metadata.json >> .gitignore

# 2. Un-track files Git already knows about
# --cached = remove from Git tracking but KEEP files on disk
git rm -r --cached uploads/
git rm --cached metadata.json
```

> ⚠️ Just adding `.gitignore` is NOT enough if Git already tracked the files.  
> You must use `git rm --cached` to remove them from the index.

---

### ❌ Problem 2 — Git's HTTP buffer was too small

Git has a default limit on data it buffers per HTTP transfer. 21 MB exceeded it.

**✅ The Fix:**

```bash
git config http.postBuffer 157286400
# 157,286,400 bytes = 150 MB (150 × 1024 × 1024)
```

---

### ❌ Problem 3 — `remote origin already exists`

You ran `git remote add origin <url>` twice. The second time Git complained.

**✅ This was harmless** — the remote was already correctly set from the first time.  
To change a remote URL in the future, use:

```bash
git remote set-url origin <new-url>   # use this instead of git remote add
```

---

### ✅ Reading the Successful Push Output

```
Writing objects: 100% (16/16), 21.22 MiB | 17.05 MiB/s, done.
* [new branch]      main -> main       ← SUCCESS
```

> Still 21 MB? Yes — because the PDF was in **Git's commit history** from the first attempt.  
> `git rm --cached` removes it going forward but doesn't erase old commits.

**🧹 Permanently erase it from history:**

```bash
git filter-branch --force --index-filter \
"git rm --cached --ignore-unmatch uploads/bdba8e9b69464126815a487cad8f4013.pdf" \
--prune-empty --tag-name-filter cat -- --all

git push origin main --force
```

---

### ⚠️ The LF/CRLF Warning

```
warning: LF will be replaced by CRLF in '.gitignore'
```

| | Line Ending | Used By |
|-|------------|---------|
| `LF` | `\n` | Unix / Linux / macOS |
| `CRLF` | `\r\n` | Windows |

Git on Windows auto-converts between them to keep repos cross-platform. **This is NOT an error.**

```bash
git config --global core.autocrlf true   # silence the warning permanently
```

---

## 🔄 Section 6 — Full App Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│  1. User opens http://192.168.1.9:5000                          │
│     └─ Flask serves index.html via the "/" route                │
│                                                                 │
│  2. User drops a file + types description → clicks Share File   │
│     └─ JS builds FormData → XHR POST to /upload                 │
│     └─ Progress bar updates via xhr.upload progress events      │
│                                                                 │
│  3. Flask /upload receives the file:                            │
│     └─ secure_filename() sanitizes the name                     │
│     └─ uuid4() generates a unique ID                            │
│     └─ File saved to uploads/<uuid>.ext                         │
│     └─ Metadata saved to metadata.json                          │
│     └─ QR code generated → Base64 encoded                       │
│     └─ JSON response returned to browser                        │
│                                                                 │
│  4. JavaScript receives JSON:                                   │
│     └─ Fills result card with filename, size, description       │
│     └─ Sets download link href                                  │
│     └─ Embeds QR as inline Base64 image                         │
│     └─ Smooth-scrolls to show result                            │
│                                                                 │
│  5. Recipient scans QR / visits link on another device          │
│     └─ Hits /d/<file_id>                                        │
│     └─ Flask looks up file in metadata.json                     │
│     └─ Renders download.html with file info + QR                │
│                                                                 │
│  6. Recipient clicks Download                                   │
│     └─ Hits /d/<file_id>/file                                   │
│     └─ send_from_directory() serves the file                    │
│     └─ Browser saves it with the original filename              │
└─────────────────────────────────────────────────────────────────┘
```

---

<div align="center">

Made with ❤️ · Explained by Claude · Project by vrutShah

</div>
