<div align="center">

# ⬡ FileShare

**A lightweight, beautifully designed local-network file sharing app.**  
Upload any file → get a **download link** + **QR code** → share instantly.

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=flat-square&logo=python)
![Flask](https://img.shields.io/badge/Flask-3.0%2B-black?style=flat-square&logo=flask)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey?style=flat-square)

</div>

---

## 📁 Folder Structure

```
fileshare/
├── 🐍 app.py                  # Flask backend — routes, QR generation, metadata
├── 📋 requirements.txt        # Python dependencies
├── 📖 README.md               # You are here
├── 📦 metadata.json           # Auto-created on first upload
├── 📂 uploads/                # Auto-created; stores all uploaded files
└── 🗂️ templates/
    ├── 🌐 index.html          # Upload page (drag & drop, description, result)
    └── 🌐 download.html       # Download page (shown when link is opened)
```

---

## 🚀 Quick Start

### 1️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Run the server

```bash
python app.py
```

The terminal will print your local network URL:

```
  ✦  FileShare running at  http://192.168.1.42:5000
```

### 3️⃣ Open in a browser

Navigate to the URL shown above.  
Any device on the **same Wi-Fi network** can access it.

---

## ✨ Features

| Feature | Details |
|---|---|
| 📂 File upload | Drag-and-drop or click to browse (max 100 MB) |
| 📝 Description | Optional 1–2 line note visible to the recipient |
| 🔗 Download link | Auto-generated using your local IP address |
| 📱 QR code | Displayed instantly — scan to download on mobile |
| 🎨 Download page | Clean page with file info, description, QR & download button |
| 📊 File metadata | Filename, size, and description stored in `metadata.json` |
| 🗂️ File type icons | Automatic emoji icons based on file extension |

---

## ✅ Pros

| # | Advantage | Details |
|---|---|---|
| 1 | ⚡ **Zero config sharing** | Just run `python app.py` — no accounts, no login, no setup |
| 2 | 🔒 **Fully local & private** | Files never leave your network; no cloud, no third-party servers |
| 3 | 📱 **Mobile friendly** | QR code lets phones download instantly without typing any URL |
| 4 | 🎨 **Polished UI** | Dark-themed, animated frontend — far better than plain file servers |
| 5 | 🧩 **No database needed** | Lightweight JSON metadata, no SQL or ORM required |
| 6 | 🐍 **Pure Python** | Only 3 dependencies: Flask, qrcode, Pillow — easy to understand & modify |
| 7 | 🌐 **Cross-platform** | Works on Windows, macOS, and Linux without any changes |
| 8 | 📝 **File descriptions** | Senders can add context so recipients know what the file is before downloading |
| 9 | 🔁 **Multiple files** | Upload as many files as you want in one session |
| 10 | 🛠️ **Easy to extend** | Clean, well-structured codebase — add features like auth or expiry easily |

---

## ❌ Cons

| # | Limitation | Details |
|---|---|---|
| 1 | 📶 **Same Wi-Fi required** | Both devices must be on the same local network — won't work across the internet |
| 2 | 💻 **Server must stay running** | Links break as soon as you stop `app.py` — no persistence across restarts |
| 3 | 🔓 **No authentication** | Anyone on your network can access upload/download pages — not suitable for public networks |
| 4 | 📦 **100 MB file limit** | Large files (videos, disk images) may exceed the default cap (configurable in `app.py`) |
| 5 | 🧹 **No auto-cleanup** | Uploaded files accumulate in `uploads/` — you must delete them manually |
| 6 | 🔐 **No HTTPS** | Traffic is unencrypted HTTP — fine for home networks, risky on public/shared Wi-Fi |
| 7 | 🌍 **Not internet-accessible** | Requires a tool like ngrok or a cloud deployment to share outside your LAN |
| 8 | 🔗 **No link expiry** | Download links stay active forever (until the server stops) — no time-based expiration |
| 9 | 👤 **Single user focus** | No multi-user management, upload history UI, or admin dashboard |
| 10 | 📵 **No resume support** | Interrupted downloads must restart from the beginning |

---

## ⚙️ Configuration

| Setting | Location | Default |
|---|---|---|
| Max file size | `app.py` → `MAX_MB` | `100` MB |
| Server port | `app.py` → `port` | `5000` |
| Upload folder | `app.py` → `UPLOAD_DIR` | `./uploads/` |
| Metadata file | `app.py` → `META_FILE` | `./metadata.json` |

---

## 🌍 Want to Share Across Different Networks?

By default this app only works on **the same Wi-Fi**. To share over the internet:

- **[ngrok](https://ngrok.com/)** — Run `ngrok http 5000` alongside the app for a free public tunnel
- **[Railway](https://railway.app/) / [Render](https://render.com/)** — Deploy for a permanent public URL

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| 🐍 Backend | Python 3.9+, Flask |
| 🎨 Frontend | HTML5, CSS3, Vanilla JavaScript |
| 📱 QR Code | `qrcode` + `Pillow` |
| 💾 Storage | Local filesystem + JSON |

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">
  Made by Vrut Shah Built with Python & Flask
</div>
