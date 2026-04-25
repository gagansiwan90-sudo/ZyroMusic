import re
from os import getenv
from dotenv import load_dotenv
from pyrogram import filters

# Load environment variables
load_dotenv()

# ─────────────── REQUIRED CREDENTIALS ───────────────
API_ID = int(getenv("API_ID", "0"))
API_HASH = getenv("API_HASH", "")
BOT_TOKEN = getenv("BOT_TOKEN", "")

# ─────────────── BOT & OWNER INFO ───────────────
OWNER_ID = int(getenv("OWNER_ID", "7918103039"))
OWNER_USERNAME = getenv("OWNER_USERNAME", "")
BOT_USERNAME = getenv("BOT_USERNAME", "")
BOT_NAME = getenv("BOT_NAME", "")
ASSUSERNAME = getenv("ASSUSERNAME", "")

# ─────────────── DATABASE ───────────────
MONGO_DB_URI = getenv("MONGO_DB_URI", "")

# ─────────────── LOGGING ───────────────
LOGGER_ID = int(getenv("LOGGER_ID", "0"))

# ─────────────── HEROKU ───────────────
HEROKU_APP_NAME = getenv("HEROKU_APP_NAME", "")
HEROKU_API_KEY = getenv("HEROKU_API_KEY", "")

# ─────────────── EVAL ───────────────
EVAL = getenv("EVAL", "True")

# ─────────────── DURATION LIMIT ───────────────
DURATION_LIMIT_MIN = int(getenv("DURATION_LIMIT", "17000"))

# ─────────────── GIT ───────────────
UPSTREAM_REPO = getenv("UPSTREAM_REPO", "https://github.com/MrZyro/ZyroMusic")
UPSTREAM_BRANCH = getenv("UPSTREAM_BRANCH", "Master")
GIT_TOKEN = getenv("GIT_TOKEN", "")

# ─────────────── SUPPORT ───────────────
SUPPORT_CHANNEL = getenv("SUPPORT_CHANNEL", "https://t.me/LoverCodes")
SUPPORT_CHAT = getenv("SUPPORT_CHAT", "https://t.me/LoverCodesChat")
SUPPORT_GROUP = SUPPORT_CHAT

# ─────────────── ASSISTANT SETTINGS ───────────────
AUTO_LEAVING_ASSISTANT = getenv("AUTO_LEAVING_ASSISTANT", "True")
AUTO_LEAVE_ASSISTANT_TIME = int(getenv("ASSISTANT_LEAVE_TIME", "9000"))

# ─────────────── SONG DOWNLOAD LIMITS ───────────────
SONG_DOWNLOAD_DURATION = int(getenv("SONG_DOWNLOAD_DURATION", "9999999"))
SONG_DOWNLOAD_DURATION_LIMIT = int(getenv("SONG_DOWNLOAD_DURATION_LIMIT", "9999999"))

# ─────────────── SPOTIFY ───────────────
SPOTIFY_CLIENT_ID = getenv("SPOTIFY_CLIENT_ID", "1c21247d714244ddbb09925dac565aed")
SPOTIFY_CLIENT_SECRET = getenv("SPOTIFY_CLIENT_SECRET", "709e1a2969664491b58200860623ef19")

# ─────────────── PLAYLIST ───────────────
PLAYLIST_FETCH_LIMIT = int(getenv("PLAYLIST_FETCH_LIMIT", "25"))

# ─────────────── TELEGRAM FILE SIZE LIMITS ───────────────
TG_AUDIO_FILESIZE_LIMIT = int(getenv("TG_AUDIO_FILESIZE_LIMIT", "5242880000"))
TG_VIDEO_FILESIZE_LIMIT = int(getenv("TG_VIDEO_FILESIZE_LIMIT", "5242880000"))

# ─────────────── SESSION STRINGS ───────────────
STRING1 = getenv("STRING_SESSION", None)
STRING2 = getenv("STRING_SESSION2", None)
STRING3 = getenv("STRING_SESSION3", None)
STRING4 = getenv("STRING_SESSION4", None)
STRING5 = getenv("STRING_SESSION5", None)
STRING6 = getenv("STRING_SESSION6", None)

# ─────────────── MISCELLANEOUS ───────────────
BANNED_USERS = filters.user()
adminlist = {}
lyrical = {}
votemode = {}
autoclean = []
confirmer = {}
DEBUG_IGNORE_LOG = True

# ─────────────── IMAGE URLS ───────────────
START_IMG_URL = getenv("START_IMG_URL", "https://files.catbox.moe/zeexhx.jpg")
PING_IMG_URL = getenv("PING_IMG_URL", "https://files.catbox.moe/l6ekqj.jpg")
PLAYLIST_IMG_URL = "https://files.catbox.moe/l6ekqj.jpg"
STATS_IMG_URL = "https://files.catbox.moe/l6ekqj.jpg"
TELEGRAM_AUDIO_URL = "https://files.catbox.moe/l6ekqj.jpg"
TELEGRAM_VIDEO_URL = "https://files.catbox.moe/l6ekqj.jpg"
STREAM_IMG_URL = "https://files.catbox.moe/l6ekqj.jpg"
SOUNCLOUD_IMG_URL = "https://files.catbox.moe/l6ekqj.jpg"
YOUTUBE_IMG_URL = "https://files.catbox.moe/l6ekqj.jpg"
SPOTIFY_ARTIST_IMG_URL = "https://files.catbox.moe/l6ekqj.jpg"
SPOTIFY_ALBUM_IMG_URL = "https://files.catbox.moe/l6ekqj.jpg"
SPOTIFY_PLAYLIST_IMG_URL = "https://files.catbox.moe/l6ekqj.jpg"
NOW_PLAYING_IMG_URL = getenv("NOW_PLAYING_IMG_URL", "https://images8.alphacoders.com/135/thumb-1920-1351572.jpeg")

# ─────────────── HELPER FUNCTION ───────────────
def time_to_seconds(time: str) -> int:
    return sum(int(x) * 60**i for i, x in enumerate(reversed(time.split(":"))))

DURATION_LIMIT = int(time_to_seconds(f"{DURATION_LIMIT_MIN}:00"))

# ─────────────── URL VALIDATION ───────────────
if SUPPORT_CHANNEL and not re.match(r"(?:http|https)://", SUPPORT_CHANNEL):
    raise SystemExit("[ERROR] - Your SUPPORT_CHANNEL url is invalid. It must start with https://")

if SUPPORT_CHAT and not re.match(r"(?:http|https)://", SUPPORT_CHAT):
    raise SystemExit("[ERROR] - Your SUPPORT_CHAT url is invalid. It must start with https://")
