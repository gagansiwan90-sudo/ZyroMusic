import aiohttp
import asyncio
import glob
import json
import os
import random
import re
from typing import Union
import yt_dlp
from pyrogram.enums import MessageEntityType
from pyrogram.types import Message
from LoverCodes import LOGGER
from LoverCodes.utils.database import is_on_off
from LoverCodes.utils.formatters import time_to_seconds
from config import API_URL, VIDEO_API_URL, API_KEY, API2_URL, YT_API_KEY as XBIT_API_KEY, YTPROXY_URL as YTPROXY

logger = LOGGER(__name__)

# Create a global session to reuse connections
_session = None

def get_session():
    global _session
    if _session is None or _session.closed:
        _session = aiohttp.ClientSession()
    return _session

async def download_xbit(video_id: str, file_type: str = "audio"):
    ext = "mp4" if file_type == "video" else "mp3"
    file_path = os.path.join("downloads", f"{video_id}.{ext}")
    if os.path.exists(file_path):
        return file_path

    session = get_session()
    try:
        url = f"{YTPROXY}/info/{video_id}"
        headers = {
            "x-api-key": XBIT_API_KEY,
            "Content-Type": "application/json"
        }
        async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=15)) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            if data.get("status") != "success":
                 return None
            
            download_url = data.get("video_url" if file_type == "video" else "audio_url")
            if not download_url:
                return None

            async with session.get(download_url) as file_resp:
                if file_resp.status != 200:
                    return None
                os.makedirs("downloads", exist_ok=True)
                with open(file_path, "wb") as f:
                    async for chunk in file_resp.content.iter_chunked(1048576):
                        f.write(chunk)
            return file_path
    except Exception as e:
        logger.error(f"XBit Download error: {e}")
        return None

async def download_api2(video_id: str, file_type: str = "audio"):
    ext = "mp4" if file_type == "video" else "mp3"
    file_path = os.path.join("downloads", f"{video_id}.{ext}")
    if os.path.exists(file_path):
        return file_path

    session = get_session()
    try:
        async with session.get(
            f"{API2_URL}/download",
            params={"url": video_id, "type": file_type},
            timeout=aiohttp.ClientTimeout(total=10)
        ) as resp:
            if resp.status != 200:
                return None
            data = await resp.json()
            token = data.get("download_token")
            if not token:
                return None

        stream_url = f"{API2_URL}/stream/{video_id}?type={file_type}&token={token}"
        async with session.get(stream_url) as audio_resp:
            if audio_resp.status == 302:
                redirect = audio_resp.headers.get("Location")
                if not redirect:
                    return None
                async with session.get(redirect) as final_resp:
                    if final_resp.status != 200:
                        return None
                    with open(file_path, "wb") as f:
                        async for chunk in final_resp.content.iter_chunked(1048576):
                            f.write(chunk)
            elif audio_resp.status == 200:
                with open(file_path, "wb") as f:
                    async for chunk in audio_resp.content.iter_chunked(1048576):
                        f.write(chunk)
            else:
                return None
        return file_path
    except Exception:
        return None

async def download_song(link: str):
    video_id = link.split('v=')[-1].split('&')[0]
    download_folder = "downloads"
    file_path = None
    for ext in ["mp3", "m4a", "webm"]:
        file_path = f"{download_folder}/{video_id}.{ext}"
        if os.path.exists(file_path):
            return file_path
        
    # Priority 1: XBit API
    xbit_path = await download_xbit(video_id, "audio")
    if xbit_path:
        return xbit_path

    # Try API 1 (NexGen)
    song_url = f"{API_URL}/song/{video_id}?api={API_KEY}"
    session = get_session()
    for attempt in range(5):
        try:
            async with session.get(song_url, timeout=10) as response:
                if response.status != 200:
                    break
                data = await response.json()
                status = data.get("status", "").lower()
                if status == "done":
                    download_url = data.get("link")
                    file_name = f"{video_id}.mp3"
                    os.makedirs(download_folder, exist_ok=True)
                    file_path = os.path.join(download_folder, file_name)
                    async with session.get(download_url) as file_response:
                        with open(file_path, 'wb') as f:
                            async for chunk in file_response.content.iter_chunked(1048576):
                                f.write(chunk)
                        return file_path
                elif status == "downloading":
                    await asyncio.sleep(2)
                else: break
        except: break
    
    # Fallback to API 2 (Shruti)
    return await download_api2(video_id, "audio")

async def download_video_api(link: str):
    video_id = link.split('v=')[-1].split('&')[0]
    download_folder = "downloads"
    file_path = None
    for ext in ["mp4", "webm", "mkv"]:
        file_path = f"{download_folder}/{video_id}.{ext}"
        if os.path.exists(file_path):
            return file_path
        
    # Priority 1: XBit API
    xbit_path = await download_xbit(video_id, "video")
    if xbit_path:
        return xbit_path

    video_url = f"{VIDEO_API_URL}/video/{video_id}?api={API_KEY}"
    session = get_session()
    for attempt in range(5):
        try:
            async with session.get(video_url, timeout=10) as response:
                if response.status != 200:
                    break
                data = await response.json()
                status = data.get("status", "").lower()
                if status == "done":
                    download_url = data.get("link")
                    file_name = f"{video_id}.mp4"
                    os.makedirs(download_folder, exist_ok=True)
                    file_path = os.path.join(download_folder, file_name)
                    async with session.get(download_url) as file_response:
                        with open(file_path, 'wb') as f:
                            async for chunk in file_response.content.iter_chunked(1048576):
                                f.write(chunk)
                        return file_path
                elif status == "downloading":
                    await asyncio.sleep(2)
                else: break
        except: break
                
    # Fallback to API 2
    return await download_api2(video_id, "video")


class YouTubeAPI:
    def __init__(self):
        self.base = "https://www.youtube.com/watch?v="
        self.regex = r"(?:youtube\.com|youtu\.be)"
        self.status = "https://www.youtube.com/oembed?url="
        self.listbase = "https://youtube.com/playlist?list="
        self.reg = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")
        self.dl_stats = {
            "total_requests": 0,
            "okflix_downloads": 0,
            "cookie_downloads": 0,
            "existing_files": 0
        }


    async def exists(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if re.search(self.regex, link):
            return True
        else:
            return False

    async def url(self, message_1: Message) -> Union[str, None]:
        messages = [message_1]
        if message_1.reply_to_message:
            messages.append(message_1.reply_to_message)
        text = ""
        offset = None
        length = None
        for message in messages:
            if offset:
                break
            if message.entities:
                for entity in message.entities:
                    if entity.type == MessageEntityType.URL:
                        text = message.text or message.caption
                        offset, length = entity.offset, entity.length
                        break
            elif message.caption_entities:
                for entity in message.caption_entities:
                    if entity.type == MessageEntityType.TEXT_LINK:
                        return entity.url
        if offset in (None,):
            return None
        return text[offset : offset + length]

    async def details(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]


        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
            duration_min = result["duration"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            vidid = result["id"]
            if str(duration_min) == "None":
                duration_sec = 0
            else:
                duration_sec = int(time_to_seconds(duration_min))
        return title, duration_min, duration_sec, thumbnail, vidid

    async def title(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]
            
        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            title = result["title"]
        return title

    async def duration(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            duration = result["duration"]
        return duration

    async def thumbnail(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        if "?si=" in link:
            link = link.split("?si=")[0]
        elif "&si=" in link:
            link = link.split("&si=")[0]

        results = VideosSearch(link, limit=1)
        for result in (await results.next())["result"]:
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        return thumbnail

    async def video(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        # Try API first
        try:
            downloaded_file = await download_video_api(link)
            if downloaded_file:
                return 1, downloaded_file
        except Exception:
            pass
        
        # Original fallback
        proc = await asyncio.create_subprocess_exec(
            "yt-dlp",
            "-g",
            "-f",
            "best[height<=?720][width<=?1280]",
            f"{link}",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await proc.communicate()
        if stdout:
            return 1, stdout.decode().split("\n")[0]
        else:
            return 0, stderr.decode()

    async def playlist(self, link, limit, user_id, videoid: Union[bool, str] = None):
        if videoid:
            link = self.listbase + link
        if "&" in link:
            link = link.split("&")[0]

        from youtubesearchpython.__future__ import Playlist as PlaylistFuture
        playlist = await PlaylistFuture.get(link)
        if playlist:
            videos = []
            for video in playlist["videos"][:limit]:
                try:
                    duration = video.get("duration")
                    if duration:
                        duration_sec = int(time_to_seconds(duration))
                    else:
                        duration_sec = 0
                    videos.append({
                        "vidid": video["id"],
                        "title": video.get("title", "Unknown"),
                        "duration_min": duration,
                        "duration_sec": duration_sec,
                        "thumbnail": video.get("thumbnails", [{}])[0].get("url", "").split("?")[0] if video.get("thumbnails") else "",
                    })
                except:
                    continue
            return videos
        return None

    async def track(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        from youtubesearchpython.__future__ import VideosSearch as VideosSearchFuture
        results = VideosSearchFuture(link, limit=1)
        res = await results.next()
        for result in res["result"]:
            title = result["title"]
            duration_min = result["duration"]
            vidid = result["id"]
            yturl = result["link"]
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
        track_details = {
            "title": title,
            "link": yturl,
            "vidid": vidid,
            "duration_min": duration_min,
            "thumb": thumbnail,
        }
        return track_details, vidid

    async def formats(self, link: str, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]
        ytdl_opts = {"quiet": True}
        ydl = yt_dlp.YoutubeDL(ytdl_opts)
        with ydl:
            formats_available = []
            r = ydl.extract_info(link, download=False)
            for format in r["formats"]:
                try:
                    str(format["format"])
                except:
                    continue
                if not "dash" in str(format["format"]).lower():
                    try:
                        format["format"]
                        format["filesize"]
                        format["format_id"]
                        format["ext"]
                        format["format_note"]
                    except:
                        continue
                    formats_available.append(
                        {
                            "format": format["format"],
                            "filesize": format["filesize"],
                            "format_id": format["format_id"],
                            "ext": format["ext"],
                            "format_note": format["format_note"],
                            "yturl": link,
                        }
                    )
        return formats_available, link

    async def slider(self, link: str, query_type: int, videoid: Union[bool, str] = None):
        if videoid:
            link = self.base + link
        if "&" in link:
            link = link.split("&")[0]

        try:
            from youtubesearchpython.__future__ import VideosSearch as VideosSearchFuture
            search = VideosSearchFuture(link, limit=10)
            res = await search.next()
            search_results = res.get("result", [])

            results = []
            for result in search_results:
                duration_str = result.get("duration", "0:00")
                try:
                    parts = duration_str.split(":")
                    duration_secs = 0
                    if len(parts) == 3:
                        duration_secs = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                    elif len(parts) == 2:
                        duration_secs = int(parts[0]) * 60 + int(parts[1])
                    if duration_secs <= 3600:
                        results.append(result)
                except:
                    continue

            if not results or query_type >= len(results):
                raise ValueError("No suitable videos found")

            selected = results[query_type]
            return (
                selected["title"],
                selected["duration"],
                selected["thumbnails"][0]["url"].split("?")[0],
                selected["id"]
            )
        except Exception as e:
            logger.error(f"Error in slider: {str(e)}")
            raise ValueError("Failed to fetch video details")

    async def download(
        self,
        link: str,
        mystic,
        video: Union[bool, str] = None,
        videoid: Union[bool, str] = None,
        songaudio: Union[bool, str] = None,
        songvideo: Union[bool, str] = None,
        format_id: Union[bool, str] = None,
        title: Union[bool, str] = None,
    ) -> str:
        if videoid:
            link = self.base + link
        
        if songvideo or video:
            fpath = await download_video_api(link)
            if fpath:
                return fpath, True
            raise Exception("Failed to download video file via APIs")
        else:
            fpath = await download_song(link)
            if fpath:
                return fpath, True
            raise Exception("Failed to download audio file via APIs")
