import os
import time
import yt_dlp

DOWNLOADS_DIR = "downloads"
MAX_FILE_SIZE_MB = 50  # Telegram upload limit


# ===================== CLEAN OLD FILES =====================
def clean_old_files(max_age_minutes=15):
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)
    now = time.time()

    for f in os.listdir(DOWNLOADS_DIR):
        path = os.path.join(DOWNLOADS_DIR, f)
        if os.path.isfile(path) and (now - os.path.getmtime(path))/60 > max_age_minutes:
            os.remove(path)


def is_too_large(path):
    return os.path.getsize(path) > MAX_FILE_SIZE_MB * 1024 * 1024



# =====================  TIKTOK  =====================
def download_tiktok(url: str):
    clean_old_files()
    ydl_opts = {
        'format': 'mp4',
        'outtmpl': f"{DOWNLOADS_DIR}/%(id)s.%(ext)s",
        'noplaylist': True,
        'quiet': True
    }
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)

        file = f"{DOWNLOADS_DIR}/{info['id']}.mp4"
        if not os.path.exists(file): raise Exception("File missing!")
        if is_too_large(file): raise Exception("FILE_TOO_LARGE")

        return file, info.get('title', '🎵 TikTok video')

    except Exception as e:
        raise Exception(f"❌ TikTok error: {e}")



# =====================  INSTAGRAM  =====================
def download_instagram(url: str):
    clean_old_files()
    url = url.replace("instagram.com","ddinstagram.com")

    ydl = {
        'format': 'mp4',
        'outtmpl': f"{DOWNLOADS_DIR}/%(id)s.%(ext)s",
        'quiet': True,
        'noplaylist': True
    }

    try:
        with yt_dlp.YoutubeDL(ydl) as y:
            info = y.extract_info(url, download=True)

    except:
        with yt_dlp.YoutubeDL(ydl) as y:
            info = y.extract_info(url.replace("ddinstagram.com","instagram.com"), download=True)

    file = f"{DOWNLOADS_DIR}/{info['id']}.mp4"
    if not os.path.exists(file): raise Exception("file missing")

    return file, info.get('title','📸 Instagram video')