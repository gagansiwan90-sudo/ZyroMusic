import asyncio
import os
from datetime import datetime, timedelta
from typing import Union

from pyrogram import Client
from pyrogram.types import InlineKeyboardMarkup
from pytgcalls import PyTgCalls, filters
from pytgcalls.exceptions import (
    CallBusy,
    NoActiveGroupCall,
)
from pytgcalls.types import Update, MediaStream, AudioQuality, VideoQuality, ChatUpdate, StreamEnded

import config
from LoverCodes import LOGGER, YouTube, app
from LoverCodes.misc import db
from LoverCodes.utils.database import (
    add_active_chat,
    add_active_video_chat,
    get_lang,
    get_loop,
    group_assistant,
    is_autoend,
    music_on,
    remove_active_chat,
    remove_active_video_chat,
    set_loop,
)
from LoverCodes.utils.exceptions import AssistantErr
from LoverCodes.utils.formatters import check_duration, seconds_to_min, speed_converter
from LoverCodes.utils.inline.play import stream_markup
from LoverCodes.utils.stream.autoclear import auto_clean
from LoverCodes.utils.thumbnails import get_thumb
from strings import get_string

autoend = {}
counter = {}


async def _clear_(chat_id):
    db[chat_id] = []
    await remove_active_video_chat(chat_id)
    await remove_active_chat(chat_id)


class Call(PyTgCalls):
    def __init__(self):
        self.userbot1 = None
        self.one = None
        self.userbot2 = None
        self.two = None
        self.userbot3 = None
        self.three = None
        self.userbot4 = None
        self.four = None
        self.userbot5 = None
        self.five = None

    async def pause_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.pause_call(chat_id)

    async def resume_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        await assistant.resume_call(chat_id)

    async def stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            await _clear_(chat_id)
            await assistant.leave_call(chat_id)
        except:
            pass

    async def stop_stream_force(self, chat_id: int):
        try:
            if config.STRING1:
                await self.one.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING2:
                await self.two.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING3:
                await self.three.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING4:
                await self.four.leave_call(chat_id)
        except:
            pass
        try:
            if config.STRING5:
                await self.five.leave_call(chat_id)
        except:
            pass
        try:
            await _clear_(chat_id)
        except:
            pass

    async def speedup_stream(self, chat_id: int, file_path, speed, playing):
        assistant = await group_assistant(self, chat_id)
        if str(speed) != str("1.0"):
            base = os.path.basename(file_path)
            chatdir = os.path.join(os.getcwd(), "playback", str(speed))
            if not os.path.isdir(chatdir):
                os.makedirs(chatdir)
            out = os.path.join(chatdir, base)
            if not os.path.isfile(out):
                if str(speed) == str("0.5"):
                    vs = 2.0
                if str(speed) == str("0.75"):
                    vs = 1.35
                if str(speed) == str("1.5"):
                    vs = 0.68
                if str(speed) == str("2.0"):
                    vs = 0.5
                proc = await asyncio.create_subprocess_shell(
                    cmd=(
                        "ffmpeg "
                        "-i "
                        f"{file_path} "
                        "-filter:v "
                        f"setpts={vs}*PTS "
                        "-filter:a "
                        f"atempo={speed} "
                        f"{out}"
                    ),
                    stdin=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )
                await proc.communicate()
            else:
                pass
        else:
            out = file_path
        dur = await asyncio.get_event_loop().run_in_executor(None, check_duration, out)
        dur = int(dur)
        played, con_seconds = speed_converter(playing[0]["played"], speed)
        duration = seconds_to_min(dur)
        if playing[0]["streamtype"] == "video":
            stream = MediaStream(
                out,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
                ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
        else:
            stream = MediaStream(
                out,
                audio_parameters=AudioQuality.HIGH,
                ffmpeg_parameters=f"-ss {played} -to {duration}",
            )
        if str(db[chat_id][0]["file"]) == str(file_path):
            await assistant.play(chat_id, stream)
        else:
            raise AssistantErr("Umm")
        if str(db[chat_id][0]["file"]) == str(file_path):
            exis = (playing[0]).get("old_dur")
            if not exis:
                db[chat_id][0]["old_dur"] = db[chat_id][0]["dur"]
                db[chat_id][0]["old_second"] = db[chat_id][0]["seconds"]
            db[chat_id][0]["played"] = con_seconds
            db[chat_id][0]["dur"] = duration
            db[chat_id][0]["seconds"] = dur
            db[chat_id][0]["speed_path"] = out
            db[chat_id][0]["speed"] = speed

    async def force_stop_stream(self, chat_id: int):
        assistant = await group_assistant(self, chat_id)
        try:
            check = db.get(chat_id)
            check.pop(0)
        except:
            pass
        await remove_active_video_chat(chat_id)
        await remove_active_chat(chat_id)
        try:
            await assistant.leave_call(chat_id)
        except:
            pass

    async def skip_stream(
        self,
        chat_id: int,
        link: str,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        if video:
            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
            )
        else:
            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
            )
        await assistant.play(
            chat_id,
            stream,
        )

    async def seek_stream(self, chat_id, file_path, to_seek, duration, mode):
        assistant = await group_assistant(self, chat_id)
        if mode == "video":
            stream = MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        else:
            stream = MediaStream(
                file_path,
                audio_parameters=AudioQuality.HIGH,
                ffmpeg_parameters=f"-ss {to_seek} -to {duration}",
            )
        await assistant.play(chat_id, stream)

    async def stream_call(self, link):
        if config.LOGGER_ID == 0:
            return
        assistant = await group_assistant(self, config.LOGGER_ID)
        await assistant.play(
            config.LOGGER_ID,
            MediaStream(link),
        )
        await asyncio.sleep(0.2)
        await assistant.leave_call(config.LOGGER_ID)

    async def join_call(
        self,
        chat_id: int,
        original_chat_id: int,
        link,
        video: Union[bool, str] = None,
        image: Union[bool, str] = None,
    ):
        assistant = await group_assistant(self, chat_id)
        language = await get_lang(chat_id)
        _ = get_string(language)
        if video:
            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
                video_parameters=VideoQuality.HD_720p,
            )
        else:
            stream = MediaStream(
                link,
                audio_parameters=AudioQuality.HIGH,
            )
        try:
            await assistant.play(
                chat_id,
                stream,
            )
        except NoActiveGroupCall:
            raise AssistantErr(_["call_8"])
        except CallBusy:
            raise AssistantErr(_["call_9"])
        except Exception:
            raise AssistantErr(_["call_10"])
        await add_active_chat(chat_id)
        await music_on(chat_id)
        if video:
            await add_active_video_chat(chat_id)
        if await is_autoend():
            counter[chat_id] = {}
            users = len(await assistant.get_participants(chat_id))
            if users == 1:
                autoend[chat_id] = datetime.now() + timedelta(minutes=1)

    async def change_stream(self, client, chat_id):
        LOGGER(__name__).info(f"Processing change_stream for chat_id: {chat_id}")
        check = db.get(chat_id)
        if not check:
            LOGGER(__name__).info(f"No songs in queue for chat_id: {chat_id}. Leaving call.")
            await _clear_(chat_id)
            return await client.leave_call(chat_id)

        popped = None
        loop = await get_loop(chat_id)
        try:
            if loop == 0:
                popped = check.pop(0)
            else:
                loop = loop - 1
                await set_loop(chat_id, loop)
            
            if popped:
                await auto_clean(popped)
            
            if not check:
                LOGGER(__name__).info(f"Queue empty after popping for chat_id: {chat_id}. Leaving call.")
                await _clear_(chat_id)
                return await client.leave_call(chat_id)
            
            # Start of song playback logic
            queued = check[0]["file"]
            language = await get_lang(chat_id)
            _ = get_string(language)
            title = (check[0]["title"]).title()
            user = check[0]["by"]
            original_chat_id = check[0]["chat_id"]
            streamtype = check[0]["streamtype"]
            videoid = check[0]["vidid"]
            db[chat_id][0]["played"] = 0
            exis = (check[0]).get("old_dur")
            if exis:
                db[chat_id][0]["dur"] = exis
                db[chat_id][0]["seconds"] = check[0]["old_second"]
                db[chat_id][0]["speed_path"] = None
                db[chat_id][0]["speed"] = 1.0
            video = True if str(streamtype) == "video" else False
            
            LOGGER(__name__).info(f"Next song: {title} (Type: {streamtype})")

            if "live_" in queued:
                n, link = await YouTube.video(videoid, True)
                if n == 0:
                    return await app.send_message(original_chat_id, text=_["call_6"])
                if video:
                    stream = MediaStream(
                        link,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.HD_720p,
                    )
                else:
                    stream = MediaStream(
                        link,
                        audio_parameters=AudioQuality.HIGH,
                    )
                await client.play(chat_id, stream)
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], check[0]["dur"], user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            elif "vid_" in queued:
                mystic = await app.send_message(original_chat_id, _["call_7"])
                file_path, direct = await YouTube.download(videoid, mystic, videoid=True, video=True if str(streamtype) == "video" else False)
                if video:
                    stream = MediaStream(
                        file_path,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.HD_720p,
                    )
                else:
                    stream = MediaStream(
                        file_path,
                        audio_parameters=AudioQuality.HIGH,
                    )
                await client.play(chat_id, stream)
                img = await get_thumb(videoid)
                button = stream_markup(_, chat_id)
                await mystic.delete()
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=img,
                    caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], check[0]["dur"], user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "stream"
            elif "index_" in queued:
                if video:
                    stream = MediaStream(
                        videoid,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.HD_720p,
                    )
                else:
                    stream = MediaStream(
                        videoid,
                        audio_parameters=AudioQuality.HIGH,
                    )
                await client.play(chat_id, stream)
                button = stream_markup(_, chat_id)
                run = await app.send_photo(
                    chat_id=original_chat_id,
                    photo=config.STREAM_IMG_URL,
                    caption=_["stream_2"].format(user),
                    reply_markup=InlineKeyboardMarkup(button),
                )
                db[chat_id][0]["mystic"] = run
                db[chat_id][0]["markup"] = "tg"
            else:
                if video:
                    stream = MediaStream(
                        queued,
                        audio_parameters=AudioQuality.HIGH,
                        video_parameters=VideoQuality.HD_720p,
                    )
                else:
                    stream = MediaStream(
                        queued,
                        audio_parameters=AudioQuality.HIGH,
                    )
                await client.play(chat_id, stream)
                if videoid == "telegram":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.TELEGRAM_VIDEO_URL if str(streamtype) == "video" else config.TELEGRAM_AUDIO_URL,
                        caption=_["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                elif videoid == "soundcloud":
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=config.SOUNCLOUD_IMG_URL,
                        caption=_["stream_1"].format(config.SUPPORT_CHAT, title[:23], check[0]["dur"], user),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "tg"
                else:
                    img = await get_thumb(videoid)
                    button = stream_markup(_, chat_id)
                    run = await app.send_photo(
                        chat_id=original_chat_id,
                        photo=img,
                        caption=_["stream_1"].format(f"https://t.me/{app.username}?start=info_{videoid}", title[:23], check[0]["dur"], user),
                        reply_markup=InlineKeyboardMarkup(button),
                    )
                    db[chat_id][0]["mystic"] = run
                    db[chat_id][0]["markup"] = "stream"
            
            LOGGER(__name__).info(f"Playback started successfully for: {title}")

        except Exception as e:
            LOGGER(__name__).error(f"Error in change_stream for chat_id {chat_id}: {e}")
            import traceback
            traceback.print_exc()
            try:
                await _clear_(chat_id)
                await client.leave_call(chat_id)
                LOGGER(__name__).info(f"Assistant left call for chat_id {chat_id} due to playback error.")
            except:
                pass

    async def ping(self):
        pings = []
        if config.STRING1:
            pings.append(await self.one.ping)
        if config.STRING2:
            pings.append(await self.two.ping)
        if config.STRING3:
            pings.append(await self.three.ping)
        if config.STRING4:
            pings.append(await self.four.ping)
        if config.STRING5:
            pings.append(await self.five.ping)
        return str(round(sum(pings) / len(pings), 3)) if pings else "0.0"

    async def start(self):
        from LoverCodes import userbot
        LOGGER(__name__).info("Starting PyTgCalls Client...\n")
        if config.STRING1:
            self.userbot1 = userbot.one
            self.one = PyTgCalls(self.userbot1)
            await self.one.start()
        if config.STRING2:
            self.userbot2 = userbot.two
            self.two = PyTgCalls(self.userbot2)
            await self.two.start()
        if config.STRING3:
            self.userbot3 = userbot.three
            self.three = PyTgCalls(self.userbot3)
            await self.three.start()
        if config.STRING4:
            self.userbot4 = userbot.four
            self.four = PyTgCalls(self.userbot4)
            await self.four.start()
        if config.STRING5:
            self.userbot5 = userbot.five
            self.five = PyTgCalls(self.userbot5)
            await self.five.start()

    async def stop(self):
        LOGGER(__name__).info("Stopping PyTgCalls Client...\n")
        if config.STRING1:
            await self.one.stop()
        if config.STRING2:
            await self.two.stop()
        if config.STRING3:
            await self.three.stop()
        if config.STRING4:
            await self.four.stop()
        if config.STRING5:
            await self.five.stop()

    async def _stream_end_handler(self, client, update: Update):
        if not isinstance(update, StreamEnded):
            return
        LOGGER(__name__).info(f"Received StreamEnded update for chat_id: {update.chat_id}")
        await self.change_stream(client, update.chat_id)

    async def _service_handler(self, _, chat_id: int):
        await self.stop_stream(chat_id)

    async def decorators(self):
        async def stream_services_handler(client, update: Update):
            await self._service_handler(client, update.chat_id)

        async def stream_end_handler(client, update: Update):
            await self._stream_end_handler(client, update)

        if self.one:
            self.one.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))(stream_services_handler)
            self.one.on_update(filters.stream_end())(stream_end_handler)
        if self.two:
            self.two.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))(stream_services_handler)
            self.two.on_update(filters.stream_end())(stream_end_handler)
        if self.three:
            self.three.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))(stream_services_handler)
            self.three.on_update(filters.stream_end())(stream_end_handler)
        if self.four:
            self.four.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))(stream_services_handler)
            self.four.on_update(filters.stream_end())(stream_end_handler)
        if self.five:
            self.five.on_update(filters.chat_update(ChatUpdate.Status.LEFT_CALL))(stream_services_handler)
            self.five.on_update(filters.stream_end())(stream_end_handler)


Lover = Call()
