```markdown
# 🎵 YouTube to MP3/MP4 Converter (GUI) — by KAZZEN

A full-featured graphical YouTube downloader with:

- ✅ MP3 and MP4 format selection
- ✅ Search by link or keyword
- ✅ Paginated results (10 per page)
- ✅ Auto-download, convert, and clean metadata
- ✅ Uses `yt-dlp`, `ffmpeg`, and `tkinter`
- ✅ No command line needed
- ✅ One-click `.bat` launcher support

---

## 💻 How It Works

1. Choose MP3 or MP4
2. Paste a YouTube URL *or* search by keyword
3. Results appear with clickable video titles
4. Confirm download → auto-convert & clean
5. File is saved, cleaned, and optionally opened

---

## 🛠 Setup

```bash
git clone https://github.com/<yourusername>/yt-converter-gui.git
cd yt-converter-gui
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

Or use `run_converter.bat` if provided.

---

## 📦 requirements.txt

```txt
imageio-ffmpeg==0.4.7
requests==2.32.3
urllib3==2.4.0
yt-dlp==2025.4.30
```

---

## 📁 Output Folders

```
Converted-mp3/
└── Example Song - Converted by KAZZEN.mp3

Converted-mp4/
└── Example Video - Converted by KAZZEN.mp4
```

---

## 🔒 Privacy & Metadata

- All metadata is stripped using `ffmpeg`
- No data ever leaves your device
- 100% offline + local

---

## 🚫 Limitations & Rules

- ❌ Cannot download or convert live streams (blocked for stability)
- ❌ Does not support playlist downloads — one video at a time
- ❌ No thumbnail previews in GUI (text-only results)
- ❌ Only supports YouTube (no TikTok, Vimeo, etc.)
- ❌ GUI will freeze if `ffmpeg` or `yt-dlp` are broken or outdated
- ❌ No built-in error logging to file — errors show as popups
- ❌ No drag & drop support for links — use copy/paste
- ❌ Requires active internet connection and working `yt-dlp` version
---

## ✅ License

MIT License  
Credit **KAZZEN** if modified or redistributed.
```
